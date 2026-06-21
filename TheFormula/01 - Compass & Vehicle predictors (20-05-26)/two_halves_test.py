"""
Two-halves cycle theory test (Dylan 2026-05-03):

Hypothesis: peak-to-peak segmentation captures only HALF of the true topological cycle.
The complete cycle = 2 consecutive halves carrying DIFFERENT information.

Three sub-tests:
  A. Compare peak-to-peak mean shape vs trough-to-trough mean shape.
     If identical → one cycle, just shifted phase.
     If different → two halves carry different info.
  B. Within a double-cycle (peak-to-peak-to-peak), compare first half vs second half shapes.
     If similar → cycles repeat identically.
     If different → consecutive cycles carry different info.
  C. Compare the AMPLITUDE of consecutive cycles. If alternating high-low pattern, that's
     a 2-cycle period at the next rung up.

Tested on ENSO and heart (both have rich peak/trough structure).

DATA: real PhysioNet (nsr001) + real NOAA Niño 3.4.
"""
import json, os
import numpy as np, pandas as pd
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\two_halves_data.js")

ecg = pd.read_csv(ECG_PATH)
t_ecg = ecg['time_s'].values.astype(float); v_ecg_orig = ecg['rr_ms'].values.astype(float)
GRID_DT = 0.5
t_grid = np.arange(t_ecg[0], t_ecg[-1], GRID_DT)
v_ecg = np.interp(t_grid, t_ecg, v_ecg_orig)

df_n = pd.read_csv(NINO_PATH, skiprows=1, header=None, names=['date','val'])
df_n['date'] = pd.to_datetime(df_n['date'].str.strip())
df_n = df_n[df_n['val'] > -90].copy()
v_nino = df_n['val'].values.astype(float)

def bandpass(arr, period_units, dt=1.0, bw=0.4):
    n = len(arr); F = np.fft.rfft(arr - np.mean(arr))
    freqs = np.fft.rfftfreq(n, d=dt)
    f_c = 1.0/period_units
    F[(freqs<(1-bw)*f_c) | (freqs>(1+bw)*f_c)] = 0
    return np.real(np.fft.irfft(F, n=n))

def find_peaks_and_troughs(band, target_period, dt):
    smooth_sigma = max(1, int(target_period * 0.15 / dt))
    smoothed = gaussian_filter1d(band - np.mean(band), smooth_sigma)
    min_dist = int(target_period * 0.7 / dt)
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    troughs, _ = find_peaks(-smoothed, distance=min_dist)
    return peaks, troughs

def normalize_cycle(seg, n_pts=100):
    x_o = np.linspace(0, 1, len(seg))
    x_n = np.linspace(0, 1, n_pts)
    s = np.interp(x_n, x_o, seg)
    s_n = s - s.min()
    if s_n.max() > 0: s_n /= s_n.max()
    return 2*s_n - 1

def extract_segments(arr, starts, target_period, dt):
    segs = []
    target_n = int(target_period / dt)
    for i in range(len(starts)-1):
        seg = arr[starts[i]:starts[i+1]]
        if len(seg) < target_n*0.5 or len(seg) > target_n*2.5: continue
        segs.append(seg)
    return segs

# === HEART analysis at φ⁵ (Mayer wave) ===
print("=" * 60)
print("HEART (Mayer wave, φ⁵ ~11s)")
print("=" * 60)
heart_period = PHI**5
heart_band = bandpass(v_ecg, heart_period, GRID_DT)
heart_peaks, heart_troughs = find_peaks_and_troughs(heart_band, heart_period, GRID_DT)
print(f"Peaks: {len(heart_peaks)}, Troughs: {len(heart_troughs)}")

# A. Peak-to-peak vs trough-to-trough
heart_p2p = extract_segments(v_ecg, heart_peaks, heart_period, GRID_DT)
heart_t2t = extract_segments(v_ecg, heart_troughs, heart_period, GRID_DT)
heart_p2p_norm = [normalize_cycle(c) for c in heart_p2p]
heart_t2t_norm = [normalize_cycle(c) for c in heart_t2t]
heart_p2p_mean = np.array(heart_p2p_norm).mean(axis=0)
heart_t2t_mean = np.array(heart_t2t_norm).mean(axis=0)

p2p_t2t_corr_heart = float(np.corrcoef(heart_p2p_mean, heart_t2t_mean)[0,1])
print(f"\nA. peak-to-peak vs trough-to-trough mean shape correlation: {p2p_t2t_corr_heart:+.3f}")
print(f"   (high → same shape, low/negative → two halves carry different info)")

# B. Double cycle (peak0 → peak2): split into halves and compare
heart_double_segs = []
for i in range(len(heart_peaks)-2):
    if heart_peaks[i+2] - heart_peaks[i] > heart_period*5/GRID_DT: continue
    seg = v_ecg[heart_peaks[i]:heart_peaks[i+2]]
    if len(seg) < heart_period*1.2/GRID_DT: continue
    heart_double_segs.append(seg)

heart_double_norms = [normalize_cycle(s, n_pts=200) for s in heart_double_segs]
if heart_double_norms:
    heart_double_mean = np.array(heart_double_norms).mean(axis=0)
    h_first_half = heart_double_mean[:100]
    h_second_half = heart_double_mean[100:]
    half_corr_heart = float(np.corrcoef(h_first_half, h_second_half)[0,1])
    print(f"\nB. Within double cycle: first-half vs second-half shape correlation: {half_corr_heart:+.3f}")
    print(f"   (high → cycles repeat, low → genuinely different halves)")

# C. Amplitude alternation (consecutive cycle amps)
heart_amps = [float(c.max() - c.min()) for c in heart_p2p]
heart_amp_lag1 = float(np.corrcoef(heart_amps[:-1], heart_amps[1:])[0,1])
heart_amp_lag2 = float(np.corrcoef(heart_amps[:-2], heart_amps[2:])[0,1])
print(f"\nC. Amplitude lag-1 autocorrelation: {heart_amp_lag1:+.3f}")
print(f"   Amplitude lag-2 autocorrelation: {heart_amp_lag2:+.3f}")
print(f"   (negative lag-1 with positive lag-2 → 2-cycle alternation pattern)")

# === ENSO analysis at φ⁸ ===
print("\n" + "=" * 60)
print("ENSO (φ⁸ ~47mo)")
print("=" * 60)
nino_period = PHI**8
nino_band = bandpass(v_nino, nino_period, dt=1.0)
nino_peaks, nino_troughs = find_peaks_and_troughs(nino_band, nino_period, dt=1.0)
print(f"Peaks: {len(nino_peaks)}, Troughs: {len(nino_troughs)}")

nino_p2p = extract_segments(v_nino, nino_peaks, nino_period, 1.0)
nino_t2t = extract_segments(v_nino, nino_troughs, nino_period, 1.0)
nino_p2p_norm = [normalize_cycle(c) for c in nino_p2p]
nino_t2t_norm = [normalize_cycle(c) for c in nino_t2t]
nino_p2p_mean = np.array(nino_p2p_norm).mean(axis=0)
nino_t2t_mean = np.array(nino_t2t_norm).mean(axis=0)
p2p_t2t_corr_nino = float(np.corrcoef(nino_p2p_mean, nino_t2t_mean)[0,1])
print(f"\nA. peak-to-peak vs trough-to-trough mean shape correlation: {p2p_t2t_corr_nino:+.3f}")

# B. Double cycle for ENSO
nino_double_segs = []
for i in range(len(nino_peaks)-2):
    if nino_peaks[i+2] - nino_peaks[i] > nino_period*5: continue
    seg = v_nino[nino_peaks[i]:nino_peaks[i+2]]
    if len(seg) < nino_period*1.2: continue
    nino_double_segs.append(seg)

nino_double_norms = [normalize_cycle(s, n_pts=200) for s in nino_double_segs]
if nino_double_norms:
    nino_double_mean = np.array(nino_double_norms).mean(axis=0)
    n_first_half = nino_double_mean[:100]
    n_second_half = nino_double_mean[100:]
    half_corr_nino = float(np.corrcoef(n_first_half, n_second_half)[0,1])
    print(f"\nB. Within double cycle: first-half vs second-half shape correlation: {half_corr_nino:+.3f}")

nino_amps = [float(c.max() - c.min()) for c in nino_p2p]
nino_amp_lag1 = float(np.corrcoef(nino_amps[:-1], nino_amps[1:])[0,1])
nino_amp_lag2 = float(np.corrcoef(nino_amps[:-2], nino_amps[2:])[0,1])
print(f"\nC. ENSO amp lag-1: {nino_amp_lag1:+.3f}, lag-2: {nino_amp_lag2:+.3f}")

# === Interpretation ===
print("\n" + "=" * 60)
print("INTERPRETATION")
print("=" * 60)
print(f"\nIf Dylan's 'one cycle = 2 halves' theory holds:")
print(f"  • peak-to-peak ≠ trough-to-trough (low correlation expected)")
print(f"  • first half ≠ second half within double cycle (low correlation expected)")
print(f"  • Amplitude shows 2-cycle pattern (lag-1 negative, lag-2 positive)")
print(f"\nResults:")
print(f"  HEART: p2p-vs-t2t = {p2p_t2t_corr_heart:+.3f}, half-vs-half = {half_corr_heart:+.3f}, amp lag-1 = {heart_amp_lag1:+.3f}, amp lag-2 = {heart_amp_lag2:+.3f}")
print(f"  ENSO:  p2p-vs-t2t = {p2p_t2t_corr_nino:+.3f}, half-vs-half = {half_corr_nino:+.3f}, amp lag-1 = {nino_amp_lag1:+.3f}, amp lag-2 = {nino_amp_lag2:+.3f}")

# Save mean curves
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001", nino="NOAA PSL Nino 3.4 1870-2025"),
    heart=dict(
        p2p_mean=heart_p2p_mean.tolist(),
        t2t_mean=heart_t2t_mean.tolist(),
        double_mean=heart_double_mean.tolist() if heart_double_norms else None,
        p2p_t2t_corr=p2p_t2t_corr_heart,
        half_corr=half_corr_heart if heart_double_norms else None,
        amp_lag1=heart_amp_lag1,
        amp_lag2=heart_amp_lag2,
        n_p2p=len(heart_p2p), n_t2t=len(heart_t2t), n_double=len(heart_double_segs),
    ),
    nino=dict(
        p2p_mean=nino_p2p_mean.tolist(),
        t2t_mean=nino_t2t_mean.tolist(),
        double_mean=nino_double_mean.tolist() if nino_double_norms else None,
        p2p_t2t_corr=p2p_t2t_corr_nino,
        half_corr=half_corr_nino if nino_double_norms else None,
        amp_lag1=nino_amp_lag1,
        amp_lag2=nino_amp_lag2,
        n_p2p=len(nino_p2p), n_t2t=len(nino_t2t), n_double=len(nino_double_segs),
    ),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.TWO_HALVES = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
