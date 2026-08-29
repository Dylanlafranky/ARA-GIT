"""Post-result timing diagnostic for T428.

This does not alter the frozen T428 gates.  It asks whether the persistent
low-gap runs reported by T428 are specifically aligned to the published event
time, or recur throughout the analysed strain history.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
COORDINATES = RESULTS / "T428_CONSENSUS_COORDINATES.csv"
FREEZE = ROOT / "T428_DEV_FREEZE.json"
OUT_PNG = RESULTS / "T428_POSTHOC_TIMING_DIAGNOSTIC.png"
OUT_JSON = RESULTS / "T428_POSTHOC_TIMING_DIAGNOSTIC.json"


def persistent_runs(frame: pd.DataFrame, threshold: float, minimum: int = 3):
    mask = frame["coupled_gap"].to_numpy() <= threshold
    runs = []
    start = None
    for i, value in enumerate(mask):
        if value and start is None:
            start = i
        if start is not None and ((not value) or i == len(mask) - 1):
            stop = i if value and i == len(mask) - 1 else i - 1
            if stop - start + 1 >= minimum:
                centre = (start + stop) // 2
                runs.append(
                    {
                        "start_s": float(frame.iloc[start]["time_s"]),
                        "end_s": float(frame.iloc[stop]["time_s"]),
                        "centre_s": float(frame.iloc[centre]["time_s"]),
                        "frames": int(stop - start + 1),
                    }
                )
            start = None
    return runs


def main() -> None:
    data = pd.read_csv(COORDINATES)
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    threshold = float(freeze["coupled_gap_threshold_q20"])
    events = list(data["event"].drop_duplicates())

    rows = []
    histories = {}
    for event in events:
        frame = data[data.event == event].sort_values("time_s").reset_index(drop=True)
        runs = persistent_runs(frame, threshold)
        histories[event] = (frame, runs)
        nearest = min((abs(r["centre_s"]) for r in runs), default=float("nan"))
        i0 = int(np.argmin(np.abs(frame["time_s"].to_numpy())))
        rows.append(
            {
                "event": event,
                "persistent_runs": len(runs),
                "nearest_run_centre_abs_s": float(nearest),
                "run_within_32ms": bool(nearest <= 0.032),
                "run_within_64ms": bool(nearest <= 0.064),
                "run_within_128ms": bool(nearest <= 0.128),
                "coupled_gap_at_native_time": float(frame.iloc[i0]["coupled_gap"]),
                "closure_at_native_time": float(frame.iloc[i0]["simultaneous_closure"]),
            }
        )

    summary = pd.DataFrame(rows)
    payload = {
        "status": "post-result exploratory diagnostic; frozen T428 gates unchanged",
        "gap_threshold": threshold,
        "events_with_run_within_32ms": int(summary.run_within_32ms.sum()),
        "events_with_run_within_64ms": int(summary.run_within_64ms.sum()),
        "events_with_run_within_128ms": int(summary.run_within_128ms.sum()),
        "n_events": len(summary),
        "events": summary.to_dict(orient="records"),
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    plt.style.use("dark_background")
    fig = plt.figure(figsize=(18, 12), constrained_layout=True)
    grid = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(grid[0, :])
    ax2 = fig.add_subplot(grid[1, 0])
    ax3 = fig.add_subplot(grid[1, 1])
    colours = plt.cm.viridis(np.linspace(0.12, 0.92, len(events)))

    for offset, (event, colour) in enumerate(zip(events, colours)):
        frame, runs = histories[event]
        y = frame["coupled_gap"].to_numpy() + offset * 1.15
        ax1.plot(frame["time_s"], y, color=colour, lw=1.35, label=event)
        ax1.axhline(threshold + offset * 1.15, color=colour, lw=0.8, ls="--", alpha=0.55)
        for run in runs:
            ax1.axvspan(run["start_s"], run["end_s"], ymin=offset / len(events), ymax=(offset + 0.8) / len(events), color="#f59e0b", alpha=0.28)
    ax1.axvline(0.0, color="white", ls=":", lw=2, label="published event time")
    ax1.set(
        title="Persistent paired runs recur across the full pre-event trace",
        xlabel="Seconds relative to published event time",
        ylabel="Coupled gap, vertically offset by event",
    )
    ax1.grid(alpha=0.18)
    ax1.legend(ncol=3, loc="upper left")

    for i, (event, colour) in enumerate(zip(events, colours)):
        _, runs = histories[event]
        centres = [r["centre_s"] for r in runs]
        ax2.scatter(centres, np.full(len(centres), i), color=colour, s=60, edgecolor="white", linewidth=0.4)
    ax2.axvline(0.0, color="white", ls=":", lw=2)
    ax2.axvspan(-0.064, 0.064, color="#f59e0b", alpha=0.18, label="±64 ms")
    ax2.set(
        title=f"Run centres: {int(summary.run_within_64ms.sum())}/{len(summary)} events within ±64 ms",
        xlabel="Persistent-run centre relative to event (s)",
        ylabel="Event",
        yticks=np.arange(len(events)),
        yticklabels=events,
    )
    ax2.grid(alpha=0.18)
    ax2.legend()

    x = np.arange(len(events))
    ax3.bar(x - 0.18, summary["coupled_gap_at_native_time"], width=0.36, color="#60a5fa", label="coupled gap at native time")
    ax3.bar(x + 0.18, summary["closure_at_native_time"], width=0.36, color="#a78bfa", label="closure residual at native time")
    ax3.axhline(threshold, color="#f59e0b", ls="--", lw=2, label=f"frozen low-gap threshold {threshold:.3f}")
    ax3.set(
        title="Native-time values do not show a common paired handover",
        ylabel="ARA distance",
        xticks=x,
        xticklabels=events,
    )
    ax3.tick_params(axis="x", rotation=25)
    ax3.grid(axis="y", alpha=0.18)
    ax3.legend()

    fig.suptitle("T428 post-result timing diagnostic — not part of the frozen gates", fontsize=24, fontweight="bold")
    fig.savefig(OUT_PNG, dpi=180, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
