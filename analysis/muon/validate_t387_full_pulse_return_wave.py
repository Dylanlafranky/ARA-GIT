#!/usr/bin/env python3
"""Independent artifact and headline-gate validator for T387."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T387_full_pulse_return_wave"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    results = json.loads((OUT / "T387_RESULTS.json").read_text(encoding="utf-8"))
    profiles = read_csv(OUT / "T387_ARA_TIME_PROFILES.csv")
    raw = read_csv(OUT / "T387_RAW_WAVEFORM_PROFILE.csv")
    summary = read_csv(OUT / "T387_WINDOW_SUMMARY.csv")
    occupancy = read_csv(OUT / "T387_QUADRANT_OCCUPANCY.csv")

    checks = {}
    checks["source_hash_frozen"] = results["source"]["sha256"] == "C2DC1E012FBDF0F3C5EC305E2D8E4DD1D87B05DF5CBA39B492189C0F7D5454CD"
    checks["protocol_hash_frozen"] = results["source"]["protocol_sha256"] == "688F23BBAB7AFB44AB29E284CCC5CAB066BB285A49FC5D6D57960162C379D296"
    checks["three_windows"] = {int(float(r["window_ns"])) for r in summary} == {64, 128, 256}
    checks["full_time_range"] = {int(float(r["time_ns"])) for r in raw} >= {-1024, 0, 768}
    checks["both_axes_profiled"] = {r["axis"] for r in profiles} == {"x_radial", "x_history"}
    checks["all_profile_coordinates_in_range"] = all(
        0 <= float(r["median"]) <= 2
        for r in profiles
        if r["median"] and math.isfinite(float(r["median"]))
    )
    checks["occupancy_complete"] = {
        (int(float(r["window_ns"])), r["phase"], r["quadrant"]) for r in occupancy
    } >= {
        (w, phase, q)
        for w in (64, 128, 256)
        for phase in ("pre", "pulse", "recovery")
        for q in ("Ab", "aB", "Ba", "bA", "ridge")
    }
    checks["figure_exists"] = (OUT / "T387_FULL_PULSE_RETURN_FIGURE.png").stat().st_size > 100_000
    checks["report_exists"] = (OUT / "T387_FULL_PULSE_RETURN_REPORT.md").stat().st_size > 1_500
    checks["retrospective_boundary"] = results["boundary"]["retrospective_not_predictive"] is True
    checks["upstream_not_claimed"] = results["boundary"]["upstream_handover_directly_observed"] is False

    windows = results["windows"]
    recomputed_gates = {
        "opposite_radial_half_recovered": all(
            s["radial_at_minimum_ci95"][0] > 1 and s["radial_one_window_later_ci95"][1] < 1
            for s in windows
        ),
        "approximate_radial_mirror": all(abs(s["mirror_residual"]) <= 0.10 for s in windows),
        "opposite_path_half_recovered": all(s["path_crosses_and_returns"] for s in windows),
        "local_loop_return": all(s["return_fraction"] >= 0.75 for s in windows),
    }
    checks["headline_gates_recompute"] = recomputed_gates == results["gates"]
    troughs = [float(s["radial_trough_time_ns_from_onset"]) for s in windows]
    win = [float(s["window_ns"]) for s in windows]
    shifted = [a - b for a, b in zip(troughs, win)]
    slope = results["timing"]["slope_ns_per_window_ns"]
    translated = max(shifted) - min(shifted) <= 32 and 0.75 <= slope <= 1.25
    anchored = max(troughs) - min(troughs) <= 32
    checks["timing_recomputes"] = translated == results["timing"]["window_translated"] and anchored == results["timing"]["physically_anchored"]

    payload = {
        "validator": "T387",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "recomputed_gates": recomputed_gates,
    }
    (OUT / "T387_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__ == "__main__":
    main()
