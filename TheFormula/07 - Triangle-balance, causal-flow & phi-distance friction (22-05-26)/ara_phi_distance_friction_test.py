"""
ara_phi_distance_friction_test.py

Test Dylan's hypothesis:

    temporal friction ~= distance from phi

Because the previous friction formula uses:

    flow = ARA / (ARA + temporal_friction)

pure friction = |ARA - phi| would make flow approach 1 at ARA=phi. So this
script tests both:

  - pure phi-distance friction
  - baseline friction 1 plus phi-distance
  - normalized/log phi-distance variants

The scoring part is causal: decoder trains only on geometry anchors a<t and lag
baseline trains only on s+h<t. The retro correlation section is diagnostic.
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

from ara_causal_flow_prediction_test import blend_dict, point, vectorize
from ara_causal_friction_prediction_test import ara_values, flow_from_friction, friction_from_flow
from ara_geometry_state_transition_test import (
    ORIGIN_STRIDE,
    build_snapshot_from_series,
    decode_state_features,
    fit_ridge_model,
    natural_advance_decode_features,
    predict_ridge_model,
    raw_series_dict,
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
    "pure_phi_distance_target_decoder",
    "one_plus_phi_distance_target_decoder",
    "one_plus_norm_phi_distance_target_decoder",
    "one_plus_log_phi_distance_target_decoder",
    "one_plus_phi_distance_triad_mean_decoder",
    "one_plus_phi_distance_weighted_ara_decoder",
    "lag_ridge",
]
ORACLE_KEY = "oracle_actual_future_geometry_decoder"


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def build_scale(decode_cache, anchors, keys):
    scale = {}
    for key in keys:
        vals = np.asarray([finite(decode_cache[a].get(key, 0.0)) for a in anchors], dtype=float)
        std = float(np.std(vals))
        scale[key] = std if std > 1e-9 else 1.0
    return scale


def phi_distance(ara):
    return abs(finite(ara, 1.0) - PHI)


def norm_phi_distance(ara):
    return abs(finite(ara, 1.0) - PHI) / PHI


def log_phi_distance(ara):
    ara = max(1e-12, finite(ara, 1.0))
    return abs(math.log(ara / PHI))


def corr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 5 or float(np.std(x)) <= 1e-12 or float(np.std(y)) <= 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def summarize(values):
    vals = np.asarray([finite(v) for v in values], dtype=float)
    if len(vals) == 0:
        return {"n": 0}
    return {
        "n": int(len(vals)),
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals)),
        "p50": float(np.percentile(vals, 50)),
    }


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

    print("ARA phi-distance temporal-friction test", flush=True)
    print("=" * 96, flush=True)
    print(f"phi = {PHI:.6f}; phi-1 = {PHI - 1.0:.6f}", flush=True)
    print("causal score: decoder a<t; lag s+h<t. Retro correlation is diagnostic only.", flush=True)
    print(
        f"test origins start: {dates[test_start - 1].date()}  "
        f"longest-horizon last origin: {dates[last_origin - 1].date()}  "
        f"origin_stride={ORIGIN_STRIDE}",
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
    ara_cache = {anchor: ara_values(snapshots[anchor]) for anchor in all_anchors}
    for h in HORIZONS:
        for anchor in all_anchors:
            projection_cache[h][anchor] = {
                "current": decode_cache[anchor],
                "natural": natural_advance_decode_features(snapshots[anchor], h),
            }

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS + [ORACLE_KEY]}
    retro_rows = {h: [] for h in HORIZONS}

    global_scale = build_scale(decode_cache, all_anchors, keys)
    for h in HORIZONS:
        # Retro diagnostic over the same origins, using actual future geometry.
        for origin in range(test_start, n - h + 1, ORIGIN_STRIDE):
            target_anchor = origin + h
            proj = projection_cache[h][origin]
            current = vectorize(proj["current"], keys, global_scale)
            natural = vectorize(proj["natural"], keys, global_scale)
            future = vectorize(decode_cache[target_anchor], keys, global_scale)
            alpha = best_scalar_flow(current, natural - current, future)
            av = ara_cache[origin]
            retro_rows[h].append(
                {
                    "origin": dates[origin - 1].strftime("%Y-%m-%d"),
                    "target": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                    "retro_flow": alpha,
                    "retro_friction_target": friction_from_flow(av["target"], alpha),
                    "retro_friction_mean": friction_from_flow(av["mean"], alpha),
                    "target_phi_distance": phi_distance(av["target"]),
                    "mean_phi_distance": phi_distance(av["mean"]),
                    "weighted_phi_distance": phi_distance(av["weighted"]),
                }
            )

        for origin in range(test_start, n - h + 1, ORIGIN_STRIDE):
            target_anchor = origin + h
            train_decoder = [a for a in all_anchors if a < origin]
            train_transition = [s for s in all_anchors if s + h < origin]
            if len(train_decoder) < MIN_TRAIN or len(train_transition) < MIN_TRAIN:
                continue

            actual = float(nino[target_anchor - 1])
            persistence = float(nino[origin - 1])
            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")

            decoder_model = fit_ridge_model(
                [decode_cache[a] for a in train_decoder],
                [float(nino[a - 1]) for a in train_decoder],
            )

            av = ara_cache[origin]
            target_ara = av["target"]
            mean_ara = av["mean"]
            weighted_ara = av["weighted"]
            phi_flow = max(0.0, min(1.25, 1.0 - PHI ** (-float(h) / HOME_PERIOD)))
            flows = {
                "phi_flow_natural_decoder": phi_flow,
                "friction1_target_ara_decoder": flow_from_friction(target_ara, 1.0),
                "pure_phi_distance_target_decoder": flow_from_friction(target_ara, max(0.05, phi_distance(target_ara))),
                "one_plus_phi_distance_target_decoder": flow_from_friction(target_ara, 1.0 + phi_distance(target_ara)),
                "one_plus_norm_phi_distance_target_decoder": flow_from_friction(target_ara, 1.0 + norm_phi_distance(target_ara)),
                "one_plus_log_phi_distance_target_decoder": flow_from_friction(target_ara, 1.0 + log_phi_distance(target_ara)),
                "one_plus_phi_distance_triad_mean_decoder": flow_from_friction(mean_ara, 1.0 + phi_distance(mean_ara)),
                "one_plus_phi_distance_weighted_ara_decoder": flow_from_friction(
                    weighted_ara,
                    1.0 + phi_distance(weighted_ara),
                ),
            }

            proj = projection_cache[h][origin]
            projected = {
                "current_decoder": proj["current"],
                "natural_advance_decoder": proj["natural"],
            }
            for model, flow in flows.items():
                projected[model] = blend_dict(proj["current"], proj["natural"], flow, keys)

            extras = {
                "target_ara": float(target_ara),
                "target_phi_distance": float(phi_distance(target_ara)),
                "mean_ara": float(mean_ara),
                "weighted_ara": float(weighted_ara),
                "flow_one_plus_phi_distance_target": float(flows["one_plus_phi_distance_target_decoder"]),
            }
            for model, features in projected.items():
                pred = float(predict_ridge_model(decoder_model, features)[0])
                all_points[model][h].append(point(origin_date, target_date, pred, actual, persistence, extras))

            train_y_delta = [float(nino[s + h - 1] - nino[s - 1]) for s in train_transition]
            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(nino, s) for s in train_transition],
                train_y_delta,
                lag_feature_dict(nino, origin),
            )
            all_points["lag_ridge"][h].append(point(origin_date, target_date, persistence + lag_delta, actual, persistence))

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
    retro_summary = {}
    for h in HORIZONS:
        rows = retro_rows[h]
        retro_summary[str(h)] = {
            "retro_flow": summarize([row["retro_flow"] for row in rows]),
            "retro_friction_target": summarize([row["retro_friction_target"] for row in rows]),
            "target_phi_distance": summarize([row["target_phi_distance"] for row in rows]),
            "corr_friction_target_vs_phi_distance": corr(
                [row["retro_friction_target"] for row in rows],
                [row["target_phi_distance"] for row in rows],
            ),
            "corr_flow_vs_phi_distance": corr(
                [row["retro_flow"] for row in rows],
                [row["target_phi_distance"] for row in rows],
            ),
        }

    print("Retro diagnostic: corr(friction, |ARA-phi|), corr(flow, |ARA-phi|)")
    for h in HORIZONS:
        s = retro_summary[str(h)]
        print(
            f"  h={h:2d}: "
            f"fric corr={s['corr_friction_target_vs_phi_distance']:+.3f}, "
            f"flow corr={s['corr_flow_vs_phi_distance']:+.3f}, "
            f"mean phi-dist={s['target_phi_distance']['mean']:.3f}",
            flush=True,
        )

    out = {
        "date": "2026-05-23",
        "method": "phi-distance temporal-friction test",
        "leakage_guard": "Forecast scores use decoder training a<t and lag training s+h<t. Retro correlations use actual future geometry and are diagnostic only.",
        "hypothesis": "temporal friction is phi-distance, or baseline friction plus phi-distance.",
        "phi": PHI,
        "horizons_months": HORIZONS,
        "rungs_k": RUNG_KS,
        "models": {
            "pure_phi_distance_target_decoder": "flow = ARA / (ARA + max(0.05, |ARA-phi|))",
            "one_plus_phi_distance_target_decoder": "flow = ARA / (ARA + 1 + |ARA-phi|)",
            "one_plus_norm_phi_distance_target_decoder": "flow = ARA / (ARA + 1 + |ARA-phi|/phi)",
            "one_plus_log_phi_distance_target_decoder": "flow = ARA / (ARA + 1 + |log(ARA/phi)|)",
        },
        "scores": scores,
        "winners": winners,
        "retro_summary": retro_summary,
        "retro_rows": retro_rows,
        "points": all_points,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    out_path = HERE / "ara_phi_distance_friction_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_PHI_DISTANCE_FRICTION = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
