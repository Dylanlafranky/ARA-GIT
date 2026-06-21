"""
ara_layered_sand_closed_cutoff_run.py

Closed/autonomous cutoff test for the layered-sand formula.

This is the test the visual workbench was not doing:

  observed data until cutoff
  -> seed the formula state
  -> generate future NINO/SOI/PDO internally
  -> never read future observed NINO/SOI/PDO inside the formula
  -> compare the autonomous path to truth afterward

The companion SOI/PDO closure is deliberately simple and fit only before the
cutoff: SOI is treated as anti-phase partner, PDO as a slow reservoir. It is
not allowed to look ahead.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ara_fractal_sphere_terrain_reader import value_to_ara
from ara_geometry_transport_test import clean_for_json, load_enso_frame
from ara_layered_sand_correlation_search import ADVANCE_DEFAULTS
from ara_layered_sand_parameter_search import predict_from_record
from ara_layered_sand_single_formula import FORMULA, HOME, formula_predict
from ara_sphere_orientation_roll_predictor import EPS


HERE = Path(__file__).resolve().parent
FIT_JSON = HERE / "ara_layered_sand_parameter_search_result.json"
CORR_JSON = HERE / "ara_layered_sand_correlation_search_result.json"
OUT_JSON = HERE / "ara_layered_sand_closed_cutoff_result.json"
OUT_JS = HERE / "ara_layered_sand_closed_cutoff_result.js"

CUTOFFS = ["2010-01-01", "2015-01-01", "2017-01-01", "2020-01-01"]
END_DATE = "2025-12-01"

MANUAL_SCREENSHOT_PARAMS = {
    "floor_drive": 1.66,
    "lower_speed": 0.22,
    "contact_transfer": 0.95,
    "second_contact": 0.82,
    "wobble": 1.05,
    "own_spin": 0.68,
    "terrain_pull": 1.59,
    "terrain_spill": 0.06,
    "roll_to_ara": 1.99,
    "roll_to_phase": 234.0,
    "phase_terrain": 3.27,
    "ara_terrain": 1.40,
    "upper_pressure": 1.76,
    "upper_grip": 1.67,
    "upper_brake": 1.65,
    "measured_roll": 3.01,
}

WAVECYCLE_SCREENSHOT_PARAMS = {
    "floor_drive": 1.08,
    "lower_speed": 2.58,
    "contact_transfer": 0.77,
    "second_contact": 0.60,
    "wobble": 0.42,
    "own_spin": 0.72,
    "terrain_pull": 0.90,
    "terrain_spill": 0.23,
    "roll_to_ara": 0.30,
    "roll_to_phase": 360.0,
    "phase_terrain": 1.14,
    "ara_terrain": 0.39,
    "upper_pressure": 2.86,
    "upper_grip": 0.24,
    "upper_brake": 0.74,
    "measured_roll": 1.0,
}


def date_string(value):
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def add_month(date, months=1):
    return pd.Timestamp(date) + pd.DateOffset(months=months)


def month_delta(start, end):
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    return (end.year - start.year) * 12 + (end.month - start.month)


def phase_clock(date):
    # This matches the atlas phase: 2001-02-01 has phase 283.404255...
    anchor_date = pd.Timestamp("2001-02-01")
    anchor_phase = 283.40425531914843
    return float((anchor_phase + month_delta(anchor_date, date) * 360.0 / HOME) % 360.0)


def corr(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if len(xs) < 3 or np.std(xs) <= EPS or np.std(ys) <= EPS:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def score(rows, key):
    usable = [row for row in rows if row.get(key) is not None and np.isfinite(row.get(key))]
    pred = np.asarray([row[key] for row in usable], dtype=float)
    actual = np.asarray([row["actual"] for row in usable], dtype=float)
    baseline = np.asarray([row["cutoff_value"] for row in usable], dtype=float)
    truth_delta = actual - baseline
    pred_delta = pred - baseline
    turn_mask = np.abs(truth_delta) > EPS
    return {
        "n": int(len(usable)),
        "mae": float(np.mean(np.abs(pred - actual))) if len(usable) else None,
        "corr": corr(pred, actual),
        "direction_from_cutoff": float(np.mean(np.sign(pred_delta[turn_mask]) == np.sign(truth_delta[turn_mask])))
        if np.any(turn_mask)
        else None,
        "amp_ratio": float(np.std(pred_delta) / np.std(truth_delta)) if np.std(truth_delta) > EPS else None,
    }


def fit_partner_closure(frame, cutoff_date):
    past = frame.loc[:pd.Timestamp(cutoff_date)].copy()
    nino = past["NINO"].values.astype(float)
    soi = past["SOI"].values.astype(float)
    pdo = past["PDO"].values.astype(float)
    soi_slope, soi_intercept = np.polyfit(nino, soi, 1)
    pdo_slope, pdo_intercept = np.polyfit(nino, pdo, 1)
    return {
        "soi_intercept": float(soi_intercept),
        "soi_slope": float(soi_slope),
        "pdo_intercept": float(pdo_intercept),
        "pdo_slope": float(pdo_slope),
    }


def close_partners(prev, pred_nino, closure):
    soi_target = closure["soi_intercept"] + closure["soi_slope"] * pred_nino
    pdo_target = closure["pdo_intercept"] + closure["pdo_slope"] * pred_nino
    return {
        "NINO": float(pred_nino),
        "SOI": float(0.72 * prev["SOI"] + 0.28 * soi_target),
        "PDO": float(0.96 * prev["PDO"] + 0.04 * pdo_target),
    }


def make_formula_row(origin, current_nino):
    return {
        "origin": date_string(origin),
        "target": date_string(add_month(origin, 1)),
        "current": float(current_nino),
        "actual": None,
        "ara_current": float(value_to_ara(current_nino)),
        "phase_clock_origin": phase_clock(origin),
    }


def run_closed_path(frame, cutoff_date, params, name):
    cutoff = pd.Timestamp(cutoff_date)
    end = pd.Timestamp(END_DATE)
    closure = fit_partner_closure(frame, cutoff)
    synthetic = frame.loc[:cutoff].copy()
    cutoff_value = float(frame.loc[cutoff, "NINO"])
    current_date = cutoff
    current = {
        "NINO": float(frame.loc[cutoff, "NINO"]),
        "SOI": float(frame.loc[cutoff, "SOI"]),
        "PDO": float(frame.loc[cutoff, "PDO"]),
    }
    records = []
    while current_date < end:
        row = make_formula_row(current_date, current["NINO"])
        prediction = formula_predict(synthetic, row, 1, params)
        next_date = add_month(current_date, 1)
        next_values = close_partners(current, prediction["value"], closure)
        synthetic.loc[next_date, ["NINO", "SOI", "PDO"]] = [
            next_values["NINO"],
            next_values["SOI"],
            next_values["PDO"],
        ]
        actual = float(frame.loc[next_date, "NINO"]) if next_date in frame.index else None
        lead = month_delta(cutoff, next_date)
        records.append(
            {
                "date": date_string(next_date),
                "lead_month": int(lead),
                "actual": actual,
                "cutoff_value": cutoff_value,
                "persistence": cutoff_value,
                name: float(next_values["NINO"]),
                f"{name}_SOI": float(next_values["SOI"]),
                f"{name}_PDO": float(next_values["PDO"]),
                f"{name}_formula_raw": float(prediction["value"]),
                f"{name}_arrival_ara": float(prediction["arrival_ara"]),
                f"{name}_arrival_phase": float(prediction["arrival_phase"]),
            }
        )
        current_date = next_date
        current = next_values
    return records


def merge_paths(paths):
    by_date = {}
    for path in paths:
        for row in path:
            key = row["date"]
            if key not in by_date:
                by_date[key] = {
                    "date": row["date"],
                    "lead_month": row["lead_month"],
                    "actual": row["actual"],
                    "cutoff_value": row["cutoff_value"],
                    "persistence": row["persistence"],
                }
            by_date[key].update({k: v for k, v in row.items() if k not in by_date[key] or k.endswith(("_SOI", "_PDO", "_formula_raw", "_arrival_ara", "_arrival_phase"))})
            for k, v in row.items():
                if k not in by_date[key]:
                    by_date[key][k] = v
    return [by_date[key] for key in sorted(by_date)]


def score_windows(records, model_keys):
    windows = {
        "lead_1_12": [row for row in records if 1 <= row["lead_month"] <= 12],
        "lead_13_36": [row for row in records if 13 <= row["lead_month"] <= 36],
        "lead_37_plus": [row for row in records if row["lead_month"] >= 37],
        "all": records,
    }
    out = {}
    for window, rows in windows.items():
        out[window] = {key: score(rows, key) for key in ["persistence", *model_keys]}
    return out


def load_presets():
    fit = json.loads(FIT_JSON.read_text(encoding="utf-8")) if FIT_JSON.exists() else {}
    corr = json.loads(CORR_JSON.read_text(encoding="utf-8")) if CORR_JSON.exists() else {}
    corr_family = corr.get("best_holdout_corr_family", {}).get("family")
    corr_params = corr.get("models", {}).get(corr_family, {}).get("params") if corr_family else None
    presets = {
        "base_formula": FORMULA,
        "fitted_formula": fit.get("best_params", FORMULA),
        "manual_screenshot": MANUAL_SCREENSHOT_PARAMS,
        "wavecycle_screenshot": WAVECYCLE_SCREENSHOT_PARAMS,
    }
    if corr_params:
        presets["best_corr_fit"] = corr_params
    return presets


def run():
    frame = load_enso_frame()
    presets = load_presets()
    results = {}
    print("ARA layered-sand closed cutoff run")
    print("=" * 100)
    print("After each cutoff, future NINO/SOI/PDO are generated internally. No future observed predictors are read.")
    print()
    for cutoff in CUTOFFS:
        model_keys = list(presets.keys())
        paths = [run_closed_path(frame, cutoff, params, name) for name, params in presets.items()]
        records = merge_paths(paths)
        evaluations = score_windows(records, model_keys)
        results[cutoff] = {
            "cutoff": cutoff,
            "records": clean_for_json(records),
            "evaluations": clean_for_json(evaluations),
        }
        print(cutoff)
        for key in model_keys:
            s = evaluations["all"][key]
            print(
                f"  {key:22s} MAE={s['mae']:.3f} corr={s['corr']:+.3f}"
                f" dir={s['direction_from_cutoff']:.3f} amp={s['amp_ratio']:.3f}"
            )
        p = evaluations["all"]["persistence"]
        print(f"  {'persistence':22s} MAE={p['mae']:.3f} corr={p['corr'] if p['corr'] is not None else float('nan'):+.3f}")
        print()

    out = {
        "date": "2026-05-26",
        "method": "closed/autonomous cutoff run for layered-sand formula",
        "cutoffs": CUTOFFS,
        "end_date": END_DATE,
        "presets": clean_for_json(presets),
        "advance_defaults_not_used": ADVANCE_DEFAULTS,
        "leakage_guard": [
            "For each cutoff, synthetic frame contains observed NINO/SOI/PDO only up to the cutoff.",
            "After cutoff, NINO is generated by the formula one month at a time.",
            "After cutoff, SOI/PDO are generated by a pre-cutoff anti-phase/slow-reservoir closure.",
            "Actual post-cutoff NINO is used only for scoring and plotting truth.",
            "This is an autonomous path test, not the old shifted-line terrain-nowcast diagnostic.",
        ],
        "partner_closure": {
            "SOI": "0.72 * previous SOI + 0.28 * pre-cutoff linear anti-phase target from predicted NINO",
            "PDO": "0.96 * previous PDO + 0.04 * pre-cutoff linear slow-reservoir target from predicted NINO",
        },
        "results": clean_for_json(results),
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LAYERED_SAND_CLOSED_CUTOFF = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
