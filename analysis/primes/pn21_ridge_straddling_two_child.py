"""PN21 ridge-straddling two-child retention test.

Development-only.  The supplied 87-bit target is not present or evaluated.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "PN21_RIDGE_STRADDLING_TWO_CHILD_RESULTS.json"
LOW = 4_000_000_000
HIGH = 4_001_000_000
MID = (LOW + HIGH) // 2
GRID_BINS = 32
PARENT_BINS = 16


def prime_table(limit: int) -> np.ndarray:
    flags = np.ones(limit + 1, dtype=np.bool_)
    flags[:2] = False
    for value in range(2, math.isqrt(limit) + 1):
        if flags[value]:
            flags[value * value : limit + 1 : value] = False
    return np.flatnonzero(flags).astype(np.int64)


def segmented_least_prime_factor(low: int, high: int, primes: np.ndarray) -> np.ndarray:
    size = high - low
    least = np.zeros(size, dtype=np.int32)
    for prime_value in primes:
        prime = int(prime_value)
        if prime * prime >= high:
            break
        start = max(prime * prime, ((low + prime - 1) // prime) * prime)
        offsets = np.arange(start - low, size, prime, dtype=np.int64)
        empty = least[offsets] == 0
        least[offsets[empty]] = prime
    return least


def phase_pair(numbers: np.ndarray, q_a: np.ndarray, q_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    phase_a = 2.0 * np.remainder(numbers, q_a) / q_a
    phase_b = 2.0 - 2.0 * np.remainder(numbers, q_b) / q_b
    return phase_a, phase_b


def grid_cells(phase_a: np.ndarray, phase_b: np.ndarray) -> np.ndarray:
    bin_a = np.minimum((phase_a * GRID_BINS / 2.0).astype(np.int64), GRID_BINS - 1)
    bin_b = np.minimum((phase_b * GRID_BINS / 2.0).astype(np.int64), GRID_BINS - 1)
    return bin_a * GRID_BINS + bin_b


def heldout_retention(
    parent: np.ndarray,
    phase_a: np.ndarray,
    phase_b: np.ndarray,
    train: np.ndarray,
    test: np.ndarray,
) -> dict:
    cells = grid_cells(phase_a, phase_b)
    cell_count = GRID_BINS * GRID_BINS
    sums = np.bincount(cells[train], weights=parent[train], minlength=cell_count)
    counts = np.bincount(cells[train], minlength=cell_count)
    global_mean = float(parent[train].mean())
    means = np.full(cell_count, global_mean, dtype=np.float64)
    occupied = counts > 0
    means[occupied] = sums[occupied] / counts[occupied]
    prediction = means[cells[test]]
    mse = float(np.mean((parent[test] - prediction) ** 2))
    baseline_mse = float(np.mean((parent[test] - global_mean) ** 2))
    retained_r2 = 1.0 - mse / baseline_mse
    return {
        "grid_bins_per_axis": GRID_BINS,
        "occupied_training_cells": int(occupied.sum()),
        "training_global_parent_mean": global_mean,
        "test_mse": mse,
        "test_global_mean_baseline_mse": baseline_mse,
        "heldout_retained_r2": retained_r2,
        "heldout_retained_percent": 100.0 * retained_r2,
    }


def average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(values.size, dtype=np.float64)
    start = 0
    while start < values.size:
        stop = start + 1
        while stop < values.size and sorted_values[stop] == sorted_values[start]:
            stop += 1
        average = (start + 1 + stop) / 2.0
        ranks[order[start:stop]] = average
        start = stop
    return ranks


def auc(labels: np.ndarray, scores: np.ndarray) -> float:
    positive = labels.astype(bool)
    n_positive = int(positive.sum())
    n_negative = int(labels.size - n_positive)
    ranks = average_ranks(scores)
    rank_sum = float(ranks[positive].sum())
    return (rank_sum - n_positive * (n_positive + 1) / 2.0) / (n_positive * n_negative)


def normalized_mutual_information(parent: np.ndarray, cells: np.ndarray) -> dict:
    parent_cell = np.minimum((parent * PARENT_BINS).astype(np.int64), PARENT_BINS - 1)
    state_count = GRID_BINS * GRID_BINS
    joint_index = cells * PARENT_BINS + parent_cell
    joint = np.bincount(joint_index, minlength=state_count * PARENT_BINS).reshape(state_count, PARENT_BINS)
    total = float(parent.size)
    joint_probability = joint / total
    state_probability = joint_probability.sum(axis=1)
    parent_probability = joint_probability.sum(axis=0)
    mutual_information = 0.0
    nonzero_state, nonzero_parent = np.nonzero(joint)
    for state, parent_bin in zip(nonzero_state, nonzero_parent):
        probability = joint_probability[state, parent_bin]
        mutual_information += probability * math.log2(
            probability / (state_probability[state] * parent_probability[parent_bin])
        )
    parent_entropy = -sum(
        probability * math.log2(probability)
        for probability in parent_probability
        if probability > 0
    )
    return {
        "parent_bins": PARENT_BINS,
        "mutual_information_bits": mutual_information,
        "parent_entropy_bits": parent_entropy,
        "normalized_by_parent_entropy": mutual_information / parent_entropy,
    }


def pair_diagnostics(
    name: str,
    numbers: np.ndarray,
    parent: np.ndarray,
    labels: np.ndarray,
    phase_a: np.ndarray,
    phase_b: np.ndarray,
    train: np.ndarray,
    test: np.ndarray,
) -> dict:
    closure = (phase_a + phase_b) / 2.0
    joint_distance = np.abs(phase_a - 1.0) + np.abs(phase_b - 1.0)
    closure_score = -np.abs(closure - 1.0)
    joint_score = -joint_distance
    cutoff_closure = float(np.quantile(closure_score, 0.99))
    cutoff_joint = float(np.quantile(joint_score, 0.99))
    population_prime_rate = float(labels.mean())
    closure_top = closure_score >= cutoff_closure
    joint_top = joint_score >= cutoff_joint
    correlation = float(np.corrcoef(closure, parent)[0, 1])
    cells = grid_cells(phase_a, phase_b)
    retention = heldout_retention(parent, phase_a, phase_b, train, test)
    return {
        "name": name,
        "phase_a_summary": {
            "mean": float(phase_a.mean()),
            "minimum": float(phase_a.min()),
            "maximum": float(phase_a.max()),
        },
        "phase_b_summary": {
            "mean": float(phase_b.mean()),
            "minimum": float(phase_b.min()),
            "maximum": float(phase_b.max()),
        },
        "closure_summary": {
            "mean": float(closure.mean()),
            "standard_deviation": float(closure.std()),
            "pearson_with_full_parent": correlation,
        },
        "retention": retention,
        "prime_diagnostics": {
            "population_prime_rate": population_prime_rate,
            "joint_ridge_auc": auc(labels, joint_score),
            "closure_ridge_auc": auc(labels, closure_score),
            "joint_ridge_top_1pct_prime_rate": float(labels[joint_top].mean()),
            "joint_ridge_top_1pct_lift": float(labels[joint_top].mean() / population_prime_rate),
            "closure_ridge_top_1pct_prime_rate": float(labels[closure_top].mean()),
            "closure_ridge_top_1pct_lift": float(labels[closure_top].mean() / population_prime_rate),
        },
        "information": normalized_mutual_information(parent, cells),
        "exact_ridge_counts": {
            "phase_a_equals_1": int(np.count_nonzero(phase_a == 1.0)),
            "phase_b_equals_1": int(np.count_nonzero(phase_b == 1.0)),
            "closure_equals_1": int(np.count_nonzero(closure == 1.0)),
        },
        "worked_rows": [
            {
                "n": int(numbers[index]),
                "is_prime": bool(labels[index]),
                "parent": float(parent[index]),
                "phase_a": float(phase_a[index]),
                "phase_b": float(phase_b[index]),
                "closure": float(closure[index]),
            }
            for index in (0, 1, 2, numbers.size // 2, numbers.size - 3, numbers.size - 2, numbers.size - 1)
        ],
    }


def main() -> None:
    if OUTPUT.exists():
        raise RuntimeError("PN21 result already exists; refusing overwrite")
    primes = prime_table(math.isqrt(HIGH - 1) + 200)
    least_all = segmented_least_prime_factor(LOW, HIGH, primes)
    all_numbers = np.arange(LOW, HIGH, dtype=np.int64)
    odd_mask = (all_numbers & 1) == 1
    numbers = all_numbers[odd_mask]
    least = least_all[odd_mask]
    labels = least == 0
    parent = np.ones(numbers.size, dtype=np.float64)
    composite = ~labels
    parent[composite] = 2.0 * np.log(least[composite]) / np.log(numbers[composite])

    sqrt_floor = np.floor(np.sqrt(numbers)).astype(np.int64)
    insertion = np.searchsorted(primes, sqrt_floor, side="right")
    q_minus = primes[insertion - 1]
    q_plus = primes[insertion]
    q_second_minus = primes[insertion - 2]

    straddle_a, straddle_b = phase_pair(numbers, q_minus, q_plus)
    same_a, same_b = phase_pair(numbers, q_minus, q_second_minus)
    train = numbers < MID
    test = ~train

    straddling = pair_diagnostics(
        "ridge_straddling_q_minus_q_plus",
        numbers,
        parent,
        labels,
        straddle_a,
        straddle_b,
        train,
        test,
    )
    same_side = pair_diagnostics(
        "same_side_q_minus_q_second_minus",
        numbers,
        parent,
        labels,
        same_a,
        same_b,
        train,
        test,
    )
    retained = straddling["retention"]["heldout_retained_r2"]
    control_retained = same_side["retention"]["heldout_retained_r2"]
    threshold_pass = retained >= 0.90
    control_pass = retained > control_retained
    payload = {
        "test_id": "PN21/RIDGE-STRADDLING-TWO-CHILD-RETENTION/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": (
            "RETENTION PASS — decoder development warranted; fresh target still sealed"
            if threshold_pass and control_pass
            else "DEVELOPMENT NULL — fresh target remains sealed"
        ),
        "population": {
            "low_inclusive": LOW,
            "high_exclusive": HIGH,
            "odd_integer_count": int(numbers.size),
            "prime_count": int(labels.sum()),
            "composite_count": int(composite.sum()),
            "training_count": int(train.sum()),
            "test_count": int(test.sum()),
            "full_parent_definition": "1 for prime; 2log(least prime factor)/log(n) for composite",
        },
        "child_definition": {
            "phase_a": "2*(n mod q_minus)/q_minus; q_minus is last prime <= sqrt(n)",
            "phase_b": "2-2*(n mod q_plus)/q_plus; q_plus is first prime > sqrt(n)",
            "unique_q_minus": sorted({int(value) for value in q_minus}),
            "unique_q_plus": sorted({int(value) for value in q_plus}),
            "same_side_control_unique_second_minus": sorted({int(value) for value in q_second_minus}),
        },
        "frozen_threshold": {
            "heldout_retained_r2_required": 0.90,
            "must_exceed_same_side_control": True,
        },
        "straddling_pair": straddling,
        "same_side_control": same_side,
        "decision": {
            "straddling_heldout_retained_r2": retained,
            "same_side_heldout_retained_r2": control_retained,
            "retention_threshold_pass": threshold_pass,
            "exceeds_same_side_control": control_pass,
            "blind_target_authorized": False,
            "reason": (
                "A separate non-collapsing deterministic decoder must be frozen even after retention pass."
                if threshold_pass and control_pass
                else "The ridge-straddling pair did not retain 90% of the full parent coordinate out of sample."
            ),
        },
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "population": payload["population"],
        "straddling_retention": retained,
        "same_side_retention": control_retained,
        "straddling_prime_diagnostics": straddling["prime_diagnostics"],
    }, indent=2))


if __name__ == "__main__":
    main()
