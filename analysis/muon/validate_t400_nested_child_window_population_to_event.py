#!/usr/bin/env python3
"""Independent saved-artifact validation for T400.

This validator does not refit the model. It recomputes reported summaries,
gate truth values, hashes, coordinate bounds and claim-boundary checks from
the files written by the primary analysis.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T400_nested_child_window_population_to_event"
PROTOCOL = HERE / "T400_NESTED_CHILD_WINDOW_POPULATION_TO_EVENT_PROTOCOL_2026-08-17.md"
RESULTS = OUT / "T400_RESULTS.json"
EXPECTED_PROTOCOL_HASH = "9a7c0e53988235e0ecc3b52c9c2a224afc3141efaf207654ba61423dc35ed263"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol


def main() -> None:
    result = json.loads(RESULTS.read_text(encoding="utf-8"))
    pop = result["primary_population"]
    event = result["primary_event_transfer"]
    curve = rows("T400_LOCAL_CHILD_CURVE.csv")
    hist = rows("T400_PRIMARY_EVENT_HISTOGRAM.csv")
    sample = rows("T400_PRIMARY_EVENT_SAMPLE.csv")
    splits = rows("T400_REPEATED_SPLITS.csv")
    loo = rows("T400_LEAVE_ONE_OUT_CHILD_WINDOWS.csv")
    shifts = rows("T400_PHASE_SHIFT_CONTROLS.csv")
    boot = rows("T400_EVENT_BOOTSTRAP.csv")
    sensitivity = rows("T400_EVENT_MODE_SENSITIVITY.csv")

    x_curve = [float(row["local_child_ara"]) for row in curve]
    hist_total = sum(float(row["effective_delayed_weight"]) for row in hist)
    sample_weight = sum(float(row["delayed_membership_weight"]) for row in sample)
    valid_splits = [row for row in splits if row["valid"].lower() == "true"]
    split_ridge = sum(0.5 <= float(row["holdout_weighted_mode"]) <= 1.5 for row in valid_splits)
    split_fraction = split_ridge / len(valid_splits)
    valid_loo = [row for row in loo if row["valid"].lower() == "true"]
    loo_fraction = sum(row["in_population_ridge_gate"].lower() == "true" for row in valid_loo) / len(valid_loo)
    as_good = sum(row["as_good_as_real"].lower() == "true" for row in shifts)
    phase_p = (as_good + 1) / (len(shifts) + 1)
    boot_ridge = sum(0.5 <= float(row["mode"]) <= 1.5 for row in boot) / len(boot)

    recomputed_population_gates = {
        "P1_ordered_objective_window": pop["left_time_us"] < pop["delayed_crest_time_us"] < pop["right_time_us"],
        "P2_crest_near_local_ridge": 0.75 <= pop["local_crest_ara"] <= 1.25,
        "P3_leave_one_out_ridge_fraction_ge_0p80": loo_fraction >= 0.80,
    }
    recomputed_event_gates = {
        "I1_effective_delayed_count_ge_10": event["effective_delayed_holdout"] >= 10.0,
        "I2_holdout_mode_in_broad_ridge": 0.5 <= event["holdout_weighted_mode"] <= 1.5,
        "I3_holdout_mean_within_0p30_of_population": abs(event["holdout_weighted_mean"] - event["population_local_mean"]) <= 0.30,
        "I4_repeated_split_mode_fraction_ge_0p70": split_fraction >= 0.70,
        "I5_C_median_membership_weight_gt_AC": event["median_delayed_weight_C"] > event["median_delayed_weight_AC"],
    }

    required_boundary_phrases = ("individual detector events", "statistical weight", "cannot identify both neutrinos")
    boundary_text = " ".join(result.get("boundaries", [])).lower()
    checks = {
        "protocol_hash_is_frozen_hash": sha256(PROTOCOL) == EXPECTED_PROTOCOL_HASH == result["protocol_sha256"],
        "raw_C_hash_matches": sha256(Path(result["source"]["data_dir"]) / "dataBeamOnC.txt") == result["source"]["beam_C_sha256"],
        "raw_AC_hash_matches": sha256(Path(result["source"]["data_dir"]) / "dataBeamOnAC.txt") == result["source"]["beam_AC_sha256"],
        "ordered_population_window": recomputed_population_gates["P1_ordered_objective_window"],
        "saved_curve_strictly_increases": all(b > a for a, b in zip(x_curve, x_curve[1:])),
        "saved_curve_spans_local_zero_to_two": x_curve[0] < 0.02 and x_curve[-1] > 1.95,
        "population_gates_recompute": recomputed_population_gates == result["population_gates"],
        "event_gates_recompute": recomputed_event_gates == result["event_gates"],
        "histogram_effective_weight_recomputes": close(hist_total, event["effective_delayed_holdout"]),
        "saved_event_sample_weight_recomputes": close(sample_weight, event["effective_delayed_holdout"]),
        "saved_event_coordinates_in_window": all(0.0 <= float(row["local_child_ara"]) <= 2.0 for row in sample),
        "saved_membership_weights_are_probabilities": all(0.0 <= float(row["delayed_membership_weight"]) <= 1.0 for row in sample),
        "repeated_split_fraction_recomputes": close(split_fraction, result["repeated_splits"]["broad_ridge_mode_fraction"]),
        "leave_one_out_fraction_recomputes": close(loo_fraction, pop["loo_ridge_fraction"]),
        "phase_shift_p_recomputes": close(phase_p, pop["phase_shift_p_upper"]),
        "bootstrap_mode_fraction_recomputes": close(boot_ridge, result["event_bootstrap"]["broad_ridge_mode_fraction"]),
        "mode_sensitivity_saved": len(sensitivity) == 12,
        "visual_exists": (OUT / "T400_NESTED_CHILD_WINDOW.png").stat().st_size > 100_000,
        "claim_boundaries_are_explicit": all(phrase in boundary_text for phrase in required_boundary_phrases),
    }

    payload = {
        "test": "T400 independent saved-artifact validation",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "recomputed": {
            "effective_delayed_weight": hist_total,
            "split_ridge_fraction": split_fraction,
            "loo_ridge_fraction": loo_fraction,
            "phase_shift_p_upper": phase_p,
            "bootstrap_mode_fraction": boot_ridge,
            "population_gates": recomputed_population_gates,
            "event_gates": recomputed_event_gates,
        },
        "note": "Validation checks arithmetic and evidence boundaries; it does not convert failed scientific gates into passes.",
    }
    (OUT / "T400_VALIDATION.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    if payload["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
