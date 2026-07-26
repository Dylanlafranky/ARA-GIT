#!/usr/bin/env python3
"""Independent source and arithmetic validation for Q9."""

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
ALLOCATIONS = HERE / "Q9_INFORMATION3_BELL_ALLOCATIONS.csv"
COMPLETIONS = HERE / "Q9_INFORMATION3_BELL_COMPLETIONS.csv"
RESULTS = HERE / "Q9_INFORMATION3_BELL_COMPLETION_RESULTS.json"
OUTPUT = HERE / "Q9_INFORMATION3_BELL_COMPLETION_VALIDATION.json"


def density_from_lock(
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
    return rho / 4


def signed_fill(magnitude: float, previous_v: float, following_v: float) -> float:
    lock = (previous_v + following_v) / 2
    positive_error = abs(magnitude - lock)
    negative_error = abs(-magnitude - lock)
    if positive_error < negative_error:
        return magnitude
    if negative_error < positive_error:
        return -magnitude
    return -magnitude if previous_v < 0 else magnitude


def main() -> None:
    expected_hash = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    actual_hash = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()
    if expected_hash != actual_hash:
        raise RuntimeError("Q9 protocol hash mismatch")

    with ALLOCATIONS.open(newline="", encoding="utf-8") as handle:
        saved_allocations = list(csv.DictReader(handle))
    with COMPLETIONS.open(newline="", encoding="utf-8") as handle:
        saved_completions = list(csv.DictReader(handle))
    saved_allocation_by_key = {
        (row["condition"], row["state"], int(row["wait_index"])): row
        for row in saved_allocations
    }
    saved_completion_by_key = {
        (row["condition"], row["state"], int(row["wait_index"])): row
        for row in saved_completions
    }

    recomputed: dict[str, dict[str, list[dict[str, float]]]] = {
        condition: {state: [] for state in STATES}
        for condition in ("Ramsey", "Hahn")
    }
    allocation_differences: list[float] = []
    rho_errors: list[float] = []
    purity_errors: list[float] = []
    allocation_values: list[float] = []
    off_shares: dict[str, list[float]] = {"Ramsey": [], "Hahn": []}
    for condition in ("Ramsey", "Hahn"):
        source, _, _ = load_condition(condition)
        for state_index, state in enumerate(STATES):
            for wait_index, coefficients in enumerate(source[state_index]):
                expectations = {
                    basis: 4 * coefficient
                    for basis, coefficient in zip(BASIS, coefficients)
                }
                rho = physical_projection(density_from_expectations(expectations))
                child_a = np.asarray(
                    [expectation(rho, axis + "I") for axis in AXES], float
                )
                child_b = np.asarray(
                    [expectation(rho, "I" + axis) for axis in AXES], float
                )
                tensor = tensor_from_rho(rho)
                relation = relation_coordinates(state, tensor)
                singular = np.sort(np.linalg.svd(tensor, compute_uv=False))[::-1]
                transverse = float((singular[1] + singular[2]) / 2)
                purity = float(np.real(np.trace(rho @ rho)))
                i_a = float(child_a @ child_a)
                i_b = float(child_b @ child_b)
                i_relation = float(np.sum(tensor**2))
                i_core = float(relation["k"] ** 2 + 2 * relation["radius"] ** 2)
                i_off = i_relation - i_core
                unresolved = 3 - i_a - i_b - i_relation
                rho_error = float(
                    np.linalg.norm(density_from_lock(child_a, child_b, tensor) - rho)
                )
                purity_error = abs(i_a + i_b + i_relation - (4 * purity - 1))
                current = {
                    "u": float(relation["u"]),
                    "v": float(relation["v"]),
                    "radius": float(relation["radius"]),
                    "transverse_radius": transverse,
                    "k": float(relation["k"]),
                    "q8_h_linear": float(relation["hidden_residual"]),
                    "purity": purity,
                    "i_child_a": i_a,
                    "i_child_b": i_b,
                    "i_relation": i_relation,
                    "i_relation_core": i_core,
                    "i_relation_off": i_off,
                    "i_unresolved_to_pure": unresolved,
                    "rho_reconstruction_fro_error": rho_error,
                    "purity_closure_abs_error": purity_error,
                }
                recomputed[condition][state].append(current)
                saved = saved_allocation_by_key[(condition, state, wait_index)]
                for field, value in current.items():
                    allocation_differences.append(abs(value - float(saved[field])))
                rho_errors.append(rho_error)
                purity_errors.append(purity_error)
                allocation_values.extend([i_a, i_b, i_relation, i_off, unresolved])
                off_shares[condition].append(i_off / i_relation)

    completion_differences: list[float] = []
    ara_errors: list[float] = []
    zero_errors: list[float] = []
    positive_errors: list[float] = []
    sign_results: list[bool] = []
    within_parent: list[bool] = []
    for condition in ("Ramsey", "Hahn"):
        for state in STATES:
            series = recomputed[condition][state]
            for index in range(1, len(series) - 1):
                current = series[index]
                magnitude = math.sqrt(
                    max(
                        0,
                        current["transverse_radius"] ** 2 - current["u"] ** 2,
                    )
                )
                prediction = signed_fill(
                    magnitude, series[index - 1]["v"], series[index + 1]["v"]
                )
                actual = current["v"]
                key = (condition, state, index)
                saved = saved_completion_by_key[key]
                values = {
                    "inferred_magnitude": magnitude,
                    "ara_information3_fill": prediction,
                    "ara_abs_error": abs(prediction - actual),
                    "zero_abs_error": abs(actual),
                    "positive_branch_abs_error": abs(magnitude - actual),
                }
                for field, value in values.items():
                    completion_differences.append(abs(value - float(saved[field])))
                ara_errors.append(values["ara_abs_error"])
                zero_errors.append(values["zero_abs_error"])
                positive_errors.append(values["positive_branch_abs_error"])
                sign_results.append((prediction >= 0) == (actual >= 0))
                within_parent.append(
                    abs(prediction) <= current["transverse_radius"] + 1e-12
                )

    off_medians = {
        condition: float(np.median(values))
        for condition, values in off_shares.items()
    }
    ara_mae = float(np.mean(ara_errors))
    zero_mae = float(np.mean(zero_errors))
    positive_mae = float(np.mean(positive_errors))
    gate_truths = {
        "I1": len(rho_errors) == 88 and max(rho_errors) <= 1e-12,
        "I2": max(purity_errors) <= 1e-12,
        "I3": min(allocation_values) >= -1e-10,
        "I4": all(value <= 0.05 for value in off_medians.values()),
        "I5": ara_mae <= 0.08,
        "I6": 1 - ara_mae / zero_mae >= 0.50,
        "I7": 1 - ara_mae / positive_mae >= 0.50,
        "I8": float(np.mean(sign_results)) >= 0.80,
        "I9": all(within_parent),
    }
    saved_result = json.loads(RESULTS.read_text(encoding="utf-8"))
    saved_truths = {
        gate["gate_id"]: bool(gate["passed"]) for gate in saved_result["gates"]
    }
    validation = {
        "test_id": "Q9-INFORMATION3-BELL-COMPLETION-v1-independent-validation",
        "protocol_sha256": actual_hash,
        "source_records_rebuilt": len(rho_errors),
        "masked_values_rebuilt": len(ara_errors),
        "maximum_allocation_field_abs_difference": max(allocation_differences),
        "maximum_completion_field_abs_difference": max(completion_differences),
        "independent_gate_truths": gate_truths,
        "saved_gate_truths": saved_truths,
        "gate_truths_match": gate_truths == saved_truths,
        "checks": {
            "all_source_records_match": max(allocation_differences) <= 1e-12,
            "all_completion_records_match": max(completion_differences) <= 1e-12,
            "gate_outcomes_match": gate_truths == saved_truths,
        },
        "validated": (
            max(allocation_differences) <= 1e-12
            and max(completion_differences) <= 1e-12
            and gate_truths == saved_truths
        ),
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
