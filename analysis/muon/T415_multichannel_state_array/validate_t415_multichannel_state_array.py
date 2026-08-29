#!/usr/bin/env python3
"""Independent arithmetic and provenance checks for T415."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
sys.path.insert(0, str(HERE))
import t415_multichannel_state_array as t415
import t415_posthoc_parent_history_diagnostic as diagnostic


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return abs(float(a) - float(b)) <= tolerance


def main() -> None:
    freeze = json.loads(t415.FREEZE.read_text(encoding="utf-8"))
    result = json.loads((RESULTS / "T415_VALIDATION_RESULTS.json").read_text(encoding="utf-8"))
    posthoc = json.loads((RESULTS / "T415_POSTHOC_PARENT_HISTORY.json").read_text(encoding="utf-8"))
    manifest = t415.t414.read_manifest()
    development = [row for row in manifest if row["split"] == "development"]
    validation = [row for row in manifest if row["split"] == "validation"]
    summary = read_csv(RESULTS / "T415_MODEL_SUMMARY.csv")
    fields = read_csv(RESULTS / "T415_FIELD_METRICS.csv")
    periods = read_csv(RESULTS / "T415_PERIOD_METRICS.csv")
    controls = read_csv(RESULTS / "T415_CONTROL_SUMMARY.csv")
    posthoc_summary = read_csv(RESULTS / "T415_POSTHOC_PARENT_HISTORY_SUMMARY.csv")

    primary_fields = [
        row for row in fields
        if row["horizon_bins"] == "4" and row["model"] == "M4 full lock"
    ]
    primary_improvements = np.asarray([float(row["improvement_fraction"]) for row in primary_fields])
    primary_rmse = np.asarray([float(row["rmse_log_rate"]) for row in primary_fields])
    primary_periods = [
        row for row in periods
        if row["horizon_bins"] == "4" and row["model"] == "M4 full lock"
    ]
    period_medians = {
        period: float(np.median([float(row["improvement_fraction"]) for row in primary_periods if row["period"] == period]))
        for period in ("RF on", "RF off")
    }
    control_map = {row["control"]: row for row in controls}
    recomputed_gates = {
        "median_improvement_positive": float(np.median(primary_improvements)) > 0,
        "at_least_10_of_13_fields_improve": int(np.sum(primary_improvements > 0)) >= 10,
        "beats_wrong_frequency_control": float(np.median(primary_rmse)) < float(control_map["wrong_frequency"]["median_field_rmse_log_rate"]),
        "beats_broken_history_control": float(np.median(primary_rmse)) < float(control_map["broken_history"]["median_field_rmse_log_rate"]),
        "both_rf_period_medians_positive": all(value > 0 for value in period_medians.values()),
    }
    recomputed_gates["full_array_supported"] = all(recomputed_gates.values())

    validation_data = diagnostic.prepare(validation)
    rate = np.asarray([row["current_log_rate"] for row in validation_data["records"]])
    strength = np.asarray([row["strength"] for row in validation_data["records"]])
    recomputed_correlation = float(np.corrcoef(strength, rate)[0, 1])
    d3 = next(row for row in posthoc_summary if row["model"] == "D3 full diagnostic")
    checks = {
        "protocol_hash_matches_freeze": freeze["protocol_sha256"] == t415.sha256(t415.PROTOCOL),
        "analysis_hash_matches_freeze": freeze["analysis_sha256"] == t415.sha256(Path(t415.__file__).resolve()),
        "t414_loader_hash_matches_freeze": freeze["t414_loader_sha256"] == t415.sha256(t415.T414_SCRIPT),
        "split_counts_are_13_and_13": len(development) == 13 and len(validation) == 13,
        "development_source_hashes_match": all(
            freeze["source_hashes"][row["run"]] == t415.sha256(t415.t414.RAW / f"{row['run']}.nxs")
            for row in development
        ),
        "validation_source_hashes_match": all(
            result["validation_source_hashes"][row["run"]] == t415.sha256(t415.t414.RAW / f"{row['run']}.nxs")
            for row in validation
        ),
        "all_15_model_horizon_rows_present": len(summary) == 15,
        "all_195_field_rows_present": len(fields) == 195,
        "all_390_period_rows_present": len(periods) == 390,
        "primary_median_recomputes": close(
            np.median(primary_improvements),
            next(row for row in summary if row["horizon_bins"] == "4" and row["model"] == "M4 full lock")["median_field_improvement_fraction"],
        ),
        "primary_field_wins_recompute": int(np.sum(primary_improvements > 0)) == 13,
        "frozen_gates_recompute": recomputed_gates == result["gates"],
        "posthoc_strength_rate_correlation_recomputes": close(recomputed_correlation, posthoc["strength_vs_current_log_rate_correlation"]),
        "posthoc_full_array_summary_matches": close(
            d3["median_field_improvement_fraction"],
            next(row for row in posthoc["models"] if row["model"] == "D3 full diagnostic")["median_field_improvement_fraction"],
        ),
    }
    audit = {
        "test": "T415 independent validation",
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "notes": {
            "frozen_primary_median_improvement_fraction": float(np.median(primary_improvements)),
            "frozen_primary_field_wins": int(np.sum(primary_improvements > 0)),
            "recomputed_gates": recomputed_gates,
            "posthoc_strength_vs_current_log_rate_correlation": recomputed_correlation,
            "posthoc_full_array_median_improvement_fraction": float(d3["median_field_improvement_fraction"]),
        },
    }
    path = RESULTS / "T415_VALIDATION_AUDIT.json"
    path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    if audit["status"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

