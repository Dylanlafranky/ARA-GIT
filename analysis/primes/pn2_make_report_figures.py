"""Create post-result presentation figures from frozen PN2 summary tables."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "PN2_GAP_CLASS_SURVIVAL.csv"
OUTPUT = HERE / "PN2_GAP_CLASS_RESIDUALS.png"


def main() -> None:
    frame = pd.read_csv(SOURCE)
    frame = frame[frame.survivor_edges >= 100].copy()
    models = [
        ("hl29_expected_survivors", "HL29", "#8C98A4", "--", "s"),
        ("raw_edge_expected_survivors", "Raw stencil", "#E67E22", "-", "s"),
        ("ara_edge_expected_survivors", "ARA endpoints", "#2E7DBA", "-", "o"),
        ("ara_edge_decompressed_expected_survivors", "ARA decompressed", "#D9A514", "-", "D"),
    ]
    actual = frame.survivor_edges.to_numpy(float)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    for column, label, color, line, marker in models:
        residual = frame[column].to_numpy(float) - actual
        axes[0].plot(frame.gap, residual, label=label, color=color, linestyle=line, marker=marker)
        axes[1].plot(frame.gap, 100.0 * residual / actual, label=label, color=color, linestyle=line, marker=marker)
    for axis in axes:
        axis.axhline(0, color="#202733", linewidth=0.9)
        axis.grid(axis="y", color="#D8DEE5", linewidth=0.7)
        axis.set_xlabel("Candidate-edge gap")
    axes[0].set_title("Expected minus actual surviving edges")
    axes[0].set_ylabel("Count residual")
    axes[1].set_title("Gap-class survivor-count error")
    axes[1].set_ylabel("Relative residual (%)")
    axes[1].legend(frameon=False, ncol=2)
    fig.suptitle("PN2 adjacent p29-wheel edge-survival residuals", fontsize=16, color="#202733")
    fig.savefig(OUTPUT, dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
