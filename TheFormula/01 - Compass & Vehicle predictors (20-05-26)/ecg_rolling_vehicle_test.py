"""
ECG rolling vehicle test — apply the strict-causal pure-structure architecture
to ECG (nsr001 RR-interval data) to see if the same compass/amplitude pattern
holds in a totally different system.

The framework predicts: same vehicle architecture (per-rung phase advance,
matched-rung coupling, AR γ=1/φ³) should work on any φ-rung-organized system.
ECG is closer to closed (the heart is mostly self-driven within one beat).

Architecture:
  - Resample RR intervals to uniform 1Hz grid
  - Apply causal Butterworth bandpass at φ-rungs (k=0..20, periods 1s..15000s)
  - Forward-project amplitude vehicle vs deterministic compass
  - Compare to persistence and climatology baselines

Test horizons (in seconds, then converted to minutes):
  h = 60s (1 min), 600s (10 min), 3600s (1 hour), 7200s (2 hours)
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

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\ecg_rolling_vehicle_data.js")

print("Loading ECG nsr001 RR-interval data...")
df = pd.read_csv(ECG_PATH)
ecg_t = df['time_s'].values
ecg_rr = df['rr_ms'].values
print(f"  {len(df)} beats, {ecg_t[-1]/3600:.2f}h total")

# Resample to uniform 10s grid (so 8000 samples covers 22h)
DT = 10.0  # 10-second sample period
t_uniform = np.arange(0, int(ecg_t[-1]) - 1, int(DT))
ecg_signal = np.interp(t_uniform, ecg_t, ecg_rr)
ecg_signal = ecg_signal - np.mean(ecg_signal)
N = len(ecg_signal)
print(f"  Resampled to {DT}s: {N} samples = {N*DT/3600:.2f}h")

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

# ECG-relevant rungs in 10s units (period in samples)
# Real periods: 1s (k=0), 1.6s (k=1), ... 15127s (k=20)
# In 10s sample units: 0.1, 0.16, ... 1512.7
# Use rungs k where period >= a few samples (k>=8 → P=4.7 samples)
# and period <= N/3 (so we have data to fit)
RUNGS_K = [k for k in range(8, 21) if PHI**k >= 5*DT/DT and PHI**k < N/3]
RUNGS = [(k, PHI**k / DT) for k in RUNGS_K]  # period in sample units
N_RUNGS = len(RUNGS)
print(f"  Using rungs k={[r[0] for r in RUNGS]} (periods {[f'{r[1]*DT:.0f}s' for r in RUNGS]})")
# Use peak rung k=19 (BRAC envelope) as ECG home
K_REF = 19
K_REF_IDX = next((i for i,(k,_) in enumerate(RUNGS) if k == K_REF), len(RUNGS)//2)
print(f"  Home rung k={RUNGS[K_REF_IDX][0]} (period {RUNGS[K_REF_IDX][1]*DT:.0f}s)")
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

def amp_predict(refit_t, h_samples, last_residual, state, mean_train):
    rung_future = []
    for ri, (k, p) in enumerate(RUNGS):
        a, th, _ = state[ri]
        new_th = th + 2*np.pi*h_samples/p
        rung_future.append(a * np.cos(new_th))
    own_pred = float(np.dot(RUNG_WEIGHTS, np.array(rung_future)))
    return mean_train + own_pred + INV_PHI3 * last_residual

def run_compass(refit_t, h_samples, last_residual, state, mean_train, step_mean):
    cur_pos = ecg_signal[refit_t - 1] + np.mean(ecg_rr)
    prev_amp = ecg_signal[refit_t - 1] + np.mean(ecg_rr)
    for tau in range(1, h_samples + 1):
        amp = amp_predict(refit_t, tau, last_residual, state, mean_train)
        delta = amp - prev_amp
        direction = 1 if delta > 0 else -1
        cur_pos += direction * min(abs(delta), step_mean * PHI)
        prev_amp = amp
    return cur_pos

# ===== Rolling test =====
HORIZONS_SAMPLES = [6, 30, 180, 360, 720]  # in 10s units = 1min, 5min, 30min, 1h, 2h
HORIZONS_LABELS = ['1min', '5min', '30min', '1h', '2h']
MIN_TRAIN = 3000  # ~8.3 hours initial training
STEP = 360  # refit every hour (3600s = 360 samples)

print(f"\n  Rolling: refit every {STEP*DT:.0f}s ({STEP*DT/3600:.1f}h), min_train={MIN_TRAIN*DT/3600:.1f}h")
print(f"  Horizons (sample/labels): {list(zip(HORIZONS_SAMPLES, HORIZONS_LABELS))}")

results = {h: dict(amp=[], compass=[]) for h in HORIZONS_SAMPLES}
last_residual = 0.0
mean_full = float(np.mean(ecg_rr))

t_start = time.time()
for refit_t in range(MIN_TRAIN, N - max(HORIZONS_SAMPLES), STEP):
    arr_train_signal = ecg_signal[:refit_t]
    mean_train_offset = float(np.mean(arr_train_signal))  # near 0 since we de-meaned
    nino_scale = float(np.std(arr_train_signal)) + 1e-9
    step_mean = float(np.mean(np.abs(np.diff(arr_train_signal))))

    # Build state for ECG only (single system, no SOI counterpart)
    bp = [causal_bandpass(arr_train_signal, p) for k,p in RUNGS]
    state = []
    for ri, (k, p) in enumerate(RUNGS):
        a, th = read_amp_theta(bp[ri])
        state.append((a, th, 1.0))

    for h in HORIZONS_SAMPLES:
        if refit_t + h - 1 >= N: continue
        truth_signal = ecg_signal[refit_t + h - 1]
        truth_rr = truth_signal + mean_full

        amp_pred_signal = amp_predict(refit_t, h, last_residual, state, 0.0)
        amp_pred_rr = amp_pred_signal + mean_full

        compass_pred_rr = run_compass(refit_t, h, last_residual, state, 0.0, step_mean)

        results[h]['amp'].append((refit_t, amp_pred_rr, truth_rr))
        results[h]['compass'].append((refit_t, compass_pred_rr, truth_rr))

    if results[HORIZONS_SAMPLES[0]]['amp']:
        last = results[HORIZONS_SAMPLES[0]]['amp'][-1]
        last_residual = float(last[2] - last[1])

print(f"  {time.time()-t_start:.1f}s, {len(results[HORIZONS_SAMPLES[0]]['amp'])} refits")

# ===== Metrics =====
print(f"\n========= ECG ROLLING VEHICLE RESULTS =========")
clim = float(np.mean(ecg_rr))
def metrics_for(recs):
    if not recs: return None
    preds = np.array([r[1] for r in recs])
    truths = np.array([r[2] for r in recs])
    pers_preds = np.array([ecg_rr[int((r[0]-1)*DT*len(ecg_rr)/(ecg_t[-1]+1))] if int((r[0]-1)*DT*len(ecg_rr)/(ecg_t[-1]+1)) < len(ecg_rr) else clim for r in recs])
    if np.std(preds) > 1e-9 and np.std(truths) > 1e-9:
        corr = float(np.corrcoef(preds, truths)[0,1])
    else: corr = 0.0
    mae = float(np.mean(np.abs(preds - truths)))
    ss_res = np.sum((truths - preds)**2)
    ss_clim = np.sum((truths - clim)**2)
    ss_pers = np.sum((truths - pers_preds)**2)
    r2_clim = float(1 - ss_res/ss_clim) if ss_clim > 0 else 0.0
    r2_pers = float(1 - ss_res/ss_pers) if ss_pers > 0 else 0.0
    return dict(corr=corr, mae=mae, r2_clim=r2_clim, r2_pers=r2_pers, n=len(recs))

print(f"\n  {'horizon':>10}  {'amp corr':>9}  {'amp MAE':>9}  {'comp corr':>10}  {'comp MAE':>9}  {'amp R²clim':>10}")
metrics_out = {}
for h, label in zip(HORIZONS_SAMPLES, HORIZONS_LABELS):
    m_amp = metrics_for(results[h]['amp'])
    m_comp = metrics_for(results[h]['compass'])
    if m_amp is None or m_comp is None: continue
    print(f"  h={label:>7}  {m_amp['corr']:+.3f}    {m_amp['mae']:.2f}ms     {m_comp['corr']:+.3f}     {m_comp['mae']:.2f}ms    {m_amp['r2_clim']:+.3f}")
    metrics_out[label] = dict(amp=m_amp, compass=m_comp)

out = dict(method="ECG nsr001 rolling vehicle test (compass + amplitude)",
           data="PhysioNet NSRDB nsr001 RR-intervals, 22.5h, resampled to 10s grid",
           horizons=HORIZONS_LABELS, results=metrics_out)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.ECG_ROLLING = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
