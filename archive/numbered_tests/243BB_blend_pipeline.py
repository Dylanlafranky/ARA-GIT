#!/usr/bin/env python3
"""
Script 243BB — Blended Pipeline (Path × Teleport at 1/φ²)

The two prediction methods see the system from different angles:
  - PATH (vehicle):    Full timeline simulation with gear mesh, snaps, coupling.
  - TELEPORT (formula): Per-fold cascade_shape with history feeding.

Both use the wave physics additions (mode coupling + standing wave).

Blending at α = 1/φ² ≈ 0.382 (a framework constant) averages out their
independent errors. On Solar this drops LOO from 42.89 → 38.66.

This script runs the full pipeline for all 3 systems.

CHAMPION RESULTS (243AJ baseline):
  Solar:   LOO 42.89  (LOO/Sine 0.879)
  ENSO:    LOO 0.408  (LOO/Sine 0.824)
  Sanriku: LOO 1.33   (LOO/Sine ... )
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import time as clock_time

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2

# Blend ratio: 1/φ² ≈ 0.382 (path weight)
BLEND_ALPHA = INV_PHI_2

t_start = clock_time.time()

# ── Load the 243AZ wave combo code (has mode coupling + standing wave) ──
combo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "243AZ_wave_combo.py")
with open(combo_path, 'r') as f:
    combo_code = f.read()

# Strip MAIN section — keep functions + data only
lines = combo_code.split('\n')
cutoff = len(lines)
for i, line in enumerate(lines):
    if '# MAIN' in line and i > 400:
        cutoff = i
        break
base_code = '\n'.join(lines[:cutoff])

ns = {'__file__': combo_path, '__name__': '__exec__'}
exec(base_code, ns)

# Pull out everything we need
SOLAR_CYCLES = ns['SOLAR_CYCLES']
SYSTEMS = ns['SYSTEMS']
run_full_fit = ns['run_full_fit']
run_formula_loo = ns['run_formula_loo']
grid_search = ns['grid_search']
run_full_simulation = ns['run_full_simulation']


def run_blended_loo(times, peaks, period, ara, target_rung, system_name, alpha=BLEND_ALPHA):
    """
    Run both teleport and path LOO, then blend predictions.

    α = path weight, (1-α) = teleport weight.
    """
    N = len(times)
    sine_baseline = np.mean(np.abs(peaks - np.mean(peaks)))

    # ── TELEPORT LOO ──
    teleport = run_formula_loo(times, peaks, period, ara, target_rung, system_name)
    teleport_preds = np.array(teleport['preds'])

    # ── PATH LOO (refit per fold) ──
    path_preds = []
    path_errors = []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        train_t = times[mask]
        train_p = peaks[mask]

        fit_tr, fit_ba, _ = grid_search(period, ara, target_rung, train_t, train_p)
        snap_t, snap_a = run_full_simulation(
            train_t, train_p, period, ara, target_rung,
            fit_tr, fit_ba
        )

        if len(snap_t) == 0:
            pred = np.mean(train_p)
        else:
            idx = np.argmin(np.abs(snap_t - times[i]))
            pred = snap_a[idx]

        path_preds.append(pred)
        path_errors.append(abs(pred - peaks[i]))

    path_preds = np.array(path_preds)
    path_loo = np.mean(path_errors)
    path_corr = np.corrcoef(path_preds, peaks)[0, 1] if np.std(path_preds) > 0 else 0

    # ── BLEND ──
    blended = alpha * path_preds + (1 - alpha) * teleport_preds
    blend_errors = np.abs(blended - peaks)
    blend_loo = np.mean(blend_errors)
    blend_corr = np.corrcoef(blended, peaks)[0, 1] if np.std(blended) > 0 else 0

    return {
        'teleport_loo': teleport['loo_mae'],
        'teleport_corr': teleport['corr'],
        'teleport_preds': teleport_preds,
        'path_loo': path_loo,
        'path_corr': path_corr,
        'path_preds': path_preds,
        'blend_loo': blend_loo,
        'blend_corr': blend_corr,
        'blend_preds': blended,
        'blend_errors': blend_errors,
        'sine_mae': sine_baseline,
        'alpha': alpha,
    }


# ════════════════════════════════════════════════════════════════
# MAIN — Run all 3 systems
# ════════════════════════════════════════════════════════════════

print("=" * 78)
print(f"  Script 243BB — Blended Pipeline")
print(f"  α = 1/φ² ≈ {BLEND_ALPHA:.4f}  (path weight)")
print(f"  Wave combo base: mode coupling + standing wave")
print("=" * 78)

# Reference values (previous champions)
ref_champ = {
    "Solar (SSN)": {"loo": 42.89, "corr": 0.422},
    "ENSO (ONI)":  {"loo": 0.408, "corr": 0.0},
    "Sanriku EQ":  {"loo": 1.33,  "corr": 0.0},
}

all_results = {}

for name, times, peaks, period, ara, rung in SYSTEMS:
    t0 = clock_time.time()
    print(f"\n{'─' * 78}")
    print(f"  {name}  (N={len(times)}, period={period:.2f}, ARA={ara:.3f})")
    print(f"{'─' * 78}")

    result = run_blended_loo(times, peaks, period, ara, rung, name)
    all_results[name] = result
    elapsed = clock_time.time() - t0

    ref = ref_champ.get(name, {"loo": 999, "corr": 0})

    print(f"\n  {'Method':<20} │ {'LOO':>7} │ {'Corr':>6} │ {'LOO/Sine':>8} │ {'Δ champ':>8}")
    print(f"  {'─'*20}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*8}")
    for meth, loo, corr in [
        ("Teleport", result['teleport_loo'], result['teleport_corr']),
        ("Path", result['path_loo'], result['path_corr']),
        (f"Blend (α={BLEND_ALPHA:.3f})", result['blend_loo'], result['blend_corr']),
        ("Previous champion", ref['loo'], ref['corr']),
    ]:
        ratio = loo / result['sine_mae'] if result['sine_mae'] > 0 else 999
        delta = loo - ref['loo']
        marker = " ★" if loo < ref['loo'] and meth != "Previous champion" else ""
        print(f"  {meth:<20} │ {loo:>7.2f} │ {corr:>+6.3f} │ {ratio:>8.3f} │ {delta:>+8.2f}{marker}")

    print(f"  Sine baseline: {result['sine_mae']:.2f}  |  Runtime: {elapsed:.0f}s")

    # Per-cycle breakdown
    if name == "Solar (SSN)":
        print(f"\n  Solar per-cycle:")
        print(f"  {'C':>3} {'Year':>7} {'Act':>6} │ {'Path':>7} {'Telep':>7} {'Blend':>7} │ {'B err':>6}")
        for i in range(len(times)):
            cn = SOLAR_CYCLES[i][0]
            actual = peaks[i]
            p = result['path_preds'][i]
            t_p = result['teleport_preds'][i]
            b = result['blend_preds'][i]
            be = result['blend_errors'][i]
            flag = " ◀" if be > 60 else ""
            print(f"  C{cn:>2} {times[i]:>7.1f} {actual:>6.1f} │ {p:>7.1f} {t_p:>7.1f} {b:>7.1f} │ {be:>6.1f}{flag}")


# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════

print(f"\n{'=' * 78}")
print("  SUMMARY — 243BB Blended Pipeline")
print(f"{'=' * 78}")
print(f"\n  Blend ratio α = 1/φ² ≈ {BLEND_ALPHA:.4f}")
print(f"  Wave physics: mode coupling (1/φ⁹) + standing wave (sin(π·ARA/2))")
print()
print(f"  {'System':<17} │ {'Prev Champ':>10} │ {'Blend LOO':>9} │ {'Δ':>7} │ {'Corr':>6} │ {'LOO/Sine':>8}")
print(f"  {'─'*17}─┼─{'─'*10}─┼─{'─'*9}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*8}")

any_new_champ = False
for name in all_results:
    r = all_results[name]
    ref = ref_champ.get(name, {"loo": 999})
    delta = r['blend_loo'] - ref['loo']
    ratio = r['blend_loo'] / r['sine_mae'] if r['sine_mae'] > 0 else 999
    marker = " ★" if delta < 0 else ""
    if delta < 0: any_new_champ = True
    print(f"  {name:<17} │ {ref['loo']:>10.2f} │ {r['blend_loo']:>9.2f} │ {delta:>+7.2f} │ "
          f"{r['blend_corr']:>+6.3f} │ {ratio:>8.3f}{marker}")

if any_new_champ:
    print(f"\n  ★ NEW CHAMPION(S) FOUND!")

total_elapsed = clock_time.time() - t_start
print(f"\n  Total runtime: {total_elapsed:.0f}s")
