#!/usr/bin/env python3
"""
Script 243BJ — ARA-Circle Post-Blend Stretch

The cascade can't be modified (correlates errors, breaks blend).
The post-blend stretch works but is a constant (1/φ⁵).

Dylan's insight: the system's ARA circle defines the range of motion.
Apply this at the blend level — the circle determines how much the
blended prediction can deviate from the training mean.

This keeps both methods untouched (errors stay independent) while
using the framework geometry to set the expansion magnitude.

Also includes the midline upgrade (camshaft) for consumer systems.

Variants:
  A) ARA-linear: stretch = 1 + (ARA/φ) × 1/φ⁵
     The system's ARA position scales the stretch. Engines get more room.
  B) Midline-scaled: stretch = 1 + midline_offset × 1/φ³
     The midline IS the circle's displacement from neutral.
     midline_offset = |midline - 1| for the system.
  C) Deviation-adaptive: bigger deviations get more stretch.
     stretch = 1 + 1/φ⁵ + 1/φ⁴ × |dev|/train_mean
     The circle has more room at its extremes.
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


# ═══════════════════════════════════════════
# Midline upgrade (camshaft-E from 237k2)
# ═══════════════════════════════════════════

MIDLINE_FN_MARKER = """def ara_midline(ara):
    \"\"\"midline = 1 + acc_frac × (ARA - 1), where acc_frac = 1/(1+ARA).
    Solar (φ): 1.236. Consumer (1/φ): 0.764. Clock (1.0): 1.0.\"\"\"
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)"""

MIDLINE_FN_CAMSHAFT = """def _base_midline(a):
    a = max(0.01, a)
    return 1.0 + (1.0 / (1.0 + a)) * (a - 1.0)

def _midline_inverse_valve(ara):
    if ara >= 1.0:
        return _base_midline(ara)
    else:
        return _base_midline(1.0 / max(0.01, ara))

def _phi_dist(ara):
    a = max(0.01, ara)
    return abs(math.log(a)) / math.log(PHI)

def ara_midline(ara):
    \"\"\"Camshaft-E: palindrome + inverse valve.\"\"\"
    inv_offset = _midline_inverse_valve(ara) - 1.0
    pd = _phi_dist(ara)
    zone = 1.0 / PHI
    if pd <= zone:
        return 1.0
    if pd >= 1.0:
        return 1.0 + inv_offset
    ramp_width = 1.0 / (PHI * PHI)
    t = (pd - zone) / ramp_width
    return 1.0 + inv_offset * t * t"""


# Apply midline upgrade to base code
upgraded_code = base_code.replace(MIDLINE_FN_MARKER, MIDLINE_FN_CAMSHAFT)
assert MIDLINE_FN_CAMSHAFT.split('\n')[0] in upgraded_code, "Midline upgrade failed"


# ═══════════════════════════════════════════
# Execution helpers (no cascade changes)
# ═══════════════════════════════════════════

def run_teleport_only(code_str, variant_name):
    ns = {'__file__': combo_path, '__name__': '__exec__'}
    try:
        exec(code_str, ns)
    except Exception as e:
        print(f"  ⚠ {variant_name}: exec error: {e}")
        return None
    solar_t = ns['solar_t']
    solar_a = ns['solar_a']
    SOLAR_CYCLES = ns['SOLAR_CYCLES']
    result = ns['run_formula_loo'](solar_t, solar_a, PHI**5, PHI, 5, "Solar")
    return {
        'loo': result['loo_mae'], 'corr': result['corr'],
        'preds': np.array(result['preds']),
        'sine': result['sine_mae'],
        'solar_a': solar_a, 'solar_t': solar_t,
        'cycles': SOLAR_CYCLES,
    }


def get_path_teleport_preds(code_str, variant_name):
    """Run both path and teleport LOO, return raw predictions."""
    ns = {'__file__': combo_path, '__name__': '__exec__'}
    exec(code_str, ns)
    solar_t = ns['solar_t']
    solar_a = ns['solar_a']
    SOLAR_CYCLES = ns['SOLAR_CYCLES']
    grid_search = ns['grid_search']
    run_full_simulation = ns['run_full_simulation']

    teleport = ns['run_formula_loo'](solar_t, solar_a, PHI**5, PHI, 5, "Solar")
    teleport_preds = np.array(teleport['preds'])

    N = len(solar_t)
    path_preds = []
    path_train_means = []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        path_train_means.append(np.mean(solar_a[mask]))
        fit_tr, fit_ba, _ = grid_search(PHI**5, PHI, 5, solar_t[mask], solar_a[mask])
        snap_t, snap_a = run_full_simulation(
            solar_t[mask], solar_a[mask], PHI**5, PHI, 5, fit_tr, fit_ba)
        if len(snap_t) == 0:
            path_preds.append(np.mean(solar_a[mask]))
        else:
            idx = np.argmin(np.abs(snap_t - solar_t[i]))
            path_preds.append(snap_a[idx])
    path_preds = np.array(path_preds)
    path_train_means = np.array(path_train_means)

    return {
        'teleport': teleport_preds, 'path': path_preds,
        'train_means': path_train_means,
        'solar_a': solar_a, 'solar_t': solar_t,
        'cycles': SOLAR_CYCLES,
        'sine_loo': teleport['sine_mae'],
    }


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

print("=" * 78)
print("  Script 243BJ — ARA-Circle Post-Blend Stretch")
print("  Physics-motivated stretch: circle geometry sets the range")
print("  Champion: LOO 38.37 / LOO/Sine 0.787")
print("=" * 78)

# Quick teleport check (midline upgrade is no-op for Solar)
print("\n  Teleport sanity check (midline upgrade is no-op for Solar):")
base_result = run_teleport_only(base_code, "BASE")
up_result = run_teleport_only(upgraded_code, "UPGRADED")
print(f"  Base LOO:     {base_result['loo']:.2f}")
print(f"  Upgraded LOO: {up_result['loo']:.2f} (should be same)")
sine_loo = base_result['sine']

# ═══════════════════════════════════════════
# Get path + teleport predictions (one run, reuse for all stretches)
# ═══════════════════════════════════════════

print(f"\n  Running path + teleport LOO...", flush=True)
t0 = clock_time.time()
raw = get_path_teleport_preds(upgraded_code, "upgraded")
elapsed = clock_time.time() - t0
print(f"  Done in {elapsed:.0f}s")

solar_a = raw['solar_a']
solar_t = raw['solar_t']
N = len(solar_a)

# Base blend (no stretch)
blended = BLEND_ALPHA * raw['path'] + (1 - BLEND_ALPHA) * raw['teleport']
base_blend_loo = np.mean(np.abs(blended - solar_a))
base_blend_corr = np.corrcoef(blended, solar_a)[0, 1]
print(f"\n  Raw blend (no stretch): LOO={base_blend_loo:.2f}, corr={base_blend_corr:+.3f}, "
      f"LOO/Sine={base_blend_loo/sine_loo:.3f}")

# Solar ARA and midline for the stretch formulas
SOLAR_ARA = PHI
SOLAR_MIDLINE = 1.0 + (1.0 / (1.0 + PHI)) * (PHI - 1.0)  # = 1.236

print(f"\n  Solar ARA = {SOLAR_ARA:.4f}, midline = {SOLAR_MIDLINE:.4f}")
print(f"  Midline offset from 1.0 = {abs(SOLAR_MIDLINE - 1.0):.4f}")

# ═══════════════════════════════════════════
# Test stretch variants
# ═══════════════════════════════════════════

print(f"\n{'=' * 78}")
print(f"  STRETCH VARIANTS (all applied post-blend, methods untouched)")
print(f"{'=' * 78}")

print(f"\n  {'Variant':40s} │ {'Factor':>8} │ {'LOO':>7} │ {'Corr':>6} │ {'LOO/Sin':>7} │ {'% vs sin':>8} │ {'Δ champ':>7}")
print(f"  {'─'*40}─┼─{'─'*8}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*8}─┼─{'─'*7}")


def test_stretch(name, stretched):
    errors = np.abs(stretched - solar_a)
    loo = np.mean(errors)
    corr = np.corrcoef(stretched, solar_a)[0, 1] if np.std(stretched) > 0 else 0
    ls = loo / sine_loo
    pct = (1 - ls) * 100
    delta = loo - 38.37
    factor = np.std(stretched) / np.std(blended) if np.std(blended) > 0 else 0
    marker = " ★" if delta < -0.3 else (" ✓" if delta < 0 else "")
    print(f"  {name:40s} │ {factor:>8.3f} │ {loo:>7.2f} │ {corr:>+6.3f} │ {ls:>7.3f} │ {pct:>+7.1f}% │ {delta:>+7.2f}{marker}")
    return loo, corr, stretched, errors


results = {}

# 0) No stretch (reference)
s0 = blended.copy()
results['none'] = test_stretch("0) No stretch (raw blend)", s0)

# 1) Champion: constant 1/φ⁵
s1 = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    s1[i] = raw['train_means'][i] + dev * (1 + INV_PHI_5)
results['champion'] = test_stretch("1) Constant 1/φ⁵ (champion 243BF)", s1)

# ─── ARA-CIRCLE VARIANTS ───

# A) ARA-linear: bigger ARA = more room on circle
ara_factor_A = 1.0 + (SOLAR_ARA / PHI) * INV_PHI_5  # = 1 + 1×0.091 = 1.091
sA = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    sA[i] = raw['train_means'][i] + dev * ara_factor_A
results['A'] = test_stretch(f"A) ARA-linear: 1+(ARA/φ)×1/φ⁵ = {ara_factor_A:.3f}", sA)

# B) Midline-scaled: the midline offset IS the circle's displacement
midline_offset = abs(SOLAR_MIDLINE - 1.0)  # = 0.236
factor_B = 1.0 + midline_offset * INV_PHI_3  # = 1 + 0.236 × 0.236 = 1.056
sB = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    sB[i] = raw['train_means'][i] + dev * factor_B
results['B'] = test_stretch(f"B) Midline-scaled: 1+offset×1/φ³ = {factor_B:.3f}", sB)

# B2) Midline with stronger coupling
factor_B2 = 1.0 + midline_offset * INV_PHI_2  # = 1 + 0.236 × 0.382 = 1.090
sB2 = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    sB2[i] = raw['train_means'][i] + dev * factor_B2
results['B2'] = test_stretch(f"B2) Midline: 1+offset×1/φ² = {factor_B2:.3f}", sB2)

# B3) Midline squared (circle area)
factor_B3 = 1.0 + midline_offset ** 2 * PHI  # = 1 + 0.0557 × 1.618 = 1.090
sB3 = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    sB3[i] = raw['train_means'][i] + dev * factor_B3
results['B3'] = test_stretch(f"B3) Midline²×φ (circle area) = {factor_B3:.3f}", sB3)

# C) Deviation-adaptive: extremes get more stretch (circle has more room)
sC = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    norm_dev = abs(dev) / raw['train_means'][i]
    adaptive_factor = 1.0 + INV_PHI_5 + INV_PHI_4 * norm_dev
    sC[i] = raw['train_means'][i] + dev * adaptive_factor
results['C'] = test_stretch("C) Adaptive: 1/φ⁵ + 1/φ⁴×|dev|/mean", sC)

# C2) Stronger adaptive
sC2 = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    norm_dev = abs(dev) / raw['train_means'][i]
    adaptive_factor = 1.0 + INV_PHI_4 + INV_PHI_3 * norm_dev
    sC2[i] = raw['train_means'][i] + dev * adaptive_factor
results['C2'] = test_stretch("C2) Stronger: 1/φ⁴ + 1/φ³×|dev|/mean", sC2)

# D) ARA circle radius: stretch = 1 + sin(π×ARA/2)/φ³
# The standing wave at the system's ARA defines the circle radius
circle_radius = math.sin(math.pi * SOLAR_ARA / 2.0)  # ≈ 0.951
factor_D = 1.0 + circle_radius * INV_PHI_4
sD = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    sD[i] = raw['train_means'][i] + dev * factor_D
results['D'] = test_stretch(f"D) Standing wave radius×1/φ⁴ = {factor_D:.3f}", sD)

# E) Combined: midline offset + deviation-adaptive
sE = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    norm_dev = abs(dev) / raw['train_means'][i]
    combined = 1.0 + midline_offset * INV_PHI_2 + INV_PHI_5 * norm_dev
    sE[i] = raw['train_means'][i] + dev * combined
results['E'] = test_stretch(f"E) Midline 1/φ² + adaptive 1/φ⁵", sE)

# F) φ-distance stretch: how far from clock determines room
phi_dist = abs(math.log(SOLAR_ARA)) / math.log(PHI)  # = 1.0 for Solar
factor_F = 1.0 + phi_dist * INV_PHI_5
sF = np.zeros(N)
for i in range(N):
    dev = blended[i] - raw['train_means'][i]
    sF[i] = raw['train_means'][i] + dev * factor_F
results['F'] = test_stretch(f"F) φ-distance×1/φ⁵ = {factor_F:.3f}", sF)


# ═══════════════════════════════════════════
# Find the best and show per-cycle comparison
# ═══════════════════════════════════════════

best_key = min(results.keys(), key=lambda k: results[k][0])
best_loo, best_corr, best_preds, best_errors = results[best_key]
champ_loo, _, champ_preds, champ_errors = results['champion']

print(f"\n{'=' * 78}")
print(f"  BEST: {best_key} — LOO {best_loo:.2f}")
print(f"{'=' * 78}")

# Per-cycle comparison: best vs champion
print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Best':>7} {'err':>6} │ {'Champ':>7} {'err':>6} │ {'Δ':>6}")
total_improved = 0
for i in range(N):
    cn = raw['cycles'][i][0]
    be = best_errors[i]
    ce = champ_errors[i]
    delta = be - ce
    flag = " ◀" if delta < -3 else (" ▶" if delta > 3 else "")
    if delta < 0:
        total_improved += 1
    print(f"  C{cn:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ {best_preds[i]:>7.1f} {be:>6.1f} │ {champ_preds[i]:>7.1f} {ce:>6.1f} │ {delta:>+6.1f}{flag}")

print(f"\n  Cycles improved: {total_improved}/{N}")
print(f"  Best σ ratio: {np.std(best_preds)/np.std(solar_a):.3f}")
print(f"  Champ σ ratio: {np.std(champ_preds)/np.std(solar_a):.3f}")

total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
