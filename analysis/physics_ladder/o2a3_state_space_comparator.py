#!/usr/bin/env python3
"""O2-A3: matched ARA fixed-lineage versus causal state-space tracking."""

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
from o2a2_time_stream_lineage import (
    construct_causal_methods,
    noisy_observations,
    odd_window,
    rms,
    score_series,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "O2A3_STATE_SPACE_COMPARATOR_PROTOCOL_v1_FROZEN.md"
PROTOCOL_RECEIPT = HERE / "O2A3_STATE_SPACE_COMPARATOR_PROTOCOL_v1_FROZEN.sha256"
FIDELITY = HERE / "O2A3_STATE_SPACE_COMPARATOR_FIDELITY_v1.md"
FIDELITY_RECEIPT = HERE / "O2A3_STATE_SPACE_COMPARATOR_FIDELITY_v1.sha256"
RESULTS_JSON = HERE / "O2A3_STATE_SPACE_COMPARATOR_RESULTS.json"
DEVELOPMENT_CSV = HERE / "O2A3_STATE_SPACE_COMPARATOR_DEVELOPMENT.csv"
TRIALS_CSV = HERE / "O2A3_STATE_SPACE_COMPARATOR_TRIALS.csv"
AGGREGATES_CSV = HERE / "O2A3_STATE_SPACE_COMPARATOR_AGGREGATES.csv"
WAVEFORMS_CSV = HERE / "O2A3_STATE_SPACE_COMPARATOR_WAVEFORMS.csv"

EXPECTED_PROTOCOL_SHA256 = "ab0b88bb9c966f2a72544015e13d724ee4aa577e99b573e01671dfa210063fc7"
EXPECTED_FIDELITY_SHA256 = "6435cbe421e6ff7f00b9cf9fef693445b34e2f1ac7643f6f977b94e17a1faf59"

ARA_DERIVATIVE_FRACTION = 0.04
ARA_HALF_LIFE_FRACTION = 0.02
CALIBRATION_FRACTION = 0.10
SNR_LEVELS = (24, 18, 12, 6, 0, -6)
DEVELOPMENT_REPLICATES = 12
TARGET_REPLICATES = 32
ALPHAS = (0.0, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1)
BETAS = (1e-10, 1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_hash(path: Path) -> str:
    return path.read_text(encoding="utf-8").split()[0].strip()


def robust_noise_variance(values: np.ndarray) -> float:
    """Estimate white measurement-noise variance from second differences."""

    values = np.asarray(values, dtype=float)
    second = np.diff(values, n=2)
    if second.size < 8:
        raise ValueError("Calibration prefix is too short.")
    centre = float(np.median(second))
    mad = float(np.median(np.abs(second - centre)))
    sigma = (mad / 0.6744897501960817) / np.sqrt(6.0)
    scale = max(float(np.std(values)), float(np.max(np.abs(values))), 1.0)
    floor = np.finfo(float).eps * scale**2
    return max(sigma**2, floor)


def causal_augmented_kalman(
    times: np.ndarray,
    q_observed: np.ndarray,
    g_observed: np.ndarray,
    alpha: float,
    beta: float,
    calibration_count: int,
) -> tuple[np.ndarray, dict[str, float]]:
    """Forward Kalman filter for q_dot = g + s with random-walk latent s."""

    times = np.asarray(times, dtype=float)
    q_observed = np.asarray(q_observed, dtype=float)
    g_observed = np.asarray(g_observed, dtype=float)
    step = float(times[1] - times[0])

    q_cal = q_observed[:calibration_count]
    g_cal = g_observed[:calibration_count]
    r_q = robust_noise_variance(q_cal)
    r_g = robust_noise_variance(g_cal)
    g_scale = max(
        float(np.std(g_cal)),
        float(np.sqrt(r_g)),
        np.finfo(float).eps,
    )
    q_process = 0.5 * step**2 * r_g + alpha * r_q
    s_process = beta * g_scale**2

    q_state = float(q_observed[0])
    s_state = 0.0
    p_qq = r_q
    p_qs = 0.0
    p_ss = g_scale**2
    estimate = np.empty_like(q_observed)
    estimate[0] = s_state

    for index in range(1, q_observed.size):
        g_midpoint = 0.5 * (g_observed[index - 1] + g_observed[index])
        q_predicted = q_state + step * (g_midpoint + s_state)
        s_predicted = s_state

        p_qq_predicted = (
            p_qq + 2.0 * step * p_qs + step**2 * p_ss + q_process
        )
        p_qs_predicted = p_qs + step * p_ss
        p_ss_predicted = p_ss + s_process

        innovation_variance = p_qq_predicted + r_q
        gain_q = p_qq_predicted / innovation_variance
        gain_s = p_qs_predicted / innovation_variance
        innovation = q_observed[index] - q_predicted

        q_state = q_predicted + gain_q * innovation
        s_state = s_predicted + gain_s * innovation
        p_qq = max((1.0 - gain_q) * p_qq_predicted, 0.0)
        p_qs = (1.0 - gain_q) * p_qs_predicted
        p_ss = max(p_ss_predicted - gain_s * p_qs_predicted, 0.0)
        estimate[index] = s_state

    return estimate, {
        "estimated_q_noise_variance": r_q,
        "estimated_g_noise_variance": r_g,
        "calibration_g_scale": g_scale,
        "q_process_variance": q_process,
        "s_process_variance": s_process,
    }


def score_start_index(model: dict) -> int:
    sample_count = int(np.asarray(model["times"]).size)
    calibration_count = int(np.ceil(CALIBRATION_FRACTION * sample_count))
    ara_start = odd_window(sample_count, ARA_DERIVATIVE_FRACTION) - 1
    return max(calibration_count, ara_start)


def ara_estimates(
    model: dict,
    q: np.ndarray,
    g: np.ndarray,
) -> tuple[dict[str, np.ndarray], np.ndarray, int]:
    methods, _, _, _, _ = construct_causal_methods(
        model,
        q,
        g,
        ARA_DERIVATIVE_FRACTION,
        ARA_HALF_LIFE_FRACTION,
    )
    ara_start = odd_window(model["times"].size, ARA_DERIVATIVE_FRACTION) - 1
    start = score_start_index(model)
    offset = start - ara_start
    aligned = {
        "ara_fixed_lineage": methods["fixed_time_lineage"][:, offset:],
        "repeated_reselection": methods["repeated_parent_reselection"][:, offset:],
        "compressed_parent": methods["compressed_parent"][:, offset:],
        "zero_other": methods["zero_other"][:, offset:],
    }
    return aligned, np.asarray(model["times"])[start:], start


def select_state_space_settings(model: dict) -> tuple[dict[str, float], list[dict]]:
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
        seed_label="O2A3_state_space_development_first_60_percent",
    )
    hidden = int(development["hidden_index"])
    start = score_start_index(development)
    calibration_count = int(np.ceil(CALIBRATION_FRACTION * limit))
    truth = np.asarray(development["native_other"])[start:, hidden]
    times = np.asarray(development["times"])[start:]

    rows: list[dict] = []
    candidates: list[tuple[float, float, float]] = []
    for alpha in ALPHAS:
        for beta in BETAS:
            correlations: list[float] = []
            nrmses: list[float] = []
            objectives: list[float] = []
            for replicate in range(DEVELOPMENT_REPLICATES):
                estimate, _ = causal_augmented_kalman(
                    development["times"],
                    q[replicate, :, hidden],
                    g[replicate, :, hidden],
                    alpha,
                    beta,
                    calibration_count,
                )
                score = score_series(estimate[start:], truth, times)
                correlations.append(score["correlation"])
                nrmses.append(score["nrmse"])
                objectives.append(
                    score["nrmse"] + 0.25 * (1.0 - score["correlation"])
                )
            objective = float(np.median(objectives))
            candidates.append((objective, alpha, beta))
            rows.append(
                {
                    "alpha": alpha,
                    "beta": beta,
                    "replicates": DEVELOPMENT_REPLICATES,
                    "median_correlation": float(np.median(correlations)),
                    "median_nrmse": float(np.median(nrmses)),
                    "selection_objective": objective,
                    "selected": 0,
                }
            )
    _, selected_alpha, selected_beta = min(candidates)
    for row in rows:
        if row["alpha"] == selected_alpha and row["beta"] == selected_beta:
            row["selected"] = 1
    return {"alpha": selected_alpha, "beta": selected_beta}, rows


def target_rows_for_condition(
    model: dict,
    snr_db: float,
    settings: dict[str, float],
) -> tuple[list[dict], list[dict]]:
    q, g = noisy_observations(
        model,
        snr_db=snr_db,
        replicates=TARGET_REPLICATES,
        seed_label="O2A3_fresh_state_space_target",
    )
    ara, scored_times, start = ara_estimates(model, q, g)
    hidden = int(model["hidden_index"])
    calibration_count = int(np.ceil(CALIBRATION_FRACTION * model["times"].size))
    truth = np.asarray(model["native_other"])[start:, hidden]
    kalman = np.empty_like(ara["ara_fixed_lineage"])
    diagnostics: list[dict[str, float]] = []
    for replicate in range(TARGET_REPLICATES):
        estimate, diagnostic = causal_augmented_kalman(
            model["times"],
            q[replicate, :, hidden],
            g[replicate, :, hidden],
            settings["alpha"],
            settings["beta"],
            calibration_count,
        )
        kalman[replicate] = estimate[start:]
        diagnostics.append(diagnostic)

    estimates = {**ara, "causal_state_space": kalman}
    rows: list[dict] = []
    for method, method_estimates in estimates.items():
        for replicate, estimate in enumerate(method_estimates):
            diagnostic = diagnostics[replicate] if method == "causal_state_space" else {}
            rows.append(
                {
                    "model": model["model"],
                    "domain": model["domain"],
                    "snr_db": snr_db,
                    "method": method,
                    "replicate": replicate,
                    "scored_samples": scored_times.size,
                    "declared_stream": model["identity_names"][hidden],
                    **score_series(estimate, truth, scored_times),
                    "estimated_q_noise_variance": diagnostic.get(
                        "estimated_q_noise_variance", ""
                    ),
                    "estimated_g_noise_variance": diagnostic.get(
                        "estimated_g_noise_variance", ""
                    ),
                }
            )

    waveforms: list[dict] = []
    if snr_db == 12:
        stride = max(1, scored_times.size // 200)
        for index in range(0, scored_times.size, stride):
            waveforms.append(
                {
                    "model": model["model"],
                    "replicate": 0,
                    "time": float(scored_times[index]),
                    "native": float(truth[index]),
                    "ara_fixed_lineage": float(ara["ara_fixed_lineage"][0, index]),
                    "causal_state_space": float(kalman[0, index]),
                    "repeated_reselection": float(
                        ara["repeated_reselection"][0, index]
                    ),
                    "compressed_parent": float(ara["compressed_parent"][0, index]),
                }
            )
    return rows, waveforms


def aggregate_trials(rows: list[dict]) -> list[dict]:
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["model"], row["snr_db"], row["method"])].append(row)
    metrics = ("sign_accuracy", "correlation", "nrmse", "integrated_error")
    output: list[dict] = []
    for (model, snr_db, method), items in groups.items():
        aggregate = {
            "model": model,
            "snr_db": snr_db,
            "method": method,
            "replicates": len(items),
        }
        for metric in metrics:
            values = np.asarray([item[metric] for item in items], dtype=float)
            aggregate[f"median_{metric}"] = float(np.median(values))
            aggregate[f"q05_{metric}"] = float(np.quantile(values, 0.05))
            aggregate[f"q95_{metric}"] = float(np.quantile(values, 0.95))
        output.append(aggregate)
    return sorted(output, key=lambda row: (row["model"], -row["snr_db"], row["method"]))


def method_metrics(rows: list[dict], method: str) -> dict[str, float]:
    selected = [row for row in rows if row["method"] == method]
    return {
        metric: float(np.median([row[metric] for row in selected]))
        for metric in ("correlation", "nrmse", "sign_accuracy", "integrated_error")
    }


def primary_verdict(rows: list[dict]) -> dict:
    primary = [
        row
        for row in rows
        if row["model"] == "Open two-level probability" and row["snr_db"] == 12
    ]
    ara = method_metrics(primary, "ara_fixed_lineage")
    kalman = method_metrics(primary, "causal_state_space")
    absolute_gates = {
        "correlation": ara["correlation"] >= 0.70,
        "nrmse": ara["nrmse"] <= 0.25,
        "sign_accuracy": ara["sign_accuracy"] >= 0.85,
        "integrated_error": ara["integrated_error"] <= 0.15,
    }
    absolute_status = (
        "GOOD ABSOLUTE TRACKING"
        if all(absolute_gates.values())
        else "NOT GOOD BY FROZEN ABSOLUTE GATES"
    )
    ara_nrmse_improvement = 1.0 - ara["nrmse"] / kalman["nrmse"]
    kalman_nrmse_improvement = 1.0 - kalman["nrmse"] / ara["nrmse"]
    correlation_difference = ara["correlation"] - kalman["correlation"]
    ara_advantage = (
        ara_nrmse_improvement >= 0.10
        and correlation_difference >= 0.05
        and ara["integrated_error"] <= 1.10 * kalman["integrated_error"]
    )
    kalman_advantage = (
        kalman_nrmse_improvement >= 0.10
        and -correlation_difference >= 0.05
        and kalman["integrated_error"] <= 1.10 * ara["integrated_error"]
    )
    tie = (
        abs(ara["nrmse"] / kalman["nrmse"] - 1.0) < 0.10
        and abs(correlation_difference) < 0.05
    )
    if ara_advantage:
        comparative_status = "ARA-SPECIFIC ADVANTAGE"
    elif kalman_advantage:
        comparative_status = "STATE-SPACE ADVANTAGE"
    elif tie:
        comparative_status = "STANDARD-RANGE TIE"
    else:
        comparative_status = "MIXED"

    paired = []
    for replicate in range(TARGET_REPLICATES):
        ara_row = next(
            row
            for row in primary
            if row["method"] == "ara_fixed_lineage"
            and row["replicate"] == replicate
        )
        kalman_row = next(
            row
            for row in primary
            if row["method"] == "causal_state_space"
            and row["replicate"] == replicate
        )
        paired.append(
            {
                "replicate": replicate,
                "correlation_gain_ara": ara_row["correlation"]
                - kalman_row["correlation"],
                "nrmse_reduction_ara": kalman_row["nrmse"] - ara_row["nrmse"],
                "integrated_error_reduction_ara": kalman_row["integrated_error"]
                - ara_row["integrated_error"],
            }
        )
    return {
        "absolute_status": absolute_status,
        "comparative_status": comparative_status,
        "absolute_gates": absolute_gates,
        "ara_metrics": ara,
        "state_space_metrics": kalman,
        "ara_nrmse_relative_improvement": ara_nrmse_improvement,
        "correlation_difference_ara_minus_state_space": correlation_difference,
        "paired_descriptive": {
            "replicates": TARGET_REPLICATES,
            "ara_correlation_win_rate": float(
                np.mean([item["correlation_gain_ara"] > 0 for item in paired])
            ),
            "ara_nrmse_win_rate": float(
                np.mean([item["nrmse_reduction_ara"] > 0 for item in paired])
            ),
            "median_paired_correlation_gain_ara": float(
                np.median([item["correlation_gain_ara"] for item in paired])
            ),
            "median_paired_nrmse_reduction_ara": float(
                np.median([item["nrmse_reduction_ara"] for item in paired])
            ),
            "median_paired_integrated_error_reduction_ara": float(
                np.median(
                    [item["integrated_error_reduction_ara"] for item in paired]
                )
            ),
        },
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
        raise RuntimeError(f"Fidelity changed after freeze: {fidelity_hash}")
    if receipt_hash(PROTOCOL_RECEIPT) != protocol_hash:
        raise RuntimeError("Protocol receipt mismatch")
    if receipt_hash(FIDELITY_RECEIPT) != fidelity_hash:
        raise RuntimeError("Fidelity receipt mismatch")

    development = simulate_classical()
    settings, development_rows = select_state_space_settings(development)
    targets = [simulate_quantum(), simulate_electromagnetic()]
    trial_rows: list[dict] = []
    waveform_rows: list[dict] = []
    for model in targets:
        for snr_db in SNR_LEVELS:
            rows, waveforms = target_rows_for_condition(model, snr_db, settings)
            trial_rows.extend(rows)
            waveform_rows.extend(waveforms)

    aggregates = aggregate_trials(trial_rows)
    verdict = primary_verdict(trial_rows)
    write_csv(DEVELOPMENT_CSV, development_rows)
    write_csv(TRIALS_CSV, trial_rows)
    write_csv(AGGREGATES_CSV, aggregates)
    write_csv(WAVEFORMS_CSV, waveform_rows)

    result = {
        "test": "O2-A3 ARA fixed lineage versus causal state-space tracking",
        "run_date": "2026-07-23",
        "protocol_sha256": protocol_hash,
        "fidelity_sha256": fidelity_hash,
        "state_space_settings": settings,
        "ara_settings": {
            "derivative_fraction": ARA_DERIVATIVE_FRACTION,
            "half_life_fraction": ARA_HALF_LIFE_FRACTION,
        },
        "primary_verdict": verdict,
        "trial_rows": len(trial_rows),
        "aggregate_rows": len(aggregates),
        "waveform_rows": len(waveform_rows),
        "scope_fence": (
            "Synthetic matched conditional tracking. Not evidence for pure quantum "
            "information, a hidden Phase B, perceptual uncoupling or a new quantum law."
        ),
    }
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"selected_state_space_settings": settings}, indent=2))
    print(json.dumps(verdict, indent=2))
    print(
        f"Wrote {len(trial_rows):,} trial rows, {len(aggregates):,} aggregates, "
        f"and {len(waveform_rows):,} waveform rows."
    )


if __name__ == "__main__":
    main()
