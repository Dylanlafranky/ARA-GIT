from __future__ import annotations

import csv
import json
import math
import statistics
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
EXPECTED_ROOTS = {"calibration": 125, "evaluation": 172, "holdout": 40}
TOLERANCE = 1e-10


def close(a: float, b: float, tolerance: float = TOLERANCE) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tolerance


def slope(values: list[float]) -> float:
    x = np.arange(5, dtype=float)
    y = np.asarray(values, dtype=float)
    return float(np.sum((x - x.mean()) * (y - y.mean())) / np.sum((x - x.mean()) ** 2))


def direct_raw_ratios(source: Path, row: dict) -> list[float]:
    run = load_run(source / row["file"])
    track = run.tracks[int(row["track_id"])]
    start = int(row["start_frame"])
    points = [track[frame] for frame in range(start, start + 33)]
    ratios = []
    for level in range(5):
        child = 2**level
        a = math.hypot(points[child].x - points[0].x, points[child].y - points[0].y)
        b = math.hypot(points[2 * child].x - points[child].x, points[2 * child].y - points[child].y)
        ratios.append(max(a, b) / min(a, b))
    return ratios


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    result_dir = base / "results"
    rows = list(csv.DictReader((result_dir / "dyadic_chain_root_levels.csv").open(encoding="utf-8")))
    summary = json.loads((result_dir / "dyadic_chain_summary.json").read_text(encoding="utf-8"))
    errors: list[str] = []

    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(row["split"], row["video"], row["track_id"], row["start_frame"])].append(row)

    actual_counts = defaultdict(int)
    for key, group in grouped.items():
        actual_counts[key[0]] += 1
        ordered = sorted(group, key=lambda item: int(item["level"]))
        if [int(item["level"]) for item in ordered] != list(range(5)):
            errors.append(f"incomplete levels for {key}")
            continue
        phi_losses = []
        for item in ordered:
            ratio = float(item["ratio_real"])
            for name, target in TARGETS.items():
                expected = abs(math.log(ratio / target))
                actual = float(item[f"loss_{name}_real"])
                if not close(actual, expected):
                    errors.append(f"target loss mismatch {key} level {item['level']} {name}")
            expected_golden = abs(math.log((1.0 + 1.0 / ratio) / ratio))
            if not close(float(item["golden_equality_real"]), expected_golden):
                errors.append(f"golden equality mismatch {key} level {item['level']}")
            phi_losses.append(abs(math.log(ratio / PHI)))
        expected_delta = phi_losses[-1] - phi_losses[0]
        expected_slope = slope(phi_losses)
        if not all(close(float(item["phi_endpoint_change_real"]), expected_delta) for item in ordered):
            errors.append(f"endpoint mismatch {key}")
        if not all(close(float(item["phi_slope_real"]), expected_slope) for item in ordered):
            errors.append(f"slope mismatch {key}")

    for split, expected in EXPECTED_ROOTS.items():
        if actual_counts[split] != expected:
            errors.append(f"root count {split}: {actual_counts[split]} != {expected}")

    raw_checks = []
    for split in ("calibration", "evaluation", "holdout"):
        candidates = sorted(
            (group for key, group in grouped.items() if key[0] == split),
            key=lambda group: (group[0]["video"], int(group[0]["start_frame"]), int(group[0]["track_id"])),
        )
        group = sorted(candidates[len(candidates) // 2], key=lambda item: int(item["level"]))
        recomputed = direct_raw_ratios(base / "source_data", group[0])
        stored = [float(item["ratio_real"]) for item in group]
        max_error = max(abs(a - b) for a, b in zip(recomputed, stored))
        raw_checks.append({"split": split, "video": group[0]["video"], "max_error": max_error})
        if max_error > TOLERANCE:
            errors.append(f"raw trajectory mismatch {split}")

    aggregate_checks = []
    for split in ("calibration", "evaluation", "holdout"):
        for level in range(5):
            subset = [row for row in rows if row["split"] == split and int(row["level"]) == level]
            ratios = [float(row["ratio_real"]) for row in subset]
            free = math.exp(statistics.median(math.log(value) for value in ratios))
            stored = float(summary["levels"][split][str(level)]["free_target"])
            aggregate_checks.append({"split": split, "level": level, "free_target_error": abs(free - stored)})
            if not close(free, stored):
                errors.append(f"free target mismatch {split} level {level}")
            for name in TARGETS:
                mean_loss = statistics.mean(float(row[f"loss_{name}_real"]) for row in subset)
                stored_loss = float(summary["levels"][split][str(level)]["targets"][name]["mean_loss"])
                if not close(mean_loss, stored_loss):
                    errors.append(f"mean loss mismatch {split} level {level} {name}")

    for split in ("evaluation", "holdout"):
        roots = [group[0] for key, group in grouped.items() if key[0] == split]
        delta_mean = statistics.mean(float(row["phi_endpoint_change_real"]) for row in roots)
        stored = float(summary["convergence"][split]["endpoint_change"]["mean"])
        if not close(delta_mean, stored):
            errors.append(f"convergence mean mismatch {split}")
        level_four = [row for row in rows if row["split"] == split and int(row["level"]) == 4]
        for name in TARGETS:
            if name == "phi":
                continue
            difference = statistics.mean(
                float(row["loss_phi_real"]) - float(row[f"loss_{name}_real"])
                for row in level_four
            )
            stored_difference = float(summary["coarsest_target_comparisons"][split][name]["mean"])
            if not close(difference, stored_difference):
                errors.append(f"coarsest comparison mismatch {split} {name}")

    reversal_error = float(summary["diagnostics"]["reversal_max_absolute_error"])
    if reversal_error > TOLERANCE:
        errors.append("reversal invariant failed")

    validation = {
        "status": "passed" if not errors else "failed",
        "row_count": len(rows),
        "root_counts": dict(actual_counts),
        "raw_trajectory_spot_checks": raw_checks,
        "aggregate_checks": aggregate_checks,
        "reversal_max_absolute_error": reversal_error,
        "errors": errors,
    }
    output = result_dir / "dyadic_chain_validation.json"
    output.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
