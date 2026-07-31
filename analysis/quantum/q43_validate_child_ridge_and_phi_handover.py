"""Independent arithmetic and artifact validation for Q43."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import pathlib
from collections import defaultdict

import numpy as np


HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_PROTOCOL_v1_FROZEN.md"
Q42_ROWS = HERE / "Q42_ARA_DUAL_STRAND_FLOW_STRANDS.csv.gz"
Q42_PROFILES = HERE / "Q42_ARA_DUAL_STRAND_FLOW_PROFILES.npz"
RESULTS = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_RESULTS.json"
CONTROL_ROWS = HERE / "Q43_CHILD_RIDGE_SAMPLING_CONTROL.csv.gz"
GRID_ROWS = HERE / "Q43_PHI_HANDOVER_GRID.csv"
FIGURE_PNG = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_DIAGNOSTICS.png"
FIGURE_SVG = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_DIAGNOSTICS.svg"
VALIDATION = HERE / "Q43_CHILD_RIDGE_AND_PHI_HANDOVER_VALIDATION.json"

PHI = (1 + math.sqrt(5)) / 2
PHI_LOW = 2 - PHI
EPS = 1e-12


def digest(path: pathlib.Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def interpolate(path, progress, coordinates, increasing):
    speed = np.abs(np.gradient(path, progress))
    if increasing:
        x_order, p_order, v_order = path, progress, speed
    else:
        x_order, p_order, v_order = path[::-1], progress[::-1], speed[::-1]
    return (
        np.interp(coordinates, x_order, p_order),
        np.interp(coordinates, x_order, v_order),
    )


def phi_scores(forward, returning, progress):
    low = np.asarray([PHI_LOW], dtype=np.float64)
    high = 2 - low
    pf_low, vf_low = interpolate(forward, progress, low, True)
    pf_high, vf_high = interpolate(forward, progress, high, True)
    pr_low, vr_low = interpolate(returning, progress, low, False)
    pr_high, vr_high = interpolate(returning, progress, high, False)
    temporal = 0.5 * (
        np.abs(pf_high - pr_low) + np.abs(pf_low - pr_high)
    )
    speed = 0.5 * (
        np.abs(vf_high - vr_low) / (vf_high + vr_low + EPS)
        + np.abs(vf_low - vr_high) / (vf_low + vr_high + EPS)
    )
    return float(temporal[0]), float(speed[0])


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    q42_rows = []
    with gzip.open(Q42_ROWS, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            q42_rows.append(
                {
                    "archive": row["archive"],
                    "seed": int(row["seed"]),
                    "pair": int(row["pair"]),
                    "family": row["family"],
                }
            )
    profiles = np.load(Q42_PROFILES)
    progress = np.asarray(profiles["progress"], dtype=np.float64)
    forward = np.asarray(profiles["forward"], dtype=np.float64)
    returning = np.asarray(profiles["returning"], dtype=np.float64)
    residual = np.asarray(profiles["residual"], dtype=np.float64)

    checks = {}
    checks["protocol_hash_matches"] = (
        digest(PROTOCOL) == result["protocol_sha256"]
    )
    checks["source_hashes_match"] = bool(
        digest(Q42_ROWS) == result["source_hashes"]["q42_rows_sha256"]
        and digest(Q42_PROFILES)
        == result["source_hashes"]["q42_profiles_sha256"]
    )
    checks["row_profile_count_matches"] = bool(
        len(q42_rows) == len(forward) == len(returning) == len(residual)
        == result["inventory"]["q42_pairs"]
    )
    checks["residual_formula_max_error"] = float(
        np.max(np.abs(residual - (forward + returning - 2)))
    )

    control_count = 0
    control_formula_error = 0.0
    with gzip.open(CONTROL_ROWS, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            control_count += 1
            observed = float(row["observed_tau_mid"])
            synthetic = float(row["symmetric_sampling_tau_mid"])
            corrected = float(row["corrected_tau_mid"])
            control_formula_error = max(
                control_formula_error,
                abs(corrected - (observed - synthetic)),
            )
    checks["control_row_count_matches"] = (
        control_count == result["inventory"]["sampling_control_lineages"]
    )
    checks["control_formula_max_error"] = float(control_formula_error)

    grid_rows = []
    with GRID_ROWS.open("r", newline="", encoding="utf-8") as stream:
        grid_rows = list(csv.DictReader(stream))
    checks["grid_row_count_matches"] = (
        len(grid_rows) == result["inventory"]["grid_rows"]
    )
    fixed_grid = np.round(np.arange(0.20, 0.5000001, 0.005), 12)
    checks["fixed_grid_is_complete"] = True
    for archive in ("greedy", "landmax"):
        for family in ("two_turn_7_5", "one_turn_15"):
            lows = np.asarray(
                [
                    float(row["low_landmark"])
                    for row in grid_rows
                    if row["archive"] == archive and row["family"] == family
                ],
                dtype=np.float64,
            )
            for expected in fixed_grid:
                if not np.any(np.isclose(lows, expected, atol=1e-12)):
                    checks["fixed_grid_is_complete"] = False

    independent_phi = {}
    common = (
        (np.min(forward, axis=1) <= 0.20)
        & (np.max(forward, axis=1) >= 1.80)
        & (np.min(returning, axis=1) <= 0.20)
        & (np.max(returning, axis=1) >= 1.80)
    )
    max_phi_temporal_error = 0.0
    max_phi_speed_error = 0.0
    count_mismatches = 0
    for archive in ("greedy", "landmax"):
        independent_phi[archive] = {}
        for family in ("two_turn_7_5", "one_turn_15"):
            by_seed_t = defaultdict(list)
            by_seed_v = defaultdict(list)
            count = 0
            for index, row in enumerate(q42_rows):
                if (
                    common[index]
                    and row["archive"] == archive
                    and row["family"] == family
                ):
                    temporal, speed = phi_scores(
                        forward[index], returning[index], progress
                    )
                    by_seed_t[row["seed"]].append(temporal)
                    by_seed_v[row["seed"]].append(speed)
                    count += 1
            temporal = float(
                np.median(
                    [
                        np.median(values)
                        for values in by_seed_t.values()
                    ]
                )
            )
            speed = float(
                np.median(
                    [
                        np.median(values)
                        for values in by_seed_v.values()
                    ]
                )
            )
            recorded = result["phi_handover"]["archives"][archive][family]
            if count != recorded["common_support_pairs"]:
                count_mismatches += 1
            max_phi_temporal_error = max(
                max_phi_temporal_error,
                abs(temporal - recorded["exact_phi"]["temporal_tension"]),
            )
            max_phi_speed_error = max(
                max_phi_speed_error,
                abs(speed - recorded["exact_phi"]["speed_tension"]),
            )
            independent_phi[archive][family] = {
                "pairs": count,
                "seeds": len(by_seed_t),
                "temporal_tension": temporal,
                "speed_tension": speed,
            }
    checks["phi_common_support_count_mismatches"] = count_mismatches
    checks["phi_temporal_max_error"] = float(max_phi_temporal_error)
    checks["phi_speed_max_error"] = float(max_phi_speed_error)
    checks["figure_png_nonempty"] = FIGURE_PNG.exists() and FIGURE_PNG.stat().st_size > 0
    checks["figure_svg_nonempty"] = FIGURE_SVG.exists() and FIGURE_SVG.stat().st_size > 0

    passed = bool(
        checks["protocol_hash_matches"]
        and checks["source_hashes_match"]
        and checks["row_profile_count_matches"]
        and checks["residual_formula_max_error"] <= 1e-12
        and checks["control_row_count_matches"]
        and checks["control_formula_max_error"] <= 1e-12
        and checks["grid_row_count_matches"]
        and checks["fixed_grid_is_complete"]
        and checks["phi_common_support_count_mismatches"] == 0
        and checks["phi_temporal_max_error"] <= 1e-12
        and checks["phi_speed_max_error"] <= 1e-12
        and checks["figure_png_nonempty"]
        and checks["figure_svg_nonempty"]
    )
    output = {
        "test_id": "Q43-VALIDATION-v1",
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "independent_phi_recalculation": independent_phi,
    }
    VALIDATION.write_text(
        json.dumps(output, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2), flush=True)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
