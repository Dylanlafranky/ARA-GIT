#!/usr/bin/env python3
"""
Script 159: Reverse Random Analysis — Observe Through the Formula
===================================================================
Script 158 tried to PREDICT random numbers and failed.
Dylan's insight: don't predict — observe. Generate pairs,
look at what the formula sees in the actual data.

METHOD:
  1. Generate random number A₁
  2. Wait R seconds
  3. Generate random number A₂
  4. Compute the ACTUAL log ratio: Δlog_actual = log₁₀(A₂/A₁)
  5. Compute what the FORMULA expects: Δlog_formula = R·sin(A₁/R)
  6. Look at the difference, distribution, and structure

QUESTIONS:
  - Is there any correlation between time gap and the actual ratio?
  - Does the formula's expected shift match any statistical property?
  - Are there preferred values of Δlog that show up more than expected?
  - Does the residual (actual - formula) have structure?
  - What does the formula need to look like to match what we see?
"""

import numpy as np
import time
import secrets
import os

print("=" * 72)
print("SCRIPT 159: REVERSE RANDOM ANALYSIS")
print("         Observe random pairs through the ARA formula")
print("=" * 72)
print()

phi = (1 + np.sqrt(5)) / 2

# ================================================================
# GENERATE PAIRS
# ================================================================
def get_random(low=1, high=1000):
    return secrets.randbelow(high - low + 1) + low

# Time gaps to test
time_gaps = [0.1, 0.5, 1.0, phi, 2.0, np.pi]
N_TRIALS = 50
LOW, HIGH = 1, 1000

print(f"Generating {N_TRIALS} pairs at each of {len(time_gaps)} time gaps...")
print(f"Range: [{LOW}, {HIGH}]")
print()

all_data = {}

for gap in time_gaps:
    pairs = []
    for trial in range(N_TRIALS):
        A1 = get_random(LOW, HIGH)
        time.sleep(gap)
        A2 = get_random(LOW, HIGH)

        # Actual relationship
        if A1 > 0 and A2 > 0:
            delta_log_actual = np.log10(A2) - np.log10(A1)
        else:
            delta_log_actual = 0

        # What the formula expects
        delta_log_formula = gap * np.sin(A1 / gap)

        # Residual
        residual = delta_log_actual - delta_log_formula

        pairs.append({
            'A1': A1, 'A2': A2,
            'delta_actual': delta_log_actual,
            'delta_formula': delta_log_formula,
            'residual': residual,
            'ratio': A2 / A1,
        })

    all_data[gap] = pairs
    print(f"  R = {gap:.3f}s: done ({N_TRIALS} pairs)")

print()

# ================================================================
# ANALYSIS 1: What does the actual Δlog look like?
# ================================================================
print("=" * 72)
print("ANALYSIS 1: DISTRIBUTION OF ACTUAL Δlog = log₁₀(A₂/A₁)")
print("=" * 72)
print()
print("  If truly random and independent, Δlog should be symmetric")
print("  around 0 with no dependence on time gap R.")
print()

print(f"  {'R (s)':>8} {'Mean Δlog':>10} {'StdDev':>8} {'Median':>8} {'Skew':>8} {'Min':>8} {'Max':>8}")
print(f"  {'-'*8} {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

from scipy.stats import skew as calc_skew

for gap in time_gaps:
    deltas = [p['delta_actual'] for p in all_data[gap]]
    label = ""
    if abs(gap - phi) < 0.01: label = " ← φ"
    elif abs(gap - np.pi) < 0.01: label = " ← π"
    print(f"  {gap:>8.3f} {np.mean(deltas):>10.4f} {np.std(deltas):>8.4f} "
          f"{np.median(deltas):>8.4f} {calc_skew(deltas):>8.4f} "
          f"{min(deltas):>8.3f} {max(deltas):>8.3f}{label}")

# Combined across all gaps
all_deltas = []
for gap in time_gaps:
    all_deltas.extend([p['delta_actual'] for p in all_data[gap]])
print(f"  {'ALL':>8} {np.mean(all_deltas):>10.4f} {np.std(all_deltas):>8.4f} "
      f"{np.median(all_deltas):>8.4f} {calc_skew(all_deltas):>8.4f} "
      f"{min(all_deltas):>8.3f} {max(all_deltas):>8.3f}")

print()

# ================================================================
# ANALYSIS 2: What does the formula predict vs reality?
# ================================================================
print("=" * 72)
print("ANALYSIS 2: FORMULA EXPECTED vs ACTUAL")
print("=" * 72)
print()
print("  Formula says: Δlog = R·sin(A₁/R)")
print("  Reality gives: Δlog = log₁₀(A₂/A₁)")
print()

print(f"  {'R (s)':>8} {'Mean Formula':>13} {'Mean Actual':>12} {'Mean Resid':>11} {'Corr(F,A)':>10}")
print(f"  {'-'*8} {'-'*13} {'-'*12} {'-'*11} {'-'*10}")

for gap in time_gaps:
    formulas = [p['delta_formula'] for p in all_data[gap]]
    actuals = [p['delta_actual'] for p in all_data[gap]]
    residuals = [p['residual'] for p in all_data[gap]]

    # Correlation between formula prediction and actual result
    if np.std(formulas) > 0 and np.std(actuals) > 0:
        corr = np.corrcoef(formulas, actuals)[0, 1]
    else:
        corr = 0

    label = ""
    if abs(gap - phi) < 0.01: label = " ← φ"
    elif abs(gap - np.pi) < 0.01: label = " ← π"
    print(f"  {gap:>8.3f} {np.mean(formulas):>13.4f} {np.mean(actuals):>12.4f} "
          f"{np.mean(residuals):>11.4f} {corr:>10.4f}{label}")

print()
print("  Correlation > 0 means the formula's direction matches reality.")
print("  Correlation ≈ 0 means no relationship (expected for random).")
print("  Correlation < 0 means inverse relationship.")

# ================================================================
# ANALYSIS 3: Distribution of A₂/A₁ ratios — any structure?
# ================================================================
print()
print("=" * 72)
print("ANALYSIS 3: RATIO DISTRIBUTION — A₂/A₁")
print("=" * 72)
print()
print("  For uniform random [1,1000], the ratio A₂/A₁ should have")
print("  a specific distribution. Does time gap change it?")
print()

# Bin the ratios into meaningful ranges
ratio_bins = [(0, 0.1, 'A₂ << A₁  (< 0.1×)'),
              (0.1, 0.5, 'A₂ < A₁   (0.1-0.5×)'),
              (0.5, 1.0, 'A₂ ≈ A₁⁻  (0.5-1.0×)'),
              (1.0, 2.0, 'A₂ ≈ A₁⁺  (1.0-2.0×)'),
              (2.0, 10,  'A₂ > A₁   (2-10×)'),
              (10, 1001, 'A₂ >> A₁  (> 10×)')]

header = f"  {'R (s)':>8}"
for lo, hi, name in ratio_bins:
    header += f" {name[:10]:>11}"
print(header)
print(f"  {'-'*8}" + f" {'-'*11}" * len(ratio_bins))

for gap in time_gaps:
    ratios = [p['ratio'] for p in all_data[gap]]
    line = f"  {gap:>8.3f}"
    for lo, hi, name in ratio_bins:
        count = sum(1 for r in ratios if lo <= r < hi)
        line += f" {count:>8}/{N_TRIALS:>2}"
    label = ""
    if abs(gap - phi) < 0.01: label = " ← φ"
    elif abs(gap - np.pi) < 0.01: label = " ← π"
    print(line + label)

# ================================================================
# ANALYSIS 4: Does the RESIDUAL have structure?
# ================================================================
print()
print("=" * 72)
print("ANALYSIS 4: RESIDUAL STRUCTURE")
print("=" * 72)
print()
print("  Residual = Actual Δlog - Formula Δlog")
print("  If residuals cluster or correlate with A₁, there's hidden structure.")
print()

# Check if residual correlates with A1
print(f"  {'R (s)':>8} {'Corr(Resid,A1)':>15} {'Corr(Resid,A2)':>15} {'Resid StdDev':>13}")
print(f"  {'-'*8} {'-'*15} {'-'*15} {'-'*13}")

for gap in time_gaps:
    a1s = [p['A1'] for p in all_data[gap]]
    a2s = [p['A2'] for p in all_data[gap]]
    residuals = [p['residual'] for p in all_data[gap]]

    corr_a1 = np.corrcoef(a1s, residuals)[0, 1] if np.std(residuals) > 0 else 0
    corr_a2 = np.corrcoef(a2s, residuals)[0, 1] if np.std(residuals) > 0 else 0

    label = ""
    if abs(gap - phi) < 0.01: label = " ← φ"
    elif abs(gap - np.pi) < 0.01: label = " ← π"
    print(f"  {gap:>8.3f} {corr_a1:>15.4f} {corr_a2:>15.4f} {np.std(residuals):>13.4f}{label}")

# ================================================================
# ANALYSIS 5: What WOULD the correct formula look like?
# ================================================================
print()
print("=" * 72)
print("ANALYSIS 5: REVERSE ENGINEERING — WHAT R WOULD MAKE IT WORK?")
print("=" * 72)
print()
print("  For each pair, solve: what R makes R·sin(A₁/R) = Δlog_actual?")
print("  If a consistent R emerges, that's the correct coupler.")
print()

from scipy.optimize import brentq

def find_R(A1, delta_actual):
    """Find R such that R·sin(A1/R) = delta_actual, if possible."""
    def f(R):
        return R * np.sin(A1 / R) - delta_actual

    # Search across a range of R values
    best_R = None
    best_err = float('inf')

    for R_try in np.linspace(0.01, 100, 5000):
        err = abs(f(R_try))
        if err < best_err:
            best_err = err
            best_R = R_try

    return best_R, best_err

# Sample a subset (this is slow)
print("  Sampling 20 pairs per gap to find optimal R...")
print()
print(f"  {'R_time(s)':>10} {'A1':>6} {'A2':>6} {'Δlog':>8} {'R_optimal':>10} {'Fit err':>8}")
print(f"  {'-'*10} {'-'*6} {'-'*6} {'-'*8} {'-'*10} {'-'*8}")

optimal_Rs = {gap: [] for gap in time_gaps}

for gap in time_gaps:
    pairs = all_data[gap][:20]  # first 20
    for p in pairs:
        if abs(p['delta_actual']) > 0.01:  # skip near-zero deltas
            R_opt, fit_err = find_R(p['A1'], p['delta_actual'])
            optimal_Rs[gap].append(R_opt)
            # Only print a few
            if len(optimal_Rs[gap]) <= 3:
                print(f"  {gap:>10.3f} {p['A1']:>6d} {p['A2']:>6d} {p['delta_actual']:>8.4f} "
                      f"{R_opt:>10.3f} {fit_err:>8.4f}")

print(f"  ... (showing 3 per gap)")
print()

# Summary of optimal R values
print(f"  {'R_time(s)':>10} {'Mean R_opt':>11} {'StdDev':>8} {'Median':>8} {'Near φ?':>8} {'Near π?':>8}")
print(f"  {'-'*10} {'-'*11} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
for gap in time_gaps:
    if optimal_Rs[gap]:
        rs = optimal_Rs[gap]
        near_phi = sum(1 for r in rs if abs(r - phi) < 0.3)
        near_pi = sum(1 for r in rs if abs(r - np.pi) < 0.3)
        label = ""
        if abs(gap - phi) < 0.01: label = " ← φ"
        elif abs(gap - np.pi) < 0.01: label = " ← π"
        print(f"  {gap:>10.3f} {np.mean(rs):>11.3f} {np.std(rs):>8.3f} "
              f"{np.median(rs):>8.3f} {near_phi:>5}/{len(rs)} {near_pi:>5}/{len(rs)}{label}")

# ================================================================
# ANALYSIS 6: Does Δlog cluster near special values?
# ================================================================
print()
print("=" * 72)
print("ANALYSIS 6: DO Δlog VALUES CLUSTER NEAR SPECIAL NUMBERS?")
print("=" * 72)
print()

special_values = [
    (0, '0'),
    (np.log10(phi), 'log₁₀(φ) = 0.209'),
    (np.log10(np.pi), 'log₁₀(π) = 0.497'),
    (np.log10(np.e), 'log₁₀(e) = 0.434'),
    (1.0, '1.0 (one decade)'),
    (-np.log10(phi), '-log₁₀(φ) = -0.209'),
    (-np.log10(np.pi), '-log₁₀(π) = -0.497'),
    (-1.0, '-1.0'),
]

# For each special value, count how many Δlog_actual fall within ±0.05
tolerance = 0.05
print(f"  Counts of Δlog_actual within ±{tolerance} of special values:")
print(f"  Total pairs: {len(all_deltas)}")
print()
for sv, name in special_values:
    count = sum(1 for d in all_deltas if abs(d - sv) < tolerance)
    # Expected count for uniform distribution of Δlog
    # Δlog ranges from about -3 to +3, so bin width 0.1 out of range 6
    expected = len(all_deltas) * (2 * tolerance) / 6.0
    ratio = count / expected if expected > 0 else 0
    marker = " ← excess" if ratio > 1.5 else ""
    print(f"  {name:<25} count={count:>4}  expected≈{expected:>5.1f}  ratio={ratio:>5.2f}{marker}")

# ================================================================
# SCORING
# ================================================================
print()
print("=" * 72)
print("WHAT DID WE LEARN?")
print("=" * 72)
print()

# Check for any signal
all_formulas = []
all_actuals_flat = []
for gap in time_gaps:
    all_formulas.extend([p['delta_formula'] for p in all_data[gap]])
    all_actuals_flat.extend([p['delta_actual'] for p in all_data[gap]])

overall_corr = np.corrcoef(all_formulas, all_actuals_flat)[0, 1]

print(f"  Overall correlation (formula vs actual): {overall_corr:.4f}")
print()

if abs(overall_corr) > 0.1:
    print("  There IS correlation between the formula and reality.")
    print("  The formula is seeing something, even if the mapping is off.")
elif abs(overall_corr) > 0.05:
    print("  Weak correlation. Possibly noise, possibly faint signal.")
else:
    print("  No correlation. The formula and reality are independent here.")
    print()
    print("  This could mean:")
    print("    1. Random numbers are genuinely uncoupled — no mechanism")
    print("    2. Time couples to information differently than R·sin(A/R)")
    print("    3. The ARA coupling needs a physical substrate to work")
    print("    4. We're looking at the right thing the wrong way")

print()
print("  Script 158 said: formula can't predict.")
print("  Script 159 asks: what does the data look like through the formula?")
print("  If the residuals or optimal R values cluster, there's a thread to pull.")
print()
