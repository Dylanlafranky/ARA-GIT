#!/usr/bin/env python3
"""Independent validation checks for T414 outputs."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MUON = HERE.parent
T413 = MUON / "T413_live_state_handover"
RESULTS = HERE / "results"
sys.path.insert(0, str(MUON / "_vendor"))
from pyhdf.SD import SD, SDC


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tolerance: float = 1e-10) -> bool:
    return abs(a - b) <= tolerance * max(1.0, abs(a), abs(b))


def main() -> None:
    checks: dict[str, bool] = {}
    notes: dict[str, object] = {}

    protocol_hash = sha256(HERE / "T414_FROZEN_PROTOCOL.md")
    freeze = json.loads((HERE / "T414_PREVALIDATION_FREEZE.json").read_text(encoding="utf-8"))
    preholdout = json.loads((HERE / "T414_PREHOLDOUT_FREEZE.json").read_text(encoding="utf-8"))
    checks["protocol_hash_matches_freeze"] = protocol_hash == freeze["protocol"]["sha256"]
    checks["analysis_code_matches_both_freezes"] = (
        sha256(HERE / "t414_spin_child_lifespan_parent.py") == freeze["analysis_code"]["sha256"]
        == preholdout["analysis_code"]["sha256"]
    )
    checks["sealed_validation_result_matches_freeze"] = (
        sha256(RESULTS / "T414_VALIDATION_RESULTS.json") == preholdout["validation_result"]["sha256"]
    )

    full = json.loads((RESULTS / "T414_FULL_RESULTS.json").read_text(encoding="utf-8"))
    metrics = read_csv(RESULTS / "T414_FULL_RUN_PERIOD_METRICS.csv")
    profiles = read_csv(RESULTS / "T414_FULL_RUN_PHASE_PROFILES.csv")
    tau_curve = read_csv(RESULTS / "T414_FULL_TAU_CALIBRATION.csv")
    source_hashes = read_csv(RESULTS / "T414_FULL_SOURCE_HASHES.csv")

    checks["92_unique_run_period_rows"] = len(metrics) == 92 and len({(r["run"], r["period"]) for r in metrics}) == 92
    counts = {split: len({r["run"] for r in metrics if r["split"] == split}) for split in ("development", "validation", "holdout")}
    checks["split_run_counts_13_13_20"] = counts == {"development": 13, "validation": 13, "holdout": 20}
    notes["split_run_counts"] = counts

    tau_rows = [(float(r["tau_us"]), float(r["objective"])) for r in tau_curve]
    tau_min = min(tau_rows, key=lambda row: row[1])[0]
    checks["tau_is_development_objective_minimum"] = close(tau_min, float(full["tau_dev_us"]), 1e-12)
    notes["tau_dev_us"] = tau_min

    gamma = float(full["gamma_dev_MHz_per_G"])
    checks["all_frequency_values_follow_frozen_development_slope"] = all(
        close(float(row["frequency_MHz"]), gamma * float(row["field_G"]), 1e-12) for row in metrics
    )
    checks["alias_classification_matches_nyquist"] = all(
        (row["alias_class"] == "primary") == (float(row["frequency_MHz"]) <= float(full["nyquist_MHz"]))
        for row in metrics
    )

    checks["phase_profiles_stay_on_local_0_to_2_ARA"] = all(
        0.0 <= float(row["x_spin_mid"]) < 2.0 and 0 <= int(row["phase_bin"]) < 32 for row in profiles
    )

    # Recompute the two frozen validation and holdout gates from the flat metric rows.
    gate_recalculation = {}
    for split in ("validation", "holdout"):
        period_gate = []
        release_gate = []
        peaks = []
        resultants = []
        for period in ("RF on", "RF off"):
            selected = [r for r in metrics if r["split"] == split and r["alias_class"] == "primary" and r["period"] == period]
            d_ratio = np.asarray([float(r["direction_target_sideband_ratio"]) for r in selected])
            d_intact_detector = np.asarray([float(r["direction_target"]) > float(r["direction_broken_detector"]) for r in selected])
            d_intact_time = np.asarray([float(r["direction_target"]) > float(r["direction_broken_time"]) for r in selected])
            period_gate.append(bool(np.median(d_ratio) > 1 and np.mean(d_ratio > 1) > 0.5 and np.mean(d_intact_detector) > 0.5 and np.mean(d_intact_time) > 0.5))
            r_ratio = np.asarray([float(r["release_target_sideband_ratio"]) for r in selected])
            r_intact_time = np.asarray([float(r["release_target"]) > float(r["release_broken_time"]) for r in selected])
            release_gate.append(bool(np.median(r_ratio) > 1 and np.mean(r_ratio > 1) > 0.5 and np.mean(r_intact_time) > 0.5))
            angles = np.pi * np.asarray([float(r["release_peak_x_spin"]) for r in selected])
            vector = np.mean(np.exp(1j * angles))
            resultants.append(float(abs(vector)))
            peaks.append(float((np.angle(vector) / np.pi) % 2.0))
        distance = min(abs(peaks[0] - peaks[1]), 2.0 - abs(peaks[0] - peaks[1]))
        phase_gate = resultants[0] > 0.5 and resultants[1] > 0.5 and distance < 0.25
        gate_recalculation[split] = {
            "spin_child_calibration_supported": bool(all(period_gate)),
            "release_statistical_gate_without_phase": bool(all(release_gate)),
            "release_phase_reproduction": bool(phase_gate),
            "total_release_phase_lock_supported": bool(all(release_gate) and phase_gate),
        }
    checks["frozen_gates_recompute_from_flat_metrics"] = all(
        all(full["aggregate"]["frozen_gates"][split][key] == value for key, value in result.items())
        for split, result in gate_recalculation.items()
    )
    notes["recomputed_gates"] = gate_recalculation

    # Separate split runs must reproduce the corresponding rows in the combined output.
    same_splits = True
    for split, suffix in (("development", "DEVELOPMENT"), ("validation", "VALIDATION"), ("holdout", "HOLDOUT")):
        split_rows = read_csv(RESULTS / f"T414_{suffix}_RUN_PERIOD_METRICS.csv")
        full_rows = [r for r in metrics if r["split"] == split]
        split_rows.sort(key=lambda r: (r["run"], r["period"]))
        full_rows.sort(key=lambda r: (r["run"], r["period"]))
        same_splits &= split_rows == full_rows
    checks["combined_run_reproduces_sealed_split_rows"] = bool(same_splits)

    manifest = {r["run"]: r for r in read_csv(T413 / "source" / "T413_SOURCE_MANIFEST.csv")}
    hash_rows_ok = True
    for row in source_hashes:
        path = T413 / "source" / "raw" / f"{row['run']}.nxs"
        hash_rows_ok &= path.exists() and sha256(path) == row["sha256"] and path.stat().st_size == int(row["bytes"])
        hash_rows_ok &= row["run"] in manifest
    checks["all_46_source_files_match_saved_hashes"] = bool(hash_rows_ok and len(source_hashes) == 46)

    # Direct raw-data channel-separation spot check.
    sample_path = T413 / "source" / "raw" / "EMU00069983.nxs"
    handle = SD(str(sample_path), SDC.READ)
    counts = np.asarray(handle.select("counts")[:], dtype=float)[:96]
    time = np.asarray(handle.select("corrected_time")[:], dtype=float)
    eligible = (time >= 0.25) & (time < 6.0)
    counts = counts[:, eligible]
    total = counts.sum(axis=0)
    share = 96.0 * counts / total[None, :]
    rng = np.random.default_rng(914)
    permuted = np.empty_like(counts)
    for column in range(counts.shape[1]):
        permuted[:, column] = counts[rng.permutation(96), column]
    checks["detector_shares_sum_to_96"] = bool(np.allclose(share.sum(axis=0), 96.0, rtol=0, atol=1e-10))
    checks["detector_permutation_leaves_release_total_exact"] = bool(np.array_equal(total, permuted.sum(axis=0)))

    primary = [r for r in metrics if r["alias_class"] == "primary"]
    samples_per_cycle = np.asarray([1.0 / (0.016 * float(r["frequency_MHz"])) for r in primary])
    log_direction = np.log(np.maximum([float(r["direction_target_sideband_ratio"]) for r in primary], 1e-15))
    resolution_correlation = float(np.corrcoef(samples_per_cycle, log_direction)[0, 1])
    notes["posthoc_samples_per_cycle_vs_log_direction_ratio_correlation"] = resolution_correlation

    passed = bool(all(checks.values()))
    output = {
        "test": "T414 independent validation",
        "status": "passed" if passed else "failed",
        "checks": checks,
        "notes": notes,
    }
    (RESULTS / "T414_VALIDATION_AUDIT.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
