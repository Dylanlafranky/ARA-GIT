#!/usr/bin/env python3
"""Independent structural validation for frozen T306 outputs."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
PREFIX_FILE = HERE / "T306_EMBEDDED_E_PHI_THREAD_PREFIX_RESULTS.csv"
HARMONIC_FILE = HERE / "T306_EMBEDDED_E_PHI_THREAD_HARMONIC_SUMMARY.csv"
COUPLING_FILE = HERE / "T306_EMBEDDED_E_PHI_THREAD_COUPLING_SWEEP.csv"
RESULT_FILE = HERE / "T306_EMBEDDED_E_PHI_THREAD_RESULTS.json"
FIGURE_FILE = HERE / "T306_EMBEDDED_E_PHI_THREAD.png"
OUT_FILE = HERE / "T306_EMBEDDED_E_PHI_THREAD_VALIDATION.json"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
E_INV = 1.0 / math.e
ALPHAS = {
    "phi_time": PHI - 1.0,
    "anti_phi": PHI ** -2,
    "one_over_e": E_INV,
    "sqrt2_minus_1": math.sqrt(2.0) - 1.0,
    "pi_minus_3": math.pi - 3.0,
}
PAIRS = {
    "parent_phi_time_vs_e": ("phi_time", "one_over_e"),
    "child_anti_phi_vs_e": ("anti_phi", "one_over_e"),
    "control_phi_time_vs_sqrt2": ("phi_time", "sqrt2_minus_1"),
    "control_e_vs_sqrt2": ("one_over_e", "sqrt2_minus_1"),
    "control_phi_time_vs_pi3": ("phi_time", "pi_minus_3"),
    "control_e_vs_pi3": ("one_over_e", "pi_minus_3"),
    "control_sqrt2_vs_pi3": ("sqrt2_minus_1", "pi_minus_3"),
}
FAMILIES = ["beam7", "beam7_cycle23", "beam7_decay"]
PREFIXES = np.arange(65, 257)
WIDTH = 0.15 / 64.0


def harmonic_fit(n: np.ndarray, y: np.ndarray, period: float) -> float:
    centred = n - np.mean(n)
    baseline = np.column_stack([np.ones_like(centred), centred])
    angle = 2.0 * math.pi * n / period
    full = np.column_stack(
        [baseline, np.sin(angle), np.cos(angle)]
    )
    residual0 = y - baseline @ np.linalg.lstsq(baseline, y, rcond=None)[0]
    residual1 = y - full @ np.linalg.lstsq(full, y, rcond=None)[0]
    rss0 = float(np.sum(residual0 * residual0))
    rss1 = float(np.sum(residual1 * residual1))
    return 0.0 if rss0 <= 1e-30 else max(0.0, (rss0 - rss1) / rss0)


def merged_length(alpha: float, n: int) -> float:
    half = WIDTH / 2.0
    raw: list[tuple[float, float]] = []
    for centre in np.mod(np.arange(n, dtype=float) * alpha, 1.0):
        low = float(centre - half)
        high = float(centre + half)
        if low < 0:
            raw.extend([(0.0, high), (1.0 + low, 1.0)])
        elif high > 1:
            raw.extend([(low, 1.0), (0.0, high - 1.0)])
        else:
            raw.append((low, high))
    raw.sort()
    merged: list[list[float]] = []
    for low, high in raw:
        if not merged or low > merged[-1][1] + 1e-15:
            merged.append([low, high])
        else:
            merged[-1][1] = max(merged[-1][1], high)
    return float(sum(high - low for low, high in merged))


def main() -> None:
    prefix = pd.read_csv(PREFIX_FILE)
    harmonic = pd.read_csv(HARMONIC_FILE)
    coupling = pd.read_csv(COUPLING_FILE)
    result = json.loads(RESULT_FILE.read_text(encoding="utf-8"))

    row_structure = bool(
        len(prefix) == len(ALPHAS) * len(PREFIXES)
        and not prefix.duplicated(["candidate", "n"]).any()
        and set(prefix["candidate"]) == set(ALPHAS)
        and set(prefix["n"]) == set(PREFIXES)
    )
    coupling_structure = bool(
        len(coupling) == len(PREFIXES) * 21
        and not coupling.duplicated(["n", "coupling"]).any()
    )
    expected_harmonic_rows = len(PAIRS) * len(FAMILIES)
    harmonic_structure = bool(
        len(harmonic) == expected_harmonic_rows
        and not harmonic.duplicated(["pair", "family"]).any()
    )

    indexed = prefix.set_index(["candidate", "n"])
    independent_p4: dict[str, list[float]] = {pair: [] for pair in PAIRS}
    for pair, (left, right) in PAIRS.items():
        for family in FAMILIES:
            contrast = np.array(
                [
                    indexed.loc[(left, int(n)), f"{family}_p05"]
                    - indexed.loc[(right, int(n)), f"{family}_p05"]
                    for n in PREFIXES
                ],
                dtype=float,
            )
            independent_p4[pair].append(
                harmonic_fit(PREFIXES.astype(float), contrast, 4.0)
            )
    independent_means = {
        pair: float(np.mean(values)) for pair, values in independent_p4.items()
    }
    independent_winner = max(independent_means, key=independent_means.get)
    published_means = result["gates"]["details"]["period4_pair_ranking"]
    period4_match = bool(
        all(
            abs(independent_means[pair] - float(published_means[pair])) <= 2e-12
            for pair in PAIRS
        )
        and independent_winner == result["gates"]["details"]["G1_winner"]
    )

    pivot = coupling.pivot(
        index="coupling", columns="n", values="contrast_phi_minus_e"
    )
    switched = [
        int(n)
        for n in PREFIXES
        if float(pivot[n].min()) < -1e-12
        and float(pivot[n].max()) > 1e-12
    ]
    coupling_match = bool(
        switched
        == result["gates"]["details"]["coupling"]["switch_prefixes"]
        and abs(len(switched) / len(PREFIXES) - 0.3645833333333333) <= 1e-15
    )

    spot_rows = [
        ("phi_time", 73),
        ("anti_phi", 129),
        ("one_over_e", 256),
    ]
    coverage_errors = {}
    for candidate, n in spot_rows:
        direct = merged_length(ALPHAS[candidate], n)
        stored = float(indexed.loc[(candidate, n), "union_coverage"])
        coverage_errors[f"{candidate}_{n}"] = abs(direct - stored)
    coverage_match = max(coverage_errors.values()) <= 2e-12

    geometry = {
        "embedded_x0": E_INV,
        "embedded_x2": PHI,
        "embedded_centre": (PHI + E_INV) / 2.0,
        "parent_delta": (PHI - 1.0) - E_INV,
        "parent_pair_beat_recurrence": 1.0 / ((PHI - 1.0) - E_INV),
        "child_delta": PHI ** -2 - E_INV,
        "child_pair_beat_recurrence": 1.0 / (PHI ** -2 - E_INV),
    }
    published_geometry = result["geometry"]
    geometry_match = bool(
        abs(geometry["embedded_centre"] - published_geometry["embedded_centre_parent_coordinate"]) <= 1e-14
        and abs(geometry["parent_delta"] - published_geometry["parent_carrier_separation"]) <= 1e-14
        and abs(geometry["child_delta"] - published_geometry["child_carrier_separation"]) <= 1e-14
    )

    with Image.open(FIGURE_FILE) as figure:
        figure_ok = figure.format == "PNG" and figure.size == (1800, 1200)

    published_gates_consistent = bool(
        result["gates"]["G1_parent_four_step_thread"] is False
        and result["gates"]["G2_parent_child_rung_separation"] is False
        and result["gates"]["G3_coupling_driven_handover"] is True
        and result["gates"]["primary_pass_count"] == 1
        and result["gates"]["verdict"] == "NOT SUPPORTED"
    )
    checks = {
        "prefix_row_structure": row_structure,
        "harmonic_row_structure": harmonic_structure,
        "coupling_row_structure": coupling_structure,
        "period4_recalculation_matches": period4_match,
        "coupling_switch_recalculation_matches": coupling_match,
        "independent_union_coverage_spots_match": coverage_match,
        "exact_geometry_matches": geometry_match,
        "figure_is_valid_png": figure_ok,
        "published_gates_are_internally_consistent": published_gates_consistent,
    }
    payload = {
        "validation": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "independent_period4_ranking": dict(
            sorted(independent_means.items(), key=lambda item: item[1], reverse=True)
        ),
        "independent_winner": independent_winner,
        "independent_switch_count": len(switched),
        "independent_switch_fraction": len(switched) / len(PREFIXES),
        "coverage_absolute_errors": coverage_errors,
        "geometry": geometry,
        "scope": (
            "Structural and numerical validation of T306's synthetic scheduling "
            "calculation; not independent laboratory replication."
        ),
    }
    OUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
