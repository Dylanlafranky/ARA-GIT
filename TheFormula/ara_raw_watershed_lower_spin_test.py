"""
ara_raw_watershed_lower_spin_test.py

Strict-causal raw-data test of the corrected watershed interpretation:

    lower fast systems = tributary torque that spins/turns the current sphere
    current sphere = the terrain frame the water slice experiences
    upper slow systems = sea/backpressure/envelope, not the main spinner

This fixes the earlier raw watershed wording where upper-period finite
differences were treated too much like "slow terrain arrival."  In this version
the topology arrival term is driven mainly by lower-rung spin pressure.

No bandpass, no z-score, no rolling smoothing, no lag-ridge/native lag block.
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
    time_to_transition,
)
from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import START_YEAR, clean_for_json, load_enso_frame
from ara_lag_phase_hybrid_predictor import extended_score, finite, format_score, point
from ara_raw_watershed_slice_test import (
    RAW_SCORE_TARGETS,
    aggregate_focus,
    class_transition,
    future_boundary_crossing,
    raw_delta,
    raw_value,
    rounded,
    score_raw,
    sign,
    sigmoid,
    squash,
)
from ara_shape_kernel_test import PHI


OUT_JSON = HERE / "ara_raw_watershed_lower_spin_result.json"
OUT_JS = HERE / "ara_raw_watershed_lower_spin_result.js"

RIDGE_ALPHA_SCALE = 4.0
RIDGE_ALPHA_DECODER = 12.0
HIGH_ERROR_QUANTILE = 0.75
EPS = 1e-9

MODEL_KEYS = [
    "persistence",
    "lower_spin_formula",
    "lower_spin_scaled",
    "lower_spin_decoder",
]

RAW_SCORE_KEYS = [
    "lower_spin_torque",
    "lower_spin_pressure",
    "topology_arrival",
    "sea_backpressure",
    "boundary_gate",
    "turbulence",
    "raw_flow",
]


def fit_predict_delta(train_rows, train_y, row, alpha, clip=3.0):
    model = fit_ridge_model(train_rows, train_y, alpha=alpha)
    pred = float(predict_ridge_model(model, row)[0])
    return max(-clip, min(clip, pred))


def corrected_lower_spin_terms(frame, anchor, horizon):
    nino = raw_value(frame, "NINO", anchor)
    soi = raw_value(frame, "SOI", anchor)
    pdo = raw_value(frame, "PDO", anchor)

    channel_ara = 1.0 + squash(nino, 1.5)
    phi_valley_pull = squash((PHI - channel_ara) / PHI, 0.35)
    ridge_proximity = max(0.0, min(1.0, 1.0 - min(channel_ara, 2.0 - channel_ara)))
    enso_boundary = 1.0 / (1.0 + (abs(abs(nino) - 0.5)))

    home_inertia = (
        0.55 * squash(raw_delta(frame, "NINO", anchor, 1), 0.35)
        + 0.30 * squash(raw_delta(frame, "NINO", anchor, 3), 0.65)
        + 0.15 * squash(raw_delta(frame, "NINO", anchor, 6), 0.90)
    )

    lower_parts = []
    lower_abs = []
    aligned = 0.0
    opposed = 0.0
    for period in LOWER_PERIODS:
        frequency_ratio = HOME / float(period)
        # Lower systems should be small but frequent: frequency_ratio raises their
        # event rate, while the final squash keeps amplitude bounded.
        nino_spin = squash(raw_delta(frame, "NINO", anchor, period), 0.80)
        soi_spin = squash(-raw_delta(frame, "SOI", anchor, period), 1.80)
        pdo_spin = squash(raw_delta(frame, "PDO", anchor, period), 2.10)
        spin = frequency_ratio * (0.40 * nino_spin + 0.40 * soi_spin + 0.20 * pdo_spin)
        lower_parts.append(spin)
        lower_abs.append(abs(spin))
        if sign(spin) == sign(home_inertia):
            aligned += abs(spin)
        elif sign(spin) == -sign(home_inertia):
            opposed += abs(spin)

    lower_spin_torque = squash(float(np.sum(lower_parts)), 2.2)
    lower_spin_pressure = squash(float(np.sum(lower_abs)), 5.0)
    lower_alignment = (aligned - opposed) / (aligned + opposed + EPS)

    # Upper periods are deliberately weak here: sea/backpressure and outlet
    # condition, not the primary turning engine.
    upper_parts = []
    upper_abs = []
    for period in UPPER_PERIODS:
        slow_weight = HOME / float(period)
        nino_sea = squash(raw_delta(frame, "NINO", anchor, period), 1.20)
        soi_sea = squash(-raw_delta(frame, "SOI", anchor, period), 2.40)
        pdo_sea = squash(raw_delta(frame, "PDO", anchor, period), 2.60)
        sea = slow_weight * (0.45 * nino_sea + 0.25 * soi_sea + 0.30 * pdo_sea)
        upper_parts.append(sea)
        upper_abs.append(abs(sea))

    sea_backpressure = squash(float(np.sum(upper_parts)), 2.0)
    sea_reservoir = squash(float(np.sum(upper_abs)), 2.5)

    topology_arrival = squash(
        0.75 * lower_spin_torque
        + 0.20 * lower_alignment
        + 0.05 * home_inertia,
        1.0,
    )
    boundary_gate = sigmoid(
        1.15 * enso_boundary
        + 0.80 * ridge_proximity
        + 0.65 * lower_spin_pressure
        + 0.20 * sea_reservoir
        - 1.45
    )
    turbulence = squash(
        opposed
        + abs(lower_spin_torque - home_inertia)
        + 0.20 * abs(soi)
        + 0.12 * abs(pdo)
        + 0.15 * abs(sea_backpressure),
        4.0,
    )
    friction_gate = max(0.10, 1.0 - 0.50 * max(0.0, turbulence))
    sea_gate = 1.0 + 0.08 * sea_backpressure + 0.06 * sea_reservoir

    raw_flow = (
        0.60 * topology_arrival
        + 0.18 * phi_valley_pull
        + 0.14 * home_inertia
        + 0.08 * sea_backpressure
    )
    raw_flow = raw_flow * sea_gate * (0.72 + 0.28 * boundary_gate) * friction_gate
    unit_delta = math.sqrt(max(float(horizon), 1.0) / HOME) * raw_flow

    return {
        "channel_ara": float(channel_ara),
        "phi_valley_pull": float(phi_valley_pull),
        "ridge_proximity": float(ridge_proximity),
        "enso_boundary": float(enso_boundary),
        "home_inertia": float(home_inertia),
        "lower_spin_torque": float(lower_spin_torque),
        "lower_spin_pressure": float(lower_spin_pressure),
        "lower_alignment": float(lower_alignment),
        "topology_arrival": float(topology_arrival),
        "sea_backpressure": float(sea_backpressure),
        "sea_reservoir": float(sea_reservoir),
        "boundary_gate": float(boundary_gate),
        "turbulence": float(turbulence),
        "friction_gate": float(friction_gate),
        "sea_gate": float(sea_gate),
        "raw_flow": float(raw_flow),
        "raw_abs_flow": abs(float(raw_flow)),
        "unit_delta": float(unit_delta),
        "raw_nino": float(nino),
        "raw_soi": float(soi),
        "raw_pdo": float(pdo),
    }


def decoder_features(record):
    terms = record["watershed"]
    keys = [
        "channel_ara",
        "phi_valley_pull",
        "ridge_proximity",
        "enso_boundary",
        "home_inertia",
        "lower_spin_torque",
        "lower_spin_pressure",
        "lower_alignment",
        "topology_arrival",
        "sea_backpressure",
        "sea_reservoir",
        "boundary_gate",
        "turbulence",
        "friction_gate",
        "raw_flow",
        "raw_abs_flow",
        "unit_delta",
        "raw_nino",
        "raw_soi",
        "raw_pdo",
    ]
    out = {key: finite(terms.get(key, 0.0)) for key in keys}
    out["horizon_over_home"] = float(record["horizon"]) / HOME
    out["sqrt_horizon_over_home"] = math.sqrt(max(float(record["horizon"]), 1.0) / HOME)
    out["spin_x_boundary"] = out["lower_spin_torque"] * out["boundary_gate"]
    out["spin_x_pressure"] = out["lower_spin_torque"] * out["lower_spin_pressure"]
    out["spin_x_sea"] = out["lower_spin_torque"] * out["sea_backpressure"]
    out["arrival_x_friction"] = out["topology_arrival"] * out["friction_gate"]
    return out


def add_predictions(records):
    for record in records:
        unit_delta = finite(record["watershed"]["unit_delta"])
        record["persistence_pred"] = record["current"]
        record["lower_spin_formula_pred"] = record["current"] + unit_delta

        past = [r for r in records if r["target_anchor"] < record["origin_anchor"] and "watershed" in r]
        if len(past) < MIN_RISK_TRAIN:
            record["lower_spin_scaled_pred"] = record["lower_spin_formula_pred"]
            record["lower_spin_decoder_pred"] = record["lower_spin_formula_pred"]
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
        record["lower_spin_scaled_pred"] = record["current"] + scale_delta
        record["lower_spin_decoder_pred"] = record["current"] + decoder_delta
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

    print("ARA raw watershed lower-spin test")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("formula: lower tributary torque spins current terrain; upper sea is weak backpressure")
    print("strict guards: raw samples <= t; no smoothing; no lag ridge; calibration target<t")
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
                    "watershed": corrected_lower_spin_terms(frame, origin, h),
                }
            )

        add_outcome_labels(records, frame)
        add_predictions(records)

        eval_records = [r for r in records if r["is_test"]]
        records_by_h[str(h)] = eval_records
        point_scores["persistence"][str(h)] = extended_score(point_records(eval_records, "persistence_pred"))
        point_scores["lower_spin_formula"][str(h)] = extended_score(point_records(eval_records, "lower_spin_formula_pred"))
        point_scores["lower_spin_scaled"][str(h)] = extended_score(point_records(eval_records, "lower_spin_scaled_pred"))
        point_scores["lower_spin_decoder"][str(h)] = extended_score(point_records(eval_records, "lower_spin_decoder_pred"))
        raw_scores[str(h)] = {
            score_key: {target: score_raw(eval_records, score_key, target) for target in RAW_SCORE_TARGETS}
            for score_key in RAW_SCORE_KEYS
        }

        print(f"h={h:>2} months")
        for key in MODEL_KEYS:
            print(f"  {key:22s} {format_score(point_scores[key][str(h)])}")
        for score_key in RAW_SCORE_KEYS:
            bc = raw_scores[str(h)][score_key]["boundary_crossing"]
            tr = raw_scores[str(h)][score_key]["enso_class_transition"]
            lm = raw_scores[str(h)][score_key]["large_move"]
            print(
                f"  raw {score_key:20s}"
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
                "lower_spin_formula_pred": rounded(r["lower_spin_formula_pred"]),
                "lower_spin_scaled_pred": rounded(r["lower_spin_scaled_pred"]),
                "lower_spin_decoder_pred": rounded(r["lower_spin_decoder_pred"]),
                "boundary_crossing": r["boundary_crossing"],
                "enso_class_transition": r["enso_class_transition"],
                "lower_spin_torque": rounded(r["watershed"]["lower_spin_torque"]),
                "lower_spin_pressure": rounded(r["watershed"]["lower_spin_pressure"]),
                "topology_arrival": rounded(r["watershed"]["topology_arrival"]),
                "sea_backpressure": rounded(r["watershed"]["sea_backpressure"]),
                "raw_flow": rounded(r["watershed"]["raw_flow"]),
            }
            for r in records[:10]
        ]
        for h, records in records_by_h.items()
    }
    observed_series = [
        {
            "date": dates[i].strftime("%Y-%m-%d"),
            "nino": rounded(nino_raw[i]),
        }
        for i in range(n)
    ]
    viz_records = {
        h: [
            {
                "origin": r["origin_date"],
                "target": r["target_date"],
                "current": rounded(r["current"]),
                "actual": rounded(r["actual"]),
                "persistence": rounded(r["persistence_pred"]),
                "lower_spin_formula": rounded(r["lower_spin_formula_pred"]),
                "lower_spin_scaled": rounded(r["lower_spin_scaled_pred"]),
                "lower_spin_decoder": rounded(r["lower_spin_decoder_pred"]),
                "boundary_crossing": bool(r["boundary_crossing"]),
                "enso_class_transition": bool(r["enso_class_transition"]),
                "lower_spin_torque": rounded(r["watershed"]["lower_spin_torque"]),
                "lower_spin_pressure": rounded(r["watershed"]["lower_spin_pressure"]),
                "topology_arrival": rounded(r["watershed"]["topology_arrival"]),
                "sea_backpressure": rounded(r["watershed"]["sea_backpressure"]),
                "boundary_gate": rounded(r["watershed"]["boundary_gate"]),
                "turbulence": rounded(r["watershed"]["turbulence"]),
                "raw_flow": rounded(r["watershed"]["raw_flow"]),
            }
            for r in records
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal raw watershed lower-spin ARA test",
        "leakage_guard": [
            "Every raw feature at origin t uses only samples <= t.",
            "No bandpass, z-score, rolling smoothing, or lag-ridge/native lag feature block.",
            "Raw lower-spin flow uses a fixed formula, not future fitting.",
            "Optional scale/decoder checks at origin t train only on previous records whose targets are already known.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly from raw lower-rung spin torque",
        "formula": {
            "lower_spin_torque": "frequency-weighted lower-offset NINO, anti-phase SOI, and PDO finite differences",
            "topology_arrival": "mostly lower_spin_torque, with small home-inertia alignment",
            "sea_backpressure": "weak upper-offset sea/backpressure term, not main driver",
            "raw_flow": "0.60*topology_arrival + 0.18*phi_valley_pull + 0.14*home_inertia + 0.08*sea_backpressure, gated by boundary/friction/sea",
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
        "observed_series": clean_for_json(observed_series),
        "viz_records": clean_for_json(viz_records),
        "elapsed_seconds": rounded(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_RAW_WATERSHED_LOWER_SPIN = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24 point scores:")
    for key, score in focus["point_scores"].items():
        print(
            f"  {key:22s}"
            f" MAE={score.get('mae'):.3f}"
            f" corr={score.get('corr'):+.3f}"
            f" turn={score.get('turn_accuracy'):.3f}"
            f" transition_mae={score.get('transition_mae'):.3f}"
        )
    print("Focus 6/12/24 raw formula AUCs:")
    for score_key in RAW_SCORE_KEYS:
        row = focus["raw_scores"][score_key]
        print(
            f"  {score_key:20s}"
            f" boundary={row['boundary_crossing'].get('auc'):+.3f}"
            f" transition={row['enso_class_transition'].get('auc'):+.3f}"
            f" large_move={row['large_move'].get('auc'):+.3f}"
            f" higherr={row['persistence_abs_error_high'].get('auc'):+.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
