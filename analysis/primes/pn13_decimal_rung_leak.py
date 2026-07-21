#!/usr/bin/env python3
"""PN13: test the frozen decimal-rung leak law on two prime ARA appearances.

Source data are deterministic integers and exact prime arithmetic. No download is
required. Target mode refuses to run unless the frozen source hashes match and the
explicit unlock token is supplied.

Arm A holds the 4,000-step aggregation size fixed while prime-ladder height moves
from 10^3 to 10^4 to 10^5. Arm B holds the one-million-integer interval and the
nine-child definition fixed while raw-number scale moves from 4e8 to 4e9 to 4e10.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from pn10b_child_phase_prime_ranking import base_primes, segmented_least_prime_factor


HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "PN13_TARGET_FREEZE_MANIFEST.json"
DEVELOPMENT_RESULTS = HERE / "PN13_DEVELOPMENT_RESULTS.json"
TARGET_RESULTS = HERE / "PN13_TARGET_RESULTS.json"
SUMMARY_CSV = HERE / "PN13_DECIMAL_RUNG_SUMMARY.csv"
TARGET_UNLOCK = "PN13_TARGET_FROZEN"
SEED = 13072126
K = 9
RAW_WIDTH = 1_000_000
RAW_BLOCKS = 100
BOOTSTRAPS = 5_000
VECTOR_STEPS = 4_000
VECTOR_WINDOWS = (1_000, 10_000, 100_000)
RAW_WINDOWS = {
    8: (400_000_000, 401_000_000),
    9: (4_000_000_000, 4_001_000_000),
    10: (40_000_000_000, 40_001_000_000),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest() -> None:
    frozen = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures: list[str] = []
    for name, expected in frozen["files"].items():
        path = HERE / name
        actual = sha256(path)
        if actual != expected:
            failures.append(f"{name}: expected {expected}, got {actual}")
    if failures:
        raise RuntimeError("PN13 target freeze mismatch:\n" + "\n".join(failures))


def first_n_primes(count: int) -> list[int]:
    if count < 1:
        return []
    if count < 6:
        limit = 15
    else:
        limit = int(count * (math.log(count) + math.log(math.log(count)))) + 100
    while True:
        sieve = bytearray(b"\x01") * (limit + 1)
        sieve[0:2] = b"\x00\x00"
        for number in range(2, math.isqrt(limit) + 1):
            if sieve[number]:
                start = number * number
                sieve[start : limit + 1 : number] = b"\x00" * (((limit - start) // number) + 1)
        primes = [index for index, is_prime in enumerate(sieve) if is_prime]
        if len(primes) >= count:
            return primes[:count]
        limit *= 2


def product_tree(values: Sequence[int]) -> int:
    """Balanced exact product; faster than a sequential primorial at high rungs."""
    level = list(values)
    if not level:
        return 1
    while len(level) > 1:
        level = [
            level[index] * level[index + 1] if index + 1 < len(level) else level[index]
            for index in range(0, len(level), 2)
        ]
    return level[0]


def circular_summary(turns: np.ndarray) -> dict[str, float]:
    angles = 2.0 * math.pi * turns
    cosine = float(np.mean(np.cos(angles)))
    sine = float(np.mean(np.sin(angles)))
    magnitude = math.hypot(cosine, sine)
    direction = (math.atan2(sine, cosine) / (2.0 * math.pi)) % 1.0
    return {
        "x": cosine,
        "y": sine,
        "resultant_length": magnitude,
        "direction_turn": direction,
        "direction_degrees": direction * 360.0,
    }


def circular_distance(first: float, second: float) -> float:
    difference = abs(first - second) % 1.0
    return min(difference, 1.0 - difference)


def phase_window(start_m: int, steps: int = VECTOR_STEPS) -> dict[str, Any]:
    primes = first_n_primes(start_m + steps + 1)
    parent = product_tree(primes[:start_m])
    phases = np.empty(steps + 1, dtype=np.float64)
    residues: list[int] = []
    for offset in range(steps + 1):
        m = start_m + offset
        next_prime = primes[m]
        residue = parent % next_prime
        phases[offset] = residue / next_prime
        if offset in (0, steps // 2, steps):
            residues.append(int(residue))
        if offset < steps:
            parent *= next_prime
    deltas = np.mod(phases[1:] - phases[:-1], 1.0)
    summary = circular_summary(deltas)
    block_vectors: list[dict[str, float]] = []
    for block in np.array_split(deltas, RAW_BLOCKS):
        block_vectors.append(circular_summary(block))
    return {
        "start_m": start_m,
        "end_m": start_m + steps - 1,
        "steps": steps,
        "phase_quantiles": {
            name: float(value)
            for name, value in zip(
                ("min", "p05", "p25", "median", "p75", "p95", "max"),
                np.quantile(phases, (0, 0.05, 0.25, 0.5, 0.75, 0.95, 1)),
            )
        },
        "increment_quantiles": {
            name: float(value)
            for name, value in zip(
                ("min", "p05", "p25", "median", "p75", "p95", "max"),
                np.quantile(deltas, (0, 0.05, 0.25, 0.5, 0.75, 0.95, 1)),
            )
        },
        "vector": summary,
        "sample_residues": residues,
        "block_vectors": block_vectors,
    }


def describe(values: np.ndarray) -> dict[str, float | int]:
    quantiles = np.quantile(values, (0, 0.05, 0.25, 0.5, 0.75, 0.95, 1))
    return {
        "n": int(len(values)),
        "mean": float(np.mean(values)),
        "sd": float(np.std(values)),
        "min": float(quantiles[0]),
        "p05": float(quantiles[1]),
        "p25": float(quantiles[2]),
        "median": float(quantiles[3]),
        "p75": float(quantiles[4]),
        "p95": float(quantiles[5]),
        "max": float(quantiles[6]),
    }


def child_couplings(numbers: np.ndarray, chunk_size: int = 100_000) -> tuple[np.ndarray, float]:
    thresholds = numbers.astype(np.float64) ** 0.45
    table = base_primes(int(math.ceil(float(np.max(thresholds)))) + 2)
    output = np.empty(len(numbers), dtype=np.float64)
    closure_error = 0.0
    for start in range(0, len(numbers), chunk_size):
        stop = min(start + chunk_size, len(numbers))
        n = numbers[start:stop]
        threshold = thresholds[start:stop]
        last = np.searchsorted(table, threshold, side="right") - 1
        indices = last[:, None] - np.arange(K, dtype=np.int64)[None, :]
        gates = table[indices]
        a = 2.0 * (n[:, None] % gates).astype(np.float64) / gates.astype(np.float64)
        b = 2.0 - a
        closure_error = max(closure_error, float(np.max(np.abs(a + b - 2.0))))
        signed = a - 1.0
        output[start:stop] = np.mean(signed[:, :-1] * signed[:, 1:], axis=1)
    return output, closure_error


def block_sums_counts(
    numbers: np.ndarray, values: np.ndarray, low: int
) -> tuple[list[float], list[int]]:
    width = RAW_WIDTH // RAW_BLOCKS
    indices = np.minimum((numbers - low) // width, RAW_BLOCKS - 1).astype(np.int64)
    sums = np.bincount(indices, weights=values, minlength=RAW_BLOCKS)
    counts = np.bincount(indices, minlength=RAW_BLOCKS)
    return [float(value) for value in sums], [int(value) for value in counts]


def raw_interval(scale: int) -> dict[str, Any]:
    low, high = RAW_WINDOWS[scale]
    numbers, least_factor = segmented_least_prime_factor(low, high)
    thresholds = numbers.astype(np.float64) ** 0.45
    primes_mask = least_factor == 0
    late_mask = (~primes_mask) & (least_factor.astype(np.float64) > thresholds)
    prime_numbers = numbers[primes_mask]
    late_numbers = numbers[late_mask]
    prime_values, prime_closure = child_couplings(prime_numbers)
    late_values, late_closure = child_couplings(late_numbers)
    prime_sums, prime_counts = block_sums_counts(prime_numbers, prime_values, low)
    late_sums, late_counts = block_sums_counts(late_numbers, late_values, low)
    return {
        "scale": scale,
        "low": low,
        "high": high,
        "raw_count": high - low,
        "prime": {
            "summary": describe(prime_values),
            "block_sums": prime_sums,
            "block_counts": prime_counts,
        },
        "late_composite": {
            "summary": describe(late_values),
            "block_sums": late_sums,
            "block_counts": late_counts,
        },
        "closure_max_abs_error": max(prime_closure, late_closure),
    }


def bootstrap_mean(block_sums: Sequence[float], block_counts: Sequence[int], rng: np.random.Generator) -> np.ndarray:
    sums = np.asarray(block_sums, dtype=np.float64)
    counts = np.asarray(block_counts, dtype=np.float64)
    results = np.empty(BOOTSTRAPS, dtype=np.float64)
    for index in range(BOOTSTRAPS):
        chosen = rng.integers(0, len(sums), size=len(sums))
        results[index] = float(np.sum(sums[chosen]) / np.sum(counts[chosen]))
    return results


def interval_from_results(results: dict[str, Any], scale: int) -> dict[str, Any]:
    for row in results["raw_integer_arm"]["intervals"]:
        if row["scale"] == scale:
            return row
    raise KeyError(scale)


def uniform_vector_control(n: int = VECTOR_STEPS, simulations: int = 5_000) -> dict[str, float]:
    rng = np.random.default_rng(SEED + 900)
    values: list[float] = []
    chunk = 250
    for start in range(0, simulations, chunk):
        count = min(chunk, simulations - start)
        turns = rng.random((count, n))
        angles = 2.0 * math.pi * turns
        x = np.mean(np.cos(angles), axis=1)
        y = np.mean(np.sin(angles), axis=1)
        values.extend(np.hypot(x, y).tolist())
    array = np.asarray(values)
    return {
        "simulations": simulations,
        "mean": float(np.mean(array)),
        "p05": float(np.quantile(array, 0.05)),
        "p50": float(np.quantile(array, 0.50)),
        "p95": float(np.quantile(array, 0.95)),
        "p995": float(np.quantile(array, 0.995)),
        "analytic_mean": math.sqrt(math.pi) / (2.0 * math.sqrt(n)),
    }


def complex_from(vector: dict[str, float]) -> complex:
    return complex(vector["x"], vector["y"])


def arm_a_result(windows: list[dict[str, Any]]) -> dict[str, Any]:
    by_start = {row["start_m"]: row for row in windows}
    vectors = {key: complex_from(value["vector"]) for key, value in by_start.items()}
    anchor = vectors[1_000]
    first = vectors[10_000]
    second = vectors[100_000]
    ratio_1 = abs(first) / abs(anchor)
    ratio_2 = abs(second) / abs(first)
    direction_1 = circular_distance(by_start[10_000]["vector"]["direction_turn"], by_start[1_000]["vector"]["direction_turn"])
    direction_2 = circular_distance(by_start[100_000]["vector"]["direction_turn"], by_start[10_000]["vector"]["direction_turn"])
    checks = {
        "first_magnitude_ratio_0p075_to_0p125": 0.075 <= ratio_1 <= 0.125,
        "second_magnitude_ratio_0p075_to_0p125": 0.075 <= ratio_2 <= 0.125,
        "first_direction_within_9_degrees": direction_1 <= 0.025,
        "second_direction_within_9_degrees": direction_2 <= 0.025,
    }
    models = {
        "factor_ten": (anchor * 0.1, anchor * 0.01),
        "sqrt_ten": (anchor / math.sqrt(10.0), anchor / 10.0),
        "constant": (anchor, anchor),
        "zero": (0j, 0j),
    }
    errors = {
        name: float(abs(first - prediction_1) + abs(second - prediction_2))
        for name, (prediction_1, prediction_2) in models.items()
    }
    return {
        "windows": windows,
        "magnitude_ratios": {"10000_over_1000": ratio_1, "100000_over_10000": ratio_2},
        "direction_shifts_turns": {"1000_to_10000": direction_1, "10000_to_100000": direction_2},
        "direction_shifts_degrees": {"1000_to_10000": 360.0 * direction_1, "10000_to_100000": 360.0 * direction_2},
        "checks": checks,
        "verdict": "SUPPORTED" if all(checks.values()) else "NOT SUPPORTED",
        "model_complex_absolute_error_sum": errors,
        "uniform_fixed_n_control": uniform_vector_control(),
        "instrument": {
            "factor_ten_scalar_ratios": [abs(anchor * 0.1) / abs(anchor), abs(anchor * 0.01) / abs(anchor * 0.1)],
            "factor_ten_direction_shifts_turns": [0.0, 0.0],
        },
    }


def arm_b_result(development: dict[str, Any], target_interval: dict[str, Any]) -> dict[str, Any]:
    intervals = development["raw_integer_arm"]["intervals"] + [target_interval]
    by_scale = {row["scale"]: row for row in intervals}
    means = {scale: by_scale[scale]["prime"]["summary"]["mean"] for scale in (8, 9, 10)}
    ratio_89 = means[9] / means[8]
    ratio_910 = means[10] / means[9]
    rng = np.random.default_rng(SEED + 1000)
    boot9 = bootstrap_mean(by_scale[9]["prime"]["block_sums"], by_scale[9]["prime"]["block_counts"], rng)
    boot10 = bootstrap_mean(by_scale[10]["prime"]["block_sums"], by_scale[10]["prime"]["block_counts"], rng)
    ratio_boot = boot10 / boot9
    ratio_ci = [float(np.quantile(ratio_boot, 0.025)), float(np.quantile(ratio_boot, 0.975))]
    same_sign = all(value != 0.0 for value in means.values()) and len({math.copysign(1.0, value) for value in means.values()}) == 1
    prediction = means[9] / 10.0
    rivals = {
        "factor_ten": prediction,
        "sqrt_ten": means[9] / math.sqrt(10.0),
        "constant": means[9],
        "zero": 0.0,
    }
    target_errors = {name: abs(means[10] - value) for name, value in rivals.items()}
    factor_best = min(target_errors, key=target_errors.get) == "factor_ten"
    checks = {
        "same_nonzero_sign": same_sign,
        "ratio_8_to_9_0p075_to_0p125": 0.075 <= ratio_89 <= 0.125,
        "ratio_9_to_10_0p075_to_0p125": 0.075 <= ratio_910 <= 0.125,
        "target_ratio_ci_inside_0p05_to_0p15": ratio_ci[0] >= 0.05 and ratio_ci[1] <= 0.15,
        "factor_ten_best_fresh_target_rival": factor_best,
    }
    alpha = math.log(abs(means[9] / means[8])) / math.log(10.0) if means[8] and means[9] else float("nan")
    development_prediction = math.copysign(abs(means[9]) * (10.0**alpha), means[9])
    pi_predictions = {
        8: -(math.pi - 3.0),
        9: -(math.pi - 3.0) / 10.0,
        10: -(math.pi - 3.0) / 100.0,
    }
    pi_relative_errors = {scale: abs(means[scale] - pi_predictions[scale]) / abs(pi_predictions[scale]) for scale in (8, 9, 10)}
    pi_pass = same_sign and all(error <= 0.20 for error in pi_relative_errors.values())
    return {
        "intervals": intervals,
        "prime_means": {str(key): value for key, value in means.items()},
        "ratios": {"C9_over_C8": ratio_89, "C10_over_C9": ratio_910},
        "fresh_target_ratio_bootstrap_95_ci": ratio_ci,
        "rival_target_predictions": rivals,
        "rival_target_absolute_errors": target_errors,
        "development_fitted_power": {
            "exponent_per_decimal_rung": alpha,
            "target_prediction": development_prediction,
            "target_absolute_error": abs(means[10] - development_prediction),
        },
        "checks": checks,
        "verdict": "SUPPORTED" if all(checks.values()) else "NOT SUPPORTED",
        "fixed_pi_sequence": {
            "predictions": {str(key): value for key, value in pi_predictions.items()},
            "relative_errors": {str(key): value for key, value in pi_relative_errors.items()},
            "verdict": "SUPPORTED" if pi_pass else "NOT SUPPORTED",
        },
        "instrument": {
            "exact_scalar_sequence": [-0.14, -0.014, -0.0014],
            "ratios": [0.1, 0.1],
        },
    }


def write_summary_csv(result: dict[str, Any]) -> None:
    rows: list[dict[str, Any]] = []
    for window in result["prime_ladder_arm"]["windows"]:
        vector = window["vector"]
        rows.append(
            {
                "arm": "prime_ladder_vector",
                "rung": window["start_m"],
                "population": "all ladder steps",
                "n": window["steps"],
                "signed_value_x_or_mean": vector["x"],
                "signed_value_y": vector["y"],
                "magnitude": vector["resultant_length"],
                "direction_degrees": vector["direction_degrees"],
            }
        )
    for interval in result["raw_integer_arm"]["intervals"]:
        for population in ("prime", "late_composite"):
            summary = interval[population]["summary"]
            rows.append(
                {
                    "arm": "raw_integer_child_coupling",
                    "rung": interval["scale"],
                    "population": population,
                    "n": summary["n"],
                    "signed_value_x_or_mean": summary["mean"],
                    "signed_value_y": "",
                    "magnitude": abs(summary["mean"]),
                    "direction_degrees": "negative" if summary["mean"] < 0 else "positive",
                }
            )
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_development() -> None:
    result = {
        "test_id": "PN13/DECIMAL-RUNG-LEAK/v1",
        "stage": "development-plus-open-anchor",
        "raw_integer_arm": {
            "intervals": [raw_interval(8), raw_interval(9)],
            "note": "Scale 9 is the already-open PN10B anchor; scale 8 is the frozen reverse/development check.",
        },
    }
    DEVELOPMENT_RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {DEVELOPMENT_RESULTS.name}")


def run_target(unlock: str) -> None:
    if unlock != TARGET_UNLOCK:
        raise RuntimeError(f"Target is sealed; supply --unlock {TARGET_UNLOCK}")
    verify_manifest()
    if not DEVELOPMENT_RESULTS.exists():
        raise RuntimeError("Run --stage development before opening the target")
    development = json.loads(DEVELOPMENT_RESULTS.read_text(encoding="utf-8"))
    windows = [phase_window(start) for start in VECTOR_WINDOWS]
    target_interval = raw_interval(10)
    result = {
        "test_id": "PN13/DECIMAL-RUNG-LEAK/v1",
        "stage": "fresh-target",
        "manifest_verified": True,
        "excluded_exploratory_window": "prime-ladder rungs 50000..53999, viewed before the PN13 freeze",
        "prime_ladder_arm": arm_a_result(windows),
        "raw_integer_arm": arm_b_result(development, target_interval),
    }
    result["overall_universal_rule_verdict"] = (
        "SUPPORTED" if result["prime_ladder_arm"]["verdict"] == "SUPPORTED" and result["raw_integer_arm"]["verdict"] == "SUPPORTED" else "NOT SUPPORTED"
    )
    TARGET_RESULTS.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary_csv(result)
    print(f"Arm A: {result['prime_ladder_arm']['verdict']}")
    print(f"Arm B: {result['raw_integer_arm']['verdict']}")
    print(f"Fixed Pi sequence: {result['raw_integer_arm']['fixed_pi_sequence']['verdict']}")
    print(f"wrote {TARGET_RESULTS.name} and {SUMMARY_CSV.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "target"), required=True)
    parser.add_argument("--unlock", default="")
    args = parser.parse_args()
    if args.stage == "development":
        run_development()
    else:
        run_target(args.unlock)


if __name__ == "__main__":
    main()
