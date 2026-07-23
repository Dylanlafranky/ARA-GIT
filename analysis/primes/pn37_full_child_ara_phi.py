"""PN37: measure the complete lower factor-child ARA field at every PN10B prime.

The calculation is post-hoc on the already opened PN10B interval.  It retains
every prime parent and every lower prime gate q <= sqrt(p).  Raw (p, q) rows
are streamed into compact per-parent and per-gate summaries because the full
Cartesian child field contains hundreds of millions of relations.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from pn10b_child_phase_prime_ranking import base_primes, segmented_least_prime_factor


HERE = Path(__file__).resolve().parent
LOW = 4_000_000_000
HIGH = 4_001_000_000
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_LEFT = 2.0 - PHI

LANDMARKS = {
    "phi": PHI_LEFT,
    "quarter": 0.25,
    "third": 1.0 / 3.0,
    "half": 0.5,
    "two_thirds": 2.0 / 3.0,
}

ARA_REGION_NAMES = [
    "left_singularity_well",
    "left_inner_to_phi",
    "left_phi_to_ridge",
    "ridge_to_right_phi",
    "right_phi_to_inner",
    "right_singularity_well",
]
ARA_REGION_BOUNDS = np.array([0.0, 0.25, PHI_LEFT, 1.0, PHI, 1.75, 2.0 + 1e-12])
CHILD_HISTOGRAM_BIN_COUNT = 160
CHILD_HISTOGRAM_BOUNDS = np.linspace(0.0, 2.0, CHILD_HISTOGRAM_BIN_COUNT + 1)

RESULTS_PATH = HERE / "PN37_FULL_CHILD_ARA_PHI_RESULTS.json"
PROTOCOL_PATH = HERE / "PN37_FULL_CHILD_ARA_PHI_PROTOCOL_v1_FROZEN.md"
PARENT_PATH = HERE / "PN37_FULL_CHILD_ARA_PARENT_SUMMARIES.csv"
GATE_PATH = HERE / "PN37_FULL_CHILD_ARA_GATE_SUMMARIES.csv"
VALIDATION_PATH = HERE / "PN37_FULL_CHILD_ARA_PHI_VALIDATION.json"


def describe(values: np.ndarray) -> dict[str, float | int]:
    quantiles = np.quantile(values.astype(np.float64), [0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1])
    return {
        "count": int(values.size),
        "mean": float(np.mean(values)),
        "sd": float(np.std(values)),
        "min": float(quantiles[0]),
        "p01": float(quantiles[1]),
        "p05": float(quantiles[2]),
        "p25": float(quantiles[3]),
        "median": float(quantiles[4]),
        "p75": float(quantiles[5]),
        "p95": float(quantiles[6]),
        "p99": float(quantiles[7]),
        "max": float(quantiles[8]),
    }


def exact_uniform_nonzero_mean_distance(q: int, left_landmark: float) -> float:
    """Mean distance to (left, 2-left) over residues 1..q-1.

    All q > 2 are odd primes.  Mirror residues r and q-r have equal distance,
    so the exact finite sum reduces to the lower half of the gate.
    """
    if q == 2:
        return 1.0 - left_landmark
    m = (q - 1) // 2
    target = left_landmark * q / 2.0
    k = min(max(int(math.floor(target)), 0), m)
    sum_abs_residue = (
        (2.0 * k - m) * target
        + m * (m + 1) / 2.0
        - k * (k + 1)
    )
    return 4.0 * sum_abs_residue / (q * (q - 1))


def nearest_folded_residue(q: int, left_landmark: float) -> int:
    if q == 2:
        return 1
    m = (q - 1) // 2
    target = left_landmark * q / 2.0
    return min(max(int(math.floor(target + 0.5)), 1), m)


def main() -> None:
    numbers, least_factor = segmented_least_prime_factor(LOW, HIGH)
    is_prime = least_factor == 0
    parents = numbers[is_prime].astype(np.int64)
    gates = base_primes(int(math.isqrt(int(parents[-1]))))

    parent_count = parents.size
    parent_child_count = np.zeros(parent_count, dtype=np.int32)
    parent_sum_a = np.zeros(parent_count, dtype=np.float64)
    parent_sum_ridge_distance = np.zeros(parent_count, dtype=np.float64)
    parent_sum_phi_distance = np.zeros(parent_count, dtype=np.float64)
    parent_min_phi_distance = np.full(parent_count, np.inf, dtype=np.float64)
    parent_phi_hits = np.zeros(parent_count, dtype=np.int32)

    global_pair_count = 0
    global_sum_a = 0.0
    global_sum_ridge_distance = 0.0
    global_below = 0
    global_equal = 0
    global_above = 0
    global_min_a = math.inf
    global_max_a = -math.inf
    global_region_counts = np.zeros(len(ARA_REGION_NAMES), dtype=np.int64)
    global_child_histogram = np.zeros(CHILD_HISTOGRAM_BIN_COUNT, dtype=np.int64)
    max_closure_error = 0.0
    zero_remainder_count = 0

    aggregate = {
        name: {
            "observed_hits": 0,
            "expected_hits": 0.0,
            "observed_distance_sum": 0.0,
            "expected_distance_sum": 0.0,
            "gate_occupancy_excesses": [],
            "gate_distance_deltas": [],
            "favorable_occupancy_gate_count": 0,
            "favorable_distance_gate_count": 0,
        }
        for name in LANDMARKS
    }
    gate_rows: list[dict[str, float | int]] = []

    for gate_index, q_value in enumerate(gates):
        q = int(q_value)
        first_parent = int(np.searchsorted(parents, q * q, side="left"))
        eligible = parents[first_parent:]
        if eligible.size == 0:
            continue

        remainders = eligible % q
        zero_remainder_count += int(np.count_nonzero(remainders == 0))
        phase_a = 2.0 * remainders.astype(np.float64) / q
        ridge_distance = np.abs(phase_a - 1.0)
        folded = np.minimum(remainders, q - remainders).astype(np.int64)

        parent_child_count[first_parent:] += 1
        parent_sum_a[first_parent:] += phase_a
        parent_sum_ridge_distance[first_parent:] += ridge_distance

        global_pair_count += int(eligible.size)
        global_sum_a += float(np.sum(phase_a))
        global_sum_ridge_distance += float(np.sum(ridge_distance))
        global_below += int(np.count_nonzero(phase_a < 1.0))
        global_equal += int(np.count_nonzero(phase_a == 1.0))
        global_above += int(np.count_nonzero(phase_a > 1.0))
        global_min_a = min(global_min_a, float(np.min(phase_a)))
        global_max_a = max(global_max_a, float(np.max(phase_a)))
        global_region_counts += np.histogram(phase_a, bins=ARA_REGION_BOUNDS)[0]
        global_child_histogram += np.histogram(phase_a, bins=CHILD_HISTOGRAM_BOUNDS)[0]
        max_closure_error = max(max_closure_error, float(np.max(np.abs(phase_a + (2.0 - phase_a) - 2.0))))

        max_folded = 1 if q == 2 else (q - 1) // 2
        folded_counts = np.bincount(folded, minlength=max_folded + 1)
        folded_values = np.arange(folded_counts.size, dtype=np.float64)
        cumulative_counts = np.cumsum(folded_counts, dtype=np.int64)
        cumulative_weight = np.cumsum(folded_counts * folded_values, dtype=np.float64)
        total_count = int(eligible.size)
        total_weight = float(cumulative_weight[-1])

        row: dict[str, float | int] = {
            "gate_rank": gate_index + 1,
            "gate_q": q,
            "first_eligible_parent": int(eligible[0]),
            "eligible_parent_count": total_count,
            "mean_phase_a": float(np.mean(phase_a)),
            "mean_ridge_distance": float(np.mean(ridge_distance)),
            "below_ridge_share": float(np.mean(phase_a < 1.0)),
            "equal_ridge_share": float(np.mean(phase_a == 1.0)),
            "above_ridge_share": float(np.mean(phase_a > 1.0)),
        }

        for name, left in LANDMARKS.items():
            target = left * q / 2.0
            split = min(max(int(math.floor(target)), 0), folded_counts.size - 1)
            count_below = int(cumulative_counts[split])
            weight_below = float(cumulative_weight[split])
            sum_abs_residue = (
                target * count_below
                - weight_below
                + (total_weight - weight_below)
                - target * (total_count - count_below)
            )
            observed_distance_sum = (2.0 / q) * sum_abs_residue
            observed_mean_distance = observed_distance_sum / total_count
            expected_mean_distance = exact_uniform_nonzero_mean_distance(q, left)

            nearest_residue = nearest_folded_residue(q, left)
            observed_hits = int(folded_counts[nearest_residue])
            selected_residue_count = 1 if q == 2 else 2
            expected_share = selected_residue_count / (q - 1)
            observed_share = observed_hits / total_count
            expected_hits = total_count * expected_share
            occupancy_excess = observed_share - expected_share
            distance_delta = observed_mean_distance - expected_mean_distance

            stats = aggregate[name]
            stats["observed_hits"] += observed_hits
            stats["expected_hits"] += expected_hits
            stats["observed_distance_sum"] += observed_distance_sum
            stats["expected_distance_sum"] += expected_mean_distance * total_count
            if q != 2:
                stats["gate_occupancy_excesses"].append(occupancy_excess)
                stats["gate_distance_deltas"].append(distance_delta)
                stats["favorable_occupancy_gate_count"] += int(occupancy_excess > 0.0)
                stats["favorable_distance_gate_count"] += int(distance_delta < 0.0)

            row[f"{name}_nearest_folded_residue"] = nearest_residue
            row[f"{name}_observed_hits"] = observed_hits
            row[f"{name}_observed_share"] = observed_share
            row[f"{name}_expected_share"] = expected_share
            row[f"{name}_occupancy_excess"] = occupancy_excess
            row[f"{name}_occupancy_lift"] = observed_share / expected_share
            row[f"{name}_observed_mean_distance"] = observed_mean_distance
            row[f"{name}_expected_mean_distance"] = expected_mean_distance
            row[f"{name}_distance_delta"] = distance_delta

            if name == "phi":
                phi_distances = (2.0 / q) * np.abs(folded.astype(np.float64) - target)
                parent_sum_phi_distance[first_parent:] += phi_distances
                parent_min_phi_distance[first_parent:] = np.minimum(
                    parent_min_phi_distance[first_parent:], phi_distances
                )
                hits = folded == nearest_residue
                parent_phi_hits[first_parent:] += hits.astype(np.int32)

        gate_rows.append(row)

    parent_centroid = parent_sum_a / parent_child_count
    parent_mean_ridge_distance = parent_sum_ridge_distance / parent_child_count
    parent_mean_phi_distance = parent_sum_phi_distance / parent_child_count
    parent_phi_hit_share = parent_phi_hits / parent_child_count

    parent_rows = [
        {
            "parent_prime": int(p),
            "child_gate_count": int(parent_child_count[i]),
            "child_centroid": float(parent_centroid[i]),
            "mean_ridge_distance": float(parent_mean_ridge_distance[i]),
            "mean_phi_pair_distance": float(parent_mean_phi_distance[i]),
            "minimum_phi_pair_distance": float(parent_min_phi_distance[i]),
            "nearest_phi_residue_hit_count": int(parent_phi_hits[i]),
            "nearest_phi_residue_hit_share": float(parent_phi_hit_share[i]),
        }
        for i, p in enumerate(parents)
    ]

    primary_pair_count = global_pair_count - parent_count  # remove the q=2 child from each odd prime
    landmark_summary: dict[str, dict[str, float | int]] = {}
    for name, stats in aggregate.items():
        # Remove q=2 from pair-weighted distance and occupancy comparisons.
        q2_distance = 1.0 - LANDMARKS[name]
        q2_hits = parent_count
        q2_expected_hits = float(parent_count)
        observed_hits = int(stats["observed_hits"] - q2_hits)
        expected_hits = float(stats["expected_hits"] - q2_expected_hits)
        observed_distance_sum = float(stats["observed_distance_sum"] - q2_distance * parent_count)
        expected_distance_sum = float(stats["expected_distance_sum"] - q2_distance * parent_count)
        occupancy_excesses = np.asarray(stats["gate_occupancy_excesses"], dtype=np.float64)
        distance_deltas = np.asarray(stats["gate_distance_deltas"], dtype=np.float64)
        gate_count = int(occupancy_excesses.size)
        landmark_summary[name] = {
            "left_landmark": LANDMARKS[name],
            "right_landmark": 2.0 - LANDMARKS[name],
            "child_pair_weighted_observed_hits": observed_hits,
            "child_pair_weighted_expected_hits": expected_hits,
            "child_pair_weighted_occupancy_lift": observed_hits / expected_hits,
            "child_pair_weighted_observed_hit_share": observed_hits / primary_pair_count,
            "child_pair_weighted_expected_hit_share": expected_hits / primary_pair_count,
            "child_pair_weighted_observed_mean_distance": observed_distance_sum / primary_pair_count,
            "child_pair_weighted_expected_mean_distance": expected_distance_sum / primary_pair_count,
            "child_pair_weighted_distance_delta": (observed_distance_sum - expected_distance_sum)
            / primary_pair_count,
            "gate_balanced_mean_occupancy_excess": float(np.mean(occupancy_excesses)),
            "gate_balanced_median_occupancy_excess": float(np.median(occupancy_excesses)),
            "gate_balanced_mean_distance_delta": float(np.mean(distance_deltas)),
            "gate_balanced_median_distance_delta": float(np.median(distance_deltas)),
            "favorable_occupancy_gate_share": int(stats["favorable_occupancy_gate_count"]) / gate_count,
            "favorable_distance_gate_share": int(stats["favorable_distance_gate_count"]) / gate_count,
            "primary_gate_count": gate_count,
        }

    phi_summary = landmark_summary["phi"]
    control_summaries = [landmark_summary[name] for name in LANDMARKS if name != "phi"]
    phi_beats_controls_occupancy = all(
        float(phi_summary["child_pair_weighted_occupancy_lift"])
        > float(control["child_pair_weighted_occupancy_lift"])
        for control in control_summaries
    )
    phi_beats_controls_distance = all(
        float(phi_summary["child_pair_weighted_distance_delta"])
        < float(control["child_pair_weighted_distance_delta"])
        for control in control_summaries
    )
    phi_directionally_favorable = (
        float(phi_summary["child_pair_weighted_occupancy_lift"]) > 1.0
        and float(phi_summary["child_pair_weighted_distance_delta"]) < 0.0
    )
    phi_protocol_pass = bool(
        phi_directionally_favorable and phi_beats_controls_occupancy and phi_beats_controls_distance
    )

    expected_parent_counts = np.searchsorted(gates, np.sqrt(parents), side="right")
    checks = [
        {
            "name": "all source parents marked prime",
            "passed": bool(np.all(is_prime[np.searchsorted(numbers, parents)])),
            "detail": f"parents={parent_count}",
        },
        {
            "name": "per-parent child counts match pi(sqrt(parent))",
            "passed": bool(np.array_equal(parent_child_count, expected_parent_counts)),
            "detail": f"max_abs_difference={int(np.max(np.abs(parent_child_count - expected_parent_counts)))}",
        },
        {
            "name": "no prime child has zero remainder",
            "passed": zero_remainder_count == 0,
            "detail": f"zero_remainders={zero_remainder_count}",
        },
        {
            "name": "all streamed TE-ARA closures equal two",
            "passed": max_closure_error < 1e-14,
            "detail": f"max_abs_error={max_closure_error:.3g}",
        },
        {
            "name": "parent child totals reconcile",
            "passed": int(np.sum(parent_child_count, dtype=np.int64)) == global_pair_count,
            "detail": f"parent_sum={int(np.sum(parent_child_count, dtype=np.int64))}; global={global_pair_count}",
        },
        {
            "name": "gate child totals reconcile",
            "passed": sum(int(row["eligible_parent_count"]) for row in gate_rows) == global_pair_count,
            "detail": f"gate_sum={sum(int(row['eligible_parent_count']) for row in gate_rows)}; global={global_pair_count}",
        },
        {
            "name": "ridge-side totals reconcile",
            "passed": global_below + global_equal + global_above == global_pair_count,
            "detail": f"below={global_below}; equal={global_equal}; above={global_above}",
        },
        {
            "name": "ARA landmark-region totals reconcile",
            "passed": int(np.sum(global_region_counts, dtype=np.int64)) == global_pair_count,
            "detail": f"region_sum={int(np.sum(global_region_counts, dtype=np.int64))}; global={global_pair_count}",
        },
        {
            "name": "child histogram totals reconcile",
            "passed": int(np.sum(global_child_histogram, dtype=np.int64)) == global_pair_count,
            "detail": f"histogram_sum={int(np.sum(global_child_histogram, dtype=np.int64))}; global={global_pair_count}",
        },
        {
            "name": "parent Phi hits reconcile with gate Phi hits",
            "passed": int(np.sum(parent_phi_hits, dtype=np.int64)) == int(aggregate["phi"]["observed_hits"]),
            "detail": (
                f"parent_sum={int(np.sum(parent_phi_hits, dtype=np.int64))}; "
                f"gate_sum={int(aggregate['phi']['observed_hits'])}"
            ),
        },
        {
            "name": "output row populations are complete",
            "passed": len(parent_rows) == parent_count and len(gate_rows) == gates.size,
            "detail": f"parent_rows={len(parent_rows)}; gate_rows={len(gate_rows)}",
        },
    ]

    results = {
        "test_id": "PN37/FULL-CHILD-ARA-PHI/v1",
        "status": "post_hoc_structural_on_opened_interval",
        "protocol_sha256": hashlib.sha256(PROTOCOL_PATH.read_bytes()).hexdigest(),
        "scope": {
            "low_inclusive": LOW,
            "high_exclusive": HIGH,
            "integer_count": int(numbers.size),
            "parent_prime_count": int(parent_count),
            "lower_prime_gate_count": int(gates.size),
            "full_child_pair_count": int(global_pair_count),
            "primary_phi_child_pair_count_excluding_q2": int(primary_pair_count),
            "minimum_gate": int(gates[0]),
            "maximum_gate": int(gates[-1]),
        },
        "definitions": {
            "child_phase_a": "A_q(p)=2*(p mod q)/q for every prime q<=sqrt(p)",
            "child_phase_b": "B_q(p)=2-A_q(p)",
            "phi_pair": [PHI_LEFT, PHI],
            "primary_phi_occupancy": "nearest available nonzero residue to each Phi landmark within each q",
            "uniform_gate_baseline": "all nonzero residues 1..q-1 have equal weight",
            "primary_exclusion": "q=2 excluded from Phi comparisons because its only nonzero residue forces A=1",
        },
        "pooled_child_geometry": {
            "mean_phase_a": global_sum_a / global_pair_count,
            "mean_phase_b": 2.0 - global_sum_a / global_pair_count,
            "mean_ridge_distance": global_sum_ridge_distance / global_pair_count,
            "minimum_phase_a": global_min_a,
            "maximum_phase_a": global_max_a,
            "below_ridge_count": global_below,
            "equal_ridge_count": global_equal,
            "above_ridge_count": global_above,
            "below_ridge_share": global_below / global_pair_count,
            "equal_ridge_share": global_equal / global_pair_count,
            "above_ridge_share": global_above / global_pair_count,
            "ara_landmark_regions": [
                {
                    "region": name,
                    "lower_inclusive": float(ARA_REGION_BOUNDS[index]),
                    "upper_exclusive": float(ARA_REGION_BOUNDS[index + 1]),
                    "count": int(global_region_counts[index]),
                    "share": float(global_region_counts[index] / global_pair_count),
                }
                for index, name in enumerate(ARA_REGION_NAMES)
            ],
            "phase_a_histogram": {
                "bin_count": CHILD_HISTOGRAM_BIN_COUNT,
                "lower_edges": [float(value) for value in CHILD_HISTOGRAM_BOUNDS[:-1]],
                "upper_edges": [float(value) for value in CHILD_HISTOGRAM_BOUNDS[1:]],
                "counts": [int(value) for value in global_child_histogram],
                "shares": [float(value / global_pair_count) for value in global_child_histogram],
            },
        },
        "parent_distributions": {
            "child_gate_count": describe(parent_child_count.astype(np.float64)),
            "child_centroid": describe(parent_centroid),
            "mean_ridge_distance": describe(parent_mean_ridge_distance),
            "mean_phi_pair_distance": describe(parent_mean_phi_distance),
            "minimum_phi_pair_distance": describe(parent_min_phi_distance),
            "nearest_phi_residue_hit_count": describe(parent_phi_hits.astype(np.float64)),
            "nearest_phi_residue_hit_share": describe(parent_phi_hit_share),
        },
        "landmark_comparisons_excluding_q2": landmark_summary,
        "phi_decision": {
            "directionally_favorable": phi_directionally_favorable,
            "beats_all_controls_on_occupancy": phi_beats_controls_occupancy,
            "beats_all_controls_on_distance": phi_beats_controls_distance,
            "protocol_pass": phi_protocol_pass,
            "interpretation": (
                "descriptively_supported_at_child_level_pending_untouched_transfer"
                if phi_protocol_pass
                else "not_supported_by_this_child_level_comparison"
            ),
        },
        "interpretation_guards": [
            "The complete child field is a factor-sieve decomposition and is not a computational advance over established prime methods.",
            "A pooled child centroid near one can be produced by cancellation among locally asymmetric children.",
            "Exact Phi hits are impossible because every child phase is rational and Phi is irrational.",
            "The interval was already opened; any favorable Phi result remains post-hoc until transferred unchanged.",
            "The full raw child table is not emitted; per-parent and per-gate summaries reconcile exactly to the streamed pair count.",
        ],
    }
    validation = {
        "validation_id": "PN37/FULL-CHILD-ARA-PHI/VALIDATION/v1",
        "all_passed": all(bool(check["passed"]) for check in checks),
        "check_count": len(checks),
        "checks": checks,
    }

    RESULTS_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    with PARENT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(parent_rows[0].keys()))
        writer.writeheader()
        writer.writerows(parent_rows)
    with GATE_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(gate_rows[0].keys()))
        writer.writeheader()
        writer.writerows(gate_rows)

    print(
        json.dumps(
            {
                "results": str(RESULTS_PATH),
                "validation": str(VALIDATION_PATH),
                "parent_rows": len(parent_rows),
                "gate_rows": len(gate_rows),
                "full_child_pairs": global_pair_count,
                "phi_protocol_pass": phi_protocol_pass,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
