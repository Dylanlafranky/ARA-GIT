"""
Apply compass refinements (tanh tick + log rung weights) to ECG nsr001.
Tests whether the refinements that worked on ENSO transfer to ECG.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, lfilter

PHI = 1.6180339887498949
INV_PHI = 1.0/PHI; INV_PHI3 = 1.0/(PHI**3); INV_PHI4 = 1.0/(PHI**4)

def _resolve(p):
    pl = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return pl if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\ecg_compass_refined_data.js")

print("Loading ECG nsr001...")
df = pd.read_csv(ECG_PATH)
ecg_t = df['time_s'].values
ecg_rr = df['rr_ms'].values
DT = 10.0
t_uniform = np.arange(0, int(ecg_t[-1]) - 1, int(DT))
ecg_signal = np.interp(t_uniform, ecg_t, ecg_rr)
ecg_signal = ecg_signal - np.mean(ecg_signal)
N = len(ecg_signal)
mean_full = float(np.mean(ecg_rr))
print(f"  {N} samples ({N*DT/3600:.1f}h)")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n=len(arr); fc=1.0/period_units; nyq=0.5
    Wn_lo = max(1e-6, (1-bw)*fc/nyq); Wn_hi = min(0.999, (1+bw)*fc/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    b,a = butter(order,[Wn_lo,Wn_hi], btype='bandpass')
    return lfilter(b,a, arr - np.mean(arr))

def read_amp_theta(bp):
    if len(bp) < 2: return 0.0, 0.0
    r = min(50, len(bp))
    amp = float(np.std(bp[-r:])*np.sqrt(2)) + 1e-9
    last = bp[-1]; rate = bp[-1]-bp[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate>0 else 1)

RUNGS_K = list(range(8, 17))
RUNGS = [(k, PHI**k / DT) for k in RUNGS_K]
N_RUNGS = len(RUNGS)
K_REF = 12
K_REF_IDX = next(i for i,(k,_) in enumerate(RUNGS) if k == K_REF)

RW_PHI = np.array([PHI**(-abs(k-K_REF)) for k,_ in RUNGS])
RW_PHI = RW_PHI / np.sum(RW_PHI)
RW_LOG = np.array([1.0/(1.0 + np.log(abs(k-K_REF)+1)) for k,_ in RUNGS])
RW_LOG = RW_LOG / np.sum(RW_LOG)

def amp_predict(refit_t, h, last_residual, state, rung_weights):
    rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a, th, _ = state[ri]
        new_th = th + 2*np.pi*h/p
        rung_future.append(a * np.cos(new_th))
    return float(np.dot(rung_weights, np.array(rung_future))) + INV_PHI3 * last_residual

def run_compass(refit_t, h, last_residual, state, step_mean, rung_weights, continuous):
    cur_pos = ecg_signal[refit_t-1] + mean_full
    prev_amp_signal = ecg_signal[refit_t-1]
    for tau in range(1, h+1):
        amp_signal = amp_predict(refit_t, tau, last_residual, state, rung_weights)
        delta = amp_signal - prev_amp_signal
        if continuous:
            step = step_mean * np.tanh(delta / max(step_mean, 1e-9))
        else:
            direction = 1 if delta > 0 else -1
            step = direction * min(abs(delta), step_mean * PHI)
        cur_pos += step
        prev_amp_signal = amp_signal
    return cur_pos

# Rolling test
HORIZONS = [6, 30, 180, 360, 720]
LABELS = ['1min','5min','30min','1h','2h']
MIN_TRAIN = 3000
STEP = 360

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
    arr_train = ecg_signal[:refit_t]
    step_mean = float(np.mean(np.abs(np.diff(arr_train))))
    bp = [causal_bandpass(arr_train, p) for k,p in RUNGS]
    state = []
    for ri, (k, p) in enumerate(RUNGS):
        a, th = read_amp_theta(bp[ri])
        state.append((a, th, 1.0))
    for h in HORIZONS:
        if refit_t+h-1 >= N: continue
        truth = ecg_signal[refit_t+h-1] + mean_full
        for vname, cfg in variants.items():
            pred = run_compass(refit_t, h, last_residual, state, step_mean,
                              cfg['rung_weights'], cfg['continuous'])
            results[vname][h].append((refit_t, pred, truth))
    if results['BASELINE'][HORIZONS[0]]:
        last = results['BASELINE'][HORIZONS[0]][-1]
        last_residual = float(last[2] - last[1] - mean_full + np.mean(ecg_signal[:refit_t]))
print(f"  {time.time()-t_start:.1f}s, {len(results['BASELINE'][HORIZONS[0]])} refits")

print("\n========= ECG REFINEMENTS RESULTS =========")
clim = float(np.mean(ecg_rr))
metrics_out = {}
for vname in ['BASELINE','CONT','LOG','BOTH']:
    print(f"\n--- {vname} ---")
    print(f"  {'horizon':>8}  {'corr':>7}  {'MAE(ms)':>8}  {'R²(pers)':>9}")
    metrics_out[vname] = {}
    for h, label in zip(HORIZONS, LABELS):
        recs = results[vname][h]
        if not recs: continue
        preds = np.array([r[1] for r in recs])
        truths = np.array([r[2] for r in recs])
        # Persistence baseline at h: predict ECG_RR[refit_t-1]
        pers_preds = np.array([ecg_signal[r[0]-1] + mean_full for r in recs])
        corr = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds)>1e-9 and np.std(truths)>1e-9 else 0.0
        mae = float(np.mean(np.abs(preds - truths)))
        ss_res = np.sum((truths-preds)**2); ss_pers = np.sum((truths-pers_preds)**2)
        r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
        print(f"  h={label:>5}  {corr:+.3f}    {mae:.1f}    {r2_pers:+.3f}")
        metrics_out[vname][label] = dict(corr=corr, mae=mae, r2_pers=r2_pers, n=len(recs))

out = dict(method="ECG compass refinements (tanh tick + log rung weights)",
           variants=variants.keys() if hasattr(variants,'keys') else list(variants),
           horizons=LABELS, results=metrics_out)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ECG_REFINED = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
