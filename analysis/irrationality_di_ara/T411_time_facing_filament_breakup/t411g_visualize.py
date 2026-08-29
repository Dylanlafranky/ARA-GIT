"""Create the fully labelled T411G causal Di-ARA result figure."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
OUT = HERE / "results" / "T411G_causal_di_ara"
BLUE = "#356bb3"
ORANGE = "#df8a16"
PURPLE = "#7552a5"
GREEN = "#3f9360"
DARK = "#202534"
GRID = "#d5dbe5"


def weighted_plane(frame: pd.DataFrame, bins: int = 10):
    edges = np.linspace(0, 2, bins + 1)
    xbin = np.clip(np.digitize(frame.x_child, edges) - 1, 0, bins - 1)
    ybin = np.clip(np.digitize(frame.x_parent, edges) - 1, 0, bins - 1)
    weight = np.zeros((bins, bins), float)
    outcome = np.zeros((bins, bins), float)
    events: list[list[set]] = [[set() for _ in range(bins)] for _ in range(bins)]
    for xb, yb, y, w, name in zip(xbin, ybin, frame.y, frame.event_weight, frame.Name):
        weight[yb, xb] += w
        outcome[yb, xb] += w * y
        events[yb][xb].add(name)
    probability = np.full_like(weight, np.nan)
    valid = weight > 0
    probability[valid] = outcome[valid] / weight[valid]
    event_count = np.array([[len(events[y][x]) for x in range(bins)] for y in range(bins)])
    probability[(weight < .15) | (event_count < 2)] = np.nan
    return edges, probability


def plane_panel(ax, frame: pd.DataFrame, title: str, vmax: float = .25):
    edges, probability = weighted_plane(frame)
    image = ax.imshow(
        probability, origin="lower", extent=[0, 2, 0, 2], aspect="equal",
        cmap="magma", vmin=0, vmax=vmax, interpolation="nearest",
    )
    ax.axvline(1, color="#74c476", lw=1.6, ls="--")
    ax.axhline(1, color="#74c476", lw=1.6, ls="--")
    ax.scatter([1], [1], s=35, facecolor="white", edgecolor="#2d7f4f", zorder=5)
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel("child ARA position $x_C$ (0–2)")
    ax.set_ylabel("parent ARA position $x_P$ (0–2)")
    ax.set_xticks([0, .5, 1, 1.5, 2])
    ax.set_yticks([0, .5, 1, 1.5, 2])
    ax.grid(False)
    return image


def main():
    predictions = pd.read_csv(OUT / "T411G_PREDICTIONS.csv")
    overall = pd.read_csv(OUT / "T411G_MODEL_PERFORMANCE.csv")
    by_fluid = pd.read_csv(OUT / "T411G_FLUID_PERFORMANCE.csv")
    null = pd.read_csv(OUT / "T411G_PARENT_SHIFT_NULL.csv")
    result = json.loads((OUT / "T411G_RESULTS.json").read_text(encoding="utf-8"))

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#4e5666",
        "axes.labelcolor": DARK,
        "xtick.color": "#596273",
        "ytick.color": "#596273",
        "text.color": DARK,
    })
    fig = plt.figure(figsize=(22, 18), facecolor="#f5f7fb")
    grid = fig.add_gridspec(3, 3, left=.055, right=.975, top=.88, bottom=.07,
                           wspace=.23, hspace=.33)

    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]),
            fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[1, 1])]
    images = []
    for ax, fluid in zip(axes, ["S1", "S2", "S3", "S4"]):
        group = predictions[predictions.fluid == fluid]
        images.append(plane_panel(
            ax, group,
            f"{fluid}: {group.Name.nunique()} held-out identities · {len(group):,} snapshots",
        ))
    cbar = fig.colorbar(images[-1], ax=axes, fraction=.022, pad=.02)
    cbar.set_label("event-balanced probability of parent handover\nwithin one frozen child window")

    pooled_ax = fig.add_subplot(grid[0, 2])
    pooled_image = plane_panel(
        pooled_ax, predictions,
        f"Pooled out-of-fluid plane: {predictions.Name.nunique()} identities",
    )
    cbar2 = fig.colorbar(pooled_image, ax=pooled_ax, fraction=.046, pad=.04)
    cbar2.set_label("handover probability")

    model_ax = fig.add_subplot(grid[1, 2])
    order = ["constant", "child_position", "child_state", "parent_state", "additive", "di_ara"]
    labels = ["constant", "child\nposition", "child\nstate", "parent\nstate", "additive", "full\nDi-ARA"]
    score = overall.set_index("model").loc[order]
    constant_brier = float(score.loc["constant", "brier"])
    colors = ["#9ca5b3" if name == "constant" else
              GREEN if score.loc[name, "brier"] < constant_brier else ORANGE for name in order]
    bars = model_ax.bar(np.arange(len(order)), score.brier, color=colors, edgecolor="#4a5260")
    model_ax.axhline(constant_brier, color="#707989", ls="--", lw=1.3,
                     label=f"constant Brier {constant_brier:.4f}")
    model_ax.set_xticks(np.arange(len(order)), labels)
    model_ax.set_ylim(0, max(score.brier) * 1.28)
    model_ax.set_ylabel("weighted Brier error (lower is better)")
    model_ax.set_title("Cross-identity model comparison", loc="left", fontweight="bold")
    model_ax.grid(axis="y", color=GRID, alpha=.8)
    model_ax.legend(frameon=False, loc="upper left")
    for bar, auc in zip(bars, score.auc):
        model_ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + .001,
                      f"AUC\n{auc:.3f}", ha="center", va="bottom", fontsize=9)

    improvement_ax = fig.add_subplot(grid[2, 0])
    focus = ["child_state", "parent_state", "additive", "di_ara"]
    focus_labels = ["child state", "parent state", "additive", "full Di-ARA"]
    pivot = by_fluid.pivot(index="fluid", columns="model", values="brier")
    x = np.arange(len(pivot.index))
    width = .19
    focus_colors = [BLUE, GREEN, "#8290a5", PURPLE]
    for i, (name, label, color) in enumerate(zip(focus, focus_labels, focus_colors)):
        delta = pivot.constant - pivot[name]
        improvement_ax.bar(x + (i-1.5)*width, delta, width, label=label,
                           color=color, edgecolor="#424a57")
    improvement_ax.axhline(0, color=DARK, lw=1.2)
    improvement_ax.set_xticks(x, pivot.index)
    improvement_ax.set_ylabel("constant Brier − model Brier\n(positive means improvement)")
    improvement_ax.set_title("Transfer differs by fluid identity", loc="left", fontweight="bold")
    improvement_ax.grid(axis="y", color=GRID, alpha=.8)
    improvement_ax.legend(frameon=False, ncol=2, fontsize=9)

    null_ax = fig.add_subplot(grid[2, 1])
    values = null.improvement_over_child_state.to_numpy(float)
    observed = result["parent_alignment_null"]["observed_improvement_over_child_state"]
    null_ax.hist(values, bins=35, color="#a8b3c3", edgecolor="white")
    null_ax.axvline(0, color=DARK, lw=1.4, label="break-even vs child state")
    null_ax.axvline(observed, color=PURPLE, lw=2.5,
                    label=f"aligned observed {observed:+.4f}")
    null_ax.set_xlabel("child-state Brier − shifted Di-ARA Brier\n(positive means Di-ARA is better)")
    null_ax.set_ylabel("circular-shift controls")
    null_ax.set_title("Correct child–parent timing is informative", loc="left", fontweight="bold")
    null_ax.grid(axis="y", color=GRID, alpha=.8)
    null_ax.legend(frameon=False, fontsize=9)
    null_ax.text(.02, .70,
                 "Aligned geometry is less damaging than every shifted control,\n"
                 "but it still does not beat child state on Brier error.",
                 transform=null_ax.transAxes, va="top", fontsize=9.5,
                 bbox=dict(boxstyle="round,pad=.45", facecolor="#f3edf9", edgecolor="#c4b3d7"))

    summary_ax = fig.add_subplot(grid[2, 2])
    summary_ax.axis("off")
    summary_ax.set_title("Frozen result and boundary", loc="left", fontweight="bold", pad=12)
    gates = result["gates"]
    gate_labels = [
        ("Brier beats constant", gates["di_ara_brier_below_constant"]),
        ("AUC > 0.5", gates["di_ara_auc_above_half"]),
        ("Brier beats child state", gates["di_ara_brier_below_child_state"]),
        ("Brier beats additive", gates["di_ara_brier_below_additive"]),
        ("beats constant in ≥3/4 fluids", gates["improves_constant_in_three_of_four_fluids"]),
        ("aligned parent beats shifts", gates["aligned_parent_beats_shift_control_p_le_005"]),
    ]
    y = .93
    summary_ax.text(0, y, f"Frozen gates passed: {result['gate_count']}/6 — NOT SUPPORTED",
                    color=PURPLE, fontsize=14, fontweight="bold", transform=summary_ax.transAxes)
    y -= .105
    for label, passed in gate_labels:
        summary_ax.text(.01, y, "PASS" if passed else "FAIL",
                        color=GREEN if passed else "#bf553f", fontweight="bold",
                        transform=summary_ax.transAxes)
        summary_ax.text(.16, y, label, transform=summary_ax.transAxes)
        y -= .072
    y -= .02
    parent = score.loc["parent_state"]
    diara = score.loc["di_ara"]
    summary_ax.text(0, y,
                    f"Best transferable score: parent state\n"
                    f"Brier {parent.brier:.4f} · AUC {parent.auc:.3f}\n\n"
                    f"Full Di-ARA\nBrier {diara.brier:.4f} · AUC {diara.auc:.3f}\n\n"
                    "Reading: the parent axis carries causal rank information.\n"
                    "Correct child–parent alignment matters, but fixed pooled\n"
                    "interactions do not yet transfer across identities.",
                    transform=summary_ax.transAxes, va="top", fontsize=10.5, linespacing=1.45)

    fig.suptitle("T411G — causal child–parent Di-ARA transfer test",
                 x=.055, y=.965, ha="left", fontsize=24, fontweight="bold")
    fig.text(.055, .925,
             "123 filament identities · 10,308 causal snapshots · every fluid held out once · outcome: parent handover within one frozen child window",
             fontsize=12, color="#657083")
    fig.text(.055, .895,
             "Result: the two-axis timing relation is real, but the full fixed Di-ARA model does not transfer cleanly; parent state alone is stronger.",
             fontsize=13, color=PURPLE, fontweight="bold")
    fig.text(.055, .025,
             "Boundary: already-exposed archive diagnostic. Heatmap cells require ≥2 identities and ≥0.15 event-balanced weight. Ridge lines mark x = 1, not fitted thresholds.",
             fontsize=10, color="#657083")
    fig.savefig(OUT / "T411G_CAUSAL_DI_ARA_VISUAL.png", dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    main()
