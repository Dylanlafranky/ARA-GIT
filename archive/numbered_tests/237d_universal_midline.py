#!/usr/bin/env python3
"""
Script 237d — Universal ARA Midline (both engines, no hardcoded numbers)

The wave midline = 1 + blend × (ARA - 1), where blend comes from
the system's own geometry — NOT a tuned constant.

Candidate blend factors (all from φ):
  1/φ⁴ = 0.146  — the π-leak / pipe leak
  1/φ³ = 0.236  — momentum fraction
  1/φ² = 0.382  — acc_frac for an engine (gate position)
  1/φ  = 0.618  — the golden ratio complement
  1/(1+φ) = 1/φ² = 0.382 — fraction of energy that stays
  acc_frac(ARA) = 1/(1+ARA) — system-dependent gate position

For solar: acc_frac(φ) = 1/(1+φ) = 1/φ² = 0.382

The blend should be derivable from the system's ARA alone,
so it works universally across data sources.

Tests both 226 v4 and 235b engines.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2
PHI_2 = PHI ** 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9
LOG2 = math.log(2)
TAU = 2 * math.pi
TWO_OVER_PHI = 2.0 / PHI
TWO_PHI = 2.0 * PHI
PHI_LEAK = INV_PHI_4
MOMENTUM_FRAC = INV_PHI_3

# ================================================================
# IMPORT BOTH ENGINES
# ================================================================

# 226 v4
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

# 235b
exec_235b = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '235b_universal_vehicle.py')
with open(exec_235b, 'r') as f:
    code_235b = f.read()
lines_235b = code_235b.split('\n')
cut_235b = None
for i, line in enumerate(lines_235b):
    if line.strip().startswith('print("="') and i > 100:
        cut_235b = i
        break
ns_235b = {}
exec('\n'.join(lines_235b[:cut_235b]), ns_235b)
ARANode = ns_235b['ARANode']

# ================================================================
# SOLAR DATA
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

times = np.array([p[0] for p in solar_peaks])
peaks = np.array([p[1] for p in solar_peaks])
period = 11.07
ara_solar = PHI
n_cycles = len(times)

# ================================================================
# UNIVERSAL MIDLINE FUNCTION
# ================================================================

def ara_midline(ara):
    """Compute the wave midline offset from the system's ARA.

    The vertical pipe delivers energy proportional to the system's
    gate position. acc_frac = 1/(1+ARA) is the fraction of the
    Gleissberg cycle spent accumulating. This IS the fraction of
    the system-above's energy that persists as a standing offset.

    midline = 1 + acc_frac(ARA) × (ARA - 1)

    For solar (ARA=φ): acc_frac = 1/φ² = 0.382
      midline = 1 + 0.382 × 0.618 = 1.236

    For a consumer (ARA=1/φ): acc_frac = 1/(1+1/φ) = 1/φ = 0.618
      midline = 1 + 0.618 × (-0.382) = 0.764

    For a clock (ARA=1): acc_frac = 0.5
      midline = 1 + 0.5 × 0 = 1.0  (no shift — symmetric)

    This is universal: derived purely from ARA.
    """
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)


# ================================================================
# PREDICTION FUNCTIONS
# ================================================================

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


def predict_226_baseline(times, peaks, t_ref, base_amp, ara, period):
    """226 v4 standard (no midline)."""
    sys226 = ARASystem("sys", ara, period, times, peaks)
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        preds.append(sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev))
    return np.array(preds)


def predict_235b_midline(times, peaks, t_ref, base_amp, ara, period):
    """235b ARANode with ARA midline shift."""
    midline = ara_midline(ara)
    preds = []
    for k in range(len(times)):
        node = ARANode("m", period, ara, 0, base_amp, "engine")
        node.set_t_ref(t_ref)
        node.prev_amp = peaks[k-1] if k > 0 else None
        node.amp_history = list(peaks[:k]) if k > 0 else []
        std_pred = node.cascade_amplitude(times[k])
        shape = std_pred / base_amp
        shifted = shape + (midline - 1.0)
        preds.append(base_amp * shifted)
    return np.array(preds)


def predict_235b_baseline(times, peaks, t_ref, base_amp, ara, period):
    """235b ARANode standard (no midline)."""
    preds = []
    for k in range(len(times)):
        node = ARANode("b", period, ara, 0, base_amp, "engine")
        node.set_t_ref(t_ref)
        node.prev_amp = peaks[k-1] if k > 0 else None
        node.amp_history = list(peaks[:k]) if k > 0 else []
        preds.append(node.cascade_amplitude(times[k]))
    return np.array(preds)


# ================================================================
# UNIVERSAL GRID SEARCH
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
# RUN ALL VARIANTS
# ================================================================

print("=" * 78)
print("237d — Universal ARA Midline (both engines)")
print("=" * 78)
print()

midline_val = ara_midline(ara_solar)
acc_frac = 1.0 / (1.0 + ara_solar)
print(f"System ARA: {ara_solar:.4f} (φ)")
print(f"acc_frac = 1/(1+ARA) = {acc_frac:.4f}")
print(f"Midline = 1 + {acc_frac:.4f} × ({ara_solar:.4f} - 1) = {midline_val:.4f}")
print()

# Base_amp ranges
ba_std_lo = np.mean(peaks) * 0.5
ba_std_hi = np.mean(peaks) * 1.5
ba_mid_lo = np.mean(peaks) * 0.25  # wider for midline variants
ba_mid_hi = np.mean(peaks) * 1.5

configs = [
    ("226 baseline",    predict_226_baseline,  ba_std_lo, ba_std_hi),
    ("226 + midline",   predict_226_midline,   ba_mid_lo, ba_mid_hi),
    ("235b baseline",   predict_235b_baseline, ba_std_lo, ba_std_hi),
    ("235b + midline",  predict_235b_midline,  ba_mid_lo, ba_mid_hi),
]

print(f"{'Config':<20} {'Cascade':>10} {'base_amp':>10} {'t_ref':>10}")
print("─" * 55)

cascade_results = {}
for name, fn, ba_lo, ba_hi in configs:
    best = grid_search(fn, times, peaks, ara_solar, period, ba_lo, ba_hi)
    cascade_results[name] = best
    print(f"  {name:<20} {best['mae']:>8.2f} {best['ba']:>10.2f} {best['tr']:>10.2f}")

print()

# ================================================================
# PER-CYCLE DETAIL FOR BEST OF EACH ENGINE
# ================================================================

for engine in ['226', '235b']:
    base_name = f'{engine} baseline'
    mid_name = f'{engine} + midline'
    base_p = cascade_results[base_name]['preds']
    mid_p = cascade_results[mid_name]['preds']

    print(f"── {engine} per-cycle ──")
    print(f"{'C':<5} {'Year':>6} {'Act':>6} {'Base':>7} {'Mid':>7} "
          f"{'BErr':>6} {'MErr':>6} {'Win':>4}")
    improved = 0
    for k in range(n_cycles):
        be = abs(base_p[k] - peaks[k])
        me = abs(mid_p[k] - peaks[k])
        win = " ✓" if me < be - 0.5 else ""
        if me < be - 0.5:
            improved += 1
        print(f"  C{k+1:<3} {times[k]:>6.1f} {peaks[k]:>6.1f} {base_p[k]:>7.1f} "
              f"{mid_p[k]:>7.1f} {be:>6.1f} {me:>6.1f} {win}")
    print(f"  Improved: {improved}/{n_cycles}")
    print()

# ================================================================
# LOO CROSS-VALIDATION — ALL FOUR
# ================================================================

print("=" * 78)
print("LOO Cross-Validation")
print("=" * 78)
print()

loo_results = {}
for name, fn, ba_lo, ba_hi in configs:
    print(f"  Running LOO: {name}...")
    loo_mae, loo_errs, loo_preds = run_loo(
        fn, times, peaks, ara_solar, period, ba_lo, ba_hi)
    loo_results[name] = {
        'mae': loo_mae, 'errors': loo_errs, 'preds': loo_preds
    }
    print(f"    LOO MAE: {loo_mae:.2f}")

sine_mae = np.mean(np.abs(peaks - np.mean(peaks)))

print()
print("─" * 78)
print("FINAL COMPARISON")
print("─" * 78)
print()
print(f"  {'Config':<20} {'Cascade':>10} {'LOO':>10} {'vs Sine':>10} {'vs Champ':>10}")
print(f"  {'─'*20} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")

for name in cascade_results:
    c_mae = cascade_results[name]['mae']
    l_mae = loo_results[name]['mae']
    vs_sine = (1 - l_mae/sine_mae) * 100
    vs_champ = 31.94 - l_mae
    marker = " ***" if l_mae < 31.94 else ""
    print(f"  {name:<20} {c_mae:>10.2f} {l_mae:>10.2f} "
          f"{vs_sine:>+9.1f}% {vs_champ:>+9.2f}{marker}")

print()
print(f"  Sine MAE: {sine_mae:.2f}")
print(f"  Previous champion: 226 v4, LOO 31.94")
print()

# Midline derivation summary
print("─" * 78)
print("MIDLINE DERIVATION (universal, no hardcoded numbers)")
print("─" * 78)
print()
print(f"  For any system with ARA value 'a':")
print(f"    acc_frac = 1 / (1 + a)")
print(f"    midline  = 1 + acc_frac × (a - 1)")
print()
print(f"  Examples:")
for name, a in [("Consumer (1/φ)", INV_PHI), ("Clock (1.0)", 1.0),
                ("Engine (φ)", PHI), ("Exothermic (√3)", math.sqrt(3))]:
    ml = ara_midline(a)
    af = 1.0 / (1.0 + a)
    print(f"    {name:>20}: ARA={a:.3f}, acc={af:.3f}, midline={ml:.4f}")

print()

# Per-cycle LOO detail for best LOO config
best_loo_name = min(loo_results, key=lambda k: loo_results[k]['mae'])
print(f"Best LOO: {best_loo_name} (MAE {loo_results[best_loo_name]['mae']:.2f})")
print()

bl = loo_results[best_loo_name]
print(f"{'C':<5} {'Year':>6} {'Actual':>7} {'Pred':>7} {'Error':>7} {'Rel%':>7}")
print("─" * 45)
for k in range(n_cycles):
    err = bl['errors'][k]
    rel = err / peaks[k] * 100
    print(f"  C{k+1:<3} {times[k]:>6.1f} {peaks[k]:>7.1f} {bl['preds'][k]:>7.1f} "
          f"{err:>7.1f} {rel:>6.1f}%")

early = list(range(0, 7))
late = list(range(7, 25))
loo_e = np.mean(np.array(bl['errors'])[early])
loo_l = np.mean(np.array(bl['errors'])[late])
print()
print(f"  Early (C1-C7): {loo_e:.2f}")
print(f"  Late (C8-C25): {loo_l:.2f}")

if loo_results[best_loo_name]['mae'] < 31.94:
    print()
    print("  *** NEW LOO CHAMPION ***")

elapsed = clock_time.time() - t_start
print()
print(f"Total time: {elapsed:.1f}s")
print("=" * 78)
