"""
Two refinements to the compass + amplitude vehicle:

1. CONTINUOUS TICK — replace binary direction × fixed step with continuous-magnitude step.
   step = tanh(predicted_Δ / step_mean) × step_mean  (bounded to ±step_mean × something)
   Or simpler: step = clip(predicted_Δ, -step_mean*φ, +step_mean*φ)
   Lets the wave "wiggle" by predicted magnitude when confident, less when uncertain.

2. LOG RUNG WEIGHTS — replace φ^(-|k-k_ref|) with 1/(1+log(|k-k_ref|+1)).
   Flatter falloff lets distant rungs contribute more, useful for long-horizon prediction.

Tests on ENSO monthly refit. Compare:
  V_BASELINE: current compass (binary tick, φ-rung weights)
  V_CONT:     continuous tick, φ-rung weights
  V_LOG:      binary tick, log-rung weights
  V_BOTH:     continuous tick + log-rung weights
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter

PHI = 1.6180339887498949
INV_PHI = 1.0 / PHI
INV_PHI3 = 1.0 / (PHI**3)
INV_PHI4 = 1.0 / (PHI**4)

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
SOI_PATH  = _resolve(r"F:\SystemFormulaFolder\SOI_NOAA\soi.data")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\compass_continuous_logweight_data.js")

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
nino = load_nino(); soi = load_soi()
def to_m(s):
    s=s.copy(); s.index=pd.to_datetime(s.index).to_period('M').to_timestamp()
    return s.groupby(s.index).first()
nino,soi = to_m(nino),to_m(soi)
common = nino.index.intersection(soi.index).sort_values()
NINO = nino.reindex(common).values.astype(float)
SOI = soi.reindex(common).values.astype(float)
DATES = common; N = len(NINO)

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    b, a = butter(order, [Wn_lo, Wn_hi], btype='bandpass')
    return lfilter(b, a, arr - np.mean(arr))

def read_amp_theta(bp_to_t):
    if len(bp_to_t) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp_to_t))
    amp = float(np.std(bp_to_t[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp_to_t[-1]; rate = bp_to_t[-1] - bp_to_t[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

RUNGS = [(k, PHI**k) for k in range(4, 14)]
N_RUNGS = len(RUNGS)
K_REF = 8
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)

# Two rung-weight schemes
RW_PHI = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RW_PHI = RW_PHI / np.sum(RW_PHI)
RW_LOG = np.array([1.0/(1.0 + np.log(abs(k - K_REF) + 1)) for k,_ in RUNGS])
RW_LOG = RW_LOG / np.sum(RW_LOG)

print(f"\nRung weights (k_ref={K_REF}):")
print(f"  {'k':>3}  {'φ-weight':>10}  {'log-weight':>11}")
for i, (k, _) in enumerate(RUNGS):
    print(f"  {k:>3}  {RW_PHI[i]:>10.4f}  {RW_LOG[i]:>11.4f}")

def amp_predict(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train, rung_weights):
    nino_rung_future = []; soi_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, _ = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        nino_rung_future.append(a_n * np.cos(new_th_n))
        a_f, th_f, _ = state[('SOI', ri)]
        soi_rung_future.append(a_f * np.cos(th_f + 2*np.pi*h/p))
    nino_rung_future = np.array(nino_rung_future)
    own_pred = float(np.dot(rung_weights, nino_rung_future))
    soi_norm = np.array(soi_rung_future) / soi_scale * nino_scale
    walker = -1.0 * 1.0 * soi_norm[K_REF_IDX] * rung_weights[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * rung_weights[ri]
    return mean_train + own_pred + walker + INV_PHI3 * last_residual

def run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train, step_mean, rung_weights, continuous=False):
    cur_pos = NINO[refit_t - 1]
    prev_amp = NINO[refit_t - 1]
    for tau in range(1, h + 1):
        amp = amp_predict(refit_t, tau, last_residual, state, soi_scale, nino_scale, mean_train, rung_weights)
        delta = amp - prev_amp
        if continuous:
            # Continuous tick (v2): soft tanh saturation — small δ → small step, big δ → step_mean
            # This lets the wave wiggle directionally with finer resolution when uncertain
            step = step_mean * np.tanh(delta / max(step_mean, 1e-9))
        else:
            # Binary tick: sign × fixed magnitude
            direction = 1 if delta > 0 else -1
            step = direction * min(abs(delta), step_mean * PHI)
        cur_pos += step
        prev_amp = amp
    return cur_pos

# ===== Rolling test (monthly refit) =====
HORIZONS = [3, 6, 12, 24]
MIN_TRAIN = 30 * 12
STEP = 1  # MONTHLY refit

print(f"\n  Monthly refit, horizons={HORIZONS}")

variants = {
    'BASELINE': dict(continuous=False, rung_weights=RW_PHI),
    'CONT': dict(continuous=True, rung_weights=RW_PHI),
    'LOG': dict(continuous=False, rung_weights=RW_LOG),
    'BOTH': dict(continuous=True, rung_weights=RW_LOG),
}

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

    for h in HORIZONS:
        if refit_t + h - 1 >= N: continue
        truth = NINO[refit_t + h - 1]
        for vname, cfg in variants.items():
            pred = run_compass(refit_t, h, last_residual, state, soi_scale, nino_scale, mean_train, step_mean,
                              cfg['rung_weights'], cfg['continuous'])
            results[vname][h].append((refit_t, pred, truth))

    if results['BASELINE'][HORIZONS[0]]:
        last = results['BASELINE'][HORIZONS[0]][-1]
        last_residual = float(last[2] - last[1])

print(f"  {time.time()-t_start:.1f}s")

print(f"\n========= CONTINUOUS TICK + LOG WEIGHTS RESULTS (monthly refit) =========")
clim = float(np.mean(NINO))
metrics_out = {}
for vname in ['BASELINE', 'CONT', 'LOG', 'BOTH']:
    print(f"\n--- {vname} ---")
    print(f"  {'horizon':>10}  {'corr':>7}  {'MAE':>7}  {'R²(clim)':>9}  {'R²(pers)':>9}  {'dir':>6}")
    metrics_out[vname] = {}
    for h in HORIZONS:
        recs = results[vname][h]
        if not recs: continue
        preds = np.array([r[1] for r in recs])
        truths = np.array([r[2] for r in recs])
        pers_preds = np.array([NINO[r[0]-1] for r in recs])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds - truths)))
        ss_res = np.sum((truths - preds)**2)
        ss_clim = np.sum((truths - clim)**2)
        ss_pers = np.sum((truths - pers_preds)**2)
        r2_clim = float(1 - ss_res/ss_clim) if ss_clim > 0 else 0.0
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        dir_acc = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
        print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {r2_clim:+.3f}    {r2_pers:+.3f}    {dir_acc*100:5.1f}%")
        metrics_out[vname][h] = dict(corr=corr, mae=mae, r2_clim=r2_clim, r2_pers=r2_pers, dir_acc=dir_acc, n=len(recs))

out = dict(method="Continuous tick + log rung weights (monthly refit)",
           variants=dict(BASELINE='binary tick + φ-rung weights',
                         CONT='continuous tick + φ-rung weights',
                         LOG='binary tick + log-rung weights',
                         BOTH='continuous tick + log-rung weights'),
           results=metrics_out)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.COMPASS_REFINE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
    f.write("window.COMPASS_REFINE = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
