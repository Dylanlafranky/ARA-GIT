#!/usr/bin/env python3
"""
Script 243BD — Discrete Alternation & Reverse-From-Below

Hale cosine modulation FAILED — continuous sinusoidal is the wrong shape.
The alternating residuals Dylan spotted aren't sinusoidal; they're discrete.

New approaches:
  1. DISCRETE even/odd: count cycles from t_ref, apply +/- nudge on alternating
  2. SIGN OF DERIVATIVE: if amplitude is rising vs falling, apply asymmetric scaling
  3. REVERSE FROM BELOW: instead of modulating shape from above (long periods),
     let the cascade's own internal state (prev_amp trend) set a discrete flip

Also: properly investigate the residual pattern first to understand what we're
actually fighting.
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
INV_PHI_6 = INV_PHI ** 6
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

STANDING_WAVE_MARKER = "shape *= (1.0 + standing_delta * INV_PHI_3)"
GRIEF_MARKER = "grief_mult = 1.0 + INV_PHI_3 * (-prev_dev) * math.exp(-PHI)"


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


# ═══════════════════════════════════════════
# PHASE 0: Analyze the actual residual pattern
# ═══════════════════════════════════════════

print("=" * 78)
print("  Script 243BD — Discrete Alternation & Reverse-From-Below")
print("  Analyzing residual pattern first, then testing corrections")
print("=" * 78)

print("\n  PHASE 0: Residual analysis on baseline...")
base_result = run_teleport_only(base_code, "BASELINE")
if base_result is None:
    print("  FATAL: Baseline failed")
    sys.exit(1)

solar_a = base_result['solar_a']
solar_t = base_result['solar_t']
preds = base_result['preds']
errors = preds - solar_a  # signed: positive = overshoot, negative = undershoot
abs_errors = np.abs(errors)

print(f"\n  Baseline teleport LOO: {base_result['loo']:.2f}")
print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} {'Pred':>6} {'Error':>7} │ {'Sign':>5} {'|Err|':>6} {'Even/Odd':>8}")
for i in range(len(solar_t)):
    cn = base_result['cycles'][i][0]
    sign = "+" if errors[i] > 0 else "-"
    eo = "even" if cn % 2 == 0 else "odd"
    flag = " ◀" if abs_errors[i] > 40 else ""
    print(f"  C{cn:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} {preds[i]:>6.1f} {errors[i]:>+7.1f} │ {sign:>5} {abs_errors[i]:>6.1f} {eo:>8}{flag}")

# Check if even vs odd cycles have different mean errors
even_err = [errors[i] for i in range(len(solar_t)) if base_result['cycles'][i][0] % 2 == 0]
odd_err = [errors[i] for i in range(len(solar_t)) if base_result['cycles'][i][0] % 2 == 1]
print(f"\n  Even cycles: mean signed error = {np.mean(even_err):+.1f}, mean |error| = {np.mean(np.abs(even_err)):.1f}")
print(f"  Odd cycles:  mean signed error = {np.mean(odd_err):+.1f}, mean |error| = {np.mean(np.abs(odd_err)):.1f}")

# Check consecutive differences (is there a flip-flop?)
consec_signs = []
for i in range(1, len(errors)):
    same_sign = (errors[i] > 0) == (errors[i-1] > 0)
    consec_signs.append(same_sign)
flips = sum(1 for x in consec_signs if not x)
print(f"  Consecutive sign flips: {flips}/{len(consec_signs)} ({100*flips/len(consec_signs):.0f}%)")
print(f"  (50% = random, >60% = alternating, <40% = clustering)")

# Autocorrelation of signed errors at lag 1 and lag 2
if len(errors) > 2:
    ac1 = np.corrcoef(errors[:-1], errors[1:])[0, 1]
    ac2 = np.corrcoef(errors[:-2], errors[2:])[0, 1]
    print(f"  Error autocorrelation: lag-1 = {ac1:+.3f}, lag-2 = {ac2:+.3f}")
    print(f"  (negative lag-1 = alternating, positive lag-2 = wave)")

# ═══════════════════════════════════════════
# PHASE 1: Targeted variants based on analysis
# ═══════════════════════════════════════════

print(f"\n{'=' * 78}")
print(f"  PHASE 1: Teleport screening of targeted variants")
print(f"{'=' * 78}")

variants = []

# 1. Discrete even/odd: cycle_number parity sets sign
#    shape *= (1 + strength) for even, shape *= (1 - strength) for odd (or vice versa)
for name, strength in [
    ("Discrete ±1/φ⁵", INV_PHI_5),
    ("Discrete ±1/φ⁶", INV_PHI_6),
]:
    block = f"""
        # ── DISCRETE EVEN/ODD ──
        cycle_num = round((t - self.t_ref) / self.schwabe)
        if cycle_num % 2 == 0:
            shape *= (1.0 + {strength})
        else:
            shape *= (1.0 - {strength})
"""
    code = base_code.replace(STANDING_WAVE_MARKER,
                              STANDING_WAVE_MARKER + "\n" + block)
    variants.append((name, code))

# 2. Trend-based: if prev_amp > base_amp (rising), apply one correction;
#    if prev_amp < base_amp (falling), apply opposite
#    This is "reverse from below" — the cascade's own derivative drives the flip
for name, strength in [
    ("Trend-flip 1/φ⁵", INV_PHI_5),
]:
    # Replace grief line with an enhanced version
    new_grief = f"""grief_mult = 1.0 + INV_PHI_3 * (-prev_dev) * math.exp(-PHI)
        # ── TREND FLIP: rising vs falling correction ──
        if prev_dev > 0:  # prev cycle was above average → system is "hot"
            grief_mult *= (1.0 - {strength})  # extra dampening
        else:  # prev cycle was below average → system is "cold"
            grief_mult *= (1.0 + {strength})  # extra boost"""
    code = base_code.replace(GRIEF_MARKER, new_grief)
    variants.append((name, code))

print(f"\n  Screening {len(variants)} variants...\n")
print(f"  {'Variant':30s} │ {'LOO':>7} │ {'Corr':>6} │ {'LOO/Sine':>8} │ {'Δ base':>7}")
print(f"  {'─'*30}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*7}")

screen_results = []
base_loo = base_result['loo']

for vname, code in variants:
    t0 = clock_time.time()
    result = run_teleport_only(code, vname)
    elapsed = clock_time.time() - t0
    if result is None:
        continue
    delta = result['loo'] - base_loo
    ratio = result['loo'] / result['sine']
    marker = " ★" if delta < -0.5 else ""
    screen_results.append((vname, result, code, delta))
    print(f"  {vname:30s} │ {result['loo']:>7.2f} │ {result['corr']:>+6.3f} │ {ratio:>8.3f} │ {delta:>+7.2f}{marker}  ({elapsed:.0f}s)")

# ═══════════════════════════════════════════
# Show per-cycle comparison for any winner
# ═══════════════════════════════════════════

winner = None
for x in sorted(screen_results, key=lambda x: x[1]['loo']):
    if x[3] < -0.3:
        winner = x
        break

if winner:
    vname, wresult, code, delta = winner
    print(f"\n  Winner: {vname} (Δ = {delta:+.2f})")
    w_preds = wresult['preds']
    w_errors = w_preds - solar_a
    print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Base':>6} {'B err':>6} │ {'New':>6} {'N err':>6} │ {'Δ':>6}")
    for i in range(len(solar_t)):
        cn = base_result['cycles'][i][0]
        b_err = abs_errors[i]
        n_err = np.abs(w_errors[i])
        d = n_err - b_err
        flag = " ★" if d < -5 else (" ◀" if d > 5 else "")
        print(f"  C{cn:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ {preds[i]:>6.1f} {b_err:>6.1f} │ {w_preds[i]:>6.1f} {n_err:>6.1f} │ {d:>+6.1f}{flag}")
else:
    print(f"\n  No variant beat baseline. The alternating pattern may not be")
    print(f"  correctable with simple even/odd or trend-based modulation.")
    print(f"  Consider: the pattern might be an artifact of small N (25 cycles)")
    print(f"  rather than a true physical mechanism.")

total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
