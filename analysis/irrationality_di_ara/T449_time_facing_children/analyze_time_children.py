"""Analyze the frozen T449 temporal-child construction and controls."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).with_name(".mplconfig")))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T449_time_facing_children")
RESULTS = ROOT / "results"
T448_RESULTS = Path(
    r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara"
    r"\T448_fruitfly_lifecycle_tomography\results"
)
LAGS = np.arange(-12, 13)
MIN_CORR_PAIRS = 20
RNG_SEED = 44901


def robust_center_scale(values: pd.Series) -> tuple[float, float]:
    values = pd.to_numeric(values, errors="coerce").dropna()
    center = float(values.median())
    mad = float((values - center).abs().median()) * 1.4826
    if not math.isfinite(mad) or mad <= 1e-12:
        mad = float(values.std(ddof=0))
    return center, max(mad, 1e-12)


def add_differences(data: pd.DataFrame, a: str, b: str, prefix: str = "") -> pd.DataFrame:
    chunks = []
    for _, group in data.groupby("source_file", sort=False):
        group = group.sort_values("child_window_index").copy()
        consecutive = group.child_window_index.diff().eq(1)
        group[f"{prefix}dA"] = group[a].diff().where(consecutive)
        group[f"{prefix}dB"] = group[b].diff().where(consecutive)
        chunks.append(group)
    return pd.concat(chunks, ignore_index=True)


def fly_corr(group: pd.DataFrame, lag: int, da: str = "dA", db: str = "dB") -> tuple[float, int]:
    group = group.sort_values("child_window_index")
    index = group.child_window_index.astype(int).to_numpy()
    x = pd.Series(group[da].to_numpy(dtype=float), index=index)
    y = pd.Series(group[db].to_numpy(dtype=float), index=index)
    xv = x.to_numpy(dtype=float)
    yv = y.reindex(index + lag).to_numpy(dtype=float)
    valid = np.isfinite(xv) & np.isfinite(yv)
    if valid.sum() < MIN_CORR_PAIRS or np.std(xv[valid]) <= 1e-12 or np.std(yv[valid]) <= 1e-12:
        return math.nan, int(valid.sum())
    return float(np.corrcoef(xv[valid], yv[valid])[0, 1]), int(valid.sum())


def lag_scan(data: pd.DataFrame, da: str = "dA", db: str = "dB") -> tuple[pd.DataFrame, pd.DataFrame]:
    by_fly = []
    for name, group in data.groupby("source_file"):
        for lag in LAGS:
            corr, pairs = fly_corr(group, int(lag), da, db)
            by_fly.append({"source_file": name, "lag_windows": int(lag), "correlation": corr, "pairs": pairs})
    by_fly = pd.DataFrame(by_fly)
    summary = (
        by_fly.groupby("lag_windows")
        .agg(
            median_correlation=("correlation", "median"),
            q25=("correlation", lambda x: x.quantile(0.25)),
            q75=("correlation", lambda x: x.quantile(0.75)),
            flies=("correlation", "count"),
            pairs=("pairs", "sum"),
        )
        .reset_index()
    )
    return summary, by_fly


def reverse_histories(data: pd.DataFrame) -> pd.DataFrame:
    chunks = []
    for _, group in data.groupby("source_file", sort=False):
        group = group.copy()
        low, high = int(group.child_window_index.min()), int(group.child_window_index.max())
        group["child_window_index"] = low + high - group.child_window_index.astype(int)
        chunks.append(group)
    reversed_data = pd.concat(chunks, ignore_index=True)
    return add_differences(reversed_data, "C_A_retention", "C_B_traversal")


def circular_shift_null(data: pd.DataFrame, lag: int, iterations: int = 2000) -> np.ndarray:
    rng = np.random.default_rng(RNG_SEED)
    grids = []
    for _, group in data.groupby("source_file"):
        group = group.sort_values("child_window_index")
        low, high = int(group.child_window_index.min()), int(group.child_window_index.max())
        n = high - low + 1
        a = np.full(n, np.nan)
        b = np.full(n, np.nan)
        positions = group.child_window_index.astype(int).to_numpy() - low
        a[positions] = group.dA.to_numpy(dtype=float)
        b[positions] = group.dB.to_numpy(dtype=float)
        grids.append((a, b))

    null = np.empty(iterations, dtype=float)
    for iteration in range(iterations):
        correlations = []
        for a, b in grids:
            if len(b) < 3:
                continue
            shifted = np.roll(b, int(rng.integers(1, len(b))))
            if lag >= 0:
                x, y = a[: len(a) - lag or None], shifted[lag:]
            else:
                x, y = a[-lag:], shifted[: len(shifted) + lag]
            valid = np.isfinite(x) & np.isfinite(y)
            if valid.sum() >= MIN_CORR_PAIRS and np.std(x[valid]) > 1e-12 and np.std(y[valid]) > 1e-12:
                correlations.append(float(np.corrcoef(x[valid], y[valid])[0, 1]))
        null[iteration] = abs(float(np.median(correlations))) if correlations else math.nan
    return null[np.isfinite(null)]


def residualize_levels(eligible: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    data = eligible.copy()
    data["share_grooming"] = data[["share_fore_groom", "share_hind_groom", "share_wing_groom"]].sum(axis=1)
    data["zt_sin"] = np.sin(2 * np.pi * data.zt_hour / 24)
    data["zt_cos"] = np.cos(2 * np.pi * data.zt_hour / 24)
    features = [
        "share_idle",
        "share_proboscis",
        "share_grooming",
        "share_unstereotyped",
        "share_on_edge",
        "zt_sin",
        "zt_cos",
    ]
    dev = data.experiment.ne("exp4")
    x_dev = np.c_[np.ones(dev.sum()), data.loc[dev, features].to_numpy(dtype=float)]
    x_all = np.c_[np.ones(len(data)), data[features].to_numpy(dtype=float)]
    coefficients = {}
    for source, target in [("C_A_retention", "residual_A"), ("C_B_traversal", "residual_B")]:
        beta, *_ = np.linalg.lstsq(x_dev, data.loc[dev, source].to_numpy(dtype=float), rcond=None)
        data[target] = data[source] - x_all @ beta
        coefficients[source] = dict(zip(["intercept", *features], beta.tolist()))
    return add_differences(data, "residual_A", "residual_B", prefix="residual_"), coefficients


def find_exchanges(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for name, group in data.groupby("source_file"):
        group = group.sort_values("child_window_index")
        previous = group.shift(1)
        crossing = (
            group.child_window_index.sub(previous.child_window_index).eq(1)
            & np.isfinite(group.dominance)
            & np.isfinite(previous.dominance)
            & (np.sign(group.dominance) != np.sign(previous.dominance))
            & group.dominance.ne(0)
            & previous.dominance.ne(0)
        )
        for index in group.index[crossing]:
            row = group.loc[index]
            rows.append(
                {
                    "source_file": name,
                    "experiment": row.experiment,
                    "child_window_index": int(row.child_window_index),
                    "child_midpoint_hours": float(row.child_midpoint_hours),
                    "hours_to_collapse": float(row.hours_to_collapse),
                    "from_side": "retention" if previous.loc[index].dominance > 0 else "traversal",
                    "to_side": "retention" if row.dominance > 0 else "traversal",
                    "dominance_before": float(previous.loc[index].dominance),
                    "dominance_after": float(row.dominance),
                    "ara_A": float(row.ara_A),
                    "ara_B": float(row.ara_B),
                    "idle_share": float(row.share_idle),
                    "unresolved_share": float(row.share_unstereotyped + row.share_on_edge),
                }
            )
    return pd.DataFrame(rows)


def attach_parent_response(exchanges: pd.DataFrame, parent: pd.DataFrame) -> pd.DataFrame:
    rows = []
    parent_groups = {name: group.sort_values("hour_midpoint") for name, group in parent.groupby("source_file")}
    for _, event in exchanges.iterrows():
        history = parent_groups.get(event.source_file)
        if history is None:
            continue
        before = history[history.hour_midpoint < event.child_midpoint_hours].tail(1)
        after = history[history.hour_midpoint > event.child_midpoint_hours].head(1)
        if before.empty or after.empty:
            continue
        if event.child_midpoint_hours - before.hour_midpoint.iloc[0] > 1.2:
            continue
        if after.hour_midpoint.iloc[0] - event.child_midpoint_hours > 1.2:
            continue
        row = event.to_dict()
        row["parent_before"] = float(before.parallel_progress.iloc[0])
        row["parent_after"] = float(after.parallel_progress.iloc[0])
        row["parent_delta_after_minus_before"] = row["parent_after"] - row["parent_before"]
        rows.append(row)
    return pd.DataFrame(rows)


def exchange_shift_null(exchanges: pd.DataFrame, parent: pd.DataFrame, iterations: int = 2000) -> np.ndarray:
    rng = np.random.default_rng(RNG_SEED + 3)
    parent_groups = {}
    for name, group in parent.groupby("source_file"):
        group = group.sort_values("hour_midpoint")
        times = group.hour_midpoint.to_numpy(dtype=float)
        progress = group.parallel_progress.to_numpy(dtype=float)
        parent_groups[name] = (times, np.diff(progress))
    event_groups = {
        name: group.child_midpoint_hours.to_numpy(dtype=float)
        for name, group in exchanges.groupby("source_file")
    }
    null = np.full(iterations, np.nan)
    for iteration in range(iterations):
        fly_values = []
        for name, event_times in event_groups.items():
            parent_arrays = parent_groups.get(name)
            if parent_arrays is None:
                continue
            times, adjacent_delta = parent_arrays
            if len(times) < 4:
                continue
            low, high = float(times[0]), float(times[-1])
            width = high - low
            shift = float(rng.uniform(0, width))
            shifted = low + ((event_times - low + shift) % width)
            indices = np.searchsorted(times, shifted, side="left") - 1
            valid = (indices >= 0) & (indices < len(adjacent_delta))
            if valid.any():
                fly_values.append(float(np.median(adjacent_delta[indices[valid]])))
        if fly_values:
            null[iteration] = float(np.median(fly_values))
    return null[np.isfinite(null)]


def binned_history(data: pd.DataFrame, stop: int = 96, step: int = 3) -> pd.DataFrame:
    cut = data[(data.hours_to_collapse > 0) & (data.hours_to_collapse <= stop)].copy()
    cut["bin"] = pd.cut(cut.hours_to_collapse, np.arange(0, stop + step, step), include_lowest=True)
    cut["hours_before"] = cut.bin.map(lambda x: float(x.mid))
    rows = []
    for (split, midpoint), group in cut.groupby(["split", "hours_before"], observed=True):
        row = {"split": split, "hours_before": midpoint, "windows": len(group)}
        for column in ["ara_A", "ara_B", "dominance", "resolved_fraction", "share_unstereotyped", "share_on_edge"]:
            row[f"{column}_median"] = float(group[column].median())
            row[f"{column}_q25"] = float(group[column].quantile(0.25))
            row[f"{column}_q75"] = float(group[column].quantile(0.75))
        rows.append(row)
    return pd.DataFrame(rows).sort_values(["split", "hours_before"])


def stage_label(hours: float) -> str:
    if hours <= 6:
        return "0–6 h"
    if hours <= 24:
        return "6–24 h"
    if hours <= 72:
        return "24–72 h"
    return ">72 h"


def configure_plots() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#f7f9fc",
            "axes.facecolor": "#ffffff",
            "savefig.facecolor": "#f7f9fc",
            "text.color": "#18212f",
            "axes.labelcolor": "#18212f",
            "axes.edgecolor": "#667085",
            "xtick.color": "#344054",
            "ytick.color": "#344054",
            "grid.color": "#d0d5dd",
            "font.size": 10,
            "axes.titleweight": "bold",
        }
    )


def save_visuals(
    all_data: pd.DataFrame,
    eligible: pd.DataFrame,
    histories: pd.DataFrame,
    lag_combined: pd.DataFrame,
    dev_fly: pd.DataFrame,
    hold_fly: pd.DataFrame,
    reverse_scan: pd.DataFrame,
    null: np.ndarray,
    frozen_lag: int,
    observed_coupling: float,
    shuffle_coupling: float,
    residual_coupling: float,
    exchange_response: pd.DataFrame,
    exchange_null: np.ndarray,
    parent: pd.DataFrame,
) -> None:
    configure_plots()
    blue, orange, purple, grey, pink = "#2f6bff", "#f28e2b", "#8f63d3", "#667085", "#d84a78"

    # 1 — scope and visibility.
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    coverage = all_data.groupby(["experiment", "source_file"]).eligible.agg(["sum", "count"]).reset_index()
    coverage["fraction"] = coverage["sum"] / coverage["count"]
    exp = all_data.groupby("experiment").eligible.agg(["sum", "count"])
    axes[0, 0].bar(exp.index, exp["count"], color="#d9e3f7", label="all windows")
    axes[0, 0].bar(exp.index, exp["sum"], color=blue, label="eligible")
    axes[0, 0].set(title="Ten-minute windows retained by experiment", ylabel="window count")
    axes[0, 0].legend()
    for experiment, group in coverage.groupby("experiment"):
        axes[0, 1].scatter([experiment] * len(group), group.fraction, alpha=0.75, label=experiment)
    axes[0, 1].axhline(0.8, color=grey, ls=":", label="per-window resolved threshold")
    axes[0, 1].set(title="Eligibility varies materially between individual flies", ylabel="eligible fraction", ylim=(0, 1))
    axes[0, 1].legend(ncol=2)
    raw = all_data[(all_data.hours_to_collapse > 0) & (all_data.hours_to_collapse <= 96)].copy()
    raw["bin"] = pd.cut(raw.hours_to_collapse, np.arange(0, 99, 3))
    q = raw.groupby(["experiment", "bin"], observed=True).eligible.mean().reset_index()
    q["mid"] = q.bin.map(lambda x: x.mid).astype(float)
    for exp_name, group in q.groupby("experiment"):
        axes[1, 0].plot(group.mid, group.eligible, marker="o", ms=3, label=exp_name)
    axes[1, 0].invert_xaxis()
    axes[1, 0].set(title="Visibility across the final 96 hours", xlabel="hours before collapse", ylabel="eligible fraction", ylim=(0, 1))
    axes[1, 0].legend(ncol=2)
    axes[1, 1].hist(all_data.share_unstereotyped, bins=35, alpha=0.65, color=orange, label="unstereotyped")
    axes[1, 1].hist(all_data.share_on_edge, bins=35, alpha=0.55, color=purple, label="on edge")
    axes[1, 1].set(title="Unresolved classifier shares retained as controls", xlabel="share of one-second states", ylabel="windows")
    axes[1, 1].legend()
    for ax in axes.flat:
        ax.grid(alpha=0.35)
    fig.suptitle("T449 — data scope and temporal visibility", fontsize=18)
    fig.savefig(RESULTS / "T449_01_scope_and_visibility.png", dpi=180)
    plt.close(fig)

    # 2 — raw children and timestamp-shuffle comparison.
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    sample = eligible.sample(min(7000, len(eligible)), random_state=RNG_SEED)
    axes[0, 0].hist(sample.C_A_retention, bins=45, alpha=0.7, color=blue, density=True, label="ordered")
    axes[0, 0].hist(sample.shuffle_C_A_retention, bins=45, alpha=0.55, color=grey, density=True, label="timestamp shuffled")
    axes[0, 0].set(title="Child A: above-chance temporal retention", xlabel="C_A retention", ylabel="density")
    axes[0, 0].legend()
    axes[0, 1].hist(sample.C_B_traversal, bins=45, alpha=0.7, color=orange, density=True, label="ordered")
    axes[0, 1].hist(sample.shuffle_C_B_traversal, bins=45, alpha=0.55, color=grey, density=True, label="timestamp shuffled")
    axes[0, 1].set(title="Child B: conditional transition entropy", xlabel="C_B traversal", ylabel="density")
    axes[0, 1].legend()
    sc = axes[1, 0].scatter(sample.ara_A, sample.ara_B, c=np.clip(sample.hours_to_collapse, 0, 96), s=7, alpha=0.25, cmap="viridis_r")
    axes[1, 0].plot([0, 2], [0, 2], color=grey, ls="--", label="standardized exchange line")
    axes[1, 0].axvline(1, color=grey, ls=":")
    axes[1, 0].axhline(1, color=grey, ls=":")
    axes[1, 0].set(title="Same-rung child plane", xlabel="C_A retention ARA (0–2 display)", ylabel="C_B traversal ARA (0–2 display)", xlim=(0, 2), ylim=(0, 2))
    axes[1, 0].legend()
    fig.colorbar(sc, ax=axes[1, 0], label="hours before collapse (clipped 96)")
    axes[1, 1].scatter(sample.C_A_retention, sample.C_B_traversal, s=7, alpha=0.2, color=purple)
    axes[1, 1].set(title="Raw coordinates are related but not forced complements", xlabel="C_A retention", ylabel="C_B traversal")
    for ax in axes.flat:
        ax.grid(alpha=0.3)
    fig.suptitle("T449 — ordered temporal children before biological interpretation", fontsize=18)
    fig.savefig(RESULTS / "T449_02_child_coordinates_and_shuffle.png", dpi=180)
    plt.close(fig)

    # 3 — directed lag and controls.
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    colors = {"development ordered": blue, "holdout ordered": orange, "holdout shuffled": grey}
    for name, group in lag_combined.groupby("series"):
        axes[0, 0].plot(group.lag_windows * 10, group.median_correlation, marker="o", ms=3, color=colors[name], label=name)
    axes[0, 0].axvline(frozen_lag * 10, color=pink, ls="--", label=f"frozen lag {frozen_lag*10:+d} min")
    axes[0, 0].axhline(0, color=grey, ls=":")
    axes[0, 0].set(title="Lead–lag scan of child changes", xlabel="lag: Child A leads Child B by minutes", ylabel="median within-fly correlation")
    axes[0, 0].legend()
    axes[0, 1].hist(null, bins=40, color="#c7ced9")
    axes[0, 1].axvline(np.quantile(null, 0.95), color=orange, ls="--", label=f"shift 95% = {np.quantile(null,0.95):.3f}")
    axes[0, 1].axvline(abs(observed_coupling), color=pink, lw=2.5, label=f"observed = {abs(observed_coupling):.3f}")
    axes[0, 1].set(title="Frozen holdout coupling against circular shifts", xlabel="absolute median coupling", ylabel="shifted histories")
    axes[0, 1].legend()
    fly = hold_fly[hold_fly.lag_windows.eq(frozen_lag)].dropna().sort_values("correlation")
    axes[1, 0].barh(np.arange(len(fly)), fly.correlation, color=np.where(fly.correlation >= 0, blue, orange))
    axes[1, 0].axvline(0, color=grey, ls=":")
    axes[1, 0].set(title="Each untouched fly at the frozen lag", xlabel="within-fly correlation", ylabel="holdout fly (sorted)")
    axes[1, 0].set_yticks([])
    axes[1, 1].plot(reverse_scan.lag_windows * 10, reverse_scan.median_correlation, marker="o", ms=3, color=purple)
    axes[1, 1].axvline(-frozen_lag * 10, color=pink, ls="--", label="expected reversed address")
    axes[1, 1].axhline(0, color=grey, ls=":")
    axes[1, 1].set(title="Full-history time reversal", xlabel="reversed lag address (minutes)", ylabel="median within-fly correlation")
    axes[1, 1].legend()
    for ax in axes.flat:
        ax.grid(alpha=0.3)
    fig.suptitle("T449 — the directed relation is tested, not assumed", fontsize=18)
    fig.savefig(RESULTS / "T449_03_lead_lag_and_temporal_controls.png", dpi=180)
    plt.close(fig)

    # 4 — parent-facing histories.
    fig, axes = plt.subplots(3, 1, figsize=(15, 13), sharex=True, constrained_layout=True)
    for split, group in histories.groupby("split"):
        style = "-" if split == "holdout" else "--"
        alpha = 1 if split == "holdout" else 0.7
        axes[0].plot(group.hours_before, group.ara_A_median, color=blue, ls=style, alpha=alpha, label=f"A retention — {split}")
        axes[0].plot(group.hours_before, group.ara_B_median, color=orange, ls=style, alpha=alpha, label=f"B traversal — {split}")
        axes[1].plot(group.hours_before, group.dominance_median, color=purple if split == "holdout" else grey, ls=style, label=split)
        axes[2].plot(group.hours_before, group.resolved_fraction_median, color=blue if split == "holdout" else grey, ls=style, label=f"resolved — {split}")
        axes[2].plot(group.hours_before, group.share_unstereotyped_median, color=orange, ls=style, alpha=alpha, label=f"unresolved — {split}")
    axes[0].axhline(1, color=grey, ls=":")
    axes[0].set(title="Median child coordinates", ylabel="ARA display coordinate (0–2)", ylim=(0, 2))
    axes[0].legend(ncol=2)
    axes[1].axhline(0, color=grey, ls=":")
    axes[1].set(title="Child dominance: retention minus traversal", ylabel="standardized dominance")
    axes[1].legend()
    axes[2].set(title="Classifier visibility is shown beside the geometry", xlabel="hours before collapse", ylabel="share", ylim=(0, 1))
    axes[2].legend(ncol=2)
    for ax in axes:
        ax.grid(alpha=0.3)
        ax.invert_xaxis()
    fig.suptitle("T449 — lifecycle-aligned child histories; collapse is used only for retrospective evaluation", fontsize=17)
    fig.savefig(RESULTS / "T449_04_lifecycle_aligned_child_histories.png", dpi=180)
    plt.close(fig)

    # 5 — phase trajectory and quadrant occupancy.
    fig, axes = plt.subplots(1, 3, figsize=(19, 6), constrained_layout=True)
    stage_colors = {">72 h": "#98a2b3", "24–72 h": blue, "6–24 h": orange, "0–6 h": pink}
    hold = eligible[eligible.split.eq("holdout")].copy()
    hold["stage"] = hold.hours_to_collapse.map(stage_label)
    for stage in [">72 h", "24–72 h", "6–24 h", "0–6 h"]:
        group = hold[hold.stage.eq(stage)]
        sample_stage = group.sample(min(900, len(group)), random_state=RNG_SEED) if len(group) else group
        axes[0].scatter(sample_stage.ara_A, sample_stage.ara_B, s=8, alpha=0.24, color=stage_colors[stage], label=stage)
    axes[0].plot([0, 2], [0, 2], color=grey, ls="--")
    axes[0].axvline(1, color=grey, ls=":")
    axes[0].axhline(1, color=grey, ls=":")
    axes[0].set(title="Untouched child plane by lifecycle stage", xlabel="C_A retention ARA", ylabel="C_B traversal ARA", xlim=(0, 2), ylim=(0, 2))
    axes[0].legend()
    trajectory = hold[(hold.hours_to_collapse > 0) & (hold.hours_to_collapse <= 96)].copy()
    trajectory["bin"] = pd.cut(trajectory.hours_to_collapse, np.arange(0, 102, 6))
    trajectory = trajectory.groupby("bin", observed=True).agg(ara_A=("ara_A", "median"), ara_B=("ara_B", "median")).reset_index()
    trajectory["hours"] = trajectory.bin.map(lambda x: x.mid).astype(float)
    trajectory = trajectory.sort_values("hours", ascending=False)
    axes[1].plot(trajectory.ara_A, trajectory.ara_B, marker="o", color=purple)
    for _, row in trajectory.iloc[::2].iterrows():
        axes[1].annotate(f"{row.hours:.0f} h", (row.ara_A, row.ara_B), fontsize=8)
    axes[1].plot([0, 2], [0, 2], color=grey, ls="--")
    axes[1].set(title="Median path through the final 96 hours", xlabel="C_A retention ARA", ylabel="C_B traversal ARA", xlim=(0, 2), ylim=(0, 2))
    occupancy = []
    for stage, group in hold.groupby("stage"):
        quadrants = pd.Series(np.select(
            [
                (group.ara_A < 1) & (group.ara_B >= 1),
                (group.ara_A >= 1) & (group.ara_B >= 1),
                (group.ara_A < 1) & (group.ara_B < 1),
            ],
            ["low A / high B", "high A / high B", "low A / low B"],
            default="high A / low B",
        )).value_counts(normalize=True)
        for quadrant, share in quadrants.items():
            occupancy.append({"stage": stage, "quadrant": quadrant, "share": share})
    occupancy = pd.DataFrame(occupancy)
    pivot = occupancy.pivot(index="stage", columns="quadrant", values="share").fillna(0).reindex([">72 h", "24–72 h", "6–24 h", "0–6 h"])
    pivot.plot(kind="bar", stacked=True, ax=axes[2], color=["#d9e3f7", blue, orange, purple][: len(pivot.columns)])
    axes[2].set(title="Quadrant occupancy changes with lifecycle stage", xlabel="hours before collapse", ylabel="share", ylim=(0, 1))
    axes[2].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.suptitle("T449 — child geometry is a gradient, not a universal terminal point", fontsize=18)
    fig.savefig(RESULTS / "T449_05_child_plane_and_gradient_path.png", dpi=180)
    plt.close(fig)

    # 6 — exchange landmarks and parent response.
    fig, axes = plt.subplots(1, 3, figsize=(19, 6), constrained_layout=True)
    if len(exchange_response):
        fly_delta = exchange_response.groupby("source_file").parent_delta_after_minus_before.median().sort_values()
        axes[0].barh(np.arange(len(fly_delta)), fly_delta, color=np.where(fly_delta >= 0, blue, orange))
        axes[0].axvline(0, color=grey, ls=":")
        axes[0].set(title="Median parent response after child exchanges", xlabel="following minus preceding parent progress", ylabel="holdout fly")
        axes[0].set_yticks([])
        axes[1].hist(exchange_null, bins=40, color="#c7ced9")
        actual = float(fly_delta.median())
        axes[1].axvline(np.quantile(exchange_null, 0.95), color=orange, ls="--", label=f"shift 95% = {np.quantile(exchange_null,0.95):.3f}")
        axes[1].axvline(actual, color=pink, lw=2.5, label=f"actual = {actual:.3f}")
        axes[1].set(title="Exchange timing against shifted landmarks", xlabel="median parent response", ylabel="shifted histories")
        axes[1].legend()
        axes[2].scatter(exchange_response.ara_A, exchange_response.ara_B, c=np.clip(exchange_response.hours_to_collapse, 0, 96), cmap="viridis_r", s=10, alpha=0.35)
        axes[2].plot([0, 2], [0, 2], color=grey, ls="--")
        axes[2].set(title="Where the descriptive exchanges occur", xlabel="C_A retention ARA", ylabel="C_B traversal ARA", xlim=(0, 2), ylim=(0, 2))
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.suptitle("T449 — child exchange landmarks tested against the existing parent direction", fontsize=18)
    fig.savefig(RESULTS / "T449_06_exchange_to_parent_response.png", dpi=180)
    plt.close(fig)

    # 7 — biological reduction control.
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)
    labels = ["ordered raw", "composition-residual", "timestamp-shuffled"]
    values = [observed_coupling, residual_coupling, shuffle_coupling]
    axes[0].bar(labels, values, color=[blue, purple, grey])
    axes[0].axhline(0, color=grey, ls=":")
    axes[0].set(title="Holdout coupling after biological-composition controls", ylabel="median correlation at frozen lag")
    axes[0].tick_params(axis="x", rotation=20)
    small = eligible.sample(min(7000, len(eligible)), random_state=RNG_SEED)
    axes[1].scatter(small.share_idle, small.C_A_retention, s=6, alpha=0.2, color=blue)
    axes[1].set(title="Retention against idle occupancy", xlabel="idle share", ylabel="C_A retention")
    axes[2].scatter(small.share_idle, small.C_B_traversal, s=6, alpha=0.2, color=orange)
    axes[2].set(title="Traversal against idle occupancy", xlabel="idle share", ylabel="C_B traversal")
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.suptitle("T449 — biological behaviour is an overlay and a confound control, not the preselected child axis", fontsize=17)
    fig.savefig(RESULTS / "T449_07_biological_reduction_control.png", dpi=180)
    plt.close(fig)

    # 8 — selected individual holdout paths.
    coverage = hold.groupby("source_file").size().sort_values(ascending=False)
    selected = list(coverage.head(6).index)
    fig, axes = plt.subplots(3, 2, figsize=(17, 14), constrained_layout=True)
    for ax, name in zip(axes.flat, selected):
        group = hold[(hold.source_file.eq(name)) & (hold.hours_to_collapse > 0) & (hold.hours_to_collapse <= 72)].sort_values("hours_to_collapse", ascending=False)
        ax.plot(group.hours_to_collapse, group.ara_A, color=blue, lw=1.4, label="A retention")
        ax.plot(group.hours_to_collapse, group.ara_B, color=orange, lw=1.4, label="B traversal")
        ax.axhline(1, color=grey, ls=":")
        ax.invert_xaxis()
        ax.set(title=name.replace(".h5", ""), xlabel="hours before collapse", ylabel="ARA coordinate", ylim=(0, 2))
        ax.grid(alpha=0.3)
    axes.flat[0].legend()
    fig.suptitle("T449 — individual untouched flies retain asymmetry around the population gradient", fontsize=18)
    fig.savefig(RESULTS / "T449_08_individual_holdout_paths.png", dpi=180)
    plt.close(fig)


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    all_data = pd.read_csv(RESULTS / "T449_child_windows.csv")
    numeric = [column for column in all_data.columns if column not in {"date", "experiment", "well", "fly_id_index", "source_file"}]
    for column in numeric:
        all_data[column] = pd.to_numeric(all_data[column], errors="coerce")
    all_data["split"] = np.where(all_data.experiment.eq("exp4"), "holdout", "development")
    eligible = all_data[all_data.eligible.eq(1)].copy()

    dev = eligible[eligible.split.eq("development")]
    center_a, scale_a = robust_center_scale(dev.C_A_retention)
    center_b, scale_b = robust_center_scale(dev.C_B_traversal)
    for frame in [all_data, eligible]:
        frame["z_A"] = (frame.C_A_retention - center_a) / scale_a
        frame["z_B"] = (frame.C_B_traversal - center_b) / scale_b
        frame["ara_A"] = np.clip(1 + 0.5 * frame.z_A, 0, 2)
        frame["ara_B"] = np.clip(1 + 0.5 * frame.z_B, 0, 2)
        frame["dominance"] = frame.z_A - frame.z_B

    dynamic = add_differences(eligible, "C_A_retention", "C_B_traversal")
    dev_dynamic = dynamic[dynamic.split.eq("development")]
    hold_dynamic = dynamic[dynamic.split.eq("holdout")]
    dev_scan, dev_fly = lag_scan(dev_dynamic)
    frozen_row = dev_scan.iloc[dev_scan.median_correlation.abs().argmax()]
    frozen_lag = int(frozen_row.lag_windows)
    development_coupling = float(frozen_row.median_correlation)
    frozen_sign = int(np.sign(development_coupling))
    hold_scan, hold_fly = lag_scan(hold_dynamic)
    observed_coupling = float(hold_scan.loc[hold_scan.lag_windows.eq(frozen_lag), "median_correlation"].iloc[0])

    shuffled_dynamic = add_differences(eligible, "shuffle_C_A_retention", "shuffle_C_B_traversal")
    shuffled_hold_scan, shuffled_hold_fly = lag_scan(shuffled_dynamic[shuffled_dynamic.split.eq("holdout")])
    shuffle_coupling = float(shuffled_hold_scan.loc[shuffled_hold_scan.lag_windows.eq(frozen_lag), "median_correlation"].iloc[0])

    reverse_scan, reverse_fly = lag_scan(reverse_histories(eligible[eligible.split.eq("holdout")]))
    reverse_lag = int(reverse_scan.iloc[reverse_scan.median_correlation.abs().argmax()].lag_windows)
    reverse_coupling = float(reverse_scan.iloc[reverse_scan.median_correlation.abs().argmax()].median_correlation)

    null = circular_shift_null(hold_dynamic, frozen_lag)
    null95 = float(np.quantile(null, 0.95))
    q1_p = float((1 + np.sum(null >= abs(observed_coupling))) / (len(null) + 1))

    hold_at_lag = hold_fly[hold_fly.lag_windows.eq(frozen_lag)].dropna(subset=["correlation"])
    sign_fraction = float((np.sign(hold_at_lag.correlation) == frozen_sign).mean()) if len(hold_at_lag) else math.nan

    residual_dynamic, coefficients = residualize_levels(eligible)
    residual_hold_scan, residual_hold_fly = lag_scan(
        residual_dynamic[residual_dynamic.split.eq("holdout")], "residual_dA", "residual_dB"
    )
    residual_coupling = float(
        residual_hold_scan.loc[residual_hold_scan.lag_windows.eq(frozen_lag), "median_correlation"].iloc[0]
    )
    residual_ratio = abs(residual_coupling) / max(abs(observed_coupling), 1e-12)

    level_corr = float(eligible[["C_A_retention", "C_B_traversal"]].corr().iloc[0, 1])
    change_corr = float(dynamic[["dA", "dB"]].corr().iloc[0, 1])
    near_deterministic_complement = abs(level_corr) >= 0.95 or abs(change_corr) >= 0.95

    exchanges = find_exchanges(eligible[eligible.split.eq("holdout")])
    parent = pd.read_csv(T448_RESULTS / "T448B_24h_directional_states.csv")
    parent = parent[parent.split.eq("holdout")].copy()
    exchange_response = attach_parent_response(exchanges, parent)
    exchange_null = exchange_shift_null(exchanges, parent)
    if len(exchange_response):
        actual_parent_response = float(
            exchange_response.groupby("source_file").parent_delta_after_minus_before.median().median()
        )
    else:
        actual_parent_response = math.nan
    exchange_null95 = float(np.quantile(exchange_null, 0.95)) if len(exchange_null) else math.nan
    exchange_p = (
        float((1 + np.sum(exchange_null >= actual_parent_response)) / (len(exchange_null) + 1))
        if len(exchange_null) and math.isfinite(actual_parent_response)
        else math.nan
    )

    histories = binned_history(eligible)
    lag_combined = pd.concat(
        [
            dev_scan.assign(series="development ordered"),
            hold_scan.assign(series="holdout ordered"),
            shuffled_hold_scan.assign(series="holdout shuffled"),
        ],
        ignore_index=True,
    )

    gates = {
        "Q1_ordered_coupling_exceeds_shift95_and_shuffle_weaker": bool(
            abs(observed_coupling) > null95 and abs(shuffle_coupling) < abs(observed_coupling)
        ),
        "Q2_sign_transfers_and_reversal_flips_lag": bool(
            sign_fraction >= 0.65 and frozen_lag != 0 and reverse_lag == -frozen_lag
        ),
        "Q3_exchange_precedes_parent_progress_beyond_shift95": bool(
            math.isfinite(actual_parent_response) and actual_parent_response > exchange_null95
        ),
        "Q4_residual_coupling_retains_at_least_half": bool(residual_ratio >= 0.5),
    }

    eligibility_by_fly = (
        all_data.groupby(["split", "experiment", "source_file"])
        .eligible.agg(windows="size", eligible_windows="sum")
        .reset_index()
    )
    eligibility_by_fly["eligible_fraction"] = eligibility_by_fly.eligible_windows / eligibility_by_fly.windows
    eligibility_by_fly.to_csv(RESULTS / "T449_eligibility_by_fly.csv", index=False)
    histories.to_csv(RESULTS / "T449_binned_child_histories.csv", index=False)
    lag_combined.to_csv(RESULTS / "T449_lag_scan.csv", index=False)
    dev_fly.assign(split="development", series="ordered").to_csv(RESULTS / "T449_development_fly_lags.csv", index=False)
    hold_fly.assign(split="holdout", series="ordered").to_csv(RESULTS / "T449_holdout_fly_lags.csv", index=False)
    reverse_fly.assign(split="holdout", series="reversed").to_csv(RESULTS / "T449_reversed_holdout_fly_lags.csv", index=False)
    exchanges.to_csv(RESULTS / "T449_holdout_exchanges.csv", index=False)
    exchange_response.to_csv(RESULTS / "T449_exchange_parent_response.csv", index=False)
    eligible.to_csv(RESULTS / "T449_eligible_child_geometry.csv", index=False)

    save_visuals(
        all_data,
        eligible,
        histories,
        lag_combined,
        dev_fly,
        hold_fly,
        reverse_scan,
        null,
        frozen_lag,
        observed_coupling,
        shuffle_coupling,
        residual_coupling,
        exchange_response,
        exchange_null,
        parent,
    )

    result = {
        "test": "T449 same-rung time-facing children",
        "source_windows": int(len(all_data)),
        "eligible_windows": int(len(eligible)),
        "eligible_fraction": float(len(eligible) / len(all_data)),
        "development_flies": int(eligible[eligible.split.eq("development")].source_file.nunique()),
        "holdout_flies": int(eligible[eligible.split.eq("holdout")].source_file.nunique()),
        "development_scaling": {
            "C_A_center": center_a,
            "C_A_robust_scale": scale_a,
            "C_B_center": center_b,
            "C_B_robust_scale": scale_b,
        },
        "frozen_development_lag_windows": frozen_lag,
        "frozen_development_lag_minutes": frozen_lag * 10,
        "development_median_coupling": development_coupling,
        "holdout_median_coupling": observed_coupling,
        "holdout_timestamp_shuffle_coupling": shuffle_coupling,
        "holdout_circular_shift_95pct": null95,
        "holdout_circular_shift_p": q1_p,
        "holdout_fly_sign_fraction": sign_fraction,
        "reverse_selected_lag_windows": reverse_lag,
        "reverse_selected_lag_minutes": reverse_lag * 10,
        "reverse_selected_coupling": reverse_coupling,
        "composition_residual_holdout_coupling": residual_coupling,
        "composition_residual_retained_ratio": residual_ratio,
        "level_C_A_C_B_correlation": level_corr,
        "change_C_A_C_B_correlation": change_corr,
        "near_deterministic_complement": near_deterministic_complement,
        "holdout_exchange_landmarks": int(len(exchanges)),
        "exchange_parent_response_events": int(len(exchange_response)),
        "actual_median_parent_response": actual_parent_response,
        "exchange_shift_95pct": exchange_null95,
        "exchange_shift_p": exchange_p,
        "gates": gates,
        "residual_coefficients": coefficients,
    }
    (RESULTS / "T449_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
