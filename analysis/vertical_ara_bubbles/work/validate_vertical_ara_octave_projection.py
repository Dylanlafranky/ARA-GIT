from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

from bubble_lineage import load_run


PHI = (1.0 + math.sqrt(5.0)) / 2.0
SEED = 20260801
BOOTSTRAPS = 5000
SCRAMBLES = 64
MIN_STEP_M = 0.0005
LEVELS = tuple(range(4))
TARGETS = {
    "direct": 0.0,
    "thirty": 30.0,
    "phi_projection": 36.0,
    "diagonal": 45.0,
    "phi_complement": 54.0,
    "ridge_half": 60.0,
    "perpendicular": 90.0,
}


def vector(row: dict, level: int, label: str) -> complex:
    magnitude = float(row[f"level_{level}_{label}_magnitude"])
    angle = math.radians(float(row[f"level_{level}_{label}_angle_deg"]))
    return magnitude * complex(math.cos(angle), math.sin(angle))


def signed_cos(left: complex, right: complex) -> float:
    return max(-1.0, min(1.0, (left.conjugate() * right).real / (abs(left) * abs(right))))


def folded_angle(left: complex, right: complex) -> float:
    return math.degrees(math.acos(abs(signed_cos(left, right))))


def loss(angles: list[float], target: float) -> float:
    return math.sqrt(statistics.mean((angle - target) ** 2 for angle in angles))


def hash_uniform(key: str) -> float:
    integer = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
    return integer / float(2**64)


def recompute_row(row: dict) -> dict:
    a_vectors = [vector(row, level, "a") for level in LEVELS]
    b_vectors = [vector(row, level, "b") for level in LEVELS]
    parents = [vector(row, level, "parent") for level in LEVELS]
    a_angles = [folded_angle(a, parent) for a, parent in zip(a_vectors, parents)]
    b_angles = [folded_angle(b, parent) for b, parent in zip(b_vectors, parents)]
    result = {
        "observed_a_free_angle_deg": statistics.mean(a_angles),
        "observed_b_free_angle_deg": statistics.mean(b_angles),
        "observed_a_phi_loss_deg": loss(a_angles, 36.0),
        "observed_b_phi_loss_deg": loss(b_angles, 36.0),
    }
    for name, target in TARGETS.items():
        result[f"observed_a_loss_{name}_deg"] = loss(a_angles, target)
        result[f"observed_b_loss_{name}_deg"] = loss(b_angles, target)
    for level, (a, b, parent) in enumerate(zip(a_vectors, b_vectors, parents)):
        ca = signed_cos(a, parent)
        cb = signed_cos(b, parent)
        result[f"level_{level}_a_signed_cosine"] = ca
        result[f"level_{level}_b_signed_cosine"] = cb
        result[f"level_{level}_a_folded_angle_deg"] = a_angles[level]
        result[f"level_{level}_b_folded_angle_deg"] = b_angles[level]
        result[f"level_{level}_a_ara_projection"] = 2.0 * abs(ca)
        result[f"level_{level}_b_ara_projection"] = 2.0 * abs(cb)

    scramble_losses = []
    for replicate in range(SCRAMBLES):
        angles = []
        for level, (a, b) in enumerate(zip(a_vectors, b_vectors)):
            relative = 2.0 * math.pi * hash_uniform(
                f"{SEED}:{row['video']}:{row['track_id']}:{row['start_frame']}:{replicate}:{level}:projection"
            )
            base = math.atan2(a.imag, a.real)
            rotated_b = abs(b) * complex(math.cos(base + relative), math.sin(base + relative))
            parent = a + rotated_b
            if abs(parent) < MIN_STEP_M:
                break
            angles.append(folded_angle(a, parent))
        if len(angles) == len(LEVELS):
            scramble_losses.append(loss(angles, 36.0))
    result["scrambled_a_phi_loss_deg"] = statistics.mean(scramble_losses)
    return result


def reconstruct_broken(rows: list[dict]) -> dict[tuple[str, str, str], float]:
    by_video: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_video[row["video"]].append(row)
    result = {}
    for video, group in by_video.items():
        group.sort(key=lambda row: (int(row["start_frame"]), int(row["track_id"]), int(row["segment_index"])))
        if len(group) < 2:
            continue
        for index, row in enumerate(group):
            partner = group[(index + 1) % len(group)]
            angles = []
            for level in LEVELS:
                a = vector(row, level, "a")
                b = vector(partner, level, "b")
                parent = a + b
                if abs(parent) < MIN_STEP_M:
                    angles = []
                    break
                angles.append(folded_angle(a, parent))
            if angles:
                result[(video, row["track_id"], row["start_frame"])] = loss(angles, 36.0)
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
    records = []
    for row in rows:
        a = float(row[left])
        b = float(row[right])
        if math.isfinite(a) and math.isfinite(b):
            copy = dict(row)
            copy["_difference"] = a - b
            records.append(copy)
    return cluster_bootstrap(records, "_difference", seed_offset)


def max_record_error(left: dict, right: dict) -> float:
    return max(abs(float(left[key]) - float(right[key])) for key in ("mean", "ci_low", "ci_high", "roots", "videos"))


def raw_source_error(base: Path, row: dict) -> float:
    run = load_run(base / "source_data" / row["file"])
    track = run.tracks[int(row["track_id"])]
    start = int(row["start_frame"])
    bubbles = [track[start + index] for index in range(33)]
    steps = [complex(b.x - a.x, b.y - a.y) for a, b in zip(bubbles, bubbles[1:])]
    errors = []
    for level in LEVELS:
        n = 2 ** (level + 1)
        actual_a = sum(steps[:n])
        actual_b = sum(steps[n : 2 * n])
        actual_parent = actual_a + actual_b
        errors.extend([
            abs(actual_a - vector(row, level, "a")),
            abs(actual_b - vector(row, level, "b")),
            abs(actual_parent - vector(row, level, "parent")),
        ])
    return max(errors)


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    results = base / "results"
    with (results / "octave_projection_root_results.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    summary = json.loads((results / "octave_projection_summary.json").read_text(encoding="utf-8"))
    errors = []

    broken = reconstruct_broken(rows)
    maximum_row_error = 0.0
    for row in rows:
        calculated = recompute_row(row)
        key = (row["video"], row["track_id"], row["start_frame"])
        if key in broken:
            calculated["broken_a_phi_loss_deg"] = broken[key]
        for field, value in calculated.items():
            maximum_row_error = max(maximum_row_error, abs(value - float(row[field])))
        for level in LEVELS:
            a = vector(row, level, "a")
            b = vector(row, level, "b")
            parent = vector(row, level, "parent")
            maximum_row_error = max(maximum_row_error, abs((a + b) - parent))
    if maximum_row_error > 1e-10:
        errors.append(f"row formula error {maximum_row_error}")

    counts = {split: sum(row["split"] == split for row in rows) for split in ("calibration", "evaluation", "holdout")}
    expected = {"calibration": 125, "evaluation": 172, "holdout": 40}
    if counts != expected:
        errors.append(f"root counts {counts} != {expected}")

    maximum_summary_error = 0.0
    for split in ("calibration", "evaluation", "holdout"):
        subset = [row for row in rows if row["split"] == split]
        free_a = statistics.median(float(row["observed_a_free_angle_deg"]) for row in subset)
        free_b = statistics.median(float(row["observed_b_free_angle_deg"]) for row in subset)
        saved_split = summary["splits"][split]
        maximum_summary_error = max(
            maximum_summary_error,
            abs(free_a - float(saved_split["median_free_a_angle_deg"])),
            abs(free_b - float(saved_split["median_free_b_angle_deg"])),
        )
        for name in TARGETS:
            mean_a = statistics.mean(float(row[f"observed_a_loss_{name}_deg"]) for row in subset)
            mean_b = statistics.mean(float(row[f"observed_b_loss_{name}_deg"]) for row in subset)
            saved = saved_split["targets"][name]
            maximum_summary_error = max(
                maximum_summary_error,
                abs(mean_a - float(saved["a_mean_loss_deg"])),
                abs(mean_b - float(saved["b_mean_loss_deg"])),
            )
        for level in LEVELS:
            mean_a = statistics.mean(float(row[f"level_{level}_a_folded_angle_deg"]) for row in subset)
            mean_b = statistics.mean(float(row[f"level_{level}_b_folded_angle_deg"]) for row in subset)
            saved = saved_split["levels"][str(level)]
            maximum_summary_error = max(
                maximum_summary_error,
                abs(mean_a - float(saved["a_mean_angle_deg"])),
                abs(mean_b - float(saved["b_mean_angle_deg"])),
            )
    if maximum_summary_error > 1e-12:
        errors.append(f"summary error {maximum_summary_error}")

    maximum_bootstrap_error = 0.0
    for split, split_index in (("evaluation", 1), ("holdout", 2)):
        subset = [row for row in rows if row["split"] == split]
        saved = summary["splits"][split]
        checks = [
            (
                "observed_minus_scrambled_phi_loss",
                "observed_a_phi_loss_deg",
                "scrambled_a_phi_loss_deg",
                100 + 10 * split_index,
            ),
            (
                "observed_minus_broken_phi_loss",
                "observed_a_phi_loss_deg",
                "broken_a_phi_loss_deg",
                101 + 10 * split_index,
            ),
        ]
        for label, left, right, offset in checks:
            maximum_bootstrap_error = max(
                maximum_bootstrap_error,
                max_record_error(paired(subset, left, right, offset), saved["controls"][label]),
            )
        for target_index, name in enumerate(TARGETS):
            if name == "phi_projection":
                continue
            calculated = paired(
                subset,
                "observed_a_loss_phi_projection_deg",
                f"observed_a_loss_{name}_deg",
                200 + 20 * split_index + target_index,
            )
            maximum_bootstrap_error = max(
                maximum_bootstrap_error,
                max_record_error(calculated, saved["phi_comparisons"][name]),
            )
    if maximum_bootstrap_error > 1e-12:
        errors.append(f"bootstrap error {maximum_bootstrap_error}")

    raw_checks = []
    for split, video in (("calibration", "V03"), ("evaluation", "V15"), ("holdout", "V31")):
        row = next(item for item in rows if item["split"] == split and item["video"] == video)
        error = raw_source_error(base, row)
        raw_checks.append({"split": split, "video": video, "max_error": error})
        if error > 1e-10:
            errors.append(f"raw source error {split} {video}: {error}")

    report = {
        "status": "passed" if not errors else "failed",
        "row_count": len(rows),
        "root_counts": counts,
        "maximum_row_formula_error": maximum_row_error,
        "maximum_summary_error": maximum_summary_error,
        "maximum_bootstrap_error": maximum_bootstrap_error,
        "raw_trajectory_spot_checks": raw_checks,
        "errors": errors,
    }
    path = results / "octave_projection_validation.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

