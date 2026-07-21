"""PN22 formal test of T(A)=oddceil(7A/2+1)."""

from __future__ import annotations

import itertools
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN22_ODD_LATTICE_ARA_CANDIDATE_RESULTS.json"
MAX_A = 1_000_000
CONTROL_OFFSETS = 10
ADMISSIBLE_MOD14 = (1, 3, 5, 9, 11, 13)
TRANSFORM_MOD14 = (1, 5, 9, 13)
EXAMPLES = (27, 32, 34, 36, 28, 30, 40, 48, 52, 56)


def oddceil_transform(values: np.ndarray) -> np.ndarray:
    values = values.astype(np.int64, copy=False)
    ceiling = (7 * values + 3) // 2
    return ceiling + (ceiling % 2 == 0)


def prime_flags(limit: int) -> np.ndarray:
    flags = np.ones(limit + 1, dtype=np.bool_)
    flags[:2] = False
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            flags[value * value : limit + 1 : value] = False
    return flags


def perfect_powers(limit: int) -> list[int]:
    values: set[int] = set()
    for base in range(2, math.isqrt(limit) + 1):
        value = base * base
        while value <= limit:
            values.add(value)
            if value > limit // base:
                break
            value *= base
    return sorted(values)


def subgroup_result(name: str, inputs: list[int], flags: np.ndarray) -> dict:
    input_array = np.array(inputs, dtype=np.int64)
    candidates = oddceil_transform(input_array)
    candidate_hits = flags[candidates].astype(np.float64)
    differences = []
    control_hits = 0
    control_count = 0
    per_input_control_rates = []
    for candidate, hit in zip(candidates, candidate_hits):
        controls = []
        for step in range(1, CONTROL_OFFSETS + 1):
            for signed in (-step, step):
                control = int(candidate + 14 * signed)
                if 2 <= control < flags.size:
                    controls.append(float(flags[control]))
        control_rate = float(sum(controls) / len(controls))
        per_input_control_rates.append(control_rate)
        differences.append(float(hit - control_rate))
        control_hits += int(sum(controls))
        control_count += len(controls)
    differences_array = np.array(differences, dtype=np.float64)
    difference_mean = float(differences_array.mean())
    standard_error = float(differences_array.std(ddof=1) / math.sqrt(len(differences))) if len(differences) > 1 else None
    z_score = difference_mean / standard_error if standard_error and standard_error > 0 else None
    return {
        "name": name,
        "input_count": len(inputs),
        "candidate_prime_count": int(candidate_hits.sum()),
        "candidate_prime_rate": float(candidate_hits.mean()),
        "matched_local_control_prime_count": control_hits,
        "matched_local_control_count": control_count,
        "matched_local_control_prime_rate": control_hits / control_count,
        "mean_input_cluster_difference": difference_mean,
        "cluster_standard_error": standard_error,
        "descriptive_z_score": z_score,
        "first_examples": [
            {
                "A": int(value),
                "T_A": int(candidate),
                "candidate_is_prime": bool(hit),
                "local_control_prime_rate": float(control_rate),
            }
            for value, candidate, hit, control_rate in zip(
                input_array[:20], candidates[:20], candidate_hits[:20], per_input_control_rates[:20]
            )
        ],
    }


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN22 output already exists; refusing overwrite")
    inputs = np.arange(1, MAX_A + 1, dtype=np.int64)
    candidates = oddceil_transform(inputs)
    minimum_output = int(candidates.min())
    maximum_output = int(candidates.max())
    flags = prime_flags(maximum_output + 14 * CONTROL_OFFSETS)
    candidate_hits = flags[candidates]

    output_range = np.arange(minimum_output, maximum_output + 1, dtype=np.int64)
    odd_mask = (output_range & 1) == 1
    coprime14_mask = np.gcd(output_range, 14) == 1
    transform_lane_mask = np.isin(output_range % 14, TRANSFORM_MOD14)
    odd_values = output_range[odd_mask]
    coprime14_values = output_range[coprime14_mask]
    transform_lane_values = output_range[transform_lane_mask]

    subset_rows = []
    for subset in itertools.combinations(ADMISSIBLE_MOD14, 4):
        mask = np.isin(output_range % 14, subset)
        values = output_range[mask]
        subset_rows.append({
            "residues": list(subset),
            "candidate_count": int(values.size),
            "prime_count": int(flags[values].sum()),
            "prime_rate": float(flags[values].mean()),
            "is_transform_subset": tuple(subset) == TRANSFORM_MOD14,
        })

    perfect = perfect_powers(MAX_A)
    powers_two = []
    value = 2
    while value <= MAX_A:
        powers_two.append(value)
        value *= 2
    odd_perfect = [value for value in perfect if value % 2 == 1]
    even_perfect = [value for value in perfect if value % 2 == 0]

    example_rows = []
    for value in EXAMPLES:
        continuous_numerator = 7 * value + 2
        transformed = int(oddceil_transform(np.array([value], dtype=np.int64))[0])
        example_rows.append({
            "A": value,
            "B": 2 * value,
            "ridge_offset": value / 2.0,
            "continuous_candidate": continuous_numerator / 2.0,
            "T_A": transformed,
            "T_A_is_prime": bool(flags[transformed]),
            "A_mod_4": value % 4,
            "T_A_mod_14": transformed % 14,
        })

    candidate_rate = float(candidate_hits.mean())
    odd_rate = float(flags[odd_values].mean())
    coprime_rate = float(flags[coprime14_values].mean())
    exact_lane_rate = float(flags[transform_lane_values].mean())
    exact_set_equal = np.array_equal(candidates, transform_lane_values)
    candidate_subset_rank = 1 + sum(
        row["prime_rate"] > candidate_rate for row in subset_rows
    )
    payload = {
        "test_id": "PN22/ODD-LATTICE-ARA-CANDIDATE/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "EXACT MOD-14 WHEEL CROSSWALK — NOT PRIME-SPECIFIC",
        "formula": {
            "continuous": "C(A)=A+2A+A/2+1=7A/2+1",
            "projection": "T(A)=smallest odd integer >= C(A)",
            "piecewise": {
                "A=4k": "T=14k+1",
                "A=4k+1": "T=14k+5",
                "A=4k+2": "T=14k+9",
                "A=4k+3": "T=14k+13",
            },
            "output_residues_mod_14": list(TRANSFORM_MOD14),
        },
        "population": {
            "input_minimum": 1,
            "input_maximum": MAX_A,
            "input_count": MAX_A,
            "output_minimum": minimum_output,
            "output_maximum": maximum_output,
            "unique_candidate_count": int(np.unique(candidates).size),
        },
        "primary": {
            "candidate_prime_count": int(candidate_hits.sum()),
            "candidate_prime_rate": candidate_rate,
            "all_odd_count": int(odd_values.size),
            "all_odd_prime_rate": odd_rate,
            "candidate_lift_over_all_odds": candidate_rate / odd_rate,
            "coprime_to_14_count": int(coprime14_values.size),
            "coprime_to_14_prime_rate": coprime_rate,
            "candidate_lift_over_coprime_to_14": candidate_rate / coprime_rate,
            "exact_transform_lane_count": int(transform_lane_values.size),
            "exact_transform_lane_prime_rate": exact_lane_rate,
            "candidate_lift_over_exact_lane": candidate_rate / exact_lane_rate,
            "candidate_set_equals_exact_transform_lane": bool(exact_set_equal),
            "candidate_subset_rank_among_15_four_of_six_admissible_subsets": candidate_subset_rank,
        },
        "admissible_four_residue_controls": subset_rows,
        "examples": example_rows,
        "subgroups": {
            "all_unique_perfect_powers": subgroup_result("all_unique_perfect_powers", perfect, flags),
            "odd_perfect_powers": subgroup_result("odd_perfect_powers", odd_perfect, flags),
            "even_perfect_powers": subgroup_result("even_perfect_powers", even_perfect, flags),
            "powers_of_two": subgroup_result("powers_of_two", powers_two, flags),
        },
        "decision": {
            "prime_enrichment_over_raw_odds": candidate_rate > odd_rate,
            "prime_enrichment_over_exact_residue_matched_control": candidate_rate > exact_lane_rate,
            "wheel_crosswalk": bool(exact_set_equal and candidate_rate == exact_lane_rate),
            "blind_target_authorized": False,
            "reason": (
                "T(A) exactly enumerates four fixed prime-admissible residues modulo 14. "
                "Any raw-odd lift is wheel filtering; there is no enrichment over the exact matched lane."
            ),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "primary": payload["primary"],
        "examples": payload["examples"],
        "perfect_powers": payload["subgroups"]["all_unique_perfect_powers"],
        "powers_of_two": payload["subgroups"]["powers_of_two"],
    }, indent=2))


if __name__ == "__main__":
    main()
