#!/usr/bin/env python3
"""Independent recomputation of the frozen Q10 two-axis unresolved-wave test."""

from __future__ import annotations

import csv
import json
import math
from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Q9_INFORMATION3_BELL_ALLOCATIONS.csv"
RECORDED = HERE / "Q10_UNRESOLVED_TWO_AXIS_RESULTS.json"
OUTPUT = HERE / "Q10_UNRESOLVED_TWO_AXIS_VALIDATION.json"

CONDITIONS = ("Ramsey", "Hahn")
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")


def coordinates(h: np.ndarray, t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    span = float(np.max(h) - np.min(h))
    x = 2.0 * (h - np.min(h)) / span
    dh = np.gradient(h, t, edge_order=2)
    y = 1.0 - np.clip(dh / np.max(np.abs(dh)), -1.0, 1.0)
    return x, y


def median_pairwise(series: dict[str, np.ndarray]) -> float:
    values = [
        float(np.corrcoef(series[left], series[right])[0, 1])
        for left, right in combinations(STATES, 2)
    ]
    return float(np.median(values))


def run() -> dict[str, object]:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    recorded = json.loads(RECORDED.read_text(encoding="utf-8"))

    primary: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    alternate: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    distances: list[float] = []
    rows_ok = len(rows) == 88
    bounds_ok = True
    inverse_error = 0.0
    relation_error = 0.0
    variance_ok = True
    te_sums: dict[str, float] = {}

    for condition in CONDITIONS:
        for state in STATES:
            subset = sorted(
                (
                    row
                    for row in rows
                    if row["condition"] == condition and row["state"] == state
                ),
                key=lambda row: int(row["wait_index"]),
            )
            t = np.array([float(row["wait_us"]) for row in subset])
            h = np.array([float(row["q8_h_linear"]) for row in subset])
            hp = np.array([float(row["i_unresolved_half_scale"]) for row in subset])
            rows_ok = bool(
                rows_ok
                and len(subset) == 11
                and len(np.unique(t)) == 11
                and np.all(np.diff(t) > 0)
                and np.ptp(h) > 0
                and np.ptp(hp) > 0
            )
            x, y = coordinates(h, t)
            xp, yp = coordinates(hp, t)
            primary[(condition, state)] = (x, y)
            alternate[(condition, state)] = (xp, yp)
            distances.extend(np.hypot(x - xp, y - yp).tolist())
            bounds_ok = bool(
                bounds_ok
                and np.all(np.isfinite(x))
                and np.all(np.isfinite(y))
                and np.min(x) >= -1e-12
                and np.max(x) <= 2 + 1e-12
                and np.min(y) >= -1e-12
                and np.max(y) <= 2 + 1e-12
            )
            reconstructed_h = np.min(h) + x * np.ptp(h) / 2.0
            inverse_error = max(
                inverse_error, float(np.max(np.abs(reconstructed_h - h)))
            )
            z = (x - 1.0) + 1j * (y - 1.0)
            rebuilt = np.abs(z) * np.exp(1j * np.angle(z))
            relation_error = max(
                relation_error,
                float(np.max(np.abs(rebuilt.real - (x - 1.0)))),
                float(np.max(np.abs(rebuilt.imag - (y - 1.0)))),
            )
            variance_ok = bool(
                variance_ok and np.var(x) > 0 and np.var(y) > 0
            )

            weights = np.empty_like(t)
            weights[0] = (t[1] - t[0]) / 2
            weights[-1] = (t[-1] - t[-2]) / 2
            weights[1:-1] = (t[2:] - t[:-2]) / 2
            labels = np.select(
                [
                    (x < 1) & (y < 1),
                    (x >= 1) & (y < 1),
                    (x >= 1) & (y >= 1),
                ],
                ["low_opening", "high_opening", "high_closing"],
                default="low_closing",
            )
            te_sum = sum(
                2.0 * float(np.sum(weights[labels == label])) / float(np.sum(weights))
                for label in (
                    "low_opening",
                    "high_opening",
                    "high_closing",
                    "low_closing",
                )
            )
            te_sums[f"{condition}/{state}"] = te_sum

    amplitude = {
        condition: median_pairwise(
            {state: primary[(condition, state)][0] for state in STATES}
        )
        for condition in CONDITIONS
    }
    rate = {
        condition: median_pairwise(
            {state: primary[(condition, state)][1] for state in STATES}
        )
        for condition in CONDITIONS
    }
    robustness = float(np.median(distances))
    recomputed_gate_values = {
        "U1": rows_ok,
        "U2": bounds_ok,
        "U3": inverse_error,
        "U4": relation_error,
        "U5": te_sums,
        "U6": variance_ok,
        "U7": amplitude,
        "U8": rate,
        "U9": robustness,
    }
    recomputed_gate_pass = {
        "U1": rows_ok,
        "U2": bounds_ok,
        "U3": inverse_error <= 1e-12,
        "U4": relation_error <= 1e-12,
        "U5": all(abs(value - 2.0) <= 1e-12 for value in te_sums.values()),
        "U6": variance_ok,
        "U7": all(value >= 0.80 for value in amplitude.values()),
        "U8": all(value >= 0.40 for value in rate.values()),
        "U9": robustness <= 0.25,
    }
    recorded_pass = {
        gate["gate_id"]: bool(gate["passed"]) for gate in recorded["gates"]
    }

    summary = recorded["summary"]
    numeric_differences = {
        "amplitude_Ramsey": abs(
            amplitude["Ramsey"]
            - summary["amplitude_cross_state_median_correlations"]["Ramsey"]
        ),
        "amplitude_Hahn": abs(
            amplitude["Hahn"]
            - summary["amplitude_cross_state_median_correlations"]["Hahn"]
        ),
        "rate_Ramsey": abs(
            rate["Ramsey"]
            - summary["rate_cross_state_median_correlations"]["Ramsey"]
        ),
        "rate_Hahn": abs(
            rate["Hahn"]
            - summary["rate_cross_state_median_correlations"]["Hahn"]
        ),
        "robustness": abs(
            robustness - summary["median_two_definition_relation_plane_distance"]
        ),
    }
    valid = bool(
        recorded_pass == recomputed_gate_pass
        and all(value <= 1e-12 for value in numeric_differences.values())
        and all(recomputed_gate_pass.values())
    )
    result = {
        "validation_id": "Q10-UNRESOLVED-TWO-AXIS-independent-v1",
        "valid": valid,
        "recomputed_gate_values": recomputed_gate_values,
        "recomputed_gate_pass": recomputed_gate_pass,
        "recorded_gate_pass": recorded_pass,
        "numeric_differences": numeric_differences,
        "maximum_numeric_difference": max(numeric_differences.values()),
        "note": (
            "This script independently reads the Q9 allocation table and recomputes "
            "Q10 coordinates and gates without importing the Q10 test implementation."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
