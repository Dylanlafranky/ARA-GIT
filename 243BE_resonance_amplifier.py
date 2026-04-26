#!/usr/bin/env python3
"""
Script 243BE — Resonance Amplifier (Dynamic Range Expansion)

DIAGNOSIS: The cascade compresses extremes toward the mean.
  - Product of (1 + small × cos) terms → geometric mean compresses toward 1.0
  - Multiplicative grief, standing wave, wall energy → further compression
  - Result: big cycles undershot, small cycles overshot

FIX: After the cascade product but BEFORE midline/amp_scale, apply a gentle
nonlinear stretch that amplifies deviations from 1.0:
  - Small deviations (normal cycles): pass through mostly unchanged
  - Large deviations (extreme cycles): get proportionally amplified
  - This is what real wave constructive/destructive interference does

Three approaches, all at φ-power strengths:
  1. Soft quadratic: dev → dev × (1 + strength × |dev|)
  2. Power-law: dev → sign(dev) × |dev|^(1 + strength)
  3. Standing-wave feedback: standing_delta scaled by |deviation|
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

# Insertion point: AFTER grief, BEFORE midline shift
# This is where deviation from 1.0 is maximal and clean
MIDLINE_MARKER = "        # ── FIX 4: Midline shift ──"
STANDING_MARKER = "shape *= (1.0 + standing_delta * INV_PHI_3)"


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
    grid_search = ns['grid_search']
    run_full_simulation = ns['run_full_simulation']
    SOLAR_CYCLES = ns['SOLAR_CYCLES']

    teleport = ns['run_formula_loo'](solar_t, solar_a, PHI**5, PHI, 5, "Solar")
    teleport_preds = np.array(teleport['preds'])

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
    path_preds = np.array(path_preds)

    blended = BLEND_ALPHA * path_preds + (1 - BLEND_ALPHA) * teleport_preds
    blend_errors = np.abs(blended - solar_a)
    blend_loo = np.mean(blend_errors)
    blend_corr = np.corrcoef(blended, solar_a)[0, 1] if np.std(blended) > 0 else 0
    return {
        'blend_loo': blend_loo, 'blend_corr': blend_corr,
        'blend_preds': blended, 'blend_errors': blend_errors,
        'solar_a': solar_a, 'solar_t': solar_t, 'cycles': SOLAR_CYCLES,
    }


print("=" * 78)
print("  Script 243BE — Resonance Amplifier (Dynamic Range Expansion)")
print("  Champion blend LOO: 38.73 | Teleport baseline: ~44.05")
print("=" * 78)

# ═══════════════════════════════════════════
# PHASE 0: Measure current compression
# ═══════════════════════════════════════════

print("\n  PHASE 0: Measuring cascade compression...")
base_result = run_teleport_only(base_code, "BASELINE")
if base_result is None:
    print("  FATAL: Baseline failed")
    sys.exit(1)

solar_a = base_result['solar_a']
preds = base_result['preds']
errors = preds - solar_a

# Compression metric: ratio of prediction range to actual range
pred_range = np.max(preds) - np.min(preds)
actual_range = np.max(solar_a) - np.min(solar_a)
compression = pred_range / actual_range
print(f"  Actual range: {np.min(solar_a):.0f} – {np.max(solar_a):.0f} = {actual_range:.0f}")
print(f"  Pred range:   {np.min(preds):.0f} – {np.max(preds):.0f} = {pred_range:.0f}")
print(f"  Compression ratio: {compression:.3f} (1.0 = perfect, <1 = compressed)")
print(f"  Pred σ / Actual σ: {np.std(preds)/np.std(solar_a):.3f}")

# ═══════════════════════════════════════════
# Build variants
# ═══════════════════════════════════════════

variants = []

# 1. Soft quadratic stretch at 1/φ⁴ — BEFORE midline/amp_scale
block1 = f"""
        # ── RESONANCE AMPLIFIER: soft quadratic stretch ──
        res_dev = shape - 1.0
        shape = 1.0 + res_dev * (1.0 + {INV_PHI_4} * abs(res_dev))
"""
code1 = base_code.replace(MIDLINE_MARKER, block1 + "\n" + MIDLINE_MARKER)
variants.append(("Quad-stretch 1/φ⁴", code1))

# 2. Power-law stretch at 1/φ⁵
block2 = f"""
        # ── RESONANCE AMPLIFIER: power-law stretch ──
        res_dev = shape - 1.0
        if res_dev != 0:
            res_sign = 1.0 if res_dev > 0 else -1.0
            shape = 1.0 + res_sign * abs(res_dev) ** (1.0 + {INV_PHI_5})
"""
code2 = base_code.replace(MIDLINE_MARKER, block2 + "\n" + MIDLINE_MARKER)
variants.append(("Power-law 1/φ⁵", code2))

# 3. Standing-wave feedback — standing wave amplified by current deviation
new_sw = f"""shape_dev_pre = abs(shape - 1.0)
        sw_strength = INV_PHI_3 * (1.0 + {INV_PHI_3} * shape_dev_pre)
        shape *= (1.0 + standing_delta * sw_strength)"""
code3 = base_code.replace(
    "shape *= (1.0 + standing_delta * INV_PHI_3)",
    new_sw
)
variants.append(("SW-feedback 1/φ³", code3))


# ═══════════════════════════════════════════
# PHASE 1: Teleport screening
# ═══════════════════════════════════════════

print(f"\n{'=' * 78}")
print(f"  PHASE 1: Teleport screening — {len(variants)} variants")
print(f"{'=' * 78}")

base_loo = base_result['loo']
print(f"\n  {'Variant':30s} │ {'LOO':>7} │ {'Corr':>6} │ {'LOO/Sine':>8} │ {'Δ base':>7} │ {'Range':>5}")
print(f"  {'─'*30}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*7}─┼─{'─'*5}")

# Print baseline first
ratio = base_result['loo'] / base_result['sine']
print(f"  {'BASELINE':30s} │ {base_loo:>7.2f} │ {base_result['corr']:>+6.3f} │ {ratio:>8.3f} │ {0:>+7.2f} │ {pred_range:>5.0f}")

screen_results = []

for vname, code in variants:
    t0 = clock_time.time()
    result = run_teleport_only(code, vname)
    elapsed = clock_time.time() - t0
    if result is None:
        continue
    delta = result['loo'] - base_loo
    ratio = result['loo'] / result['sine']
    v_range = np.max(result['preds']) - np.min(result['preds'])
    marker = " ★" if delta < -0.5 else ""
    screen_results.append((vname, result, code, delta))
    print(f"  {vname:30s} │ {result['loo']:>7.2f} │ {result['corr']:>+6.3f} │ {ratio:>8.3f} │ {delta:>+7.2f} │ {v_range:>5.0f}{marker}  ({elapsed:.0f}s)")

# ═══════════════════════════════════════════
# PHASE 2: Blend the winner
# ═══════════════════════════════════════════

winner = None
for x in sorted(screen_results, key=lambda x: x[1]['loo']):
    if x[3] < -0.3 and x[0] != "BASELINE":
        winner = x
        break

if winner:
    vname, screen, code, delta = winner
    print(f"\n{'=' * 78}")
    print(f"  PHASE 2: Blend pipeline — {vname}")
    print(f"{'=' * 78}")

    t0 = clock_time.time()
    print(f"\n  Blending {vname}...", end="", flush=True)
    blend_result = run_blend(code, vname)
    elapsed = clock_time.time() - t0
    bdelta = blend_result['blend_loo'] - 38.73
    marker = "★ NEW CHAMPION" if bdelta < 0 else ""
    print(f"\r  {vname:30s} │ Blend LOO={blend_result['blend_loo']:6.2f} │ "
          f"Corr={blend_result['blend_corr']:+.3f} │ Δ champ={bdelta:+6.2f} │ {marker}  ({elapsed:.0f}s)")

    if bdelta < 0:
        solar_a = blend_result['solar_a']
        solar_t = blend_result['solar_t']
        cycles = blend_result['cycles']

        # Compare against baseline blend (38.73)
        print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'New':>7} {'Err':>6}")
        for i in range(len(solar_t)):
            cn = cycles[i][0]
            b_err = blend_result['blend_errors'][i]
            flag = " ◀" if b_err > 60 else ""
            print(f"  C{cn:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
                  f"{blend_result['blend_preds'][i]:>7.1f} {b_err:>6.1f}{flag}")
else:
    # Even if no teleport winner, show per-cycle analysis for best variant
    if screen_results:
        best = sorted(screen_results, key=lambda x: x[1]['loo'])[0]
        vname, result, code, delta = best
        print(f"\n  No variant beat baseline by >0.3 in teleport.")
        print(f"  Best: {vname} (LOO={result['loo']:.2f}, Δ={delta:+.2f})")

        # Show signed error comparison
        new_errors = result['preds'] - solar_a
        print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Base err':>8} {'New err':>8} │ {'Δ|err|':>7}")
        for i in range(len(solar_a)):
            cn = base_result['cycles'][i][0]
            b_e = errors[i]
            n_e = new_errors[i]
            d = abs(n_e) - abs(b_e)
            flag = " ★" if d < -5 else (" ◀" if d > 5 else "")
            print(f"  C{cn:>2} {base_result['solar_t'][i]:>7.1f} {solar_a[i]:>6.1f} │ {b_e:>+8.1f} {n_e:>+8.1f} │ {d:>+7.1f}{flag}")
    else:
        print(f"\n  All variants failed.")

total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
