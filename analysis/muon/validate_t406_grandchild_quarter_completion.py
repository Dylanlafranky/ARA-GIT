#!/usr/bin/env python3
"""Independent saved-artifact checks for T406."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T406_grandchild_quarter_completion"
PROTOCOL = ROOT / "T406_GRANDCHILD_QUARTER_COMPLETION_PROTOCOL_2026-08-18.md"


def main() -> None:
    results = json.loads((OUT / "T406_RESULTS.json").read_text(encoding="utf-8"))
    with (OUT / "T406_SPLIT_RESULTS.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    x = np.asarray([float(r["observed_child_crest"]) for r in rows])
    err = np.asarray([float(r["absolute_error"]) for r in rows])
    primary = next(r for r in rows if int(r["salt"]) == 400)
    checks = {
        "protocol_hash": results["protocol_sha256"] == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "twenty_splits": len(rows) == 20,
        "primary_crest": abs(float(primary["observed_child_crest"]) - results["primary"]["observed_child_crest"]) < 1e-12,
        "primary_completion": abs((float(primary["observed_child_crest"]) - 0.5) / 0.25 - results["primary"]["completion_fraction"]) < 1e-12,
        "raw_fraction": abs(float(np.mean(np.abs(x - 0.75) <= 0.10)) - results["replication"]["raw_fraction_in_band"]) < 1e-12,
        "loo_median_error": abs(float(np.median(err)) - results["loo_prediction"]["median_absolute_error"]) < 1e-12,
        "figure_exists": (OUT / "T406_GRANDCHILD_QUARTER_COMPLETION.png").stat().st_size > 10_000,
    }
    payload = {"test": "T406", "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "T406_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

