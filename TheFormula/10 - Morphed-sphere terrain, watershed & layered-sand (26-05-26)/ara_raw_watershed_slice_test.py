"""
ara_raw_watershed_slice_test.py

Strict-causal raw-data test of the ARA watershed metaphor.

This version deliberately avoids the smoothed/bandpassed rung state machinery.
It uses the raw ENSO dataframe directly:

    water slice = current raw NINO state
    ARA channel = raw NINO mapped into a 0..2 channel coordinate
    phi valley = low-energy route inside that channel
    tributaries = raw lower-offset NINO/SOI/PDO finite differences
    slow terrain arrival = raw upper-offset finite differences
    ridges = ARA/ENSO boundary proximity

No bandpass, no z-scoring, no rolling averages, no smoothed curve fitting.

Leakage guard:

  - every raw terrain feature at origin t uses only samples <= t.
  - raw watershed flow uses a fixed formula, not future fitting.
  - optional scale/decoder checks at origin t train only on previous records
    whose targets are already known: target_anchor < t.
  - no lag-ridge/native lag feature block is used.
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
    MIN_RISK_TRAIN,
    MIN_TRAIN,
    ORIGIN_STRIDE,
    TIME_TO_TRANSITION_WINDOW,
    UPPER_PERIODS,
    enso_class,
    time_to_transition,
)
from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import START_YEAR, clean_for_json, load_enso_frame
from ara_lag_phase_hybrid_predictor import extended_score, finite, format_score, point
from ara_shape_kernel_test import PHI


OUT_JSON = HERE / "ara_raw_watershed_slice_result.json"
OUT_JS = HERE / "ara_raw_watershed_slice_result.js"

RIDGE_ALPHA_SCALE = 4.0
RIDGE_ALPHA_DECODER = 12.0
HIGH_ERROR_QUANTILE = 0.75
EPS = 1e-9

MODEL_KEYS = [
    "persistence",
    "raw_watershed_formula",
    "raw_watershed_scaled",
    "raw_watershed_decoder",
]

RAW_SCORE_KEYS = [
    "raw_flow",
    "raw_abs_flow",
    "tributary_pressure",
    "boundary_pressure",
    "slow_terrain_arrival",
    "turbulence",
]

RAW_SCORE_TARGETS = [
    "boundary_crossing",
    "enso_class_transition",
    "large_move",
    "persistence_abs_error_high",
]


def rounded(value, digits=6):
    if value is None:
        return None
    return round(finite(value), digits)


def sign(value):
    value = finite(value)
    if value > EPS:
        return 1
    if value < -EPS:
        return -1
    return 0


def squash(value, scale=1.0):
    return math.tanh(finite(value) / max(scale, EPS))


def sigmoid(value):
    value = max(-40.0, min(40.0, finite(value)))
    return 1.0 / (1.0 + math.exp(-value))


def raw_value(frame, name, anchor):
    if anchor <= 0:
        return 0.0
    return finite(frame[name].values[anchor - 1])


def raw_delta(frame, name, anchor, lag):
    lag = int(round(lag))
    prev = anchor - lag
    if prev <= 0:
        return 0.0
    return raw_value(frame, name, anchor) - raw_value(frame, name, prev)


def enso_boundary_distance(value):
    value = finite(value)
    if value >= 0:
        return abs(0.5 - value)
    return abs(-0.5 - value)


def future_boundary_crossing(record):
    return abs(record["current"]) < 0.5 and abs(record["actual"]) >= 0.5


def class_transition(record):
    return enso_class(record["actual"]) != enso_class(record["current"])


def raw_watershed_terms(frame, anchor, horizon):
    nino = raw_value(frame, "NINO", anchor)
    soi = raw_value(frame, "SOI", anchor)
    pdo = raw_value(frame, "PDO", anchor)

    # Raw NINO is mapped into a 0..2 ARA channel only to express the ridge/valley geometry.
    channel_ara = 1.0 + squash(nino, 1.5)
    channel_width = abs(nino) + 0.35 * abs(soi) + 0.25 * abs(pdo)
    phi_valley = (PHI - channel_ara) / PHI
    phi_valley_pull = squash(phi_valley, 0.35)

    nino_d1 = raw_delta(frame, "NINO", anchor, 1)
    nino_d3 = raw_delta(frame, "NINO", anchor, 3)
    nino_d6 = raw_delta(frame, "NINO", anchor, 6)
    home_flow = (
        0.50 * squash(nino_d1, 0.35)
        + 0.30 * squash(nino_d3, 0.65)
        + 0.20 * squash(nino_d6, 0.90)
    )

    tributary_parts = []
    tributary_abs = []
    opposed = 0.0
    aligned = 0.0
    for period in LOWER_PERIODS:
        weight = HOME / float(period)
        nino_part = squash(raw_delta(frame, "NINO", anchor, period), 0.75)
        soi_part = squash(-raw_delta(frame, "SOI", anchor, period), 1.75)
        pdo_part = squash(raw_delta(frame, "PDO", anchor, period), 1.75)
        part = weight * (0.45 * nino_part + 0.35 * soi_part + 0.20 * pdo_part)
        tributary_parts.append(part)
        tributary_abs.append(abs(part))
        if sign(part) == sign(home_flow):
            aligned += abs(part)
        elif sign(part) == -sign(home_flow):
            opposed += abs(part)

    tributary_flow = squash(float(np.sum(tributary_parts)), 2.0)
    tributary_pressure = squash(float(np.sum(tributary_abs)), 5.0)

    slow_parts = []
    for period in UPPER_PERIODS:
        nino_part = squash(raw_delta(frame, "NINO", anchor, period), 1.10)
        soi_part = squash(-raw_delta(frame, "SOI", anchor, period), 2.25)
        pdo_part = squash(raw_delta(frame, "PDO", anchor, period), 2.25)
        slow_parts.append(0.50 * nino_part + 0.30 * soi_part + 0.20 * pdo_part)
    slow_arrival = squash(float(np.mean(slow_parts)) if slow_parts else 0.0, 1.0)
    slow_resistance = squash(float(np.mean([abs(x) for x in slow_parts])) if slow_parts else 0.0, 1.0)

    ara_ridge_distance = min(channel_ara, 2.0 - channel_ara)
    ara_ridge_proximity = 1.0 - max(0.0, min(1.0, ara_ridge_distance))
    enso_ridge_proximity = 1.0 / (1.0 + enso_boundary_distance(nino))
    boundary_pressure = sigmoid(
        1.20 * enso_ridge_proximity
        + 0.80 * ara_ridge_proximity
        + 0.55 * tributary_pressure
        + 0.45 * slow_resistance
        - 1.50
    )

    turbulence = squash(
        opposed
        + abs(tributary_flow - home_flow)
        + 0.25 * abs(soi)
        + 0.15 * abs(pdo),
        4.0,
    )
    friction_gate = max(0.10, 1.0 - 0.55 * max(0.0, turbulence))
    reservoir_gate = 0.75 + 0.25 * slow_resistance
    boundary_gate = 0.70 + 0.30 * boundary_pressure

    raw_route = (
        0.30 * home_flow
        + 0.30 * tributary_flow
        + 0.20 * slow_arrival
        + 0.20 * phi_valley_pull
    )
    raw_flow = raw_route * reservoir_gate * boundary_gate * friction_gate
    unit_delta = math.sqrt(max(float(horizon), 1.0) / HOME) * raw_flow

    return {
        "channel_ara": float(channel_ara),
        "channel_width": float(channel_width),
        "phi_valley_pull": float(phi_valley_pull),
        "home_flow": float(home_flow),
        "tributary_flow": float(tributary_flow),
        "tributary_pressure": float(tributary_pressure),
        "tributary_aligned": float(aligned),
        "tributary_opposed": float(opposed),
        "slow_terrain_arrival": float(slow_arrival),
        "slow_resistance": float(slow_resistance),
        "ara_ridge_proximity": float(ara_ridge_proximity),
        "enso_ridge_proximity": float(enso_ridge_proximity),
        "boundary_pressure": float(boundary_pressure),
        "turbulence": float(turbulence),
        "friction_gate": float(friction_gate),
        "reservoir_gate": float(reservoir_gate),
        "boundary_gate": float(boundary_gate),
        "raw_route": float(raw_route),
        "raw_flow": float(raw_flow),
        "raw_abs_flow": abs(float(raw_flow)),
        "unit_delta": float(unit_delta),
        "raw_nino": float(nino),
        "raw_soi": float(soi),
        "raw_pdo": float(pdo),
        "raw_nino_d1": float(nino_d1),
        "raw_nino_d3": float(nino_d3),
        "raw_nino_d6": float(nino_d6),
    }


def decoder_features(record):
    terms = record["watershed"]
    keys = [
        "channel_ara",
        "channel_width",
        "phi_valley_pull",
        "home_flow",
        "tributary_flow",
        "tributary_pressure",
        "slow_terrain_arrival",
        "slow_resistance",
        "boundary_pressure",
        "turbulence",
        "raw_flow",
        "raw_abs_flow",
        "unit_delta",
        "raw_nino",
        "raw_soi",
        "raw_pdo",
        "raw_nino_d1",
        "raw_nino_d3",
        "raw_nino_d6",
    ]
    out = {key: finite(terms.get(key, 0.0)) for key in keys}
    out["horizon_over_home"] = float(record["horizon"]) / HOME
    out["sqrt_horizon_over_home"] = math.sqrt(max(float(record["horizon"]), 1.0) / HOME)
    out["flow_x_boundary"] = out["raw_flow"] * out["boundary_pressure"]
    out["flow_x_tributary"] = out["raw_flow"] * out["tributary_pressure"]
    out["flow_x_resistance"] = out["raw_flow"] * out["slow_resistance"]
    return out


def fit_predict_delta(train_rows, train_y, row, alpha, clip=3.0):
    model = fit_ridge_model(train_rows, train_y, alpha=alpha)
    pred = float(predict_ridge_model(model, row)[0])
    return max(-clip, min(clip, pred))


def add_predictions(records):
    for record in records:
        unit_delta = finite(record["watershed"]["unit_delta"])
        record["persistence_pred"] = record["current"]
        record["raw_watershed_formula_pred"] = record["current"] + unit_delta

        past = [r for r in records if r["target_anchor"] < record["origin_anchor"] and "watershed" in r]
        if len(past) < MIN_RISK_TRAIN:
            record["raw_watershed_scaled_pred"] = record["raw_watershed_formula_pred"]
            record["raw_watershed_decoder_pred"] = record["raw_watershed_formula_pred"]
            record["scale_ready"] = False
            record["decoder_ready"] = False
            continue

        train_y = [r["actual"] - r["current"] for r in past]
        scale_delta = fit_predict_delta(
            [{"unit_delta": finite(r["watershed"]["unit_delta"])} for r in past],
            train_y,
            {"unit_delta": unit_delta},
            RIDGE_ALPHA_SCALE,
        )
        decoder_delta = fit_predict_delta(
            [decoder_features(r) for r in past],
            train_y,
            decoder_features(record),
            RIDGE_ALPHA_DECODER,
        )
        record["raw_watershed_scaled_pred"] = record["current"] + scale_delta
        record["raw_watershed_decoder_pred"] = record["current"] + decoder_delta
        record["scale_ready"] = True
        record["decoder_ready"] = True


def add_outcome_labels(records, frame):
    nino = frame["NINO"].values.astype(float)
    for i, record in enumerate(records):
        record["boundary_crossing"] = bool(future_boundary_crossing(record))
        record["enso_class_transition"] = bool(class_transition(record))
        record["large_move"] = bool(abs(record["actual"] - record["current"]) >= 0.5)
        record["time_to_transition"] = time_to_transition(nino, record["origin_anchor"], TIME_TO_TRANSITION_WINDOW)
        record["persistence_abs_error"] = abs(record["current"] - record["actual"])
        past = [r for r in records[:i] if r["target_anchor"] < record["origin_anchor"] and "persistence_abs_error" in r]
        if past:
            threshold = float(np.quantile([r["persistence_abs_error"] for r in past], HIGH_ERROR_QUANTILE))
        else:
            threshold = float("inf")
        record["persistence_abs_error_high"] = bool(record["persistence_abs_error"] >= threshold)


def point_records(records, pred_key):
    return [point(r["origin_date"], r["target_date"], r[pred_key], r["actual"], r["current"]) for r in records]


def auc_score(labels, scores):
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    pos = scores[labels == 1]
    neg = scores[labels == 0]
    if len(pos) == 0 or len(neg) == 0:
        return None
    wins = 0.0
    total = 0.0
    for p in pos:
        wins += float(np.sum(p > neg)) + 0.5 * float(np.sum(p == neg))
        total += len(neg)
    return wins / total if total else None


def score_raw(records, score_key, target_key):
    usable = [r for r in records if score_key in r["watershed"] and target_key in r]
    if not usable:
        return {"n": 0}
    scores = np.asarray([finite(r["watershed"][score_key]) for r in usable], dtype=float)
    labels = np.asarray([int(bool(r[target_key])) for r in usable], dtype=int)
    event_rate = float(np.mean(labels))
    auc = auc_score(labels, scores)
    top_cut = float(np.quantile(scores, 0.75))
    bottom_cut = float(np.quantile(scores, 0.25))
    top = labels[scores >= top_cut]
    bottom = labels[scores <= bottom_cut]
    top_rate = float(np.mean(top)) if len(top) else None
    bottom_rate = float(np.mean(bottom)) if len(bottom) else None
    return {
        "n": int(len(usable)),
        "event_rate": event_rate,
        "auc": auc,
        "mean_score": float(np.mean(scores)),
        "top_quartile_event_rate": top_rate,
        "bottom_quartile_event_rate": bottom_rate,
        "top_vs_base_lift": top_rate / event_rate if top_rate is not None and event_rate > EPS else None,
        "top_vs_bottom_lift": top_rate / bottom_rate if top_rate is not None and bottom_rate is not None and bottom_rate > EPS else None,
    }


def aggregate_metric(items, key):
    vals = [item.get(key) for item in items if item.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def aggregate_focus(score_by_h, horizons):
    selected = [score_by_h[str(h)] for h in horizons]
    keys = sorted({key for item in selected for key in item.keys()})
    out = {}
    for key in keys:
        if key == "n":
            out[key] = int(sum(item.get(key, 0) for item in selected))
        else:
            out[key] = aggregate_metric(selected, key)
    return out


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

    print("ARA raw watershed-slice test")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("formula: raw water slice over raw terrain; no bandpass, no z-score, no rolling smoothing")
    print("strict guards: raw samples <= t; no lag ridge; calibration target<t")
    print()

    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    raw_scores = {}

    for h in HORIZONS:
        records = []
        origins = list(range(min_anchor + max_h + 1, n - h + 1, ORIGIN_STRIDE))
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
                    "watershed": raw_watershed_terms(frame, origin, h),
                }
            )

        add_outcome_labels(records, frame)
        add_predictions(records)

        eval_records = [r for r in records if r["is_test"]]
        records_by_h[str(h)] = eval_records
        point_scores["persistence"][str(h)] = extended_score(point_records(eval_records, "persistence_pred"))
        point_scores["raw_watershed_formula"][str(h)] = extended_score(
            point_records(eval_records, "raw_watershed_formula_pred")
        )
        point_scores["raw_watershed_scaled"][str(h)] = extended_score(
            point_records(eval_records, "raw_watershed_scaled_pred")
        )
        point_scores["raw_watershed_decoder"][str(h)] = extended_score(
            point_records(eval_records, "raw_watershed_decoder_pred")
        )
        raw_scores[str(h)] = {
            score_key: {target: score_raw(eval_records, score_key, target) for target in RAW_SCORE_TARGETS}
            for score_key in RAW_SCORE_KEYS
        }

        print(f"h={h:>2} months")
        for key in MODEL_KEYS:
            print(f"  {key:24s} {format_score(point_scores[key][str(h)])}")
        for score_key in RAW_SCORE_KEYS:
            bc = raw_scores[str(h)][score_key]["boundary_crossing"]
            tr = raw_scores[str(h)][score_key]["enso_class_transition"]
            lm = raw_scores[str(h)][score_key]["large_move"]
            print(
                f"  raw {score_key:22s}"
                f" boundary_auc={bc.get('auc') if bc.get('auc') is not None else float('nan'):+.3f}"
                f" transition_auc={tr.get('auc') if tr.get('auc') is not None else float('nan'):+.3f}"
                f" large_move_auc={lm.get('auc') if lm.get('auc') is not None else float('nan'):+.3f}"
            )
        print()

    focus_horizons = [6, 12, 24]
    focus = {
        "point_scores": {key: aggregate_focus(point_scores[key], focus_horizons) for key in point_scores},
        "raw_scores": {},
    }
    for score_key in RAW_SCORE_KEYS:
        focus["raw_scores"][score_key] = {
            target: aggregate_focus(
                {str(h): raw_scores[str(h)][score_key][target] for h in focus_horizons},
                focus_horizons,
            )
            for target in RAW_SCORE_TARGETS
        }

    examples = {
        h: [
            {
                "origin": r["origin_date"],
                "target": r["target_date"],
                "current": rounded(r["current"]),
                "actual": rounded(r["actual"]),
                "raw_watershed_formula_pred": rounded(r["raw_watershed_formula_pred"]),
                "raw_watershed_scaled_pred": rounded(r["raw_watershed_scaled_pred"]),
                "raw_watershed_decoder_pred": rounded(r["raw_watershed_decoder_pred"]),
                "boundary_crossing": r["boundary_crossing"],
                "enso_class_transition": r["enso_class_transition"],
                "raw_flow": rounded(r["watershed"]["raw_flow"]),
                "tributary_pressure": rounded(r["watershed"]["tributary_pressure"]),
                "boundary_pressure": rounded(r["watershed"]["boundary_pressure"]),
                "slow_terrain_arrival": rounded(r["watershed"]["slow_terrain_arrival"]),
                "channel_ara": rounded(r["watershed"]["channel_ara"]),
            }
            for r in records[:10]
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal raw watershed-slice ARA test",
        "leakage_guard": [
            "Every raw terrain feature at origin t uses only samples <= t.",
            "Raw watershed flow uses a fixed formula, not future fitting.",
            "Optional scale/decoder checks at origin t train only on previous records whose targets are already known.",
            "No bandpass, no z-score, no rolling smoothing, and no lag-ridge/native lag feature block.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly from raw watershed geometry",
        "formula": {
            "channel_ara": "1 + tanh(raw_NINO / 1.5), bounded in 0..2",
            "phi_valley_pull": "(phi - channel_ara) / phi, squashed",
            "tributaries": "raw finite differences at lower offsets for NINO, anti-phase SOI, and PDO",
            "slow_terrain_arrival": "raw finite differences at upper offsets for NINO, anti-phase SOI, and PDO",
            "raw_flow": "(home_flow + tributary_flow + slow_arrival + phi_valley_pull) gated by reservoir/boundary/friction",
            "unit_delta": "sqrt(h/home_period) * raw_flow",
        },
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
        "raw_scores": clean_for_json(raw_scores),
        "focus_6_12_24": clean_for_json(focus),
        "example_records": clean_for_json(examples),
        "elapsed_seconds": rounded(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_RAW_WATERSHED_SLICE = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
    print("Focus 6/12/24 raw formula AUCs:")
    for score_key in RAW_SCORE_KEYS:
        row = focus["raw_scores"][score_key]
        print(
            f"  {score_key:22s}"
            f" boundary={row['boundary_crossing'].get('auc'):+.3f}"
            f" transition={row['enso_class_transition'].get('auc'):+.3f}"
            f" large_move={row['large_move'].get('auc'):+.3f}"
            f" higherr={row['persistence_abs_error_high'].get('auc'):+.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
