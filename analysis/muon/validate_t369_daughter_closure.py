#!/usr/bin/env python3
"""Independent raw-source validation for T369 and T369C headline metrics."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "T368_SUPERK_DECAYES_AND_NEUTRONS_SOURCE.csv"
T369 = HERE / "T369_MUON_CAPTURE_DAUGHTER_CLOSURE_RESULTS.json"
T369C = HERE / "T369C_MUON_DAUGHTER_ENERGY_BRANCH_RESULTS.json"
OUTPUT = HERE / "T369_DAUGHTER_CLOSURE_VALIDATION.json"


def parse() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    p, t, m = [], [], []
    with SOURCE.open("r", newline="", encoding="utf-8") as handle:
        for row in csv.reader(handle):
            p.append(float(row[0]))
            t.append(float(row[1]))
            m.append(sum(bool(value) and float(value) > 0 for value in row[2:]))
    return np.asarray(p), np.asarray(t), np.asarray(m, dtype=np.int16)


def hashes(n: int) -> np.ndarray:
    return np.fromiter(
        (
            int.from_bytes(hashlib.sha256(f"T369|{i}".encode("ascii")).digest()[:8], "big")
            for i in range(1, n + 1)
        ),
        dtype=np.uint64,
        count=n,
    )


def rank_corr(x: np.ndarray, y: np.ndarray) -> float:
    xr = pd.Series(x).rank(method="average").to_numpy()
    yr = pd.Series(y).rank(method="average").to_numpy()
    return float(np.corrcoef(xr, yr)[0, 1])


def table(category: np.ndarray, target: np.ndarray, ncat: int, ntarget: int) -> np.ndarray:
    return np.bincount(category * ntarget + target, minlength=ncat * ntarget).reshape(ncat, ntarget)


def ce(test: np.ndarray, train: np.ndarray) -> float:
    n_target = train.shape[1]
    conditional = (train + 1) / (train.sum(axis=1, keepdims=True) + n_target)
    marginal = (train.sum(axis=0) + 1) / (train.sum() + n_target)
    c = -np.sum(test * np.log(conditional)) / test.sum()
    u = -np.sum(test * np.log(marginal)[None, :]) / test.sum()
    return float((u - c) / u)


def close(a: float, b: float, tol: float = 1e-12) -> bool:
    return abs(a - b) <= tol


def main() -> None:
    saved369 = json.loads(T369.read_text(encoding="utf-8"))
    savedc = json.loads(T369C.read_text(encoding="utf-8"))
    p, t, multiplicity = parse()
    h = hashes(len(p))
    capture = np.isfinite(p) & np.isfinite(t) & (p <= 15)
    dev = capture & ((h % 10) <= 5)
    hold = capture & ((h % 10) >= 6)
    prompt = (p > 0) & (p <= 15) & (t >= 1.1) & (t <= 5)
    neutron = multiplicity > 0
    dev_table = table(prompt[dev].astype(int), neutron[dev].astype(int), 2, 2)
    hold_table = table(prompt[hold].astype(int), neutron[hold].astype(int), 2, 2)
    common = ce(hold_table, dev_table)

    energy_edges = np.quantile(p[dev & prompt], np.arange(1, 8) / 8)
    selected = hold & prompt
    ebin = np.digitize(p[selected], energy_edges)
    strength = np.minimum(multiplicity[selected], 2)
    correlation = rank_corr(ebin, strength)
    counts = np.bincount(ebin, minlength=8)
    rates = np.bincount(ebin, weights=(strength > 0), minlength=8) / counts
    strict = selected & (p > 5)
    strict_corr = rank_corr(np.digitize(p[strict], energy_edges), np.minimum(multiplicity[strict], 2))
    halves = {
        f"hash_{parity}": rank_corr(
            np.digitize(p[selected & ((h & 1) == parity)], energy_edges),
            np.minimum(multiplicity[selected & ((h & 1) == parity)], 2),
        )
        for parity in (0, 1)
    }
    checks = {
        "row_count": len(p) == 1_986_465,
        "holdout_capture_count": int(hold.sum()) == saved369["source_qa"]["holdout_capture_enriched"],
        "holdout_prompt_count": int(selected.sum()) == savedc["n"],
        "common_parent_effect": close(common, saved369["primary"]["common_parent"]["cross_entropy"]["relative_improvement"]),
        "energy_edges": np.allclose(energy_edges, saved369["coordinate_edges"]["prompt_momentum_mev"], rtol=0, atol=1e-12),
        "signed_correlation": close(correlation, savedc["rank_correlation"]),
        "bin_rates": np.allclose(rates, savedc["neutron_presence_by_energy_bin"], rtol=0, atol=1e-12),
        "strict_correlation": close(strict_corr, savedc["strict_rank_correlation"]),
        "hash_half_0": close(halves["hash_0"], savedc["hash_halves"]["hash_0"]),
        "hash_half_1": close(halves["hash_1"], savedc["hash_halves"]["hash_1"]),
    }
    result = {
        "verdict": "PASS" if all(checks.values()) else "FAIL",
        "checks": {key: bool(value) for key, value in checks.items()},
        "independent_values": {
            "common_parent_effect": common,
            "signed_correlation": correlation,
            "neutron_rates": rates.tolist(),
            "strict_correlation": strict_corr,
            "hash_halves": halves,
        },
        "method": "Reparsed the checksum-locked raw CSV; did not import analysis code or derived arrays.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
