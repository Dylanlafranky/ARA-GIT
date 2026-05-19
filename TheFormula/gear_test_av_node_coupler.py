"""gear_test_av_node_coupler.py — Dylan 2026-05-12. v2 fix R baseline."""
import os, math
import numpy as np
import pandas as pd
from scipy.signal import find_peaks, butter, sosfiltfilt

_HERE = os.path.dirname(os.path.abspath(__file__))
def log(s): print(s, flush=True)

df = pd.read_csv(os.path.join(_HERE, 'bidmc01_ecg.csv'))
ecg = df.iloc[:, 0].values
FS = 125
log(f'ECG: {len(ecg)} samples = {len(ecg)/FS:.1f} sec at {FS} Hz')

sos = butter(4, 0.5 / (FS/2), btype='high', output='sos')
ecg_hp = sosfiltfilt(sos, ecg)

r_threshold = np.percentile(ecg_hp, 95) * 0.6
min_distance = int(0.4 * FS)
r_peaks, _ = find_peaks(ecg_hp, height=r_threshold, distance=min_distance)
log(f'R-peaks: {len(r_peaks)} (mean HR = {60 * FS * len(r_peaks) / len(ecg):.1f} bpm)')

# Sample offsets
P_SEARCH_START = int(0.20 * FS)  # 25 samples = 200 ms before R
P_SEARCH_END = int(0.08 * FS)    # 10 samples = 80 ms before R
R_BASELINE_BACK = int(0.30 * FS)  # 37 samples = 300 ms before R
R_BASELINE_FRONT = int(0.20 * FS)  # 25 samples = 200 ms before R (start of P search)

p_amps = []; r_amps = []; pr_ratios = []; pr_intervals = []

for ri in r_peaks:
    if ri - R_BASELINE_BACK < 0: continue
    if ri + 5 >= len(ecg_hp): continue
    
    # P-wave window
    p_window = ecg_hp[ri - P_SEARCH_START : ri - P_SEARCH_END]
    if len(p_window) < 5: continue
    p_baseline = np.median(p_window)
    p_amp = p_window.max() - p_baseline
    
    # R-wave: peak minus baseline taken from 300-200ms before R (clean isoelectric)
    r_baseline_window = ecg_hp[ri - R_BASELINE_BACK : ri - R_BASELINE_FRONT]
    if len(r_baseline_window) < 5: continue
    r_baseline = np.median(r_baseline_window)
    r_amp = ecg_hp[ri] - r_baseline
    if r_amp <= 0: continue
    
    p_peak_idx = np.argmax(p_window) + (ri - P_SEARCH_START)
    pr_interval_ms = (ri - p_peak_idx) / FS * 1000
    
    p_amps.append(p_amp)
    r_amps.append(r_amp)
    pr_ratios.append(p_amp / r_amp)
    pr_intervals.append(pr_interval_ms)

p_amps = np.array(p_amps); r_amps = np.array(r_amps); pr_ratios = np.array(pr_ratios); pr_intervals = np.array(pr_intervals)

log(f'\nUsable beats: {len(p_amps)} / {len(r_peaks)}')
log(f'')
log(f'P-wave amp (atrial gear output):     mean {p_amps.mean():.4f} mV, median {np.median(p_amps):.4f} mV')
log(f'R-wave amp (ventricular gear output): mean {r_amps.mean():.4f} mV, median {np.median(r_amps):.4f} mV')
log(f'')
log(f'=== P/R amplitude ratio (AV node gear transfer) ===')
log(f'  mean:   {pr_ratios.mean():.4f}')
log(f'  median: {np.median(pr_ratios):.4f}')
log(f'  std:    {pr_ratios.std():.4f}')
log(f'  CV:     {pr_ratios.std()/pr_ratios.mean():.3f}')
log(f'')
log(f'PR interval: mean {pr_intervals.mean():.1f} ms, std {pr_intervals.std():.1f} ms  (clinical norm 120-200ms)')
log(f'')
log(f'=== FRAMEWORK INTERPRETATION ===')
log(f'Clinical norm P/R ≈ 0.1 (P ~0.1mV, R ~1mV)')
log(f'Measured: {pr_ratios.mean():.3f}')
log(f'')
log(f'If AV node were pure π-leak friction: predicted P/R ≈ 0.955')
log(f'  Measured {pr_ratios.mean():.3f} is MUCH lower → AV node is NOT pure friction.')
log(f'')
log(f'AV node as sized intermediate gear: ratio 1:{1/pr_ratios.mean():.1f}')
log(f'  (small atrial input → {1/pr_ratios.mean():.1f}× larger ventricular output)')
log(f'')
log(f'Stability (CV {pr_ratios.std()/pr_ratios.mean():.3f}):')
if pr_ratios.std()/pr_ratios.mean() < 0.3:
    log(f'  ✓ STABLE coupler — consistent with framework "structural coupler" claim')
elif pr_ratios.std()/pr_ratios.mean() < 0.6:
    log(f'  ~ Moderately variable')
else:
    log(f'  ✗ Highly variable')

log(f'')
log(f'PR interval CV = {pr_intervals.std()/pr_intervals.mean():.3f}')
log(f'PR interval and P/R ratio correlation: {np.corrcoef(pr_intervals, pr_ratios)[0,1]:+.3f}')
log(f'  Framework would predict: longer PR → more attenuation if AV node is a coupler with delay-dependent loss')
log(f'  (Negative correlation = more delay means MORE attenuation = supports framework)')

log('\n=== Done ===')
