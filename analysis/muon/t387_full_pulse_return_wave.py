#!/usr/bin/env python3
"""T387: map the full visible BUAP pulse and its state/path ARA return."""

from __future__ import annotations

import csv
import json
import math
import os
import sys
from dataclasses import dataclass
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


RAW = base.RAW
OUT = HERE / "T387_full_pulse_return_wave"
PROTOCOL = HERE / "T387_FULL_PULSE_RETURN_WAVE_PROTOCOL_2026-08-15.md"
EXPECTED_RAW_SHA256 = base.EXPECTED_RAW_SHA256
EXPECTED_PROTOCOL_SHA256 = "688F23BBAB7AFB44AB29E284CCC5CAB066BB285A49FC5D6D57960162C379D296"

DT_NS = 8
WINDOW_SAMPLES = (8, 16, 32)
TIMES_NS = np.arange(-1024, 769, DT_NS, dtype=int)
SEED = 387
EPS_MV = base.EPS_MV
LAG = base.LAG


@dataclass
class AlignedEvent:
    event: base.Event
    onset: int
    amplitude: float
    minimum_from_onset_ns: int


def detect_onset(event: base.Event) -> tuple[int, float] | None:
    y = event.values - event.causal_baseline
    amplitude = float(-y[event.second_index])
    if not math.isfinite(amplitude) or amplitude <= 0:
        return None
    threshold = -0.10 * amplitude
    lo = max(event.first_index + base.RECOVERY, event.second_index - 256 // DT_NS)
    hi = event.second_index - 2
    candidates = [i for i in range(lo, hi + 1) if np.all(y[i : i + 3] <= threshold)]
    if not candidates:
        return None
    runs: list[list[int]] = [[candidates[0]]]
    for item in candidates[1:]:
        if item == runs[-1][-1] + 1:
            runs[-1].append(item)
        else:
            runs.append([item])
    onset = runs[-1][0]
    return onset, amplitude


def coordinate_at(event: base.Event, endpoint: int, window: int) -> tuple[float, float] | None:
    first = endpoint - 2 * window + 1
    if first < event.first_index + base.RECOVERY or endpoint >= len(event.values):
        return None
    y = event.values - event.causal_baseline
    previous = y[endpoint - 2 * window + 1 : endpoint - window + 1]
    current = y[endpoint - window + 1 : endpoint + 1]
    if len(previous) != window or len(current) != window:
        return None
    rms_previous = float(np.sqrt(np.mean(previous**2)))
    rms_current = float(np.sqrt(np.mean(current**2)))
    ratio = (rms_current + EPS_MV) / (rms_previous + EPS_MV)
    x_r = float(np.clip(2.0 * ratio / (1.0 + ratio), 0.0, 2.0))
    _, _, x_h = base.path_metrics(current)
    return x_r, x_h


def bootstrap_median(values: np.ndarray, seed: int, n_boot: int = 1000) -> tuple[float, list[float]]:
    values = values[np.isfinite(values)]
    if len(values) == 0:
        return math.nan, [math.nan, math.nan]
    rng = np.random.default_rng(seed)
    medians = np.asarray([np.median(rng.choice(values, len(values), replace=True)) for _ in range(n_boot)])
    return float(np.median(values)), [float(np.quantile(medians, 0.025)), float(np.quantile(medians, 0.975))]


def matrix_profile(matrix: np.ndarray, window_ns: int, axis: str) -> list[dict]:
    rows = []
    for j, time_ns in enumerate(TIMES_NS):
        values = matrix[:, j]
        values = values[np.isfinite(values)]
        rows.append(
            {
                "window_ns": window_ns,
                "time_ns": int(time_ns),
                "axis": axis,
                "n": int(len(values)),
                "median": float(np.median(values)) if len(values) else math.nan,
                "q25": float(np.quantile(values, 0.25)) if len(values) else math.nan,
                "q75": float(np.quantile(values, 0.75)) if len(values) else math.nan,
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


def quadrant_label(x_r: float, x_h: float) -> str:
    sx = 1 if x_r > 1 else -1 if x_r < 1 else 0
    sy = 1 if x_h > 1 else -1 if x_h < 1 else 0
    if sx == 0 or sy == 0:
        return "ridge"
    return {(1, 1): "Ab", (1, -1): "aB", (-1, 1): "Ba", (-1, -1): "bA"}[(sx, sy)]


def analyse_window(events: list[AlignedEvent], window: int) -> tuple[np.ndarray, np.ndarray, dict, list[dict]]:
    n = len(events)
    x_r = np.full((n, len(TIMES_NS)), np.nan)
    x_h = np.full((n, len(TIMES_NS)), np.nan)
    radial_min = np.full(n, np.nan)
    radial_later = np.full(n, np.nan)
    path_min = np.full(n, np.nan)
    path_later = np.full(n, np.nan)

    for i, aligned in enumerate(events):
        event = aligned.event
        for j, time_ns in enumerate(TIMES_NS):
            endpoint = aligned.onset + int(time_ns // DT_NS)
            value = coordinate_at(event, endpoint, window)
            if value is not None:
                x_r[i, j], x_h[i, j] = value
        at_min = coordinate_at(event, event.second_index, window)
        after = coordinate_at(event, event.second_index + window, window)
        if at_min is not None:
            radial_min[i], path_min[i] = at_min
        if after is not None:
            radial_later[i], path_later[i] = after

    window_ns = window * DT_NS
    med_r = np.nanmedian(x_r, axis=0)
    med_h = np.nanmedian(x_h, axis=0)
    valid_profile = np.isfinite(med_r) & np.isfinite(med_h)
    search_peak = valid_profile & (TIMES_NS >= 0) & (TIMES_NS <= 128)
    search_trough = valid_profile & (TIMES_NS >= 0) & (TIMES_NS <= window_ns + 256)
    peak_i = np.flatnonzero(search_peak)[int(np.argmax(med_r[search_peak]))]
    trough_i = np.flatnonzero(search_trough)[int(np.argmin(med_r[search_trough]))]
    peak_time = int(TIMES_NS[peak_i])
    trough_time = int(TIMES_NS[trough_i])

    pre_i = int(np.where(TIMES_NS == -256)[0][0])
    final_i = int(np.where(TIMES_NS == 768)[0][0])
    pre = np.asarray([med_r[pre_i], med_h[pre_i]])
    final = np.asarray([med_r[final_i], med_h[final_i]])
    loop_mask = valid_profile & (TIMES_NS >= 0) & (TIMES_NS <= window_ns + 256)
    loop_points = np.column_stack([med_r[loop_mask], med_h[loop_mask]])
    distances = np.linalg.norm(loop_points - pre, axis=1)
    max_distance = float(np.max(distances))
    final_distance = float(np.linalg.norm(final - pre))
    return_fraction = float(1.0 - final_distance / max_distance) if max_distance > 0 else math.nan

    mirror = radial_min + radial_later - 2.0
    radial_min_med, radial_min_ci = bootstrap_median(radial_min, SEED + window)
    radial_later_med, radial_later_ci = bootstrap_median(radial_later, SEED + 100 + window)
    mirror_med, mirror_ci = bootstrap_median(mirror, SEED + 200 + window)

    max_xh = float(np.nanmax(med_h[loop_mask]))
    final_xh = float(med_h[final_i])
    pre_xh = float(med_h[pre_i])
    pre_side = -1 if pre_xh < 1 else 1 if pre_xh > 1 else 0
    crosses = bool((pre_side < 0 and max_xh > 1 and final_xh < 1) or (pre_side > 0 and np.nanmin(med_h[loop_mask]) < 1 and final_xh > 1))

    phases = {
        "pre": (TIMES_NS >= -512) & (TIMES_NS <= -128),
        "pulse": (TIMES_NS >= 0) & (TIMES_NS <= window_ns),
        "recovery": (TIMES_NS > window_ns) & (TIMES_NS <= window_ns + 256),
    }
    occupancy: list[dict] = []
    for phase, time_mask in phases.items():
        labels = []
        for i in range(n):
            for j in np.flatnonzero(time_mask):
                if np.isfinite(x_r[i, j]) and np.isfinite(x_h[i, j]):
                    labels.append(quadrant_label(float(x_r[i, j]), float(x_h[i, j])))
        for label in ("Ab", "aB", "Ba", "bA", "ridge"):
            count = labels.count(label)
            occupancy.append(
                {
                    "window_ns": window_ns,
                    "phase": phase,
                    "quadrant": label,
                    "count": count,
                    "share": count / len(labels) if labels else math.nan,
                }
            )

    summary = {
        "window_ns": window_ns,
        "n_events": n,
        "radial_at_minimum": radial_min_med,
        "radial_at_minimum_ci95": radial_min_ci,
        "radial_one_window_later": radial_later_med,
        "radial_one_window_later_ci95": radial_later_ci,
        "mirror_residual": mirror_med,
        "mirror_residual_ci95": mirror_ci,
        "path_at_minimum": float(np.nanmedian(path_min)),
        "path_one_window_later": float(np.nanmedian(path_later)),
        "path_pre_minus256": pre_xh,
        "path_max_event_interval": max_xh,
        "path_final_plus768": final_xh,
        "path_crosses_and_returns": crosses,
        "radial_peak_time_ns_from_onset": peak_time,
        "radial_peak_value": float(med_r[peak_i]),
        "radial_trough_time_ns_from_onset": trough_time,
        "radial_trough_value": float(med_r[trough_i]),
        "post_result_extrema_mirror_residual": float(
            med_r[peak_i] + med_r[trough_i] - 2.0
        ),
        "trough_time_minus_window_ns": trough_time - window_ns,
        "pre_point": pre.tolist(),
        "final_point": final.tolist(),
        "maximum_displacement": max_distance,
        "final_distance": final_distance,
        "return_fraction": return_fraction,
    }
    return x_r, x_h, summary, occupancy


def make_figure(
    raw_profile: list[dict],
    profile_rows: list[dict],
    summaries: list[dict],
    path: Path,
) -> None:
    blue, orange, olive = "#3F6FAE", "#D89432", "#71814A"
    charcoal, grey = "#202833", "#98A2AE"
    colors = {64: blue, 128: orange, 256: olive}
    fig, axes = plt.subplots(3, 2, figsize=(17, 15), constrained_layout=True)
    fig.patch.set_facecolor("#FAFBFC")
    for ax in axes.ravel():
        ax.set_facecolor("#FFFFFF")
        ax.grid(True, color="#E5E9EF", linewidth=0.8)
        for spine in ax.spines.values():
            spine.set_color("#B7C0CA")

    ax = axes[0, 0]
    t = np.asarray([r["time_ns"] for r in raw_profile])
    med = np.asarray([r["median"] for r in raw_profile])
    q25 = np.asarray([r["q25"] for r in raw_profile])
    q75 = np.asarray([r["q75"] for r in raw_profile])
    ax.plot(t, med, color=blue, linewidth=2, label=f"median normalized voltage · n<={max(r['n'] for r in raw_profile):,}")
    ax.fill_between(t, q25, q75, color=blue, alpha=0.18, label="interquartile range")
    ax.axvline(0, color=charcoal, linewidth=1.2, label="10% pulse onset")
    ax.axhline(0, color=grey, linewidth=1)
    ax.set_xlabel("Time from second-pulse onset (ns)")
    ax.set_ylabel("Voltage / pulse amplitude (0 baseline; negative pulse)")
    ax.set_title("Visible detector waveform and recovery", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8)

    for plot_ax, axis_name, title, ylabel in (
        (axes[0, 1], "x_radial", "Radial state through the full pulse", "x_R: 0 contraction - 1 ridge - 2 expansion"),
        (axes[1, 0], "x_history", "Path state through the full pulse", "x_H: 0 recurrent - 1 ridge - 2 open"),
    ):
        for window_ns in (64, 128, 256):
            items = [r for r in profile_rows if r["window_ns"] == window_ns and r["axis"] == axis_name]
            tx = np.asarray([r["time_ns"] for r in items])
            md = np.asarray([r["median"] for r in items])
            lo = np.asarray([r["q25"] for r in items])
            hi = np.asarray([r["q75"] for r in items])
            plot_ax.plot(tx, md, color=colors[window_ns], linewidth=2, label=f"{window_ns} ns window")
            plot_ax.fill_between(tx, lo, hi, color=colors[window_ns], alpha=0.10)
        plot_ax.axhline(1, color=charcoal, linestyle="--", linewidth=1.2, label="ARA ridge 1")
        plot_ax.axvline(0, color=charcoal, linewidth=1)
        plot_ax.set_xlim(-1050, 800)
        plot_ax.set_ylim(0, 2)
        plot_ax.set_xlabel("Time from second-pulse onset (ns)")
        plot_ax.set_ylabel(ylabel)
        plot_ax.set_title(title, loc="left", fontweight="bold")
        plot_ax.legend(frameon=False, fontsize=8, ncol=2)

    ax = axes[1, 1]
    for window_ns in (64, 128, 256):
        radial = {r["time_ns"]: r["median"] for r in profile_rows if r["window_ns"] == window_ns and r["axis"] == "x_radial"}
        history = {r["time_ns"]: r["median"] for r in profile_rows if r["window_ns"] == window_ns and r["axis"] == "x_history"}
        upper = window_ns + 256
        times = [tt for tt in TIMES_NS if -256 <= tt <= upper and tt in radial and tt in history]
        ax.plot([radial[tt] for tt in times], [history[tt] for tt in times], color=colors[window_ns], linewidth=2, label=f"{window_ns} ns window")
        for marker_time, marker in ((-256, "o"), (0, "s"), (window_ns, "^") ):
            if marker_time in radial:
                ax.scatter(radial[marker_time], history[marker_time], color=colors[window_ns], marker=marker, s=55, edgecolor=charcoal, linewidth=0.5)
    ax.axvline(1, color=charcoal, linewidth=1.2)
    ax.axhline(1, color=charcoal, linewidth=1.2)
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    ax.set_xlabel("x_R radial state")
    ax.set_ylabel("x_H path state")
    ax.set_title("Median state/path trajectories", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8)
    ax.text(0.03, 0.03, "markers: circle=-256 ns · square=onset · triangle=one window", transform=ax.transAxes, fontsize=8, color=charcoal)

    ax = axes[2, 0]
    x = np.arange(3)
    width = 0.34
    ax.bar(x - width / 2, [s["radial_at_minimum"] for s in summaries], width, color=orange, label="at pulse minimum")
    ax.bar(x + width / 2, [s["radial_one_window_later"] for s in summaries], width, color=blue, label="one window later")
    ax.axhline(1, color=charcoal, linestyle="--", linewidth=1.2, label="ARA ridge 1")
    ax.set_xticks(x, [f"{s['window_ns']} ns" for s in summaries])
    ax.set_ylim(0, 2)
    ax.set_ylabel("Median x_R (event-level paired coordinates)")
    ax.set_title("Expansion and proposed opposite radial half", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8)
    for i, s in enumerate(summaries):
        ax.text(i, 0.06, f"sum-2={s['mirror_residual']:+.3f}", ha="center", fontsize=8, color=charcoal)

    ax = axes[2, 1]
    windows = np.asarray([s["window_ns"] for s in summaries])
    peaks = np.asarray([s["radial_peak_time_ns_from_onset"] for s in summaries])
    troughs = np.asarray([s["radial_trough_time_ns_from_onset"] for s in summaries])
    median_min = float(np.median([r["minimum_from_onset_ns"] for r in raw_profile if "minimum_from_onset_ns" in r])) if raw_profile and "minimum_from_onset_ns" in raw_profile[0] else 0.0
    ax.plot(windows, peaks, marker="o", color=orange, linewidth=2, label="x_R expansion peak")
    ax.plot(windows, troughs, marker="s", color=blue, linewidth=2, label="x_R contraction trough")
    ax.plot(windows, windows + median_min, linestyle="--", color=grey, linewidth=1.5, label="pulse minimum + one window")
    ax.set_xlabel("Analysis window duration (ns)")
    ax.set_ylabel("Feature time from pulse onset (ns)")
    ax.set_title("Does the return translate with the window?", loc="left", fontweight="bold")
    ax.legend(frameon=False, fontsize=8)

    fig.suptitle(
        "T387 - full visible pulse and state/path return\n"
        "Same BUAP liquid-scintillator events · retrospective detector map",
        fontsize=18,
        color=charcoal,
    )
    fig.savefig(path, dpi=190, facecolor=fig.get_facecolor())
    plt.close(fig)


def make_report(results: dict, path: Path) -> None:
    text = f"""# T387 — full-pulse return-wave result

## Outcome

**{results['status']}**

{results['plain_language']}

This is a retrospective Class-D liquid-scintillator detector result. It does
not provide advance neutrino timing and does not directly observe the proposed
upstream muon handover.

## Exact window comparison

| Window | Events | x_R at pulse minimum | 95% CI | x_R one window later | 95% CI | mirror residual | x_H maximum | return fraction | trough time |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
"""
    for s in results["windows"]:
        text += (
            f"| {s['window_ns']} ns | {s['n_events']} | {s['radial_at_minimum']:.5f} | "
            f"[{s['radial_at_minimum_ci95'][0]:.5f},{s['radial_at_minimum_ci95'][1]:.5f}] | "
            f"{s['radial_one_window_later']:.5f} | "
            f"[{s['radial_one_window_later_ci95'][0]:.5f},{s['radial_one_window_later_ci95'][1]:.5f}] | "
            f"{s['mirror_residual']:+.5f} | {s['path_max_event_interval']:.5f} | "
            f"{s['return_fraction']:.1%} | {s['radial_trough_time_ns_from_onset']} ns |\n"
        )
    text += f"""

## Frozen gates

- {'PASS' if results['gates']['opposite_radial_half_recovered'] else 'FAIL'} — opposite radial half recovered.
- {'PASS' if results['gates']['approximate_radial_mirror'] else 'FAIL'} — approximate radial mirror (`|sum-2|<=0.10`).
- {'PASS' if results['gates']['opposite_path_half_recovered'] else 'FAIL'} — `x_H` crosses ridge and returns.
- {'PASS' if results['gates']['local_loop_return'] else 'FAIL'} — at least 75% return by `+768 ns`.
- Timing classification: **{results['timing']['classification']}**; trough-time slope `{results['timing']['slope_ns_per_window_ns']:.3f}`.

## Interpretation

An `x_R` expansion followed by contraction is partly expected from comparing
adjacent RMS windows: activity first enters the current window and later sits
in the previous window. Its timing-scale test determines whether that symmetry
is predominantly instrument-generated or physically anchored.

The stronger claim requires the independent path coordinate to cross its own
ridge and return. If `x_H` remains on one side, the test has recovered a radial
pair inside only one half of the state/path Di-ARA, not a complete local
two-axis wave.

### Post-result extrema observation

The actual median `x_R` expansion peaks and contraction troughs were much more
nearly complementary than the frozen pulse-minimum/one-window-later pair:
their `peak + trough - 2` residuals were
`{results['post_result_observation']['extrema_mirror_residuals'][0]:+.5f}`,
`{results['post_result_observation']['extrema_mirror_residuals'][1]:+.5f}` and
`{results['post_result_observation']['extrema_mirror_residuals'][2]:+.5f}` for
64, 128 and 256 ns. This is exploratory and does not replace the failed frozen
mirror gate. It is partly induced by the same pulse energy moving between the
two adjacent RMS windows, for which `x_R(1/s)=2-x_R(s)` exactly.

## Reproduction

```powershell
python analysis/muon/t387_full_pulse_return_wave.py
python analysis/muon/validate_t387_full_pulse_return_wave.py
```
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    source_hash = base.sha256(RAW)
    protocol_hash = base.sha256(PROTOCOL)
    if source_hash != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"source hash mismatch: {source_hash}")
    if protocol_hash != EXPECTED_PROTOCOL_SHA256:
        raise RuntimeError(f"protocol hash mismatch: {protocol_hash}")

    loaded = base.load_events(RAW)
    aligned: list[AlignedEvent] = []
    onset_excluded = 0
    for event in loaded:
        if event.split != "evaluation" or not event.eligible:
            continue
        detected = detect_onset(event)
        if detected is None:
            onset_excluded += 1
            continue
        onset, amplitude = detected
        aligned.append(
            AlignedEvent(
                event=event,
                onset=onset,
                amplitude=amplitude,
                minimum_from_onset_ns=(event.second_index - onset) * DT_NS,
            )
        )

    raw = np.full((len(aligned), len(TIMES_NS)), np.nan)
    for i, item in enumerate(aligned):
        y = item.event.values - item.event.causal_baseline
        for j, time_ns in enumerate(TIMES_NS):
            index = item.onset + int(time_ns // DT_NS)
            if 0 <= index < len(y):
                raw[i, j] = y[index] / item.amplitude
    median_minimum_from_onset_ns = float(
        np.median([a.minimum_from_onset_ns for a in aligned])
    )
    raw_profile: list[dict] = []
    for j, time_ns in enumerate(TIMES_NS):
        values = raw[:, j]
        values = values[np.isfinite(values)]
        raw_profile.append(
            {
                "time_ns": int(time_ns),
                "n": int(len(values)),
                "median": float(np.median(values)) if len(values) else math.nan,
                "q25": float(np.quantile(values, 0.25)) if len(values) else math.nan,
                "q75": float(np.quantile(values, 0.75)) if len(values) else math.nan,
                "minimum_from_onset_ns": median_minimum_from_onset_ns,
            }
        )

    profiles: list[dict] = []
    summaries: list[dict] = []
    occupancy: list[dict] = []
    for window in WINDOW_SAMPLES:
        xr, xh, summary, occ = analyse_window(aligned, window)
        profiles.extend(matrix_profile(xr, window * DT_NS, "x_radial"))
        profiles.extend(matrix_profile(xh, window * DT_NS, "x_history"))
        summaries.append(summary)
        occupancy.extend(occ)

    windows = np.asarray([s["window_ns"] for s in summaries], dtype=float)
    troughs = np.asarray([s["radial_trough_time_ns_from_onset"] for s in summaries], dtype=float)
    shifted = troughs - windows
    slope = float(np.polyfit(windows, troughs, 1)[0])
    window_translated = bool(np.ptp(shifted) <= 32 and 0.75 <= slope <= 1.25)
    physically_anchored = bool(np.ptp(troughs) <= 32)
    timing_class = "WINDOW-TRANSLATED" if window_translated else "PHYSICALLY ANCHORED" if physically_anchored else "MIXED / UNDETERMINED"

    gates = {
        "opposite_radial_half_recovered": all(
            s["radial_at_minimum_ci95"][0] > 1 and s["radial_one_window_later_ci95"][1] < 1
            for s in summaries
        ),
        "approximate_radial_mirror": all(abs(s["mirror_residual"]) <= 0.10 for s in summaries),
        "opposite_path_half_recovered": all(s["path_crosses_and_returns"] for s in summaries),
        "local_loop_return": all(s["return_fraction"] >= 0.75 for s in summaries),
    }

    if all(gates.values()) and physically_anchored:
        status = "LOCAL DETECTOR LOOP SUPPORTED"
        plain = "Both state/path coordinates completed a physically anchored out-and-return loop across all frozen window sizes."
    elif gates["opposite_radial_half_recovered"] and window_translated:
        status = "WINDOW-TRANSLATED RADIAL RETURN"
        plain = "The missing radial contraction was recovered, but its timing moved with the analysis window; this is a coherent detector-coordinate pair, not independent evidence of an upstream physical wave."
    elif (
        gates["opposite_radial_half_recovered"]
        and gates["opposite_path_half_recovered"]
        and gates["local_loop_return"]
    ):
        status = "NON-MIRRORED TWO-AXIS RETURN"
        plain = "Both state/path coordinates crossed and returned, closing the median detector loop, but the radial halves were unequal and the return timing was neither physically fixed nor a one-window translation."
    elif gates["opposite_radial_half_recovered"]:
        status = "PARTIAL RADIAL RETURN"
        plain = "The missing radial contraction was recovered, while the full path return or timing interpretation remained incomplete."
    else:
        status = "RETURN NOT RECOVERED"
        plain = "The frozen multi-window map did not recover the proposed opposite detector return."

    results = {
        "test": "T387",
        "status": status,
        "plain_language": plain,
        "source": {
            "path": str(RAW),
            "sha256": source_hash,
            "protocol": str(PROTOCOL),
            "protocol_sha256": protocol_hash,
            "medium": "BUAP 95 L liquid scintillator",
            "claim_class": "D retrospective detector waveform",
        },
        "cohort": {
            "aligned_events": len(aligned),
            "onset_rule_excluded": onset_excluded,
            "median_minimum_from_onset_ns": median_minimum_from_onset_ns,
            "time_range_ns": [int(TIMES_NS[0]), int(TIMES_NS[-1])],
        },
        "windows": summaries,
        "timing": {
            "classification": timing_class,
            "trough_times_ns": troughs.tolist(),
            "trough_minus_window_ns": shifted.tolist(),
            "slope_ns_per_window_ns": slope,
            "window_translated": window_translated,
            "physically_anchored": physically_anchored,
        },
        "gates": gates,
        "post_result_observation": {
            "extrema_mirror_residuals": [
                s["post_result_extrema_mirror_residual"] for s in summaries
            ],
            "trough_time_over_window": [
                s["radial_trough_time_ns_from_onset"] / s["window_ns"]
                for s in summaries
            ],
            "status": "exploratory; not a replacement for the frozen fixed-time mirror gate",
            "forced_component": "adjacent RMS windows approximately exchange the same pulse energy, and x_R(1/s)=2-x_R(s)",
        },
        "boundary": {
            "retrospective_not_predictive": True,
            "radial_mirror_partly_induced_by_adjacent_windows": True,
            "upstream_handover_directly_observed": False,
        },
    }

    write_csv(OUT / "T387_RAW_WAVEFORM_PROFILE.csv", raw_profile)
    write_csv(OUT / "T387_ARA_TIME_PROFILES.csv", profiles)
    write_csv(OUT / "T387_QUADRANT_OCCUPANCY.csv", occupancy)
    write_csv(OUT / "T387_WINDOW_SUMMARY.csv", [
        {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in s.items()} for s in summaries
    ])
    (OUT / "T387_RESULTS.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(raw_profile, profiles, summaries, OUT / "T387_FULL_PULSE_RETURN_FIGURE.png")
    make_report(results, OUT / "T387_FULL_PULSE_RETURN_REPORT.md")
    print(json.dumps({"status": status, "gates": gates, "timing": results["timing"], "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
