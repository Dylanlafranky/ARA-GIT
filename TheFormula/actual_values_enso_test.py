"""
actual_values_enso_test.py

Port of the actual-values delta-integration architecture to ENSO:
  - Per-month indexing (NINO 3.4 monthly anomaly, no resampling)
  - No mean subtraction or addition
  - Per-rung state from most recent cycle only (peak-to-peak / 2)
  - Sum (not average) across rungs
  - Forward via closed-form delta integration:
      v(h) = v_now + Σ_rung amp × (cos(θ + 2π·h/p) − cos(θ))
  - SOI matched-rung partner at φ⁸ included as another summed contributor

Compare to the prior best vehicle (mean + averaged amp + cosine + weighted average).
"""
import os
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
# Repo root: parent dir if this script is in TheFormula/, else current dir
REPO_ROOT = _PARENT if os.path.basename(_HERE) == "TheFormula" else _HERE

PHI = 1.6180339887498949
INV_PHI3 = 1.0 / PHI**3

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", REPO_ROOT).replace("\\","/")
    return p_lin if os.path.isdir(REPO_ROOT) else p

NINO_PATH = _resolve(r"<repo>/Nino34\nino34.long.anom.csv")
SOI_PATH  = _resolve(r"<repo>/SOI_NOAA\soi.data")
OUT       = _resolve(r"<repo>/TheFormula\actual_values_enso_data.js")

print("Loading NINO + SOI...")
def load_nino():
    df = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
    df['date'] = pd.to_datetime(df['date'].str.strip())
    df = df[df['val'] > -90].copy()
    return df.set_index('date')['val'].astype(float)

def load_soi():
    rows=[]
    with open(SOI_PATH) as f:
        next(f)
        for ln in f:
            parts = ln.split()
            if len(parts) < 13: continue
            try: y = int(parts[0])
            except: continue
            if y < 1900 or y > 2100: continue
            for m in range(12):
                try: v = float(parts[1+m])
                except: continue
                if v < -90: continue
                rows.append((pd.Timestamp(year=y, month=m+1, day=1), v))
    return pd.Series(dict(rows)).sort_index()

def to_monthly(s):
    s = s.copy(); s.index = pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()

nino = to_monthly(load_nino()); soi = to_monthly(load_soi())
common = nino.index.intersection(soi.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
SOI  = soi.reindex(common).values.astype(float)
DATES = common
N = len(NINO)
print(f"  N={N} months ({DATES[0].date()} to {DATES[-1].date()})")

def causal_bandpass(arr, period_months, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_months; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

def measure_state(bp, period_months):
    p_int = max(2, int(period_months))
    if len(bp) < 2 * p_int + 5: return None
    last_cycle = bp[-p_int:]
    amp = float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)
    if amp < 1e-9: return None
    v_now = float(bp[-1]); v_prev = float(bp[-2])
    norm = max(amp, 1e-9)
    ratio = max(-0.99, min(0.99, v_now / norm))
    th = np.arccos(ratio) * (-1 if (v_now - v_prev) > 0 else 1)
    return dict(amp=amp, theta=float(th), period=float(period_months))

# φ-rungs in MONTH units
RUNGS_K = list(range(3, 13))
RUNGS = [(k, PHI**k) for k in RUNGS_K]
K_REF = 8

def states_at_anchor(arr, t_anchor):
    states = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr[:t_anchor], p)
        st = measure_state(bp, p)
        if st is None: continue
        st['k'] = k
        states.append(st)
    return states

def project_actual(t_anchor, h):
    """Actual-values architecture for ENSO:
    v(h) = v_now + Σ_rung amp × (cos(θ + 2π·h/p) − cos(θ))
    SOI partner contributes its own state at matched rung (anti-phase)."""
    v_now = float(NINO[t_anchor - 1])
    nino_states = states_at_anchor(NINO, t_anchor)
    soi_states  = states_at_anchor(SOI,  t_anchor)
    if not nino_states: return v_now

    # NINO own delta
    delta = 0.0
    for s in nino_states:
        delta += s['amp'] * (np.cos(s['theta'] + 2*np.pi*h/s['period']) - np.cos(s['theta']))

    # SOI matched-rung partner at K_REF, anti-phase, scaled to NINO units
    soi_at_ref = next((s for s in soi_states if s['k'] == K_REF), None)
    if soi_at_ref is not None:
        # rescale SOI's amplitude to NINO units by ratio of training stds
        soi_train_std = float(np.std(SOI[:t_anchor])) + 1e-9
        nino_train_std = float(np.std(NINO[:t_anchor])) + 1e-9
        scale = nino_train_std / soi_train_std
        soi_delta = soi_at_ref['amp'] * (np.cos(soi_at_ref['theta'] + 2*np.pi*h/soi_at_ref['period']) - np.cos(soi_at_ref['theta']))
        # anti-phase coupling: subtract SOI's delta (mirrors NINO's behaviour)
        delta += -1 * soi_delta * scale * 0.5   # 0.5 weight = matched-pair coupling

    return v_now + delta

# === OLD baseline for comparison ===
def amp_std50(bp):
    n_recent = min(50, len(bp))
    return float(np.std(bp[-n_recent:]) * np.sqrt(2)) + 1e-9

def project_old(t_anchor, h):
    arr = NINO[:t_anchor]
    mean_t = float(np.mean(arr))
    pinned = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr, p)
        a = amp_std50(bp)
        last = bp[-1]; rate = bp[-1] - bp[-2]
        ratio = max(-0.99, min(0.99, last/a))
        th = np.arccos(ratio) * (-1 if rate > 0 else 1)
        pinned.append(dict(p=p, amp=a, theta=th, k=k))
    if not pinned: return mean_t
    rung_w = np.array([PHI**(-abs(s['k'] - K_REF)) for s in pinned])
    rung_w = rung_w / rung_w.sum()
    contrib = 0.0
    for j, s in enumerate(pinned):
        new_th = s['theta'] + 2*np.pi*h/s['p']
        contrib += rung_w[j] * s['amp'] * np.cos(new_th)
    return mean_t + contrib

# === Sweep ===
HORIZONS = [1, 3, 6, 12, 24]
MIN_TRAIN = 30 * 12   # 30 years
STEP = 3   # quarterly refit
ANCHORS = list(range(MIN_TRAIN, N - max(HORIZONS), STEP))
print(f"\n{len(ANCHORS)} anchors from year 30 to end, every 3 months")

t0 = time.time()
results_old = {h: [] for h in HORIZONS}
results_act = {h: [] for h in HORIZONS}
for t_a in ANCHORS:
    for h in HORIZONS:
        if t_a + h - 1 >= N: continue
        truth = float(NINO[t_a + h - 1])
        results_old[h].append((t_a, project_old(t_a, h), truth))
        results_act[h].append((t_a, project_actual(t_a, h), truth))
print(f"  ran in {time.time()-t0:.1f}s")

print(f"\n{'horizon':>9}  {'method':>4}  {'corr':>7}  {'MAE':>6}  {'R2(pers)':>9}  {'dir':>6}  n")
out_metrics = {}
for h in HORIZONS:
    for label, recs in [('OLD', results_old[h]), ('ACT', results_act[h])]:
        if not recs: continue
        rec = np.array(recs)
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        pers = NINO[origins-1]
        c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds) > 1e-9 else 0
        mae = float(np.mean(np.abs(preds-truths)))
        r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
        d = float(np.mean(np.sign(preds-pers) == np.sign(truths-pers)))
        print(f"  {h:>3} mo    {label:>4}  {c:+.3f}    {mae:.3f}    {r2p:>+.3f}   {d*100:5.1f}%   {len(recs)}")
        out_metrics[f'h{h}_{label}'] = dict(corr=c, mae=mae, r2p=r2p, dir=d, n=int(len(recs)))

# Dense forward at one anchor for visualization
anchor_idx = next(i for i, d in enumerate(DATES) if d >= pd.Timestamp('2010-12-01'))
print(f"\nDense forward at anchor {DATES[anchor_idx-1].date()}...")
dense_h = list(range(1, 49))
dense_old = [project_old(anchor_idx, h) for h in dense_h]
dense_act = [project_actual(anchor_idx, h) for h in dense_h]
dense_truth = [float(NINO[anchor_idx + h - 1]) if anchor_idx + h - 1 < N else None for h in dense_h]
dense_dates = [DATES[anchor_idx + h - 1].strftime('%Y-%m-%d') if anchor_idx + h - 1 < N else None for h in dense_h]
hist_dates = [DATES[i].strftime('%Y-%m-%d') for i in range(max(0, anchor_idx-48), anchor_idx)]
hist_truth = [float(NINO[i]) for i in range(max(0, anchor_idx-48), anchor_idx)]

out = dict(metrics=out_metrics, anchor_date=DATES[anchor_idx-1].strftime('%Y-%m-%d'),
           dense=dict(dates=dense_dates, old=dense_old, act=dense_act, truth=dense_truth),
           history=dict(dates=hist_dates, truth=hist_truth))
with open(OUT, 'w') as f:
    f.write("window.ENSO_ACT = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
