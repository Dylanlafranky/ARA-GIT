"""
ara_raw_terrain_address_lookup.py

Strict-causal raw terrain address lookup.

The prior sphere-orientation model still averaged many surface neighbours,
which washes amplitude out. This test keeps the orientation step, but reads the
terrain map as an address:

    predict future sphere pose
    find nearest raw stored terrain coordinate
    return that raw value

Top-1 is the primary framework-faithful branch. Top-3 median / weighted top-3
are controls for very small interpolation without turning the map into a
smoothed analogue average.
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
    load_sphere_baselines,
    predict_ridge,
    roll_vector,
    row_surface_vec,
    row_target_vec,
    rotate_vec,
    sign,
    surface_features,
    unit,
    vec_to_ara,
)
from ara_sphere_topology_direction_predictor import month_index


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
OUT_JSON = HERE / "ara_raw_terrain_address_lookup_result.json"
OUT_JS = HERE / "ara_raw_terrain_address_lookup_result.js"

MIN_ADDRESS_POINTS = 12
ADDRESS_TOP_K = 3

MODEL_KEYS = [
    "persistence",
    "wobble_surface_analog",
    "sphere_nested2_level",
    "roll_learned_average",
    "raw_address_top1",
    "raw_address_top3_median",
    "raw_address_top3_weighted",
    "contact_address_top1",
]


def surface_distance(target_vec, candidate):
    dot = float(np.clip(np.dot(unit(target_vec), unit(candidate["surface_vec"])), -1.0, 1.0))
    sphere_dist = math.acos(dot) / math.pi
    ara_dist = abs(float(candidate["ara_current"]) - vec_to_ara(target_vec)) / 2.0
    return float(math.sqrt(max(0.0, sphere_dist * sphere_dist + 0.45 * ara_dist * ara_dist)))


def address_candidates(records, row):
    origin_m = month_index(row["origin"])
    return [candidate for candidate in records if month_index(candidate["origin"]) < origin_m]


def raw_address_lookup(records, row, target_vec):
    candidates = address_candidates(records, row)
    if len(candidates) < MIN_ADDRESS_POINTS:
        return None
    ranked = sorted([(surface_distance(target_vec, candidate), candidate) for candidate in candidates], key=lambda item: item[0])
    nearest = ranked[:ADDRESS_TOP_K]
    values = np.asarray([candidate["current"] for _, candidate in nearest], dtype=float)
    distances = np.asarray([distance for distance, _ in nearest], dtype=float)
    weights = 1.0 / np.maximum(distances, 1e-6)
    weights = weights / float(np.sum(weights))
    return {
        "top1": float(values[0]),
        "top3_median": float(np.median(values)),
        "top3_weighted": float(np.sum(weights * values)),
        "top1_distance": float(distances[0]),
        "top3_distance": float(np.mean(distances)),
        "candidate_count": int(len(candidates)),
        "top1_origin": nearest[0][1]["origin"],
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
    return {
        "n": int(len(records)),
        "pred_delta_std": pred_std,
        "truth_delta_std": truth_std,
        "std_ratio": pred_std / truth_std if truth_std > EPS else None,
        "abs_delta_ratio": float(np.mean(np.abs(pred_delta)) / np.mean(np.abs(truth_delta)))
        if float(np.mean(np.abs(truth_delta))) > EPS
        else None,
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
    amplitude = {key: {} for key in MODEL_KEYS}
    ready_point_scores = {key: {} for key in MODEL_KEYS}
    ready_direction_scores = {key: {} for key in MODEL_KEYS}
    ready_amplitude = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA raw terrain address lookup")
    print("=" * 100)
    print("strict guards: learned future pose, then top-1/top-3 raw surface address; no averaging branch as primary")
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
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            row["sphere_nested2_level_pred"] = sphere_baselines.get(h, {}).get((row["origin"], row["target"]), row["current"])
            # Comparison against the earlier many-neighbour average is loaded from the
            # sphere result when available; otherwise use persistence.
            row["roll_learned_average_pred"] = row["current"]

            target_vec = learned_target_vec(records, row)
            contact_vec = rotate_vec(row["surface_vec"], roll_vector(row, "contact"))
            learned = raw_address_lookup(records, row, target_vec) if target_vec is not None else None
            contact = raw_address_lookup(records, row, contact_vec)

            if learned is None:
                row["raw_address_ready"] = False
                for key in ["top1", "top3_median", "top3_weighted"]:
                    row[f"raw_address_{key}_pred"] = row["current"]
                row["raw_address_top1_distance"] = None
                row["raw_address_top3_distance"] = None
                row["raw_address_candidate_count"] = 0
                row["raw_address_top1_origin"] = None
            else:
                row["raw_address_ready"] = True
                row["raw_address_top1_pred"] = learned["top1"]
                row["raw_address_top3_median_pred"] = learned["top3_median"]
                row["raw_address_top3_weighted_pred"] = learned["top3_weighted"]
                row["raw_address_top1_distance"] = learned["top1_distance"]
                row["raw_address_top3_distance"] = learned["top3_distance"]
                row["raw_address_candidate_count"] = learned["candidate_count"]
                row["raw_address_top1_origin"] = learned["top1_origin"]

            if contact is None:
                row["contact_address_top1_pred"] = row["current"]
            else:
                row["contact_address_top1_pred"] = contact["top1"]

        # Pull the averaged learned roll values from the previous result for exact
        # apples-to-apples scoring when present.
        previous = {}
        prior_path = HERE / "ara_sphere_orientation_roll_result.json"
        if prior_path.exists():
            prior = json.loads(prior_path.read_text(encoding="utf-8"))
            previous = {
                (row["origin"], row["target"]): row["roll_learned_surface"]
                for row in prior.get("viz_records", {}).get(h, [])
            }
        for row in records:
            row["roll_learned_average_pred"] = previous.get((row["origin"], row["target"]), row["current"])

        score_keys = {
            "persistence": "persistence_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "sphere_nested2_level": "sphere_nested2_level_pred",
            "roll_learned_average": "roll_learned_average_pred",
            "raw_address_top1": "raw_address_top1_pred",
            "raw_address_top3_median": "raw_address_top3_median_pred",
            "raw_address_top3_weighted": "raw_address_top3_weighted_pred",
            "contact_address_top1": "contact_address_top1_pred",
        }
        ready = [row for row in records if row["raw_address_ready"]]
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
            "mean_candidate_count": float(np.mean([row["raw_address_candidate_count"] for row in ready])) if ready else None,
            "mean_top1_distance": float(np.mean([row["raw_address_top1_distance"] for row in ready])) if ready else None,
            "mean_top3_distance": float(np.mean([row["raw_address_top3_distance"] for row in ready])) if ready else None,
        }

        records_by_h[h] = [
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": rounded(row["current"]),
                "actual": rounded(row["actual"]),
                "wobble_surface_analog": rounded(row["wobble_surface_analog_pred"]),
                "sphere_nested2_level": rounded(row["sphere_nested2_level_pred"]),
                "roll_learned_average": rounded(row["roll_learned_average_pred"]),
                "raw_address_top1": rounded(row["raw_address_top1_pred"]),
                "raw_address_top3_median": rounded(row["raw_address_top3_median_pred"]),
                "raw_address_top3_weighted": rounded(row["raw_address_top3_weighted_pred"]),
                "contact_address_top1": rounded(row["contact_address_top1_pred"]),
                "raw_address_top1_distance": rounded(row["raw_address_top1_distance"])
                if row["raw_address_top1_distance"] is not None
                else None,
                "raw_address_top1_origin": row["raw_address_top1_origin"],
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
            f"  raw diagnostics          ready={diagnostics[h]['ready_fraction']:.3f}"
            f" top1_dist={diagnostics[h]['mean_top1_distance'] if diagnostics[h]['mean_top1_distance'] is not None else float('nan'):.3f}"
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
        "method": "strict-causal raw terrain address lookup",
        "source": "TheFormula/ara_sphere_atlas_data.json",
        "orientation_source": "TheFormula/ara_sphere_orientation_roll_predictor.py",
        "leakage_guard": [
            "Learned future pose trains only on completed historical rows whose target is before current origin t.",
            "Raw address lookup reads only historical origin-surface points before current origin t.",
            "Top-1 raw lookup is the primary branch; top-3 median/weighted are small interpolation controls.",
            "No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.",
            "Non-ready rows fall back to persistence.",
        ],
        "address_rule": {
            "top1": "nearest raw stored terrain coordinate to predicted future pose",
            "top3_median": "median of the nearest three raw stored terrain values",
            "top3_weighted": "inverse-distance weighted nearest three raw stored terrain values",
        },
        "horizons_months": HORIZONS,
        "min_address_points": MIN_ADDRESS_POINTS,
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
        "window.ARA_RAW_TERRAIN_ADDRESS = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
