"""
ara_phi_distance_bk_fit_test.py

Strict-causal test for:

    temporal_friction = B + k * |ARA - phi|

The intent is to separate a baseline temporal resistance (B) from a phi-distance
modulation (k).  The same single-signal geometry runner is used for ENSO,
Solar, and ECG RR so the result is not hardcoded to ENSO feeder structure.

For origin t and horizon h:
  - B,k are fit only from completed windows s+h<t
  - the value decoder trains only on geometry anchors a<t
  - geometry at t+h is used only for retro diagnostics / training targets whose
    outcomes are already closed before t
"""

from __future__ import annotations

import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
WORKSPACE_ROOT = REPO_ROOT.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_framework import _measure_rung, causal_bandpass
from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import clean_for_json, fit_predict_ridge, lag_feature_dict, score_points
from ara_retroactive_flow_test import best_scalar_flow
from ara_shape_kernel_test import (
    PHI,
    infer_phase_from_shape,
    kernel_from_bandpass,
    measure_rung_ara_from_bp,
    release_fraction,
    shape_value_at_phase,
)


PI_LEAK_ENERGY = (math.pi - 3.0) / math.pi
PI_LEAK_TOPOLOGY = math.pi - 3.0
FRICTION_MIN = 0.05
FRICTION_MAX = 4.0
FLOW_MIN = 0.02
FLOW_MAX = 0.98


@dataclass(frozen=True)
class DatasetSpec:
    name: str
    unit: str
    dates: list[str]
    values: np.ndarray
    home_period: float
    rungs_k: list[int]
    horizons: list[int]
    min_train: int
    anchor_stride: int
    origin_stride: int
    start_index_floor: int = 0
    base: float = 2.0


MODEL_KEYS = [
    "current_decoder",
    "natural_advance_decoder",
    "phi_flow_decoder",
    "friction1_decoder",
    "fixed_1_plus_phi_distance_decoder",
    "fixed_1_plus_pi_leak_phi_distance_decoder",
    "mean_friction_decoder",
    "learned_bk_phi_distance_decoder",
    "positive_bk_phi_distance_decoder",
    "one_plus_pi_floor_bk_decoder",
    "lag_ridge",
]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def clip(value, lo, hi):
    return max(lo, min(hi, finite(value)))


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


def flow_from_friction(ara, friction):
    ara = max(1e-12, finite(ara, 1.0))
    friction = clip(friction, FRICTION_MIN, FRICTION_MAX)
    return float(ara / (ara + friction))


def friction_from_flow(ara, flow):
    ara = max(1e-12, finite(ara, 1.0))
    flow = clip(flow, FLOW_MIN, FLOW_MAX)
    return float(ara * (1.0 - flow) / flow)


def phi_distance(ara):
    return abs(finite(ara, 1.0) - PHI)


def fit_bk(distances, frictions):
    d = np.asarray(distances, dtype=float)
    f = np.asarray(frictions, dtype=float)
    good = np.isfinite(d) & np.isfinite(f)
    d = d[good]
    f = f[good]
    if len(d) < 3 or float(np.std(d)) < 1e-9:
        return float(np.mean(f)) if len(f) else 1.0, 0.0

    x = np.column_stack([np.ones(len(d)), d])
    reg = np.diag([0.0, 1e-3])
    try:
        beta = np.linalg.solve(x.T @ x + reg, x.T @ f)
    except np.linalg.LinAlgError:
        beta, *_ = np.linalg.lstsq(x.T @ x + reg, x.T @ f, rcond=None)
    return float(beta[0]), float(beta[1])


def fit_bk_constrained(distances, frictions, b_floor):
    """Fit B+k*d with B>=b_floor and k>=0 by checking the active boundaries."""
    d = np.asarray(distances, dtype=float)
    f = np.asarray(frictions, dtype=float)
    good = np.isfinite(d) & np.isfinite(f)
    d = d[good]
    f = f[good]
    if len(d) < 3:
        return float(max(b_floor, np.mean(f))) if len(f) else float(b_floor), 0.0

    candidates = []
    b_ols, k_ols = fit_bk(d, f)
    if b_ols >= b_floor and k_ols >= 0.0:
        candidates.append((b_ols, k_ols))

    b_const = max(float(b_floor), float(np.mean(f)))
    candidates.append((b_const, 0.0))

    denom = float(np.dot(d, d))
    if denom > 1e-12:
        k_floor = max(0.0, float(np.dot(d, f - b_floor) / denom))
        candidates.append((float(b_floor), k_floor))

    if float(np.std(d)) > 1e-9:
        # k=0 boundary has already been handled; this fallback protects against
        # tiny numerical cases where the OLS point is just outside the feasible set.
        candidates.append((max(float(b_floor), b_ols), max(0.0, k_ols)))

    best = min(candidates, key=lambda bk: float(np.mean((bk[0] + bk[1] * d - f) ** 2)))
    return float(best[0]), float(best[1])


def summarize(values):
    vals = np.asarray([finite(v) for v in values if math.isfinite(finite(v, float("nan")))], dtype=float)
    if len(vals) == 0:
        return {"n": 0}
    return {
        "n": int(len(vals)),
        "mean": float(np.mean(vals)),
        "std": float(np.std(vals)),
        "p25": float(np.percentile(vals, 25)),
        "p50": float(np.percentile(vals, 50)),
        "p75": float(np.percentile(vals, 75)),
    }


def corr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    good = np.isfinite(x) & np.isfinite(y)
    x = x[good]
    y = y[good]
    if len(x) < 5 or float(np.std(x)) < 1e-12 or float(np.std(y)) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def build_scale(cache, anchors, keys):
    scale = {}
    for key in keys:
        vals = np.asarray([finite(cache[a].get(key, 0.0)) for a in anchors if a in cache], dtype=float)
        std = float(np.std(vals)) if len(vals) else 1.0
        scale[key] = std if std > 1e-9 else 1.0
    return scale


def vectorize(features, keys, scale):
    return np.asarray([finite(features.get(key, 0.0)) / scale.get(key, 1.0) for key in keys], dtype=float)


def blend_features(start, end, alpha, keys):
    alpha = finite(alpha)
    return {
        key: finite(start.get(key, 0.0)) + alpha * (finite(end.get(key, 0.0)) - finite(start.get(key, 0.0)))
        for key in keys
    }


def label_for(dates, index_1_based):
    idx = max(1, min(index_1_based, len(dates))) - 1
    return str(dates[idx])


def read_signal_state(values, anchor, spec: DatasetSpec):
    arr = np.asarray(values, dtype=float)
    base = float(spec.base)
    home_period = float(spec.home_period)
    home_coordinate = math.log(home_period) / math.log(base)

    home_bp = causal_bandpass(arr[:anchor], home_period)
    home_kernel = kernel_from_bandpass(home_bp, home_period)
    home_ara = measure_rung_ara_from_bp(home_bp, home_period)
    if home_ara is None or not math.isfinite(home_ara):
        home_ara = 1.0
    home_position = home_coordinate + home_ara / 2.0

    rungs = []
    for k in spec.rungs_k:
        period = float(base**k)
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
                "position": float(k) + float(ara) / 2.0,
                "home_distance": abs(float(k) + float(ara) / 2.0 - home_position),
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


def finalize_state(state):
    total_energy = max(finite(state.get("total_energy", 0.0)), 1e-12)
    center_position = 0.0
    center_ara = 0.0
    phase_x = 0.0
    phase_y = 0.0
    for rung in state["rungs"]:
        rung["position"] = float(rung["k"] + rung["ara"] / 2.0)
        rung["amp"] = float(math.sqrt(max(rung["occupancy"] * total_energy, 0.0)))
        rung["shape_now"] = float(shape_value_at_phase(rung["phase"], rung["ara"], rung["kernel"]))
        rung["component"] = float(rung["amp"] * rung["shape_now"])
        rung["release_fraction"] = float(release_fraction(rung["ara"]))
        rung["is_release"] = 1.0 if rung["phase"] < rung["release_fraction"] else 0.0
        center_position += rung["position"] * rung["occupancy"]
        center_ara += rung["ara"] * rung["occupancy"]
        angle = 2.0 * math.pi * rung["phase"]
        phase_x += rung["occupancy"] * math.cos(angle)
        phase_y += rung["occupancy"] * math.sin(angle)

    state["center_position"] = float(center_position if state["rungs"] else state["home_position"])
    state["center_ara"] = float(center_ara if state["rungs"] else state["home_ara"])
    state["center_phase"] = float((math.atan2(phase_y, phase_x) / (2.0 * math.pi)) % 1.0) if abs(phase_x) + abs(phase_y) > 1e-12 else 0.0
    return state


def natural_advance_state(state, horizon):
    projected = dict(state)
    projected["rungs"] = []
    for rung in state["rungs"]:
        nr = dict(rung)
        nr["phase"] = float((rung["phase"] + float(horizon) / max(rung["period"], 1e-12)) % 1.0)
        projected["rungs"].append(nr)
    return finalize_state(projected)


def decode_signal_features(state, spec: DatasetSpec):
    out = {
        "home_ara": state["home_ara"],
        "center_position": state["center_position"],
        "center_ara": state["center_ara"],
        "center_phase_sin": math.sin(2.0 * math.pi * state["center_phase"]),
        "center_phase_cos": math.cos(2.0 * math.pi * state["center_phase"]),
        "total_energy": state["total_energy"],
        "release_balance": sum((2.0 * r["is_release"] - 1.0) * r["occupancy"] for r in state["rungs"]),
    }

    by_k = {r["k"]: r for r in state["rungs"]}
    for k in spec.rungs_k:
        r = by_k.get(k)
        prefix = f"k{k}"
        if r is None:
            out[f"{prefix}_amp"] = 0.0
            out[f"{prefix}_ara"] = 0.0
            out[f"{prefix}_position"] = 0.0
            out[f"{prefix}_occupancy"] = 0.0
            out[f"{prefix}_phase_sin"] = 0.0
            out[f"{prefix}_phase_cos"] = 0.0
            out[f"{prefix}_shape_now"] = 0.0
            out[f"{prefix}_component"] = 0.0
            out[f"{prefix}_is_release"] = 0.0
            continue
        out[f"{prefix}_amp"] = r["amp"]
        out[f"{prefix}_ara"] = r["ara"]
        out[f"{prefix}_position"] = r["position"]
        out[f"{prefix}_occupancy"] = r["occupancy"]
        out[f"{prefix}_phase_sin"] = math.sin(2.0 * math.pi * r["phase"])
        out[f"{prefix}_phase_cos"] = math.cos(2.0 * math.pi * r["phase"])
        out[f"{prefix}_shape_now"] = r["shape_now"]
        out[f"{prefix}_component"] = r["amp"] * r["shape_now"]
        out[f"{prefix}_is_release"] = r["is_release"]

    return {key: finite(value) for key, value in out.items()}


def load_enso():
    path = WORKSPACE_ROOT / "Nino34" / "nino34.long.anom.csv"
    df = pd.read_csv(path, skiprows=1, header=None, names=["date", "value"])
    df["date"] = pd.to_datetime(df["date"].astype(str).str.strip(), errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()
    df = df[df["value"] > -50].reset_index(drop=True)
    start_floor = int(np.searchsorted(df["date"].values.astype("datetime64[ns]"), np.datetime64("2001-01-01"))) + 1
    return DatasetSpec(
        name="ENSO_NINO34",
        unit="monthly anomaly",
        dates=df["date"].dt.strftime("%Y-%m-%d").tolist(),
        values=df["value"].values.astype(float),
        home_period=47.0,
        rungs_k=[3, 4, 5, 6, 7],
        horizons=[1, 3, 6, 12, 24, 60],
        min_train=96,
        anchor_stride=3,
        origin_stride=3,
        start_index_floor=start_floor,
    )


def load_solar():
    path = WORKSPACE_ROOT / "SILSO_Solar" / "SN_m_tot_V2.0.csv"
    df = pd.read_csv(
        path,
        sep=";",
        header=None,
        names=["year", "month", "decimal_year", "value", "std", "n_obs", "provisional"],
    )
    df["date"] = pd.to_datetime(
        {
            "year": pd.to_numeric(df["year"], errors="coerce"),
            "month": pd.to_numeric(df["month"], errors="coerce"),
            "day": 1,
        },
        errors="coerce",
    )
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna()
    df = df[df["value"] >= 0].reset_index(drop=True)
    start_floor = int(np.searchsorted(df["date"].values.astype("datetime64[ns]"), np.datetime64("1850-01-01"))) + 1
    return DatasetSpec(
        name="Solar_SILSO",
        unit="monthly sunspot number",
        dates=df["date"].dt.strftime("%Y-%m-%d").tolist(),
        values=df["value"].values.astype(float),
        home_period=132.0,
        rungs_k=[4, 5, 6, 7, 8, 9],
        horizons=[6, 12, 24, 60, 132],
        min_train=120,
        anchor_stride=6,
        origin_stride=12,
        start_index_floor=start_floor,
    )


def load_ecg_rr():
    path = WORKSPACE_ROOT / "TheFormula" / "nsr001_rr.csv"
    df = pd.read_csv(path)
    time_s = pd.to_numeric(df["time_s"], errors="coerce").values.astype(float)
    rr_ms = pd.to_numeric(df["rr_ms"], errors="coerce").values.astype(float)
    good = np.isfinite(time_s) & np.isfinite(rr_ms)
    time_s = time_s[good]
    rr_ms = rr_ms[good]
    dt = 10.0
    grid = np.arange(0.0, int(time_s[-1]) - 1, dt)
    values = np.interp(grid, time_s, rr_ms)
    labels = [f"{t / 3600.0:.3f}h" for t in grid]
    return DatasetSpec(
        name="ECG_NSR001_RR",
        unit="10s RR ms",
        dates=labels,
        values=values.astype(float),
        home_period=512.0,
        rungs_k=[4, 5, 6, 7, 8, 9, 10],
        horizons=[6, 30, 180, 360, 720],
        min_train=60,
        anchor_stride=20,
        origin_stride=60,
        start_index_floor=0,
    )


def run_dataset(spec: DatasetSpec):
    values = np.asarray(spec.values, dtype=float)
    n = len(values)
    max_h = max(spec.horizons)
    max_period = max(float(spec.base**k) for k in spec.rungs_k)
    min_anchor = max(int(math.ceil(4.0 * max_period)), int(4 * max(spec.rungs_k)), 48)
    test_start = max(
        spec.start_index_floor,
        min_anchor + spec.min_train * spec.anchor_stride + max_h + 1,
    )
    if test_start >= n - max_h:
        test_start = max(min_anchor + max_h + 1, int(n * 0.70))

    base_anchors = list(range(min_anchor, n + 1, spec.anchor_stride))
    origins_by_h = {
        h: list(range(test_start, n - h + 1, spec.origin_stride))
        for h in spec.horizons
        if test_start < n - h + 1
    }

    needed = set(base_anchors)
    for h in spec.horizons:
        for a in base_anchors:
            if a + h <= n:
                needed.add(a + h)
        for origin in origins_by_h.get(h, []):
            needed.add(origin)
            if origin + h <= n:
                needed.add(origin + h)
    needed_anchors = sorted(a for a in needed if min_anchor <= a <= n)

    print(f"\n{spec.name}: n={n}, unit={spec.unit}", flush=True)
    print(
        f"  home={spec.home_period:g}, base={spec.base:g}, rungs={spec.rungs_k}, "
        f"min_anchor={min_anchor}, test_start={label_for(spec.dates, test_start)}",
        flush=True,
    )
    print(f"  building {len(needed_anchors)} causal geometry states...", flush=True)

    t0 = time.time()
    state_cache = {}
    for i, anchor in enumerate(needed_anchors, start=1):
        state_cache[anchor] = read_signal_state(values, anchor, spec)
        if i % 250 == 0:
            print(f"    states {i:4d}/{len(needed_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"    states {len(needed_anchors):4d}/{len(needed_anchors)} in {time.time() - t0:.1f}s", flush=True)

    decode_cache = {a: decode_signal_features(state, spec) for a, state in state_cache.items()}
    keys = sorted(next(iter(decode_cache.values())).keys())
    natural_cache = {
        h: {a: decode_signal_features(natural_advance_state(state_cache[a], h), spec) for a in needed_anchors}
        for h in spec.horizons
    }

    points = {model: {h: [] for h in spec.horizons} for model in MODEL_KEYS}
    coefficient_rows = {h: [] for h in spec.horizons}
    retro_rows = {h: [] for h in spec.horizons}

    for h in spec.horizons:
        origins = origins_by_h.get(h, [])
        for origin in origins:
            target_anchor = origin + h
            train_transition = [
                a for a in base_anchors
                if a + h < origin and a in decode_cache and a + h in decode_cache
            ]
            train_decoder = [a for a in base_anchors if a < origin and a in decode_cache]
            if len(train_transition) < spec.min_train or len(train_decoder) < spec.min_train:
                continue

            scale = build_scale(decode_cache, train_decoder, keys)
            train_distances = []
            train_frictions = []
            train_flows = []
            for s in train_transition:
                current_vec = vectorize(decode_cache[s], keys, scale)
                natural_vec = vectorize(natural_cache[h][s], keys, scale)
                future_vec = vectorize(decode_cache[s + h], keys, scale)
                alpha = best_scalar_flow(current_vec, natural_vec - current_vec, future_vec)
                ara = state_cache[s]["center_ara"]
                friction = clip(friction_from_flow(ara, alpha), FRICTION_MIN, FRICTION_MAX)
                train_distances.append(phi_distance(ara))
                train_frictions.append(friction)
                train_flows.append(clip(alpha, FLOW_MIN, FLOW_MAX))

            b_fit, k_fit = fit_bk(train_distances, train_frictions)
            b_pos, k_pos = fit_bk_constrained(train_distances, train_frictions, FRICTION_MIN)
            b_pi, k_pi = fit_bk_constrained(train_distances, train_frictions, 1.0 + PI_LEAK_ENERGY)
            mean_friction = float(np.mean(train_frictions))

            current_vec = vectorize(decode_cache[origin], keys, scale)
            natural_vec = vectorize(natural_cache[h][origin], keys, scale)
            future_vec = vectorize(decode_cache[target_anchor], keys, scale)
            retro_flow = best_scalar_flow(current_vec, natural_vec - current_vec, future_vec)
            ara = state_cache[origin]["center_ara"]
            dist = phi_distance(ara)
            retro_friction = clip(friction_from_flow(ara, retro_flow), FRICTION_MIN, FRICTION_MAX)
            retro_rows[h].append(
                {
                    "origin": label_for(spec.dates, origin),
                    "date": label_for(spec.dates, target_anchor),
                    "flow": float(retro_flow),
                    "friction": float(retro_friction),
                    "ara": float(ara),
                    "phi_distance": float(dist),
                }
            )

            learned_friction = clip(b_fit + k_fit * dist, FRICTION_MIN, FRICTION_MAX)
            positive_friction = clip(b_pos + k_pos * dist, FRICTION_MIN, FRICTION_MAX)
            pi_floor_friction = clip(b_pi + k_pi * dist, FRICTION_MIN, FRICTION_MAX)
            fixed_phi_friction = 1.0 + dist
            fixed_pi_phi_friction = 1.0 + PI_LEAK_ENERGY + dist
            phi_flow = clip(1.0 - PHI ** (-float(h) / max(spec.home_period, 1e-12)), 0.0, 1.25)

            flow_values = {
                "phi_flow_decoder": phi_flow,
                "friction1_decoder": flow_from_friction(ara, 1.0),
                "fixed_1_plus_phi_distance_decoder": flow_from_friction(ara, fixed_phi_friction),
                "fixed_1_plus_pi_leak_phi_distance_decoder": flow_from_friction(ara, fixed_pi_phi_friction),
                "mean_friction_decoder": flow_from_friction(ara, mean_friction),
                "learned_bk_phi_distance_decoder": flow_from_friction(ara, learned_friction),
                "positive_bk_phi_distance_decoder": flow_from_friction(ara, positive_friction),
                "one_plus_pi_floor_bk_decoder": flow_from_friction(ara, pi_floor_friction),
            }

            decoder = fit_ridge_model(
                [decode_cache[a] for a in train_decoder],
                [float(values[a - 1]) for a in train_decoder],
            )

            projected = {
                "current_decoder": decode_cache[origin],
                "natural_advance_decoder": natural_cache[h][origin],
            }
            for model, flow in flow_values.items():
                projected[model] = blend_features(decode_cache[origin], natural_cache[h][origin], flow, keys)

            actual = float(values[target_anchor - 1])
            persistence = float(values[origin - 1])
            origin_date = label_for(spec.dates, origin)
            target_date = label_for(spec.dates, target_anchor)
            extras = {
                "ara": float(ara),
                "phi_distance": float(dist),
                "B": float(b_fit),
                "k": float(k_fit),
                "B_positive": float(b_pos),
                "k_positive": float(k_pos),
                "B_one_plus_pi_floor": float(b_pi),
                "k_one_plus_pi_floor": float(k_pi),
                "learned_friction": float(learned_friction),
                "positive_friction": float(positive_friction),
                "one_plus_pi_floor_friction": float(pi_floor_friction),
                "mean_friction": float(mean_friction),
                "retro_flow": float(retro_flow),
                "retro_friction": float(retro_friction),
            }

            for model, features in projected.items():
                pred = float(predict_ridge_model(decoder, features)[0])
                points[model][h].append(point(origin_date, target_date, pred, actual, persistence, extras))

            train_delta = [float(values[s + h - 1] - values[s - 1]) for s in train_transition]
            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(values, s) for s in train_transition],
                train_delta,
                lag_feature_dict(values, origin),
            )
            points["lag_ridge"][h].append(
                point(origin_date, target_date, persistence + lag_delta, actual, persistence, extras)
            )

            coefficient_rows[h].append(
                {
                    "origin": origin_date,
                    "date": target_date,
                    "B": float(b_fit),
                    "k": float(k_fit),
                    "B_positive": float(b_pos),
                    "k_positive": float(k_pos),
                    "B_one_plus_pi_floor": float(b_pi),
                    "k_one_plus_pi_floor": float(k_pi),
                    "B_minus_1": float(b_fit - 1.0),
                    "B_minus_1_plus_pi_leak": float(b_fit - (1.0 + PI_LEAK_ENERGY)),
                    "train_mean_friction": float(mean_friction),
                    "train_mean_flow": float(np.mean(train_flows)),
                    "ara": float(ara),
                    "phi_distance": float(dist),
                    "learned_friction": float(learned_friction),
                    "positive_friction": float(positive_friction),
                    "one_plus_pi_floor_friction": float(pi_floor_friction),
                    "retro_friction": float(retro_friction),
                }
            )

        print(f"  h={h:>4} {spec.unit}", flush=True)
        for model in MODEL_KEYS:
            print(f"    {model:43s} {format_score(score_points(points[model][h]))}", flush=True)

    scores = {model: {str(h): score_points(points[model][h]) for h in spec.horizons} for model in MODEL_KEYS}
    coefficient_summary = {}
    retro_summary = {}
    for h in spec.horizons:
        rows = coefficient_rows[h]
        coefficient_summary[str(h)] = {
            "B": summarize([r["B"] for r in rows]),
            "k": summarize([r["k"] for r in rows]),
            "B_positive": summarize([r["B_positive"] for r in rows]),
            "k_positive": summarize([r["k_positive"] for r in rows]),
            "B_one_plus_pi_floor": summarize([r["B_one_plus_pi_floor"] for r in rows]),
            "k_one_plus_pi_floor": summarize([r["k_one_plus_pi_floor"] for r in rows]),
            "B_minus_1": summarize([r["B_minus_1"] for r in rows]),
            "B_minus_1_plus_pi_leak": summarize([r["B_minus_1_plus_pi_leak"] for r in rows]),
            "learned_friction": summarize([r["learned_friction"] for r in rows]),
            "positive_friction": summarize([r["positive_friction"] for r in rows]),
            "one_plus_pi_floor_friction": summarize([r["one_plus_pi_floor_friction"] for r in rows]),
            "train_mean_friction": summarize([r["train_mean_friction"] for r in rows]),
            "phi_distance": summarize([r["phi_distance"] for r in rows]),
            "corr_retro_friction_phi_distance": corr(
                [r["friction"] for r in retro_rows[h]],
                [r["phi_distance"] for r in retro_rows[h]],
            ),
        }
        retro_summary[str(h)] = {
            "flow": summarize([r["flow"] for r in retro_rows[h]]),
            "friction": summarize([r["friction"] for r in retro_rows[h]]),
            "phi_distance": summarize([r["phi_distance"] for r in retro_rows[h]]),
            "corr_friction_phi_distance": coefficient_summary[str(h)]["corr_retro_friction_phi_distance"],
        }

    return {
        "config": {
            "name": spec.name,
            "unit": spec.unit,
            "n": int(n),
            "home_period": float(spec.home_period),
            "base": float(spec.base),
            "rungs_k": spec.rungs_k,
            "horizons": spec.horizons,
            "min_train": spec.min_train,
            "anchor_stride": spec.anchor_stride,
            "origin_stride": spec.origin_stride,
            "test_start": label_for(spec.dates, test_start),
            "min_anchor": int(min_anchor),
        },
        "scores": scores,
        "coefficient_summary": coefficient_summary,
        "retro_summary": retro_summary,
        "coefficients": coefficient_rows,
        "retro_rows": retro_rows,
        "points": points,
    }


def run():
    started = time.time()
    print("ARA phi-distance B+k temporal-friction fit", flush=True)
    print("=" * 100, flush=True)
    print(f"phi={PHI:.9f}; phi-1={PHI - 1.0:.9f}", flush=True)
    print(f"pi-leak energy=(pi-3)/pi={PI_LEAK_ENERGY:.9f}; topology pi-3={PI_LEAK_TOPOLOGY:.9f}", flush=True)
    print("No future leakage: B,k train on completed windows only; decoder trains on past anchors only.", flush=True)

    specs = [load_enso(), load_solar(), load_ecg_rr()]
    datasets = {}
    for spec in specs:
        datasets[spec.name] = run_dataset(spec)

    out = {
        "method": "strict-causal single-signal temporal friction fit: B + k*abs(ARA-phi)",
        "phi": PHI,
        "phi_minus_1": PHI - 1.0,
        "pi_leak_energy": PI_LEAK_ENERGY,
        "pi_leak_topology": PI_LEAK_TOPOLOGY,
        "datasets": datasets,
        "elapsed_seconds": time.time() - started,
    }
    out_path = HERE / "ara_phi_distance_bk_fit_data.js"
    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_PHI_DISTANCE_BK_FIT = ")
        json.dump(clean_for_json(out), f, indent=2)
        f.write(";\n")

    print("\nCoefficient stability summary", flush=True)
    print("-" * 100, flush=True)
    for name, result in datasets.items():
        print(name, flush=True)
        for h, summary in result["coefficient_summary"].items():
            b = summary["B"]
            k = summary["k"]
            bp = summary["B_positive"]
            kp = summary["k_positive"]
            bpi = summary["B_one_plus_pi_floor"]
            kpi = summary["k_one_plus_pi_floor"]
            corr_fd = summary["corr_retro_friction_phi_distance"]
            if b.get("n", 0) == 0:
                print(f"  h={h:>4}: no scored origins", flush=True)
                continue
            print(
                f"  h={h:>4}: B={b['mean']:.3f}±{b['std']:.3f} "
                f"k={k['mean']:.3f}±{k['std']:.3f} "
                f"posB={bp['mean']:.3f}/posK={kp['mean']:.3f} "
                f"piFloorB={bpi['mean']:.3f}/piFloorK={kpi['mean']:.3f} "
                f"B-(1+piLeak)={summary['B_minus_1_plus_pi_leak']['mean']:+.3f} "
                f"retro corr(friction, phiDist)={corr_fd:+.3f}",
                flush=True,
            )

    print(f"\nWrote {out_path}", flush=True)
    print(f"Done in {time.time() - started:.1f}s", flush=True)


if __name__ == "__main__":
    run()
