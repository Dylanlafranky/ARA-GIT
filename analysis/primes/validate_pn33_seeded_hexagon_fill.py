"""Independent deterministic validation for PN33's frozen and scored artifacts."""

from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
COORDINATE_FREEZE = HERE / "PN33_COORDINATE_FREEZE_MANIFEST.json"
COORDINATE_SUMMARY = HERE / "PN33_SEEDED_HEXAGON_FILL_COORDINATE_SUMMARY.json"
PRIME_BINARY = HERE / "PN33_TARGET_PRIME_GATES_UINT32.bin"
RESULTS = HERE / "PN33_SEEDED_HEXAGON_FILL_RESULTS_VALIDATED.json"
BOOTSTRAP = HERE / "PN33_SEEDED_HEXAGON_FILL_BOOTSTRAP_RATIOS_CORRECTED.npy"
ORDER_CONTROL = HERE / "PN33_SEEDED_HEXAGON_FILL_ORDER_BROKEN_LOG_MAE.npz"
VALIDATION = HERE / "PN33_SEEDED_HEXAGON_FILL_VALIDATION.json"

BAND_WIDTH = 0.25
BAND_CENTERS = np.arange(0.125, 2.0, 0.25, dtype=np.float64)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def independent_sieve(limit: int) -> np.ndarray:
    sieve = np.ones(limit + 1, dtype=np.bool_)
    sieve[:2] = False
    for value in range(2, math.isqrt(limit) + 1):
        if sieve[value]:
            sieve[value * value:limit + 1:value] = False
    return np.flatnonzero(sieve).astype(np.uint32)


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(len(values), dtype=np.float64)
    start = 0
    while start < len(values):
        stop = start + 1
        while stop < len(values) and values[order[stop]] == values[order[start]]:
            stop += 1
        ranks[order[start:stop]] = (start + stop - 1) / 2.0 + 1.0
        start = stop
    return ranks


def spearman(values: np.ndarray) -> float:
    return float(np.corrcoef(np.arange(1, len(values) + 1), rankdata(values))[0, 1])


def log_mae(observed: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(np.log(observed) - np.log(predicted))))


def close(actual: float, expected: float, tolerance: float = 1e-12) -> bool:
    return bool(abs(actual - expected) <= tolerance * max(1.0, abs(expected)))


def main() -> None:
    if VALIDATION.exists():
        raise RuntimeError(f"refusing to overwrite {VALIDATION.name}")
    freeze = json.loads(COORDINATE_FREEZE.read_text(encoding="utf-8"))
    summary = json.loads(COORDINATE_SUMMARY.read_text(encoding="utf-8"))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    stored = np.fromfile(PRIME_BINARY, dtype="<u4")

    checks: dict[str, bool] = {}
    checks["coordinate_summary_hash"] = sha256(COORDINATE_SUMMARY) == freeze["coordinate_summary_sha256"]
    checks["prime_binary_hash"] = sha256(PRIME_BINARY) == freeze["prime_binary_sha256"]
    checks["prime_binary_count"] = len(stored) == freeze["prime_binary_count"]
    checks["prime_binary_strictly_increasing"] = bool(np.all(np.diff(stored.astype(np.int64)) > 0))

    # Full independent enumeration guards both primality and omitted-prime errors.
    independently_enumerated = independent_sieve(int(stored[-1]))
    checks["full_prime_enumeration_matches"] = bool(np.array_equal(stored, independently_enumerated))
    del independently_enumerated

    prime_float = stored.astype(np.float64)
    cumulative_log_d = np.cumsum(np.log1p(1.0 / (prime_float - 1.0)))
    log_two = math.log(2.0)
    baseline_checks = {}
    recomputed_metrics = {}
    for coordinate in summary["baselines"]:
        name = coordinate["baseline_name"]
        lo = int(coordinate["baseline_prime_index"])
        hi = int(coordinate["completion_prime_index"])
        local_logs = cumulative_log_d[lo + 1:] - cumulative_log_d[lo]
        recomputed_hi = lo + 1 + int(np.searchsorted(local_logs, log_two, side="left"))
        local_x_at_completion = 2.0 * (cumulative_log_d[hi] - cumulative_log_d[lo]) / log_two
        gates = stored[lo + 1:hi + 1].astype(np.int64)
        gaps = gates - stored[lo:hi].astype(np.int64)
        x = 2.0 * np.cumsum(np.log1p(1.0 / (gates.astype(np.float64) - 1.0))) / log_two
        bands = np.minimum((x / BAND_WIDTH).astype(np.int16), 7)
        medians = np.array([np.median(gaps[bands == band]) for band in range(8)], dtype=np.float64)
        median_x = np.array([np.median(x[bands == band]) for band in range(8)], dtype=np.float64)
        median_gates = np.array([np.median(gates[bands == band]) for band in range(8)], dtype=np.float64)
        observed = medians / medians[0]
        ara = np.power(2.0, median_x / 2.0)
        ara /= ara[0]
        pnt = np.log(median_gates) / math.log(int(coordinate["baseline_prime"]))
        pnt /= pnt[0]
        result = next(item for item in results["baselines"] if item["baseline_name"] == name)
        baseline_checks[name] = {
            "completion_is_first_crossing": recomputed_hi == hi,
            "completion_prime_matches": int(stored[recomputed_hi]) == int(coordinate["completion_prime"]),
            "completion_x_matches": close(local_x_at_completion, float(coordinate["completion_x"]), 1e-11),
            "band_medians_match": bool(np.array_equal(medians, np.asarray(result["observed_normalized_band_medians"]) * medians[0])),
            "spearman_matches": close(spearman(medians), float(result["spearman_band_median_gap"])),
            "ara_log_mae_matches": close(log_mae(observed, ara), float(result["ara_log_mae"])),
            "pnt_log_mae_matches": close(log_mae(observed, pnt), float(result["pnt_log_mae"])),
            "gap_count_matches": len(gaps) == int(result["gap_count"]),
        }
        recomputed_metrics[name] = {
            "completion_prime": int(stored[recomputed_hi]),
            "completion_x": float(local_x_at_completion),
            "band_medians": medians.tolist(),
            "spearman": spearman(medians),
            "ara_log_mae": log_mae(observed, ara),
            "pnt_log_mae": log_mae(observed, pnt),
        }

    ratios = np.load(BOOTSTRAP)
    ratio_interval = [float(value) for value in np.quantile(ratios, [0.025, 0.975])]
    primary = next(item for item in results["baselines"] if item["baseline_name"] == "primary")
    checks["bootstrap_repetitions"] = len(ratios) == 10_000
    checks["bootstrap_interval_matches"] = bool(np.allclose(ratio_interval, primary["endpoint_bootstrap_95_ci"]))
    checks["bootstrap_interval_contains_point"] = bool(
        ratio_interval[0] <= primary["endpoint_final_first_median_ratio"] <= ratio_interval[1]
    )
    checks["bootstrap_interval_contains_two"] = bool(ratio_interval[0] <= 2.0 <= ratio_interval[1])
    checks["bootstrap_interval_excludes_one"] = bool(ratio_interval[0] > 1.0)

    order = np.load(ORDER_CONTROL)
    order_checks = {}
    for name in ("primary", "scale_check_a", "scale_check_b"):
        values = order[name]
        result = next(item for item in results["baselines"] if item["baseline_name"] == name)
        expected_p = (1 + int(np.count_nonzero(values <= result["ara_log_mae"]))) / 1001
        order_checks[name] = {
            "permutation_count": len(values) == 1000,
            "reported_p_matches": close(expected_p, result["order_broken_control"]["one_sided_p_intact_better"]),
        }

    nested_pass = all(all(group.values()) for group in baseline_checks.values())
    order_pass = all(all(group.values()) for group in order_checks.values())
    all_pass = all(checks.values()) and nested_pass and order_pass
    payload = {
        "test_id": "PN33/SEEDED-HEXAGON-FILL/v1",
        "validated_utc": datetime.now(timezone.utc).isoformat(),
        "validator": "independent dense prime enumeration plus separate metric reconstruction",
        "results_file": RESULTS.name,
        "results_sha256": sha256(RESULTS),
        "all_checks_pass": all_pass,
        "checks": checks,
        "baseline_checks": baseline_checks,
        "order_control_checks": order_checks,
        "recomputed_metrics": recomputed_metrics,
        "corrected_bootstrap_interval": ratio_interval,
        "interpretive_guardrails": {
            "spacing_expression_supported_under_frozen_rule": results["status"] == "SUPPORTED SPACING EXPRESSION",
            "ara_specific_residual_support": results["decision"]["ara_specific_residual_support"],
            "prime_generator_tested": False,
            "literal_hexagon_tested": False,
            "phi_causation_tested": False,
        },
    }
    VALIDATION.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "all_checks_pass": all_pass,
        "full_prime_enumeration_matches": checks["full_prime_enumeration_matches"],
        "bootstrap_interval": ratio_interval,
        "result_status": results["status"],
        "ara_specific_residual_support": results["decision"]["ara_specific_residual_support"],
    }, indent=2))


if __name__ == "__main__":
    main()
