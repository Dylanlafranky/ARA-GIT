"""
ara_transition_risk_and_uncertainty_model.py

Strict-causal risk layer on top of the lag/ARA decomposition.

This is intentionally not another point predictor.  It keeps:

    lag ridge = central native-unit forecast / carried energy
    ARA phase-flow = route, timing, boundary geometry

and asks whether geometry/work features can predict risk:

  - high lag absolute error
  - lag turn failure
  - future event/boundary state
  - ENSO class transition
  - forecast interval width around the lag forecast

Leakage guard:

  - Base lag and phase predictions use strict-causal training pairs s+h<t.
  - All risk inputs are known at origin t.
  - At origin t, risk/interval models train only on previous records whose
    target_anchor < t, so those outcomes would already be known.
  - High-error thresholds and interval calibration are estimated from that same
    past-only set for each origin.
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

from ara_energy_work_decomposition_test import (
    actual_transition,
    add_targets,
    build_decomposition_features,
    sign,
)
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


OUT_JSON = HERE / "ara_transition_risk_and_uncertainty_result.json"
OUT_JS = HERE / "ara_transition_risk_and_uncertainty_result.js"

MIN_RISK_TRAIN = 30
RIDGE_ALPHA_RISK = 8.0
RIDGE_ALPHA_INTERVAL = 10.0
HIGH_ERROR_QUANTILE = 0.75
INTERVAL_QUANTILE = 0.80
EPS = 1e-9

RISK_TARGETS = [
    "lag_abs_error_high",
    "lag_turn_failure",
    "boundary_crossing",
    "enso_class_transition",
]


def rounded(value, digits=6):
    if value is None:
        return None
    return round(finite(value), digits)


def clip_prob(value):
    return float(min(0.98, max(0.02, finite(value, 0.5))))


def future_boundary_state(record):
    """Future is in a named ENSO event state rather than neutral."""
    return enso_class(record["actual"]) != "neutral"


def build_risk_features(record):
    """Inputs known at origin t. Keep the layer interpretable."""
    f = record["features"]
    lag_delta = record["lag_pred"] - record["persistence"]
    phase_delta = record["phase_pred"] - record["persistence"]
    out = {
        "lag_prediction": record["lag_pred"],
        "lag_delta": lag_delta,
        "lag_delta_abs": abs(lag_delta),
        "phase_prediction": record["phase_pred"],
        "phase_delta": phase_delta,
        "phase_delta_abs": abs(phase_delta),
        "lag_phase_delta_gap": abs(lag_delta - phase_delta),
        "lag_phase_same_direction": 1.0 if sign(lag_delta) == sign(phase_delta) else 0.0,
        "lag_phase_opposed": 1.0 if sign(lag_delta) == -sign(phase_delta) else 0.0,
    }
    keep = [
        "work_alignment_lag_phase",
        "work_opposition_lag_phase",
        "work_agreement_strength",
        "work_disagreement_strength",
        "work_dissipation_proxy",
        "work_turbulence_proxy",
        "work_energy_aligned_with_phase",
        "work_energy_opposing_phase",
        "work_coupling_pressure",
        "geometry_boundary_distance_phi",
        "geometry_boundary_distance_balance",
        "geometry_boundary_distance_time",
        "geometry_boundary_velocity_phi_3",
        "geometry_boundary_velocity_phi_12",
        "geometry_nino_phase_velocity_1",
        "geometry_nino_phase_velocity_3",
        "geometry_nino_phase_velocity_12",
        "geometry_nino_phase_curvature_3",
        "geometry_partner_phase_gap",
        "geometry_counterbalance_gate",
        "geometry_feeder_pressure",
        "energy_raw_amplitude",
        "energy_raw_momentum_3",
        "energy_raw_momentum_12",
        "energy_amplitude_velocity_3",
        "energy_amplitude_velocity_12",
        "energy_amplitude_acceleration_3",
        "energy_rolling_variance_12",
        "energy_rolling_variance_24",
        "energy_reservoir_proxy",
        "energy_pdo_momentum_12",
        "season_sin",
        "season_cos",
        "regime_pdo_coupling_pdo_high",
        "regime_pdo_coupling_pdo_low",
        "regime_phase_gap_anti",
        "regime_phase_gap_mixed",
        "regime_phase_gap_same",
        "regime_boundary_motion_approach_phi",
        "regime_boundary_motion_retreat_phi",
        "regime_boundary_motion_boundary_flat",
    ]
    for key in keep:
        out[key] = finite(f.get(key, 0.0))
    return {key: finite(value) for key, value in out.items()}


def predict_probability(train_rows, train_y, row):
    if len(set(int(v) for v in train_y)) < 2:
        return float(np.mean(train_y)) if train_y else 0.5
    model = fit_ridge_model(train_rows, train_y, alpha=RIDGE_ALPHA_RISK)
    return clip_prob(float(predict_ridge_model(model, row)[0]))


def predict_interval_width(past, row):
    errors = np.asarray([r["lag_abs_error"] for r in past], dtype=float)
    baseline_width = float(np.quantile(errors, INTERVAL_QUANTILE))
    if len(past) < MIN_RISK_TRAIN or errors.std() <= EPS:
        return baseline_width, baseline_width

    rows = [r["risk_features"] for r in past]
    model = fit_ridge_model(rows, errors, alpha=RIDGE_ALPHA_INTERVAL)
    expected = max(0.03, float(predict_ridge_model(model, row)[0]))

    fitted = np.asarray([max(0.03, float(predict_ridge_model(model, r["risk_features"])[0])) for r in past], dtype=float)
    ratio = errors / np.maximum(fitted, 0.03)
    scale = float(np.quantile(ratio, INTERVAL_QUANTILE))
    width = expected * scale
    width = float(min(3.0, max(0.05, width)))
    return baseline_width, width


def auc_score(labels, scores):
    labels = np.asarray(labels, dtype=int)
    scores = np.asarray(scores, dtype=float)
    pos = int(np.sum(labels == 1))
    neg = int(np.sum(labels == 0))
    if pos == 0 or neg == 0:
        return None
    order = np.argsort(scores)
    ranks = np.empty_like(order, dtype=float)
    i = 0
    while i < len(scores):
        j = i
        while j + 1 < len(scores) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        ranks[order[i : j + 1]] = avg_rank
        i = j + 1
    rank_sum_pos = float(np.sum(ranks[labels == 1]))
    return (rank_sum_pos - pos * (pos + 1) / 2.0) / (pos * neg)


def risk_metric(records, target):
    usable = [r for r in records if r.get("risk_ready") and f"prob_{target}" in r]
    if not usable:
        return {"n": 0}
    labels = np.asarray([int(r[target]) for r in usable], dtype=int)
    probs = np.asarray([finite(r[f"prob_{target}"], 0.5) for r in usable], dtype=float)
    event_rate = float(np.mean(labels))
    brier = float(np.mean((probs - labels) ** 2))
    auc = auc_score(labels, probs)
    cutoff_hi = float(np.quantile(probs, 0.75))
    cutoff_lo = float(np.quantile(probs, 0.25))
    top = labels[probs >= cutoff_hi]
    bottom = labels[probs <= cutoff_lo]
    top_rate = float(np.mean(top)) if len(top) else None
    bottom_rate = float(np.mean(bottom)) if len(bottom) else None
    return {
        "n": int(len(usable)),
        "event_rate": event_rate,
        "mean_probability": float(np.mean(probs)),
        "mean_probability_event": float(np.mean(probs[labels == 1])) if np.any(labels == 1) else None,
        "mean_probability_nonevent": float(np.mean(probs[labels == 0])) if np.any(labels == 0) else None,
        "brier": brier,
        "auc": auc,
        "top_quartile_event_rate": top_rate,
        "bottom_quartile_event_rate": bottom_rate,
        "top_vs_base_lift": top_rate / event_rate if top_rate is not None and event_rate > EPS else None,
        "top_vs_bottom_lift": top_rate / bottom_rate if top_rate is not None and bottom_rate is not None and bottom_rate > EPS else None,
    }


def interval_metrics(records):
    usable = [r for r in records if r.get("risk_ready")]
    if not usable:
        return {"n": 0}
    actual = np.asarray([r["actual"] for r in usable], dtype=float)
    pred = np.asarray([r["lag_pred"] for r in usable], dtype=float)
    base_w = np.asarray([r["baseline_interval_width"] for r in usable], dtype=float)
    risk_w = np.asarray([r["risk_interval_width"] for r in usable], dtype=float)
    abs_err = np.abs(actual - pred)
    transitions = np.asarray([r["enso_class_transition"] for r in usable], dtype=bool)
    out = {
        "n": int(len(usable)),
        "baseline_coverage": float(np.mean(abs_err <= base_w)),
        "risk_coverage": float(np.mean(abs_err <= risk_w)),
        "baseline_mean_width": float(np.mean(base_w)),
        "risk_mean_width": float(np.mean(risk_w)),
        "baseline_miss_rate": float(np.mean(abs_err > base_w)),
        "risk_miss_rate": float(np.mean(abs_err > risk_w)),
        "width_abs_error_corr": (
            float(np.corrcoef(risk_w, abs_err)[0, 1]) if risk_w.std() > EPS and abs_err.std() > EPS else None
        ),
    }
    if np.any(transitions):
        out["baseline_transition_coverage"] = float(np.mean(abs_err[transitions] <= base_w[transitions]))
        out["risk_transition_coverage"] = float(np.mean(abs_err[transitions] <= risk_w[transitions]))
        out["risk_transition_mean_width"] = float(np.mean(risk_w[transitions]))
    else:
        out["baseline_transition_coverage"] = None
        out["risk_transition_coverage"] = None
        out["risk_transition_mean_width"] = None
    return out


def point_records(records):
    return [point(r["origin_date"], r["target_date"], r["lag_pred"], r["actual"], r["persistence"]) for r in records]


def add_causal_risk_predictions(records):
    for record in records:
        past = [r for r in records if r["target_anchor"] < record["origin_anchor"]]
        if len(past) < MIN_RISK_TRAIN:
            record["risk_ready"] = False
            record["baseline_interval_width"] = None
            record["risk_interval_width"] = None
            continue

        threshold = float(np.quantile([r["lag_abs_error"] for r in past], HIGH_ERROR_QUANTILE))
        for r in past:
            r["lag_abs_error_high_train_label"] = bool(r["lag_abs_error"] >= threshold)
        record["lag_abs_error_high"] = bool(record["lag_abs_error"] >= threshold)
        record["lag_abs_error_high_threshold"] = threshold
        record["lag_turn_failure"] = bool(record["lag_turn_failure"])
        record["boundary_crossing"] = bool(future_boundary_state(record))
        record["enso_class_transition"] = bool(actual_transition(record))

        rows = [r["risk_features"] for r in past]
        labels = {
            "lag_abs_error_high": [float(r["lag_abs_error_high_train_label"]) for r in past],
            "lag_turn_failure": [float(r["lag_turn_failure"]) for r in past],
            "boundary_crossing": [float(future_boundary_state(r)) for r in past],
            "enso_class_transition": [float(actual_transition(r)) for r in past],
        }
        for target in RISK_TARGETS:
            record[f"prob_{target}"] = predict_probability(rows, labels[target], record["risk_features"])

        baseline_width, risk_width = predict_interval_width(past, record["risk_features"])
        record["baseline_interval_width"] = baseline_width
        record["risk_interval_width"] = risk_width
        record["risk_interval_hit"] = bool(abs(record["actual"] - record["lag_pred"]) <= risk_width)
        record["baseline_interval_hit"] = bool(abs(record["actual"] - record["lag_pred"]) <= baseline_width)
        record["risk_ready"] = True


def mean_metric(items, key):
    vals = [item.get(key) for item in items if item.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def aggregate_risk_metrics(metrics_by_h, horizons, target):
    selected = [metrics_by_h[str(h)][target] for h in horizons]
    keys = sorted({key for item in selected for key in item.keys()})
    out = {}
    for key in keys:
        if key == "n":
            out[key] = int(sum(item.get(key, 0) for item in selected))
        else:
            out[key] = mean_metric(selected, key)
    return out


def aggregate_interval_metrics(metrics_by_h, horizons):
    selected = [metrics_by_h[str(h)] for h in horizons]
    keys = sorted({key for item in selected for key in item.keys()})
    out = {}
    for key in keys:
        if key == "n":
            out[key] = int(sum(item.get(key, 0) for item in selected))
        else:
            out[key] = mean_metric(selected, key)
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

    print("ARA transition risk and uncertainty model")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("risk layer: lag remains central forecast; ARA/work features estimate failure and interval width")
    print("strict guards: base s+h<t; risk train target<t")
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
    lag_scores = {}
    risk_metrics_by_h = {}
    interval_metrics_by_h = {}

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

            record = {
                "horizon": int(h),
                "origin_anchor": int(origin),
                "target_anchor": int(target_anchor),
                "origin_date": dates[origin - 1].strftime("%Y-%m-%d"),
                "target_date": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                "persistence": float(components["persistence"]),
                "actual": float(nino_raw[target_anchor - 1]),
                "lag_pred": float(components["lag_pred"]),
                "phase_pred": float(components["regime_velocity_phase_pred"]),
            }
            record["features"] = build_decomposition_features(record, compact_cache, series, origin, components, dates)
            add_targets(record)
            record["risk_features"] = build_risk_features(record)
            records.append(record)

        add_causal_risk_predictions(records)
        records_by_h[str(h)] = records
        lag_scores[str(h)] = extended_score(point_records(records))
        risk_metrics_by_h[str(h)] = {target: risk_metric(records, target) for target in RISK_TARGETS}
        interval_metrics_by_h[str(h)] = interval_metrics(records)

        print(f"h={h:>2} months")
        print(f"  lag central forecast       {format_score(lag_scores[str(h)])}")
        for target in RISK_TARGETS:
            m = risk_metrics_by_h[str(h)][target]
            print(
                f"  risk {target:24s}"
                f" n={m.get('n', 0):>2}"
                f" event={m.get('event_rate') if m.get('event_rate') is not None else float('nan'):.3f}"
                f" auc={m.get('auc') if m.get('auc') is not None else float('nan'):+.3f}"
                f" brier={m.get('brier') if m.get('brier') is not None else float('nan'):.3f}"
                f" top_lift={m.get('top_vs_base_lift') if m.get('top_vs_base_lift') is not None else float('nan'):.3f}"
            )
        im = interval_metrics_by_h[str(h)]
        print(
            f"  interval q{INTERVAL_QUANTILE:.2f}"
            f" base_cov={im.get('baseline_coverage') if im.get('baseline_coverage') is not None else float('nan'):.3f}"
            f" risk_cov={im.get('risk_coverage') if im.get('risk_coverage') is not None else float('nan'):.3f}"
            f" base_w={im.get('baseline_mean_width') if im.get('baseline_mean_width') is not None else float('nan'):.3f}"
            f" risk_w={im.get('risk_mean_width') if im.get('risk_mean_width') is not None else float('nan'):.3f}"
            f" width_err_corr={im.get('width_abs_error_corr') if im.get('width_abs_error_corr') is not None else float('nan'):+.3f}"
        )
        print()

    focus_horizons = [6, 12, 24]
    focus_risk = {target: aggregate_risk_metrics(risk_metrics_by_h, focus_horizons, target) for target in RISK_TARGETS}
    focus_interval = aggregate_interval_metrics(interval_metrics_by_h, focus_horizons)
    focus_lag = {
        key: float(np.mean([lag_scores[str(h)][key] for h in focus_horizons]))
        for key in ["mae", "corr", "turn_accuracy", "enso_class_accuracy", "transition_mae"]
    }

    slim_examples = {
        h: [
            {
                "origin": r["origin_date"],
                "target": r["target_date"],
                "actual": rounded(r["actual"]),
                "lag_pred": rounded(r["lag_pred"]),
                "phase_pred": rounded(r["phase_pred"]),
                "lag_abs_error": rounded(r["lag_abs_error"]),
                "risk_ready": bool(r.get("risk_ready")),
                "prob_lag_abs_error_high": rounded(r.get("prob_lag_abs_error_high")),
                "prob_lag_turn_failure": rounded(r.get("prob_lag_turn_failure")),
                "prob_boundary_crossing": rounded(r.get("prob_boundary_crossing")),
                "prob_enso_class_transition": rounded(r.get("prob_enso_class_transition")),
                "baseline_interval_width": rounded(r.get("baseline_interval_width")),
                "risk_interval_width": rounded(r.get("risk_interval_width")),
            }
            for r in records[:12]
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal ARA transition risk and uncertainty layer",
        "leakage_guard": [
            "Base lag and phase predictions use strict-causal training pairs s+h<t.",
            "All risk inputs are known at origin t.",
            "At origin t, risk/interval models train only on previous records whose target_anchor < t.",
            "High-error thresholds and interval calibration are estimated from that same past-only set.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly",
        "base": BASE,
        "home_period_months": HOME_PERIOD,
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "min_risk_train": MIN_RISK_TRAIN,
        "high_error_quantile": HIGH_ERROR_QUANTILE,
        "interval_quantile": INTERVAL_QUANTILE,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
        },
        "risk_targets": {
            "lag_abs_error_high": "lag absolute error above the past-only 75th percentile for that origin/horizon",
            "lag_turn_failure": "lag forecast has wrong sign for future delta from current value",
            "boundary_crossing": "future ENSO state is non-neutral",
            "enso_class_transition": "future ENSO class differs from current class",
        },
        "lag_central_forecast_scores": clean_for_json(lag_scores),
        "risk_metrics": clean_for_json(risk_metrics_by_h),
        "interval_metrics": clean_for_json(interval_metrics_by_h),
        "focus_6_12_24": {
            "lag_central_forecast": clean_for_json(focus_lag),
            "risk_metrics": clean_for_json(focus_risk),
            "interval_metrics": clean_for_json(focus_interval),
        },
        "example_records": clean_for_json(slim_examples),
        "elapsed_seconds": rounded(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_TRANSITION_RISK_UNCERTAINTY = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24 risk metrics:")
    for target, m in focus_risk.items():
        print(
            f"  {target:24s}"
            f" n={m.get('n', 0):>3}"
            f" event={m.get('event_rate') if m.get('event_rate') is not None else float('nan'):.3f}"
            f" auc={m.get('auc') if m.get('auc') is not None else float('nan'):+.3f}"
            f" brier={m.get('brier') if m.get('brier') is not None else float('nan'):.3f}"
            f" top_lift={m.get('top_vs_base_lift') if m.get('top_vs_base_lift') is not None else float('nan'):.3f}"
        )
    print("Focus interval metrics:")
    print(
        f"  baseline coverage={focus_interval.get('baseline_coverage'):.3f}"
        f" width={focus_interval.get('baseline_mean_width'):.3f}"
        f" | risk coverage={focus_interval.get('risk_coverage'):.3f}"
        f" width={focus_interval.get('risk_mean_width'):.3f}"
        f" width/error corr={focus_interval.get('width_abs_error_corr'):+.3f}"
    )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
