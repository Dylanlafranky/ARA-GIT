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
    ROOT_STEPS,
    SEED,
    TARGETS,
    Root,
    add_vectors,
    deterministic_permutation,
    extract_roots,
    magnitude,
)


LEVELS = tuple(range(5))
TRANSITIONS = tuple(range(4))


def complex_parent_vectors(steps: list[tuple[float, float]]) -> list[complex]:
    vectors = []
    for level in LEVELS:
        span = 2 ** (level + 1)
        x, y = add_vectors(steps, 0, span)
        vectors.append(complex(x, y))
    return vectors


def eligible_vectors(vectors: list[complex]) -> bool:
    return all(abs(value) >= MIN_STEP_M for value in vectors)


def wrap_angle(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def multipliers(vectors: list[complex]) -> list[complex]:
    return [vectors[index + 1] / vectors[index] for index in TRANSITIONS]


def circular_mean_angle(values: list[float]) -> float:
    resultant = sum(complex(math.cos(value), math.sin(value)) for value in values)
    if abs(resultant) < 1e-15:
        return 0.0
    return math.atan2(resultant.imag, resultant.real)


def angular_coherence(values: list[float]) -> float:
    resultant = sum(complex(math.cos(value), math.sin(value)) for value in values)
    return abs(resultant) / len(values)


def free_radial_scale(values: list[complex]) -> float:
    return math.exp(statistics.mean(math.log(abs(value)) for value in values))


def full_loss(values: list[complex], target: float) -> float:
    angles = [math.atan2(value.imag, value.real) for value in values]
    center = circular_mean_angle(angles)
    terms = [
        math.log(abs(value) / target) ** 2 + wrap_angle(angle - center) ** 2
        for value, angle in zip(values, angles)
    ]
    return math.sqrt(statistics.mean(terms))


def shorthand_loss(vectors: list[complex], target: float) -> float:
    base = abs(vectors[0])
    terms = []
    for level in range(1, len(vectors)):
        expected = base * target**level
        terms.append(math.log(abs(vectors[level]) / expected) ** 2)
    return math.sqrt(statistics.mean(terms))


def sequence_metrics(vectors: list[complex]) -> dict:
    values = multipliers(vectors)
    angles = [math.atan2(value.imag, value.real) for value in values]
    free_scale = free_radial_scale(values)
    record = {
        "free_scale": free_scale,
        "free_full_loss": full_loss(values, free_scale),
        "angular_coherence": angular_coherence(angles),
        "mean_rotation_rad": circular_mean_angle(angles),
        "mean_rotation_deg": math.degrees(circular_mean_angle(angles)),
    }
    for index, value in enumerate(values):
        record[f"scale_transition_{index}"] = abs(value)
        record[f"rotation_transition_{index}_deg"] = math.degrees(
            math.atan2(value.imag, value.real)
        )
    for name, target in TARGETS.items():
        record[f"full_loss_{name}"] = full_loss(values, target)
        record[f"shorthand_loss_{name}"] = shorthand_loss(vectors, target)
    return record


def eligible_spiral_roots(roots: list[Root]) -> tuple[list[tuple[Root, list[complex]]], dict]:
    retained = []
    diagnostics = defaultdict(int)
    for root in roots:
        vectors = complex_parent_vectors(root.steps)
        if not eligible_vectors(vectors):
            diagnostics[f"{root.split}_spiral_resolution_exclusions"] += 1
            continue
        retained.append((root, vectors))
        diagnostics[f"{root.split}_spiral_eligible_roots"] += 1
    return retained, dict(diagnostics)


def attach_broken_vectors(
    roots: list[tuple[Root, list[complex]]],
) -> dict[tuple[str, int, int], list[complex]]:
    by_video: dict[str, list[tuple[Root, list[complex]]]] = defaultdict(list)
    for item in roots:
        by_video[item[0].video].append(item)
    controls = {}
    for video, group in by_video.items():
        group.sort(key=lambda item: (item[0].start_frame, item[0].track_id, item[0].segment_index))
        if len(group) < 2:
            continue
        for index, (root, vectors) in enumerate(group):
            partner_vectors = group[(index + 1) % len(group)][1]
            broken = [vectors[0]]
            # Each next-rung vector comes from the paired root. This is used
            # only through q_l = partner Z_(l+1) / observed Z_l below.
            broken.extend(partner_vectors[1:])
            controls[(video, root.track_id, root.start_frame)] = broken
    return controls


def broken_metrics(observed: list[complex], partner_levels: list[complex]) -> dict:
    values = [partner_levels[level + 1] / observed[level] for level in TRANSITIONS]
    angles = [math.atan2(value.imag, value.real) for value in values]
    scale = free_radial_scale(values)
    return {
        "free_scale": scale,
        "free_full_loss": full_loss(values, scale),
        "angular_coherence": angular_coherence(angles),
    }


def build_rows(roots: list[tuple[Root, list[complex]]]) -> tuple[list[dict], dict]:
    broken = attach_broken_vectors(roots)
    diagnostics = defaultdict(int)
    rows = []
    for root, vectors in roots:
        observed = sequence_metrics(vectors)
        key_text = f"{root.video}:{root.track_id}:{root.start_frame}:spiral"
        permuted_steps = deterministic_permutation(root.steps, key_text)
        permuted_vectors = complex_parent_vectors(permuted_steps)
        if eligible_vectors(permuted_vectors):
            permuted = sequence_metrics(permuted_vectors)
        else:
            diagnostics[f"{root.split}_permutation_incomplete_controls"] += 1
            permuted = None

        key = (root.video, root.track_id, root.start_frame)
        partner_levels = broken.get(key)
        broken_record = broken_metrics(vectors, partner_levels) if partner_levels else None
        if broken_record is None:
            diagnostics[f"{root.split}_broken_incomplete_controls"] += 1

        row = {
            "split": root.split,
            "video": root.video,
            "file": root.file,
            "track_id": root.track_id,
            "segment_index": root.segment_index,
            "start_frame": root.start_frame,
            "time_sec": root.time_sec,
        }
        for level, vector in enumerate(vectors):
            row[f"parent_{level}_frames"] = 2 ** (level + 1)
            row[f"parent_{level}_magnitude"] = abs(vector)
            row[f"parent_{level}_angle_deg"] = math.degrees(math.atan2(vector.imag, vector.real))
        for name, value in observed.items():
            row[f"observed_{name}"] = value
        for name in ("free_scale", "free_full_loss", "angular_coherence"):
            row[f"permuted_{name}"] = permuted[name] if permuted else float("nan")
            row[f"broken_{name}"] = broken_record[name] if broken_record else float("nan")
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


def geometric_median_scale(rows: list[dict]) -> float:
    return math.exp(statistics.median(math.log(float(row["observed_free_scale"])) for row in rows))


def closest_target(value: float) -> str:
    return min(TARGETS, key=lambda name: abs(math.log(value / TARGETS[name])))


def summarize(rows: list[dict], diagnostics: dict) -> tuple[dict, list[dict]]:
    summary = {
        "source": "Zenodo 10.5281/zenodo.15102957",
        "protocol": "FROZEN_PROTOCOL_VERTICAL_ARA_SPIRAL_SCALE_2026-08-01.md",
        "root_steps": ROOT_STEPS,
        "bootstraps": BOOTSTRAPS,
        "diagnostics": diagnostics,
        "splits": {},
        "verdict": {},
    }
    target_table = []
    for split_index, split in enumerate(("calibration", "evaluation", "holdout")):
        subset = [row for row in rows if row["split"] == split]
        target_results = {}
        for target_index, (name, target) in enumerate(TARGETS.items()):
            full_values = [float(row[f"observed_full_loss_{name}"]) for row in subset]
            short_values = [float(row[f"observed_shorthand_loss_{name}"]) for row in subset]
            target_results[name] = {
                "target": target,
                "full_mean": statistics.mean(full_values),
                "full_median": statistics.median(full_values),
                "shorthand_mean": statistics.mean(short_values),
                "shorthand_median": statistics.median(short_values),
            }
            target_table.append({
                "split": split,
                "target": name,
                "target_value": target,
                "full_mean": target_results[name]["full_mean"],
                "full_median": target_results[name]["full_median"],
                "shorthand_mean": target_results[name]["shorthand_mean"],
                "shorthand_median": target_results[name]["shorthand_median"],
                "roots": len(subset),
                "videos": len({row["video"] for row in subset}),
            })
        free_scale = geometric_median_scale(subset)
        summary["splits"][split] = {
            "roots": len(subset),
            "videos": len({row["video"] for row in subset}),
            "geometric_median_free_scale": free_scale,
            "closest_fixed_target_to_free_scale": closest_target(free_scale),
            "mean_free_full_loss": statistics.mean(float(row["observed_free_full_loss"]) for row in subset),
            "mean_angular_coherence": statistics.mean(float(row["observed_angular_coherence"]) for row in subset),
            "mean_rotation_deg": statistics.mean(float(row["observed_mean_rotation_deg"]) for row in subset),
            "targets": target_results,
        }

        if split in ("evaluation", "holdout"):
            summary["splits"][split]["controls"] = {
                "full_loss_observed_minus_permuted": paired_bootstrap(
                    subset, "observed_free_full_loss", "permuted_free_full_loss", 100 + 10 * split_index
                ),
                "full_loss_observed_minus_broken": paired_bootstrap(
                    subset, "observed_free_full_loss", "broken_free_full_loss", 101 + 10 * split_index
                ),
                "coherence_observed_minus_permuted": paired_bootstrap(
                    subset, "observed_angular_coherence", "permuted_angular_coherence", 102 + 10 * split_index
                ),
                "coherence_observed_minus_broken": paired_bootstrap(
                    subset, "observed_angular_coherence", "broken_angular_coherence", 103 + 10 * split_index
                ),
            }
            comparisons = {"full": {}, "shorthand": {}}
            for target_index, name in enumerate(TARGETS):
                if name == "phi":
                    continue
                comparisons["full"][name] = paired_bootstrap(
                    subset,
                    "observed_full_loss_phi",
                    f"observed_full_loss_{name}",
                    200 + 20 * split_index + target_index,
                )
                comparisons["shorthand"][name] = paired_bootstrap(
                    subset,
                    "observed_shorthand_loss_phi",
                    f"observed_shorthand_loss_{name}",
                    300 + 20 * split_index + target_index,
                )
            summary["splits"][split]["phi_comparisons"] = comparisons

    evaluation = summary["splits"]["evaluation"]
    confirmation = summary["splits"]["holdout"]
    eval_controls = evaluation["controls"]
    confirm_controls = confirmation["controls"]
    gate_1 = (
        eval_controls["full_loss_observed_minus_permuted"]["ci_high"] < 0
        and eval_controls["full_loss_observed_minus_broken"]["ci_high"] < 0
        and eval_controls["coherence_observed_minus_permuted"]["ci_low"] > 0
        and eval_controls["coherence_observed_minus_broken"]["ci_low"] > 0
        and confirm_controls["full_loss_observed_minus_permuted"]["mean"] < 0
        and confirm_controls["full_loss_observed_minus_broken"]["mean"] < 0
        and confirm_controls["coherence_observed_minus_permuted"]["mean"] > 0
        and confirm_controls["coherence_observed_minus_broken"]["mean"] > 0
    )
    gate_2 = (
        all(record["ci_high"] < 0 for record in evaluation["phi_comparisons"]["full"].values())
        and all(record["mean"] < 0 for record in confirmation["phi_comparisons"]["full"].values())
    )
    gate_3 = (
        all(record["ci_high"] < 0 for record in evaluation["phi_comparisons"]["shorthand"].values())
        and all(record["mean"] < 0 for record in confirmation["phi_comparisons"]["shorthand"].values())
    )
    gate_4 = (
        evaluation["closest_fixed_target_to_free_scale"] == "phi"
        and confirmation["closest_fixed_target_to_free_scale"] == "phi"
    )
    summary["verdict"] = {
        "gate_1_repeated_spiral_operator": gate_1,
        "gate_2_phi_full_operator_scale": gate_2,
        "gate_3_phi_per_octave_shorthand": gate_3,
        "gate_4_free_scale_closest_to_phi": gate_4,
        "overall_vertical_ara_phi_spiral_supported": gate_1 and gate_2 and gate_3 and gate_4,
    }
    return summary, target_table


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
    retained, spiral_diagnostics = eligible_spiral_roots(prior_roots)
    rows, control_diagnostics = build_rows(retained)
    diagnostics = {**prior_diagnostics, **spiral_diagnostics, **control_diagnostics}
    summary, target_table = summarize(rows, diagnostics)

    results = base / "results"
    row_path = results / "spiral_scale_root_results.csv"
    table_path = results / "spiral_scale_target_summary.csv"
    summary_path = results / "spiral_scale_summary.json"
    write_csv(row_path, rows)
    write_csv(table_path, target_table)
    summary_path.write_text(json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8")

    print(json.dumps({
        "eligible_roots": {
            split: spiral_diagnostics.get(f"{split}_spiral_eligible_roots", 0)
            for split in ("calibration", "evaluation", "holdout")
        },
        "splits": summary["splits"],
        "verdict": summary["verdict"],
    }, indent=2, allow_nan=True))
    for path in (row_path, table_path, summary_path):
        print(f"{path.name}\t{hashlib.sha256(path.read_bytes()).hexdigest().upper()}")


if __name__ == "__main__":
    main()
