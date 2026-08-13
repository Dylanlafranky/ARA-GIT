#!/usr/bin/env python3
"""Validate exported T343 temporal-leakage audit summaries."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
STEM = "T343_BROKEN_CONTROL_TEMPORAL_LEAKAGE_AUDIT"
CONTROLS = HERE / f"{STEM}_CONTROLS.csv"
SUMMARY = HERE / f"{STEM}_SUMMARY.csv"
RESULTS = HERE / f"{STEM}_RESULTS.json"
FIGURE = HERE / f"{STEM}_FIGURE.png"
REPORT = HERE / f"{STEM}_REPORT_2026-08-05.md"
DOMAINS = ("pendulum", "hydraulic", "bubbles", "cold_room", "acoustics", "qutrit", "river")


def require(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def close(a: float, b: float, message: str, tol: float = 2e-12) -> None:
    if math.isnan(a) and math.isnan(b):
        return
    require(abs(float(a) - float(b)) <= tol, f"{message}: {a} != {b}")


def main() -> None:
    for path in (CONTROLS, SUMMARY, RESULTS, FIGURE, REPORT):
        require(path.exists() and path.stat().st_size > 0, f"missing {path.name}")
    controls = pd.read_csv(CONTROLS)
    summary = pd.read_csv(SUMMARY)
    results = json.loads(RESULTS.read_text(encoding="utf-8"))
    require(tuple(summary.domain) == DOMAINS, "domain order")
    require(len(controls) == 7000, "control count")
    require("post-result" in results["status"], "evidence label")
    for row in summary.itertuples(index=False):
        part = controls[controls.domain == row.domain].sort_values("replicate")
        require(len(part) == 1000, f"{row.domain} controls")
        require(np.array_equal(part.replicate.to_numpy(int), np.arange(1, 1001)), f"{row.domain} ids")
        require(np.all((part.original_circular_future_share >= 0) & (part.original_circular_future_share <= 1)), f"{row.domain} future range")
        close(part.original_circular_future_share.median(), row.median_original_future_share, f"{row.domain} future median")
        close(part.original_circular_future_share.quantile(.95), row.q95_original_future_share, f"{row.domain} future q95")
        close(part.original_circular_direct_target_share.median(), row.median_original_direct_target_share, f"{row.domain} direct median")
        require(int((part.original_circular_direct_target_share > .05).sum()) == row.controls_with_direct_target_share_over_05, f"{row.domain} direct count")
        valid = part[np.isfinite(part.causal_delta) & (part.causal_holdout_transitions >= 1000)]
        require(len(valid) == row.eligible_causal_controls, f"{row.domain} causal eligibility")
        if len(valid):
            close(valid.causal_delta.median(), row.median_causal_delta, f"{row.domain} causal median")
            close(valid.causal_delta.quantile(.05), row.q05_causal_delta, f"{row.domain} causal q05")
            close(valid.causal_delta.quantile(.95), row.q95_causal_delta, f"{row.domain} causal q95")
            p = (1 + np.count_nonzero(valid.causal_delta.to_numpy(float) <= 0)) / (len(valid) + 1)
            close(p, row.p_causal_broken_not_worse, f"{row.domain} causal p")
            passed = bool(len(valid) >= 100 and valid.causal_delta.median() > 0 and p <= .05)
            require(passed == bool(row.causal_pairing_pass), f"{row.domain} causal pass")
        else:
            require(not bool(row.causal_pairing_pass), f"{row.domain} empty pass")
    require(int(summary.causal_pairing_pass.sum()) == 3, "expected descriptive pass count")
    print("PASS: T343 temporal-leakage audit artifacts validated (3 causal sensitivity passes; post-result only).")


if __name__ == "__main__":
    main()
