#!/usr/bin/env python3
"""Decompress Q7 Bell trajectories into the frozen Q8 ARA relation plane."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from q7_bell_decoherence_test import (
    AXES,
    BASIS,
    DATA,
    FILES,
    PAULI,
    STATES,
    TSIRELSON,
    WAITS,
    density_from_expectations,
    expectation,
    load_condition,
    physical_projection,
)


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q8_BELL_RELATION_PLANE_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q8_BELL_RELATION_PLANE_PROTOCOL_v1_FROZEN.sha256"
RECORDS_CSV = HERE / "Q8_BELL_RELATION_PLANE_RECORDS.csv"
GATES_CSV = HERE / "Q8_BELL_RELATION_PLANE_GATES.csv"
RESULTS_JSON = HERE / "Q8_BELL_RELATION_PLANE_RESULTS.json"
FIGURE_SVG = HERE / "Q8_BELL_RELATION_PLANE_DECONSTRUCTION.svg"

STATE_STYLE = {
    "Phi-plus": ("#2F6B9A", "o", "-"),
    "Phi-minus": ("#D17A22", "^", "--"),
    "Psi-plus": ("#6E7F3B", "s", "-."),
    "Psi-minus": ("#B05A7A", "D", ":"),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed = sha256(PROTOCOL)
    if expected != observed:
        raise RuntimeError(f"Q8 frozen protocol mismatch: {observed} != {expected}")
    return observed


def tensor_from_rho(rho: np.ndarray) -> np.ndarray:
    return np.asarray(
        [
            [expectation(rho, left + right) for right in AXES]
            for left in AXES
        ],
        dtype=float,
    )


def physical_diagnostics(rho: np.ndarray, tensor: np.ndarray) -> dict[str, float]:
    singular = np.sort(np.linalg.svd(tensor, compute_uv=False))[::-1]
    eigenvalues = np.linalg.eigvalsh(rho)
    return {
        "s1": float(singular[0]),
        "s2": float(singular[1]),
        "s3": float(singular[2]),
        "chsh_smax": float(2 * math.sqrt(singular[0] ** 2 + singular[1] ** 2)),
        "strong_axes": int(np.sum(singular >= 0.50)),
        "trace_error": float(abs(np.trace(rho) - 1)),
        "minimum_eigenvalue": float(np.min(eigenvalues)),
        "hermiticity_residual": float(np.max(np.abs(rho - rho.conj().T))),
    }


def relation_coordinates(state: str, tensor: np.ndarray) -> dict[str, float | np.ndarray]:
    xx, xy, xz = tensor[0]
    yx, yy, yz = tensor[1]
    zx, zy, zz = tensor[2]
    core = np.zeros((3, 3), dtype=float)

    if state.startswith("Phi"):
        u = 0.5 * (xx - yy)
        v = 0.5 * (xy + yx)
        alt_u = 0.5 * (xx + yy)
        alt_v = 0.5 * (yx - xy)
        core[0, 0] = u
        core[1, 1] = -u
        core[0, 1] = v
        core[1, 0] = v
        family = "Phi"
    else:
        u = 0.5 * (xx + yy)
        v = 0.5 * (yx - xy)
        alt_u = 0.5 * (xx - yy)
        alt_v = 0.5 * (xy + yx)
        core[0, 0] = u
        core[1, 1] = u
        core[0, 1] = -v
        core[1, 0] = v
        family = "Psi"

    core[2, 2] = zz
    radius = float(math.hypot(u, v))
    alt_radius = float(math.hypot(alt_u, alt_v))
    k = float(abs(zz))
    tensor_energy = float(np.sum(tensor**2))
    residual_energy = float(np.sum((tensor - core) ** 2))
    core_share = (
        float(1 - residual_energy / tensor_energy)
        if tensor_energy > 1e-15
        else 1.0
    )
    return {
        "family": family,
        "u": float(u),
        "v": float(v),
        "radius": radius,
        "theta_rad": float(math.atan2(v, u)),
        "theta_deg": float(math.degrees(math.atan2(v, u))),
        "k": k,
        "zz_signed": float(zz),
        "te_observed": float(k + radius),
        "hidden_residual": float(2 - k - radius),
        "connection_deficit": float(1 - k),
        "phase_deficit": float(1 - radius),
        "alt_u": float(alt_u),
        "alt_v": float(alt_v),
        "alt_radius": alt_radius,
        "tensor_energy": tensor_energy,
        "core_residual_energy": residual_energy,
        "core_share": core_share,
        "xz": float(xz),
        "yz": float(yz),
        "zx": float(zx),
        "zy": float(zy),
        "core_tensor": core,
    }


def first_index(series: list[dict[str, object]], predicate) -> int | None:
    for record in series:
        if predicate(record):
            return int(record["wait_index"])
    return None


def gmean(values: list[float]) -> float:
    return float(math.exp(sum(math.log(value) for value in values) / len(values)))


def add_gate(gates: list[dict[str, object]], gate_id: str, description: str, passed: bool, value: object) -> None:
    gates.append(
        {
            "gate_id": gate_id,
            "description": description,
            "passed": bool(passed),
            "value": value,
        }
    )


def build_figure(records_by: dict[str, dict[str, list[dict[str, object]]]]) -> None:
    """Write a dependency-free research SVG with two phase planes and two TE stacks."""

    width, height = 1500, 1180
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>"
        "text{font-family:Arial,sans-serif;fill:#20252B}"
        ".title{font-size:28px;font-weight:700}.panel{font-size:19px;font-weight:700}"
        ".sub{font-size:13px;fill:#56616B}.axis{font-size:13px;fill:#46515A}"
        ".tick{font-size:11px;fill:#68737D}.legend{font-size:12px}"
        "</style>",
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        '<text x="60" y="48" class="title">Bell relation-plane and TE-ARA decomposition</text>',
        '<text x="60" y="73" class="sub">Four public Bell states; Q8 post-outcome deconstruction of the Q7 physical trajectories</text>',
    ]

    def phase_panel(x: float, y: float, w: float, h: float, condition: str) -> None:
        px, py = x + 70, y + 95
        pw, ph = w - 100, h - 150
        scale = 0.45 * min(pw, ph)
        cx, cy = px + pw / 2, py + ph / 2
        parts.extend(
            [
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#FBFCFD" stroke="#DCE2E7"/>',
                f'<text x="{x+22}" y="{y+30}" class="panel">{condition} Bell-family relation plane</text>',
                f'<text x="{x+22}" y="{y+52}" class="sub">Open marker = first wait; dashed circle = ideal relation radius</text>',
                f'<line x1="{cx-scale*1.08}" y1="{cy}" x2="{cx+scale*1.08}" y2="{cy}" stroke="#CCD3D9"/>',
                f'<line x1="{cx}" y1="{cy-scale*1.08}" x2="{cx}" y2="{cy+scale*1.08}" stroke="#CCD3D9"/>',
                f'<circle cx="{cx}" cy="{cy}" r="{scale}" fill="none" stroke="#9EA8B0" stroke-dasharray="7 6"/>',
                f'<text x="{cx+scale+8}" y="{cy+5}" class="tick">u=1</text>',
                f'<text x="{cx+5}" y="{cy-scale-8}" class="tick">v=1</text>',
            ]
        )
        for state_index, state in enumerate(STATES):
            color, marker, linestyle = STATE_STYLE[state]
            legend_x = x + 24 + state_index * 150
            parts.extend(
                [
                    f'<line x1="{legend_x}" y1="{y+73}" x2="{legend_x+18}" y2="{y+73}" stroke="{color}" stroke-width="3"/>',
                    f'<text x="{legend_x+24}" y="{y+77}" class="legend" style="fill:{color}">{state}</text>',
                ]
            )
            series = records_by[condition][state]
            points = [
                (
                    cx + scale * float(record["u"]),
                    cy - scale * float(record["v"]),
                )
                for record in series
            ]
            dash = "" if linestyle == "-" else ' stroke-dasharray="7 5"'
            point_string = " ".join(f"{xx:.2f},{yy:.2f}" for xx, yy in points)
            parts.append(
                f'<polyline points="{point_string}" fill="none" stroke="{color}" stroke-width="2.5"{dash}/>'
            )
            for index, (xx, yy) in enumerate(points):
                fill = "#FFFFFF" if index == 0 else color
                radius = 6 if index == 0 else 3.5
                parts.append(
                    f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="{radius}" fill="{fill}" stroke="{color}" stroke-width="2"/>'
                )
        parts.extend(
            [
                f'<text x="{cx-65}" y="{y+h-18}" class="axis">u — first relation cut</text>',
                f'<text x="{x+18}" y="{cy}" class="axis" transform="rotate(-90 {x+18} {cy})">v — perpendicular cut</text>',
            ]
        )

    def te_panel(x: float, y: float, w: float, h: float, condition: str) -> None:
        px, py = x + 75, y + 75
        pw, ph = w - 110, h - 130
        waits = np.asarray(WAITS[condition], float)
        mean_k = np.asarray(
            [
                np.mean([records_by[condition][state][i]["k"] for state in STATES])
                for i in range(len(waits))
            ]
        )
        mean_r = np.asarray(
            [
                np.mean([records_by[condition][state][i]["radius"] for state in STATES])
                for i in range(len(waits))
            ]
        )
        top_k = mean_k
        top_r = mean_k + mean_r
        top_h = np.full_like(mean_k, 2.0)

        if condition == "Hahn":
            x_values = np.log10(waits)
        else:
            x_values = waits
        x_min, x_max = float(np.min(x_values)), float(np.max(x_values))

        def map_x(value: float) -> float:
            return px + (value - x_min) / (x_max - x_min) * pw

        def map_y(value: float) -> float:
            return py + ph - value / 2.0 * ph

        def area_polygon(lower: np.ndarray, upper: np.ndarray) -> str:
            upper_points = [
                (map_x(float(xv)), map_y(float(yv)))
                for xv, yv in zip(x_values, upper)
            ]
            lower_points = [
                (map_x(float(xv)), map_y(float(yv)))
                for xv, yv in zip(x_values[::-1], lower[::-1])
            ]
            return " ".join(
                f"{xx:.2f},{yy:.2f}" for xx, yy in upper_points + lower_points
            )

        zeros = np.zeros_like(mean_k)
        parts.extend(
            [
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#FBFCFD" stroke="#DCE2E7"/>',
                f'<text x="{x+22}" y="{y+30}" class="panel">{condition} observable TE-ARA closure</text>',
                f'<text x="{x+22}" y="{y+52}" class="sub">Four-state mean; K + R + unresolved H = 2</text>',
                f'<line x1="{px}" y1="{py}" x2="{px}" y2="{py+ph}" stroke="#9EA8B0"/>',
                f'<line x1="{px}" y1="{py+ph}" x2="{px+pw}" y2="{py+ph}" stroke="#9EA8B0"/>',
                f'<polygon points="{area_polygon(zeros, top_k)}" fill="#2F6B9A" fill-opacity="0.90"/>',
                f'<polygon points="{area_polygon(top_k, top_r)}" fill="#D7A33D" fill-opacity="0.90"/>',
                f'<polygon points="{area_polygon(top_r, top_h)}" fill="#D9DEE3" fill-opacity="0.95"/>',
            ]
        )
        for value in (0, 1, 2):
            yy = map_y(value)
            parts.extend(
                [
                    f'<line x1="{px}" y1="{yy}" x2="{px+pw}" y2="{yy}" stroke="#EDF0F2"/>',
                    f'<text x="{px-24}" y="{yy+4}" class="tick">{value}</text>',
                ]
            )
        tick_indices = [0, len(waits) // 2, len(waits) - 1]
        for index in tick_indices:
            xx = map_x(float(x_values[index]))
            parts.append(
                f'<text x="{xx-16}" y="{py+ph+20}" class="tick">{waits[index]:g}</text>'
            )
        legend_y = y + 69
        legend_items = [
            ("#2F6B9A", "persistent parity K"),
            ("#D7A33D", "phase relation R"),
            ("#D9DEE3", "unresolved H"),
        ]
        lx = x + 25
        for color, label in legend_items:
            parts.extend(
                [
                    f'<rect x="{lx}" y="{legend_y-11}" width="14" height="14" fill="{color}" stroke="#AAB2BA"/>',
                    f'<text x="{lx+20}" y="{legend_y}" class="legend">{label}</text>',
                ]
            )
            lx += 175
        parts.extend(
            [
                f'<text x="{px+pw/2-45}" y="{py+ph+40}" class="axis">Wait time (μs)</text>',
                f'<text x="{x+18}" y="{py+ph/2}" class="axis" transform="rotate(-90 {x+18} {py+ph/2})">Normalized share</text>',
            ]
        )

    phase_panel(55, 95, 680, 500, "Ramsey")
    phase_panel(765, 95, 680, 500, "Hahn")
    te_panel(55, 625, 680, 500, "Ramsey")
    te_panel(765, 625, 680, 500, "Hahn")
    parts.append("</svg>")
    FIGURE_SVG.write_text("\n".join(parts), encoding="utf-8")


def run() -> dict[str, object]:
    protocol_hash = verify_protocol()
    records: list[dict[str, object]] = []
    records_by: dict[str, dict[str, list[dict[str, object]]]] = {}

    for condition in ("Ramsey", "Hahn"):
        pauli, _, _ = load_condition(condition)
        records_by[condition] = {}
        for state_index, state in enumerate(STATES):
            series = []
            for wait_index, wait_us in enumerate(WAITS[condition]):
                exp = {
                    basis: 4 * coefficient
                    for basis, coefficient in zip(BASIS, pauli[state_index][wait_index])
                }
                rho = physical_projection(density_from_expectations(exp))
                tensor = tensor_from_rho(rho)
                diag = physical_diagnostics(rho, tensor)
                rel = relation_coordinates(state, tensor)
                singular_model = np.sort(
                    np.asarray([rel["k"], rel["radius"], rel["radius"]], float)
                )[::-1]
                singular_actual = np.asarray([diag["s1"], diag["s2"], diag["s3"]], float)
                singular_mae = float(np.mean(np.abs(singular_actual - singular_model)))
                transverse_radius = 0.5 * (diag["s2"] + diag["s3"])
                inferred_v_magnitude = float(
                    math.sqrt(max(0.0, transverse_radius**2 - float(rel["u"]) ** 2))
                )
                hidden_quadrature_error = float(
                    abs(inferred_v_magnitude - abs(float(rel["v"])))
                )
                record = {
                    "condition": condition,
                    "state": state,
                    "family": rel["family"],
                    "wait_index": wait_index,
                    "wait_us": float(wait_us),
                    "u": rel["u"],
                    "v": rel["v"],
                    "radius": rel["radius"],
                    "theta_rad": rel["theta_rad"],
                    "theta_deg": rel["theta_deg"],
                    "k": rel["k"],
                    "zz_signed": rel["zz_signed"],
                    "te_observed": rel["te_observed"],
                    "hidden_residual": rel["hidden_residual"],
                    "connection_deficit": rel["connection_deficit"],
                    "phase_deficit": rel["phase_deficit"],
                    "alt_u": rel["alt_u"],
                    "alt_v": rel["alt_v"],
                    "alt_radius": rel["alt_radius"],
                    "core_share": rel["core_share"],
                    "core_residual_energy": rel["core_residual_energy"],
                    "tensor_energy": rel["tensor_energy"],
                    "xz": rel["xz"],
                    "yz": rel["yz"],
                    "zx": rel["zx"],
                    "zy": rel["zy"],
                    "s1": diag["s1"],
                    "s2": diag["s2"],
                    "s3": diag["s3"],
                    "strong_axes": diag["strong_axes"],
                    "chsh_smax": diag["chsh_smax"],
                    "singular_model_mae": singular_mae,
                    "transverse_radius_from_singulars": transverse_radius,
                    "inferred_v_magnitude": inferred_v_magnitude,
                    "hidden_quadrature_abs_error": hidden_quadrature_error,
                    "trace_error": diag["trace_error"],
                    "minimum_eigenvalue": diag["minimum_eigenvalue"],
                    "hermiticity_residual": diag["hermiticity_residual"],
                }
                records.append(record)
                series.append(record)

            unwrapped = np.unwrap(np.asarray([record["theta_rad"] for record in series], float))
            for record, theta_unwrapped in zip(series, unwrapped):
                record["theta_unwrapped_rad"] = float(theta_unwrapped)
                record["theta_unwrapped_deg"] = float(math.degrees(theta_unwrapped))
            records_by[condition][state] = series

    condition_core_medians = {
        condition: float(
            np.median(
                [
                    record["core_share"]
                    for state in STATES
                    for record in records_by[condition][state]
                ]
            )
        )
        for condition in ("Ramsey", "Hahn")
    }
    physicality_ok = all(
        record["trace_error"] <= 1e-12
        and record["minimum_eigenvalue"] >= -1e-12
        and record["hermiticity_residual"] <= 1e-12
        and record["chsh_smax"] <= TSIRELSON + 1e-12
        for record in records
    )
    initial = {
        condition: {state: records_by[condition][state][0] for state in STATES}
        for condition in ("Ramsey", "Hahn")
    }
    final_ramsey = {state: records_by["Ramsey"][state][-1] for state in STATES}
    k_retention = {
        state: final_ramsey[state]["k"] / initial["Ramsey"][state]["k"]
        for state in STATES
    }
    r_retention = {
        state: final_ramsey[state]["radius"] / initial["Ramsey"][state]["radius"]
        for state in STATES
    }
    median_k_retention = float(np.median(list(k_retention.values())))
    median_r_retention = float(np.median(list(r_retention.values())))
    singular_model_median_mae = float(
        np.median([record["singular_model_mae"] for record in records])
    )
    hidden_quadrature_median_error = float(
        np.median([record["hidden_quadrature_abs_error"] for record in records])
    )

    first_r_below: dict[str, dict[str, dict[str, float | int | None]]] = {
        "Ramsey": {},
        "Hahn": {},
    }
    first_one_axis: dict[str, dict[str, int | None]] = {"Ramsey": {}, "Hahn": {}}
    for condition in ("Ramsey", "Hahn"):
        for state in STATES:
            series = records_by[condition][state]
            r_index = first_index(series, lambda row: row["radius"] < 0.50)
            axis_index = first_index(series, lambda row: row["strong_axes"] == 1)
            first_r_below[condition][state] = {
                "index": r_index,
                "wait_us": None if r_index is None else float(series[r_index]["wait_us"]),
            }
            first_one_axis[condition][state] = axis_index

    ramsey_cross = [
        float(first_r_below["Ramsey"][state]["wait_us"])
        for state in STATES
        if first_r_below["Ramsey"][state]["wait_us"] is not None
    ]
    hahn_cross = [
        float(first_r_below["Hahn"][state]["wait_us"])
        for state in STATES
        if first_r_below["Hahn"][state]["wait_us"] is not None
    ]
    delay_ratio = (
        gmean(hahn_cross) / gmean(ramsey_cross)
        if len(ramsey_cross) == 4 and len(hahn_cross) == 4
        else float("nan")
    )

    gates: list[dict[str, object]] = []
    add_gate(gates, "D1", "all 88 physical reconstructions pass", physicality_ok, physicality_ok)
    add_gate(
        gates,
        "D2",
        "median compact-core tensor share >= 0.90 in Ramsey and Hahn",
        all(value >= 0.90 for value in condition_core_medians.values()),
        condition_core_medians,
    )
    initial_checks = {
        f"{condition}/{state}": {
            "k": initial[condition][state]["k"],
            "radius": initial[condition][state]["radius"],
            "te_observed": initial[condition][state]["te_observed"],
        }
        for condition in ("Ramsey", "Hahn")
        for state in STATES
    }
    add_gate(
        gates,
        "D3",
        "all initial states have K>=0.80, R>=0.80 and TE>=1.60",
        all(
            values["k"] >= 0.80
            and values["radius"] >= 0.80
            and values["te_observed"] >= 1.60
            for values in initial_checks.values()
        ),
        initial_checks,
    )
    add_gate(
        gates,
        "D4",
        "every final Ramsey K retention >= 0.75",
        all(value >= 0.75 for value in k_retention.values()),
        k_retention,
    )
    add_gate(
        gates,
        "D5",
        "every final Ramsey R retention <= 0.20",
        all(value <= 0.20 for value in r_retention.values()),
        r_retention,
    )
    add_gate(
        gates,
        "D6",
        "median K-minus-R retention gap >= 0.60",
        median_k_retention - median_r_retention >= 0.60,
        {
            "median_k_retention": median_k_retention,
            "median_r_retention": median_r_retention,
            "gap": median_k_retention - median_r_retention,
        },
    )
    add_gate(
        gates,
        "D7",
        "median singular-model MAE <= 0.08",
        singular_model_median_mae <= 0.08,
        singular_model_median_mae,
    )
    alignment = {
        state: {
            "first_R_below_index": first_r_below["Ramsey"][state]["index"],
            "first_one_axis_index": first_one_axis["Ramsey"][state],
        }
        for state in STATES
    }
    add_gate(
        gates,
        "D8",
        "Ramsey R<0.50 and first one-axis observations align within one sample",
        all(
            values["first_R_below_index"] is not None
            and values["first_one_axis_index"] is not None
            and abs(values["first_R_below_index"] - values["first_one_axis_index"]) <= 1
            for values in alignment.values()
        ),
        alignment,
    )
    add_gate(
        gates,
        "D9",
        "Hahn/Ramsey R<0.50 delay ratio >= 4",
        math.isfinite(delay_ratio) and delay_ratio >= 4.0,
        delay_ratio,
    )
    initial_family_margins = {
        f"{condition}/{state}": (
            initial[condition][state]["radius"] - initial[condition][state]["alt_radius"]
        )
        for condition in ("Ramsey", "Hahn")
        for state in STATES
    }
    add_gate(
        gates,
        "D10",
        "declared initial Bell-family radius exceeds alternate by >= 0.60",
        all(value >= 0.60 for value in initial_family_margins.values()),
        initial_family_margins,
    )
    add_gate(
        gates,
        "D11",
        "hidden quadrature magnitude median absolute error <= 0.08",
        hidden_quadrature_median_error <= 0.08,
        hidden_quadrature_median_error,
    )

    state_summaries = {}
    for condition in ("Ramsey", "Hahn"):
        state_summaries[condition] = {}
        for state in STATES:
            series = records_by[condition][state]
            state_summaries[condition][state] = {
                "initial": {
                    "u": series[0]["u"],
                    "v": series[0]["v"],
                    "radius": series[0]["radius"],
                    "theta_deg": series[0]["theta_deg"],
                    "k": series[0]["k"],
                    "te_observed": series[0]["te_observed"],
                    "hidden_residual": series[0]["hidden_residual"],
                    "core_share": series[0]["core_share"],
                },
                "final": {
                    "u": series[-1]["u"],
                    "v": series[-1]["v"],
                    "radius": series[-1]["radius"],
                    "theta_deg": series[-1]["theta_deg"],
                    "k": series[-1]["k"],
                    "te_observed": series[-1]["te_observed"],
                    "hidden_residual": series[-1]["hidden_residual"],
                    "core_share": series[-1]["core_share"],
                },
                "phase_rotation_range_deg": float(
                    max(record["theta_unwrapped_deg"] for record in series)
                    - min(record["theta_unwrapped_deg"] for record in series)
                ),
                "first_radius_below_0p50_us": first_r_below[condition][state][
                    "wait_us"
                ],
            }

    result = {
        "test_id": "Q8-BELL-RELATION-PLANE-v1",
        "ledger_id": "T267",
        "test_class": "post-outcome ARA deconstruction / exact quantum crosswalk",
        "verdict": "CALIBRATED" if all(gate["passed"] for gate in gates) else "NOT CALIBRATED",
        "protocol_sha256": protocol_hash,
        "summary": {
            "condition_core_share_medians": condition_core_medians,
            "median_final_ramsey_k_retention": median_k_retention,
            "median_final_ramsey_r_retention": median_r_retention,
            "median_retention_gap": median_k_retention - median_r_retention,
            "median_singular_model_mae": singular_model_median_mae,
            "median_hidden_quadrature_abs_error": hidden_quadrature_median_error,
            "ramsey_radius_crossing_geomean_us": gmean(ramsey_cross),
            "hahn_radius_crossing_geomean_us": gmean(hahn_cross),
            "hahn_to_ramsey_radius_crossing_ratio": delay_ratio,
            "gates_passed": sum(gate["passed"] for gate in gates),
            "gates_total": len(gates),
        },
        "first_radius_below_0p50": first_r_below,
        "state_summaries": state_summaries,
        "gates": gates,
        "interpretation_boundary": (
            "H is an unresolved relation deficit inside the selected two-qubit boundary, "
            "not a uniquely identified environmental state or conserved energy."
        ),
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
    build_figure(records_by)
    return result


if __name__ == "__main__":
    result = run()
    print(json.dumps(result["summary"], indent=2))
    print(f"Verdict: {result['verdict']}")
