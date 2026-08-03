#!/usr/bin/env python3
"""T335: frozen river/thalweg Irrationality Di-ARA test.

The analysis uses only native downstream planform positions from the public
bed-topography workbook.  It applies no smoothing, interpolation, Fourier
processing, fitted trajectory, Phi target, or after-result axis rotation.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "source_bedrock_bends" / "Bed-topography.xlsx"
PROTOCOL = BASE / "T335_RIVER_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"
RESULTS_DIR = BASE / "results"
STEM = "T335_RIVER_IRRATIONALITY_DI_ARA"

PROTOCOL_HASH = "9724EA029D2A4A51A28149D1C6639CC55964A7F3DF0F37FE0D7B02F5A4953C72"
SOURCE_HASH = "041FBFF2233E590AECFD9A5DFC08C84C5A17678A8DF1ABDAC667A21A2D823ED7"
N_NULL = 1_000
RNG_SEED = 335
RIDGE_TOL = 1e-12
SECTORS = ("Ba", "Ab", "bA", "aB")
SPLITS = ("calibration", "evaluation", "holdout")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def split_for_angle(angle: int) -> str:
    if 15 <= angle <= 60:
        return "calibration"
    if 65 <= angle <= 110:
        return "evaluation"
    if 115 <= angle <= 165:
        return "holdout"
    raise ValueError(f"Unexpected middle angle {angle}")


def read_feature_paths() -> pd.DataFrame:
    raw = pd.read_excel(SOURCE)
    if raw.shape != (1666, 3):
        raise RuntimeError(f"Unexpected source shape {raw.shape}")
    raw.columns = ["x_mm", "y_mm", "z_mm"]

    records: list[dict] = []
    for block_index, expected_angle in zip(range(2, 35), range(10, 175, 5)):
        section = raw.iloc[block_index * 41 : (block_index + 1) * 41].copy()
        if len(section) != 41:
            raise RuntimeError(f"Section {expected_angle} has {len(section)} rows")
        observed_angle = np.degrees(np.arctan2(section["y_mm"], section["x_mm"]))
        if float(np.max(np.abs(observed_angle - expected_angle))) > 1e-5:
            raise RuntimeError(f"Coordinate angle mismatch at {expected_angle}")
        section["radius_mm"] = np.hypot(section["x_mm"], section["y_mm"])
        section = section.sort_values("radius_mm", kind="mergesort").reset_index(drop=True)
        section["lateral_index"] = np.arange(1, 42)
        z = section["z_mm"].to_numpy(float)
        order = np.argsort(z, kind="mergesort")
        rank_of_index = np.empty(41, dtype=int)
        rank_of_index[order] = np.arange(1, 42)
        section["elevation_rank"] = rank_of_index
        for row in section.itertuples(index=False):
            records.append(
                {
                    "angle_deg": expected_angle,
                    "elevation_rank": int(row.elevation_rank),
                    "path_type": "thalweg" if int(row.elevation_rank) == 1 else "control",
                    "lateral_index": int(row.lateral_index),
                    "x_mm": float(row.x_mm),
                    "y_mm": float(row.y_mm),
                    "z_mm": float(row.z_mm),
                    "radius_mm": float(row.radius_mm),
                }
            )
    features = pd.DataFrame(records)
    if len(features) != 33 * 41:
        raise RuntimeError(f"Expected 1353 features, found {len(features)}")
    return features


def build_steps(features: pd.DataFrame) -> tuple[dict[int, np.ndarray], np.ndarray]:
    steps: dict[int, np.ndarray] = {}
    expected_angles = np.arange(10, 175, 5, dtype=int)
    for rank in range(1, 42):
        path = features[features["elevation_rank"] == rank].sort_values("angle_deg")
        angles = path["angle_deg"].to_numpy(int)
        if not np.array_equal(angles, expected_angles):
            raise RuntimeError(f"Rank {rank} angle sequence is incomplete")
        positions = path["x_mm"].to_numpy(float) + 1j * path["y_mm"].to_numpy(float)
        differences = np.diff(positions)
        if np.any(np.abs(differences) <= 0):
            raise RuntimeError(f"Rank {rank} has a zero displacement")
        steps[rank] = differences
    return steps, expected_angles


def sector_for(scale: float, delta: float) -> str:
    if abs(math.log(scale)) <= RIDGE_TOL or abs(delta) <= RIDGE_TOL:
        return "boundary"
    if scale < 1 and delta > 0:
        return "Ba"
    if scale > 1 and delta > 0:
        return "Ab"
    if scale < 1 and delta < 0:
        return "bA"
    return "aB"


def event_from_q(
    q: complex,
    rank: int,
    event_index: int,
    middle_angle: int,
    source_kind: str,
) -> dict:
    scale = float(abs(q))
    delta = float(np.angle(q))
    x_ara = 2.0 * scale / (1.0 + scale)
    y_ara = 1.0 + delta / math.pi
    return {
        "source_kind": source_kind,
        "elevation_rank": rank,
        "path_type": "thalweg" if rank == 1 else "control",
        "event_index": event_index,
        "middle_angle_deg": middle_angle,
        "split": split_for_angle(middle_angle),
        "scale_ratio_s": scale,
        "turn_delta_rad": delta,
        "x_radial_ara": x_ara,
        "y_turn_ara": y_ara,
        "sector": sector_for(scale, delta),
    }


def build_observed_events(steps: dict[int, np.ndarray], angles: np.ndarray) -> pd.DataFrame:
    records: list[dict] = []
    middle_angles = angles[1:-1]
    for rank in range(1, 42):
        vector = steps[rank]
        quotients = vector[1:] / vector[:-1]
        for index, (angle, quotient) in enumerate(zip(middle_angles, quotients)):
            records.append(event_from_q(quotient, rank, index, int(angle), "observed"))
    return pd.DataFrame(records)


def build_broken_events(steps: dict[int, np.ndarray], angles: np.ndarray) -> pd.DataFrame:
    records: list[dict] = []
    middle_angles = angles[1:-1]
    for rank in range(1, 42):
        partner = rank + 1 if rank < 41 else 1
        quotients = steps[partner][1:] / steps[rank][:-1]
        for index, (angle, quotient) in enumerate(zip(middle_angles, quotients)):
            records.append(event_from_q(quotient, rank, index, int(angle), "broken_lineage"))
    return pd.DataFrame(records)


def build_reversed_events(steps: dict[int, np.ndarray], angles: np.ndarray) -> pd.DataFrame:
    records: list[dict] = []
    middle_angles = angles[1:-1][::-1]
    for rank in range(1, 42):
        reverse_steps = -steps[rank][::-1]
        quotients = reverse_steps[1:] / reverse_steps[:-1]
        for index, (angle, quotient) in enumerate(zip(middle_angles, quotients)):
            row = event_from_q(quotient, rank, index, int(angle), "reversed")
            row["split"] = "reverse_audit"
            records.append(row)
    return pd.DataFrame(records)


def endpoint(values: np.ndarray, alpha: float | None = None) -> dict:
    values = np.asarray(values, dtype=float)
    low = values[values < 1.0 - RIDGE_TOL]
    high = values[values > 1.0 + RIDGE_TOL]
    if len(low) == 0 or len(high) == 0:
        return {
            "n": int(len(values)),
            "n_contraction": int(len(low)),
            "n_expansion": int(len(high)),
            "s_minus": None,
            "s_plus": None,
            "product": None,
            "implied_alpha": None,
            "endpoint_loss": None,
        }
    log_low = float(np.median(np.log(low)))
    log_high = float(np.median(np.log(high)))
    s_minus = float(np.median(low))
    s_plus = float(np.median(high))
    implied_alpha = float(math.exp((log_high - log_low) / 2.0))
    loss = None
    if alpha is not None:
        loss = 0.5 * (abs(log_low + math.log(alpha)) + abs(log_high - math.log(alpha)))
    return {
        "n": int(len(values)),
        "n_contraction": int(len(low)),
        "n_expansion": int(len(high)),
        "s_minus": s_minus,
        "s_plus": s_plus,
        "product": s_minus * s_plus,
        "implied_alpha": implied_alpha,
        "endpoint_loss": float(loss) if loss is not None else None,
    }


def endpoint_rows(
    observed: pd.DataFrame,
    broken: pd.DataFrame,
    alpha_cal: float,
) -> pd.DataFrame:
    records: list[dict] = []
    populations = [
        ("field", observed),
        ("thalweg", observed[observed["elevation_rank"] == 1]),
        ("broken_field", broken),
        ("broken_thalweg", broken[broken["elevation_rank"] == 1]),
    ]
    for name, frame in populations:
        for split in (*SPLITS, "pooled"):
            part = frame if split == "pooled" else frame[frame["split"] == split]
            records.append(
                {
                    "population": name,
                    "split": split,
                    **endpoint(part["scale_ratio_s"].to_numpy(float), alpha_cal),
                }
            )
    return pd.DataFrame(records)


def quadrant_rows(observed: pd.DataFrame) -> pd.DataFrame:
    records: list[dict] = []
    for population, frame in (
        ("field", observed),
        ("thalweg", observed[observed["elevation_rank"] == 1]),
    ):
        for split in (*SPLITS, "pooled"):
            part = frame if split == "pooled" else frame[frame["split"] == split]
            nonboundary = part[part["sector"] != "boundary"]
            denominator = len(nonboundary)
            for name in SECTORS:
                count = int((nonboundary["sector"] == name).sum())
                records.append(
                    {
                        "population": population,
                        "split": split,
                        "sector": name,
                        "count": count,
                        "nonboundary_n": denominator,
                        "share_nonboundary": count / denominator if denominator else None,
                    }
                )
            records.append(
                {
                    "population": population,
                    "split": split,
                    "sector": "boundary",
                    "count": int((part["sector"] == "boundary").sum()),
                    "nonboundary_n": denominator,
                    "share_nonboundary": None,
                }
            )
    return pd.DataFrame(records)


def path_score_rows(observed: pd.DataFrame, alpha_cal: float) -> pd.DataFrame:
    records: list[dict] = []
    for split in SPLITS:
        for rank in range(1, 42):
            values = observed[
                (observed["split"] == split) & (observed["elevation_rank"] == rank)
            ]["scale_ratio_s"].to_numpy(float)
            records.append(
                {
                    "split": split,
                    "elevation_rank": rank,
                    "path_type": "thalweg" if rank == 1 else "control",
                    **endpoint(values, alpha_cal),
                }
            )
    frame = pd.DataFrame(records)
    frame["loss_rank"] = frame.groupby("split")["endpoint_loss"].rank(method="min")
    return frame


def shuffled_scale_values(
    steps: dict[int, np.ndarray],
    rng: np.random.Generator,
) -> np.ndarray:
    """Return one complete 41 x 31 scale field from one shuffled realization."""
    values: list[np.ndarray] = []
    for rank in range(1, 42):
        shuffled = steps[rank][rng.permutation(len(steps[rank]))]
        values.append(np.abs(shuffled[1:] / shuffled[:-1]))
    return np.stack(values)


def order_nulls(
    steps: dict[int, np.ndarray],
    alpha_cal: float,
    observed_endpoints: dict[tuple[str, str], dict],
) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(RNG_SEED)
    centers = np.arange(15, 170, 5)
    index_by_split = {
        split: np.flatnonzero(np.array([split_for_angle(int(a)) for a in centers]) == split)
        for split in ("evaluation", "holdout")
    }
    rows: list[dict] = []
    scores = {split: [] for split in index_by_split}
    for draw in range(N_NULL):
        shuffled_field = shuffled_scale_values(steps, rng)
        for split, indices in index_by_split.items():
            values = shuffled_field[:, indices].reshape(-1)
            record = endpoint(values, alpha_cal)
            score = float(record["endpoint_loss"])
            scores[split].append(score)
            rows.append({"draw": draw, "split": split, "endpoint_loss": score})
    summary = {}
    for split, values in scores.items():
        array = np.asarray(values, dtype=float)
        observed_score = float(observed_endpoints[("field", split)]["endpoint_loss"])
        summary[split] = {
            "observed_endpoint_loss": observed_score,
            "null_median": float(np.median(array)),
            "null_95": [float(np.quantile(array, 0.025)), float(np.quantile(array, 0.975))],
            "empirical_p_lower": float((1 + np.sum(array <= observed_score)) / (N_NULL + 1)),
        }
    return pd.DataFrame(rows), summary


def reverse_audit(observed: pd.DataFrame, reversed_events: pd.DataFrame) -> dict:
    maximum_scale_error = 0.0
    maximum_delta_error = 0.0
    matches = 0
    total = 0
    diagonal_map = {"Ab": "bA", "bA": "Ab", "aB": "Ba", "Ba": "aB", "boundary": "boundary"}
    for rank in range(1, 42):
        forward = observed[observed["elevation_rank"] == rank].sort_values("event_index")
        reverse = reversed_events[reversed_events["elevation_rank"] == rank].sort_values("event_index")
        expected_scale = 1.0 / forward["scale_ratio_s"].to_numpy(float)[::-1]
        expected_delta = -forward["turn_delta_rad"].to_numpy(float)[::-1]
        actual_scale = reverse["scale_ratio_s"].to_numpy(float)
        actual_delta = reverse["turn_delta_rad"].to_numpy(float)
        maximum_scale_error = max(maximum_scale_error, float(np.max(np.abs(expected_scale - actual_scale))))
        maximum_delta_error = max(maximum_delta_error, float(np.max(np.abs(expected_delta - actual_delta))))
        expected_sector = [diagonal_map[value] for value in forward["sector"].tolist()[::-1]]
        actual_sector = reverse["sector"].tolist()
        matches += sum(a == b for a, b in zip(expected_sector, actual_sector))
        total += len(expected_sector)
    return {
        "maximum_reciprocal_scale_error": maximum_scale_error,
        "maximum_turn_sign_error_rad": maximum_delta_error,
        "sector_diagonal_reflection_matches": matches,
        "sector_diagonal_reflection_total": total,
        "sector_diagonal_reflection_share": matches / total,
    }


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def json_value(value):
    if isinstance(value, dict):
        return {str(key): json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        number = float(value)
        return number if math.isfinite(number) else None
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    return value


def font(size: int, bold: bool = False):
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def make_figure(
    features: pd.DataFrame,
    observed: pd.DataFrame,
    quadrants: pd.DataFrame,
    endpoints: pd.DataFrame,
    path_scores: pd.DataFrame,
    null_summary: dict,
    gates: dict,
    output: Path,
) -> None:
    width, height = 1800, 1450
    image = Image.new("RGB", (width, height), "#f7f8fa")
    draw = ImageDraw.Draw(image)
    ink, muted, grid = "#172033", "#5d6978", "#d9dee5"
    blue, gold, orange, pink = "#4f7dbd", "#d99b2b", "#d36d3d", "#a85d83"
    title_f, sub_f = font(48, True), font(24),
    panel_f, body_f, small_f = font(28, True), font(19), font(16)
    draw.text((60, 32), "T335 — river/thalweg Irrationality Di-ARA", fill=ink, font=title_f)
    draw.text(
        (60, 92),
        "Native downstream planform quotients · contraction/expansion × signed turning · no Phi target",
        fill=muted,
        font=sub_f,
    )

    panels = [
        (55, 150, 870, 735),
        (930, 150, 1745, 735),
        (55, 790, 870, 1370),
        (930, 790, 1745, 1370),
    ]
    for box in panels:
        draw.rounded_rectangle(box, radius=18, fill="#ffffff", outline=grid, width=2)

    # Panel 1: source paths.
    box = panels[0]
    draw.text((box[0] + 24, box[1] + 18), "River coordinates and declared thalweg", fill=ink, font=panel_f)
    draw.text((box[0] + 24, box[1] + 58), "Gold = minimum-bed rank 1; blue = 40 matched elevation-rank controls", fill=muted, font=small_f)
    plot = (box[0] + 65, box[1] + 100, box[2] - 40, box[3] - 55)
    x_all = features["x_mm"].to_numpy(float)
    y_all = features["y_mm"].to_numpy(float)
    xmin, xmax = float(x_all.min()), float(x_all.max())
    ymin, ymax = float(y_all.min()), float(y_all.max())
    def river_xy(x, y):
        px = plot[0] + (x - xmin) / (xmax - xmin) * (plot[2] - plot[0])
        py = plot[3] - (y - ymin) / (ymax - ymin) * (plot[3] - plot[1])
        return int(px), int(py)
    for rank in range(2, 42):
        path = features[features["elevation_rank"] == rank].sort_values("angle_deg")
        points = [river_xy(row.x_mm, row.y_mm) for row in path.itertuples(index=False)]
        draw.line(points, fill="#b7c8df", width=1)
    thalweg = features[features["elevation_rank"] == 1].sort_values("angle_deg")
    thalweg_points = [river_xy(row.x_mm, row.y_mm) for row in thalweg.itertuples(index=False)]
    draw.line(thalweg_points, fill=gold, width=5)
    for point in thalweg_points[::4]:
        draw.ellipse((point[0]-4, point[1]-4, point[0]+4, point[1]+4), fill=gold, outline=ink)
    draw.text((plot[0], plot[3] + 16), "downstream: 10° → 170°", fill=muted, font=small_f)

    # Panel 2: Di-ARA plane.
    box = panels[1]
    draw.text((box[0] + 24, box[1] + 18), "Native Di-ARA plane", fill=ink, font=panel_f)
    draw.text((box[0] + 24, box[1] + 58), "X = radial scale ratio on 0–2; Y = signed turn on 0–2", fill=muted, font=small_f)
    plot = (box[0] + 75, box[1] + 105, box[2] - 45, box[3] - 65)
    def ara_xy(x, y):
        return (
            int(plot[0] + x / 2 * (plot[2] - plot[0])),
            int(plot[3] - y / 2 * (plot[3] - plot[1])),
        )
    for tick in (0, 0.5, 1, 1.5, 2):
        x = ara_xy(tick, 0)[0]
        y = ara_xy(0, tick)[1]
        draw.line((x, plot[1], x, plot[3]), fill=grid, width=1)
        draw.line((plot[0], y, plot[2], y), fill=grid, width=1)
        draw.text((x - 10, plot[3] + 7), f"{tick:g}", fill=muted, font=small_f)
        draw.text((plot[0] - 35, y - 8), f"{tick:g}", fill=muted, font=small_f)
    ridge_x = ara_xy(1, 0)[0]
    ridge_y = ara_xy(0, 1)[1]
    draw.line((ridge_x, plot[1], ridge_x, plot[3]), fill=ink, width=2)
    draw.line((plot[0], ridge_y, plot[2], ridge_y), fill=ink, width=2)
    draw.text((plot[0] + 15, plot[1] + 10), "Ba", fill=pink, font=panel_f)
    draw.text((plot[2] - 55, plot[1] + 10), "Ab", fill=orange, font=panel_f)
    draw.text((plot[0] + 15, plot[3] - 38), "bA", fill=blue, font=panel_f)
    draw.text((plot[2] - 55, plot[3] - 38), "aB", fill=gold, font=panel_f)
    field = observed[observed["elevation_rank"] != 1]
    for row in field.itertuples(index=False):
        px, py = ara_xy(row.x_radial_ara, row.y_turn_ara)
        draw.ellipse((px-2, py-2, px+2, py+2), fill="#b7c8df")
    path = observed[observed["elevation_rank"] == 1].sort_values("event_index")
    points = [ara_xy(row.x_radial_ara, row.y_turn_ara) for row in path.itertuples(index=False)]
    draw.line(points, fill=ink, width=3)
    split_colors = {"calibration": blue, "evaluation": orange, "holdout": pink}
    for row in path.itertuples(index=False):
        px, py = ara_xy(row.x_radial_ara, row.y_turn_ara)
        draw.ellipse((px-6, py-6, px+6, py+6), fill=split_colors[row.split], outline=ink)
    draw.text((plot[0], plot[3] + 24), "radial contraction  ←  1.0  →  expansion", fill=muted, font=small_f)
    draw.text((plot[0], plot[3] + 46), "thalweg: blue calibration · orange evaluation · pink holdout", fill=muted, font=small_f)

    # Panel 3: four-sector shares.
    box = panels[2]
    draw.text((box[0] + 24, box[1] + 18), "Four-sector occupancy", fill=ink, font=panel_f)
    draw.text((box[0] + 24, box[1] + 58), "Field shares in evaluation and untouched holdout; thalweg shown as points", fill=muted, font=small_f)
    plot = (box[0] + 75, box[1] + 105, box[2] - 45, box[3] - 85)
    for tick in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
        y = int(plot[3] - tick / 0.5 * (plot[3] - plot[1]))
        draw.line((plot[0], y, plot[2], y), fill=grid, width=1)
        draw.text((plot[0] - 50, y - 8), f"{tick:.0%}", fill=muted, font=small_f)
    group_w = (plot[2] - plot[0]) / 4
    bar_w = 45
    for index, name in enumerate(SECTORS):
        center = plot[0] + group_w * (index + 0.5)
        for offset, split, color in ((-28, "evaluation", orange), (28, "holdout", pink)):
            row = quadrants[(quadrants["population"] == "field") & (quadrants["split"] == split) & (quadrants["sector"] == name)].iloc[0]
            share = float(row["share_nonboundary"])
            top = int(plot[3] - share / 0.5 * (plot[3] - plot[1]))
            draw.rectangle((int(center+offset-bar_w/2), top, int(center+offset+bar_w/2), plot[3]), fill=color, outline=ink)
            trow = quadrants[(quadrants["population"] == "thalweg") & (quadrants["split"] == split) & (quadrants["sector"] == name)].iloc[0]
            tshare = float(trow["share_nonboundary"])
            ty = int(plot[3] - tshare / 0.5 * (plot[3] - plot[1]))
            draw.ellipse((int(center+offset-6), ty-6, int(center+offset+6), ty+6), fill="#ffffff", outline=ink, width=2)
        draw.text((int(center-14), plot[3] + 12), name, fill=ink, font=body_f)
    draw.rectangle((plot[0], plot[3] + 52, plot[0] + 20, plot[3] + 68), fill=orange)
    draw.text((plot[0] + 28, plot[3] + 49), "evaluation", fill=muted, font=small_f)
    draw.rectangle((plot[0] + 160, plot[3] + 52, plot[0] + 180, plot[3] + 68), fill=pink)
    draw.text((plot[0] + 188, plot[3] + 49), "holdout", fill=muted, font=small_f)
    draw.ellipse((plot[0] + 320, plot[3] + 51, plot[0] + 334, plot[3] + 65), fill="#ffffff", outline=ink, width=2)
    draw.text((plot[0] + 343, plot[3] + 49), "open point = thalweg share", fill=muted, font=small_f)

    # Panel 4: controls and gates.
    box = panels[3]
    draw.text((box[0] + 24, box[1] + 18), "Reciprocal closure and controls", fill=ink, font=panel_f)
    draw.text((box[0] + 24, box[1] + 58), "Endpoint loss to calibration-fitted reciprocal pair; lower is better", fill=muted, font=small_f)
    y = box[1] + 120
    endpoint_lookup = {(row.population, row.split): row for row in endpoints.itertuples(index=False)}
    path_lookup = path_scores[path_scores["elevation_rank"] == 1].set_index("split")
    for split, color in (("evaluation", orange), ("holdout", pink)):
        obs = endpoint_lookup[("field", split)]
        broken = endpoint_lookup[("broken_field", split)]
        null = null_summary[split]
        thalweg_row = path_lookup.loc[split]
        draw.text((box[0] + 40, y), split.upper(), fill=color, font=body_f)
        draw.text((box[0] + 180, y), f"field {obs.endpoint_loss:.4f}", fill=ink, font=body_f)
        draw.text((box[0] + 345, y), f"broken {broken.endpoint_loss:.4f}", fill=ink, font=body_f)
        draw.text((box[0] + 540, y), f"shuffle p={null['empirical_p_lower']:.3f}", fill=ink, font=body_f)
        draw.text((box[0] + 40, y + 38), f"field P={obs.product:.4f} · thalweg rank={int(thalweg_row.loss_rank)}/41", fill=muted, font=small_f)
        y += 100
    draw.line((box[0] + 30, y + 5, box[2] - 30, y + 5), fill=grid, width=2)
    y += 28
    gate_items = list(gates.items())
    for index, (gate, passed) in enumerate(gate_items):
        column = index // 4
        row = index % 4
        gx = box[0] + 40 + column * 390
        gy = y + row * 38
        if gate == "G0_integrity":
            marker = "SEE 17/17 VALIDATOR"
            color = muted
        else:
            marker = "PASS" if passed else "FAIL"
            color = blue if passed else pink
        short_gate = gate.replace("_", " ")
        draw.text((gx, gy), f"{short_gate}: {marker}", fill=color, font=small_f)
    draw.text((box[0] + 40, box[3] - 42), "Four sectors alone are descriptive; order, lineage and specificity are load-bearing.", fill=muted, font=small_f)

    draw.text((60, 1400), "Source: public bed-topography archive reused from T327 · 33 sections · 41 rank paths · 1,271 quotient events", fill=muted, font=small_f)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> None:
    if sha256(PROTOCOL) != PROTOCOL_HASH:
        raise SystemExit("Frozen protocol hash mismatch")
    if sha256(SOURCE) != SOURCE_HASH:
        raise SystemExit("Source workbook hash mismatch")

    features = read_feature_paths()
    steps, angles = build_steps(features)
    observed = build_observed_events(steps, angles)
    broken = build_broken_events(steps, angles)
    reversed_events = build_reversed_events(steps, angles)

    calibration = observed[observed["split"] == "calibration"]["scale_ratio_s"].to_numpy(float)
    alpha_cal = float(endpoint(calibration)["implied_alpha"])
    endpoints = endpoint_rows(observed, broken, alpha_cal)
    endpoint_lookup = {
        (row.population, row.split): row._asdict() for row in endpoints.itertuples(index=False)
    }
    quadrants = quadrant_rows(observed)
    path_scores = path_score_rows(observed, alpha_cal)
    nulls, null_summary = order_nulls(steps, alpha_cal, endpoint_lookup)
    reverse = reverse_audit(observed, reversed_events)

    quadrant_lookup = {
        (row.population, row.split, row.sector): row._asdict()
        for row in quadrants.itertuples(index=False)
    }
    field_eval_holdout = [
        quadrant_lookup[("field", split, name)]["share_nonboundary"]
        for split in ("evaluation", "holdout")
        for name in SECTORS
    ]
    g1 = all(value is not None and value >= 0.05 for value in field_eval_holdout)

    thalweg_pooled_sectors = sum(
        quadrant_lookup[("thalweg", "pooled", name)]["count"] > 0 for name in SECTORS
    )
    thalweg_split_sectors = {
        split: sum(quadrant_lookup[("thalweg", split, name)]["count"] > 0 for name in SECTORS)
        for split in ("evaluation", "holdout")
    }
    g2 = thalweg_pooled_sectors == 4 and all(value >= 3 for value in thalweg_split_sectors.values())

    field_products = {
        split: endpoint_lookup[("field", split)]["product"] for split in ("evaluation", "holdout")
    }
    thalweg_products = {
        split: endpoint_lookup[("thalweg", split)]["product"]
        for split in ("evaluation", "holdout", "pooled")
    }
    g3 = (
        all(value is not None and 0.90 <= value <= 1.10 for value in field_products.values())
        and thalweg_products["pooled"] is not None
        and 0.80 <= thalweg_products["pooled"] <= 1.20
        and all(
            thalweg_products[split] is not None and 0.75 <= thalweg_products[split] <= 1.25
            for split in ("evaluation", "holdout")
        )
    )

    implied = {
        split: endpoint_lookup[("field", split)]["implied_alpha"]
        for split in ("evaluation", "holdout")
    }
    g4 = all(
        value is not None and abs(math.log(value / alpha_cal)) <= math.log(1.10)
        for value in implied.values()
    )
    g5 = all(null_summary[split]["empirical_p_lower"] <= 0.05 for split in ("evaluation", "holdout"))
    g6 = all(
        endpoint_lookup[("field", split)]["endpoint_loss"]
        < endpoint_lookup[("broken_field", split)]["endpoint_loss"]
        for split in ("evaluation", "holdout")
    )

    thalweg_rows = path_scores[path_scores["elevation_rank"] == 1].set_index("split")
    control_medians = {
        split: float(
            path_scores[
                (path_scores["split"] == split) & (path_scores["elevation_rank"] > 1)
            ]["endpoint_loss"].median()
        )
        for split in ("evaluation", "holdout")
    }
    g7 = (
        all(
            float(thalweg_rows.loc[split, "endpoint_loss"]) < control_medians[split]
            for split in ("evaluation", "holdout")
        )
        and any(float(thalweg_rows.loc[split, "loss_rank"]) <= 4 for split in ("evaluation", "holdout"))
    )

    gates = {
        "G0_integrity": False,
        "G1_field_four_sectors": g1,
        "G2_thalweg_sector_coverage": g2,
        "G3_reciprocal_closure": g3,
        "G4_calibration_transfer": g4,
        "G5_recorded_order": g5,
        "G6_intact_rank_lineage": g6,
        "G7_thalweg_specificity": g7,
    }

    results = {
        "test": "T335 river/thalweg Irrationality Di-ARA",
        "date": "2026-08-03",
        "protocol": PROTOCOL.name,
        "protocol_sha256": PROTOCOL_HASH,
        "source": "Public bed-topography workbook reused from T327",
        "source_sha256": SOURCE_HASH,
        "counts": {
            "source_rows": 1666,
            "retained_sections": 33,
            "paths": 41,
            "events_per_path": 31,
            "observed_events": int(len(observed)),
            "split_events_field": observed.groupby("split").size().to_dict(),
            "split_events_thalweg": observed[observed["elevation_rank"] == 1].groupby("split").size().to_dict(),
            "boundary_events": int((observed["sector"] == "boundary").sum()),
        },
        "coordinate": {
            "radial": "X=2s/(1+s)",
            "turn": "Y=1+delta/pi",
            "reciprocal_identity": "X(1/s)=2-X(s)",
            "sector_map": {
                "Ba": "contracting_forward",
                "Ab": "expanding_forward",
                "bA": "contracting_reverse",
                "aB": "expanding_reverse",
            },
        },
        "alpha_cal": alpha_cal,
        "field_endpoints": {
            split: endpoint_lookup[("field", split)] for split in (*SPLITS, "pooled")
        },
        "thalweg_endpoints": {
            split: endpoint_lookup[("thalweg", split)] for split in (*SPLITS, "pooled")
        },
        "broken_field_endpoints": {
            split: endpoint_lookup[("broken_field", split)] for split in (*SPLITS, "pooled")
        },
        "quadrant_shares": {
            population: {
                split: {
                    name: quadrant_lookup[(population, split, name)]["share_nonboundary"]
                    for name in SECTORS
                }
                for split in (*SPLITS, "pooled")
            }
            for population in ("field", "thalweg")
        },
        "thalweg_sector_counts": {
            split: {
                name: int(quadrant_lookup[("thalweg", split, name)]["count"])
                for name in SECTORS
            }
            for split in (*SPLITS, "pooled")
        },
        "order_null": null_summary,
        "reverse_audit": reverse,
        "thalweg_control_comparison": {
            split: {
                "thalweg_endpoint_loss": float(thalweg_rows.loc[split, "endpoint_loss"]),
                "thalweg_rank_of_41": int(thalweg_rows.loc[split, "loss_rank"]),
                "control_median_endpoint_loss": control_medians[split],
            }
            for split in ("evaluation", "holdout")
        },
        "gates": gates,
        "verdict": {
            "field_di_ara_coordinate_supported": g1,
            "transferable_reciprocal_field_organisation_supported": g1 and g3 and g4,
            "ordered_same_lineage_field_mechanism_supported": all(gates[key] for key in (
                "G1_field_four_sectors", "G3_reciprocal_closure", "G4_calibration_transfer",
                "G5_recorded_order", "G6_intact_rank_lineage"
            )),
            "thalweg_specific_expression_supported": g2 and g3 and g7,
            "full_river_thalweg_claim_supported_pending_validation": all(
                value for key, value in gates.items() if key != "G0_integrity"
            ),
            "phi_supported": False,
        },
        "boundaries": [
            "The source was opened previously in T327; T335 is confirmatory reuse.",
            "Reciprocal scale ratios can partly reflect stationary step-size variation, so order and lineage controls are load-bearing.",
            "The flume bend can bias signed turning.",
            "Elevation ranks are geometric feature paths, not persistent water parcels.",
            "T335 contains no Phi or fixed-constant target.",
        ],
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(RESULTS_DIR / f"{STEM}_EVENTS.csv", pd.concat([observed, broken, reversed_events], ignore_index=True))
    write_csv(RESULTS_DIR / f"{STEM}_ENDPOINTS.csv", endpoints)
    write_csv(RESULTS_DIR / f"{STEM}_QUADRANTS.csv", quadrants)
    write_csv(RESULTS_DIR / f"{STEM}_PATH_SCORES.csv", path_scores)
    write_csv(RESULTS_DIR / f"{STEM}_ORDER_NULLS.csv", nulls)
    result_path = BASE / f"{STEM}_RESULTS.json"
    figure_path = BASE / f"{STEM}_FIGURE.png"
    result_path.write_text(json.dumps(json_value(results), indent=2, allow_nan=False), encoding="utf-8")
    make_figure(features, observed, quadrants, endpoints, path_scores, null_summary, gates, figure_path)
    print(json.dumps(json_value({
        "alpha_cal": alpha_cal,
        "field_endpoints": results["field_endpoints"],
        "thalweg_endpoints": results["thalweg_endpoints"],
        "quadrant_shares": results["quadrant_shares"],
        "order_null": null_summary,
        "reverse_audit": reverse,
        "thalweg_control_comparison": results["thalweg_control_comparison"],
        "gates": gates,
        "verdict": results["verdict"],
    }), indent=2))


if __name__ == "__main__":
    main()
