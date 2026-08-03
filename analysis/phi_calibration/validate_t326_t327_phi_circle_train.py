#!/usr/bin/env python3
"""Independent arithmetic and provenance validation for T326 and T327.

This validator does not import either production analysis.  It reconstructs
the central scores from exported ordered events (T326) and the raw workbook
(T327), then checks the reported artifacts and frozen protocol hashes.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
HYDRO = HERE.parent / "hydraulics"
T326 = "T326_PHI_CIRCLE_TRAIN_INDEPENDENT_PLANTS"
T327 = "T327_PHI_CIRCLE_TRAIN_THALWEG"
PHI = (1 + math.sqrt(5)) / 2
PHI_INCREMENT = 2 / PHI**2

CANDIDATES = OrderedDict(
    [
        ("persistence", 0.0),
        ("one_third", 2 / 3),
        ("one_over_e", 2 / math.e),
        ("three_eighths", 3 / 4),
        ("fibonacci_8_21", 16 / 21),
        ("phi", PHI_INCREMENT),
        ("two_fifths", 4 / 5),
        ("silver_conjugate", 2 * (math.sqrt(2) - 1)),
        ("ridge", 1.0),
    ]
)


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest().upper()


def d2(a, b):
    difference = np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))
    return np.minimum(difference, 2 - difference)


checks: list[dict] = []


def check(name: str, passed: bool, observed=None, expected=None, tolerance=None):
    checks.append(
        {
            "name": name,
            "passed": bool(passed),
            "observed": observed,
            "expected": expected,
            "tolerance": tolerance,
        }
    )


def close(name, observed, expected, tolerance=1e-10):
    check(name, abs(float(observed) - float(expected)) <= tolerance, float(observed), float(expected), tolerance)


def validate_t326() -> dict:
    result = json.loads((HERE / f"{T326}_RESULTS.json").read_text(encoding="utf-8"))
    events = pd.read_csv(HERE / f"{T326}_EVENTS.csv")
    exported_scores = pd.read_csv(HERE / f"{T326}_PLANT_SCORES.csv")
    fib_export = pd.read_csv(HERE / f"{T326}_FIBONACCI.csv")
    raw_checks = pd.read_csv(HERE / f"{T326}_RAW_RECONSTRUCTION.csv")

    protocol = HERE / "T326_PHI_CIRCLE_TRAIN_INDEPENDENT_PLANTS_PROTOCOL_v1_FROZEN.md"
    check("T326 protocol hash", digest(protocol) == result["protocol_sha256"], digest(protocol), result["protocol_sha256"])
    for relative, expected in result["source_hashes"].items():
        path = HERE / relative
        check(f"T326 source hash {relative}", path.exists() and digest(path) == expected, digest(path) if path.exists() else None, expected)

    land = events[events["dataset"] == "Landrein2015"].copy()
    cyanella = events[events["dataset"] == "Cyanella2025"].copy()
    check("T326 Landrein event count", len(land) == 7507, len(land), 7507)
    check("T326 Landrein plant count", land["plant_id"].nunique() == 196, int(land["plant_id"].nunique()), 196)
    check("T326 Landrein cohort count", land["cohort"].nunique() == 8, int(land["cohort"].nunique()), 8)
    check("T326 Cyanella event count", len(cyanella) == 684, len(cyanella), 684)
    check("T326 Cyanella plant count", cyanella["plant_id"].nunique() == 130, int(cyanella["plant_id"].nunique()), 130)

    rebuilt = []
    land_groups = []
    for plant_id, group in land.groupby("plant_id", sort=False):
        g = group.sort_values("event")
        steps = g["u_ara"].to_numpy(float)
        positions = g["position_ara"].to_numpy(float)
        anchor = positions[1]
        horizons = np.arange(1, len(g) - 1, dtype=float)
        land_groups.append((steps, positions, anchor, horizons))
        for candidate, delta in CANDIDATES.items():
            prediction = np.mod(anchor + horizons * delta, 2)
            rebuilt.append(
                {
                    "plant_id": plant_id,
                    "candidate": candidate,
                    "one_step_median_ara": float(np.median(d2(steps[2:], delta))),
                    "carrier_median_ara": float(np.median(d2(positions[2:], prediction))),
                }
            )
    rebuilt = pd.DataFrame(rebuilt)
    merged = rebuilt.merge(
        exported_scores[exported_scores["dataset"] == "Landrein2015"],
        on=["plant_id", "candidate"],
        suffixes=("_rebuilt", "_exported"),
    )
    close(
        "T326 maximum one-step reconstruction difference",
        np.max(np.abs(merged["one_step_median_ara_rebuilt"] - merged["one_step_median_ara_exported"])),
        0.0,
        2e-12,
    )
    close(
        "T326 maximum carrier reconstruction difference",
        np.max(np.abs(merged["carrier_median_ara_rebuilt"] - merged["carrier_median_ara_exported"])),
        0.0,
        2e-12,
    )
    aggregate = rebuilt.groupby("candidate").agg(
        child=("one_step_median_ara", "median"), parent=("carrier_median_ara", "median")
    )
    child_winner = str(aggregate["child"].idxmin())
    parent_winner = str(aggregate["parent"].idxmin())
    check("T326 child winner", child_winner == result["Landrein2015"]["child_winner"], child_winner, result["Landrein2015"]["child_winner"])
    check("T326 parent winner", parent_winner == result["Landrein2015"]["parent_winner"], parent_winner, result["Landrein2015"]["parent_winner"])

    true_losses = []
    prepared = []
    for steps, positions, anchor, horizons in land_groups:
        prediction = np.mod(anchor + horizons * PHI_INCREMENT, 2)
        true_losses.append(float(np.median(d2(positions[2:], prediction))))
        prepared.append((anchor, steps[2:].copy(), prediction))
    observed_order = float(np.median(true_losses))
    close("T326 observed ordered carrier", observed_order, result["Landrein2015"]["order_shuffle"]["observed"])

    # Exact frozen order null. This repeats the registered random stream but
    # rebuilds every synthetic path from the exported source-order events.
    rng = np.random.default_rng(326)
    null = np.empty(10_000)
    for draw in range(10_000):
        losses = []
        for anchor, held, prediction in prepared:
            synthetic = np.mod(anchor + np.cumsum(rng.permutation(held)), 2)
            losses.append(float(np.median(d2(synthetic, prediction))))
        null[draw] = np.median(losses)
    p_lower = float((1 + np.sum(null <= observed_order)) / 10_001)
    close("T326 exact shuffle p-value", p_lower, result["Landrein2015"]["order_shuffle"]["p_lower"])

    residuals = [steps[2:] - PHI_INCREMENT for steps, _, _, _ in land_groups]
    x = np.concatenate([values[:-1] for values in residuals if len(values) >= 2])
    y = np.concatenate([values[1:] for values in residuals if len(values) >= 2])
    denominator = np.median((np.abs(x) + np.abs(y)) / 2)
    compensation = float(np.median(np.abs((x + y) / 2)) / denominator)
    close("T326 compensation observed", compensation, result["Landrein2015"]["compensation"]["observed_ratio"])

    fib_mae = fib_export.groupby("candidate")["absolute_profile_error"].mean()
    fib_winner = str(fib_mae.idxmin())
    check("T326 Fibonacci-return winner", fib_winner == result["Landrein2015"]["fibonacci_best_candidate"], fib_winner, result["Landrein2015"]["fibonacci_best_candidate"])
    close("T326 raw reconstruction maximum MAE", raw_checks["best_mae_deg"].max(), 0.0)
    check("T326 formal verdict", result["verdict"] == "NOT REPLICATED", result["verdict"], "NOT REPLICATED")

    return {
        "verdict": result["verdict"],
        "child_winner": child_winner,
        "parent_winner": parent_winner,
        "order_p_lower": p_lower,
        "compensation_observed": compensation,
    }


def path_scores(x: np.ndarray, delta: float) -> dict:
    increments = np.mod(np.diff(x), 2)
    local_positive = float(np.median(d2(increments, delta)))
    local_negative = float(np.median(d2(increments, (2 - delta) % 2)))
    horizons = np.arange(1, len(x) - 1, dtype=float)
    positive = np.mod(x[1] + horizons * delta, 2)
    negative = np.mod(x[1] - horizons * delta, 2)
    parent_positive = float(np.median(d2(x[2:], positive)))
    parent_negative = float(np.median(d2(x[2:], negative)))
    return {
        "local_score": min(local_positive, local_negative),
        "parent_score": min(parent_positive, parent_negative),
        "local_positive": local_positive,
        "local_negative": local_negative,
        "parent_positive": parent_positive,
        "parent_negative": parent_negative,
    }


def validate_t327() -> dict:
    result = json.loads((HYDRO / f"{T327}_RESULTS.json").read_text(encoding="utf-8"))
    protocol = HYDRO / "T327_PHI_CIRCLE_TRAIN_THALWEG_PROTOCOL_v2_FROZEN.md"
    source = HYDRO / "source_bedrock_bends" / "Bed-topography.xlsx"
    exported_positions = pd.read_csv(HYDRO / f"{T327}_PATH_POSITIONS.csv")
    exported_scores = pd.read_csv(HYDRO / f"{T327}_PATH_SCORES.csv")
    check("T327 protocol hash", digest(protocol) == result["protocol_sha256"], digest(protocol), result["protocol_sha256"])
    check("T327 source hash", digest(source) == result["source_sha256"], digest(source), result["source_sha256"])

    raw = pd.read_excel(source)
    raw.columns = ["x_mm", "y_mm", "z_mm"]
    rebuilt_rows = []
    for block, angle_expected in zip(range(2, 35), range(10, 175, 5)):
        section = raw.iloc[block * 41 : (block + 1) * 41].copy()
        section["radius_mm"] = np.hypot(section["x_mm"], section["y_mm"])
        angle = np.degrees(np.arctan2(section["y_mm"], section["x_mm"]))
        check(f"T327 source angle {angle_expected}", np.max(np.abs(angle - angle_expected)) < 1e-5, float(np.max(np.abs(angle - angle_expected))), 0.0, 1e-5)
        section = section.sort_values("radius_mm", kind="mergesort").reset_index(drop=True)
        section["x_ara"] = 2 * (section["radius_mm"] - section["radius_mm"].min()) / (
            section["radius_mm"].max() - section["radius_mm"].min()
        )
        order = np.argsort(section["z_mm"].to_numpy(float), kind="mergesort")
        for elevation_rank, source_index in enumerate(order, start=1):
            row = section.iloc[source_index]
            rebuilt_rows.append(
                {
                    "angle_deg": angle_expected,
                    "elevation_rank": elevation_rank,
                    "z_mm": float(row["z_mm"]),
                    "x_ara": float(row["x_ara"]),
                }
            )
    rebuilt = pd.DataFrame(rebuilt_rows)
    check("T327 rebuilt cross-sections", rebuilt["angle_deg"].nunique() == 33, int(rebuilt["angle_deg"].nunique()), 33)
    check("T327 rebuilt ordered paths", rebuilt["elevation_rank"].nunique() == 41, int(rebuilt["elevation_rank"].nunique()), 41)
    merged_positions = rebuilt.merge(exported_positions, on=["angle_deg", "elevation_rank"], suffixes=("_rebuilt", "_exported"))
    close("T327 maximum path-coordinate reconstruction difference", np.max(np.abs(merged_positions["x_ara_rebuilt"] - merged_positions["x_ara_exported"])), 0.0, 2e-12)
    close("T327 maximum selected-Z reconstruction difference", np.max(np.abs(merged_positions["z_mm_rebuilt"] - merged_positions["z_mm_exported"])), 0.0, 2e-12)

    score_rows = []
    for rank, group in rebuilt.groupby("elevation_rank", sort=True):
        x = group.sort_values("angle_deg")["x_ara"].to_numpy(float)
        for candidate, delta in CANDIDATES.items():
            score_rows.append({"elevation_rank": rank, "candidate": candidate, **path_scores(x, delta)})
    rebuilt_scores = pd.DataFrame(score_rows)
    merged_scores = rebuilt_scores.merge(exported_scores, on=["elevation_rank", "candidate"], suffixes=("_rebuilt", "_exported"))
    for field in ("local_score", "parent_score", "local_positive", "local_negative", "parent_positive", "parent_negative"):
        close(
            f"T327 maximum {field} reconstruction difference",
            np.max(np.abs(merged_scores[f"{field}_rebuilt"] - merged_scores[f"{field}_exported"])),
            0.0,
            2e-12,
        )

    thalweg_scores = rebuilt_scores[rebuilt_scores["elevation_rank"] == 1]
    local_winner = str(thalweg_scores.loc[thalweg_scores["local_score"].idxmin(), "candidate"])
    parent_winner = str(thalweg_scores.loc[thalweg_scores["parent_score"].idxmin(), "candidate"])
    check("T327 local winner", local_winner == result["thalweg"]["local_winner"], local_winner, result["thalweg"]["local_winner"])
    check("T327 parent winner", parent_winner == result["thalweg"]["parent_winner"], parent_winner, result["thalweg"]["parent_winner"])

    thalweg_x = rebuilt[rebuilt["elevation_rank"] == 1].sort_values("angle_deg")["x_ara"].to_numpy(float)
    observed = path_scores(thalweg_x, PHI_INCREMENT)["parent_score"]
    rng = np.random.default_rng(327)
    null = np.array([path_scores(rng.permutation(thalweg_x), PHI_INCREMENT)["parent_score"] for _ in range(10_000)])
    p_lower = float((1 + np.sum(null <= observed)) / 10_001)
    close("T327 observed Phi carrier", observed, result["order_controls"]["observed"])
    close("T327 exact shuffle p-value", p_lower, result["order_controls"]["shuffle_p_lower"])

    phi_paths = rebuilt_scores[rebuilt_scores["candidate"] == "phi"]
    thalweg_phi = float(phi_paths.loc[phi_paths["elevation_rank"] == 1, "parent_score"].iloc[0])
    control = phi_paths.loc[phi_paths["elevation_rank"] > 1, "parent_score"].to_numpy(float)
    control_rank = int(1 + np.sum(control < thalweg_phi))
    check("T327 thalweg control rank", control_rank == result["thalweg"]["phi_control_rank_of_41"], control_rank, result["thalweg"]["phi_control_rank_of_41"])

    figure = HYDRO / f"{T327}_FIGURE.png"
    with Image.open(figure) as im:
        check("T327 figure dimensions", im.size == (1900, 1260), list(im.size), [1900, 1260])
    check("T327 formal verdict", result["verdict"] == "NOT SUPPORTED", result["verdict"], "NOT SUPPORTED")

    return {
        "verdict": result["verdict"],
        "local_winner": local_winner,
        "parent_winner": parent_winner,
        "shuffle_p_lower": p_lower,
        "phi_control_rank_of_41": control_rank,
    }


def main() -> None:
    t326 = validate_t326()
    t327 = validate_t327()
    failed = [item for item in checks if not item["passed"]]
    validation = {
        "validator": "independent rebuild; production modules not imported",
        "T326": t326,
        "T327": t327,
        "checks_total": len(checks),
        "checks_passed": len(checks) - len(failed),
        "checks_failed": len(failed),
        "status": "PASS" if not failed else "FAIL",
        "checks": checks,
    }
    output = HERE / "T326_T327_PHI_CIRCLE_TRAIN_VALIDATION.json"
    output.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: validation[key] for key in ("T326", "T327", "checks_total", "checks_passed", "checks_failed", "status")}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
