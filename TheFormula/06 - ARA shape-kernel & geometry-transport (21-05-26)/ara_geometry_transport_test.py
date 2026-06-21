"""
ara_geometry_transport_test.py

Strict-causal ENSO test for ARA geometry transport.

This tests the next step after ara_state_geometry.py:
  1. read the ARA state geometry at each rolling origin
  2. turn that geometry into transport primitives
  3. train only on past origins whose outcomes are already known
  4. predict NINO3.4 deltas and compare with persistence

The learned models do not see future data. For an origin t and horizon h,
training examples are limited to anchors s where s + h < t.
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

from ara_framework import _measure_rung, causal_bandpass
from ara_shape_kernel_test import (
    PHI,
    infer_phase_from_shape,
    kernel_from_bandpass,
    measure_rung_ara_from_bp,
    release_fraction,
    shape_value_at_phase,
)
from ara_state_geometry import load_enso_frame


BASE = 2.0
HOME_PERIOD = 47.0
HOME_COORDINATE = math.log(HOME_PERIOD) / math.log(BASE)
RUNG_KS = [3, 4, 5, 6, 7]
HORIZONS = [1, 3, 6, 12, 24, 60]
MIN_TRAIN = 96
RIDGE_ALPHA = 5.0
START_YEAR = 2001
MODEL_KEYS = [
    "deterministic_self_transport",
    "nino_geometry_ridge",
    "compact_transport_ridge",
    "wide_geometry_ridge",
    "lag_ridge",
    "lag_plus_nino_geometry_ridge",
    "lag_plus_compact_transport_ridge",
    "lag_plus_wide_geometry_ridge",
]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def round_float(value, digits=6):
    return round(finite(value), digits)


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


def zscore_columns(frame):
    out = {}
    for name in frame.columns:
        vals = frame[name].values.astype(float)
        out[name] = {
            "raw": vals,
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)) + 1e-9,
            "z": (vals - float(np.mean(vals))) / (float(np.std(vals)) + 1e-9),
        }
    return out


def read_subsystem_state(name, values, anchor):
    arr = np.asarray(values, dtype=float)
    home_bp = causal_bandpass(arr[:anchor], HOME_PERIOD)
    home_kernel = kernel_from_bandpass(home_bp, HOME_PERIOD)
    home_ara = measure_rung_ara_from_bp(home_bp, HOME_PERIOD)
    if home_ara is None or not math.isfinite(home_ara):
        home_ara = 1.0
    home_position = HOME_COORDINATE + home_ara / 2.0

    rungs = []
    for k in RUNG_KS:
        period = float(BASE**k)
        if 4.0 * period > anchor:
            continue
        bp = causal_bandpass(arr[:anchor], period)
        rec = _measure_rung(bp, period, k)
        if rec is None:
            continue
        ara = measure_rung_ara_from_bp(bp, period)
        if ara is None or not math.isfinite(ara):
            ara = home_ara
        kernel = kernel_from_bandpass(bp, period)
        phase = infer_phase_from_shape(bp, rec["amp"], ara, kernel)
        split = release_fraction(ara)
        position = float(k) + float(ara) / 2.0
        shape_now = shape_value_at_phase(phase, ara, kernel)
        rungs.append(
            {
                "k": int(k),
                "period": period,
                "amp": float(rec["amp"]),
                "energy": float(rec["amp"] ** 2),
                "theta": float(rec["theta"]),
                "ara": float(ara),
                "phase": float(phase),
                "release_fraction": float(split),
                "is_release": 1.0 if phase < split else 0.0,
                "position": position,
                "home_distance": abs(position - home_position),
                "shape_now": float(shape_now),
                "kernel": kernel,
            }
        )

    total_energy = sum(r["energy"] for r in rungs)
    for rung in rungs:
        rung["occupancy"] = rung["energy"] / total_energy if total_energy > 1e-12 else 0.0

    if rungs:
        center_position = sum(r["position"] * r["occupancy"] for r in rungs)
        center_ara = sum(r["ara"] * r["occupancy"] for r in rungs)
        sx = sum(r["occupancy"] * math.cos(2.0 * math.pi * r["phase"]) for r in rungs)
        sy = sum(r["occupancy"] * math.sin(2.0 * math.pi * r["phase"]) for r in rungs)
        center_phase = (math.atan2(sy, sx) / (2.0 * math.pi)) % 1.0 if abs(sx) + abs(sy) > 1e-12 else 0.0
    else:
        center_position = home_position
        center_ara = home_ara
        center_phase = 0.0

    return {
        "name": name,
        "anchor": int(anchor),
        "home_ara": float(home_ara),
        "home_position": float(home_position),
        "mean": float(np.mean(arr[:anchor])),
        "std": float(np.std(arr[:anchor])) + 1e-9,
        "current": float(arr[anchor - 1]),
        "center_position": float(center_position),
        "center_ara": float(center_ara),
        "center_phase": float(center_phase),
        "total_energy": float(total_energy),
        "rungs": rungs,
    }


def build_snapshot(series_by_name, anchor):
    return {name: read_subsystem_state(name, spec["z"], anchor) for name, spec in series_by_name.items()}


def phase_gap(a, b):
    d = abs((float(a) - float(b)) % 1.0)
    return min(d, 1.0 - d)


def phase_alignment(a, b):
    return math.cos(2.0 * math.pi * phase_gap(a, b))


def geometry_weights(subsystem):
    rungs = subsystem["rungs"]
    if not rungs:
        return np.asarray([], dtype=float)
    raw = np.asarray(
        [max(r["occupancy"], 0.0) * (BASE ** (-abs(r["position"] - subsystem["home_position"]))) for r in rungs],
        dtype=float,
    )
    if raw.sum() <= 1e-12:
        raw = np.ones(len(rungs), dtype=float)
    return raw / raw.sum()


def rung_delta(rung, horizon):
    future = shape_value_at_phase(
        rung["phase"] + horizon / rung["period"],
        rung["ara"],
        rung["kernel"],
    )
    return float(rung["amp"] * (future - rung["shape_now"]))


def self_drive(subsystem, horizon):
    weights = geometry_weights(subsystem)
    if len(weights) == 0:
        return 0.0
    deltas = np.asarray([rung_delta(r, horizon) for r in subsystem["rungs"]], dtype=float)
    return float(np.dot(weights, deltas))


def coupling_drive(target, feeder, horizon):
    weights = []
    drives = []
    supports = []
    oppositions = []
    for tr in target["rungs"]:
        for fr in feeder["rungs"]:
            dist = abs(tr["position"] - fr["position"])
            align = phase_alignment(tr["phase"], fr["phase"])
            energy = math.sqrt(max(tr["occupancy"], 0.0) * max(fr["occupancy"], 0.0))
            proximity = BASE ** (-dist)
            signed = energy * proximity * align
            weights.append(signed)
            drives.append(rung_delta(fr, horizon))
            supports.append(energy * proximity * max(0.0, (1.0 + align) / 2.0))
            oppositions.append(energy * proximity * max(0.0, (1.0 - align) / 2.0))
    if not weights:
        return {
            "drive": 0.0,
            "support": 0.0,
            "opposition": 0.0,
            "mean_abs_weight": 0.0,
            "max_abs_weight": 0.0,
        }
    weights = np.asarray(weights, dtype=float)
    drives = np.asarray(drives, dtype=float)
    denom = float(np.sum(np.abs(weights))) + 1e-12
    return {
        "drive": float(np.dot(weights, drives) / denom),
        "support": float(np.sum(supports)),
        "opposition": float(np.sum(oppositions)),
        "mean_abs_weight": float(np.mean(np.abs(weights))),
        "max_abs_weight": float(np.max(np.abs(weights))),
    }


def center_features(left, right):
    return {
        "distance": abs(left["center_position"] - right["center_position"]),
        "ara_gap": abs(left["center_ara"] - right["center_ara"]),
        "phase_gap": phase_gap(left["center_phase"], right["center_phase"]),
        "phase_alignment": phase_alignment(left["center_phase"], right["center_phase"]),
        "energy_product": math.sqrt(max(left["total_energy"], 0.0) * max(right["total_energy"], 0.0)),
    }


def compact_feature_dict(snapshot, horizon):
    nino = snapshot["NINO"]
    soi = snapshot["SOI"]
    pdo = snapshot["PDO"]
    soi_coupling = coupling_drive(nino, soi, horizon)
    pdo_coupling = coupling_drive(nino, pdo, horizon)
    soi_center = center_features(nino, soi)
    pdo_center = center_features(nino, pdo)
    sp_center = center_features(soi, pdo)

    out = {
        "nino_current": nino["current"],
        "nino_self_drive": self_drive(nino, horizon),
        "nino_total_energy": nino["total_energy"],
        "nino_center_position": nino["center_position"],
        "nino_center_ara": nino["center_ara"],
        "nino_home_ara": nino["home_ara"],
        "nino_release_balance": sum((2.0 * r["is_release"] - 1.0) * r["occupancy"] for r in nino["rungs"]),
        "soi_self_drive": self_drive(soi, horizon),
        "soi_coupled_drive": soi_coupling["drive"],
        "soi_support": soi_coupling["support"],
        "soi_opposition": soi_coupling["opposition"],
        "soi_center_distance": soi_center["distance"],
        "soi_center_ara_gap": soi_center["ara_gap"],
        "soi_center_phase_alignment": soi_center["phase_alignment"],
        "pdo_self_drive": self_drive(pdo, horizon),
        "pdo_coupled_drive": pdo_coupling["drive"],
        "pdo_support": pdo_coupling["support"],
        "pdo_opposition": pdo_coupling["opposition"],
        "pdo_center_distance": pdo_center["distance"],
        "pdo_center_ara_gap": pdo_center["ara_gap"],
        "pdo_center_phase_alignment": pdo_center["phase_alignment"],
        "soi_pdo_center_distance": sp_center["distance"],
        "soi_pdo_center_phase_alignment": sp_center["phase_alignment"],
    }
    return {k: finite(v) for k, v in out.items()}


def nino_geometry_feature_dict(snapshot, horizon):
    nino = snapshot["NINO"]
    out = compact_feature_dict(snapshot, horizon)
    keep = {
        "nino_current",
        "nino_self_drive",
        "nino_total_energy",
        "nino_center_position",
        "nino_center_ara",
        "nino_home_ara",
        "nino_release_balance",
    }
    return {k: v for k, v in out.items() if k in keep}


def wide_feature_dict(snapshot, horizon):
    out = compact_feature_dict(snapshot, horizon)
    for name, subsystem in snapshot.items():
        by_k = {r["k"]: r for r in subsystem["rungs"]}
        for k in RUNG_KS:
            prefix = f"{name.lower()}_k{k}"
            rung = by_k.get(k)
            if rung is None:
                for key in ["amp", "ara", "position", "occupancy", "phase_sin", "phase_cos", "is_release", "delta"]:
                    out[f"{prefix}_{key}"] = 0.0
                continue
            out[f"{prefix}_amp"] = rung["amp"]
            out[f"{prefix}_ara"] = rung["ara"]
            out[f"{prefix}_position"] = rung["position"]
            out[f"{prefix}_occupancy"] = rung["occupancy"]
            out[f"{prefix}_phase_sin"] = math.sin(2.0 * math.pi * rung["phase"])
            out[f"{prefix}_phase_cos"] = math.cos(2.0 * math.pi * rung["phase"])
            out[f"{prefix}_is_release"] = rung["is_release"]
            out[f"{prefix}_delta"] = rung_delta(rung, horizon)

    nino_by_k = {r["k"]: r for r in snapshot["NINO"]["rungs"]}
    for feeder_name in ["SOI", "PDO"]:
        feeder_by_k = {r["k"]: r for r in snapshot[feeder_name]["rungs"]}
        for k in RUNG_KS:
            prefix = f"{feeder_name.lower()}_to_nino_k{k}"
            nino_r = nino_by_k.get(k)
            feeder_r = feeder_by_k.get(k)
            if nino_r is None or feeder_r is None:
                out[f"{prefix}_distance"] = 0.0
                out[f"{prefix}_alignment"] = 0.0
                out[f"{prefix}_signed_drive"] = 0.0
                continue
            dist = abs(nino_r["position"] - feeder_r["position"])
            align = phase_alignment(nino_r["phase"], feeder_r["phase"])
            energy = math.sqrt(max(nino_r["occupancy"], 0.0) * max(feeder_r["occupancy"], 0.0))
            out[f"{prefix}_distance"] = dist
            out[f"{prefix}_alignment"] = align
            out[f"{prefix}_signed_drive"] = energy * (BASE ** (-dist)) * align * rung_delta(feeder_r, horizon)
    return {k: finite(v) for k, v in out.items()}


def lag_feature_dict(nino, anchor):
    current = float(nino[anchor - 1])
    def lag(n):
        return float(nino[anchor - 1 - n]) if anchor - 1 - n >= 0 else current

    return {
        "current": current,
        "lag1": lag(1),
        "lag2": lag(2),
        "lag3": lag(3),
        "lag6": lag(6),
        "lag12": lag(12),
        "slope1": current - lag(1),
        "slope3": current - lag(3),
        "slope12": current - lag(12),
    }


def merge_feature_dicts(*items):
    out = {}
    for item in items:
        for key, value in item.items():
            out[key] = value
    return out


def dict_to_matrix(dicts, keys=None):
    if keys is None:
        keys = sorted({key for item in dicts for key in item})
    mat = np.asarray([[finite(item.get(key, 0.0)) for key in keys] for item in dicts], dtype=float)
    return mat, keys


def fit_predict_ridge(train_dicts, train_y, test_dict, alpha=RIDGE_ALPHA):
    x_train, keys = dict_to_matrix(train_dicts)
    x_test, _ = dict_to_matrix([test_dict], keys=keys)
    y = np.asarray(train_y, dtype=float)

    mean_x = x_train.mean(axis=0)
    std_x = x_train.std(axis=0)
    std_x[std_x < 1e-9] = 1.0
    xz = (x_train - mean_x) / std_x
    tz = (x_test - mean_x) / std_x
    mean_y = float(y.mean())
    yc = y - mean_y

    reg = float(alpha) * np.eye(xz.shape[1])
    try:
        beta = np.linalg.solve(xz.T @ xz + reg, xz.T @ yc)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(xz.T @ xz + reg, xz.T @ yc, rcond=None)
    return float(mean_y + tz[0] @ beta), keys, beta


def score_points(points):
    if len(points) < 5:
        return {"n": int(len(points))}
    pred = np.asarray([p["pred"] for p in points], dtype=float)
    truth = np.asarray([p["actual"] for p in points], dtype=float)
    pers = np.asarray([p["persistence"] for p in points], dtype=float)
    pred_delta = pred - pers
    truth_delta = truth - pers
    pers_mae = float(np.mean(np.abs(pers - truth)))
    mae = float(np.mean(np.abs(pred - truth)))
    denom = float(np.sum((truth - pers) ** 2))
    return {
        "n": int(len(points)),
        "mae": mae,
        "rmse": float(np.sqrt(np.mean((pred - truth) ** 2))),
        "corr": float(np.corrcoef(pred, truth)[0, 1]) if pred.std() > 1e-9 and truth.std() > 1e-9 else 0.0,
        "direction": float(np.mean(np.sign(pred_delta) == np.sign(truth_delta))),
        "persistence_mae": pers_mae,
        "mae_lift_vs_persistence": float(pers_mae - mae),
        "r2_vs_persistence": float(1.0 - np.sum((truth - pred) ** 2) / denom) if denom > 1e-12 else 0.0,
        "pred_delta_std": float(np.std(pred_delta)),
        "truth_delta_std": float(np.std(truth_delta)),
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
    series = zscore_columns(frame)
    nino_raw = series["NINO"]["raw"]
    nino_z = series["NINO"]["z"]
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01")))
    test_start = max(start_idx, min_anchor + MIN_TRAIN + max_h + 1)
    last_origin = n - max_h - 1
    anchors = list(range(min_anchor, n - max_h))

    print("ARA geometry transport ENSO test")
    print("=" * 108)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}")
    print(f"base={BASE}, home_period={HOME_PERIOD} months, rungs={RUNG_KS}")
    print(f"test origins start: {dates[test_start].date()}  longest-horizon last origin: {dates[last_origin].date()}  strict min_train={MIN_TRAIN}")
    print()

    snapshots = {}
    t0 = time.time()
    for i, anchor in enumerate(anchors, start=1):
        snapshots[anchor] = build_snapshot(series, anchor)
        if i % 100 == 0:
            print(f"  snapshots {i:4d}/{len(anchors)} in {time.time() - t0:.1f}s")
    print(f"  snapshots {len(anchors):4d}/{len(anchors)} in {time.time() - t0:.1f}s")
    print()

    feature_cache = {h: {} for h in HORIZONS}
    for h in HORIZONS:
        for anchor in anchors:
            snap = snapshots[anchor]
            lag_features = lag_feature_dict(nino_z, anchor)
            nino_features = nino_geometry_feature_dict(snap, h)
            compact_features = compact_feature_dict(snap, h)
            wide_features = wide_feature_dict(snap, h)
            feature_cache[h][anchor] = {
                "nino_geometry_ridge": nino_features,
                "compact_transport_ridge": compact_features,
                "wide_geometry_ridge": wide_features,
                "lag_ridge": lag_features,
                "lag_plus_nino_geometry_ridge": merge_feature_dicts(
                    {f"lag_{k}": v for k, v in lag_features.items()},
                    {f"geom_{k}": v for k, v in nino_features.items()},
                ),
                "lag_plus_compact_transport_ridge": merge_feature_dicts(
                    {f"lag_{k}": v for k, v in lag_features.items()},
                    {f"transport_{k}": v for k, v in compact_features.items()},
                ),
                "lag_plus_wide_geometry_ridge": merge_feature_dicts(
                    {f"lag_{k}": v for k, v in lag_features.items()},
                    {f"wide_{k}": v for k, v in wide_features.items()},
                ),
                "self_drive": self_drive(snap["NINO"], h),
            }

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS}
    all_scores = {model: {} for model in MODEL_KEYS}
    examples = {h: [] for h in HORIZONS}

    for h in HORIZONS:
        origins = list(range(test_start, n - h))
        for origin in origins:
            train_anchors = [s for s in anchors if s + h < origin]
            if len(train_anchors) < MIN_TRAIN or origin not in snapshots:
                continue

            actual_raw = float(nino_raw[origin + h])
            persistence_raw = float(nino_raw[origin - 1])
            current_raw = persistence_raw

            actual_z = float(nino_z[origin + h])
            current_z = float(nino_z[origin - 1])
            scale_std = series["NINO"]["std"]

            self_delta_z = feature_cache[h][origin]["self_drive"]
            self_pred_raw = current_raw + self_delta_z * scale_std
            all_points["deterministic_self_transport"][h].append(
                {
                    "date": dates[origin + h].strftime("%Y-%m-%d"),
                    "origin": dates[origin - 1].strftime("%Y-%m-%d"),
                    "pred": self_pred_raw,
                    "actual": actual_raw,
                    "persistence": persistence_raw,
                }
            )

            train_y = [float(nino_z[s + h] - nino_z[s - 1]) for s in train_anchors]
            for model in [
                "nino_geometry_ridge",
                "compact_transport_ridge",
                "wide_geometry_ridge",
                "lag_ridge",
                "lag_plus_nino_geometry_ridge",
                "lag_plus_compact_transport_ridge",
                "lag_plus_wide_geometry_ridge",
            ]:
                train_dicts = [feature_cache[h][s][model] for s in train_anchors]
                test_dict = feature_cache[h][origin][model]
                pred_delta_z, _, _ = fit_predict_ridge(train_dicts, train_y, test_dict)
                pred_raw = current_raw + pred_delta_z * scale_std
                all_points[model][h].append(
                    {
                        "date": dates[origin + h].strftime("%Y-%m-%d"),
                        "origin": dates[origin - 1].strftime("%Y-%m-%d"),
                        "pred": pred_raw,
                        "actual": actual_raw,
                        "persistence": persistence_raw,
                        "pred_delta_z": pred_delta_z,
                        "actual_delta_z": actual_z - current_z,
                    }
                )

        for model in MODEL_KEYS:
            all_scores[model][h] = score_points(all_points[model][h])

        rows = [(all_scores[model][h].get("mae", float("inf")), model) for model in MODEL_KEYS]
        rows.sort(key=lambda x: x[0])
        best_model = rows[0][1]
        examples[h] = all_points[best_model][h][:8]
        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:30s} {format_score(all_scores[model][h])}")
        print(f"  best: {best_model}")
        print()

    winners = {}
    for h in HORIZONS:
        scored = [(all_scores[model][h].get("mae", float("inf")), model) for model in MODEL_KEYS]
        scored.sort(key=lambda x: x[0])
        winners[str(h)] = scored[0][1]

    out = {
        "date": "2026-05-21",
        "method": "strict-causal ARA geometry transport ENSO test",
        "leakage_guard": "At origin t, ridge training uses only anchors s with s + horizon < t.",
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "feeders": ["SOI", "PDO"],
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "rungs_k": RUNG_KS,
        "horizons_months": HORIZONS,
        "ridge_alpha": RIDGE_ALPHA,
        "min_train_examples": MIN_TRAIN,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start": dates[test_start].strftime("%Y-%m-%d"),
            "test_last_origin": dates[last_origin].strftime("%Y-%m-%d"),
        },
        "models": {
            "deterministic_self_transport": "Current NINO plus unfit ARA shape self-drive.",
            "nino_geometry_ridge": "Ridge on NINO-only geometry transport features.",
            "compact_transport_ridge": "Ridge on self-drive plus SOI/PDO coupling primitives.",
            "wide_geometry_ridge": "Ridge on compact primitives plus per-rung ARA/phase/occupancy.",
            "lag_ridge": "Ridge on causal NINO lags and slopes.",
            "lag_plus_nino_geometry_ridge": "Causal NINO lags plus NINO-only ARA geometry.",
            "lag_plus_compact_transport_ridge": "Causal NINO lags plus compact ARA transport/coupling primitives.",
            "lag_plus_wide_geometry_ridge": "Causal NINO lags plus wide per-rung ARA geometry.",
        },
        "scores": all_scores,
        "winners": winners,
        "points": all_points,
        "example_points_by_winner": examples,
        "elapsed_seconds": round_float(time.time() - started, 3),
    }
    out_path = HERE / "ara_geometry_transport_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_GEOMETRY_TRANSPORT = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    run()
