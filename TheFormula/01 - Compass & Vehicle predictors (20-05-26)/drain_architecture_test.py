"""
drain_architecture_test.py

Dylan's deeper-fix architecture:
  - Dominant rung = the rung the measurement naturally lives on (not bandpass-derived).
    For ECG sampled at 10 s, the natural rung is the one closest to our sample-grid period.
  - ALL rungs contribute fully forward — no per-rung amplitude decay, no kappa damping.
  - Other rungs feed in with LOG distance weights:
      vertical_weight(k, k_home) = 1 / (1 + log(|k - k_home| + 1))
  - Constant drain per step at (φ - 1) + (π - 3)/π — the "movement through time downward"
    that bleeds deviation from the mean each step. φ - 1 = 1/φ = 0.618; π-leak = 0.045.
  - Forward starts at v_now (last observed), not at mean.

Compare three architectures on PhysioNet nsr001 ECG, multiple anchors, multiple horizons:
  OLD       — current method (kappa decay + cosine + sum of weighted rungs from mean)
  STATE     — single-step ARA-shaped state propagation (previous test)
  DRAIN     — Dylan's architecture: anchor at v_now, full-energy rung sum, constant drain
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI  = 1.0 / PHI                   # 0.618
PI_LEAK  = (np.pi - 3) / np.pi         # 0.045
DRAIN_RATE = INV_PHI + PI_LEAK         # ~0.663 per home-rung cycle

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\drain_architecture_data.js")

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
print(f"  N={N} samples ({N*DT/3600:.2f}h), DT={DT}s, drain rate per home-cycle = {DRAIN_RATE:.4f}")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

# φ-rungs in 10s sample units
RUNGS_K = list(range(8, 21))
RUNGS = [(k, PHI**k / DT) for k in RUNGS_K]
RUNGS_DICT = {k: p for k, p in RUNGS}

# Dylan's "dominant rung = where the measurement naturally lives".
# For 10s-grid ECG, the smallest pinned rung is k=8 (period 47s ≈ 4.7 samples).
# But the SLOWEST observed rhythm is the BRAC envelope at k=19 (~2.6h).
# Use k=8 as the "data-native" home — that's where the data's intrinsic rhythm lives
# at this sampling rate. The system's nervous-system tick.
K_HOME_DATA = 8  # rung where the measurement resolves

def vertical_log_weight(k, k_home):
    """Information attenuation by rung distance (vertical)."""
    return 1.0 / (1.0 + np.log(abs(k - k_home) + 1))

# Pre-compute log weights from the data-home rung
LOG_WEIGHTS = {k: vertical_log_weight(k, K_HOME_DATA) for k, _ in RUNGS}
W_SUM = sum(LOG_WEIGHTS.values())

def read_amp_theta(bp):
    if len(bp) < 2: return 0.0, 0.0
    n_recent = min(50, len(bp))
    amp = float(np.std(bp[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp[-1]; rate = bp[-1] - bp[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    return amp, np.arccos(ratio) * (-1 if rate > 0 else 1)

def ara_full(arr, period):
    bp = causal_bandpass(arr, period, bw=0.85)
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

def project_old(t_anchor, h):
    """Current method: per-rung cosine + ARA-driven decay, weighted sum from mean."""
    arr = ecg_zero[:t_anchor]
    mean_train = float(np.mean(ecg_signal[:t_anchor]))
    pinned = [(i, k, p) for i, (k, p) in enumerate(RUNGS) if 4*p <= t_anchor]
    if not pinned: return mean_train
    rung_w = np.array([PHI**(-abs(k - 19)) for _, k, _ in pinned])
    rung_w = rung_w / rung_w.sum()
    own = 0.0
    for j, (i, k, p) in enumerate(pinned):
        bp = causal_bandpass(arr, p)
        amp, th = read_amp_theta(bp)
        ara = ara_full(arr, p)
        new_th = th + 2*np.pi*h/p
        decay = np.exp(-abs(ara - PHI) * h / p * 0.05)
        own += rung_w[j] * amp * decay * np.cos(new_th)
    return mean_train + own

def project_drain(t_anchor, h):
    """Dylan's architecture: anchor at v_now, ALL rungs contribute fully forward,
    log-distance weighted from data-home rung, constant drain per step."""
    arr = ecg_zero[:t_anchor]
    mean_train = float(np.mean(ecg_signal[:t_anchor]))

    # State at anchor: amp + θ for each pinned rung
    states = []
    for k, p in RUNGS:
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr, p)
        amp, th = read_amp_theta(bp)
        states.append(dict(k=k, p=p, amp=amp, th=th, w=LOG_WEIGHTS[k]))
    if not states: return mean_full

    # Anchor at v_now (last observed signal — NOT mean)
    v = float(ecg_signal[t_anchor - 1])
    p_home = RUNGS_DICT[K_HOME_DATA]
    drain_per_step = DRAIN_RATE / p_home  # drain rate scaled to one home-rung cycle

    # March forward step by step (1 sample = 10s) for h steps
    for step in range(1, h + 1):
        # all-rungs contribution at this future step (relative to anchor)
        contrib = 0.0
        w_total = 0.0
        for s in states:
            new_th = s['th'] + 2*np.pi*step/s['p']
            # rung's natural wave value at this future moment, full amplitude
            val = s['amp'] * np.cos(new_th)
            contrib += s['w'] * val
            w_total += s['w']
        if w_total > 0:
            contrib = contrib / w_total

        # The contribution drives v toward (mean + contrib) — instantaneous target
        target = mean_train + contrib

        # drain pulls v back toward target at constant rate (entropy bleed)
        # but also lets the wave drive v: combined as a relaxation step
        v = v + (target - v) * drain_per_step

    return v

# === Sweep anchors ===
HORIZONS = [6, 30, 90, 180, 360, 720]
HORIZON_LABELS = ['1min', '5min', '15min', '30min', '1h', '2h']
ANCHORS = list(range(int(12*3600/DT), int(20*3600/DT), int(30*60/DT)))
print(f"\n{len(ANCHORS)} anchors from 12h to 20h every 30 min")

t0 = time.time()
results_old = {h: [] for h in HORIZONS}
results_drain = {h: [] for h in HORIZONS}
for t_a in ANCHORS:
    for h in HORIZONS:
        if t_a + h - 1 >= N: continue
        truth = float(ecg_signal[t_a + h - 1])
        results_old[h].append((t_a, project_old(t_a, h), truth))
        results_drain[h].append((t_a, project_drain(t_a, h), truth))
print(f"  ran in {time.time()-t0:.1f}s")

print(f"\n{'horizon':>8}  {'method':>6}  {'corr':>7}  {'MAE_ms':>7}  {'R2(pers)':>9}  n")
out_metrics = {}
for h, lbl in zip(HORIZONS, HORIZON_LABELS):
    for label, recs in [('OLD', results_old[h]), ('DRAIN', results_drain[h])]:
        if not recs: continue
        rec = np.array(recs)
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        pers = ecg_signal[origins-1]
        c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds) > 1e-9 else 0
        mae = float(np.mean(np.abs(preds-truths)))
        r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
        print(f"  {lbl:>8}  {label:>6}  {c:+.3f}    {mae:>6.1f}    {r2p:>+.3f}    {len(recs)}")
        out_metrics[f'{lbl}_{label}'] = dict(corr=c, mae=mae, r2p=r2p, n=int(len(recs)))

# Save dense forward at one anchor for visualization
anchor_idx = int(14*3600/DT)
print(f"\nDense forward at 14h for visualization...")
dense_h = list(range(6, 1440 + 6, 6))
dense_old = [project_old(anchor_idx, h) for h in dense_h]
dense_drain = [project_drain(anchor_idx, h) for h in dense_h]
dense_truth = [float(ecg_signal[anchor_idx + h - 1]) if anchor_idx + h - 1 < N else None for h in dense_h]
dense_t_h = [(anchor_idx + h - 1) * DT / 3600 for h in dense_h]
hist_t_h = [i * DT / 3600 for i in range(max(0, anchor_idx-1440), anchor_idx)]
hist_truth = [float(ecg_signal[i]) for i in range(max(0, anchor_idx-1440), anchor_idx)]

out = dict(metrics=out_metrics, anchor_t_h=anchor_idx*DT/3600,
           drain_rate=DRAIN_RATE, k_home=K_HOME_DATA,
           dense=dict(t_h=dense_t_h, old=dense_old, drain=dense_drain, truth=dense_truth),
           history=dict(t_h=hist_t_h, truth=hist_truth))
with open(OUT, 'w') as f:
    f.write("window.DRAIN_ARCH = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
