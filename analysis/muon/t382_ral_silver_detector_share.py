#!/usr/bin/env python3
"""T382 conformance execution: 96-detector-share traversal child.

This is the primary C03-C06 implementation required by the frozen T382
protocol.  The earlier forward/backward implementation is retained only as a
bank-proxy diagnostic.  No holdout amplitude, cadence, phase, or gate is fitted
to make the child pass.
"""

from __future__ import annotations

import html
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import t382_ral_silver_traversal_child as base


HERE = Path(__file__).resolve().parent
OUT = HERE / "T382_ral_silver_detector_share"
OUT.mkdir(exist_ok=True)

RESULTS = OUT / "T382_DETECTOR_SHARE_RESULTS.json"
VALIDATION = OUT / "T382_DETECTOR_SHARE_VALIDATION.json"
RUNS = OUT / "T382_DETECTOR_SHARE_RUNS.csv"
SHIFTS = OUT / "T382_DETECTOR_SHARE_SHIFT_CONTROLS.csv"
BINS = OUT / "T382_DETECTOR_SHARE_BIN_SENSITIVITY.csv"
BOOT = OUT / "T382_DETECTOR_BOOTSTRAP.csv"
PATTERN = OUT / "T382_DETECTOR_PATTERN_AT_PARENT_RIDGE.csv"
RELEASE = OUT / "T382_RELEASE_MODULATION.csv"
FIGURE = OUT / "T382_DETECTOR_SHARE_FIGURE.svg"
REPORT = OUT / "T382_DETECTOR_SHARE_REPORT.html"

SEED = 382
N_DETECTOR_BOOT = 800
N_RUN_BOOT = 20000
N_RANDOM_PHASE = 4000


def detector_series(record: dict, factor: int = 1):
    """Return native or deterministically rebinned detector-share residuals."""
    mask = record["analysis_mask"]
    counts = np.asarray(record["counts"][:, mask], dtype=float)
    time = np.asarray(record["time"][mask], dtype=float)
    if factor > 1:
        usable = (counts.shape[1] // factor) * factor
        counts = counts[:, :usable].reshape(96, -1, factor).sum(axis=2)
        time = time[:usable].reshape(-1, factor).mean(axis=1)
    total = counts.sum(axis=0)
    shares = np.divide(counts, total[None, :], out=np.zeros_like(counts), where=total[None, :] > 0)
    baseline = counts.sum(axis=1) / max(float(total.sum()), 1.0)
    y = shares.T - baseline[None, :]
    return time, y, total, baseline, counts


def sufficient_statistics(records: list[dict], gamma: float, relaxation: float, factor: int = 1):
    xtwx = np.zeros((2, 2), dtype=float)
    xtwy = np.zeros((2, 96), dtype=float)
    ywy = 0.0
    for record in records:
        time, y, weight, _, _ = detector_series(record, factor)
        omega = 2.0 * np.pi * gamma * record["field_g"] * time
        env = np.exp(-relaxation * time)
        x = np.column_stack([env * np.cos(omega), env * np.sin(omega)])
        # y has its run-specific time-averaged detector share removed.  Centre
        # the phase basis under the same count weights so the eliminated
        # detector baseline is not silently reintroduced by the predictor.
        x -= np.average(x, axis=0, weights=weight)[None, :]
        xtwx += x.T @ (weight[:, None] * x)
        xtwy += x.T @ (weight[:, None] * y)
        ywy += float(np.sum(weight[:, None] * y * y))
    beta = np.linalg.solve(xtwx + np.eye(2) * 1e-18, xtwy)
    sse = max(ywy - float(np.sum(beta * xtwy)), 0.0)
    return sse, beta


def fit_detector_child(records: list[dict]):
    best = None
    for relaxation in np.arange(0.0, 0.8001, 0.1):
        for gamma in np.arange(0.005, 0.0200001, 0.0002):
            score, beta = sufficient_statistics(records, float(gamma), float(relaxation))
            if best is None or score < best[0]:
                best = (score, float(gamma), float(relaxation), beta)
    _, gamma0, relaxation0, _ = best
    for relaxation in np.arange(max(0.0, relaxation0 - 0.10), relaxation0 + 0.1001, 0.01):
        for gamma in np.arange(max(0.001, gamma0 - 0.00020), gamma0 + 0.0002001, 0.000005):
            score, beta = sufficient_statistics(records, float(gamma), float(relaxation))
            if score < best[0]:
                best = (score, float(gamma), float(relaxation), beta)
    score, gamma, relaxation, beta = best
    axis = np.r_[np.ones(48), -np.ones(48)]
    a_fb = float(axis @ beta[0])
    c_fb = float(axis @ beta[1])
    phi0 = float(math.atan2(-c_fb, a_fb))
    return {
        "score": score,
        "gamma_mhz_per_g": gamma,
        "relaxation_per_us": relaxation,
        "beta": beta,
        "phi0_rad": phi0,
        "fb_amplitude": float(math.hypot(a_fb, c_fb)),
    }


def score_record(record: dict, child: dict, factor: int = 1, reverse: bool = False,
                 shift: int = 0):
    time, y, weight, baseline, counts = detector_series(record, factor)
    omega = 2.0 * np.pi * child["gamma_mhz_per_g"] * record["field_g"] * time
    env = np.exp(-child["relaxation_per_us"] * time)
    sign = -1.0 if reverse else 1.0
    x = np.column_stack([env * np.cos(omega), sign * env * np.sin(omega)])
    x -= np.average(x, axis=0, weights=weight)[None, :]
    beta = np.roll(child["beta"], shift, axis=1) if shift else child["beta"]
    predicted = x @ beta
    sse = float(np.sum(weight[:, None] * (y - predicted) ** 2))
    null_sse = float(np.sum(weight[:, None] * y * y))
    covariance = float(np.sum(weight[:, None] * y * predicted))
    return {
        "time": time,
        "observed": y,
        "predicted": predicted,
        "weight": weight,
        "baseline": baseline,
        "counts": counts,
        "sse": sse,
        "null_sse": null_sse,
        "improvement": 1.0 - sse / null_sse,
        "orientation_covariance": covariance,
    }


def free_gamma(record: dict, relaxation: float):
    best = None
    for gamma in np.arange(0.001, 0.0220001, 0.00005):
        score, _ = sufficient_statistics([record], float(gamma), relaxation)
        if best is None or score < best[0]:
            best = (score, float(gamma))
    return {"gamma_mhz_per_g": best[1], "frequency_mhz": best[1] * record["field_g"], "sse": best[0]}


def release_modulation(record: dict, tau: float, child: dict):
    _, fit_map = base.parent_fit_for_tau([record], tau)
    fit = fit_map[record["run"]]
    mask = record["analysis_mask"]
    time = record["time"][mask]
    observed = record["total"][mask]
    expected = fit["mu"]
    residual = observed / np.maximum(expected, 1.0) - 1.0
    theta = 2.0 * np.pi * child["gamma_mhz_per_g"] * record["field_g"] * time + child["phi0_rad"]
    phase_design = np.column_stack([np.ones(len(time)), np.cos(theta), np.sin(theta)])
    null_design = np.ones((len(time), 1))
    _, phase_sse = base.weighted_lstsq(residual, phase_design, expected)
    _, null_sse = base.weighted_lstsq(residual, null_design, expected)
    return 1.0 - phase_sse / null_sse


def circular_distance(a: float, b: float) -> float:
    return abs(float(np.angle(np.exp(1j * (a - b)))))


def make_figure(results: dict, run_frame: pd.DataFrame, pattern: pd.DataFrame):
    width, height = 1600, 1160
    tau = results["parent"]["tau_us"]
    gamma = results["child"]["gamma_mhz_per_g"]
    phi0 = results["child"]["phi0_rad"]
    t = np.linspace(base.T_MIN, base.T_MAX, 700)
    x_parent = 2.0 * (1.0 - np.exp(-t / tau))

    def polyline(x, y, x0, y0, w, h, xmin, xmax, ymin, ymax):
        px = x0 + w * (np.asarray(x) - xmin) / (xmax - xmin)
        py = y0 + h * (ymax - np.asarray(y)) / (ymax - ymin)
        return " ".join(f"{a:.2f},{b:.2f}" for a, b in zip(px, py))

    curves = []
    colours = ["#3d79bd", "#7d5bc7", "#e29a32"]
    for colour, (run, field) in zip(colours, base.HOLDOUT.items()):
        theta = 2.0 * np.pi * gamma * field * t + phi0
        x_child = 1.0 - np.cos(theta)
        curves.append(f'<polyline points="{polyline(t,x_child,100,205,650,300,base.T_MIN,base.T_MAX,0,2)}" fill="none" stroke="{colour}" stroke-width="2" opacity=".82"/>')
    parent_curve = polyline(t, x_parent, 100, 205, 650, 300, base.T_MIN, base.T_MAX, 0, 2)

    polar = []
    cx, cy, radius = 1190, 350, 155
    for colour, row in zip(colours, results["alignment"]["runs"]):
        angle = row["phase_at_parent_ridge_rad"]
        px, py = cx + radius * math.cos(angle), cy - radius * math.sin(angle)
        polar.append(f'<line x1="{cx}" y1="{cy}" x2="{px:.2f}" y2="{py:.2f}" stroke="{colour}" stroke-width="4"/><circle cx="{px:.2f}" cy="{py:.2f}" r="10" fill="{colour}"/><text x="{px+12:.2f}" y="{py-8:.2f}" class="small">{int(row["field_g"])} G</text>')

    pattern_bits = []
    p = pattern.copy()
    limit = max(float(np.nanmax(np.abs(p["observed_share_residual"]))), float(np.nanmax(np.abs(p["predicted_share_residual"]))), 1e-7)
    for colour, (_, group) in zip(colours, p.groupby("run", sort=False)):
        for row in group.itertuples():
            px = 105 + 640 * (row.observed_share_residual + limit) / (2 * limit)
            py = 1010 - 300 * (row.predicted_share_residual + limit) / (2 * limit)
            pattern_bits.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3" fill="{colour}" opacity=".55"/>')
    diag_x1, diag_y1 = 105, 1010
    diag_x2, diag_y2 = 745, 710
    time_ticks = []
    for value in (0.25, 2.0, 4.0, 6.0, 8.0):
        px = 100 + 650 * (value - base.T_MIN) / (base.T_MAX - base.T_MIN)
        time_ticks.append(f'<line x1="{px:.2f}" y1="505" x2="{px:.2f}" y2="512" stroke="#536170"/><text x="{px:.2f}" y="530" class="small" text-anchor="middle">{value:g}</text>')
    scatter_ticks = f'''<text x="105" y="1032" class="small" text-anchor="middle">{-limit:.2e}</text><text x="425" y="1032" class="small" text-anchor="middle">0</text><text x="745" y="1032" class="small" text-anchor="middle">{limit:.2e}</text>
<text x="96" y="1015" class="small" text-anchor="end">{-limit:.2e}</text><text x="96" y="865" class="small" text-anchor="end">0</text><text x="96" y="715" class="small" text-anchor="end">{limit:.2e}</text>'''

    gates = [
        ("C01 parent", results["gates"]["c01_parent_pass"]),
        ("C02 parent-only baseline", results["gates"]["c02_parent_only_pass"]),
        ("C03-C05 96-detector child", results["gates"]["c03_c05_child_pass"]),
        ("C06 child pole / parent ridge", results["gates"]["c06_alignment_pass"]),
        ("C16 individual prediction", None),
    ]
    gate_rows = []
    for i, (label, value) in enumerate(gates):
        y = 735 + i * 62
        text_value = "PASS" if value is True else "FAIL" if value is False else "UNAVAILABLE"
        colour = "#198754" if value is True else "#b43636" if value is False else "#6c7684"
        gate_rows.append(f'<text x="885" y="{y}" class="body">{html.escape(label)}</text><text x="1420" y="{y}" class="body" text-anchor="end" fill="{colour}">{text_value}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="#f6f8fb"/><style>.title{{font:700 34px Arial;fill:#17202b}}.subtitle{{font:18px Arial;fill:#596575}}.heading{{font:700 22px Arial;fill:#17202b}}.body{{font:18px Arial;fill:#26313d}}.small{{font:14px Arial;fill:#596575}}.panel{{fill:white;stroke:#d4dbe5;stroke-width:2}}.grid{{stroke:#dce2ea;stroke-width:1}}</style>
<text x="60" y="58" class="title">T382 — 96-detector ARA child conformance test</text>
<text x="60" y="88" class="subtitle">Parent population, native child traversal, detector pattern and frozen controls kept as separate cuts</text>
<rect x="55" y="115" width="730" height="470" rx="14" class="panel"/><text x="90" y="150" class="heading">Parent and child coordinates (both native 0–2)</text>
<line x1="100" y1="205" x2="100" y2="505" stroke="#536170"/><line x1="100" y1="505" x2="750" y2="505" stroke="#536170"/>
<line x1="100" y1="355" x2="750" y2="355" class="grid"/><text x="78" y="510" class="small">0</text><text x="78" y="360" class="small">1</text><text x="78" y="210" class="small">2</text>
<polyline points="{parent_curve}" fill="none" stroke="#111827" stroke-width="5"/>{''.join(curves)}{''.join(time_ticks)}
<text x="425" y="558" class="small" text-anchor="middle">time after implantation (μs)</text><text x="105" y="180" class="small">black parent xP; coloured child xC for 63, 160 and 400 G</text>
<rect x="815" y="115" width="730" height="470" rx="14" class="panel"/><text x="850" y="150" class="heading">Child phase at independently fitted parent ridge</text>
<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#8491a1" stroke-width="2"/><line x1="{cx-radius}" y1="{cy}" x2="{cx+radius}" y2="{cy}" class="grid"/><line x1="{cx}" y1="{cy-radius}" x2="{cx}" y2="{cy+radius}" class="grid"/>{''.join(polar)}
<text x="{cx+radius+12}" y="{cy+5}" class="small">0 / 2π</text><text x="{cx-radius-18}" y="{cy+5}" class="small" text-anchor="end">π child pole</text><text x="850" y="548" class="small">Mean direction {results['alignment']['mean_direction_rad']:.3f} rad; exact pole π; three primary holdout runs.</text>
<rect x="55" y="620" width="730" height="485" rx="14" class="panel"/><text x="90" y="658" class="heading">Observed vs frozen-predicted 96-detector pattern at parent ridge</text>
<line x1="{diag_x1}" y1="{diag_y1}" x2="{diag_x2}" y2="{diag_y2}" stroke="#8491a1" stroke-dasharray="7 6"/><line x1="105" y1="1010" x2="745" y2="1010" stroke="#536170"/><line x1="105" y1="710" x2="105" y2="1010" stroke="#536170"/>{''.join(pattern_bits)}{scatter_ticks}
<text x="425" y="1060" class="small" text-anchor="middle">observed detector-share residual (share fraction)</text><text x="60" y="860" class="small" transform="rotate(-90 60 860)" text-anchor="middle">frozen-predicted residual (share fraction)</text><text x="105" y="1090" class="small">Dashed diagonal is exact pattern recovery; colour identifies field.</text>
<rect x="815" y="620" width="730" height="485" rx="14" class="panel"/><text x="850" y="658" class="heading">Frozen cut verdicts</text>{''.join(gate_rows)}
<text x="850" y="1070" class="small">C16 is unavailable: these are aggregate time-by-detector histograms, not linked individual muons.</text>
</svg>'''
    FIGURE.write_text(svg, encoding="utf-8")


def make_report(results: dict, validation: dict, run_frame: pd.DataFrame):
    rows = []
    for row in run_frame.itertuples():
        rows.append(f"<tr><td>{row.run}</td><td>{row.split}</td><td>{row.field_g:.0f}</td><td>{row.detector_child_gain:.6f}</td><td>{row.reverse_gain:.6f}</td><td>{row.free_gamma_mhz_per_g:.6f}</td><td>{row.phase_at_parent_ridge_rad:.4f}</td></tr>")
    gate_rows = []
    for key, value in results["gates"].items():
        if isinstance(value, dict):
            continue
        verdict = "PASS" if value is True else "FAIL" if value is False else "UNAVAILABLE"
        gate_rows.append(f"<tr><td>{html.escape(key)}</td><td>{verdict}</td></tr>")
    report = f'''<!doctype html><html><head><meta charset="utf-8"><title>T382 detector-share report</title><style>body{{font:16px/1.5 Arial;background:#f4f6fa;color:#17202b;margin:0}}main{{max-width:1280px;margin:auto;padding:34px}}.card{{background:white;border:1px solid #d8dee8;border-radius:12px;padding:22px;margin:18px 0}}table{{border-collapse:collapse;width:100%}}th,td{{padding:8px;border-bottom:1px solid #e1e5eb;text-align:left}}code{{background:#edf1f7;padding:2px 5px}}.boundary{{border-left:6px solid #d58a20}}img{{width:100%;height:auto}}</style></head><body><main>
<h1>T382 — ARA-native 96-detector traversal-child test</h1><p><b>{html.escape(results['status'])}</b></p>
<div class="card"><h2>Answer first</h2><p>{html.escape(results['plain_language'])}</p><p>{html.escape(results['claim_boundary'])}</p></div>
<div class="card"><h2>Frozen identities</h2><p><b>Parent:</b> detector-summed muon population, xP=2(1−exp(−t/τ)). <b>Child:</b> the calibration-frozen 96-detector spin relation, xC=1−cos(θ). Both retain their own native 0–2 coordinate. Projection xC/2 is bookkeeping only.</p></div>
<div class="card"><h2>Key numbers</h2><ul><li>Parent τ: {results['parent']['tau_us']:.6f} μs; ridge: {results['parent']['ridge_time_us']:.6f} μs.</li><li>Detector-share cadence coefficient: {results['child']['gamma_mhz_per_g']:.9f} MHz/G; post-freeze reference difference: {100*results['child']['known_gamma_relative_error']:.3f}%.</li><li>Mean primary holdout child gain: {results['child']['mean_holdout_gain']:.6f}; reverse gain: {results['child']['mean_reverse_gain']:.6f}.</li><li>Correct detector map gain: {results['child']['correct_shift_gain']:.6f}; wrong-shift 95th percentile: {results['child']['wrong_shift_95']:.6f}.</li><li>Detector-bootstrap 95% interval for mean gain: [{results['child']['detector_bootstrap_95'][0]:.6f}, {results['child']['detector_bootstrap_95'][1]:.6f}].</li></ul></div>
<div class="card"><h2>Visual audit</h2><img src="T382_DETECTOR_SHARE_FIGURE.svg" alt="ARA parent and child diagnostic figure"></div>
<div class="card"><h2>Gate table</h2><table><tr><th>cut</th><th>verdict</th></tr>{''.join(gate_rows)}</table></div>
<div class="card"><h2>Per-run audit</h2><table><tr><th>run</th><th>split</th><th>G</th><th>child gain</th><th>reverse gain</th><th>free γ MHz/G</th><th>phase@parent ridge rad</th></tr>{''.join(rows)}</table></div>
<div class="card"><h2>Secondary diagnostics</h2><p>Native/2-bin/4-bin sensitivity, detector bootstrap, detector-map shifts, and detector-summed release modulation are machine-readable beside this report. They audit stability; they do not replace a failed primary gate.</p></div>
<div class="card boundary"><h2>Boundary</h2><p>The source is Class P aggregate μSR. It does not record a named muon's repeated pre-decay state linked to its own decay daughters, and it does not detect either neutrino. C16 therefore remains unavailable.</p></div>
<div class="card"><h2>Reproduce</h2><p>Run <code>t382_ral_silver_detector_share.py</code> after the frozen T382 parent execution. Source hashes and all quality checks are recorded in the validation JSON.</p></div>
</main></body></html>'''
    REPORT.write_text(report, encoding="utf-8")


def main():
    split = {**{r: "calibration" for r in base.CALIBRATION},
             **{r: "validation" for r in base.VALIDATION},
             **{r: "holdout" for r in base.HOLDOUT},
             **{r: "diagnostic" for r in base.DIAGNOSTIC}}
    records = {run: base.load_run(run, field, split[run]) for run, field in base.ALL_RUNS.items()}
    calibration = [records[r] for r in base.CALIBRATION]
    validation_records = [records[r] for r in base.VALIDATION]
    holdout = [records[r] for r in base.HOLDOUT]
    data_quality = {run: rec["quality"] for run, rec in records.items()}
    data_quality_pass = all(all(v.values()) for v in data_quality.values())

    parent_result = json.loads(base.RESULTS.read_text(encoding="utf-8"))
    tau = float(parent_result["parent"]["tau_us"])
    ridge_time = float(parent_result["parent"]["ridge_time_us"])
    c01_pass = bool(parent_result["gates"]["c01_parent_pass"])
    c02_pass = c01_pass and all(parent_result["gates"]["c01_components"].values())

    child = fit_detector_child(calibration)
    fits = {run: score_record(rec, child) for run, rec in records.items()}
    reverse = {run: score_record(rec, child, reverse=True) for run, rec in records.items()}
    free = {run: free_gamma(rec, child["relaxation_per_us"])
            for run, rec in records.items() if rec["split"] in {"validation", "holdout", "diagnostic"}}

    shift_rows = []
    for shift_value in range(96):
        gains = [score_record(rec, child, shift=shift_value)["improvement"] for rec in holdout]
        shift_rows.append({"shift": shift_value, "mean_holdout_improvement": float(np.mean(gains)),
                           "minimum_holdout_improvement": float(np.min(gains))})
    shift_frame = pd.DataFrame(shift_rows)
    shift_frame.to_csv(SHIFTS, index=False)
    correct_shift_gain = float(shift_frame.loc[shift_frame["shift"] == 0, "mean_holdout_improvement"].iloc[0])
    wrong_shift_95 = float(np.quantile(shift_frame.loc[shift_frame["shift"] != 0, "mean_holdout_improvement"], 0.95))

    validation_positive = all(fits[r]["improvement"] > 0 for r in base.VALIDATION)
    holdout_positive = all(fits[r]["improvement"] > 0 for r in base.HOLDOUT)
    orientation_positive = all(fits[r]["orientation_covariance"] > 0 for r in base.HOLDOUT)
    mean_gain = float(np.mean([fits[r]["improvement"] for r in base.HOLDOUT]))
    reverse_gain = float(np.mean([reverse[r]["improvement"] for r in base.HOLDOUT]))
    beats_reverse = mean_gain > reverse_gain
    beats_shifts = correct_shift_gain > wrong_shift_95
    recovered_frequencies = [free[r]["frequency_mhz"] for r in base.HOLDOUT]
    frequency_monotone = bool(np.all(np.diff(recovered_frequencies) > 0))

    bin_rows = []
    for factor in (1, 2, 4):
        for run in base.HOLDOUT:
            score = score_record(records[run], child, factor=factor)
            bin_rows.append({"factor": factor, "run": run, "field_g": records[run]["field_g"],
                             "improvement": score["improvement"], "orientation_covariance": score["orientation_covariance"]})
    bin_frame = pd.DataFrame(bin_rows)
    bin_frame.to_csv(BINS, index=False)

    rng = np.random.default_rng(SEED)
    boot_rows = []
    native_holdout = [fits[r] for r in base.HOLDOUT]
    for replicate in range(N_DETECTOR_BOOT):
        indices = rng.integers(0, 96, 96)
        gains = []
        for fit in native_holdout:
            y = fit["observed"][:, indices]
            pred = fit["predicted"][:, indices]
            weight = fit["weight"]
            sse = float(np.sum(weight[:, None] * (y - pred) ** 2))
            null_sse = float(np.sum(weight[:, None] * y * y))
            gains.append(1.0 - sse / null_sse)
        boot_rows.append({"replicate": replicate, "mean_holdout_improvement": float(np.mean(gains))})
    boot_frame = pd.DataFrame(boot_rows)
    boot_frame.to_csv(BOOT, index=False)
    detector_boot_ci = [float(np.quantile(boot_frame.mean_holdout_improvement, 0.025)),
                        float(np.quantile(boot_frame.mean_holdout_improvement, 0.975))]

    release_rows = []
    for run in base.HOLDOUT:
        release_rows.append({"run": run, "field_g": records[run]["field_g"],
                             "release_modulation_gain": release_modulation(records[run], tau, child)})
    release_frame = pd.DataFrame(release_rows)
    release_frame.to_csv(RELEASE, index=False)

    alignment_rows = []
    pattern_rows = []
    for run, field in base.HOLDOUT.items():
        theta = float((2.0 * np.pi * child["gamma_mhz_per_g"] * field * ridge_time + child["phi0_rad"]) % (2.0 * np.pi))
        mirror_theta = float((-2.0 * np.pi * child["gamma_mhz_per_g"] * field * ridge_time + child["phi0_rad"]) % (2.0 * np.pi))
        alignment_rows.append({
            "run": run, "field_g": field, "phase_at_parent_ridge_rad": theta,
            "distance_to_child_pole_rad": circular_distance(theta, math.pi),
            "native_child_at_parent_ridge": 1.0 - math.cos(theta),
            "projected_child_at_parent_ridge": (1.0 - math.cos(theta)) / 2.0,
            "pole_score": -math.cos(theta), "mirror_pole_score": -math.cos(mirror_theta),
        })
        fit = fits[run]
        index = int(np.argmin(np.abs(fit["time"] - ridge_time)))
        for detector in range(96):
            pattern_rows.append({"run": run, "field_g": field, "time_us": fit["time"][index],
                                 "detector": detector + 1, "observed_share_residual": fit["observed"][index, detector],
                                 "predicted_share_residual": fit["predicted"][index, detector],
                                 "baseline_share": fit["baseline"][detector],
                                 "native_bin_counts": int(fit["counts"][detector, index])})
    alignment_frame = pd.DataFrame(alignment_rows)
    pattern_frame = pd.DataFrame(pattern_rows)
    pattern_frame.to_csv(PATTERN, index=False)

    phases = alignment_frame.phase_at_parent_ridge_rad.to_numpy()
    pole_scores = alignment_frame.pole_score.to_numpy()
    mirror_scores = alignment_frame.mirror_pole_score.to_numpy()
    mean_vector = np.mean(np.exp(1j * phases))
    mean_direction = float(np.angle(mean_vector) % (2.0 * np.pi))
    references = {"pole_pi": math.pi, "origin_0": 0.0, "quarter_pi_2": math.pi / 2.0,
                  "quarter_3pi_2": 3.0 * math.pi / 2.0}
    reference_distances = {name: circular_distance(mean_direction, value) for name, value in references.items()}
    all_within_quarter = bool(np.all(alignment_frame.distance_to_child_pole_rad <= math.pi / 4.0))
    mean_closest_pole = reference_distances["pole_pi"] == min(reference_distances.values())
    run_boot = []
    for _ in range(N_RUN_BOOT):
        sample = rng.integers(0, len(pole_scores), len(pole_scores))
        run_boot.append(float(np.mean(pole_scores[sample])))
    run_boot_ci = [float(np.quantile(run_boot, 0.025)), float(np.quantile(run_boot, 0.975))]
    fields = np.asarray(list(base.HOLDOUT.values()), dtype=float)
    random_scores = []
    for random_origin in rng.uniform(0.0, 2.0 * np.pi, N_RANDOM_PHASE):
        phase = (2.0 * np.pi * child["gamma_mhz_per_g"] * fields * ridge_time + random_origin) % (2.0 * np.pi)
        random_scores.append(float(np.mean(-np.cos(phase))))
    random_975 = float(np.quantile(random_scores, 0.975))
    mean_pole_score = float(np.mean(pole_scores))
    beats_random = mean_pole_score > random_975
    beats_mirror = mean_pole_score > float(np.mean(mirror_scores))

    child_pass = bool(data_quality_pass and validation_positive and holdout_positive and orientation_positive
                      and beats_reverse and beats_shifts and frequency_monotone)
    c06_pass = bool(child_pass and all_within_quarter and mean_closest_pole and run_boot_ci[0] > 0
                    and beats_random and beats_mirror)

    run_rows = []
    alignment_lookup = alignment_frame.set_index("run").to_dict("index")
    for run, rec in records.items():
        align = alignment_lookup.get(run, {})
        run_rows.append({"run": run, "split": rec["split"], "field_g": rec["field_g"],
                         "start_time": rec["start_time"], "temperature_k": rec["temperature_k"],
                         "orientation_metadata": rec["orientation"],
                         "analysis_counts": int(rec["total"][rec["analysis_mask"]].sum()),
                         "detector_child_gain": fits[run]["improvement"],
                         "orientation_covariance": fits[run]["orientation_covariance"],
                         "reverse_gain": reverse[run]["improvement"],
                         "free_gamma_mhz_per_g": free.get(run, {}).get("gamma_mhz_per_g", np.nan),
                         "recovered_frequency_mhz": free.get(run, {}).get("frequency_mhz", np.nan),
                         "phase_at_parent_ridge_rad": align.get("phase_at_parent_ridge_rad", np.nan),
                         "native_child_at_parent_ridge": align.get("native_child_at_parent_ridge", np.nan),
                         "projected_child_at_parent_ridge": align.get("projected_child_at_parent_ridge", np.nan),
                         "pole_score": align.get("pole_score", np.nan)})
    run_frame = pd.DataFrame(run_rows).sort_values(["split", "field_g", "run"])
    run_frame.to_csv(RUNS, index=False)

    gates = {
        "data_quality_pass": data_quality_pass,
        "c01_parent_pass": c01_pass,
        "c02_parent_only_pass": c02_pass,
        "c03_c05_child_pass": child_pass,
        "c06_alignment_pass": c06_pass,
        "c16_individual_prediction": None,
        "child_components": {
            "validation_gain_positive_each": validation_positive,
            "holdout_gain_positive_each": holdout_positive,
            "holdout_orientation_covariance_positive_each": orientation_positive,
            "beats_reverse_pooled": beats_reverse,
            "beats_95_percent_detector_map_shifts": beats_shifts,
            "holdout_recovered_frequency_monotone": frequency_monotone,
        },
        "alignment_components": {
            "every_holdout_within_pi_over_4": all_within_quarter,
            "mean_direction_closest_to_pi": mean_closest_pole,
            "run_bootstrap_lower_above_zero": run_boot_ci[0] > 0,
            "beats_random_phase_97_5_percentile": beats_random,
            "beats_mirror": beats_mirror,
        },
    }
    if c01_pass and child_pass and c06_pass:
        status = "DETECTOR_CHILD_HANDOVER_ALIGNMENT_LEAD"
        plain = "The population parent and 96-detector traversal child both passed their frozen controls, and the child pole aligned with the parent ridge. This is a three-run aggregate lead requiring same-medium replication."
    elif c01_pass and child_pass:
        status = "DETECTOR_CHILD_RECOVERED_ALIGNMENT_NOT_SUPPORTED"
        plain = "The population parent and 96-detector traversal child were separately recovered, but the frozen child pole did not align with the parent ridge. The source supports a readable child relation, not child-mediated decay timing."
    elif c01_pass:
        status = "PARENT_RECOVERED_96_DETECTOR_CHILD_NOT_QUALIFIED"
        plain = "The population parent passed, but the calibration-frozen 96-detector relation did not qualify as a stable traversal child under the frozen controls. C06 cannot be interpreted as child-mediated handover evidence."
    else:
        status = "SOURCE_OR_PARENT_GATE_FAILED"
        plain = "The source or parent failed its frozen construct gate, so the traversal-child claim is not evaluated as physical evidence."

    results = {
        "test": "T382 RAL Silver 96-detector-share ARA traversal child",
        "status": status,
        "source": parent_result["source"],
        "implementation": "96-detector time-varying shares; forward/backward bank result retained only as proxy diagnostic",
        "parent": parent_result["parent"],
        "child": {
            "gamma_mhz_per_g": child["gamma_mhz_per_g"],
            "relaxation_per_us": child["relaxation_per_us"],
            "phi0_rad": child["phi0_rad"],
            "forward_backward_coefficient_amplitude": child["fb_amplitude"],
            "known_gamma_mhz_per_g_revealed_after_fit": base.KNOWN_GAMMA_MHZ_PER_G,
            "known_gamma_relative_error": abs(child["gamma_mhz_per_g"] - base.KNOWN_GAMMA_MHZ_PER_G) / base.KNOWN_GAMMA_MHZ_PER_G,
            "native_coordinate": "xC(t)=1-cos(theta(t))",
            "projection": "pC=xC/2",
            "mean_holdout_gain": mean_gain,
            "mean_reverse_gain": reverse_gain,
            "correct_shift_gain": correct_shift_gain,
            "wrong_shift_95": wrong_shift_95,
            "detector_bootstrap_95": detector_boot_ci,
        },
        "alignment": {"runs": alignment_rows, "mean_direction_rad": mean_direction,
                      "mean_resultant_length": float(abs(mean_vector)), "mean_pole_score": mean_pole_score,
                      "run_bootstrap_95": run_boot_ci, "random_phase_97_5": random_975,
                      "mean_mirror_pole_score": float(np.mean(mirror_scores)),
                      "reference_distances_rad": reference_distances},
        "diagnostics": {"bin_sensitivity": bin_frame.groupby("factor").improvement.mean().to_dict(),
                        "release_modulation_mean_gain": float(release_frame.release_modulation_gain.mean()),
                        "bank_proxy_status": parent_result["status"]},
        "gates": gates,
        "plain_language": plain,
        "claim_boundary": "Aggregate daughter histograms reconstruct a population parent and candidate spin child. Neither neutrino is observed, and individual advance prediction is unavailable.",
        "artifacts": {"run_summary": str(RUNS), "shift_controls": str(SHIFTS), "bin_sensitivity": str(BINS),
                      "detector_bootstrap": str(BOOT), "detector_pattern": str(PATTERN),
                      "release_modulation": str(RELEASE), "figure": str(FIGURE), "report": str(REPORT)},
    }
    validation = {
        "protocol": "T382_RAL_SILVER_TRAVERSAL_CHILD_PROTOCOL_2026-08-14.md",
        "conformance_addendum": "T382_IMPLEMENTATION_CONFORMANCE_ADDENDUM_2026-08-14.md",
        "data_quality_by_run": data_quality,
        "all_data_quality_pass": data_quality_pass,
        "source_class": "P_population_histograms",
        "individual_prediction_available": False,
        "controls": {"detector_bootstrap_replicates": N_DETECTOR_BOOT, "run_bootstrap_replicates": N_RUN_BOOT,
                     "random_phase_draws": N_RANDOM_PHASE, "bin_factors": [1, 2, 4], "seed": SEED},
        "implementation_notes": [
            "All 96 detector shares implement the frozen primary child; forward/backward is used only to fix the calibrated phase gauge.",
            "Detector coefficients, cadence and relaxation are calibration-only and are frozen on validation/holdout.",
            "The established muon cadence coefficient is disclosed only after the ARA calibration fit.",
            "Release modulation is diagnostic because detector acceptance can leak phase into detector-summed counts.",
        ],
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    VALIDATION.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    make_figure(results, run_frame, pattern_frame)
    make_report(results, validation, run_frame)
    print(json.dumps({"status": status, "tau_us": tau, "gamma_mhz_per_g": child["gamma_mhz_per_g"],
                      "c01": c01_pass, "c02": c02_pass, "c03_c05": child_pass,
                      "c06": c06_pass, "c16": None, "report": str(REPORT)}, indent=2))


if __name__ == "__main__":
    main()
