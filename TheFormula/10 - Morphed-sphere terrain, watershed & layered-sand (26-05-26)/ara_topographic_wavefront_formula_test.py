"""
ara_topographic_wavefront_formula_test.py

First strict-causal test of the "energy over terrain" ARA formulation:

    ARA topology = curved constraint surface
    wavefront = current energy path across that surface
    lower rungs = micro-wave impulse/texture
    upper rungs = envelope/reservoir terrain
    friction/turbulence = scattering or resistance from opposition/roughness

The goal is not to add more flat features.  The goal is to build an explicit
terrain-flow formula and ask what it predicts:

  - boundary/event risk
  - ENSO class transition risk
  - lag forecast failure risk
  - residual correction to the lag point forecast

Leakage guard:

  - Every terrain component at origin t uses only data[:t].
  - Base lag prediction at origin t uses only anchors s where s+h<t.
  - Residual correction calibration for origin t uses only previous records
    whose targets are already known: target_anchor < t.
  - Raw terrain scores are unsupervised formula scores, not fitted on future.
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

from ara_cross_rung_spin_transfer_test import (
    ALL_PERIODS,
    FEATURE_GROUPS,
    HOME,
    HORIZONS,
    LOWER_PERIODS,
    MIN_RISK_TRAIN,
    MIN_TRAIN,
    ORIGIN_STRIDE,
    SIGNALS,
    TIME_TO_TRANSITION_WINDOW,
    UPPER_PERIODS,
    add_lag_predictions,
    add_outcome_labels,
    build_feature_sets,
    phase_acceleration,
    phase_velocity,
    turn_density,
    velocity_sign_change_density,
)
from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import START_YEAR, clean_for_json, load_enso_frame, zscore_columns
from ara_lag_phase_hybrid_predictor import extended_score, finite, format_score, point
from ara_multirung_feeder_ablation import band_state
from ara_transition_risk_and_uncertainty_model import auc_score


OUT_JSON = HERE / "ara_topographic_wavefront_formula_result.json"
OUT_JS = HERE / "ara_topographic_wavefront_formula_result.js"

RIDGE_ALPHA_CORRECTION = 8.0
HIGH_ERROR_QUANTILE = 0.75
EPS = 1e-9

RAW_SCORE_TARGETS = [
    "boundary_crossing",
    "enso_class_transition",
    "lag_turn_failure",
    "lag_abs_error_high",
]

FORMULA_SCORE_KEYS = [
    "terrain_flow_score",
    "transition_pressure_score",
    "turbulence_score",
    "boundary_encounter_score",
]


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


def squash(value, scale=1.0):
    return math.tanh(finite(value) / max(scale, EPS))


def sigmoid(value):
    value = max(-40.0, min(40.0, finite(value)))
    return 1.0 / (1.0 + math.exp(-value))


def boundary_distance(value):
    value = finite(value)
    if value >= 0:
        return abs(0.5 - value)
    return abs(-0.5 - value)


def current_boundary_state(series, anchor):
    nino = series["NINO"]["raw"]
    current = finite(nino[anchor - 1])
    prior3 = finite(nino[anchor - 4]) if anchor >= 4 else current
    prior12 = finite(nino[anchor - 13]) if anchor >= 13 else current
    d_now = boundary_distance(current)
    d3 = boundary_distance(prior3)
    d12 = boundary_distance(prior12)
    return {
        "current": current,
        "distance_now": d_now,
        "proximity": 1.0 / (1.0 + d_now),
        "near_boundary": 1.0 if d_now <= 0.25 else 0.0,
        "surface_slope_3": d3 - d_now,
        "surface_slope_12": d12 - d_now,
        "native_direction": sign(current) if abs(current) >= 0.15 else 0,
    }


def mean_abs_velocity(cache, anchor, signal_name, periods):
    vals = [abs(phase_velocity(cache, anchor, signal_name, p, 1)) for p in periods]
    return float(np.mean(vals)) if vals else 0.0


def upper_reservoir(cache, anchor):
    energies = []
    slopes = []
    velocities = []
    for signal_name in SIGNALS:
        for period in UPPER_PERIODS:
            st = cache[anchor][signal_name][period]
            energies.append(finite(st.get("energy", 0.0)))
            slopes.append(finite(st.get("slope", 0.0)))
            velocities.append(abs(phase_velocity(cache, anchor, signal_name, period, 1)))
    return {
        "energy": float(np.sum(energies)),
        "mean_slope": float(np.mean(slopes)) if slopes else 0.0,
        "mean_abs_velocity": float(np.mean(velocities)) if velocities else 0.0,
    }


def lower_micro_impulses(cache, anchor):
    pressures = []
    aligned = []
    opposed = []
    locks = []
    for feeder in ["SOI", "PDO"]:
        home_theta = cache[anchor]["NINO"][HOME]["theta"]
        home_v = phase_velocity(cache, anchor, "NINO", HOME, 1)
        for period in LOWER_PERIODS:
            theta = cache[anchor][feeder][period]["theta"]
            v = phase_velocity(cache, anchor, feeder, period, 1)
            lock = math.cos(theta - home_theta)
            orientation = sign(v) * sign(home_v)
            pressure = abs(v) * (HOME / period)
            pressures.append(pressure)
            locks.append(lock)
            aligned.append(max(0.0, lock * orientation) * pressure)
            opposed.append(max(0.0, -lock * orientation) * pressure)
    return {
        "pressure": float(np.sum(pressures)),
        "mean_lock": float(np.mean(locks)) if locks else 0.0,
        "aligned_pressure": float(np.sum(aligned)),
        "opposed_pressure": float(np.sum(opposed)),
        "pressure_balance": float(np.sum(aligned) - np.sum(opposed)),
        "turn_density": turn_density(cache, anchor, "NINO", LOWER_PERIODS, 12)
        + turn_density(cache, anchor, "SOI", LOWER_PERIODS, 12),
        "sign_change_density": velocity_sign_change_density(cache, anchor, "NINO", LOWER_PERIODS, 12)
        + velocity_sign_change_density(cache, anchor, "SOI", LOWER_PERIODS, 12),
    }


def wavefront_terms(cache, anchor):
    home_v = phase_velocity(cache, anchor, "NINO", HOME, 1)
    home_v3 = phase_velocity(cache, anchor, "NINO", HOME, 3)
    curvature = phase_acceleration(cache, anchor, "NINO", HOME, 3)
    return {
        "home_velocity": home_v,
        "home_velocity_3": home_v3,
        "home_abs_velocity": abs(home_v),
        "home_curvature": curvature,
        "home_roughness": abs(curvature) + velocity_sign_change_density(cache, anchor, "NINO", [HOME], 12),
    }


def terrain_formula_components(series, cache, anchor):
    boundary = current_boundary_state(series, anchor)
    wave = wavefront_terms(cache, anchor)
    micro = lower_micro_impulses(cache, anchor)
    upper = upper_reservoir(cache, anchor)

    surface_descent = 0.7 * boundary["surface_slope_3"] + 0.3 * boundary["surface_slope_12"]
    surface_slope_score = squash(surface_descent, 0.20)
    wave_score = squash(wave["home_velocity"] * HOME, 1.0)
    curvature_score = squash(wave["home_curvature"] * HOME, 0.6)
    micro_score = squash(micro["pressure_balance"], 1.5)
    micro_density = squash(micro["turn_density"], 8.0)
    reservoir_score = squash(upper["energy"], 5.0)
    envelope_resistance = reservoir_score * (0.5 + 0.5 * squash(abs(upper["mean_slope"]), 0.10))
    boundary_proximity = squash(boundary["proximity"] - 0.75, 0.20)
    turbulence = squash(
        micro["opposed_pressure"]
        + 2.0 * micro["sign_change_density"]
        + 2.0 * wave["home_roughness"]
        + abs(micro_score - wave_score),
        2.5,
    )

    terrain_flow = (
        0.35 * wave_score
        + 0.30 * surface_slope_score
        + 0.25 * micro_score
        + 0.15 * curvature_score
        - 0.20 * turbulence
    )
    transition_pressure = sigmoid(
        1.10 * boundary_proximity
        + 0.85 * max(0.0, surface_slope_score)
        + 0.70 * abs(terrain_flow)
        + 0.45 * micro_density
        + 0.35 * reservoir_score
        - 0.55 * turbulence
    )
    boundary_encounter = sigmoid(
        1.20 * boundary_proximity
        + 0.55 * reservoir_score
        + 0.35 * max(0.0, surface_slope_score)
        - 0.35 * turbulence
    )

    return {
        "surface_slope_score": surface_slope_score,
        "wavefront_score": wave_score,
        "curvature_score": curvature_score,
        "micro_impulse_score": micro_score,
        "micro_density_score": micro_density,
        "upper_reservoir_score": reservoir_score,
        "envelope_resistance": envelope_resistance,
        "boundary_proximity_score": boundary_proximity,
        "turbulence_score": turbulence,
        "terrain_flow_score": terrain_flow,
        "transition_pressure_score": transition_pressure,
        "boundary_encounter_score": boundary_encounter,
        "raw_surface_descent": surface_descent,
        "raw_micro_pressure": micro["pressure"],
        "raw_micro_aligned_pressure": micro["aligned_pressure"],
        "raw_micro_opposed_pressure": micro["opposed_pressure"],
        "raw_upper_energy": upper["energy"],
        "raw_home_velocity": wave["home_velocity"],
        "raw_home_curvature": wave["home_curvature"],
    }


def score_raw_formula(records, score_key, target_key):
    usable = [r for r in records if score_key in r["terrain"] and target_key in r]
    if not usable:
        return {"n": 0}
    scores = np.asarray([finite(r["terrain"][score_key]) for r in usable], dtype=float)
    labels = np.asarray([int(bool(r[target_key])) for r in usable], dtype=int)
    event_rate = float(np.mean(labels))
    auc = auc_score(labels, scores)
    top_cut = float(np.quantile(scores, 0.75))
    bottom_cut = float(np.quantile(scores, 0.25))
    top = labels[scores >= top_cut]
    bottom = labels[scores <= bottom_cut]
    top_rate = float(np.mean(top)) if len(top) else None
    bottom_rate = float(np.mean(bottom)) if len(bottom) else None
    return {
        "n": int(len(usable)),
        "event_rate": event_rate,
        "auc": auc,
        "mean_score": float(np.mean(scores)),
        "top_quartile_event_rate": top_rate,
        "bottom_quartile_event_rate": bottom_rate,
        "top_vs_base_lift": top_rate / event_rate if top_rate is not None and event_rate > EPS else None,
        "top_vs_bottom_lift": top_rate / bottom_rate if top_rate is not None and bottom_rate is not None and bottom_rate > EPS else None,
    }


def terrain_correction_features(record):
    t = record["terrain"]
    keys = [
        "surface_slope_score",
        "wavefront_score",
        "curvature_score",
        "micro_impulse_score",
        "micro_density_score",
        "upper_reservoir_score",
        "envelope_resistance",
        "boundary_proximity_score",
        "turbulence_score",
        "terrain_flow_score",
        "transition_pressure_score",
        "boundary_encounter_score",
    ]
    return {key: finite(t.get(key, 0.0)) for key in keys}


def add_causal_terrain_correction(records):
    for record in records:
        past = [r for r in records if r["target_anchor"] < record["origin_anchor"] and "lag_pred" in r]
        if len(past) < MIN_RISK_TRAIN:
            record["terrain_corrected_pred"] = record["lag_pred"]
            record["terrain_correction"] = 0.0
            record["terrain_correction_ready"] = False
            continue
        train_rows = [terrain_correction_features(r) for r in past]
        train_y = [r["actual"] - r["lag_pred"] for r in past]
        model = fit_ridge_model(train_rows, train_y, alpha=RIDGE_ALPHA_CORRECTION)
        correction = float(predict_ridge_model(model, terrain_correction_features(record))[0])
        correction = max(-1.5, min(1.5, correction))
        record["terrain_correction"] = correction
        record["terrain_corrected_pred"] = record["lag_pred"] + correction
        record["terrain_correction_ready"] = True


def point_records(records, pred_key):
    return [point(r["origin_date"], r["target_date"], r[pred_key], r["actual"], r["current"]) for r in records]


def aggregate_metric(items, key):
    vals = [item.get(key) for item in items if item.get(key) is not None]
    return float(np.mean(vals)) if vals else None


def aggregate_focus(score_by_h, horizons):
    selected = [score_by_h[str(h)] for h in horizons]
    keys = sorted({key for item in selected for key in item.keys()})
    out = {}
    for key in keys:
        if key == "n":
            out[key] = int(sum(item.get(key, 0) for item in selected))
        else:
            out[key] = aggregate_metric(selected, key)
    return out


def run():
    started = time.time()
    frame = load_enso_frame()
    dates = list(frame.index)
    series = zscore_columns(frame)
    nino_raw = series["NINO"]["raw"]
    n = len(frame)
    max_h = max(HORIZONS)
    min_anchor = int(math.ceil(4.0 * max(ALL_PERIODS))) + 2
    start_idx = int(np.searchsorted(np.asarray(dates, dtype="datetime64[ns]"), np.datetime64(f"{START_YEAR}-01-01"))) + 1
    test_start = max(start_idx, min_anchor + MIN_TRAIN + TIME_TO_TRANSITION_WINDOW + max_h + 1)
    all_anchors = list(range(min_anchor, n + 1))

    print("ARA topographic wavefront formula test")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("formula: wavefront downhill over ARA terrain, micro-impulse modulation, upper-envelope constraint")
    print("strict guards: terrain data[:t]; lag s+h<t; correction target<t")
    print()

    cache = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        cache[anchor] = {
            signal_name: {period: band_state(series[signal_name]["z"], anchor, period) for period in ALL_PERIODS}
            for signal_name in SIGNALS
        }
        if i % 50 == 0:
            print(f"  cached terrain states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached terrain states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    records_by_h = {}
    point_scores = {"lag": {}, "lag_plus_terrain": {}}
    raw_formula_scores = {}

    for h in HORIZONS:
        records = []
        origins = list(range(min_anchor + max_h + 1, n - h + 1, ORIGIN_STRIDE))
        for origin in origins:
            target_anchor = origin + h
            if target_anchor > n:
                continue
            feature_sets = build_feature_sets(series, cache, origin)
            records.append(
                {
                    "horizon": int(h),
                    "origin_anchor": int(origin),
                    "target_anchor": int(target_anchor),
                    "origin_date": dates[origin - 1].strftime("%Y-%m-%d"),
                    "target_date": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                    "is_test": bool(origin >= test_start),
                    "current": float(nino_raw[origin - 1]),
                    "actual": float(nino_raw[target_anchor - 1]),
                    "feature_sets": {key: val for key, val in feature_sets.items() if key != "_parts"},
                    "terrain": terrain_formula_components(series, cache, origin),
                }
            )
        add_lag_predictions(records, series, h)
        add_outcome_labels(records, cache, series, h)
        add_causal_terrain_correction(records)

        eval_records = [r for r in records if r["is_test"]]
        records_by_h[str(h)] = eval_records
        point_scores["lag"][str(h)] = extended_score(point_records(eval_records, "lag_pred"))
        point_scores["lag_plus_terrain"][str(h)] = extended_score(point_records(eval_records, "terrain_corrected_pred"))
        raw_formula_scores[str(h)] = {
            score_key: {target: score_raw_formula(eval_records, score_key, target) for target in RAW_SCORE_TARGETS}
            for score_key in FORMULA_SCORE_KEYS
        }

        print(f"h={h:>2} months")
        print(f"  lag              {format_score(point_scores['lag'][str(h)])}")
        print(f"  lag+terrain      {format_score(point_scores['lag_plus_terrain'][str(h)])}")
        for score_key in FORMULA_SCORE_KEYS:
            bc = raw_formula_scores[str(h)][score_key]["boundary_crossing"]
            tr = raw_formula_scores[str(h)][score_key]["enso_class_transition"]
            lf = raw_formula_scores[str(h)][score_key]["lag_turn_failure"]
            print(
                f"  raw {score_key:26s}"
                f" boundary_auc={bc.get('auc') if bc.get('auc') is not None else float('nan'):+.3f}"
                f" transition_auc={tr.get('auc') if tr.get('auc') is not None else float('nan'):+.3f}"
                f" lagfail_auc={lf.get('auc') if lf.get('auc') is not None else float('nan'):+.3f}"
            )
        print()

    focus_horizons = [6, 12, 24]
    focus = {
        "point_scores": {
            key: aggregate_focus(point_scores[key], focus_horizons) for key in point_scores
        },
        "raw_formula_scores": {},
    }
    for score_key in FORMULA_SCORE_KEYS:
        focus["raw_formula_scores"][score_key] = {
            target: aggregate_focus(
                {str(h): raw_formula_scores[str(h)][score_key][target] for h in focus_horizons},
                focus_horizons,
            )
            for target in RAW_SCORE_TARGETS
        }

    examples = {
        h: [
            {
                "origin": r["origin_date"],
                "target": r["target_date"],
                "current": rounded(r["current"]),
                "actual": rounded(r["actual"]),
                "lag_pred": rounded(r["lag_pred"]),
                "terrain_corrected_pred": rounded(r["terrain_corrected_pred"]),
                "terrain_correction": rounded(r["terrain_correction"]),
                "boundary_crossing": r["boundary_crossing"],
                "enso_class_transition": r["enso_class_transition"],
                "terrain_flow_score": rounded(r["terrain"]["terrain_flow_score"]),
                "transition_pressure_score": rounded(r["terrain"]["transition_pressure_score"]),
                "turbulence_score": rounded(r["terrain"]["turbulence_score"]),
                "boundary_encounter_score": rounded(r["terrain"]["boundary_encounter_score"]),
            }
            for r in records[:10]
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal topographic wavefront formula test",
        "leakage_guard": [
            "Every terrain component at origin t uses only data[:t].",
            "Base lag prediction at origin t uses only anchors s where s+h<t.",
            "Residual correction calibration for origin t uses only previous records whose targets are already known.",
            "Raw terrain scores are unsupervised formula scores, not fitted on future.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly and transition/risk labels",
        "formula": {
            "terrain_flow": "0.35*wavefront + 0.30*surface_slope + 0.25*micro_impulse + 0.15*curvature - 0.20*turbulence",
            "transition_pressure": "sigmoid(boundary_proximity + positive_surface_slope + |flow| + micro_density + upper_reservoir - turbulence)",
            "boundary_encounter": "sigmoid(boundary_proximity + upper_reservoir + positive_surface_slope - turbulence)",
        },
        "horizons_months": HORIZONS,
        "origin_stride_months": ORIGIN_STRIDE,
        "sample": {
            "start": dates[0].strftime("%Y-%m-%d"),
            "end": dates[-1].strftime("%Y-%m-%d"),
            "n": int(n),
            "test_start_origin": dates[test_start - 1].strftime("%Y-%m-%d"),
            "min_anchor": int(min_anchor),
        },
        "point_scores": clean_for_json(point_scores),
        "raw_formula_scores": clean_for_json(raw_formula_scores),
        "focus_6_12_24": clean_for_json(focus),
        "example_records": clean_for_json(examples),
        "elapsed_seconds": rounded(time.time() - started, 3),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_TOPOGRAPHIC_WAVEFRONT_FORMULA = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24 point scores:")
    for key, score in focus["point_scores"].items():
        print(
            f"  {key:16s}"
            f" MAE={score.get('mae'):.3f}"
            f" corr={score.get('corr'):+.3f}"
            f" turn={score.get('turn_accuracy'):.3f}"
            f" transition_mae={score.get('transition_mae'):.3f}"
        )
    print("Focus 6/12/24 raw formula AUCs:")
    for score_key in FORMULA_SCORE_KEYS:
        row = focus["raw_formula_scores"][score_key]
        print(
            f"  {score_key:26s}"
            f" boundary={row['boundary_crossing'].get('auc'):+.3f}"
            f" transition={row['enso_class_transition'].get('auc'):+.3f}"
            f" lagfail={row['lag_turn_failure'].get('auc'):+.3f}"
            f" higherr={row['lag_abs_error_high'].get('auc'):+.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
