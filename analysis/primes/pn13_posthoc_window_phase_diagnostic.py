#!/usr/bin/env python3
"""Post-hoc PN13 diagnostic: does signed coupling depend on local window phase?

This does not alter the frozen PN13 verdict. It repeats the unchanged one-million-
integer instrument on ten consecutive windows at each tested decimal scale.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import numpy as np

from pn10b_child_phase_prime_ranking import base_primes, segmented_least_prime_factor
from pn13_decimal_rung_leak import child_couplings


HERE = Path(__file__).resolve().parent
WIDTH = 1_000_000
WINDOWS = 10
BASES = {8: 400_000_000, 9: 4_000_000_000, 10: 40_000_000_000}
OUTPUT = HERE / "PN13_POSTHOC_WINDOW_PHASE_RESULTS.json"
CSV_OUTPUT = HERE / "PN13_POSTHOC_WINDOW_PHASE_WINDOWS.csv"


def one_window(low: int) -> dict[str, float | int]:
    high = low + WIDTH
    numbers, least_factor = segmented_least_prime_factor(low, high)
    threshold = numbers.astype(np.float64) ** 0.45
    prime_mask = least_factor == 0
    late_mask = (~prime_mask) & (least_factor.astype(np.float64) > threshold)
    prime_values, _ = child_couplings(numbers[prime_mask])
    late_values, _ = child_couplings(numbers[late_mask])
    return {
        "low": low,
        "high": high,
        "prime_count": int(np.count_nonzero(prime_mask)),
        "prime_mean": float(np.mean(prime_values)),
        "prime_se_independent_only": float(np.std(prime_values) / math.sqrt(len(prime_values))),
        "late_composite_count": int(np.count_nonzero(late_mask)),
        "late_composite_mean": float(np.mean(late_values)),
    }


def local_gate_beat_geometry(n: int) -> dict[str, object]:
    threshold = n**0.45
    table = base_primes(int(math.ceil(threshold)) + 2)
    last = int(np.searchsorted(table, threshold, side="right") - 1)
    gates = table[last - np.arange(9, dtype=np.int64)]
    pairs: list[dict[str, float | int]] = []
    for first64, second64 in zip(gates[:-1], gates[1:]):
        first = int(first64)
        second = int(second64)
        gap = abs(first - second)
        relative_phase_beat = first * second / gap
        pairs.append(
            {
                "gate_a": first,
                "gate_b": second,
                "gap": gap,
                "joint_repeat": first * second,
                "relative_phase_beat": relative_phase_beat,
                "one_million_window_share_of_beat": WIDTH / relative_phase_beat,
            }
        )
    beats = np.asarray([row["relative_phase_beat"] for row in pairs], dtype=np.float64)
    repeats = np.asarray([row["joint_repeat"] for row in pairs], dtype=np.float64)
    return {
        "n": n,
        "threshold_n_pow_0p45": threshold,
        "gates_descending": [int(value) for value in gates],
        "adjacent_pairs": pairs,
        "median_exact_joint_repeat": float(np.median(repeats)),
        "median_relative_phase_beat": float(np.median(beats)),
        "one_million_window_share_of_median_beat": float(WIDTH / np.median(beats)),
    }


def main() -> None:
    rows: list[dict[str, float | int]] = []
    for scale, base in BASES.items():
        for window in range(WINDOWS):
            row = one_window(base + window * WIDTH)
            row["scale"] = scale
            row["window"] = window
            rows.append(row)

    summaries: dict[str, dict[str, float | int]] = {}
    for scale in BASES:
        selected = [row for row in rows if row["scale"] == scale]
        prime = np.asarray([row["prime_mean"] for row in selected], dtype=np.float64)
        late = np.asarray([row["late_composite_mean"] for row in selected], dtype=np.float64)
        summaries[str(scale)] = {
            "window_count": len(selected),
            "prime_window_mean": float(np.mean(prime)),
            "prime_window_sd": float(np.std(prime)),
            "prime_window_min": float(np.min(prime)),
            "prime_window_max": float(np.max(prime)),
            "prime_positive_windows": int(np.count_nonzero(prime > 0)),
            "prime_negative_windows": int(np.count_nonzero(prime < 0)),
            "late_window_mean": float(np.mean(late)),
            "prime_late_window_correlation": float(np.corrcoef(prime, late)[0, 1]),
        }

    result = {
        "status": "POST-HOC DIAGNOSTIC; DOES NOT CHANGE PN13 REGISTERED VERDICTS",
        "definition": "ten consecutive one-million-integer windows at each scale; unchanged K=9 and n^0.45 gates",
        "summaries": summaries,
        "local_gate_beat_geometry": {
            str(scale): local_gate_beat_geometry(base) for scale, base in BASES.items()
        },
        "analytic_scaling_note": {
            "paid_gate_exponent": 0.45,
            "joint_repeat_exponent": 0.90,
            "predicted_joint_repeat_factor_per_decimal_integer_rung": 10.0**0.90,
            "full_sqrt_gate_counterfactual_exponent": 1.0,
            "full_sqrt_gate_factor_per_decimal_integer_rung": 10.0,
            "interpretation": "For adjacent prime gates q,r near n^a, exact joint closure is q*r and therefore scales approximately as n^(2a). This concerns wavelength/closure length, not residual amplitude.",
        },
        "windows": rows,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with CSV_OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUTPUT.name} and {CSV_OUTPUT.name}")


if __name__ == "__main__":
    main()
