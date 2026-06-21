"""
ara_terrain_spin_standin_test.py

Test: replace raw data input (T) with terrain-derived ARA decoded back into
spin components. Keep the EXACT Layered Sand formula — same cascade, same
terrain reading, same parameters — just swap where the spin comes from.

The idea (Dylan's):
  ARA = Accumulation / Release ratio. ARA develops FROM the topographic spheres.
  If we know where we ARE on each sphere (from previous step or calibration),
  the terrain tells us the local energy state. Decode that back into the
  equivalent of raw NINO/SOI/PDO and feed it through the identical formula.

  The formula is NOT wrong — it's a terrain scanner with instrument delay.
  We just need to generate T from within the formula rather than from data.

Reconstruction model (fitted from actual data):
  Given value V = ara_to_value(ARA):
    nino_spin ≈ tanh(V × 0.528)
    soi_spin  ≈ tanh(V × 0.390)   [already anti-correlated, then negated in raw_spin]
    pdo_spin  ≈ tanh(V × 0.206)
  Quality: nino r=0.92, soi r=0.83, pdo r=0.60

Two modes:
  A. Calibrated: use real raw_spin for first N steps, then switch to terrain spin
  B. Full formula: run the identical Layered Sand cascade with terrain spin
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ara_cross_rung_spin_transfer_test import HOME, HORIZONS, PHI
from ara_fractal_sphere_terrain_reader import (
    ara_to_value, value_to_ara, read_fractal_terrain, clamp_ara,
)
from ara_geometry_transport_test import clean_for_json, load_enso_frame
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import (
    aggregate_focus, raw_delta, raw_value, rounded, squash,
)
from ara_sphere_orientation_roll_predictor import EPS, sign
from ara_layered_sand_single_formula import (
    FORMULA, LAYER_SPECS, UPPER_SPECS,
    clamp, sigmoid, month_anchor, raw_spin, upper_pressure,
    read_sphere_terrain, vector_from_state, propagate_layer,
    formula_predict,
)

# ─── Reconstruction coefficients (fitted from data) ─────────────────────────
NINO_SCALE = 0.528
SOI_SCALE = 0.390
PDO_SCALE = 0.206


def terrain_spin(ara_position, period, name):
    """
    Produce the same dict as raw_spin(), but derived from an ARA position
    on the topographic sphere instead of from raw data.

    ARA → value → decompose into nino/soi/pdo spin components → build
    forward/lateral/twist/pressure exactly as raw_spin does.
    """
    value = ara_to_value(clamp_ara(ara_position))

    # Reconstruct individual spin components from the unified value
    nino = math.tanh(value * NINO_SCALE)
    soi = math.tanh(value * SOI_SCALE)
    pdo = math.tanh(value * PDO_SCALE)

    # Exact same formulas as raw_spin
    frequency = math.sqrt(HOME / max(float(period), EPS))
    forward = frequency * (0.43 * nino + 0.41 * soi + 0.16 * pdo)
    lateral = frequency * (0.48 * (nino - soi) + 0.22 * pdo)
    twist = frequency * (0.36 * nino * soi + 0.24 * (nino + soi) + 0.18 * pdo)
    pressure = frequency * (abs(nino) + abs(soi) + 0.55 * abs(pdo))

    return {
        "name": name,
        "period": float(period),
        "frequency": float(frequency),
        "forward": float(forward),
        "lateral": float(lateral),
        "twist": float(twist),
        "pressure": float(pressure),
        "ara": float(clamp_ara(ara_position)),
        "nino_spin": float(nino),
        "soi_spin": float(soi),
        "pdo_spin": float(pdo),
    }


def terrain_upper_pressure(ara_position):
    """Upper pressure from terrain-derived ARA instead of raw data."""
    parts = []
    for spec in UPPER_SPECS:
        spin = terrain_spin(ara_position, spec["period"], spec["name"])
        slow_weight = math.sqrt(HOME / spec["period"])
        parts.append({
            "name": spec["name"],
            "period": spec["period"],
            "compression": slow_weight * spin["pressure"],
            "direction": slow_weight * spin["forward"],
            "lateral": slow_weight * spin["lateral"],
            "twist": slow_weight * spin["twist"],
        })
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


def formula_predict_terrain(row, horizon, params, layer_aras):
    """
    Identical to formula_predict() but uses terrain_spin() instead of raw_spin().

    layer_aras: list of 5 ARA positions, one per layer sphere.
    These come from the previous step's output (or calibration).
    """
    # Build spins from terrain-derived ARA instead of raw data
    spins = []
    for i, spec in enumerate(LAYER_SPECS):
        spins.append(terrain_spin(layer_aras[i], spec["period"], spec["name"]))

    # Upper pressure from the measured layer's ARA
    upper = terrain_upper_pressure(layer_aras[-1])

    # Exact same cascade as formula_predict
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

    # Extract the next layer ARAs from the cascade (for feeding into next step)
    next_layer_aras = [layer["ara"] for layer in layers]

    return {
        "value": float(value),
        "arrival_ara": float(arrival_ara),
        "arrival_phase": float(arrival_phase),
        "force_ara": float(terrain["force_ara"]),
        "delta_ara": float(delta_ara),
        "delta_phase": float(delta_phase),
        "terrain_slope": float(terrain["combined_slope"]),
        "terrain_spillover": float(terrain["ara_spillover"]),
        "final_forward": float(state["forward"]),
        "final_pressure": float(state["pressure"]),
        "layers": layers,
        "next_layer_aras": next_layer_aras,
    }


def run():
    data = json.loads((HERE / "ara_sphere_atlas_data.json").read_text(encoding="utf-8"))
    frame = load_enso_frame()

    print("=" * 100)
    print("TERRAIN SPIN STAND-IN TEST")
    print("=" * 100)
    print()
    print("Keep exact Layered Sand formula. Replace raw_spin() data reader")
    print("with terrain-derived ARA → decoded spin components.")
    print(f"Reconstruction: nino×{NINO_SCALE}, soi×{SOI_SCALE}, pdo×{PDO_SCALE}")
    print()

    all_results = {}

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in data["records_by_horizon"][h]]

        # ─── Mode A: Original formula (data-fed) ────────────────────────
        for row in records:
            result = formula_predict(frame, row, horizon, FORMULA)
            row["original_pred"] = result["value"]
            row["original_layer_aras"] = [layer["ara"] for layer in result["layers"]]
            row["original_spins"] = result["layers"]  # save for comparison

        # ─── Mode B: Terrain spin, ARA from data (each step independent) ─
        for row in records:
            # Use the same layer ARAs that the original formula computed from data
            layer_aras = row["original_layer_aras"]
            result = formula_predict_terrain(row, horizon, FORMULA, layer_aras)
            row["terrain_same_ara_pred"] = result["value"]

        # ─── Mode C: Terrain spin, ARA cascaded from previous step ───────
        # First step uses data ARAs, then each step's output ARAs feed the next
        prev_layer_aras = None
        for i, row in enumerate(records):
            if prev_layer_aras is None:
                # Bootstrap from data
                layer_aras = row["original_layer_aras"]
            else:
                layer_aras = prev_layer_aras

            result = formula_predict_terrain(row, horizon, FORMULA, layer_aras)
            row["terrain_cascaded_pred"] = result["value"]
            prev_layer_aras = result["next_layer_aras"]

        # ─── Mode D: Calibrate N steps from data, then free-run ──────────
        calibration_n = 20
        prev_layer_aras = None
        for i, row in enumerate(records):
            if i < calibration_n:
                # Use real data ARAs during calibration
                result = formula_predict(frame, row, horizon, FORMULA)
                row["hybrid_pred"] = result["value"]
                prev_layer_aras = [layer["ara"] for layer in result["layers"]]
            else:
                # Free-run: terrain spin from previous step's ARAs
                result = formula_predict_terrain(row, horizon, FORMULA, prev_layer_aras)
                row["hybrid_pred"] = result["value"]
                prev_layer_aras = result["next_layer_aras"]

        # ─── Score all modes ─────────────────────────────────────────────
        modes = {
            "original": "original_pred",
            "terrain_same_ara": "terrain_same_ara_pred",
            "terrain_cascaded": "terrain_cascaded_pred",
            "hybrid_20cal": "hybrid_pred",
        }

        print(f"h={horizon:>2} months")
        for mode_name, pred_key in modes.items():
            pts = [point(r["origin"], r["target"], r[pred_key], r["actual"], r["current"])
                   for r in records]
            score = extended_score(pts)
            print(f"  {mode_name:22s} {format_score(score)}")

        # Score the free-run portion only (after calibration)
        free_records = records[calibration_n:]
        if free_records:
            pts_free = [point(r["origin"], r["target"], r["hybrid_pred"], r["actual"], r["current"])
                        for r in free_records]
            score_free = extended_score(pts_free)
            print(f"  {'hybrid_free_only':22s} {format_score(score_free)}")

        print()

        # Save for viz
        all_results[h] = [{
            "origin": r["origin"],
            "target": r["target"],
            "actual": r["actual"],
            "current": r["current"],
            "original": rounded(r["original_pred"]),
            "terrain_same_ara": rounded(r["terrain_same_ara_pred"]),
            "terrain_cascaded": rounded(r["terrain_cascaded_pred"]),
            "hybrid": rounded(r["hybrid_pred"]),
            "calibrated": i < calibration_n,
        } for i, r in enumerate(records)]

    # ─── Save results ────────────────────────────────────────────────────
    out = {
        "date": "2026-05-29",
        "method": "terrain_spin_standin",
        "reconstruction_coefficients": {
            "nino_scale": NINO_SCALE,
            "soi_scale": SOI_SCALE,
            "pdo_scale": PDO_SCALE,
        },
        "calibration_steps": 20,
        "records": clean_for_json(all_results),
    }

    out_path = HERE / "ara_terrain_spin_standin_result.json"
    out_path.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")

    # JS for viz
    js_path = HERE / "ara_terrain_spin_standin_viz_data.js"
    js_path.write_text(
        "window.TERRAIN_STANDIN_DATA = " + json.dumps(clean_for_json(out)) + ";\n",
        encoding="utf-8",
    )

    print(f"Saved → {out_path}")
    print(f"Saved → {js_path}")


if __name__ == "__main__":
    run()
