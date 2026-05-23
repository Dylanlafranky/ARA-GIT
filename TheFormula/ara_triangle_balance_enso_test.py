"""
ara_triangle_balance_enso_test.py

Strict-causal ENSO test of the "pick two, but actually inside the triangle"
version of the ARA counter-balance idea.

Base relation:
    A1 = NINO
    A2 = -SOI
    R  = PDO

Triangle coordinates:
    ARA corner         = imbalance / stored-pressure side
    Rationality corner = triad closure / coupling-coherence side
    Time corner        = continuation / recent-motion side

The model asks whether the forecast pressure is better described as a position
inside that triangle than as a one-dimensional A1 <-> A2 equalization.
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

from ara_counter_balance_enso_test import counter_balance_features, fixed_counter_delta
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
from ara_shape_kernel_test import PHI, shape_value_at_phase


MODEL_KEYS = [
    "triangle_balance_fixed",
    "triangle_balance_ridge",
    "triangle_balance_snap_ridge",
    "triangle_slow_antiphase_ridge",
    "counter_balance_snap_ridge",
    "lag_ridge",
]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def zlag(zseries, name, anchor, lag):
    idx = anchor - 1 - lag
    if idx < 0:
        idx = anchor - 1
    return finite(zseries[name][idx])


def safe_ratio(num, denom):
    return finite(num) / (abs(finite(denom)) + 1e-12)


def normalize_triangle(a_raw, r_raw, t_raw):
    vals = np.asarray([max(0.0, finite(a_raw)), max(0.0, finite(r_raw)), max(0.0, finite(t_raw))], dtype=float)
    if vals.sum() <= 1e-12:
        vals[:] = 1.0 / 3.0
    else:
        vals /= vals.sum()
    return float(vals[0]), float(vals[1]), float(vals[2])


def triangle_balance_features(snapshot, zseries, anchor, horizon, include_snap):
    base = counter_balance_features(snapshot, zseries, anchor, horizon, include_snap=include_snap)
    energy = (
        abs(base["weighted_nino"])
        + abs(base["weighted_counter"])
        + abs(base["weighted_feed"])
        + 1e-12
    )

    nino_v1 = base["nino"] - zlag(zseries, "NINO", anchor, 1)
    nino_v3 = (base["nino"] - zlag(zseries, "NINO", anchor, 3)) / 3.0
    nino_v12 = (base["nino"] - zlag(zseries, "NINO", anchor, 12)) / 12.0

    counter_prev1 = -zlag(zseries, "SOI", anchor, 1)
    counter_prev3 = -zlag(zseries, "SOI", anchor, 3)
    counter_v1 = base["soi_counter"] - counter_prev1
    counter_v3 = (base["soi_counter"] - counter_prev3) / 3.0

    feed_v1 = base["pdo_feed"] - zlag(zseries, "PDO", anchor, 1)
    feed_v3 = (base["pdo_feed"] - zlag(zseries, "PDO", anchor, 3)) / 3.0

    pair_imbalance_ratio = min(1.0, abs(base["imbalance"]) / energy)
    feed_excess_ratio = min(1.0, abs(base["weighted_feed"]) / energy)
    closure_error = abs(base["weighted_nino"] - base["weighted_counter"] + 0.5 * base["weighted_feed"])
    triad_closure = 1.0 - min(1.0, closure_error / energy)
    coupling_coherence = (
        max(base["nino_soi_gate"], 0.0)
        * max(base["nino_pdo_gate"], 0.0)
        * max(base["soi_pdo_gate"], 0.0)
    ) ** (1.0 / 3.0)

    time_pressure = (
        0.50 * nino_v1
        + 0.25 * nino_v3
        + 0.15 * counter_v1
        + 0.05 * counter_v3
        + 0.05 * feed_v1
        + 0.05 * feed_v3
    )
    time_motion_ratio = min(1.0, abs(time_pressure) / energy)

    ara_raw = pair_imbalance_ratio + 0.5 * feed_excess_ratio
    rationality_raw = triad_closure * coupling_coherence
    time_raw = base["flow"] + time_motion_ratio
    tri_ara, tri_rationality, tri_time = normalize_triangle(ara_raw, rationality_raw, time_raw)

    balance_pressure = base["balance_to_nino"] + 0.5 * base["feed_to_nino"]
    rationality_pressure = triad_closure * (
        base["balance_to_nino"] - 0.5 * base["feed_to_counter"]
    )
    snap_pressure = base.get("nino_snap", 0.0) - 0.5 * base.get("counter_snap", 0.0)
    triangle_pressure = (
        tri_ara * (balance_pressure + snap_pressure)
        + tri_rationality * rationality_pressure
        + tri_time * time_pressure
    )

    out = dict(base)
    out.update(
        {
            "nino_v1": nino_v1,
            "nino_v3": nino_v3,
            "nino_v12": nino_v12,
            "counter_v1": counter_v1,
            "counter_v3": counter_v3,
            "feed_v1": feed_v1,
            "feed_v3": feed_v3,
            "pair_imbalance_ratio": pair_imbalance_ratio,
            "feed_excess_ratio": feed_excess_ratio,
            "closure_error": closure_error,
            "triad_closure": triad_closure,
            "coupling_coherence": coupling_coherence,
            "time_pressure": time_pressure,
            "time_motion_ratio": time_motion_ratio,
            "triangle_ara": tri_ara,
            "triangle_rationality": tri_rationality,
            "triangle_time": tri_time,
            "balance_pressure": balance_pressure,
            "rationality_pressure": rationality_pressure,
            "triangle_snap_pressure": snap_pressure,
            "triangle_pressure": triangle_pressure,
            "ara_x_balance": tri_ara * balance_pressure,
            "ara_x_snap": tri_ara * snap_pressure,
            "rationality_x_closure": tri_rationality * triad_closure,
            "rationality_x_pressure": tri_rationality * rationality_pressure,
            "time_x_pressure": tri_time * time_pressure,
            "time_x_flow": tri_time * base["flow"],
        }
    )

    if not include_snap:
        for key in [
            "nino_snap",
            "counter_snap",
            "snap_difference",
            "snap_sum",
            "flow_nino_snap",
            "flow_counter_snap",
            "is_nino_snap",
            "is_counter_snap",
            "triangle_snap_pressure",
            "ara_x_snap",
        ]:
            out.pop(key, None)

    return {key: finite(value) for key, value in out.items()}


def triangle_fixed_delta(features):
    return features["flow"] * features["triangle_pressure"]


def slowest_nino_rung(snapshot):
    rungs = snapshot["NINO"]["rungs"]
    if not rungs:
        return None
    return max(rungs, key=lambda rung: rung["period"])


def with_slow_antiphase_features(features, snapshot, horizon):
    out = dict(features)
    rung = slowest_nino_rung(snapshot)
    if rung is None:
        return out

    slow_phase = finite(rung["phase"])
    slow_period = max(finite(rung["period"], 1.0), 1e-12)
    slow_alignment = math.cos(2.0 * math.pi * float(horizon) / slow_period)
    slow_antiphase = max(0.0, -slow_alignment)
    slow_inphase = max(0.0, slow_alignment)
    future_phase = (slow_phase + horizon / slow_period) % 1.0
    future_shape = shape_value_at_phase(future_phase, rung["ara"], rung["kernel"])
    now_shape = finite(rung.get("shape_now", 0.0))
    slow_shape_delta = future_shape - now_shape

    triangle_pressure = finite(out.get("triangle_pressure", 0.0))
    balance_pressure = finite(out.get("balance_pressure", 0.0))
    rationality_pressure = finite(out.get("rationality_pressure", 0.0))
    time_pressure = finite(out.get("time_pressure", 0.0))
    snap_pressure = finite(out.get("triangle_snap_pressure", 0.0))

    out.update(
        {
            "slow_period": slow_period,
            "slow_phase_sin": math.sin(2.0 * math.pi * slow_phase),
            "slow_phase_cos": math.cos(2.0 * math.pi * slow_phase),
            "slow_alignment_to_horizon": slow_alignment,
            "slow_inphase_gate": slow_inphase,
            "slow_antiphase_gate": slow_antiphase,
            "slow_shape_now": now_shape,
            "slow_shape_future": future_shape,
            "slow_shape_delta": slow_shape_delta,
            "triangle_pressure_slow_aligned": triangle_pressure * slow_alignment,
            "triangle_pressure_slow_inphase": triangle_pressure * slow_inphase,
            "triangle_pressure_slow_antiphase": -triangle_pressure * slow_antiphase,
            "balance_pressure_slow_aligned": balance_pressure * slow_alignment,
            "rationality_pressure_slow_aligned": rationality_pressure * slow_alignment,
            "time_pressure_slow_aligned": time_pressure * slow_alignment,
            "snap_pressure_slow_antiphase": -snap_pressure * slow_antiphase,
            "triangle_pressure_x_slow_future": triangle_pressure * future_shape,
            "triangle_pressure_x_slow_delta": triangle_pressure * slow_shape_delta,
        }
    )
    return {key: finite(value) for key, value in out.items()}


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
    series = zscore_columns(frame)
    zseries = {name: series[name]["z"] for name in ["NINO", "SOI", "PDO"]}
    nino_raw = series["NINO"]["raw"]
    nino_z = series["NINO"]["z"]
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01")))
    test_start = max(start_idx + 1, min_anchor + MIN_TRAIN + max_h + 1)
    last_origin = n - max_h
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA triangle-balance ENSO test", flush=True)
    print("=" * 96, flush=True)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}", flush=True)
    print("A1=NINO, A2=-SOI, third=PDO, triangle=(ARA, Rationality, Time)", flush=True)
    print(
        f"test origins start: {dates[test_start - 1].date()}  "
        f"longest-horizon last origin: {dates[last_origin - 1].date()}",
        flush=True,
    )
    print(flush=True)

    snapshots = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        snapshots[anchor] = build_snapshot(series, anchor)
        if i % 100 == 0:
            print(f"  snapshots {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  snapshots {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(flush=True)

    feature_cache = {h: {} for h in HORIZONS}
    for h in HORIZONS:
        for anchor in all_anchors:
            snap = snapshots[anchor]
            triangle_snap = triangle_balance_features(snap, zseries, anchor, h, include_snap=True)
            feature_cache[h][anchor] = {
                "triangle": triangle_balance_features(snap, zseries, anchor, h, include_snap=False),
                "triangle_snap": triangle_snap,
                "triangle_slow_antiphase": with_slow_antiphase_features(triangle_snap, snap, h),
                "counter_snap": counter_balance_features(snap, zseries, anchor, h, include_snap=True),
                "lag": lag_feature_dict(nino_z, anchor),
            }

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS}
    triangle_summary_rows = {h: [] for h in HORIZONS}

    for h in HORIZONS:
        origins = list(range(test_start, n - h + 1))
        for origin in origins:
            train_anchors = [s for s in all_anchors if s + h < origin]
            if len(train_anchors) < MIN_TRAIN:
                continue

            target_anchor = origin + h
            actual_raw = float(nino_raw[target_anchor - 1])
            persistence_raw = float(nino_raw[origin - 1])
            actual_delta_z = float(nino_z[target_anchor - 1] - nino_z[origin - 1])
            scale_std = series["NINO"]["std"]

            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")

            tri_snap = feature_cache[h][origin]["triangle_snap"]
            fixed_delta_z = triangle_fixed_delta(tri_snap)
            all_points["triangle_balance_fixed"][h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    "pred": persistence_raw + fixed_delta_z * scale_std,
                    "actual": actual_raw,
                    "persistence": persistence_raw,
                    "pred_delta_z": fixed_delta_z,
                    "actual_delta_z": actual_delta_z,
                }
            )
            triangle_summary_rows[h].append(
                {
                    "ara": tri_snap["triangle_ara"],
                    "rationality": tri_snap["triangle_rationality"],
                    "time": tri_snap["triangle_time"],
                }
            )

            train_y = [float(nino_z[s + h - 1] - nino_z[s - 1]) for s in train_anchors]
            for model, variant in [
                ("triangle_balance_ridge", "triangle"),
                ("triangle_balance_snap_ridge", "triangle_snap"),
                ("triangle_slow_antiphase_ridge", "triangle_slow_antiphase"),
                ("counter_balance_snap_ridge", "counter_snap"),
                ("lag_ridge", "lag"),
            ]:
                pred_delta_z, _, _ = fit_predict_ridge(
                    [feature_cache[h][s][variant] for s in train_anchors],
                    train_y,
                    feature_cache[h][origin][variant],
                )
                all_points[model][h].append(
                    {
                        "origin": origin_date,
                        "date": target_date,
                        "pred": persistence_raw + pred_delta_z * scale_std,
                        "actual": actual_raw,
                        "persistence": persistence_raw,
                        "pred_delta_z": pred_delta_z,
                        "actual_delta_z": actual_delta_z,
                    }
                )

        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:34s} {format_score(score_points(all_points[model][h]))}")
        best = min(MODEL_KEYS, key=lambda m: score_points(all_points[m][h]).get("mae", float("inf")))
        print(f"  best: {best}")
        print()

    scores = {model: {h: score_points(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS}
    triangle_summary = {}
    for h in HORIZONS:
        rows = triangle_summary_rows[h]
        triangle_summary[str(h)] = {
            key: float(np.mean([row[key] for row in rows])) if rows else None
            for key in ["ara", "rationality", "time"]
        }

    winners = {}
    for h in HORIZONS:
        winners[str(h)] = min(MODEL_KEYS, key=lambda m: scores[m][h].get("mae", float("inf")))

    out = {
        "date": "2026-05-22",
        "method": "strict-causal ARA triangle-balance ENSO test",
        "leakage_guard": "At origin t, training uses only anchors s with s+h<t. Triangle coordinates use only current A1/A2/R, current ARA geometry, and causal past motion.",
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "triangle": {
            "A1": "NINO",
            "A2": "-SOI",
            "third_system": "PDO",
            "vertices": ["ARA", "Rationality", "Time"],
        },
        "horizons_months": HORIZONS,
        "min_train_examples": MIN_TRAIN,
        "models": {
            "triangle_balance_fixed": "Parameter-free triangle pressure from ARA/Rationality/Time coordinates.",
            "triangle_balance_ridge": "Causal ridge on triangle coordinates and pressure terms without snap.",
            "triangle_balance_snap_ridge": "Causal ridge on triangle coordinates and pressure terms with snap.",
            "triangle_slow_antiphase_ridge": "Triangle+snap features with slowest NINO rung anti-phase interactions for later windows.",
            "counter_balance_snap_ridge": "Control: previous A1/A2/R counter-balance snap model.",
            "lag_ridge": "Control: causal NINO lags and slopes.",
        },
        "scores": scores,
        "winners": winners,
        "triangle_summary": triangle_summary,
        "points": all_points,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    out_path = HERE / "ara_triangle_balance_enso_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_TRIANGLE_BALANCE_ENSO = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
