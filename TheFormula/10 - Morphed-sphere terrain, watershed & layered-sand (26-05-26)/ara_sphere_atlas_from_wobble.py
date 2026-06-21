"""
ara_sphere_atlas_from_wobble.py

Build a full-sphere ARA atlas from the strict-causal wobble terrain records.

This is a mapping/export script, not a predictor. It converts the held-out ENSO
water-slice records into spherical coordinates:

    ARA latitude: 0..2 mapped from raw NINO state
    longitude:   selectable phase/degrees view
    wobble:      local 3-axis tangent/radial displacement on the sphere

The output is used by ara_sphere_atlas_viz.html.
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from pathlib import Path

from ara_geometry_transport_test import HOME_PERIOD, clean_for_json
from ara_raw_watershed_slice_test import rounded
from ara_shape_kernel_test import PHI


HERE = Path(__file__).resolve().parent
IN_JSON = HERE / "ara_wobble_terrain_arrival_result.json"
OUT_JSON = HERE / "ara_sphere_atlas_data.json"
OUT_JS = HERE / "ara_sphere_atlas_data.js"

SQUASH_SCALE = 1.5


def month_index(date_str):
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.year * 12 + date.month - 1


def deg(rad):
    return (math.degrees(rad) + 360.0) % 360.0


def value_to_ara(value):
    return max(0.0, min(2.0, 1.0 + math.tanh(float(value) / SQUASH_SCALE)))


def wrap_deg(value):
    return float(value % 360.0)


def build_record(row, sample_start_month):
    origin_month = month_index(row["origin"])
    target_month = month_index(row["target"])
    clock_origin = wrap_deg(((origin_month - sample_start_month) / HOME_PERIOD) * 360.0)
    clock_target = wrap_deg(((target_month - sample_start_month) / HOME_PERIOD) * 360.0)
    horizon_offset = wrap_deg((float(row["horizon"]) / HOME_PERIOD) * 360.0) if "horizon" in row else wrap_deg(clock_target - clock_origin)

    x = float(row["x"])
    y = float(row["y"])
    z = float(row["z"])
    xv = float(row["x_v3"])
    yv = float(row["y_v3"])
    zv = float(row["z_v3"])
    torsion = float(row["torsion"])
    nino_spin = float(row["nino_spin"])
    soi_spin = float(row["soi_spin"])

    wobble_phase = deg(math.atan2(z, x))
    flow_phase = deg(math.atan2(xv, x if abs(x) > 1e-9 else 1e-9))
    torsion_phase = deg(math.atan2(torsion, nino_spin if abs(nino_spin) > 1e-9 else 1e-9))

    return {
        "id": f"h{row['horizon']}_{row['origin']}",
        "horizon": int(row["horizon"]),
        "origin": row["origin"],
        "target": row["target"],
        "current": float(row["current"]),
        "actual": float(row["actual"]),
        "persistence": float(row["persistence"]),
        "terrain_level_analog": float(row["terrain_level_analog"]),
        "wobble_level_analog": float(row["wobble_level_analog"]),
        "wobble_delta_analog": float(row["wobble_delta_analog"]),
        "wobble_surface_analog": float(row["wobble_surface_analog"]),
        "ara_current": value_to_ara(row["current"]),
        "ara_actual": value_to_ara(row["actual"]),
        "ara_terrain_level": value_to_ara(row["terrain_level_analog"]),
        "ara_wobble_level": value_to_ara(row["wobble_level_analog"]),
        "ara_wobble_surface": value_to_ara(row["wobble_surface_analog"]),
        "phase_clock_origin": clock_origin,
        "phase_clock_target": clock_target,
        "phase_wobble_origin": wobble_phase,
        "phase_flow_origin": flow_phase,
        "phase_torsion_origin": torsion_phase,
        "phase_horizon_offset": horizon_offset,
        "wobble": {
            "x": x,
            "y": y,
            "z": z,
            "x_v3": xv,
            "y_v3": yv,
            "z_v3": zv,
            "torsion": torsion,
            "nino_spin": nino_spin,
            "soi_spin": soi_spin,
            "mean_distance": row.get("wobble_mean_distance"),
            "orientation_match": row.get("wobble_orientation_match"),
        },
        "error": {
            "wobble_surface": float(row["wobble_surface_analog"]) - float(row["actual"]),
            "terrain_level": float(row["terrain_level_analog"]) - float(row["actual"]),
            "persistence": float(row["persistence"]) - float(row["actual"]),
        },
    }


def run():
    data = json.loads(IN_JSON.read_text(encoding="utf-8"))
    sample_start_month = month_index(data["sample"]["start"])
    records_by_horizon = {}
    for horizon, rows in data["viz_records"].items():
        records_by_horizon[horizon] = [build_record({**row, "horizon": int(horizon)}, sample_start_month) for row in rows]

    out = {
        "date": "2026-05-25",
        "method": "ARA full-sphere atlas from wobble terrain records",
        "source": "TheFormula/ara_wobble_terrain_arrival_result.json",
        "home_period_months": HOME_PERIOD,
        "phi": PHI,
        "ara_mapping": {
            "latitude": "ARA 0..2 maps pole-to-pole: y = 1 - ARA",
            "longitude_modes": {
                "clock": "home-cycle phase in degrees using the 47-month ENSO home period",
                "wobble": "atan2(local z tilt, local x tilt)",
                "flow": "atan2(3-month x wobble velocity, x tilt)",
                "torsion": "atan2(local torsion, lower NINO spin)",
            },
            "value_to_ara": "1 + tanh(value / 1.5), clamped to 0..2",
        },
        "ara_bands": [
            {"name": "space_pole", "label": "ARA 0", "value": 0.0, "kind": "pole"},
            {"name": "anti_phi", "label": "2-phi", "value": 2.0 - PHI, "kind": "mirror"},
            {"name": "quarter", "label": "0.5", "value": 0.5, "kind": "quarter"},
            {"name": "balance", "label": "1.0", "value": 1.0, "kind": "balance"},
            {"name": "phi", "label": "phi", "value": PHI, "kind": "phi"},
            {"name": "time_pole", "label": "ARA 2", "value": 2.0, "kind": "pole"},
        ],
        "horizons_months": data["horizons_months"],
        "point_scores": data["point_scores"],
        "focus_6_12_24": data["focus_6_12_24"],
        "records_by_horizon": records_by_horizon,
    }

    OUT_JSON.write_text(json.dumps(clean_for_json(out), indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.ARA_SPHERE_ATLAS = " + json.dumps(clean_for_json(out), allow_nan=False) + ";\n",
        encoding="utf-8",
    )
    print("ARA sphere atlas data")
    print("=" * 80)
    print(f"source: {IN_JSON}")
    for horizon, rows in records_by_horizon.items():
        ara_vals = [r["ara_current"] for r in rows]
        print(
            f"h={horizon:>2} n={len(rows):3d}"
            f" current_ara_range={rounded(min(ara_vals))}..{rounded(max(ara_vals))}"
        )
    print(f"Saved -> {OUT_JSON}")
    print(f"Saved -> {OUT_JS}")


if __name__ == "__main__":
    run()
