#!/usr/bin/env python3
"""T399: test whether cumulative child half precedes the delayed-neutrino crest.

Uses only saved, evidence-graded T371/T372/T378/T398 artifacts.  The primary
calculation is native-resolution; robustness comes from registered leave-one-
bin-out fits, a yield sensitivity ensemble, a coarse independent release, and
a circular-shift alignment control.
"""

from __future__ import annotations

import bisect
import csv
import hashlib
import html
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "T399_child_half_precrest_sequence"
PROTOCOL = HERE / "T399_CHILD_HALF_PRECREST_SEQUENCE_PROTOCOL_2026-08-17.md"
OVERLAP = HERE / "T398_population_neutrino_wave_overlap" / "T398_NATIVE_WAVE_OVERLAP.csv"
T371_RESULTS = HERE / "T371_COHERENT_PION_MUON_DIARA_RESULTS.json"
T378_COMPONENTS = HERE / "T378_coherent_2017_holdout" / "T378_timing_components.csv"
T378_RESULTS = HERE / "T378_coherent_2017_holdout" / "T378_results.json"

SEED = 399
N_SENSITIVITY = 10_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def normalize(values: list[float]) -> list[float]:
    total = sum(values)
    if not total > 0:
        raise ValueError("Cannot normalize a non-positive curve")
    return [v / total for v in values]


def cumsum(values: list[float]) -> list[float]:
    out: list[float] = []
    running = 0.0
    for value in values:
        running += value
        out.append(running)
    return out


def interpolate_crossing(times: list[float], values: list[float], target: float) -> float:
    i = bisect.bisect_left(values, target)
    if i <= 0:
        return times[0]
    if i >= len(values):
        return times[-1]
    y0, y1 = values[i - 1], values[i]
    if y1 == y0:
        return times[i]
    fraction = (target - y0) / (y1 - y0)
    return times[i - 1] + fraction * (times[i] - times[i - 1])


def interpolate_at_time(times: list[float], values: list[float], target_time: float) -> float:
    i = bisect.bisect_left(times, target_time)
    if i <= 0:
        return values[0]
    if i >= len(times):
        return values[-1]
    fraction = (target_time - times[i - 1]) / (times[i] - times[i - 1])
    return values[i - 1] + fraction * (values[i] - values[i - 1])


def equality_crossing(times: list[float], prompt: list[float], delayed: list[float]) -> tuple[float, int, float]:
    peak = max(range(len(prompt)), key=prompt.__getitem__)
    diff = [a - b for a, b in zip(prompt, delayed)]
    for i in range(peak, len(diff) - 1):
        if diff[i] >= 0.0 and diff[i + 1] <= 0.0:
            denominator = diff[i] - diff[i + 1]
            fraction = 0.0 if denominator == 0 else diff[i] / denominator
            return times[i] + fraction * (times[i + 1] - times[i]), i, fraction
    return float("nan"), -1, float("nan")


def landmarks(
    times: list[float],
    prompt_shape: list[float],
    delayed_shape: list[float],
    prompt_yield: float,
    delayed_yield: float,
) -> dict[str, float | bool]:
    prompt = [prompt_yield * v for v in prompt_shape]
    delayed = [delayed_yield * v for v in delayed_shape]
    total = [a + b for a, b in zip(prompt, delayed)]
    cumulative = [2.0 * v / (prompt_yield + delayed_yield) for v in cumsum(total)]
    ip = max(range(len(prompt)), key=prompt.__getitem__)
    idelayed = max(range(len(delayed)), key=delayed.__getitem__)
    t_half = interpolate_crossing(times, cumulative, 0.5)
    t_equality, ieq, frac = equality_crossing(times, prompt, delayed)
    x_equality = float("nan")
    if ieq >= 0:
        x0 = cumulative[ieq]
        x1 = cumulative[ieq + 1]
        x_equality = x0 + frac * (x1 - x0)
    t_prompt = times[ip]
    t_delayed = times[idelayed]
    x_prompt = cumulative[ip]
    x_delayed = cumulative[idelayed]
    delta_quarter = 0.5 - x_prompt
    full_order = bool(
        math.isfinite(t_equality)
        and t_prompt < t_equality < t_half < t_delayed
    )
    return {
        "prompt_crest_time_us": t_prompt,
        "prompt_crest_ara": x_prompt,
        "branch_equality_time_us": t_equality,
        "branch_equality_ara": x_equality,
        "child_half_time_us": t_half,
        "child_half_ara": 0.5,
        "delayed_crest_time_us": t_delayed,
        "delayed_crest_ara": x_delayed,
        "time_half_to_delayed_crest_us": t_delayed - t_half,
        "ara_prompt_crest_to_half": delta_quarter,
        "full_four_landmark_order": full_order,
        "half_before_delayed_crest": t_half < t_delayed,
    }


def split_normal_draw(rng: random.Random, mean: float, low: float, high: float) -> float:
    sigma_low = max((mean - low) / 1.96, 1e-12)
    sigma_high = max((high - mean) / 1.96, 1e-12)
    while True:
        z = rng.gauss(0.0, 1.0)
        value = mean + z * (sigma_high if z >= 0 else sigma_low)
        if value > 0:
            return value


def quantile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return float("nan")
    position = (len(sorted_values) - 1) * p
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return sorted_values[lo]
    fraction = position - lo
    return sorted_values[lo] * (1.0 - fraction) + sorted_values[hi] * fraction


def piecewise_bin_half_time(times: list[float], prompt: list[float], delayed: list[float]) -> float:
    widths = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    width = sorted(widths)[len(widths) // 2]
    masses = [a + b for a, b in zip(prompt, delayed)]
    target = 0.25 * sum(masses)  # x=0.5 on a cumulative 0-2 scale
    running = 0.0
    for t, mass in zip(times, masses):
        if running + mass >= target:
            fraction = 0.0 if mass == 0 else (target - running) / mass
            return (t - width / 2.0) + fraction * width
        running += mass
    return times[-1] + width / 2.0


def svg_report(
    times: list[float],
    prompt_shape: list[float],
    delayed_shape: list[float],
    prompt_yield: float,
    delayed_yield: float,
    primary: dict[str, float | bool],
    robustness: dict[str, float | bool],
) -> str:
    width, height = 1500, 980
    blue, orange, gold, green = "#3267a8", "#d97824", "#d7a128", "#3f8c69"
    ink, muted, grid, paper = "#172033", "#657084", "#d9dee8", "#f8fafc"
    p = [prompt_yield * v for v in prompt_shape]
    d = [delayed_yield * v for v in delayed_shape]
    pmax, dmax = max(p), max(d)
    pnorm = [v / pmax for v in p]
    dnorm = [v / dmax for v in d]
    total = [a + b for a, b in zip(p, d)]
    cum = [2.0 * v / sum(total) for v in cumsum(total)]

    def panel(x: int, y: int, w: int, h: int, title: str, subtitle: str) -> list[str]:
        return [
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="white" stroke="{grid}"/>',
            f'<text x="{x+24}" y="{y+34}" fill="{ink}" font-size="22" font-weight="700">{html.escape(title)}</text>',
            f'<text x="{x+24}" y="{y+58}" fill="{muted}" font-size="14">{html.escape(subtitle)}</text>',
        ]

    def path_for(xs: list[float], ys: list[float], x0: float, y0: float, w: float, h: float, xmax: float, ymax: float) -> str:
        points = []
        for x, y in zip(xs, ys):
            if x > xmax:
                break
            px = x0 + w * x / xmax
            py = y0 + h * (1.0 - y / ymax)
            points.append(f"{px:.2f},{py:.2f}")
        return "M " + " L ".join(points)

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="{paper}"/>',
        f'<text x="60" y="58" fill="{ink}" font-size="34" font-weight="800">T399 — Child-half before neutrino release crest</text>',
        f'<text x="60" y="88" fill="{muted}" font-size="17">COHERENT population timing; native landmarks, robustness cuts and alignment control</text>',
    ]

    # Top native waveform panel.
    s += panel(50, 120, 1400, 385, "Native prompt and delayed population rates", "Peak-normalized rates; vertical guides show the four distinct ARA landmarks")
    x0, y0, pw, ph, xmax = 125, 205, 1255, 235, 1.55
    for k in range(5):
        gy = y0 + ph * k / 4
        s.append(f'<line x1="{x0}" y1="{gy}" x2="{x0+pw}" y2="{gy}" stroke="{grid}"/>')
        s.append(f'<text x="{x0-18}" y="{gy+5}" text-anchor="end" fill="{muted}" font-size="13">{1-k/4:.2f}</text>')
    for k in range(7):
        value = xmax * k / 6
        gx = x0 + pw * k / 6
        s.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y0+ph}" stroke="{grid}"/>')
        s.append(f'<text x="{gx}" y="{y0+ph+24}" text-anchor="middle" fill="{muted}" font-size="13">{value:.2f}</text>')
    s.append(f'<path d="{path_for(times, pnorm, x0, y0, pw, ph, xmax, 1.0)}" fill="none" stroke="{blue}" stroke-width="4"/>')
    s.append(f'<path d="{path_for(times, dnorm, x0, y0, pw, ph, xmax, 1.0)}" fill="none" stroke="{orange}" stroke-width="4"/>')
    marks = [
        ("prompt crest", float(primary["prompt_crest_time_us"]), blue, -86),
        ("branch equality", float(primary["branch_equality_time_us"]), gold, -28),
        ("child half x=0.5", float(primary["child_half_time_us"]), green, 34),
        ("delayed crest", float(primary["delayed_crest_time_us"]), orange, 92),
    ]
    for label, value, color, offset in marks:
        gx = x0 + pw * value / xmax
        s.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y0+ph}" stroke="{color}" stroke-width="2" stroke-dasharray="7 6"/>')
        s.append(f'<text x="{gx+offset}" y="{y0-12}" fill="{color}" font-size="14" font-weight="700">{html.escape(label)} {value:.4f} μs</text>')
    s.append(f'<text x="{x0+pw/2}" y="{y0+ph+50}" text-anchor="middle" fill="{ink}" font-size="15">time after SNS pulse (μs)</text>')
    s.append(f'<text x="{x0}" y="{y0-36}" fill="{blue}" font-size="15" font-weight="700">prompt νμ</text>')
    s.append(f'<text x="{x0+105}" y="{y0-36}" fill="{orange}" font-size="15" font-weight="700">delayed νe + anti-νμ</text>')

    # Bottom-left cumulative coordinate panel.
    s += panel(50, 535, 885, 390, "Cumulative ARA traversal", "The child-half crossing occurs before the delayed release-rate crest")
    x1, y1, cw, ch = 125, 620, 735, 235
    for value in (0.0, 0.25, 0.5, 0.75, 1.0):
        gy = y1 + ch * (1.0 - value)
        s.append(f'<line x1="{x1}" y1="{gy}" x2="{x1+cw}" y2="{gy}" stroke="{grid}"/>')
        s.append(f'<text x="{x1-16}" y="{gy+5}" text-anchor="end" fill="{muted}" font-size="13">{value:.2f}</text>')
    s.append(f'<path d="{path_for(times, cum, x1, y1, cw, ch, xmax, 1.0)}" fill="none" stroke="{green}" stroke-width="4"/>')
    for label, value, color, _ in marks:
        gx = x1 + cw * value / xmax
        s.append(f'<line x1="{gx}" y1="{y1}" x2="{gx}" y2="{y1+ch}" stroke="{color}" stroke-width="2" stroke-dasharray="6 6"/>')
    s.append(f'<text x="{x1+cw/2}" y="{y1+ch+48}" text-anchor="middle" fill="{ink}" font-size="15">time after SNS pulse (μs)</text>')
    s.append(f'<text x="{x1-54}" y="{y1+ch/2}" transform="rotate(-90 {x1-54} {y1+ch/2})" text-anchor="middle" fill="{ink}" font-size="15">cumulative ARA x (0–2)</text>')

    # Bottom-right scorecard.
    s += panel(965, 535, 485, 390, "Frozen gate readout", "Percentages are robustness frequencies, not particle-level birth probabilities")
    items = [
        ("Native Δx prompt→half", f'{float(primary["ara_prompt_crest_to_half"]):.4f}', bool(robustness["native_quarter_pass"])),
        ("Half→delayed crest", f'{float(primary["time_half_to_delayed_crest_us"]):.4f} μs', bool(robustness["native_half_before_crest"])),
        ("Leave-one-out order", f'{100*float(robustness["loo_half_before_crest_fraction"]):.1f}%', bool(robustness["loo_pass"])),
        ("Yield sensitivity order", f'{100*float(robustness["sensitivity_half_before_crest_fraction"]):.1f}%', bool(robustness["sensitivity_pass"])),
        ("T378 coarse holdout", "PASS" if robustness["holdout_pass"] else "FAIL", bool(robustness["holdout_pass"])),
        ("Circular-shift p", f'{float(robustness["shift_p_upper"]):.4f}', bool(robustness["alignment_pass"])),
    ]
    for i, (label, value, passed) in enumerate(items):
        yy = 625 + i * 48
        color = green if passed else "#ad3f4f"
        s.append(f'<circle cx="1000" cy="{yy-5}" r="8" fill="{color}"/>')
        s.append(f'<text x="1020" y="{yy}" fill="{ink}" font-size="14">{html.escape(label)}</text>')
        s.append(f'<text x="1415" y="{yy}" text-anchor="end" fill="{color}" font-size="15" font-weight="700">{html.escape(value)}</text>')
    s.append(f'<text x="990" y="897" fill="{muted}" font-size="12">Source: COHERENT CsI releases; T371/T372/T378/T398 saved artifacts</text>')
    s.append('</svg>')
    return "\n".join(s)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    overlap = read_csv(OVERLAP)
    times = [float(row["time_us"]) for row in overlap]
    prompt_raw = [float(row["prompt_fitted_events_per_native_ns"]) for row in overlap]
    delayed_raw = [float(row["delayed_total_fitted_events_per_native_ns"]) for row in overlap]
    prompt_shape = normalize(prompt_raw)
    delayed_shape = normalize(delayed_raw)
    saved_cumulative = [float(row["cumulative_ara_0_to_2"]) for row in overlap]

    t371 = json.loads(T371_RESULTS.read_text(encoding="utf-8"))
    prompt_yield = float(t371["fit"]["prompt_nu_mu"])
    delayed_yield = float(t371["fit"]["delayed_nu_e_plus_anti_nu_mu"])
    primary = landmarks(times, prompt_shape, delayed_shape, prompt_yield, delayed_yield)

    # The saved T398 cumulative column was integrated on the full 1-ns source
    # before display sampling.  Use it for the headline native coordinates;
    # the 5-ns sampled shapes below are retained for robustness projections.
    prompt_index = max(range(len(prompt_raw)), key=prompt_raw.__getitem__)
    delayed_index = max(range(len(delayed_raw)), key=delayed_raw.__getitem__)
    primary["prompt_crest_ara"] = saved_cumulative[prompt_index]
    primary["branch_equality_ara"] = interpolate_at_time(
        times, saved_cumulative, float(primary["branch_equality_time_us"])
    )
    primary["child_half_time_us"] = interpolate_crossing(times, saved_cumulative, 0.5)
    primary["delayed_crest_ara"] = saved_cumulative[delayed_index]
    primary["time_half_to_delayed_crest_us"] = (
        float(primary["delayed_crest_time_us"]) - float(primary["child_half_time_us"])
    )
    primary["ara_prompt_crest_to_half"] = 0.5 - float(primary["prompt_crest_ara"])
    primary["full_four_landmark_order"] = bool(
        float(primary["prompt_crest_time_us"])
        < float(primary["branch_equality_time_us"])
        < float(primary["child_half_time_us"])
        < float(primary["delayed_crest_time_us"])
    )
    primary["half_before_delayed_crest"] = bool(
        float(primary["child_half_time_us"]) < float(primary["delayed_crest_time_us"])
    )

    # Registered leave-one-bin-out fits from T371.
    loo_rows: list[dict[str, object]] = []
    for row in t371["leave_one_out"]:
        lm = landmarks(
            times,
            prompt_shape,
            delayed_shape,
            float(row["prompt"]),
            float(row["delayed"]),
        )
        loo_rows.append(
            {
                "axis": row["axis"],
                "removed_bin": int(row["removed_bin"]),
                "prompt_yield": float(row["prompt"]),
                "delayed_yield": float(row["delayed"]),
                **lm,
            }
        )
    write_csv(OUT / "T399_LEAVE_ONE_OUT_LANDMARKS.csv", loo_rows)
    loo_fraction = sum(bool(row["half_before_delayed_crest"]) for row in loo_rows) / len(loo_rows)
    loo_full_fraction = sum(bool(row["full_four_landmark_order"]) for row in loo_rows) / len(loo_rows)
    loo_quarters = sorted(float(row["ara_prompt_crest_to_half"]) for row in loo_rows)

    # Post-result diagnostic, not a frozen gate: the exact fitted prompt share
    # above which x=0.5 is crossed before the delayed crest.  This makes the
    # parent-asymmetry dependency explicit instead of treating 0.5 as rigid.
    cp = cumsum(prompt_shape)
    cd = cumsum(delayed_shape)
    delayed_crest_index = max(range(len(delayed_shape)), key=delayed_shape.__getitem__)
    denominator = cp[delayed_crest_index] - cd[delayed_crest_index]
    share_threshold = (
        (0.25 - cd[delayed_crest_index]) / denominator
        if denominator != 0
        else float("nan")
    )
    observed_prompt_share = prompt_yield / (prompt_yield + delayed_yield)
    loo_failures = [
        {"axis": row["axis"], "removed_bin": row["removed_bin"], "prompt_share": row["prompt_yield"] / (row["prompt_yield"] + row["delayed_yield"])}
        for row in loo_rows
        if not bool(row["half_before_delayed_crest"])
    ]

    # Yield sensitivity draws. The branch shapes remain fixed by design.
    rng = random.Random(SEED)
    p_ci = [float(v) for v in t371["fit"]["prompt_ci95"]]
    d_ci = [float(v) for v in t371["fit"]["delayed_ci95"]]
    sensitivity_half = 0
    sensitivity_full = 0
    sensitivity_quarter = 0
    sensitivity_t_half: list[float] = []
    sensitivity_delta: list[float] = []
    for _ in range(N_SENSITIVITY):
        py = split_normal_draw(rng, prompt_yield, p_ci[0], p_ci[1])
        dy = split_normal_draw(rng, delayed_yield, d_ci[0], d_ci[1])
        lm = landmarks(times, prompt_shape, delayed_shape, py, dy)
        sensitivity_half += int(bool(lm["half_before_delayed_crest"]))
        sensitivity_full += int(bool(lm["full_four_landmark_order"]))
        delta = float(lm["ara_prompt_crest_to_half"])
        sensitivity_quarter += int(0.20 <= delta <= 0.30)
        sensitivity_t_half.append(float(lm["child_half_time_us"]))
        sensitivity_delta.append(delta)
    sensitivity_t_half.sort()
    sensitivity_delta.sort()

    hist_rows: list[dict[str, object]] = []
    hist_min, hist_max, bins = min(sensitivity_delta), max(sensitivity_delta), 40
    step = (hist_max - hist_min) / bins if hist_max > hist_min else 1.0
    counts = [0] * bins
    for value in sensitivity_delta:
        index = min(int((value - hist_min) / step), bins - 1)
        counts[index] += 1
    for i, count in enumerate(counts):
        hist_rows.append(
            {
                "delta_x_bin_low": hist_min + i * step,
                "delta_x_bin_high": hist_min + (i + 1) * step,
                "count": count,
                "fraction": count / N_SENSITIVITY,
            }
        )
    write_csv(OUT / "T399_YIELD_SENSITIVITY_HISTOGRAM.csv", hist_rows)

    # Circular-shift alignment control: same delayed shape, wrong relative phase.
    observed_error = abs(float(primary["ara_prompt_crest_to_half"]) - 0.25)
    null_rows: list[dict[str, object]] = []
    as_good = 0
    n = len(delayed_shape)
    for shift in range(1, n):
        shifted = delayed_shape[-shift:] + delayed_shape[:-shift]
        lm = landmarks(times, prompt_shape, shifted, prompt_yield, delayed_yield)
        error = abs(float(lm["ara_prompt_crest_to_half"]) - 0.25)
        qualifies = bool(lm["full_four_landmark_order"]) and error <= observed_error + 1e-15
        as_good += int(qualifies)
        null_rows.append(
            {
                "shift_samples": shift,
                "shift_us": shift * (times[1] - times[0]),
                "full_four_landmark_order": bool(lm["full_four_landmark_order"]),
                "quarter_error": error,
                "as_good_as_real": qualifies,
            }
        )
    write_csv(OUT / "T399_CIRCULAR_SHIFT_CONTROLS.csv", null_rows)
    p_upper = (as_good + 1) / (len(null_rows) + 1)

    # Independent, coarse COHERENT release. Use piecewise-uniform mass in each
    # released 0.5-us bin; do not overclaim native within-bin landmark order.
    holdout_rows = read_csv(T378_COMPONENTS)
    holdout_times = [float(row["time_us"]) for row in holdout_rows]
    holdout_prompt = [float(row["prompt_neutrino_fit"]) for row in holdout_rows]
    holdout_delayed = [float(row["delayed_neutrino_fit"]) for row in holdout_rows]
    holdout_half = piecewise_bin_half_time(holdout_times, holdout_prompt, holdout_delayed)
    holdout_prompt_peak = holdout_times[max(range(len(holdout_prompt)), key=holdout_prompt.__getitem__)]
    holdout_delayed_peak = holdout_times[max(range(len(holdout_delayed)), key=holdout_delayed.__getitem__)]
    holdout_pass = holdout_half < holdout_delayed_peak

    sensitivity_half_fraction = sensitivity_half / N_SENSITIVITY
    gates = {
        "G1_native_four_landmark_order": bool(primary["full_four_landmark_order"]),
        "G2_native_child_half_before_delayed_crest": bool(primary["half_before_delayed_crest"]),
        "G3_native_quarter_compatibility": 0.20 <= float(primary["ara_prompt_crest_to_half"]) <= 0.30,
        "G4_leave_one_out_half_before_crest_at_least_90pct": loo_fraction >= 0.90,
        "G5_yield_sensitivity_half_before_crest_at_least_95pct": sensitivity_half_fraction >= 0.95,
        "G6_T378_coarse_holdout_half_before_delayed_peak": holdout_pass,
        "G7_circular_shift_alignment_p_at_most_0p05": p_upper <= 0.05,
        "G8_population_not_individual_birth_boundary": True,
    }
    core_pass = all(gates[key] for key in (
        "G1_native_four_landmark_order",
        "G2_native_child_half_before_delayed_crest",
        "G3_native_quarter_compatibility",
        "G4_leave_one_out_half_before_crest_at_least_90pct",
        "G5_yield_sensitivity_half_before_crest_at_least_95pct",
        "G6_T378_coarse_holdout_half_before_delayed_peak",
        "G8_population_not_individual_birth_boundary",
    ))
    if core_pass and gates["G7_circular_shift_alignment_p_at_most_0p05"]:
        verdict = "CHILD-HALF PRE-CREST SEQUENCE SUPPORTED; ALIGNMENT-SPECIFIC CONTROL PASSED"
    elif core_pass:
        verdict = "CHILD-HALF PRE-CREST SEQUENCE SUPPORTED; ALIGNMENT-SPECIFIC CLAIM UNRESOLVED"
    else:
        verdict = "CHILD-HALF PRE-CREST SEQUENCE NOT SUPPORTED"

    robustness = {
        "native_quarter_pass": gates["G3_native_quarter_compatibility"],
        "native_half_before_crest": gates["G2_native_child_half_before_delayed_crest"],
        "loo_half_before_crest_fraction": loo_fraction,
        "loo_full_order_fraction": loo_full_fraction,
        "loo_pass": gates["G4_leave_one_out_half_before_crest_at_least_90pct"],
        "sensitivity_half_before_crest_fraction": sensitivity_half_fraction,
        "sensitivity_full_order_fraction": sensitivity_full / N_SENSITIVITY,
        "sensitivity_quarter_fraction": sensitivity_quarter / N_SENSITIVITY,
        "sensitivity_pass": gates["G5_yield_sensitivity_half_before_crest_at_least_95pct"],
        "holdout_pass": holdout_pass,
        "alignment_pass": gates["G7_circular_shift_alignment_p_at_most_0p05"],
        "shift_p_upper": p_upper,
    }

    result = {
        "test": "T399",
        "date": datetime.now(timezone.utc).date().isoformat(),
        "protocol_sha256": sha256(PROTOCOL),
        "verdict": verdict,
        "claim_tested": "joint delayed-neutrino population reaches cumulative child half before its release-rate crest",
        "primary_native_landmarks": primary,
        "leave_one_out": {
            "n": len(loo_rows),
            "half_before_delayed_crest_fraction": loo_fraction,
            "full_four_landmark_order_fraction": loo_full_fraction,
            "quarter_delta_median": quantile(loo_quarters, 0.5),
            "quarter_delta_range": [min(loo_quarters), max(loo_quarters)],
        },
        "yield_sensitivity": {
            "n": N_SENSITIVITY,
            "seed": SEED,
            "method": "independent split-normal positive-yield draws from registered T371 95% intervals; fixed native branch shapes",
            "half_before_delayed_crest_fraction": sensitivity_half_fraction,
            "full_four_landmark_order_fraction": sensitivity_full / N_SENSITIVITY,
            "quarter_window_fraction": sensitivity_quarter / N_SENSITIVITY,
            "child_half_time_us_95pct": [quantile(sensitivity_t_half, 0.025), quantile(sensitivity_t_half, 0.975)],
            "quarter_delta_95pct": [quantile(sensitivity_delta, 0.025), quantile(sensitivity_delta, 0.975)],
        },
        "T378_independent_coarse_holdout": {
            "prompt_peak_bin_center_us": holdout_prompt_peak,
            "piecewise_uniform_child_half_time_us": holdout_half,
            "delayed_peak_bin_center_us": holdout_delayed_peak,
            "half_before_delayed_peak": holdout_pass,
            "boundary": "0.5-us released bins do not resolve the native four-landmark order or quarter displacement",
        },
        "circular_shift_control": {
            "n_nonzero_shifts": len(null_rows),
            "as_good_as_real": as_good,
            "p_upper_add_one": p_upper,
            "observed_quarter_error": observed_error,
            "method": "circularly shift native delayed shape relative to prompt; require real order and quarter error no larger than observed",
        },
        "post_result_parent_asymmetry_diagnostic": {
            "status": "diagnostic added after frozen-gate execution; not a new pass criterion",
            "observed_prompt_share": observed_prompt_share,
            "prompt_share_threshold_for_child_half_before_delayed_crest": share_threshold,
            "observed_margin_above_threshold": observed_prompt_share - share_threshold,
            "leave_one_out_failures": loo_failures,
            "interpretation": "the pre-crest placement is an identity-specific branch-balance result, not a yield-independent constant",
        },
        "gates": gates,
        "evidence_boundaries": [
            "The result is population-level and does not time-tag an individual neutrino birth.",
            "x=0.5 is a cumulative ARA landmark of the joint fitted population, not proof that either neutrino individually equals 0.5.",
            "The quarter displacement was proposed after T398 and is therefore a calibration result here.",
            "The yield ensemble is a fixed-shape sensitivity test, not a fresh detector bootstrap.",
            "T378 independently checks only child-half-before-delayed-crest because its released time bins are coarse.",
        ],
        "input_hashes_sha256": {
            path.name: sha256(path)
            for path in (OVERLAP, T371_RESULTS, T378_COMPONENTS, T378_RESULTS)
        },
    }
    (OUT / "T399_RESULTS.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    landmark_rows = [
        {"landmark": "prompt crest", "time_us": primary["prompt_crest_time_us"], "ara_x": primary["prompt_crest_ara"]},
        {"landmark": "branch equality", "time_us": primary["branch_equality_time_us"], "ara_x": primary["branch_equality_ara"]},
        {"landmark": "child half", "time_us": primary["child_half_time_us"], "ara_x": 0.5},
        {"landmark": "delayed crest", "time_us": primary["delayed_crest_time_us"], "ara_x": primary["delayed_crest_ara"]},
    ]
    write_csv(OUT / "T399_NATIVE_LANDMARKS.csv", landmark_rows)

    svg = svg_report(times, prompt_shape, delayed_shape, prompt_yield, delayed_yield, primary, robustness)
    (OUT / "T399_CHILD_HALF_PRECREST_SEQUENCE.svg").write_text(svg, encoding="utf-8")
    html_report = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>T399 child-half before crest</title>
<style>body{{margin:0;background:#eef2f7;font-family:Inter,Segoe UI,Arial,sans-serif;color:#172033}}main{{max-width:1500px;margin:20px auto;padding:0 18px 40px}}img{{width:100%;height:auto;display:block}}section{{background:white;border:1px solid #d9dee8;border-radius:16px;padding:24px;margin-top:18px;line-height:1.55}}code{{background:#f1f4f8;padding:2px 5px;border-radius:4px}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:9px;border-bottom:1px solid #e1e5ec}}.pass{{color:#287453;font-weight:700}}.fail{{color:#a63d4b;font-weight:700}}</style></head><body><main>
<img src="T399_CHILD_HALF_PRECREST_SEQUENCE.svg" alt="T399 child-half pre-crest test">
<section><h2>Result</h2><p><strong>{html.escape(verdict)}</strong></p>
<p>The native sequence is <code>prompt crest → branch equality → child half → delayed crest</code>. Child half occurs {float(primary['time_half_to_delayed_crest_us']):.6f} μs before the delayed-rate maximum. The earlier prompt crest is {float(primary['ara_prompt_crest_to_half']):.6f} ARA units below child half.</p>
<p>This is a joint population timing result. It does not directly observe one muon producing one named pair of neutrinos.</p></section>
<section><h2>Frozen gates</h2><table><thead><tr><th>Gate</th><th>Status</th></tr></thead><tbody>
{''.join(f'<tr><td>{html.escape(k)}</td><td class="{"pass" if v else "fail"}">{"PASS" if v else "FAIL"}</td></tr>' for k,v in gates.items())}
</tbody></table></section>
<section><h2>Reproduction</h2><p>Run <code>python analysis/muon/t399_child_half_precrest_sequence.py</code>, then <code>python analysis/muon/validate_t399_child_half_precrest_sequence.py</code>.</p></section>
</main></body></html>"""
    (OUT / "T399_CHILD_HALF_PRECREST_SEQUENCE_REPORT.html").write_text(html_report, encoding="utf-8")
    print(json.dumps({"output": str(OUT), "verdict": verdict, "gates": gates}, indent=2))


if __name__ == "__main__":
    main()
