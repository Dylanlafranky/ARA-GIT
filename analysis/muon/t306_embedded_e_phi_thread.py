#!/usr/bin/env python3
"""T306: frozen embedded 1/e <-> Phi ARA thread test."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

import t305_phi_temporal_carrier_fusion as t305


HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "T306_EMBEDDED_E_PHI_THREAD_RESULTS.json"
OUT_PREFIX = HERE / "T306_EMBEDDED_E_PHI_THREAD_PREFIX_RESULTS.csv"
OUT_HARMONIC = HERE / "T306_EMBEDDED_E_PHI_THREAD_HARMONIC_SUMMARY.csv"
OUT_COUPLING = HERE / "T306_EMBEDDED_E_PHI_THREAD_COUPLING_SWEEP.csv"
OUT_FIG = HERE / "T306_EMBEDDED_E_PHI_THREAD.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
E_INV = 1.0 / math.e
PHI_TIME = PHI - 1.0
ANTI_PHI = PHI ** -2
SQRT2M1 = math.sqrt(2.0) - 1.0
PI_M3 = math.pi - 3.0

PARENT_CENTRE = (PHI + E_INV) / 2.0
PARENT_RADIUS = (PHI - E_INV) / 2.0
PARENT_DIAMETER = PHI - E_INV
PARENT_DEFICIT = 2.0 - PHI - E_INV
PARENT_DELTA = PHI_TIME - E_INV
CHILD_DELTA = ANTI_PHI - E_INV

PREFIXES = np.arange(65, 257)
FAMILIES = ["beam7", "beam7_cycle23", "beam7_decay"]
COUPLINGS = np.linspace(0.0, 1.0, 21)

ALPHAS = {
    "phi_time": PHI_TIME,
    "anti_phi": ANTI_PHI,
    "one_over_e": E_INV,
    "sqrt2_minus_1": SQRT2M1,
    "pi_minus_3": PI_M3,
}

PAIRS = {
    "parent_phi_time_vs_e": ("phi_time", "one_over_e"),
    "child_anti_phi_vs_e": ("anti_phi", "one_over_e"),
    "control_phi_time_vs_sqrt2": ("phi_time", "sqrt2_minus_1"),
    "control_e_vs_sqrt2": ("one_over_e", "sqrt2_minus_1"),
    "control_phi_time_vs_pi3": ("phi_time", "pi_minus_3"),
    "control_e_vs_pi3": ("one_over_e", "pi_minus_3"),
    "control_sqrt2_vs_pi3": ("sqrt2_minus_1", "pi_minus_3"),
}


def embedded_parent_x(u: float) -> float:
    return E_INV + 0.5 * u * (PHI - E_INV)


def run_prefixes() -> tuple[pd.DataFrame, dict[tuple[str, int, str], np.ndarray]]:
    rows: list[dict] = []
    raw: dict[tuple[str, int, str], np.ndarray] = {}
    for candidate, alpha in ALPHAS.items():
        for n in PREFIXES:
            centres = t305.carrier_centres(alpha, int(n))
            intervals = t305.merged_intervals(centres, t305.WIDTH)
            row = {
                "candidate": candidate,
                "alpha": alpha,
                "n": int(n),
                "largest_gap": t305.largest_gap(centres),
                "circular_star_discrepancy": t305.circular_star_discrepancy(centres),
                "union_coverage": t305.union_length(intervals),
                "overlap_loss": max(
                    0.0, int(n) * t305.WIDTH - t305.union_length(intervals)
                ),
            }
            row["flat_mean"] = t305.union_length(intervals)
            for family in FAMILIES:
                values = t305.arrival_overlap(intervals, family)
                raw[(candidate, int(n), family)] = values
                row[f"{family}_mean"] = float(np.mean(values))
                row[f"{family}_p05"] = float(np.percentile(values, 5))
                row[f"{family}_min"] = float(np.min(values))
            rows.append(row)
    return pd.DataFrame(rows), raw


def linear_harmonic_fit(n: np.ndarray, y: np.ndarray, period: float) -> dict:
    x = n - np.mean(n)
    x0 = np.column_stack([np.ones_like(x), x])
    angle = 2.0 * math.pi * n / period
    x1 = np.column_stack([x0, np.sin(angle), np.cos(angle)])
    b0 = np.linalg.lstsq(x0, y, rcond=None)[0]
    b1 = np.linalg.lstsq(x1, y, rcond=None)[0]
    r0 = y - x0 @ b0
    r1 = y - x1 @ b1
    rss0 = float(np.sum(r0 * r0))
    rss1 = float(np.sum(r1 * r1))
    partial_r2 = 0.0 if rss0 <= 1e-30 else max(0.0, (rss0 - rss1) / rss0)
    amplitude = float(math.hypot(float(b1[-2]), float(b1[-1])))
    phase = float(math.atan2(float(b1[-1]), float(b1[-2])))
    return {
        "period": float(period),
        "partial_r2": partial_r2,
        "amplitude": amplitude,
        "phase_rad": phase,
        "rss_baseline": rss0,
        "rss_full": rss1,
    }


def scan_dominant_period(n: np.ndarray, y: np.ndarray) -> dict:
    periods = np.linspace(4.0, 128.0, 497)
    fits = [linear_harmonic_fit(n, y, float(period)) for period in periods]
    return max(fits, key=lambda item: item["partial_r2"])


def harmonic_summary(frame: pd.DataFrame) -> pd.DataFrame:
    indexed = frame.set_index(["candidate", "n"])
    rows: list[dict] = []
    n = PREFIXES.astype(float)
    for pair_name, (left, right) in PAIRS.items():
        for family in FAMILIES:
            yl = np.array(
                [indexed.loc[(left, int(k)), f"{family}_p05"] for k in PREFIXES],
                dtype=float,
            )
            yr = np.array(
                [indexed.loc[(right, int(k)), f"{family}_p05"] for k in PREFIXES],
                dtype=float,
            )
            contrast = yl - yr
            p4 = linear_harmonic_fit(n, contrast, 4.0)
            dominant = scan_dominant_period(n, contrast)
            rows.append(
                {
                    "pair": pair_name,
                    "left": left,
                    "right": right,
                    "family": family,
                    "contrast_mean": float(np.mean(contrast)),
                    "contrast_std": float(np.std(contrast)),
                    "period4_partial_r2": p4["partial_r2"],
                    "period4_amplitude": p4["amplitude"],
                    "period4_phase_rad": p4["phase_rad"],
                    "dominant_period": dominant["period"],
                    "dominant_partial_r2": dominant["partial_r2"],
                    "dominant_amplitude": dominant["amplitude"],
                }
            )
    return pd.DataFrame(rows)


def coupling_sweep(
    raw: dict[tuple[str, int, str], np.ndarray],
) -> tuple[pd.DataFrame, dict]:
    rows: list[dict] = []
    switched: list[int] = []
    for n in PREFIXES:
        contrasts = []
        for coupling in COUPLINGS:
            endpoint_values = {}
            for candidate in ["phi_time", "one_over_e"]:
                decay = raw[(candidate, int(n), "beam7_decay")]
                complex_flow = raw[(candidate, int(n), "beam7_cycle23")]
                mixed = (1.0 - coupling) * decay + coupling * complex_flow
                endpoint_values[candidate] = float(np.percentile(mixed, 5))
            contrast = endpoint_values["phi_time"] - endpoint_values["one_over_e"]
            contrasts.append(contrast)
            rows.append(
                {
                    "n": int(n),
                    "coupling": float(coupling),
                    "phi_time_p05": endpoint_values["phi_time"],
                    "one_over_e_p05": endpoint_values["one_over_e"],
                    "contrast_phi_minus_e": contrast,
                    "winner": (
                        "phi_time"
                        if contrast > 1e-12
                        else "one_over_e"
                        if contrast < -1e-12
                        else "tie"
                    ),
                }
            )
        if min(contrasts) < -1e-12 and max(contrasts) > 1e-12:
            switched.append(int(n))
    output = pd.DataFrame(rows)
    stats = {
        "fresh_prefixes": int(len(PREFIXES)),
        "switch_count": int(len(switched)),
        "switch_fraction": float(len(switched) / len(PREFIXES)),
        "switch_prefixes": switched,
        "gate_threshold": 0.20,
        "pass": bool(len(switched) / len(PREFIXES) >= 0.20),
    }
    return output, stats


def dense_numeric(candidate: str, n: int, family: str, phase: float) -> dict:
    alpha = ALPHAS[candidate]
    intervals = t305.merged_intervals(
        t305.carrier_centres(alpha, n), t305.WIDTH
    )
    analytic = float(
        t305.arrival_overlap(intervals, family, np.array([phase]))[0]
    )
    m = 400_000
    t = (np.arange(m) + 0.5) / m
    cover = np.zeros(m, dtype=bool)
    for lo, hi in intervals:
        cover |= (t >= lo) & (t < hi)
    if family == "beam7_decay":
        g = np.exp(-t / 0.45) * (
            1.0 + 0.85 * np.cos(2.0 * math.pi * 7.0 * t + phase)
        )
    elif family == "beam7_cycle23":
        d = 0.6
        g = (
            1.0
            + d * np.cos(2.0 * math.pi * 7.0 * t + phase)
            + d * np.cos(2.0 * math.pi * 23.0 * t + 1.7 * phase)
            + 0.5 * d * d
            * np.cos(2.0 * math.pi * 16.0 * t - 0.7 * phase)
            + 0.5 * d * d
            * np.cos(2.0 * math.pi * 30.0 * t + 2.7 * phase)
        )
    else:
        raise KeyError(family)
    numeric = float(np.mean(g * cover) / np.mean(g))
    return {
        "candidate": candidate,
        "n": n,
        "family": family,
        "phase": phase,
        "analytic": analytic,
        "dense_numeric": numeric,
        "absolute_error": abs(analytic - numeric),
        "pass": bool(abs(analytic - numeric) <= 5e-4),
    }


def evaluate(
    prefix: pd.DataFrame,
    harmonic: pd.DataFrame,
    coupling_stats: dict,
) -> dict:
    pair_means = (
        harmonic.groupby("pair", sort=False)["period4_partial_r2"]
        .mean()
        .sort_values(ascending=False)
    )
    parent = float(pair_means["parent_phi_time_vs_e"])
    child = float(pair_means["child_anti_phi_vs_e"])
    g1_winner = str(pair_means.index[0])
    g1 = g1_winner == "parent_phi_time_vs_e"

    med_periods = harmonic.groupby("pair")["dominant_period"].median()
    parent_period = float(med_periods["parent_phi_time_vs_e"])
    child_period = float(med_periods["child_anti_phi_vs_e"])
    # Historical frozen gate retained for provenance. It is not a valid
    # child-cadence test: ARA predicts a smaller/faster child, while these
    # fitted periods are carrier-pair beat recurrences across prefix count.
    g2 = bool(parent > child and child_period > parent_period)

    valid_flat = prefix[prefix["overlap_loss"] <= 1e-12]
    flat_spreads = valid_flat.groupby("n")["flat_mean"].agg(lambda x: x.max() - x.min())
    max_flat_spread = float(flat_spreads.max()) if len(flat_spreads) else math.inf
    g4 = max_flat_spread <= 5e-4

    dense = [
        dense_numeric("phi_time", 73, "beam7_decay", 0.713),
        dense_numeric("one_over_e", 129, "beam7_cycle23", 1.117),
    ]
    all_overlap_cols = [
        col
        for col in prefix.columns
        if col.endswith("_mean") or col.endswith("_p05") or col.endswith("_min")
    ]
    bounded = bool(
        (prefix[all_overlap_cols].to_numpy() >= -1e-12).all()
        and (prefix[all_overlap_cols].to_numpy() <= 1.0 + 1e-12).all()
    )
    geometry_checks = {
        "x0_error": abs(embedded_parent_x(0.0) - E_INV),
        "x2_error": abs(embedded_parent_x(2.0) - PHI),
        "quarter_seam_drift": abs(4.0 * PARENT_DELTA - 1.0),
    }
    g0 = bool(
        geometry_checks["x0_error"] <= 1e-12
        and geometry_checks["x2_error"] <= 1e-12
        and geometry_checks["quarter_seam_drift"] < 0.001
        and bounded
        and all(item["pass"] for item in dense)
    )

    g3 = bool(coupling_stats["pass"])
    primary_count = sum([g1, g2, g3])
    if not (g0 and g4):
        verdict = "INVALID"
    elif primary_count == 3:
        verdict = "SUPPORTED FOR THIS IDEALIZED THREAD MODEL"
    elif primary_count == 2:
        verdict = "MIXED"
    else:
        verdict = "NOT SUPPORTED"
    return {
        "G0_implementation": g0,
        "G1_parent_four_step_thread": g1,
        "G2_parent_child_rung_separation": g2,
        "G3_coupling_driven_handover": g3,
        "G4_stationary_null": g4,
        "primary_pass_count": primary_count,
        "verdict": verdict,
        "details": {
            "period4_pair_ranking": {
                key: float(value) for key, value in pair_means.items()
            },
            "G1_winner": g1_winner,
            "parent_period4_partial_r2_mean": parent,
            "child_period4_partial_r2_mean": child,
            "parent_dominant_period_median": parent_period,
            "child_dominant_period_median": child_period,
            "coupling": coupling_stats,
            "max_flat_spread_nonoverlap": max_flat_spread,
            "geometry_checks": geometry_checks,
            "dense_checks": dense,
        },
    }


def make_figure(
    prefix: pd.DataFrame,
    harmonic: pd.DataFrame,
    coupling: pd.DataFrame,
    gates: dict,
) -> None:
    width, height = 1800, 1200
    image = Image.new("RGB", (width, height), "#f4f7fb")
    draw = ImageDraw.Draw(image)

    def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
        choices = [
            "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        ]
        for choice in choices:
            if Path(choice).exists():
                return ImageFont.truetype(choice, size)
        return ImageFont.load_default()

    title_font = font(30, True)
    panel_font = font(19, True)
    body_font = font(14)
    small_font = font(12)

    draw.text(
        (60, 34),
        (
            "T306 - embedded 1/e <-> Phi ARA thread | "
            f"frozen {gates['verdict']} | G2 cadence gate invalid"
        ),
        fill="#172033",
        font=title_font,
    )
    draw.text(
        (60, 78),
        "Fresh prefixes N=65..256 | unchanged idealized scheduling field from frozen T305",
        fill="#56657a",
        font=body_font,
    )
    panels = [
        (55, 125, 870, 625),
        (930, 125, 1745, 625),
        (55, 670, 870, 1145),
        (930, 670, 1745, 1145),
    ]
    for box in panels:
        draw.rounded_rectangle(
            box, radius=16, fill="#ffffff", outline="#d4dce8", width=2
        )

    # Exact embedded ARA geometry.
    x0, y0, x1, y1 = panels[0]
    draw.text(
        (x0 + 25, y0 + 20),
        "Embedded sphere on the unchanged parent 0-2 ARA",
        fill="#172033",
        font=panel_font,
    )
    line_left, line_right, line_y = x0 + 55, x1 - 55, y0 + 255
    draw.line((line_left, line_y, line_right, line_y), fill="#77869a", width=6)

    def scale_x(value: float) -> int:
        return int(line_left + (value / 2.0) * (line_right - line_left))

    draw.rounded_rectangle(
        (scale_x(E_INV), line_y - 18, scale_x(PHI), line_y + 18),
        radius=8,
        fill="#eee1c6",
    )
    points = [
        (0.0, "0", "#6b7788", -6, 42),
        (E_INV, "1/e\nSpace / Phase B", "#315f9b", -80, -92),
        (ANTI_PHI, "anti-Phi\nchild marker", "#7c8ba1", -35, 48),
        (PARENT_CENTRE, f"embedded ridge\n{PARENT_CENTRE:.6f}", "#2f8f64", -95, -92),
        (1.0, "parent ridge\n1.0", "#172033", 18, 48),
        (PHI, "Phi\nTime / Phase A", "#d49325", -70, -92),
        (2.0, "2", "#6b7788", -6, 42),
    ]
    for value, label, color, dx, dy in points:
        xp = scale_x(value)
        draw.ellipse((xp - 8, line_y - 8, xp + 8, line_y + 8), fill=color)
        draw.multiline_text(
            (xp + dx, line_y + dy),
            label,
            fill=color,
            font=small_font,
            spacing=2,
            align="center",
        )
    draw.text(
        (x0 + 35, y1 - 82),
        f"Parent-pair separation {PARENT_DELTA:.9f} -> beat recurrence {1/PARENT_DELTA:.4f}",
        fill="#37465a",
        font=body_font,
    )
    draw.text(
        (x0 + 35, y1 - 51),
        f"Child-pair separation {CHILD_DELTA:.9f} -> beat recurrence {1/CHILD_DELTA:.2f}",
        fill="#37465a",
        font=body_font,
    )

    # Fresh-prefix endpoint contrasts.
    x0, y0, x1, y1 = panels[1]
    draw.text(
        (x0 + 25, y0 + 20),
        "Fresh-prefix contrast: Phi(Time) - 1/e",
        fill="#172033",
        font=panel_font,
    )
    plot_left, plot_top, plot_right, plot_bottom = (
        x0 + 65,
        y0 + 70,
        x1 - 35,
        y1 - 65,
    )
    indexed = prefix.set_index(["candidate", "n"])
    curves: list[tuple[str, str, np.ndarray]] = []
    for family, color in zip(FAMILIES, ["#315f9b", "#8f5b9a", "#d49325"]):
        values = np.array(
            [
                indexed.loc[("phi_time", int(n)), f"{family}_p05"]
                - indexed.loc[("one_over_e", int(n)), f"{family}_p05"]
                for n in PREFIXES
            ],
            dtype=float,
        )
        curves.append((family, color, values))
    y_max = max(
        max(float(np.max(np.abs(values))), 1e-9) for _, _, values in curves
    )
    draw.rectangle(
        (plot_left, plot_top, plot_right, plot_bottom),
        outline="#cad3df",
        width=1,
    )
    zero_y = int((plot_top + plot_bottom) / 2)
    draw.line((plot_left, zero_y, plot_right, zero_y), fill="#7b8797", width=1)
    for family, color, values in curves:
        coordinates = []
        for n, value in zip(PREFIXES, values):
            xp = plot_left + (
                float(n - PREFIXES.min())
                / float(PREFIXES.max() - PREFIXES.min())
            ) * (plot_right - plot_left)
            yp = plot_top + ((y_max - float(value)) / (2 * y_max)) * (
                plot_bottom - plot_top
            )
            coordinates.append((int(xp), int(yp)))
        draw.line(coordinates, fill=color, width=2)
    for index, (family, color, _) in enumerate(curves):
        xx = x0 + 72 + index * 225
        draw.line((xx, y1 - 36, xx + 30, y1 - 36), fill=color, width=4)
        draw.text((xx + 38, y1 - 46), family, fill="#445167", font=small_font)

    # Period-four rankings.
    x0, y0, x1, y1 = panels[2]
    draw.text(
        (x0 + 25, y0 + 20),
        "Predeclared period-four signal by pair",
        fill="#172033",
        font=panel_font,
    )
    means = harmonic.groupby("pair")["period4_partial_r2"].mean().sort_values()
    max_mean = max(float(means.max()), 1e-12)
    bar_left, bar_right = x0 + 300, x1 - 45
    for index, (name, value) in enumerate(means.items()):
        yy = y0 + 70 + index * 49
        color = (
            "#d49325"
            if name == "parent_phi_time_vs_e"
            else "#315f9b"
            if name == "child_anti_phi_vs_e"
            else "#aab3bf"
        )
        draw.text(
            (x0 + 25, yy + 4),
            name.replace("_", " "),
            fill="#445167",
            font=small_font,
        )
        length = int((float(value) / max_mean) * (bar_right - bar_left))
        draw.rectangle((bar_left, yy, bar_left + length, yy + 25), fill=color)
        draw.text(
            (bar_left + length + 8, yy + 4),
            f"{float(value):.4f}",
            fill="#445167",
            font=small_font,
        )

    # Coupling-sweep heat map.
    x0, y0, x1, y1 = panels[3]
    switch_fraction = gates["details"]["coupling"]["switch_fraction"]
    draw.text(
        (x0 + 25, y0 + 20),
        f"Coupling sweep ({switch_fraction:.1%} of prefixes switch winner)",
        fill="#172033",
        font=panel_font,
    )
    pivot = coupling.pivot(
        index="coupling", columns="n", values="contrast_phi_minus_e"
    )
    values = pivot.to_numpy()
    value_max = max(float(np.max(np.abs(values))), 1e-12)
    heat_left, heat_top, heat_right, heat_bottom = (
        x0 + 65,
        y0 + 75,
        x1 - 45,
        y1 - 65,
    )
    cell_width = (heat_right - heat_left) / values.shape[1]
    cell_height = (heat_bottom - heat_top) / values.shape[0]
    for row in range(values.shape[0]):
        for column in range(values.shape[1]):
            scaled = float(values[row, column]) / value_max
            if scaled >= 0:
                color = (
                    int(238 - 120 * scaled),
                    int(238 - 80 * scaled),
                    int(244 - 25 * scaled),
                )
            else:
                scaled = -scaled
                color = (
                    int(244 - 25 * scaled),
                    int(238 - 80 * scaled),
                    int(238 - 120 * scaled),
                )
            xa = int(heat_left + column * cell_width)
            xb = max(xa + 1, int(heat_left + (column + 1) * cell_width))
            ya = int(heat_bottom - (row + 1) * cell_height)
            yb = max(ya + 1, int(heat_bottom - row * cell_height))
            draw.rectangle((xa, ya, xb, yb), fill=color)
    draw.rectangle(
        (heat_left, heat_top, heat_right, heat_bottom),
        outline="#9aa7b8",
        width=1,
    )
    draw.text((heat_left, heat_bottom + 12), "N=65", fill="#56657a", font=small_font)
    draw.text(
        (heat_right - 45, heat_bottom + 12),
        "256",
        fill="#56657a",
        font=small_font,
    )
    draw.text((x0 + 12, heat_top), "c=1", fill="#56657a", font=small_font)
    draw.text(
        (x0 + 12, heat_bottom - 16),
        "c=0",
        fill="#56657a",
        font=small_font,
    )

    image.save(OUT_FIG)


def main() -> None:
    prefix, raw = run_prefixes()
    harmonic = harmonic_summary(prefix)
    coupling, coupling_stats = coupling_sweep(raw)
    gates = evaluate(prefix, harmonic, coupling_stats)

    prefix.to_csv(OUT_PREFIX, index=False, float_format="%.12g")
    harmonic.to_csv(OUT_HARMONIC, index=False, float_format="%.12g")
    coupling.to_csv(OUT_COUPLING, index=False, float_format="%.12g")
    make_figure(prefix, harmonic, coupling, gates)

    payload = {
        "test": "T306 embedded 1/e <-> Phi ARA thread",
        "frozen_protocol": "T306_EMBEDDED_E_PHI_THREAD_PROTOCOL_v1_FROZEN.md",
        "fresh_range": {"min": 65, "max": 256, "count": len(PREFIXES)},
        "geometry": {
            "space_phaseB_parent_location": E_INV,
            "time_phaseA_parent_location": PHI,
            "time_carrier_fraction": PHI_TIME,
            "embedded_centre_parent_coordinate": PARENT_CENTRE,
            "embedded_radius_parent_units": PARENT_RADIUS,
            "embedded_diameter_parent_units": PARENT_DIAMETER,
            "TE_ARA_endpoint_sum": PHI + E_INV,
            "closure_deficit": PARENT_DEFICIT,
            "parent_carrier_separation": PARENT_DELTA,
            "parent_pair_beat_recurrence_placements": 1.0 / PARENT_DELTA,
            "child_carrier_separation": CHILD_DELTA,
            "child_pair_beat_recurrence_placements": 1.0 / CHILD_DELTA,
        },
        "framework_fidelity_amendment": {
            "date": "2026-07-30",
            "issue": (
                "Frozen G2 inverted the ARA octave direction by treating the "
                "child as slower than the parent."
            ),
            "correct_ara_rule": (
                "A child one pure octave down is smaller and faster, with "
                "approximately half the parent period."
            ),
            "measurement_boundary": (
                "The reported 3.9975 and 70.99 values are pairwise carrier "
                "beat recurrences, not physical parent/child cadences."
            ),
            "interpretive_status": (
                "Original frozen verdict retained; G2 is invalid as evidence "
                "against the faster-child ARA rule."
            ),
        },
        "gates": gates,
        "artifacts": {
            "prefix_csv": OUT_PREFIX.name,
            "harmonic_csv": OUT_HARMONIC.name,
            "coupling_csv": OUT_COUPLING.name,
            "figure": OUT_FIG.name,
        },
        "boundary": (
            "Fresh-prefix idealized scheduling result; not laboratory Fusion "
            "evidence and not proof of a literal physical double helix."
        ),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(json.dumps({"verdict": gates["verdict"], "gates": gates}, indent=2))


if __name__ == "__main__":
    main()
