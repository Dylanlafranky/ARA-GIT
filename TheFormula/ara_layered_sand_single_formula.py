"""
ara_layered_sand_single_formula.py

Single-formula implementation of the layered-sand / rolling-sphere ARA model.

Scenario encoded:
  floor moves in one direction
  fine grains roll because the floor moves
  each coarser layer rolls opposite the layer beneath it
  every layer has recursive ARA terrain
  each layer touches two lower grains, producing wobble
  lower spin speed determines transfer into the layer above
  upper coarse layers apply downward pressure
  the measured coarse sphere rolls under the fixed reading point

This file exports one physical formula (`Formula`) and one parameter-identical
copy (`Formula_Adjustable`) for the HTML visualiser. Baselines and legacy
overlays are labelled as overlays only. They are not inputs to the formula.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ara_cross_rung_spin_transfer_test import HOME, HORIZONS, PHI
from ara_fractal_sphere_terrain_reader import ara_to_value, read_fractal_terrain, value_to_ara
from ara_geometry_transport_test import clean_for_json, load_enso_frame
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, raw_delta, raw_value, rounded, squash
from ara_sphere_orientation_roll_predictor import EPS, sign


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
RAW_ADDRESS_JSON = HERE / "ara_raw_terrain_address_lookup_result.json"
OUT_JSON = HERE / "ara_layered_sand_single_formula_result.json"
OUT_JS = HERE / "ara_layered_sand_single_formula_result.js"

FLOOR_PERIOD = HOME / (PHI**4)
LAYER_SPECS = [
    {"name": "floor", "period": FLOOR_PERIOD, "role": "moving floor"},
    {"name": "fine", "period": HOME / (PHI**3), "role": "fine sand"},
    {"name": "medium", "period": HOME / (PHI**2), "role": "larger sand"},
    {"name": "coarse", "period": HOME / PHI, "role": "coarse sand"},
    {"name": "measured", "period": HOME, "role": "measured sphere"},
]
UPPER_SPECS = [
    {"name": "upper_coarse", "period": HOME * PHI},
    {"name": "upper_coursest", "period": HOME * (PHI**2)},
]

MOVING_PARTS = [
    {
        "part": "floor_motion",
        "variable": "D0",
        "meaning": "deep moving floor / lowest driver direction",
        "formula_role": "raw spin at HOME/phi^4 starts the cascade",
    },
    {
        "part": "layer_spin",
        "variable": "Si",
        "meaning": "own spin of each layer i",
        "formula_role": "raw NINO, anti-phase SOI, and PDO finite differences at each rung period",
    },
    {
        "part": "opposite_roll",
        "variable": "Qi = (-1)^i",
        "meaning": "each layer rolls opposite the layer beneath",
        "formula_role": "alternating parity applied to lower contact transfer",
    },
    {
        "part": "two_lower_contacts",
        "variable": "CiA, CiB",
        "meaning": "grain sits between two lower grains",
        "formula_role": "pressure-weighted lower contact and adjacent raw lower contact",
    },
    {
        "part": "wobble",
        "variable": "Wi = CiA - CiB",
        "meaning": "non-uniform roll caused by unequal contacts",
        "formula_role": "lateral/twist perturbation of layer roll vector",
    },
    {
        "part": "speed_transfer",
        "variable": "Ri = sqrt(Pi / Pi-1)",
        "meaning": "faster lower layer transfers more frequent motion upward",
        "formula_role": "multiplies lower contact impulse",
    },
    {
        "part": "recursive_terrain",
        "variable": "Ti(ARA, phase)",
        "meaning": "each sphere has filled recursive ARA terrain",
        "formula_role": "local phi-valley/ridge read at each layer and final measured coordinate",
    },
    {
        "part": "upper_pressure",
        "variable": "U",
        "meaning": "coarser upper layer applies downward pressure",
        "formula_role": "increases contact grip and also adds braking/compression",
    },
    {
        "part": "measured_roll",
        "variable": "M",
        "meaning": "terrain on the measured coarse sphere rolls under the reading point",
        "formula_role": "final ARA and phase displacement over forecast horizon",
    },
]

FORMULA = {
    "floor_drive": 1.0,
    "lower_speed": 1.0,
    "contact_transfer": 0.34,
    "second_contact": 0.46,
    "wobble": 0.52,
    "own_spin": 0.12,
    "terrain_pull": 0.78,
    "terrain_spill": 0.24,
    "roll_to_ara": 0.34,
    "roll_to_phase": 92.0,
    "phase_terrain": 0.42,
    "ara_terrain": 0.78,
    "upper_pressure": 1.0,
    "upper_grip": 0.22,
    "upper_brake": 0.20,
    "measured_roll": 1.0,
}

FORMULA_ADJUSTABLE = dict(FORMULA)

MODEL_KEYS = [
    "baseline_persistence",
    "legacy_wobble_surface",
    "legacy_raw_address_top1",
    "Formula",
]


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def sigmoid(value):
    value = clamp(value, -40.0, 40.0)
    return 1.0 / (1.0 + math.exp(-value))


def month_anchor(frame, date_string):
    target = np.datetime64(date_string)
    dates = np.asarray(frame.index, dtype="datetime64[D]")
    return int(np.where(dates == target)[0][0]) + 1


def raw_spin(frame, anchor, period, name):
    nino = squash(raw_delta(frame, "NINO", anchor, period), 0.75 + 0.25 * period / HOME)
    soi = squash(-raw_delta(frame, "SOI", anchor, period), 1.65 + 0.20 * period / HOME)
    pdo = squash(raw_delta(frame, "PDO", anchor, period), 2.10 + 0.25 * period / HOME)
    frequency = math.sqrt(HOME / max(float(period), EPS))
    forward = frequency * (0.43 * nino + 0.41 * soi + 0.16 * pdo)
    lateral = frequency * (0.48 * (nino - soi) + 0.22 * pdo)
    twist = frequency * (0.36 * nino * soi + 0.24 * (nino + soi) + 0.18 * pdo)
    pressure = frequency * (abs(nino) + abs(soi) + 0.55 * abs(pdo))
    local_value = raw_value(frame, "NINO", anchor) + 0.55 * raw_delta(frame, "NINO", anchor, period)
    local_value += 0.24 * (-raw_delta(frame, "SOI", anchor, period))
    local_value += 0.16 * raw_delta(frame, "PDO", anchor, period)
    return {
        "name": name,
        "period": float(period),
        "frequency": float(frequency),
        "forward": float(forward),
        "lateral": float(lateral),
        "twist": float(twist),
        "pressure": float(pressure),
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
                "name": spec["name"],
                "period": spec["period"],
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


def local_phi_slope(x, depth=5):
    x = clamp(x, 0.0, 2.0)
    lo = 0.0
    hi = 2.0
    for _ in range(depth):
        mid = 0.5 * (lo + hi)
        if x < mid:
            hi = mid
        else:
            lo = mid
    width = max(hi - lo, EPS)
    p1 = hi - width / PHI
    p2 = lo + width / PHI
    target = p1 if abs(x - p1) <= abs(x - p2) else p2
    return {
        "lo": lo,
        "hi": hi,
        "target": target,
        "slope": target - x,
        "ridge_distance": min(abs(x - lo), abs(hi - x)) / width,
        "width": width,
    }


def terrain_terms(contact_pressure, lower_drive, upper_gate):
    return {
        "contact_pressure": float(contact_pressure),
        "lower_drive": float(lower_drive),
        "upper_gate": float(upper_gate),
    }


def read_sphere_terrain(arrival_ara, current_ara, phase_deg, contact_pressure, lower_drive, upper_gate, params):
    ara_terrain = read_fractal_terrain(
        arrival_ara,
        current_ara,
        terrain_terms(contact_pressure, lower_drive, upper_gate),
    )
    phase_ara = 2.0 * ((float(phase_deg) % 360.0) / 360.0)
    phase_terrain = local_phi_slope(phase_ara, depth=5)
    combined_slope = params["ara_terrain"] * ara_terrain["weighted_slope"]
    combined_slope += params["phase_terrain"] * phase_terrain["slope"]
    force_gain = params["terrain_pull"] * ara_terrain["force_gain"]
    force_gain += params["terrain_spill"] * ara_terrain["spillover"]
    force_ara = clamp(arrival_ara + combined_slope * force_gain, 0.0, 2.0)
    return {
        "arrival_ara": float(arrival_ara),
        "phase_ara": float(phase_ara),
        "force_ara": float(force_ara),
        "combined_slope": float(combined_slope),
        "ara_spillover": float(ara_terrain["spillover"]),
        "ara_force": float(ara_terrain["force"]),
        "phase_target": float(phase_terrain["target"]),
        "phase_slope": float(phase_terrain["slope"]),
    }


def vector_from_state(state):
    return np.asarray([state["forward"], state["lateral"], state["twist"]], dtype=float)


def propagate_layer(lower_state, second_contact_spin, layer_spin, upper, layer_index, params, phase_deg):
    lower_vec = vector_from_state(lower_state)
    second_vec = np.asarray(
        [second_contact_spin["forward"], second_contact_spin["lateral"], second_contact_spin["twist"]],
        dtype=float,
    )
    own_vec = np.asarray([layer_spin["forward"], layer_spin["lateral"], layer_spin["twist"]], dtype=float)

    lower_pressure = abs(lower_state["pressure"])
    second_pressure = abs(second_contact_spin["pressure"])
    total_pressure = lower_pressure + second_pressure + EPS
    pressure_mix = second_pressure / total_pressure
    second_mix = clamp(params["second_contact"] * pressure_mix, 0.0, 0.95)
    contact = (1.0 - second_mix) * lower_vec + second_mix * second_vec
    wobble = lower_vec - second_vec

    parity = -1.0
    speed_ratio = math.sqrt(max(layer_spin["period"] / max(lower_state["period"], EPS), EPS))
    normal = 1.0 + params["upper_pressure"] * params["upper_grip"] * abs(upper["compression"])
    brake = 1.0 + params["upper_pressure"] * params["upper_brake"] * abs(upper["compression"])
    contact_drive = math.tanh(params["lower_speed"] * speed_ratio * total_pressure / 3.0)
    transfer = params["contact_transfer"] * contact_drive * normal / brake
    slip = sigmoid(params["wobble"] * (abs(wobble[1]) + 0.7 * abs(wobble[2])) - 0.65 * brake)

    out_vec = parity * transfer * contact
    out_vec += params["own_spin"] * own_vec
    out_vec += np.asarray([0.0, params["wobble"] * slip * wobble[1], params["wobble"] * slip * wobble[2]])
    out_vec += np.asarray([0.05 * upper["direction"], 0.04 * upper["lateral"], 0.04 * upper["twist"]])

    arrival_ara = clamp(layer_spin["ara"] + params["roll_to_ara"] * out_vec[0], 0.0, 2.0)
    terrain = read_sphere_terrain(
        arrival_ara,
        layer_spin["ara"],
        phase_deg + 31.0 * layer_index,
        total_pressure,
        out_vec[0],
        upper["compression"],
        params,
    )
    out_vec[0] += terrain["combined_slope"] * params["terrain_pull"]
    pressure = total_pressure * (0.65 + 0.35 * normal)
    return {
        "name": layer_spin["name"],
        "period": float(layer_spin["period"]),
        "forward": float(out_vec[0]),
        "lateral": float(out_vec[1]),
        "twist": float(out_vec[2]),
        "pressure": float(pressure),
        "ara": float(arrival_ara),
        "terrain_force_ara": float(terrain["force_ara"]),
        "terrain_slope": float(terrain["combined_slope"]),
        "terrain_spillover": float(terrain["ara_spillover"]),
        "speed_ratio": float(speed_ratio),
        "transfer": float(transfer),
        "slip": float(slip),
        "second_mix": float(second_mix),
        "parity": parity,
    }


def formula_predict(frame, row, horizon, params):
    anchor = month_anchor(frame, row["origin"])
    upper = upper_pressure(frame, anchor)
    spins = [raw_spin(frame, anchor, spec["period"], spec["name"]) for spec in LAYER_SPECS]

    floor_spin = spins[0]
    floor_vec_scale = params["floor_drive"]
    state = {
        "name": "floor",
        "period": floor_spin["period"],
        "forward": floor_spin["forward"] * floor_vec_scale,
        "lateral": floor_spin["lateral"] * floor_vec_scale,
        "twist": floor_spin["twist"] * floor_vec_scale,
        "pressure": floor_spin["pressure"],
        "ara": floor_spin["ara"],
    }
    phase_deg = float(row["phase_clock_origin"])
    layers = [state]
    for i, layer_spin in enumerate(spins[1:], start=1):
        second_contact_spin = spins[max(0, i - 2)]
        state = propagate_layer(state, second_contact_spin, layer_spin, upper, i, params, phase_deg)
        layers.append(state)

    horizon_gain = math.sqrt(max(float(horizon), 1.0) / HOME)
    upper_brake = 1.0 + params["upper_pressure"] * params["upper_brake"] * abs(upper["compression"])
    measured = params["measured_roll"] * horizon_gain / upper_brake
    floor_phase = params["floor_drive"] * (float(horizon) / HOME) * 360.0
    delta_ara = measured * params["roll_to_ara"] * (state["forward"] + 0.18 * state["lateral"])
    delta_phase = floor_phase + measured * params["roll_to_phase"] * (
        state["lateral"] + 0.45 * state["twist"] + 0.18 * state["forward"]
    )
    arrival_ara = clamp(float(row["ara_current"]) + delta_ara, 0.0, 2.0)
    arrival_phase = (phase_deg + delta_phase) % 360.0
    terrain = read_sphere_terrain(
        arrival_ara,
        row["ara_current"],
        arrival_phase,
        state["pressure"],
        state["forward"],
        upper["compression"],
        params,
    )
    value = ara_to_value(terrain["force_ara"])
    return {
        "value": float(value),
        "arrival_ara": float(arrival_ara),
        "arrival_phase": float(arrival_phase),
        "force_ara": float(terrain["force_ara"]),
        "delta_ara": float(delta_ara),
        "delta_phase": float(delta_phase),
        "upper_compression": float(upper["compression"]),
        "final_forward": float(state["forward"]),
        "final_lateral": float(state["lateral"]),
        "final_twist": float(state["twist"]),
        "final_pressure": float(state["pressure"]),
        "terrain_slope": float(terrain["combined_slope"]),
        "terrain_spillover": float(terrain["ara_spillover"]),
        "layers": layers,
        "spins": spins,
        "upper": upper,
    }


def read_legacy_raw_top1():
    if not RAW_ADDRESS_JSON.exists():
        return {}
    data = json.loads(RAW_ADDRESS_JSON.read_text(encoding="utf-8"))
    out = {}
    for horizon, rows in data.get("viz_records", {}).items():
        out[horizon] = {}
        for row in rows:
            out[horizon][(row["origin"], row["target"])] = row.get("raw_address_top1")
    return out


def point_records(records, pred_key):
    return [point(row["origin"], row["target"], row[pred_key], row["actual"], row["current"]) for row in records]


def direction_score(records, pred_key):
    rows = []
    for row in records:
        truth = sign(row["actual"] - row["current"])
        pred = sign(row[pred_key] - row["current"])
        if truth:
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
    pred_delta = np.asarray([row[pred_key] - row["current"] for row in records], dtype=float)
    truth_delta = np.asarray([row["actual"] - row["current"] for row in records], dtype=float)
    truth_std = float(np.std(truth_delta))
    return {
        "n": int(len(records)),
        "pred_delta_std": float(np.std(pred_delta)),
        "truth_delta_std": truth_std,
        "std_ratio": float(np.std(pred_delta) / truth_std) if truth_std > EPS else None,
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
    legacy_raw = read_legacy_raw_top1()
    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    direction_scores = {key: {} for key in MODEL_KEYS}
    amplitude = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA layered-sand single formula")
    print("=" * 100)
    print("Formula is one deterministic cascade. Persistence/raw/wobble are labelled overlays only.")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in data["records_by_horizon"][h]]
        for row in records:
            key = (row["origin"], row["target"])
            formula = formula_predict(frame, row, horizon, FORMULA)
            row["baseline_persistence_pred"] = row["current"]
            row["legacy_wobble_surface_pred"] = row["wobble_surface_analog"]
            row["legacy_raw_address_top1_pred"] = legacy_raw.get(h, {}).get(key, row["current"])
            row["Formula_pred"] = formula["value"]
            row["Formula"] = formula

        score_keys = {
            "baseline_persistence": "baseline_persistence_pred",
            "legacy_wobble_surface": "legacy_wobble_surface_pred",
            "legacy_raw_address_top1": "legacy_raw_address_top1_pred",
            "Formula": "Formula_pred",
        }
        for key, pred_key in score_keys.items():
            point_scores[key][h] = extended_score(point_records(records, pred_key))
            direction_scores[key][h] = direction_score(records, pred_key)
            amplitude[key][h] = amplitude_stats(records, pred_key)

        diagnostics[h] = {
            "mean_delta_ara": float(np.mean([r["Formula"]["delta_ara"] for r in records])),
            "mean_abs_delta_ara": float(np.mean([abs(r["Formula"]["delta_ara"]) for r in records])),
            "mean_delta_phase": float(np.mean([r["Formula"]["delta_phase"] for r in records])),
            "mean_upper_compression": float(np.mean([r["Formula"]["upper_compression"] for r in records])),
            "mean_final_pressure": float(np.mean([r["Formula"]["final_pressure"] for r in records])),
            "mean_terrain_spillover": float(np.mean([r["Formula"]["terrain_spillover"] for r in records])),
        }

        records_by_h[h] = []
        for row in records:
            formula = row["Formula"]
            records_by_h[h].append(
                {
                    "origin": row["origin"],
                    "target": row["target"],
                    "current": rounded(row["current"]),
                    "actual": rounded(row["actual"]),
                    "ara_current": rounded(row["ara_current"]),
                    "phase_clock_origin": rounded(row["phase_clock_origin"]),
                    "baseline_persistence": rounded(row["baseline_persistence_pred"]),
                    "legacy_wobble_surface": rounded(row["legacy_wobble_surface_pred"]),
                    "legacy_raw_address_top1": rounded(row["legacy_raw_address_top1_pred"]),
                    "Formula": rounded(row["Formula_pred"]),
                    "formula": clean_for_json(
                        {
                            "arrival_ara": formula["arrival_ara"],
                            "arrival_phase": formula["arrival_phase"],
                            "force_ara": formula["force_ara"],
                            "delta_ara": formula["delta_ara"],
                            "delta_phase": formula["delta_phase"],
                            "upper_compression": formula["upper_compression"],
                            "final_forward": formula["final_forward"],
                            "final_lateral": formula["final_lateral"],
                            "final_twist": formula["final_twist"],
                            "final_pressure": formula["final_pressure"],
                            "terrain_slope": formula["terrain_slope"],
                            "terrain_spillover": formula["terrain_spillover"],
                            "layers": formula["layers"],
                            "spins": formula["spins"],
                            "upper": formula["upper"],
                        }
                    ),
                }
            )

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
            f"  Formula diagnostics      |dARA|={diagnostics[h]['mean_abs_delta_ara']:.3f}"
            f" dphase={diagnostics[h]['mean_delta_phase']:.2f}"
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
        "method": "single layered-sand rolling-sphere ARA formula",
        "moving_parts": MOVING_PARTS,
        "formula_parameters": FORMULA,
        "formula_adjustable_defaults": FORMULA_ADJUSTABLE,
        "parameter_notes": {
            "baseline_persistence": "baseline overlay only, not used by Formula or Formula_Adjustable",
            "legacy_wobble_surface": "legacy comparison overlay only, not used by Formula or Formula_Adjustable",
            "legacy_raw_address_top1": "legacy comparison overlay only, not used by Formula or Formula_Adjustable",
        },
        "leakage_guard": [
            "Formula uses raw samples at or before origin t only.",
            "Formula is a deterministic layer-contact cascade.",
            "Formula_Adjustable is the same formula with exposed constants.",
            "No lag ridge, persistence blend, native-value decoder, historical nearest-neighbour terrain lookup, future geometry oracle, smoothing, or visual shift is used inside the formula.",
            "Persistence/wobble/raw-address traces are labelled display overlays only.",
        ],
        "layers": {"layer_specs": LAYER_SPECS, "upper_specs": UPPER_SPECS},
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
        "window.ARA_LAYERED_SAND_SINGLE_FORMULA = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
