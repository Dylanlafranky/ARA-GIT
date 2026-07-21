"""Post-target PN17 diagnostic of simple scalar TE-ARA aggregations.

This file is explicitly descriptive. It was created after the one-shot target
prediction was sealed and independently validated; it cannot alter that result.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREDICTION = HERE / "PN17_ONE_SHOT_LOCAL_RIDGE_PREDICTION.json"
OUTPUT = HERE / "PN17_SCALAR_RIDGE_DIAGNOSTIC.json"


def primes_upto(limit: int) -> list[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for prime in range(2, math.isqrt(limit) + 1):
        if sieve[prime]:
            start = prime * prime
            sieve[start : limit + 1 : prime] = b"\x00" * (((limit - start) // prime) + 1)
    return [value for value in range(2, limit + 1) if sieve[value]]


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN17 scalar diagnostic already exists; refusing to overwrite")
    prediction = json.loads(PREDICTION.read_text(encoding="utf-8"))
    anchor = prediction["target"]["anchor"]
    correction = prediction["target"]["correction"]
    ceiling = prediction["target"]["sqrt_block_end_floor"]
    children = primes_upto(ceiling)
    weighting = {
        "equal_child": lambda q: 1.0,
        "log_child": lambda q: math.log(q),
        "inverse_period": lambda q: 1.0 / q,
    }

    methods = {}
    for name, weight_function in weighting.items():
        weights = [weight_function(child) for child in children]
        weight_total = sum(weights)
        rows = []
        for offset in range(correction + 1):
            number = anchor + offset
            phase_a = sum(
                weight * 2.0 * (number % child) / child
                for child, weight in zip(children, weights)
            ) / weight_total
            collision_count = sum(number % child == 0 for child in children)
            rows.append({
                "offset": offset,
                "phase_a": phase_a,
                "phase_b": 2.0 - phase_a,
                "ridge_error": abs(phase_a - 1.0),
                "collision_count": collision_count,
            })
        best = min(rows, key=lambda row: (row["ridge_error"], row["offset"]))
        target = rows[correction]
        anchor_row = rows[0]
        methods[name] = {
            "best_scalar_ridge_offset_in_opened_range": best["offset"],
            "best_scalar_ridge_is_quiet": best["collision_count"] == 0,
            "best_scalar_ridge_error": best["ridge_error"],
            "sealed_prime_offset": correction,
            "sealed_prime_scalar_ridge_error": target["ridge_error"],
            "sealed_prime_rank_by_scalar_ridge_error": 1 + sum(
                row["ridge_error"] < target["ridge_error"] for row in rows
            ),
            "anchor_phase_a": anchor_row["phase_a"],
            "anchor_phase_b": anchor_row["phase_b"],
            "anchor_ridge_error": anchor_row["ridge_error"],
            "anchor_collision_count": anchor_row["collision_count"],
            "literal_parent_scale_correction_N_times_error": anchor * anchor_row["ridge_error"],
            "literal_full_diameter_correction_2N_times_error": 2 * anchor * anchor_row["ridge_error"],
            "rows_0_through_sealed_offset": rows,
        }

    output = {
        "status": "POST_TARGET_DIAGNOSTIC_ONLY",
        "prediction_packet": PREDICTION.name,
        "anchor": anchor,
        "sealed_prime_offset": correction,
        "child_count": len(children),
        "finding": (
            "The fully decompressed collision vector locates the quiet ridge exactly. None of the three simple "
            "scalar A/B averages selects that offset within 0..Delta, so a scalar shortcut requires a different "
            "predeclared coupling/aggregation law."
        ),
        "methods": methods,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        name: {
            "best_offset": record["best_scalar_ridge_offset_in_opened_range"],
            "best_is_quiet": record["best_scalar_ridge_is_quiet"],
            "prime_rank": record["sealed_prime_rank_by_scalar_ridge_error"],
        }
        for name, record in methods.items()
    }, indent=2))


if __name__ == "__main__":
    main()
