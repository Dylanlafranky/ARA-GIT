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
BOOTSTRAPS = 5000
SEED = 20260801


def wrap(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def complex_vectors(row: dict) -> list[complex]:
    result = []
    for level in range(5):
        magnitude = float(row[f"parent_{level}_magnitude"])
        angle = math.radians(float(row[f"parent_{level}_angle_deg"]))
        result.append(magnitude * complex(math.cos(angle), math.sin(angle)))
    return result


def recompute(vectors: list[complex]) -> dict:
    q = [vectors[index + 1] / vectors[index] for index in range(4)]
    angles = [math.atan2(value.imag, value.real) for value in q]
    resultant = sum(complex(math.cos(value), math.sin(value)) for value in angles)
    center = math.atan2(resultant.imag, resultant.real) if abs(resultant) >= 1e-15 else 0.0
    free = math.exp(statistics.mean(math.log(abs(value)) for value in q))

    def full(target: float) -> float:
        terms = [
            math.log(abs(value) / target) ** 2 + wrap(angle - center) ** 2
            for value, angle in zip(q, angles)
        ]
        return math.sqrt(statistics.mean(terms))

    def short(target: float) -> float:
        base = abs(vectors[0])
        terms = [
            math.log(abs(vectors[level]) / (base * target**level)) ** 2
            for level in range(1, 5)
        ]
        return math.sqrt(statistics.mean(terms))

    result = {
        "observed_free_scale": free,
        "observed_free_full_loss": full(free),
        "observed_angular_coherence": abs(resultant) / 4.0,
        "observed_mean_rotation_deg": math.degrees(center),
    }
    for index, value in enumerate(q):
        result[f"observed_scale_transition_{index}"] = abs(value)
        result[f"observed_rotation_transition_{index}_deg"] = math.degrees(
            math.atan2(value.imag, value.real)
        )
    for name, target in TARGETS.items():
        result[f"observed_full_loss_{name}"] = full(target)
        result[f"observed_shorthand_loss_{name}"] = short(target)
    return result


def cluster_bootstrap(rows: list[dict], field: str, seed_offset: int) -> dict:
    by_video: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        value = float(row[field])
        if math.isfinite(value):
            by_video[row["video"]].append(value)
    videos = sorted(by_video)
    sums = np.asarray([sum(by_video[video]) for video in videos], dtype=float)
    counts = np.asarray([len(by_video[video]) for video in videos], dtype=float)
    mean = float(sums.sum() / counts.sum())
    rng = np.random.default_rng(SEED + seed_offset)
    draws = rng.integers(0, len(videos), size=(BOOTSTRAPS, len(videos)))
    samples = np.sum(sums[draws], axis=1) / np.sum(counts[draws], axis=1)
    return {
        "mean": mean,
        "ci_low": float(np.quantile(samples, 0.025)),
        "ci_high": float(np.quantile(samples, 0.975)),
        "roots": int(counts.sum()),
        "videos": len(videos),
    }


def paired(rows: list[dict], left: str, right: str, seed_offset: int) -> dict:
    pairs = []
    for row in rows:
        a = float(row[left])
        b = float(row[right])
        if math.isfinite(a) and math.isfinite(b):
            copy = dict(row)
            copy["_difference"] = a - b
            pairs.append(copy)
    return cluster_bootstrap(pairs, "_difference", seed_offset)


def max_record_error(left: dict, right: dict) -> float:
    fields = ("mean", "ci_low", "ci_high", "roots", "videos")
    return max(abs(float(left[field]) - float(right[field])) for field in fields)


def raw_source_check(base: Path, row: dict) -> float:
    run = load_run(base / "source_data" / row["file"])
    track = run.tracks[int(row["track_id"])]
    start = int(row["start_frame"])
    bubbles = [track[start + index] for index in range(33)]
    steps = [complex(b.x - a.x, b.y - a.y) for a, b in zip(bubbles, bubbles[1:])]
    vectors = [sum(steps[: 2 ** (level + 1)]) for level in range(5)]
    csv_vectors = complex_vectors(row)
    return max(abs(a - b) for a, b in zip(vectors, csv_vectors))


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    results = base / "results"
    with (results / "spiral_scale_root_results.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    summary = json.loads((results / "spiral_scale_summary.json").read_text(encoding="utf-8"))
    errors = []

    maximum_row_error = 0.0
    for row in rows:
        calculated = recompute(complex_vectors(row))
        for field, value in calculated.items():
            maximum_row_error = max(maximum_row_error, abs(value - float(row[field])))
    if maximum_row_error > 1e-10:
        errors.append(f"row formula error {maximum_row_error}")

    split_counts = {split: sum(row["split"] == split for row in rows) for split in ("calibration", "evaluation", "holdout")}
    expected_counts = {"calibration": 125, "evaluation": 172, "holdout": 40}
    if split_counts != expected_counts:
        errors.append(f"root counts {split_counts} != {expected_counts}")

    maximum_target_error = 0.0
    maximum_free_scale_error = 0.0
    for split in ("calibration", "evaluation", "holdout"):
        subset = [row for row in rows if row["split"] == split]
        free_scale = math.exp(statistics.median(math.log(float(row["observed_free_scale"])) for row in subset))
        maximum_free_scale_error = max(
            maximum_free_scale_error,
            abs(free_scale - float(summary["splits"][split]["geometric_median_free_scale"])),
        )
        for name in TARGETS:
            full_mean = statistics.mean(float(row[f"observed_full_loss_{name}"]) for row in subset)
            short_mean = statistics.mean(float(row[f"observed_shorthand_loss_{name}"]) for row in subset)
            saved = summary["splits"][split]["targets"][name]
            maximum_target_error = max(
                maximum_target_error,
                abs(full_mean - float(saved["full_mean"])),
                abs(short_mean - float(saved["shorthand_mean"])),
            )
    if maximum_target_error > 1e-12:
        errors.append(f"target summary error {maximum_target_error}")
    if maximum_free_scale_error > 1e-12:
        errors.append(f"free scale error {maximum_free_scale_error}")

    maximum_bootstrap_error = 0.0
    for split, split_index in (("evaluation", 1), ("holdout", 2)):
        subset = [row for row in rows if row["split"] == split]
        controls = summary["splits"][split]["controls"]
        definitions = [
            ("full_loss_observed_minus_permuted", "observed_free_full_loss", "permuted_free_full_loss", 100 + 10 * split_index),
            ("full_loss_observed_minus_broken", "observed_free_full_loss", "broken_free_full_loss", 101 + 10 * split_index),
            ("coherence_observed_minus_permuted", "observed_angular_coherence", "permuted_angular_coherence", 102 + 10 * split_index),
            ("coherence_observed_minus_broken", "observed_angular_coherence", "broken_angular_coherence", 103 + 10 * split_index),
        ]
        for label, left, right, offset in definitions:
            maximum_bootstrap_error = max(
                maximum_bootstrap_error,
                max_record_error(paired(subset, left, right, offset), controls[label]),
            )
        for target_index, name in enumerate(TARGETS):
            if name == "phi":
                continue
            for kind, prefix, base_offset in (("full", "observed_full_loss", 200), ("shorthand", "observed_shorthand_loss", 300)):
                calculated = paired(
                    subset,
                    f"{prefix}_phi",
                    f"{prefix}_{name}",
                    base_offset + 20 * split_index + target_index,
                )
                saved = summary["splits"][split]["phi_comparisons"][kind][name]
                maximum_bootstrap_error = max(maximum_bootstrap_error, max_record_error(calculated, saved))
    if maximum_bootstrap_error > 1e-12:
        errors.append(f"bootstrap error {maximum_bootstrap_error}")

    raw_checks = []
    for split, video in (("calibration", "V03"), ("evaluation", "V15"), ("holdout", "V31")):
        row = next(item for item in rows if item["split"] == split and item["video"] == video)
        error = raw_source_check(base, row)
        raw_checks.append({"split": split, "video": video, "max_error": error})
        if error > 1e-10:
            errors.append(f"raw source error {split} {video}: {error}")

    report = {
        "status": "passed" if not errors else "failed",
        "row_count": len(rows),
        "root_counts": split_counts,
        "maximum_row_formula_error": maximum_row_error,
        "maximum_target_summary_error": maximum_target_error,
        "maximum_free_scale_error": maximum_free_scale_error,
        "maximum_bootstrap_error": maximum_bootstrap_error,
        "raw_trajectory_spot_checks": raw_checks,
        "errors": errors,
    }
    path = results / "spiral_scale_validation.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
