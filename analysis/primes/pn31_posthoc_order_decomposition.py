"""Decompose PN31's frozen full-order result after label reveal."""

from __future__ import annotations

import csv
import itertools
import json
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCORED = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_SCORED.csv"
OUTPUT = HERE / "PN31_FIVE_INDEPENDENT_HANDOVER_POSTHOC.json"
WAVES = (3, 5, 9, 11, 13)
PERMUTATIONS = 10_000


def read_rows() -> list[dict[str, str]]:
    with SCORED.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def distance(row: dict[str, str], wave: int) -> float:
    return float(row[f"handover_distance_{wave}_decimal"])


def before_score(row: dict[str, str], left: int, right: int) -> float:
    left_distance = distance(row, left)
    right_distance = distance(row, right)
    return 1.0 if left_distance < right_distance else 0.5 if left_distance == right_distance else 0.0


def rank(row: dict[str, str], wave: int) -> float:
    own = distance(row, wave)
    lower = sum(distance(row, other) < own for other in WAVES if other != wave)
    ties = sum(distance(row, other) == own for other in WAVES if other != wave)
    return 1 + lower + ties / 2


def permutation_difference(prime: list[float], composite: list[float], seed: int) -> dict:
    combined = prime + composite
    prime_n = len(prime)
    observed = statistics.fmean(prime) - statistics.fmean(composite)
    rng = random.Random(seed)
    indices = list(range(len(combined)))
    at_or_above = 0
    for _ in range(PERMUTATIONS):
        selected = set(rng.sample(indices, prime_n))
        p = [value for index, value in enumerate(combined) if index in selected]
        c = [value for index, value in enumerate(combined) if index not in selected]
        at_or_above += abs(statistics.fmean(p) - statistics.fmean(c)) >= abs(observed)
    return {
        "prime_mean_minus_composite_mean": observed,
        "permutations": PERMUTATIONS,
        "seed": seed,
        "two_sided_p": (at_or_above + 1) / (PERMUTATIONS + 1),
    }


def holm(p_values: dict[str, float]) -> dict[str, float]:
    ordered = sorted(p_values, key=p_values.get)
    adjusted = {}
    running = 0.0
    count = len(ordered)
    for index, key in enumerate(ordered):
        candidate = min(1.0, (count - index) * p_values[key])
        running = max(running, candidate)
        adjusted[key] = running
    return adjusted


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    rows = read_rows()
    primes = [row for row in rows if int(row["is_prime"])]
    unresolved = [
        row for row in rows
        if not int(row["is_prime"]) and int(row["unresolved_by_five_children"])
    ]

    pairwise = {}
    raw_p = {}
    for index, (left, right) in enumerate(itertools.combinations(WAVES, 2)):
        key = f"{left}_before_{right}"
        prime_values = [before_score(row, left, right) for row in primes]
        composite_values = [before_score(row, left, right) for row in unresolved]
        test = permutation_difference(prime_values, composite_values, 31200 + index)
        raw_p[key] = test["two_sided_p"]
        pairwise[key] = {
            "prime_probability": statistics.fmean(prime_values),
            "unresolved_composite_probability": statistics.fmean(composite_values),
            **test,
        }
    adjusted = holm(raw_p)
    for key in pairwise:
        pairwise[key]["holm_adjusted_p"] = adjusted[key]

    mean_ranks = {}
    for wave in WAVES:
        mean_ranks[str(wave)] = {
            "prime_mean_rank": statistics.fmean(rank(row, wave) for row in primes),
            "unresolved_composite_mean_rank": statistics.fmean(rank(row, wave) for row in unresolved),
        }

    payload = {
        "test_id": "PN31/FIVE-INDEPENDENT-HANDOVER/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "POST-HOC DESCRIPTIVE - NOT A FROZEN ENDPOINT",
        "pairwise_order_relations": pairwise,
        "mean_wave_ranks": mean_ranks,
        "holm_family_size": len(pairwise),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
