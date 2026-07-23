#!/usr/bin/env python3
"""Prospective recovery of hidden source/sink terms from ARA continuity residuals."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Callable

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "HIDDEN_OTHER_RESIDUAL_PROTOCOL_2026-07-23.md"
SUMMARY_CSV = HERE / "ARA_HIDDEN_OTHER_RESIDUAL_SUMMARY.csv"
SAMPLE_CSV = HERE / "ARA_HIDDEN_OTHER_RESIDUAL_BOUNDED_SAMPLE.csv"
RESULTS_JSON = HERE / "ARA_HIDDEN_OTHER_RESIDUAL_RESULTS.json"

SIGN_THRESHOLD = 0.999
CORRELATION_THRESHOLD = 0.999
NRMSE_THRESHOLD = 0.001
INTEGRATED_ERROR_THRESHOLD = 0.001
INACTIVE_RMS_THRESHOLD = 0.001


def rk4(
    rhs: Callable[[float, np.ndarray], np.ndarray],
    initial: np.ndarray,
    times: np.ndarray,
) -> np.ndarray:
    values = np.empty((times.size, initial.size), dtype=initial.dtype)
    values[0] = initial
    for index in range(times.size - 1):
        time = float(times[index])
        step = float(times[index + 1] - times[index])
        state = values[index]
        k1 = rhs(time, state)
        k2 = rhs(time + step / 2.0, state + step * k1 / 2.0)
        k3 = rhs(time + step / 2.0, state + step * k2 / 2.0)
        k4 = rhs(time + step, state + step * k3)
        values[index + 1] = state + step * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
    return values


def fourth_order_derivative(values: np.ndarray, step: float) -> np.ndarray:
    return (
        -values[4:]
        + 8.0 * values[3:-1]
        - 8.0 * values[1:-3]
        + values[:-4]
    ) / (12.0 * step)


def simulate_classical() -> dict:
    times = np.linspace(0.0, 30.0, 6001)
    omega0 = 1.0
    coupling = 0.8
    hidden_gamma = 0.14

    def rhs(_time: float, state: np.ndarray) -> np.ndarray:
        q1, q2, p1, p2 = state
        difference = q2 - q1
        return np.array(
            [
                p1,
                p2,
                -omega0**2 * q1 + coupling * difference,
                -omega0**2 * q2 - coupling * difference - hidden_gamma * p2,
            ]
        )

    state = rk4(rhs, np.array([1.0, 0.2, 0.0, 0.7]), times)
    q1, q2, p1, p2 = state.T
    difference = q2 - q1

    stored = np.column_stack(
        [
            0.5 * p1**2 + 0.5 * omega0**2 * q1**2,
            0.5 * coupling * difference**2,
            0.5 * p2**2 + 0.5 * omega0**2 * q2**2,
        ]
    )

    spring_to_1 = coupling * difference * p1
    spring_to_2 = -coupling * difference * p2
    net_internal = np.column_stack(
        [
            spring_to_1,
            -spring_to_1 - spring_to_2,
            spring_to_2,
        ]
    )
    native_other = np.column_stack(
        [
            np.zeros_like(times),
            np.zeros_like(times),
            -hidden_gamma * p2**2,
        ]
    )
    return {
        "model": "Damped coupled oscillators",
        "domain": "Newton/Hamilton mechanics",
        "role": "Development",
        "times": times,
        "stored": stored,
        "net_internal": net_internal,
        "native_other": native_other,
        "identity_names": ["oscillator 1", "coupling spring", "oscillator 2"],
        "hidden_index": 2,
        "hidden_kind": "child-local viscous sink",
        "native_law": "s_hidden = -gamma * p2^2",
        "hidden_parameter": hidden_gamma,
    }


def simulate_electromagnetic() -> dict:
    times = np.linspace(0.0, 12.0, 5001)
    capacitance_1 = 1.0
    capacitance_2 = 1.3
    hidden_resistance = 0.7

    def rhs(_time: float, state: np.ndarray) -> np.ndarray:
        voltage_1, voltage_2 = state
        current = (voltage_1 - voltage_2) / hidden_resistance
        return np.array(
            [
                -current / capacitance_1,
                current / capacitance_2,
            ]
        )

    state = rk4(rhs, np.array([2.0, 0.3]), times)
    voltage_1, voltage_2 = state.T
    current = (voltage_1 - voltage_2) / hidden_resistance
    power_from_1 = voltage_1 * current
    power_to_2 = voltage_2 * current

    stored = np.column_stack(
        [
            0.5 * capacitance_1 * voltage_1**2,
            np.zeros_like(times),
            0.5 * capacitance_2 * voltage_2**2,
        ]
    )
    net_internal = np.column_stack(
        [
            -power_from_1,
            power_from_1 - power_to_2,
            power_to_2,
        ]
    )
    native_other = np.column_stack(
        [
            np.zeros_like(times),
            -hidden_resistance * current**2,
            np.zeros_like(times),
        ]
    )
    return {
        "model": "Resistive capacitor coupling",
        "domain": "Electromagnetic circuit energy",
        "role": "Verification",
        "times": times,
        "stored": stored,
        "net_internal": net_internal,
        "native_other": native_other,
        "identity_names": ["capacitor 1", "coupling relation", "capacitor 2"],
        "hidden_index": 1,
        "hidden_kind": "relation-local Joule sink",
        "native_law": "s_hidden = -R * I^2",
        "hidden_parameter": hidden_resistance,
    }


def simulate_quantum() -> dict:
    times = np.linspace(0.0, 20.0, 8001)
    coupling = 0.9
    hidden_gamma = 0.25

    def rhs(_time: float, state: np.ndarray) -> np.ndarray:
        amplitude_1, amplitude_2 = state
        return np.array(
            [
                -1j * coupling * amplitude_2,
                -1j * coupling * amplitude_1
                - hidden_gamma * amplitude_2 / 2.0,
            ],
            dtype=complex,
        )

    initial = np.array([1.0 + 0j, 0.0 + 0.3j], dtype=complex)
    initial /= np.linalg.norm(initial)
    state = rk4(rhs, initial, times)
    amplitude_1, amplitude_2 = state.T
    probability_1 = np.abs(amplitude_1) ** 2
    probability_2 = np.abs(amplitude_2) ** 2
    current_1_to_2 = -2.0 * coupling * np.imag(
        np.conjugate(amplitude_1) * amplitude_2
    )

    stored = np.column_stack([probability_1, probability_2])
    net_internal = np.column_stack([-current_1_to_2, current_1_to_2])
    native_other = np.column_stack(
        [
            np.zeros_like(times),
            -hidden_gamma * probability_2,
        ]
    )
    return {
        "model": "Open two-level probability",
        "domain": "Non-Hermitian quantum continuity",
        "role": "Holdout",
        "times": times,
        "stored": stored,
        "net_internal": net_internal,
        "native_other": native_other,
        "identity_names": ["quantum state 1", "quantum state 2"],
        "hidden_index": 1,
        "hidden_kind": "child-local probability sink",
        "native_law": "s_hidden = -Gamma * |b|^2",
        "hidden_parameter": hidden_gamma,
    }


def recover_hidden_other(model: dict) -> tuple[dict, list[dict]]:
    times = model["times"]
    step = float(times[1] - times[0])
    scored_times = times[2:-2]
    stored = model["stored"]
    net_internal = model["net_internal"][2:-2]
    native = model["native_other"][2:-2]

    derivative = np.column_stack(
        [
            fourth_order_derivative(stored[:, index], step)
            for index in range(stored.shape[1])
        ]
    )
    estimated = derivative - net_internal

    integrated_abs = np.trapezoid(np.abs(estimated), scored_times, axis=0)
    predicted_index = int(np.argmax(integrated_abs))
    hidden_index = int(model["hidden_index"])

    native_hidden = native[:, hidden_index]
    estimated_hidden = estimated[:, hidden_index]
    native_peak = float(np.max(np.abs(native_hidden)))
    active = np.abs(native_hidden) >= 1e-6 * native_peak
    sign_accuracy = float(
        np.mean(
            np.sign(estimated_hidden[active])
            == np.sign(native_hidden[active])
        )
    )
    correlation = float(np.corrcoef(estimated_hidden, native_hidden)[0, 1])
    rmse = float(np.sqrt(np.mean((estimated_hidden - native_hidden) ** 2)))
    nrmse = rmse / native_peak
    estimated_integral = float(np.trapezoid(estimated_hidden, scored_times))
    native_integral = float(np.trapezoid(native_hidden, scored_times))
    integrated_relative_error = abs(estimated_integral - native_integral) / abs(
        native_integral
    )

    inactive_indices = [
        index for index in range(stored.shape[1]) if index != hidden_index
    ]
    inactive_rms = max(
        float(np.sqrt(np.mean(estimated[:, index] ** 2)))
        for index in inactive_indices
    )
    inactive_rms_fraction = inactive_rms / native_peak

    total_estimated = np.sum(estimated, axis=1)
    parent_only_each = total_estimated / stored.shape[1]
    parent_only_nrmse = float(
        np.sqrt(np.mean((parent_only_each - native_hidden) ** 2)) / native_peak
    )
    no_other_nrmse = float(
        np.sqrt(np.mean(native_hidden**2)) / native_peak
    )
    wrong_index = int(np.argmin(integrated_abs))
    wrong_location_nrmse = float(
        np.sqrt(np.mean((estimated[:, wrong_index] - native_hidden) ** 2))
        / native_peak
    )
    beats_controls = (
        nrmse < no_other_nrmse
        and nrmse < parent_only_nrmse
        and nrmse < wrong_location_nrmse
        and predicted_index == hidden_index
    )

    passed = (
        predicted_index == hidden_index
        and sign_accuracy >= SIGN_THRESHOLD
        and correlation >= CORRELATION_THRESHOLD
        and nrmse <= NRMSE_THRESHOLD
        and integrated_relative_error <= INTEGRATED_ERROR_THRESHOLD
        and inactive_rms_fraction <= INACTIVE_RMS_THRESHOLD
        and beats_controls
    )

    summary = {
        "model": model["model"],
        "domain": model["domain"],
        "test_role": model["role"],
        "hidden_kind": model["hidden_kind"],
        "identity_count": len(model["identity_names"]),
        "planned_samples": int(times.size),
        "scored_samples": int(scored_times.size),
        "native_hidden_location": model["identity_names"][hidden_index],
        "predicted_hidden_location": model["identity_names"][predicted_index],
        "location_correct": predicted_index == hidden_index,
        "predicted_sign": (
            "sink"
        if float(np.trapezoid(estimated_hidden, scored_times)) < 0
            else "source"
        ),
        "native_sign": (
            "sink" if native_integral < 0 else "source"
        ),
        "sign_accuracy": sign_accuracy,
        "source_correlation": correlation,
        "source_nrmse": nrmse,
        "integrated_relative_error": integrated_relative_error,
        "inactive_rms_fraction": inactive_rms_fraction,
        "estimated_integrated_other": estimated_integral,
        "native_integrated_other": native_integral,
        "native_peak_magnitude": native_peak,
        "no_other_control_nrmse": no_other_nrmse,
        "parent_only_control_nrmse": parent_only_nrmse,
        "wrong_location_control_nrmse": wrong_location_nrmse,
        "wrong_location_identity": model["identity_names"][wrong_index],
        "beats_all_controls": beats_controls,
        "passed": passed,
        "native_law_revealed_for_scoring": model["native_law"],
    }

    selected_indices = np.unique(
        np.linspace(0, scored_times.size - 1, 181, dtype=int)
    )
    sample_rows: list[dict] = []
    for sample_index in selected_indices:
        for identity_index, identity_name in enumerate(model["identity_names"]):
            sample_rows.append(
                {
                    "model": model["model"],
                    "domain": model["domain"],
                    "test_role": model["role"],
                    "time": float(scored_times[sample_index]),
                    "identity": identity_name,
                    "identity_index": identity_index,
                    "is_native_hidden_location": identity_index == hidden_index,
                    "stored_quantity": float(stored[sample_index + 2, identity_index]),
                    "net_internal_transfer": float(
                        net_internal[sample_index, identity_index]
                    ),
                    "estimated_other": float(
                        estimated[sample_index, identity_index]
                    ),
                    "native_other_revealed": float(
                        native[sample_index, identity_index]
                    ),
                    "absolute_recovery_error": float(
                        abs(
                            estimated[sample_index, identity_index]
                            - native[sample_index, identity_index]
                        )
                    ),
                }
            )
    return summary, sample_rows


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    model_outputs = [
        simulate_classical(),
        simulate_electromagnetic(),
        simulate_quantum(),
    ]
    summaries: list[dict] = []
    samples: list[dict] = []
    for model in model_outputs:
        summary, sample_rows = recover_hidden_other(model)
        summaries.append(summary)
        samples.extend(sample_rows)

    passed_models = sum(int(row["passed"]) for row in summaries)
    results = {
        "status": "passed" if passed_models == len(summaries) else "failed",
        "protocol_sha256": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "estimator": "s_hat_i = fourth_order_dq_i_dt - net_internal_transfer_i",
        "models_passed": passed_models,
        "models_total": len(summaries),
        "total_planned_samples": sum(row["planned_samples"] for row in summaries),
        "total_scored_samples": sum(row["scored_samples"] for row in summaries),
        "all_locations_correct": all(row["location_correct"] for row in summaries),
        "minimum_sign_accuracy": min(row["sign_accuracy"] for row in summaries),
        "minimum_source_correlation": min(
            row["source_correlation"] for row in summaries
        ),
        "maximum_source_nrmse": max(row["source_nrmse"] for row in summaries),
        "maximum_integrated_relative_error": max(
            row["integrated_relative_error"] for row in summaries
        ),
        "maximum_inactive_rms_fraction": max(
            row["inactive_rms_fraction"] for row in summaries
        ),
        "interpretation": (
            "The unchanged continuity residual recovered concealed child-local and "
            "relation-local sinks in controlled raw simulations. This is a diagnostic "
            "inverse result, not yet forward prediction of an unseen waveform."
        ),
        "model_summaries": summaries,
    }
    write_csv(SUMMARY_CSV, summaries)
    write_csv(SAMPLE_CSV, samples)
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(results, indent=2, ensure_ascii=False))
    if results["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
