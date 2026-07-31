"""Independent deterministic checks for the frozen ordered-recurrence result.

This validator reads only the saved cycle table and result JSON.  It
reconstructs candidate geometry, matched-stratum correlations, data hashes,
and the frozen verdict without loading or calling the analysis module.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os

import numpy as np
from scipy.stats import spearmanr


HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "phi_ordered_recurrence_cycles.csv")
JSON_PATH = os.path.join(HERE, "phi_ordered_recurrence_results.json")
PHI = (1.0 + math.sqrt(5.0)) / 2.0
CANDIDATES = {
    "phi": PHI**-2,
    "three_eighths": 3.0 / 8.0,
    "two_fifths": 2.0 / 5.0,
    "sqrt2_conjugate": math.sqrt(2.0) - 1.0,
    "third": 1.0 / 3.0,
    "quarter": 1.0 / 4.0,
    "e_conjugate": 3.0 - math.e,
    "pi_conjugate": math.pi - 3.0,
}


def sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def orbit_gaps(alpha: float) -> np.ndarray:
    points = np.sort(np.mod(np.arange(4, dtype=float) * alpha, 1.0))
    return np.diff(np.r_[points, points[0] + 1.0])


def orientations(template: np.ndarray) -> list[np.ndarray]:
    values: list[np.ndarray] = []
    for base in (template, template[::-1]):
        for shift in range(4):
            candidate = np.roll(base, shift)
            if not any(np.allclose(candidate, old) for old in values):
                values.append(candidate)
    return values


TEMPLATES = {
    name: orientations(orbit_gaps(alpha)) for name, alpha in CANDIDATES.items()
}


def gap_distance(row: dict, name: str) -> float:
    mu = np.sort(
        np.array([row["mu_AA"], row["mu_AB"], row["mu_BB"], row["mu_BA"]])
    )
    gaps = np.diff(np.r_[mu, mu[0] + 1.0])
    return float(
        min(0.5 * np.sum(np.abs(gaps - template)) for template in TEMPLATES[name])
    )


def fold_step(alpha: float) -> float:
    return float(min(alpha % 1.0, 1.0 - alpha % 1.0))


def drift_distance(row: dict, name: str) -> float:
    return abs(row["rotation_folded"] - fold_step(CANDIDATES[name]))


def score(row: dict, name: str) -> float:
    return float(
        np.clip(
            1.0
            - 0.5 * (gap_distance(row, name) + 2.0 * drift_distance(row, name)),
            0.0,
            1.0,
        )
    )


def read_rows() -> list[dict]:
    text_columns = {"run", "stratum"}
    rows: list[dict] = []
    with open(CSV_PATH, newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle):
            row = {
                key: value if key in text_columns else float(value)
                for key, value in source.items()
            }
            rows.append(row)
    return rows


def usable_strata(rows: list[dict]) -> dict[str, list[dict]]:
    strata: dict[str, list[dict]] = {}
    for row in rows:
        if np.isfinite(row["next_retention"]):
            strata.setdefault(row["stratum"], []).append(row)
    return {key: values for key, values in strata.items() if len(values) >= 3}


def conditional_rho(rows: list[dict], name: str) -> tuple[int, int, float]:
    x_all: list[float] = []
    y_all: list[float] = []
    strata = usable_strata(rows)
    for values in strata.values():
        x = np.array([score(row, name) for row in values])
        y = np.array([row["next_retention"] for row in values])
        x_all.extend((x - x.mean()).tolist())
        y_all.extend((y - y.mean()).tolist())
    rho = float(spearmanr(np.asarray(x_all), np.asarray(y_all)).statistic)
    return len(x_all), len(strata), rho


def resonance_counts(rows: list[dict]) -> tuple[int, int, float]:
    repeat: list[float] = []
    nonclosing: list[float] = []
    for values in usable_strata(rows).values():
        retention = np.array([row["next_retention"] for row in values])
        residual = retention - retention.mean()
        labels = []
        local_values = []
        for value, row in zip(residual, values):
            drift = row["rotation_folded"]
            label = 0 if drift < 0.05 else (1 if 0.10 <= drift <= 0.45 else -1)
            if label >= 0:
                labels.append(label)
                local_values.append(float(value))
        if len(local_values) >= 2 and set(labels) == {0, 1}:
            repeat.extend(v for v, label in zip(local_values, labels) if label == 0)
            nonclosing.extend(
                v for v, label in zip(local_values, labels) if label == 1
            )
    difference = float(np.median(nonclosing) - np.median(repeat))
    return len(repeat), len(nonclosing), difference


def close(a: float, b: float, tolerance: float = 1e-12) -> None:
    if not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError(f"{a!r} != {b!r}")


def main() -> None:
    rows = read_rows()
    with open(JSON_PATH, encoding="utf-8") as handle:
        result = json.load(handle)

    if len(rows) != 158:
        raise AssertionError(f"Expected 158 cycles, found {len(rows)}")

    for row in rows:
        close(
            row["te_AA"] + row["te_AB"] + row["te_BB"] + row["te_BA"],
            2.0,
        )

    for run, metadata in result["data_quality"].items():
        if sha256(metadata["path"]) != metadata["sha256"]:
            raise AssertionError(f"Hash mismatch for {run}")

    pooled = [row for row in rows if row["run"] in {"run2", "run3"}]
    finite = [row for row in pooled if np.isfinite(row["next_retention"])]
    saved = result["pooled_frozen_run2_run3"]

    gap_medians = {
        name: float(np.median([gap_distance(row, name) for row in finite]))
        for name in CANDIDATES
    }
    drift_medians = {
        name: float(np.median([drift_distance(row, name) for row in finite]))
        for name in CANDIDATES
    }
    for name in CANDIDATES:
        close(gap_medians[name], saved["gap_candidate_median_distance"][name])
        close(drift_medians[name], saved["drift_candidate_median_distance"][name])
        n, n_strata, rho = conditional_rho(pooled, name)
        association = saved["conditional_retention"][name]
        if n != association["n"] or n_strata != association["n_strata"]:
            raise AssertionError(f"Matched-stratum count mismatch for {name}")
        close(rho, association["spearman_r"])

    repeat_n, nonclosing_n, difference = resonance_counts(pooled)
    resonance = saved["resonance_death"]
    if repeat_n != resonance["n_repeat"] or nonclosing_n != resonance["n_nonclosing"]:
        raise AssertionError("Resonance group count mismatch")
    close(difference, resonance["difference_nonclosing_minus_repeat"])

    if min(gap_medians, key=gap_medians.get) != "quarter":
        raise AssertionError("Expected quarter to be the pooled gap winner")
    if min(drift_medians, key=drift_medians.get) != "pi_conjugate":
        raise AssertionError("Expected pi-conjugate to be the nonzero drift winner")
    if result["verdict"]["checks_passed"] != 0:
        raise AssertionError("Frozen verdict was not 0/5")

    print("validation: PASS")
    print(f"cycles={len(rows)} pooled_transitions={len(finite)}")
    print(
        "pooled gap best=quarter "
        f"({gap_medians['quarter']:.9f}); phi={gap_medians['phi']:.9f}"
    )
    print(
        "pooled median folded movement="
        f"{np.median([row['rotation_folded'] for row in finite]):.9f}"
    )
    print(
        "phi conditional retention rho="
        f"{saved['conditional_retention']['phi']['spearman_r']:.6f}"
    )
    print(
        f"resonance matched n={repeat_n}+{nonclosing_n}; "
        f"difference={difference:.6f}"
    )
    print("frozen verdict=NOT SUPPORTED (0/5)")


if __name__ == "__main__":
    main()
