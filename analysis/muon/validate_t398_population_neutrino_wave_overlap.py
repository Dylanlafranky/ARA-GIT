#!/usr/bin/env python3
"""Independent saved-artifact validation for T398."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T398_population_neutrino_wave_overlap"
RESULTS = OUT / "T398_RESULTS.json"
OVERLAP = OUT / "T398_NATIVE_WAVE_OVERLAP.csv"
BINNED = OUT / "T398_T371_MEASURED_AND_FITTED.csv"
HOLDOUT = OUT / "T398_T378_INDEPENDENT_HOLDOUT.csv"
PHASE = OUT / "T398_T397_SEPARATE_PHASE_COMPARISON.csv"
PROTOCOL = HERE / "T398_POPULATION_NEUTRINO_WAVE_OVERLAP_PROTOCOL_2026-08-17.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


def rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def interpolate_crossing(data: list[dict[str, str]]) -> float:
    values = [
        (
            float(row["time_us"]),
            float(row["prompt_fitted_events_per_native_ns"])
            - float(row["delayed_total_fitted_events_per_native_ns"]),
        )
        for row in data
    ]
    prompt_peak = max(
        range(len(data)), key=lambda i: float(data[i]["prompt_fitted_events_per_native_ns"])
    )
    for index in range(prompt_peak, len(values) - 1):
        x0, y0 = values[index]
        x1, y1 = values[index + 1]
        if y0 >= 0.0 and y1 <= 0.0:
            return x0 - y0 * (x1 - x0) / (y1 - y0)
    return float("nan")


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    overlap = rows(OVERLAP)
    binned = rows(BINNED)
    holdout = rows(HOLDOUT)
    phase = rows(PHASE)

    child_error = max(
        abs(
            float(row["nu_e_fitted_events_per_native_ns"])
            + float(row["anti_nu_mu_fitted_events_per_native_ns"])
            - float(row["delayed_total_fitted_events_per_native_ns"])
        )
        for row in overlap
    )
    complement_error = max(
        abs(
            float(row["inferred_muon_remaining_fraction"])
            + float(row["cumulative_delayed_release_fraction"])
            - 1.0
        )
        for row in overlap
    )
    display_crossing = interpolate_crossing(overlap)
    reported_crossing = float(result["handover"]["reconstructed_native_equality_us"])
    # The delivered overlap is a 5 ns display sample, so its independently
    # interpolated crossing may differ from the 1 ns reconstruction by <5 ns.
    crossing_display_close = abs(display_crossing - reported_crossing) < 0.005

    prompt_peak = max(binned, key=lambda row: float(row["fitted_prompt_nu_mu"]))
    delayed_peak = max(binned, key=lambda row: float(row["fitted_delayed_nu_e_plus_anti_nu_mu"]))
    holdout_prompt_peak = max(holdout, key=lambda row: float(row["fitted_prompt_nu_mu"]))
    holdout_delayed_peak = max(
        holdout, key=lambda row: float(row["fitted_delayed_nu_e_plus_anti_nu_mu"])
    )

    checks = {
        "protocol_hash_matches": sha256(PROTOCOL) == result["protocol_sha256"],
        "all_frozen_gates_pass": all(bool(value) for value in result["gates"].values()),
        "native_overlap_has_1200_rows": len(overlap) == 1200,
        "native_time_is_strictly_increasing": all(
            float(overlap[i + 1]["time_us"]) > float(overlap[i]["time_us"])
            for i in range(len(overlap) - 1)
        ),
        "display_crossing_reconstructs_native_handover": crossing_display_close,
        "flavor_children_close_exactly": child_error < 1e-14,
        "survival_and_release_are_complements": complement_error < 1e-14,
        "T371_binned_delayed_peak_after_prompt": float(delayed_peak["time_us"])
        > float(prompt_peak["time_us"]),
        "T378_holdout_delayed_peak_after_prompt": float(holdout_delayed_peak["time_us"])
        > float(holdout_prompt_peak["time_us"]),
        "T397_comparison_is_separate_and_complete": len(phase) == 96
        and all("separate experiment" in row["source_identity"] for row in phase),
        "verdict_preserves_individual_event_boundary": "INDIVIDUAL BIRTH UNOBSERVED"
        in result["verdict"],
    }
    validation = {
        "test": "T398 independent saved-artifact validation",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "recomputed": {
            "display_sample_crossing_us": display_crossing,
            "reported_native_1ns_crossing_us": reported_crossing,
            "crossing_abs_difference_us": abs(display_crossing - reported_crossing),
            "max_abs_flavor_closure_error": child_error,
            "max_abs_survival_release_complement_error": complement_error,
            "T371_prompt_peak_us": float(prompt_peak["time_us"]),
            "T371_delayed_peak_us": float(delayed_peak["time_us"]),
            "T378_prompt_peak_us": float(holdout_prompt_peak["time_us"]),
            "T378_delayed_peak_us": float(holdout_delayed_peak["time_us"]),
        },
        "boundary": "Validation checks the saved population-level artifact; it cannot create event linkage absent from the source data.",
    }
    (OUT / "T398_VALIDATION.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(validation, indent=2))
    if validation["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

