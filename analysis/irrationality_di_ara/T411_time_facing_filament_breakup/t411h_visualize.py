"""Create the fully labelled T411H three-rung result figure."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "T411H_three_rung_grandchild_lock"
BLUE = "#326cb8"
PURPLE = "#72519b"
GOLD = "#d89a27"
INK = "#222936"
GREY = "#8b96a6"
GRID = "#d6dce6"


def weighted_plane(frame: pd.DataFrame, bins: int = 10):
    edges = np.linspace(0, 2, bins + 1)
    xbin = np.clip(np.digitize(frame.x_child, edges) - 1, 0, bins - 1)
    ybin = np.clip(np.digitize(frame.x_grandchild, edges) - 1, 0, bins - 1)
    weight = np.zeros((bins, bins), float)
    outcome = np.zeros((bins, bins), float)
    names = [[set() for _ in range(bins)] for _ in range(bins)]
    for xb, yb, y, w, name in zip(xbin, ybin, frame.y, frame.event_weight, frame.Name):
        weight[yb, xb] += w
        outcome[yb, xb] += w * y
        names[yb][xb].add(name)
    probability = np.full_like(weight, np.nan)
    valid = weight > 0
    probability[valid] = outcome[valid] / weight[valid]
    event_count = np.array([[len(names[y][x]) for x in range(bins)] for y in range(bins)])
    probability[(weight < .15) | (event_count < 2)] = np.nan
    return probability


def plane_panel(ax, frame: pd.DataFrame, title: str, vmax: float = .30):
    probability = weighted_plane(frame)
    image = ax.imshow(
        probability, origin="lower", extent=[0, 2, 0, 2], aspect="equal",
        cmap="magma", vmin=0, vmax=vmax, interpolation="nearest",
    )
    ax.axvline(1, color="#65a86c", lw=1.5, ls="--")
    ax.axhline(1, color="#65a86c", lw=1.5, ls="--")
    ax.scatter([1], [1], s=28, facecolor="white", edgecolor="#397c47", zorder=5)
    ax.set_title(title, loc="left", fontsize=11.5, fontweight="bold")
    ax.set_xlabel("direct child ARA $x_C$ (0–2)")
    ax.set_ylabel("grandchild seam ARA $x_G$ (0–2)")
    ax.set_xticks([0, .5, 1, 1.5, 2])
    ax.set_yticks([0, .5, 1, 1.5, 2])
    ax.grid(False)
    return image


def main():
    predictions = pd.read_csv(OUT / "T411H_PREDICTIONS.csv")
    events = pd.read_csv(OUT / "T411H_EVENTS.csv")
    overall = pd.read_csv(OUT / "T411H_MODEL_PERFORMANCE.csv")
    by_fluid = pd.read_csv(OUT / "T411H_FLUID_PERFORMANCE.csv")
    null = pd.read_csv(OUT / "T411H_GRANDCHILD_SHIFT_NULL.csv")
    result = json.loads((OUT / "T411H_RESULTS.json").read_text(encoding="utf-8"))

    plt.rcParams.update({
        "font.family": "DejaVu Sans", "axes.edgecolor": "#4d5666",
        "axes.labelcolor": INK, "xtick.color": "#5a6474",
        "ytick.color": "#5a6474", "text.color": INK,
    })
    fig = plt.figure(figsize=(22, 18), facecolor="#f6f7fb")
    grid = fig.add_gridspec(3, 3, left=.055, right=.975, top=.875, bottom=.07,
                           wspace=.25, hspace=.34)

    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]),
            fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[1, 1])]
    images = []
    for ax, fluid in zip(axes, ["S1", "S2", "S3", "S4"]):
        group = predictions[predictions.fluid == fluid]
        gw = events[events.fluid == fluid].grandchild_window_frames
        window_text = f"G window {int(gw.min())}" if gw.min() == gw.max() else f"G window {int(gw.min())}–{int(gw.max())} frames"
        images.append(plane_panel(
            ax, group,
            f"{fluid}: {group.Name.nunique()} identities · {window_text}",
        ))
    colorbar = fig.colorbar(images[-1], ax=axes, fraction=.022, pad=.02)
    colorbar.set_label("event-balanced probability of parent handover\nwithin one frozen child window")

    pooled_ax = fig.add_subplot(grid[0, 2])
    pooled_image = plane_panel(
        pooled_ax, predictions,
        f"Pooled out-of-fluid plane: {predictions.Name.nunique()} identities",
    )
    pooled_colorbar = fig.colorbar(pooled_image, ax=pooled_ax, fraction=.046, pad=.04)
    pooled_colorbar.set_label("handover probability")

    model_ax = fig.add_subplot(grid[1, 2])
    order = ["constant", "parent_state", "parent_child", "parent_grandchild",
             "three_rung_additive", "three_point_lock"]
    labels = ["constant", "parent", "parent +\nchild", "parent +\ngrandchild",
              "three-rung\nadditive", "three-point\nlock"]
    score = overall.set_index("model").loc[order]
    bars = model_ax.bar(
        np.arange(len(order)), score.brier,
        color=[GREY, "#68778c", BLUE, GOLD, "#9a88b1", PURPLE],
        edgecolor="#404856",
    )
    parent_brier = float(score.loc["parent_state", "brier"])
    model_ax.axhline(parent_brier, color="#596475", lw=1.3, ls="--",
                     label=f"parent Brier {parent_brier:.4f}")
    model_ax.set_xticks(np.arange(len(order)), labels)
    model_ax.set_ylim(0, max(score.brier) * 1.28)
    model_ax.set_ylabel("weighted Brier error (lower is better)")
    model_ax.set_title("Leave-one-fluid-out model comparison", loc="left", fontweight="bold")
    model_ax.grid(axis="y", color=GRID, alpha=.8)
    model_ax.legend(frameon=False, loc="upper left")
    for bar, auc in zip(bars, score.auc):
        model_ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + .001,
                      f"AUC\n{auc:.3f}", ha="center", va="bottom", fontsize=8.8)

    improvement_ax = fig.add_subplot(grid[2, 0])
    focus = ["parent_child", "parent_grandchild", "three_rung_additive", "three_point_lock"]
    focus_labels = ["parent + child", "parent + grandchild", "three-rung additive", "three-point lock"]
    colors = [BLUE, GOLD, "#9a88b1", PURPLE]
    pivot = by_fluid.pivot(index="fluid", columns="model", values="brier")
    x = np.arange(len(pivot.index))
    width = .19
    for i, (name, label, color) in enumerate(zip(focus, focus_labels, colors)):
        delta = pivot.parent_state - pivot[name]
        improvement_ax.bar(x + (i - 1.5) * width, delta, width,
                           color=color, edgecolor="#414957", label=label)
    improvement_ax.axhline(0, color=INK, lw=1.2)
    improvement_ax.set_xticks(x, pivot.index)
    improvement_ax.set_ylabel("parent Brier − model Brier\n(positive means improvement)")
    improvement_ax.set_title("Grandchild lock transfer by fluid", loc="left", fontweight="bold")
    improvement_ax.grid(axis="y", color=GRID, alpha=.8)
    improvement_ax.legend(frameon=False, fontsize=8.8, ncol=2)

    null_ax = fig.add_subplot(grid[2, 1])
    values = null.improvement_over_parent_child.to_numpy(float)
    observed = result["grandchild_alignment_null"]["observed_improvement_over_parent_child"]
    null_ax.hist(values, bins=35, color="#aab4c3", edgecolor="white")
    null_ax.axvline(0, color=INK, lw=1.4, label="break-even")
    null_ax.axvline(observed, color=PURPLE, lw=2.5,
                    label=f"aligned observed {observed:+.4f}")
    null_ax.set_xlabel("parent+child Brier − shifted lock Brier\n(positive means lock is better)")
    null_ax.set_ylabel("grandchild-shift controls")
    null_ax.set_title("Grandchild timing falsification", loc="left", fontweight="bold")
    null_ax.grid(axis="y", color=GRID, alpha=.8)
    null_ax.legend(frameon=False, fontsize=9)
    null_ax.text(.02, .70,
                 "Correctly aligned three-way lock beats every shifted\n"
                 "grandchild control (p = 0.001).",
                 transform=null_ax.transAxes, va="top", fontsize=9.5,
                 bbox=dict(boxstyle="round,pad=.4", facecolor="#f1ebf7", edgecolor="#c2afd5"))

    example_ax = fig.add_subplot(grid[2, 2])
    s2_events = events[events.fluid == "S2"].sort_values("target_t_s")
    chosen = s2_events.iloc[len(s2_events) // 2]
    example = predictions[predictions.Name == chosen.Name].sort_values("time_s").copy()
    example["relative_window"] = (example.time_s - example.target_t_s) / example.child_horizon_s
    example = example[example.relative_window >= -8]
    example_ax.axvspan(-1, 0, color="#f3d99a", alpha=.45,
                       label="forecast outcome window")
    example_ax.axhline(1, color="#4d8d59", lw=1.3, ls="--", label="ARA ridge 1")
    example_ax.plot(example.relative_window, example.x_parent, color=INK, lw=1.8,
                    label="parent $x_P$")
    example_ax.plot(example.relative_window, example.x_child, color=BLUE, lw=1.5,
                    label="child $x_C$")
    example_ax.plot(example.relative_window, example.x_grandchild, color=PURPLE, lw=1.5,
                    label="grandchild seam $x_G$")
    example_ax.axvline(0, color="#7b8492", lw=1.4, ls=":", label="offline parent handover")
    example_ax.set_xlim(-8, .05)
    example_ax.set_ylim(-.05, 2.05)
    example_ax.set_xlabel("time relative to parent handover (child-window units)")
    example_ax.set_ylabel("ARA coordinate (0–2)")
    example_ax.set_title(f"Causal three-rung example: S2 {chosen.Name}", loc="left", fontweight="bold")
    example_ax.grid(color=GRID, alpha=.75)
    example_ax.legend(frameon=False, fontsize=8.3, ncol=2, loc="upper left")

    fig.suptitle("T411H — three-rung grandchild singularity lock",
                 x=.055, y=.965, ha="left", fontsize=24, fontweight="bold")
    fig.text(.055, .925,
             "123 filament identities · 10,206 causal snapshots · parent / half-window child / quarter-window grandchild · every fluid held out once",
             fontsize=12, color="#657083")
    fig.text(.055, .895,
             "Frozen result: 4/5 gates. Correct grandchild timing improves the parent–child lock, but the full lock misses pooled parent Brier because S1 does not transfer.",
             fontsize=12.7, color=PURPLE, fontweight="bold")
    pair = result["posthoc_parent_grandchild_alignment"]
    fig.text(.055, .025,
             "Boundary: archive diagnostic, not external confirmation. Blank heatmap cells lack coverage. Parent+grandchild alone improves parent Brier in 4/4 fluids, "
             f"but its timing audit fails (post-hoc p={pair['p_ge_observed']:.3f}); timing specificity requires the three-way relation.",
             fontsize=9.8, color="#657083")
    fig.savefig(OUT / "T411H_THREE_RUNG_GRANDCHILD_LOCK_VISUAL.png",
                dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    main()

