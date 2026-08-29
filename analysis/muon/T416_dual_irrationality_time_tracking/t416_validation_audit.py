#!/usr/bin/env python3
"""Independent structural and arithmetic audit of the frozen T416 validation run."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RAW = HERE.parent / "T413_live_state_handover" / "source" / "raw"


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def median(rows: list[dict], field: str) -> float:
    return float(np.median([float(row[field]) for row in rows]))


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return bool(np.isclose(float(a), float(b), rtol=0.0, atol=tolerance, equal_nan=True))


def main() -> None:
    result = json.loads((RESULTS / "T416_VALIDATION_RESULTS.json").read_text(encoding="utf-8"))
    timeline = read_csv(RESULTS / "T416_VALIDATION_TIMELINE.csv")
    summary = read_csv(RESULTS / "T416_VALIDATION_RUN_PERIOD_SUMMARY.csv")

    keys = [(row["run"], row["period"], row["time_us"]) for row in timeline]
    coordinate_fields = ("parent_ARA", "state_x_L", "state_x_C", "history_x_P", "history_x_R")
    coordinates = np.asarray([[float(row[field]) for field in coordinate_fields] for row in timeline])
    validation_runs = sorted({row["run"] for row in timeline})

    checks: dict[str, bool] = {
        "stage_is_validation": result["stage"] == "validation",
        "timeline_row_count": len(timeline) == result["timeline_rows"] == 1534,
        "run_count": len(validation_runs) == result["run_count"] == 13,
        "run_period_count": len(summary) == result["run_period_count"] == 26,
        "timeline_key_unique": len(keys) == len(set(keys)),
        "coordinates_finite": bool(np.isfinite(coordinates).all()),
        "coordinates_inside_0_2": bool(((coordinates >= 0.0) & (coordinates <= 2.0)).all()),
        "protocol_hash_matches": digest(HERE / "T416_FROZEN_PROTOCOL.md") == result["protocol_sha256"],
        "analysis_hash_matches": digest(HERE / "t416_dual_irrationality_time_tracking.py") == result["analysis_sha256"],
        "source_hashes_match": all(digest(RAW / f"{run}.nxs") == expected for run, expected in result["source_hashes"].items()),
    }

    for period in ("RF on", "RF off"):
        part = [row for row in summary if row["period"] == period]
        stored = result["rf_state"][period]
        checks[f"{period}_median_x_L"] = close(median(part, "median_state_x_L"), stored["median_x_L"])
        checks[f"{period}_median_x_C"] = close(median(part, "median_state_x_C"), stored["median_x_C"])
        checks[f"{period}_median_x_P"] = close(median(part, "median_history_x_P"), stored["median_x_P"])
        checks[f"{period}_median_x_R"] = close(median(part, "median_history_x_R"), stored["median_x_R"])

    stored_gates = result["gates"]
    recomputed_gates = {
        "G1_observed_state_orientation": all(result["rf_state"][period]["median_x_C"] > 1.0 for period in ("RF on", "RF off")),
        "G2_observed_contraction": (
            result["paired_field_effects"]["state_x_L"]["median"] < 1.0
            and result["paired_field_effects"]["state_x_L"]["ci_high"] < 1.0
        ),
        "G3_chronology_determinacy": result["paired_field_effects"]["shuffle_minus_target_x_R"]["ci_low"] > 0.0,
        "G4_support_preservation": result["paired_field_effects"]["abs_shuffle_minus_target_x_P"]["median"] < 0.10,
        "G5_closure_history": result["paired_field_effects"]["target_minus_shuffle_closure_rho"]["ci_low"] > 0.0,
        "G6_frequency_specificity": result["paired_field_effects"]["wrong_minus_target_x_R"]["ci_low"] > 0.0,
        "G7_nonredundancy_diagnostic": abs(result["parent_adjusted_spearman_state_x_L_history_x_R"]) < 0.80,
    }
    checks["frozen_gates_recompute"] = all(stored_gates[key] == value for key, value in recomputed_gates.items())
    checks["complete_gate_recomputes"] = stored_gates["dual_instrument_supported"] == all(recomputed_gates.values())

    payload = {
        "status": "passed" if all(checks.values()) else "failed",
        "scope": "Independent structural, provenance, range, median and frozen-gate recomputation.",
        "checks": checks,
        "check_count": len(checks),
        "pass_count": sum(checks.values()),
        "frozen_gate_pass_count": sum(bool(value) for key, value in stored_gates.items() if key.startswith("G")),
        "frozen_gate_count": sum(1 for key in stored_gates if key.startswith("G")),
        "boundary": result["boundary"],
    }
    (RESULTS / "T416_VALIDATION_AUDIT.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
