"""PN39: prepare a time-ordered raster of individual prime child ARA fields."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from pn10b_child_phase_prime_ranking import base_primes, segmented_least_prime_factor


HERE = Path(__file__).resolve().parent
LOW = 4_000_000_000
HIGH = 4_001_000_000
WINDOW_START = 0
WINDOW_SIZE = 512
BINS = 160
OUTPUT = HERE / "PN39_INDIVIDUAL_PRIME_CHILD_RASTER.json"


def main() -> None:
    numbers, least_factor = segmented_least_prime_factor(LOW, HIGH)
    all_parents = numbers[least_factor == 0].astype(np.int64)
    parents = all_parents[WINDOW_START : WINDOW_START + WINDOW_SIZE]
    gates = base_primes(int(math.isqrt(int(parents[-1]))))

    rows: list[list[int]] = []
    child_counts: list[int] = []
    centroids: list[float] = []
    occupied_bins: list[int] = []
    minimum_a: list[float] = []
    maximum_a: list[float] = []

    for parent_value in parents:
        parent = int(parent_value)
        eligible = gates[gates.astype(np.int64) * gates.astype(np.int64) <= parent].astype(np.int64)
        remainders = parent % eligible
        if np.any(remainders == 0):
            raise AssertionError(f"prime parent {parent} closed a lower gate")
        bin_index = np.minimum((remainders * BINS) // eligible, BINS - 1)
        histogram = np.bincount(bin_index, minlength=BINS).astype(np.int64)
        phase_a = 2.0 * remainders.astype(np.float64) / eligible

        rows.append([int(value) for value in histogram])
        child_counts.append(int(eligible.size))
        centroids.append(float(np.mean(phase_a)))
        occupied_bins.append(int(np.count_nonzero(histogram)))
        minimum_a.append(float(np.min(phase_a)))
        maximum_a.append(float(np.max(phase_a)))

    matrix = np.asarray(rows, dtype=np.int64)
    if not np.all(matrix.sum(axis=1) == np.asarray(child_counts)):
        raise AssertionError("row totals do not match child counts")

    residual = matrix.astype(np.float64) - matrix.mean(axis=1, keepdims=True)

    def lag_correlation(lag: int) -> dict[str, float | int]:
        left = residual[:-lag]
        right = residual[lag:]
        numerator = np.sum(left * right, axis=1)
        denominator = np.linalg.norm(left, axis=1) * np.linalg.norm(right, axis=1)
        correlations = numerator / denominator
        return {
            "lag": lag,
            "pair_count": int(correlations.size),
            "mean_residual_correlation": float(np.mean(correlations)),
            "median_residual_correlation": float(np.median(correlations)),
        }

    lag_diagnostics = [lag_correlation(lag) for lag in (1, 2, 3, 4, 5, 8, 13, 21, 34, 55, 89, 144, 233)]
    half = matrix.shape[0] // 2
    control_left = residual[:half]
    control_right = residual[half : half + half][::-1]
    control_correlation = np.sum(control_left * control_right, axis=1) / (
        np.linalg.norm(control_left, axis=1) * np.linalg.norm(control_right, axis=1)
    )

    payload = {
        "test": "PN39 individual-prime complete-child raster",
        "status": "descriptive opened-data window",
        "source_interval": {"low_inclusive": LOW, "high_exclusive": HIGH},
        "window": {
            "start_parent_index": WINDOW_START,
            "parent_count": int(parents.size),
            "first_prime": int(parents[0]),
            "last_prime": int(parents[-1]),
        },
        "ara_bins": BINS,
        "bin_width": 2.0 / BINS,
        "prime_values": [int(value) for value in parents],
        "child_counts": child_counts,
        "parent_centroids": centroids,
        "occupied_bins": occupied_bins,
        "minimum_child_a": minimum_a,
        "maximum_child_a": maximum_a,
        "histogram_rows": rows,
        "sequential_diagnostics": {
            "lag_correlations": lag_diagnostics,
            "parent_centroid_lag_1_correlation": float(np.corrcoef(centroids[:-1], centroids[1:])[0, 1]),
            "reversed_distant_half_control_mean_correlation": float(np.mean(control_correlation)),
            "reversed_distant_half_control_median_correlation": float(np.median(control_correlation)),
        },
        "checks": {
            "rows": int(matrix.shape[0]),
            "columns": int(matrix.shape[1]),
            "all_rows_reconcile": True,
            "minimum_cell_count": int(np.min(matrix)),
            "maximum_cell_count": int(np.max(matrix)),
        },
    }
    OUTPUT.write_text(json.dumps(payload, separators=(",", ":")) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "first_prime": int(parents[0]),
        "last_prime": int(parents[-1]),
        "parents": int(parents.size),
        "bins": BINS,
        "minimum_cell_count": int(np.min(matrix)),
        "maximum_cell_count": int(np.max(matrix)),
        "mean_occupied_bins": float(np.mean(occupied_bins)),
        "adjacent_residual_correlation": lag_diagnostics[0]["mean_residual_correlation"],
        "parent_centroid_lag_1_correlation": float(np.corrcoef(centroids[:-1], centroids[1:])[0, 1]),
    }, indent=2))


if __name__ == "__main__":
    main()
