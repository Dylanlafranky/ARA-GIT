#!/usr/bin/env python3
"""T370: frozen polarized-muon parent-phase handover test.

Dependencies are deliberately limited to NumPy, pandas, pyhdf and the Python
standard library.  pyhdf is installed locally under ``analysis/muon/_vendor``.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_vendor"))

import numpy as np
import pandas as pd
from pyhdf.SD import SD, SDC


DATA = HERE / "data"
RUNS = ["EMU00066666", "EMU00066667", "EMU00066668", "EMU00066669"]
SOURCE_URL = "https://data.isis.stfc.ac.uk/doi-redirect/ISIS/investigation/82360483"
SOURCE_DOI = "10.5286/ISIS.E.RB1620201"
M_MU = 105.6583755
M_E = 0.51099895
T_MIN = 0.25
T_SPLIT = 3.0
T_MAX = 6.0
REBIN = 4
FREQUENCIES = np.arange(0.2, 12.0001, 0.02)
DECAYS = np.arange(0.0, 1.5001, 0.05)
SEED = 370
N_BOOT = 1000

RESULTS = HERE / "T370_POLARIZED_MUON_PHASE_HANDOVER_RESULTS.json"
RUN_CSV = HERE / "T370_POLARIZED_MUON_PHASE_HANDOVER_RUNS.csv"
DET_CSV = HERE / "T370_POLARIZED_MUON_PHASE_HANDOVER_DETECTORS.csv"
CLOSURE_CSV = HERE / "T370_MUON_DECAY_CLOSURE_COORDINATES.csv"
FIGURE = HERE / "T370_POLARIZED_MUON_PHASE_HANDOVER_FIGURE.svg"
REPORT = HERE / "T370_POLARIZED_MUON_PHASE_HANDOVER_REPORT_2026-08-12.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_field(handle: SD, name: str) -> str:
    values = np.asarray(handle.select(name)[:]).reshape(-1).tolist()
    return b"".join(values).decode("latin1").rstrip("\x00 ")


def weighted_rmse(observed: np.ndarray, predicted: np.ndarray, weights: np.ndarray) -> float:
    return float(np.sqrt(np.sum(weights[None, :] * (observed - predicted) ** 2) / (weights.sum() * observed.shape[0])))


def weighted_correlation(observed: np.ndarray, predicted: np.ndarray, weights: np.ndarray) -> float:
    x = observed.reshape(-1)
    y = predicted.reshape(-1)
    w = np.tile(weights, observed.shape[0]).astype(float)
    w /= w.sum()
    mx = np.sum(w * x)
    my = np.sum(w * y)
    cov = np.sum(w * (x - mx) * (y - my))
    vx = np.sum(w * (x - mx) ** 2)
    vy = np.sum(w * (y - my) ** 2)
    return float(cov / np.sqrt(vx * vy))


def fit_parent_phase(time: np.ndarray, y: np.ndarray, weights: np.ndarray, development: np.ndarray):
    target = y[:, development].T
    t_dev = time[development]
    w_dev = weights[development] / weights[development].mean()
    root_w = np.sqrt(w_dev)[:, None]
    best = None
    for decay in DECAYS:
        envelope = np.exp(-decay * t_dev)
        for frequency in FREQUENCIES:
            omega_t = 2.0 * np.pi * frequency * t_dev
            design = np.column_stack((np.ones(len(t_dev)), envelope * np.cos(omega_t), envelope * np.sin(omega_t)))
            beta = np.linalg.lstsq(design * root_w, target * root_w, rcond=None)[0]
            residual = target - design @ beta
            score = float(np.sum(w_dev[:, None] * residual * residual))
            if best is None or score < best[0]:
                best = (score, frequency, decay, beta)
    _, frequency, decay, beta = best
    envelope = np.exp(-decay * time)
    omega_t = 2.0 * np.pi * frequency * time
    design = np.column_stack((np.ones(len(time)), envelope * np.cos(omega_t), envelope * np.sin(omega_t)))
    reversed_design = np.column_stack((np.ones(len(time)), envelope * np.cos(omega_t), -envelope * np.sin(omega_t)))
    return frequency, decay, (design @ beta).T, (reversed_design @ beta).T, beta


def analyse_run(run: str):
    path = DATA / f"{run}.nxs"
    handle = SD(str(path), SDC.READ)
    counts = np.asarray(handle.select("counts")[:], dtype=float)
    time = np.asarray(handle.select("corrected_time")[:], dtype=float)
    n_rebinned = counts.shape[1] // REBIN
    counts = counts[:, : n_rebinned * REBIN].reshape(counts.shape[0], n_rebinned, REBIN).sum(axis=2)
    time = time[: n_rebinned * REBIN].reshape(n_rebinned, REBIN).mean(axis=1)
    total = counts.sum(axis=0)
    eligible = (time >= T_MIN) & (time < T_MAX) & (total > 0)
    time = time[eligible]
    counts = counts[:, eligible]
    total = total[eligible]
    development = time < T_SPLIT
    holdout = ~development

    shares = counts / total
    baseline = np.average(shares[:, development], axis=1, weights=total[development])
    y = shares / baseline[:, None] - 1.0
    frequency, decay, ara_prediction, wrong_orientation, beta = fit_parent_phase(time, y, total, development)
    no_phase = np.repeat(np.average(y[:, development], axis=1, weights=total[development])[:, None], len(time), axis=1)
    persistence = np.repeat(y[:, development][:, -1, None], len(time), axis=1)

    candidates = {
        "ara_parent_phase": ara_prediction,
        "no_phase": no_phase,
        "persistence": persistence,
        "wrong_orientation": wrong_orientation,
    }
    rmse = {name: weighted_rmse(y[:, holdout], prediction[:, holdout], total[holdout]) for name, prediction in candidates.items()}
    correlation = weighted_correlation(y[:, holdout], ara_prediction[:, holdout], total[holdout])
    gates = {
        "beats_no_phase": rmse["ara_parent_phase"] < rmse["no_phase"],
        "beats_persistence": rmse["ara_parent_phase"] < rmse["persistence"],
        "beats_wrong_orientation": rmse["ara_parent_phase"] < rmse["wrong_orientation"],
        "positive_correlation": correlation > 0,
    }

    rng = np.random.default_rng(SEED + int(run[-2:]))
    detector_bootstrap = []
    detector_rows = []
    detector_rmse_model = np.sqrt(np.average((y[:, holdout] - ara_prediction[:, holdout]) ** 2, axis=1, weights=total[holdout]))
    detector_rmse_zero = np.sqrt(np.average((y[:, holdout] - no_phase[:, holdout]) ** 2, axis=1, weights=total[holdout]))
    for detector in range(y.shape[0]):
        detector_rows.append({
            "run": run,
            "detector": detector + 1,
            "phase_cos": float(beta[1, detector]),
            "phase_sin": float(beta[2, detector]),
            "phase_amplitude": float(np.hypot(beta[1, detector], beta[2, detector])),
            "phase_angle_rad": float(math.atan2(beta[2, detector], beta[1, detector])),
            "holdout_rmse_ara": float(detector_rmse_model[detector]),
            "holdout_rmse_no_phase": float(detector_rmse_zero[detector]),
            "ara_improvement": float(1.0 - detector_rmse_model[detector] / detector_rmse_zero[detector]),
        })
    detector_improvement = 1.0 - detector_rmse_model / detector_rmse_zero
    for _ in range(N_BOOT):
        sample = rng.integers(0, y.shape[0], y.shape[0])
        detector_bootstrap.append(float(np.median(detector_improvement[sample])))

    shift_rmse = []
    for shift in range(1, y.shape[0]):
        shifted = np.roll(ara_prediction, shift, axis=0)
        shift_rmse.append(weighted_rmse(y[:, holdout], shifted[:, holdout], total[holdout]))

    metadata = {
        "run": run,
        "title": text_field(handle, "title"),
        "start_time": text_field(handle, "start_time"),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "raw_counts": int(np.asarray(handle.select("counts")[:], dtype=np.int64).sum()),
        "eligible_counts": int(total.sum()),
        "development_counts": int(total[development].sum()),
        "holdout_counts": int(total[holdout].sum()),
        "frequency_mhz": frequency,
        "decay_per_us": decay,
        "holdout_rmse": rmse,
        "holdout_correlation": correlation,
        "improvement_vs_no_phase": 1.0 - rmse["ara_parent_phase"] / rmse["no_phase"],
        "gates": gates,
        "pass": all(gates.values()),
        "median_detector_improvement": float(np.median(detector_improvement)),
        "median_detector_improvement_bootstrap_95": [float(np.quantile(detector_bootstrap, 0.025)), float(np.quantile(detector_bootstrap, 0.975))],
        "circular_shift_better_count": int(np.sum(np.asarray(shift_rmse) <= rmse["ara_parent_phase"])),
        "circular_shift_count": len(shift_rmse),
    }
    series = {
        "time": time,
        "observed": y,
        "predicted": ara_prediction,
        "holdout": holdout,
        "total": total,
        "beta": beta,
    }
    return metadata, detector_rows, series


def decay_closure_crosswalk():
    source = HERE / "T368_SUPERK_DECAYES_AND_NEUTRONS_SOURCE.csv"
    frame = pd.read_csv(source, header=None, usecols=[0, 1], names=["electron_momentum_mev", "electron_time_us"])
    frame = frame[(frame.electron_momentum_mev > 0) & (frame.electron_time_us > 0)].copy()
    # A stopped-muon crosswalk is physically valid only at or below the Michel endpoint.
    endpoint = (M_MU * M_MU + M_E * M_E) / (2.0 * M_MU)
    frame = frame[frame.electron_momentum_mev <= endpoint]
    momentum = frame.electron_momentum_mev.to_numpy()
    energy = np.sqrt(momentum * momentum + M_E * M_E)
    x_visible = 2.0 * energy / M_MU
    x_hidden = 2.0 - x_visible
    hidden_mass_sq = np.maximum(M_MU * M_MU + M_E * M_E - 2.0 * M_MU * energy, 0.0)
    quantiles = np.linspace(0.0, 1.0, 101)
    rows = []
    for q in quantiles:
        p = float(np.quantile(momentum, q))
        e = float(np.sqrt(p * p + M_E * M_E))
        rows.append({
            "quantile": q,
            "electron_momentum_mev": p,
            "visible_ara": 2.0 * e / M_MU,
            "hidden_packet_ara": 2.0 - 2.0 * e / M_MU,
            "hidden_packet_mass_mev": float(np.sqrt(max(M_MU * M_MU + M_E * M_E - 2.0 * M_MU * e, 0.0))),
        })
    pd.DataFrame(rows).to_csv(CLOSURE_CSV, index=False)
    return {
        "eligible_events": int(len(frame)),
        "michel_endpoint_mev_c": endpoint,
        "visible_ara_median": float(np.median(x_visible)),
        "hidden_packet_ara_median": float(np.median(x_hidden)),
        "closure_max_abs_error": float(np.max(np.abs(x_visible + x_hidden - 2.0))),
        "hidden_packet_mass_median_mev": float(np.median(np.sqrt(hidden_mass_sq))),
        "boundary": "Exact closure follows from stopped-parent energy conservation; it is a crosswalk, not an empirical ARA validation.",
    }


def svg_polyline(x, y, x0, y0, width, height, xmin, xmax, ymin, ymax):
    px = x0 + width * (x - xmin) / (xmax - xmin)
    py = y0 + height * (ymax - y) / (ymax - ymin)
    return " ".join(f"{a:.2f},{b:.2f}" for a, b in zip(px, py))


def make_svg(runs, series, closure):
    width, height = 1500, 1150
    panels = []
    for index, meta in enumerate(runs):
        row, col = divmod(index, 2)
        x0, y0 = 70 + col * 710, 130 + row * 315
        w, h = 630, 245
        data = series[meta["run"]]
        time = data["time"]
        beta = data["beta"]
        detector = int(np.argmax(np.hypot(beta[1], beta[2])))
        observed = data["observed"][detector]
        predicted = data["predicted"][detector]
        span = max(0.03, float(np.max(np.abs(np.r_[observed, predicted]))))
        op = svg_polyline(time, observed, x0, y0, w, h, T_MIN, T_MAX, -span, span)
        pp = svg_polyline(time, predicted, x0, y0, w, h, T_MIN, T_MAX, -span, span)
        ridge = y0 + h / 2
        split = x0 + w * (T_SPLIT - T_MIN) / (T_MAX - T_MIN)
        panels.append(f'''<g><rect x="{x0}" y="{y0}" width="{w}" height="{h}" class="panel"/><line x1="{x0}" y1="{ridge}" x2="{x0+w}" y2="{ridge}" class="ridge"/><line x1="{split}" y1="{y0}" x2="{split}" y2="{y0+h}" class="split"/><polyline points="{op}" class="obs"/><polyline points="{pp}" class="pred"/><text x="{x0}" y="{y0-48}" class="title">{html.escape(meta['run'])} · strongest detector {detector+1}</text><text x="{x0}" y="{y0-23}" class="sub">{html.escape(meta['title'])} · f={meta['frequency_mhz']:.3f}/µs · λ={meta['decay_per_us']:.2f}/µs</text><text x="{x0+8}" y="{ridge-7}" class="label">parent ridge</text><text x="{split+8}" y="{y0+18}" class="label">untouched holdout →</text><text x="{x0+w-175}" y="{y0+20}" class="metric">ΔRMSE {100*meta['improvement_vs_no_phase']:+.1f}%</text></g>''')

    cx0, cy0, cw, ch = 70, 800, 630, 245
    close = pd.read_csv(CLOSURE_CSV)
    vv = close.visible_ara.to_numpy()
    hh = close.hidden_packet_ara.to_numpy()
    closure_quantile = close["quantile"].to_numpy()
    pts_v = svg_polyline(closure_quantile, vv, cx0, cy0, cw, ch, 0, 1, 0, 2)
    pts_h = svg_polyline(closure_quantile, hh, cx0, cy0, cw, ch, 0, 1, 0, 2)
    panels.append(f'''<g><rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" class="panel"/><line x1="{cx0}" y1="{cy0+ch/2}" x2="{cx0+cw}" y2="{cy0+ch/2}" class="ridge"/><polyline points="{pts_v}" class="obs"/><polyline points="{pts_h}" class="hidden"/><text x="{cx0}" y="{cy0-48}" class="title">Stopped-muon daughter TE-ARA crosswalk</text><text x="{cx0}" y="{cy0-23}" class="sub">Blue = visible electron · orange = hidden combined neutrino packet · sum is forced to 2</text><text x="{cx0+10}" y="{cy0+ch/2-8}" class="label">1.0 ridge</text></g>''')

    bx0, by0, bw, bh = 780, 800, 630, 245
    labels = [m["run"][-2:] for m in runs]
    vals = [100 * m["improvement_vs_no_phase"] for m in runs]
    scale = max(10.0, max(abs(v) for v in vals) * 1.25)
    bars = []
    for i, (lab, val) in enumerate(zip(labels, vals)):
        bar_w = 95
        x = bx0 + 70 + i * 135
        zero = by0 + bh * 0.72
        bar_h = bh * 0.56 * abs(val) / scale
        y = zero - bar_h if val >= 0 else zero
        bars.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bar_h}" class="bar"/><text x="{x+bar_w/2}" y="{zero+28}" text-anchor="middle" class="label">run {lab}</text><text x="{x+bar_w/2}" y="{y-8}" text-anchor="middle" class="metric">{val:+.1f}%</text>')
    panels.append(f'''<g><rect x="{bx0}" y="{by0}" width="{bw}" height="{bh}" class="panel"/><line x1="{bx0}" y1="{by0+bh*.72}" x2="{bx0+bw}" y2="{by0+bh*.72}" class="ridge"/><text x="{bx0}" y="{by0-48}" class="title">Holdout improvement over no-parent-phase</text><text x="{bx0}" y="{by0-23}" class="sub">Positive means the frozen circular parent relation predicts more of the new acquisition interval</text>{''.join(bars)}</g>''')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><style>text{{font-family:Segoe UI,Arial,sans-serif;fill:#273142}}.bg{{fill:#f7f9fc}}.panel{{fill:#fff;stroke:#cfd7e3;stroke-width:1.5}}.title{{font-size:21px;font-weight:650}}.sub{{font-size:14px;fill:#667085}}.label{{font-size:13px;fill:#596579}}.metric{{font-size:15px;font-weight:650}}.ridge{{stroke:#2f3947;stroke-width:1.4;stroke-dasharray:6 5}}.split{{stroke:#98a2b3;stroke-width:1.2;stroke-dasharray:4 5}}.obs{{fill:none;stroke:#356eb7;stroke-width:2.1}}.pred{{fill:none;stroke:#df9b2f;stroke-width:2.1}}.hidden{{fill:none;stroke:#df7f2f;stroke-width:2.4}}.bar{{fill:#5f89c9;stroke:#355f98}}</style><rect width="100%" height="100%" class="bg"/><text x="70" y="48" style="font-size:32px;font-weight:700">T370 — polarized-muon parent phase → decay handover</text><text x="70" y="80" style="font-size:17px;fill:#667085">Raw EMU detector counts · development before 3 µs · untouched holdout after 3 µs · blue observed · gold predicted</text>{''.join(panels)}<text x="70" y="1120" style="font-size:13px;fill:#667085">Source: ISIS EMU open data, DOI {SOURCE_DOI}. Closure panel is an exact conservation crosswalk and is not counted as empirical validation.</text></svg>'''
    FIGURE.write_text(svg, encoding="utf-8")


def main():
    closure = decay_closure_crosswalk()
    run_results = []
    detector_rows = []
    series = {}
    for run in RUNS:
        result, rows, run_series = analyse_run(run)
        run_results.append(result)
        detector_rows.extend(rows)
        series[run] = run_series
    cross_pass_count = sum(item["pass"] for item in run_results)
    overall_pass = cross_pass_count >= 3

    flat_runs = []
    for item in run_results:
        flat_runs.append({
            "run": item["run"],
            "title": item["title"],
            "raw_counts": item["raw_counts"],
            "eligible_counts": item["eligible_counts"],
            "frequency_mhz": item["frequency_mhz"],
            "decay_per_us": item["decay_per_us"],
            "rmse_ara": item["holdout_rmse"]["ara_parent_phase"],
            "rmse_no_phase": item["holdout_rmse"]["no_phase"],
            "rmse_persistence": item["holdout_rmse"]["persistence"],
            "rmse_wrong_orientation": item["holdout_rmse"]["wrong_orientation"],
            "correlation": item["holdout_correlation"],
            "improvement_vs_no_phase": item["improvement_vs_no_phase"],
            "pass": item["pass"],
        })
    pd.DataFrame(flat_runs).to_csv(RUN_CSV, index=False)
    pd.DataFrame(detector_rows).to_csv(DET_CSV, index=False)

    result = {
        "test": "T370 polarized-muon parent-phase handover",
        "status": "SUPPORTED_AS_CROSSWALK" if overall_pass else "NOT_SUPPORTED",
        "source": {"url": SOURCE_URL, "doi": SOURCE_DOI},
        "protocol": str(HERE / "T370_POLARIZED_MUON_PHASE_HANDOVER_PROTOCOL_2026-08-12.md"),
        "parameters": {"t_min_us": T_MIN, "t_split_us": T_SPLIT, "t_max_us": T_MAX, "rebin_raw_channels": REBIN},
        "decay_closure_crosswalk": closure,
        "runs": run_results,
        "cross_acquisition_pass_count": cross_pass_count,
        "cross_acquisition_required": 3,
        "overall_pass": overall_pass,
        "claim_boundary": "The empirical parent-phase model is the established polarized-muon phase relation written as ARA geometry. Passing recovers the same relation; it does not establish a distinct or hidden new field.",
    }
    RESULTS.write_text(json.dumps(result, indent=2), encoding="utf-8")
    make_svg(run_results, series, closure)

    rows_md = "\n".join(
        f"| {r['run']} | {r['title']} | {r['frequency_mhz']:.3f} | {r['decay_per_us']:.2f} | {r['holdout_rmse']['ara_parent_phase']:.5f} | {r['holdout_rmse']['no_phase']:.5f} | {r['holdout_rmse']['persistence']:.5f} | {r['holdout_rmse']['wrong_orientation']:.5f} | {r['holdout_correlation']:.3f} | {100*r['improvement_vs_no_phase']:+.1f}% | {'PASS' if r['pass'] else 'FAIL'} |"
        for r in run_results
    )
    report = f"""# T370 — Polarized-muon parent-phase handover

## Result

**{'SUPPORTED AS A CROSSWALK' if overall_pass else 'NOT SUPPORTED'}** — the frozen
common parent-phase model passed every primary gate in **{cross_pass_count} of
{len(run_results)}** independent public acquisitions (required: 3 of 4).

The result is a clean recovery of the known polarized-muon decay relation in
ARA language. It is not yet evidence for a new hidden field: the ARA circle and
the established precessing-spin sinusoid are the same mathematical instrument
at this cut.

## Plain-language reading

Before the muon decays, its directional parent relation rotates. After many
decays, different detectors receive slightly different shares of the visible
positrons depending on that parent phase. A single rotating two-coordinate
parent, learned only before 3 microseconds, predicted part of the detector
pattern after 3 microseconds in {cross_pass_count} acquisitions.

For each individual decay, the unobserved two-neutrino packet carries the
remaining energy and the opposite total momentum in the stopped-muon frame.
That makes it the natural hidden complementary daughter branch. Its exact
closure with the visible electron/positron is conservation bookkeeping, not an
independent empirical success.

## Frozen holdout results

| Run | Acquisition | f (/µs) | lambda (/µs) | ARA RMSE | no-phase | persistence | wrong orientation | corr. | vs no-phase | gate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{rows_md}

## Exact daughter closure crosswalk

- Events below the stopped-muon Michel endpoint: **{closure['eligible_events']:,}**
- Median visible daughter ARA: **{closure['visible_ara_median']:.6f}**
- Median hidden-packet ARA: **{closure['hidden_packet_ara_median']:.6f}**
- Maximum numerical closure error in `visible + hidden = 2`:
  **{closure['closure_max_abs_error']:.3g}**

## What this establishes

The pre-decay parent carries directional information that is expressed in the
visible daughter distribution, and a two-pole/circular ARA representation can
recover it from raw detector counts on untouched later time bins. The hidden
combined neutrino packet is the exact complementary daughter in the muon rest
frame.

## What it does not establish

- Standard EMU data do not measure the neutrinos.
- The hidden packet is inferred from conservation, not observed separately.
- The parent-phase ARA model is mathematically the standard polarized-muon
  phase model, so this is a physics crosswalk/recovery rather than a novel
  ARA-only prediction.
- The four acquisitions use different applied fields. They are independent
  repetitions of the frozen method, not identical-condition replications.
- A distinct new claim would require ARA to predict untouched structure beyond
  the standard phase model, or independent directional/energy measurements of
  both visible and invisible daughters.

## Reproduction

```powershell
$env:PYTHONPATH='F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\muon\\_vendor'
& 'C:\\Users\\Dylan\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe' `
  'F:\\SystemFormulaFolder\\GIT\\ARA-GIT\\analysis\\muon\\t370_polarized_muon_phase_handover.py'
```

Raw files are public under ISIS experiment DOI `{SOURCE_DOI}`. The repository
does not need to store them; expected SHA-256 hashes are recorded in the JSON.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "pass_count": cross_pass_count, "figure": str(FIGURE), "report": str(REPORT)}, indent=2))


if __name__ == "__main__":
    main()
