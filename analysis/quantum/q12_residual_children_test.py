#!/usr/bin/env python3
"""Run the frozen Q12 residual-child decomposition and held-out test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
INPUT = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
PROTOCOL = HERE / "Q12_RESIDUAL_CHILDREN_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q12_RESIDUAL_CHILDREN_PROTOCOL_v1_FROZEN.sha256"
MODES_CSV = HERE / "Q12_RESIDUAL_CHILDREN_MODES.csv"
PREDICTIONS_CSV = HERE / "Q12_RESIDUAL_CHILDREN_PREDICTIONS.csv"
METRICS_CSV = HERE / "Q12_RESIDUAL_CHILDREN_METRICS.csv"
GATES_CSV = HERE / "Q12_RESIDUAL_CHILDREN_GATES.csv"
RESULTS_JSON = HERE / "Q12_RESIDUAL_CHILDREN_RESULTS.json"
FIGURE_SVG = HERE / "Q12_RESIDUAL_CHILDREN_GEOMETRY.svg"

CONDITIONS = ("Ramsey", "Hahn")
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
LABELS = {
    "Phi-plus": (1, 1),
    "Phi-minus": (1, -1),
    "Psi-plus": (-1, 1),
    "Psi-minus": (-1, -1),
}
STATE_FROM_LABEL = {value: key for key, value in LABELS.items()}
MODE_COLORS = {
    "common": "#2F6B9A",
    "family": "#D9B44A",
    "sign": "#D17A22",
    "interaction": "#B05A7A",
}
CONDITION_COLORS = {"Ramsey": "#2F6B9A", "Hahn": "#D17A22"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed = digest(PROTOCOL)
    if expected != observed:
        raise RuntimeError(f"Q12 protocol mismatch: {observed} != {expected}")
    return observed


def transform(values: dict[str, complex]) -> dict[str, complex]:
    pp = values["Phi-plus"]
    pm = values["Phi-minus"]
    qp = values["Psi-plus"]
    qm = values["Psi-minus"]
    return {
        "common": (pp + pm + qp + qm) / 2.0,
        "family": (pp + pm - qp - qm) / 2.0,
        "sign": (pp - pm + qp - qm) / 2.0,
        "interaction": (pp - pm - qp + qm) / 2.0,
    }


def inverse(modes: dict[str, complex], family: int, sign: int) -> complex:
    return 0.5 * (
        modes["common"]
        + family * modes["family"]
        + sign * modes["sign"]
        + family * sign * modes["interaction"]
    )


def signed_accuracy(actual: np.ndarray, predicted: np.ndarray) -> tuple[float, int]:
    mask = (np.abs(actual) > 1e-12) & (np.abs(predicted) > 1e-12)
    if not np.any(mask):
        return float("nan"), 0
    return float(np.mean(np.sign(actual[mask]) == np.sign(predicted[mask]))), int(
        np.sum(mask)
    )


def summarize_predictions(rows: list[dict[str, object]], scope: str) -> dict[str, object]:
    actual = np.array(
        [complex(float(row["actual_real"]), float(row["actual_imag"])) for row in rows]
    )
    predicted = np.array(
        [
            complex(float(row["predicted_real"]), float(row["predicted_imag"]))
            for row in rows
        ]
    )
    zero_error = np.abs(actual)
    predicted_error = np.abs(actual - predicted)
    mean_error = np.array([float(row["loo_mean_error"]) for row in rows])
    sibling_error = np.array([float(row["sibling_error"]) for row in rows])
    zero_mean = float(np.mean(zero_error))
    loo_mean = float(np.mean(mean_error))
    child_mean = float(np.mean(predicted_error))
    real_accuracy, real_n = signed_accuracy(actual.real, predicted.real)
    imag_accuracy, imag_n = signed_accuracy(actual.imag, predicted.imag)
    return {
        "scope": scope,
        "records": len(rows),
        "real_mae": float(np.mean(np.abs(actual.real - predicted.real))),
        "imag_mae": float(np.mean(np.abs(actual.imag - predicted.imag))),
        "complex_mean_error": child_mean,
        "complex_median_error": float(np.median(predicted_error)),
        "zero_mean_error": zero_mean,
        "loo_mean_error": loo_mean,
        "sibling_mean_error": float(np.mean(sibling_error)),
        "improvement_vs_zero_pct": 100.0 * (zero_mean - child_mean) / zero_mean,
        "improvement_vs_loo_mean_pct": 100.0 * (loo_mean - child_mean) / loo_mean,
        "real_sign_accuracy": real_accuracy,
        "real_sign_evaluable": real_n,
        "imag_sign_accuracy": imag_accuracy,
        "imag_sign_evaluable": imag_n,
        "real_correlation": float(np.corrcoef(actual.real, predicted.real)[0, 1]),
        "imag_correlation": float(np.corrcoef(actual.imag, predicted.imag)[0, 1]),
    }


def add_gate(
    gates: list[dict[str, object]],
    gate_id: str,
    description: str,
    passed: bool,
    value: object,
) -> None:
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, dict):
        value = {
            key: item.item() if isinstance(item, np.generic) else item
            for key, item in value.items()
        }
    gates.append(
        {
            "gate_id": gate_id,
            "description": description,
            "passed": bool(passed),
            "value": value,
        }
    )


def txt(parts: list[str], x: float, y: float, text: str, css: str = "label") -> None:
    parts.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{css}">{text}</text>')


def build_svg(
    energy_shares: dict[str, dict[str, dict[str, float]]],
    predictions: list[dict[str, object]],
    metrics: list[dict[str, object]],
) -> None:
    width, height = 1500, 1120
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,sans-serif;fill:#17212B}.title{font-size:27px;font-weight:700}.subtitle{font-size:13px;fill:#405164}.paneltitle{font-size:19px;font-weight:700}.axis{font-size:12px;fill:#405164}.tick{font-size:11px;fill:#566573}.label{font-size:12px}.small{font-size:10px;fill:#566573}",
        "</style>",
        '<rect width="1500" height="1120" fill="#FFFFFF"/>',
    ]
    txt(parts, 52, 44, "Q11 residual decomposed into Bell-label coordinate children", "title")
    txt(
        parts,
        52,
        69,
        "Q12: exact four-mode closure plus held-out fourth-identity prediction",
        "subtitle",
    )

    energy_x, energy_y, energy_w, energy_h = 50, 95, 1400, 355
    parts.append(
        f'<rect x="{energy_x}" y="{energy_y}" width="{energy_w}" height="{energy_h}" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
    )
    txt(parts, energy_x + 22, energy_y + 33, "Residual energy share by coordinate child", "paneltitle")
    txt(
        parts,
        energy_x + 22,
        energy_y + 55,
        "Each row sums to 100%; shares describe the derived residual field, not named physical mechanisms",
        "subtitle",
    )
    legend_x = energy_x + 730
    for index, mode in enumerate(("common", "family", "sign", "interaction")):
        lx = legend_x + index * 155
        parts.append(
            f'<rect x="{lx}" y="{energy_y+24}" width="15" height="15" fill="{MODE_COLORS[mode]}"/>'
        )
        txt(parts, lx + 21, energy_y + 36, mode, "label")
    bar_left, bar_width = energy_x + 260, energy_w - 315
    rows = [
        ("Ramsey", "real"),
        ("Ramsey", "imag"),
        ("Ramsey", "complex"),
        ("Hahn", "real"),
        ("Hahn", "imag"),
        ("Hahn", "complex"),
    ]
    for index, (condition, component) in enumerate(rows):
        yy = energy_y + 88 + index * 41
        txt(parts, energy_x + 24, yy + 16, f"{condition} / {component}", "label")
        cursor = bar_left
        for mode in ("common", "family", "sign", "interaction"):
            share = energy_shares[condition][component][mode]
            segment = bar_width * share
            parts.append(
                f'<rect x="{cursor:.2f}" y="{yy}" width="{segment:.2f}" height="22" fill="{MODE_COLORS[mode]}" stroke="#FFFFFF"/>'
            )
            if segment >= 54:
                text_fill = "#FFFFFF" if mode == "common" else "#17212B"
                parts.append(
                    f'<text x="{cursor + segment / 2 - 16:.1f}" y="{yy + 15:.1f}" class="small" style="fill:{text_fill}">{share*100:.1f}%</text>'
                )
            cursor += segment

    scatter_panels = [
        (50, 480, 680, 420, "Held-out amplitude residual", "actual_real", "predicted_real"),
        (770, 480, 680, 420, "Held-out direction residual", "actual_imag", "predicted_imag"),
    ]
    for px, py, pw, ph, title, actual_field, predicted_field in scatter_panels:
        parts.append(
            f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
        )
        txt(parts, px + 22, py + 33, title, "paneltitle")
        txt(parts, px + 22, py + 55, "Target state omitted; diagonal is exact prediction", "subtitle")
        actual_values = np.array([float(row[actual_field]) for row in predictions])
        predicted_values = np.array([float(row[predicted_field]) for row in predictions])
        limit = max(0.1, float(max(np.max(np.abs(actual_values)), np.max(np.abs(predicted_values)))) * 1.08)
        left, top, cw, ch = px + 76, py + 78, pw - 112, ph - 126
        parts.append(
            f'<rect x="{left}" y="{top}" width="{cw}" height="{ch}" fill="#FFFFFF" stroke="#DCE3E9"/>'
        )
        x0, y0 = left + cw / 2, top + ch / 2
        parts.append(f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{top+ch}" stroke="#AAB4BE"/>')
        parts.append(f'<line x1="{left}" y1="{y0}" x2="{left+cw}" y2="{y0}" stroke="#AAB4BE"/>')
        parts.append(f'<line x1="{left}" y1="{top+ch}" x2="{left+cw}" y2="{top}" stroke="#273746"/>')
        for row in predictions:
            xx = x0 + float(row[predicted_field]) / limit * cw / 2
            yy = y0 - float(row[actual_field]) / limit * ch / 2
            parts.append(
                f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="3.4" fill="{CONDITION_COLORS[str(row["condition"])]}" fill-opacity="0.62" stroke="#FFFFFF" stroke-width="0.5"/>'
            )
        txt(parts, left, top + ch + 21, f"-{limit:.2f}", "tick")
        txt(parts, x0 - 4, top + ch + 21, "0", "tick")
        txt(parts, left + cw - 28, top + ch + 21, f"+{limit:.2f}", "tick")
        txt(parts, left + cw / 2 - 40, top + ch + 41, "predicted", "axis")
        parts.append(
            f'<text x="{left-48}" y="{top+ch/2+25}" class="axis" transform="rotate(-90 {left-48} {top+ch/2+25})">actual</text>'
        )

    metric_by = {str(row["scope"]): row for row in metrics}
    note_y = 930
    parts.append(
        f'<rect x="50" y="{note_y}" width="1400" height="145" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
    )
    txt(parts, 72, note_y + 31, "Held-out no-interaction model versus controls", "paneltitle")
    for index, condition in enumerate(CONDITIONS):
        row = metric_by[condition]
        xx = 85 + index * 680
        txt(parts, xx, note_y + 60, condition, "label")
        txt(
            parts,
            xx,
            note_y + 83,
            f"child error {float(row['complex_mean_error']):.3f} / zero {float(row['zero_mean_error']):.3f} / LOO mean {float(row['loo_mean_error']):.3f}",
            "axis",
        )
        txt(
            parts,
            xx,
            note_y + 106,
            f"real sign {float(row['real_sign_accuracy'])*100:.1f}% / direction sign {float(row['imag_sign_accuracy'])*100:.1f}%",
            "axis",
        )
    parts.append("</svg>")
    FIGURE_SVG.write_text("\n".join(parts), encoding="utf-8")


def run() -> dict[str, object]:
    protocol_hash = verify_protocol()
    with INPUT.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    keys = {
        (row["condition"], int(row["wait_index"]), row["state"]) for row in source
    }
    data_ok = len(source) == 88 and len(keys) == 88
    modes_rows: list[dict[str, object]] = []
    predictions: list[dict[str, object]] = []
    inverse_errors: list[float] = []
    parseval_errors: list[float] = []

    cells: dict[tuple[str, int], dict[str, complex]] = {}
    wait_values: dict[tuple[str, int], float] = {}
    for condition in CONDITIONS:
        for wait_index in range(11):
            subset = [
                row
                for row in source
                if row["condition"] == condition
                and int(row["wait_index"]) == wait_index
            ]
            values = {
                row["state"]: complex(
                    float(row["residual_real"]), float(row["residual_imag"])
                )
                for row in subset
            }
            data_ok = bool(data_ok and set(values) == set(STATES) and len(subset) == 4)
            cells[(condition, wait_index)] = values
            wait_values[(condition, wait_index)] = float(subset[0]["wait_us"])

    energy: dict[str, dict[str, dict[str, float]]] = {
        condition: {
            component: {mode: 0.0 for mode in MODE_COLORS}
            for component in ("real", "imag", "complex")
        }
        for condition in CONDITIONS
    }

    for (condition, wait_index), values in cells.items():
        modes = transform(values)
        source_energy = sum(abs(value) ** 2 for value in values.values())
        mode_energy = sum(abs(value) ** 2 for value in modes.values())
        parseval_errors.append(abs(source_energy - mode_energy))
        for state, (family, sign) in LABELS.items():
            inverse_errors.append(abs(inverse(modes, family, sign) - values[state]))
        for mode, value in modes.items():
            energy[condition]["real"][mode] += value.real**2
            energy[condition]["imag"][mode] += value.imag**2
            energy[condition]["complex"][mode] += abs(value) ** 2
            modes_rows.append(
                {
                    "condition": condition,
                    "wait_index": wait_index,
                    "wait_us": wait_values[(condition, wait_index)],
                    "mode": mode,
                    "real": value.real,
                    "imag": value.imag,
                    "radius": abs(value),
                    "theta_deg": math.degrees(math.atan2(value.imag, value.real)),
                }
            )

        for target, (family, sign) in LABELS.items():
            sibling = STATE_FROM_LABEL[(family, -sign)]
            cross_same_sign = STATE_FROM_LABEL[(-family, sign)]
            diagonal = STATE_FROM_LABEL[(-family, -sign)]
            actual = values[target]
            predicted = values[sibling] + values[cross_same_sign] - values[diagonal]
            donors = [values[state] for state in STATES if state != target]
            loo_mean = sum(donors) / 3.0
            predictions.append(
                {
                    "condition": condition,
                    "wait_index": wait_index,
                    "wait_us": wait_values[(condition, wait_index)],
                    "target_state": target,
                    "family_sibling": sibling,
                    "cross_same_sign": cross_same_sign,
                    "diagonal": diagonal,
                    "actual_real": actual.real,
                    "actual_imag": actual.imag,
                    "predicted_real": predicted.real,
                    "predicted_imag": predicted.imag,
                    "prediction_error": abs(actual - predicted),
                    "zero_error": abs(actual),
                    "loo_mean_real": loo_mean.real,
                    "loo_mean_imag": loo_mean.imag,
                    "loo_mean_error": abs(actual - loo_mean),
                    "sibling_error": abs(actual - values[sibling]),
                }
            )

    energy_shares: dict[str, dict[str, dict[str, float]]] = {}
    for condition in CONDITIONS:
        energy_shares[condition] = {}
        for component in ("real", "imag", "complex"):
            total = sum(energy[condition][component].values())
            energy_shares[condition][component] = {
                mode: value / total for mode, value in energy[condition][component].items()
            }

    metrics = [
        summarize_predictions(
            [row for row in predictions if row["condition"] == condition],
            condition,
        )
        for condition in CONDITIONS
    ]
    metrics.append(summarize_predictions(predictions, "Overall"))
    metric_by = {str(row["scope"]): row for row in metrics}

    gates: list[dict[str, object]] = []
    add_gate(gates, "C1", "88 records form 22 complete four-state cells", data_ok and len(cells) == 22, {"records": len(source), "cells": len(cells)})
    max_inverse = max(inverse_errors)
    add_gate(gates, "C2", "Hadamard inverse maximum error <= 1e-12", max_inverse <= 1e-12, max_inverse)
    max_parseval = max(parseval_errors)
    add_gate(gates, "C3", "Parseval maximum error <= 1e-12", max_parseval <= 1e-12, max_parseval)
    common_real = {
        condition: energy_shares[condition]["real"]["common"]
        for condition in CONDITIONS
    }
    add_gate(gates, "C4", "common real-energy share >= 50% in both conditions", all(value >= 0.50 for value in common_real.values()), common_real)
    noncommon_imag = {
        condition: 1.0 - energy_shares[condition]["imag"]["common"]
        for condition in CONDITIONS
    }
    add_gate(gates, "C5", "non-common imaginary-energy share >= 50% in both conditions", all(value >= 0.50 for value in noncommon_imag.values()), noncommon_imag)
    zero_improvement = {
        condition: float(metric_by[condition]["improvement_vs_zero_pct"])
        for condition in CONDITIONS
    }
    add_gate(gates, "C6", "held-out error improves zero by >= 10% in both conditions", all(value >= 10.0 for value in zero_improvement.values()), zero_improvement)
    loo_improvement = {
        condition: float(metric_by[condition]["improvement_vs_loo_mean_pct"])
        for condition in CONDITIONS
    }
    add_gate(gates, "C7", "held-out error improves LOO mean by >= 5% in both conditions", all(value >= 5.0 for value in loo_improvement.values()), loo_improvement)
    real_sign = {
        condition: float(metric_by[condition]["real_sign_accuracy"])
        for condition in CONDITIONS
    }
    add_gate(gates, "C8", "held-out real sign accuracy >= 75% in both conditions", all(value >= 0.75 for value in real_sign.values()), real_sign)
    imag_sign = {
        condition: float(metric_by[condition]["imag_sign_accuracy"])
        for condition in CONDITIONS
    }
    add_gate(gates, "C9", "held-out imaginary sign accuracy >= 60% in both conditions", all(value >= 0.60 for value in imag_sign.values()), imag_sign)
    interaction_share = {
        condition: energy_shares[condition]["complex"]["interaction"]
        for condition in CONDITIONS
    }
    add_gate(gates, "C10", "interaction complex-energy share <= 25% in both conditions", all(value <= 0.25 for value in interaction_share.values()), interaction_share)

    result = {
        "test_id": "Q12-RESIDUAL-CHILDREN-v1",
        "ledger_id": "T271",
        "test_class": "post-outcome orthogonal child decomposition with held-out identity",
        "protocol_sha256": protocol_hash,
        "verdict": "CALIBRATED" if all(gate["passed"] for gate in gates) else "PARTIAL / NOT CALIBRATED",
        "summary": {
            "records": len(source),
            "cells": len(cells),
            "energy_shares": energy_shares,
            "heldout_metrics": {
                condition: metric_by[condition] for condition in CONDITIONS
            },
            "gates_passed": sum(bool(gate["passed"]) for gate in gates),
            "gates_total": len(gates),
        },
        "gates": gates,
        "boundary": (
            "The four child modes are an exact coordinate rotation of Q11 residuals. "
            "Only held-out-state performance and energy allocation are empirical. "
            "The test does not identify physical environmental channels or predict future times."
        ),
    }

    with MODES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(modes_rows[0]))
        writer.writeheader()
        writer.writerows(modes_rows)
    with PREDICTIONS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    with METRICS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics[0]))
        writer.writeheader()
        writer.writerows(metrics)
    with GATES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("gate_id", "description", "passed", "value"))
        writer.writeheader()
        for gate in gates:
            writer.writerow({**gate, "value": json.dumps(gate["value"], sort_keys=True)})
    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    build_svg(energy_shares, predictions, metrics)
    print(json.dumps(result["summary"], indent=2))
    print(f"Verdict: {result['verdict']}")
    return result


if __name__ == "__main__":
    run()
