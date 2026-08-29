"""T425: older geometric/state Irrationality Di-ARA on T424 hourglass data.

This script does not re-extract video or refit the T424 instrument. It applies
the frozen radial/angular quotient to the existing held-out T424 ARA histories
and creates matched side-by-side visual comparisons.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
T424 = HERE.parent / "T424_hourglass_handover" / "results"
PROTOCOL = HERE / "T425_FROZEN_PROTOCOL.md"
EXPECTED_PROTOCOL_SHA256 = "BA48F5066E4B237031A7A25305A81EBD96F076B9B9CEE1F910531DBF4665AFFD"

EPS = 1e-12
N_BINS = 40
PHI = (1.0 + math.sqrt(5.0)) / 2.0
PHI_INV_SQ = PHI ** -2

DYNAMIC_NAMES = {
    0: "both-low",
    1: "connection-heavy",
    2: "movement-heavy",
    3: "both-high",
}
DYNAMIC_COLORS = {
    "both-low": "#9da8b6",
    "connection-heavy": "#d79a2b",
    "movement-heavy": "#4c78a8",
    "both-high": "#6f8f61",
}

SECTOR_NAMES = {
    0: "contracting reverse",
    1: "expanding reverse",
    2: "expanding forward",
    3: "contracting forward",
}
SECTOR_COLORS = {
    "contracting reverse": "#4c78a8",
    "expanding reverse": "#f28e2b",
    "expanding forward": "#6f8f61",
    "contracting forward": "#d88390",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def preclosure(group: pd.DataFrame) -> pd.DataFrame:
    group = group.sort_values("frame").reset_index(drop=True)
    closure = min(int(group["closure_index"].iloc[0]), len(group) - 1)
    return group.iloc[: closure + 1].copy().reset_index(drop=True)


def sector_from_ab(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    sector = np.full(len(a), -1, dtype=np.int8)
    good = np.isfinite(a) & np.isfinite(b) & (np.abs(a) > EPS) & (np.abs(b) > EPS)
    sector[good & (a < 0) & (b < 0)] = 0
    sector[good & (a > 0) & (b < 0)] = 1
    sector[good & (a > 0) & (b > 0)] = 2
    sector[good & (a < 0) & (b > 0)] = 3
    return sector


def geometric_transitions(group: pd.DataFrame, lag: int = 1) -> pd.DataFrame:
    history = preclosure(group)
    n = len(history)
    if lag < 1:
        raise ValueError("lag must be at least one frame")
    if n <= lag + 1:
        return pd.DataFrame()

    z = (history["x_trav"].to_numpy(float) - 1.0) + 1j * (
        history["x_conn"].to_numpy(float) - 1.0
    )
    radius = np.abs(z)
    cal_stop = max(2, int(math.floor(0.40 * n)))
    positive = radius[:cal_stop][np.isfinite(radius[:cal_stop]) & (radius[:cal_stop] > 0)]
    floor = max(EPS, float(np.quantile(positive, 0.05)) if len(positive) else EPS)

    valid = (
        np.isfinite(z[:-lag].real)
        & np.isfinite(z[:-lag].imag)
        & np.isfinite(z[lag:].real)
        & np.isfinite(z[lag:].imag)
        & (radius[:-lag] > floor)
        & (radius[lag:] > floor)
    )
    q = np.full(n - lag, np.nan + 1j * np.nan, dtype=np.complex128)
    q[valid] = z[lag:][valid] / z[:-lag][valid]
    s = np.abs(q)
    a = np.log(s)
    b = np.angle(q)
    x_radial = 2.0 * s / (1.0 + s)
    y_angular = 1.0 + b / math.pi
    sector = sector_from_ab(a, b)

    right = history.iloc[lag:].reset_index(drop=True)
    out = pd.DataFrame(
        {
            "video": right["video"],
            "run_id": right["run_id"],
            "gravity_index": right["gravity_index"].astype(int),
            "lag_frames": lag,
            "frame_left": history["frame"].iloc[:-lag].to_numpy(int),
            "frame_right": right["frame"].to_numpy(int),
            "run_time_s": right["run_time_s"].to_numpy(float),
            "history_fraction": np.arange(lag, n, dtype=float) / (n - 1),
            "radius_before": radius[:-lag],
            "radius_after": radius[lag:],
            "amplitude_floor": floor,
            "scale_ratio_s": s,
            "log_radial_a": a,
            "turn_delta_rad_b": b,
            "x_radial": x_radial,
            "y_angular": y_angular,
            "sector_id": sector,
            "valid_transition": valid & (sector >= 0),
        }
    )
    out["sector"] = [SECTOR_NAMES.get(int(value), "axis boundary") for value in sector]
    return out


def plot_scale_sensitivity(
    lag_points: dict[int, pd.DataFrame],
    lag_summaries: dict[int, dict[str, np.ndarray]],
    lag_occupancies: dict[int, dict[str, float]],
    path: Path,
) -> None:
    """Post-freeze scale view; it does not replace the lag-one primary result."""
    lags = list(lag_points)
    fig, axes = plt.subplots(2, len(lags), figsize=(5.0 * len(lags), 10.2), constrained_layout=True)
    fig.suptitle(
        "T425 scale sensitivity: the same geometric Di-ARA across longer time cuts",
        fontsize=20,
    )
    for column, lag in enumerate(lags):
        summary = lag_summaries[lag]
        points = lag_points[lag]
        occupancy = lag_occupancies[lag]

        ax = axes[0, column]
        f = summary["fraction"]
        ax.fill_between(f, summary["x_radial_lo"], summary["x_radial_hi"], color="#4c78a8", alpha=0.18)
        ax.plot(f, summary["x_radial"], color="#2f6ea5", linewidth=2.2, label="X radial")
        ax.fill_between(f, summary["y_angular_lo"], summary["y_angular_hi"], color="#f28e2b", alpha=0.18)
        ax.plot(f, summary["y_angular"], color="#d97400", linewidth=2.2, label="Y angular")
        ax.axhline(1.0, color="#555b62", linestyle="--", linewidth=1.0)
        ax.set_title(f"{lag}-frame relation\nmedian histories (zoomed)")
        ax.set_xlabel("Fraction of discharge-to-closure history")
        if column == 0:
            ax.set_ylabel("Geometric ARA coordinate\n(zoomed about ridge 1)")
        ax.set_ylim(0.82, 1.18)
        ax.grid(alpha=0.18)
        if column == len(lags) - 1:
            ax.legend(frameon=False, loc="best")

        ax = axes[1, column]
        sample = points.iloc[:: max(1, len(points) // 3000)]
        for name in SECTOR_NAMES.values():
            subset = sample[sample["sector"] == name]
            ax.scatter(
                subset["x_radial"], subset["y_angular"], s=8, alpha=0.22,
                color=SECTOR_COLORS[name], rasterized=True,
            )
        ax.plot(summary["x_radial"], summary["y_angular"], color="#23272d", linewidth=2.0)
        add_ridges(ax)
        ax.set_title(
            "\n".join(
                [
                    f"{lag}-frame quadrant plane",
                    f"EF {100*occupancy['expanding forward']:.1f}% · CR {100*occupancy['contracting reverse']:.1f}%",
                    f"ER {100*occupancy['expanding reverse']:.1f}% · CF {100*occupancy['contracting forward']:.1f}%",
                ]
            ),
            fontsize=11,
        )
        ax.set_xlabel("X radial: contraction ↔ expansion")
        if column == 0:
            ax.set_ylabel("Y angular: reverse ↔ forward")

    fig.text(
        0.5,
        0.003,
        "Post-freeze sensitivity only. All panels use the same T424 states and frozen quotient; only temporal separation changes.",
        ha="center",
        fontsize=10,
        color="#555555",
    )
    fig.savefig(path, dpi=170, facecolor="white")
    plt.close(fig)


def binned_run(
    fraction: np.ndarray, values: dict[str, np.ndarray], bins: int = N_BINS
) -> dict[str, np.ndarray]:
    edges = np.linspace(0.0, 1.0, bins + 1)
    centres = (edges[:-1] + edges[1:]) / 2.0
    result: dict[str, np.ndarray] = {"fraction": centres}
    indices = np.clip(np.digitize(fraction, edges, right=False) - 1, 0, bins - 1)
    for name, array in values.items():
        array = np.asarray(array, dtype=float)
        binned = np.full(bins, np.nan)
        for index in range(bins):
            selected = array[indices == index]
            selected = selected[np.isfinite(selected)]
            if len(selected):
                binned[index] = float(np.median(selected))
        result[name] = binned
    return result


def aggregate_binned(runs: list[dict[str, np.ndarray]], fields: list[str]) -> dict[str, np.ndarray]:
    result = {"fraction": runs[0]["fraction"]}
    for field in fields:
        stack = np.vstack([run[field] for run in runs])
        result[field] = np.nanmedian(stack, axis=0)
        result[f"{field}_lo"] = np.nanquantile(stack, 0.25, axis=0)
        result[f"{field}_hi"] = np.nanquantile(stack, 0.75, axis=0)
        result[f"{field}_n"] = np.sum(np.isfinite(stack), axis=0)
    return result


def mean_run_occupancy(rows: list[dict[str, object]], key: str, order: list[str]) -> dict[str, float]:
    frame = pd.DataFrame(rows)
    pivot = frame.pivot(index="run_id", columns=key, values="share").fillna(0.0)
    return {name: float(pivot[name].mean()) if name in pivot else 0.0 for name in order}


def add_ridges(ax: plt.Axes) -> None:
    ax.axvline(1.0, color="#555b62", linestyle="--", linewidth=1.15)
    ax.axhline(1.0, color="#555b62", linestyle="--", linewidth=1.15)
    ax.set(xlim=(0, 2), ylim=(0, 2))
    ax.set_aspect("equal", adjustable="box")
    ax.grid(alpha=0.15)


def plot_histories(
    dynamic: dict[str, np.ndarray], geometric: dict[str, np.ndarray], path: Path
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(16, 6.6), constrained_layout=True, sharey=True)
    fig.suptitle("Hourglass: two Irrationality Di-ARA history cuts", fontsize=20)

    ax = axes[0]
    f = dynamic["fraction"]
    ax.fill_between(f, dynamic["x_trav_lo"], dynamic["x_trav_hi"], color="#4c78a8", alpha=0.18)
    ax.plot(f, dynamic["x_trav"], color="#2f6ea5", linewidth=2.5, label="C1 movement / traversal")
    ax.fill_between(f, dynamic["x_conn_lo"], dynamic["x_conn_hi"], color="#d79a2b", alpha=0.18)
    ax.plot(f, dynamic["x_conn"], color="#d97400", linewidth=2.5, label="C2 connection / packing")
    ax.axhline(1.0, color="#555b62", linestyle="--", linewidth=1.15, label="ARA ridge")
    ax.set_title("T424 dynamic/state Di-ARA")
    ax.set_xlabel("Fraction of discharge-to-closure history")
    ax.set_ylabel("ARA coordinate (0–2)")
    ax.set_ylim(0, 2)
    ax.grid(alpha=0.18)
    ax.legend(frameon=False, loc="best")

    ax = axes[1]
    f = geometric["fraction"]
    ax.fill_between(f, geometric["x_radial_lo"], geometric["x_radial_hi"], color="#4c78a8", alpha=0.18)
    ax.plot(f, geometric["x_radial"], color="#2f6ea5", linewidth=2.5, label="X radial: contraction ↔ expansion")
    ax.fill_between(f, geometric["y_angular_lo"], geometric["y_angular_hi"], color="#f28e2b", alpha=0.18)
    ax.plot(f, geometric["y_angular"], color="#d97400", linewidth=2.5, label="Y angular: reverse ↔ forward")
    ax.axhline(1.0, color="#555b62", linestyle="--", linewidth=1.15, label="ARA ridge")
    ax.set_title("T425 geometric movement-of-state Di-ARA")
    ax.set_xlabel("Fraction of discharge-to-closure history")
    ax.grid(alpha=0.18)
    ax.legend(frameon=False, loc="best")

    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)


def plot_planes(
    dynamic_points: pd.DataFrame,
    geometric_points: pd.DataFrame,
    dynamic: dict[str, np.ndarray],
    geometric: dict[str, np.ndarray],
    dynamic_occupancy: dict[str, float],
    geometric_occupancy: dict[str, float],
    event_points: pd.DataFrame,
    path: Path,
) -> None:
    fig = plt.figure(figsize=(17, 11.2), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.26])
    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])]
    occ = fig.add_subplot(grid[1, :])
    fig.suptitle("Hourglass: side-by-side quadrant geometry", fontsize=20)

    ax = axes[0]
    sample = dynamic_points.iloc[:: max(1, len(dynamic_points) // 4500)]
    for name in DYNAMIC_NAMES.values():
        subset = sample[sample["quadrant_name"] == name]
        ax.scatter(subset["x_trav"], subset["x_conn"], s=9, alpha=0.22,
                   color=DYNAMIC_COLORS[name], label=name, rasterized=True)
    ax.plot(dynamic["x_trav"], dynamic["x_conn"], color="#23272d", linewidth=2.3,
            label="median history")
    add_ridges(ax)
    ax.set_title("T424: current state—movement × packing")
    ax.set_xlabel("C1 movement / traversal ARA (0–2)")
    ax.set_ylabel("C2 connection / packing ARA (0–2)")
    ax.legend(frameon=False, fontsize=9, loc="lower left")

    ax = axes[1]
    sample = geometric_points.iloc[:: max(1, len(geometric_points) // 4500)]
    for name in SECTOR_NAMES.values():
        subset = sample[sample["sector"] == name]
        ax.scatter(subset["x_radial"], subset["y_angular"], s=9, alpha=0.24,
                   color=SECTOR_COLORS[name], label=name, rasterized=True)
    ax.plot(geometric["x_radial"], geometric["y_angular"], color="#23272d", linewidth=2.3,
            label="median history")
    if len(event_points):
        ax.scatter(event_points["x_radial"], event_points["y_angular"], marker="x",
                   s=70, linewidth=1.8, color="#111111", label="direct events")
    radial_low = 2.0 / (1.0 + math.e)
    radial_high = 2.0 * math.e / (1.0 + math.e)
    angular_low = 1.0 - 2.0 * PHI_INV_SQ
    angular_high = 1.0 + 2.0 * PHI_INV_SQ
    for value in (radial_low, radial_high):
        ax.axvline(value, color="#777777", linestyle=":", linewidth=0.8, alpha=0.65)
    for value in (angular_low, angular_high):
        ax.axhline(value, color="#777777", linestyle=":", linewidth=0.8, alpha=0.65)
    add_ridges(ax)
    ax.set_title("T425: movement of state—radial × angular")
    ax.set_xlabel("X radial ARA: contraction ↔ expansion (0–2)")
    ax.set_ylabel("Y angular ARA: reverse ↔ forward (0–2)")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    ax.text(1.98, 0.03, "dotted = historical e / reciprocal-φ references\n(not gates)",
            ha="right", va="bottom", fontsize=8.5, color="#555555")

    y_positions = [1, 0]
    bar_height = 0.55
    left = 0.0
    for name in DYNAMIC_NAMES.values():
        value = dynamic_occupancy[name]
        occ.barh(y_positions[0], value, left=left, height=bar_height,
                 color=DYNAMIC_COLORS[name], edgecolor="white", linewidth=1)
        if value >= 0.055:
            occ.text(left + value / 2, y_positions[0], f"{name}\n{100*value:.1f}%",
                     ha="center", va="center", fontsize=9,
                     color="white" if name in {"movement-heavy", "both-high"} else "#18202a")
        left += value
    left = 0.0
    for name in SECTOR_NAMES.values():
        value = geometric_occupancy[name]
        occ.barh(y_positions[1], value, left=left, height=bar_height,
                 color=SECTOR_COLORS[name], edgecolor="white", linewidth=1)
        if value >= 0.055:
            occ.text(left + value / 2, y_positions[1], f"{name}\n{100*value:.1f}%",
                     ha="center", va="center", fontsize=9, color="white" if name != "expanding reverse" else "#18202a")
        left += value
    occ.set_xlim(0, 1)
    occ.set_yticks(y_positions, ["T424 state", "T425 movement of state"])
    occ.set_xlabel("Equal-run mean share of eligible pre-closure observations")
    occ.set_title("Quadrant / sector occupancy")
    occ.grid(axis="x", alpha=0.15)

    fig.savefig(path, dpi=180, facecolor="white")
    plt.close(fig)


def plot_full(
    histories_path: Path, planes_path: Path, output_path: Path
) -> None:
    from PIL import Image, ImageOps, ImageDraw

    history = Image.open(histories_path).convert("RGB")
    planes = Image.open(planes_path).convert("RGB")
    width = max(history.width, planes.width)
    if history.width != width:
        history = ImageOps.pad(history, (width, round(history.height * width / history.width)), color="white")
    if planes.width != width:
        planes = ImageOps.pad(planes, (width, round(planes.height * width / planes.width)), color="white")
    gap = 26
    canvas = Image.new("RGB", (width, history.height + gap + planes.height), "white")
    canvas.paste(history, (0, 0))
    canvas.paste(planes, (0, history.height + gap))
    draw = ImageDraw.Draw(canvas)
    draw.line((40, history.height + gap // 2, width - 40, history.height + gap // 2), fill="#d9d3c6", width=2)
    canvas.save(output_path, quality=95)


def main() -> None:
    if sha256(PROTOCOL) != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError("Frozen T425 protocol hash mismatch")
    RESULTS.mkdir(parents=True, exist_ok=True)

    frame = pd.read_csv(T424 / "T424_HOLDOUT_ARA_COORDINATES.csv")
    events = pd.read_csv(T424 / "T424_HOLDOUT_DIRECT_EVENTS.csv")

    geometric_runs: list[pd.DataFrame] = []
    dynamic_binned: list[dict[str, np.ndarray]] = []
    geometric_binned: list[dict[str, np.ndarray]] = []
    dynamic_occ_rows: list[dict[str, object]] = []
    geometric_occ_rows: list[dict[str, object]] = []
    dynamic_point_runs: list[pd.DataFrame] = []

    for run_id, group in frame.groupby("run_id", sort=False):
        history = preclosure(group)
        fraction = np.linspace(0.0, 1.0, len(history))
        dynamic_binned.append(
            binned_run(
                fraction,
                {
                    "x_trav": history["x_trav"].to_numpy(float),
                    "x_conn": history["x_conn"].to_numpy(float),
                },
            )
        )
        dynamic_point = history[["run_id", "frame", "x_trav", "x_conn", "quadrant"]].copy()
        dynamic_point["quadrant_name"] = [DYNAMIC_NAMES[int(value)] for value in dynamic_point["quadrant"]]
        dynamic_point_runs.append(dynamic_point)
        dynamic_shares = dynamic_point["quadrant_name"].value_counts(normalize=True)
        for name in DYNAMIC_NAMES.values():
            dynamic_occ_rows.append({"run_id": run_id, "quadrant_name": name, "share": float(dynamic_shares.get(name, 0.0))})

        geo = geometric_transitions(history)
        if geo.empty:
            continue
        eligible = geo[geo["valid_transition"]].copy()
        geometric_runs.append(eligible)
        geometric_binned.append(
            binned_run(
                eligible["history_fraction"].to_numpy(float),
                {
                    "x_radial": eligible["x_radial"].to_numpy(float),
                    "y_angular": eligible["y_angular"].to_numpy(float),
                },
            )
        )
        geometric_shares = eligible["sector"].value_counts(normalize=True)
        for name in SECTOR_NAMES.values():
            geometric_occ_rows.append({"run_id": run_id, "sector": name, "share": float(geometric_shares.get(name, 0.0))})

    if len(geometric_runs) != frame["run_id"].nunique():
        raise RuntimeError("At least one holdout run produced no eligible geometric transitions")

    dynamic_points = pd.concat(dynamic_point_runs, ignore_index=True)
    geometric_points = pd.concat(geometric_runs, ignore_index=True)
    dynamic_summary = aggregate_binned(dynamic_binned, ["x_trav", "x_conn"])
    geometric_summary = aggregate_binned(geometric_binned, ["x_radial", "y_angular"])

    dynamic_order = list(DYNAMIC_NAMES.values())
    geometric_order = list(SECTOR_NAMES.values())
    dynamic_occupancy = mean_run_occupancy(dynamic_occ_rows, "quadrant_name", dynamic_order)
    geometric_occupancy = mean_run_occupancy(geometric_occ_rows, "sector", geometric_order)

    event_rows: list[dict[str, object]] = []
    for event in events.to_dict("records"):
        candidates = geometric_points[
            (geometric_points["run_id"] == event["run_id"])
            & (geometric_points["frame_right"] <= int(event["frame"]))
        ]
        if len(candidates):
            row = candidates.iloc[-1]
            event_rows.append(
                {
                    **event,
                    "transition_frame": int(row["frame_right"]),
                    "x_radial": float(row["x_radial"]),
                    "y_angular": float(row["y_angular"]),
                    "sector": str(row["sector"]),
                }
            )
    event_points = pd.DataFrame(event_rows)

    geometric_points.to_csv(RESULTS / "T425_HOLDOUT_GEOMETRIC_COORDINATES.csv", index=False)
    pd.DataFrame(dynamic_occ_rows).to_csv(RESULTS / "T425_T424_DYNAMIC_QUADRANT_OCCUPANCY.csv", index=False)
    pd.DataFrame(geometric_occ_rows).to_csv(RESULTS / "T425_GEOMETRIC_SECTOR_OCCUPANCY.csv", index=False)
    event_points.to_csv(RESULTS / "T425_DIRECT_EVENT_GEOMETRIC_COORDINATES.csv", index=False)

    histories_path = RESULTS / "T425_MEDIAN_HISTORIES_SIDE_BY_SIDE.png"
    planes_path = RESULTS / "T425_QUADRANT_PLANES_SIDE_BY_SIDE.png"
    plot_histories(dynamic_summary, geometric_summary, histories_path)
    plot_planes(
        dynamic_points,
        geometric_points,
        dynamic_summary,
        geometric_summary,
        dynamic_occupancy,
        geometric_occupancy,
        event_points,
        planes_path,
    )
    plot_full(histories_path, planes_path, RESULTS / "T425_FULL_SIDE_BY_SIDE.png")

    # The frozen primary test is the one-frame quotient above. Because these
    # videos are sampled densely relative to the smoothed T424 state, retain
    # that answer and separately expose how the same quotient behaves over
    # longer, predeclared temporal separations. No lag is selected as a winner.
    sensitivity_lags = [1, 3, 6, 12]
    sensitivity_points: dict[int, pd.DataFrame] = {}
    sensitivity_summaries: dict[int, dict[str, np.ndarray]] = {}
    sensitivity_occupancies: dict[int, dict[str, float]] = {}
    sensitivity_rows: list[dict[str, object]] = []
    for lag in sensitivity_lags:
        lag_runs: list[pd.DataFrame] = []
        lag_binned: list[dict[str, np.ndarray]] = []
        lag_occ_rows: list[dict[str, object]] = []
        for run_id, group in frame.groupby("run_id", sort=False):
            lag_geo = geometric_transitions(group, lag=lag)
            eligible = lag_geo[lag_geo["valid_transition"]].copy()
            if eligible.empty:
                continue
            lag_runs.append(eligible)
            lag_binned.append(
                binned_run(
                    eligible["history_fraction"].to_numpy(float),
                    {
                        "x_radial": eligible["x_radial"].to_numpy(float),
                        "y_angular": eligible["y_angular"].to_numpy(float),
                    },
                )
            )
            shares = eligible["sector"].value_counts(normalize=True)
            for name in geometric_order:
                share = float(shares.get(name, 0.0))
                lag_occ_rows.append({"lag_frames": lag, "run_id": run_id, "sector": name, "share": share})
                sensitivity_rows.append({"lag_frames": lag, "run_id": run_id, "sector": name, "share": share})
        if not lag_runs:
            raise RuntimeError(f"No eligible transitions for sensitivity lag {lag}")
        sensitivity_points[lag] = pd.concat(lag_runs, ignore_index=True)
        sensitivity_summaries[lag] = aggregate_binned(lag_binned, ["x_radial", "y_angular"])
        sensitivity_occupancies[lag] = mean_run_occupancy(lag_occ_rows, "sector", geometric_order)

    pd.DataFrame(sensitivity_rows).to_csv(RESULTS / "T425_SCALE_SENSITIVITY_OCCUPANCY.csv", index=False)
    plot_scale_sensitivity(
        sensitivity_points,
        sensitivity_summaries,
        sensitivity_occupancies,
        RESULTS / "T425_GEOMETRIC_SCALE_SENSITIVITY.png",
    )

    coverage = {}
    occ_frame = pd.DataFrame(geometric_occ_rows)
    for name in geometric_order:
        coverage[name] = int((occ_frame[occ_frame["sector"] == name]["share"] > 0).sum())
    pivot = occ_frame.pivot(index="run_id", columns="sector", values="share").fillna(0.0)
    all_four = int((pivot.reindex(columns=geometric_order, fill_value=0.0) > 0).all(axis=1).sum())
    all_four_one_percent = int((pivot.reindex(columns=geometric_order, fill_value=0.0) >= 0.01).all(axis=1).sum())

    summary = {
        "status": "DESCRIPTIVE_INSTRUMENT_COMPARISON",
        "protocol_sha256": EXPECTED_PROTOCOL_SHA256,
        "runs": int(frame["run_id"].nunique()),
        "t424_dynamic_equal_run_mean_occupancy": dynamic_occupancy,
        "t425_geometric_equal_run_mean_occupancy": geometric_occupancy,
        "t425_valid_transitions": int(len(geometric_points)),
        "t425_sector_run_coverage": coverage,
        "runs_with_all_four_geometric_sectors": all_four,
        "runs_with_each_geometric_sector_at_least_one_percent": all_four_one_percent,
        "direct_events_with_prior_geometric_state": int(len(event_points)),
        "median_direct_event_x_radial": float(event_points["x_radial"].median()) if len(event_points) else None,
        "median_direct_event_y_angular": float(event_points["y_angular"].median()) if len(event_points) else None,
        "historical_reference_coordinates": {
            "radial_1_over_e": 2.0 / (1.0 + math.e),
            "radial_e": 2.0 * math.e / (1.0 + math.e),
            "angular_reverse_phi_inverse_squared": 1.0 - 2.0 * PHI_INV_SQ,
            "angular_forward_phi_inverse_squared": 1.0 + 2.0 * PHI_INV_SQ,
        },
        "postfreeze_scale_sensitivity_equal_run_mean_occupancy": {
            str(lag): occupancy for lag, occupancy in sensitivity_occupancies.items()
        },
        "interpretation_boundary": "Exact geometric re-expression; four-sector occupancy alone is descriptive, not proof.",
    }
    (RESULTS / "T425_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
