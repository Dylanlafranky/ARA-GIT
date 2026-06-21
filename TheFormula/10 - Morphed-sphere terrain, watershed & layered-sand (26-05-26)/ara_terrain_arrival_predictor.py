"""
ara_terrain_arrival_predictor.py

Strict-causal test of the "terrain comes around again" interpretation.

The previous lower-spin watershed formula appears to reconstruct the terrain
slice at the origin very well, but the phase-delay diagnostic showed it is not
advancing that terrain to the forecast date. This script treats that formula as
a current terrain extractor, then predicts future terrain by historical
recurrence:

    current raw data <= t
    -> lower-spin terrain signature S(t)
    -> search only older completed signatures S(s), where s+h < t
    -> average what those older terrains looked like at s+h
    -> forecast at t+h

No decoder or lag ridge is used. The only learning-like operation is a causal
nearest-terrain analogue lookup whose outcomes were already known at origin t.
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
    rounded,
    sign,
)


OUT_JSON = HERE / "ara_terrain_arrival_predictor_result.json"
OUT_JS = HERE / "ara_terrain_arrival_predictor_result.js"

MODEL_KEYS = [
    "persistence",
    "lower_spin_formula",
    "terrain_delta_analog",
    "terrain_level_analog",
    "terrain_erosion_analog",
]

FEATURE_WEIGHTS = {
    "raw_nino": 1.20,
    "raw_soi": 0.35,
    "raw_pdo": 0.25,
    "channel_ara": 0.70,
    "phi_valley_pull": 0.55,
    "ridge_proximity": 0.65,
    "enso_boundary": 0.75,
    "home_inertia": 0.85,
    "lower_spin_torque": 1.65,
    "lower_spin_pressure": 0.85,
    "lower_alignment": 0.95,
    "topology_arrival": 1.65,
    "sea_backpressure": 0.45,
    "sea_reservoir": 0.35,
    "boundary_gate": 0.85,
    "turbulence": 0.65,
    "raw_flow": 1.35,
}

NEIGHBOR_COUNT = 36
MIN_ANALOG_TRAIN = 48
DISTANCE_BANDWIDTH = 2.15
EPS = 1e-9


def terrain_signature(record):
    terms = record["watershed"]
    return {key: finite(terms.get(key, 0.0)) for key in FEATURE_WEIGHTS}


def robust_center_scale(candidates):
    centers = {}
    scales = {}
    for key in FEATURE_WEIGHTS:
        values = np.asarray([terrain_signature(row)[key] for row in candidates], dtype=float)
        center = float(np.median(values))
        mad = float(np.median(np.abs(values - center)))
        std = float(np.std(values))
        scale = max(1e-6, 1.4826 * mad, 0.25 * std)
        centers[key] = center
        scales[key] = scale
    return centers, scales


def weighted_distance(current, candidate, centers, scales):
    cur = terrain_signature(current)
    cand = terrain_signature(candidate)
    total_w = 0.0
    total = 0.0
    for key, weight in FEATURE_WEIGHTS.items():
        diff = ((cur[key] - centers[key]) - (cand[key] - centers[key])) / scales[key]
        total += weight * diff * diff
        total_w += weight

    distance = math.sqrt(total / max(total_w, EPS))
    cur_terms = current["watershed"]
    cand_terms = candidate["watershed"]

    cur_flow_sign = sign(cur_terms["raw_flow"])
    cand_flow_sign = sign(cand_terms["raw_flow"])
    cur_spin_sign = sign(cur_terms["lower_spin_torque"])
    cand_spin_sign = sign(cand_terms["lower_spin_torque"])
    cur_sea_sign = sign(cur_terms["sea_backpressure"])
    cand_sea_sign = sign(cand_terms["sea_backpressure"])

    orientation_penalty = 0.0
    if cur_flow_sign != 0 and cand_flow_sign != 0 and cur_flow_sign != cand_flow_sign:
        orientation_penalty += 0.90
    if cur_spin_sign != 0 and cand_spin_sign != 0 and cur_spin_sign != cand_spin_sign:
        orientation_penalty += 0.55
    if cur_sea_sign != 0 and cand_sea_sign != 0 and cur_sea_sign != cand_sea_sign:
        orientation_penalty += 0.20

    return float(distance + orientation_penalty)


def analog_candidates(records, record):
    return [
        candidate
        for candidate in records
        if candidate["target_anchor"] < record["origin_anchor"]
        and candidate["origin_anchor"] < record["origin_anchor"]
    ]


def analog_prediction(records, record):
    candidates = analog_candidates(records, record)
    if len(candidates) < MIN_ANALOG_TRAIN:
        return None

    centers, scales = robust_center_scale(candidates)
    ranked = []
    for candidate in candidates:
        distance = weighted_distance(record, candidate, centers, scales)
        ranked.append((distance, candidate))
    ranked.sort(key=lambda row: row[0])
    nearest = ranked[:NEIGHBOR_COUNT]

    weights = np.asarray(
        [math.exp(-0.5 * (distance / DISTANCE_BANDWIDTH) ** 2) for distance, _ in nearest],
        dtype=float,
    )
    if float(np.sum(weights)) <= EPS:
        weights = np.ones(len(nearest), dtype=float)
    weights = weights / float(np.sum(weights))

    neighbors = [candidate for _, candidate in nearest]
    neighbor_current = np.asarray([candidate["current"] for candidate in neighbors], dtype=float)
    neighbor_actual = np.asarray([candidate["actual"] for candidate in neighbors], dtype=float)
    neighbor_delta = neighbor_actual - neighbor_current
    neighbor_unit = np.asarray([candidate["watershed"]["unit_delta"] for candidate in neighbors], dtype=float)

    current_unit = float(record["watershed"]["unit_delta"])
    mean_neighbor_current = float(np.sum(weights * neighbor_current))
    mean_neighbor_actual = float(np.sum(weights * neighbor_actual))
    mean_neighbor_delta = float(np.sum(weights * neighbor_delta))
    mean_neighbor_unit = float(np.sum(weights * neighbor_unit))

    delta_pred = float(record["current"] + mean_neighbor_delta)
    level_pred = mean_neighbor_actual
    erosion_pred = float(delta_pred + 0.33 * (current_unit - mean_neighbor_unit))
    erosion_pred = max(-4.0, min(4.0, erosion_pred))

    orientation_matches = []
    for candidate in neighbors:
        same_flow = sign(record["watershed"]["raw_flow"]) == sign(candidate["watershed"]["raw_flow"])
        same_spin = sign(record["watershed"]["lower_spin_torque"]) == sign(candidate["watershed"]["lower_spin_torque"])
        orientation_matches.append(1.0 if same_flow and same_spin else 0.0)

    return {
        "terrain_delta_analog_pred": delta_pred,
        "terrain_level_analog_pred": float(level_pred),
        "terrain_erosion_analog_pred": erosion_pred,
        "analog_neighbor_count": int(len(neighbors)),
        "analog_candidate_count": int(len(candidates)),
        "analog_mean_distance": float(np.sum(weights * np.asarray([row[0] for row in nearest], dtype=float))),
        "analog_best_distance": float(nearest[0][0]),
        "analog_orientation_match": float(np.sum(weights * np.asarray(orientation_matches, dtype=float))),
        "analog_mean_neighbor_current": mean_neighbor_current,
        "analog_mean_neighbor_actual": mean_neighbor_actual,
        "analog_mean_neighbor_delta": mean_neighbor_delta,
        "analog_mean_neighbor_unit_delta": mean_neighbor_unit,
        "analog_current_unit_delta": current_unit,
    }


def add_outcome_labels(records):
    for record in records:
        record["boundary_crossing"] = bool(future_boundary_crossing(record))
        record["enso_class_transition"] = bool(class_transition(record))
        record["large_move"] = bool(abs(record["actual"] - record["current"]) >= 0.5)
        record["persistence_abs_error"] = abs(record["current"] - record["actual"])


def add_predictions(records):
    for record in records:
        record["persistence_pred"] = record["current"]
        record["lower_spin_formula_pred"] = record["current"] + finite(record["watershed"]["unit_delta"])

        pred = analog_prediction(records, record)
        if pred is None:
            record["terrain_delta_analog_pred"] = record["lower_spin_formula_pred"]
            record["terrain_level_analog_pred"] = record["lower_spin_formula_pred"]
            record["terrain_erosion_analog_pred"] = record["lower_spin_formula_pred"]
            record["analog_ready"] = False
            record["analog_neighbor_count"] = 0
            record["analog_candidate_count"] = 0
            record["analog_mean_distance"] = None
            record["analog_best_distance"] = None
            record["analog_orientation_match"] = None
            record["analog_mean_neighbor_delta"] = None
            record["analog_current_unit_delta"] = finite(record["watershed"]["unit_delta"])
            record["analog_mean_neighbor_unit_delta"] = None
            continue

        record.update(pred)
        record["analog_ready"] = True


def point_records(records, pred_key):
    return [point(r["origin_date"], r["target_date"], r[pred_key], r["actual"], r["current"]) for r in records]


def transition_subset(records):
    return [r for r in records if r.get("boundary_crossing") or r.get("enso_class_transition") or r.get("large_move")]


def diagnostic_summary(records):
    ready = [r for r in records if r.get("analog_ready")]
    if not ready:
        return {}
    return {
        "ready_fraction": float(len(ready) / len(records)),
        "mean_neighbor_count": float(np.mean([r["analog_neighbor_count"] for r in ready])),
        "mean_candidate_count": float(np.mean([r["analog_candidate_count"] for r in ready])),
        "mean_distance": float(np.mean([r["analog_mean_distance"] for r in ready if r["analog_mean_distance"] is not None])),
        "mean_best_distance": float(np.mean([r["analog_best_distance"] for r in ready if r["analog_best_distance"] is not None])),
        "mean_orientation_match": float(
            np.mean([r["analog_orientation_match"] for r in ready if r["analog_orientation_match"] is not None])
        ),
        "mean_current_minus_neighbor_unit": float(
            np.mean(
                [
                    r["analog_current_unit_delta"] - r["analog_mean_neighbor_unit_delta"]
                    for r in ready
                    if r["analog_mean_neighbor_unit_delta"] is not None
                ]
            )
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
                "watershed": corrected_lower_spin_terms(frame, origin, h),
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
    max_lag = int(math.ceil(max(UPPER_PERIODS + LOWER_PERIODS))) + 2
    min_anchor = max_lag + 1
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + MIN_TRAIN + TIME_TO_TRANSITION_WINDOW + max_h + 1)

    print("ARA terrain arrival predictor")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("strict guards: raw samples <= t; analog outcomes require s+h < t; no decoder; no lag ridge")
    print()

    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    transition_scores = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    for h in HORIZONS:
        records = build_records(frame, h, dates, nino_raw, n, min_anchor, test_start)
        eval_records = [r for r in records if r["is_test"] and r.get("analog_ready")]
        trans_records = transition_subset(eval_records)
        records_by_h[str(h)] = eval_records
        diagnostics[str(h)] = diagnostic_summary(eval_records)

        score_key_map = {
            "persistence": "persistence_pred",
            "lower_spin_formula": "lower_spin_formula_pred",
            "terrain_delta_analog": "terrain_delta_analog_pred",
            "terrain_level_analog": "terrain_level_analog_pred",
            "terrain_erosion_analog": "terrain_erosion_analog_pred",
        }
        for key, pred_key in score_key_map.items():
            point_scores[key][str(h)] = extended_score(point_records(eval_records, pred_key))
            transition_scores[key][str(h)] = extended_score(point_records(trans_records, pred_key))

        print(f"h={h:>2} months")
        for key in MODEL_KEYS:
            print(f"  {key:24s} {format_score(point_scores[key][str(h)])}")
        diag = diagnostics[str(h)]
        print(
            f"  analog diagnostics        ready={diag.get('ready_fraction', float('nan')):.3f}"
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
                "lower_spin_formula": rounded(r["lower_spin_formula_pred"]),
                "terrain_delta_analog": rounded(r["terrain_delta_analog_pred"]),
                "terrain_level_analog": rounded(r["terrain_level_analog_pred"]),
                "terrain_erosion_analog": rounded(r["terrain_erosion_analog_pred"]),
                "boundary_crossing": bool(r["boundary_crossing"]),
                "enso_class_transition": bool(r["enso_class_transition"]),
                "large_move": bool(r["large_move"]),
                "lower_spin_torque": rounded(r["watershed"]["lower_spin_torque"]),
                "topology_arrival": rounded(r["watershed"]["topology_arrival"]),
                "sea_backpressure": rounded(r["watershed"]["sea_backpressure"]),
                "boundary_gate": rounded(r["watershed"]["boundary_gate"]),
                "turbulence": rounded(r["watershed"]["turbulence"]),
                "raw_flow": rounded(r["watershed"]["raw_flow"]),
                "analog_mean_distance": rounded(r["analog_mean_distance"]) if r["analog_mean_distance"] is not None else None,
                "analog_best_distance": rounded(r["analog_best_distance"]) if r["analog_best_distance"] is not None else None,
                "analog_orientation_match": rounded(r["analog_orientation_match"])
                if r["analog_orientation_match"] is not None
                else None,
                "analog_neighbor_count": int(r["analog_neighbor_count"]),
                "analog_candidate_count": int(r["analog_candidate_count"]),
                "analog_current_unit_delta": rounded(r["analog_current_unit_delta"]),
                "analog_mean_neighbor_unit_delta": rounded(r["analog_mean_neighbor_unit_delta"])
                if r["analog_mean_neighbor_unit_delta"] is not None
                else None,
            }
            for r in records
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal terrain-arrival analogue predictor from raw lower-spin watershed signatures",
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "leakage_guard": [
            "Every terrain feature at origin t uses only raw samples <= t.",
            "Analog neighbors are eligible only when their future target s+h is before the current origin t.",
            "No decoder, lag ridge, future geometry oracle, smoothing, z-score transform, or visual shift is used for scores.",
            "The visualizer defaults to target-date alignment; shifted diagnostics are deliberately omitted.",
        ],
        "interpretation": {
            "terrain_delta_analog": "current value plus weighted future deltas from older similar terrain signatures",
            "terrain_level_analog": "weighted future level reached by older similar terrain signatures",
            "terrain_erosion_analog": "terrain_delta_analog plus a fixed symbolic correction for current-vs-neighbor unit_delta difference",
        },
        "feature_weights": FEATURE_WEIGHTS,
        "neighbor_count": NEIGHBOR_COUNT,
        "min_analog_train": MIN_ANALOG_TRAIN,
        "distance_bandwidth": DISTANCE_BANDWIDTH,
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
        "window.ARA_TERRAIN_ARRIVAL_PREDICTOR = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
    print("Focus 6/12/24 transition-window scores:")
    for key, score in focus["transition_scores"].items():
        print(
            f"  {key:24s}"
            f" MAE={score.get('mae'):.3f}"
            f" corr={score.get('corr'):+.3f}"
            f" turn={score.get('turn_accuracy'):.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
