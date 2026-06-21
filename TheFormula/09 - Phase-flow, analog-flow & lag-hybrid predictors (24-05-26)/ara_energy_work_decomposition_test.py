"""
ara_energy_work_decomposition_test.py

Strict-causal diagnostic for the current decomposition:

    ARA geometry / phase-flow = route, timing, turn topology
    lag ridge = carried energy / inertia memory
    work = how energy is converted into motion along the route

The main hypothesis tested here is alignment:

    alignment = sign(energy_momentum) == sign(geometry_flow)

If energy and geometry agree, movement should be cleaner.  If they oppose,
the result should look more turbulent: stalls, whipsaws, delayed turns,
overshoots, undershoots, and false boundary signals.

Leakage guard:

  - Base lag and phase predictions are generated with strict-causal training
    pairs s+h<t via ara_lag_phase_hybrid_predictor.py.
  - All decomposition features are measured at origin t or earlier.
  - The causal error selector only uses previous records whose target is
    already known: target_anchor < origin_anchor.
  - Feature/target correlations are diagnostic summaries, not forecast inputs.
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

from ara_geometry_analog_flow_predictor import compact_state_features
from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import (
    BASE,
    HOME_PERIOD,
    HORIZONS,
    RUNG_KS,
    START_YEAR,
    build_snapshot,
    clean_for_json,
    load_enso_frame,
    score_points,
    zscore_columns,
)
from ara_lag_phase_hybrid_predictor import (
    MIN_FLOW_TRAIN,
    ORIGIN_STRIDE,
    enso_class,
    extended_score,
    finite,
    format_score,
    point,
    predict_components_for_origin,
)
from ara_phase_flow_predictor import PHASE_KEYS, phase_clean_input, phase_velocity_input


OUT_JSON = HERE / "ara_energy_work_decomposition_result.json"
OUT_JS = HERE / "ara_energy_work_decomposition_result.js"

MIN_CAUSAL_ERROR_TRAIN = 45
RIDGE_ALPHA_ERROR = 10.0
EPS = 1e-9


def rounded(value, digits=6):
    if value is None:
        return None
    return round(finite(value), digits)


def sign(value):
    value = finite(value)
    if value > EPS:
        return 1
    if value < -EPS:
        return -1
    return 0


def phase_angle(cache, anchor, prefix):
    return math.atan2(
        finite(cache[anchor].get(f"{prefix}_phase_sin", 0.0)),
        finite(cache[anchor].get(f"{prefix}_phase_cos", 1.0)),
    )


def angle_diff(a, b):
    return math.atan2(math.sin(a - b), math.cos(a - b))


def phase_velocity(cache, anchor, prefix, lag):
    prior = anchor - int(lag)
    if prior not in cache:
        return 0.0
    return angle_diff(phase_angle(cache, anchor, prefix), phase_angle(cache, prior, prefix)) / float(lag)


def phase_curvature(cache, anchor, prefix, lag=3):
    lag = int(lag)
    a0 = anchor
    a1 = anchor - lag
    a2 = anchor - 2 * lag
    if a1 not in cache or a2 not in cache:
        return 0.0
    v_now = angle_diff(phase_angle(cache, a0, prefix), phase_angle(cache, a1, prefix)) / float(lag)
    v_prev = angle_diff(phase_angle(cache, a1, prefix), phase_angle(cache, a2, prefix)) / float(lag)
    return v_now - v_prev


def delta_value(values, anchor, lag):
    idx = anchor - 1
    prior = idx - int(lag)
    if prior < 0:
        return 0.0
    return finite(values[idx] - values[prior])


def accel_value(values, anchor, lag):
    idx = anchor - 1
    lag = int(lag)
    i1 = idx - lag
    i2 = idx - 2 * lag
    if i1 < 0 or i2 < 0:
        return 0.0
    return finite(values[idx] - 2.0 * values[i1] + values[i2])


def rolling_var(values, anchor, window):
    idx = anchor
    start = max(0, idx - int(window))
    segment = np.asarray(values[start:idx], dtype=float)
    return float(np.var(segment)) if len(segment) >= 3 else 0.0


def boundary_cross(pred, persistence):
    return enso_class(pred) != enso_class(persistence)


def actual_transition(record):
    return enso_class(record["actual"]) != enso_class(record["persistence"])


def direction_delta(record, key):
    return sign(record[key] - record["persistence"])


def actual_direction(record):
    return sign(record["actual"] - record["persistence"])


def direction_correct(record, key):
    return direction_delta(record, key) == actual_direction(record)


def abs_error(record, key):
    return abs(record[key] - record["actual"])


def amplitude_error(record, key):
    pred_delta = record[key] - record["persistence"]
    actual_delta = record["actual"] - record["persistence"]
    return abs(abs(pred_delta) - abs(actual_delta))


def overshoot_label(record, key):
    pred_delta = record[key] - record["persistence"]
    actual_delta = record["actual"] - record["persistence"]
    if sign(pred_delta) != sign(actual_delta):
        return "wrong_direction"
    pred_mag = abs(pred_delta)
    actual_mag = abs(actual_delta)
    if pred_mag > actual_mag * 1.15 + 0.05:
        return "overshoot"
    if pred_mag < actual_mag * 0.85 - 0.05:
        return "undershoot"
    return "matched"


def compact_delta(compact_cache, anchor, key, lag):
    prior = anchor - int(lag)
    if prior not in compact_cache:
        return 0.0
    return finite(compact_cache[anchor].get(key, 0.0)) - finite(compact_cache[prior].get(key, 0.0))


def regime_onehots(parts):
    out = {}
    for key, value in parts.items():
        out[f"regime_{key}_{value}"] = 1.0
    return out


def build_decomposition_features(record, compact_cache, series, origin, components, dates):
    compact = compact_cache[origin]
    nino_raw = series["NINO"]["raw"]
    nino_z = series["NINO"]["z"]
    soi_z = series["SOI"]["z"]
    pdo_z = series["PDO"]["z"]

    persistence = record["persistence"]
    lag_delta = record["lag_pred"] - persistence
    phase_delta = record["phase_pred"] - persistence
    energy_momentum = lag_delta
    geometry_flow = phase_delta
    raw_momentum_3 = delta_value(nino_raw, origin, 3)
    raw_momentum_12 = delta_value(nino_raw, origin, 12)
    amp_velocity_3 = abs(nino_raw[origin - 1]) - abs(nino_raw[max(0, origin - 1 - 3)])
    amp_velocity_12 = abs(nino_raw[origin - 1]) - abs(nino_raw[max(0, origin - 1 - 12)])

    alignment = 1.0 if sign(energy_momentum) == sign(geometry_flow) else 0.0
    raw_alignment = 1.0 if sign(raw_momentum_3) == sign(geometry_flow) else 0.0
    opposing = 1.0 if sign(energy_momentum) == -sign(geometry_flow) else 0.0
    agreement_strength = abs(lag_delta + phase_delta) / (abs(lag_delta) + abs(phase_delta) + EPS)
    disagreement_strength = abs(lag_delta - phase_delta)
    coupling_pressure = finite(compact.get("nino_soi_coupling_pressure", 0.0)) + finite(
        compact.get("nino_pdo_coupling_pressure", 0.0)
    )
    rolling_variance = rolling_var(nino_z, origin, 24)
    dissipation_proxy = disagreement_strength * (1.0 + coupling_pressure + rolling_variance)
    reservoir_proxy = (
        abs(finite(nino_raw[origin - 1]))
        + rolling_var(nino_z, origin, 12)
        + finite(compact.get("nino_amplitude_energy_log", 0.0))
    )

    month = dates[origin - 1].month
    season_angle = 2.0 * math.pi * (month - 1) / 12.0

    parts = components.get("regime_info", {}).get("parts", {})
    out = {
        # Geometry.
        "geometry_phase_flow_prediction": phase_delta,
        "geometry_phase_abs_flow": abs(phase_delta),
        "geometry_nino_phase_velocity_1": phase_velocity(compact_cache, origin, "nino", 1),
        "geometry_nino_phase_velocity_3": phase_velocity(compact_cache, origin, "nino", 3),
        "geometry_nino_phase_velocity_12": phase_velocity(compact_cache, origin, "nino", 12),
        "geometry_soi_phase_velocity_3": phase_velocity(compact_cache, origin, "soi", 3),
        "geometry_nino_phase_curvature_3": phase_curvature(compact_cache, origin, "nino", 3),
        "geometry_soi_phase_curvature_3": phase_curvature(compact_cache, origin, "soi", 3),
        "geometry_boundary_distance_phi": finite(compact.get("nino_boundary_distance_phi", 0.0)),
        "geometry_boundary_distance_balance": finite(compact.get("nino_boundary_distance_balance", 0.0)),
        "geometry_boundary_distance_time": finite(compact.get("nino_boundary_distance_time", 0.0)),
        "geometry_boundary_velocity_phi_3": compact_delta(compact_cache, origin, "nino_boundary_distance_phi", 3),
        "geometry_boundary_velocity_phi_12": compact_delta(compact_cache, origin, "nino_boundary_distance_phi", 12),
        "geometry_partner_phase_gap": finite(compact.get("nino_soi_partner_phase_gap", 0.0)),
        "geometry_counterbalance_gate": finite(compact.get("enso_counterbalance_gate", 0.0)),
        "geometry_feeder_pressure": finite(compact.get("enso_feeder_pressure", 0.0)),
        # Energy.
        "energy_lag_prediction": record["lag_pred"],
        "energy_lag_delta": lag_delta,
        "energy_raw_amplitude": abs(finite(nino_raw[origin - 1])),
        "energy_raw_momentum_3": raw_momentum_3,
        "energy_raw_momentum_12": raw_momentum_12,
        "energy_amplitude_velocity_3": amp_velocity_3,
        "energy_amplitude_velocity_12": amp_velocity_12,
        "energy_amplitude_acceleration_3": accel_value(nino_raw, origin, 3),
        "energy_rolling_variance_12": rolling_var(nino_z, origin, 12),
        "energy_rolling_variance_24": rolling_variance,
        "energy_reservoir_proxy": reservoir_proxy,
        "energy_soi_momentum_3": delta_value(soi_z, origin, 3),
        "energy_pdo_momentum_12": delta_value(pdo_z, origin, 12),
        "season_sin": math.sin(season_angle),
        "season_cos": math.cos(season_angle),
        # Work.
        "work_alignment_lag_phase": alignment,
        "work_alignment_raw_phase": raw_alignment,
        "work_opposition_lag_phase": opposing,
        "work_agreement_strength": agreement_strength,
        "work_disagreement_strength": disagreement_strength,
        "work_energy_aligned_with_phase": abs(energy_momentum) if alignment else 0.0,
        "work_energy_opposing_phase": abs(energy_momentum) if opposing else 0.0,
        "work_raw_energy_aligned_with_phase": abs(raw_momentum_3) if raw_alignment else 0.0,
        "work_raw_energy_opposing_phase": abs(raw_momentum_3) if not raw_alignment else 0.0,
        "work_coupling_pressure": coupling_pressure,
        "work_dissipation_proxy": dissipation_proxy,
        "work_turbulence_proxy": opposing * (1.0 + dissipation_proxy),
    }
    out.update(regime_onehots(parts))
    return {key: finite(value) for key, value in out.items()}


def add_targets(record):
    for key in ["lag_pred", "phase_pred"]:
        prefix = "lag" if key == "lag_pred" else "phase"
        record[f"{prefix}_abs_error"] = abs_error(record, key)
        record[f"{prefix}_amplitude_error"] = amplitude_error(record, key)
        record[f"{prefix}_turn_success"] = direction_correct(record, key)
        record[f"{prefix}_turn_failure"] = not record[f"{prefix}_turn_success"]
        record[f"{prefix}_boundary_success"] = boundary_cross(record[key], record["persistence"]) == actual_transition(record)
        record[f"{prefix}_overshoot_label"] = overshoot_label(record, key)
    record["actual_transition"] = actual_transition(record)
    record["lag_phase_disagree"] = sign(record["lag_pred"] - record["persistence"]) != sign(
        record["phase_pred"] - record["persistence"]
    )
    record["lag_phase_aligned"] = not record["lag_phase_disagree"]
    record["lag_better_abs"] = record["lag_abs_error"] < record["phase_abs_error"]
    record["phase_better_abs"] = record["phase_abs_error"] < record["lag_abs_error"]


def points_from_records(records, key):
    return [point(r["origin_date"], r["target_date"], r[key], r["actual"], r["persistence"]) for r in records]


def subset_summary(records):
    if not records:
        return {
            "n": 0,
            "lag_mae": None,
            "phase_mae": None,
            "lag_turn_accuracy": None,
            "phase_turn_accuracy": None,
            "lag_boundary_accuracy": None,
            "phase_boundary_accuracy": None,
            "transition_rate": None,
            "lag_overshoot_rate": None,
            "lag_undershoot_rate": None,
            "lag_wrong_direction_rate": None,
            "phase_overshoot_rate": None,
            "phase_undershoot_rate": None,
            "phase_wrong_direction_rate": None,
            "mean_dissipation_proxy": None,
            "mean_turbulence_proxy": None,
        }
    return {
        "n": int(len(records)),
        "lag_mae": float(np.mean([r["lag_abs_error"] for r in records])),
        "phase_mae": float(np.mean([r["phase_abs_error"] for r in records])),
        "lag_turn_accuracy": float(np.mean([r["lag_turn_success"] for r in records])),
        "phase_turn_accuracy": float(np.mean([r["phase_turn_success"] for r in records])),
        "lag_boundary_accuracy": float(np.mean([r["lag_boundary_success"] for r in records])),
        "phase_boundary_accuracy": float(np.mean([r["phase_boundary_success"] for r in records])),
        "transition_rate": float(np.mean([r["actual_transition"] for r in records])),
        "lag_overshoot_rate": float(np.mean([r["lag_overshoot_label"] == "overshoot" for r in records])),
        "lag_undershoot_rate": float(np.mean([r["lag_overshoot_label"] == "undershoot" for r in records])),
        "lag_wrong_direction_rate": float(np.mean([r["lag_overshoot_label"] == "wrong_direction" for r in records])),
        "phase_overshoot_rate": float(np.mean([r["phase_overshoot_label"] == "overshoot" for r in records])),
        "phase_undershoot_rate": float(np.mean([r["phase_overshoot_label"] == "undershoot" for r in records])),
        "phase_wrong_direction_rate": float(np.mean([r["phase_overshoot_label"] == "wrong_direction" for r in records])),
        "mean_dissipation_proxy": float(np.mean([r["features"].get("work_dissipation_proxy", 0.0) for r in records])),
        "mean_turbulence_proxy": float(np.mean([r["features"].get("work_turbulence_proxy", 0.0) for r in records])),
    }


def causal_error_selector(records):
    """Past-only selector that predicts whether lag or phase should have lower MAE."""
    for record in records:
        past = [r for r in records if r["target_anchor"] < record["origin_anchor"]]
        if len(past) < MIN_CAUSAL_ERROR_TRAIN:
            record["work_selector_pred"] = record["lag_pred"]
            record["work_selector_choice"] = "lag_fallback"
            continue

        rows = [r["features"] for r in past]
        lag_y = [r["lag_abs_error"] for r in past]
        phase_y = [r["phase_abs_error"] for r in past]
        lag_model = fit_ridge_model(rows, lag_y, alpha=RIDGE_ALPHA_ERROR)
        phase_model = fit_ridge_model(rows, phase_y, alpha=RIDGE_ALPHA_ERROR)
        lag_expected = float(predict_ridge_model(lag_model, record["features"])[0])
        phase_expected = float(predict_ridge_model(phase_model, record["features"])[0])
        record["expected_lag_error"] = lag_expected
        record["expected_phase_error"] = phase_expected
        if phase_expected + 0.02 < lag_expected:
            record["work_selector_pred"] = record["phase_pred"]
            record["work_selector_choice"] = "phase"
        else:
            record["work_selector_pred"] = record["lag_pred"]
            record["work_selector_choice"] = "lag"


def feature_correlations(records, target_key, top_n=12):
    if len(records) < 12:
        return []
    feature_keys = sorted({key for r in records for key in r["features"].keys()})
    y = np.asarray([finite(r[target_key]) for r in records], dtype=float)
    if y.std() <= EPS:
        return []
    rows = []
    for key in feature_keys:
        x = np.asarray([finite(r["features"].get(key, 0.0)) for r in records], dtype=float)
        if x.std() <= EPS:
            continue
        corr = float(np.corrcoef(x, y)[0, 1])
        if math.isfinite(corr):
            rows.append({"feature": key, "corr": corr, "abs_corr": abs(corr)})
    rows.sort(key=lambda item: item["abs_corr"], reverse=True)
    return rows[:top_n]


def aggregate_metric(summaries, key):
    vals = [s[key] for s in summaries if s.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def aggregate_subsets(subsets_by_h, horizons):
    out = {}
    subset_names = sorted(next(iter(subsets_by_h.values())).keys())
    for subset in subset_names:
        selected = [subsets_by_h[str(h)][subset] for h in horizons]
        out[subset] = {}
        for key in selected[0].keys():
            if key == "n":
                out[subset][key] = int(sum(s[key] for s in selected))
            else:
                out[subset][key] = aggregate_metric(selected, key)
    return out


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = zscore_columns(frame)
    nino_raw = series["NINO"]["raw"]
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = max(4 * max(RUNG_KS), int(4 * BASE ** max(RUNG_KS)), 48)
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + MIN_FLOW_TRAIN + max_h + 1)
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA energy/work decomposition test")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("diagnostic: route geometry + carried energy -> effective work / turbulence")
    print("strict guards: base s+h<t; error selector uses target<t")
    print()

    compact_cache = {}
    phase_cache = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        compact = compact_state_features(build_snapshot(series, anchor))
        compact_cache[anchor] = compact
        phase_cache[anchor] = {key: finite(compact.get(key, 0.0)) for key in PHASE_KEYS}
        if i % 100 == 0:
            print(f"  cached states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    clean_inputs = {anchor: phase_clean_input(phase_cache, anchor) for anchor in all_anchors}
    velocity_inputs = {anchor: phase_velocity_input(compact_cache, phase_cache, anchor) for anchor in all_anchors}

    records_by_h = {}
    points_by_model = {"lag_ridge": {}, "ara_phase": {}, "work_error_selector": {}}

    for h in HORIZONS:
        records = []
        origins = list(range(test_start, n - h + 1, ORIGIN_STRIDE))
        for origin in origins:
            target_anchor = origin + h
            if target_anchor > n:
                continue
            train_transition = [s for s in all_anchors if s + h < origin]
            decoder_anchors = [a for a in all_anchors if a < origin]
            if len(train_transition) < MIN_FLOW_TRAIN or len(decoder_anchors) < MIN_FLOW_TRAIN:
                continue
            components = predict_components_for_origin(
                origin,
                h,
                train_transition,
                decoder_anchors,
                compact_cache,
                phase_cache,
                clean_inputs,
                velocity_inputs,
                series,
                nino_raw,
            )
            if components is None:
                continue
            actual = float(nino_raw[target_anchor - 1])
            record = {
                "horizon": int(h),
                "origin_anchor": int(origin),
                "target_anchor": int(target_anchor),
                "origin_date": dates[origin - 1].strftime("%Y-%m-%d"),
                "target_date": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                "persistence": float(components["persistence"]),
                "actual": actual,
                "lag_pred": float(components["lag_pred"]),
                "phase_pred": float(components["regime_velocity_phase_pred"]),
            }
            record["features"] = build_decomposition_features(record, compact_cache, series, origin, components, dates)
            add_targets(record)
            records.append(record)

        causal_error_selector(records)
        for record in records:
            record["work_selector_abs_error"] = abs_error(record, "work_selector_pred")
            record["work_selector_turn_success"] = direction_correct(record, "work_selector_pred")

        records_by_h[str(h)] = records
        points_by_model["lag_ridge"][str(h)] = points_from_records(records, "lag_pred")
        points_by_model["ara_phase"][str(h)] = points_from_records(records, "phase_pred")
        points_by_model["work_error_selector"][str(h)] = points_from_records(records, "work_selector_pred")

        aligned = [r for r in records if r["features"]["work_alignment_lag_phase"] >= 0.5]
        opposing = [r for r in records if r["features"]["work_opposition_lag_phase"] >= 0.5]
        transitions = [r for r in records if r["actual_transition"]]
        print(f"h={h:>2} months")
        for model in points_by_model:
            print(f"  {model:24s} {format_score(extended_score(points_by_model[model][str(h)]))}")
        a = subset_summary(aligned)
        o = subset_summary(opposing)
        t = subset_summary(transitions)
        print(
            f"  aligned   n={a['n']:>2} lag_mae={a['lag_mae']:.3f} phase_mae={a['phase_mae']:.3f}"
            f" lag_turn={a['lag_turn_accuracy']:.3f} phase_turn={a['phase_turn_accuracy']:.3f}"
        )
        print(
            f"  opposing  n={o['n']:>2} lag_mae={o['lag_mae']:.3f} phase_mae={o['phase_mae']:.3f}"
            f" lag_turn={o['lag_turn_accuracy']:.3f} phase_turn={o['phase_turn_accuracy']:.3f}"
        )
        print(
            f"  transition n={t['n']:>2} lag_mae={t['lag_mae']:.3f} phase_mae={t['phase_mae']:.3f}"
            f" lag_bound={t['lag_boundary_accuracy']:.3f} phase_bound={t['phase_boundary_accuracy']:.3f}"
        )
        print()

    scores = {
        model: {h: extended_score(points_by_model[model][h]) for h in points_by_model[model]}
        for model in points_by_model
    }
    subsets_by_h = {}
    feature_corrs = {}
    for h, records in records_by_h.items():
        aligned = [r for r in records if r["features"]["work_alignment_lag_phase"] >= 0.5]
        opposing = [r for r in records if r["features"]["work_opposition_lag_phase"] >= 0.5]
        transitions = [r for r in records if r["actual_transition"]]
        high_diss = sorted(records, key=lambda r: r["features"]["work_dissipation_proxy"], reverse=True)
        high_diss = high_diss[: max(8, len(high_diss) // 4)]
        subsets_by_h[h] = {
            "all": subset_summary(records),
            "aligned": subset_summary(aligned),
            "opposing": subset_summary(opposing),
            "transition": subset_summary(transitions),
            "high_dissipation_top_quarter": subset_summary(high_diss),
        }
        feature_corrs[h] = {
            "lag_abs_error": feature_correlations(records, "lag_abs_error"),
            "lag_amplitude_error": feature_correlations(records, "lag_amplitude_error"),
            "lag_turn_failure": feature_correlations(records, "lag_turn_failure"),
            "lag_boundary_failure": feature_correlations(
                [{**r, "lag_boundary_failure": not r["lag_boundary_success"]} for r in records],
                "lag_boundary_failure",
            ),
        }

    focus_horizons = [6, 12, 24]
    focus_records = [r for h in focus_horizons for r in records_by_h[str(h)]]
    focus_subsets = aggregate_subsets(subsets_by_h, focus_horizons)
    focus_scores = {
        model: {
            key: float(np.mean([scores[model][str(h)][key] for h in focus_horizons]))
            for key in ["mae", "corr", "turn_accuracy", "enso_class_accuracy", "transition_mae"]
            if all(scores[model][str(h)].get(key) is not None for h in focus_horizons)
        }
        for model in points_by_model
    }
    focus_feature_corrs = {
        "lag_abs_error": feature_correlations(focus_records, "lag_abs_error", top_n=16),
        "lag_amplitude_error": feature_correlations(focus_records, "lag_amplitude_error", top_n=16),
        "lag_turn_failure": feature_correlations(focus_records, "lag_turn_failure", top_n=16),
        "lag_boundary_failure": feature_correlations(
            [{**r, "lag_boundary_failure": not r["lag_boundary_success"]} for r in focus_records],
            "lag_boundary_failure",
            top_n=16,
        ),
    }

    slim_examples = {
        h: [
            {
                "origin": r["origin_date"],
                "target": r["target_date"],
                "actual": rounded(r["actual"]),
                "persistence": rounded(r["persistence"]),
                "lag_pred": rounded(r["lag_pred"]),
                "phase_pred": rounded(r["phase_pred"]),
                "work_selector_pred": rounded(r["work_selector_pred"]),
                "lag_error": rounded(r["lag_abs_error"]),
                "phase_error": rounded(r["phase_abs_error"]),
                "lag_overshoot": r["lag_overshoot_label"],
                "phase_overshoot": r["phase_overshoot_label"],
                "aligned": bool(r["features"]["work_alignment_lag_phase"]),
                "opposing": bool(r["features"]["work_opposition_lag_phase"]),
                "dissipation_proxy": rounded(r["features"]["work_dissipation_proxy"]),
                "turbulence_proxy": rounded(r["features"]["work_turbulence_proxy"]),
                "selector_choice": r["work_selector_choice"],
            }
            for r in records[:10]
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal energy/work decomposition diagnostic",
        "leakage_guard": [
            "Base lag and phase predictions use strict-causal training pairs s+h<t.",
            "All decomposition features are measured at origin t or earlier.",
            "The causal error selector only uses records with target_anchor < origin_anchor.",
            "Feature/target correlations are retrospective diagnostics, not forecast inputs.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
        },
        "models": {
            "lag_ridge": "Native-unit lag/slope ridge energy prior.",
            "ara_phase": "Regime+velocity ARA phase-flow decoded to native units.",
            "work_error_selector": "Past-only error model chooses lag or phase by expected MAE from geometry/energy/work features.",
        },
        "scores": clean_for_json(scores),
        "focus_6_12_24_scores": clean_for_json(focus_scores),
        "subset_summaries": clean_for_json(subsets_by_h),
        "focus_6_12_24_subset_summary": clean_for_json(focus_subsets),
        "feature_correlations": clean_for_json(feature_corrs),
        "focus_6_12_24_feature_correlations": clean_for_json(focus_feature_corrs),
        "example_records": clean_for_json(slim_examples),
        "elapsed_seconds": rounded(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_ENERGY_WORK_DECOMPOSITION = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24 scores:")
    for model, score in focus_scores.items():
        print(
            f"  {model:24s}"
            f" MAE={score.get('mae', float('nan')):.3f}"
            f" corr={score.get('corr', float('nan')):+.3f}"
            f" turn={score.get('turn_accuracy', float('nan')):.3f}"
            f" trans_mae={score.get('transition_mae', float('nan')):.3f}"
        )
    print("Focus alignment summary:")
    for subset in ["aligned", "opposing", "transition", "high_dissipation_top_quarter"]:
        s = focus_subsets[subset]
        print(
            f"  {subset:28s} n={s['n']:>3}"
            f" lag_mae={s['lag_mae']:.3f} phase_mae={s['phase_mae']:.3f}"
            f" lag_turn={s['lag_turn_accuracy']:.3f} phase_turn={s['phase_turn_accuracy']:.3f}"
            f" lag_bound={s['lag_boundary_accuracy']:.3f} phase_bound={s['phase_boundary_accuracy']:.3f}"
        )
    print("Top focus correlations with lag_abs_error:")
    for row in focus_feature_corrs["lag_abs_error"][:8]:
        print(f"  {row['feature']:42s} corr={row['corr']:+.3f}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
