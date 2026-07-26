#!/usr/bin/env python3
"""Independent output and calculation checks for Q3 ridge-normal calibration."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "Q3_RIDGE_NORMAL_CUT_PROTOCOL_v1_FROZEN.md"
PROTOCOL_SHA = HERE / "Q3_RIDGE_NORMAL_CUT_PROTOCOL_v1_FROZEN.sha256"
FOLDS = HERE / "Q3_RIDGE_NORMAL_CUT_FOLDS.csv"
SWEEP = HERE / "Q3_RIDGE_NORMAL_CUT_SWEEP.csv"
RESULTS = HERE / "Q3_RIDGE_NORMAL_CUT_RESULTS.json"
VALIDATION = HERE / "Q3_RIDGE_NORMAL_CUT_VALIDATION.json"
ARCHIVE = HERE / "public_data" / "AllopticalSCQreadout_data.zip"
SOURCE_SHA256 = "73f3e2ca7b3658452b4c171532c751e96d7392dcb8741b87a18e28c7073d67fd"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tolerance)


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "detail": detail})

    expected_protocol_hash = PROTOCOL_SHA.read_text(encoding="utf-8").split()[0]
    actual_protocol_hash = sha256(PROTOCOL)
    check(
        "frozen protocol hash",
        actual_protocol_hash == expected_protocol_hash,
        actual_protocol_hash,
    )
    check(
        "public source checksum",
        ARCHIVE.exists() and sha256(ARCHIVE) == SOURCE_SHA256,
        sha256(ARCHIVE) if ARCHIVE.exists() else "archive absent",
    )

    with FOLDS.open(encoding="utf-8", newline="") as handle:
        folds = list(csv.DictReader(handle))
    with SWEEP.open(encoding="utf-8", newline="") as handle:
        sweep = list(csv.DictReader(handle))
    results = json.loads(RESULTS.read_text(encoding="utf-8"))

    check("six whole-condition folds", len(folds) == 6, str(len(folds)))
    check("180 sweep angles per fold", len(sweep) == 6 * 180, str(len(sweep)))

    phase_a_ba = [float(row["phase_a_ba"]) for row in folds]
    phase_b_ba = [float(row["phase_b_control_ba"]) for row in folds]
    raw_ba = [float(row["raw_iq_lda_ba"]) for row in folds]
    shares = [float(row["phase_a_separation_share"]) for row in folds]
    residuals = [float(row["training_tangent_residual"]) for row in folds]
    total_disagreements = sum(
        int(row["phase_a_raw_disagreements"]) for row in folds
    )
    total_reversal_disagreements = sum(
        int(row["pole_reversal_disagreements"]) for row in folds
    )

    overall = results["overall"]
    check(
        "Phase-A balanced accuracy recomputed",
        close(sum(phase_a_ba) / 6, float(overall["phase_a_ba"])),
        f"{sum(phase_a_ba) / 6:.15f}",
    )
    check(
        "Phase-B balanced accuracy recomputed",
        close(sum(phase_b_ba) / 6, float(overall["phase_b_control_ba"])),
        f"{sum(phase_b_ba) / 6:.15f}",
    )
    check(
        "raw LDA balanced accuracy recomputed",
        close(sum(raw_ba) / 6, float(overall["raw_iq_lda_ba"])),
        f"{sum(raw_ba) / 6:.15f}",
    )
    check(
        "mean separation share recomputed",
        close(sum(shares) / 6, float(overall["mean_phase_a_separation_share"])),
        f"{sum(shares) / 6:.15f}",
    )
    check(
        "worst separation share recomputed",
        close(min(shares), float(overall["worst_phase_a_separation_share"])),
        f"{min(shares):.15f}",
    )
    check(
        "training tangent residual recomputed",
        close(max(residuals), float(overall["max_training_tangent_residual"])),
        f"{max(residuals):.3e}",
    )
    check(
        "Phase-A/raw disagreements total",
        total_disagreements == int(overall["phase_a_raw_disagreements"]) == 0,
        str(total_disagreements),
    )
    check(
        "pole reversal disagreements total",
        total_reversal_disagreements
        == int(overall["pole_reversal_disagreements"])
        == 0,
        str(total_reversal_disagreements),
    )

    share_formulas_ok = True
    angle_formulas_ok = True
    for row in folds:
        d_a = float(row["target_d_phase_a"])
        d_b = float(row["target_d_phase_b"])
        expected_share = d_a * d_a / (d_a * d_a + d_b * d_b)
        expected_angle = math.degrees(math.atan2(d_b, d_a))
        share_formulas_ok &= close(
            expected_share, float(row["phase_a_separation_share"])
        )
        angle_formulas_ok &= close(
            expected_angle, float(row["target_separation_angle_degrees"])
        )
    check("separation-share formulas", share_formulas_ok, "all six folds")
    check("held-out angle formulas", angle_formulas_ok, "all six folds")

    sweep_by_condition: dict[int, list[dict[str, str]]] = {}
    for row in sweep:
        condition = int(row["held_out_condition_hz"])
        sweep_by_condition.setdefault(condition, []).append(row)
    sweep_coverage_ok = all(
        sorted(int(row["angle_from_phase_a_degrees"]) for row in rows)
        == list(range(180))
        for rows in sweep_by_condition.values()
    )
    sweep_best_ok = True
    for fold in folds:
        condition = int(fold["held_out_condition_hz"])
        rows = sweep_by_condition[condition]
        best = max(
            rows,
            key=lambda row: (
                float(row["balanced_accuracy"]),
                -int(row["angle_from_phase_a_degrees"]),
            ),
        )
        sweep_best_ok &= int(best["angle_from_phase_a_degrees"]) == int(
            fold["best_sweep_angle_degrees"]
        )
        sweep_best_ok &= close(
            float(best["balanced_accuracy"]), float(fold["best_sweep_ba"])
        )
    check("sweep angle coverage", sweep_coverage_ok, "0 through 179 in every fold")
    check("descriptive sweep maxima", sweep_best_ok, "all six folds")

    recomputed_gate_passes = {
        "C1_phase_a_equals_raw_lda": total_disagreements == 0,
        "C2_phase_a_ba_at_least_0p80": sum(phase_a_ba) / 6 >= 0.80,
        "C3_phase_b_control_between_0p40_and_0p60": 0.40
        <= sum(phase_b_ba) / 6
        <= 0.60,
        "C4_mean_phase_a_share_at_least_0p90": sum(shares) / 6 >= 0.90,
        "C5_worst_phase_a_share_at_least_0p75": min(shares) >= 0.75,
        "C6_training_tangent_residual_at_most_1e_12": max(residuals) <= 1e-12,
        "C7_pole_reversal_invariant": total_reversal_disagreements == 0,
    }
    recorded_gate_passes = {
        name: bool(gate["pass"]) for name, gate in results["gates"].items()
    }
    check(
        "gate verdicts independently recomputed",
        recomputed_gate_passes == recorded_gate_passes,
        f"{sum(recomputed_gate_passes.values())}/7",
    )
    check(
        "verdict follows gates",
        results["verdict"] == "CALIBRATED"
        and all(recomputed_gate_passes.values()),
        results["verdict"],
    )

    passed = sum(int(item["pass"]) for item in checks)
    output = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
        "review_boundary": (
            "Calculation and artifact consistency only. Q3 remains a post-hoc "
            "known-source calibration, and the Phase-A/LDA equality is expected algebra."
        ),
    }
    VALIDATION.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2))
    if output["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
