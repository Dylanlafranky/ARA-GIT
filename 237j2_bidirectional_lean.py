#!/usr/bin/env python3
"""
Script 237j2 — Bidirectional Valve (Lean: 3 configs only)

Only: Baseline, InvValve (237h), BiDir-A (wave collision).

BiDir-A formula: midline = 1 + (ARA - 1)^2 / (ARA^2 + 1)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2

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


def _base_midline(a):
    a = max(0.01, a)
    return 1.0 + (1.0/(1.0+a)) * (a - 1.0)

def midline_inverse_valve(ara):
    if ara >= 1.0:
        return _base_midline(ara)
    else:
        return _base_midline(1.0 / max(0.01, ara))

def midline_bidirectional(ara):
    """Wave collision: midline = 1 + (ARA-1)^2 / (ARA^2 + 1)"""
    a = max(0.01, ara)
    return 1.0 + (a - 1.0)**2 / (a**2 + 1.0)


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

N_TR = 80
N_BA = 40

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


# DATA
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
best_eq_rung = 3
best_diff = abs(np.mean(eq_intervals) - PHI**3)
for r in range(2, 6):
    d = abs(np.mean(eq_intervals) - PHI**r)
    if d < best_diff:
        best_eq_rung = r
        best_diff = d

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


# RUN
print("=" * 78)
print("237j2 — Bidirectional Valve (Wave Collision) — Lean Run")
print(f"Grid: {N_TR}×{N_BA}")
print("=" * 78)
print()

print("MIDLINE COMPARISON:")
print(f"  {'System':<12} {'ARA':>6} {'Base':>8} {'InvV':>8} {'BiDir':>8}")
print(f"  {'─'*12} {'─'*6} {'─'*8} {'─'*8} {'─'*8}")
for name, cfg in systems.items():
    a = cfg['ara']
    print(f"  {name:<12} {a:>6.3f} {'1.000':>8} "
          f"{midline_inverse_valve(a):>8.4f} "
          f"{midline_bidirectional(a):>8.4f}")
print()

configs = [
    ("Baseline",  predict_baseline),
    ("InvValve",  make_predict_fn(midline_inverse_valve)),
    ("BiDir",     make_predict_fn(midline_bidirectional)),
]

print("LOO CROSS-VALIDATION:")
print()

all_loo = {}

for sys_name, cfg in systems.items():
    times = cfg['times']
    peaks = cfg['peaks']
    ara = cfg['ara']
    period = cfg['period']
    mean_amp = np.mean(peaks)
    sine_mae = np.mean(np.abs(peaks - mean_amp))

    ba_lo = mean_amp * 0.15
    ba_hi = mean_amp * 2.0

    print(f"── {sys_name.upper()} (ARA={ara:.3f}, N={len(times)}) ──")

    sys_results = {}
    for label, fn in configs:
        t0 = clock_time.time()
        print(f"  {label:<12}...", end=" ", flush=True)
        loo_mae, errs = run_loo(fn, times, peaks, ara, period,
                                ba_lo, ba_hi)
        dt = clock_time.time() - t0
        sys_results[label] = loo_mae
        bl = sys_results.get('Baseline', loo_mae)
        delta = bl - loo_mae
        pct = (delta / bl) * 100 if bl > 0 else 0
        marker = "+" if delta > 0.001 else "-" if delta < -0.001 else "="
        if label == 'Baseline':
            marker = "="
        print(f"LOO={loo_mae:.4f}  Δ={delta:+.4f} ({pct:+.1f}%) [{marker}] ({dt:.0f}s)")

    all_loo[sys_name] = sys_results
    print()


# SCOREBOARD
print("=" * 78)
print("SCOREBOARD")
print("=" * 78)
print()

labels = [c[0] for c in configs]
print(f"  {'System':<12} {'Baseline':>12} {'InvValve':>12} {'BiDir':>12}   Best")
print(f"  {'─'*12} {'─'*12} {'─'*12} {'─'*12}   {'─'*12}")

for sys_name in all_loo:
    r = all_loo[sys_name]
    best_l = min(r, key=r.get)
    print(f"  {sys_name:<12}", end="")
    for l in labels:
        marker = "***" if l == best_l else "   "
        print(f" {r[l]:>9.4f}{marker}", end="")
    print(f"   {best_l}")

# Universal check
print()
print("UNIVERSAL CHECK:")
for label in labels[1:]:
    hurts, helps, neutral = [], [], []
    for sys_name in all_loo:
        bl = all_loo[sys_name]['Baseline']
        val = all_loo[sys_name][label]
        delta_pct = ((bl - val) / bl) * 100
        if val > bl + 0.001:
            hurts.append(f"{sys_name}({delta_pct:+.1f}%)")
        elif val < bl - 0.001:
            helps.append(f"{sys_name}({delta_pct:+.1f}%)")
        else:
            neutral.append(sys_name)
    status = "★ HURTS NOTHING" if not hurts else f"HURTS: {', '.join(hurts)}"
    print(f"  {label:<12} helps [{', '.join(helps)}]  {status}")

elapsed = clock_time.time() - t_start
print(f"\nTotal time: {elapsed:.1f}s")
print("=" * 78)
