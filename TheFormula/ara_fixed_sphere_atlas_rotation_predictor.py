"""
ara_fixed_sphere_atlas_rotation_predictor.py

Closed, fixed-atlas test for the sphere-terrain idea.

This is intentionally different from the earlier "formula draws the future
origin" workbench. The rule here is:

    current/cutoff pose
    -> rotate/wobble to a future sphere address
    -> read the fixed atlas terrain at that address
    -> compare afterward

No model in this file reads a future origin row, a future target row, or the
truth value for the row being predicted. The atlas is filtered to samples whose
terrain date is already known at prediction time.

Important limitation:
    The existing sphere atlas is a historical point-cloud terrain map, not a
    dense recursive globe. "Read terrain" therefore means top-1 raw nearest
    known past atlas address. There is no averaging in the primary predictors.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from ara_fractal_sphere_terrain_reader import value_to_ara
from ara_geometry_transport_test import clean_for_json, load_enso_frame
from ara_layered_sand_closed_cutoff_run import (
    MANUAL_SCREENSHOT_PARAMS,
    WAVECYCLE_SCREENSHOT_PARAMS,
    phase_clock,
)
from ara_layered_sand_single_formula import FORMULA, formula_predict
from ara_raw_watershed_slice_test import rounded
from ara_sphere_orientation_roll_predictor import EPS, sign


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_sphere_atlas_data.json"
OUT_JSON = HERE / "ara_fixed_sphere_atlas_rotation_result.json"
OUT_JS = HERE / "ara_fixed_sphere_atlas_rotation_result.js"

CUTOFFS = ["2010-01-01", "2015-01-01", "2017-01-01", "2020-01-01"]
PRIMARY_HORIZONS = [3, 6, 12, 18, 24]
HOME = 47.0
WOBBLE_AMOUNT = 0.18

MODEL_KEYS = [
    "persistence",
    "atlas_clock_flat_top1",
    "atlas_clock_wobble_top1",
    "atlas_formula_pose_top1",
    "atlas_manual_pose_top1",
    "atlas_wavecycle_pose_top1",
]

POSE_LABELS = {
    "atlas_clock_flat_top1": "Clock rotation, flat atlas",
    "atlas_clock_wobble_top1": "Clock rotation, wobble atlas",
    "atlas_formula_pose_top1": "Formula pose -> atlas read",
    "atlas_manual_pose_top1": "Manual pose -> atlas read",
    "atlas_wavecycle_pose_top1": "Wavecycle pose -> atlas read",
}


def month_index(date_str):
    date = datetime.strptime(str(date_str)[:10], "%Y-%m-%d")
    return date.year * 12 + date.month - 1


def add_months(date, months):
    return pd.Timestamp(date) + pd.DateOffset(months=int(months))


def month_delta(start, end):
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    return (end.year - start.year) * 12 + (end.month - start.month)


def clamp(value, lo, hi):
    return float(max(lo, min(hi, float(value))))


def ara_y(ara):
    return 1.0 - clamp(ara, 0.0, 2.0)


def norm(vec):
    arr = np.asarray(vec, dtype=float)
    length = float(np.linalg.norm(arr))
    if length <= EPS:
        return arr
    return arr / length


def point3(ara, phase_deg, wobble=None, amount=WOBBLE_AMOUNT):
    """Match the visual atlas point projection without drawing it."""
    lon = math.radians(float(phase_deg) % 360.0)
    y = ara_y(ara)
    ring = math.sqrt(max(0.0, 1.0 - y * y))
    base = np.asarray([ring * math.cos(lon), y, ring * math.sin(lon)], dtype=float)
    if not wobble or amount <= 0.0:
        return base

    normal = norm(base)
    east = np.asarray([-math.sin(lon), 0.0, math.cos(lon)], dtype=float)
    north = norm(np.asarray([-y * math.cos(lon), ring, -y * math.sin(lon)], dtype=float))
    torsion = float(wobble.get("torsion") or 0.0)
    lateral = float(wobble.get("x") or 0.0) + 0.18 * torsion
    bank = float(wobble.get("y") or 0.0)
    lift = float(wobble.get("z") or 0.0)
    return base + amount * (east * lateral + north * bank + normal * lift)


def corr(xs, ys):
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if len(xs) < 3 or np.std(xs) <= EPS or np.std(ys) <= EPS:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def score(rows, key, current_key="current"):
    usable = [row for row in rows if row.get(key) is not None and np.isfinite(row.get(key))]
    if not usable:
        return {"n": 0, "mae": None, "corr": None, "direction": None, "amp_ratio": None, "corr_with_current": None}
    pred = np.asarray([row[key] for row in usable], dtype=float)
    actual = np.asarray([row["actual"] for row in usable], dtype=float)
    current = np.asarray([row[current_key] for row in usable], dtype=float)
    truth_delta = actual - current
    pred_delta = pred - current
    mask = np.abs(truth_delta) > EPS
    return {
        "n": int(len(usable)),
        "mae": float(np.mean(np.abs(pred - actual))),
        "corr": corr(pred, actual),
        "direction": float(np.mean(np.sign(pred_delta[mask]) == np.sign(truth_delta[mask]))) if np.any(mask) else None,
        "amp_ratio": float(np.std(pred_delta) / np.std(truth_delta)) if np.std(truth_delta) > EPS else None,
        "corr_with_current": corr(pred, current),
    }


def make_sample(record, use_wobble=True):
    """A raw, observed terrain address from the existing atlas."""
    phase = float(record["phase_clock_origin"])
    wobble = record.get("wobble") if use_wobble else None
    return {
        "date": record["origin"],
        "month": month_index(record["origin"]),
        "value": float(record["current"]),
        "ara": float(record["ara_current"]),
        "phase": phase,
        "coord": point3(record["ara_current"], phase, wobble=wobble),
        "source": "observed_current_atlas_point",
    }


def build_fixed_samples(atlas, use_wobble=True):
    # All horizons repeat the same origin dates. Use the 3-month records as the
    # canonical visited terrain points to avoid duplicate weighting.
    samples = {}
    for record in atlas["records_by_horizon"]["3"]:
        samples[record["origin"]] = make_sample(record, use_wobble=use_wobble)
    return [samples[key] for key in sorted(samples)]


def read_top1(samples, query_coord, max_month):
    past = [sample for sample in samples if sample["month"] <= max_month]
    if not past:
        return None
    q = np.asarray(query_coord, dtype=float)
    distances = [float(np.linalg.norm(q - sample["coord"])) for sample in past]
    idx = int(np.argmin(distances))
    sample = past[idx]
    return {
        "value": float(sample["value"]),
        "distance": float(distances[idx]),
        "date": sample["date"],
        "ara": float(sample["ara"]),
        "phase": float(sample["phase"]),
    }


def formula_pose(frame, row, horizon, params):
    out = formula_predict(frame, row, horizon, params)
    return {
        "ara": float(out["arrival_ara"]),
        "phase": float(out["arrival_phase"]),
        "delta_ara": float(out["delta_ara"]),
        "delta_phase": float(out["delta_phase"]),
    }


def clock_pose(row, horizon):
    return {
        "ara": float(row["ara_current"]),
        "phase": (float(row["phase_clock_origin"]) + (float(horizon) / HOME) * 360.0) % 360.0,
        "delta_ara": 0.0,
        "delta_phase": (float(horizon) / HOME) * 360.0,
    }


def apply_pose_read(row, samples, pose, use_wobble, max_month):
    query = point3(pose["ara"], pose["phase"], wobble=row.get("wobble") if use_wobble else None)
    found = read_top1(samples, query, max_month=max_month)
    if not found:
        return None
    return {
        "prediction": found["value"],
        "lookup": found,
        "pose": pose,
    }


def rolling_predictions(atlas, frame):
    flat_samples = build_fixed_samples(atlas, use_wobble=False)
    wobble_samples = build_fixed_samples(atlas, use_wobble=True)
    records_by_h = {}
    scores = {key: {} for key in MODEL_KEYS}
    diagnostics = {}

    for horizon in PRIMARY_HORIZONS:
        hkey = str(horizon)
        out_rows = []
        for source in atlas["records_by_horizon"][hkey]:
            row = dict(source)
            origin_month = month_index(row["origin"])
            row["persistence"] = float(row["current"])

            poses = {
                "atlas_clock_flat_top1": clock_pose(row, horizon),
                "atlas_clock_wobble_top1": clock_pose(row, horizon),
                "atlas_formula_pose_top1": formula_pose(frame, row, horizon, FORMULA),
                "atlas_manual_pose_top1": formula_pose(frame, row, horizon, MANUAL_SCREENSHOT_PARAMS),
                "atlas_wavecycle_pose_top1": formula_pose(frame, row, horizon, WAVECYCLE_SCREENSHOT_PARAMS),
            }
            reads = {
                "atlas_clock_flat_top1": apply_pose_read(row, flat_samples, poses["atlas_clock_flat_top1"], False, origin_month),
                "atlas_clock_wobble_top1": apply_pose_read(row, wobble_samples, poses["atlas_clock_wobble_top1"], True, origin_month),
                "atlas_formula_pose_top1": apply_pose_read(row, wobble_samples, poses["atlas_formula_pose_top1"], True, origin_month),
                "atlas_manual_pose_top1": apply_pose_read(row, wobble_samples, poses["atlas_manual_pose_top1"], True, origin_month),
                "atlas_wavecycle_pose_top1": apply_pose_read(row, wobble_samples, poses["atlas_wavecycle_pose_top1"], True, origin_month),
            }
            for key, read in reads.items():
                row[key] = float(read["prediction"]) if read else None
                row[f"{key}_lookup"] = read["lookup"] if read else None
                row[f"{key}_pose"] = read["pose"] if read else poses[key]

            out_rows.append(
                {
                    "origin": row["origin"],
                    "target": row["target"],
                    "horizon": int(horizon),
                    "current": rounded(row["current"]),
                    "actual": rounded(row["actual"]),
                    "persistence": rounded(row["persistence"]),
                    **{key: rounded(row[key]) if row[key] is not None else None for key in MODEL_KEYS if key != "persistence"},
                    "lookups": clean_for_json(
                        {
                            key: row.get(f"{key}_lookup")
                            for key in MODEL_KEYS
                            if key != "persistence"
                        }
                    ),
                    "poses": clean_for_json(
                        {
                            key: row.get(f"{key}_pose")
                            for key in MODEL_KEYS
                            if key != "persistence"
                        }
                    ),
                }
            )

        records_by_h[hkey] = out_rows
        for key in MODEL_KEYS:
            scores[key][hkey] = score(out_rows, key)
        diagnostics[hkey] = {
            "mean_lookup_distance": {
                key: float(
                    np.mean(
                        [
                            row["lookups"][key]["distance"]
                            for row in out_rows
                            if row["lookups"].get(key)
                        ]
                    )
                )
                for key in MODEL_KEYS
                if key != "persistence"
            },
            "mean_abs_delta_ara": {
                key: float(
                    np.mean(
                        [
                            abs(row["poses"][key].get("delta_ara", 0.0))
                            for row in out_rows
                            if row["poses"].get(key)
                        ]
                    )
                )
                for key in MODEL_KEYS
                if key != "persistence"
            },
            "mean_abs_delta_phase": {
                key: float(
                    np.mean(
                        [
                            abs(row["poses"][key].get("delta_phase", 0.0))
                            for row in out_rows
                            if row["poses"].get(key)
                        ]
                    )
                )
                for key in MODEL_KEYS
                if key != "persistence"
            },
        }

    return {"records_by_horizon": records_by_h, "scores": scores, "diagnostics": diagnostics}


def make_cutoff_seed(frame, cutoff_date):
    value = float(frame.loc[pd.Timestamp(cutoff_date), "NINO"])
    return {
        "origin": cutoff_date,
        "target": cutoff_date,
        "current": value,
        "actual": value,
        "ara_current": value_to_ara(value),
        "phase_clock_origin": phase_clock(cutoff_date),
        "wobble": None,
    }


def cutoff_predictions(atlas, frame):
    flat_samples = build_fixed_samples(atlas, use_wobble=False)
    wobble_samples = build_fixed_samples(atlas, use_wobble=True)
    out = {}

    for cutoff in CUTOFFS:
        cutoff_ts = pd.Timestamp(cutoff)
        seed = make_cutoff_seed(frame, cutoff)
        cutoff_month = month_index(cutoff)
        cutoff_value = float(seed["current"])
        rows = []
        end = min(pd.Timestamp("2025-12-01"), frame.index.max())
        lead = 1
        while cutoff_ts + pd.DateOffset(months=lead) <= end:
            target = cutoff_ts + pd.DateOffset(months=lead)
            actual = float(frame.loc[target, "NINO"])
            row = dict(seed)
            row["target"] = target.strftime("%Y-%m-%d")
            row["actual"] = actual
            row["persistence"] = cutoff_value
            row["lead_month"] = int(lead)

            poses = {
                "atlas_clock_flat_top1": clock_pose(seed, lead),
                "atlas_clock_wobble_top1": clock_pose(seed, lead),
                "atlas_formula_pose_top1": formula_pose(frame, seed, lead, FORMULA),
                "atlas_manual_pose_top1": formula_pose(frame, seed, lead, MANUAL_SCREENSHOT_PARAMS),
                "atlas_wavecycle_pose_top1": formula_pose(frame, seed, lead, WAVECYCLE_SCREENSHOT_PARAMS),
            }
            reads = {
                "atlas_clock_flat_top1": apply_pose_read(seed, flat_samples, poses["atlas_clock_flat_top1"], False, cutoff_month),
                "atlas_clock_wobble_top1": apply_pose_read(seed, wobble_samples, poses["atlas_clock_wobble_top1"], True, cutoff_month),
                "atlas_formula_pose_top1": apply_pose_read(seed, wobble_samples, poses["atlas_formula_pose_top1"], True, cutoff_month),
                "atlas_manual_pose_top1": apply_pose_read(seed, wobble_samples, poses["atlas_manual_pose_top1"], True, cutoff_month),
                "atlas_wavecycle_pose_top1": apply_pose_read(seed, wobble_samples, poses["atlas_wavecycle_pose_top1"], True, cutoff_month),
            }
            for key, read in reads.items():
                row[key] = float(read["prediction"]) if read else None
                row[f"{key}_lookup"] = read["lookup"] if read else None
                row[f"{key}_pose"] = read["pose"] if read else poses[key]
            rows.append(
                {
                    "date": row["target"],
                    "lead_month": int(lead),
                    "current": rounded(cutoff_value),
                    "actual": rounded(actual),
                    "persistence": rounded(row["persistence"]),
                    **{key: rounded(row[key]) if row[key] is not None else None for key in MODEL_KEYS if key != "persistence"},
                    "lookups": clean_for_json({key: row.get(f"{key}_lookup") for key in MODEL_KEYS if key != "persistence"}),
                    "poses": clean_for_json({key: row.get(f"{key}_pose") for key in MODEL_KEYS if key != "persistence"}),
                }
            )
            lead += 1

        windows = {
            "lead_1_12": [row for row in rows if 1 <= row["lead_month"] <= 12],
            "lead_13_36": [row for row in rows if 13 <= row["lead_month"] <= 36],
            "lead_37_plus": [row for row in rows if row["lead_month"] >= 37],
            "all": rows,
        }
        out[cutoff] = {
            "records": rows,
            "scores": {
                window: {key: score(window_rows, key) for key in MODEL_KEYS}
                for window, window_rows in windows.items()
            },
        }

    return out


def print_summary(result):
    print("ARA fixed sphere atlas rotation predictor")
    print("=" * 100)
    print("Primary predictors rotate to a future coordinate and perform top-1 raw past-atlas lookup.")
    print("No future-origin/current rows are used inside the predictors.")
    print()
    print("Rolling-origin focus:")
    for horizon in PRIMARY_HORIZONS:
        hkey = str(horizon)
        line = [f"h={horizon:>2}m"]
        for key in MODEL_KEYS:
            sc = result["rolling"]["scores"][key][hkey]
            line.append(f"{key}: corr={rounded(sc['corr']) if sc['corr'] is not None else 'n/a'} mae={rounded(sc['mae'])}")
        print(" | ".join(line))
    print()
    print("Closed cutoff all-window:")
    for cutoff, block in result["closed_cutoffs"].items():
        line = [cutoff]
        for key in MODEL_KEYS:
            sc = block["scores"]["all"][key]
            line.append(f"{key}: corr={rounded(sc['corr']) if sc['corr'] is not None else 'n/a'} mae={rounded(sc['mae'])}")
        print(" | ".join(line))


def run():
    atlas = json.loads(IN_JSON.read_text(encoding="utf-8"))
    frame = load_enso_frame()
    result = {
        "date": "2026-05-26",
        "method": "Fixed sphere atlas rotation reader",
        "source_atlas": str(IN_JSON.name),
        "home_period_months": HOME,
        "leakage_rules": [
            "Atlas samples are filtered to terrain dates <= prediction origin or cutoff.",
            "Primary atlas reads are top-1 raw nearest address, not averaged neighbours.",
            "The predictor may use current observed state at the prediction origin, but never a future origin row.",
            "Closed cutoff paths use one cutoff pose and a fixed pre-cutoff atlas.",
        ],
        "atlas_limitation": (
            "The existing sphere atlas is a historical point-cloud, not a dense recursive terrain globe. "
            "This test reads the nearest known past terrain point after rotation."
        ),
        "model_labels": POSE_LABELS,
        "rolling": rolling_predictions(atlas, frame),
        "closed_cutoffs": cutoff_predictions(atlas, frame),
    }
    OUT_JSON.write_text(json.dumps(clean_for_json(result), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_FIXED_SPHERE_ATLAS_ROTATION = " + json.dumps(clean_for_json(result), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print_summary(result)
    print()
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
