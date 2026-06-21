"""
morlet_vs_butterworth_test.py — does the filter choice affect framework results?

Dylan 2026-05-11: SOS Butterworth bandpass has sharp band edges and may suppress
broadband transients (snaps). Morlet wavelet has Gaussian frequency envelope —
better time localisation, captures more of a transient's spectral spread at
the dominant rung.

Test:
  1. Build causal Morlet bandpass: ψ(t) = exp(-t²/(2σ²)) × cos(ωt), applied
     via past-only convolution.
  2. Compare to Butterworth on three signals:
     a. Synthetic sinusoid + embedded sharp snap (controlled test)
     b. Real ECG (snap-class beats embedded)
     c. Real ENSO (continuous oscillator, baseline)
  3. Measure per-rung amplitude and ARA with each filter.
  4. Verdict: do framework results change materially?

If yes — Morlet should become the framework's standard for snap-sensitive
analyses. If no — Butterworth stays as the simpler default.
"""
import os, json, math
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfilt, find_peaks
from scipy.ndimage import gaussian_filter1d

PHI = (1 + 5**0.5) / 2


# ============================================================================
# CAUSAL FILTERS
# ============================================================================
def butter_bandpass(arr, period, bw=0.4, order=2):
    """Standard SOS Butterworth causal bandpass."""
    arr = np.asarray(arr, dtype=float)
    n = len(arr)
    f_c = 1.0 / period; nyq = 0.5
    Wn_lo = max(1e-6, (1-bw)*f_c/nyq); Wn_hi = min(0.999, (1+bw)*f_c/nyq)
    if Wn_lo >= Wn_hi: return np.zeros(n)
    sos = butter(order, [Wn_lo, Wn_hi], btype='bandpass', output='sos')
    return sosfilt(sos, arr - np.mean(arr))


def morlet_causal_bandpass(arr, period, n_cycles=4):
    """Causal Morlet wavelet bandpass.
       Morlet kernel: ψ(t) = exp(-t²/(2σ²)) × cos(2π t/period)
       σ chosen so the wavelet spans n_cycles cycles at the target period.
       Causal: convolved with past-only kernel (one-sided, window from -∞ to 0).
    """
    arr = np.asarray(arr, dtype=float) - np.mean(arr)
    n = len(arr)
    # Gaussian std σ such that the wavelet has n_cycles full cycles of the
    # target period within ±3σ (3-sigma containment).
    sigma = n_cycles * period / 6.0
    # Build a causal (one-sided, past-only) kernel of length ~ 6σ
    kernel_len = max(int(6 * sigma), 10)
    t_kernel = np.arange(kernel_len)
    # Wavelet centered at time 0, only past samples (so kernel is reversed)
    # For causal conv: kernel runs from t=0 (most recent past) backwards
    kernel = np.exp(-t_kernel**2 / (2 * sigma**2)) * np.cos(2*np.pi * t_kernel / period)
    # Normalise to unit energy
    kernel = kernel / max(1e-9, np.sqrt(np.sum(kernel**2)))
    # Causal convolution: output[i] = sum_{j=0..k-1} kernel[j] * arr[i-j]
    # Equivalent to full convolution then take first n samples
    out = np.zeros(n)
    for i in range(n):
        j_max = min(kernel_len, i+1)
        out[i] = float(np.dot(kernel[:j_max], arr[i-j_max+1:i+1][::-1]))
    return out


# ============================================================================
# ARA measurement (same for both filters)
# ============================================================================
def measure_amp(bp, period):
    p_int = max(2, int(period))
    if len(bp) < 2*p_int + 5: return None
    last_cycle = bp[-p_int:]
    return float((np.max(last_cycle) - np.min(last_cycle)) / 2.0)


def measure_ara_from_bp(bp, period):
    if len(bp) < 3 * int(period): return None
    smoothed = gaussian_filter1d(bp, max(1, int(period * 0.05)))
    peaks, _ = find_peaks(smoothed, distance=max(2, int(period * 0.7)))
    if len(peaks) < 2: return None
    aras = []
    for i in range(len(peaks)-1):
        seg = smoothed[peaks[i]:peaks[i+1]+1]
        if len(seg) < 3: continue
        f_t = max(0.15, min(0.85, int(np.argmin(seg)) / max(1, len(seg)-1)))
        aras.append((1 - f_t) / f_t)
    if not aras: return None
    return float(np.mean(np.clip(aras, 0.3, 3.0)))


# ============================================================================
# 1. SYNTHETIC TEST: sinusoid + embedded snap
# ============================================================================
print('=' * 78)
print('TEST 1: Synthetic — clean sinusoid + embedded sharp snap')
print('=' * 78)

np.random.seed(42)
n = 2000
t = np.arange(n)
# Clean sinusoid at period 64
period_carrier = 64.0
clean = np.sin(2*np.pi * t / period_carrier)
# Add a sharp snap at t=1000: a fast spike (exponential decay)
snap_t = 1000
snap_width = 5
snap = np.zeros(n)
snap[snap_t:snap_t+50] = 3.0 * np.exp(-np.arange(50) / snap_width)
signal_1 = clean + snap + 0.1*np.random.randn(n)

print(f'Carrier period: {period_carrier}, snap at t={snap_t}, width ~ {snap_width} samples')
print()
print(f"{'rung':>5}  {'period':>9}  {'butter_amp':>12}  {'morlet_amp':>12}  {'butter_ara':>11}  {'morlet_ara':>11}")
print('-' * 75)
results_1 = []
for k in range(2, 12):
    p = PHI ** k
    if 4*p > n: break
    bp_b = butter_bandpass(signal_1, p)
    bp_m = morlet_causal_bandpass(signal_1, p)
    a_b = measure_amp(bp_b, p); a_m = measure_amp(bp_m, p)
    ar_b = measure_ara_from_bp(bp_b, p); ar_m = measure_ara_from_bp(bp_m, p)
    results_1.append(dict(k=k, period=float(p), butter_amp=a_b, morlet_amp=a_m,
                          butter_ara=ar_b, morlet_ara=ar_m))
    print(f"  {k:>3}  {p:>9.2f}  {a_b or 0:>12.3f}  {a_m or 0:>12.3f}  "
          f"{ar_b or 0:>11.3f}  {ar_m or 0:>11.3f}")

# Compute ratio: morlet/butter amplitude per rung
ratios = [(r['morlet_amp'] / r['butter_amp']) for r in results_1
          if r['morlet_amp'] and r['butter_amp']]
if ratios:
    print(f'\n  Mean morlet/butter amplitude ratio: {np.mean(ratios):.3f}')
print(f'  Carrier rung k = {round(math.log(period_carrier)/math.log(PHI))}')

# ============================================================================
# 2. ECG TEST
# ============================================================================
print()
print('=' * 78)
print('TEST 2: Real ECG (BIDMC subject 01, II-lead, ~1 minute)')
print('=' * 78)
try:
    import wfdb
    r = wfdb.rdrecord('bidmc01', pn_dir='bidmc', sampto=7500)
    ii_idx = next((j for j,n in enumerate(r.sig_name) if n.startswith('II')), None)
    ecg = r.p_signal[:, ii_idx]
    fs = r.fs
    print(f'  Loaded {len(ecg)} samples at {fs} Hz')

    print(f"\n{'rung':>5}  {'period_s':>10}  {'butter_amp':>12}  {'morlet_amp':>12}  {'butter_ara':>11}  {'morlet_ara':>11}")
    print('-' * 80)
    for k in range(0, 12):
        p = PHI ** k  # samples
        if 4*p > len(ecg) or p < 2: continue
        bp_b = butter_bandpass(ecg, p)
        bp_m = morlet_causal_bandpass(ecg, p)
        a_b = measure_amp(bp_b, p); a_m = measure_amp(bp_m, p)
        ar_b = measure_ara_from_bp(bp_b, p); ar_m = measure_ara_from_bp(bp_m, p)
        if a_b is None and a_m is None: continue
        print(f"  {k:>3}  {p/fs:>10.4f}  {a_b or 0:>12.3f}  {a_m or 0:>12.3f}  "
              f"{ar_b or 0:>11.3f}  {ar_m or 0:>11.3f}")
except Exception as e:
    print(f'  ECG test skipped: {e}')

# ============================================================================
# 3. ENSO TEST (continuous oscillator baseline — no snaps)
# ============================================================================
print()
print('=' * 78)
print('TEST 3: ENSO (continuous oscillator — baseline, no snaps)')
print('=' * 78)
try:
    df = pd.read_csv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   'Nino34', 'nino34.long.anom.csv'),
                     skiprows=1, names=['d','v'], header=None, sep=',', engine='python')
    nino = pd.to_numeric(df['v'], errors='coerce').dropna().values.astype(float)
    nino = nino[nino > -50]
    print(f'  Loaded {len(nino)} months')

    print(f"\n{'rung':>5}  {'period_mo':>10}  {'butter_amp':>12}  {'morlet_amp':>12}  {'butter_ara':>11}  {'morlet_ara':>11}")
    print('-' * 80)
    for k in range(2, 14):
        p = PHI ** k
        if 4*p > len(nino) or p < 2: continue
        bp_b = butter_bandpass(nino, p)
        bp_m = morlet_causal_bandpass(nino, p)
        a_b = measure_amp(bp_b, p); a_m = measure_amp(bp_m, p)
        ar_b = measure_ara_from_bp(bp_b, p); ar_m = measure_ara_from_bp(bp_m, p)
        if a_b is None and a_m is None: continue
        print(f"  {k:>3}  {p:>10.2f}  {a_b or 0:>12.3f}  {a_m or 0:>12.3f}  "
              f"{ar_b or 0:>11.3f}  {ar_m or 0:>11.3f}")
except Exception as e:
    print(f'  ENSO test skipped: {e}')

# Save
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'morlet_vs_butterworth_data.js')
with open(OUT, 'w') as f:
    f.write("window.MORLET_VS_BUTTERWORTH = " + json.dumps({
        'date': '2026-05-11',
        'synthetic_test': results_1,
        'method_butter': 'SOS Butterworth, order 2, bandwidth 0.4 (40% of center freq)',
        'method_morlet': 'Causal Morlet wavelet, 4 cycles span, Gaussian envelope σ=4*period/6',
    }, default=str) + ";\n")
print(f'\nSaved -> {OUT}')
