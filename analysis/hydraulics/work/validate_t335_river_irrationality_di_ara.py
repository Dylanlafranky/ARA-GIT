#!/usr/bin/env python3
"""Independent source-to-artifact validator for T335."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


BASE = Path(__file__).resolve().parents[1]
SOURCE = BASE / "source_bedrock_bends" / "Bed-topography.xlsx"
PROTOCOL = BASE / "T335_RIVER_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md"
RESULTS = BASE / "T335_RIVER_IRRATIONALITY_DI_ARA_RESULTS.json"
EVENTS = BASE / "results" / "T335_RIVER_IRRATIONALITY_DI_ARA_EVENTS.csv"
ENDPOINTS = BASE / "results" / "T335_RIVER_IRRATIONALITY_DI_ARA_ENDPOINTS.csv"
QUADRANTS = BASE / "results" / "T335_RIVER_IRRATIONALITY_DI_ARA_QUADRANTS.csv"
PATH_SCORES = BASE / "results" / "T335_RIVER_IRRATIONALITY_DI_ARA_PATH_SCORES.csv"
NULLS = BASE / "results" / "T335_RIVER_IRRATIONALITY_DI_ARA_ORDER_NULLS.csv"
OUTPUT = BASE / "T335_RIVER_IRRATIONALITY_DI_ARA_VALIDATION.json"

EXPECTED_PROTOCOL_HASH = "9724EA029D2A4A51A28149D1C6639CC55964A7F3DF0F37FE0D7B02F5A4953C72"
EXPECTED_SOURCE_HASH = "041FBFF2233E590AECFD9A5DFC08C84C5A17678A8DF1ABDAC667A21A2D823ED7"
RIDGE_TOL = 1e-12
N_NULL = 1_000
RNG_SEED = 335
SECTORS = ("Ba", "Ab", "bA", "aB")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest().upper()


def split_for(angle: int) -> str:
    if angle <= 60:
        return "calibration"
    if angle <= 110:
        return "evaluation"
    return "holdout"


def sector(scale: float, turn: float) -> str:
    if abs(math.log(scale)) <= RIDGE_TOL or abs(turn) <= RIDGE_TOL:
        return "boundary"
    if scale < 1 and turn > 0:
        return "Ba"
    if scale > 1 and turn > 0:
        return "Ab"
    if scale < 1 and turn < 0:
        return "bA"
    return "aB"


def close(a, b, tolerance=1e-10) -> bool:
    if a is None or b is None:
        return a is None and b is None
    if pd.isna(a) or pd.isna(b):
        return pd.isna(a) and pd.isna(b)
    return math.isclose(float(a), float(b), rel_tol=tolerance, abs_tol=tolerance)


def endpoint(values: np.ndarray, alpha: float | None = None) -> dict:
    values = np.asarray(values, dtype=float)
    low = values[values < 1 - RIDGE_TOL]
    high = values[values > 1 + RIDGE_TOL]
    if len(low) == 0 or len(high) == 0:
        return {"s_minus": None, "s_plus": None, "product": None, "implied_alpha": None, "endpoint_loss": None}
    log_low = float(np.median(np.log(low)))
    log_high = float(np.median(np.log(high)))
    s_minus = float(np.median(low))
    s_plus = float(np.median(high))
    implied = math.exp((log_high - log_low) / 2)
    loss = None if alpha is None else 0.5 * (
        abs(log_low + math.log(alpha)) + abs(log_high - math.log(alpha))
    )
    return {
        "s_minus": s_minus,
        "s_plus": s_plus,
        "product": s_minus * s_plus,
        "implied_alpha": implied,
        "endpoint_loss": loss,
    }


def reconstruct_steps() -> tuple[dict[int, np.ndarray], dict[int, np.ndarray], tuple[int, int]]:
    raw = pd.read_excel(SOURCE)
    original_shape = raw.shape
    raw.columns = ["x", "y", "z"]
    positions: dict[int, list[complex]] = {rank: [] for rank in range(1, 42)}
    for block, expected_angle in zip(range(2, 35), range(10, 175, 5)):
        section = raw.iloc[block * 41 : (block + 1) * 41].copy()
        section["radius"] = np.hypot(section["x"], section["y"])
        section = section.sort_values("radius", kind="mergesort").reset_index(drop=True)
        order = np.argsort(section["z"].to_numpy(float), kind="mergesort")
        for rank, index in enumerate(order, start=1):
            row = section.iloc[index]
            observed_angle = math.degrees(math.atan2(float(row["y"]), float(row["x"])))
            if abs(observed_angle - expected_angle) > 1e-5:
                raise AssertionError("Source angle mismatch")
            positions[rank].append(complex(float(row["x"]), float(row["y"])))
    arrays = {rank: np.asarray(values, dtype=complex) for rank, values in positions.items()}
    steps = {rank: np.diff(values) for rank, values in arrays.items()}
    return arrays, steps, original_shape


def expected_events(steps: dict[int, np.ndarray], kind: str) -> pd.DataFrame:
    records = []
    centers = np.arange(15, 170, 5)
    for rank in range(1, 42):
        if kind == "observed":
            q = steps[rank][1:] / steps[rank][:-1]
        elif kind == "broken_lineage":
            partner = rank + 1 if rank < 41 else 1
            q = steps[partner][1:] / steps[rank][:-1]
        else:
            reverse_steps = -steps[rank][::-1]
            q = reverse_steps[1:] / reverse_steps[:-1]
        used_centers = centers if kind != "reversed" else centers[::-1]
        for index, (angle, value) in enumerate(zip(used_centers, q)):
            scale = float(abs(value))
            turn = float(np.angle(value))
            records.append({
                "source_kind": kind,
                "elevation_rank": rank,
                "event_index": index,
                "middle_angle_deg": int(angle),
                "split": split_for(int(angle)) if kind != "reversed" else "reverse_audit",
                "scale_ratio_s": scale,
                "turn_delta_rad": turn,
                "x_radial_ara": 2 * scale / (1 + scale),
                "y_turn_ara": 1 + turn / math.pi,
                "sector": sector(scale, turn),
            })
    return pd.DataFrame(records)


def main() -> None:
    checks = []

    def check(name: str, passed: bool, detail) -> None:
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("protocol_hash", digest(PROTOCOL) == EXPECTED_PROTOCOL_HASH, digest(PROTOCOL))
    check("source_hash", digest(SOURCE) == EXPECTED_SOURCE_HASH, digest(SOURCE))

    positions, steps, raw_shape = reconstruct_steps()
    check("source_shape", raw_shape == (1666, 3), list(raw_shape))
    check(
        "reconstructed_path_shape",
        len(positions) == 41 and all(len(value) == 33 for value in positions.values()),
        {"paths": len(positions), "sections": sorted({len(value) for value in positions.values()})},
    )

    saved_events = pd.read_csv(EVENTS)
    expected = {
        kind: expected_events(steps, kind)
        for kind in ("observed", "broken_lineage", "reversed")
    }
    check(
        "saved_event_counts",
        len(saved_events) == 3 * 1271 and all(
            int((saved_events["source_kind"] == kind).sum()) == 1271 for kind in expected
        ),
        saved_events.groupby("source_kind").size().to_dict(),
    )

    event_match = True
    maximum_errors = {name: 0.0 for name in ("scale_ratio_s", "turn_delta_rad", "x_radial_ara", "y_turn_ara")}
    for kind, frame in expected.items():
        saved = saved_events[saved_events["source_kind"] == kind].sort_values(
            ["elevation_rank", "event_index"]
        ).reset_index(drop=True)
        frame = frame.sort_values(["elevation_rank", "event_index"]).reset_index(drop=True)
        for column in maximum_errors:
            error = float(np.max(np.abs(saved[column].to_numpy(float) - frame[column].to_numpy(float))))
            maximum_errors[column] = max(maximum_errors[column], error)
            event_match = event_match and error <= 1e-10
        event_match = event_match and saved["sector"].tolist() == frame["sector"].tolist()
        event_match = event_match and saved["split"].tolist() == frame["split"].tolist()
    check("source_to_event_reconstruction", event_match, maximum_errors)

    observed = expected["observed"]
    split_counts = observed.groupby("split").size().to_dict()
    check(
        "split_counts",
        split_counts == {"calibration": 410, "evaluation": 410, "holdout": 451},
        split_counts,
    )
    check(
        "ara_coordinate_ranges",
        bool(observed["x_radial_ara"].between(0, 2).all() and observed["y_turn_ara"].between(0, 2).all()),
        {
            "x": [float(observed["x_radial_ara"].min()), float(observed["x_radial_ara"].max())],
            "y": [float(observed["y_turn_ara"].min()), float(observed["y_turn_ara"].max())],
        },
    )
    reciprocal_test = np.geomspace(1e-4, 1e4, 1000)
    transform = lambda value: 2 * value / (1 + value)
    reciprocal_error = float(np.max(np.abs(transform(1 / reciprocal_test) - (2 - transform(reciprocal_test)))))
    check("exact_reciprocal_transform", reciprocal_error <= 1e-12, reciprocal_error)

    alpha_cal = float(endpoint(observed[observed["split"] == "calibration"]["scale_ratio_s"].to_numpy())["implied_alpha"])
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    check("calibration_alpha", close(alpha_cal, result["alpha_cal"]), {"recomputed": alpha_cal, "saved": result["alpha_cal"]})

    saved_endpoints = pd.read_csv(ENDPOINTS)
    endpoint_match = True
    endpoint_errors = []
    sources = {
        "field": observed,
        "thalweg": observed[observed["elevation_rank"] == 1],
        "broken_field": expected["broken_lineage"],
        "broken_thalweg": expected["broken_lineage"][expected["broken_lineage"]["elevation_rank"] == 1],
    }
    for population, frame in sources.items():
        for split in ("calibration", "evaluation", "holdout", "pooled"):
            part = frame if split == "pooled" else frame[frame["split"] == split]
            calculated = endpoint(part["scale_ratio_s"].to_numpy(float), alpha_cal)
            saved = saved_endpoints[(saved_endpoints["population"] == population) & (saved_endpoints["split"] == split)].iloc[0]
            for key, value in calculated.items():
                endpoint_match = endpoint_match and close(value, saved[key])
                if value is not None and not pd.isna(saved[key]):
                    endpoint_errors.append(abs(float(value) - float(saved[key])))
    check("endpoint_recalculation", endpoint_match, {"max_error": max(endpoint_errors, default=0.0)})

    saved_quadrants = pd.read_csv(QUADRANTS)
    quadrant_match = True
    for population in ("field", "thalweg"):
        frame = observed if population == "field" else observed[observed["elevation_rank"] == 1]
        for split in ("calibration", "evaluation", "holdout", "pooled"):
            part = frame if split == "pooled" else frame[frame["split"] == split]
            nonboundary = part[part["sector"] != "boundary"]
            for name in SECTORS:
                share = float((nonboundary["sector"] == name).sum() / len(nonboundary))
                saved = saved_quadrants[(saved_quadrants["population"] == population) & (saved_quadrants["split"] == split) & (saved_quadrants["sector"] == name)].iloc[0]
                quadrant_match = quadrant_match and close(share, saved["share_nonboundary"])
    check("quadrant_recalculation", quadrant_match, "all field and thalweg split shares")

    saved_paths = pd.read_csv(PATH_SCORES)
    path_match = True
    for split in ("calibration", "evaluation", "holdout"):
        recalculated = []
        for rank in range(1, 42):
            values = observed[(observed["split"] == split) & (observed["elevation_rank"] == rank)]["scale_ratio_s"].to_numpy(float)
            recalculated.append(endpoint(values, alpha_cal)["endpoint_loss"])
        ranks = pd.Series(recalculated).rank(method="min").to_numpy(float)
        saved = saved_paths[saved_paths["split"] == split].sort_values("elevation_rank")
        saved_loss = saved["endpoint_loss"].to_numpy(float)
        path_match = path_match and np.allclose(saved_loss, np.asarray(recalculated, dtype=float), equal_nan=True)
        path_match = path_match and np.allclose(saved["loss_rank"].to_numpy(float), ranks, equal_nan=True)
    check("path_score_recalculation", path_match, "41 ranks x 3 splits")

    saved_nulls = pd.read_csv(NULLS).sort_values(["draw", "split"]).reset_index(drop=True)
    rng = np.random.default_rng(RNG_SEED)
    center_splits = np.array([split_for(int(a)) for a in np.arange(15, 170, 5)])
    null_records = []
    for draw in range(N_NULL):
        shuffled_field = []
        for rank in range(1, 42):
            shuffled = steps[rank][rng.permutation(32)]
            shuffled_field.append(np.abs(shuffled[1:] / shuffled[:-1]))
        shuffled_field = np.stack(shuffled_field)
        for split in ("evaluation", "holdout"):
            values = shuffled_field[:, center_splits == split].reshape(-1)
            null_records.append({"draw": draw, "split": split, "endpoint_loss": endpoint(values, alpha_cal)["endpoint_loss"]})
    recalculated_nulls = pd.DataFrame(null_records).sort_values(["draw", "split"]).reset_index(drop=True)
    null_error = float(np.max(np.abs(saved_nulls["endpoint_loss"].to_numpy(float) - recalculated_nulls["endpoint_loss"].to_numpy(float))))
    check("order_null_recalculation", null_error <= 1e-10, {"rows": len(saved_nulls), "max_error": null_error})

    reverse_forward = observed.sort_values(["elevation_rank", "event_index"])
    reverse_saved = expected["reversed"].sort_values(["elevation_rank", "event_index"])
    reverse_ok = True
    for rank in range(1, 42):
        f = reverse_forward[reverse_forward["elevation_rank"] == rank]
        r = reverse_saved[reverse_saved["elevation_rank"] == rank]
        reverse_ok = reverse_ok and np.allclose(r["scale_ratio_s"].to_numpy(), 1 / f["scale_ratio_s"].to_numpy()[::-1])
        reverse_ok = reverse_ok and np.allclose(r["turn_delta_rad"].to_numpy(), -f["turn_delta_rad"].to_numpy()[::-1])
    check("reverse_diagonal_reflection", reverse_ok, "s -> 1/s and delta -> -delta")

    gate_values = result["gates"]
    expected_gates = {
        "G1_field_four_sectors": all(
            result["quadrant_shares"]["field"][split][name] >= 0.05
            for split in ("evaluation", "holdout") for name in SECTORS
        ),
        "G2_thalweg_sector_coverage": (
            all(result["thalweg_sector_counts"]["pooled"][name] > 0 for name in SECTORS)
            and all(sum(result["thalweg_sector_counts"][split][name] > 0 for name in SECTORS) >= 3 for split in ("evaluation", "holdout"))
        ),
        "G3_reciprocal_closure": (
            all(0.90 <= result["field_endpoints"][split]["product"] <= 1.10 for split in ("evaluation", "holdout"))
            and 0.80 <= result["thalweg_endpoints"]["pooled"]["product"] <= 1.20
            and all(0.75 <= result["thalweg_endpoints"][split]["product"] <= 1.25 for split in ("evaluation", "holdout"))
        ),
        "G4_calibration_transfer": all(
            abs(math.log(result["field_endpoints"][split]["implied_alpha"] / result["alpha_cal"])) <= math.log(1.10)
            for split in ("evaluation", "holdout")
        ),
        "G5_recorded_order": all(result["order_null"][split]["empirical_p_lower"] <= 0.05 for split in ("evaluation", "holdout")),
        "G6_intact_rank_lineage": all(
            result["field_endpoints"][split]["endpoint_loss"] < result["broken_field_endpoints"][split]["endpoint_loss"]
            for split in ("evaluation", "holdout")
        ),
        "G7_thalweg_specificity": (
            all(
                result["thalweg_control_comparison"][split]["thalweg_endpoint_loss"]
                < result["thalweg_control_comparison"][split]["control_median_endpoint_loss"]
                for split in ("evaluation", "holdout")
            )
            and any(result["thalweg_control_comparison"][split]["thalweg_rank_of_41"] <= 4 for split in ("evaluation", "holdout"))
        ),
    }
    check("gate_recalculation", all(bool(gate_values[key]) == value for key, value in expected_gates.items()), expected_gates)
    check("declared_phi_boundary", result["verdict"]["phi_supported"] is False, result["verdict"]["phi_supported"])

    all_pass = all(item["passed"] for item in checks)
    validation = {
        "test": "T335 river/thalweg Irrationality Di-ARA independent validation",
        "date": "2026-08-03",
        "passed": all_pass,
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
        "note": "G0 passes when this validator passes; the runner leaves G0 pending/false to avoid self-validation.",
    }
    OUTPUT.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not all_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
