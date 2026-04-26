#!/usr/bin/env python3
"""
Script 243BF — Post-Blend Stretch (Dynamic Range Expansion)

INSIGHT: Modifying the cascade helps teleport but hurts path (and vice versa).
The blend's power comes from their INDEPENDENT errors canceling.

So: don't touch the cascade. Instead, stretch the BLENDED output away from
the training mean. This expands dynamic range AFTER both methods have
contributed, without interfering with either.

blended = α × path + (1-α) × teleport
stretched = train_mean + (blended - train_mean) × stretch

Test stretch factors at φ-powers above 1.0:
  1 + 1/φ⁵ ≈ 1.09  (gentle)
  1 + 1/φ⁴ ≈ 1.15  (moderate)
  1 + 1/φ³ ≈ 1.24  (strong)
  1 + 1/φ² ≈ 1.38  (aggressive)

Also test: agreement-weighted stretch — stretch MORE when path and teleport
agree on the direction from mean (both see the same extreme).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import time as clock_time

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4
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

ns = {'__file__': combo_path, '__name__': '__exec__'}
exec(base_code, ns)

solar_t = ns['solar_t']
solar_a = ns['solar_a']
SOLAR_CYCLES = ns['SOLAR_CYCLES']
grid_search = ns['grid_search']
run_full_simulation = ns['run_full_simulation']
run_formula_loo = ns['run_formula_loo']

N = len(solar_t)

print("=" * 78)
print("  Script 243BF — Post-Blend Stretch (Dynamic Range Expansion)")
print("  Champion blend LOO: 38.73 | Testing stretch factors")
print("=" * 78)

# ═══════════════════════════════════════════
# Get teleport + path predictions (one run, reuse for all stretches)
# ═══════════════════════════════════════════

print("\n  Computing teleport LOO...", flush=True)
t0 = clock_time.time()
teleport = run_formula_loo(solar_t, solar_a, PHI**5, PHI, 5, "Solar")
teleport_preds = np.array(teleport['preds'])
print(f"  Teleport LOO: {teleport['loo_mae']:.2f} ({clock_time.time()-t0:.0f}s)")

print("  Computing path LOO...", flush=True)
t0 = clock_time.time()
path_preds = []
path_train_means = []  # per-fold training mean
for i in range(N):
    mask = np.ones(N, dtype=bool)
    mask[i] = False
    train_mean = np.mean(solar_a[mask])
    path_train_means.append(train_mean)
    fit_tr, fit_ba, _ = grid_search(PHI**5, PHI, 5, solar_t[mask], solar_a[mask])
    snap_t, snap_a = run_full_simulation(
        solar_t[mask], solar_a[mask], PHI**5, PHI, 5, fit_tr, fit_ba)
    if len(snap_t) == 0:
        path_preds.append(train_mean)
    else:
        idx = np.argmin(np.abs(snap_t - solar_t[i]))
        path_preds.append(snap_a[idx])
    if (i + 1) % 5 == 0:
        print(f"    Path fold {i+1}/{N}...", flush=True)
path_preds = np.array(path_preds)
path_train_means = np.array(path_train_means)
print(f"  Path LOO: {np.mean(np.abs(path_preds - solar_a)):.2f} ({clock_time.time()-t0:.0f}s)")

# Base blend (no stretch)
blended_base = BLEND_ALPHA * path_preds + (1 - BLEND_ALPHA) * teleport_preds
base_blend_loo = np.mean(np.abs(blended_base - solar_a))
base_blend_corr = np.corrcoef(blended_base, solar_a)[0, 1]
print(f"  Base blend LOO: {base_blend_loo:.2f} (corr={base_blend_corr:+.3f})")

# ═══════════════════════════════════════════
# Test stretch factors
# ═══════════════════════════════════════════

print(f"\n{'=' * 78}")
print(f"  Stretch factor scan")
print(f"{'=' * 78}")
print(f"\n  {'Stretch':30s} │ {'LOO':>7} │ {'Corr':>6} │ {'Δ champ':>8} │ {'Δ base':>7}")
print(f"  {'─'*30}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*7}")

# Print base blend
print(f"  {'Base blend (no stretch)':30s} │ {base_blend_loo:>7.2f} │ {base_blend_corr:>+6.3f} │ {base_blend_loo-38.73:>+8.2f} │ {0:>+7.2f}")

best_loo = base_blend_loo
best_name = "Base"
best_preds = blended_base

stretches = [
    ("Stretch 1+1/φ⁵ (1.091)", 1.0 + INV_PHI_5),
    ("Stretch 1+1/φ⁴ (1.146)", 1.0 + INV_PHI_4),
    ("Stretch 1+1/φ³ (1.236)", 1.0 + INV_PHI_3),
    ("Stretch 1+1/φ² (1.382)", 1.0 + INV_PHI_2),
    ("Stretch φ (1.618)",       PHI),
]

for name, factor in stretches:
    # Per-fold stretch using that fold's training mean
    stretched = np.zeros(N)
    for i in range(N):
        deviation = blended_base[i] - path_train_means[i]
        stretched[i] = path_train_means[i] + deviation * factor

    s_errors = np.abs(stretched - solar_a)
    s_loo = np.mean(s_errors)
    s_corr = np.corrcoef(stretched, solar_a)[0, 1] if np.std(stretched) > 0 else 0
    delta_champ = s_loo - 38.73
    delta_base = s_loo - base_blend_loo
    marker = " ★" if s_loo < best_loo else ""

    if s_loo < best_loo:
        best_loo = s_loo
        best_name = name
        best_preds = stretched

    print(f"  {name:30s} │ {s_loo:>7.2f} │ {s_corr:>+6.3f} │ {delta_champ:>+8.2f} │ {delta_base:>+7.2f}{marker}")

# Agreement-weighted: stretch more when path & teleport agree on direction
print(f"\n  Agreement-weighted variants:")
for name, base_factor in [
    ("Agree-stretch 1+1/φ⁴", 1.0 + INV_PHI_4),
    ("Agree-stretch 1+1/φ³", 1.0 + INV_PHI_3),
]:
    stretched = np.zeros(N)
    for i in range(N):
        p_dev = path_preds[i] - path_train_means[i]
        t_dev = teleport_preds[i] - path_train_means[i]
        b_dev = blended_base[i] - path_train_means[i]

        # Agreement: 1.0 when same sign, 0.0 when opposite
        if p_dev * t_dev > 0:
            agreement = 1.0
        else:
            agreement = 0.0

        # Stretch factor = 1 + (factor-1) * agreement
        eff_factor = 1.0 + (base_factor - 1.0) * agreement
        stretched[i] = path_train_means[i] + b_dev * eff_factor

    s_errors = np.abs(stretched - solar_a)
    s_loo = np.mean(s_errors)
    s_corr = np.corrcoef(stretched, solar_a)[0, 1] if np.std(stretched) > 0 else 0
    delta_champ = s_loo - 38.73
    delta_base = s_loo - base_blend_loo
    marker = " ★" if s_loo < best_loo else ""

    if s_loo < best_loo:
        best_loo = s_loo
        best_name = name
        best_preds = stretched

    print(f"  {name:30s} │ {s_loo:>7.2f} │ {s_corr:>+6.3f} │ {delta_champ:>+8.2f} │ {delta_base:>+7.2f}{marker}")

# ═══════════════════════════════════════════
# Per-cycle breakdown of best
# ═══════════════════════════════════════════

print(f"\n{'=' * 78}")
print(f"  Best: {best_name} (LOO={best_loo:.2f})")
print(f"{'=' * 78}")

best_errors = np.abs(best_preds - solar_a)
base_errors = np.abs(blended_base - solar_a)

print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Base':>7} {'B err':>6} │ {'Best':>7} {'N err':>6} │ {'Δ':>6}")
for i in range(N):
    cn = SOLAR_CYCLES[i][0]
    d = best_errors[i] - base_errors[i]
    flag = " ★" if d < -5 else (" ◀" if d > 5 else "")
    print(f"  C{cn:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ {blended_base[i]:>7.1f} {base_errors[i]:>6.1f} │ "
          f"{best_preds[i]:>7.1f} {best_errors[i]:>6.1f} │ {d:>+6.1f}{flag}")

total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
