#!/usr/bin/env python3
"""T401: test whether T400's missing winning band is an anti-phase shadow.

The test retains every split's complete distribution.  It separates occupancy
from dominance, removes the fixed-bin edge with a KDE mode, compares the exact
ARA reflection with every other lower/upper pairing, and uses the AC records as
a negative control.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "_vendor"
EXTRA = Path(r"F:\SystemFormulaFolder\.codex_python_packages")
for entry in (EXTRA, VENDOR):
    if entry.exists():
        sys.path.insert(0, str(entry))

os.environ.setdefault("MPLCONFIGDIR", str(HERE / "_mplconfig"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import binomtest, spearmanr

import t400_nested_child_window_population_to_event as t400


OUT = HERE / "T401_winner_projection_child_antiphase"
PROTOCOL = HERE / "T401_WINNER_PROJECTION_CHILD_ANTIPHASE_PROTOCOL_2026-08-17.md"
SEED_START = 400
N_SPLITS = 200
KDE_BANDWIDTH = 0.15
GAP_LOW = 1.25
GAP_HIGH = 1.50
NULL_SINGLE_DRAWS = 200_000
NULL_EXPERIMENTS = 50_000
EDGES = np.linspace(0.0, 2.0, 9)
CENTERS = (EDGES[:-1] + EDGES[1:]) / 2.0
GRID = np.linspace(0.0, 2.0, 2001)
GAP_INDEX = int(np.where(np.isclose(CENTERS, 1.375))[0][0])
LOWER = (0, 1, 2, 3)
UPPER = (4, 5, 6, 7)
REFLECTION = (7, 6, 5, 4)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def weighted_kde_mode(x: np.ndarray, weights: np.ndarray) -> float:
    if len(x) == 0 or float(np.sum(weights)) <= 0:
        return float("nan")
    density = np.zeros_like(GRID)
    # Chunking avoids an unnecessary event-by-grid allocation for AC records.
    for start in range(0, len(x), 256):
        stop = min(start + 256, len(x))
        density += np.sum(
            weights[start:stop, None]
            * np.exp(-0.5 * ((GRID[None, :] - x[start:stop, None]) / KDE_BANDWIDTH) ** 2),
            axis=0,
        )
    return float(GRID[int(np.argmax(density))])


def effective_sample_size(weights: np.ndarray) -> float:
    total = float(np.sum(weights))
    square = float(np.sum(np.square(weights)))
    return total * total / square if square > 0 else 0.0


def source_distribution(
    local_x: np.ndarray,
    weights: np.ndarray,
) -> dict[str, object]:
    counts, _ = np.histogram(local_x, bins=EDGES, weights=weights)
    total = float(np.sum(counts))
    if total <= 0:
        proportions = np.full(len(CENTERS), np.nan)
        binned_mode = float("nan")
    else:
        proportions = counts / total
        binned_mode = float(CENTERS[int(np.argmax(counts))])
    return {
        "counts": counts,
        "proportions": proportions,
        "weight_total": total,
        "event_count": int(len(local_x)),
        "effective_sample_size": effective_sample_size(weights),
        "binned_mode": binned_mode,
        "kde_mode": weighted_kde_mode(local_x, weights),
    }


def run_one_split(
    c_events: np.ndarray,
    ac_events: np.ndarray,
    static: tuple[list[np.ndarray], np.ndarray, np.ndarray, np.ndarray],
    salt: int,
) -> tuple[dict[str, object], dict[str, dict[str, object]]] | None:
    base_templates, native_time, native_prompt, native_delayed = static
    c_mask = t400.event_split(c_events, "C", salt)
    ac_mask = t400.event_split(ac_events, "AC", salt)
    c_cal, c_hold = c_events[c_mask], c_events[~c_mask]
    ac_cal, ac_hold = ac_events[ac_mask], ac_events[~ac_mask]
    templates = list(base_templates)
    fit = t400.fit_calibration(t400.hist_time(c_cal), t400.hist_time(ac_cal), templates, t400.CAL_FRACTION)
    params = np.asarray(fit["params"], dtype=float)
    window = t400.child_window(native_time, native_prompt, native_delayed, float(params[3]), float(params[4]))
    if not bool(window.get("valid", False)):
        return None
    views = {
        "C": t400.event_membership(c_hold, params, templates, window, native_time, True),
        "AC": t400.event_membership(ac_hold, params, templates, window, native_time, False),
    }
    distributions: dict[str, dict[str, object]] = {}
    for source, view in views.items():
        distributions[source] = source_distribution(
            np.asarray(view["local_x"], dtype=float),
            np.asarray(view["weight"], dtype=float),
        )
    split = {
        "salt": salt,
        "fit_success": bool(fit["success"]),
        "left_time_us": float(window["left_time_us"]),
        "crest_time_us": float(window["mode_time_us"]),
        "right_time_us": float(window["right_time_us"]),
        "population_local_crest": float(window["local_mode_ara"]),
        "population_local_mean": float(window["local_weighted_mean"]),
    }
    return split, distributions


def clr(matrix: np.ndarray, epsilon: float = 1e-9) -> np.ndarray:
    logged = np.log(np.maximum(matrix, epsilon))
    return logged - np.mean(logged, axis=1, keepdims=True)


def safe_spearman(a: np.ndarray, b: np.ndarray) -> float:
    rho = float(spearmanr(a, b).statistic)
    return rho if math.isfinite(rho) else 0.0


def pairing_analysis(matrix: np.ndarray, source: str) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    transformed = clr(matrix)
    permutation_rows: list[dict[str, object]] = []
    scores: list[tuple[tuple[int, ...], float, list[float]]] = []
    for assignment in itertools.permutations(UPPER):
        correlations = [safe_spearman(transformed[:, low], transformed[:, high]) for low, high in zip(LOWER, assignment)]
        score = float(np.mean([-rho for rho in correlations]))
        scores.append((assignment, score, correlations))
    exact = next(item for item in scores if item[0] == REFLECTION)
    exact_rank = 1 + sum(score > exact[1] + 1e-12 for _, score, _ in scores)
    for assignment, score, correlations in sorted(scores, key=lambda item: item[1], reverse=True):
        rank = 1 + sum(other > score + 1e-12 for _, other, _ in scores)
        permutation_rows.append(
            {
                "source": source,
                "rank": rank,
                "mapping": " | ".join(f"{CENTERS[low]:.3f}->{CENTERS[high]:.3f}" for low, high in zip(LOWER, assignment)),
                "is_exact_reflection": assignment == REFLECTION,
                "exchange_score_mean_negative_rho": score,
                "pair_rhos": " | ".join(f"{rho:.9f}" for rho in correlations),
            }
        )
    pair_rows: list[dict[str, object]] = []
    for low, high, rho in zip(LOWER, REFLECTION, exact[2]):
        pair_rows.append(
            {
                "source": source,
                "lower_center": float(CENTERS[low]),
                "reflected_upper_center": float(CENTERS[high]),
                "spearman_rho_clr_across_splits": rho,
                "negative_exchange_contribution": -rho,
            }
        )
    summary = {
        "exchange_score": exact[1],
        "negative_pair_count": int(sum(rho < 0 for rho in exact[2])),
        "reflection_rank_of_24": int(exact_rank),
        "pair_rhos": [float(rho) for rho in exact[2]],
    }
    return pair_rows, permutation_rows, summary


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c_events = np.loadtxt(t400.DATA / "dataBeamOnC.txt")
    ac_events = np.loadtxt(t400.DATA / "dataBeamOnAC.txt")
    static = t400.build_templates()

    split_rows: list[dict[str, object]] = []
    invalid_split_rows: list[dict[str, object]] = []
    bin_rows: list[dict[str, object]] = []
    mode_rows: list[dict[str, object]] = []
    matrices: dict[str, list[np.ndarray]] = {"C": [], "AC": []}

    for salt in range(SEED_START, SEED_START + N_SPLITS):
        outcome = run_one_split(c_events, ac_events, static, salt)
        if outcome is None:
            invalid_split_rows.append(
                {
                    "salt": salt,
                    "valid": False,
                    "reason": "calibration-only window did not satisfy L < delayed crest < R",
                }
            )
            continue
        split, distributions = outcome
        split["valid"] = True
        split_rows.append(split)
        for source, distribution in distributions.items():
            proportions = np.asarray(distribution["proportions"], dtype=float)
            if not np.all(np.isfinite(proportions)):
                continue
            matrices[source].append(proportions)
            mode_rows.append(
                {
                    "salt": salt,
                    "source": source,
                    "event_count_in_window": int(distribution["event_count"]),
                    "effective_delayed_weight": float(distribution["weight_total"]),
                    "effective_sample_size": float(distribution["effective_sample_size"]),
                    "binned_mode_ara": float(distribution["binned_mode"]),
                    "kde_mode_ara": float(distribution["kde_mode"]),
                    "binned_mode_in_candidate_band": bool(GAP_LOW <= float(distribution["binned_mode"]) < GAP_HIGH),
                    "kde_mode_in_candidate_band": bool(GAP_LOW <= float(distribution["kde_mode"]) < GAP_HIGH),
                }
            )
            counts = np.asarray(distribution["counts"], dtype=float)
            winner = int(np.argmax(counts))
            for j, center in enumerate(CENTERS):
                bin_rows.append(
                    {
                        "salt": salt,
                        "source": source,
                        "bin_low": float(EDGES[j]),
                        "bin_high": float(EDGES[j + 1]),
                        "bin_center": float(center),
                        "effective_delayed_weight": float(counts[j]),
                        "proportion_of_split_weight": float(proportions[j]),
                        "is_binned_mode": j == winner,
                        "is_candidate_band": j == GAP_INDEX,
                    }
                )

    valid_split_count = len(split_rows)
    if valid_split_count == 0 or any(len(matrices[source]) != valid_split_count for source in matrices):
        raise RuntimeError(f"No aligned valid splits: {valid_split_count} / {[len(v) for v in matrices.values()]}")

    matrix_np = {source: np.vstack(rows) for source, rows in matrices.items()}
    bin_summary_rows: list[dict[str, object]] = []
    summaries: dict[str, dict[str, np.ndarray]] = {}
    for source, matrix in matrix_np.items():
        occupancy = np.mean(matrix, axis=0)
        volatility_sd = np.std(matrix, axis=0, ddof=1)
        volatility_cv = np.divide(volatility_sd, occupancy, out=np.zeros_like(volatility_sd), where=occupancy > 0)
        source_modes = [row for row in mode_rows if row["source"] == source]
        dominance = np.array([np.mean([math.isclose(float(row["binned_mode_ara"]), center) for row in source_modes]) for center in CENTERS])
        kde_dominance = np.array(
            [np.mean([(EDGES[j] <= float(row["kde_mode_ara"]) < EDGES[j + 1]) or (j == 7 and math.isclose(float(row["kde_mode_ara"]), 2.0)) for row in source_modes]) for j in range(8)]
        )
        summaries[source] = {
            "occupancy": occupancy,
            "sd": volatility_sd,
            "cv": volatility_cv,
            "dominance": dominance,
            "kde_dominance": kde_dominance,
        }
        for j, center in enumerate(CENTERS):
            bin_summary_rows.append(
                {
                    "source": source,
                    "bin_center": float(center),
                    "mean_occupancy": float(occupancy[j]),
                    "occupancy_sd": float(volatility_sd[j]),
                    "occupancy_cv": float(volatility_cv[j]),
                    "binned_mode_fraction": float(dominance[j]),
                    "kde_mode_fraction_in_bin": float(kde_dominance[j]),
                    "is_candidate_band": j == GAP_INDEX,
                }
            )

    pair_rows: list[dict[str, object]] = []
    permutation_rows: list[dict[str, object]] = []
    reflection: dict[str, dict[str, object]] = {}
    for source in ("C", "AC"):
        pairs, permutations, summary = pairing_analysis(matrix_np[source], source)
        pair_rows.extend(pairs)
        permutation_rows.extend(permutations)
        reflection[source] = summary

    c_modes = [row for row in mode_rows if row["source"] == "C"]
    c_occ = summaries["C"]["occupancy"]
    c_cv = summaries["C"]["cv"]
    occupancy_ratio = float(c_occ[GAP_INDEX] / np.mean(c_occ[[GAP_INDEX - 1, GAP_INDEX + 1]]))
    gap_dominance = float(summaries["C"]["dominance"][GAP_INDEX])
    kde_gap_fraction = float(np.mean([bool(row["kde_mode_in_candidate_band"]) for row in c_modes]))
    volatility_ratio = float(c_cv[GAP_INDEX] / np.median(c_cv))
    if volatility_ratio <= 0.80:
        volatility_class = "quiet"
    elif volatility_ratio >= 1.20:
        volatility_class = "turbulent"
    else:
        volatility_class = "intermediate"

    # Heuristic sampling-only mode null, frozen in the protocol.
    pooled = c_occ / np.sum(c_occ)
    median_neff = float(np.median([float(row["effective_sample_size"]) for row in c_modes]))
    null_n = max(2, int(round(median_neff)))
    rng = np.random.default_rng(401)
    simulated_counts = rng.multinomial(null_n, pooled, size=NULL_SINGLE_DRAWS)
    simulated_modes = np.argmax(simulated_counts, axis=1)
    single_mode_frequency = np.array([np.mean(simulated_modes == j) for j in range(8)])
    single_gap_probability = float(single_mode_frequency[GAP_INDEX])
    observed_gap_winners = int(round(gap_dominance * valid_split_count))
    observed_vs_null_two_sided_p = float(binomtest(observed_gap_winners, valid_split_count, single_gap_probability).pvalue)
    zero_gap_counts = rng.binomial(valid_split_count, single_gap_probability, size=NULL_EXPERIMENTS)
    p_zero_gap_winners = float(np.mean(zero_gap_counts == 0))
    exact_p_zero = float((1.0 - single_gap_probability) ** valid_split_count)
    null_rows = [
        {
            "bin_center": float(center),
            "pooled_probability": float(pooled[j]),
            "observed_binned_mode_fraction": float(summaries["C"]["dominance"][j]),
            "sampling_null_mode_fraction": float(single_mode_frequency[j]),
        }
        for j, center in enumerate(CENTERS)
    ]

    gates = {
        "G1_occupied_but_nondominant": bool(occupancy_ratio >= 0.50 and gap_dominance <= 0.01),
        "G2_continuous_missing_winner_persists": bool(kde_gap_fraction <= 0.05),
        "G3_beyond_sampling_argmax_null": bool(observed_gap_winners == 0 and p_zero_gap_winners < 0.05),
        "G4_reflected_exchange": bool(
            int(reflection["C"]["negative_pair_count"]) >= 3
            and float(reflection["C"]["exchange_score"]) >= 0.20
            and int(reflection["C"]["reflection_rank_of_24"]) <= 3
        ),
        "G5_C_exceeds_AC_control": bool(
            float(reflection["C"]["exchange_score"]) - float(reflection["AC"]["exchange_score"]) >= 0.10
            and int(reflection["C"]["reflection_rank_of_24"]) < int(reflection["AC"]["reflection_rank_of_24"])
        ),
    }
    if all(gates.values()):
        verdict = "INDIRECT CHILD ANTI-PHASE SHADOW SUPPORTED"
    elif gates["G1_occupied_but_nondominant"] and gates["G2_continuous_missing_winner_persists"] and gates["G3_beyond_sampling_argmax_null"]:
        verdict = "STRUCTURED WINNER SHADOW; ANTI-PHASE NOT IDENTIFIED"
    elif gates["G1_occupied_but_nondominant"] and gates["G2_continuous_missing_winner_persists"]:
        verdict = "OCCUPIED BAND; WINNER SELECTION EXPLAINS THE GAP"
    else:
        verdict = "NO STABLE MISSING-WINNER BAND"

    results = {
        "test": "T401",
        "date": "2026-08-17",
        "verdict": verdict,
        "protocol_sha256": sha256(PROTOCOL),
        "source": {
            "identity": "COHERENT 2022 CsI delayed-child event distribution, with beam-coincident C and anti-coincident AC evaluated separately",
            "beam_C_sha256": sha256(t400.DATA / "dataBeamOnC.txt"),
            "beam_AC_sha256": sha256(t400.DATA / "dataBeamOnAC.txt"),
        },
        "coordinate": "T400 local child ARA 0-2 between calibration-only branch equality L and delayed-rate return R",
        "splits": {
            "requested": N_SPLITS,
            "valid": valid_split_count,
            "invalid": len(invalid_split_rows),
            "valid_fraction": valid_split_count / N_SPLITS,
            "salts": [SEED_START, SEED_START + N_SPLITS - 1],
            "execution_note": "The frozen protocol requested 200 splits. Thirty-six calibration partitions did not form an ordered child window; distribution gates and the sampling null use the 164 valid transfers only.",
        },
        "candidate_band": {
            "range": [GAP_LOW, GAP_HIGH],
            "center": float(CENTERS[GAP_INDEX]),
            "mean_occupancy_C": float(c_occ[GAP_INDEX]),
            "mean_occupancy_AC": float(summaries["AC"]["occupancy"][GAP_INDEX]),
            "occupancy_ratio_to_C_neighbours": occupancy_ratio,
            "binned_mode_fraction_C": gap_dominance,
            "kde_mode_fraction_C": kde_gap_fraction,
            "volatility_ratio_to_C_median": volatility_ratio,
            "volatility_class": volatility_class,
        },
        "sampling_null": {
            "pooled_effective_sample_size_rounded": null_n,
            "single_split_candidate_mode_probability": single_gap_probability,
            "observed_candidate_winners": observed_gap_winners,
            "observed_vs_null_two_sided_binomial_p": observed_vs_null_two_sided_p,
            "experiments": NULL_EXPERIMENTS,
            "valid_split_count_used": valid_split_count,
            "simulated_probability_zero_candidate_winners": p_zero_gap_winners,
            "exact_probability_zero_candidate_winners": exact_p_zero,
        },
        "reflection": reflection,
        "C_minus_AC_exchange_score": float(reflection["C"]["exchange_score"]) - float(reflection["AC"]["exchange_score"]),
        "gates": gates,
        "boundaries": [
            "The candidate band was selected after inspecting T400 and is a registered follow-up, not an independent discovery interval.",
            "Thirty-six of 200 calibration partitions did not form an ordered child window; all distribution calculations use the 164 valid transfers.",
            "Overlapping deterministic splits test resampling stability and are not independent physical experiments.",
            "CLR mirrored-pair correlations remove the trivial lower-half/upper-half sum constraint but do not establish causality.",
            "The sampling-only null approximates weighted events by a multinomial effective sample size.",
            "A statistical shadow cannot by itself label an individual event as a neutrino or hidden physical wave.",
        ],
    }

    write_csv(OUT / "T401_SPLITS.csv", split_rows)
    write_csv(OUT / "T401_INVALID_SPLITS.csv", invalid_split_rows)
    write_csv(OUT / "T401_SPLIT_BIN_DISTRIBUTIONS.csv", bin_rows)
    write_csv(OUT / "T401_SPLIT_MODES.csv", mode_rows)
    write_csv(OUT / "T401_BIN_SUMMARY.csv", bin_summary_rows)
    write_csv(OUT / "T401_MIRROR_RELATIONS.csv", pair_rows)
    write_csv(OUT / "T401_ALL_PAIRING_SCORES.csv", permutation_rows)
    write_csv(OUT / "T401_SAMPLING_NULL.csv", null_rows)
    (OUT / "T401_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    # Six small multiples keep occupancy, winner selection, volatility and
    # reflected exchange visually separate.  All panels use explicit ARA axes.
    blue = "#3267a8"
    gold = "#d7a128"
    ink = "#172033"
    grey = "#aeb7c2"
    width = 0.10
    fig, axes = plt.subplots(3, 2, figsize=(16, 15), constrained_layout=True)

    ax = axes[0, 0]
    ax.bar(CENTERS - width / 2, summaries["C"]["occupancy"], width=width, color=blue, edgecolor=ink, label="C signal-side")
    ax.bar(CENTERS + width / 2, summaries["AC"]["occupancy"], width=width, facecolor="white", edgecolor=gold, hatch="//", label="AC control")
    ax.axvspan(GAP_LOW, GAP_HIGH, color=grey, alpha=0.20, label="candidate 1.25–1.50")
    ax.axvline(1.0, color=ink, ls="--", lw=1.4)
    ax.set(xlim=(0, 2), xlabel="local child ARA", ylabel="mean share of split weight", title=f"Full-distribution occupancy across {valid_split_count} valid splits")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[0, 1]
    ax.bar(CENTERS - width / 2, summaries["C"]["dominance"], width=width, color=blue, edgecolor=ink, label="C binned winner")
    ax.bar(CENTERS + width / 2, summaries["AC"]["dominance"], width=width, facecolor="white", edgecolor=gold, hatch="//", label="AC binned winner")
    ax.axvspan(GAP_LOW, GAP_HIGH, color=grey, alpha=0.20)
    ax.axvline(1.0, color=ink, ls="--", lw=1.4)
    ax.set(xlim=(0, 2), xlabel="winning local child ARA bin", ylabel="fraction of splits", title="Dominance after argmax projection")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[1, 0]
    relative_cv = summaries["C"]["cv"] / np.median(summaries["C"]["cv"])
    ax.bar(CENTERS, relative_cv, width=0.20, color=gold, edgecolor=ink)
    ax.axhline(0.80, color=ink, ls=":", lw=1.2, label="quiet threshold 0.80")
    ax.axhline(1.20, color=ink, ls="--", lw=1.2, label="turbulent threshold 1.20")
    ax.axvspan(GAP_LOW, GAP_HIGH, color=grey, alpha=0.20)
    ax.set(xlim=(0, 2), xlabel="local child ARA bin", ylabel="CV / median CV", title="C occupancy volatility")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[1, 1]
    ax.bar(CENTERS - width / 2, summaries["C"]["dominance"], width=width, color=blue, edgecolor=ink, label="8-bin mode")
    ax.bar(CENTERS + width / 2, summaries["C"]["kde_dominance"], width=width, facecolor="white", edgecolor=gold, hatch="//", label="KDE mode, h=0.15")
    ax.axvspan(GAP_LOW, GAP_HIGH, color=grey, alpha=0.20)
    ax.axvline(1.0, color=ink, ls="--", lw=1.4)
    ax.set(xlim=(0, 2), xlabel="local child ARA mode region", ylabel="fraction of C splits", title="Fixed-bin and continuous mode locations")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[2, 0]
    c_pair = [row for row in pair_rows if row["source"] == "C"]
    ac_pair = [row for row in pair_rows if row["source"] == "AC"]
    positions = np.arange(4)
    labels = [f"{row['lower_center']:.3f}↔{row['reflected_upper_center']:.3f}" for row in c_pair]
    ax.bar(positions - 0.18, [row["spearman_rho_clr_across_splits"] for row in c_pair], width=0.36, color=blue, edgecolor=ink, label="C")
    ax.bar(positions + 0.18, [row["spearman_rho_clr_across_splits"] for row in ac_pair], width=0.36, facecolor="white", edgecolor=gold, hatch="//", label="AC")
    ax.axhline(0.0, color=ink, lw=1.2)
    ax.set(xticks=positions, xticklabels=labels, xlabel="predeclared reflected ARA pair", ylabel="Spearman ρ after CLR", title="Reflected-pair exchange across splits")
    ax.legend(frameon=False, fontsize=9)

    ax = axes[2, 1]
    ax.bar(CENTERS - width / 2, summaries["C"]["dominance"], width=width, color=blue, edgecolor=ink, label="observed")
    ax.bar(CENTERS + width / 2, single_mode_frequency, width=width, facecolor="white", edgecolor=gold, hatch="//", label=f"sampling null, N_eff={null_n}")
    ax.axvspan(GAP_LOW, GAP_HIGH, color=grey, alpha=0.20)
    ax.set(xlim=(0, 2), xlabel="local child ARA winning bin", ylabel="fraction of split winners", title="Observed winner pattern versus sampling-only null")
    ax.legend(frameon=False, fontsize=9)

    fig.suptitle(f"T401 — Winner projection and candidate child anti-phase\n{verdict}", fontsize=18, fontweight="bold")
    fig.savefig(OUT / "T401_WINNER_PROJECTION_CHILD_ANTIPHASE.png", dpi=180)
    plt.close(fig)

    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
