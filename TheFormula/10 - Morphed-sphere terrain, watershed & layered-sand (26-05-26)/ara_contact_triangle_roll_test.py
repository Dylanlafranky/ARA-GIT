"""
ara_contact_triangle_roll_test.py

Strict-causal test of rolling contact through local sphere triangles.

The hypothesis is not "lower rungs are extra features." It is:

    lower/faster layers roll first
    each layer induces the next layer with a parity/orientation flip
    local neighbouring spheres constrain the roll through triangle contact
    the water slice then traverses the terrain that arrives from that contact

This script uses the existing ARA sphere atlas as the current terrain map and
tests whether contact-pair/contact-triangle matching improves future direction
or level lookup. It uses no lag ridge, no decoder, no future geometry, no
smoothing, and no visual shift.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np

from ara_geometry_transport_test import clean_for_json
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, rounded
from ara_shape_kernel_test import PHI
from ara_sphere_topology_direction_predictor import (
    ARA_MARKS,
    EPS,
    eligible_candidates,
    localize_ara,
    month_index,
    nested_ara_distance,
    phase_value,
    sign,
    sphere_distance,
    sphere_vec,
)


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
SPHERE_TOPOLOGY_JSON = HERE / "ara_sphere_topology_direction_result.json"
OUT_JSON = HERE / "ara_contact_triangle_roll_result.json"
OUT_JS = HERE / "ara_contact_triangle_roll_result.js"

HORIZONS = [3, 6, 12, 18, 24]
MIN_NEIGHBORS = 48
NEIGHBOR_COUNT = 42
DISTANCE_BANDWIDTH = 1.25

MODEL_KEYS = [
    "persistence",
    "terrain_level_analog",
    "wobble_surface_analog",
    "sphere_nested2_level",
    "contact_pair_level",
    "contact_triangle_level",
    "contact_triangle_delta",
    "contact_roll_level",
]

PAIR_WEIGHTS = {
    "lower_drive": 0.95,
    "contact_pressure": 0.80,
    "home_roll": 0.95,
    "upper_gate": 0.55,
    "lower_home_parity": 0.75,
    "home_upper_parity": 0.60,
    "neighbor_opposition": 0.45,
    "roll_chain": 0.70,
    "wobble_x": 0.70,
    "wobble_y": 0.45,
    "wobble_z": 0.55,
    "torsion": 0.75,
}

TRIANGLE_WEIGHTS = {
    **PAIR_WEIGHTS,
    "triangle_area": 0.90,
    "triangle_compactness": 0.80,
    "triangle_handedness": 0.85,
    "lower_home_side": 0.70,
    "home_constraint_side": 0.65,
    "lower_constraint_side": 0.55,
    "contact_normal_x": 0.50,
    "contact_normal_y": 0.35,
    "contact_normal_z": 0.50,
    "local_surface_alignment": 0.65,
}


def safe_tanh(value, scale=1.0):
    return float(math.tanh(float(value) / max(scale, EPS)))


def unit_vector(vec):
    vec = np.asarray(vec, dtype=float)
    norm = float(np.linalg.norm(vec))
    if norm <= EPS:
        return np.zeros_like(vec)
    return vec / norm


def contact_phase(row, mode, spin_term=0.0, flip=False):
    phase = phase_value(row, mode)
    turn = 18.0 * safe_tanh(spin_term, 3.0)
    if flip:
        turn *= -1.0
    return (phase + turn) % 360.0


def triangle_geometry(row):
    wobble = row["wobble"]
    lower_drive_raw = float(wobble["nino_spin"]) - float(wobble["soi_spin"])
    home_roll_raw = float(wobble["x_v3"]) + 0.38 * float(wobble["torsion"])
    upper_gate_raw = float(wobble["z_v3"]) + 0.30 * float(wobble["z"])

    # The lower layer induces the home layer in the opposite rolling direction.
    lower_phase = contact_phase(row, "flow", lower_drive_raw, flip=True)
    # The neighbouring/constraint sphere is read through torsion and SOI opposition.
    constraint_phase = contact_phase(row, "torsion", float(wobble["soi_spin"]) - float(wobble["nino_spin"]))
    home_phase = phase_value(row, "clock")

    home = sphere_vec(row["ara_current"], home_phase)
    lower = sphere_vec(row["ara_current"], lower_phase)
    constraint = sphere_vec(row["ara_current"], constraint_phase)

    lower_home = lower - home
    home_constraint = constraint - home
    lower_constraint = constraint - lower
    a = float(np.linalg.norm(lower_home))
    b = float(np.linalg.norm(home_constraint))
    c = float(np.linalg.norm(lower_constraint))
    perimeter = max(a + b + c, EPS)
    s = 0.5 * perimeter
    area = math.sqrt(max(0.0, s * (s - a) * (s - b) * (s - c)))
    compactness = 4.0 * math.sqrt(3.0) * area / max(perimeter * perimeter, EPS)

    normal = unit_vector(np.cross(lower_home, home_constraint))
    surface = unit_vector([wobble["x"], wobble["y"], wobble["z"]])
    handedness = float(np.dot(home, np.cross(lower, constraint)))

    lower_home_parity = sign(-lower_drive_raw) * sign(home_roll_raw)
    home_upper_parity = sign(-home_roll_raw) * sign(upper_gate_raw)
    neighbor_opposition = sign(wobble["nino_spin"]) * sign(wobble["soi_spin"])

    return {
        "lower_drive": safe_tanh(lower_drive_raw, 3.0),
        "contact_pressure": safe_tanh(abs(wobble["nino_spin"]) + abs(wobble["soi_spin"]), 5.0),
        "home_roll": safe_tanh(home_roll_raw, 1.2),
        "upper_gate": safe_tanh(upper_gate_raw, 1.4),
        "lower_home_parity": float(lower_home_parity),
        "home_upper_parity": float(home_upper_parity),
        "neighbor_opposition": float(neighbor_opposition),
        "roll_chain": float(lower_home_parity * home_upper_parity),
        "wobble_x": float(wobble["x"]),
        "wobble_y": float(wobble["y"]),
        "wobble_z": float(wobble["z"]),
        "torsion": float(wobble["torsion"]),
        "triangle_area": float(area),
        "triangle_compactness": float(compactness),
        "triangle_handedness": safe_tanh(handedness, 0.45),
        "lower_home_side": float(a),
        "home_constraint_side": float(b),
        "lower_constraint_side": float(c),
        "contact_normal_x": float(normal[0]),
        "contact_normal_y": float(normal[1]),
        "contact_normal_z": float(normal[2]),
        "local_surface_alignment": float(np.dot(normal, surface)),
    }


def enrich_records(records):
    for row in records:
        row["contact"] = triangle_geometry(row)
    return records


def robust_center_scale(rows, keys):
    centers = {}
    scales = {}
    for key in keys:
        values = np.asarray([row["contact"][key] for row in rows], dtype=float)
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        std = float(np.std(values))
        centers[key] = center
        scales[key] = max(1e-6, 1.4826 * mad, 0.25 * std)
    return centers, scales


def scalar_distance(a, b, weights, centers, scales):
    total = 0.0
    total_w = 0.0
    for key, weight in weights.items():
        diff = ((a["contact"][key] - centers[key]) - (b["contact"][key] - centers[key])) / scales[key]
        total += weight * diff * diff
        total_w += weight
    return total / max(total_w, EPS)


def contact_distance(a, b, weights, centers, scales, use_triangle):
    distance = 1.15 * sphere_distance(a, b)
    distance += 0.72 * nested_ara_distance(a, b, depth=2)
    distance += 0.90 * scalar_distance(a, b, weights, centers, scales)

    penalties = 0.0
    parity_keys = ["lower_home_parity", "home_upper_parity", "roll_chain", "neighbor_opposition"]
    for key in parity_keys:
        va = sign(a["contact"][key])
        vb = sign(b["contact"][key])
        if va and vb and va != vb:
            penalties += 0.22
    if use_triangle:
        if sign(a["contact"]["triangle_handedness"]) and sign(b["contact"]["triangle_handedness"]):
            if sign(a["contact"]["triangle_handedness"]) != sign(b["contact"]["triangle_handedness"]):
                penalties += 0.28
        if sign(a["contact"]["local_surface_alignment"]) and sign(b["contact"]["local_surface_alignment"]):
            if sign(a["contact"]["local_surface_alignment"]) != sign(b["contact"]["local_surface_alignment"]):
                penalties += 0.18
    return math.sqrt(max(0.0, distance)) + penalties


def weighted_lookup(records, row, weights, use_triangle):
    candidates = eligible_candidates(records, row)
    if len(candidates) < MIN_NEIGHBORS:
        return None

    centers, scales = robust_center_scale(candidates, weights.keys())
    ranked = sorted(
        [(contact_distance(row, candidate, weights, centers, scales, use_triangle), candidate) for candidate in candidates],
        key=lambda item: item[0],
    )
    nearest = ranked[:NEIGHBOR_COUNT]
    kernel = np.asarray([math.exp(-0.5 * (dist / DISTANCE_BANDWIDTH) ** 2) for dist, _ in nearest], dtype=float)
    if float(np.sum(kernel)) <= EPS:
        kernel = np.ones(len(nearest), dtype=float)
    kernel = kernel / float(np.sum(kernel))

    neighbors = [candidate for _, candidate in nearest]
    actual = np.asarray([candidate["actual"] for candidate in neighbors], dtype=float)
    delta = np.asarray([candidate["actual"] - candidate["current"] for candidate in neighbors], dtype=float)
    directions = np.asarray([sign(candidate["actual"] - candidate["current"]) for candidate in neighbors], dtype=float)
    distances = np.asarray([dist for dist, _ in nearest], dtype=float)

    direction_vote = float(np.sum(kernel * directions))
    return {
        "level_pred": float(np.sum(kernel * actual)),
        "delta_pred": float(row["current"] + np.sum(kernel * delta)),
        "direction_vote": direction_vote,
        "confidence": abs(direction_vote),
        "candidate_count": int(len(candidates)),
        "neighbor_count": int(len(neighbors)),
        "mean_distance": float(np.sum(kernel * distances)),
        "best_distance": float(nearest[0][0]),
    }


def contact_roll_level(row, pred):
    base = pred["level_pred"]
    vote = pred["direction_vote"]
    # Bounded current-contact correction: let parity/contact pressure nudge the
    # level, but keep the topology lookup as the main term.
    pressure = row["contact"]["contact_pressure"]
    chain = row["contact"]["roll_chain"]
    surface = row["contact"]["local_surface_alignment"]
    correction = 0.16 * vote * pressure + 0.08 * chain + 0.06 * surface
    return float(max(-4.0, min(4.0, base + correction)))


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

    print("ARA contact triangle roll test")
    print("=" * 100)
    print("strict guards: current contact geometry only; analog outcomes require s+h < t; no decoder or lag")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        records = enrich_records([dict(row) for row in data["records_by_horizon"][h]])
        for row in records:
            row["persistence_pred"] = row["current"]
            row["terrain_level_analog_pred"] = row["terrain_level_analog"]
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            row["sphere_nested2_level_pred"] = sphere_baselines.get(h, {}).get(
                (row["origin"], row["target"]),
                row["current"],
            )

            pair = weighted_lookup(records, row, PAIR_WEIGHTS, use_triangle=False)
            triangle = weighted_lookup(records, row, TRIANGLE_WEIGHTS, use_triangle=True)
            for prefix, pred in [("contact_pair", pair), ("contact_triangle", triangle)]:
                if pred is None:
                    row[f"{prefix}_level_pred"] = row["current"]
                    row[f"{prefix}_delta_pred"] = row["current"]
                    row[f"{prefix}_roll_level_pred"] = row["current"]
                    row[f"{prefix}_direction_vote"] = 0.0
                    row[f"{prefix}_confidence"] = 0.0
                    row[f"{prefix}_candidate_count"] = 0
                    row[f"{prefix}_mean_distance"] = None
                    row[f"{prefix}_best_distance"] = None
                    continue
                row[f"{prefix}_level_pred"] = pred["level_pred"]
                row[f"{prefix}_delta_pred"] = pred["delta_pred"]
                row[f"{prefix}_roll_level_pred"] = contact_roll_level(row, pred)
                row[f"{prefix}_direction_vote"] = pred["direction_vote"]
                row[f"{prefix}_confidence"] = pred["confidence"]
                row[f"{prefix}_candidate_count"] = pred["candidate_count"]
                row[f"{prefix}_mean_distance"] = pred["mean_distance"]
                row[f"{prefix}_best_distance"] = pred["best_distance"]

        score_keys = {
            "persistence": "persistence_pred",
            "terrain_level_analog": "terrain_level_analog_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "sphere_nested2_level": "sphere_nested2_level_pred",
            "contact_pair_level": "contact_pair_level_pred",
            "contact_triangle_level": "contact_triangle_level_pred",
            "contact_triangle_delta": "contact_triangle_delta_pred",
            "contact_roll_level": "contact_triangle_roll_level_pred",
        }
        ready = [row for row in records if row["contact_triangle_candidate_count"] > 0]
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
            "mean_candidate_count": float(np.mean([row["contact_triangle_candidate_count"] for row in ready])) if ready else None,
            "mean_distance": float(np.mean([row["contact_triangle_mean_distance"] for row in ready])) if ready else None,
            "mean_confidence": float(np.mean([row["contact_triangle_confidence"] for row in ready])) if ready else None,
            "mean_lower_home_parity": float(np.mean([row["contact"]["lower_home_parity"] for row in records])),
            "mean_home_upper_parity": float(np.mean([row["contact"]["home_upper_parity"] for row in records])),
            "mean_triangle_compactness": float(np.mean([row["contact"]["triangle_compactness"] for row in records])),
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
                "contact_pair_level": rounded(row["contact_pair_level_pred"]),
                "contact_triangle_level": rounded(row["contact_triangle_level_pred"]),
                "contact_triangle_delta": rounded(row["contact_triangle_delta_pred"]),
                "contact_roll_level": rounded(row["contact_triangle_roll_level_pred"]),
                "contact_direction_vote": rounded(row["contact_triangle_direction_vote"]),
                "contact_confidence": rounded(row["contact_triangle_confidence"]),
                "contact_mean_distance": rounded(row["contact_triangle_mean_distance"])
                if row["contact_triangle_mean_distance"] is not None
                else None,
                "lower_home_parity": rounded(row["contact"]["lower_home_parity"]),
                "home_upper_parity": rounded(row["contact"]["home_upper_parity"]),
                "roll_chain": rounded(row["contact"]["roll_chain"]),
                "triangle_compactness": rounded(row["contact"]["triangle_compactness"]),
                "triangle_handedness": rounded(row["contact"]["triangle_handedness"]),
                "local_surface_alignment": rounded(row["contact"]["local_surface_alignment"]),
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
            f"  contact diagnostics      ready={diagnostics[h]['ready_fraction']:.3f}"
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
        "method": "strict-causal contact triangle roll topology lookup",
        "source": "TheFormula/ara_sphere_atlas_data.json",
        "baseline_source": "TheFormula/ara_sphere_topology_direction_result.json",
        "leakage_guard": [
            "Every contact feature at origin t uses only current-origin sphere/wobble/spin values.",
            "Analog neighbours are eligible only when their target s+h is before the current origin t.",
            "No decoder, lag ridge, future geometry oracle, smoothing, or visual shift is used.",
            "Non-ready rows fall back to persistence.",
        ],
        "contact_model": {
            "lower_to_home": "lower/faster spin induces home roll with one orientation flip",
            "home_to_upper": "home roll and upper/constraint gate are compared with a second orientation flip",
            "triangle": "home sphere point + induced lower contact point + torsion/neighbor constraint point",
            "nested_ara": {
                "bands": ARA_MARKS,
                "depth": 2,
                "reason": "two ARA-in-ARA layers was the best previous sphere-topology depth",
            },
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
        "window.ARA_CONTACT_TRIANGLE_ROLL = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
