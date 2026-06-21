"""
ara_enso_12m_boundary_distance_transfer_test.py

Strict-causal test for the boundary-distance transfer idea:

    locate source and target systems in rung/ARA/event coordinates
    measure rung distance and singularity-boundary count
    attenuate/flip by boundary crossings
    scale the lower-rung source event path to the target 12-month event
    decode the target coupled ENSO state

This is a follow-up to ara_enso_12m_feeder_amplitude_test.py. That test used
delayed lower-rung feeder energy. This one adds explicit source/target
locations, boundary counts, parity flips, and transferred event coordinates.
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
from ara_enso_12m_feeder_amplitude_test import (
    ALPHA_GRID,
    DELAY_BASES,
    HOME_PERIOD,
    HORIZON,
    LOWER_PERIODS,
    MIN_ORIGIN,
    build_old_shape_payload,
    fit_predict_feature_model,
    run_factorized_model,
    run_lag_model,
    scale_delay,
    select_factor_alpha,
)
from ara_enso_12m_geometry_state_predictor_test import (
    clean_for_json,
    finite,
    rolling_stats,
)
from ara_nasal_to_enso_prediction_test import (
    load_templates_and_signals,
    last_completed_cycle_info,
    score_prediction,
    sign_nonzero,
)


OUT_JSON = HERE / "ara_enso_12m_boundary_distance_transfer_result.json"
OUT_JS = HERE / "ara_enso_12m_boundary_distance_transfer_result.js"

PI_LEAK_ENERGY = (math.pi - 3.0) / math.pi
RIDGE_ALPHA = 8.0
EPS = 1e-9


def phase_gap(a, b):
    return abs(((float(a) - float(b) + 0.5) % 1.0) - 0.5)


def phase_alignment(a, b):
    return math.cos(2.0 * math.pi * phase_gap(a, b))


def phase_from_bp_value_slope(value, slope, amp):
    amp = max(float(amp), EPS)
    x = max(-1.0, min(1.0, float(value) / amp))
    y = max(-1.0, min(1.0, float(slope) / amp))
    return float((math.atan2(y, x) / (2.0 * math.pi)) % 1.0)


def local_ara_from_cycle(bp, period):
    p = max(4, int(round(period)))
    if len(bp) < p + 2:
        return 1.0
    seg = np.asarray(bp[-p:], dtype=float)
    peak = int(np.argmax(seg))
    trough = int(np.argmin(seg))
    if peak == trough:
        return 1.0
    if peak < trough:
        release = max(1, trough - peak)
        accumulate = max(1, p - release)
    else:
        accumulate = max(1, peak - trough)
        release = max(1, p - accumulate)
    return float(np.clip(release / accumulate, 0.2, 4.0))


def rung_state(signal, sample, period):
    p = max(2, int(round(period)))
    if sample < max(8, int(math.ceil(4.0 * period))):
        return {
            "value": 0.0,
            "slope": 0.0,
            "amp": 0.0,
            "energy": 0.0,
            "norm": 0.0,
            "phase": 0.0,
            "ara": 1.0,
            "rolling_std": 0.0,
            "rolling_slope": 0.0,
        }
    arr = np.asarray(signal[: sample + 1], dtype=float)
    bp = causal_bandpass(arr, float(period))
    value = float(bp[-1])
    prev = float(bp[-2]) if len(bp) > 1 else value
    slope = value - prev
    cycle = bp[-p:]
    amp = float((np.max(cycle) - np.min(cycle)) / 2.0)
    mean, std, rslope = rolling_stats(signal, sample, p)
    phase = phase_from_bp_value_slope(value, slope, amp)
    return {
        "value": value,
        "slope": slope,
        "amp": amp,
        "energy": amp * amp,
        "norm": value / (amp + EPS),
        "phase": phase,
        "ara": local_ara_from_cycle(bp, period),
        "rolling_std": std,
        "rolling_slope": rslope,
    }


def target_coordinate_state(state, origin, base):
    target = state["target"]
    cinfo = last_completed_cycle_info(state["target_crossings"], origin) or {
        "ara": 1.0,
        "midpoint_fraction": 0.5,
        "period": state["period_info"]["coupled"]["median_full"],
    }
    last_crossings = [c for c in state["target_crossings"] if c <= origin]
    last_cross = last_crossings[-1] if last_crossings else 0
    elapsed = float(origin - last_cross)
    period = max(2.0, finite(cinfo["period"], state["period_info"]["coupled"]["median_full"]))
    phase = (elapsed / period) % 1.0
    ara = max(0.05, finite(cinfo["ara"], 1.0))
    rung = math.log(HOME_PERIOD) / math.log(base)
    position = rung + ara / 2.0
    release_fraction = 1.0 / (1.0 + ara)
    return {
        "ara": ara,
        "rung": rung,
        "position": position,
        "phase": phase,
        "release_fraction": release_fraction,
        "current": float(target[origin]),
        "abs_current": abs(float(target[origin])),
        "sign": sign_nonzero(target[origin], 0.0),
    }


def feeder_sample_index(origin, horizon, period, base):
    target_idx = origin + horizon
    sample = int(math.floor(target_idx - scale_delay(period, base)))
    return sample if sample <= origin else None


def boundary_rows_for_origin(state, origin, carrier_raw, carrier_decoded, include_detail=False):
    signals = {
        "li": state["target"],
        "nino": state["signals"]["nino_only"],
        "soi": state["signals"]["soi_only"],
        "gap": state["signals"]["nino_only"] - state["signals"]["soi_only"],
        "sum": state["signals"]["nino_only"] + state["signals"]["soi_only"],
    }
    out = {
        "carrier_raw": finite(carrier_raw),
        "carrier_decoded": finite(carrier_decoded),
        "carrier_abs": abs(finite(carrier_decoded)),
        "origin_value": float(state["target"][origin]),
        "origin_abs": abs(float(state["target"][origin])),
    }

    for base_name, base in DELAY_BASES.items():
        target_state = target_coordinate_state(state, origin, base)
        out[f"{base_name}_target_ara"] = target_state["ara"]
        out[f"{base_name}_target_position"] = target_state["position"]
        out[f"{base_name}_target_phase_sin"] = math.sin(2.0 * math.pi * target_state["phase"])
        out[f"{base_name}_target_phase_cos"] = math.cos(2.0 * math.pi * target_state["phase"])

        total_weight = 0.0
        transfer_pressure = 0.0
        transfer_energy = 0.0
        transfer_slope = 0.0
        transfer_alignment = 0.0
        transfer_boundary = 0.0
        transfer_boundary_energy = 0.0
        transfer_singularity_proximity = 0.0
        transfer_phase_sin = 0.0
        transfer_phase_cos = 0.0

        for period in LOWER_PERIODS:
            sample = feeder_sample_index(origin, HORIZON, period, base)
            if sample is None or sample < 0:
                continue
            source_rung = math.log(period) / math.log(base)
            delay_weight = math.exp(-abs(scale_delay(period, base) - HORIZON) / max(HORIZON, 1.0))
            for signal_name, signal in signals.items():
                src = rung_state(signal, sample, period)
                source_position = source_rung + src["ara"] / 2.0
                distance = target_state["position"] - source_position
                boundary_count = int(math.ceil(abs(distance)))
                attenuation = (1.0 - PI_LEAK_ENERGY) ** boundary_count
                parity = -1.0 if boundary_count % 2 else 1.0
                equivalent_phase = (src["phase"] + 0.5 * (boundary_count % 2)) % 1.0
                align = phase_alignment(equivalent_phase, target_state["phase"])
                release_gap = min(
                    phase_gap(equivalent_phase, 0.0),
                    phase_gap(equivalent_phase, target_state["release_fraction"]),
                    phase_gap(equivalent_phase, 0.5),
                )
                singularity_prox = math.exp(-release_gap / 0.08)
                energy_weight = math.sqrt(max(src["energy"], 0.0)) + 0.05 * abs(src["norm"])
                weight = delay_weight * attenuation * (0.1 + energy_weight)

                total_weight += weight
                transfer_pressure += weight * parity * src["norm"]
                transfer_energy += weight * src["energy"]
                transfer_slope += weight * parity * src["slope"]
                transfer_alignment += weight * align
                transfer_boundary += weight * boundary_count
                transfer_boundary_energy += weight * src["energy"] / max(1.0, boundary_count)
                transfer_singularity_proximity += weight * singularity_prox
                transfer_phase_sin += weight * math.sin(2.0 * math.pi * equivalent_phase)
                transfer_phase_cos += weight * math.cos(2.0 * math.pi * equivalent_phase)

                if include_detail:
                    prefix = f"{base_name}_{signal_name}_p{int(period)}"
                    out[f"{prefix}_sample_lag"] = float(origin - sample)
                    out[f"{prefix}_distance"] = distance
                    out[f"{prefix}_boundaries"] = float(boundary_count)
                    out[f"{prefix}_attenuation"] = attenuation
                    out[f"{prefix}_equiv_phase_sin"] = math.sin(2.0 * math.pi * equivalent_phase)
                    out[f"{prefix}_equiv_phase_cos"] = math.cos(2.0 * math.pi * equivalent_phase)
                    out[f"{prefix}_alignment"] = align
                    out[f"{prefix}_singularity_prox"] = singularity_prox
                    out[f"{prefix}_pressure"] = parity * src["norm"] * attenuation
                    out[f"{prefix}_energy"] = src["energy"] * attenuation

        denom = total_weight if total_weight > EPS else 1.0
        out[f"{base_name}_boundary_total_weight"] = total_weight
        out[f"{base_name}_boundary_pressure"] = transfer_pressure / denom
        out[f"{base_name}_boundary_energy"] = transfer_energy / denom
        out[f"{base_name}_boundary_slope"] = transfer_slope / denom
        out[f"{base_name}_boundary_alignment"] = transfer_alignment / denom
        out[f"{base_name}_boundary_count"] = transfer_boundary / denom
        out[f"{base_name}_boundary_energy_per_boundary"] = transfer_boundary_energy / denom
        out[f"{base_name}_boundary_singularity_proximity"] = transfer_singularity_proximity / denom
        out[f"{base_name}_boundary_phase_sin"] = transfer_phase_sin / denom
        out[f"{base_name}_boundary_phase_cos"] = transfer_phase_cos / denom
        out[f"{base_name}_carrier_x_pressure"] = finite(carrier_decoded) * out[f"{base_name}_boundary_pressure"]
        out[f"{base_name}_carrier_x_energy"] = finite(carrier_decoded) * out[f"{base_name}_boundary_energy"]
        out[f"{base_name}_carrier_x_alignment"] = finite(carrier_decoded) * out[f"{base_name}_boundary_alignment"]

    return {key: finite(value) for key, value in out.items()}


def run_shape_boundary_deterministic(rows):
    preds = []
    for row in rows:
        pressure = 0.5 * (row.get("base2_boundary_pressure", 0.0) + row.get("phi_boundary_pressure", 0.0))
        energy = max(0.0, 0.5 * (row.get("base2_boundary_energy", 0.0) + row.get("phi_boundary_energy", 0.0)))
        align = 0.5 * (row.get("base2_boundary_alignment", 0.0) + row.get("phi_boundary_alignment", 0.0))
        sign = sign_nonzero(row.get("carrier_decoded", 0.0) + 0.35 * pressure, row.get("origin_value", 0.0))
        amp = abs(row.get("carrier_decoded", 0.0)) * (0.65 + 0.25 * math.tanh(energy) + 0.10 * max(0.0, align))
        preds.append(sign * amp)
    return np.asarray(preds, dtype=float)


def select_alpha(rows, y_train, current_train, metric="mae"):
    return select_factor_alpha(rows, y_train, current_train, metric=metric)


def run_model_set(train_rows, y_train, current_train, test_rows, y_test, current_test):
    direct_pred, direct_keys = fit_predict_feature_model(train_rows, y_train, test_rows, alpha=RIDGE_ALPHA)
    alpha_mae, alpha_mae_score, alpha_mae_candidates = select_alpha(train_rows, y_train, current_train, metric="mae")
    alpha_corr, alpha_corr_score, alpha_corr_candidates = select_alpha(train_rows, y_train, current_train, metric="corr")
    factor_mae_pred, factor_mae_meta = run_factorized_model(train_rows, y_train, test_rows, alpha=alpha_mae)
    factor_corr_pred, factor_corr_meta = run_factorized_model(train_rows, y_train, test_rows, alpha=alpha_corr)
    deterministic_pred = run_shape_boundary_deterministic(test_rows)
    return {
        "boundary_direct_value_control": {
            "n_features": int(len(direct_keys)),
            "score": score_prediction(direct_pred, y_test, current_test),
        },
        "boundary_sign_amp_alpha_mae_selected": {
            **factor_mae_meta,
            "inner_selected_alpha": alpha_mae,
            "inner_selection_score": alpha_mae_score,
            "inner_candidates": alpha_mae_candidates,
            "score": score_prediction(factor_mae_pred, y_test, current_test),
        },
        "boundary_sign_amp_alpha_corr_selected": {
            **factor_corr_meta,
            "inner_selected_alpha": alpha_corr,
            "inner_selection_score": alpha_corr_score,
            "inner_candidates": alpha_corr_candidates,
            "score": score_prediction(factor_corr_pred, y_test, current_test),
        },
        "boundary_deterministic_shape_scale": {
            "score": score_prediction(deterministic_pred, y_test, current_test),
        },
    }


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
    print("Building old ARA/midpoint shape carriers...")
    old_train, old_test = build_old_shape_payload(state, train_origins, test_origins)
    train_raw = np.asarray(old_train["raw_pred_values"], dtype=float)
    train_decoded = np.asarray(old_train["pred_values"], dtype=float)
    test_raw = np.asarray(old_test["raw_pred_values"], dtype=float)
    test_decoded = np.asarray(old_test["pred_values"], dtype=float)

    print("Building aggregate boundary-coordinate rows...")
    train_rows_agg = [
        boundary_rows_for_origin(state, o, r, d, include_detail=False)
        for o, r, d in zip(train_origins, train_raw, train_decoded)
    ]
    test_rows_agg = [
        boundary_rows_for_origin(state, o, r, d, include_detail=False)
        for o, r, d in zip(test_origins, test_raw, test_decoded)
    ]

    print("Building detailed boundary-coordinate rows...")
    train_rows_detail = [
        boundary_rows_for_origin(state, o, r, d, include_detail=True)
        for o, r, d in zip(train_origins, train_raw, train_decoded)
    ]
    test_rows_detail = [
        boundary_rows_for_origin(state, o, r, d, include_detail=True)
        for o, r, d in zip(test_origins, test_raw, test_decoded)
    ]

    baselines = {
        "persistence": score_prediction(current_test, y_test, current_test),
        "old_nasal_ara_matched_template": old_test["decoded_score"],
        "old_nasal_ara_matched_raw": old_test["raw_score"],
        "lag_only_ridge": run_lag_model(state, train_origins, test_origins)["score"],
    }
    models = {}
    for prefix, train_rows, test_rows in [
        ("aggregate", train_rows_agg, test_rows_agg),
        ("detail", train_rows_detail, test_rows_detail),
    ]:
        group = run_model_set(train_rows, y_train, current_train, test_rows, y_test, current_test)
        for name, payload in group.items():
            models[f"{prefix}_{name}"] = payload

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
        "method": "Strict-causal 12-month ENSO boundary-distance transfer test. Lower-rung source systems are mapped to target event coordinates with rung distance, boundary count, parity flip, and pi-leak attenuation.",
        "horizon_months": HORIZON,
        "home_period_months": HOME_PERIOD,
        "lower_periods_months": LOWER_PERIODS,
        "pi_leak_energy": PI_LEAK_ENERGY,
        "leakage_guard": [
            "NINO/SOI scaling and old ARA/midpoint shape carrier inherit train-only loader.",
            "Source feeder sample indices are never later than forecast origin.",
            "Causal bandpass state at feeder sample uses only data through that sample.",
            "Ridge alpha is selected only on an inner pre-split calibration slice where used.",
            "Heldout origins are after 2003-07-01.",
        ],
        "boundary_rule": {
            "source_position": "log(source_period)/log(base) + source_ara/2",
            "target_position": "log(home_period)/log(base) + target_ara/2",
            "boundary_count": "ceil(abs(target_position-source_position))",
            "attenuation": "(1 - pi_leak_energy) ** boundary_count",
            "phase_parity": "equivalent_phase = source_phase + 0.5*(boundary_count % 2)",
        },
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
    OUT_JS.write_text("window.ARA_ENSO_12M_BOUNDARY_DISTANCE_TRANSFER = " + json.dumps(clean_for_json(payload)) + ";\n", encoding="utf-8")

    print("\n=== 12M BOUNDARY-DISTANCE TRANSFER SUMMARY ===")
    for name, score in baselines.items():
        print(f"{name:46s} MAE={score['mae']:.3f} corr={score['corr']:+.3f} turn={score.get('turn_event_accuracy', 0):.3f}")
    for name, payload in models.items():
        score = payload["score"]
        print(f"{name:46s} MAE={score['mae']:.3f} corr={score['corr']:+.3f} turn={score.get('turn_event_accuracy', 0):.3f}")
    print(f"Best corr: {best_corr[0]} corr={best_corr[2]:+.3f} MAE={best_corr[1]:.3f}")
    print(f"Best MAE : {best_mae[0]} MAE={best_mae[1]:.3f} corr={best_mae[2]:+.3f}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    main()
