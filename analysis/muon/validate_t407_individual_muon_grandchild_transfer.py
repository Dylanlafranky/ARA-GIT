#!/usr/bin/env python3
"""Independent saved-artifact checks for T407."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "T407_individual_muon_grandchild_transfer"
PROTOCOL = ROOT / "T407_INDIVIDUAL_MUON_GRANDCHILD_TRANSFER_PROTOCOL_2026-08-18.md"


def main() -> None:
    result = json.loads((OUT / "T407_RESULTS.json").read_text(encoding="utf-8"))
    with (OUT / "T407_MODEL_SUMMARY.csv").open(newline="", encoding="utf-8") as handle:
        models = list(csv.DictReader(handle))
    with (OUT / "T407_HOLDOUT_EVENT_SCORES.csv").open(newline="", encoding="utf-8") as handle:
        events = list(csv.DictReader(handle))
    lookup = {r["model"]: r for r in models}
    pure = lookup["M075"]
    observed = lookup["M0706"]
    checks = {
        "protocol_hash": result["protocol_sha256"] == hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),
        "event_count": len(events) == result["n_holdout"] == 2109,
        "model_count": len(models) == 6,
        "pure_centre": abs(float(pure["centre"]) - 0.75) < 1e-12,
        "observed_centre": abs(float(observed["centre"]) - 0.7063064837018814) < 1e-12,
        "pure_nll_delta": abs(float(pure["nll_improvement"]) - result["models"]["M075"]["bootstrap"]["mean"]) < 1e-12,
        "finite_event_scores": bool(np.all(np.isfinite([float(r["pure_band_predicted_median_us"]) for r in events]))),
        "figure_exists": (OUT / "T407_INDIVIDUAL_MUON_GRANDCHILD_TRANSFER.png").stat().st_size > 10_000,
        "boundaries_present": len(result["boundaries"]) >= 4,
    }
    payload = {"test": "T407", "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    (OUT / "T407_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

