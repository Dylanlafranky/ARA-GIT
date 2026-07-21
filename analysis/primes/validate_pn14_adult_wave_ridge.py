#!/usr/bin/env python3
"""Independent PN14 validator.

This deliberately does not import the primary PN14 implementation. It rebuilds
the gate table with a bytearray sieve, reconstructs the target blocks, checks all
target counts and means, and validates a complete small-prime joint cycle.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "PN14_TARGET_FREEZE_MANIFEST.json"
DEVELOPMENT = HERE / "PN14_DEVELOPMENT_RESULTS.json"
TARGET = HERE / "PN14_TARGET_RESULTS.json"
OUTPUT = HERE / "PN14_ADULT_WAVE_RIDGE_VALIDATION.json"
SCALE = 11
K = 9
SECTORS = 16
BLOCK_MULTIPLIER = 8


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def primes_through(limit: int) -> list[int]:
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0:2] = b"\x00\x00"
    for number in range(2, math.isqrt(limit) + 1):
        if flags[number]:
            start = number * number
            flags[start : limit + 1 : number] = b"\x00" * (((limit - start) // number) + 1)
    return [index for index, flag in enumerate(flags) if flag]


def target_geometry() -> dict[str, Any]:
    anchor = 4 * 10**SCALE
    boundary = anchor**0.45
    primes = primes_through(int(math.ceil(boundary)) + 2)
    last = max(index for index, value in enumerate(primes) if value <= boundary)
    gates = [primes[last - index] for index in range(K)]
    pairs = []
    for index in range(K - 1):
        q, r = gates[index], gates[index + 1]
        pairs.append({
            "pair_index": index, "q": q, "r": r, "gap": abs(q - r),
            "joint_period": q * r, "relative_phase_period": q * r / abs(q - r),
        })
    joint = sorted(row["joint_period"] for row in pairs)
    median = (joint[3] + joint[4]) / 2.0
    representative = min(range(len(pairs)), key=lambda i: (abs(pairs[i]["joint_period"] - median), i))
    return {
        "anchor": anchor, "threshold_n_pow_0p45": boundary, "gates_descending": gates,
        "pairs": pairs, "median_joint_period": median, "representative_pair_index": representative,
        "representative_pair": pairs[representative],
    }


def phase_scalar(number: int, q: int, r: int) -> float:
    return ((number * (r - q)) % (q * r)) / (q * r)


def circle_distance(a: float, b: float) -> float:
    gap = abs(a - b) % 1.0
    return min(gap, 1.0 - gap)


def phase_center_number(anchor: int, q: int, r: int, target: float) -> int:
    period = q * r
    delta = r - q
    initial = phase_scalar(anchor, q, r)
    travel = ((initial - target) if delta < 0 else (target - initial)) % 1.0
    estimate = int(round(travel * period / abs(delta)))
    return anchor + min(
        (max(0, estimate + shift) for shift in range(-3, 4)),
        key=lambda offset: circle_distance(phase_scalar(anchor + offset, q, r), target),
    )


def independent_masks(low: int, high: int, paid_limit: int, prime_table: list[int]) -> tuple[np.ndarray, np.ndarray]:
    prime = np.ones(high - low, dtype=bool)
    paid = np.ones(high - low, dtype=bool)
    for p in prime_table:
        if p * p >= high and p > paid_limit:
            break
        first = ((low + p - 1) // p) * p
        if first == p:
            first += p
        if first < p * p:
            first = p * p
        if first >= high:
            continue
        prime[first - low :: p] = False
        if p <= paid_limit:
            paid[first - low :: p] = False
    return prime, paid


def validate_sector(expected: dict[str, Any], geometry: dict[str, Any], prime_table: list[int]) -> dict[str, Any]:
    q = int(geometry["representative_pair"]["q"])
    r = int(geometry["representative_pair"]["r"])
    sector = int(expected["sector"])
    target_phase = (sector + 0.5) / SECTORS
    center = phase_center_number(int(geometry["anchor"]), q, r, target_phase)
    half = BLOCK_MULTIPLIER * max(q, r) // 2
    low, high = center - half, center + half + 1
    numbers = np.arange(low, high, dtype=np.int64)
    prime, paid = independent_masks(low, high, max(q, r), prime_table)
    theta = np.mod(numbers * (r - q), q * r).astype(np.float64) / (q * r)
    selected = np.minimum((theta * SECTORS).astype(np.int64), SECTORS - 1) == sector
    aq = 2.0 * (numbers % q).astype(np.float64) / q
    ar = 2.0 * (numbers % r).astype(np.float64) / r
    z = (aq - 1.0) * (ar - 1.0)
    masks = {
        "raw": selected,
        "prime": selected & prime,
        "late_composite": selected & paid & (~prime),
    }
    comparisons: dict[str, Any] = {}
    for name, mask in masks.items():
        values = z[mask]
        expected_summary = expected["populations"][name]
        measured_count = int(np.count_nonzero(mask))
        measured_mean = float(np.mean(values))
        comparisons[name] = {
            "expected_count": int(expected_summary["n"]), "measured_count": measured_count,
            "count_match": measured_count == int(expected_summary["n"]),
            "expected_mean": float(expected_summary["mean"]), "measured_mean": measured_mean,
            "mean_abs_error": abs(measured_mean - float(expected_summary["mean"])),
        }
    return {
        "sector": sector, "center_match": center == int(expected["center_number"]),
        "low_match": low == int(expected["block_low"]), "high_match": high == int(expected["block_high"]),
        "populations": comparisons,
    }


def small_cycle_fixture() -> dict[str, Any]:
    q, r = 101, 103
    numbers = np.arange(q * r, dtype=np.int64)
    theta = np.mod(numbers * (r - q), q * r).astype(np.float64) / (q * r)
    z = (2.0 * (numbers % q) / q - 1.0) * (2.0 * (numbers % r) / r - 1.0)
    index = np.minimum((theta * SECTORS).astype(np.int64), SECTORS - 1)
    means = np.asarray([np.mean(z[index == sector]) for sector in range(SECTORS)])
    centers = (np.arange(SECTORS) + 0.5) / SECTORS
    analytic = 1.0 / 3.0 - 2.0 * centers + 2.0 * centers**2
    return {
        "q": q, "r": r, "lcm": math.lcm(q, r), "product": q * r,
        "lcm_equals_product": math.lcm(q, r) == q * r,
        "curve_correlation": float(np.corrcoef(means, analytic)[0, 1]),
        "curve_rmse": float(np.sqrt(np.mean((means - analytic) ** 2))),
    }


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hash_checks = {
        name: {"expected": digest, "actual": file_hash(HERE / name), "match": file_hash(HERE / name) == digest}
        for name, digest in manifest["files"].items()
    }
    expected = json.loads(TARGET.read_text(encoding="utf-8"))
    development = json.loads(DEVELOPMENT.read_text(encoding="utf-8"))
    measured_geometry = target_geometry()
    recorded_geometry = expected["target"]["geometry"]
    geometry_checks = {
        "gates_match": measured_geometry["gates_descending"] == recorded_geometry["gates_descending"],
        "pairs_match": measured_geometry["pairs"] == recorded_geometry["pairs"],
        "median_match": measured_geometry["median_joint_period"] == recorded_geometry["median_joint_period"],
        "representative_match": measured_geometry["representative_pair_index"] == recorded_geometry["representative_pair_index"],
        "all_lcm_equal_product": all(math.lcm(row["q"], row["r"]) == row["joint_period"] for row in measured_geometry["pairs"]),
    }
    max_forward = int(math.ceil(float(measured_geometry["representative_pair"]["relative_phase_period"])))
    max_high = int(measured_geometry["anchor"]) + max_forward + BLOCK_MULTIPLIER * int(measured_geometry["representative_pair"]["q"])
    prime_table = primes_through(math.isqrt(max_high) + 1)
    sectors = [
        validate_sector(row, measured_geometry, prime_table) for row in expected["target"]["sectors"]
    ]

    j9 = float(development["scales"][1]["geometry"]["median_joint_period"])
    j10 = float(development["scales"][2]["geometry"]["median_joint_period"])
    j11 = float(measured_geometry["median_joint_period"])
    g9, g10 = j10 / j9, j11 / j10
    ridge = 2.0 * g9 / (g9 + g10)
    metric_checks = {
        "G10_abs_error": abs(g10 - float(expected["metrics"]["adult_scale_ridge"]["G10"])),
        "ridge_abs_error": abs(ridge - float(expected["metrics"]["adult_scale_ridge"]["ridge_A"])),
    }
    fixture = small_cycle_fixture()
    all_sector_checks = all(
        row["center_match"] and row["low_match"] and row["high_match"]
        and all(pop["count_match"] and pop["mean_abs_error"] <= 1e-12 for pop in row["populations"].values())
        for row in sectors
    )
    checks = {
        "all_frozen_hashes_match": all(row["match"] for row in hash_checks.values()),
        "geometry_matches": all(geometry_checks.values()),
        "all_16_sector_counts_and_means_match": all_sector_checks,
        "adult_metrics_match": metric_checks["G10_abs_error"] <= 1e-15 and metric_checks["ridge_abs_error"] <= 1e-15,
        "small_cycle_recovers_analytic_curve": fixture["curve_correlation"] >= 0.999 and fixture["curve_rmse"] <= 0.005,
    }
    result = {
        "test_id": "PN14/CHILD-ADULT-RIDGE/v1", "validator": "independent bytearray prime sieve",
        "hash_checks": hash_checks, "geometry_checks": geometry_checks, "sector_checks": sectors,
        "metric_checks": metric_checks, "small_cycle_fixture": fixture, "checks": checks,
        "passed": all(checks.values()), "passed_count": sum(checks.values()), "total_count": len(checks),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": OUTPUT.name, "passed": result["passed"], "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
