#!/usr/bin/env python3
"""Run the frozen Q9 Information³ Bell closure and completion test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from q7_bell_decoherence_test import (
    AXES,
    BASIS,
    PAULI,
    STATES,
    WAITS,
    density_from_expectations,
    expectation,
    load_condition,
    physical_projection,
)
from q8_bell_relation_plane_test import relation_coordinates, tensor_from_rho


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q9_INFORMATION3_BELL_COMPLETION_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q9_INFORMATION3_BELL_COMPLETION_PROTOCOL_v1_FROZEN.sha256"
ALLOCATIONS_CSV = HERE / "Q9_INFORMATION3_BELL_ALLOCATIONS.csv"
COMPLETIONS_CSV = HERE / "Q9_INFORMATION3_BELL_COMPLETIONS.csv"
GATES_CSV = HERE / "Q9_INFORMATION3_BELL_GATES.csv"
RESULTS_JSON = HERE / "Q9_INFORMATION3_BELL_COMPLETION_RESULTS.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed = digest(PROTOCOL)
    if expected != observed:
        raise RuntimeError(f"Q9 frozen protocol mismatch: {observed} != {expected}")
    return observed


def bloch_children(rho: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    child_a = np.asarray([expectation(rho, axis + "I") for axis in AXES], float)
    child_b = np.asarray([expectation(rho, "I" + axis) for axis in AXES], float)
    return child_a, child_b


def information3_density(
    child_a: np.ndarray, child_b: np.ndarray, tensor: np.ndarray
) -> np.ndarray:
    rho = np.kron(PAULI["I"], PAULI["I"]).astype(complex)
    for index, axis in enumerate(AXES):
        rho += child_a[index] * np.kron(PAULI[axis], PAULI["I"])
        rho += child_b[index] * np.kron(PAULI["I"], PAULI[axis])
    for left_index, left in enumerate(AXES):
        for right_index, right in enumerate(AXES):
            rho += tensor[left_index, right_index] * np.kron(
                PAULI[left], PAULI[right]
            )
    return 0.25 * rho


def sign_of(value: float) -> int:
    return 1 if value >= 0 else -1


def choose_signed_magnitude(
    magnitude: float, previous_v: float, following_v: float
) -> tuple[float, float]:
    temporal_lock = 0.5 * (previous_v + following_v)
    positive_error = abs(magnitude - temporal_lock)
    negative_error = abs(-magnitude - temporal_lock)
    if positive_error < negative_error:
        return magnitude, temporal_lock
    if negative_error < positive_error:
        return -magnitude, temporal_lock
    if previous_v < 0:
        return -magnitude, temporal_lock
    return magnitude, temporal_lock


def add_gate(
    gates: list[dict[str, object]],
    gate_id: str,
    description: str,
    passed: bool,
    value: object,
) -> None:
    gates.append(
        {
            "gate_id": gate_id,
            "description": description,
            "passed": bool(passed),
            "value": value,
        }
    )


def pearson(x: list[float], y: list[float]) -> float:
    x_array = np.asarray(x, float)
    y_array = np.asarray(y, float)
    if np.std(x_array) <= 1e-15 or np.std(y_array) <= 1e-15:
        return float("nan")
    return float(np.corrcoef(x_array, y_array)[0, 1])


def run() -> dict[str, object]:
    protocol_hash = verify_protocol()
    allocations: list[dict[str, object]] = []
    by_condition: dict[str, dict[str, list[dict[str, object]]]] = {
        "Ramsey": {},
        "Hahn": {},
    }

    for condition in ("Ramsey", "Hahn"):
        source, _, _ = load_condition(condition)
        for state_index, state in enumerate(STATES):
            series: list[dict[str, object]] = []
            for wait_index, wait_us in enumerate(WAITS[condition]):
                coefficients = source[state_index][wait_index]
                expectations = {
                    basis: 4 * coefficient
                    for basis, coefficient in zip(BASIS, coefficients)
                }
                rho = physical_projection(density_from_expectations(expectations))
                child_a, child_b = bloch_children(rho)
                tensor = tensor_from_rho(rho)
                relation = relation_coordinates(state, tensor)
                rho_i3 = information3_density(child_a, child_b, tensor)
                rho_error = float(np.linalg.norm(rho_i3 - rho, ord="fro"))
                purity = float(np.real(np.trace(rho @ rho)))
                i_a = float(np.dot(child_a, child_a))
                i_b = float(np.dot(child_b, child_b))
                i_ab = float(np.sum(tensor**2))
                i_core = float(relation["k"] ** 2 + 2 * relation["radius"] ** 2)
                i_off = float(i_ab - i_core)
                i_unresolved = float(3 - i_a - i_b - i_ab)
                purity_closure = float(
                    abs(i_a + i_b + i_ab - (4 * purity - 1))
                )
                singular = np.sort(np.linalg.svd(tensor, compute_uv=False))[::-1]
                transverse_radius = float((singular[1] + singular[2]) / 2)
                q8_h = float(relation["hidden_residual"])
                record = {
                    "condition": condition,
                    "state": state,
                    "wait_index": wait_index,
                    "wait_us": float(wait_us),
                    "a_x": float(child_a[0]),
                    "a_y": float(child_a[1]),
                    "a_z": float(child_a[2]),
                    "b_x": float(child_b[0]),
                    "b_y": float(child_b[1]),
                    "b_z": float(child_b[2]),
                    "u": float(relation["u"]),
                    "v": float(relation["v"]),
                    "radius": float(relation["radius"]),
                    "transverse_radius": transverse_radius,
                    "k": float(relation["k"]),
                    "q8_h_linear": q8_h,
                    "purity": purity,
                    "i_child_a": i_a,
                    "i_child_b": i_b,
                    "i_relation": i_ab,
                    "i_relation_core": i_core,
                    "i_relation_off": i_off,
                    "i_unresolved_to_pure": i_unresolved,
                    "i_unresolved_half_scale": i_unresolved / 2,
                    "information3_sum": i_a + i_b + i_ab + i_unresolved,
                    "rho_reconstruction_fro_error": rho_error,
                    "purity_closure_abs_error": purity_closure,
                }
                allocations.append(record)
                series.append(record)
            by_condition[condition][state] = series

    completions: list[dict[str, object]] = []
    for condition in ("Ramsey", "Hahn"):
        for state in STATES:
            series = by_condition[condition][state]
            for index in range(1, len(series) - 1):
                current = series[index]
                magnitude = float(
                    math.sqrt(
                        max(
                            0,
                            current["transverse_radius"] ** 2 - current["u"] ** 2,
                        )
                    )
                )
                predicted, temporal_lock = choose_signed_magnitude(
                    magnitude,
                    float(series[index - 1]["v"]),
                    float(series[index + 1]["v"]),
                )
                actual = float(current["v"])
                time_only = temporal_lock
                positive_only = magnitude
                completions.append(
                    {
                        "condition": condition,
                        "state": state,
                        "wait_index": int(current["wait_index"]),
                        "wait_us": float(current["wait_us"]),
                        "visible_u": float(current["u"]),
                        "parent_transverse_radius": float(
                            current["transverse_radius"]
                        ),
                        "previous_v": float(series[index - 1]["v"]),
                        "following_v": float(series[index + 1]["v"]),
                        "actual_hidden_v": actual,
                        "inferred_magnitude": magnitude,
                        "temporal_direction_lock": temporal_lock,
                        "ara_information3_fill": predicted,
                        "zero_fill": 0.0,
                        "time_only_fill": time_only,
                        "positive_branch_only_fill": positive_only,
                        "ara_abs_error": abs(predicted - actual),
                        "zero_abs_error": abs(actual),
                        "time_only_abs_error": abs(time_only - actual),
                        "positive_branch_abs_error": abs(positive_only - actual),
                        "ara_sign_correct": sign_of(predicted) == sign_of(actual),
                        "magnitude_within_parent": abs(predicted)
                        <= float(current["transverse_radius"]) + 1e-12,
                    }
                )

    rho_errors = [float(row["rho_reconstruction_fro_error"]) for row in allocations]
    purity_errors = [float(row["purity_closure_abs_error"]) for row in allocations]
    allocation_values = [
        float(row[key])
        for row in allocations
        for key in (
            "i_child_a",
            "i_child_b",
            "i_relation",
            "i_relation_off",
            "i_unresolved_to_pure",
        )
    ]
    off_share_medians = {}
    for condition in ("Ramsey", "Hahn"):
        shares = [
            float(row["i_relation_off"]) / float(row["i_relation"])
            for row in allocations
            if row["condition"] == condition and float(row["i_relation"]) > 1e-15
        ]
        off_share_medians[condition] = float(np.median(shares))

    ara_mae = float(np.mean([row["ara_abs_error"] for row in completions]))
    zero_mae = float(np.mean([row["zero_abs_error"] for row in completions]))
    time_mae = float(np.mean([row["time_only_abs_error"] for row in completions]))
    positive_mae = float(
        np.mean([row["positive_branch_abs_error"] for row in completions])
    )
    sign_accuracy = float(
        np.mean([bool(row["ara_sign_correct"]) for row in completions])
    )
    zero_improvement = 1 - ara_mae / zero_mae if zero_mae > 0 else float("nan")
    positive_improvement = (
        1 - ara_mae / positive_mae if positive_mae > 0 else float("nan")
    )
    h_bridge_correlation = pearson(
        [float(row["q8_h_linear"]) for row in allocations],
        [float(row["i_unresolved_half_scale"]) for row in allocations],
    )
    h_bridge_mae = float(
        np.mean(
            [
                abs(
                    float(row["q8_h_linear"])
                    - float(row["i_unresolved_half_scale"])
                )
                for row in allocations
            ]
        )
    )

    gates: list[dict[str, object]] = []
    add_gate(
        gates,
        "I1",
        "all 88 Information³ density reconstructions have Frobenius error <= 1e-12",
        len(rho_errors) == 88 and max(rho_errors) <= 1e-12,
        max(rho_errors),
    )
    add_gate(
        gates,
        "I2",
        "all 88 purity-closure residuals <= 1e-12",
        max(purity_errors) <= 1e-12,
        max(purity_errors),
    )
    add_gate(
        gates,
        "I3",
        "all declared information allocations are nonnegative within tolerance",
        min(allocation_values) >= -1e-10,
        min(allocation_values),
    )
    add_gate(
        gates,
        "I4",
        "median measured off-core relation share <= 0.05 in Ramsey and Hahn",
        all(value <= 0.05 for value in off_share_medians.values()),
        off_share_medians,
    )
    add_gate(
        gates,
        "I5",
        "masked Information³ signed-v completion MAE <= 0.08",
        ara_mae <= 0.08,
        ara_mae,
    )
    add_gate(
        gates,
        "I6",
        "masked Information³ completion improves zero fill by >= 50%",
        zero_improvement >= 0.50,
        zero_improvement,
    )
    add_gate(
        gates,
        "I7",
        "masked Information³ completion improves positive-branch-only fill by >= 50%",
        positive_improvement >= 0.50,
        positive_improvement,
    )
    add_gate(
        gates,
        "I8",
        "masked Information³ completion sign accuracy >= 80%",
        sign_accuracy >= 0.80,
        sign_accuracy,
    )
    add_gate(
        gates,
        "I9",
        "all completion magnitudes remain inside the supplied parent radius",
        all(bool(row["magnitude_within_parent"]) for row in completions),
        all(bool(row["magnitude_within_parent"]) for row in completions),
    )

    allocation_medians: dict[str, dict[str, dict[str, float]]] = {}
    for condition in ("Ramsey", "Hahn"):
        allocation_medians[condition] = {}
        condition_rows = [row for row in allocations if row["condition"] == condition]
        final_index = max(int(row["wait_index"]) for row in condition_rows)
        for label, wait_index in (("initial", 0), ("final", final_index)):
            selected = [
                row for row in condition_rows if int(row["wait_index"]) == wait_index
            ]
            allocation_medians[condition][label] = {
                key: float(np.median([float(row[key]) for row in selected]))
                for key in (
                    "i_child_a",
                    "i_child_b",
                    "i_relation_core",
                    "i_relation_off",
                    "i_unresolved_to_pure",
                    "purity",
                    "q8_h_linear",
                )
            }

    result = {
        "test_id": "Q9-INFORMATION3-BELL-COMPLETION-v1",
        "ledger_id": "T268",
        "test_class": "post-outcome exact-closure and masked-data completion",
        "protocol_sha256": protocol_hash,
        "verdict": "CALIBRATED" if all(gate["passed"] for gate in gates) else "NOT CALIBRATED",
        "summary": {
            "records": len(allocations),
            "masked_interior_values": len(completions),
            "maximum_rho_reconstruction_fro_error": max(rho_errors),
            "maximum_purity_closure_abs_error": max(purity_errors),
            "off_core_relation_share_medians": off_share_medians,
            "ara_information3_fill_mae": ara_mae,
            "zero_fill_mae": zero_mae,
            "time_only_linear_fill_mae": time_mae,
            "positive_branch_only_fill_mae": positive_mae,
            "zero_fill_relative_improvement": zero_improvement,
            "positive_branch_relative_improvement": positive_improvement,
            "signed_completion_accuracy": sign_accuracy,
            "q8_h_vs_half_unresolved_information_correlation": h_bridge_correlation,
            "q8_h_vs_half_unresolved_information_mae": h_bridge_mae,
            "gates_passed": sum(bool(gate["passed"]) for gate in gates),
            "gates_total": len(gates),
        },
        "allocation_medians": allocation_medians,
        "gates": gates,
        "interpretation_boundary": (
            "The state closure is an exact Pauli-basis identity and the masked test is "
            "parent-assisted interpolation. It does not obtain the parent radius for free, "
            "predict future data, or identify unresolved purity as a coherent environmental wave."
        ),
    }

    with ALLOCATIONS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(allocations[0]))
        writer.writeheader()
        writer.writerows(allocations)
    with COMPLETIONS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(completions[0]))
        writer.writeheader()
        writer.writerows(completions)
    with GATES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=("gate_id", "description", "passed", "value")
        )
        writer.writeheader()
        for gate in gates:
            writer.writerow(
                {
                    **gate,
                    "value": json.dumps(gate["value"], sort_keys=True),
                }
            )
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    output = run()
    print(json.dumps(output["summary"], indent=2))
    print(f"Verdict: {output['verdict']}")
