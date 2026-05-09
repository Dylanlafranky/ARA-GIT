"""
Add camshaft phase-gate restriction on top of BOTH (tanh tick + log weights).

Past framework method: camshaft valve = 1/(1+ARA) restricts when each rung
contributes. Untapped in the current vehicle. Test if adding it improves
short-mid lead.

Per-rung gate restriction in compass forward:
  At each tick τ, each rung's contribution is multiplied by
    gate_k(τ) = 1 if cos(new_θ_k) > -valve_k else attenuation_factor
  In smooth form:
    gate_k(τ) = 0.5*(1 + tanh(slope × (cos(new_θ_k) + valve_k)))

Where valve_k = 1/(1+ARA_k) for that rung's measured ARA.
Engines (ARA≈φ): valve ≈ 0.38 — 38% of cycle is "active"
Consumers (ARA<1): valve > 0.5 — most of cycle is active
Harmonics (ARA=2): valve ≈ 0.33 — only 1/3 active

Test on ENSO monthly refit: variants
  V_BOTH:    tanh tick + log weights (current best)
  V_GATE:    + camshaft phase gate (smooth tanh)
  V_GATE_HARD: + hard binary phase gate
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI = 1.0/PHI; INV_PHI3 = 1.0/(PHI**3); INV_PHI4 = 1.0/(PHI**4)

def _resolve(p):
    pl = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return pl if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\compass_gate_restriction_data.js")

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
            parts=ln.split()
            if len(parts)<13: continue
            try: year=int(parts[0])
            except: continue
            if year<1900 or year>2100: continue
            for m in range(12):
                try: v=float(parts[1+m])
                except: continue
                if v<-90: continue
                rows.append((pd.Timestamp(year=year,month=m+1,day=1),v))
    return pd.Series(dict(rows)).sort_index()

print("Loading...")
nino=load_nino(); soi=load_soi()
def to_m(s): s=s.copy(); s.index=pd.to_datetime(s.index).to_period('M').to_timestamp(); return s.groupby(s.index).first()
nino,soi = to_m(nino),to_m(soi)
common = nino.index.intersection(soi.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
SOI = soi.reindex(common).values.astype(float)
N = len(NINO)

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n=len(arr); fc=1.0/period_units; nyq=0.5
    Wn_lo=max(1e-6,(1-bw)*fc/nyq); Wn_hi=min(0.999,(1+bw)*fc/nyq)
    if Wn_lo>=Wn_hi: return np.zeros(n)
    b,a=butter(order,[Wn_lo,Wn_hi],btype='bandpass')
    return lfilter(b,a, arr - np.mean(arr))

def read_amp_theta(bp):
    if len(bp)<2: return 0.0,0.0
    r=min(50,len(bp))
    amp=float(np.std(bp[-r:])*np.sqrt(2))+1e-9
    last=bp[-1]; rate=bp[-1]-bp[-2]
    ratio=max(-0.99,min(0.99,last/amp))
    return amp, np.arccos(ratio)*(-1 if rate>0 else 1)

def per_rung_ARA_causal(arr_train, period):
    bp = causal_bandpass(arr_train, period, bw=0.85)
    if len(bp) < 3*int(period): return 1.0
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2: return 1.0
    aras = []
    for i in range(len(peaks)-1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg)-1)))
        aras.append((1 - f_t) / f_t)
    if not aras: return 1.0
    return float(np.mean(np.clip(aras, 0.3, 3.0)))

RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)
RW_LOG = np.array([1.0/(1.0 + np.log(abs(k - K_REF) + 1)) for k,_ in RUNGS])
RW_LOG = RW_LOG / np.sum(RW_LOG)

def amp_predict(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train, gate_mode='NONE', valves=None):
    nino_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, _ = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        cos_val = np.cos(new_th_n)
        if gate_mode == 'SMOOTH':
            v = valves[ri]
            g = 0.5 * (1 + np.tanh(5.0 * (cos_val + (1-2*v))))  # active when cos > -(1-2v)
            cos_val = cos_val * g
        elif gate_mode == 'HARD':
            v = valves[ri]
            cos_val = cos_val if cos_val > -(1-2*v) else cos_val * 0.3
        nino_rung_future.append(a_n * cos_val)
    own_pred = float(np.dot(RW_LOG, np.array(nino_rung_future)))

    soi_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_f, th_f, _ = state[('SOI', ri)]
        soi_rung_future.append(a_f * np.cos(th_f + 2*np.pi*h/p))
    soi_norm = np.array(soi_rung_future) / soi_scale * nino_scale
    walker = -1.0 * 1.0 * soi_norm[K_REF_IDX] * RW_LOG[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * RW_LOG[ri]
    return mean_train + own_pred + walker + INV_PHI3 * last_residual

def run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train, step_mean, gate_mode, valves):
    cur_pos = NINO[refit_t-1]
    prev_amp = NINO[refit_t-1]
    for tau in range(1, h+1):
        amp = amp_predict(refit_t, tau, last_residual, state, soi_scale, nino_scale, mean_train, gate_mode, valves)
        delta = amp - prev_amp
        step = step_mean * np.tanh(delta / max(step_mean, 1e-9))  # CONT tick
        cur_pos += step
        prev_amp = amp
    return cur_pos

HORIZONS = [3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 1

print(f"\n  Monthly refit, gate restriction test on top of BOTH (tanh tick + log weights)")

variants = ['BOTH', 'GATE_SMOOTH', 'GATE_HARD']
results = {v: {h: [] for h in HORIZONS} for v in variants}
last_residual = 0.0

t_start = time.time()
for refit_t in range(MIN_TRAIN, N - max(HORIZONS), STEP):
    arr_train = NINO[:refit_t]
    mean_train = float(np.mean(arr_train))
    nino_scale = float(np.std(arr_train)) + 1e-9
    soi_scale = float(np.std(SOI[:refit_t])) + 1e-9
    step_mean = float(np.mean(np.abs(np.diff(arr_train))))

    bp = {nm: [causal_bandpass({'NINO':NINO,'SOI':SOI}[nm][:refit_t], p) for k,p in RUNGS] for nm in ['NINO','SOI']}
    state = {}
    for nm in ['NINO','SOI']:
        for ri, (k, p) in enumerate(RUNGS):
            a, th = read_amp_theta(bp[nm][ri])
            state[(nm, ri)] = (a, th, 1.0)

    # Compute per-rung valves from NINO ARA
    valves = []
    for k, p in RUNGS:
        ara_k = per_rung_ARA_causal(arr_train, p)
        valves.append(1.0 / (1.0 + ara_k))

    for h in HORIZONS:
        if refit_t+h-1 >= N: continue
        truth = NINO[refit_t+h-1]
        for vname, gate_mode in [('BOTH','NONE'), ('GATE_SMOOTH','SMOOTH'), ('GATE_HARD','HARD')]:
            pred = run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train, step_mean, gate_mode, valves)
            results[vname][h].append((refit_t, pred, truth))

    if results['BOTH'][HORIZONS[0]]:
        last = results['BOTH'][HORIZONS[0]][-1]
        last_residual = float(last[2] - last[1])

print(f"  {time.time()-t_start:.1f}s")

print("\n========= GATE RESTRICTION RESULTS =========")
clim = float(np.mean(NINO))
for vname in variants:
    print(f"\n--- {vname} ---")
    print(f"  {'horizon':>10}  {'corr':>7}  {'MAE':>7}  {'R²(pers)':>9}  {'dir':>6}")
    for h in HORIZONS:
        recs = results[vname][h]
        if not recs: continue
        preds = np.array([r[1] for r in recs])
        truths = np.array([r[2] for r in recs])
        pers_preds = np.array([NINO[r[0]-1] for r in recs])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds-truths)))
        ss_res = np.sum((truths-preds)**2); ss_pers = np.sum((truths-pers_preds)**2)
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        dir_acc = float(np.mean(np.sign(preds-pers_preds) == np.sign(truths-pers_preds)))
        print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {r2_pers:+.3f}    {dir_acc*100:5.1f}%")

out = dict(method="Camshaft phase-gate restriction on compass (tanh tick + log weights)",
           horizons=HORIZONS, results={v: {h: dict(n=len(results[v][h])) for h in HORIZONS} for v in variants})
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.GATE_RESTRICT = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
