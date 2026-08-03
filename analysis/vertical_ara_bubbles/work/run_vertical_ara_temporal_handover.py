from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from bubble_lineage import load_run


PHI = (1.0 + math.sqrt(5.0)) / 2.0
TARGETS = {
    "one": 1.0,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "two": 2.0,
}
MIN_STEP_M = 0.0005
PERMUTATIONS = 5000
PERMUTATION_CAP_PER_VIDEO = 250
BOOTSTRAPS = 5000
SEED = 20260801


def split_for_video(video: str) -> str:
    number = int(video[1:])
    if number <= 7:
        return "calibration"
    if number <= 28:
        return "evaluation"
    return "holdout"


def rank_average(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        ranks[order[i:j]] = (i + j - 1) / 2.0 + 1.0
        i = j
    return ranks


def spearman(x, y) -> tuple[float, int]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 4 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan"), int(len(x))
    return float(np.corrcoef(rank_average(x), rank_average(y))[0, 1]), int(len(x))


def target_distance(q_whole: float, q_lineage: float, target: float) -> float:
    return math.sqrt(
        math.log(q_whole / target) ** 2
        + math.log(q_lineage / target) ** 2
    )


def turn_tension(v_a: tuple[float, float], v_b: tuple[float, float]) -> float:
    a = math.hypot(*v_a)
    b = math.hypot(*v_b)
    if a <= 0 or b <= 0:
        return float("nan")
    cosine = (v_a[0] * v_b[0] + v_a[1] * v_b[1]) / (a * b)
    cosine = min(1.0, max(-1.0, cosine))
    return math.acos(cosine) / math.pi


def contiguous_segments(track: dict) -> list[list]:
    rows = [track[frame] for frame in sorted(track)]
    if not rows:
        return []
    segments: list[list] = []
    current = [rows[0]]
    for row in rows[1:]:
        if row.frame == current[-1].frame + 1:
            current.append(row)
        else:
            if len(current) >= 5:
                segments.append(current)
            current = [row]
    if len(current) >= 5:
        segments.append(current)
    return segments


def vector(a, b) -> tuple[float, float]:
    return (b.x - a.x, b.y - a.y)


def deterministic_shift(video: str, ident: int, n_steps: int) -> int:
    if n_steps <= 3:
        return 2
    digest = hashlib.sha256(f"{video}:{ident}:{SEED}".encode()).digest()
    return 2 + int.from_bytes(digest[:4], "little") % (n_steps - 2)


def extract_windows(source_dir: Path) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    diagnostics = defaultdict(int)
    for path in sorted(source_dir.glob("V*_Amp*_umf*.csv")):
        run = load_run(path)
        split = split_for_video(run.video)
        for ident, track in run.tracks.items():
            for segment_index, segment in enumerate(contiguous_segments(track)):
                diagnostics["segments"] += 1
                steps = [vector(a, b) for a, b in zip(segment, segment[1:])]
                speeds = [math.hypot(*step) for step in steps]
                shift = deterministic_shift(run.video, ident, len(steps))
                for i in range(len(segment) - 4):
                    diagnostics["candidate_windows"] += 1
                    s0, s1, s2, s3 = speeds[i:i + 4]
                    if s0 < MIN_STEP_M or s1 < MIN_STEP_M:
                        diagnostics["subresolution_handover"] += 1
                        continue
                    larger = max(s0, s1)
                    smaller = min(s0, s1)
                    q_whole = (larger + smaller) / larger
                    q_lineage = larger / smaller
                    shifted_partner = speeds[(i + shift) % len(speeds)]
                    shifted_distance = float("nan")
                    if shifted_partner >= MIN_STEP_M:
                        shifted_large = max(s0, shifted_partner)
                        shifted_small = min(s0, shifted_partner)
                        shifted_q_whole = (shifted_large + shifted_small) / shifted_large
                        shifted_q_lineage = shifted_large / shifted_small
                        shifted_distance = target_distance(shifted_q_whole, shifted_q_lineage, PHI)
                    else:
                        shifted_q_whole = float("nan")
                        shifted_q_lineage = float("nan")
                    future_turn = turn_tension(steps[i + 2], steps[i + 3])
                    immediate_turn = turn_tension(steps[i + 1], steps[i + 2])
                    future_speed_tension = (
                        abs(math.log(s3 / s2)) if s2 > 0 and s3 > 0 else float("nan")
                    )
                    frames_after_p2 = segment[-1].frame - segment[i + 2].frame
                    row = {
                        "split": split,
                        "video": run.video,
                        "file": path.name,
                        "amplitude": run.amplitude,
                        "umf": run.umf,
                        "track_id": ident,
                        "segment_index": segment_index,
                        "start_frame": segment[i].frame,
                        "time_sec": segment[i].time,
                        "s0_m": s0,
                        "s1_m": s1,
                        "s2_m": s2,
                        "s3_m": s3,
                        "handover_direction": "release" if s1 >= s0 else "accumulation",
                        "q_whole": q_whole,
                        "q_lineage": q_lineage,
                        "future_turn_tension": future_turn,
                        "future_speed_tension": future_speed_tension,
                        "immediate_turn_tension": immediate_turn,
                        "persists_10_frames": int(frames_after_p2 >= 10),
                        "distance_phi_shift_control": shifted_distance,
                        "nonoverlap": int(i % 4 == 0),
                    }
                    for name, target in TARGETS.items():
                        row[f"distance_{name}"] = target_distance(q_whole, q_lineage, target)
                        row[f"direct_distance_{name}"] = abs(math.log(q_lineage / target))
                        row[f"distance_{name}_shift_control"] = (
                            target_distance(shifted_q_whole, shifted_q_lineage, target)
                            if math.isfinite(shifted_q_whole) else float("nan")
                        )
                        row[f"direct_distance_{name}_shift_control"] = (
                            abs(math.log(shifted_q_lineage / target))
                            if math.isfinite(shifted_q_lineage) else float("nan")
                        )
                    row["golden_equality_residual"] = abs(math.log(q_whole / q_lineage))
                    row["golden_equality_residual_shift_control"] = (
                        abs(math.log(shifted_q_whole / shifted_q_lineage))
                        if math.isfinite(shifted_q_whole) else float("nan")
                    )
                    rows.append(row)
                    diagnostics["eligible_windows"] += 1
    return rows, dict(diagnostics)


def fit_free_target(rows: list[dict]) -> float:
    calibration = [row for row in rows if row["split"] == "calibration"]
    if not calibration:
        return float("nan")

    def loss(target: float) -> float:
        return statistics.mean(
            target_distance(row["q_whole"], row["q_lineage"], target)
            for row in calibration
        )

    left, right = 1.0, 2.0
    golden = (math.sqrt(5.0) - 1.0) / 2.0
    c = right - golden * (right - left)
    d = left + golden * (right - left)
    fc, fd = loss(c), loss(d)
    for _ in range(60):
        if fc <= fd:
            right, d, fd = d, c, fc
            c = right - golden * (right - left)
            fc = loss(c)
        else:
            left, c, fc = c, d, fd
            d = left + golden * (right - left)
            fd = loss(d)
    return (left + right) / 2.0


def fit_direct_free_target(rows: list[dict]) -> float:
    log_ratios = sorted(
        math.log(row["q_lineage"])
        for row in rows if row["split"] == "calibration"
    )
    return math.exp(statistics.median(log_ratios)) if log_ratios else float("nan")


def deterministic_inference_sample(rows: list[dict], split: str, outcome: str) -> list[dict]:
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["split"] == split and math.isfinite(float(row[outcome])):
            by_video[row["video"]].append(row)
    sampled: list[dict] = []
    for video in sorted(by_video):
        group = by_video[video]
        if len(group) <= PERMUTATION_CAP_PER_VIDEO:
            sampled.extend(group)
            continue
        indices = np.linspace(0, len(group) - 1, PERMUTATION_CAP_PER_VIDEO, dtype=int)
        sampled.extend(group[int(index)] for index in indices)
    return sampled


def blocked_permutation_multi(
    rows: list[dict], predictors: list[str], outcome: str
) -> dict[str, tuple[float, float, int]]:
    x_columns = [np.asarray([float(row[predictor]) for row in rows], dtype=float) for predictor in predictors]
    y = np.asarray([float(row[outcome]) for row in rows], dtype=float)
    groups = np.asarray([row["video"] for row in rows])
    mask = np.isfinite(y)
    for x in x_columns:
        mask &= np.isfinite(x)
    x_columns = [x[mask] for x in x_columns]
    y, groups = y[mask], groups[mask]
    n = len(y)
    if n < 4 or np.std(y) == 0:
        return {predictor: (float("nan"), float("nan"), n) for predictor in predictors}
    ranked_x = []
    for x in x_columns:
        rx = rank_average(x)
        if np.std(rx) == 0:
            ranked_x.append(np.full_like(rx, np.nan))
        else:
            ranked_x.append((rx - rx.mean()) / rx.std())
    x_matrix = np.column_stack(ranked_x)
    ry = rank_average(y)
    ry = (ry - ry.mean()) / ry.std()
    observed = np.mean(x_matrix * ry[:, None], axis=0)
    index_groups = [np.flatnonzero(groups == group) for group in np.unique(groups)]
    rng = np.random.default_rng(SEED)
    exceed = np.zeros(len(predictors), dtype=int)
    for _ in range(PERMUTATIONS):
        permuted = ry.copy()
        for idx in index_groups:
            if len(idx) > 1:
                permuted[idx] = permuted[idx][rng.permutation(len(idx))]
        rhos = np.mean(x_matrix * permuted[:, None], axis=0)
        exceed += rhos >= observed
    return {
        predictor: (
            float(observed[index]),
            float((exceed[index] + 1.0) / (PERMUTATIONS + 1.0)),
            n,
        )
        for index, predictor in enumerate(predictors)
    }


def cluster_bootstrap_difference(rows: list[dict], split: str, other: str) -> dict:
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["split"] == split:
            by_video[row["video"]].append(row)
    videos = sorted(by_video)
    if not videos:
        return {"difference": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}

    counts = np.asarray([len(by_video[video]) for video in videos], dtype=float)
    differences = np.asarray([
        sum(float(row["distance_phi"]) - float(row[f"distance_{other}"]) for row in by_video[video])
        for video in videos
    ], dtype=float)
    observed = float(differences.sum() / counts.sum())
    rng = np.random.default_rng(SEED + len(other) + len(split))
    draws = rng.integers(0, len(videos), size=(BOOTSTRAPS, len(videos)))
    samples = np.sum(differences[draws], axis=1) / np.sum(counts[draws], axis=1)
    return {
        "difference": observed,
        "ci_low": float(np.quantile(samples, 0.025)),
        "ci_high": float(np.quantile(samples, 0.975)),
    }


def cluster_bootstrap_shift_advantage(rows: list[dict], split: str, target: str) -> dict:
    by_video: dict[str, list[dict]] = defaultdict(list)
    shifted_name = f"distance_{target}_shift_control"
    for row in rows:
        if row["split"] == split and math.isfinite(float(row[shifted_name])):
            by_video[row["video"]].append(row)
    videos = sorted(by_video)
    if not videos:
        return {"difference": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
    counts = np.asarray([len(by_video[video]) for video in videos], dtype=float)
    differences = np.asarray([
        sum(float(row[f"distance_{target}"]) - float(row[shifted_name]) for row in by_video[video])
        for video in videos
    ], dtype=float)
    observed = float(differences.sum() / counts.sum())
    rng = np.random.default_rng(SEED + 100 + len(target) + len(split))
    draws = rng.integers(0, len(videos), size=(BOOTSTRAPS, len(videos)))
    samples = np.sum(differences[draws], axis=1) / np.sum(counts[draws], axis=1)
    return {
        "difference": observed,
        "ci_low": float(np.quantile(samples, 0.025)),
        "ci_high": float(np.quantile(samples, 0.975)),
    }


def cluster_bootstrap_paired_fields(rows: list[dict], split: str, observed_field: str, control_field: str) -> dict:
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if (
            row["split"] == split
            and math.isfinite(float(row[observed_field]))
            and math.isfinite(float(row[control_field]))
        ):
            by_video[row["video"]].append(row)
    videos = sorted(by_video)
    if not videos:
        return {"difference": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
    counts = np.asarray([len(by_video[video]) for video in videos], dtype=float)
    differences = np.asarray([
        sum(float(row[observed_field]) - float(row[control_field]) for row in by_video[video])
        for video in videos
    ], dtype=float)
    observed = float(differences.sum() / counts.sum())
    rng = np.random.default_rng(SEED + 200 + len(split) + len(observed_field))
    draws = rng.integers(0, len(videos), size=(BOOTSTRAPS, len(videos)))
    samples = np.sum(differences[draws], axis=1) / np.sum(counts[draws], axis=1)
    return {
        "difference": observed,
        "ci_low": float(np.quantile(samples, 0.025)),
        "ci_high": float(np.quantile(samples, 0.975)),
    }


def summarize(rows: list[dict], diagnostics: dict, free_target: float, direct_free_target: float) -> tuple[dict, list[dict]]:
    summary: dict = {
        "source": "Zenodo 10.5281/zenodo.15102957",
        "minimum_step_m": MIN_STEP_M,
        "permutations": PERMUTATIONS,
        "bootstraps": BOOTSTRAPS,
        "free_target_calibration": free_target,
        "direct_free_target_calibration": direct_free_target,
        "diagnostics": diagnostics,
        "splits": {},
        "placement_bootstrap": {},
        "adjacency_vs_shift_bootstrap": {},
        "outcomes": {},
        "post_protocol_audit": {},
    }
    target_rows: list[dict] = []
    for split in ("calibration", "evaluation", "holdout"):
        subset = [row for row in rows if row["split"] == split]
        videos = sorted({row["video"] for row in subset})
        split_summary = {"windows": len(subset), "videos": len(videos), "targets": {}}
        for name, target in {**TARGETS, "free_calibration": free_target}.items():
            values = [
                target_distance(row["q_whole"], row["q_lineage"], target)
                if name == "free_calibration" else float(row[f"distance_{name}"])
                for row in subset
            ]
            record = {
                "split": split,
                "series": "observed_adjacent",
                "target": name,
                "target_value": target,
                "windows": len(values),
                "mean_distance": statistics.mean(values) if values else float("nan"),
                "median_distance": statistics.median(values) if values else float("nan"),
            }
            split_summary["targets"][name] = record
            target_rows.append(record)
            if name in TARGETS:
                shifted_values_for_target = [
                    float(row[f"distance_{name}_shift_control"])
                    for row in subset
                    if math.isfinite(float(row[f"distance_{name}_shift_control"]))
                ]
                target_rows.append({
                    "split": split,
                    "series": "within_track_shift_control",
                    "target": name,
                    "target_value": target,
                    "windows": len(shifted_values_for_target),
                    "mean_distance": statistics.mean(shifted_values_for_target) if shifted_values_for_target else float("nan"),
                    "median_distance": statistics.median(shifted_values_for_target) if shifted_values_for_target else float("nan"),
                })
        phi_values = [float(row["distance_phi"]) for row in subset]
        shifted_values = [
            float(row["distance_phi_shift_control"])
            for row in subset if math.isfinite(float(row["distance_phi_shift_control"]))
        ]
        split_summary["phi_mean"] = statistics.mean(phi_values) if phi_values else float("nan")
        split_summary["phi_median"] = statistics.median(phi_values) if phi_values else float("nan")
        split_summary["shift_control_phi_mean"] = statistics.mean(shifted_values) if shifted_values else float("nan")
        split_summary["shift_control_phi_median"] = statistics.median(shifted_values) if shifted_values else float("nan")
        summary["splits"][split] = split_summary

        direct_targets = {**TARGETS, "free_calibration": direct_free_target}
        direct_records = {}
        for name, target in direct_targets.items():
            values = [
                abs(math.log(row["q_lineage"] / target))
                for row in subset
            ]
            direct_records[name] = {
                "target_value": target,
                "mean_direct_distance": statistics.mean(values) if values else float("nan"),
                "median_direct_distance": statistics.median(values) if values else float("nan"),
            }
        equality = [float(row["golden_equality_residual"]) for row in subset]
        equality_shift = [
            float(row["golden_equality_residual_shift_control"])
            for row in subset if math.isfinite(float(row["golden_equality_residual_shift_control"]))
        ]
        summary["post_protocol_audit"][split] = {
            "direct_targets": direct_records,
            "golden_equality_mean": statistics.mean(equality) if equality else float("nan"),
            "golden_equality_median": statistics.median(equality) if equality else float("nan"),
            "golden_equality_shift_mean": statistics.mean(equality_shift) if equality_shift else float("nan"),
            "golden_equality_shift_median": statistics.median(equality_shift) if equality_shift else float("nan"),
        }

    for split in ("evaluation", "holdout"):
        summary["placement_bootstrap"][split] = {
            other: cluster_bootstrap_difference(rows, split, other)
            for other in TARGETS if other != "phi"
        }
        summary["adjacency_vs_shift_bootstrap"][split] = {
            target: cluster_bootstrap_shift_advantage(rows, split, target)
            for target in TARGETS
        }
        summary["post_protocol_audit"][split]["golden_equality_adjacent_minus_shift_bootstrap"] = (
            cluster_bootstrap_paired_fields(
                rows,
                split,
                "golden_equality_residual",
                "golden_equality_residual_shift_control",
            )
        )
        summary["outcomes"][split] = {}
        inference_rows = deterministic_inference_sample(rows, split, "future_turn_tension")
        predictor_names = [f"distance_{name}" for name in TARGETS] + ["distance_phi_shift_control"]
        multi_results = blocked_permutation_multi(
            inference_rows, predictor_names, "future_turn_tension"
        )
        for name in TARGETS:
            rho, p_value, n = multi_results[f"distance_{name}"]
            summary["outcomes"][split][name] = {
                "future_turn_spearman": rho,
                "future_turn_one_sided_p": p_value,
                "inference_windows": n,
            }
        rho, p_value, n = multi_results["distance_phi_shift_control"]
        summary["outcomes"][split]["phi_shift_control"] = {
            "future_turn_spearman": rho,
            "future_turn_one_sided_p": p_value,
            "inference_windows": n,
        }
        nonoverlap = [row for row in inference_rows if row["nonoverlap"]]
        nonoverlap_result = blocked_permutation_multi(
            nonoverlap, ["distance_phi"], "future_turn_tension"
        )
        rho, p_value, n = nonoverlap_result["distance_phi"]
        summary["outcomes"][split]["phi_nonoverlap"] = {
            "future_turn_spearman": rho,
            "future_turn_one_sided_p": p_value,
            "inference_windows": n,
        }
    return summary, target_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_deterministic_sample(path: Path, rows: list[dict], max_rows: int = 10000) -> None:
    ordered = sorted(
        rows,
        key=lambda row: hashlib.sha256(
            f"{row['video']}:{row['track_id']}:{row['start_frame']}:{SEED}".encode()
        ).digest(),
    )
    write_csv(path, ordered[:max_rows])


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    source = base / "source_data"
    results = base / "results"
    rows, diagnostics = extract_windows(source)
    if not rows:
        raise SystemExit("No eligible temporal windows found")
    print(f"Extracted {len(rows):,} eligible windows", flush=True)
    free_target = fit_free_target(rows)
    print(f"Calibration free target: {free_target:.9f}", flush=True)
    direct_free_target = fit_direct_free_target(rows)
    print(f"Calibration direct-ratio free target: {direct_free_target:.9f}", flush=True)
    summary, target_rows = summarize(rows, diagnostics, free_target, direct_free_target)
    results.mkdir(parents=True, exist_ok=True)
    write_csv(results / "temporal_ara_target_results.csv", target_rows)
    write_deterministic_sample(results / "temporal_ara_window_sample.csv", rows)
    summary_path = results / "temporal_ara_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8")
    for path in (
        results / "temporal_ara_target_results.csv",
        results / "temporal_ara_window_sample.csv",
        summary_path,
    ):
        digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        print(f"{path.name}\t{digest}")
    print(json.dumps(summary, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
