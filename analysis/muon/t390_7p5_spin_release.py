#!/usr/bin/env python3
"""T390 frozen 7.5-spin population-release test."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

import t382_ral_silver_traversal_child as base


HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / "T390_7P5_SPIN_RELEASE_PROTOCOL_2026-08-15.md"
T382_RESULTS = HERE / "T382_ral_silver_detector_share" / "T382_DETECTOR_SHARE_RESULTS.json"
OUT = HERE / "T390_7p5_spin_release"
OUT.mkdir(exist_ok=True)
RESULTS = OUT / "T390_RESULTS.json"
LANDMARKS = OUT / "T390_HALF_INTEGER_LANDMARKS.csv"
CONTROLS = OUT / "T390_CONTROL_SCORES.csv"
FIELDS = OUT / "T390_FIELD_DETAILS.csv"
BOOTSTRAP = OUT / "T390_DETECTOR_BOOTSTRAP.csv"
FIGURE = OUT / "T390_7P5_SPIN_RELEASE.svg"
REPORT = OUT / "T390_7P5_SPIN_RELEASE_REPORT.md"

T_MIN = 0.25
T_MAX = 10.0
WINDOW_HALF_TURNS = 0.125
SEED = 390
N_BOOT = 800


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def fit_parent_series(record: dict, tau: float, total_override: np.ndarray | None = None) -> dict:
    total = record["total"] if total_override is None else np.asarray(total_override, dtype=float)
    time = record["time"]
    mask = (time >= T_MIN) & (time < T_MAX)
    background_mask = record["background_mask"]
    background = float(np.mean(total[background_mask]))
    t = time[mask]
    observed = total[mask]
    shape = np.exp(-t / tau)
    amplitude = base.fit_amplitude(observed, shape, background)
    expected = amplitude * shape + background
    pearson = (observed - expected) / np.sqrt(np.maximum(expected, 1.0))
    return {"time": t, "observed": observed, "expected": expected, "pearson": pearson,
            "amplitude": amplitude, "background": background}


def landmark_time(turns: float, timing_field_g: float, gamma: float, phi_cycles: float) -> float:
    return (turns - phi_cycles) / (gamma * timing_field_g)


def score_mapping(records: dict[str, dict], fits: dict[str, dict], turns: float,
                  timing_fields: dict[str, float], gamma: float, phi_cycles: float) -> dict | None:
    observed_total = 0.0
    expected_total = 0.0
    field_rows = []
    for run, actual_field in base.HOLDOUT.items():
        timing_field = float(timing_fields[run])
        centre = landmark_time(turns, timing_field, gamma, phi_cycles)
        half_width = WINDOW_HALF_TURNS / (gamma * timing_field)
        if centre - half_width < T_MIN or centre + half_width >= T_MAX:
            return None
        fit = fits[run]
        window = np.abs(fit["time"] - centre) <= half_width
        if not np.any(window):
            return None
        observed = float(fit["observed"][window].sum())
        expected = float(fit["expected"][window].sum())
        mean_pearson = float(fit["pearson"][window].mean())
        observed_total += observed; expected_total += expected
        field_rows.append({"run": run, "field_g": float(actual_field), "timing_field_g": timing_field,
                           "turns": float(turns), "centre_us": centre, "half_width_us": half_width,
                           "n_bins": int(window.sum()), "observed_counts": observed,
                           "expected_counts": expected, "observed_expected_ratio": observed / expected,
                           "mean_pearson_residual": mean_pearson})
    return {"turns": float(turns), "observed_counts": observed_total, "expected_counts": expected_total,
            "observed_expected_ratio": observed_total / expected_total,
            "excess_ratio": observed_total / expected_total - 1.0,
            "field_rows": field_rows}


def candidate_landmarks(records, fits, gamma, phi_cycles):
    timing = {run: field for run, field in base.HOLDOUT.items()}
    rows = []
    for turns in np.arange(0.5, 8.5001, 1.0):
        score = score_mapping(records, fits, float(turns), timing, gamma, phi_cycles)
        if score is not None:
            rows.append({k: v for k, v in score.items() if k != "field_rows"})
    return pd.DataFrame(rows)


def control_scores(records, fits, gamma, phi_cycles):
    actual = {run: field for run, field in base.HOLDOUT.items()}
    rows = []
    for family, values in {
        "integer": np.arange(1.0, 9.0001, 1.0),
        "quarter": np.arange(0.25, 9.0001, 1.0),
        "three_quarter": np.arange(0.75, 9.0001, 1.0),
    }.items():
        for turns in values:
            score = score_mapping(records, fits, float(turns), actual, gamma, phi_cycles)
            if score is not None:
                rows.append({"control_family": family, "label": f"{family}_{turns:g}",
                             **{k: v for k, v in score.items() if k != "field_rows"}})
    runs = list(base.HOLDOUT)
    fields = [base.HOLDOUT[run] for run in runs]
    for index, permutation in enumerate(itertools.permutations(fields)):
        if list(permutation) == fields:
            continue
        timing = dict(zip(runs, permutation))
        score = score_mapping(records, fits, 7.5, timing, gamma, phi_cycles)
        if score is not None:
            rows.append({"control_family": "field_permutation", "label": f"field_permutation_{index}",
                         **{k: v for k, v in score.items() if k != "field_rows"}})
    return pd.DataFrame(rows)


def bootstrap_candidate(records: dict[str, dict], tau: float, gamma: float, phi_cycles: float):
    rng = np.random.default_rng(SEED)
    rows = []
    timing = {run: field for run, field in base.HOLDOUT.items()}
    for replicate in range(N_BOOT):
        boot_fits = {}
        for run, record in records.items():
            indices = rng.integers(0, 96, 96)
            total = record["counts"][indices].sum(axis=0)
            boot_fits[run] = fit_parent_series(record, tau, total)
        score = score_mapping(records, boot_fits, 7.5, timing, gamma, phi_cycles)
        rows.append({"replicate": replicate, "observed_expected_ratio": score["observed_expected_ratio"],
                     "excess_ratio": score["excess_ratio"]})
    return pd.DataFrame(rows)


def make_figure(fits: dict[str, dict], landmarks: pd.DataFrame, controls: pd.DataFrame,
                results: dict):
    colours = {63.0: "#2f6fb3", 160.0: "#d99226", 400.0: "#8755a6"}
    width, height = 1600, 1120
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="#f6f8fb"/>',
             '<style>.title{font:700 32px Arial;fill:#17202b}.heading{font:700 20px Arial;fill:#17202b}.body{font:16px Arial;fill:#26313d}.small{font:13px Arial;fill:#596575}.panel{fill:white;stroke:#d4dbe5;stroke-width:2}.axis{stroke:#46515e;stroke-width:1.2}.grid{stroke:#e2e6ec;stroke-width:1}</style>',
             '<text x="55" y="50" class="title">T390 — does population release concentrate at 7.5 spin turns?</text>',
             '<text x="55" y="78" class="body">300 K silver · detector-summed charged daughters · 0.25–10.00 μs · neutrinos are not directly detected</text>']
    panels = [(50, 105, 720, 440), (830, 105, 720, 440), (50, 595, 720, 440), (830, 595, 720, 440)]
    for x, y, w, h in panels:
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="panel"/>')

    # Panel 1: smoothed residuals and field-specific candidate times.
    parts.append('<text x="75" y="140" class="heading">Summed release residuals; dashed lines mark 7.5 turns</text>')
    x0, y0, pw, ph = 110, 180, 610, 300
    residual_sets = []
    for detail in results["candidate_7p5"]["field_rows"]:
        fit = fits[detail["run"]]
        rolling = pd.Series(fit["pearson"]).rolling(9, center=True, min_periods=1).mean().to_numpy()
        residual_sets.append((detail, fit["time"], rolling))
    ymin = min(float(np.quantile(v, 0.01)) for _, _, v in residual_sets)
    ymax = max(float(np.quantile(v, 0.99)) for _, _, v in residual_sets)
    pad = 0.08 * max(ymax-ymin, 1e-6); ymin -= pad; ymax += pad
    for tick in [0, 2, 4, 6, 8, 10]:
        px = x0 + pw*(tick-T_MIN)/(T_MAX-T_MIN)
        parts.extend([f'<line x1="{px:.1f}" y1="{y0}" x2="{px:.1f}" y2="{y0+ph}" class="grid"/>',
                      f'<text x="{px:.1f}" y="{y0+ph+21}" class="small" text-anchor="middle">{tick:g}</text>'])
    zero_y = y0 + ph*(ymax)/(ymax-ymin); parts.append(f'<line x1="{x0}" y1="{zero_y:.1f}" x2="{x0+pw}" y2="{zero_y:.1f}" class="grid"/>')
    for tick in [ymin, 0.0, ymax]:
        py = y0+ph*(ymax-tick)/(ymax-ymin)
        parts.append(f'<line x1="{x0-5}" y1="{py:.1f}" x2="{x0}" y2="{py:.1f}" class="axis"/><text x="{x0-10}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:.2f}</text>')
    for detail, time, rolling in residual_sets:
        field = detail["field_g"]
        stride = max(1, len(time)//500)
        points = " ".join(f"{x0+pw*(t-T_MIN)/(T_MAX-T_MIN):.1f},{y0+ph*(ymax-r)/(ymax-ymin):.1f}" for t, r in zip(time[::stride], rolling[::stride]))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{colours[field]}" stroke-width="1.7"/>')
        cx = x0+pw*(detail["centre_us"]-T_MIN)/(T_MAX-T_MIN)
        parts.append(f'<line x1="{cx:.1f}" y1="{y0}" x2="{cx:.1f}" y2="{y0+ph}" stroke="{colours[field]}" stroke-width="1.5" stroke-dasharray="7 5"/>')
    parts.extend([f'<line x1="{x0}" y1="{y0+ph}" x2="{x0+pw}" y2="{y0+ph}" class="axis"/>',
                  f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+ph}" class="axis"/>',
                  '<text x="415" y="525" class="small" text-anchor="middle">time after muon arrival (microseconds)</text>',
                  '<text x="68" y="330" class="small" text-anchor="middle" transform="rotate(-90 68 330)">9-bin rolling Pearson residual</text>'])
    for i, field in enumerate(base.HOLDOUT.values()):
        parts.append(f'<line x1="540" y1="{205+i*32}" x2="580" y2="{205+i*32}" stroke="{colours[field]}" stroke-width="4"/><text x="590" y="{210+i*32}" class="body">{field:g} G</text>')

    # Panel 2: half-integer family.
    parts.append('<text x="855" y="140" class="heading">Same-family half-integer landmarks</text>')
    bx0, by0, bw, bh = 950, 190, 555, 280
    ratios = landmarks.observed_expected_ratio.to_numpy(dtype=float)
    rmin = min(1.0, float(ratios.min())); rmax = max(1.0, float(ratios.max()))
    rpad = max((rmax-rmin)*0.2, 0.0005); rmin -= rpad; rmax += rpad
    zero_y = by0+bh*(rmax-1.0)/(rmax-rmin); parts.append(f'<line x1="{bx0}" y1="{zero_y:.1f}" x2="{bx0+bw}" y2="{zero_y:.1f}" stroke="#333842"/>')
    for tick in [rmin, 1.0, rmax]:
        py = by0+bh*(rmax-tick)/(rmax-rmin)
        parts.append(f'<line x1="{bx0-5}" y1="{py:.1f}" x2="{bx0}" y2="{py:.1f}" class="axis"/><text x="{bx0-10}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:.5f}</text>')
    slot = bw/len(landmarks)
    for i, row in enumerate(landmarks.itertuples()):
        centre = bx0+(i+0.5)*slot; y = by0+bh*(rmax-row.observed_expected_ratio)/(rmax-rmin)
        base_y = zero_y; top = min(y, base_y); height_bar = max(abs(base_y-y), 1.2)
        colour = "#d99226" if abs(row.turns-7.5)<1e-9 else "#aeb7c3"
        parts.extend([f'<rect x="{centre-slot*0.32:.1f}" y="{top:.1f}" width="{slot*0.64:.1f}" height="{height_bar:.1f}" fill="{colour}" stroke="#515a66"/>',
                      f'<text x="{centre:.1f}" y="{by0+bh+22}" class="small" text-anchor="middle">{row.turns:g}</text>'])
    parts.extend(['<text x="1195" y="520" class="small" text-anchor="middle">accumulated spin turns</text>',
                  '<text x="865" y="330" class="small" text-anchor="middle" transform="rotate(-90 865 330)">pooled observed / expected counts</text>'])

    # Panel 3: controls.
    parts.append('<text x="75" y="630" class="heading">Frozen timing controls</text>')
    families = ["integer", "quarter", "three_quarter", "field_permutation"]
    cvals = controls.observed_expected_ratio.to_numpy(dtype=float)
    cmin = min(float(cvals.min()), results["candidate_7p5"]["observed_expected_ratio"])
    cmax = max(float(cvals.max()), results["candidate_7p5"]["observed_expected_ratio"])
    cpad = max((cmax-cmin)*0.15, 0.0005); cmin -= cpad; cmax += cpad
    cx0, cy0, cw, ch = 110, 680, 610, 290
    for tick in [cmin, (cmin+cmax)/2.0, cmax]:
        py = cy0+ch*(cmax-tick)/(cmax-cmin)
        parts.append(f'<line x1="{cx0-5}" y1="{py:.1f}" x2="{cx0}" y2="{py:.1f}" class="axis"/><text x="{cx0-10}" y="{py+4:.1f}" class="small" text-anchor="end">{tick:.5f}</text>')
    for i, family in enumerate(families):
        values = controls.loc[controls.control_family == family, "observed_expected_ratio"].to_numpy()
        for j, value in enumerate(values):
            px = cx0+(i+0.5)*cw/len(families)+(j-(len(values)-1)/2)*min(12, cw/len(families)/max(len(values),1)*0.8)
            py = cy0+ch*(cmax-value)/(cmax-cmin)
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="#73859a" opacity="0.82"/>')
        parts.append(f'<text x="{cx0+(i+0.5)*cw/len(families):.1f}" y="{cy0+ch+22}" class="small" text-anchor="middle">{family.replace("three_quarter","3/4").replace("field_permutation","field perm.")}</text>')
    cand_y = cy0+ch*(cmax-results["candidate_7p5"]["observed_expected_ratio"])/(cmax-cmin)
    p975_y = cy0+ch*(cmax-results["control_97_5_ratio"])/(cmax-cmin)
    parts.extend([f'<line x1="{cx0}" y1="{cand_y:.1f}" x2="{cx0+cw}" y2="{cand_y:.1f}" stroke="#d99226" stroke-width="2"/>',
                  f'<line x1="{cx0}" y1="{p975_y:.1f}" x2="{cx0+cw}" y2="{p975_y:.1f}" stroke="#333842" stroke-dasharray="7 5"/>',
                  '<text x="415" y="1015" class="small" text-anchor="middle">control family (equal-width timing windows)</text>',
                  '<text x="68" y="825" class="small" text-anchor="middle" transform="rotate(-90 68 825)">pooled observed / expected counts</text>'])

    # Panel 4: gates.
    parts.append('<text x="855" y="630" class="heading">Frozen gates</text>')
    gate_lines = [("7.5 pooled ratio is above 1", results["gates"]["candidate_ratio_above_one"]),
                  ("7.5 beats every other half-integer", results["gates"]["beats_other_half_integers"]),
                  ("7.5 beats control 97.5th percentile", results["gates"]["beats_control_97_5"]),
                  ("Local residual is positive in every field", results["gates"]["positive_each_field"]),
                  ("Detector-bootstrap lower excess is above zero", results["gates"]["bootstrap_excess_lower_above_zero"])]
    for i, (label, passed) in enumerate(gate_lines):
        y = 688+i*54; colour = "#1f7a55" if passed else "#a33b3b"
        parts.append(f'<text x="865" y="{y}" class="body">{label}</text><text x="1515" y="{y}" class="body" text-anchor="end" fill="{colour}" font-weight="700">{"PASS" if passed else "FAIL"}</text>')
    ci = results["detector_bootstrap_95_excess_ratio"]
    parts.extend([f'<rect x="860" y="930" width="650" height="85" rx="8" fill="#f0f3f7" stroke="#c8ced8"/>',
                  f'<text x="880" y="958" class="body">7.5 ratio {results["candidate_7p5"]["observed_expected_ratio"]:.6f}; excess {100*results["candidate_7p5"]["excess_ratio"]:.4f}%</text>',
                  f'<text x="880" y="983" class="body">detector-bootstrap excess 95% [{100*ci[0]:.4f}%, {100*ci[1]:.4f}%]</text>',
                  f'<text x="880" y="1008" class="body" font-weight="700">Verdict: {results["status"]}</text>',
                  '<text x="800" y="1090" class="small" text-anchor="middle">Charged-daughter counts timestamp population decay; this archive does not observe either neutrino or an individual deterministic lifetime.</text>',
                  '</svg>'])
    FIGURE.write_text("".join(parts), encoding="utf-8")


def main():
    source = json.loads(T382_RESULTS.read_text(encoding="utf-8"))
    tau = float(source["parent"]["tau_us"])
    gamma = float(source["child"]["gamma_mhz_per_g"])
    phi0 = float(source["child"]["phi0_rad"])
    phi_cycles = phi0 / (2.0 * np.pi)
    records = {run: base.load_run(run, field, "holdout") for run, field in base.HOLDOUT.items()}
    fits = {run: fit_parent_series(record, tau) for run, record in records.items()}

    timing = {run: field for run, field in base.HOLDOUT.items()}
    candidate = score_mapping(records, fits, 7.5, timing, gamma, phi_cycles)
    landmarks = candidate_landmarks(records, fits, gamma, phi_cycles)
    controls = control_scores(records, fits, gamma, phi_cycles)
    boot = bootstrap_candidate(records, tau, gamma, phi_cycles)
    landmarks.to_csv(LANDMARKS, index=False); controls.to_csv(CONTROLS, index=False)
    boot.to_csv(BOOTSTRAP, index=False)
    pd.DataFrame(candidate["field_rows"]).to_csv(FIELDS, index=False)

    other_half = landmarks.loc[~np.isclose(landmarks.turns, 7.5), "observed_expected_ratio"]
    control_975 = float(np.quantile(controls.observed_expected_ratio, 0.975))
    boot_ci = [float(np.quantile(boot.excess_ratio, 0.025)), float(np.quantile(boot.excess_ratio, 0.975))]
    gates = {
        "candidate_ratio_above_one": candidate["observed_expected_ratio"] > 1.0,
        "beats_other_half_integers": candidate["observed_expected_ratio"] > float(other_half.max()),
        "beats_control_97_5": candidate["observed_expected_ratio"] > control_975,
        "positive_each_field": all(row["mean_pearson_residual"] > 0 for row in candidate["field_rows"]),
        "bootstrap_excess_lower_above_zero": boot_ci[0] > 0,
    }
    gates["primary_pass"] = all(gates.values())
    status = "SUPPORTED" if gates["primary_pass"] else "NOT_SUPPORTED"

    results = {
        "test": "T390 7.5-spin population release",
        "status": status,
        "source": {"doi": "10.5286/ISIS.E.RB1620201", "medium": "300 K silver",
                   "instrument": "ISIS EMU", "observed": "aggregate charged-daughter histograms"},
        "frozen_parameters": {"tau_us": tau, "gamma_mhz_per_g": gamma, "phi0_rad": phi0,
                              "window_half_turns": WINDOW_HALF_TURNS,
                              "analysis_time_us": [T_MIN, T_MAX]},
        "candidate_7p5": candidate,
        "other_half_integer_max_ratio": float(other_half.max()),
        "candidate_rank_among_half_integers_descending": int(
            landmarks.observed_expected_ratio.rank(method="min", ascending=False)[np.isclose(landmarks.turns, 7.5)].iloc[0]),
        "control_97_5_ratio": control_975,
        "detector_bootstrap_95_excess_ratio": boot_ci,
        "gates": gates,
        "claim_boundary": "Population-level charged-daughter timing only. Neutrinos and individual muons are not directly observed.",
        "protocol_sha256": sha256(PROTOCOL),
        "source_hashes": {run: record["sha256"] for run, record in records.items()},
        "artifacts": {"half_integer_landmarks": str(LANDMARKS), "control_scores": str(CONTROLS),
                      "field_details": str(FIELDS), "detector_bootstrap": str(BOOTSTRAP),
                      "figure": str(FIGURE), "report": str(REPORT)},
    }
    RESULTS.write_text(json.dumps(results, indent=2), encoding="utf-8")
    make_figure(fits, landmarks, controls, results)

    field_frame = pd.DataFrame(candidate["field_rows"])[
        ["run", "field_g", "centre_us", "half_width_us", "observed_expected_ratio", "mean_pearson_residual"]
    ]
    headers = list(field_frame.columns)
    field_table = "| " + " | ".join(headers) + " |\n| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in field_frame.itertuples(index=False, name=None):
        field_table += "| " + " | ".join(f"{value:.6g}" if isinstance(value, (float, np.floating)) else str(value) for value in row) + " |\n"
    REPORT.write_text(
        "# T390 — 7.5-spin population-release result\n\n"
        f"**{status}.** The primary claim requires all five frozen gates.\n\n"
        "## Field-specific 7.5-turn windows\n\n" + field_table + "\n\n"
        f"Pooled observed/expected ratio: `{candidate['observed_expected_ratio']:.8f}`; "
        f"rank among half-integer landmarks: `{results['candidate_rank_among_half_integers_descending']}` "
        f"of `{len(landmarks)}`. Control 97.5th percentile: `{control_975:.8f}`.\n\n"
        f"Detector-bootstrap excess 95% interval: `[{boot_ci[0]:.8f}, {boot_ci[1]:.8f}]`.\n\n"
        "## Boundary\n\n" + results["claim_boundary"] + "\n",
        encoding="utf-8")
    print(json.dumps({"status": status, "candidate_ratio": candidate["observed_expected_ratio"],
                      "rank": results["candidate_rank_among_half_integers_descending"],
                      "control_97_5": control_975, "bootstrap_ci": boot_ci, "gates": gates}, indent=2))


if __name__ == "__main__":
    main()
