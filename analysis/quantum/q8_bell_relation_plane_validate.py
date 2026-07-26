#!/usr/bin/env python3
"""Independent arithmetic and source-data validation for Q8."""

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
PROTOCOL = HERE / "Q8_BELL_RELATION_PLANE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q8_BELL_RELATION_PLANE_PROTOCOL_v1_FROZEN.sha256"
RECORDS = HERE / "Q8_BELL_RELATION_PLANE_RECORDS.csv"
RESULTS = HERE / "Q8_BELL_RELATION_PLANE_RESULTS.json"
OUTPUT = HERE / "Q8_BELL_RELATION_PLANE_VALIDATION.json"

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
        [0.02, 4.02, 8.02, 12.02, 16.02, 20.02, 24.02, 28.02, 32.02, 36.02, 40.02]
    ),
    "Hahn": np.asarray(
        [1.00, 1.99, 3.98, 7.94, 15.85, 31.62, 63.09, 125.89, 251.19, 501.18, 1000.00]
    ),
}
FILES = {
    "Ramsey": "SuppFigure5a.csv",
    "Hahn": "SuppFigure5b.csv",
}
PAULI = {
    "I": np.asarray([[1, 0], [0, 1]], dtype=complex),
    "X": np.asarray([[0, 1], [1, 0]], dtype=complex),
    "Y": np.asarray([[0, -1j], [1j, 0]], dtype=complex),
    "Z": np.asarray([[1, 0], [0, -1]], dtype=complex),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def simplex_projection(values: np.ndarray) -> np.ndarray:
    ordered = np.sort(np.real(values))[::-1]
    cumulative = np.cumsum(ordered)
    eligible = ordered - (cumulative - 1) / np.arange(1, len(values) + 1) > 0
    active = int(np.flatnonzero(eligible)[-1] + 1)
    theta = float((cumulative[active - 1] - 1) / active)
    return np.maximum(np.real(values) - theta, 0)


def make_physical_density(coefficients: list[float]) -> np.ndarray:
    rho_linear = np.zeros((4, 4), dtype=complex)
    for basis, coefficient in zip(BASIS, coefficients):
        expectation = 4 * coefficient
        rho_linear += expectation * np.kron(PAULI[basis[0]], PAULI[basis[1]])
    rho_linear *= 0.25
    hermitian = 0.5 * (rho_linear + rho_linear.conj().T)
    values, vectors = np.linalg.eigh(hermitian)
    projected = simplex_projection(values)
    rho = (vectors * projected) @ vectors.conj().T
    return 0.5 * (rho + rho.conj().T)


def expectation(rho: np.ndarray, basis: str) -> float:
    operator = np.kron(PAULI[basis[0]], PAULI[basis[1]])
    return float(np.real(np.trace(rho @ operator)))


def source_coefficients(condition: str) -> list[list[list[float]]]:
    with (DATA / FILES[condition]).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.reader(handle))
    return [
        [[float(value) for value in ast.literal_eval(cell)] for cell in rows[5 + state]]
        for state in range(4)
    ]


def independently_calculate(state: str, coefficients: list[float]) -> dict[str, float]:
    rho = make_physical_density(coefficients)
    tensor = np.asarray(
        [[expectation(rho, left + right) for right in AXES] for left in AXES]
    )
    xx, xy, _ = tensor[0]
    yx, yy, _ = tensor[1]
    _, _, zz = tensor[2]
    core = np.zeros((3, 3))
    if state.startswith("Phi"):
        u = (xx - yy) / 2
        v = (xy + yx) / 2
        alternate = math.hypot((xx + yy) / 2, (yx - xy) / 2)
        core[0, 0], core[1, 1] = u, -u
        core[0, 1] = core[1, 0] = v
    else:
        u = (xx + yy) / 2
        v = (yx - xy) / 2
        alternate = math.hypot((xx - yy) / 2, (xy + yx) / 2)
        core[0, 0] = core[1, 1] = u
        core[0, 1], core[1, 0] = -v, v
    core[2, 2] = zz
    radius = math.hypot(u, v)
    k = abs(zz)
    energy = float(np.sum(tensor**2))
    singular = np.sort(np.linalg.svd(tensor, compute_uv=False))[::-1]
    transverse = float((singular[1] + singular[2]) / 2)
    inferred_v = math.sqrt(max(0, transverse**2 - u**2))
    return {
        "u": u,
        "v": v,
        "radius": radius,
        "theta_rad": math.atan2(v, u),
        "k": k,
        "te_observed": k + radius,
        "hidden_residual": 2 - k - radius,
        "alt_radius": alternate,
        "core_share": 1 - float(np.sum((tensor - core) ** 2)) / energy,
        "s1": float(singular[0]),
        "s2": float(singular[1]),
        "s3": float(singular[2]),
        "inferred_v_magnitude": inferred_v,
        "hidden_quadrature_abs_error": abs(inferred_v - abs(v)),
    }


def geometric_mean(values: list[float]) -> float:
    return math.exp(sum(math.log(value) for value in values) / len(values))


def first_index(rows: list[dict[str, float]], key: str, predicate) -> int | None:
    for index, row in enumerate(rows):
        if predicate(row[key]):
            return index
    return None


def main() -> None:
    expected_hash = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed_hash = digest(PROTOCOL)
    if expected_hash != observed_hash:
        raise RuntimeError("Frozen Q8 protocol hash mismatch")

    with RECORDS.open(newline="", encoding="utf-8") as handle:
        saved = list(csv.DictReader(handle))
    saved_by_key = {
        (row["condition"], row["state"], int(row["wait_index"])): row for row in saved
    }
    if len(saved_by_key) != 88:
        raise RuntimeError(f"Expected 88 unique records; found {len(saved_by_key)}")

    recomputed: dict[str, dict[str, list[dict[str, float]]]] = {
        "Ramsey": {state: [] for state in STATES},
        "Hahn": {state: [] for state in STATES},
    }
    checked_fields = (
        "u", "v", "radius", "theta_rad", "k", "te_observed",
        "hidden_residual", "alt_radius", "core_share", "s1", "s2", "s3",
        "inferred_v_magnitude", "hidden_quadrature_abs_error",
    )
    maximum_saved_difference = 0.0
    for condition in ("Ramsey", "Hahn"):
        source = source_coefficients(condition)
        for state_index, state in enumerate(STATES):
            for wait_index, coefficients in enumerate(source[state_index]):
                values = independently_calculate(state, coefficients)
                values["wait_us"] = float(WAITS[condition][wait_index])
                values["strong_axes"] = int(
                    sum(values[key] >= 0.50 for key in ("s1", "s2", "s3"))
                )
                recomputed[condition][state].append(values)
                saved_row = saved_by_key[(condition, state, wait_index)]
                for field in checked_fields:
                    difference = abs(values[field] - float(saved_row[field]))
                    maximum_saved_difference = max(maximum_saved_difference, difference)

    core_medians = {
        condition: float(
            np.median(
                [
                    row["core_share"]
                    for state in STATES
                    for row in recomputed[condition][state]
                ]
            )
        )
        for condition in ("Ramsey", "Hahn")
    }
    initial = {
        condition: {state: recomputed[condition][state][0] for state in STATES}
        for condition in ("Ramsey", "Hahn")
    }
    final_ramsey = {state: recomputed["Ramsey"][state][-1] for state in STATES}
    k_retention = {
        state: final_ramsey[state]["k"] / initial["Ramsey"][state]["k"]
        for state in STATES
    }
    r_retention = {
        state: final_ramsey[state]["radius"] / initial["Ramsey"][state]["radius"]
        for state in STATES
    }
    median_k = float(np.median(list(k_retention.values())))
    median_r = float(np.median(list(r_retention.values())))
    singular_errors = []
    hidden_errors = []
    crossings: dict[str, list[float]] = {"Ramsey": [], "Hahn": []}
    alignment_ok = True
    for condition in ("Ramsey", "Hahn"):
        for state in STATES:
            rows = recomputed[condition][state]
            for row in rows:
                model = np.sort([row["k"], row["radius"], row["radius"]])[::-1]
                singular_errors.append(
                    float(np.mean(np.abs(model - [row["s1"], row["s2"], row["s3"]])))
                )
                hidden_errors.append(row["hidden_quadrature_abs_error"])
            radius_index = first_index(rows, "radius", lambda value: value < 0.50)
            axis_index = next(
                (i for i, row in enumerate(rows) if row["strong_axes"] == 1), None
            )
            alignment_ok &= (
                radius_index is not None
                and axis_index is not None
                and abs(radius_index - axis_index) <= 1
            )
            if radius_index is not None:
                crossings[condition].append(rows[radius_index]["wait_us"])
    delay = geometric_mean(crossings["Hahn"]) / geometric_mean(crossings["Ramsey"])
    family_margins = [
        initial[condition][state]["radius"] - initial[condition][state]["alt_radius"]
        for condition in ("Ramsey", "Hahn")
        for state in STATES
    ]
    gate_truths = {
        "D1": len(saved_by_key) == 88 and maximum_saved_difference <= 1e-12,
        "D2": all(value >= 0.90 for value in core_medians.values()),
        "D3": all(
            initial[condition][state]["k"] >= 0.80
            and initial[condition][state]["radius"] >= 0.80
            and initial[condition][state]["te_observed"] >= 1.60
            for condition in ("Ramsey", "Hahn")
            for state in STATES
        ),
        "D4": all(value >= 0.75 for value in k_retention.values()),
        "D5": all(value <= 0.20 for value in r_retention.values()),
        "D6": median_k - median_r >= 0.60,
        "D7": float(np.median(singular_errors)) <= 0.08,
        "D8": alignment_ok,
        "D9": len(crossings["Ramsey"]) == len(crossings["Hahn"]) == 4 and delay >= 4,
        "D10": all(value >= 0.60 for value in family_margins),
        "D11": float(np.median(hidden_errors)) <= 0.08,
    }
    saved_results = json.loads(RESULTS.read_text(encoding="utf-8"))
    saved_gate_truths = {
        gate["gate_id"]: bool(gate["passed"]) for gate in saved_results["gates"]
    }
    validation = {
        "test_id": "Q8-BELL-RELATION-PLANE-v1-independent-validation",
        "protocol_sha256": observed_hash,
        "source_rows_reconstructed": len(saved_by_key),
        "maximum_saved_field_abs_difference": maximum_saved_difference,
        "independent_gate_truths": gate_truths,
        "saved_gate_truths": saved_gate_truths,
        "gate_truths_match": gate_truths == saved_gate_truths,
        "checks": {
            "all_source_records_reproduced": maximum_saved_difference <= 1e-12,
            "all_11_gates_pass": all(gate_truths.values()),
            "saved_and_independent_gate_outcomes_match": gate_truths == saved_gate_truths,
        },
        "summary": {
            "core_share_medians": core_medians,
            "median_final_ramsey_k_retention": median_k,
            "median_final_ramsey_r_retention": median_r,
            "median_singular_model_mae": float(np.median(singular_errors)),
            "median_hidden_quadrature_abs_error": float(np.median(hidden_errors)),
            "hahn_to_ramsey_radius_crossing_ratio": delay,
        },
        "validated": (
            maximum_saved_difference <= 1e-12
            and all(gate_truths.values())
            and gate_truths == saved_gate_truths
        ),
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
