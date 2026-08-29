#!/usr/bin/env python3
"""Independent saved-output checks for T408."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T408_nested_windows_individual_muon"
PROTOCOL = ROOT / "T408_NESTED_WINDOWS_INDIVIDUAL_MUON_PROTOCOL_2026-08-18.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    results = json.loads((OUT / "T408_RESULTS.json").read_text(encoding="utf-8"))
    with (OUT / "T408_HOLDOUT_EVENT_SCORES.csv").open(newline="", encoding="utf-8") as handle:
        events = list(csv.DictReader(handle))
    with (OUT / "T408_WINDOWS.csv").open(newline="", encoding="utf-8") as handle:
        windows = {row["window"]: row for row in csv.DictReader(handle)}

    parent = results["windows_us"]["parent"]
    pure = results["windows_us"]["pure"]
    observed = results["windows_us"]["observed"]
    checks = {
        "protocol_hash": results["protocol_sha256"] == sha256(PROTOCOL),
        "source_counts": results["all_event_counts"] == {"calibration": 2396, "holdout": 2109},
        "ordered_nested_windows": parent[0] <= pure[0] < observed[1] < pure[1] <= parent[1],
        "window_csv_matches": all(
            math.isclose(float(windows[name]["left_us"]), results["windows_us"][name][0], abs_tol=1e-12)
            and math.isclose(float(windows[name]["right_us"]), results["windows_us"][name][1], abs_tol=1e-12)
            for name in ("parent", "pure", "observed")
        ),
        "event_count": len(events) == results["parent_window_counts"]["holdout"],
        "event_outcomes_match": sum(int(r["actual_in_pure_small_window"]) for r in events) == results["pure"]["positive_holdout"],
        "finite_probabilities": all(
            0 <= float(r[key]) <= 1
            for r in events
            for key in (
                "ordinary_probability_pure",
                "parent_probability_pure",
                "nested_probability_pure",
                "wrong_lineage_probability_pure",
                "nested_probability_observed",
            )
        ),
        "models_present": all(set(results[name]["models"]) == {"MG", "MP", "MN", "MW"} for name in ("pure", "observed")),
        "figure_exists": (OUT / "T408_NESTED_WINDOWS_INDIVIDUAL_MUON.png").exists(),
        "boundaries_present": len(results["boundaries"]) >= 4,
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    payload = {"test": "T408", "status": status, "checks": checks}
    (OUT / "T408_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if status != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
