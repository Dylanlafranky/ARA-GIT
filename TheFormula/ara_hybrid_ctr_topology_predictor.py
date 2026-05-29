"""
ara_hybrid_ctr_topology_predictor.py

Hybrid predictor: contact_triangle_roll runs first to predict the next NINO
value, then the layered sand topology processes that result to get the next
topological coordinate on the sphere.

Two variants:
  1. FILTERED   — standard K=42 Gaussian-kernel weighted lookup (existing CTR)
  2. UNFILTERED — K=1 nearest neighbor, no averaging, raw analog match

Integration logic:
  - CTR predicts a value at (origin + horizon)
  - That value is converted to an ARA coordinate via value_to_ara()
  - The layered sand cascade computes topology displacement (delta_ara, delta_phase)
    from origin-time spin packets
  - The hybrid arrival coordinate = CTR's ARA base + topology displacement
  - Sphere terrain is read at the combined coordinate
  - Final output = ara_to_value(terrain reading)

This tests whether the contact triangle geometry can steer the topology to a
better arrival point than either system alone.

Strict causality: all inputs are origin-time only. No future data.
Train/holdout: pre-2017 / 2017+.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from ara_fractal_sphere_terrain_reader import ara_to_value, value_to_ara
from ara_geometry_transport_test import clean_for_json, load_enso_frame
from ara_lag_phase_hybrid_predictor import extended_score, format_score, point
from ara_raw_watershed_slice_test import aggregate_focus, rounded
from ara_sphere_orientation_roll_predictor import EPS
from ara_layered_sand_single_formula import (
    FORMULA,
    HOME,
    PHI,
    LAYER_SPECS,
    clamp,
    formula_predict,
    month_anchor,
    propagate_layer,
    raw_spin,
    read_sphere_terrain,
    upper_pressure,
)
from ara_contact_triangle_roll_test import (
    DISTANCE_BANDWIDTH,
    MIN_NEIGHBORS,
    NEIGHBOR_COUNT,
    PAIR_WEIGHTS,
    TRIANGLE_WEIGHTS,
    contact_distance,
    eligible_candidates,
    enrich_records,
    robust_center_scale,
    triangle_geometry,
    contact_roll_level,
)
from ara_sphere_topology_direction_predictor import sign


HERE = Path(__file__).resolve().parent
ATLAS_JSON = HERE / "ara_sphere_atlas_data.json"
LS_RESULT_JSON = HERE / "ara_layered_sand_single_formula_result.json"
LS_FIT_JSON = HERE / "ara_layered_sand_parameter_search_result.json"
OUT_JSON = HERE / "ara_hybrid_ctr_topology_result.json"
OUT_JS = HERE / "ara_hybrid_ctr_topology_result.js"

TRAIN_CUTOFF = "2017-01-01"
HORIZONS = [3, 6, 12, 18, 24]
FOCUS_HORIZONS = [6, 12, 24]


# ---------------------------------------------------------------------------
# CTR: filtered (K=42 Gaussian) and unfiltered (K=1 nearest) lookups
# ---------------------------------------------------------------------------

def ctr_lookup_filtered(records, row, weights, use_triangle=True):
    """Standard K=42 Gaussian kernel weighted lookup (existing CTR)."""
    candidates = eligible_candidates(records, row)
    if len(candidates) < MIN_NEIGHBORS:
        return None

    centers, scales = robust_center_scale(candidates, weights.keys())
    ranked = sorted(
        [(contact_distance(row, c, weights, centers, scales, use_triangle), c)
         for c in candidates],
        key=lambda item: item[0],
    )
    nearest = ranked[:NEIGHBOR_COUNT]
    kernel = np.asarray(
        [math.exp(-0.5 * (dist / DISTANCE_BANDWIDTH) ** 2)
         for dist, _ in nearest],
        dtype=float,
    )
    if float(np.sum(kernel)) <= EPS:
        kernel = np.ones(len(nearest), dtype=float)
    kernel = kernel / float(np.sum(kernel))

    neighbors = [c for _, c in nearest]
    actual = np.asarray([c["actual"] for c in neighbors], dtype=float)
    delta = np.asarray([c["actual"] - c["current"] for c in neighbors], dtype=float)
    directions = np.asarray([sign(c["actual"] - c["current"]) for c in neighbors], dtype=float)
    distances = np.asarray([d for d, _ in nearest], dtype=float)

    direction_vote = float(np.sum(kernel * directions))
    return {
        "level_pred": float(np.sum(kernel * actual)),
        "delta_pred": float(row["current"] + np.sum(kernel * delta)),
        "direction_vote": direction_vote,
        "confidence": abs(direction_vote),
        "neighbor_count": int(len(neighbors)),
        "mean_distance": float(np.sum(kernel * distances)),
        "best_distance": float(nearest[0][0]),
        "variant": "filtered",
    }


def ctr_lookup_unfiltered(records, row, weights, use_triangle=True):
    """K=1 nearest neighbor — no averaging, raw single analog match."""
    candidates = eligible_candidates(records, row)
    if len(candidates) < MIN_NEIGHBORS:
        return None

    centers, scales = robust_center_scale(candidates, weights.keys())
    ranked = sorted(
        [(contact_distance(row, c, weights, centers, scales, use_triangle), c)
         for c in candidates],
        key=lambda item: item[0],
    )
    best_dist, best = ranked[0]
    direction_vote = float(sign(best["actual"] - best["current"]))
    return {
        "level_pred": float(best["actual"]),
        "delta_pred": float(row["current"] + (best["actual"] - best["current"])),
        "direction_vote": direction_vote,
        "confidence": abs(direction_vote),
        "neighbor_count": 1,
        "mean_distance": float(best_dist),
        "best_distance": float(best_dist),
        "variant": "unfiltered",
    }


# ---------------------------------------------------------------------------
# Layered sand topology: compute displacement from origin spins
# ---------------------------------------------------------------------------

def topology_displacement(ls_row, horizon, params):
    """
    Given a layered-sand viz_record (which stores spins and formula diagnostics),
    recompute the cascade displacement (delta_ara, delta_phase) and final state.
    This is the topology's contribution — independent of what value we start from.
    """
    formula = ls_row["formula"]
    spins = formula["spins"]
    upper = formula["upper"]

    # Rebuild cascade state from stored spins
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
    phase_deg = float(ls_row["phase_clock_origin"])
    for i, layer_spin in enumerate(spins[1:], start=1):
        second_spin = spins[max(0, i - 2)]
        state = propagate_layer(state, second_spin, layer_spin, upper, i, params, phase_deg)

    horizon_gain = math.sqrt(max(float(horizon), 1.0) / HOME)
    upper_brake = 1.0 + float(params["upper_pressure"]) * float(params["upper_brake"]) * abs(float(upper["compression"]))
    measured = float(params["measured_roll"]) * horizon_gain / upper_brake
    floor_phase = float(params["floor_drive"]) * (float(horizon) / HOME) * 360.0
    delta_ara = measured * float(params["roll_to_ara"]) * (float(state["forward"]) + 0.18 * float(state["lateral"]))
    delta_phase = floor_phase + measured * float(params["roll_to_phase"]) * (
        float(state["lateral"]) + 0.45 * float(state["twist"]) + 0.18 * float(state["forward"])
    )
    return {
        "state": state,
        "upper": upper,
        "delta_ara": float(delta_ara),
        "delta_phase": float(delta_phase),
        "phase_deg": float(phase_deg),
    }


def hybrid_predict(ctr_value, topo, ls_row, params):
    """
    Combine CTR's predicted value with the topology's displacement.

    1. Convert CTR value to ARA coordinate
    2. Add topology displacement
    3. Read terrain at the combined coordinate
    4. Convert back to value
    """
    ctr_ara = value_to_ara(ctr_value)
    arrival_ara = clamp(ctr_ara + topo["delta_ara"], 0.0, 2.0)
    arrival_phase = (topo["phase_deg"] + topo["delta_phase"]) % 360.0

    terrain = read_sphere_terrain(
        arrival_ara,
        ctr_ara,  # use CTR's position as "current" for terrain reading
        arrival_phase,
        float(topo["state"]["pressure"]),
        float(topo["state"]["forward"]),
        float(topo["upper"]["compression"]),
        params,
    )
    return {
        "value": float(ara_to_value(terrain["force_ara"])),
        "ctr_value": float(ctr_value),
        "ctr_ara": float(ctr_ara),
        "arrival_ara": float(arrival_ara),
        "arrival_phase": float(arrival_phase),
        "delta_ara": float(topo["delta_ara"]),
        "delta_phase": float(topo["delta_phase"]),
        "terrain_force_ara": float(terrain["force_ara"]),
        "terrain_slope": float(terrain["combined_slope"]),
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def corr(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if len(xs) < 3 or np.std(xs) <= EPS or np.std(ys) <= EPS:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def score_split(rows, key):
    usable = [r for r in rows if r.get(key) is not None]
    if not usable:
        return {"n": 0, "mae": None, "corr": None, "direction": None}
    pred = np.asarray([r[key] for r in usable], dtype=float)
    actual = np.asarray([r["actual"] for r in usable], dtype=float)
    current = np.asarray([r["current"] for r in usable], dtype=float)
    truth_delta = actual - current
    pred_delta = pred - current
    turn_mask = np.abs(truth_delta) > EPS
    return {
        "n": int(len(usable)),
        "mae": float(np.mean(np.abs(pred - actual))),
        "corr": corr(pred, actual),
        "direction": float(np.mean(np.sign(pred_delta[turn_mask]) == np.sign(truth_delta[turn_mask])))
        if np.any(turn_mask) else None,
    }


MODEL_KEYS = [
    "persistence",
    "formula_standalone",
    "ctr_filtered",
    "ctr_unfiltered",
    "ctr_roll_filtered",
    "ctr_roll_unfiltered",
    "hybrid_filtered",
    "hybrid_unfiltered",
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    # Load data
    atlas = json.loads(ATLAS_JSON.read_text(encoding="utf-8"))
    ls_data = json.loads(LS_RESULT_JSON.read_text(encoding="utf-8"))
    ls_fit = json.loads(LS_FIT_JSON.read_text(encoding="utf-8"))
    params = ls_fit["best_params"]

    # Build lookup from layered sand results keyed by (horizon, origin)
    ls_lookup = {}
    for h_str, rows in ls_data["viz_records"].items():
        for row in rows:
            ls_lookup[(h_str, row["origin"])] = row

    print("ARA Hybrid Predictor: contact_triangle_roll → layered sand topology")
    print("=" * 100)
    print("CTR runs first (filtered K=42, unfiltered K=1), then topology processes the result")
    print(f"Train cutoff: {TRAIN_CUTOFF}")
    print()

    all_records = []
    point_scores_train = {k: {} for k in MODEL_KEYS}
    point_scores_holdout = {k: {} for k in MODEL_KEYS}
    point_scores_all = {k: {} for k in MODEL_KEYS}
    viz_records = {}

    for horizon in HORIZONS:
        h = str(horizon)
        records = [dict(row) for row in atlas["records_by_horizon"][h]]

        # Enrich with contact triangle geometry
        records = enrich_records(records)

        # Process each record
        for row in records:
            row["persistence"] = row["current"]

            # Get layered sand result for this (horizon, origin)
            ls_row = ls_lookup.get((h, row["origin"]))
            row["formula_standalone"] = float(ls_row["Formula"]) if ls_row else row["current"]

            # CTR filtered (K=42 Gaussian)
            pred_filt = ctr_lookup_filtered(records, row, TRIANGLE_WEIGHTS, use_triangle=True)
            if pred_filt is not None:
                row["ctr_filtered"] = pred_filt["level_pred"]
                row["ctr_roll_filtered"] = contact_roll_level(row, pred_filt)
                row["ctr_filt_meta"] = pred_filt
            else:
                row["ctr_filtered"] = row["current"]
                row["ctr_roll_filtered"] = row["current"]
                row["ctr_filt_meta"] = None

            # CTR unfiltered (K=1 nearest)
            pred_unfilt = ctr_lookup_unfiltered(records, row, TRIANGLE_WEIGHTS, use_triangle=True)
            if pred_unfilt is not None:
                row["ctr_unfiltered"] = pred_unfilt["level_pred"]
                row["ctr_roll_unfiltered"] = contact_roll_level(row, pred_unfilt)
                row["ctr_unfilt_meta"] = pred_unfilt
            else:
                row["ctr_unfiltered"] = row["current"]
                row["ctr_roll_unfiltered"] = row["current"]
                row["ctr_unfilt_meta"] = None

            # Hybrid: CTR → topology
            if ls_row is not None:
                topo = topology_displacement(ls_row, horizon, params)

                # Filtered hybrid: use CTR filtered prediction as base
                if pred_filt is not None:
                    h_filt = hybrid_predict(row["ctr_roll_filtered"], topo, ls_row, params)
                    row["hybrid_filtered"] = h_filt["value"]
                    row["hybrid_filt_meta"] = h_filt
                else:
                    row["hybrid_filtered"] = row["formula_standalone"]
                    row["hybrid_filt_meta"] = None

                # Unfiltered hybrid: use CTR unfiltered prediction as base
                if pred_unfilt is not None:
                    h_unfilt = hybrid_predict(row["ctr_roll_unfiltered"], topo, ls_row, params)
                    row["hybrid_unfiltered"] = h_unfilt["value"]
                    row["hybrid_unfilt_meta"] = h_unfilt
                else:
                    row["hybrid_unfiltered"] = row["formula_standalone"]
                    row["hybrid_unfilt_meta"] = None
            else:
                row["hybrid_filtered"] = row["current"]
                row["hybrid_unfiltered"] = row["current"]
                row["hybrid_filt_meta"] = None
                row["hybrid_unfilt_meta"] = None

        # Split train/holdout
        train = [r for r in records if r["origin"] < TRAIN_CUTOFF]
        holdout = [r for r in records if r["origin"] >= TRAIN_CUTOFF]

        for key in MODEL_KEYS:
            point_scores_train[key][h] = score_split(train, key)
            point_scores_holdout[key][h] = score_split(holdout, key)
            point_scores_all[key][h] = score_split(records, key)

        # Print results
        print(f"h={horizon:>2} months  (train={len(train)}, holdout={len(holdout)})")
        print(f"  {'Model':30s} {'Train MAE':>10s} {'Train corr':>11s} {'Hold MAE':>10s} {'Hold corr':>11s} {'Hold dir':>10s}")
        for key in MODEL_KEYS:
            t = point_scores_train[key][h]
            ho = point_scores_holdout[key][h]
            t_mae = f"{t['mae']:.3f}" if t['mae'] is not None else "   —"
            t_corr = f"{t['corr']:+.3f}" if t['corr'] is not None else "    —"
            h_mae = f"{ho['mae']:.3f}" if ho['mae'] is not None else "   —"
            h_corr = f"{ho['corr']:+.3f}" if ho['corr'] is not None else "    —"
            h_dir = f"{ho['direction']:.3f}" if ho['direction'] is not None else "   —"
            print(f"  {key:30s} {t_mae:>10s} {t_corr:>11s} {h_mae:>10s} {h_corr:>11s} {h_dir:>10s}")
        print()

        # Save viz records
        viz_records[h] = [
            {
                "origin": r["origin"],
                "target": r["target"],
                "current": rounded(r["current"]),
                "actual": rounded(r["actual"]),
                "persistence": rounded(r["persistence"]),
                "formula_standalone": rounded(r["formula_standalone"]),
                "ctr_filtered": rounded(r["ctr_filtered"]),
                "ctr_unfiltered": rounded(r["ctr_unfiltered"]),
                "ctr_roll_filtered": rounded(r.get("ctr_roll_filtered", r["current"])),
                "ctr_roll_unfiltered": rounded(r.get("ctr_roll_unfiltered", r["current"])),
                "hybrid_filtered": rounded(r["hybrid_filtered"]),
                "hybrid_unfiltered": rounded(r["hybrid_unfiltered"]),
            }
            for r in records
        ]
        all_records.extend(records)

    # Focus 6/12/24 aggregation
    focus_train = {key: aggregate_focus(point_scores_train[key], FOCUS_HORIZONS) for key in MODEL_KEYS}
    focus_holdout = {key: aggregate_focus(point_scores_holdout[key], FOCUS_HORIZONS) for key in MODEL_KEYS}
    focus_all = {key: aggregate_focus(point_scores_all[key], FOCUS_HORIZONS) for key in MODEL_KEYS}

    print("=" * 100)
    print("FOCUS 6/12/24 — HOLDOUT (2017+)")
    print(f"  {'Model':30s} {'MAE':>10s} {'corr':>11s} {'direction':>10s}")
    for key in MODEL_KEYS:
        f = focus_holdout[key]
        mae = f"{f.get('mae', 0):.3f}" if f.get('mae') is not None else "   —"
        c = f"{f.get('corr', 0):+.3f}" if f.get('corr') is not None else "    —"
        d = f"{f.get('direction', 0):.3f}" if f.get('direction') is not None else "   —"
        print(f"  {key:30s} {mae:>10s} {c:>11s} {d:>10s}")

    print()
    print("FOCUS 6/12/24 — TRAIN (pre-2017)")
    print(f"  {'Model':30s} {'MAE':>10s} {'corr':>11s} {'direction':>10s}")
    for key in MODEL_KEYS:
        f = focus_train[key]
        mae = f"{f.get('mae', 0):.3f}" if f.get('mae') is not None else "   —"
        c = f"{f.get('corr', 0):+.3f}" if f.get('corr') is not None else "    —"
        d = f"{f.get('direction', 0):.3f}" if f.get('direction') is not None else "   —"
        print(f"  {key:30s} {mae:>10s} {c:>11s} {d:>10s}")

    # Save results
    out = {
        "date": "2026-05-27",
        "method": "hybrid: contact_triangle_roll → layered sand topology",
        "description": "CTR predicts next value, topology maps it to sphere coordinate",
        "variants": {
            "filtered": "K=42 Gaussian kernel CTR (standard) → topology displacement",
            "unfiltered": "K=1 nearest neighbor CTR (no averaging) → topology displacement",
        },
        "leakage_guard": [
            "CTR uses only origin-time contact geometry features",
            "Analog neighbors require s+h < t (strict temporal causality)",
            "Topology displacement uses origin-time spin packets only",
            "No future data, decoder, or lag ridge",
        ],
        "train_cutoff": TRAIN_CUTOFF,
        "horizons_months": HORIZONS,
        "ctr_params": {
            "filtered_neighbors": NEIGHBOR_COUNT,
            "unfiltered_neighbors": 1,
            "bandwidth": DISTANCE_BANDWIDTH,
            "min_candidates": MIN_NEIGHBORS,
        },
        "topology_params": "layered_sand_parameter_search best_params (fitted on pre-2017)",
        "point_scores_train": clean_for_json(point_scores_train),
        "point_scores_holdout": clean_for_json(point_scores_holdout),
        "point_scores_all": clean_for_json(point_scores_all),
        "focus_6_12_24": {
            "train": clean_for_json(focus_train),
            "holdout": clean_for_json(focus_holdout),
            "all": clean_for_json(focus_all),
        },
        "viz_records": clean_for_json(viz_records),
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_HYBRID_CTR_TOPOLOGY = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print(f"\nSaved → {OUT_JSON}")
    print(f"Saved → {OUT_JS}")


if __name__ == "__main__":
    run()
