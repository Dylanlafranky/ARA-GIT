"""
ara_rotating_terrain_slice_model.py

Strict-causal test of the "fixed water slice, rotating terrain" idea.

The previous contact-triangle test still matched current feature states. This
one changes the object being matched:

    current water slice at t
    -> estimate which terrain patch rotates/arrives under it by t+h
    -> search older completed target patches that resemble that arrival patch
    -> read the historical target level / direction

No decoder, lag ridge, future geometry oracle, smoothing, or visual shift.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ara_geometry_transport_test import clean_for_json
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, rounded
from ara_shape_kernel_test import PHI
from ara_sphere_topology_direction_predictor import (
    ARA_MARKS,
    EPS,
    localize_ara,
    month_index,
    sign,
    sphere_vec,
)


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
SPHERE_TOPOLOGY_JSON = HERE / "ara_sphere_topology_direction_result.json"
OUT_JSON = HERE / "ara_rotating_terrain_slice_result.json"
OUT_JS = HERE / "ara_rotating_terrain_slice_result.js"

HORIZONS = [3, 6, 12, 18, 24]
MIN_NEIGHBORS = 48
NEIGHBOR_COUNT = 42
DISTANCE_BANDWIDTH = 1.08

MODEL_KEYS = [
    "persistence",
    "terrain_level_analog",
    "wobble_surface_analog",
    "sphere_nested2_level",
    "surface_clock_level",
    "surface_wobble_level",
    "surface_parity_level",
    "arrival_clock_level",
    "arrival_wobble_level",
    "arrival_parity_level",
    "arrival_parity_delta",
]

ARRIVAL_MODE_WEIGHTS = {
    "clock": 1.35,
    "wobble": 0.95,
    "flow": 0.85,
    "torsion": 0.65,
}

ARRIVAL_SCALAR_WEIGHTS = {
    "arrival_ara": 1.25,
    "arrival_ara_local_1": 0.55,
    "arrival_ara_local_2": 0.38,
    "lower_drive": 0.55,
    "home_roll": 0.55,
    "upper_gate": 0.35,
    "roll_parity": 0.55,
    "terrain_width": 0.45,
    "slice_pressure": 0.55,
}


def wrap_deg(value):
    return float(value % 360.0)


def clamp_ara(value):
    return float(max(0.0, min(2.0, value)))


def safe_tanh(value, scale=1.0):
    return float(math.tanh(float(value) / max(scale, EPS)))


def phase_deg(row, key):
    return float(row[key]) % 360.0


def phase_distance_deg(a, b):
    diff = abs((float(a) - float(b) + 180.0) % 360.0 - 180.0)
    return diff / 180.0


def nested_ara_features(value):
    features = {"arrival_ara": clamp_ara(value)}
    cur = clamp_ara(value)
    for level in [1, 2]:
        _, cur = localize_ara(cur)
        features[f"arrival_ara_local_{level}"] = cur
    return features


def current_roll_terms(row):
    wobble = row["wobble"]
    lower_drive = float(wobble["nino_spin"]) - float(wobble["soi_spin"])
    home_roll = float(wobble["x_v3"]) + 0.34 * float(wobble["torsion"])
    upper_gate = float(wobble["z_v3"]) + 0.25 * float(wobble["z"])
    roll_parity = sign(-lower_drive) * sign(home_roll)
    terrain_width = abs(float(wobble["x"])) + 0.65 * abs(float(wobble["y"])) + 0.75 * abs(float(wobble["z"]))
    slice_pressure = abs(lower_drive) + 0.55 * abs(home_roll) + 0.35 * abs(upper_gate)
    return {
        "lower_drive": safe_tanh(lower_drive, 3.0),
        "home_roll": safe_tanh(home_roll, 1.4),
        "upper_gate": safe_tanh(upper_gate, 1.4),
        "roll_parity": float(roll_parity),
        "terrain_width": safe_tanh(terrain_width, 2.0),
        "slice_pressure": safe_tanh(slice_pressure, 5.0),
    }


def arrival_patch(row, variant):
    terms = current_roll_terms(row)
    lower_turn = 24.0 * terms["lower_drive"]
    home_turn = -18.0 * terms["home_roll"]
    upper_turn = 8.0 * terms["upper_gate"]

    if variant == "clock":
        phase_base = float(row["phase_horizon_offset"])
        ara_shift = 0.0
        phase_gain = 0.0
    elif variant == "wobble":
        phase_base = float(row["phase_horizon_offset"])
        ara_shift = 0.18 * terms["home_roll"] + 0.11 * terms["upper_gate"]
        phase_gain = 0.55 * lower_turn + 0.35 * home_turn + 0.15 * upper_turn
    elif variant == "parity":
        phase_base = float(row["phase_horizon_offset"])
        ara_shift = 0.20 * terms["home_roll"] + 0.12 * terms["upper_gate"] + 0.08 * terms["roll_parity"]
        phase_gain = lower_turn + home_turn + upper_turn + 7.0 * terms["roll_parity"]
    else:
        raise ValueError(f"unknown arrival variant {variant}")

    ara = clamp_ara(float(row["ara_current"]) + ara_shift)
    phases = {
        "clock": wrap_deg(phase_deg(row, "phase_clock_origin") + phase_base + (0.20 * phase_gain if variant != "clock" else 0.0)),
        "wobble": wrap_deg(phase_deg(row, "phase_wobble_origin") + phase_base + phase_gain),
        "flow": wrap_deg(phase_deg(row, "phase_flow_origin") + phase_base + 0.85 * phase_gain),
        "torsion": wrap_deg(phase_deg(row, "phase_torsion_origin") + phase_base + 0.65 * phase_gain),
    }
    out = {"ara": ara, "phases": phases, **terms, **nested_ara_features(ara)}
    return out


def observed_target_patch(row):
    terms = current_roll_terms(row)
    ara = clamp_ara(float(row["ara_actual"]))
    # Clock target is the observed target date coordinate. Other longitudes use
    # the same arrival estimate formula from the candidate origin; the candidate
    # target value is known because it is already in the past.
    estimated = arrival_patch(row, "parity")
    phases = {
        "clock": phase_deg(row, "phase_clock_target"),
        "wobble": estimated["phases"]["wobble"],
        "flow": estimated["phases"]["flow"],
        "torsion": estimated["phases"]["torsion"],
    }
    return {"ara": ara, "phases": phases, **terms, **nested_ara_features(ara)}


def observed_surface_patch(row):
    terms = current_roll_terms(row)
    ara = clamp_ara(float(row["ara_current"]))
    phases = {
        "clock": phase_deg(row, "phase_clock_origin"),
        "wobble": phase_deg(row, "phase_wobble_origin"),
        "flow": phase_deg(row, "phase_flow_origin"),
        "torsion": phase_deg(row, "phase_torsion_origin"),
    }
    return {"ara": ara, "phases": phases, **terms, **nested_ara_features(ara)}


def patch_sphere_distance(a_patch, b_patch):
    total = 0.0
    total_w = 0.0
    for mode, weight in ARRIVAL_MODE_WEIGHTS.items():
        va = sphere_vec(a_patch["ara"], a_patch["phases"][mode])
        vb = sphere_vec(b_patch["ara"], b_patch["phases"][mode])
        dot = float(np.clip(np.dot(va, vb), -1.0, 1.0))
        total += weight * (1.0 - dot) * 0.5
        total_w += weight
    return total / max(total_w, EPS)


def robust_center_scale(patches, keys):
    centers = {}
    scales = {}
    for key in keys:
        values = np.asarray([patch[key] for patch in patches], dtype=float)
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        std = float(np.std(values))
        centers[key] = center
        scales[key] = max(1e-6, 1.4826 * mad, 0.25 * std)
    return centers, scales


def patch_scalar_distance(a_patch, b_patch, centers, scales):
    total = 0.0
    total_w = 0.0
    for key, weight in ARRIVAL_SCALAR_WEIGHTS.items():
        diff = ((a_patch[key] - centers[key]) - (b_patch[key] - centers[key])) / scales[key]
        total += weight * diff * diff
        total_w += weight
    return total / max(total_w, EPS)


def patch_distance(a_patch, b_patch, centers, scales, variant):
    distance = 1.55 * patch_sphere_distance(a_patch, b_patch)
    distance += 0.60 * patch_scalar_distance(a_patch, b_patch, centers, scales)

    penalties = 0.0
    if variant == "parity":
        for key, penalty in [("lower_drive", 0.14), ("home_roll", 0.14), ("roll_parity", 0.22)]:
            if sign(a_patch[key]) and sign(b_patch[key]) and sign(a_patch[key]) != sign(b_patch[key]):
                penalties += penalty
    return math.sqrt(max(0.0, distance)) + penalties


def eligible(records, row):
    origin_m = month_index(row["origin"])
    return [candidate for candidate in records if month_index(candidate["target"]) < origin_m]


def surface_candidates(records, row):
    origin_m = month_index(row["origin"])
    return [candidate for candidate in records if month_index(candidate["origin"]) < origin_m]


def rotating_lookup(records, row, variant):
    candidates = eligible(records, row)
    if len(candidates) < MIN_NEIGHBORS:
        return None

    target_patch = arrival_patch(row, variant)
    candidate_patches = [candidate["target_patch"] for candidate in candidates]
    centers, scales = robust_center_scale(candidate_patches, ARRIVAL_SCALAR_WEIGHTS.keys())
    ranked = sorted(
        [
            (
                patch_distance(target_patch, candidate["target_patch"], centers, scales, variant),
                candidate,
            )
            for candidate in candidates
        ],
        key=lambda item: item[0],
    )
    nearest = ranked[:NEIGHBOR_COUNT]
    weights = np.asarray([math.exp(-0.5 * (dist / DISTANCE_BANDWIDTH) ** 2) for dist, _ in nearest], dtype=float)
    if float(np.sum(weights)) <= EPS:
        weights = np.ones(len(nearest), dtype=float)
    weights = weights / float(np.sum(weights))
    neighbors = [candidate for _, candidate in nearest]
    levels = np.asarray([candidate["actual"] for candidate in neighbors], dtype=float)
    deltas = np.asarray([candidate["actual"] - candidate["current"] for candidate in neighbors], dtype=float)
    directions = np.asarray([sign(candidate["actual"] - candidate["current"]) for candidate in neighbors], dtype=float)
    distances = np.asarray([dist for dist, _ in nearest], dtype=float)
    direction_vote = float(np.sum(weights * directions))
    return {
        "level_pred": float(np.sum(weights * levels)),
        "delta_pred": float(row["current"] + np.sum(weights * deltas)),
        "direction_vote": direction_vote,
        "confidence": abs(direction_vote),
        "candidate_count": int(len(candidates)),
        "neighbor_count": int(len(neighbors)),
        "mean_distance": float(np.sum(weights * distances)),
        "best_distance": float(nearest[0][0]),
        "arrival_ara": target_patch["ara"],
        "arrival_clock": target_patch["phases"]["clock"],
        "arrival_wobble": target_patch["phases"]["wobble"],
    }


def surface_lookup(records, row, variant):
    candidates = surface_candidates(records, row)
    if len(candidates) < MIN_NEIGHBORS:
        return None

    target_patch = arrival_patch(row, variant)
    candidate_patches = [candidate["surface_patch"] for candidate in candidates]
    centers, scales = robust_center_scale(candidate_patches, ARRIVAL_SCALAR_WEIGHTS.keys())
    ranked = sorted(
        [
            (
                patch_distance(target_patch, candidate["surface_patch"], centers, scales, variant),
                candidate,
            )
            for candidate in candidates
        ],
        key=lambda item: item[0],
    )
    nearest = ranked[:NEIGHBOR_COUNT]
    weights = np.asarray([math.exp(-0.5 * (dist / DISTANCE_BANDWIDTH) ** 2) for dist, _ in nearest], dtype=float)
    if float(np.sum(weights)) <= EPS:
        weights = np.ones(len(nearest), dtype=float)
    weights = weights / float(np.sum(weights))
    neighbors = [candidate for _, candidate in nearest]
    levels = np.asarray([candidate["current"] for candidate in neighbors], dtype=float)
    directions = np.asarray([sign(candidate["current"] - row["current"]) for candidate in neighbors], dtype=float)
    distances = np.asarray([dist for dist, _ in nearest], dtype=float)
    direction_vote = float(np.sum(weights * directions))
    return {
        "level_pred": float(np.sum(weights * levels)),
        "direction_vote": direction_vote,
        "confidence": abs(direction_vote),
        "candidate_count": int(len(candidates)),
        "neighbor_count": int(len(neighbors)),
        "mean_distance": float(np.sum(weights * distances)),
        "best_distance": float(nearest[0][0]),
    }


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


def run():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    sphere_baselines = load_sphere_baselines()
    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    direction_scores = {key: {} for key in MODEL_KEYS}
    ready_point_scores = {key: {} for key in MODEL_KEYS}
    ready_direction_scores = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA rotating terrain slice model")
    print("=" * 100)
    print("strict guards: estimate arriving terrain patch at t+h; match only older completed target/surface patches")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in data["records_by_horizon"][h]]
        for row in records:
            row["target_patch"] = observed_target_patch(row)
            row["surface_patch"] = observed_surface_patch(row)

        for row in records:
            row["persistence_pred"] = row["current"]
            row["terrain_level_analog_pred"] = row["terrain_level_analog"]
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            row["sphere_nested2_level_pred"] = sphere_baselines.get(h, {}).get((row["origin"], row["target"]), row["current"])

            for variant, prefix in [
                ("clock", "surface_clock"),
                ("wobble", "surface_wobble"),
                ("parity", "surface_parity"),
            ]:
                pred = surface_lookup(records, row, variant)
                if pred is None:
                    row[f"{prefix}_level_pred"] = row["current"]
                    row[f"{prefix}_direction_vote"] = 0.0
                    row[f"{prefix}_confidence"] = 0.0
                    row[f"{prefix}_candidate_count"] = 0
                    row[f"{prefix}_mean_distance"] = None
                    row[f"{prefix}_best_distance"] = None
                    continue
                row[f"{prefix}_level_pred"] = pred["level_pred"]
                row[f"{prefix}_direction_vote"] = pred["direction_vote"]
                row[f"{prefix}_confidence"] = pred["confidence"]
                row[f"{prefix}_candidate_count"] = pred["candidate_count"]
                row[f"{prefix}_mean_distance"] = pred["mean_distance"]
                row[f"{prefix}_best_distance"] = pred["best_distance"]

            for variant, prefix in [
                ("clock", "arrival_clock"),
                ("wobble", "arrival_wobble"),
                ("parity", "arrival_parity"),
            ]:
                pred = rotating_lookup(records, row, variant)
                if pred is None:
                    row[f"{prefix}_level_pred"] = row["current"]
                    row[f"{prefix}_delta_pred"] = row["current"]
                    row[f"{prefix}_direction_vote"] = 0.0
                    row[f"{prefix}_confidence"] = 0.0
                    row[f"{prefix}_candidate_count"] = 0
                    row[f"{prefix}_mean_distance"] = None
                    row[f"{prefix}_best_distance"] = None
                    row[f"{prefix}_arrival_ara"] = None
                    row[f"{prefix}_arrival_clock"] = None
                    row[f"{prefix}_arrival_wobble"] = None
                    continue
                row[f"{prefix}_level_pred"] = pred["level_pred"]
                row[f"{prefix}_delta_pred"] = pred["delta_pred"]
                row[f"{prefix}_direction_vote"] = pred["direction_vote"]
                row[f"{prefix}_confidence"] = pred["confidence"]
                row[f"{prefix}_candidate_count"] = pred["candidate_count"]
                row[f"{prefix}_mean_distance"] = pred["mean_distance"]
                row[f"{prefix}_best_distance"] = pred["best_distance"]
                row[f"{prefix}_arrival_ara"] = pred["arrival_ara"]
                row[f"{prefix}_arrival_clock"] = pred["arrival_clock"]
                row[f"{prefix}_arrival_wobble"] = pred["arrival_wobble"]

        score_keys = {
            "persistence": "persistence_pred",
            "terrain_level_analog": "terrain_level_analog_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "sphere_nested2_level": "sphere_nested2_level_pred",
            "surface_clock_level": "surface_clock_level_pred",
            "surface_wobble_level": "surface_wobble_level_pred",
            "surface_parity_level": "surface_parity_level_pred",
            "arrival_clock_level": "arrival_clock_level_pred",
            "arrival_wobble_level": "arrival_wobble_level_pred",
            "arrival_parity_level": "arrival_parity_level_pred",
            "arrival_parity_delta": "arrival_parity_delta_pred",
        }
        ready = [row for row in records if row["arrival_parity_candidate_count"] > 0]
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
            "mean_candidate_count": float(np.mean([row["arrival_parity_candidate_count"] for row in ready])) if ready else None,
            "mean_distance": float(np.mean([row["arrival_parity_mean_distance"] for row in ready])) if ready else None,
            "mean_confidence": float(np.mean([row["arrival_parity_confidence"] for row in ready])) if ready else None,
            "mean_arrival_ara": float(np.mean([row["arrival_parity_arrival_ara"] for row in ready])) if ready else None,
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
                "surface_clock_level": rounded(row["surface_clock_level_pred"]),
                "surface_wobble_level": rounded(row["surface_wobble_level_pred"]),
                "surface_parity_level": rounded(row["surface_parity_level_pred"]),
                "arrival_clock_level": rounded(row["arrival_clock_level_pred"]),
                "arrival_wobble_level": rounded(row["arrival_wobble_level_pred"]),
                "arrival_parity_level": rounded(row["arrival_parity_level_pred"]),
                "arrival_parity_delta": rounded(row["arrival_parity_delta_pred"]),
                "arrival_direction_vote": rounded(row["arrival_parity_direction_vote"]),
                "arrival_confidence": rounded(row["arrival_parity_confidence"]),
                "arrival_mean_distance": rounded(row["arrival_parity_mean_distance"])
                if row["arrival_parity_mean_distance"] is not None
                else None,
                "arrival_ara": rounded(row["arrival_parity_arrival_ara"])
                if row["arrival_parity_arrival_ara"] is not None
                else None,
                "arrival_clock": rounded(row["arrival_parity_arrival_clock"])
                if row["arrival_parity_arrival_clock"] is not None
                else None,
                "arrival_wobble": rounded(row["arrival_parity_arrival_wobble"])
                if row["arrival_parity_arrival_wobble"] is not None
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
            f"  arrival diagnostics      ready={diagnostics[h]['ready_fraction']:.3f}"
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
        "method": "strict-causal rotating terrain slice lookup",
        "source": "TheFormula/ara_sphere_atlas_data.json",
        "baseline_source": "TheFormula/ara_sphere_topology_direction_result.json",
        "leakage_guard": [
            "Current rows estimate the arriving t+h patch only from current-origin sphere/wobble/spin values and horizon.",
            "Candidate terrain patches use historical target coordinates/values only when candidate target s+h is before current origin t.",
            "No decoder, lag ridge, future geometry oracle, smoothing, or visual shift is used.",
            "Non-ready rows fall back to persistence.",
        ],
        "arrival_model": {
            "slice_frame": "the current water slice is treated as the fixed reading point",
            "terrain_frame": "the sphere surface rotates under the slice by horizon clock plus current wobble/parity corrections",
            "clock_variant": "date/horizon terrain arrival only",
            "wobble_variant": "adds current wobble rotation and estimated ARA drift",
            "parity_variant": "adds lower-to-home orientation flip and upper gate correction",
            "target_lookup": "match estimated current arrival patch to older completed target patches",
            "ara_bands": ARA_MARKS,
        },
        "horizons_months": HORIZONS,
        "neighbor_count": NEIGHBOR_COUNT,
        "min_neighbors": MIN_NEIGHBORS,
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
        "window.ARA_ROTATING_TERRAIN_SLICE = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
