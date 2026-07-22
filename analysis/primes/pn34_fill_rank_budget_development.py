"""Development-only bridge from PN33 fill to PN26 rank coverage.

This script reads already-open PN26 rows.  It does not create or score any
PN34 target.  Its only purpose is to make the proposed no-fit bridge explicit
before a fresh test is frozen.
"""

from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "PN26_DOMINANT_PARENT_RIDGE_VALIDATED_ROWS_V1_1.csv"
OUTPUT = HERE / "PN34_FILL_RANK_BUDGET_DEVELOPMENT.json"

SCALES = {
    "low": 71_000_000,
    "middle": 71_000_000_000,
    "high": 710_000_000_000,
}


def sieve_primes(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            start = value * value
            flags[start : limit + 1 : value] = b"\x00" * (((limit - start) // value) + 1)
    return [value for value in range(2, limit + 1) if flags[value]]


def wilson_interval(successes: int, trials: int, z: float = 1.959963984540054) -> tuple[float, float]:
    p = successes / trials
    z2 = z * z
    denominator = 1.0 + z2 / trials
    centre = (p + z2 / (2.0 * trials)) / denominator
    half = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * trials)) / trials) / denominator
    return centre - half, centre + half


def main() -> None:
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    primes = sieve_primes(math.isqrt(2 * max(SCALES.values())) + 1)
    cohorts: list[dict] = []
    pooled_hits = [0, 0, 0]
    pooled_n = 0

    for cohort, scale_anchor in SCALES.items():
        selected = [row for row in rows if row["cohort"] == cohort]
        if not selected:
            raise RuntimeError(f"no PN26 rows for {cohort}")

        phase_a_count = int(selected[0]["phase_a_child_count"])
        phase_b_count = int(selected[0]["phase_b_child_count"])
        phase_b = primes[phase_a_count : phase_a_count + phase_b_count]
        log_remaining_fill = sum(-math.log1p(-1.0 / prime) for prime in phase_b)
        remaining_fill_ratio = math.exp(log_remaining_fill)
        remaining_fill_x = 2.0 * log_remaining_fill / math.log(2.0)
        predicted_top1 = 1.0 / remaining_fill_ratio
        predicted = [1.0 - (1.0 - predicted_top1) ** depth for depth in (1, 2, 3)]

        observed: list[float] = []
        intervals: list[list[float]] = []
        counts: list[int] = []
        for depth in (1, 2, 3):
            hits = sum(int(row[f"phase_a_top{depth}_hit"]) for row in selected)
            counts.append(hits)
            observed.append(hits / len(selected))
            intervals.append(list(wilson_interval(hits, len(selected))))
            pooled_hits[depth - 1] += hits
        pooled_n += len(selected)

        cohorts.append(
            {
                "cohort": cohort,
                "scale_anchor": scale_anchor,
                "rows": len(selected),
                "phase_a_count": phase_a_count,
                "phase_b_count": phase_b_count,
                "remaining_fill_ratio": remaining_fill_ratio,
                "remaining_fill_x": remaining_fill_x,
                "predicted_top1": predicted[0],
                "predicted_top2": predicted[1],
                "predicted_top3": predicted[2],
                "observed_top1": observed[0],
                "observed_top2": observed[1],
                "observed_top3": observed[2],
                "observed_wilson95": intervals,
                "absolute_errors": [abs(a - b) for a, b in zip(predicted, observed)],
                "rank_counts_1_to_5": [
                    sum(int(row["phase_a_rank_of_prime"]) == rank for row in selected)
                    for rank in range(1, 6)
                ],
            }
        )

    payload = {
        "test_id": "PN34/FILL-RANK-BUDGET/development",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE.name,
        "source_status": "already opened PN26 development evidence",
        "formula": {
            "remaining_fill_ratio": "R_B=product_{p in B} p/(p-1)",
            "remaining_fill_coordinate": "x_B=2 log(R_B)/log(2)",
            "top1_prior": "pi_1=1/R_B=2^(-x_B/2)",
            "rank_budget": "pi_k=1-(1-pi_1)^k",
        },
        "cohorts": cohorts,
        "pooled_observed": [value / pooled_n for value in pooled_hits],
        "maximum_absolute_error_by_depth": [
            max(row["absolute_errors"][index] for row in cohorts) for index in range(3)
        ],
        "interpretation": (
            "The PN33-style inverse-density fill of PN26's omitted Phase B parent is a no-fit "
            "population prior for how many Phase A quiet candidates must be retained. It is not "
            "an individual candidate classifier."
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
