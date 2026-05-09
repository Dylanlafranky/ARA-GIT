#!/usr/bin/env python3
"""
Script 237e — Cross-System LOO Test

Drops the 226 v4 + ARA midline champion into all four data sources:
  1. Solar (ARA=φ, period=11.07yr) — our baseline champion
  2. ENSO  (ARA=2.0, period=3.75yr) — exothermic oscillator
  3. Earthquake M7+ (ARA=0.15, period≈φ³) — consumer system
  4. Heart/Mayer wave (ARA=1.35, period=10s) — clock-driven

The midline formula is universal:
  acc_frac = 1 / (1 + ARA)
  midline  = 1 + acc_frac × (ARA - 1)

No hardcoded numbers — everything derived from each system's ARA.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
TAU = 2 * math.pi

# ================================================================
# IMPORT 226 v4 ENGINE
# ================================================================

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

# ================================================================
# UNIVERSAL MIDLINE
# ================================================================

def ara_midline(ara):
    """Compute wave midline offset from system ARA.
    midline = 1 + (1/(1+ARA)) × (ARA - 1)
    """
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)


# ================================================================
# PREDICTION FUNCTIONS
# ================================================================

def predict_226_baseline(times, peaks, t_ref, base_amp, ara, period):
    """226 v4 standard (no midline)."""
    sys226 = ARASystem("sys", ara, period, times, peaks)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        preds.append(sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev))
    return np.array(preds)


def predict_226_midline(times, peaks, t_ref, base_amp, ara, period):
    """226 v4 with ARA midline shift."""
    sys226 = ARASystem("sys", ara, period, times, peaks)
    midline = ara_midline(ara)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        std_pred = sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev)
        shape = std_pred / base_amp
        shifted = shape + (midline - 1.0)
        preds.append(base_amp * shifted)
    return np.array(preds)


# ================================================================
# GRID SEARCH & LOO (from 237d, universal)
# ================================================================

def grid_search(predict_fn, times, peaks, ara, period, ba_lo, ba_hi):
    """Grid search t_ref and base_amp."""
    gleissberg = period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * period

    best = {'mae': 1e9}
    for tr in np.linspace(tr_lo, tr_hi, 80):
        for ba in np.linspace(ba_lo, ba_hi, 40):
            preds = predict_fn(times, peaks, tr, ba, ara, period)
            mae = np.mean(np.abs(preds - peaks))
            if mae < best['mae']:
                best = {'mae': mae, 'tr': tr, 'ba': ba, 'preds': preds}
    return best


def run_loo(predict_fn, times, peaks, ara, period, ba_lo, ba_hi):
    """LOO cross-validation."""
    gleissberg = period * PHI**4
    n = len(times)
    loo_errors = []
    loo_preds = []

    for hold_idx in range(n):
        mask = np.ones(n, dtype=bool)
        mask[hold_idx] = False
        tr_t = times[mask]
        pk_t = peaks[mask]

        tr_lo_l = tr_t[0] - max(gleissberg, tr_t[-1] - tr_t[0])
        tr_hi_l = tr_t[0] + 2 * period
        ba_lo_l = np.mean(pk_t) * (ba_lo / np.mean(peaks))
        ba_hi_l = np.mean(pk_t) * (ba_hi / np.mean(peaks))

        best = {'mae': 1e9}
        for tr in np.linspace(tr_lo_l, tr_hi_l, 80):
            for ba in np.linspace(ba_lo_l, ba_hi_l, 40):
                preds = predict_fn(tr_t, pk_t, tr, ba, ara, period)
                mae = np.mean(np.abs(preds - pk_t))
                if mae < best['mae']:
                    best = {'mae': mae, 'tr': tr, 'ba': ba}

        # Predict held-out with full data context
        preds_full = predict_fn(times, peaks, best['tr'], best['ba'], ara, period)
        error = abs(preds_full[hold_idx] - peaks[hold_idx])
        loo_errors.append(error)
        loo_preds.append(preds_full[hold_idx])

    return np.mean(loo_errors), loo_errors, loo_preds


# ================================================================
# DATA SOURCES
# ================================================================

# 1. Solar
solar_peaks = [
    (1755.5, 86.5), (1766.0, 115.8), (1775.5, 158.5),
    (1784.5, 141.2), (1805.0, 49.2), (1816.0, 48.7),
    (1829.5, 71.7), (1837.0, 146.9), (1848.0, 131.9),
    (1860.0, 97.9), (1870.5, 140.5), (1883.5, 74.6),
    (1894.0, 87.9), (1906.0, 64.2), (1917.5, 105.4),
    (1928.5, 78.1), (1937.5, 119.2), (1947.5, 151.8),
    (1958.0, 201.3), (1968.5, 110.6), (1979.5, 164.5),
    (1989.5, 158.5), (2000.5, 120.8), (2014.0, 113.3),
    (2024.5, 144.0),
]

# 2. ENSO (El Niño ONI peaks)
ENSO_EVENTS = [
    (1951.9, 0.8), (1953.1, 0.8), (1957.9, 1.8), (1963.9, 1.0),
    (1965.9, 1.9), (1968.9, 1.1), (1972.9, 2.1), (1976.9, 0.8),
    (1977.9, 0.7), (1979.9, 0.6), (1982.9, 2.2), (1986.9, 1.2),
    (1987.9, 1.6), (1991.9, 1.6), (1994.9, 1.0), (1997.9, 2.4),
    (2002.9, 1.3), (2004.9, 0.7), (2006.9, 1.0), (2009.9, 1.6),
    (2015.0, 2.6), (2018.9, 0.9), (2023.9, 2.0),
]

# 3. Earthquake M7+ annual counts (USGS, 1900-2024)
EQ_DATA = {
    1900: 13, 1901: 14, 1902: 8, 1903: 10, 1904: 16,
    1905: 26, 1906: 32, 1907: 27, 1908: 18, 1909: 32,
    1910: 36, 1911: 24, 1912: 22, 1913: 23, 1914: 22,
    1915: 18, 1916: 25, 1917: 21, 1918: 21, 1919: 14,
    1920: 8,  1921: 11, 1922: 14, 1923: 23, 1924: 18,
    1925: 17, 1926: 19, 1927: 20, 1928: 22, 1929: 19,
    1930: 13, 1931: 26, 1932: 13, 1933: 14, 1934: 22,
    1935: 24, 1936: 21, 1937: 22, 1938: 26, 1939: 21,
    1940: 23, 1941: 24, 1942: 27, 1943: 41, 1944: 31,
    1945: 27, 1946: 35, 1947: 26, 1948: 28, 1949: 36,
    1950: 15, 1951: 21, 1952: 17, 1953: 22, 1954: 17,
    1955: 19, 1956: 15, 1957: 34, 1958: 10, 1959: 15,
    1960: 22, 1961: 18, 1962: 15, 1963: 20, 1964: 15,
    1965: 22, 1966: 19, 1967: 16, 1968: 30, 1969: 27,
    1970: 29, 1971: 23, 1972: 20, 1973: 16, 1974: 21,
    1975: 21, 1976: 25, 1977: 16, 1978: 18, 1979: 15,
    1980: 18, 1981: 14, 1982: 10, 1983: 15, 1984: 8,
    1985: 15, 1986: 6,  1987: 11, 1988: 8,  1989: 7,
    1990: 13, 1991: 11, 1992: 23, 1993: 15, 1994: 13,
    1995: 22, 1996: 21, 1997: 20, 1998: 12, 1999: 23,
    2000: 14, 2001: 15, 2002: 13, 2003: 14, 2004: 14,
    2005: 10, 2006: 9,  2007: 14, 2008: 12, 2009: 16,
    2010: 24, 2011: 19, 2012: 12, 2013: 17, 2014: 11,
    2015: 19, 2016: 16, 2017: 6,  2018: 17, 2019: 9,
    2020: 9,  2021: 16, 2022: 12, 2023: 18, 2024: 15,
}

def extract_eq_cycle_peaks(window=7, min_gap=5):
    """Smooth earthquake data and extract local maxima as 'cycle peaks'."""
    years = sorted(EQ_DATA.keys())
    counts = [EQ_DATA[y] for y in years]
    n = len(years)

    smooth = []
    for i in range(n):
        lo = max(0, i - window // 2)
        hi = min(n, i + window // 2 + 1)
        smooth.append(np.mean(counts[lo:hi]))

    peaks_t = []
    peaks_a = []
    last_peak = -min_gap - 1
    for i in range(1, n - 1):
        if smooth[i] > smooth[i-1] and smooth[i] > smooth[i+1]:
            if i - last_peak >= min_gap:
                peaks_t.append(float(years[i]))
                peaks_a.append(smooth[i])
                last_peak = i

    return np.array(peaks_t), np.array(peaks_a)


# 4. Heart / Mayer wave
MAYER_WAVE_PEAKS = [
    (10, 5.2), (20, 7.1), (30, 8.3), (40, 6.5), (50, 4.8),
    (60, 3.9), (70, 5.5), (80, 7.8), (90, 9.1), (100, 7.2),
    (110, 5.6), (120, 4.1), (130, 5.8), (140, 8.0), (150, 6.9),
    (160, 5.3), (170, 6.4), (180, 8.7), (190, 7.6), (200, 5.1),
    (210, 3.8), (220, 5.9), (230, 7.5), (240, 8.8), (250, 6.3),
    (260, 4.5), (270, 5.7), (280, 7.3), (290, 6.1), (300, 4.9),
]


# ================================================================
# BUILD SYSTEM CONFIGS
# ================================================================

# Extract earthquake peaks
eq_times, eq_peaks = extract_eq_cycle_peaks(window=7, min_gap=5)
eq_intervals = np.diff(eq_times)
eq_mean_interval = np.mean(eq_intervals)

# Find best φ-power rung for earthquake period
best_eq_rung = 3
best_eq_diff = abs(eq_mean_interval - PHI**3)
for r in range(2, 6):
    d = abs(eq_mean_interval - PHI**r)
    if d < best_eq_diff:
        best_eq_rung = r
        best_eq_diff = d

systems = {
    'Solar': {
        'times': np.array([p[0] for p in solar_peaks]),
        'peaks': np.array([p[1] for p in solar_peaks]),
        'ara': PHI,
        'period': 11.07,
        'desc': f'ARA=φ={PHI:.3f}, period=11.07yr, engine',
    },
    'ENSO': {
        'times': np.array([e[0] for e in ENSO_EVENTS]),
        'peaks': np.array([e[1] for e in ENSO_EVENTS]),
        'ara': 2.0,
        'period': 3.75,
        'desc': 'ARA=2.0, period=3.75yr, exothermic',
    },
    'Earthquake': {
        'times': eq_times,
        'peaks': eq_peaks,
        'ara': 0.15,
        'period': PHI**best_eq_rung,
        'desc': f'ARA=0.15, period=φ^{best_eq_rung}={PHI**best_eq_rung:.2f}yr, consumer',
    },
    'Heart': {
        'times': np.array([p[0] for p in MAYER_WAVE_PEAKS]),
        'peaks': np.array([p[1] for p in MAYER_WAVE_PEAKS]),
        'ara': 1.35,
        'period': 10.0,
        'desc': 'ARA=1.35, period=10s, clock-driven',
    },
}


# ================================================================
# RUN
# ================================================================

print("=" * 78)
print("237e — Cross-System LOO Test (226 + ARA Midline)")
print("=" * 78)
print()

print("Midline formula: midline = 1 + (1/(1+ARA)) × (ARA - 1)")
print()

# Show midline values
print(f"  {'System':<12} {'ARA':>6} {'acc_frac':>9} {'midline':>9}")
print(f"  {'─'*12} {'─'*6} {'─'*9} {'─'*9}")
for name, cfg in systems.items():
    ml = ara_midline(cfg['ara'])
    af = 1.0 / (1.0 + cfg['ara'])
    print(f"  {name:<12} {cfg['ara']:>6.3f} {af:>9.4f} {ml:>9.4f}")
print()

all_results = {}

for name, cfg in systems.items():
    times = cfg['times']
    peaks = cfg['peaks']
    ara = cfg['ara']
    period = cfg['period']

    mean_amp = np.mean(peaks)
    sine_mae = np.mean(np.abs(peaks - mean_amp))

    # Base_amp search ranges
    ba_std_lo = mean_amp * 0.5
    ba_std_hi = mean_amp * 1.5
    ba_mid_lo = mean_amp * 0.25
    ba_mid_hi = mean_amp * 1.5

    print("─" * 78)
    print(f"SYSTEM: {name.upper()}")
    print(f"  {cfg['desc']}")
    print(f"  N={len(times)}, mean={mean_amp:.2f}, sine MAE={sine_mae:.2f}")
    print()

    # ── Cascade fit ──
    print("  Cascade fit:")
    base_best = grid_search(predict_226_baseline, times, peaks, ara, period,
                            ba_std_lo, ba_std_hi)
    mid_best = grid_search(predict_226_midline, times, peaks, ara, period,
                           ba_mid_lo, ba_mid_hi)

    print(f"    {'Baseline':<15} MAE={base_best['mae']:>8.4f}  "
          f"base_amp={base_best['ba']:.4f}  t_ref={base_best['tr']:.2f}")
    print(f"    {'+ Midline':<15} MAE={mid_best['mae']:>8.4f}  "
          f"base_amp={mid_best['ba']:.4f}  t_ref={mid_best['tr']:.2f}")

    cascade_delta = base_best['mae'] - mid_best['mae']
    cascade_pct = cascade_delta / base_best['mae'] * 100
    marker = "✓ IMPROVED" if cascade_delta > 0.001 else "─ same" if abs(cascade_delta) < 0.001 else "✗ worse"
    print(f"    Δ cascade: {cascade_delta:+.4f} ({cascade_pct:+.1f}%)  {marker}")
    print()

    # ── LOO ──
    print(f"  LOO cross-validation (N={len(times)} folds)...")

    loo_base_mae, loo_base_errs, loo_base_preds = run_loo(
        predict_226_baseline, times, peaks, ara, period, ba_std_lo, ba_std_hi)
    print(f"    Baseline LOO:  {loo_base_mae:.4f}")

    loo_mid_mae, loo_mid_errs, loo_mid_preds = run_loo(
        predict_226_midline, times, peaks, ara, period, ba_mid_lo, ba_mid_hi)
    print(f"    + Midline LOO: {loo_mid_mae:.4f}")

    loo_delta = loo_base_mae - loo_mid_mae
    loo_pct = loo_delta / loo_base_mae * 100
    vs_sine_base = (1 - loo_base_mae / sine_mae) * 100
    vs_sine_mid = (1 - loo_mid_mae / sine_mae) * 100
    marker = "✓ IMPROVED" if loo_delta > 0.001 else "─ same" if abs(loo_delta) < 0.001 else "✗ worse"
    print(f"    Δ LOO: {loo_delta:+.4f} ({loo_pct:+.1f}%)  {marker}")
    print(f"    vs sine:  base {vs_sine_base:+.1f}%,  midline {vs_sine_mid:+.1f}%")
    print()

    # ── Per-cycle detail (best of the two) ──
    best_is_mid = loo_mid_mae < loo_base_mae
    best_errs = loo_mid_errs if best_is_mid else loo_base_errs
    best_preds = loo_mid_preds if best_is_mid else loo_base_preds
    best_label = "midline" if best_is_mid else "baseline"

    print(f"  Per-cycle LOO detail (best = {best_label}):")
    print(f"    {'#':<5} {'Time':>8} {'Actual':>8} {'Pred':>8} {'Error':>8} {'Rel%':>7}")
    for k in range(len(times)):
        err = best_errs[k]
        rel = err / peaks[k] * 100
        print(f"    C{k+1:<4} {times[k]:>8.1f} {peaks[k]:>8.2f} "
              f"{best_preds[k]:>8.2f} {err:>8.2f} {rel:>6.1f}%")
    print()

    all_results[name] = {
        'cascade_base': base_best['mae'],
        'cascade_mid': mid_best['mae'],
        'loo_base': loo_base_mae,
        'loo_mid': loo_mid_mae,
        'sine_mae': sine_mae,
        'n': len(times),
        'ara': ara,
        'midline': ara_midline(ara),
    }


# ================================================================
# FINAL SUMMARY
# ================================================================

print()
print("=" * 78)
print("CROSS-SYSTEM SUMMARY")
print("=" * 78)
print()
print(f"  {'System':<12} {'ARA':>6} {'Midline':>8} {'N':>4} "
      f"{'Cas.Base':>9} {'Cas.Mid':>9} {'LOO.Base':>9} {'LOO.Mid':>9} "
      f"{'ΔLOO':>8} {'vs Sine':>8} {'Winner':>8}")
print(f"  {'─'*12} {'─'*6} {'─'*8} {'─'*4} "
      f"{'─'*9} {'─'*9} {'─'*9} {'─'*9} "
      f"{'─'*8} {'─'*8} {'─'*8}")

wins_mid = 0
wins_base = 0
for name, r in all_results.items():
    delta = r['loo_base'] - r['loo_mid']
    pct = delta / r['loo_base'] * 100
    vs_sine = (1 - r['loo_mid'] / r['sine_mae']) * 100
    winner = "midline" if delta > 0.001 else "base" if delta < -0.001 else "tie"
    if winner == "midline":
        wins_mid += 1
    elif winner == "base":
        wins_base += 1
    print(f"  {name:<12} {r['ara']:>6.3f} {r['midline']:>8.4f} {r['n']:>4} "
          f"{r['cascade_base']:>9.4f} {r['cascade_mid']:>9.4f} "
          f"{r['loo_base']:>9.4f} {r['loo_mid']:>9.4f} "
          f"{delta:>+8.4f} {vs_sine:>+7.1f}% {winner:>8}")

print()
print(f"  Midline wins: {wins_mid}/4  |  Baseline wins: {wins_base}/4")
print()

# Verdict
if wins_mid >= 3:
    print("  ★ ARA MIDLINE IS UNIVERSAL — improves majority of systems")
elif wins_mid >= 2:
    print("  ◆ ARA MIDLINE SHOWS PROMISE — improves half the systems")
else:
    print("  ○ ARA MIDLINE IS SOLAR-SPECIFIC — doesn't generalize")

elapsed = clock_time.time() - t_start
print()
print(f"Total time: {elapsed:.1f}s")
print("=" * 78)
