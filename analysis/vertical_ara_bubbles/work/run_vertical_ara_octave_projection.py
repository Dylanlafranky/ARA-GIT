from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import numpy as np

from run_vertical_ara_dyadic_chain import (
    BOOTSTRAPS,
    MIN_STEP_M,
    PHI,
    SEED,
    Root,
    add_vectors,
    extract_roots,
)


LEVELS = tuple(range(4))
SCRAMBLES = 64
ANGLE_TARGETS_DEG = {
    "direct": 0.0,
    "thirty": 30.0,
    "phi_projection": 36.0,
    "diagonal": 45.0,
    "phi_complement": 54.0,
    "ridge_half": 60.0,
    "perpendicular": 90.0,
}


def as_complex(value: tuple[float, float]) -> complex:
    return complex(value[0], value[1])


def child_parent_vectors(steps: list[tuple[float, float]]) -> list[tuple[complex, complex, complex]]:
    vectors = []
    for level in LEVELS:
        child = 2 ** (level + 1)
        a = as_complex(add_vectors(steps, 0, child))
        b = as_complex(add_vectors(steps, child, 2 * child))
        vectors.append((a, b, a + b))
    return vectors


def eligible(vectors: list[tuple[complex, complex, complex]]) -> bool:
    return all(abs(value) >= MIN_STEP_M for triple in vectors for value in triple)


def signed_cosine(left: complex, right: complex) -> float:
    return max(-1.0, min(1.0, (left.conjugate() * right).real / (abs(left) * abs(right))))


def folded_angle_deg(left: complex, right: complex) -> float:
    return math.degrees(math.acos(abs(signed_cosine(left, right))))


def target_loss(angles: list[float], target: float) -> float:
    return math.sqrt(statistics.mean((angle - target) ** 2 for angle in angles))


def hash_uniform(key: str) -> float:
    integer = int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big")
    return integer / float(2**64)


def phase_scrambled_phi_loss(
    root: Root,
    vectors: list[tuple[complex, complex, complex]],
) -> float:
    losses = []
    for replicate in range(SCRAMBLES):
        angles = []
        for level, (a, b, _) in enumerate(vectors):
            relative = 2.0 * math.pi * hash_uniform(
                f"{SEED}:{root.video}:{root.track_id}:{root.start_frame}:{replicate}:{level}:projection"
            )
            rotated_b = abs(b) * complex(
                math.cos(math.atan2(a.imag, a.real) + relative),
                math.sin(math.atan2(a.imag, a.real) + relative),
            )
            parent = a + rotated_b
            if abs(parent) < MIN_STEP_M:
                continue
            angles.append(folded_angle_deg(a, parent))
        if len(angles) == len(LEVELS):
            losses.append(target_loss(angles, 36.0))
    return statistics.mean(losses) if losses else float("nan")


def attach_broken_complements(
    retained: list[tuple[Root, list[tuple[complex, complex, complex]]]],
) -> dict[tuple[str, int, int], list[complex]]:
    by_video: dict[str, list[tuple[Root, list[tuple[complex, complex, complex]]]]] = defaultdict(list)
    for item in retained:
        by_video[item[0].video].append(item)
    result = {}
    for video, group in by_video.items():
        group.sort(key=lambda item: (item[0].start_frame, item[0].track_id, item[0].segment_index))
        if len(group) < 2:
            continue
        for index, (root, _) in enumerate(group):
            partner = group[(index + 1) % len(group)][1]
            result[(video, root.track_id, root.start_frame)] = [triple[1] for triple in partner]
    return result


def broken_phi_loss(
    vectors: list[tuple[complex, complex, complex]],
    complements: list[complex] | None,
) -> float:
    if complements is None:
        return float("nan")
    angles = []
    for (a, _, _), b in zip(vectors, complements):
        parent = a + b
        if abs(parent) < MIN_STEP_M:
            return float("nan")
        angles.append(folded_angle_deg(a, parent))
    return target_loss(angles, 36.0)


def retain_roots(roots: list[Root]) -> tuple[list[tuple[Root, list[tuple[complex, complex, complex]]]], dict]:
    retained = []
    diagnostics = defaultdict(int)
    for root in roots:
        vectors = child_parent_vectors(root.steps)
        if not eligible(vectors):
            diagnostics[f"{root.split}_projection_resolution_exclusions"] += 1
            continue
        retained.append((root, vectors))
        diagnostics[f"{root.split}_projection_eligible_roots"] += 1
    return retained, dict(diagnostics)


def build_rows(
    retained: list[tuple[Root, list[tuple[complex, complex, complex]]]],
) -> tuple[list[dict], dict]:
    broken = attach_broken_complements(retained)
    diagnostics = defaultdict(int)
    rows = []
    for root, vectors in retained:
        a_angles = [folded_angle_deg(a, parent) for a, _, parent in vectors]
        b_angles = [folded_angle_deg(b, parent) for _, b, parent in vectors]
        key = (root.video, root.track_id, root.start_frame)
        scramble_loss = phase_scrambled_phi_loss(root, vectors)
        broken_loss = broken_phi_loss(vectors, broken.get(key))
        if not math.isfinite(scramble_loss):
            diagnostics[f"{root.split}_projection_scramble_incomplete"] += 1
        if not math.isfinite(broken_loss):
            diagnostics[f"{root.split}_projection_broken_incomplete"] += 1

        row = {
            "split": root.split,
            "video": root.video,
            "file": root.file,
            "track_id": root.track_id,
            "segment_index": root.segment_index,
            "start_frame": root.start_frame,
            "time_sec": root.time_sec,
            "observed_a_free_angle_deg": statistics.mean(a_angles),
            "observed_b_free_angle_deg": statistics.mean(b_angles),
            "observed_a_phi_loss_deg": target_loss(a_angles, 36.0),
            "observed_b_phi_loss_deg": target_loss(b_angles, 36.0),
            "scrambled_a_phi_loss_deg": scramble_loss,
            "broken_a_phi_loss_deg": broken_loss,
        }
        for name, target in ANGLE_TARGETS_DEG.items():
            row[f"observed_a_loss_{name}_deg"] = target_loss(a_angles, target)
            row[f"observed_b_loss_{name}_deg"] = target_loss(b_angles, target)

        for level, (a, b, parent) in enumerate(vectors):
            signed_a = signed_cosine(a, parent)
            signed_b = signed_cosine(b, parent)
            values = {
                "a": a,
                "b": b,
                "parent": parent,
            }
            row[f"level_{level}_child_frames"] = 2 ** (level + 1)
            row[f"level_{level}_parent_frames"] = 2 ** (level + 2)
            for label, value in values.items():
                row[f"level_{level}_{label}_magnitude"] = abs(value)
                row[f"level_{level}_{label}_angle_deg"] = math.degrees(math.atan2(value.imag, value.real))
            row[f"level_{level}_a_signed_cosine"] = signed_a
            row[f"level_{level}_b_signed_cosine"] = signed_b
            row[f"level_{level}_a_folded_angle_deg"] = a_angles[level]
            row[f"level_{level}_b_folded_angle_deg"] = b_angles[level]
            row[f"level_{level}_a_ara_projection"] = 2.0 * abs(signed_a)
            row[f"level_{level}_b_ara_projection"] = 2.0 * abs(signed_b)
        rows.append(row)
    return rows, dict(diagnostics)


def cluster_bootstrap_mean(rows: list[dict], field: str, seed_offset: int) -> dict:
    by_video: dict[str, list[float]] = defaultdict(list)
    for row in rows:
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


def paired_bootstrap(rows: list[dict], left: str, right: str, seed_offset: int) -> dict:
    paired = []
    for row in rows:
        a = float(row[left])
        b = float(row[right])
        if math.isfinite(a) and math.isfinite(b):
            copy = dict(row)
            copy["_difference"] = a - b
            paired.append(copy)
    return cluster_bootstrap_mean(paired, "_difference", seed_offset)


def closest_angle(value: float) -> str:
    return min(ANGLE_TARGETS_DEG, key=lambda name: abs(value - ANGLE_TARGETS_DEG[name]))


def summarize(rows: list[dict], diagnostics: dict) -> tuple[dict, list[dict]]:
    summary = {
        "source": "Zenodo 10.5281/zenodo.15102957",
        "protocol": "FROZEN_PROTOCOL_VERTICAL_ARA_OCTAVE_PROJECTION_2026-08-01.md",
        "scrambles_per_root": SCRAMBLES,
        "bootstraps": BOOTSTRAPS,
        "diagnostics": diagnostics,
        "splits": {},
        "verdict": {},
    }
    level_table = []
    for split_index, split in enumerate(("calibration", "evaluation", "holdout")):
        subset = [row for row in rows if row["split"] == split]
        target_results = {}
        for name, target in ANGLE_TARGETS_DEG.items():
            a_losses = [float(row[f"observed_a_loss_{name}_deg"]) for row in subset]
            b_losses = [float(row[f"observed_b_loss_{name}_deg"]) for row in subset]
            target_results[name] = {
                "angle_deg": target,
                "ara_projection": 2.0 * math.cos(math.radians(target)),
                "a_mean_loss_deg": statistics.mean(a_losses),
                "a_median_loss_deg": statistics.median(a_losses),
                "b_mean_loss_deg": statistics.mean(b_losses),
                "b_median_loss_deg": statistics.median(b_losses),
            }
        level_results = {}
        for level in LEVELS:
            a_angles = [float(row[f"level_{level}_a_folded_angle_deg"]) for row in subset]
            b_angles = [float(row[f"level_{level}_b_folded_angle_deg"]) for row in subset]
            signed_a = [float(row[f"level_{level}_a_signed_cosine"]) for row in subset]
            signed_b = [float(row[f"level_{level}_b_signed_cosine"]) for row in subset]
            a_projection = [float(row[f"level_{level}_a_ara_projection"]) for row in subset]
            b_projection = [float(row[f"level_{level}_b_ara_projection"]) for row in subset]
            record = {
                "level": level,
                "child_frames": 2 ** (level + 1),
                "parent_frames": 2 ** (level + 2),
                "a_mean_angle_deg": statistics.mean(a_angles),
                "a_median_angle_deg": statistics.median(a_angles),
                "a_closest_target_to_mean": closest_angle(statistics.mean(a_angles)),
                "a_mean_projection": statistics.mean(a_projection),
                "a_median_projection": statistics.median(a_projection),
                "a_negative_signed_fraction": sum(value < 0 for value in signed_a) / len(signed_a),
                "b_mean_angle_deg": statistics.mean(b_angles),
                "b_median_angle_deg": statistics.median(b_angles),
                "b_closest_target_to_mean": closest_angle(statistics.mean(b_angles)),
                "b_mean_projection": statistics.mean(b_projection),
                "b_median_projection": statistics.median(b_projection),
                "b_negative_signed_fraction": sum(value < 0 for value in signed_b) / len(signed_b),
            }
            level_results[str(level)] = record
            level_table.append({"split": split, **record, "roots": len(subset), "videos": len({row["video"] for row in subset})})

        free_a = statistics.median(float(row["observed_a_free_angle_deg"]) for row in subset)
        free_b = statistics.median(float(row["observed_b_free_angle_deg"]) for row in subset)
        split_record = {
            "roots": len(subset),
            "videos": len({row["video"] for row in subset}),
            "median_free_a_angle_deg": free_a,
            "median_free_b_angle_deg": free_b,
            "closest_target_to_free_a_angle": closest_angle(free_a),
            "closest_target_to_free_b_angle": closest_angle(free_b),
            "targets": target_results,
            "levels": level_results,
        }
        if split in ("evaluation", "holdout"):
            split_record["controls"] = {
                "observed_minus_scrambled_phi_loss": paired_bootstrap(
                    subset,
                    "observed_a_phi_loss_deg",
                    "scrambled_a_phi_loss_deg",
                    100 + 10 * split_index,
                ),
                "observed_minus_broken_phi_loss": paired_bootstrap(
                    subset,
                    "observed_a_phi_loss_deg",
                    "broken_a_phi_loss_deg",
                    101 + 10 * split_index,
                ),
            }
            comparisons = {}
            for target_index, name in enumerate(ANGLE_TARGETS_DEG):
                if name == "phi_projection":
                    continue
                comparisons[name] = paired_bootstrap(
                    subset,
                    "observed_a_loss_phi_projection_deg",
                    f"observed_a_loss_{name}_deg",
                    200 + 20 * split_index + target_index,
                )
            split_record["phi_comparisons"] = comparisons
        summary["splits"][split] = split_record

    evaluation = summary["splits"]["evaluation"]
    confirmation = summary["splits"]["holdout"]
    gate_1 = (
        all(record["ci_high"] < 0 for record in evaluation["phi_comparisons"].values())
        and all(record["mean"] < 0 for record in confirmation["phi_comparisons"].values())
    )
    gate_2 = (
        evaluation["controls"]["observed_minus_scrambled_phi_loss"]["ci_high"] < 0
        and evaluation["controls"]["observed_minus_broken_phi_loss"]["ci_high"] < 0
        and confirmation["controls"]["observed_minus_scrambled_phi_loss"]["mean"] < 0
        and confirmation["controls"]["observed_minus_broken_phi_loss"]["mean"] < 0
    )
    gate_3 = (
        all(record["a_closest_target_to_mean"] == "phi_projection" for record in evaluation["levels"].values())
        and all(record["a_closest_target_to_mean"] == "phi_projection" for record in confirmation["levels"].values())
    )
    gate_4 = (
        evaluation["closest_target_to_free_a_angle"] == "phi_projection"
        and confirmation["closest_target_to_free_a_angle"] == "phi_projection"
    )
    summary["verdict"] = {
        "gate_1_phi_target_specificity": gate_1,
        "gate_2_real_phase_relation": gate_2,
        "gate_3_cross_rung_recurrence": gate_3,
        "gate_4_free_angle_proximity": gate_4,
        "overall_octave_to_phi_projection_supported": gate_1 and gate_2 and gate_3 and gate_4,
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
    prior_roots, prior_diagnostics = extract_roots(base / "source_data")
    retained, projection_diagnostics = retain_roots(prior_roots)
    rows, control_diagnostics = build_rows(retained)
    diagnostics = {**prior_diagnostics, **projection_diagnostics, **control_diagnostics}
    summary, level_table = summarize(rows, diagnostics)

    results = base / "results"
    row_path = results / "octave_projection_root_results.csv"
    level_path = results / "octave_projection_level_summary.csv"
    summary_path = results / "octave_projection_summary.json"
    write_csv(row_path, rows)
    write_csv(level_path, level_table)
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8")

    print(json.dumps({
        "eligible_roots": {
            split: projection_diagnostics.get(f"{split}_projection_eligible_roots", 0)
            for split in ("calibration", "evaluation", "holdout")
        },
        "splits": summary["splits"],
        "verdict": summary["verdict"],
    }, indent=2, allow_nan=True))
    for path in (row_path, level_path, summary_path):
        print(f"{path.name}\t{hashlib.sha256(path.read_bytes()).hexdigest().upper()}")


if __name__ == "__main__":
    main()

