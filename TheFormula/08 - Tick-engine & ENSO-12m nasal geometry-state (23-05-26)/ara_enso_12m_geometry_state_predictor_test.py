"""
ara_enso_12m_geometry_state_predictor_test.py

Strict-causal 12-month ENSO test of the next proposed architecture:

    current data -> predicted future geometry state -> decoded ENSO state

This is intentionally not the same as direct value regression. The model first
predicts future coupled-state variables: sign, turn event, phase, ARA, midpoint,
and magnitude. A second decoder then maps those predicted state variables back
to the ENSO coupled laterality index.

Leakage guard:
  - NINO/SOI scaling and ENSO templates are inherited from the existing
    train-only nasal-to-ENSO loader.
  - All state models train on origins before the chronological split.
  - The decoder is calibrated only on predicted state variables from an inner
    train/calibration split, so it is not trained on actual future state labels
    and then asked to consume predicted labels at test time.
  - Held-out origins start after the split.
  - Oracle future-state decoding is diagnostic only.
"""

from __future__ import annotations

import json
import math
from bisect import bisect_right
from pathlib import Path

import numpy as np

from ara_nasal_to_enso_prediction_test import (
    EPS,
    HORIZONS,
    ara_matched_raw_prediction,
    build_ara_matched_rows,
    corr,
    last_completed_cycle_info,
    load_templates_and_signals,
    mae,
    ridge_fit,
    ridge_predict,
    score_prediction,
    sign_nonzero,
    template_raw_prediction,
)


HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "ara_enso_12m_geometry_state_predictor_result.json"
OUT_JS = HERE / "ara_enso_12m_geometry_state_predictor_result.js"

HORIZON = 12
MIN_ORIGIN = 120
RIDGE_ALPHA_STATE = 20.0
RIDGE_ALPHA_DECODER = 5.0
RIDGE_ALPHA_DIRECT = 10.0
CALIB_FRACTION = 0.34
LAGS = [1, 2, 3, 6, 9, 12, 18, 24, 36, 48, 60]
WINDOWS = [3, 6, 12, 24, 36]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def clean_for_json(value):
    if isinstance(value, dict):
        return {str(k): clean_for_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_for_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean_for_json(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        value = float(value)
        return value if math.isfinite(value) else None
    return value


def train_ridge(x, y, alpha):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    good = np.isfinite(y) & np.all(np.isfinite(x), axis=1)
    x = x[good]
    y = y[good]
    x_mean = np.mean(x, axis=0)
    x_std = np.std(x, axis=0)
    x_std[x_std < 1e-9] = 1.0
    xs = (x - x_mean) / x_std
    x1 = np.column_stack([np.ones(len(xs)), xs])
    reg = np.eye(x1.shape[1]) * float(alpha)
    reg[0, 0] = 0.0
    try:
        beta = np.linalg.solve(x1.T @ x1 + reg, x1.T @ y)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(x1.T @ x1 + reg, x1.T @ y, rcond=None)
    return {"beta": beta, "x_mean": x_mean, "x_std": x_std}


def predict_ridge(model, x):
    x = np.asarray(x, dtype=float)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    xs = (x - model["x_mean"]) / model["x_std"]
    x1 = np.column_stack([np.ones(len(xs)), xs])
    return x1 @ model["beta"]


def train_multi_ridge(x, y_by_name, alpha):
    return {name: train_ridge(x, values, alpha) for name, values in y_by_name.items()}


def predict_multi_ridge(models, x):
    return {name: predict_ridge(model, x) for name, model in models.items()}


def circular_phase_from_crossing(signal, crossings, period_info, idx):
    pos = bisect_right(crossings, idx) - 1
    if pos < 0:
        elapsed = float(idx)
        last = 0
    else:
        last = crossings[pos]
        elapsed = float(idx - last)
    full = max(2.0, float(period_info["median_full"]))
    half = max(1.0, float(period_info["median_half"]))
    phase = (elapsed / full) % 1.0
    return {
        "last_crossing": int(last),
        "elapsed": elapsed,
        "elapsed_frac_full": elapsed / full,
        "elapsed_frac_half": elapsed / half,
        "phase": phase,
        "phase_sin": math.sin(2.0 * math.pi * phase),
        "phase_cos": math.cos(2.0 * math.pi * phase),
    }


def cycle_info_at(crossings, idx):
    info = last_completed_cycle_info(crossings, idx)
    if info is None:
        return {
            "ara": 1.0,
            "midpoint_fraction": 0.5,
            "period": 1.0,
        }
    return info


def rolling_stats(arr, origin, window):
    start = max(0, origin - int(window) + 1)
    vals = np.asarray(arr[start : origin + 1], dtype=float)
    if len(vals) == 0:
        return 0.0, 0.0, 0.0
    mean = float(np.mean(vals))
    std = float(np.std(vals))
    slope = float(vals[-1] - vals[0]) / max(1, len(vals) - 1)
    return mean, std, slope


def add_signal_features(out, name, signal, origin):
    current = float(signal[origin])
    out[f"{name}_current"] = current
    out[f"{name}_abs"] = abs(current)
    out[f"{name}_sign"] = sign_nonzero(current, 0.0)
    for lag in LAGS:
        if origin - lag >= 0:
            out[f"{name}_lag{lag}"] = float(signal[origin - lag])
            out[f"{name}_delta{lag}"] = current - float(signal[origin - lag])
        else:
            out[f"{name}_lag{lag}"] = current
            out[f"{name}_delta{lag}"] = 0.0
    for window in WINDOWS:
        mean, std, slope = rolling_stats(signal, origin, window)
        out[f"{name}_mean{window}"] = mean
        out[f"{name}_std{window}"] = std
        out[f"{name}_slope{window}"] = slope


def raw_prior_features(state, origin, horizon):
    target = state["target"]
    signals = state["signals"]
    period_info = state["period_info"]
    out = {}

    for name, spec in state["templates"].items():
        if spec.get("ara_matched"):
            raw = ara_matched_raw_prediction(
                state["source_library"],
                target,
                state["target_crossings"],
                origin,
                horizon,
            )
        else:
            phase_signal = signals[spec["phase_signal"]]
            pinfo = period_info[spec["phase_signal"]]
            raw = template_raw_prediction(spec["template"], phase_signal, pinfo, origin, horizon)
        out[f"prior_{name}"] = finite(raw, 0.0)

    info = cycle_info_at(state["target_crossings"], origin)
    out["last_cycle_ara"] = finite(info["ara"], 1.0)
    out["last_cycle_midpoint_fraction"] = finite(info["midpoint_fraction"], 0.5)
    out["last_cycle_period"] = finite(info["period"], period_info["coupled"]["median_full"])
    out["origin_distance_from_balance"] = abs(float(target[origin]))
    return out


def build_feature_dict(state, origin, include_nasal=True):
    target = state["target"]
    signals = state["signals"]
    out = {}

    add_signal_features(out, "li", target, origin)
    add_signal_features(out, "nino", signals["nino_only"], origin)
    add_signal_features(out, "soi", signals["soi_only"], origin)

    out["nino_soi_sum"] = float(signals["nino_only"][origin] + signals["soi_only"][origin])
    out["nino_soi_gap"] = float(signals["nino_only"][origin] - signals["soi_only"][origin])
    out["nino_soi_product"] = float(signals["nino_only"][origin] * signals["soi_only"][origin])
    out["coupled_abs_denominator"] = float(abs(signals["nino_only"][origin]) + abs(signals["soi_only"][origin]) + EPS)

    month = int(state["dates"][origin][5:7])
    angle = 2.0 * math.pi * (month - 1) / 12.0
    out["season_sin"] = math.sin(angle)
    out["season_cos"] = math.cos(angle)

    for signal_name in ["coupled", "nino_only", "soi_only"]:
        pinfo = state["period_info"][signal_name]
        crossings = state["target_crossings"] if signal_name == "coupled" else state[f"{signal_name}_crossings"]
        phase = circular_phase_from_crossing(signals[signal_name], crossings, pinfo, origin)
        cinfo = cycle_info_at(crossings, origin)
        prefix = f"phase_{signal_name}"
        out[f"{prefix}_elapsed_frac_full"] = phase["elapsed_frac_full"]
        out[f"{prefix}_elapsed_frac_half"] = phase["elapsed_frac_half"]
        out[f"{prefix}_sin"] = phase["phase_sin"]
        out[f"{prefix}_cos"] = phase["phase_cos"]
        out[f"{prefix}_ara"] = finite(cinfo["ara"], 1.0)
        out[f"{prefix}_midpoint_fraction"] = finite(cinfo["midpoint_fraction"], 0.5)
        out[f"{prefix}_after_midpoint"] = 1.0 if phase["elapsed_frac_full"] > finite(cinfo["midpoint_fraction"], 0.5) else 0.0

    priors = raw_prior_features(state, origin, HORIZON)
    if not include_nasal:
        priors = {k: v for k, v in priors.items() if "nasal" not in k}
    out.update(priors)
    return {k: finite(v) for k, v in out.items()}


def future_state_targets(state, origin, horizon):
    target = state["target"]
    future = origin + horizon
    current = float(target[origin])
    actual = float(target[future])
    crossings = state["target_crossings"]
    phase = circular_phase_from_crossing(target, crossings, state["period_info"]["coupled"], future)
    cinfo = cycle_info_at(crossings, future)
    return {
        "future_sign": sign_nonzero(actual, 0.0),
        "future_turn": 1.0 if sign_nonzero(actual, 0.0) != sign_nonzero(current, 0.0) else 0.0,
        "future_delta_dir": 1.0 if actual - current > 0.0 else 0.0,
        "future_abs": abs(actual),
        "future_phase_sin": phase["phase_sin"],
        "future_phase_cos": phase["phase_cos"],
        "future_elapsed_frac_full": phase["elapsed_frac_full"],
        "future_ara": finite(cinfo["ara"], 1.0),
        "future_midpoint_fraction": finite(cinfo["midpoint_fraction"], 0.5),
        "future_after_midpoint": 1.0 if phase["elapsed_frac_full"] > finite(cinfo["midpoint_fraction"], 0.5) else 0.0,
    }


def matrix_from_dicts(dicts, keys):
    return np.asarray([[finite(row.get(key, 0.0)) for key in keys] for row in dicts], dtype=float)


def target_matrix(targets):
    names = list(targets[0].keys())
    return names, {name: np.asarray([row[name] for row in targets], dtype=float) for name in names}


def predicted_state_dicts(pred_by_name, n):
    rows = []
    for i in range(n):
        row = {}
        for name, values in pred_by_name.items():
            value = finite(values[i], 0.0)
            if name in {"future_turn", "future_delta_dir", "future_after_midpoint"}:
                value = min(1.0, max(0.0, value))
            elif name == "future_abs":
                value = max(0.0, value)
            elif name == "future_midpoint_fraction":
                value = min(0.98, max(0.02, value))
            elif name == "future_ara":
                value = min(6.0, max(0.05, value))
            row[f"pred_{name}"] = value
        rows.append(row)
    return rows


def decoder_feature_dict(state_row, current_feature_row):
    out = dict(state_row)
    out["state_value_reconstruction"] = sign_nonzero(state_row.get("pred_future_sign", 0.0), 0.0) * max(
        0.0, finite(state_row.get("pred_future_abs", 0.0))
    )
    out["current_li"] = current_feature_row.get("li_current", 0.0)
    out["current_abs_li"] = abs(current_feature_row.get("li_current", 0.0))
    out["prior_nasal_ara_matched_template"] = current_feature_row.get("prior_nasal_ara_matched_template", 0.0)
    out["prior_soi_only_template"] = current_feature_row.get("prior_soi_only_template", 0.0)
    out["prior_nino_only_template"] = current_feature_row.get("prior_nino_only_template", 0.0)
    return {k: finite(v) for k, v in out.items()}


def state_metrics(pred_state_rows, actual_state_rows):
    pred_sign = np.asarray([sign_nonzero(r["pred_future_sign"], 0.0) for r in pred_state_rows], dtype=float)
    actual_sign = np.asarray([r["future_sign"] for r in actual_state_rows], dtype=float)
    pred_turn = np.asarray([1.0 if r["pred_future_turn"] >= 0.5 else 0.0 for r in pred_state_rows], dtype=float)
    actual_turn = np.asarray([r["future_turn"] for r in actual_state_rows], dtype=float)
    pred_delta = np.asarray([1.0 if r["pred_future_delta_dir"] >= 0.5 else 0.0 for r in pred_state_rows], dtype=float)
    actual_delta = np.asarray([r["future_delta_dir"] for r in actual_state_rows], dtype=float)

    pred_phase = np.asarray(
        [
            math.atan2(r["pred_future_phase_sin"], r["pred_future_phase_cos"]) / (2.0 * math.pi) % 1.0
            for r in pred_state_rows
        ],
        dtype=float,
    )
    actual_phase = np.asarray(
        [
            math.atan2(r["future_phase_sin"], r["future_phase_cos"]) / (2.0 * math.pi) % 1.0
            for r in actual_state_rows
        ],
        dtype=float,
    )
    phase_gap = np.abs(((pred_phase - actual_phase + 0.5) % 1.0) - 0.5)

    pred_abs = np.asarray([r["pred_future_abs"] for r in pred_state_rows], dtype=float)
    actual_abs = np.asarray([r["future_abs"] for r in actual_state_rows], dtype=float)
    pred_ara = np.asarray([r["pred_future_ara"] for r in pred_state_rows], dtype=float)
    actual_ara = np.asarray([r["future_ara"] for r in actual_state_rows], dtype=float)
    return {
        "future_sign_accuracy": float(np.mean(pred_sign == actual_sign)),
        "future_turn_accuracy": float(np.mean(pred_turn == actual_turn)),
        "future_delta_direction_accuracy": float(np.mean(pred_delta == actual_delta)),
        "future_abs_mae": mae(pred_abs, actual_abs),
        "future_abs_corr": corr(pred_abs, actual_abs),
        "future_ara_mae": mae(pred_ara, actual_ara),
        "future_ara_corr": corr(pred_ara, actual_ara),
        "future_phase_mean_abs_cycle_error": float(np.mean(phase_gap)),
    }


def run_state_model(state, train_origins, test_origins, include_nasal=True, name="state_model"):
    feature_rows = {origin: build_feature_dict(state, origin, include_nasal=include_nasal) for origin in train_origins + test_origins}
    state_rows = {origin: future_state_targets(state, origin, HORIZON) for origin in train_origins + test_origins}

    feature_keys = sorted({key for origin in train_origins for key in feature_rows[origin].keys()})
    split_at = max(20, int(len(train_origins) * (1.0 - CALIB_FRACTION)))
    state_train = train_origins[:split_at]
    calib = train_origins[split_at:]

    x_state_train = matrix_from_dicts([feature_rows[o] for o in state_train], feature_keys)
    _, y_state_train = target_matrix([state_rows[o] for o in state_train])
    inner_models = train_multi_ridge(x_state_train, y_state_train, RIDGE_ALPHA_STATE)

    x_calib = matrix_from_dicts([feature_rows[o] for o in calib], feature_keys)
    pred_calib = predicted_state_dicts(predict_multi_ridge(inner_models, x_calib), len(calib))
    decoder_rows_calib = [decoder_feature_dict(pr, feature_rows[o]) for pr, o in zip(pred_calib, calib)]
    decoder_keys = sorted({key for row in decoder_rows_calib for key in row.keys()})
    x_decoder = matrix_from_dicts(decoder_rows_calib, decoder_keys)
    y_decoder = np.asarray([state["target"][o + HORIZON] for o in calib], dtype=float)
    decoder = train_ridge(x_decoder, y_decoder, RIDGE_ALPHA_DECODER)

    # Fit the state models on all pre-split training origins for the heldout run.
    x_train = matrix_from_dicts([feature_rows[o] for o in train_origins], feature_keys)
    _, y_train = target_matrix([state_rows[o] for o in train_origins])
    final_models = train_multi_ridge(x_train, y_train, RIDGE_ALPHA_STATE)

    x_test = matrix_from_dicts([feature_rows[o] for o in test_origins], feature_keys)
    pred_test_state = predicted_state_dicts(predict_multi_ridge(final_models, x_test), len(test_origins))
    decoder_rows_test = [decoder_feature_dict(pr, feature_rows[o]) for pr, o in zip(pred_test_state, test_origins)]
    x_test_decoder = matrix_from_dicts(decoder_rows_test, decoder_keys)
    pred = predict_ridge(decoder, x_test_decoder)

    actual = np.asarray([state["target"][o + HORIZON] for o in test_origins], dtype=float)
    current = np.asarray([state["target"][o] for o in test_origins], dtype=float)
    reconstruct = np.asarray([row["state_value_reconstruction"] for row in decoder_rows_test], dtype=float)

    return {
        "label": name,
        "include_nasal": bool(include_nasal),
        "n_state_train": int(len(state_train)),
        "n_calibration": int(len(calib)),
        "n_test": int(len(test_origins)),
        "n_features": int(len(feature_keys)),
        "n_decoder_features": int(len(decoder_keys)),
        "decoded_score": score_prediction(pred, actual, current),
        "state_reconstruction_score": score_prediction(reconstruct, actual, current),
        "state_metrics": state_metrics(pred_test_state, [state_rows[o] for o in test_origins]),
        "pred_values": [float(x) for x in pred],
        "reconstruct_values": [float(x) for x in reconstruct],
        "actual_values": [float(x) for x in actual],
        "current_values": [float(x) for x in current],
    }


def run_direct_model(state, train_origins, test_origins, include_nasal=True):
    train_features = [build_feature_dict(state, o, include_nasal=include_nasal) for o in train_origins]
    test_features = [build_feature_dict(state, o, include_nasal=include_nasal) for o in test_origins]
    keys = sorted({key for row in train_features for key in row.keys()})
    x_train = matrix_from_dicts(train_features, keys)
    y_train = np.asarray([state["target"][o + HORIZON] for o in train_origins], dtype=float)
    x_test = matrix_from_dicts(test_features, keys)
    actual = np.asarray([state["target"][o + HORIZON] for o in test_origins], dtype=float)
    current = np.asarray([state["target"][o] for o in test_origins], dtype=float)
    model = train_ridge(x_train, y_train, RIDGE_ALPHA_DIRECT)
    pred = predict_ridge(model, x_test)
    return {
        "n_features": int(len(keys)),
        "score": score_prediction(pred, actual, current),
        "pred_values": [float(x) for x in pred],
        "actual_values": [float(x) for x in actual],
        "current_values": [float(x) for x in current],
    }


def run_lag_model(state, train_origins, test_origins):
    signals = state["signals"]
    target = state["target"]

    def row(origin):
        out = {}
        for name, signal in [("li", target), ("nino", signals["nino_only"]), ("soi", signals["soi_only"])]:
            for lag in LAGS:
                out[f"{name}_lag{lag}"] = float(signal[origin - lag]) if origin - lag >= 0 else float(signal[origin])
            for window in WINDOWS:
                mean, std, slope = rolling_stats(signal, origin, window)
                out[f"{name}_mean{window}"] = mean
                out[f"{name}_std{window}"] = std
                out[f"{name}_slope{window}"] = slope
        return out

    train_features = [row(o) for o in train_origins]
    test_features = [row(o) for o in test_origins]
    keys = sorted({key for item in train_features for key in item.keys()})
    x_train = matrix_from_dicts(train_features, keys)
    y_train = np.asarray([target[o + HORIZON] for o in train_origins], dtype=float)
    x_test = matrix_from_dicts(test_features, keys)
    actual = np.asarray([target[o + HORIZON] for o in test_origins], dtype=float)
    current = np.asarray([target[o] for o in test_origins], dtype=float)
    model = train_ridge(x_train, y_train, RIDGE_ALPHA_DIRECT)
    pred = predict_ridge(model, x_test)
    return {
        "n_features": int(len(keys)),
        "score": score_prediction(pred, actual, current),
        "pred_values": [float(x) for x in pred],
        "actual_values": [float(x) for x in actual],
        "current_values": [float(x) for x in current],
    }


def run_old_ara_matched(state, train_origins, test_origins):
    target = state["target"]
    xtr, ytr, _ = build_ara_matched_rows(state["source_library"], target, state["target_crossings"], train_origins, HORIZON)
    xte, yte, kept = build_ara_matched_rows(state["source_library"], target, state["target_crossings"], test_origins, HORIZON)
    beta = ridge_fit(xtr, ytr)
    pred = ridge_predict(beta, xte)
    current = np.asarray([target[o] for o in kept], dtype=float)
    raw_pred = xte[:, 0]
    return {
        "n_train": int(len(ytr)),
        "n_test": int(len(yte)),
        "decoded_score": score_prediction(pred, yte, current),
        "raw_score": score_prediction(raw_pred, yte, current),
        "beta": [float(x) for x in beta],
        "pred_values": [float(x) for x in pred],
        "raw_pred_values": [float(x) for x in raw_pred],
        "actual_values": [float(x) for x in yte],
        "current_values": [float(x) for x in current],
    }


def prediction_vector(payload, kind="decoded"):
    if kind == "raw":
        return np.asarray(payload["raw_pred_values"], dtype=float)
    if kind == "reconstruct":
        return np.asarray(payload["reconstruct_values"], dtype=float)
    return np.asarray(payload["pred_values"], dtype=float)


def run_base_payloads(state, fit_origins, predict_origins):
    return {
        "old_nasal_ara_matched_template": run_old_ara_matched(state, fit_origins, predict_origins),
        "direct_full_current_variables": run_direct_model(state, fit_origins, predict_origins, include_nasal=True),
        "direct_local_current_variables": run_direct_model(state, fit_origins, predict_origins, include_nasal=False),
        "lag_only_ridge": run_lag_model(state, fit_origins, predict_origins),
        "future_state_full_decoder": run_state_model(
            state,
            fit_origins,
            predict_origins,
            include_nasal=True,
            name="future state decoder with nasal/ARA priors",
        ),
        "future_state_local_decoder": run_state_model(
            state,
            fit_origins,
            predict_origins,
            include_nasal=False,
            name="future state decoder with local variables only",
        ),
    }


def blend_feature_rows(payloads, current_values):
    vectors = {
        "old_ara_decoded": prediction_vector(payloads["old_nasal_ara_matched_template"]),
        "old_ara_raw": prediction_vector(payloads["old_nasal_ara_matched_template"], "raw"),
        "direct_full": prediction_vector(payloads["direct_full_current_variables"]),
        "direct_local": prediction_vector(payloads["direct_local_current_variables"]),
        "lag": prediction_vector(payloads["lag_only_ridge"]),
        "state_full": prediction_vector(payloads["future_state_full_decoder"]),
        "state_full_reconstruct": prediction_vector(payloads["future_state_full_decoder"], "reconstruct"),
        "state_local": prediction_vector(payloads["future_state_local_decoder"]),
        "state_local_reconstruct": prediction_vector(payloads["future_state_local_decoder"], "reconstruct"),
        "current": np.asarray(current_values, dtype=float),
    }
    keys = list(vectors.keys())
    n = len(current_values)
    return keys, np.column_stack([vectors[key][:n] for key in keys])


def run_stacked_blend(state, train_origins, test_origins):
    split_at = max(40, int(len(train_origins) * (1.0 - CALIB_FRACTION)))
    stage_train = train_origins[:split_at]
    calib = train_origins[split_at:]

    calib_payloads = run_base_payloads(state, stage_train, calib)
    test_payloads = run_base_payloads(state, train_origins, test_origins)

    calib_actual = np.asarray([state["target"][o + HORIZON] for o in calib], dtype=float)
    calib_current = np.asarray([state["target"][o] for o in calib], dtype=float)
    test_actual = np.asarray([state["target"][o + HORIZON] for o in test_origins], dtype=float)
    test_current = np.asarray([state["target"][o] for o in test_origins], dtype=float)

    keys, x_calib = blend_feature_rows(calib_payloads, calib_current)
    _, x_test = blend_feature_rows(test_payloads, test_current)
    model = train_ridge(x_calib, calib_actual, RIDGE_ALPHA_DECODER)
    pred = predict_ridge(model, x_test)

    return {
        "label": "inner-calibrated stack of template, lag, direct, and future-state predictions",
        "n_stage_train": int(len(stage_train)),
        "n_calibration": int(len(calib)),
        "n_test": int(len(test_origins)),
        "feature_keys": keys,
        "score": score_prediction(pred, test_actual, test_current),
        "pred_values": [float(x) for x in pred],
        "actual_values": [float(x) for x in test_actual],
        "current_values": [float(x) for x in test_current],
    }


def add_crossings(state):
    from ara_nasal_to_enso_prediction_test import zero_crossings

    state["nino_only_crossings"] = zero_crossings(state["signals"]["nino_only"])
    state["soi_only_crossings"] = zero_crossings(state["signals"]["soi_only"])


def best_by_corr(results):
    rows = []
    for name, payload in results["models"].items():
        score = payload.get("decoded_score") or payload.get("score")
        if score:
            rows.append((name, score.get("corr", -999.0), score.get("mae", float("inf"))))
    for name, score in results["baselines"].items():
        rows.append((name, score.get("corr", -999.0), score.get("mae", float("inf"))))
    return max(rows, key=lambda x: x[1])


def best_by_mae(results):
    rows = []
    for name, payload in results["models"].items():
        score = payload.get("decoded_score") or payload.get("score")
        if score:
            rows.append((name, score.get("mae", float("inf")), score.get("corr", -999.0)))
    for name, score in results["baselines"].items():
        rows.append((name, score.get("mae", float("inf")), score.get("corr", -999.0)))
    return min(rows, key=lambda x: x[1])


def main():
    print("Loading existing nasal/ENSO state...")
    state = load_templates_and_signals()
    add_crossings(state)

    split = state["split"]
    target = state["target"]
    train_origins = list(range(MIN_ORIGIN, split - HORIZON))
    test_origins = list(range(split, len(target) - HORIZON))
    actual_test = np.asarray([target[o + HORIZON] for o in test_origins], dtype=float)
    current_test = np.asarray([target[o] for o in test_origins], dtype=float)

    print(f"Train origins: {len(train_origins)}; test origins: {len(test_origins)}; split={state['dates'][split]}")

    baselines = {
        "persistence": score_prediction(current_test, actual_test, current_test),
    }
    x_train_current = np.asarray([[target[o]] for o in train_origins], dtype=float)
    y_train = np.asarray([target[o + HORIZON] for o in train_origins], dtype=float)
    beta_current = ridge_fit(x_train_current, y_train)
    ar_pred = ridge_predict(beta_current, np.asarray([[target[o]] for o in test_origins], dtype=float))
    baselines["ar_current"] = {
        **score_prediction(ar_pred, actual_test, current_test),
        "beta": [float(x) for x in beta_current],
    }

    models = {}
    print("Running old ARA/midpoint template baseline...")
    models["old_nasal_ara_matched_template"] = run_old_ara_matched(state, train_origins, test_origins)

    print("Running direct current-variable controls...")
    models["direct_full_current_variables"] = run_direct_model(state, train_origins, test_origins, include_nasal=True)
    models["direct_local_current_variables"] = run_direct_model(state, train_origins, test_origins, include_nasal=False)
    models["lag_only_ridge"] = run_lag_model(state, train_origins, test_origins)

    print("Running future-state geometry decoders...")
    models["future_state_full_decoder"] = run_state_model(
        state,
        train_origins,
        test_origins,
        include_nasal=True,
        name="future state decoder with nasal/ARA priors",
    )
    models["future_state_local_decoder"] = run_state_model(
        state,
        train_origins,
        test_origins,
        include_nasal=False,
        name="future state decoder with local variables only",
    )

    print("Running inner-calibrated stacked blend...")
    models["inner_calibrated_stacked_blend"] = run_stacked_blend(state, train_origins, test_origins)

    best_corr = best_by_corr({"baselines": baselines, "models": models})
    best_mae = best_by_mae({"baselines": baselines, "models": models})

    payload = {
        "date": "2026-05-23",
        "method": "Strict-causal 12-month ENSO future geometry-state predictor. Predicts future sign/turn/phase/ARA/magnitude first, then decodes heldout coupled LI.",
        "target": "ENSO coupled laterality index LI=(zNINO-zSOI)/(abs(zNINO)+abs(zSOI)), causal-smoothed as in nasal-to-ENSO test.",
        "horizon_months": HORIZON,
        "leakage_guard": [
            "NINO/SOI scaling and templates inherited from train-only nasal-to-ENSO loader.",
            "Training origins are before split; heldout origins are after split.",
            "Future-state decoder is calibrated on predicted states from an inner chronological train/calibration split.",
            "Heldout actual future states are used only for state-metric scoring, not for prediction.",
        ],
        "split": {
            "index": int(split),
            "date": state["dates"][split],
            "n_months": int(len(target)),
            "train_origins": int(len(train_origins)),
            "test_origins": int(len(test_origins)),
            "train_start": state["dates"][train_origins[0]],
            "test_end": state["dates"][test_origins[-1] + HORIZON],
        },
        "baselines": baselines,
        "models": models,
        "summary": {
            "best_corr_model": best_corr[0],
            "best_corr": float(best_corr[1]),
            "best_corr_mae": float(best_corr[2]),
            "best_mae_model": best_mae[0],
            "best_mae": float(best_mae[1]),
            "best_mae_corr": float(best_mae[2]),
            "persistence_mae": baselines["persistence"]["mae"],
            "persistence_corr": baselines["persistence"]["corr"],
        },
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(payload), indent=2), encoding="utf-8")
    OUT_JS.write_text("window.ARA_ENSO_12M_GEOMETRY_STATE_PREDICTOR = " + json.dumps(clean_for_json(payload)) + ";\n", encoding="utf-8")

    print("\n=== 12M GEOMETRY-STATE SUMMARY ===")
    for name, score in baselines.items():
        print(f"{name:36s} MAE={score['mae']:.3f} corr={score['corr']:+.3f} turn={score.get('turn_event_accuracy', 0):.3f}")
    for name, payload in models.items():
        score = payload.get("decoded_score") or payload.get("score")
        print(f"{name:36s} MAE={score['mae']:.3f} corr={score['corr']:+.3f} turn={score.get('turn_event_accuracy', 0):.3f}")
        if "state_metrics" in payload:
            sm = payload["state_metrics"]
            print(
                f"{'':36s} state sign={sm['future_sign_accuracy']:.3f} "
                f"turn={sm['future_turn_accuracy']:.3f} "
                f"abs_corr={sm['future_abs_corr']:+.3f} "
                f"phase_err={sm['future_phase_mean_abs_cycle_error']:.3f}"
            )
    print(f"Best corr: {best_corr[0]} corr={best_corr[1]:+.3f} MAE={best_corr[2]:.3f}")
    print(f"Best MAE : {best_mae[0]} MAE={best_mae[1]:.3f} corr={best_mae[2]:+.3f}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    main()
