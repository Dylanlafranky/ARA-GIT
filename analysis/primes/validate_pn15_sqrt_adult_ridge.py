#!/usr/bin/env python3
"""Independent PN15 scale-12 validator using a bytearray sieve."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "PN15_TARGET_FREEZE_MANIFEST.json"
DEVELOPMENT = HERE / "PN15_DEVELOPMENT_RESULTS.json"
TEMPLATE = HERE / "PN15_DEVELOPMENT_TEMPLATE.json"
TARGET = HERE / "PN15_TARGET_RESULTS.json"
OUTPUT = HERE / "PN15_SQRT_ADULT_RIDGE_VALIDATION.json"
SCALE = 12
K = 9
SECTORS = 16
BLOCK_MULTIPLIER = 2


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
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
    parent = 4 * 10**SCALE
    boundary = math.sqrt(parent)
    primes = primes_through(int(math.ceil(boundary)) + 1_000)
    last = max(index for index, value in enumerate(primes) if value <= boundary)
    gates = [primes[last - index] for index in range(K)]
    pairs: list[dict[str, Any]] = []
    for index in range(K - 1):
        q, r = gates[index], gates[index + 1]
        child_a = 2.0 * math.log(q) / math.log(parent)
        child_b = 2.0 * math.log(r) / math.log(parent)
        pairs.append(
            {
                "pair_index": index,
                "q": q,
                "r": r,
                "gap": abs(q - r),
                "child_A_coordinate": child_a,
                "child_B_coordinate": child_b,
                "adult_coordinate_sum": child_a + child_b,
                "joint_period": q * r,
                "adult_fill_of_anchor": q * r / parent,
                "relative_phase_period": q * r / abs(q - r),
            }
        )
    ordered = sorted(row["joint_period"] for row in pairs)
    median = (ordered[3] + ordered[4]) / 2.0
    representative = min(range(len(pairs)), key=lambda i: (abs(pairs[i]["joint_period"] - median), i))
    return {
        "scale": SCALE,
        "anchor": parent,
        "sqrt_anchor": boundary,
        "gates_descending": gates,
        "first_omitted_prime_above_boundary": primes[last + 1],
        "pairs": pairs,
        "median_joint_period": median,
        "median_adult_fill": median / parent,
        "representative_pair_index": representative,
        "representative_pair": pairs[representative],
    }


def phase(number: int | np.ndarray, q: int, r: int) -> float | np.ndarray:
    period = q * r
    return np.mod(np.asarray(number, dtype=np.int64) * (r - q), period).astype(np.float64) / period


def circle_gap(a: float, b: float) -> float:
    gap = abs(a - b) % 1.0
    return min(gap, 1.0 - gap)


def center_number(anchor: int, q: int, r: int, desired: float) -> int:
    period = q * r
    delta = r - q
    initial = float(phase(anchor, q, r))
    travel = ((initial - desired) if delta < 0 else (desired - initial)) % 1.0
    estimate = int(round(travel * period / abs(delta)))
    offset = min(
        (max(0, estimate + shift) for shift in range(-3, 4)),
        key=lambda value: circle_gap(float(phase(anchor + value, q, r)), desired),
    )
    return anchor + offset


def prime_mask(low: int, high: int, table: list[int]) -> np.ndarray:
    mask = np.ones(high - low, dtype=bool)
    for p in table:
        if p * p >= high:
            break
        first = max(p * p, ((low + p - 1) // p) * p)
        if first < high:
            mask[first - low :: p] = False
    return mask


def validate_sector(expected: dict[str, Any], geometry: dict[str, Any], table: list[int]) -> dict[str, Any]:
    pair = geometry["representative_pair"]
    q, r = int(pair["q"]), int(pair["r"])
    sector = int(expected["sector"])
    desired = (sector + 0.5) / SECTORS
    center = center_number(int(geometry["anchor"]), q, r, desired)
    half_width = BLOCK_MULTIPLIER * max(q, r) // 2
    low, high = center - half_width, center + half_width + 1
    numbers = np.arange(low, high, dtype=np.int64)
    is_prime = prime_mask(low, high, table)
    theta = np.asarray(phase(numbers, q, r), dtype=np.float64)
    selected = np.minimum((theta * SECTORS).astype(np.int64), SECTORS - 1) == sector
    a_q = 2.0 * (numbers % q).astype(np.float64) / q
    a_r = 2.0 * (numbers % r).astype(np.float64) / r
    product = (a_q - 1.0) * (a_r - 1.0)
    masks = {"raw": selected, "prime": selected & is_prime, "composite": selected & (~is_prime)}
    populations: dict[str, Any] = {}
    for name, mask in masks.items():
        values = product[mask]
        expected_summary = expected["populations"][name]
        count = int(np.count_nonzero(mask))
        mean = float(np.mean(values))
        populations[name] = {
            "expected_count": int(expected_summary["n"]),
            "measured_count": count,
            "count_match": count == int(expected_summary["n"]),
            "expected_mean": float(expected_summary["mean"]),
            "measured_mean": mean,
            "mean_abs_error": abs(mean - float(expected_summary["mean"])),
        }
    return {
        "sector": sector,
        "center_match": center == int(expected["center_number"]),
        "low_match": low == int(expected["block_low"]),
        "high_match": high == int(expected["block_high"]),
        "populations": populations,
    }


def small_cycle_fixture() -> dict[str, Any]:
    q, r = 1009, 1013
    numbers = np.arange(q * r, dtype=np.int64)
    theta = np.asarray(phase(numbers, q, r), dtype=np.float64)
    product = (2.0 * (numbers % q) / q - 1.0) * (2.0 * (numbers % r) / r - 1.0)
    bins = np.minimum((theta * SECTORS).astype(np.int64), SECTORS - 1)
    means = np.asarray([np.mean(product[bins == sector]) for sector in range(SECTORS)])
    centers = (np.arange(SECTORS) + 0.5) / SECTORS
    analytic = 1.0 / 3.0 - 2.0 * centers + 2.0 * centers**2
    return {
        "q": q,
        "r": r,
        "lcm_equals_product": math.lcm(q, r) == q * r,
        "curve_correlation": float(np.corrcoef(means, analytic)[0, 1]),
        "curve_rmse": float(np.sqrt(np.mean((means - analytic) ** 2))),
    }


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hash_checks: dict[str, Any] = {}
    for name, expected_hash in manifest["files"].items():
        actual_hash = file_hash(HERE / name)
        hash_checks[name] = {"expected": expected_hash, "actual": actual_hash, "match": actual_hash == expected_hash}

    expected = json.loads(TARGET.read_text(encoding="utf-8"))
    development = json.loads(DEVELOPMENT.read_text(encoding="utf-8"))
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    measured_geometry = target_geometry()
    recorded_geometry = expected["target"]["geometry"]
    geometry_checks = {
        "gates_match": measured_geometry["gates_descending"] == recorded_geometry["gates_descending"],
        "omitted_gate_match": measured_geometry["first_omitted_prime_above_boundary"] == recorded_geometry["first_omitted_prime_above_boundary"],
        "pairs_match": measured_geometry["pairs"] == recorded_geometry["pairs"],
        "median_match": measured_geometry["median_joint_period"] == recorded_geometry["median_joint_period"],
        "representative_match": measured_geometry["representative_pair_index"] == recorded_geometry["representative_pair_index"],
        "all_lcm_equal_product": all(math.lcm(row["q"], row["r"]) == row["joint_period"] for row in measured_geometry["pairs"]),
    }
    pair = measured_geometry["representative_pair"]
    max_forward = int(math.ceil(float(pair["relative_phase_period"])))
    max_high = int(measured_geometry["anchor"]) + max_forward + BLOCK_MULTIPLIER * int(pair["q"])
    prime_table = primes_through(math.isqrt(max_high) + 1)
    sectors = [validate_sector(row, measured_geometry, prime_table) for row in expected["target"]["sectors"]]
    all_sectors_match = all(
        row["center_match"] and row["low_match"] and row["high_match"]
        and all(pop["count_match"] and pop["mean_abs_error"] <= 1e-12 for pop in row["populations"].values())
        for row in sectors
    )

    dev_geometry = {int(row["scale"]): row["geometry"] for row in development["scales"]}
    j10 = float(dev_geometry[10]["median_joint_period"])
    j11 = float(dev_geometry[11]["median_joint_period"])
    j12 = float(measured_geometry["median_joint_period"])
    g10, g11 = j11 / j10, j12 / j11
    ridge = 2.0 * g10 / (g10 + g11)
    recorded_adult = expected["metrics"]["full_sqrt_adult_ridge"]
    adult_metric_checks = {
        "G11_abs_error": abs(g11 - float(recorded_adult["G11"])),
        "ridge_A_abs_error": abs(ridge - float(recorded_adult["ridge_A"])),
        "fill_abs_error": abs(j12 / (4 * 10**12) - float(recorded_adult["target_adult_fill"])),
    }

    target_curve = np.asarray(expected["target"]["curves"]["prime"]["means"], dtype=np.float64)
    development_curve = np.asarray(template["prime_template"], dtype=np.float64)
    measured_correlation = float(np.corrcoef(target_curve, development_curve)[0, 1])
    measured_rmse = float(np.sqrt(np.mean((target_curve - development_curve) ** 2)))
    recorded_phase = expected["metrics"]["phase_transfer"]
    phase_metric_checks = {
        "correlation_abs_error": abs(measured_correlation - float(recorded_phase["target_template_correlation"])),
        "rmse_abs_error": abs(measured_rmse - float(recorded_phase["target_template_rmse"])),
    }
    fixture = small_cycle_fixture()
    checks = {
        "all_frozen_hashes_match": all(row["match"] for row in hash_checks.values()),
        "geometry_matches": all(geometry_checks.values()),
        "all_16_sector_counts_and_means_match": all_sectors_match,
        "adult_metrics_match": all(value <= 1e-15 for value in adult_metric_checks.values()),
        "phase_metrics_match": all(value <= 1e-15 for value in phase_metric_checks.values()),
        "small_cycle_recovers_analytic_curve": fixture["curve_correlation"] >= 0.999 and fixture["curve_rmse"] <= 0.005,
    }
    result = {
        "test_id": "PN15/SQRT-CHILD-ADULT-RIDGE/v1",
        "validator": "independent bytearray prime sieve",
        "hash_checks": hash_checks,
        "geometry_checks": geometry_checks,
        "sector_checks": sectors,
        "adult_metric_checks": adult_metric_checks,
        "phase_metric_checks": phase_metric_checks,
        "small_cycle_fixture": fixture,
        "checks": checks,
        "passed": all(checks.values()),
        "passed_count": sum(checks.values()),
        "total_count": len(checks),
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": OUTPUT.name, "passed": result["passed"], "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
