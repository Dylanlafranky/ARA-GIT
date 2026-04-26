#!/usr/bin/env python3
"""
Script 238 — Lynx-Hare Population Cycle Test

First NEW domain test of the camshaft palindrome formula (237k2).
Uses Hudson's Bay Company fur trapping records (1845-1935).

Two coupled oscillators:
  Hare (snowshoe hare) — the ENGINE: self-reproducing, drives the cycle
  Lynx (Canada lynx) — the CONSUMER: lags hare, crashes when prey declines

ARA classification:
  Hare: engine-type. Growth phase > decline phase. ARA scan around φ.
  Lynx: consumer-type. Driven by external food supply. ARA scan < 1.

Period: ~9.6 years (hare), ~10.5 years (lynx).
Both close to the solar ~11 year cycle — sitting near the same φ-rung.

Source: MacLulich (1937) / Odum (1953), thousands of pelts per year.
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
    """Camshaft-E: palindrome [0,1/φ], quadratic ramp [1/φ,1], full [1+]."""
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


# ── RAW DATA: Hudson's Bay Company (thousands of pelts) ──
HARE_RAW = [
    (1845, 20.0), (1846, 20.0), (1847, 52.0), (1848, 83.4), (1849, 64.6),
    (1850, 68.0), (1851, 83.0), (1852, 12.3), (1853, 36.9), (1854, 7.4),
    (1855, 30.5), (1856, 2.0), (1857, 65.0), (1858, 10.6), (1859, 44.0),
    (1860, 18.0), (1861, 56.0), (1862, 75.6), (1863, 60.0), (1864, 31.6),
    (1865, 16.0), (1866, 24.0), (1867, 28.0), (1868, 30.0), (1869, 60.0),
    (1870, 64.0), (1871, 56.0), (1872, 42.0), (1873, 60.0), (1874, 46.0),
    (1875, 38.0), (1876, 14.0), (1877, 20.0), (1878, 24.0), (1879, 42.0),
    (1880, 60.0), (1881, 140.0), (1882, 149.0), (1883, 85.0), (1884, 46.0),
    (1885, 40.0), (1886, 12.0), (1887, 6.0), (1888, 12.0), (1889, 40.0),
    (1890, 60.0), (1891, 46.0), (1892, 60.0), (1893, 28.0), (1894, 30.0),
    (1895, 46.0), (1896, 24.0), (1897, 14.0), (1898, 46.0), (1899, 75.0),
    (1900, 80.0), (1901, 40.0), (1902, 20.0), (1903, 10.0), (1904, 8.0),
    (1905, 10.0), (1906, 36.0), (1907, 46.0), (1908, 75.0), (1909, 60.0),
    (1910, 30.0), (1911, 20.0), (1912, 10.0), (1913, 10.0), (1914, 14.0),
    (1915, 36.0), (1916, 46.0), (1917, 40.0), (1918, 30.0), (1919, 24.0),
    (1920, 14.0), (1921, 6.0), (1922, 6.0), (1923, 14.0), (1924, 46.0),
    (1925, 75.0), (1926, 60.0), (1927, 40.0), (1928, 20.0), (1929, 14.0),
    (1930, 8.0), (1931, 6.0), (1932, 8.0), (1933, 20.0), (1934, 46.0),
    (1935, 85.0),
]

LYNX_RAW = [
    (1845, 30.0), (1846, 45.7), (1847, 49.0), (1848, 39.0), (1849, 21.0),
    (1850, 8.0), (1851, 13.6), (1852, 19.6), (1853, 21.7), (1854, 26.6),
    (1855, 34.9), (1856, 29.7), (1857, 7.3), (1858, 8.6), (1859, 28.4),
    (1860, 42.0), (1861, 55.0), (1862, 65.0), (1863, 36.0), (1864, 20.6),
    (1865, 13.6), (1866, 5.8), (1867, 9.0), (1868, 10.0), (1869, 12.0),
    (1870, 17.0), (1871, 29.0), (1872, 52.0), (1873, 48.0), (1874, 26.0),
    (1875, 17.0), (1876, 8.0), (1877, 4.0), (1878, 5.0), (1879, 10.0),
    (1880, 27.0), (1881, 42.0), (1882, 70.0), (1883, 68.0), (1884, 35.0),
    (1885, 16.0), (1886, 8.0), (1887, 6.0), (1888, 2.0), (1889, 5.0),
    (1890, 10.0), (1891, 60.0), (1892, 62.0), (1893, 40.0), (1894, 13.0),
    (1895, 5.0), (1896, 2.0), (1897, 3.0), (1898, 6.0), (1899, 12.0),
    (1900, 35.0), (1901, 43.0), (1902, 43.0), (1903, 30.0), (1904, 12.0),
    (1905, 4.0), (1906, 2.0), (1907, 3.0), (1908, 7.0), (1909, 20.0),
    (1910, 34.0), (1911, 34.0), (1912, 26.0), (1913, 12.0), (1914, 6.0),
    (1915, 2.0), (1916, 3.0), (1917, 5.0), (1918, 12.0), (1919, 26.0),
    (1920, 38.0), (1921, 44.0), (1922, 18.0), (1923, 10.0), (1924, 8.0),
    (1925, 3.0), (1926, 4.0), (1927, 5.0), (1928, 10.0), (1929, 22.0),
    (1930, 34.0), (1931, 56.0), (1932, 42.0), (1933, 20.0), (1934, 8.0),
    (1935, 4.0),
]


# ── Extract cycle peaks ──
def find_cycle_peaks(data, smooth_window=5, min_gap=7):
    years = np.array([d[0] for d in data])
    vals = np.array([d[1] for d in data])
    n = len(vals)

    # Smooth
    hw = smooth_window // 2
    smooth = np.zeros(n)
    for i in range(n):
        lo = max(0, i - hw)
        hi = min(n, i + hw + 1)
        smooth[i] = np.mean(vals[lo:hi])

    # Find peaks in smoothed data
    peaks = []
    last_peak_idx = -min_gap - 1
    for i in range(2, n - 2):
        if (smooth[i] >= smooth[i-1] and smooth[i] >= smooth[i+1] and
            smooth[i] >= smooth[i-2] and smooth[i] >= smooth[i+2]):
            if i - last_peak_idx >= min_gap:
                # Take highest raw value within ±2
                lo = max(0, i - 2)
                hi = min(n, i + 3)
                best_j = lo + np.argmax(vals[lo:hi])
                peaks.append((float(years[best_j]), float(vals[best_j])))
                last_peak_idx = i
    return peaks


hare_peaks = find_cycle_peaks(HARE_RAW, smooth_window=5, min_gap=7)
lynx_peaks = find_cycle_peaks(LYNX_RAW, smooth_window=5, min_gap=7)

hare_times = np.array([p[0] for p in hare_peaks])
hare_amps = np.array([p[1] for p in hare_peaks])
lynx_times = np.array([p[0] for p in lynx_peaks])
lynx_amps = np.array([p[1] for p in lynx_peaks])

hare_period = np.mean(np.diff(hare_times))
lynx_period = np.mean(np.diff(lynx_times))

print("=" * 78)
print("Script 238 — Lynx-Hare Population Cycle Test")
print("=" * 78)
print()
print("DATA (Hudson's Bay Company, 1845-1935, thousands of pelts):")
print()
print(f"  HARE peaks: {len(hare_peaks)}")
for t, a in hare_peaks:
    print(f"    {t:.0f}  {a:.1f}k")
print(f"  Mean interval: {hare_period:.1f} years")
print()
print(f"  LYNX peaks: {len(lynx_peaks)}")
for t, a in lynx_peaks:
    print(f"    {t:.0f}  {a:.1f}k")
print(f"  Mean interval: {lynx_period:.1f} years")
print()


# ── Prediction machinery ──
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
                best = {'mae': mae, 'tr': tr, 'ba': ba, 'preds': preds}
    return best

def sine_baseline_loo(times, peaks, period):
    """Simple sine baseline: fit A*sin(2π/P * t + φ) + C."""
    n = len(times)
    errs = []
    for hold in range(n):
        mask = np.ones(n, dtype=bool)
        mask[hold] = False
        tr_t, pk_t = times[mask], peaks[mask]
        # Least-squares fit: y = a*sin(wt) + b*cos(wt) + c
        w = 2 * np.pi / period
        A = np.column_stack([np.sin(w * tr_t), np.cos(w * tr_t), np.ones(n-1)])
        coeffs, _, _, _ = np.linalg.lstsq(A, pk_t, rcond=None)
        pred = coeffs[0]*np.sin(w*times[hold]) + coeffs[1]*np.cos(w*times[hold]) + coeffs[2]
        errs.append(abs(pred - peaks[hold]))
    return np.mean(errs)


# ── ARA SCAN ──
# Scan ARA values to find best-fitting classification for each species
print("=" * 78)
print("ARA SCAN (fit MAE at grid 80×40)")
print("=" * 78)
print()

ara_candidates_hare = [1.0, 1.2, 1.35, PHI, 1.73, 2.0]
ara_candidates_lynx = [0.15, 0.3, 0.5, 0.75, 1.0, 1/PHI]

print("HARE (engine candidate):")
print(f"  {'ARA':>6} {'φ-dist':>7} {'midline':>8} {'fitMAE':>8}")
best_hare = {'mae': 1e9}
for ara in ara_candidates_hare:
    mean_amp = np.mean(hare_amps)
    ba_lo = mean_amp * 0.15
    ba_hi = mean_amp * 2.0
    fn = make_predict_fn(midline_camshaft)
    res = grid_best(fn, hare_times, hare_amps, ara, hare_period, ba_lo, ba_hi)
    pd = _phi_dist(ara)
    ml = midline_camshaft(ara)
    print(f"  {ara:>6.3f} {pd:>7.3f} {ml:>8.4f} {res['mae']:>8.2f}")
    if res['mae'] < best_hare['mae']:
        best_hare = {'mae': res['mae'], 'ara': ara}

print(f"\n  → Best ARA for hare: {best_hare['ara']:.3f} (fitMAE={best_hare['mae']:.2f})")

print()
print("LYNX (consumer candidate):")
print(f"  {'ARA':>6} {'φ-dist':>7} {'midline':>8} {'fitMAE':>8}")
best_lynx = {'mae': 1e9}
for ara in ara_candidates_lynx:
    mean_amp = np.mean(lynx_amps)
    ba_lo = mean_amp * 0.15
    ba_hi = mean_amp * 2.0
    fn = make_predict_fn(midline_camshaft)
    res = grid_best(fn, lynx_times, lynx_amps, ara, lynx_period, ba_lo, ba_hi)
    pd = _phi_dist(ara)
    ml = midline_camshaft(ara)
    print(f"  {ara:>6.3f} {pd:>7.3f} {ml:>8.4f} {res['mae']:>8.2f}")
    if res['mae'] < best_lynx['mae']:
        best_lynx = {'mae': res['mae'], 'ara': ara}

print(f"\n  → Best ARA for lynx: {best_lynx['ara']:.3f} (fitMAE={best_lynx['mae']:.2f})")

hare_ara = best_hare['ara']
lynx_ara = best_lynx['ara']

print()
print("=" * 78)
print("LOO CROSS-VALIDATION")
print("=" * 78)
print()

# ── Run LOO for both species ──
configs = [
    ("Baseline",   predict_baseline),
    ("Camshaft",   make_predict_fn(midline_camshaft)),
]

systems = {
    'Hare': {
        'times': hare_times, 'peaks': hare_amps,
        'ara': hare_ara, 'period': hare_period,
    },
    'Lynx': {
        'times': lynx_times, 'peaks': lynx_amps,
        'ara': lynx_ara, 'period': lynx_period,
    },
}

all_results = {}

for sys_name, cfg in systems.items():
    times = cfg['times']
    peaks = cfg['peaks']
    ara = cfg['ara']
    period = cfg['period']
    mean_amp = np.mean(peaks)
    ba_lo = mean_amp * 0.15
    ba_hi = mean_amp * 2.0

    pd = _phi_dist(ara)
    ml = midline_camshaft(ara)

    print(f"── {sys_name.upper()} (ARA={ara:.3f}, φ-dist={pd:.3f}, midline={ml:.4f}) ──")

    # Sine baseline
    sine_loo = sine_baseline_loo(times, peaks, period)
    print(f"  {'Sine':14}  LOO={sine_loo:.4f}")

    sys_results = {'Sine': sine_loo}
    for label, fn in configs:
        t0 = clock_time.time()
        print(f"  {label:14}...", end=" ", flush=True)
        loo_mae, errs = run_loo(fn, times, peaks, ara, period, ba_lo, ba_hi)
        dt = clock_time.time() - t0

        sys_results[label] = loo_mae

        # vs sine
        sine_delta = sine_loo - loo_mae
        sine_pct = (sine_delta / sine_loo) * 100 if sine_loo > 0 else 0

        # vs baseline
        bl = sys_results.get('Baseline', loo_mae)
        delta = bl - loo_mae
        pct = (delta / bl) * 100 if bl > 0 else 0

        if label == 'Baseline':
            print(f"LOO={loo_mae:.4f}  vs sine: {sine_pct:+.1f}% ({dt:.0f}s)")
        else:
            print(f"LOO={loo_mae:.4f}  vs base: {pct:+.1f}%, vs sine: {sine_pct:+.1f}% ({dt:.0f}s)")

    all_results[sys_name] = sys_results
    print()


# ── SCOREBOARD ──
print("=" * 78)
print("SCOREBOARD")
print("=" * 78)
print()
print(f"  {'System':<10} {'ARA':>6} {'Sine LOO':>10} {'Base LOO':>10} "
      f"{'Camshaft':>10} {'vs Sine':>10}")
for sys_name, r in all_results.items():
    cfg = systems[sys_name]
    vsine = r['Sine'] - r['Camshaft']
    pct = (vsine / r['Sine']) * 100 if r['Sine'] > 0 else 0
    print(f"  {sys_name:<10} {cfg['ara']:>6.3f} {r['Sine']:>10.3f} "
          f"{r['Baseline']:>10.3f} {r['Camshaft']:>10.3f} {pct:>+9.1f}%")

print()

# ── COMPARISON WITH EXISTING SYSTEMS ──
print("=" * 78)
print("CROSS-DOMAIN COMPARISON")
print("=" * 78)
print()
print("  System       ARA     φ-dist  Zone          Midline")
print("  ─" * 38)
all_systems = [
    ('Solar',      PHI,    ),
    ('Hare',       hare_ara),
    ('Heart',      1.35    ),
    ('Lynx',       lynx_ara),
    ('ENSO',       2.0     ),
    ('Earthquake', 0.15    ),
]
for name, ara in all_systems:
    pd = _phi_dist(ara)
    ml = midline_camshaft(ara)
    zone = 'Palindrome' if pd <= 1/PHI else ('Ramp' if pd < 1.0 else 'Full')
    print(f"  {name:<12}  {ara:>6.3f}  {pd:>6.3f}  {zone:<12}  {ml:.4f}")

print()
elapsed = clock_time.time() - t_start
print(f"Total runtime: {elapsed:.0f}s")
