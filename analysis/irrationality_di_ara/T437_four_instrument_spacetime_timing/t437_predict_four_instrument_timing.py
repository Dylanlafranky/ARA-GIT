"""T437 waveform-only four-instrument ARA timing prediction.

This script MUST NOT read the SXS horizon file or any scored event-time answer.
It writes and hashes the prediction that the separate T437 scorer evaluates.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
T435 = HERE.parent / "T435_blind_ara_binary_inversion"
T436 = HERE.parent / "T436_irrationality_timing_transfer"
SOURCE = T435 / "results" / "T435_WAVEFORM_ONLY_PREDICTION.npz"
T436_PREDICTION = T436 / "results" / "T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.json"
PROTOCOL = HERE / "T437_FROZEN_PROTOCOL.md"
OUTPUT = RESULTS / "T437_WAVEFORM_ONLY_FOUR_INSTRUMENT_CLOCKS.npz"
SUMMARY = RESULTS / "T437_WAVEFORM_ONLY_FOUR_INSTRUMENT_CLOCKS.json"
RECEIPT = RESULTS / "T437_PREDICTION_SHA256.txt"

WINDOW = 128
STEP = 4
MAX_LAG = 32
K_NEIGHBOURS = 5
RESOLUTIONS = np.asarray([8, 16, 32, 64], dtype=float)
SEED = 437
EPS = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def circular_mean(values: np.ndarray) -> float:
    vector = np.mean(np.exp(2j * np.pi * values))
    return 0.0 if abs(vector) < 1e-15 else float((np.angle(vector) / (2 * np.pi)) % 1.0)


def circular_loss(actual: np.ndarray, predicted: np.ndarray) -> np.ndarray:
    return 1.0 - np.cos(2.0 * np.pi * (actual - predicted))


def knn_predict(train_x: np.ndarray, train_y: np.ndarray, test_x: np.ndarray) -> np.ndarray:
    order = np.argsort(train_x)
    sx, sy = train_x[order], train_y[order]
    insertion = np.searchsorted(sx, test_x)
    radius = max(K_NEIGHBOURS + 2, 7)
    offsets = np.arange(-radius, radius + 1)
    candidates = (insertion[:, None] + offsets[None, :]) % len(sx)
    candidate_x = sx[candidates]
    distance = np.abs(candidate_x - test_x[:, None])
    distance = np.minimum(distance, 1.0 - distance)
    nearest_positions = np.argpartition(distance, K_NEIGHBOURS - 1, axis=1)[:, :K_NEIGHBOURS]
    nearest = np.take_along_axis(candidates, nearest_positions, axis=1)
    vectors = np.mean(np.exp(2j * np.pi * sy[nearest]), axis=1)
    predicted = (np.angle(vectors) / (2.0 * np.pi)) % 1.0
    predicted[np.abs(vectors) < 1e-12] = circular_mean(train_y)
    return predicted


def address_openness(z: np.ndarray) -> float:
    occupied = []
    for bins_float in RESOLUTIONS:
        bins = int(bins_float)
        index = np.minimum((z * bins).astype(int), bins - 1)
        occupied.append(int(np.unique(index).size))
    beta = float(np.polyfit(np.log(RESOLUTIONS), np.log(occupied), 1)[0])
    return 2.0 * float(np.clip(beta, 0.0, 1.0))


def stochastic_residual(z: np.ndarray) -> tuple[float, float, float]:
    split = len(z) // 2
    train_x, train_y = z[: split - 1], z[1:split]
    test_x, test_y = z[split:-1], z[split + 1 :]
    prediction = knn_predict(train_x, train_y, test_x)
    null_prediction = np.full_like(test_y, circular_mean(train_y))
    local = float(np.mean(circular_loss(test_y, prediction)))
    null = float(np.mean(circular_loss(test_y, null_prediction)))
    return 2.0 * min(1.0, local / max(null, EPS)), local, null


def path_metrics(z: np.ndarray) -> tuple[float, float, float, float, float]:
    x_r, local, null = stochastic_residual(z)
    vector = np.exp(2j * np.pi * z)
    relations = np.asarray([
        np.mean(vector[lag:] * np.conj(vector[:-lag]))
        for lag in range(1, MAX_LAG + 1)
    ])
    rho = float(np.median(np.abs(relations)))
    x_p = address_openness(z)
    distance = float(np.sqrt((x_p - 1.0) ** 2 + x_r**2 + (1.0 - rho) ** 2))
    return x_p, x_r, rho, local, distance


def build_path_history(phase_radians: np.ndarray, time: np.ndarray, reverse_support: bool) -> dict[str, np.ndarray]:
    z = (np.asarray(phase_radians, dtype=float) / (2.0 * np.pi)) % 1.0
    if reverse_support:
        anchors = np.arange(0, len(z) - WINDOW + 1, STEP, dtype=int)
        windows = (z[start : start + WINDOW][::-1] for start in anchors)
    else:
        anchors = np.arange(WINDOW - 1, len(z), STEP, dtype=int)
        windows = (z[end - WINDOW + 1 : end + 1] for end in anchors)
    rows = np.asarray([path_metrics(window) for window in windows], dtype=float)
    return {
        "index": anchors,
        "time": time[anchors],
        "x_P": rows[:, 0],
        "x_R": rows[:, 1],
        "rho": rows[:, 2],
        "local_loss": rows[:, 3],
        "distance": rows[:, 4],
    }


def select_path_clock(
    history: dict[str, np.ndarray], relation: np.ndarray, power_peak_time: float
) -> dict[str, object]:
    idx = history["index"].astype(int)
    eligible = (history["time"] <= power_peak_time) & (relation[idx] <= 1.0)
    if not np.any(eligible):
        raise RuntimeError("Frozen late-parent basin is empty")
    eligible_indices = np.flatnonzero(eligible)
    k = int(eligible_indices[np.argmin(history["distance"][eligible])])

    crossings: list[dict[str, float]] = []
    d = history["x_P"] - 1.0
    for j in range(len(d) - 1):
        if not (eligible[j] and eligible[j + 1]):
            continue
        if not (d[j] >= 0.0 and d[j + 1] < 0.0):
            continue
        frac = float(d[j] / max(d[j] - d[j + 1], EPS))
        interp = lambda a: float(a[j] + frac * (a[j + 1] - a[j]))
        crossings.append({
            "time_M": interp(history["time"]),
            "x_P": 1.0,
            "x_R": interp(history["x_R"]),
            "rho": interp(history["rho"]),
        })
    return {
        "k": k,
        "time_M": float(history["time"][k]),
        "x_P": float(history["x_P"][k]),
        "x_R": float(history["x_R"][k]),
        "rho": float(history["rho"][k]),
        "distance": float(history["distance"][k]),
        "eligible_count": int(np.sum(eligible)),
        "eligible": eligible,
        "downward_xP_crossings": crossings,
    }


def build_state_history(
    amplitude: np.ndarray,
    phase_radians: np.ndarray,
    cadence: np.ndarray,
    time: np.ndarray,
) -> dict[str, np.ndarray]:
    x_l = np.full(len(time), np.nan, dtype=float)
    x_c = np.full(len(time), np.nan, dtype=float)
    previous = np.full(len(time), -1, dtype=int)
    for i in range(1, len(time)):
        period = float(cadence[i])
        if not np.isfinite(period) or period <= 0 or time[i] - period < time[0]:
            continue
        j = int(np.searchsorted(time, time[i] - period, side="left"))
        if j >= i:
            continue
        previous[i] = j
        scale = float(amplitude[i] / max(amplitude[j], EPS))
        x_l[i] = 2.0 * scale / (1.0 + scale)
        delta = np.angle(np.exp(1j * np.diff(phase_radians[j : i + 1])))
        denominator = float(np.sum(np.abs(np.sin(delta))))
        orientation = 0.0 if denominator < 1e-15 else float(np.sum(np.sin(delta)) / denominator)
        x_c[i] = 1.0 + orientation
    return {"time": time, "x_L": x_l, "x_C": x_c, "previous_index": previous}


def select_state_clock(
    history: dict[str, np.ndarray],
    amplitude: np.ndarray,
    relation: np.ndarray,
    power_peak_time: float,
) -> dict[str, object]:
    t = history["time"]
    x_l = history["x_L"]
    eligible = np.isfinite(x_l) & (t <= power_peak_time) & (relation <= 1.0)
    candidates: list[dict[str, float | int]] = []
    for i in range(1, len(x_l)):
        if not (eligible[i - 1] and eligible[i]):
            continue
        if not (x_l[i - 1] >= 1.0 and x_l[i] < 1.0):
            continue
        frac = float((x_l[i - 1] - 1.0) / max(x_l[i - 1] - x_l[i], EPS))
        candidates.append({
            "i": i,
            "time_M": float(t[i - 1] + frac * (t[i] - t[i - 1])),
            "amplitude": float(max(amplitude[i - 1], amplitude[i])),
            "x_C": float(history["x_C"][i - 1] + frac * (history["x_C"][i] - history["x_C"][i - 1])),
        })
    if candidates:
        chosen = max(candidates, key=lambda row: float(row["amplitude"]))
        mode = "expansion_to_contraction_crossing"
    else:
        eligible_indices = np.flatnonzero(eligible)
        i = int(eligible_indices[np.argmin(np.abs(x_l[eligible] - 1.0))])
        chosen = {
            "i": i,
            "time_M": float(t[i]),
            "amplitude": float(amplitude[i]),
            "x_C": float(history["x_C"][i]),
        }
        mode = "fallback_nearest_x_L_ridge"
    i = int(chosen["i"])
    return {
        "k": i,
        "time_M": float(chosen["time_M"]),
        "x_L": 1.0 if mode.startswith("expansion") else float(x_l[i]),
        "x_C": float(chosen["x_C"]),
        "selection_mode": mode,
        "crossing_count": len(candidates),
        "eligible_count": int(np.sum(eligible)),
        "eligible": eligible,
    }


def compact_path_clock(clock: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in clock.items() if key not in {"k", "eligible"}}


def compact_state_clock(clock: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in clock.items() if key not in {"k", "eligible"}}


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    source = np.load(SOURCE)
    time = np.asarray(source["time"], dtype=float)
    child_phase = np.asarray(source["theta_hat"], dtype=float)
    parent_phase = np.asarray(source["parent_phase"], dtype=float)
    power = np.asarray(source["total_power"], dtype=float)
    amplitude = np.sqrt(np.maximum(power, 0.0))
    cadence = np.asarray(source["cadence"], dtype=float)
    relation = np.asarray(source["relation_ara"], dtype=float)
    power_peak_time = float(time[np.argmax(power)])

    state = build_state_history(amplitude, child_phase, cadence, time)
    state_clock = select_state_clock(state, amplitude, relation, power_peak_time)

    path = build_path_history(child_phase, time, reverse_support=False)
    path_clock = select_path_clock(path, relation, power_peak_time)

    rational = build_path_history(child_phase, time, reverse_support=True)
    rational_clock = select_path_clock(rational, relation, power_peak_time)

    rng = np.random.default_rng(SEED)
    phase_variants = {
        "full_parent_phase": parent_phase,
        "quarter_record_roll": np.roll(child_phase, len(child_phase) // 4),
        "chronology_shuffle": child_phase[rng.permutation(len(child_phase))],
    }
    path_controls: dict[str, dict[str, object]] = {}
    rational_controls: dict[str, dict[str, object]] = {}
    for name, phase in phase_variants.items():
        control_path = build_path_history(phase, time, reverse_support=False)
        control_rational = build_path_history(phase, time, reverse_support=True)
        path_controls[name] = compact_path_clock(select_path_clock(control_path, relation, power_peak_time))
        rational_controls[name] = compact_path_clock(select_path_clock(control_rational, relation, power_peak_time))

    rolled_amplitude = np.roll(amplitude, len(amplitude) // 4)
    rolled_phase = np.roll(child_phase, len(child_phase) // 4)
    state_control_history = build_state_history(rolled_amplitude, rolled_phase, cadence, time)
    state_control_clock = compact_state_clock(
        select_state_clock(state_control_history, rolled_amplitude, relation, power_peak_time)
    )

    t436 = json.loads(T436_PREDICTION.read_text(encoding="utf-8"))

    np.savez_compressed(
        OUTPUT,
        waveform_time=time,
        waveform_amplitude=amplitude,
        waveform_power=power,
        relation_ara=relation,
        state_time=state["time"],
        state_x_L=state["x_L"],
        state_x_C=state["x_C"],
        state_eligible=np.asarray(state_clock["eligible"], dtype=np.uint8),
        path_time=path["time"],
        path_index=path["index"],
        path_x_P=path["x_P"],
        path_x_R=path["x_R"],
        path_rho=path["rho"],
        path_distance=path["distance"],
        path_eligible=np.asarray(path_clock["eligible"], dtype=np.uint8),
        rational_time=rational["time"],
        rational_index=rational["index"],
        rational_x_P=rational["x_P"],
        rational_x_R=rational["x_R"],
        rational_rho=rational["rho"],
        rational_distance=rational["distance"],
        rational_eligible=np.asarray(rational_clock["eligible"], dtype=np.uint8),
    )

    summary = {
        "status": "WAVEFORM_ONLY_FROZEN_PREDICTION",
        "evidence_class": "one-event method calibration; no population validation",
        "source": SOURCE.name,
        "answer_key_read_by_prediction": False,
        "late_parent_basin": "relation_ara <= 1 and timestamp <= waveform-power maximum",
        "window_samples": WINDOW,
        "step_samples": STEP,
        "max_lag_samples": MAX_LAG,
        "power_peak_time_M": power_peak_time,
        "state_clock": compact_state_clock(state_clock),
        "path_history_clock": compact_path_clock(path_clock),
        "dynamic_clock_unchanged_from_T436": {
            "time_M": float(t436["primary_predicted_time_M"]),
            "coordinates": t436["primary_at"],
        },
        "experimental_rationality_clock": compact_path_clock(rational_clock),
        "controls": {
            "state_quarter_record_roll": state_control_clock,
            "path_history": path_controls,
            "experimental_rationality": rational_controls,
        },
        "causality": {
            "state": "past/current support only",
            "path_history": "past-only 128-sample support",
            "dynamic": "past-only 128-sample support; exact T436 import",
            "experimental_rationality": "future 128-sample support read backward; retrospective only",
        },
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    RECEIPT.write_text(
        f"prediction_sha256  {sha256(OUTPUT)}\n"
        f"summary_sha256     {sha256(SUMMARY)}\n"
        f"protocol_sha256    {sha256(PROTOCOL)}\n"
        f"script_sha256      {sha256(Path(__file__))}\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
