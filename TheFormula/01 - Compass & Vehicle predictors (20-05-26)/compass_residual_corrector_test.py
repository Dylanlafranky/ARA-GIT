"""
Compass with residual corrector — exploits the framework structure
hiding in the compass's own prediction errors.

Discovery (2026-05-02): compass residual has Hurst H=0.339 (mean-reverting),
lag-1 autocorr -0.527, residual ARA 0.483 (consumer-class). The errors
themselves are framework-structured.

Corrector: pred_corrected[t] = pred_compass[t] - γ × residual[t-1]
where γ is set by the empirical lag-1 autocorrelation OR a framework constant.

Test:
  V_baseline:   deterministic compass (no correction)
  V_corr_emp:   subtract γ_empirical × prev_residual (γ ≈ 0.527)
  V_corr_phi:   subtract 1/φ × prev_residual (γ ≈ 0.618, framework constant)

If correction helps, the residual structure was real signal. If it overcorrects,
we've gone too far.
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
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\compass_corrector_data.js")

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
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

def amp_predict(refit_t, h, last_residual_internal, state, soi_scale, nino_scale, mean_train):
    nino_rung_future = []; soi_rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a_n, th_n, _ = state[('NINO', ri)]
        new_th_n = th_n + 2*np.pi*h/p
        nino_rung_future.append(a_n * np.cos(new_th_n))
        a_f, th_f, _ = state[('SOI', ri)]
        soi_rung_future.append(a_f * np.cos(th_f + 2*np.pi*h/p))
    nino_rung_future = np.array(nino_rung_future)
    own_pred = float(np.dot(RUNG_WEIGHTS, nino_rung_future))
    soi_norm = np.array(soi_rung_future) / soi_scale * nino_scale
    walker = -1.0 * 1.0 * soi_norm[K_REF_IDX] * RUNG_WEIGHTS[K_REF_IDX] * 5
    for ri in range(N_RUNGS):
        if ri == K_REF_IDX: continue
        walker += -1.0 * (1.0/PHI**abs(RUNGS[ri][0]-K_REF)) * INV_PHI4 * soi_norm[ri] * RUNG_WEIGHTS[ri]
    return mean_train + own_pred + walker + INV_PHI3 * last_residual_internal

def run_compass(refit_t, horizon, last_residual_internal, state, soi_scale, nino_scale, mean_train, step_mean):
    cur_pos = NINO[refit_t - 1]
    prev_amp = NINO[refit_t - 1]
    for tau in range(1, horizon + 1):
        amp = amp_predict(refit_t, tau, last_residual_internal, state, soi_scale, nino_scale, mean_train)
        delta = amp - prev_amp
        direction = 1 if delta > 0 else -1
        cur_pos += direction * min(abs(delta), step_mean * PHI)
        prev_amp = amp
    return cur_pos

# ===== Rolling test with three corrector variants =====
HORIZONS = [1, 3, 6, 12]
MIN_TRAIN = 30 * 12
STEP = 12
GAMMA_EMP = 0.527  # empirical lag-1 autocorrelation
GAMMA_PHI = INV_PHI  # 1/φ ≈ 0.618 (framework constant)

print(f"\n  Rolling compass with residual corrector (γ_empirical={GAMMA_EMP}, γ_φ={GAMMA_PHI:.3f})")

results = {h: dict(baseline=[], corr_emp=[], corr_phi=[]) for h in HORIZONS}
prev_res = {h: 0.0 for h in HORIZONS}  # one previous residual per horizon
last_residual_internal = 0.0

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
        # Baseline compass
        base_pred = run_compass(refit_t, h, last_residual_internal, state, soi_scale, nino_scale, mean_train, step_mean)
        # Corrected predictions — lag-1 autocorr is NEGATIVE (-0.527),
        # so the predicted residual is -|γ| × prev_res, which we ADD to base_pred:
        # corrected = base_pred + (-|γ|) × prev_res = base_pred - |γ| × prev_res
        corr_emp = base_pred - GAMMA_EMP * prev_res[h]
        corr_phi = base_pred - GAMMA_PHI * prev_res[h]
        # Record
        results[h]['baseline'].append((refit_t, base_pred, truth))
        results[h]['corr_emp'].append((refit_t, corr_emp, truth))
        results[h]['corr_phi'].append((refit_t, corr_phi, truth))
        # Update previous residual (using the BASE compass's residual to avoid feedback amplification)
        prev_res[h] = float(truth - base_pred)

    if results[1]['baseline']:
        last_residual_internal = float(results[1]['baseline'][-1][2] - results[1]['baseline'][-1][1])

print(f"  {time.time()-t_start:.1f}s")

print(f"\n========= COMPASS RESIDUAL CORRECTOR RESULTS =========")
clim_pred = float(np.mean(NINO))
metrics_out = {}
for variant in ['baseline', 'corr_emp', 'corr_phi']:
    print(f"\n--- {variant} ---")
    print(f"  {'horizon':>10}  {'corr':>7}  {'MAE':>7}  {'R²(clim)':>9}  {'R²(pers)':>9}  {'dir':>6}")
    metrics_out[variant] = {}
    for h in HORIZONS:
        recs = results[h][variant]
        if not recs: continue
        preds = np.array([r[1] for r in recs])
        truths = np.array([r[2] for r in recs])
        pers_preds = np.array([NINO[r[0]-1] for r in recs])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds - truths)))
        ss_res = np.sum((truths - preds)**2)
        ss_clim = np.sum((truths - clim_pred)**2)
        ss_pers = np.sum((truths - pers_preds)**2)
        r2_clim = float(1 - ss_res/ss_clim) if ss_clim > 0 else 0.0
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        dir_acc = float(np.mean(np.sign(preds - pers_preds) == np.sign(truths - pers_preds)))
        print(f"  h={h:>2} mo  {corr:+.3f}  {mae:.3f}    {r2_clim:+.3f}    {r2_pers:+.3f}    {dir_acc*100:5.1f}%")
        metrics_out[variant][h] = dict(corr=corr, mae=mae, r2_clim=r2_clim, r2_pers=r2_pers, dir_acc=dir_acc, n=len(recs))

out = dict(method="Compass + residual corrector (lag-1 AR feedback)",
           gamma_empirical=GAMMA_EMP, gamma_phi=GAMMA_PHI,
           variants=dict(baseline='no correction', corr_emp='gamma_empirical', corr_phi='gamma_phi'),
           results=metrics_out)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.COMPASS_CORR = " + json.dumps(out, default=str) + ";\n")
print("Saved -> " + OUT)
