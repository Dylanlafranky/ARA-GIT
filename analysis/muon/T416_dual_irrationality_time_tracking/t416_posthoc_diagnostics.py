#!/usr/bin/env python3
"""Labelled post-result summaries for interpreting the frozen T416 outcome."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"empty output: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def f(row: dict, key: str) -> float:
    return float(row[key])


def parent_profiles(rows: list[dict]) -> list[dict]:
    output = []
    for period in ("RF on", "RF off"):
        part = [row for row in rows if row["period"] == period]
        for index in range(10):
            low, high = 0.2 * index, 0.2 * (index + 1)
            selected = [
                row for row in part
                if f(row, "parent_ARA") >= low and (f(row, "parent_ARA") < high or (index == 9 and f(row, "parent_ARA") <= high))
            ]
            if not selected:
                continue
            record = {
                "period": period,
                "parent_bin": index + 1,
                "parent_ARA_mid": 0.5 * (low + high),
                "parent_ARA_observed_median": float(np.median([f(row, "parent_ARA") for row in selected])),
                "state_x_L_median": float(np.median([f(row, "state_x_L") for row in selected])),
                "state_x_C_median": float(np.median([f(row, "state_x_C") for row in selected])),
                "history_x_P_median": float(np.median([f(row, "history_x_P") for row in selected])),
                "history_x_R_median": float(np.median([f(row, "history_x_R") for row in selected])),
                "closure_rho_median": float(np.median([f(row, "median_closure_rho") for row in selected])),
                "x_R_below_1_99_share": float(np.mean([f(row, "history_x_R") < 1.99 for row in selected])),
                "rows": len(selected),
                "fields": len({row["field_G"] for row in selected}),
            }
            output.append(record)
    return output


def occupancy(rows: list[dict]) -> list[dict]:
    output = []
    for period in ("RF on", "RF off"):
        part = [row for row in rows if row["period"] == period]
        for instrument, field in (("State Di-ARA", "state_sector"), ("History Di-ARA", "history_sector")):
            counts = Counter(row[field] for row in part)
            for name in ("Ba", "Ab", "bA", "aB", "ridge"):
                output.append({
                    "period": period,
                    "instrument": instrument,
                    "sector": name,
                    "windows": counts.get(name, 0),
                    "share": counts.get(name, 0) / len(part),
                })
    return output


def field_controls(rows: list[dict]) -> list[dict]:
    output = []
    for row in rows:
        output.append({
            "run": row["run"],
            "period": row["period"],
            "field_G": f(row, "field_G"),
            "shuffle_minus_target_x_R": f(row, "shuffle_x_R") - f(row, "target_x_R"),
            "wrong_minus_target_x_R": f(row, "wrong_x_R") - f(row, "target_x_R"),
            "target_minus_shuffle_closure_rho": f(row, "target_rho") - f(row, "shuffle_rho"),
            "abs_shuffle_minus_target_x_P": abs(f(row, "shuffle_x_P") - f(row, "target_x_P")),
            "median_state_x_L": f(row, "median_state_x_L"),
            "median_state_x_C": f(row, "median_state_x_C"),
            "median_history_x_P": f(row, "median_history_x_P"),
            "median_history_x_R": f(row, "median_history_x_R"),
            "calibration_improvement": f(row, "calibration_improvement"),
        })
    return output


def example(rows: list[dict]) -> list[dict]:
    return [
        {
            "period": row["period"],
            "field_G": f(row, "field_G"),
            "time_us": f(row, "time_us"),
            "parent_ARA": f(row, "parent_ARA"),
            "state_x_L": f(row, "state_x_L"),
            "state_x_C": f(row, "state_x_C"),
            "history_x_P": f(row, "history_x_P"),
            "history_x_R": f(row, "history_x_R"),
            "median_closure_rho": f(row, "median_closure_rho"),
            "observed_phase_ARA": f(row, "observed_phase_ARA"),
            "state_sector": row["state_sector"],
            "history_sector": row["history_sector"],
        }
        for row in rows
        if row["run"] == "EMU00070022"
    ]


def main() -> None:
    timeline = read_csv(RESULTS / "T416_VALIDATION_TIMELINE.csv")
    summary = read_csv(RESULTS / "T416_VALIDATION_RUN_PERIOD_SUMMARY.csv")
    profiles = parent_profiles(timeline)
    sectors = occupancy(timeline)
    controls = field_controls(summary)
    example_rows = example(timeline)
    write_csv(RESULTS / "T416_POSTHOC_PARENT_PROFILES.csv", profiles)
    write_csv(RESULTS / "T416_POSTHOC_SECTOR_OCCUPANCY.csv", sectors)
    write_csv(RESULTS / "T416_POSTHOC_FIELD_CONTROLS.csv", controls)
    write_csv(RESULTS / "T416_EXAMPLE_284G_TIMELINE.csv", example_rows)
    payload = {
        "status": "labelled post-result diagnostics; does not alter frozen gates",
        "parent_profiles": len(profiles),
        "sector_rows": len(sectors),
        "field_control_rows": len(controls),
        "example_rows": len(example_rows),
        "target_x_R_ceiling_share": float(np.mean([f(row, "history_x_R") >= 1.999999 for row in timeline])),
        "state_x_L_ridge_band_share": float(np.mean([abs(f(row, "state_x_L") - 1.0) <= 0.10 for row in timeline])),
        "history_x_P_open_side_share": float(np.mean([f(row, "history_x_P") > 1.0 for row in timeline])),
        "state_forward_side_share": float(np.mean([f(row, "state_x_C") > 1.0 for row in timeline])),
    }
    (RESULTS / "T416_POSTHOC_DIAGNOSTICS.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
