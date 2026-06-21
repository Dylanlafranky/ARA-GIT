"""
ara_sphere_topology_direction_predictor.py

Strict-causal route predictor using the mapped ARA sphere.

Hypothesis:
    If the water-slice visits the same or similar sphere topology, the older
    completed route through that region tells us the likely future direction.

This script tests that as a direction/route analogue:

    current sphere spot at t
    + nested ARA-band-in-ARA-band coordinates
    + local wobble/torsion state
    -> older completed sphere spots s where s+h < t
    -> weighted route direction / future level

No decoder, lag ridge, future geometry oracle, smoothing, or visual shift.
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


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
OUT_JSON = HERE / "ara_sphere_topology_direction_result.json"
OUT_JS = HERE / "ara_sphere_topology_direction_result.js"

HORIZONS = [3, 6, 12, 18, 24]
MIN_NEIGHBORS = 48
NEIGHBOR_COUNT = 42
DISTANCE_BANDWIDTH = 1.18
EPS = 1e-9

ARA_MARKS = [0.0, 2.0 - PHI, 0.5, 1.0, PHI, 2.0]
PHASE_MODES = [
    ("clock", 1.15),
    ("wobble", 0.95),
    ("flow", 0.85),
    ("torsion", 0.65),
]
SCALAR_WEIGHTS = {
    "wobble.x": 0.80,
    "wobble.y": 0.55,
    "wobble.z": 0.70,
    "wobble.x_v3": 0.95,
    "wobble.y_v3": 0.55,
    "wobble.z_v3": 0.70,
    "wobble.torsion": 0.80,
    "wobble.nino_spin": 0.70,
    "wobble.soi_spin": 0.70,
}

MODEL_KEYS = [
    "persistence",
    "terrain_level_analog",
    "wobble_surface_analog",
    "sphere_global_delta",
    "sphere_global_level",
    "sphere_nested2_delta",
    "sphere_nested2_level",
    "sphere_nested3_delta",
    "sphere_nested3_level",
]


def month_index(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.year * 12 + date.month - 1


def sign(value, eps=1e-9):
    value = float(value)
    if value > eps:
        return 1
    if value < -eps:
        return -1
    return 0


def get_nested(row, dotted_key):
    cur = row
    for part in dotted_key.split("."):
        cur = cur[part]
    return float(cur)


def ara_y(ara):
    return 1.0 - max(0.0, min(2.0, float(ara)))


def sphere_vec(ara, phase_deg):
    lon = math.radians(float(phase_deg) % 360.0)
    y = ara_y(ara)
    ring = math.sqrt(max(0.0, 1.0 - y * y))
    return np.asarray([ring * math.cos(lon), y, ring * math.sin(lon)], dtype=float)


def phase_value(row, mode):
    return float(row[f"phase_{mode}_origin"])


def sphere_distance(a, b):
    total = 0.0
    total_w = 0.0
    for mode, weight in PHASE_MODES:
        va = sphere_vec(a["ara_current"], phase_value(a, mode))
        vb = sphere_vec(b["ara_current"], phase_value(b, mode))
        dot = float(np.clip(np.dot(va, vb), -1.0, 1.0))
        total += weight * (1.0 - dot) * 0.5
        total_w += weight
    return total / max(total_w, EPS)


def localize_ara(value):
    value = max(0.0, min(2.0, float(value)))
    for idx in range(len(ARA_MARKS) - 1):
        lo = ARA_MARKS[idx]
        hi = ARA_MARKS[idx + 1]
        if value <= hi or idx == len(ARA_MARKS) - 2:
            frac = 0.0 if hi == lo else (value - lo) / (hi - lo)
            return idx, max(0.0, min(2.0, 2.0 * frac))
    return len(ARA_MARKS) - 2, 2.0


def nested_ara_distance(a, b, depth):
    cur_a = float(a["ara_current"])
    cur_b = float(b["ara_current"])
    total = 0.0
    total_w = 0.0
    for level in range(1, depth + 1):
        band_a, local_a = localize_ara(cur_a)
        band_b, local_b = localize_ara(cur_b)
        weight = 1.0 / math.log2(level + 2.0)
        band_diff = (band_a - band_b) / max(1, len(ARA_MARKS) - 2)
        local_diff = (local_a - local_b) / 2.0
        total += weight * (local_diff * local_diff + 0.22 * band_diff * band_diff)
        total_w += weight
        cur_a = local_a
        cur_b = local_b
    return total / max(total_w, EPS)


def robust_center_scale(candidates):
    centers = {}
    scales = {}
    for key in SCALAR_WEIGHTS:
        values = np.asarray([get_nested(row, key) for row in candidates], dtype=float)
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        std = float(np.std(values))
        centers[key] = center
        scales[key] = max(1e-6, 1.4826 * mad, 0.25 * std)
    return centers, scales


def scalar_distance(a, b, centers, scales):
    total = 0.0
    total_w = 0.0
    for key, weight in SCALAR_WEIGHTS.items():
        diff = ((get_nested(a, key) - centers[key]) - (get_nested(b, key) - centers[key])) / scales[key]
        total += weight * diff * diff
        total_w += weight
    return total / max(total_w, EPS)


def topology_distance(a, b, centers, scales, depth):
    distance = 1.50 * sphere_distance(a, b)
    distance += 0.85 * nested_ara_distance(a, b, depth)
    distance += 0.55 * scalar_distance(a, b, centers, scales)

    penalties = 0.0
    for key, penalty in [
        ("wobble.x_v3", 0.22),
        ("wobble.torsion", 0.18),
        ("wobble.nino_spin", 0.16),
        ("wobble.soi_spin", 0.16),
    ]:
        sa = sign(get_nested(a, key))
        sb = sign(get_nested(b, key))
        if sa and sb and sa != sb:
            penalties += penalty
    return math.sqrt(max(0.0, distance)) + penalties


def eligible_candidates(records, row):
    origin_m = month_index(row["origin"])
    return [candidate for candidate in records if month_index(candidate["target"]) < origin_m]


def predict_from_sphere(records, row, depth):
    candidates = eligible_candidates(records, row)
    if len(candidates) < MIN_NEIGHBORS:
        return None

    centers, scales = robust_center_scale(candidates)
    ranked = sorted(
        [(topology_distance(row, candidate, centers, scales, depth), candidate) for candidate in candidates],
        key=lambda item: item[0],
    )
    nearest = ranked[:NEIGHBOR_COUNT]
    weights = np.asarray([math.exp(-0.5 * (dist / DISTANCE_BANDWIDTH) ** 2) for dist, _ in nearest], dtype=float)
    if float(np.sum(weights)) <= EPS:
        weights = np.ones(len(nearest), dtype=float)
    weights = weights / float(np.sum(weights))
    neighbors = [candidate for _, candidate in nearest]

    deltas = np.asarray([candidate["actual"] - candidate["current"] for candidate in neighbors], dtype=float)
    levels = np.asarray([candidate["actual"] for candidate in neighbors], dtype=float)
    directions = np.asarray([sign(candidate["actual"] - candidate["current"]) for candidate in neighbors], dtype=float)
    distances = np.asarray([dist for dist, _ in nearest], dtype=float)

    mean_delta = float(np.sum(weights * deltas))
    mean_level = float(np.sum(weights * levels))
    direction_vote = float(np.sum(weights * directions))
    confidence = abs(direction_vote)
    return {
        "delta_pred": float(row["current"] + mean_delta),
        "level_pred": mean_level,
        "direction_vote": direction_vote,
        "direction_confidence": confidence,
        "mean_distance": float(np.sum(weights * distances)),
        "best_distance": float(nearest[0][0]),
        "candidate_count": int(len(candidates)),
        "neighbor_count": int(len(neighbors)),
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


def run():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    direction_scores = {key: {} for key in MODEL_KEYS}
    ready_point_scores = {key: {} for key in MODEL_KEYS}
    ready_direction_scores = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA sphere topology direction predictor")
    print("=" * 100)
    print("strict guards: current sphere features only; analog outcomes require s+h < t; no decoder or lag ridge")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        source = data["records_by_horizon"][h]
        records = [dict(row) for row in source]
        for row in records:
            row["persistence_pred"] = row["current"]
            row["terrain_level_analog_pred"] = row["terrain_level_analog"]
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            global_pred = predict_from_sphere(records, row, depth=0)
            nested2 = predict_from_sphere(records, row, depth=2)
            nested3 = predict_from_sphere(records, row, depth=3)
            for prefix, pred in [
                ("sphere_global", global_pred),
                ("sphere_nested2", nested2),
                ("sphere_nested3", nested3),
            ]:
                if pred is None:
                    fallback = row["current"]
                    row[f"{prefix}_delta_pred"] = fallback
                    row[f"{prefix}_level_pred"] = fallback
                    row[f"{prefix}_direction_vote"] = 0.0
                    row[f"{prefix}_confidence"] = 0.0
                    row[f"{prefix}_mean_distance"] = None
                    row[f"{prefix}_best_distance"] = None
                    row[f"{prefix}_candidate_count"] = 0
                    row[f"{prefix}_neighbor_count"] = 0
                else:
                    row[f"{prefix}_delta_pred"] = pred["delta_pred"]
                    row[f"{prefix}_level_pred"] = pred["level_pred"]
                    row[f"{prefix}_direction_vote"] = pred["direction_vote"]
                    row[f"{prefix}_confidence"] = pred["direction_confidence"]
                    row[f"{prefix}_mean_distance"] = pred["mean_distance"]
                    row[f"{prefix}_best_distance"] = pred["best_distance"]
                    row[f"{prefix}_candidate_count"] = pred["candidate_count"]
                    row[f"{prefix}_neighbor_count"] = pred["neighbor_count"]

        score_keys = {
            "persistence": "persistence_pred",
            "terrain_level_analog": "terrain_level_analog_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "sphere_global_delta": "sphere_global_delta_pred",
            "sphere_global_level": "sphere_global_level_pred",
            "sphere_nested2_delta": "sphere_nested2_delta_pred",
            "sphere_nested2_level": "sphere_nested2_level_pred",
            "sphere_nested3_delta": "sphere_nested3_delta_pred",
            "sphere_nested3_level": "sphere_nested3_level_pred",
        }
        for key, pred_key in score_keys.items():
            point_scores[key][h] = extended_score(point_records(records, pred_key))
            direction_scores[key][h] = direction_score(records, pred_key)

        ready = [row for row in records if row["sphere_nested3_candidate_count"] > 0]
        for key, pred_key in score_keys.items():
            ready_point_scores[key][h] = extended_score(point_records(ready, pred_key)) if ready else {}
            ready_direction_scores[key][h] = direction_score(ready, pred_key) if ready else {
                "n": 0,
                "accuracy": None,
                "large_accuracy": None,
                "transition_accuracy": None,
            }
        diagnostics[h] = {
            "ready_fraction": float(len(ready) / len(records)),
            "mean_candidate_count": float(np.mean([row["sphere_nested3_candidate_count"] for row in ready])) if ready else None,
            "mean_distance": float(np.mean([row["sphere_nested3_mean_distance"] for row in ready])) if ready else None,
            "mean_confidence": float(np.mean([row["sphere_nested3_confidence"] for row in ready])) if ready else None,
        }

        records_by_h[h] = [
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": rounded(row["current"]),
                "actual": rounded(row["actual"]),
                "terrain_level_analog": rounded(row["terrain_level_analog_pred"]),
                "wobble_surface_analog": rounded(row["wobble_surface_analog_pred"]),
                "sphere_global_delta": rounded(row["sphere_global_delta_pred"]),
                "sphere_global_level": rounded(row["sphere_global_level_pred"]),
                "sphere_nested2_delta": rounded(row["sphere_nested2_delta_pred"]),
                "sphere_nested2_level": rounded(row["sphere_nested2_level_pred"]),
                "sphere_nested3_delta": rounded(row["sphere_nested3_delta_pred"]),
                "sphere_nested3_level": rounded(row["sphere_nested3_level_pred"]),
                "ara_current": rounded(row["ara_current"]),
                "phase_clock_origin": rounded(row["phase_clock_origin"]),
                "phase_wobble_origin": rounded(row["phase_wobble_origin"]),
                "phase_flow_origin": rounded(row["phase_flow_origin"]),
                "sphere_nested3_direction_vote": rounded(row["sphere_nested3_direction_vote"]),
                "sphere_nested3_confidence": rounded(row["sphere_nested3_confidence"]),
                "sphere_nested3_mean_distance": rounded(row["sphere_nested3_mean_distance"])
                if row["sphere_nested3_mean_distance"] is not None
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
            f"  nested3 diagnostics      ready={diagnostics[h]['ready_fraction']:.3f}"
            f" dist={diagnostics[h]['mean_distance'] if diagnostics[h]['mean_distance'] is not None else float('nan'):.3f}"
            f" conf={diagnostics[h]['mean_confidence'] if diagnostics[h]['mean_confidence'] is not None else float('nan'):.3f}"
        )
        print()

    focus_horizons = [6, 12, 24]
    focus = {
        "point_scores": {key: aggregate_focus(point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "direction_scores": {
            key: {
                "n": int(sum(direction_scores[key][str(h)]["n"] for h in focus_horizons)),
                "accuracy": float(np.mean([direction_scores[key][str(h)]["accuracy"] for h in focus_horizons])),
                "large_accuracy": float(
                    np.mean(
                        [
                            direction_scores[key][str(h)]["large_accuracy"]
                            for h in focus_horizons
                            if direction_scores[key][str(h)]["large_accuracy"] is not None
                        ]
                    )
                ),
                "transition_accuracy": float(
                    np.mean(
                        [
                            direction_scores[key][str(h)]["transition_accuracy"]
                            for h in focus_horizons
                            if direction_scores[key][str(h)]["transition_accuracy"] is not None
                        ]
                    )
                ),
            }
            for key in MODEL_KEYS
        },
        "ready_point_scores": {key: aggregate_focus(ready_point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "ready_direction_scores": {
            key: {
                "n": int(sum(ready_direction_scores[key][str(h)]["n"] for h in focus_horizons)),
                "accuracy": float(np.mean([ready_direction_scores[key][str(h)]["accuracy"] for h in focus_horizons])),
                "large_accuracy": float(
                    np.mean(
                        [
                            ready_direction_scores[key][str(h)]["large_accuracy"]
                            for h in focus_horizons
                            if ready_direction_scores[key][str(h)]["large_accuracy"] is not None
                        ]
                    )
                ),
                "transition_accuracy": float(
                    np.mean(
                        [
                            ready_direction_scores[key][str(h)]["transition_accuracy"]
                            for h in focus_horizons
                            if ready_direction_scores[key][str(h)]["transition_accuracy"] is not None
                        ]
                    )
                ),
            }
            for key in MODEL_KEYS
        },
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal ARA sphere topology direction predictor",
        "source": "TheFormula/ara_sphere_atlas_data.json",
        "leakage_guard": [
            "Every sphere/topology feature at origin t uses only current-origin values exported from the wobble sphere atlas.",
            "Analog neighbors are eligible only when their target s+h is before the current origin t.",
            "No decoder, lag ridge, future geometry oracle, smoothing, or visual shift is used.",
        ],
        "nested_ara_rule": {
            "bands": ARA_MARKS,
            "depths_tested": [0, 2, 3],
            "depth_weight": "1/log2(level+2), so deeper ARA-in-ARA layers contribute logarithmically less",
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
        "window.ARA_SPHERE_TOPOLOGY_DIRECTION = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
