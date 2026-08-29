#!/usr/bin/env python3
"""Labelled post-result diagnostics for T417 boundary censoring and shift availability."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

import t417_coupled_rationality_irrationality_handover as t417


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SEED = 417417
DRAWS = 1000


def early_or_full_crossing(time: np.ndarray, r_wave: np.ndarray, i_wave: np.ndarray) -> tuple[float, str]:
    full = t417.first_balance_crossing(time, r_wave, i_wave)
    if np.isfinite(full):
        return full, "fully observed"
    difference = i_wave - r_wave
    if np.all(difference[:3] > 0):
        return float(time[0]), "left-censored: already I-leading"
    for index in range(1, min(3, len(difference) - 2)):
        if difference[index - 1] <= 0 and np.all(difference[index : index + 3] > 0):
            left, right = float(difference[index - 1]), float(difference[index])
            fraction = 0.0 if abs(right - left) < t417.EPS else -left / (right - left)
            at = float(time[index - 1] + fraction * (time[index] - time[index - 1]))
            return at, "left-censored: boundary crossing"
    return float("nan"), "not recovered"


def main() -> None:
    source = t417.T416 / "results" / "T416_VALIDATION_TIMELINE.csv"
    rows = t417.load_csv(source)
    groups = t417.grouped(rows)
    diagnostics: list[dict] = []
    for key in sorted(groups):
        arrays = t417.sequence_arrays(groups[key])
        crossing, classification = early_or_full_crossing(arrays["time"], arrays["R"], arrays["I"])
        saturation = t417.first_saturation(arrays["time"], arrays["I"])
        first = groups[key][0]
        diagnostics.append({
            "run": first["run"],
            "period": first["period"],
            "field_G": float(first["field_G"]),
            "classification": classification,
            "crossing_time_us": crossing,
            "crossing_parent_ARA": t417.interpolate_at(arrays["time"], arrays["parent"], crossing),
            "saturation_time_us": saturation,
            "lead_us": float(saturation - crossing) if np.isfinite(crossing) and np.isfinite(saturation) else float("nan"),
            "start_balance_B": float(arrays["B"][0]),
            "start_R": float(arrays["R"][0]),
            "start_I": float(arrays["I"][0]),
        })

    rng = np.random.default_rng(SEED)
    null_cross_counts: list[int] = []
    null_eligible_counts: list[int] = []
    null_ordered_counts: list[int] = []
    for _ in range(DRAWS):
        cross_count = 0
        eligible_count = 0
        ordered_count = 0
        for key in sorted(groups):
            arrays = t417.sequence_arrays(groups[key])
            shifted_r = np.roll(arrays["R"], t417.random_nontrivial_shift(rng, len(arrays["R"])))
            crossing = t417.first_balance_crossing(arrays["time"], shifted_r, arrays["I"])
            saturation = t417.first_saturation(arrays["time"], arrays["I"])
            if np.isfinite(crossing):
                cross_count += 1
            if np.isfinite(crossing) and np.isfinite(saturation):
                eligible_count += 1
                ordered_count += int(crossing < saturation)
        null_cross_counts.append(cross_count)
        null_eligible_counts.append(eligible_count)
        null_ordered_counts.append(ordered_count)

    observed_full = int(sum(row["classification"] == "fully observed" for row in diagnostics))
    observed_any = int(sum(row["classification"] != "not recovered" for row in diagnostics))
    observed_ordered = int(sum(bool(np.isfinite(float(row["lead_us"]))) and float(row["lead_us"]) > 0 for row in diagnostics))
    p_full_count = float((1 + np.count_nonzero(np.asarray(null_eligible_counts) >= observed_full)) / (DRAWS + 1))
    p_ordered_count = float((1 + np.count_nonzero(np.asarray(null_ordered_counts) >= observed_ordered)) / (DRAWS + 1))
    counts = {name: int(sum(row["classification"] == name for row in diagnostics)) for name in sorted({row["classification"] for row in diagnostics})}
    payload = {
        "label": "POST-RESULT DIAGNOSTIC; does not modify T417 gates",
        "classification_counts": counts,
        "full_crossings": observed_full,
        "full_or_boundary_censored_crossings": observed_any,
        "ordered_full_or_boundary_crossings": observed_ordered,
        "shift_null_eligible_count": {
            "median": float(np.median(null_eligible_counts)),
            "q025": float(np.percentile(null_eligible_counts, 2.5)),
            "q975": float(np.percentile(null_eligible_counts, 97.5)),
            "maximum": int(np.max(null_eligible_counts)),
            "p_null_at_least_observed_full": p_full_count,
        },
        "shift_null_ordered_count": {
            "median": float(np.median(null_ordered_counts)),
            "q025": float(np.percentile(null_ordered_counts, 2.5)),
            "q975": float(np.percentile(null_ordered_counts, 97.5)),
            "maximum": int(np.max(null_ordered_counts)),
            "p_null_at_least_observed_boundary_ordered": p_ordered_count,
        },
        "interpretation_boundary": "Censoring can explain missing full crossings but cannot upgrade the frozen verdict.",
    }
    t417.write_csv(RESULTS / "T417_POSTHOC_BOUNDARY_CLASSIFICATION.csv", diagnostics)
    t417.write_csv(RESULTS / "T417_POSTHOC_SHIFT_COUNTS.csv", [
        {
            "draw": index,
            "crossing_count": null_cross_counts[index],
            "eligible_count": null_eligible_counts[index],
            "ordered_count": null_ordered_counts[index],
        }
        for index in range(DRAWS)
    ])
    t417.write_json(RESULTS / "T417_POSTHOC_DIAGNOSTICS.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
