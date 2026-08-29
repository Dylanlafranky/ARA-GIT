"""Frozen T448 lifecycle geometry analysis and visual report assets."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
import pandas as pd


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T448_fruitfly_lifecycle_tomography")
RESULTS = ROOT / "results"
SOURCE = ROOT / "source"
ZCOLS = ["z_traversal_maintenance", "z_action_intake", "z_participation_quiescence"]
WCOLS = ["w_traversal_maintenance", "w_action_intake", "w_participation_quiescence"]
ACOLS = ["ara_traversal_maintenance", "ara_action_intake", "ara_participation_quiescence"]
SHORT = ["T↔G", "Action↔Intake", "Participation↔Idle"]
COLORS = {"early >72 h": "#4c78a8", "middle 24–72 h": "#f58518", "late 6–24 h": "#54a24b", "terminal 0–6 h": "#b279a2"}


def style():
    plt.rcParams.update(
        {
            "figure.facecolor": "#0f1622",
            "axes.facecolor": "#131d2c",
            "savefig.facecolor": "#0f1622",
            "text.color": "#e8edf4",
            "axes.labelcolor": "#e8edf4",
            "axes.edgecolor": "#aeb8c6",
            "xtick.color": "#d5dbe4",
            "ytick.color": "#d5dbe4",
            "grid.color": "#334155",
            "font.size": 10,
            "axes.titleweight": "bold",
        }
    )


def stage_of(hours):
    return pd.cut(
        hours,
        bins=[-np.inf, 6, 24, 72, np.inf],
        labels=["terminal 0–6 h", "late 6–24 h", "middle 24–72 h", "early >72 h"],
    )


def auc(labels, scores):
    labels = np.asarray(labels, dtype=int)
    scores = pd.Series(np.asarray(scores)).rank(method="average").to_numpy()
    n1 = labels.sum()
    n0 = len(labels) - n1
    if n1 == 0 or n0 == 0:
        return math.nan
    return float((scores[labels == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def ellipse_from_points(ax, points, color, label=None, level=2.0, lw=2.2, ls="-"):
    points = np.asarray(points, dtype=float)
    center = np.median(points, axis=0)
    cov = np.cov(points, rowvar=False)
    values, vectors = np.linalg.eigh(cov)
    order = np.argsort(values)[::-1]
    values, vectors = values[order], vectors[:, order]
    angle = np.degrees(np.arctan2(vectors[1, 0], vectors[0, 0]))
    patch = Ellipse(
        center,
        2 * level * np.sqrt(max(values[0], 1e-12)),
        2 * level * np.sqrt(max(values[1], 1e-12)),
        angle=angle,
        fill=False,
        edgecolor=color,
        lw=lw,
        ls=ls,
        label=label,
    )
    ax.add_patch(patch)
    return center, values


def binned_summary(data, x, ys, start=0, stop=72, step=3):
    cut = data[(data[x] > start) & (data[x] <= stop)].copy()
    cut["bin"] = pd.cut(cut[x], bins=np.arange(start, stop + step, step), right=True)
    centers = cut["bin"].map(lambda interval: interval.mid).astype(float)
    cut["bin_center"] = centers
    out = []
    for name, group in cut.groupby("bin_center", observed=True):
        row = {"bin_center": float(name), "n": len(group)}
        for y in ys:
            row[f"{y}_median"] = group[y].median()
            row[f"{y}_q25"] = group[y].quantile(0.25)
            row[f"{y}_q75"] = group[y].quantile(0.75)
        out.append(row)
    return pd.DataFrame(out).sort_values("bin_center")


def attach_environment(data):
    idx = pd.read_csv(SOURCE / "analysis_data_index.csv")
    idx = idx[idx["Experiment"].notna()].copy()
    idx["camera"] = idx["Camera"].str.extract(r"(\d+)").astype(int)
    idx["well"] = idx["Well location"].str.upper()
    idx["local_start"] = pd.to_datetime(idx["Start Time"], errors="coerce")
    lookup = idx.set_index(["Experiment", "camera", "well"])["local_start"]
    starts = [lookup.get((row.experiment, int(row.camera), row.well), pd.NaT) for row in data.itertuples()]
    data["local_datetime"] = pd.to_datetime(starts) + pd.to_timedelta(data["hour_midpoint"], unit="h")

    env = []
    for filename in ["02-17-2022.csv", "03-12-2022.csv", "03-26-2022.csv", "04-18-2022.csv"]:
        frame = pd.read_csv(SOURCE / filename)
        frame["local_datetime"] = pd.to_datetime(frame["DATETIME"], errors="coerce")
        env.append(frame[["local_datetime", "TEMPERATURE", "RELATIVE-HUMIDITY"]])
    env = pd.concat(env, ignore_index=True).dropna().sort_values("local_datetime")
    env["local_datetime"] = env["local_datetime"].astype("datetime64[ns]")
    ordered = data.sort_values("local_datetime").copy()
    ordered["local_datetime"] = ordered["local_datetime"].astype("datetime64[ns]")
    ordered = pd.merge_asof(ordered, env, on="local_datetime", direction="nearest", tolerance=pd.Timedelta("5min"))
    return ordered.sort_index()


def main():
    style()
    data = pd.read_csv(RESULTS / "hourly_lifecycle_states.csv")
    data = attach_environment(data)
    data["split"] = np.where(data["experiment"].eq("exp4"), "holdout", "development")
    data["stage"] = stage_of(data["hours_to_collapse"])
    dev = data[data["split"].eq("development")].copy()
    hold = data[data["split"].eq("holdout")].copy()

    center = dev[ZCOLS].median().to_numpy()
    pooled_abs = np.abs(dev[ZCOLS].to_numpy() - center)
    shared_scale = float(np.quantile(pooled_abs, 0.95))
    for index, (zcol, wcol, acol) in enumerate(zip(ZCOLS, WCOLS, ACOLS)):
        data[wcol] = (data[zcol] - center[index]) / shared_scale
        data[acol] = np.clip(1.0 + 0.9 * data[wcol], 0.0, 2.0)
    dev = data[data["split"].eq("development")].copy()
    hold = data[data["split"].eq("holdout")].copy()

    terminal = dev[(dev["hours_to_collapse"] > 0) & (dev["hours_to_collapse"] <= 6)].copy()
    baseline = dev[(dev["hours_to_collapse"] > 24) & (dev["hours_to_collapse"] <= 30)].copy()
    terminal_center = terminal[WCOLS].median().to_numpy()
    terminal_cov = np.cov(terminal[WCOLS].to_numpy(), rowvar=False)
    eigenvalues = np.linalg.eigvalsh(terminal_cov)[::-1]
    radial_terminal = np.linalg.norm(terminal[WCOLS].to_numpy() - terminal_center, axis=1)
    terminal_radius90 = float(np.quantile(radial_terminal, 0.90))

    distance_columns = {}
    for i, wcol in enumerate(WCOLS):
        name = f"d_{i+1}"
        data[name] = np.abs(data[wcol] - terminal_center[i])
        distance_columns[name] = SHORT[i]
    pairs = [(0, 1), (0, 2), (1, 2)]
    for i, j in pairs:
        name = f"d_{i+1}{j+1}"
        data[name] = np.sqrt((data[WCOLS[i]] - terminal_center[i]) ** 2 + (data[WCOLS[j]] - terminal_center[j]) ** 2)
        distance_columns[name] = f"{SHORT[i]} + {SHORT[j]}"
    data["d_123"] = np.sqrt(sum((data[WCOLS[i]] - terminal_center[i]) ** 2 for i in range(3)))
    distance_columns["d_123"] = "all three cuts"
    dev = data[data["split"].eq("development")].copy()
    hold = data[data["split"].eq("holdout")].copy()

    positive = hold[(hold["hours_to_collapse"] > 0) & (hold["hours_to_collapse"] <= 6)].copy()
    controls = hold[["source_file", "hour_index", *distance_columns]].copy()
    controls["hour_index"] = controls["hour_index"] + 24
    paired = positive.merge(controls, on=["source_file", "hour_index"], suffixes=("_terminal", "_control"))
    metric_rows = []
    for column, label in distance_columns.items():
        labels = np.r_[np.ones(len(paired)), np.zeros(len(paired))]
        scores = -np.r_[paired[f"{column}_terminal"], paired[f"{column}_control"]]
        metric_rows.append(
            {
                "metric": column,
                "label": label,
                "auc": auc(labels, scores),
                "paired_win_rate": float((paired[f"{column}_terminal"] < paired[f"{column}_control"]).mean()),
                "median_control_minus_terminal": float(
                    (paired[f"{column}_control"] - paired[f"{column}_terminal"]).median()
                ),
                "pairs": int(len(paired)),
            }
        )
    metrics = pd.DataFrame(metric_rows)

    correlations = []
    for source_file, group in hold[(hold["hours_to_collapse"] > 0) & (hold["hours_to_collapse"] <= 24)].groupby("source_file"):
        correlations.append(
            {
                "source_file": source_file,
                "spearman_final24": group["hours_to_collapse"].rank().corr(group["d_123"].rank()),
            }
        )
    correlations = pd.DataFrame(correlations)

    rng = np.random.default_rng(448)
    shuffled = []
    grouped_hold = {name: group.sort_values("hour_index") for name, group in hold.groupby("source_file")}
    for repeat in range(2000):
        wins = []
        for group in grouped_hold.values():
            values = group["d_123"].to_numpy()
            if len(values) < 30:
                continue
            endpoint = int(rng.integers(29, len(values)))
            terminal_values = values[endpoint - 5 : endpoint + 1]
            control_values = values[endpoint - 29 : endpoint - 23]
            wins.extend(terminal_values < control_values)
        shuffled.append(float(np.mean(wins)))
    actual_win = float(metrics.loc[metrics.metric.eq("d_123"), "paired_win_rate"].iloc[0])
    shuffle_p = float((1 + np.sum(np.asarray(shuffled) >= actual_win)) / (len(shuffled) + 1))

    best_other_auc = float(metrics.loc[~metrics.metric.eq("d_123"), "auc"].max())
    auc3 = float(metrics.loc[metrics.metric.eq("d_123"), "auc"].iloc[0])
    median_spearman = float(correlations["spearman_final24"].median())
    gates = {
        "A_paired_win_at_least_0_65": actual_win >= 0.65,
        "B_three_cut_auc_margin_at_least_0_02": auc3 >= best_other_auc + 0.02,
        "C_exceeds_95pct_shift_null": actual_win > float(np.quantile(shuffled, 0.95)),
        "supporting_median_spearman_at_least_0_25": median_spearman >= 0.25,
    }

    # Frozen threshold crossing is descriptive; it does not alter the gates above.
    data["inside_terminal90"] = data["d_123"] <= terminal_radius90
    hold["inside_terminal90"] = hold["d_123"] <= terminal_radius90
    lead_rows = []
    for source_file, group in hold.groupby("source_file"):
        group = group.sort_values("hour_index")
        inside = group["inside_terminal90"].to_numpy(dtype=bool)
        run3 = np.convolve(inside.astype(int), np.ones(3, dtype=int), mode="valid") >= 3
        candidates = np.where(run3)[0]
        terminal_candidates = [idx for idx in candidates if group.iloc[idx + 2]["hours_to_collapse"] <= 48]
        lead = float(group.iloc[terminal_candidates[0] + 2]["hours_to_collapse"]) if terminal_candidates else math.nan
        false_early = int(any(group.iloc[idx + 2]["hours_to_collapse"] > 48 for idx in candidates))
        lead_rows.append({"source_file": source_file, "lead_hours": lead, "false_early_alert": false_early})
    leads = pd.DataFrame(lead_rows)

    # Geometry summaries by stage and projection.
    geometry_rows = []
    for stage, group in dev.dropna(subset=["stage"]).groupby("stage", observed=True):
        for i, j in pairs:
            cov = np.cov(group[[WCOLS[i], WCOLS[j]]].to_numpy(), rowvar=False)
            vals = np.linalg.eigvalsh(cov)[::-1]
            geometry_rows.append(
                {
                    "stage": str(stage),
                    "projection": f"{i+1}{j+1}",
                    "center_x": group[ACOLS[i]].median(),
                    "center_y": group[ACOLS[j]].median(),
                    "major_variance": vals[0],
                    "minor_variance": vals[1],
                    "anisotropy": float(math.sqrt(max(vals[0], 1e-12) / max(vals[1], 1e-12))),
                }
            )
    geometry = pd.DataFrame(geometry_rows)

    # Persist reusable tables before plotting.
    data.to_csv(RESULTS / "T448_hourly_states_with_geometry.csv", index=False)
    paired.to_csv(RESULTS / "T448_holdout_24h_pairs.csv", index=False)
    metrics.to_csv(RESULTS / "T448_holdout_metrics.csv", index=False)
    correlations.to_csv(RESULTS / "T448_individual_final24_correlations.csv", index=False)
    leads.to_csv(RESULTS / "T448_individual_terminal_leads.csv", index=False)
    geometry.to_csv(RESULTS / "T448_projection_geometry.csv", index=False)

    # 01 — scope and raw behavior.
    fig, axes = plt.subplots(2, 2, figsize=(15, 10), constrained_layout=True)
    for experiment, group in data.groupby("experiment"):
        lifespans = group.groupby("source_file")["collapse_hour"].first()
        axes[0, 0].hist(lifespans, bins=np.arange(30, 195, 15), alpha=0.55, label=experiment)
    axes[0, 0].set(title="Individual collapse times", xlabel="author-index collapse hour", ylabel="flies")
    axes[0, 0].legend()
    coverage = data.groupby(["split", "source_file"])["hour_index"].count().reset_index(name="hours").sort_values("hours")
    for split, group in coverage.groupby("split"):
        axes[0, 1].scatter(np.arange(len(group)), group["hours"], s=28, label=split)
    axes[0, 1].set(title="Complete pre-collapse hours per fly", xlabel="flies sorted within split", ylabel="hours")
    axes[0, 1].legend()
    summary = binned_summary(data, "hours_to_collapse", ["traversal_share", "grooming_share", "proboscis_share", "idle_share"], 0, 72, 3)
    for column, label, color in [
        ("traversal_share", "traversal", "#5ea0ff"),
        ("grooming_share", "grooming", "#55d17a"),
        ("proboscis_share", "proboscis", "#f6c85f"),
        ("idle_share", "idle", "#df6c6c"),
    ]:
        axes[1, 0].plot(summary.bin_center, summary[f"{column}_median"], lw=2, label=label, color=color)
        axes[1, 0].fill_between(summary.bin_center, summary[f"{column}_q25"], summary[f"{column}_q75"], alpha=0.12, color=color)
    axes[1, 0].invert_xaxis()
    axes[1, 0].set(title="Raw behaviour approaching collapse", xlabel="hours remaining", ylabel="share of resolved behaviour")
    axes[1, 0].legend(ncol=2)
    axes[1, 1].boxplot(
        [data.excluded_unstereotyped_share, data.excluded_edge_share],
        tick_labels=["unstereotyped", "on edge"],
        patch_artist=True,
        boxprops={"facecolor": "#52657a"},
        medianprops={"color": "#f6c85f", "lw": 2},
    )
    axes[1, 1].set(title="Excluded observation share (QA, not lifecycle coordinates)", ylabel="fraction of frames")
    for ax in axes.flat:
        ax.grid(alpha=0.25)
    fig.suptitle("T448 — source scope before ARA geometry", fontsize=18, fontweight="bold")
    fig.savefig(RESULTS / "T448_01_data_scope_and_behaviors.png", dpi=170)
    plt.close(fig)

    # 02 — three projections.
    fig, axes = plt.subplots(1, 3, figsize=(19, 6.4), constrained_layout=True)
    for ax, (i, j) in zip(axes, pairs):
        for stage in ["early >72 h", "middle 24–72 h", "late 6–24 h", "terminal 0–6 h"]:
            group = dev[dev.stage.astype(str).eq(stage)]
            sample = group.sample(min(600, len(group)), random_state=448)
            ax.scatter(sample[ACOLS[i]], sample[ACOLS[j]], s=8, alpha=0.18, color=COLORS[stage], label=stage)
            ellipse_from_points(ax, group[[ACOLS[i], ACOLS[j]]], COLORS[stage], level=1.5, lw=1.8)
        hold_terminal = hold[(hold.hours_to_collapse > 0) & (hold.hours_to_collapse <= 6)]
        ax.scatter(hold_terminal[ACOLS[i]], hold_terminal[ACOLS[j]], marker="x", s=28, color="#ffffff", alpha=0.75, label="holdout terminal")
        ax.axvline(1, color="#d6d9df", lw=1, ls=":")
        ax.axhline(1, color="#d6d9df", lw=1, ls=":")
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_aspect("equal")
        ax.set_xlabel(f"Cut {i+1}: {SHORT[i]} (ARA 0–2)")
        ax.set_ylabel(f"Cut {j+1}: {SHORT[j]} (ARA 0–2)")
        ax.set_title(f"Projection {i+1}{j+1}")
        ax.grid(alpha=0.22)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=5)
    fig.suptitle("T448 — three independent tomographic disks; ellipses are measured, not forced circles", fontsize=17)
    fig.savefig(RESULTS / "T448_02_three_tomographic_disks.png", dpi=180)
    plt.close(fig)

    # 03 — combined 3D lifecycle shadow.
    fig = plt.figure(figsize=(15, 7), constrained_layout=True)
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    sample = data.sample(min(2600, len(data)), random_state=448)
    colors = np.clip(sample.hours_to_collapse, 0, 72)
    scatter = ax.scatter(sample[ACOLS[0]], sample[ACOLS[1]], sample[ACOLS[2]], c=colors, cmap="viridis_r", s=7, alpha=0.45)
    ax.scatter(*[terminal[col].median() for col in ACOLS], color="#ff5b5b", marker="*", s=180, label="development terminal median")
    ax.set(xlabel="Cut 1", ylabel="Cut 2", zlabel="Cut 3", xlim=(0, 2), ylim=(0, 2), zlim=(0, 2))
    ax.set_title("Visible three-coordinate lifecycle shadow")
    ax.legend()
    fig.colorbar(scatter, ax=ax, shrink=0.65, label="hours to collapse (clipped at 72)")
    ax2 = fig.add_subplot(1, 2, 2)
    vals = eigenvalues / eigenvalues.sum()
    ax2.bar(["largest", "middle", "smallest"], vals, color=["#5ea0ff", "#55d17a", "#f6c85f"])
    ax2.set_ylim(0, 1)
    ax2.set_ylabel("share of terminal-region variance")
    ax2.set_title("Terminal geometry is measured as an ellipsoid")
    ax2.text(0.04, 0.94, f"axis SD ratio = {math.sqrt(eigenvalues[0]/eigenvalues[-1]):.2f}:1\n90% terminal radius = {terminal_radius90:.3f}", transform=ax2.transAxes, va="top")
    ax2.grid(axis="y", alpha=0.25)
    fig.suptitle("T448 — combined shadow and its distortion", fontsize=18)
    fig.savefig(RESULTS / "T448_03_combined_lifecycle_shadow.png", dpi=180)
    plt.close(fig)

    # 04 — aligned histories.
    summary = binned_summary(hold, "hours_to_collapse", [*ACOLS, "d_123"], 0, 72, 2)
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True, constrained_layout=True)
    for column, label, color in zip(ACOLS, SHORT, ["#5ea0ff", "#55d17a", "#f6c85f"]):
        axes[0].plot(summary.bin_center, summary[f"{column}_median"], lw=2.4, label=label, color=color)
        axes[0].fill_between(summary.bin_center, summary[f"{column}_q25"], summary[f"{column}_q75"], color=color, alpha=0.13)
    axes[0].axhline(1, color="white", ls=":", lw=1)
    axes[0].set_ylabel("ARA coordinate (0–2)")
    axes[0].set_title("Untouched holdout: three independent histories")
    axes[0].legend(ncol=3)
    axes[1].plot(summary.bin_center, summary["d_123_median"], color="#d18cf0", lw=2.6, label="three-cut terminal distance")
    axes[1].fill_between(summary.bin_center, summary["d_123_q25"], summary["d_123_q75"], color="#d18cf0", alpha=0.18)
    axes[1].axvspan(0, 6, color="#ff5b5b", alpha=0.12, label="frozen terminal window")
    axes[1].axhline(terminal_radius90, color="#ffba52", ls="--", label="development terminal 90% radius")
    axes[1].set(xlabel="hours remaining to author-index collapse", ylabel="distance (shared robust units)")
    axes[1].set_title("Does the combined state approach the frozen terminal region?")
    axes[1].legend()
    for ax in axes:
        ax.invert_xaxis()
        ax.grid(alpha=0.25)
    fig.suptitle("T448 — population-to-individual temporal handover", fontsize=18)
    fig.savefig(RESULTS / "T448_04_aligned_handover_histories.png", dpi=180)
    plt.close(fig)

    # 05 — all individual holdout distance histories.
    fig, axes = plt.subplots(4, 4, figsize=(18, 14), sharex=True, sharey=True, constrained_layout=True)
    for ax, (source_file, group) in zip(axes.flat, hold.groupby("source_file")):
        group = group.sort_values("hours_to_collapse")
        ax.plot(group.hours_to_collapse, group.d_123, color="#71b7ff", lw=1.15)
        ax.axhline(terminal_radius90, color="#ffba52", ls="--", lw=0.9)
        ax.axvspan(0, 6, color="#ff5b5b", alpha=0.12)
        ax.set_title(source_file.replace(".h5", ""), fontsize=9)
        ax.invert_xaxis()
        ax.grid(alpha=0.18)
    fig.supxlabel("hours remaining to collapse")
    fig.supylabel("three-cut terminal distance")
    fig.suptitle("T448 — every untouched experiment-4 individual, followed toward collapse", fontsize=18)
    fig.savefig(RESULTS / "T448_05_all_holdout_individuals.png", dpi=170)
    plt.close(fig)

    # 06 — prediction and controls.
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), constrained_layout=True)
    order = metrics.sort_values("auc")
    axes[0, 0].barh(order.label, order.auc, color=["#d18cf0" if metric == "d_123" else "#5ea0ff" for metric in order.metric])
    axes[0, 0].axvline(0.5, color="white", ls=":")
    axes[0, 0].set(xlim=(0, 1), xlabel="AUROC", title="Final 6 h vs exact 24 h-earlier control")
    axes[0, 1].barh(order.label, order.paired_win_rate, color=["#d18cf0" if metric == "d_123" else "#55d17a" for metric in order.metric])
    axes[0, 1].axvline(0.65, color="#ffba52", ls="--", label="frozen Gate A")
    axes[0, 1].set(xlim=(0, 1), xlabel="paired win rate", title="Same fly, same circadian phase")
    axes[0, 1].legend()
    axes[1, 0].hist(shuffled, bins=35, color="#52657a", alpha=0.9)
    axes[1, 0].axvline(np.quantile(shuffled, 0.95), color="#ffba52", ls="--", label="95% shift null")
    axes[1, 0].axvline(actual_win, color="#ff5b5b", lw=2.5, label=f"actual = {actual_win:.3f}")
    axes[1, 0].set(title="Within-fly circular endpoint shifts", xlabel="three-cut paired win rate", ylabel="shuffles")
    axes[1, 0].legend()
    axes[1, 1].hist(correlations.spearman_final24.dropna(), bins=np.linspace(-1, 1, 17), color="#54a24b", alpha=0.9)
    axes[1, 1].axvline(0.25, color="#ffba52", ls="--", label="supporting gate")
    axes[1, 1].axvline(median_spearman, color="#ff5b5b", lw=2.5, label=f"median = {median_spearman:.3f}")
    axes[1, 1].set(title="Individual final-24 h approach slopes", xlabel="Spearman(hours remaining, distance)", ylabel="flies")
    axes[1, 1].legend()
    for ax in axes.flat:
        ax.grid(alpha=0.22)
    fig.suptitle("T448 — frozen gates, predictive ordering and null controls", fontsize=18)
    fig.savefig(RESULTS / "T448_06_prediction_and_controls.png", dpi=180)
    plt.close(fig)

    # 07 — environment and observation-quality distortions.
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), constrained_layout=True)
    zt = binned_summary(hold, "zt_hour", ["d_123"], 0, 24, 1)
    axes[0, 0].plot(zt.bin_center, zt.d_123_median, color="#5ea0ff", lw=2)
    axes[0, 0].fill_between(zt.bin_center, zt.d_123_q25, zt.d_123_q75, color="#5ea0ff", alpha=0.18)
    axes[0, 0].axvspan(0, 12, color="#ffd75e", alpha=0.08, label="lights on")
    axes[0, 0].set(title="Terminal distance by Zeitgeber hour", xlabel="ZT hour (0 = lights on)", ylabel="distance")
    axes[0, 0].legend()
    axes[0, 1].scatter(data["TEMPERATURE"], data.d_123, s=6, alpha=0.13, color="#f58518")
    axes[0, 1].set(title="Temperature distortion check", xlabel="temperature (°C)", ylabel="terminal distance")
    axes[1, 0].scatter(data.excluded_edge_share, data.d_123, s=6, alpha=0.13, color="#54a24b")
    axes[1, 0].set(title="Wall/edge classification check", xlabel="excluded edge share", ylabel="terminal distance")
    axes[1, 1].scatter(data.excluded_unstereotyped_share, data.d_123, s=6, alpha=0.13, color="#b279a2")
    axes[1, 1].set(title="Unstereotyped behaviour check", xlabel="excluded share", ylabel="terminal distance")
    for ax in axes.flat:
        ax.grid(alpha=0.22)
    fig.suptitle("T448 — external and measurement distortions kept outside the lifecycle coordinates", fontsize=17)
    fig.savefig(RESULTS / "T448_07_distortion_controls.png", dpi=180)
    plt.close(fig)

    # 08 — distortion across projections and stages.
    fig, axes = plt.subplots(1, 2, figsize=(16, 6.5), constrained_layout=True)
    for projection, group in geometry.groupby("projection"):
        group = group.set_index("stage").reindex(["early >72 h", "middle 24–72 h", "late 6–24 h", "terminal 0–6 h"])
        axes[0].plot(group.index, group.anisotropy, marker="o", lw=2, label=f"projection {projection}")
    axes[0].set(title="Ellipse anisotropy changes by lifecycle stage", ylabel="major/minor standard-deviation ratio")
    axes[0].tick_params(axis="x", rotation=25)
    axes[0].legend()
    radial_by_stage = []
    for stage, group in dev.groupby("stage", observed=True):
        values = np.linalg.norm(group[WCOLS].to_numpy() - terminal_center, axis=1)
        radial_by_stage.append((str(stage), values))
    axes[1].boxplot([values for _, values in radial_by_stage], tick_labels=[name for name, _ in radial_by_stage], patch_artist=True, boxprops={"facecolor": "#52657a"}, medianprops={"color": "#ffba52", "lw": 2})
    axes[1].axhline(terminal_radius90, color="#ff5b5b", ls="--", label="terminal 90% radius")
    axes[1].set(title="Distance to the development terminal center", ylabel="three-cut distance")
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].legend()
    for ax in axes:
        ax.grid(alpha=0.22)
    fig.suptitle("T448 — the sphere question is tested through changing projected distortion", fontsize=17)
    fig.savefig(RESULTS / "T448_08_projection_distortion.png", dpi=180)
    plt.close(fig)

    # 09 — selected full individual coordinate histories, shortest through longest.
    lifespans = hold.groupby("source_file")["collapse_hour"].first().sort_values()
    picks = [lifespans.index[0], lifespans.index[len(lifespans)//3], lifespans.index[2*len(lifespans)//3], lifespans.index[-1]]
    fig, axes = plt.subplots(4, 1, figsize=(15, 13), constrained_layout=True)
    for ax, source_file in zip(axes, picks):
        group = hold[hold.source_file.eq(source_file)].sort_values("hour_midpoint")
        for column, label, color in zip(ACOLS, SHORT, ["#5ea0ff", "#55d17a", "#f6c85f"]):
            ax.plot(group.hour_midpoint, group[column], lw=1.25, label=label, color=color, alpha=0.9)
        ax.axhline(1, color="white", ls=":", lw=0.8)
        ax.axvspan(max(0, group.collapse_hour.iloc[0] - 6), group.collapse_hour.iloc[0], color="#ff5b5b", alpha=0.12)
        ax.set(title=f"{source_file} — collapse at {group.collapse_hour.iloc[0]:.0f} h", ylabel="ARA 0–2", ylim=(0, 2))
        ax.grid(alpha=0.2)
    axes[0].legend(ncol=3)
    axes[-1].set_xlabel("hours since recording began")
    fig.suptitle("T448 — four complete individual lifecycle histories (retrospective view)", fontsize=18)
    fig.savefig(RESULTS / "T448_09_selected_individual_lifecycles.png", dpi=180)
    plt.close(fig)

    qa = {
        "rows": int(len(data)),
        "flies": int(data.source_file.nunique()),
        "development_flies": int(dev.source_file.nunique()),
        "holdout_flies": int(hold.source_file.nunique()),
        "core_missing_cells": int(
            data[["source_file", "hour_index", "hours_to_collapse", *ZCOLS, *WCOLS, *ACOLS]].isna().sum().sum()
        ),
        "environment_missing_rows": int(data[["TEMPERATURE", "RELATIVE-HUMIDITY"]].isna().any(axis=1).sum()),
        "environment_match_rate": float(data[["TEMPERATURE", "RELATIVE-HUMIDITY"]].notna().all(axis=1).mean()),
        "max_composition_sum_error": float(
            np.abs(data[["traversal_share", "grooming_share", "proboscis_share", "idle_share"]].sum(axis=1) - 1).max()
        ),
        "median_unstereotyped_share": float(data.excluded_unstereotyped_share.median()),
        "p95_unstereotyped_share": float(data.excluded_unstereotyped_share.quantile(0.95)),
        "median_edge_share": float(data.excluded_edge_share.median()),
        "p95_edge_share": float(data.excluded_edge_share.quantile(0.95)),
    }
    result = {
        "test": "T448 individual fruit-fly lifecycle tomography",
        "data_quality": qa,
        "development_center_logratio": dict(zip(ZCOLS, center.tolist())),
        "shared_robust_scale": shared_scale,
        "terminal_center_standardized": dict(zip(WCOLS, terminal_center.tolist())),
        "terminal_covariance_eigenvalues": eigenvalues.tolist(),
        "terminal_axis_sd_ratio": float(math.sqrt(eigenvalues[0] / eigenvalues[-1])),
        "terminal_radius90": terminal_radius90,
        "metrics": metrics.to_dict(orient="records"),
        "actual_three_cut_paired_win": actual_win,
        "shuffle_95pct": float(np.quantile(shuffled, 0.95)),
        "shuffle_p_value": shuffle_p,
        "median_final24_spearman": median_spearman,
        "gates": gates,
        "lead_summary": {
            "flies_with_3h_entry_in_final48": int(leads.lead_hours.notna().sum()),
            "median_lead_hours": float(leads.lead_hours.median()) if leads.lead_hours.notna().any() else None,
            "flies_with_early_false_alert": int(leads.false_early_alert.sum()),
        },
    }
    (RESULTS / "T448_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (RESULTS / "T448_DATA_QUALITY.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
