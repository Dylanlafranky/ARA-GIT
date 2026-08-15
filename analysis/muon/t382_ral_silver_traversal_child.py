#!/usr/bin/env python3
"""T382: ARA-native RAL Silver traversal-child test.

This script executes the source-specific frozen protocol and its two pre-outcome
qualification addenda.  It deliberately separates:

* the detector-summed parent population envelope;
* the forward/backward daughter-visible spin relation;
* the native child phase coordinate;
* the child projection; and
* the independently estimated parent ridge.

The source is aggregate histogram data, so individual advance prediction is
marked unavailable rather than approximated with detector channels.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "_vendor"))
from pyhdf.SD import SD, SDC  # noqa: E402


RAW = HERE / "data" / "raw_full"
OUT = HERE / "T382_ral_silver_traversal_child"
OUT.mkdir(exist_ok=True)

CALIBRATION = {
    "EMU00066572": 20.0,
    "EMU00066573": 25.0,
    "EMU00066574": 20.0,
    "EMU00066575": 25.0,
    "EMU00066576": 20.0,
    "EMU00066577": 25.0,
}
VALIDATION = {"EMU00066571": 25.0, "EMU00066584": 20.0}
HOLDOUT = {"EMU00066578": 63.0, "EMU00066579": 160.0, "EMU00066580": 400.0}
DIAGNOSTIC = {"EMU00066581": 1000.0, "EMU00066582": 2000.0, "EMU00066583": 4000.0}
ALL_RUNS = {**CALIBRATION, **VALIDATION, **HOLDOUT, **DIAGNOSTIC}

EXPECTED_HASH = {
    "EMU00066571": "F08F376BC995A88BDF4F5F3DE97E203DD7ACD286A4AC6EAF25818EBFF7F43908",
    "EMU00066572": "A01EE39846193C08DC4B661E04C78ECA60A825337C5AFD1DE9320E666097CB39",
    "EMU00066573": "4A50403866A1218A885733E3228DA24DD38C547CAB792B66020EC6363FB92F05",
    "EMU00066574": "7242B168C30BF685F045AD8F755F8267BE9CBA07EB745D595605EBD8064F531A",
    "EMU00066575": "C351F6D451A85C84E08E114B2FCFA8B8FC9CF750B78B6AC63AE50F18B3D2595B",
    "EMU00066576": "FA55FFC01159D1CAA93838B8BADF0099D16D2A451414C16097D198245A2E58A0",
    "EMU00066577": "12149F36B0441FF6C2A71F5AE8108ADBD8CB19CDEB4E4E9E59A86D6BCA32C751",
    "EMU00066578": "B2C575E52E38A23C61A3F5A8B1D86ACB5D56291AE028B2CC04E3844268CC482C",
    "EMU00066579": "7E88216711AD466AA05ED90FC456A89C26AD56C8F44ABB93E275254816E422A5",
    "EMU00066580": "A48FB41CA2CC4FA34CD23604B03F15F3D67D3CBDCB920187242DBAB3C68A5BB4",
    "EMU00066581": "E18CB646DC10B0E7F2A689E286D78F028AF251AE145EC2011D372BFF26697786",
    "EMU00066582": "75F263E4EA3D759801B135174C4BD0391CCAFC3FD16022DA4F35429033E33B31",
    "EMU00066583": "BCF6F1AEE00ED4F65B9E84729C9F301CDED91E2E6A60EC8076E339119CA9CCF5",
    "EMU00066584": "BE23FD0CFBCF654E53F0D97C044930E5745F636CC4F0BD0E9FC4513573AD3A08",
}

T_MIN = 0.25
T_MAX = 8.0
BG_MIN = 12.0
BG_MAX = 30.0
DEV_MAX = 3.0
SEED = 382
N_PARENT_BOOT = 120
N_PHASE_RANDOM = 4000
N_RUN_BOOT = 20000
KNOWN_GAMMA_MHZ_PER_G = 0.013553896

RESULTS = OUT / "T382_RESULTS.json"
VALIDATION_JSON = OUT / "T382_VALIDATION.json"
RUNS_CSV = OUT / "T382_RUN_SUMMARY.csv"
SERIES_CSV = OUT / "T382_HOLDOUT_SERIES.csv"
SHIFT_CSV = OUT / "T382_DETECTOR_SHIFT_CONTROLS.csv"
FIGURE = OUT / "T382_ARA_NATIVE_CHILD_FIGURE.svg"
REPORT = OUT / "T382_ARA_NATIVE_CHILD_REPORT.html"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def run_path(run: str) -> Path:
    matches = list(RAW.rglob(f"{run}.nxs"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one file for {run}; found {len(matches)}")
    return matches[0]


def text_field(handle: SD, name: str) -> str:
    values = np.asarray(handle.select(name)[:]).reshape(-1).tolist()
    return b"".join(values).decode("latin1").rstrip("\x00 ")


def load_run(run: str, field: float, split: str) -> dict:
    path = run_path(run)
    handle = SD(str(path), SDC.READ)
    try:
        counts = np.asarray(handle.select("counts")[:], dtype=float)
        time = np.asarray(handle.select("corrected_time")[:], dtype=float)
        title = text_field(handle, "title")
        start_time = text_field(handle, "start_time")
        temperature = float(np.asarray(handle.select("temperature")[:]).reshape(-1)[0])
        orientation = text_field(handle, "orientation")
    finally:
        handle.end()

    dt = float(np.median(np.diff(time)))
    analysis = (time >= T_MIN) & (time < T_MAX)
    background = (time >= BG_MIN) & (time < BG_MAX)
    forward = counts[:48].sum(axis=0)
    backward = counts[48:].sum(axis=0)
    total = forward + backward
    hash_value = sha256(path)
    quality = {
        "shape_96_by_2048": list(counts.shape) == [96, 2048],
        "finite_time": bool(np.isfinite(time).all()),
        "strict_time": bool(np.all(np.diff(time) > 0)),
        "native_step_0_016": abs(dt - 0.016) <= 0.0001,
        "finite_counts": bool(np.isfinite(counts).all()),
        "integer_counts": bool(np.allclose(counts, np.rint(counts))),
        "nonnegative_counts": bool((counts >= 0).all()),
        "no_empty_detector_analysis": bool(np.all(counts[:, analysis].sum(axis=1) > 0)),
        "hash_matches": hash_value == EXPECTED_HASH[run],
        "analysis_nonempty": bool(analysis.any()),
        "background_nonempty": bool(background.any()),
    }
    return {
        "run": run,
        "field_g": field,
        "split": split,
        "path": str(path),
        "bytes": path.stat().st_size,
        "sha256": hash_value,
        "title": title,
        "start_time": start_time,
        "temperature_k": temperature,
        "orientation": orientation,
        "counts": counts,
        "time": time,
        "dt_us": dt,
        "analysis_mask": analysis,
        "background_mask": background,
        "forward": forward,
        "backward": backward,
        "total": total,
        "quality": quality,
    }


def poisson_nll(y: np.ndarray, mu: np.ndarray) -> float:
    mu = np.maximum(np.asarray(mu, dtype=float), 1e-12)
    y = np.asarray(y, dtype=float)
    return float(np.sum(mu - y * np.log(mu)))


def poisson_deviance(y: np.ndarray, mu: np.ndarray) -> float:
    mu = np.maximum(np.asarray(mu, dtype=float), 1e-12)
    y = np.asarray(y, dtype=float)
    term = np.zeros_like(y)
    positive = y > 0
    term[positive] = y[positive] * np.log(y[positive] / mu[positive])
    return float(2.0 * np.sum(mu - y + term))


def fit_amplitude(y: np.ndarray, x: np.ndarray, background: float) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    amplitude = max((float(y.sum()) - len(y) * background) / max(float(x.sum()), 1e-12), 0.0)
    for _ in range(60):
        mu = np.maximum(amplitude * x + background, 1e-12)
        gradient = float(np.sum(x * (1.0 - y / mu)))
        hessian = float(np.sum(y * x * x / (mu * mu)))
        if hessian <= 0:
            break
        updated = max(amplitude - gradient / hessian, 0.0)
        if abs(updated - amplitude) <= 1e-10 * max(amplitude, 1.0):
            amplitude = updated
            break
        amplitude = updated
    return amplitude


def parent_fit_for_tau(records: list[dict], tau: float, replacement: dict[str, np.ndarray] | None = None):
    total_nll = 0.0
    fits = {}
    for record in records:
        time = record["time"]
        analysis = record["analysis_mask"]
        background_mask = record["background_mask"]
        full_y = record["total"] if replacement is None else replacement[record["run"]]
        y = full_y[analysis]
        t = time[analysis]
        background = float(np.mean(full_y[background_mask]))
        x = np.exp(-t / tau)
        amplitude = fit_amplitude(y, x, background)
        mu = amplitude * x + background
        nll = poisson_nll(y, mu)
        total_nll += nll
        fits[record["run"]] = {
            "amplitude": amplitude,
            "background": background,
            "nll": nll,
            "deviance": poisson_deviance(y, mu),
            "mu": mu,
        }
    return total_nll, fits


def fit_parent(records: list[dict], grid: np.ndarray, replacement=None):
    scores = []
    for tau in grid:
        scores.append(parent_fit_for_tau(records, float(tau), replacement)[0])
    index = int(np.argmin(scores))
    tau = float(grid[index])
    nll, fits = parent_fit_for_tau(records, tau, replacement)
    return tau, nll, fits


def weighted_lstsq(y: np.ndarray, design: np.ndarray, weights: np.ndarray):
    root = np.sqrt(np.maximum(weights, 1e-12))
    beta = np.linalg.lstsq(design * root[:, None], y * root, rcond=None)[0]
    residual = y - design @ beta
    sse = float(np.sum(weights * residual * residual))
    return beta, sse


def build_asymmetry(record: dict, alpha: float, shift: int = 0):
    counts = record["counts"]
    if shift:
        indices = np.roll(np.arange(96), -shift)
        forward = counts[indices[:48]].sum(axis=0)
        backward = counts[indices[48:]].sum(axis=0)
    else:
        forward = record["forward"]
        backward = record["backward"]
    numerator = forward - alpha * backward
    denominator = forward + alpha * backward
    asymmetry = np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0)
    return asymmetry, denominator


def calibration_alpha(records: list[dict], shift: int = 0) -> float:
    forward_total = 0.0
    backward_total = 0.0
    for record in records:
        mask = record["analysis_mask"]
        counts = record["counts"]
        if shift:
            indices = np.roll(np.arange(96), -shift)
            forward_total += float(counts[indices[:48]][:, mask].sum())
            backward_total += float(counts[indices[48:]][:, mask].sum())
        else:
            forward_total += float(record["forward"][mask].sum())
            backward_total += float(record["backward"][mask].sum())
    return forward_total / backward_total


def child_score(records: list[dict], alpha: float, gamma: float, relaxation: float, shift: int = 0):
    score = 0.0
    details = {}
    for record in records:
        mask = record["analysis_mask"]
        t = record["time"][mask]
        asymmetry, denominator = build_asymmetry(record, alpha, shift)
        y = asymmetry[mask]
        w = denominator[mask]
        omega_t = 2.0 * np.pi * gamma * record["field_g"] * t
        envelope = np.exp(-relaxation * t)
        design = np.column_stack([np.ones(len(t)), envelope * np.cos(omega_t), envelope * np.sin(omega_t)])
        beta, sse = weighted_lstsq(y, design, w)
        score += sse
        details[record["run"]] = {"beta": beta, "sse": sse}
    return score, details


def fit_child_calibration(records: list[dict], alpha: float):
    coarse_gamma = np.arange(0.005, 0.0200001, 0.00005)
    coarse_relaxation = np.arange(0.0, 0.80001, 0.05)
    best = None
    for relaxation in coarse_relaxation:
        for gamma in coarse_gamma:
            score, _ = child_score(records, alpha, float(gamma), float(relaxation))
            if best is None or score < best[0]:
                best = (score, float(gamma), float(relaxation))
    _, gamma0, relaxation0 = best
    fine_gamma = np.arange(max(0.001, gamma0 - 0.00012), gamma0 + 0.0001201, 0.000002)
    fine_relaxation = np.arange(max(0.0, relaxation0 - 0.06), relaxation0 + 0.0601, 0.005)
    for relaxation in fine_relaxation:
        for gamma in fine_gamma:
            score, _ = child_score(records, alpha, float(gamma), float(relaxation))
            if score < best[0]:
                best = (score, float(gamma), float(relaxation))
    score, gamma, relaxation = best
    _, details = child_score(records, alpha, gamma, relaxation)
    phases = []
    phase_weights = []
    for record in records:
        beta = details[record["run"]]["beta"]
        amplitude = float(np.hypot(beta[1], beta[2]))
        phase = float(math.atan2(-beta[2], beta[1]))
        phases.append(phase)
        phase_weights.append(max(amplitude, 1e-12))
        details[record["run"]]["amplitude"] = amplitude
        details[record["run"]]["phase_rad"] = phase
    vector = np.sum(np.asarray(phase_weights) * np.exp(1j * np.asarray(phases)))
    phi0 = float(np.angle(vector))
    phase_concentration = float(abs(vector) / np.sum(phase_weights))
    return {
        "score": score,
        "gamma_mhz_per_g": gamma,
        "relaxation_per_us": relaxation,
        "phi0_rad": phi0,
        "phase_concentration": phase_concentration,
        "details": details,
    }


def fixed_template_fit(record: dict, alpha: float, child: dict, reverse=False, shift: int = 0):
    mask = record["analysis_mask"]
    t = record["time"][mask]
    asymmetry, denominator = build_asymmetry(record, alpha, shift)
    y = asymmetry[mask]
    w = denominator[mask]
    sign = -1.0 if reverse else 1.0
    theta = sign * 2.0 * np.pi * child["gamma_mhz_per_g"] * record["field_g"] * t + child["phi0_rad"]
    template = np.exp(-child["relaxation_per_us"] * t) * np.cos(theta)
    design = np.column_stack([np.ones(len(t)), template])
    beta, sse = weighted_lstsq(y, design, w)
    null_design = np.ones((len(t), 1))
    null_beta, null_sse = weighted_lstsq(y, null_design, w)
    return {
        "sse": sse,
        "null_sse": null_sse,
        "improvement": 1.0 - sse / null_sse,
        "offset": float(beta[0]),
        "amplitude": float(beta[1]),
        "null_offset": float(null_beta[0]),
        "time": t,
        "observed": y,
        "predicted": design @ beta,
        "theta": theta,
        "weight": w,
    }


def free_gamma_diagnostic(record: dict, alpha: float, relaxation: float):
    mask = record["analysis_mask"]
    t = record["time"][mask]
    y_full, denominator = build_asymmetry(record, alpha)
    y = y_full[mask]
    w = denominator[mask]
    gamma_grid = np.arange(0.001, 0.0220001, 0.00002)
    best = None
    envelope = np.exp(-relaxation * t)
    for gamma in gamma_grid:
        omega = 2.0 * np.pi * gamma * record["field_g"] * t
        design = np.column_stack([np.ones(len(t)), envelope * np.cos(omega), envelope * np.sin(omega)])
        beta, sse = weighted_lstsq(y, design, w)
        if best is None or sse < best[0]:
            best = (sse, float(gamma), beta)
    return {"gamma_mhz_per_g": best[1], "frequency_mhz": best[1] * record["field_g"], "sse": best[0]}


def shift_controls(cal_records: list[dict], hold_records: list[dict], child: dict):
    rows = []
    for shift in range(96):
        alpha = calibration_alpha(cal_records, shift)
        # Keep the frozen cadence/relaxation but let each control learn its own
        # calibration phase gauge, matching the primary construction.
        _, details = child_score(cal_records, alpha, child["gamma_mhz_per_g"], child["relaxation_per_us"], shift)
        phases = []
        weights = []
        for record in cal_records:
            beta = details[record["run"]]["beta"]
            phases.append(math.atan2(-beta[2], beta[1]))
            weights.append(max(float(np.hypot(beta[1], beta[2])), 1e-12))
        vector = np.sum(np.asarray(weights) * np.exp(1j * np.asarray(phases)))
        control_child = {**child, "phi0_rad": float(np.angle(vector))}
        improvements = []
        for record in hold_records:
            fit = fixed_template_fit(record, alpha, control_child, shift=shift)
            improvements.append(fit["improvement"])
        rows.append({
            "shift": shift,
            "alpha": alpha,
            "mean_holdout_improvement": float(np.mean(improvements)),
            "min_holdout_improvement": float(np.min(improvements)),
        })
    return pd.DataFrame(rows)


def circular_distance(a: float, b: float) -> float:
    return abs(float(np.angle(np.exp(1j * (a - b)))))


def svg_polyline(x, y, x0, y0, width, height, xmin, xmax, ymin, ymax):
    x = np.asarray(x)
    y = np.asarray(y)
    px = x0 + width * (x - xmin) / (xmax - xmin)
    py = y0 + height * (ymax - y) / (ymax - ymin)
    return " ".join(f"{a:.2f},{b:.2f}" for a, b in zip(px, py))


def make_figure(results: dict, run_rows: pd.DataFrame, series_rows: pd.DataFrame, shifts: pd.DataFrame):
    width, height = 1600, 1120
    colours = {63: "#3578c4", 160: "#6d55b6", 400: "#d8842f"}
    # Panel 1: parent and child coordinates.
    x0, y0, w, h = 90, 165, 650, 350
    panel1 = []
    parent_t = np.linspace(T_MIN, 5.5, 500)
    parent_x = 2.0 * (1.0 - np.exp(-parent_t / results["parent"]["tau_us"]))
    panel1.append(f'<polyline points="{svg_polyline(parent_t,parent_x,x0,y0,w,h,T_MIN,5.5,0,2)}" class="parent"/>')
    for field in [63, 160, 400]:
        theta = 2*np.pi*results["child"]["gamma_mhz_per_g"]*field*parent_t + results["child"]["phi0_rad"]
        child_x = 1.0 - np.cos(theta)
        points = svg_polyline(parent_t, child_x, x0, y0, w, h, T_MIN, 5.5, 0, 2)
        panel1.append(f'<polyline points="{points}" fill="none" stroke="{colours[field]}" stroke-width="1.5" opacity="0.78"/>')
    ridge_y = y0 + h/2
    ridge_x = x0 + w*(results["parent"]["ridge_time_us"]-T_MIN)/(5.5-T_MIN)

    # Panel 2: phase at parent ridge.
    cx, cy, radius = 1110, 340, 155
    polar = [f'<circle cx="{cx}" cy="{cy}" r="{radius}" class="circle"/>',
             f'<line x1="{cx-radius}" y1="{cy}" x2="{cx+radius}" y2="{cy}" class="axis"/>',
             f'<line x1="{cx}" y1="{cy-radius}" x2="{cx}" y2="{cy+radius}" class="axis"/>']
    for row in run_rows[run_rows.split == "holdout"].itertuples():
        px = cx + radius * math.cos(row.phase_at_parent_ridge_rad)
        py = cy - radius * math.sin(row.phase_at_parent_ridge_rad)
        colour = colours[int(row.field_g)]
        polar.append(f'<line x1="{cx}" y1="{cy}" x2="{px:.1f}" y2="{py:.1f}" stroke="{colour}" stroke-width="3"/>')
        polar.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="{colour}"/><text x="{px+10:.1f}" y="{py-8:.1f}" class="small">{int(row.field_g)} G</text>')

    # Panel 3: held-out child template gains.
    bx, by, bw, bh = 90, 700, 650, 260
    bars = []
    hold = run_rows[run_rows.split == "holdout"]
    max_gain = max(0.01, float(max(hold.child_improvement.max(), hold.reverse_improvement.max())) * 1.15)
    for i, row in enumerate(hold.itertuples()):
        base = bx + 80 + i*180
        for j, (value, colour, label) in enumerate([(row.child_improvement,"#3d79bd","aligned"),(row.reverse_improvement,"#b7c0cd","reverse")]):
            hh = bh * max(value,0)/max_gain
            bars.append(f'<rect x="{base+j*48}" y="{by+bh-hh:.1f}" width="34" height="{hh:.1f}" fill="{colour}"/><text x="{base+j*48+17}" y="{by+bh+20}" text-anchor="middle" class="tiny">{label}</text>')
        bars.append(f'<text x="{base+40}" y="{by+bh+48}" text-anchor="middle" class="small">{int(row.field_g)} G</text>')

    # Panel 4: gate and control summary.
    correct_gain = float(shifts.loc[shifts["shift"] == 0, "mean_holdout_improvement"].iloc[0])
    wrong95 = float(np.quantile(shifts.loc[shifts["shift"] != 0, "mean_holdout_improvement"], 0.95))
    gate_lines = [
        ("C01 parent population", results["gates"]["c01_parent_pass"]),
        ("C03-C05 traversal child", results["gates"]["c03_c05_child_pass"]),
        ("C06 child pole -> parent ridge", results["gates"]["c06_alignment_pass"]),
        ("C16 individual prediction", None),
    ]
    gate_svg=[]
    for i,(label,value) in enumerate(gate_lines):
        yy=700+i*58
        status="UNAVAILABLE" if value is None else ("PASS" if value else "FAIL")
        colour="#8a6f2d" if value is None else ("#287a55" if value else "#a64d48")
        gate_svg.append(f'<text x="875" y="{yy}" class="metric">{html.escape(label)}</text><text x="1390" y="{yy}" text-anchor="end" fill="{colour}" style="font:700 20px Segoe UI">{status}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>.bg{{fill:#f6f8fc}}.panel{{fill:#fff;stroke:#cbd3df;stroke-width:1.5}}text{{font-family:Segoe UI,Arial,sans-serif;fill:#263244}}.title{{font-size:30px;font-weight:700}}.subtitle{{font-size:15px;fill:#667085}}.heading{{font-size:20px;font-weight:650}}.small{{font-size:13px}}.tiny{{font-size:10px}}.metric{{font-size:17px;font-weight:600}}.axis{{stroke:#9da8b7;stroke-width:1}}.grid{{stroke:#dfe4ec;stroke-width:1}}.ridge{{stroke:#2e3948;stroke-width:2}}.parent{{fill:none;stroke:#2e3948;stroke-width:4}}.circle{{fill:none;stroke:#aab3c0;stroke-width:2}}</style>
<rect width="100%" height="100%" class="bg"/>
<text x="70" y="55" class="title">T382 — RAL Silver ARA traversal-child test</text>
<text x="70" y="84" class="subtitle">Population parent and native spin child kept separate · primary holdout 63/160/400 G · neutrinos not directly observed</text>
<rect x="55" y="115" width="720" height="455" rx="12" class="panel"/><text x="90" y="145" class="heading">Parent 0–2 and native child 0–2</text>
<line x1="{x0}" y1="{ridge_y}" x2="{x0+w}" y2="{ridge_y}" class="ridge"/><line x1="{ridge_x:.1f}" y1="{y0}" x2="{ridge_x:.1f}" y2="{y0+h}" class="ridge"/>{''.join(panel1)}
<text x="{x0+w/2}" y="545" text-anchor="middle" class="small">time after muon arrival (microseconds)</text><text x="45" y="340" text-anchor="middle" class="small" transform="rotate(-90 45 340)">ARA coordinate (0–2)</text>
<text x="110" y="190" class="small">black: population parent</text><text x="110" y="212" class="small" fill="#3578c4">blue/purple/orange: native spin child at 63/160/400 G</text>
<rect x="810" y="115" width="735" height="455" rx="12" class="panel"/><text x="845" y="145" class="heading">Native child phase when parent reaches ridge 1</text>{''.join(polar)}
<text x="{cx-radius-15}" y="{cy+5}" class="small">child pole π / x=2</text><text x="{cx+radius+10}" y="{cy+5}" class="small">origin 0 / x=0</text>
<text x="845" y="535" class="small">Exact child-mediated claim requires all points within ±π/4 of the left-hand pole.</text>
<rect x="55" y="620" width="720" height="410" rx="12" class="panel"/><text x="90" y="655" class="heading">Frozen child-template gain over no phase</text>{''.join(bars)}
<text x="90" y="995" class="small">Correct detector-axis mean gain {correct_gain:.5f}; wrong-shift 95th percentile {wrong95:.5f}</text>
<rect x="810" y="620" width="735" height="410" rx="12" class="panel"/><text x="845" y="655" class="heading">Frozen decision gates</text>{''.join(gate_svg)}
<text x="845" y="950" class="small">C16 is unavailable because this archive stores aggregate detector histograms.</text>
<text x="845" y="980" class="small">Source: ISIS EMU RB1620201 · protocol and addenda frozen before count inspection.</text>
</svg>'''
    FIGURE.write_text(svg, encoding="utf-8")


def make_report(results: dict, validation: dict, run_rows: pd.DataFrame, shifts: pd.DataFrame):
    gate_rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td class='{('na' if value is None else ('pass' if value else 'fail'))}'>{'UNAVAILABLE' if value is None else ('PASS' if value else 'FAIL')}</td></tr>"
        for name, value in [
            ("C01 parent population", results["gates"]["c01_parent_pass"]),
            ("C03-C05 traversal child", results["gates"]["c03_c05_child_pass"]),
            ("C06 child pole to parent ridge", results["gates"]["c06_alignment_pass"]),
            ("C16 individual advance prediction", None),
        ]
    )
    rows = []
    for row in run_rows.itertuples():
        phase = "—" if not np.isfinite(row.phase_at_parent_ridge_rad) else f"{row.phase_at_parent_ridge_rad:.4f}"
        child_x = "—" if not np.isfinite(row.child_at_parent_ridge) else f"{row.child_at_parent_ridge:.4f}"
        imp = "—" if not np.isfinite(row.child_improvement) else f"{100*row.child_improvement:+.3f}%"
        rows.append(f"<tr><td>{row.run}</td><td>{row.split}</td><td>{row.field_g:.0f}</td><td>{row.parent_nll_gain:.4f}</td><td>{imp}</td><td>{phase}</td><td>{child_x}</td></tr>")
    dq_failures = [f"{run}:{key}" for run, checks in validation["data_quality_by_run"].items() for key, value in checks.items() if not value]
    correct_gain = float(shifts.loc[shifts["shift"] == 0, "mean_holdout_improvement"].iloc[0])
    wrong95 = float(np.quantile(shifts.loc[shifts["shift"] != 0, "mean_holdout_improvement"], 0.95))
    report = f'''<!doctype html><html><head><meta charset="utf-8"><title>T382 RAL Silver traversal child</title><style>
body{{font-family:Segoe UI,Arial,sans-serif;background:#f5f7fb;color:#253044;margin:0}}main{{max-width:1240px;margin:auto;padding:34px}}.card{{background:white;border:1px solid #d5dbe5;border-radius:12px;padding:24px;margin:18px 0}}h1{{font-size:34px}}h2{{margin-top:0}}table{{width:100%;border-collapse:collapse}}th,td{{padding:9px;border-bottom:1px solid #e3e7ee;text-align:left}}.pass{{color:#167149;font-weight:700}}.fail{{color:#a33f3b;font-weight:700}}.na{{color:#8a6f2d;font-weight:700}}code{{background:#eef2f7;padding:2px 5px;border-radius:4px}}img{{width:100%;height:auto}}.boundary{{border-left:5px solid #d18a33}}</style></head><body><main>
<h1>T382 — RAL Silver ARA traversal-child test</h1><p><b>{html.escape(results['status'].replace('_',' '))}</b></p>
<div class="card boundary"><h2>Identity boundary</h2><p>This is a Class P aggregate μSR test. Phase A is the declared traversal direction of the spin child; the parent is the detector-summed muon population. The neutrino pair is not directly observed, and C16 cannot be evaluated.</p></div>
<div class="card"><h2>Frozen gates</h2><table><tr><th>Cut</th><th>Verdict</th></tr>{gate_rows}</table></div>
<div class="card"><h2>Visual result</h2><img src="{FIGURE.name}" alt="T382 ARA parent and traversal child results"></div>
<div class="card"><h2>Key measurements</h2><ul>
<li>Parent lifetime: <b>{results['parent']['tau_us']:.6f} μs</b>; ridge time <b>{results['parent']['ridge_time_us']:.6f} μs</b>.</li>
<li>ARA-calibrated child cadence coefficient: <b>{results['child']['gamma_mhz_per_g']:.8f} MHz/G</b>.</li>
<li>External established coefficient revealed after fitting: <b>{KNOWN_GAMMA_MHZ_PER_G:.8f} MHz/G</b>; relative difference <b>{100*results['child']['known_gamma_relative_error']:.3f}%</b>.</li>
<li>Calibration phase concentration: <b>{results['child']['calibration_phase_concentration']:.4f}</b>.</li>
<li>Mean holdout pole score: <b>{results['alignment']['mean_pole_score']:.4f}</b>, run-bootstrap 95% interval <b>[{results['alignment']['bootstrap_95'][0]:.4f}, {results['alignment']['bootstrap_95'][1]:.4f}]</b>.</li>
<li>Correct detector-axis mean child gain: <b>{correct_gain:.6f}</b>; wrong-shift 95th percentile: <b>{wrong95:.6f}</b>.</li>
</ul></div>
<div class="card"><h2>Per-run audit</h2><table><tr><th>run</th><th>split</th><th>field G</th><th>parent NLL gain</th><th>child gain</th><th>phase at parent ridge rad</th><th>native child x at parent ridge</th></tr>{''.join(rows)}</table></div>
<div class="card"><h2>Data quality</h2><p>{'All frozen checks passed.' if not dq_failures else 'Failures: '+html.escape(', '.join(dq_failures))}</p><p>Files: {len(validation['data_quality_by_run'])}; native bins: 2,048; detectors: 96.</p></div>
<div class="card"><h2>Interpretation</h2><p>{html.escape(results['plain_language'])}</p><p>{html.escape(results['claim_boundary'])}</p></div>
<div class="card"><h2>Reproduction</h2><p>Run <code>t382_ral_silver_traversal_child.py</code> with the bundled Python 3.12 runtime after the frozen source files are present under <code>analysis/muon/data/raw_full</code>.</p></div>
</main></body></html>'''
    REPORT.write_text(report, encoding="utf-8")


def main():
    split_lookup = {}
    for run in CALIBRATION: split_lookup[run] = "calibration"
    for run in VALIDATION: split_lookup[run] = "validation"
    for run in HOLDOUT: split_lookup[run] = "holdout"
    for run in DIAGNOSTIC: split_lookup[run] = "diagnostic"
    records = {run: load_run(run, field, split_lookup[run]) for run, field in ALL_RUNS.items()}
    calibration = [records[run] for run in CALIBRATION]
    validation_records = [records[run] for run in VALIDATION]
    holdout = [records[run] for run in HOLDOUT]

    data_quality = {run: record["quality"] for run, record in records.items()}
    data_quality_pass = all(all(checks.values()) for checks in data_quality.values())

    # C01 parent calibration.
    coarse_tau = np.arange(1.5, 3.0001, 0.002)
    tau0, _, _ = fit_parent(calibration, coarse_tau)
    fine_tau = np.arange(max(0.5, tau0 - 0.02), tau0 + 0.02001, 0.0001)
    tau_parent, parent_nll, parent_cal_fits = fit_parent(calibration, fine_tau)
    ridge_time = tau_parent * math.log(2.0)

    rng = np.random.default_rng(SEED)
    parent_boot = []
    bootstrap_grid = np.arange(max(0.5, tau_parent - 0.05), tau_parent + 0.05001, 0.0005)
    for _ in range(N_PARENT_BOOT):
        replacement = {}
        for record in calibration:
            fit = parent_cal_fits[record["run"]]
            full_mu = np.full_like(record["total"], fit["background"], dtype=float)
            mask = record["analysis_mask"]
            full_mu[mask] = fit["amplitude"] * np.exp(-record["time"][mask] / tau_parent) + fit["background"]
            replacement[record["run"]] = rng.poisson(np.maximum(full_mu, 1e-9)).astype(float)
        boot_tau, _, _ = fit_parent(calibration, bootstrap_grid, replacement)
        parent_boot.append(boot_tau)

    # Per-run parent fits and baseline comparisons.
    per_run_parent = {}
    independent_tau_grid = np.arange(max(0.5, tau_parent * 0.6), tau_parent * 1.4 + 0.0001, 0.001)
    for record in records.values():
        _, fixed = parent_fit_for_tau([record], tau_parent)
        fit = fixed[record["run"]]
        mask = record["analysis_mask"]
        y = record["total"][mask]
        constant = np.repeat(max(float(np.mean(y)), 1e-12), len(y))
        null_nll = poisson_nll(y, constant)
        individual_tau, _, _ = fit_parent([record], independent_tau_grid)
        per_run_parent[record["run"]] = {
            "nll": fit["nll"],
            "null_nll": null_nll,
            "nll_gain": null_nll - fit["nll"],
            "deviance": fit["deviance"],
            "individual_tau_us": individual_tau,
            "ridge_shift_fraction": abs(individual_tau - tau_parent) / tau_parent,
            "amplitude": fit["amplitude"],
            "background": fit["background"],
        }

    parent_holdout_better = all(per_run_parent[r]["nll_gain"] > 0 for r in HOLDOUT)
    parent_drift_ok = all(per_run_parent[r]["ridge_shift_fraction"] <= 0.10 for r in HOLDOUT)
    c01_pass = bool(data_quality_pass and parent_holdout_better and parent_drift_ok and T_MIN < ridge_time < T_MAX)

    # C03-C05 calibration and holdout template tests.
    alpha = calibration_alpha(calibration)
    child = fit_child_calibration(calibration, alpha)
    child_fits = {}
    reverse_fits = {}
    free_gamma = {}
    for record in records.values():
        child_fits[record["run"]] = fixed_template_fit(record, alpha, child, reverse=False)
        reverse_fits[record["run"]] = fixed_template_fit(record, alpha, child, reverse=True)
        if record["split"] in {"validation", "holdout", "diagnostic"}:
            free_gamma[record["run"]] = free_gamma_diagnostic(record, alpha, child["relaxation_per_us"])

    shifts = shift_controls(calibration, holdout, child)
    shifts.to_csv(SHIFT_CSV, index=False)
    correct_shift_gain = float(shifts.loc[shifts["shift"] == 0, "mean_holdout_improvement"].iloc[0])
    wrong_shift_95 = float(np.quantile(shifts.loc[shifts["shift"] != 0, "mean_holdout_improvement"], 0.95))
    holdout_improvement_each = all(child_fits[r]["improvement"] > 0 for r in HOLDOUT)
    validation_improvement_each = all(child_fits[r]["improvement"] > 0 for r in VALIDATION)
    primary_mean_gain = float(np.mean([child_fits[r]["improvement"] for r in HOLDOUT]))
    reverse_mean_gain = float(np.mean([reverse_fits[r]["improvement"] for r in HOLDOUT]))
    beats_reverse = primary_mean_gain > reverse_mean_gain
    beats_shifts = correct_shift_gain > wrong_shift_95
    holdout_recovered_frequency = [free_gamma[r]["frequency_mhz"] for r in HOLDOUT]
    frequency_monotone = bool(np.all(np.diff(holdout_recovered_frequency) > 0))
    positive_amplitude = all(child_fits[r]["amplitude"] > 0 for r in HOLDOUT)
    child_pass = bool(data_quality_pass and validation_improvement_each and holdout_improvement_each and beats_reverse and beats_shifts and frequency_monotone and positive_amplitude)

    # C06 independent parent-ridge/child-phase comparison.
    alignment_rows = []
    for run, field in HOLDOUT.items():
        theta = float((2.0 * np.pi * child["gamma_mhz_per_g"] * field * ridge_time + child["phi0_rad"]) % (2.0 * np.pi))
        child_at_parent = float(1.0 - math.cos(theta))
        projected = child_at_parent / 2.0
        pole_score = float(-math.cos(theta))
        distance = circular_distance(theta, math.pi)
        mirror_theta = float((-2.0 * np.pi * child["gamma_mhz_per_g"] * field * ridge_time + child["phi0_rad"]) % (2.0*np.pi))
        alignment_rows.append({
            "run": run,
            "field_g": field,
            "phase_at_parent_ridge_rad": theta,
            "distance_to_child_pole_rad": distance,
            "child_at_parent_ridge": child_at_parent,
            "projected_child_at_parent_ridge": projected,
            "pole_score": pole_score,
            "mirror_pole_score": float(-math.cos(mirror_theta)),
        })
    alignment_frame = pd.DataFrame(alignment_rows)
    pole_scores = alignment_frame.pole_score.to_numpy()
    mirror_scores = alignment_frame.mirror_pole_score.to_numpy()
    run_boot = []
    for _ in range(N_RUN_BOOT):
        sample = rng.integers(0, len(pole_scores), len(pole_scores))
        run_boot.append(float(np.mean(pole_scores[sample])))
    boot_ci = [float(np.quantile(run_boot, 0.025)), float(np.quantile(run_boot, 0.975))]
    phases = alignment_frame.phase_at_parent_ridge_rad.to_numpy()
    mean_vector = np.mean(np.exp(1j * phases))
    mean_direction = float(np.angle(mean_vector) % (2*np.pi))
    reference_distances = {name: circular_distance(mean_direction, value) for name, value in {"pole_pi":np.pi,"origin_0":0.0,"quarter_pi_2":np.pi/2,"quarter_3pi_2":3*np.pi/2}.items()}
    all_within_quarter = bool(np.all(alignment_frame.distance_to_child_pole_rad.to_numpy() <= np.pi/4))
    mean_closer_to_pole = reference_distances["pole_pi"] == min(reference_distances.values())
    random_phi = rng.uniform(0.0, 2*np.pi, N_PHASE_RANDOM)
    random_scores = []
    fields = np.asarray(list(HOLDOUT.values()), dtype=float)
    for phi in random_phi:
        random_theta = (2*np.pi*child["gamma_mhz_per_g"]*fields*ridge_time + phi) % (2*np.pi)
        random_scores.append(float(np.mean(-np.cos(random_theta))))
    random_975 = float(np.quantile(random_scores, 0.975))
    mean_pole_score = float(np.mean(pole_scores))
    beats_random = mean_pole_score > random_975
    beats_mirror = mean_pole_score > float(np.mean(mirror_scores))
    c06_pass = bool(child_pass and all_within_quarter and mean_closer_to_pole and boot_ci[0] > 0 and beats_random and beats_mirror)

    # Output run table and holdout series.
    run_rows = []
    series_rows = []
    alignment_lookup = alignment_frame.set_index("run").to_dict("index")
    for run, record in records.items():
        fit = child_fits[run]
        reverse = reverse_fits[run]
        align = alignment_lookup.get(run, {})
        run_rows.append({
            "run": run,
            "split": record["split"],
            "field_g": record["field_g"],
            "start_time": record["start_time"],
            "temperature_k": record["temperature_k"],
            "orientation_metadata": record["orientation"],
            "analysis_counts": int(record["total"][record["analysis_mask"]].sum()),
            "parent_nll_gain": per_run_parent[run]["nll_gain"],
            "individual_tau_us": per_run_parent[run]["individual_tau_us"],
            "parent_ridge_shift_fraction": per_run_parent[run]["ridge_shift_fraction"],
            "child_improvement": fit["improvement"],
            "child_amplitude": fit["amplitude"],
            "reverse_improvement": reverse["improvement"],
            "free_gamma_mhz_per_g": free_gamma.get(run, {}).get("gamma_mhz_per_g", np.nan),
            "recovered_frequency_mhz": free_gamma.get(run, {}).get("frequency_mhz", np.nan),
            "phase_at_parent_ridge_rad": align.get("phase_at_parent_ridge_rad", np.nan),
            "distance_to_child_pole_rad": align.get("distance_to_child_pole_rad", np.nan),
            "child_at_parent_ridge": align.get("child_at_parent_ridge", np.nan),
            "projected_child_at_parent_ridge": align.get("projected_child_at_parent_ridge", np.nan),
            "pole_score": align.get("pole_score", np.nan),
        })
        if record["split"] == "holdout":
            t = fit["time"]
            x_parent = 2.0 * (1.0 - np.exp(-t/tau_parent))
            x_child = 1.0 - np.cos(fit["theta"])
            for i in range(len(t)):
                series_rows.append({
                    "run": run,
                    "field_g": record["field_g"],
                    "time_us": t[i],
                    "parent_ara": x_parent[i],
                    "native_child_ara": x_child[i],
                    "projected_child_ara": x_child[i]/2.0,
                    "observed_fb_asymmetry": fit["observed"][i],
                    "predicted_fb_asymmetry": fit["predicted"][i],
                    "detector_weight": fit["weight"][i],
                })
    run_frame = pd.DataFrame(run_rows).sort_values(["split", "field_g", "run"])
    series_frame = pd.DataFrame(series_rows)
    run_frame.to_csv(RUNS_CSV, index=False)
    series_frame.to_csv(SERIES_CSV, index=False)

    gates = {
        "data_quality_pass": data_quality_pass,
        "c01_parent_pass": c01_pass,
        "c03_c05_child_pass": child_pass,
        "c06_alignment_pass": c06_pass,
        "c16_individual_prediction": None,
        "c01_components": {
            "parent_beats_constant_every_holdout": parent_holdout_better,
            "holdout_ridge_drift_within_10_percent": parent_drift_ok,
            "parent_ridge_inside_window": T_MIN < ridge_time < T_MAX,
        },
        "child_components": {
            "validation_gain_positive_each": validation_improvement_each,
            "holdout_gain_positive_each": holdout_improvement_each,
            "beats_reverse_pooled": beats_reverse,
            "beats_95_percent_detector_shifts": beats_shifts,
            "holdout_recovered_frequency_monotone": frequency_monotone,
            "holdout_amplitude_positive_each": positive_amplitude,
        },
        "alignment_components": {
            "every_holdout_within_pi_over_4": all_within_quarter,
            "mean_direction_closest_to_pi": mean_closer_to_pole,
            "bootstrap_lower_above_zero": boot_ci[0] > 0,
            "beats_random_phase_97_5_percentile": beats_random,
            "beats_mirror": beats_mirror,
        },
    }
    if c01_pass and child_pass and c06_pass:
        status = "CHILD_HANDOVER_ALIGNMENT_LEAD"
        plain = "The population parent and spin traversal child were both recovered, and the frozen child pole aligned with the parent ridge across the primary field ladder. This is a weak three-run population lead requiring same-medium replication."
    elif c01_pass and child_pass:
        status = "CHILD_RECOVERED_ALIGNMENT_NOT_SUPPORTED"
        plain = "The population parent and physical spin traversal child were recovered separately, but the child pole did not satisfy the frozen parent-ridge alignment gates. The child is readable through the charged daughter distribution without evidence that this phase triggers the population decay handover."
    elif c01_pass:
        status = "PARENT_RECOVERED_CHILD_NOT_QUALIFIED"
        plain = "The parent population cycle was recovered, but the frozen forward/backward spin relation did not qualify as a stable traversal child under the controls. No child-handover interpretation is made."
    else:
        status = "SOURCE_OR_PARENT_GATE_FAILED"
        plain = "The source did not pass the frozen data/parent construct gates, so the child-handover claim is not evaluated as physical evidence."

    results = {
        "test": "T382 RAL Silver ARA-native traversal-child handover",
        "status": status,
        "source": {
            "doi": "10.5286/ISIS.E.RB1620201",
            "investigation": "Muon search for fluctuating loop currents in cuprates",
            "instrument": "ISIS EMU",
            "capability_class": "P_population_histograms",
        },
        "phase_orientation": "Phase A traversal 0->2; Phase B return 2->0 within the spin child",
        "parent": {
            "tau_us": tau_parent,
            "ridge_time_us": ridge_time,
            "bootstrap_95_tau_us": [float(np.quantile(parent_boot,0.025)), float(np.quantile(parent_boot,0.975))],
            "population_coordinate": "xP(t)=2*(1-exp(-t/tau))",
        },
        "child": {
            "alpha_forward_backward": alpha,
            "gamma_mhz_per_g": child["gamma_mhz_per_g"],
            "relaxation_per_us": child["relaxation_per_us"],
            "phi0_rad": child["phi0_rad"],
            "calibration_phase_concentration": child["phase_concentration"],
            "known_gamma_mhz_per_g_revealed_after_fit": KNOWN_GAMMA_MHZ_PER_G,
            "known_gamma_relative_error": abs(child["gamma_mhz_per_g"]-KNOWN_GAMMA_MHZ_PER_G)/KNOWN_GAMMA_MHZ_PER_G,
            "native_coordinate": "xC(t)=1-cos(theta(t))",
            "projection": "pC=xC/2",
            "mean_holdout_gain": primary_mean_gain,
            "mean_reverse_gain": reverse_mean_gain,
            "correct_shift_gain": correct_shift_gain,
            "wrong_shift_95": wrong_shift_95,
        },
        "alignment": {
            "runs": alignment_rows,
            "mean_direction_rad": mean_direction,
            "mean_resultant_length": float(abs(mean_vector)),
            "mean_pole_score": mean_pole_score,
            "bootstrap_95": boot_ci,
            "random_phase_97_5": random_975,
            "mean_mirror_pole_score": float(np.mean(mirror_scores)),
            "reference_distances_rad": reference_distances,
        },
        "gates": gates,
        "plain_language": plain,
        "claim_boundary": "Aggregate daughter histograms reconstruct a population parent and candidate spin child. Neutrinos are not directly observed, and individual advance prediction is unavailable.",
        "artifacts": {
            "run_summary": str(RUNS_CSV),
            "holdout_series": str(SERIES_CSV),
            "shift_controls": str(SHIFT_CSV),
            "figure": str(FIGURE),
            "report": str(REPORT),
        },
    }
    validation = {
        "protocol": "T382_RAL_SILVER_TRAVERSAL_CHILD_PROTOCOL_2026-08-14.md",
        "source_qualification_addendum": "T382_SOURCE_QUALIFICATION_ADDENDUM_2026-08-14.md",
        "instrument_band_addendum": "T382_INSTRUMENT_BAND_ADDENDUM_2026-08-14.md",
        "data_quality_by_run": data_quality,
        "all_data_quality_pass": data_quality_pass,
        "split_counts": {"calibration":len(CALIBRATION),"validation":len(VALIDATION),"holdout":len(HOLDOUT),"diagnostic":len(DIAGNOSTIC)},
        "individual_prediction_available": False,
        "notes": [
            "Forward/backward bank definition follows the official EMU user guide: detectors 1-48 and 49-96.",
            "The source metadata orientation is recorded as l; the spin child is admitted only through the frozen calibration qualification.",
            "1000/2000/4000 G runs are diagnostics outside the primary instrument-band gate.",
        ],
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    VALIDATION_JSON.write_text(json.dumps(validation, indent=2), encoding="utf-8")
    make_figure(results, run_frame, series_frame, shifts)
    make_report(results, validation, run_frame, shifts)
    print(json.dumps({
        "status": status,
        "tau_us": tau_parent,
        "gamma_mhz_per_g": child["gamma_mhz_per_g"],
        "c01": c01_pass,
        "c03_c05": child_pass,
        "c06": c06_pass,
        "c16": None,
        "report": str(REPORT),
    }, indent=2))


if __name__ == "__main__":
    main()
