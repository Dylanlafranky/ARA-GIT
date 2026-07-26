#!/usr/bin/env python3
"""Run frozen T265/Q6B with an explicit physical density-matrix projection."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from q4_bell_parent_child_test import expectations
from q5_bell_four_state_test import STATE_CONFIGS, load_state, verify_sources
from q6_chsh_coherence_ladder_test import (
    BELL_STATES,
    CLASSICAL_CONTROLS,
    CONTROL_WEIGHTS,
    ENTITY_ORDER,
    STRONG_AXIS_THRESHOLD,
    UNIFORM_CONTROL,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_PROTOCOL_v1_FROZEN.sha256"
Q5_RESULTS = HERE / "Q5_BELL_FOUR_STATE_RESULTS.json"
STATES_CSV = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_STATES.csv"
BOOTSTRAP_CSV = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_BOOTSTRAP.csv"
RESULTS_JSON = HERE / "Q6B_PHYSICAL_CHSH_COHERENCE_RESULTS.json"

BOOTSTRAP_SEED = 2026072406
BOOTSTRAP_REPS = 5000
TSIRELSON = 2.0 * np.sqrt(2.0)
PAULI = {
    "I": np.asarray([[1, 0], [0, 1]], dtype=np.complex128),
    "X": np.asarray([[0, 1], [1, 0]], dtype=np.complex128),
    "Y": np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128),
    "Z": np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
}
AXES = ("X", "Y", "Z")


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed = digest(PROTOCOL, "sha256")
    if observed != expected:
        raise RuntimeError(
            f"Frozen Q6B protocol mismatch: expected {expected}, observed {observed}"
        )
    return observed


def linear_density(exp: dict[str, float]) -> np.ndarray:
    rho = np.zeros((4, 4), dtype=np.complex128)
    for left in ("I", *AXES):
        for right in ("I", *AXES):
            rho += float(exp[left + right]) * np.kron(PAULI[left], PAULI[right])
    return 0.25 * (rho + rho.conj().T) / 2.0


def project_to_simplex(values: np.ndarray) -> np.ndarray:
    ordered = np.sort(np.real(values))[::-1]
    cumulative = np.cumsum(ordered)
    eligible = ordered - (cumulative - 1.0) / np.arange(1, len(values) + 1) > 0
    if not np.any(eligible):
        raise RuntimeError("Probability-simplex projection found no active eigenvalue")
    active = int(np.flatnonzero(eligible)[-1] + 1)
    theta = float((cumulative[active - 1] - 1.0) / active)
    return np.maximum(np.real(values) - theta, 0.0)


def physical_projection(rho_linear: np.ndarray) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eigh(
        0.5 * (rho_linear + rho_linear.conj().T)
    )
    projected = project_to_simplex(eigenvalues)
    rho = (eigenvectors * projected) @ eigenvectors.conj().T
    return 0.5 * (rho + rho.conj().T)


def tensor_from_density(rho: np.ndarray) -> np.ndarray:
    return np.asarray(
        [
            [
                float(np.real(np.trace(rho @ np.kron(PAULI[left], PAULI[right]))))
                for right in AXES
            ]
            for left in AXES
        ],
        dtype=np.float64,
    )


def state_metrics(rho: np.ndarray) -> dict[str, object]:
    tensor = tensor_from_density(rho)
    singular = np.sort(np.linalg.svd(tensor, compute_uv=False))[::-1]
    eigenvalues = np.linalg.eigvalsh(rho)
    local_expectations = {
        left + "I": float(
            np.real(np.trace(rho @ np.kron(PAULI[left], PAULI["I"])))
        )
        for left in AXES
    }
    local_expectations.update(
        {
            "I" + right: float(
                np.real(np.trace(rho @ np.kron(PAULI["I"], PAULI[right])))
            )
            for right in AXES
        }
    )
    return {
        "tensor": tensor.tolist(),
        "singular_values": [float(value) for value in singular],
        "chsh_smax": float(2.0 * np.sqrt(singular[0] ** 2 + singular[1] ** 2)),
        "retained_axes_at_0p50": int(np.sum(singular >= STRONG_AXIS_THRESHOLD)),
        "local_expectations": local_expectations,
        "local_child_mean_abs": float(
            np.mean(np.abs(list(local_expectations.values())))
        ),
        "local_child_max_abs": float(
            np.max(np.abs(list(local_expectations.values())))
        ),
        "trace": float(np.real(np.trace(rho))),
        "trace_error": float(abs(np.trace(rho) - 1.0)),
        "minimum_eigenvalue": float(np.min(eigenvalues)),
        "maximum_eigenvalue": float(np.max(eigenvalues)),
        "hermiticity_residual": float(np.max(np.abs(rho - rho.conj().T))),
        "purity": float(np.real(np.trace(rho @ rho))),
    }


def point_states() -> tuple[
    dict[str, np.ndarray], dict[str, dict[str, float]], dict[str, object]
]:
    q5 = json.loads(Q5_RESULTS.read_text(encoding="utf-8"))
    physical = {}
    diagnostics = {}
    for state in BELL_STATES:
        exp = q5["states"][state]["expectations"]
        linear = linear_density(exp)
        physical[state] = physical_projection(linear)
        diagnostics[state] = {
            "linear_trace": float(np.real(np.trace(linear))),
            "linear_minimum_eigenvalue": float(np.min(np.linalg.eigvalsh(linear))),
            "projection_frobenius_distance": float(
                np.linalg.norm(physical[state] - linear, ord="fro")
            ),
        }
    for control, weights in CONTROL_WEIGHTS.items():
        physical[control] = sum(
            (weight * physical[state] for state, weight in weights.items()),
            start=np.zeros((4, 4), dtype=np.complex128),
        )
    return physical, diagnostics, q5


def load_raw_records() -> dict[str, dict[str, np.ndarray]]:
    records = {}
    for state in BELL_STATES:
        state_records, _ = load_state(state, STATE_CONFIGS[state])
        records[state] = state_records
    return records


def bootstrap(
    records: dict[str, dict[str, np.ndarray]]
) -> tuple[dict[str, dict[str, np.ndarray]], list[dict[str, object]]]:
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = {
        entity: {
            "s1": np.empty(BOOTSTRAP_REPS, dtype=np.float64),
            "s2": np.empty(BOOTSTRAP_REPS, dtype=np.float64),
            "s3": np.empty(BOOTSTRAP_REPS, dtype=np.float64),
            "chsh_smax": np.empty(BOOTSTRAP_REPS, dtype=np.float64),
            "retained_axes": np.empty(BOOTSTRAP_REPS, dtype=np.int8),
        }
        for entity in ENTITY_ORDER
    }
    rows: list[dict[str, object]] = []

    for repetition in range(BOOTSTRAP_REPS):
        state_rhos = {}
        for state in BELL_STATES:
            probabilities = {}
            for orientation, values in records[state].items():
                indices = rng.integers(0, len(values), size=len(values))
                probabilities[orientation] = values[indices].mean(axis=0)
            state_rhos[state] = physical_projection(
                linear_density(expectations(probabilities))
            )

        rhos = dict(state_rhos)
        for control, weights in CONTROL_WEIGHTS.items():
            rhos[control] = sum(
                (weight * state_rhos[state] for state, weight in weights.items()),
                start=np.zeros((4, 4), dtype=np.complex128),
            )

        for entity in ENTITY_ORDER:
            metrics = state_metrics(rhos[entity])
            singular = metrics["singular_values"]
            draws[entity]["s1"][repetition] = singular[0]
            draws[entity]["s2"][repetition] = singular[1]
            draws[entity]["s3"][repetition] = singular[2]
            draws[entity]["chsh_smax"][repetition] = metrics["chsh_smax"]
            draws[entity]["retained_axes"][repetition] = metrics[
                "retained_axes_at_0p50"
            ]
            rows.append(
                {
                    "entity": entity,
                    "entity_type": (
                        "physically_prepared"
                        if entity in BELL_STATES
                        else "equal_weight_reconstruction"
                    ),
                    "replicate": repetition,
                    "s1": singular[0],
                    "s2": singular[1],
                    "s3": singular[2],
                    "chsh_smax": metrics["chsh_smax"],
                    "retained_axes_at_0p50": metrics[
                        "retained_axes_at_0p50"
                    ],
                }
            )
    return draws, rows


def interval(values: np.ndarray) -> list[float]:
    low, high = np.percentile(values, [2.5, 97.5])
    return [float(low), float(high)]


def summarize_bootstrap(
    draws: dict[str, dict[str, np.ndarray]]
) -> dict[str, dict[str, object]]:
    summary = {}
    for entity in ENTITY_ORDER:
        entity_draws = draws[entity]
        chsh = entity_draws["chsh_smax"]
        summary[entity] = {
            "chsh_95ci": interval(chsh),
            "s1_95ci": interval(entity_draws["s1"]),
            "s2_95ci": interval(entity_draws["s2"]),
            "s3_95ci": interval(entity_draws["s3"]),
            "fraction_chsh_above_2p00": float(np.mean(chsh > 2.0)),
            "fraction_chsh_at_most_2p10": float(np.mean(chsh <= 2.1)),
            "fraction_chsh_at_most_0p60": float(np.mean(chsh <= 0.6)),
        }
    return summary


def gates(
    metrics: dict[str, dict[str, object]],
    bootstrap_metrics: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    all_trace = [metrics[entity]["trace_error"] for entity in ENTITY_ORDER]
    all_min_eigen = [
        metrics[entity]["minimum_eigenvalue"] for entity in ENTITY_ORDER
    ]
    all_hermiticity = [
        metrics[entity]["hermiticity_residual"] for entity in ENTITY_ORDER
    ]
    all_chsh = [metrics[entity]["chsh_smax"] for entity in ENTITY_ORDER]
    bell_chsh = [metrics[state]["chsh_smax"] for state in BELL_STATES]
    classical_chsh = [
        metrics[state]["chsh_smax"] for state in CLASSICAL_CONTROLS
    ]
    sequence = [
        metrics[entity]["retained_axes_at_0p50"] for entity in ENTITY_ORDER
    ]
    return {
        "P1_trace_error_at_most_1e_12": {
            "values": all_trace,
            "threshold": 1e-12,
            "pass": all(value <= 1e-12 for value in all_trace),
        },
        "P2_minimum_eigenvalue_at_least_negative_1e_12": {
            "values": all_min_eigen,
            "threshold": -1e-12,
            "pass": all(value >= -1e-12 for value in all_min_eigen),
        },
        "P3_hermiticity_residual_at_most_1e_12": {
            "values": all_hermiticity,
            "threshold": 1e-12,
            "pass": all(value <= 1e-12 for value in all_hermiticity),
        },
        "P4_tsirelson_bound": {
            "values": all_chsh,
            "threshold": float(TSIRELSON + 1e-12),
            "pass": all(value <= TSIRELSON + 1e-12 for value in all_chsh),
        },
        "B1_all_bell_chsh_above_2p00": {
            "values": bell_chsh,
            "threshold": 2.0,
            "pass": all(value > 2.0 for value in bell_chsh),
        },
        "B2_all_bell_chsh_at_least_2p20": {
            "values": bell_chsh,
            "threshold": 2.2,
            "pass": all(value >= 2.2 for value in bell_chsh),
        },
        "B3_all_bell_s2_at_least_0p50": {
            "values": [metrics[state]["singular_values"][1] for state in BELL_STATES],
            "threshold": 0.5,
            "pass": all(
                metrics[state]["singular_values"][1] >= 0.5
                for state in BELL_STATES
            ),
        },
        "B4_all_bell_have_three_retained_axes": {
            "values": [
                metrics[state]["retained_axes_at_0p50"] for state in BELL_STATES
            ],
            "target": 3,
            "pass": all(
                metrics[state]["retained_axes_at_0p50"] == 3
                for state in BELL_STATES
            ),
        },
        "B5_bell_bootstrap_violation_fraction_at_least_0p95": {
            "values": [
                bootstrap_metrics[state]["fraction_chsh_above_2p00"]
                for state in BELL_STATES
            ],
            "threshold": 0.95,
            "pass": all(
                bootstrap_metrics[state]["fraction_chsh_above_2p00"] >= 0.95
                for state in BELL_STATES
            ),
        },
        "C1_classical_chsh_at_most_2p00": {
            "values": classical_chsh,
            "threshold": 2.0,
            "pass": all(value <= 2.0 for value in classical_chsh),
        },
        "C2_classical_s1_at_least_0p70": {
            "values": [
                metrics[state]["singular_values"][0]
                for state in CLASSICAL_CONTROLS
            ],
            "threshold": 0.70,
            "pass": all(
                metrics[state]["singular_values"][0] >= 0.70
                for state in CLASSICAL_CONTROLS
            ),
        },
        "C3_classical_s2_at_most_0p30": {
            "values": [
                metrics[state]["singular_values"][1]
                for state in CLASSICAL_CONTROLS
            ],
            "threshold": 0.30,
            "pass": all(
                metrics[state]["singular_values"][1] <= 0.30
                for state in CLASSICAL_CONTROLS
            ),
        },
        "C4_classical_one_retained_axis": {
            "values": [
                metrics[state]["retained_axes_at_0p50"]
                for state in CLASSICAL_CONTROLS
            ],
            "target": 1,
            "pass": all(
                metrics[state]["retained_axes_at_0p50"] == 1
                for state in CLASSICAL_CONTROLS
            ),
        },
        "C5_classical_bootstrap_at_most_2p10_fraction_at_least_0p90": {
            "values": [
                bootstrap_metrics[state]["fraction_chsh_at_most_2p10"]
                for state in CLASSICAL_CONTROLS
            ],
            "threshold": 0.90,
            "pass": all(
                bootstrap_metrics[state]["fraction_chsh_at_most_2p10"] >= 0.90
                for state in CLASSICAL_CONTROLS
            ),
        },
        "M1_uniform_chsh_at_most_0p60": {
            "value": metrics[UNIFORM_CONTROL]["chsh_smax"],
            "threshold": 0.60,
            "pass": metrics[UNIFORM_CONTROL]["chsh_smax"] <= 0.60,
        },
        "M2_uniform_s1_at_most_0p30": {
            "value": metrics[UNIFORM_CONTROL]["singular_values"][0],
            "threshold": 0.30,
            "pass": metrics[UNIFORM_CONTROL]["singular_values"][0] <= 0.30,
        },
        "M3_uniform_zero_retained_axes": {
            "value": metrics[UNIFORM_CONTROL]["retained_axes_at_0p50"],
            "target": 0,
            "pass": metrics[UNIFORM_CONTROL]["retained_axes_at_0p50"] == 0,
        },
        "M4_uniform_bootstrap_at_most_0p60_fraction_at_least_0p95": {
            "value": bootstrap_metrics[UNIFORM_CONTROL][
                "fraction_chsh_at_most_0p60"
            ],
            "threshold": 0.95,
            "pass": bootstrap_metrics[UNIFORM_CONTROL][
                "fraction_chsh_at_most_0p60"
            ]
            >= 0.95,
        },
        "O1_mean_bell_minus_classical_chsh_at_least_0p40": {
            "value": float(np.mean(bell_chsh) - np.mean(classical_chsh)),
            "threshold": 0.40,
            "pass": float(np.mean(bell_chsh) - np.mean(classical_chsh)) >= 0.40,
        },
        "O2_retained_axis_sequence_exact": {
            "value": sequence,
            "target": [3, 3, 3, 3, 1, 1, 0],
            "pass": sequence == [3, 3, 3, 3, 1, 1, 0],
        },
    }


def write_bootstrap(rows: list[dict[str, object]]) -> None:
    fields = [
        "entity",
        "entity_type",
        "replicate",
        "s1",
        "s2",
        "s3",
        "chsh_smax",
        "retained_axes_at_0p50",
    ]
    with BOOTSTRAP_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    protocol_sha = verify_protocol()
    source_md5s, q5_protocol_sha = verify_sources()
    rhos, diagnostics, q5 = point_states()
    records = load_raw_records()
    draws, bootstrap_rows = bootstrap(records)
    bootstrap_metrics = summarize_bootstrap(draws)
    metrics = {entity: state_metrics(rhos[entity]) for entity in ENTITY_ORDER}

    state_rows = []
    for entity in ENTITY_ORDER:
        row = {
            "entity": entity,
            "entity_type": (
                "physically_prepared"
                if entity in BELL_STATES
                else "equal_weight_reconstruction"
            ),
            "s1": metrics[entity]["singular_values"][0],
            "s2": metrics[entity]["singular_values"][1],
            "s3": metrics[entity]["singular_values"][2],
            "chsh_smax": metrics[entity]["chsh_smax"],
            "retained_axes_at_0p50": metrics[entity]["retained_axes_at_0p50"],
            "purity": metrics[entity]["purity"],
            "minimum_eigenvalue": metrics[entity]["minimum_eigenvalue"],
            "trace_error": metrics[entity]["trace_error"],
            "chsh_ci_low": bootstrap_metrics[entity]["chsh_95ci"][0],
            "chsh_ci_high": bootstrap_metrics[entity]["chsh_95ci"][1],
        }
        state_rows.append(row)

    with STATES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(state_rows[0]))
        writer.writeheader()
        writer.writerows(state_rows)
    write_bootstrap(bootstrap_rows)

    gate_results = gates(metrics, bootstrap_metrics)
    passed = sum(int(gate["pass"]) for gate in gate_results.values())
    total = len(gate_results)
    verdict = "SUPPORTED" if passed == total else "NOT SUPPORTED"
    results = {
        "protocol_id": "Q6B-PHYSICAL-CHSH-v1",
        "ledger_id": "T265",
        "test_class": "remedial post-hoc known-source calibration",
        "verdict": verdict,
        "gates_passed": passed,
        "gates_total": total,
        "protocol_sha256": protocol_sha,
        "q5_protocol_sha256": q5_protocol_sha,
        "source": {
            "doi": q5["source"]["doi"],
            "license": q5["source"]["license"],
            "archive_md5s": source_md5s,
        },
        "physical_projection": {
            "method": "Hermitian linear inversion followed by Euclidean eigenvalue projection onto the probability simplex",
            "tsirelson_bound": float(TSIRELSON),
            "point_state_diagnostics": diagnostics,
        },
        "bootstrap": {
            "seed": BOOTSTRAP_SEED,
            "replicates": BOOTSTRAP_REPS,
        },
        "entities": {
            entity: {
                "entity_type": (
                    "physically_prepared"
                    if entity in BELL_STATES
                    else "equal_weight_reconstruction"
                ),
                **metrics[entity],
                **bootstrap_metrics[entity],
            }
            for entity in ENTITY_ORDER
        },
        "gates": gate_results,
    }
    RESULTS_JSON.write_text(
        json.dumps(results, indent=2) + "\n", encoding="utf-8"
    )

    print(
        json.dumps(
            {
                "verdict": verdict,
                "gates": f"{passed}/{total}",
                "entities": {
                    entity: {
                        "Smax": results["entities"][entity]["chsh_smax"],
                        "Smax_95ci": results["entities"][entity]["chsh_95ci"],
                        "singular_values": results["entities"][entity][
                            "singular_values"
                        ],
                        "axes": results["entities"][entity][
                            "retained_axes_at_0p50"
                        ],
                        "purity": results["entities"][entity]["purity"],
                    }
                    for entity in ENTITY_ORDER
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
