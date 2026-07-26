#!/usr/bin/env python3
"""Run the frozen Q10 two-axis ARA of the unresolved H waveform."""

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
PROTOCOL = HERE / "Q10_UNRESOLVED_TWO_AXIS_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q10_UNRESOLVED_TWO_AXIS_PROTOCOL_v1_FROZEN.sha256"
RECORDS_CSV = HERE / "Q10_UNRESOLVED_TWO_AXIS_RECORDS.csv"
TRAJECTORIES_CSV = HERE / "Q10_UNRESOLVED_TWO_AXIS_TRAJECTORIES.csv"
GATES_CSV = HERE / "Q10_UNRESOLVED_TWO_AXIS_GATES.csv"
RESULTS_JSON = HERE / "Q10_UNRESOLVED_TWO_AXIS_RESULTS.json"
FIGURE_SVG = HERE / "Q10_UNRESOLVED_TWO_AXIS_GEOMETRY.svg"

CONDITIONS = ("Ramsey", "Hahn")
STATES = ("Phi-plus", "Phi-minus", "Psi-plus", "Psi-minus")
STATE_STYLE = {
    "Phi-plus": ("#2F6B9A", ""),
    "Phi-minus": ("#D17A22", "7 5"),
    "Psi-plus": ("#6E7F3B", "10 4"),
    "Psi-minus": ("#B05A7A", "3 4"),
}
QUADRANTS = (
    "low_opening",
    "high_opening",
    "high_closing",
    "low_closing",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_protocol() -> str:
    expected = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    observed = digest(PROTOCOL)
    if expected != observed:
        raise RuntimeError(f"Q10 protocol mismatch: {observed} != {expected}")
    return observed


def time_weights(times: np.ndarray) -> np.ndarray:
    weights = np.empty_like(times)
    weights[0] = (times[1] - times[0]) / 2
    weights[-1] = (times[-1] - times[-2]) / 2
    weights[1:-1] = (times[2:] - times[:-2]) / 2
    return weights


def normalized_coordinates(values: np.ndarray, times: np.ndarray) -> dict[str, np.ndarray | float]:
    minimum = float(np.min(values))
    maximum = float(np.max(values))
    span = maximum - minimum
    if span <= 0:
        raise ValueError("Two-axis ARA requires a nonzero amplitude range")
    amplitude = 2 * (values - minimum) / span
    derivative = np.gradient(values, times, edge_order=2)
    rate_scale = float(np.max(np.abs(derivative)))
    if rate_scale <= 0:
        raise ValueError("Two-axis ARA requires a nonzero derivative range")
    rate = 1 - np.clip(derivative / rate_scale, -1, 1)
    relation = (amplitude - 1) + 1j * (rate - 1)
    return {
        "minimum": minimum,
        "maximum": maximum,
        "span": span,
        "derivative": derivative,
        "rate_scale": rate_scale,
        "amplitude": amplitude,
        "rate": rate,
        "relation_real": np.real(relation),
        "relation_imag": np.imag(relation),
        "relation_radius": np.abs(relation),
        "relation_theta_rad": np.angle(relation),
        "relation_theta_deg": np.degrees(np.angle(relation)),
    }


def quadrant(amplitude: float, rate: float) -> str:
    if amplitude < 1 and rate < 1:
        return "low_opening"
    if amplitude >= 1 and rate < 1:
        return "high_opening"
    if amplitude >= 1 and rate >= 1:
        return "high_closing"
    return "low_closing"


def sign_changes(values: np.ndarray, tolerance: float) -> int:
    signs = []
    for value in values:
        if value > tolerance:
            signs.append(1)
        elif value < -tolerance:
            signs.append(-1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def trajectory_geometry(
    condition: str,
    state: str,
    times: np.ndarray,
    coordinates: dict[str, np.ndarray | float],
) -> dict[str, object]:
    amplitude = np.asarray(coordinates["amplitude"], float)
    rate = np.asarray(coordinates["rate"], float)
    derivative = np.asarray(coordinates["derivative"], float)
    weights = time_weights(times)
    total_weight = float(np.sum(weights))
    labels = [quadrant(x, y) for x, y in zip(amplitude, rate)]
    shares = {
        label: float(
            2 * sum(weight for weight, observed in zip(weights, labels) if observed == label)
            / total_weight
        )
        for label in QUADRANTS
    }
    points = np.column_stack([amplitude, rate])
    path_length = float(np.sum(np.linalg.norm(np.diff(points, axis=0), axis=1)))
    closure_gap = float(np.linalg.norm(points[-1] - points[0]))
    x, y = points[:, 0], points[:, 1]
    signed_area = float(
        0.5
        * (
            np.dot(x, np.roll(y, -1))
            - np.dot(y, np.roll(x, -1))
        )
    )
    opening_share = float(
        sum(weight for weight, value in zip(weights, rate) if value < 1)
        / total_weight
    )
    closing_share = float(
        sum(weight for weight, value in zip(weights, rate) if value > 1)
        / total_weight
    )
    still_share = max(0.0, 1 - opening_share - closing_share)
    turns = sign_changes(
        derivative, tolerance=max(1e-15, float(coordinates["rate_scale"]) * 1e-12)
    )
    return {
        "condition": condition,
        "state": state,
        "h_min": coordinates["minimum"],
        "h_max": coordinates["maximum"],
        "h_range": coordinates["span"],
        "rate_scale_per_us": coordinates["rate_scale"],
        "amplitude_rate_correlation": float(np.corrcoef(amplitude, rate)[0, 1]),
        "path_length": path_length,
        "closure_gap": closure_gap,
        "chord_closed_signed_area": signed_area,
        "opening_time_share": opening_share,
        "closing_time_share": closing_share,
        "still_time_share": still_share,
        "derivative_sign_changes": turns,
        "low_opening_te": shares["low_opening"],
        "high_opening_te": shares["high_opening"],
        "high_closing_te": shares["high_closing"],
        "low_closing_te": shares["low_closing"],
        "quadrant_te_sum": sum(shares.values()),
        "closed_loop_candidate": bool(
            opening_share >= 0.15
            and closing_share >= 0.15
            and closure_gap <= 0.35
        ),
    }


def median_pairwise_correlation(
    series_by_state: dict[str, np.ndarray],
) -> tuple[float, dict[str, float]]:
    values = {}
    for left, right in combinations(STATES, 2):
        correlation = float(np.corrcoef(series_by_state[left], series_by_state[right])[0, 1])
        values[f"{left}/{right}"] = correlation
    return float(np.median(list(values.values()))), values


def add_gate(
    gates: list[dict[str, object]],
    gate_id: str,
    description: str,
    passed: bool,
    value: object,
) -> None:
    if isinstance(value, np.generic):
        value = value.item()
    elif isinstance(value, dict):
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


def build_svg(
    records_by: dict[str, dict[str, list[dict[str, object]]]],
    trajectories: list[dict[str, object]],
) -> None:
    width, height = 1500, 1160
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>"
        "text{font-family:Arial,sans-serif;fill:#20252B}"
        ".title{font-size:28px;font-weight:700}.panel{font-size:19px;font-weight:700}"
        ".sub{font-size:13px;fill:#56616B}.axis{font-size:13px;fill:#46515A}"
        ".tick{font-size:11px;fill:#68737D}.legend{font-size:12px}"
        "</style>",
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        '<text x="55" y="48" class="title">Unresolved H: amplitude and opening/closing relation</text>',
        '<text x="55" y="73" class="sub">Local 0–2 coordinates from eleven public Bell-state waits per trajectory</text>',
    ]

    def relation_panel(x: float, y: float, w: float, h: float, condition: str) -> None:
        px, py = x + 70, y + 100
        pw, ph = w - 105, h - 155

        def mx(value: float) -> float:
            return px + value / 2 * pw

        def my(value: float) -> float:
            return py + ph - value / 2 * ph

        parts.extend(
            [
                f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#FBFCFD" stroke="#DCE2E7"/>',
                f'<text x="{x+22}" y="{y+31}" class="panel">{condition} unresolved-H relation plane</text>',
                f'<text x="{x+22}" y="{y+53}" class="sub">Open circle = first wait; square = final wait; cross = two 1.0 ridges</text>',
            ]
        )
        for state_index, state in enumerate(STATES):
            color, dash = STATE_STYLE[state]
            lx = x + 25 + state_index * 150
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            parts.extend(
                [
                    f'<line x1="{lx}" y1="{y+75}" x2="{lx+18}" y2="{y+75}" stroke="{color}" stroke-width="3"{dash_attr}/>',
                    f'<text x="{lx+24}" y="{y+79}" class="legend">{state}</text>',
                ]
            )
        parts.extend(
            [
                f'<rect x="{mx(0)}" y="{my(1)}" width="{pw/2}" height="{ph/2}" fill="#2F6B9A" fill-opacity="0.035"/>',
                f'<rect x="{mx(1)}" y="{my(1)}" width="{pw/2}" height="{ph/2}" fill="#D7A33D" fill-opacity="0.045"/>',
                f'<rect x="{mx(1)}" y="{my(2)}" width="{pw/2}" height="{ph/2}" fill="#D7A33D" fill-opacity="0.025"/>',
                f'<rect x="{mx(0)}" y="{my(2)}" width="{pw/2}" height="{ph/2}" fill="#2F6B9A" fill-opacity="0.025"/>',
                f'<line x1="{mx(0)}" y1="{my(0)}" x2="{mx(2)}" y2="{my(0)}" stroke="#9EA8B0"/>',
                f'<line x1="{mx(0)}" y1="{my(0)}" x2="{mx(0)}" y2="{my(2)}" stroke="#9EA8B0"/>',
                f'<line x1="{mx(1)}" y1="{my(0)}" x2="{mx(1)}" y2="{my(2)}" stroke="#606B74" stroke-width="1.4"/>',
                f'<line x1="{mx(0)}" y1="{my(1)}" x2="{mx(2)}" y2="{my(1)}" stroke="#606B74" stroke-width="1.4"/>',
                f'<text x="{mx(0)+8}" y="{my(0.12)}" class="tick">low / opening</text>',
                f'<text x="{mx(1)+8}" y="{my(0.12)}" class="tick">high / opening</text>',
                f'<text x="{mx(1)+8}" y="{my(1.88)}" class="tick">high / closing</text>',
                f'<text x="{mx(0)+8}" y="{my(1.88)}" class="tick">low / closing</text>',
            ]
        )
        for value in (0, 1, 2):
            parts.extend(
                [
                    f'<text x="{mx(value)-4}" y="{my(0)+19}" class="tick">{value}</text>',
                    f'<text x="{mx(0)-22}" y="{my(value)+4}" class="tick">{value}</text>',
                ]
            )
        for state in STATES:
            color, dash = STATE_STYLE[state]
            rows = records_by[condition][state]
            points = [(mx(float(row["amplitude_x"])), my(float(row["rate_y"]))) for row in rows]
            point_text = " ".join(f"{xx:.2f},{yy:.2f}" for xx, yy in points)
            dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
            parts.append(
                f'<polyline points="{point_text}" fill="none" stroke="{color}" stroke-width="2.5"{dash_attr}/>'
            )
            for index, (xx, yy) in enumerate(points):
                if index == 0:
                    parts.append(
                        f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="6" fill="#FFFFFF" stroke="{color}" stroke-width="2"/>'
                    )
                elif index == len(points) - 1:
                    parts.append(
                        f'<rect x="{xx-5:.2f}" y="{yy-5:.2f}" width="10" height="10" fill="{color}" stroke="#FFFFFF"/>'
                    )
                else:
                    parts.append(
                        f'<circle cx="{xx:.2f}" cy="{yy:.2f}" r="3.3" fill="{color}"/>'
                    )
        parts.extend(
            [
                f'<text x="{px+pw/2-70}" y="{y+h-18}" class="axis">amplitude: nothing → maximum</text>',
                f'<text x="{x+18}" y="{py+ph/2}" class="axis" transform="rotate(-90 {x+18} {py+ph/2})">opening → closing</text>',
            ]
        )

    relation_panel(50, 92, 685, 510, "Ramsey")
    relation_panel(765, 92, 685, 510, "Hahn")

    x, y, w, h = 50, 635, 1400, 470
    parts.extend(
        [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#FBFCFD" stroke="#DCE2E7"/>',
            f'<text x="{x+22}" y="{y+32}" class="panel">Time-weighted TE-ARA composition of each unresolved-H path</text>',
            f'<text x="{x+22}" y="{y+54}" class="sub">Each row sums to 2; composition describes geometry, not named physical causes</text>',
        ]
    )
    bar_x, bar_w = x + 235, w - 285
    row_y = y + 92
    colors = {
        "low_opening_te": "#8FB4D2",
        "high_opening_te": "#D9B35C",
        "high_closing_te": "#C98B2E",
        "low_closing_te": "#487FA9",
    }
    legend_labels = {
        "low_opening_te": "low/opening",
        "high_opening_te": "high/opening",
        "high_closing_te": "high/closing",
        "low_closing_te": "low/closing",
    }
    lx = x + 650
    for key in colors:
        parts.extend(
            [
                f'<rect x="{lx}" y="{y+28}" width="14" height="14" fill="{colors[key]}" stroke="#7C8790"/>',
                f'<text x="{lx+20}" y="{y+40}" class="legend">{legend_labels[key]}</text>',
            ]
        )
        lx += 155
    trajectory_map = {(row["condition"], row["state"]): row for row in trajectories}
    for condition_index, condition in enumerate(CONDITIONS):
        for state_index, state in enumerate(STATES):
            yy = row_y + (condition_index * 4 + state_index) * 42
            row = trajectory_map[(condition, state)]
            parts.append(
                f'<text x="{x+24}" y="{yy+14}" class="axis">{condition} · {state}</text>'
            )
            cursor = bar_x
            for key in colors:
                value = float(row[key])
                segment = bar_w * value / 2
                parts.append(
                    f'<rect x="{cursor:.2f}" y="{yy}" width="{segment:.2f}" height="20" fill="{colors[key]}" stroke="#FFFFFF"/>'
                )
                if segment >= 45:
                    parts.append(
                        f'<text x="{cursor+segment/2-14:.2f}" y="{yy+14}" class="tick">{value:.2f}</text>'
                    )
                cursor += segment
            parts.append(
                f'<text x="{bar_x+bar_w+8}" y="{yy+14}" class="tick">gap {float(row["closure_gap"]):.2f}</text>'
            )
    parts.append("</svg>")
    FIGURE_SVG.write_text("\n".join(parts), encoding="utf-8")


def run() -> dict[str, object]:
    protocol_hash = verify_protocol()
    with INPUT.open(newline="", encoding="utf-8") as handle:
        source = list(csv.DictReader(handle))
    key_count = len(
        {(row["condition"], row["state"], int(row["wait_index"])) for row in source}
    )
    by_key = {}
    for condition in CONDITIONS:
        for state in STATES:
            by_key[(condition, state)] = sorted(
                [
                    row
                    for row in source
                    if row["condition"] == condition and row["state"] == state
                ],
                key=lambda item: int(item["wait_index"]),
            )

    records: list[dict[str, object]] = []
    records_by: dict[str, dict[str, list[dict[str, object]]]] = {
        condition: {} for condition in CONDITIONS
    }
    trajectories: list[dict[str, object]] = []
    inverse_errors: list[float] = []
    relation_errors: list[float] = []
    robustness_distances: list[float] = []
    data_quality_ok = key_count == 88
    bounds_ok = True
    variance_ok = True

    coordinate_cache: dict[tuple[str, str], dict[str, np.ndarray | float]] = {}
    for condition in CONDITIONS:
        for state in STATES:
            rows = by_key[(condition, state)]
            times = np.asarray([float(row["wait_us"]) for row in rows])
            h = np.asarray([float(row["q8_h_linear"]) for row in rows])
            h_purity = np.asarray(
                [float(row["i_unresolved_half_scale"]) for row in rows]
            )
            data_quality_ok &= (
                len(rows) == 11
                and len(np.unique(times)) == 11
                and np.all(np.diff(times) > 0)
                and np.ptp(h) > 0
                and np.ptp(h_purity) > 0
            )
            primary = normalized_coordinates(h, times)
            robustness = normalized_coordinates(h_purity, times)
            coordinate_cache[(condition, state)] = primary
            geometry = trajectory_geometry(condition, state, times, primary)
            trajectories.append(geometry)
            series_records = []
            for index, (source_row, time_us) in enumerate(zip(rows, times)):
                x = float(np.asarray(primary["amplitude"])[index])
                y = float(np.asarray(primary["rate"])[index])
                relation_real = float(np.asarray(primary["relation_real"])[index])
                relation_imag = float(np.asarray(primary["relation_imag"])[index])
                radius = float(np.asarray(primary["relation_radius"])[index])
                theta_rad = float(np.asarray(primary["relation_theta_rad"])[index])
                x_p = float(np.asarray(robustness["amplitude"])[index])
                y_p = float(np.asarray(robustness["rate"])[index])
                h_reconstructed = float(primary["minimum"]) + x / 2 * float(
                    primary["span"]
                )
                inverse_errors.append(abs(h_reconstructed - h[index]))
                c_reconstructed = radius * complex(
                    math.cos(theta_rad), math.sin(theta_rad)
                )
                relation_errors.extend(
                    [
                        abs(c_reconstructed.real - relation_real),
                        abs(c_reconstructed.imag - relation_imag),
                        abs((relation_real + 1) - x),
                        abs((relation_imag + 1) - y),
                    ]
                )
                robustness_distances.append(math.hypot(x - x_p, y - y_p))
                bounds_ok &= (
                    -1e-12 <= x <= 2 + 1e-12
                    and -1e-12 <= y <= 2 + 1e-12
                    and math.isfinite(x)
                    and math.isfinite(y)
                )
                record = {
                    "condition": condition,
                    "state": state,
                    "wait_index": int(source_row["wait_index"]),
                    "wait_us": float(time_us),
                    "h_linear": float(h[index]),
                    "h_purity_half_scale": float(h_purity[index]),
                    "h_local_min": primary["minimum"],
                    "h_local_max": primary["maximum"],
                    "h_local_range": primary["span"],
                    "h_derivative_per_us": float(
                        np.asarray(primary["derivative"])[index]
                    ),
                    "h_rate_scale_per_us": primary["rate_scale"],
                    "amplitude_x": x,
                    "rate_y": y,
                    "relation_real": relation_real,
                    "relation_imag": relation_imag,
                    "relation_radius": radius,
                    "relation_theta_rad": theta_rad,
                    "relation_theta_deg": float(
                        np.asarray(primary["relation_theta_deg"])[index]
                    ),
                    "quadrant": quadrant(x, y),
                    "purity_amplitude_x": x_p,
                    "purity_rate_y": y_p,
                    "two_definition_distance": math.hypot(x - x_p, y - y_p),
                }
                records.append(record)
                series_records.append(record)
            records_by[condition][state] = series_records
            variance_ok &= (
                np.var(np.asarray(primary["amplitude"], float)) > 0
                and np.var(np.asarray(primary["rate"], float)) > 0
            )

    amplitude_correlations = {}
    rate_correlations = {}
    pairwise_details = {}
    for condition in CONDITIONS:
        amplitude_median, amplitude_pairs = median_pairwise_correlation(
            {
                state: np.asarray(coordinate_cache[(condition, state)]["amplitude"], float)
                for state in STATES
            }
        )
        rate_median, rate_pairs = median_pairwise_correlation(
            {
                state: np.asarray(coordinate_cache[(condition, state)]["rate"], float)
                for state in STATES
            }
        )
        amplitude_correlations[condition] = amplitude_median
        rate_correlations[condition] = rate_median
        pairwise_details[condition] = {
            "amplitude": amplitude_pairs,
            "rate": rate_pairs,
        }

    gates: list[dict[str, object]] = []
    add_gate(
        gates,
        "U1",
        "88 unique rows form eight valid eleven-point nonzero-range trajectories",
        data_quality_ok,
        data_quality_ok,
    )
    add_gate(
        gates,
        "U2",
        "all amplitude and rate coordinates are finite and inside 0-2",
        bounds_ok,
        bounds_ok,
    )
    add_gate(
        gates,
        "U3",
        "inverse amplitude reconstruction maximum error <= 1e-12",
        max(inverse_errors) <= 1e-12,
        max(inverse_errors),
    )
    add_gate(
        gates,
        "U4",
        "relation radius/angle and centred axes reconstruct within 1e-12",
        max(relation_errors) <= 1e-12,
        max(relation_errors),
    )
    quadrant_sums = {
        f"{row['condition']}/{row['state']}": float(row["quadrant_te_sum"])
        for row in trajectories
    }
    add_gate(
        gates,
        "U5",
        "every quadrant TE composition sums to 2 within 1e-12",
        all(abs(value - 2) <= 1e-12 for value in quadrant_sums.values()),
        quadrant_sums,
    )
    add_gate(
        gates,
        "U6",
        "both axes have nonzero variance in every trajectory",
        variance_ok,
        variance_ok,
    )
    add_gate(
        gates,
        "U7",
        "median cross-state amplitude-axis correlation >= 0.80 in both conditions",
        all(value >= 0.80 for value in amplitude_correlations.values()),
        amplitude_correlations,
    )
    add_gate(
        gates,
        "U8",
        "median cross-state rate-axis correlation >= 0.40 in both conditions",
        all(value >= 0.40 for value in rate_correlations.values()),
        rate_correlations,
    )
    robustness_median = float(np.median(robustness_distances))
    add_gate(
        gates,
        "U9",
        "median two-axis distance using purity-defined H <= 0.25",
        robustness_median <= 0.25,
        robustness_median,
    )

    closed_candidates = [
        f"{row['condition']}/{row['state']}"
        for row in trajectories
        if bool(row["closed_loop_candidate"])
    ]
    result = {
        "test_id": "Q10-UNRESOLVED-TWO-AXIS-v1",
        "ledger_id": "T269",
        "test_class": "post-outcome geometry-first instrument calibration",
        "protocol_sha256": protocol_hash,
        "verdict": "CALIBRATED" if all(gate["passed"] for gate in gates) else "NOT CALIBRATED",
        "summary": {
            "records": len(records),
            "trajectories": len(trajectories),
            "amplitude_cross_state_median_correlations": amplitude_correlations,
            "rate_cross_state_median_correlations": rate_correlations,
            "median_two_definition_relation_plane_distance": robustness_median,
            "closed_loop_candidates": closed_candidates,
            "gates_passed": sum(bool(gate["passed"]) for gate in gates),
            "gates_total": len(gates),
        },
        "pairwise_correlations": pairwise_details,
        "trajectory_diagnostics": trajectories,
        "gates": gates,
        "interpretation_boundary": (
            "The instrument recovers a local amplitude/rate relation plane from sparse observed trajectories. "
            "It does not identify physical causes, establish a full cycle beyond the measured window, "
            "or make a forward prediction."
        ),
    }

    with RECORDS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    with TRAJECTORIES_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(trajectories[0]))
        writer.writeheader()
        writer.writerows(trajectories)
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
    build_svg(records_by, trajectories)
    return result


if __name__ == "__main__":
    output = run()
    print(json.dumps(output["summary"], indent=2))
    print(f"Verdict: {output['verdict']}")
