#!/usr/bin/env python3
"""O2-A1: robustness of the hidden-Other continuity residual under controlled noise.

Synthetic instrument test only. The frozen protocol is the authority:
O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_PROTOCOL_v1_FROZEN.md
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from ara_hidden_other_residual_test import (
    simulate_classical,
    simulate_electromagnetic,
    simulate_quantum,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_RECEIPT = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_PROTOCOL_v1_FROZEN.sha256"
RESULTS_JSON = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_RESULTS.json"
AGGREGATE_CSV = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_AGGREGATES.csv"
TRIALS_CSV_GZ = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_TRIALS.csv.gz"
WAVEFORM_CSV = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_WAVEFORMS.csv"
DEVELOPMENT_CSV = HERE / "O2A1_HIDDEN_OTHER_CONTROLLED_NOISE_DEVELOPMENT.csv"

EXPECTED_PROTOCOL_SHA256 = "d16485a828d4396e3ced05ce04fd7ca784a7e662fb9f6f46e078b83cb12add49"
WINDOW_FRACTIONS = (0.005, 0.010, 0.020, 0.040, 0.080)
SNR_LEVELS = (24, 18, 12, 6, 0, -6)
NOISE_FAMILIES = ("white", "ar1", "impulsive", "drift")
INJECTION_MODES = ("q_only", "g_only", "q_and_g")
METHODS = ("local_poly", "raw_fd", "moving_average_fd", "causal_local_linear")
TARGET_REPLICATES = 16
DEVELOPMENT_REPLICATES = 8
MISSING_FRACTIONS = (0.0025, 0.005, 0.01, 0.02, 0.05, 0.10)
JITTER_DT = (0.02, 0.05, 0.10, 0.25, 0.50, 1.00)

PRIMARY_THRESHOLDS = {
    "location_accuracy_min": 0.90,
    "median_sign_accuracy_min": 0.95,
    "median_correlation_min": 0.80,
    "median_nrmse_max": 0.50,
    "median_integrated_error_max": 0.35,
    "median_inactive_rms_fraction_max": 0.50,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_seed(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little") % (2**32)


def rms(values: np.ndarray, axis: int | None = None) -> np.ndarray | float:
    return np.sqrt(np.mean(np.square(values), axis=axis))


def odd_window(sample_count: int, fraction: float, minimum: int = 5) -> int:
    window = max(minimum, int(round(sample_count * fraction)))
    if window % 2 == 0:
        window += 1
    largest = sample_count - 1 if sample_count % 2 == 0 else sample_count
    return min(window, largest)


def batch_valid_convolution(values: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Linear valid convolution along time (axis 1), vectorized by FFT.

    This is an exact computational implementation of the frozen finite impulse
    response convolution, not a spectral feature transformation.
    """

    full_length = values.shape[1] + kernel.size - 1
    fft_length = 1 << (full_length - 1).bit_length()
    value_fft = np.fft.rfft(values, n=fft_length, axis=1)
    kernel_fft = np.fft.rfft(kernel, n=fft_length)
    full = np.fft.irfft(value_fft * kernel_fft[None, :, None], n=fft_length, axis=1)
    full = full[:, :full_length, :]
    return full[:, kernel.size - 1 : values.shape[1], :]


def centered_poly_derivative(values: np.ndarray, step: float, window: int) -> np.ndarray:
    half = window // 2
    offsets = np.arange(-half, half + 1, dtype=float)
    design = np.column_stack([offsets**power for power in range(4)])
    weights = np.linalg.pinv(design)[1] / step
    valid = batch_valid_convolution(values, weights[::-1])
    result = np.full(values.shape, np.nan)
    result[:, half : values.shape[1] - half, :] = valid
    return result


def raw_fourth_derivative(values: np.ndarray, step: float) -> np.ndarray:
    result = np.full(values.shape, np.nan)
    result[:, 2:-2, :] = (
        -values[:, 4:, :]
        + 8.0 * values[:, 3:-1, :]
        - 8.0 * values[:, 1:-3, :]
        + values[:, :-4, :]
    ) / (12.0 * step)
    return result


def moving_average_derivative(values: np.ndarray, step: float, window: int) -> np.ndarray:
    half = window // 2
    padded = np.pad(values, ((0, 0), (half, half), (0, 0)), mode="reflect")
    smoothed = batch_valid_convolution(padded, np.ones(window) / window)
    derivative = raw_fourth_derivative(smoothed, step)
    derivative[:, : half + 2, :] = np.nan
    derivative[:, -(half + 2) :, :] = np.nan
    return derivative


def causal_local_linear_derivative(values: np.ndarray, step: float, window: int) -> np.ndarray:
    offsets = np.arange(-(window - 1), 1, dtype=float)
    design = np.column_stack([np.ones(window), offsets])
    weights = np.linalg.pinv(design)[1] / step
    valid = batch_valid_convolution(values, weights[::-1])
    result = np.full(values.shape, np.nan)
    result[:, window - 1 :, :] = valid
    return result


def derivative(values: np.ndarray, step: float, method: str, fraction: float | None) -> np.ndarray:
    if method == "raw_fd":
        return raw_fourth_derivative(values, step)
    if fraction is None:
        raise ValueError(f"{method} requires a selected window fraction")
    window = odd_window(values.shape[1], fraction)
    if method == "local_poly":
        return centered_poly_derivative(values, step, window)
    if method == "moving_average_fd":
        return moving_average_derivative(values, step, window)
    if method == "causal_local_linear":
        return causal_local_linear_derivative(values, step, window)
    raise ValueError(f"Unknown method: {method}")


def unit_noise(length: int, family: str, rng: np.random.Generator) -> np.ndarray:
    if family == "white":
        values = rng.normal(size=length)
    elif family == "ar1":
        innovations = rng.normal(size=length)
        values = np.empty(length)
        values[0] = innovations[0]
        for index in range(1, length):
            values[index] = 0.95 * values[index - 1] + innovations[index]
    elif family == "impulsive":
        values = rng.normal(scale=0.25, size=length)
        count = max(1, int(round(0.01 * length)))
        indices = rng.choice(length, size=count, replace=False)
        values[indices] += rng.normal(scale=12.0, size=count)
    elif family == "drift":
        axis = np.linspace(-1.0, 1.0, length)
        slope, curve, amplitude, phase = rng.normal(size=4)
        values = (
            slope * axis
            + curve * (axis**2 - np.mean(axis**2))
            + amplitude * np.sin(np.pi * axis + phase)
        )
    else:
        raise ValueError(f"Unknown noise family: {family}")
    values = values - np.mean(values)
    scale = float(rms(values))
    if not np.isfinite(scale) or scale == 0.0:
        raise ValueError("Noise generator produced zero or invalid RMS")
    return values / scale


def channel_scales(values: np.ndarray, kind: str) -> np.ndarray:
    if kind == "stored":
        raw = rms(values - np.mean(values, axis=0), axis=0)
    elif kind == "transfer":
        raw = rms(values, axis=0)
    else:
        raise ValueError(kind)
    raw = np.asarray(raw, dtype=float)
    nonzero = raw[raw > np.finfo(float).eps]
    fallback = float(np.median(nonzero)) if nonzero.size else 1.0
    return np.where(raw > np.finfo(float).eps, raw, fallback)


def additive_batch(
    model: dict,
    family: str,
    snr_db: float,
    mode: str,
    replicates: int,
    seed_label: str,
) -> tuple[np.ndarray, np.ndarray]:
    stored = np.asarray(model["stored"], dtype=float)
    transfer = np.asarray(model["net_internal"], dtype=float)
    q = np.repeat(stored[None, :, :], replicates, axis=0)
    g = np.repeat(transfer[None, :, :], replicates, axis=0)
    q_scales = channel_scales(stored, "stored")
    g_scales = channel_scales(transfer, "transfer")
    multiplier = 10.0 ** (-float(snr_db) / 20.0)

    for replicate in range(replicates):
        rng = np.random.default_rng(
            stable_seed("O2A1", seed_label, model["model"], family, snr_db, mode, replicate)
        )
        if mode in ("q_only", "q_and_g"):
            for channel in range(stored.shape[1]):
                q[replicate, :, channel] += (
                    q_scales[channel] * multiplier * unit_noise(stored.shape[0], family, rng)
                )
        if mode in ("g_only", "q_and_g"):
            for channel in range(transfer.shape[1]):
                g[replicate, :, channel] += (
                    g_scales[channel]
                    * multiplier
                    * unit_noise(transfer.shape[0], family, rng)
                )
    return q, g


def structural_batch(
    model: dict,
    corruption: str,
    severity: float,
    replicates: int,
) -> tuple[np.ndarray, np.ndarray]:
    times = np.asarray(model["times"], dtype=float)
    stored = np.asarray(model["stored"], dtype=float)
    transfer = np.asarray(model["net_internal"], dtype=float)
    q = np.empty((replicates, *stored.shape))
    g = np.empty((replicates, *transfer.shape))
    step = float(times[1] - times[0])

    for replicate in range(replicates):
        rng = np.random.default_rng(
            stable_seed("O2A1", "structural", model["model"], corruption, severity, replicate)
        )
        if corruption == "missing_block":
            block = max(1, int(round(severity * times.size)))
            start = int(rng.integers(1, max(2, times.size - block - 1)))
            keep = np.ones(times.size, dtype=bool)
            keep[start : start + block] = False
            observed_times = times[keep]
            for channel in range(stored.shape[1]):
                q[replicate, :, channel] = np.interp(
                    times, observed_times, stored[keep, channel]
                )
            for channel in range(transfer.shape[1]):
                g[replicate, :, channel] = np.interp(
                    times, observed_times, transfer[keep, channel]
                )
        elif corruption == "timestamp_jitter":
            observed_times = times + rng.normal(scale=severity * step, size=times.size)
            observed_times[0] = times[0]
            observed_times[-1] = times[-1]
            order = np.argsort(observed_times)
            observed_times = observed_times[order]
            observed_times = np.maximum.accumulate(observed_times)
            for index in range(1, observed_times.size):
                if observed_times[index] <= observed_times[index - 1]:
                    observed_times[index] = observed_times[index - 1] + step * 1e-9
            for channel in range(stored.shape[1]):
                q[replicate, :, channel] = np.interp(
                    times, observed_times, stored[order, channel]
                )
            for channel in range(transfer.shape[1]):
                g[replicate, :, channel] = np.interp(
                    times, observed_times, transfer[order, channel]
                )
        else:
            raise ValueError(corruption)
    return q, g


def score_batch(
    model: dict,
    q: np.ndarray,
    g: np.ndarray,
    method: str,
    fraction: float | None,
    metadata: dict,
    return_hidden: bool = False,
) -> tuple[list[dict], np.ndarray | None, np.ndarray | None, np.ndarray | None]:
    times = np.asarray(model["times"], dtype=float)
    step = float(times[1] - times[0])
    native = np.asarray(model["native_other"], dtype=float)
    hidden_index = int(model["hidden_index"])
    dq = derivative(q, step, method, fraction)
    estimated = dq - g
    valid = np.all(np.isfinite(estimated), axis=(0, 2))
    scored_times = times[valid]
    native_scored = native[valid]
    estimated = estimated[:, valid, :]
    native_hidden = native_scored[:, hidden_index]
    native_peak = float(np.max(np.abs(native_hidden)))
    active = np.abs(native_hidden) >= 0.05 * native_peak
    native_integral = float(np.trapezoid(native_hidden, scored_times))
    zero_nrmse = float(rms(native_hidden) / native_peak)

    rows: list[dict] = []
    hidden_estimates: list[np.ndarray] = []
    for replicate in range(q.shape[0]):
        current = estimated[replicate]
        integrated_abs = np.trapezoid(np.abs(current), scored_times, axis=0)
        predicted_index = int(np.argmax(integrated_abs))
        hidden_estimated = current[:, hidden_index]
        hidden_estimates.append(hidden_estimated)
        sign_accuracy = float(
            np.mean(np.sign(hidden_estimated[active]) == np.sign(native_hidden[active]))
        )
        if np.std(hidden_estimated) == 0.0 or np.std(native_hidden) == 0.0:
            correlation = 0.0
        else:
            correlation = float(np.corrcoef(hidden_estimated, native_hidden)[0, 1])
        nrmse = float(rms(hidden_estimated - native_hidden) / native_peak)
        estimated_integral = float(np.trapezoid(hidden_estimated, scored_times))
        integrated_error = abs(estimated_integral - native_integral) / abs(native_integral)
        inactive_indices = [
            index for index in range(current.shape[1]) if index != hidden_index
        ]
        inactive_fraction = max(
            float(rms(current[:, index]) / native_peak) for index in inactive_indices
        )
        total = np.sum(current, axis=1)
        parent_each = total / current.shape[1]
        parent_nrmse = float(rms(parent_each - native_hidden) / native_peak)
        wrong_index = int(np.argmin(integrated_abs))
        wrong_nrmse = float(rms(current[:, wrong_index] - native_hidden) / native_peak)

        row = {
            **metadata,
            "model": model["model"],
            "domain": model["domain"],
            "method": method,
            "window_fraction": "" if fraction is None else fraction,
            "window_samples": "" if fraction is None else odd_window(times.size, fraction),
            "replicate": replicate,
            "scored_samples": int(scored_times.size),
            "native_location": model["identity_names"][hidden_index],
            "predicted_location": model["identity_names"][predicted_index],
            "location_correct": int(predicted_index == hidden_index),
            "sign_accuracy": sign_accuracy,
            "correlation": correlation,
            "nrmse": nrmse,
            "integrated_error": float(integrated_error),
            "inactive_rms_fraction": inactive_fraction,
            "zero_other_nrmse": zero_nrmse,
            "parent_only_nrmse": parent_nrmse,
            "wrong_location_nrmse": wrong_nrmse,
            "beats_zero_other": int(nrmse < zero_nrmse),
            "beats_parent_only": int(nrmse < parent_nrmse),
            "beats_wrong_location": int(nrmse < wrong_nrmse),
        }
        rows.append(row)

    if return_hidden:
        return rows, np.stack(hidden_estimates), native_hidden, active
    return rows, None, None, None


def select_windows(models: list[dict]) -> tuple[dict[str, float], list[dict]]:
    development = models[0]
    limit = int(math.floor(0.60 * development["times"].size))
    development_model = {
        **development,
        "times": development["times"][:limit],
        "stored": development["stored"][:limit],
        "net_internal": development["net_internal"][:limit],
        "native_other": development["native_other"][:limit],
    }
    q, g = additive_batch(
        development_model,
        family="white",
        snr_db=12,
        mode="q_and_g",
        replicates=DEVELOPMENT_REPLICATES,
        seed_label="development",
    )
    selected: dict[str, float] = {}
    development_rows: list[dict] = []
    for method in ("local_poly", "moving_average_fd", "causal_local_linear"):
        candidates: list[tuple[float, float]] = []
        for fraction in WINDOW_FRACTIONS:
            rows, _, _, _ = score_batch(
                development_model,
                q,
                g,
                method,
                fraction,
                {
                    "suite": "development",
                    "corruption": "white",
                    "injection_mode": "q_and_g",
                    "level": "12_dB",
                    "level_value": 12,
                },
            )
            objective_values = [
                row["nrmse"] + row["inactive_rms_fraction"] for row in rows
            ]
            objective = float(np.median(objective_values))
            candidates.append((objective, fraction))
            development_rows.append(
                {
                    "method": method,
                    "window_fraction": fraction,
                    "window_samples": odd_window(limit, fraction),
                    "replicates": DEVELOPMENT_REPLICATES,
                    "median_nrmse": float(np.median([row["nrmse"] for row in rows])),
                    "median_inactive_rms_fraction": float(
                        np.median([row["inactive_rms_fraction"] for row in rows])
                    ),
                    "selection_objective": objective,
                    "selected": 0,
                }
            )
        selected[method] = min(candidates)[1]
        for row in development_rows:
            if row["method"] == method and row["window_fraction"] == selected[method]:
                row["selected"] = 1
    return selected, development_rows


def empirical_coverage(
    estimates: np.ndarray | None,
    native: np.ndarray | None,
    active: np.ndarray | None,
) -> float:
    if estimates is None or native is None or active is None or estimates.shape[0] < 2:
        return float("nan")
    lower = np.quantile(estimates, 0.05, axis=0)
    upper = np.quantile(estimates, 0.95, axis=0)
    return float(np.mean((native[active] >= lower[active]) & (native[active] <= upper[active])))


def aggregate_trials(rows: list[dict], coverage_by_group: dict[tuple, float]) -> list[dict]:
    group_fields = (
        "suite",
        "model",
        "corruption",
        "injection_mode",
        "level",
        "level_value",
        "method",
        "window_fraction",
        "window_samples",
    )
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[tuple(row[field] for field in group_fields)].append(row)

    output: list[dict] = []
    metric_fields = (
        "sign_accuracy",
        "correlation",
        "nrmse",
        "integrated_error",
        "inactive_rms_fraction",
        "zero_other_nrmse",
        "parent_only_nrmse",
        "wrong_location_nrmse",
    )
    for key, items in groups.items():
        base = dict(zip(group_fields, key))
        aggregate = {
            **base,
            "replicates": len(items),
            "location_accuracy": float(np.mean([row["location_correct"] for row in items])),
            "beats_zero_other_rate": float(
                np.mean([row["beats_zero_other"] for row in items])
            ),
            "beats_parent_only_rate": float(
                np.mean([row["beats_parent_only"] for row in items])
            ),
            "beats_wrong_location_rate": float(
                np.mean([row["beats_wrong_location"] for row in items])
            ),
            "empirical_90_interval_coverage": coverage_by_group.get(key, float("nan")),
        }
        for field in metric_fields:
            values = np.asarray([row[field] for row in items], dtype=float)
            aggregate[f"median_{field}"] = float(np.median(values))
            aggregate[f"q05_{field}"] = float(np.quantile(values, 0.05))
            aggregate[f"q95_{field}"] = float(np.quantile(values, 0.95))
        output.append(aggregate)
    return sorted(
        output,
        key=lambda row: (
            row["suite"],
            row["model"],
            row["corruption"],
            row["injection_mode"],
            float(row["level_value"]),
            row["method"],
        ),
    )


def write_csv(path: Path, rows: list[dict], compressed: bool = False) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    opener = gzip.open if compressed else open
    kwargs = {"newline": "", "encoding": "utf-8"}
    with opener(path, "wt" if compressed else "w", **kwargs) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def primary_verdict(trials: list[dict]) -> dict:
    primary = [
        row
        for row in trials
        if row["suite"] == "additive"
        and row["model"] in ("Resistive capacitor coupling", "Open two-level probability")
        and row["corruption"] == "white"
        and row["injection_mode"] == "q_and_g"
        and row["level_value"] == 12
        and row["method"] == "local_poly"
    ]
    raw = [
        row
        for row in trials
        if row["suite"] == "additive"
        and row["model"] in ("Resistive capacitor coupling", "Open two-level probability")
        and row["corruption"] == "white"
        and row["injection_mode"] == "q_and_g"
        and row["level_value"] == 12
        and row["method"] == "raw_fd"
    ]
    if len(primary) != 32 or len(raw) != 32:
        raise RuntimeError(
            f"Primary rows malformed: local_poly={len(primary)}, raw_fd={len(raw)}"
        )
    metrics = {
        "target_runs": len(primary),
        "location_accuracy": float(np.mean([row["location_correct"] for row in primary])),
        "median_sign_accuracy": float(np.median([row["sign_accuracy"] for row in primary])),
        "median_correlation": float(np.median([row["correlation"] for row in primary])),
        "median_nrmse": float(np.median([row["nrmse"] for row in primary])),
        "median_integrated_error": float(
            np.median([row["integrated_error"] for row in primary])
        ),
        "median_inactive_rms_fraction": float(
            np.median([row["inactive_rms_fraction"] for row in primary])
        ),
        "raw_fd_median_nrmse": float(np.median([row["nrmse"] for row in raw])),
        "zero_other_median_nrmse": float(
            np.median([row["zero_other_nrmse"] for row in primary])
        ),
    }
    gates = {
        "location": metrics["location_accuracy"]
        >= PRIMARY_THRESHOLDS["location_accuracy_min"],
        "sign": metrics["median_sign_accuracy"]
        >= PRIMARY_THRESHOLDS["median_sign_accuracy_min"],
        "correlation": metrics["median_correlation"]
        >= PRIMARY_THRESHOLDS["median_correlation_min"],
        "nrmse": metrics["median_nrmse"] <= PRIMARY_THRESHOLDS["median_nrmse_max"],
        "integrated_error": metrics["median_integrated_error"]
        <= PRIMARY_THRESHOLDS["median_integrated_error_max"],
        "inactive_spill": metrics["median_inactive_rms_fraction"]
        <= PRIMARY_THRESHOLDS["median_inactive_rms_fraction_max"],
        "beats_raw_fd": metrics["median_nrmse"] < metrics["raw_fd_median_nrmse"],
        "beats_zero_other": metrics["median_nrmse"]
        < metrics["zero_other_median_nrmse"],
    }
    return {
        "status": "SUPPORTED" if all(gates.values()) else "NOT SUPPORTED",
        "metrics": metrics,
        "thresholds": PRIMARY_THRESHOLDS,
        "gates": gates,
        "passed_gates": sum(int(value) for value in gates.values()),
        "total_gates": len(gates),
    }


def noise_floor_summary(aggregates: list[dict]) -> list[dict]:
    output: list[dict] = []
    for model in ("Resistive capacitor coupling", "Open two-level probability"):
        rows = [
            row
            for row in aggregates
            if row["suite"] == "additive"
            and row["model"] == model
            and row["corruption"] == "white"
            and row["injection_mode"] == "q_and_g"
            and row["method"] == "local_poly"
        ]
        rows = sorted(rows, key=lambda row: -float(row["level_value"]))
        passing = []
        for row in rows:
            passed = (
                row["location_accuracy"] >= PRIMARY_THRESHOLDS["location_accuracy_min"]
                and row["median_sign_accuracy"]
                >= PRIMARY_THRESHOLDS["median_sign_accuracy_min"]
                and row["median_correlation"]
                >= PRIMARY_THRESHOLDS["median_correlation_min"]
                and row["median_nrmse"] <= PRIMARY_THRESHOLDS["median_nrmse_max"]
                and row["median_integrated_error"]
                <= PRIMARY_THRESHOLDS["median_integrated_error_max"]
                and row["median_inactive_rms_fraction"]
                <= PRIMARY_THRESHOLDS["median_inactive_rms_fraction_max"]
            )
            passing.append((int(row["level_value"]), passed))
        lowest = min((snr for snr, passed in passing if passed), default=None)
        first_fail = next((snr for snr, passed in passing if not passed), None)
        output.append(
            {
                "model": model,
                "lowest_passing_snr_db": lowest,
                "first_failure_descending_snr_db": first_fail,
                "per_snr": [{"snr_db": snr, "passed": passed} for snr, passed in passing],
            }
        )
    return output


def main() -> None:
    actual_protocol_hash = sha256(PROTOCOL)
    if actual_protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(
            f"Frozen protocol hash mismatch: {actual_protocol_hash} != "
            f"{EXPECTED_PROTOCOL_SHA256}"
        )
    receipt_hash = PROTOCOL_RECEIPT.read_text(encoding="utf-8").split()[0]
    if receipt_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Protocol receipt does not match embedded frozen hash")

    models = [simulate_classical(), simulate_electromagnetic(), simulate_quantum()]
    selected_windows, development_rows = select_windows(models)
    write_csv(DEVELOPMENT_CSV, development_rows)

    trials: list[dict] = []
    coverage_by_group: dict[tuple, float] = {}
    representative_rows: list[dict] = []

    for model in models:
        clean_q = np.asarray(model["stored"], dtype=float)[None, :, :]
        clean_g = np.asarray(model["net_internal"], dtype=float)[None, :, :]
        for method in METHODS:
            fraction = selected_windows.get(method)
            rows, estimates, native, active = score_batch(
                model,
                clean_q,
                clean_g,
                method,
                fraction,
                {
                    "suite": "clean",
                    "corruption": "none",
                    "injection_mode": "none",
                    "level": "clean",
                    "level_value": 999,
                },
                return_hidden=True,
            )
            trials.extend(rows)

        for family in NOISE_FAMILIES:
            for mode in INJECTION_MODES:
                for snr_db in SNR_LEVELS:
                    q, g = additive_batch(
                        model,
                        family,
                        snr_db,
                        mode,
                        TARGET_REPLICATES,
                        seed_label="target",
                    )
                    metadata = {
                        "suite": "additive",
                        "corruption": family,
                        "injection_mode": mode,
                        "level": f"{snr_db}_dB",
                        "level_value": snr_db,
                    }
                    for method in METHODS:
                        fraction = selected_windows.get(method)
                        want_hidden = method == "local_poly"
                        rows, estimates, native, active = score_batch(
                            model,
                            q,
                            g,
                            method,
                            fraction,
                            metadata,
                            return_hidden=want_hidden,
                        )
                        trials.extend(rows)
                        if want_hidden:
                            first = rows[0]
                            group_key = (
                                first["suite"],
                                first["model"],
                                first["corruption"],
                                first["injection_mode"],
                                first["level"],
                                first["level_value"],
                                first["method"],
                                first["window_fraction"],
                                first["window_samples"],
                            )
                            coverage_by_group[group_key] = empirical_coverage(
                                estimates, native, active
                            )
                            if (
                                model["model"]
                                in (
                                    "Resistive capacitor coupling",
                                    "Open two-level probability",
                                )
                                and family == "white"
                                and mode == "q_and_g"
                                and snr_db == 12
                            ):
                                valid_indices = np.flatnonzero(active)
                                selected_indices = np.unique(
                                    np.linspace(
                                        valid_indices[0],
                                        valid_indices[-1],
                                        181,
                                        dtype=int,
                                    )
                                )
                                for index in selected_indices:
                                    representative_rows.append(
                                        {
                                            "model": model["model"],
                                            "snr_db": snr_db,
                                            "noise_family": family,
                                            "injection_mode": mode,
                                            "replicate": 0,
                                            "relative_time_index": int(index),
                                            "native_other": float(native[index]),
                                            "estimated_other": float(estimates[0, index]),
                                            "absolute_error": float(
                                                abs(estimates[0, index] - native[index])
                                            ),
                                        }
                                    )

        for corruption, severities in (
            ("missing_block", MISSING_FRACTIONS),
            ("timestamp_jitter", JITTER_DT),
        ):
            for severity_index, severity in enumerate(severities):
                q, g = structural_batch(
                    model, corruption, severity, TARGET_REPLICATES
                )
                metadata = {
                    "suite": "structural",
                    "corruption": corruption,
                    "injection_mode": "q_and_g",
                    "level": f"severity_{severity_index + 1}",
                    "level_value": severity,
                }
                for method in METHODS:
                    fraction = selected_windows.get(method)
                    want_hidden = method == "local_poly"
                    rows, estimates, native, active = score_batch(
                        model,
                        q,
                        g,
                        method,
                        fraction,
                        metadata,
                        return_hidden=want_hidden,
                    )
                    trials.extend(rows)
                    if want_hidden:
                        first = rows[0]
                        group_key = (
                            first["suite"],
                            first["model"],
                            first["corruption"],
                            first["injection_mode"],
                            first["level"],
                            first["level_value"],
                            first["method"],
                            first["window_fraction"],
                            first["window_samples"],
                        )
                        coverage_by_group[group_key] = empirical_coverage(
                            estimates, native, active
                        )

    aggregates = aggregate_trials(trials, coverage_by_group)
    verdict = primary_verdict(trials)
    floors = noise_floor_summary(aggregates)

    write_csv(TRIALS_CSV_GZ, trials, compressed=True)
    write_csv(AGGREGATE_CSV, aggregates)
    write_csv(WAVEFORM_CSV, representative_rows)

    results = {
        "test": "O2-A1 hidden Other under controlled observation noise",
        "run_date": "2026-07-23",
        "protocol_sha256": actual_protocol_hash,
        "protocol_receipt_sha256": receipt_hash,
        "parent_operator": "s_hat_i = dq_i/dt - g_i",
        "selected_window_fractions": selected_windows,
        "selected_window_samples_by_model": {
            model["model"]: {
                method: (
                    None
                    if method == "raw_fd"
                    else odd_window(model["times"].size, selected_windows[method])
                )
                for method in METHODS
            }
            for model in models
        },
        "primary_verdict": verdict,
        "white_both_noise_floors": floors,
        "trial_rows": len(trials),
        "aggregate_rows": len(aggregates),
        "representative_waveform_rows": len(representative_rows),
        "scope_fence": (
            "Controlled synthetic diagnostic recovery only. This run observes storage "
            "change and therefore is not forward prediction or physical attribution "
            "in an open natural system."
        ),
        "artifacts": {
            "development": DEVELOPMENT_CSV.name,
            "trials_gzip": TRIALS_CSV_GZ.name,
            "aggregates": AGGREGATE_CSV.name,
            "waveforms": WAVEFORM_CSV.name,
        },
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

