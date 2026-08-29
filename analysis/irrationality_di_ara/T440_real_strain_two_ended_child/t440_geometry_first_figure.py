"""Build a geometry-first companion figure for T440.

The frozen gates remain in the registered result.  This companion deliberately
answers a different question first: what shape did the independently derived
Space/Connection and Time/Movement coordinates actually make?
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def _common_histories(histories: pd.DataFrame) -> pd.DataFrame:
    grid = np.linspace(-0.32, 0.08, 103)
    rows: list[dict[str, float | str]] = []
    fields = ("p_space", "p_time", "e_space", "e_time")
    for field in fields:
        curves = []
        for _, group in histories.groupby(["event", "detector"], sort=False):
            group = group.sort_values("time_s")
            curves.append(np.interp(grid, group.time_s, group[field]))
        values = np.vstack(curves)
        for t, q25, median, q75 in zip(
            grid,
            np.quantile(values, 0.25, axis=0),
            np.median(values, axis=0),
            np.quantile(values, 0.75, axis=0),
        ):
            rows.append(
                {
                    "field": field,
                    "time_s": float(t),
                    "q25": float(q25),
                    "median": float(median),
                    "q75": float(q75),
                }
            )
    return pd.DataFrame(rows)


def _occupancy_fraction(x: np.ndarray, y: np.ndarray, bins: int = 20) -> float:
    counts, _, _ = np.histogram2d(x, y, bins=bins, range=((0, 2), (0, 2)))
    return float(np.mean(counts > 0))


def main() -> None:
    histories = pd.read_csv(RESULTS / "T440_EVENT_HISTORIES.csv")
    histories = histories[histories.role.str.startswith("locked")].copy()
    detector = pd.read_csv(RESULTS / "T440_DETECTOR_RESULTS.csv")
    detector = detector[detector.role.str.startswith("locked")].copy()
    controls = pd.read_csv(RESULTS / "T440_OFFSOURCE_CONTROLS.csv")
    null = pd.read_csv(RESULTS / "T440_WRONG_EVENT_NULL.csv").iloc[:, 0].to_numpy()
    result = json.loads((RESULTS / "T440_RESULTS.json").read_text(encoding="utf-8"))

    stream_rows = []
    for (event, det), group in histories.groupby(["event", "detector"], sort=True):
        stream_rows.append(
            {
                "event": event,
                "detector": det,
                "parent_spearman": float(group.p_space.corr(group.p_time, method="spearman")),
                "parent_sum_std": float((group.p_space + group.p_time).std(ddof=0)),
                "parent_sum_mean": float((group.p_space + group.p_time).mean()),
            }
        )
    streams = pd.DataFrame(stream_rows)
    common = _common_histories(histories)

    median_parent = common[common.field.isin(["p_space", "p_time"])].pivot(
        index="time_s", columns="field", values="median"
    ).sort_index()
    parent_difference = median_parent.p_space - median_parent.p_time
    post_peak = parent_difference.loc[parent_difference.idxmax():]
    sign_change = np.flatnonzero(
        np.signbit(post_peak.to_numpy()[:-1]) != np.signbit(post_peak.to_numpy()[1:])
    )
    first_post_peak_crossing = None
    if len(sign_change):
        i = int(sign_change[0])
        first_post_peak_crossing = [
            float(post_peak.index[i]),
            float(post_peak.index[i + 1]),
        ]

    event_quadrants = detector.quadrant.value_counts()
    control_quadrants = controls.quadrant.value_counts()
    quadrants = ["S+/T+", "S+/T-", "S-/T+", "S-/T-"]

    summary = {
        "purpose": "descriptive ARA geometry companion; does not alter frozen T440 gates",
        "locked_events": int(histories.event.nunique()),
        "locked_detector_streams": int(len(streams)),
        "history_points": int(len(histories)),
        "parent_spearman_median": float(streams.parent_spearman.median()),
        "parent_spearman_min": float(streams.parent_spearman.min()),
        "parent_spearman_max": float(streams.parent_spearman.max()),
        "negative_parent_spearman_streams": int((streams.parent_spearman < 0).sum()),
        "parent_sum_std_median": float(streams.parent_sum_std.median()),
        "parent_sum_std_min": float(streams.parent_sum_std.min()),
        "parent_sum_std_max": float(streams.parent_sum_std.max()),
        "event_aligned_parent_difference_peak_time_s": float(parent_difference.idxmax()),
        "event_aligned_parent_difference_peak": float(parent_difference.max()),
        "event_aligned_parent_difference_min_time_s": float(parent_difference.idxmin()),
        "event_aligned_parent_difference_min": float(parent_difference.min()),
        "first_post_peak_parent_crossing_bracket_s": first_post_peak_crossing,
        "parent_plane_20x20_occupancy": _occupancy_fraction(histories.p_time.to_numpy(), histories.p_space.to_numpy()),
        "child_plane_20x20_occupancy": _occupancy_fraction(histories.e_time.to_numpy(), histories.e_space.to_numpy()),
        "event_opposing_quadrant_fraction": float(detector.quadrant.isin(["S+/T-", "S-/T+"]).mean()),
        "offsource_opposing_quadrant_fraction": float(controls.quadrant.isin(["S+/T-", "S-/T+"]).mean()),
        "correct_record_median_overlap": float(result["correct_event_median_overlap"]),
        "wrong_event_empirical_p": float(result["wrong_event_empirical_p"]),
    }
    (RESULTS / "T440_GEOMETRY_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    streams.to_csv(RESULTS / "T440_STREAM_GEOMETRY.csv", index=False)
    common.to_csv(RESULTS / "T440_COMMON_GEOMETRY.csv", index=False)

    plt.style.use("dark_background")
    fig, axes = plt.subplots(3, 2, figsize=(18, 19))
    fig.patch.set_facecolor("#0b1220")
    fig.subplots_adjust(left=0.07, right=0.95, top=0.945, bottom=0.09, hspace=0.30, wspace=0.25)
    for ax in axes.flat:
        ax.set_facecolor("#111827")
        ax.grid(color="#64748b", alpha=0.18)

    hb = axes[0, 0].hexbin(
        histories.p_time,
        histories.p_space,
        gridsize=28,
        extent=(0, 2, 0, 2),
        mincnt=1,
        bins="log",
        cmap="magma",
    )
    axes[0, 0].axvline(1, color="white", ls=":", lw=1.4)
    axes[0, 0].axhline(1, color="white", ls=":", lw=1.4)
    axes[0, 0].set(
        title="Parent Di-ARA occupancy: persistent inverse band, not a forced mirror",
        xlabel="Time/Movement parent (derived ARA 0–2)",
        ylabel="Space/Connection parent (derived ARA 0–2)",
        xlim=(0, 2),
        ylim=(0, 2),
    )
    fig.colorbar(hb, ax=axes[0, 0], label="log point count")

    hc = axes[0, 1].hexbin(
        histories.e_time,
        histories.e_space,
        gridsize=28,
        extent=(0, 2, 0, 2),
        mincnt=1,
        bins="log",
        cmap="viridis",
    )
    axes[0, 1].axvline(1, color="white", ls=":", lw=1.4)
    axes[0, 1].axhline(1, color="white", ls=":", lw=1.4)
    axes[0, 1].set(
        title="Child-side plane: broad, edge-rich transition texture",
        xlabel="Child cut from Time end (derived ARA 0–2)",
        ylabel="Child cut from Space end (derived ARA 0–2)",
        xlim=(0, 2),
        ylim=(0, 2),
    )
    fig.colorbar(hc, ax=axes[0, 1], label="log point count")

    colors = {"p_space": "#f59e0b", "p_time": "#60a5fa"}
    labels = {"p_space": "Space/Connection parent", "p_time": "Time/Movement parent"}
    for field in ("p_space", "p_time"):
        part = common[common.field == field]
        axes[1, 0].fill_between(part.time_s, part.q25, part.q75, color=colors[field], alpha=0.18)
        axes[1, 0].plot(part.time_s, part["median"], color=colors[field], lw=2.4, label=labels[field])
    axes[1, 0].axhline(1, color="white", ls=":", lw=1.4, label="ARA ridge 1.0")
    axes[1, 0].axvline(0, color="#f472b6", ls="--", lw=1.4, label="published event GPS")
    axes[1, 0].set(
        title="Event-aligned parent histories: median and interquartile envelope",
        xlabel="Seconds relative to published event GPS",
        ylabel="Parent ARA coordinate (0–2)",
        xlim=(-0.32, 0.08),
        ylim=(0, 2),
    )
    axes[1, 0].legend(loc="best")

    detector_colors = {"H1": "#60a5fa", "L1": "#f59e0b"}
    for det, group in streams.groupby("detector"):
        axes[1, 1].scatter(
            group.parent_spearman,
            group.parent_sum_std,
            s=70,
            alpha=0.85,
            color=detector_colors.get(det, "white"),
            label=f"{det} stream",
        )
    axes[1, 1].axvline(0, color="white", ls=":", lw=1.4)
    axes[1, 1].axvline(streams.parent_spearman.median(), color="#22c55e", ls="--", lw=1.8,
                       label=f"median correlation {streams.parent_spearman.median():.3f}")
    axes[1, 1].set(
        title="Stream geometry: inverse tendency with variable closure sum",
        xlabel="Within-stream Spearman(Space parent, Time parent)",
        ylabel="Standard deviation of Space + Time (ARA units)",
    )
    axes[1, 1].legend(loc="best")

    axes[2, 0].hist(null, bins=35, color="#64748b", alpha=0.8, label="wrong-event pairings")
    axes[2, 0].axvline(result["correct_event_median_overlap"], color="#22c55e", lw=3,
                       label=f"same-record median {result['correct_event_median_overlap']:.4f}")
    axes[2, 0].set(
        title="Same-record Space/Time histories retain a specific relational identity",
        xlabel="Median Bhattacharyya history overlap",
        ylabel="Permutation count",
    )
    axes[2, 0].legend(loc="best")

    x = np.arange(len(quadrants))
    event_fraction = np.array([event_quadrants.get(q, 0) for q in quadrants], dtype=float) / len(detector)
    control_fraction = np.array([control_quadrants.get(q, 0) for q in quadrants], dtype=float) / len(controls)
    width = 0.37
    axes[2, 1].bar(x - width / 2, event_fraction, width, color="#60a5fa", label="event windows")
    axes[2, 1].bar(x + width / 2, control_fraction, width, color="#f59e0b", label="off-source windows")
    axes[2, 1].set_xticks(x, quadrants)
    axes[2, 1].set(
        title="Opposing push/pull occupies both event and background histories",
        xlabel="Signed parent-derivative quadrant at joint maximum",
        ylabel="Fraction of windows",
        ylim=(0, 0.7),
    )
    axes[2, 1].legend(loc="best")

    fig.suptitle(
        "T440 geometry-first reading — real H1/L1 strain, 10 locked events / 20 detector streams",
        fontsize=22,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.018,
        "Geometry retained: a persistent record-specific inverse Space/Time relation is visible, while the "
        "magnitude-derived child remains broad.\n"
        "Benchmark only: the frozen child-localization gates are recorded separately and do not erase these shapes.",
        ha="center",
        va="bottom",
        fontsize=12,
        color="#d1d5db",
    )
    out = RESULTS / "T440_GEOMETRY_FIRST.png"
    fig.savefig(out, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(json.dumps({"figure": str(out), "summary": summary}, indent=2))


if __name__ == "__main__":
    main()
