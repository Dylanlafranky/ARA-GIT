"""
ara_wobble_terrain_arrival_predictor.py

Strict-causal follow-up to the terrain-arrival analog test.

The prior test assumed a repeating terrain signature. This version treats the
measured water-slice frame as a local 3-axis surface on a wobbling sphere:

    x = downstream / topology-arrival tilt
    y = lateral bank / ridge-channel tilt
    z = vertical sea/backpressure / lift-sink tilt

The analog search matches current terrain position plus recent wobble velocity
and curvature, including lower-subsystem spin components. Older states are
eligible only when their own future target is already before the current origin.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_cross_rung_spin_transfer_test import (
    HOME,
    HORIZONS,
    LOWER_PERIODS,
    MIN_TRAIN,
    ORIGIN_STRIDE,
    TIME_TO_TRANSITION_WINDOW,
    UPPER_PERIODS,
)
from ara_geometry_transport_test import START_YEAR, clean_for_json, load_enso_frame
from ara_lag_phase_hybrid_predictor import extended_score, finite, format_score, point
from ara_raw_watershed_lower_spin_test import corrected_lower_spin_terms
from ara_raw_watershed_slice_test import (
    aggregate_focus,
    class_transition,
    future_boundary_crossing,
    raw_delta,
    rounded,
    sign,
    squash,
)


OUT_JSON = HERE / "ara_wobble_terrain_arrival_result.json"
OUT_JS = HERE / "ara_wobble_terrain_arrival_result.js"

MODEL_KEYS = [
    "persistence",
    "terrain_level_analog",
    "wobble_level_analog",
    "wobble_delta_analog",
    "wobble_surface_analog",
]

NEIGHBOR_COUNT = 40
MIN_ANALOG_TRAIN = 48
DISTANCE_BANDWIDTH = 2.35
EPS = 1e-9

FEATURE_WEIGHTS = {
    "x": 1.60,
    "y": 1.10,
    "z": 1.05,
    "torsion": 0.85,
    "x_v3": 1.45,
    "y_v3": 0.95,
    "z_v3": 1.00,
    "x_v6": 0.95,
    "y_v6": 0.65,
    "z_v6": 0.70,
    "x_curve": 1.15,
    "y_curve": 0.75,
    "z_curve": 0.80,
    "nino_spin": 1.05,
    "soi_spin": 1.00,
    "pdo_spin": 0.55,
    "nino_spin_v3": 0.75,
    "soi_spin_v3": 0.70,
    "spin_torsion": 0.85,
    "raw_nino": 0.85,
    "raw_soi": 0.25,
    "raw_pdo": 0.20,
    "boundary_gate": 0.70,
    "turbulence": 0.50,
}


def terrain_axes(terms):
    x = squash(
        0.46 * terms["topology_arrival"]
        + 0.30 * terms["lower_spin_torque"]
        + 0.24 * terms["raw_flow"],
        1.25,
    )
    y = squash(
        0.38 * (terms["channel_ara"] - 1.0)
        + 0.28 * terms["phi_valley_pull"]
        + 0.22 * (2.0 * terms["boundary_gate"] - 1.0)
        + 0.12 * terms["ridge_proximity"],
        1.20,
    )
    z = squash(
        0.46 * terms["sea_backpressure"]
        + 0.22 * terms["home_inertia"]
        + 0.20 * terms["lower_alignment"]
        - 0.12 * terms["turbulence"],
        1.35,
    )
    torsion = squash(
        terms["lower_spin_torque"] * terms["lower_alignment"]
        - 0.45 * terms["sea_backpressure"] * (2.0 * terms["boundary_gate"] - 1.0)
        - 0.25 * terms["turbulence"],
        1.0,
    )
    return {"x": float(x), "y": float(y), "z": float(z), "torsion": float(torsion)}


def subsystem_spin(frame, anchor):
    parts = {"nino": [], "soi": [], "pdo": []}
    for period in LOWER_PERIODS:
        weight = HOME / float(period)
        lag = int(round(period))
        parts["nino"].append(weight * squash(raw_delta(frame, "NINO", anchor, lag), 0.80))
        parts["soi"].append(weight * squash(-raw_delta(frame, "SOI", anchor, lag), 1.80))
        parts["pdo"].append(weight * squash(raw_delta(frame, "PDO", anchor, lag), 2.10))
    nino_spin = float(np.mean(parts["nino"]))
    soi_spin = float(np.mean(parts["soi"]))
    pdo_spin = float(np.mean(parts["pdo"]))
    return {
        "nino_spin": nino_spin,
        "soi_spin": soi_spin,
        "pdo_spin": pdo_spin,
        "spin_torsion": float(squash(nino_spin - soi_spin + 0.35 * pdo_spin, 1.5)),
    }


def axis_state(frame, anchor, horizon):
    terms = corrected_lower_spin_terms(frame, anchor, horizon)
    out = terrain_axes(terms)
    out.update(subsystem_spin(frame, anchor))
    out.update(
        {
            "raw_nino": float(terms["raw_nino"]),
            "raw_soi": float(terms["raw_soi"]),
            "raw_pdo": float(terms["raw_pdo"]),
            "boundary_gate": float(terms["boundary_gate"]),
            "turbulence": float(terms["turbulence"]),
            "unit_delta": float(terms["unit_delta"]),
        }
    )
    return out


def wobble_signature(frame, anchor, horizon):
    now = axis_state(frame, anchor, horizon)
    lag3 = axis_state(frame, anchor - 3, horizon)
    lag6 = axis_state(frame, anchor - 6, horizon)

    out = {key: now[key] for key in ["x", "y", "z", "torsion", "raw_nino", "raw_soi", "raw_pdo", "boundary_gate", "turbulence"]}
    for key in ["x", "y", "z"]:
        out[f"{key}_v3"] = now[key] - lag3[key]
        out[f"{key}_v6"] = now[key] - lag6[key]
        out[f"{key}_curve"] = now[key] - 2.0 * lag3[key] + lag6[key]
    for key in ["nino_spin", "soi_spin", "pdo_spin", "spin_torsion"]:
        out[key] = now[key]
    out["nino_spin_v3"] = now["nino_spin"] - lag3["nino_spin"]
    out["soi_spin_v3"] = now["soi_spin"] - lag3["soi_spin"]
    out["unit_delta"] = now["unit_delta"]
    return out


def robust_center_scale(records):
    centers = {}
    scales = {}
    for key in FEATURE_WEIGHTS:
        values = np.asarray([row["wobble"][key] for row in records], dtype=float)
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        std = float(np.std(values))
        centers[key] = center
        scales[key] = max(1e-6, 1.4826 * mad, 0.25 * std)
    return centers, scales


def analog_candidates(records, record):
    return [
        candidate
        for candidate in records
        if candidate["target_anchor"] < record["origin_anchor"]
        and candidate["origin_anchor"] < record["origin_anchor"]
    ]


def weighted_distance(record, candidate, centers, scales):
    total = 0.0
    total_w = 0.0
    for key, weight in FEATURE_WEIGHTS.items():
        diff = ((record["wobble"][key] - centers[key]) - (candidate["wobble"][key] - centers[key])) / scales[key]
        total += weight * diff * diff
        total_w += weight
    distance = math.sqrt(total / max(total_w, EPS))

    penalties = 0.0
    for key, penalty in [("x", 0.55), ("x_v3", 0.85), ("nino_spin", 0.45), ("soi_spin", 0.40), ("torsion", 0.35)]:
        a = sign(record["wobble"][key])
        b = sign(candidate["wobble"][key])
        if a != 0 and b != 0 and a != b:
            penalties += penalty
    return float(distance + penalties)


def terrain_level_baseline(records, record):
    candidates = analog_candidates(records, record)
    if len(candidates) < MIN_ANALOG_TRAIN:
        return None

    base_weights = {
        "raw_nino": 1.20,
        "raw_soi": 0.35,
        "raw_pdo": 0.25,
        "x": 1.60,
        "y": 1.10,
        "z": 1.05,
        "boundary_gate": 0.70,
        "turbulence": 0.50,
    }
    centers = {}
    scales = {}
    for key in base_weights:
        values = np.asarray([row["wobble"][key] for row in candidates], dtype=float)
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        std = float(np.std(values))
        centers[key] = center
        scales[key] = max(1e-6, 1.4826 * mad, 0.25 * std)

    ranked = []
    for candidate in candidates:
        total = 0.0
        total_w = 0.0
        for key, weight in base_weights.items():
            diff = ((record["wobble"][key] - centers[key]) - (candidate["wobble"][key] - centers[key])) / scales[key]
            total += weight * diff * diff
            total_w += weight
        ranked.append((math.sqrt(total / max(total_w, EPS)), candidate))
    ranked.sort(key=lambda row: row[0])
    nearest = ranked[:36]
    weights = np.asarray([math.exp(-0.5 * (distance / 2.15) ** 2) for distance, _ in nearest], dtype=float)
    weights = weights / max(float(np.sum(weights)), EPS)
    return float(np.sum(weights * np.asarray([candidate["actual"] for _, candidate in nearest], dtype=float)))


def wobble_prediction(records, record):
    candidates = analog_candidates(records, record)
    if len(candidates) < MIN_ANALOG_TRAIN:
        return None

    centers, scales = robust_center_scale(candidates)
    ranked = sorted(
        [(weighted_distance(record, candidate, centers, scales), candidate) for candidate in candidates],
        key=lambda row: row[0],
    )
    nearest = ranked[:NEIGHBOR_COUNT]
    weights = np.asarray([math.exp(-0.5 * (distance / DISTANCE_BANDWIDTH) ** 2) for distance, _ in nearest], dtype=float)
    if float(np.sum(weights)) <= EPS:
        weights = np.ones(len(nearest), dtype=float)
    weights = weights / float(np.sum(weights))

    neighbors = [candidate for _, candidate in nearest]
    actual = np.asarray([candidate["actual"] for candidate in neighbors], dtype=float)
    delta = np.asarray([candidate["actual"] - candidate["current"] for candidate in neighbors], dtype=float)
    unit = np.asarray([candidate["wobble"]["unit_delta"] for candidate in neighbors], dtype=float)
    x = np.asarray([candidate["wobble"]["x"] for candidate in neighbors], dtype=float)
    y = np.asarray([candidate["wobble"]["y"] for candidate in neighbors], dtype=float)
    z = np.asarray([candidate["wobble"]["z"] for candidate in neighbors], dtype=float)

    mean_actual = float(np.sum(weights * actual))
    mean_delta = float(np.sum(weights * delta))
    mean_unit = float(np.sum(weights * unit))
    level_pred = mean_actual
    delta_pred = float(record["current"] + mean_delta)

    surface_correction = (
        0.22 * (record["wobble"]["x"] - float(np.sum(weights * x)))
        - 0.10 * (record["wobble"]["y"] - float(np.sum(weights * y)))
        + 0.08 * (record["wobble"]["z"] - float(np.sum(weights * z)))
        + 0.18 * (record["wobble"]["unit_delta"] - mean_unit)
    )
    surface_pred = max(-4.0, min(4.0, level_pred + surface_correction))

    orientation_matches = []
    for candidate in neighbors:
        same_x = sign(record["wobble"]["x_v3"]) == sign(candidate["wobble"]["x_v3"])
        same_spin = sign(record["wobble"]["nino_spin"]) == sign(candidate["wobble"]["nino_spin"])
        same_torsion = sign(record["wobble"]["torsion"]) == sign(candidate["wobble"]["torsion"])
        orientation_matches.append(1.0 if same_x and same_spin and same_torsion else 0.0)

    return {
        "wobble_level_analog_pred": level_pred,
        "wobble_delta_analog_pred": delta_pred,
        "wobble_surface_analog_pred": surface_pred,
        "wobble_neighbor_count": int(len(neighbors)),
        "wobble_candidate_count": int(len(candidates)),
        "wobble_mean_distance": float(np.sum(weights * np.asarray([row[0] for row in nearest], dtype=float))),
        "wobble_best_distance": float(nearest[0][0]),
        "wobble_orientation_match": float(np.sum(weights * np.asarray(orientation_matches, dtype=float))),
    }


def add_outcome_labels(records):
    for record in records:
        record["boundary_crossing"] = bool(future_boundary_crossing(record))
        record["enso_class_transition"] = bool(class_transition(record))
        record["large_move"] = bool(abs(record["actual"] - record["current"]) >= 0.5)


def add_predictions(records):
    for record in records:
        record["persistence_pred"] = record["current"]
        record["terrain_level_analog_pred"] = terrain_level_baseline(records, record)
        pred = wobble_prediction(records, record)
        if pred is None or record["terrain_level_analog_pred"] is None:
            fallback = record["current"] + record["wobble"]["unit_delta"]
            record["terrain_level_analog_pred"] = fallback
            record["wobble_level_analog_pred"] = fallback
            record["wobble_delta_analog_pred"] = fallback
            record["wobble_surface_analog_pred"] = fallback
            record["wobble_ready"] = False
            record["wobble_neighbor_count"] = 0
            record["wobble_candidate_count"] = 0
            record["wobble_mean_distance"] = None
            record["wobble_best_distance"] = None
            record["wobble_orientation_match"] = None
            continue
        record.update(pred)
        record["wobble_ready"] = True


def point_records(records, pred_key):
    return [point(r["origin_date"], r["target_date"], r[pred_key], r["actual"], r["current"]) for r in records]


def transition_subset(records):
    return [r for r in records if r.get("boundary_crossing") or r.get("enso_class_transition") or r.get("large_move")]


def diagnostic_summary(records):
    ready = [r for r in records if r.get("wobble_ready")]
    if not ready:
        return {}
    return {
        "ready_fraction": float(len(ready) / len(records)),
        "mean_candidate_count": float(np.mean([r["wobble_candidate_count"] for r in ready])),
        "mean_distance": float(np.mean([r["wobble_mean_distance"] for r in ready if r["wobble_mean_distance"] is not None])),
        "mean_orientation_match": float(
            np.mean([r["wobble_orientation_match"] for r in ready if r["wobble_orientation_match"] is not None])
        ),
    }


def build_records(frame, h, dates, nino_raw, n, min_anchor, test_start):
    records = []
    origins = list(range(min_anchor + max(HORIZONS) + 1, n - h + 1, ORIGIN_STRIDE))
    for origin in origins:
        target_anchor = origin + h
        if target_anchor > n:
            continue
        records.append(
            {
                "horizon": int(h),
                "origin_anchor": int(origin),
                "target_anchor": int(target_anchor),
                "origin_date": dates[origin - 1].strftime("%Y-%m-%d"),
                "target_date": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                "is_test": bool(origin >= test_start),
                "current": float(nino_raw[origin - 1]),
                "actual": float(nino_raw[target_anchor - 1]),
                "wobble": wobble_signature(frame, origin, h),
            }
        )
    add_outcome_labels(records)
    add_predictions(records)
    return records


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    nino_raw = frame["NINO"].values.astype(float)
    n = len(frame)
    max_h = max(HORIZONS)
    max_lag = int(math.ceil(max(UPPER_PERIODS + LOWER_PERIODS))) + 8
    min_anchor = max_lag + 1
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + MIN_TRAIN + TIME_TO_TRANSITION_WINDOW + max_h + 1)

    print("ARA wobble terrain arrival predictor")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("strict guards: raw samples <= t; analog outcomes require s+h < t; no decoder; no lag ridge")
    print()

    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    transition_scores = {key: {} for key in MODEL_KEYS}
    diagnostics = {}
    pred_keys = {
        "persistence": "persistence_pred",
        "terrain_level_analog": "terrain_level_analog_pred",
        "wobble_level_analog": "wobble_level_analog_pred",
        "wobble_delta_analog": "wobble_delta_analog_pred",
        "wobble_surface_analog": "wobble_surface_analog_pred",
    }

    for h in HORIZONS:
        records = build_records(frame, h, dates, nino_raw, n, min_anchor, test_start)
        eval_records = [r for r in records if r["is_test"] and r.get("wobble_ready")]
        trans_records = transition_subset(eval_records)
        records_by_h[str(h)] = eval_records
        diagnostics[str(h)] = diagnostic_summary(eval_records)
        for key, pred_key in pred_keys.items():
            point_scores[key][str(h)] = extended_score(point_records(eval_records, pred_key))
            transition_scores[key][str(h)] = extended_score(point_records(trans_records, pred_key))

        print(f"h={h:>2} months")
        for key in MODEL_KEYS:
            print(f"  {key:24s} {format_score(point_scores[key][str(h)])}")
        diag = diagnostics[str(h)]
        print(
            f"  wobble diagnostics       ready={diag.get('ready_fraction', float('nan')):.3f}"
            f" candidates={diag.get('mean_candidate_count', float('nan')):.1f}"
            f" dist={diag.get('mean_distance', float('nan')):.3f}"
            f" orient={diag.get('mean_orientation_match', float('nan')):.3f}"
        )
        print()

    focus_horizons = [6, 12, 24]
    focus = {
        "point_scores": {key: aggregate_focus(point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "transition_scores": {key: aggregate_focus(transition_scores[key], focus_horizons) for key in MODEL_KEYS},
    }

    observed_series = [{"date": dates[i].strftime("%Y-%m-%d"), "nino": rounded(nino_raw[i])} for i in range(n)]
    viz_records = {
        h: [
            {
                "origin": r["origin_date"],
                "target": r["target_date"],
                "current": rounded(r["current"]),
                "actual": rounded(r["actual"]),
                "persistence": rounded(r["persistence_pred"]),
                "terrain_level_analog": rounded(r["terrain_level_analog_pred"]),
                "wobble_level_analog": rounded(r["wobble_level_analog_pred"]),
                "wobble_delta_analog": rounded(r["wobble_delta_analog_pred"]),
                "wobble_surface_analog": rounded(r["wobble_surface_analog_pred"]),
                "x": rounded(r["wobble"]["x"]),
                "y": rounded(r["wobble"]["y"]),
                "z": rounded(r["wobble"]["z"]),
                "x_v3": rounded(r["wobble"]["x_v3"]),
                "y_v3": rounded(r["wobble"]["y_v3"]),
                "z_v3": rounded(r["wobble"]["z_v3"]),
                "torsion": rounded(r["wobble"]["torsion"]),
                "nino_spin": rounded(r["wobble"]["nino_spin"]),
                "soi_spin": rounded(r["wobble"]["soi_spin"]),
                "wobble_mean_distance": rounded(r["wobble_mean_distance"]) if r["wobble_mean_distance"] is not None else None,
                "wobble_orientation_match": rounded(r["wobble_orientation_match"])
                if r["wobble_orientation_match"] is not None
                else None,
            }
            for r in records
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal 3-axis wobble terrain-arrival analogue predictor",
        "leakage_guard": [
            "Every terrain/wobble feature at origin t uses only raw samples <= t.",
            "Analog neighbors are eligible only when their future target s+h is before the current origin t.",
            "No decoder, lag ridge, future geometry oracle, smoothing, z-score transform, or visual shift is used for scores.",
        ],
        "axis_definition": {
            "x": "downstream/topology-arrival tilt",
            "y": "lateral bank/ridge-channel tilt",
            "z": "vertical sea/backpressure/lift-sink tilt",
            "torsion": "coupled spin/sea twist of the local surface",
        },
        "feature_weights": FEATURE_WEIGHTS,
        "neighbor_count": NEIGHBOR_COUNT,
        "min_analog_train": MIN_ANALOG_TRAIN,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
            "min_anchor": int(min_anchor),
        },
        "point_scores": clean_for_json(point_scores),
        "transition_scores": clean_for_json(transition_scores),
        "diagnostics": clean_for_json(diagnostics),
        "focus_6_12_24": clean_for_json(focus),
        "observed_series": clean_for_json(observed_series),
        "viz_records": clean_for_json(viz_records),
        "elapsed_seconds": rounded(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_WOBBLE_TERRAIN_ARRIVAL = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24 point scores:")
    for key, score in focus["point_scores"].items():
        print(
            f"  {key:24s}"
            f" MAE={score.get('mae'):.3f}"
            f" corr={score.get('corr'):+.3f}"
            f" turn={score.get('turn_accuracy'):.3f}"
            f" transition_mae={score.get('transition_mae'):.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
