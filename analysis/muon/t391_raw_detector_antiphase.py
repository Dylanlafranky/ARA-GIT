#!/usr/bin/env python3
"""T391 frozen raw 96-detector anti-phase test."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

import numpy as np
import pandas as pd

import t382_ral_silver_traversal_child as base
import t382_ral_silver_detector_share as detector


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "T391_RAW_DETECTOR_ANTIPHASE_PROTOCOL_2026-08-15.md"
OUT = HERE / "T391_raw_detector_antiphase"
OUT.mkdir(exist_ok=True)

RESULTS = OUT / "T391_RESULTS.json"
RUNS = OUT / "T391_RUN_SUMMARY.csv"
SHIFTS = OUT / "T391_TEMPORAL_SHIFT_CURVES.csv"
DETECTOR_SHIFTS = OUT / "T391_DETECTOR_SHIFT_CONTROLS.csv"
WRONG_CADENCE = OUT / "T391_WRONG_CADENCE_CONTROLS.csv"
PROFILES = OUT / "T391_RAW_PHASE_PROFILES.csv"
FIGURE = OUT / "T391_RAW_DETECTOR_ANTIPHASE.svg"
REPORT = OUT / "T391_RAW_DETECTOR_ANTIPHASE_REPORT.html"

SEED = 391
N_PHASE = 48
N_BOOT = 20000
SHIFT_GRID = np.round(np.arange(0.30, 0.7001, 0.01), 2)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def phase_profile(record: dict, gamma: float, timing_field: float | None = None) -> dict:
    """Fold raw detector-share residuals by cadence without a spatial decoder."""
    time, y, total, _, _ = detector.detector_series(record)
    field = float(record["field_g"] if timing_field is None else timing_field)
    phase = np.mod(gamma * field * time, 1.0)
    index = np.minimum((phase * N_PHASE).astype(int), N_PHASE - 1)
    profile = np.zeros((N_PHASE, y.shape[1]), dtype=float)
    phase_weight = np.zeros(N_PHASE, dtype=float)
    samples = np.zeros(N_PHASE, dtype=int)
    for j in range(N_PHASE):
        mask = index == j
        samples[j] = int(mask.sum())
        if not mask.any():
            continue
        phase_weight[j] = float(total[mask].sum())
        profile[j] = np.sum(total[mask, None] * y[mask], axis=0) / max(phase_weight[j], 1.0)
    if np.any(phase_weight <= 0):
        raise RuntimeError(f"Empty phase bin in {record['run']} using {field:g} G cadence")
    profile -= np.average(profile, axis=0, weights=phase_weight)[None, :]
    centres = (np.arange(N_PHASE, dtype=float) + 0.5) / N_PHASE
    return {"phase": centres, "profile": profile, "weight": phase_weight, "samples": samples}


def circular_interpolate(values: np.ndarray, centres: np.ndarray, target: np.ndarray) -> np.ndarray:
    xp = np.concatenate([centres - 1.0, centres, centres + 1.0])
    if values.ndim == 1:
        fp = np.tile(values, 3)
        return np.interp(np.mod(target, 1.0), xp, fp)
    fp = np.concatenate([values, values, values], axis=0)
    return np.column_stack([
        np.interp(np.mod(target, 1.0), xp, fp[:, j]) for j in range(values.shape[1])
    ])


def shifted_phase_pairs(folded: dict, fraction: float, half_unique: bool = False):
    phase = folded["phase"]
    profile = folded["profile"]
    weight = folded["weight"]
    if half_unique and abs(fraction - 0.5) < 1e-12:
        source = profile[: N_PHASE // 2]
        target = profile[N_PHASE // 2 :]
        pair_weight = np.sqrt(weight[: N_PHASE // 2] * weight[N_PHASE // 2 :])
        return source, target, pair_weight
    target_phase = np.mod(phase + fraction, 1.0)
    target = circular_interpolate(profile, phase, target_phase)
    target_weight = circular_interpolate(weight, phase, target_phase)
    pair_weight = np.sqrt(weight * target_weight)
    return profile, target, pair_weight


def weighted_error(target: np.ndarray, prediction: np.ndarray, weight: np.ndarray) -> float:
    numerator = float(np.sum(weight[:, None] * (target - prediction) ** 2))
    denominator = float(np.sum(weight[:, None] * target ** 2))
    return float(np.sqrt(numerator / max(denominator, 1e-30)))


def weighted_cosine(source: np.ndarray, target: np.ndarray, weight: np.ndarray) -> float:
    numerator = float(np.sum(weight[:, None] * source * target))
    denominator = float(np.sqrt(
        np.sum(weight[:, None] * source * source) *
        np.sum(weight[:, None] * target * target)
    ))
    return numerator / max(denominator, 1e-30)


def native_diagnostic(record: dict, gamma: float) -> dict:
    time, y, total, _, _ = detector.detector_series(record)
    period = 1.0 / (gamma * float(record["field_g"]))
    target_time = time + 0.5 * period
    valid = target_time <= time[-1]
    source = y[valid]
    target = np.column_stack([
        np.interp(target_time[valid], time, y[:, j]) for j in range(y.shape[1])
    ])
    target_weight = np.interp(target_time[valid], time, total)
    pair_weight = np.sqrt(total[valid] * target_weight)
    return {
        "native_n_pairs": int(valid.sum()),
        "native_half_turn_correlation": weighted_cosine(source, target, pair_weight),
        "native_full_inversion_error": weighted_error(target, -source, pair_weight),
        "native_direct_repeat_error": weighted_error(target, source, pair_weight),
    }


def score_profile(record: dict, folded: dict) -> tuple[dict, list[dict], list[dict], dict]:
    source, target, weight = shifted_phase_pairs(folded, 0.5, half_unique=True)
    predictions = {
        "full_inversion": -source,
        "direct_repeat": source,
        "first_bank_only": np.column_stack([-source[:, :48], source[:, 48:]]),
        "second_bank_only": np.column_stack([source[:, :48], -source[:, 48:]]),
    }
    errors = {name: weighted_error(target, pred, weight) for name, pred in predictions.items()}
    competitor_error = min(value for name, value in errors.items() if name != "full_inversion")
    half_correlation = weighted_cosine(source, target, weight)

    temporal_rows = []
    for fraction in SHIFT_GRID:
        shift_source, shift_target, shift_weight = shifted_phase_pairs(folded, float(fraction))
        temporal_rows.append({
            "run": record["run"],
            "field_g": float(record["field_g"]),
            "turn_fraction": float(fraction),
            "raw_pattern_correlation": weighted_cosine(shift_source, shift_target, shift_weight),
            "full_inversion_error": weighted_error(shift_target, -shift_source, shift_weight),
        })
    temporal = pd.DataFrame(temporal_rows)
    minimum = temporal.loc[temporal.raw_pattern_correlation.idxmin()]

    detector_shift_rows = []
    for shift in range(96):
        prediction = -np.roll(source, shift, axis=1)
        detector_shift_rows.append({
            "run": record["run"],
            "field_g": float(record["field_g"]),
            "detector_label_shift": shift,
            "full_inversion_error": weighted_error(target, prediction, weight),
        })
    wrong = np.asarray([row["full_inversion_error"] for row in detector_shift_rows[1:]], dtype=float)

    # Pair-level sums are retained for the hierarchical bootstrap.
    pair_parts = {"denominator": weight * np.sum(target * target, axis=1)}
    for name, prediction in predictions.items():
        pair_parts[name] = weight * np.sum((target - prediction) ** 2, axis=1)

    summary = {
        "run": record["run"],
        "split": record["split"],
        "field_g": float(record["field_g"]),
        "period_us": 1.0 / (float(record["field_g"]) * GAMMA),
        "phase_bins": N_PHASE,
        "minimum_samples_per_phase_bin": int(folded["samples"].min()),
        **{f"error_{name}": value for name, value in errors.items()},
        "full_inversion_advantage": float(competitor_error - errors["full_inversion"]),
        "half_turn_raw_correlation": float(half_correlation),
        "minimum_correlation_turn_fraction": float(minimum.turn_fraction),
        "minimum_raw_correlation": float(minimum.raw_pattern_correlation),
        "wrong_detector_shift_p05_error": float(np.quantile(wrong, 0.05)),
        "wrong_detector_shift_median_error": float(np.median(wrong)),
        "correct_beats_fraction_detector_shifts": float(np.mean(errors["full_inversion"] < wrong)),
    }
    return summary, temporal_rows, detector_shift_rows, pair_parts


def bootstrap_advantage(pair_parts: dict[str, dict], run_names: list[str]) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    samples = np.empty(N_BOOT, dtype=float)
    mapping_names = ["full_inversion", "direct_repeat", "first_bank_only", "second_bank_only"]
    for b in range(N_BOOT):
        chosen_runs = rng.choice(run_names, size=len(run_names), replace=True)
        numerator = {name: 0.0 for name in mapping_names}
        denominator = 0.0
        for run in chosen_runs:
            parts = pair_parts[str(run)]
            n = len(parts["denominator"])
            index = rng.integers(0, n, size=n)
            denominator += float(parts["denominator"][index].sum())
            for name in mapping_names:
                numerator[name] += float(parts[name][index].sum())
        errors = {name: float(np.sqrt(numerator[name] / max(denominator, 1e-30))) for name in mapping_names}
        samples[b] = min(errors[name] for name in mapping_names if name != "full_inversion") - errors["full_inversion"]
    return samples


def svg_text(value: object) -> str:
    return html.escape(str(value))


def make_figure(run_frame: pd.DataFrame, shift_frame: pd.DataFrame, profiles: dict[str, dict], results: dict):
    holdout = run_frame[run_frame.split == "holdout"].copy()
    colours = {63.0: "#2f6fb3", 160.0: "#d99226", 400.0: "#8755a6"}
    width, height = 1640, 1160
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f6f8fb"/>',
        '<style>.title{font:700 32px Arial;fill:#17202b}.heading{font:700 20px Arial;fill:#17202b}.body{font:16px Arial;fill:#26313d}.small{font:13px Arial;fill:#596575}.mono{font:14px Consolas,monospace;fill:#26313d}.panel{fill:white;stroke:#d4dbe5;stroke-width:2}.axis{stroke:#46515e;stroke-width:1.2}.grid{stroke:#e2e6ec;stroke-width:1}</style>',
        '<text x="55" y="48" class="title">T391 - raw 96-detector anti-phase test</text>',
        '<text x="55" y="77" class="body">300 K silver | calibration cadence 0.013820 MHz/G | untouched holdouts 63, 160, 400 G | 48 phase bins</text>',
    ]
    panels = [(45, 105, 750, 455), (845, 105, 750, 455), (45, 605, 750, 455), (845, 605, 750, 455)]
    for x, y, w, h in panels:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="panel"/>')

    # Panel 1: point-level raw field comparison for 160 G.
    run160 = holdout.loc[holdout.field_g == 160.0, "run"].iloc[0]
    source, target, _ = shifted_phase_pairs(profiles[run160], 0.5, half_unique=True)
    expected = (-source * 1e6).reshape(-1)
    observed = (target * 1e6).reshape(-1)
    lim = float(np.quantile(np.abs(np.concatenate([expected, observed])), 0.995)) * 1.08
    lim = max(lim, 1.0)
    x0, y0, pw, ph = 105, 175, 620, 315
    parts.append('<text x="70" y="142" class="heading">Raw detector field after a half-turn (160 G)</text>')
    for tick in np.linspace(-lim, lim, 5):
        px = x0 + pw * (tick + lim) / (2 * lim)
        py = y0 + ph * (lim - tick) / (2 * lim)
        parts.extend([
            f'<line x1="{px:.1f}" y1="{y0}" x2="{px:.1f}" y2="{y0+ph}" class="grid"/>',
            f'<line x1="{x0}" y1="{py:.1f}" x2="{x0+pw}" y2="{py:.1f}" class="grid"/>',
            f'<text x="{px:.1f}" y="{y0+ph+20}" class="small" text-anchor="middle">{tick:.0f}</text>',
            f'<text x="{x0-9}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:.0f}</text>',
        ])
    parts.append(f'<line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0}" stroke="#333842" stroke-dasharray="6 5"/>')
    stride = max(1, len(expected) // 1800)
    for ex, ob in zip(expected[::stride], observed[::stride]):
        if abs(ex) <= lim and abs(ob) <= lim:
            px = x0 + pw * (ex + lim) / (2 * lim)
            py = y0 + ph * (lim - ob) / (2 * lim)
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="1.8" fill="#2f6fb3" opacity="0.35"/>')
    parts.extend([
        f'<line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>',
        f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>',
        '<text x="415" y="535" class="small" text-anchor="middle">expected anti-phase -y(theta), detector-share residual (ppm)</text>',
        '<text x="62" y="335" class="small" text-anchor="middle" transform="rotate(-90 62 335)">observed y(theta+0.5 turn), residual (ppm)</text>',
    ])

    # Panel 2: mapping errors.
    parts.append('<text x="870" y="142" class="heading">Raw half-turn mapping error (lower is better)</text>')
    mappings = [("error_full_inversion", "both invert"), ("error_direct_repeat", "direct"),
                ("error_first_bank_only", "bank 1 only"), ("error_second_bank_only", "bank 2 only")]
    max_error = float(holdout[[m[0] for m in mappings]].to_numpy().max()) * 1.08
    bx0, by0, bph = 915, 185, 290
    for tick in np.linspace(0, max_error, 4):
        py = by0 + bph * (1 - tick / max_error)
        parts.append(f'<line x1="{bx0}" y1="{py:.1f}" x2="1550" y2="{py:.1f}" class="grid"/><text x="{bx0-10}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:.2f}</text>')
    for j, (column, label) in enumerate(mappings):
        centre = bx0 + 90 + j * 150
        for i, field in enumerate([63.0, 160.0, 400.0]):
            value = float(holdout.loc[holdout.field_g == field, column].iloc[0])
            bh = bph * value / max_error
            x = centre + (i - 1) * 31 - 12
            parts.append(f'<rect x="{x:.1f}" y="{by0+bph-bh:.1f}" width="24" height="{bh:.1f}" fill="{colours[field]}"/>')
        parts.append(f'<text x="{centre}" y="{by0+bph+22}" class="small" text-anchor="middle">{label}</text>')
    parts.extend([
        f'<line x1="{bx0}" y1="{by0+bph}" x2="1550" y2="{by0+bph}" class="axis"/>',
        '<text x="860" y="330" class="small" text-anchor="middle" transform="rotate(-90 860 330)">weighted normalized RMS error</text>',
    ])
    for i, field in enumerate([63.0, 160.0, 400.0]):
        legend_x = 1055 + i * 135
        parts.append(f'<rect x="{legend_x}" y="510" width="18" height="10" fill="{colours[field]}"/><text x="{legend_x+25}" y="520" class="small">{field:g} G</text>')

    # Panel 3: temporal shift curves.
    parts.append('<text x="70" y="642" class="heading">Raw pattern correlation versus spin shift</text>')
    sx0, sy0, sw, sh = 105, 690, 620, 300
    ymin = min(-1.0, float(shift_frame.raw_pattern_correlation.min()) * 1.05)
    ymax = max(0.25, float(shift_frame.raw_pattern_correlation.max()) * 1.05)
    for tick in [0.3, 0.4, 0.5, 0.6, 0.7]:
        px = sx0 + sw * (tick - 0.3) / 0.4
        parts.extend([f'<line x1="{px:.1f}" y1="{sy0}" x2="{px:.1f}" y2="{sy0+sh}" class="grid"/>',
                      f'<text x="{px:.1f}" y="{sy0+sh+20}" class="small" text-anchor="middle">{tick:.1f}</text>'])
    for tick in np.linspace(ymin, ymax, 5):
        py = sy0 + sh * (ymax - tick) / (ymax - ymin)
        parts.append(f'<line x1="{sx0}" y1="{py:.1f}" x2="{sx0+sw}" y2="{py:.1f}" class="grid"/><text x="{sx0-9}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:.2f}</text>')
    halfx = sx0 + sw * 0.5
    parts.append(f'<line x1="{halfx:.1f}" y1="{sy0}" x2="{halfx:.1f}" y2="{sy0+sh}" stroke="#333842" stroke-dasharray="6 5"/>')
    for field in [63.0, 160.0, 400.0]:
        subset = shift_frame[(shift_frame.field_g == field) & (shift_frame.run.isin(holdout.run))]
        points = " ".join(f"{sx0+sw*(q-0.3)/0.4:.1f},{sy0+sh*(ymax-r)/(ymax-ymin):.1f}" for q, r in zip(subset.turn_fraction, subset.raw_pattern_correlation))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{colours[field]}" stroke-width="3"/>')
    parts.extend([
        f'<line x1="{sx0}" y1="{sy0+sh}" x2="{sx0+sw}" y2="{sy0+sh}" class="axis"/>',
        f'<line x1="{sx0}" y1="{sy0}" x2="{sx0}" y2="{sy0+sh}" class="axis"/>',
        '<text x="415" y="1035" class="small" text-anchor="middle">temporal shift (fraction of frozen spin turn)</text>',
        '<text x="62" y="840" class="small" text-anchor="middle" transform="rotate(-90 62 840)">raw 96-detector cosine correlation</text>',
    ])

    # Panel 4: exact controls and gates.
    parts.append('<text x="870" y="642" class="heading">Frozen holdout controls and gates</text>')
    parts.append('<text x="875" y="681" class="mono">Field  anti err  shift p05  best wrong cadence  half corr  min shift</text>')
    for i, row in enumerate(holdout.sort_values("field_g").itertuples()):
        y = 715 + i * 34
        parts.append(f'<text x="875" y="{y}" class="mono">{row.field_g:5.0f}  {row.error_full_inversion:8.4f}  {row.wrong_detector_shift_p05_error:9.4f}  {row.best_wrong_cadence_error:18.4f}  {row.half_turn_raw_correlation:9.4f}  {row.minimum_correlation_turn_fraction:9.2f}</text>')
    gates = [
        ("Inversion beats three mappings in every field", results["gates"]["inversion_beats_mappings_every_field"]),
        ("Half-turn correlation negative in every field", results["gates"]["negative_half_correlation_every_field"]),
        ("Minimum at 0.50 +/- 0.05 in every field", results["gates"]["minimum_near_half_every_field"]),
        ("Correct labels beat >=95% shifts every field", results["gates"]["detector_labels_pass_every_field"]),
        ("Correct cadence beats both wrong cadences", results["gates"]["cadence_control_pass_every_field"]),
        ("Bootstrap lower advantage above zero", results["gates"]["bootstrap_lower_above_zero"]),
    ]
    for i, (label, passed) in enumerate(gates):
        y = 845 + i * 32
        colour = "#1f7a55" if passed else "#a33b3b"
        parts.append(f'<text x="875" y="{y}" class="body">{svg_text(label)}</text><text x="1550" y="{y}" text-anchor="end" font-family="Arial" font-size="16" font-weight="700" fill="{colour}">{"PASS" if passed else "FAIL"}</text>')
    ci = results["bootstrap_95_advantage"]
    parts.append(f'<text x="875" y="1045" class="body" font-weight="700">Verdict: {results["status"]} | advantage {results["pooled_advantage"]:.4f} | 95% [{ci[0]:.4f}, {ci[1]:.4f}]</text>')
    parts.append('<text x="820" y="1130" class="small" text-anchor="middle">Raw detector-share field; no learned spatial decoder. Source: ISIS EMU RAL Silver, DOI 10.5286/ISIS.E.RB1620201.</text>')
    parts.append('</svg>')
    FIGURE.write_text("".join(parts), encoding="utf-8")


def make_report(results: dict, holdout: pd.DataFrame):
    rows = []
    for row in holdout.sort_values("field_g").itertuples():
        rows.append(
            f"<tr><td>{row.run}</td><td>{row.field_g:.0f}</td><td>{row.period_us:.6f}</td>"
            f"<td>{row.error_full_inversion:.6f}</td><td>{row.error_direct_repeat:.6f}</td>"
            f"<td>{row.error_first_bank_only:.6f}</td><td>{row.error_second_bank_only:.6f}</td>"
            f"<td>{row.half_turn_raw_correlation:.6f}</td><td>{row.minimum_correlation_turn_fraction:.2f}</td>"
            f"<td>{row.correct_beats_fraction_detector_shifts:.3f}</td><td>{row.best_wrong_cadence_error:.6f}</td></tr>"
        )
    gates = "".join(
        f"<li><b>{'PASS' if value else 'FAIL'}</b> — {html.escape(name.replace('_', ' '))}</li>"
        for name, value in results["gates"].items() if name != "primary_pass"
    )
    REPORT.write_text(f"""<!doctype html>
<html><head><meta charset="utf-8"><title>T391 raw detector anti-phase</title>
<style>body{{font:16px Arial,sans-serif;color:#17202b;background:#f6f8fb;max-width:1500px;margin:0 auto;padding:28px}}h1,h2{{margin-bottom:8px}}.card{{background:white;border:1px solid #d4dbe5;border-radius:12px;padding:20px;margin:18px 0}}img{{width:100%;height:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:8px;border-bottom:1px solid #dfe4eb;text-align:right}}th:first-child,td:first-child{{text-align:left}}code{{background:#eef1f5;padding:2px 5px}}</style></head>
<body><h1>T391 — raw 96-detector anti-phase</h1>
<p><b>{results['status']}.</b> All six frozen gates were required.</p>
<div class="card"><img src="{FIGURE.name}" alt="T391 four-panel labelled test report"></div>
<div class="card"><h2>Exact holdout results</h2><table><thead><tr><th>run</th><th>G</th><th>period us</th><th>anti err</th><th>direct err</th><th>bank 1 err</th><th>bank 2 err</th><th>half corr</th><th>min shift</th><th>detector shifts beaten</th><th>best wrong cadence</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<div class="card"><h2>Frozen gates</h2><ul>{gates}</ul><p>Pooled full-inversion advantage: <code>{results['pooled_advantage']:.6f}</code>; hierarchical-bootstrap 95% interval <code>[{results['bootstrap_95_advantage'][0]:.6f}, {results['bootstrap_95_advantage'][1]:.6f}]</code>.</p></div>
<div class="card"><h2>Interpretation boundary</h2><p>{html.escape(results['claim_boundary'])}</p></div>
</body></html>""", encoding="utf-8")


def main():
    split = {**{r: "calibration" for r in base.CALIBRATION},
             **{r: "validation" for r in base.VALIDATION},
             **{r: "holdout" for r in base.HOLDOUT}}
    selected = {**base.CALIBRATION, **base.VALIDATION, **base.HOLDOUT}
    records = {run: base.load_run(run, field, split[run]) for run, field in selected.items()}
    calibration = [records[run] for run in base.CALIBRATION]
    child = detector.fit_detector_child(calibration)
    global GAMMA
    GAMMA = float(child["gamma_mhz_per_g"])

    profiles = {run: phase_profile(record, GAMMA) for run, record in records.items() if split[run] != "calibration"}
    run_rows, temporal_rows, detector_rows = [], [], []
    pair_parts = {}
    for run in [*base.VALIDATION, *base.HOLDOUT]:
        summary, temporal, detector_shifts, parts = score_profile(records[run], profiles[run])
        summary.update(native_diagnostic(records[run], GAMMA))
        run_rows.append(summary)
        temporal_rows.extend(temporal)
        detector_rows.extend(detector_shifts)
        pair_parts[run] = parts

    wrong_rows = []
    holdout_fields = list(base.HOLDOUT.values())
    for run, actual_field in base.HOLDOUT.items():
        for timing_field in holdout_fields:
            if timing_field == actual_field:
                continue
            folded = phase_profile(records[run], GAMMA, timing_field=timing_field)
            source, target, weight = shifted_phase_pairs(folded, 0.5, half_unique=True)
            wrong_rows.append({"run": run, "actual_field_g": actual_field, "timing_field_g": timing_field,
                               "full_inversion_error": weighted_error(target, -source, weight),
                               "half_turn_raw_correlation": weighted_cosine(source, target, weight)})

    run_frame = pd.DataFrame(run_rows)
    shift_frame = pd.DataFrame(temporal_rows)
    detector_frame = pd.DataFrame(detector_rows)
    wrong_frame = pd.DataFrame(wrong_rows)
    for run in base.HOLDOUT:
        best_wrong = float(wrong_frame.loc[wrong_frame.run == run, "full_inversion_error"].min())
        run_frame.loc[run_frame.run == run, "best_wrong_cadence_error"] = best_wrong

    profile_rows = []
    for run, folded in profiles.items():
        for i, phase in enumerate(folded["phase"]):
            for detector_index, value in enumerate(folded["profile"][i], start=1):
                profile_rows.append({"run": run, "split": split[run], "field_g": selected[run],
                                     "phase_turns": float(phase), "detector": detector_index,
                                     "share_residual": float(value), "phase_bin_weight": float(folded["weight"][i])})

    run_frame.to_csv(RUNS, index=False)
    shift_frame.to_csv(SHIFTS, index=False)
    detector_frame.to_csv(DETECTOR_SHIFTS, index=False)
    wrong_frame.to_csv(WRONG_CADENCE, index=False)
    pd.DataFrame(profile_rows).to_csv(PROFILES, index=False)

    holdout = run_frame[run_frame.split == "holdout"].copy()
    g1 = bool((holdout.full_inversion_advantage > 0).all())
    g2 = bool((holdout.half_turn_raw_correlation < 0).all())
    g3 = bool((np.abs(holdout.minimum_correlation_turn_fraction - 0.5) <= 0.05 + 1e-12).all())
    g4 = bool((holdout.correct_beats_fraction_detector_shifts >= 0.95).all())
    g5 = bool((holdout.error_full_inversion < holdout.best_wrong_cadence_error).all())

    boot = bootstrap_advantage(pair_parts, list(base.HOLDOUT))
    ci = [float(np.quantile(boot, 0.025)), float(np.quantile(boot, 0.975))]
    g6 = bool(ci[0] > 0)
    gates = {
        "inversion_beats_mappings_every_field": g1,
        "negative_half_correlation_every_field": g2,
        "minimum_near_half_every_field": g3,
        "detector_labels_pass_every_field": g4,
        "cadence_control_pass_every_field": g5,
        "bootstrap_lower_above_zero": g6,
    }
    status = "SUPPORTED" if all(gates.values()) else "NOT_SUPPORTED"
    gates["primary_pass"] = status == "SUPPORTED"

    results = {
        "test": "T391 raw 96-detector anti-phase",
        "status": status,
        "source": {"doi": "10.5286/ISIS.E.RB1620201", "medium": "300 K silver",
                   "instrument": "ISIS EMU", "capability": "aggregate 96-detector histograms"},
        "frozen_calibration": {"gamma_mhz_per_g": GAMMA, "calibration_runs": list(base.CALIBRATION),
                               "spatial_decoder_used_in_primary_score": False, "phase_bins": N_PHASE},
        "pooled_advantage": float(holdout.full_inversion_advantage.mean()),
        "bootstrap_95_advantage": ci,
        "gates": gates,
        "holdout_runs": holdout.to_dict("records"),
        "claim_boundary": "The primary score uses raw population detector-share patterns after cadence-only phase folding. It does not observe individual muons, decay vertices, neutrinos, or a spin-controlled decay trigger.",
        "protocol_sha256": sha256(PROTOCOL),
        "source_hashes": {run: records[run]["sha256"] for run in selected},
        "artifacts": {"run_summary": str(RUNS), "temporal_shift_curves": str(SHIFTS),
                      "detector_shift_controls": str(DETECTOR_SHIFTS), "wrong_cadence_controls": str(WRONG_CADENCE),
                      "raw_phase_profiles": str(PROFILES), "figure": str(FIGURE), "report": str(REPORT)},
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(run_frame, shift_frame, profiles, results)
    make_report(results, holdout)
    print(json.dumps({"status": status, "gamma": GAMMA, "pooled_advantage": results["pooled_advantage"],
                      "bootstrap_95": ci, "gates": gates,
                      "holdout": holdout[["field_g", "error_full_inversion", "error_direct_repeat",
                                           "half_turn_raw_correlation", "minimum_correlation_turn_fraction",
                                           "correct_beats_fraction_detector_shifts", "best_wrong_cadence_error"]].to_dict("records")}, indent=2))


if __name__ == "__main__":
    main()
