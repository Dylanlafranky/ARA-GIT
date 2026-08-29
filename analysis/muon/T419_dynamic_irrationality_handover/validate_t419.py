#!/usr/bin/env python3
"""Independent saved-artifact validation for T419."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
PROTOCOL = HERE / "T419_FROZEN_PROTOCOL.md"
ANALYSIS = HERE / "t419_dynamic_irrationality_handover.py"
FREEZE = HERE / "T419_DEVELOPMENT_FREEZE.json"
STAGES = ("DEVELOPMENT", "VALIDATION", "HOLDOUT")
ARMS = ("U_to_R", "R_to_U")
TOL = 1e-12


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def field_median(rows: list[dict], key: str) -> float:
    values = []
    fields = sorted({float(row["field_G"]) for row in rows})
    for field in fields:
        selected = [float(row[key]) for row in rows if float(row["field_G"]) == field]
        values.append(float(np.median(selected)))
    return float(np.median(values))


def close(a: float, b: float) -> bool:
    return bool(abs(a - b) <= TOL * max(1.0, abs(a), abs(b)))


def main() -> None:
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    checks: list[dict] = []
    checks.append({"check": "freeze protocol hash", "pass": frozen["protocol_sha256"] == sha256(PROTOCOL)})
    checks.append({"check": "freeze analysis hash", "pass": frozen["analysis_sha256"] == sha256(ANALYSIS)})

    for stage in STAGES:
        result = json.loads((RESULTS / f"T419_{stage}_RESULTS.json").read_text(encoding="utf-8"))
        predictions = load_csv(RESULTS / f"T419_{stage}_PREDICTION_ROWS.csv")
        sequences = load_csv(RESULTS / f"T419_{stage}_SEQUENCE_METRICS.csv")
        eligibility = load_csv(RESULTS / f"T419_{stage}_SEQUENCE_ELIGIBILITY.csv")
        timeline = load_csv(RESULTS / f"T419_{stage}_TIMELINE.csv")

        checks.append({
            "check": f"{stage} source-target histories do not overlap",
            "pass": all(int(row["shared_native_bins"]) == 0 for row in predictions),
        })
        checks.append({
            "check": f"{stage} primary horizon is 128 native bins",
            "pass": all(int(row["horizon_native_bins"]) == 128 for row in predictions),
        })
        checks.append({
            "check": f"{stage} all sequences eligible",
            "pass": len(eligibility) == result["run_period_sequences"] and all(int(row["eligible"]) == 1 for row in eligibility),
        })
        u = np.asarray([float(row["openness_U"]) for row in timeline])
        r = np.asarray([float(row["closure_R"]) for row in timeline])
        checks.append({
            "check": f"{stage} U and R are not forced complements",
            "pass": bool(np.std(u + r) > 1e-3 and not np.allclose(u + r, 2.0)),
            "sum_std": float(np.std(u + r)),
        })
        for arm in ARMS:
            selected = [row for row in sequences if row["arm"] == arm]
            saved = result["arms"][arm]["errors"]
            for csv_key, result_key in (
                ("baseline_mse", "baseline_mse"),
                ("transfer_mse", "transfer_mse"),
                ("wrong_mse", "wrong_frequency_mse"),
                ("reverse_mse", "reverse_mse"),
            ):
                recomputed = field_median(selected, csv_key)
                checks.append({
                    "check": f"{stage} {arm} {result_key} recomputes",
                    "pass": close(recomputed, float(saved[result_key])),
                    "recomputed": recomputed,
                    "saved": float(saved[result_key]),
                })
            period_effects = result["arms"][arm]["effects"]["rf_baseline_minus_transfer"]
            for period in ("RF on", "RF off"):
                recomputed = float(np.median([
                    float(row["baseline_minus_transfer"])
                    for row in selected if row["period"] == period
                ]))
                checks.append({
                    "check": f"{stage} {arm} {period} effect recomputes",
                    "pass": close(recomputed, float(period_effects[period])),
                    "recomputed": recomputed,
                    "saved": float(period_effects[period]),
                })

    failed = [item for item in checks if not item["pass"]]
    output = {
        "test": "T419 independent saved-artifact validation",
        "checks": len(checks),
        "failed_checks": len(failed),
        "all_pass": not failed,
        "details": checks,
    }
    (RESULTS / "T419_INDEPENDENT_VALIDATION.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

