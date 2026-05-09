"""
Wave-ARA carry test (resurrecting 243AR concept):

Original concept (Dylan, in 243AR):
  wave_ara = peak[i-1] / peak[i-2]   (the wave's own growth/decay between peaks)
  phi_distance = wave_ara - φ

  If positive (>φ) → excess energy was conserved → next cycle amplifies (1/φ² weight)
  If negative (<φ) → energy was consumed → next cycle dampens (1/φ⁴ weight, weaker)

Tests today:
  1. Does wave_ara at cycle i predict amplitude of cycle i+1? (correlation)
  2. Does the asymmetric carry (φ-distance × 1/φ² up vs 1/φ⁴ down) match data?
  3. Does adding wave_ara as a feature improve our 86% direction predictor?

This connects to today's "consecutive cycles share 85-92% of shape but differ"
finding — the wave_ara measures exactly that ~10-15% difference.

DATA: real PhysioNet (nsr001) + real NOAA Niño 3.4.
"""
import json, os
import numpy as np, pandas as pd
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = 1.6180339887498949
INV_PHI_2 = 1/PHI**2
INV_PHI_4 = 1/PHI**4

def _resolve(p_win):
    p_lin = p_win.replace("F:\\SystemFormulaFolder", "/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder").replace("\\","/")
    return p_lin if os.path.isdir("/sessions/amazing-cool-archimedes/mnt/SystemFormulaFolder") else p_win

ECG_PATH  = _resolve(r"F:\SystemFormulaFolder\TheFormula\nsr001_rr.csv")
NINO_PATH = _resolve(r"F:\SystemFormulaFolder\Nino34\nino34.long.anom.csv")
OUT       = _resolve(r"F:\SystemFormulaFolder\TheFormula\wave_ara_carry_data.js")

# Load
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

def extract_cycle_amplitudes(arr, target_period, dt):
    """Return amplitude (peak-to-trough) of each cycle in chronological order."""
    smooth_sigma = max(1, int(target_period * 0.15 / dt))
    smoothed = gaussian_filter1d(arr - np.mean(arr), smooth_sigma)
    min_dist = int(target_period * 0.7 / dt)
    peaks, _ = find_peaks(smoothed, distance=min_dist)
    amps = []
    for i in range(len(peaks)-1):
        seg = arr[peaks[i]:peaks[i+1]]
        target_n = int(target_period / dt)
        if len(seg) < target_n*0.5 or len(seg) > target_n*2.5: continue
        amps.append(float(seg.max() - seg.min()))
    return np.array(amps)

# === HEART analysis ===
print("=" * 60)
print("HEART (Mayer wave φ⁵ ~11s)")
print("=" * 60)
heart_amps = extract_cycle_amplitudes(v_ecg, PHI**5, GRID_DT)
print(f"Cycles extracted: {len(heart_amps)}")

# wave_ara at cycle i = amps[i-1] / amps[i-2]
# Then check: does it predict amps[i] / amps[i-1]?
def wave_ara_analysis(amps, label):
    if len(amps) < 5: return None
    # wave_ara[i] = amps[i] / amps[i-1] (ratio of consecutive)
    # OR per Dylan's 243AR: wave_ara = peak[i-1]/peak[i-2] tells you about peak[i] coming up
    # Let's compute: prev_ratio = amps[i-1] / amps[i-2]; next_ratio = amps[i] / amps[i-1]
    # Question: does prev_ratio predict next_ratio?

    n = len(amps)
    prev_ratios = []
    next_ratios = []
    phi_distances = []
    actual_amps_next = []
    predicted_amps_next = []  # what 243AR predicts for next amp

    for i in range(2, n):
        prev_ratio = amps[i-1] / amps[i-2] if amps[i-2] > 0 else 1.0
        next_ratio = amps[i] / amps[i-1] if amps[i-1] > 0 else 1.0
        prev_ratios.append(prev_ratio)
        next_ratios.append(next_ratio)
        phi_distances.append(prev_ratio - PHI)
        actual_amps_next.append(amps[i])
        # 243AR's prediction:
        # If prev_ratio > φ: excess energy conserved → amplify (carry × 1/φ²)
        # If prev_ratio < φ: deficit → dampen (carry × 1/φ⁴)
        carry = prev_ratio - PHI
        weight = INV_PHI_2 if carry > 0 else INV_PHI_4
        # Predict next amp = amps[i-1] * (1 + carry × weight)
        pred = amps[i-1] * (1 + carry * weight)
        predicted_amps_next.append(pred)

    prev_ratios = np.array(prev_ratios)
    next_ratios = np.array(next_ratios)
    phi_distances = np.array(phi_distances)
    actual_amps_next = np.array(actual_amps_next)
    predicted_amps_next = np.array(predicted_amps_next)

    # Test 1: does prev_ratio predict next_ratio?
    if np.std(prev_ratios) > 1e-9 and np.std(next_ratios) > 1e-9:
        ratio_corr = float(np.corrcoef(prev_ratios, next_ratios)[0,1])
    else: ratio_corr = 0

    # Test 2: does phi_distance predict whether next cycle is larger or smaller?
    # Direction: 1 if amps[i] > amps[i-1], -1 otherwise
    # Predicted: 1 if phi_distance > 0, -1 if < 0
    correct_dir = 0; total_dir = 0
    for pd_v, ar_next, ar_prev in zip(phi_distances, actual_amps_next, amps[1:n-1]):
        actual_d = 1 if ar_next > ar_prev else (-1 if ar_next < ar_prev else 0)
        pred_d = 1 if pd_v > 0 else -1
        if actual_d == 0: continue
        correct_dir += (actual_d == pred_d)
        total_dir += 1
    dir_acc = correct_dir / total_dir if total_dir else 0

    # Test 3: how well does 243AR's amplitude prediction track actual?
    if np.std(predicted_amps_next) > 1e-9:
        amp_corr = float(np.corrcoef(predicted_amps_next, actual_amps_next)[0,1])
    else: amp_corr = 0
    amp_rmse = float(np.sqrt(np.mean((predicted_amps_next - actual_amps_next)**2)))

    # Mean of phi_distances — is wave_ara typically near φ?
    mean_prev_ratio = float(np.mean(prev_ratios))

    print(f"\n  Mean prev_ratio (peak_i-1 / peak_i-2): {mean_prev_ratio:.3f} (φ = {PHI:.3f})")
    print(f"  T1: prev_ratio vs next_ratio correlation: {ratio_corr:+.3f}")
    print(f"  T2: phi_distance > 0 → next cycle amplifies? Direction acc: {dir_acc*100:.1f}%")
    print(f"  T3: 243AR amp prediction → corr {amp_corr:+.3f}, rmse {amp_rmse:.3f}")

    # Also test PERSISTENCE baseline (predict next = prev)
    pers_amp = amps[1:n-1]  # for n-2 elements
    pers_corr = float(np.corrcoef(pers_amp, actual_amps_next)[0,1]) if np.std(pers_amp) > 1e-9 else 0
    pers_rmse = float(np.sqrt(np.mean((pers_amp - actual_amps_next)**2)))
    print(f"  Persistence baseline: corr {pers_corr:+.3f}, rmse {pers_rmse:.3f}")

    return dict(
        mean_prev_ratio=mean_prev_ratio,
        ratio_corr=ratio_corr,
        direction_accuracy=dir_acc,
        n_dir_tested=total_dir,
        amp_pred_corr=amp_corr,
        amp_pred_rmse=amp_rmse,
        persistence_corr=pers_corr,
        persistence_rmse=pers_rmse,
        prev_ratios=prev_ratios.tolist(),
        next_ratios=next_ratios.tolist(),
        phi_distances=phi_distances.tolist(),
        actual_amps=actual_amps_next.tolist(),
        predicted_amps=predicted_amps_next.tolist(),
    )

heart_result = wave_ara_analysis(heart_amps, 'heart')

# === ENSO analysis ===
print("\n" + "=" * 60)
print("ENSO (φ⁸ ~47mo)")
print("=" * 60)
nino_amps = extract_cycle_amplitudes(v_nino, PHI**8, dt=1.0)
print(f"Cycles extracted: {len(nino_amps)}")
nino_result = wave_ara_analysis(nino_amps, 'ENSO')

# === Combined: also try using wave_ara as ADDITIONAL feature in direction predictor ===
# This requires lining up cycles with the v2 direction predictor's time series
# Simpler: just compute direction accuracy from wave_ara alone vs persistence

print("\n" + "=" * 60)
print("DIRECTION ACCURACY COMPARISON")
print("=" * 60)
print(f"For predicting whether next cycle's amplitude > current cycle's amplitude:")
print(f"  Wave-ARA carry  ENSO: {nino_result['direction_accuracy']*100:.1f}%")
print(f"  Wave-ARA carry  HEART: {heart_result['direction_accuracy']*100:.1f}%")

# Also compute: phi-distance correlation with NEXT amplitude change
def phi_dist_corr_with_change(amps):
    if len(amps) < 5: return None
    n = len(amps)
    pds = []
    delta_amps = []
    for i in range(2, n):
        prev_ratio = amps[i-1] / amps[i-2] if amps[i-2]>0 else 1.0
        delta = amps[i] - amps[i-1]
        pds.append(prev_ratio - PHI)
        delta_amps.append(delta)
    pds = np.array(pds); delta_amps = np.array(delta_amps)
    if np.std(pds)<1e-9 or np.std(delta_amps)<1e-9: return 0
    return float(np.corrcoef(pds, delta_amps)[0,1])

heart_pdcorr = phi_dist_corr_with_change(heart_amps)
nino_pdcorr = phi_dist_corr_with_change(nino_amps)
print(f"\nphi_distance vs next-amplitude-change correlation:")
print(f"  HEART: {heart_pdcorr:+.3f}")
print(f"  ENSO:  {nino_pdcorr:+.3f}")
print(f"  (positive → wave_ara > φ predicts amplification, < φ predicts dampening)")

# Save
out = dict(
    sources=dict(ecg="PhysioNet NSRDB nsr001", nino="NOAA PSL Nino 3.4 1870-2025"),
    heart=heart_result,
    nino=nino_result,
    phi_distance_corr_with_amp_change=dict(heart=heart_pdcorr, nino=nino_pdcorr),
    n_cycles=dict(heart=len(heart_amps), nino=len(nino_amps)),
)
with open(OUT,'w',encoding='utf-8') as f:
    f.write("window.WAVE_ARA = " + json.dumps(out, default=str) + ";\n")
print(f"\nSaved -> {OUT}")
