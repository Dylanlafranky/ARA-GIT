"""
ara_targeted_geometry_flow_predictor.py

Strict-causal follow-up to the oracle geometry ablation.

The ablation said the decoder mostly needs a small future-geometry target:

  - NINO phase
  - SOI phase
  - NINO energy/rung context
  - NINO-SOI and NINO-PDO coupling energy
  - NINO build/release orientation

This script asks whether those smaller geometry targets can be forecast better
than the whole compact state.  It adds geometry velocity and acceleration to
the flow input, then decodes the predicted target geometry back into NINO3.4.

Leakage guard for origin t and horizon h:

  - S(t) and all velocity features use only snapshots at anchors <= t.
  - Transition training uses only completed pairs s+h<t.
  - Decoder training uses only geometry anchors a<t.
  - Oracle decoders use actual S(t+h) and are diagnostic only.
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
    K_NEIGHBORS,
    analog_direct_raw_prediction,
    analog_weights,
    compact_state_features,
    feature_bounds,
    raw_lag_state_features,
    sanitize_features,
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


OUT_JSON = HERE / "ara_targeted_geometry_flow_predictor_result.json"
OUT_JS = HERE / "ara_targeted_geometry_flow_predictor_result.js"

ORIGIN_STRIDE = 3
RIDGE_ALPHA_TRANSITION = 20.0
RIDGE_ALPHA_DECODER = 5.0
RIDGE_ALPHA_DIRECT = 10.0
MIN_FLOW_TRAIN = max(MIN_TRAIN, 120)
VELOCITY_LAGS = [1, 3, 12]


PHASE_KEYS = [
    "nino_phase_sin",
    "nino_phase_cos",
    "soi_phase_sin",
    "soi_phase_cos",
]

PHASE_ENERGY_KEYS = PHASE_KEYS + [
    "nino_amplitude_energy_log",
    "nino_rung_position",
    "nino_weighted_k",
    "nino_occupancy_entropy",
    "nino_home_distance",
    "nino_pdo_coupling_energy_log",
    "nino_soi_coupling_energy_log",
    "nino_orientation_release_balance",
]

SELECTED_TARGET_KEYS = PHASE_ENERGY_KEYS + [
    "pdo_phase_sin",
    "pdo_phase_cos",
    "soi_amplitude_energy_log",
    "nino_pdo_coupling_pressure",
    "nino_pdo_rung_distance",
    "nino_pdo_ara_gap",
    "nino_soi_coupling_pressure",
    "nino_soi_rung_distance",
    "nino_soi_ara_gap",
    "nino_regime_accumulate_side",
    "nino_regime_balance_engine",
    "nino_regime_release_donor",
    "enso_feeder_pressure",
    "enso_counterbalance_gate",
    "enso_partner_gap",
]

TARGET_SETS = {
    "phase_only": PHASE_KEYS,
    "phase_energy": PHASE_ENERGY_KEYS,
    "selected": SELECTED_TARGET_KEYS,
}

MODEL_KEYS = [
    "persistence",
    "phase_only_ridge_flow_decoder",
    "phase_energy_ridge_flow_decoder",
    "selected_ridge_flow_decoder",
    "selected_analog_flow_decoder",
    "selected_direct_geometry_control",
    "raw_analog_baseline",
    "lag_ridge",
    "oracle_phase_only_decoder",
    "oracle_selected_decoder",
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


def matrix_from_cache(cache, anchors, keys):
    return np.asarray([[finite(cache[a].get(key, 0.0)) for key in keys] for a in anchors], dtype=float)


def vector_to_dict(vector, keys):
    return {key: finite(value) for key, value in zip(keys, vector)}


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


def flow_input_features(cache, anchor, target_keys):
    """Current target geometry plus velocity/acceleration and a few gates."""

    out = {}
    support_keys = sorted(
        set(target_keys)
        | {
            "enso_feeder_pressure",
            "enso_counterbalance_gate",
            "enso_partner_gap",
            "nino_soi_coupling_pressure",
            "nino_pdo_coupling_pressure",
            "nino_soi_partner_antiphase_fit",
            "nino_pdo_partner_antiphase_fit",
            "nino_boundary_distance_phi",
            "nino_boundary_distance_balance",
            "nino_boundary_distance_time",
        }
    )
    for key in support_keys:
        out[f"now_{key}"] = finite(cache[anchor].get(key, 0.0))
        for lag in VELOCITY_LAGS:
            out[f"d{lag}_{key}"] = delta_feature(cache, anchor, key, lag)
            out[f"a{lag}_{key}"] = accel_feature(cache, anchor, key, lag)
    return {key: finite(value) for key, value in out.items()}


def normalize_phase_pairs(features):
    out = dict(features)
    for base in ["nino_phase", "soi_phase", "pdo_phase"]:
        sin_key = f"{base}_sin"
        cos_key = f"{base}_cos"
        if sin_key not in out or cos_key not in out:
            continue
        sx = finite(out[sin_key], 0.0)
        cx = finite(out[cos_key], 1.0)
        norm = math.hypot(sx, cx)
        if norm > 1e-9:
            out[sin_key] = sx / norm
            out[cos_key] = cx / norm
    return out


def sanitize_target_prediction(features, bounds):
    out = sanitize_features(features, bounds)
    out = normalize_phase_pairs(out)
    for key in list(out):
        if "_regime_" in key:
            out[key] = min(1.0, max(0.0, finite(out[key])))
        if key.endswith("_energy_log") or key.endswith("_occupancy_entropy"):
            out[key] = max(0.0, finite(out[key]))
    return out


def analog_project_targets(input_cache, target_cache, train_anchors, origin, horizon, input_keys, target_keys, bounds):
    info = analog_weights(input_cache, train_anchors, origin, input_keys)
    current_targets = matrix_from_cache(target_cache, train_anchors, target_keys)
    future_targets = matrix_from_cache(target_cache, [a + horizon for a in train_anchors], target_keys)
    current_origin = matrix_from_cache(target_cache, [origin], target_keys)[0]
    deltas = future_targets - current_targets
    selected_delta = deltas[info["indices"]]
    pred_vec = current_origin + np.average(selected_delta, axis=0, weights=info["weights"])
    pred = sanitize_target_prediction(vector_to_dict(pred_vec, target_keys), bounds)
    effective_n = 1.0 / float(np.sum(info["weights"] ** 2)) if len(info["weights"]) else 0.0
    return pred, {
        "mean_neighbor_distance": float(np.mean(info["distances"])) if len(info["distances"]) else None,
        "effective_neighbors": effective_n,
        "neighbor_anchors": info["anchors"][:8],
    }


def predict_target_ridge(input_cache, target_cache, train_anchors, origin, horizon, input_keys, target_keys, bounds):
    train_x = [input_cache[s] for s in train_anchors]
    train_y = [[finite(target_cache[s + horizon].get(key, 0.0)) for key in target_keys] for s in train_anchors]
    model = fit_ridge_model(train_x, train_y, alpha=RIDGE_ALPHA_TRANSITION)
    pred_vec = predict_ridge_model(model, input_cache[origin])
    return sanitize_target_prediction(vector_to_dict(pred_vec, target_keys), bounds)


def train_decoder_model(target_cache, decoder_anchors, target_keys, nino_raw):
    train_x = [subset_features(target_cache[a], target_keys) for a in decoder_anchors]
    train_y = [float(nino_raw[a - 1]) for a in decoder_anchors]
    return fit_ridge_model(train_x, train_y, alpha=RIDGE_ALPHA_DECODER)


def decode(decoder, features, target_keys):
    return float(predict_ridge_model(decoder, subset_features(features, target_keys))[0])


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
    candidates = [m for m in MODEL_KEYS if not m.startswith("oracle_")]
    rows = [(scores[m][horizon].get("mae", float("inf")), m) for m in candidates]
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

    print("ARA targeted geometry flow predictor")
    print("=" * 104)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}")
    print(f"test origins start: {dates[test_start - 1].date()}  stride={ORIGIN_STRIDE}")
    print("targets: phase_only, phase_energy, selected")
    print("strict guards: transition s+h<t; decoder a<t")
    print()

    compact_cache = {}
    raw_cache = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        snap = build_snapshot(series, anchor)
        compact_cache[anchor] = compact_state_features(snap)
        raw_cache[anchor] = raw_lag_state_features(series, anchor)
        if i % 100 == 0:
            print(f"  cached states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    target_caches = {
        name: {anchor: subset_features(compact_cache[anchor], keys) for anchor in all_anchors}
        for name, keys in TARGET_SETS.items()
    }
    input_caches = {
        name: {anchor: flow_input_features(compact_cache, anchor, keys) for anchor in all_anchors}
        for name, keys in TARGET_SETS.items()
    }
    input_keys = {name: cache_keys(input_caches[name], all_anchors) for name in TARGET_SETS}
    raw_keys = cache_keys(raw_cache, all_anchors)

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS}

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

            all_points["persistence"][h].append(point(origin_date, target_date, persistence, actual, persistence))

            decoders = {
                name: train_decoder_model(target_caches[name], decoder_anchors, keys, nino_raw)
                for name, keys in TARGET_SETS.items()
            }
            bounds = {
                name: feature_bounds(target_caches[name], decoder_anchors, keys)
                for name, keys in TARGET_SETS.items()
            }

            for name, model_key in [
                ("phase_only", "phase_only_ridge_flow_decoder"),
                ("phase_energy", "phase_energy_ridge_flow_decoder"),
                ("selected", "selected_ridge_flow_decoder"),
            ]:
                keys = TARGET_SETS[name]
                pred_targets = predict_target_ridge(
                    input_caches[name],
                    target_caches[name],
                    train_transition,
                    origin,
                    h,
                    input_keys[name],
                    keys,
                    bounds[name],
                )
                pred = decode(decoders[name], pred_targets, keys)
                all_points[model_key][h].append(point(origin_date, target_date, pred, actual, persistence))

            selected_pred, analog_info = analog_project_targets(
                input_caches["selected"],
                target_caches["selected"],
                train_transition,
                origin,
                h,
                input_keys["selected"],
                TARGET_SETS["selected"],
                bounds["selected"],
            )
            selected_analog = decode(decoders["selected"], selected_pred, TARGET_SETS["selected"])
            all_points["selected_analog_flow_decoder"][h].append(
                point(origin_date, target_date, selected_analog, actual, persistence, analog_info)
            )

            train_raw_delta = [float(nino_raw[s + h - 1] - nino_raw[s - 1]) for s in train_transition]
            direct_delta, _, _ = fit_predict_ridge(
                [input_caches["selected"][s] for s in train_transition],
                train_raw_delta,
                input_caches["selected"][origin],
                alpha=RIDGE_ALPHA_DIRECT,
            )
            all_points["selected_direct_geometry_control"][h].append(
                point(origin_date, target_date, persistence + direct_delta, actual, persistence)
            )

            raw_pred, raw_dist = analog_direct_raw_prediction(raw_cache, train_transition, origin, h, raw_keys, nino_raw)
            all_points["raw_analog_baseline"][h].append(point(origin_date, target_date, raw_pred, actual, persistence, raw_dist))

            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(series["NINO"]["z"], s) for s in train_transition],
                train_raw_delta,
                lag_feature_dict(series["NINO"]["z"], origin),
                alpha=RIDGE_ALPHA_DIRECT,
            )
            all_points["lag_ridge"][h].append(point(origin_date, target_date, persistence + lag_delta, actual, persistence))

            oracle_phase = decode(decoders["phase_only"], target_caches["phase_only"][target_anchor], TARGET_SETS["phase_only"])
            all_points["oracle_phase_only_decoder"][h].append(point(origin_date, target_date, oracle_phase, actual, persistence))

            oracle_selected = decode(decoders["selected"], target_caches["selected"][target_anchor], TARGET_SETS["selected"])
            all_points["oracle_selected_decoder"][h].append(point(origin_date, target_date, oracle_selected, actual, persistence))

        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:36s} {format_score(score_points(all_points[model][h]))}")
        print()

    scores = {model: {h: score_points(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS}
    winners = {str(h): best_forecast(scores, h) for h in HORIZONS}

    out = {
        "date": "2026-05-24",
        "method": "strict-causal targeted future-geometry flow predictor",
        "leakage_guard": [
            "S(t), velocity, and acceleration features use only anchors <= t.",
            "Transition models use only completed pairs s+h<t.",
            "Decoders use only geometry anchors a<t.",
            "Oracle phase/selected decoders use actual S(t+h) and are diagnostic only.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "rungs_k": RUNG_KS,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "velocity_lags_months": VELOCITY_LAGS,
        "ridge_alpha_transition": RIDGE_ALPHA_TRANSITION,
        "ridge_alpha_decoder": RIDGE_ALPHA_DECODER,
        "target_sets": TARGET_SETS,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
        },
        "models": {
            "phase_only_ridge_flow_decoder": "Predict future NINO/SOI phase only, then decode.",
            "phase_energy_ridge_flow_decoder": "Predict phase plus NINO energy/rung and coupling-energy context, then decode.",
            "selected_ridge_flow_decoder": "Predict the broader ablation-selected future geometry target set, then decode.",
            "selected_analog_flow_decoder": "Analog transition over selected future targets using current geometry plus velocity/acceleration neighbors.",
            "selected_direct_geometry_control": "Control: current selected geometry/velocity directly regresses future raw value delta.",
            "raw_analog_baseline": "Raw NINO/SOI/PDO lag analog baseline.",
            "lag_ridge": "Causal NINO lag/slope ridge baseline.",
            "oracle_phase_only_decoder": "Diagnostic only: decode actual future phase fields.",
            "oracle_selected_decoder": "Diagnostic only: decode actual future selected geometry fields.",
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
        "window.ARA_TARGETED_GEOMETRY_FLOW_PREDICTOR = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Winners:")
    for h in HORIZONS:
        print(f"  h={h:>2}: {winners[str(h)]}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
