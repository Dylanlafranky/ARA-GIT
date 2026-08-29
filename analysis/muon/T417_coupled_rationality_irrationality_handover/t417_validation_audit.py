#!/usr/bin/env python3
"""Independent structural and arithmetic audit of T417 locked-evaluation outputs."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
T416 = HERE.parent / "T416_dual_irrationality_time_tracking" / "results"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    freeze = json.loads((HERE / "T417_DEVELOPMENT_FREEZE.json").read_text(encoding="utf-8"))
    result = json.loads((RESULTS / "T417_EVALUATION_RESULTS.json").read_text(encoding="utf-8"))
    timeline = rows(RESULTS / "T417_EVALUATION_TIMELINE.csv")
    summary = rows(RESULTS / "T417_EVALUATION_SEQUENCE_SUMMARY.csv")
    source = rows(T416 / "T416_VALIDATION_TIMELINE.csv")
    posthoc = json.loads((RESULTS / "T417_POSTHOC_DIAGNOSTICS.json").read_text(encoding="utf-8"))

    lookup = {(r["run"], r["period"], r["time_us"]): r for r in source}
    formula_errors = []
    range_errors = []
    for row in timeline:
        original = lookup[(row["run"], row["period"], row["time_us"])]
        closure_r = 2.0 * float(original["median_closure_rho"])
        unresolved_i = float(original["history_x_R"])
        amount_a = 0.5 * (closure_r + unresolved_i)
        balance_b = 1.0 + (unresolved_i - closure_r) / (unresolved_i + closure_r + 1e-12)
        formula_errors.extend([
            abs(float(row["rational_closure_R"]) - closure_r),
            abs(float(row["irrational_unresolved_I"]) - unresolved_i),
            abs(float(row["coupled_amount_A"]) - amount_a),
            abs(float(row["coupled_balance_B"]) - balance_b),
        ])
        range_errors.extend([
            not (0 <= float(row[name]) <= 2)
            for name in ("rational_closure_R", "irrational_unresolved_I", "coupled_amount_A", "coupled_balance_B")
        ])

    eligible = sum(int(row["eligible"]) for row in summary)
    ordered = sum(int(row["ordered"]) for row in summary)
    checks = {
        "protocol_hash_matches_freeze": digest(HERE / "T417_FROZEN_PROTOCOL.md") == freeze["protocol_sha256"],
        "script_hash_matches_freeze": digest(HERE / "t417_coupled_rationality_irrationality_handover.py") == freeze["script_sha256"],
        "evaluation_source_hash_matches_result": digest(T416 / "T416_VALIDATION_TIMELINE.csv") == result["hashes"]["source_sha256"],
        "timeline_row_count_matches_source": len(timeline) == len(source) == 1534,
        "run_period_count_is_26": len(summary) == result["run_period_sequences"] == 26,
        "rf_periods_remain_separate": {row["period"] for row in timeline} == {"RF on", "RF off"},
        "coupled_formulas_recompute": max(formula_errors) < 1e-10,
        "all_coupled_coordinates_in_0_2": not any(range_errors),
        "eligible_count_recomputes": eligible == result["eligible_sequences"] == 14,
        "ordered_count_recomputes": ordered == result["ordered_sequences"] == 14,
        "ordering_gate_recomputes": bool(result["gates"]["G2_ordering"]["pass"]) == (ordered / eligible >= 0.80),
        "availability_gate_recomputes": bool(result["gates"]["G1_availability"]["pass"]) == (eligible >= 20),
        "frozen_primary_verdict_is_not_supported": result["primary_coupled_handover"] == "NOT SUPPORTED",
        "state_alignment_verdict_is_not_supported": result["state_alignment"] == "NOT SUPPORTED",
        "posthoc_is_explicitly_labelled": posthoc["label"].startswith("POST-RESULT DIAGNOSTIC"),
        "posthoc_partition_sums_to_26": sum(posthoc["classification_counts"].values()) == 26,
        "posthoc_does_not_modify_frozen_result": result["status"] == "NOT SUPPORTED",
    }
    payload = {
        "test": "T417 validation audit",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks_passed": sum(checks.values()),
        "checks_total": len(checks),
        "checks": checks,
        "maximum_formula_error": max(formula_errors),
        "boundary": "Audit verifies saved calculations and frozen bookkeeping; it does not upgrade the scientific verdict.",
    }
    (RESULTS / "T417_VALIDATION_AUDIT.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
