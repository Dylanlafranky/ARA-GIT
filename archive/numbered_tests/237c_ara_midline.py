#!/usr/bin/env python3
"""
Script 237c — ARA Midline on 226 v4 Engine

Dylan's insight: "Can we oscillate the wave line around the ARA of the
system? The dynamic ARA or the ARA from the system above."

The cascade shape currently oscillates around 1.0:
  amplitude = base_amp * shape  (shape ≈ 1.0 ± modulation)

Instead, oscillate around the system's ARA:
  amplitude = base_amp * (shape + ARA - 1)

For solar (ARA = φ ≈ 1.618):
  shape oscillates around φ, not 1.0
  The vertical pipe delivers φ units before horizontal cascade runs

Three variants tested:
  A. Fixed ARA midline (φ for solar — the system's identity)
  B. Dynamic ARA midline (prev_amp / base_amp — instantaneous state)
  C. ARA from above (if the system above has ARA_above, midline = ARA_above)
     For solar sitting below the galactic scale, this would be the
     galactic ARA — but we approximate as 2.0 (pure harmonic / top of scale)

Built on 226 v4 ARASystem which has LOO MAE 31.94.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9
LOG2 = np.log(2)
TAU = 2 * np.pi

# ================================================================
# IMPORT 226 v4 CHAMPION
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
n_cycles = len(times)

# ================================================================
# ARA-MIDLINE PREDICTION FUNCTIONS
# ================================================================

def predict_baseline(sys226, times, peaks, t_ref, base_amp):
    """Standard 226 v4 — shape oscillates around 1.0."""
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        pred = sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev)
        preds.append(pred)
    return np.array(preds)


def predict_fixed_ara_midline(sys226, times, peaks, t_ref, base_amp, midline_ara):
    """Shape oscillates around midline_ara instead of 1.0.

    amplitude = base_amp * (shape + midline_ara - 1.0)

    When midline_ara = 1.0, this is identical to baseline.
    When midline_ara = φ, the wave sits higher — vertical gift from above.
    """
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        # Get the standard prediction (= base_amp * shape)
        std_pred = sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev)
        # The shape is std_pred / base_amp. Shift its center from 1.0 to midline_ara.
        shape = std_pred / base_amp
        shifted_shape = shape + (midline_ara - 1.0)
        preds.append(base_amp * shifted_shape)
    return np.array(preds)


def predict_dynamic_ara_midline(sys226, times, peaks, t_ref, base_amp):
    """Shape oscillates around the instantaneous ARA (prev_amp / base_amp).

    Each cycle, the midline shifts based on the previous cycle's energy.
    High prev → high midline (engine momentum carries forward)
    Low prev → low midline (depleted system sits lower)

    When no prev_amp: use the system's fixed ARA (φ for solar).
    """
    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None

        # Dynamic midline
        if prev is not None:
            midline = prev / base_amp  # instantaneous ARA
        else:
            midline = PHI  # system's natural ARA

        std_pred = sys226.predict_amplitude(times[k], t_ref, base_amp, prev_amp=prev)
        shape = std_pred / base_amp
        shifted_shape = shape + (midline - 1.0)
        preds.append(base_amp * shifted_shape)
    return np.array(preds)


def predict_blended_ara_midline(sys226, times, peaks, t_ref, base_amp, blend):
    """Blend between fixed (1.0) and system ARA (φ) midline.

    blend = 0.0 → standard (midline = 1.0)
    blend = 1.0 → full ARA midline (midline = φ)
    blend = 0.5 → halfway
    """
    midline = 1.0 + blend * (PHI - 1.0)
    return predict_fixed_ara_midline(sys226, times, peaks, t_ref, base_amp, midline)


# ================================================================
# GRID SEARCH
# ================================================================

print("=" * 78)
print("237c — ARA Midline on 226 v4 Engine")
print("=" * 78)
print()

gleissberg = period * PHI**4
data_span = times[-1] - times[0]
tr_lo = times[0] - max(gleissberg, data_span)
tr_hi = times[0] + 2 * period

# ── A: 226 v4 baseline (midline = 1.0) ──
print("A. 226 v4 baseline (midline = 1.0)...")
sys226 = ARASystem("Solar", PHI, period, times, peaks)
best_base = {'mae': 1e9}
for tr in np.linspace(tr_lo, tr_hi, 80):
    for ba in np.linspace(np.mean(peaks)*0.5, np.mean(peaks)*1.5, 40):
        preds = predict_baseline(sys226, times, peaks, tr, ba)
        mae = np.mean(np.abs(preds - peaks))
        if mae < best_base['mae']:
            best_base = {'mae': mae, 'tr': tr, 'ba': ba}
print(f"   MAE {best_base['mae']:.2f}, t_ref={best_base['tr']:.2f}, "
      f"base_amp={best_base['ba']:.2f}")

# ── B: Fixed ARA midline (φ) ──
print("B. Fixed ARA midline (φ ≈ 1.618)...")
best_phi = {'mae': 1e9}
ba_lo_phi = np.mean(peaks) * 0.2
ba_hi_phi = np.mean(peaks) * 1.5
for tr in np.linspace(tr_lo, tr_hi, 80):
    for ba in np.linspace(ba_lo_phi, ba_hi_phi, 40):
        sys_t = ARASystem("Solar", PHI, period, times, peaks)
        preds = predict_fixed_ara_midline(sys_t, times, peaks, tr, ba, PHI)
        mae = np.mean(np.abs(preds - peaks))
        if mae < best_phi['mae']:
            best_phi = {'mae': mae, 'tr': tr, 'ba': ba}
print(f"   MAE {best_phi['mae']:.2f}, t_ref={best_phi['tr']:.2f}, "
      f"base_amp={best_phi['ba']:.2f}")

# ── C: Dynamic ARA midline (prev_amp / base_amp) ──
print("C. Dynamic ARA midline (instantaneous)...")
best_dyn = {'mae': 1e9}
for tr in np.linspace(tr_lo, tr_hi, 80):
    for ba in np.linspace(ba_lo_phi, ba_hi_phi, 40):
        sys_t = ARASystem("Solar", PHI, period, times, peaks)
        preds = predict_dynamic_ara_midline(sys_t, times, peaks, tr, ba)
        mae = np.mean(np.abs(preds - peaks))
        if mae < best_dyn['mae']:
            best_dyn = {'mae': mae, 'tr': tr, 'ba': ba}
print(f"   MAE {best_dyn['mae']:.2f}, t_ref={best_dyn['tr']:.2f}, "
      f"base_amp={best_dyn['ba']:.2f}")

# ── D: Blended ARA midline (scan blend factor) ──
print("D. Blended ARA midline (scanning blend factor)...")
best_blend = {'mae': 1e9}
for blend in np.linspace(0, 1, 21):
    for tr in np.linspace(tr_lo, tr_hi, 80):
        for ba in np.linspace(ba_lo_phi, ba_hi_phi, 40):
            sys_t = ARASystem("Solar", PHI, period, times, peaks)
            preds = predict_blended_ara_midline(sys_t, times, peaks, tr, ba, blend)
            mae = np.mean(np.abs(preds - peaks))
            if mae < best_blend['mae']:
                best_blend = {'mae': mae, 'tr': tr, 'ba': ba, 'blend': blend}
print(f"   MAE {best_blend['mae']:.2f}, t_ref={best_blend['tr']:.2f}, "
      f"base_amp={best_blend['ba']:.2f}, blend={best_blend['blend']:.2f}")

# ── E: INV_PHI midline (ARA from below) ──
print("E. INV_PHI midline (consumer perspective)...")
best_inv = {'mae': 1e9}
for tr in np.linspace(tr_lo, tr_hi, 80):
    for ba in np.linspace(np.mean(peaks)*0.3, np.mean(peaks)*2.0, 40):
        sys_t = ARASystem("Solar", PHI, period, times, peaks)
        preds = predict_fixed_ara_midline(sys_t, times, peaks, tr, ba, INV_PHI)
        mae = np.mean(np.abs(preds - peaks))
        if mae < best_inv['mae']:
            best_inv = {'mae': mae, 'tr': tr, 'ba': ba}
print(f"   MAE {best_inv['mae']:.2f}, t_ref={best_inv['tr']:.2f}, "
      f"base_amp={best_inv['ba']:.2f}")

print()

# ================================================================
# PICK BEST AND RUN DETAILS
# ================================================================

configs = {
    'A: baseline (1.0)': (best_base, 1.0, False),
    'B: fixed φ': (best_phi, PHI, False),
    'C: dynamic ARA': (best_dyn, None, True),
    'D: blended': (best_blend, 1.0 + best_blend['blend'] * (PHI - 1.0), False),
    'E: INV_PHI': (best_inv, INV_PHI, False),
}

print("Summary:")
for name, (cfg, _, _) in configs.items():
    print(f"  {name:>25}: MAE {cfg['mae']:.2f}")
print()

# Find overall best
best_name = min(configs, key=lambda k: configs[k][0]['mae'])
best_cfg, best_midline, best_is_dynamic = configs[best_name]

print(f"Best: {best_name}")
print(f"Cascade MAE: {best_cfg['mae']:.2f}")
print()

# Per-cycle detail
sys226 = ARASystem("Solar", PHI, period, times, peaks)

baseline_preds = predict_baseline(sys226, times, peaks, best_base['tr'], best_base['ba'])

if best_is_dynamic:
    best_preds = predict_dynamic_ara_midline(
        sys226, times, peaks, best_cfg['tr'], best_cfg['ba'])
elif 'blend' in best_cfg:
    best_preds = predict_blended_ara_midline(
        sys226, times, peaks, best_cfg['tr'], best_cfg['ba'], best_cfg['blend'])
else:
    best_preds = predict_fixed_ara_midline(
        sys226, times, peaks, best_cfg['tr'], best_cfg['ba'], best_midline)

print(f"{'Cycle':<6} {'Year':>6} {'Actual':>7} {'Base':>7} {'Best':>7} "
      f"{'BaseErr':>8} {'BestErr':>8} {'Better':>7}")
print("─" * 70)

for k in range(n_cycles):
    be_base = abs(baseline_preds[k] - peaks[k])
    be_best = abs(best_preds[k] - peaks[k])
    better = "  ✓" if be_best < be_base - 0.5 else ""
    print(f"  C{k+1:<4} {times[k]:>6.1f} {peaks[k]:>7.1f} {baseline_preds[k]:>7.1f} "
          f"{best_preds[k]:>7.1f} {be_base:>8.1f} {be_best:>8.1f} {better}")

print()
early = list(range(0, 7))
late = list(range(7, 25))

for label, preds in [('baseline', baseline_preds), (best_name, best_preds)]:
    mae_all = np.mean(np.abs(preds - peaks))
    mae_e = np.mean(np.abs(preds[early] - peaks[early]))
    mae_l = np.mean(np.abs(preds[late] - peaks[late]))
    print(f"  {label:>25}: MAE={mae_all:.2f}  early={mae_e:.2f}  late={mae_l:.2f}")

# ================================================================
# LOO — RUN ON ALL NON-BASELINE CONFIGS
# ================================================================

print()
print("=" * 78)
print("LOO Cross-Validation")
print("=" * 78)
print()

def run_loo(predict_fn, ba_lo, ba_hi, label):
    """Generic LOO runner."""
    loo_errors = []
    for hold_idx in range(n_cycles):
        train_mask = np.ones(n_cycles, dtype=bool)
        train_mask[hold_idx] = False
        train_times = times[train_mask]
        train_peaks = peaks[train_mask]

        tr_lo_loo = train_times[0] - max(gleissberg, train_times[-1] - train_times[0])
        tr_hi_loo = train_times[0] + 2 * period

        best_loo = {'mae': 1e9}
        for tr in np.linspace(tr_lo_loo, tr_hi_loo, 80):
            for ba in np.linspace(ba_lo, ba_hi, 40):
                sys_t = ARASystem("Solar", PHI, period, train_times, train_peaks)
                preds = predict_fn(sys_t, train_times, train_peaks, tr, ba)
                mae = np.mean(np.abs(preds - train_peaks))
                if mae < best_loo['mae']:
                    best_loo = {'mae': mae, 'tr': tr, 'ba': ba}

        # Predict held-out
        sys_full = ARASystem("Solar", PHI, period, times, peaks)
        preds_full = predict_fn(sys_full, times, peaks, best_loo['tr'], best_loo['ba'])
        error = abs(preds_full[hold_idx] - peaks[hold_idx])
        loo_errors.append(error)

    loo_mae = np.mean(loo_errors)
    sine_mae = np.mean(np.abs(peaks - np.mean(peaks)))
    return loo_mae, loo_errors

# Baseline LOO
print("Running LOO: A (baseline)...")
loo_base, loo_base_errors = run_loo(
    lambda s, t, p, tr, ba: predict_baseline(s, t, p, tr, ba),
    np.mean(peaks)*0.5, np.mean(peaks)*1.5, "baseline")
print(f"  A baseline:     LOO MAE {loo_base:.2f}")

# Fixed φ LOO
print("Running LOO: B (fixed φ)...")
loo_phi, loo_phi_errors = run_loo(
    lambda s, t, p, tr, ba: predict_fixed_ara_midline(s, t, p, tr, ba, PHI),
    ba_lo_phi, ba_hi_phi, "fixed φ")
print(f"  B fixed φ:      LOO MAE {loo_phi:.2f}")

# Dynamic ARA LOO
print("Running LOO: C (dynamic ARA)...")
loo_dyn, loo_dyn_errors = run_loo(
    lambda s, t, p, tr, ba: predict_dynamic_ara_midline(s, t, p, tr, ba),
    ba_lo_phi, ba_hi_phi, "dynamic ARA")
print(f"  C dynamic ARA:  LOO MAE {loo_dyn:.2f}")

# Blended LOO (at best blend)
blend_val = best_blend['blend']
print(f"Running LOO: D (blend={blend_val:.2f})...")
loo_bld, loo_bld_errors = run_loo(
    lambda s, t, p, tr, ba: predict_blended_ara_midline(s, t, p, tr, ba, blend_val),
    ba_lo_phi, ba_hi_phi, f"blend={blend_val:.2f}")
print(f"  D blend={blend_val:.2f}:   LOO MAE {loo_bld:.2f}")

# INV_PHI LOO
print("Running LOO: E (INV_PHI)...")
loo_inv, loo_inv_errors = run_loo(
    lambda s, t, p, tr, ba: predict_fixed_ara_midline(s, t, p, tr, ba, INV_PHI),
    np.mean(peaks)*0.3, np.mean(peaks)*2.0, "INV_PHI")
print(f"  E INV_PHI:      LOO MAE {loo_inv:.2f}")

sine_mae = np.mean(np.abs(peaks - np.mean(peaks)))

print()
print("─" * 78)
print("FINAL COMPARISON")
print("─" * 78)
print()
print(f"  {'Config':<30} {'Cascade':>10} {'LOO':>10} {'vs Sine':>10}")
print(f"  {'─'*30} {'─'*10} {'─'*10} {'─'*10}")
print(f"  {'A: baseline (1.0)':<30} {best_base['mae']:>10.2f} {loo_base:>10.2f} "
      f"{(1-loo_base/sine_mae)*100:>+9.1f}%")
print(f"  {'B: fixed φ':<30} {best_phi['mae']:>10.2f} {loo_phi:>10.2f} "
      f"{(1-loo_phi/sine_mae)*100:>+9.1f}%")
print(f"  {'C: dynamic ARA':<30} {best_dyn['mae']:>10.2f} {loo_dyn:>10.2f} "
      f"{(1-loo_dyn/sine_mae)*100:>+9.1f}%")
print(f"  {f'D: blend={blend_val:.2f}':<30} {best_blend['mae']:>10.2f} {loo_bld:>10.2f} "
      f"{(1-loo_bld/sine_mae)*100:>+9.1f}%")
print(f"  {'E: INV_PHI':<30} {best_inv['mae']:>10.2f} {loo_inv:>10.2f} "
      f"{(1-loo_inv/sine_mae)*100:>+9.1f}%")
print()
print(f"  226 v4 champion: Cascade 27.17, LOO 31.94 ({(1-31.94/sine_mae)*100:+.1f}% vs sine)")
print(f"  Sine MAE: {sine_mae:.2f}")
print()

# Find LOO champion
all_loo = {'A': loo_base, 'B': loo_phi, 'C': loo_dyn, 'D': loo_bld, 'E': loo_inv}
best_loo_name = min(all_loo, key=all_loo.get)
best_loo_val = all_loo[best_loo_name]

if best_loo_val < 31.94:
    print(f"  *** NEW LOO CHAMPION: {best_loo_name} (MAE {best_loo_val:.2f}) ***")
elif best_loo_val < sine_mae:
    print(f"  Best LOO: {best_loo_name} ({best_loo_val:.2f}) — beats sine, not champion")
else:
    print(f"  Best LOO: {best_loo_name} ({best_loo_val:.2f}) — does not beat sine")

elapsed = clock_time.time() - t_start
print()
print(f"Total time: {elapsed:.1f}s")
print("=" * 78)
