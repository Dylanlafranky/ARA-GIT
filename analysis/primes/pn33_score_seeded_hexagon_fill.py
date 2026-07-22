"""Score frozen PN33 fill coordinates against raw prime-gap outcomes and controls."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL_FREEZE = HERE / "PN33_PROTOCOL_FREEZE_MANIFEST.json"
COORDINATE_FREEZE = HERE / "PN33_COORDINATE_FREEZE_MANIFEST.json"
COORDINATES = HERE / "PN33_SEEDED_HEXAGON_FILL_COORDINATES.csv"
SUMMARY = HERE / "PN33_SEEDED_HEXAGON_FILL_COORDINATE_SUMMARY.json"
PRIME_BINARY = HERE / "PN33_TARGET_PRIME_GATES_UINT32.bin"
SCORED_GAPS = HERE / "PN33_SEEDED_HEXAGON_FILL_SCORED_GAPS.csv.gz"
BOOTSTRAP_RATIOS = HERE / "PN33_SEEDED_HEXAGON_FILL_BOOTSTRAP_RATIOS.npy"
ORDER_CONTROLS = HERE / "PN33_SEEDED_HEXAGON_FILL_ORDER_BROKEN_LOG_MAE.npz"
BAND_SUMMARY = HERE / "PN33_SEEDED_HEXAGON_FILL_BANDS.csv"
RESULTS = HERE / "PN33_SEEDED_HEXAGON_FILL_RESULTS.json"

BOOTSTRAPS = 10_000
BOOTSTRAP_BLOCK = 64
BOOTSTRAP_SEED = 33_001
ORDER_PERMUTATIONS = 1_000
ORDER_SEED = 33_002
BAND_WIDTH = 0.25
BAND_CENTERS = np.arange(0.125, 2.0, 0.25, dtype=np.float64)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def rankdata(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)
    start = 0
    while start < len(values):
        end = start + 1
        while end < len(values) and values[order[end]] == values[order[start]]:
            end += 1
        ranks[order[start:end]] = (start + end - 1) / 2.0 + 1.0
        start = end
    return ranks


def spearman_order(values: np.ndarray) -> float:
    ranks = rankdata(values)
    return float(np.corrcoef(np.arange(1, len(values) + 1, dtype=np.float64), ranks)[0, 1])


def log_mae(observed: np.ndarray, predicted: np.ndarray) -> float:
    return float(np.mean(np.abs(np.log(observed) - np.log(predicted))))


def block_medians(values: np.ndarray, block: int) -> np.ndarray:
    """Medians of all overlapping contiguous blocks, processed in bounded chunks."""
    if len(values) < block:
        raise ValueError("endpoint band shorter than bootstrap block")
    windows = np.lib.stride_tricks.sliding_window_view(values, block)
    output = np.empty(len(windows), dtype=np.float64)
    chunk = 100_000
    for start in range(0, len(windows), chunk):
        stop = min(start + chunk, len(windows))
        output[start:stop] = np.median(windows[start:stop], axis=1)
    return output


def sampled_medians_from_distribution(
    rng: np.random.Generator,
    values: np.ndarray,
    draws: int,
    repetitions: int,
) -> np.ndarray:
    unique, counts = np.unique(values, return_counts=True)
    probabilities = counts / counts.sum()
    output = np.empty(repetitions, dtype=np.float64)
    first_rank = (draws - 1) // 2 + 1
    second_rank = draws // 2 + 1
    batch_size = 500
    for start in range(0, repetitions, batch_size):
        stop = min(start + batch_size, repetitions)
        samples = rng.multinomial(draws, probabilities, size=stop - start)
        cumulative = np.cumsum(samples, axis=1)
        first_index = np.argmax(cumulative >= first_rank, axis=1)
        second_index = np.argmax(cumulative >= second_rank, axis=1)
        output[start:stop] = (unique[first_index] + unique[second_index]) / 2.0
    return output


def moving_block_median_ratio(
    first: np.ndarray,
    final: np.ndarray,
) -> tuple[float, np.ndarray, tuple[float, float]]:
    first_blocks = block_medians(first, BOOTSTRAP_BLOCK)
    final_blocks = block_medians(final, BOOTSTRAP_BLOCK)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    first_draws = math.ceil(len(first) / BOOTSTRAP_BLOCK)
    final_draws = math.ceil(len(final) / BOOTSTRAP_BLOCK)
    first_boot = sampled_medians_from_distribution(rng, first_blocks, first_draws, BOOTSTRAPS)
    final_boot = sampled_medians_from_distribution(rng, final_blocks, final_draws, BOOTSTRAPS)
    ratios = final_boot / first_boot
    point = float(np.median(final) / np.median(first))
    interval = tuple(float(value) for value in np.quantile(ratios, [0.025, 0.975]))
    return point, ratios, interval


class RangeMedian:
    """Exact medians for many contiguous ranges using block-prefix histograms."""

    def __init__(self, values: np.ndarray, block_size: int = 4096) -> None:
        self.values = values.astype(np.int64, copy=False)
        self.block_size = block_size
        self.max_value = int(self.values.max())
        self.full_blocks = len(values) // block_size
        counts = np.zeros((self.full_blocks, self.max_value + 1), dtype=np.int32)
        for block in range(self.full_blocks):
            lo = block * block_size
            hi = lo + block_size
            counts[block] = np.bincount(self.values[lo:hi], minlength=self.max_value + 1)
        self.prefix = np.zeros((self.full_blocks + 1, self.max_value + 1), dtype=np.int64)
        np.cumsum(counts, axis=0, out=self.prefix[1:])

    def histogram(self, lo: int, hi: int) -> np.ndarray:
        if not 0 <= lo < hi <= len(self.values):
            raise ValueError((lo, hi, len(self.values)))
        first_full = (lo + self.block_size - 1) // self.block_size
        last_full = hi // self.block_size
        if first_full < last_full:
            histogram = self.prefix[last_full] - self.prefix[first_full]
            left_end = first_full * self.block_size
            right_start = last_full * self.block_size
            if lo < left_end:
                histogram = histogram + np.bincount(
                    self.values[lo:left_end], minlength=self.max_value + 1
                )
            if right_start < hi:
                histogram = histogram + np.bincount(
                    self.values[right_start:hi], minlength=self.max_value + 1
                )
            return histogram
        return np.bincount(self.values[lo:hi], minlength=self.max_value + 1)

    @staticmethod
    def median_from_histogram(histogram: np.ndarray) -> float:
        count = int(histogram.sum())
        cumulative = np.cumsum(histogram)
        first_rank = (count - 1) // 2 + 1
        second_rank = count // 2 + 1
        first = int(np.searchsorted(cumulative, first_rank, side="left"))
        second = int(np.searchsorted(cumulative, second_rank, side="left"))
        return (first + second) / 2.0

    def medians(self, boundaries: np.ndarray) -> np.ndarray:
        return np.array([
            self.median_from_histogram(self.histogram(int(boundaries[index]), int(boundaries[index + 1])))
            for index in range(len(boundaries) - 1)
        ], dtype=np.float64)


def summarize_band(gaps: np.ndarray, gates: np.ndarray, x: np.ndarray, band: int) -> dict:
    mask = band == np.minimum((x / BAND_WIDTH).astype(np.int16), 7)
    values = gaps[mask]
    gate_values = gates[mask]
    x_values = x[mask]
    quantiles = np.quantile(values, [0.10, 0.25, 0.50, 0.75, 0.90])
    return {
        "band": band,
        "x_low": band * BAND_WIDTH,
        "x_high": (band + 1) * BAND_WIDTH,
        "n": int(len(values)),
        "first_gate": int(gate_values[0]),
        "last_gate": int(gate_values[-1]),
        "mean_gap": float(np.mean(values)),
        "median_gap": float(quantiles[2]),
        "p10_gap": float(quantiles[0]),
        "q1_gap": float(quantiles[1]),
        "q3_gap": float(quantiles[3]),
        "p90_gap": float(quantiles[4]),
        "median_x": float(np.median(x_values)),
        "median_gate": float(np.median(gate_values)),
    }


def write_gap_rows(
    handle,
    baseline_id: int,
    previous: np.ndarray,
    gates: np.ndarray,
    gaps: np.ndarray,
    x: np.ndarray,
    bands: np.ndarray,
) -> None:
    chunk = 100_000
    for start in range(0, len(gaps), chunk):
        stop = min(start + chunk, len(gaps))
        matrix = np.column_stack((
            np.full(stop - start, baseline_id, dtype=np.int16),
            previous[start:stop],
            gates[start:stop],
            gaps[start:stop],
            x[start:stop],
            bands[start:stop],
        ))
        np.savetxt(handle, matrix, fmt=["%d", "%d", "%d", "%d", "%.12g", "%d"], delimiter=",")


def gate_count_control(gaps: np.ndarray) -> dict:
    boundaries = np.linspace(0, len(gaps), 9, dtype=np.int64)
    medians = np.array([np.median(gaps[boundaries[i]:boundaries[i + 1]]) for i in range(8)])
    observed = medians / medians[0]
    predicted = np.power(2.0, BAND_CENTERS / 2.0)
    predicted /= predicted[0]
    return {
        "band_medians": medians.tolist(),
        "normalized": observed.tolist(),
        "log_mae": log_mae(observed, predicted),
    }


def raw_double_control(primes: np.ndarray, baseline_index: int, baseline_prime: int) -> dict:
    end_index = int(np.searchsorted(primes, 2 * baseline_prime, side="right")) - 1
    local = primes[baseline_index:end_index + 1].astype(np.int64)
    gaps = np.diff(local)
    if len(gaps) < 8:
        return {"n": int(len(gaps)), "adequate": False}
    boundaries = np.linspace(0, len(gaps), 9, dtype=np.int64)
    medians = np.array([np.median(gaps[boundaries[i]:boundaries[i + 1]]) for i in range(8)])
    return {
        "n": int(len(gaps)),
        "adequate": bool(np.all(np.diff(boundaries) > 0)),
        "band_medians": medians.tolist(),
        "final_first_ratio": float(medians[-1] / medians[0]),
        "endpoint_n_below_500": bool((boundaries[1] - boundaries[0] < 500) or (boundaries[-1] - boundaries[-2] < 500)),
    }


def fixed_count_controls(gaps: np.ndarray) -> dict:
    output = {}
    for count in (6, 12, 24):
        if len(gaps) < count:
            output[str(count)] = {"adequate": False}
            continue
        selected = gaps[:count]
        midpoint = count // 2
        output[str(count)] = {
            "adequate_for_frozen_500_gap_endpoint": False,
            "first_half_median": float(np.median(selected[:midpoint])),
            "second_half_median": float(np.median(selected[midpoint:])),
            "second_first_ratio": float(np.median(selected[midpoint:]) / np.median(selected[:midpoint])),
        }
    return output


def order_broken_control(
    gaps: np.ndarray,
    increments: np.ndarray,
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    range_median = RangeMedian(gaps)
    threshold_logs = np.arange(1, 8, dtype=np.float64) * BAND_WIDTH * math.log(2.0) / 2.0
    predicted = np.power(2.0, BAND_CENTERS / 2.0)
    predicted /= predicted[0]
    errors = np.empty(ORDER_PERMUTATIONS, dtype=np.float64)
    for repetition in range(ORDER_PERMUTATIONS):
        permuted = rng.permutation(increments)
        cumulative = np.cumsum(permuted)
        internal = np.searchsorted(cumulative, threshold_logs, side="left") + 1
        boundaries = np.concatenate(([0], internal, [len(gaps)])).astype(np.int64)
        medians = range_median.medians(boundaries)
        normalized = medians / medians[0]
        errors[repetition] = log_mae(normalized, predicted)
    return {
        "permutations": ORDER_PERMUTATIONS,
        "seed": seed,
        "log_mae_mean": float(np.mean(errors)),
        "log_mae_median": float(np.median(errors)),
        "log_mae_p05": float(np.quantile(errors, 0.05)),
        "log_mae_p95": float(np.quantile(errors, 0.95)),
        "errors": errors,
    }


def main() -> None:
    for output in (SCORED_GAPS, BOOTSTRAP_RATIOS, ORDER_CONTROLS, BAND_SUMMARY, RESULTS):
        if output.exists():
            raise RuntimeError(f"refusing to overwrite {output.name}")

    protocol = json.loads(PROTOCOL_FREEZE.read_text(encoding="utf-8"))
    freeze = json.loads(COORDINATE_FREEZE.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    if sha256(COORDINATES) != freeze["coordinate_file_sha256"]:
        raise RuntimeError("coordinate hash mismatch")
    if sha256(SUMMARY) != freeze["coordinate_summary_sha256"]:
        raise RuntimeError("coordinate summary hash mismatch")
    if sha256(PRIME_BINARY) != freeze["prime_binary_sha256"]:
        raise RuntimeError("prime binary hash mismatch")
    if freeze["target_gap_summaries_calculated"]:
        raise RuntimeError("freeze manifest says gaps were already scored")

    primes = np.fromfile(PRIME_BINARY, dtype="<u4")
    if len(primes) != freeze["prime_binary_count"]:
        raise RuntimeError("prime binary count mismatch")
    prime_float = primes.astype(np.float64)
    cumulative_log_d = np.cumsum(np.log1p(1.0 / (prime_float - 1.0)))
    log_two = math.log(2.0)

    baseline_results = []
    band_rows = []
    bootstrap_primary = None
    order_arrays = {}
    baseline_ids = {"primary": 0, "scale_check_a": 1, "scale_check_b": 2}

    with gzip.open(SCORED_GAPS, "wt", encoding="utf-8", newline="") as handle:
        handle.write("baseline_id,previous_prime,prime_gate,gap,x,band\n")
        for item in summary["baselines"]:
            name = item["baseline_name"]
            baseline_index = int(item["baseline_prime_index"])
            completion_index = int(item["completion_prime_index"])
            previous = primes[baseline_index:completion_index].astype(np.int64)
            gates = primes[baseline_index + 1:completion_index + 1].astype(np.int64)
            gaps = gates - previous
            increments = np.log1p(1.0 / (gates.astype(np.float64) - 1.0))
            x = 2.0 * np.cumsum(increments) / log_two
            bands = np.minimum((x / BAND_WIDTH).astype(np.int16), 7)
            write_gap_rows(handle, baseline_ids[name], previous, gates, gaps, x, bands)

            stats = [summarize_band(gaps, gates, x, band) for band in range(8)]
            for row in stats:
                band_rows.append({"baseline_name": name, **row})
            medians = np.array([row["median_gap"] for row in stats], dtype=np.float64)
            median_x = np.array([row["median_x"] for row in stats], dtype=np.float64)
            median_gate = np.array([row["median_gate"] for row in stats], dtype=np.float64)
            observed_normalized = medians / medians[0]
            ara_predicted = np.power(2.0, median_x / 2.0)
            ara_predicted /= ara_predicted[0]
            pnt_predicted = np.log(median_gate) / math.log(item["baseline_prime"])
            pnt_predicted /= pnt_predicted[0]
            ara_error = log_mae(observed_normalized, ara_predicted)
            pnt_error = log_mae(observed_normalized, pnt_predicted)
            flat_error = log_mae(observed_normalized, np.ones(8, dtype=np.float64))
            correlation = spearman_order(medians)

            point_ratio, bootstrap_ratios, interval = moving_block_median_ratio(
                gaps[bands == 0], gaps[bands == 7]
            )
            if name == "primary":
                bootstrap_primary = bootstrap_ratios

            order = order_broken_control(gaps, increments, ORDER_SEED + baseline_ids[name])
            order_arrays[name] = order.pop("errors")
            order_p = (1 + int(np.count_nonzero(order_arrays[name] <= ara_error))) / (ORDER_PERMUTATIONS + 1)
            order["intact_ara_log_mae"] = ara_error
            order["one_sided_p_intact_better"] = order_p

            reset_pass = bool(
                item["next_generation_local_x"] < 0.25
                and item["next_generation_retained_ratio"] >= 2.0
            )
            endpoint_adequate = stats[0]["n"] >= 500 and stats[7]["n"] >= 500
            doubling_contains_two = interval[0] <= 2.0 <= interval[1]
            doubling_excludes_one = interval[0] > 1.0
            baseline_result = {
                "baseline_name": name,
                "anchor": item["anchor"],
                "baseline_prime": item["baseline_prime"],
                "seed_prime": item["seed_prime"],
                "seed_x": item["seed_x"],
                "completion_prime": item["completion_prime"],
                "completion_x": item["completion_x"],
                "completion_ratio": item["completion_ratio"],
                "completion_overshoot": item["completion_overshoot"],
                "next_generation_seed": item["next_generation_seed"],
                "next_generation_local_x": item["next_generation_local_x"],
                "next_generation_retained_ratio": item["next_generation_retained_ratio"],
                "seed_child_square": item["seed_child_square"],
                "seed_child_square_x": item["seed_child_square_x"],
                "nearest_phi_prime": item["nearest_phi_prime"],
                "nearest_phi_x": item["nearest_phi_x"],
                "gap_count": int(len(gaps)),
                "bands": stats,
                "observed_normalized_band_medians": observed_normalized.tolist(),
                "ara_predicted_normalized": ara_predicted.tolist(),
                "pnt_predicted_normalized": pnt_predicted.tolist(),
                "spearman_band_median_gap": correlation,
                "endpoint_final_first_median_ratio": point_ratio,
                "endpoint_bootstrap_95_ci": list(interval),
                "endpoint_adequate": endpoint_adequate,
                "doubling_contains_two": doubling_contains_two,
                "doubling_excludes_one": doubling_excludes_one,
                "ara_log_mae": ara_error,
                "pnt_log_mae": pnt_error,
                "flat_log_mae": flat_error,
                "ara_vs_pnt_error_ratio": ara_error / pnt_error if pnt_error else None,
                "gate_count_control": gate_count_control(gaps),
                "raw_integer_doubling_control": raw_double_control(primes, baseline_index, item["baseline_prime"]),
                "fixed_polygon_count_controls": fixed_count_controls(gaps),
                "order_broken_control": order,
                "reset_pass": reset_pass,
            }
            baseline_results.append(baseline_result)

    if bootstrap_primary is None:
        raise RuntimeError("primary bootstrap missing")
    np.save(BOOTSTRAP_RATIOS, bootstrap_primary)
    np.savez_compressed(ORDER_CONTROLS, **order_arrays)

    with BAND_SUMMARY.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = list(band_rows[0])
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(band_rows)

    primary = next(item for item in baseline_results if item["baseline_name"] == "primary")
    scale_checks = [item for item in baseline_results if item["baseline_name"] != "primary"]
    direction_pass = primary["spearman_band_median_gap"] > 0
    scale_direction_pass = all(item["spearman_band_median_gap"] > 0 for item in scale_checks)
    doubling_pass = (
        primary["endpoint_adequate"]
        and primary["doubling_contains_two"]
        and primary["doubling_excludes_one"]
    )
    curve_pass = primary["ara_log_mae"] <= 1.05 * primary["pnt_log_mae"]
    residual_support = (
        primary["ara_log_mae"] <= 0.95 * primary["pnt_log_mae"]
        and scale_direction_pass
    )
    support = direction_pass and doubling_pass and curve_pass and scale_direction_pass
    closer_to_two = abs(primary["endpoint_final_first_median_ratio"] - 2.0) < abs(
        primary["endpoint_final_first_median_ratio"] - 1.0
    )
    if not primary["endpoint_adequate"]:
        status = "INCONCLUSIVE"
    elif support:
        status = "SUPPORTED SPACING EXPRESSION"
    elif direction_pass and closer_to_two:
        status = "SUGGESTIVE"
    elif primary["spearman_band_median_gap"] <= 0 or (
        not primary["doubling_contains_two"] and not closer_to_two
    ):
        status = "NOT SUPPORTED"
    else:
        status = "NULL"

    payload = {
        "test_id": "PN33/SEEDED-HEXAGON-FILL/v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "coordinate_freeze_sha256": sha256(COORDINATE_FREEZE),
        "scored_gap_file": SCORED_GAPS.name,
        "scored_gap_file_sha256": sha256(SCORED_GAPS),
        "bootstrap_file": BOOTSTRAP_RATIOS.name,
        "bootstrap_file_sha256": sha256(BOOTSTRAP_RATIOS),
        "order_control_file": ORDER_CONTROLS.name,
        "order_control_file_sha256": sha256(ORDER_CONTROLS),
        "band_summary_file": BAND_SUMMARY.name,
        "band_summary_file_sha256": sha256(BAND_SUMMARY),
        "methods": {
            "bootstrap": "10,000 resamples of all overlapping 64-gap block medians; empirical multinomial resampling",
            "bootstrap_seed": BOOTSTRAP_SEED,
            "order_broken_permutations": ORDER_PERMUTATIONS,
            "order_seed": ORDER_SEED,
            "gap_assignment": "gap ending at each newly added prime gate",
            "outcomes_scored_after_coordinate_freeze": True,
        },
        "baselines": baseline_results,
        "decision": {
            "status": status,
            "primary_direction_pass": direction_pass,
            "primary_doubling_pass": doubling_pass,
            "primary_curve_within_5pct_of_pnt": curve_pass,
            "scale_checks_same_direction": scale_direction_pass,
            "ara_specific_residual_support": residual_support,
            "reset_pass": primary["reset_pass"],
            "prime_generator_tested": False,
            "literal_spatial_hexagon_proved": False,
            "phi_causation_tested": False,
        },
    }
    RESULTS.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": status,
        "primary": {
            "baseline": primary["baseline_prime"],
            "completion": primary["completion_prime"],
            "gap_count": primary["gap_count"],
            "spearman": primary["spearman_band_median_gap"],
            "final_first_ratio": primary["endpoint_final_first_median_ratio"],
            "bootstrap_95_ci": primary["endpoint_bootstrap_95_ci"],
            "ara_log_mae": primary["ara_log_mae"],
            "pnt_log_mae": primary["pnt_log_mae"],
            "order_broken_p": primary["order_broken_control"]["one_sided_p_intact_better"],
        },
        "scale_check_spearman": {
            item["baseline_name"]: item["spearman_band_median_gap"] for item in scale_checks
        },
        "scored_gap_sha256": payload["scored_gap_file_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()

