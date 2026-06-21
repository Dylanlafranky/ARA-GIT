"""
state_propagation_test.py

Dylan's proposed alternative architecture: instead of averaging amplitude across
the whole training window and using pure cosine forward, use a *state-propagation*
view at each moment:

  - v_now = the most recent rung value (not a long-term std)
  - delta = v_now - v_prev (current momentum)
  - amp_local = peak amplitude of the most recent complete cycle (not historical avg)
  - ARA_local = build/release ratio measured on the most recent cycle
  - rung_max = bound on amplitude this rung can carry

Then forward-project step-by-step using an ARA-shaped wave — building over
T_build = P × ARA / (1+ARA), releasing over T_release = P / (1+ARA).
This reacts to the current state instead of dragging through historical means.

Run on PhysioNet nsr001 ECG anchored at 14h.
"""
import json, os
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\state_propagation_data.js")

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
print(f"  N={N} samples ({N*DT/3600:.2f}h)")

def causal_bandpass(arr, period_units, bw=0.4, order=2):
    n = len(arr); f_c = 1.0/period_units; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    try:
        sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
        return sosfilt(sos, arr - np.mean(arr))
    except Exception:
        return np.zeros(n)

def measure_local_state(bp, period_samples):
    """Read state from the MOST RECENT cycle of this rung's bandpass.
    Returns: v_now, delta, amp_local (peak in last cycle), ARA_local."""
    period_int = max(2, int(period_samples))
    if len(bp) < 2 * period_int + 5:
        return None
    v_now = float(bp[-1])
    v_prev = float(bp[-2])
    delta = v_now - v_prev

    # last full cycle
    last_cycle = bp[-period_int:]
    amp_local = float(np.max(np.abs(last_cycle)))

    # ARA from the last 2 cycles — find peaks/troughs, measure asymmetry
    recent = bp[-2*period_int:]
    smoothed = gaussian_filter1d(recent, max(1, int(period_samples * 0.05)))
    peaks_pos, _ = find_peaks(smoothed, distance=max(2, int(period_samples * 0.5)))
    peaks_neg, _ = find_peaks(-smoothed, distance=max(2, int(period_samples * 0.5)))
    if len(peaks_pos) >= 1 and len(peaks_neg) >= 1:
        # Most recent peak and trough
        p_pos = peaks_pos[-1]
        p_neg = peaks_neg[-1]
        if p_pos > p_neg:
            t_build = p_pos - p_neg
            t_release = (len(recent) - 1 - p_pos)
        else:
            t_release = p_neg - p_pos
            t_build = (len(recent) - 1 - p_neg)
        if t_release > 0 and t_build > 0:
            ara_local = max(0.3, min(3.0, t_build / t_release))
        else:
            ara_local = 1.0
    else:
        ara_local = 1.0

    return dict(v_now=v_now, delta=delta, amp_local=amp_local, ara_local=ara_local,
                period_samples=float(period_samples))

def ara_shaped_step(state_k, h_samples):
    """Single-step forward projection using ARA-shaped wave.
    Wave shape: builds over T_build = P*ARA/(1+ARA), releases over T_release = P/(1+ARA).
    We approximate by a piecewise sinusoidal-like shape with asymmetric half-cycles."""
    P = state_k['period_samples']
    ara = state_k['ara_local']
    amp = state_k['amp_local']
    v_now = state_k['v_now']
    delta = state_k['delta']

    # Determine current phase: use atan2 on (v, delta*P/(2π))
    # That gives phase in [-π, π] where 0 = peak (max v, zero velocity)
    # +π/2 = descending (zero v, negative velocity)
    # ±π = trough (min v, zero velocity)
    # -π/2 = ascending (zero v, positive velocity)
    if amp < 1e-9: return v_now
    norm = max(amp, 1e-9)
    phase_now = np.arctan2(delta * P / (2*np.pi*norm), v_now/norm)

    # Step forward by dt — phase advance rate depends on which half-cycle we're in
    # Build phase covers [-π, 0]; release covers [0, π]
    # Build duration T_build = P*ara/(1+ara); release T_release = P/(1+ara)
    # Phase rate during build: π / T_build; during release: π / T_release
    rate_build   = np.pi / (P * ara / (1 + ara))
    rate_release = np.pi / (P / (1 + ara))

    # Step phase forward dt
    dt = h_samples
    phase = phase_now
    remaining = dt
    while remaining > 1e-9:
        if phase < 0:  # build phase
            # how far to phase=0?
            d_phase_to_peak = -phase
            time_to_peak = d_phase_to_peak / rate_build
            if time_to_peak >= remaining:
                phase = phase + rate_build * remaining
                remaining = 0
            else:
                phase = 0
                remaining -= time_to_peak
        else:  # release phase  (0 to π, then wraps to -π)
            d_phase_to_trough = np.pi - phase
            time_to_trough = d_phase_to_trough / rate_release
            if time_to_trough >= remaining:
                phase = phase + rate_release * remaining
                remaining = 0
            else:
                phase = -np.pi  # wrap to next build
                remaining -= time_to_trough

    # value at this phase: cos(phase) gives 1 at phase=0 (peak), -1 at ±π (trough)
    return amp * np.cos(phase)

# Original method for comparison
def std_amp_method(bp, period_samples, theta_offset, h_samples, ara):
    """Current method: use std of last 50 points × √2 as amplitude, cosine forward."""
    n_recent = min(50, len(bp))
    amp = float(np.std(bp[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp[-1]; rate = bp[-1] - bp[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    th = np.arccos(ratio) * (-1 if rate > 0 else 1)
    new_th = th + 2*np.pi*h_samples/period_samples
    decay = np.exp(-abs(ara - PHI) * h_samples / period_samples * 0.05)
    return amp * decay * np.cos(new_th)

def ara_full_history(arr, period):
    """Same ARA computation as current vehicle (full-history) for comparison."""
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

# === Run both methods at multiple anchor points on ECG ===
RUNGS_K = list(range(8, 21))
RUNGS = [(k, PHI**k / DT) for k in RUNGS_K]
K_REF = 19
RUNG_WEIGHTS_BASE = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])

# Multiple anchors so we can compare statistically
HORIZONS = [6, 30, 90, 180, 360, 720]   # 1min, 5min, 15min, 30min, 1h, 2h
HORIZON_LABELS = ['1min', '5min', '15min', '30min', '1h', '2h']

def project_old(t_anchor, h):
    arr = ecg_zero[:t_anchor]
    mean_train = float(np.mean(ecg_signal[:t_anchor]))
    rung_w = np.array([RUNG_WEIGHTS_BASE[i] if 4*RUNGS[i][1] <= t_anchor else 0
                       for i in range(len(RUNGS))])
    rung_w = rung_w / max(rung_w.sum(), 1e-9)
    own = 0.0
    for i, (k, p) in enumerate(RUNGS):
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr, p)
        ara = ara_full_history(arr, p)
        own += rung_w[i] * std_amp_method(bp, p, 0, h, ara)
    return mean_train + own

def project_new(t_anchor, h):
    arr = ecg_zero[:t_anchor]
    mean_train = float(np.mean(ecg_signal[:t_anchor]))
    rung_w = np.array([RUNG_WEIGHTS_BASE[i] if 4*RUNGS[i][1] <= t_anchor else 0
                       for i in range(len(RUNGS))])
    rung_w = rung_w / max(rung_w.sum(), 1e-9)
    own = 0.0
    for i, (k, p) in enumerate(RUNGS):
        if 4*p > t_anchor: continue
        bp = causal_bandpass(arr, p)
        st = measure_local_state(bp, p)
        if st is None: continue
        own += rung_w[i] * ara_shaped_step(st, h)
    return mean_train + own

# Sweep anchors every 30 min from 12h to 20h, project at each horizon, score
ANCHORS = list(range(int(12*3600/DT), int(20*3600/DT), int(30*60/DT)))  # every 30min
print(f"\n{len(ANCHORS)} anchors from 12h to 20h, every 30 min")

import time
t0 = time.time()
results_old = {h: [] for h in HORIZONS}
results_new = {h: [] for h in HORIZONS}
for t_a in ANCHORS:
    for h in HORIZONS:
        if t_a + h - 1 >= N: continue
        truth = float(ecg_signal[t_a + h - 1])
        po = project_old(t_a, h)
        pn = project_new(t_a, h)
        results_old[h].append((t_a, po, truth))
        results_new[h].append((t_a, pn, truth))
print(f"  ran in {time.time()-t0:.1f}s")

print(f"\n{'horizon':>8}  {'method':>6}  {'corr':>7}  {'MAE_ms':>7}  {'R2(pers)':>9}  n")
out_metrics = {}
for h, lbl in zip(HORIZONS, HORIZON_LABELS):
    for method, recs in [('OLD', results_old[h]), ('NEW', results_new[h])]:
        if not recs: continue
        rec = np.array(recs)
        origins = rec[:,0].astype(int); preds = rec[:,1].astype(float); truths = rec[:,2].astype(float)
        pers = ecg_signal[origins-1]
        c = float(np.corrcoef(preds, truths)[0,1]) if np.std(preds) > 1e-9 else 0
        mae = float(np.mean(np.abs(preds-truths)))
        r2p = float(1 - np.sum((truths-preds)**2)/np.sum((truths-pers)**2))
        print(f"  {lbl:>8}  {method:>6}  {c:+.3f}    {mae:>6.1f}    {r2p:>+.3f}    {len(recs)}")
        out_metrics[f'{lbl}_{method}'] = dict(corr=c, mae=mae, r2p=r2p, n=int(len(recs)))

# Save dense forward curves at one specific anchor for the visualizer
anchor_idx = int(14*3600/DT)
print(f"\nDense forward curves at anchor 14h for visualization...")
dense_h = list(range(6, 1440 + 6, 6))  # every 1min up to 4h
dense_old = [project_old(anchor_idx, h) for h in dense_h]
dense_new = [project_new(anchor_idx, h) for h in dense_h]
dense_truth = [float(ecg_signal[anchor_idx + h - 1]) if anchor_idx + h - 1 < N else None for h in dense_h]
dense_t_h = [(anchor_idx + h - 1) * DT / 3600 for h in dense_h]
hist_t_h = [i * DT / 3600 for i in range(max(0, anchor_idx-1440), anchor_idx)]
hist_truth = [float(ecg_signal[i]) for i in range(max(0, anchor_idx-1440), anchor_idx)]

out = dict(metrics=out_metrics, anchor_t_h=anchor_idx*DT/3600,
           dense=dict(t_h=dense_t_h, old=dense_old, new=dense_new, truth=dense_truth),
           history=dict(t_h=hist_t_h, truth=hist_truth))
with open(OUT, 'w') as f:
    f.write("window.STATE_PROP = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
