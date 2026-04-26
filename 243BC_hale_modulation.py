#!/usr/bin/env python3
"""
Script 243BC — Hale Modulation (Alternating Dampener)

Dylan's insight: the residuals show an alternating pattern — every second
Schwabe cycle is systematically over/under predicted. This looks like a
~22-year Hale magnetic cycle that our formula doesn't account for.

The Sun's magnetic field flips polarity every ~11 years (one Schwabe cycle),
completing a full magnetic cycle every ~22 years (one Hale cycle). The
Gnevyshev-Ohl rule says consecutive Schwabe cycles have systematically
different amplitudes due to this polarity alternation.

Implementation: cos(π × t / Schwabe) flips sign every Schwabe cycle.
Multiply shape by (1 + strength × hale_cos).

We test strengths at φ-powers: 1/φ⁴, 1/φ³, 1/φ², 1/φ, and also 0.5.
Each variant runs through the FULL blend pipeline (path + teleport at 1/φ²).
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
BLEND_ALPHA = INV_PHI_2

t_start = clock_time.time()

# ── Load the 243AZ wave combo code ──
combo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "243AZ_wave_combo.py")
with open(combo_path, 'r') as f:
    combo_code = f.read()

# Strip MAIN section
lines = combo_code.split('\n')
cutoff = len(lines)
for i, line in enumerate(lines):
    if '# MAIN' in line and i > 400:
        cutoff = i
        break
base_code = '\n'.join(lines[:cutoff])


def run_variant(code_str, variant_name):
    """Exec a variant and run blended LOO on Solar."""
    ns = {'__file__': combo_path, '__name__': '__exec__'}
    try:
        exec(code_str, ns)
    except Exception as e:
        print(f"  ⚠ {variant_name}: exec error: {e}")
        return None

    solar_t = ns['solar_t']
    solar_a = ns['solar_a']
    run_formula_loo = ns['run_formula_loo']
    grid_search = ns['grid_search']
    run_full_simulation = ns['run_full_simulation']
    SOLAR_CYCLES = ns['SOLAR_CYCLES']

    N = len(solar_t)
    sine_baseline = np.mean(np.abs(solar_a - np.mean(solar_a)))

    # Teleport LOO
    teleport = run_formula_loo(solar_t, solar_a, PHI**5, PHI, 5, "Solar")
    teleport_preds = np.array(teleport['preds'])

    # Path LOO
    path_preds = []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        train_t = solar_t[mask]
        train_p = solar_a[mask]
        fit_tr, fit_ba, _ = grid_search(PHI**5, PHI, 5, train_t, train_p)
        snap_t, snap_a = run_full_simulation(
            train_t, train_p, PHI**5, PHI, 5, fit_tr, fit_ba)
        if len(snap_t) == 0:
            path_preds.append(np.mean(train_p))
        else:
            idx = np.argmin(np.abs(snap_t - solar_t[i]))
            path_preds.append(snap_a[idx])
    path_preds = np.array(path_preds)

    # Blend
    blended = BLEND_ALPHA * path_preds + (1 - BLEND_ALPHA) * teleport_preds
    blend_errors = np.abs(blended - solar_a)
    blend_loo = np.mean(blend_errors)
    blend_corr = np.corrcoef(blended, solar_a)[0, 1] if np.std(blended) > 0 else 0

    # Teleport-only LOO
    tele_loo = teleport['loo_mae']
    tele_corr = teleport['corr']

    # Path-only LOO
    path_errors = np.abs(path_preds - solar_a)
    path_loo = np.mean(path_errors)

    return {
        'blend_loo': blend_loo, 'blend_corr': blend_corr,
        'tele_loo': tele_loo, 'tele_corr': tele_corr,
        'path_loo': path_loo,
        'sine': sine_baseline,
        'blend_preds': blended, 'blend_errors': blend_errors,
        'tele_preds': teleport_preds, 'path_preds': path_preds,
    }


# ── The Hale insertion point ──
# Goes after standing wave, before grief. We insert after the standing wave block.
STANDING_WAVE_MARKER = "shape *= (1.0 + standing_delta * INV_PHI_3)"
GRIEF_MARKER = "# ── FIX 2 DISABLED"

# Verify markers exist
assert STANDING_WAVE_MARKER in base_code, "Can't find standing wave marker"
assert GRIEF_MARKER in base_code, "Can't find grief marker"

print("=" * 78)
print("  Script 243BC — Hale Modulation (Alternating Dampener)")
print("  Blend pipeline: α = 1/φ² | Champion blend LOO: 38.73")
print("=" * 78)

# ── Variants ──
variants = [
    ("BASELINE (no Hale)", None),
    ("Hale 1/φ⁴ (0.146)", INV_PHI_4),
    ("Hale 1/φ³ (0.236)", INV_PHI_3),
    ("Hale 1/φ² (0.382)", INV_PHI_2),
    ("Hale 1/φ  (0.618)", INV_PHI),
    ("Hale 0.5  (half)", 0.5),
]

results = []
SOLAR_CYCLES_DATA = None

for vname, strength in variants:
    t0 = clock_time.time()

    if strength is None:
        code = base_code
    else:
        # Insert Hale modulation after standing wave
        hale_block = f"""
        # ── HALE MODULATION: alternating dampener ──
        hale_phase = math.pi * (t - self.t_ref) / self.schwabe
        hale_cos = math.cos(hale_phase)
        shape *= (1.0 + {strength} * hale_cos)
"""
        code = base_code.replace(
            STANDING_WAVE_MARKER,
            STANDING_WAVE_MARKER + "\n" + hale_block
        )

    print(f"\n  Running {vname}...", end="", flush=True)
    result = run_variant(code, vname)
    elapsed = clock_time.time() - t0

    if result is None:
        continue

    delta = result['blend_loo'] - 38.73
    ratio = result['blend_loo'] / result['sine']
    marker = "★ NEW BEST" if result['blend_loo'] < 38.73 else ("✓ < sine" if ratio < 1.0 else "✗")
    results.append((vname, result, delta, marker))

    print(f"\r  {vname:30s} │ Blend LOO={result['blend_loo']:6.2f} │ Corr={result['blend_corr']:+.3f} │ "
          f"Tele={result['tele_loo']:6.2f} │ Path={result['path_loo']:6.2f} │ "
          f"Δ={delta:+6.2f} │ {marker}  ({elapsed:.0f}s)")

# ── Ranked results ──
print(f"\n{'=' * 78}")
print("  RANKED BY BLEND LOO")
print(f"{'=' * 78}")
for vname, result, delta, marker in sorted(results, key=lambda x: x[1]['blend_loo']):
    ratio = result['blend_loo'] / result['sine']
    print(f"  {result['blend_loo']:6.2f} │ {result['blend_corr']:+.3f} │ {ratio:.3f}× sine │ "
          f"Δ={delta:+6.2f} │ {vname} {marker}")

# ── Per-cycle breakdown of best ──
best = sorted(results, key=lambda x: x[1]['blend_loo'])[0]
bname, bresult = best[0], best[1]
if bresult['blend_loo'] < 38.73:
    print(f"\n{'─' * 78}")
    print(f"  Per-cycle: {bname}")
    print(f"{'─' * 78}")

    # Load cycle numbers from the base code namespace
    ns_temp = {'__file__': combo_path, '__name__': '__exec__'}
    exec(base_code, ns_temp)
    SOLAR_CYCLES = ns_temp['SOLAR_CYCLES']
    solar_a = ns_temp['solar_a']
    solar_t = ns_temp['solar_t']

    print(f"  {'C':>3} {'Year':>7} {'Act':>6} │ {'Blend':>7} {'Err':>6} │ {'Base Err':>8} │ {'Δ':>6}")
    base_result = [r for r in results if r[0].startswith("BASELINE")][0][1]
    for i in range(len(solar_t)):
        cn = SOLAR_CYCLES[i][0]
        actual = solar_a[i]
        b_pred = bresult['blend_preds'][i]
        b_err = bresult['blend_errors'][i]
        base_err = base_result['blend_errors'][i]
        d = b_err - base_err
        flag = " ◀ worse" if d > 5 else (" ★ better" if d < -5 else "")
        print(f"  C{cn:>2} {solar_t[i]:>7.1f} {actual:>6.1f} │ {b_pred:>7.1f} {b_err:>6.1f} │ {base_err:>8.1f} │ {d:>+6.1f}{flag}")

total = clock_time.time() - t_start
print(f"\n  Total runtime: {total:.0f}s")
