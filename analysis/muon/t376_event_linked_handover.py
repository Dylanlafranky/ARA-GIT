#!/usr/bin/env python3
"""T376: frozen event-linked muon handover test.

Uses only the two ends of the *initial* solid-scintillator pulse to predict the
later visible daughter time.  Delayed-pulse fields are outcomes only.
"""

from __future__ import annotations

import bisect
import csv
import hashlib
import html
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "quarknet" / "t376"
OUT = ROOT / "T376_event_linked"
PROTOCOL = ROOT / "T376_EVENT_LINKED_MUON_HANDOVER_PROTOCOL_2026-08-13.md"

TRAIN_FILES = [
    "6234.2017.1221.0.wd",
    "6234.2017.1224.0.wd",
    "6234.2018.0104.0.wd",
    "6234.2018.0115.0.wd",
]
HOLDOUT_FILES = [
    "6234.2018.0201.0.wd",
    "6234.2018.0207.0.wd",
    "6234.2018.0219.0.wd",
    "6234.2018.0220.0.wd",
]
LANDMARKS = [(0.50, "direct child"), (0.75, "quarter below ridge"),
             (0.25, "reversed flow"), (1.25, "liquid comparison")]
HALF_WIDTH = 0.125
MIN_DELAY_US = 0.300


def first_jd(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        next(f)
        for line in f:
            p = line.split()
            if len(p) >= 5:
                return int(p[1])
    raise ValueError(f"No event rows in {path}")


def file_spans(path: Path) -> dict[int, tuple[float, float]]:
    spans = {}
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            p = line.split()
            if len(p) < 5:
                continue
            jd, t = int(p[1]), float(p[2])
            if jd not in spans:
                spans[jd] = (t, t)
            else:
                spans[jd] = (min(spans[jd][0], t), max(spans[jd][1], t))
    return spans


def read_decay_rows(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            p = line.split()
            if len(p) < 8:
                continue
            rows.append({
                "channel": int(p[0].split(".")[-1]), "jd": int(p[1]),
                "delay_us": float(p[2]), "start": float(p[3]),
                "end": float(p[4]), "first_tot": float(p[5]),
                "second_tot": float(p[6]), "candidate_n": int(p[7]),
            })
    return rows


def cluster_candidates(rows: list[dict], tolerance_s: float = 250e-9) -> list[dict]:
    """Collapse channel-level rows into one physical initial-pulse event."""
    out = []
    for jd in sorted({r["jd"] for r in rows}):
        rr = sorted((r for r in rows if r["jd"] == jd), key=lambda x: (x["start"], x["end"]))
        cur = []
        anchor = None
        for r in rr:
            if anchor is None or r["start"] - anchor <= tolerance_s:
                cur.append(r)
                anchor = r["start"] if anchor is None else anchor
            else:
                best = min(cur, key=lambda x: x["end"])
                out.append({"jd": jd, "start": min(x["start"] for x in cur),
                            "end": best["end"], "delay_us": best["delay_us"]})
                cur, anchor = [r], r["start"]
        if cur:
            best = min(cur, key=lambda x: x["end"])
            out.append({"jd": jd, "start": min(x["start"] for x in cur),
                        "end": best["end"], "delay_us": best["delay_us"]})
    return out


def attach_initial_poles(path: Path, events: list[dict], tolerance_s: float = 250e-9) -> None:
    by_jd = defaultdict(list)
    for e in events:
        e["hits"] = {}
        by_jd[e["jd"]].append(e)
    for jd in by_jd:
        by_jd[jd].sort(key=lambda x: x["start"])
    starts_by_jd = {jd: [e["start"] for e in ev] for jd, ev in by_jd.items()}
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if not line or line.startswith("#"):
                continue
            p = line.split()
            if len(p) < 5:
                continue
            channel, jd = int(p[0].split(".")[-1]), int(p[1])
            if channel not in (1, 2):
                continue
            if jd not in by_jd:
                continue
            t, tot = float(p[2]), float(p[4])
            starts = starts_by_jd[jd]
            jd_events = by_jd[jd]
            i = bisect.bisect_left(starts, t)
            candidates = [j for j in (i - 1, i) if 0 <= j < len(starts)]
            if not candidates:
                continue
            j = min(candidates, key=lambda k: abs(starts[k] - t))
            dt = abs(starts[j] - t)
            if dt <= tolerance_s:
                old = jd_events[j]["hits"].get(channel)
                if old is None or dt < old[0]:
                    jd_events[j]["hits"][channel] = (dt, tot)
    for e in events:
        if 1 in e["hits"] and 2 in e["hits"]:
            e["q1"], e["q2"] = e["hits"][1][1], e["hits"][2][1]


def load_events() -> tuple[list[dict], dict]:
    rows = read_decay_rows(DATA / "lifetimeOut")
    raw_clusters = cluster_candidates(rows)
    by_jd = defaultdict(list)
    for e in raw_clusters:
        by_jd[e["jd"]].append(e)
    infos = []
    for split, names in (("train", TRAIN_FILES), ("holdout", HOLDOUT_FILES)):
        for name in names:
            path = DATA / name
            infos.append({"file": name, "split": split, "path": path,
                          "spans": file_spans(path)})
    # Assign by both Julian day and within-day acquisition span. This matters
    # when one short run and the next full run share a Julian-day label.
    assigned = defaultdict(list)
    for jd, evs in by_jd.items():
        candidates = [i for i in infos if jd in i["spans"]]
        for e in evs:
            valid = [i for i in candidates if i["spans"][jd][0] - 1e-12 <= e["start"] <= i["spans"][jd][1] + 1e-12]
            if len(valid) == 1:
                info = valid[0]
            elif valid:
                info = min(valid, key=lambda i: min(abs(e["start"]-i["spans"][jd][0]), abs(e["start"]-i["spans"][jd][1])))
            else:
                continue
            e.update({"file": info["file"], "split": info["split"]})
            assigned[info["file"]].append(e)
    for info in infos:
        attach_initial_poles(info["path"], assigned[info["file"]])
    usable = []
    for evs in assigned.values():
        for e in evs:
            if "q1" not in e or e["delay_us"] < MIN_DELAY_US or e["delay_us"] > 20:
                continue
            q1, q2 = e["q1"], e["q2"]
            x = 2 * q2 / (q1 + q2)
            e.update({"Q": q1 + q2, "x_mu": x, "s": x - 1, "a": abs(x - 1)})
            usable.append(e)
    quality = {
        "raw_channel_rows": len(rows), "clustered_visible_candidates": len(raw_clusters),
        "usable_two_pole_events": len(usable),
        "usable_fraction": len(usable) / max(1, len(raw_clusters)),
        "by_file": {name: sum(e["file"] == name for e in usable)
                    for name in TRAIN_FILES + HOLDOUT_FILES},
    }
    return usable, quality


def design(events: list[dict], kind: str, stats: dict | None = None):
    logq = np.log(np.array([e["Q"] for e in events], float))
    s = np.array([e["s"] for e in events], float)
    a = np.array([e["a"] for e in events], float)
    if stats is None:
        stats = {"logq_mean": float(logq.mean()), "logq_sd": float(logq.std() or 1),
                 "s_sd": float(s.std() or 1), "a_mean": float(a.mean()),
                 "a_sd": float(a.std() or 1)}
    zq = (logq - stats["logq_mean"]) / stats["logq_sd"]
    zs = s / stats["s_sd"]
    za = (a - stats["a_mean"]) / stats["a_sd"]
    if kind == "M0": X = np.ones((len(events), 1))
    elif kind == "MQ": X = np.column_stack([np.ones(len(events)), zq])
    else: X = np.column_stack([np.ones(len(events)), zq, zs, za])
    return X, stats


def fit_exp_regression(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """MLE for exponential mean mu=exp(X beta), using Newton steps."""
    beta = np.zeros(X.shape[1])
    beta[0] = math.log(max(float(y.mean()), 1e-6))
    for _ in range(100):
        eta = np.clip(X @ beta, -12, 12)
        w = y * np.exp(-eta)
        grad = X.T @ (1 - w)
        hess = X.T @ (X * w[:, None]) + np.eye(X.shape[1]) * 1e-8
        step = np.linalg.solve(hess, grad)
        beta2 = beta - step
        if np.max(np.abs(step)) < 1e-10:
            beta = beta2
            break
        beta = beta2
    return beta


def exp_nll(X, y, beta):
    eta = np.clip(X @ beta, -12, 12)
    return eta + y * np.exp(-eta)


def rankdata(x):
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), float)
    i = 0
    while i < len(x):
        j = i + 1
        while j < len(x) and x[order[j]] == x[order[i]]: j += 1
        ranks[order[i:j]] = (i + j - 1) / 2 + 1
        i = j
    return ranks


def spearman(x, y):
    return float(np.corrcoef(rankdata(np.asarray(x)), rankdata(np.asarray(y)))[0, 1])


def bootstrap_run_delta(events, q_losses, ara_losses, seed=376, n=10000):
    rng = np.random.default_rng(seed)
    runs = sorted({e["file"] for e in events})
    by = {r: np.where(np.array([e["file"] for e in events]) == r)[0] for r in runs}
    vals = []
    for _ in range(n):
        picked = rng.choice(runs, len(runs), replace=True)
        ix = np.concatenate([by[r] for r in picked])
        vals.append(float(np.mean(q_losses[ix] - ara_losses[ix])))
    return np.quantile(vals, [0.025, 0.5, 0.975]).tolist()


def svg_bar(labels, vals, colors, title, ylabel, baseline=None,
            baseline_label=None, zoom=True, width=760, height=390):
    m = dict(l=92, r=24, t=62, b=98)
    w=width-m['l']-m['r']; h=height-m['t']-m['b']
    anchors=list(vals)+([baseline] if baseline is not None else [])
    if zoom:
        span=max(anchors)-min(anchors)
        pad=max(span*0.35, 0.0005 if max(anchors)>1.5 else 0.01)
        lo=min(anchors)-pad; hi=max(anchors)+pad
    else:
        lo=min([0]+anchors); hi=max([0]+anchors)
    if hi==lo: hi=lo+1
    y=lambda v:m['t']+h-(v-lo)/(hi-lo)*h
    bw=w/max(1,len(vals))*0.62
    parts=[f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title><rect width="100%" height="100%" fill="#10151d"/><text x="20" y="30" fill="#eef4ff" font-size="18" font-weight="700">{html.escape(title)}</text>']
    for tick in np.linspace(lo,hi,5):
        yy=y(float(tick)); fmt=f'{tick:.4f}' if abs(hi-lo)<0.1 else f'{tick:.2f}'
        parts += [f'<line x1="{m["l"]}" y1="{yy:.1f}" x2="{width-m["r"]}" y2="{yy:.1f}" stroke="#2d3949"/>',
                  f'<text x="{m["l"]-10}" y="{yy+4:.1f}" text-anchor="end" fill="#c2ccda" font-size="12">{fmt}</text>']
    parts += [f'<line x1="{m["l"]}" y1="{m["t"]+h}" x2="{width-m["r"]}" y2="{m["t"]+h}" stroke="#8a97a8"/>',
              f'<line x1="{m["l"]}" y1="{m["t"]}" x2="{m["l"]}" y2="{m["t"]+h}" stroke="#8a97a8"/>']
    if baseline is not None:
        label=baseline_label or f'reference = {baseline:g}'
        parts += [f'<line x1="{m["l"]}" y1="{y(baseline):.1f}" x2="{width-m["r"]}" y2="{y(baseline):.1f}" stroke="#f3b562" stroke-width="2" stroke-dasharray="6 5"/>',
                  f'<text x="{width-m["r"]-4}" y="{y(baseline)-7:.1f}" text-anchor="end" fill="#f3c77a" font-size="12">{html.escape(label)}</text>']
    for i,(lab,v,c) in enumerate(zip(labels,vals,colors)):
        cx=m['l']+(i+.5)*w/len(vals); yy=y(v); base=y(lo); hh=max(base-yy,1)
        parts += [f'<rect x="{cx-bw/2:.1f}" y="{yy:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{c}" rx="4"/>',
                  f'<text x="{cx:.1f}" y="{height-54}" text-anchor="middle" fill="#d8e1ed" font-size="13">{html.escape(lab)}</text>',
                  f'<text x="{cx:.1f}" y="{yy-7:.1f}" text-anchor="middle" fill="#ffffff" font-size="13">{v:.4f}</text>']
    parts += [f'<text transform="translate(20 {m["t"]+h/2}) rotate(-90)" text-anchor="middle" fill="#d0d8e5" font-size="12">{html.escape(ylabel)}</text>',
              f'<text x="{m["l"]+w/2}" y="{height-18}" text-anchor="middle" fill="#aebacc" font-size="12">bars are labelled with their exact held-out value</text></svg>']
    return ''.join(parts)


def svg_scatter(events, title, width=760, height=430, maxn=2200):
    rng=np.random.default_rng(376); use=events if len(events)<=maxn else [events[i] for i in rng.choice(len(events),maxn,replace=False)]
    m=dict(l=78,r=22,t=72,b=70); w=width-m['l']-m['r']; h=height-m['t']-m['b']
    X=np.array([e['x_mu'] for e in use]); Y=np.array([e['delay_us'] for e in use]); ymax=min(12,float(np.quantile(Y,.99)))
    sx=lambda x:m['l']+x/2*w; sy=lambda y:m['t']+h-min(y,ymax)/ymax*h
    parts=[f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}"><title>{html.escape(title)}</title><rect width="100%" height="100%" fill="#10151d"/><text x="20" y="30" fill="#eef4ff" font-size="18" font-weight="700">{html.escape(title)}</text>',
           f'<text x="20" y="50" fill="#aebacc" font-size="12">one blue dot = one displayed held-out muon; {len(use):,} sampled from {len(events):,}</text>']
    for xtick in np.arange(0,2.001,.25):
        xx=sx(float(xtick)); parts += [f'<line x1="{xx:.1f}" y1="{m["t"]}" x2="{xx:.1f}" y2="{m["t"]+h}" stroke="#263241"/>',
                                      f'<text x="{xx:.1f}" y="{m["t"]+h+20}" text-anchor="middle" fill="#c2ccda" font-size="11">{xtick:.2f}</text>']
    for ytick in np.linspace(0,ymax,7):
        yy=sy(float(ytick)); parts += [f'<line x1="{m["l"]}" y1="{yy:.1f}" x2="{m["l"]+w}" y2="{yy:.1f}" stroke="#263241"/>',
                                     f'<text x="{m["l"]-10}" y="{yy+4:.1f}" text-anchor="end" fill="#c2ccda" font-size="11">{ytick:.0f}</text>']
    landmark_names={0.25:'0.25 reverse',0.5:'0.50 child',0.75:'0.75 flow',1.25:'1.25 liquid'}
    for i,(lm,_) in enumerate(LANDMARKS):
        parts += [f'<line x1="{sx(lm):.1f}" y1="{m["t"]}" x2="{sx(lm):.1f}" y2="{m["t"]+h}" stroke="#f3b562" stroke-width="1.5" stroke-dasharray="5 5" opacity=".9"/>',
                  f'<text x="{sx(lm):.1f}" y="{m["t"]+13+(i%2)*14}" text-anchor="middle" fill="#f3c77a" font-size="10">{landmark_names[lm]}</text>']
    parts += [f'<line x1="{sx(1):.1f}" y1="{m["t"]}" x2="{sx(1):.1f}" y2="{m["t"]+h}" stroke="#65d6a3" stroke-width="2"/>',
              f'<text x="{sx(1)+5:.1f}" y="{m["t"]+h-8}" fill="#86e3b8" font-size="11">1.00 ridge: q1 = q2</text>']
    for e in use: parts += [f'<circle cx="{sx(e["x_mu"]):.1f}" cy="{sy(e["delay_us"]):.1f}" r="1.7" fill="#69aaf5" opacity=".28"/>']
    parts += [f'<line x1="{m["l"]}" y1="{m["t"]+h}" x2="{m["l"]+w}" y2="{m["t"]+h}" stroke="#8a97a8"/><line x1="{m["l"]}" y1="{m["t"]}" x2="{m["l"]}" y2="{m["t"]+h}" stroke="#8a97a8"/>',
              f'<text x="{m["l"]+w/2}" y="{height-18}" text-anchor="middle" fill="#d0d8e5">incoming ARA relation x_mu = 2q2 / (q1 + q2), full scale 0-2</text>',
              f'<text transform="translate(18 {m["t"]+h/2}) rotate(-90)" text-anchor="middle" fill="#d0d8e5">delay to visible daughter (microseconds)</text>',
              f'<text x="{width-m["r"]}" y="{m["t"]-8}" text-anchor="end" fill="#aebacc" font-size="10">delays at or above {ymax:.0f} microseconds shown at top edge</text></svg>']
    return ''.join(parts)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events, quality = load_events()
    train = [e for e in events if e["split"] == "train"]
    hold = [e for e in events if e["split"] == "holdout"]
    yt=np.array([e["delay_us"]-MIN_DELAY_US for e in train]); yh=np.array([e["delay_us"]-MIN_DELAY_US for e in hold])
    models={}; stats=None
    for kind in ("M0","MQ","MARA"):
        Xt, st=design(train,kind,stats); stats=st
        Xh,_=design(hold,kind,stats)
        beta=fit_exp_regression(Xt,yt); loss=exp_nll(Xh,yh,beta)
        models[kind]={"beta":beta.tolist(),"mean_holdout_nll":float(loss.mean()),"loss":loss,"pred_mean":np.exp(np.clip(Xh@beta,-12,12))}
    delta=models["MQ"]["loss"]-models["MARA"]["loss"]
    boot=bootstrap_run_delta(hold,models["MQ"]["loss"],models["MARA"]["loss"])
    tau=float(np.mean(yt)); xt=2*(1-np.exp(-yh/tau))
    landmark=[]
    for center,label in LANDMARKS:
        inside=np.abs(xt-center)<=HALF_WIDTH; p=float(inside.mean()); n=int(inside.sum()); N=len(inside)
        se=math.sqrt(max(p*(1-p)/max(N,1),0)); landmark.append({"center":center,"label":label,"n":n,"N":N,"fraction":p,"enrichment_vs_uniform":p/0.125,"ci95":[max(0,p-1.96*se),min(1,p+1.96*se)]})
    rho_s=spearman([e['s'] for e in hold],[e['delay_us'] for e in hold]);rho_a=spearman([e['a'] for e in hold],[e['delay_us'] for e in hold])
    result={"protocol_sha256":hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),"quality":quality,
            "n_train":len(train),"n_holdout":len(hold),"tau_cal_us_after_0.3":tau,
            "models":{k:{kk:vv for kk,vv in v.items() if kk not in ('loss','pred_mean')} for k,v in models.items()},
            "delta_nll_Q_minus_ARA":float(delta.mean()),"run_block_bootstrap_ci95":boot,
            "holdout_spearman_s":rho_s,"holdout_spearman_a":rho_a,"landmarks":landmark}
    (OUT/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (OUT/'events.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=['split','file','jd','start','delay_us','q1','q2','Q','x_mu','s','a']);w.writeheader();w.writerows({k:e[k] for k in w.fieldnames} for e in events)
    nlls=[models[k]['mean_holdout_nll'] for k in ('M0','MQ','MARA')]
    lmvals=[x['enrichment_vs_uniform'] for x in landmark]
    verdict_ind='SUPPORTED' if delta.mean()>0 and boot[0]>0 else ('WEAK/UNSTABLE' if delta.mean()>0 else 'NOT SUPPORTED')
    best=max(landmark,key=lambda z:z['enrichment_vs_uniform'])
    verdict_lm=f"{best['center']:.2f} ({best['label']}) is the largest fixed-window enrichment"
    report=f'''<!doctype html><html><head><meta charset="utf-8"><title>T376 event-linked muon handover</title><style>body{{margin:0;background:#0b0f15;color:#e8eef7;font:16px system-ui}}main{{max-width:1180px;margin:auto;padding:28px}}.hero,.card{{background:#131a24;border:1px solid #293547;border-radius:16px;padding:22px;margin:16px 0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(480px,1fr));gap:16px}}.big{{font-size:30px;font-weight:800}}.good{{color:#67d8a4}}.warn{{color:#f3b562}}code{{color:#8dc3ff}}table{{border-collapse:collapse;width:100%}}th,td{{padding:8px;border-bottom:1px solid #2a3544;text-align:left}}</style></head><body><main><section class="hero"><h1>T376 — event-linked muon handover</h1><div class="big">Individual advance information: <span class="{'good' if verdict_ind=='SUPPORTED' else 'warn'}">{verdict_ind}</span></div><p>Frozen protocol SHA-256: <code>{result['protocol_sha256']}</code></p><p>{len(train):,} calibration and {len(hold):,} untouched later visible-decay events; {len(HOLDOUT_FILES)} holdout runs.</p></section><section class="grid"><div class="card">{svg_bar(['memoryless','pulse size Q','ARA Q+s+a'],nlls,['#75869c','#83b3e6','#65d6a3'],'Prospective holdout score','mean exponential NLL (lower is better)')}</div><div class="card">{svg_bar([f'{z["center"]:.2f}' for z in landmark],lmvals,['#65d6a3','#f3b562','#d16d86','#8e86dc'],'Frozen release windows','held-out enrichment vs exponential',baseline=1)}</div><div class="card">{svg_scatter(hold,'Incoming ARA relation vs later daughter time')}</div><div class="card"><h2>Results in plain language</h2><p>The ARA relation changed held-out NLL by <b>{delta.mean():+.6f}</b> per visible decay relative to pulse size alone. Run-block 95% interval: <b>{boot[0]:+.6f} to {boot[2]:+.6f}</b>.</p><p>Direction correlation <code>s</code>: {rho_s:+.4f}; asymmetry correlation <code>a</code>: {rho_a:+.4f}.</p><p>Landmark result: <b>{html.escape(verdict_lm)}</b>. This population statement is separate from predicting one muon.</p><h3>Data quality</h3><p>{quality['usable_two_pole_events']:,} of {quality['clustered_visible_candidates']:,} clustered visible candidates retained both initial poles ({quality['usable_fraction']:.1%}).</p></div></section><section class="card"><h2>Frozen landmark table</h2><table><tr><th>x</th><th>Meaning</th><th>Holdout count</th><th>fraction</th><th>enrichment</th><th>95% interval</th></tr>{''.join(f'<tr><td>{z["center"]:.2f}</td><td>{z["label"]}</td><td>{z["n"]:,}/{z["N"]:,}</td><td>{z["fraction"]:.3%}</td><td>{z["enrichment_vs_uniform"]:.3f}×</td><td>{z["ci95"][0]:.3%}–{z["ci95"][1]:.3%}</td></tr>' for z in landmark)}</table></section></main></body></html>'''
    read_key='''<section class="card"><h2>How to read every chart</h2><div class="key"><div><b>q1 and q2</b><br>Initial pulse widths measured at the two ends of the upper solid scintillator.</div><div><b>x_mu — horizontal ARA coordinate</b><br><code>2q2 / (q1 + q2)</code> on the full 0–2 scale. <b>1.00</b> means q1=q2.</div><div><b>Daughter delay — vertical coordinate</b><br>Microseconds from the incoming muon to its later visible decay daughter.</div><div><b>Blue dots and vertical ribs</b><br>Each displayed dot is one held-out event. Repeated vertical positions mostly come from discrete pulse-width steps.</div></div><p><b>Gold dashed lines:</b> frozen ARA landmarks. <b>Green line:</b> the 1.00 ridge. In the score chart, lower NLL is better. In the enrichment chart, the dashed 1.000 reference is ordinary exponential expectation.</p></section>'''
    report=report.replace('</style>', '.key{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px}.key div{padding:10px 12px;background:#10151d;border-left:3px solid #65d6a3}</style>')
    report=report.replace('</section><section class="grid">', '</section>'+read_key+'<section class="grid">', 1)
    report=report.replace('held-out enrichment vs exponential', 'enrichment ratio (observed / exponential)')
    (OUT/'T376_EVENT_LINKED_MUON_HANDOVER.html').write_text(report,encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
