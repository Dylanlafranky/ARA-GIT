"""
ara_phase_flow_predictor.py

Strict-causal test of three focused phase-flow operators:

1. Clean phase-only flow:
   current NINO/SOI phase -> future NINO/SOI phase -> phase decoder.

2. Regime-gated phase flow:
   classify current regime, then train the phase transition only on matching
   historical regimes before decoding.

3. Velocity-aware phase flow:
   phase position plus geometry velocity/acceleration -> future phase -> decoder.

All three use the same phase-only decoder, so differences come from the flow
operator rather than the decoder.

Leakage guard for origin t and horizon h:

  - S(t), velocity, acceleration, raw sign, and trend inputs use only anchors <= t.
  - Transition training uses only completed pairs s+h<t.
  - Regime thresholds are computed only from the current transition-training set.
  - Decoder training uses only observed geometry anchors a<t.
  - Oracle phase decoder uses actual S(t+h) and is diagnostic only.
"""

from __future__ import annotations

import json
import math
import sys
import time
from collections import Counter
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


OUT_JSON = HERE / "ara_phase_flow_predictor_result.json"
OUT_JS = HERE / "ara_phase_flow_predictor_result.js"

PHASE_KEYS = [
    "nino_phase_sin",
    "nino_phase_cos",
    "soi_phase_sin",
    "soi_phase_cos",
]

VELOCITY_LAGS = [1, 3, 12]
ORIGIN_STRIDE = 3
MIN_FLOW_TRAIN = max(MIN_TRAIN, 120)
MIN_REGIME_EXAMPLES = 45
RIDGE_ALPHA_TRANSITION = 20.0
RIDGE_ALPHA_DECODER = 5.0
RIDGE_ALPHA_DIRECT = 10.0

MODEL_KEYS = [
    "persistence",
    "phase_clean_flow_decoder",
    "phase_regime_gated_flow_decoder",
    "phase_velocity_flow_decoder",
    "phase_regime_velocity_flow_decoder",
    "raw_analog_baseline",
    "lag_ridge",
    "oracle_phase_decoder",
]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def round_float(value, digits=6):
    return round(finite(value), digits)


def subset_features(features, keys):
    return {key: finite(features.get(key, 0.0)) for key in keys}


def cache_keys(cache, anchors):
    keys = set()
    for anchor in anchors:
        keys.update(cache[anchor].keys())
    return sorted(keys)


def train_decoder(phase_cache, decoder_anchors, nino_raw):
    train_x = [subset_features(phase_cache[a], PHASE_KEYS) for a in decoder_anchors]
    train_y = [float(nino_raw[a - 1]) for a in decoder_anchors]
    return fit_ridge_model(train_x, train_y, alpha=RIDGE_ALPHA_DECODER)


def decode_phase(decoder, phase_features):
    return float(predict_ridge_model(decoder, subset_features(phase_features, PHASE_KEYS))[0])


def normalize_phase(features):
    out = dict(features)
    for prefix in ["nino_phase", "soi_phase"]:
        sx_key = f"{prefix}_sin"
        cx_key = f"{prefix}_cos"
        sx = finite(out.get(sx_key, 0.0))
        cx = finite(out.get(cx_key, 1.0))
        norm = math.hypot(sx, cx)
        if norm > 1e-9:
            out[sx_key] = sx / norm
            out[cx_key] = cx / norm
    return {key: finite(out.get(key, 0.0)) for key in PHASE_KEYS}


def delta_feature(cache, anchor, key, lag):
    here = finite(cache[anchor].get(key, 0.0))
    prior_anchor = anchor - int(lag)
    if prior_anchor not in cache:
        return 0.0
    return here - finite(cache[prior_anchor].get(key, 0.0))


def accel_feature(cache, anchor, key, lag):
    lag = int(lag)
    a0 = anchor
    a1 = anchor - lag
    a2 = anchor - 2 * lag
    if a1 not in cache or a2 not in cache:
        return 0.0
    return finite(cache[a0].get(key, 0.0)) - 2.0 * finite(cache[a1].get(key, 0.0)) + finite(cache[a2].get(key, 0.0))


def phase_clean_input(phase_cache, anchor):
    return subset_features(phase_cache[anchor], PHASE_KEYS)


def phase_velocity_input(compact_cache, phase_cache, anchor):
    out = {}
    support_keys = PHASE_KEYS + [
        "nino_boundary_distance_phi",
        "nino_boundary_distance_balance",
        "nino_boundary_distance_time",
        "nino_soi_coupling_energy_log",
        "nino_pdo_coupling_energy_log",
        "nino_soi_coupling_pressure",
        "nino_pdo_coupling_pressure",
        "enso_feeder_pressure",
        "enso_counterbalance_gate",
    ]
    for key in support_keys:
        source = phase_cache if key in PHASE_KEYS else compact_cache
        out[f"now_{key}"] = finite(source[anchor].get(key, 0.0))
        for lag in VELOCITY_LAGS:
            out[f"d{lag}_{key}"] = delta_feature(source, anchor, key, lag)
            out[f"a{lag}_{key}"] = accel_feature(source, anchor, key, lag)
    return {key: finite(value) for key, value in out.items()}


def predict_phase_ridge(input_rows, phase_cache, train_anchors, origin, horizon, input_row):
    train_x = [input_rows[s] for s in train_anchors]
    train_y = [[finite(phase_cache[s + horizon].get(key, 0.0)) for key in PHASE_KEYS] for s in train_anchors]
    model = fit_ridge_model(train_x, train_y, alpha=RIDGE_ALPHA_TRANSITION)
    pred = predict_ridge_model(model, input_row)
    return normalize_phase({key: value for key, value in zip(PHASE_KEYS, pred)})


def sign_class(value, eps=0.10):
    value = finite(value, 0.0)
    if value > eps:
        return "pos"
    if value < -eps:
        return "neg"
    return "zero"


def trend_class(values, anchor, lag=3, eps=0.05):
    current = finite(values[anchor - 1], 0.0)
    prior_idx = anchor - 1 - int(lag)
    prior = finite(values[prior_idx], current) if prior_idx >= 0 else current
    delta = current - prior
    if delta > eps:
        return "up"
    if delta < -eps:
        return "down"
    return "flat"


def phase_gap_class(compact_cache, anchor):
    gap = finite(compact_cache[anchor].get("nino_soi_partner_phase_gap", 0.0))
    if gap >= 0.38:
        return "anti"
    if gap <= 0.12:
        return "same"
    return "mixed"


def boundary_motion_class(compact_cache, anchor):
    d3 = delta_feature(compact_cache, anchor, "nino_boundary_distance_phi", 3)
    d12 = delta_feature(compact_cache, anchor, "nino_boundary_distance_phi", 12)
    motion = 0.7 * d3 + 0.3 * d12
    if motion < -0.015:
        return "approach_phi"
    if motion > 0.015:
        return "retreat_phi"
    return "boundary_flat"


def pdo_coupling_class(compact_cache, anchor, threshold):
    value = finite(compact_cache[anchor].get("nino_pdo_coupling_energy_log", 0.0))
    return "pdo_high" if value >= threshold else "pdo_low"


def regime_parts(compact_cache, series, anchor, pdo_threshold):
    nino = series["NINO"]["z"]
    soi = series["SOI"]["z"]
    parts = {
        "nino_sign": sign_class(nino[anchor - 1]),
        "nino_trend": trend_class(nino, anchor),
        "soi_sign": sign_class(soi[anchor - 1]),
        "soi_trend": trend_class(soi, anchor),
        "phase_gap": phase_gap_class(compact_cache, anchor),
        "boundary_motion": boundary_motion_class(compact_cache, anchor),
        "pdo_coupling": pdo_coupling_class(compact_cache, anchor, pdo_threshold),
    }
    return parts


def regime_label(parts, level="full"):
    if level == "full":
        keys = ["nino_sign", "nino_trend", "soi_sign", "soi_trend", "phase_gap", "boundary_motion", "pdo_coupling"]
    elif level == "no_pdo":
        keys = ["nino_sign", "nino_trend", "soi_sign", "soi_trend", "phase_gap", "boundary_motion"]
    elif level == "core":
        keys = ["nino_trend", "soi_trend", "phase_gap"]
    elif level == "phase":
        keys = ["phase_gap"]
    else:
        keys = []
    return "|".join(parts[key] for key in keys) if keys else "global"


def matching_regime_anchors(compact_cache, series, train_anchors, origin, pdo_threshold):
    origin_parts = regime_parts(compact_cache, series, origin, pdo_threshold)
    train_parts = {a: regime_parts(compact_cache, series, a, pdo_threshold) for a in train_anchors}
    for level in ["full", "no_pdo", "core", "phase"]:
        label = regime_label(origin_parts, level)
        matched = [a for a in train_anchors if regime_label(train_parts[a], level) == label]
        if len(matched) >= MIN_REGIME_EXAMPLES:
            return matched, {"level": level, "label": label, "n": int(len(matched)), "parts": origin_parts}
    return train_anchors, {"level": "global", "label": "global", "n": int(len(train_anchors)), "parts": origin_parts}


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


def format_score(score):
    if "mae" not in score:
        return "n/a"
    return (
        f"MAE={score['mae']:.4f} vs pers={score['persistence_mae']:.4f} "
        f"lift={score['mae_lift_vs_persistence']:+.4f} corr={score['corr']:+.3f} "
        f"dir={score['direction']:.3f}"
    )


def best_forecast(scores, horizon):
    rows = []
    for model in MODEL_KEYS:
        if model.startswith("oracle_"):
            continue
        rows.append((scores[model][horizon].get("mae", float("inf")), model))
    rows.sort()
    return rows[0][1]


def summarize_regimes(records):
    counts = Counter(record["level"] for record in records)
    train_sizes = [record["n"] for record in records]
    return {
        "levels": dict(sorted(counts.items())),
        "mean_train_examples": float(np.mean(train_sizes)) if train_sizes else None,
        "min_train_examples": int(min(train_sizes)) if train_sizes else None,
        "max_train_examples": int(max(train_sizes)) if train_sizes else None,
    }


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

    print("ARA phase-flow predictor")
    print("=" * 104)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}")
    print(f"test origins start: {dates[test_start - 1].date()}  stride={ORIGIN_STRIDE}")
    print("models: clean phase, regime-gated phase, velocity-aware phase")
    print("strict guards: transition s+h<t; decoder a<t")
    print()

    compact_cache = {}
    phase_cache = {}
    raw_cache = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        snap = build_snapshot(series, anchor)
        compact = compact_state_features(snap)
        compact_cache[anchor] = compact
        phase_cache[anchor] = subset_features(compact, PHASE_KEYS)
        raw_cache[anchor] = raw_lag_state_features(series, anchor)
        if i % 100 == 0:
            print(f"  cached states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    clean_inputs = {anchor: phase_clean_input(phase_cache, anchor) for anchor in all_anchors}
    velocity_inputs = {anchor: phase_velocity_input(compact_cache, phase_cache, anchor) for anchor in all_anchors}
    raw_keys = cache_keys(raw_cache, all_anchors)

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS}
    regime_records = {h: [] for h in HORIZONS}

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

            actual = float(nino_raw[target_anchor - 1])
            persistence = float(nino_raw[origin - 1])
            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")
            decoder = train_decoder(phase_cache, decoder_anchors, nino_raw)

            all_points["persistence"][h].append(point(origin_date, target_date, persistence, actual, persistence))

            clean_phase = predict_phase_ridge(clean_inputs, phase_cache, train_transition, origin, h, clean_inputs[origin])
            clean_pred = decode_phase(decoder, clean_phase)
            all_points["phase_clean_flow_decoder"][h].append(point(origin_date, target_date, clean_pred, actual, persistence))

            pdo_threshold = float(
                np.median([finite(compact_cache[s].get("nino_pdo_coupling_energy_log", 0.0)) for s in train_transition])
            )
            matched, regime_info = matching_regime_anchors(compact_cache, series, train_transition, origin, pdo_threshold)
            regime_records[h].append(regime_info)
            regime_phase = predict_phase_ridge(clean_inputs, phase_cache, matched, origin, h, clean_inputs[origin])
            regime_pred = decode_phase(decoder, regime_phase)
            all_points["phase_regime_gated_flow_decoder"][h].append(
                point(origin_date, target_date, regime_pred, actual, persistence, regime_info)
            )

            velocity_phase = predict_phase_ridge(velocity_inputs, phase_cache, train_transition, origin, h, velocity_inputs[origin])
            velocity_pred = decode_phase(decoder, velocity_phase)
            all_points["phase_velocity_flow_decoder"][h].append(point(origin_date, target_date, velocity_pred, actual, persistence))

            regime_velocity_phase = predict_phase_ridge(velocity_inputs, phase_cache, matched, origin, h, velocity_inputs[origin])
            regime_velocity_pred = decode_phase(decoder, regime_velocity_phase)
            all_points["phase_regime_velocity_flow_decoder"][h].append(
                point(origin_date, target_date, regime_velocity_pred, actual, persistence, regime_info)
            )

            raw_pred, raw_dist = analog_direct_raw_prediction(raw_cache, train_transition, origin, h, raw_keys, nino_raw)
            all_points["raw_analog_baseline"][h].append(point(origin_date, target_date, raw_pred, actual, persistence, raw_dist))

            train_raw_delta = [float(nino_raw[s + h - 1] - nino_raw[s - 1]) for s in train_transition]
            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(series["NINO"]["z"], s) for s in train_transition],
                train_raw_delta,
                lag_feature_dict(series["NINO"]["z"], origin),
                alpha=RIDGE_ALPHA_DIRECT,
            )
            all_points["lag_ridge"][h].append(point(origin_date, target_date, persistence + lag_delta, actual, persistence))

            oracle_pred = decode_phase(decoder, phase_cache[target_anchor])
            all_points["oracle_phase_decoder"][h].append(point(origin_date, target_date, oracle_pred, actual, persistence))

        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:36s} {format_score(score_points(all_points[model][h]))}")
        print(f"  regime levels: {summarize_regimes(regime_records[h])['levels']}")
        print()

    scores = {model: {h: score_points(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS}
    winners = {str(h): best_forecast(scores, h) for h in HORIZONS}
    regime_summary = {str(h): summarize_regimes(regime_records[h]) for h in HORIZONS}

    out = {
        "date": "2026-05-24",
        "method": "strict-causal phase-flow predictor",
        "leakage_guard": [
            "S(t), velocity, acceleration, raw sign, and trend inputs use only anchors <= t.",
            "Transition models use only completed pairs s+h<t.",
            "Regime thresholds are computed only from the current transition-training set.",
            "Decoders use only geometry anchors a<t.",
            "Oracle phase decoder uses actual S(t+h) and is diagnostic only.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "rungs_k": RUNG_KS,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "velocity_lags_months": VELOCITY_LAGS,
        "phase_keys": PHASE_KEYS,
        "min_regime_examples": MIN_REGIME_EXAMPLES,
        "ridge_alpha_transition": RIDGE_ALPHA_TRANSITION,
        "ridge_alpha_decoder": RIDGE_ALPHA_DECODER,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
        },
        "models": {
            "phase_clean_flow_decoder": "Current NINO/SOI phase only -> future phase -> phase decoder.",
            "phase_regime_gated_flow_decoder": "Clean phase flow trained only inside the current regime, with hierarchical fallback.",
            "phase_velocity_flow_decoder": "Phase plus phase/boundary/coupling velocity and acceleration -> future phase -> phase decoder.",
            "phase_regime_velocity_flow_decoder": "Velocity-aware phase flow trained inside current regime, with fallback.",
            "raw_analog_baseline": "Raw NINO/SOI/PDO lag analog baseline.",
            "lag_ridge": "Causal NINO lag/slope ridge baseline.",
            "oracle_phase_decoder": "Diagnostic only: phase decoder applied to actual future NINO/SOI phase.",
        },
        "regime_summary": regime_summary,
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
        "window.ARA_PHASE_FLOW_PREDICTOR = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Winners:")
    for h in HORIZONS:
        print(f"  h={h:>2}: {winners[str(h)]}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
