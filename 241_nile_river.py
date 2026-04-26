#!/usr/bin/env python3
"""
Script 241 — Nile River Discharge Cycle Test

9th domain test of the camshaft palindrome formula (237k2).
Uses the classic Nile at Aswan dataset (1871-1970, 100 years).

Annual flow (10^8 m³) measured at Aswan gauge.
Oscillatory structure with ~7.4 year envelope cycle.
Famous 1898 regime shift (22% drop in mean flow).

The Nile is a CONSUMER — flood amplitude is driven by Ethiopian
monsoon, ENSO teleconnections, and Indian Ocean Dipole. The river
does not generate its own variability; it receives it.

Source: statsmodels built-in 'nile' dataset (Cobb, 1978; Balke, 1993).
Original: Annual flow of the Nile at Aswan, 1871-1970.
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


# ── RAW DATA: Nile at Aswan, annual flow (10^8 m³), 1871-1970 ──
NILE_RAW = [
    (1871, 1120), (1872, 1160), (1873, 963), (1874, 1210), (1875, 1160),
    (1876, 1160), (1877, 813), (1878, 1230), (1879, 1370), (1880, 1140),
    (1881, 995), (1882, 935), (1883, 1110), (1884, 994), (1885, 1020),
    (1886, 960), (1887, 1180), (1888, 799), (1889, 958), (1890, 1140),
    (1891, 1100), (1892, 1210), (1893, 1150), (1894, 1250), (1895, 1260),
    (1896, 1220), (1897, 1030), (1898, 1100), (1899, 774), (1900, 840),
    (1901, 874), (1902, 694), (1903, 940), (1904, 833), (1905, 701),
    (1906, 916), (1907, 692), (1908, 1020), (1909, 1050), (1910, 969),
    (1911, 831), (1912, 726), (1913, 456), (1914, 824), (1915, 702),
    (1916, 1120), (1917, 1100), (1918, 832), (1919, 764), (1920, 821),
    (1921, 768), (1922, 845), (1923, 864), (1924, 862), (1925, 698),
    (1926, 845), (1927, 744), (1928, 796), (1929, 1040), (1930, 759),
    (1931, 781), (1932, 865), (1933, 845), (1934, 944), (1935, 984),
    (1936, 897), (1937, 822), (1938, 1010), (1939, 771), (1940, 676),
    (1941, 649), (1942, 846), (1943, 812), (1944, 742), (1945, 801),
    (1946, 1040), (1947, 860), (1948, 874), (1949, 848), (1950, 890),
    (1951, 744), (1952, 749), (1953, 838), (1954, 1050), (1955, 918),
    (1956, 986), (1957, 797), (1958, 923), (1959, 975), (1960, 815),
    (1961, 1020), (1962, 906), (1963, 901), (1964, 1170), (1965, 912),
    (1966, 746), (1967, 919), (1968, 718), (1969, 714), (1970, 740),
]


# ── Extract envelope peaks (multi-year flood cycles) ──
def find_envelope_peaks(data, smooth_window=3, min_gap=4):
    """Extract peaks from smoothed annual flow data."""
    years = np.array([d[0] for d in data])
    vals = np.array([float(d[1]) for d in data])
    n = len(vals)

    # Smooth with window
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
                # Take highest raw value within ±1
                lo = max(0, i - 1)
                hi = min(n, i + 2)
                best_j = lo + np.argmax(vals[lo:hi])
                peaks.append((float(years[best_j]), float(vals[best_j])))
                last_peak_idx = i
    return peaks


nile_peaks = find_envelope_peaks(NILE_RAW, smooth_window=3, min_gap=4)
nile_times = np.array([p[0] for p in nile_peaks])
nile_amps = np.array([p[1] for p in nile_peaks])
nile_period = np.mean(np.diff(nile_times))

print("=" * 78)
print("Script 241 — Nile River Discharge Cycle Test")
print("=" * 78)
print()
print("DATA: Nile at Aswan, annual flow (10^8 m³), 1871-1970")
print(f"Source: statsmodels built-in (Cobb 1978 / Balke 1993)")
print()
print(f"  Envelope peaks: {len(nile_peaks)}")
for t, a in nile_peaks:
    print(f"    {t:.0f}  {a:.0f}")
print(f"  Mean interval: {nile_period:.1f} years")
print(f"  Mean amplitude: {np.mean(nile_amps):.1f}")
print(f"  Std amplitude: {np.std(nile_amps):.1f}")
print(f"  CV: {np.std(nile_amps)/np.mean(nile_amps)*100:.1f}%")
print()


# ── Prediction machinery (same as 238) ──
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
        w = 2 * np.pi / period
        A = np.column_stack([np.sin(w * tr_t), np.cos(w * tr_t), np.ones(n-1)])
        coeffs, _, _, _ = np.linalg.lstsq(A, pk_t, rcond=None)
        pred = coeffs[0]*np.sin(w*times[hold]) + coeffs[1]*np.cos(w*times[hold]) + coeffs[2]
        errs.append(abs(pred - peaks[hold]))
    return np.mean(errs)


# ── ARA SCAN ──
print("=" * 78)
print("ARA SCAN (fit MAE at grid 80×40)")
print("=" * 78)
print()

# Nile is a consumer — scan consumer and near-clock range
ara_candidates = [0.15, 0.3, 0.5, 1/PHI, 0.75, 1.0, 1.2, 1.35, PHI, 2.0]

mean_amp = np.mean(nile_amps)
ba_lo = mean_amp * 0.15
ba_hi = mean_amp * 2.0

print(f"  {'ARA':>6} {'φ-dist':>7} {'midline':>8} {'fitMAE':>8}")
best_nile = {'mae': 1e9}
for ara in ara_candidates:
    fn = make_predict_fn(midline_camshaft)
    res = grid_best(fn, nile_times, nile_amps, ara, nile_period, ba_lo, ba_hi)
    pd = _phi_dist(ara)
    ml = midline_camshaft(ara)
    print(f"  {ara:>6.3f} {pd:>7.3f} {ml:>8.4f} {res['mae']:>8.2f}")
    if res['mae'] < best_nile['mae']:
        best_nile = {'mae': res['mae'], 'ara': ara, 'preds': res['preds']}

nile_ara = best_nile['ara']
print(f"\n  → Best ARA: {nile_ara:.3f} (fitMAE={best_nile['mae']:.2f})")


# ── LOO CROSS-VALIDATION ──
print()
print("=" * 78)
print("LOO CROSS-VALIDATION")
print("=" * 78)
print()

pd = _phi_dist(nile_ara)
ml = midline_camshaft(nile_ara)
print(f"Nile (ARA={nile_ara:.3f}, φ-dist={pd:.3f}, midline={ml:.4f})")
print()

# Sine baseline
sine_loo = sine_baseline_loo(nile_times, nile_amps, nile_period)
print(f"  {'Sine':14}  LOO={sine_loo:.4f}")

configs = [
    ("Baseline",   predict_baseline),
    ("Camshaft",   make_predict_fn(midline_camshaft)),
]

nile_results = {'Sine': sine_loo}
for label, fn in configs:
    t0 = clock_time.time()
    print(f"  {label:14}...", end=" ", flush=True)
    loo_mae, errs = run_loo(fn, nile_times, nile_amps, nile_ara, nile_period, ba_lo, ba_hi)
    dt = clock_time.time() - t0

    nile_results[label] = loo_mae

    sine_delta = sine_loo - loo_mae
    sine_pct = (sine_delta / sine_loo) * 100 if sine_loo > 0 else 0

    bl = nile_results.get('Baseline', loo_mae)
    delta = bl - loo_mae
    pct = (delta / bl) * 100 if bl > 0 else 0

    if label == 'Baseline':
        print(f"LOO={loo_mae:.4f}  vs sine: {sine_pct:+.1f}% ({dt:.0f}s)")
    else:
        print(f"LOO={loo_mae:.4f}  vs base: {pct:+.1f}%, vs sine: {sine_pct:+.1f}% ({dt:.0f}s)")

# Get best-fit predictions for visualization
fn_best = make_predict_fn(midline_camshaft)
best_fit = grid_best(fn_best, nile_times, nile_amps, nile_ara, nile_period, ba_lo, ba_hi)
baseline_fit = grid_best(predict_baseline, nile_times, nile_amps, nile_ara, nile_period, ba_lo, ba_hi)

print()
print("=" * 78)
print("SCOREBOARD")
print("=" * 78)
print()
print(f"  Nile River (Aswan, 1871-1970)")
print(f"  ARA = {nile_ara:.3f}, φ-dist = {pd:.3f}, midline = {ml:.4f}")
print(f"  Period = {nile_period:.1f} years, {len(nile_peaks)} envelope peaks")
print()
print(f"  Sine LOO:     {nile_results['Sine']:.4f}")
print(f"  Baseline LOO: {nile_results['Baseline']:.4f}")
print(f"  Camshaft LOO: {nile_results['Camshaft']:.4f}")
vsine = nile_results['Sine'] - nile_results['Camshaft']
pct = (vsine / nile_results['Sine']) * 100 if nile_results['Sine'] > 0 else 0
print(f"  vs Sine:      {pct:+.1f}%")

# ── Data for visualization ──
print()
print("=" * 78)
print("DATA FOR VISUALIZATION")
print("=" * 78)
print()
print(f"times: {list(nile_times)}")
print(f"peaks: {list(nile_amps)}")
print(f"baseline_preds: {[round(p, 2) for p in baseline_fit['preds']]}")
print(f"camshaft_preds: {[round(p, 2) for p in best_fit['preds']]}")
print(f"baseline_mae: {round(baseline_fit['mae'], 2)}")
print(f"camshaft_mae: {round(best_fit['mae'], 2)}")
print(f"sine_mean: {round(np.mean(nile_amps), 2)}")
print(f"ara: {nile_ara}")
print(f"period: {round(nile_period, 1)}")
print(f"midline: {round(ml, 4)}")
print(f"phi_dist: {round(pd, 3)}")

print()

# ── CROSS-DOMAIN COMPARISON ──
print("=" * 78)
print("CROSS-DOMAIN COMPARISON")
print("=" * 78)
print()
print("  System         ARA     φ-dist  Zone          Midline")
print("  ─" * 38)
all_systems = [
    ('Solar',        PHI    ),
    ('ENSO',         2.0    ),
    ('Heart',        1.35   ),
    ('Hare',         1.0    ),
    ('Lynx',         1.0    ),
    ('Unemployment', 0.75   ),
    ('GDP_Growth',   1.0    ),
    ('CO2_Amplitude',0.15   ),
    ('Nile',         nile_ara),
    ('Earthquake',   0.15   ),
]
for name, ara in all_systems:
    pd_s = _phi_dist(ara)
    ml_s = midline_camshaft(ara)
    zone = 'Palindrome' if pd_s <= 1/PHI else ('Ramp' if pd_s < 1.0 else 'Full')
    print(f"  {name:<14}  {ara:>6.3f}  {pd_s:>6.3f}  {zone:<12}  {ml_s:.4f}")

print()
elapsed = clock_time.time() - t_start
print(f"Total runtime: {elapsed:.0f}s")
