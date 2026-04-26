#!/usr/bin/env python3
"""
Script 243BG — Gate Inertia (The φ-Delay)

Insight from Google's Gemini: the gate updates instantly, but real systems
have inertia. The Rationality cog is HEAVY — it can't spin up instantly.

When energy spikes faster than the gate can open:
  - Tension builds inside the cascade (energy backs up)
  - When the gate finally catches up, it's dealing with a backlog
  - Result: naturally overshoots → extreme peaks

When energy drops faster than the gate can close:
  - The gate is still wide open from the previous spike
  - Energy bleeds out too fast → deeper minimums
  - Result: naturally undershoots → extreme valleys

This should naturally expand dynamic range WITHOUT the post-blend stretch.

Implementation: track a "gate_ara" that chases inst_ara with maximum rate
of change per cycle:
  gate_ara += clamp(inst_ara - gate_ara, -max_delta, +max_delta)
  acc = 1 / (1 + gate_ara)

Test max_delta at φ-powers: 1/φ⁴, 1/φ³, 1/φ²
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

# The gate is computed at line: acc = 1.0 / (1.0 + max(0.01, inst_ara))
# We need to:
# 1. Add gate_ara state to __init__
# 2. Replace acc computation with lagged version

INIT_MARKER = "        # Asymmetric breathing state\n        self.tilt_momentum = 0.0"
ACC_MARKER = "        acc = 1.0 / (1.0 + max(0.01, inst_ara))"


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

    # Also compute with 1/φ⁵ stretch for comparison
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
    }


print("=" * 78)
print("  Script 243BG — Gate Inertia (The φ-Delay)")
print("  Gate can only shift by max_delta per cycle")
print("  Champion: 38.37 (with stretch) / 38.73 (without)")
print("=" * 78)

# Verify markers exist
assert ACC_MARKER in base_code, f"Can't find ACC_MARKER"
assert INIT_MARKER in base_code, f"Can't find INIT_MARKER:\n{INIT_MARKER!r}"

# ═══════════════════════════════════════════
# Build variants
# ═══════════════════════════════════════════

variants = []

for name, max_delta in [
    ("Inertia 1/φ⁴ (0.146)", INV_PHI_4),
    ("Inertia 1/φ³ (0.236)", INV_PHI_3),
    ("Inertia 1/φ² (0.382)", INV_PHI_2),
]:
    # Add gate_ara state to __init__
    init_add = "        # Asymmetric breathing state\n        self.tilt_momentum = 0.0\n        self.gate_ara = None  # lagged gate ARA"
    code = base_code.replace(INIT_MARKER, init_add)

    # Replace instant acc with lagged version
    lagged_acc = f"""        # ── GATE INERTIA: Rationality cog has mass ──
        if self.gate_ara is None:
            self.gate_ara = inst_ara
        else:
            gate_delta = inst_ara - self.gate_ara
            gate_delta = max(-{max_delta}, min({max_delta}, gate_delta))
            self.gate_ara += gate_delta
        acc = 1.0 / (1.0 + max(0.01, self.gate_ara))"""
    code = code.replace(ACC_MARKER, lagged_acc)
    variants.append((name, code))


# ═══════════════════════════════════════════
# PHASE 1: Teleport screening
# ═══════════════════════════════════════════

print(f"\n  PHASE 1: Teleport screening — {len(variants)} variants\n")

# Baseline first
base_result = run_teleport_only(base_code, "BASELINE")
base_loo = base_result['loo']
base_preds = base_result['preds']
solar_a = base_result['solar_a']

pred_range = np.max(base_preds) - np.min(base_preds)
actual_range = np.max(solar_a) - np.min(solar_a)
print(f"  BASELINE: LOO={base_loo:.2f}, corr={base_result['corr']:+.3f}, "
      f"pred σ/act σ = {np.std(base_preds)/np.std(solar_a):.3f}, "
      f"range {pred_range:.0f}/{actual_range:.0f}")

print(f"\n  {'Variant':30s} │ {'LOO':>7} │ {'Corr':>6} │ {'σ ratio':>7} │ {'Range':>5} │ {'Δ base':>7}")
print(f"  {'─'*30}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*5}─┼─{'─'*7}")

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
    marker = " ★" if delta < -0.5 else ""
    screen_results.append((vname, result, code, delta))
    print(f"  {vname:30s} │ {result['loo']:>7.2f} │ {result['corr']:>+6.3f} │ {sigma_ratio:>7.3f} │ {v_range:>5.0f} │ {delta:>+7.2f}{marker}  ({elapsed:.0f}s)")

# ═══════════════════════════════════════════
# PHASE 2: Blend the best
# ═══════════════════════════════════════════

winner = None
for x in sorted(screen_results, key=lambda x: x[1]['loo']):
    if x[0] != "BASELINE":
        winner = x
        break

if winner:
    vname, screen, code, delta = winner
    print(f"\n{'=' * 78}")
    print(f"  PHASE 2: Blend pipeline — {vname}")
    print(f"{'=' * 78}")

    t0 = clock_time.time()
    print(f"\n  Blending {vname}...", flush=True)
    blend_result = run_blend(code, vname)
    elapsed = clock_time.time() - t0

    bdelta_raw = blend_result['blend_loo'] - 38.73  # vs raw blend champion
    bdelta_stretch = blend_result['stretch_loo'] - 38.37  # vs stretch champion

    print(f"\n  Results:")
    print(f"  Raw blend LOO:     {blend_result['blend_loo']:6.2f} (corr={blend_result['blend_corr']:+.3f}) "
          f"Δ raw champ={bdelta_raw:+.2f} {'★' if bdelta_raw < 0 else ''}")
    print(f"  + 1/φ⁵ stretch:   {blend_result['stretch_loo']:6.2f} (corr={blend_result['stretch_corr']:+.3f}) "
          f"Δ stretch champ={bdelta_stretch:+.2f} {'★' if bdelta_stretch < 0 else ''}")
    print(f"  Time: {elapsed:.0f}s")

    # Per-cycle
    print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Blend':>7} {'B err':>6} │ {'Stretch':>7} {'S err':>6}")
    for i in range(len(blend_result['solar_t'])):
        cn = blend_result['cycles'][i][0]
        b_err = blend_result['blend_errors'][i]
        s_err = blend_result['stretch_errors'][i]
        flag = " ◀" if b_err > 60 else ""
        print(f"  C{cn:>2} {blend_result['solar_t'][i]:>7.1f} {blend_result['solar_a'][i]:>6.1f} │ "
              f"{blend_result['blend_preds'][i]:>7.1f} {b_err:>6.1f} │ "
              f"{blend_result['stretch_preds'][i]:>7.1f} {s_err:>6.1f}{flag}")

    # Sigma comparison
    b_sigma = np.std(blend_result['blend_preds']) / np.std(blend_result['solar_a'])
    s_sigma = np.std(blend_result['stretch_preds']) / np.std(blend_result['solar_a'])
    print(f"\n  Blend pred σ/actual σ = {b_sigma:.3f}")
    print(f"  Stretch pred σ/actual σ = {s_sigma:.3f}")
    print(f"  (Previous blend without inertia: σ ratio ≈ 0.793)")
else:
    print(f"\n  All variants failed.")

total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
