#!/usr/bin/env python3
"""Independent artifact and arithmetic checks for T388."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T388_same_event_antiphase"
RESULTS = OUT / "T388_RESULTS.json"
EVENTS = OUT / "T388_PAIRED_EVENT_METRICS.csv"
FIGURE = OUT / "T388_SAME_EVENT_ANTIPHASE_FIGURE.png"
REPORT = OUT / "T388_SAME_EVENT_ANTIPHASE_REPORT.md"
EXPECTED_PROTOCOL_SHA256 = "2B18E310FE2E261EB82A7F78F8F8A87ED7BE17AA8F02402C83D3898D41A5CD2D"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest().upper()


def main() -> None:
    data = json.loads(RESULTS.read_text(encoding="utf-8"))
    with EVENTS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    checks = {
        "result_is_t388": data["test"] == "T388",
        "protocol_hash_matches_frozen": data["protocol"]["sha256"] == EXPECTED_PROTOCOL_SHA256,
        "protocol_file_hash_matches": sha256(Path(data["protocol"]["path"])) == EXPECTED_PROTOCOL_SHA256,
        "raw_file_hash_matches_record": sha256(Path(data["source"]["path"])) == data["source"]["sha256"],
        "event_count_matches_csv": len(rows) == data["population"]["paired_complete_events"],
        "population_is_650": len(rows) == 650,
        "direct_is_lowest_saved_score": data["winner"] == "direct" and data["scores"]["direct"]["median"] == min(item["median"] for item in data["scores"].values()),
        "all_reversal_delta_intervals_above_zero": all(data["deltas"][name]["ci95"][0] > 0 for name in ("full", "radial", "path")),
        "orientation_share_valid": 0 <= data["same_loop_orientation_share"] <= 1,
        "orientation_gate_is_met": data["same_loop_orientation_share"] > 0.75,
        "direct_gate_passes": data["gates"]["direct_repeat"] is True,
        "reversal_gates_fail": data["gates"]["full_antiphase"] is False and data["gates"]["one_axis_antiphase"] is False,
        "advance_gate_fails": data["gates"]["advance_handover"] is False,
        "claim_boundary_is_preserved": data["claim_boundary"]["neutrinos_directly_observed"] is False and data["claim_boundary"]["upstream_muon_child_identified"] is False,
        "figure_exists_and_nonempty": FIGURE.exists() and FIGURE.stat().st_size > 100_000,
        "report_exists_and_nonempty": REPORT.exists() and REPORT.stat().st_size > 1_000,
    }
    passed = all(checks.values())
    validation = {
        "validator": "T388",
        "passed": passed,
        "checks": checks,
        "validated_result": str(RESULTS),
    }
    (OUT / "T388_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps(validation, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
