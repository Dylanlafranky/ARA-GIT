#!/usr/bin/env python3
"""Combine PN7B's exact adjacent-prime ARA inventories across R7-R11.

This is a deterministic post-endpoint decompression of the already validated
PN7B aggregates. It does not generate or predict primes, and it does not claim
to cover the infinite prime sequence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE_NPZ = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.npz"
SOURCE_JSON = HERE / "PN7B_ACTUAL_PRIME_NODE_GAP_AGGREGATES.json"
PAIR_CSV = HERE / "PN7B_ALL_MEASURED_PRIME_ARA_EXACT_GAP_PAIRS.csv"
STATE_CSV = HERE / "PN7B_ALL_MEASURED_PRIME_ARA_EXACT_STATES.csv"
SUMMARY_JSON = HERE / "PN7B_ALL_MEASURED_PRIME_ARA_SUMMARY.json"
RUNGS = ("r7", "r8", "r9", "r10", "r11")
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_MIRROR = 2.0 - PHI


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def weighted_quantiles(values: np.ndarray, counts: np.ndarray) -> dict[str, float]:
    order = np.argsort(values)
    sorted_values = values[order]
    cumulative = np.cumsum(counts[order])
    total = int(cumulative[-1])
    result: dict[str, float] = {}
    for quantile in (0.01, 0.05, 0.25, 0.50, 0.75, 0.95, 0.99):
        index = int(np.searchsorted(cumulative, quantile * total, side="left"))
        result[f"q{int(100 * quantile):02d}"] = float(sorted_values[index])
    return result


def main() -> dict:
    source_meta = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    loaded = np.load(SOURCE_NPZ)
    rung_matrices = {
        rung: loaded[f"{rung}__gap_pair_inventory"].astype(np.int64, copy=False)
        for rung in RUNGS
    }
    width = max(matrix.shape[0] for matrix in rung_matrices.values())
    combined = np.zeros((width, width), dtype=np.int64)
    for matrix in rung_matrices.values():
        combined[: matrix.shape[0], : matrix.shape[1]] += matrix

    incoming, outgoing = np.nonzero(combined)
    counts = combined[incoming, outgoing]
    ara_values = 2.0 * outgoing / (incoming + outgoing)
    node_total = int(counts.sum())
    expected_total = sum(int(source_meta["rungs"][rung]["node_total"]) for rung in RUNGS)
    if node_total != expected_total:
        raise RuntimeError(f"node total mismatch: {node_total} != {expected_total}")

    state_counts: dict[Fraction, int] = {}
    state_rung_counts: dict[Fraction, dict[str, int]] = {}
    pair_rows: list[dict] = []
    for left, right, count in zip(incoming.tolist(), outgoing.tolist(), counts.tolist()):
        state = Fraction(2 * right, left + right)
        per_rung = {
            rung: int(rung_matrices[rung][left, right])
            if left < rung_matrices[rung].shape[0] and right < rung_matrices[rung].shape[1]
            else 0
            for rung in RUNGS
        }
        state_counts[state] = state_counts.get(state, 0) + count
        if state not in state_rung_counts:
            state_rung_counts[state] = {rung: 0 for rung in RUNGS}
        for rung in RUNGS:
            state_rung_counts[state][rung] += per_rung[rung]
        pair_rows.append(
            {
                "incoming_gap": left,
                "outgoing_gap": right,
                "local_span": left + right,
                "ara_numerator": state.numerator,
                "ara_denominator": state.denominator,
                "ara_value": float(state),
                "distance_from_ridge": float(state) - 1.0,
                **{f"{rung}_count": per_rung[rung] for rung in RUNGS},
                "total_count": count,
                "share": count / node_total,
            }
        )

    pair_fields = [
        "incoming_gap", "outgoing_gap", "local_span", "ara_numerator", "ara_denominator",
        "ara_value", "distance_from_ridge", *[f"{rung}_count" for rung in RUNGS],
        "total_count", "share",
    ]
    with PAIR_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=pair_fields)
        writer.writeheader()
        writer.writerows(sorted(pair_rows, key=lambda row: (row["incoming_gap"], row["outgoing_gap"])))

    state_rows: list[dict] = []
    for state in sorted(state_counts, key=float):
        mirror = Fraction(2, 1) - state
        count = state_counts[state]
        mirror_count = state_counts.get(mirror, 0)
        state_rows.append(
            {
                "ara_numerator": state.numerator,
                "ara_denominator": state.denominator,
                "ara_value": float(state),
                "mirror_numerator": mirror.numerator,
                "mirror_denominator": mirror.denominator,
                "mirror_value": float(mirror),
                "distance_from_ridge": float(state) - 1.0,
                "count": count,
                "share": count / node_total,
                "mirror_count": mirror_count,
                "count_minus_mirror": count - mirror_count,
                **{f"{rung}_count": state_rung_counts[state][rung] for rung in RUNGS},
            }
        )

    state_fields = [
        "ara_numerator", "ara_denominator", "ara_value", "mirror_numerator",
        "mirror_denominator", "mirror_value", "distance_from_ridge", "count", "share",
        "mirror_count", "count_minus_mirror", *[f"{rung}_count" for rung in RUNGS],
    ]
    with STATE_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=state_fields)
        writer.writeheader()
        writer.writerows(state_rows)

    equal_count = int(np.trace(combined))
    below_count = int(combined[np.tril_indices(width, -1)].sum())
    above_count = int(combined[np.triu_indices(width, 1)].sum())
    expected_equal = sum(int(source_meta["rungs"][rung]["exact_equal_gap_nodes"]) for rung in RUNGS)
    expected_below = sum(int(source_meta["rungs"][rung]["incoming_gap_larger_nodes"]) for rung in RUNGS)
    expected_above = sum(int(source_meta["rungs"][rung]["outgoing_gap_larger_nodes"]) for rung in RUNGS)
    expected_mean_ara = 1.0 + sum(
        float(source_meta["rungs"][rung]["mean_asymmetry"])
        * int(source_meta["rungs"][rung]["node_total"])
        for rung in RUNGS
    ) / node_total
    probability = combined / node_total
    mirror_probability = probability.T
    transpose_tv = float(0.5 * np.abs(probability - mirror_probability).sum())
    transpose_cosine = float(
        (probability.ravel() @ mirror_probability.ravel())
        / (np.linalg.norm(probability) * np.linalg.norm(mirror_probability))
    )
    mean_ara = float(np.dot(ara_values, counts) / node_total)
    mean_abs_distance = float(np.dot(np.abs(ara_values - 1.0), counts) / node_total)
    rms_distance = float(np.sqrt(np.dot((ara_values - 1.0) ** 2, counts) / node_total))

    top_states = sorted(state_counts.items(), key=lambda item: (-item[1], float(item[0])))[:20]
    states_without_observed_mirror = [
        state for state in state_counts if (Fraction(2, 1) - state) not in state_counts
    ]
    nodes_without_observed_mirror = sum(state_counts[state] for state in states_without_observed_mirror)
    phi_bands = {}
    for tolerance in (0.001, 0.005, 0.010, 0.020, 0.050):
        mask = (np.abs(ara_values - PHI) <= tolerance) | (
            np.abs(ara_values - PHI_MIRROR) <= tolerance
        )
        count = int(counts[mask].sum())
        phi_bands[f"within_{tolerance:.3f}"] = {"count": count, "share": count / node_total}

    summary = {
        "status": "DESCRIPTIVE_POST_ENDPOINT_DECOMPRESSION_OF_VALIDATED_PN7B",
        "scope": "every internal actual prime in the five complete PN7B windows; not all infinitely many primes",
        "formula": "x_i = 2*g_out/(g_in+g_out)",
        "source_npz": SOURCE_NPZ.name,
        "source_npz_sha256": sha256(SOURCE_NPZ),
        "source_json": SOURCE_JSON.name,
        "source_json_sha256": sha256(SOURCE_JSON),
        "rungs": {
            rung: {
                "interval": source_meta["rungs"][rung]["interval"],
                "prime_total": int(source_meta["rungs"][rung]["prime_total"]),
                "node_total": int(source_meta["rungs"][rung]["node_total"]),
            }
            for rung in RUNGS
        },
        "combined": {
            "node_total": node_total,
            "nonzero_exact_gap_pairs": int(counts.size),
            "distinct_exact_ara_states": len(state_counts),
            "mean_ara": mean_ara,
            "median_ara": weighted_quantiles(ara_values, counts)["q50"],
            "mean_absolute_distance_from_1": mean_abs_distance,
            "rms_distance_from_1": rms_distance,
            "below_1": {"count": below_count, "share": below_count / node_total},
            "exactly_1": {"count": equal_count, "share": equal_count / node_total},
            "above_1": {"count": above_count, "share": above_count / node_total},
            "weighted_quantiles": weighted_quantiles(ara_values, counts),
            "exact_gap_pair_transpose_tv": transpose_tv,
            "exact_gap_pair_transpose_cosine": transpose_cosine,
            "states_without_observed_mirror": len(states_without_observed_mirror),
            "nodes_in_states_without_observed_mirror": nodes_without_observed_mirror,
            "share_in_states_without_observed_mirror": nodes_without_observed_mirror / node_total,
        },
        "top_exact_states": [
            {
                "fraction": f"{state.numerator}/{state.denominator}",
                "ara_value": float(state),
                "count": count,
                "share": count / node_total,
            }
            for state, count in top_states
        ],
        "phi_landmarks": {
            "phi": PHI,
            "mirror": PHI_MIRROR,
            "exact_hits": 0,
            "reason_exact_hits_are_zero": "Every adjacent-gap ARA is rational; phi is irrational.",
            "post_hoc_nearby_occupancy_without_null_baseline": phi_bands,
        },
        "checks": {
            "combined_total_matches_all_rung_node_totals": node_total == expected_total,
            "side_partition_sums_to_total": below_count + equal_count + above_count == node_total,
            "state_counts_sum_to_total": sum(state_counts.values()) == node_total,
            "pair_rows_sum_to_total": sum(row["total_count"] for row in pair_rows) == node_total,
            "equal_count_matches_source_metadata": equal_count == expected_equal,
            "below_count_matches_source_metadata": below_count == expected_below,
            "above_count_matches_source_metadata": above_count == expected_above,
            "mean_matches_weighted_source_metadata": abs(mean_ara - expected_mean_ara) < 1e-14,
        },
    }
    if not all(summary["checks"].values()):
        raise RuntimeError(f"validation failed: {summary['checks']}")
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
