"""Post-hoc descriptive summary for the already-scored T424 holdout.

This does not alter the frozen model or primary gates. It translates the
holdout into readable ARA trajectory, event-position, and forecast summaries.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def quantile_curves(curves: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    stack = np.vstack(curves)
    return (
        np.nanmedian(stack, axis=0),
        np.nanquantile(stack, 0.25, axis=0),
        np.nanquantile(stack, 0.75, axis=0),
    )


def main() -> None:
    frame = pd.read_csv(RESULTS / "T424_HOLDOUT_ARA_COORDINATES.csv")
    events = pd.read_csv(RESULTS / "T424_HOLDOUT_DIRECT_EVENTS.csv")
    leads = pd.read_csv(RESULTS / "T424_HOLDOUT_WARNING_LEADS.csv")
    metrics = pd.read_csv(RESULTS / "T424_HOLDOUT_MODEL_METRICS.csv")
    outcome = json.loads((RESULTS / "T424_HOLDOUT_OUTCOME.json").read_text(encoding="utf-8"))

    event_join = events.merge(
        frame[["run_id", "frame", "x_trav", "x_conn", "s_joint", "d_eq", "quadrant"]],
        on=["run_id", "frame"],
        how="left",
    )
    event_join.to_csv(RESULTS / "T424_HOLDOUT_EVENT_ARA_COORDINATES.csv", index=False)

    grid = np.linspace(0.0, 1.0, 101)
    trav_curves: list[np.ndarray] = []
    conn_curves: list[np.ndarray] = []
    crossing_runs = 0
    quadrant_rows: list[dict[str, object]] = []
    onset_rows: list[dict[str, float | str | int]] = []
    sequence_rows: list[dict[str, str]] = []
    sequence_names = {
        0: "both-low",
        1: "connection-heavy",
        2: "movement-heavy",
        3: "both-high",
    }

    for run_id, group in frame.groupby("run_id", sort=False):
        group = group.reset_index(drop=True)
        closure = min(int(group["closure_index"].iloc[0]), len(group) - 1)
        history = group.iloc[: closure + 1].copy()
        native = np.linspace(0.0, 1.0, len(history))
        trav_curves.append(np.interp(grid, native, history["x_trav"]))
        conn_curves.append(np.interp(grid, native, history["x_conn"]))

        difference = history["x_trav"].to_numpy() - history["x_conn"].to_numpy()
        crossing_runs += int(np.any(np.signbit(difference[:-1]) != np.signbit(difference[1:])))

        quadrant = history["quadrant"].astype(int).to_numpy()
        compressed = quadrant[np.r_[True, quadrant[1:] != quadrant[:-1]]]
        sequence_rows.append(
            {
                "run_id": run_id,
                "compressed_sequence": " -> ".join(sequence_names[int(value)] for value in compressed),
            }
        )
        for value, name in sequence_names.items():
            quadrant_rows.append(
                {
                    "run_id": run_id,
                    "quadrant": value,
                    "quadrant_name": name,
                    "fraction_before_closure": float(np.mean(quadrant == value)),
                }
            )

        active = np.flatnonzero(group["direct_active"].to_numpy(int) == 1)
        if len(active):
            index = int(active[0])
            onset_rows.append(
                {
                    "run_id": run_id,
                    "gravity_index": int(group.loc[index, "gravity_index"]),
                    "x_trav": float(group.loc[index, "x_trav"]),
                    "x_conn": float(group.loc[index, "x_conn"]),
                    "s_joint": float(group.loc[index, "s_joint"]),
                    "d_eq": float(group.loc[index, "d_eq"]),
                }
            )

    pd.DataFrame(quadrant_rows).to_csv(RESULTS / "T424_HOLDOUT_QUADRANT_OCCUPANCY.csv", index=False)
    pd.DataFrame(onset_rows).to_csv(RESULTS / "T424_HOLDOUT_RELEASE_ONSET_COORDINATES.csv", index=False)
    pd.DataFrame(sequence_rows).to_csv(RESULTS / "T424_HOLDOUT_QUADRANT_SEQUENCES.csv", index=False)

    trav_median, trav_lo, trav_hi = quantile_curves(trav_curves)
    conn_median, conn_lo, conn_hi = quantile_curves(conn_curves)
    prevalence = float(metrics["positive_frames"].iloc[0] / metrics["total_frames"].iloc[0])
    model_order = ["joint_di_ara", "traversal_only", "connection_only", "amount_only", "elapsed_only"]
    metrics = metrics.set_index("model").loc[model_order].reset_index()

    plt.rcParams.update({"font.size": 11})
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), constrained_layout=True)
    fig.suptitle("T424 — literal hourglass Irrationality Di-ARA holdout", fontsize=20)

    ax = axes[0, 0]
    ax.fill_between(grid, trav_lo, trav_hi, color="#4c78a8", alpha=0.18)
    ax.plot(grid, trav_median, color="#2f6ea5", linewidth=2.6, label="C1 traversal / movement")
    ax.fill_between(grid, conn_lo, conn_hi, color="#f28e2b", alpha=0.18)
    ax.plot(grid, conn_median, color="#d97400", linewidth=2.6, label="C2 connection / packing")
    ax.axhline(1.0, color="#555555", linestyle="--", linewidth=1.2, label="ARA ridge 1.0")
    ax.set(xlabel="Fraction of observed discharge-to-closure history", ylabel="Independent ARA coordinate (0–2)")
    ax.set_title("Median histories; bands are the middle 50% of 16 runs")
    ax.set_ylim(-0.03, 2.03)
    ax.legend(frameon=False, loc="best")
    ax.grid(alpha=0.2)

    ax = axes[0, 1]
    ax.plot(trav_median, conn_median, color="#555555", linewidth=2.0)
    sample_indices = [0, 25, 50, 75, 100]
    scatter = ax.scatter(
        trav_median[sample_indices],
        conn_median[sample_indices],
        c=grid[sample_indices],
        cmap="viridis",
        s=80,
        edgecolor="white",
        linewidth=0.8,
        zorder=3,
    )
    for index in [25, 50, 75]:
        ax.annotate(f"{grid[index]:.2f}", (trav_median[index], conn_median[index]),
                    xytext=(7, -18 if index == 25 else 6), textcoords="offset points")
    ax.scatter(trav_median[0], conn_median[0], marker="s", s=115,
               facecolor="white", edgecolor="#2f6ea5", linewidth=2.0, zorder=4,
               label="start")
    ax.scatter(trav_median[-1], conn_median[-1], marker="*", s=175,
               facecolor="#d97400", edgecolor="white", linewidth=0.8, zorder=5,
               label="closure")
    ax.axvline(1.0, color="#666666", linestyle="--", linewidth=1.1)
    ax.axhline(1.0, color="#666666", linestyle="--", linewidth=1.1)
    ax.plot([0, 2], [2, 0], color="#999999", linestyle=":", linewidth=1.1, label="exact complement")
    ax.set(
        xlim=(0, 2),
        ylim=(0, 2),
        xlabel="C1 traversal / movement ARA (0–2)",
        ylabel="C2 connection / packing ARA (0–2)",
    )
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Median Di-ARA path, annotated by history fraction")
    ax.grid(alpha=0.15)
    ax.legend(frameon=False, loc="lower left")
    fig.colorbar(scatter, ax=ax, label="History fraction")

    ax = axes[1, 0]
    colors = ["#d99a20"] + ["#a9b3bf"] * 4
    ax.barh(metrics["model"], metrics["average_precision"], color=colors)
    ax.axvline(prevalence, color="#7b3294", linestyle="--", linewidth=1.5,
               label=f"event-frame prevalence = {prevalence:.3f}")
    for row_index, row in metrics.iterrows():
        ax.text(float(row["average_precision"]) + 0.008, row_index,
                f"AP {row['average_precision']:.3f} · Brier {row['brier']:.3f}", va="center")
    ax.set(xlabel="Average precision (higher is better)", xlim=(0, max(0.42, metrics["average_precision"].max() + 0.08)))
    ax.invert_yaxis()
    ax.set_title("Frozen forecast: joint beats single axes, not elapsed time")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.2)

    ax = axes[1, 1]
    found = leads.loc[leads["forecast_found"].astype(bool), "lead_s"].to_numpy(float)
    bins = np.linspace(0.6, 2.6, 9)
    ax.hist(found, bins=bins, color="#59a14f", alpha=0.82, edgecolor="white")
    median_lead = float(np.median(found)) if len(found) else float("nan")
    ax.axvline(median_lead, color="#2b6f2b", linestyle="--", linewidth=2,
               label=f"median lead = {median_lead:.2f} s")
    ax.set(xlabel="First frozen warning before direct event (s)", ylabel="Event count")
    ax.set_title(f"Warnings found for {len(found)} / {len(leads)} direct events")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)

    figure_path = RESULTS / "T424_HOLDOUT_RESULT_SUMMARY.png"
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    quadrant_summary = (
        pd.DataFrame(quadrant_rows)
        .groupby("quadrant_name")["fraction_before_closure"]
        .mean()
        .sort_values(ascending=False)
        .to_dict()
    )
    onset_frame = pd.DataFrame(onset_rows)
    sequence_counts = pd.Series(
        [row["compressed_sequence"] for row in sequence_rows], dtype="object"
    ).value_counts()

    def median_coordinates(data: pd.DataFrame) -> dict[str, float]:
        return {
            key: float(data[key].median())
            for key in ["x_trav", "x_conn", "s_joint", "d_eq"]
            if key in data and len(data)
        }

    summary = {
        "status": "PARTIAL_STRUCTURAL_SUPPORT__PREDICTION_GATE_FAILED",
        "runs": int(frame["run_id"].nunique()),
        "direct_events": int(len(events)),
        "runs_with_traversal_connection_crossing": int(crossing_runs),
        "event_frame_prevalence": prevalence,
        "joint_average_precision": float(metrics.loc[metrics.model == "joint_di_ara", "average_precision"].iloc[0]),
        "elapsed_average_precision": float(metrics.loc[metrics.model == "elapsed_only", "average_precision"].iloc[0]),
        "joint_brier": float(metrics.loc[metrics.model == "joint_di_ara", "brier"].iloc[0]),
        "best_brier": float(metrics["brier"].min()),
        "median_warning_lead_s": median_lead,
        "warning_coverage": int(len(found)),
        "structural_observed_median_d_eq": outcome["structural_null"]["observed_median_d_eq"],
        "structural_null_median_d_eq": outcome["structural_null"]["null_median_d_eq"],
        "structural_improvement_fraction": outcome["structural_null"]["improvement_fraction"],
        "structural_empirical_p": outcome["structural_null"]["empirical_p"],
        "mean_quadrant_fraction_before_closure": quadrant_summary,
        "median_direct_event_coordinates": median_coordinates(event_join),
        "median_release_onset_coordinates": median_coordinates(onset_frame),
        "top_compressed_quadrant_sequences": {
            str(key): int(value) for key, value in sequence_counts.head(5).items()
        },
        "primary_gate_pass": bool(outcome["primary_gate_pass"]),
    }
    (RESULTS / "T424_POSTHOC_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
