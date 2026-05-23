"""
ara_causal_flow_prediction_test.py

Causal test for retroactively inferred ARA geometry flow.

The previous retroactive diagnostic used actual future geometry to infer:

    alpha_natural: future ~= current + alpha * (natural_phase_advance - current)

This script turns that into a forecast test:

  - At origin t and horizon h, train alpha only on anchors s where s+h<t.
  - Predict alpha from current ARA geometry only.
  - Plug predicted alpha into several forward geometry formulas.
  - Decode projected geometry with a decoder trained only on geometry anchors a<t.

This asks whether flow is reusable/predictable, and whether ARA geometry can
provide the missing forward transport amount.
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

from ara_gear_coupled_transition_test import gear_event_ordered_cascade_decode_features
from ara_geometry_state_transition_test import (
    ORIGIN_STRIDE,
    build_snapshot_from_series,
    decode_state_features,
    event_ordered_cascade_decode_features,
    fit_ridge_model,
    natural_advance_decode_features,
    predict_ridge_model,
    raw_series_dict,
    sanitize_predicted_state_features,
    transition_features,
)
from ara_geometry_transport_test import (
    BASE,
    HORIZONS,
    HOME_PERIOD,
    MIN_TRAIN,
    RUNG_KS,
    START_YEAR,
    clean_for_json,
    fit_predict_ridge,
    lag_feature_dict,
    load_enso_frame,
    score_points,
)
from ara_shape_kernel_test import PHI, release_fraction


MODEL_KEYS = [
    "current_decoder",
    "natural_advance_decoder",
    "phi_flow_natural_decoder",
    "mean_flow_natural_decoder",
    "predicted_flow_natural_decoder",
    "predicted_flow_sync_direction_decoder",
    "predicted_flow_gear_direction_decoder",
    "predicted_sync_residual_decoder",
    "predicted_gear_residual_decoder",
    "lag_ridge",
]
ORACLE_KEY = "oracle_actual_future_geometry_decoder"


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def active_period(subsystem, fallback=HOME_PERIOD):
    rungs = subsystem.get("rungs", [])
    if not rungs:
        return float(fallback)
    weights = [max(0.0, finite(rung.get("occupancy", 0.0))) for rung in rungs]
    total = sum(weights)
    if total <= 1e-12:
        return float(fallback)
    return float(sum(weight * finite(rung.get("period", fallback), fallback) for weight, rung in zip(weights, rungs)) / total)


def add_flow_summary_features(features, snapshot, horizon):
    out = dict(features)
    center_aras = []
    active_periods = []
    release_fracs = []
    total_energy = 0.0
    for name, subsystem in snapshot.items():
        prefix = name.lower()
        period = active_period(subsystem)
        phase = float(horizon) / max(period, 1e-12)
        release = release_fraction(subsystem["center_ara"])
        center_aras.append(float(subsystem["center_ara"]))
        active_periods.append(period)
        release_fracs.append(release)
        total_energy += max(0.0, float(subsystem["total_energy"]))
        out[f"{prefix}_active_period"] = period
        out[f"{prefix}_horizon_over_active_period"] = phase
        out[f"{prefix}_meta_phase_sin"] = math.sin(2.0 * math.pi * phase)
        out[f"{prefix}_meta_phase_cos"] = math.cos(2.0 * math.pi * phase)
        out[f"{prefix}_release_fraction"] = release
        out[f"{prefix}_accumulate_fraction"] = 1.0 - release

    out.update(
        {
            "flow_phi_formula": 1.0 - PHI ** (-float(horizon) / HOME_PERIOD),
            "center_ara_mean": float(np.mean(center_aras)) if center_aras else 0.0,
            "center_ara_std": float(np.std(center_aras)) if center_aras else 0.0,
            "active_period_mean": float(np.mean(active_periods)) if active_periods else HOME_PERIOD,
            "active_period_std": float(np.std(active_periods)) if active_periods else 0.0,
            "release_fraction_mean": float(np.mean(release_fracs)) if release_fracs else 0.5,
            "release_fraction_std": float(np.std(release_fracs)) if release_fracs else 0.0,
            "total_energy_sum": total_energy,
            "log_total_energy_sum": math.log1p(total_energy),
        }
    )
    return {key: finite(value) for key, value in out.items()}


def build_scale(decode_cache, anchors, keys):
    scale = {}
    for key in keys:
        vals = np.asarray([finite(decode_cache[a].get(key, 0.0)) for a in anchors], dtype=float)
        std = float(np.std(vals))
        scale[key] = std if std > 1e-9 else 1.0
    return scale


def vectorize(features, keys, scale):
    return np.asarray([finite(features.get(key, 0.0)) / scale[key] for key in keys], dtype=float)


def best_scalar_flow(start, direction, actual):
    denom = float(np.dot(direction, direction))
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(actual - start, direction) / denom)


def clip_flow(value, lo=0.0, hi=1.25):
    return max(lo, min(hi, finite(value)))


def clip_residual_flow(value):
    return max(-1.0, min(2.0, finite(value)))


def blend_dict(start, end, alpha, keys):
    alpha = finite(alpha)
    return sanitize_predicted_state_features(
        {
            key: finite(start.get(key, 0.0)) + alpha * (finite(end.get(key, 0.0)) - finite(start.get(key, 0.0)))
            for key in keys
        }
    )


def residual_blend_dict(start, residual_target, beta, keys):
    beta = finite(beta)
    return sanitize_predicted_state_features(
        {
            key: finite(start.get(key, 0.0))
            + beta * (finite(residual_target.get(key, 0.0)) - finite(start.get(key, 0.0)))
            for key in keys
        }
    )


def point(origin_date, target_date, pred, actual, persistence, extras=None):
    out = {
        "origin": origin_date,
        "date": target_date,
        "pred": float(pred),
        "actual": float(actual),
        "persistence": float(persistence),
    }
    if extras:
        out.update(extras)
    return out


def format_score(score):
    if "mae" not in score:
        return "n/a"
    return (
        f"MAE={score['mae']:.4f} vs pers={score['persistence_mae']:.4f} "
        f"lift={score['mae_lift_vs_persistence']:+.4f} corr={score['corr']:+.3f} "
        f"dir={score['direction']:.3f}"
    )


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = raw_series_dict(frame)
    nino = frame["NINO"].values.astype(float)
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01")))
    test_start = max(start_idx + 1, min_anchor + MIN_TRAIN + max_h + 1)
    last_origin = n - max_h
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA causal flow-prediction ENSO test", flush=True)
    print("=" * 104, flush=True)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}", flush=True)
    print("strict guards: alpha train s+h<t; decoder train a<t; lag train s+h<t", flush=True)
    print(
        f"test origins start: {dates[test_start - 1].date()}  "
        f"longest-horizon last origin: {dates[last_origin - 1].date()}  "
        f"origin_stride={ORIGIN_STRIDE} months",
        flush=True,
    )
    print(flush=True)

    snapshots = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        snapshots[anchor] = build_snapshot_from_series(series, anchor)
        if i % 100 == 0:
            print(f"  snapshots {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  snapshots {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(flush=True)

    decode_cache = {anchor: decode_state_features(snapshots[anchor]) for anchor in all_anchors}
    keys = sorted(decode_cache[min_anchor].keys())
    projection_cache = {h: {} for h in HORIZONS}
    flow_feature_cache = {h: {} for h in HORIZONS}
    for h in HORIZONS:
        for anchor in all_anchors:
            snap = snapshots[anchor]
            projection_cache[h][anchor] = {
                "current": decode_cache[anchor],
                "natural": natural_advance_decode_features(snap, h),
                "sync": event_ordered_cascade_decode_features(snap, h),
                "gear": gear_event_ordered_cascade_decode_features(snap, h),
            }
            flow_feature_cache[h][anchor] = add_flow_summary_features(
                transition_features(snap, h, include_current=False),
                snap,
                h,
            )

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}
    flow_predictions = {h: [] for h in HORIZONS}

    for h in HORIZONS:
        for origin in range(test_start, n - h + 1, ORIGIN_STRIDE):
            target_anchor = origin + h
            train_transition = [s for s in all_anchors if s + h < origin]
            train_decoder = [a for a in all_anchors if a < origin]
            if len(train_transition) < MIN_TRAIN or len(train_decoder) < MIN_TRAIN:
                continue

            scale = build_scale(decode_cache, train_decoder, keys)

            alpha_targets = []
            sync_targets = []
            gear_targets = []
            for s in train_transition:
                proj = projection_cache[h][s]
                current = vectorize(proj["current"], keys, scale)
                future = vectorize(decode_cache[s + h], keys, scale)
                natural = vectorize(proj["natural"], keys, scale)
                sync = vectorize(proj["sync"], keys, scale)
                gear = vectorize(proj["gear"], keys, scale)
                alpha_targets.append(best_scalar_flow(current, natural - current, future))
                sync_targets.append(best_scalar_flow(natural, sync - natural, future))
                gear_targets.append(best_scalar_flow(natural, gear - natural, future))

            alpha_raw, _, _ = fit_predict_ridge(
                [flow_feature_cache[h][s] for s in train_transition],
                alpha_targets,
                flow_feature_cache[h][origin],
            )
            sync_raw, _, _ = fit_predict_ridge(
                [flow_feature_cache[h][s] for s in train_transition],
                sync_targets,
                flow_feature_cache[h][origin],
            )
            gear_raw, _, _ = fit_predict_ridge(
                [flow_feature_cache[h][s] for s in train_transition],
                gear_targets,
                flow_feature_cache[h][origin],
            )

            alpha_pred = clip_flow(alpha_raw)
            alpha_mean = clip_flow(float(np.mean(alpha_targets)))
            sync_pred = clip_residual_flow(sync_raw)
            gear_pred = clip_residual_flow(gear_raw)
            phi_flow = clip_flow(1.0 - PHI ** (-float(h) / HOME_PERIOD))

            actual = float(nino[target_anchor - 1])
            persistence = float(nino[origin - 1])
            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")

            decoder_model = fit_ridge_model(
                [decode_cache[a] for a in train_decoder],
                [float(nino[a - 1]) for a in train_decoder],
            )

            proj = projection_cache[h][origin]
            projected = {
                "current_decoder": proj["current"],
                "natural_advance_decoder": proj["natural"],
                "phi_flow_natural_decoder": blend_dict(proj["current"], proj["natural"], phi_flow, keys),
                "mean_flow_natural_decoder": blend_dict(proj["current"], proj["natural"], alpha_mean, keys),
                "predicted_flow_natural_decoder": blend_dict(proj["current"], proj["natural"], alpha_pred, keys),
                "predicted_flow_sync_direction_decoder": blend_dict(proj["current"], proj["sync"], alpha_pred, keys),
                "predicted_flow_gear_direction_decoder": blend_dict(proj["current"], proj["gear"], alpha_pred, keys),
                "predicted_sync_residual_decoder": residual_blend_dict(proj["natural"], proj["sync"], sync_pred, keys),
                "predicted_gear_residual_decoder": residual_blend_dict(proj["natural"], proj["gear"], gear_pred, keys),
            }

            extras = {
                "alpha_pred_raw": float(alpha_raw),
                "alpha_pred": float(alpha_pred),
                "alpha_mean": float(alpha_mean),
                "sync_residual_pred": float(sync_pred),
                "gear_residual_pred": float(gear_pred),
            }
            flow_predictions[h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    "alpha_pred_raw": float(alpha_raw),
                    "alpha_pred": float(alpha_pred),
                    "alpha_mean": float(alpha_mean),
                    "alpha_train_mean": float(np.mean(alpha_targets)),
                    "alpha_train_std": float(np.std(alpha_targets)),
                    "sync_residual_pred_raw": float(sync_raw),
                    "gear_residual_pred_raw": float(gear_raw),
                }
            )

            for model, features in projected.items():
                pred = float(predict_ridge_model(decoder_model, features)[0])
                all_points[model][h].append(point(origin_date, target_date, pred, actual, persistence, extras))

            train_y_delta = [float(nino[s + h - 1] - nino[s - 1]) for s in train_transition]
            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(nino, s) for s in train_transition],
                train_y_delta,
                lag_feature_dict(nino, origin),
            )
            all_points["lag_ridge"][h].append(
                point(origin_date, target_date, persistence + lag_delta, actual, persistence)
            )

            oracle_pred = float(predict_ridge_model(decoder_model, decode_cache[target_anchor])[0])
            all_points[ORACLE_KEY][h].append(point(origin_date, target_date, oracle_pred, actual, persistence))

        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:40s} {format_score(score_points(all_points[model][h]))}")
        print(f"  {ORACLE_KEY:40s} {format_score(score_points(all_points[ORACLE_KEY][h]))}  diagnostic")
        best = min(MODEL_KEYS, key=lambda m: score_points(all_points[m][h]).get("mae", float("inf")))
        print(f"  best forecast: {best}")
        print()

    scores = {model: {h: score_points(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}
    winners = {str(h): min(MODEL_KEYS, key=lambda m: scores[m][h].get("mae", float("inf"))) for h in HORIZONS}
    flow_summary = {}
    for h in HORIZONS:
        rows = flow_predictions[h]
        flow_summary[str(h)] = {
            key: {
                "mean": float(np.mean([row[key] for row in rows])) if rows else None,
                "std": float(np.std([row[key] for row in rows])) if rows else None,
            }
            for key in ["alpha_pred", "alpha_mean", "sync_residual_pred_raw", "gear_residual_pred_raw"]
        }

    out = {
        "date": "2026-05-23",
        "method": "strict-causal ARA flow prediction ENSO test",
        "leakage_guard": "At origin t, alpha targets train only on s+h<t, decoder trains only on a<t, and lag baseline trains only on s+h<t.",
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "horizons_months": HORIZONS,
        "rungs_k": RUNG_KS,
        "min_train_examples": MIN_TRAIN,
        "origin_stride_months": ORIGIN_STRIDE,
        "models": {
            "current_decoder": "Decode current geometry with causal decoder.",
            "natural_advance_decoder": "Natural phase advance with full alpha=1.",
            "phi_flow_natural_decoder": "Current->natural blend using old phi-flow formula.",
            "mean_flow_natural_decoder": "Current->natural blend using causal training-window mean retro-flow.",
            "predicted_flow_natural_decoder": "Current->natural blend using ridge-predicted alpha from current ARA geometry.",
            "predicted_flow_sync_direction_decoder": "Current->sync-cascade blend using the same predicted natural-flow alpha.",
            "predicted_flow_gear_direction_decoder": "Current->gear-cascade blend using the same predicted natural-flow alpha.",
            "predicted_sync_residual_decoder": "Natural geometry plus predicted sync-event residual flow.",
            "predicted_gear_residual_decoder": "Natural geometry plus predicted gear-event residual flow.",
            "lag_ridge": "Control: causal target lags and slopes.",
            ORACLE_KEY: "Diagnostic only: decode actual future geometry.",
        },
        "scores": scores,
        "winners": winners,
        "flow_summary": flow_summary,
        "flow_predictions": flow_predictions,
        "points": all_points,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    out_path = HERE / "ara_causal_flow_prediction_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_CAUSAL_FLOW_PREDICTION = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
