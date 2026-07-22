"""Produce labelled, explicitly post-hoc PN30 descriptive diagnostics."""

from __future__ import annotations

import csv
import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCORED = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_SCORED.csv"
OUTPUT = HERE / "PN30_DYNAMIC_RELATIONAL_FLIP_POSTHOC.json"
PAIR_KEYS = ("1_13", "3_11", "5_9")


def read_rows() -> list[dict[str, str]]:
    with SCORED.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def auc_lower(positive: list[float], negative: list[float]) -> float:
    score = sum(
        1.0 if pos < neg else 0.5 if pos == neg else 0.0
        for pos in positive
        for neg in negative
    )
    return score / (len(positive) * len(negative))


def group_summary(rows: list[dict[str, str]]) -> dict:
    collapsed = [float(row["dynamic_ridge_distance_2_decimal"]) * 4 for row in rows]
    mean_absolute_pair = []
    cancellation = []
    for row, collapsed_distance in zip(rows, collapsed):
        pair_distances = [abs(float(row[f"x_dynamic_{key}_decimal"]) - 1) for key in PAIR_KEYS]
        local_mean_absolute = statistics.fmean(pair_distances)
        mean_absolute_pair.append(local_mean_absolute)
        cancellation.append(
            1 - collapsed_distance / local_mean_absolute if local_mean_absolute else 1.0
        )
    return {
        "n": len(rows),
        "mean_child_rung_collapsed_distance": statistics.fmean(collapsed),
        "median_child_rung_collapsed_distance": statistics.median(collapsed),
        "mean_of_pair_absolute_distances": statistics.fmean(mean_absolute_pair),
        "mean_signed_cancellation_fraction": statistics.fmean(cancellation),
        "median_signed_cancellation_fraction": statistics.median(cancellation),
    }


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError(f"refusing to overwrite {OUTPUT.name}")
    rows = read_rows()
    primes = [row for row in rows if int(row["is_prime"])]
    unresolved = [
        row for row in rows
        if not int(row["is_prime"]) and int(row["unresolved_by_declared_children"])
    ]

    pairs = {}
    for key in PAIR_KEYS:
        prime_distance = [abs(float(row[f"x_dynamic_{key}_decimal"]) - 1) for row in primes]
        unresolved_distance = [abs(float(row[f"x_dynamic_{key}_decimal"]) - 1) for row in unresolved]
        pairs[key] = {
            "prime_mean_absolute_pair_distance": statistics.fmean(prime_distance),
            "unresolved_mean_absolute_pair_distance": statistics.fmean(unresolved_distance),
            "auc_prime_more_pair_ridge_close": auc_lower(prime_distance, unresolved_distance),
            "prime_orientations": dict(Counter(row[f"orientation_{key}"] for row in primes)),
            "unresolved_orientations": dict(Counter(row[f"orientation_{key}"] for row in unresolved)),
        }

    def pattern_counts(group: list[dict[str, str]]) -> dict:
        return dict(Counter(
            " | ".join(row[f"orientation_{key}"] for key in PAIR_KEYS)
            for row in group
        ).most_common())

    payload = {
        "test_id": "PN30/DYNAMIC-RELATIONAL-FLIP/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "POST-HOC DESCRIPTIVE - NOT A FROZEN ENDPOINT",
        "prime": group_summary(primes),
        "unresolved_composite": group_summary(unresolved),
        "pair_breakdown": pairs,
        "orientation_patterns": {
            "prime": pattern_counts(primes),
            "unresolved_composite": pattern_counts(unresolved),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
