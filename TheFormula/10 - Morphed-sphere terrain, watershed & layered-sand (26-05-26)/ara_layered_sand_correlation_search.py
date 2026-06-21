"""
ara_layered_sand_correlation_search.py

Correlation-only variable search for the layered-sand ARA formula and its
strict advance variants.

Guardrail:
  Tuning variables against truth is calibration. To avoid leakage claims, this
  script fits on pre-2017 rows only, then reports 2017+ holdout separately. All
  predictors still use only origin-time spin packets and current ARA/contact
  coordinates when making each prediction.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ara_geometry_transport_test import clean_for_json
from ara_layered_sand_advance_operator_test import advance_spin, read_value, run_cascade_from_spins
from ara_layered_sand_parameter_search import BOUNDS as FORMULA_BOUNDS
from ara_layered_sand_parameter_search import PARAM_ORDER, predict_from_record
from ara_layered_sand_single_formula import FORMULA
from ara_sphere_orientation_roll_predictor import EPS


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_layered_sand_single_formula_result.json"
FIT_JSON = HERE / "ara_layered_sand_parameter_search_result.json"
OUT_JSON = HERE / "ara_layered_sand_correlation_search_result.json"
OUT_JS = HERE / "ara_layered_sand_correlation_search_result.js"

TRAIN_CUTOFF = "2017-01-01"
FOCUS_HORIZONS = [6, 12, 24]
SEED = 260526

ADVANCE_ORDER = [
    "phase_read_gain",
    "layer_roll_gain",
    "layer_roll_fast_gain",
    "lower_terrain_base_mix",
    "lower_terrain_roll_gain",
]

ADVANCE_DEFAULTS = {
    "phase_read_gain": 1.0,
    "layer_roll_gain": 1.0,
    "layer_roll_fast_gain": 2.0,
    "lower_terrain_base_mix": 1.0,
    "lower_terrain_roll_gain": 0.0,
}

ADVANCE_BOUNDS = {
    "phase_read_gain": (0.0, 4.0),
    "layer_roll_gain": (0.0, 6.0),
    "layer_roll_fast_gain": (0.0, 8.0),
    "lower_terrain_base_mix": (0.0, 1.0),
    "lower_terrain_roll_gain": (0.0, 6.0),
}

FAMILIES = [
    "Formula_Adjustable",
    "Advance_Phase_Read",
    "Advance_Layer_Roll",
    "Advance_Layer_Roll_Fast",
    "Advance_Lower_Terrain_Base",
    "Combined_Advance",
]


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def corr(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if len(xs) < 3 or np.std(xs) <= EPS or np.std(ys) <= EPS:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def score_rows(rows, pred_key):
    usable = [row for row in rows if row.get(pred_key) is not None and np.isfinite(row.get(pred_key))]
    pred = np.asarray([row[pred_key] for row in usable], dtype=float)
    actual = np.asarray([row["actual"] for row in usable], dtype=float)
    current = np.asarray([row["current"] for row in usable], dtype=float)
    truth_delta = actual - current
    pred_delta = pred - current
    turn_mask = np.abs(truth_delta) > EPS
    return {
        "n": int(len(usable)),
        "mae": float(np.mean(np.abs(pred - actual))) if len(usable) else None,
        "corr": corr(pred, actual),
        "corr_with_current": corr(pred, current),
        "direction": float(np.mean(np.sign(pred_delta[turn_mask]) == np.sign(truth_delta[turn_mask])))
        if np.any(turn_mask)
        else None,
        "amp_ratio": float(np.std(pred_delta) / np.std(truth_delta)) if np.std(truth_delta) > EPS else None,
    }


def by_horizon(rows, pred_key):
    out = {}
    for horizon in sorted({int(row["horizon"]) for row in rows}):
        hrows = [row for row in rows if int(row["horizon"]) == horizon]
        out[str(horizon)] = score_rows(hrows, pred_key)
    return out


def vector_to_params(vector):
    return {key: float(value) for key, value in zip(PARAM_ORDER, vector[: len(PARAM_ORDER)])}


def vector_to_advance(vector):
    start = len(PARAM_ORDER)
    return {key: float(value) for key, value in zip(ADVANCE_ORDER, vector[start:])}


def params_to_vector(params, advance):
    return np.asarray(
        [params[key] for key in PARAM_ORDER] + [advance[key] for key in ADVANCE_ORDER],
        dtype=float,
    )


def bounds_vector():
    return [FORMULA_BOUNDS[key] for key in PARAM_ORDER] + [ADVANCE_BOUNDS[key] for key in ADVANCE_ORDER]


def predict_family(row, horizon, params, advance, family):
    if family == "Formula_Adjustable":
        return float(predict_from_record(row, horizon, params)[0])

    spins = [dict(spin) for spin in row["formula"]["spins"]]
    phase_extra = 0.0
    base_mix = 0.0

    if family in {"Advance_Phase_Read", "Combined_Advance"}:
        phase_extra = 360.0 * (float(horizon) / 12.0) * float(advance["phase_read_gain"])

    if family == "Advance_Layer_Roll":
        spins = [advance_spin(spin, horizon, i, params, advance["layer_roll_gain"]) for i, spin in enumerate(spins)]
    elif family == "Advance_Layer_Roll_Fast":
        spins = [advance_spin(spin, horizon, i, params, advance["layer_roll_fast_gain"]) for i, spin in enumerate(spins)]
    elif family == "Advance_Lower_Terrain_Base":
        if abs(float(advance["lower_terrain_roll_gain"])) > EPS:
            spins = [
                advance_spin(spin, horizon, i, params, advance["lower_terrain_roll_gain"])
                for i, spin in enumerate(spins)
            ]
        base_mix = float(advance["lower_terrain_base_mix"])
    elif family == "Combined_Advance":
        spins = [advance_spin(spin, horizon, i, params, advance["layer_roll_gain"]) for i, spin in enumerate(spins)]
        base_mix = float(advance["lower_terrain_base_mix"])

    active_row = {**row, "_active_params": params}
    state, delta_ara, delta_phase, upper = run_cascade_from_spins(active_row, horizon, params, spins, phase_extra)
    lower_base = float(state.get("terrain_force_ara", state["ara"]))
    base_ara = (1.0 - base_mix) * float(row["ara_current"]) + base_mix * lower_base
    return read_value(active_row, state, delta_ara, delta_phase, upper, base_ara)["value"]


def predict_rows(rows, params, advance, family, key):
    out = []
    for row in rows:
        item = dict(row)
        try:
            pred = predict_family(row, int(row["horizon"]), params, advance, family)
        except Exception:
            pred = None
        item[key] = pred
        out.append(item)
    return out


def objective_factory(rows, family):
    actual = np.asarray([float(row["actual"]) for row in rows], dtype=float)

    def objective(vector):
        params = vector_to_params(vector)
        advance = vector_to_advance(vector)
        preds = []
        for row in rows:
            pred = predict_family(row, int(row["horizon"]), params, advance, family)
            if not np.isfinite(pred):
                return 10.0
            preds.append(pred)
        model_corr = corr(preds, actual)
        if model_corr is None:
            return 10.0
        # Correlation only. No MAE term. Small invalid-range guard only.
        return -model_corr

    return objective


def random_candidates(rng, base_vector, n=160, jitter=0.32):
    bounds = bounds_vector()
    candidates = [np.asarray(base_vector, dtype=float)]
    lo = np.asarray([b[0] for b in bounds], dtype=float)
    hi = np.asarray([b[1] for b in bounds], dtype=float)
    span = hi - lo
    for _ in range(n):
        if rng.random() < 0.62:
            vector = np.asarray(base_vector, dtype=float) + rng.normal(0.0, jitter, len(bounds)) * span
            vector = np.clip(vector, lo, hi)
        else:
            vector = lo + rng.random(len(bounds)) * span
        candidates.append(vector)
    return candidates


def coordinate_polish(objective, vector, rounds=3):
    bounds = bounds_vector()
    lo = np.asarray([b[0] for b in bounds], dtype=float)
    hi = np.asarray([b[1] for b in bounds], dtype=float)
    best = np.asarray(vector, dtype=float)
    best_fun = objective(best)
    step = 0.18 * (hi - lo)
    for _ in range(rounds):
        improved = False
        for i in range(len(best)):
            for direction in (-1.0, 1.0):
                candidate = best.copy()
                candidate[i] = clamp(candidate[i] + direction * step[i], lo[i], hi[i])
                fun = objective(candidate)
                if fun < best_fun:
                    best = candidate
                    best_fun = fun
                    improved = True
        step *= 0.5
        if not improved and float(np.max(step)) < 1e-3:
            break
    return best, float(best_fun)


def fit_family(train_rows, family, base_params, base_advance):
    rng = np.random.default_rng(SEED + 31 * FAMILIES.index(family))
    objective = objective_factory(train_rows, family)
    base_vector = params_to_vector(base_params, base_advance)
    candidates = random_candidates(rng, base_vector)
    ranked = sorted(((objective(vector), vector) for vector in candidates), key=lambda item: item[0])
    best_fun, best_vector = ranked[0]

    polished_vector, polished_fun = coordinate_polish(objective, best_vector)
    if polished_fun < best_fun:
        best_fun = polished_fun
        best_vector = polished_vector

    return vector_to_params(best_vector), vector_to_advance(best_vector), float(-best_fun)


def load_rows():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    fit = json.loads(FIT_JSON.read_text(encoding="utf-8"))
    rows = []
    for horizon in data["horizons_months"]:
        for row in data["viz_records"][str(horizon)]:
            rows.append({**row, "horizon": int(horizon)})
    return rows, fit


def split_rows(rows):
    focus = [row for row in rows if int(row["horizon"]) in FOCUS_HORIZONS]
    return {
        "train_focus_pre2017": [row for row in focus if row["origin"] < TRAIN_CUTOFF],
        "holdout_focus_2017_on": [row for row in focus if row["origin"] >= TRAIN_CUTOFF],
        "all_focus": focus,
        "all_horizons": rows,
    }


def records_for_viz(rows, family_predictions):
    out = {}
    for row in rows:
        h = str(row["horizon"])
        record = {
            "origin": row["origin"],
            "target": row["target"],
            "current": round(float(row["current"]), 6),
            "actual": round(float(row["actual"]), 6),
        }
        for family, predictions in family_predictions.items():
            pred_row = predictions[(row["horizon"], row["origin"], row["target"])]
            record[family] = round(float(pred_row[f"{family}_corrfit"]), 6)
        out.setdefault(h, []).append(record)
    return out


def run():
    rows, fit = load_rows()
    splits = split_rows(rows)
    base_params = fit["best_params"]
    base_advance = dict(ADVANCE_DEFAULTS)

    print("ARA layered-sand correlation-only variable search")
    print("=" * 100)
    print("Objective: maximize train correlation only. Holdout is the leakage-free check.")
    print(f"Train rows: {len(splits['train_focus_pre2017'])} | Holdout rows: {len(splits['holdout_focus_2017_on'])}")
    print()

    models = {}
    family_predictions = {}
    for family in FAMILIES:
        print(f"Fitting {family}...")
        params, advance, train_corr = fit_family(splits["train_focus_pre2017"], family, base_params, base_advance)
        key = f"{family}_corrfit"
        predicted = predict_rows(rows, params, advance, family, key)
        family_predictions[family] = {
            (row["horizon"], row["origin"], row["target"]): row for row in predicted
        }
        evaluations = {name: score_rows(split, key) for name, split in split_rows(predicted).items()}
        evaluations["by_horizon"] = {
            name: by_horizon(split, key) for name, split in split_rows(predicted).items()
        }
        models[family] = {
            "train_objective_corr": train_corr,
            "params": params,
            "advance": advance,
            "evaluations": evaluations,
        }
        hold = evaluations["holdout_focus_2017_on"]
        train = evaluations["train_focus_pre2017"]
        print(
            f"  train corr={train['corr']:+.3f} MAE={train['mae']:.3f}"
            f" | holdout corr={hold['corr']:+.3f} MAE={hold['mae']:.3f}"
            f" dir={hold['direction']:.3f} amp={hold['amp_ratio']:.3f}"
        )

    best_holdout = max(
        (
            (family, result["evaluations"]["holdout_focus_2017_on"]["corr"])
            for family, result in models.items()
            if result["evaluations"]["holdout_focus_2017_on"]["corr"] is not None
        ),
        key=lambda item: item[1],
    )
    out = {
        "date": "2026-05-26",
        "method": "correlation-only calibration of layered-sand formula and advance variables",
        "leakage_guard": [
            "Variables are fitted against truth only on train_focus_pre2017.",
            "2017+ holdout rows are never used by the optimizer.",
            "Each prediction uses only origin-time spin packets and current ARA/contact coordinates.",
            "Objective is train correlation only; MAE is reported but not optimized.",
        ],
        "train_cutoff": TRAIN_CUTOFF,
        "focus_horizons": FOCUS_HORIZONS,
        "families": FAMILIES,
        "parameter_order": PARAM_ORDER,
        "advance_order": ADVANCE_ORDER,
        "base_params": FORMULA,
        "starting_params": base_params,
        "starting_advance": base_advance,
        "best_holdout_corr_family": {"family": best_holdout[0], "corr": best_holdout[1]},
        "models": clean_for_json(models),
        "viz_records": clean_for_json(records_for_viz(rows, family_predictions)),
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LAYERED_SAND_CORRELATION_SEARCH = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print()
    print(f"Best holdout corr: {best_holdout[0]} {best_holdout[1]:+.3f}")
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
