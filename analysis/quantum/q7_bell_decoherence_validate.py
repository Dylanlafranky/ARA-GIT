#!/usr/bin/env python3
"""Independent validation for T266/Q7 Bell-decoherence results."""

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
RESULTS = HERE / "Q7_BELL_DECOHERENCE_RESULTS.json"
RECORDS = HERE / "Q7_BELL_DECOHERENCE_RECORDS.csv"
OUTPUT = HERE / "Q7_BELL_DECOHERENCE_VALIDATION.json"

EXPECTED_MD5 = {
    "MainFigure5b.csv": "3991a446f66fc244651dc3c303ea0990",
    "MainFigure5c.csv": "fc7cc2a7376d5ca1ca81c91611b38500",
    "SuppFigure5a.csv": "c198c156a7aa2235b2c3c35b6a1aaa35",
    "SuppFigure5b.csv": "55ff84cddfc6b009fcc626345195af5b",
}
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
BASIS = (
    "II", "IX", "IY", "IZ", "XI", "XX", "XY", "XZ",
    "YI", "YX", "YY", "YZ", "ZI", "ZX", "ZY", "ZZ",
)
AXES = "XYZ"
WAITS = {
    "Ramsey": [0.02, 4.02, 8.02, 12.02, 16.02, 20.02, 24.02, 28.02, 32.02, 36.02, 40.02],
    "Hahn": [1.00, 1.99, 3.98, 7.94, 15.85, 31.62, 63.09, 125.89, 251.19, 501.18, 1000.00],
}
SUPP = {"Ramsey": "SuppFigure5a.csv", "Hahn": "SuppFigure5b.csv"}
PAULI = {
    "I": np.array([[1, 0], [0, 1]], complex),
    "X": np.array([[0, 1], [1, 0]], complex),
    "Y": np.array([[0, -1j], [1j, 0]], complex),
    "Z": np.array([[1, 0], [0, -1]], complex),
}
TSIRELSON = 2 * math.sqrt(2)


def checksum(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    h.update(path.read_bytes())
    return h.hexdigest()


def simplex(values: np.ndarray) -> np.ndarray:
    u = np.sort(np.real(values))[::-1]
    cssv = np.cumsum(u)
    rho = np.nonzero(u * np.arange(1, len(u) + 1) > cssv - 1)[0][-1]
    theta = (cssv[rho] - 1) / (rho + 1)
    return np.maximum(np.real(values) - theta, 0)


def calculate(vector: list[float]) -> dict[str, float]:
    # Source values are density-expansion coefficients c_ij; c_II=1/4.
    expectations = {basis: 4 * float(value) for basis, value in zip(BASIS, vector)}
    rho = np.zeros((4, 4), complex)
    for basis, value in expectations.items():
        rho += value * np.kron(PAULI[basis[0]], PAULI[basis[1]]) / 4
    rho = (rho + rho.conj().T) / 2
    eigenvalues, eigenvectors = np.linalg.eigh(rho)
    rho = (eigenvectors * simplex(eigenvalues)) @ eigenvectors.conj().T
    rho = (rho + rho.conj().T) / 2
    tensor = np.array(
        [
            [
                np.real(np.trace(rho @ np.kron(PAULI[left], PAULI[right])))
                for right in AXES
            ]
            for left in AXES
        ],
        float,
    )
    singular = np.sort(np.linalg.svd(tensor, compute_uv=False))[::-1]
    eigenvalues = np.linalg.eigvalsh(rho)
    return {
        "s1": float(singular[0]),
        "s2": float(singular[1]),
        "s3": float(singular[2]),
        "chsh_smax": float(2 * math.sqrt(singular[0] ** 2 + singular[1] ** 2)),
        "strong_axes": int(np.sum(singular >= 0.5)),
        "trace_error": float(abs(np.trace(rho) - 1)),
        "minimum_eigenvalue": float(np.min(eigenvalues)),
        "hermiticity_residual": float(np.max(np.abs(rho - rho.conj().T))),
    }


def gmean(values: list[float]) -> float:
    return math.exp(sum(math.log(value) for value in values) / len(values))


def validate() -> dict[str, object]:
    stored = json.loads(RESULTS.read_text(encoding="utf-8"))
    with RECORDS.open(newline="", encoding="utf-8") as handle:
        stored_records = list(csv.DictReader(handle))

    recomputed = []
    cii = []
    by_condition: dict[str, dict[str, list[dict[str, float]]]] = {}
    for condition in ("Ramsey", "Hahn"):
        with (DATA / SUPP[condition]).open(newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        by_condition[condition] = {}
        for state_index, state in enumerate(STATES):
            series = []
            for index, wait in enumerate(WAITS[condition]):
                vector = [float(value) for value in ast.literal_eval(rows[5 + state_index][index])]
                cii.append(vector[0])
                metrics = calculate(vector)
                record = {
                    "condition": condition,
                    "state": state,
                    "wait_index": index,
                    "wait_us": wait,
                    **metrics,
                }
                series.append(record)
                recomputed.append(record)
            by_condition[condition][state] = series

    ramsey_cross = {}
    hahn_cross = {}
    one_axis = {}
    last_three = {}
    for condition, target in (("Ramsey", ramsey_cross), ("Hahn", hahn_cross)):
        for state in STATES:
            series = by_condition[condition][state]
            target[state] = next(
                (row["wait_us"] for row in series[1:] if row["chsh_smax"] <= 2),
                None,
            )
            last_three[(condition, state)] = max(
                (row["wait_index"] for row in series if row["strong_axes"] == 3),
                default=-1,
            )
            one_axis[(condition, state)] = next(
                (
                    row["wait_us"]
                    for row in series
                    if row["wait_index"] > last_three[(condition, state)]
                    and row["strong_axes"] == 1
                ),
                None,
            )

    s1_ret = [
        by_condition["Ramsey"][state][-1]["s1"]
        / by_condition["Ramsey"][state][0]["s1"]
        for state in STATES
    ]
    s2_ret = [
        by_condition["Ramsey"][state][-1]["s2"]
        / by_condition["Ramsey"][state][0]["s2"]
        for state in STATES
    ]
    median_s1 = float(np.median(s1_ret))
    median_s2 = float(np.median(s2_ret))
    crossing_ratio = gmean(list(hahn_cross.values())) / gmean(list(ramsey_cross.values()))

    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, value: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "value": value})

    expected_protocol = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    check("protocol_hash", checksum(PROTOCOL, "sha256") == expected_protocol, expected_protocol)
    observed_md5 = {name: checksum(DATA / name, "md5") for name in EXPECTED_MD5}
    check("source_hashes", observed_md5 == EXPECTED_MD5, observed_md5)
    check("source_cII_is_quarter", max(abs(value - 0.25) for value in cii) <= 1e-14, [min(cii), max(cii)])
    check("record_count", len(recomputed) == len(stored_records) == 88, len(recomputed))
    check(
        "record_order",
        all(
            row["condition"] == stored_row["condition"]
            and row["state"] == stored_row["state"]
            and row["wait_index"] == int(stored_row["wait_index"])
            and abs(row["wait_us"] - float(stored_row["wait_us"])) <= 1e-12
            for row, stored_row in zip(recomputed, stored_records)
        ),
        True,
    )
    for field in ("s1", "s2", "s3", "chsh_smax"):
        maximum_error = max(
            abs(row[field] - float(stored_row[field]))
            for row, stored_row in zip(recomputed, stored_records)
        )
        check(f"recompute_{field}", maximum_error <= 1e-12, maximum_error)
    check(
        "recompute_axis_counts",
        all(row["strong_axes"] == int(stored_row["strong_axes"]) for row, stored_row in zip(recomputed, stored_records)),
        True,
    )
    check("all_trace_one", max(row["trace_error"] for row in recomputed) <= 1e-12, max(row["trace_error"] for row in recomputed))
    check("all_psd", min(row["minimum_eigenvalue"] for row in recomputed) >= -1e-12, min(row["minimum_eigenvalue"] for row in recomputed))
    check("all_hermitian", max(row["hermiticity_residual"] for row in recomputed) <= 1e-12, max(row["hermiticity_residual"] for row in recomputed))
    check("all_below_tsirelson", max(row["chsh_smax"] for row in recomputed) <= TSIRELSON + 1e-12, max(row["chsh_smax"] for row in recomputed))
    check("ramsey_initial_three", all(by_condition["Ramsey"][state][0]["strong_axes"] == 3 for state in STATES), [by_condition["Ramsey"][state][0]["strong_axes"] for state in STATES])
    check("ramsey_all_cross", all(value is not None for value in ramsey_cross.values()), ramsey_cross)
    check("ramsey_all_reach_one", all(one_axis[("Ramsey", state)] is not None for state in STATES), {state: one_axis[("Ramsey", state)] for state in STATES})
    check("median_s1_retention", median_s1 >= 0.50, median_s1)
    check("median_s2_retention", median_s2 <= 0.50, median_s2)
    check("preferential_retention", median_s1 - median_s2 >= 0.20, median_s1 - median_s2)
    check(
        "chsh_after_last_three",
        all(
            next(row["wait_index"] for row in by_condition["Ramsey"][state] if row["wait_us"] == ramsey_cross[state])
            >= last_three[("Ramsey", state)]
            for state in STATES
        ),
        True,
    )
    check("hahn_initial_three", all(by_condition["Hahn"][state][0]["strong_axes"] == 3 for state in STATES), True)
    check("hahn_all_cross", all(value is not None for value in hahn_cross.values()), hahn_cross)
    check("hahn_crossing_ratio", crossing_ratio >= 4.0, crossing_ratio)
    check(
        "hahn_three_beyond_ramsey_cross",
        all(
            any(row["strong_axes"] == 3 and row["wait_us"] > ramsey_cross[state] for row in by_condition["Hahn"][state])
            for state in STATES
        ),
        True,
    )
    check("stored_primary_verdict", stored["verdict"] == "SUPPORTED", stored["verdict"])
    check("stored_echo_verdict", stored["echo_replication"] == "SUPPORTED", stored["echo_replication"])
    check(
        "stored_summary",
        abs(stored["summary"]["median_final_ramsey_s1_retention"] - median_s1) <= 1e-12
        and abs(stored["summary"]["median_final_ramsey_s2_retention"] - median_s2) <= 1e-12
        and abs(stored["summary"]["hahn_to_ramsey_crossing_ratio"] - crossing_ratio) <= 1e-12,
        stored["summary"],
    )

    result = {
        "test_id": "Q7-BELL-DECOHERENCE-v1-validation",
        "passed": all(item["passed"] for item in checks),
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    validation = validate()
    print(json.dumps({key: validation[key] for key in ("passed", "checks_passed", "checks_total")}, indent=2))

