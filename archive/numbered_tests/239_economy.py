#!/usr/bin/env python3
"""
Script 239 — US Economic Cycle Test (v2: detrended GDP)

Two faces of the same business cycle:
  Unemployment peaks — the CONSUMER: spikes during recessions, doesn't
    self-generate. Acted upon by economic collapse.
  GDP growth peaks — DETRENDED to remove secular decline (maturing economy).
    Raw GDP growth drops from ~8% (1950s) to ~3% (2010s). The WAVE rides
    on top of that trend. Detrending via exponential decay fit exposes the
    oscillatory signal: the business cycle clock.

Data: Post-WWII US business cycles.
  GDP: peak annual real GDP growth rate in each expansion, detrended.
  Unemployment: peak unemployment rate in each recession.

Source: Bureau of Economic Analysis (GDP), Bureau of Labor Statistics (unemployment).
Both are among the most documented time series in economics.
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
# DATA
# ══════════════════════════════════════════════════════════════

# POST-WWII US UNEMPLOYMENT RATE PEAKS (% at recession peak)
# Source: BLS, NBER recession dates
# Each value = peak monthly unemployment rate during that recession
UNEMP_PEAKS = [
    (1949.8,  7.9),   # 1948-49 recession
    (1954.2,  5.9),   # 1953-54 recession
    (1958.5,  7.5),   # 1957-58 recession
    (1961.4,  7.1),   # 1960-61 recession
    (1970.9,  6.1),   # 1969-70 recession
    (1975.4,  9.0),   # 1973-75 recession (oil crisis)
    (1982.9, 10.8),   # 1981-82 recession (Volcker)
    (1992.5,  7.8),   # 1990-91 recession
    (2003.5,  6.3),   # 2001 recession (dot-com)
    (2009.8, 10.0),   # 2007-09 recession (GFC)
    (2020.3, 14.7),   # 2020 COVID recession
]

# POST-WWII US REAL GDP GROWTH PEAKS (% annual growth rate at cycle peak)
# Source: BEA, peak annual growth during each expansion
GDP_PEAKS = [
    (1950.0,  8.7),   # Post-WWII boom
    (1951.0,  8.0),   # Korean War expansion
    (1955.0,  7.1),   # 1950s expansion
    (1959.0,  6.9),   # Late 50s
    (1962.0,  6.1),   # Kennedy expansion
    (1966.0,  6.6),   # Vietnam/Great Society
    (1968.0,  4.9),   # Late 60s
    (1973.0,  5.6),   # Early 70s
    (1978.0,  5.5),   # Carter expansion
    (1984.0,  7.2),   # Reagan recovery
    (1988.0,  4.2),   # Late Reagan
    (1994.0,  4.0),   # Clinton early
    (1998.0,  4.5),   # Dot-com era
    (2000.0,  4.1),   # Late 90s peak
    (2004.0,  3.8),   # Post 9/11 recovery
    (2006.0,  2.7),   # Housing boom
    (2015.0,  2.9),   # Obama expansion
    (2018.0,  3.0),   # Trump tax cut
    (2021.0,  5.9),   # COVID recovery bounce
]


# ── Detrend GDP growth (remove secular decline) ──
from scipy.optimize import curve_fit

def _exp_decay(t, a, b, c):
    return a * np.exp(-b * (t - 1950)) + c

_gdp_raw_times = np.array([p[0] for p in GDP_PEAKS])
_gdp_raw_amps = np.array([p[1] for p in GDP_PEAKS])
_gdp_popt, _ = curve_fit(_exp_decay, _gdp_raw_times, _gdp_raw_amps,
                          p0=[5, 0.02, 3], maxfev=10000)
_gdp_trend = _exp_decay(_gdp_raw_times, *_gdp_popt)
_gdp_residuals = _gdp_raw_amps - _gdp_trend
_gdp_shift = abs(np.min(_gdp_residuals)) + 1.0  # ensure all positive

# Detrended GDP peaks: residual + shift so wave oscillates around positive center
GDP_DETRENDED = list(zip(_gdp_raw_times, _gdp_residuals + _gdp_shift))


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
print("Script 239 — US Economic Cycle Test")
print("=" * 78)
print()

# ── Setup ──
unemp_times = np.array([p[0] for p in UNEMP_PEAKS])
unemp_amps = np.array([p[1] for p in UNEMP_PEAKS])
unemp_period = np.mean(np.diff(unemp_times))

gdp_times = np.array([p[0] for p in GDP_DETRENDED])
gdp_amps = np.array([p[1] for p in GDP_DETRENDED])
gdp_period = np.mean(np.diff(gdp_times))

print("DATA:")
print()
print(f"  UNEMPLOYMENT peaks: {len(UNEMP_PEAKS)}")
for t, a in UNEMP_PEAKS:
    print(f"    {t:.1f}  {a:.1f}%")
print(f"  Mean interval: {unemp_period:.1f} years")
print(f"  Range: {min(unemp_amps):.1f} - {max(unemp_amps):.1f}%")
print()
print(f"  GDP GROWTH (detrended) peaks: {len(GDP_DETRENDED)}")
print(f"  Trend removed: {_gdp_popt[0]:.3f} * exp(-{_gdp_popt[1]:.5f} * (t-1950)) + {_gdp_popt[2]:.3f}")
for i, (t, a) in enumerate(GDP_DETRENDED):
    raw = GDP_PEAKS[i][1]
    print(f"    {t:.1f}  raw={raw:.1f}%  detrended={a:.3f}")
print(f"  Mean interval: {gdp_period:.1f} years")
print(f"  Range: {min(gdp_amps):.3f} - {max(gdp_amps):.3f}")
print()


# ── ARA SCAN ──
print("=" * 78)
print("ARA SCAN (fit MAE at grid 80×40)")
print("=" * 78)
print()

ara_candidates = [0.15, 0.3, 0.5, 1/PHI, 0.75, 1.0, 1.2, 1.35, PHI, 2.0]

for sys_name, times, amps, period in [
    ("Unemployment", unemp_times, unemp_amps, unemp_period),
    ("GDP Growth", gdp_times, gdp_amps, gdp_period),
]:
    print(f"{sys_name}:")
    print(f"  {'ARA':>6} {'φ-dist':>7} {'midline':>8} {'fitMAE':>8}")
    best = {'mae': 1e9}
    mean_amp = np.mean(amps)
    ba_lo = mean_amp * 0.15
    ba_hi = mean_amp * 2.0
    for ara in ara_candidates:
        fn = make_predict_fn(midline_camshaft)
        res = grid_best(fn, times, amps, ara, period, ba_lo, ba_hi)
        pd = _phi_dist(ara)
        ml = midline_camshaft(ara)
        print(f"  {ara:>6.3f} {pd:>7.3f} {ml:>8.4f} {res['mae']:>8.3f}")
        if res['mae'] < best['mae']:
            best = {'mae': res['mae'], 'ara': ara}
    print(f"\n  → Best ARA: {best['ara']:.3f} (fitMAE={best['mae']:.3f})")
    print()


# ── Use best ARAs for LOO ──
# Re-scan to get best
def find_best_ara(times, amps, period):
    mean_amp = np.mean(amps)
    ba_lo = mean_amp * 0.15
    ba_hi = mean_amp * 2.0
    best = {'mae': 1e9}
    for ara in ara_candidates:
        fn = make_predict_fn(midline_camshaft)
        res = grid_best(fn, times, amps, ara, period, ba_lo, ba_hi)
        if res['mae'] < best['mae']:
            best = {'mae': res['mae'], 'ara': ara}
    return best['ara']

unemp_ara = find_best_ara(unemp_times, unemp_amps, unemp_period)
gdp_ara = find_best_ara(gdp_times, gdp_amps, gdp_period)

print("=" * 78)
print("LOO CROSS-VALIDATION")
print("=" * 78)
print()

configs = [
    ("Baseline",   predict_baseline),
    ("Camshaft",   make_predict_fn(midline_camshaft)),
]

systems = {
    'Unemployment': {
        'times': unemp_times, 'peaks': unemp_amps,
        'ara': unemp_ara, 'period': unemp_period,
    },
    'GDP_Growth': {
        'times': gdp_times, 'peaks': gdp_amps,
        'ara': gdp_ara, 'period': gdp_period,
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

    print(f"── {sys_name.upper()} (ARA={ara:.3f}, φ-dist={pd:.3f}, midline={ml:.4f}, period={period:.1f}y) ──")

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

        sine_delta = sine_loo - loo_mae
        sine_pct = (sine_delta / sine_loo) * 100 if sine_loo > 0 else 0

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
print(f"  {'System':<15} {'ARA':>6} {'Sine LOO':>10} {'Base LOO':>10} "
      f"{'Camshaft':>10} {'vs Sine':>10}")
for sys_name, r in all_results.items():
    cfg = systems[sys_name]
    vsine = r['Sine'] - r['Camshaft']
    pct = (vsine / r['Sine']) * 100 if r['Sine'] > 0 else 0
    print(f"  {sys_name:<15} {cfg['ara']:>6.3f} {r['Sine']:>10.3f} "
          f"{r['Baseline']:>10.3f} {r['Camshaft']:>10.3f} {pct:>+9.1f}%")

print()

# ── FULL CROSS-DOMAIN TABLE ──
print("=" * 78)
print("ALL SYSTEMS TESTED (Scripts 237k2–239)")
print("=" * 78)
print()
print(f"  {'System':<15} {'ARA':>6} {'φ-dist':>7} {'Zone':<12} {'Midline':>8}")
print(f"  {'─'*15} {'─'*6} {'─'*7} {'─'*12} {'─'*8}")
all_sys = [
    ('Solar',        PHI    ),
    ('ENSO',         2.0    ),
    ('Earthquake',   0.15   ),
    ('Heart',        1.35   ),
    ('Hare',         1.0    ),
    ('Lynx',         1.0    ),
    ('Unemployment', unemp_ara),
    ('GDP Growth',   gdp_ara),
]
for name, ara in all_sys:
    pd = _phi_dist(ara)
    ml = midline_camshaft(ara)
    zone = 'Palindrome' if pd <= 1/PHI else ('Ramp' if pd < 1.0 else 'Full')
    print(f"  {name:<15} {ara:>6.3f} {pd:>7.3f} {zone:<12} {ml:.4f}")

print()
elapsed = clock_time.time() - t_start
print(f"Total runtime: {elapsed:.0f}s")
