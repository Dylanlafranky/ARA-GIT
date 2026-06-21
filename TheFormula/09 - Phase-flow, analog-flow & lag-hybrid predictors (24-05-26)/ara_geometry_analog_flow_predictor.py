"""
ara_geometry_analog_flow_predictor.py

Strict-causal ENSO test of the analog-flow predictor architecture:

    raw signal
    -> causal ARA mapper
    -> geometry state S(t)
    -> similar-state search in ARA space
    -> averaged transition vector dS
    -> estimated future geometry S(t+h)
    -> causal decoder back into native NINO units

The key guardrail is separation:

  - The flow operator predicts geometry, not the raw value.
  - The decoder maps geometry states to native observations.
  - Direct current-geometry -> future-value regression is included only as a
    control so the test can tell us whether the two-stage architecture earns
    anything.

Leakage guard for origin t and horizon h:

  - Snapshot S(t) is built only from data[:t].
  - Analog library uses only anchors s where s+h < t.
  - Decoder training uses only already observed geometry anchors a < t.
  - The true future geometry S(t+h) is used only for the oracle diagnostic.
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
from ara_geometry_state_transition_test import decode_state_features, fit_ridge_model, predict_ridge_model
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


OUT_JSON = HERE / "ara_geometry_analog_flow_predictor_result.json"
OUT_JS = HERE / "ara_geometry_analog_flow_predictor_result.js"

ORIGIN_STRIDE = 3
K_NEIGHBORS = 32
RIDGE_ALPHA_DECODER = 5.0
RIDGE_ALPHA_DIRECT = 10.0
ANALOG_MIN_TRAIN = max(MIN_TRAIN, 120)
LOG_CONTROL_BASE = 1.7
LOG_CONTROL_KS = [4, 5, 6, 7, 8]

MODEL_KEYS = [
    "persistence",
    "analog_flow_decoder",
    "analog_direct_value_control",
    "direct_geometry_ridge_control",
    "raw_analog_baseline",
    "non_ara_log_flow_decoder",
    "lag_ridge",
    "shuffled_state_null",
    "oracle_actual_future_geometry_decoder",
]


def finite(value, fallback=0.0):
    try:
        value = float(value)
    except (TypeError, ValueError):
        return fallback
    return value if math.isfinite(value) else fallback


def round_float(value, digits=6):
    return round(finite(value), digits)


def phase_gap(a, b):
    d = abs((float(a) - float(b)) % 1.0)
    return min(d, 1.0 - d)


def phase_alignment(a, b):
    return math.cos(2.0 * math.pi * phase_gap(a, b))


def release_balance(subsystem):
    return sum((2.0 * finite(r.get("is_release"), 0.0) - 1.0) * finite(r.get("occupancy"), 0.0) for r in subsystem["rungs"])


def occupancy_entropy(subsystem):
    occ = np.asarray([max(0.0, finite(r.get("occupancy"), 0.0)) for r in subsystem["rungs"]], dtype=float)
    if occ.sum() <= 1e-12:
        return 0.0
    occ = occ / occ.sum()
    return float(-np.sum(occ * np.log(occ + 1e-12)) / max(math.log(len(occ)), 1e-12))


def regime_flags(ara):
    ara = finite(ara, 1.0)
    return {
        "space_edge": 1.0 if ara < 0.25 else 0.0,
        "accumulate_side": 1.0 if 0.25 <= ara < 1.0 else 0.0,
        "balance_engine": 1.0 if 1.0 <= ara < PHI else 0.0,
        "release_donor": 1.0 if PHI <= ara <= 2.0 else 0.0,
        "overflow": 1.0 if ara > 2.0 else 0.0,
    }


def compact_state_features(snapshot):
    """Minimal ARA state S(t), matching the proposed predictor vocabulary."""

    out = {}
    for name in ["NINO", "SOI", "PDO"]:
        subsystem = snapshot[name]
        prefix = name.lower()
        ara = finite(subsystem["center_ara"], 1.0)
        phase = finite(subsystem["center_phase"], 0.0)
        total_energy = max(0.0, finite(subsystem["total_energy"], 0.0))
        weighted_k = 0.0
        for rung in subsystem["rungs"]:
            weighted_k += finite(rung.get("k"), 0.0) * finite(rung.get("occupancy"), 0.0)

        out[f"{prefix}_phase_sin"] = math.sin(2.0 * math.pi * phase)
        out[f"{prefix}_phase_cos"] = math.cos(2.0 * math.pi * phase)
        out[f"{prefix}_ara_position"] = ara
        out[f"{prefix}_ara_bounded"] = min(2.0, max(0.0, ara))
        out[f"{prefix}_boundary_distance_space"] = abs(ara - 0.0)
        out[f"{prefix}_boundary_distance_quarter"] = abs(ara - 0.25)
        out[f"{prefix}_boundary_distance_balance"] = abs(ara - 1.0)
        out[f"{prefix}_boundary_distance_phi"] = abs(ara - PHI)
        out[f"{prefix}_boundary_distance_donor_wall"] = abs(ara - 1.75)
        out[f"{prefix}_boundary_distance_time"] = abs(ara - 2.0)
        out[f"{prefix}_orientation_release_balance"] = release_balance(subsystem)
        out[f"{prefix}_amplitude_energy_log"] = math.log1p(total_energy)
        out[f"{prefix}_rung_position"] = finite(subsystem["center_position"], 0.0)
        out[f"{prefix}_home_distance"] = abs(finite(subsystem["center_position"], 0.0) - finite(subsystem["home_position"], 0.0))
        out[f"{prefix}_weighted_k"] = weighted_k
        out[f"{prefix}_occupancy_entropy"] = occupancy_entropy(subsystem)
        for label, value in regime_flags(ara).items():
            out[f"{prefix}_regime_{label}"] = value

    for left_name, right_name in [("NINO", "SOI"), ("NINO", "PDO"), ("SOI", "PDO")]:
        left = snapshot[left_name]
        right = snapshot[right_name]
        prefix = f"{left_name.lower()}_{right_name.lower()}"
        align = phase_alignment(left["center_phase"], right["center_phase"])
        distance = abs(finite(left["center_position"], 0.0) - finite(right["center_position"], 0.0))
        ara_gap = abs(finite(left["center_ara"], 1.0) - finite(right["center_ara"], 1.0))
        energy_product = math.sqrt(max(0.0, finite(left["total_energy"], 0.0)) * max(0.0, finite(right["total_energy"], 0.0)))
        out[f"{prefix}_partner_phase_gap"] = phase_gap(left["center_phase"], right["center_phase"])
        out[f"{prefix}_partner_phase_alignment"] = align
        out[f"{prefix}_partner_antiphase_fit"] = (1.0 - align) / 2.0
        out[f"{prefix}_rung_distance"] = distance
        out[f"{prefix}_ara_gap"] = ara_gap
        out[f"{prefix}_coupling_energy_log"] = math.log1p(energy_product)
        out[f"{prefix}_coupling_pressure"] = energy_product * (1.0 - align) / (1.0 + distance + ara_gap)

    out["enso_feeder_pressure"] = out["nino_soi_coupling_pressure"] + out["nino_pdo_coupling_pressure"]
    out["enso_partner_gap"] = out["nino_soi_partner_phase_gap"]
    out["enso_counterbalance_gate"] = out["nino_soi_partner_antiphase_fit"] / (1.0 + out["nino_soi_ara_gap"])
    return {key: finite(value) for key, value in out.items()}


def wide_state_features(snapshot):
    out = decode_state_features(snapshot)
    for key, value in compact_state_features(snapshot).items():
        out[f"compact_{key}"] = value
    return {key: finite(value) for key, value in out.items()}


def raw_lag_state_features(series, anchor):
    out = {}
    for name in ["NINO", "SOI", "PDO"]:
        arr = series[name]["z"]
        current = float(arr[anchor - 1])
        prefix = name.lower()
        out[f"{prefix}_current"] = current
        for lag in [1, 2, 3, 6, 12, 24, 36, 48, 60]:
            idx = anchor - 1 - lag
            prior = float(arr[idx]) if idx >= 0 else current
            out[f"{prefix}_lag{lag}"] = prior
            out[f"{prefix}_delta{lag}"] = current - prior
    return out


def non_ara_log_state_features(series, anchor):
    """Same analog-flow shell, but with arbitrary log-band features and no ARA."""

    out = {}
    for name in ["NINO", "SOI", "PDO"]:
        arr = np.asarray(series[name]["z"], dtype=float)
        prefix = name.lower()
        total_energy = 0.0
        for k in LOG_CONTROL_KS:
            period = float(LOG_CONTROL_BASE**k)
            rprefix = f"{prefix}_logbase{LOG_CONTROL_BASE:.1f}_k{k}"
            if 4.0 * period > anchor:
                amp = 0.0
                theta = 0.0
            else:
                bp = causal_bandpass(arr[:anchor], period)
                rec = _measure_rung(bp, period, k)
                amp = finite(rec["amp"], 0.0) if rec is not None else 0.0
                theta = finite(rec["theta"], 0.0) if rec is not None else 0.0
            total_energy += amp * amp
            out[f"{rprefix}_amp"] = amp
            out[f"{rprefix}_phase_sin"] = math.sin(theta)
            out[f"{rprefix}_phase_cos"] = math.cos(theta)
            out[f"{rprefix}_component"] = amp * math.cos(theta)
        out[f"{prefix}_log_total_energy"] = math.log1p(total_energy)
    return {key: finite(value) for key, value in out.items()}


def cache_keys(cache, anchors):
    keys = set()
    for anchor in anchors:
        keys.update(cache[anchor].keys())
    return sorted(keys)


def matrix_from_cache(cache, anchors, keys):
    return np.asarray([[finite(cache[a].get(key, 0.0)) for key in keys] for a in anchors], dtype=float)


def vector_to_dict(vector, keys):
    return {key: finite(value) for key, value in zip(keys, vector)}


def feature_bounds(cache, anchors, keys):
    bounds = {}
    for key in keys:
        vals = np.asarray([finite(cache[a].get(key, 0.0), float("nan")) for a in anchors], dtype=float)
        vals = vals[np.isfinite(vals)]
        if len(vals) == 0:
            bounds[key] = (-1.0, 1.0)
            continue
        lo = float(np.percentile(vals, 1))
        hi = float(np.percentile(vals, 99))
        span = max(hi - lo, float(np.std(vals)), 1e-9)
        bounds[key] = (lo - 0.25 * span, hi + 0.25 * span)
    return bounds


def normalize_phase_pairs(features):
    out = dict(features)
    for key in list(out):
        if not key.endswith("_phase_sin"):
            continue
        base = key[: -len("_phase_sin")]
        cos_key = f"{base}_phase_cos"
        if cos_key not in out:
            continue
        sx = finite(out[key], 0.0)
        cx = finite(out[cos_key], 1.0)
        norm = math.hypot(sx, cx)
        if norm > 1e-9:
            out[key] = sx / norm
            out[cos_key] = cx / norm
    return out


def sanitize_features(features, bounds):
    out = {}
    for key, value in features.items():
        lo, hi = bounds.get(key, (-1e9, 1e9))
        out[key] = min(hi, max(lo, finite(value)))
    return normalize_phase_pairs(out)


def analog_weights(cache, train_anchors, origin, keys):
    train_matrix = matrix_from_cache(cache, train_anchors, keys)
    current = matrix_from_cache(cache, [origin], keys)[0]
    mean = train_matrix.mean(axis=0)
    std = train_matrix.std(axis=0)
    std[std < 1e-9] = 1.0
    train_z = (train_matrix - mean) / std
    current_z = (current - mean) / std
    distances = np.sqrt(np.mean((train_z - current_z) ** 2, axis=1))
    order = np.argsort(distances)
    take = order[: min(K_NEIGHBORS, len(order))]
    selected_distances = distances[take]
    tau = float(np.median(selected_distances)) if len(selected_distances) else 1.0
    tau = max(tau, 1e-9)
    weights = np.exp(-selected_distances / tau)
    if weights.sum() <= 1e-12:
        weights = np.ones(len(take), dtype=float)
    weights = weights / weights.sum()
    return {
        "indices": take,
        "anchors": [int(train_anchors[i]) for i in take],
        "weights": weights,
        "distances": selected_distances,
        "current_vector": current,
        "train_matrix": train_matrix,
    }


def analog_project_state(cache, train_anchors, origin, horizon, keys, bounds, shuffled=False):
    info = analog_weights(cache, train_anchors, origin, keys)
    current_matrix = info["train_matrix"]
    future_matrix = matrix_from_cache(cache, [a + horizon for a in train_anchors], keys)
    deltas = future_matrix - current_matrix
    if shuffled and len(deltas) > 1:
        deltas = np.roll(deltas, max(1, len(deltas) // 3), axis=0)
    selected_delta = deltas[info["indices"]]
    pred_vec = info["current_vector"] + np.average(selected_delta, axis=0, weights=info["weights"])
    pred = sanitize_features(vector_to_dict(pred_vec, keys), bounds)
    effective_n = 1.0 / float(np.sum(info["weights"] ** 2)) if len(info["weights"]) else 0.0
    return pred, {
        "neighbor_anchors": info["anchors"],
        "neighbor_weights": [float(x) for x in info["weights"]],
        "mean_neighbor_distance": float(np.mean(info["distances"])) if len(info["distances"]) else None,
        "effective_neighbors": effective_n,
    }


def weighted_quantiles(values, weights, quantiles):
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if len(values) == 0 or weights.sum() <= 1e-12:
        return {str(q): None for q in quantiles}
    order = np.argsort(values)
    values = values[order]
    weights = weights[order] / weights.sum()
    cdf = np.cumsum(weights)
    return {str(q): float(np.interp(q, cdf, values)) for q in quantiles}


def analog_direct_raw_prediction(cache, train_anchors, origin, horizon, keys, nino_raw):
    info = analog_weights(cache, train_anchors, origin, keys)
    deltas = np.asarray([nino_raw[a + horizon - 1] - nino_raw[a - 1] for a in train_anchors], dtype=float)
    selected_delta = deltas[info["indices"]]
    pred = float(nino_raw[origin - 1] + np.average(selected_delta, weights=info["weights"]))
    future_values = np.asarray([nino_raw[a + horizon - 1] for a in info["anchors"]], dtype=float)
    q = weighted_quantiles(future_values, info["weights"], [0.1, 0.5, 0.9])
    signed_deltas = future_values - np.asarray([nino_raw[a - 1] for a in info["anchors"]], dtype=float)
    drift = np.abs(signed_deltas) < 0.10
    extras = {
        "q10": q["0.1"],
        "q50": q["0.5"],
        "q90": q["0.9"],
        "p_build": float(np.sum(info["weights"][signed_deltas > 0.10])),
        "p_release": float(np.sum(info["weights"][signed_deltas < -0.10])),
        "p_drift": float(np.sum(info["weights"][drift])),
        "mean_neighbor_distance": float(np.mean(info["distances"])) if len(info["distances"]) else None,
        "effective_neighbors": 1.0 / float(np.sum(info["weights"] ** 2)) if len(info["weights"]) else 0.0,
    }
    return pred, extras


def point(origin_date, target_date, pred, actual, persistence, extras=None):
    out = {
        "origin": origin_date,
        "date": target_date,
        "pred": float(pred),
        "actual": float(actual),
        "persistence": float(persistence),
    }
    if extras:
        out.update({key: clean_for_json(value) for key, value in extras.items()})
    return out


def format_score(score):
    if "mae" not in score:
        return "n/a"
    return (
        f"MAE={score['mae']:.4f} vs pers={score['persistence_mae']:.4f} "
        f"lift={score['mae_lift_vs_persistence']:+.4f} corr={score['corr']:+.3f} "
        f"dir={score['direction']:.3f}"
    )


def best_forecasts(scores, horizon):
    rows = []
    for model in MODEL_KEYS:
        if model == "oracle_actual_future_geometry_decoder":
            continue
        score = scores[model][horizon]
        rows.append((score.get("mae", float("inf")), model))
    rows.sort()
    return rows[0][1]


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = zscore_columns(frame)
    nino_raw = series["NINO"]["raw"]
    n = len(frame)
    max_h = max(HORIZONS)
    max_log_period = LOG_CONTROL_BASE ** max(LOG_CONTROL_KS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), int(4 * max_log_period), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + ANALOG_MIN_TRAIN + max_h + 1)
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA geometry analog-flow predictor")
    print("=" * 104)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()}  n={n}")
    print(f"ARA base={BASE}, home_period={HOME_PERIOD} months, rungs={RUNG_KS}")
    print(f"test origins start: {dates[test_start - 1].date()}  stride={ORIGIN_STRIDE} months")
    print(f"analog neighbors={K_NEIGHBORS}; strict guard s+h<t")
    print()

    snapshots = {}
    compact_cache = {}
    wide_cache = {}
    raw_cache = {}
    log_cache = {}

    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        snap = build_snapshot(series, anchor)
        snapshots[anchor] = snap
        compact_cache[anchor] = compact_state_features(snap)
        wide_cache[anchor] = wide_state_features(snap)
        raw_cache[anchor] = raw_lag_state_features(series, anchor)
        log_cache[anchor] = non_ara_log_state_features(series, anchor)
        if i % 100 == 0:
            print(f"  cached states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    compact_keys = cache_keys(compact_cache, all_anchors)
    log_keys = cache_keys(log_cache, all_anchors)
    raw_keys = cache_keys(raw_cache, all_anchors)

    all_points = {model: {h: [] for h in HORIZONS} for model in MODEL_KEYS}

    for h in HORIZONS:
        origins = list(range(test_start, n - h + 1, ORIGIN_STRIDE))
        for origin in origins:
            target_anchor = origin + h
            if target_anchor > n:
                continue
            train_transition = [s for s in all_anchors if s + h < origin]
            train_decoder = [a for a in all_anchors if a < origin]
            if len(train_transition) < ANALOG_MIN_TRAIN or len(train_decoder) < ANALOG_MIN_TRAIN:
                continue

            actual = float(nino_raw[target_anchor - 1])
            persistence = float(nino_raw[origin - 1])
            origin_date = dates[origin - 1].strftime("%Y-%m-%d")
            target_date = dates[target_anchor - 1].strftime("%Y-%m-%d")

            all_points["persistence"][h].append(point(origin_date, target_date, persistence, actual, persistence))

            compact_bounds = feature_bounds(compact_cache, train_decoder, compact_keys)
            compact_decoder = fit_ridge_model(
                [compact_cache[a] for a in train_decoder],
                [float(nino_raw[a - 1]) for a in train_decoder],
                alpha=RIDGE_ALPHA_DECODER,
            )

            pred_state, analog_info = analog_project_state(
                compact_cache,
                train_transition,
                origin,
                h,
                compact_keys,
                compact_bounds,
                shuffled=False,
            )
            pred = float(predict_ridge_model(compact_decoder, pred_state)[0])
            direct_pred, distribution = analog_direct_raw_prediction(compact_cache, train_transition, origin, h, compact_keys, nino_raw)
            all_points["analog_flow_decoder"][h].append(
                point(
                    origin_date,
                    target_date,
                    pred,
                    actual,
                    persistence,
                    {
                        **distribution,
                        "mean_neighbor_distance": analog_info["mean_neighbor_distance"],
                        "effective_neighbors": analog_info["effective_neighbors"],
                    },
                )
            )
            all_points["analog_direct_value_control"][h].append(
                point(origin_date, target_date, direct_pred, actual, persistence, distribution)
            )

            shuffled_state, shuffled_info = analog_project_state(
                compact_cache,
                train_transition,
                origin,
                h,
                compact_keys,
                compact_bounds,
                shuffled=True,
            )
            shuffled_pred = float(predict_ridge_model(compact_decoder, shuffled_state)[0])
            all_points["shuffled_state_null"][h].append(
                point(
                    origin_date,
                    target_date,
                    shuffled_pred,
                    actual,
                    persistence,
                    {
                        "mean_neighbor_distance": shuffled_info["mean_neighbor_distance"],
                        "effective_neighbors": shuffled_info["effective_neighbors"],
                    },
                )
            )

            oracle_pred = float(predict_ridge_model(compact_decoder, compact_cache[target_anchor])[0])
            all_points["oracle_actual_future_geometry_decoder"][h].append(
                point(origin_date, target_date, oracle_pred, actual, persistence)
            )

            train_raw_delta = [float(nino_raw[s + h - 1] - nino_raw[s - 1]) for s in train_transition]
            direct_delta, _, _ = fit_predict_ridge(
                [compact_cache[s] for s in train_transition],
                train_raw_delta,
                compact_cache[origin],
                alpha=RIDGE_ALPHA_DIRECT,
            )
            all_points["direct_geometry_ridge_control"][h].append(
                point(origin_date, target_date, persistence + direct_delta, actual, persistence)
            )

            lag_delta, _, _ = fit_predict_ridge(
                [lag_feature_dict(series["NINO"]["z"], s) for s in train_transition],
                train_raw_delta,
                lag_feature_dict(series["NINO"]["z"], origin),
                alpha=RIDGE_ALPHA_DIRECT,
            )
            all_points["lag_ridge"][h].append(point(origin_date, target_date, persistence + lag_delta, actual, persistence))

            raw_pred, raw_dist = analog_direct_raw_prediction(raw_cache, train_transition, origin, h, raw_keys, nino_raw)
            all_points["raw_analog_baseline"][h].append(point(origin_date, target_date, raw_pred, actual, persistence, raw_dist))

            log_bounds = feature_bounds(log_cache, train_decoder, log_keys)
            log_decoder = fit_ridge_model(
                [log_cache[a] for a in train_decoder],
                [float(nino_raw[a - 1]) for a in train_decoder],
                alpha=RIDGE_ALPHA_DECODER,
            )
            pred_log_state, log_info = analog_project_state(
                log_cache,
                train_transition,
                origin,
                h,
                log_keys,
                log_bounds,
                shuffled=False,
            )
            log_pred = float(predict_ridge_model(log_decoder, pred_log_state)[0])
            all_points["non_ara_log_flow_decoder"][h].append(
                point(
                    origin_date,
                    target_date,
                    log_pred,
                    actual,
                    persistence,
                    {
                        "mean_neighbor_distance": log_info["mean_neighbor_distance"],
                        "effective_neighbors": log_info["effective_neighbors"],
                    },
                )
            )

        print(f"h={h:>2} months")
        for model in MODEL_KEYS:
            print(f"  {model:38s} {format_score(score_points(all_points[model][h]))}")
        print()

    scores = {model: {h: score_points(all_points[model][h]) for h in HORIZONS} for model in MODEL_KEYS}
    winners = {str(h): best_forecasts(scores, h) for h in HORIZONS}
    examples = {
        str(h): {model: all_points[model][h][:6] for model in MODEL_KEYS if all_points[model][h]}
        for h in HORIZONS
    }

    out = {
        "date": "2026-05-24",
        "method": "strict-causal ARA geometry analog-flow predictor",
        "architecture": [
            "raw signal",
            "ARA mapper",
            "geometry state S(t)",
            "similar-state search",
            "transition vector dS",
            "future geometry S(t+h)",
            "decoder",
            "forecast in native NINO units",
        ],
        "leakage_guard": [
            "Snapshots use only data[:t].",
            "Analog flow library uses only completed pairs s+h<t.",
            "Decoder training uses only observed geometry anchors a<t.",
            "Direct geometry-to-value regression is reported only as a control.",
            "Oracle future geometry decoder is diagnostic only and is excluded from winner selection.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "feeders": ["SOI", "PDO"],
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "rungs_k": RUNG_KS,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "analog_neighbors": K_NEIGHBORS,
        "ridge_alpha_decoder": RIDGE_ALPHA_DECODER,
        "ridge_alpha_direct_control": RIDGE_ALPHA_DIRECT,
        "non_ara_log_control": {
            "base": LOG_CONTROL_BASE,
            "ks": LOG_CONTROL_KS,
            "note": "Same analog-flow plus decoder shell, but arbitrary log-band amplitude/phase features and no ARA positions.",
        },
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
        },
        "models": {
            "persistence": "Current NINO value carried forward.",
            "analog_flow_decoder": "ARA state S(t) -> analog averaged dS -> estimated S(t+h) -> causal decoder.",
            "analog_direct_value_control": "Uses the same ARA-state neighbors, but directly averages their future raw value deltas.",
            "direct_geometry_ridge_control": "Direct current ARA geometry -> future raw value delta regression; included as the mushy control.",
            "raw_analog_baseline": "Similar-state search over raw NINO/SOI/PDO lag vectors, then direct future raw delta averaging.",
            "non_ara_log_flow_decoder": "Same analog-flow decoder architecture using arbitrary non-ARA log-band state features.",
            "lag_ridge": "Causal NINO lag/slope ridge baseline.",
            "shuffled_state_null": "ARA neighbor search with transition vectors deliberately mispaired by a deterministic roll.",
            "oracle_actual_future_geometry_decoder": "Diagnostic only: decode actual future ARA geometry.",
        },
        "scores": scores,
        "winners": winners,
        "example_points": examples,
        "elapsed_seconds": round_float(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_GEOMETRY_ANALOG_FLOW_PREDICTOR = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print("Winners:")
    for h in HORIZONS:
        print(f"  h={h:>2}: {winners[str(h)]}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
