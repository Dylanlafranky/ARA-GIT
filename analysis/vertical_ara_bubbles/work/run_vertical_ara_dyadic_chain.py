from __future__ import annotations

import csv
import hashlib
import json
import math
import random
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from bubble_lineage import Bubble, load_run


PHI = (1.0 + math.sqrt(5.0)) / 2.0
TARGETS = {
    "one": 1.0,
    "sqrt2": math.sqrt(2.0),
    "three_halves": 1.5,
    "phi": PHI,
    "two": 2.0,
}
LEVELS = tuple(range(5))
ROOT_STEPS = 32
MIN_STEP_M = 0.0005
BOOTSTRAPS = 5000
SEED = 20260801


@dataclass
class Root:
    split: str
    video: str
    file: str
    track_id: int
    segment_index: int
    start_frame: int
    time_sec: float
    steps: list[tuple[float, float]]
    real_ratios: list[float]
    permuted_ratios: list[float]
    whole_tree_ratios: list[list[float]]


def split_for_video(video: str) -> str:
    number = int(video[1:])
    if number <= 7:
        return "calibration"
    if number <= 28:
        return "evaluation"
    return "holdout"


def contiguous_segments(track: dict[int, Bubble]) -> list[list[Bubble]]:
    frames = sorted(track)
    if not frames:
        return []
    segments: list[list[Bubble]] = []
    current = [track[frames[0]]]
    for previous, frame in zip(frames, frames[1:]):
        if frame == previous + 1:
            current.append(track[frame])
        else:
            segments.append(current)
            current = [track[frame]]
    segments.append(current)
    return segments


def add_vectors(vectors: list[tuple[float, float]], start: int, end: int) -> tuple[float, float]:
    x = sum(vector[0] for vector in vectors[start:end])
    y = sum(vector[1] for vector in vectors[start:end])
    return x, y


def magnitude(vector: tuple[float, float]) -> float:
    return math.hypot(vector[0], vector[1])


def pair_ratio(left: tuple[float, float], right: tuple[float, float]) -> float:
    a = magnitude(left)
    b = magnitude(right)
    if a < MIN_STEP_M or b < MIN_STEP_M:
        return float("nan")
    return max(a, b) / min(a, b)


def nested_ratios(steps: list[tuple[float, float]]) -> list[float]:
    ratios: list[float] = []
    for level in LEVELS:
        child = 2**level
        ratios.append(pair_ratio(
            add_vectors(steps, 0, child),
            add_vectors(steps, child, 2 * child),
        ))
    return ratios


def whole_tree_ratios(steps: list[tuple[float, float]]) -> list[list[float]]:
    levels: list[list[float]] = []
    for level in LEVELS:
        child = 2**level
        ratios = []
        for start in range(0, ROOT_STEPS, 2 * child):
            ratio = pair_ratio(
                add_vectors(steps, start, start + child),
                add_vectors(steps, start + child, start + 2 * child),
            )
            if math.isfinite(ratio):
                ratios.append(ratio)
        levels.append(ratios)
    return levels


def deterministic_permutation(steps: list[tuple[float, float]], key: str) -> list[tuple[float, float]]:
    seed = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") ^ SEED
    indices = list(range(len(steps)))
    random.Random(seed).shuffle(indices)
    return [steps[index] for index in indices]


def reversal_error(steps: list[tuple[float, float]]) -> float:
    original = whole_tree_ratios(steps)
    reversed_steps = [(-x, -y) for x, y in reversed(steps)]
    reversed_tree = whole_tree_ratios(reversed_steps)
    errors = []
    for left, right in zip(original, reversed_tree):
        if len(left) != len(right):
            return float("inf")
        errors.extend(abs(a - b) for a, b in zip(sorted(left), sorted(right)))
    return max(errors, default=0.0)


def extract_roots(source: Path) -> tuple[list[Root], dict]:
    roots: list[Root] = []
    diagnostics = defaultdict(int)
    max_reversal_error = 0.0
    for path in sorted(source.glob("*.csv")):
        run = load_run(path)
        split = split_for_video(run.video)
        diagnostics[f"{split}_source_videos"] += 1
        for track_id, track in sorted(run.tracks.items()):
            for segment_index, segment in enumerate(contiguous_segments(track)):
                for start in range(0, len(segment) - ROOT_STEPS, ROOT_STEPS):
                    diagnostics[f"{split}_candidate_roots"] += 1
                    block = segment[start:start + ROOT_STEPS + 1]
                    steps = [
                        (b.x - a.x, b.y - a.y)
                        for a, b in zip(block, block[1:])
                    ]
                    real = nested_ratios(steps)
                    if not all(math.isfinite(value) for value in real):
                        diagnostics[f"{split}_resolution_exclusions"] += 1
                        continue
                    key = f"{run.video}:{track_id}:{block[0].frame}"
                    permuted = nested_ratios(deterministic_permutation(steps, key))
                    if not all(math.isfinite(value) for value in permuted):
                        diagnostics[f"{split}_permutation_incomplete_controls"] += 1
                    tree = whole_tree_ratios(steps)
                    max_reversal_error = max(max_reversal_error, reversal_error(steps))
                    roots.append(Root(
                        split=split,
                        video=run.video,
                        file=path.name,
                        track_id=track_id,
                        segment_index=segment_index,
                        start_frame=block[0].frame,
                        time_sec=block[0].time,
                        steps=steps,
                        real_ratios=real,
                        permuted_ratios=permuted,
                        whole_tree_ratios=tree,
                    ))
                    diagnostics[f"{split}_eligible_roots"] += 1
    diagnostics["reversal_max_absolute_error"] = max_reversal_error
    return roots, dict(diagnostics)


def target_loss(ratio: float, target: float) -> float:
    return abs(math.log(ratio / target))


def golden_equality_residual(ratio: float) -> float:
    return abs(math.log((1.0 + 1.0 / ratio) / ratio))


def ols_slope(values: list[float]) -> float:
    x = np.asarray(LEVELS, dtype=float)
    y = np.asarray(values, dtype=float)
    return float(np.sum((x - x.mean()) * (y - y.mean())) / np.sum((x - x.mean()) ** 2))


def attach_broken_controls(roots: list[Root]) -> dict[tuple[str, int, int], list[float]]:
    by_video: dict[str, list[Root]] = defaultdict(list)
    for root in roots:
        by_video[root.video].append(root)
    controls: dict[tuple[str, int, int], list[float]] = {}
    for video, group in by_video.items():
        group.sort(key=lambda item: (item.start_frame, item.track_id, item.segment_index))
        if len(group) < 2:
            continue
        for index, root in enumerate(group):
            partner = group[(index + 1) % len(group)]
            ratios = []
            for level in LEVELS:
                child = 2**level
                left = add_vectors(root.steps, 0, child)
                right = add_vectors(partner.steps, child, 2 * child)
                ratios.append(pair_ratio(left, right))
            controls[(video, root.track_id, root.start_frame)] = ratios
    return controls


def build_rows(roots: list[Root]) -> list[dict]:
    broken = attach_broken_controls(roots)
    rows: list[dict] = []
    for root in roots:
        key = (root.video, root.track_id, root.start_frame)
        broken_ratios = broken.get(key, [float("nan")] * len(LEVELS))
        real_phi_losses = [target_loss(ratio, PHI) for ratio in root.real_ratios]
        perm_phi_losses = [
            target_loss(ratio, PHI) if math.isfinite(ratio) else float("nan")
            for ratio in root.permuted_ratios
        ]
        broken_phi_losses = [
            target_loss(ratio, PHI) if math.isfinite(ratio) else float("nan")
            for ratio in broken_ratios
        ]
        real_slope = ols_slope(real_phi_losses)
        perm_slope = (
            ols_slope(perm_phi_losses)
            if all(math.isfinite(value) for value in perm_phi_losses)
            else float("nan")
        )
        broken_slope = (
            ols_slope(broken_phi_losses)
            if all(math.isfinite(value) for value in broken_phi_losses)
            else float("nan")
        )
        for level in LEVELS:
            ratio = root.real_ratios[level]
            permuted = root.permuted_ratios[level]
            broken_ratio = broken_ratios[level]
            record = {
                "split": root.split,
                "video": root.video,
                "file": root.file,
                "track_id": root.track_id,
                "segment_index": root.segment_index,
                "start_frame": root.start_frame,
                "time_sec": root.time_sec,
                "level": level,
                "child_frames": 2**level,
                "parent_frames": 2 ** (level + 1),
                "ratio_real": ratio,
                "ratio_permuted": permuted,
                "ratio_broken": broken_ratio,
                "golden_equality_real": golden_equality_residual(ratio),
                "golden_equality_permuted": (
                    golden_equality_residual(permuted)
                    if math.isfinite(permuted) else float("nan")
                ),
                "golden_equality_broken": (
                    golden_equality_residual(broken_ratio)
                    if math.isfinite(broken_ratio) else float("nan")
                ),
                "phi_endpoint_change_real": real_phi_losses[-1] - real_phi_losses[0],
                "phi_endpoint_change_permuted": (
                    perm_phi_losses[-1] - perm_phi_losses[0]
                    if math.isfinite(perm_phi_losses[-1]) and math.isfinite(perm_phi_losses[0])
                    else float("nan")
                ),
                "phi_endpoint_change_broken": broken_phi_losses[-1] - broken_phi_losses[0]
                if all(math.isfinite(value) for value in broken_phi_losses) else float("nan"),
                "phi_slope_real": real_slope,
                "phi_slope_permuted": perm_slope,
                "phi_slope_broken": broken_slope,
            }
            for name, target in TARGETS.items():
                record[f"loss_{name}_real"] = target_loss(ratio, target)
                record[f"loss_{name}_permuted"] = (
                    target_loss(permuted, target)
                    if math.isfinite(permuted) else float("nan")
                )
                record[f"loss_{name}_broken"] = (
                    target_loss(broken_ratio, target)
                    if math.isfinite(broken_ratio) else float("nan")
                )
                tree_losses = [target_loss(value, target) for value in root.whole_tree_ratios[level]]
                record[f"whole_tree_median_loss_{name}"] = statistics.median(tree_losses)
            rows.append(record)
    return rows


def unique_root_rows(rows: list[dict], split: str) -> list[dict]:
    return [row for row in rows if row["split"] == split and row["level"] == 0]


def cluster_bootstrap_mean(root_rows: list[dict], field: str, seed_offset: int = 0) -> dict:
    by_video: dict[str, list[float]] = defaultdict(list)
    for row in root_rows:
        value = float(row[field])
        if math.isfinite(value):
            by_video[row["video"]].append(value)
    videos = sorted(by_video)
    if not videos:
        return {"mean": float("nan"), "ci_low": float("nan"), "ci_high": float("nan"), "roots": 0, "videos": 0}
    sums = np.asarray([sum(by_video[video]) for video in videos], dtype=float)
    counts = np.asarray([len(by_video[video]) for video in videos], dtype=float)
    observed = float(sums.sum() / counts.sum())
    rng = np.random.default_rng(SEED + seed_offset)
    draws = rng.integers(0, len(videos), size=(BOOTSTRAPS, len(videos)))
    samples = np.sum(sums[draws], axis=1) / np.sum(counts[draws], axis=1)
    return {
        "mean": observed,
        "ci_low": float(np.quantile(samples, 0.025)),
        "ci_high": float(np.quantile(samples, 0.975)),
        "roots": int(counts.sum()),
        "videos": len(videos),
    }


def cluster_bootstrap_paired(root_rows: list[dict], left: str, right: str, seed_offset: int = 0) -> dict:
    paired = []
    for row in root_rows:
        a = float(row[left])
        b = float(row[right])
        if math.isfinite(a) and math.isfinite(b):
            copy = dict(row)
            copy["_paired_difference"] = a - b
            paired.append(copy)
    return cluster_bootstrap_mean(paired, "_paired_difference", seed_offset)


def median_absolute_deviation(values: list[float]) -> float:
    center = statistics.median(values)
    return statistics.median(abs(value - center) for value in values)


def level_summary(rows: list[dict], split: str, level: int, calibration_targets: dict[int, float]) -> dict:
    subset = [row for row in rows if row["split"] == split and row["level"] == level]
    ratios = [float(row["ratio_real"]) for row in subset]
    log_ratios = [math.log(value) for value in ratios]
    targets = {}
    for name, target in TARGETS.items():
        values = [float(row[f"loss_{name}_real"]) for row in subset]
        targets[name] = {
            "target_value": target,
            "mean_loss": statistics.mean(values),
            "median_loss": statistics.median(values),
        }
    calibration_target = calibration_targets[level]
    calibration_losses = [target_loss(value, calibration_target) for value in ratios]
    return {
        "roots": len(subset),
        "videos": len({row["video"] for row in subset}),
        "ratio_mean": statistics.mean(ratios),
        "ratio_median": statistics.median(ratios),
        "ratio_geometric_mean": math.exp(statistics.mean(log_ratios)),
        "free_target": math.exp(statistics.median(log_ratios)),
        "log_ratio_mad": median_absolute_deviation(log_ratios),
        "log_phi_residual_mad": median_absolute_deviation([value - math.log(PHI) for value in log_ratios]),
        "targets": targets,
        "calibration_free_target": calibration_target,
        "calibration_free_mean_loss": statistics.mean(calibration_losses),
        "phi_permuted_mean_loss": statistics.mean(
            float(row["loss_phi_permuted"])
            for row in subset if math.isfinite(float(row["loss_phi_permuted"]))
        ),
        "phi_broken_mean_loss": statistics.mean(
            float(row["loss_phi_broken"]) for row in subset if math.isfinite(float(row["loss_phi_broken"]))
        ),
        "whole_tree_phi_median_loss_mean": statistics.mean(
            float(row["whole_tree_median_loss_phi"]) for row in subset
        ),
    }


def summarize(rows: list[dict], diagnostics: dict) -> tuple[dict, list[dict]]:
    calibration_targets = {}
    for level in LEVELS:
        values = [
            math.log(float(row["ratio_real"]))
            for row in rows if row["split"] == "calibration" and row["level"] == level
        ]
        calibration_targets[level] = math.exp(statistics.median(values))

    summary = {
        "source": "Zenodo 10.5281/zenodo.15102957",
        "root_steps": ROOT_STEPS,
        "minimum_child_displacement_m": MIN_STEP_M,
        "bootstraps": BOOTSTRAPS,
        "diagnostics": diagnostics,
        "calibration_free_targets": calibration_targets,
        "levels": {},
        "convergence": {},
        "coarsest_target_comparisons": {},
        "verdict": {},
    }
    level_table = []
    for split in ("calibration", "evaluation", "holdout"):
        summary["levels"][split] = {}
        for level in LEVELS:
            record = level_summary(rows, split, level, calibration_targets)
            summary["levels"][split][str(level)] = record
            for name, target_record in record["targets"].items():
                level_table.append({
                    "split": split,
                    "level": level,
                    "child_frames": 2**level,
                    "parent_frames": 2 ** (level + 1),
                    "target": name,
                    "target_value": target_record["target_value"],
                    "mean_loss": target_record["mean_loss"],
                    "median_loss": target_record["median_loss"],
                    "roots": record["roots"],
                    "videos": record["videos"],
                    "free_target": record["free_target"],
                    "phi_permuted_mean_loss": record["phi_permuted_mean_loss"],
                    "phi_broken_mean_loss": record["phi_broken_mean_loss"],
                    "whole_tree_phi_median_loss_mean": record["whole_tree_phi_median_loss_mean"],
                })

    for split_index, split in enumerate(("evaluation", "holdout")):
        roots = unique_root_rows(rows, split)
        summary["convergence"][split] = {
            "endpoint_change": cluster_bootstrap_mean(roots, "phi_endpoint_change_real", 10 + split_index),
            "five_level_slope": cluster_bootstrap_mean(roots, "phi_slope_real", 20 + split_index),
            "real_minus_permuted_endpoint_change": cluster_bootstrap_paired(
                roots, "phi_endpoint_change_real", "phi_endpoint_change_permuted", 30 + split_index
            ),
            "real_minus_broken_endpoint_change": cluster_bootstrap_paired(
                roots, "phi_endpoint_change_real", "phi_endpoint_change_broken", 40 + split_index
            ),
            "real_minus_permuted_slope": cluster_bootstrap_paired(
                roots, "phi_slope_real", "phi_slope_permuted", 50 + split_index
            ),
            "real_minus_broken_slope": cluster_bootstrap_paired(
                roots, "phi_slope_real", "phi_slope_broken", 60 + split_index
            ),
        }
        level_four = [row for row in rows if row["split"] == split and row["level"] == 4]
        comparisons = {}
        for target_index, name in enumerate(TARGETS):
            if name == "phi":
                continue
            comparisons[name] = cluster_bootstrap_paired(
                level_four, "loss_phi_real", f"loss_{name}_real", 100 + 10 * split_index + target_index
            )
        summary["coarsest_target_comparisons"][split] = comparisons

    eval_conv = summary["convergence"]["evaluation"]
    hold_conv = summary["convergence"]["holdout"]
    convergence_pass = (
        eval_conv["endpoint_change"]["ci_high"] < 0
        and eval_conv["five_level_slope"]["ci_high"] < 0
        and hold_conv["endpoint_change"]["mean"] < 0
        and hold_conv["five_level_slope"]["mean"] < 0
        and eval_conv["real_minus_permuted_endpoint_change"]["ci_high"] < 0
        and eval_conv["real_minus_broken_endpoint_change"]["ci_high"] < 0
        and hold_conv["real_minus_permuted_endpoint_change"]["mean"] < 0
        and hold_conv["real_minus_broken_endpoint_change"]["mean"] < 0
    )
    placement_pass = all(
        record["mean"] < 0
        for split in ("evaluation", "holdout")
        for record in summary["coarsest_target_comparisons"][split].values()
    )
    concentration_pass = all(
        summary["levels"][split]["4"]["log_phi_residual_mad"]
        < summary["levels"][split]["0"]["log_phi_residual_mad"]
        for split in ("evaluation", "holdout")
    )
    summary["verdict"] = {
        "long_chain_convergence_supported": convergence_pass,
        "coarsest_phi_placement_supported": placement_pass,
        "secondary_concentration_supported": concentration_pass,
        "overall_supports_registered_long_chain_phi_placement": convergence_pass and placement_pass,
    }
    return summary, level_table


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base = Path(__file__).resolve().parents[1]
    roots, diagnostics = extract_roots(base / "source_data")
    if not roots:
        raise SystemExit("No eligible roots")
    rows = build_rows(roots)
    summary, level_table = summarize(rows, diagnostics)
    results = base / "results"
    results.mkdir(parents=True, exist_ok=True)
    row_path = results / "dyadic_chain_root_levels.csv"
    table_path = results / "dyadic_chain_level_summary.csv"
    summary_path = results / "dyadic_chain_summary.json"
    write_csv(row_path, rows)
    write_csv(table_path, level_table)
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8")
    print(json.dumps({
        "eligible_roots": {
            split: diagnostics.get(f"{split}_eligible_roots", 0)
            for split in ("calibration", "evaluation", "holdout")
        },
        "reversal_max_absolute_error": diagnostics["reversal_max_absolute_error"],
        "calibration_free_targets": summary["calibration_free_targets"],
        "convergence": summary["convergence"],
        "coarsest_target_comparisons": summary["coarsest_target_comparisons"],
        "verdict": summary["verdict"],
    }, indent=2, allow_nan=True))
    for path in (row_path, table_path, summary_path):
        print(f"{path.name}\t{hashlib.sha256(path.read_bytes()).hexdigest().upper()}")


if __name__ == "__main__":
    main()
