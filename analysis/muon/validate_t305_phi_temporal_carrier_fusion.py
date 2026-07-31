#!/usr/bin/env python3
"""Independent validation of T305 result artifacts."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PREFIX_PATH = HERE / "T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_PREFIX_RESULTS.csv"
SUMMARY_PATH = HERE / "T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_SUMMARY.csv"
RESULT_PATH = HERE / "T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_RESULTS.json"
OUT_PATH = HERE / "T305_ARA_PHI_TEMPORAL_CARRIER_FUSION_VALIDATION.json"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
WIDTH = 0.15 / 64.0
PHASES = np.linspace(0.0, 2.0 * math.pi, 128, endpoint=False)
NONFLAT = ["beam7", "beam7_cycle23", "beam7_decay"]
FORWARD = [
    "phi",
    "three_eighths",
    "eight_twentyone",
    "one_over_e",
    "two_fifths",
    "sqrt2_minus_1",
    "one_third",
    "pi_minus_3",
]
ALPHAS = {
    "phi": PHI ** -2,
    "phi_reverse": PHI ** -1,
    "three_eighths": 3 / 8,
    "eight_twentyone": 8 / 21,
    "one_over_e": 1 / math.e,
    "two_fifths": 2 / 5,
    "sqrt2_minus_1": math.sqrt(2) - 1,
    "one_third": 1 / 3,
    "pi_minus_3": math.pi - 3,
}


def check(name: str, passed: bool, detail, checks: list[dict]) -> None:
    checks.append({"check": name, "passed": bool(passed), "detail": detail})


def direct_centres(name: str, n: int) -> np.ndarray:
    if name == "oracle_uniform":
        return (np.arange(n, dtype=float) + 0.5) / n
    return np.mod(np.arange(n, dtype=float) * ALPHAS[name], 1.0)


def direct_coverage(name: str, n: int, m: int = 80_000) -> tuple[np.ndarray, np.ndarray]:
    t = (np.arange(m) + 0.5) / m
    c = np.zeros(m, dtype=bool)
    half = WIDTH / 2
    for centre in direct_centres(name, n):
        distance = np.abs(t - centre)
        distance = np.minimum(distance, 1.0 - distance)
        c |= distance <= half
    return t, c


def direct_arrival(t: np.ndarray, family: str, phase: float) -> np.ndarray:
    if family == "beam7":
        g = 1.0 + 0.85 * np.cos(2 * math.pi * 7 * t + phase)
    elif family == "beam7_cycle23":
        g = (
            1.0 + 0.6 * np.cos(2 * math.pi * 7 * t + phase)
        ) * (
            1.0 + 0.6 * np.cos(2 * math.pi * 23 * t + 1.7 * phase)
        )
    elif family == "beam7_decay":
        g = np.exp(-t / 0.45) * (
            1.0 + 0.85 * np.cos(2 * math.pi * 7 * t + phase)
        )
    else:
        raise KeyError(family)
    return g / g.mean()


def direct_phase_stats(name: str, n: int, family: str) -> dict:
    t, coverage = direct_coverage(name, n)
    values = []
    for phase in PHASES:
        values.append(float(np.mean(direct_arrival(t, family, phase) * coverage)))
    values = np.asarray(values)
    return {
        "mean": float(values.mean()),
        "p05": float(np.percentile(values, 5)),
        "min": float(values.min()),
    }


def recompute_summary(prefix: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, group in prefix.groupby("candidate", sort=False):
        cells = group[[f"{f}_p05" for f in NONFLAT]].to_numpy().ravel()
        row = {
            "candidate": name,
            "geometry_mean_rank": (
                float(
                    np.nanmean(
                        group[
                            ["largest_gap_rank", "discrepancy_rank"]
                        ].to_numpy()
                    )
                )
                if name in FORWARD
                else np.nan
            ),
            "fusion_robust_overlap_mean": float(np.mean(cells)),
            "fusion_robust_overlap_tail_p05": float(np.percentile(cells, 5)),
        }
        rows.append(row)
    return pd.DataFrame(rows).set_index("candidate")


def main() -> None:
    prefix = pd.read_csv(PREFIX_PATH)
    summary = pd.read_csv(SUMMARY_PATH).set_index("candidate")
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    checks: list[dict] = []

    check("prefix rows 10x61", len(prefix) == 610, len(prefix), checks)
    check(
        "unique candidate-prefix rows",
        not prefix.duplicated(["candidate", "n"]).any(),
        int(prefix.duplicated(["candidate", "n"]).sum()),
        checks,
    )
    check(
        "every candidate has N=4..64",
        all(
            group["n"].tolist() == list(range(4, 65))
            for _, group in prefix.sort_values("n").groupby("candidate")
        ),
        "checked",
        checks,
    )
    check(
        "flat equals union coverage",
        bool(np.allclose(prefix["flat_mean"], prefix["union_coverage"], atol=1e-12)),
        float(np.max(np.abs(prefix["flat_mean"] - prefix["union_coverage"]))),
        checks,
    )
    score_cols = [
        c for c in prefix.columns
        if c.endswith("_mean") or c.endswith("_p05") or c.endswith("_min")
    ]
    check(
        "all overlap scores bounded",
        bool(((prefix[score_cols] >= -1e-12) & (prefix[score_cols] <= 1 + 1e-12)).all().all()),
        [float(prefix[score_cols].min().min()), float(prefix[score_cols].max().max())],
        checks,
    )

    reconstructed = recompute_summary(prefix)
    for column in [
        "geometry_mean_rank",
        "fusion_robust_overlap_mean",
        "fusion_robust_overlap_tail_p05",
    ]:
        delta = (
            reconstructed[column].sort_index()
            - summary[column].sort_index()
        ).abs()
        delta = delta.dropna()
        check(
            f"reconstruct {column}",
            bool((delta <= 5e-12).all()),
            float(delta.max()) if len(delta) else 0.0,
            checks,
        )

    geometry_winner = str(
        summary.loc[FORWARD, "geometry_mean_rank"].idxmin()
    )
    fusion_winner = str(
        summary.loc[FORWARD, "fusion_robust_overlap_mean"].idxmax()
    )
    tail_winner = str(
        summary.loc[FORWARD, "fusion_robust_overlap_tail_p05"].idxmax()
    )
    check("geometry winner Phi", geometry_winner == "phi", geometry_winner, checks)
    check("Fusion mean winner Phi", fusion_winner == "phi", fusion_winner, checks)
    check("Fusion tail winner 1/e", tail_winner == "one_over_e", tail_winner, checks)
    check(
        "reverse Phi best overall mean",
        summary["fusion_robust_overlap_mean"].idxmax() == "oracle_uniform"
        and summary.drop(index="oracle_uniform")["fusion_robust_overlap_mean"].idxmax()
        == "phi_reverse",
        {
            "all": str(summary["fusion_robust_overlap_mean"].idxmax()),
            "fixed": str(
                summary.drop(index="oracle_uniform")[
                    "fusion_robust_overlap_mean"
                ].idxmax()
            ),
        },
        checks,
    )

    # Direct dense-grid checks use a separate implementation.
    spot_specs = [
        ("phi", 64, "beam7"),
        ("phi", 64, "beam7_decay"),
        ("phi_reverse", 37, "beam7_cycle23"),
        ("three_eighths", 64, "beam7_decay"),
        ("one_over_e", 4, "beam7_decay"),
        ("one_over_e", 64, "beam7"),
    ]
    spot_results = []
    for name, n, family in spot_specs:
        direct = direct_phase_stats(name, n, family)
        row = prefix[
            (prefix["candidate"] == name) & (prefix["n"] == n)
        ].iloc[0]
        deltas = {
            stat: abs(direct[stat] - float(row[f"{family}_{stat}"]))
            for stat in ["mean", "p05", "min"]
        }
        spot_results.append(
            {
                "candidate": name,
                "n": n,
                "family": family,
                "direct": direct,
                "absolute_deltas": deltas,
            }
        )
    worst_spot = max(
        delta
        for spot in spot_results
        for delta in spot["absolute_deltas"].values()
    )
    check("independent dense-grid spot checks", worst_spot <= 5e-4, worst_spot, checks)

    gates = result["gates"]
    check(
        "stored verdict is mixed 2/3",
        gates["verdict"] == "MIXED" and gates["primary_pass_count"] == 2,
        {"verdict": gates["verdict"], "primary": gates["primary_pass_count"]},
        checks,
    )
    check(
        "stored gate pattern",
        [
            gates["G0_implementation"],
            gates["G1_geometry"],
            gates["G2_fusion_mean_robust_overlap"],
            gates["G3_fusion_tail_robustness"],
            gates["G4_stationary_null"],
        ] == [True, True, True, False, True],
        gates,
        checks,
    )

    validation = {
        "test": "T305 independent validation",
        "checks": checks,
        "passed": sum(int(x["passed"]) for x in checks),
        "total": len(checks),
        "all_passed": all(x["passed"] for x in checks),
        "dense_spot_checks": spot_results,
    }
    OUT_PATH.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    print(json.dumps({
        "passed": validation["passed"],
        "total": validation["total"],
        "all_passed": validation["all_passed"],
        "worst_dense_delta": worst_spot,
    }, indent=2))
    if not validation["all_passed"]:
        for item in checks:
            if not item["passed"]:
                print("FAILED", item)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

