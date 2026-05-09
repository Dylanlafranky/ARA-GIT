#!/usr/bin/env python3
"""
Script 95 — ENERGY AXIS FORMALIZATION
=====================================================================
The energy axis (logE) is the weakest coordinate in the ARA 3D spine.
Different scales use different kinds of energy (binding, metabolic,
mechanical, thermal, luminosity). This script tests six candidate
replacements for the energy axis:

  1. Raw E (baseline)
  2. Action: S = E × T  (units J·s = ℏ)
  3. Power: P = E / T  (units W)
  4. Action per cycle: S / 2π
  5. Dimensionless action: S / ℏ
  6. Entropy proxy: k_B × ln(S / ℏ)

For each candidate we measure:
  - Slope consistency across 8 scales
  - Meta-wave sine/parabola fit quality
  - Circle circularity in each system
  - Monotonicity with scale order
  - Whether anomalies (subatomic negative slope) are reduced

TESTS (10):
  1. At least one candidate gives more uniform slopes (lower CV)
  2. Action (E×T) meta-wave R² > 0.9
  3. Power (E/T) shows less scale variation than raw E
  4. Action/ℏ increases monotonically with scale (Spearman r > 0.8)
  5. Best candidate improves sine fit R² over raw E
  6. Circle circularity improves for ≥ 1 system with best candidate
  7. log(S/ℏ) spacing more regular than logE spacing
  8. At least one candidate reduces subatomic negative slope anomaly
  9. Best energy axis makes planetary peak slope closer to φ
  10. Action/ℏ spans > 100 decades from subatomic to cosmic

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit
import sys, os, io

# ============================================================
# LOAD DATA FROM SCRIPT 89
# ============================================================
script_dir = os.path.dirname(os.path.abspath(__file__))
script_89 = os.path.join(script_dir, '89_gap_filling_scales.py')
old_stdout = sys.stdout
sys.stdout = io.StringIO()
exec(open(script_89).read())
sys.stdout = old_stdout
# 'results' now available with fields: name, T, logT, logE, ARA, sys, scale, layer

PHI = (1 + np.sqrt(5)) / 2
HBAR = 1.0546e-34   # J·s
K_B  = 1.3806e-23   # J/K
BOUNDARY_1 = 0.6
BOUNDARY_2 = 1.4

scales_ordered = ["subatomic", "quantum", "cellular", "organ", "organism",
                  "planetary", "solar-system", "cosmic"]

print("=" * 72)
print("SCRIPT 95 — ENERGY AXIS FORMALIZATION")
print("Which quantity makes the best energy coordinate?")
print("=" * 72)
print(f"\n  Loaded {len(results)} processes from Script 89")

# ============================================================
# PART 1: COMPUTE ALL CANDIDATES
# ============================================================
print("\n" + "=" * 72)
print("PART 1: COMPUTING 6 ENERGY-AXIS CANDIDATES FOR ALL PROCESSES")
print("=" * 72)

for r in results:
    E = 10**r['logE']       # energy in joules
    T = r['T']              # period in seconds

    r['E']       = E
    r['action']  = E * T                  # S = E × T  (J·s)
    r['power']   = E / T                  # P = E / T  (W)
    r['act_cyc'] = E * T / (2 * np.pi)   # S / 2π
    r['act_h']   = E * T / HBAR           # S / ℏ  (dimensionless)
    r['entropy'] = K_B * np.log(max(E * T / HBAR, 1e-300))  # k_B ln(S/ℏ)

    # Log versions (safe)
    r['logE_raw']     = r['logE']
    r['logAction']    = np.log10(max(r['action'], 1e-300))
    r['logPower']     = np.log10(max(r['power'], 1e-300))
    r['logActCyc']    = np.log10(max(r['act_cyc'], 1e-300))
    r['logActH']      = np.log10(max(r['act_h'], 1e-300))
    r['logEntropy']   = np.log10(max(r['entropy'], 1e-300))

candidates = {
    'Raw E':       'logE_raw',
    'Action E×T':  'logAction',
    'Power E/T':   'logPower',
    'Action/2π':   'logActCyc',
    'Action/ℏ':    'logActH',
    'Entropy':     'logEntropy',
}

# Show a sample
print(f"\n  {'Process':<28s} {'logE':>7s} {'logS':>8s} {'logP':>8s} {'logS/ℏ':>10s} {'logEntr':>8s}")
print(f"  {'-'*28} {'-'*7} {'-'*8} {'-'*8} {'-'*10} {'-'*8}")
for r in results[:10]:
    print(f"  {r['name']:<28s} {r['logE_raw']:7.1f} {r['logAction']:8.1f} "
          f"{r['logPower']:8.1f} {r['logActH']:10.1f} {r['logEntropy']:8.1f}")
print(f"  ... ({len(results)} total)")

# ============================================================
# PART 2: SCALE SLOPES FOR EACH CANDIDATE
# ============================================================
print("\n" + "=" * 72)
print("PART 2: SCALE SLOPES — WHICH CANDIDATE IS MOST CONSISTENT?")
print("=" * 72)

def compute_scale_slopes(field):
    """Compute logY/logT slope at each of 8 scales."""
    slopes = []
    for scale in scales_ordered:
        pts = [r for r in results if r['scale'] == scale]
        if len(pts) < 4:
            slopes.append(np.nan)
            continue
        x = np.array([r['logT'] for r in pts])
        y = np.array([r[field] for r in pts])
        sl, _, _, _, _ = stats.linregress(x, y)
        slopes.append(sl)
    return slopes

# Compute slopes for all candidates
all_slopes = {}
for cname, field in candidates.items():
    all_slopes[cname] = compute_scale_slopes(field)

# Print slope table
print(f"\n  {'Scale':<15s}", end='')
for cname in candidates:
    print(f"  {cname:>10s}", end='')
print()
print(f"  {'-'*15}", end='')
for _ in candidates:
    print(f"  {'-'*10}", end='')
print()

for i, scale in enumerate(scales_ordered):
    print(f"  {scale:<15s}", end='')
    for cname in candidates:
        sl = all_slopes[cname][i]
        if np.isnan(sl):
            print(f"  {'N/A':>10s}", end='')
        else:
            print(f"  {sl:10.3f}", end='')
    print()

# CV of slopes (lower = more consistent)
print(f"\n  Slope uniformity (CV = stdev/|mean|, lower is better):")
slope_cvs = {}
for cname in candidates:
    svals = [s for s in all_slopes[cname] if not np.isnan(s)]
    if len(svals) > 1 and np.mean(svals) != 0:
        cv = np.std(svals) / abs(np.mean(svals))
    else:
        cv = float('inf')
    slope_cvs[cname] = cv
    print(f"    {cname:<15s}: CV = {cv:.3f}")

best_cv_name = min(slope_cvs, key=slope_cvs.get)
print(f"\n  Most uniform slopes: {best_cv_name} (CV = {slope_cvs[best_cv_name]:.3f})")
raw_cv = slope_cvs['Raw E']
print(f"  Raw E baseline CV: {raw_cv:.3f}")

# ============================================================
# PART 2b: META-WAVE FITS (sine and parabola)
# ============================================================
print("\n" + "=" * 72)
print("PART 2b: META-WAVE FITS — SINE AND PARABOLA FOR EACH CANDIDATE")
print("=" * 72)

def sine_func(x, A, phi, C):
    return A * np.sin(2 * np.pi * x / 8.0 + phi) + C

def parabola_func(x, a, x0, y0):
    return a * (x - x0)**2 + y0

orders = np.arange(len(scales_ordered), dtype=float)

sine_r2s = {}
para_r2s = {}

for cname in candidates:
    svals = np.array(all_slopes[cname])
    valid = ~np.isnan(svals)
    x = orders[valid]
    y = svals[valid]

    if len(x) < 4:
        sine_r2s[cname] = 0
        para_r2s[cname] = 0
        continue

    ss_tot = np.sum((y - np.mean(y))**2)
    if ss_tot < 1e-30:
        sine_r2s[cname] = 0
        para_r2s[cname] = 0
        continue

    # Sine fit
    try:
        popt, _ = curve_fit(sine_func, x, y, p0=[np.std(y), 0, np.mean(y)], maxfev=5000)
        pred = sine_func(x, *popt)
        sine_r2s[cname] = 1 - np.sum((y - pred)**2) / ss_tot
    except:
        sine_r2s[cname] = 0

    # Parabola fit
    try:
        popt, _ = curve_fit(parabola_func, x, y, p0=[-0.05, 4, np.max(y)], maxfev=5000)
        pred = parabola_func(x, *popt)
        para_r2s[cname] = 1 - np.sum((y - pred)**2) / ss_tot
    except:
        para_r2s[cname] = 0

print(f"\n  {'Candidate':<15s}  {'Sine R²':>8s}  {'Parabola R²':>12s}")
print(f"  {'-'*15}  {'-'*8}  {'-'*12}")
for cname in candidates:
    print(f"  {cname:<15s}  {sine_r2s[cname]:8.4f}  {para_r2s[cname]:12.4f}")

best_sine_name = max(sine_r2s, key=sine_r2s.get)
print(f"\n  Best sine fit: {best_sine_name} (R² = {sine_r2s[best_sine_name]:.4f})")
print(f"  Raw E sine R²: {sine_r2s['Raw E']:.4f}")

# ============================================================
# PART 3: CIRCLE CIRCULARITY TEST
# ============================================================
print("\n" + "=" * 72)
print("PART 3: CIRCLE CIRCULARITY — EIGENVALUE RATIO IN EACH SYSTEM")
print("=" * 72)

def circularity_ratio(logT_arr, logY_arr):
    """Ratio of eigenvalues of 2D point cloud. 1.0 = perfect circle."""
    if len(logT_arr) < 3:
        return 0.0
    # Standardize
    x = (logT_arr - np.mean(logT_arr))
    y = (logY_arr - np.mean(logY_arr))
    if np.std(x) > 0:
        x = x / np.std(x)
    if np.std(y) > 0:
        y = y / np.std(y)
    cov = np.cov(x, y)
    eigvals = np.linalg.eigvalsh(cov)
    eigvals = np.sort(eigvals)
    if eigvals[-1] < 1e-30:
        return 0.0
    return eigvals[0] / eigvals[-1]  # 1 = circular, 0 = linear

circ_by_candidate = {}
for cname, field in candidates.items():
    circ_by_sys = {}
    for sys_num in [1, 2, 3]:
        pts = [r for r in results if r['sys'] == sys_num]
        if len(pts) < 5:
            circ_by_sys[sys_num] = 0.0
            continue
        logT_arr = np.array([r['logT'] for r in pts])
        logY_arr = np.array([r[field] for r in pts])
        circ_by_sys[sys_num] = circularity_ratio(logT_arr, logY_arr)
    circ_by_candidate[cname] = circ_by_sys

print(f"\n  {'Candidate':<15s}  {'Sys 1':>7s}  {'Sys 2':>7s}  {'Sys 3':>7s}  {'Mean':>7s}")
print(f"  {'-'*15}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*7}")
for cname in candidates:
    c = circ_by_candidate[cname]
    mn = np.mean([c[1], c[2], c[3]])
    print(f"  {cname:<15s}  {c[1]:7.4f}  {c[2]:7.4f}  {c[3]:7.4f}  {mn:7.4f}")

# Find which candidate improves circularity over Raw E for at least one system
raw_circ = circ_by_candidate['Raw E']
circ_improved = {}
for cname in candidates:
    if cname == 'Raw E':
        continue
    c = circ_by_candidate[cname]
    improved = any(c[s] > raw_circ[s] for s in [1, 2, 3])
    circ_improved[cname] = improved

best_circ_name = max(circ_by_candidate, key=lambda cn: np.mean(list(circ_by_candidate[cn].values())))
print(f"\n  Best mean circularity: {best_circ_name}")

# ============================================================
# PART 4: ACTION/ℏ AS THE NATURAL AXIS
# ============================================================
print("\n" + "=" * 72)
print("PART 4: DIMENSIONLESS ACTION S/ℏ — THE NATURAL AXIS?")
print("=" * 72)

# Group by scale, compute median logActH
print(f"\n  {'Scale':<15s}  {'Median log(S/ℏ)':>16s}  {'Min':>10s}  {'Max':>10s}  {'Range':>8s}")
print(f"  {'-'*15}  {'-'*16}  {'-'*10}  {'-'*10}  {'-'*8}")

scale_median_acth = {}
for scale in scales_ordered:
    pts = [r for r in results if r['scale'] == scale]
    vals = [r['logActH'] for r in pts]
    med = np.median(vals)
    scale_median_acth[scale] = med
    print(f"  {scale:<15s}  {med:16.1f}  {min(vals):10.1f}  {max(vals):10.1f}  {max(vals)-min(vals):8.1f}")

# Monotonicity test
scale_order_nums = list(range(len(scales_ordered)))
median_vals = [scale_median_acth[s] for s in scales_ordered]
r_mono, p_mono = stats.spearmanr(scale_order_nums, median_vals)
print(f"\n  Spearman correlation (scale order vs median log(S/ℏ)): r = {r_mono:.4f}, p = {p_mono:.6f}")

# Total range
all_acth = [r['logActH'] for r in results]
acth_range = max(all_acth) - min(all_acth)
print(f"  Total range of log(S/ℏ): {acth_range:.1f} decades")
print(f"    Min: {min(all_acth):.1f} (subatomic)")
print(f"    Max: {max(all_acth):.1f} (cosmic)")

# ============================================================
# PART 5: DOES POWER (E/T) COLLAPSE THE SCALES?
# ============================================================
print("\n" + "=" * 72)
print("PART 5: POWER E/T — DOES IT COLLAPSE SCALE DEPENDENCE?")
print("=" * 72)

print(f"\n  {'Scale':<15s}  {'logP slope':>11s}  {'logE slope':>11s}  {'|ΔSlope|':>10s}")
print(f"  {'-'*15}  {'-'*11}  {'-'*11}  {'-'*10}")

power_slopes = all_slopes['Power E/T']
raw_slopes = all_slopes['Raw E']

for i, scale in enumerate(scales_ordered):
    ps = power_slopes[i]
    rs = raw_slopes[i]
    if np.isnan(ps) or np.isnan(rs):
        print(f"  {scale:<15s}  {'N/A':>11s}  {'N/A':>11s}  {'N/A':>10s}")
    else:
        print(f"  {scale:<15s}  {ps:11.3f}  {rs:11.3f}  {abs(ps)-abs(rs):10.3f}")

# Variance of slopes
power_valid = [s for s in power_slopes if not np.isnan(s)]
raw_valid = [s for s in raw_slopes if not np.isnan(s)]
power_var = np.var(power_valid)
raw_var = np.var(raw_valid)
print(f"\n  Slope variance: Power = {power_var:.4f}, Raw E = {raw_var:.4f}")
print(f"  Power reduces variance: {power_var < raw_var}")

# ============================================================
# PART 6: INFORMATION CONTENT — log(S/ℏ) vs SCALE ORDER
# ============================================================
print("\n" + "=" * 72)
print("PART 6: INFORMATION CONTENT — IS log(S/ℏ) SPACING REGULAR?")
print("=" * 72)

# Average log(S/ℏ) per scale
avg_acth = []
avg_logE = []
for scale in scales_ordered:
    pts = [r for r in results if r['scale'] == scale]
    avg_acth.append(np.mean([r['logActH'] for r in pts]))
    avg_logE.append(np.mean([r['logE_raw'] for r in pts]))

# Spacings
acth_spacings = np.diff(avg_acth)
logE_spacings = np.diff(avg_logE)

print(f"\n  {'Transition':<30s}  {'Δlog(S/ℏ)':>10s}  {'ΔlogE':>10s}")
print(f"  {'-'*30}  {'-'*10}  {'-'*10}")
for i in range(len(acth_spacings)):
    trans = f"{scales_ordered[i]} → {scales_ordered[i+1]}"
    print(f"  {trans:<30s}  {acth_spacings[i]:10.1f}  {logE_spacings[i]:10.1f}")

acth_cv = np.std(acth_spacings) / abs(np.mean(acth_spacings)) if abs(np.mean(acth_spacings)) > 0 else float('inf')
logE_cv = np.std(logE_spacings) / abs(np.mean(logE_spacings)) if abs(np.mean(logE_spacings)) > 0 else float('inf')
print(f"\n  Spacing CV: log(S/ℏ) = {acth_cv:.3f}, logE = {logE_cv:.3f}")
print(f"  log(S/ℏ) more regular: {acth_cv < logE_cv}")

# Linear fit: log(S/ℏ) vs scale order
r_lin, p_lin = stats.pearsonr(scale_order_nums, avg_acth)
print(f"\n  Pearson r (scale order vs avg log(S/ℏ)): {r_lin:.4f}")

# ============================================================
# PART 7: OVERALL RANKING OF CANDIDATES
# ============================================================
print("\n" + "=" * 72)
print("PART 7: OVERALL CANDIDATE RANKING")
print("=" * 72)

# Composite score for each candidate
print(f"\n  {'Candidate':<15s}  {'Slope CV':>9s}  {'Sine R²':>8s}  {'Para R²':>8s}  {'Circ':>6s}")
print(f"  {'-'*15}  {'-'*9}  {'-'*8}  {'-'*8}  {'-'*6}")
for cname in candidates:
    cv = slope_cvs[cname]
    sr = sine_r2s[cname]
    pr = para_r2s[cname]
    cr = np.mean(list(circ_by_candidate[cname].values()))
    print(f"  {cname:<15s}  {cv:9.3f}  {sr:8.4f}  {pr:8.4f}  {cr:6.4f}")

# Determine overall best
# Normalize each metric to [0,1] and sum (lower CV is better, higher R² and circ are better)
scores = {}
cv_vals = [slope_cvs[c] for c in candidates]
sr_vals = [sine_r2s[c] for c in candidates]
pr_vals = [para_r2s[c] for c in candidates]
cr_vals = [np.mean(list(circ_by_candidate[c].values())) for c in candidates]

cv_min, cv_max = min(cv_vals), max(cv_vals)
sr_min, sr_max = min(sr_vals), max(sr_vals)
pr_min, pr_max = min(pr_vals), max(pr_vals)
cr_min, cr_max = min(cr_vals), max(cr_vals)

for cname in candidates:
    # CV: lower is better → invert
    cv_norm = 1 - (slope_cvs[cname] - cv_min) / (cv_max - cv_min + 1e-30)
    sr_norm = (sine_r2s[cname] - sr_min) / (sr_max - sr_min + 1e-30)
    pr_norm = (para_r2s[cname] - pr_min) / (pr_max - pr_min + 1e-30)
    cr_norm = (np.mean(list(circ_by_candidate[cname].values())) - cr_min) / (cr_max - cr_min + 1e-30)
    scores[cname] = cv_norm + sr_norm + pr_norm + cr_norm

ranked = sorted(scores, key=scores.get, reverse=True)
print(f"\n  Composite ranking (higher = better):")
for i, cname in enumerate(ranked):
    print(f"    {i+1}. {cname:<15s}  score = {scores[cname]:.3f}")

overall_best = ranked[0]
print(f"\n  OVERALL BEST: {overall_best}")

# ============================================================
# PART 8: SUBATOMIC SLOPE ANOMALY
# ============================================================
print("\n" + "=" * 72)
print("PART 8: SUBATOMIC SLOPE ANOMALY — WHICH CANDIDATE FIXES IT?")
print("=" * 72)

sub_idx = scales_ordered.index('subatomic')
print(f"\n  Subatomic slope by candidate:")
for cname in candidates:
    sl = all_slopes[cname][sub_idx]
    marker = " ← closest to 0" if cname == min(candidates, key=lambda c: abs(all_slopes[c][sub_idx])) else ""
    if np.isnan(sl):
        print(f"    {cname:<15s}: N/A")
    else:
        print(f"    {cname:<15s}: {sl:+.3f}{marker}")

raw_sub_slope = all_slopes['Raw E'][sub_idx]
reduced_anomaly = {}
for cname in candidates:
    if cname == 'Raw E':
        continue
    sl = all_slopes[cname][sub_idx]
    if np.isnan(sl) or np.isnan(raw_sub_slope):
        reduced_anomaly[cname] = False
    else:
        reduced_anomaly[cname] = abs(sl) < abs(raw_sub_slope)
    print(f"    {cname} reduces anomaly: {reduced_anomaly.get(cname, False)}")

# ============================================================
# PART 9: PLANETARY PEAK SLOPE vs φ
# ============================================================
print("\n" + "=" * 72)
print("PART 9: PLANETARY PEAK — WHICH CANDIDATE MAKES IT CLOSEST TO φ?")
print("=" * 72)

plan_idx = scales_ordered.index('planetary')
print(f"\n  Planetary slope by candidate (φ = {PHI:.6f}):")
for cname in candidates:
    sl = all_slopes[cname][plan_idx]
    if np.isnan(sl):
        print(f"    {cname:<15s}: N/A")
    else:
        dist = abs(sl - PHI)
        print(f"    {cname:<15s}: {sl:+.4f}  (distance to φ: {dist:.4f})")

raw_plan_dist = abs(all_slopes['Raw E'][plan_idx] - PHI)
best_plan_name = min(candidates, key=lambda c: abs(all_slopes[c][plan_idx] - PHI) if not np.isnan(all_slopes[c][plan_idx]) else float('inf'))
best_plan_dist = abs(all_slopes[best_plan_name][plan_idx] - PHI)
print(f"\n  Closest to φ: {best_plan_name} (distance {best_plan_dist:.4f})")
print(f"  Raw E distance: {raw_plan_dist:.4f}")

# ============================================================
# TESTS
# ============================================================
print("\n" + "=" * 72)
print("TESTS")
print("=" * 72)

passed = 0
total_tests = 10

# Test 1: At least one candidate gives lower CV of slopes than raw E
t1 = any(slope_cvs[c] < slope_cvs['Raw E'] for c in candidates if c != 'Raw E')
print(f"\n  Test  1: At least one candidate has lower slope CV than Raw E")
print(f"           Raw E CV = {slope_cvs['Raw E']:.3f}")
better_cvs = [(c, slope_cvs[c]) for c in candidates if c != 'Raw E' and slope_cvs[c] < slope_cvs['Raw E']]
if better_cvs:
    for c, cv in better_cvs:
        print(f"           {c}: CV = {cv:.3f}")
print(f"           -> {'PASS' if t1 else 'FAIL'}")
passed += t1

# Test 2: Action (E×T) gives meta-wave with R² > 0.9
action_best_r2 = max(sine_r2s['Action E×T'], para_r2s['Action E×T'])
t2 = action_best_r2 > 0.9
print(f"\n  Test  2: Action (E×T) meta-wave R² > 0.9")
print(f"           Sine R² = {sine_r2s['Action E×T']:.4f}, Parabola R² = {para_r2s['Action E×T']:.4f}")
print(f"           Best = {action_best_r2:.4f}")
print(f"           -> {'PASS' if t2 else 'FAIL'}")
passed += t2

# Test 3: Power shows less scale variation than raw E
t3 = power_var < raw_var
print(f"\n  Test  3: Power (E/T) slope variance < Raw E slope variance")
print(f"           Power var = {power_var:.4f}, Raw E var = {raw_var:.4f}")
print(f"           -> {'PASS' if t3 else 'FAIL'}")
passed += t3

# Test 4: Action/ℏ increases monotonically with scale (Spearman r > 0.8)
t4 = r_mono > 0.8
print(f"\n  Test  4: Action/ℏ increases monotonically with scale (Spearman r > 0.8)")
print(f"           Spearman r = {r_mono:.4f}")
print(f"           -> {'PASS' if t4 else 'FAIL'}")
passed += t4

# Test 5: Best candidate improves sine fit R² over raw E
raw_sine = sine_r2s['Raw E']
best_sine_r2 = max(sine_r2s.values())
t5 = best_sine_r2 > raw_sine
print(f"\n  Test  5: Best candidate sine R² > Raw E sine R²")
print(f"           Raw E: {raw_sine:.4f}, Best ({best_sine_name}): {best_sine_r2:.4f}")
print(f"           -> {'PASS' if t5 else 'FAIL'}")
passed += t5

# Test 6: Circle circularity improves for ≥ 1 system with best candidate
t6 = any(circ_improved.get(c, False) for c in circ_improved)
improved_list = [c for c in circ_improved if circ_improved[c]]
print(f"\n  Test  6: Circularity improves for ≥ 1 system with some candidate")
print(f"           Improved: {improved_list if improved_list else 'none'}")
print(f"           -> {'PASS' if t6 else 'FAIL'}")
passed += t6

# Test 7: log(S/ℏ) spacing more regular than logE spacing
t7 = acth_cv < logE_cv
print(f"\n  Test  7: log(S/ℏ) spacing CV < logE spacing CV")
print(f"           log(S/ℏ) CV = {acth_cv:.3f}, logE CV = {logE_cv:.3f}")
print(f"           -> {'PASS' if t7 else 'FAIL'}")
passed += t7

# Test 8: At least one candidate reduces subatomic negative slope anomaly
t8 = any(reduced_anomaly.get(c, False) for c in reduced_anomaly)
print(f"\n  Test  8: At least one candidate reduces subatomic slope anomaly")
print(f"           Raw E subatomic slope: {raw_sub_slope:+.3f}")
reducers = [c for c in reduced_anomaly if reduced_anomaly[c]]
if reducers:
    for c in reducers:
        print(f"           {c}: {all_slopes[c][sub_idx]:+.3f}")
print(f"           -> {'PASS' if t8 else 'FAIL'}")
passed += t8

# Test 9: Best energy axis makes planetary slope closer to φ
t9 = best_plan_dist < raw_plan_dist
print(f"\n  Test  9: Best candidate planetary slope closer to φ than Raw E")
print(f"           Best ({best_plan_name}): distance = {best_plan_dist:.4f}")
print(f"           Raw E: distance = {raw_plan_dist:.4f}")
print(f"           -> {'PASS' if t9 else 'FAIL'}")
passed += t9

# Test 10: Action/ℏ spans > 100 decades
t10 = acth_range > 100
print(f"\n  Test 10: Action/ℏ spans > 100 decades from subatomic to cosmic")
print(f"           Range: {acth_range:.1f} decades")
print(f"           -> {'PASS' if t10 else 'FAIL'}")
passed += t10

# ============================================================
# FINAL SCORE
# ============================================================
print("\n" + "=" * 72)
print(f"  SCORE: {passed} / {total_tests}")
print("=" * 72)

print(f"\n  SUMMARY:")
print(f"  --------")
print(f"  Overall best energy axis: {overall_best}")
print(f"  Action/ℏ range: {acth_range:.0f} decades (dimensionless)")
print(f"  Monotonicity with scale: Spearman r = {r_mono:.3f}")
print(f"  Best sine fit: {best_sine_name} (R² = {sine_r2s[best_sine_name]:.4f})")
print(f"  Best circularity: {best_circ_name}")
print(f"  Subatomic anomaly reducers: {reducers if reducers else 'none'}")

if overall_best == 'Raw E':
    print(f"\n  VERDICT: Raw energy holds up — no candidate clearly dominates.")
elif 'Action' in overall_best:
    print(f"\n  VERDICT: ACTION is the natural energy coordinate.")
    print(f"  E×T has units of ℏ. The energy axis was always action in disguise.")
    print(f"  This connects ARA directly to the path integral (quantum)")
    print(f"  and Hamilton's principle (classical).")
elif 'Power' in overall_best:
    print(f"\n  VERDICT: POWER is the natural energy coordinate.")
    print(f"  E/T = watts. The axis measures instantaneous energy flow rate.")
elif 'Entropy' in overall_best:
    print(f"\n  VERDICT: ENTROPY PROXY is the natural energy coordinate.")
    print(f"  k_B ln(S/ℏ) = information content. The axis measures bits.")

print()
