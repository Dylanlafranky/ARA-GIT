"""
ara_tick_variable_recursion_test.py

Strict-causal universal test for the current hypothesis:

    data at t -> required formula variables at t
    required variables(t) -> required variables(t + tick)
    repeat ticks to horizon
    decode predicted variables(t + horizon) -> observed value

This is intentionally different from the older direct transport tests.  The
direct tests learned current geometry -> future value delta.  This script first
learns a one-tick transition for the required variables themselves, rolls those
variables forward recursively, then decodes the future variable state.

Leakage guard for origin t and horizon h:
  - variable snapshots at t use only data[:t]
  - one-tick transition training uses only completed pairs s+tick < t
  - value decoder training uses only snapshots a < t
  - direct controls use only completed windows s+h < t
  - actual future variables are used only for oracle/error diagnostics
"""

from __future__ import annotations

import json
import math
import re
import sys
import time
from functools import reduce
from math import gcd
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO_ROOT))

from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import clean_for_json, fit_predict_ridge, lag_feature_dict, score_points
from ara_phi_distance_bk_fit_test import (
    PHI,
    PI_LEAK_ENERGY,
    DatasetSpec,
    decode_signal_features,
    label_for,
    load_ecg_rr,
    load_enso,
    load_solar,
    read_signal_state,
)
from ara_triangle_amplitude_gate_test import add_triangle_breath_features, universal_triangle_features


RIDGE_ALPHA_VARIABLES = 25.0
RIDGE_ALPHA_DECODER = 5.0
RIDGE_ALPHA_DIRECT = 10.0

MODEL_KEYS = [
    "tick_variables_geometry_decoder",
    "tick_variables_energy_decoder",
    "horizon_variables_energy_decoder",
    "direct_value_required_variables",
    "lag_ridge",
]
ORACLE_KEY = "oracle_actual_future_variables_decoder"


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def format_score(score):
    if "mae" not in score:
        return "n/a"
    return (
        f"MAE={score['mae']:.4f} vs pers={score['persistence_mae']:.4f} "
        f"lift={score['mae_lift_vs_persistence']:+.4f} corr={score['corr']:+.3f} "
        f"dir={score['direction']:.3f}"
    )


def summarize(values):
    vals = np.asarray([finite(v, float("nan")) for v in values], dtype=float)
    vals = vals[np.isfinite(vals)]
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


def gcd_list(values):
    values = [int(v) for v in values if int(v) > 0]
    return reduce(gcd, values) if values else 1


def min_anchor_for(spec: DatasetSpec):
    max_period = max(float(spec.base**k) for k in spec.rungs_k)
    return max(int(math.ceil(4.0 * max_period)), int(4 * max(spec.rungs_k)), 48)


def with_prefix(prefix, features):
    return {f"{prefix}{key}": finite(value) for key, value in features.items()}


def recent_delta(values, anchor, lag):
    current_idx = anchor - 1
    previous_idx = current_idx - int(lag)
    if previous_idx < 0:
        return 0.0
    return float(values[current_idx] - values[previous_idx])


def energy_variables(state, values, anchor, tick, spec):
    arr = np.asarray(values, dtype=float)
    current = float(arr[anchor - 1])
    mean = finite(state.get("mean", np.mean(arr[:anchor])))
    std = max(finite(state.get("std", np.std(arr[:anchor]))), 1e-9)
    d1 = recent_delta(arr, anchor, 1)
    dt = recent_delta(arr, anchor, tick)
    d2t = recent_delta(arr, anchor, 2 * tick)
    total_energy = max(finite(state.get("total_energy", 0.0)), 0.0)
    amp_scale = math.sqrt(total_energy) + 1e-9
    return {
        "current_value": current,
        "history_mean": mean,
        "history_std": std,
        "system_offset_z": (current - mean) / std,
        "energy_in_delta_1_z": d1 / std,
        "energy_in_delta_tick_z": dt / std,
        "energy_in_delta_2tick_z": d2t / std,
        "energy_in_abs_1_z": abs(d1) / std,
        "energy_in_abs_tick_z": abs(dt) / std,
        "energy_in_abs_2tick_z": abs(d2t) / std,
        "energy_in_tick_per_amp": dt / amp_scale,
        "energy_in_abs_tick_per_amp": abs(dt) / amp_scale,
        "energy_in_direction": math.copysign(1.0, dt) if abs(dt) > 1e-12 else 0.0,
        "energy_in_release_product": (dt / std) * finite(state.get("center_ara", 1.0), 1.0),
        "temporal_friction_phi_distance": abs(finite(state.get("center_ara", 1.0), 1.0) - PHI),
        "pi_leak_energy": PI_LEAK_ENERGY,
        "tick_fraction_of_home": float(tick) / max(float(spec.home_period), 1e-12),
    }


def build_variable_caches(spec: DatasetSpec, anchors, tick):
    anchors = sorted(set(int(a) for a in anchors if 1 <= int(a) <= len(spec.values)))
    state_cache = {}
    triangle_cache = {}
    t0 = time.time()
    for i, anchor in enumerate(anchors, start=1):
        state = read_signal_state(spec.values, anchor, spec)
        state_cache[anchor] = state
        triangle_cache[anchor] = universal_triangle_features(state, spec)
        if i % 250 == 0:
            print(f"    states {i:4d}/{len(anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"    states {len(anchors):4d}/{len(anchors)} in {time.time() - t0:.1f}s", flush=True)

    add_triangle_breath_features(triangle_cache, spec)

    geometry_cache = {}
    energy_cache = {}
    for anchor in anchors:
        state = state_cache[anchor]
        geometry = {}
        geometry.update(decode_signal_features(state, spec))
        geometry.update(with_prefix("tri_", triangle_cache[anchor]))
        geometry = {key: finite(value) for key, value in geometry.items()}

        energy = dict(geometry)
        energy.update(with_prefix("energy_", energy_variables(state, spec.values, anchor, tick, spec)))
        energy = {key: finite(value) for key, value in energy.items()}

        geometry_cache[anchor] = geometry
        energy_cache[anchor] = energy

    return state_cache, geometry_cache, energy_cache


def key_bounds(cache, anchors, keys):
    bounds = {}
    for key in keys:
        vals = np.asarray([finite(cache[a].get(key, 0.0)) for a in anchors if a in cache], dtype=float)
        vals = vals[np.isfinite(vals)]
        if len(vals) == 0:
            bounds[key] = (-1.0, 1.0)
            continue
        lo = float(np.percentile(vals, 1))
        hi = float(np.percentile(vals, 99))
        span = max(hi - lo, float(np.std(vals)), 1e-9)
        bounds[key] = (lo - 0.25 * span, hi + 0.25 * span)
    return bounds


PHASE_PAIR_RE = re.compile(r"^(.*)_phase_(sin|cos)$")
RUNG_OCC_RE = re.compile(r"^k\d+_occupancy$")


def sanitize_features(features, keys, bounds, spec: DatasetSpec):
    out = {key: finite(features.get(key, 0.0)) for key in keys}

    for key in keys:
        lo, hi = bounds.get(key, (-1e6, 1e6))
        value = finite(out.get(key, 0.0))
        out[key] = min(hi, max(lo, value))

    occ_keys = [key for key in keys if RUNG_OCC_RE.match(key)]
    occ = np.asarray([max(0.0, finite(out.get(key, 0.0))) for key in occ_keys], dtype=float)
    if len(occ) and float(occ.sum()) > 1e-12:
        occ /= float(occ.sum())
        for key, value in zip(occ_keys, occ):
            out[key] = float(value)

    pair_roots = {}
    for key in keys:
        match = PHASE_PAIR_RE.match(key)
        if match:
            pair_roots.setdefault(match.group(1), set()).add(match.group(2))
    for root, parts in pair_roots.items():
        if "sin" not in parts or "cos" not in parts:
            continue
        skey = f"{root}_phase_sin"
        ckey = f"{root}_phase_cos"
        s = finite(out.get(skey, 0.0))
        c = finite(out.get(ckey, 1.0))
        norm = math.hypot(s, c)
        if norm > 1e-9:
            out[skey] = s / norm
            out[ckey] = c / norm

    for key in keys:
        if key.endswith("_ara") or key == "center_ara" or key == "home_ara" or key == "tri_center_ara":
            out[key] = min(4.0, max(0.05, finite(out.get(key, 1.0), 1.0)))
        elif key.endswith("_amp") or key == "total_energy" or key.endswith("_total_energy"):
            out[key] = max(0.0, finite(out.get(key, 0.0)))
        elif key.endswith("_is_release"):
            out[key] = 1.0 if finite(out.get(key, 0.0)) >= 0.5 else 0.0
        elif key.startswith("tri_") and (
            key.endswith("_edge")
            or key.endswith("_corner")
            or key.endswith("_occupancy")
            or key.endswith("_gate")
            or key.endswith("_pull")
        ):
            out[key] = min(3.0, max(-3.0, finite(out.get(key, 0.0))))
        elif key == "energy_history_std":
            out[key] = max(1e-9, finite(out.get(key, 1.0), 1.0))

    for k in spec.rungs_k:
        ara_key = f"k{k}_ara"
        pos_key = f"k{k}_position"
        if ara_key in out and pos_key in out:
            out[pos_key] = float(k) + finite(out.get(ara_key, 1.0), 1.0) / 2.0

    return out


def fit_tick_delta_model(cache, train_anchors, tick, keys, spec: DatasetSpec):
    train_x = []
    train_delta = []
    for anchor in train_anchors:
        if anchor not in cache or anchor + tick not in cache:
            continue
        train_x.append(cache[anchor])
        train_delta.append(
            [finite(cache[anchor + tick].get(key, 0.0)) - finite(cache[anchor].get(key, 0.0)) for key in keys]
        )
    model = fit_ridge_model(train_x, train_delta, alpha=RIDGE_ALPHA_VARIABLES)
    bounds = key_bounds(cache, train_anchors, keys)
    return {"model": model, "bounds": bounds, "keys": keys, "spec": spec}


def predict_tick(model_pack, features):
    model = model_pack["model"]
    keys = model_pack["keys"]
    pred_delta = predict_ridge_model(model, features)
    raw = {
        key: finite(features.get(key, 0.0)) + finite(delta)
        for key, delta in zip(keys, pred_delta)
    }
    return sanitize_features(raw, keys, model_pack["bounds"], model_pack["spec"])


def roll_variables(cache, origin, horizon, tick, model_pack):
    features = sanitize_features(cache[origin], model_pack["keys"], model_pack["bounds"], model_pack["spec"])
    steps = int(horizon // tick)
    for _ in range(steps):
        features = predict_tick(model_pack, features)
    return features


def state_feature_error(predicted, actual, train_cache, train_anchors, keys):
    if not actual:
        return None
    scales = {}
    for key in keys:
        vals = np.asarray([finite(train_cache[a].get(key, 0.0)) for a in train_anchors if a in train_cache], dtype=float)
        scale = float(np.std(vals)) if len(vals) else 1.0
        scales[key] = scale if scale > 1e-9 else 1.0
    diffs = [
        abs(finite(predicted.get(key, 0.0)) - finite(actual.get(key, 0.0))) / scales[key]
        for key in keys
    ]
    return float(np.mean(diffs)) if diffs else None


def make_point(origin, date, pred, actual, persistence, extras=None):
    out = {
        "origin": origin,
        "date": date,
        "pred": float(pred),
        "actual": float(actual),
        "persistence": float(persistence),
    }
    if extras:
        out.update(extras)
    return out


def run_dataset(spec: DatasetSpec):
    values = np.asarray(spec.values, dtype=float)
    n = len(values)
    tick = gcd_list(spec.horizons)
    max_h = max(spec.horizons)
    min_anchor = min_anchor_for(spec)
    test_start = max(
        spec.start_index_floor,
        min_anchor + spec.min_train * tick + max_h + 1,
    )
    if test_start >= n - max_h:
        test_start = max(min_anchor + spec.min_train * tick + max_h + 1, int(n * 0.70))

    base_anchors = list(range(min_anchor, n + 1, tick))
    origins_by_h = {
        h: list(range(test_start, n - h + 1, spec.origin_stride))
        for h in spec.horizons
        if h % tick == 0 and test_start < n - h + 1
    }

    needed = set(base_anchors)
    for h, origins in origins_by_h.items():
        needed.update(origins)
        needed.update(origin + h for origin in origins if origin + h <= n)
    needed = sorted(a for a in needed if min_anchor <= a <= n)

    print(f"\n{spec.name}: n={n}, unit={spec.unit}", flush=True)
    print(
        f"  tick={tick}, home={spec.home_period:g}, rungs={spec.rungs_k}, "
        f"min_anchor={min_anchor}, test_start={label_for(spec.dates, test_start)}",
        flush=True,
    )
    print(f"  building {len(needed)} causal variable states...", flush=True)

    _, geometry_cache, energy_cache = build_variable_caches(spec, needed, tick)
    geometry_keys = sorted({key for item in geometry_cache.values() for key in item})
    energy_keys = sorted({key for item in energy_cache.values() for key in item})

    points = {model: {str(h): [] for h in spec.horizons} for model in MODEL_KEYS + [ORACLE_KEY]}
    variable_errors = {
        "tick_variables_geometry_decoder": {str(h): [] for h in spec.horizons},
        "tick_variables_energy_decoder": {str(h): [] for h in spec.horizons},
        "horizon_variables_energy_decoder": {str(h): [] for h in spec.horizons},
    }
    origin_model_cache = {}

    def get_origin_models(origin):
        cached = origin_model_cache.get(origin)
        if cached is not None:
            return cached

        train_tick = [
            a for a in base_anchors
            if a + tick < origin and a in energy_cache and a + tick in energy_cache
        ]
        train_decoder = [a for a in base_anchors if a < origin and a in energy_cache]
        if len(train_tick) < spec.min_train or len(train_decoder) < spec.min_train:
            return None

        decoder_energy = fit_ridge_model(
            [energy_cache[a] for a in train_decoder],
            [float(values[a - 1]) for a in train_decoder],
            alpha=RIDGE_ALPHA_DECODER,
        )
        decoder_geometry = fit_ridge_model(
            [geometry_cache[a] for a in train_decoder],
            [float(values[a - 1]) for a in train_decoder],
            alpha=RIDGE_ALPHA_DECODER,
        )
        geom_tick_model = fit_tick_delta_model(geometry_cache, train_tick, tick, geometry_keys, spec)
        energy_tick_model = fit_tick_delta_model(energy_cache, train_tick, tick, energy_keys, spec)
        cached = {
            "train_tick": train_tick,
            "train_decoder": train_decoder,
            "decoder_energy": decoder_energy,
            "decoder_geometry": decoder_geometry,
            "geom_tick_model": geom_tick_model,
            "energy_tick_model": energy_tick_model,
            "energy_bounds": key_bounds(energy_cache, train_decoder, energy_keys),
        }
        origin_model_cache[origin] = cached
        return cached

    for h in spec.horizons:
        h_key = str(h)
        origins = origins_by_h.get(h, [])
        for origin in origins:
            target_anchor = origin + h
            train_horizon = [
                a for a in base_anchors
                if a + h < origin and a in energy_cache and a + h in energy_cache
            ]
            origin_models = get_origin_models(origin)
            if origin_models is None or len(train_horizon) < spec.min_train:
                continue
            train_decoder = origin_models["train_decoder"]

            actual = float(values[target_anchor - 1])
            persistence = float(values[origin - 1])
            origin_date = label_for(spec.dates, origin)
            target_date = label_for(spec.dates, target_anchor)

            geom_pred_vars = roll_variables(
                geometry_cache,
                origin,
                h,
                tick,
                origin_models["geom_tick_model"],
            )
            energy_pred_vars = roll_variables(
                energy_cache,
                origin,
                h,
                tick,
                origin_models["energy_tick_model"],
            )
            geom_pred = float(predict_ridge_model(origin_models["decoder_geometry"], geom_pred_vars)[0])
            energy_pred = float(predict_ridge_model(origin_models["decoder_energy"], energy_pred_vars)[0])

            common = {
                "tick": float(tick),
                "steps": int(h // tick),
                "origin_anchor": int(origin),
                "target_anchor": int(target_anchor),
            }
            points["tick_variables_geometry_decoder"][h_key].append(
                make_point(origin_date, target_date, geom_pred, actual, persistence, common)
            )
            points["tick_variables_energy_decoder"][h_key].append(
                make_point(origin_date, target_date, energy_pred, actual, persistence, common)
            )
            variable_errors["tick_variables_geometry_decoder"][h_key].append(
                state_feature_error(geom_pred_vars, geometry_cache.get(target_anchor), geometry_cache, train_decoder, geometry_keys)
            )
            variable_errors["tick_variables_energy_decoder"][h_key].append(
                state_feature_error(energy_pred_vars, energy_cache.get(target_anchor), energy_cache, train_decoder, energy_keys)
            )

            horizon_model = fit_ridge_model(
                [energy_cache[a] for a in train_horizon],
                [[finite(energy_cache[a + h].get(key, 0.0)) for key in energy_keys] for a in train_horizon],
                alpha=RIDGE_ALPHA_VARIABLES,
            )
            horizon_vec = predict_ridge_model(horizon_model, energy_cache[origin])
            horizon_vars = sanitize_features(
                {key: finite(value) for key, value in zip(energy_keys, horizon_vec)},
                energy_keys,
                origin_models["energy_bounds"],
                spec,
            )
            horizon_pred = float(predict_ridge_model(origin_models["decoder_energy"], horizon_vars)[0])
            points["horizon_variables_energy_decoder"][h_key].append(
                make_point(origin_date, target_date, horizon_pred, actual, persistence, common)
            )
            variable_errors["horizon_variables_energy_decoder"][h_key].append(
                state_feature_error(horizon_vars, energy_cache.get(target_anchor), energy_cache, train_decoder, energy_keys)
            )

            train_delta = [float(values[a + h - 1] - values[a - 1]) for a in train_horizon]
            direct_delta, _, _ = fit_predict_ridge(
                [energy_cache[a] for a in train_horizon],
                train_delta,
                energy_cache[origin],
                alpha=RIDGE_ALPHA_DIRECT,
            )
            points["direct_value_required_variables"][h_key].append(
                make_point(origin_date, target_date, persistence + direct_delta, actual, persistence, common)
            )

            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(values, a) for a in train_horizon],
                train_delta,
                lag_feature_dict(values, origin),
                alpha=RIDGE_ALPHA_DIRECT,
            )
            points["lag_ridge"][h_key].append(
                make_point(origin_date, target_date, persistence + lag_delta, actual, persistence, common)
            )

            oracle_pred = float(predict_ridge_model(origin_models["decoder_energy"], energy_cache[target_anchor])[0])
            points[ORACLE_KEY][h_key].append(
                make_point(origin_date, target_date, oracle_pred, actual, persistence, common)
            )

        print(f"  h={h:>4} {spec.unit}", flush=True)
        for model in MODEL_KEYS:
            print(f"    {model:38s} {format_score(score_points(points[model][h_key]))}", flush=True)
        oracle = score_points(points[ORACLE_KEY][h_key])
        print(f"    {ORACLE_KEY:38s} {format_score(oracle)}  diagnostic only", flush=True)

    scores = {model: {str(h): score_points(points[model][str(h)]) for h in spec.horizons} for model in MODEL_KEYS + [ORACLE_KEY]}
    for model, by_h in variable_errors.items():
        for h_key, rows in by_h.items():
            vals = [finite(v, float("nan")) for v in rows]
            vals = [v for v in vals if math.isfinite(v)]
            if h_key in scores[model]:
                scores[model][h_key]["mean_scaled_variable_error"] = float(np.mean(vals)) if vals else None

    winners = {}
    for h in spec.horizons:
        h_key = str(h)
        candidates = {model: scores[model][h_key].get("mae", float("inf")) for model in MODEL_KEYS}
        winners[h_key] = min(candidates, key=candidates.get) if candidates else None

    return {
        "config": {
            "name": spec.name,
            "unit": spec.unit,
            "n": int(n),
            "home_period": float(spec.home_period),
            "base": float(spec.base),
            "rungs_k": spec.rungs_k,
            "horizons": spec.horizons,
            "tick": int(tick),
            "min_train": int(spec.min_train),
            "origin_stride": int(spec.origin_stride),
            "test_start": label_for(spec.dates, test_start),
            "min_anchor": int(min_anchor),
            "geometry_variable_count": int(len(geometry_keys)),
            "energy_variable_count": int(len(energy_keys)),
        },
        "scores": scores,
        "winners": winners,
        "variable_error_summary": {
            model: {h: summarize(rows) for h, rows in by_h.items()}
            for model, by_h in variable_errors.items()
        },
        "points": points,
    }


def run(out_path=HERE / "ara_tick_variable_recursion_data.js"):
    started = time.time()
    print("ARA tick-variable recursion test", flush=True)
    print("=" * 100, flush=True)
    print(
        "No leakage: state data[:t], tick transitions s+tick<t, decoders a<t, controls s+h<t.",
        flush=True,
    )
    print(
        "This test predicts the required variables first, then decodes those predicted variables.",
        flush=True,
    )

    datasets = {}
    for spec in [load_enso(), load_solar(), load_ecg_rr()]:
        datasets[spec.name] = run_dataset(spec)

    out = {
        "date": "2026-05-23",
        "method": "strict-causal universal tick recursion over required ARA/formula variables",
        "hypothesis": (
            "Forecasting future geometry/energy variables one tick at a time should be a better match "
            "to the formula than directly regressing the observed value."
        ),
        "leakage_guard": (
            "At origin t, variable snapshots use only data[:t]; one-tick transition training uses only "
            "completed pairs s+tick<t; decoder training uses only a<t; direct controls use s+h<t; "
            "oracle future variables are diagnostic only."
        ),
        "models": {
            "tick_variables_geometry_decoder": "Roll geometry/topography variables forward by one-tick causal transitions, then decode.",
            "tick_variables_energy_decoder": "Same as geometry model plus current-level and incoming-energy variables.",
            "horizon_variables_energy_decoder": "Control: predict future variables in one horizon jump, then decode.",
            "direct_value_required_variables": "Control: current required variables directly regress future value delta.",
            "lag_ridge": "Control: causal raw-value lags and slopes directly regress future value delta.",
            ORACLE_KEY: "Diagnostic only: decode the actual future required variables using a causal decoder.",
        },
        "ridge_alpha_variables": RIDGE_ALPHA_VARIABLES,
        "ridge_alpha_decoder": RIDGE_ALPHA_DECODER,
        "ridge_alpha_direct": RIDGE_ALPHA_DIRECT,
        "datasets": datasets,
        "elapsed_seconds": time.time() - started,
    }

    with out_path.open("w", encoding="utf-8") as f:
        f.write("window.ARA_TICK_VARIABLE_RECURSION = ")
        json.dump(clean_for_json(out), f, indent=2, allow_nan=False)
        f.write(";\n")

    print("\nSummary", flush=True)
    print("-" * 100, flush=True)
    for name, data in datasets.items():
        print(name, flush=True)
        for h in data["config"]["horizons"]:
            h_key = str(h)
            winner = data["winners"].get(h_key)
            tick_score = data["scores"]["tick_variables_energy_decoder"].get(h_key, {})
            direct_score = data["scores"]["direct_value_required_variables"].get(h_key, {})
            lag_score = data["scores"]["lag_ridge"].get(h_key, {})
            oracle = data["scores"][ORACLE_KEY].get(h_key, {})
            print(
                f"  h={h:>4}: winner={winner} "
                f"tickEnergy MAE={tick_score.get('mae', float('nan')):.4f} "
                f"direct MAE={direct_score.get('mae', float('nan')):.4f} "
                f"lag MAE={lag_score.get('mae', float('nan')):.4f} "
                f"oracle MAE={oracle.get('mae', float('nan')):.4f}",
                flush=True,
            )
    print(f"\nWrote {out_path}", flush=True)
    print(f"Done in {time.time() - started:.1f}s", flush=True)


if __name__ == "__main__":
    run()
