#!/usr/bin/env python3
"""O2-A2: conditional downstream tracking of a predeclared moving child.

Synthetic instrument test only. The frozen protocol is the authority:
O2A2_TIME_STREAM_LINEAGE_PROTOCOL_v1_FROZEN.md
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from ara_hidden_other_residual_test import (
    simulate_classical,
    simulate_electromagnetic,
    simulate_quantum,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "O2A2_TIME_STREAM_LINEAGE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_RECEIPT = HERE / "O2A2_TIME_STREAM_LINEAGE_PROTOCOL_v1_FROZEN.sha256"
FIDELITY = HERE / "O2A2_TIME_STREAM_LINEAGE_FIDELITY_v1.md"
FIDELITY_RECEIPT = HERE / "O2A2_TIME_STREAM_LINEAGE_FIDELITY_v1.sha256"
RESULTS_JSON = HERE / "O2A2_TIME_STREAM_LINEAGE_RESULTS.json"
DEVELOPMENT_CSV = HERE / "O2A2_TIME_STREAM_LINEAGE_DEVELOPMENT.csv"
TRIALS_CSV = HERE / "O2A2_TIME_STREAM_LINEAGE_TRIALS.csv"
AGGREGATES_CSV = HERE / "O2A2_TIME_STREAM_LINEAGE_AGGREGATES.csv"
WAVEFORMS_CSV = HERE / "O2A2_TIME_STREAM_LINEAGE_WAVEFORMS.csv"

EXPECTED_PROTOCOL_SHA256 = "bea32f164f3d2dd3f4df211c5f7bca5b630c390bff9a211b3916659e54f5f712"
EXPECTED_FIDELITY_SHA256 = "3437518df06a178a549b4cedddea119545e79f77f2763d908bd65c7e1967d777"

DERIVATIVE_FRACTIONS = (0.005, 0.010, 0.020, 0.040, 0.080)
HALF_LIFE_FRACTIONS = (0.0, 0.0005, 0.001, 0.002, 0.005, 0.010, 0.020, 0.040)
SNR_LEVELS = (24, 18, 12, 6, 0, -6)
DEVELOPMENT_REPLICATES = 8
TARGET_REPLICATES = 16
OFFLINE_WINDOW_FRACTION = 0.080

METHODS = (
    "fixed_time_lineage",
    "repeated_parent_reselection",
    "fixed_child_no_memory",
    "wrong_fixed_child",
    "compressed_parent",
    "zero_other",
    "offline_centered_child",
)

THRESHOLDS = {
    "correlation_min": 0.40,
    "nrmse_max": 0.35,
    "sign_accuracy_min": 0.75,
    "integrated_error_max": 0.35,
    "correlation_advantage_min": 0.10,
    "nrmse_relative_improvement_min": 0.10,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_hash(path: Path) -> str:
    return path.read_text(encoding="utf-8").split()[0].strip()


def stable_seed(*parts: object) -> int:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little") % (2**32)


def rms(values: np.ndarray, axis: int | None = None) -> np.ndarray | float:
    return np.sqrt(np.mean(np.square(values), axis=axis))


def odd_window(sample_count: int, fraction: float, minimum: int = 5) -> int:
    window = max(minimum, int(round(sample_count * fraction)))
    if window % 2 == 0:
        window += 1
    return min(window, sample_count if sample_count % 2 else sample_count - 1)


def unit_white_noise(length: int, rng: np.random.Generator) -> np.ndarray:
    values = rng.normal(size=length)
    values -= np.mean(values)
    return values / float(rms(values))


def channel_scales(values: np.ndarray, kind: str) -> np.ndarray:
    if kind == "stored":
        scales = rms(values - np.mean(values, axis=0), axis=0)
    elif kind == "transfer":
        scales = rms(values, axis=0)
    else:
        raise ValueError(kind)
    scales = np.asarray(scales, dtype=float)
    nonzero = scales[scales > np.finfo(float).eps]
    fallback = float(np.median(nonzero)) if nonzero.size else 1.0
    return np.where(scales > np.finfo(float).eps, scales, fallback)


def noisy_observations(
    model: dict,
    snr_db: float,
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
            stable_seed(
                "O2A2",
                seed_label,
                model["model"],
                "white",
                snr_db,
                "q_and_g",
                replicate,
            )
        )
        for channel in range(stored.shape[1]):
            q[replicate, :, channel] += (
                q_scales[channel] * multiplier * unit_white_noise(stored.shape[0], rng)
            )
        for channel in range(transfer.shape[1]):
            g[replicate, :, channel] += (
                g_scales[channel] * multiplier * unit_white_noise(transfer.shape[0], rng)
            )
    return q, g


def trailing_poly_derivative(
    values: np.ndarray,
    step: float,
    window: int,
    degree: int = 3,
) -> np.ndarray:
    """Causal polynomial slope at the current (right-edge) sample."""

    offsets = np.arange(-(window - 1), 1, dtype=float)
    design = np.column_stack([offsets**power for power in range(degree + 1)])
    weights = np.linalg.pinv(design)[1] / step
    output = np.full(values.shape, np.nan)
    for replicate in range(values.shape[0]):
        for channel in range(values.shape[2]):
            output[replicate, window - 1 :, channel] = np.convolve(
                values[replicate, :, channel], weights[::-1], mode="valid"
            )
    return output


def centered_poly_derivative(
    values: np.ndarray,
    step: float,
    window: int,
    degree: int = 3,
) -> np.ndarray:
    """Noncausal O2-A1-style offline reference."""

    half = window // 2
    offsets = np.arange(-half, half + 1, dtype=float)
    design = np.column_stack([offsets**power for power in range(degree + 1)])
    weights = np.linalg.pinv(design)[1] / step
    output = np.full(values.shape, np.nan)
    for replicate in range(values.shape[0]):
        for channel in range(values.shape[2]):
            output[replicate, half:-half, channel] = np.convolve(
                values[replicate, :, channel], weights[::-1], mode="valid"
            )
    return output


def ewma(values: np.ndarray, half_life_samples: int) -> np.ndarray:
    if half_life_samples <= 0:
        return values.copy()
    decay = 2.0 ** (-1.0 / float(half_life_samples))
    output = np.empty_like(values)
    output[:, 0, :] = values[:, 0, :]
    for index in range(1, values.shape[1]):
        output[:, index, :] = (
            decay * output[:, index - 1, :] + (1.0 - decay) * values[:, index, :]
        )
    return output


def half_life_samples(sample_count: int, fraction: float) -> int:
    if fraction == 0.0:
        return 0
    return max(1, int(round(sample_count * fraction)))


def correlation(estimate: np.ndarray, truth: np.ndarray) -> float:
    if np.std(estimate) == 0.0 or np.std(truth) == 0.0:
        return 0.0
    return float(np.corrcoef(estimate, truth)[0, 1])


def score_series(
    estimate: np.ndarray,
    truth: np.ndarray,
    times: np.ndarray,
) -> dict[str, float]:
    peak = float(np.max(np.abs(truth)))
    active = np.abs(truth) >= 0.05 * peak
    native_integral = float(np.trapezoid(truth, times))
    estimated_integral = float(np.trapezoid(estimate, times))
    return {
        "sign_accuracy": float(
            np.mean(np.sign(estimate[active]) == np.sign(truth[active]))
        ),
        "correlation": correlation(estimate, truth),
        "nrmse": float(rms(estimate - truth) / peak),
        "integrated_error": float(
            abs(estimated_integral - native_integral) / abs(native_integral)
        ),
    }


def construct_causal_methods(
    model: dict,
    q: np.ndarray,
    g: np.ndarray,
    derivative_fraction: float,
    half_life_fraction: float,
) -> tuple[dict[str, np.ndarray], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    times = np.asarray(model["times"], dtype=float)
    step = float(times[1] - times[0])
    window = odd_window(times.size, derivative_fraction)
    dq = trailing_poly_derivative(q, step, window)
    valid = np.all(np.isfinite(dq), axis=(0, 2))
    residual = dq[:, valid, :] - g[:, valid, :]
    scored_times = times[valid]
    native = np.asarray(model["native_other"], dtype=float)[valid]
    hidden_index = int(model["hidden_index"])
    truth = native[:, hidden_index]
    half_samples = half_life_samples(residual.shape[1], half_life_fraction)
    filtered = ewma(residual, half_samples)
    evidence = ewma(np.abs(residual), half_samples)
    selected = np.argmax(evidence, axis=2)
    reselected = np.take_along_axis(filtered, selected[:, :, None], axis=2)[:, :, 0]
    wrong_index = (hidden_index + 1) % residual.shape[2]
    methods = {
        "fixed_time_lineage": filtered[:, :, hidden_index],
        "repeated_parent_reselection": reselected,
        "fixed_child_no_memory": residual[:, :, hidden_index],
        "wrong_fixed_child": filtered[:, :, wrong_index],
        "compressed_parent": np.mean(filtered, axis=2),
        "zero_other": np.zeros((q.shape[0], residual.shape[1])),
    }
    return methods, selected, scored_times, truth, residual


def select_development_settings(model: dict) -> tuple[dict, list[dict]]:
    limit = int(np.floor(0.60 * model["times"].size))
    development = {
        **model,
        "times": model["times"][:limit],
        "stored": model["stored"][:limit],
        "net_internal": model["net_internal"][:limit],
        "native_other": model["native_other"][:limit],
    }
    q, g = noisy_observations(
        development,
        snr_db=12,
        replicates=DEVELOPMENT_REPLICATES,
        seed_label="development_first_60_percent",
    )
    rows: list[dict] = []
    candidates: list[tuple[float, float, float]] = []
    for derivative_fraction in DERIVATIVE_FRACTIONS:
        for half_fraction in HALF_LIFE_FRACTIONS:
            methods, _, times, truth, _ = construct_causal_methods(
                development,
                q,
                g,
                derivative_fraction,
                half_fraction,
            )
            correlations = []
            nrmses = []
            objectives = []
            for estimate in methods["fixed_time_lineage"]:
                score = score_series(estimate, truth, times)
                correlations.append(score["correlation"])
                nrmses.append(score["nrmse"])
                objectives.append(score["nrmse"] + 0.25 * (1.0 - score["correlation"]))
            objective = float(np.median(objectives))
            candidates.append((objective, derivative_fraction, half_fraction))
            rows.append(
                {
                    "derivative_fraction": derivative_fraction,
                    "derivative_window_samples": odd_window(limit, derivative_fraction),
                    "half_life_fraction": half_fraction,
                    "half_life_samples": half_life_samples(
                        limit - odd_window(limit, derivative_fraction) + 1,
                        half_fraction,
                    ),
                    "replicates": DEVELOPMENT_REPLICATES,
                    "median_correlation": float(np.median(correlations)),
                    "median_nrmse": float(np.median(nrmses)),
                    "selection_objective": objective,
                    "selected": 0,
                }
            )
    _, selected_derivative, selected_half = min(candidates)
    for row in rows:
        if (
            row["derivative_fraction"] == selected_derivative
            and row["half_life_fraction"] == selected_half
        ):
            row["selected"] = 1
    return {
        "derivative_fraction": selected_derivative,
        "half_life_fraction": selected_half,
    }, rows


def target_rows_for_condition(
    model: dict,
    snr_db: float,
    selected_settings: dict,
) -> tuple[list[dict], list[dict]]:
    q, g = noisy_observations(
        model,
        snr_db=snr_db,
        replicates=TARGET_REPLICATES,
        seed_label="fresh_target",
    )
    methods, selected, times, truth, _ = construct_causal_methods(
        model,
        q,
        g,
        selected_settings["derivative_fraction"],
        selected_settings["half_life_fraction"],
    )
    hidden_index = int(model["hidden_index"])
    rows: list[dict] = []
    for method, estimates in methods.items():
        for replicate, estimate in enumerate(estimates):
            score = score_series(estimate, truth, times)
            if method == "repeated_parent_reselection":
                occupancy = float(np.mean(selected[replicate] == hidden_index))
                switches = int(np.sum(selected[replicate, 1:] != selected[replicate, :-1]))
            else:
                occupancy = 1.0 if method == "fixed_time_lineage" else float("nan")
                switches = 0 if method == "fixed_time_lineage" else -1
            rows.append(
                {
                    "model": model["model"],
                    "domain": model["domain"],
                    "snr_db": snr_db,
                    "method": method,
                    "replicate": replicate,
                    "scored_samples": times.size,
                    "declared_stream": model["identity_names"][hidden_index],
                    **score,
                    "declared_child_occupancy": occupancy,
                    "switch_count": switches,
                }
            )

    # Required noncausal reference from O2-A1. It is not used in causal gates.
    step = float(model["times"][1] - model["times"][0])
    window = odd_window(model["times"].size, OFFLINE_WINDOW_FRACTION)
    dq_offline = centered_poly_derivative(q, step, window)
    valid = np.all(np.isfinite(dq_offline), axis=(0, 2))
    offline_times = model["times"][valid]
    offline_truth = model["native_other"][valid, hidden_index]
    offline = dq_offline[:, valid, hidden_index] - g[:, valid, hidden_index]
    for replicate, estimate in enumerate(offline):
        rows.append(
            {
                "model": model["model"],
                "domain": model["domain"],
                "snr_db": snr_db,
                "method": "offline_centered_child",
                "replicate": replicate,
                "scored_samples": offline_times.size,
                "declared_stream": model["identity_names"][hidden_index],
                **score_series(estimate, offline_truth, offline_times),
                "declared_child_occupancy": 1.0,
                "switch_count": 0,
            }
        )

    waveforms: list[dict] = []
    if snr_db == 12:
        replicate = 0
        fixed = methods["fixed_time_lineage"][replicate]
        reselected = methods["repeated_parent_reselection"][replicate]
        raw = methods["fixed_child_no_memory"][replicate]
        stride = max(1, times.size // 180)
        for index in range(0, times.size, stride):
            waveforms.append(
                {
                    "model": model["model"],
                    "time": float(times[index]),
                    "native": float(truth[index]),
                    "fixed_time_lineage": float(fixed[index]),
                    "repeated_parent_reselection": float(reselected[index]),
                    "fixed_child_no_memory": float(raw[index]),
                    "selected_child": model["identity_names"][int(selected[replicate, index])],
                }
            )
    return rows, waveforms


def aggregate_trials(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["model"], row["snr_db"], row["method"])].append(row)
    output: list[dict] = []
    metrics = (
        "sign_accuracy",
        "correlation",
        "nrmse",
        "integrated_error",
        "declared_child_occupancy",
        "switch_count",
    )
    for (model, snr, method), items in groups.items():
        aggregate = {
            "model": model,
            "snr_db": snr,
            "method": method,
            "replicates": len(items),
        }
        for metric in metrics:
            values = np.asarray([row[metric] for row in items], dtype=float)
            finite = values[np.isfinite(values)]
            if finite.size:
                aggregate[f"median_{metric}"] = float(np.median(finite))
                aggregate[f"q05_{metric}"] = float(np.quantile(finite, 0.05))
                aggregate[f"q95_{metric}"] = float(np.quantile(finite, 0.95))
            else:
                aggregate[f"median_{metric}"] = ""
                aggregate[f"q05_{metric}"] = ""
                aggregate[f"q95_{metric}"] = ""
        output.append(aggregate)
    return sorted(output, key=lambda row: (row["model"], -row["snr_db"], row["method"]))


def median_metric(rows: list[dict], method: str, metric: str) -> float:
    values = [row[metric] for row in rows if row["method"] == method]
    if not values:
        raise RuntimeError(f"No rows for {method} / {metric}")
    return float(np.median(values))


def primary_verdict(rows: list[dict]) -> dict:
    primary = [
        row
        for row in rows
        if row["snr_db"] == 12
        and row["model"] in ("Resistive capacitor coupling", "Open two-level probability")
    ]
    fixed_corr = median_metric(primary, "fixed_time_lineage", "correlation")
    fixed_nrmse = median_metric(primary, "fixed_time_lineage", "nrmse")
    fixed_sign = median_metric(primary, "fixed_time_lineage", "sign_accuracy")
    fixed_integral = median_metric(primary, "fixed_time_lineage", "integrated_error")
    reselect_corr = median_metric(primary, "repeated_parent_reselection", "correlation")
    reselect_nrmse = median_metric(primary, "repeated_parent_reselection", "nrmse")
    zero_nrmse = median_metric(primary, "zero_other", "nrmse")
    corr_advantage = fixed_corr - reselect_corr
    nrmse_improvement = 1.0 - fixed_nrmse / reselect_nrmse
    system_nrmse = {}
    for model in ("Resistive capacitor coupling", "Open two-level probability"):
        system_rows = [row for row in primary if row["model"] == model]
        system_nrmse[model] = {
            "fixed": median_metric(system_rows, "fixed_time_lineage", "nrmse"),
            "reselection": median_metric(
                system_rows, "repeated_parent_reselection", "nrmse"
            ),
        }
    gates = {
        "correlation": fixed_corr >= THRESHOLDS["correlation_min"],
        "nrmse": fixed_nrmse <= THRESHOLDS["nrmse_max"],
        "sign": fixed_sign >= THRESHOLDS["sign_accuracy_min"],
        "integrated_error": fixed_integral <= THRESHOLDS["integrated_error_max"],
        "correlation_advantage": corr_advantage
        >= THRESHOLDS["correlation_advantage_min"],
        "nrmse_relative_improvement": nrmse_improvement
        >= THRESHOLDS["nrmse_relative_improvement_min"],
        "beats_zero_other": fixed_nrmse < zero_nrmse,
        "beats_reselection_in_both_systems": all(
            values["fixed"] < values["reselection"] for values in system_nrmse.values()
        ),
    }
    absolute_names = ("correlation", "nrmse", "sign", "integrated_error")
    comparative_names = (
        "correlation_advantage",
        "nrmse_relative_improvement",
        "beats_zero_other",
        "beats_reselection_in_both_systems",
    )
    absolute_pass = all(gates[name] for name in absolute_names)
    comparative_pass = all(gates[name] for name in comparative_names)
    if all(gates.values()):
        status = "SUPPORTED"
    elif comparative_pass and not absolute_pass:
        status = "INCONCLUSIVE"
    else:
        status = "NOT SUPPORTED"
    metrics = {
        "target_runs_per_method": 32,
        "median_fixed_correlation": fixed_corr,
        "median_fixed_nrmse": fixed_nrmse,
        "median_fixed_sign_accuracy": fixed_sign,
        "median_fixed_integrated_error": fixed_integral,
        "median_reselection_correlation": reselect_corr,
        "median_reselection_nrmse": reselect_nrmse,
        "median_zero_other_nrmse": zero_nrmse,
        "correlation_advantage": corr_advantage,
        "nrmse_relative_improvement": nrmse_improvement,
        "system_nrmse": system_nrmse,
    }
    return {
        "status": status,
        "metrics": metrics,
        "thresholds": THRESHOLDS,
        "gates": gates,
        "absolute_pass": absolute_pass,
        "comparative_pass": comparative_pass,
        "passed_gates": sum(int(value) for value in gates.values()),
        "total_gates": len(gates),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    protocol_hash = sha256(PROTOCOL)
    fidelity_hash = sha256(FIDELITY)
    if protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"Protocol changed after freeze: {protocol_hash}")
    if fidelity_hash != EXPECTED_FIDELITY_SHA256:
        raise RuntimeError(f"Fidelity packet changed after freeze: {fidelity_hash}")
    if receipt_hash(PROTOCOL_RECEIPT) != protocol_hash:
        raise RuntimeError("Protocol receipt mismatch")
    if receipt_hash(FIDELITY_RECEIPT) != fidelity_hash:
        raise RuntimeError("Fidelity receipt mismatch")

    models = [simulate_classical(), simulate_electromagnetic(), simulate_quantum()]
    selected, development_rows = select_development_settings(models[0])

    target_rows: list[dict] = []
    waveform_rows: list[dict] = []
    for model in models:
        for snr_db in SNR_LEVELS:
            rows, waveforms = target_rows_for_condition(model, snr_db, selected)
            target_rows.extend(rows)
            waveform_rows.extend(waveforms)

    aggregates = aggregate_trials(target_rows)
    verdict = primary_verdict(target_rows)

    write_csv(DEVELOPMENT_CSV, development_rows)
    write_csv(TRIALS_CSV, target_rows)
    write_csv(AGGREGATES_CSV, aggregates)
    write_csv(WAVEFORMS_CSV, waveform_rows)

    result = {
        "test": "O2-A2 declared-child downstream time-stream lineage",
        "run_date": "2026-07-23",
        "orientation": "predeclared movement/traversal child followed downstream",
        "protocol_sha256": protocol_hash,
        "fidelity_sha256": fidelity_hash,
        "selected_settings": {
            **selected,
            "development_model": models[0]["model"],
            "development_fraction": 0.60,
            "development_replicates": DEVELOPMENT_REPLICATES,
            "target_replicates": TARGET_REPLICATES,
        },
        "primary_verdict": verdict,
        "trial_rows": len(target_rows),
        "aggregate_rows": len(aggregates),
        "waveform_rows": len(waveform_rows),
        "scope_fence": (
            "Synthetic conditional tracking of a known moving child. Not hidden-child discovery, "
            "upstream recursion, space-side information retention or forward physical prediction."
        ),
        "artifacts": {
            "development": DEVELOPMENT_CSV.name,
            "trials": TRIALS_CSV.name,
            "aggregates": AGGREGATES_CSV.name,
            "waveforms": WAVEFORMS_CSV.name,
        },
    }
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result["selected_settings"], indent=2))
    print(json.dumps(verdict, indent=2))
    print(
        f"Wrote {len(target_rows):,} trial rows, {len(aggregates):,} aggregates, "
        f"and {len(waveform_rows):,} waveform rows."
    )


if __name__ == "__main__":
    main()

