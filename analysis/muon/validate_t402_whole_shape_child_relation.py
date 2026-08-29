#!/usr/bin/env python3
"""Independent saved-output validation for T402."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTRA = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
VENDOR = HERE / "_vendor"
for entry in (EXTRA, VENDOR):
    if entry.exists():
        sys.path.insert(0, str(entry))

import numpy as np


OUT = HERE / "T402_whole_shape_child_relation"
PROTOCOL = HERE / "T402_WHOLE_SHAPE_CHILD_RELATION_PROTOCOL_2026-08-17.md"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)


def main() -> None:
    results = json.loads((OUT / "T402_RESULTS.json").read_text(encoding="utf-8"))
    split_rows = rows("T402_SPLITS.csv")
    invalid_rows = rows("T402_INVALID_SPLITS.csv")
    distributions = rows("T402_PRIMARY_BIN_DISTRIBUTIONS.csv")
    summary = rows("T402_BIN_SUMMARY.csv")
    topology = rows("T402_KDE_TOPOLOGY.csv")
    permutations = rows("T402_REFLECTION_PERMUTATIONS.csv")
    alignments = rows("T402_ALIGNMENT_CONTROLS.csv")
    sensitivities = rows("T402_BIN_SENSITIVITY.csv")

    valid = len(split_rows)
    grouped: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    for row in distributions:
        grouped[(int(row["salt"]), row["source"])].append(row)
    distribution_sums_ok = all(
        len(group) == 8 and close(sum(float(row["proportion_of_split_weight"]) for row in group), 1.0, 1e-9)
        for group in grouped.values()
    )

    c_matrix = []
    ac_matrix = []
    for salt in sorted({int(row["salt"]) for row in distributions}):
        c_group = sorted(grouped[(salt, "C")], key=lambda row: float(row["bin_center"]))
        ac_group = sorted(grouped[(salt, "AC")], key=lambda row: float(row["bin_center"]))
        c_matrix.append([float(row["proportion_of_split_weight"]) for row in c_group])
        ac_matrix.append([float(row["proportion_of_split_weight"]) for row in ac_group])
    c = np.asarray(c_matrix)
    ac = np.asarray(ac_matrix)
    d = np.mean(c, axis=0) - np.mean(ac, axis=0)

    c_lower = np.mean(c[:, 2:4], axis=1) - np.mean(c[:, 4:6], axis=1)
    c_upper = np.mean(c[:, 6:8], axis=1) - np.mean(c[:, 4:6], axis=1)
    ac_lower = np.mean(ac[:, 2:4], axis=1) - np.mean(ac[:, 4:6], axis=1)
    split_lower_d = np.mean(c[:, :4] - ac[:, :4], axis=1)
    split_upper_d = np.mean(c[:, 4:] - ac[:, 4:], axis=1)
    lower_advantage = c_lower - ac_lower

    exact_rows = [row for row in permutations if row["is_exact_reflection"].lower() == "true"]
    exact_rank = int(exact_rows[0]["rank"]) if len(exact_rows) == 1 else -1
    exact_cosine = float(exact_rows[0]["cosine_similarity"]) if len(exact_rows) == 1 else float("nan")
    unshifted = [row for row in alignments if row["is_unshifted"].lower() == "true"]
    unshifted_rank = int(unshifted[0]["error_rank_lower_is_better"]) if len(unshifted) == 1 else -1
    topology_passes = sum(row["passes_registered_windows"].lower() == "true" for row in topology)
    sensitivity_passes = sum(row["passes_cosine_0_65"].lower() == "true" for row in sensitivities)

    saved_gates = results["gates"]
    g2_recalc = bool(
        int(np.sum(d[:4] > 0)) >= 3
        and int(np.sum(d[4:] < 0)) >= 3
        and float(np.mean(split_lower_d > 0)) >= 0.65
        and float(np.mean(split_upper_d < 0)) >= 0.65
    )
    g3_recalc = topology_passes >= 3
    g4_recalc = bool(exact_cosine >= 0.75 and exact_rank <= 3 and sensitivity_passes >= 3)
    g5_recalc = bool(unshifted_rank <= 2 and float(np.mean(lower_advantage > 0)) >= 0.70)

    raw = results["raw_C_shape"]
    source = results["source_difference"]
    checks = {
        "protocol_hash_matches_frozen_file": results["protocol_sha256"] == sha256(PROTOCOL),
        "requested_split_accounting_is_400": valid + len(invalid_rows) == 400,
        "saved_valid_and_invalid_counts_match": valid == results["splits"]["valid"] and len(invalid_rows) == results["splits"]["invalid"],
        "distribution_row_count_is_valid_x2x8": len(distributions) == valid * 2 * 8,
        "each_distribution_sums_to_one": distribution_sums_ok and len(grouped) == valid * 2,
        "summary_has_two_sources_and_eight_bins": len(summary) == 16,
        "mean_differential_recalculates": all(close(a, b) for a, b in zip(d, results["source_difference"]["mean_C_minus_AC_by_bin"])),
        "raw_lower_contrast_recalculates": close(float(np.mean(c_lower)), raw["mean_lower_minus_saddle"]),
        "raw_upper_contrast_recalculates": close(float(np.mean(c_upper)), raw["mean_upper_minus_saddle"]),
        "source_split_fractions_recalculate": close(float(np.mean(split_lower_d > 0)), source["fraction_splits_mean_lower_positive"]) and close(float(np.mean(split_upper_d < 0)), source["fraction_splits_mean_upper_negative"]),
        "topology_has_four_bandwidths": len(topology) == 4 and topology_passes == results["continuous_topology"]["bandwidths_passing_registered_windows"],
        "reflection_has_24_unique_assignments": len(permutations) == 24 and len(exact_rows) == 1,
        "exact_reflection_metrics_match": exact_rank == results["reflection"]["exact_mapping_rank_of_24"] and close(exact_cosine, results["reflection"]["primary_eight_bin_cosine"]),
        "alignment_has_eight_shifts": len(alignments) == 8 and len(unshifted) == 1,
        "unshifted_alignment_rank_matches": unshifted_rank == results["alignment"]["unshifted_rank_of_8"],
        "bin_sensitivity_has_four_counts": len(sensitivities) == 4 and sensitivity_passes == results["reflection"]["bin_sensitivities_passing_cosine_0_65"],
        "G2_recalculates": g2_recalc == saved_gates["G2_source_specific_two_sided_difference"],
        "G3_recalculates": g3_recalc == saved_gates["G3_continuous_topology"],
        "G4_recalculates": g4_recalc == saved_gates["G4_exact_static_reflection"],
        "G5_recalculates": g5_recalc == saved_gates["G5_correct_source_alignment"],
        "G1_failure_matches_saved_interval_and_fractions": not saved_gates["G1_raw_whole_shape"] and raw["upper_resampling_interval_95"][0] <= 0 and raw["fraction_splits_upper_positive"] < 0.60,
        "verdict_matches_frozen_ladder": results["verdict"] == "NO STABLE WHOLE SHAPE",
        "static_figure_exists": (OUT / "T402_WHOLE_SHAPE_CHILD_RELATION.png").exists() and (OUT / "T402_WHOLE_SHAPE_CHILD_RELATION.png").stat().st_size > 100_000,
    }
    validation = {
        "test": "T402 independent saved-output validation",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "recalculated": {
            "valid_splits": valid,
            "invalid_splits": len(invalid_rows),
            "mean_C_minus_AC_by_bin": [float(value) for value in d],
            "mean_C_lower_minus_saddle": float(np.mean(c_lower)),
            "mean_C_upper_minus_saddle": float(np.mean(c_upper)),
            "exact_reflection_cosine": exact_cosine,
            "exact_reflection_rank": exact_rank,
            "unshifted_alignment_rank": unshifted_rank,
            "topology_bandwidth_pass_count": topology_passes,
        },
    }
    (OUT / "T402_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
