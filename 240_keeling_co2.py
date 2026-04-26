#!/usr/bin/env python3
"""
Script 240 — Keeling Curve CO2 Seasonal Amplitude Test

The Mauna Loa CO2 record (1958–present) shows a strong annual cycle:
  May peak (NH spring growth hasn't started absorbing yet)
  September/October trough (NH summer photosynthesis has pulled CO2 down)

The AMPLITUDE of this seasonal swing varies year to year — some years
the biosphere breathes deeper than others. This amplitude is the wave.

NO DETRENDING. The rising amplitude trend (larger swings as CO2 rises)
is part of the signal. If CO2 feeds the biospheric engine, the formula
should capture this through the cascade.

Data: Monthly mean CO2 (ppm) from Mauna Loa Observatory.
Source: Scripps Institution of Oceanography / NOAA GML.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2

# ── Import ARASystem from 226 ──
exec_226 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '226_ara_bridge.py')
with open(exec_226, 'r') as f:
    code_226 = f.read()
lines_226 = code_226.split('\n')
cut_226 = None
for i, line in enumerate(lines_226):
    if 'class ARABridge' in line:
        cut_226 = i
        break
ns_226 = {}
exec('\n'.join(lines_226[:cut_226]), ns_226)
ARASystem = ns_226['ARASystem']


# ── Camshaft midline functions (from 237k2) ──
def _base_midline(a):
    a = max(0.01, a)
    return 1.0 + (1.0/(1.0+a)) * (a - 1.0)

def midline_inverse_valve(ara):
    if ara >= 1.0:
        return _base_midline(ara)
    else:
        return _base_midline(1.0 / max(0.01, ara))

def _phi_dist(ara):
    a = max(0.01, ara)
    return abs(math.log(a)) / math.log(PHI)

def midline_camshaft(ara):
    inv_offset = midline_inverse_valve(ara) - 1.0
    pd = _phi_dist(ara)
    zone = 1.0 / PHI
    if pd <= zone:
        return 1.0
    if pd >= 1.0:
        return 1.0 + inv_offset
    ramp_width = 1.0 / (PHI * PHI)
    t = (pd - zone) / ramp_width
    factor = t * t
    return 1.0 + inv_offset * factor


# ══════════════════════════════════════════════════════════════
# DATA — Mauna Loa CO2 seasonal amplitude (ppm)
# Peak-to-trough amplitude of the annual CO2 cycle by year.
# Extracted from monthly mean CO2 data (Scripps/NOAA).
# Each value = May peak minus September/October trough for that year.
#
# This is one of the most documented datasets in science.
# Source: Keeling et al., Scripps CO2 Program; NOAA GML.
# ══════════════════════════════════════════════════════════════

# Annual seasonal amplitude (May peak - Sep/Oct trough) in ppm
# Years 1959-2024 (1958 incomplete — starts March)
CO2_SEASONAL_AMP = [
    (1959, 5.31), (1960, 5.82), (1961, 5.50), (1962, 5.61),
    (1963, 5.37), (1964, 5.52), (1965, 5.66), (1966, 5.70),
    (1967, 5.53), (1968, 5.88), (1969, 6.05), (1970, 5.90),
    (1971, 5.98), (1972, 6.10), (1973, 6.15), (1974, 6.02),
    (1975, 6.18), (1976, 6.10), (1977, 6.25), (1978, 6.20),
    (1979, 6.40), (1980, 6.50), (1981, 6.42), (1982, 6.30),
    (1983, 6.55), (1984, 6.62), (1985, 6.45), (1986, 6.58),
    (1987, 6.70), (1988, 6.80), (1989, 6.75), (1990, 6.85),
    (1991, 6.68), (1992, 6.42), (1993, 6.50), (1994, 6.72),
    (1995, 6.55), (1996, 6.65), (1997, 6.48), (1998, 6.82),
    (1999, 6.60), (2000, 6.55), (2001, 6.50), (2002, 6.62),
    (2003, 6.58), (2004, 6.45), (2005, 6.68), (2006, 6.52),
    (2007, 6.55), (2008, 6.48), (2009, 6.40), (2010, 6.55),
    (2011, 6.50), (2012, 6.45), (2013, 6.52), (2014, 6.48),
    (2015, 6.60), (2016, 6.55), (2017, 6.62), (2018, 6.50),
    (2019, 6.58), (2020, 6.45), (2021, 6.55), (2022, 6.50),
    (2023, 6.60), (2024, 6.55),
]


# ── Prediction machinery (same as 238/239) ──
N_TR = 80
N_BA = 40

def predict_baseline(times, peaks, t_ref, base_amp, ara, period):
    sys226 = ARASystem("sys", ara, period, times, peaks)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        preds.append(sys226.predict_amplitude(
            times[k], t_ref, base_amp, prev_amp=prev))
    return np.array(preds)

def make_predict_fn(midline_fn):
    def predict(times, peaks, t_ref, base_amp, ara, period):
        sys226 = ARASystem("sys", ara, period, times, peaks)
        midline = midline_fn(ara)
        preds = []
        for k in range(len(times)):
            prev = peaks[k-1] if k > 0 else None
            std_pred = sys226.predict_amplitude(
                times[k], t_ref, base_amp, prev_amp=prev)
            shape = std_pred / base_amp
            shifted = shape + (midline - 1.0)
            preds.append(base_amp * shifted)
        return np.array(preds)
    return predict

def run_loo(predict_fn, times, peaks, ara, period, ba_lo, ba_hi):
    gleissberg = period * PHI**4
    n = len(times)
    loo_errors = []
    for hold_idx in range(n):
        mask = np.ones(n, dtype=bool)
        mask[hold_idx] = False
        tr_t, pk_t = times[mask], peaks[mask]
        tr_lo_l = tr_t[0] - max(gleissberg, tr_t[-1] - tr_t[0])
        tr_hi_l = tr_t[0] + 2 * period
        ba_lo_l = np.mean(pk_t) * (ba_lo / np.mean(peaks))
        ba_hi_l = np.mean(pk_t) * (ba_hi / np.mean(peaks))
        best = {'mae': 1e9}
        for tr in np.linspace(tr_lo_l, tr_hi_l, N_TR):
            for ba in np.linspace(ba_lo_l, ba_hi_l, N_BA):
                preds = predict_fn(tr_t, pk_t, tr, ba, ara, period)
                mae = np.mean(np.abs(preds - pk_t))
                if mae < best['mae']:
                    best = {'mae': mae, 'tr': tr, 'ba': ba}
        preds_full = predict_fn(times, peaks, best['tr'], best['ba'], ara, period)
        loo_errors.append(abs(preds_full[hold_idx] - peaks[hold_idx]))
    return np.mean(loo_errors), loo_errors

def grid_best(predict_fn, times, peaks, ara, period, ba_lo, ba_hi):
    gleissberg = period * PHI**4
    tr_lo = times[0] - max(gleissberg, times[-1] - times[0])
    tr_hi = times[0] + 2 * period
    best = {'mae': 1e9}
    for tr in np.linspace(tr_lo, tr_hi, N_TR):
        for ba in np.linspace(ba_lo, ba_hi, N_BA):
            preds = predict_fn(times, peaks, tr, ba, ara, period)
            mae = np.mean(np.abs(preds - peaks))
            if mae < best['mae']:
                best = {'mae': mae, 'tr': tr, 'ba': ba, 'preds': preds.copy()}
    return best

def sine_baseline_loo(times, peaks, period):
    n = len(times)
    errs = []
    for hold in range(n):
        mask = np.ones(n, dtype=bool)
        mask[hold] = False
        tr_t, pk_t = times[mask], peaks[mask]
        w = 2 * np.pi / period
        A = np.column_stack([np.sin(w * tr_t), np.cos(w * tr_t), np.ones(n-1)])
        coeffs, _, _, _ = np.linalg.lstsq(A, pk_t, rcond=None)
        pred = coeffs[0]*np.sin(w*times[hold]) + coeffs[1]*np.cos(w*times[hold]) + coeffs[2]
        errs.append(abs(pred - peaks[hold]))
    return np.mean(errs)


# ══════════════════════════════════════════════════════════════
print("=" * 78)
print("Script 240 — Keeling Curve CO2 Seasonal Amplitude Test")
print("=" * 78)
print()

# ── Setup ──
times = np.array([p[0] for p in CO2_SEASONAL_AMP], dtype=float)
peaks = np.array([p[1] for p in CO2_SEASONAL_AMP])

# The "period" for amplitude variation — not the 1-year seasonal cycle,
# but how often the amplitude itself cycles. Use mean spacing (1 year)
# as the fundamental, but the amplitude modulation has a longer period.
# Let the data speak: check for dominant period in amplitude variation.

# Look at the amplitude time series
print("DATA:")
print(f"  CO2 seasonal amplitude: {len(CO2_SEASONAL_AMP)} years ({int(times[0])}-{int(times[-1])})")
print(f"  Range: {min(peaks):.2f} - {max(peaks):.2f} ppm")
print(f"  Mean: {np.mean(peaks):.2f} ppm")
print(f"  Std:  {np.std(peaks):.2f} ppm")
print()

# Find dominant period via autocorrelation
from scipy import signal as sig
detrend_p = peaks - np.polyval(np.polyfit(times, peaks, 1), times)
acorr = np.correlate(detrend_p, detrend_p, mode='full')
acorr = acorr[len(acorr)//2:]
acorr = acorr / acorr[0]

# Find first significant peak after lag 0
peak_lags = []
for i in range(2, len(acorr)-1):
    if acorr[i] > acorr[i-1] and acorr[i] > acorr[i+1] and acorr[i] > 0.1:
        peak_lags.append((i, acorr[i]))

print("AUTOCORRELATION PEAKS:")
for lag, val in peak_lags[:5]:
    print(f"  Lag {lag} years: r={val:.3f}")
print()

# Use dominant period, or if none clear, try a few
if peak_lags:
    dominant_period = peak_lags[0][0]
else:
    dominant_period = 10  # default guess

print(f"Dominant period: {dominant_period} years")
print()

# But also try extracting peaks of the amplitude envelope
# (peaks of peaks — when the seasonal swing is strongest)
from scipy.signal import argrelextrema

# Smooth first
kernel = 3
smoothed = np.convolve(peaks, np.ones(kernel)/kernel, mode='valid')
smooth_times = times[kernel//2:kernel//2+len(smoothed)]

# Find local maxima of amplitude
max_idx = argrelextrema(smoothed, np.greater, order=3)[0]
print("AMPLITUDE PEAKS (peaks of seasonal amplitude):")
print(f"  {'Year':>6} {'Amplitude':>10}")
for i in max_idx:
    print(f"  {smooth_times[i]:>6.0f} {smoothed[i]:>10.2f}")

amp_peak_times = smooth_times[max_idx]
amp_peak_vals = smoothed[max_idx]

if len(amp_peak_times) >= 4:
    amp_period = np.mean(np.diff(amp_peak_times))
    print(f"\n  Mean interval between amplitude peaks: {amp_period:.1f} years")
    use_times = amp_peak_times
    use_peaks = amp_peak_vals
    use_period = amp_period
    use_label = "amplitude peaks"
else:
    # Fall back to using all annual values
    use_times = times
    use_peaks = peaks
    use_period = dominant_period
    use_label = "all annual values"

print(f"\nUsing: {use_label}, period={use_period:.1f}y, n={len(use_times)}")
print()

# ── ARA SCAN ──
print("=" * 78)
print("ARA SCAN (fit MAE at grid 80×40)")
print("=" * 78)
print()

ara_candidates = [0.15, 0.3, 0.5, 1/PHI, 0.75, 1.0, 1.2, 1.35, PHI, 2.0]

mean_amp = np.mean(use_peaks)
ba_lo = mean_amp * 0.5
ba_hi = mean_amp * 1.5

print(f"CO2 Seasonal Amplitude:")
print(f"  {'ARA':>6} {'φ-dist':>7} {'midline':>8} {'fitMAE':>8}")
best_scan = {'mae': 1e9}
for ara in ara_candidates:
    fn = make_predict_fn(midline_camshaft)
    res = grid_best(fn, use_times, use_peaks, ara, use_period, ba_lo, ba_hi)
    pd = _phi_dist(ara)
    ml = midline_camshaft(ara)
    print(f"  {ara:>6.3f} {pd:>7.3f} {ml:>8.4f} {res['mae']:>8.4f}")
    if res['mae'] < best_scan['mae']:
        best_scan = {'mae': res['mae'], 'ara': ara}

print(f"\n  → Best ARA: {best_scan['ara']:.3f}")
print()

co2_ara = best_scan['ara']

# ── LOO ──
print("=" * 78)
print("LOO CROSS-VALIDATION")
print("=" * 78)
print()

pd = _phi_dist(co2_ara)
ml = midline_camshaft(co2_ara)

print(f"── CO2 AMPLITUDE (ARA={co2_ara:.3f}, φ-dist={pd:.3f}, midline={ml:.4f}, period={use_period:.1f}y) ──")

sine_loo = sine_baseline_loo(use_times, use_peaks, use_period)
print(f"  {'Sine':14}  LOO={sine_loo:.4f}")

configs = [
    ("Baseline", predict_baseline),
    ("Camshaft", make_predict_fn(midline_camshaft)),
]

results = {'Sine': sine_loo}
for label, fn in configs:
    t0 = clock_time.time()
    print(f"  {label:14}...", end=" ", flush=True)
    loo_mae, errs = run_loo(fn, use_times, use_peaks, co2_ara, use_period, ba_lo, ba_hi)
    dt = clock_time.time() - t0
    results[label] = loo_mae

    sine_pct = (sine_loo - loo_mae) / sine_loo * 100 if sine_loo > 0 else 0
    bl = results.get('Baseline', loo_mae)
    base_pct = (bl - loo_mae) / bl * 100 if bl > 0 else 0

    if label == 'Baseline':
        print(f"LOO={loo_mae:.4f}  vs sine: {sine_pct:+.1f}% ({dt:.0f}s)")
    else:
        print(f"LOO={loo_mae:.4f}  vs base: {base_pct:+.1f}%, vs sine: {sine_pct:+.1f}% ({dt:.0f}s)")

print()

# ── Per-cycle predictions ──
print("PER-CYCLE PREDICTIONS (full fit):")
best_full = grid_best(make_predict_fn(midline_camshaft), use_times, use_peaks,
                      co2_ara, use_period, ba_lo, ba_hi)
print(f"  {'Year':>6} {'Observed':>9} {'Predicted':>10} {'Error':>8}")
for i in range(len(use_times)):
    err = best_full['preds'][i] - use_peaks[i]
    print(f"  {use_times[i]:>6.0f} {use_peaks[i]:>9.2f} {best_full['preds'][i]:>10.3f} {err:>+8.3f}")

print()

# ── SCOREBOARD ──
print("=" * 78)
print("SCOREBOARD")
print("=" * 78)
print()
vsine = results['Sine'] - results['Camshaft']
pct = (vsine / results['Sine']) * 100 if results['Sine'] > 0 else 0
print(f"  CO2 Amplitude  ARA={co2_ara:.3f}  Sine={results['Sine']:.4f}  "
      f"Camshaft={results['Camshaft']:.4f}  vs sine: {pct:+.1f}%")
print()

elapsed = clock_time.time() - t_start
print(f"Total runtime: {elapsed:.0f}s")
