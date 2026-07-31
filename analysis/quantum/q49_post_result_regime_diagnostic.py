"""Post-result visual diagnosis of the Q49 development/evaluation reversal.

This is exploratory. It does not alter the frozen Q49 verdict or gates.
"""

from __future__ import annotations

import csv
import gzip
import math
import pathlib

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = pathlib.Path(__file__).resolve().parent
EVENTS = ROOT / "Q49_EXTERNAL_TIME_VECTOR_EVENTS.csv.gz"
OUTPUT = ROOT / "Q49_EXTERNAL_TIME_VECTOR_REGIME_DIAGNOSTIC.png"

LEFT = 1.0 / math.e
RIGHT = ((1.0 + math.sqrt(5.0)) / 2.0) - 1.0
WIDTH = RIGHT - LEFT
ARC_STARTS = np.mod(LEFT + np.arange(4) / 4.0, 1.0)
ARC_NAMES = ["declared", "+quarter", "opposite", "-quarter"]
THRESHOLDS = np.asarray([0.005, 0.01, 0.02, 0.05, 0.10])


def in_arc(values: np.ndarray, start: float) -> np.ndarray:
    return np.mod(values - start, 1.0) <= WIDTH


def load() -> dict[str, np.ndarray]:
    rows: list[dict[str, str]] = []
    with gzip.open(EVENTS, "rt", encoding="utf-8", newline="") as handle:
        rows.extend(csv.DictReader(handle))
    return {
        "start": np.asarray([int(row["current_start"]) for row in rows]),
        "heading": np.asarray([float(row["circle_heading"]) for row in rows]),
        "strength": np.asarray([float(row["circle_strength"]) for row in rows]),
        "stratum": np.asarray([row["stratum"] for row in rows]),
    }


def occupancy(
    heading: np.ndarray, strength: np.ndarray, threshold: float
) -> np.ndarray:
    selected = heading[strength >= threshold]
    if not selected.size:
        return np.full(4, np.nan)
    return np.asarray(
        [np.mean(in_arc(selected, float(start))) for start in ARC_STARTS]
    )


def shade_arc(axis: plt.Axes, start: float, width: float, **kwargs: object) -> None:
    end = start + width
    if end <= 1.0:
        axis.axhspan(start, end, **kwargs)
    else:
        axis.axhspan(start, 1.0, **kwargs)
        continuation = dict(kwargs)
        continuation.pop("label", None)
        axis.axhspan(0.0, end - 1.0, **continuation)


def main() -> None:
    data = load()
    eligible = data["strength"] >= 0.01
    development = eligible & (data["stratum"] == "development")
    evaluation = eligible & (data["stratum"] == "evaluation")

    figure, axes = plt.subplots(2, 2, figsize=(17, 11), constrained_layout=True)
    figure.suptitle(
        "Q49 post-result diagnosis — the whole-circle centreline reverses after the split",
        fontsize=21,
        fontweight="bold",
    )

    axis = axes[0, 0]
    shade_arc(
        axis,
        float(ARC_STARTS[0]),
        WIDTH,
        color="#e4a12c",
        alpha=0.18,
        label="declared 1/e → Phi arc",
    )
    shade_arc(
        axis,
        float(ARC_STARTS[2]),
        WIDTH,
        color="#6a83b7",
        alpha=0.14,
        label="opposite matched arc",
    )
    axis.scatter(
        data["start"][development],
        data["heading"][development],
        s=13,
        alpha=0.46,
        color="#d99017",
        label="development",
    )
    axis.scatter(
        data["start"][evaluation],
        data["heading"][evaluation],
        s=18,
        alpha=0.58,
        color="#456da8",
        label="evaluation",
    )
    axis.axvline(250, color="#222222", ls="--", lw=1.6, label="split at 250")
    axis.set(
        xlabel="time-slice index of complete-circle centre",
        ylabel="external centreline heading (full turns)",
        ylim=(0, 1),
        title="Eligible external headings through time",
    )
    axis.legend(fontsize=9, ncol=2)

    axis = axes[0, 1]
    dev_occ = occupancy(
        data["heading"][data["stratum"] == "development"],
        data["strength"][data["stratum"] == "development"],
        0.01,
    )
    eval_occ = occupancy(
        data["heading"][data["stratum"] == "evaluation"],
        data["strength"][data["stratum"] == "evaluation"],
        0.01,
    )
    positions = np.arange(4)
    axis.bar(
        positions - 0.19,
        dev_occ,
        width=0.38,
        color="#d99017",
        label="development",
    )
    axis.bar(
        positions + 0.19,
        eval_occ,
        width=0.38,
        color="#456da8",
        label="evaluation",
    )
    axis.axhline(WIDTH, color="#333333", ls="--", label="uniform expectation")
    axis.set_xticks(positions, ARC_NAMES)
    axis.set(
        ylabel="fraction of eligible headings",
        title="Matched quarter-turn arcs at the frozen 0.01 floor",
    )
    axis.legend()

    axis = axes[1, 0]
    for stratum, color, marker in (
        ("development", "#d99017", "o"),
        ("evaluation", "#456da8", "s"),
    ):
        mask = data["stratum"] == stratum
        declared = []
        opposite = []
        for threshold in THRESHOLDS:
            fractions = occupancy(
                data["heading"][mask], data["strength"][mask], float(threshold)
            )
            declared.append(fractions[0])
            opposite.append(fractions[2])
        axis.plot(
            THRESHOLDS,
            declared,
            marker=marker,
            color=color,
            lw=2.2,
            label=f"{stratum}: declared",
        )
        axis.plot(
            THRESHOLDS,
            opposite,
            marker=marker,
            color=color,
            lw=1.8,
            ls="--",
            label=f"{stratum}: opposite",
        )
    axis.axhline(WIDTH, color="#333333", ls=":", label="uniform expectation")
    axis.set(
        xlabel="minimum centre movement / circle radius",
        ylabel="matched-arc occupancy",
        title="Direction persists as the movement floor changes",
    )
    axis.legend(fontsize=9)

    axis = axes[1, 1]
    axis.scatter(
        data["heading"][development],
        data["strength"][development],
        s=13,
        alpha=0.34,
        color="#d99017",
        label="development",
    )
    axis.scatter(
        data["heading"][evaluation],
        data["strength"][evaluation],
        s=18,
        alpha=0.55,
        color="#456da8",
        label="evaluation",
    )
    axis.axvspan(LEFT, RIGHT, color="#e4a12c", alpha=0.14)
    opposite_start = float(ARC_STARTS[2])
    axis.axvspan(opposite_start, 1.0, color="#6a83b7", alpha=0.10)
    axis.axvspan(0.0, opposite_start + WIDTH - 1.0, color="#6a83b7", alpha=0.10)
    axis.set_yscale("log")
    axis.set(
        xlabel="external centreline heading (full turns)",
        ylabel="centre movement / circle radius",
        xlim=(0, 1),
        title="The reversal is directional, not a single movement magnitude",
    )
    axis.legend()

    figure.savefig(OUTPUT, dpi=180)
    print(OUTPUT)


if __name__ == "__main__":
    main()
