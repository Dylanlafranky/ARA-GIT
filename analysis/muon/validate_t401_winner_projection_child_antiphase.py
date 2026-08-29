#!/usr/bin/env python3
"""Independent saved-output validation for T401."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T401_winner_projection_child_antiphase"
PROTOCOL = HERE / "T401_WINNER_PROJECTION_CHILD_ANTIPHASE_PROTOCOL_2026-08-17.md"


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
    results = json.loads((OUT / "T401_RESULTS.json").read_text(encoding="utf-8"))
    valid = rows("T401_SPLITS.csv")
    invalid = rows("T401_INVALID_SPLITS.csv")
    distributions = rows("T401_SPLIT_BIN_DISTRIBUTIONS.csv")
    modes = rows("T401_SPLIT_MODES.csv")
    summary = rows("T401_BIN_SUMMARY.csv")
    pairs = rows("T401_MIRROR_RELATIONS.csv")
    permutations = rows("T401_ALL_PAIRING_SCORES.csv")
    null = rows("T401_SAMPLING_NULL.csv")

    grouped: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    for row in distributions:
        grouped[(int(row["salt"]), row["source"])].append(row)
    sums_ok = all(
        len(group) == 8 and close(sum(float(row["proportion_of_split_weight"]) for row in group), 1.0, 1e-9)
        for group in grouped.values()
    )

    c_gap = [row for row in distributions if row["source"] == "C" and close(float(row["bin_center"]), 1.375)]
    occupancy = sum(float(row["proportion_of_split_weight"]) for row in c_gap) / len(c_gap)
    binned_gap_winners = sum(row["is_binned_mode"].lower() == "true" for row in c_gap)
    c_modes = [row for row in modes if row["source"] == "C"]
    kde_gap_winners = sum(row["kde_mode_in_candidate_band"].lower() == "true" for row in c_modes)

    c_pair = [row for row in pairs if row["source"] == "C"]
    c_score = sum(float(row["negative_exchange_contribution"]) for row in c_pair) / len(c_pair)
    exact_c = [row for row in permutations if row["source"] == "C" and row["is_exact_reflection"].lower() == "true"]
    exact_ac = [row for row in permutations if row["source"] == "AC" and row["is_exact_reflection"].lower() == "true"]

    checks = {
        "protocol_hash_matches_frozen_file": results["protocol_sha256"] == sha256(PROTOCOL),
        "requested_split_accounting_is_200": len(valid) + len(invalid) == 200,
        "valid_split_count_is_164": len(valid) == 164 and results["splits"]["valid"] == 164,
        "invalid_split_count_is_36": len(invalid) == 36 and results["splits"]["invalid"] == 36,
        "distribution_row_count_is_164x2x8": len(distributions) == 164 * 2 * 8,
        "mode_row_count_is_164x2": len(modes) == 164 * 2,
        "each_distribution_sums_to_one": sums_ok and len(grouped) == 164 * 2,
        "summary_has_two_sources_and_eight_bins": len(summary) == 16,
        "candidate_occupancy_recalculates": close(occupancy, float(results["candidate_band"]["mean_occupancy_C"])),
        "candidate_binned_winner_count_recalculates": binned_gap_winners == 13 and close(binned_gap_winners / 164, float(results["candidate_band"]["binned_mode_fraction_C"])),
        "candidate_kde_winner_count_recalculates": kde_gap_winners == 17 and close(kde_gap_winners / 164, float(results["candidate_band"]["kde_mode_fraction_C"])),
        "mirror_relations_are_four_per_source": len(pairs) == 8,
        "all_pairings_are_24_per_source": len(permutations) == 48,
        "C_reflection_score_recalculates": close(c_score, float(results["reflection"]["C"]["exchange_score"])),
        "exact_reflection_is_unique_per_source": len(exact_c) == 1 and len(exact_ac) == 1,
        "sampling_null_has_eight_bins": len(null) == 8,
        "observed_gap_is_consistent_with_null": float(results["sampling_null"]["observed_vs_null_two_sided_binomial_p"]) > 0.05,
        "all_frozen_gates_failed": not any(bool(value) for value in results["gates"].values()),
        "verdict_matches_gate_state": results["verdict"] == "NO STABLE MISSING-WINNER BAND",
        "static_figure_exists": (OUT / "T401_WINNER_PROJECTION_CHILD_ANTIPHASE.png").exists() and (OUT / "T401_WINNER_PROJECTION_CHILD_ANTIPHASE.png").stat().st_size > 100_000,
    }
    validation = {
        "test": "T401 independent saved-output validation",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "recalculated": {
            "valid_splits": len(valid),
            "invalid_splits": len(invalid),
            "candidate_mean_occupancy_C": occupancy,
            "candidate_binned_winners_C": binned_gap_winners,
            "candidate_kde_winners_C": kde_gap_winners,
            "C_reflection_exchange_score": c_score,
        },
    }
    (OUT / "T401_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
