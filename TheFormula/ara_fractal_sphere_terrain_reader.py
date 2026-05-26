"""
ara_fractal_sphere_terrain_reader.py

Strict-causal test of the filled ARA-sphere terrain idea.

The prior raw-address lookup still treated the sphere as a sparse historical
point cloud. This version separates:

    pose / roll:
        current surface state -> predicted future sphere coordinate

    terrain reader:
        future coordinate -> recursive ARA band/sub-band address
        -> nearest in-bounds phi valley
        -> ridge/spillover response

Historical rows are used to learn the future pose, but not to define the
terrain under that pose. The terrain is deterministic and filled: there is no
blank space between old observations.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ara_geometry_transport_test import clean_for_json
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, rounded
from ara_sphere_orientation_roll_predictor import (
    EPS,
    HORIZONS,
    MIN_LEARN_TRAIN,
    RIDGE_ALPHA,
    completed_motion_candidates,
    fit_ridge,
    predict_ridge,
    roll_terms,
    row_surface_vec,
    row_target_vec,
    sign,
    surface_features,
    unit,
    vec_to_ara,
)
from ara_sphere_topology_direction_predictor import month_index
from ara_shape_kernel_test import PHI


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
RAW_ADDRESS_JSON = HERE / "ara_raw_terrain_address_lookup_result.json"
ORIENTATION_JSON = HERE / "ara_sphere_orientation_roll_result.json"
OUT_JSON = HERE / "ara_fractal_sphere_terrain_reader_result.json"
OUT_JS = HERE / "ara_fractal_sphere_terrain_reader_result.js"

MAX_TERRAIN_DEPTH = 6
VALUE_SCALE = 1.5

MODEL_KEYS = [
    "persistence",
    "wobble_surface_analog",
    "roll_learned_average",
    "raw_address_top1",
    "fractal_phi_depth1",
    "fractal_phi_depth2",
    "fractal_phi_depth3",
    "fractal_phi_direct",
    "fractal_phi_settle",
    "fractal_phi_force",
    "fractal_phi_spill",
]


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def clamp_ara(value):
    return clamp(value, 0.0, 2.0)


def value_to_ara(value):
    return clamp_ara(1.0 + math.tanh(float(value) / VALUE_SCALE))


def ara_to_value(ara):
    x = clamp(float(ara) - 1.0, -0.985, 0.985)
    return float(VALUE_SCALE * np.arctanh(x))


def sigmoid(value):
    value = clamp(value, -60.0, 60.0)
    return float(1.0 / (1.0 + math.exp(-value)))


def binary_bounds(ara, depth):
    lo = 0.0
    hi = 2.0
    x = clamp_ara(ara)
    address = []
    for _ in range(depth):
        mid = 0.5 * (lo + hi)
        if x < mid:
            hi = mid
            address.append(0)
        else:
            lo = mid
            address.append(1)
    return lo, hi, address


def local_phi_points(lo, hi):
    width = hi - lo
    lower_phi = hi - width / PHI
    upper_phi = lo + width / PHI
    return lower_phi, upper_phi


def choose_local_phi(ara, lo, hi, orientation):
    lower_phi, upper_phi = local_phi_points(lo, hi)
    lower_dist = abs(ara - lower_phi)
    upper_dist = abs(ara - upper_phi)
    if abs(lower_dist - upper_dist) <= 1e-8:
        return upper_phi if orientation >= 0 else lower_phi
    return lower_phi if lower_dist < upper_dist else upper_phi


def layer_terrain_read(ara, roll_delta, force, depth):
    lo, hi, address = binary_bounds(ara, depth)
    width = hi - lo
    orientation = sign(roll_delta)
    target = choose_local_phi(ara, lo, hi, orientation)
    natural_slope = target - ara
    natural_sign = sign(natural_slope) or orientation or 1

    boundary = hi if natural_sign > 0 else lo
    ridge_distance = abs(boundary - ara)
    ridge_resistance = clamp(ridge_distance / max(width, EPS), 0.0, 1.0)
    force_scaled = abs(float(force)) / max(width, EPS)
    spillover = sigmoid(3.2 * (force_scaled - ridge_resistance - 0.28))

    next_mid = clamp_ara(ara + natural_sign * width)
    next_lo, next_hi, _ = binary_bounds(next_mid, depth)
    next_target = choose_local_phi(clamp(next_mid, next_lo, next_hi), next_lo, next_hi, natural_sign)

    target_with_spill = (1.0 - spillover) * target + spillover * next_target
    return {
        "depth": depth,
        "lo": lo,
        "hi": hi,
        "width": width,
        "address": address,
        "local_phi_lower": local_phi_points(lo, hi)[0],
        "local_phi_upper": local_phi_points(lo, hi)[1],
        "target": target,
        "target_with_spill": clamp_ara(target_with_spill),
        "slope": target - ara,
        "slope_with_spill": target_with_spill - ara,
        "ridge_distance": ridge_distance,
        "ridge_resistance": ridge_resistance,
        "spillover": spillover,
        "next_lo": next_lo,
        "next_hi": next_hi,
        "next_target": next_target,
    }


def read_fractal_terrain(arrival_ara, current_ara, terms, max_depth=MAX_TERRAIN_DEPTH):
    ara = clamp_ara(arrival_ara)
    roll_delta = ara - clamp_ara(current_ara)
    contact_pressure = abs(float(terms["contact_pressure"]))
    lower_drive = abs(float(terms["lower_drive"]))
    upper_gate = abs(float(terms["upper_gate"]))
    force = clamp(0.72 * abs(roll_delta) + 0.16 * contact_pressure + 0.10 * lower_drive + 0.05 * upper_gate, 0.0, 1.2)

    layers = [layer_terrain_read(ara, roll_delta, force, depth) for depth in range(1, max_depth + 1)]
    weights = np.asarray([1.0 / (PHI ** (layer["depth"] - 1)) for layer in layers], dtype=float)
    weights = weights / float(np.sum(weights))
    target = float(np.sum(weights * np.asarray([layer["target"] for layer in layers], dtype=float)))
    target_with_spill = float(
        np.sum(weights * np.asarray([layer["target_with_spill"] for layer in layers], dtype=float))
    )
    spillover = float(np.sum(weights * np.asarray([layer["spillover"] for layer in layers], dtype=float)))
    ridge_resistance = float(
        np.sum(weights * np.asarray([layer["ridge_resistance"] for layer in layers], dtype=float))
    )
    weighted_width = float(np.sum(weights * np.asarray([layer["width"] for layer in layers], dtype=float)))
    slope = target - ara
    slope_with_spill = target_with_spill - ara
    settle_gain = clamp(0.18 + 0.42 * force + 0.23 * spillover + 0.12 * abs(slope) / max(weighted_width, EPS), 0.10, 0.92)
    force_gain = clamp(0.25 + 0.58 * force + 0.15 * spillover, 0.12, 1.05)

    return {
        "arrival_ara": ara,
        "current_ara": clamp_ara(current_ara),
        "roll_delta": roll_delta,
        "force": force,
        "weighted_target": clamp_ara(target),
        "weighted_target_spill": clamp_ara(target_with_spill),
        "weighted_slope": slope,
        "weighted_slope_spill": slope_with_spill,
        "spillover": spillover,
        "ridge_resistance": ridge_resistance,
        "settle_gain": settle_gain,
        "force_gain": force_gain,
        "dominant_bounds": [layers[0]["lo"], layers[0]["hi"]],
        "dominant_address": layers[0]["address"],
        "deep_address": layers[-1]["address"],
        "dominant_target": layers[0]["target"],
        "dominant_target_spill": layers[0]["target_with_spill"],
        "layers": layers,
    }


def learned_target_vec(records, row):
    train = completed_motion_candidates(records, row)
    if len(train) < MIN_LEARN_TRAIN:
        return None
    X = [candidate["features"] for candidate in train]
    Y = [candidate["target_vec"] for candidate in train]
    model = fit_ridge(X, Y, RIDGE_ALPHA)
    pred = predict_ridge(model, row["features"])
    return unit(pred)


def load_comparison_predictions(path, fields):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for horizon, rows in data.get("viz_records", {}).items():
        out[horizon] = {}
        for row in rows:
            key = (row["origin"], row["target"])
            out[horizon][key] = {field: row.get(field) for field in fields}
    return out


def point_records(records, pred_key):
    return [point(row["origin"], row["target"], row[pred_key], row["actual"], row["current"]) for row in records]


def direction_score(records, pred_key):
    rows = []
    for row in records:
        truth = sign(row["actual"] - row["current"])
        pred = sign(row[pred_key] - row["current"])
        if truth == 0:
            continue
        rows.append((truth, pred, row))
    if not rows:
        return {"n": 0, "accuracy": None, "large_accuracy": None, "transition_accuracy": None}
    large = [item for item in rows if abs(item[2]["actual"] - item[2]["current"]) >= 0.5]
    transition = [item for item in rows if abs(item[2]["actual"]) >= 0.5 or abs(item[2]["current"]) >= 0.5]
    return {
        "n": int(len(rows)),
        "accuracy": float(np.mean([truth == pred for truth, pred, _ in rows])),
        "large_accuracy": float(np.mean([truth == pred for truth, pred, _ in large])) if large else None,
        "transition_accuracy": float(np.mean([truth == pred for truth, pred, _ in transition])) if transition else None,
    }


def amplitude_stats(records, pred_key):
    if not records:
        return {"n": 0, "pred_delta_std": None, "truth_delta_std": None, "std_ratio": None, "abs_delta_ratio": None}
    pred_delta = np.asarray([row[pred_key] - row["current"] for row in records], dtype=float)
    truth_delta = np.asarray([row["actual"] - row["current"] for row in records], dtype=float)
    pred_std = float(np.std(pred_delta))
    truth_std = float(np.std(truth_delta))
    mean_abs_truth = float(np.mean(np.abs(truth_delta)))
    return {
        "n": int(len(records)),
        "pred_delta_std": pred_std,
        "truth_delta_std": truth_std,
        "std_ratio": pred_std / truth_std if truth_std > EPS else None,
        "abs_delta_ratio": float(np.mean(np.abs(pred_delta)) / mean_abs_truth) if mean_abs_truth > EPS else None,
    }


def focus_direction(scores, horizons):
    return {
        "n": int(sum(scores[str(h)]["n"] for h in horizons)),
        "accuracy": float(np.mean([scores[str(h)]["accuracy"] for h in horizons])),
        "large_accuracy": float(
            np.mean([scores[str(h)]["large_accuracy"] for h in horizons if scores[str(h)]["large_accuracy"] is not None])
        ),
        "transition_accuracy": float(
            np.mean(
                [
                    scores[str(h)]["transition_accuracy"]
                    for h in horizons
                    if scores[str(h)]["transition_accuracy"] is not None
                ]
            )
        ),
    }


def run():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    raw_comparison = load_comparison_predictions(RAW_ADDRESS_JSON, ["raw_address_top1"])
    orientation_comparison = load_comparison_predictions(ORIENTATION_JSON, ["roll_learned_surface"])
    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    direction_scores = {key: {} for key in MODEL_KEYS}
    amplitude = {key: {} for key in MODEL_KEYS}
    ready_point_scores = {key: {} for key in MODEL_KEYS}
    ready_direction_scores = {key: {} for key in MODEL_KEYS}
    ready_amplitude = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA fractal sphere terrain reader")
    print("=" * 100)
    print("strict guards: causal future pose; deterministic recursive ARA terrain; no historical neighbour terrain")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in data["records_by_horizon"][h]]
        for row in records:
            row["surface_vec"] = row_surface_vec(row)
            row["target_vec"] = row_target_vec(row)
            row["features"] = surface_features(row)

        for row in records:
            key = (row["origin"], row["target"])
            row["persistence_pred"] = row["current"]
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            row["roll_learned_average_pred"] = orientation_comparison.get(h, {}).get(key, {}).get(
                "roll_learned_surface", row["current"]
            )
            row["raw_address_top1_pred"] = raw_comparison.get(h, {}).get(key, {}).get(
                "raw_address_top1", row["current"]
            )

            target_vec = learned_target_vec(records, row)
            if target_vec is None:
                row["fractal_ready"] = False
                row["fractal_arrival_ara"] = None
                row["fractal_target_ara"] = None
                row["fractal_force"] = None
                row["fractal_spillover"] = None
                row["fractal_bounds"] = None
                row["fractal_deep_address"] = None
                for branch in ["depth1", "depth2", "depth3", "direct", "settle", "force", "spill"]:
                    row[f"fractal_phi_{branch}_pred"] = row["current"]
                continue

            terrain = read_fractal_terrain(vec_to_ara(target_vec), row["ara_current"], roll_terms(row))
            depth1_value = ara_to_value(terrain["layers"][0]["target_with_spill"])
            depth2_value = ara_to_value(terrain["layers"][1]["target_with_spill"])
            depth3_value = ara_to_value(terrain["layers"][2]["target_with_spill"])
            direct_value = ara_to_value(terrain["weighted_target"])
            spill_value = ara_to_value(terrain["weighted_target_spill"])
            force_ara = clamp_ara(terrain["arrival_ara"] + terrain["weighted_slope"] * terrain["force_gain"])
            force_value = ara_to_value(force_ara)
            settle_value = row["current"] + (spill_value - row["current"]) * terrain["settle_gain"]

            row["fractal_ready"] = True
            row["fractal_phi_depth1_pred"] = depth1_value
            row["fractal_phi_depth2_pred"] = depth2_value
            row["fractal_phi_depth3_pred"] = depth3_value
            row["fractal_phi_direct_pred"] = direct_value
            row["fractal_phi_settle_pred"] = settle_value
            row["fractal_phi_force_pred"] = force_value
            row["fractal_phi_spill_pred"] = spill_value
            row["fractal_arrival_ara"] = terrain["arrival_ara"]
            row["fractal_target_ara"] = terrain["weighted_target"]
            row["fractal_target_spill_ara"] = terrain["weighted_target_spill"]
            row["fractal_force"] = terrain["force"]
            row["fractal_spillover"] = terrain["spillover"]
            row["fractal_ridge_resistance"] = terrain["ridge_resistance"]
            row["fractal_bounds"] = terrain["dominant_bounds"]
            row["fractal_deep_address"] = "".join(str(bit) for bit in terrain["deep_address"])

        score_keys = {
            "persistence": "persistence_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "roll_learned_average": "roll_learned_average_pred",
            "raw_address_top1": "raw_address_top1_pred",
            "fractal_phi_depth1": "fractal_phi_depth1_pred",
            "fractal_phi_depth2": "fractal_phi_depth2_pred",
            "fractal_phi_depth3": "fractal_phi_depth3_pred",
            "fractal_phi_direct": "fractal_phi_direct_pred",
            "fractal_phi_settle": "fractal_phi_settle_pred",
            "fractal_phi_force": "fractal_phi_force_pred",
            "fractal_phi_spill": "fractal_phi_spill_pred",
        }
        ready = [row for row in records if row["fractal_ready"]]
        for key, pred_key in score_keys.items():
            point_scores[key][h] = extended_score(point_records(records, pred_key))
            direction_scores[key][h] = direction_score(records, pred_key)
            amplitude[key][h] = amplitude_stats(records, pred_key)
            ready_point_scores[key][h] = extended_score(point_records(ready, pred_key)) if ready else {}
            ready_direction_scores[key][h] = direction_score(ready, pred_key) if ready else {
                "n": 0,
                "accuracy": None,
                "large_accuracy": None,
                "transition_accuracy": None,
            }
            ready_amplitude[key][h] = amplitude_stats(ready, pred_key) if ready else {
                "n": 0,
                "pred_delta_std": None,
                "truth_delta_std": None,
                "std_ratio": None,
                "abs_delta_ratio": None,
            }

        diagnostics[h] = {
            "ready_fraction": float(len(ready) / len(records)),
            "mean_arrival_ara": float(np.mean([row["fractal_arrival_ara"] for row in ready])) if ready else None,
            "mean_target_ara": float(np.mean([row["fractal_target_ara"] for row in ready])) if ready else None,
            "mean_force": float(np.mean([row["fractal_force"] for row in ready])) if ready else None,
            "mean_spillover": float(np.mean([row["fractal_spillover"] for row in ready])) if ready else None,
        }

        records_by_h[h] = [
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": rounded(row["current"]),
                "actual": rounded(row["actual"]),
                "wobble_surface_analog": rounded(row["wobble_surface_analog_pred"]),
                "roll_learned_average": rounded(row["roll_learned_average_pred"]),
                "raw_address_top1": rounded(row["raw_address_top1_pred"]),
                "fractal_phi_depth1": rounded(row["fractal_phi_depth1_pred"]),
                "fractal_phi_depth2": rounded(row["fractal_phi_depth2_pred"]),
                "fractal_phi_depth3": rounded(row["fractal_phi_depth3_pred"]),
                "fractal_phi_direct": rounded(row["fractal_phi_direct_pred"]),
                "fractal_phi_settle": rounded(row["fractal_phi_settle_pred"]),
                "fractal_phi_force": rounded(row["fractal_phi_force_pred"]),
                "fractal_phi_spill": rounded(row["fractal_phi_spill_pred"]),
                "fractal_arrival_ara": rounded(row["fractal_arrival_ara"])
                if row["fractal_arrival_ara"] is not None
                else None,
                "fractal_target_ara": rounded(row["fractal_target_ara"])
                if row["fractal_target_ara"] is not None
                else None,
                "fractal_force": rounded(row["fractal_force"]) if row["fractal_force"] is not None else None,
                "fractal_spillover": rounded(row["fractal_spillover"])
                if row["fractal_spillover"] is not None
                else None,
                "fractal_bounds": row["fractal_bounds"],
                "fractal_deep_address": row["fractal_deep_address"],
            }
            for row in records
        ]

        print(f"h={horizon:>2} months")
        for key in MODEL_KEYS:
            ps = point_scores[key][h]
            ds = direction_scores[key][h]
            amp = amplitude[key][h]
            print(
                f"  {key:24s} {format_score(ps)}"
                f" dir={ds['accuracy'] if ds['accuracy'] is not None else float('nan'):.3f}"
                f" amp_ratio={amp['std_ratio'] if amp['std_ratio'] is not None else float('nan'):.3f}"
            )
        print(
            f"  fractal diagnostics      ready={diagnostics[h]['ready_fraction']:.3f}"
            f" target_ara={diagnostics[h]['mean_target_ara'] if diagnostics[h]['mean_target_ara'] is not None else float('nan'):.3f}"
            f" spill={diagnostics[h]['mean_spillover'] if diagnostics[h]['mean_spillover'] is not None else float('nan'):.3f}"
        )
        print()

    focus_horizons = [6, 12, 24]
    focus = {
        "point_scores": {key: aggregate_focus(point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "direction_scores": {key: focus_direction(direction_scores[key], focus_horizons) for key in MODEL_KEYS},
        "amplitude": {key: aggregate_focus(amplitude[key], focus_horizons) for key in MODEL_KEYS},
        "ready_point_scores": {key: aggregate_focus(ready_point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "ready_direction_scores": {key: focus_direction(ready_direction_scores[key], focus_horizons) for key in MODEL_KEYS},
        "ready_amplitude": {key: aggregate_focus(ready_amplitude[key], focus_horizons) for key in MODEL_KEYS},
    }

    out = {
        "date": "2026-05-26",
        "method": "strict-causal fractal ARA sphere terrain reader",
        "source": "TheFormula/ara_sphere_atlas_data.json",
        "orientation_source": "TheFormula/ara_sphere_orientation_roll_predictor.py",
        "leakage_guard": [
            "Learned future pose trains only on completed historical rows whose target is before current origin t.",
            "The fractal terrain reader is deterministic and filled; it does not use nearest historical points as terrain.",
            "Recursive bounds are read inside the 0..2 ARA sphere, with local in-bounds phi valleys at every depth.",
            "Boundary spillover is allowed only when roll/contact force exceeds local ridge resistance.",
            "No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.",
            "Non-ready rows fall back to persistence.",
        ],
        "terrain_rule": {
            "bounds": "binary recursive sub-ARA bands inside 0..2",
            "local_phi": "for each [lo, hi], valleys are hi - (hi-lo)/phi and lo + (hi-lo)/phi",
            "motion": "rolls toward the closest local phi within bounds unless force spills across a ridge",
            "depth_weighting": "deeper layers are weighted by phi^-(depth-1)",
        },
        "horizons_months": HORIZONS,
        "max_terrain_depth": MAX_TERRAIN_DEPTH,
        "point_scores": clean_for_json(point_scores),
        "direction_scores": clean_for_json(direction_scores),
        "amplitude": clean_for_json(amplitude),
        "ready_point_scores": clean_for_json(ready_point_scores),
        "ready_direction_scores": clean_for_json(ready_direction_scores),
        "ready_amplitude": clean_for_json(ready_amplitude),
        "diagnostics": clean_for_json(diagnostics),
        "focus_6_12_24": clean_for_json(focus),
        "viz_records": clean_for_json(records_by_h),
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_FRACTAL_SPHERE_TERRAIN = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24:")
    for key in MODEL_KEYS:
        ps = focus["point_scores"][key]
        ds = focus["direction_scores"][key]
        amp = focus["amplitude"][key]
        print(
            f"  {key:24s}"
            f" MAE={ps.get('mae'):.3f}"
            f" corr={ps.get('corr'):+.3f}"
            f" dir={ds.get('accuracy'):.3f}"
            f" amp_ratio={amp.get('std_ratio'):.3f}"
        )
    print("Ready-only focus 6/12/24:")
    for key in MODEL_KEYS:
        ps = focus["ready_point_scores"][key]
        ds = focus["ready_direction_scores"][key]
        amp = focus["ready_amplitude"][key]
        print(
            f"  {key:24s}"
            f" MAE={ps.get('mae'):.3f}"
            f" corr={ps.get('corr'):+.3f}"
            f" dir={ds.get('accuracy'):.3f}"
            f" amp_ratio={amp.get('std_ratio'):.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
