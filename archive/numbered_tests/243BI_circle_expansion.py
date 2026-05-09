#!/usr/bin/env python3
"""
Script 243BI — ARA Circle Expansion + Midline Upgrade

Two changes stacked:
  1. Midline upgrade: inverse valve + camshaft (from Phase 13-14)
     → Helps consumer/near-clock systems, no-op on Solar itself
  2. Dynamic range expansion: the system's ARA circle contributes
     additive energy that widens the oscillation range

Dylan's insight: "it probably has φ range of motion, but we need it
to have 1 or 0.5+φ range of motion. It's always got at least part
of its initial ARA domain/circle that adds to it."

The cascade product Π(1+ε·cos) compresses via geometric mean.
The system's own ARA circle should provide additional range:
  - When waves constructively interfere: circle amplifies the surge
  - When they cancel: circle still provides baseline contribution
  - Net effect: wider dynamic range, especially at extremes

Three expansion variants (all applied uniformly to both methods):
  A) ARA-circle additive: deviation *= (1 + ara/φ × 1/φ⁴)
     The system's position on its circle adds proportional energy.
     Higher ARA = bigger circle = more room.
  B) Constructive boost: when deviation is positive (constructive
     interference), boost by circle_energy × |dev|/midline.
     Asymmetric: peaks get amplified more than troughs get dampened.
  C) Scaled power: deviation *= (1 + 1/φ³ × |deviation|/midline)
     Nonlinear: bigger deviations get stretched more. The system's
     natural variance determines the expansion magnitude.
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
# MARKERS
# ═══════════════════════════════════════════

# Midline function replacement
MIDLINE_FN_MARKER = """def ara_midline(ara):
    \"\"\"midline = 1 + acc_frac × (ARA - 1), where acc_frac = 1/(1+ARA).
    Solar (φ): 1.236. Consumer (1/φ): 0.764. Clock (1.0): 1.0.\"\"\"
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)"""

# The deviation/amplitude section where we inject expansion
AMP_MARKER = """        # ── FIX 5: Amplitude scale — the other half ──
        deviation = shape - self.midline
        shape = self.midline + deviation * self.amp_scale"""


# ═══════════════════════════════════════════
# UPGRADED MIDLINE (camshaft-E, the 237k2 champion)
# ═══════════════════════════════════════════

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
    \"\"\"Camshaft-E: palindrome zone [0, 1/phi] phi-rungs from clock.
    Inside zone: midline = 1.0 (perfect energy transfer).
    Quadratic ramp from 1/phi to 1 full rung.
    Beyond 1 rung: full inverse valve.\"\"\"
    inv_offset = _midline_inverse_valve(ara) - 1.0
    pd = _phi_dist(ara)
    zone = 1.0 / PHI
    if pd <= zone:
        return 1.0
    if pd >= 1.0:
        return 1.0 + inv_offset
    ramp_width = 1.0 / (PHI * PHI)
    t = (pd - zone) / ramp_width
    factor = t * t
    return 1.0 + inv_offset * factor"""


# ═══════════════════════════════════════════
# EXPANSION VARIANTS
# ═══════════════════════════════════════════

# A) ARA-circle proportional: bigger ARA = bigger circle = more room
AMP_VARIANT_A = """        # ── FIX 5: Amplitude scale + ARA circle expansion ──
        deviation = shape - self.midline
        # ARA circle adds proportional energy: bigger ARA = wider swing
        circle_factor = 1.0 + (self.ara / PHI) * INV_PHI_4
        shape = self.midline + deviation * self.amp_scale * circle_factor"""

# B) Constructive boost: asymmetric — peaks amplified more than troughs
AMP_VARIANT_B = """        # ── FIX 5: Amplitude scale + constructive circle boost ──
        deviation = shape - self.midline
        # Circle energy amplifies constructive interference more
        if deviation > 0:
            circle_boost = 1.0 + (self.ara / PHI) * INV_PHI_3 * (deviation / self.midline)
        else:
            circle_boost = 1.0 + (self.ara / PHI) * INV_PHI_4 * abs(deviation / self.midline)
        shape = self.midline + deviation * self.amp_scale * circle_boost"""

# C) Nonlinear: bigger deviations get stretched more (soft quadratic)
AMP_VARIANT_C = """        # ── FIX 5: Amplitude scale + nonlinear circle expansion ──
        deviation = shape - self.midline
        # Bigger deviations get more room — the circle's full extent
        norm_dev = abs(deviation) / max(0.01, self.midline)
        circle_factor = 1.0 + INV_PHI_3 * norm_dev
        shape = self.midline + deviation * self.amp_scale * circle_factor"""


# ═══════════════════════════════════════════
# Execution helpers
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

    # Also test WITHOUT post-blend stretch (expansion might replace it)
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

    sine_loo = teleport['sine_mae']

    return {
        'blend_loo': blend_loo, 'blend_corr': blend_corr,
        'blend_preds': blended, 'blend_errors': blend_errors,
        'stretch_loo': stretch_loo, 'stretch_corr': stretch_corr,
        'stretch_preds': stretched, 'stretch_errors': stretch_errors,
        'solar_a': solar_a, 'solar_t': solar_t, 'cycles': SOLAR_CYCLES,
        'teleport_preds': teleport_preds, 'path_preds': path_preds,
        'path_train_means': path_train_means,
        'sine_loo': sine_loo,
    }


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════

print("=" * 78)
print("  Script 243BI — ARA Circle Expansion + Midline Upgrade")
print("  Expand dynamic range uniformly (both methods get it)")
print("  Champion: LOO 38.37 / LOO/Sine 0.787")
print("=" * 78)

assert MIDLINE_FN_MARKER in base_code, "Can't find MIDLINE_FN_MARKER"
assert AMP_MARKER in base_code, "Can't find AMP_MARKER"

# Build variants: midline upgrade + expansion
variants = []
for name, amp_code in [
    ("A: Circle proportional", AMP_VARIANT_A),
    ("B: Constructive boost", AMP_VARIANT_B),
    ("C: Nonlinear stretch", AMP_VARIANT_C),
]:
    code = base_code.replace(MIDLINE_FN_MARKER, MIDLINE_FN_CAMSHAFT)
    code = code.replace(AMP_MARKER, amp_code)
    variants.append((name, code))


# ═══════════════════════════════════════════
# PHASE 1: Teleport screening
# ═══════════════════════════════════════════

print(f"\n  PHASE 1: Teleport screening — {len(variants)} variants\n")

base_result = run_teleport_only(base_code, "BASELINE")
base_loo = base_result['loo']
base_preds = base_result['preds']
solar_a = base_result['solar_a']
sine_loo = base_result['sine']

pred_range = np.max(base_preds) - np.min(base_preds)
actual_range = np.max(solar_a) - np.min(solar_a)
print(f"  BASELINE: LOO={base_loo:.2f}, corr={base_result['corr']:+.3f}, "
      f"σ ratio={np.std(base_preds)/np.std(solar_a):.3f}, "
      f"range {pred_range:.0f}/{actual_range:.0f}, "
      f"LOO/Sine={base_loo/sine_loo:.3f}")

print(f"\n  {'Variant':26s} │ {'LOO':>7} │ {'Corr':>6} │ {'σ ratio':>7} │ {'Range':>9} │ {'LOO/Sin':>7} │ {'Δ base':>7}")
print(f"  {'─'*26}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*9}─┼─{'─'*7}─┼─{'─'*7}")

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
    print(f"  {vname:26s} │ {result['loo']:>7.2f} │ {result['corr']:>+6.3f} │ {sigma_ratio:>7.3f} │ {v_range:>5.0f}/{actual_range:.0f} │ {loo_sine:>7.3f} │ {delta:>+7.2f}{marker}  ({elapsed:.0f}s)")


# ═══════════════════════════════════════════
# PHASE 2: Blend the best
# ═══════════════════════════════════════════

winner = sorted(screen_results, key=lambda x: x[1]['loo'])[0]
vname, screen, code, delta = winner

print(f"\n{'=' * 78}")
print(f"  PHASE 2: Blend pipeline — {vname}")
print(f"{'=' * 78}")

print(f"\n  Blending {vname}...", flush=True)
t0 = clock_time.time()
blend_result = run_blend(code, vname)
elapsed = clock_time.time() - t0

sine_loo = blend_result['sine_loo']
loo_sine_raw = blend_result['blend_loo'] / sine_loo
loo_sine_stretch = blend_result['stretch_loo'] / sine_loo
pct_raw = (1 - loo_sine_raw) * 100
pct_stretch = (1 - loo_sine_stretch) * 100

print(f"\n  Results for {vname}:")
print(f"  Raw blend LOO:     {blend_result['blend_loo']:6.2f} (corr={blend_result['blend_corr']:+.3f}) "
      f"LOO/Sine={loo_sine_raw:.3f} ({pct_raw:+.1f}% vs sine)")
print(f"  + 1/φ⁵ stretch:   {blend_result['stretch_loo']:6.2f} (corr={blend_result['stretch_corr']:+.3f}) "
      f"LOO/Sine={loo_sine_stretch:.3f} ({pct_stretch:+.1f}% vs sine)")
print(f"  ──────────────────────────────────────")
print(f"  CHAMPION (243BF):  raw=38.73 stretch=38.37 LOO/Sine=0.787 (−21.3%)")
print(f"  Δ champion raw:    {blend_result['blend_loo'] - 38.73:+.2f}")
print(f"  Δ champion stretch:{blend_result['stretch_loo'] - 38.37:+.2f}")
print(f"  Time: {elapsed:.0f}s")

# Per-cycle
print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Blend':>7} {'B err':>6} │ {'Stretch':>7} {'S err':>6}")
for i in range(len(blend_result['solar_t'])):
    cn = blend_result['cycles'][i][0]
    b_err = blend_result['blend_errors'][i]
    s_err = blend_result['stretch_errors'][i]
    flag = " ◀" if s_err > 60 else ""
    print(f"  C{cn:>2} {blend_result['solar_t'][i]:>7.1f} {blend_result['solar_a'][i]:>6.1f} │ "
          f"{blend_result['blend_preds'][i]:>7.1f} {b_err:>6.1f} │ "
          f"{blend_result['stretch_preds'][i]:>7.1f} {s_err:>6.1f}{flag}")

# Sigma comparison
b_sigma = np.std(blend_result['blend_preds']) / np.std(blend_result['solar_a'])
s_sigma = np.std(blend_result['stretch_preds']) / np.std(blend_result['solar_a'])
print(f"\n  Blend pred σ/actual σ = {b_sigma:.3f}")
print(f"  Stretch pred σ/actual σ = {s_sigma:.3f}")
print(f"  (Previous baseline: 0.793)")

# Error independence check
tp = blend_result['teleport_preds']
pp = blend_result['path_preds']
tp_err = tp - blend_result['solar_a']
pp_err = pp - blend_result['solar_a']
err_corr = np.corrcoef(tp_err, pp_err)[0, 1]
print(f"\n  Path-teleport error correlation: {err_corr:+.3f}")
print(f"  (Baseline was ~0.0 — lower = more independent = better blend)")


total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
