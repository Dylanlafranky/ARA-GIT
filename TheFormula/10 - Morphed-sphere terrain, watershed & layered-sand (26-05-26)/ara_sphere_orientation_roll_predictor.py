"""
ara_sphere_orientation_roll_predictor.py

Strict-causal test of the explicit sphere-orientation version of the terrain
model.

Concept:

    the terrain map is mostly fixed on the sphere
    the local water/signal slice is the reading point
    prediction means estimating how the sphere will roll/wobble
    then sampling the fixed surface patch that arrives under the slice

This script represents roll as a 3D angular vector. It compares hand-built
roll estimates with a causal learned orientation operator:

    current surface pose -> predicted future surface vector
    predicted vector -> lookup fixed historical terrain surface
    lookup terrain value -> forecast

No lag ridge, no native-value decoder, no future geometry oracle, no smoothing,
and no visual shift.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ara_geometry_transport_test import clean_for_json
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, rounded
from ara_sphere_topology_direction_predictor import (
    EPS,
    localize_ara,
    month_index,
    sign,
    sphere_vec,
)


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
SPHERE_TOPOLOGY_JSON = HERE / "ara_sphere_topology_direction_result.json"
OUT_JSON = HERE / "ara_sphere_orientation_roll_result.json"
OUT_JS = HERE / "ara_sphere_orientation_roll_result.js"

HORIZONS = [3, 6, 12, 18, 24]
NEIGHBOR_COUNT = 42
MIN_SURFACE_NEIGHBORS = 48
MIN_LEARN_TRAIN = 56
DISTANCE_BANDWIDTH = 0.58
RIDGE_ALPHA = 7.5

MODEL_KEYS = [
    "persistence",
    "terrain_level_analog",
    "wobble_surface_analog",
    "sphere_nested2_level",
    "roll_clock_surface",
    "roll_wobble_surface",
    "roll_contact_surface",
    "roll_learned_surface",
]


def clamp_ara(value):
    return float(max(0.0, min(2.0, value)))


def wrap_rad(value):
    return math.atan2(math.sin(float(value)), math.cos(float(value)))


def safe_tanh(value, scale=1.0):
    return float(math.tanh(float(value) / max(scale, EPS)))


def deg_to_rad(value):
    return math.radians(float(value) % 360.0)


def unit(vec):
    vec = np.asarray(vec, dtype=float)
    norm = float(np.linalg.norm(vec))
    if norm <= EPS:
        return np.asarray([1.0, 0.0, 0.0], dtype=float)
    return vec / norm


def rotate_vec(vec, omega):
    vec = unit(vec)
    omega = np.asarray(omega, dtype=float)
    angle = float(np.linalg.norm(omega))
    if angle <= EPS:
        return vec
    axis = omega / angle
    return unit(
        vec * math.cos(angle)
        + np.cross(axis, vec) * math.sin(angle)
        + axis * float(np.dot(axis, vec)) * (1.0 - math.cos(angle))
    )


def local_basis(surface_vec):
    radial = unit(surface_vec)
    pole = np.asarray([0.0, 1.0, 0.0], dtype=float)
    east = np.cross(pole, radial)
    if float(np.linalg.norm(east)) <= 1e-6:
        east = np.asarray([1.0, 0.0, 0.0], dtype=float)
    east = unit(east)
    north = unit(np.cross(radial, east))
    return radial, east, north


def row_surface_vec(row):
    return sphere_vec(row["ara_current"], row["phase_clock_origin"])


def row_target_vec(row):
    return sphere_vec(row["ara_actual"], row["phase_clock_target"])


def roll_terms(row):
    wobble = row["wobble"]
    lower_drive = float(wobble["nino_spin"]) - float(wobble["soi_spin"])
    home_roll = float(wobble["x_v3"]) + 0.34 * float(wobble["torsion"])
    lateral_roll = float(wobble["y_v3"]) + 0.18 * float(wobble["y"])
    upper_gate = float(wobble["z_v3"]) + 0.25 * float(wobble["z"])
    twist = float(wobble["torsion"]) + 0.18 * (float(wobble["nino_spin"]) + float(wobble["soi_spin"]))
    parity = sign(-lower_drive) * sign(home_roll)
    return {
        "lower_drive": safe_tanh(lower_drive, 3.0),
        "home_roll": safe_tanh(home_roll, 1.4),
        "lateral_roll": safe_tanh(lateral_roll, 1.0),
        "upper_gate": safe_tanh(upper_gate, 1.4),
        "twist": safe_tanh(twist, 3.0),
        "parity": float(parity),
        "contact_pressure": safe_tanh(abs(lower_drive) + abs(home_roll) + 0.5 * abs(upper_gate), 5.0),
    }


def roll_vector(row, variant):
    p = row["surface_vec"]
    radial, east, north = local_basis(p)
    base = np.asarray([0.0, 1.0, 0.0], dtype=float) * deg_to_rad(row["phase_horizon_offset"])
    terms = roll_terms(row)

    if variant == "clock":
        return base

    wobble = (
        north * math.radians(18.0 * terms["home_roll"])
        + east * math.radians(13.0 * terms["lateral_roll"])
        + radial * math.radians(10.0 * terms["twist"])
    )
    if variant == "wobble":
        return base + wobble

    contact = (
        north * math.radians(-16.0 * terms["lower_drive"])
        + east * math.radians(10.0 * terms["upper_gate"])
        + radial * math.radians(7.0 * terms["parity"])
    )
    return base + wobble + contact


def nested_ara_values(ara):
    values = [clamp_ara(ara)]
    cur = clamp_ara(ara)
    for _ in [1, 2]:
        _, cur = localize_ara(cur)
        values.append(cur)
    return values


def surface_features(row):
    p = row["surface_vec"]
    terms = roll_terms(row)
    nested = nested_ara_values(row["ara_current"])
    return np.asarray(
        [
            p[0],
            p[1],
            p[2],
            nested[0],
            nested[1],
            nested[2],
            terms["lower_drive"],
            terms["home_roll"],
            terms["lateral_roll"],
            terms["upper_gate"],
            terms["twist"],
            terms["parity"],
            terms["contact_pressure"],
        ],
        dtype=float,
    )


def standardize_train(X):
    center = np.median(X, axis=0)
    mad = np.median(np.abs(X - center), axis=0)
    std = np.std(X, axis=0)
    scale = np.maximum(1e-6, np.maximum(1.4826 * mad, 0.25 * std))
    return center, scale


def fit_ridge(X, Y, alpha=RIDGE_ALPHA):
    X = np.asarray(X, dtype=float)
    Y = np.asarray(Y, dtype=float)
    center, scale = standardize_train(X)
    Xs = (X - center) / scale
    Xb = np.column_stack([np.ones(len(Xs)), Xs])
    penalty = np.eye(Xb.shape[1]) * float(alpha)
    penalty[0, 0] = 0.0
    coef = np.linalg.solve(Xb.T @ Xb + penalty, Xb.T @ Y)
    return {"center": center, "scale": scale, "coef": coef}


def predict_ridge(model, x):
    xs = (np.asarray(x, dtype=float) - model["center"]) / model["scale"]
    xb = np.concatenate([[1.0], xs])
    return xb @ model["coef"]


def surface_distance(target_vec, candidate):
    dot = float(np.clip(np.dot(unit(target_vec), unit(candidate["surface_vec"])), -1.0, 1.0))
    sphere_dist = (1.0 - dot) * 0.5
    ara_dist = abs(float(candidate["ara_current"]) - vec_to_ara(target_vec)) / 2.0
    return math.sqrt(max(0.0, 1.35 * sphere_dist + 0.35 * ara_dist * ara_dist))


def vec_to_ara(vec):
    vec = unit(vec)
    return clamp_ara(1.0 - float(vec[1]))


def surface_candidates(records, row):
    origin_m = month_index(row["origin"])
    return [candidate for candidate in records if month_index(candidate["origin"]) < origin_m]


def completed_motion_candidates(records, row):
    origin_m = month_index(row["origin"])
    return [candidate for candidate in records if month_index(candidate["target"]) < origin_m]


def lookup_surface(records, row, target_vec):
    candidates = surface_candidates(records, row)
    if len(candidates) < MIN_SURFACE_NEIGHBORS:
        return None
    ranked = sorted([(surface_distance(target_vec, candidate), candidate) for candidate in candidates], key=lambda item: item[0])
    nearest = ranked[:NEIGHBOR_COUNT]
    weights = np.asarray([math.exp(-0.5 * (dist / DISTANCE_BANDWIDTH) ** 2) for dist, _ in nearest], dtype=float)
    if float(np.sum(weights)) <= EPS:
        weights = np.ones(len(nearest), dtype=float)
    weights = weights / float(np.sum(weights))
    values = np.asarray([candidate["current"] for _, candidate in nearest], dtype=float)
    directions = np.asarray([sign(candidate["current"] - row["current"]) for _, candidate in nearest], dtype=float)
    distances = np.asarray([dist for dist, _ in nearest], dtype=float)
    direction_vote = float(np.sum(weights * directions))
    return {
        "level_pred": float(np.sum(weights * values)),
        "direction_vote": direction_vote,
        "confidence": abs(direction_vote),
        "candidate_count": int(len(candidates)),
        "mean_distance": float(np.sum(weights * distances)),
        "target_ara": vec_to_ara(target_vec),
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


def load_sphere_baselines():
    if not SPHERE_TOPOLOGY_JSON.exists():
        return {}
    data = json.loads(SPHERE_TOPOLOGY_JSON.read_text(encoding="utf-8"))
    out = {}
    for horizon, rows in data.get("viz_records", {}).items():
        out[horizon] = {
            (row["origin"], row["target"]): row.get("sphere_nested2_level", row.get("current"))
            for row in rows
        }
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
    sphere_baselines = load_sphere_baselines()
    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    direction_scores = {key: {} for key in MODEL_KEYS}
    ready_point_scores = {key: {} for key in MODEL_KEYS}
    ready_direction_scores = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA sphere orientation roll predictor")
    print("=" * 100)
    print("strict guards: predict future pose, then sample older fixed terrain surface; no value decoder")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in data["records_by_horizon"][h]]
        for row in records:
            row["surface_vec"] = row_surface_vec(row)
            row["target_vec"] = row_target_vec(row)
            row["features"] = surface_features(row)

        for row in records:
            row["persistence_pred"] = row["current"]
            row["terrain_level_analog_pred"] = row["terrain_level_analog"]
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            row["sphere_nested2_level_pred"] = sphere_baselines.get(h, {}).get((row["origin"], row["target"]), row["current"])

            roll_targets = {
                "roll_clock": rotate_vec(row["surface_vec"], roll_vector(row, "clock")),
                "roll_wobble": rotate_vec(row["surface_vec"], roll_vector(row, "wobble")),
                "roll_contact": rotate_vec(row["surface_vec"], roll_vector(row, "contact")),
            }
            learned = learned_target_vec(records, row)
            if learned is not None:
                roll_targets["roll_learned"] = learned

            for prefix in ["roll_clock", "roll_wobble", "roll_contact", "roll_learned"]:
                target_vec = roll_targets.get(prefix)
                pred = lookup_surface(records, row, target_vec) if target_vec is not None else None
                if pred is None:
                    row[f"{prefix}_surface_pred"] = row["current"]
                    row[f"{prefix}_direction_vote"] = 0.0
                    row[f"{prefix}_confidence"] = 0.0
                    row[f"{prefix}_candidate_count"] = 0
                    row[f"{prefix}_mean_distance"] = None
                    row[f"{prefix}_target_ara"] = None
                    continue
                row[f"{prefix}_surface_pred"] = pred["level_pred"]
                row[f"{prefix}_direction_vote"] = pred["direction_vote"]
                row[f"{prefix}_confidence"] = pred["confidence"]
                row[f"{prefix}_candidate_count"] = pred["candidate_count"]
                row[f"{prefix}_mean_distance"] = pred["mean_distance"]
                row[f"{prefix}_target_ara"] = pred["target_ara"]

        score_keys = {
            "persistence": "persistence_pred",
            "terrain_level_analog": "terrain_level_analog_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "sphere_nested2_level": "sphere_nested2_level_pred",
            "roll_clock_surface": "roll_clock_surface_pred",
            "roll_wobble_surface": "roll_wobble_surface_pred",
            "roll_contact_surface": "roll_contact_surface_pred",
            "roll_learned_surface": "roll_learned_surface_pred",
        }
        ready = [row for row in records if row["roll_learned_candidate_count"] > 0]
        for key, pred_key in score_keys.items():
            point_scores[key][h] = extended_score(point_records(records, pred_key))
            direction_scores[key][h] = direction_score(records, pred_key)
            ready_point_scores[key][h] = extended_score(point_records(ready, pred_key)) if ready else {}
            ready_direction_scores[key][h] = direction_score(ready, pred_key) if ready else {
                "n": 0,
                "accuracy": None,
                "large_accuracy": None,
                "transition_accuracy": None,
            }

        diagnostics[h] = {
            "ready_fraction": float(len(ready) / len(records)),
            "mean_candidate_count": float(np.mean([row["roll_learned_candidate_count"] for row in ready])) if ready else None,
            "mean_distance": float(np.mean([row["roll_learned_mean_distance"] for row in ready])) if ready else None,
            "mean_confidence": float(np.mean([row["roll_learned_confidence"] for row in ready])) if ready else None,
            "mean_target_ara": float(np.mean([row["roll_learned_target_ara"] for row in ready])) if ready else None,
        }

        records_by_h[h] = [
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": rounded(row["current"]),
                "actual": rounded(row["actual"]),
                "terrain_level_analog": rounded(row["terrain_level_analog_pred"]),
                "wobble_surface_analog": rounded(row["wobble_surface_analog_pred"]),
                "sphere_nested2_level": rounded(row["sphere_nested2_level_pred"]),
                "roll_clock_surface": rounded(row["roll_clock_surface_pred"]),
                "roll_wobble_surface": rounded(row["roll_wobble_surface_pred"]),
                "roll_contact_surface": rounded(row["roll_contact_surface_pred"]),
                "roll_learned_surface": rounded(row["roll_learned_surface_pred"]),
                "roll_learned_confidence": rounded(row["roll_learned_confidence"]),
                "roll_learned_mean_distance": rounded(row["roll_learned_mean_distance"])
                if row["roll_learned_mean_distance"] is not None
                else None,
                "roll_learned_target_ara": rounded(row["roll_learned_target_ara"])
                if row["roll_learned_target_ara"] is not None
                else None,
            }
            for row in records
        ]

        print(f"h={horizon:>2} months")
        for key in MODEL_KEYS:
            ps = point_scores[key][h]
            ds = direction_scores[key][h]
            print(
                f"  {key:24s} {format_score(ps)}"
                f" dir={ds['accuracy'] if ds['accuracy'] is not None else float('nan'):.3f}"
                f" large_dir={ds['large_accuracy'] if ds['large_accuracy'] is not None else float('nan'):.3f}"
            )
        print(
            f"  learned diagnostics      ready={diagnostics[h]['ready_fraction']:.3f}"
            f" dist={diagnostics[h]['mean_distance'] if diagnostics[h]['mean_distance'] is not None else float('nan'):.3f}"
            f" conf={diagnostics[h]['mean_confidence'] if diagnostics[h]['mean_confidence'] is not None else float('nan'):.3f}"
        )
        print()

    focus_horizons = [6, 12, 24]
    focus = {
        "point_scores": {key: aggregate_focus(point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "direction_scores": {key: focus_direction(direction_scores[key], focus_horizons) for key in MODEL_KEYS},
        "ready_point_scores": {key: aggregate_focus(ready_point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "ready_direction_scores": {key: focus_direction(ready_direction_scores[key], focus_horizons) for key in MODEL_KEYS},
    }

    out = {
        "date": "2026-05-26",
        "method": "strict-causal sphere orientation roll predictor",
        "source": "TheFormula/ara_sphere_atlas_data.json",
        "baseline_source": "TheFormula/ara_sphere_topology_direction_result.json",
        "leakage_guard": [
            "Hand-built roll variants estimate future pose only from current-origin sphere/wobble/spin values and horizon.",
            "The learned orientation operator trains only on completed historical rows whose target is before current origin t.",
            "Surface map lookup uses only historical origin patches before current origin t.",
            "No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.",
            "Non-ready rows fall back to persistence.",
        ],
        "orientation_model": {
            "surface": "fixed terrain map on the sphere",
            "slice": "local reading point; prediction samples terrain rotating under it",
            "roll_clock": "home-cycle rotation around the ARA pole axis",
            "roll_wobble": "clock roll plus local forward/lateral/twist angular components",
            "roll_contact": "wobble roll plus lower-drive, upper-gate, and parity contact components",
            "roll_learned": "causal ridge map from current pose features to future surface vector, then fixed-surface lookup",
        },
        "horizons_months": HORIZONS,
        "neighbor_count": NEIGHBOR_COUNT,
        "min_surface_neighbors": MIN_SURFACE_NEIGHBORS,
        "min_learn_train": MIN_LEARN_TRAIN,
        "point_scores": clean_for_json(point_scores),
        "direction_scores": clean_for_json(direction_scores),
        "ready_point_scores": clean_for_json(ready_point_scores),
        "ready_direction_scores": clean_for_json(ready_direction_scores),
        "diagnostics": clean_for_json(diagnostics),
        "focus_6_12_24": clean_for_json(focus),
        "viz_records": clean_for_json(records_by_h),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_SPHERE_ORIENTATION_ROLL = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24:")
    for key in MODEL_KEYS:
        ps = focus["point_scores"][key]
        ds = focus["direction_scores"][key]
        print(
            f"  {key:24s}"
            f" MAE={ps.get('mae'):.3f}"
            f" corr={ps.get('corr'):+.3f}"
            f" turn={ps.get('turn_accuracy'):.3f}"
            f" dir={ds.get('accuracy'):.3f}"
            f" large_dir={ds.get('large_accuracy'):.3f}"
        )
    print("Ready-only focus 6/12/24:")
    for key in MODEL_KEYS:
        ps = focus["ready_point_scores"][key]
        ds = focus["ready_direction_scores"][key]
        print(
            f"  {key:24s}"
            f" MAE={ps.get('mae'):.3f}"
            f" corr={ps.get('corr'):+.3f}"
            f" turn={ps.get('turn_accuracy'):.3f}"
            f" dir={ds.get('accuracy'):.3f}"
            f" large_dir={ds.get('large_accuracy'):.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
