#!/usr/bin/env python3
"""Run the frozen Q14 crossed-child correspondence test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
INPUT = HERE / "Q13_RAMSEY_HAHN_FOUR_CHILDREN.csv"
PROTOCOL = HERE / "Q14_CHILD_PHASE_SWAP_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q14_CHILD_PHASE_SWAP_PROTOCOL_v1_FROZEN.sha256"
METRICS_CSV = HERE / "Q14_CHILD_PHASE_SWAP_METRICS.csv"
FOLDS_CSV = HERE / "Q14_CHILD_PHASE_SWAP_FOLDS.csv"
GATES_CSV = HERE / "Q14_CHILD_PHASE_SWAP_GATES.csv"
NULL_JSON = HERE / "Q14_CHILD_PHASE_SWAP_NULL.json"
RESULTS_JSON = HERE / "Q14_CHILD_PHASE_SWAP_RESULTS.json"
FIGURE_SVG = HERE / "Q14_CHILD_PHASE_SWAP_GEOMETRY.svg"

STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
AXES = ("amplitude", "direction")
PERMUTATIONS = 9999
SEED = 27014
EPSILON = 1e-15


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed = sha256(PROTOCOL)
    if expected != observed:
        raise RuntimeError(f"Q14 protocol mismatch: {observed} != {expected}")
    return observed


def parameter_free_metrics(
    ramsey: np.ndarray, hahn: np.ndarray
) -> dict[str, float | int]:
    identity_error = float(np.sum((hahn - ramsey) ** 2))
    swapped_ramsey = ramsey[:, ::-1]
    swap_error = float(np.sum((hahn - swapped_ramsey) ** 2))
    swap_gain = (
        1.0 - swap_error / identity_error
        if identity_error > EPSILON
        else float("nan")
    )
    ramsey_difference = ramsey[:, 0] - ramsey[:, 1]
    hahn_difference = hahn[:, 0] - hahn[:, 1]
    parity_product = ramsey_difference * hahn_difference
    evaluable = np.abs(parity_product) > EPSILON
    flipped_fraction = (
        float(np.mean(parity_product[evaluable] < 0))
        if np.any(evaluable)
        else float("nan")
    )
    denominator = math.sqrt(
        float(np.sum(ramsey_difference**2))
        * float(np.sum(hahn_difference**2))
    )
    flipped_cosine = (
        -float(np.sum(ramsey_difference * hahn_difference)) / denominator
        if denominator > EPSILON
        else float("nan")
    )
    sum_error = float(
        np.max(
            np.abs(
                np.sum(swapped_ramsey, axis=1) - np.sum(ramsey, axis=1)
            )
        )
    )
    return {
        "identity_sse": identity_error,
        "swap_sse": swap_error,
        "swap_gain": swap_gain,
        "flipped_fraction": flipped_fraction,
        "flipped_cosine": flipped_cosine,
        "evaluable_cells": int(np.sum(evaluable)),
        "sum_invariance_max_error": sum_error,
    }


def fit_common_nonnegative_scale(
    source: np.ndarray, target: np.ndarray
) -> dict[str, np.ndarray | float]:
    source_mean = np.mean(source, axis=0)
    target_mean = np.mean(target, axis=0)
    source_centered = source - source_mean
    target_centered = target - target_mean
    denominator = float(np.sum(source_centered**2))
    raw_scale = (
        float(np.sum(source_centered * target_centered)) / denominator
        if denominator > EPSILON
        else 0.0
    )
    scale = max(0.0, raw_scale)
    offset = target_mean - scale * source_mean
    return {"scale": scale, "raw_scale": raw_scale, "offset": offset}


def predict(
    source: np.ndarray, model: dict[str, np.ndarray | float]
) -> np.ndarray:
    return (
        np.asarray(model["offset"], dtype=float)
        + float(model["scale"]) * source
    )


def heldout_folds(
    ramsey: np.ndarray, hahn: np.ndarray, state_labels: np.ndarray
) -> list[dict[str, float | int | str]]:
    folds = []
    for state in STATES:
        train = state_labels != state
        test = state_labels == state
        identity_train = ramsey[train]
        swap_train = ramsey[train][:, ::-1]
        identity_model = fit_common_nonnegative_scale(
            identity_train, hahn[train]
        )
        swap_model = fit_common_nonnegative_scale(swap_train, hahn[train])
        identity_prediction = predict(ramsey[test], identity_model)
        swap_prediction = predict(ramsey[test][:, ::-1], swap_model)
        identity_sse = float(
            np.sum((hahn[test] - identity_prediction) ** 2)
        )
        swap_sse = float(np.sum((hahn[test] - swap_prediction) ** 2))
        gain = (
            1.0 - swap_sse / identity_sse
            if identity_sse > EPSILON
            else float("nan")
        )
        folds.append(
            {
                "heldout_state": state,
                "train_cells": int(np.sum(train)),
                "test_cells": int(np.sum(test)),
                "identity_scale": float(identity_model["scale"]),
                "identity_raw_scale": float(identity_model["raw_scale"]),
                "swap_scale": float(swap_model["scale"]),
                "swap_raw_scale": float(swap_model["raw_scale"]),
                "identity_sse": identity_sse,
                "swap_sse": swap_sse,
                "swap_gain": gain,
                "swap_wins": swap_sse < identity_sse,
            }
        )
    return folds


def add_gate(
    gates: list[dict[str, object]],
    gate_id: str,
    description: str,
    passed: bool,
    value: object,
) -> None:
    if isinstance(value, np.generic):
        value = value.item()
    gates.append(
        {
            "gate_id": gate_id,
            "description": description,
            "passed": bool(passed),
            "value": value,
        }
    )


def svg_text(
    parts: list[str], x: float, y: float, value: str, css: str = "label"
) -> None:
    parts.append(
        f'<text x="{x:.1f}" y="{y:.1f}" class="{css}">{value}</text>'
    )


def build_svg(
    metrics: dict[str, dict[str, float | int]],
    folds: dict[str, list[dict[str, float | int | str]]],
    nulls: dict[str, object],
) -> None:
    width, height = 1500, 1030
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,sans-serif;fill:#17212B}.title{font-size:27px;font-weight:700}.subtitle{font-size:13px;fill:#405164}.paneltitle{font-size:19px;font-weight:700}.axis{font-size:12px;fill:#405164}.label{font-size:12px}.small{font-size:10px;fill:#566573}.value{font-size:15px;font-weight:700}",
        "</style>",
        '<rect width="1500" height="1030" fill="#FFFFFF"/>',
    ]
    svg_text(parts, 52, 44, "Same-child versus crossed-child correspondence", "title")
    svg_text(
        parts,
        52,
        69,
        "Q14: parameter-free A/B swap, paired within-state null, and leave-one-Bell-identity-out transform",
        "subtitle",
    )

    panel_y, panel_h = 96, 370
    for panel_index, axis in enumerate(AXES):
        x = 50 + panel_index * 720
        parts.append(
            f'<rect x="{x}" y="{panel_y}" width="680" height="{panel_h}" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
        )
        svg_text(parts, x + 22, panel_y + 34, axis.capitalize(), "paneltitle")
        m = metrics[axis]
        rows = [
            ("parameter-free swap gain", float(m["swap_gain"])),
            ("flipped-parity fraction", float(m["flipped_fraction"])),
            ("flipped cosine", float(m["flipped_cosine"])),
            (
                "median held-out swap gain",
                float(np.median([float(row["swap_gain"]) for row in folds[axis]])),
            ),
        ]
        for row_index, (label, value) in enumerate(rows):
            yy = panel_y + 88 + row_index * 58
            svg_text(parts, x + 28, yy, label, "label")
            svg_text(parts, x + 360, yy, f"{value:+.4f}", "value")
        svg_text(
            parts,
            x + 28,
            panel_y + 326,
            f"matched-stage p = {float(nulls[axis]['p_value']):.4f}",
            "label",
        )
        wins = sum(bool(row["swap_wins"]) for row in folds[axis])
        svg_text(
            parts,
            x + 360,
            panel_y + 326,
            f"held-out wins = {wins}/4",
            "label",
        )

    table_y = 500
    parts.append(
        f'<rect x="50" y="{table_y}" width="1400" height="455" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
    )
    svg_text(parts, 72, table_y + 35, "Held-out Bell-identity results", "paneltitle")
    headings = (
        "axis",
        "held out",
        "same SSE",
        "swap SSE",
        "gain",
        "same scale",
        "swap scale",
        "winner",
    )
    xs = (75, 185, 355, 530, 705, 850, 1015, 1190)
    for xx, heading in zip(xs, headings):
        svg_text(parts, xx, table_y + 72, heading, "axis")
    row_number = 0
    for axis in AXES:
        for row in folds[axis]:
            yy = table_y + 107 + row_number * 36
            if row_number % 2 == 0:
                parts.append(
                    f'<rect x="68" y="{yy-21}" width="1360" height="29" fill="#F0F4F7"/>'
                )
            values = (
                axis,
                str(row["heldout_state"]),
                f"{float(row['identity_sse']):.4f}",
                f"{float(row['swap_sse']):.4f}",
                f"{float(row['swap_gain']):+.4f}",
                f"{float(row['identity_scale']):.4f}",
                f"{float(row['swap_scale']):.4f}",
                "swap" if bool(row["swap_wins"]) else "same",
            )
            for xx, value in zip(xs, values):
                svg_text(parts, xx, yy, value, "label")
            row_number += 1
    svg_text(
        parts,
        75,
        table_y + 425,
        "Crossed correspondence is structural only: Ramsey and Hahn are separate protocols matched by ordinal stage.",
        "subtitle",
    )
    parts.append("</svg>")
    FIGURE_SVG.write_text("\n".join(parts), encoding="utf-8")


def run() -> dict[str, object]:
    protocol_hash = verify_protocol()
    with INPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    labels = np.asarray([row["state"] for row in rows])
    complete = (
        len(rows) == 44
        and set(labels) == set(STATES)
        and all(int(np.sum(labels == state)) == 11 for state in STATES)
    )
    arrays = {}
    for axis in AXES:
        ramsey = np.asarray(
            [
                [
                    float(row[f"R_A_{axis}"]),
                    float(row[f"R_B_{axis}"]),
                ]
                for row in rows
            ]
        )
        hahn = np.asarray(
            [
                [
                    float(row[f"H_A_{axis}"]),
                    float(row[f"H_B_{axis}"]),
                ]
                for row in rows
            ]
        )
        arrays[axis] = {"R": ramsey, "H": hahn}
        complete = bool(
            complete and np.isfinite(ramsey).all() and np.isfinite(hahn).all()
        )

    metrics = {
        axis: parameter_free_metrics(
            arrays[axis]["R"], arrays[axis]["H"]
        )
        for axis in AXES
    }
    folds = {
        axis: heldout_folds(
            arrays[axis]["R"], arrays[axis]["H"], labels
        )
        for axis in AXES
    }

    rng = np.random.default_rng(SEED)
    state_indices = {
        state: np.flatnonzero(labels == state) for state in STATES
    }
    null_gains = {axis: [] for axis in AXES}
    for _ in range(PERMUTATIONS):
        permutations = {
            state: rng.permutation(indices)
            for state, indices in state_indices.items()
        }
        for axis in AXES:
            permuted_hahn = arrays[axis]["H"].copy()
            for state, indices in state_indices.items():
                permuted_hahn[indices] = arrays[axis]["H"][
                    permutations[state]
                ]
            null_gains[axis].append(
                float(
                    parameter_free_metrics(
                        arrays[axis]["R"], permuted_hahn
                    )["swap_gain"]
                )
            )

    nulls = {}
    for axis in AXES:
        observed = float(metrics[axis]["swap_gain"])
        values = null_gains[axis]
        p_value = (1 + sum(value >= observed for value in values)) / (
            len(values) + 1
        )
        nulls[axis] = {
            "permutations": PERMUTATIONS,
            "seed": SEED,
            "observed_swap_gain": observed,
            "p_value": p_value,
            "null_q95": float(np.quantile(values, 0.95)),
            "null_q99": float(np.quantile(values, 0.99)),
            "null_mean": float(np.mean(values)),
        }
    NULL_JSON.write_text(json.dumps(nulls, indent=2), encoding="utf-8")

    cv_medians = {
        axis: float(
            np.median([float(row["swap_gain"]) for row in folds[axis]])
        )
        for axis in AXES
    }
    cv_wins = {
        axis: sum(bool(row["swap_wins"]) for row in folds[axis])
        for axis in AXES
    }
    max_sum_error = max(
        float(metrics[axis]["sum_invariance_max_error"]) for axis in AXES
    )

    gates: list[dict[str, object]] = []
    add_gate(
        gates,
        "F1",
        "44 finite cells and four expected Bell identities",
        complete,
        {"cells": len(rows), "complete": complete},
    )
    add_gate(
        gates,
        "F2",
        "swap preserves the two-component sum within 1e-12",
        max_sum_error <= 1e-12,
        max_sum_error,
    )
    add_gate(
        gates,
        "F3",
        "parameter-free direction swap gain > 0",
        float(metrics["direction"]["swap_gain"]) > 0,
        metrics["direction"]["swap_gain"],
    )
    add_gate(
        gates,
        "F4",
        "direction matched-stage permutation p <= 0.05",
        float(nulls["direction"]["p_value"]) <= 0.05,
        nulls["direction"]["p_value"],
    )
    add_gate(
        gates,
        "F5",
        "direction flipped-parity fraction >= 0.75",
        float(metrics["direction"]["flipped_fraction"]) >= 0.75,
        metrics["direction"]["flipped_fraction"],
    )
    add_gate(
        gates,
        "F6",
        "direction flipped cosine >= 0.50",
        float(metrics["direction"]["flipped_cosine"]) >= 0.50,
        metrics["direction"]["flipped_cosine"],
    )
    add_gate(
        gates,
        "F7",
        "median held-out direction swap gain > 0",
        cv_medians["direction"] > 0,
        cv_medians["direction"],
    )
    add_gate(
        gates,
        "F8",
        "swap wins direction in at least 3/4 held-out states",
        cv_wins["direction"] >= 3,
        cv_wins["direction"],
    )
    add_gate(
        gates,
        "F9",
        "parameter-free amplitude swap gain > 0",
        float(metrics["amplitude"]["swap_gain"]) > 0,
        metrics["amplitude"]["swap_gain"],
    )
    add_gate(
        gates,
        "F10",
        "amplitude matched-stage permutation p <= 0.05",
        float(nulls["amplitude"]["p_value"]) <= 0.05,
        nulls["amplitude"]["p_value"],
    )
    add_gate(
        gates,
        "F11",
        "amplitude flipped-parity fraction >= 0.75",
        float(metrics["amplitude"]["flipped_fraction"]) >= 0.75,
        metrics["amplitude"]["flipped_fraction"],
    )
    add_gate(
        gates,
        "F12",
        "median held-out amplitude swap gain > 0",
        cv_medians["amplitude"] > 0,
        cv_medians["amplitude"],
    )

    metric_rows = []
    for axis in AXES:
        metric_rows.append(
            {
                "axis": axis,
                **metrics[axis],
                "permutation_p": nulls[axis]["p_value"],
                "null_q95": nulls[axis]["null_q95"],
                "cv_median_swap_gain": cv_medians[axis],
                "cv_swap_wins": cv_wins[axis],
            }
        )
    fold_rows = [
        {"axis": axis, **row}
        for axis in AXES
        for row in folds[axis]
    ]

    result = {
        "test_id": "Q14-CHILD-PHASE-SWAP-v1",
        "ledger_id": "T273",
        "test_class": "post-outcome parameter-free correspondence and held-out transform test",
        "protocol_sha256": protocol_hash,
        "verdict": (
            "CALIBRATED"
            if all(bool(gate["passed"]) for gate in gates)
            else "PARTIAL / NOT CALIBRATED"
        ),
        "summary": {
            "metrics": metrics,
            "nulls": nulls,
            "cv_median_swap_gain": cv_medians,
            "cv_swap_wins": cv_wins,
            "gates_passed": sum(bool(gate["passed"]) for gate in gates),
            "gates_total": len(gates),
        },
        "gates": gates,
        "boundary": (
            "Q14 tests crossed correspondence between two locally normalized child sets. "
            "Ramsey and Hahn are separate protocols matched by ordinal stage, so the result "
            "does not establish causal or literal energy transfer between them."
        ),
    }

    with METRICS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metric_rows[0]))
        writer.writeheader()
        writer.writerows(metric_rows)
    with FOLDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fold_rows[0]))
        writer.writeheader()
        writer.writerows(fold_rows)
    with GATES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("gate_id", "description", "passed", "value"),
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
    build_svg(metrics, folds, nulls)
    print(json.dumps(result["summary"], indent=2))
    print(f"Verdict: {result['verdict']}")
    return result


if __name__ == "__main__":
    run()
