#!/usr/bin/env python3
"""Independent artifact and arithmetic checks for T389 and T390."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def main():
    checks = {}
    r389_path = HERE / "T389_spin_antiphase_diara" / "T389_RESULTS.json"
    r390_path = HERE / "T390_7p5_spin_release" / "T390_RESULTS.json"
    r389 = json.loads(r389_path.read_text(encoding="utf-8"))
    r390 = json.loads(r390_path.read_text(encoding="utf-8"))

    p389 = HERE / "T389_SPIN_ANTIPHASE_DIARA_PROTOCOL_2026-08-15.md"
    p390 = HERE / "T390_7P5_SPIN_RELEASE_PROTOCOL_2026-08-15.md"
    checks["t389_protocol_hash"] = sha256(p389) == r389["protocol_sha256"]
    checks["t390_protocol_hash"] = sha256(p390) == r390["protocol_sha256"]

    runs = pd.read_csv(HERE / "T389_spin_antiphase_diara" / "T389_RUN_SUMMARY.csv")
    hold = runs[runs.split == "holdout"].copy()
    checks["t389_three_holdouts"] = len(hold) == 3 and set(hold.field_g) == {63.0, 160.0, 400.0}
    checks["t389_inversion_advantage_recomputed"] = bool((hold.full_inversion_advantage > 0).all())
    checks["t389_negative_half_correlation_recomputed"] = bool((hold.half_turn_correlation_real < 0).all())
    checks["t389_minimum_near_half_recomputed"] = bool((np.abs(hold.minimum_correlation_turn_fraction - 0.5) <= 0.05 + 1e-12).all())
    checks["t389_pooled_advantage_recomputed"] = bool(np.isclose(
        hold.full_inversion_advantage.mean(), r389["pooled_full_inversion_advantage"], rtol=0, atol=1e-12))
    checks["t389_gate_consistency"] = bool(
        r389["gates"]["inversion_beats_controls_every_field"] == checks["t389_inversion_advantage_recomputed"] and
        r389["gates"]["negative_half_correlation_every_field"] == checks["t389_negative_half_correlation_recomputed"] and
        r389["gates"]["minimum_near_half_every_field"] == checks["t389_minimum_near_half_recomputed"] and
        r389["gates"]["bootstrap_advantage_lower_above_zero"] == (r389["bootstrap_95_full_inversion_advantage"][0] > 0))

    fields = pd.read_csv(HERE / "T390_7p5_spin_release" / "T390_FIELD_DETAILS.csv")
    landmarks = pd.read_csv(HERE / "T390_7p5_spin_release" / "T390_HALF_INTEGER_LANDMARKS.csv")
    controls = pd.read_csv(HERE / "T390_7p5_spin_release" / "T390_CONTROL_SCORES.csv")
    boot = pd.read_csv(HERE / "T390_7p5_spin_release" / "T390_DETECTOR_BOOTSTRAP.csv")
    ratio = fields.observed_counts.sum() / fields.expected_counts.sum()
    candidate_row = landmarks[np.isclose(landmarks.turns, 7.5)].iloc[0]
    other_max = landmarks.loc[~np.isclose(landmarks.turns, 7.5), "observed_expected_ratio"].max()
    control_975 = float(np.quantile(controls.observed_expected_ratio, 0.975))
    boot_ci = [float(np.quantile(boot.excess_ratio, 0.025)), float(np.quantile(boot.excess_ratio, 0.975))]
    checks["t390_three_holdouts"] = len(fields) == 3 and set(fields.field_g) == {63.0, 160.0, 400.0}
    checks["t390_ratio_recomputed"] = bool(np.isclose(ratio, r390["candidate_7p5"]["observed_expected_ratio"], atol=1e-12))
    checks["t390_landmark_ratio_consistent"] = bool(np.isclose(candidate_row.observed_expected_ratio, ratio, atol=1e-12))
    checks["t390_other_max_recomputed"] = bool(np.isclose(other_max, r390["other_half_integer_max_ratio"], atol=1e-12))
    checks["t390_control_quantile_recomputed"] = bool(np.isclose(control_975, r390["control_97_5_ratio"], atol=1e-12))
    checks["t390_bootstrap_ci_recomputed"] = bool(np.allclose(boot_ci, r390["detector_bootstrap_95_excess_ratio"], atol=1e-12))
    gate_recomputed = {
        "candidate_ratio_above_one": ratio > 1,
        "beats_other_half_integers": ratio > other_max,
        "beats_control_97_5": ratio > control_975,
        "positive_each_field": bool((fields.mean_pearson_residual > 0).all()),
        "bootstrap_excess_lower_above_zero": boot_ci[0] > 0,
    }
    checks["t390_gate_consistency"] = all(r390["gates"][name] == value for name, value in gate_recomputed.items())

    for test, path, required in [
        ("t389", HERE / "T389_spin_antiphase_diara" / "T389_SPIN_ANTIPHASE_DIARA.svg",
         ["Two measured spin quadratures", "Half-turn mapping error", "Frozen gates"]),
        ("t390", HERE / "T390_7p5_spin_release" / "T390_7P5_SPIN_RELEASE.svg",
         ["Summed release residuals", "Same-family half-integer landmarks", "Frozen gates"]),
    ]:
        root = ET.parse(path).getroot()
        text = " ".join(element.text or "" for element in root.iter())
        checks[f"{test}_svg_parse"] = root.tag.endswith("svg") and root.attrib.get("width") == "1600"
        checks[f"{test}_svg_labels"] = all(label in text for label in required)

    passed = all(checks.values())
    output = {"passed": passed, "checks": checks}
    out_path = HERE / "T389_T390_VALIDATION.json"
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

