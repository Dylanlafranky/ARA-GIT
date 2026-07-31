#!/usr/bin/env python3
"""Independent output and formula checks for T308."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_RESULTS.json"
ROWS = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_ROWS.csv"
VALIDATION = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_VALIDATION.json"
PROTOCOL = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_PROTOCOL_v1_FROZEN.md"
FIGURE = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE.png"
REPORT = HERE / "T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_REPORT_2026-07-31.md"


def check(name: str, condition: bool, detail: str) -> dict:
    return {"name": name, "passed": bool(condition), "detail": detail}


def main() -> None:
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    rows = pd.read_csv(ROWS)
    checks = []

    checks.append(check("protocol_exists", PROTOCOL.exists(), str(PROTOCOL)))
    checks.append(check("report_exists", REPORT.exists(), str(REPORT)))
    checks.append(
        check(
            "figure_exists",
            FIGURE.exists() and FIGURE.stat().st_size > 50_000,
            f"{FIGURE.stat().st_size if FIGURE.exists() else 0} bytes",
        )
    )
    checks.append(
        check(
            "declared_systems",
            set(rows["system"]) == {"moon_earth", "earth_sun"},
            str(sorted(rows["system"].unique())),
        )
    )
    checks.append(
        check(
            "declared_halves",
            set(rows["half"]) == {"calibration", "evaluation"},
            str(sorted(rows["half"].unique())),
        )
    )
    checks.append(
        check(
            "declared_candidates",
            set(rows["candidate"])
            == {"1.25", "sqrt2", "1.5", "phi", "1.75", "2", "e"},
            str(sorted(rows["candidate"].unique())),
        )
    )
    checks.append(
        check(
            "declared_horizons",
            set(np.round(rows["horizon_ratio"].unique(), 6))
            == {0.25, 0.375, 0.5, 0.75, 1.0, 1.5, 2.0},
            str(sorted(rows["horizon_ratio"].unique())),
        )
    )
    checks.append(
        check(
            "finite_metrics",
            np.isfinite(
                rows[
                    [
                        "phase_abs_error",
                        "ara_abs_error",
                        "curvature_norm_error",
                        "branch_match",
                    ]
                ].to_numpy()
            ).all(),
            f"{len(rows):,} scored rows",
        )
    )

    # Independent spot-check of the frozen relation and ARA projection.
    sample = rows.iloc[len(rows) // 3]
    qhat = sample["q2"] + sample["lambda"] * (sample["q2"] - sample["q1"])
    xhat = 1.0 - math.cos(qhat)
    phase_error = abs(qhat - sample["q3_true"])
    ara_error = abs(xhat - sample["x3_true"])
    denom = (
        (sample["horizon_days"] - sample["horizon_days"] / sample["lambda"] ** 2)
        * (sample["horizon_days"] - sample["horizon_days"] / sample["lambda"])
    )
    curvature = phase_error / denom
    checks.append(
        check(
            "frozen_formula_spot_check",
            math.isclose(qhat, sample["q3_pred"], rel_tol=0, abs_tol=1e-12)
            and math.isclose(xhat, sample["x3_pred"], rel_tol=0, abs_tol=1e-12)
            and math.isclose(
                phase_error, sample["phase_abs_error"], rel_tol=0, abs_tol=1e-12
            )
            and math.isclose(
                ara_error, sample["ara_abs_error"], rel_tol=0, abs_tol=1e-12
            )
            and math.isclose(
                curvature,
                sample["curvature_norm_error"],
                rel_tol=0,
                abs_tol=1e-12,
            ),
            f"row index {len(rows) // 3}",
        )
    )

    # Recompute fixed-candidate evaluation ranks without using saved summary.
    recomputed = (
        rows[rows["half"] == "evaluation"]
        .groupby(["system", "candidate"])["curvature_norm_error"]
        .median()
        .reset_index()
    )
    saved_summary = pd.DataFrame(results["summary"])
    saved_eval = saved_summary[saved_summary["half"] == "evaluation"]
    merged = recomputed.merge(
        saved_eval[["system", "candidate", "median_curvature_error"]],
        on=["system", "candidate"],
        how="inner",
    )
    rank_match = len(merged) == 14 and np.allclose(
        merged["curvature_norm_error"],
        merged["median_curvature_error"],
        rtol=0,
        atol=1e-15,
    )
    checks.append(
        check(
            "summary_recomputed",
            rank_match,
            f"{len(merged)}/14 candidate-system rows reconciled",
        )
    )

    source_checks = []
    for system in ["moon_earth", "earth_sun"]:
        raw = HERE / "data" / "t308" / f"{system}_horizons_raw.txt"
        parsed = HERE / "data" / "t308" / f"{system}_vectors.csv"
        raw_text = raw.read_text(encoding="utf-8") if raw.exists() else ""
        parsed_rows = len(pd.read_csv(parsed)) if parsed.exists() else 0
        okay = (
            "$$SOE" in raw_text
            and "$$EOE" in raw_text
            and "GEOMETRIC cartesian states" in raw_text
            and "Reference frame : Ecliptic of J2000.0" in raw_text
            and parsed_rows >= 9000
        )
        source_checks.append(okay)
        checks.append(
            check(
                f"source_{system}",
                okay,
                f"raw markers and metadata present; parsed rows={parsed_rows}",
            )
        )

    passed = all(item["passed"] for item in checks)
    validation = {
        "test": "T308",
        "passed": passed,
        "checks_passed": sum(item["passed"] for item in checks),
        "checks_total": len(checks),
        "checks": checks,
    }
    VALIDATION.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

