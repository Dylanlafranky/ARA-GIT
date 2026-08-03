#!/usr/bin/env python3
"""T327: frozen ARA Phi circle-train test on a river-flume thalweg.

The source workbook contains 41 lateral bed points at each retained bend
cross-section.  Rank 1 (minimum Z) is the thalweg; ranks 2..41 are matched
downstream-ordered controls.  No interpolation, smoothing, Fourier transform,
or source-order optimization is used.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source_bedrock_bends" / "Bed-topography.xlsx"
PROTOCOL = HERE / "T327_PHI_CIRCLE_TRAIN_THALWEG_PROTOCOL_v2_FROZEN.md"
PREFIX = "T327_PHI_CIRCLE_TRAIN_THALWEG"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INCREMENT = 2.0 / PHI**2
N_NULL = 10_000
RNG_SEED = 327
LAGS = (2, 3, 5, 8, 13, 21)
HORIZONS = (1, 2, 3, 5, 8, 13, 21)

CANDIDATES = OrderedDict(
    [
        ("persistence", 0.0),
        ("one_third", 2.0 / 3.0),
        ("one_over_e", 2.0 / math.e),
        ("three_eighths", 3.0 / 4.0),
        ("fibonacci_8_21", 16.0 / 21.0),
        ("phi", PHI_INCREMENT),
        ("two_fifths", 4.0 / 5.0),
        ("silver_conjugate", 2.0 * (math.sqrt(2.0) - 1.0)),
        ("ridge", 1.0),
    ]
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def d2(a, b):
    difference = np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))
    return np.minimum(difference, 2.0 - difference)


def whole_path_scores(x: np.ndarray, delta: float) -> dict[str, float | str]:
    """Score a candidate using one fixed sign for the complete path."""
    x = np.asarray(x, dtype=float)
    increments = np.mod(np.diff(x), 2.0)
    local_positive = float(np.median(d2(increments, delta)))
    local_negative = float(np.median(d2(increments, (2.0 - delta) % 2.0)))

    anchor = float(x[1])
    horizons = np.arange(1, len(x) - 1, dtype=float)
    target = x[2:]
    positive_prediction = np.mod(anchor + horizons * delta, 2.0)
    negative_prediction = np.mod(anchor - horizons * delta, 2.0)
    parent_positive = float(np.median(d2(target, positive_prediction)))
    parent_negative = float(np.median(d2(target, negative_prediction)))

    return {
        "local_positive": local_positive,
        "local_negative": local_negative,
        "local_score": min(local_positive, local_negative),
        "local_sign": "+" if local_positive <= local_negative else "-",
        "parent_positive": parent_positive,
        "parent_negative": parent_negative,
        "parent_score": min(parent_positive, parent_negative),
        "parent_sign": "+" if parent_positive <= parent_negative else "-",
    }


def read_cross_sections() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_excel(SOURCE)
    if raw.shape != (1666, 3):
        raise RuntimeError(f"Unexpected source workbook shape {raw.shape}")
    raw.columns = ["x_mm", "y_mm", "z_mm"]

    # The bend portion is stored in consecutive 41-row source blocks.  Block
    # 2 is 10 degrees and block 34 is 170 degrees; the 5-degree block is not
    # present, matching the eligibility declaration in the frozen protocol.
    rows: list[dict[str, float | int]] = []
    features: list[dict[str, float | int]] = []
    for block_index, angle_expected in zip(range(2, 35), range(10, 175, 5)):
        section = raw.iloc[block_index * 41 : (block_index + 1) * 41].copy()
        if len(section) != 41:
            raise RuntimeError(f"Cross-section {angle_expected} has {len(section)} rows")
        angle = np.degrees(np.arctan2(section["y_mm"], section["x_mm"]))
        if float(np.max(np.abs(angle - angle_expected))) > 1e-5:
            raise RuntimeError(f"Coordinate angle mismatch at {angle_expected} degrees")
        section["radius_mm"] = np.hypot(section["x_mm"], section["y_mm"])
        section = section.sort_values("radius_mm", kind="mergesort").reset_index(drop=True)
        r_min = float(section["radius_mm"].min())
        r_max = float(section["radius_mm"].max())
        if abs(r_min - 1000.0) > 1e-3 or abs(r_max - 1400.0) > 1e-3:
            raise RuntimeError(f"Unexpected lateral support at {angle_expected}")
        section["x_ara"] = 2.0 * (section["radius_mm"] - r_min) / (r_max - r_min)
        section["angle_deg"] = angle_expected
        section["lateral_index"] = np.arange(1, 42)

        z = section["z_mm"].to_numpy(float)
        # Stable sorting gives a fully declared deterministic rank control.
        order = np.argsort(z, kind="mergesort")
        sorted_z = z[order]
        exact_ties = np.r_[np.diff(sorted_z) == 0.0, False]
        rank_of_index = np.empty(41, dtype=int)
        rank_of_index[order] = np.arange(1, 42)
        section["elevation_rank"] = rank_of_index
        section["exact_elevation_tie"] = False
        if exact_ties.any():
            for index in np.flatnonzero(exact_ties):
                value = sorted_z[index]
                tied = np.flatnonzero(z == value)
                section.loc[tied, "exact_elevation_tie"] = True

        for record in section.itertuples(index=False):
            rows.append(record._asdict())
        for elevation_rank in range(1, 42):
            selected = section[section["elevation_rank"] == elevation_rank]
            if len(selected) != 1:
                raise RuntimeError(
                    f"Rank {elevation_rank} at {angle_expected} is not unique; "
                    "the frozen exact-tie averaging branch would be required"
                )
            record = selected.iloc[0]
            other = section.loc[section.index != selected.index[0], "x_ara"].to_numpy(float)
            neighbour = float(np.min(np.abs(other - float(record["x_ara"]))))
            features.append(
                {
                    "angle_deg": angle_expected,
                    "elevation_rank": elevation_rank,
                    "path_type": "thalweg" if elevation_rank == 1 else "control",
                    "lateral_index": int(record["lateral_index"]),
                    "radius_mm": float(record["radius_mm"]),
                    "z_mm": float(record["z_mm"]),
                    "x_ara": float(record["x_ara"]),
                    "nearest_lateral_spacing_ara": neighbour,
                    "exact_elevation_tie": bool(record["exact_elevation_tie"]),
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(features)


def score_paths(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rank, group in features.groupby("elevation_rank", sort=True):
        x = group.sort_values("angle_deg")["x_ara"].to_numpy(float)
        for candidate, delta in CANDIDATES.items():
            score = whole_path_scores(x, delta)
            rows.append(
                {
                    "elevation_rank": int(rank),
                    "path_type": "thalweg" if rank == 1 else "control",
                    "candidate": candidate,
                    "increment_ara": delta,
                    **score,
                }
            )
    scores = pd.DataFrame(rows)
    for measure in ("local_score", "parent_score"):
        scores[f"{measure}_rank_within_candidate"] = scores.groupby("candidate")[measure].rank(
            method="min"
        )
    return scores


def return_profiles(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for rank, group in features.groupby("elevation_rank", sort=True):
        x = group.sort_values("angle_deg")["x_ara"].to_numpy(float)
        observed = {lag: float(np.median(d2(x[lag:], x[:-lag]))) for lag in LAGS}
        for candidate, delta in CANDIDATES.items():
            errors = []
            for lag in LAGS:
                predicted = float(d2(0.0, (lag * delta) % 2.0))
                error = abs(observed[lag] - predicted)
                errors.append(error)
                rows.append(
                    {
                        "elevation_rank": int(rank),
                        "path_type": "thalweg" if rank == 1 else "control",
                        "candidate": candidate,
                        "lag": lag,
                        "observed_return_ara": observed[lag],
                        "predicted_return_ara": predicted,
                        "absolute_error_ara": error,
                    }
                )
            rows.append(
                {
                    "elevation_rank": int(rank),
                    "path_type": "thalweg" if rank == 1 else "control",
                    "candidate": candidate,
                    "lag": "MAE",
                    "observed_return_ara": np.nan,
                    "predicted_return_ara": np.nan,
                    "absolute_error_ara": float(np.mean(errors)),
                }
            )
    return pd.DataFrame(rows)


def carrier_loss(x: np.ndarray, delta: float) -> float:
    return float(whole_path_scores(x, delta)["parent_score"])


def order_controls(thalweg_x: np.ndarray) -> dict:
    rng = np.random.default_rng(RNG_SEED)
    observed = carrier_loss(thalweg_x, PHI_INCREMENT)
    shuffled = np.empty(N_NULL)
    for draw in range(N_NULL):
        shuffled[draw] = carrier_loss(rng.permutation(thalweg_x), PHI_INCREMENT)
    reverse = carrier_loss(thalweg_x[::-1], PHI_INCREMENT)
    seam = [carrier_loss(np.roll(thalweg_x, -shift), PHI_INCREMENT) for shift in range(len(thalweg_x))]
    return {
        "observed": observed,
        "shuffle_median": float(np.median(shuffled)),
        "shuffle_95": [float(np.quantile(shuffled, 0.025)), float(np.quantile(shuffled, 0.975))],
        "shuffle_p_lower": float((1 + np.sum(shuffled <= observed)) / (N_NULL + 1)),
        "reverse": reverse,
        "seam_median": float(np.median(seam)),
        "seam_min": float(np.min(seam)),
        "seam_max": float(np.max(seam)),
        "shuffle_values": shuffled,
        "seam_values": np.asarray(seam),
    }


def free_increment(thalweg_x: np.ndarray) -> dict:
    grid = np.linspace(0.0, 1.0, 20_001)
    loss = np.array([carrier_loss(thalweg_x, delta) for delta in grid])
    index = int(np.argmin(loss))
    return {"increment_ara": float(grid[index]), "parent_loss_ara": float(loss[index])}


def plot_result(
    sections: pd.DataFrame,
    features: pd.DataFrame,
    scores: pd.DataFrame,
    order: dict,
    figure_path: Path,
) -> None:
    width, height = 1900, 1260
    image = Image.new("RGB", (width, height), "#f7f9fc")
    draw = ImageDraw.Draw(image)
    regular = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 22)
    small = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 18)
    title_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 34)
    panel_font = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 24)
    draw.text((70, 35), "T327 — ARA Phi circle-train river thalweg test", fill="#172033", font=title_font)

    panels = [(65, 110, 920, 610), (980, 110, 1835, 610), (65, 690, 920, 1190), (980, 690, 1835, 1190)]

    def frame(box, heading, xlabel, ylabel):
        left, top, right, bottom = box
        draw.rounded_rectangle(box, radius=14, fill="white", outline="#c8d0dc", width=2)
        draw.text((left + 22, top + 16), heading, fill="#172033", font=panel_font)
        plot = (left + 80, top + 70, right - 28, bottom - 62)
        draw.line((plot[0], plot[3], plot[2], plot[3]), fill="#596273", width=2)
        draw.line((plot[0], plot[1], plot[0], plot[3]), fill="#596273", width=2)
        draw.text((plot[0] + (plot[2] - plot[0]) // 2 - 80, bottom - 42), xlabel, fill="#343b49", font=small)
        draw.text((left + 12, top + 45), ylabel, fill="#343b49", font=small)
        return plot

    def xy(plot, x_value, y_value, xlim, ylim):
        px = plot[0] + (float(x_value) - xlim[0]) / (xlim[1] - xlim[0]) * (plot[2] - plot[0])
        py = plot[3] - (float(y_value) - ylim[0]) / (ylim[1] - ylim[0]) * (plot[3] - plot[1])
        return int(px), int(py)

    def polyline(plot, xs, ys, xlim, ylim, color, line_width=3):
        points = [xy(plot, xv, yv, xlim, ylim) for xv, yv in zip(xs, ys)]
        if len(points) > 1:
            draw.line(points, fill=color, width=line_width, joint="curve")
        for px, py in points:
            draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=color)

    # Panel 1: raw bed field and downstream paths.
    plot = frame(panels[0], "Raw bed slices and matched paths", "lateral ARA: inner 0 → outer 2", "downstream")
    z_min, z_max = float(sections["z_mm"].min()), float(sections["z_mm"].max())
    for row in sections.itertuples(index=False):
        px, py = xy(plot, row.x_ara, row.angle_deg, (0, 2), (10, 170))
        ratio = (row.z_mm - z_min) / max(z_max - z_min, 1e-12)
        color = (int(45 + 170 * ratio), int(80 + 120 * ratio), int(150 - 90 * ratio))
        draw.rectangle((px - 4, py - 4, px + 4, py + 4), fill=color)
    for rank in (2, 5, 10, 20, 30, 41):
        path = features[features["elevation_rank"] == rank].sort_values("angle_deg")
        polyline(plot, path["x_ara"], path["angle_deg"], (0, 2), (10, 170), "#a7adb7", 1)
    thalweg = features[features["elevation_rank"] == 1].sort_values("angle_deg")
    polyline(plot, thalweg["x_ara"], thalweg["angle_deg"], (0, 2), (10, 170), "#111111", 4)

    # Panel 2: observed thalweg and frozen carrier.
    plot = frame(panels[1], "Thalweg movement on ARA", "bend angle / downstream order", "ARA")
    x = thalweg["x_ara"].to_numpy(float)
    angles = thalweg["angle_deg"].to_numpy(float)
    phi_score = whole_path_scores(x, PHI_INCREMENT)
    sign = 1.0 if phi_score["parent_sign"] == "+" else -1.0
    horizons = np.arange(1, len(x) - 1)
    prediction = np.mod(x[1] + sign * horizons * PHI_INCREMENT, 2.0)
    ridge_y = xy(plot, 10, 1.0, (10, 170), (0, 2))[1]
    draw.line((plot[0], ridge_y, plot[2], ridge_y), fill="#9ba3af", width=2)
    polyline(plot, angles, x, (10, 170), (0, 2), "#2774b7", 4)
    polyline(plot, angles[2:], prediction, (10, 170), (0, 2), "#d87521", 3)
    draw.text((plot[0] + 12, plot[1] + 10), f"blue observed  |  orange Phi carrier ({phi_score['parent_sign']})", fill="#343b49", font=small)

    # Panel 3: candidate losses.
    plot = frame(panels[2], "Frozen parent-carrier candidates", "candidate", "loss")
    thalweg_scores = scores[scores["elevation_rank"] == 1].sort_values("parent_score")
    maximum = max(0.01, float(thalweg_scores["parent_score"].max()) * 1.12)
    count = len(thalweg_scores)
    bar_width = (plot[2] - plot[0]) / count
    for index, row in enumerate(thalweg_scores.itertuples(index=False)):
        left = plot[0] + index * bar_width + 5
        right = plot[0] + (index + 1) * bar_width - 5
        top = xy(plot, 0, row.parent_score, (0, 1), (0, maximum))[1]
        color = "#d87521" if row.candidate == "phi" else "#849bc2"
        draw.rectangle((int(left), top, int(right), plot[3]), fill=color)
        label = row.candidate.replace("fibonacci_", "fib_").replace("three_eighths", "3/8")
        draw.text((int(left), plot[3] + 6), label[:11], fill="#343b49", font=ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 13))

    # Panel 4: all ordered control paths.
    plot = frame(panels[3], "Phi: thalweg versus ordered controls", "elevation rank (1 = thalweg)", "loss")
    phi_paths = scores[scores["candidate"] == "phi"].sort_values("elevation_rank")
    y_max = max(float(phi_paths["parent_score"].max()), order["shuffle_95"][1]) * 1.1
    y_low = xy(plot, 1, order["shuffle_95"][0], (1, 41), (0, y_max))[1]
    y_high = xy(plot, 1, order["shuffle_95"][1], (1, 41), (0, y_max))[1]
    draw.rectangle((plot[0], y_high, plot[2], y_low), fill="#ece2f4")
    y_med = xy(plot, 1, order["shuffle_median"], (1, 41), (0, y_max))[1]
    draw.line((plot[0], y_med, plot[2], y_med), fill="#8f55a2", width=3)
    for row in phi_paths.itertuples(index=False):
        px, py = xy(plot, row.elevation_rank, row.parent_score, (1, 41), (0, y_max))
        radius = 7 if row.elevation_rank == 1 else 4
        color = "#111111" if row.elevation_rank == 1 else "#4caa78"
        draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=color)
    draw.text((plot[0] + 12, plot[1] + 10), "black thalweg  |  green controls  |  purple shuffle 95%", fill="#343b49", font=small)

    image.save(figure_path)


def main() -> None:
    sections, features = read_cross_sections()
    scores = score_paths(features)
    returns = return_profiles(features)

    thalweg = features[features["elevation_rank"] == 1].sort_values("angle_deg")
    thalweg_x = thalweg["x_ara"].to_numpy(float)
    order = order_controls(thalweg_x)
    free = free_increment(thalweg_x)

    thalweg_scores = scores[scores["elevation_rank"] == 1].sort_values("parent_score")
    parent_winner = str(thalweg_scores.iloc[0]["candidate"])
    local_winner = str(
        scores[scores["elevation_rank"] == 1].sort_values("local_score").iloc[0]["candidate"]
    )
    phi_row = scores[(scores["elevation_rank"] == 1) & (scores["candidate"] == "phi")].iloc[0]
    control_phi = scores[(scores["elevation_rank"] > 1) & (scores["candidate"] == "phi")]
    phi_control_rank = int(1 + np.sum(control_phi["parent_score"].to_numpy() < phi_row["parent_score"]))
    phi_control_percentile = 100.0 * phi_control_rank / 41.0

    return_mae = returns[returns["lag"] == "MAE"].copy()
    thalweg_return = return_mae[return_mae["elevation_rank"] == 1].sort_values("absolute_error_ara")
    return_winner = str(thalweg_return.iloc[0]["candidate"])
    phi_return = float(thalweg_return[thalweg_return["candidate"] == "phi"]["absolute_error_ara"].iloc[0])
    best_return = float(thalweg_return["absolute_error_ara"].min())

    nearest_rational_name = min(
        [name for name in CANDIDATES if name not in ("phi", "persistence", "ridge", "one_over_e", "silver_conjugate")],
        key=lambda name: abs(CANDIDATES[name] - PHI_INCREMENT),
    )
    nearest_rational = CANDIDATES[nearest_rational_name]
    candidate_separation = float(d2(PHI_INCREMENT, nearest_rational))
    raw_grain = float(thalweg["nearest_lateral_spacing_ara"].median())
    horizon_resolution = []
    for horizon in HORIZONS:
        separation = float(d2((horizon * PHI_INCREMENT) % 2.0, (horizon * nearest_rational) % 2.0))
        horizon_resolution.append(
            {"horizon": horizon, "separation_ara": separation, "resolves_raw_grain": bool(separation > raw_grain)}
        )
    first_resolved = next((row["horizon"] for row in horizon_resolution if row["resolves_raw_grain"]), None)

    fixed_index_persistence = []
    for lateral_index, group in sections.groupby("lateral_index", sort=True):
        x = group.sort_values("angle_deg")["x_ara"].to_numpy(float)
        fixed_index_persistence.append(float(np.median(d2(np.mod(np.diff(x), 2.0), 0.0))))

    gates = {
        "phi_parent_winner": parent_winner == "phi",
        "downstream_order_p_lt_0_05": order["shuffle_p_lower"] < 0.05,
        "thalweg_below_control_median": float(phi_row["parent_score"]) < float(control_phi["parent_score"].median()),
        "thalweg_best_ten_percent": phi_control_rank <= 4,
        "fibonacci_return_no_worse_than_best_fixed": math.isclose(phi_return, best_return, abs_tol=1e-12),
        "local_exact_phi_resolution": raw_grain < candidate_separation,
        "multistep_phi_resolution": first_resolved is not None,
    }
    substantive = [
        gates["phi_parent_winner"],
        gates["downstream_order_p_lt_0_05"],
        gates["thalweg_best_ten_percent"],
        gates["fibonacci_return_no_worse_than_best_fixed"],
    ]
    if all(substantive) and gates["multistep_phi_resolution"]:
        verdict = "SUPPORTED IN THIS THALWEG CUT"
    elif any(substantive):
        verdict = "PARTIAL / MIXED"
    elif not gates["multistep_phi_resolution"]:
        verdict = "INCONCLUSIVE — RESOLUTION"
    else:
        verdict = "NOT SUPPORTED"

    result = {
        "test_id": "T327-PHI-CIRCLE-TRAIN-THALWEG-v2",
        "protocol_sha256": sha256(PROTOCOL),
        "source_sha256": sha256(SOURCE),
        "verdict": verdict,
        "source_geometry": {
            "cross_sections": int(features["angle_deg"].nunique()),
            "points_per_cross_section": int(sections.groupby("angle_deg").size().iloc[0]),
            "angles_deg": sorted(features["angle_deg"].unique().tolist()),
            "thalweg_ties": int(thalweg["exact_elevation_tie"].sum()),
            "control_paths": 40,
        },
        "thalweg": {
            "local_winner": local_winner,
            "parent_winner": parent_winner,
            "phi_local_score": float(phi_row["local_score"]),
            "phi_local_positive": float(phi_row["local_positive"]),
            "phi_local_negative": float(phi_row["local_negative"]),
            "phi_local_sign": str(phi_row["local_sign"]),
            "phi_parent_score": float(phi_row["parent_score"]),
            "phi_parent_positive": float(phi_row["parent_positive"]),
            "phi_parent_negative": float(phi_row["parent_negative"]),
            "phi_parent_sign": str(phi_row["parent_sign"]),
            "phi_control_rank_of_41": phi_control_rank,
            "phi_control_percentile": phi_control_percentile,
            "control_phi_median": float(control_phi["parent_score"].median()),
            "return_winner": return_winner,
            "phi_return_mae": phi_return,
            "best_return_mae": best_return,
            "free_increment_diagnostic": free,
        },
        "order_controls": {key: value for key, value in order.items() if key not in ("shuffle_values", "seam_values")},
        "resolution": {
            "nearest_fixed_rational": nearest_rational_name,
            "phi_increment_ara": PHI_INCREMENT,
            "nearest_rational_increment_ara": nearest_rational,
            "candidate_separation_ara": candidate_separation,
            "median_raw_lateral_neighbour_spacing_ara": raw_grain,
            "horizons": horizon_resolution,
            "first_resolved_horizon": first_resolved,
        },
        "fixed_index_persistence": {
            "paths": len(fixed_index_persistence),
            "median_local_persistence_loss": float(np.median(fixed_index_persistence)),
            "maximum_local_persistence_loss": float(np.max(fixed_index_persistence)),
        },
        "gates": gates,
    }

    sections.to_csv(HERE / f"{PREFIX}_CROSS_SECTIONS.csv", index=False)
    features.to_csv(HERE / f"{PREFIX}_PATH_POSITIONS.csv", index=False)
    scores.to_csv(HERE / f"{PREFIX}_PATH_SCORES.csv", index=False)
    returns.to_csv(HERE / f"{PREFIX}_RETURN_PROFILES.csv", index=False)
    pd.DataFrame({"shuffle_phi_parent_loss": order["shuffle_values"]}).to_csv(
        HERE / f"{PREFIX}_SHUFFLE_NULL.csv", index=False
    )
    pd.DataFrame(
        {"seam_shift": np.arange(len(order["seam_values"])), "phi_parent_loss": order["seam_values"]}
    ).to_csv(HERE / f"{PREFIX}_SEAM_SHIFTS.csv", index=False)
    with (HERE / f"{PREFIX}_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    figure_path = HERE / f"{PREFIX}_FIGURE.png"
    plot_result(sections, features, scores, order, figure_path)

    ranking = thalweg_scores[["candidate", "increment_ara", "parent_score", "parent_sign", "local_score", "local_sign"]]
    ranking_lines = "\n".join(
        f"| {row.candidate} | {row.increment_ara:.9f} | {row.parent_score:.6f} | {row.parent_sign} | {row.local_score:.6f} | {row.local_sign} |"
        for row in ranking.itertuples(index=False)
    )
    gate_lines = "\n".join(f"- `{key}`: **{value}**" for key, value in gates.items())
    report = f"""# T327 river thalweg Phi circle-train report

**Run date:** 2 August 2026  
**Frozen protocol:** `T327_PHI_CIRCLE_TRAIN_THALWEG_PROTOCOL_v2_FROZEN.md`  
**Verdict:** **{verdict}**

## Answer first

The exact T325 Phi carrier did **{'win' if parent_winner == 'phi' else 'not win'}** the fixed-candidate parent comparison on the deepest-bed path. The parent winner was **{parent_winner}**; the local-increment winner was **{local_winner}**. Phi's parent loss was `{float(phi_row['parent_score']):.6f}` ARA.

The real downstream order had lower-tail shuffle `p={order['shuffle_p_lower']:.6f}`. Among the same 41 downstream-ordered elevation-rank paths, the thalweg ranked **{phi_control_rank}/41** for the Phi parent carrier (1 is best); the 40-control median was `{float(control_phi['parent_score'].median()):.6f}`.

This is a direct path test, not a test of all river dynamics. The 40 controls are matched sections of the same bed and therefore establish feature specificity, not independent replication.

## Frozen candidate ranking on the thalweg

| candidate | increment ARA | parent loss | sign | local loss | sign |
|---|---:|---:|:---:|---:|:---:|
{ranking_lines}

## Downstream-order controls

- Observed Phi parent loss: `{order['observed']:.6f}`.
- 10,000-shuffle median: `{order['shuffle_median']:.6f}`; 95% interval `{order['shuffle_95'][0]:.6f}–{order['shuffle_95'][1]:.6f}`.
- Lower-tail permutation p-value: `{order['shuffle_p_lower']:.6f}`.
- Reversed path loss: `{order['reverse']:.6f}`.
- Circular seam-shift range: `{order['seam_min']:.6f}–{order['seam_max']:.6f}`.

## Resolution

The nearest tested fixed rational to Phi was **{nearest_rational_name}**. Their one-step separation is `{candidate_separation:.9f}` ARA, while the median raw neighbour spacing at the thalweg is `{raw_grain:.9f}` ARA. The local exact-constant claim is therefore **{'eligible' if gates['local_exact_phi_resolution'] else 'not resolution-eligible'}**. The first declared horizon that separates the two beyond that raw grain is **{first_resolved if first_resolved is not None else 'none'}**.

## Frozen gates

{gate_lines}

## Boundaries

- Inner bank `0` and outer bank `2` are the predeclared ARA orientation.
- One sign is selected for the complete path; signs are not changed event by event.
- No smoothing, fitted thalweg, interpolation, Fourier transform, or after-result rotation was used.
- A free increment was diagnostic only: `{free['increment_ara']:.6f}` with parent loss `{free['parent_loss_ara']:.6f}`.
- Fixed lateral-index paths have zero local movement by construction; their median persistence loss was `{float(np.median(fixed_index_persistence)):.6f}`.
"""
    (HERE / f"{PREFIX}_REPORT_2026-08-02.md").write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
