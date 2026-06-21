"""
ara_counter_balance_enso_test.py

Strict-causal ENSO test of Dylan's ARA counter-balance idea:

    A1 and A2 are opposite sides of one coupled relation.
    Weighted by their ARA state, the sides should tend toward equality.
    External feeder energy R shifts that balance.
    If feeder pressure exceeds the current stored level, a snap term fires.

For ENSO:
    A1 = NINO
    A2 = -SOI, because SOI is expected to be anti-phase with NINO
    R  = PDO as external feeder pressure

The learned variants train only on past origins whose target is already known:
at origin t and horizon h, training anchors satisfy s + h < t.
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
from ara_shape_kernel_test import PHI


MODEL_KEYS = [
    "ara_counter_balance_fixed",
    "ara_counter_balance_ridge",
    "ara_counter_balance_snap_ridge",
    "lag_ridge",
]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def ara_side_weight(ara):
    """Weight one side of a relation by its ARA valve fraction."""
    ara = max(0.2, min(3.0, finite(ara, 1.0)))
    return 1.0 / (1.0 + ara)


def snap_pressure(feed, current_level):
    """Signed snap pressure when feeder magnitude exceeds stored level."""
    feed = finite(feed)
    current_level = finite(current_level)
    excess = max(0.0, abs(feed) - abs(current_level))
    if excess <= 0.0:
        return 0.0
    return math.copysign(excess, feed)


def pair_gate(left, right):
    distance = abs(left["center_position"] - right["center_position"])
    return BASE ** (-distance), distance


def counter_balance_features(snapshot, zseries, anchor, horizon, include_snap):
    nino = finite(zseries["NINO"][anchor - 1])
    soi_counter = -finite(zseries["SOI"][anchor - 1])
    pdo_feed = finite(zseries["PDO"][anchor - 1])

    nino_sys = snapshot["NINO"]
    soi_sys = snapshot["SOI"]
    pdo_sys = snapshot["PDO"]

    ns_gate, ns_distance = pair_gate(nino_sys, soi_sys)
    np_gate, np_distance = pair_gate(nino_sys, pdo_sys)
    sp_gate, sp_distance = pair_gate(soi_sys, pdo_sys)

    nino_weight = ara_side_weight(nino_sys["center_ara"])
    soi_weight = ara_side_weight(soi_sys["center_ara"])
    pdo_weight = ara_side_weight(pdo_sys["center_ara"])

    weighted_nino = nino_weight * nino
    weighted_counter = soi_weight * soi_counter
    weighted_feed = pdo_weight * pdo_feed

    balance_to_nino = ns_gate * (weighted_counter - weighted_nino)
    balance_to_counter = ns_gate * (weighted_nino - weighted_counter)
    feed_to_nino = np_gate * (weighted_feed - weighted_nino)
    feed_to_counter = sp_gate * (-weighted_feed - weighted_counter)
    common_mode = 0.5 * (weighted_nino + weighted_counter)
    imbalance = weighted_nino - weighted_counter
    flow = 1.0 - PHI ** (-float(horizon) / HOME_PERIOD)
    flow = max(0.0, min(0.75, flow))

    out = {
        "horizon": float(horizon),
        "flow": flow,
        "nino": nino,
        "soi_counter": soi_counter,
        "pdo_feed": pdo_feed,
        "nino_weight": nino_weight,
        "soi_weight": soi_weight,
        "pdo_weight": pdo_weight,
        "weighted_nino": weighted_nino,
        "weighted_counter": weighted_counter,
        "weighted_feed": weighted_feed,
        "nino_soi_gate": ns_gate,
        "nino_soi_distance": ns_distance,
        "nino_pdo_gate": np_gate,
        "nino_pdo_distance": np_distance,
        "soi_pdo_gate": sp_gate,
        "soi_pdo_distance": sp_distance,
        "balance_to_nino": balance_to_nino,
        "balance_to_counter": balance_to_counter,
        "feed_to_nino": feed_to_nino,
        "feed_to_counter": feed_to_counter,
        "common_mode": common_mode,
        "imbalance": imbalance,
        "flow_balance_to_nino": flow * balance_to_nino,
        "flow_feed_to_nino": flow * feed_to_nino,
    }

    if include_snap:
        nino_snap = np_gate * snap_pressure(weighted_feed, weighted_nino)
        counter_snap = sp_gate * snap_pressure(-weighted_feed, weighted_counter)
        out.update(
            {
                "nino_snap": nino_snap,
                "counter_snap": counter_snap,
                "snap_difference": nino_snap - counter_snap,
                "snap_sum": nino_snap + counter_snap,
                "flow_nino_snap": flow * nino_snap,
                "flow_counter_snap": flow * counter_snap,
                "is_nino_snap": 1.0 if abs(weighted_feed) > abs(weighted_nino) else 0.0,
                "is_counter_snap": 1.0 if abs(weighted_feed) > abs(weighted_counter) else 0.0,
            }
        )

    return {key: finite(value) for key, value in out.items()}


def fixed_counter_delta(features):
    """Parameter-free first pass at the proposed rule."""
    return features["flow"] * (
        features["balance_to_nino"]
        + 0.5 * features["feed_to_nino"]
        + features.get("nino_snap", 0.0)
        - 0.5 * features.get("counter_snap", 0.0)
    )


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

    print("ARA counter-balance ENSO test", flush=True)
    print("=" * 96, flush=True)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}", flush=True)
    print("A1=NINO, A2=-SOI, R=PDO, strict guard s+h<t", flush=True)
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
            feature_cache[h][anchor] = {
                "balance": counter_balance_features(snap, zseries, anchor, h, include_snap=False),
                "snap": counter_balance_features(snap, zseries, anchor, h, include_snap=True),
                "lag": lag_feature_dict(nino_z, anchor),
            }

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS}
    snap_rates = {h: [] for h in HORIZONS}

    for h in HORIZONS:
        origins = list(range(test_start, n - h + 1))
        for origin in origins:
            train_anchors = [s for s in all_anchors if s + h < origin]
            if len(train_anchors) < MIN_TRAIN:
                continue

            target_anchor = origin + h
            actual_raw = float(nino_raw[target_anchor - 1])
            persistence_raw = float(nino_raw[origin - 1])
            current_z = float(nino_z[origin - 1])
            actual_delta_z = float(nino_z[target_anchor - 1] - nino_z[origin - 1])
            scale_std = series["NINO"]["std"]

            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")

            snap_features = feature_cache[h][origin]["snap"]
            fixed_delta_z = fixed_counter_delta(snap_features)
            all_points["ara_counter_balance_fixed"][h].append(
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
            snap_rates[h].append(
                {
                    "nino": snap_features.get("is_nino_snap", 0.0),
                    "counter": snap_features.get("is_counter_snap", 0.0),
                }
            )

            train_y = [float(nino_z[s + h - 1] - nino_z[s - 1]) for s in train_anchors]
            for model, variant in [
                ("ara_counter_balance_ridge", "balance"),
                ("ara_counter_balance_snap_ridge", "snap"),
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
    snap_summary = {}
    for h in HORIZONS:
        snap_summary[str(h)] = {
            "nino_snap_rate": float(np.mean([row["nino"] for row in snap_rates[h]])) if snap_rates[h] else None,
            "counter_snap_rate": float(np.mean([row["counter"] for row in snap_rates[h]])) if snap_rates[h] else None,
        }

    winners = {}
    for h in HORIZONS:
        winners[str(h)] = min(MODEL_KEYS, key=lambda m: scores[m][h].get("mae", float("inf")))

    out = {
        "date": "2026-05-22",
        "method": "strict-causal ARA counter-balance ENSO test",
        "leakage_guard": "At origin t, training uses only anchors s with s+h<t. Snap flags use only current A1/A2/R and current ARA geometry.",
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "counter_pair": {"A1": "NINO", "A2": "-SOI", "R": "PDO"},
        "horizons_months": HORIZONS,
        "min_train_examples": MIN_TRAIN,
        "models": {
            "ara_counter_balance_fixed": "Parameter-free ARA-weighted counter equality plus feeder excess snap.",
            "ara_counter_balance_ridge": "Causal ridge on ARA-weighted counter-balance features without snap terms.",
            "ara_counter_balance_snap_ridge": "Causal ridge on counter-balance features plus snap terms.",
            "lag_ridge": "Control: causal NINO lags and slopes.",
        },
        "scores": scores,
        "winners": winners,
        "snap_summary": snap_summary,
        "points": all_points,
        "elapsed_seconds": round(time.time() - started, 3),
    }

    out_path = HERE / "ara_counter_balance_enso_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_COUNTER_BALANCE_ENSO = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
