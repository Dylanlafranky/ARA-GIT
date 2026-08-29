"""Score T436's sealed waveform-only clock against the already-known T435 horizon."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
T435 = HERE.parent / "T435_blind_ara_binary_inversion"
PRED_NPZ = RESULTS / "T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.npz"
PRED_JSON = RESULTS / "T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.json"
RECEIPT = RESULTS / "T436_PREDICTION_SHA256.txt"
ANSWER = T435 / "results" / "T435_SCORED_RESULT.json"
SCORED = RESULTS / "T436_SCORED_RESULT.json"
HISTORY_CSV = RESULTS / "T436_IRRATIONALITY_HISTORY.csv"
TIMING_CSV = RESULTS / "T436_TIMING_COMPARISON.csv"
FIGURE = RESULTS / "T436_IRRATIONALITY_TIMING_COMPARISON.png"
SUMMARY_MD = HERE / "T436_RESULTS_SUMMARY.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def receipt_hash(key: str) -> str:
    for line in RECEIPT.read_text(encoding="utf-8").splitlines():
        if line.split()[0] == key:
            return line.split()[-1]
    raise KeyError(key)


def nearest_index(values: np.ndarray, target: float) -> int:
    return int(np.nanargmin(np.abs(values - target)))


def main() -> None:
    prediction_hash_verified = sha256(PRED_NPZ) == receipt_hash("prediction_sha256")
    if not prediction_hash_verified:
        raise RuntimeError("T436 prediction hash mismatch; refusing to score")

    pred = json.loads(PRED_JSON.read_text(encoding="utf-8"))
    answer = json.loads(ANSWER.read_text(encoding="utf-8"))
    arrays = np.load(PRED_NPZ)

    actual = float(answer["hidden_system_revealed"]["common_horizon_time"])
    t435_time = float(answer["metrics"]["predicted_handover_time"])
    t435_error = float(answer["metrics"]["handover_absolute_error"])
    cycle = float(answer["metrics"]["parent_waveform_cycle_at_prediction"])
    primary_time = float(pred["primary_predicted_time_M"])

    clocks = {
        "T436 joint Irr-Di-ARA": primary_time,
        "T435 frozen median": t435_time,
        "Child-only |U-R|": float(pred["single_distance_times_M"]["child_only_abs_U_minus_R"]),
        "Parent-only |H-1|": float(pred["single_distance_times_M"]["parent_only_abs_H_minus_1"]),
        "Wrong rung / full phase": float(pred["phase_control_times_M"]["wrong_rung_unhalved"]),
        "Quarter-shift control": float(pred["phase_control_times_M"]["quarter_shift"]),
        "Reverse-time control": float(pred["phase_control_times_M"]["reverse_chronology"]),
        "Waveform power maximum": float(pred["waveform_power_peak_time_M"]),
    }
    errors = {name: abs(value - actual) for name, value in clocks.items()}
    phase_control_errors = [
        errors["Wrong rung / full phase"],
        errors["Quarter-shift control"],
        errors["Reverse-time control"],
    ]

    improvement_gate = errors["T436 joint Irr-Di-ARA"] < t435_error
    cycle_gate = errors["T436 joint Irr-Di-ARA"] <= cycle
    specificity_gate = (
        errors["T436 joint Irr-Di-ARA"] <= errors["Child-only |U-R|"]
        and errors["T436 joint Irr-Di-ARA"] <= errors["Parent-only |H-1|"]
        and sum(errors["T436 joint Irr-Di-ARA"] <= value for value in phase_control_errors) >= 2
    )
    if improvement_gate and cycle_gate and specificity_gate:
        verdict = "SUPPORTED FOR TIMING TRANSFER"
    elif improvement_gate:
        verdict = "IMPROVED BUT NOT LOCKED"
    else:
        verdict = "NOT SUPPORTED"

    crossings = pred["eligible_child_crossings"]
    if crossings:
        nearest_crossing = min(crossings, key=lambda row: abs(float(row["time"]) - actual))
        nearest_crossing_error = abs(float(nearest_crossing["time"]) - actual)
    else:
        nearest_crossing = None
        nearest_crossing_error = None

    timing_rows = [
        {
            "clock": name,
            "predicted_time_M": value,
            "actual_common_horizon_M": actual,
            "signed_error_M": value - actual,
            "absolute_error_M": errors[name],
            "error_in_T435_parent_cycles": errors[name] / cycle,
        }
        for name, value in clocks.items()
    ]
    pd.DataFrame(timing_rows).to_csv(TIMING_CSV, index=False)

    time = np.asarray(arrays["time"], dtype=float)
    u = np.asarray(arrays["primary_half_phase_U"], dtype=float)
    r = np.asarray(arrays["primary_half_phase_R"], dtype=float)
    h = np.asarray(arrays["primary_half_phase_H"], dtype=float)
    lock = np.asarray(arrays["lock_distance"], dtype=float)
    child_d = np.asarray(arrays["child_distance"], dtype=float)
    parent_d = np.asarray(arrays["parent_distance"], dtype=float)
    relation = np.asarray(arrays["relation_at_reads"], dtype=float)
    eligible = np.asarray(arrays["eligible"], dtype=bool)

    history = pd.DataFrame({
        "simulation_time_M": time,
        "openness_U": u,
        "closure_R": r,
        "parent_H": h,
        "child_distance_abs_U_minus_R": child_d,
        "parent_distance_abs_H_minus_1": parent_d,
        "joint_lock_distance": lock,
        "T435_relation_ARA": relation,
        "eligible_late_parent_basin": eligible,
    })
    history.to_csv(HISTORY_CSV, index=False)

    primary_k = nearest_index(time, primary_time)
    actual_k = nearest_index(time, actual)
    start = max(float(time[eligible][0]) - 25.0, actual - 180.0)
    end = min(float(pred["waveform_power_peak_time_M"]) + 30.0, float(time[-1]))
    view = (time >= start) & (time <= end)

    plt.style.use("dark_background")
    fig, axes = plt.subplots(2, 2, figsize=(18, 12), constrained_layout=True)
    fig.patch.set_facecolor("#0b1220")
    for ax in axes.flat:
        ax.set_facecolor("#101827")
        ax.grid(color="#334155", alpha=0.45)

    ax = axes[0, 0]
    ax.plot(time[view], u[view], color="#60a5fa", lw=1.8, label="U — openness / traversal")
    ax.plot(time[view], r[view], color="#f59e0b", lw=1.8, label="R — connection closure")
    ax.plot(time[view], h[view], color="#a78bfa", lw=1.5, label="H — parent lag-angle")
    ax.axhline(1.0, color="#e2e8f0", ls=":", label="ARA ridge = 1")
    ax.axvline(actual, color="#22c55e", lw=2.2, label=f"common horizon C = {actual:.3f} M")
    ax.axvline(primary_time, color="#ef4444", lw=2.2, ls="--", label=f"T436 = {primary_time:.3f} M")
    ax.axvline(t435_time, color="#f8fafc", lw=1.4, ls="-.", label=f"T435 = {t435_time:.3f} M")
    ax.set(
        title="Time-facing Irrationality Di-ARA histories",
        xlabel="SXS simulation time / M",
        ylabel="Independent ARA coordinate (0–2)",
        ylim=(0, 2),
    )
    ax.legend(fontsize=8, loc="upper left")

    ax = axes[0, 1]
    sc = ax.scatter(u[eligible], r[eligible], c=time[eligible], cmap="viridis", s=24, alpha=0.8)
    ax.plot(u[eligible], r[eligible], color="#94a3b8", alpha=0.3, lw=0.8)
    ax.scatter(u[primary_k], r[primary_k], s=160, marker="*", color="#ef4444", edgecolor="white", label="T436 joint lock")
    ax.scatter(u[actual_k], r[actual_k], s=100, marker="o", facecolor="none", edgecolor="#22c55e", lw=2.2, label="nearest read to horizon C")
    ax.plot([0, 2], [0, 2], color="#e2e8f0", ls=":", label="child singularity U=R")
    ax.axvline(1, color="#64748b", ls="--", lw=1)
    ax.axhline(1, color="#64748b", ls="--", lw=1)
    ax.set(
        title="Chronological child Di-ARA path in the late parent basin",
        xlabel="U — openness / traversal (0–2)",
        ylabel="R — connection closure (0–2)",
        xlim=(0, 2),
        ylim=(0, 2.04),
    )
    ax.legend(fontsize=8, loc="lower right")
    cbar = fig.colorbar(sc, ax=ax, pad=0.01)
    cbar.set_label("SXS simulation time / M")
    inset = ax.inset_axes([0.08, 0.08, 0.43, 0.32])
    inset.plot(u[eligible], r[eligible], color="#94a3b8", alpha=0.35, lw=0.7)
    inset.scatter(u[eligible], r[eligible], c=time[eligible], cmap="viridis", s=8)
    inset.scatter(u[primary_k], r[primary_k], s=55, marker="*", color="#ef4444", edgecolor="white")
    inset.set(
        title="zoom: closure pole",
        xlim=(max(0.0, float(np.min(u[eligible])) - 0.03), min(2.0, float(np.max(u[eligible])) + 0.03)),
        ylim=(float(np.min(r[eligible])) - 2e-5, min(2.00002, float(np.max(r[eligible])) + 2e-5)),
    )
    inset.tick_params(labelsize=7)
    inset.grid(color="#334155", alpha=0.35)

    ax = axes[1, 0]
    ax.plot(time[view], child_d[view], color="#60a5fa", lw=1.5, label="child distance |U-R|")
    ax.plot(time[view], parent_d[view], color="#a78bfa", lw=1.5, label="parent ridge distance |H-1|")
    ax.plot(time[view], lock[view], color="#f59e0b", lw=2.2, label="joint lock distance")
    ax.axvline(actual, color="#22c55e", lw=2.2, label="common horizon C")
    ax.axvline(primary_time, color="#ef4444", lw=2.2, ls="--", label="T436 minimum joint lock")
    ax.axvline(float(pred["waveform_power_peak_time_M"]), color="#e2e8f0", lw=1.3, ls=":", label="waveform power maximum")
    ax.set(
        title="Child singularity and parent ridge lock",
        xlabel="SXS simulation time / M",
        ylabel="ARA distance (lower = more locked)",
    )
    ax.legend(fontsize=8, loc="upper left")

    ax = axes[1, 1]
    ordered = sorted(timing_rows, key=lambda row: row["absolute_error_M"])
    labels = [row["clock"] for row in ordered]
    values = [row["absolute_error_M"] for row in ordered]
    colors = ["#ef4444" if label.startswith("T436") else "#64748b" for label in labels]
    bars = ax.barh(labels, values, color=colors, edgecolor="#e2e8f0")
    ax.axvline(cycle, color="#f59e0b", lw=2, ls="--", label=f"one parent cycle = {cycle:.3f} M")
    ax.axvline(t435_error, color="#f8fafc", lw=1.5, ls=":", label=f"old T435 error = {t435_error:.3f} M")
    for bar, value in zip(bars, values):
        ax.text(value + max(values) * 0.01, bar.get_y() + bar.get_height() / 2, f"{value:.3f} M", va="center", fontsize=9)
    ax.set(
        title="Handover timing errors: primary, components, and controls",
        xlabel="Absolute error from first common horizon / M (lower is better)",
        ylabel="Frozen clock or control",
    )
    ax.invert_yaxis()
    ax.legend(fontsize=8, loc="lower right")

    fig.suptitle(
        f"T436 — Irrationality Di-ARA timing transfer: {verdict}\n"
        f"T436 error {errors['T436 joint Irr-Di-ARA']:.3f} M vs T435 {t435_error:.3f} M",
        fontsize=18,
        fontweight="bold",
    )
    fig.savefig(FIGURE, dpi=180, facecolor=fig.get_facecolor())
    plt.close(fig)

    result = {
        "test": "T436_irrationality_timing_transfer",
        "verdict": verdict,
        "evidence_class": "known-answer method-transfer calibration on one numerical-relativity simulation",
        "prediction_sha256_verified": prediction_hash_verified,
        "source": "SXS:BBH:0305 Lev6 combined waveform; T435 horizon answer key used only by scorer",
        "actual_common_horizon_time_M": actual,
        "T435": {
            "predicted_time_M": t435_time,
            "absolute_error_M": t435_error,
            "parent_waveform_cycle_M": cycle,
        },
        "T436": {
            "predicted_time_M": primary_time,
            "signed_error_M": primary_time - actual,
            "absolute_error_M": errors["T436 joint Irr-Di-ARA"],
            "error_parent_cycles": errors["T436 joint Irr-Di-ARA"] / cycle,
            "timing_improvement_M": t435_error - errors["T436 joint Irr-Di-ARA"],
            "timing_error_reduction_fraction": 1.0 - errors["T436 joint Irr-Di-ARA"] / t435_error,
            "coordinates_at_prediction": pred["primary_at"],
        },
        "gates": {
            "improves_on_T435": bool(improvement_gate),
            "within_one_parent_waveform_cycle": bool(cycle_gate),
            "joint_lock_specificity": bool(specificity_gate),
        },
        "timing_comparison": timing_rows,
        "nearest_observed_child_crossing_posthoc": nearest_crossing,
        "nearest_observed_child_crossing_error_M": nearest_crossing_error,
        "caveat": "The horizon answer was already known historically before T436; this is not blind confirmation.",
    }
    SCORED.write_text(json.dumps(result, indent=2), encoding="utf-8")

    gate_lines = "\n".join(
        f"- **{'PASS' if value else 'FAIL'}** — {name.replace('_', ' ')}."
        for name, value in result["gates"].items()
    )
    controls_lines = [
        "| Clock | Predicted time (M) | Signed error (M) | Absolute error (M) | Error (parent cycles) |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in timing_rows:
        controls_lines.append(
            f"| {row['clock']} | {row['predicted_time_M']:.3f} | "
            f"{row['signed_error_M']:.3f} | {row['absolute_error_M']:.3f} | "
            f"{row['error_in_T435_parent_cycles']:.3f} |"
        )
    controls_table = "\n".join(controls_lines)
    error_change = t435_error - errors["T436 joint Irr-Di-ARA"]
    if error_change >= 0:
        change_text = (
            f"The timing error improved by `{error_change:.6f} M` "
            f"(`{100.0 * error_change / t435_error:.1f}%` reduction)."
        )
    else:
        change_text = (
            f"The timing error worsened by `{abs(error_change):.6f} M` "
            f"(`{100.0 * abs(error_change) / t435_error:.1f}%` larger than T435)."
        )
    summary = f"""# T436 results — Irrationality Di-ARA timing transfer

**Frozen verdict: {verdict}.**

## Answer first

The transferred Irrationality Di-ARA clock predicted the common handover at
`{primary_time:.6f} M`, compared with the first common horizon at
`{actual:.6f} M`. Its absolute error is `{errors['T436 joint Irr-Di-ARA']:.6f} M`
(`{errors['T436 joint Irr-Di-ARA'] / cycle:.3f}` T435 parent-waveform cycles),
versus T435's `{t435_error:.6f} M` error.

{change_text} The primary estimate is {'before' if primary_time < actual else 'after'}
the common horizon by `{abs(primary_time - actual):.6f} M`.

## Frozen gates

{gate_lines}

## What the clock measured

The primary estimate minimized the predeclared joint distance

```text
sqrt((U-R)^2 + (H-1)^2)
```

inside the waveform-only late parent basin (`T435 relation <= 1`, before the
total modal-power maximum). At the selected read:

- `U = {pred['primary_at']['U']:.6f}`;
- `R = {pred['primary_at']['R']:.6f}`;
- `H = {pred['primary_at']['H']:.6f}`;
- child distance `|U-R| = {pred['primary_at']['child_distance_abs_U_minus_R']:.6f}`;
- parent-ridge distance `|H-1| = {pred['primary_at']['parent_distance_abs_H_minus_1']:.6f}`.

This is the T421 hierarchy transferred to the T435 half-phase child axis:
child singularity and parent ridge are measured together rather than treating a
single waveform extremum as the clock.

## Timing comparison

{controls_table}

## Evidence boundary

This same simulation's common-horizon time was already revealed in T435 before
T436 was designed. The prediction script did not read the answer key and its
artifact was hashed before scoring, but the result remains **known-answer
calibration**, not independent blind evidence. A fixed rerun on an untouched SXS
simulation is required before treating the timing rule as predictive.

## Files

- `T436_FROZEN_PROTOCOL.md`
- `T436_waveform_irrationality_clock.py`
- `T436_score_known_handover.py`
- `results/T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.npz`
- `results/T436_WAVEFORM_ONLY_IRRATIONALITY_CLOCK.json`
- `results/T436_SCORED_RESULT.json`
- `results/T436_IRRATIONALITY_HISTORY.csv`
- `results/T436_TIMING_COMPARISON.csv`
- `results/T436_IRRATIONALITY_TIMING_COMPARISON.png`
"""
    SUMMARY_MD.write_text(summary, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
