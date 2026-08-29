"""T411C source-qualified time-facing Irrationality Di-ARA test.

Uses only numpy/pandas/pdfplumber from the bundled workspace runtime.  The
local quadratic convolution is the interior Savitzky-Golay construction used
in T411B; edge values are padded but source qualification prevents the missing
tail from being interpreted as a physical phase.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pdfplumber

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
OUT = HERE / "results"
RAW = SOURCE / "ThinningData.txt"
SUPPLEMENT = SOURCE / "rsos252527_si_001.pdf"
PARAMS = HERE / "T411C_FROZEN_PARAMETERS.json"

ALPHA = 0.0709
G = 9.81
DEV = {"S1", "S3"}
HOLD = {"S2", "S4"}
SURFACE_TENSION = {"S1": 30.76e-3, "S2": 28.65e-3, "S3": 27.24e-3, "S4": 16.61e-3}
VISCOSITY = {"S1": (-18.381, 5340.0), "S2": (-17.522, 5706.0), "S3": (-21.827, 7619.5), "S4": (-2.7863, 1582.4)}
DENSITY = {"S1": (838.64, -0.00081978), "S2": (842.20, -0.0010956), "S3": (908.40, -0.0028823), "S4": (976.04, -0.0012792)}


def load_metadata() -> pd.DataFrame:
    rows = []
    with pdfplumber.open(SUPPLEMENT) as pdf:
        for page_index in range(3, 7):
            table = pdf.pages[page_index].extract_tables()[0]
            rows.extend(table[1:] if page_index == 3 else table)
    cols = ["Name", "Fluid", "D0_mm", "T_C", "v_aim_mm_s", "v_mm_s", "H0_D0", "tbrk_s", "px_per_mm"]
    m = pd.DataFrame(rows, columns=cols)
    if m.Name.isna().sum() == 1 and m.iloc[-1].Fluid == "S4":
        m.loc[m.index[-1], "Name"] = "250822 u"
    m.Name = m.Name.str.replace(" ", "", regex=False)
    for c in cols[2:]:
        m[c] = pd.to_numeric(m[c], errors="raise")
    if len(m) != 176 or m.Name.nunique() != 176:
        raise RuntimeError("Metadata parse failed")
    return m


def load_raw() -> pd.DataFrame:
    r = pd.read_csv(RAW)
    r.Name = r.Name.ffill().astype(str).str.replace(" ", "", regex=False)
    return r.loc[~((r.Time_s == 0) & (r.D_px == 0) & (r.D_mm == 0))].copy()


def fluid_properties(fluid: str, temp_c: float) -> tuple[float, float, float]:
    tk = temp_c + 273.15
    a, b = VISCOSITY[fluid]
    mu = float(np.exp(a + b / tk))
    rho0, expansion = DENSITY[fluid]
    rho = float(rho0 * (1 + expansion * (tk - 293.15)))
    return mu, rho, SURFACE_TENSION[fluid]


def odd_window(n: int, target: int) -> int:
    cap = max(11, int(np.floor(0.31 * n)))
    if cap % 2 == 0:
        cap -= 1
    w = max(11, target)
    if w % 2 == 0:
        w += 1
    return min(w, cap)


def local_quadratic(y: np.ndarray, window: int, dt: float) -> tuple[np.ndarray, np.ndarray]:
    half = window // 2
    x = np.arange(-half, half + 1, dtype=float)
    a = np.column_stack([np.ones(window), x, x * x])
    pinv = np.linalg.pinv(a)
    smooth_kernel = pinv[0]
    deriv_kernel = pinv[1] / dt
    padded = np.pad(y.astype(float), (half, half), mode="edge")
    smooth = np.convolve(padded, smooth_kernel[::-1], mode="valid")
    deriv = np.convolve(padded, deriv_kernel[::-1], mode="valid")
    return smooth, deriv


def rank_corr(a: np.ndarray, b: np.ndarray) -> float:
    ok = np.isfinite(a) & np.isfinite(b)
    if ok.sum() < 5:
        return float("nan")
    ar = pd.Series(a[ok]).rank(method="average").to_numpy(float)
    br = pd.Series(b[ok]).rank(method="average").to_numpy(float)
    return float(np.corrcoef(ar, br)[0, 1])


def persistent_cross(u: np.ndarray, x: np.ndarray, persistence: int = 5) -> float:
    for j in range(1, len(x)):
        if not (np.isfinite(x[j - 1]) and np.isfinite(x[j])):
            continue
        if x[j - 1] < 1 <= x[j]:
            tail = x[j:j + persistence]
            if len(tail) == persistence and np.all(np.isfinite(tail)) and np.all(tail >= 1):
                d = x[j] - x[j - 1]
                f = 0 if d == 0 else (1 - x[j - 1]) / d
                return float(u[j - 1] + f * (u[j] - u[j - 1]))
    return float("nan")


def analyse(group: pd.DataFrame, m: pd.Series) -> tuple[pd.DataFrame, dict]:
    g = group[np.isfinite(group.D_mm) & (group.D_px >= 5)].copy().sort_values("Time_s")
    tbrk = float(m.tbrk_s)
    coverage = float(g.Time_s.max() / tbrk) if len(g) else 0.0
    if len(g) < 40 or coverage < 0.90:
        return pd.DataFrame(), {"Name": m.Name, "fluid": m.Fluid, "D0_mm": float(m.D0_mm), "coverage": coverage, "excluded": True, "reason": "source_coverage"}
    fluid = str(m.Fluid)
    mu, rho, sigma = fluid_properties(fluid, float(m.T_C))
    d0 = float(m.D0_mm); h0 = d0 * float(m.H0_D0); v = float(m.v_mm_s)
    t = g.Time_s.to_numpy(float); d = g.D_mm.to_numpy(float); dt = float(np.median(np.diff(t)))
    r_cap = 2 * ALPHA * sigma / mu * 1000
    target = int(np.ceil((2 / float(m.px_per_mm)) / max(r_cap, 1e-12) / dt))
    window = odd_window(len(g), target)
    d_smooth, deriv = local_quadratic(d, window, dt)
    r_obs = -deriv
    d_mech = d0 * np.power(1 + v * t / h0, -0.75)
    r_mech = 0.75 * (v / h0) * d0 * np.power(1 + v * t / h0, -1.75)
    r_i = r_obs - r_mech
    u = t / tbrk
    valid = (u >= 0.05) & (r_mech >= 0) & (r_i >= 0) & (r_obs > 0)
    x = np.full(len(t), np.nan); x[valid] = 2 * r_i[valid] / r_obs[valid]
    cross_u = persistent_cross(u, x)
    k = int(np.nanargmin(np.abs(u - cross_u))) if np.isfinite(cross_u) else -1
    d0m = d0 / 1000; dm = d_smooth / 1000; hm = (h0 + v * t) / 1000
    bo0 = rho * G * (d0m / 2) ** 2 / sigma
    bol = rho * G * (dm / 2) ** 2 / sigma
    gh = rho * G * hm * dm / (2 * sigma)
    g["D_smooth_mm"] = d_smooth; g["u_breakup"] = u
    g["r_observed_mm_s"] = r_obs; g["r_mechanical_mm_s"] = r_mech
    g["r_unresolved_mm_s"] = r_i; g["x_rate_ara"] = x
    g["Bo_local"] = bol; g["G_height_proxy"] = gh
    g["fluid"] = fluid; g["D0_mm"] = d0; g["coverage"] = coverage
    sm = {
        "Name": str(m.Name), "fluid": fluid, "D0_mm": d0, "coverage": coverage,
        "n_reliable": int(len(g)), "window_ms": float(window * dt * 1000),
        "unmeasured_tail_ms": float((tbrk - t[-1]) * 1000), "cross_u": cross_u,
        "cross_t_s": float(t[k]) if k >= 0 else float("nan"),
        "rho_time_x": rank_corr(u, x), "Bo0": float(bo0),
        "Bo_cross": float(bol[k]) if k >= 0 else float("nan"),
        "G_height_cross": float(gh[k]) if k >= 0 else float("nan"),
        "capillary_rate_mm_s": float(r_cap),
        "late_unresolved_to_capillary": float(np.nanmedian(r_i[u >= .70]) / r_cap),
        "excluded": False, "reason": "",
    }
    return g, sm


def shift_control(series: pd.DataFrame, summary: pd.DataFrame, seed: int, reps: int = 1000) -> dict:
    obs = float(summary.rho_time_x.median())
    groups = [g.sort_values("Time_s") for _, g in series.groupby("Name")]
    rng = np.random.default_rng(seed); null = []
    for _ in range(reps):
        vals = []
        for g in groups:
            rm = g.r_mechanical_mm_s.to_numpy(float); ri = g.r_unresolved_mm_s.to_numpy(float)
            u = g.u_breakup.to_numpy(float); ris = np.roll(ri, int(rng.integers(1, len(g))))
            total = rm + ris; ok = (u >= .05) & (rm >= 0) & (ris >= 0) & (total > 0)
            if ok.sum() >= 5:
                vals.append(rank_corr(u[ok], 2 * ris[ok] / total[ok]))
        if vals: null.append(float(np.nanmedian(vals)))
    null = np.asarray(null)
    return {"observed_median_rho": obs, "null_median": float(np.median(null)), "null_q95": float(np.quantile(null,.95)), "p_ge_observed": float((1 + np.sum(null >= obs)) / (1 + len(null))), "reps": len(null)}


def report_html(series: pd.DataFrame, active: pd.DataFrame, excluded: pd.DataFrame, result: dict, mode: str) -> None:
    colors = {"S1":"#d95f02","S2":"#1b9e77","S3":"#7570b3","S4":"#e7298a"}
    def sx(v): return 70 + 560 * float(v)
    def sy(v): return 330 - 260 * float(v) / 2
    traj=[]
    for fluid in sorted(active.fluid.unique()):
        a=active[(active.fluid==fluid)&active.cross_u.notna()].sort_values('cross_u')
        if len(a):
            name=a.iloc[len(a)//2].Name; g=series[series.Name==name]
            pts=' '.join(f'{sx(u):.1f},{sy(x):.1f}' for u,x in zip(g.u_breakup,g.x_rate_ara) if np.isfinite(x))
            traj.append(f'<polyline points="{pts}" fill="none" stroke="{colors[fluid]}" stroke-width="2"/><text x="{80+120*len(traj)}" y="55" fill="{colors[fluid]}">{fluid}</text>')
    hist=[]
    bins=np.linspace(0,1,21)
    for j,fluid in enumerate(sorted(active.fluid.unique())):
        vals=active.loc[(active.fluid==fluid)&active.cross_u.notna(),'cross_u'].to_numpy(float)
        h,_=np.histogram(vals,bins); maxh=max(1,max(h) if len(h) else 1)
        for i,n in enumerate(h):
            x=720+i*28+j*5; height=230*n/maxh
            hist.append(f'<rect x="{x}" y="{330-height}" width="5" height="{height}" fill="{colors[fluid]}" opacity=".75"/>')
    scat=[]
    bmax=max(float(active.Bo0.max()),1e-9)
    for _,r in active[active.cross_u.notna()].iterrows():
        scat.append(f'<circle cx="{70+560*r.Bo0/bmax:.1f}" cy="{710-260*r.cross_u:.1f}" r="4" fill="{colors[r.fluid]}" opacity=".65"/>')
    cov=[]
    for j,(fluid,g) in enumerate(pd.concat([active,excluded]).groupby('fluid')):
        y=500+j*48
        med=float(g.coverage.median()); q10=float(g.coverage.quantile(.1))
        cov.append(f'<text x="720" y="{y}">{fluid}</text><line x1="790" y1="{y-5}" x2="{790+500*med}" y2="{y-5}" stroke="{colors[fluid]}" stroke-width="14"/><circle cx="{790+500*q10}" cy="{y-5}" r="5" fill="#111"/><text x="1310" y="{y}">median {med:.3f}; q10 {q10:.3f}</text>')
    title=f'T411C {mode}: time-facing current-rate ARA'
    rows=''.join(f'<tr><td>{k}</td><td>{v}</td></tr>' for k,v in result.items() if not isinstance(v,(dict,list)))
    html=f'''<!doctype html><meta charset="utf-8"><title>{title}</title><style>body{{font:15px system-ui;margin:24px;color:#18212b}}h1{{margin-bottom:4px}}.note{{max-width:1100px}}svg{{background:#fafbfc;border:1px solid #ccd3da}}table{{border-collapse:collapse;margin-top:18px}}td{{padding:6px 12px;border-bottom:1px solid #ddd}}td:first-child{{font-weight:700}}</style><h1>{title}</h1><p class="note">0 = mechanical-rate pole, 1 = equal-rate ridge, 2 = additional-rate pole. Breakup time is direct; the rate partition and handover are inferred. Only traces retaining at least 90% of the direct lifetime are scored.</p><svg width="1420" height="760" viewBox="0 0 1420 760"><text x="70" y="30" font-size="20" font-weight="700">Example source-qualified trajectories</text>{''.join(traj)}<line x1="70" y1="200" x2="630" y2="200" stroke="#222" stroke-dasharray="6 5"/><text x="75" y="194">ARA ridge 1.0</text><line x1="70" y1="330" x2="630" y2="330" stroke="#555"/><line x1="70" y1="70" x2="70" y2="330" stroke="#555"/><text x="300" y="355">u = t / direct breakup time</text><text x="715" y="30" font-size="20" font-weight="700">Handover distribution</text>{''.join(hist)}<line x1="720" y1="330" x2="1280" y2="330" stroke="#555"/><text x="900" y="355">inferred crossing u</text><text x="70" y="400" font-size="20" font-weight="700">Gravity rival: initial Bond number vs handover</text>{''.join(scat)}<line x1="70" y1="710" x2="630" y2="710" stroke="#555"/><line x1="70" y1="450" x2="70" y2="710" stroke="#555"/><text x="260" y="735">initial Bond number Bo₀</text><text x="715" y="400" font-size="20" font-weight="700">Source coverage (black dot = q10)</text>{''.join(cov)}<line x1="1240" y1="430" x2="1240" y2="690" stroke="#222" stroke-dasharray="5 5"/><text x="1210" y="420">0.90 gate</text></svg><h2>Numeric summary</h2><table>{rows}</table>'''
    (OUT/f'T411C_{mode.upper()}_REPORT.html').write_text(html,encoding='utf-8')


def run(mode: str) -> None:
    if mode == "holdout" and not PARAMS.exists():
        raise RuntimeError("Holdout locked: freeze T411C_FROZEN_PARAMETERS.json first")
    meta=load_metadata(); raw=load_raw(); fluids=DEV if mode=='development' else HOLD
    meta=meta[meta.Fluid.isin(fluids)]
    all_ts=[]; sms=[]
    for _,m in meta.iterrows():
        ts,sm=analyse(raw[raw.Name==m.Name],m); sms.append(sm)
        if len(ts): all_ts.append(ts)
    series=pd.concat(all_ts,ignore_index=True); summary=pd.DataFrame(sms); active=summary[~summary.excluded].copy()
    control=shift_control(series,active,41132026 if mode=='development' else 41132027)
    plate={str(k):float(v) for k,v in active.groupby('D0_mm').cross_u.median().items()}
    bo_rho=rank_corr(active.Bo0.to_numpy(float),active.cross_u.to_numpy(float))
    gh_rho=rank_corr(active.G_height_cross.to_numpy(float),active.cross_u.to_numpy(float))
    result={"mode":mode,"source_runs":len(summary),"qualified_runs":len(active),"crossings":int(active.cross_u.notna().sum()),"crossing_fraction":float(active.cross_u.notna().mean()),"median_cross_u":float(active.cross_u.median()),"q10_cross_u":float(active.cross_u.quantile(.1)),"q90_cross_u":float(active.cross_u.quantile(.9)),"median_rho_time_x":float(active.rho_time_x.median()),"median_window_ms":float(active.window_ms.median()),"median_source_coverage":float(active.coverage.median()),"plate_size_cross_medians":plate,"bo0_cross_spearman":bo_rho,"height_proxy_cross_spearman":gh_rho,"temporal_shift_control":control}
    OUT.mkdir(exist_ok=True)
    series.to_csv(OUT/f'T411C_{mode.upper()}_TIMESERIES.csv',index=False)
    summary.to_csv(OUT/f'T411C_{mode.upper()}_EVENT_SUMMARY.csv',index=False)
    (OUT/f'T411C_{mode.upper()}_RESULTS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    report_html(series,active,summary[summary.excluded],result,mode)
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--mode',choices=['development','holdout'],required=True)
    run(p.parse_args().mode)
