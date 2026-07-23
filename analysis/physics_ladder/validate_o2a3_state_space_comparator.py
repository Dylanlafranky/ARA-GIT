#!/usr/bin/env python3
"""Independent checks for O2-A3 state-space comparator outputs."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from ara_hidden_other_residual_test import simulate_electromagnetic, simulate_quantum
from o2a2_time_stream_lineage import noisy_observations, score_series
from o2a3_state_space_comparator import (
    ARA_DERIVATIVE_FRACTION,
    ARA_HALF_LIFE_FRACTION,
    CALIBRATION_FRACTION,
    EXPECTED_FIDELITY_SHA256,
    EXPECTED_PROTOCOL_SHA256,
    TARGET_REPLICATES,
    ara_estimates,
    robust_noise_variance,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "O2A3_STATE_SPACE_COMPARATOR_PROTOCOL_v1_FROZEN.md"
FIDELITY = HERE / "O2A3_STATE_SPACE_COMPARATOR_FIDELITY_v1.md"
RESULTS = HERE / "O2A3_STATE_SPACE_COMPARATOR_RESULTS.json"
DEVELOPMENT = HERE / "O2A3_STATE_SPACE_COMPARATOR_DEVELOPMENT.csv"
TRIALS = HERE / "O2A3_STATE_SPACE_COMPARATOR_TRIALS.csv"
AGGREGATES = HERE / "O2A3_STATE_SPACE_COMPARATOR_AGGREGATES.csv"
WAVEFORMS = HERE / "O2A3_STATE_SPACE_COMPARATOR_WAVEFORMS.csv"
VALIDATION = HERE / "O2A3_STATE_SPACE_COMPARATOR_VALIDATION.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def median_metric(rows: list[dict], method: str, metric: str) -> float:
    values = [
        float(row[metric])
        for row in rows
        if row["method"] == method
    ]
    return float(np.median(values))


def independent_kalman(
    times: np.ndarray,
    q_observed: np.ndarray,
    g_observed: np.ndarray,
    alpha: float,
    beta: float,
    calibration_count: int,
) -> np.ndarray:
    """Separate scalar implementation of the registered forward filter."""

    step = float(times[1] - times[0])
    r_q = robust_noise_variance(q_observed[:calibration_count])
    r_g = robust_noise_variance(g_observed[:calibration_count])
    g_scale = max(
        float(np.std(g_observed[:calibration_count])),
        float(np.sqrt(r_g)),
        np.finfo(float).eps,
    )
    q_process = 0.5 * step**2 * r_g + alpha * r_q
    s_process = beta * g_scale**2

    state = np.array([q_observed[0], 0.0], dtype=float)
    covariance = np.diag([r_q, g_scale**2])
    transition = np.array([[1.0, step], [0.0, 1.0]])
    observation = np.array([[1.0, 0.0]])
    process = np.diag([q_process, s_process])
    identity = np.eye(2)
    estimate = np.empty_like(q_observed)
    estimate[0] = state[1]

    for index in range(1, q_observed.size):
        midpoint_g = 0.5 * (g_observed[index - 1] + g_observed[index])
        state = transition @ state + np.array([step * midpoint_g, 0.0])
        covariance = transition @ covariance @ transition.T + process
        innovation = q_observed[index] - (observation @ state).item()
        innovation_variance = (
            observation @ covariance @ observation.T
        ).item() + r_q
        gain = (covariance @ observation.T)[:, 0] / innovation_variance
        state = state + gain * innovation
        covariance = (identity - np.outer(gain, observation[0])) @ covariance
        covariance = 0.5 * (covariance + covariance.T)
        estimate[index] = state[1]
    return estimate


def bootstrap_interval(
    values: np.ndarray,
    seed: int,
    draws: int = 20_000,
) -> list[float]:
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, values.size, size=(draws, values.size))
    medians = np.median(values[indices], axis=1)
    return [float(np.quantile(medians, 0.05)), float(np.quantile(medians, 0.95))]


def main() -> None:
    checks: list[dict] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    protocol_hash = sha256(PROTOCOL)
    fidelity_hash = sha256(FIDELITY)
    check("protocol_hash", protocol_hash == EXPECTED_PROTOCOL_SHA256, protocol_hash)
    check("fidelity_hash", fidelity_hash == EXPECTED_FIDELITY_SHA256, fidelity_hash)

    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    trials = read_csv(TRIALS)
    development = read_csv(DEVELOPMENT)
    aggregates = read_csv(AGGREGATES)
    waveforms = read_csv(WAVEFORMS)
    check(
        "artifact_row_counts",
        len(trials) == 1920 and len(development) == 63
        and len(aggregates) == 60 and len(waveforms) == 405,
        {
            "trials": len(trials),
            "development": len(development),
            "aggregates": len(aggregates),
            "waveforms": len(waveforms),
        },
    )

    selected = [row for row in development if row["selected"] == "1"]
    selected_settings = {
        "alpha": float(selected[0]["alpha"]),
        "beta": float(selected[0]["beta"]),
    }
    check(
        "development_selection",
        len(selected) == 1
        and selected_settings == result["state_space_settings"],
        selected_settings,
    )

    primary = [
        row
        for row in trials
        if row["model"] == "Open two-level probability"
        and float(row["snr_db"]) == 12.0
    ]
    check(
        "primary_counts",
        len(primary) == 32 * 5
        and all(
            sum(row["method"] == method for row in primary) == 32
            for method in {
                "ara_fixed_lineage",
                "causal_state_space",
                "repeated_reselection",
                "compressed_parent",
                "zero_other",
            }
        ),
        len(primary),
    )

    ara = {
        metric: median_metric(primary, "ara_fixed_lineage", metric)
        for metric in ("correlation", "nrmse", "sign_accuracy", "integrated_error")
    }
    kalman = {
        metric: median_metric(primary, "causal_state_space", metric)
        for metric in ("correlation", "nrmse", "sign_accuracy", "integrated_error")
    }
    saved_verdict = result["primary_verdict"]
    check(
        "primary_ara_metrics",
        all(
            np.isclose(ara[key], saved_verdict["ara_metrics"][key], rtol=0, atol=1e-14)
            for key in ara
        ),
        ara,
    )
    check(
        "primary_state_space_metrics",
        all(
            np.isclose(
                kalman[key],
                saved_verdict["state_space_metrics"][key],
                rtol=0,
                atol=1e-14,
            )
            for key in kalman
        ),
        kalman,
    )

    gates = {
        "correlation": ara["correlation"] >= 0.70,
        "nrmse": ara["nrmse"] <= 0.25,
        "sign_accuracy": ara["sign_accuracy"] >= 0.85,
        "integrated_error": ara["integrated_error"] <= 0.15,
    }
    check(
        "absolute_status",
        all(gates.values())
        and saved_verdict["absolute_status"] == "GOOD ABSOLUTE TRACKING",
        gates,
    )

    ara_nrmse_improvement = 1.0 - ara["nrmse"] / kalman["nrmse"]
    correlation_difference = ara["correlation"] - kalman["correlation"]
    expected_mixed = (
        ara_nrmse_improvement >= 0.10
        and correlation_difference >= 0.05
        and ara["integrated_error"] > 1.10 * kalman["integrated_error"]
    )
    check(
        "comparative_status",
        expected_mixed and saved_verdict["comparative_status"] == "MIXED",
        {
            "status": saved_verdict["comparative_status"],
            "ara_nrmse_relative_improvement": ara_nrmse_improvement,
            "correlation_difference": correlation_difference,
            "ara_integrated_error": ara["integrated_error"],
            "state_space_integrated_error": kalman["integrated_error"],
        },
    )

    paired_correlation = []
    paired_nrmse = []
    paired_integral = []
    for replicate in range(TARGET_REPLICATES):
        ara_row = next(
            row
            for row in primary
            if row["method"] == "ara_fixed_lineage"
            and int(row["replicate"]) == replicate
        )
        kalman_row = next(
            row
            for row in primary
            if row["method"] == "causal_state_space"
            and int(row["replicate"]) == replicate
        )
        paired_correlation.append(
            float(ara_row["correlation"]) - float(kalman_row["correlation"])
        )
        paired_nrmse.append(float(kalman_row["nrmse"]) - float(ara_row["nrmse"]))
        paired_integral.append(
            float(kalman_row["integrated_error"])
            - float(ara_row["integrated_error"])
        )
    paired_correlation_array = np.asarray(paired_correlation)
    paired_nrmse_array = np.asarray(paired_nrmse)
    paired_integral_array = np.asarray(paired_integral)
    check(
        "paired_direction",
        np.all(paired_correlation_array > 0)
        and np.all(paired_nrmse_array > 0)
        and np.all(paired_integral_array < 0),
        {
            "ara_correlation_wins": int(np.sum(paired_correlation_array > 0)),
            "ara_nrmse_wins": int(np.sum(paired_nrmse_array > 0)),
            "ara_integral_wins": int(np.sum(paired_integral_array > 0)),
        },
    )

    quantum = simulate_quantum()
    q, g = noisy_observations(
        quantum,
        snr_db=12,
        replicates=TARGET_REPLICATES,
        seed_label="O2A3_fresh_state_space_target",
    )
    ara_estimate, scored_times, start = ara_estimates(quantum, q, g)
    calibration_count = int(np.ceil(CALIBRATION_FRACTION * quantum["times"].size))
    hidden = int(quantum["hidden_index"])
    direct_kalman = independent_kalman(
        quantum["times"],
        q[0, :, hidden],
        g[0, :, hidden],
        selected_settings["alpha"],
        selected_settings["beta"],
        calibration_count,
    )[start:]
    truth = quantum["native_other"][start:, hidden]
    direct_kalman_score = score_series(direct_kalman, truth, scored_times)
    direct_ara_score = score_series(
        ara_estimate["ara_fixed_lineage"][0],
        truth,
        scored_times,
    )
    trial_kalman = next(
        row
        for row in primary
        if row["method"] == "causal_state_space" and int(row["replicate"]) == 0
    )
    trial_ara = next(
        row
        for row in primary
        if row["method"] == "ara_fixed_lineage" and int(row["replicate"]) == 0
    )
    direct_match = all(
        np.isclose(direct_kalman_score[key], float(trial_kalman[key]), atol=1e-12)
        and np.isclose(direct_ara_score[key], float(trial_ara[key]), atol=1e-12)
        for key in direct_kalman_score
    )
    check(
        "direct_quantum_reproduction",
        direct_match,
        {"ara": direct_ara_score, "state_space": direct_kalman_score},
    )

    capacitor = simulate_electromagnetic()
    cap_start = max(
        int(np.ceil(CALIBRATION_FRACTION * capacitor["times"].size)),
        int(round(capacitor["times"].size * ARA_DERIVATIVE_FRACTION))
        + (1 - int(round(capacitor["times"].size * ARA_DERIVATIVE_FRACTION)) % 2)
        - 1,
    )
    cap_hidden = int(capacitor["hidden_index"])
    cap_native = np.abs(capacitor["native_other"][:, cap_hidden])
    cap_remaining_peak_fraction = float(
        np.max(cap_native[cap_start:]) / np.max(cap_native)
    )
    check(
        "secondary_target_identifiability_warning",
        cap_remaining_peak_fraction < 0.10,
        {"remaining_peak_fraction_after_scoring_start": cap_remaining_peak_fraction},
    )

    post_hoc = {
        "paired_quantum_12db": {
            "n": TARGET_REPLICATES,
            "median_correlation_gain_ara": float(np.median(paired_correlation_array)),
            "correlation_gain_90_bootstrap_interval": bootstrap_interval(
                paired_correlation_array, 25701
            ),
            "median_nrmse_reduction_ara": float(np.median(paired_nrmse_array)),
            "nrmse_reduction_90_bootstrap_interval": bootstrap_interval(
                paired_nrmse_array, 25702
            ),
            "median_integrated_error_reduction_ara": float(
                np.median(paired_integral_array)
            ),
            "integrated_error_reduction_90_bootstrap_interval": bootstrap_interval(
                paired_integral_array, 25703
            ),
        }
    }

    artifact_hashes = {
        "results": sha256(RESULTS),
        "development": sha256(DEVELOPMENT),
        "trials": sha256(TRIALS),
        "aggregates": sha256(AGGREGATES),
        "waveforms": sha256(WAVEFORMS),
    }
    output = {
        "test": "O2-A3 ARA fixed lineage versus causal state-space tracking",
        "validated_at": "2026-07-23",
        "checks_passed": sum(int(item["passed"]) for item in checks),
        "checks_total": len(checks),
        "all_passed": all(item["passed"] for item in checks),
        "checks": checks,
        "post_hoc_descriptive": post_hoc,
        "artifact_sha256": artifact_hashes,
    }
    VALIDATION.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not output["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
