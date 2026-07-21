#!/usr/bin/env python3
"""Independent arithmetic validation for PN13.

This validator uses a separately implemented boolean segmented sieve, ascending
gate order, and direct sequential primorial construction. It is algorithmically
independent checking, not an independent scientific replication.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
SAVED = json.loads((HERE / "PN13_TARGET_RESULTS.json").read_text(encoding="utf-8"))
OUTPUT = HERE / "PN13_DECIMAL_RUNG_VALIDATION.json"
K = 9


def simple_primes(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=bool)
    sieve[:2] = False
    for p in range(2, math.isqrt(limit) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = False
    return np.flatnonzero(sieve).astype(np.int64)


def interval_primes(low: int, high: int) -> np.ndarray:
    composite = np.zeros(high - low, dtype=bool)
    for p64 in simple_primes(math.isqrt(high - 1)):
        p = int(p64)
        start = max(p * p, ((low + p - 1) // p) * p)
        if start < high:
            composite[start - low :: p] = True
    numbers = np.arange(low, high, dtype=np.int64)
    return numbers[~composite]


def coupling_mean(primes: np.ndarray) -> float:
    thresholds = primes.astype(np.float64) ** 0.45
    gates_all = simple_primes(int(math.ceil(float(np.max(thresholds)))) + 2)
    values = np.empty(len(primes), dtype=np.float64)
    for start in range(0, len(primes), 50_000):
        stop = min(start + 50_000, len(primes))
        n = primes[start:stop]
        last = np.searchsorted(gates_all, thresholds[start:stop], side="right") - 1
        # Ascending order is deliberately different from the primary implementation.
        indices = last[:, None] - np.arange(K - 1, -1, -1, dtype=np.int64)[None, :]
        gates = gates_all[indices]
        signed = 2.0 * (n[:, None] % gates).astype(np.float64) / gates.astype(np.float64) - 1.0
        values[start:stop] = np.mean(signed[:, :-1] * signed[:, 1:], axis=1)
    return float(np.mean(values))


def first_n_primes(count: int) -> list[int]:
    limit = 15 if count < 6 else int(count * (math.log(count) + math.log(math.log(count)))) + 100
    while True:
        primes = simple_primes(limit).tolist()
        if len(primes) >= count:
            return primes[:count]
        limit *= 2


def direct_vector(start_m: int, steps: int = 4_000) -> dict[str, float]:
    primes = first_n_primes(start_m + steps + 1)
    parent = 1
    for value in primes[:start_m]:
        parent *= value
    previous = None
    x_sum = 0.0
    y_sum = 0.0
    count = 0
    for offset in range(steps + 1):
        m = start_m + offset
        phase = (parent % primes[m]) / primes[m]
        if previous is not None:
            delta = (phase - previous) % 1.0
            x_sum += math.cos(2.0 * math.pi * delta)
            y_sum += math.sin(2.0 * math.pi * delta)
            count += 1
        previous = phase
        if offset < steps:
            parent *= primes[m]
    x = x_sum / count
    y = y_sum / count
    return {"x": x, "y": y, "R": math.hypot(x, y)}


def check(name: str, passed: bool, evidence: str) -> dict[str, Any]:
    return {"name": name, "pass": bool(passed), "evidence": evidence}


def main() -> None:
    checks: list[dict[str, Any]] = []
    recomputed_vectors: dict[str, dict[str, float]] = {}
    saved_windows = {row["start_m"]: row for row in SAVED["prime_ladder_arm"]["windows"]}
    for start in (1_000, 10_000, 100_000):
        result = direct_vector(start)
        recomputed_vectors[str(start)] = result
        saved = saved_windows[start]["vector"]
        checks.append(check(f"vector_{start}_x", abs(result["x"] - saved["x"]) < 1e-13, f"recomputed={result['x']:.15g} saved={saved['x']:.15g}"))
        checks.append(check(f"vector_{start}_y", abs(result["y"] - saved["y"]) < 1e-13, f"recomputed={result['y']:.15g} saved={saved['y']:.15g}"))
        checks.append(check(f"vector_{start}_R", abs(result["R"] - saved["resultant_length"]) < 1e-13, f"recomputed={result['R']:.15g} saved={saved['resultant_length']:.15g}"))

    saved_intervals = {row["scale"]: row for row in SAVED["raw_integer_arm"]["intervals"]}
    recomputed_intervals: dict[str, Any] = {}
    for scale in (8, 9, 10):
        saved = saved_intervals[scale]
        primes = interval_primes(saved["low"], saved["high"])
        mean = coupling_mean(primes)
        recomputed_intervals[str(scale)] = {"prime_count": int(len(primes)), "prime_mean": mean}
        checks.append(check(f"scale_{scale}_prime_count", len(primes) == saved["prime"]["summary"]["n"], f"recomputed={len(primes)} saved={saved['prime']['summary']['n']}"))
        checks.append(check(f"scale_{scale}_prime_mean", abs(mean - saved["prime"]["summary"]["mean"]) < 1e-14, f"recomputed={mean:.15g} saved={saved['prime']['summary']['mean']:.15g}"))

    means = [recomputed_intervals[str(scale)]["prime_mean"] for scale in (8, 9, 10)]
    ratio_89 = means[1] / means[0]
    ratio_910 = means[2] / means[1]
    checks.append(check("registered_ratios_reproduced", abs(ratio_89 - SAVED["raw_integer_arm"]["ratios"]["C9_over_C8"]) < 1e-13 and abs(ratio_910 - SAVED["raw_integer_arm"]["ratios"]["C10_over_C9"]) < 1e-13, f"ratios={ratio_89:.12g},{ratio_910:.12g}"))
    checks.append(check("arm_a_verdict", SAVED["prime_ladder_arm"]["verdict"] == "NOT SUPPORTED", SAVED["prime_ladder_arm"]["verdict"]))
    checks.append(check("arm_b_verdict", SAVED["raw_integer_arm"]["verdict"] == "NOT SUPPORTED", SAVED["raw_integer_arm"]["verdict"]))
    checks.append(check("fixed_pi_verdict", SAVED["raw_integer_arm"]["fixed_pi_sequence"]["verdict"] == "NOT SUPPORTED", SAVED["raw_integer_arm"]["fixed_pi_sequence"]["verdict"]))

    result = {
        "test_id": "PN13/DECIMAL-RUNG-LEAK/v1",
        "validator": "boolean segmented sieve + ascending gates + direct sequential primorial",
        "scientific_replication": False,
        "checks_passed": sum(item["pass"] for item in checks),
        "checks_total": len(checks),
        "all_pass": all(item["pass"] for item in checks),
        "recomputed_vectors": recomputed_vectors,
        "recomputed_intervals": recomputed_intervals,
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PN13 validation: {result['checks_passed']}/{result['checks_total']} checks pass")
    if not result["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
