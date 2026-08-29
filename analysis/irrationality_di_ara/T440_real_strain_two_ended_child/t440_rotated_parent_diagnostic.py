"""Geometry-only diagnostic for the frozen T440 parent coordinates.

This companion does not change the T440 protocol or verdict.  It rotates the
two independently constructed parents into fixed ARA directions:

    exchange = (Space - Time) / sqrt(2)       # along a slope -1 band
    common   = (Space + Time - 2) / sqrt(2)   # perpendicular to that band

The purpose is to determine which direction contains the observed variation
and where the published event GPS sits in that rotated geometry.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
HISTORIES = RESULTS / "T440_EVENT_HISTORIES.csv"
OUT_PNG = RESULTS / "T440_ROTATED_PARENT_DIAGNOSTIC.png"
OUT_JSON = RESULTS / "T440_ROTATED_PARENT_DIAGNOSTIC.json"
OUT_CSV = RESULTS / "T440_ROTATED_PARENT_COMMON_GRID.csv"


def q(arr: np.ndarray, p: float, axis: int = 0) -> np.ndarray:
    return np.nanquantile(arr, p, axis=axis)


def first_zero_bracket(t: np.ndarray, y: np.ndarray, after: float = -0.02):
    valid = np.flatnonzero(t >= after)
    for left, right in zip(valid[:-1], valid[1:]):
        if y[left] == 0 or y[left] * y[right] < 0:
            return [float(t[left]), float(t[right])]
    return None


def main() -> None:
    df = pd.read_csv(HISTORIES)
    df = df[df["role"].str.startswith("locked_evaluation")].copy()
    keys = ["event", "detector"]
    groups = list(df.groupby(keys, sort=True))

    grid = np.linspace(-0.32, 0.08, 103)
    space_rows, time_rows = [], []
    per_stream = []
    for (event, detector), g in groups:
        g = g.sort_values("time_s")
        t = g["time_s"].to_numpy(float)
        ps = np.interp(grid, t, g["p_space"].to_numpy(float))
        pt = np.interp(grid, t, g["p_time"].to_numpy(float))
        exchange = (ps - pt) / np.sqrt(2.0)
        common = (ps + pt - 2.0) / np.sqrt(2.0)
        vx = float(np.var(exchange, ddof=1))
        vc = float(np.var(common, ddof=1))
        per_stream.append(
            {
                "event": event,
                "detector": detector,
                "exchange_variance": vx,
                "common_variance": vc,
                "exchange_to_common_variance_ratio": vx / vc if vc else np.inf,
            }
        )
        space_rows.append(ps)
        time_rows.append(pt)

    space = np.asarray(space_rows)
    time = np.asarray(time_rows)
    exchange = (space - time) / np.sqrt(2.0)
    common = (space + time - 2.0) / np.sqrt(2.0)
    med_s, med_t = np.median(space, axis=0), np.median(time, axis=0)
    med_x, med_c = np.median(exchange, axis=0), np.median(common, axis=0)

    pooled = df[["p_time", "p_space"]].to_numpy(float)
    covariance = np.cov(pooled.T)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues, eigenvectors = eigenvalues[order], eigenvectors[:, order]
    pc = eigenvectors[:, 0]
    if pc[0] < 0:
        pc = -pc
    pc_angle = float(np.degrees(np.arctan2(pc[1], pc[0])))
    inverse_axis = np.array([1.0, -1.0]) / np.sqrt(2.0)
    angle_to_inverse = float(
        np.degrees(np.arccos(np.clip(abs(np.dot(pc, inverse_axis)), 0, 1)))
    )

    index_gps = int(np.argmin(abs(grid)))
    crossing = first_zero_bracket(grid, med_x, after=-0.02)
    stream_frame = pd.DataFrame(per_stream)
    summary = {
        "purpose": "post-hoc geometry diagnostic; does not alter frozen T440",
        "locked_streams": len(groups),
        "pooled_principal_axis_angle_degrees_from_positive_time_axis": pc_angle,
        "principal_axis_angle_degrees_from_exact_inverse_band": angle_to_inverse,
        "principal_to_secondary_variance_ratio": float(eigenvalues[0] / eigenvalues[1]),
        "median_stream_exchange_to_common_variance_ratio": float(
            stream_frame["exchange_to_common_variance_ratio"].median()
        ),
        "streams_exchange_variance_greater_than_common": int(
            (stream_frame["exchange_variance"] > stream_frame["common_variance"]).sum()
        ),
        "at_nearest_published_gps_time_s": float(grid[index_gps]),
        "at_gps_median_space_parent": float(med_s[index_gps]),
        "at_gps_median_time_parent": float(med_t[index_gps]),
        "at_gps_median_exchange_coordinate": float(med_x[index_gps]),
        "at_gps_median_common_coordinate": float(med_c[index_gps]),
        "post_gps_exchange_zero_crossing_bracket_s": crossing,
    }

    common_grid = pd.DataFrame(
        {
            "time_s": grid,
            "space_q25": q(space, 0.25),
            "space_median": med_s,
            "space_q75": q(space, 0.75),
            "time_q25": q(time, 0.25),
            "time_median": med_t,
            "time_q75": q(time, 0.75),
            "exchange_q25": q(exchange, 0.25),
            "exchange_median": med_x,
            "exchange_q75": q(exchange, 0.75),
            "common_q25": q(common, 0.25),
            "common_median": med_c,
            "common_q75": q(common, 0.75),
        }
    )
    common_grid.to_csv(OUT_CSV, index=False)
    OUT_JSON.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), constrained_layout=True)
    fig.patch.set_facecolor("#08111f")
    for ax in axes.flat:
        ax.set_facecolor("#0c1626")
        ax.grid(alpha=0.16)

    ax = axes[0, 0]
    hb = ax.hexbin(
        df["p_time"], df["p_space"], gridsize=34, extent=(0, 2, 0, 2),
        mincnt=1, bins="log", cmap="magma"
    )
    ax.axhline(1, color="white", ls=":", alpha=0.65)
    ax.axvline(1, color="white", ls=":", alpha=0.65)
    center = pooled.mean(axis=0)
    scale = 0.95
    ax.plot(
        center[0] + np.array([-1, 1]) * pc[0] * scale,
        center[1] + np.array([-1, 1]) * pc[1] * scale,
        color="#22d3a7", lw=3, label=f"pooled principal direction ({pc_angle:.1f}°)"
    )
    ax.plot([0, 2], [2, 0], color="#60a5fa", lw=1.5, ls="--", label="exact inverse direction")
    ax.set(xlim=(0, 2), ylim=(0, 2), xlabel="Time/Movement parent", ylabel="Space/Connection parent")
    ax.set_title("Observed parent plane and its dominant orientation")
    ax.legend(loc="lower left", fontsize=8)
    fig.colorbar(hb, ax=ax, label="log point count")

    ax = axes[0, 1]
    ax.fill_between(grid, q(exchange, 0.25), q(exchange, 0.75), color="#f59e0b", alpha=0.23)
    ax.plot(grid, med_x, color="#f59e0b", lw=2.4, label="exchange: (Space − Time)/√2")
    ax.fill_between(grid, q(common, 0.25), q(common, 0.75), color="#60a5fa", alpha=0.20)
    ax.plot(grid, med_c, color="#60a5fa", lw=2.4, label="common/perpendicular: (Space + Time − 2)/√2")
    ax.axhline(0, color="white", ls=":", alpha=0.65)
    ax.axvline(0, color="#f472b6", ls="--", label="published event GPS")
    if crossing:
        ax.axvspan(crossing[0], crossing[1], color="#22d3a7", alpha=0.25, label="exchange ordering reversal")
    ax.set(xlabel="Seconds relative to published event GPS", ylabel="Rotated parent coordinate")
    ax.set_title("The inverse-band direction carries the dominant event-aligned excursion")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    for i, ((event, detector), _) in enumerate(groups):
        ax.plot(common[i], exchange[i], alpha=0.30, lw=0.9)
        ax.scatter(common[i, index_gps], exchange[i, index_gps], s=10, alpha=0.55)
    ax.axhline(0, color="white", ls=":", alpha=0.65)
    ax.axvline(0, color="white", ls=":", alpha=0.65)
    ax.set(xlabel="Common/perpendicular coordinate", ylabel="Exchange/along-band coordinate")
    ax.set_title("Individual temporal paths after rotating the parent plane\n(points mark published GPS)")

    ax = axes[1, 1]
    ratios = stream_frame["exchange_to_common_variance_ratio"].to_numpy()
    colors = ["#60a5fa" if d == "H1" else "#f59e0b" for d in stream_frame["detector"]]
    ax.scatter(np.arange(len(ratios)), ratios, c=colors, s=48)
    ax.axhline(1, color="white", ls=":", alpha=0.7, label="equal variance")
    ax.axhline(np.median(ratios), color="#22d3a7", ls="--", label=f"median {np.median(ratios):.2f}")
    ax.set_yscale("log")
    ax.set(xlabel="Locked detector stream", ylabel="Variance along band / variance perpendicular")
    ax.set_title("How strongly each record is viewed along the inverse band")
    ax.legend(fontsize=8)

    fig.suptitle(
        "T440 rotated-parent diagnostic — traversal direction versus perpendicular pressure",
        fontsize=18, fontweight="bold"
    )
    fig.savefig(OUT_PNG, dpi=190, facecolor=fig.get_facecolor())
    plt.close(fig)

    print(json.dumps(summary, indent=2))
    print(OUT_PNG)


if __name__ == "__main__":
    main()
