"""Exploratory follow-up to failed frozen T409 equality-crossing gate.

This analysis was specified only after the primary result was known.  It asks
whether the two independently measured waves approach one another at handover
without requiring an exact crossing.  It must not be reported as preregistered.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
RNG = np.random.default_rng(4092027)
EVENT_ORDER = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8"]


def event_record(group: pd.DataFrame) -> dict[str, object]:
    u = group["u_event"].to_numpy(float)
    r = group["x_r"].to_numpy(float)
    i = group["x_i"].to_numpy(float)
    separation = np.abs(r - i)
    target_index = int(np.argmin(np.abs(u - 1.0)))
    local = (u >= 0.60) & (u <= 1.40)
    local_indices = np.flatnonzero(local)
    minimum_index = int(local_indices[np.argmin(separation[local])])
    rho, _ = spearmanr(r, i)
    return {
        "event_id": group["event_id"].iloc[0],
        "video": group["video"].iloc[0],
        "split": group["split"].iloc[0],
        "target_u_sampled": float(u[target_index]),
        "x_r_at_handover": float(r[target_index]),
        "x_i_at_handover": float(i[target_index]),
        "mean_participation_at_handover": float(0.5 * (r[target_index] + i[target_index])),
        "wave_separation_at_handover": float(separation[target_index]),
        "dominant_wave_at_handover": "R" if r[target_index] > i[target_index] else "I",
        "local_minimum_separation_u": float(u[minimum_index]),
        "local_minimum_separation": float(separation[minimum_index]),
        "local_minimum_timing_error_abs_u": float(abs(u[minimum_index] - 1.0)),
        "handover_separation_percentile_local": float(np.mean(separation[local] <= separation[target_index])),
        "within_event_spearman_r_i": float(rho),
    }


def shift_controls(groups: list[pd.DataFrame], draws: int = 10_000) -> np.ndarray:
    values = np.empty(draws, dtype=float)
    for draw in range(draws):
        separations: list[float] = []
        for group in groups:
            u = group["u_event"].to_numpy(float)
            r = group["x_r"].to_numpy(float)
            i = group["x_i"].to_numpy(float)
            target_index = int(np.argmin(np.abs(u - 1.0)))
            shift = int(RNG.integers(1, len(i)))
            separations.append(abs(r[target_index] - np.roll(i, shift)[target_index]))
        values[draw] = float(np.median(separations))
    return values


def make_figure(frame_df: pd.DataFrame, summary: pd.DataFrame, controls: np.ndarray) -> None:
    fig, axes = plt.subplots(4, 2, figsize=(16, 16))
    for ax, event_id in zip(axes.flat, EVENT_ORDER):
        group = frame_df[frame_df["event_id"] == event_id]
        row = summary[summary["event_id"] == event_id].iloc[0]
        sep = abs(group["x_r"] - group["x_i"])
        ax.plot(group["u_event"], sep, color="#4c6fa8", lw=2)
        ax.axvline(1.0, color="#111111", lw=1.5, label="direct handover")
        ax.axvline(row["local_minimum_separation_u"], color="#d14b4b", ls=":", lw=1.8, label="nearest local close approach")
        ax.scatter(
            [row["target_u_sampled"]],
            [row["wave_separation_at_handover"]],
            color="#e98b2a",
            edgecolor="black",
            s=55,
            zorder=4,
            label="measured separation at handover",
        )
        ax.set_xlim(0, max(1.4, float(group["u_event"].max())))
        ax.set_title(
            f"{event_id} · {row['split']} · dominant {row['dominant_wave_at_handover']}\n"
            f"|R−I| at handover={row['wave_separation_at_handover']:.3f}"
        )
        ax.set_xlabel("event position u (direct handover = 1.0)")
        ax.set_ylabel("wave separation |R − I| on ARA 0–2")
        ax.grid(alpha=0.25)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.subplots_adjust(top=0.89, hspace=0.50, wspace=0.18)
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 0.95), ncol=3, frameon=False)
    fig.suptitle("T409 exploratory close-approach diagnostic — specified after the crossing gate failed", fontsize=18, y=0.995)
    fig.savefig(RESULTS / "T409_POSTHOC_CLOSE_APPROACH_EVENTS.png", dpi=175)
    plt.close(fig)

    hold = summary[summary["split"] == "holdout"]
    observed = float(hold["wave_separation_at_handover"].median())
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.5), constrained_layout=True)
    axes[0].bar(
        summary["event_id"],
        summary["wave_separation_at_handover"],
        color=["#5a80b8" if x == "holdout" else "#aeb8c6" for x in summary["split"]],
    )
    axes[0].set(
        title="Exact wave separation at independently registered handover",
        xlabel="droplet event (blue = holdout)",
        ylabel="|R − I| at direct handover (ARA units)",
    )
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].hist(controls, bins=50, color="#b4bcc8", edgecolor="white")
    axes[1].axvline(observed, color="#d14b4b", lw=2.2, label=f"observed holdout median = {observed:.3f}")
    axes[1].axvline(np.median(controls), color="#222222", ls="--", label=f"shift median = {np.median(controls):.3f}")
    axes[1].set(
        title="Post-hoc circular-shift comparison",
        xlabel="median holdout |R − I| at target",
        ylabel="control draws",
    )
    axes[1].legend(frameon=False)
    axes[1].grid(axis="y", alpha=0.2)
    fig.suptitle("Close approach is exploratory, not the frozen T409 endpoint", fontsize=17)
    fig.savefig(RESULTS / "T409_POSTHOC_CLOSE_APPROACH_CONTROL.png", dpi=180)
    plt.close(fig)


def main() -> None:
    frame_df = pd.read_csv(RESULTS / "T409_FRAME_WAVES.csv")
    records = [event_record(frame_df[frame_df["event_id"] == event_id]) for event_id in EVENT_ORDER]
    summary = pd.DataFrame(records)
    holdout_groups = [
        frame_df[frame_df["event_id"] == event_id]
        for event_id in summary.loc[summary["split"] == "holdout", "event_id"]
    ]
    controls = shift_controls(holdout_groups)
    holdout = summary[summary["split"] == "holdout"]
    observed = float(holdout["wave_separation_at_handover"].median())
    control_median = float(np.median(controls))
    empirical_p = float((1 + np.sum(controls <= observed)) / (1 + len(controls)))
    result = {
        "status": "POST-HOC EXPLORATORY — not frozen",
        "question": "Do R and I make a close approach at handover even when they do not cross?",
        "holdout_median_separation_at_handover": observed,
        "circular_shift_median": control_median,
        "relative_reduction": float(1.0 - observed / control_median),
        "empirical_p": empirical_p,
        "events_dominated_by_R": int(np.sum(summary["dominant_wave_at_handover"] == "R")),
        "events_dominated_by_I": int(np.sum(summary["dominant_wave_at_handover"] == "I")),
    }
    summary.to_csv(RESULTS / "T409_POSTHOC_CLOSE_APPROACH_SUMMARY.csv", index=False)
    pd.DataFrame({"circular_shift_median_target_separation": controls}).to_csv(
        RESULTS / "T409_POSTHOC_CLOSE_APPROACH_CONTROLS.csv", index=False
    )
    with (RESULTS / "T409_POSTHOC_CLOSE_APPROACH_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    make_figure(frame_df, summary, controls)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
