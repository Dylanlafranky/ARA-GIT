#!/usr/bin/env python3
"""
Script 243BC v2 — Hale Modulation (Refined)

Previous attempt: multiplicative Hale at φ-power strengths was catastrophic
(LOO 57-62 vs baseline 44). The continuous cosine destroys cascade timing.

New approach:
  1. ADDITIVE, not multiplicative — don't corrupt the cascade shape
  2. Much weaker — 1/φ⁹ to 1/φ⁵ range (0.01 to 0.09)
  3. Test both the Hale frequency AND a subharmonic at Gleissberg/2
  4. Teleport-only first for speed, blend the winner

Also test: "anti-grief" — use the previous cycle's deviation with OPPOSITE
sign to the existing grief. If grief says "last was high, dampen", anti-grief
says "if we're dampening, we've gone too far — correct back."
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
INV_PHI_9 = INV_PHI ** 9
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
    """Quick teleport-only LOO for screening."""
    ns = {'__file__': combo_path, '__name__': '__exec__'}
    try:
        exec(code_str, ns)
    except Exception as e:
        print(f"  ⚠ {variant_name}: exec error: {e}")
        return None
    solar_t = ns['solar_t']
    solar_a = ns['solar_a']
    result = ns['run_formula_loo'](solar_t, solar_a, PHI**5, PHI, 5, "Solar")
    return {
        'loo': result['loo_mae'], 'corr': result['corr'],
        'preds': np.array(result['preds']),
        'sine': result['sine_mae'],
    }


def run_blend(code_str, variant_name):
    """Full blend pipeline."""
    ns = {'__file__': combo_path, '__name__': '__exec__'}
    exec(code_str, ns)
    solar_t = ns['solar_t']
    solar_a = ns['solar_a']
    grid_search = ns['grid_search']
    run_full_simulation = ns['run_full_simulation']

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
    }


print("=" * 78)
print("  Script 243BC v2 — Hale Modulation (Refined)")
print("  Screening via teleport-only | Champion blend: 38.73")
print("=" * 78)

# ═══════════════════════════════════════════
# PHASE 1: Teleport-only screening
# ═══════════════════════════════════════════

variants = []

# Baseline
variants.append(("BASELINE", base_code))

# A: ADDITIVE Hale at various strengths
for name, strength in [
    ("Hale-add 1/φ⁹", "INV_PHI_9"),
    ("Hale-add 1/φ⁶", f"{INV_PHI_6}"),
    ("Hale-add 1/φ⁵", f"{INV_PHI_5}"),
]:
    hale_block = f"""
        # ── HALE: additive alternating ──
        hale_phase = math.pi * (t - self.t_ref) / self.schwabe
        shape += {strength} * math.cos(hale_phase)
"""
    code = base_code.replace(STANDING_WAVE_MARKER,
                              STANDING_WAVE_MARKER + "\n" + hale_block)
    variants.append((name, code))

# B: Hale at HALF the Schwabe (so period = Schwabe, not 2×Schwabe)
# This tests if the alternation is per half-cycle, not per full cycle
for name, strength in [
    ("Half-Schw 1/φ⁶", f"{INV_PHI_6}"),
    ("Half-Schw 1/φ⁵", f"{INV_PHI_5}"),
]:
    hale_block = f"""
        # ── HALF-SCHWABE: alternation within each cycle ──
        half_phase = TAU * (t - self.t_ref) / self.schwabe
        shape += {strength} * math.cos(half_phase)
"""
    code = base_code.replace(STANDING_WAVE_MARKER,
                              STANDING_WAVE_MARKER + "\n" + hale_block)
    variants.append((name, code))

# C: Anti-grief — reverse the grief sign (positive feedback from previous deviation)
# Current grief: shape *= 1 + INV_PHI_3 * (-prev_dev) * exp(-PHI)
# Anti-grief adds: shape *= 1 + strength * (+prev_dev) * exp(-PHI)  [SAME direction]
for name, strength in [
    ("Anti-grief 1/φ⁴", f"{INV_PHI_4}"),
    ("Anti-grief 1/φ⁵", f"{INV_PHI_5}"),
]:
    # Add a SECOND grief-like term with opposite polarity (rebound)
    anti_grief = f"""
        # ── ANTI-GRIEF: rebound correction ──
        if self.prev_amp is not None:
            ag_dev = (self.prev_amp - self.base_amp) / self.base_amp
            shape *= (1.0 + {strength} * ag_dev * math.exp(-PHI))
"""
    code = base_code.replace(GRIEF_MARKER,
                              GRIEF_MARKER.replace(
                                  "grief_mult = 1.0 + INV_PHI_3 * (-prev_dev) * math.exp(-PHI)",
                                  f"grief_mult = 1.0 + INV_PHI_3 * (-prev_dev) * math.exp(-PHI)\n{' '*8}# plus rebound:\n{' '*8}grief_mult *= (1.0 + {strength} * prev_dev * math.exp(-PHI))"
                              ))
    variants.append((name, code))

# D: Gleissberg sub-harmonic (period = 2 × Gleissberg ≈ 176yr)
# The long-period modulation that might explain the clustering
for name, strength, period_mult in [
    ("Gleiss-sub 1/φ⁵", f"{INV_PHI_5}", 2.0),
    ("Gleiss-sub 1/φ⁴", f"{INV_PHI_4}", 2.0),
]:
    hale_block = f"""
        # ── GLEISSBERG SUB-HARMONIC ──
        gleiss_sub_period = live_gleissberg * {period_mult}
        gleiss_sub_phase = TAU * (t - self.t_ref) / gleiss_sub_period
        shape += {strength} * math.cos(gleiss_sub_phase)
"""
    code = base_code.replace(STANDING_WAVE_MARKER,
                              STANDING_WAVE_MARKER + "\n" + hale_block)
    variants.append((name, code))


print(f"\n  Screening {len(variants)} variants (teleport-only)...\n")
print(f"  {'Variant':30s} │ {'LOO':>7} │ {'Corr':>6} │ {'LOO/Sine':>8} │ {'Δ base':>7}")
print(f"  {'─'*30}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*7}")

screen_results = []
base_loo = None

for vname, code in variants:
    t0 = clock_time.time()
    result = run_teleport_only(code, vname)
    elapsed = clock_time.time() - t0
    if result is None:
        continue
    if base_loo is None:
        base_loo = result['loo']
    delta = result['loo'] - base_loo
    ratio = result['loo'] / result['sine']
    marker = " ★" if delta < -0.5 else ""
    screen_results.append((vname, result, code, delta))
    print(f"  {vname:30s} │ {result['loo']:>7.2f} │ {result['corr']:>+6.3f} │ {ratio:>8.3f} │ {delta:>+7.2f}{marker}  ({elapsed:.0f}s)")

# ═══════════════════════════════════════════
# PHASE 2: Run blend on top 3
# ═══════════════════════════════════════════

# Sort by LOO, take top 3 that beat baseline
winners = [x for x in sorted(screen_results, key=lambda x: x[1]['loo']) if x[3] < -0.3][:3]

if winners:
    print(f"\n{'=' * 78}")
    print(f"  PHASE 2: Blend pipeline on top {len(winners)} winners")
    print(f"{'=' * 78}")

    for vname, screen, code, delta in winners:
        t0 = clock_time.time()
        print(f"\n  Blending {vname}...", end="", flush=True)
        blend_result = run_blend(code, vname)
        elapsed = clock_time.time() - t0
        bdelta = blend_result['blend_loo'] - 38.73
        marker = "★ NEW CHAMPION" if bdelta < 0 else ""
        print(f"\r  {vname:30s} │ Blend LOO={blend_result['blend_loo']:6.2f} │ "
              f"Corr={blend_result['blend_corr']:+.3f} │ Δ champ={bdelta:+6.2f} │ {marker}  ({elapsed:.0f}s)")

        if bdelta < 0:
            # Show per-cycle
            ns_temp = {'__file__': combo_path, '__name__': '__exec__'}
            exec(base_code, ns_temp)
            solar_a = ns_temp['solar_a']
            solar_t = ns_temp['solar_t']
            SOLAR_CYCLES = ns_temp['SOLAR_CYCLES']

            print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Blend':>7} {'Err':>6}")
            for i in range(len(solar_t)):
                cn = SOLAR_CYCLES[i][0]
                b_err = blend_result['blend_errors'][i]
                flag = " ◀" if b_err > 60 else ""
                print(f"  C{cn:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
                      f"{blend_result['blend_preds'][i]:>7.1f} {b_err:>6.1f}{flag}")
else:
    print(f"\n  No variants beat baseline in teleport screening.")

total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
