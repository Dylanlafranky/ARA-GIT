"""Post-target descriptive cost audit for PN18 and standard local controls."""

from __future__ import annotations

import json
import math
import platform
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path

from pn18_recursive_teara_product_tree import (
    P29_PRIMORIAL,
    TARGET_ANCHOR,
    WINDOW,
    eratosthenes,
    recursive_product,
    run_anchor,
)
from validate_pn18_recursive_teara_product_tree import miller_rabin_64, segmented_first_quiet


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN18_COST_AUDIT.json"
ITERATIONS = 5


def median_timed(callable_):
    times = []
    values = []
    for _ in range(ITERATIONS):
        started = time.perf_counter()
        values.append(callable_())
        times.append(time.perf_counter() - started)
    if len(set(values)) != 1:
        raise RuntimeError("benchmark returned inconsistent values")
    return values[0], times, statistics.median(times)


def segmented_from_scratch() -> int:
    children = eratosthenes(math.isqrt(TARGET_ANCHOR + WINDOW - 1))
    correction, _ = segmented_first_quiet(TARGET_ANCHOR, WINDOW, children)
    return correction


def recursive_from_scratch() -> int:
    row, _, _ = run_anchor(TARGET_ANCHOR)
    return row["correction"]


def first_prime_by_miller_rabin_wheel() -> tuple[int, int]:
    rank = 0
    for offset in range(1, WINDOW):
        candidate = TARGET_ANCHOR + offset
        if math.gcd(candidate, P29_PRIMORIAL) != 1:
            continue
        rank += 1
        if miller_rabin_64(candidate):
            return offset, rank
    raise RuntimeError("no Miller-Rabin candidate in block")


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN18 cost audit already exists; refusing to overwrite")

    children = eratosthenes(math.isqrt(TARGET_ANCHOR + WINDOW - 1))
    child_root, _ = recursive_product(children)

    def sequential_root_gcd() -> tuple[int, int]:
        rank = 0
        for offset in range(1, WINDOW):
            candidate = TARGET_ANCHOR + offset
            if math.gcd(candidate, P29_PRIMORIAL) != 1:
                continue
            rank += 1
            if math.gcd(candidate, child_root) == 1:
                return offset, rank
        raise RuntimeError("no root-GCD candidate in block")

    segmented_value, segmented_times, segmented_median = median_timed(segmented_from_scratch)
    recursive_value, recursive_times, recursive_median = median_timed(recursive_from_scratch)
    gcd_value, gcd_times, gcd_median = median_timed(sequential_root_gcd)
    mr_value, mr_times, mr_median = median_timed(first_prime_by_miller_rabin_wheel)

    payload = {
        "test_id": "PN18/POST-TARGET-COST-AUDIT/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "descriptive post-target implementation timing; not a frozen prediction endpoint",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "iterations": ITERATIONS,
        "anchor": TARGET_ANCHOR,
        "window": WINDOW,
        "results": {
            "segmented_sieve_from_scratch": {
                "correction": segmented_value,
                "seconds": segmented_times,
                "median_seconds": segmented_median,
            },
            "pn18_recursive_tree_from_scratch": {
                "correction": recursive_value,
                "seconds": recursive_times,
                "median_seconds": recursive_median,
            },
            "sequential_root_gcd_with_prebuilt_root": {
                "correction_and_p29_rank": gcd_value,
                "seconds": gcd_times,
                "median_seconds": gcd_median,
            },
            "p29_wheel_deterministic_miller_rabin": {
                "correction_and_p29_rank": mr_value,
                "seconds": mr_times,
                "median_seconds": mr_median,
            },
        },
        "interpretation_guardrail": (
            "The prebuilt-root query excludes the cost of generating primes and multiplying the root. "
            "Wall times compare these Python implementations only and are not asymptotic benchmarks."
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        name: record["median_seconds"]
        for name, record in payload["results"].items()
    }, indent=2))


if __name__ == "__main__":
    main()
