from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

from bubble_lineage import Candidate, contiguous_forward, detect_candidates, load_run


PHI = (1.0 + math.sqrt(5.0)) / 2.0
TARGETS = {
    "one": 1.0,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "two": 2.0,
}

CONFIGS = {
    "strict": {},
    "primary": {
        "min_child_age": 2,
        "min_parent_life": 5,
        "closure_min": 0.65,
        "closure_max": 1.35,
        "separation_max": 2.25,
        "center_max": 1.15,
        "isolation_radius": 1.15,
    },
    "broad": {
        "min_child_age": 2,
        "min_parent_life": 4,
        "closure_min": 0.60,
        "closure_max": 1.40,
        "separation_max": 2.50,
        "center_max": 1.25,
        "isolation_radius": 1.00,
        "ambiguity_min": 1.05,
    },
}


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


def spearman(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 4 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan"), int(len(x))
    return float(np.corrcoef(rank_average(x), rank_average(y))[0, 1]), int(len(x))


def blocked_permutation_p(x, y, groups, observed, *, permutations=5000, seed=20260801):
    if not math.isfinite(observed):
        return float("nan")
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    groups = np.asarray(groups)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y, groups = x[mask], y[mask], groups[mask]
    if len(x) < 4:
        return float("nan")
    index_groups = [np.flatnonzero(groups == group) for group in np.unique(groups)]
    rng = np.random.default_rng(seed)
    exceed = 0
    for _ in range(permutations):
        permuted = y.copy()
        for idx in index_groups:
            if len(idx) > 1:
                permuted[idx] = permuted[rng.permutation(idx)]
        rho, _ = spearman(x, permuted)
        if math.isfinite(rho) and rho >= observed:
            exceed += 1
    return (exceed + 1.0) / (permutations + 1.0)


def self_similar_distance(child_ratio: float, parent_ratio: float, target: float) -> float:
    return math.sqrt(math.log(child_ratio / target) ** 2 + math.log(parent_ratio / target) ** 2)


def event_record(event: Candidate, detector: str):
    children = sorted((event.child_a, event.child_b), key=lambda bubble: bubble.area)
    small, large = children
    parent_track = contiguous_forward(event.run.tracks[event.parent.ident], event.frame + 1)
    circularity = [row.circularity for row in parent_track if math.isfinite(row.circularity)]
    life_frames = len(parent_track)
    tension = float("nan")
    plateau = float("nan")
    settle_frames = float("nan")
    settled = False
    if len(circularity) >= 2:
        diffs = [abs(b - a) for a, b in zip(circularity, circularity[1:])]
        scale = max(statistics.median(abs(v) for v in circularity), 0.05)
        tension = statistics.mean(diffs) / scale
    if len(circularity) >= 5:
        plateau = statistics.median(circularity[-3:])
        tolerance = 0.10 * max(abs(plateau), 0.05)
        for idx in range(1, len(circularity) - 2):
            if all(abs(value - plateau) <= tolerance for value in circularity[idx:idx + 3]):
                settle_frames = idx
                settled = True
                break

    child_ratio = large.area / small.area
    parent_ratio = event.parent.area / large.area
    row = {
        "detector": detector,
        "split": split_for_video(event.run.video),
        "video": event.run.video,
        "file": event.run.path.name,
        "amplitude": event.run.amplitude,
        "umf": event.run.umf,
        "frame": event.frame,
        "time_sec": event.child_a.time,
        "child_small_id": small.ident,
        "child_large_id": large.ident,
        "parent_id": event.parent.ident,
        "child_small_area_m2": small.area,
        "child_large_area_m2": large.area,
        "parent_area_m2": event.parent.area,
        "child_ratio": child_ratio,
        "parent_ratio": parent_ratio,
        "vertical_equality_gap": abs(math.log(child_ratio / parent_ratio)),
        "closure": event.closure,
        "separation_norm": event.separation_norm,
        "separation_change": event.separation_change,
        "center_norm": event.center_norm,
        "detector_score": event.score,
        "ambiguity_ratio": event.ambiguity_ratio,
        "parent_y_m": event.parent.y,
        "parent_speed_reported": math.hypot(event.parent.vx, event.parent.vy),
        "parent_life_frames": life_frames,
        "parent_life_sec": life_frames * 0.02,
        "circularity_initial": circularity[0] if circularity else float("nan"),
        "circularity_plateau": plateau,
        "circularity_tension": tension,
        "settled": int(settled),
        "settle_frames": settle_frames,
        "settle_sec": settle_frames * 0.02 if math.isfinite(settle_frames) else float("nan"),
    }
    for name, target in TARGETS.items():
        row[f"distance_{name}"] = self_similar_distance(child_ratio, parent_ratio, target)
    return row


def analyze_target(rows, split, metric, target_name, *, invert=False):
    subset = [row for row in rows if row["split"] == split and math.isfinite(float(row[metric]))]
    x = [row[f"distance_{target_name}"] for row in subset]
    y = [-float(row[metric]) if invert else float(row[metric]) for row in subset]
    groups = [row["video"] for row in subset]
    rho, n = spearman(x, y)
    p = blocked_permutation_p(x, y, groups, rho)
    detector = subset[0]["detector"] if subset else "unknown"
    return {"detector": detector, "target": target_name, "split": split, "metric": metric, "n": n, "rho_expected_positive": rho, "blocked_p_one_sided": p}


def free_optimum(rows, split, metric, *, invert=False):
    subset = [row for row in rows if row["split"] == split and math.isfinite(float(row[metric]))]
    y = [-float(row[metric]) if invert else float(row[metric]) for row in subset]
    best = None
    for target in np.linspace(1.0, 2.0, 401):
        x = [self_similar_distance(row["child_ratio"], row["parent_ratio"], float(target)) for row in subset]
        rho, n = spearman(x, y)
        if math.isfinite(rho) and (best is None or rho > best["rho"]):
            best = {"target": float(target), "rho": rho, "n": n}
    return best


def evaluate_free_target(rows, target, split, metric, *, invert=False):
    subset = [row for row in rows if row["split"] == split and math.isfinite(float(row[metric]))]
    x = [self_similar_distance(row["child_ratio"], row["parent_ratio"], target) for row in subset]
    y = [-float(row[metric]) if invert else float(row[metric]) for row in subset]
    groups = [row["video"] for row in subset]
    rho, n = spearman(x, y)
    return {
        "detector": subset[0]["detector"] if subset else "unknown",
        "target": target,
        "split": split,
        "metric": metric,
        "n": n,
        "rho_expected_positive": rho,
        "blocked_p_one_sided": blocked_permutation_p(x, y, groups, rho),
    }


def finite_summary(values):
    values = sorted(float(v) for v in values if math.isfinite(float(v)))
    if not values:
        return None
    def q(p):
        return float(np.quantile(values, p))
    return {"n": len(values), "min": values[0], "q25": q(0.25), "median": q(0.5), "q75": q(0.75), "max": values[-1]}


def write_csv(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(data_dir: str, output_dir: str):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    runs = [load_run(path) for path in sorted(Path(data_dir).glob("*.csv"))]

    all_rows = []
    detector_counts = defaultdict(lambda: defaultdict(int))
    for detector, config in CONFIGS.items():
        for run in runs:
            events = detect_candidates(run, **config)
            detector_counts[detector][split_for_video(run.video)] += len(events)
            all_rows.extend(event_record(event, detector) for event in events)

    analyses = []
    for detector in CONFIGS:
        detector_rows = [row for row in all_rows if row["detector"] == detector]
        for metric, invert in (("circularity_tension", False), ("settle_sec", False), ("parent_life_sec", True)):
            for split in ("evaluation", "holdout"):
                for target_name in TARGETS:
                    analyses.append(analyze_target(detector_rows, split, metric, target_name, invert=invert))
            fitted = free_optimum(detector_rows, "evaluation", metric, invert=invert)
            if fitted:
                analyses.append({"detector": detector, "target": "free_evaluation_optimum", "split": "evaluation", "metric": metric,
                                 "n": fitted["n"], "rho_expected_positive": fitted["rho"],
                                 "blocked_p_one_sided": float("nan"), "fitted_ratio": fitted["target"]})
                holdout_free = evaluate_free_target(detector_rows, fitted["target"], "holdout", metric, invert=invert)
                holdout_free["detector"] = detector
                holdout_free["target"] = "free_evaluation_optimum"
                holdout_free["fitted_ratio"] = fitted["target"]
                analyses.append(holdout_free)

    summary = {
        "source_files": len(runs),
        "detector_counts": {name: dict(counts) for name, counts in detector_counts.items()},
        "event_summaries": {
            detector: {
                split: {
                    "events": len(subset := [row for row in all_rows if row["detector"] == detector and row["split"] == split]),
                    "child_ratio": finite_summary(row["child_ratio"] for row in subset),
                    "parent_ratio": finite_summary(row["parent_ratio"] for row in subset),
                    "closure": finite_summary(row["closure"] for row in subset),
                    "vertical_equality_gap": finite_summary(row["vertical_equality_gap"] for row in subset),
                    "tension": finite_summary(row["circularity_tension"] for row in subset),
                    "settle_sec": finite_summary(row["settle_sec"] for row in subset),
                    "life_sec": finite_summary(row["parent_life_sec"] for row in subset),
                    "near_phi_20pct_both_legs": sum(
                        abs(math.log(row["child_ratio"] / PHI)) <= abs(math.log(1.2)) and
                        abs(math.log(row["parent_ratio"] / PHI)) <= abs(math.log(1.2))
                        for row in subset
                    ),
                }
                for split in ("calibration", "evaluation", "holdout")
            }
            for detector in CONFIGS
        },
        "target_analyses": analyses,
    }

    write_csv(output / "vertical_ara_bubble_events.csv", all_rows)
    write_csv(output / "vertical_ara_target_results.csv", analyses)
    (output / "vertical_ara_summary.json").write_text(json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8")
    for path in (output / "vertical_ara_bubble_events.csv", output / "vertical_ara_target_results.csv", output / "vertical_ara_summary.json"):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        print(f"{path.name}\t{path.stat().st_size}\t{digest}")
    print(json.dumps(summary, indent=2, allow_nan=True))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
