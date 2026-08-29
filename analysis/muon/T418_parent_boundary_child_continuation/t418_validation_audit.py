#!/usr/bin/env python3
"""Independent file-level audit for T418 saved outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PROTOCOL = HERE / "T418_FROZEN_PROTOCOL.md"
ANALYSIS = HERE / "t418_parent_boundary_child_continuation.py"
FREEZE = HERE / "T418_DEVELOPMENT_FREEZE.json"
EPS = 1e-12
BOOTSTRAPS = 10000
SEED = 418


def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def field_values(rows: list[dict], key: str) -> dict[float, float]:
    output = {}
    for field in sorted({float(row["field_G"]) for row in rows}):
        values = [float(row[key]) for row in rows if float(row["field_G"]) == field]
        output[field] = float(np.median(values))
    return output


def bootstrap(values: dict[float, float], seed: int) -> tuple[float, float, float]:
    data = np.asarray([values[field] for field in sorted(values)], dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(data, size=(BOOTSTRAPS, len(data)), replace=True)
    medians = np.median(draws, axis=1)
    return float(np.median(data)), float(np.percentile(medians, 2.5)), float(np.percentile(medians, 97.5))


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return bool(abs(a - b) <= tolerance * max(1.0, abs(a), abs(b)))


def audit_stage(stage: str) -> dict:
    prefix = f"T418_{stage.upper()}"
    timeline = load_csv(RESULTS / f"{prefix}_TIMELINE.csv")
    predictions = load_csv(RESULTS / f"{prefix}_PREDICTION_ROWS.csv")
    eligibility = load_csv(RESULTS / f"{prefix}_SEQUENCE_ELIGIBILITY.csv")
    sequences = load_csv(RESULTS / f"{prefix}_SEQUENCE_METRICS.csv")
    shifts = load_csv(RESULTS / f"{prefix}_SHIFT_NULL.csv")
    result = json.loads((RESULTS / f"{prefix}_RESULTS.json").read_text(encoding="utf-8"))

    geometry_errors = []
    for row in timeline:
        local = float(row["local_loss"])
        null = float(row["null_loss"])
        q = local / max(null, EPS)
        child = 2.0 * local / max(local + null, EPS)
        parent_i = 2.0 * min(1.0, q)
        r = float(row["rational_closure_R"])
        a = float(row["coupled_amount_A"])
        b = float(row["coupled_balance_B"])
        checks = (
            close(q, float(row["raw_loss_ratio_q"])),
            close(child, float(row["child_x"])),
            close(child + float(row["child_anti_x"]), 2.0),
            close(parent_i, float(row["irrational_parent_I"])),
            close(a * b, parent_i),
            close(a * (2.0 - b), r),
        )
        if not all(checks):
            geometry_errors.append((row["run"], row["period"], row["time_us"], checks))

    prediction_checks = []
    for row in predictions:
        actual = np.asarray([float(row["future_state_x_L"]), float(row["future_state_x_C"])])
        base = np.asarray([float(row["baseline_pred_x_L"]), float(row["baseline_pred_x_C"])])
        child = np.asarray([float(row["child_pred_x_L"]), float(row["child_pred_x_C"])])
        wrong = np.asarray([float(row["wrong_pred_x_L"]), float(row["wrong_pred_x_C"])])
        prediction_checks.append(
            close(float(np.mean((base - actual) ** 2)), float(row["baseline_error"]))
            and close(float(np.mean((child - actual) ** 2)), float(row["child_error"]))
            and close(float(np.mean((wrong - actual) ** 2)), float(row["wrong_error"]))
            and float(row["raw_loss_ratio_q"]) >= 1.0 if "raw_loss_ratio_q" in row else True
        )

    available = sum(int(row["eligible"]) for row in eligibility)
    availability = available / len(eligibility)
    baseline = bootstrap(field_values(sequences, "baseline_minus_child"), SEED + 1)
    wrong = bootstrap(field_values(sequences, "wrong_minus_child"), SEED + 2)
    reverse = bootstrap(field_values(sequences, "reverse_minus_child"), SEED + 3)
    child_mse = float(np.median(list(field_values(sequences, "child_mse").values())))
    null = np.asarray([float(row["shifted_child_mse"]) for row in shifts], dtype=float)
    shift_p = float((1 + np.count_nonzero(null <= child_mse)) / (1 + len(null)))

    recomputed = {
        "availability": availability,
        "baseline_effect": baseline,
        "wrong_effect": wrong,
        "reverse_effect": reverse,
        "child_mse": child_mse,
        "shift_p": shift_p,
    }
    result_matches = (
        close(availability, float(result["availability_fraction"]))
        and close(baseline[0], float(result["gates"]["G2_added_future_state_information"]["value"]))
        and close(wrong[0], float(result["gates"]["G4_frequency_specificity"]["value"]))
        and close(reverse[0], float(result["gates"]["G5_direction_specificity"]["value"]))
        and close(child_mse, float(result["errors"]["child_mse"]))
        and close(shift_p, float(result["gates"]["G3_timing_specificity"]["empirical_p"]))
    )

    checks = {
        "protocol_hash_matches": result["protocol_sha256"] == sha256(PROTOCOL),
        "analysis_hash_matches": result["analysis_sha256"] == sha256(ANALYSIS),
        "development_freeze_exists": FREEZE.exists(),
        "geometry_exact_for_every_timeline_row": len(geometry_errors) == 0,
        "prediction_errors_recompute": all(prediction_checks),
        "saved_summary_recomputes": result_matches,
        "all_prediction_origins_precede_targets": all(
            float(row["future_time_us"]) > float(row["time_us"])
            for row in predictions
        ),
        "rf_boundaries_not_joined": all(row["period"] in {"RF on", "RF off"} for row in predictions),
        "no_null_loss_denominator_collapse": all(float(row["null_loss"]) > EPS for row in timeline),
    }
    return {
        "stage": stage,
        "checks": checks,
        "all_checks_pass": bool(all(checks.values())),
        "row_counts": {
            "timeline": len(timeline),
            "predictions": len(predictions),
            "sequences": len(sequences),
            "shift_draws": len(shifts),
        },
        "recomputed": recomputed,
        "geometry_error_examples": geometry_errors[:5],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "validation", "holdout", "all"), default="all")
    args = parser.parse_args()
    stages = ("development", "validation", "holdout") if args.stage == "all" else (args.stage,)
    output = {stage: audit_stage(stage) for stage in stages}
    output["all_stages_pass"] = all(item["all_checks_pass"] for item in output.values())
    write_path = RESULTS / "T418_VALIDATION_AUDIT.json"
    write_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
