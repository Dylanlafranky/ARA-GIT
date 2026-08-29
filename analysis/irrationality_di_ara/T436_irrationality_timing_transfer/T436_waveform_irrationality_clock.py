"""T436 waveform-only Irrationality Di-ARA timing transfer.

This stage reads T435's waveform-only prediction artifact and does not read the
SXS horizon or metadata answer keys.  The equations are transferred from the
frozen T419/T421 time-facing instrument.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
T435 = HERE.parent / "T435_blind_ara_binary_inversion"
SOURCE = T435 / "results" / "T435_WAVEFORM_ONLY_PREDICTION.npz"
PROTOCOL = HERE / "T436_FROZEN_PROTOCOL.md"
OUTPUT = RESULTS / "T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.npz"
SUMMARY = RESULTS / "T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.json"
RECEIPT = RESULTS / "T436_PREDICTION_SHA256.txt"

WINDOW = 128
STEP = 4
MAX_LAG = 32
K_NEIGHBOURS = 5
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
    predicted = (np.angle(vectors) / (2 * np.pi)) % 1.0
    predicted[np.abs(vectors) < 1e-12] = circular_mean(train_y)
    return predicted


def relation_metrics(z: np.ndarray) -> tuple[float, float, float, float, float]:
    """Return U, R, H and the two predictor losses using T419/T421 equations."""
    split = len(z) // 2
    train_x, train_y = z[: split - 1], z[1:split]
    test_x, test_y = z[split:-1], z[split + 1 :]
    prediction = knn_predict(train_x, train_y, test_x)
    null_prediction = np.full_like(test_y, circular_mean(train_y))
    local_loss = float(np.mean(circular_loss(test_y, prediction)))
    null_loss = float(np.mean(circular_loss(test_y, null_prediction)))
    denominator = local_loss + null_loss
    openness = 1.0 if denominator <= EPS else 2.0 * local_loss / denominator

    vector = np.exp(2j * np.pi * z)
    relations = np.asarray([
        np.mean(vector[lag:] * np.conj(vector[:-lag]))
        for lag in range(1, MAX_LAG + 1)
    ])
    closure = 2.0 * float(np.median(np.abs(relations)))
    parent_h = 2.0 * float(np.median(np.abs(np.angle(relations))) / np.pi)
    return openness, closure, parent_h, local_loss, null_loss


def build_history(phase_radians: np.ndarray, time: np.ndarray) -> dict[str, np.ndarray]:
    z = (np.asarray(phase_radians, dtype=float) / (2.0 * np.pi)) % 1.0
    ends = np.arange(WINDOW - 1, len(z), STEP, dtype=int)
    rows = np.empty((len(ends), 5), dtype=float)
    for k, end in enumerate(ends):
        rows[k] = relation_metrics(z[end - WINDOW + 1 : end + 1])
    return {
        "index": ends,
        "time": time[ends],
        "U": rows[:, 0],
        "R": rows[:, 1],
        "H": rows[:, 2],
        "local_loss": rows[:, 3],
        "null_loss": rows[:, 4],
    }


def choose_clock(history: dict[str, np.ndarray], relation: np.ndarray, power: np.ndarray) -> dict[str, float | int]:
    idx = history["index"].astype(int)
    t = history["time"]
    rel = relation[idx]
    power_peak_time = float(t[np.argmax(power[idx])])
    eligible = (t <= power_peak_time) & (rel <= 1.0)
    if not np.any(eligible):
        raise RuntimeError("Frozen late parent basin is empty")

    child_distance = np.abs(history["U"] - history["R"])
    parent_distance = np.abs(history["H"] - 1.0)
    lock_distance = np.sqrt(child_distance**2 + parent_distance**2)

    eligible_indices = np.flatnonzero(eligible)
    primary_k = int(eligible_indices[np.argmin(lock_distance[eligible])])
    child_k = int(eligible_indices[np.argmin(child_distance[eligible])])
    parent_k = int(eligible_indices[np.argmin(parent_distance[eligible])])
    return {
        "primary_k": primary_k,
        "primary_time": float(t[primary_k]),
        "child_only_k": child_k,
        "child_only_time": float(t[child_k]),
        "parent_only_k": parent_k,
        "parent_only_time": float(t[parent_k]),
        "power_peak_time": power_peak_time,
        "eligible_count": int(np.sum(eligible)),
        "lock_distance": lock_distance,
        "child_distance": child_distance,
        "parent_distance": parent_distance,
        "eligible": eligible,
        "relation_at_reads": rel,
    }


def crossings(history: dict[str, np.ndarray], eligible: np.ndarray) -> list[dict[str, float]]:
    d = history["U"] - history["R"]
    output: list[dict[str, float]] = []
    for i in range(len(d) - 1):
        if not (eligible[i] and eligible[i + 1]):
            continue
        if d[i] == 0.0:
            frac = 0.0
        elif d[i] * d[i + 1] > 0:
            continue
        else:
            frac = float(abs(d[i]) / max(abs(d[i]) + abs(d[i + 1]), EPS))
        interp = lambda a: float(a[i] + frac * (a[i + 1] - a[i]))
        output.append({
            "time": interp(history["time"]),
            "U_equals_R": 0.5 * (interp(history["U"]) + interp(history["R"])),
            "H": interp(history["H"]),
            "parent_ridge_distance": abs(interp(history["H"]) - 1.0),
        })
    return output


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    source = np.load(SOURCE)
    time = np.asarray(source["time"], dtype=float)
    child_phase = np.asarray(source["theta_hat"], dtype=float)
    parent_phase = np.asarray(source["parent_phase"], dtype=float)
    relation = np.asarray(source["relation_ara"], dtype=float)
    power = np.asarray(source["total_power"], dtype=float)

    variants = {
        "primary_half_phase": child_phase,
        "wrong_rung_unhalved": parent_phase,
        "quarter_shift": np.roll(child_phase, len(child_phase) // 4),
        "reverse_chronology": child_phase[::-1],
    }
    histories: dict[str, dict[str, np.ndarray]] = {}
    clocks: dict[str, dict[str, float | int]] = {}
    for name, phase in variants.items():
        histories[name] = build_history(phase, time)
        clocks[name] = choose_clock(histories[name], relation, power)

    primary = histories["primary_half_phase"]
    clock = clocks["primary_half_phase"]
    cross = crossings(primary, np.asarray(clock["eligible"], dtype=bool))

    arrays: dict[str, np.ndarray] = {
        "time": primary["time"],
        "index": primary["index"],
        "relation_at_reads": np.asarray(clock["relation_at_reads"]),
        "eligible": np.asarray(clock["eligible"], dtype=np.uint8),
        "lock_distance": np.asarray(clock["lock_distance"]),
        "child_distance": np.asarray(clock["child_distance"]),
        "parent_distance": np.asarray(clock["parent_distance"]),
    }
    for name, history in histories.items():
        for field in ("U", "R", "H", "local_loss", "null_loss"):
            arrays[f"{name}_{field}"] = np.asarray(history[field])
    np.savez_compressed(OUTPUT, **arrays)

    summary = {
        "status": "WAVEFORM_ONLY_METHOD_TRANSFER_PREDICTION",
        "source": str(SOURCE.name),
        "answer_key_read_by_prediction": False,
        "window_samples": WINDOW,
        "step_samples": STEP,
        "max_lag_samples": MAX_LAG,
        "sample_dt_M": float(np.median(np.diff(time))),
        "history_duration_M": float((WINDOW - 1) * np.median(np.diff(time))),
        "eligible_parent_basin": "relation_ara <= 1 and time <= waveform total-power maximum",
        "primary_predicted_time_M": float(clock["primary_time"]),
        "primary_at": {
            "U": float(primary["U"][int(clock["primary_k"])]),
            "R": float(primary["R"][int(clock["primary_k"])]),
            "H": float(primary["H"][int(clock["primary_k"])]),
            "child_distance_abs_U_minus_R": float(np.asarray(clock["child_distance"])[int(clock["primary_k"])]),
            "parent_distance_abs_H_minus_1": float(np.asarray(clock["parent_distance"])[int(clock["primary_k"])]),
            "joint_lock_distance": float(np.asarray(clock["lock_distance"])[int(clock["primary_k"])]),
            "relation_ara": float(np.asarray(clock["relation_at_reads"])[int(clock["primary_k"])]),
        },
        "waveform_power_peak_time_M": float(clock["power_peak_time"]),
        "single_distance_times_M": {
            "child_only_abs_U_minus_R": float(clock["child_only_time"]),
            "parent_only_abs_H_minus_1": float(clock["parent_only_time"]),
        },
        "phase_control_times_M": {
            name: float(item["primary_time"])
            for name, item in clocks.items()
            if name != "primary_half_phase"
        },
        "eligible_read_count": int(clock["eligible_count"]),
        "eligible_child_crossing_count": len(cross),
        "eligible_child_crossings": cross,
        "selection_rule": "minimum sqrt((U-R)^2 + (H-1)^2) in frozen late parent basin",
        "known_answer_status": "not read by this script; already known historically from T435",
    }
    SUMMARY.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    RECEIPT.write_text(
        f"prediction_sha256  {sha256(OUTPUT)}\n"
        f"protocol_sha256    {sha256(PROTOCOL)}\n"
        f"script_sha256      {sha256(Path(__file__))}\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

