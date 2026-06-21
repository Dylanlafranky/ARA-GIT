"""
ara_causal_friction_prediction_test.py

Causal test for the temporal-friction version of ARA natural flow.

Previous diagnostics found retroactive natural-flow alpha around phi-1, but
direct alpha prediction was weak. This test learns temporal friction instead:

    flow = ARA / (ARA + temporal_friction)

At origin t and horizon h:
  - friction targets are inferred only from completed past windows s+h<t
  - the decoder trains only on geometry anchors a<t
  - current origin features never use future geometry

Diagnostic oracle decodes actual future geometry and is not a forecast.
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

from ara_causal_flow_prediction_test import (
    add_flow_summary_features,
    blend_dict,
    build_scale,
    point,
    vectorize,
)
from ara_geometry_state_transition_test import (
    ORIGIN_STRIDE,
    build_snapshot_from_series,
    decode_state_features,
    fit_ridge_model,
    natural_advance_decode_features,
    predict_ridge_model,
    raw_series_dict,
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
from ara_retroactive_flow_test import best_scalar_flow
from ara_shape_kernel_test import PHI


MODEL_KEYS = [
    "current_decoder",
    "natural_advance_decoder",
    "phi_flow_natural_decoder",
    "friction1_target_ara_decoder",
    "friction1_triad_mean_ara_decoder",
    "mean_friction_target_ara_decoder",
    "mean_friction_triad_mean_ara_decoder",
    "predicted_friction_target_ara_decoder",
    "predicted_friction_triad_mean_ara_decoder",
    "predicted_friction_weighted_ara_decoder",
    "predicted_flow_alpha_decoder",
    "lag_ridge",
]
ORACLE_KEY = "oracle_actual_future_geometry_decoder"
FRICTION_MIN = 0.05
FRICTION_MAX = 3.0
FLOW_FOR_FRICTION_MIN = 0.02
FLOW_FOR_FRICTION_MAX = 0.98


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def clip(value, lo, hi):
    return max(lo, min(hi, finite(value)))


def triad_mean_ara(snapshot):
    return float(np.mean([finite(subsystem["center_ara"], 1.0) for subsystem in snapshot.values()]))


def triad_weighted_ara(snapshot):
    weights = np.asarray([max(0.0, finite(subsystem["total_energy"], 0.0)) for subsystem in snapshot.values()], dtype=float)
    aras = np.asarray([finite(subsystem["center_ara"], 1.0) for subsystem in snapshot.values()], dtype=float)
    if float(weights.sum()) <= 1e-12:
        return float(np.mean(aras))
    return float(np.dot(weights / weights.sum(), aras))


def ara_values(snapshot):
    return {
        "target": finite(snapshot["NINO"]["center_ara"], 1.0),
        "mean": triad_mean_ara(snapshot),
        "weighted": triad_weighted_ara(snapshot),
    }


def flow_from_friction(ara, friction):
    ara = max(1e-12, finite(ara, 1.0))
    friction = clip(friction, FRICTION_MIN, FRICTION_MAX)
    return float(ara / (ara + friction))


def friction_from_flow(ara, flow):
    ara = max(1e-12, finite(ara, 1.0))
    flow = clip(flow, FLOW_FOR_FRICTION_MIN, FLOW_FOR_FRICTION_MAX)
    return float(ara * (1.0 - flow) / flow)


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

    print("ARA causal temporal-friction ENSO test", flush=True)
    print("=" * 104, flush=True)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}", flush=True)
    print("flow = ARA / (ARA + friction); friction targets train only on completed past windows", flush=True)
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
    ara_cache = {}
    for anchor in all_anchors:
        ara_cache[anchor] = ara_values(snapshots[anchor])
    for h in HORIZONS:
        for anchor in all_anchors:
            snap = snapshots[anchor]
            projection_cache[h][anchor] = {
                "current": decode_cache[anchor],
                "natural": natural_advance_decode_features(snap, h),
            }
            flow_feature_cache[h][anchor] = add_flow_summary_features(
                transition_features(snap, h, include_current=False),
                snap,
                h,
            )

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}
    friction_predictions = {h: [] for h in HORIZONS}

    for h in HORIZONS:
        for origin in range(test_start, n - h + 1, ORIGIN_STRIDE):
            target_anchor = origin + h
            train_transition = [s for s in all_anchors if s + h < origin]
            train_decoder = [a for a in all_anchors if a < origin]
            if len(train_transition) < MIN_TRAIN or len(train_decoder) < MIN_TRAIN:
                continue

            scale = build_scale(decode_cache, train_decoder, keys)
            alpha_targets = []
            friction_targets = {"target": [], "mean": [], "weighted": []}
            for s in train_transition:
                proj = projection_cache[h][s]
                current = vectorize(proj["current"], keys, scale)
                future = vectorize(decode_cache[s + h], keys, scale)
                natural = vectorize(proj["natural"], keys, scale)
                alpha = best_scalar_flow(current, natural - current, future)
                alpha_targets.append(alpha)
                for ara_key, ara in ara_cache[s].items():
                    friction_targets[ara_key].append(friction_from_flow(ara, alpha))

            alpha_raw, _, _ = fit_predict_ridge(
                [flow_feature_cache[h][s] for s in train_transition],
                alpha_targets,
                flow_feature_cache[h][origin],
            )
            friction_raw = {}
            friction_pred = {}
            friction_mean = {}
            for ara_key in ["target", "mean", "weighted"]:
                pred, _, _ = fit_predict_ridge(
                    [flow_feature_cache[h][s] for s in train_transition],
                    friction_targets[ara_key],
                    flow_feature_cache[h][origin],
                )
                friction_raw[ara_key] = float(pred)
                friction_pred[ara_key] = clip(pred, FRICTION_MIN, FRICTION_MAX)
                friction_mean[ara_key] = clip(float(np.mean(friction_targets[ara_key])), FRICTION_MIN, FRICTION_MAX)

            current_ara = ara_cache[origin]
            alpha_pred = clip(alpha_raw, 0.0, 1.25)
            phi_flow = clip(1.0 - PHI ** (-float(h) / HOME_PERIOD), 0.0, 1.25)

            flow_values = {
                "phi": phi_flow,
                "friction1_target": flow_from_friction(current_ara["target"], 1.0),
                "friction1_mean": flow_from_friction(current_ara["mean"], 1.0),
                "mean_friction_target": flow_from_friction(current_ara["target"], friction_mean["target"]),
                "mean_friction_mean": flow_from_friction(current_ara["mean"], friction_mean["mean"]),
                "predicted_friction_target": flow_from_friction(current_ara["target"], friction_pred["target"]),
                "predicted_friction_mean": flow_from_friction(current_ara["mean"], friction_pred["mean"]),
                "predicted_friction_weighted": flow_from_friction(current_ara["weighted"], friction_pred["weighted"]),
                "predicted_alpha": alpha_pred,
            }

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
                "phi_flow_natural_decoder": blend_dict(proj["current"], proj["natural"], flow_values["phi"], keys),
                "friction1_target_ara_decoder": blend_dict(
                    proj["current"], proj["natural"], flow_values["friction1_target"], keys
                ),
                "friction1_triad_mean_ara_decoder": blend_dict(
                    proj["current"], proj["natural"], flow_values["friction1_mean"], keys
                ),
                "mean_friction_target_ara_decoder": blend_dict(
                    proj["current"], proj["natural"], flow_values["mean_friction_target"], keys
                ),
                "mean_friction_triad_mean_ara_decoder": blend_dict(
                    proj["current"], proj["natural"], flow_values["mean_friction_mean"], keys
                ),
                "predicted_friction_target_ara_decoder": blend_dict(
                    proj["current"], proj["natural"], flow_values["predicted_friction_target"], keys
                ),
                "predicted_friction_triad_mean_ara_decoder": blend_dict(
                    proj["current"], proj["natural"], flow_values["predicted_friction_mean"], keys
                ),
                "predicted_friction_weighted_ara_decoder": blend_dict(
                    proj["current"], proj["natural"], flow_values["predicted_friction_weighted"], keys
                ),
                "predicted_flow_alpha_decoder": blend_dict(
                    proj["current"], proj["natural"], flow_values["predicted_alpha"], keys
                ),
            }

            extras = {
                "alpha_pred_raw": float(alpha_raw),
                "alpha_pred": float(alpha_pred),
                "target_ara": float(current_ara["target"]),
                "triad_mean_ara": float(current_ara["mean"]),
                "triad_weighted_ara": float(current_ara["weighted"]),
                "friction_target_pred_raw": friction_raw["target"],
                "friction_target_pred": friction_pred["target"],
                "friction_target_mean": friction_mean["target"],
                "flow_predicted_friction_target": flow_values["predicted_friction_target"],
            }
            friction_predictions[h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    **extras,
                    "friction_mean_pred_raw": friction_raw["mean"],
                    "friction_mean_pred": friction_pred["mean"],
                    "friction_weighted_pred_raw": friction_raw["weighted"],
                    "friction_weighted_pred": friction_pred["weighted"],
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
            print(f"  {model:42s} {format_score(score_points(all_points[model][h]))}")
        print(f"  {ORACLE_KEY:42s} {format_score(score_points(all_points[ORACLE_KEY][h]))}  diagnostic")
        best = min(MODEL_KEYS, key=lambda m: score_points(all_points[m][h]).get("mae", float("inf")))
        print(f"  best forecast: {best}")
        print()

    scores = {model: {h: score_points(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}
    winners = {str(h): min(MODEL_KEYS, key=lambda m: scores[m][h].get("mae", float("inf"))) for h in HORIZONS}
    friction_summary = {}
    for h in HORIZONS:
        rows = friction_predictions[h]
        friction_summary[str(h)] = {
            key: {
                "mean": float(np.mean([row[key] for row in rows])) if rows else None,
                "std": float(np.std([row[key] for row in rows])) if rows else None,
            }
            for key in [
                "alpha_pred",
                "friction_target_pred",
                "friction_target_mean",
                "friction_mean_pred",
                "friction_weighted_pred",
                "flow_predicted_friction_target",
            ]
        }

    out = {
        "date": "2026-05-23",
        "method": "strict-causal temporal-friction ENSO test",
        "leakage_guard": "At origin t, friction targets train only on s+h<t, decoder trains only on a<t, and lag baseline trains only on s+h<t.",
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "formula": "flow = ARA / (ARA + temporal_friction)",
        "friction_target_note": "Retro flow is clipped to [0.02, 0.98] before deriving positive physical friction.",
        "horizons_months": HORIZONS,
        "rungs_k": RUNG_KS,
        "min_train_examples": MIN_TRAIN,
        "origin_stride_months": ORIGIN_STRIDE,
        "models": {
            "current_decoder": "Decode current geometry with causal decoder.",
            "natural_advance_decoder": "Natural phase advance with full alpha=1.",
            "phi_flow_natural_decoder": "Current->natural blend using old phi-flow formula.",
            "friction1_target_ara_decoder": "Current->natural blend using target ARA and friction=1.",
            "friction1_triad_mean_ara_decoder": "Current->natural blend using triad mean ARA and friction=1.",
            "mean_friction_target_ara_decoder": "Target ARA with causal training-window mean temporal friction.",
            "mean_friction_triad_mean_ara_decoder": "Triad mean ARA with causal training-window mean temporal friction.",
            "predicted_friction_target_ara_decoder": "Target ARA with ridge-predicted temporal friction.",
            "predicted_friction_triad_mean_ara_decoder": "Triad mean ARA with ridge-predicted temporal friction.",
            "predicted_friction_weighted_ara_decoder": "Energy-weighted triad ARA with ridge-predicted temporal friction.",
            "predicted_flow_alpha_decoder": "Comparison: direct ridge-predicted alpha flow.",
            "lag_ridge": "Control: causal target lags and slopes.",
            ORACLE_KEY: "Diagnostic only: decode actual future geometry.",
        },
        "scores": scores,
        "winners": winners,
        "friction_summary": friction_summary,
        "friction_predictions": friction_predictions,
        "points": all_points,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    out_path = HERE / "ara_causal_friction_prediction_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_CAUSAL_FRICTION_PREDICTION = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
