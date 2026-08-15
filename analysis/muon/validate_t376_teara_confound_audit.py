#!/usr/bin/env python3
import json
from pathlib import Path

root = Path(__file__).resolve().parent / "T376_teara_audit"
r = json.loads((root / "results.json").read_text(encoding="utf-8"))
h = (root / "T376_TEARA_CONFOUND_AUDIT.html").read_text(encoding="utf-8")

assert r["n_holdout"] == 4751
assert abs(r["max_forced_closure_error"]) < 1e-12
assert r["holdout_tick_quantised_fraction"] > .95
assert abs(r["holdout_mean_B_corrected"] - 1) < .02
assert abs(r["correlations"]["C_corrected_vs_delay"]) < .05
assert r["leave_one_run_out_posthoc"]["delta_pulse_minus_teara"] < 0
for required in (
    "TE-ARA coupling and confound audit",
    "Detector-end balance by run",
    "Later daughter time across incoming strata",
    "Leave-one-run-out timing test",
    "A+B=2 and “Other=0” are forced",
    "Variables capable of skewing T376",
):
    assert required in h, required

print("T376 TE-ARA confound audit: PASS")
