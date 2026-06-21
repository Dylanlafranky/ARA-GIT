"""
sum_vs_average_test.py

The actual energy bug: rung contributions were being weighted-AVERAGED, not summed.
A real signal is the SUM of its bandpass channels (∑ bandpass = signal − DC − high-freq).
Averaging collapses that sum into a tiny mean.

Fix: sum, don't average. Test on ECG nsr001.
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt

PHI = 1.6180339887498949
INV_PHI  = 1.0 / PHI
PI_LEAK  = (np.pi - 3) / np.pi
DRAIN_RATE = INV_PHI + PI_LEAK

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\sum_vs_average_data.js")

print("Loading ECG nsr001...")
df = pd.read_csv(ECG_PATH)
ecg_t = df['time_s'].values; ecg_rr = df['rr_ms'].values
DT = 10.0
t_uniform = np.arange(0, int(ecg_t[-1]) - 1, int(DT))
ecg_signal = np.interp(t_uniform, ecg_t, ecg_rr)
mean_full = float(np.mean(ecg_signal))
ecg_zero = ecg_signal - mean_full
N = len(ecg_signal)

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))

def amp_peak(bp, period_samples):
    n_recent = min(int(1.5 * period_samples), len(bp))
    if n_recent < 10: n_recent = min(50, len(bp))
    seg = bp[-n_recent:]
    if len(seg) < 2: return 1e-9
    return float((np.max(seg) - np.min(seg)) / 2.0) + 1e-9

def read_theta(bp, amp_val):
    last = bp[-1]; rate = bp[-1] - bp[-2] if len(bp) >= 2 else 0
    ratio = max(-0.99, min(0.99, last/amp_val))
    return float(np.arccos(ratio) * (-1 if rate > 0 else 1))

# Verify the identity: at anchor, sum of bandpass values ≈ signal - mean
print(f"\nIdentity check: at anchor t=14h, sum(bandpass[t-1]) vs signal[t-1] - mean")
t_anchor = int(14*3600/DT)
arr = ecg_zero[:t_anchor]
RUNGS = [(k, PHI**k / DT) for k in range(8, 21)]
sum_bp_at_anchor = 0.0
for k, p in RUNGS:
    if 4*p > t_anchor: continue
    bp = causal_bandpass(arr, p)
    sum_bp_at_anchor += float(bp[-1])
signal_at_anchor = ecg_signal[t_anchor - 1]
print(f"  signal[t-1] - mean = {signal_at_anchor - mean_full:+.2f}")
print(f"  Σ bandpass[t-1]    = {sum_bp_at_anchor:+.2f}")
print(f"  difference (high-freq + unpinned slow): {(signal_at_anchor - mean_full) - sum_bp_at_anchor:+.2f}")

# === Three projection methods ===

def project_avg(t_a, h, weighted=True):
    """OLD: weighted-average rung contributions."""
    arr_t = ecg_zero[:t_a]
    mean_t = float(np.mean(ecg_signal[:t_a]))
    states = []
    for k, p in RUNGS:
        if 4*p > t_a: continue
        bp = causal_bandpass(arr_t, p)
        a = amp_peak(bp, p); th = read_theta(bp, a)
        w = 1.0 / (1.0 + np.log(abs(k - 8) + 1)) if weighted else 1.0
        states.append(dict(p=p, amp=a, th=th, w=w))
    if not states: return mean_full
    v = float(ecg_signal[t_a - 1])
    p_home = PHI**8 / DT
    drain_per_step = DRAIN_RATE / p_home
    for step in range(1, h+1):
        contrib = 0.0; wt = 0.0
        for s in states:
            new_th = s['th'] + 2*np.pi*step/s['p']
            contrib += s['w'] * s['amp'] * np.cos(new_th)
            wt += s['w']
        if wt > 0: contrib = contrib / wt
        target = mean_t + contrib
        v = v + (target - v) * drain_per_step
    return v

def project_sum(t_a, h, log_weighted=True):
    """NEW: SUM rung contributions (with optional log distance weighting)."""
    arr_t = ecg_zero[:t_a]
    mean_t = float(np.mean(ecg_signal[:t_a]))
    states = []
    for k, p in RUNGS:
        if 4*p > t_a: continue
        bp = causal_bandpass(arr_t, p)
        a = amp_peak(bp, p); th = read_theta(bp, a)
        w = 1.0 / (1.0 + np.log(abs(k - 8) + 1)) if log_weighted else 1.0
        states.append(dict(p=p, amp=a, th=th, w=w))
    if not states: return mean_full
    v = float(ecg_signal[t_a - 1])
    p_home = PHI**8 / DT
    drain_per_step = DRAIN_RATE / p_home
    for step in range(1, h+1):
        contrib = 0.0
        for s in states:
            new_th = s['th'] + 2*np.pi*step/s['p']
            contrib += s['w'] * s['amp'] * np.cos(new_th)
        # NO division — pure sum
        target = mean_t + contrib
        v = v + (target - v) * drain_per_step
    return v

def project_pure_sum(t_a, h):
    """Cleanest: pure sum of channel forecasts, no weighting."""
    return project_sum(t_a, h, log_weighted=False)

# === Sweep ===
HORIZONS = [6, 30, 90, 180, 360, 720]
HORIZON_LABELS = ['1min', '5min', '15min', '30min', '1h', '2h']
ANCHORS = list(range(int(12*3600/DT), int(20*3600/DT), int(30*60/DT)))
print(f"\n{len(ANCHORS)} anchors, comparing AVG / LOG-SUM / PURE-SUM")

t0 = time.time()
results = {('AVG', h): [] for h in HORIZONS}
results.update({('LOGSUM', h): [] for h in HORIZONS})
results.update({('PURESUM', h): [] for h in HORIZONS})
for t_a in ANCHORS:
    for h in HORIZONS:
        if t_a + h - 1 >= N: continue
        truth = float(ecg_signal[t_a + h - 1])
        results[('AVG', h)].append((t_a, project_avg(t_a, h), truth))
        results[('LOGSUM', h)].append((t_a, project_sum(t_a, h, log_weighted=True), truth))
        results[('PURESUM', h)].append((t_a, project_pure_sum(t_a, h), truth))
print(f"  ran in {time.time()-t0:.1f}s")

print(f"\n{'horizon':>8}  {'method':>8}  {'corr':>7}  {'MAE_ms':>7}  {'R2(pers)':>9}  n")
out_metrics = {}
for h, lbl in zip(HORIZONS, HORIZON_LABELS):
    for method in ['AVG', 'LOGSUM', 'PURESUM']:
        recs = results[(method, h)]
        if not recs: continue
        rec = np.array(recs)
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        pers = ecg_signal[origins-1]
        c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds) > 1e-9 else 0
        mae = float(np.mean(np.abs(preds-truths)))
        r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
        print(f"  {lbl:>8}  {method:>8}  {c:+.3f}    {mae:>6.1f}    {r2p:>+.3f}    {len(recs)}")
        out_metrics[f'{lbl}_{method}'] = dict(corr=c, mae=mae, r2p=r2p, n=int(len(recs)))

# Dense forward at 14h
anchor_idx = int(14*3600/DT)
dense_h = list(range(6, 1440 + 6, 6))
dense_avg     = [project_avg(anchor_idx, h) for h in dense_h]
dense_logsum  = [project_sum(anchor_idx, h, log_weighted=True) for h in dense_h]
dense_puresum = [project_pure_sum(anchor_idx, h) for h in dense_h]
dense_truth   = [float(ecg_signal[anchor_idx + h - 1]) if anchor_idx + h - 1 < N else None for h in dense_h]
dense_t_h = [(anchor_idx + h - 1) * DT / 3600 for h in dense_h]
hist_t_h = [i * DT / 3600 for i in range(max(0, anchor_idx-1440), anchor_idx)]
hist_truth = [float(ecg_signal[i]) for i in range(max(0, anchor_idx-1440), anchor_idx)]

out = dict(metrics=out_metrics, anchor_t_h=anchor_idx*DT/3600,
           dense=dict(t_h=dense_t_h, avg=dense_avg, logsum=dense_logsum, puresum=dense_puresum, truth=dense_truth),
           history=dict(t_h=hist_t_h, truth=hist_truth))
with open(OUT, 'w') as f:
    f.write("window.SUMVAVG = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
