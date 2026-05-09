"""
ecg_topology_navigator.py — same architecture as time_topology_navigator.py
but applied to PhysioNet nsr001 ECG (RR intervals).

Differences from ENSO:
  - Time unit: seconds (resampled to 10s grid)
  - Rungs: k=8..20 (periods 76s to 15127s)
  - Home rung: k=19 (BRAC envelope ~2.6h)
  - No matched-rung partner (single-channel data) — Operation C disabled
  - Anchor: 8 hours into the recording, leaving ~14h for comparison
"""
import json, os, time
import numpy as np, pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI3 = 1.0 / PHI**3

def _resolve(p):
    p_lin = p.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p

ECG_PATH = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
OUT      = _resolve(r"F:\SystemFormulaFolder\TheFormula\ecg_topology_navigator_data.js")

print("Loading ECG nsr001 RR-interval data...")
df = pd.read_csv(ECG_PATH)
ecg_t = df['time_s'].values
ecg_rr = df['rr_ms'].values
print(f"  {len(df)} beats, {ecg_t[-1]/3600:.2f}h total")

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

def per_rung_ARA(arr, period):
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

def read_amp_theta(bp):
    if len(bp) < 2: return 0.0, 0.0, 0.0
    n_recent = min(50, len(bp))
    amp = float(np.std(bp[-n_recent:]) * np.sqrt(2)) + 1e-9
    last = bp[-1]; rate = bp[-1] - bp[-2]
    ratio = max(-0.99, min(0.99, last/amp))
    th = np.arccos(ratio) * (-1 if rate > 0 else 1)
    return amp, th, last

# Rungs: k=8..20, period in 10s sample units = PHI^k / 10
RUNGS_K = [k for k in range(8, 21)]
RUNGS = [(k, PHI**k / DT) for k in RUNGS_K]
N_RUNGS = len(RUNGS)
K_REF = 19
RUNG_WEIGHTS = np.array([PHI**(-abs(k - K_REF)) for k,_ in RUNGS])
RUNG_WEIGHTS = RUNG_WEIGHTS / np.sum(RUNG_WEIGHTS)

# Anchor at 14h in — needs ≥10.4h training to pin home rung k=19 (period 9349s)
anchor_idx = int(14 * 3600 / DT)  # 5040 samples = 14h
print(f"\nAnchor: {anchor_idx*DT:.0f}s = {anchor_idx*DT/3600:.2f}h into recording")
print(f"  Training: 0..{anchor_idx} samples ({anchor_idx*DT/3600:.2f}h)")
print(f"  Available test: {anchor_idx} to {N} samples ({(N-anchor_idx)*DT/3600:.2f}h)")

# === INVERSE ===
def inverse_extract(t):
    state = []
    arr = ecg_zero[:t]
    mean_train = float(np.mean(ecg_signal[:t]))
    std_train  = float(np.std(arr)) + 1e-9
    for k, p_samples in RUNGS:
        if 4 * p_samples > t:
            state.append(dict(k=k, period_samples=float(p_samples), period_s=float(p_samples*DT),
                              pinned=False, amp=0, theta=0, ara=1.0, last_value=0))
            continue
        bp = causal_bandpass(arr, p_samples)
        amp, th, last = read_amp_theta(bp)
        ara = per_rung_ARA(arr, p_samples)
        state.append(dict(k=k, period_samples=float(p_samples), period_s=float(p_samples*DT),
                          pinned=True, amp=amp, theta=float(th), ara=ara,
                          last_value=float(last)))
    return state, mean_train, std_train

state, mean_train, std_train = inverse_extract(anchor_idx)
print(f"\n=== INVERSE EXTRACTION at anchor (8h into recording) ===")
print(f"  {'k':>3}  {'period':>10}  {'pinned':>7}  {'amp':>7}  {'θ (deg)':>8}  {'ARA':>5}  {'last':>7}")
for s in state:
    pinned = "✓" if s['pinned'] else "—"
    th_deg = np.degrees(s['theta'])
    period_str = f"{s['period_s']:.0f}s" if s['period_s'] < 600 else f"{s['period_s']/60:.1f}min" if s['period_s'] < 3600 else f"{s['period_s']/3600:.1f}h"
    print(f"  {s['k']:>3}  {period_str:>10}  {pinned:>7}  {s['amp']:>7.2f}  {th_deg:>+7.1f}°  {s['ara']:.2f}  {s['last_value']:>+7.2f}")

# === FORWARD ===
def spin_theta(state_k, h_samples):
    p = state_k['period_samples']
    new_th = state_k['theta'] + 2*np.pi*h_samples/p
    decay = np.exp(-abs(state_k['ara'] - PHI) * h_samples / p * 0.05)
    return state_k['amp'] * decay * np.cos(new_th)

def hop_rung(state, current_k, target_k, h_samples_in_current):
    cur = next((s for s in state if s['k'] == current_k), None)
    tar = next((s for s in state if s['k'] == target_k), None)
    if cur is None or tar is None or not tar['pinned']: return None
    delta_k = target_k - current_k
    p_tar = tar['period_samples']
    new_th = tar['theta'] + 2*np.pi*h_samples_in_current*(PHI**delta_k)/p_tar
    decay = np.exp(-abs(tar['ara'] - PHI) * h_samples_in_current * (PHI**delta_k) / p_tar * 0.05)
    return tar['amp'] * decay * np.cos(new_th)

def project(state, mean_train, h_samples):
    pinned_w = np.array([RUNG_WEIGHTS[i] if state[i]['pinned'] else 0.0 for i in range(N_RUNGS)])
    pinned_w = pinned_w / max(pinned_w.sum(), 1e-9)
    own = 0.0
    for i, s in enumerate(state):
        if s['pinned']:
            own += pinned_w[i] * spin_theta(s, h_samples)
    return mean_train + own

# Forward horizons: 1min, 5min, 15min, 30min, 1h, 2h, 4h
horizon_labels = ['1min', '5min', '15min', '30min', '1h', '2h', '4h']
horizons_samples = [6, 30, 90, 180, 360, 720, 1440]

print(f"\n=== FORWARD PROJECTION (k=19 home, no partner) ===")
print(f"  {'h':>6}  {'pred (ms)':>10}  {'truth (ms)':>11}")
forward_table = []
for h_lbl, h_samp in zip(horizon_labels, horizons_samples):
    pred = project(state, mean_train, h_samp)
    if anchor_idx + h_samp - 1 < N:
        truth = float(ecg_signal[anchor_idx + h_samp - 1])
    else:
        truth = None
    print(f"  {h_lbl:>6}  {pred:>10.1f}  {truth if truth is None else f'{truth:.1f}':>11}")
    forward_table.append(dict(h=h_lbl, h_samples=h_samp, pred=pred, truth=truth))

# Rung-hop: same projection through k=17,18,19,20
print(f"\n=== RUNG-HOP — same forward shape through different rungs ===")
hop_results = {}
for hop_k in [16, 17, 18, 19, 20]:
    print(f"\n  -- through k={hop_k} (period {PHI**hop_k:.0f}s = {PHI**hop_k/3600:.2f}h) --")
    rec = []
    for h_lbl, h_samp in zip(horizon_labels, horizons_samples):
        val = hop_rung(state, K_REF, hop_k, h_samp)
        if val is not None:
            rec.append(dict(h=h_lbl, h_samples=h_samp, amp=float(val)))
            print(f"    {h_lbl:>6}: {val:>+10.2f}")
        else:
            rec.append(dict(h=h_lbl, h_samples=h_samp, amp=None))
    hop_results[f'k{hop_k}'] = rec

# Dense forward curve for time chart — every minute (6 samples) for 4 hours
print("\nBuilding dense forward curves...")
dense_h_samples = list(range(6, 1440 + 6, 6))  # every 1 min up to 4h
dense_pred = [project(state, mean_train, h) for h in dense_h_samples]
dense_truth = [float(ecg_signal[anchor_idx + h - 1]) if anchor_idx + h - 1 < N else None for h in dense_h_samples]
dense_t_hours = [(anchor_idx + h - 1) * DT / 3600 for h in dense_h_samples]

# History (last 4 hours before anchor)
hist_start = max(0, anchor_idx - 1440)
hist_t_hours = [i * DT / 3600 for i in range(hist_start, anchor_idx)]
hist_truth = [float(ecg_signal[i]) for i in range(hist_start, anchor_idx)]

# Per-rung curves: full multi-cycle forward view
print("Computing per-rung forward waves...")
per_rung_curves = {}
for k_view in [12, 14, 16, 17, 18, 19, 20]:
    s = next((s for s in state if s['k'] == k_view), None)
    if s is None or not s['pinned']: continue
    span_samples = int(2 * s['period_samples'])
    curve = []
    for h_samp in range(6, span_samples + 6, 6):
        if h_samp > span_samples: break
        v = spin_theta(s, h_samp) + mean_train
        curve.append(dict(h_samples=h_samp, t_min=h_samp*DT/60, amp=float(v)))
    per_rung_curves[f'k{k_view}'] = dict(period_s=s['period_s'], ara=s['ara'], amp=s['amp'],
                                          theta_deg=float(np.degrees(s['theta'])), curve=curve)

out = dict(
    anchor=dict(idx=int(anchor_idx), t_hours=anchor_idx*DT/3600),
    state=state, mean_train=mean_train, std_train=std_train,
    forward=dict(t_hours=dense_t_hours, pred=dense_pred, truth=dense_truth),
    history=dict(t_hours=hist_t_hours, truth=hist_truth),
    hop_table=hop_results,
    per_rung_curves=per_rung_curves,
    forward_table=forward_table,
    rungs=RUNGS_K,
)
with open(OUT, 'w') as f:
    f.write("window.ECG_NAV = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
