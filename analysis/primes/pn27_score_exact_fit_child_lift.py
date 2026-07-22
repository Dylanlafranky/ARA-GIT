"""Attach blind primality outcomes to the frozen PN27 predictions."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PREDICTIONS = HERE / "PN27_EXACT_FIT_CHILD_LIFT_FROZEN_PREDICTIONS.csv"
TARGET_MANIFEST = HERE / "PN27_TARGET_FREEZE_MANIFEST.json"
VALIDATED_ROWS = HERE / "PN27_EXACT_FIT_CHILD_LIFT_VALIDATED_ROWS.csv"
GROUPS = HERE / "PN27_EXACT_FIT_CHILD_LIFT_GROUPS.csv"
RESULTS = HERE / "PN27_EXACT_FIT_CHILD_LIFT_RESULTS.json"

OFFSETS = (16, 18, 20, 24, 26, 28)
PERMUTATIONS = 10_000
PERMUTATION_SEED = 27200


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def is_prime(number: int) -> bool:
    """Deterministic Miller-Rabin for the unsigned 64-bit range."""
    if number < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small_primes:
        if number % prime == 0:
            return number == prime
    odd_part = number - 1
    powers_of_two = 0
    while odd_part % 2 == 0:
        powers_of_two += 1
        odd_part //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % number == 0:
            continue
        value = pow(base, odd_part, number)
        if value in (1, number - 1):
            continue
        for _ in range(powers_of_two - 1):
            value = pow(value, 2, number)
            if value == number - 1:
                break
        else:
            return False
    return True


def read_predictions() -> list[dict]:
    with PREDICTIONS.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean(values) -> float:
    return statistics.fmean(values)


def difference_summary(rows: list[dict]) -> dict:
    ara = [row["is_prime"] for row in rows]
    uniform = [row["uniform_offset_prime_rate"] for row in rows]
    fixed = [row["fixed_plus_2_is_prime"] for row in rows]
    differences = [a - u for a, u in zip(ara, uniform)]
    average = mean(differences)
    standard_error = statistics.stdev(differences) / math.sqrt(len(differences))
    return {
        "n": len(rows),
        "ara_hit_rate": mean(ara),
        "uniform_allowed_offset_rate": mean(uniform),
        "difference_vs_uniform": average,
        "difference_vs_uniform_95ci_normal": [
            average - 1.96 * standard_error,
            average + 1.96 * standard_error,
        ],
        "fixed_plus_2_rate": mean(fixed),
        "difference_vs_fixed_plus_2": mean(a - f for a, f in zip(ara, fixed)),
    }


def permutation_test(rows: list[dict]) -> dict:
    scales = sorted(set(row["scale"] for row in rows))
    outcome_matrix = np.asarray(
        [[int(value) for value in row["allowed_offset_outcomes"].split("|")] for row in rows],
        dtype=np.int8,
    )
    actual_indices = np.asarray([OFFSETS.index(row["offset"]) for row in rows], dtype=np.int8)
    row_indices = np.arange(len(rows))
    scale_indices = {
        scale: np.asarray([index for index, row in enumerate(rows) if row["scale"] == scale])
        for scale in scales
    }
    observed_rate = float(outcome_matrix[row_indices, actual_indices].mean())
    observed_by_scale = {
        scale: float(
            outcome_matrix[indices, actual_indices[indices]].mean()
        )
        for scale, indices in scale_indices.items()
    }
    rng = np.random.default_rng(PERMUTATION_SEED)
    at_or_above_pooled = 0
    at_or_above_scale = {scale: 0 for scale in scales}
    null_sum = 0.0
    null_sumsq = 0.0
    permuted_indices = actual_indices.copy()
    for _ in range(PERMUTATIONS):
        for scale, indices in scale_indices.items():
            permuted_indices[indices] = rng.permutation(actual_indices[indices])
        outcomes = outcome_matrix[row_indices, permuted_indices]
        pooled_rate = float(outcomes.mean())
        null_sum += pooled_rate
        null_sumsq += pooled_rate * pooled_rate
        at_or_above_pooled += pooled_rate >= observed_rate
        for scale, indices in scale_indices.items():
            scale_rate = float(outcomes[indices].mean())
            at_or_above_scale[scale] += scale_rate >= observed_by_scale[scale]
    null_mean = null_sum / PERMUTATIONS
    null_variance = max(0.0, null_sumsq / PERMUTATIONS - null_mean * null_mean)
    return {
        "permutations": PERMUTATIONS,
        "seed": PERMUTATION_SEED,
        "alternative": "ARA hit rate greater than relation-broken offset assignment",
        "observed_ara_rate": observed_rate,
        "null_mean_rate": null_mean,
        "null_sd_rate": math.sqrt(null_variance),
        "one_sided_p_pooled": (at_or_above_pooled + 1) / (PERMUTATIONS + 1),
        "observed_by_scale": observed_by_scale,
        "one_sided_p_by_scale": {
            scale: (count + 1) / (PERMUTATIONS + 1)
            for scale, count in at_or_above_scale.items()
        },
    }


def main() -> None:
    for output in (VALIDATED_ROWS, GROUPS, RESULTS):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    manifest = json.loads(TARGET_MANIFEST.read_text(encoding="utf-8"))
    actual_hash = sha256(PREDICTIONS)
    if actual_hash != manifest["prediction_file_sha256"]:
        raise RuntimeError("frozen prediction hash mismatch")
    source_rows = read_predictions()
    if len(source_rows) != manifest["row_count"]:
        raise RuntimeError("frozen prediction row-count mismatch")

    validated: list[dict] = []
    prime_cache: dict[int, int] = {}

    def prime_label(value: int) -> int:
        if value not in prime_cache:
            prime_cache[value] = int(is_prime(value))
        return prime_cache[value]

    for source in source_rows:
        anchor = int(source["anchor"])
        predicted = int(source["predicted_candidate"])
        allowed_outcomes = [prime_label(anchor + offset) for offset in OFFSETS]
        validated.append({
            **source,
            "anchor": anchor,
            "phase_a": int(source["phase_a"]),
            "phase_b": int(source["phase_b"]),
            "child_identity": int(source["child_identity"]),
            "upper_reference": int(source["upper_reference"]),
            "crossing_step": int(source["crossing_step"]),
            "offset": int(source["offset"]),
            "predicted_candidate": predicted,
            "is_prime": prime_label(predicted),
            "fixed_plus_2_candidate": anchor + 2,
            "fixed_plus_2_is_prime": prime_label(anchor + 2),
            "allowed_offset_prime_count": sum(allowed_outcomes),
            "uniform_offset_prime_rate": sum(allowed_outcomes) / len(OFFSETS),
            "allowed_offset_outcomes": "|".join(map(str, allowed_outcomes)),
        })

    odd_rows = [row for row in validated if row["parity"] == "odd"]
    even_rows = [row for row in validated if row["parity"] == "even"]
    overall = difference_summary(odd_rows)
    by_scale = {
        scale: difference_summary([row for row in odd_rows if row["scale"] == scale])
        for scale in sorted(set(row["scale"] for row in odd_rows))
    }

    groups = []
    for scale in sorted(set(row["scale"] for row in odd_rows)) + ["pooled"]:
        scale_rows = odd_rows if scale == "pooled" else [row for row in odd_rows if row["scale"] == scale]
        for phase_a in sorted(set(row["phase_a"] for row in scale_rows), reverse=True):
            group = [row for row in scale_rows if row["phase_a"] == phase_a]
            groups.append({
                "scale": scale,
                "phase_a": phase_a,
                "phase_b": 14 - phase_a,
                "offset": 29 - phase_a,
                "n": len(group),
                "share_of_scale": len(group) / len(scale_rows),
                "prime_hits": sum(row["is_prime"] for row in group),
                "prime_hit_rate": mean(row["is_prime"] for row in group),
                "uniform_offset_prime_rate": mean(row["uniform_offset_prime_rate"] for row in group),
                "difference_vs_uniform": mean(
                    row["is_prime"] - row["uniform_offset_prime_rate"] for row in group
                ),
                "fixed_plus_2_rate": mean(row["fixed_plus_2_is_prime"] for row in group),
            })

    permutation = permutation_test(odd_rows)
    positive_all_scales = all(
        summary["difference_vs_uniform"] > 0 for summary in by_scale.values()
    )
    if (
        overall["difference_vs_uniform"] > 0
        and overall["difference_vs_fixed_plus_2"] > 0
        and permutation["one_sided_p_pooled"] < 0.01
        and positive_all_scales
    ):
        status = "STRONG PREDICTIVE SUPPORT"
    elif overall["difference_vs_uniform"] > 0:
        status = "PARTIAL PREDICTIVE SUPPORT"
    elif overall["difference_vs_uniform"] < -0.002:
        status = "NEGATIVE RESULT"
    else:
        status = "NULL"

    write_csv(VALIDATED_ROWS, validated)
    write_csv(GROUPS, groups)
    payload = {
        "test_id": "PN27/EXACT-FIT-CHILD-LIFT/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "protocol": "PN27_EXACT_FIT_CHILD_LIFT_PROTOCOL_v1_FROZEN.md",
        "frozen_prediction_file": PREDICTIONS.name,
        "frozen_prediction_sha256": actual_hash,
        "population": {
            "all_rows": len(validated),
            "odd_primary_rows": len(odd_rows),
            "even_control_rows": len(even_rows),
            "scales": sorted(set(row["scale"] for row in odd_rows)),
            "protected_87_bit_anchor_used": False,
        },
        "worked_example_35": {
            "prediction": 59,
            "is_prime": is_prime(59),
        },
        "odd_primary": overall,
        "by_scale": by_scale,
        "by_child_pair": groups,
        "offset_permutation_control": permutation,
        "even_negative_control": {
            "n": len(even_rows),
            "prime_hits": sum(row["is_prime"] for row in even_rows),
            "prime_hit_rate": mean(row["is_prime"] for row in even_rows),
            "all_candidates_even": all(row["predicted_candidate"] % 2 == 0 for row in even_rows),
        },
        "decision": {
            "status": status,
            "positive_vs_uniform_all_scales": positive_all_scales,
            "beats_uniform_offset_control": overall["difference_vs_uniform"] > 0,
            "beats_fixed_plus_2": overall["difference_vs_fixed_plus_2"] > 0,
            "permutation_p_below_0_01": permutation["one_sided_p_pooled"] < 0.01,
            "exact_one_shot_prime_algorithm_established": False,
            "interpretation": (
                "This scores the frozen N+a+2b+1 rule exactly once per anchor. "
                "Any advantage may reflect finite small-divisor residue selection and must not be described as "
                "a general prime formula without stronger untouched replication and algorithmic comparison."
            ),
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "odd_primary": overall,
        "by_scale": by_scale,
        "permutation": permutation,
        "even_control": payload["even_negative_control"],
    }, indent=2))


if __name__ == "__main__":
    main()
