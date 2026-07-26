#!/usr/bin/env python3
"""Run the frozen Q11 visible/unresolved Information³ relation test."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
INPUT = HERE / "Q9_INFORMATION3_BELL_ALLOCATIONS.csv"
PROTOCOL = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_PROTOCOL_v1_FROZEN.sha256"
RECORDS_CSV = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
METRICS_CSV = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_METRICS.csv"
GATES_CSV = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_GATES.csv"
RESULTS_JSON = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RESULTS.json"
FIGURE_SVG = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_GEOMETRY.svg"

CONDITIONS = ("Ramsey", "Hahn")
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
COLORS = {"Ramsey": "#2F6B9A", "Hahn": "#D17A22"}
STATE_DASH = {
    "Phi-plus": "",
    "Phi-minus": "7 5",
    "Psi-plus": "10 4",
    "Psi-minus": "3 4",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed = digest(PROTOCOL)
    if expected != observed:
        raise RuntimeError(f"Q11 protocol mismatch: {observed} != {expected}")
    return observed


def coordinates(values: np.ndarray, times: np.ndarray) -> dict[str, object]:
    minimum = float(np.min(values))
    maximum = float(np.max(values))
    span = maximum - minimum
    if span <= 0:
        raise ValueError("Q11 requires a nonzero trajectory range")
    x = 2.0 * (values - minimum) / span
    derivative = np.gradient(values, times, edge_order=2)
    speed = float(np.max(np.abs(derivative)))
    if speed <= 0:
        raise ValueError("Q11 requires a nonzero trajectory derivative")
    y = 1.0 - np.clip(derivative / speed, -1.0, 1.0)
    c = (x - 1.0) + 1j * (y - 1.0)
    return {
        "minimum": minimum,
        "maximum": maximum,
        "span": span,
        "derivative": derivative,
        "rate_scale": speed,
        "x": x,
        "y": y,
        "c": c,
    }


def control_predictions(x_v: float, y_v: float) -> dict[str, tuple[float, float]]:
    return {
        "anti_phase": (2.0 - x_v, 2.0 - y_v),
        "ridge_only": (1.0, 1.0),
        "same_phase": (x_v, y_v),
        "amplitude_only": (2.0 - x_v, 1.0),
        "direction_only": (1.0, 2.0 - y_v),
    }


def branch(y: float, tolerance: float = 1e-12) -> int:
    if y < 1.0 - tolerance:
        return 1
    if y > 1.0 + tolerance:
        return -1
    return 0


def residual_quadrant(real: float, imag: float) -> str:
    horizontal = "target_more_unresolved" if real >= 0 else "visible_prediction_more_unresolved"
    vertical = "target_more_closing" if imag >= 0 else "target_more_opening"
    return f"{horizontal}/{vertical}"


def summarize(rows: list[dict[str, object]], label: str) -> dict[str, object]:
    x_actual = np.array([float(row["target_x"]) for row in rows])
    y_actual = np.array([float(row["target_y"]) for row in rows])
    x_pred = np.array([float(row["predicted_x"]) for row in rows])
    y_pred = np.array([float(row["predicted_y"]) for row in rows])
    distance = np.hypot(x_actual - x_pred, y_actual - y_pred)
    metrics: dict[str, object] = {
        "scope": label,
        "records": len(rows),
        "amplitude_correlation": float(np.corrcoef(x_pred, x_actual)[0, 1]),
        "direction_correlation": float(np.corrcoef(y_pred, y_actual)[0, 1]),
        "amplitude_mae": float(np.mean(np.abs(x_actual - x_pred))),
        "direction_mae": float(np.mean(np.abs(y_actual - y_pred))),
        "anti_phase_mean_2d_error": float(np.mean(distance)),
        "anti_phase_median_2d_error": float(np.median(distance)),
    }
    for control in (
        "ridge_only",
        "same_phase",
        "amplitude_only",
        "direction_only",
    ):
        values = np.array([float(row[f"{control}_2d_error"]) for row in rows])
        metrics[f"{control}_mean_2d_error"] = float(np.mean(values))
    ridge_error = float(metrics["ridge_only_mean_2d_error"])
    same_error = float(metrics["same_phase_mean_2d_error"])
    anti_error = float(metrics["anti_phase_mean_2d_error"])
    metrics["improvement_vs_ridge_pct"] = 100.0 * (ridge_error - anti_error) / ridge_error
    metrics["improvement_vs_same_phase_pct"] = (
        100.0 * (same_error - anti_error) / same_error
    )

    branch_rows = [
        row
        for row in rows
        if int(row["target_branch"]) != 0 and int(row["predicted_branch"]) != 0
    ]
    metrics["branch_evaluable"] = len(branch_rows)
    metrics["branch_accuracy"] = (
        sum(
            int(row["target_branch"]) == int(row["predicted_branch"])
            for row in branch_rows
        )
        / len(branch_rows)
        if branch_rows
        else float("nan")
    )
    angular = [
        float(row["opposition_score"])
        for row in rows
        if bool(row["angle_evaluable"])
    ]
    metrics["angle_evaluable"] = len(angular)
    metrics["median_opposition_score"] = (
        float(np.median(angular)) if angular else float("nan")
    )
    metrics["mean_residual_radius"] = float(
        np.mean([float(row["residual_radius"]) for row in rows])
    )
    metrics["median_residual_radius"] = float(
        np.median([float(row["residual_radius"]) for row in rows])
    )
    return metrics


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


def svg_text(parts: list[str], x: float, y: float, text: str, css: str = "label") -> None:
    parts.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{css}">{text}</text>')


def build_svg(records: list[dict[str, object]], metrics: list[dict[str, object]]) -> None:
    width, height = 1500, 1120
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>",
        "text{font-family:Arial,sans-serif;fill:#17212B}.title{font-size:27px;font-weight:700}.subtitle{font-size:13px;fill:#405164}.paneltitle{font-size:19px;font-weight:700}.axis{font-size:12px;fill:#405164}.tick{font-size:11px;fill:#566573}.label{font-size:12px}.small{font-size:10px;fill:#566573}",
        "</style>",
        '<rect width="1500" height="1120" fill="#FFFFFF"/>',
    ]
    svg_text(parts, 52, 44, "Visible relation predicts independently defined unresolved geometry", "title")
    svg_text(
        parts,
        52,
        69,
        "Q11: parameter-free anti-phase map; 88 points from eight public Bell-state trajectories",
        "subtitle",
    )

    panels = [(50, 95, 680, 430), (770, 95, 680, 430)]
    for panel_index, (px, py, pw, ph) in enumerate(panels):
        parts.append(
            f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
        )
        title = (
            "Amplitude: predicted versus observed"
            if panel_index == 0
            else "Opening/closing: predicted versus observed"
        )
        svg_text(parts, px + 22, py + 32, title, "paneltitle")
        svg_text(parts, px + 22, py + 54, "Diagonal is exact anti-phase agreement", "subtitle")
        left, top = px + 72, py + 78
        chart_w, chart_h = pw - 105, ph - 120
        parts.append(
            f'<rect x="{left}" y="{top}" width="{chart_w}" height="{chart_h}" fill="#FFFFFF" stroke="#DCE3E9"/>'
        )
        for value in (0, 0.5, 1, 1.5, 2):
            xx = left + value / 2 * chart_w
            yy = top + chart_h - value / 2 * chart_h
            parts.append(
                f'<line x1="{xx}" y1="{top}" x2="{xx}" y2="{top+chart_h}" stroke="#EDF1F4"/>'
            )
            parts.append(
                f'<line x1="{left}" y1="{yy}" x2="{left+chart_w}" y2="{yy}" stroke="#EDF1F4"/>'
            )
            svg_text(parts, xx - 6, top + chart_h + 18, f"{value:g}", "tick")
            svg_text(parts, left - 28, yy + 4, f"{value:g}", "tick")
        parts.append(
            f'<line x1="{left}" y1="{top+chart_h}" x2="{left+chart_w}" y2="{top}" stroke="#273746" stroke-width="1.6"/>'
        )
        x_field = "predicted_x" if panel_index == 0 else "predicted_y"
        y_field = "target_x" if panel_index == 0 else "target_y"
        for row in records:
            cx = left + float(row[x_field]) / 2 * chart_w
            cy = top + chart_h - float(row[y_field]) / 2 * chart_h
            color = COLORS[str(row["condition"])]
            parts.append(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="3.4" fill="{color}" fill-opacity="0.58" stroke="#FFFFFF" stroke-width="0.6"/>'
            )
        svg_text(parts, left + chart_w / 2 - 45, top + chart_h + 39, "predicted coordinate", "axis")
        parts.append(
            f'<text x="{left-53}" y="{top+chart_h/2+45}" class="axis" transform="rotate(-90 {left-53} {top+chart_h/2+45})">observed coordinate</text>'
        )

    residual_x, residual_y, residual_w, residual_h = 50, 555, 680, 510
    parts.append(
        f'<rect x="{residual_x}" y="{residual_y}" width="{residual_w}" height="{residual_h}" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
    )
    svg_text(parts, residual_x + 22, residual_y + 32, "Residual child field E = C(P) + C(V)", "paneltitle")
    svg_text(
        parts,
        residual_x + 22,
        residual_y + 54,
        "Zero is exact anti-phase; paths retain what the parent relation does not explain",
        "subtitle",
    )
    max_residual = max(
        0.2,
        max(
            max(abs(float(row["residual_real"])), abs(float(row["residual_imag"])))
            for row in records
        )
        * 1.1,
    )
    left, top = residual_x + 74, residual_y + 82
    chart_w, chart_h = residual_w - 112, residual_h - 126
    parts.append(
        f'<rect x="{left}" y="{top}" width="{chart_w}" height="{chart_h}" fill="#FFFFFF" stroke="#DCE3E9"/>'
    )
    x0, y0 = left + chart_w / 2, top + chart_h / 2
    parts.append(f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{top+chart_h}" stroke="#687683"/>')
    parts.append(f'<line x1="{left}" y1="{y0}" x2="{left+chart_w}" y2="{y0}" stroke="#687683"/>')
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for row in records:
        grouped.setdefault((str(row["condition"]), str(row["state"])), []).append(row)
    for (condition, state), rows in grouped.items():
        rows.sort(key=lambda row: int(row["wait_index"]))
        points = []
        for row in rows:
            xx = x0 + float(row["residual_real"]) / max_residual * chart_w / 2
            yy = y0 - float(row["residual_imag"]) / max_residual * chart_h / 2
            points.append(f"{xx:.2f},{yy:.2f}")
        dash = STATE_DASH[state]
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        parts.append(
            f'<polyline points="{" ".join(points)}" fill="none" stroke="{COLORS[condition]}" stroke-width="2.1"{dash_attr} opacity="0.82"/>'
        )
    svg_text(parts, left, top + chart_h + 28, f"-{max_residual:.2f}", "tick")
    svg_text(parts, x0 - 5, top + chart_h + 28, "0", "tick")
    svg_text(parts, left + chart_w - 26, top + chart_h + 28, f"+{max_residual:.2f}", "tick")
    svg_text(parts, left + chart_w / 2 - 60, top + chart_h + 48, "amplitude residual", "axis")
    parts.append(
        f'<text x="{left-51}" y="{top+chart_h/2+48}" class="axis" transform="rotate(-90 {left-51} {top+chart_h/2+48})">direction residual</text>'
    )

    bar_x, bar_y, bar_w, bar_h = 770, 555, 680, 510
    parts.append(
        f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="14" fill="#FAFBFC" stroke="#D6DEE6"/>'
    )
    svg_text(parts, bar_x + 22, bar_y + 32, "Mean two-axis error by method", "paneltitle")
    svg_text(parts, bar_x + 22, bar_y + 54, "Lower is better; anti-phase has no fitted parameters", "subtitle")
    condition_metrics = {str(row["scope"]): row for row in metrics if row["scope"] in CONDITIONS}
    methods = (
        ("anti_phase_mean_2d_error", "ARA anti-phase"),
        ("ridge_only_mean_2d_error", "ridge-only"),
        ("same_phase_mean_2d_error", "same-phase"),
        ("amplitude_only_mean_2d_error", "amplitude-only"),
        ("direction_only_mean_2d_error", "direction-only"),
    )
    max_error = max(
        float(condition_metrics[condition][key])
        for condition in CONDITIONS
        for key, _ in methods
    )
    origin_x, origin_y = bar_x + 188, bar_y + 92
    usable_w = bar_w - 235
    row_height = 66
    for method_index, (key, label) in enumerate(methods):
        yy = origin_y + method_index * row_height
        svg_text(parts, bar_x + 24, yy + 20, label, "label")
        for condition_index, condition in enumerate(CONDITIONS):
            value = float(condition_metrics[condition][key])
            bw = usable_w * value / max_error
            by = yy + condition_index * 23
            parts.append(
                f'<rect x="{origin_x}" y="{by}" width="{bw:.2f}" height="17" rx="2" fill="{COLORS[condition]}" opacity="0.86"/>'
            )
            svg_text(parts, origin_x + bw + 7, by + 13, f"{value:.3f}", "small")
    svg_text(parts, bar_x + 195, bar_y + 452, "Ramsey", "label")
    parts.append(f'<rect x="{bar_x+170}" y="{bar_y+440}" width="16" height="16" fill="{COLORS["Ramsey"]}"/>')
    svg_text(parts, bar_x + 315, bar_y + 452, "Hahn", "label")
    parts.append(f'<rect x="{bar_x+290}" y="{bar_y+440}" width="16" height="16" fill="{COLORS["Hahn"]}"/>')
    parts.append("</svg>")
    FIGURE_SVG.write_text("\n".join(parts), encoding="utf-8")


def run() -> dict[str, object]:
    protocol_hash = verify_protocol()
    with INPUT.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    key_count = len(
        {(row["condition"], row["state"], int(row["wait_index"])) for row in source}
    )
    records: list[dict[str, object]] = []
    data_ok = key_count == 88 and len(source) == 88
    bounds_ok = True
    reconstruction_errors: list[float] = []

    for condition in CONDITIONS:
        for state in STATES:
            rows = sorted(
                [
                    row
                    for row in source
                    if row["condition"] == condition and row["state"] == state
                ],
                key=lambda row: int(row["wait_index"]),
            )
            times = np.array([float(row["wait_us"]) for row in rows])
            visible = np.array(
                [float(row["k"]) + float(row["radius"]) for row in rows]
            )
            target = np.array(
                [float(row["i_unresolved_half_scale"]) for row in rows]
            )
            data_ok = bool(
                data_ok
                and len(rows) == 11
                and len(np.unique(times)) == 11
                and np.all(np.diff(times) > 0)
                and np.ptp(visible) > 0
                and np.ptp(target) > 0
            )
            v = coordinates(visible, times)
            p = coordinates(target, times)
            for index, row in enumerate(rows):
                x_v = float(np.asarray(v["x"])[index])
                y_v = float(np.asarray(v["y"])[index])
                x_p = float(np.asarray(p["x"])[index])
                y_p = float(np.asarray(p["y"])[index])
                c_v = complex(np.asarray(v["c"])[index])
                c_p = complex(np.asarray(p["c"])[index])
                residual = c_p + c_v
                rebuilt = -c_v + residual
                reconstruction_errors.extend(
                    [abs(rebuilt.real - c_p.real), abs(rebuilt.imag - c_p.imag)]
                )
                predictions = control_predictions(x_v, y_v)
                errors = {
                    name: math.hypot(x_p - pair[0], y_p - pair[1])
                    for name, pair in predictions.items()
                }
                predicted_x, predicted_y = predictions["anti_phase"]
                radius_v, radius_p = abs(c_v), abs(c_p)
                angle_evaluable = radius_v >= 0.10 and radius_p >= 0.10
                opposition = (
                    float(-math.cos(math.atan2(c_p.imag, c_p.real) - math.atan2(c_v.imag, c_v.real)))
                    if angle_evaluable
                    else float("nan")
                )
                bounds_ok = bool(
                    bounds_ok
                    and all(
                        math.isfinite(value) and -1e-12 <= value <= 2 + 1e-12
                        for value in (x_v, y_v, x_p, y_p)
                    )
                )
                records.append(
                    {
                        "condition": condition,
                        "state": state,
                        "wait_index": int(row["wait_index"]),
                        "wait_us": float(row["wait_us"]),
                        "visible_value": float(visible[index]),
                        "target_purity_loss": float(target[index]),
                        "visible_x": x_v,
                        "visible_y": y_v,
                        "target_x": x_p,
                        "target_y": y_p,
                        "predicted_x": predicted_x,
                        "predicted_y": predicted_y,
                        "amplitude_error": x_p - predicted_x,
                        "direction_error": y_p - predicted_y,
                        "anti_phase_2d_error": errors["anti_phase"],
                        "ridge_only_2d_error": errors["ridge_only"],
                        "same_phase_2d_error": errors["same_phase"],
                        "amplitude_only_2d_error": errors["amplitude_only"],
                        "direction_only_2d_error": errors["direction_only"],
                        "target_branch": branch(y_p),
                        "predicted_branch": branch(predicted_y),
                        "visible_radius": radius_v,
                        "target_radius": radius_p,
                        "angle_evaluable": angle_evaluable,
                        "opposition_score": opposition,
                        "residual_real": residual.real,
                        "residual_imag": residual.imag,
                        "residual_radius": abs(residual),
                        "residual_theta_deg": math.degrees(
                            math.atan2(residual.imag, residual.real)
                        ),
                        "residual_quadrant": residual_quadrant(
                            residual.real, residual.imag
                        ),
                    }
                )

    metrics = [
        summarize([row for row in records if row["condition"] == condition], condition)
        for condition in CONDITIONS
    ]
    metrics.append(summarize(records, "Overall"))
    metric_by = {str(row["scope"]): row for row in metrics}
    residual_exploratory: dict[str, dict[str, object]] = {}
    for condition in CONDITIONS:
        series: dict[str, dict[str, np.ndarray]] = {}
        for state in STATES:
            subset = sorted(
                [
                    row
                    for row in records
                    if row["condition"] == condition and row["state"] == state
                ],
                key=lambda row: int(row["wait_index"]),
            )
            series[state] = {
                "real": np.array([float(row["residual_real"]) for row in subset]),
                "imag": np.array([float(row["residual_imag"]) for row in subset]),
                "radius": np.array([float(row["residual_radius"]) for row in subset]),
            }
        pairwise_medians = {}
        pairwise_values = {}
        for component in ("real", "imag", "radius"):
            values = {
                f"{left}/{right}": float(
                    np.corrcoef(
                        series[left][component], series[right][component]
                    )[0, 1]
                )
                for left, right in combinations(STATES, 2)
            }
            pairwise_values[component] = values
            pairwise_medians[component] = float(np.median(list(values.values())))
        condition_rows = [
            row for row in records if row["condition"] == condition
        ]
        residual_exploratory[condition] = {
            "median_pairwise_correlations": pairwise_medians,
            "pairwise_correlations": pairwise_values,
            "mean_signed_real": float(
                np.mean([float(row["residual_real"]) for row in condition_rows])
            ),
            "mean_signed_imag": float(
                np.mean([float(row["residual_imag"]) for row in condition_rows])
            ),
            "positive_real_count": sum(
                float(row["residual_real"]) >= 0 for row in condition_rows
            ),
            "positive_imag_count": sum(
                float(row["residual_imag"]) >= 0 for row in condition_rows
            ),
            "records": len(condition_rows),
        }

    gates: list[dict[str, object]] = []
    add_gate(gates, "R1", "88 unique rows form eight valid trajectories", data_ok, data_ok)
    add_gate(gates, "R2", "all visible and target coordinates lie inside 0-2", bounds_ok, bounds_ok)
    amplitude_corr = {
        condition: float(metric_by[condition]["amplitude_correlation"])
        for condition in CONDITIONS
    }
    add_gate(
        gates,
        "R3",
        "amplitude correlation >= 0.95 in both conditions",
        all(value >= 0.95 for value in amplitude_corr.values()),
        amplitude_corr,
    )
    direction_corr = {
        condition: float(metric_by[condition]["direction_correlation"])
        for condition in CONDITIONS
    }
    add_gate(
        gates,
        "R4",
        "direction correlation >= 0.40 in both conditions",
        all(value >= 0.40 for value in direction_corr.values()),
        direction_corr,
    )
    median_error = float(metric_by["Overall"]["anti_phase_median_2d_error"])
    add_gate(gates, "R5", "overall median two-axis error <= 0.25", median_error <= 0.25, median_error)
    ridge_improvement = {
        condition: float(metric_by[condition]["improvement_vs_ridge_pct"])
        for condition in CONDITIONS
    }
    add_gate(
        gates,
        "R6",
        "mean error improvement over ridge-only >= 25% in both conditions",
        all(value >= 25.0 for value in ridge_improvement.values()),
        ridge_improvement,
    )
    same_improvement = {
        condition: float(metric_by[condition]["improvement_vs_same_phase_pct"])
        for condition in CONDITIONS
    }
    add_gate(
        gates,
        "R7",
        "mean error improvement over same-phase >= 50% in both conditions",
        all(value >= 50.0 for value in same_improvement.values()),
        same_improvement,
    )
    branch_accuracy = {
        condition: float(metric_by[condition]["branch_accuracy"])
        for condition in CONDITIONS
    }
    add_gate(
        gates,
        "R8",
        "opening/closing branch accuracy >= 75% in both conditions",
        all(value >= 0.75 for value in branch_accuracy.values()),
        branch_accuracy,
    )
    angular_score = {
        condition: float(metric_by[condition]["median_opposition_score"])
        for condition in CONDITIONS
    }
    add_gate(
        gates,
        "R9",
        "median angular opposition score >= 0.75 in both conditions",
        all(value >= 0.75 for value in angular_score.values()),
        angular_score,
    )
    max_reconstruction_error = max(reconstruction_errors)
    add_gate(
        gates,
        "R10",
        "target relation reconstructed from visible anti-phase plus residual <= 1e-12",
        max_reconstruction_error <= 1e-12,
        max_reconstruction_error,
    )

    result = {
        "test_id": "Q11-VISIBLE-UNRESOLVED-INFORMATION3-v1",
        "ledger_id": "T270",
        "test_class": "post-outcome parameter-free relation calibration",
        "protocol_sha256": protocol_hash,
        "verdict": "CALIBRATED" if all(gate["passed"] for gate in gates) else "NOT CALIBRATED",
        "summary": {
            "records": len(records),
            "amplitude_correlations": amplitude_corr,
            "direction_correlations": direction_corr,
            "overall_median_2d_error": median_error,
            "ridge_improvements_pct": ridge_improvement,
            "same_phase_improvements_pct": same_improvement,
            "branch_accuracy": branch_accuracy,
            "angular_opposition_score": angular_score,
            "gates_passed": sum(bool(gate["passed"]) for gate in gates),
            "gates_total": len(gates),
        },
        "metrics": metrics,
        "post_outcome_exploratory_residual_structure": residual_exploratory,
        "gates": gates,
        "interpretation_boundary": (
            "The target and predictor are different projections of the same reconstructed quantum states. "
            "Q10 already exposed equivalent aggregate agreement. Q11 formalizes an unfitted anti-phase relation "
            "and leaves E as a candidate child field; it does not identify E's physical mechanisms or predict "
            "an independent experiment."
        ),
    }

    with RECORDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
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
    build_svg(records, metrics)
    print(json.dumps(result["summary"], indent=2))
    print(f"Verdict: {result['verdict']}")
    return result


if __name__ == "__main__":
    run()
