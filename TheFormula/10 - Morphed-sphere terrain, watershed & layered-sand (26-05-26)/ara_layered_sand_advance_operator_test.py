"""
ara_layered_sand_advance_operator_test.py

Test the missing "terrain arrival advance" operator for the layered-sand ARA
formula.

The prior timing diagnostic showed that the fixed Formula has a strong shape
when shifted left by roughly the forecast horizon. This script asks the stricter
question: can origin-time lower-layer spins advance the measured sphere's
terrain state without reading future raw values?

Strict predictor variants here use only:
  - origin-time row metadata
  - origin-time raw spin packets already stored in Formula diagnostics
  - current ARA coordinate as the present contact location

The "future_origin_shift_oracle" is included only as a leakage diagnostic. It
uses the later origin's Formula value, so it is not a forecast.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ara_fractal_sphere_terrain_reader import ara_to_value
from ara_geometry_transport_test import clean_for_json
from ara_layered_sand_parameter_search import predict_from_record
from ara_layered_sand_single_formula import (
    FORMULA,
    HOME,
    PHI,
    clamp,
    propagate_layer,
    read_sphere_terrain,
)
from ara_sphere_orientation_roll_predictor import EPS


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_layered_sand_single_formula_result.json"
FIT_JSON = HERE / "ara_layered_sand_parameter_search_result.json"
OUT_JSON = HERE / "ara_layered_sand_advance_operator_result.json"
OUT_JS = HERE / "ara_layered_sand_advance_operator_result.js"

TRAIN_CUTOFF = "2017-01-01"
FOCUS_HORIZONS = [6, 12, 24]

MODEL_KEYS = [
    "Formula",
    "Formula_Fitted",
    "Advance_Phase_Read",
    "Advance_Layer_Roll",
    "Advance_Layer_Roll_Fast",
    "Advance_Lower_Terrain_Base",
    "future_origin_shift_oracle",
]


def sign(value):
    if value > EPS:
        return 1
    if value < -EPS:
        return -1
    return 0


def corr(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if len(xs) < 3 or np.std(xs) <= EPS or np.std(ys) <= EPS:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def score(rows, key):
    usable = [row for row in rows if row.get(key) is not None]
    pred = np.asarray([row[key] for row in usable], dtype=float)
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


def rotate2(forward, lateral, angle):
    c = math.cos(angle)
    s = math.sin(angle)
    return forward * c - lateral * s, forward * s + lateral * c


def advance_spin(spin, horizon, layer_index, params, gain):
    """Causally rotate one stored raw spin packet by its own lower-scale speed."""
    out = dict(spin)
    period = max(float(out["period"]), EPS)
    turns = float(horizon) / period
    parity = -1.0 if layer_index % 2 else 1.0
    pressure = math.tanh(abs(float(out["pressure"])) / 2.0)
    speed_gate = math.tanh(float(params["lower_speed"]) / 3.0)
    angle = parity * gain * 2.0 * math.pi * turns * (0.28 + 0.72 * pressure) * speed_gate

    original_lateral = float(out["lateral"])
    out["forward"], out["lateral"] = rotate2(float(out["forward"]), original_lateral, angle)
    out["twist"] = float(out["twist"]) * math.cos(0.5 * angle)
    out["twist"] += parity * original_lateral * math.sin(0.5 * angle) * float(params["wobble"])

    drive = out["forward"] + 0.22 * out["lateral"] + 0.12 * out["twist"]
    out["ara"] = clamp(float(out["ara"]) + gain * float(params["roll_to_ara"]) * turns * 0.18 * drive, 0.0, 2.0)
    return out


def run_cascade_from_spins(row, horizon, params, spins, phase_extra=0.0):
    upper = row["formula"]["upper"]
    floor = spins[0]
    state = {
        "name": "floor",
        "period": float(floor["period"]),
        "forward": float(floor["forward"]) * float(params["floor_drive"]),
        "lateral": float(floor["lateral"]) * float(params["floor_drive"]),
        "twist": float(floor["twist"]) * float(params["floor_drive"]),
        "pressure": float(floor["pressure"]),
        "ara": float(floor["ara"]),
    }
    phase_deg = float(row["phase_clock_origin"]) + phase_extra
    for i, layer_spin in enumerate(spins[1:], start=1):
        second_spin = spins[max(0, i - 2)]
        state = propagate_layer(state, second_spin, layer_spin, upper, i, params, phase_deg)

    horizon_gain = math.sqrt(max(float(horizon), 1.0) / HOME)
    upper_brake = 1.0 + float(params["upper_pressure"]) * float(params["upper_brake"]) * abs(float(upper["compression"]))
    measured = float(params["measured_roll"]) * horizon_gain / upper_brake
    floor_phase = float(params["floor_drive"]) * (float(horizon) / HOME) * 360.0
    delta_ara = measured * float(params["roll_to_ara"]) * (float(state["forward"]) + 0.18 * float(state["lateral"]))
    delta_phase = floor_phase + phase_extra
    delta_phase += measured * float(params["roll_to_phase"]) * (
        float(state["lateral"]) + 0.45 * float(state["twist"]) + 0.18 * float(state["forward"])
    )
    return state, delta_ara, delta_phase, upper


def read_value(row, state, delta_ara, delta_phase, upper, base_ara):
    phase_deg = float(row["phase_clock_origin"]) + delta_phase
    arrival_ara = clamp(float(base_ara) + delta_ara, 0.0, 2.0)
    terrain = read_sphere_terrain(
        arrival_ara,
        float(base_ara),
        phase_deg,
        float(state["pressure"]),
        float(state["forward"]),
        float(upper["compression"]),
        row["_active_params"],
    )
    return {
        "value": float(ara_to_value(terrain["force_ara"])),
        "arrival_ara": float(arrival_ara),
        "arrival_phase": float(phase_deg % 360.0),
        "delta_ara": float(delta_ara),
        "delta_phase": float(delta_phase),
    }


def predict_advance(row, horizon, params, variant):
    row = {**row, "_active_params": params}
    spins = [dict(spin) for spin in row["formula"]["spins"]]
    phase_extra = 0.0
    base_ara = float(row["ara_current"])

    if variant == "Advance_Phase_Read":
        # Advance the terrain longitude only. This tests whether "late shape" is
        # just a phase-clock issue.
        phase_extra = 360.0 * float(horizon) / HOME
    elif variant == "Advance_Layer_Roll":
        # Each stored lower spin packet is rolled forward by its own faster
        # period before it drives the layer above.
        spins = [advance_spin(spin, horizon, i, params, gain=1.0) for i, spin in enumerate(spins)]
    elif variant == "Advance_Layer_Roll_Fast":
        spins = [advance_spin(spin, horizon, i, params, gain=2.0) for i, spin in enumerate(spins)]
    elif variant == "Advance_Lower_Terrain_Base":
        # Read the future patch from the lower-induced measured state instead of
        # from the visible current NINO coordinate. This is the strictest "do not
        # carry the current value" variant in this batch.
        pass

    state, delta_ara, delta_phase, upper = run_cascade_from_spins(row, horizon, params, spins, phase_extra)
    if variant == "Advance_Lower_Terrain_Base":
        base_ara = float(state.get("terrain_force_ara", state["ara"]))
    return read_value(row, state, delta_ara, delta_phase, upper, base_ara)


def load_rows():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    fit = json.loads(FIT_JSON.read_text(encoding="utf-8"))
    rows = []
    for horizon in data["horizons_months"]:
        for row in data["viz_records"][str(horizon)]:
            rows.append({**row, "horizon": int(horizon)})
    return rows, data, fit


def split_rows(rows):
    focus = [row for row in rows if int(row["horizon"]) in FOCUS_HORIZONS]
    return {
        "train_focus_pre2017": [row for row in focus if row["origin"] < TRAIN_CUTOFF],
        "holdout_focus_2017_on": [row for row in focus if row["origin"] >= TRAIN_CUTOFF],
        "all_focus": focus,
        "all_horizons": rows,
    }


def score_by_horizon(rows, key):
    out = {}
    for horizon in sorted({int(row["horizon"]) for row in rows}):
        hrows = [row for row in rows if int(row["horizon"]) == horizon]
        out[str(horizon)] = score(hrows, key)
    return out


def build_oracle_lookup(rows):
    by_horizon = {}
    for row in rows:
        by_horizon.setdefault(int(row["horizon"]), {})[row["origin"]] = row
    return by_horizon


def add_predictions(rows, params):
    by_horizon = build_oracle_lookup(rows)
    out = []
    for row in rows:
        horizon = int(row["horizon"])
        item = dict(row)
        item["Formula"] = float(row["Formula"])
        item["Formula_Fitted"] = float(predict_from_record(row, horizon, params)[0])
        for variant in ["Advance_Phase_Read", "Advance_Layer_Roll", "Advance_Layer_Roll_Fast", "Advance_Lower_Terrain_Base"]:
            pred = predict_advance(row, horizon, params, variant)
            item[variant] = pred["value"]
            item[f"{variant}_diagnostics"] = pred

        # Leakage diagnostic: this reads the later origin's formula value. It is
        # what the previous phase-shift result measured, not a causal forecast.
        future = by_horizon.get(horizon, {}).get(row["target"])
        item["future_origin_shift_oracle"] = float(future["Formula"]) if future else None
        out.append(item)
    return out


def records_for_viz(rows):
    out = {}
    for row in rows:
        h = str(row["horizon"])
        out.setdefault(h, []).append(
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": round(float(row["current"]), 6),
                "actual": round(float(row["actual"]), 6),
                "Formula": round(float(row["Formula"]), 6),
                "Formula_Fitted": round(float(row["Formula_Fitted"]), 6),
                "Advance_Phase_Read": round(float(row["Advance_Phase_Read"]), 6),
                "Advance_Layer_Roll": round(float(row["Advance_Layer_Roll"]), 6),
                "Advance_Layer_Roll_Fast": round(float(row["Advance_Layer_Roll_Fast"]), 6),
                "Advance_Lower_Terrain_Base": round(float(row["Advance_Lower_Terrain_Base"]), 6),
                "future_origin_shift_oracle": round(float(row["future_origin_shift_oracle"]), 6)
                if row["future_origin_shift_oracle"] is not None
                else None,
            }
        )
    return out


def run():
    rows, source, fit = load_rows()
    params = fit["best_params"]
    predicted = add_predictions(rows, params)
    splits = split_rows(predicted)
    evaluations = {}
    print("ARA layered-sand advance operator test")
    print("=" * 100)
    print("Strict variants use origin-time lower-layer spin only. Oracle shift is labelled as leakage diagnostic.")
    print()
    for split_name, split in splits.items():
        evaluations[split_name] = {
            key: score(split, key) for key in MODEL_KEYS if any(row.get(key) is not None for row in split)
        }
        evaluations[split_name]["by_horizon"] = {
            key: score_by_horizon([row for row in split if row.get(key) is not None], key)
            for key in MODEL_KEYS
            if any(row.get(key) is not None for row in split)
        }

    for split_name in ["train_focus_pre2017", "holdout_focus_2017_on", "all_focus"]:
        print(split_name)
        for key in MODEL_KEYS:
            if key not in evaluations[split_name]:
                continue
            s = evaluations[split_name][key]
            print(
                f"  {key:30s}"
                f" MAE={s['mae']:.3f}"
                f" corr={s['corr']:+.3f}"
                f" curcorr={s['corr_with_current']:+.3f}"
                f" dir={s['direction']:.3f}"
                f" amp={s['amp_ratio']:.3f}"
            )
        print()

    out = {
        "date": "2026-05-26",
        "method": "strict causal terrain-arrival advance operator test for layered-sand formula",
        "train_cutoff": TRAIN_CUTOFF,
        "focus_horizons": FOCUS_HORIZONS,
        "models": MODEL_KEYS,
        "variant_notes": {
            "Formula": "Fixed base formula from ara_layered_sand_single_formula.py.",
            "Formula_Fitted": "Same formula with constants fitted on train_focus_pre2017.",
            "Advance_Phase_Read": "Fitted formula plus horizon phase/longitude advance only.",
            "Advance_Layer_Roll": "Origin-time lower spin packets are rolled forward by their own periods before cascade.",
            "Advance_Layer_Roll_Fast": "Same as Advance_Layer_Roll with doubled causal spin advance.",
            "Advance_Lower_Terrain_Base": "Reads from the lower-induced measured terrain state instead of carrying the visible current ARA coordinate.",
            "future_origin_shift_oracle": "Diagnostic only. Uses the later origin's fixed Formula value, therefore leaks future raw state.",
        },
        "leakage_guard": [
            "Strict advance variants use only origin-time Formula diagnostic spin packets.",
            "No future raw NINO/SOI/PDO values are read by strict advance variants.",
            "No historical nearest-neighbour averaging, smoothing, lag ridge, or native-value decoder is used.",
            "future_origin_shift_oracle is excluded from predictor claims because it reads a future origin row.",
        ],
        "evaluations": clean_for_json(evaluations),
        "viz_records": clean_for_json(records_for_viz(predicted)),
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LAYERED_SAND_ADVANCE_OPERATOR = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
