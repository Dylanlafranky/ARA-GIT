#!/usr/bin/env python3
"""Post-hoc direction-pair audit for T354; not a frozen gate."""

from __future__ import annotations

from pathlib import Path

import matplotlib

HERE = Path(__file__).resolve().parent
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PREFIX = "T354_IRRATIONALITY_PARENT_RIDGE_CENTRE"


def main() -> None:
    series = pd.read_csv(HERE / f"{PREFIX}_SERIES.csv")
    keys = ["q", "d", "duration", "replicate", "mode", "window", "true_center"]
    paired = series.pivot(index=keys, columns="direction", values="predicted_ridge").reset_index()
    paired["paired_ridge"] = (
        paired["irrational_to_rational"] + paired["rational_to_irrational"]
    ) / 2.0
    paired["forward_error"] = paired["irrational_to_rational"] - paired.true_center
    paired["reverse_error"] = paired["rational_to_irrational"] - paired.true_center
    paired["paired_error"] = paired.paired_ridge - paired.true_center
    paired["paired_abs_error"] = np.abs(paired.paired_error)
    paired.to_csv(HERE / f"{PREFIX}_POSTHOC_DIRECTION_PAIRS.csv", index=False)

    summary = (
        paired.groupby(["mode", "window"])
        .agg(
            n=("paired_abs_error", "size"),
            forward_error=("forward_error", "median"),
            reverse_error=("reverse_error", "median"),
            paired_error=("paired_error", "median"),
            paired_abs_error=("paired_abs_error", "median"),
            paired_p95_abs=("paired_abs_error", lambda x: float(np.quantile(x, 0.95))),
        )
        .reset_index()
    )
    summary.to_csv(HERE / f"{PREFIX}_POSTHOC_DIRECTION_PAIR_SUMMARY.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), constrained_layout=True)
    ax = axes[0]
    example = paired[(paired["mode"] == "ordered") & (paired.window == 512)]
    ax.scatter(example.true_center, example.irrational_to_rational, s=24, alpha=0.55, label="irrational to rational")
    ax.scatter(example.true_center, example.rational_to_irrational, s=24, alpha=0.55, label="rational to irrational")
    ax.scatter(example.true_center, example.paired_ridge, s=22, color="#222222", label="direction-pair midpoint")
    limits = (1320, 2780)
    ax.plot(limits, limits, color="#7A8490", lw=1, linestyle=":")
    ax.set(
        xlim=limits,
        ylim=limits,
        xlabel="hidden referee centre (states)",
        ylabel="predicted centre (states)",
        title="Each direction misses; their midpoint returns to the seam",
    )
    ax.legend(frameon=False, fontsize=8)

    ax = axes[1]
    styles = {"ordered": ("-", "o"), "abrupt": ("--", "s")}
    for mode, (line, marker) in styles.items():
        part = summary[summary["mode"] == mode]
        ax.plot(part.window, part.forward_error, line, marker=marker, color="#2F6FB0", alpha=0.85, label=f"{mode}: forward")
        ax.plot(part.window, part.reverse_error, line, marker=marker, color="#D49A2E", alpha=0.85, label=f"{mode}: reverse")
        ax.plot(part.window, part.paired_error, line, marker=marker, color="#222222", lw=2, label=f"{mode}: midpoint")
    ax.axhline(0, color="#7A8490", lw=1)
    ax.set(
        xlabel="observation window W (states)",
        ylabel="median centre error (states)",
        title="Opposite one-sided biases cancel in the paired reading",
    )
    ax.legend(frameon=False, fontsize=8, ncol=2)
    fig.suptitle("T354 post-hoc direction-pair audit - hypothesis-generating only", fontsize=15, fontweight="bold")
    fig.savefig(HERE / f"{PREFIX}_POSTHOC_DIRECTION_PAIR_FIGURE.png", dpi=170)
    plt.close(fig)

    ordered = paired[paired["mode"] == "ordered"].paired_abs_error
    abrupt = paired[paired["mode"] == "abrupt"].paired_abs_error
    lines = [
        "# T354 post-hoc direction-pair audit",
        "",
        "**Status:** hypothesis-generating; not a frozen T354 gate",
        "",
        "The frozen single-direction ridge test failed. Its directional errors were nevertheless nearly equal and opposite. Pairing the independently measured forward and reverse centres and taking their midpoint recovered the known seam to within a few states.",
        "",
        f"- ordered median paired absolute error: `{ordered.median():.6f}` states",
        f"- ordered 95th percentile paired absolute error: `{ordered.quantile(0.95):.6f}` states",
        f"- abrupt median paired absolute error: `{abrupt.median():.6f}` states",
        f"- abrupt 95th percentile paired absolute error: `{abrupt.quantile(0.95):.6f}` states",
        "",
        f"![T354 post-hoc direction pair]({PREFIX}_POSTHOC_DIRECTION_PAIR_FIGURE.png)",
        "",
        "## Boundary",
        "",
        "The generator uses exactly reversed endpoint paths, so antisymmetric cancellation may be partly forced by the synthetic construction. This result cannot rescue the frozen T354 verdict. It motivates a new preregistered test in which a simultaneous two-sided pair must recover the parent ridge under controlled child asymmetry.",
    ]
    (HERE / f"{PREFIX}_POSTHOC_DIRECTION_PAIR_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
