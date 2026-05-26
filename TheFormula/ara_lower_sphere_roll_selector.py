"""
ara_lower_sphere_roll_selector.py

Strict-causal test of the user's correction:

    the lower spheres determine the roll/contact mode

The previous displacement-mode script used broad current-state similarity to
select the roll mode. That restored amplitude but often chose the wrong route.
This version selects roll displacement from lower-sphere spin/torque features
only, then applies that displacement before reading deterministic fractal ARA
terrain.

No future value decoder, no lag ridge, no future geometry oracle, no visual
shift. Historical roll displacements are eligible only when their targets are
already before the current origin.
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from ara_fractal_sphere_terrain_reader import ara_to_value, read_fractal_terrain
from ara_geometry_transport_test import clean_for_json
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, rounded
from ara_roll_displacement_mode_predictor import (
    DISTANCE_BANDWIDTH,
    MODE_NEIGHBOR_COUNT,
    NEIGHBOR_COUNT,
    coarse_band,
    components_to_omega,
    load_comparison_predictions,
    log_roll_components,
)
from ara_sphere_orientation_roll_predictor import (
    EPS,
    HORIZONS,
    completed_motion_candidates,
    roll_terms,
    row_surface_vec,
    row_target_vec,
    rotate_vec,
    sign,
    unit,
    vec_to_ara,
)


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
RAW_ADDRESS_JSON = HERE / "ara_raw_terrain_address_lookup_result.json"
FRACTAL_JSON = HERE / "ara_fractal_sphere_terrain_reader_result.json"
LOWER_SPIN_JSON = HERE / "ara_raw_watershed_lower_spin_result.json"
OUT_JSON = HERE / "ara_lower_sphere_roll_selector_result.json"
OUT_JS = HERE / "ara_lower_sphere_roll_selector_result.js"

MIN_SELECTOR_TRAIN = 56

MODEL_KEYS = [
    "persistence",
    "wobble_surface_analog",
    "raw_address_top1",
    "fractal_phi_force",
    "lower_core_top1",
    "lower_core_mode_top1",
    "lower_gate_top1",
    "lower_gate_mode_top1",
    "lower_gate_weighted",
]


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def mode_label(row):
    comp = row["roll_components"]
    delta_ara = float(row["ara_actual"]) - float(row["ara_current"])
    ara_dir = sign(delta_ara, 0.06)
    forward = sign(comp[0], 0.055)
    lateral = sign(comp[1], 0.055)
    twist = sign(comp[2], 0.035)
    spill = coarse_band(row["ara_actual"], 2) != coarse_band(row["ara_current"], 2)
    return f"a{ara_dir:+d}_f{forward:+d}_l{lateral:+d}_t{twist:+d}_s{int(spill)}"


def load_lower_terms():
    if not LOWER_SPIN_JSON.exists():
        return {}
    data = json.loads(LOWER_SPIN_JSON.read_text(encoding="utf-8"))
    out = {}
    for horizon, rows in data.get("viz_records", {}).items():
        out[horizon] = {}
        for row in rows:
            out[horizon][(row["origin"], row["target"])] = {
                "lower_spin_torque": float(row.get("lower_spin_torque", 0.0)),
                "lower_spin_pressure": float(row.get("lower_spin_pressure", 0.0)),
                "topology_arrival": float(row.get("topology_arrival", 0.0)),
                "boundary_gate": float(row.get("boundary_gate", 0.0)),
                "turbulence": float(row.get("turbulence", 0.0)),
                "raw_flow": float(row.get("raw_flow", 0.0)),
            }
    return out


def lower_core_features(row):
    wobble = row["wobble"]
    nino = float(wobble.get("nino_spin", 0.0))
    soi = float(wobble.get("soi_spin", 0.0))
    torsion = float(wobble.get("torsion", 0.0))
    lower_drive = nino - soi
    common = nino + soi
    pressure = abs(nino) + abs(soi)
    imbalance = (abs(nino) - abs(soi)) / max(pressure, EPS)
    gear_mesh = nino * soi
    return np.asarray(
        [
            nino,
            soi,
            lower_drive,
            common,
            pressure,
            imbalance,
            gear_mesh,
            torsion,
            sign(nino),
            sign(soi),
            sign(lower_drive),
            sign(common),
            sign(gear_mesh),
        ],
        dtype=float,
    )


def lower_gate_features(row):
    terms = row.get("lower_terms", {})
    base = list(lower_core_features(row))
    base.extend(
        [
            float(terms.get("lower_spin_torque", 0.0)),
            float(terms.get("lower_spin_pressure", 0.0)),
            float(terms.get("topology_arrival", 0.0)),
            float(terms.get("boundary_gate", 0.0)),
            float(terms.get("turbulence", 0.0)),
            float(terms.get("raw_flow", 0.0)),
            sign(terms.get("lower_spin_torque", 0.0)),
            sign(terms.get("topology_arrival", 0.0)),
            sign(terms.get("raw_flow", 0.0)),
        ]
    )
    return np.asarray(base, dtype=float)


def standardize(candidates, feature_key):
    X = np.asarray([row[feature_key] for row in candidates], dtype=float)
    center = np.median(X, axis=0)
    mad = np.median(np.abs(X - center), axis=0)
    std = np.std(X, axis=0)
    scale = np.maximum(1e-6, np.maximum(1.4826 * mad, 0.25 * std))
    return center, scale


def feature_distance(row, candidate, feature_key, center, scale):
    a = (np.asarray(row[feature_key], dtype=float) - center) / scale
    b = (np.asarray(candidate[feature_key], dtype=float) - center) / scale
    return float(np.sqrt(np.mean((a - b) ** 2)))


def select_lower_displacement(records, row, feature_key, mode_locked):
    candidates = completed_motion_candidates(records, row)
    if len(candidates) < MIN_SELECTOR_TRAIN:
        return None
    center, scale = standardize(candidates, feature_key)
    ranked = sorted(
        [(feature_distance(row, candidate, feature_key, center, scale), candidate) for candidate in candidates],
        key=lambda item: item[0],
    )
    if not mode_locked:
        distance, candidate = ranked[0]
        return {
            "mode": candidate["roll_mode"],
            "mode_weight": None,
            "mode_count": None,
            "candidate_count": int(len(candidates)),
            "best_distance": float(distance),
            "components": candidate["roll_components"],
        }

    nearest = ranked[:NEIGHBOR_COUNT]
    weights = np.asarray([math.exp(-0.5 * (distance / DISTANCE_BANDWIDTH) ** 2) for distance, _ in nearest])
    if float(np.sum(weights)) <= EPS:
        weights = np.ones(len(nearest), dtype=float)
    weights = weights / float(np.sum(weights))
    mode_weights = defaultdict(float)
    for weight, (_, candidate) in zip(weights, nearest):
        mode_weights[candidate["roll_mode"]] += float(weight)
    mode = max(mode_weights.items(), key=lambda item: item[1])[0]
    mode_ranked = [(distance, candidate) for distance, candidate in ranked if candidate["roll_mode"] == mode]
    if not mode_ranked:
        return None
    selected = mode_ranked[:MODE_NEIGHBOR_COUNT]
    selected_dist = np.asarray([distance for distance, _ in selected], dtype=float)
    selected_weights = 1.0 / np.maximum(selected_dist, 1e-6)
    selected_weights = selected_weights / float(np.sum(selected_weights))
    comps = np.asarray([candidate["roll_components"] for _, candidate in selected], dtype=float)
    return {
        "mode": mode,
        "mode_weight": float(mode_weights[mode]),
        "mode_count": int(len(mode_ranked)),
        "candidate_count": int(len(candidates)),
        "best_distance": float(selected_dist[0]),
        "top1_components": comps[0],
        "weighted_components": np.sum(selected_weights[:, None] * comps, axis=0),
    }


def predict_from_components(row, components):
    arrival_vec = rotate_vec(row["surface_vec"], components_to_omega(row["surface_vec"], components))
    arrival_ara = vec_to_ara(arrival_vec)
    terrain = read_fractal_terrain(arrival_ara, row["ara_current"], roll_terms(row))
    force_ara = clamp(terrain["arrival_ara"] + terrain["weighted_slope"] * terrain["force_gain"], 0.0, 2.0)
    return ara_to_value(force_ara), arrival_ara, terrain


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
    lower_terms = load_lower_terms()
    raw_comparison = load_comparison_predictions(RAW_ADDRESS_JSON, ["raw_address_top1"])
    fractal_comparison = load_comparison_predictions(FRACTAL_JSON, ["fractal_phi_force"])
    records_by_h = {}
    point_scores = {key: {} for key in MODEL_KEYS}
    direction_scores = {key: {} for key in MODEL_KEYS}
    amplitude = {key: {} for key in MODEL_KEYS}
    ready_point_scores = {key: {} for key in MODEL_KEYS}
    ready_direction_scores = {key: {} for key in MODEL_KEYS}
    ready_amplitude = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    print("ARA lower-sphere roll selector")
    print("=" * 100)
    print("strict guards: lower-sphere features select completed roll displacement; no future-value decoder")
    print()

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in data["records_by_horizon"][h]]
        for row in records:
            key = (row["origin"], row["target"])
            row["surface_vec"] = row_surface_vec(row)
            row["target_vec"] = row_target_vec(row)
            row["roll_components"] = log_roll_components(row["surface_vec"], row["target_vec"])
            row["roll_mode"] = mode_label(row)
            row["lower_terms"] = lower_terms.get(h, {}).get(key, {})
            row["lower_core_features"] = lower_core_features(row)
            row["lower_gate_features"] = lower_gate_features(row)

        for row in records:
            key = (row["origin"], row["target"])
            row["persistence_pred"] = row["current"]
            row["wobble_surface_analog_pred"] = row["wobble_surface_analog"]
            row["raw_address_top1_pred"] = raw_comparison.get(h, {}).get(key, {}).get(
                "raw_address_top1", row["current"]
            )
            row["fractal_phi_force_pred"] = fractal_comparison.get(h, {}).get(key, {}).get(
                "fractal_phi_force", row["current"]
            )
            selectors = {
                "lower_core_top1": select_lower_displacement(records, row, "lower_core_features", False),
                "lower_core_mode_top1": select_lower_displacement(records, row, "lower_core_features", True),
                "lower_gate_top1": select_lower_displacement(records, row, "lower_gate_features", False),
                "lower_gate_mode_top1": select_lower_displacement(records, row, "lower_gate_features", True),
                "lower_gate_weighted": select_lower_displacement(records, row, "lower_gate_features", True),
            }
            row["lower_ready"] = selectors["lower_gate_mode_top1"] is not None
            row["predicted_lower_mode"] = None
            row["lower_mode_weight"] = None
            row["lower_arrival_ara"] = None
            for name, selector in selectors.items():
                if selector is None:
                    row[f"{name}_pred"] = row["current"]
                    continue
                components = selector.get("components")
                if components is None:
                    components = selector["weighted_components"] if name.endswith("weighted") else selector["top1_components"]
                value, arrival_ara, terrain = predict_from_components(row, components)
                row[f"{name}_pred"] = value
                if name == "lower_gate_mode_top1":
                    row["predicted_lower_mode"] = selector["mode"]
                    row["lower_mode_weight"] = selector.get("mode_weight")
                    row["lower_arrival_ara"] = arrival_ara
                    row["lower_spillover"] = terrain["spillover"]
                    row["lower_force"] = terrain["force"]

        score_keys = {
            "persistence": "persistence_pred",
            "wobble_surface_analog": "wobble_surface_analog_pred",
            "raw_address_top1": "raw_address_top1_pred",
            "fractal_phi_force": "fractal_phi_force_pred",
            "lower_core_top1": "lower_core_top1_pred",
            "lower_core_mode_top1": "lower_core_mode_top1_pred",
            "lower_gate_top1": "lower_gate_top1_pred",
            "lower_gate_mode_top1": "lower_gate_mode_top1_pred",
            "lower_gate_weighted": "lower_gate_weighted_pred",
        }
        ready = [row for row in records if row["lower_ready"]]
        for key, pred_key in score_keys.items():
            point_scores[key][h] = extended_score(point_records(records, pred_key))
            direction_scores[key][h] = direction_score(records, pred_key)
            amplitude[key][h] = amplitude_stats(records, pred_key)
            ready_point_scores[key][h] = extended_score(point_records(ready, pred_key)) if ready else {}
            ready_direction_scores[key][h] = direction_score(ready, pred_key) if ready else {
                "n": 0,
                "accuracy": None,
                "large_accuracy": None,
                "transition_accuracy": None,
            }
            ready_amplitude[key][h] = amplitude_stats(ready, pred_key) if ready else {
                "n": 0,
                "pred_delta_std": None,
                "truth_delta_std": None,
                "std_ratio": None,
                "abs_delta_ratio": None,
            }

        mode_matches = [
            row["predicted_lower_mode"] == row["roll_mode"]
            for row in ready
            if row.get("predicted_lower_mode") is not None
        ]
        diagnostics[h] = {
            "ready_fraction": float(len(ready) / len(records)),
            "mode_accuracy": float(np.mean(mode_matches)) if mode_matches else None,
            "mean_mode_weight": float(np.mean([row["lower_mode_weight"] for row in ready])) if ready else None,
            "mean_arrival_ara": float(np.mean([row["lower_arrival_ara"] for row in ready])) if ready else None,
            "mean_spillover": float(np.mean([row["lower_spillover"] for row in ready])) if ready else None,
        }

        records_by_h[h] = [
            {
                "origin": row["origin"],
                "target": row["target"],
                "current": rounded(row["current"]),
                "actual": rounded(row["actual"]),
                "wobble_surface_analog": rounded(row["wobble_surface_analog_pred"]),
                "raw_address_top1": rounded(row["raw_address_top1_pred"]),
                "fractal_phi_force": rounded(row["fractal_phi_force_pred"]),
                "lower_core_top1": rounded(row["lower_core_top1_pred"]),
                "lower_core_mode_top1": rounded(row["lower_core_mode_top1_pred"]),
                "lower_gate_top1": rounded(row["lower_gate_top1_pred"]),
                "lower_gate_mode_top1": rounded(row["lower_gate_mode_top1_pred"]),
                "lower_gate_weighted": rounded(row["lower_gate_weighted_pred"]),
                "actual_mode": row["roll_mode"],
                "predicted_lower_mode": row["predicted_lower_mode"],
                "lower_mode_weight": rounded(row["lower_mode_weight"]) if row["lower_mode_weight"] is not None else None,
                "lower_arrival_ara": rounded(row["lower_arrival_ara"]) if row["lower_arrival_ara"] is not None else None,
                "lower_spin_torque": rounded(row["lower_terms"].get("lower_spin_torque"))
                if "lower_spin_torque" in row["lower_terms"]
                else None,
                "lower_spin_pressure": rounded(row["lower_terms"].get("lower_spin_pressure"))
                if "lower_spin_pressure" in row["lower_terms"]
                else None,
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
            f"  lower diagnostics        ready={diagnostics[h]['ready_fraction']:.3f}"
            f" mode_acc={diagnostics[h]['mode_accuracy'] if diagnostics[h]['mode_accuracy'] is not None else float('nan'):.3f}"
            f" arrive={diagnostics[h]['mean_arrival_ara'] if diagnostics[h]['mean_arrival_ara'] is not None else float('nan'):.3f}"
        )
        print()

    focus_horizons = [6, 12, 24]
    focus = {
        "point_scores": {key: aggregate_focus(point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "direction_scores": {key: focus_direction(direction_scores[key], focus_horizons) for key in MODEL_KEYS},
        "amplitude": {key: aggregate_focus(amplitude[key], focus_horizons) for key in MODEL_KEYS},
        "ready_point_scores": {key: aggregate_focus(ready_point_scores[key], focus_horizons) for key in MODEL_KEYS},
        "ready_direction_scores": {key: focus_direction(ready_direction_scores[key], focus_horizons) for key in MODEL_KEYS},
        "ready_amplitude": {key: aggregate_focus(ready_amplitude[key], focus_horizons) for key in MODEL_KEYS},
    }

    out = {
        "date": "2026-05-26",
        "method": "strict-causal lower-sphere roll selector",
        "source": "TheFormula/ara_sphere_atlas_data.json",
        "leakage_guard": [
            "Roll mode selection uses only current-origin lower-sphere spin/torque features.",
            "Candidate roll displacements are eligible only when candidate target is before current origin t.",
            "The selected displacement is applied before deterministic fractal terrain reading.",
            "No lag ridge, native-value decoder, future geometry oracle, smoothing, or visual shift is used.",
            "Non-ready rows fall back to persistence.",
        ],
        "selector_rule": {
            "lower_core": "atlas nino_spin, soi_spin, gear/common/pressure/torsion features",
            "lower_gate": "lower_core plus raw lower-spin torque, pressure, topology-arrival, boundary, turbulence, and raw-flow gates",
            "top1": "nearest completed lower-sphere pattern supplies roll displacement directly",
            "mode_top1": "nearest completed lower-sphere patterns vote roll mode, then nearest displacement inside that mode is applied",
            "weighted": "same lower-gate mode selection, but weighted displacement inside the selected mode",
        },
        "horizons_months": HORIZONS,
        "point_scores": clean_for_json(point_scores),
        "direction_scores": clean_for_json(direction_scores),
        "amplitude": clean_for_json(amplitude),
        "ready_point_scores": clean_for_json(ready_point_scores),
        "ready_direction_scores": clean_for_json(ready_direction_scores),
        "ready_amplitude": clean_for_json(ready_amplitude),
        "diagnostics": clean_for_json(diagnostics),
        "focus_6_12_24": clean_for_json(focus),
        "viz_records": clean_for_json(records_by_h),
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_LOWER_SPHERE_ROLL_SELECTOR = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
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
    print("Ready-only focus 6/12/24:")
    for key in MODEL_KEYS:
        ps = focus["ready_point_scores"][key]
        ds = focus["ready_direction_scores"][key]
        amp = focus["ready_amplitude"][key]
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
