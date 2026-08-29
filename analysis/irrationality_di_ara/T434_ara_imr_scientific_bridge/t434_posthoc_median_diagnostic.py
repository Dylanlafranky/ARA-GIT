"""Post-result T434 diagnostic: median coherent-excess frequency.

This is not the frozen primary test. It is retained to explain why the
maximum-bin frequency translation failed and to define a possible future
replication target without rewriting T434's verdict.
"""

from __future__ import annotations

import itertools
import json
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import t434_ara_imr_bridge as core


HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"


def main() -> None:
    rows = pd.read_csv(RESULTS / "T434_EVENT_RESULTS.csv")
    tracks_all = pd.read_csv(RESULTS / "T434_FREQUENCY_TRACKS.csv")
    coords = pd.read_csv(core.COORDS)
    tracks = {event: tracks_all[tracks_all.event == event].copy().sort_values("time_s") for event in core.EVENTS}

    f_values = rows.set_index("event").loc[core.EVENTS, "ara_handover_median_excess_frequency_hz"].to_numpy(float)
    fc_values = np.array([core.IMR[event]["fc_hz"] for event in core.EVENTS], float)
    event_errors = np.abs(np.log(f_values / fc_values))
    observed_error = float(np.median(event_errors))
    wrong = np.array([
        np.median(np.abs(np.log(f_values / np.asarray(perm, float))))
        for perm in itertools.permutations(fc_values)
    ])

    auc_inputs: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    observed_aucs = []
    for event in core.EVENTS:
        frame = coords[(coords.event == event) & coords.time_s.between(*core.WINDOW)].copy().sort_values("time_s")
        track = tracks[event]
        merged = pd.merge_asof(
            frame,
            track,
            on="time_s",
            direction="nearest",
            tolerance=0.0025,
        ).dropna(subset=["median_excess_frequency_hz"])
        delta = core.rolling_median((merged.c1 - merged.c2).to_numpy(float))
        labels = merged.median_excess_frequency_hz.to_numpy(float) >= core.IMR[event]["fc_hz"]
        auc_inputs[event] = (delta, labels)
        observed_aucs.append(core.auc_score(delta, labels))
    observed_auc = float(np.nanmedian(observed_aucs))

    rng = np.random.default_rng(core.SEED)
    shift_errors = np.empty(core.N_NULL)
    shift_aucs = np.empty(core.N_NULL)
    for k in range(core.N_NULL):
        errors = []
        aucs = []
        for event in core.EVENTS:
            track = tracks[event]
            n = len(track)
            allowed = np.concatenate([
                np.arange(core.MIN_SHIFT_FRAMES, n // 2 + 1),
                np.arange(n // 2 + 1, n - core.MIN_SHIFT_FRAMES + 1),
            ])
            shift = int(rng.choice(allowed))
            landmark = float(rows.loc[rows.event == event, "landmark_time_s"].iloc[0])
            idx = int(np.argmin(np.abs(track.time_s.to_numpy(float) - landmark)))
            shifted_f = float(np.roll(track.median_excess_frequency_hz.to_numpy(float), shift)[idx])
            errors.append(abs(np.log(shifted_f / core.IMR[event]["fc_hz"])))
            delta, labels = auc_inputs[event]
            aucs.append(core.auc_score(np.roll(delta, shift), labels))
        shift_errors[k] = np.median(errors)
        shift_aucs[k] = np.nanmedian(aucs)

    out = rows[["event", "ara_handover_median_excess_frequency_hz", "published_imr_fc_hz"]].copy()
    out["ratio_to_imr_fc"] = out.ara_handover_median_excess_frequency_hz / out.published_imr_fc_hz
    out["absolute_percent_difference"] = np.abs(out.ratio_to_imr_fc - 1.0) * 100.0
    out.to_csv(RESULTS / "T434_POSTHOC_MEDIAN_EVENT_RESULTS.csv", index=False)

    payload = {
        "status": "post_result_exploratory_diagnostic_not_a_frozen_pass",
        "median_absolute_percent_difference": float(np.median(out.absolute_percent_difference)),
        "events_within_25_percent": int((out.absolute_percent_difference <= 25.0).sum()),
        "wrong_event_assignment_p": float(np.mean(wrong <= observed_error)),
        "temporal_shift_error_p": float((1 + np.sum(shift_errors <= observed_error)) / (core.N_NULL + 1)),
        "median_orientation_invariant_auc": observed_auc,
        "temporal_shift_auc_p": float((1 + np.sum(shift_aucs >= observed_auc)) / (core.N_NULL + 1)),
        "interpretation": "Potential future replication target only; selected after inspecting the failed maximum-bin translation.",
    }
    (RESULTS / "T434_POSTHOC_MEDIAN_DIAGNOSTIC.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(11.5, 6.3), constrained_layout=True)
    x = np.arange(len(out))
    primary = rows.set_index("event").loc[core.EVENTS, "ara_handover_ridge_frequency_hz"].to_numpy(float)
    scientific = out.published_imr_fc_hz.to_numpy(float)
    diagnostic = out.ara_handover_median_excess_frequency_hz.to_numpy(float)
    ax.scatter(x, scientific, s=110, marker="s", color="#d99a22", label="Published IMR cutoff (independent method)", zorder=4)
    ax.scatter(x, primary, s=95, facecolor="white", edgecolor="#2468b4", linewidth=2, label="Frozen ARA maximum-bin translation (primary)", zorder=4)
    ax.scatter(x, diagnostic, s=95, marker="D", color="#2f9e67", label="ARA median-excess translation (post-result diagnostic)", zorder=4)
    for i in range(len(out)):
        ax.plot([i, i], [min(scientific[i], primary[i], diagnostic[i]), max(scientific[i], primary[i], diagnostic[i])], color="#94a3b8", lw=1.2, zorder=1)
        ax.text(i, diagnostic[i] + 13, f"{out.absolute_percent_difference.iloc[i]:.1f}%", ha="center", color="#207a4f", fontsize=9)
    ax.set_xticks(x, core.EVENTS)
    ax.set_ylim(20, 330)
    ax.set_ylabel("Frequency (Hz)")
    ax.set_title("T434 bridge audit: the frozen translation fails; the robust diagnostic is timing-specific only", fontsize=14, fontweight="bold")
    ax.text(
        0.01,
        0.01,
        "Diagnostic controls: temporal shift p=0.00010; wrong-event assignment p=0.375; child-order AUC shift p=0.182.\n"
        "Therefore the green series is a future replication target, not a T434 pass.",
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        bbox={"facecolor": "white", "edgecolor": "#cbd5e1", "alpha": 0.92, "boxstyle": "round,pad=0.5"},
    )
    ax.legend(loc="upper left", fontsize=9)
    fig.savefig(RESULTS / "T434_BRIDGE_AUDIT.png", dpi=180)
    plt.close(fig)
    print(out.to_string(index=False))
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
