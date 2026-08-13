#!/usr/bin/env python3
"""Lightweight validator for T376 outputs."""

import json
from pathlib import Path

root = Path(__file__).resolve().parent
r = json.loads((root / "T376_event_linked" / "results.json").read_text())

assert r["n_train"] > 2000
assert r["n_holdout"] > 2000
assert len(r["landmarks"]) == 4
assert [x["center"] for x in r["landmarks"]] == [0.5, 0.75, 0.25, 1.25]
assert r["delta_nll_Q_minus_ARA"] < 0
assert r["run_block_bootstrap_ci95"][0] < 0
assert max(r["landmarks"], key=lambda x: x["enrichment_vs_uniform"])["center"] == 0.5
visual = root / "T376_event_linked" / "T376_EVENT_LINKED_MUON_HANDOVER.html"
assert visual.stat().st_size > 10000
html = visual.read_text(encoding="utf-8")
for required in (
    "How to read every chart",
    "x_mu = 2q2 / (q1 + q2)",
    "delay to visible daughter (microseconds)",
    "0.50 child",
    "1.00 ridge: q1 = q2",
    "one blue dot = one displayed held-out muon",
):
    assert required in html, required

print("T376 validation: PASS")
