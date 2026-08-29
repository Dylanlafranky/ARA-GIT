"""Separate cross-medium transfer control for T409 Video S1.

The target (persistent loss of the small central droplet at encoded frame 40)
was registered by visual QA before extracting the S1 R/I waves.  This control
is not pooled with, and cannot rescue, the frozen fibre holdout gate.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from t409_combined_handover_test import (
    Event,
    ara_map,
    causal_ema,
    extract_event,
    nearest_crossing_error,
)


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
EVENT = Event("S1C", "Video_S1.mp4", 120, 760, 0, 40, 80, "transfer-control")


def main() -> None:
    with (RESULTS / "T409_RESULTS.json").open(encoding="utf-8") as handle:
        frozen = json.load(handle)
    scaling = frozen["scaling"]
    frame = extract_event(EVENT)
    frame["x_r"] = causal_ema(
        ara_map(frame["r_raw"].to_numpy(float), scaling["r_log1p_q05"], scaling["r_log1p_q95"])
    )
    frame["x_i"] = causal_ema(
        ara_map(frame["i_raw"].to_numpy(float), scaling["i_log1p_q05"], scaling["i_log1p_q95"])
    )
    u = frame["u_event"].to_numpy(float)
    r = frame["x_r"].to_numpy(float)
    i = frame["x_i"].to_numpy(float)
    crossing_u, crossing_error, crossing_count = nearest_crossing_error(u, r, i)
    target_index = int(np.argmin(abs(u - 1.0)))
    result = {
        "status": "separate cross-medium transfer control",
        "target": "persistent loss of the small central droplet",
        "registered_frame": 40,
        "x_r_at_handover": float(r[target_index]),
        "x_i_at_handover": float(i[target_index]),
        "dominant_wave_at_handover": "R" if r[target_index] > i[target_index] else "I",
        "wave_separation_at_handover": float(abs(r[target_index] - i[target_index])),
        "nearest_crossing_u": None if not np.isfinite(crossing_u) else float(crossing_u),
        "nearest_crossing_error_abs_u": None if not np.isfinite(crossing_error) else float(crossing_error),
        "candidate_crossing_count": int(crossing_count),
        "interpretation_boundary": "Not pooled with and cannot alter the frozen fibre gate.",
    }
    frame.to_csv(RESULTS / "T409_S1_TRANSFER_CONTROL_WAVES.csv", index=False)
    with (RESULTS / "T409_S1_TRANSFER_CONTROL_RESULTS.json").open("w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)

    fig, axes = plt.subplots(1, 2, figsize=(15, 5.7), constrained_layout=True)
    axes[0].plot(u, r, color="#e98b2a", lw=2.1, label="R: coherent affine flow")
    axes[0].plot(u, i, color="#7652c7", lw=2.1, label="I: non-affine residual")
    axes[0].axvline(1.0, color="#111111", lw=1.6, label="registered small-droplet handover")
    axes[0].axhline(1.0, color="#4c956c", ls="--", label="ARA ridge = 1")
    if np.isfinite(crossing_u):
        axes[0].axvline(crossing_u, color="#d14b4b", ls=":", lw=2, label="nearest R=I crossing")
    axes[0].set(
        title="S1 transfer-control waves",
        xlabel="event position u (small-droplet handover = 1.0)",
        ylabel="independent ARA participation (0-2)",
        xlim=(0, 2.0),
        ylim=(-0.05, 2.05),
    )
    axes[0].legend(frameon=False, fontsize=9)
    axes[0].grid(alpha=0.25)

    axes[1].plot(r, i, color="#4c78a8", lw=2)
    axes[1].scatter([r[target_index]], [i[target_index]], s=75, color="#e98b2a", edgecolor="black", zorder=3)
    axes[1].plot([0, 2], [0, 2], color="#d14b4b", ls=":", label="R = I")
    axes[1].axvline(1.0, color="#4c956c", ls="--")
    axes[1].axhline(1.0, color="#4c956c", ls="--")
    axes[1].set(
        title="S1 transfer-control relation plane",
        xlabel="Rationality R (ARA 0-2)",
        ylabel="Irrationality I (ARA 0-2)",
        xlim=(-0.05, 2.05),
        ylim=(-0.05, 2.05),
    )
    axes[1].legend(frameon=False)
    axes[1].grid(alpha=0.25)
    fig.suptitle("T409 separate flat-substrate S1 transfer control", fontsize=17)
    fig.savefig(RESULTS / "T409_S1_TRANSFER_CONTROL.png", dpi=180)
    plt.close(fig)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
