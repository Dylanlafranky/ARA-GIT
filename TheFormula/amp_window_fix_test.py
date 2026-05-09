"""
amp_window_fix_test.py

The amplitude-underestimation bug: the current per-rung amp = std(bp[-50:]) × √2.
For slow rungs that's a window covering only a few percent of one cycle —
gives a tiny number that doesn't reflect the actual cycle amplitude.

Fix: scale the window with the rung's period AND use peak-to-peak of the most
recent full cycle (or two) as the amplitude.

Compare three architectures on ECG nsr001:
  OLD       — std(bp[-50:]) × √2  (broken keyhole-window amp)
  WIDEAMP   — std(bp[-2*period:]) × √2  (window scales with period)
  PEAKAMP   — max(|bp[-period:]|)  (peak-to-peak of last full cycle)

Combined with Dylan's drain architecture (anchor at v_now, log weights, drain rate).
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI  = 1.0 / PHI
PI_LEAK  = (np.pi - 3) / np.pi
DRAIN_RATE = INV_PHI + PI_LEAK

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\amp_window_fix_data.js")

print("Loading ECG nsr001...")
df = pd.read_csv(ECG_PATH)
ecg_t = df['time_s'].values
ecg_rr = df['rr_ms'].values
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
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

# Three different amp estimators
def amp_old(bp, period_samples):
    """Broken: 50-sample keyhole window"""
    n_recent = min(50, len(bp))
    return float(np.std(bp[-n_recent:]) * np.sqrt(2)) + 1e-9

def amp_wide(bp, period_samples):
    """Window scales with rung period — covers ~2 full cycles"""
    n_recent = min(int(2 * period_samples), len(bp))
    if n_recent < 10: n_recent = min(50, len(bp))
    return float(np.std(bp[-n_recent:]) * np.sqrt(2)) + 1e-9

def amp_peak(bp, period_samples):
    """Peak-to-peak of last full cycle — direct measure of actual swing"""
    n_recent = min(int(1.5 * period_samples), len(bp))
    if n_recent < 10: n_recent = min(50, len(bp))
    seg = bp[-n_recent:]
    if len(seg) < 2: return 1e-9
    pp = (np.max(seg) - np.min(seg)) / 2.0
    return float(pp) + 1e-9

def read_theta(bp, amp_val):
    last = bp[-1]; rate = bp[-1] - bp[-2] if len(bp) >= 2 else 0
    ratio = max(-0.99, min(0.99, last/amp_val))
    return float(np.arccos(ratio) * (-1 if rate > 0 else 1))

# φ-rungs
RUNGS_K = list(range(8, 21))
RUNGS = [(k, PHI**k / DT) for k in RUNGS_K]
K_HOME = 8
LOG_WEIGHTS = {k: 1.0 / (1.0 + np.log(abs(k - K_HOME) + 1)) for k, _ in RUNGS}

def project(t_anchor, h, amp_fn):
    arr = ecg_zero[:t_anchor]
    mean_train = float(np.mean(ecg_signal[:t_anchor]))
    states = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr, p)
        amp = amp_fn(bp, p)
        th = read_theta(bp, amp)
        states.append(dict(k=k, p=p, amp=amp, th=th, w=LOG_WEIGHTS[k]))
    if not states: return mean_full

    v = float(ecg_signal[t_anchor - 1])
    p_home = PHI**K_HOME / DT
    drain_per_step = DRAIN_RATE / p_home

    for step in range(1, h + 1):
        contrib = 0.0
        w_total = 0.0
        for s in states:
            new_th = s['th'] + 2*np.pi*step/s['p']
            val = s['amp'] * np.cos(new_th)
            contrib += s['w'] * val
            w_total += s['w']
        if w_total > 0:
            contrib = contrib / w_total
        target = mean_train + contrib
        v = v + (target - v) * drain_per_step
    return v

# === Sweep anchors ===
HORIZONS = [6, 30, 90, 180, 360, 720]
HORIZON_LABELS = ['1min', '5min', '15min', '30min', '1h', '2h']
ANCHORS = list(range(int(12*3600/DT), int(20*3600/DT), int(30*60/DT)))

# Show amplitude estimates for one anchor first
print(f"\nAnchor diagnostic at 14h — amp estimates per rung")
t_diag = int(14*3600/DT)
arr_diag = ecg_zero[:t_diag]
print(f"  {'k':>3}  {'period':>10}  {'amp_old':>9}  {'amp_wide':>10}  {'amp_peak':>10}")
for k, p in RUNGS:
    if 4*p > t_diag: continue
    bp = causal_bandpass(arr_diag, p)
    a_o = amp_old(bp, p); a_w = amp_wide(bp, p); a_p = amp_peak(bp, p)
    p_str = f"{p*DT:.0f}s" if p*DT < 600 else f"{p*DT/60:.1f}min" if p*DT < 3600 else f"{p*DT/3600:.2f}h"
    print(f"  {k:>3}  {p_str:>10}  {a_o:>9.2f}  {a_w:>10.2f}  {a_p:>10.2f}")

print(f"\n{len(ANCHORS)} anchors, comparing 3 amp estimators")
t0 = time.time()
results = {('OLD', h): [] for h in HORIZONS}
results.update({('WIDE', h): [] for h in HORIZONS})
results.update({('PEAK', h): [] for h in HORIZONS})
for t_a in ANCHORS:
    for h in HORIZONS:
        if t_a + h - 1 >= N: continue
        truth = float(ecg_signal[t_a + h - 1])
        results[('OLD', h)].append((t_a, project(t_a, h, amp_old), truth))
        results[('WIDE', h)].append((t_a, project(t_a, h, amp_wide), truth))
        results[('PEAK', h)].append((t_a, project(t_a, h, amp_peak), truth))
print(f"  ran in {time.time()-t0:.1f}s")

print(f"\n{'horizon':>8}  {'method':>6}  {'corr':>7}  {'MAE_ms':>7}  {'R2(pers)':>9}  n")
out_metrics = {}
for h, lbl in zip(HORIZONS, HORIZON_LABELS):
    for method in ['OLD', 'WIDE', 'PEAK']:
        recs = results[(method, h)]
        if not recs: continue
        rec = np.array(recs)
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        pers = ecg_signal[origins-1]
        c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds) > 1e-9 else 0
        mae = float(np.mean(np.abs(preds-truths)))
        r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
        print(f"  {lbl:>8}  {method:>6}  {c:+.3f}    {mae:>6.1f}    {r2p:>+.3f}    {len(recs)}")
        out_metrics[f'{lbl}_{method}'] = dict(corr=c, mae=mae, r2p=r2p, n=int(len(recs)))

# Dense forward at 14h
anchor_idx = int(14*3600/DT)
dense_h = list(range(6, 1440 + 6, 6))
dense_old   = [project(anchor_idx, h, amp_old) for h in dense_h]
dense_wide  = [project(anchor_idx, h, amp_wide) for h in dense_h]
dense_peak  = [project(anchor_idx, h, amp_peak) for h in dense_h]
dense_truth = [float(ecg_signal[anchor_idx + h - 1]) if anchor_idx + h - 1 < N else None for h in dense_h]
dense_t_h = [(anchor_idx + h - 1) * DT / 3600 for h in dense_h]
hist_t_h = [i * DT / 3600 for i in range(max(0, anchor_idx-1440), anchor_idx)]
hist_truth = [float(ecg_signal[i]) for i in range(max(0, anchor_idx-1440), anchor_idx)]

# Per-rung amp comparison
amp_diag = []
for k, p in RUNGS:
    if 4*p > anchor_idx: continue
    bp = causal_bandpass(ecg_zero[:anchor_idx], p)
    amp_diag.append(dict(k=k, period_s=p*DT,
                         old=amp_old(bp,p), wide=amp_wide(bp,p), peak=amp_peak(bp,p)))

out = dict(metrics=out_metrics, anchor_t_h=anchor_idx*DT/3600,
           dense=dict(t_h=dense_t_h, old=dense_old, wide=dense_wide, peak=dense_peak, truth=dense_truth),
           history=dict(t_h=hist_t_h, truth=hist_truth),
           amp_diagnostic=amp_diag)
with open(OUT, 'w') as f:
    f.write("window.AMP_FIX = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
