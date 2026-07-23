"""Independent validation of PN37 outputs and selected raw child relations."""

from __future__ import annotations

import csv
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

RESULTS_PATH = HERE / "PN37_FULL_CHILD_ARA_PHI_RESULTS.json"
PARENT_PATH = HERE / "PN37_FULL_CHILD_ARA_PARENT_SUMMARIES.csv"
GATE_PATH = HERE / "PN37_FULL_CHILD_ARA_GATE_SUMMARIES.csv"
OUTPUT_PATH = HERE / "PN37_FULL_CHILD_ARA_PHI_INDEPENDENT_VALIDATION.json"


def check(name: str, passed: bool, detail: str) -> dict[str, str | bool]:
    return {"name": name, "passed": bool(passed), "detail": detail}


def close(first: float, second: float, tolerance: float = 1e-12) -> bool:
    return abs(first - second) <= tolerance * max(1.0, abs(first), abs(second))


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    with PARENT_PATH.open(encoding="utf-8", newline="") as handle:
        parent_rows = list(csv.DictReader(handle))
    with GATE_PATH.open(encoding="utf-8", newline="") as handle:
        gate_rows = list(csv.DictReader(handle))

    numbers, least_factor = segmented_least_prime_factor(LOW, HIGH)
    parents = numbers[least_factor == 0].astype(np.int64)
    gates = base_primes(int(math.isqrt(int(parents[-1]))))
    scope = results["scope"]

    checks: list[dict[str, str | bool]] = []
    checks.append(
        check(
            "CSV row counts match regenerated source populations",
            len(parent_rows) == parents.size and len(gate_rows) == gates.size,
            f"parent_csv={len(parent_rows)} source={parents.size}; gate_csv={len(gate_rows)} source={gates.size}",
        )
    )

    parent_total = sum(int(row["child_gate_count"]) for row in parent_rows)
    gate_total = sum(int(row["eligible_parent_count"]) for row in gate_rows)
    checks.append(
        check(
            "independent CSV pair totals reconcile",
            parent_total == gate_total == int(scope["full_child_pair_count"]),
            f"parent_total={parent_total}; gate_total={gate_total}; result={scope['full_child_pair_count']}",
        )
    )

    parent_phi_hits = sum(int(row["nearest_phi_residue_hit_count"]) for row in parent_rows)
    gate_phi_hits = sum(int(row["phi_observed_hits"]) for row in gate_rows)
    checks.append(
        check(
            "independent CSV Phi hit totals reconcile",
            parent_phi_hits == gate_phi_hits,
            f"parent_hits={parent_phi_hits}; gate_hits={gate_phi_hits}",
        )
    )

    sample_indices = np.unique(
        np.array([0, 1, parents.size // 7, parents.size // 3, parents.size // 2, 2 * parents.size // 3, parents.size - 2, parents.size - 1])
    )
    max_parent_error = 0.0
    parent_sample_passed = True
    for index in sample_indices:
        p = int(parents[index])
        q_values = gates[gates.astype(np.int64) ** 2 <= p].astype(np.int64)
        remainders = p % q_values
        phase_a = 2.0 * remainders.astype(np.float64) / q_values.astype(np.float64)
        folded = np.minimum(remainders, q_values - remainders).astype(np.float64)
        phi_target = PHI_LEFT * q_values.astype(np.float64) / 2.0
        phi_distance = 2.0 * np.abs(folded - phi_target) / q_values.astype(np.float64)
        nearest = np.floor(phi_target + 0.5).astype(np.int64)
        nearest = np.maximum(nearest, 1)
        nearest[0] = 1
        observed = {
            "child_gate_count": float(q_values.size),
            "child_centroid": float(np.mean(phase_a)),
            "mean_ridge_distance": float(np.mean(np.abs(phase_a - 1.0))),
            "mean_phi_pair_distance": float(np.mean(phi_distance)),
            "minimum_phi_pair_distance": float(np.min(phi_distance)),
            "nearest_phi_residue_hit_count": float(np.count_nonzero(folded == nearest)),
        }
        stored = parent_rows[int(index)]
        for field, value in observed.items():
            error = abs(value - float(stored[field]))
            max_parent_error = max(max_parent_error, error)
            parent_sample_passed &= close(value, float(stored[field]))
    checks.append(
        check(
            "eight parent rows reconstruct from raw child phases",
            parent_sample_passed,
            f"sample_count={sample_indices.size}; max_abs_error={max_parent_error:.3g}",
        )
    )

    sample_gate_indices = np.unique(np.array([0, 1, 2, gates.size // 7, gates.size // 2, gates.size - 2, gates.size - 1]))
    max_gate_error = 0.0
    gate_sample_passed = True
    for index in sample_gate_indices:
        q = int(gates[index])
        eligible = parents[parents >= q * q]
        remainder = eligible % q
        phase_a = 2.0 * remainder.astype(np.float64) / q
        folded = np.minimum(remainder, q - remainder).astype(np.int64)
        target = PHI_LEFT * q / 2.0
        nearest = 1 if q == 2 else min(max(int(math.floor(target + 0.5)), 1), (q - 1) // 2)
        phi_distance = 2.0 * np.abs(folded.astype(np.float64) - target) / q
        observed = {
            "eligible_parent_count": float(eligible.size),
            "mean_phase_a": float(np.mean(phase_a)),
            "mean_ridge_distance": float(np.mean(np.abs(phase_a - 1.0))),
            "phi_observed_hits": float(np.count_nonzero(folded == nearest)),
            "phi_observed_mean_distance": float(np.mean(phi_distance)),
        }
        stored = gate_rows[int(index)]
        for field, value in observed.items():
            error = abs(value - float(stored[field]))
            max_gate_error = max(max_gate_error, error)
            gate_sample_passed &= close(value, float(stored[field]))
    checks.append(
        check(
            "seven gate rows reconstruct from raw parent residues",
            gate_sample_passed,
            f"sample_count={sample_gate_indices.size}; max_abs_error={max_gate_error:.3g}",
        )
    )

    primary_gate_rows = [row for row in gate_rows if int(row["gate_q"]) != 2]
    primary_pairs = sum(int(row["eligible_parent_count"]) for row in primary_gate_rows)
    phi_observed_hits = sum(int(row["phi_observed_hits"]) for row in primary_gate_rows)
    phi_expected_hits = sum(
        int(row["eligible_parent_count"]) * float(row["phi_expected_share"])
        for row in primary_gate_rows
    )
    phi_observed_distance_sum = sum(
        int(row["eligible_parent_count"]) * float(row["phi_observed_mean_distance"])
        for row in primary_gate_rows
    )
    phi_expected_distance_sum = sum(
        int(row["eligible_parent_count"]) * float(row["phi_expected_mean_distance"])
        for row in primary_gate_rows
    )
    stored_phi = results["landmark_comparisons_excluding_q2"]["phi"]
    aggregate_values = {
        "pairs": (float(primary_pairs), float(scope["primary_phi_child_pair_count_excluding_q2"])),
        "occupancy_lift": (
            phi_observed_hits / phi_expected_hits,
            float(stored_phi["child_pair_weighted_occupancy_lift"]),
        ),
        "distance_delta": (
            (phi_observed_distance_sum - phi_expected_distance_sum) / primary_pairs,
            float(stored_phi["child_pair_weighted_distance_delta"]),
        ),
    }
    aggregate_passed = all(close(first, second) for first, second in aggregate_values.values())
    max_aggregate_error = max(abs(first - second) for first, second in aggregate_values.values())
    checks.append(
        check(
            "Phi aggregate recomputes from gate CSV",
            aggregate_passed,
            f"max_abs_error={max_aggregate_error:.3g}",
        )
    )

    validation = {
        "validation_id": "PN37/FULL-CHILD-ARA-PHI/INDEPENDENT-VALIDATION/v1",
        "all_passed": all(bool(item["passed"]) for item in checks),
        "check_count": len(checks),
        "checks": checks,
        "note": "This validator reloads the source interval, reconstructs selected parent and gate child fields, and recomputes the primary Phi aggregate from CSV outputs.",
    }
    OUTPUT_PATH.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()

