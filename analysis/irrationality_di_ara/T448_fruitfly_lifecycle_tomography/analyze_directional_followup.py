"""T448B frozen directional lifecycle diagnostic."""

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


ROOT = Path(r"F:\SystemFormulaFolder\GIT\ARA-GIT\analysis\irrationality_di_ara\T448_fruitfly_lifecycle_tomography")
RESULTS = ROOT / "results"
WCOLS = ["w_traversal_maintenance", "w_action_intake", "w_participation_quiescence"]
LABELS = ["T↔G", "Action↔Intake", "Participation↔Idle"]


def auc(labels, scores):
    labels = np.asarray(labels, dtype=int)
    ranks = pd.Series(np.asarray(scores)).rank(method="average").to_numpy()
    n1 = labels.sum()
    n0 = len(labels) - n1
    return float((ranks[labels == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def summary_bins(data, stop=72, step=3):
    cut = data[(data.hours_to_collapse > 0) & (data.hours_to_collapse <= stop)].copy()
    cut["bin"] = pd.cut(cut.hours_to_collapse, np.arange(0, stop + step, step))
    cut["mid"] = cut["bin"].map(lambda x: x.mid).astype(float)
    rows = []
    for midpoint, group in cut.groupby("mid", observed=True):
        row = {"mid": midpoint}
        for column in ["parallel_progress", "perpendicular_residual", "delta_magnitude", "alignment_cosine"]:
            row[f"{column}_median"] = group[column].median()
            row[f"{column}_q25"] = group[column].quantile(0.25)
            row[f"{column}_q75"] = group[column].quantile(0.75)
        rows.append(row)
    return pd.DataFrame(rows).sort_values("mid")


def main():
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
    data = pd.read_csv(RESULTS / "T448_hourly_states_with_geometry.csv")
    lag = data[["source_file", "hour_index", *WCOLS]].copy()
    lag["hour_index"] = lag["hour_index"] + 24
    lag = lag.rename(columns={column: f"lag24_{column}" for column in WCOLS})
    dynamic = data.merge(lag, on=["source_file", "hour_index"], how="inner")
    DCOLS = []
    for column in WCOLS:
        dcolumn = f"delta24_{column}"
        dynamic[dcolumn] = dynamic[column] - dynamic[f"lag24_{column}"]
        DCOLS.append(dcolumn)

    dev_terminal = dynamic[(dynamic.split.eq("development")) & (dynamic.hours_to_collapse > 0) & (dynamic.hours_to_collapse <= 6)]
    direction = dev_terminal[DCOLS].median().to_numpy()
    direction_norm = float(np.linalg.norm(direction))
    unit = direction / direction_norm
    deltas = dynamic[DCOLS].to_numpy()
    dynamic["parallel_progress"] = deltas @ unit
    dynamic["delta_magnitude"] = np.linalg.norm(deltas, axis=1)
    dynamic["perpendicular_residual"] = np.linalg.norm(deltas - np.outer(dynamic.parallel_progress, unit), axis=1)
    dynamic["alignment_cosine"] = np.divide(
        dynamic.parallel_progress,
        dynamic.delta_magnitude,
        out=np.zeros(len(dynamic), dtype=float),
        where=dynamic.delta_magnitude.to_numpy() > 1e-12,
    )
    hold = dynamic[dynamic.split.eq("holdout")].copy()
    terminal = hold[(hold.hours_to_collapse > 0) & (hold.hours_to_collapse <= 6)].copy()
    earlier = hold[(hold.hours_to_collapse > 12) & (hold.hours_to_collapse <= 72)].copy()

    labels = np.r_[np.ones(len(terminal)), np.zeros(len(earlier))]
    projection_auc = auc(labels, np.r_[terminal.parallel_progress, earlier.parallel_progress])
    single_aucs = []
    for index, column in enumerate(DCOLS):
        sign = 1 if direction[index] >= 0 else -1
        single_aucs.append(auc(labels, sign * np.r_[terminal[column], earlier[column]]))

    rng = np.random.default_rng(4482)
    grouped = {name: group.sort_values("hour_index") for name, group in hold.groupby("source_file")}
    shuffled = []
    for _ in range(2000):
        blocks = []
        for group in grouped.values():
            if len(group) < 6:
                continue
            endpoint = int(rng.integers(5, len(group)))
            blocks.extend(group.parallel_progress.iloc[endpoint - 5 : endpoint + 1])
        shuffled.append(float(np.mean(blocks)))
    actual_mean = float(terminal.parallel_progress.mean())
    shift95 = float(np.quantile(shuffled, 0.95))
    shift_p = float((1 + np.sum(np.asarray(shuffled) >= actual_mean)) / (len(shuffled) + 1))
    positive_fraction = float((terminal.alignment_cosine > 0).mean())
    median_cosine = float(terminal.alignment_cosine.median())
    gates = {
        "D_parallel_progress_exceeds_shift95": actual_mean > shift95,
        "E_positive_fraction_and_median_cosine": positive_fraction >= 0.65 and median_cosine >= 0.30,
        "F_projection_auc_margin_at_least_0_02": projection_auc >= max(single_aucs) + 0.02,
    }

    fly_vectors = terminal.groupby("source_file")[DCOLS].median()
    fly_vectors["parallel_progress"] = fly_vectors.to_numpy() @ unit
    fly_vectors["magnitude"] = np.linalg.norm(fly_vectors[DCOLS].to_numpy(), axis=1)
    fly_vectors["cosine"] = np.divide(fly_vectors.parallel_progress, fly_vectors.magnitude, out=np.zeros(len(fly_vectors)), where=fly_vectors.magnitude > 1e-12)

    dynamic.to_csv(RESULTS / "T448B_24h_directional_states.csv", index=False)
    fly_vectors.to_csv(RESULTS / "T448B_holdout_terminal_vectors.csv")

    summary = summary_bins(hold)
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), sharex=True, constrained_layout=True)
    settings = [
        ("parallel_progress", "parallel progress", "#5ea0ff"),
        ("perpendicular_residual", "perpendicular distortion", "#f58518"),
        ("delta_magnitude", "total 24 h displacement", "#54a24b"),
        ("alignment_cosine", "direction alignment cosine", "#d18cf0"),
    ]
    for ax, (column, title, color) in zip(axes.flat, settings):
        ax.plot(summary.mid, summary[f"{column}_median"], color=color, lw=2.5)
        ax.fill_between(summary.mid, summary[f"{column}_q25"], summary[f"{column}_q75"], color=color, alpha=0.18)
        ax.axvspan(0, 6, color="#ff5b5b", alpha=0.11)
        if column in {"parallel_progress", "alignment_cosine"}:
            ax.axhline(0, color="white", ls=":", lw=1)
        ax.set_title(title)
        ax.grid(alpha=0.22)
        ax.invert_xaxis()
    axes[1, 0].set_xlabel("hours remaining to collapse")
    axes[1, 1].set_xlabel("hours remaining to collapse")
    fig.suptitle("T448B — time-facing change relative to the same fly 24 hours earlier", fontsize=18)
    fig.savefig(RESULTS / "T448B_10_directional_histories.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), constrained_layout=True)
    sample = hold.sample(min(1800, len(hold)), random_state=4482)
    sc = axes[0].scatter(sample.parallel_progress, sample.perpendicular_residual, c=np.clip(sample.hours_to_collapse, 0, 72), cmap="viridis_r", s=10, alpha=0.45)
    axes[0].scatter(terminal.parallel_progress, terminal.perpendicular_residual, marker="x", s=32, color="white", alpha=0.75, label="real terminal hours")
    axes[0].axvline(0, color="white", ls=":")
    axes[0].set(title="Directional Di-ARA-style plane", xlabel="parallel progress", ylabel="perpendicular residual")
    axes[0].legend()
    fig.colorbar(sc, ax=axes[0], label="hours remaining (clipped at 72)")
    axes[1].hist(shuffled, bins=35, color="#52657a")
    axes[1].axvline(shift95, color="#ffba52", ls="--", label=f"shift 95% = {shift95:.3f}")
    axes[1].axvline(actual_mean, color="#ff5b5b", lw=2.5, label=f"real = {actual_mean:.3f}")
    axes[1].set(title="Frozen terminal direction vs shifted endpoints", xlabel="mean parallel progress", ylabel="shuffles")
    axes[1].legend()
    for ax in axes:
        ax.grid(alpha=0.22)
    fig.suptitle("T448B — shared direction and branch distortion", fontsize=18)
    fig.savefig(RESULTS / "T448B_11_direction_plane_and_null.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)
    pairs = [(0, 1), (0, 2), (1, 2)]
    for ax, (i, j) in zip(axes, pairs):
        ax.axhline(0, color="white", ls=":", lw=0.8)
        ax.axvline(0, color="white", ls=":", lw=0.8)
        for _, row in fly_vectors.iterrows():
            ax.arrow(0, 0, row[DCOLS[i]], row[DCOLS[j]], color="#71b7ff", alpha=0.5, width=0.002, head_width=0.035, length_includes_head=True)
        ax.arrow(0, 0, direction[i], direction[j], color="#ff5b5b", width=0.008, head_width=0.07, length_includes_head=True, label="development terminal direction")
        ax.set(xlabel=f"Δ24 {LABELS[i]}", ylabel=f"Δ24 {LABELS[j]}", title=f"projection {i+1}{j+1}")
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(alpha=0.2)
    axes[0].legend()
    fig.suptitle("T448B — each holdout fly's median terminal arrow", fontsize=18)
    fig.savefig(RESULTS / "T448B_12_individual_terminal_arrows.png", dpi=180)
    plt.close(fig)

    result = {
        "test": "T448B 24-hour directional handover",
        "development_direction": dict(zip(DCOLS, direction.tolist())),
        "direction_norm": direction_norm,
        "holdout_terminal_observations": int(len(terminal)),
        "actual_mean_parallel_progress": actual_mean,
        "shift_95pct": shift95,
        "shift_p_value": shift_p,
        "positive_alignment_fraction": positive_fraction,
        "median_alignment_cosine": median_cosine,
        "projection_auc": projection_auc,
        "single_axis_signed_aucs": dict(zip(LABELS, single_aucs)),
        "gates": gates,
    }
    (RESULTS / "T448B_RESULT.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
