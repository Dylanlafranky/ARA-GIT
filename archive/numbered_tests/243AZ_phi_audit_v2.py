#!/usr/bin/env python3
"""
Script 243AZ v2 — φ Constant Audit (Real Pipeline)

Tests top 3 suspect φ-constants through the ACTUAL champion pipeline,
not a standalone engine. Each variant modifies one constant in the
champion 243AJ code via string replacement, then runs run_formula_loo.

Top 3 suspects from standalone screening:
  G2: gate_norm = φ  (instead of (φ+1/φ)/2)
  A3: eps symmetric 1/φ⁴  (instead of 1/φ³ for d≤0)
  E2: schwabe coupling = 1/φ²  (instead of 1/φ³)
"""

import sys, os, time, re
import numpy as np
import math

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4

t_start = time.time()

# Read the champion 243AJ source
champ_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "243AJ_amp_scale.py")
with open(champ_path, 'r') as f:
    champ_code = f.read()

# Strip the print/output section — we just want the functions + data
# Find the MAIN section and replace it
main_marker = '# MAIN'
lines = champ_code.split('\n')
cutoff = len(lines)
for i, line in enumerate(lines):
    if '# MAIN' in line or (line.strip().startswith('print("=') and i > 600):
        cutoff = i
        break

base_code = '\n'.join(lines[:cutoff])

# Define variants: (name, list of (old_str, new_str) replacements)
variants = [
    ("BASELINE (champion 243AJ)", []),

    # G2: gate normalization  (PHI + INV_PHI) / 2  → PHI
    ("G2: gate_norm=φ", [
        ("gate = state / ((PHI + INV_PHI) / 2)", "gate = state / PHI"),
    ]),

    # A3: eps symmetric — change the d≤0 branch from INV_PHI_3 to INV_PHI_4
    # Line 334: base_eps = INV_PHI_4 if d > 0 else INV_PHI_3
    ("A3: eps symmetric 1/φ⁴", [
        ("base_eps = INV_PHI_4 if d > 0 else INV_PHI_3",
         "base_eps = INV_PHI_4 if d > 0 else INV_PHI_4"),
    ]),

    # E2: schwabe coupling 1/φ² instead of 1/φ³
    # Line 370: shape += INV_PHI_3 * math.exp(-PHI * cp_schwabe) * math.cos(sp)
    ("E2: schwabe=1/φ²", [
        ("shape += INV_PHI_3 * math.exp(-PHI * cp_schwabe) * math.cos(sp)",
         "shape += INV_PHI_2 * math.exp(-PHI * cp_schwabe) * math.cos(sp)"),
    ]),

    # BONUS: amp_scale = φ (the docstring suspect)
    ("B1: amp_scale=φ", [
        ("self.amp_scale = self.midline",
         "self.amp_scale = PHI"),
    ]),

    # BONUS: collision_frac = 1/φ
    ("C1: collision_frac=1/φ", [
        ("eps_vals[j] *= (1 + collisions[j] * INV_PHI * 0.5)",
         "eps_vals[j] *= (1 + collisions[j] * INV_PHI * INV_PHI)"),
    ]),
]


print("=" * 78)
print("  φ CONSTANT AUDIT v2 — Real Pipeline (Solar LOO)")
print("  Champion LOO: 42.89 | Sine baseline: 48.78")
print("=" * 78)
print()

results = []

for vname, replacements in variants:
    # Apply replacements to the base code
    modified = base_code
    ok = True
    for old_str, new_str in replacements:
        if old_str not in modified:
            print(f"  ⚠ SKIP {vname}: couldn't find '{old_str}'")
            ok = False
            break
        modified = modified.replace(old_str, new_str, 1)

    if not ok:
        continue

    # Create a namespace and exec the modified code
    ns = {'__file__': champ_path, '__name__': '__main__'}
    try:
        exec(modified, ns)
    except Exception as e:
        print(f"  ⚠ SKIP {vname}: exec error: {e}")
        continue

    # Get Solar data and run LOO
    solar_t = ns.get('solar_t')
    solar_a = ns.get('solar_a')
    run_loo = ns.get('run_formula_loo')

    if solar_t is None or run_loo is None:
        print(f"  ⚠ SKIP {vname}: missing solar data or run_formula_loo")
        continue

    try:
        result = run_loo(solar_t, solar_a, PHI**5, PHI, 5, "Solar")
        loo = result['loo_mae']
        corr = result['corr']
        ratio = result['ratio']
        delta = loo - 42.89
        marker = "★ NEW BEST" if loo < 42.89 else ("✓ beats sine" if ratio < 1.0 else "✗")
        results.append((vname, loo, corr, delta, ratio, marker))
        print(f"  {vname:40s} │ LOO={loo:6.2f} │ Corr={corr:+.3f} │ Δchamp={delta:+6.2f} │ LOO/sine={ratio:.3f} │ {marker}")
    except Exception as e:
        print(f"  ⚠ SKIP {vname}: LOO error: {e}")

print()
print("=" * 78)
print("  RANKED BY LOO (best first)")
print("=" * 78)
for vname, loo, corr, delta, ratio, marker in sorted(results, key=lambda x: x[1]):
    print(f"  {loo:6.2f} │ {corr:+.3f} │ Δ={delta:+6.2f} │ {ratio:.3f}× sine │ {vname} {marker}")

elapsed = time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
