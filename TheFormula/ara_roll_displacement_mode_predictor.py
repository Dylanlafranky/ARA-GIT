"""
ara_roll_displacement_mode_predictor.py

Strict-causal test for the "terrain address advancer" bottleneck.

The fractal sphere reader filled the terrain, but the future-pose step was
still too conservative. This script learns completed roll displacements instead
of predicting the final coordinate directly:

    current address
    -> classify completed historical roll mode
    -> apply a raw/within-mode roll displacement
    -> read fractal ARA terrain at the advanced coordinate

Historical data trains/selects the roll displacement only when the candidate
target is already before the current origin. The fractal terrain remains a
deterministic filled reader, not a historical terrain table.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from ara_fractal_sphere_terrain_reader import ara_to_value, read_fractal_terrain
from ara_geometry_transport_test import clean_for_json
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, rounded
from ara_sphere_orientation_roll_predictor import (
    EPS,
    HORIZONS,
    completed_motion_candidates,
    local_basis,
    roll_terms,
    row_surface_vec,
    row_target_vec,
    rotate_vec,
    sign,
    surface_features,
    unit,
    vec_to_ara,
)


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
RAW_ADDRESS_JSON = HERE / "ara_raw_terrain_address_lookup_result.json"
FRACTAL_JSON = HERE / "ara_fractal_sphere_terrain_reader_result.json"
OUT_JSON = HERE / "ara_roll_displacement_mode_predictor_result.json"
OUT_JS = HERE / "ara_roll_displacement_mode_predictor_result.js"

MIN_MODE_TRAIN = 56
NEIGHBOR_COUNT = 44
MODE_NEIGHBOR_COUNT = 11
DISTANCE_BANDWIDTH = 3.4

MODEL_KEYS = [
    "persistence",
    "wobble_surface_analog",
    "raw_address_top1",
    "fractal_phi_force",
    "mode_top1_fractal",
    "mode_median_fractal",
    "mode_weighted_fractal",
    "mode_top1_arrival",
]


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def log_roll_components(start_vec, end_vec):
    start = unit(start_vec)
    end = unit(end_vec)
    dot = float(np.clip(np.dot(start, end), -1.0, 1.0))
    angle = math.acos(dot)
    cross = np.cross(start, end)
    norm = float(np.linalg.norm(cross))
    if angle <= EPS or norm <= EPS:
        omega = np.asarray([0.0, 0.0, 0.0], dtype=float)
    else:
        omega = (cross / norm) * angle
    radial, east, north = local_basis(start)
    return np.asarray(
        [
            float(np.dot(omega, north)),
            float(np.dot(omega, east)),
            float(np.dot(omega, radial)),
        ],
        dtype=float,
    )


def components_to_omega(surface_vec, components):
    radial, east, north = local_basis(surface_vec)
    comp = np.asarray(components, dtype=float)
    return north * comp[0] + east * comp[1] + radial * comp[2]


def coarse_band(ara, depth=2):
    x = clamp(float(ara), 0.0, 2.0)
    lo = 0.0
    hi = 2.0
    bits = []
    for _ in range(depth):
        mid = 0.5 * (lo + hi)
        if x < mid:
            bits.append("0")
            hi = mid
        else:
            bits.append("1")
            lo = mid
    return "".join(bits)


def mode_label(row):
    comp = row["roll_components"]
    delta_ara = float(row["ara_actual"]) - float(row["ara_current"])
    ara_dir = sign(delta_ara, 0.06)
    forward = sign(comp[0], 0.055)
    lateral = sign(comp[1], 0.055)
    twist = sign(comp[2], 0.035)
    spill = coarse_band(row["ara_actual"], 2) != coarse_band(row["ara_current"], 2)
    return f"a{ara_dir:+d}_f{forward:+d}_l{lateral:+d}_t{twist:+d}_s{int(spill)}"


def standardize(candidates):
    X = np.asarray([row["features"] for row in candidates], dtype=float)
    center = np.median(X, axis=0)
    mad = np.median(np.abs(X - center), axis=0)
    std = np.std(X, axis=0)
    scale = np.maximum(1e-6, np.maximum(1.4826 * mad, 0.25 * std))
    return center, scale


def feature_distance(row, candidate, center, scale):
    a = (np.asarray(row["features"], dtype=float) - center) / scale
    b = (np.asarray(candidate["features"], dtype=float) - center) / scale
    return float(np.sqrt(np.mean((a - b) ** 2)))


def predict_roll_mode(records, row):
    candidates = completed_motion_candidates(records, row)
    if len(candidates) < MIN_MODE_TRAIN:
        return None
    center, scale = standardize(candidates)
    ranked = sorted(
        [(feature_distance(row, candidate, center, scale), candidate) for candidate in candidates],
        key=lambda item: item[0],
    )
    nearest = ranked[:NEIGHBOR_COUNT]
    weights = np.asarray([math.exp(-0.5 * (distance / DISTANCE_BANDWIDTH) ** 2) for distance, _ in nearest])
    if float(np.sum(weights)) <= EPS:
        weights = np.ones(len(nearest), dtype=float)
    weights = weights / float(np.sum(weights))

    mode_weights = defaultdict(float)
    for weight, (_, candidate) in zip(weights, nearest):
        mode_weights[candidate["roll_mode"]] += float(weight)
    mode = max(mode_weights.items(), key=lambda item: item[1])[0]
    mode_ranked = [(distance, candidate) for distance, candidate in ranked if candidate["roll_mode"] == mode]
    if not mode_ranked:
        return None
    selected = mode_ranked[:MODE_NEIGHBOR_COUNT]
    selected_dist = np.asarray([distance for distance, _ in selected], dtype=float)
    selected_weights = 1.0 / np.maximum(selected_dist, 1e-6)
    selected_weights = selected_weights / float(np.sum(selected_weights))
    comps = np.asarray([candidate["roll_components"] for _, candidate in selected], dtype=float)
    return {
        "mode": mode,
        "mode_weight": float(mode_weights[mode]),
        "mode_count": int(len(mode_ranked)),
        "candidate_count": int(len(candidates)),
        "best_distance": float(selected_dist[0]),
        "mean_distance": float(np.sum(selected_weights * selected_dist)),
        "top1_components": comps[0],
        "median_components": np.median(comps, axis=0),
        "weighted_components": np.sum(selected_weights[:, None] * comps, axis=0),
    }


def terrain_value_from_components(row, components, branch):
    arrival_vec = rotate_vec(row["surface_vec"], components_to_omega(row["surface_vec"], components))
    arrival_ara = vec_to_ara(arrival_vec)
    terrain = read_fractal_terrain(arrival_ara, row["ara_current"], roll_terms(row))
    if branch == "arrival":
        return ara_to_value(arrival_ara), terrain, arrival_ara
    force_ara = clamp(
        terrain["arrival_ara"] + terrain["weighted_slope"] * terrain["force_gain"],
        0.0,
        2.0,
    )
    return ara_to_value(force_ara), terrain, arrival_ara


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
    fractal_comparison = load_comparison_predictions(FRACTAL_JSON, ["fractal_phi_force"])
    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    direction_scores = {key: {} for key in MODEL_KEYS}
    amplitude = {key: {} for key in MODEL_KEYS}
    ready_point_scores = {key: {} for key in MODEL_KEYS}
    ready_direction_scores = {key: {} for key in MODEL_KEYS}
    ready_amplitude = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA roll displacement mode predictor")
    print("=" * 100)
    print("strict guards: completed roll displacement modes only; no direct future coordinate ridge")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in data["records_by_horizon"][h]]
        for row in records:
            row["surface_vec"] = row_surface_vec(row)
            row["target_vec"] = row_target_vec(row)
            row["features"] = surface_features(row)
            row["roll_components"] = log_roll_components(row["surface_vec"], row["target_vec"])
            row["roll_mode"] = mode_label(row)

        for row in records:
            key = (row["origin"], row["target"])
            row["persistence_pred"] = row["current"]
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            row["raw_address_top1_pred"] = raw_comparison.get(h, {}).get(key, {}).get(
                "raw_address_top1", row["current"]
            )
            row["fractal_phi_force_pred"] = fractal_comparison.get(h, {}).get(key, {}).get(
                "fractal_phi_force", row["current"]
            )
            pred = predict_roll_mode(records, row)
            if pred is None:
                row["mode_ready"] = False
                row["predicted_mode"] = None
                row["mode_weight"] = None
                row["mode_best_distance"] = None
                row["mode_arrival_ara"] = None
                for branch in ["top1_fractal", "median_fractal", "weighted_fractal", "top1_arrival"]:
                    row[f"mode_{branch}_pred"] = row["current"]
                continue

            top1_value, top1_terrain, top1_ara = terrain_value_from_components(row, pred["top1_components"], "force")
            median_value, _, _ = terrain_value_from_components(row, pred["median_components"], "force")
            weighted_value, _, _ = terrain_value_from_components(row, pred["weighted_components"], "force")
            arrival_value, _, _ = terrain_value_from_components(row, pred["top1_components"], "arrival")

            row["mode_ready"] = True
            row["predicted_mode"] = pred["mode"]
            row["mode_weight"] = pred["mode_weight"]
            row["mode_count"] = pred["mode_count"]
            row["mode_best_distance"] = pred["best_distance"]
            row["mode_mean_distance"] = pred["mean_distance"]
            row["mode_arrival_ara"] = top1_ara
            row["mode_spillover"] = top1_terrain["spillover"]
            row["mode_force"] = top1_terrain["force"]
            row["mode_top1_fractal_pred"] = top1_value
            row["mode_median_fractal_pred"] = median_value
            row["mode_weighted_fractal_pred"] = weighted_value
            row["mode_top1_arrival_pred"] = arrival_value

        score_keys = {
            "persistence": "persistence_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "raw_address_top1": "raw_address_top1_pred",
            "fractal_phi_force": "fractal_phi_force_pred",
            "mode_top1_fractal": "mode_top1_fractal_pred",
            "mode_median_fractal": "mode_median_fractal_pred",
            "mode_weighted_fractal": "mode_weighted_fractal_pred",
            "mode_top1_arrival": "mode_top1_arrival_pred",
        }
        ready = [row for row in records if row["mode_ready"]]
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
            "mean_mode_weight": float(np.mean([row["mode_weight"] for row in ready])) if ready else None,
            "mean_best_distance": float(np.mean([row["mode_best_distance"] for row in ready])) if ready else None,
            "mean_arrival_ara": float(np.mean([row["mode_arrival_ara"] for row in ready])) if ready else None,
            "mean_spillover": float(np.mean([row["mode_spillover"] for row in ready])) if ready else None,
        }

        records_by_h[h] = [
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": rounded(row["current"]),
                "actual": rounded(row["actual"]),
                "wobble_surface_analog": rounded(row["wobble_surface_analog_pred"]),
                "raw_address_top1": rounded(row["raw_address_top1_pred"]),
                "fractal_phi_force": rounded(row["fractal_phi_force_pred"]),
                "mode_top1_fractal": rounded(row["mode_top1_fractal_pred"]),
                "mode_median_fractal": rounded(row["mode_median_fractal_pred"]),
                "mode_weighted_fractal": rounded(row["mode_weighted_fractal_pred"]),
                "mode_top1_arrival": rounded(row["mode_top1_arrival_pred"]),
                "predicted_mode": row["predicted_mode"],
                "mode_weight": rounded(row["mode_weight"]) if row["mode_weight"] is not None else None,
                "mode_arrival_ara": rounded(row["mode_arrival_ara"]) if row["mode_arrival_ara"] is not None else None,
                "mode_spillover": rounded(row["mode_spillover"]) if row.get("mode_spillover") is not None else None,
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
            f"  mode diagnostics         ready={diagnostics[h]['ready_fraction']:.3f}"
            f" mode_w={diagnostics[h]['mean_mode_weight'] if diagnostics[h]['mean_mode_weight'] is not None else float('nan'):.3f}"
            f" arrive={diagnostics[h]['mean_arrival_ara'] if diagnostics[h]['mean_arrival_ara'] is not None else float('nan'):.3f}"
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
        "method": "strict-causal roll displacement mode predictor",
        "source": "TheFormula/ara_sphere_atlas_data.json",
        "leakage_guard": [
            "Candidate roll displacements are eligible only when candidate target is before current origin t.",
            "The model predicts/apply roll displacement components, not final future native values.",
            "Mode locking prevents averaging incompatible roll directions before applying displacement.",
            "The terrain read is deterministic fractal ARA terrain; no future geometry oracle or visual shift is used.",
            "No lag ridge or native-value decoder is used.",
            "Non-ready rows fall back to persistence.",
        ],
        "roll_mode_rule": {
            "components": "axis-angle roll from current surface vector to actual future vector, expressed in the current local north/east/radial basis",
            "mode": "coarse signs of ARA direction, forward roll, lateral roll, twist, and sub-ARA spillover",
            "prediction": "nearest completed current states vote a mode; top-1/median/weighted displacement inside that mode is applied to current pose",
        },
        "horizons_months": HORIZONS,
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
        "window.ARA_ROLL_DISPLACEMENT_MODE = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
