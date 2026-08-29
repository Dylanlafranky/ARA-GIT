"""T452: generation-built lifespan Phase A versus clock-built time Phase B.

The script is intentionally self-contained and deterministic.  It parses the
published S1 workbook, preserves raw units, creates the frozen ARA views, runs
the interval-order controls, and writes audit tables plus static visual QA.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".mplconfig"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T452_yeast_lifespan_time_phase")
SOURCE = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T451_birth_to_death_source_inventory\source\yeast\supplementary\pone.0167394.s005.xlsx")
RESULTS = ROOT / "results"
RESULTS.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(452)
GRID = np.round(np.linspace(0.0, 2.0, 41), 8)
RATE_GRID = np.round(np.linspace(0.05, 1.95, 39), 8)
N_SHUFFLES = 2000

COLORS = {
    "development": "#315ea8",
    "holdout": "#d27a20",
    "external": "#6b8e23",
    "pure": "#30343b",
    "q": "#a46ad7",
    "size": "#c06374",
    "fluorescence": "#6a5acd",
    "total": "#2f8f8b",
}


def finite(values):
    return pd.to_numeric(pd.Series(values), errors="coerce").to_numpy(float)


def ara_ratio(ratio):
    ratio = np.asarray(ratio, dtype=float)
    return 2.0 * ratio / (1.0 + ratio)


def cohort_for(experiment):
    n = int(str(experiment).split("_")[-1])
    if n in (7, 8):
        return "development"
    if n == 9:
        return "holdout"
    return "external"


def parse_pair(size_sheet, time_sheet, fluorescence_sheet=None, dataset_label=""):
    size = pd.read_excel(SOURCE, sheet_name=size_sheet, header=None)
    timing = pd.read_excel(SOURCE, sheet_name=time_sheet, header=None)
    fluor = pd.read_excel(SOURCE, sheet_name=fluorescence_sheet, header=None) if fluorescence_sheet else None

    generation_rows = []
    interval_rows = []
    cell_rows = []

    for col in range(1, size.shape[1]):
        experiment = str(size.iat[0, col])
        cell_id = str(size.iat[1, col])
        s = finite(size.iloc[2:, col])
        t = finite(timing.iloc[2:, col])
        f = finite(fluor.iloc[2:, col]) if fluor is not None else np.full_like(s, np.nan)
        mask = np.isfinite(s) & np.isfinite(t)
        s, t, f = s[mask], t[mask], f[mask]
        if len(s) < 3 or not np.isfinite(t[-1]) or t[-1] <= t[0]:
            continue
        t = t - t[0]
        if np.any(np.diff(t) <= 0):
            continue

        n = len(t)
        a = 2.0 * np.arange(n) / (n - 1)
        b_elapsed = 2.0 * t / t[-1]
        b_remaining = 2.0 - b_elapsed
        shadow = b_elapsed - a
        size_fold = s / s[0]
        fluor_fold = f / f[0] if np.isfinite(f[0]) and f[0] != 0 else np.full(n, np.nan)
        total = s * f
        total_fold = total / total[0] if np.isfinite(total[0]) and total[0] != 0 else np.full(n, np.nan)
        cohort = cohort_for(experiment)

        intervals = np.diff(t)
        mean_interval = float(np.mean(intervals))
        rate = intervals / mean_interval
        a_mid = (a[:-1] + a[1:]) / 2.0
        thirds = np.where(a_mid < 2 / 3, "early", np.where(a_mid < 4 / 3, "middle", "late"))
        log_size_change = np.log(s[1:] / s[:-1])
        log_fluor_change = np.log(f[1:] / f[:-1]) if np.all(f > 0) else np.full(n - 1, np.nan)
        log_total_change = np.log(total[1:] / total[:-1]) if np.all(total > 0) else np.full(n - 1, np.nan)

        for i in range(n):
            generation_rows.append(
                {
                    "dataset": dataset_label,
                    "cohort": cohort,
                    "experiment": experiment,
                    "cell_id": cell_id,
                    "generation_observation": i + 1,
                    "observed_g1_count": n,
                    "hours_elapsed": t[i],
                    "lifespan_hours_observed": t[-1],
                    "maturity_A": a[i],
                    "time_elapsed_B": b_elapsed[i],
                    "time_remaining_B": b_remaining[i],
                    "time_shadow": shadow[i],
                    "te_ara_sum": a[i] + b_remaining[i],
                    "size_um2": s[i],
                    "size_fold": size_fold[i],
                    "size_ara": ara_ratio(size_fold[i]),
                    "rpl13a_concentration": f[i],
                    "rpl13a_concentration_fold": fluor_fold[i],
                    "rpl13a_concentration_ara": ara_ratio(fluor_fold[i]) if np.isfinite(fluor_fold[i]) else np.nan,
                    "rpl13a_total": total[i],
                    "rpl13a_total_fold": total_fold[i],
                    "rpl13a_total_ara": ara_ratio(total_fold[i]) if np.isfinite(total_fold[i]) else np.nan,
                }
            )

        for i in range(n - 1):
            interval_rows.append(
                {
                    "dataset": dataset_label,
                    "cohort": cohort,
                    "experiment": experiment,
                    "cell_id": cell_id,
                    "interval_index": i + 1,
                    "intervals_observed": n - 1,
                    "maturity_mid_A": a_mid[i],
                    "life_third": thirds[i],
                    "division_interval_hours": intervals[i],
                    "local_time_rate": rate[i],
                    "local_time_ara": ara_ratio(rate[i]),
                    "log_size_change": log_size_change[i],
                    "log_rpl13a_concentration_change": log_fluor_change[i],
                    "log_rpl13a_total_change": log_total_change[i],
                }
            )

        early = rate[thirds == "early"]
        late = rate[thirds == "late"]
        cell_rows.append(
            {
                "dataset": dataset_label,
                "cohort": cohort,
                "experiment": experiment,
                "cell_id": cell_id,
                "observed_g1_count": n,
                "observed_division_intervals": n - 1,
                "lifespan_hours_observed": t[-1],
                "mean_division_interval_hours": mean_interval,
                "start_size_um2": s[0],
                "end_size_um2": s[-1],
                "size_fold_end": size_fold[-1],
                "start_rpl13a_concentration": f[0],
                "end_rpl13a_concentration": f[-1],
                "rpl13a_concentration_fold_end": fluor_fold[-1],
                "rpl13a_total_fold_end": total_fold[-1],
                "shadow_min": float(np.min(shadow)),
                "shadow_min_A": float(a[np.argmin(shadow)]),
                "shadow_max": float(np.max(shadow)),
                "shadow_max_A": float(a[np.argmax(shadow)]),
                "late_minus_early_rate": float(np.mean(late) - np.mean(early)),
            }
        )

    return pd.DataFrame(generation_rows), pd.DataFrame(interval_rows), pd.DataFrame(cell_rows)


def interpolate_cells(frame, x, columns, grid):
    rows = []
    for (cohort, cell_id), group in frame.groupby(["cohort", "cell_id"], sort=True):
        group = group.sort_values(x)
        xp = group[x].to_numpy(float)
        for column in columns:
            yp = group[column].to_numpy(float)
            valid = np.isfinite(xp) & np.isfinite(yp)
            if valid.sum() < 2:
                continue
            values = np.interp(grid, xp[valid], yp[valid], left=np.nan, right=np.nan)
            for gx, value in zip(grid, values):
                rows.append({"cohort": cohort, "cell_id": cell_id, "grid_A": gx, "metric": column, "value": value})
    return pd.DataFrame(rows)


def summarise_interpolated(long_frame):
    return (
        long_frame.groupby(["cohort", "grid_A", "metric"], observed=True)["value"]
        .agg(median="median", q25=lambda x: x.quantile(0.25), q75=lambda x: x.quantile(0.75), n="count")
        .reset_index()
    )


def safe_corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    valid = np.isfinite(a) & np.isfinite(b)
    if valid.sum() < 3 or np.std(a[valid]) == 0 or np.std(b[valid]) == 0:
        return float("nan")
    return float(np.corrcoef(a[valid], b[valid])[0, 1])


def curve_pair_metrics(summary, metric, reference="development"):
    subset = summary[(summary.metric == metric) & summary.grid_A.between(0.10, 1.90)].copy()
    wide = subset.pivot(index="grid_A", columns="cohort", values="median")
    rows = []
    for cohort in ["holdout", "external"]:
        a = wide[reference].to_numpy(float)
        b = wide[cohort].to_numpy(float)
        rows.append(
            {
                "metric": metric,
                "comparison": f"{reference}_vs_{cohort}",
                "correlation": safe_corr(a, b),
                "rmse": float(np.sqrt(np.nanmean((a - b) ** 2))),
                "mae": float(np.nanmean(np.abs(a - b))),
                "sign_agreement": float(np.nanmean(np.sign(a) == np.sign(b))),
                "grid_points": int(np.isfinite(a + b).sum()),
            }
        )
    return rows


def median_curve(summary, metric, cohort, grid):
    subset = summary[(summary.metric == metric) & (summary.cohort == cohort)].set_index("grid_A")
    return subset.reindex(grid)["median"].to_numpy(float)


def first_up_crossing(grid, values, lower=0.5):
    grid, values = np.asarray(grid, float), np.asarray(values, float)
    for i in range(1, len(grid)):
        if grid[i] < lower or not np.isfinite(values[i - 1 : i + 1]).all():
            continue
        if values[i - 1] < 1 <= values[i]:
            denom = values[i] - values[i - 1]
            return float(grid[i - 1] + (1 - values[i - 1]) * (grid[i] - grid[i - 1]) / denom) if denom else float(grid[i])
    return float("nan")


def shuffle_test(intervals, cohort):
    groups = []
    for _, group in intervals[intervals.cohort == cohort].groupby("cell_id", sort=True):
        groups.append((group.local_time_rate.to_numpy(float), group.maturity_mid_A.to_numpy(float)))

    def statistic(rate_arrays):
        values = []
        for rates, mids in rate_arrays:
            early = rates[mids < 2 / 3]
            late = rates[mids >= 4 / 3]
            values.append(float(np.mean(late) - np.mean(early)))
        return float(np.median(values))

    observed = statistic(groups)
    null = np.empty(N_SHUFFLES)
    for j in range(N_SHUFFLES):
        shuffled = [(RNG.permutation(rates), mids) for rates, mids in groups]
        null[j] = statistic(shuffled)
    p_upper = float((1 + np.sum(null >= observed)) / (N_SHUFFLES + 1))
    return {
        "cohort": cohort,
        "cells": len(groups),
        "observed_median_late_minus_early": observed,
        "null_median": float(np.median(null)),
        "null_q025": float(np.quantile(null, 0.025)),
        "null_q95": float(np.quantile(null, 0.95)),
        "null_q975": float(np.quantile(null, 0.975)),
        "empirical_p_upper": p_upper,
        "shuffles": N_SHUFFLES,
        "null_values": null,
    }


def bootstrap_ci(values, n=2000):
    values = np.asarray(values, float)
    values = values[np.isfinite(values)]
    medians = np.empty(n)
    for i in range(n):
        medians[i] = np.median(RNG.choice(values, size=len(values), replace=True))
    return float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))


def curve_to_wide(summary, metrics):
    return summary[summary.metric.isin(metrics)].copy()


def add_curve(ax, summary, metric, cohorts=("development", "holdout", "external"), label_suffix=""):
    for cohort in cohorts:
        d = summary[(summary.metric == metric) & (summary.cohort == cohort)].sort_values("grid_A")
        if d.empty:
            continue
        ax.fill_between(d.grid_A, d.q25, d.q75, color=COLORS[cohort], alpha=0.10)
        ax.plot(d.grid_A, d["median"], color=COLORS[cohort], lw=2.1, label=f"{cohort}{label_suffix}")


def style(ax, xlabel, ylabel, title):
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(alpha=0.20)
    ax.spines[["top", "right"]].set_visible(False)


def save_fig(fig, name):
    fig.tight_layout(rect=(0, 0, 1, 0.965))
    fig.savefig(RESULTS / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def make_figures(generations, intervals, cells, gen_summary, rate_summary, shuffle_results, metrics, landmarks):
    plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "figure.facecolor": "white"})

    # 1. Scope and raw units.
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    counts = cells.groupby("cohort").size().reindex(["development", "holdout", "external"])
    axes[0, 0].bar(counts.index, counts.values, color=[COLORS[x] for x in counts.index])
    for i, v in enumerate(counts.values):
        axes[0, 0].text(i, v + 2, str(v), ha="center")
    style(axes[0, 0], "Frozen cohort", "Individual mother cells", "Cell count and frozen role")
    for cohort, d in cells.groupby("cohort"):
        axes[0, 1].scatter(d.observed_g1_count, d.lifespan_hours_observed, s=28, alpha=0.70, color=COLORS[cohort], label=cohort)
    style(axes[0, 1], "Observed G1 measurements per cell", "First-to-last observed G1 span (hours)", "Raw lifespan: generations and clock hours")
    axes[0, 1].legend(frameon=False)
    bins = np.arange(0, math.ceil(cells.lifespan_hours_observed.max() / 5) * 5 + 5, 5)
    for cohort, d in cells.groupby("cohort"):
        axes[1, 0].hist(d.lifespan_hours_observed, bins=bins, histtype="step", lw=2, color=COLORS[cohort], label=cohort)
    style(axes[1, 0], "First-to-last observed G1 span (hours)", "Cells per bin", "Observed lifespan distribution")
    axes[1, 0].legend(frameon=False)
    for cohort, d in cells.groupby("cohort"):
        axes[1, 1].scatter(d.observed_g1_count, d.mean_division_interval_hours, s=28, alpha=0.70, color=COLORS[cohort], label=cohort)
    style(axes[1, 1], "Observed G1 measurements per cell", "Mean division interval (hours)", "Long life can mean more divisions, faster divisions, or both")
    fig.suptitle("T452 — raw yeast lifespan measurements before ARA normalization", fontsize=18)
    save_fig(fig, "T452_01_SCOPE_AND_RAW_LIFESPANS.png")

    # 2. The two equivalent orientations.
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    sample_parts = []
    for cohort, cohort_frame in generations.groupby("cohort"):
        keep = sorted(cohort_frame.cell_id.unique())[:25]
        sample_parts.append(cohort_frame[cohort_frame.cell_id.isin(keep)])
    sample = pd.concat(sample_parts, ignore_index=True)
    for cohort, d in sample.groupby("cohort"):
        for _, cell in d.groupby("cell_id"):
            axes[0, 0].plot(cell.maturity_A, cell.time_elapsed_B, color=COLORS[cohort], alpha=0.15, lw=0.9)
    axes[0, 0].plot([0, 2], [0, 2], ls="--", color=COLORS["pure"], lw=2, label="pure equal progress")
    style(axes[0, 0], "Reproductive maturity Phase A (0–2)", "Elapsed clock Phase B, display orientation (0–2)", "Individual elapsed-time paths")
    axes[0, 0].legend(frameon=False)
    add_curve(axes[0, 1], gen_summary, "time_elapsed_B")
    axes[0, 1].plot([0, 2], [0, 2], ls="--", color=COLORS["pure"], lw=2, label="pure equal progress")
    style(axes[0, 1], "Reproductive maturity Phase A (0–2)", "Elapsed clock Phase B (0–2)", "Population median paths with interquartile bands")
    axes[0, 1].legend(frameon=False)
    add_curve(axes[1, 0], gen_summary, "te_ara_sum")
    axes[1, 0].axhline(2, ls="--", color=COLORS["pure"], lw=2, label="pure TE-ARA total 2")
    style(axes[1, 0], "Reproductive maturity Phase A (0–2)", "A maturity + B remaining-time", "Counter-traversing same-slice TE-ARA view")
    axes[1, 0].legend(frameon=False)
    add_curve(axes[1, 1], gen_summary, "time_shadow")
    axes[1, 1].axhline(0, ls="--", color=COLORS["pure"], lw=2)
    style(axes[1, 1], "Reproductive maturity Phase A (0–2)", "Signed time shadow B_elapsed − A", "Interior departure from pure equal progress")
    axes[1, 1].legend(frameon=False)
    fig.suptitle("T452 — the same lifespan/time geometry in elapsed and counter-phase views", fontsize=18)
    save_fig(fig, "T452_02_PHASE_GEOMETRY.png")

    # 3. Local time child and shuffled controls.
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    add_curve(axes[0, 0], rate_summary, "local_time_rate")
    axes[0, 0].axhline(1, ls="--", color=COLORS["pure"], lw=2, label="equal-rate ridge")
    for cohort, x in landmarks.items():
        if np.isfinite(x):
            axes[0, 0].axvline(x, color=COLORS[cohort], ls=":", alpha=0.85)
    style(axes[0, 0], "Interval midpoint maturity A (0–2)", "Division interval ÷ cell mean", "Local clock participation across reproductive life")
    axes[0, 0].legend(frameon=False, ncol=2)
    add_curve(axes[0, 1], rate_summary, "local_time_ara")
    axes[0, 1].axhline(1, ls="--", color=COLORS["pure"], lw=2)
    style(axes[0, 1], "Interval midpoint maturity A (0–2)", "Local time child ARA 2r/(1+r)", "The same rate on a bounded 0–2 ARA display")
    axes[0, 1].legend(frameon=False)
    for idx, cohort in enumerate(["holdout", "external"]):
        result = shuffle_results[cohort]
        ax = axes[1, idx]
        ax.hist(result["null_values"], bins=35, color="#c9ced6", edgecolor="#ffffff", label="2,000 within-cell order shuffles")
        ax.axvline(result["observed_median_late_minus_early"], color=COLORS[cohort], lw=3, label=f"observed = {result['observed_median_late_minus_early']:.3f}")
        ax.axvline(result["null_q95"], color=COLORS["pure"], ls="--", lw=2, label=f"shuffle 95% = {result['null_q95']:.3f}")
        style(ax, "Median late-minus-early normalized interval rate", "Shuffle count", f"{cohort}: does age-order survive interval shuffling?")
        ax.legend(frameon=False, fontsize=9)
    fig.suptitle("T452 — local time child, ridge crossing, and order-destroying controls", fontsize=18)
    save_fig(fig, "T452_03_TIME_CHILD_AND_NULL.png")

    # 4. Independent biological witnesses.
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    add_curve(axes[0, 0], gen_summary, "size_fold")
    axes[0, 0].axhline(1, color=COLORS["pure"], ls="--")
    style(axes[0, 0], "Reproductive maturity Phase A (0–2)", "Cell area ÷ starting area", "Independent witness: cell-size growth")
    axes[0, 0].legend(frameon=False)
    add_curve(axes[0, 1], gen_summary, "rpl13a_concentration_fold", cohorts=("development", "holdout"))
    axes[0, 1].axhline(1, color=COLORS["pure"], ls="--")
    style(axes[0, 1], "Reproductive maturity Phase A (0–2)", "Rpl13A-GFP concentration ÷ starting value", "Independent witness: ribosome concentration")
    axes[0, 1].legend(frameon=False)
    add_curve(axes[1, 0], gen_summary, "rpl13a_total_fold", cohorts=("development", "holdout"))
    axes[1, 0].axhline(1, color=COLORS["pure"], ls="--")
    style(axes[1, 0], "Reproductive maturity Phase A (0–2)", "Area × concentration, fold from start", "Derived witness: total Rpl13A-GFP abundance")
    axes[1, 0].legend(frameon=False)
    rate_dev = rate_summary[(rate_summary.cohort == "development") & (rate_summary.metric == "local_time_rate")]
    size_dev = rate_summary[(rate_summary.cohort == "development") & (rate_summary.metric == "log_size_change")]
    fluor_dev = rate_summary[(rate_summary.cohort == "development") & (rate_summary.metric == "log_rpl13a_concentration_change")]
    axes[1, 1].plot(rate_dev.grid_A, rate_dev["median"], color=COLORS["development"], lw=2.5, label="local time rate (ridge=1)")
    if not size_dev.empty:
        z = (size_dev["median"] - size_dev["median"].median()) / (size_dev["median"].std() or 1)
        axes[1, 1].plot(size_dev.grid_A, 1 + 0.25 * z, color=COLORS["size"], lw=2, label="size-change shape (centred)")
    if not fluor_dev.empty:
        z = (fluor_dev["median"] - fluor_dev["median"].median()) / (fluor_dev["median"].std() or 1)
        axes[1, 1].plot(fluor_dev.grid_A, 1 + 0.25 * z, color=COLORS["fluorescence"], lw=2, label="Rpl13A-change shape (centred)")
    axes[1, 1].axhline(1, color=COLORS["pure"], ls="--")
    style(axes[1, 1], "Interval midpoint maturity A (0–2)", "Shape-only aligned display", "Do the lower witnesses turn with the local time child?")
    axes[1, 1].legend(frameon=False)
    fig.suptitle("T452 — biological children are witnesses, not substitutes for the time phase", fontsize=18)
    save_fig(fig, "T452_04_WITNESS_CHILDREN.png")

    # 5. Deterministic holdout individuals: shortest, median, longest by G1 count.
    hold = cells[cells.cohort == "holdout"].sort_values(["observed_g1_count", "cell_id"])
    selected = [hold.iloc[0].cell_id, hold.iloc[len(hold) // 2].cell_id, hold.iloc[-1].cell_id]
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    for row, cell_id in enumerate(selected):
        g = generations[(generations.cohort == "holdout") & (generations.cell_id == cell_id)].sort_values("maturity_A")
        it = intervals[(intervals.cohort == "holdout") & (intervals.cell_id == cell_id)].sort_values("maturity_mid_A")
        axes[row, 0].plot(g.maturity_A, g.time_elapsed_B, marker="o", color=COLORS["holdout"])
        axes[row, 0].plot([0, 2], [0, 2], ls="--", color=COLORS["pure"])
        style(axes[row, 0], "Maturity A", "Elapsed time B", f"{cell_id}: phase path")
        axes[row, 1].plot(g.maturity_A, g.time_shadow, marker="o", color=COLORS["q"])
        axes[row, 1].axhline(0, ls="--", color=COLORS["pure"])
        style(axes[row, 1], "Maturity A", "Time shadow B−A", f"{g.observed_g1_count.iloc[0]} G1 observations; {g.lifespan_hours_observed.iloc[0]:.1f} h")
        axes[row, 2].plot(it.maturity_mid_A, it.local_time_rate, marker="o", color=COLORS["development"], label="local time rate")
        axes[row, 2].plot(g.maturity_A, g.size_fold, marker="s", color=COLORS["size"], label="size fold")
        if g.rpl13a_concentration_fold.notna().any():
            axes[row, 2].plot(g.maturity_A, g.rpl13a_concentration_fold, marker="^", color=COLORS["fluorescence"], label="Rpl13A concentration fold")
        axes[row, 2].axhline(1, ls="--", color=COLORS["pure"])
        style(axes[row, 2], "Maturity A", "Within-cell ratio (start or mean = 1)", "Lower children in raw relational units")
        axes[row, 2].legend(frameon=False, fontsize=8)
    fig.suptitle("T452 — untouched experiment 9 individuals: short, median, and long reproductive spans", fontsize=18)
    save_fig(fig, "T452_05_INDIVIDUAL_HOLDOUT_CELLS.png")

    # 6. One overview for quick orientation.
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    for cohort, d in cells.groupby("cohort"):
        axes[0, 0].scatter(d.observed_g1_count, d.lifespan_hours_observed, s=22, alpha=0.65, color=COLORS[cohort], label=cohort)
    style(axes[0, 0], "Observed G1 count", "Observed hours", "Raw lifespan")
    axes[0, 0].legend(frameon=False, fontsize=8)
    add_curve(axes[0, 1], gen_summary, "time_shadow")
    axes[0, 1].axhline(0, ls="--", color=COLORS["pure"])
    style(axes[0, 1], "Maturity A", "B_elapsed − A", "Time-wave shadow")
    add_curve(axes[0, 2], rate_summary, "local_time_rate")
    axes[0, 2].axhline(1, ls="--", color=COLORS["pure"])
    style(axes[0, 2], "Maturity midpoint A", "Interval ÷ cell mean", "Local time child")
    add_curve(axes[1, 0], gen_summary, "size_fold")
    axes[1, 0].axhline(1, ls="--", color=COLORS["pure"])
    style(axes[1, 0], "Maturity A", "Area fold", "Size witness")
    add_curve(axes[1, 1], gen_summary, "rpl13a_concentration_fold", cohorts=("development", "holdout"))
    axes[1, 1].axhline(1, ls="--", color=COLORS["pure"])
    style(axes[1, 1], "Maturity A", "Concentration fold", "Rpl13A witness")
    gate_names = list(metrics["gates"].keys())
    gate_values = [int(metrics["gates"][x]) for x in gate_names]
    axes[1, 2].barh(range(len(gate_names)), gate_values, color=["#315ea8" if x else "#c9ced6" for x in gate_values])
    axes[1, 2].set_yticks(range(len(gate_names)), [x.replace("_", " ") for x in gate_names], fontsize=8)
    axes[1, 2].set_xlim(0, 1.1)
    axes[1, 2].set_xticks([0, 1], ["fail", "pass"])
    style(axes[1, 2], "Frozen result", "", "Frozen gates (secondary to geometry)")
    fig.suptitle("T452 — yeast reproductive lifespan and the inferred clock-time phase", fontsize=20)
    save_fig(fig, "T452_OVERVIEW.png")


def main():
    g2, i2, c2 = parse_pair("Table c", "Table d", "Table e", "Rpl13A cohort")
    g1, i1, c1 = parse_pair(" Table a", "Table b", None, "mixed-GFP cohort")
    generations = pd.concat([g2, g1], ignore_index=True)
    intervals = pd.concat([i2, i1], ignore_index=True)
    cells = pd.concat([c2, c1], ignore_index=True)

    gen_metrics = [
        "time_elapsed_B",
        "time_remaining_B",
        "time_shadow",
        "te_ara_sum",
        "size_fold",
        "size_ara",
        "rpl13a_concentration_fold",
        "rpl13a_concentration_ara",
        "rpl13a_total_fold",
        "rpl13a_total_ara",
    ]
    rate_metrics = ["local_time_rate", "local_time_ara", "log_size_change", "log_rpl13a_concentration_change", "log_rpl13a_total_change"]
    gen_long = interpolate_cells(generations, "maturity_A", gen_metrics, GRID)
    rate_long = interpolate_cells(intervals, "maturity_mid_A", rate_metrics, RATE_GRID)
    gen_summary = summarise_interpolated(gen_long)
    rate_summary = summarise_interpolated(rate_long)

    transfer = pd.DataFrame(curve_pair_metrics(gen_summary, "time_shadow") + curve_pair_metrics(rate_summary, "local_time_rate"))

    landmarks = {}
    landmark_rows = []
    for cohort in ["development", "holdout", "external"]:
        rate_curve = median_curve(rate_summary, "local_time_rate", cohort, RATE_GRID)
        crossing = first_up_crossing(RATE_GRID, rate_curve, lower=0.5)
        shadow_curve = median_curve(gen_summary, "time_shadow", cohort, GRID)
        interior = (GRID >= 0.10) & (GRID <= 1.90)
        min_a = float(GRID[interior][np.nanargmin(shadow_curve[interior])])
        landmarks[cohort] = crossing
        landmark_rows.append(
            {
                "cohort": cohort,
                "local_rate_upcrossing_A": crossing,
                "time_shadow_minimum_A": min_a,
                "time_shadow_minimum": float(np.nanmin(shadow_curve[interior])),
                "crossing_minus_shadow_minimum_A": crossing - min_a if np.isfinite(crossing) else np.nan,
            }
        )
    landmark_table = pd.DataFrame(landmark_rows)

    shuffle_results = {cohort: shuffle_test(intervals, cohort) for cohort in ["development", "holdout", "external"]}
    shuffle_table = pd.DataFrame([{k: v for k, v in result.items() if k != "null_values"} for result in shuffle_results.values()])

    cell_group_summary = []
    for cohort, d in cells.groupby("cohort"):
        low, high = bootstrap_ci(d.late_minus_early_rate)
        cell_group_summary.append(
            {
                "cohort": cohort,
                "cells": len(d),
                "median_observed_g1": float(d.observed_g1_count.median()),
                "min_observed_g1": int(d.observed_g1_count.min()),
                "max_observed_g1": int(d.observed_g1_count.max()),
                "median_lifespan_hours": float(d.lifespan_hours_observed.median()),
                "min_lifespan_hours": float(d.lifespan_hours_observed.min()),
                "max_lifespan_hours": float(d.lifespan_hours_observed.max()),
                "median_mean_interval_hours": float(d.mean_division_interval_hours.median()),
                "median_late_minus_early_rate": float(d.late_minus_early_rate.median()),
                "late_minus_early_bootstrap_q025": low,
                "late_minus_early_bootstrap_q975": high,
            }
        )
    cohort_summary = pd.DataFrame(cell_group_summary)

    shadow_transfer = transfer[transfer.metric == "time_shadow"].set_index("comparison")
    dev_cross = landmarks["development"]
    gates = {
        "same_platform_shadow_correlation_ge_0_60": bool(shadow_transfer.loc["development_vs_holdout", "correlation"] >= 0.60),
        "external_shadow_correlation_ge_0_60": bool(shadow_transfer.loc["development_vs_external", "correlation"] >= 0.60),
        "holdout_order_above_shuffle_q95": bool(shuffle_results["holdout"]["observed_median_late_minus_early"] > shuffle_results["holdout"]["null_q95"]),
        "external_order_above_shuffle_q95": bool(shuffle_results["external"]["observed_median_late_minus_early"] > shuffle_results["external"]["null_q95"]),
        "holdout_handover_within_0_20": bool(np.isfinite(dev_cross) and np.isfinite(landmarks["holdout"]) and abs(landmarks["holdout"] - dev_cross) <= 0.20),
        "external_handover_within_0_20": bool(np.isfinite(dev_cross) and np.isfinite(landmarks["external"]) and abs(landmarks["external"] - dev_cross) <= 0.20),
    }

    # Shape relationships among median interval curves. These are descriptive.
    witness_relationships = []
    for cohort in ["development", "holdout", "external"]:
        rate = median_curve(rate_summary, "local_time_rate", cohort, RATE_GRID)
        for metric in ["log_size_change", "log_rpl13a_concentration_change", "log_rpl13a_total_change"]:
            witness = median_curve(rate_summary, metric, cohort, RATE_GRID)
            witness_relationships.append({"cohort": cohort, "witness": metric, "same_A_curve_correlation_with_local_time_rate": safe_corr(rate, witness)})
    witness_relationships = pd.DataFrame(witness_relationships)

    metrics = {
        "test": "T452",
        "source_cells": int(len(cells)),
        "source_generation_rows": int(len(generations)),
        "source_interval_rows": int(len(intervals)),
        "forced_endpoint_warning": "Both endpoints close by construction; only interior shape, local ordering, transfer, and witnesses are informative.",
        "development_crossing_A": landmarks["development"],
        "holdout_crossing_A": landmarks["holdout"],
        "external_crossing_A": landmarks["external"],
        "gates": gates,
        "gates_passed": int(sum(gates.values())),
        "gates_total": int(len(gates)),
        "curve_transfer": transfer.to_dict(orient="records"),
        "shuffle_tests": shuffle_table.to_dict(orient="records"),
        "landmarks": landmark_table.to_dict(orient="records"),
    }

    generations.to_csv(RESULTS / "T452_GENERATION_STATES.csv", index=False)
    intervals.to_csv(RESULTS / "T452_INTERVAL_CHILDREN.csv", index=False)
    cells.to_csv(RESULTS / "T452_CELL_SUMMARY.csv", index=False)
    gen_summary.to_csv(RESULTS / "T452_GENERATION_CURVES.csv", index=False)
    rate_summary.to_csv(RESULTS / "T452_INTERVAL_CURVES.csv", index=False)
    transfer.to_csv(RESULTS / "T452_TRANSFER_METRICS.csv", index=False)
    shuffle_table.to_csv(RESULTS / "T452_SHUFFLE_TESTS.csv", index=False)
    landmark_table.to_csv(RESULTS / "T452_HANDOVER_LANDMARKS.csv", index=False)
    cohort_summary.to_csv(RESULTS / "T452_COHORT_SUMMARY.csv", index=False)
    witness_relationships.to_csv(RESULTS / "T452_WITNESS_RELATIONSHIPS.csv", index=False)
    (RESULTS / "T452_RESULT.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    make_figures(generations, intervals, cells, gen_summary, rate_summary, shuffle_results, metrics, landmarks)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
