#!/usr/bin/env python3
"""T388: distinguish same-detector repetition from ARA anti-phase reversal."""

from __future__ import annotations

import csv
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
VENDOR = HERE / "_vendor"
if VENDOR.exists():
    sys.path.insert(0, str(VENDOR))
MPL_CONFIG = HERE / "_matplotlib_cache"
MPL_CONFIG.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG))

import matplotlib.pyplot as plt
import numpy as np

import t385_buap_causal_irrationality_di_ara as base
import t387_full_pulse_return_wave as fullwave


RAW = base.RAW
OUT = HERE / "T388_same_event_antiphase"
PROTOCOL = HERE / "T388_SAME_EVENT_ANTIPHASE_PROTOCOL_2026-08-15.md"
EXPECTED_RAW_SHA256 = base.EXPECTED_RAW_SHA256
EXPECTED_PROTOCOL_SHA256 = "2B18E310FE2E261EB82A7F78F8F8A87ED7BE17AA8F02402C83D3898D41A5CD2D"

DT_NS = 8
WINDOW = 16
WINDOW_NS = WINDOW * DT_NS
TIMES_NS = np.arange(-256, 513, DT_NS, dtype=int)
SEED = 388


def sha256(path: Path) -> str:
    return base.sha256(path)


def bootstrap_median(values: np.ndarray, seed: int, n_boot: int = 2000) -> tuple[float, list[float]]:
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if not len(values):
        return math.nan, [math.nan, math.nan]
    rng = np.random.default_rng(seed)
    boot = np.asarray(
        [np.median(rng.choice(values, len(values), replace=True)) for _ in range(n_boot)]
    )
    return float(np.median(values)), [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]


def transform(trace: np.ndarray, name: str) -> np.ndarray:
    result = trace.copy()
    if name in ("full", "radial"):
        result[:, 0] = 2.0 - result[:, 0]
    if name in ("full", "path"):
        result[:, 1] = 2.0 - result[:, 1]
    return result


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def signed_area(trace: np.ndarray) -> float:
    z = trace - 1.0
    x = z[:, 0]
    y = z[:, 1]
    return float(0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1]))


def coordinate_at(event: base.Event, endpoint: int, window: int) -> tuple[float, float] | None:
    """T387 coordinate without its first-pulse recovery exclusion.

    T388 explicitly studies both recorded pulses, so both receive the identical
    adjacent-window calculation at their native positions.
    """
    first = endpoint - 2 * window + 1
    if first < 0 or endpoint >= len(event.values):
        return None
    y = event.values - event.causal_baseline
    previous = y[endpoint - 2 * window + 1 : endpoint - window + 1]
    current = y[endpoint - window + 1 : endpoint + 1]
    if len(previous) != window or len(current) != window:
        return None
    rms_previous = float(np.sqrt(np.mean(previous**2)))
    rms_current = float(np.sqrt(np.mean(current**2)))
    ratio = (rms_current + base.EPS_MV) / (rms_previous + base.EPS_MV)
    x_r = float(np.clip(2.0 * ratio / (1.0 + ratio), 0.0, 2.0))
    _, _, x_h = base.path_metrics(current)
    return x_r, x_h


def profile_rows(first: np.ndarray, second: np.ndarray) -> list[dict]:
    rows: list[dict] = []
    for pulse, matrix in (("stopped_muon", first), ("daughter", second)):
        for axis_i, axis in enumerate(("x_R", "x_H")):
            for j, time_ns in enumerate(TIMES_NS):
                values = matrix[:, j, axis_i]
                rows.append(
                    {
                        "pulse": pulse,
                        "axis": axis,
                        "time_ns_from_minimum": int(time_ns),
                        "n": int(len(values)),
                        "median": float(np.median(values)),
                        "q25": float(np.quantile(values, 0.25)),
                        "q75": float(np.quantile(values, 0.75)),
                    }
                )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    raw_hash = sha256(RAW)
    protocol_hash = sha256(PROTOCOL)
    if raw_hash != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"raw hash mismatch: {raw_hash}")
    if protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"protocol hash mismatch: {protocol_hash}")

    events = [e for e in base.load_events() if e.split == "evaluation" and e.eligible]
    retained = []
    minimum_pre = 2 * WINDOW + 32
    post_samples = 512 // DT_NS
    separation_guard = 256 // DT_NS
    for event in events:
        if event.first_index < minimum_pre:
            continue
        if event.first_index + post_samples > event.second_index - separation_guard:
            continue
        if event.second_index + post_samples >= len(event.values):
            continue
        retained.append(event)

    first = np.full((len(retained), len(TIMES_NS), 2), np.nan)
    second = np.full_like(first, np.nan)
    voltage_first = np.full((len(retained), len(TIMES_NS)), np.nan)
    voltage_second = np.full_like(voltage_first, np.nan)

    for i, event in enumerate(retained):
        y = event.values - event.causal_baseline
        for j, time_ns in enumerate(TIMES_NS):
            offset = int(time_ns // DT_NS)
            c1 = coordinate_at(event, event.first_index + offset, WINDOW)
            c2 = coordinate_at(event, event.second_index + offset, WINDOW)
            if c1 is not None:
                first[i, j] = c1
            if c2 is not None:
                second[i, j] = c2
            voltage_first[i, j] = -y[event.first_index + offset] / max(event.first_amp, 1e-12)
            voltage_second[i, j] = -y[event.second_index + offset] / max(event.second_amp, 1e-12)

    complete = np.all(np.isfinite(first), axis=(1, 2)) & np.all(np.isfinite(second), axis=(1, 2))
    retained = [event for event, keep in zip(retained, complete) if keep]
    first = first[complete]
    second = second[complete]
    voltage_first = voltage_first[complete]
    voltage_second = voltage_second[complete]
    if not len(retained):
        raise RuntimeError("no complete paired events")

    mapping_names = ("direct", "full", "radial", "path")
    mapping_labels = {
        "direct": "Direct repeat",
        "full": "Full reversal",
        "radial": "x_R-only reversal",
        "path": "x_H-only reversal",
    }
    event_rows: list[dict] = []
    scores = {name: [] for name in mapping_names}
    same_orientation = []
    area_first = []
    area_second = []
    for i, event in enumerate(retained):
        a1 = signed_area(first[i])
        a2 = signed_area(second[i])
        area_first.append(a1)
        area_second.append(a2)
        same = bool(np.sign(a1) == np.sign(a2) and abs(a1) > 1e-12 and abs(a2) > 1e-12)
        same_orientation.append(same)
        row = {
            "row": event.row,
            "event_id": event.event_id,
            "delay_ns": event.delay_ns,
            "first_amp_mV": event.first_amp,
            "second_amp_mV": event.second_amp,
            "first_loop_area": a1,
            "second_loop_area": a2,
            "same_orientation": int(same),
        }
        for name in mapping_names:
            score = rmse(transform(first[i], name), second[i])
            scores[name].append(score)
            row[f"rmse_{name}"] = score
        event_rows.append(row)

    scores = {k: np.asarray(v, dtype=float) for k, v in scores.items()}
    score_summary = {}
    for index, name in enumerate(mapping_names):
        median, ci = bootstrap_median(scores[name], SEED + index)
        score_summary[name] = {"median": median, "ci95": ci}

    deltas = {}
    for index, name in enumerate(("full", "radial", "path")):
        values = scores[name] - scores["direct"]
        median, ci = bootstrap_median(values, SEED + 20 + index)
        deltas[name] = {"reversal_minus_direct": median, "ci95": ci}

    winner = min(mapping_names, key=lambda name: score_summary[name]["median"])
    same_share = float(np.mean(same_orientation))
    direct_pass = bool(
        winner == "direct"
        and all(deltas[name]["ci95"][0] > 0 for name in ("full", "radial", "path"))
        and same_share > 0.75
    )
    full_pass = bool(
        winner == "full" and deltas["full"]["ci95"][1] < 0 and same_share > 0.75
    )
    one_axis_winner = winner if winner in ("radial", "path") else None
    one_axis_pass = bool(
        one_axis_winner
        and deltas[one_axis_winner]["ci95"][1] < 0
        and same_share < 0.25
    )

    guard_i = int(np.where(TIMES_NS == -128)[0][0])
    pre_first = first[:, guard_i]
    pre_second = second[:, guard_i]
    pre_distance = np.linalg.norm(pre_second - pre_first, axis=1)
    pre_distance_med, pre_distance_ci = bootstrap_median(pre_distance, SEED + 40)
    pre_summary = {
        "time_ns_from_minimum": -128,
        "first_median": np.median(pre_first, axis=0).tolist(),
        "second_median": np.median(pre_second, axis=0).tolist(),
        "paired_direct_distance_median": pre_distance_med,
        "paired_direct_distance_ci95": pre_distance_ci,
        "advance_handover_gate": False,
        "reason": "T385 found no held-out advance contribution outside the 128 ns guard; T388 is a paired response-identity test.",
    }

    med_first = np.median(first, axis=0)
    med_second = np.median(second, axis=0)
    q25_first = np.quantile(first, 0.25, axis=0)
    q75_first = np.quantile(first, 0.75, axis=0)
    q25_second = np.quantile(second, 0.25, axis=0)
    q75_second = np.quantile(second, 0.75, axis=0)

    blue = "#4c78a8"
    orange = "#e39d27"
    pink = "#b45b75"
    olive = "#73864b"
    charcoal = "#27313c"
    light = "#d7dde5"
    fig, axes = plt.subplots(3, 2, figsize=(15, 15), constrained_layout=True)
    fig.suptitle(
        "T388 — same-event stopped-muon / daughter anti-phase test\n"
        f"{len(retained):,} paired liquid-scintillator events · 128 ns ARA windows · Class-D detector boundary",
        fontsize=18,
        fontweight="bold",
        linespacing=1.35,
    )

    ax = axes[0, 0]
    vf = np.median(voltage_first, axis=0)
    vs = np.median(voltage_second, axis=0)
    ax.plot(TIMES_NS, vf, color=blue, linewidth=2.2, label="stopped-muon pulse")
    ax.plot(TIMES_NS, vs, color=orange, linewidth=2.2, label="daughter pulse")
    ax.axvline(0, color=charcoal, linewidth=1, linestyle="--")
    ax.axvline(-128, color=pink, linewidth=1, linestyle=":", label="causal guard")
    ax.set(title="Amplitude-normalised recorded pulses", xlabel="Time from pulse minimum (ns)", ylabel="Negative voltage / pulse amplitude")
    ax.legend(frameon=False)

    for axis_i, (title, ylabel) in enumerate((("Radial state coordinate", "x_R: 0 contraction · 1 ridge · 2 expansion"), ("Path/history coordinate", "x_H: 0 recurrent · 1 ridge · 2 open"))):
        ax = axes[0, 1] if axis_i == 0 else axes[1, 0]
        ax.fill_between(TIMES_NS, q25_first[:, axis_i], q75_first[:, axis_i], color=blue, alpha=0.15)
        ax.fill_between(TIMES_NS, q25_second[:, axis_i], q75_second[:, axis_i], color=orange, alpha=0.15)
        ax.plot(TIMES_NS, med_first[:, axis_i], color=blue, linewidth=2.2, label="stopped-muon pulse")
        ax.plot(TIMES_NS, med_second[:, axis_i], color=orange, linewidth=2.2, label="daughter pulse")
        ax.axhline(1, color=charcoal, linewidth=1, linestyle="--", label="ARA ridge 1.0")
        ax.axvline(-128, color=pink, linewidth=1, linestyle=":")
        ax.set(xlim=(TIMES_NS[0], TIMES_NS[-1]), ylim=(0, 2), title=title, xlabel="Time from pulse minimum (ns)", ylabel=ylabel)
        ax.legend(frameon=False, fontsize=8)

    ax = axes[1, 1]
    ax.plot(med_first[:, 0], med_first[:, 1], color=blue, linewidth=2.5, marker="o", markevery=12, label="first pulse")
    ax.plot(med_second[:, 0], med_second[:, 1], color=orange, linewidth=2.5, marker="s", markevery=12, label="second pulse")
    full_first = transform(med_first, "full")
    ax.plot(full_first[:, 0], full_first[:, 1], color=pink, linewidth=1.8, linestyle="--", label="full anti-phase of first")
    ax.axvline(1, color=charcoal, linewidth=1)
    ax.axhline(1, color=charcoal, linewidth=1)
    ax.set(xlim=(0, 2), ylim=(0, 2), aspect="equal", title="Median ARA loops and full anti-phase candidate", xlabel="x_R radial state", ylabel="x_H path/history")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[2, 0]
    values = [score_summary[n]["median"] for n in mapping_names]
    lows = [values[i] - score_summary[n]["ci95"][0] for i, n in enumerate(mapping_names)]
    highs = [score_summary[n]["ci95"][1] - values[i] for i, n in enumerate(mapping_names)]
    colors = [blue, pink, olive, orange]
    ax.bar(range(4), values, color=colors, edgecolor=charcoal, linewidth=0.8)
    ax.errorbar(range(4), values, yerr=[lows, highs], fmt="none", ecolor=charcoal, capsize=4)
    ax.set_xticks(range(4), [mapping_labels[n] for n in mapping_names], rotation=18, ha="right")
    ax.set(title="Paired trajectory error by frozen mapping", ylabel="Median two-axis RMSE (ARA units)")
    for i, value in enumerate(values):
        ax.text(i, value, f" {value:.4f}", ha="center", va="bottom", fontsize=9)

    ax = axes[2, 1]
    gate_labels = ["Direct repeat", "Full reversal", "One-axis reversal", "Advance outside guard"]
    gate_values = [direct_pass, full_pass, one_axis_pass, False]
    gate_colors = [blue if value else light for value in gate_values]
    ax.barh(range(4), [1, 1, 1, 1], color=gate_colors, edgecolor=charcoal)
    ax.set_yticks(range(4), gate_labels)
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.invert_yaxis()
    ax.set_title("Frozen gates")
    for i, value in enumerate(gate_values):
        ax.text(0.5, i, "PASS" if value else "FAIL", ha="center", va="center", fontweight="bold", color="white" if value else charcoal)
    ax.text(0, 4.28, f"Same loop orientation: {same_share:.1%}\nLowest RMSE mapping: {mapping_labels[winner]}", transform=ax.transData, fontsize=9, color="#586474")

    for ax in axes.flat:
        ax.grid(True, color="#d8dde5", linewidth=0.7, alpha=0.75)
        ax.spines[["top", "right"]].set_visible(False)

    figure_path = OUT / "T388_SAME_EVENT_ANTIPHASE_FIGURE.png"
    fig.savefig(figure_path, dpi=180, bbox_inches="tight")
    plt.close(fig)

    write_csv(OUT / "T388_PAIRED_EVENT_METRICS.csv", event_rows)
    write_csv(OUT / "T388_MEDIAN_PROFILES.csv", profile_rows(first, second))

    if direct_pass:
        status = "DIRECT DETECTOR REPETITION"
    elif full_pass:
        status = "FULL DIAGONAL ANTI-PHASE CANDIDATE"
    elif one_axis_pass:
        status = f"ONE-AXIS ANTI-PHASE CANDIDATE ({one_axis_winner})"
    else:
        status = "MIXED / UNIDENTIFIED"

    results = {
        "test": "T388",
        "status": status,
        "source": {"path": str(RAW), "sha256": raw_hash},
        "protocol": {"path": str(PROTOCOL), "sha256": protocol_hash},
        "population": {
            "eligible_evaluation_before_pair_filter": len(events),
            "paired_complete_events": len(retained),
            "medium": "95 L liquid scintillator",
            "identity_ceiling": "Class-D detector proxy",
        },
        "orientation": {
            "x_R": "0 contraction/retention, 1 equality ridge, 2 expansion/release",
            "x_H": "0 recurrent/closing, 1 path ridge, 2 open traversal",
        },
        "scores": score_summary,
        "deltas": deltas,
        "winner": winner,
        "same_loop_orientation_share": same_share,
        "gates": {
            "direct_repeat": direct_pass,
            "full_antiphase": full_pass,
            "one_axis_antiphase": one_axis_pass,
            "advance_handover": False,
        },
        "strict_pre_daughter": pre_summary,
        "claim_boundary": {
            "neutrinos_directly_observed": False,
            "upstream_muon_child_identified": False,
            "post_pulse_return_can_predict_creation": False,
        },
        "artifacts": {
            "figure": str(figure_path),
            "event_metrics": str(OUT / "T388_PAIRED_EVENT_METRICS.csv"),
            "profiles": str(OUT / "T388_MEDIAN_PROFILES.csv"),
        },
    }
    (OUT / "T388_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    report = f"""# T388 — same-event anti-phase identification result

## Outcome

**{status}**

T388 compared the ARA detector loop around the chronological stopped-muon
pulse with the later charged-daughter pulse in the same liquid-scintillator
record. It did not directly observe either neutrino.

## Population

- Eligible evaluation events before pair filtering: `{len(events):,}`
- Complete, non-overlapping paired loops: `{len(retained):,}`
- Native sample cadence: `8 ns`
- ARA window: `128 ns`
- Scored interval: `-256 ns` to `+512 ns` from each pulse minimum

## Frozen mapping scores

| Mapping | Median paired RMSE | 95% bootstrap CI |
|---|---:|---:|
"""
    for name in mapping_names:
        item = score_summary[name]
        report += f"| {mapping_labels[name]} | {item['median']:.6f} | [{item['ci95'][0]:.6f}, {item['ci95'][1]:.6f}] |\n"
    report += "\n### Reversal minus direct repetition\n\n| Reversal | Median difference | 95% bootstrap CI |\n|---|---:|---:|\n"
    for name in ("full", "radial", "path"):
        item = deltas[name]
        report += f"| {mapping_labels[name]} | {item['reversal_minus_direct']:+.6f} | [{item['ci95'][0]:+.6f}, {item['ci95'][1]:+.6f}] |\n"
    report += f"""

The lowest-error mapping was **{mapping_labels[winner]}**. The two pulse loops
retained the same handedness in **{same_share:.1%}** of paired events.

## Strict pre-daughter guard

At `-128 ns` relative to each pulse minimum:

- first-pulse median `(x_R,x_H)` = `({pre_summary['first_median'][0]:.6f}, {pre_summary['first_median'][1]:.6f})`;
- daughter-pulse median `(x_R,x_H)` = `({pre_summary['second_median'][0]:.6f}, {pre_summary['second_median'][1]:.6f})`;
- paired direct distance = `{pre_distance_med:.6f}` ARA units, 95% CI
  `[{pre_distance_ci[0]:.6f}, {pre_distance_ci[1]:.6f}]`.

T388 does not pass the advance-handover gate. T385 had already found no held-
out advance contribution outside the final `128 ns` visible-pulse guard.

## Meaning

This test identifies what the visible T387 opposite belongs to at the measured
boundary. A direct-repeat result says the expansion/opening and later
contraction/reclosure are principally the detector's response to an energy
deposit, repeated after both pulses. A reversal result would instead nominate
an anti-phase candidate for independent physical-lineage testing.

Even a clean reversal here would remain Class D. The muon's proposed retained-
connection child and the neutral-daughter release require a source that measures
their physical lineage rather than only the scintillator voltage response.
"""
    (OUT / "T388_SAME_EVENT_ANTIPHASE_REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps({"status": status, "n": len(retained), "winner": winner, "scores": score_summary, "same_orientation": same_share, "pre": pre_summary}, indent=2))


if __name__ == "__main__":
    main()
