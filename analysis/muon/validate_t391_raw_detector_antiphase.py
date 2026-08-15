#!/usr/bin/env python3
"""Independent artifact and arithmetic checks for T391."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
OUT = HERE / "T391_raw_detector_antiphase"
RESULTS = OUT / "T391_RESULTS.json"
RUNS = OUT / "T391_RUN_SUMMARY.csv"
SHIFTS = OUT / "T391_TEMPORAL_SHIFT_CURVES.csv"
DETECTOR_SHIFTS = OUT / "T391_DETECTOR_SHIFT_CONTROLS.csv"
WRONG_CADENCE = OUT / "T391_WRONG_CADENCE_CONTROLS.csv"
PROFILES = OUT / "T391_RAW_PHASE_PROFILES.csv"
VALIDATION = OUT / "T391_VALIDATION.json"
PROTOCOL = HERE / "T391_RAW_DETECTOR_ANTIPHASE_PROTOCOL_2026-08-15.md"
SCRIPT = HERE / "t391_raw_detector_antiphase.py"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def error(target: np.ndarray, prediction: np.ndarray, weight: np.ndarray) -> float:
    return float(np.sqrt(np.sum(weight[:, None] * (target - prediction) ** 2) /
                         np.sum(weight[:, None] * target ** 2)))


def correlation(source: np.ndarray, target: np.ndarray, weight: np.ndarray) -> float:
    return float(np.sum(weight[:, None] * source * target) /
                 np.sqrt(np.sum(weight[:, None] * source ** 2) * np.sum(weight[:, None] * target ** 2)))


def main():
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    runs = pd.read_csv(RUNS)
    shifts = pd.read_csv(SHIFTS)
    detector_shifts = pd.read_csv(DETECTOR_SHIFTS)
    wrong = pd.read_csv(WRONG_CADENCE)
    profiles = pd.read_csv(PROFILES)
    holdout = runs[runs.split == "holdout"].copy()

    checks: dict[str, bool] = {}
    checks["all_expected_artifacts_nonempty"] = all(path.exists() and path.stat().st_size > 0 for path in
        [RESULTS, RUNS, SHIFTS, DETECTOR_SHIFTS, WRONG_CADENCE, PROFILES,
         OUT / "T391_RAW_DETECTOR_ANTIPHASE.svg", OUT / "T391_RAW_DETECTOR_ANTIPHASE_REPORT.html"])
    checks["protocol_hash_matches"] = results["protocol_sha256"] == sha256(PROTOCOL)
    checks["no_spatial_decoder_declared"] = results["frozen_calibration"]["spatial_decoder_used_in_primary_score"] is False
    script_text = SCRIPT.read_text(encoding="utf-8")
    checks["no_t389_projection_called"] = "project_record(" not in script_text and "child[\"beta\"]" not in script_text
    checks["three_holdouts"] = set(holdout.field_g) == {63.0, 160.0, 400.0}
    checks["forty_eight_phase_bins"] = bool((profiles.groupby("run").phase_turns.nunique() == 48).all())
    checks["ninety_six_detectors"] = bool((profiles.groupby("run").detector.nunique() == 96).all())
    checks["profile_share_closure"] = float(profiles.groupby(["run", "phase_turns"]).share_residual.sum().abs().max()) < 1e-12

    arithmetic_ok = True
    shift_logic_ok = True
    wrong_cadence_ok = True
    for row in holdout.itertuples():
        frame = profiles[profiles.run == row.run]
        matrix = frame.pivot(index="phase_turns", columns="detector", values="share_residual").sort_index().to_numpy()
        weights = frame.groupby("phase_turns").phase_bin_weight.first().sort_index().to_numpy()
        source, target = matrix[:24], matrix[24:]
        pair_weight = np.sqrt(weights[:24] * weights[24:])
        full = error(target, -source, pair_weight)
        direct = error(target, source, pair_weight)
        first = error(target, np.column_stack([-source[:, :48], source[:, 48:]]), pair_weight)
        second = error(target, np.column_stack([source[:, :48], -source[:, 48:]]), pair_weight)
        corr = correlation(source, target, pair_weight)
        values = [full, direct, first, second, corr]
        references = [row.error_full_inversion, row.error_direct_repeat, row.error_first_bank_only,
                      row.error_second_bank_only, row.half_turn_raw_correlation]
        arithmetic_ok &= bool(np.allclose(values, references, atol=2e-12, rtol=2e-12))

        detector_errors = np.asarray([error(target, -np.roll(source, k, axis=1), pair_weight) for k in range(96)])
        saved_shifts = detector_shifts[detector_shifts.run == row.run].sort_values("detector_label_shift").full_inversion_error.to_numpy()
        shift_logic_ok &= bool(np.allclose(detector_errors, saved_shifts, atol=2e-12, rtol=2e-12))
        shift_logic_ok &= bool(row.error_full_inversion < np.quantile(detector_errors[1:], 0.05))

        wrong_errors = wrong[wrong.run == row.run].full_inversion_error.to_numpy()
        wrong_cadence_ok &= bool(len(wrong_errors) == 2 and row.error_full_inversion < wrong_errors.min())
        curve = shifts[shifts.run == row.run]
        minimum = float(curve.loc[curve.raw_pattern_correlation.idxmin(), "turn_fraction"])
        shift_logic_ok &= abs(minimum - row.minimum_correlation_turn_fraction) < 1e-12

    checks["primary_arithmetic_recomputed"] = arithmetic_ok
    checks["detector_and_temporal_controls_recomputed"] = shift_logic_ok
    checks["wrong_cadence_gate_rechecked"] = wrong_cadence_ok

    recomputed = {
        "inversion_beats_mappings_every_field": bool((holdout.full_inversion_advantage > 0).all()),
        "negative_half_correlation_every_field": bool((holdout.half_turn_raw_correlation < 0).all()),
        "minimum_near_half_every_field": bool((np.abs(holdout.minimum_correlation_turn_fraction - 0.5) <= 0.05 + 1e-12).all()),
        "detector_labels_pass_every_field": bool((holdout.correct_beats_fraction_detector_shifts >= 0.95).all()),
        "cadence_control_pass_every_field": wrong_cadence_ok,
        "bootstrap_lower_above_zero": bool(results["bootstrap_95_advantage"][0] > 0),
    }
    checks["gate_values_match_results"] = all(results["gates"][name] == value for name, value in recomputed.items())
    checks["status_matches_all_gates"] = (results["status"] == "SUPPORTED") == all(recomputed.values())
    checks["claim_boundary_present"] = all(term in results["claim_boundary"] for term in ["population", "individual muons", "neutrinos"])

    validation = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks,
                  "max_profile_share_sum_abs": float(profiles.groupby(["run", "phase_turns"]).share_residual.sum().abs().max()),
                  "holdout_fields_g": sorted(holdout.field_g.tolist())}
    VALIDATION.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

