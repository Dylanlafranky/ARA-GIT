"""
ara_layered_sand_full_formula.py

First full implementation of the layered-sand / rolling-sphere ARA formula.

This is intentionally not another nearest-neighbour predictor. It encodes the
whole mechanism as a deterministic contact cascade:

    moving floor
    -> fine sand sphere
    -> medium sand sphere
    -> coarse sand sphere
    -> measured sphere

Each layer:
  - has its own recursive ARA terrain read
  - receives two lower contacts, causing non-uniform wobble
  - rolls opposite the lower layer it touches
  - transfers faster lower spin upward through bounded contact gain
  - is compressed/resisted by upper coarse spheres

The final measured-sphere roll advances the current surface coordinate, then
the fractal terrain reader gives the predicted terrain response.

Strict guard: all inputs at origin t use raw samples <= t only. There is no
lag ridge, native-value decoder, historical nearest-neighbour terrain, future
geometry oracle, or visual shift.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ara_cross_rung_spin_transfer_test import HOME, HORIZONS, ORIGIN_STRIDE, PHI
from ara_fractal_sphere_terrain_reader import ara_to_value, read_fractal_terrain, value_to_ara
from ara_geometry_transport_test import clean_for_json, load_enso_frame
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, raw_delta, raw_value, rounded, squash
from ara_sphere_orientation_roll_predictor import (
    EPS,
    local_basis,
    row_surface_vec,
    rotate_vec,
    sign,
    vec_to_ara,
)


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
RAW_ADDRESS_JSON = HERE / "ara_raw_terrain_address_lookup_result.json"
LOWER_SELECTOR_JSON = HERE / "ara_lower_sphere_roll_selector_result.json"
OUT_JSON = HERE / "ara_layered_sand_full_formula_result.json"
OUT_JS = HERE / "ara_layered_sand_full_formula_result.js"

VALUE_SCALE = 1.5

FLOOR_PERIOD = HOME / (PHI**4)
LAYER_SPECS = [
    {"name": "floor", "period": FLOOR_PERIOD, "kind": "driver"},
    {"name": "fine", "period": HOME / (PHI**3), "kind": "lower"},
    {"name": "medium", "period": HOME / (PHI**2), "kind": "lower"},
    {"name": "coarse", "period": HOME / PHI, "kind": "lower"},
    {"name": "measured", "period": HOME, "kind": "home"},
]
UPPER_SPECS = [
    {"name": "upper_coarse", "period": HOME * PHI},
    {"name": "upper_coursest", "period": HOME * (PHI**2)},
]

MODEL_KEYS = [
    "persistence",
    "wobble_surface_analog",
    "raw_address_top1",
    "lower_core_top1",
    "layered_arrival",
    "layered_fractal",
    "layered_water",
]


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def month_anchor(frame, date_string):
    target = np.datetime64(date_string)
    dates = np.asarray(frame.index, dtype="datetime64[D]")
    idx = int(np.where(dates == target)[0][0])
    return idx + 1


def sigmoid(value):
    value = clamp(value, -40.0, 40.0)
    return 1.0 / (1.0 + math.exp(-value))


def read_json_predictions(path, fields):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for horizon, rows in data.get("viz_records", {}).items():
        out[horizon] = {}
        for row in rows:
            out[horizon][(row["origin"], row["target"])] = {field: row.get(field) for field in fields}
    return out


def raw_spin(frame, anchor, period, name):
    nino = squash(raw_delta(frame, "NINO", anchor, period), 0.75 + 0.25 * period / HOME)
    soi = squash(-raw_delta(frame, "SOI", anchor, period), 1.65 + 0.20 * period / HOME)
    pdo = squash(raw_delta(frame, "PDO", anchor, period), 2.10 + 0.25 * period / HOME)
    frequency = math.sqrt(HOME / max(float(period), EPS))
    forward = frequency * (0.43 * nino + 0.41 * soi + 0.16 * pdo)
    lateral = frequency * (0.48 * (nino - soi) + 0.22 * pdo)
    twist = frequency * (0.36 * nino * soi + 0.24 * (nino + soi) + 0.18 * pdo)
    pressure = frequency * (abs(nino) + abs(soi) + 0.55 * abs(pdo))
    gear_mesh = nino * soi
    local_value = raw_value(frame, "NINO", anchor) + 0.55 * raw_delta(frame, "NINO", anchor, period)
    local_value += 0.24 * (-raw_delta(frame, "SOI", anchor, period))
    local_value += 0.16 * raw_delta(frame, "PDO", anchor, period)
    return {
        "name": name,
        "period": float(period),
        "forward": float(forward),
        "lateral": float(lateral),
        "twist": float(twist),
        "pressure": float(pressure),
        "gear_mesh": float(gear_mesh),
        "ara": value_to_ara(local_value),
        "nino_spin": float(nino),
        "soi_spin": float(soi),
        "pdo_spin": float(pdo),
    }


def upper_pressure(frame, anchor):
    parts = []
    for spec in UPPER_SPECS:
        spin = raw_spin(frame, anchor, spec["period"], spec["name"])
        slow_weight = math.sqrt(HOME / spec["period"])
        parts.append(
            {
                "spin": spin,
                "compression": slow_weight * spin["pressure"],
                "direction": slow_weight * spin["forward"],
                "lateral": slow_weight * spin["lateral"],
                "twist": slow_weight * spin["twist"],
            }
        )
    compression = float(np.sum([p["compression"] for p in parts]))
    direction = float(np.sum([p["direction"] for p in parts]))
    lateral = float(np.sum([p["lateral"] for p in parts]))
    twist = float(np.sum([p["twist"] for p in parts]))
    return {
        "compression": squash(compression, 2.5),
        "direction": squash(direction, 1.4),
        "lateral": squash(lateral, 1.1),
        "twist": squash(twist, 1.1),
        "parts": parts,
    }


def terrain_terms(contact_pressure, lower_drive, upper_gate):
    return {
        "contact_pressure": float(contact_pressure),
        "lower_drive": float(lower_drive),
        "upper_gate": float(upper_gate),
    }


def propagate_layer(lower_state, contact_spin, layer_spin, upper, layer_index):
    period_ratio = layer_spin["period"] / max(lower_state["period"], EPS)
    speed_gain = math.sqrt(period_ratio)
    contact_a = np.asarray([lower_state["forward"], lower_state["lateral"], lower_state["twist"]], dtype=float)
    contact_b = np.asarray([contact_spin["forward"], contact_spin["lateral"], contact_spin["twist"]], dtype=float)

    pressure_a = abs(lower_state["pressure"])
    pressure_b = abs(contact_spin["pressure"])
    total_pressure = pressure_a + pressure_b + EPS
    weight_a = pressure_a / total_pressure
    weight_b = pressure_b / total_pressure
    lower_contact = weight_a * contact_a + weight_b * contact_b

    # Spheres roll against the layer below them, so every upward contact flips orientation.
    parity = -1.0
    wobble = contact_a - contact_b
    own = np.asarray([layer_spin["forward"], layer_spin["lateral"], layer_spin["twist"]], dtype=float)

    compression = 1.0 + 0.45 * abs(upper["compression"])
    contact_gain = squash(speed_gain * total_pressure, 3.4)
    slip = sigmoid(1.2 * abs(wobble[1]) + 0.9 * abs(wobble[2]) - 0.85 * compression)
    transfer = (0.72 + 0.28 * slip) * contact_gain / compression

    arrival_ara = clamp(layer_spin["ara"] + 0.18 * parity * lower_contact[0], 0.0, 2.0)
    terrain = read_fractal_terrain(
        arrival_ara,
        layer_spin["ara"],
        terrain_terms(total_pressure, lower_contact[0], upper["compression"]),
    )
    terrain_drive = terrain["weighted_slope"] * (0.30 + 0.42 * terrain["force"] + 0.20 * terrain["spillover"])

    out_vec = parity * transfer * lower_contact
    out_vec += 0.18 * own
    out_vec += np.asarray(
        [
            terrain_drive + 0.06 * upper["direction"],
            0.32 * slip * wobble[1] + 0.05 * upper["lateral"],
            0.28 * slip * wobble[2] + 0.05 * upper["twist"],
        ],
        dtype=float,
    )

    return {
        "name": layer_spin["name"],
        "period": layer_spin["period"],
        "forward": float(out_vec[0]),
        "lateral": float(out_vec[1]),
        "twist": float(out_vec[2]),
        "pressure": float(total_pressure * (0.55 + 0.45 * compression)),
        "ara": float(arrival_ara),
        "terrain_target_ara": float(terrain["weighted_target_spill"]),
        "terrain_slope": float(terrain["weighted_slope"]),
        "terrain_spillover": float(terrain["spillover"]),
        "contact_gain": float(contact_gain),
        "transfer": float(transfer),
        "slip": float(slip),
        "weight_a": float(weight_a),
        "weight_b": float(weight_b),
        "layer_index": int(layer_index),
    }


def vector_to_omega(surface_vec, roll_state, horizon):
    radial, east, north = local_basis(surface_vec)
    horizon_gain = math.sqrt(max(float(horizon), 1.0) / HOME)
    forward = clamp(roll_state["forward"] * horizon_gain, -1.8, 1.8)
    lateral = clamp(roll_state["lateral"] * horizon_gain, -1.4, 1.4)
    twist = clamp(roll_state["twist"] * horizon_gain, -1.2, 1.2)
    return (
        north * math.radians(42.0 * forward)
        + east * math.radians(34.0 * lateral)
        + radial * math.radians(24.0 * twist)
    )


def layered_sand_formula(frame, row, horizon):
    anchor = month_anchor(frame, row["origin"])
    upper = upper_pressure(frame, anchor)
    spins = [raw_spin(frame, anchor, spec["period"], spec["name"]) for spec in LAYER_SPECS]
    floor = spins[0]
    state = {
        "name": "floor",
        "period": floor["period"],
        "forward": floor["forward"],
        "lateral": floor["lateral"],
        "twist": floor["twist"],
        "pressure": floor["pressure"],
        "ara": floor["ara"],
    }
    layers = [state]
    for i, layer_spin in enumerate(spins[1:], start=1):
        contact_spin = spins[max(0, i - 2)]
        state = propagate_layer(state, contact_spin, layer_spin, upper, i)
        layers.append(state)

    surface_vec = row_surface_vec(row)
    omega = vector_to_omega(surface_vec, state, horizon)
    arrival_vec = rotate_vec(surface_vec, omega)
    arrival_ara = vec_to_ara(arrival_vec)
    terrain = read_fractal_terrain(
        arrival_ara,
        row["ara_current"],
        terrain_terms(state["pressure"], state["forward"], upper["compression"]),
    )
    force_ara = clamp(arrival_ara + terrain["weighted_slope"] * terrain["force_gain"], 0.0, 2.0)
    arrival_value = ara_to_value(arrival_ara)
    fractal_value = ara_to_value(force_ara)

    carried = row["current"]
    water_gain = clamp(
        0.18 + 0.35 * abs(state["forward"]) + 0.18 * terrain["spillover"] + 0.12 * upper["compression"],
        0.12,
        0.88,
    )
    water_value = carried + water_gain * (fractal_value - carried)
    return {
        "arrival": float(arrival_value),
        "fractal": float(fractal_value),
        "water": float(water_value),
        "arrival_ara": float(arrival_ara),
        "force_ara": float(force_ara),
        "water_gain": float(water_gain),
        "upper_compression": float(upper["compression"]),
        "final_forward": float(state["forward"]),
        "final_lateral": float(state["lateral"]),
        "final_twist": float(state["twist"]),
        "final_pressure": float(state["pressure"]),
        "terrain_spillover": float(terrain["spillover"]),
        "terrain_force": float(terrain["force"]),
        "layers": layers,
    }


def point_records(records, pred_key):
    return [point(row["origin"], row["target"], row[pred_key], row["actual"], row["current"]) for row in records]


def direction_score(records, pred_key):
    rows = []
    for row in records:
        truth = sign(row["actual"] - row["current"])
        pred = sign(row[pred_key] - row["current"])
        if truth == 0:
            continue
        rows.append((truth, pred, row))
    if not rows:
        return {"n": 0, "accuracy": None, "large_accuracy": None, "transition_accuracy": None}
    large = [item for item in rows if abs(item[2]["actual"] - item[2]["current"]) >= 0.5]
    transition = [item for item in rows if abs(item[2]["actual"]) >= 0.5 or abs(item[2]["current"]) >= 0.5]
    return {
        "n": int(len(rows)),
        "accuracy": float(np.mean([truth == pred for truth, pred, _ in rows])),
        "large_accuracy": float(np.mean([truth == pred for truth, pred, _ in large])) if large else None,
        "transition_accuracy": float(np.mean([truth == pred for truth, pred, _ in transition])) if transition else None,
    }


def amplitude_stats(records, pred_key):
    if not records:
        return {"n": 0, "pred_delta_std": None, "truth_delta_std": None, "std_ratio": None, "abs_delta_ratio": None}
    pred_delta = np.asarray([row[pred_key] - row["current"] for row in records], dtype=float)
    truth_delta = np.asarray([row["actual"] - row["current"] for row in records], dtype=float)
    pred_std = float(np.std(pred_delta))
    truth_std = float(np.std(truth_delta))
    mean_abs_truth = float(np.mean(np.abs(truth_delta)))
    return {
        "n": int(len(records)),
        "pred_delta_std": pred_std,
        "truth_delta_std": truth_std,
        "std_ratio": pred_std / truth_std if truth_std > EPS else None,
        "abs_delta_ratio": float(np.mean(np.abs(pred_delta)) / mean_abs_truth) if mean_abs_truth > EPS else None,
    }


def focus_direction(scores, horizons):
    return {
        "n": int(sum(scores[str(h)]["n"] for h in horizons)),
        "accuracy": float(np.mean([scores[str(h)]["accuracy"] for h in horizons])),
        "large_accuracy": float(
            np.mean([scores[str(h)]["large_accuracy"] for h in horizons if scores[str(h)]["large_accuracy"] is not None])
        ),
        "transition_accuracy": float(
            np.mean(
                [
                    scores[str(h)]["transition_accuracy"]
                    for h in horizons
                    if scores[str(h)]["transition_accuracy"] is not None
                ]
            )
        ),
    }


def run():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    frame = load_enso_frame()
    raw_preds = read_json_predictions(RAW_ADDRESS_JSON, ["raw_address_top1"])
    lower_preds = read_json_predictions(LOWER_SELECTOR_JSON, ["lower_core_top1"])
    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    direction_scores = {key: {} for key in MODEL_KEYS}
    amplitude = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA layered-sand full formula")
    print("=" * 100)
    print("strict guards: deterministic contact cascade; raw inputs <= origin; no historical terrain lookup")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in data["records_by_horizon"][h]]
        for row in records:
            key = (row["origin"], row["target"])
            formula = layered_sand_formula(frame, row, horizon)
            row["persistence_pred"] = row["current"]
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            row["raw_address_top1_pred"] = raw_preds.get(h, {}).get(key, {}).get("raw_address_top1", row["current"])
            row["lower_core_top1_pred"] = lower_preds.get(h, {}).get(key, {}).get("lower_core_top1", row["current"])
            row["layered_arrival_pred"] = formula["arrival"]
            row["layered_fractal_pred"] = formula["fractal"]
            row["layered_water_pred"] = formula["water"]
            row["layered_formula"] = formula

        score_keys = {
            "persistence": "persistence_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "raw_address_top1": "raw_address_top1_pred",
            "lower_core_top1": "lower_core_top1_pred",
            "layered_arrival": "layered_arrival_pred",
            "layered_fractal": "layered_fractal_pred",
            "layered_water": "layered_water_pred",
        }
        for key, pred_key in score_keys.items():
            point_scores[key][h] = extended_score(point_records(records, pred_key))
            direction_scores[key][h] = direction_score(records, pred_key)
            amplitude[key][h] = amplitude_stats(records, pred_key)

        diagnostics[h] = {
            "mean_upper_compression": float(np.mean([r["layered_formula"]["upper_compression"] for r in records])),
            "mean_final_pressure": float(np.mean([r["layered_formula"]["final_pressure"] for r in records])),
            "mean_final_forward": float(np.mean([r["layered_formula"]["final_forward"] for r in records])),
            "mean_final_lateral": float(np.mean([r["layered_formula"]["final_lateral"] for r in records])),
            "mean_final_twist": float(np.mean([r["layered_formula"]["final_twist"] for r in records])),
            "mean_terrain_spillover": float(np.mean([r["layered_formula"]["terrain_spillover"] for r in records])),
        }

        records_by_h[h] = [
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": rounded(row["current"]),
                "actual": rounded(row["actual"]),
                "wobble_surface_analog": rounded(row["wobble_surface_analog_pred"]),
                "raw_address_top1": rounded(row["raw_address_top1_pred"]),
                "lower_core_top1": rounded(row["lower_core_top1_pred"]),
                "layered_arrival": rounded(row["layered_arrival_pred"]),
                "layered_fractal": rounded(row["layered_fractal_pred"]),
                "layered_water": rounded(row["layered_water_pred"]),
                "arrival_ara": rounded(row["layered_formula"]["arrival_ara"]),
                "force_ara": rounded(row["layered_formula"]["force_ara"]),
                "water_gain": rounded(row["layered_formula"]["water_gain"]),
                "upper_compression": rounded(row["layered_formula"]["upper_compression"]),
                "final_forward": rounded(row["layered_formula"]["final_forward"]),
                "final_lateral": rounded(row["layered_formula"]["final_lateral"]),
                "final_twist": rounded(row["layered_formula"]["final_twist"]),
                "terrain_spillover": rounded(row["layered_formula"]["terrain_spillover"]),
                "layers": [
                    {
                        "name": layer["name"],
                        "period": rounded(layer["period"]),
                        "forward": rounded(layer["forward"]),
                        "lateral": rounded(layer["lateral"]),
                        "twist": rounded(layer["twist"]),
                        "pressure": rounded(layer["pressure"]),
                        "ara": rounded(layer["ara"]),
                        "terrain_spillover": rounded(layer.get("terrain_spillover")),
                        "transfer": rounded(layer.get("transfer")),
                        "slip": rounded(layer.get("slip")),
                    }
                    for layer in row["layered_formula"]["layers"]
                ],
            }
            for row in records
        ]

        print(f"h={horizon:>2} months")
        for key in MODEL_KEYS:
            ps = point_scores[key][h]
            ds = direction_scores[key][h]
            amp = amplitude[key][h]
            print(
                f"  {key:24s} {format_score(ps)}"
                f" dir={ds['accuracy'] if ds['accuracy'] is not None else float('nan'):.3f}"
                f" amp_ratio={amp['std_ratio'] if amp['std_ratio'] is not None else float('nan'):.3f}"
            )
        print(
            f"  layered diagnostics      pressure={diagnostics[h]['mean_final_pressure']:.3f}"
            f" spill={diagnostics[h]['mean_terrain_spillover']:.3f}"
        )
        print()

    focus_horizons = [6, 12, 24]
    focus = {
        "point_scores": {key: aggregate_focus(point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "direction_scores": {key: focus_direction(direction_scores[key], focus_horizons) for key in MODEL_KEYS},
        "amplitude": {key: aggregate_focus(amplitude[key], focus_horizons) for key in MODEL_KEYS},
    }
    out = {
        "date": "2026-05-26",
        "method": "deterministic layered sand full ARA formula",
        "leakage_guard": [
            "Every floor/layer/upper spin input uses raw samples at or before current origin t.",
            "No historical nearest-neighbour terrain table is used by the layered formula.",
            "Each layer has deterministic recursive ARA terrain read.",
            "Layer-to-layer roll alternates direction by contact parity.",
            "Each layer receives two lower contacts, creating non-uniform wobble.",
            "Upper layers apply compression/down-pressure to the transfer.",
            "No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.",
        ],
        "layers": clean_for_json({"floor_period": FLOOR_PERIOD, "layer_specs": LAYER_SPECS, "upper_specs": UPPER_SPECS}),
        "horizons_months": HORIZONS,
        "point_scores": clean_for_json(point_scores),
        "direction_scores": clean_for_json(direction_scores),
        "amplitude": clean_for_json(amplitude),
        "diagnostics": clean_for_json(diagnostics),
        "focus_6_12_24": clean_for_json(focus),
        "viz_records": clean_for_json(records_by_h),
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LAYERED_SAND_FULL_FORMULA = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )

    print("Focus 6/12/24:")
    for key in MODEL_KEYS:
        ps = focus["point_scores"][key]
        ds = focus["direction_scores"][key]
        amp = focus["amplitude"][key]
        print(
            f"  {key:24s}"
            f" MAE={ps.get('mae'):.3f}"
            f" corr={ps.get('corr'):+.3f}"
            f" dir={ds.get('accuracy'):.3f}"
            f" amp_ratio={amp.get('std_ratio'):.3f}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
