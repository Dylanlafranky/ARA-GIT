#!/usr/bin/env python3
"""Descriptive post-T259 ARA crosswalk of the source's published T1/Ramsey curves."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(__file__).resolve().parent / "public_data" / ".matplotlib"),
)

import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "public_data" / "extracted" / "AllopticalSCQreadout_data"
CSV_OUT = HERE / "Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.csv"
JSON_OUT = HERE / "Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.json"
FIG_OUT = HERE / "Q2_PUBLIC_HARDWARE_DYNAMICS_CROSSWALK.png"

MODES = ("MW → MW", "MW → optical", "optical → optical")
COLORS = ("#6f4ba8", "#58a86c", "#c96055")


def ara_map(y: np.ndarray, fit_y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    low = float(np.min(fit_y))
    high = float(np.max(fit_y))
    width = high - low
    if width <= 0:
        raise RuntimeError("Degenerate published fit")
    if fit_y[0] >= fit_y[-1]:
        return 2 * (high - y) / width, 2 * (high - fit_y) / width
    return 2 * (y - low) / width, 2 * (fit_y - low) / width


def crossings(x: np.ndarray, level: float = 1.0) -> int:
    sign = np.sign(x - level)
    nonzero = sign[sign != 0]
    return int(np.sum(nonzero[1:] != nonzero[:-1])) if len(nonzero) else 0


def main() -> None:
    rows = []
    figure, axes = plt.subplots(2, 1, figsize=(10, 8), constrained_layout=True)
    specs = (
        ("T1 relaxation", "data_t1_exp.npy", "data_t1_fits.npy", 1000.0),
        ("Ramsey / T2*", "data_ramsey_exp.npy", "data_ramsey_fits.npy", 1000.0),
    )
    for ax, (family, data_name, fit_name, time_scale) in zip(axes, specs):
        data = np.load(SOURCE / data_name)
        fits = np.load(SOURCE / fit_name)
        for index, (mode, color) in enumerate(zip(MODES, COLORS)):
            t = data[index, 0] / time_scale
            y = data[index, 1]
            fit_t = fits[index, 0] / time_scale
            fit_y = fits[index, 1]
            x_data, x_fit_native = ara_map(y, fit_y)
            _, x_fit = ara_map(
                np.interp(t, fit_t, fit_y),
                fit_y,
            )
            # ara_map above returns a fit on its supplied grid; interpolate explicitly for scoring.
            low = float(np.min(fit_y))
            high = float(np.max(fit_y))
            if fit_y[0] >= fit_y[-1]:
                x_fit_at_data = 2 * (high - np.interp(t, fit_t, fit_y)) / (high - low)
            else:
                x_fit_at_data = 2 * (np.interp(t, fit_t, fit_y) - low) / (high - low)
            rows.append(
                {
                    "family": family,
                    "mode": mode,
                    "samples": len(t),
                    "time_min_us": float(t.min()),
                    "time_max_us": float(t.max()),
                    "ridge_crossings_published_fit": crossings(x_fit_native),
                    "ara_data_min": float(x_data.min()),
                    "ara_data_max": float(x_data.max()),
                    "ara_data_mean": float(x_data.mean()),
                    "ara_fit_mae": float(np.mean(np.abs(x_data - x_fit_at_data))),
                    "ara_fit_rmse": float(
                        np.sqrt(np.mean((x_data - x_fit_at_data) ** 2))
                    ),
                    "fraction_below_ridge": float(np.mean(x_data < 1)),
                    "fraction_above_ridge": float(np.mean(x_data > 1)),
                }
            )
            ax.scatter(t, x_data, s=10, alpha=0.32, color=color)
            ax.plot(fit_t, x_fit_native, lw=2, color=color, label=mode)
        ax.axhline(1.0, color="#e5e7eb", lw=1.2, ls="--", label="ARA ridge")
        ax.set_title(f"{family}: public data mapped to its published-fit 0–2 span")
        ax.set_ylabel("ARA coordinate")
        ax.set_ylim(-0.25, 2.25)
        ax.grid(alpha=0.18)
    axes[-1].set_xlabel("Time (µs)")
    axes[0].legend(ncol=4, fontsize=9, loc="upper right")
    figure.suptitle(
        "Real superconducting-qubit dynamics — descriptive ARA crosswalk",
        fontsize=14,
    )
    figure.savefig(FIG_OUT, dpi=180)
    plt.close(figure)

    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "status": "DESCRIPTIVE SECONDARY; NOT A FROZEN PREDICTIVE TEST",
        "source_doi": "10.5281/zenodo.14033026",
        "rows": rows,
        "boundary": (
            "The 0–2 span is calibrated from the source-supplied fit extrema. "
            "This demonstrates a readable coordinate crosswalk, not independent recovery "
            "of T1, T2*, or a new quantum law."
        ),
    }
    JSON_OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
