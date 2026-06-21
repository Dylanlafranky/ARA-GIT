"""
ara_recursive_sphere_grid_predictor.py

Sphere-only recursive ARA terrain test.

This is the clean version of the user's latest correction:

    We are not using the layered-sand "now formula" as the predictor.
    We are reading the measured sphere itself.

Rule:

    current measured sphere coordinate
    -> deterministic sphere rotation to future longitude
    -> if a close past recorded coordinate exists, read that raw terrain point
    -> otherwise read the filled recursive ARA/sub-ARA/sub-sub-ARA grid

The recursive grid is not sparse:

    every cell has a midline/boundary split
    every cell has a local phi valley
    every cell has a local anti-phi counterline
    each deeper level contributes with phi-log lower weight

No future-origin rows, shifted truth, lag regression, smoothing, or neighbour
averaging are used by the primary models.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np

from ara_geometry_transport_test import clean_for_json
from ara_raw_watershed_slice_test import rounded
from ara_sphere_orientation_roll_predictor import EPS
from ara_shape_kernel_test import PHI


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
OUT_JSON = HERE / "ara_recursive_sphere_grid_result.json"
OUT_JS = HERE / "ara_recursive_sphere_grid_result.js"

HOME = 47.0
HORIZONS = [3, 6, 12, 18, 24]
MAX_DEPTH = 7
OBSERVED_DISTANCE_THRESHOLD = 0.16
VALUE_SCALE = 1.5

MODEL_KEYS = [
    "persistence",
    "recorded_top1_any",
    "recorded_close_else_grid",
    "grid_phi_valley",
    "grid_phi_water",
]


def month_index(date_str):
    date = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
    return date.year * 12 + date.month - 1


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def value_to_ara(value):
    return clamp(1.0 + math.tanh(float(value) / VALUE_SCALE), 0.0, 2.0)


def ara_to_value(ara):
    x = clamp(float(ara) - 1.0, -0.985, 0.985)
    return float(VALUE_SCALE * np.arctanh(x))


def ara_y(ara):
    return 1.0 - clamp(ara, 0.0, 2.0)


def norm(vec):
    arr = np.asarray(vec, dtype=float)
    length = float(np.linalg.norm(arr))
    if length <= EPS:
        return arr
    return arr / length


def point3(ara, phase_deg):
    lon = math.radians(float(phase_deg) % 360.0)
    y = ara_y(ara)
    ring = math.sqrt(max(0.0, 1.0 - y * y))
    return np.asarray([ring * math.cos(lon), y, ring * math.sin(lon)], dtype=float)


def phase_to_ara(phase_deg):
    return 2.0 * ((float(phase_deg) % 360.0) / 360.0)


def phase_from_ara(phase_ara):
    return (clamp(phase_ara, 0.0, 2.0) / 2.0) * 360.0


def corr(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if len(xs) < 3 or np.std(xs) <= EPS or np.std(ys) <= EPS:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def score(rows, key):
    usable = [row for row in rows if row.get(key) is not None and np.isfinite(row.get(key))]
    if not usable:
        return {"n": 0, "mae": None, "corr": None, "direction": None, "amp_ratio": None, "corr_with_current": None}
    pred = np.asarray([row[key] for row in usable], dtype=float)
    actual = np.asarray([row["actual"] for row in usable], dtype=float)
    current = np.asarray([row["current"] for row in usable], dtype=float)
    truth_delta = actual - current
    pred_delta = pred - current
    mask = np.abs(truth_delta) > EPS
    return {
        "n": int(len(usable)),
        "mae": float(np.mean(np.abs(pred - actual))),
        "corr": corr(pred, actual),
        "direction": float(np.mean(np.sign(pred_delta[mask]) == np.sign(truth_delta[mask]))) if np.any(mask) else None,
        "amp_ratio": float(np.std(pred_delta) / np.std(truth_delta)) if np.std(truth_delta) > EPS else None,
        "corr_with_current": corr(pred, current),
    }


def binary_bounds(x, depth):
    lo = 0.0
    hi = 2.0
    address = []
    x = clamp(x, 0.0, 2.0)
    for _ in range(depth):
        mid = 0.5 * (lo + hi)
        if x < mid:
            hi = mid
            address.append(0)
        else:
            lo = mid
            address.append(1)
    return lo, hi, address


def local_lines(lo, hi):
    width = hi - lo
    # User diagram: root phi line is at 1.618 on a 0..2 axis, anti-phi at 0.382.
    phi_line = lo + width * (PHI / 2.0)
    anti_phi_line = lo + width * ((2.0 - PHI) / 2.0)
    midline = lo + 0.5 * width
    return phi_line, anti_phi_line, midline


def axis_recursive_read(x, max_depth=MAX_DEPTH):
    x = clamp(x, 0.0, 2.0)
    layers = []
    weights = []
    for depth in range(1, max_depth + 1):
        lo, hi, address = binary_bounds(x, depth - 1)
        width = max(hi - lo, EPS)
        phi_line, anti_phi_line, midline = local_lines(lo, hi)
        slope_to_phi = phi_line - x
        phi_distance = abs(slope_to_phi) / width
        anti_distance = abs(x - anti_phi_line) / width
        boundary_distance = min(abs(x - lo), abs(x - hi)) / width
        mid_distance = abs(x - midline) / width
        weight = 1.0 / (PHI ** (depth - 1))
        layers.append(
            {
                "depth": depth,
                "lo": lo,
                "hi": hi,
                "address": address,
                "phi": phi_line,
                "anti_phi": anti_phi_line,
                "midline": midline,
                "width": width,
                "slope_to_phi": slope_to_phi,
                "phi_distance": phi_distance,
                "anti_phi_distance": anti_distance,
                "boundary_distance": boundary_distance,
                "mid_distance": mid_distance,
                "weight": weight,
            }
        )
        weights.append(weight)
    weights = np.asarray(weights, dtype=float)
    weights = weights / float(np.sum(weights))
    slope = float(np.sum(weights * np.asarray([layer["slope_to_phi"] for layer in layers], dtype=float)))
    phi_target = float(np.sum(weights * np.asarray([layer["phi"] for layer in layers], dtype=float)))
    anti_pressure = float(
        np.sum(weights * np.asarray([1.0 - min(1.0, layer["anti_phi_distance"]) for layer in layers], dtype=float))
    )
    ridge_pressure = float(
        np.sum(weights * np.asarray([1.0 - min(1.0, layer["boundary_distance"] * 2.0) for layer in layers], dtype=float))
    )
    return {
        "x": x,
        "weighted_phi": clamp(phi_target, 0.0, 2.0),
        "weighted_slope_to_phi": slope,
        "anti_phi_pressure": anti_pressure,
        "ridge_pressure": ridge_pressure,
        "dominant_address": layers[0]["address"],
        "deep_address": layers[-1]["address"],
        "layers": layers,
    }


def recursive_grid_read(arrival_ara, arrival_phase, horizon):
    ara_axis = axis_recursive_read(arrival_ara)
    phase_axis = axis_recursive_read(phase_to_ara(arrival_phase))
    horizon_gain = clamp(float(horizon) / HOME, 0.04, 0.80)

    # Terrain is a filled grid. ARA-axis phi gives vertical water pull. Phase-axis
    # phi gives longitudinal terrain pressure and a smaller cross-pressure onto
    # measured ARA.
    vertical_pull = ara_axis["weighted_slope_to_phi"]
    phase_pull = phase_axis["weighted_slope_to_phi"]
    ridge_brake = 1.0 + 0.75 * ara_axis["ridge_pressure"] + 0.45 * phase_axis["ridge_pressure"]
    anti_pressure = 0.12 * (ara_axis["anti_phi_pressure"] - phase_axis["anti_phi_pressure"])
    water_step = horizon_gain * (1.0 + 0.55 * abs(vertical_pull) + 0.25 * abs(phase_pull)) / ridge_brake
    next_ara = arrival_ara + water_step * (vertical_pull + 0.28 * phase_pull + anti_pressure)
    valley_ara = ara_axis["weighted_phi"]
    valley_value = ara_to_value(valley_ara)
    water_value = ara_to_value(clamp(next_ara, 0.0, 2.0))
    return {
        "arrival_ara": float(arrival_ara),
        "arrival_phase": float(arrival_phase % 360.0),
        "phase_ara": float(phase_to_ara(arrival_phase)),
        "valley_ara": float(valley_ara),
        "water_ara": float(clamp(next_ara, 0.0, 2.0)),
        "valley_value": float(valley_value),
        "water_value": float(water_value),
        "vertical_pull": float(vertical_pull),
        "phase_pull": float(phase_pull),
        "water_step": float(water_step),
        "ridge_brake": float(ridge_brake),
        "ara_axis": ara_axis,
        "phase_axis": phase_axis,
    }


def build_samples(atlas):
    samples = []
    seen = set()
    for record in atlas["records_by_horizon"]["3"]:
        if record["origin"] in seen:
            continue
        seen.add(record["origin"])
        samples.append(
            {
                "date": record["origin"],
                "month": month_index(record["origin"]),
                "value": float(record["current"]),
                "ara": float(record["ara_current"]),
                "phase": float(record["phase_clock_origin"]),
                "coord": point3(record["ara_current"], record["phase_clock_origin"]),
            }
        )
    return samples


def read_top1(samples, query_coord, max_month):
    past = [sample for sample in samples if sample["month"] <= max_month]
    if not past:
        return None
    q = np.asarray(query_coord, dtype=float)
    distances = [float(np.linalg.norm(q - sample["coord"])) for sample in past]
    idx = int(np.argmin(distances))
    sample = past[idx]
    return {
        "value": float(sample["value"]),
        "distance": float(distances[idx]),
        "date": sample["date"],
        "ara": float(sample["ara"]),
        "phase": float(sample["phase"]),
    }


def predict_row(row, samples, horizon):
    origin_month = month_index(row["origin"])
    arrival_ara = float(row["ara_current"])
    arrival_phase = (float(row["phase_clock_origin"]) + (float(horizon) / HOME) * 360.0) % 360.0
    query = point3(arrival_ara, arrival_phase)
    top1 = read_top1(samples, query, origin_month)
    grid = recursive_grid_read(arrival_ara, arrival_phase, horizon)
    use_recorded = bool(top1 and top1["distance"] <= OBSERVED_DISTANCE_THRESHOLD)
    return {
        "recorded_top1_any": top1["value"] if top1 else float(row["current"]),
        "recorded_close_else_grid": top1["value"] if use_recorded else grid["water_value"],
        "grid_phi_valley": grid["valley_value"],
        "grid_phi_water": grid["water_value"],
        "used_recorded_close": use_recorded,
        "recorded_lookup": top1,
        "grid": grid,
        "arrival_ara": arrival_ara,
        "arrival_phase": arrival_phase,
    }


def run():
    atlas = json.loads(IN_JSON.read_text(encoding="utf-8"))
    samples = build_samples(atlas)
    records_by_h = {}
    scores = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA recursive sphere grid predictor")
    print("=" * 100)
    print("No layered-sand now formula. Measured sphere coordinate -> rotation -> recorded point or recursive grid.")
    print()

    for horizon in HORIZONS:
        hkey = str(horizon)
        rows = []
        for source in atlas["records_by_horizon"][hkey]:
            pred = predict_row(source, samples, horizon)
            row = {
                "origin": source["origin"],
                "target": source["target"],
                "horizon": int(horizon),
                "current": rounded(source["current"]),
                "actual": rounded(source["actual"]),
                "persistence": rounded(source["current"]),
                "recorded_top1_any": rounded(pred["recorded_top1_any"]),
                "recorded_close_else_grid": rounded(pred["recorded_close_else_grid"]),
                "grid_phi_valley": rounded(pred["grid_phi_valley"]),
                "grid_phi_water": rounded(pred["grid_phi_water"]),
                "used_recorded_close": pred["used_recorded_close"],
                "arrival_ara": rounded(pred["arrival_ara"]),
                "arrival_phase": rounded(pred["arrival_phase"]),
                "recorded_lookup": clean_for_json(pred["recorded_lookup"]),
                "grid": clean_for_json(
                    {
                        "valley_ara": pred["grid"]["valley_ara"],
                        "water_ara": pred["grid"]["water_ara"],
                        "vertical_pull": pred["grid"]["vertical_pull"],
                        "phase_pull": pred["grid"]["phase_pull"],
                        "water_step": pred["grid"]["water_step"],
                        "ridge_brake": pred["grid"]["ridge_brake"],
                        "ara_deep_address": pred["grid"]["ara_axis"]["deep_address"],
                        "phase_deep_address": pred["grid"]["phase_axis"]["deep_address"],
                    }
                ),
            }
            rows.append(row)
        records_by_h[hkey] = rows
        for key in MODEL_KEYS:
            scores[key][hkey] = score(rows, key)
        diagnostics[hkey] = {
            "recorded_close_rate": float(np.mean([row["used_recorded_close"] for row in rows])),
            "mean_top1_distance": float(
                np.mean([row["recorded_lookup"]["distance"] for row in rows if row["recorded_lookup"]])
            ),
            "mean_abs_vertical_pull": float(np.mean([abs(row["grid"]["vertical_pull"]) for row in rows])),
            "mean_abs_phase_pull": float(np.mean([abs(row["grid"]["phase_pull"]) for row in rows])),
            "mean_water_step": float(np.mean([row["grid"]["water_step"] for row in rows])),
        }

        line = [f"h={horizon:>2}m"]
        for key in MODEL_KEYS:
            sc = scores[key][hkey]
            line.append(f"{key}: corr={rounded(sc['corr']) if sc['corr'] is not None else 'n/a'} mae={rounded(sc['mae'])}")
        print(" | ".join(line))

    result = {
        "date": "2026-05-26",
        "method": "Sphere-only recursive ARA/sub-ARA/sub-sub-ARA grid predictor",
        "source_atlas": str(IN_JSON.name),
        "home_period_months": HOME,
        "max_depth": MAX_DEPTH,
        "observed_distance_threshold": OBSERVED_DISTANCE_THRESHOLD,
        "leakage_rules": [
            "No layered-sand now formula is used.",
            "No future-origin row is read.",
            "No future target value is read until scoring.",
            "Past recorded coordinate lookup is raw top-1 only.",
            "If the top-1 recorded coordinate is not close, the filled recursive grid is read instead.",
        ],
        "grid_definition": {
            "axis_range": "0..2",
            "root_phi": PHI,
            "root_anti_phi": 2.0 - PHI,
            "midline": 1.0,
            "depth_weight": "1 / phi^(depth - 1)",
            "cell_rule": "split current cell by midpoint; each cell receives local phi and anti-phi lines",
            "terrain_rule": "energy/water moves toward the local weighted phi valley unless ridge/counter pressure brakes it",
        },
        "model_keys": MODEL_KEYS,
        "scores": scores,
        "diagnostics": diagnostics,
        "records_by_horizon": records_by_h,
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(result), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_RECURSIVE_SPHERE_GRID = " + json.dumps(clean_for_json(result), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print()
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
