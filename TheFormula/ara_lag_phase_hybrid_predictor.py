"""
ara_lag_phase_hybrid_predictor.py

Strict-causal hybrid test:

    lag ridge = native-unit amplitude / inertia prior
    ARA phase flow = timing / turn / shape prior
    ARA coupling-energy = amplitude gate

The question is not whether ARA phase-flow beats lag ridge alone.  The question
is whether phase/regime geometry can improve lag ridge around turns and regime
transitions.

Leakage guard for origin t and horizon h:

  - Geometry snapshots and velocity/gate features use only anchors <= t.
  - Base lag/phase transition models use only completed pairs s+h<t.
  - Final hybrid weights are trained on an inner past calibration slice.
  - Calibration predictions for a calibration origin c use only pairs s+h<c.
  - Oracle phase hybrid is diagnostic only because it uses actual S(t+h).
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

from ara_geometry_analog_flow_predictor import (
    analog_direct_raw_prediction,
    compact_state_features,
    raw_lag_state_features,
)
from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import (
    BASE,
    HOME_PERIOD,
    HORIZONS,
    MIN_TRAIN,
    RUNG_KS,
    START_YEAR,
    build_snapshot,
    clean_for_json,
    fit_predict_ridge,
    lag_feature_dict,
    load_enso_frame,
    score_points,
    zscore_columns,
)
from ara_phase_flow_predictor import (
    MIN_REGIME_EXAMPLES,
    PHASE_KEYS,
    VELOCITY_LAGS,
    decode_phase,
    matching_regime_anchors,
    phase_clean_input,
    phase_velocity_input,
    predict_phase_ridge,
    train_decoder as train_phase_decoder,
)


OUT_JSON = HERE / "ara_lag_phase_hybrid_predictor_result.json"
OUT_JS = HERE / "ara_lag_phase_hybrid_predictor_result.js"

ORIGIN_STRIDE = 3
MIN_FLOW_TRAIN = max(MIN_TRAIN, 120)
MIN_CALIBRATION = 45
CALIBRATION_FRACTION = 0.32
RIDGE_ALPHA_HYBRID = 5.0
RIDGE_ALPHA_DIRECT = 10.0

MODEL_KEYS = [
    "persistence",
    "lag_ridge",
    "phase_clean_only",
    "phase_regime_velocity_only",
    "lag_plus_clean_phase",
    "lag_plus_regime_velocity_phase",
    "lag_plus_phase_coupling_gate",
    "raw_analog_baseline",
    "lag_plus_oracle_phase_diagnostic",
]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def round_float(value, digits=6):
    return round(finite(value), digits)


def cache_keys(cache, anchors):
    keys = set()
    for anchor in anchors:
        keys.update(cache[anchor].keys())
    return sorted(keys)


def delta_feature(cache, anchor, key, lag):
    here = finite(cache[anchor].get(key, 0.0))
    prior = anchor - int(lag)
    if prior not in cache:
        return 0.0
    return here - finite(cache[prior].get(key, 0.0))


def enso_class(value):
    value = finite(value)
    if value >= 0.5:
        return "el_nino"
    if value <= -0.5:
        return "la_nina"
    return "neutral"


def gate_features(compact_cache, origin):
    keys = [
        "nino_amplitude_energy_log",
        "soi_amplitude_energy_log",
        "pdo_amplitude_energy_log",
        "nino_soi_coupling_energy_log",
        "nino_pdo_coupling_energy_log",
        "nino_soi_coupling_pressure",
        "nino_pdo_coupling_pressure",
        "enso_feeder_pressure",
        "enso_counterbalance_gate",
        "enso_partner_gap",
        "nino_soi_partner_antiphase_fit",
        "nino_pdo_partner_antiphase_fit",
        "nino_boundary_distance_phi",
        "nino_boundary_distance_balance",
        "nino_boundary_distance_time",
        "nino_orientation_release_balance",
        "nino_rung_position",
        "nino_weighted_k",
    ]
    out = {}
    for key in keys:
        out[f"gate_{key}"] = finite(compact_cache[origin].get(key, 0.0))
        out[f"gate_d3_{key}"] = delta_feature(compact_cache, origin, key, 3)
        out[f"gate_d12_{key}"] = delta_feature(compact_cache, origin, key, 12)
    return out


def ridge_from_rows(rows, y, alpha=RIDGE_ALPHA_HYBRID):
    return fit_ridge_model(rows, y, alpha=alpha)


def predict_from_row(model, row):
    return float(predict_ridge_model(model, row)[0])


def point(origin_date, target_date, pred, actual, persistence, extras=None):
    out = {
        "origin": origin_date,
        "date": target_date,
        "pred": float(pred),
        "actual": float(actual),
        "persistence": float(persistence),
    }
    if extras:
        out.update({key: clean_for_json(value) for key, value in extras.items()})
    return out


def extended_score(points):
    base = score_points(points)
    if len(points) < 5:
        return base
    pred = np.asarray([p["pred"] for p in points], dtype=float)
    actual = np.asarray([p["actual"] for p in points], dtype=float)
    current = np.asarray([p["persistence"] for p in points], dtype=float)
    pred_delta = pred - current
    actual_delta = actual - current
    base["turn_accuracy"] = float(np.mean(np.sign(pred_delta) == np.sign(actual_delta)))

    large_mask = np.abs(actual_delta) >= 0.5
    base["large_event_n"] = int(np.sum(large_mask))
    base["large_event_direction_accuracy"] = (
        float(np.mean(np.sign(pred_delta[large_mask]) == np.sign(actual_delta[large_mask]))) if np.any(large_mask) else None
    )

    pred_class = np.asarray([enso_class(v) for v in pred], dtype=object)
    actual_class = np.asarray([enso_class(v) for v in actual], dtype=object)
    current_class = np.asarray([enso_class(v) for v in current], dtype=object)
    base["enso_class_accuracy"] = float(np.mean(pred_class == actual_class))

    pred_cross = pred_class != current_class
    actual_cross = actual_class != current_class
    base["boundary_crossing_accuracy"] = float(np.mean(pred_cross == actual_cross))
    base["boundary_crossing_n"] = int(np.sum(actual_cross))

    transition_mask = actual_cross
    base["transition_n"] = int(np.sum(transition_mask))
    base["transition_mae"] = (
        float(np.mean(np.abs(pred[transition_mask] - actual[transition_mask]))) if np.any(transition_mask) else None
    )
    base["transition_corr"] = (
        float(np.corrcoef(pred[transition_mask], actual[transition_mask])[0, 1])
        if np.sum(transition_mask) >= 5 and pred[transition_mask].std() > 1e-9 and actual[transition_mask].std() > 1e-9
        else None
    )
    return base


def format_score(score):
    if "mae" not in score:
        return "n/a"
    transition = score.get("transition_mae")
    transition_txt = f" trans_mae={transition:.4f}" if transition is not None else ""
    return (
        f"MAE={score['mae']:.4f} vs pers={score['persistence_mae']:.4f} "
        f"lift={score['mae_lift_vs_persistence']:+.4f} corr={score['corr']:+.3f} "
        f"turn={score['turn_accuracy']:.3f} class={score['enso_class_accuracy']:.3f}"
        f"{transition_txt}"
    )


def predict_components_for_origin(
    origin,
    horizon,
    train_transition,
    decoder_anchors,
    compact_cache,
    phase_cache,
    clean_inputs,
    velocity_inputs,
    series,
    nino_raw,
):
    if len(train_transition) < MIN_FLOW_TRAIN or len(decoder_anchors) < MIN_FLOW_TRAIN:
        return None

    persistence = float(nino_raw[origin - 1])
    train_raw_delta = [float(nino_raw[s + horizon - 1] - nino_raw[s - 1]) for s in train_transition]
    lag_delta, _, _ = fit_predict_ridge(
        [lag_feature_dict(series["NINO"]["z"], s) for s in train_transition],
        train_raw_delta,
        lag_feature_dict(series["NINO"]["z"], origin),
        alpha=RIDGE_ALPHA_DIRECT,
    )
    lag_pred = persistence + lag_delta

    decoder = train_phase_decoder(phase_cache, decoder_anchors, nino_raw)
    clean_phase = predict_phase_ridge(clean_inputs, phase_cache, train_transition, origin, horizon, clean_inputs[origin])
    clean_phase_pred = decode_phase(decoder, clean_phase)

    pdo_threshold = float(
        np.median([finite(compact_cache[s].get("nino_pdo_coupling_energy_log", 0.0)) for s in train_transition])
    )
    matched, regime_info = matching_regime_anchors(compact_cache, series, train_transition, origin, pdo_threshold)
    regime_velocity_phase = predict_phase_ridge(
        velocity_inputs,
        phase_cache,
        matched,
        origin,
        horizon,
        velocity_inputs[origin],
    )
    regime_velocity_pred = decode_phase(decoder, regime_velocity_phase)

    oracle_phase_pred = None
    target_anchor = origin + horizon
    if target_anchor in phase_cache:
        oracle_phase_pred = decode_phase(decoder, phase_cache[target_anchor])

    return {
        "persistence": persistence,
        "lag_pred": finite(lag_pred),
        "clean_phase_pred": finite(clean_phase_pred),
        "regime_velocity_phase_pred": finite(regime_velocity_pred),
        "oracle_phase_pred": finite(oracle_phase_pred, lag_pred),
        "regime_info": regime_info,
    }


def hybrid_feature_row(components, compact_cache, origin, mode):
    row = {
        "bias": 1.0,
        "current": components["persistence"],
        "lag_pred": components["lag_pred"],
        "clean_phase_pred": components["clean_phase_pred"],
        "regime_velocity_phase_pred": components["regime_velocity_phase_pred"],
        "clean_minus_lag": components["clean_phase_pred"] - components["lag_pred"],
        "regime_velocity_minus_lag": components["regime_velocity_phase_pred"] - components["lag_pred"],
        "clean_minus_current": components["clean_phase_pred"] - components["persistence"],
        "regime_velocity_minus_current": components["regime_velocity_phase_pred"] - components["persistence"],
    }
    if mode == "clean":
        return {key: row[key] for key in ["bias", "current", "lag_pred", "clean_phase_pred", "clean_minus_lag"]}
    if mode == "regime_velocity":
        return {
            key: row[key]
            for key in ["bias", "current", "lag_pred", "regime_velocity_phase_pred", "regime_velocity_minus_lag"]
        }
    if mode == "gate":
        row.update(gate_features(compact_cache, origin))
        return row
    if mode == "oracle":
        row["oracle_phase_pred"] = components["oracle_phase_pred"]
        row["oracle_minus_lag"] = components["oracle_phase_pred"] - components["lag_pred"]
        row.update(gate_features(compact_cache, origin))
        return row
    raise ValueError(f"unknown mode {mode}")


def build_calibration_rows(
    calib_anchors,
    horizon,
    compact_cache,
    phase_cache,
    clean_inputs,
    velocity_inputs,
    series,
    nino_raw,
    mode,
):
    rows = []
    y = []
    for c in calib_anchors:
        sub_train = [s for s in compact_cache if s + horizon < c]
        sub_decoder = [a for a in compact_cache if a < c]
        components = predict_components_for_origin(
            c,
            horizon,
            sub_train,
            sub_decoder,
            compact_cache,
            phase_cache,
            clean_inputs,
            velocity_inputs,
            series,
            nino_raw,
        )
        if components is None:
            continue
        rows.append(hybrid_feature_row(components, compact_cache, c, mode))
        y.append(float(nino_raw[c + horizon - 1]))
    return rows, y


def build_calibration_components(
    calib_anchors,
    horizon,
    compact_cache,
    phase_cache,
    clean_inputs,
    velocity_inputs,
    series,
    nino_raw,
):
    records = []
    for c in calib_anchors:
        sub_train = [s for s in compact_cache if s + horizon < c]
        sub_decoder = [a for a in compact_cache if a < c]
        components = predict_components_for_origin(
            c,
            horizon,
            sub_train,
            sub_decoder,
            compact_cache,
            phase_cache,
            clean_inputs,
            velocity_inputs,
            series,
            nino_raw,
        )
        if components is None:
            continue
        records.append(
            {
                "origin": c,
                "components": components,
                "actual": float(nino_raw[c + horizon - 1]),
            }
        )
    return records


def calibration_rows_from_components(records, compact_cache, mode):
    rows = [hybrid_feature_row(record["components"], compact_cache, record["origin"], mode) for record in records]
    y = [record["actual"] for record in records]
    return rows, y


def best_forecast(scores, horizon):
    rows = []
    for model in MODEL_KEYS:
        if "oracle" in model:
            continue
        rows.append((scores[model][horizon].get("mae", float("inf")), model))
    rows.sort()
    return rows[0][1]


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = zscore_columns(frame)
    nino_raw = series["NINO"]["raw"]
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + MIN_FLOW_TRAIN + max_h + 1)
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA lag/phase hybrid predictor")
    print("=" * 108)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}")
    print(f"test origins start: {dates[test_start - 1].date()}  stride={ORIGIN_STRIDE}")
    print("hybrid: lag amplitude prior + ARA phase timing + coupling-energy gate")
    print("strict guards: base s+h<t; calibration c uses s+h<c; decoder a<t")
    print()

    compact_cache = {}
    phase_cache = {}
    raw_cache = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        compact = compact_state_features(build_snapshot(series, anchor))
        compact_cache[anchor] = compact
        phase_cache[anchor] = {key: finite(compact.get(key, 0.0)) for key in PHASE_KEYS}
        raw_cache[anchor] = raw_lag_state_features(series, anchor)
        if i % 100 == 0:
            print(f"  cached states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    clean_inputs = {anchor: phase_clean_input(phase_cache, anchor) for anchor in all_anchors}
    velocity_inputs = {anchor: phase_velocity_input(compact_cache, phase_cache, anchor) for anchor in all_anchors}
    raw_keys = cache_keys(raw_cache, all_anchors)

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS}
    calibration_counts = {h: [] for h in HORIZONS}

    for h in HORIZONS:
        origins = list(range(test_start, n - h + 1, ORIGIN_STRIDE))
        for origin in origins:
            target_anchor = origin + h
            if target_anchor > n:
                continue
            train_transition = [s for s in all_anchors if s + h < origin]
            decoder_anchors = [a for a in all_anchors if a < origin]
            if len(train_transition) < MIN_FLOW_TRAIN or len(decoder_anchors) < MIN_FLOW_TRAIN:
                continue

            split_at = max(MIN_FLOW_TRAIN, int(len(train_transition) * (1.0 - CALIBRATION_FRACTION)))
            calib = train_transition[split_at:]
            if len(calib) < MIN_CALIBRATION:
                calib = train_transition[-MIN_CALIBRATION:]
            calibration_counts[h].append(len(calib))

            components = predict_components_for_origin(
                origin,
                h,
                train_transition,
                decoder_anchors,
                compact_cache,
                phase_cache,
                clean_inputs,
                velocity_inputs,
                series,
                nino_raw,
            )
            if components is None:
                continue

            actual = float(nino_raw[target_anchor - 1])
            persistence = components["persistence"]
            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")

            all_points["persistence"][h].append(point(origin_date, target_date, persistence, actual, persistence))
            all_points["lag_ridge"][h].append(point(origin_date, target_date, components["lag_pred"], actual, persistence))
            all_points["phase_clean_only"][h].append(point(origin_date, target_date, components["clean_phase_pred"], actual, persistence))
            all_points["phase_regime_velocity_only"][h].append(
                point(
                    origin_date,
                    target_date,
                    components["regime_velocity_phase_pred"],
                    actual,
                    persistence,
                    components["regime_info"],
                )
            )

            raw_pred, raw_dist = analog_direct_raw_prediction(raw_cache, train_transition, origin, h, raw_keys, nino_raw)
            all_points["raw_analog_baseline"][h].append(point(origin_date, target_date, raw_pred, actual, persistence, raw_dist))

            calibration_records = build_calibration_components(
                calib,
                h,
                compact_cache,
                phase_cache,
                clean_inputs,
                velocity_inputs,
                series,
                nino_raw,
            )
            for model_key, mode in [
                ("lag_plus_clean_phase", "clean"),
                ("lag_plus_regime_velocity_phase", "regime_velocity"),
                ("lag_plus_phase_coupling_gate", "gate"),
                ("lag_plus_oracle_phase_diagnostic", "oracle"),
            ]:
                rows, y = calibration_rows_from_components(calibration_records, compact_cache, mode)
                if len(rows) < 12:
                    pred = components["lag_pred"]
                else:
                    model = ridge_from_rows(rows, y, alpha=RIDGE_ALPHA_HYBRID)
                    pred = predict_from_row(model, hybrid_feature_row(components, compact_cache, origin, mode))
                all_points[model_key][h].append(point(origin_date, target_date, pred, actual, persistence))

        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:36s} {format_score(extended_score(all_points[model][h]))}")
        print()

    scores = {model: {h: extended_score(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS}
    winners = {str(h): best_forecast(scores, h) for h in HORIZONS}
    calibration_summary = {
        str(h): {
            "mean_calibration_origins": float(np.mean(calibration_counts[h])) if calibration_counts[h] else None,
            "min_calibration_origins": int(min(calibration_counts[h])) if calibration_counts[h] else None,
            "max_calibration_origins": int(max(calibration_counts[h])) if calibration_counts[h] else None,
        }
        for h in HORIZONS
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal lag/phase hybrid predictor",
        "leakage_guard": [
            "Geometry snapshots and velocity/gate features use only anchors <= t.",
            "Base lag/phase transition models use only completed pairs s+h<t.",
            "Final hybrid weights are trained on an inner past calibration slice.",
            "Calibration predictions for calibration origin c use only pairs s+h<c.",
            "Oracle phase hybrid is diagnostic only because it uses actual S(t+h).",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "rungs_k": RUNG_KS,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "phase_keys": PHASE_KEYS,
        "velocity_lags_months": VELOCITY_LAGS,
        "min_regime_examples": MIN_REGIME_EXAMPLES,
        "calibration_fraction": CALIBRATION_FRACTION,
        "min_calibration": MIN_CALIBRATION,
        "calibration_summary": calibration_summary,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
        },
        "models": {
            "lag_ridge": "Causal NINO lag/slope ridge baseline.",
            "phase_clean_only": "Clean NINO/SOI phase-flow decoded directly.",
            "phase_regime_velocity_only": "Regime+velocity phase-flow decoded directly.",
            "lag_plus_clean_phase": "Inner-calibrated hybrid of lag ridge and clean phase-flow prediction.",
            "lag_plus_regime_velocity_phase": "Inner-calibrated hybrid of lag ridge and regime+velocity phase-flow prediction.",
            "lag_plus_phase_coupling_gate": "Hybrid of lag, phase-flow predictions, and current ARA coupling/energy gates.",
            "raw_analog_baseline": "Raw NINO/SOI/PDO lag analog baseline.",
            "lag_plus_oracle_phase_diagnostic": "Diagnostic upper bound hybrid using actual future phase decoder.",
        },
        "scores": scores,
        "winners": winners,
        "points": {
            str(h): {model: all_points[model][h][:6] for model in MODEL_KEYS if all_points[model][h]}
            for h in HORIZONS
        },
        "elapsed_seconds": round_float(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LAG_PHASE_HYBRID_PREDICTOR = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Winners:")
    for h in HORIZONS:
        print(f"  h={h:>2}: {winners[str(h)]}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
