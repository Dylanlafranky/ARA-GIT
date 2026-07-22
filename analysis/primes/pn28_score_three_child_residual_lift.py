"""Score frozen PN28 residual-corrected candidates against their PN27 bases."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PREDICTIONS = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_FROZEN_PREDICTIONS.csv"
TARGET_MANIFEST = HERE / "PN28_TARGET_FREEZE_MANIFEST.json"
VALIDATED_ROWS = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_VALIDATED_ROWS.csv"
GROUPS = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_GROUPS.csv"
RESULTS = HERE / "PN28_THREE_CHILD_RESIDUAL_LIFT_RESULTS.json"

PERMUTATIONS = 10_000
PERMUTATION_SEED = 28200


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def is_prime(number: int) -> bool:
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def paired_summary(rows: list[dict]) -> dict:
    corrected = [row["corrected_is_prime"] for row in rows]
    base = [row["base_is_prime"] for row in rows]
    differences = [new - old for new, old in zip(corrected, base)]
    average = statistics.fmean(differences)
    standard_error = statistics.stdev(differences) / math.sqrt(len(differences))
    gained = sum(new == 1 and old == 0 for new, old in zip(corrected, base))
    lost = sum(new == 0 and old == 1 for new, old in zip(corrected, base))
    both = sum(new == 1 and old == 1 for new, old in zip(corrected, base))
    neither = len(rows) - gained - lost - both
    return {
        "n": len(rows),
        "base_hits": sum(base),
        "base_hit_rate": statistics.fmean(base),
        "corrected_hits": sum(corrected),
        "corrected_hit_rate": statistics.fmean(corrected),
        "difference": average,
        "difference_95ci_normal": [
            average - 1.96 * standard_error,
            average + 1.96 * standard_error,
        ],
        "gained_hits": gained,
        "lost_hits": lost,
        "both_prime": both,
        "neither_prime": neither,
        "candidate_changed_rate": statistics.fmean(row["integer_adjustment"] != 0 for row in rows),
        "corrected_candidate_odd_rate": statistics.fmean(row["corrected_candidate"] % 2 == 1 for row in rows),
    }


def permutation_test(odd_rows: list[dict], prime_label) -> dict:
    scales = sorted(set(row["scale"] for row in odd_rows))
    adjustments = sorted(set(row["integer_adjustment"] for row in odd_rows))
    adjustment_index = {value: index for index, value in enumerate(adjustments)}
    outcome_matrix = np.asarray([
        [prime_label(row["base_candidate"] + adjustment) for adjustment in adjustments]
        for row in odd_rows
    ], dtype=np.int8)
    actual_indices = np.asarray([adjustment_index[row["integer_adjustment"]] for row in odd_rows], dtype=np.int8)
    row_indices = np.arange(len(odd_rows))
    scale_indices = {
        scale: np.asarray([index for index, row in enumerate(odd_rows) if row["scale"] == scale])
        for scale in scales
    }
    observed = float(outcome_matrix[row_indices, actual_indices].mean())
    observed_by_scale = {
        scale: float(outcome_matrix[indices, actual_indices[indices]].mean())
        for scale, indices in scale_indices.items()
    }
    rng = np.random.default_rng(PERMUTATION_SEED)
    permuted_indices = actual_indices.copy()
    at_or_above = 0
    at_or_above_scale = {scale: 0 for scale in scales}
    null_sum = 0.0
    null_sumsq = 0.0
    for _ in range(PERMUTATIONS):
        for scale, indices in scale_indices.items():
            permuted_indices[indices] = rng.permutation(actual_indices[indices])
        outcomes = outcome_matrix[row_indices, permuted_indices]
        pooled_rate = float(outcomes.mean())
        null_sum += pooled_rate
        null_sumsq += pooled_rate * pooled_rate
        at_or_above += pooled_rate >= observed
        for scale, indices in scale_indices.items():
            scale_rate = float(outcomes[indices].mean())
            at_or_above_scale[scale] += scale_rate >= observed_by_scale[scale]
    null_mean = null_sum / PERMUTATIONS
    null_variance = max(0.0, null_sumsq / PERMUTATIONS - null_mean * null_mean)
    return {
        "adjustments": adjustments,
        "permutations": PERMUTATIONS,
        "seed": PERMUTATION_SEED,
        "observed_corrected_rate": observed,
        "relation_broken_mean_rate": null_mean,
        "relation_broken_sd_rate": math.sqrt(null_variance),
        "one_sided_p_pooled": (at_or_above + 1) / (PERMUTATIONS + 1),
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
    if sha256(PREDICTIONS) != manifest["prediction_file_sha256"]:
        raise RuntimeError("frozen prediction hash mismatch")
    source_rows = read_csv(PREDICTIONS)

    prime_cache: dict[int, int] = {}

    def prime_label(value: int) -> int:
        if value not in prime_cache:
            prime_cache[value] = int(is_prime(value))
        return prime_cache[value]

    rows: list[dict] = []
    for source in source_rows:
        row = {
            **source,
            "anchor": int(source["anchor"]),
            "phase_a": int(source["phase_a"]),
            "phase_b": int(source["phase_b"]),
            "base_offset": int(source["base_offset"]),
            "base_candidate": int(source["base_candidate"]),
            "integer_adjustment": int(source["integer_adjustment"]),
            "corrected_offset": int(source["corrected_offset"]),
            "corrected_candidate": int(source["corrected_candidate"]),
        }
        row["base_is_prime"] = prime_label(row["base_candidate"])
        row["corrected_is_prime"] = prime_label(row["corrected_candidate"])
        rows.append(row)

    odd_rows = [row for row in rows if row["parity"] == "odd"]
    even_rows = [row for row in rows if row["parity"] == "even"]
    all_summary = paired_summary(rows)
    odd_summary = paired_summary(odd_rows)
    even_summary = paired_summary(even_rows)
    by_scale = {
        scale: paired_summary([row for row in odd_rows if row["scale"] == scale])
        for scale in sorted(set(row["scale"] for row in odd_rows))
    }

    groups = []
    for dimension, values in (
        ("integer_adjustment", sorted(set(row["integer_adjustment"] for row in odd_rows))),
        ("phase_a", sorted(set(row["phase_a"] for row in odd_rows), reverse=True)),
    ):
        for value in values:
            group = [row for row in odd_rows if row[dimension] == value]
            summary = paired_summary(group)
            groups.append({"dimension": dimension, "value": value, **summary})

    permutation = permutation_test(odd_rows, prime_label)
    positive_all_scales = all(summary["difference"] > 0 for summary in by_scale.values())
    if (
        odd_summary["difference"] > 0
        and permutation["one_sided_p_pooled"] < 0.01
        and positive_all_scales
    ):
        status = "STRONG CORRECTIVE SUPPORT"
    elif odd_summary["difference"] > 0:
        status = "PARTIAL CORRECTIVE SUPPORT"
    elif odd_summary["difference"] == 0:
        status = "NULL"
    else:
        status = "NEGATIVE RESULT"

    write_csv(VALIDATED_ROWS, rows)
    write_csv(GROUPS, groups)
    payload = {
        "test_id": "PN28/THREE-CHILD-RESIDUAL-LIFT/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "protocol": "PN28_THREE_CHILD_RESIDUAL_LIFT_PROTOCOL_v1_FROZEN.md",
        "frozen_prediction_sha256": sha256(PREDICTIONS),
        "population": {
            "all_rows": len(rows),
            "odd_primary_rows": len(odd_rows),
            "even_secondary_rows": len(even_rows),
            "protected_87_bit_anchor_used": False,
        },
        "worked_example_35": {
            "base_candidate": 59,
            "integer_adjustment": 0,
            "corrected_candidate": 59,
            "is_prime": is_prime(59),
        },
        "odd_primary": odd_summary,
        "even_secondary": even_summary,
        "all_balanced": all_summary,
        "odd_by_scale": by_scale,
        "odd_group_results": groups,
        "relation_broken_permutation": permutation,
        "decision": {
            "status": status,
            "corrected_beats_base_on_odd_anchors": odd_summary["difference"] > 0,
            "positive_at_all_three_scales": positive_all_scales,
            "permutation_p_below_0_01": permutation["one_sided_p_pooled"] < 0.01,
            "general_prime_formula_supported": False,
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "odd_primary": odd_summary,
        "even_secondary": even_summary,
        "by_scale": by_scale,
        "permutation": permutation,
    }, indent=2))


if __name__ == "__main__":
    main()
