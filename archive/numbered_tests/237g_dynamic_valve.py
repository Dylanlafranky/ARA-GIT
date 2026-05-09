#!/usr/bin/env python3
"""
Script 237g — Dynamic Valve Midline (instantaneous ARA)

The valve isn't the system's static ARA — it's the ARA of the
vehicle's CURRENT position. prev_amp / base_amp = instantaneous ARA.

The pipe breathes:
  - Grand maximum → inst_ARA >> 1 → valve wide open → midline shifts up
  - Dalton minimum → inst_ARA << 1 → valve closes → midline ≈ 1.0
  - Clock-like state → inst_ARA ≈ 1 → midline = 1.0 (no offset)

Per-cycle computation:
  inst_ara = prev_amp / base_amp   (or 1.0 for first cycle)
  acc_frac = 1 / (1 + inst_ara)
  midline_k = 1 + valve(inst_ara) × acc_frac × (inst_ara - 1)

Valve candidates:
  V1: valve = inst_ara / (1 + inst_ara)    — release fraction
  V2: valve = (inst_ara / (1 + inst_ara))² — pipe cross-section

This naturally handles all system types:
  - Earthquake: amplitudes hover near mean → inst_ara ≈ 1 → valve neutral
  - Solar maxima: prev_amp >> base_amp → valve opens → midline rises
  - Solar minima: prev_amp << base_amp → valve closes → midline drops
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2

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
# DYNAMIC VALVE PREDICTION FUNCTIONS
# ================================================================

def predict_dynamic_v1(times, peaks, t_ref, base_amp, ara, period):
    """Dynamic valve V1: valve = inst_ara / (1 + inst_ara).

    Each cycle's midline depends on the PREVIOUS cycle's amplitude
    relative to base_amp. The pipe opens when the system is producing,
    closes when consuming.
    """
    sys226 = ARASystem("sys", ara, period, times, peaks)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None

        # Standard cascade prediction
        std_pred = sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev)
        shape = std_pred / base_amp

        # Instantaneous ARA from previous cycle
        if prev is not None and base_amp > 0:
            inst_ara = prev / base_amp
        else:
            inst_ara = 1.0  # first cycle: clock-like, no offset

        # Dynamic valve and midline
        inst_ara = max(0.01, inst_ara)
        acc = 1.0 / (1.0 + inst_ara)
        raw_offset = acc * (inst_ara - 1.0)
        valve = inst_ara / (1.0 + inst_ara)

        midline = 1.0 + valve * raw_offset
        shifted = shape + (midline - 1.0)
        preds.append(base_amp * shifted)

    return np.array(preds)


def predict_dynamic_v2(times, peaks, t_ref, base_amp, ara, period):
    """Dynamic valve V2: valve = (inst_ara / (1 + inst_ara))².

    Squared valve — pipe cross-section scales as circumference².
    Sharper cutoff for consumer-like states.
    """
    sys226 = ARASystem("sys", ara, period, times, peaks)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        std_pred = sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev)
        shape = std_pred / base_amp

        if prev is not None and base_amp > 0:
            inst_ara = prev / base_amp
        else:
            inst_ara = 1.0

        inst_ara = max(0.01, inst_ara)
        acc = 1.0 / (1.0 + inst_ara)
        raw_offset = acc * (inst_ara - 1.0)
        valve = (inst_ara / (1.0 + inst_ara)) ** 2

        midline = 1.0 + valve * raw_offset
        shifted = shape + (midline - 1.0)
        preds.append(base_amp * shifted)

    return np.array(preds)


def predict_dynamic_pure(times, peaks, t_ref, base_amp, ara, period):
    """Dynamic pure: midline from inst_ara directly, no separate valve.

    midline = 1 + acc(inst_ara) × (inst_ara - 1)

    Same formula as 237d but with inst_ara instead of system ARA.
    The instantaneous ARA IS the valve — no extra function needed.
    """
    sys226 = ARASystem("sys", ara, period, times, peaks)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        std_pred = sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev)
        shape = std_pred / base_amp

        if prev is not None and base_amp > 0:
            inst_ara = prev / base_amp
        else:
            inst_ara = 1.0

        inst_ara = max(0.01, inst_ara)
        acc = 1.0 / (1.0 + inst_ara)
        midline = 1.0 + acc * (inst_ara - 1.0)

        shifted = shape + (midline - 1.0)
        preds.append(base_amp * shifted)

    return np.array(preds)


def predict_226_baseline(times, peaks, t_ref, base_amp, ara, period):
    """226 v4 no midline."""
    sys226 = ARASystem("sys", ara, period, times, peaks)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        preds.append(sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev))
    return np.array(preds)


def predict_static_midline(times, peaks, t_ref, base_amp, ara, period):
    """237d static midline (for comparison)."""
    sys226 = ARASystem("sys", ara, period, times, peaks)
    acc = 1.0 / (1.0 + max(0.01, ara))
    midline = 1.0 + acc * (ara - 1.0)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        std_pred = sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev)
        shape = std_pred / base_amp
        shifted = shape + (midline - 1.0)
        preds.append(base_amp * shifted)
    return np.array(preds)


# ================================================================
# GRID SEARCH & LOO
# ================================================================

def grid_search(predict_fn, times, peaks, ara, period, ba_lo, ba_hi):
    gleissberg = period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * period

    best = {'mae': 1e9}
    for tr in np.linspace(tr_lo, tr_hi, 60):
        for ba in np.linspace(ba_lo, ba_hi, 30):
            preds = predict_fn(times, peaks, tr, ba, ara, period)
            mae = np.mean(np.abs(preds - peaks))
            if mae < best['mae']:
                best = {'mae': mae, 'tr': tr, 'ba': ba, 'preds': preds}
    return best


def run_loo(predict_fn, times, peaks, ara, period, ba_lo, ba_hi):
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
        for tr in np.linspace(tr_lo_l, tr_hi_l, 60):
            for ba in np.linspace(ba_lo_l, ba_hi_l, 30):
                preds = predict_fn(tr_t, pk_t, tr, ba, ara, period)
                mae = np.mean(np.abs(preds - pk_t))
                if mae < best['mae']:
                    best = {'mae': mae, 'tr': tr, 'ba': ba}

        preds_full = predict_fn(times, peaks, best['tr'], best['ba'], ara, period)
        error = abs(preds_full[hold_idx] - peaks[hold_idx])
        loo_errors.append(error)
        loo_preds.append(preds_full[hold_idx])

    return np.mean(loo_errors), loo_errors, loo_preds


# ================================================================
# DATA SOURCES
# ================================================================

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

ENSO_EVENTS = [
    (1951.9, 0.8), (1953.1, 0.8), (1957.9, 1.8), (1963.9, 1.0),
    (1965.9, 1.9), (1968.9, 1.1), (1972.9, 2.1), (1976.9, 0.8),
    (1977.9, 0.7), (1979.9, 0.6), (1982.9, 2.2), (1986.9, 1.2),
    (1987.9, 1.6), (1991.9, 1.6), (1994.9, 1.0), (1997.9, 2.4),
    (2002.9, 1.3), (2004.9, 0.7), (2006.9, 1.0), (2009.9, 1.6),
    (2015.0, 2.6), (2018.9, 0.9), (2023.9, 2.0),
]

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
    years = sorted(EQ_DATA.keys())
    counts = [EQ_DATA[y] for y in years]
    n = len(years)
    smooth = []
    for i in range(n):
        lo = max(0, i - window // 2)
        hi = min(n, i + window // 2 + 1)
        smooth.append(np.mean(counts[lo:hi]))
    peaks_t, peaks_a = [], []
    last_peak = -min_gap - 1
    for i in range(1, n - 1):
        if smooth[i] > smooth[i-1] and smooth[i] > smooth[i+1]:
            if i - last_peak >= min_gap:
                peaks_t.append(float(years[i]))
                peaks_a.append(smooth[i])
                last_peak = i
    return np.array(peaks_t), np.array(peaks_a)

MAYER_WAVE_PEAKS = [
    (10, 5.2), (20, 7.1), (30, 8.3), (40, 6.5), (50, 4.8),
    (60, 3.9), (70, 5.5), (80, 7.8), (90, 9.1), (100, 7.2),
    (110, 5.6), (120, 4.1), (130, 5.8), (140, 8.0), (150, 6.9),
    (160, 5.3), (170, 6.4), (180, 8.7), (190, 7.6), (200, 5.1),
    (210, 3.8), (220, 5.9), (230, 7.5), (240, 8.8), (250, 6.3),
    (260, 4.5), (270, 5.7), (280, 7.3), (290, 6.1), (300, 4.9),
]

eq_times, eq_peaks = extract_eq_cycle_peaks(window=7, min_gap=5)
eq_intervals = np.diff(eq_times)
eq_mean_interval = np.mean(eq_intervals)
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
        'ara': PHI, 'period': 11.07,
    },
    'ENSO': {
        'times': np.array([e[0] for e in ENSO_EVENTS]),
        'peaks': np.array([e[1] for e in ENSO_EVENTS]),
        'ara': 2.0, 'period': 3.75,
    },
    'Earthquake': {
        'times': eq_times, 'peaks': eq_peaks,
        'ara': 0.15, 'period': PHI**best_eq_rung,
    },
    'Heart': {
        'times': np.array([p[0] for p in MAYER_WAVE_PEAKS]),
        'peaks': np.array([p[1] for p in MAYER_WAVE_PEAKS]),
        'ara': 1.35, 'period': 10.0,
    },
}


# ================================================================
# RUN
# ================================================================

print("=" * 78)
print("237g — Dynamic Valve Midline (instantaneous ARA)")
print("=" * 78)
print()
print("The valve breathes: inst_ara = prev_amp / base_amp")
print("  High prev_amp → pipe open → midline shifts")
print("  Low prev_amp  → pipe closes → midline ≈ 1.0")
print()

configs = [
    ("Baseline",     predict_226_baseline),
    ("Static mid",   predict_static_midline),
    ("Dyn pure",     predict_dynamic_pure),
    ("Dyn V1",       predict_dynamic_v1),
    ("Dyn V2",       predict_dynamic_v2),
]

# ── Show cascade fit first (fast) ──
print("─" * 78)
print("CASCADE FIT (all systems, all variants)")
print("─" * 78)
print()

for sys_name, cfg in systems.items():
    times = cfg['times']
    peaks = cfg['peaks']
    ara = cfg['ara']
    period = cfg['period']
    mean_amp = np.mean(peaks)

    ba_lo = mean_amp * 0.25
    ba_hi = mean_amp * 1.5

    print(f"  {sys_name} (ARA={ara:.3f}, N={len(times)}):")
    for label, fn in configs:
        best = grid_search(fn, times, peaks, ara, period, ba_lo, ba_hi)
        print(f"    {label:<14} cascade={best['mae']:.4f}  "
              f"ba={best['ba']:.4f}  tr={best['tr']:.2f}")
    print()


# ── LOO (the real test) ──
print("=" * 78)
print("LOO CROSS-VALIDATION")
print("=" * 78)
print()

all_loo = {}

for sys_name, cfg in systems.items():
    times = cfg['times']
    peaks = cfg['peaks']
    ara = cfg['ara']
    period = cfg['period']
    mean_amp = np.mean(peaks)
    sine_mae = np.mean(np.abs(peaks - mean_amp))

    ba_lo = mean_amp * 0.25
    ba_hi = mean_amp * 1.5

    print(f"── {sys_name.upper()} (ARA={ara:.3f}, N={len(times)}, "
          f"sine={sine_mae:.4f}) ──")

    sys_results = {}
    for label, fn in configs:
        print(f"  {label}...", end=" ", flush=True)
        loo_mae, errs, preds = run_loo(fn, times, peaks, ara, period,
                                        ba_lo, ba_hi)
        sys_results[label] = {'mae': loo_mae, 'errs': errs, 'preds': preds}
        print(f"LOO = {loo_mae:.4f}")

    all_loo[sys_name] = sys_results

    # Per-cycle for dynamic pure (our main candidate)
    dp = sys_results['Dyn pure']
    print(f"\n  Per-cycle (Dyn pure):")
    print(f"    {'C':<5} {'Time':>8} {'Act':>8} {'Pred':>8} {'Err':>8}")
    for k in range(len(times)):
        print(f"    C{k+1:<4} {times[k]:>8.1f} {peaks[k]:>8.2f} "
              f"{dp['preds'][k]:>8.2f} {dp['errs'][k]:>8.2f}")
    print()


# ================================================================
# FINAL SUMMARY
# ================================================================

print("=" * 78)
print("FINAL SUMMARY")
print("=" * 78)
print()

labels = [c[0] for c in configs]

print(f"  {'System':<12} {'ARA':>5}", end="")
for l in labels:
    print(f" {l:>12}", end="")
print("   Best")
print(f"  {'─'*12} {'─'*5}", end="")
for _ in labels:
    print(f" {'─'*12}", end="")
print(f"   {'─'*12}")

wins = {l: 0 for l in labels}

for sys_name in all_loo:
    ara = systems[sys_name]['ara']
    r = all_loo[sys_name]
    vals = {l: r[l]['mae'] for l in labels}
    best_l = min(vals, key=vals.get)
    wins[best_l] += 1

    print(f"  {sys_name:<12} {ara:>5.3f}", end="")
    for l in labels:
        marker = "***" if l == best_l else "   "
        print(f" {vals[l]:>9.4f}{marker}", end="")
    print(f"   {best_l}")

print()
print("  Wins:", end="")
for l in labels:
    if wins[l] > 0:
        print(f"  {l}: {wins[l]}", end="")
print()

# ── Improvement table for best dynamic variant ──
dyn_labels = [l for l in labels if l.startswith('Dyn')]
best_dyn = None
best_dyn_score = 0
for dl in dyn_labels:
    score = sum(1 for s in all_loo
                if all_loo[s][dl]['mae'] < all_loo[s]['Baseline']['mae'])
    if score > best_dyn_score:
        best_dyn = dl
        best_dyn_score = score

if best_dyn:
    print(f"\n  Best dynamic variant: {best_dyn}")
    print(f"\n  {best_dyn} vs Baseline:")
    for sys_name in all_loo:
        base = all_loo[sys_name]['Baseline']['mae']
        dyn = all_loo[sys_name][best_dyn]['mae']
        delta = base - dyn
        pct = delta / base * 100 if base > 0 else 0
        marker = "✓" if delta > 0.001 else "✗" if delta < -0.001 else "─"
        print(f"    {sys_name:<12}: {base:.4f} → {dyn:.4f}  "
              f"Δ={delta:+.4f} ({pct:+.1f}%) {marker}")

    print(f"\n  {best_dyn} vs Static midline:")
    for sys_name in all_loo:
        stat = all_loo[sys_name]['Static mid']['mae']
        dyn = all_loo[sys_name][best_dyn]['mae']
        delta = stat - dyn
        pct = delta / stat * 100 if stat > 0 else 0
        marker = "✓" if delta > 0.001 else "✗" if delta < -0.001 else "─"
        print(f"    {sys_name:<12}: {stat:.4f} → {dyn:.4f}  "
              f"Δ={delta:+.4f} ({pct:+.1f}%) {marker}")

elapsed = clock_time.time() - t_start
print()
print(f"Total time: {elapsed:.1f}s")
print("=" * 78)
