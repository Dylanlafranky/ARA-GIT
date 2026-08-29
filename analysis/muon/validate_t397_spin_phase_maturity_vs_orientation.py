#!/usr/bin/env python3
"""Independent arithmetic and claim-boundary audit for T397."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

import t382_ral_silver_traversal_child as base


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "T397_SPIN_PHASE_MATURITY_VS_ORIENTATION_PROTOCOL_2026-08-17.md"
OUT = HERE / "T397_spin_phase_maturity_vs_orientation"
RESULTS = OUT / "T397_RESULTS.json"
RUNS = OUT / "T397_RUN_SCORES.csv"
CONTROLS = OUT / "T397_WRONG_CADENCE_CONTROLS.csv"
BOOTSTRAP = OUT / "T397_BOOTSTRAP.csv"
SOURCE = OUT / "T397_SOURCE_MANIFEST.csv"
VALIDATION = OUT / "T397_VALIDATION.json"

TAU = 2.1928
GAMMA = 0.01382
T_MIN = 0.25
T_MAX = 8.0


def independently_recompute_w(record: dict, weights: np.ndarray) -> dict:
    full = np.sum(weights[:, None] * np.asarray(record["counts"], dtype=float), axis=0)
    background = float(full[record["background_mask"]].mean())
    mask = (record["time"] >= T_MIN) & (record["time"] < T_MAX)
    time = np.asarray(record["time"][mask], dtype=float)
    observed = full[mask]
    cycles = np.floor(GAMMA * float(record["field_g"]) * time).astype(int)
    train = cycles % 2 == 1
    test = ~train
    shape = np.exp(-time[train] / TAU)
    amplitude = base.fit_amplitude(observed[train], shape, background)
    parent = amplitude * np.exp(-time / TAU) + background
    theta = 2.0 * np.pi * GAMMA * float(record["field_g"]) * time
    x = parent[:, None] * np.c_[np.cos(theta), np.sin(theta)]
    xw = x[train] / np.sqrt(np.maximum(parent[train], 1.0))[:, None]
    yw = (observed[train] - parent[train]) / np.sqrt(np.maximum(parent[train], 1.0))
    beta, *_ = np.linalg.lstsq(xw, yw, rcond=None)
    prediction = parent + x @ beta
    null = float(np.sum((observed[test] - parent[test]) ** 2 / np.maximum(parent[test], 1.0)))
    phase = float(np.sum((observed[test] - prediction[test]) ** 2 / np.maximum(parent[test], 1.0)))
    return {
        "gain": 1.0 - phase / null,
        "amplitude": float(np.hypot(*beta)),
        "angle": float(np.mod(np.arctan2(beta[1], beta[0]), 2.0 * np.pi)),
    }


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    runs = pd.read_csv(RUNS)
    controls = pd.read_csv(CONTROLS)
    boot = pd.read_csv(BOOTSTRAP)
    source = pd.read_csv(SOURCE)
    checks: dict[str, bool] = {}

    checks["protocol_hash"] = hashlib.sha256(PROTOCOL.read_bytes()).hexdigest().upper() == result["protocol_sha256"]
    checks["all_source_quality"] = bool(source["all_quality_gates_pass"].astype(bool).all())
    checks["source_rows_11"] = len(source) == 11

    for channel in ["O", "U", "V", "W"]:
        rows = runs[(runs.score_family == "primary") & (runs.channel == channel) & (runs.run != "POOLED")]
        recomputed = 1.0 - rows.phase_sse.sum() / rows.null_sse.sum()
        checks[f"pooled_gain_{channel}"] = abs(recomputed - result["primary_pooled_gain"][channel]) < 1e-12
        ci = [float(boot[f"gain_{channel}"].quantile(0.025)), float(boot[f"gain_{channel}"].quantile(0.975))]
        checks[f"bootstrap_ci_{channel}"] = bool(np.allclose(ci, result["bootstrap_95_gain"][channel], atol=1e-12))

    primary_w = runs[(runs.score_family == "primary") & (runs.channel == "W") & (runs.run != "POOLED")]
    angles = primary_w.phase_angle_rad.to_numpy(dtype=float)
    resultant = abs(np.mean(np.exp(1j * angles)))
    checks["w_phase_resultant"] = abs(resultant - result["w_common_mode"]["phase_resultant_length"]) < 1e-12
    wrong_w = controls[(controls.channel == "W") & (controls.run == "POOLED")].gain.to_numpy(dtype=float)
    checks["wrong_w_97_5"] = abs(float(np.quantile(wrong_w, 0.975)) - result["w_common_mode"]["wrong_cadence_97_5_gain"]) < 1e-12

    calibration = [base.load_run(run, field, "calibration") for run, field in base.CALIBRATION.items()]
    detector_totals = np.zeros(96, dtype=float)
    for record in calibration:
        detector_totals += record["counts"][:, record["analysis_mask"]].sum(axis=1)
    shares = detector_totals / detector_totals.sum()
    weights = np.median(shares) / shares
    check_rows = []
    for run, field in base.HOLDOUT.items():
        record = base.load_run(run, field, "holdout")
        audit = independently_recompute_w(record, weights)
        recorded = primary_w.loc[primary_w.run == run].iloc[0]
        check_rows.append({
            "run": run,
            "gain_match": abs(audit["gain"] - float(recorded.gain)) < 1e-12,
            "amplitude_match": abs(audit["amplitude"] - float(recorded.phase_amplitude_fraction)) < 1e-12,
            "angle_match": abs(np.angle(np.exp(1j * (audit["angle"] - float(recorded.phase_angle_rad))))) < 1e-12,
        })
    checks["independent_w_raw_recompute"] = all(all(row[key] for key in ["gain_match", "amplitude_match", "angle_match"]) for row in check_rows)

    orientation_components = result["gates"]["orientation_components"]
    checks["orientation_gate_recomputed"] = result["gates"]["orientation_pass"] == all(orientation_components.values())
    maturity_components = result["gates"]["maturity_components"]
    checks["maturity_gate_recomputed"] = result["gates"]["maturity_pass"] == all(maturity_components.values())
    expected_status = (
        "POPULATION_SPIN_MATURITY_SUPPORTED_REPLICATION_REQUIRED"
        if result["gates"]["maturity_pass"] else
        "ORIENTATION_SUPPORTED_MATURITY_NOT_SUPPORTED"
        if result["gates"]["orientation_pass"] else
        "INCONCLUSIVE_ORIENTATION_POSITIVE_CONTROL_FAILED"
    )
    checks["status_matches_gates"] = result["status"] == expected_status
    boundary = result["claim_boundary"].lower()
    checks["claim_boundary_retained"] = all(term in boundary for term in ["population", "no individual", "neutrino"])

    checks = {key: bool(value) for key, value in checks.items()}
    check_rows = [{key: (bool(value) if key != "run" else value) for key, value in row.items()} for row in check_rows]
    payload = {
        "test": "T397 independent validation",
        "passed": all(checks.values()),
        "checks": checks,
        "independent_w_rows": check_rows,
        "assessment": "READY_TO_SHARE_WITH_CAVEATS" if all(checks.values()) else "NEEDS_REVISION",
        "required_caveats": [
            "The archive contains aggregate detector histograms, not individual parent-daughter records.",
            "The source was inspected in prior tests; T397 is a locked reanalysis, not a source-blind replication.",
            "The strict common-mode pooled gain is small and its cycle/field bootstrap interval crosses zero.",
        ],
    }
    VALIDATION.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not payload["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
