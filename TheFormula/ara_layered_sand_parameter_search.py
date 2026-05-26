"""
ara_layered_sand_parameter_search.py

Fit Formula_Adjustable constants for the single layered-sand formula, then
test whether those constants carry to held-out dates and horizons.

Important guard:
  The optimiser does see truth on the selected training rows. That makes the
  fitted constants calibration results, not proof. Generalisation is checked by
  applying the same constants to later dates and separate horizons.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution, minimize

from ara_fractal_sphere_terrain_reader import ara_to_value
from ara_geometry_transport_test import clean_for_json
from ara_layered_sand_single_formula import (
    FORMULA,
    HOME,
    PHI,
    clamp,
    propagate_layer,
    read_sphere_terrain,
)
from ara_sphere_orientation_roll_predictor import EPS, sign


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_layered_sand_single_formula_result.json"
OUT_JSON = HERE / "ara_layered_sand_parameter_search_result.json"
OUT_JS = HERE / "ara_layered_sand_parameter_search_result.js"

PARAM_ORDER = [
    "floor_drive",
    "lower_speed",
    "contact_transfer",
    "second_contact",
    "wobble",
    "own_spin",
    "terrain_pull",
    "terrain_spill",
    "roll_to_ara",
    "roll_to_phase",
    "phase_terrain",
    "ara_terrain",
    "upper_pressure",
    "upper_grip",
    "upper_brake",
    "measured_roll",
]

BOUNDS = {
    "floor_drive": (0.0, 4.0),
    "lower_speed": (0.0, 8.0),
    "contact_transfer": (0.0, 2.0),
    "second_contact": (0.0, 1.0),
    "wobble": (0.0, 3.0),
    "own_spin": (0.0, 1.0),
    "terrain_pull": (0.0, 4.0),
    "terrain_spill": (0.0, 2.0),
    "roll_to_ara": (0.0, 5.0),
    "roll_to_phase": (0.0, 360.0),
    "phase_terrain": (0.0, 4.0),
    "ara_terrain": (0.0, 4.0),
    "upper_pressure": (0.0, 4.0),
    "upper_grip": (0.0, 2.0),
    "upper_brake": (0.0, 2.0),
    "measured_roll": (0.0, 8.0),
}

TRAIN_CUTOFF = "2017-01-01"
FOCUS_HORIZONS = [6, 12, 24]


def vector_to_params(vector):
    return {key: float(value) for key, value in zip(PARAM_ORDER, vector)}


def params_to_vector(params):
    return np.asarray([params[key] for key in PARAM_ORDER], dtype=float)


def month_key(date_string):
    return str(date_string)


def predict_from_record(row, horizon, params):
    spins = row["formula"]["spins"]
    upper = row["formula"]["upper"]
    floor = spins[0]
    state = {
        "name": "floor",
        "period": float(floor["period"]),
        "forward": float(floor["forward"]) * params["floor_drive"],
        "lateral": float(floor["lateral"]) * params["floor_drive"],
        "twist": float(floor["twist"]) * params["floor_drive"],
        "pressure": float(floor["pressure"]),
        "ara": float(floor["ara"]),
    }
    phase_deg = float(row["phase_clock_origin"])
    for i, layer_spin in enumerate(spins[1:], start=1):
        second_spin = spins[max(0, i - 2)]
        state = propagate_layer(state, second_spin, layer_spin, upper, i, params, phase_deg)

    horizon_gain = math.sqrt(max(float(horizon), 1.0) / HOME)
    upper_brake = 1.0 + params["upper_pressure"] * params["upper_brake"] * abs(upper["compression"])
    measured = params["measured_roll"] * horizon_gain / upper_brake
    floor_phase = params["floor_drive"] * (float(horizon) / HOME) * 360.0
    delta_ara = measured * params["roll_to_ara"] * (state["forward"] + 0.18 * state["lateral"])
    delta_phase = floor_phase + measured * params["roll_to_phase"] * (
        state["lateral"] + 0.45 * state["twist"] + 0.18 * state["forward"]
    )
    arrival_ara = clamp(float(row["ara_current"]) + delta_ara, 0.0, 2.0)
    arrival_phase = phase_deg + delta_phase

    terrain = read_sphere_terrain(
        arrival_ara,
        float(row["ara_current"]),
        arrival_phase,
        float(state["pressure"]),
        float(state["forward"]),
        float(upper["compression"]),
        params,
    )
    return float(ara_to_value(terrain["force_ara"])), float(delta_ara), float(delta_phase)


def load_rows():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    rows = []
    for h in data["horizons_months"]:
        for row in data["viz_records"][str(h)]:
            rows.append({**row, "horizon": int(h)})
    return rows, data


def split_rows(rows):
    focus = [row for row in rows if int(row["horizon"]) in FOCUS_HORIZONS]
    train = [row for row in focus if month_key(row["origin"]) < TRAIN_CUTOFF]
    holdout = [row for row in focus if month_key(row["origin"]) >= TRAIN_CUTOFF]
    return {
        "train_focus_pre2017": train,
        "holdout_focus_2017_on": holdout,
        "all_focus": focus,
        "all_horizons": rows,
    }


def metrics(rows, params):
    preds = []
    actual = []
    current = []
    delta_ara = []
    delta_phase = []
    by_horizon = {}
    for row in rows:
        pred, dara, dphase = predict_from_record(row, row["horizon"], params)
        preds.append(pred)
        actual.append(float(row["actual"]))
        current.append(float(row["current"]))
        delta_ara.append(abs(dara))
        delta_phase.append(dphase)
        by_horizon.setdefault(str(row["horizon"]), []).append({**row, "_pred": pred, "_dara": dara, "_dphase": dphase})
    preds = np.asarray(preds, dtype=float)
    actual = np.asarray(actual, dtype=float)
    current = np.asarray(current, dtype=float)
    mae = float(np.mean(np.abs(preds - actual))) if len(rows) else None
    corr = float(np.corrcoef(preds, actual)[0, 1]) if len(rows) > 2 and np.std(preds) > EPS and np.std(actual) > EPS else None
    truth_delta = actual - current
    pred_delta = preds - current
    turn_mask = np.abs(truth_delta) > EPS
    direction = float(np.mean(np.sign(pred_delta[turn_mask]) == np.sign(truth_delta[turn_mask]))) if np.any(turn_mask) else None
    amp_ratio = float(np.std(pred_delta) / np.std(truth_delta)) if np.std(truth_delta) > EPS else None
    out = {
        "n": int(len(rows)),
        "mae": mae,
        "corr": corr,
        "direction": direction,
        "amp_ratio": amp_ratio,
        "mean_abs_delta_ara": float(np.mean(delta_ara)) if delta_ara else None,
        "mean_delta_phase": float(np.mean(delta_phase)) if delta_phase else None,
    }
    if len(by_horizon) > 1:
        out["by_horizon"] = {h: metrics(hrows, params) for h, hrows in sorted(by_horizon.items(), key=lambda item: int(item[0]))}
    return out


def objective_factory(rows):
    truth_delta = np.asarray([float(row["actual"]) - float(row["current"]) for row in rows], dtype=float)
    truth_std = max(float(np.std(truth_delta)), EPS)

    def objective(vector):
        params = vector_to_params(vector)
        preds = []
        actual = []
        current = []
        for row in rows:
            pred, _, _ = predict_from_record(row, row["horizon"], params)
            if not np.isfinite(pred):
                return 1e9
            preds.append(pred)
            actual.append(float(row["actual"]))
            current.append(float(row["current"]))
        preds = np.asarray(preds, dtype=float)
        actual_a = np.asarray(actual, dtype=float)
        current_a = np.asarray(current, dtype=float)
        mae_norm = float(np.mean(np.abs(preds - actual_a)) / truth_std)
        pred_delta = preds - current_a
        truth_delta_local = actual_a - current_a
        corr = float(np.corrcoef(preds, actual_a)[0, 1]) if np.std(preds) > EPS and np.std(actual_a) > EPS else -1.0
        amp_ratio = float(np.std(pred_delta) / max(np.std(truth_delta_local), EPS))
        amp_penalty = abs(math.log(max(amp_ratio, 1e-4)))
        turn_mask = np.abs(truth_delta_local) > EPS
        direction = float(np.mean(np.sign(pred_delta[turn_mask]) == np.sign(truth_delta_local[turn_mask]))) if np.any(turn_mask) else 0.0
        saturation = float(np.mean(np.abs(preds) > 4.0))
        return 0.56 * mae_norm + 0.24 * (1.0 - corr) + 0.12 * amp_penalty + 0.08 * (1.0 - direction) + 0.20 * saturation

    return objective


def fit_params(train_rows):
    bounds = [BOUNDS[key] for key in PARAM_ORDER]
    objective = objective_factory(train_rows)
    baseline = params_to_vector(FORMULA)
    print(f"Baseline objective: {objective(baseline):.6f}")
    result = differential_evolution(
        objective,
        bounds,
        seed=260526,
        maxiter=28,
        popsize=7,
        tol=0.008,
        polish=False,
        updating="immediate",
        workers=1,
    )
    print(f"DE objective: {result.fun:.6f}")
    polished = minimize(
        objective,
        result.x,
        method="Powell",
        bounds=bounds,
        options={"maxiter": 260, "xtol": 1e-4, "ftol": 1e-4, "disp": False},
    )
    best = polished if polished.fun <= result.fun else result
    print(f"Best objective: {best.fun:.6f}")
    return vector_to_params(best.x), float(best.fun)


def predictions_for_viz(rows, params):
    out = {}
    for row in rows:
        h = str(row["horizon"])
        pred, dara, dphase = predict_from_record(row, row["horizon"], params)
        out.setdefault(h, []).append(
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": row["current"],
                "actual": row["actual"],
                "Formula": row["Formula"],
                "Formula_Fitted": round(pred, 6),
                "delta_ara": round(dara, 6),
                "delta_phase": round(dphase, 6),
            }
        )
    return out


def run():
    rows, source = load_rows()
    splits = split_rows(rows)
    print("ARA layered-sand parameter search")
    print("=" * 100)
    print(f"Training rows: {len(splits['train_focus_pre2017'])} | Holdout rows: {len(splits['holdout_focus_2017_on'])}")
    best_params, objective_value = fit_params(splits["train_focus_pre2017"])
    evaluations = {name: metrics(split_rows_, best_params) for name, split_rows_ in splits.items()}
    baseline_evaluations = {name: metrics(split_rows_, FORMULA) for name, split_rows_ in splits.items()}

    print()
    print("Best parameters:")
    for key in PARAM_ORDER:
        print(f"  {key:18s} {best_params[key]:.6f}")
    print()
    for name in ["train_focus_pre2017", "holdout_focus_2017_on", "all_focus", "all_horizons"]:
        e = evaluations[name]
        b = baseline_evaluations[name]
        print(
            f"{name:24s}"
            f" fitted MAE={e['mae']:.3f} corr={e['corr']:+.3f} dir={e['direction']:.3f} amp={e['amp_ratio']:.3f}"
            f" | base MAE={b['mae']:.3f} corr={b['corr']:+.3f} dir={b['direction']:.3f} amp={b['amp_ratio']:.3f}"
        )

    out = {
        "date": "2026-05-26",
        "method": "Formula_Adjustable parameter calibration",
        "fit_warning": "The fitted constants see truth on train_focus_pre2017. Holdout scores are the first generalisation check.",
        "train_cutoff": TRAIN_CUTOFF,
        "focus_horizons": FOCUS_HORIZONS,
        "parameter_order": PARAM_ORDER,
        "bounds": BOUNDS,
        "baseline_params": FORMULA,
        "best_params": best_params,
        "objective_value": objective_value,
        "evaluations": evaluations,
        "baseline_evaluations": baseline_evaluations,
        "viz_records": predictions_for_viz(rows, best_params),
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LAYERED_SAND_PARAMETER_SEARCH = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
