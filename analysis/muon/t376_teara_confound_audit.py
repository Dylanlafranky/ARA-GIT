#!/usr/bin/env python3
"""T376 post-hoc TE-ARA coupling and confound audit.

This diagnostic does not alter the frozen T376 verdict.  It asks whether the
incoming two-end relation was materially distorted by total pulse strength,
run identity, gain imbalance, digitisation, or two-ended selection.
"""

from __future__ import annotations

import csv
import html
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "T376_event_linked" / "events.csv"
OUT = ROOT / "T376_teara_audit"


def read_events():
    rows = []
    with SOURCE.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            e = dict(r)
            for k in ("start", "delay_us", "q1", "q2", "Q", "x_mu", "s", "a"):
                e[k] = float(e[k])
            # TE-ARA decomposition.  Closure is forced by construction.
            e["A"] = 2.0 * e["q1"] / e["Q"]
            e["B"] = 2.0 * e["q2"] / e["Q"]
            e["C"] = e["A"] * e["B"]  # 1 at ridge; 0 at one-pole domination.
            rows.append(e)
    return rows


def ranks(x):
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    out = np.empty(len(x), float)
    i = 0
    while i < len(x):
        j = i + 1
        while j < len(x) and x[order[j]] == x[order[i]]:
            j += 1
        out[order[i:j]] = (i + j - 1) / 2 + 1
        i = j
    return out


def spearman(x, y):
    rx, ry = ranks(x), ranks(y)
    if np.std(rx) == 0 or np.std(ry) == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def quantile_rows(rows, key, n=4):
    vals = np.array([r[key] for r in rows], float)
    edges = np.quantile(vals, np.linspace(0, 1, n + 1))
    ans = []
    for i in range(n):
        lo, hi = edges[i], edges[i + 1]
        use = [r for r in rows if r[key] >= lo and (r[key] <= hi if i == n - 1 else r[key] < hi)]
        d = np.array([r["delay_us"] for r in use], float)
        ans.append({
            "group": i + 1, "lo": float(lo), "hi": float(hi), "n": len(use),
            "mean_delay_us": float(np.mean(d)), "median_delay_us": float(np.median(d)),
            "p_delay_lt_1us": float(np.mean(d < 1.0)),
        })
    return ans


def gain_correct(rows):
    by = defaultdict(list)
    for r in rows:
        by[r["file"]].append(r)
    factors = {}
    for run, rr in by.items():
        factors[run] = float(np.median([r["q1"] / r["q2"] for r in rr]))
        g = factors[run]
        for r in rr:
            q2c = g * r["q2"]
            r["B_corrected"] = 2 * q2c / (r["q1"] + q2c)
            r["C_corrected"] = r["B_corrected"] * (2 - r["B_corrected"])
    return factors


def run_summary(rows):
    ans = []
    for run in sorted({r["file"] for r in rows}):
        rr = [r for r in rows if r["file"] == run]
        ans.append({
            "run": run, "split": rr[0]["split"], "n": len(rr),
            "mean_B": float(np.mean([r["B"] for r in rr])),
            "mean_B_corrected": float(np.mean([r["B_corrected"] for r in rr])),
            "median_C": float(np.median([r["C"] for r in rr])),
            "mean_Q": float(np.mean([r["Q"] for r in rr])),
            "mean_delay_us": float(np.mean([r["delay_us"] for r in rr])),
            "rho_C_delay": spearman([r["C"] for r in rr], [r["delay_us"] for r in rr]),
            "rho_Q_delay": spearman([r["Q"] for r in rr], [r["delay_us"] for r in rr]),
        })
    return ans


def conditional_cells(rows):
    q_edges = np.quantile([r["Q"] for r in rows], [0, .25, .5, .75, 1])
    c_edges = np.quantile([r["C_corrected"] for r in rows], [0, .25, .5, .75, 1])
    cells = []
    for qi in range(4):
        for ci in range(4):
            use = [r for r in rows
                   if r["Q"] >= q_edges[qi]
                   and (r["Q"] <= q_edges[qi+1] if qi == 3 else r["Q"] < q_edges[qi+1])
                   and r["C_corrected"] >= c_edges[ci]
                   and (r["C_corrected"] <= c_edges[ci+1] if ci == 3 else r["C_corrected"] < c_edges[ci+1])]
            cells.append({"pulse_quartile": qi+1, "coupling_quartile": ci+1,
                          "n": len(use),
                          "mean_delay_us": float(np.mean([r["delay_us"] for r in use])) if use else None,
                          "median_delay_us": float(np.median([r["delay_us"] for r in use])) if use else None})
    return cells


def fit_exp(X, y):
    beta = np.zeros(X.shape[1])
    beta[0] = math.log(max(float(np.mean(y)), 1e-6))
    for _ in range(100):
        eta = np.clip(X @ beta, -12, 12)
        wt = y * np.exp(-eta)
        grad = X.T @ (1 - wt)
        hess = X.T @ (X * wt[:, None]) + np.eye(X.shape[1]) * 1e-8
        step = np.linalg.solve(hess, grad)
        beta -= step
        if np.max(np.abs(step)) < 1e-10:
            break
    return beta


def exp_loss(X, y, beta):
    eta = np.clip(X @ beta, -12, 12)
    return eta + y * np.exp(-eta)


def leave_one_run_out(rows):
    # Centre incoming variables inside each acquisition run first.  This removes
    # between-run calibration offsets without consulting the decay outcome.
    for run in sorted({r["file"] for r in rows}):
        rr = [r for r in rows if r["file"] == run]
        lq = np.log([r["Q"] for r in rr])
        cc = np.array([r["C_corrected"] for r in rr])
        mq, sq = float(np.mean(lq)), float(np.std(lq) or 1)
        mc, sc = float(np.mean(cc)), float(np.std(cc) or 1)
        for r in rr:
            r["zq_run"] = (math.log(r["Q"]) - mq) / sq
            r["zc_run"] = (r["C_corrected"] - mc) / sc
    folds = []
    base_all, full_all = [], []
    for run in sorted({r["file"] for r in rows}):
        tr = [r for r in rows if r["file"] != run]
        te = [r for r in rows if r["file"] == run]
        ytr = np.array([r["delay_us"] - .3 for r in tr])
        yte = np.array([r["delay_us"] - .3 for r in te])
        xb_tr = np.array([[1, r["zq_run"]] for r in tr])
        xb_te = np.array([[1, r["zq_run"]] for r in te])
        xf_tr = np.array([[1, r["zq_run"], r["zc_run"], r["zq_run"]*r["zc_run"]] for r in tr])
        xf_te = np.array([[1, r["zq_run"], r["zc_run"], r["zq_run"]*r["zc_run"]] for r in te])
        lb = exp_loss(xb_te, yte, fit_exp(xb_tr, ytr))
        lf = exp_loss(xf_te, yte, fit_exp(xf_tr, ytr))
        base_all.extend(lb.tolist()); full_all.extend(lf.tolist())
        folds.append({"run": run, "n": len(te), "nll_pulse_only": float(np.mean(lb)),
                      "nll_with_teara": float(np.mean(lf)),
                      "delta_pulse_minus_teara": float(np.mean(lb-lf))})
    return {"folds": folds, "mean_nll_pulse_only": float(np.mean(base_all)),
            "mean_nll_with_teara": float(np.mean(full_all)),
            "delta_pulse_minus_teara": float(np.mean(np.array(base_all)-np.array(full_all)))}


def svg_bars(labels, series, title, ylabel, reference=None, width=920, height=430):
    # series: [(name, values, colour)]
    m = dict(l=86, r=25, t=72, b=105)
    w, h = width - m["l"] - m["r"], height - m["t"] - m["b"]
    flat = [v for _, vals, _ in series for v in vals]
    if reference is not None:
        flat.append(reference)
    lo, hi = min(flat), max(flat)
    pad = max((hi - lo) * .18, .005)
    lo, hi = lo - pad, hi + pad
    sy = lambda v: m["t"] + h - (v - lo) / (hi - lo) * h
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">',
             f'<title>{html.escape(title)}</title><rect width="100%" height="100%" fill="#10151d"/>',
             f'<text x="20" y="30" fill="#eef4ff" font-size="19" font-weight="700">{html.escape(title)}</text>']
    for tick in np.linspace(lo, hi, 6):
        yy = sy(float(tick))
        parts += [f'<line x1="{m["l"]}" y1="{yy:.1f}" x2="{width-m["r"]}" y2="{yy:.1f}" stroke="#293645"/>',
                  f'<text x="{m["l"]-9}" y="{yy+4:.1f}" text-anchor="end" fill="#c5cfdd" font-size="11">{tick:.3f}</text>']
    if reference is not None:
        parts += [f'<line x1="{m["l"]}" y1="{sy(reference):.1f}" x2="{width-m["r"]}" y2="{sy(reference):.1f}" stroke="#65d6a3" stroke-width="2"/>',
                  f'<text x="{width-m["r"]-4}" y="{sy(reference)-7:.1f}" text-anchor="end" fill="#86e3b8" font-size="11">reference {reference:.3f}</text>']
    groupw = w / len(labels)
    bw = groupw * .72 / len(series)
    for j, (name, vals, colour) in enumerate(series):
        for i, v in enumerate(vals):
            x = m["l"] + i * groupw + groupw * .14 + j * bw
            base = sy(lo)
            parts += [f'<rect x="{x:.1f}" y="{sy(v):.1f}" width="{bw-3:.1f}" height="{max(base-sy(v),1):.1f}" fill="{colour}" rx="3"/>',
                      f'<text x="{x+(bw-3)/2:.1f}" y="{sy(v)-5:.1f}" text-anchor="middle" fill="#f3f6fb" font-size="9">{v:.3f}</text>']
    for i, lab in enumerate(labels):
        x = m["l"] + (i + .5) * groupw
        parts += [f'<text x="{x:.1f}" y="{m["t"]+h+20}" text-anchor="middle" fill="#d2dbe7" font-size="11">{html.escape(lab)}</text>']
    lx = m["l"]
    for name, _, colour in series:
        parts += [f'<rect x="{lx}" y="48" width="12" height="12" fill="{colour}"/><text x="{lx+17}" y="59" fill="#cbd5e2" font-size="11">{html.escape(name)}</text>']
        lx += 145
    parts += [f'<line x1="{m["l"]}" y1="{m["t"]+h}" x2="{width-m["r"]}" y2="{m["t"]+h}" stroke="#8794a5"/>',
              f'<line x1="{m["l"]}" y1="{m["t"]}" x2="{m["l"]}" y2="{m["t"]+h}" stroke="#8794a5"/>',
              f'<text transform="translate(18 {m["t"]+h/2}) rotate(-90)" text-anchor="middle" fill="#d0d8e5" font-size="12">{html.escape(ylabel)}</text></svg>']
    return "".join(parts)


def short_run(run):
    p = run.split(".")
    return f"{p[-4]}.{p[-3]}" if len(p) >= 5 else run


def main():
    OUT.mkdir(exist_ok=True)
    rows = read_events()
    factors = gain_correct(rows)
    hold = [r for r in rows if r["split"] == "holdout"]
    runs = run_summary(rows)

    closure_err = max(abs((r["A"] + r["B"]) - 2) for r in rows)
    ticked = np.mean([
        abs(r["q1"] / 1.25 - round(r["q1"] / 1.25)) < .011 and
        abs(r["q2"] / 1.25 - round(r["q2"] / 1.25)) < .011 for r in hold
    ])
    correlations = {
        "B_vs_delay": spearman([r["B"] for r in hold], [r["delay_us"] for r in hold]),
        "C_vs_delay": spearman([r["C"] for r in hold], [r["delay_us"] for r in hold]),
        "C_corrected_vs_delay": spearman([r["C_corrected"] for r in hold], [r["delay_us"] for r in hold]),
        "Q_vs_delay": spearman([r["Q"] for r in hold], [r["delay_us"] for r in hold]),
        "C_vs_Q": spearman([r["C"] for r in hold], [r["Q"] for r in hold]),
    }
    cq = quantile_rows(hold, "C")
    qq = quantile_rows(hold, "Q")
    cells = conditional_cells(hold)
    loro = leave_one_run_out(rows)
    result = {
        "evidence_class": "post-hoc confound diagnostic; frozen T376 verdict unchanged",
        "n_all": len(rows), "n_holdout": len(hold),
        "teara_definition": {"A": "2q1/Q", "B": "2q2/Q", "forced_closure": "A+B=2", "coupling": "C=A*B=1-(B-1)^2"},
        "max_forced_closure_error": closure_err,
        "holdout_tick_quantised_fraction": float(ticked),
        "holdout_mean_B": float(np.mean([r["B"] for r in hold])),
        "holdout_mean_B_corrected": float(np.mean([r["B_corrected"] for r in hold])),
        "holdout_median_C": float(np.median([r["C"] for r in hold])),
        "holdout_median_C_corrected": float(np.median([r["C_corrected"] for r in hold])),
        "correlations": correlations,
        "gain_factors_q2_by_run": factors,
        "coupling_quartiles": cq, "pulse_quartiles": qq,
        "pulse_by_corrected_coupling_cells": cells,
        "leave_one_run_out_posthoc": loro, "runs": runs,
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (OUT / "run_diagnostics.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=runs[0].keys()); w.writeheader(); w.writerows(runs)

    run_labels = [short_run(r["run"]) for r in runs]
    run_svg = svg_bars(run_labels, [
        ("raw B", [r["mean_B"] for r in runs], "#69aaf5"),
        ("gain-corrected B", [r["mean_B_corrected"] for r in runs], "#65d6a3"),
    ], "Detector-end balance by run", "mean B coordinate", reference=1.0)
    strata_svg = svg_bars(["Q1", "Q2", "Q3", "Q4"], [
        ("coupling C quartile", [r["mean_delay_us"] for r in cq], "#8e86dc"),
        ("pulse Q quartile", [r["mean_delay_us"] for r in qq], "#f3b562"),
    ], "Later daughter time across incoming strata", "mean daughter delay (microseconds)")
    corr_rows = "".join(f'<tr><td>{html.escape(k)}</td><td>{v:+.4f}</td></tr>' for k, v in correlations.items())
    q_rows = "".join(
        f'<tr><td>C Q{r["group"]}</td><td>{r["lo"]:.3f}–{r["hi"]:.3f}</td><td>{r["n"]:,}</td><td>{r["mean_delay_us"]:.3f}</td><td>{r["median_delay_us"]:.3f}</td></tr>'
        for r in cq
    ) + "".join(
        f'<tr><td>Pulse Q{r["group"]}</td><td>{r["lo"]:.2f}–{r["hi"]:.2f}</td><td>{r["n"]:,}</td><td>{r["mean_delay_us"]:.3f}</td><td>{r["median_delay_us"]:.3f}</td></tr>'
        for r in qq
    )
    cell_rows = "".join(
        f'<tr><td>Pulse Q{r["pulse_quartile"]}</td><td>Coupling Q{r["coupling_quartile"]}</td><td>{r["n"]:,}</td><td>{r["mean_delay_us"]:.3f}</td><td>{r["median_delay_us"]:.3f}</td></tr>'
        for r in cells
    )
    loro_rows = "".join(
        f'<tr><td>{html.escape(short_run(r["run"]))}</td><td>{r["n"]:,}</td><td>{r["nll_pulse_only"]:.6f}</td><td>{r["nll_with_teara"]:.6f}</td><td>{r["delta_pulse_minus_teara"]:+.6f}</td></tr>'
        for r in loro["folds"]
    )
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>T376 TE-ARA confound audit</title><style>body{{margin:0;background:#0b0f15;color:#e8eef7;font:16px system-ui}}main{{max-width:1180px;margin:auto;padding:28px}}section{{background:#131a24;border:1px solid #293547;border-radius:15px;padding:20px;margin:16px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(500px,1fr));gap:16px}}table{{border-collapse:collapse;width:100%}}th,td{{padding:8px;border-bottom:1px solid #2d3949;text-align:left}}code{{color:#8dc3ff}}.warn{{color:#f3b562}}.good{{color:#65d6a3}}</style></head><body><main><section><h1>T376 — TE-ARA coupling and confound audit</h1><p><b>Evidence class:</b> post-hoc diagnostic. The prospective T376 verdict remains unchanged.</p><p><code>A=2q1/Q</code>, <code>B=2q2/Q</code>, <code>A+B=2</code>. Empirical coupling strength is <code>C=AB</code>: 1 is equal two-end participation; 0 is one-end domination.</p><p class="warn"><b>Boundary:</b> because A and B are normalized from only q1 and q2, A+B=2 and “Other=0” are forced. This audit measures detector-end sharing, not the full muon identity's Other.</p></section><section><h2>Answer first</h2><p>The incoming event is strongly two-ended: median <code>C={result["holdout_median_C"]:.3f}</code>. But this mainly describes how the solid scintillator and its two sensors shared the flash. Coupling had only <code>ρ={correlations["C_vs_delay"]:+.4f}</code> association with later daughter time, and gain correction left it at <code>ρ={correlations["C_corrected_vs_delay"]:+.4f}</code>.</p><p class="warn">The strongest distortion is instrumental: {ticked:.1%} of held-out pulse pairs lie on the detector's discrete 1.25 ns grid. Run-dependent end imbalance also moves the apparent ARA position. These effects explain much of the ribs and skew, but they do not reveal a hidden individual decay clock.</p></section><section class="grid"><div>{run_svg}</div><div>{strata_svg}</div></section><section class="grid"><div><h2>Rank correlations</h2><table><tr><th>Relation</th><th>Spearman ρ</th></tr>{corr_rows}</table></div><div><h2>Quartile diagnostics</h2><table><tr><th>Incoming stratum</th><th>range</th><th>n</th><th>mean delay</th><th>median delay</th></tr>{q_rows}</table></div></section><section><h2>Pulse-strength × corrected-coupling cells</h2><p>This checks whether TE-ARA coupling matters only inside weak or strong incoming pulses rather than on average.</p><table><tr><th>Pulse stratum</th><th>Coupling stratum</th><th>n</th><th>mean delay</th><th>median delay</th></tr>{cell_rows}</table></section><section><h2>Leave-one-run-out timing test</h2><p>Incoming variables were centred within each run first. Positive delta would mean corrected TE-ARA coupling improved prediction beyond pulse strength. Overall delta: <b>{loro["delta_pulse_minus_teara"]:+.6f}</b> NLL/event.</p><table><tr><th>Left-out run</th><th>n</th><th>pulse-only NLL</th><th>with TE-ARA</th><th>pulse − TE-ARA</th></tr>{loro_rows}</table></section><section><h2>Variables capable of skewing T376</h2><ol><li><b>End-to-end gain and geometry:</b> moves the apparent ridge away from 1.00; corrected separately within each run above.</li><li><b>Total pulse Q:</b> mixes deposited energy, track length and detector response. It was the best of the tested prediction models, but only slightly.</li><li><b>Two-ended trigger requirement:</b> removes events where one end is too weak, artificially filling the middle and emptying the poles.</li><li><b>1.25 ns digitisation:</b> creates rational vertical ribs in x_mu.</li><li><b>Run identity:</b> calibration and geometry drift across days.</li><li><b>Visible-daughter conditioning:</b> this table excludes initial muons without a qualified visible daughter.</li><li><b>0.3–20 microsecond search window:</b> truncates the observed lifetime distribution.</li><li><b>Lower-counter veto and stopping geometry:</b> selects a restricted subset of muon paths.</li></ol></section></main></body></html>'''
    (OUT / "T376_TEARA_CONFOUND_AUDIT.html").write_text(doc, encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
