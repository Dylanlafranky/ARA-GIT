"""T321: corrected same-arm, full-half-swing temporal Phi-handover test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import pathlib
import sys
from dataclasses import dataclass

import numpy as np
from scipy.signal import find_peaks


HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PENDULUM = ROOT / "analysis" / "pendulum_scripts"
sys.path.insert(0, str(PENDULUM))
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(HERE / ".mplconfig"))

import matplotlib.pyplot as plt

from pendulum_common import load_triple, load_triple_driven, rest_centered


TEST_ID = "T321-SAME-ARM-TEMPORAL-PHI-HANDOVER-v1"
PROTOCOL = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA256 = "073d577b7b423b95a6b6c912113b43c6d725458060b78b271ebfc6ea269a09eb"
RESULTS = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_RESULTS.json"
EVENTS = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER_EVENTS.csv"
FIGURE = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER.png"
FIGURE_SVG = HERE / "T321_SAME_ARM_TEMPORAL_PHI_HANDOVER.svg"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
DECIMATE = 20
N_PATH = 129
PDOM_S = 1.333
PROM_ARA = 0.02
EPS = 1e-12
SHIFT_FRACTIONS = (0.17, 0.31, 0.47)
CANDIDATES = {
    "1": 1.0,
    "sqrt2": math.sqrt(2.0),
    "1.5": 1.5,
    "phi": PHI,
    "sqrt3": math.sqrt(3.0),
    "2": 2.0,
}
MODES = ("angle_time", "angle_only", "phase_space_time")


@dataclass
class Swing:
    arm: int
    index: int
    direction: str
    start_sample: int
    end_sample: int
    start_time: float
    end_time: float
    center_time: float
    paths: dict[str, np.ndarray]


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def robust_scale(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=np.float64)
    med = float(np.median(values))
    scale = 1.4826 * float(np.median(np.abs(values - med)))
    if not np.isfinite(scale) or scale <= EPS:
        scale = float(np.std(values))
    if not np.isfinite(scale) or scale <= EPS:
        raise RuntimeError("Degenerate robust scale")
    return scale


def extrema(x: np.ndarray, fs: float) -> np.ndarray:
    distance = max(1, int(0.4 * PDOM_S * fs))
    prominence = PROM_ARA * np.pi
    hi, _ = find_peaks(x, prominence=prominence, distance=distance)
    lo, _ = find_peaks(-x, prominence=prominence, distance=distance)
    return np.sort(np.concatenate([hi, lo])).astype(int)


def development_scales() -> dict:
    cycle_parts: dict[int, list[np.ndarray]] = {1: [], 2: [], 3: []}
    velocity_parts: dict[int, list[np.ndarray]] = {1: [], 2: [], 3: []}
    turn_counts: dict[str, dict[str, int]] = {}
    for run in ("run1", "run2"):
        time, theta, velocity, fs = load_triple(run, decimate=DECIMATE)
        centered = rest_centered(theta)
        turn_counts[run] = {}
        for arm in (1, 2, 3):
            turns = extrema(np.asarray(centered[arm]), fs)
            if len(turns) < 3:
                raise RuntimeError(f"Insufficient development turns: {run} arm {arm}")
            cycle_parts[arm].append(np.asarray(time)[turns[2:]] - np.asarray(time)[turns[:-2]])
            velocity_parts[arm].append(np.asarray(velocity[arm], dtype=np.float64))
            turn_counts[run][str(arm)] = int(len(turns))
    return {
        "complete_cycle_s": {
            str(arm): float(np.median(np.concatenate(cycle_parts[arm])))
            for arm in (1, 2, 3)
        },
        "velocity_robust_scale": {
            str(arm): robust_scale(np.concatenate(velocity_parts[arm]))
            for arm in (1, 2, 3)
        },
        "turn_counts": turn_counts,
    }


def resample_segment(values: np.ndarray, start: int, end: int) -> np.ndarray:
    source = np.linspace(0.0, 1.0, end - start + 1)
    target = np.linspace(0.0, 1.0, N_PATH)
    return np.interp(target, source, np.asarray(values[start : end + 1], dtype=np.float64))


def make_swings(
    arm: int,
    time: np.ndarray,
    angle: np.ndarray,
    velocity: np.ndarray,
    turns: np.ndarray,
    cycle_s: float,
    velocity_scale: float,
) -> list[Swing]:
    swings: list[Swing] = []
    for index, (start, end) in enumerate(zip(turns[:-1], turns[1:])):
        start, end = int(start), int(end)
        if end <= start + 1:
            continue
        theta_path = resample_segment(angle, start, end)
        velocity_path = resample_segment(velocity, start, end)
        time_path = resample_segment(time, start, end)
        x_theta = 1.0 + theta_path / np.pi
        x_time = 2.0 * time_path / cycle_s
        direction = "increasing" if theta_path[-1] > theta_path[0] else "decreasing"
        paths = {
            "angle_time": np.column_stack([x_theta, x_time]),
            "angle_only": x_theta[:, None],
            "phase_space_time": np.column_stack(
                [x_theta, velocity_path / velocity_scale, x_time]
            ),
        }
        swings.append(
            Swing(
                arm=arm,
                index=index,
                direction=direction,
                start_sample=start,
                end_sample=end,
                start_time=float(time[start]),
                end_time=float(time[end]),
                center_time=float(0.5 * (time[start] + time[end])),
                paths=paths,
            )
        )
    return swings


def path_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.sum((a - b) ** 2, axis=1))))


def recenter_time(path: np.ndarray, source_center: float, target_center: float, cycle_s: float) -> np.ndarray:
    shifted = np.array(path, copy=True)
    shifted[:, -1] += 2.0 * (target_center - source_center) / cycle_s
    return shifted


def event_q(a0: Swing, b: Swing, a1: Swing, mode: str, replacement_b: Swing | None = None, cycle_s: float | None = None) -> tuple[float, float, float, float]:
    pa0 = a0.paths[mode]
    pb = b.paths[mode]
    if replacement_b is not None:
        pb = replacement_b.paths[mode]
        if mode in ("angle_time", "phase_space_time"):
            if cycle_s is None:
                raise RuntimeError("cycle_s required for time re-centring")
            pb = recenter_time(pb, replacement_b.center_time, b.center_time, cycle_s)
    pa1 = a1.paths[mode]
    d0 = path_distance(pa0, pb)
    d1 = path_distance(pb, pa1)
    direct = path_distance(pa0, pa1)
    route = d0 + d1
    if route <= EPS:
        raise RuntimeError("Degenerate A-B-A route")
    return 2.0 * direct / route, direct, d0, d1


def extract_dataset(run: str, scales: dict, driven: bool = False) -> tuple[list[dict], dict, dict[int, list[Swing]]]:
    loader = load_triple_driven if driven else load_triple
    time, theta, velocity, fs = loader(run, decimate=DECIMATE)
    centered = rest_centered(theta)
    all_swings: dict[int, list[Swing]] = {}
    rows: list[dict] = []
    meta = {
        "run": run,
        "driven": driven,
        "samples": int(len(time)),
        "fs_hz": float(fs),
        "duration_s": float(time[-1] - time[0]),
        "arms": {},
    }
    for arm in (1, 2, 3):
        angle = np.asarray(centered[arm], dtype=np.float64)
        turns = extrema(angle, fs)
        cycle_s = float(scales["complete_cycle_s"][str(arm)])
        vel_scale = float(scales["velocity_robust_scale"][str(arm)])
        swings = make_swings(
            arm,
            np.asarray(time, dtype=np.float64),
            angle,
            np.asarray(velocity[arm], dtype=np.float64),
            turns,
            cycle_s,
            vel_scale,
        )
        all_swings[arm] = swings
        eligible = 0
        for i in range(len(swings) - 2):
            a0, b, a1 = swings[i : i + 3]
            if not (a0.direction == a1.direction and b.direction != a0.direction):
                continue
            values: dict[str, float] = {}
            for mode in MODES:
                q, direct, d0, d1 = event_q(a0, b, a1, mode)
                values[f"q_{mode}"] = q
                values[f"direct_{mode}"] = direct
                values[f"leg0_{mode}"] = d0
                values[f"leg1_{mode}"] = d1
            rows.append(
                {
                    "dataset": "driven_triple1" if driven else "free_run3",
                    "arm": arm,
                    "event_index": eligible,
                    "phase_direction": a0.direction,
                    "a0_swing_index": a0.index,
                    "b_swing_index": b.index,
                    "a1_swing_index": a1.index,
                    "time_mid_s": b.center_time,
                    "a0_duration_s": a0.end_time - a0.start_time,
                    "b_duration_s": b.end_time - b.start_time,
                    "a1_duration_s": a1.end_time - a1.start_time,
                    **values,
                }
            )
            eligible += 1
        meta["arms"][str(arm)] = {
            "turns": int(len(turns)),
            "complete_half_swings": int(len(swings)),
            "eligible_aba_events": int(eligible),
        }
    return rows, meta, all_swings


def candidate_errors(values: np.ndarray) -> dict[str, float]:
    return {
        name: float(np.median(np.abs(values - target)))
        for name, target in CANDIDATES.items()
    }


def winner(errors: dict[str, float]) -> tuple[str, bool]:
    ordered = sorted(errors.items(), key=lambda item: (item[1], item[0]))
    unique = len(ordered) == 1 or ordered[1][1] - ordered[0][1] > 1e-9
    return ordered[0][0], unique


def summarize_rows(rows: list[dict], mode: str) -> dict:
    key = f"q_{mode}"
    values = np.asarray([row[key] for row in rows], dtype=np.float64)
    errors = candidate_errors(values)
    best, unique = winner(errors)
    by_direction = {}
    for direction in ("increasing", "decreasing"):
        subset = np.asarray(
            [row[key] for row in rows if row["phase_direction"] == direction],
            dtype=np.float64,
        )
        sub_errors = candidate_errors(subset)
        sub_best, sub_unique = winner(sub_errors)
        by_direction[direction] = {
            "n": int(len(subset)),
            "median_q": float(np.median(subset)),
            "candidate_errors": sub_errors,
            "winner": sub_best,
            "unique_winner": sub_unique,
        }
    by_arm = {}
    for arm in (1, 2, 3):
        subset = np.asarray([row[key] for row in rows if row["arm"] == arm], dtype=np.float64)
        sub_errors = candidate_errors(subset)
        sub_best, sub_unique = winner(sub_errors)
        by_arm[str(arm)] = {
            "n": int(len(subset)),
            "median_q": float(np.median(subset)),
            "candidate_errors": sub_errors,
            "winner": sub_best,
            "unique_winner": sub_unique,
        }
    return {
        "n": int(len(values)),
        "median_q": float(np.median(values)),
        "q25": float(np.quantile(values, 0.25)),
        "q75": float(np.quantile(values, 0.75)),
        "candidate_errors": errors,
        "winner": best,
        "unique_winner": unique,
        "by_direction": by_direction,
        "by_arm": by_arm,
    }


def shifted_controls(rows: list[dict], swings: dict[int, list[Swing]], scales: dict) -> dict:
    controls: dict[str, dict] = {}
    for fraction in SHIFT_FRACTIONS:
        q_values: list[float] = []
        for arm in (1, 2, 3):
            arm_rows = [row for row in rows if row["arm"] == arm]
            cycle_s = float(scales["complete_cycle_s"][str(arm)])
            for direction in ("increasing", "decreasing"):
                group = [row for row in arm_rows if row["phase_direction"] == direction]
                if not group:
                    continue
                shift = max(1, int(round(fraction * len(group)))) % len(group)
                replacements = [group[(i + shift) % len(group)] for i in range(len(group))]
                for row, replacement in zip(group, replacements):
                    a0 = swings[arm][int(row["a0_swing_index"])]
                    b = swings[arm][int(row["b_swing_index"])]
                    a1 = swings[arm][int(row["a1_swing_index"])]
                    replacement_b = swings[arm][int(replacement["b_swing_index"])]
                    q, _, _, _ = event_q(
                        a0,
                        b,
                        a1,
                        "angle_time",
                        replacement_b=replacement_b,
                        cycle_s=cycle_s,
                    )
                    q_values.append(q)
        values = np.asarray(q_values, dtype=np.float64)
        controls[f"{fraction:.2f}"] = {
            "n": int(len(values)),
            "median_q": float(np.median(values)),
            "median_abs_phi_error": float(np.median(np.abs(values - PHI))),
            "candidate_errors": candidate_errors(values),
        }
    return controls


def write_events(rows: list[dict]) -> None:
    with EVENTS.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def draw_figure(rows: list[dict], result: dict, swings: dict[int, list[Swing]]) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(16, 9.5), constrained_layout=True)
    fig.suptitle(
        "T321 — same-arm temporal Phi handover",
        fontsize=17,
        weight="bold",
    )

    # One concrete complete A-B-A trajectory, shown in raw rest-centred angle.
    sample = next(row for row in rows if row["arm"] == 1)
    for label, field, color in (
        ("A(k)", "a0_swing_index", "#2563EB"),
        ("B(k)", "b_swing_index", "#D97706"),
        ("A(k+1)", "a1_swing_index", "#0F766E"),
    ):
        swing = swings[1][int(sample[field])]
        progress = np.linspace(0.0, 1.0, N_PATH)
        angle = (swing.paths["angle_only"][:, 0] - 1.0) * 180.0
        axes[0, 0].plot(progress, angle, label=label, color=color, linewidth=2)
    axes[0, 0].set(
        title="One eligible same-arm event",
        xlabel="fraction of complete half-swing",
        ylabel="rest-centred angle (degrees)",
    )
    axes[0, 0].legend()

    colors = {1: "#2563EB", 2: "#7C3AED", 3: "#0F766E"}
    for arm in (1, 2, 3):
        take = [row for row in rows if row["arm"] == arm]
        axes[0, 1].scatter(
            [row["time_mid_s"] for row in take],
            [row["q_angle_time"] for row in take],
            s=14,
            alpha=0.6,
            label=f"arm {arm}",
            color=colors[arm],
        )
    axes[0, 1].axhline(PHI, color="#D97706", linestyle="--", linewidth=2, label="Phi")
    axes[0, 1].set(title="Primary ARA route through time", xlabel="time (s)", ylabel="q on 0–2 ARA", ylim=(0, 2.03))
    axes[0, 1].legend(fontsize=8)

    inc = np.asarray([row["q_angle_time"] for row in rows if row["phase_direction"] == "increasing"])
    dec = np.asarray([row["q_angle_time"] for row in rows if row["phase_direction"] == "decreasing"])
    bins = np.linspace(0.0, 2.0, 45)
    axes[0, 2].hist(inc, bins=bins, alpha=0.62, label="increasing / Phase A")
    axes[0, 2].hist(dec, bins=bins, alpha=0.62, label="decreasing / Phase B")
    axes[0, 2].axvline(PHI, color="#D97706", linestyle="--", linewidth=2)
    axes[0, 2].set(title="Reversible phase branches", xlabel="q", ylabel="events")
    axes[0, 2].legend(fontsize=8)

    errors = result["evaluation"]["angle_time"]["candidate_errors"]
    axes[1, 0].bar(list(errors), list(errors.values()), color="#D4A017")
    axes[1, 0].set(title="Frozen primary landmarks", ylabel="median |q − landmark|")
    axes[1, 0].tick_params(axis="x", rotation=25)

    control_names = ["real", "shift 17%", "shift 31%", "shift 47%"]
    control_errors = [errors["phi"]] + [
        result["shifted_b_controls"][key]["median_abs_phi_error"]
        for key in ("0.17", "0.31", "0.47")
    ]
    axes[1, 1].bar(control_names, control_errors, color=["#2563EB", "#A3A3A3", "#A3A3A3", "#A3A3A3"])
    axes[1, 1].set(title="Observed B versus re-paired B controls", ylabel="median |q − Phi|")
    axes[1, 1].tick_params(axis="x", rotation=20)

    mode_names = ["angle + time\n(primary)", "angle only", "angle + velocity + time"]
    mode_values = [result["evaluation"][mode]["median_q"] for mode in MODES]
    axes[1, 2].bar(mode_names, mode_values, color=["#2563EB", "#94A3B8", "#0F766E"])
    axes[1, 2].axhline(PHI, color="#D97706", linestyle="--", linewidth=2, label="Phi")
    axes[1, 2].set(title="Coordinate sensitivity", ylabel="median q", ylim=(0, 2.03))
    axes[1, 2].tick_params(axis="x", rotation=12)
    axes[1, 2].legend()

    primary = result["evaluation"]["angle_time"]
    fig.text(
        0.5,
        0.004,
        f"Primary median q={primary['median_q']:.5f}; winner={primary['winner']}; "
        f"verdict={result['verdict']} ({result['gates_passed']}/5 gates). "
        "Run 3 evaluation; runs 1–2 supplied scales only.",
        ha="center",
        fontsize=10,
    )
    fig.savefig(FIGURE, dpi=180)
    fig.savefig(FIGURE_SVG)
    plt.close(fig)


def main() -> None:
    if sha256(PROTOCOL) != PROTOCOL_SHA256:
        raise RuntimeError("Frozen T321 protocol hash mismatch")

    scales = development_scales()
    evaluation_rows, evaluation_meta, evaluation_swings = extract_dataset("run3", scales)
    driven_rows, driven_meta, _ = extract_dataset("triple1", scales, driven=True)
    controls = shifted_controls(evaluation_rows, evaluation_swings, scales)

    evaluation = {mode: summarize_rows(evaluation_rows, mode) for mode in MODES}
    driven = {mode: summarize_rows(driven_rows, mode) for mode in MODES}
    primary = evaluation["angle_time"]
    gates = {
        "G1_phi_unique_pooled_primary_winner": primary["winner"] == "phi" and primary["unique_winner"],
        "G2_both_phase_directions_choose_phi": all(
            primary["by_direction"][direction]["winner"] == "phi"
            and primary["by_direction"][direction]["unique_winner"]
            for direction in ("increasing", "decreasing")
        ),
        "G3_at_least_two_arms_choose_phi": sum(
            primary["by_arm"][str(arm)]["winner"] == "phi"
            and primary["by_arm"][str(arm)]["unique_winner"]
            for arm in (1, 2, 3)
        )
        >= 2,
        "G4_median_within_0_08_of_phi": abs(primary["median_q"] - PHI) <= 0.08,
        "G5_real_b_pairing_beats_all_shifts": all(
            primary["candidate_errors"]["phi"]
            < controls[key]["median_abs_phi_error"]
            for key in controls
        ),
    }
    passed = int(sum(gates.values()))
    verdict = "SUPPORTED" if passed == 5 else "MIXED" if passed >= 3 else "NOT SUPPORTED"
    result = {
        "test_id": TEST_ID,
        "protocol_sha256": PROTOCOL_SHA256,
        "status": "frozen retrospective identity-boundary correction",
        "source": "dynamicslab MultiArm-Pendulum, Zenodo 10.5281/zenodo.6633719",
        "identity_boundary": "same arm; complete A half-swing -> intervening B half-swing -> next A half-swing",
        "primary_coordinate": "q = 2*d(A_k,A_k+1)/(d(A_k,B_k)+d(B_k,A_k+1)) in angle-time path space",
        "development_scales": scales,
        "evaluation_meta": evaluation_meta,
        "driven_transfer_meta": driven_meta,
        "evaluation": evaluation,
        "shifted_b_controls": controls,
        "driven_transfer": driven,
        "gates": gates,
        "gates_passed": passed,
        "gates_total": 5,
        "verdict": verdict,
        "boundary": (
            "This tests one fixed raw-data operationalization of the same-arm temporal handover. "
            "Sensitivity coordinates are descriptive and cannot rescue the frozen primary verdict."
        ),
    }
    write_events(evaluation_rows + driven_rows)
    RESULTS.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    draw_figure(evaluation_rows, result, evaluation_swings)
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
