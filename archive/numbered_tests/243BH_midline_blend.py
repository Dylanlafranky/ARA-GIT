#!/usr/bin/env python3
"""
Script 243BH — Midline + Blend (Combining Two Breakthroughs)

Peer review v15 identified that the two biggest wins address different problems:
  - Phase 13 midline (237k2): WHERE the wave oscillates (vertical pipe geometry)
  - Phase 17 blend (243BB/BF): HOW two perspectives average (Space × Time)

The 243 architecture has only the basic midline. This script upgrades it to
the full Phase 13-14 architecture:
  1. Inverse valve: consumers (ARA < 1) use _base_midline(1/ARA)
  2. Camshaft palindrome zone: near-clock systems (within 1/φ rungs) get
     no midline shift; quadratic ramp from 1/φ to 1 full rung
  3. amp_scale uses the camshaft midline

Then runs the full blend pipeline: teleport LOO + path LOO + 1/φ² blend
+ 1/φ⁵ post-blend stretch.

Variants:
  A) Inverse valve only (no palindrome zone)
  B) Camshaft-E (quadratic ramp palindrome zone)  ← the 237k2 champion
  C) Camshaft-F (linear ramp palindrome zone)
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
# Markers for string replacement
# ══════��════════════════════════════════════

# The basic midline function we're replacing
MIDLINE_FN_MARKER = """def ara_midline(ara):
    \"\"\"midline = 1 + acc_frac × (ARA - 1), where acc_frac = 1/(1+ARA).
    Solar (φ): 1.236. Consumer (1/φ): 0.764. Clock (1.0): 1.0.\"\"\"
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)"""

# Where midline and amp_scale are set in __init__
MIDLINE_INIT_MARKER = """        # FIX 4: Midline
        self.midline = ara_midline(ara)

        # FIX 5: Amplitude scale — the "other half" of accumulate/snap
        # Use midline itself as the scale: Solar 1.236, Consumer 0.764, Clock 1.0
        self.amp_scale = self.midline"""


# ═══════════════════════════════════════════
# Replacement code for each variant
# ═════════════════���═════════════════════════

# --- Variant A: Inverse valve only ---
MIDLINE_FN_INVERSE = """def _base_midline(a):
    a = max(0.01, a)
    return 1.0 + (1.0 / (1.0 + a)) * (a - 1.0)

def ara_midline(ara):
    \"\"\"Inverse valve: engines use ARA, consumers use 1/ARA.
    This makes the midline symmetric: Solar (φ) and Earthquake (1/φ) get
    the same magnitude offset, just in opposite directions.\"\"\"
    if ara >= 1.0:
        return _base_midline(ara)
    else:
        return _base_midline(1.0 / max(0.01, ara))"""

# --- Variant B: Camshaft-E (quadratic ramp) ---
MIDLINE_FN_CAMSHAFT_E = """def _base_midline(a):
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
    \"\"\"Camshaft-E: palindrome zone [0, 1/φ] φ-rungs from clock.
    Inside zone: midline = 1.0 (perfect φ energy transfer).
    Quadratic ramp from 1/φ to 1 full rung.
    Beyond 1 rung: full inverse valve.\"\"\"
    inv_offset = _midline_inverse_valve(ara) - 1.0
    pd = _phi_dist(ara)
    zone = 1.0 / PHI  # palindrome boundary
    if pd <= zone:
        return 1.0
    if pd >= 1.0:
        return 1.0 + inv_offset
    # Ramp zone: quadratic
    ramp_width = 1.0 / (PHI * PHI)
    t = (pd - zone) / ramp_width
    factor = t * t
    return 1.0 + inv_offset * factor"""

# --- Variant C: Camshaft-F (linear ramp) ---
MIDLINE_FN_CAMSHAFT_F = """def _base_midline(a):
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
    \"\"\"Camshaft-F: same palindrome zone but linear ramp (not quadratic).\"\"\"
    inv_offset = _midline_inverse_valve(ara) - 1.0
    pd = _phi_dist(ara)
    zone = 1.0 / PHI
    if pd <= zone:
        return 1.0
    if pd >= 1.0:
        return 1.0 + inv_offset
    ramp_width = 1.0 / (PHI * PHI)
    t = (pd - zone) / ramp_width
    return 1.0 + inv_offset * t"""


# ═════��══════════════════���══════════════════
# Execution helpers
# ═════���══════════════���══════════════════════

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


def run_blend(code_str, variant_name):
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

    blended = BLEND_ALPHA * path_preds + (1 - BLEND_ALPHA) * teleport_preds

    # Post-blend stretch at 1/φ⁵
    stretch = 1.0 + INV_PHI_5
    stretched = np.zeros(N)
    for i in range(N):
        dev = blended[i] - path_train_means[i]
        stretched[i] = path_train_means[i] + dev * stretch

    blend_errors = np.abs(blended - solar_a)
    blend_loo = np.mean(blend_errors)
    blend_corr = np.corrcoef(blended, solar_a)[0, 1] if np.std(blended) > 0 else 0

    stretch_errors = np.abs(stretched - solar_a)
    stretch_loo = np.mean(stretch_errors)
    stretch_corr = np.corrcoef(stretched, solar_a)[0, 1] if np.std(stretched) > 0 else 0

    return {
        'blend_loo': blend_loo, 'blend_corr': blend_corr,
        'blend_preds': blended, 'blend_errors': blend_errors,
        'stretch_loo': stretch_loo, 'stretch_corr': stretch_corr,
        'stretch_preds': stretched, 'stretch_errors': stretch_errors,
        'solar_a': solar_a, 'solar_t': solar_t, 'cycles': SOLAR_CYCLES,
        'teleport_preds': teleport_preds, 'path_preds': path_preds,
        'path_train_means': path_train_means,
        'sine_loo': teleport['sine_mae'],
    }


# ═══════════════════════════════════════════
# MAIN
# ════════════════════════���══════════════════

print("=" * 78)
print("  Script 243BH — Midline + Blend (Combining Two Breakthroughs)")
print("  Phase 13 midline (inverse valve + camshaft) × Phase 17 blend")
print("  Champion: LOO 38.37 (stretch) / 38.73 (raw blend) / Sine 48.78")
print("=" * 78)

# Verify markers exist
assert MIDLINE_FN_MARKER in base_code, f"Can't find MIDLINE_FN_MARKER"
assert MIDLINE_INIT_MARKER in base_code, f"Can't find MIDLINE_INIT_MARKER"

# ═══════════════════════════════════════════
# Build variants
# ═══���═══════════���═══════════════════════════

variants = []
for name, midline_fn_code in [
    ("A: Inverse valve", MIDLINE_FN_INVERSE),
    ("B: Camshaft-E (quad)", MIDLINE_FN_CAMSHAFT_E),
    ("C: Camshaft-F (lin)", MIDLINE_FN_CAMSHAFT_F),
]:
    code = base_code.replace(MIDLINE_FN_MARKER, midline_fn_code)
    variants.append((name, code))


# ═���═══════════════════��═════════════════════
# PHASE 1: Teleport screening
# ══��════════════════���═══════════════════════

print(f"\n  PHASE 1: Teleport screening — {len(variants)} variants\n")

# Baseline first
base_result = run_teleport_only(base_code, "BASELINE")
base_loo = base_result['loo']
base_preds = base_result['preds']
solar_a = base_result['solar_a']
sine_loo = base_result['sine']

pred_range = np.max(base_preds) - np.min(base_preds)
actual_range = np.max(solar_a) - np.min(solar_a)
print(f"  BASELINE: LOO={base_loo:.2f}, corr={base_result['corr']:+.3f}, "
      f"pred σ/act σ = {np.std(base_preds)/np.std(solar_a):.3f}, "
      f"range {pred_range:.0f}/{actual_range:.0f}, "
      f"LOO/Sine={base_loo/sine_loo:.3f}")

print(f"\n  {'Variant':28s} │ {'LOO':>7} │ {'Corr':>6} │ {'σ ratio':>7} │ {'LOO/Sin':>7} │ {'Δ base':>7}")
print(f"  {'─'*28}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}")

screen_results = []

for vname, code in variants:
    t0 = clock_time.time()
    result = run_teleport_only(code, vname)
    elapsed = clock_time.time() - t0
    if result is None:
        continue
    delta = result['loo'] - base_loo
    v_range = np.max(result['preds']) - np.min(result['preds'])
    sigma_ratio = np.std(result['preds']) / np.std(solar_a)
    loo_sine = result['loo'] / sine_loo
    marker = " ★" if delta < -0.5 else ""
    screen_results.append((vname, result, code, delta))
    print(f"  {vname:28s} │ {result['loo']:>7.2f} │ {result['corr']:>+6.3f} │ {sigma_ratio:>7.3f} │ {loo_sine:>7.3f} │ {delta:>+7.2f}{marker}  ({elapsed:.0f}s)")


# ════════════════════��══════════════════════
# PHASE 2: Blend the best variant(s)
# ═══════════════════════════════════════════

# Blend ALL variants that improved teleport, plus the best even if it didn't
candidates = sorted(screen_results, key=lambda x: x[1]['loo'])

# Always blend the best
blend_list = [candidates[0]]

# Also blend any that beat baseline
for c in candidates[1:]:
    if c[3] < 0:  # negative delta = improvement
        blend_list.append(c)

print(f"\n{'=' * 78}")
print(f"  PHASE 2: Blend pipeline ��� {len(blend_list)} variant(s)")
print(f"{'=' * 78}")

# Also run baseline blend for comparison
print(f"\n  Blending BASELINE...", flush=True)
t0 = clock_time.time()
base_blend = run_blend(base_code, "BASELINE")
elapsed = clock_time.time() - t0
print(f"  BASELINE blend:  raw={base_blend['blend_loo']:.2f} (corr={base_blend['blend_corr']:+.3f}), "
      f"stretch={base_blend['stretch_loo']:.2f} (corr={base_blend['stretch_corr']:+.3f}), "
      f"LOO/Sine raw={base_blend['blend_loo']/sine_loo:.3f}, "
      f"LOO/Sine stretch={base_blend['stretch_loo']/sine_loo:.3f}  ({elapsed:.0f}s)")

for vname, screen, code, delta in blend_list:
    print(f"\n  Blending {vname}...", flush=True)
    t0 = clock_time.time()
    blend_result = run_blend(code, vname)
    elapsed = clock_time.time() - t0

    bdelta_raw = blend_result['blend_loo'] - base_blend['blend_loo']
    bdelta_stretch = blend_result['stretch_loo'] - base_blend['stretch_loo']

    loo_sine_raw = blend_result['blend_loo'] / sine_loo
    loo_sine_stretch = blend_result['stretch_loo'] / sine_loo
    pct_better_raw = (1 - loo_sine_raw) * 100
    pct_better_stretch = (1 - loo_sine_stretch) * 100

    print(f"\n  Results for {vname}:")
    print(f"  Raw blend LOO:     {blend_result['blend_loo']:6.2f} (corr={blend_result['blend_corr']:+.3f}) "
          f"Δ baseline blend={bdelta_raw:+.2f} {'★' if bdelta_raw < -0.3 else ''}")
    print(f"  + 1/φ⁵ stretch:   {blend_result['stretch_loo']:6.2f} (corr={blend_result['stretch_corr']:+.3f}) "
          f"Δ baseline stretch={bdelta_stretch:+.2f} {'★' if bdelta_stretch < -0.3 else ''}")
    print(f"  LOO/Sine raw:      {loo_sine_raw:.3f} ({pct_better_raw:+.1f}% vs sine)")
    print(f"  LOO/Sine stretch:  {loo_sine_stretch:.3f} ({pct_better_stretch:+.1f}% vs sine)")
    print(f"  Prev champ (243BF): LOO/Sine = 0.787 (−21.3% vs sine)")
    print(f"  Time: {elapsed:.0f}s")

    # Per-cycle
    print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Blend':>7} {'B err':>6} │ {'Stretch':>7} {'S err':>6} │ {'Base B':>7} {'Base S':>7}")
    for i in range(len(blend_result['solar_t'])):
        cn = blend_result['cycles'][i][0]
        b_err = blend_result['blend_errors'][i]
        s_err = blend_result['stretch_errors'][i]
        bb = base_blend['blend_errors'][i]
        bs = base_blend['stretch_errors'][i]
        improved = " ◀" if s_err < bs - 3 else (" ▶" if s_err > bs + 10 else "")
        print(f"  C{cn:>2} {blend_result['solar_t'][i]:>7.1f} {blend_result['solar_a'][i]:>6.1f} │ "
              f"{blend_result['blend_preds'][i]:>7.1f} {b_err:>6.1f} │ "
              f"{blend_result['stretch_preds'][i]:>7.1f} {s_err:>6.1f} │ "
              f"{base_blend['blend_preds'][i]:>7.1f} {base_blend['stretch_preds'][i]:>7.1f}{improved}")

    # Sigma comparison
    b_sigma = np.std(blend_result['blend_preds']) / np.std(blend_result['solar_a'])
    s_sigma = np.std(blend_result['stretch_preds']) / np.std(blend_result['solar_a'])
    base_b_sigma = np.std(base_blend['blend_preds']) / np.std(base_blend['solar_a'])
    base_s_sigma = np.std(base_blend['stretch_preds']) / np.std(base_blend['solar_a'])
    print(f"\n  Blend σ ratio:   {b_sigma:.3f} (baseline: {base_b_sigma:.3f})")
    print(f"  Stretch σ ratio: {s_sigma:.3f} (baseline: {base_s_sigma:.3f})")


total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
