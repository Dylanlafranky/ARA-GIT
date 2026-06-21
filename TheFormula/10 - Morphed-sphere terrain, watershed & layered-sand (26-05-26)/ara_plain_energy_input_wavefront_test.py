"""
ara_plain_energy_input_wavefront_test.py

Strict-causal no-lag test of the ARA "smaller spheres spin the larger sphere"
idea.

This deliberately removes the lag ridge / inertial native-unit predictor used
by ara_topographic_wavefront_formula_test.py.  The point forecast is anchored at
the current observed value, but the future delta is produced only from current
ARA geometry and energy-input terms:

    lower rungs = faster spin pressure / micro-impulses
    home rung = current wavefront direction and curvature
    upper rungs = reservoir / envelope gate
    turbulence = opposed spin and roughness loss

Leakage guard:

  - every ARA terrain component at origin t uses only data[:t].
  - raw ARA energy-flow uses no fitted future data.
  - calibrated ARA scale/decoder at origin t trains only on previous records
    whose targets are already known: target_anchor < t.
  - no lag-only/native lag feature block is used by any ARA model here.
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
    HOME,
    HORIZONS,
    MIN_RISK_TRAIN,
    MIN_TRAIN,
    ORIGIN_STRIDE,
    SIGNALS,
    TIME_TO_TRANSITION_WINDOW,
    enso_class,
    time_to_transition,
)
from ara_geometry_state_transition_test import fit_ridge_model, predict_ridge_model
from ara_geometry_transport_test import START_YEAR, clean_for_json, load_enso_frame, zscore_columns
from ara_lag_phase_hybrid_predictor import extended_score, finite, format_score, point
from ara_multirung_feeder_ablation import band_state
from ara_topographic_wavefront_formula_test import (
    aggregate_focus,
    rounded,
    score_raw_formula,
    sign,
    terrain_correction_features,
    terrain_formula_components,
)


OUT_JSON = HERE / "ara_plain_energy_input_wavefront_result.json"
OUT_JS = HERE / "ara_plain_energy_input_wavefront_result.js"

RIDGE_ALPHA_SCALE = 4.0
RIDGE_ALPHA_ARA_DECODER = 10.0
HIGH_ERROR_QUANTILE = 0.75
EPS = 1e-9

MODEL_KEYS = [
    "persistence",
    "ara_energy_raw",
    "ara_energy_scaled",
    "ara_energy_decoder",
]

FORMULA_SCORE_KEYS = [
    "ara_unit_delta",
    "ara_energy_input_score",
    "ara_effective_work_score",
    "ara_turbulence_loss_score",
]

RAW_SCORE_TARGETS = [
    "boundary_crossing",
    "enso_class_transition",
    "persistence_turn_failure",
    "persistence_abs_error_high",
]


def squash(value, scale=1.0):
    return math.tanh(finite(value) / max(scale, EPS))


def class_transition(record):
    return enso_class(record["actual"]) != enso_class(record["current"])


def future_boundary_crossing(record):
    return abs(record["current"]) < 0.5 and abs(record["actual"]) >= 0.5


def ara_energy_formula(record, horizon):
    """Return an ARA-only native-unit-free delta from lower spin energy."""
    t = record["terrain"]
    horizon_gate = math.sqrt(max(float(horizon), 1.0) / HOME)

    lower_signed_spin = (
        0.50 * finite(t.get("micro_impulse_score", 0.0))
        + 0.25 * finite(t.get("micro_density_score", 0.0)) * sign(t.get("micro_impulse_score", 0.0))
        + 0.25 * squash(finite(t.get("raw_micro_aligned_pressure", 0.0)) - finite(t.get("raw_micro_opposed_pressure", 0.0)), 2.0)
    )
    home_wave = (
        0.65 * finite(t.get("wavefront_score", 0.0))
        + 0.35 * finite(t.get("curvature_score", 0.0))
    )
    route = (
        0.45 * lower_signed_spin
        + 0.35 * home_wave
        + 0.20 * finite(t.get("surface_slope_score", 0.0))
    )

    reservoir_gate = 0.65 + 0.35 * max(0.0, finite(t.get("upper_reservoir_score", 0.0)))
    boundary_gate = 0.70 + 0.30 * finite(t.get("transition_pressure_score", 0.5))
    turbulence = max(0.0, finite(t.get("turbulence_score", 0.0)))
    friction_gate = max(0.10, 1.0 - 0.55 * turbulence)

    energy_input = abs(lower_signed_spin) * (0.75 + 0.25 * finite(t.get("micro_density_score", 0.0)))
    effective_work = route * reservoir_gate * boundary_gate * friction_gate
    unit_delta = horizon_gate * effective_work

    return {
        "ara_unit_delta": float(unit_delta),
        "ara_energy_input_score": float(energy_input),
        "ara_effective_work_score": float(effective_work),
        "ara_turbulence_loss_score": float(turbulence),
        "ara_route_score": float(route),
        "ara_reservoir_gate": float(reservoir_gate),
        "ara_boundary_gate": float(boundary_gate),
        "ara_friction_gate": float(friction_gate),
        "ara_lower_signed_spin": float(lower_signed_spin),
        "ara_home_wave_score": float(home_wave),
    }


def ara_decoder_features(record):
    out = terrain_correction_features(record)
    for key, value in record["ara_energy"].items():
        out[key] = finite(value)
    h = float(record["horizon"])
    out["horizon_over_home"] = h / HOME
    out["sqrt_horizon_over_home"] = math.sqrt(max(h, 1.0) / HOME)
    out["unit_x_energy"] = finite(record["ara_energy"]["ara_unit_delta"]) * finite(record["ara_energy"]["ara_energy_input_score"])
    out["unit_x_reservoir"] = finite(record["ara_energy"]["ara_unit_delta"]) * finite(record["ara_energy"]["ara_reservoir_gate"])
    out["unit_x_friction"] = finite(record["ara_energy"]["ara_unit_delta"]) * finite(record["ara_energy"]["ara_friction_gate"])
    return out


def add_outcome_labels(records, series):
    nino = series["NINO"]["raw"]
    for i, record in enumerate(records):
        record["boundary_crossing"] = bool(future_boundary_crossing(record))
        record["enso_class_transition"] = bool(class_transition(record))
        record["future_amplitude_size"] = abs(record["actual"] - record["current"])
        record["time_to_transition"] = time_to_transition(nino, record["origin_anchor"], TIME_TO_TRANSITION_WINDOW)
        record["persistence_abs_error"] = abs(record["current"] - record["actual"])
        record["persistence_turn_failure"] = bool(sign(record["actual"] - record["current"]) != 0)
        past = [r for r in records[:i] if r["target_anchor"] < record["origin_anchor"] and "persistence_abs_error" in r]
        if past:
            threshold = float(np.quantile([r["persistence_abs_error"] for r in past], HIGH_ERROR_QUANTILE))
        else:
            threshold = float("inf")
        record["persistence_abs_error_high"] = bool(record["persistence_abs_error"] >= threshold)


def fit_predict_delta(train_rows, train_y, row, alpha, clip=3.0):
    model = fit_ridge_model(train_rows, train_y, alpha=alpha)
    pred = float(predict_ridge_model(model, row)[0])
    return max(-clip, min(clip, pred))


def add_no_lag_ara_predictions(records):
    for record in records:
        unit_delta = finite(record["ara_energy"]["ara_unit_delta"])
        record["persistence_pred"] = record["current"]
        record["ara_energy_raw_pred"] = record["current"] + unit_delta

        past = [r for r in records if r["target_anchor"] < record["origin_anchor"] and "ara_energy" in r]
        if len(past) < MIN_RISK_TRAIN:
            record["ara_energy_scaled_pred"] = record["ara_energy_raw_pred"]
            record["ara_energy_decoder_pred"] = record["ara_energy_raw_pred"]
            record["ara_scale_ready"] = False
            record["ara_decoder_ready"] = False
            continue

        scale_rows = [{"unit_delta": finite(r["ara_energy"]["ara_unit_delta"])} for r in past]
        train_y = [r["actual"] - r["current"] for r in past]
        scale_delta = fit_predict_delta(
            scale_rows,
            train_y,
            {"unit_delta": unit_delta},
            RIDGE_ALPHA_SCALE,
            clip=3.0,
        )
        record["ara_energy_scaled_pred"] = record["current"] + scale_delta
        record["ara_scale_ready"] = True

        decoder_rows = [ara_decoder_features(r) for r in past]
        decoder_delta = fit_predict_delta(
            decoder_rows,
            train_y,
            ara_decoder_features(record),
            RIDGE_ALPHA_ARA_DECODER,
            clip=3.0,
        )
        record["ara_energy_decoder_pred"] = record["current"] + decoder_delta
        record["ara_decoder_ready"] = True


def point_records(records, pred_key):
    return [point(r["origin_date"], r["target_date"], r[pred_key], r["actual"], r["current"]) for r in records]


def raw_score(records, score_key, target_key):
    usable = []
    for record in records:
        if score_key in record["ara_energy"]:
            item = dict(record)
            item["terrain"] = {score_key: record["ara_energy"][score_key]}
            usable.append(item)
    return score_raw_formula(usable, score_key, target_key)


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

    print("ARA plain energy-input wavefront test")
    print("=" * 100)
    print(f"sample: {dates[0].date()} -> {dates[-1].date()} n={n}")
    print(f"test origins start: {dates[test_start - 1].date()} stride={ORIGIN_STRIDE}")
    print("formula: lower spin pressure -> home wavefront, gated by upper reservoir and turbulence")
    print("strict guards: terrain data[:t]; no lag block; calibration target<t")
    print()

    cache = {}
    t0 = time.time()
    for i, anchor in enumerate(all_anchors, start=1):
        cache[anchor] = {
            signal_name: {period: band_state(series[signal_name]["z"], anchor, period) for period in ALL_PERIODS}
            for signal_name in SIGNALS
        }
        if i % 50 == 0:
            print(f"  cached ARA states {i:4d}/{len(all_anchors)} in {time.time() - t0:.1f}s", flush=True)
    print(f"  cached ARA states {len(all_anchors):4d}/{len(all_anchors)} in {time.time() - t0:.1f}s")
    print()

    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    raw_formula_scores = {}

    for h in HORIZONS:
        records = []
        origins = list(range(min_anchor + max_h + 1, n - h + 1, ORIGIN_STRIDE))
        for origin in origins:
            target_anchor = origin + h
            if target_anchor > n:
                continue
            record = {
                "horizon": int(h),
                "origin_anchor": int(origin),
                "target_anchor": int(target_anchor),
                "origin_date": dates[origin - 1].strftime("%Y-%m-%d"),
                "target_date": dates[target_anchor - 1].strftime("%Y-%m-%d"),
                "is_test": bool(origin >= test_start),
                "current": float(nino_raw[origin - 1]),
                "actual": float(nino_raw[target_anchor - 1]),
                "terrain": terrain_formula_components(series, cache, origin),
            }
            record["ara_energy"] = ara_energy_formula(record, h)
            records.append(record)

        add_outcome_labels(records, series)
        add_no_lag_ara_predictions(records)

        eval_records = [r for r in records if r["is_test"]]
        records_by_h[str(h)] = eval_records
        point_scores["persistence"][str(h)] = extended_score(point_records(eval_records, "persistence_pred"))
        point_scores["ara_energy_raw"][str(h)] = extended_score(point_records(eval_records, "ara_energy_raw_pred"))
        point_scores["ara_energy_scaled"][str(h)] = extended_score(point_records(eval_records, "ara_energy_scaled_pred"))
        point_scores["ara_energy_decoder"][str(h)] = extended_score(point_records(eval_records, "ara_energy_decoder_pred"))

        raw_formula_scores[str(h)] = {
            score_key: {target: raw_score(eval_records, score_key, target) for target in RAW_SCORE_TARGETS}
            for score_key in FORMULA_SCORE_KEYS
        }

        print(f"h={h:>2} months")
        for key in MODEL_KEYS:
            print(f"  {key:18s} {format_score(point_scores[key][str(h)])}")
        for score_key in FORMULA_SCORE_KEYS:
            bc = raw_formula_scores[str(h)][score_key]["boundary_crossing"]
            tr = raw_formula_scores[str(h)][score_key]["enso_class_transition"]
            lf = raw_formula_scores[str(h)][score_key]["persistence_turn_failure"]
            print(
                f"  raw {score_key:26s}"
                f" boundary_auc={bc.get('auc') if bc.get('auc') is not None else float('nan'):+.3f}"
                f" transition_auc={tr.get('auc') if tr.get('auc') is not None else float('nan'):+.3f}"
                f" pers_turnfail_auc={lf.get('auc') if lf.get('auc') is not None else float('nan'):+.3f}"
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
                "ara_energy_raw_pred": rounded(r["ara_energy_raw_pred"]),
                "ara_energy_scaled_pred": rounded(r["ara_energy_scaled_pred"]),
                "ara_energy_decoder_pred": rounded(r["ara_energy_decoder_pred"]),
                "boundary_crossing": r["boundary_crossing"],
                "enso_class_transition": r["enso_class_transition"],
                "ara_unit_delta": rounded(r["ara_energy"]["ara_unit_delta"]),
                "ara_energy_input_score": rounded(r["ara_energy"]["ara_energy_input_score"]),
                "ara_effective_work_score": rounded(r["ara_energy"]["ara_effective_work_score"]),
                "ara_turbulence_loss_score": rounded(r["ara_energy"]["ara_turbulence_loss_score"]),
            }
            for r in records[:10]
        ]
        for h, records in records_by_h.items()
    }

    out = {
        "date": "2026-05-25",
        "method": "strict-causal plain ARA energy-input wavefront test",
        "leakage_guard": [
            "Every ARA terrain component at origin t uses only data[:t].",
            "Raw ARA energy-flow uses no fitted future data.",
            "Scale and decoder calibration at origin t use only records whose targets are already known.",
            "No lag-only/native lag feature block is used by any ARA model here.",
        ],
        "system": "ENSO",
        "target": "NINO3.4 anomaly from ARA geometry/energy only",
        "formula": {
            "lower_signed_spin": "0.50*micro_impulse + 0.25*micro_density*sign(micro_impulse) + 0.25*squash(aligned_pressure-opposed_pressure)",
            "home_wave": "0.65*wavefront + 0.35*curvature",
            "route": "0.45*lower_signed_spin + 0.35*home_wave + 0.20*surface_slope",
            "effective_work": "route * reservoir_gate * boundary_gate * friction_gate",
            "unit_delta": "sqrt(h/home_period) * effective_work",
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
        "window.ARA_PLAIN_ENERGY_INPUT_WAVEFRONT = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24 point scores:")
    for key, score in focus["point_scores"].items():
        print(
            f"  {key:18s}"
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
            f" pers_turnfail={row['persistence_turn_failure'].get('auc'):+.3f}"
            f" higherr={row['persistence_abs_error_high'].get('auc'):+.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
