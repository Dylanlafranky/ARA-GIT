#!/usr/bin/env python3
"""Run the frozen T266/Q7 physical Bell-decoherence trajectory test."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "public_data" / "q7_bell_lifetime"
PROTOCOL = HERE / "Q7_BELL_DECOHERENCE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q7_BELL_DECOHERENCE_PROTOCOL_v1_FROZEN.sha256"
RECORDS_CSV = HERE / "Q7_BELL_DECOHERENCE_RECORDS.csv"
GATES_CSV = HERE / "Q7_BELL_DECOHERENCE_GATES.csv"
RESULTS_JSON = HERE / "Q7_BELL_DECOHERENCE_RESULTS.json"

EXPECTED_MD5 = {
    "MainFigure5b.csv": "3991a446f66fc244651dc3c303ea0990",
    "MainFigure5c.csv": "fc7cc2a7376d5ca1ca81c91611b38500",
    "SuppFigure5a.csv": "c198c156a7aa2235b2c3c35b6a1aaa35",
    "SuppFigure5b.csv": "55ff84cddfc6b009fcc626345195af5b",
}

STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
BASIS = (
    "II", "IX", "IY", "IZ",
    "XI", "XX", "XY", "XZ",
    "YI", "YX", "YY", "YZ",
    "ZI", "ZX", "ZY", "ZZ",
)
AXES = ("X", "Y", "Z")
WAITS = {
    "Ramsey": np.asarray(
        [0.02, 4.02, 8.02, 12.02, 16.02, 20.02, 24.02, 28.02, 32.02, 36.02, 40.02],
        dtype=np.float64,
    ),
    "Hahn": np.asarray(
        [1.00, 1.99, 3.98, 7.94, 15.85, 31.62, 63.09, 125.89, 251.19, 501.18, 1000.00],
        dtype=np.float64,
    ),
}
FILES = {
    "Ramsey": ("SuppFigure5a.csv", "MainFigure5b.csv"),
    "Hahn": ("SuppFigure5b.csv", "MainFigure5c.csv"),
}
STRONG_AXIS_THRESHOLD = 0.50
TSIRELSON = 2.0 * math.sqrt(2.0)
PAULI = {
    "I": np.asarray([[1, 0], [0, 1]], dtype=np.complex128),
    "X": np.asarray([[0, 1], [1, 0]], dtype=np.complex128),
    "Y": np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128),
    "Z": np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
}


def digest(path: Path, algorithm: str) -> str:
    hasher = hashlib.new(algorithm)
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def verify_inputs() -> dict[str, str]:
    expected_protocol = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed_protocol = digest(PROTOCOL, "sha256")
    if expected_protocol != observed_protocol:
        raise RuntimeError(
            f"Frozen protocol mismatch: {observed_protocol} != {expected_protocol}"
        )
    observed = {}
    for name, expected in EXPECTED_MD5.items():
        value = digest(DATA / name, "md5")
        if value != expected:
            raise RuntimeError(f"Source checksum mismatch for {name}: {value} != {expected}")
        observed[name] = value
    observed["protocol_sha256"] = observed_protocol
    return observed


def project_to_simplex(values: np.ndarray) -> np.ndarray:
    ordered = np.sort(np.real(values))[::-1]
    cumulative = np.cumsum(ordered)
    eligible = ordered - (cumulative - 1.0) / np.arange(1, len(values) + 1) > 0
    if not np.any(eligible):
        raise RuntimeError("Probability-simplex projection found no active eigenvalue")
    active = int(np.flatnonzero(eligible)[-1] + 1)
    theta = float((cumulative[active - 1] - 1.0) / active)
    return np.maximum(np.real(values) - theta, 0.0)


def density_from_expectations(expectations: dict[str, float]) -> np.ndarray:
    rho = np.zeros((4, 4), dtype=np.complex128)
    for basis, value in expectations.items():
        rho += value * np.kron(PAULI[basis[0]], PAULI[basis[1]])
    return 0.25 * rho


def physical_projection(rho_linear: np.ndarray) -> np.ndarray:
    rho_h = 0.5 * (rho_linear + rho_linear.conj().T)
    eigenvalues, eigenvectors = np.linalg.eigh(rho_h)
    projected = project_to_simplex(eigenvalues)
    rho = (eigenvectors * projected) @ eigenvectors.conj().T
    return 0.5 * (rho + rho.conj().T)


def expectation(rho: np.ndarray, basis: str) -> float:
    return float(
        np.real(np.trace(rho @ np.kron(PAULI[basis[0]], PAULI[basis[1]])))
    )


def metrics(rho: np.ndarray) -> dict[str, object]:
    tensor = np.asarray(
        [[expectation(rho, left + right) for right in AXES] for left in AXES],
        dtype=np.float64,
    )
    singular = np.sort(np.linalg.svd(tensor, compute_uv=False))[::-1]
    eigenvalues = np.linalg.eigvalsh(rho)
    return {
        "singular_values": [float(value) for value in singular],
        "chsh_smax": float(2.0 * math.sqrt(singular[0] ** 2 + singular[1] ** 2)),
        "strong_axes": int(np.sum(singular >= STRONG_AXIS_THRESHOLD)),
        "trace": float(np.real(np.trace(rho))),
        "trace_error": float(abs(np.trace(rho) - 1.0)),
        "minimum_eigenvalue": float(np.min(eigenvalues)),
        "hermiticity_residual": float(np.max(np.abs(rho - rho.conj().T))),
        "purity": float(np.real(np.trace(rho @ rho))),
        "tensor": tensor.tolist(),
    }


def load_condition(condition: str) -> tuple[list[list[list[float]]], list[list[float]], list[list[float]]]:
    supp_name, main_name = FILES[condition]
    with (DATA / supp_name).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    if len(rows) != 9 or any(len(row) != 11 for row in rows):
        raise RuntimeError(f"Unexpected supplementary schema for {supp_name}")

    aggregate = [[float(value) for value in rows[index]] for index in range(4)]
    pauli: list[list[list[float]]] = []
    for state_index in range(4):
        trajectory = []
        for cell in rows[5 + state_index]:
            vector = [float(value) for value in ast.literal_eval(cell)]
            if len(vector) != 16:
                raise RuntimeError(
                    f"Expected 16 Pauli coefficients, got {len(vector)} in {supp_name}"
                )
            trajectory.append(vector)
        pauli.append(trajectory)

    with (DATA / main_name).open(newline="", encoding="utf-8") as handle:
        main_rows = [[float(value) for value in row] for row in csv.reader(handle)]
    if len(main_rows) != 4 or any(len(row) != 11 for row in main_rows):
        raise RuntimeError(f"Unexpected main-figure schema for {main_name}")
    return pauli, aggregate, main_rows


def first_chsh_cross(records: list[dict[str, object]]) -> dict[str, object] | None:
    if not records or float(records[0]["chsh_smax"]) <= 2.0:
        return None
    for record in records[1:]:
        if float(record["chsh_smax"]) <= 2.0:
            return record
    return None


def geometric_mean(values: list[float]) -> float:
    return float(math.exp(sum(math.log(value) for value in values) / len(values)))


def evaluate_gate(gate_id: str, description: str, passed: bool, value: object) -> dict[str, object]:
    return {
        "gate_id": gate_id,
        "description": description,
        "passed": bool(passed),
        "value": value,
    }


def run() -> dict[str, object]:
    source_hashes = verify_inputs()
    records: list[dict[str, object]] = []
    by_condition: dict[str, dict[str, list[dict[str, object]]]] = {}
    source_cii: list[float] = []

    for condition in ("Ramsey", "Hahn"):
        pauli, aggregate, reported = load_condition(condition)
        by_condition[condition] = {}
        for state_index, state in enumerate(STATES):
            state_records = []
            for wait_index, wait_us in enumerate(WAITS[condition]):
                source_cii.append(float(pauli[state_index][wait_index][0]))
                # The source heatmap stores density-expansion coefficients c_ij,
                # not normalized Pauli expectations. Its invariant c_II = 0.25
                # fixes the exact conversion <ij> = 4*c_ij, with <II> = 1.
                exp = {
                    basis: 4.0 * coefficient
                    for basis, coefficient in zip(
                        BASIS, pauli[state_index][wait_index]
                    )
                }
                rho_linear = density_from_expectations(exp)
                linear_min_eigenvalue = float(
                    np.min(np.linalg.eigvalsh(0.5 * (rho_linear + rho_linear.conj().T)))
                )
                rho = physical_projection(rho_linear)
                met = metrics(rho)
                singular = met["singular_values"]
                record = {
                    "condition": condition,
                    "state": state,
                    "wait_index": wait_index,
                    "wait_us": float(wait_us),
                    "split": (
                        "development"
                        if condition == "Ramsey" and wait_index <= 4
                        else "target"
                        if condition == "Ramsey"
                        else "intervention_replication"
                    ),
                    "source_aggregate_norm": aggregate[state_index][wait_index],
                    "source_reported_bell_signal": reported[state_index][wait_index],
                    "linear_minimum_eigenvalue": linear_min_eigenvalue,
                    "s1": singular[0],
                    "s2": singular[1],
                    "s3": singular[2],
                    "chsh_smax": met["chsh_smax"],
                    "strong_axes": met["strong_axes"],
                    "trace": met["trace"],
                    "trace_error": met["trace_error"],
                    "minimum_eigenvalue": met["minimum_eigenvalue"],
                    "hermiticity_residual": met["hermiticity_residual"],
                    "purity": met["purity"],
                }
                records.append(record)
                state_records.append(record)
            by_condition[condition][state] = state_records

    crossings: dict[str, dict[str, object]] = {"Ramsey": {}, "Hahn": {}}
    state_summaries: dict[str, dict[str, object]] = {"Ramsey": {}, "Hahn": {}}
    for condition in ("Ramsey", "Hahn"):
        for state in STATES:
            state_records = by_condition[condition][state]
            cross = first_chsh_cross(state_records)
            crossing = {
                "found": cross is not None,
                "wait_us": None if cross is None else float(cross["wait_us"]),
                "wait_index": None if cross is None else int(cross["wait_index"]),
            }
            crossings[condition][state] = crossing
            initial = state_records[0]
            final = state_records[-1]
            last_three = max(
                (
                    int(record["wait_index"])
                    for record in state_records
                    if int(record["strong_axes"]) == 3
                ),
                default=-1,
            )
            first_one_after_three = next(
                (
                    record
                    for record in state_records
                    if int(record["wait_index"]) > last_three
                    and int(record["strong_axes"]) == 1
                ),
                None,
            )
            state_summaries[condition][state] = {
                "initial_strong_axes": int(initial["strong_axes"]),
                "final_strong_axes": int(final["strong_axes"]),
                "initial_s1": float(initial["s1"]),
                "initial_s2": float(initial["s2"]),
                "initial_s3": float(initial["s3"]),
                "final_s1": float(final["s1"]),
                "final_s2": float(final["s2"]),
                "final_s3": float(final["s3"]),
                "final_s1_retention": float(final["s1"]) / float(initial["s1"]),
                "final_s2_retention": float(final["s2"]) / float(initial["s2"]),
                "final_s3_retention": float(final["s3"]) / float(initial["s3"]),
                "last_three_axis_index": last_three,
                "last_three_axis_wait_us": (
                    None if last_three < 0 else float(state_records[last_three]["wait_us"])
                ),
                "one_axis_after_last_three": first_one_after_three is not None,
                "first_one_axis_wait_us": (
                    None
                    if first_one_after_three is None
                    else float(first_one_after_three["wait_us"])
                ),
                "first_chsh_failure_wait_us": crossing["wait_us"],
            }

    ramsey_s1_retention = [
        state_summaries["Ramsey"][state]["final_s1_retention"] for state in STATES
    ]
    ramsey_s2_retention = [
        state_summaries["Ramsey"][state]["final_s2_retention"] for state in STATES
    ]
    median_s1_retention = float(np.median(ramsey_s1_retention))
    median_s2_retention = float(np.median(ramsey_s2_retention))

    physicality_ok = all(
        float(record["trace_error"]) <= 1e-12
        and float(record["minimum_eigenvalue"]) >= -1e-12
        and float(record["hermiticity_residual"]) <= 1e-12
        and float(record["chsh_smax"]) <= TSIRELSON + 1e-12
        for record in records
    )
    ramsey_cross_times = [
        float(crossings["Ramsey"][state]["wait_us"])
        for state in STATES
        if crossings["Ramsey"][state]["found"]
    ]
    hahn_cross_times = [
        float(crossings["Hahn"][state]["wait_us"])
        for state in STATES
        if crossings["Hahn"][state]["found"]
    ]
    crossing_ratio = (
        geometric_mean(hahn_cross_times) / geometric_mean(ramsey_cross_times)
        if len(ramsey_cross_times) == 4 and len(hahn_cross_times) == 4
        else float("nan")
    )

    gates = [
        evaluate_gate("P1", "all 88 physical reconstructions pass", physicality_ok, physicality_ok),
        evaluate_gate(
            "P2",
            "all Ramsey states begin with three strong axes",
            all(state_summaries["Ramsey"][state]["initial_strong_axes"] == 3 for state in STATES),
            [state_summaries["Ramsey"][state]["initial_strong_axes"] for state in STATES],
        ),
        evaluate_gate(
            "P3",
            "all Ramsey states cross CHSH within sampled interval",
            len(ramsey_cross_times) == 4,
            crossings["Ramsey"],
        ),
        evaluate_gate(
            "P4",
            "all Ramsey states exhibit one axis after their last three-axis observation",
            all(state_summaries["Ramsey"][state]["one_axis_after_last_three"] for state in STATES),
            {
                state: state_summaries["Ramsey"][state]["first_one_axis_wait_us"]
                for state in STATES
            },
        ),
        evaluate_gate(
            "P5",
            "median final Ramsey s1 retention >= 0.50",
            median_s1_retention >= 0.50,
            median_s1_retention,
        ),
        evaluate_gate(
            "P6",
            "median final Ramsey s2 retention <= 0.50",
            median_s2_retention <= 0.50,
            median_s2_retention,
        ),
        evaluate_gate(
            "P7",
            "preferential retention gap >= 0.20",
            median_s1_retention - median_s2_retention >= 0.20,
            median_s1_retention - median_s2_retention,
        ),
        evaluate_gate(
            "P8",
            "CHSH failure is not earlier than last three-axis observation",
            all(
                crossings["Ramsey"][state]["found"]
                and int(crossings["Ramsey"][state]["wait_index"])
                >= int(state_summaries["Ramsey"][state]["last_three_axis_index"])
                for state in STATES
            ),
            {
                state: {
                    "last_three_axis_index": state_summaries["Ramsey"][state][
                        "last_three_axis_index"
                    ],
                    "chsh_failure_index": crossings["Ramsey"][state]["wait_index"],
                }
                for state in STATES
            },
        ),
        evaluate_gate(
            "E1",
            "all Hahn states begin with three strong axes",
            all(state_summaries["Hahn"][state]["initial_strong_axes"] == 3 for state in STATES),
            [state_summaries["Hahn"][state]["initial_strong_axes"] for state in STATES],
        ),
        evaluate_gate(
            "E2",
            "all Hahn states cross CHSH within sampled interval",
            len(hahn_cross_times) == 4,
            crossings["Hahn"],
        ),
        evaluate_gate(
            "E3",
            "Hahn/Ramsey crossing-time geometric-mean ratio >= 4",
            math.isfinite(crossing_ratio) and crossing_ratio >= 4.0,
            crossing_ratio,
        ),
        evaluate_gate(
            "E4",
            "each Hahn state retains three axes beyond its Ramsey crossing time",
            all(
                any(
                    int(record["strong_axes"]) == 3
                    and float(record["wait_us"])
                    > float(crossings["Ramsey"][state]["wait_us"])
                    for record in by_condition["Hahn"][state]
                )
                for state in STATES
                if crossings["Ramsey"][state]["found"]
            )
            and len(ramsey_cross_times) == 4,
            {
                state: {
                    "ramsey_cross_us": crossings["Ramsey"][state]["wait_us"],
                    "latest_hahn_three_axis_us": max(
                        (
                            float(record["wait_us"])
                            for record in by_condition["Hahn"][state]
                            if int(record["strong_axes"]) == 3
                        ),
                        default=None,
                    ),
                }
                for state in STATES
            },
        ),
    ]

    primary_pass = all(gate["passed"] for gate in gates if gate["gate_id"].startswith("P"))
    echo_pass = all(gate["passed"] for gate in gates if gate["gate_id"].startswith("E"))
    result = {
        "test_id": "Q7-BELL-DECOHERENCE-v1",
        "ledger_id": "T266",
        "verdict": "SUPPORTED" if primary_pass else "NOT SUPPORTED",
        "echo_replication": "SUPPORTED" if echo_pass else "NOT SUPPORTED",
        "test_class": "public-data, partially blinded reanalysis",
        "source_hashes": source_hashes,
        "schema_unit_correction": {
            "source_cII_min": min(source_cii),
            "source_cII_max": max(source_cii),
            "source_cII_expected": 0.25,
            "conversion": "<ij> = 4*c_ij",
            "normalized_II_after_conversion": 1.0,
            "gates_changed": False,
        },
        "strong_axis_threshold": STRONG_AXIS_THRESHOLD,
        "state_summaries": state_summaries,
        "crossings": crossings,
        "summary": {
            "median_final_ramsey_s1_retention": median_s1_retention,
            "median_final_ramsey_s2_retention": median_s2_retention,
            "preferential_retention_gap": median_s1_retention - median_s2_retention,
            "ramsey_crossing_geometric_mean_us": (
                geometric_mean(ramsey_cross_times) if len(ramsey_cross_times) == 4 else None
            ),
            "hahn_crossing_geometric_mean_us": (
                geometric_mean(hahn_cross_times) if len(hahn_cross_times) == 4 else None
            ),
            "hahn_to_ramsey_crossing_ratio": crossing_ratio,
            "primary_gates_passed": sum(
                gate["passed"] for gate in gates if gate["gate_id"].startswith("P")
            ),
            "primary_gates_total": sum(
                gate["gate_id"].startswith("P") for gate in gates
            ),
            "echo_gates_passed": sum(
                gate["passed"] for gate in gates if gate["gate_id"].startswith("E")
            ),
            "echo_gates_total": sum(
                gate["gate_id"].startswith("E") for gate in gates
            ),
        },
        "gates": gates,
    }

    fieldnames = list(records[0])
    with RECORDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
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
    outcome = run()
    print(json.dumps(outcome["summary"], indent=2))
    print(f"Primary verdict: {outcome['verdict']}")
    print(f"Echo replication: {outcome['echo_replication']}")
