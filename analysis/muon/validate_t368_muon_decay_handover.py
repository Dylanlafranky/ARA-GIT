#!/usr/bin/env python3
"""Independent validation of T368 saved results from raw source values."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T368_SUPERK_DECAYES_AND_NEUTRONS_SOURCE.csv"
RESULTS = HERE / "T368_MUON_DECAY_HANDOVER_RESULTS.json"
OUTPUT = HERE / "T368_MUON_DECAY_HANDOVER_VALIDATION.json"
N_BINS = 8


def hashes(n: int) -> np.ndarray:
    result = np.empty(n, dtype=np.uint64)
    for index in range(n):
        result[index] = int.from_bytes(
            hashlib.sha256(f"T368|{index + 1}".encode()).digest()[:8], "big"
        )
    return result


def table(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return np.bincount(a * N_BINS + b, minlength=64).reshape(8, 8)


def entropy(counts: np.ndarray) -> float:
    p = counts[counts > 0] / counts.sum()
    return float(-(p * np.log(p)).sum())


def close(a: float, b: float, tolerance: float = 1e-12) -> bool:
    return bool(abs(a - b) <= tolerance)


def main() -> None:
    saved = json.loads(RESULTS.read_text(encoding="utf-8"))
    frame = pd.read_csv(SOURCE, header=None, usecols=[0, 1], dtype=float)
    momentum = frame.iloc[:, 0].to_numpy()
    decay_time = frame.iloc[:, 1].to_numpy()
    row_hash = hashes(len(frame))
    residue = row_hash % 10
    eligible = (momentum > 15) & (decay_time >= 1.1) & (decay_time <= 5.0)
    development = eligible & (residue <= 5)
    holdout = eligible & (residue >= 6)

    time_edges = np.quantile(decay_time[development], np.arange(1, 8) / 8)
    momentum_edges = np.quantile(momentum[development], np.arange(1, 8) / 8)
    dev_t = np.digitize(decay_time[development], time_edges).astype(np.int64)
    dev_p = np.digitize(momentum[development], momentum_edges).astype(np.int64)
    hold_t = np.digitize(decay_time[holdout], time_edges).astype(np.int64)
    hold_p = np.digitize(momentum[holdout], momentum_edges).astype(np.int64)
    dev_table = table(dev_t, dev_p)
    hold_table = table(hold_t, hold_p)

    conditional = (dev_table + 1) / (dev_table.sum(axis=1, keepdims=True) + 8)
    marginal_counts = dev_table.sum(axis=0)
    marginal = (marginal_counts + 1) / (marginal_counts.sum() + 8)
    n = hold_table.sum()
    conditional_ce = -float(np.sum(hold_table * np.log(conditional))) / n
    marginal_ce = -float(np.sum(hold_table * np.log(marginal)[None, :])) / n
    improvement = (marginal_ce - conditional_ce) / marginal_ce
    early = entropy(hold_table[:2].sum(axis=0))
    late = entropy(hold_table[-2:].sum(axis=0))
    narrowing = (late - early) / early

    saved_primary = saved["primary"]
    checks = {
        "row_count": len(frame) == saved["source_qa"]["rows"],
        "development_count": int(development.sum()) == saved_primary["development_n"],
        "holdout_count": int(holdout.sum()) == saved_primary["holdout_n"],
        "time_edges": np.allclose(time_edges, saved_primary["time_edges"], rtol=0, atol=1e-12),
        "momentum_edges": np.allclose(momentum_edges, saved_primary["momentum_edges"], rtol=0, atol=1e-12),
        "development_table": np.array_equal(dev_table, saved_primary["development_table"]),
        "holdout_table": np.array_equal(hold_table, saved_primary["holdout_table"]),
        "conditional_cross_entropy": close(conditional_ce, saved_primary["cross_entropy"]["conditional_cross_entropy"]),
        "unconditional_cross_entropy": close(marginal_ce, saved_primary["cross_entropy"]["unconditional_cross_entropy"]),
        "relative_improvement": close(improvement, saved_primary["cross_entropy"]["relative_improvement"]),
        "narrowing": close(narrowing, saved_primary["narrowing"]["relative_change"]),
        "verdict_consistent": saved["verdict"] == "NO OBSERVABLE PREFORMATION IN THE RELEASED VARIABLES",
    }
    payload = {
        "validation": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "independent_values": {
            "conditional_cross_entropy": conditional_ce,
            "unconditional_cross_entropy": marginal_ce,
            "relative_improvement": improvement,
            "early_entropy": early,
            "late_entropy": late,
            "relative_narrowing": narrowing,
        },
        "boundary": "Independent recomputation validates the saved numerical result; it does not add new observables absent from the public archive.",
    }
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
