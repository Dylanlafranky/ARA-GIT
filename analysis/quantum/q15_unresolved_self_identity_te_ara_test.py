"""Q15: unresolved-component self-identity and conditional Phase-B handover.

This script implements the frozen post-outcome protocol:

Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_PROTOCOL_v1_FROZEN.md

Use the bundled workspace Python because NumPy and Matplotlib are required.
"""

from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_PROTOCOL_v1_FROZEN.md"
Q11 = HERE / "Q11_VISIBLE_UNRESOLVED_INFORMATION3_RECORDS.csv"
Q8 = HERE / "Q8_BELL_RELATION_PLANE_RECORDS.csv"

RESULTS = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_RESULTS.json"
IDENTITY_CSV = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA_METRICS.csv"
HANDOVER_CSV = HERE / "Q15_UNRESOLVED_PHASE_B_HANDOVER_RECORDS.csv"
FIGURE_SVG = HERE / "Q15_UNRESOLVED_SELF_IDENTITY_TE_ARA.svg"

CONDITIONS = ("Ramsey", "Hahn")
STATES = ("Phi-minus", "Phi-plus", "Psi-minus", "Psi-plus")
PERMUTATION_DRAWS = 9_999
SEED = 20_260_724
WAIT_RELATIVE_TOLERANCE = 0.02


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) < 2 or np.std(a) <= 1e-15 or np.std(b) <= 1e-15:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def energy_share(matrix: np.ndarray) -> tuple[float, float, float]:
    common = np.mean(matrix, axis=0)
    common_energy = float(matrix.shape[0] * np.sum(common**2))
    residual_energy = float(np.sum((matrix - common) ** 2))
    total = common_energy + residual_energy
    eta = common_energy / total if total > 0 else float("nan")
    return float(eta), common_energy, residual_energy


def pooled_loso_r2(matrix: np.ndarray) -> tuple[float, list[float]]:
    predictions = np.empty_like(matrix)
    per_state: list[float] = []
    for held_out in range(matrix.shape[0]):
        keep = [index for index in range(matrix.shape[0]) if index != held_out]
        predictions[held_out] = np.mean(matrix[keep], axis=0)
        actual = matrix[held_out]
        denominator = float(np.sum((actual - np.mean(actual)) ** 2))
        numerator = float(np.sum((actual - predictions[held_out]) ** 2))
        per_state.append(
            1.0 - numerator / denominator if denominator > 0 else float("nan")
        )

    denominator = float(np.sum((matrix - np.mean(matrix)) ** 2))
    numerator = float(np.sum((matrix - predictions) ** 2))
    pooled = 1.0 - numerator / denominator if denominator > 0 else float("nan")
    return float(pooled), [float(value) for value in per_state]


def identity_arrays(
    unresolved: np.ndarray, waits: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    change = unresolved - unresolved[:, [0]]
    rate = np.gradient(unresolved, waits, axis=1, edge_order=2)
    return change, rate


def identity_metrics(
    unresolved: np.ndarray, waits: np.ndarray
) -> dict[str, Any]:
    change, rate = identity_arrays(unresolved, waits)
    eta_change, common_change, residual_change = energy_share(change)
    eta_rate, common_rate, residual_rate = energy_share(rate)
    loso_change, state_loso_change = pooled_loso_r2(change)
    loso_rate, state_loso_rate = pooled_loso_r2(rate)
    eta_self = min(eta_change, eta_rate)
    return {
        "eta_change": eta_change,
        "eta_rate": eta_rate,
        "eta_self_conservative": eta_self,
        "te_ara_self": 2.0 * eta_self,
        "te_ara_other": 2.0 * (1.0 - eta_self),
        "te_ara_closure": 2.0,
        "common_change_energy": common_change,
        "other_change_energy": residual_change,
        "common_rate_energy": common_rate,
        "other_rate_energy": residual_rate,
        "loso_r2_change_pooled": loso_change,
        "loso_r2_rate_pooled": loso_rate,
        "loso_r2_change_by_state": dict(zip(STATES, state_loso_change)),
        "loso_r2_rate_by_state": dict(zip(STATES, state_loso_rate)),
    }


def permutation_identity_null(
    unresolved: np.ndarray,
    waits: np.ndarray,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    null_change = np.empty(PERMUTATION_DRAWS, dtype=float)
    null_rate = np.empty(PERMUTATION_DRAWS, dtype=float)
    null_self = np.empty(PERMUTATION_DRAWS, dtype=float)
    for draw in range(PERMUTATION_DRAWS):
        permuted = np.stack(
            [row[rng.permutation(len(row))] for row in unresolved],
            axis=0,
        )
        change, rate = identity_arrays(permuted, waits)
        null_change[draw] = energy_share(change)[0]
        null_rate[draw] = energy_share(rate)[0]
        null_self[draw] = min(null_change[draw], null_rate[draw])
    return null_change, null_rate, null_self


def p_greater_equal(null: np.ndarray, observed: float) -> float:
    return float((1 + np.count_nonzero(null >= observed)) / (len(null) + 1))


def quantiles(values: np.ndarray) -> dict[str, float]:
    points = np.quantile(values, [0.025, 0.25, 0.5, 0.75, 0.975])
    return {
        "q2_5": float(points[0]),
        "q25": float(points[1]),
        "median": float(points[2]),
        "q75": float(points[3]),
        "q97_5": float(points[4]),
    }


def build_condition_arrays(
    rows: list[dict[str, str]], value_field: str
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = {
        condition: {state: [] for state in STATES} for condition in CONDITIONS
    }
    for row in rows:
        if row["condition"] in grouped and row["state"] in grouped[row["condition"]]:
            grouped[row["condition"]][row["state"]].append(row)

    result: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for condition in CONDITIONS:
        state_values: list[np.ndarray] = []
        reference_waits: np.ndarray | None = None
        for state in STATES:
            ordered = sorted(
                grouped[condition][state], key=lambda row: int(row["wait_index"])
            )
            waits = np.asarray([float(row["wait_us"]) for row in ordered])
            values = np.asarray([float(row[value_field]) for row in ordered])
            if reference_waits is None:
                reference_waits = waits
            elif not np.allclose(waits, reference_waits, rtol=0, atol=1e-12):
                raise ValueError(f"{condition} wait grid differs across Bell states")
            state_values.append(values)
        if reference_waits is None:
            raise ValueError(f"No rows for {condition}")
        result[condition] = (reference_waits, np.stack(state_values, axis=0))
    return result


def cross_definition_correlations(
    q11_rows: list[dict[str, str]], q8_rows: list[dict[str, str]]
) -> dict[str, float]:
    q8_index = {
        (row["condition"], row["state"], int(row["wait_index"])): float(
            row["hidden_residual"]
        )
        for row in q8_rows
    }
    result: dict[str, float] = {}
    for condition in CONDITIONS:
        purity: list[float] = []
        algebraic: list[float] = []
        for row in q11_rows:
            if row["condition"] != condition:
                continue
            key = (condition, row["state"], int(row["wait_index"]))
            purity.append(float(row["target_purity_loss"]))
            algebraic.append(q8_index[key])
        result[condition] = pearson(np.asarray(purity), np.asarray(algebraic))
    return result


def matched_handover_records(
    q11_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, list[dict[str, str]]]] = {
        condition: {state: [] for state in STATES} for condition in CONDITIONS
    }
    for row in q11_rows:
        grouped[row["condition"]][row["state"]].append(row)

    records: list[dict[str, Any]] = []
    for state in STATES:
        ramsey_rows = sorted(
            grouped["Ramsey"][state], key=lambda row: float(row["wait_us"])
        )
        hahn_rows = sorted(
            grouped["Hahn"][state], key=lambda row: float(row["wait_us"])
        )
        for ramsey in ramsey_rows:
            ramsey_wait = float(ramsey["wait_us"])
            hahn = min(
                hahn_rows,
                key=lambda row: abs(float(row["wait_us"]) - ramsey_wait),
            )
            hahn_wait = float(hahn["wait_us"])
            relative_gap = abs(hahn_wait - ramsey_wait) / (
                (hahn_wait + ramsey_wait) / 2
            )
            if relative_gap <= WAIT_RELATIVE_TOLERANCE:
                delta_u = float(ramsey["target_purity_loss"]) - float(
                    hahn["target_purity_loss"]
                )
                delta_visible = float(hahn["visible_value"]) - float(
                    ramsey["visible_value"]
                )
                records.append(
                    {
                        "state": state,
                        "ramsey_wait_index": int(ramsey["wait_index"]),
                        "hahn_wait_index": int(hahn["wait_index"]),
                        "ramsey_wait_us": ramsey_wait,
                        "hahn_wait_us": hahn_wait,
                        "relative_wait_gap": relative_gap,
                        "ramsey_unresolved": float(
                            ramsey["target_purity_loss"]
                        ),
                        "hahn_unresolved": float(hahn["target_purity_loss"]),
                        "ramsey_visible": float(ramsey["visible_value"]),
                        "hahn_visible": float(hahn["visible_value"]),
                        "delta_unresolved": delta_u,
                        "delta_visible": delta_visible,
                        "same_sign": bool(
                            np.sign(delta_u) == np.sign(delta_visible)
                        ),
                        "apparent_refocusable_share": (
                            delta_u / float(ramsey["target_purity_loss"])
                            if float(ramsey["target_purity_loss"]) > 1e-12
                            else float("nan")
                        ),
                    }
                )
    return records


def handover_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    delta_u = np.asarray([row["delta_unresolved"] for row in records])
    delta_visible = np.asarray([row["delta_visible"] for row in records])
    shares = np.asarray(
        [
            row["apparent_refocusable_share"]
            for row in records
            if row["delta_unresolved"] > 0
        ]
    )
    return {
        "matched_records": len(records),
        "sign_agreement_fraction": float(
            np.mean(
                [
                    np.sign(row["delta_unresolved"])
                    == np.sign(row["delta_visible"])
                    for row in records
                ]
            )
        ),
        "positive_delta_unresolved_count": int(
            np.count_nonzero(delta_u > 0)
        ),
        "positive_delta_visible_count": int(
            np.count_nonzero(delta_visible > 0)
        ),
        "delta_correlation": pearson(delta_u, delta_visible),
        "through_origin_slope": float(
            np.dot(delta_u, delta_visible) / np.dot(delta_u, delta_u)
        ),
        "mae_from_unit_handover": float(
            np.mean(np.abs(delta_visible - delta_u))
        ),
        "median_positive_apparent_refocusable_share": float(
            np.median(shares)
        ),
    }


def handover_rematching_null(
    records: list[dict[str, Any]], rng: np.random.Generator
) -> np.ndarray:
    by_state: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_state[row["state"]].append(row)

    null_correlations = np.empty(PERMUTATION_DRAWS, dtype=float)
    for draw in range(PERMUTATION_DRAWS):
        delta_u: list[float] = []
        delta_visible: list[float] = []
        for state in STATES:
            state_rows = sorted(
                by_state[state], key=lambda row: row["ramsey_wait_us"]
            )
            permutation = rng.permutation(len(state_rows))
            for ramsey_row, hahn_index in zip(state_rows, permutation):
                hahn_row = state_rows[int(hahn_index)]
                delta_u.append(
                    ramsey_row["ramsey_unresolved"]
                    - hahn_row["hahn_unresolved"]
                )
                delta_visible.append(
                    hahn_row["hahn_visible"] - ramsey_row["ramsey_visible"]
                )
        null_correlations[draw] = pearson(
            np.asarray(delta_u), np.asarray(delta_visible)
        )
    return null_correlations


def classifications(
    metrics: dict[str, dict[str, Any]],
    cross_correlations: dict[str, float],
    handover: dict[str, Any],
) -> dict[str, Any]:
    dominant_by_condition: dict[str, bool] = {}
    mixed_by_condition: dict[str, bool] = {}
    for condition in CONDITIONS:
        row = metrics[condition]
        dominant_by_condition[condition] = bool(
            row["eta_change"] >= 0.80
            and row["eta_rate"] >= 0.80
            and row["eta_self_conservative"] >= 0.80
            and row["loso_r2_change_pooled"] >= 0.75
            and row["loso_r2_rate_pooled"] >= 0.50
            and row["permutation_p_self"] <= 0.01
            and cross_correlations[condition] >= 0.95
        )
        mixed_by_condition[condition] = bool(
            row["eta_change"] >= 0.60
            and row["eta_rate"] >= 0.60
            and row["eta_self_conservative"] >= 0.60
            and row["loso_r2_change_pooled"] > 0
            and row["loso_r2_rate_pooled"] > 0
            and row["permutation_p_self"] <= 0.05
            and cross_correlations[condition] >= 0.90
        )

    dominant = all(dominant_by_condition.values())
    mixed = all(mixed_by_condition.values())
    handover_pass = bool(
        handover["matched_records"] >= 16
        and handover["sign_agreement_fraction"] >= 0.75
        and handover["delta_correlation"] >= 0.80
        and 0.5 <= handover["through_origin_slope"] <= 1.5
        and handover["mae_from_unit_handover"] <= 0.20
        and handover["rematching_permutation_p_correlation"] <= 0.05
    )

    if dominant and handover_pass:
        verdict = "POST_OUTCOME_CALIBRATED_PHASE_B_CROSSWALK"
    elif dominant:
        verdict = "DOMINANT_IDENTITY_HANDOVER_NOT_DISTINGUISHED"
    elif mixed:
        verdict = "COHERENT_BUT_MIXED_PHASE_B_NOT_PROMOTED"
    else:
        verdict = "UNRESOLVED_COMPONENT_PHASE_B_NOT_PROMOTED"

    return {
        "dominant_by_condition": dominant_by_condition,
        "mixed_by_condition": mixed_by_condition,
        "dominant_coherent_identity_gate": dominant,
        "coherent_but_mixed_gate": mixed,
        "conditional_handover_gate": handover_pass,
        "verdict": verdict,
    }


def write_identity_csv(
    metrics: dict[str, dict[str, Any]],
    q8_metrics: dict[str, dict[str, Any]],
    cross_correlations: dict[str, float],
) -> None:
    fields = [
        "definition",
        "condition",
        "eta_change",
        "eta_rate",
        "eta_self_conservative",
        "te_ara_self",
        "te_ara_other",
        "loso_r2_change_pooled",
        "loso_r2_rate_pooled",
        "permutation_p_self",
        "cross_definition_correlation",
    ]
    with IDENTITY_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for definition, source in (
            ("purity_defined_primary", metrics),
            ("q8_algebraic_robustness", q8_metrics),
        ):
            for condition in CONDITIONS:
                row = source[condition]
                writer.writerow(
                    {
                        "definition": definition,
                        "condition": condition,
                        **{
                            field: row.get(field, "")
                            for field in fields
                            if field not in {"definition", "condition"}
                        },
                        "cross_definition_correlation": cross_correlations[
                            condition
                        ],
                    }
                )


def write_handover_csv(records: list[dict[str, Any]]) -> None:
    with HANDOVER_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def make_figure(
    primary_arrays: dict[str, tuple[np.ndarray, np.ndarray]],
    metrics: dict[str, dict[str, Any]],
    handover_records: list[dict[str, Any]],
) -> None:
    def polyline(
        points: list[tuple[float, float]],
        color: str,
        width: float,
        opacity: float = 1.0,
    ) -> str:
        joined = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        return (
            f'<polyline points="{joined}" fill="none" stroke="{color}" '
            f'stroke-width="{width}" opacity="{opacity}" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
        )

    def scaled_points(
        x_values: np.ndarray,
        y_values: np.ndarray,
        x: float,
        y: float,
        width: float,
        height: float,
        y_min: float,
        y_max: float,
    ) -> list[tuple[float, float]]:
        x_span = max(float(np.max(x_values) - np.min(x_values)), 1e-12)
        y_span = max(y_max - y_min, 1e-12)
        return [
            (
                x + width * (float(xv) - float(np.min(x_values))) / x_span,
                y + height * (1 - (float(yv) - y_min) / y_span),
            )
            for xv, yv in zip(x_values, y_values)
        ]

    state_colors = {
        "Phi-minus": "#9F4A75",
        "Phi-plus": "#2C6EAD",
        "Psi-minus": "#D17A00",
        "Psi-plus": "#6B7D2A",
    }
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900" '
        'viewBox="0 0 1400 900">',
        "<style>",
        ".title{font:700 26px system-ui,sans-serif;fill:#17202A}",
        ".head{font:700 17px system-ui,sans-serif;fill:#17202A}",
        ".text{font:13px system-ui,sans-serif;fill:#34495E}",
        ".small{font:11px system-ui,sans-serif;fill:#566573}",
        ".axis{stroke:#5D6D7E;stroke-width:1}",
        ".grid{stroke:#D5DBDB;stroke-width:1}",
        ".panel{fill:#F8F9F9;stroke:#D5DBDB;stroke-width:1.5}",
        "</style>",
        '<rect width="1400" height="900" fill="#FFFFFF"/>',
        '<text x="45" y="46" class="title">Q15 unresolved component: '
        "self-identity before Phase-B naming</text>",
        '<text x="45" y="72" class="text">Common trajectory versus state-specific '
        "Other, followed by the conditional Ramsey/Hahn handover check.</text>",
    ]

    for column, condition in enumerate(CONDITIONS):
        waits, values = primary_arrays[condition]
        changes = values - values[:, [0]]
        panel_x = 45 + column * 675
        panel_y = 100
        panel_w = 635
        panel_h = 335
        plot_x = panel_x + 58
        plot_y = panel_y + 62
        plot_w = panel_w - 85
        plot_h = panel_h - 105
        y_min = float(np.min(changes))
        y_max = float(np.max(changes))
        padding = max((y_max - y_min) * 0.08, 1e-5)
        y_min -= padding
        y_max += padding

        parts.extend(
            [
                f'<rect x="{panel_x}" y="{panel_y}" width="{panel_w}" '
                f'height="{panel_h}" rx="10" class="panel"/>',
                f'<text x="{panel_x+22}" y="{panel_y+31}" class="head">'
                f"{condition}: baseline-subtracted unresolved trajectory</text>",
                f'<line x1="{plot_x}" y1="{plot_y+plot_h}" x2="{plot_x+plot_w}" '
                f'y2="{plot_y+plot_h}" class="axis"/>',
                f'<line x1="{plot_x}" y1="{plot_y}" x2="{plot_x}" '
                f'y2="{plot_y+plot_h}" class="axis"/>',
            ]
        )
        for fraction in (0.25, 0.5, 0.75):
            grid_y = plot_y + plot_h * fraction
            parts.append(
                f'<line x1="{plot_x}" y1="{grid_y}" x2="{plot_x+plot_w}" '
                f'y2="{grid_y}" class="grid"/>'
            )

        for index, state in enumerate(STATES):
            parts.append(
                polyline(
                    scaled_points(
                        waits,
                        changes[index],
                        plot_x,
                        plot_y,
                        plot_w,
                        plot_h,
                        y_min,
                        y_max,
                    ),
                    state_colors[state],
                    2.0,
                    0.72,
                )
            )
        parts.append(
            polyline(
                scaled_points(
                    waits,
                    np.mean(changes, axis=0),
                    plot_x,
                    plot_y,
                    plot_w,
                    plot_h,
                    y_min,
                    y_max,
                ),
                "#111111",
                4.0,
            )
        )
        parts.extend(
            [
                f'<text x="{plot_x}" y="{plot_y+plot_h+25}" class="small">'
                f"{float(np.min(waits)):.2f} µs</text>",
                f'<text x="{plot_x+plot_w-48}" y="{plot_y+plot_h+25}" '
                f'class="small">{float(np.max(waits)):.2f} µs</text>',
                f'<text x="{plot_x-48}" y="{plot_y+7}" class="small">'
                f"{y_max:.3f}</text>",
                f'<text x="{plot_x-48}" y="{plot_y+plot_h}" class="small">'
                f"{y_min:.3f}</text>",
            ]
        )

        bar_x = panel_x + 25
        bar_y = 505
        bar_w = 600
        bar_h = 68
        eta = metrics[condition]["eta_self_conservative"]
        self_width = bar_w * eta
        parts.extend(
            [
                f'<text x="{bar_x}" y="{bar_y-24}" class="head">{condition} '
                f"TE-ARA participation account</text>",
                f'<rect x="{bar_x}" y="{bar_y}" width="{bar_w}" '
                f'height="{bar_h}" rx="6" fill="#C7CED6"/>',
                f'<rect x="{bar_x}" y="{bar_y}" width="{self_width}" '
                f'height="{bar_h}" rx="6" fill="#4B78A8"/>',
                f'<line x1="{bar_x+bar_w/2}" y1="{bar_y-6}" '
                f'x2="{bar_x+bar_w/2}" y2="{bar_y+bar_h+6}" '
                'stroke="#17202A" stroke-width="1" opacity="0.6"/>',
                f'<text x="{bar_x+10}" y="{bar_y+41}" fill="#FFFFFF" '
                f'font-family="system-ui,sans-serif" font-size="15">'
                f"self {2*eta:.3f}</text>",
                f'<text x="{bar_x+bar_w-100}" y="{bar_y+41}" class="text">'
                f"Other {2*(1-eta):.3f}</text>",
                f'<text x="{bar_x}" y="{bar_y+98}" class="text">'
                f"ηΔ={metrics[condition]['eta_change']:.3f}; "
                f"ηrate={metrics[condition]['eta_rate']:.3f}; "
                f"conservative η={eta:.3f}</text>",
            ]
        )

    scatter_x = 720
    scatter_y = 660
    scatter_w = 610
    scatter_h = 170
    delta_u = np.asarray(
        [row["delta_unresolved"] for row in handover_records]
    )
    delta_visible = np.asarray(
        [row["delta_visible"] for row in handover_records]
    )
    low = float(min(np.min(delta_u), np.min(delta_visible)))
    high = float(max(np.max(delta_u), np.max(delta_visible)))
    span = max(high - low, 1e-12)
    map_x = lambda value: scatter_x + scatter_w * (value - low) / span
    map_y = lambda value: scatter_y + scatter_h * (1 - (value - low) / span)
    parts.extend(
        [
            f'<rect x="{scatter_x-35}" y="{scatter_y-42}" '
            f'width="{scatter_w+55}" height="{scatter_h+90}" rx="10" '
            'class="panel"/>',
            f'<text x="{scatter_x-15}" y="{scatter_y-12}" class="head">'
            "Conditional Ramsey/Hahn handover</text>",
            f'<line x1="{scatter_x}" y1="{scatter_y+scatter_h}" '
            f'x2="{scatter_x+scatter_w}" y2="{scatter_y+scatter_h}" '
            'class="axis"/>',
            f'<line x1="{scatter_x}" y1="{scatter_y}" '
            f'x2="{scatter_x}" y2="{scatter_y+scatter_h}" class="axis"/>',
            f'<line x1="{map_x(low)}" y1="{map_y(low)}" '
            f'x2="{map_x(high)}" y2="{map_y(high)}" '
            'stroke="#566573" stroke-width="1.5" stroke-dasharray="6 5"/>',
        ]
    )
    for u_value, visible_value in zip(delta_u, delta_visible):
        parts.append(
            f'<circle cx="{map_x(float(u_value))}" '
            f'cy="{map_y(float(visible_value))}" r="5" fill="#C66A1B"/>'
        )
    parts.extend(
        [
            f'<text x="{scatter_x+scatter_w/2-75}" '
            f'y="{scatter_y+scatter_h+37}" class="small">'
            "Ramsey−Hahn unresolved</text>",
            f'<text x="{scatter_x-20}" y="{scatter_y+scatter_h+18}" '
            f'class="small">{low:.3f}</text>',
            f'<text x="{scatter_x+scatter_w-30}" '
            f'y="{scatter_y+scatter_h+18}" class="small">{high:.3f}</text>',
            '<text x="45" y="680" class="head">Legend</text>',
        ]
    )
    legend_y = 710
    for index, state in enumerate(STATES):
        x = 45 + (index % 2) * 220
        y = legend_y + (index // 2) * 32
        parts.extend(
            [
                f'<line x1="{x}" y1="{y}" x2="{x+32}" y2="{y}" '
                f'stroke="{state_colors[state]}" stroke-width="4"/>',
                f'<text x="{x+42}" y="{y+5}" class="text">{state}</text>',
            ]
        )
    parts.extend(
        [
            '<line x1="45" y1="785" x2="77" y2="785" '
            'stroke="#111111" stroke-width="5"/>',
            '<text x="87" y="790" class="text">four-state common mode</text>',
            '<rect x="45" y="815" width="28" height="15" fill="#4B78A8"/>',
            '<text x="87" y="828" class="text">repeatable self-mode</text>',
            '<rect x="270" y="815" width="28" height="15" fill="#C7CED6"/>',
            '<text x="312" y="828" class="text">state-specific Other</text>',
            '<text x="45" y="875" class="small">The TE-ARA bar is a '
            "normalized participation account, not a claim of physical energy "
            "conservation.</text>",
            "</svg>",
        ]
    )
    FIGURE_SVG.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    q11_rows = read_csv(Q11)
    q8_rows = read_csv(Q8)
    primary_arrays = build_condition_arrays(
        q11_rows, "target_purity_loss"
    )
    q8_arrays = build_condition_arrays(q8_rows, "hidden_residual")
    rng = np.random.default_rng(SEED)

    metrics: dict[str, dict[str, Any]] = {}
    q8_metrics: dict[str, dict[str, Any]] = {}
    for condition in CONDITIONS:
        waits, values = primary_arrays[condition]
        row = identity_metrics(values, waits)
        null_change, null_rate, null_self = permutation_identity_null(
            values, waits, rng
        )
        row.update(
            {
                "permutation_draws": PERMUTATION_DRAWS,
                "permutation_seed": SEED,
                "permutation_p_change": p_greater_equal(
                    null_change, row["eta_change"]
                ),
                "permutation_p_rate": p_greater_equal(
                    null_rate, row["eta_rate"]
                ),
                "permutation_p_self": p_greater_equal(
                    null_self, row["eta_self_conservative"]
                ),
                "null_eta_change_quantiles": quantiles(null_change),
                "null_eta_rate_quantiles": quantiles(null_rate),
                "null_eta_self_quantiles": quantiles(null_self),
            }
        )
        metrics[condition] = row

        q8_waits, q8_values = q8_arrays[condition]
        q8_metrics[condition] = identity_metrics(q8_values, q8_waits)

    cross_correlations = cross_definition_correlations(q11_rows, q8_rows)
    handover_records = matched_handover_records(q11_rows)
    handover = handover_summary(handover_records)
    rematching_null = handover_rematching_null(handover_records, rng)
    handover.update(
        {
            "rematching_permutation_draws": PERMUTATION_DRAWS,
            "rematching_permutation_seed": SEED,
            "rematching_permutation_p_correlation": p_greater_equal(
                rematching_null, handover["delta_correlation"]
            ),
            "rematching_null_correlation_quantiles": quantiles(
                rematching_null
            ),
        }
    )

    classification = classifications(metrics, cross_correlations, handover)
    result = {
        "test": "Q15 unresolved self-identity TE-ARA and conditional handover",
        "protocol_status": "post-outcome calibration",
        "protocol_sha256": sha256(PROTOCOL),
        "source_sha256": {
            Q11.name: sha256(Q11),
            Q8.name: sha256(Q8),
        },
        "record_counts": {
            "q11": len(q11_rows),
            "q8": len(q8_rows),
            "per_condition": {
                condition: int(primary_arrays[condition][1].size)
                for condition in CONDITIONS
            },
        },
        "primary_definition": "P = 2(1 - Tr(rho^2))",
        "primary_identity_metrics": metrics,
        "q8_algebraic_robustness_metrics": q8_metrics,
        "cross_definition_correlations": cross_correlations,
        "conditional_handover": handover,
        "classification": classification,
        "claim_boundary": (
            "This test can calibrate an ARA Phase-B crosswalk. It does not "
            "discover a new quantum degree of freedom or establish causal "
            "transfer outside the measured system."
        ),
    }

    RESULTS.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_identity_csv(metrics, q8_metrics, cross_correlations)
    write_handover_csv(handover_records)
    make_figure(primary_arrays, metrics, handover_records)

    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
