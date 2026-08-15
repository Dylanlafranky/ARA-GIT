#!/usr/bin/env python3
"""T389 frozen two-axis spin anti-phase Di-ARA test."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

import t382_ral_silver_traversal_child as base
import t382_ral_silver_detector_share as detector


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "T389_SPIN_ANTIPHASE_DIARA_PROTOCOL_2026-08-15.md"
OUT = HERE / "T389_spin_antiphase_diara"
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "T389_RESULTS.json"
RUNS = OUT / "T389_RUN_SUMMARY.csv"
SHIFTS = OUT / "T389_SHIFT_CURVES.csv"
FIGURE = OUT / "T389_SPIN_ANTIPHASE_DIARA.svg"
REPORT = OUT / "T389_SPIN_ANTIPHASE_DIARA_REPORT.md"

SEED = 389
N_BOOT = 20000
SHIFT_GRID = np.round(np.arange(0.30, 0.7001, 0.01), 2)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def project_record(record: dict, child: dict) -> dict:
    time, y, total, _, _ = detector.detector_series(record)
    basis = np.asarray(child["beta"], dtype=float)
    decoder = basis.T @ np.linalg.pinv(basis @ basis.T)
    coeff = y @ decoder
    coeff -= np.average(coeff, axis=0, weights=total)[None, :]
    return {"time": time, "coeff": coeff, "weight": total}


def shifted_pairs(projected: dict, period: float, fraction: float):
    time = projected["time"]
    coeff = projected["coeff"]
    weight = projected["weight"]
    target_time = time + period * fraction
    valid = target_time <= time[-1]
    source = coeff[valid]
    target = np.column_stack([
        np.interp(target_time[valid], time, coeff[:, 0]),
        np.interp(target_time[valid], time, coeff[:, 1]),
    ])
    target_weight = np.interp(target_time[valid], time, weight)
    pair_weight = np.sqrt(weight[valid] * target_weight)
    return source, target, pair_weight


def weighted_vector_error(target: np.ndarray, prediction: np.ndarray, weight: np.ndarray) -> float:
    numerator = np.sum(weight * np.sum((target - prediction) ** 2, axis=1))
    denominator = np.sum(weight * np.sum(target ** 2, axis=1))
    return float(np.sqrt(numerator / max(denominator, 1e-30)))


def complex_correlation(source: np.ndarray, target: np.ndarray, weight: np.ndarray) -> complex:
    z0 = source[:, 0] + 1j * source[:, 1]
    z1 = target[:, 0] + 1j * target[:, 1]
    numerator = np.sum(weight * z1 * np.conj(z0))
    denominator = np.sqrt(np.sum(weight * np.abs(z0) ** 2) * np.sum(weight * np.abs(z1) ** 2))
    return complex(numerator / max(float(denominator), 1e-30))


def score_run(record: dict, projected: dict, child: dict) -> tuple[dict, list[dict]]:
    field = float(record["field_g"])
    period = 1.0 / (child["gamma_mhz_per_g"] * field)
    source, target, weight = shifted_pairs(projected, period, 0.5)
    predictions = {
        "full_inversion": -source,
        "direct_repeat": source,
        "cosine_axis_reflection": np.column_stack([-source[:, 0], source[:, 1]]),
        "sine_axis_reflection": np.column_stack([source[:, 0], -source[:, 1]]),
    }
    errors = {name: weighted_vector_error(target, pred, weight) for name, pred in predictions.items()}
    correlation = complex_correlation(source, target, weight)
    competitors = [v for k, v in errors.items() if k != "full_inversion"]
    advantage = min(competitors) - errors["full_inversion"]

    shift_rows = []
    for fraction in SHIFT_GRID:
        shift_source, shift_target, shift_weight = shifted_pairs(projected, period, float(fraction))
        corr = complex_correlation(shift_source, shift_target, shift_weight)
        shift_rows.append({
            "run": record["run"], "field_g": field, "turn_fraction": float(fraction),
            "correlation_real": float(corr.real), "correlation_imag": float(corr.imag),
            "anti_similarity": float(-corr.real),
        })
    shift_frame = pd.DataFrame(shift_rows)
    minimum = shift_frame.loc[shift_frame.correlation_real.idxmin()]
    summary = {
        "run": record["run"], "split": record["split"], "field_g": field,
        "period_us": period, "n_half_pairs": int(len(source)),
        **{f"error_{k}": v for k, v in errors.items()},
        "full_inversion_advantage": float(advantage),
        "half_turn_correlation_real": float(correlation.real),
        "half_turn_correlation_imag": float(correlation.imag),
        "minimum_correlation_turn_fraction": float(minimum.turn_fraction),
        "minimum_correlation_real": float(minimum.correlation_real),
    }
    return summary, shift_rows


def make_figure(run_frame: pd.DataFrame, shift_frame: pd.DataFrame, projected: dict[str, dict], results: dict):
    colours = {63.0: "#2f6fb3", 160.0: "#d99226", 400.0: "#8755a6"}
    width, height = 1600, 1120
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="#f6f8fb"/>',
             '<style>.title{font:700 32px Arial;fill:#17202b}.heading{font:700 20px Arial;fill:#17202b}.body{font:16px Arial;fill:#26313d}.small{font:13px Arial;fill:#596575}.panel{fill:white;stroke:#d4dbe5;stroke-width:2}.axis{stroke:#46515e;stroke-width:1.2}.grid{stroke:#e2e6ec;stroke-width:1}</style>',
             '<text x="55" y="50" class="title">T389 — population spin anti-phase Di-ARA</text>',
             '<text x="55" y="78" class="body">300 K silver · calibration 20/25 G · untouched holdouts 63/160/400 G · native 0.016 μs bins</text>']
    panels = [(50, 105, 720, 440), (830, 105, 720, 440), (50, 595, 720, 440), (830, 595, 720, 440)]
    for x, y, w, h in panels:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="panel"/>')

    # Panel 1: ARA-normalized quadrature paths.
    x0, y0, pw, ph = 110, 165, 390, 330
    parts.append('<text x="75" y="140" class="heading">Two measured spin quadratures in geometric Di-ARA</text>')
    for tick in [0, 0.5, 1, 1.5, 2]:
        px = x0 + pw * tick / 2; py = y0 + ph * (2 - tick) / 2
        parts.extend([f'<line x1="{px:.1f}" y1="{y0}" x2="{px:.1f}" y2="{y0+ph}" class="grid"/>',
                      f'<line x1="{x0}" y1="{py:.1f}" x2="{x0+pw}" y2="{py:.1f}" class="grid"/>',
                      f'<text x="{px:.1f}" y="{y0+ph+21}" class="small" text-anchor="middle">{tick:g}</text>',
                      f'<text x="{x0-10}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:g}</text>'])
    for run, field in base.HOLDOUT.items():
        coeff = projected[run]["coeff"]
        radius = np.sqrt(np.sum(coeff * coeff, axis=1)); scale = max(float(np.quantile(radius, 0.95)), 1e-12)
        x_c = np.clip(1.0 - coeff[:, 0] / scale, 0.0, 2.0)
        x_s = np.clip(1.0 - coeff[:, 1] / scale, 0.0, 2.0)
        stride = max(1, len(x_c) // 420)
        points = " ".join(f"{x0+pw*x/2:.1f},{y0+ph*(2-y)/2:.1f}" for x, y in zip(x_c[::stride], x_s[::stride]))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{colours[field]}" stroke-width="1.2" opacity="0.75"/>')
    parts.extend([f'<line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>',
                  f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>',
                  '<text x="305" y="530" class="small" text-anchor="middle">cosine ARA cut x_c (0–2 display normalization)</text>',
                  '<text x="68" y="330" class="small" text-anchor="middle" transform="rotate(-90 68 330)">sine ARA cut x_s (0–2 display normalization)</text>'])
    for i, field in enumerate(base.HOLDOUT.values()):
        parts.append(f'<line x1="540" y1="{215+i*35}" x2="580" y2="{215+i*35}" stroke="{colours[field]}" stroke-width="4"/><text x="590" y="{220+i*35}" class="body">{field:g} G</text>')

    # Panel 2: mapping errors.
    parts.append('<text x="855" y="140" class="heading">Half-turn mapping error (lower is better)</text>')
    names = ["full_inversion", "direct_repeat", "cosine_axis_reflection", "sine_axis_reflection"]
    labels = ["both invert", "direct", "cosine flip", "sine flip"]
    max_error = float(run_frame[[f"error_{n}" for n in names]].to_numpy().max()) * 1.08
    bx0, by0, bph = 895, 180, 300
    parts.append(f'<line x1="{bx0}" y1="{by0+bph}" x2="1510" y2="{by0+bph}" class="axis"/>')
    for tick in [0.0, max_error/2.0, max_error]:
        py = by0+bph-bph*tick/max_error
        parts.append(f'<line x1="{bx0-5}" y1="{py:.1f}" x2="1510" y2="{py:.1f}" class="grid"/><text x="{bx0-10}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:.2f}</text>')
    for j, name in enumerate(names):
        centre = bx0 + 90 + j * 145
        for i, field in enumerate(base.HOLDOUT.values()):
            value = float(run_frame.loc[run_frame.field_g == field, f"error_{name}"].iloc[0])
            bh = bph * value / max_error; x = centre + (i-1)*30 - 12
            parts.append(f'<rect x="{x:.1f}" y="{by0+bph-bh:.1f}" width="24" height="{bh:.1f}" fill="{colours[field]}"/>')
        parts.append(f'<text x="{centre}" y="{by0+bph+22}" class="small" text-anchor="middle">{labels[j]}</text>')
    parts.append(f'<text x="850" y="{by0+bph/2}" class="small" text-anchor="middle" transform="rotate(-90 850 {by0+bph/2})">normalized vector error</text>')

    # Panel 3: shift correlation.
    parts.append('<text x="75" y="630" class="heading">Two-axis correlation versus temporal shift</text>')
    sx0, sy0, sw, sh = 110, 675, 610, 300
    ymin = min(-1.0, float(shift_frame.correlation_real.min()) * 1.05); ymax = max(1.0, float(shift_frame.correlation_real.max()) * 1.05)
    for tick in [0.3, 0.4, 0.5, 0.6, 0.7]:
        px = sx0 + sw * (tick - 0.3) / 0.4
        parts.extend([f'<line x1="{px:.1f}" y1="{sy0}" x2="{px:.1f}" y2="{sy0+sh}" class="grid"/>',
                      f'<text x="{px:.1f}" y="{sy0+sh+21}" class="small" text-anchor="middle">{tick:.1f}</text>'])
    zero_y = sy0 + sh * (ymax / (ymax-ymin)); parts.append(f'<line x1="{sx0}" y1="{zero_y:.1f}" x2="{sx0+sw}" y2="{zero_y:.1f}" class="grid"/>')
    for tick in [ymin, 0.0, ymax]:
        py = sy0+sh*(ymax-tick)/(ymax-ymin)
        parts.append(f'<line x1="{sx0-5}" y1="{py:.1f}" x2="{sx0}" y2="{py:.1f}" class="axis"/><text x="{sx0-10}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:.2f}</text>')
    half_x = sx0 + sw*0.5; parts.append(f'<line x1="{half_x:.1f}" y1="{sy0}" x2="{half_x:.1f}" y2="{sy0+sh}" stroke="#333842" stroke-dasharray="7 6"/>')
    for field in base.HOLDOUT.values():
        subset = shift_frame[shift_frame.field_g == field]
        points = " ".join(f"{sx0+sw*(q-0.3)/0.4:.1f},{sy0+sh*(ymax-r)/(ymax-ymin):.1f}" for q, r in zip(subset.turn_fraction, subset.correlation_real))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{colours[field]}" stroke-width="3"/>')
    parts.extend([f'<line x1="{sx0}" y1="{sy0+sh}" x2="{sx0+sw}" y2="{sy0+sh}" class="axis"/>',
                  f'<line x1="{sx0}" y1="{sy0}" x2="{sx0}" y2="{sy0+sh}" class="axis"/>',
                  '<text x="415" y="1015" class="small" text-anchor="middle">shift (fraction of frozen spin turn)</text>',
                  '<text x="68" y="825" class="small" text-anchor="middle" transform="rotate(-90 68 825)">real correlation (−1 anti, +1 repeat)</text>'])

    # Panel 4: frozen gates.
    parts.append('<text x="855" y="630" class="heading">Frozen gates</text>')
    gates = [("Inversion beats 3 controls in every field", results["gates"]["inversion_beats_controls_every_field"]),
             ("Half-turn correlation is negative in every field", results["gates"]["negative_half_correlation_every_field"]),
             ("Minimum is at 0.50 ± 0.05 in every field", results["gates"]["minimum_near_half_every_field"]),
             ("Field-bootstrap lower advantage is above zero", results["gates"]["bootstrap_advantage_lower_above_zero"])]
    for i, (label, passed) in enumerate(gates):
        y = 690 + i*62; colour = "#1f7a55" if passed else "#a33b3b"
        parts.append(f'<text x="865" y="{y}" class="body">{label}</text><text x="1515" y="{y}" class="body" text-anchor="end" fill="{colour}" font-weight="700">{"PASS" if passed else "FAIL"}</text>')
    ci = results["bootstrap_95_full_inversion_advantage"]
    parts.extend([f'<rect x="860" y="940" width="650" height="70" rx="8" fill="#f0f3f7" stroke="#c8ced8"/>',
                  f'<text x="880" y="968" class="body">Pooled inversion advantage {results["pooled_full_inversion_advantage"]:.4f}; 95% [{ci[0]:.4f}, {ci[1]:.4f}]</text>',
                  f'<text x="880" y="995" class="body" font-weight="700">Verdict: {results["status"]}</text>',
                  '<text x="800" y="1090" class="small" text-anchor="middle">ARA panel normalization is display-only; gates use raw projected detector coefficients. Source: ISIS EMU RAL Silver.</text>',
                  '</svg>'])
    FIGURE.write_text("".join(parts), encoding="utf-8")


def main():
    split = {**{r: "calibration" for r in base.CALIBRATION},
             **{r: "validation" for r in base.VALIDATION},
             **{r: "holdout" for r in base.HOLDOUT}}
    selected = {**base.CALIBRATION, **base.VALIDATION, **base.HOLDOUT}
    records = {run: base.load_run(run, field, split[run]) for run, field in selected.items()}
    calibration = [records[run] for run in base.CALIBRATION]
    child = detector.fit_detector_child(calibration)
    projected = {run: project_record(record, child) for run, record in records.items()}

    run_rows, shift_rows = [], []
    for run in [*base.VALIDATION, *base.HOLDOUT]:
        summary, curve = score_run(records[run], projected[run], child)
        run_rows.append(summary); shift_rows.extend(curve)
    run_frame = pd.DataFrame(run_rows)
    shift_frame = pd.DataFrame(shift_rows)
    run_frame.to_csv(RUNS, index=False); shift_frame.to_csv(SHIFTS, index=False)

    holdout = run_frame[run_frame.split == "holdout"].copy()
    g1 = bool((holdout.full_inversion_advantage > 0).all())
    g2 = bool((holdout.half_turn_correlation_real < 0).all())
    g3 = bool((np.abs(holdout.minimum_correlation_turn_fraction - 0.5) <= 0.05 + 1e-12).all())
    rng = np.random.default_rng(SEED)
    advantages = holdout.full_inversion_advantage.to_numpy(dtype=float)
    samples = rng.choice(advantages, size=(N_BOOT, len(advantages)), replace=True).mean(axis=1)
    ci = [float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))]
    g4 = ci[0] > 0
    status = "SUPPORTED" if all([g1, g2, g3, g4]) else "NOT_SUPPORTED"

    results = {
        "test": "T389 spin anti-phase Di-ARA",
        "status": status,
        "source": {"doi": "10.5286/ISIS.E.RB1620201", "medium": "300 K silver",
                   "instrument": "ISIS EMU", "capability": "aggregate 96-detector histograms"},
        "frozen_calibration": {"gamma_mhz_per_g": child["gamma_mhz_per_g"],
                               "relaxation_per_us": child["relaxation_per_us"],
                               "phi0_rad": child["phi0_rad"],
                               "calibration_runs": list(base.CALIBRATION)},
        "coordinate": {"projection": "z(t)=c(t)+i*s(t) from the calibration-frozen 96-detector basis",
                       "ara": "(x_c,x_s)=(1-c,1-s); full anti-phase maps to (2-x_c,2-x_s) after common normalization"},
        "pooled_full_inversion_advantage": float(advantages.mean()),
        "bootstrap_95_full_inversion_advantage": ci,
        "gates": {"inversion_beats_controls_every_field": g1,
                  "negative_half_correlation_every_field": g2,
                  "minimum_near_half_every_field": g3,
                  "bootstrap_advantage_lower_above_zero": g4,
                  "primary_pass": status == "SUPPORTED"},
        "holdout_runs": holdout.to_dict("records"),
        "claim_boundary": "A population detector-field test. T382's child remained unqualified; neutrinos and individual muons are not observed.",
        "protocol_sha256": sha256(PROTOCOL),
        "source_hashes": {run: records[run]["sha256"] for run in selected},
        "artifacts": {"run_summary": str(RUNS), "shift_curves": str(SHIFTS),
                      "figure": str(FIGURE), "report": str(REPORT)},
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(run_frame, shift_frame, projected, results)

    table_frame = holdout[["run", "field_g", "error_full_inversion", "error_direct_repeat",
                           "error_cosine_axis_reflection", "error_sine_axis_reflection",
                           "half_turn_correlation_real", "minimum_correlation_turn_fraction"]]
    headers = list(table_frame.columns)
    table = "| " + " | ".join(headers) + " |\n| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in table_frame.itertuples(index=False, name=None):
        table += "| " + " | ".join(f"{value:.6g}" if isinstance(value, (float, np.floating)) else str(value) for value in row) + " |\n"
    REPORT.write_text(
        "# T389 — spin anti-phase Di-ARA result\n\n"
        f"**{status}.** The primary claim requires all four frozen gates.\n\n"
        "## Holdout results\n\n" + table + "\n\n"
        f"Pooled full-inversion advantage: `{advantages.mean():.6f}`; field-bootstrap 95% interval "
        f"`[{ci[0]:.6f}, {ci[1]:.6f}]`.\n\n"
        "## Boundary\n\n" + results["claim_boundary"] + "\n",
        encoding="utf-8")
    print(json.dumps({"status": status, "advantage": float(advantages.mean()), "ci": ci,
                      "gates": results["gates"]}, indent=2))


if __name__ == "__main__":
    main()
