#!/usr/bin/env python3
"""Independent validation of Q11 without importing its implementation."""

from __future__ import annotations

import csv
import json
import math
from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "Q9_INFORMATION3_BELL_ALLOCATIONS.csv"
RECORDED_ROWS = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
RECORDED_RESULT = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RESULTS.json"
OUTPUT = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_VALIDATION.json"
CONDITIONS = ("Ramsey", "Hahn")
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")


def make_coordinates(z: np.ndarray, t: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = 2.0 * (z - np.min(z)) / np.ptp(z)
    dz = np.gradient(z, t, edge_order=2)
    y = 1.0 - np.clip(dz / np.max(np.abs(dz)), -1.0, 1.0)
    return x, y


def scope_metrics(rows: list[dict[str, float]]) -> dict[str, float]:
    xa = np.array([row["target_x"] for row in rows])
    ya = np.array([row["target_y"] for row in rows])
    xp = np.array([row["predicted_x"] for row in rows])
    yp = np.array([row["predicted_y"] for row in rows])
    anti = np.hypot(xa - xp, ya - yp)
    ridge = np.hypot(xa - 1.0, ya - 1.0)
    same = np.hypot(
        xa - np.array([row["visible_x"] for row in rows]),
        ya - np.array([row["visible_y"] for row in rows]),
    )
    branch_match = [
        (1 if ya_i < 1 else -1) == (1 if yp_i < 1 else -1)
        for ya_i, yp_i in zip(ya, yp)
        if abs(ya_i - 1) > 1e-12 and abs(yp_i - 1) > 1e-12
    ]
    angle_scores = [
        row["opposition_score"]
        for row in rows
        if row["visible_radius"] >= 0.10 and row["target_radius"] >= 0.10
    ]
    anti_mean = float(np.mean(anti))
    ridge_mean = float(np.mean(ridge))
    same_mean = float(np.mean(same))
    return {
        "amplitude_correlation": float(np.corrcoef(xp, xa)[0, 1]),
        "direction_correlation": float(np.corrcoef(yp, ya)[0, 1]),
        "anti_phase_mean_2d_error": anti_mean,
        "anti_phase_median_2d_error": float(np.median(anti)),
        "improvement_vs_ridge_pct": 100.0 * (ridge_mean - anti_mean) / ridge_mean,
        "improvement_vs_same_phase_pct": 100.0 * (same_mean - anti_mean) / same_mean,
        "branch_accuracy": float(np.mean(branch_match)),
        "median_opposition_score": float(np.median(angle_scores)),
    }


def run() -> dict[str, object]:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    with RECORDED_ROWS.open(newline="", encoding="utf-8") as handle:
        saved_rows = list(csv.DictReader(handle))
    recorded = json.loads(RECORDED_RESULT.read_text(encoding="utf-8"))
    saved_by = {
        (row["condition"], row["state"], int(row["wait_index"])): row
        for row in saved_rows
    }

    recomputed: list[dict[str, float | str | int]] = []
    data_ok = len(source) == 88 and len(saved_by) == 88
    bounds_ok = True
    max_field_difference = 0.0
    max_reconstruction_error = 0.0

    for condition in CONDITIONS:
        for state in STATES:
            subset = sorted(
                (
                    row
                    for row in source
                    if row["condition"] == condition and row["state"] == state
                ),
                key=lambda row: int(row["wait_index"]),
            )
            t = np.array([float(row["wait_us"]) for row in subset])
            visible = np.array([float(row["k"]) + float(row["radius"]) for row in subset])
            target = np.array([float(row["i_unresolved_half_scale"]) for row in subset])
            data_ok = bool(
                data_ok
                and len(subset) == 11
                and len(np.unique(t)) == 11
                and np.all(np.diff(t) > 0)
                and np.ptp(visible) > 0
                and np.ptp(target) > 0
            )
            xv, yv = make_coordinates(visible, t)
            xp, yp = make_coordinates(target, t)
            for index, row in enumerate(subset):
                cv = complex(xv[index] - 1.0, yv[index] - 1.0)
                cp = complex(xp[index] - 1.0, yp[index] - 1.0)
                residual = cp + cv
                prediction_x = 2.0 - xv[index]
                prediction_y = 2.0 - yv[index]
                radius_v, radius_p = abs(cv), abs(cp)
                score = (
                    -math.cos(math.atan2(cp.imag, cp.real) - math.atan2(cv.imag, cv.real))
                    if radius_v >= 0.10 and radius_p >= 0.10
                    else float("nan")
                )
                item = {
                    "condition": condition,
                    "state": state,
                    "wait_index": int(row["wait_index"]),
                    "visible_x": float(xv[index]),
                    "visible_y": float(yv[index]),
                    "target_x": float(xp[index]),
                    "target_y": float(yp[index]),
                    "predicted_x": float(prediction_x),
                    "predicted_y": float(prediction_y),
                    "visible_radius": float(radius_v),
                    "target_radius": float(radius_p),
                    "opposition_score": float(score),
                    "residual_real": float(residual.real),
                    "residual_imag": float(residual.imag),
                    "residual_radius": float(abs(residual)),
                }
                recomputed.append(item)
                bounds_ok = bool(
                    bounds_ok
                    and all(
                        math.isfinite(value) and -1e-12 <= value <= 2 + 1e-12
                        for value in (xv[index], yv[index], xp[index], yp[index])
                    )
                )
                rebuilt = -cv + residual
                max_reconstruction_error = max(
                    max_reconstruction_error,
                    abs(rebuilt.real - cp.real),
                    abs(rebuilt.imag - cp.imag),
                )
                saved = saved_by[(condition, state, int(row["wait_index"]))]
                for field in (
                    "visible_x",
                    "visible_y",
                    "target_x",
                    "target_y",
                    "predicted_x",
                    "predicted_y",
                    "visible_radius",
                    "target_radius",
                    "residual_real",
                    "residual_imag",
                    "residual_radius",
                ):
                    max_field_difference = max(
                        max_field_difference,
                        abs(float(item[field]) - float(saved[field])),
                    )
                if math.isfinite(score):
                    max_field_difference = max(
                        max_field_difference,
                        abs(score - float(saved["opposition_score"])),
                    )

    metrics = {
        condition: scope_metrics(
            [row for row in recomputed if row["condition"] == condition]
        )
        for condition in CONDITIONS
    }
    overall = scope_metrics(recomputed)
    residual_exploratory = {}
    for condition in CONDITIONS:
        state_series = {}
        for state in STATES:
            subset = sorted(
                [
                    row
                    for row in recomputed
                    if row["condition"] == condition and row["state"] == state
                ],
                key=lambda row: int(row["wait_index"]),
            )
            state_series[state] = {
                "real": np.array([float(row["residual_real"]) for row in subset]),
                "imag": np.array([float(row["residual_imag"]) for row in subset]),
                "radius": np.array([float(row["residual_radius"]) for row in subset]),
            }
        residual_exploratory[condition] = {
            component: float(
                np.median(
                    [
                        np.corrcoef(
                            state_series[left][component],
                            state_series[right][component],
                        )[0, 1]
                        for left, right in combinations(STATES, 2)
                    ]
                )
            )
            for component in ("real", "imag", "radius")
        }
    recomputed_pass = {
        "R1": data_ok,
        "R2": bounds_ok,
        "R3": all(metrics[c]["amplitude_correlation"] >= 0.95 for c in CONDITIONS),
        "R4": all(metrics[c]["direction_correlation"] >= 0.40 for c in CONDITIONS),
        "R5": overall["anti_phase_median_2d_error"] <= 0.25,
        "R6": all(metrics[c]["improvement_vs_ridge_pct"] >= 25.0 for c in CONDITIONS),
        "R7": all(
            metrics[c]["improvement_vs_same_phase_pct"] >= 50.0 for c in CONDITIONS
        ),
        "R8": all(metrics[c]["branch_accuracy"] >= 0.75 for c in CONDITIONS),
        "R9": all(metrics[c]["median_opposition_score"] >= 0.75 for c in CONDITIONS),
        "R10": max_reconstruction_error <= 1e-12,
    }
    recorded_pass = {
        gate["gate_id"]: bool(gate["passed"]) for gate in recorded["gates"]
    }

    summary = recorded["summary"]
    headline_differences = {
        "amplitude_Ramsey": abs(
            metrics["Ramsey"]["amplitude_correlation"]
            - summary["amplitude_correlations"]["Ramsey"]
        ),
        "amplitude_Hahn": abs(
            metrics["Hahn"]["amplitude_correlation"]
            - summary["amplitude_correlations"]["Hahn"]
        ),
        "direction_Ramsey": abs(
            metrics["Ramsey"]["direction_correlation"]
            - summary["direction_correlations"]["Ramsey"]
        ),
        "direction_Hahn": abs(
            metrics["Hahn"]["direction_correlation"]
            - summary["direction_correlations"]["Hahn"]
        ),
        "median_error": abs(
            overall["anti_phase_median_2d_error"]
            - summary["overall_median_2d_error"]
        ),
    }
    recorded_exploratory = recorded["post_outcome_exploratory_residual_structure"]
    exploratory_differences = {
        f"{condition}_{component}": abs(
            residual_exploratory[condition][component]
            - recorded_exploratory[condition]["median_pairwise_correlations"][
                component
            ]
        )
        for condition in CONDITIONS
        for component in ("real", "imag", "radius")
    }
    valid = bool(
        recomputed_pass == recorded_pass
        and all(recomputed_pass.values())
        and max_field_difference <= 1e-12
        and max(headline_differences.values()) <= 1e-12
        and max(exploratory_differences.values()) <= 1e-12
    )
    result = {
        "validation_id": "Q11-VISIBLE-UNRESOLVED-INFORMATION3-independent-v1",
        "valid": valid,
        "recomputed_condition_metrics": metrics,
        "recomputed_overall_metrics": overall,
        "recomputed_gate_pass": recomputed_pass,
        "recorded_gate_pass": recorded_pass,
        "maximum_record_field_difference": max_field_difference,
        "headline_differences": headline_differences,
        "maximum_headline_difference": max(headline_differences.values()),
        "recomputed_exploratory_residual_medians": residual_exploratory,
        "exploratory_differences": exploratory_differences,
        "maximum_exploratory_difference": max(exploratory_differences.values()),
        "note": (
            "Independent source-to-result recomputation; the validator does not import "
            "the Q11 test implementation."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
