"""Score frozen PN31 independent-wave coordinates after direct label reveal."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
COORDINATES = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_FROZEN_COORDINATES.csv"
FREEZE = HERE / "PN31_COORDINATE_FREEZE_MANIFEST.json"
SCORED = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_SCORED.csv"
RESULTS = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_RESULTS.json"
WAVES = (3, 5, 9, 11, 13)
COMPONENT_SEEDS = {3: 31103, 5: 31105, 9: 31109, 11: 31111, 13: 31113}
PERMUTATIONS = 10_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def is_prime_trial(number: int) -> bool:
    if number < 2:
        return False
    if number % 2 == 0:
        return number == 2
    divisor = 3
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 2
    return True


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def auc_lower(positive: list[float], negative: list[float]) -> float:
    score = sum(
        1.0 if pos < neg else 0.5 if pos == neg else 0.0
        for pos in positive for neg in negative
    )
    return score / (len(positive) * len(negative))


def numeric_permutation(
    positive: list[float], negative: list[float], seed: int, alternative: str = "lower"
) -> dict:
    combined = positive + negative
    positive_n = len(positive)
    observed_signed = statistics.fmean(negative) - statistics.fmean(positive)
    observed = abs(observed_signed) if alternative == "two-sided" else observed_signed
    rng = random.Random(seed)
    indices = list(range(len(combined)))
    at_or_above = 0
    null_sum = 0.0
    for _ in range(PERMUTATIONS):
        chosen = set(rng.sample(indices, positive_n))
        perm_positive = [value for index, value in enumerate(combined) if index in chosen]
        perm_negative = [value for index, value in enumerate(combined) if index not in chosen]
        signed = statistics.fmean(perm_negative) - statistics.fmean(perm_positive)
        statistic = abs(signed) if alternative == "two-sided" else signed
        null_sum += statistic
        at_or_above += statistic >= observed
    return {
        "alternative": alternative,
        "observed_composite_minus_prime": observed_signed,
        "test_statistic": observed,
        "permutations": PERMUTATIONS,
        "seed": seed,
        "null_mean_test_statistic": null_sum / PERMUTATIONS,
        "p_value": (at_or_above + 1) / (PERMUTATIONS + 1),
    }


def total_variation(positive: list[str], negative: list[str]) -> float:
    positive_counts = Counter(positive)
    negative_counts = Counter(negative)
    categories = set(positive_counts) | set(negative_counts)
    return 0.5 * sum(
        abs(positive_counts[item] / len(positive) - negative_counts[item] / len(negative))
        for item in categories
    )


def categorical_permutation(positive: list[str], negative: list[str], seed: int) -> dict:
    combined = positive + negative
    positive_n = len(positive)
    observed = total_variation(positive, negative)
    rng = random.Random(seed)
    indices = list(range(len(combined)))
    at_or_above = 0
    null_sum = 0.0
    for _ in range(PERMUTATIONS):
        chosen = set(rng.sample(indices, positive_n))
        perm_positive = [value for index, value in enumerate(combined) if index in chosen]
        perm_negative = [value for index, value in enumerate(combined) if index not in chosen]
        statistic = total_variation(perm_positive, perm_negative)
        null_sum += statistic
        at_or_above += statistic >= observed
    return {
        "statistic": "total_variation_distance",
        "observed": observed,
        "permutations": PERMUTATIONS,
        "seed": seed,
        "null_mean": null_sum / PERMUTATIONS,
        "p_value": (at_or_above + 1) / (PERMUTATIONS + 1),
        "prime_counts": dict(Counter(positive)),
        "composite_counts": dict(Counter(negative)),
    }


def distance_summary(primes: list[dict], composites: list[dict], field: str) -> dict:
    prime_values = [row[field] for row in primes]
    composite_values = [row[field] for row in composites]
    return {
        "prime_n": len(primes),
        "composite_n": len(composites),
        "prime_mean": statistics.fmean(prime_values),
        "composite_mean": statistics.fmean(composite_values),
        "prime_median": statistics.median(prime_values),
        "composite_median": statistics.median(composite_values),
        "auc_prime_lower": auc_lower(prime_values, composite_values),
    }


def holm_adjust(p_values: dict[int, float]) -> dict[int, float]:
    ordered = sorted(p_values, key=p_values.get)
    adjusted = {}
    running = 0.0
    m = len(ordered)
    for rank, wave in enumerate(ordered):
        candidate = min(1.0, (m - rank) * p_values[wave])
        running = max(running, candidate)
        adjusted[wave] = running
    return adjusted


def main() -> None:
    for output in (SCORED, RESULTS):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if sha256(COORDINATES) != freeze["coordinate_file_sha256"]:
        raise RuntimeError("coordinate freeze hash mismatch")

    rows = []
    for source in read_csv(COORDINATES):
        number = int(source["number"])
        parsed = {
            **source,
            "number": number,
            "phase_a_distance": float(source["phase_a_distance_decimal"]),
            "approaching_count_value": int(source["approaching_count"]),
            "unresolved_by_five_children": int(source["unresolved_by_five_children"]),
            "is_prime": int(is_prime_trial(number)),
        }
        for wave in WAVES:
            parsed[f"handover_distance_{wave}"] = float(source[f"handover_distance_{wave}_decimal"])
        rows.append(parsed)

    primes = [row for row in rows if row["is_prime"]]
    composites = [row for row in rows if not row["is_prime"]]
    unresolved = [row for row in composites if row["unresolved_by_five_children"]]

    phase_a_hard = distance_summary(primes, unresolved, "phase_a_distance")
    phase_a_hard["permutation"] = numeric_permutation(
        [row["phase_a_distance"] for row in primes],
        [row["phase_a_distance"] for row in unresolved],
        31001,
    )
    phase_a_all = distance_summary(primes, composites, "phase_a_distance")

    phase_a_identity = categorical_permutation(
        [row["phase_a_waves"] for row in primes],
        [row["phase_a_waves"] for row in unresolved],
        31002,
    )
    full_order = categorical_permutation(
        [row["five_wave_order"] for row in primes],
        [row["five_wave_order"] for row in unresolved],
        31003,
    )
    approaching = distance_summary(primes, unresolved, "approaching_count_value")
    approaching["permutation"] = numeric_permutation(
        [row["approaching_count_value"] for row in primes],
        [row["approaching_count_value"] for row in unresolved],
        31004,
        alternative="two-sided",
    )

    components = {}
    raw_component_p = {}
    for wave in WAVES:
        field = f"handover_distance_{wave}"
        summary = distance_summary(primes, unresolved, field)
        summary["permutation"] = numeric_permutation(
            [row[field] for row in primes],
            [row[field] for row in unresolved],
            COMPONENT_SEEDS[wave],
        )
        raw_component_p[wave] = summary["permutation"]["p_value"]
        components[str(wave)] = summary
    adjusted = holm_adjust(raw_component_p)
    for wave in WAVES:
        components[str(wave)]["holm_adjusted_p"] = adjusted[wave]

    distance_p = phase_a_hard["permutation"]["p_value"]
    identity_p = phase_a_identity["p_value"]
    order_p = full_order["p_value"]
    approaching_p = approaching["permutation"]["p_value"]
    if (
        phase_a_hard["auc_prime_lower"] > 0.60
        and distance_p < 0.01
        and (identity_p < 0.01 or order_p < 0.01)
    ):
        status = "FIVE-WAVE PHASE A SUPPORT"
    elif identity_p < 0.01 or order_p < 0.01:
        status = "ORDERED CHILD STRUCTURE ONLY"
    elif min(distance_p, identity_p, order_p, approaching_p) < 0.05:
        status = "SUGGESTIVE"
    elif (
        phase_a_hard["prime_mean"] > phase_a_hard["composite_mean"]
        and distance_p > 0.99
    ):
        status = "OPPOSITE DIRECTION"
    else:
        status = "NULL"

    write_csv(SCORED, rows)
    payload = {
        "test_id": "PN31/FIVE-INDEPENDENT-HANDOVER/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "population": {
            "n": len(rows),
            "prime_n": len(primes),
            "odd_composite_n": len(composites),
            "unresolved_composite_n": len(unresolved),
            "range": "odd integers 2001 through 2999 inclusive",
            "waves": list(WAVES),
            "wave_1_included": False,
            "fixed_pairs_used": False,
            "sieve_used": False,
            "label_method": "direct trial division after coordinate freeze",
        },
        "primary_prime_vs_unresolved": {
            "phase_a_distance": phase_a_hard,
            "phase_a_identity": phase_a_identity,
            "five_wave_order": full_order,
            "approaching_count": approaching,
            "individual_waves": components,
        },
        "secondary_prime_vs_all_composites": {
            "phase_a_distance": phase_a_all,
        },
        "decision": {
            "status": status,
            "parent_collapse_tested": False,
            "prime_generator_tested": False,
            "prime_certification_tested": False,
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
