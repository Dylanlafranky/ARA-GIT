#!/usr/bin/env python3
"""Independent source-to-result validation for Q12."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
RECORDED = HERE / "Q12_RESIDUAL_CHILDREN_RESULTS.json"
OUTPUT = HERE / "Q12_RESIDUAL_CHILDREN_VALIDATION.json"
CONDITIONS = ("Ramsey", "Hahn")
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
LABELS = {
    "Phi-plus": (1, 1),
    "Phi-minus": (1, -1),
    "Psi-plus": (-1, 1),
    "Psi-minus": (-1, -1),
}
REVERSE = {value: key for key, value in LABELS.items()}
MODES = ("common", "family", "sign", "interaction")


def child_modes(e: dict[str, complex]) -> dict[str, complex]:
    a, b, c, d = (e[state] for state in STATES)
    return {
        "common": (a + b + c + d) / 2,
        "family": (a + b - c - d) / 2,
        "sign": (a - b + c - d) / 2,
        "interaction": (a - b - c + d) / 2,
    }


def rebuild(m: dict[str, complex], family: int, sign: int) -> complex:
    return (
        m["common"]
        + family * m["family"]
        + sign * m["sign"]
        + family * sign * m["interaction"]
    ) / 2


def metrics(rows: list[dict[str, object]]) -> dict[str, float]:
    actual = np.array([row["actual"] for row in rows], dtype=complex)
    predicted = np.array([row["predicted"] for row in rows], dtype=complex)
    child_error = np.abs(actual - predicted)
    zero_error = np.abs(actual)
    loo_error = np.array([float(row["loo_error"]) for row in rows])
    mask_r = (np.abs(actual.real) > 1e-12) & (np.abs(predicted.real) > 1e-12)
    mask_i = (np.abs(actual.imag) > 1e-12) & (np.abs(predicted.imag) > 1e-12)
    return {
        "complex_mean_error": float(np.mean(child_error)),
        "zero_mean_error": float(np.mean(zero_error)),
        "loo_mean_error": float(np.mean(loo_error)),
        "improvement_vs_zero_pct": float(
            100 * (np.mean(zero_error) - np.mean(child_error)) / np.mean(zero_error)
        ),
        "improvement_vs_loo_mean_pct": float(
            100 * (np.mean(loo_error) - np.mean(child_error)) / np.mean(loo_error)
        ),
        "real_sign_accuracy": float(
            np.mean(np.sign(actual.real[mask_r]) == np.sign(predicted.real[mask_r]))
        ),
        "imag_sign_accuracy": float(
            np.mean(np.sign(actual.imag[mask_i]) == np.sign(predicted.imag[mask_i]))
        ),
    }


def run() -> dict[str, object]:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))
    cells = {}
    data_ok = len(source) == 88
    for condition in CONDITIONS:
        for wait_index in range(11):
            rows = [
                row
                for row in source
                if row["condition"] == condition
                and int(row["wait_index"]) == wait_index
            ]
            values = {
                row["state"]: complex(
                    float(row["residual_real"]), float(row["residual_imag"])
                )
                for row in rows
            }
            data_ok = bool(data_ok and len(rows) == 4 and set(values) == set(STATES))
            cells[(condition, wait_index)] = values

    inverse_error = 0.0
    parseval_error = 0.0
    energy = {
        condition: {
            component: {mode: 0.0 for mode in MODES}
            for component in ("real", "imag", "complex")
        }
        for condition in CONDITIONS
    }
    predictions = []
    for (condition, wait_index), values in cells.items():
        modes = child_modes(values)
        parseval_error = max(
            parseval_error,
            abs(
                sum(abs(value) ** 2 for value in values.values())
                - sum(abs(value) ** 2 for value in modes.values())
            ),
        )
        for state, (family, sign) in LABELS.items():
            inverse_error = max(
                inverse_error, abs(rebuild(modes, family, sign) - values[state])
            )
        for mode, value in modes.items():
            energy[condition]["real"][mode] += value.real**2
            energy[condition]["imag"][mode] += value.imag**2
            energy[condition]["complex"][mode] += abs(value) ** 2

        for target, (family, sign) in LABELS.items():
            sibling = REVERSE[(family, -sign)]
            cross = REVERSE[(-family, sign)]
            diagonal = REVERSE[(-family, -sign)]
            donors = [values[state] for state in STATES if state != target]
            predictions.append(
                {
                    "condition": condition,
                    "actual": values[target],
                    "predicted": values[sibling] + values[cross] - values[diagonal],
                    "loo_error": abs(values[target] - sum(donors) / 3),
                }
            )

    shares = {}
    for condition in CONDITIONS:
        shares[condition] = {}
        for component in ("real", "imag", "complex"):
            total = sum(energy[condition][component].values())
            shares[condition][component] = {
                mode: energy[condition][component][mode] / total for mode in MODES
            }
    condition_metrics = {
        condition: metrics(
            [row for row in predictions if row["condition"] == condition]
        )
        for condition in CONDITIONS
    }
    gate_pass = {
        "C1": data_ok and len(cells) == 22,
        "C2": inverse_error <= 1e-12,
        "C3": parseval_error <= 1e-12,
        "C4": all(shares[c]["real"]["common"] >= 0.50 for c in CONDITIONS),
        "C5": all(1 - shares[c]["imag"]["common"] >= 0.50 for c in CONDITIONS),
        "C6": all(
            condition_metrics[c]["improvement_vs_zero_pct"] >= 10.0
            for c in CONDITIONS
        ),
        "C7": all(
            condition_metrics[c]["improvement_vs_loo_mean_pct"] >= 5.0
            for c in CONDITIONS
        ),
        "C8": all(
            condition_metrics[c]["real_sign_accuracy"] >= 0.75 for c in CONDITIONS
        ),
        "C9": all(
            condition_metrics[c]["imag_sign_accuracy"] >= 0.60 for c in CONDITIONS
        ),
        "C10": all(
            shares[c]["complex"]["interaction"] <= 0.25 for c in CONDITIONS
        ),
    }
    recorded_pass = {
        gate["gate_id"]: bool(gate["passed"]) for gate in recorded["gates"]
    }
    recorded_shares = recorded["summary"]["energy_shares"]
    share_differences = {
        f"{condition}_{component}_{mode}": abs(
            shares[condition][component][mode]
            - recorded_shares[condition][component][mode]
        )
        for condition in CONDITIONS
        for component in ("real", "imag", "complex")
        for mode in MODES
    }
    recorded_metrics = recorded["summary"]["heldout_metrics"]
    metric_fields = (
        "complex_mean_error",
        "improvement_vs_zero_pct",
        "improvement_vs_loo_mean_pct",
        "real_sign_accuracy",
        "imag_sign_accuracy",
    )
    metric_differences = {
        f"{condition}_{field}": abs(
            condition_metrics[condition][field]
            - float(recorded_metrics[condition][field])
        )
        for condition in CONDITIONS
        for field in metric_fields
    }
    valid = bool(
        gate_pass == recorded_pass
        and max(share_differences.values()) <= 1e-12
        and max(metric_differences.values()) <= 1e-12
    )
    result = {
        "validation_id": "Q12-RESIDUAL-CHILDREN-independent-v1",
        "valid": valid,
        "recomputed_gate_pass": gate_pass,
        "recorded_gate_pass": recorded_pass,
        "recomputed_energy_shares": shares,
        "recomputed_condition_metrics": condition_metrics,
        "maximum_share_difference": max(share_differences.values()),
        "maximum_metric_difference": max(metric_differences.values()),
        "inverse_error": inverse_error,
        "parseval_error": parseval_error,
        "note": "Independent source-to-result recomputation without importing Q12.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
