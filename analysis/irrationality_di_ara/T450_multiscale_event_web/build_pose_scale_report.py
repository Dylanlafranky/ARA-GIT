"""Create the visual T450A technical report from frozen development and holdout results."""

from __future__ import annotations

import base64
import html
import json
import math
import os
import sys
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / "cache" / "matplotlib"))
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FIGURES = RESULTS / "figures"
sys.path.insert(0, str(HERE))
from analyze_pose_scales import FEATURE_META, FEATURE_ORDER, SCALES, load_split  # noqa: E402


BG = "#0b1220"
PANEL = "#111c2f"
GRID = "#34445e"
TEXT = "#e7edf7"
MUTED = "#9db0ca"
BLUE = "#58a6ff"
ORANGE = "#ff9f43"
GREEN = "#3ddc97"
PURPLE = "#b78cff"
PINK = "#ff6fae"
YELLOW = "#ffd166"
FRACTION_COLOURS = {0.125: BLUE, 0.375: GREEN, 0.625: ORANGE, 0.875: PINK}
FEATURE_LABELS = {
    "traversal_speed": "Whole-body traversal speed",
    "rotation_speed": "Body-axis rotation speed",
    "core_bend": "Core bend",
    "core_span": "Core span",
    "articulation_speed": "Internal articulation speed",
    "lr_articulation_balance": "Left/right articulation balance",
}
DESCRIPTOR_LABELS = {
    "persistence": "Adjacent-block persistence (Spearman ρ)",
    "retained_dispersion": "Retained dispersion (block MAD / raw MAD)",
    "abs_reversal_asymmetry": "Absolute time-reversal asymmetry",
}


def theme() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": PANEL,
            "axes.edgecolor": MUTED,
            "axes.labelcolor": TEXT,
            "axes.titlecolor": TEXT,
            "xtick.color": TEXT,
            "ytick.color": TEXT,
            "text.color": TEXT,
            "grid.color": GRID,
            "grid.alpha": 0.55,
            "font.size": 10,
            "axes.titleweight": "bold",
            "legend.facecolor": PANEL,
            "legend.edgecolor": GRID,
            "savefig.facecolor": BG,
        }
    )


def save(fig: plt.Figure, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return path


def load_tables() -> dict[str, object]:
    tables: dict[str, object] = {
        "config": json.loads((RESULTS / "T450A_FROZEN_CONFIG.json").read_text(encoding="utf-8")),
        "dev_result": json.loads((RESULTS / "T450A_DEVELOPMENT_RESULT.json").read_text(encoding="utf-8")),
        "hold_result": json.loads((RESULTS / "T450A_HOLDOUT_RESULT.json").read_text(encoding="utf-8")),
    }
    for name in (
        "development_quality",
        "development_scale_metrics",
        "development_fly_boundaries",
        "development_nominations",
        "development_ara_coordinates",
        "development_controls",
        "holdout_quality",
        "holdout_scale_metrics",
        "holdout_fly_boundaries",
        "holdout_nominations",
        "holdout_ara_coordinates",
        "holdout_transfer",
    ):
        tables[name] = pd.read_csv(RESULTS / f"T450A_{name}.csv")
    return tables


def figure_address(tables: dict) -> Path:
    dev_q = tables["development_quality"]
    hold_q = tables["holdout_quality"]
    fig = plt.figure(figsize=(16, 9))
    grid = fig.add_gridspec(2, 2, height_ratios=[1.1, 1], wspace=0.22, hspace=0.33)
    ax = fig.add_subplot(grid[0, :])
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.15, 1.0, 1.4, 1.0, "Individual fly\nidentity", BLUE),
        (2.0, 1.0, 1.65, 1.0, "Recording-fraction\nparent", GREEN),
        (4.1, 1.0, 1.55, 1.0, "60-second\npose envelope", ORANGE),
        (6.1, 1.0, 1.65, 1.0, "Body-frame\nfeature children", PURPLE),
        (8.2, 1.0, 1.55, 1.0, "Empirical local\nrungs ≤10.24 s", PINK),
    ]
    for x, y, w, h, label, colour in boxes:
        patch = plt.Rectangle((x, y), w, h, facecolor=colour, alpha=0.18, edgecolor=colour, linewidth=2)
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=12, weight="bold")
    for left, right in zip(boxes[:-1], boxes[1:]):
        ax.annotate("", xy=(right[0], 1.5), xytext=(left[0] + left[2], 1.5), arrowprops={"arrowstyle": "->", "color": TEXT, "lw": 2})
    ax.text(0.15, 2.55, "T450A relational address", fontsize=18, weight="bold")
    ax.text(0.15, 0.45, "Longer 10–60 s structure is intentionally unresolved here; T449 (10 min), T448 (1 h) and T448B (24 h) remain parent landmarks, not refit targets.", color=MUTED, fontsize=11)

    ax = fig.add_subplot(grid[1, 0])
    counts = [dev_q.source_file.nunique(), hold_q.source_file.nunique()]
    bars = ax.bar(["Development\nexperiments 1–3", "Untouched transfer\nexperiment 4"], counts, color=[BLUE, ORANGE], alpha=0.82)
    ax.bar_label(bars, labels=[f"{value} flies" for value in counts], padding=5, color=TEXT, fontsize=12)
    ax.set_ylim(0, max(counts) + 1.5)
    ax.set_ylabel("Independent flies")
    ax.set_title("Who: fly is the independent unit")
    ax.grid(axis="y")

    ax = fig.add_subplot(grid[1, 1])
    seconds = SCALES / 99.96
    ax.scatter(seconds, np.ones_like(seconds), s=np.linspace(45, 180, len(seconds)), c=np.arange(len(seconds)), cmap="viridis", edgecolor=TEXT, linewidth=0.6)
    for value, frames in zip(seconds, SCALES):
        ax.text(value, 1.07 if frames % 4 else 0.93, f"{value:.3g}s\n({frames}f)", ha="center", va="center", fontsize=8)
    ax.axvspan(seconds[-1], 60, color=ORANGE, alpha=0.10, label="unresolved inside this test")
    ax.set_xscale("log")
    ax.set_xlim(seconds[0] * 0.7, 75)
    ax.set_ylim(0.72, 1.28)
    ax.set_yticks([])
    ax.set_xlabel("Temporal scale (seconds, logarithmic)")
    ax.set_title("When: measured local ladder inside each 60-second parent")
    ax.legend(loc="lower right")
    fig.suptitle("T450A — what is measured, and where it sits", fontsize=22, weight="bold", y=0.99)
    return save(fig, "T450A_01_RELATIONAL_ADDRESS.png")


def figure_raw_example(dev_bursts: list[dict]) -> Path:
    burst = sorted(dev_bursts, key=lambda row: (row["source_file"], row["recording_fraction"]))[0]
    fps = burst["fps"]
    start, stop = 0, min(len(burst["behaviours"]), int(round(10 * fps)))
    time = np.arange(stop - start) / fps
    fig = plt.figure(figsize=(16, 13))
    grid = fig.add_gridspec(4, 2, hspace=0.38, wspace=0.24)
    ax = fig.add_subplot(grid[0:2, 0])
    thorax_x = -burst["body_x"][3, start:stop]  # thorax is identically zero in body frame; show global-equivalent motion through integrated speed inset.
    # Show body-frame skeletons because absolute camera coordinates are intentionally removed.
    indices = np.linspace(start, stop - 1, 18).round().astype(int)
    nodes = [0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    cmap = plt.get_cmap("viridis")
    for number, frame in enumerate(indices):
        colour = cmap(number / max(len(indices) - 1, 1))
        x, y = burst["body_x"][:, frame], burst["body_y"][:, frame]
        ax.plot(x[[4, 3, 0]], y[[4, 3, 0]], color=colour, alpha=0.75, lw=1.2)
        ax.scatter(x[nodes], y[nodes], color=colour, s=13, alpha=0.75)
    ax.axhline(0, color=GRID, lw=1)
    ax.axvline(0, color=GRID, lw=1)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("Body-axis x (body lengths; head is +x)")
    ax.set_ylabel("Perpendicular y (body lengths)")
    ax.set_title("Body-frame pose overlay — 18 moments across 10 seconds")
    ax.text(0.02, 0.02, "colour: early → late", transform=ax.transAxes, color=MUTED)
    ax.grid()

    axes = [fig.add_subplot(grid[row, col]) for row, col in [(0, 1), (1, 1), (2, 0), (2, 1), (3, 0), (3, 1)]]
    for ax, feature in zip(axes, FEATURE_ORDER):
        values = burst["signals"][feature][start:stop]
        ax.plot(time, values, color=BLUE if "speed" in feature else GREEN, lw=0.85)
        ax.set_title(FEATURE_LABELS[feature])
        ax.set_xlabel("Seconds from start of envelope")
        ax.set_ylabel(FEATURE_META[feature]["units"])
        ax.grid()
    fig.suptitle(f"Raw observed children before scale selection — {burst['source_file']}, 12.5% envelope", fontsize=20, weight="bold", y=0.995)
    return save(fig, "T450A_02_RAW_BODY_FRAME_CHILDREN.png")


def figure_scale_landscape(metrics: pd.DataFrame, name: str, title: str) -> Path:
    fig, axes = plt.subplots(len(FEATURE_ORDER), len(DESCRIPTOR_LABELS), figsize=(18, 22), sharex=True)
    for row, feature in enumerate(FEATURE_ORDER):
        for col, descriptor in enumerate(DESCRIPTOR_LABELS):
            ax = axes[row, col]
            part = metrics[metrics.feature == feature]
            for fraction, colour in FRACTION_COLOURS.items():
                frac = part[np.isclose(part.recording_fraction, fraction)]
                grouped = frac.groupby("scale_seconds")[descriptor]
                median = grouped.median()
                q1 = grouped.quantile(0.25)
                q3 = grouped.quantile(0.75)
                ax.plot(median.index, median.values, color=colour, marker="o", ms=3, lw=1.6, label=f"{fraction*100:.1f}%")
                ax.fill_between(median.index, q1.values, q3.values, color=colour, alpha=0.10)
            ax.set_xscale("log", base=2)
            ax.grid()
            if row == 0:
                ax.set_title(DESCRIPTOR_LABELS[descriptor])
            if col == 0:
                ax.set_ylabel(FEATURE_LABELS[feature])
            if row == len(FEATURE_ORDER) - 1:
                ax.set_xlabel("Block scale (seconds, log₂)")
    handles, labels = axes[0, -1].get_legend_handles_labels()
    fig.legend(handles, labels, title="Recording position", loc="upper center", ncol=4, bbox_to_anchor=(0.5, 0.985))
    fig.suptitle(title, fontsize=21, weight="bold", y=0.999)
    fig.text(0.5, 0.006, "Lines are medians across independent flies; shaded regions are the interquartile range. Raw units remain feature-specific.", ha="center", color=MUTED)
    return save(fig, name)


def figure_rung_support(tables: dict) -> Path:
    summary = tables["development_fly_boundaries"]
    nominations = tables["development_nominations"]
    config = tables["config"]
    sources = sorted(summary.source_file.unique())
    scales = SCALES[1:]
    support = np.zeros((len(FEATURE_ORDER), len(scales)))
    score = np.full_like(support, np.nan, dtype=float)
    for i, feature in enumerate(FEATURE_ORDER):
        part = nominations[nominations.feature == feature]
        for j, scale in enumerate(scales):
            support[i, j] = sum(
                any(abs(math.log2(value / scale)) <= 1 for value in group.boundary_scale_frames)
                for _, group in part.groupby("source_file")
            )
            local = summary[(summary.feature == feature) & (np.abs(np.log2(summary.boundary_scale_frames / scale)) <= 1)]
            score[i, j] = local.null_z_score.median()
    fig, axes = plt.subplots(1, 2, figsize=(18, 7), gridspec_kw={"width_ratios": [1.05, 1]})
    im = axes[0].imshow(support, aspect="auto", vmin=0, vmax=len(sources), cmap="viridis")
    for i in range(support.shape[0]):
        for j in range(support.shape[1]):
            axes[0].text(j, i, f"{int(support[i,j])}/6", ha="center", va="center", color="white" if support[i, j] < 4 else "black", fontsize=8)
    axes[0].set_xticks(range(len(scales)), [f"{scale/99.96:.3g}" for scale in scales], rotation=45, ha="right")
    axes[0].set_yticks(range(len(FEATURE_ORDER)), [FEATURE_LABELS[f] for f in FEATURE_ORDER])
    axes[0].set_xlabel("Boundary scale (seconds)")
    axes[0].set_title("Fly support within ±1 octave")
    fig.colorbar(im, ax=axes[0], label="Independent development flies")
    for rung in config["rungs"]:
        i = FEATURE_ORDER.index(rung["feature"])
        j = list(scales).index(rung["scale_frames"])
        axes[0].scatter(j, i, s=260, facecolors="none", edgecolors=PINK, linewidths=3)

    im = axes[1].imshow(score, aspect="auto", cmap="magma")
    axes[1].set_xticks(range(len(scales)), [f"{scale/99.96:.3g}" for scale in scales], rotation=45, ha="right")
    axes[1].set_yticks(range(len(FEATURE_ORDER)), [FEATURE_LABELS[f] for f in FEATURE_ORDER])
    axes[1].set_xlabel("Boundary scale (seconds)")
    axes[1].set_title("Median local null-standardised excess")
    fig.colorbar(im, ax=axes[1], label="Observed score above timestamp-null centre (MAD units)")
    fig.suptitle("Development-only rung discovery — circles are frozen before holdout", fontsize=20, weight="bold")
    return save(fig, "T450A_04_DEVELOPMENT_RUNG_SUPPORT.png")


def first_rung_by_feature(config: dict) -> dict[str, int]:
    result = {}
    for row in config["rungs"]:
        result.setdefault(row["feature"], int(row["scale_frames"]))
    return result


def figure_ara_planes(tables: dict) -> Path:
    dev = tables["development_ara_coordinates"]
    hold = tables["holdout_ara_coordinates"]
    config = tables["config"]
    rung = first_rung_by_feature(config)
    if len(rung) < 2:
        feature = next(iter(rung)) if rung else None
        fig, axes = plt.subplots(2, 3, figsize=(18, 11))
        if feature is None:
            for ax in axes.flat:
                ax.text(0.5, 0.5, "No supported development rung", ha="center", va="center", transform=ax.transAxes)
                ax.set_axis_off()
            fig.suptitle("No ARA amount plane was frozen", fontsize=20, weight="bold")
            return save(fig, "T450A_05_ARA_AMOUNT_PLANES.png")
        scale = rung[feature]
        all_ara = pd.concat([dev, hold], ignore_index=True)
        selected = all_ara[(all_ara.feature == feature) & (all_ara.scale_frames == scale)].copy()
        for role, colour, marker in [("development", BLUE, "o"), ("holdout", ORANGE, "^")]:
            part = selected[selected.split == role]
            axes[0, 0].scatter(100 * part.recording_fraction, part.ARA_coordinate, color=colour, marker=marker, s=60, alpha=0.75, label=role)
        axes[0, 0].axhline(1, color=TEXT, ls="--")
        axes[0, 0].set_xlabel("Recording position (%)")
        axes[0, 0].set_ylabel(f"{FEATURE_LABELS[feature]} ARA amount (0–2)")
        axes[0, 0].set_title("Frozen amount coordinate across the lifecycle-position parent")
        axes[0, 0].legend(); axes[0, 0].grid()

        combined_metrics = pd.concat([tables["development_scale_metrics"], tables["holdout_scale_metrics"]], ignore_index=True)
        exact = combined_metrics[(combined_metrics.feature == feature) & (combined_metrics.scale_frames == scale)]
        for role, colour in [("development", BLUE), ("holdout", ORANGE)]:
            part = exact[exact.split == role]
            med = part.groupby("recording_fraction").amount.median()
            axes[0, 1].plot(100 * med.index, med.values, color=colour, marker="o", lw=2, label=role)
        axes[0, 1].set_xlabel("Recording position (%)"); axes[0, 1].set_ylabel(FEATURE_META[feature]["units"])
        axes[0, 1].set_title("Raw amount at the frozen scale"); axes[0, 1].legend(); axes[0, 1].grid()

        for role, colour in [("development", BLUE), ("holdout", ORANGE)]:
            part = exact[exact.split == role]
            med = part.groupby("recording_fraction").persistence.median()
            axes[0, 2].plot(100 * med.index, med.values, color=colour, marker="o", lw=2, label=role)
        axes[0, 2].set_xlabel("Recording position (%)"); axes[0, 2].set_ylabel("Adjacent-block persistence (Spearman ρ)")
        axes[0, 2].set_title("Temporal character at the same scale"); axes[0, 2].legend(); axes[0, 2].grid()

        for source, group in selected.sort_values("recording_fraction").groupby("source_file"):
            colour = ORANGE if group.split.iloc[0] == "holdout" else BLUE
            axes[1, 0].plot(100 * group.recording_fraction, group.ARA_coordinate, color=colour, alpha=0.72, marker="o", ms=3)
        axes[1, 0].axhline(1, color=TEXT, ls="--")
        axes[1, 0].set_xlabel("Recording position (%)"); axes[1, 0].set_ylabel("ARA amount (0–2)")
        axes[1, 0].set_title("Every individual path; no population averaging"); axes[1, 0].grid()

        dev_boundary = tables["development_fly_boundaries"]
        diagnostic = dev_boundary.groupby("feature", as_index=False).null_z_score.max().sort_values("null_z_score")
        axes[1, 1].barh([FEATURE_LABELS[value] for value in diagnostic.feature], diagnostic.null_z_score, color=[GREEN if value == feature else MUTED for value in diagnostic.feature])
        axes[1, 1].axvline(0, color=TEXT, lw=0.8)
        axes[1, 1].set_xlabel("Strongest median fly null-standardised excess")
        axes[1, 1].set_title("Why only one feature retained a candidate rung")
        axes[1, 1].grid(axis="x")

        axes[1, 2].axis("off")
        axes[1, 2].text(0.04, 0.92, "ARA reading", fontsize=16, weight="bold", transform=axes[1, 2].transAxes)
        axes[1, 2].text(0.04, 0.78, f"Observed child: {FEATURE_LABELS[feature]}\nCandidate band centre: {scale/99.96:.3f} s\nAddress: simple one-coordinate rung\nNot established: its coupled pole or Di-ARA", fontsize=12, linespacing=1.7, va="top", transform=axes[1, 2].transAxes)
        axes[1, 2].text(0.04, 0.36, "Ridge 1 = development median.\nIndividual displacement around it is retained.\nThe band may be pose-control timing, tracking structure,\nor a child of a larger lifecycle relation.", color=MUTED, fontsize=11, linespacing=1.6, va="top", transform=axes[1, 2].transAxes)
        fig.suptitle(f"The only frozen ARA amount coordinate — {FEATURE_LABELS[feature]} at {scale/99.96:.3f} s", fontsize=19, weight="bold")
        return save(fig, "T450A_05_ARA_AMOUNT_PLANES.png")
    pairings = [
        ("traversal_speed", "articulation_speed"),
        ("rotation_speed", "lr_articulation_balance"),
        ("core_bend", "core_span"),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    for col, (x_feature, y_feature) in enumerate(pairings):
        ax = axes[0, col]
        if x_feature not in rung or y_feature not in rung:
            ax.text(0.5, 0.5, "No supported rung for one or both axes", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
            axes[1, col].set_axis_off()
            continue
        for split_frame, marker, label in [(dev, "o", "development"), (hold, "^", "holdout")]:
            x = split_frame[(split_frame.feature == x_feature) & (split_frame.scale_frames == rung[x_feature])]
            y = split_frame[(split_frame.feature == y_feature) & (split_frame.scale_frames == rung[y_feature])]
            merged = x[["source_file", "burst", "recording_fraction", "ARA_coordinate"]].merge(
                y[["source_file", "burst", "ARA_coordinate"]], on=["source_file", "burst"], suffixes=("_x", "_y")
            )
            ax.scatter(merged.ARA_coordinate_x, merged.ARA_coordinate_y, c=[FRACTION_COLOURS.get(v, TEXT) for v in merged.recording_fraction], marker=marker, s=55, alpha=0.78, edgecolor=BG, linewidth=0.5, label=label)
        ax.axhline(1, color=TEXT, ls="--", lw=0.9)
        ax.axvline(1, color=TEXT, ls="--", lw=0.9)
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_xlabel(f"{FEATURE_LABELS[x_feature]}\nARA amount at {rung[x_feature]/99.96:.3g}s")
        ax.set_ylabel(f"{FEATURE_LABELS[y_feature]}\nARA amount at {rung[y_feature]/99.96:.3g}s")
        ax.set_title("Same-envelope simple ARA cut")
        ax.grid()
        ax.legend(loc="best")

        ax = axes[1, col]
        x = pd.concat([dev, hold])
        x = x[(x.feature == x_feature) & (x.scale_frames == rung[x_feature])]
        y = pd.concat([dev, hold])
        y = y[(y.feature == y_feature) & (y.scale_frames == rung[y_feature])]
        merged = x[["source_file", "split", "recording_fraction", "ARA_coordinate"]].merge(
            y[["source_file", "split", "recording_fraction", "ARA_coordinate"]], on=["source_file", "split", "recording_fraction"], suffixes=("_x", "_y")
        ).sort_values(["source_file", "recording_fraction"])
        for source, group in merged.groupby("source_file"):
            colour = ORANGE if group.split.iloc[0] == "holdout" else BLUE
            ax.plot(group.ARA_coordinate_x, group.ARA_coordinate_y, color=colour, alpha=0.55, lw=1)
            ax.scatter(group.ARA_coordinate_x, group.ARA_coordinate_y, c=[FRACTION_COLOURS.get(v, TEXT) for v in group.recording_fraction], s=35, zorder=3)
        ax.axhline(1, color=TEXT, ls="--", lw=0.9)
        ax.axvline(1, color=TEXT, ls="--", lw=0.9)
        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.set_xlabel(FEATURE_LABELS[x_feature])
        ax.set_ylabel(FEATURE_LABELS[y_feature])
        ax.set_title("Individual recording-fraction paths")
        ax.grid()
    fig.suptitle("Frozen ARA displays — ridge 1 is the development relational centre, not a universal landmark", fontsize=19, weight="bold")
    return save(fig, "T450A_05_ARA_AMOUNT_PLANES.png")


def figure_controls(tables: dict) -> Path:
    controls = tables["development_controls"]
    fig, axes = plt.subplots(1, 2, figsize=(17, 7))
    summary = controls.groupby(["feature", "scale_frames"], as_index=False).agg(observed=("observed_score", "median"), null=("permuted_q95", "median"))
    x = np.arange(len(summary))
    width = 0.38
    axes[0].bar(x - width / 2, summary.observed, width, color=BLUE, label="observed median")
    axes[0].bar(x + width / 2, summary.null, width, color=ORANGE, label="median 95th-percentile timestamp null")
    axes[0].set_xticks(x, [f"{FEATURE_LABELS[row.feature]}\n{row.scale_frames/99.96:.3g}s" for row in summary.itertuples()], rotation=35, ha="right")
    axes[0].set_ylabel("Geometry-change score")
    axes[0].set_title("Chronology control at frozen rungs")
    axes[0].legend()
    axes[0].grid(axis="y")

    axes[1].scatter(controls.observed_reversal_asymmetry, controls.reversed_reversal_asymmetry, c=[FEATURE_ORDER.index(value) for value in controls.feature], cmap="viridis", alpha=0.65)
    limit = np.nanmax(np.abs(controls[["observed_reversal_asymmetry", "reversed_reversal_asymmetry"]].to_numpy()))
    limit = max(limit, 0.1)
    axes[1].plot([-limit, limit], [limit, -limit], color=GREEN, ls="--", label="ideal sign reversal")
    axes[1].axhline(0, color=TEXT, lw=0.7)
    axes[1].axvline(0, color=TEXT, lw=0.7)
    axes[1].set_xlim(-limit, limit)
    axes[1].set_ylim(-limit, limit)
    axes[1].set_xlabel("Observed signed asymmetry")
    axes[1].set_ylabel("Time-reversed signed asymmetry")
    axes[1].set_title("Phase control: reversal must change directional sign")
    axes[1].legend()
    axes[1].grid()
    fig.suptitle("Controls distinguish a temporal scale from unordered occupancy", fontsize=20, weight="bold")
    return save(fig, "T450A_06_CHRONOLOGY_AND_REVERSAL_CONTROLS.png")


def figure_transfer(tables: dict) -> Path:
    dev = tables["development_scale_metrics"]
    hold = tables["holdout_scale_metrics"]
    config = tables["config"]
    transfer = tables["holdout_transfer"]
    hold_nominations = tables["holdout_nominations"]
    holdout_sources = sorted(hold.source_file.unique())
    fig, axes = plt.subplots(len(FEATURE_ORDER), 2, figsize=(17, 22), sharex="col")
    for row, feature in enumerate(FEATURE_ORDER):
        ax = axes[row, 0]
        part = dev[dev.feature == feature]
        med = part.groupby("scale_seconds").persistence.median()
        q1 = part.groupby("scale_seconds").persistence.quantile(0.25)
        q3 = part.groupby("scale_seconds").persistence.quantile(0.75)
        ax.plot(med.index, med.values, color=BLUE, lw=2, label="development median")
        ax.fill_between(med.index, q1.values, q3.values, color=BLUE, alpha=0.18, label="development IQR")
        for source, group in hold[hold.feature == feature].groupby("source_file"):
            series = group.groupby("scale_seconds").persistence.median()
            ax.plot(series.index, series.values, marker="o", ms=3, lw=1.2, label=source.replace(".h5", ""))
        for rung in config["rungs"]:
            if rung["feature"] == feature:
                ax.axvline(rung["scale_seconds_at_99_96fps"], color=PINK, ls="--", lw=1.3)
        ax.set_xscale("log", base=2)
        ax.set_ylabel(FEATURE_LABELS[feature])
        ax.grid()
        if row == 0:
            ax.set_title("Persistence curve: development band vs both holdouts")
            ax.legend(fontsize=8)
        if row == len(FEATURE_ORDER) - 1:
            ax.set_xlabel("Block scale (seconds, log₂)")

        ax = axes[row, 1]
        feature_nominations = hold_nominations[hold_nominations.feature == feature]
        for source_index, source in enumerate(holdout_sources):
            points = feature_nominations[feature_nominations.source_file == source]
            colour = BLUE if source_index == 0 else ORANGE
            if len(points):
                ax.scatter(
                    points.boundary_scale_seconds,
                    np.full(len(points), source_index),
                    s=55 + 18 * np.maximum(points.null_z_score, 0),
                    color=colour,
                    alpha=0.82,
                    edgecolor=TEXT,
                    linewidth=0.5,
                    label=source.replace(".h5", "") if row == 0 else None,
                )
                for point in points.itertuples():
                    ax.text(point.boundary_scale_seconds, source_index + 0.12, f"{point.boundary_scale_seconds:.3g}s", ha="center", va="bottom", fontsize=7, color=colour)
        frozen = [r for r in config["rungs"] if r["feature"] == feature]
        for rung_item in frozen:
            ax.axvline(rung_item["scale_seconds_at_99_96fps"], color=PINK, ls="--", lw=2, label="frozen development rung" if row == 0 else None)
        ax.set_xscale("log", base=2)
        ax.set_xlim(SCALES[0] / 99.96 * 0.72, SCALES[-1] / 99.96 * 1.4)
        ax.set_ylim(-0.55, 1.55)
        ax.set_yticks([0, 1], [value.replace(".h5", "") for value in holdout_sources], fontsize=8)
        ax.set_xlabel("Above-null nominated scale (seconds, log₂)" if row == len(FEATURE_ORDER) - 1 else "")
        ax.grid(axis="x")
        if row == 0:
            ax.set_title("All above-null holdout nominations; dashed line = frozen development address")
            ax.legend(fontsize=8, loc="upper left")
    fig.suptitle("Untouched experiment-4 regime transfer — shape is shown even when a frozen qualification fails", fontsize=19, weight="bold")
    return save(fig, "T450A_07_UNTOUCHED_HOLDOUT_TRANSFER.png")


def figure_quality(tables: dict) -> Path:
    quality = pd.concat([tables["development_quality"], tables["holdout_quality"]], ignore_index=True)
    quality["role"] = np.where(quality.split == "development", "development", "untouched holdout")
    fig, axes = plt.subplots(2, 2, figsize=(17, 11))
    metrics = ["core_valid_fraction", "appendage_valid_fraction", "lr_valid_fraction"]
    colours = [BLUE, GREEN, ORANGE]
    x = np.arange(len(quality))
    for metric, colour in zip(metrics, colours):
        axes[0, 0].plot(x, 100 * quality[metric], marker="o", ms=3, lw=1, label=metric.replace("_", " "), color=colour)
    axes[0, 0].set_ylim(0, 102)
    axes[0, 0].set_ylabel("Finite feature frames (%)")
    axes[0, 0].set_xlabel("Each fly × recording-position envelope")
    axes[0, 0].set_title("Pose visibility; no long-gap interpolation")
    axes[0, 0].legend()
    axes[0, 0].grid()

    for role, colour in [("development", BLUE), ("untouched holdout", ORANGE)]:
        part = quality[quality.role == role]
        axes[0, 1].scatter(part.temperature_median, part.relative_humidity_median, c=colour, label=role, s=55, alpha=0.75)
    axes[0, 1].set_xlabel("Median temperature (°C)")
    axes[0, 1].set_ylabel("Median relative humidity (%)")
    axes[0, 1].set_title("The holdout is a real environmental regime transfer")
    axes[0, 1].legend()
    axes[0, 1].grid()

    grouped = quality.groupby(["recording_fraction", "role"])[["idle_fraction", "locomotion_fraction", "on_edge_fraction"]].median().reset_index()
    for role, style in [("development", "-"), ("untouched holdout", "--")]:
        part = grouped[grouped.role == role]
        for metric, colour in [("idle_fraction", PURPLE), ("locomotion_fraction", GREEN), ("on_edge_fraction", ORANGE)]:
            axes[1, 0].plot(100 * part.recording_fraction, 100 * part[metric], ls=style, marker="o", color=colour, label=f"{metric.replace('_fraction','')} — {role}")
    axes[1, 0].set_xlabel("Recording position (%)")
    axes[1, 0].set_ylabel("Median envelope occupancy (%)")
    axes[1, 0].set_title("Published behaviour and edge channels are annotations, not axes")
    axes[1, 0].legend(fontsize=8, ncol=2)
    axes[1, 0].grid()

    source_order = sorted(quality.source_file.unique())
    matrix = np.full((len(source_order), 4), np.nan)
    for i, source in enumerate(source_order):
        part = quality[quality.source_file == source].sort_values("recording_fraction")
        matrix[i, : len(part)] = 100 * part.lr_valid_fraction.to_numpy()
    im = axes[1, 1].imshow(matrix, aspect="auto", vmin=0, vmax=100, cmap="viridis")
    axes[1, 1].set_yticks(range(len(source_order)), [value.replace(".h5", "") for value in source_order], fontsize=8)
    axes[1, 1].set_xticks(range(4), ["12.5%", "37.5%", "62.5%", "87.5%"])
    axes[1, 1].set_xlabel("Recording position")
    axes[1, 1].set_title("Paired left/right visibility control")
    fig.colorbar(im, ax=axes[1, 1], label="Valid left/right frames (%)")
    fig.suptitle("Data quality and possible distortions remain visible beside the geometry", fontsize=20, weight="bold")
    return save(fig, "T450A_08_DATA_QUALITY_AND_ANNOTATIONS.png")


def image_data(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def table_html(frame: pd.DataFrame, columns: list[str], precision: int = 3) -> str:
    view = frame[columns].copy()
    for column in view.select_dtypes(include=[np.number]).columns:
        view[column] = view[column].map(lambda value: "" if pd.isna(value) else f"{value:.{precision}f}")
    return view.to_html(index=False, escape=True, classes="data-table")


def build_html(tables: dict, figures: list[tuple[Path, str, str]]) -> Path:
    config = tables["config"]
    dev_result = tables["dev_result"]
    hold_result = tables["hold_result"]
    controls = tables["development_controls"]
    transfer = tables["holdout_transfer"]
    quality = pd.concat([tables["development_quality"], tables["holdout_quality"]])
    observed_above = float((controls.observed_score > controls.permuted_q95).mean()) if len(controls) else math.nan
    reversal_opposes = float((np.sign(controls.observed_reversal_asymmetry) == -np.sign(controls.reversed_reversal_asymmetry)).mean()) if len(controls) else math.nan
    rung_count = len(config["rungs"])
    transferred = int(sum(row["both_flies_transfer"] for row in hold_result["rung_transfer"]))
    common = config["common_parent_candidates"]
    common_text = (
        "; ".join(f"{row['centre_scale_frames']/99.96:.3g}s across {row['feature_count']} features" for row in common)
        if common
        else "none met the three-feature rule"
    )
    rung_frame = pd.DataFrame(config["rungs"])
    if len(rung_frame):
        rung_frame["scale_seconds"] = rung_frame.scale_frames / 99.96
        rung_frame["feature_label"] = rung_frame.feature.map(FEATURE_LABELS)
    transfer_summary = pd.DataFrame(hold_result["rung_transfer"])
    title = "T450A pose-scale discovery: observed children before lifecycle inference"
    sections = []
    for index, (path, heading, explanation) in enumerate(figures, start=1):
        sections.append(
            f'<section id="figure-{index}" class="report-section"><h2>{html.escape(heading)}</h2><p>{html.escape(explanation)}</p><img src="{image_data(path)}" alt="{html.escape(heading)}"></section>'
        )
    rung_table = table_html(rung_frame, ["feature_label", "rung_label", "scale_frames", "scale_seconds", "support_flies", "support_fraction", "median_local_score"], 4) if len(rung_frame) else "<p>No feature met the frozen support rule.</p>"
    transfer_table = table_html(transfer_summary, list(transfer_summary.columns), 3) if len(transfer_summary) else "<p>No frozen rung was available for transfer.</p>"
    files = sorted(set(quality.source_file))
    sources_list = "".join(f"<li>{html.escape(value)}</li>" for value in files)
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root{{--bg:{BG};--panel:{PANEL};--text:{TEXT};--muted:{MUTED};--line:{GRID};--blue:{BLUE};--orange:{ORANGE};--green:{GREEN};}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,Segoe UI,sans-serif}} a{{color:#7cc4ff}} .wrap{{max-width:1500px;margin:auto;padding:28px}} header{{padding:30px;border:1px solid var(--line);border-radius:18px;background:linear-gradient(135deg,#14233c,#0e1727)}} h1{{font-size:2.25rem;line-height:1.12;margin:0 0 12px}} h2{{font-size:1.55rem;margin-top:0}} h3{{margin-bottom:.3rem}} p{{max-width:1100px}} .lede{{font-size:1.13rem;color:#d9e6f7}} .cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:13px;margin:22px 0}} .card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px}} .number{{font-size:1.75rem;font-weight:800;color:#fff}} .label{{color:var(--muted);font-size:.92rem}} .notice{{border-left:5px solid var(--orange);background:#211b19;padding:15px 18px;border-radius:8px;margin:18px 0}} .good{{border-left-color:var(--green);background:#12231f}} .report-section{{margin:28px 0;padding:22px;background:var(--panel);border:1px solid var(--line);border-radius:15px}} img{{display:block;width:100%;height:auto;border-radius:10px;border:1px solid #263752;margin-top:16px}} .data-table{{border-collapse:collapse;width:100%;font-size:.9rem;display:block;overflow:auto}} .data-table th,.data-table td{{border:1px solid var(--line);padding:8px 10px;text-align:left;white-space:nowrap}} .data-table th{{background:#182842;position:sticky;top:0}} code{{background:#172238;padding:2px 5px;border-radius:4px}} details{{background:#0e1727;border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:12px 0}} summary{{cursor:pointer;font-weight:700}} nav{{margin:18px 0;color:var(--muted)}} .two{{display:grid;grid-template-columns:1fr 1fr;gap:18px}} @media(max-width:900px){{.two{{grid-template-columns:1fr}}.wrap{{padding:14px}}}}
</style></head><body><main class="wrap">
<header><h1>{html.escape(title)}</h1><p class="lede"><strong>Result first:</strong> T450A is a scale-and-node calibration, not yet a lifecycle-period or hidden-time claim. Development produced {rung_count} supported feature-rung address(es); {transferred} transferred to both experiment-4 flies under the frozen scale-and-direction rule. The raw shapes, failed transfers and distortions are all shown below rather than reduced to gates.</p></header>
<div class="cards">
<div class="card"><div class="number">8</div><div class="label">individual flies (6 development, 2 untouched)</div></div>
<div class="card"><div class="number">32</div><div class="label">continuous 60-second pose envelopes</div></div>
<div class="card"><div class="number">{rung_count}</div><div class="label">development-supported feature rungs</div></div>
<div class="card"><div class="number">{transferred}/{max(rung_count,1)}</div><div class="label">rungs transferring to both holdout flies</div></div>
<div class="card"><div class="number">{100*observed_above:.1f}%</div><div class="label">envelope/rung scores above their timestamp-null 95th percentile</div></div>
<div class="card"><div class="number">{100*reversal_opposes:.1f}%</div><div class="label">signed asymmetries opposing under reversal</div></div>
</div>
<section class="report-section"><h2>Who, what, when, where, why and how</h2>
<p><strong>Who:</strong> eight individual adult male fruit flies; experiments 1–3 are development, experiment 4 is untouched transfer. <strong>What:</strong> traversal, rotation, core bend, core span, appendage articulation and left/right balance, all derived independently from pose. <strong>When:</strong> four 60-second envelopes at 12.5%, 37.5%, 62.5% and 87.5% of each recording; local scales 10 ms–10.24 s. <strong>Where:</strong> fly → recording-position parent → pose envelope → body-frame children → empirical local rungs → previously mapped 10-minute/hour/day parents. <strong>Why:</strong> discover real observable children and scale addresses before attempting a lifecycle web or meta-time wave. <strong>How:</strong> development-only winsorisation, scale descriptors and rung support; frozen mappings applied unchanged to experiment 4.</p>
<p><strong>Common parent-scale candidates:</strong> {html.escape(common_text)}. A shared band means several observed identities change temporal character near the same scale; it does not by itself make them a Di-ARA.</p></section>
<div class="notice"><strong>Boundary of the answer:</strong> a 60-second parent contains too few independent repetitions to establish a 10–60 second cycle. T450A can discover local micro/bout rungs only. Longer structure belongs to T450B and requires a newly stated test, not extrapolation.</div>
<section class="report-section"><h2>Frozen development rungs</h2><p>A ring in the support figure is frozen only when at least four of six independent development flies nominate the same boundary within ±1 octave. Raw scale curves remain the primary evidence.</p>{rung_table}</section>
<section class="report-section"><h2>Untouched transfer decisions</h2><p>Transfer requires both experiment-4 flies to nominate a boundary within ±1 octave and agree with at least two of three development descriptor directions. A failed row does not erase the shape shown in the holdout figure.</p>{transfer_table}</section>
{''.join(sections)}
<section class="report-section"><h2>ARA interpretation—bounded</h2><p>Each selected amount is mapped to 0–2 only for comparison, with ridge 1 equal to the development median under a robust tanh map. This is a relational centre, not a universal physical ridge. The paired panels are simple same-envelope ARA cuts. They become candidate Di-ARA relations only if later T450B/T450C tests establish strongly coupled poles and directional lineage across scales.</p></section>
<section class="report-section"><h2>Data limitations and possible distortions</h2><ul><li>Camera coordinates are pixels; within-fly body length supplies the only spatial normalisation.</li><li>Pose has no per-point confidence score. Finite means available, not anatomically perfect.</li><li>Right/left appendage visibility is asymmetric; left/right balance is conditioned on paired visibility and cannot be read as pure biology.</li><li>The cohort is warm, nutrient-limited and stress/terminal accelerated—not a normal-lifespan population.</li><li>Only two independent holdout flies are available in this calibration; transfer is preliminary.</li><li>Published behaviours and edge contact can explain occupancy, but did not construct the pose axes.</li></ul></section>
<section class="report-section"><h2>Reproducibility and source files</h2><p>Protocol: <a href="../T450A_FROZEN_PROTOCOL.md">T450A_FROZEN_PROTOCOL.md</a>. Frozen configuration: <a href="T450A_FROZEN_CONFIG.json">T450A_FROZEN_CONFIG.json</a>. Main tables: <a href="T450A_development_scale_metrics.csv">development scale metrics</a>, <a href="T450A_development_fly_boundaries.csv">development boundaries</a>, <a href="T450A_holdout_transfer.csv">holdout transfer</a>, <a href="T450A_development_controls.csv">controls</a>. Public source: <a href="https://doi.org/10.34770/1sab-8845">Princeton Drosophila lifetime dataset</a>.</p><details><summary>Eight selected source identities</summary><ul>{sources_list}</ul></details></section>
</main></body></html>"""
    output = RESULTS / "T450A_POSE_SCALE_DISCOVERY_REPORT.html"
    output.write_text(document, encoding="utf-8")
    return output


def main() -> None:
    theme()
    tables = load_tables()
    dev_bursts, _ = load_split(HERE / "cache" / "development")
    figures = [
        (figure_address(tables), "1. Relational address and measured scale", "This establishes exactly which identity, scale and projection T450A observes. The orange 10–60 second region is visibly unresolved, preventing the 60-second envelope from being mistaken for a cycle."),
        (figure_raw_example(dev_bursts), "2. Raw pose children in their body frame", "The skeleton overlay shows what body-frame normalisation removes and retains. The six numbered axes use physical or dimensionless units before any 0–2 ARA display mapping."),
        (figure_scale_landscape(tables["development_scale_metrics"], "T450A_03_DEVELOPMENT_SCALE_LANDSCAPE.png", "Development-only temporal geometry across every measured feature"), "3. Development scale landscape", "Each row is a different observed child; each column asks a different temporal question. Curves separate recording position from scale, so decline is not silently renamed a rung."),
        (figure_rung_support(tables), "4. Development rung support", "The left panel counts independent flies; the right panel shows strength. Pink rings mark the configuration frozen before experiment 4 was opened."),
        (figure_ara_planes(tables), "5. Same-envelope ARA amount planes", "These paired cuts show relational occupancy and individual recording-position paths at supported rungs. They are not automatically Di-ARAs, and ridge 1 is explicitly the development centre."),
        (figure_controls(tables), "6. Chronology and time-reversal controls", "Timestamp permutation tests whether ordered history matters. Reversal tests the directional component: persistence can survive reversal, while signed time asymmetry should flip."),
        (figure_transfer(tables), "7. Untouched experiment-4 transfer", "The full holdout curves are shown beside the frozen decision. This lets visible regime deformation remain examinable even when a strict transfer rule is missed."),
        (figure_quality(tables), "8. Visibility, environment and behavioural annotations", "This makes measurement limits part of the geometry. In particular, paired left/right visibility and the hotter holdout regime can distort child paths."),
    ]
    report = build_html(tables, figures)
    print(report)


if __name__ == "__main__":
    main()
