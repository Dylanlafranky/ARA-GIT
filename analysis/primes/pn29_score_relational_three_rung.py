"""Attach direct-trial-division labels to frozen PN29 ARA coordinates."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
COORDINATES = HERE / "PN29_RELATIONAL_THREE_RUNG_FROZEN_COORDINATES.csv"
FREEZE = HERE / "PN29_COORDINATE_FREEZE_MANIFEST.json"
SCORED = HERE / "PN29_RELATIONAL_THREE_RUNG_SCORED.csv"
RESULTS = HERE / "PN29_RELATIONAL_THREE_RUNG_RESULTS.json"
PERMUTATIONS = 10_000
PERMUTATION_SEED = 29200


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


def auc_lower_is_positive(positive: list[float], negative: list[float]) -> float:
    wins = 0.0
    for pos in positive:
        for neg in negative:
            if pos < neg:
                wins += 1.0
            elif pos == neg:
                wins += 0.5
    return wins / (len(positive) * len(negative))


def permutation_test(distances: list[float], labels: list[int], seed: int) -> dict:
    prime_count = sum(labels)
    observed_prime = [distance for distance, label in zip(distances, labels) if label]
    observed_composite = [distance for distance, label in zip(distances, labels) if not label]
    observed = statistics.fmean(observed_composite) - statistics.fmean(observed_prime)
    rng = random.Random(seed)
    indices = list(range(len(distances)))
    at_or_above = 0
    null_sum = 0.0
    for _ in range(PERMUTATIONS):
        prime_indices = set(rng.sample(indices, prime_count))
        prime_values = [distance for index, distance in enumerate(distances) if index in prime_indices]
        composite_values = [distance for index, distance in enumerate(distances) if index not in prime_indices]
        statistic = statistics.fmean(composite_values) - statistics.fmean(prime_values)
        null_sum += statistic
        at_or_above += statistic >= observed
    return {
        "statistic": "mean_composite_distance_minus_mean_prime_distance",
        "alternative": "prime distance is lower",
        "observed": observed,
        "permutations": PERMUTATIONS,
        "seed": seed,
        "null_mean": null_sum / PERMUTATIONS,
        "one_sided_p": (at_or_above + 1) / (PERMUTATIONS + 1),
    }


def comparison(primes: list[dict], composites: list[dict], seed: int) -> dict:
    prime_d = [row["ridge_distance_2"] for row in primes]
    composite_d = [row["ridge_distance_2"] for row in composites]
    combined = primes + composites
    return {
        "prime_n": len(primes),
        "composite_n": len(composites),
        "prime_mean_distance": statistics.fmean(prime_d),
        "composite_mean_distance": statistics.fmean(composite_d),
        "prime_median_distance": statistics.median(prime_d),
        "composite_median_distance": statistics.median(composite_d),
        "auc_prime_more_ridge_close": auc_lower_is_positive(prime_d, composite_d),
        "permutation": permutation_test(
            [row["ridge_distance_2"] for row in combined],
            [row["is_prime"] for row in combined],
            seed,
        ),
    }


def main() -> None:
    for output in (SCORED, RESULTS):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if sha256(COORDINATES) != freeze["coordinate_file_sha256"]:
        raise RuntimeError("coordinate freeze hash mismatch")
    source_rows = read_csv(COORDINATES)
    rows = []
    for source in source_rows:
        number = int(source["number"])
        rows.append({
            **source,
            "number": number,
            "ridge_distance_2": float(source["ridge_distance_2_decimal"]),
            "unresolved_by_declared_children": int(source["unresolved_by_declared_children"]),
            "is_prime": int(is_prime_trial(number)),
        })

    primes = [row for row in rows if row["is_prime"]]
    composites = [row for row in rows if not row["is_prime"]]
    unresolved_composites = [
        row for row in composites if row["unresolved_by_declared_children"]
    ]
    overall = comparison(primes, composites, PERMUTATION_SEED)
    unresolved = comparison(primes, unresolved_composites, PERMUTATION_SEED + 1)

    if (
        overall["auc_prime_more_ridge_close"] > 0.60
        and unresolved["auc_prime_more_ridge_close"] > 0.60
        and overall["permutation"]["one_sided_p"] < 0.01
        and unresolved["permutation"]["one_sided_p"] < 0.01
    ):
        status = "STRONG RIDGE SUPPORT"
    elif (
        overall["prime_mean_distance"] < overall["composite_mean_distance"]
        and overall["permutation"]["one_sided_p"] < 0.01
    ):
        status = "PARTIAL / CHILD-FILTER SUPPORT"
    elif (
        overall["prime_mean_distance"] > overall["composite_mean_distance"]
        and overall["permutation"]["one_sided_p"] > 0.99
    ):
        status = "OPPOSITE DIRECTION"
    else:
        status = "NULL"

    write_csv(SCORED, rows)
    payload = {
        "test_id": "PN29/RELATIONAL-THREE-RUNG-RIDGE/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "population": {
            "n": len(rows),
            "prime_n": len(primes),
            "odd_composite_n": len(composites),
            "unresolved_composite_n": len(unresolved_composites),
            "range": "odd integers 15 through 999 inclusive",
            "sieve_used": False,
            "label_method": "direct trial division after coordinate freeze",
        },
        "worked_example_35": next(row for row in rows if row["number"] == 35),
        "overall_prime_vs_odd_composite": overall,
        "prime_vs_unresolved_composite": unresolved,
        "rung_transport": {
            "rule": "epsilon_1=epsilon_0/2; epsilon_2=epsilon_0/4",
            "ordering_changed": False,
            "interpretation": "Upward transport changes scale but cannot add classification information because D2=D0/4.",
        },
        "decision": {
            "status": status,
            "prime_ridge_supported_beyond_declared_child_filter": (
                unresolved["auc_prime_more_ridge_close"] > 0.60
                and unresolved["permutation"]["one_sided_p"] < 0.01
            ),
            "next_prime_generator_tested": False,
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
