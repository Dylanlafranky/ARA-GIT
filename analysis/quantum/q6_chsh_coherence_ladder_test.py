#!/usr/bin/env python3
"""Run the frozen T264/Q6 CHSH coherence-ladder calibration."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from q4_bell_parent_child_test import expectations, probabilities_from_records
from q5_bell_four_state_test import STATE_CONFIGS, load_state, verify_sources


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q6_CHSH_COHERENCE_LADDER_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q6_CHSH_COHERENCE_LADDER_PROTOCOL_v1_FROZEN.sha256"
Q5_RESULTS = HERE / "Q5_BELL_FOUR_STATE_RESULTS.json"
TENSORS_CSV = HERE / "Q6_CHSH_COHERENCE_LADDER_TENSORS.csv"
BOOTSTRAP_CSV = HERE / "Q6_CHSH_COHERENCE_LADDER_BOOTSTRAP.csv"
RESULTS_JSON = HERE / "Q6_CHSH_COHERENCE_LADDER_RESULTS.json"

BOOTSTRAP_SEED = 2026072406
BOOTSTRAP_REPS = 5000
STRONG_AXIS_THRESHOLD = 0.50
BELL_STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
CLASSICAL_CONTROLS = ("Phi-classical", "Psi-classical")
UNIFORM_CONTROL = "Bell-uniform-mixed"
ENTITY_ORDER = (*BELL_STATES, *CLASSICAL_CONTROLS, UNIFORM_CONTROL)
TENSOR_LABELS = (
    ("XX", "XY", "XZ"),
    ("YX", "YY", "YZ"),
    ("ZX", "ZY", "ZZ"),
)
CONTROL_WEIGHTS = {
    "Phi-classical": {"Phi-plus": 0.5, "Phi-minus": 0.5},
    "Psi-classical": {"Psi-plus": 0.5, "Psi-minus": 0.5},
    "Bell-uniform-mixed": {
        "Phi-plus": 0.25,
        "Phi-minus": 0.25,
        "Psi-plus": 0.25,
        "Psi-minus": 0.25,
    },
}


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
            f"Frozen Q6 protocol mismatch: expected {expected}, observed {observed}"
        )
    return observed


def tensor_from_expectations(exp: dict[str, float]) -> np.ndarray:
    return np.asarray(
        [[exp[label] for label in row] for row in TENSOR_LABELS],
        dtype=np.float64,
    )


def weighted_tensor(
    state_tensors: dict[str, np.ndarray], weights: dict[str, float]
) -> np.ndarray:
    return sum(
        (weight * state_tensors[state] for state, weight in weights.items()),
        start=np.zeros((3, 3), dtype=np.float64),
    )


def tensor_metrics(tensor: np.ndarray) -> dict[str, object]:
    singular = np.linalg.svd(tensor, compute_uv=False)
    singular = np.sort(singular)[::-1]
    chsh = float(2.0 * np.sqrt(singular[0] ** 2 + singular[1] ** 2))
    return {
        "singular_values": [float(value) for value in singular],
        "chsh_smax": chsh,
        "retained_axes_at_0p50": int(np.sum(singular >= STRONG_AXIS_THRESHOLD)),
        "frobenius_norm": float(np.linalg.norm(tensor, ord="fro")),
        "determinant": float(np.linalg.det(tensor)),
    }


def point_tensors() -> tuple[dict[str, np.ndarray], dict[str, object]]:
    q5 = json.loads(Q5_RESULTS.read_text(encoding="utf-8"))
    state_tensors = {
        state: tensor_from_expectations(q5["states"][state]["expectations"])
        for state in BELL_STATES
    }
    all_tensors = dict(state_tensors)
    for control, weights in CONTROL_WEIGHTS.items():
        all_tensors[control] = weighted_tensor(state_tensors, weights)
    return all_tensors, q5


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
        state_tensors = {}
        for state in BELL_STATES:
            probabilities = {}
            for orientation, values in records[state].items():
                indices = rng.integers(0, len(values), size=len(values))
                probabilities[orientation] = values[indices].mean(axis=0)
            state_tensors[state] = tensor_from_expectations(
                expectations(probabilities)
            )

        tensors = dict(state_tensors)
        for control, weights in CONTROL_WEIGHTS.items():
            tensors[control] = weighted_tensor(state_tensors, weights)

        for entity in ENTITY_ORDER:
            metrics = tensor_metrics(tensors[entity])
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


def percentile_interval(values: np.ndarray) -> list[float]:
    low, high = np.percentile(values, [2.5, 97.5])
    return [float(low), float(high)]


def bootstrap_summary(
    draws: dict[str, dict[str, np.ndarray]]
) -> dict[str, dict[str, object]]:
    summary = {}
    for entity in ENTITY_ORDER:
        entity_draws = draws[entity]
        chsh = entity_draws["chsh_smax"]
        summary[entity] = {
            "chsh_95ci": percentile_interval(chsh),
            "s1_95ci": percentile_interval(entity_draws["s1"]),
            "s2_95ci": percentile_interval(entity_draws["s2"]),
            "s3_95ci": percentile_interval(entity_draws["s3"]),
            "fraction_chsh_above_2p00": float(np.mean(chsh > 2.0)),
            "fraction_chsh_at_most_2p10": float(np.mean(chsh <= 2.1)),
            "fraction_chsh_at_most_0p50": float(np.mean(chsh <= 0.5)),
            "modal_retained_axes": int(
                np.bincount(entity_draws["retained_axes"], minlength=4).argmax()
            ),
        }
    return summary


def evaluate_gates(
    metrics: dict[str, dict[str, object]],
    bootstrap_metrics: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    bell_chsh = [float(metrics[state]["chsh_smax"]) for state in BELL_STATES]
    classical_chsh = [
        float(metrics[state]["chsh_smax"]) for state in CLASSICAL_CONTROLS
    ]
    sequence = [
        int(metrics[entity]["retained_axes_at_0p50"]) for entity in ENTITY_ORDER
    ]

    return {
        "B1_all_four_bell_chsh_above_2p00": {
            "values": bell_chsh,
            "threshold": 2.0,
            "pass": all(value > 2.0 for value in bell_chsh),
        },
        "B2_all_four_bell_chsh_at_least_2p30": {
            "values": bell_chsh,
            "threshold": 2.3,
            "pass": all(value >= 2.3 for value in bell_chsh),
        },
        "B3_all_four_bell_s2_at_least_0p50": {
            "values": [metrics[state]["singular_values"][1] for state in BELL_STATES],
            "threshold": 0.5,
            "pass": all(
                metrics[state]["singular_values"][1] >= 0.5
                for state in BELL_STATES
            ),
        },
        "B4_all_four_bell_have_three_retained_axes": {
            "values": [
                metrics[state]["retained_axes_at_0p50"] for state in BELL_STATES
            ],
            "target": 3,
            "pass": all(
                metrics[state]["retained_axes_at_0p50"] == 3
                for state in BELL_STATES
            ),
        },
        "B5_each_bell_bootstrap_chsh_violation_at_least_0p95": {
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
        "C1_both_classical_chsh_at_most_2p00": {
            "values": classical_chsh,
            "threshold": 2.0,
            "pass": all(value <= 2.0 for value in classical_chsh),
        },
        "C2_both_classical_s1_at_least_0p75": {
            "values": [
                metrics[state]["singular_values"][0]
                for state in CLASSICAL_CONTROLS
            ],
            "threshold": 0.75,
            "pass": all(
                metrics[state]["singular_values"][0] >= 0.75
                for state in CLASSICAL_CONTROLS
            ),
        },
        "C3_both_classical_s2_at_most_0p25": {
            "values": [
                metrics[state]["singular_values"][1]
                for state in CLASSICAL_CONTROLS
            ],
            "threshold": 0.25,
            "pass": all(
                metrics[state]["singular_values"][1] <= 0.25
                for state in CLASSICAL_CONTROLS
            ),
        },
        "C4_both_classical_have_one_retained_axis": {
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
        "C5_each_classical_bootstrap_at_most_2p10_at_least_0p90": {
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
        "M1_uniform_chsh_at_most_0p50": {
            "value": metrics[UNIFORM_CONTROL]["chsh_smax"],
            "threshold": 0.5,
            "pass": metrics[UNIFORM_CONTROL]["chsh_smax"] <= 0.5,
        },
        "M2_uniform_s1_at_most_0p25": {
            "value": metrics[UNIFORM_CONTROL]["singular_values"][0],
            "threshold": 0.25,
            "pass": metrics[UNIFORM_CONTROL]["singular_values"][0] <= 0.25,
        },
        "M3_uniform_has_zero_retained_axes": {
            "value": metrics[UNIFORM_CONTROL]["retained_axes_at_0p50"],
            "target": 0,
            "pass": metrics[UNIFORM_CONTROL]["retained_axes_at_0p50"] == 0,
        },
        "M4_uniform_bootstrap_at_most_0p50_at_least_0p95": {
            "value": bootstrap_metrics[UNIFORM_CONTROL][
                "fraction_chsh_at_most_0p50"
            ],
            "threshold": 0.95,
            "pass": bootstrap_metrics[UNIFORM_CONTROL][
                "fraction_chsh_at_most_0p50"
            ]
            >= 0.95,
        },
        "O1_mean_bell_minus_classical_chsh_at_least_0p50": {
            "value": float(np.mean(bell_chsh) - np.mean(classical_chsh)),
            "threshold": 0.5,
            "pass": float(np.mean(bell_chsh) - np.mean(classical_chsh)) >= 0.5,
        },
        "O2_retained_axis_sequence_exact": {
            "value": sequence,
            "target": [3, 3, 3, 3, 1, 1, 0],
            "pass": sequence == [3, 3, 3, 3, 1, 1, 0],
        },
    }


def write_csv(
    path: Path, rows: list[dict[str, object]], fields: list[str]
) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    protocol_sha = verify_protocol()
    source_md5s, q5_protocol_sha = verify_sources()
    tensors, q5 = point_tensors()
    records = load_raw_records()
    draws, bootstrap_rows = bootstrap(records)
    bootstrap_metrics = bootstrap_summary(draws)
    metrics = {entity: tensor_metrics(tensors[entity]) for entity in ENTITY_ORDER}

    tensor_rows = []
    for entity in ENTITY_ORDER:
        tensor = tensors[entity]
        for row_index, row_name in enumerate(("X", "Y", "Z")):
            for column_index, column_name in enumerate(("X", "Y", "Z")):
                tensor_rows.append(
                    {
                        "entity": entity,
                        "entity_type": (
                            "physically_prepared"
                            if entity in BELL_STATES
                            else "equal_weight_reconstruction"
                        ),
                        "row_axis": row_name,
                        "column_axis": column_name,
                        "projection": row_name + column_name,
                        "expectation": float(tensor[row_index, column_index]),
                    }
                )

    gates = evaluate_gates(metrics, bootstrap_metrics)
    passed = sum(int(gate["pass"]) for gate in gates.values())
    total = len(gates)
    verdict = "SUPPORTED" if passed == total else "NOT SUPPORTED"

    write_csv(
        TENSORS_CSV,
        tensor_rows,
        [
            "entity",
            "entity_type",
            "row_axis",
            "column_axis",
            "projection",
            "expectation",
        ],
    )
    write_csv(
        BOOTSTRAP_CSV,
        bootstrap_rows,
        [
            "entity",
            "entity_type",
            "replicate",
            "s1",
            "s2",
            "s3",
            "chsh_smax",
            "retained_axes_at_0p50",
        ],
    )

    results = {
        "protocol_id": "Q6-CHSH-COHERENCE-v1",
        "ledger_id": "T264",
        "test_class": (
            "post-Q5 known-source calibration with physically prepared Bell rows "
            "and equal-weight reconstructed controls"
        ),
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
                "tensor": tensors[entity].tolist(),
                **metrics[entity],
                **bootstrap_metrics[entity],
            }
            for entity in ENTITY_ORDER
        },
        "gates": gates,
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
                        "singular_values": results["entities"][entity][
                            "singular_values"
                        ],
                        "axes": results["entities"][entity][
                            "retained_axes_at_0p50"
                        ],
                        "Smax_95ci": results["entities"][entity]["chsh_95ci"],
                    }
                    for entity in ENTITY_ORDER
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
