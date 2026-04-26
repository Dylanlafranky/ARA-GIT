#!/usr/bin/env python3
"""
Script 243BE — Blend the power-law 1/φ⁵ resonance amplifier winner.
Teleport screening showed LOO 43.56 vs baseline 44.05 (Δ=-0.49).
Now test if this carries through to the blend (champion: 38.73).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import time as clock_time

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
INV_PHI_5 = INV_PHI ** 5
BLEND_ALPHA = INV_PHI_2

t_start = clock_time.time()

combo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "243AZ_wave_combo.py")
with open(combo_path, 'r') as f:
    combo_code = f.read()

lines = combo_code.split('\n')
cutoff = len(lines)
for i, line in enumerate(lines):
    if '# MAIN' in line and i > 400:
        cutoff = i
        break
base_code = '\n'.join(lines[:cutoff])

MIDLINE_MARKER = "        # ── FIX 4: Midline shift ──"

# Apply power-law stretch
block = f"""
        # ── RESONANCE AMPLIFIER: power-law stretch ──
        res_dev = shape - 1.0
        if res_dev != 0:
            res_sign = 1.0 if res_dev > 0 else -1.0
            shape = 1.0 + res_sign * abs(res_dev) ** (1.0 + {INV_PHI_5})
"""
modified_code = base_code.replace(MIDLINE_MARKER, block + "\n" + MIDLINE_MARKER)

ns = {'__file__': combo_path, '__name__': '__exec__'}
exec(modified_code, ns)

solar_t = ns['solar_t']
solar_a = ns['solar_a']
SOLAR_CYCLES = ns['SOLAR_CYCLES']
grid_search = ns['grid_search']
run_full_simulation = ns['run_full_simulation']

print("=" * 78)
print("  243BE — Power-law 1/φ⁵ Resonance Amplifier (Blend)")
print("=" * 78)

# Teleport LOO
teleport = ns['run_formula_loo'](solar_t, solar_a, PHI**5, PHI, 5, "Solar")
teleport_preds = np.array(teleport['preds'])
print(f"\n  Teleport LOO: {teleport['loo_mae']:.2f} (corr={teleport['corr']:+.3f})")

# Path LOO
N = len(solar_t)
path_preds = []
for i in range(N):
    mask = np.ones(N, dtype=bool)
    mask[i] = False
    fit_tr, fit_ba, _ = grid_search(PHI**5, PHI, 5, solar_t[mask], solar_a[mask])
    snap_t, snap_a = run_full_simulation(
        solar_t[mask], solar_a[mask], PHI**5, PHI, 5, fit_tr, fit_ba)
    if len(snap_t) == 0:
        path_preds.append(np.mean(solar_a[mask]))
    else:
        idx = np.argmin(np.abs(snap_t - solar_t[i]))
        path_preds.append(snap_a[idx])
    if (i + 1) % 5 == 0:
        print(f"    Path fold {i+1}/{N}...", flush=True)
path_preds = np.array(path_preds)
path_loo = np.mean(np.abs(path_preds - solar_a))
print(f"  Path LOO: {path_loo:.2f}")

# Blend
blended = BLEND_ALPHA * path_preds + (1 - BLEND_ALPHA) * teleport_preds
blend_errors = np.abs(blended - solar_a)
blend_loo = np.mean(blend_errors)
blend_corr = np.corrcoef(blended, solar_a)[0, 1] if np.std(blended) > 0 else 0
bdelta = blend_loo - 38.73
marker = "★ NEW CHAMPION" if bdelta < 0 else ""

print(f"\n  Blend LOO: {blend_loo:.2f} (corr={blend_corr:+.3f}) Δ champ={bdelta:+.2f} {marker}")

# Per-cycle
print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Blend':>7} {'Err':>6}")
for i in range(N):
    cn = SOLAR_CYCLES[i][0]
    flag = " ◀" if blend_errors[i] > 60 else ""
    print(f"  C{cn:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ {blended[i]:>7.1f} {blend_errors[i]:>6.1f}{flag}")

total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
