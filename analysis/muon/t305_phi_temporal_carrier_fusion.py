#!/usr/bin/env python3
"""T305: frozen ARA Phi temporal-carrier test for muon-Fusion scheduling."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHI_DIR = ROOT / "analysis" / "phi_calibration"

OUT_JSON = HERE / "T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_RESULTS.json"
OUT_PREFIX = HERE / "T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_PREFIX_RESULTS.csv"
OUT_SUMMARY = HERE / "T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_SUMMARY.csv"
OUT_FIG = HERE / "T305_ARA_PHI_TEMPORAL_CARRIER_FUSION.png"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_A = PHI ** -2
PHI_REVERSE = 1.0 - PHI_A
N_MAX = 64
WIDTH = 0.15 / N_MAX
PREFIXES = np.arange(4, N_MAX + 1)
PHASES = np.linspace(0.0, 2.0 * math.pi, 128, endpoint=False)

CANDIDATES = {
    "phi": PHI_A,
    "phi_reverse": PHI_REVERSE,
    "three_eighths": 3.0 / 8.0,
    "eight_twentyone": 8.0 / 21.0,
    "one_over_e": 1.0 / math.e,
    "two_fifths": 2.0 / 5.0,
    "sqrt2_minus_1": math.sqrt(2.0) - 1.0,
    "one_third": 1.0 / 3.0,
    "pi_minus_3": math.pi - 3.0,
}

# Reverse Phi is an orientation control. The oracle changes with N.
FORWARD_ELIGIBLE = [name for name in CANDIDATES if name != "phi_reverse"]
IRRATIONAL_CONTROLS = [
    "phi", "phi_reverse", "one_over_e", "sqrt2_minus_1", "pi_minus_3"
]
NONFLAT = ["beam7", "beam7_cycle23", "beam7_decay"]


def carrier_centres(alpha: float, n: int) -> np.ndarray:
    return np.mod(np.arange(n, dtype=float) * alpha, 1.0)


def oracle_centres(n: int) -> np.ndarray:
    return (np.arange(n, dtype=float) + 0.5) / n


def merged_intervals(centres: np.ndarray, width: float = WIDTH) -> list[tuple[float, float]]:
    """Union of wrapped pulse intervals on [0,1]."""
    raw: list[tuple[float, float]] = []
    half = width / 2.0
    for centre in centres:
        lo = float(centre - half)
        hi = float(centre + half)
        if lo < 0.0:
            raw.append((0.0, hi))
            raw.append((1.0 + lo, 1.0))
        elif hi > 1.0:
            raw.append((lo, 1.0))
            raw.append((0.0, hi - 1.0))
        else:
            raw.append((lo, hi))
    raw.sort()
    merged: list[list[float]] = []
    for lo, hi in raw:
        if not merged or lo > merged[-1][1] + 1e-15:
            merged.append([lo, hi])
        else:
            merged[-1][1] = max(merged[-1][1], hi)
    return [(float(lo), float(hi)) for lo, hi in merged]


def union_length(intervals: list[tuple[float, float]]) -> float:
    return float(sum(hi - lo for lo, hi in intervals))


def largest_gap(centres: np.ndarray) -> float:
    x = np.sort(np.mod(centres, 1.0))
    gaps = np.diff(np.r_[x, x[0] + 1.0])
    return float(np.max(gaps))


def ordinary_star_discrepancy(x: np.ndarray) -> float:
    y = np.sort(np.mod(x, 1.0))
    n = len(y)
    idx = np.arange(1, n + 1, dtype=float)
    return float(max(np.max(idx / n - y), np.max(y - (idx - 1.0) / n)))


def circular_star_discrepancy(centres: np.ndarray) -> float:
    """Rotation-invariant 1D discrepancy: best point-origin rotation."""
    x = np.mod(centres, 1.0)
    values = []
    for origin in x:
        values.append(ordinary_star_discrepancy(np.mod(x - origin, 1.0)))
    return float(min(values))


def exp_integral(intervals: list[tuple[float, float]], z: complex) -> complex:
    return sum((np.exp(z * hi) - np.exp(z * lo)) / z for lo, hi in intervals)


def cosine_integral(
    intervals: list[tuple[float, float]], frequency: float, phase: np.ndarray
) -> np.ndarray:
    w = 2.0 * math.pi * frequency
    total = np.zeros_like(phase, dtype=float)
    for lo, hi in intervals:
        total += (np.sin(w * hi + phase) - np.sin(w * lo + phase)) / w
    return total


def arrival_overlap(
    intervals: list[tuple[float, float]], family: str, phases: np.ndarray = PHASES
) -> np.ndarray:
    length = union_length(intervals)
    if family == "flat":
        return np.full_like(phases, length, dtype=float)
    if family == "beam7":
        numerator = length + 0.85 * cosine_integral(intervals, 7.0, phases)
        return np.clip(numerator, 0.0, 1.0)
    if family == "beam7_cycle23":
        d = 0.6
        numerator = (
            length
            + d * cosine_integral(intervals, 7.0, phases)
            + d * cosine_integral(intervals, 23.0, 1.7 * phases)
            + 0.5 * d * d
            * cosine_integral(intervals, 16.0, -0.7 * phases)
            + 0.5 * d * d
            * cosine_integral(intervals, 30.0, 2.7 * phases)
        )
        return np.clip(numerator, 0.0, 1.0)
    if family == "beam7_decay":
        tau = 0.45
        d = 0.85
        z0 = -1.0 / tau
        z1 = complex(-1.0 / tau, 2.0 * math.pi * 7.0)
        base = float(np.real(exp_integral(intervals, z0)))
        harmonic = exp_integral(intervals, z1)
        numerator = base + d * np.real(np.exp(1j * phases) * harmonic)
        full = [(0.0, 1.0)]
        norm_base = float(np.real(exp_integral(full, z0)))
        norm_harmonic = exp_integral(full, z1)
        denominator = norm_base + d * np.real(np.exp(1j * phases) * norm_harmonic)
        return np.clip(numerator / denominator, 0.0, 1.0)
    raise KeyError(family)


def circular_step_estimate(centres: np.ndarray) -> float:
    steps = np.mod(np.diff(centres), 1.0)
    vector = np.mean(np.exp(2j * math.pi * steps))
    return float((np.angle(vector) / (2.0 * math.pi)) % 1.0)


def circular_distance(a: float, b: float) -> float:
    d = abs(a - b) % 1.0
    return float(min(d, 1.0 - d))


def exact_controls() -> dict:
    controls = {
        "phi": PHI_A,
        "phi_reverse": PHI_REVERSE,
        "three_eighths": 3.0 / 8.0,
        "sqrt2_minus_1": math.sqrt(2.0) - 1.0,
        "one_third": 1.0 / 3.0,
    }
    rows = {}
    for name, alpha in controls.items():
        estimate = circular_step_estimate(carrier_centres(alpha, 257))
        error = circular_distance(estimate, alpha)
        rows[name] = {
            "supplied": alpha,
            "recovered": estimate,
            "circular_abs_error": error,
            "pass": error <= 1e-12,
        }
    return rows


def t302_calibration() -> dict:
    source = PHI_DIR / "T302_PHI_PHYLLOTAXIS_RESULTS.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    frozen = payload["frozen"]
    return {
        "source": str(source.relative_to(ROOT)),
        "confirmation_wt_coordinate": frozen["P1_confirmation_wt_coordinate"],
        "distance_from_phi": frozen["P1_distance_from_phi"],
        "fixed_step_winner": frozen["P2_fixed_step_winner"],
        "fixed_cumulative_winner": frozen["P3_fixed_cumulative_winner"],
        "landmark_pass": frozen["passes"]["P1_landmark_within_0.01"],
        "cumulative_phi_pass": frozen["passes"]["P3_exact_phi_cumulative_winner"],
        "calibration_only": True,
    }


def dense_spot_check() -> dict:
    n = 37
    phase = 0.713
    intervals = merged_intervals(carrier_centres(PHI_A, n))
    analytic = float(arrival_overlap(intervals, "beam7_decay", np.array([phase]))[0])
    m = 400_000
    t = (np.arange(m) + 0.5) / m
    cover = np.zeros(m, dtype=bool)
    for lo, hi in intervals:
        cover |= (t >= lo) & (t < hi)
    g = np.exp(-t / 0.45) * (1.0 + 0.85 * np.cos(2.0 * math.pi * 7.0 * t + phase))
    g /= g.mean()
    numeric = float(np.mean(g * cover))
    return {
        "candidate": "phi",
        "n": n,
        "family": "beam7_decay",
        "phase": phase,
        "analytic": analytic,
        "dense_numeric": numeric,
        "absolute_error": abs(analytic - numeric),
        "pass": abs(analytic - numeric) <= 5e-4,
    }


def run_prefixes() -> pd.DataFrame:
    rows: list[dict] = []
    schedules = list(CANDIDATES) + ["oracle_uniform"]
    families = ["flat"] + NONFLAT
    for name in schedules:
        for n in PREFIXES:
            centres = (
                oracle_centres(int(n))
                if name == "oracle_uniform"
                else carrier_centres(CANDIDATES[name], int(n))
            )
            intervals = merged_intervals(centres)
            length = union_length(intervals)
            row = {
                "candidate": name,
                "n": int(n),
                "largest_gap": largest_gap(centres),
                "circular_star_discrepancy": circular_star_discrepancy(centres),
                "union_coverage": length,
                "overlap_loss": max(0.0, int(n) * WIDTH - length),
            }
            for family in families:
                values = arrival_overlap(intervals, family)
                row[f"{family}_mean"] = float(np.mean(values))
                row[f"{family}_p05"] = float(np.percentile(values, 5))
                row[f"{family}_min"] = float(np.min(values))
            rows.append(row)
    return pd.DataFrame(rows)


def add_geometry_ranks(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output["largest_gap_rank"] = np.nan
    output["discrepancy_rank"] = np.nan
    for n in PREFIXES:
        mask = (output["n"] == n) & output["candidate"].isin(FORWARD_ELIGIBLE)
        output.loc[mask, "largest_gap_rank"] = (
            output.loc[mask, "largest_gap"].rank(method="average", ascending=True)
        )
        output.loc[mask, "discrepancy_rank"] = (
            output.loc[mask, "circular_star_discrepancy"]
            .rank(method="average", ascending=True)
        )
    return output


def aggregate(frame: pd.DataFrame) -> pd.DataFrame:
    records = []
    for name, group in frame.groupby("candidate", sort=False):
        cells = group[[f"{family}_p05" for family in NONFLAT]].to_numpy().ravel()
        records.append(
            {
                "candidate": name,
                "alpha": CANDIDATES.get(name, np.nan),
                "eligible_forward": name in FORWARD_ELIGIBLE,
                "geometry_mean_rank": float(
                    np.nanmean(
                        group[["largest_gap_rank", "discrepancy_rank"]].to_numpy()
                    )
                )
                if name in FORWARD_ELIGIBLE
                else np.nan,
                "largest_gap_mean": float(group["largest_gap"].mean()),
                "discrepancy_mean": float(
                    group["circular_star_discrepancy"].mean()
                ),
                "overlap_loss_total": float(group["overlap_loss"].sum()),
                "fusion_robust_overlap_mean": float(np.mean(cells)),
                "fusion_robust_overlap_tail_p05": float(np.percentile(cells, 5)),
                "flat_overlap_mean": float(group["flat_mean"].mean()),
            }
        )
    summary = pd.DataFrame(records)
    reference = frame[frame["candidate"] == "three_eighths"].set_index("n")
    win_shares = {}
    for name in CANDIDATES:
        group = frame[frame["candidate"] == name].set_index("n")
        strict = []
        for family in NONFLAT:
            strict.extend(
                (
                    group[f"{family}_p05"]
                    > reference[f"{family}_p05"] + 1e-15
                ).tolist()
            )
        win_shares[name] = float(np.mean(strict))
    summary["strict_cell_win_share_vs_three_eighths"] = summary["candidate"].map(
        win_shares
    )
    return summary


def unique_min_winner(summary: pd.DataFrame, column: str) -> tuple[str, bool]:
    eligible = summary[summary["eligible_forward"]].sort_values(column)
    best = str(eligible.iloc[0]["candidate"])
    unique = float(eligible.iloc[1][column] - eligible.iloc[0][column]) > 1e-12
    return best, bool(unique)


def unique_max_winner(summary: pd.DataFrame, column: str) -> tuple[str, bool]:
    eligible = summary[summary["eligible_forward"]].sort_values(
        column, ascending=False
    )
    best = str(eligible.iloc[0]["candidate"])
    unique = float(eligible.iloc[0][column] - eligible.iloc[1][column]) > 1e-12
    return best, bool(unique)


def evaluate_gates(
    frame: pd.DataFrame,
    summary: pd.DataFrame,
    controls: dict,
    dense_check: dict,
) -> dict:
    phi_row = summary.set_index("candidate").loc["phi"]
    three_row = summary.set_index("candidate").loc["three_eighths"]
    g1_winner, g1_unique = unique_min_winner(summary, "geometry_mean_rank")
    g2_winner, g2_unique = unique_max_winner(
        summary, "fusion_robust_overlap_mean"
    )
    g3_winner, g3_unique = unique_max_winner(
        summary, "fusion_robust_overlap_tail_p05"
    )

    null_spreads = []
    for n in PREFIXES:
        group = frame[
            (frame["n"] == n)
            & frame["candidate"].isin(IRRATIONAL_CONTROLS)
            & (frame["overlap_loss"] <= 1e-12)
        ]
        if len(group) >= 2:
            null_spreads.append(float(group["flat_mean"].max() - group["flat_mean"].min()))
    max_null_spread = max(null_spreads) if null_spreads else math.inf

    g0 = (
        all(item["pass"] for item in controls.values())
        and dense_check["pass"]
        and bool(
            (
                frame[
                    [
                        col
                        for col in frame.columns
                        if col.endswith("_mean")
                        or col.endswith("_p05")
                        or col.endswith("_min")
                    ]
                ].to_numpy()
                >= -1e-12
            ).all()
        )
        and bool(
            (
                frame[
                    [
                        col
                        for col in frame.columns
                        if col.endswith("_mean")
                        or col.endswith("_p05")
                        or col.endswith("_min")
                    ]
                ].to_numpy()
                <= 1.0 + 1e-12
            ).all()
        )
    )
    g1 = bool(
        g1_winner == "phi"
        and g1_unique
        and phi_row["geometry_mean_rank"] < three_row["geometry_mean_rank"]
    )
    g2 = bool(
        g2_winner == "phi"
        and g2_unique
        and phi_row["fusion_robust_overlap_mean"]
        > three_row["fusion_robust_overlap_mean"]
        and phi_row["strict_cell_win_share_vs_three_eighths"] >= 0.60
    )
    g3 = bool(
        g3_winner == "phi"
        and g3_unique
        and phi_row["fusion_robust_overlap_tail_p05"]
        > three_row["fusion_robust_overlap_tail_p05"]
    )
    g4 = bool(max_null_spread <= 5e-4)

    primary_passes = sum([g1, g2, g3])
    if not (g0 and g4):
        verdict = "INVALID"
    elif primary_passes >= 2:
        verdict = (
            "SUPPORTED FOR THIS SCHEDULING MODEL"
            if primary_passes == 3
            else "MIXED"
        )
    else:
        verdict = "NOT SUPPORTED"
    return {
        "G0_implementation": g0,
        "G1_geometry": g1,
        "G2_fusion_mean_robust_overlap": g2,
        "G3_fusion_tail_robustness": g3,
        "G4_stationary_null": g4,
        "primary_pass_count": primary_passes,
        "verdict": verdict,
        "details": {
            "G1_winner": g1_winner,
            "G1_unique": g1_unique,
            "G2_winner": g2_winner,
            "G2_unique": g2_unique,
            "G3_winner": g3_winner,
            "G3_unique": g3_unique,
            "phi_strict_cell_win_share_vs_three_eighths": float(
                phi_row["strict_cell_win_share_vs_three_eighths"]
            ),
            "max_flat_null_spread_nonoverlap": max_null_spread,
        },
    }


def make_figure(frame: pd.DataFrame, summary: pd.DataFrame, calibration: dict) -> None:
    from PIL import Image, ImageDraw, ImageFont

    labels = {
        "phi": "Phi",
        "phi_reverse": "Phi reverse",
        "three_eighths": "3/8",
        "eight_twentyone": "8/21",
        "one_over_e": "1/e",
        "two_fifths": "2/5",
        "sqrt2_minus_1": "sqrt(2)-1",
        "one_third": "1/3",
        "pi_minus_3": "pi-3",
        "oracle_uniform": "oracle uniform",
    }
    colors = {
        "phi": (215, 155, 46),
        "phi_reverse": (181, 101, 118),
        "three_eighths": (76, 120, 168),
        "oracle_uniform": (95, 107, 118),
    }

    image = Image.new("RGB", (1800, 1200), (247, 249, 252))
    draw = ImageDraw.Draw(image)
    try:
        title_font = ImageFont.truetype("arial.ttf", 34)
        panel_font = ImageFont.truetype("arial.ttf", 24)
        text_font = ImageFont.truetype("arial.ttf", 17)
        small_font = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        title_font = panel_font = text_font = small_font = ImageFont.load_default()

    ink = (37, 48, 60)
    grid = (215, 221, 228)
    panel_fill = (255, 255, 255)
    draw.text(
        (55, 28),
        "T305 — ARA Phi temporal carrier: known calibration → Fusion schedule",
        fill=ink,
        font=title_font,
    )

    panels = [(50, 100, 875, 590), (925, 100, 1750, 590),
              (50, 650, 875, 1140), (925, 650, 1750, 1140)]
    for box in panels:
        draw.rounded_rectangle(box, radius=18, fill=panel_fill, outline=grid, width=2)

    # Panel 1: known calibration landmarks.
    x0, y0, x1, y1 = panels[0]
    draw.text((x0 + 24, y0 + 20), "Known empirical calibration (not Fusion evidence)",
              fill=ink, font=panel_font)
    left, right, baseline = x0 + 70, x1 - 50, y0 + 260
    draw.line((left, baseline, right, baseline), fill=ink, width=3)
    for value, name, color, yoff in [
        (PHI_A, "Phi 0.381966", colors["phi"], -65),
        (3 / 8, "3/8 0.375", colors["three_eighths"], 35),
        (
            calibration["confirmation_wt_coordinate"],
            f"T302 WT {calibration['confirmation_wt_coordinate']:.6f}",
            (42, 157, 143),
            -10,
        ),
    ]:
        px = left + (value - 0.34) / (0.42 - 0.34) * (right - left)
        draw.line((px, baseline - 55, px, baseline + 55), fill=color, width=5)
        draw.text((px - 48, baseline + yoff), name, fill=color, font=small_font)
    draw.text((left, baseline + 90), "0.34", fill=ink, font=small_font)
    draw.text((right - 30, baseline + 90), "0.42", fill=ink, font=small_font)
    draw.text((left, y1 - 75), "Exact Phi already won T302 cumulative position;",
              fill=ink, font=text_font)
    draw.text((left, y1 - 48), "3/8 won the local one-step endpoint.",
              fill=ink, font=text_font)

    def bar_panel(box, title, data, value_col, lower_better):
        bx0, by0, bx1, by1 = box
        draw.text((bx0 + 24, by0 + 20), title, fill=ink, font=panel_font)
        chart_l, chart_r = bx0 + 65, bx1 - 25
        chart_t, chart_b = by0 + 75, by1 - 105
        values = data[value_col].astype(float).to_numpy()
        vmax, vmin = float(np.max(values)), float(np.min(values))
        base = 0.0 if vmin >= 0 else vmin
        span = max(vmax - base, 1e-12)
        width = (chart_r - chart_l) / len(data)
        for i, (_, row) in enumerate(data.iterrows()):
            name = str(row["candidate"])
            value = float(row[value_col])
            height = (value - base) / span * (chart_b - chart_t)
            xa = chart_l + i * width + 5
            xb = chart_l + (i + 1) * width - 5
            ya = chart_b - height
            draw.rectangle((xa, ya, xb, chart_b),
                           fill=colors.get(name, (174, 184, 194)))
            label = labels[name]
            draw.text((xa, chart_b + 10), label[:12], fill=ink, font=small_font)
        draw.line((chart_l, chart_b, chart_r, chart_b), fill=ink, width=2)
        qualifier = "lower is better" if lower_better else "higher is better"
        draw.text((chart_l, by1 - 35), qualifier, fill=ink, font=small_font)

    # Panel 2: geometric mean ranks.
    eligible = summary[summary["eligible_forward"]].sort_values(
        "geometry_mean_rank"
    )
    bar_panel(
        panels[1],
        "Unknown-prefix geometric coverage",
        eligible,
        "geometry_mean_rank",
        True,
    )

    # Panel 3: Fusion aggregate robust overlap.
    ordered = summary.sort_values("fusion_robust_overlap_mean", ascending=False)
    bar_panel(
        panels[2],
        "Fusion model: robust overlap across unknown phase",
        ordered,
        "fusion_robust_overlap_mean",
        False,
    )

    # Panel 4: prefix curves.
    bx0, by0, bx1, by1 = panels[3]
    draw.text((bx0 + 24, by0 + 20), "Carrier performance while sequence unfolds",
              fill=ink, font=panel_font)
    chart_l, chart_r = bx0 + 70, bx1 - 35
    chart_t, chart_b = by0 + 80, by1 - 75
    curves = {}
    for name in ["phi", "three_eighths", "sqrt2_minus_1", "oracle_uniform"]:
        group = frame[frame["candidate"] == name].sort_values("n")
        curves[name] = group[[f"{family}_p05" for family in NONFLAT]].mean(
            axis=1
        ).to_numpy()
    ymin = min(float(np.min(v)) for v in curves.values())
    ymax = max(float(np.max(v)) for v in curves.values())
    for fraction in np.linspace(0, 1, 5):
        yy = chart_b - fraction * (chart_b - chart_t)
        draw.line((chart_l, yy, chart_r, yy), fill=grid, width=1)
    for name, curve in curves.items():
        points = []
        for n, value in zip(PREFIXES, curve):
            px = chart_l + (n - PREFIXES.min()) / (PREFIXES.max() - PREFIXES.min()) * (chart_r - chart_l)
            py = chart_b - (value - ymin) / max(ymax - ymin, 1e-12) * (chart_b - chart_t)
            points.append((px, py))
        draw.line(points, fill=colors.get(name, (114, 126, 139)),
                  width=4 if name in {"phi", "three_eighths"} else 2)
    draw.line((chart_l, chart_b, chart_r, chart_b), fill=ink, width=2)
    legend_x = chart_l
    for name in curves:
        draw.line((legend_x, by1 - 34, legend_x + 24, by1 - 34),
                  fill=colors.get(name, (114, 126, 139)), width=4)
        draw.text((legend_x + 30, by1 - 44), labels[name], fill=ink, font=small_font)
        legend_x += 165

    image.save(OUT_FIG)


def main() -> None:
    controls = exact_controls()
    calibration = t302_calibration()
    dense_check = dense_spot_check()
    prefix = add_geometry_ranks(run_prefixes())
    summary = aggregate(prefix)
    gates = evaluate_gates(prefix, summary, controls, dense_check)

    prefix.to_csv(OUT_PREFIX, index=False, float_format="%.12g")
    summary.to_csv(OUT_SUMMARY, index=False, float_format="%.12g")
    make_figure(prefix, summary, calibration)

    result = {
        "test": "T305",
        "config": {
            "n_max": N_MAX,
            "prefix_min": int(PREFIXES.min()),
            "prefix_max": int(PREFIXES.max()),
            "n_prefixes": len(PREFIXES),
            "pulse_width": WIDTH,
            "total_duty_at_n64": WIDTH * N_MAX,
            "n_source_phases": len(PHASES),
            "candidates": CANDIDATES,
            "forward_eligible": FORWARD_ELIGIBLE,
            "nonflat_families": NONFLAT,
        },
        "known_exact_controls": controls,
        "known_empirical_calibration": calibration,
        "dense_integration_spot_check": dense_check,
        "gates": gates,
        "summary": summary.replace({np.nan: None}).to_dict(orient="records"),
        "artifacts": {
            "prefix_csv": OUT_PREFIX.name,
            "summary_csv": OUT_SUMMARY.name,
            "figure": OUT_FIG.name,
        },
        "interpretation_boundary": (
            "Idealized overlap scheduling only; not laboratory muon data, "
            "microscopic stripping, recycling, or proof of a natural Phi carrier."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(gates, indent=2))
    print()
    print(
        summary.sort_values("fusion_robust_overlap_mean", ascending=False)[
            [
                "candidate",
                "geometry_mean_rank",
                "fusion_robust_overlap_mean",
                "fusion_robust_overlap_tail_p05",
                "strict_cell_win_share_vs_three_eighths",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
