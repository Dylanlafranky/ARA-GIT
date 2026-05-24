"""
ara_enso_12m_feeder_amplitude_test.py

Strict-causal test for Dylan's feeder-amplitude idea:

    below/faster systems record incoming energy first
    -> that energy feeds upward after a scale-distance delay
    -> shape prior gives the future transition shape
    -> feeder energy sets amplitude/sign strength

For the 12-month ENSO coupled LI target, this samples lower-rung feeder states
at the earlier index implied by:

    delay(period) = period * log(home_period / period) / log(base)
    feeder_sample = target_index - delay(period)

Only feeder_sample <= origin is used. If a period would require future feeder
data, it is skipped. This keeps the test strict-causal.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_framework import causal_bandpass
from ara_enso_12m_geometry_state_predictor_test import (
    HORIZON,
    LAGS,
    MIN_ORIGIN,
    WINDOWS,
    clean_for_json,
    finite,
    matrix_from_dicts,
    rolling_stats,
    run_lag_model,
    run_old_ara_matched,
    train_ridge,
    predict_ridge,
)
from ara_nasal_to_enso_prediction_test import load_templates_and_signals, mae, corr, score_prediction


OUT_JSON = HERE / "ara_enso_12m_feeder_amplitude_result.json"
OUT_JS = HERE / "ara_enso_12m_feeder_amplitude_result.js"

HOME_PERIOD = 47.0
LOWER_PERIODS = [3.0, 4.0, 6.0, 8.0, 12.0, 16.0, 24.0]
DELAY_BASES = {"base2": 2.0, "phi": (1.0 + math.sqrt(5.0)) / 2.0}
RIDGE_ALPHA = 8.0
ALPHA_GRID = [0.3, 1.0, 3.0, 8.0, 20.0, 50.0, 100.0]
EPS = 1e-9


def safe_sign(value):
    value = finite(value)
    if abs(value) < 1e-12:
        return 0.0
    return 1.0 if value > 0 else -1.0


def scale_delay(period, base):
    if period <= 0 or period >= HOME_PERIOD:
        return 0.0
    return float(period * math.log(HOME_PERIOD / period) / math.log(base))


def feeder_sample_index(origin, horizon, period, base):
    target_idx = origin + horizon
    sample = int(math.floor(target_idx - scale_delay(period, base)))
    return sample if sample <= origin else None


def bandpass_features(signal, idx, period):
    period = float(period)
    p_int = max(2, int(round(period)))
    if idx < max(8, int(math.ceil(4.0 * period))):
        return {
            "bp_value": 0.0,
            "bp_slope": 0.0,
            "amp": 0.0,
            "energy": 0.0,
            "norm_value": 0.0,
            "rolling_std": 0.0,
            "rolling_slope": 0.0,
        }
    arr = np.asarray(signal[: idx + 1], dtype=float)
    bp = causal_bandpass(arr, period)
    last = float(bp[-1])
    prev = float(bp[-2]) if len(bp) > 1 else last
    cycle = bp[-p_int:]
    amp = float((np.max(cycle) - np.min(cycle)) / 2.0)
    mean, std, slope = rolling_stats(signal, idx, p_int)
    return {
        "bp_value": last,
        "bp_slope": last - prev,
        "amp": amp,
        "energy": amp * amp,
        "norm_value": last / (amp + EPS),
        "rolling_std": std,
        "rolling_slope": slope,
    }


def current_signal_features(out, name, signal, origin):
    current = float(signal[origin])
    out[f"{name}_current"] = current
    out[f"{name}_abs"] = abs(current)
    out[f"{name}_sign"] = safe_sign(current)
    for lag in LAGS:
        if origin - lag >= 0:
            lagv = float(signal[origin - lag])
        else:
            lagv = current
        out[f"{name}_lag{lag}"] = lagv
        out[f"{name}_delta{lag}"] = current - lagv
    for window in WINDOWS:
        mean, std, slope = rolling_stats(signal, origin, window)
        out[f"{name}_mean{window}"] = mean
        out[f"{name}_std{window}"] = std
        out[f"{name}_slope{window}"] = slope


def build_old_shape_payload(state, train_origins, test_origins):
    train_payload = run_old_ara_matched(state, train_origins, train_origins)
    test_payload = run_old_ara_matched(state, train_origins, test_origins)
    return train_payload, test_payload


def build_feeder_features(state, origin, carrier_raw, carrier_decoded, include_detail=True):
    target = state["target"]
    signals = {
        "li": target,
        "nino": state["signals"]["nino_only"],
        "soi": state["signals"]["soi_only"],
        "gap": state["signals"]["nino_only"] - state["signals"]["soi_only"],
        "sum": state["signals"]["nino_only"] + state["signals"]["soi_only"],
    }
    out = {
        "carrier_raw": finite(carrier_raw),
        "carrier_decoded": finite(carrier_decoded),
        "carrier_raw_abs": abs(finite(carrier_raw)),
        "carrier_decoded_abs": abs(finite(carrier_decoded)),
        "carrier_agreement": safe_sign(carrier_raw) * safe_sign(carrier_decoded),
        "origin_value": float(target[origin]),
        "origin_abs": abs(float(target[origin])),
    }

    month = int(state["dates"][origin][5:7])
    angle = 2.0 * math.pi * (month - 1) / 12.0
    out["season_sin"] = math.sin(angle)
    out["season_cos"] = math.cos(angle)

    for name, signal in signals.items():
        current_signal_features(out, name, signal, origin)

    for base_name, base in DELAY_BASES.items():
        total_energy = 0.0
        total_pressure = 0.0
        total_slope = 0.0
        total_abs_norm = 0.0
        used = 0
        for period in LOWER_PERIODS:
            sample = feeder_sample_index(origin, HORIZON, period, base)
            if sample is None or sample < 0:
                continue
            used += 1
            period_weight = math.exp(-abs(scale_delay(period, base) - HORIZON) / max(HORIZON, 1.0))
            for signal_name, signal in signals.items():
                feats = bandpass_features(signal, sample, period)
                prefix = f"feed_{base_name}_{signal_name}_p{int(period)}"
                total_energy += period_weight * feats["energy"]
                total_pressure += period_weight * feats["bp_value"]
                total_slope += period_weight * feats["bp_slope"]
                total_abs_norm += period_weight * abs(feats["norm_value"])
                if include_detail:
                    out[f"{prefix}_sample_lag"] = float(origin - sample)
                    out[f"{prefix}_energy"] = feats["energy"]
                    out[f"{prefix}_amp"] = feats["amp"]
                    out[f"{prefix}_pressure"] = feats["bp_value"]
                    out[f"{prefix}_slope"] = feats["bp_slope"]
                    out[f"{prefix}_norm_value"] = feats["norm_value"]
                    out[f"{prefix}_rolling_std"] = feats["rolling_std"]
                    out[f"{prefix}_rolling_slope"] = feats["rolling_slope"]

        out[f"feed_{base_name}_used_count"] = float(used)
        out[f"feed_{base_name}_total_energy"] = total_energy
        out[f"feed_{base_name}_total_pressure"] = total_pressure
        out[f"feed_{base_name}_total_slope"] = total_slope
        out[f"feed_{base_name}_total_abs_norm"] = total_abs_norm
        out[f"feed_{base_name}_raw_x_energy"] = finite(carrier_raw) * total_energy
        out[f"feed_{base_name}_raw_x_pressure"] = finite(carrier_raw) * total_pressure
        out[f"feed_{base_name}_decoded_x_energy"] = finite(carrier_decoded) * total_energy
        out[f"feed_{base_name}_decoded_x_pressure"] = finite(carrier_decoded) * total_pressure

    return {k: finite(v) for k, v in out.items()}


def fit_predict_feature_model(train_rows, y_train, test_rows, alpha=RIDGE_ALPHA):
    keys = sorted({key for row in train_rows for key in row.keys()})
    x_train = matrix_from_dicts(train_rows, keys)
    x_test = matrix_from_dicts(test_rows, keys)
    model = train_ridge(x_train, y_train, alpha)
    return predict_ridge(model, x_test), keys


def run_factorized_model(train_rows, y_train, test_rows, alpha=RIDGE_ALPHA):
    abs_y = np.abs(np.asarray(y_train, dtype=float))
    sign_y = np.asarray([safe_sign(v) for v in y_train], dtype=float)
    amp_pred, amp_keys = fit_predict_feature_model(train_rows, abs_y, test_rows, alpha=alpha)
    sign_pred, sign_keys = fit_predict_feature_model(train_rows, sign_y, test_rows, alpha=alpha)
    amp_pred = np.maximum(0.0, amp_pred)
    sign_pred = np.clip(sign_pred, -1.25, 1.25)
    return sign_pred * amp_pred, {
        "amp_features": len(amp_keys),
        "sign_features": len(sign_keys),
        "alpha": float(alpha),
    }


def run_shape_fixed_sign_model(train_rows, y_train, test_rows, alpha=RIDGE_ALPHA):
    abs_y = np.abs(np.asarray(y_train, dtype=float))
    amp_pred, keys = fit_predict_feature_model(train_rows, abs_y, test_rows, alpha=alpha)
    amp_pred = np.maximum(0.0, amp_pred)
    signs = np.asarray([safe_sign(row.get("carrier_decoded", row.get("carrier_raw", 0.0))) for row in test_rows], dtype=float)
    return signs * amp_pred, {"amp_features": len(keys), "alpha": float(alpha)}


def select_factor_alpha(train_rows, y_train, current_train, metric="mae"):
    split = max(40, int(len(train_rows) * 0.66))
    fit_rows = train_rows[:split]
    fit_y = y_train[:split]
    calib_rows = train_rows[split:]
    calib_y = y_train[split:]
    calib_current = current_train[split:]
    candidates = []
    for alpha in ALPHA_GRID:
        pred, _ = run_factorized_model(fit_rows, fit_y, calib_rows, alpha=alpha)
        score = score_prediction(pred, calib_y, calib_current)
        candidates.append((alpha, score))
    if metric == "corr":
        alpha, score = max(candidates, key=lambda item: item[1]["corr"])
    else:
        alpha, score = min(candidates, key=lambda item: item[1]["mae"])
    return float(alpha), score, [{"alpha": float(a), "score": s} for a, s in candidates]


def main():
    print("Loading ENSO/nasal state...")
    state = load_templates_and_signals()
    split = state["split"]
    target = state["target"]
    train_origins = list(range(MIN_ORIGIN, split - HORIZON))
    test_origins = list(range(split, len(target) - HORIZON))
    y_train = np.asarray([target[o + HORIZON] for o in train_origins], dtype=float)
    y_test = np.asarray([target[o + HORIZON] for o in test_origins], dtype=float)
    current_train = np.asarray([target[o] for o in train_origins], dtype=float)
    current_test = np.asarray([target[o] for o in test_origins], dtype=float)

    print(f"Train origins={len(train_origins)} test origins={len(test_origins)}")
    print("Building old ARA/midpoint carriers...")
    old_train, old_test = build_old_shape_payload(state, train_origins, test_origins)

    train_raw = np.asarray(old_train["raw_pred_values"], dtype=float)
    train_decoded = np.asarray(old_train["pred_values"], dtype=float)
    test_raw = np.asarray(old_test["raw_pred_values"], dtype=float)
    test_decoded = np.asarray(old_test["pred_values"], dtype=float)

    print("Building below-rung feeder features...")
    train_rows = [
        build_feeder_features(state, o, r, d, include_detail=True)
        for o, r, d in zip(train_origins, train_raw, train_decoded)
    ]
    test_rows = [
        build_feeder_features(state, o, r, d, include_detail=True)
        for o, r, d in zip(test_origins, test_raw, test_decoded)
    ]
    train_rows_agg = [
        build_feeder_features(state, o, r, d, include_detail=False)
        for o, r, d in zip(train_origins, train_raw, train_decoded)
    ]
    test_rows_agg = [
        build_feeder_features(state, o, r, d, include_detail=False)
        for o, r, d in zip(test_origins, test_raw, test_decoded)
    ]

    baselines = {
        "persistence": score_prediction(current_test, y_test, current_test),
        "old_nasal_ara_matched_template": old_test["decoded_score"],
        "old_nasal_ara_matched_raw": old_test["raw_score"],
        "lag_only_ridge": run_lag_model(state, train_origins, test_origins)["score"],
    }

    direct_pred, direct_keys = fit_predict_feature_model(train_rows, y_train, test_rows)
    factor_pred, factor_meta = run_factorized_model(train_rows, y_train, test_rows)
    fixed_sign_pred, fixed_meta = run_shape_fixed_sign_model(train_rows, y_train, test_rows)
    direct_agg_pred, direct_agg_keys = fit_predict_feature_model(train_rows_agg, y_train, test_rows_agg)
    factor_agg_pred, factor_agg_meta = run_factorized_model(train_rows_agg, y_train, test_rows_agg)
    fixed_agg_pred, fixed_agg_meta = run_shape_fixed_sign_model(train_rows_agg, y_train, test_rows_agg)
    alpha_mae, alpha_mae_score, alpha_candidates_mae = select_factor_alpha(train_rows_agg, y_train, current_train, metric="mae")
    alpha_corr, alpha_corr_score, alpha_candidates_corr = select_factor_alpha(train_rows_agg, y_train, current_train, metric="corr")
    factor_agg_mae_pred, factor_agg_mae_meta = run_factorized_model(train_rows_agg, y_train, test_rows_agg, alpha=alpha_mae)
    factor_agg_corr_pred, factor_agg_corr_meta = run_factorized_model(train_rows_agg, y_train, test_rows_agg, alpha=alpha_corr)

    models = {
        "feeder_direct_value_control": {
            "label": "Direct ridge from shape carriers plus delayed below-rung feeder features to future value.",
            "n_features": int(len(direct_keys)),
            "score": score_prediction(direct_pred, y_test, current_test),
        },
        "feeder_sign_amp_factorized": {
            "label": "Separate sign and amplitude models from delayed feeder energy; pred = sign_score * amplitude.",
            **factor_meta,
            "score": score_prediction(factor_pred, y_test, current_test),
        },
        "shape_fixed_sign_feeder_amp": {
            "label": "Use old shape sign only; feeder features predict amplitude.",
            **fixed_meta,
            "score": score_prediction(fixed_sign_pred, y_test, current_test),
        },
        "feeder_direct_value_aggregate_control": {
            "label": "Direct ridge from shape carriers plus aggregate delayed feeder pressure/energy only.",
            "n_features": int(len(direct_agg_keys)),
            "score": score_prediction(direct_agg_pred, y_test, current_test),
        },
        "feeder_sign_amp_aggregate_factorized": {
            "label": "Aggregate-only separate sign and amplitude models.",
            **factor_agg_meta,
            "score": score_prediction(factor_agg_pred, y_test, current_test),
        },
        "shape_fixed_sign_aggregate_amp": {
            "label": "Use old shape sign only; aggregate feeder features predict amplitude.",
            **fixed_agg_meta,
            "score": score_prediction(fixed_agg_pred, y_test, current_test),
        },
        "feeder_sign_amp_aggregate_alpha_mae_selected": {
            "label": "Aggregate sign/amplitude model with ridge alpha selected on inner-train MAE only.",
            **factor_agg_mae_meta,
            "inner_selected_alpha": alpha_mae,
            "inner_selection_score": alpha_mae_score,
            "inner_candidates": alpha_candidates_mae,
            "score": score_prediction(factor_agg_mae_pred, y_test, current_test),
        },
        "feeder_sign_amp_aggregate_alpha_corr_selected": {
            "label": "Aggregate sign/amplitude model with ridge alpha selected on inner-train correlation only.",
            **factor_agg_corr_meta,
            "inner_selected_alpha": alpha_corr,
            "inner_selection_score": alpha_corr_score,
            "inner_candidates": alpha_candidates_corr,
            "score": score_prediction(factor_agg_corr_pred, y_test, current_test),
        },
    }

    rows = []
    for name, score in baselines.items():
        rows.append((name, score["mae"], score["corr"]))
    for name, payload in models.items():
        score = payload["score"]
        rows.append((name, score["mae"], score["corr"]))
    best_mae = min(rows, key=lambda row: row[1])
    best_corr = max(rows, key=lambda row: row[2])

    payload = {
        "date": "2026-05-23",
        "method": "Strict-causal 12-month ENSO below-rung feeder amplitude test. Lower/faster feeder states are sampled at scale-delay-aligned times before the forecast origin, then used to amplitude/sign-gate the ARA shape prior.",
        "horizon_months": HORIZON,
        "home_period_months": HOME_PERIOD,
        "lower_periods_months": LOWER_PERIODS,
        "delay_rule": "delay = period * log(home_period / period) / log(base); feeder_sample = origin + horizon - delay; only sample<=origin is allowed.",
        "leakage_guard": [
            "NINO/SOI scaling and old ARA/midpoint shape carrier inherit train-only loader.",
            "Feeder sample indices are never later than the forecast origin.",
            "Causal bandpass features at a feeder sample use only data through that sample.",
            "All model fitting uses pre-split origins only; heldout origins are after 2003-07-01.",
        ],
        "split": {
            "index": int(split),
            "date": state["dates"][split],
            "train_origins": int(len(train_origins)),
            "test_origins": int(len(test_origins)),
            "test_end": state["dates"][test_origins[-1] + HORIZON],
        },
        "baselines": baselines,
        "models": models,
        "summary": {
            "best_mae_model": best_mae[0],
            "best_mae": float(best_mae[1]),
            "best_mae_corr": float(best_mae[2]),
            "best_corr_model": best_corr[0],
            "best_corr": float(best_corr[2]),
            "best_corr_mae": float(best_corr[1]),
        },
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(payload), indent=2), encoding="utf-8")
    OUT_JS.write_text("window.ARA_ENSO_12M_FEEDER_AMPLITUDE = " + json.dumps(clean_for_json(payload)) + ";\n", encoding="utf-8")

    print("\n=== 12M FEEDER AMPLITUDE SUMMARY ===")
    for name, score in baselines.items():
        print(f"{name:34s} MAE={score['mae']:.3f} corr={score['corr']:+.3f} turn={score.get('turn_event_accuracy', 0):.3f}")
    for name, payload in models.items():
        score = payload["score"]
        print(f"{name:34s} MAE={score['mae']:.3f} corr={score['corr']:+.3f} turn={score.get('turn_event_accuracy', 0):.3f}")
    print(f"Best corr: {best_corr[0]} corr={best_corr[2]:+.3f} MAE={best_corr[1]:.3f}")
    print(f"Best MAE : {best_mae[0]} MAE={best_mae[1]:.3f} corr={best_mae[2]:+.3f}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    main()
