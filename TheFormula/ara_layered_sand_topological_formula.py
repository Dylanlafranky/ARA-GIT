"""
ara_layered_sand_topological_formula.py

Layered-sand roll formula with recursive ARA sphere topology inside the
measured spheres.

This is the corrected combination:

    layered sand formula = how the sphere rolls / arrives
    recursive ARA grid  = what terrain exists at that arrived coordinate

It does not use the recursive grid as a replacement for the layered formula.
It replaces the old per-sphere terrain read inside the formula with the
topology described by the user:

    ARA 0..2
    root phi / anti-phi
    sub-ARA phi / anti-phi
    sub-sub-ARA phi / anti-phi
    depth weights fall by phi each level
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import ara_layered_sand_single_formula as single
from ara_geometry_transport_test import clean_for_json, load_enso_frame
from ara_layered_sand_closed_cutoff_run import MANUAL_SCREENSHOT_PARAMS, WAVECYCLE_SCREENSHOT_PARAMS
from ara_raw_watershed_slice_test import rounded
from ara_recursive_sphere_grid_predictor import axis_recursive_read, phase_to_ara
from ara_sphere_orientation_roll_predictor import EPS, sign
from ara_shape_kernel_test import PHI


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
OUT_JSON = HERE / "ara_layered_sand_topological_formula_result.json"
OUT_JS = HERE / "ara_layered_sand_topological_formula_result.js"

HORIZONS = [3, 6, 12, 18, 24]
MODEL_KEYS = [
    "persistence",
    "legacy_layered_formula",
    "topological_formula",
    "topological_rotated",
    "topological_phi_wobble",
    "topological_saturation_gate",
    "topological_manual",
    "topological_wavecycle",
]

GOLDEN_ANGLE_DEG = 360.0 / (PHI * PHI)
TIME_ZERO_YEAR = 2000
TIME_ZERO_MONTH = 1


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def corr(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if len(xs) < 3 or np.std(xs) <= EPS or np.std(ys) <= EPS:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def score(rows, key):
    usable = [row for row in rows if row.get(key) is not None and np.isfinite(row.get(key))]
    if not usable:
        return {"n": 0, "mae": None, "corr": None, "direction": None, "amp_ratio": None, "corr_with_current": None}
    pred = np.asarray([row[key] for row in usable], dtype=float)
    actual = np.asarray([row["actual"] for row in usable], dtype=float)
    current = np.asarray([row["current"] for row in usable], dtype=float)
    truth_delta = actual - current
    pred_delta = pred - current
    turn_mask = np.abs(truth_delta) > EPS
    return {
        "n": int(len(usable)),
        "mae": float(np.mean(np.abs(pred - actual))),
        "corr": corr(pred, actual),
        "direction": float(np.mean(np.sign(pred_delta[turn_mask]) == np.sign(truth_delta[turn_mask])))
        if np.any(turn_mask)
        else None,
        "amp_ratio": float(np.std(pred_delta) / np.std(truth_delta)) if np.std(truth_delta) > EPS else None,
        "corr_with_current": corr(pred, current),
    }


def topological_read_sphere_terrain(
    arrival_ara,
    current_ara,
    phase_deg,
    contact_pressure,
    lower_drive,
    upper_gate,
    params,
):
    """
    Same call signature as ara_layered_sand_single_formula.read_sphere_terrain.

    The read is now the filled recursive ARA topology:
    - ARA axis terrain
    - phase/longitude axis terrain mapped onto 0..2
    - phi valleys pull like water downhill
    - anti-phi and ridges create counter/pressure terms
    """
    ara_axis = axis_recursive_read(arrival_ara)
    phase_axis = axis_recursive_read(phase_to_ara(phase_deg))

    ara_slope = float(ara_axis["weighted_slope_to_phi"])
    phase_slope = float(phase_axis["weighted_slope_to_phi"])
    anti_pressure = float(ara_axis["anti_phi_pressure"] - phase_axis["anti_phi_pressure"])
    ridge_pressure = float(0.62 * ara_axis["ridge_pressure"] + 0.38 * phase_axis["ridge_pressure"])

    contact = clamp(
        0.22 * abs(float(contact_pressure))
        + 0.18 * abs(float(lower_drive))
        + 0.10 * abs(float(upper_gate)),
        0.0,
        2.0,
    )
    ridge_brake = 1.0 + 0.55 * ridge_pressure + 0.22 * abs(float(upper_gate))
    force_gain = clamp(
        0.16
        + 0.42 * params["terrain_pull"]
        + 0.18 * params["terrain_spill"] * ridge_pressure
        + 0.15 * contact,
        0.04,
        1.80,
    )

    combined_slope = (
        params["ara_terrain"] * ara_slope
        + 0.36 * params["phase_terrain"] * phase_slope
        + 0.08 * anti_pressure
    )
    force_ara = clamp(arrival_ara + (force_gain / ridge_brake) * combined_slope, 0.0, 2.0)

    return {
        "arrival_ara": float(arrival_ara),
        "phase_ara": float(phase_to_ara(phase_deg)),
        "force_ara": float(force_ara),
        "combined_slope": float(combined_slope),
        "ara_spillover": float(ridge_pressure),
        "ara_force": float(force_gain),
        "phase_target": float(phase_axis["weighted_phi"]),
        "phase_slope": float(phase_slope),
        "ara_target": float(ara_axis["weighted_phi"]),
        "anti_pressure": float(anti_pressure),
        "ridge_brake": float(ridge_brake),
        "ara_deep_address": ara_axis["deep_address"],
        "phase_deep_address": phase_axis["deep_address"],
    }


def norm(vec):
    arr = np.asarray(vec, dtype=float)
    length = float(np.linalg.norm(arr))
    if length <= EPS:
        return arr
    return arr / length


def sphere_point(ara, phase_deg):
    lon = math.radians(float(phase_deg) % 360.0)
    y = 1.0 - clamp(ara, 0.0, 2.0)
    ring = math.sqrt(max(0.0, 1.0 - y * y))
    return np.asarray([ring * math.cos(lon), y, ring * math.sin(lon)], dtype=float)


def point_to_ara_phase(point):
    p = norm(point)
    ara = clamp(1.0 - p[1], 0.0, 2.0)
    phase = (math.degrees(math.atan2(p[2], p[0])) + 360.0) % 360.0
    return ara, phase


def rotate_about_axis(point, axis, angle_rad):
    axis = norm(axis)
    if float(np.linalg.norm(axis)) <= EPS:
        return point
    p = np.asarray(point, dtype=float)
    return (
        p * math.cos(angle_rad)
        + np.cross(axis, p) * math.sin(angle_rad)
        + axis * float(np.dot(axis, p)) * (1.0 - math.cos(angle_rad))
    )


def local_east(phase_deg):
    lon = math.radians(float(phase_deg) % 360.0)
    return np.asarray([-math.sin(lon), 0.0, math.cos(lon)], dtype=float)


def month_index(origin):
    year, month, *_ = str(origin).split("-")
    return (int(year) - TIME_ZERO_YEAR) * 12 + (int(month) - TIME_ZERO_MONTH)


def phi_time_wobble(row, horizon):
    """
    Golden-angle wobble phase from time alone.

    This deliberately uses only the origin date and requested horizon. It is a
    deterministic pose clock, not a fit to the future target value.
    """
    t = month_index(row["origin"]) + int(horizon)
    phase_deg = (t * GOLDEN_ANGLE_DEG) % 360.0
    phase_rad = math.radians(phase_deg)
    companion_rad = phase_rad + (2.0 * math.pi / PHI)
    return {
        "time_index": int(t),
        "phase_deg": float(phase_deg),
        "axis": norm(
            np.asarray(
                [
                    math.cos(phase_rad),
                    math.sin(companion_rad) / PHI,
                    math.sin(phase_rad),
                ],
                dtype=float,
            )
        ),
        "meridian_phase_deg": float((row["phase_clock_origin"] + phase_deg / PHI) % 360.0),
    }


def true_rotated_pose(row, formula, horizon, params, phi_wobble=False):
    """
    Rotate the measured sphere itself instead of adding tiny ARA offsets.

    The old branch used:
        arrival_ara = current_ara + delta_ara
        arrival_phase = current_phase + delta_phase

    This branch treats delta_phase/final roll as a 3D rotation. The clock
    component rotates around the vertical axis; lower/contact roll tilts that
    axis, so the same phase movement can carry the reading point into a new
    ARA latitude instead of staying in the current band.
    """
    p0 = sphere_point(row["ara_current"], row["phase_clock_origin"])
    clock_axis = np.asarray([0.0, 1.0, 0.0], dtype=float)
    raw_contact_axis = norm(
        np.asarray(
            [
                formula["final_lateral"] + 0.35 * formula["final_twist"],
                0.30 * formula["final_twist"],
                formula["final_forward"] - 0.25 * formula["final_lateral"],
            ],
            dtype=float,
        )
    )
    phi_wobble_state = None
    if phi_wobble:
        phi_wobble_state = phi_time_wobble(row, horizon)
        phi_rotated_contact = rotate_about_axis(
            raw_contact_axis,
            clock_axis,
            math.radians(phi_wobble_state["phase_deg"]),
        )
        contact_axis = norm((1.0 / PHI) * phi_rotated_contact + (1.0 - 1.0 / PHI) * phi_wobble_state["axis"])
    else:
        contact_axis = raw_contact_axis
    tilt = clamp(0.18 + 0.42 * abs(formula["final_pressure"]) / (1.0 + abs(formula["upper_compression"])), 0.10, 0.85)
    axis = norm((1.0 - tilt) * clock_axis + tilt * contact_axis)
    angle = math.radians(float(formula["delta_phase"]))
    p1 = rotate_about_axis(p0, axis, angle)

    # Apply the north/south roll as actual meridian rotation, not as a small
    # scalar added to ARA. This is deliberately still driven by the layered
    # formula's current/past roll variables.
    meridian_phase = phi_wobble_state["meridian_phase_deg"] if phi_wobble_state else row["phase_clock_origin"]
    meridian_axis = local_east(meridian_phase)
    meridian_angle = clamp(float(formula["delta_ara"]) * (1.0 + 0.35 * float(params["measured_roll"])), -1.4, 1.4)
    p2 = rotate_about_axis(p1, meridian_axis, meridian_angle)
    ara, phase = point_to_ara_phase(p2)
    pose = {
        "arrival_ara": float(ara),
        "arrival_phase": float(phase),
        "rotation_axis": clean_for_json(axis),
        "rotation_angle_deg": float(math.degrees(angle)),
        "meridian_angle_deg": float(math.degrees(meridian_angle)),
        "tilt": float(tilt),
    }
    if phi_wobble_state:
        pose["phi_wobble"] = {
            "time_index": phi_wobble_state["time_index"],
            "phase_deg": phi_wobble_state["phase_deg"],
            "meridian_phase_deg": phi_wobble_state["meridian_phase_deg"],
            "axis": clean_for_json(phi_wobble_state["axis"]),
        }
    return pose


def predict_true_rotation(frame, row, horizon, params, phi_wobble=False):
    base = predict_with_read(frame, row, horizon, params, topological_read_sphere_terrain)
    pose = true_rotated_pose(row, base, horizon, params, phi_wobble=phi_wobble)
    terrain = topological_read_sphere_terrain(
        pose["arrival_ara"],
        row["ara_current"],
        pose["arrival_phase"],
        base["final_pressure"],
        base["final_forward"],
        base["upper_compression"],
        params,
    )
    return {
        **base,
        "value": float(single.ara_to_value(terrain["force_ara"])),
        "arrival_ara": pose["arrival_ara"],
        "arrival_phase": pose["arrival_phase"],
        "force_ara": terrain["force_ara"],
        "terrain_slope": terrain["combined_slope"],
        "terrain_spillover": terrain["ara_spillover"],
        "true_rotation": pose,
    }


def predict_phi_wobble(frame, row, horizon, params):
    return predict_true_rotation(frame, row, horizon, params, phi_wobble=True)


def rotation_diagnostic(row, formula, rotated):
    spins = formula["spins"]
    upper = formula["upper"]
    current_term = math.tanh(float(row["current"]) / 0.45)
    basin_pressure = (
        float(spins[-1]["forward"])
        + 0.45 * float(upper["direction"])
        + 0.25 * float(spins[-2]["forward"])
        + 0.32 * current_term
    )
    rotated_delta = float(rotated["value"]) - float(row["current"])
    truth_delta = float(row["actual"]) - float(row["current"])
    conflict = abs(basin_pressure) > 0.20 and basin_pressure * rotated_delta < 0.0
    wrong = abs(truth_delta) > EPS and truth_delta * rotated_delta < 0.0
    return {
        "basin_pressure": float(basin_pressure),
        "rotated_delta": float(rotated_delta),
        "truth_delta": float(truth_delta),
        "rotation_conflicts_basin": bool(conflict),
        "rotated_wrong_direction": bool(wrong),
        "measured_forward": float(spins[-1]["forward"]),
        "coarse_forward": float(spins[-2]["forward"]),
        "upper_direction": float(upper["direction"]),
        "current_term": float(current_term),
    }


def basin_saturation_threshold(current_value):
    # Candidate ENSO-specific dwell scales from the home wave:
    # warm events release faster; cold/recharge basins hold longer.
    return single.HOME / (PHI**3.5) if float(current_value) >= 0.0 else single.HOME / (PHI**2.0)


def sigmoid(value):
    return 1.0 / (1.0 + math.exp(-clamp(value, -60.0, 60.0)))


def basin_age_months(frame, origin):
    import pandas as pd

    date = pd.Timestamp(origin)
    if date not in frame.index:
        return 0
    value = float(frame.loc[date, "NINO"])
    basin_sign = sign(value)
    if basin_sign == 0:
        return 0
    age = 0
    cursor = date
    while cursor in frame.index and sign(float(frame.loc[cursor, "NINO"])) == basin_sign:
        age += 1
        cursor = cursor - pd.DateOffset(months=1)
    return int(age)


def predict_saturation_gate(frame, row, horizon, params):
    base = predict_with_read(frame, row, horizon, params, topological_read_sphere_terrain)
    rotated = predict_true_rotation(frame, row, horizon, params)
    current_ara = float(row["ara_current"])
    rotated_ara = float(rotated["arrival_ara"])
    crossing = (current_ara - 1.0) * (rotated_ara - 1.0) < 0.0
    age = basin_age_months(frame, row["origin"])
    threshold = basin_saturation_threshold(row["current"])
    saturation = sigmoid((age - threshold) / 4.0)

    if not crossing:
        return {
            **rotated,
            "saturation_gate": {
                "crossing": False,
                "basin_age_months": age,
                "threshold_months": float(threshold),
                "saturation": 1.0,
                "held_value": None,
                "rotated_value": rotated["value"],
            },
        }

    # If the basin is not saturated enough to cross, the water is allowed to
    # reach the ridge/contact line but not to spill into the next basin yet.
    held_ara = 1.0 + (0.01 if current_ara >= 1.0 else -0.01)
    held_terrain = topological_read_sphere_terrain(
        held_ara,
        current_ara,
        rotated["arrival_phase"],
        base["final_pressure"],
        base["final_forward"],
        base["upper_compression"],
        params,
    )
    held_value = float(single.ara_to_value(held_terrain["force_ara"]))
    value = (1.0 - saturation) * held_value + saturation * float(rotated["value"])
    force_ara = (1.0 - saturation) * float(held_terrain["force_ara"]) + saturation * float(rotated["force_ara"])

    return {
        **rotated,
        "value": float(value),
        "force_ara": float(force_ara),
        "terrain_slope": float((1.0 - saturation) * held_terrain["combined_slope"] + saturation * rotated["terrain_slope"]),
        "terrain_spillover": float(
            (1.0 - saturation) * held_terrain["ara_spillover"] + saturation * rotated["terrain_spillover"]
        ),
        "saturation_gate": {
            "crossing": True,
            "basin_age_months": age,
            "threshold_months": float(threshold),
            "saturation": float(saturation),
            "held_ara": float(held_ara),
            "held_value": held_value,
            "held_force_ara": float(held_terrain["force_ara"]),
            "rotated_value": rotated["value"],
        },
    }


def predict_with_read(frame, row, horizon, params, terrain_reader):
    old_reader = single.read_sphere_terrain
    try:
        single.read_sphere_terrain = terrain_reader
        return single.formula_predict(frame, row, horizon, params)
    finally:
        single.read_sphere_terrain = old_reader


def run():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    frame = load_enso_frame()
    records_by_h = {}
    scores = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA layered-sand topological formula")
    print("=" * 100)
    print("Layered sand roll is kept. Per-sphere terrain is replaced with recursive ARA topology.")
    print()

    for horizon in HORIZONS:
        hkey = str(horizon)
        rows = []
        for source in data["records_by_horizon"][hkey]:
            legacy = single.formula_predict(frame, source, horizon, single.FORMULA)
            topo_base = predict_with_read(frame, source, horizon, single.FORMULA, topological_read_sphere_terrain)
            topo_rotated = predict_true_rotation(frame, source, horizon, single.FORMULA)
            topo_phi_wobble = predict_phi_wobble(frame, source, horizon, single.FORMULA)
            topo_saturation = predict_saturation_gate(frame, source, horizon, single.FORMULA)
            rotated_diag = rotation_diagnostic(source, topo_base, topo_rotated)
            basin_age = basin_age_months(frame, source["origin"])
            topo_manual = predict_with_read(frame, source, horizon, MANUAL_SCREENSHOT_PARAMS, topological_read_sphere_terrain)
            topo_wavecycle = predict_with_read(frame, source, horizon, WAVECYCLE_SCREENSHOT_PARAMS, topological_read_sphere_terrain)
            row = {
                "origin": source["origin"],
                "target": source["target"],
                "horizon": int(horizon),
                "current": rounded(source["current"]),
                "actual": rounded(source["actual"]),
                "ara_current": rounded(source["ara_current"]),
                "phase_clock_origin": rounded(source["phase_clock_origin"]),
                "persistence": rounded(source["current"]),
                "legacy_layered_formula": rounded(legacy["value"]),
                "topological_formula": rounded(topo_base["value"]),
                "topological_rotated": rounded(topo_rotated["value"]),
                "topological_phi_wobble": rounded(topo_phi_wobble["value"]),
                "topological_saturation_gate": rounded(topo_saturation["value"]),
                "topological_manual": rounded(topo_manual["value"]),
                "topological_wavecycle": rounded(topo_wavecycle["value"]),
                "rotation_conflicts_basin": rotated_diag["rotation_conflicts_basin"],
                "rotated_wrong_direction": rotated_diag["rotated_wrong_direction"],
                "basin_pressure": rounded(rotated_diag["basin_pressure"]),
                "basin_age_months": basin_age,
                "topological": clean_for_json(
                    {
                        "formula": {
                            "arrival_ara": topo_base["arrival_ara"],
                            "arrival_phase": topo_base["arrival_phase"],
                            "force_ara": topo_base["force_ara"],
                            "delta_ara": topo_base["delta_ara"],
                            "delta_phase": topo_base["delta_phase"],
                            "terrain_slope": topo_base["terrain_slope"],
                            "terrain_spillover": topo_base["terrain_spillover"],
                        },
                        "rotated": {
                            "arrival_ara": topo_rotated["arrival_ara"],
                            "arrival_phase": topo_rotated["arrival_phase"],
                            "force_ara": topo_rotated["force_ara"],
                            "delta_ara": topo_rotated["delta_ara"],
                            "delta_phase": topo_rotated["delta_phase"],
                            "terrain_slope": topo_rotated["terrain_slope"],
                            "terrain_spillover": topo_rotated["terrain_spillover"],
                            "true_rotation": topo_rotated["true_rotation"],
                            "diagnostic": rotated_diag,
                            "basin_age_months": basin_age,
                        },
                        "saturation_gate": {
                            "arrival_ara": topo_saturation["arrival_ara"],
                            "arrival_phase": topo_saturation["arrival_phase"],
                            "force_ara": topo_saturation["force_ara"],
                            "delta_ara": topo_saturation["delta_ara"],
                            "delta_phase": topo_saturation["delta_phase"],
                            "terrain_slope": topo_saturation["terrain_slope"],
                            "terrain_spillover": topo_saturation["terrain_spillover"],
                            "true_rotation": topo_saturation["true_rotation"],
                            "gate": topo_saturation["saturation_gate"],
                        },
                        "phi_wobble": {
                            "arrival_ara": topo_phi_wobble["arrival_ara"],
                            "arrival_phase": topo_phi_wobble["arrival_phase"],
                            "force_ara": topo_phi_wobble["force_ara"],
                            "delta_ara": topo_phi_wobble["delta_ara"],
                            "delta_phase": topo_phi_wobble["delta_phase"],
                            "terrain_slope": topo_phi_wobble["terrain_slope"],
                            "terrain_spillover": topo_phi_wobble["terrain_spillover"],
                            "true_rotation": topo_phi_wobble["true_rotation"],
                        },
                        "manual": {
                            "arrival_ara": topo_manual["arrival_ara"],
                            "arrival_phase": topo_manual["arrival_phase"],
                            "force_ara": topo_manual["force_ara"],
                            "delta_ara": topo_manual["delta_ara"],
                            "delta_phase": topo_manual["delta_phase"],
                            "terrain_slope": topo_manual["terrain_slope"],
                            "terrain_spillover": topo_manual["terrain_spillover"],
                        },
                        "wavecycle": {
                            "arrival_ara": topo_wavecycle["arrival_ara"],
                            "arrival_phase": topo_wavecycle["arrival_phase"],
                            "force_ara": topo_wavecycle["force_ara"],
                            "delta_ara": topo_wavecycle["delta_ara"],
                            "delta_phase": topo_wavecycle["delta_phase"],
                            "terrain_slope": topo_wavecycle["terrain_slope"],
                            "terrain_spillover": topo_wavecycle["terrain_spillover"],
                        },
                    }
                ),
            }
            rows.append(row)

        records_by_h[hkey] = rows
        for key in MODEL_KEYS:
            scores[key][hkey] = score(rows, key)
        diagnostics[hkey] = {
            "mean_abs_topological_delta_ara": float(
                np.mean([abs(row["topological"]["formula"]["delta_ara"]) for row in rows])
            ),
            "mean_abs_rotated_arrival_shift_ara": float(
                np.mean([abs(row["topological"]["rotated"]["arrival_ara"] - row["ara_current"]) for row in rows])
            ),
            "mean_abs_phi_wobble_arrival_shift_ara": float(
                np.mean([abs(row["topological"]["phi_wobble"]["arrival_ara"] - row["ara_current"]) for row in rows])
            ),
            "mean_phi_wobble_phase_deg": float(
                np.mean([row["topological"]["phi_wobble"]["true_rotation"]["phi_wobble"]["phase_deg"] for row in rows])
            ),
            "mean_abs_topological_delta_phase": float(
                np.mean([abs(row["topological"]["formula"]["delta_phase"]) for row in rows])
            ),
            "mean_abs_rotated_angle_deg": float(
                np.mean([abs(row["topological"]["rotated"]["true_rotation"]["rotation_angle_deg"]) for row in rows])
            ),
            "mean_abs_topological_terrain_slope": float(
                np.mean([abs(row["topological"]["formula"]["terrain_slope"]) for row in rows])
            ),
            "mean_topological_spillover": float(
                np.mean([row["topological"]["formula"]["terrain_spillover"] for row in rows])
            ),
            "rotation_conflict_rate": float(np.mean([row["rotation_conflicts_basin"] for row in rows])),
            "rotated_wrong_direction_rate": float(np.mean([row["rotated_wrong_direction"] for row in rows])),
            "wrong_when_conflict_rate": float(
                np.mean(
                    [
                        row["rotated_wrong_direction"]
                        for row in rows
                        if row["rotation_conflicts_basin"]
                    ]
                )
            )
            if any(row["rotation_conflicts_basin"] for row in rows)
            else None,
            "mean_basin_age_wrong_direction": float(
                np.mean([row["basin_age_months"] for row in rows if row["rotated_wrong_direction"]])
            )
            if any(row["rotated_wrong_direction"] for row in rows)
            else None,
            "mean_basin_age_correct_direction": float(
                np.mean([row["basin_age_months"] for row in rows if not row["rotated_wrong_direction"]])
            )
            if any(not row["rotated_wrong_direction"] for row in rows)
            else None,
            "saturation_crossing_rate": float(
                np.mean([row["topological"]["saturation_gate"]["gate"]["crossing"] for row in rows])
            ),
            "mean_saturation_when_crossing": float(
                np.mean(
                    [
                        row["topological"]["saturation_gate"]["gate"]["saturation"]
                        for row in rows
                        if row["topological"]["saturation_gate"]["gate"]["crossing"]
                    ]
                )
            )
            if any(row["topological"]["saturation_gate"]["gate"]["crossing"] for row in rows)
            else None,
        }
        line = [f"h={horizon:>2}m"]
        for key in MODEL_KEYS:
            sc = scores[key][hkey]
            line.append(f"{key}: corr={rounded(sc['corr']) if sc['corr'] is not None else 'n/a'} mae={rounded(sc['mae'])}")
        print(" | ".join(line))

    result = {
        "date": "2026-05-26",
        "method": "Layered-sand roll formula with recursive ARA sphere topology",
        "source_atlas": str(IN_JSON.name),
        "leakage_rules": [
            "The layered-sand formula is kept as the roll/arrival mechanism.",
            "The per-sphere terrain read is recursive ARA/sub-ARA topology.",
            "Phi-time wobble uses only the origin date, horizon, and golden-angle precession.",
            "No future-origin row or future target is read inside prediction.",
            "Persistence and legacy layered formula are comparison overlays only.",
        ],
        "topology_definition": {
            "root_phi": float(PHI),
            "root_anti_phi": float(2.0 - PHI),
            "golden_angle_deg": float(GOLDEN_ANGLE_DEG),
            "depth_weight": "1 / phi^(depth - 1)",
            "terrain_axes": ["ARA latitude", "phase longitude mapped to 0..2"],
            "water_rule": "arrival coordinate is pulled toward weighted local phi valleys with ridge/anti-phi pressure",
            "phi_time_wobble_rule": "wobble axis precesses by 360 / phi^2 degrees per month of origin+horizon time",
        },
        "model_keys": MODEL_KEYS,
        "scores": scores,
        "diagnostics": diagnostics,
        "records_by_horizon": records_by_h,
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(result), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LAYERED_SAND_TOPOLOGICAL_FORMULA = " + json.dumps(clean_for_json(result), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print()
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
