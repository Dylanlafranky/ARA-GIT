#!/usr/bin/env python3
"""Independent validation for T325.

This script deliberately does not import the T325 analysis implementation. It
reconstructs the plant lineages, ARA positions, fixed-candidate scores and
Fibonacci return profile directly from the checksum-locked workbook, then
checks those independently calculated quantities against the saved artifacts.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "Source Data 21.xlsx"
PROTOCOL = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_PROTOCOL_v2_FROZEN.md"
RESULTS = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_RESULTS.json"
CANDIDATE_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_CANDIDATES.csv"
HORIZON_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_HORIZONS.csv"
FIBONACCI_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_FIBONACCI.csv"
EVENT_CSV = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_EVENTS.csv"
VALIDATION_JSON = HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_VALIDATION.json"

SOURCE_SHA256 = "E78372214B1386A486B25C8340C19F22BC74D3382F80A9B36A2972CC3D35ADFB"
PROTOCOL_SHA256 = "3CFD1A0BE552DF7BECBF69087462BF8C2C3A974EBD7ED15340A4696306536593"
PHI = (1.0 + math.sqrt(5.0)) / 2.0

FIXED = OrderedDict(
    [
        ("persistence", 0.0),
        ("one_third_phase", 2.0 / 3.0),
        ("one_over_e", 2.0 / math.e),
        ("nearest_eighth_3_8", 3.0 / 4.0),
        ("fibonacci_8_21", 16.0 / 21.0),
        ("phi", 2.0 / (PHI * PHI)),
        ("two_fifths_phase", 4.0 / 5.0),
        ("silver_conjugate", 2.0 * (math.sqrt(2.0) - 1.0)),
        ("half_turn_ridge", 1.0),
    ]
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def circular_distance(x, y):
    difference = np.abs(np.asarray(x, dtype=float) - np.asarray(y, dtype=float))
    return np.minimum(difference, 2.0 - difference)


def reconstruct() -> pd.DataFrame:
    source = pd.read_excel(SOURCE, sheet_name="EPFL_phyllo-angle")
    assert source.columns.tolist() == ["genotype", "meristem", "angle"]
    assert len(source) == 359
    assert source["angle"].between(0.0, 360.0, inclusive="both").all()

    counters: dict[str, int] = {}
    plant_ids: list[int] = []
    for row in source.itertuples(index=False):
        genotype = str(row.genotype)
        if genotype not in counters or int(row.meristem) == 1:
            counters[genotype] = counters.get(genotype, 0) + 1
        plant_ids.append(counters[genotype])
    source["plant"] = plant_ids
    source["split"] = np.where(source["plant"] % 2 == 0, "confirmation", "development")
    source["u_ara"] = source["angle"].astype(float) / 180.0
    source["position_ara"] = np.nan
    for _, group in source.groupby(["genotype", "plant"], sort=False):
        sequence = group["meristem"].astype(int).tolist()
        assert sequence == list(range(1, len(sequence) + 1))
        source.loc[group.index, "position_ara"] = np.mod(
            np.cumsum(group["u_ara"].to_numpy(float)), 2.0
        )
    assert source.groupby(["genotype", "plant"]).ngroups == 58
    return source


def confirmation_groups(source: pd.DataFrame) -> list[pd.DataFrame]:
    chosen = source[(source["genotype"] == "Col") & (source["split"] == "confirmation")]
    groups = [g.sort_values("meristem") for _, g in chosen.groupby("plant", sort=True)]
    assert len(groups) == 10
    return groups


def fixed_candidate_summary(groups: list[pd.DataFrame]) -> dict[str, dict[str, float]]:
    output: dict[str, dict[str, float]] = {}
    for name, increment in FIXED.items():
        step_losses: list[float] = []
        carrier_losses: list[float] = []
        for group in groups:
            steps = group["u_ara"].to_numpy(float)
            positions = group["position_ara"].to_numpy(float)
            held = np.arange(2, len(group))
            step_losses.append(float(np.median(circular_distance(steps[held], increment))))
            horizons = held - 1
            predicted = np.mod(positions[1] + horizons * increment, 2.0)
            carrier_losses.append(float(np.median(circular_distance(positions[held], predicted))))
        output[name] = {
            "one_step_median_ara": float(np.median(step_losses)),
            "carrier_median_ara": float(np.median(carrier_losses)),
        }
    return output


def fibonacci_profile(groups: list[pd.DataFrame]) -> dict[str, float]:
    observed: dict[int, float] = {}
    for lag in (2, 3, 5):
        plant_medians: list[float] = []
        for group in groups:
            positions = np.r_[0.0, group["position_ara"].to_numpy(float)]
            if len(positions) > lag:
                plant_medians.append(
                    float(np.median(circular_distance(positions[lag:], positions[:-lag])))
                )
        observed[lag] = float(np.median(plant_medians))

    profile: dict[str, float] = {}
    for name, increment in FIXED.items():
        errors = []
        for lag in (2, 3, 5):
            predicted = float(circular_distance((lag * increment) % 2.0, 0.0))
            errors.append(abs(observed[lag] - predicted))
        profile[name] = float(np.mean(errors))
    return profile


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: object) -> None:
        checks.append({"check": name, "passed": bool(passed), "detail": detail})
        if not passed:
            raise AssertionError(f"{name}: {detail}")

    check("source_sha256", digest(SOURCE) == SOURCE_SHA256, digest(SOURCE))
    check("protocol_sha256", digest(PROTOCOL) == PROTOCOL_SHA256, digest(PROTOCOL))
    source = reconstruct()
    groups = confirmation_groups(source)
    check("source_rows", len(source) == 359, len(source))
    check("source_plants", source.groupby(["genotype", "plant"]).ngroups == 58, 58)
    check("confirmation_wild_type_plants", len(groups) == 10, len(groups))

    saved_events = pd.read_csv(EVENT_CSV)
    check("event_rows", len(saved_events) == len(source), len(saved_events))
    check(
        "event_u_coordinates",
        np.allclose(saved_events["u_ara"], source["u_ara"], atol=1e-12),
        "recomputed angle/180",
    )
    check(
        "event_parent_positions",
        np.allclose(saved_events["position_ara"], source["position_ara"], atol=1e-12),
        "recomputed cumulative modulo-2 positions",
    )

    recomputed_candidates = fixed_candidate_summary(groups)
    saved_candidates = pd.read_csv(CANDIDATE_CSV).set_index("candidate")
    for name, values in recomputed_candidates.items():
        for metric, expected in values.items():
            actual = float(saved_candidates.loc[name, metric])
            check(f"candidate_{name}_{metric}", abs(actual - expected) < 1e-10, actual)

    one_step_winner = min(
        recomputed_candidates,
        key=lambda name: recomputed_candidates[name]["one_step_median_ara"],
    )
    carrier_winner = min(
        recomputed_candidates,
        key=lambda name: recomputed_candidates[name]["carrier_median_ara"],
    )
    check("one_step_fixed_winner", one_step_winner == "nearest_eighth_3_8", one_step_winner)
    check("carrier_fixed_winner", carrier_winner == "phi", carrier_winner)

    recomputed_fibonacci = fibonacci_profile(groups)
    fibonacci_winner = min(recomputed_fibonacci, key=recomputed_fibonacci.get)
    check("fibonacci_fixed_winner", fibonacci_winner == "phi", fibonacci_winner)
    saved_fibonacci = pd.read_csv(FIBONACCI_CSV)
    saved_profile = (
        saved_fibonacci.groupby("candidate")["profile_mae_ara"].first().to_dict()
    )
    for name, expected in recomputed_fibonacci.items():
        check(
            f"fibonacci_{name}",
            abs(float(saved_profile[name]) - expected) < 1e-10,
            float(saved_profile[name]),
        )

    saved_result = json.loads(RESULTS.read_text(encoding="utf-8"))
    check(
        "headline_one_step_winner",
        saved_result["headline"]["fixed_one_step_winner"] == one_step_winner,
        saved_result["headline"]["fixed_one_step_winner"],
    )
    check(
        "headline_carrier_winner",
        saved_result["headline"]["fixed_carrier_winner"] == carrier_winner,
        saved_result["headline"]["fixed_carrier_winner"],
    )
    check(
        "headline_fibonacci_winner",
        saved_result["headline"]["fibonacci_profile_winner"] == fibonacci_winner,
        saved_result["headline"]["fibonacci_profile_winner"],
    )

    horizon = pd.read_csv(HORIZON_CSV)
    check("horizon_rows", len(horizon) == 55, len(horizon))
    check("horizon_bounds", horizon["median_error_ara"].between(0.0, 1.0).all(), "0..1")

    nulls = pd.read_csv(HERE / "T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_NULLS.csv")
    expected_controls = {
        "within_plant_order_carrier",
        "within_plant_order_compensation",
        "broken_lineage_compensation",
    }
    check("null_summary_rows", len(nulls) == 3, len(nulls))
    check("null_controls", set(nulls["control"]) == expected_controls, sorted(nulls["control"]))
    numeric_null_columns = ["observed", "null_median", "null_lo", "null_hi", "p_lower"]
    check(
        "null_summary_finite",
        np.isfinite(nulls[numeric_null_columns].to_numpy(float)).all(),
        "all summary values finite",
    )

    validation = {
        "test_id": "T325-PHI-CIRCLE-TRAIN-PHYLLOTAXIS-v2-independent-validation",
        "status": "PASS",
        "independence_boundary": "Independent formulas and workbook reconstruction; statistical null arrays are audited from frozen outputs rather than regenerated.",
        "headline": {
            "fixed_one_step_winner": one_step_winner,
            "fixed_carrier_winner": carrier_winner,
            "fibonacci_profile_winner": fibonacci_winner,
            "phi_one_step_median_deg": recomputed_candidates["phi"]["one_step_median_ara"] * 180.0,
            "three_eighths_one_step_median_deg": recomputed_candidates["nearest_eighth_3_8"]["one_step_median_ara"] * 180.0,
            "phi_carrier_median_deg": recomputed_candidates["phi"]["carrier_median_ara"] * 180.0,
            "three_eighths_carrier_median_deg": recomputed_candidates["nearest_eighth_3_8"]["carrier_median_ara"] * 180.0,
        },
        "checks": checks,
    }
    VALIDATION_JSON.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation["headline"], indent=2))
    print(f"PASS: {len(checks)} checks")


if __name__ == "__main__":
    main()
