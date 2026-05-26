"""
ara_layered_sand_shape_timing_diagnostic.py

Diagnostics for the user's observation:
  "Formula has a good shape, but it looks offset."

This script does not ask whether MAE wins first. It checks:
  1. best-lag cross-correlation
  2. affine remap actual ~= a * formula + b
  3. peak/trough sequence matching
  4. phase correction only: one global origin-step offset fit on train

Lag convention:
  shift_steps > 0 means the formula is late. To compare with truth, use a
  later formula point for the current truth point. Visually this means "shift
  the formula line left" by shift_steps origin intervals.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ara_geometry_transport_test import clean_for_json


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_layered_sand_parameter_search_result.json"
OUT_JSON = HERE / "ara_layered_sand_shape_timing_diagnostic_result.json"
OUT_JS = HERE / "ara_layered_sand_shape_timing_diagnostic_result.js"

TRAIN_CUTOFF = "2017-01-01"
FOCUS_HORIZONS = [6, 12, 24]
SHIFT_RANGE = list(range(-8, 9))
MODEL_KEYS = ["Formula", "Formula_Fitted"]


def mean(values):
    return float(np.mean(values)) if len(values) else None


def corr(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if len(x) < 3 or np.std(x) <= 1e-12 or np.std(y) <= 1e-12:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def mae(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    return float(np.mean(np.abs(x - y))) if len(x) else None


def sign(value):
    if value > 1e-9:
        return 1
    if value < -1e-9:
        return -1
    return 0


def direction_accuracy(pred, actual, current):
    pred = np.asarray(pred, dtype=float)
    actual = np.asarray(actual, dtype=float)
    current = np.asarray(current, dtype=float)
    truth_delta = actual - current
    pred_delta = pred - current
    mask = np.abs(truth_delta) > 1e-12
    if not np.any(mask):
        return None
    return float(np.mean(np.sign(pred_delta[mask]) == np.sign(truth_delta[mask])))


def load_rows():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    rows = []
    for horizon, horizon_rows in data["viz_records"].items():
        for row in horizon_rows:
            rows.append({**row, "horizon": int(horizon)})
    return rows, data


def ordered(rows):
    return sorted(rows, key=lambda row: row["origin"])


def split_rows(rows):
    focus = [row for row in rows if row["horizon"] in FOCUS_HORIZONS]
    return {
        "train_focus_pre2017": [row for row in focus if row["origin"] < TRAIN_CUTOFF],
        "holdout_focus_2017_on": [row for row in focus if row["origin"] >= TRAIN_CUTOFF],
        "all_focus": focus,
        "all_horizons": rows,
    }


def rows_by_horizon(rows):
    out = {}
    for row in rows:
        out.setdefault(str(row["horizon"]), []).append(row)
    return {horizon: ordered(horizon_rows) for horizon, horizon_rows in out.items()}


def shifted_arrays(rows, model_key, shift_steps):
    rows = ordered(rows)
    pred = []
    actual = []
    current = []
    origins = []
    for i, row in enumerate(rows):
        j = i + shift_steps
        if j < 0 or j >= len(rows):
            continue
        source = rows[j]
        pred.append(float(source[model_key]))
        actual.append(float(row["actual"]))
        current.append(float(row["current"]))
        origins.append(row["origin"])
    return np.asarray(pred), np.asarray(actual), np.asarray(current), origins


def score_shift(rows, model_key, shift_steps):
    pred, actual, current, origins = shifted_arrays(rows, model_key, shift_steps)
    return {
        "shift_steps": int(shift_steps),
        "shift_months": int(3 * shift_steps),
        "n": int(len(pred)),
        "corr": corr(pred, actual),
        "mae": mae(pred, actual),
        "direction": direction_accuracy(pred, actual, current),
        "origin_start": origins[0] if origins else None,
        "origin_end": origins[-1] if origins else None,
    }


def best_lag(rows, model_key, shifts=SHIFT_RANGE):
    scores = [score_shift(rows, model_key, shift) for shift in shifts]
    valid = [score for score in scores if score["corr"] is not None]
    best = max(valid, key=lambda score: score["corr"]) if valid else None
    zero = next((score for score in scores if score["shift_steps"] == 0), None)
    return {
        "zero_shift": zero,
        "best_shift": best,
        "scores": scores,
    }


def fit_affine(rows, model_key, shift_steps=0):
    pred, actual, _, _ = shifted_arrays(rows, model_key, shift_steps)
    if len(pred) < 2 or np.std(pred) <= 1e-12:
        return {"a": 0.0, "b": mean(actual) or 0.0, "shift_steps": shift_steps}
    a, b = np.polyfit(pred, actual, 1)
    return {"a": float(a), "b": float(b), "shift_steps": int(shift_steps)}


def apply_affine(rows, model_key, affine):
    pred, actual, current, origins = shifted_arrays(rows, model_key, affine["shift_steps"])
    remapped = affine["a"] * pred + affine["b"]
    return {
        "n": int(len(remapped)),
        "mae": mae(remapped, actual),
        "corr": corr(remapped, actual),
        "direction": direction_accuracy(remapped, actual, current),
        "amp_ratio": float(np.std(remapped - current) / np.std(actual - current))
        if len(remapped) and np.std(actual - current) > 1e-12
        else None,
        "origin_start": origins[0] if origins else None,
        "origin_end": origins[-1] if origins else None,
    }


def affine_test(train_rows, holdout_rows, model_key, shift_steps=0):
    affine = fit_affine(train_rows, model_key, shift_steps)
    return {
        "fit": affine,
        "train": apply_affine(train_rows, model_key, affine),
        "holdout": apply_affine(holdout_rows, model_key, affine),
    }


def extrema(values):
    values = np.asarray(values, dtype=float)
    out = []
    for i in range(1, len(values) - 1):
        if values[i] > values[i - 1] and values[i] >= values[i + 1]:
            out.append({"index": i, "type": "peak", "value": float(values[i])})
        elif values[i] < values[i - 1] and values[i] <= values[i + 1]:
            out.append({"index": i, "type": "trough", "value": float(values[i])})
    return out


def peak_trough_match(rows, model_key, max_offset=4):
    rows = ordered(rows)
    actual = np.asarray([row["actual"] for row in rows], dtype=float)
    pred = np.asarray([row[model_key] for row in rows], dtype=float)
    actual_ext = extrema(actual)
    pred_ext = extrema(pred)
    matches = []
    used = set()
    for item in actual_ext:
        candidates = [
            cand
            for cand in pred_ext
            if cand["type"] == item["type"] and cand["index"] not in used and abs(cand["index"] - item["index"]) <= max_offset
        ]
        if not candidates:
            continue
        best = min(candidates, key=lambda cand: abs(cand["index"] - item["index"]))
        used.add(best["index"])
        matches.append(
            {
                "type": item["type"],
                "truth_index": item["index"],
                "formula_index": best["index"],
                "offset_steps": int(best["index"] - item["index"]),
                "offset_months": int(3 * (best["index"] - item["index"])),
                "truth_origin": rows[item["index"]]["origin"],
                "formula_origin": rows[best["index"]]["origin"],
            }
        )
    offsets = [match["offset_steps"] for match in matches]
    exact_type_sequence = [match["type"] for match in matches]
    truth_sequence = [item["type"] for item in actual_ext[: len(exact_type_sequence)]]
    return {
        "truth_extrema": int(len(actual_ext)),
        "formula_extrema": int(len(pred_ext)),
        "matched": int(len(matches)),
        "match_rate": float(len(matches) / len(actual_ext)) if actual_ext else None,
        "mean_offset_steps": mean(offsets),
        "median_offset_steps": float(np.median(offsets)) if offsets else None,
        "mean_abs_offset_steps": mean([abs(offset) for offset in offsets]),
        "sequence_prefix_agreement": float(np.mean([a == b for a, b in zip(exact_type_sequence, truth_sequence)]))
        if truth_sequence
        else None,
        "matches": matches[:30],
    }


def global_best_shift(train_rows, model_key):
    return best_lag(train_rows, model_key)["best_shift"]["shift_steps"]


def phase_correction(train_rows, holdout_rows, model_key):
    shift = global_best_shift(train_rows, model_key)
    return {
        "train_best_shift_steps": int(shift),
        "train_best_shift_months": int(3 * shift),
        "train": score_shift(train_rows, model_key, shift),
        "holdout": score_shift(holdout_rows, model_key, shift),
    }


def run():
    rows, source = load_rows()
    splits = split_rows(rows)
    results = {
        "date": "2026-05-26",
        "method": "shape and timing diagnostics for layered-sand formulas",
        "lag_convention": "positive shift means formula is late; visually shift formula left by shift_steps origin intervals",
        "origin_step_months": 3,
        "train_cutoff": TRAIN_CUTOFF,
        "focus_horizons": FOCUS_HORIZONS,
        "models": {},
    }
    print("ARA layered-sand shape/timing diagnostic")
    print("=" * 100)
    for model_key in MODEL_KEYS:
        print()
        print(model_key)
        model_result = {
            "best_lag_by_split": {},
            "best_lag_by_horizon": {},
            "affine_global_focus": None,
            "affine_with_phase_global_focus": None,
            "phase_correction_global_focus": None,
            "peak_trough_by_horizon": {},
        }
        for split_name, split in splits.items():
            model_result["best_lag_by_split"][split_name] = best_lag(split, model_key)
        for split_name in ["train_focus_pre2017", "holdout_focus_2017_on", "all_focus"]:
            model_result["best_lag_by_horizon"][split_name] = {
                horizon: best_lag(hrows, model_key)
                for horizon, hrows in rows_by_horizon(splits[split_name]).items()
            }
        train = splits["train_focus_pre2017"]
        holdout = splits["holdout_focus_2017_on"]
        model_result["affine_global_focus"] = affine_test(train, holdout, model_key, shift_steps=0)
        phase = phase_correction(train, holdout, model_key)
        model_result["phase_correction_global_focus"] = phase
        model_result["affine_with_phase_global_focus"] = affine_test(
            train,
            holdout,
            model_key,
            shift_steps=phase["train_best_shift_steps"],
        )
        model_result["peak_trough_by_horizon"] = {
            horizon: peak_trough_match(hrows, model_key)
            for horizon, hrows in rows_by_horizon(splits["all_focus"]).items()
        }
        results["models"][model_key] = clean_for_json(model_result)

        zero = model_result["best_lag_by_split"]["all_focus"]["zero_shift"]
        best = model_result["best_lag_by_split"]["all_focus"]["best_shift"]
        aff = model_result["affine_global_focus"]["holdout"]
        ph = model_result["phase_correction_global_focus"]["holdout"]
        aff_phase = model_result["affine_with_phase_global_focus"]["holdout"]
        print(
            f"  all-focus zero corr={zero['corr']:+.3f}; best shift={best['shift_steps']} steps"
            f" ({best['shift_months']}m) corr={best['corr']:+.3f} mae={best['mae']:.3f}"
        )
        print(
            f"  holdout affine-only corr={aff['corr']:+.3f} mae={aff['mae']:.3f};"
            f" phase-only shift={phase['train_best_shift_steps']} corr={ph['corr']:+.3f} mae={ph['mae']:.3f};"
            f" affine+phase corr={aff_phase['corr']:+.3f} mae={aff_phase['mae']:.3f}"
        )
    OUT_JSON.write_text(json.dumps(clean_for_json(results), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LAYERED_SAND_SHAPE_TIMING_DIAGNOSTIC = " + json.dumps(clean_for_json(results), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print()
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
