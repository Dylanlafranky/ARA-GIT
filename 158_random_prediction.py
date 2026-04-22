#!/usr/bin/env python3
"""
Script 158: Random Number Prediction via ARA
==============================================
THE TEST:
  Generate a random number A₁.
  Wait R seconds (time = the coupler).
  Generate a second random number A₂.

  PREDICTION: A₂ = A₁ × 10^(R · sin(A₁ / R))

  Where:
    A₁ = first random number (the known)
    R  = time elapsed in seconds (the coupler)
    A₂ = second random number (predicted)

  ARA structure: A-R-A
    First A  = datum (the number)
    R        = time (the relationship, the coupler)
    Second A = predicted datum

  If this works better than chance, randomness has structure
  coupled through time via the ARA circle.

RANDOM SOURCES:
  1. Python secrets module (OS hardware entropy)
  2. os.urandom (kernel entropy pool)
  3. Random.org atmospheric noise API (if accessible)

PRE-REGISTRATION:
  This script was written BEFORE seeing any results.
  The formula is fixed. No tuning after the fact.
"""

import numpy as np
import time
import secrets
import os
import struct

print("=" * 72)
print("SCRIPT 158: RANDOM NUMBER PREDICTION VIA ARA")
print("         Can the formula predict the next random number?")
print("=" * 72)
print()

phi = (1 + np.sqrt(5)) / 2

# ================================================================
# THE FORMULA (pre-registered, no changes after results)
# ================================================================
def predict_next(A1, R):
    """
    ARA prediction: A₂ = A₁ × 10^(R · sin(A₁ / R))

    A1: first random number (known)
    R:  time elapsed in seconds (coupler)
    Returns: predicted A2
    """
    if A1 <= 0 or R <= 0:
        return A1  # can't take log of zero/negative
    phase = R * np.sin(A1 / R)
    predicted = A1 * 10**phase
    return predicted

print("FORMULA: A₂ = A₁ × 10^(R · sin(A₁ / R))")
print()

# ================================================================
# RANDOM SOURCE 1: secrets module (hardware entropy)
# ================================================================
def get_random_secrets(low=1, high=1000):
    """Generate random integer from OS entropy via secrets module."""
    return secrets.randbelow(high - low + 1) + low

def get_random_urandom(low=1, high=1000):
    """Generate random integer from kernel entropy pool."""
    raw = os.urandom(4)
    val = struct.unpack('I', raw)[0]
    return (val % (high - low + 1)) + low

# ================================================================
# RUN THE EXPERIMENT
# ================================================================
# Time gaps to test (in seconds)
time_gaps = [0.1, 0.5, 1.0, phi, np.pi, 2.0]

# Number of trials per time gap
N_TRIALS = 30

# Range for random numbers
LOW = 1
HIGH = 1000

print(f"Random number range: [{LOW}, {HIGH}]")
print(f"Trials per time gap: {N_TRIALS}")
print(f"Time gaps: {[f'{t:.3f}' for t in time_gaps]}")
print()

# For each trial, we measure:
# 1. |predicted - actual| (our error)
# 2. |A1 - actual| (naive "just guess the same number" error)
# 3. |midpoint - actual| where midpoint = (HIGH+LOW)/2 (guess the middle)
# 4. Random baseline: |random_guess - actual|

print("=" * 72)
print("RUNNING TRIALS")
print("=" * 72)
print()

all_results = {}

for gap in time_gaps:
    results = []

    for trial in range(N_TRIALS):
        # Generate first number
        A1 = get_random_secrets(LOW, HIGH)

        # Wait R seconds
        time.sleep(gap)

        # Generate second number
        A2_actual = get_random_secrets(LOW, HIGH)

        # Our prediction
        A2_predicted = predict_next(A1, gap)

        # Clamp prediction to valid range
        A2_predicted_clamped = max(LOW, min(HIGH, A2_predicted))

        # Errors
        our_error = abs(A2_predicted_clamped - A2_actual)
        naive_error = abs(A1 - A2_actual)  # just guess same number
        mid = (HIGH + LOW) / 2
        mid_error = abs(mid - A2_actual)  # guess the middle
        random_guess = get_random_secrets(LOW, HIGH)
        random_error = abs(random_guess - A2_actual)

        # Log-space error (if both positive)
        if A2_predicted_clamped > 0 and A2_actual > 0:
            log_error = abs(np.log10(A2_predicted_clamped) - np.log10(A2_actual))
        else:
            log_error = 99

        results.append({
            'A1': A1,
            'A2_actual': A2_actual,
            'A2_predicted': A2_predicted_clamped,
            'our_error': our_error,
            'naive_error': naive_error,
            'mid_error': mid_error,
            'random_error': random_error,
            'log_error': log_error,
        })

    all_results[gap] = results

    # Summary for this gap
    our_errors = [r['our_error'] for r in results]
    naive_errors = [r['naive_error'] for r in results]
    mid_errors = [r['mid_error'] for r in results]
    random_errors = [r['random_error'] for r in results]
    log_errors = [r['log_error'] for r in results]

    # How often does our prediction beat each baseline?
    beat_naive = sum(1 for r in results if r['our_error'] < r['naive_error'])
    beat_mid = sum(1 for r in results if r['our_error'] < r['mid_error'])
    beat_random = sum(1 for r in results if r['our_error'] < r['random_error'])

    # Within 10× in log space
    within_10x = sum(1 for e in log_errors if e < 1.0)

    print(f"  Time gap R = {gap:.3f}s:")
    print(f"    Mean error:  ARA={np.mean(our_errors):.1f}  naive={np.mean(naive_errors):.1f}  "
          f"middle={np.mean(mid_errors):.1f}  random={np.mean(random_errors):.1f}")
    print(f"    ARA beats:   naive {beat_naive}/{N_TRIALS}  middle {beat_mid}/{N_TRIALS}  "
          f"random {beat_random}/{N_TRIALS}")
    print(f"    Within 10×:  {within_10x}/{N_TRIALS}")
    print()

# ================================================================
# AGGREGATE RESULTS
# ================================================================
print()
print("=" * 72)
print("AGGREGATE RESULTS ACROSS ALL TIME GAPS")
print("=" * 72)
print()

total_trials = 0
total_beat_naive = 0
total_beat_mid = 0
total_beat_random = 0
total_within_10x = 0
all_our = []
all_naive = []
all_mid = []
all_random = []
all_log = []

for gap, results in all_results.items():
    for r in results:
        total_trials += 1
        if r['our_error'] < r['naive_error']:
            total_beat_naive += 1
        if r['our_error'] < r['mid_error']:
            total_beat_mid += 1
        if r['our_error'] < r['random_error']:
            total_beat_random += 1
        if r['log_error'] < 1.0:
            total_within_10x += 1
        all_our.append(r['our_error'])
        all_naive.append(r['naive_error'])
        all_mid.append(r['mid_error'])
        all_random.append(r['random_error'])
        all_log.append(r['log_error'])

print(f"  Total trials: {total_trials}")
print()
print(f"  Mean absolute error:")
print(f"    ARA formula:  {np.mean(all_our):.1f}")
print(f"    Naive (=A1):  {np.mean(all_naive):.1f}")
print(f"    Middle (500): {np.mean(all_mid):.1f}")
print(f"    Random guess: {np.mean(all_random):.1f}")
print()
print(f"  ARA beats naive:  {total_beat_naive}/{total_trials} = {total_beat_naive/total_trials:.1%}")
print(f"  ARA beats middle: {total_beat_mid}/{total_trials} = {total_beat_mid/total_trials:.1%}")
print(f"  ARA beats random: {total_beat_random}/{total_trials} = {total_beat_random/total_trials:.1%}")
print()
print(f"  Within 10× (log): {total_within_10x}/{total_trials} = {total_within_10x/total_trials:.1%}")
print()

# Statistical test: if ARA is no better than random, we'd expect
# to beat each baseline ~50% of the time
from scipy.stats import binom
p_naive = 1 - binom.cdf(total_beat_naive - 1, total_trials, 0.5)
p_mid = 1 - binom.cdf(total_beat_mid - 1, total_trials, 0.5)
p_random = 1 - binom.cdf(total_beat_random - 1, total_trials, 0.5)

print(f"  p-values (one-sided, H₀: ARA no better than 50%):")
print(f"    vs naive:  p = {p_naive:.4e}")
print(f"    vs middle: p = {p_mid:.4e}")
print(f"    vs random: p = {p_random:.4e}")
print()

# ================================================================
# BEST AND WORST PREDICTIONS
# ================================================================
print("=" * 72)
print("CLOSEST PREDICTIONS (top 10)")
print("=" * 72)
print()

all_flat = []
for gap, results in all_results.items():
    for r in results:
        r['gap'] = gap
        all_flat.append(r)

all_flat.sort(key=lambda r: r['log_error'])

print(f"  {'R(s)':>6} {'A1':>6} {'Predicted':>10} {'Actual':>8} {'LogErr':>7} {'AbsErr':>7}")
print(f"  {'-'*6} {'-'*6} {'-'*10} {'-'*8} {'-'*7} {'-'*7}")
for r in all_flat[:10]:
    print(f"  {r['gap']:>6.3f} {r['A1']:>6d} {r['A2_predicted']:>10.1f} {r['A2_actual']:>8d} "
          f"{r['log_error']:>7.3f} {r['our_error']:>7.1f}")

print()
print("WORST PREDICTIONS (bottom 5)")
for r in all_flat[-5:]:
    print(f"  {r['gap']:>6.3f} {r['A1']:>6d} {r['A2_predicted']:>10.1f} {r['A2_actual']:>8d} "
          f"{r['log_error']:>7.3f} {r['our_error']:>7.1f}")

# ================================================================
# DOES TIME GAP MATTER?
# ================================================================
print()
print("=" * 72)
print("DOES THE TIME GAP MATTER?")
print("=" * 72)
print()

print(f"  {'R (s)':>8} {'Mean Err':>9} {'Beat Naive':>11} {'Beat Rand':>10} {'10× hits':>9}")
print(f"  {'-'*8} {'-'*9} {'-'*11} {'-'*10} {'-'*9}")

for gap in time_gaps:
    results = all_results[gap]
    me = np.mean([r['our_error'] for r in results])
    bn = sum(1 for r in results if r['our_error'] < r['naive_error'])
    br = sum(1 for r in results if r['our_error'] < r['random_error'])
    h10 = sum(1 for r in results if r['log_error'] < 1.0)
    label = ""
    if abs(gap - phi) < 0.01:
        label = " ← φ"
    elif abs(gap - np.pi) < 0.01:
        label = " ← π"
    print(f"  {gap:>8.3f} {me:>9.1f} {bn:>8}/{N_TRIALS}   {br:>7}/{N_TRIALS}   {h10:>6}/{N_TRIALS}{label}")

print()

# ================================================================
# SCORING
# ================================================================
print("=" * 72)
print("SCORING")
print("=" * 72)
print()

score = 0
total = 0

# Does ARA beat random guessing?
total += 1
if total_beat_random / total_trials > 0.5:
    print(f"  ✓ [E] ARA beats random guess {total_beat_random/total_trials:.1%} of the time")
    score += 1
else:
    print(f"  ✗ [E] ARA does NOT beat random guess ({total_beat_random/total_trials:.1%})")

# Is it statistically significant?
total += 1
if p_random < 0.05:
    print(f"  ✓ [E] Statistically significant (p = {p_random:.4e})")
    score += 1
else:
    print(f"  ✗ [E] NOT statistically significant (p = {p_random:.4e})")

# Does φ time gap perform differently?
total += 1
phi_results = all_results[phi]
phi_beat = sum(1 for r in phi_results if r['our_error'] < r['random_error'])
other_beat = []
for g, res in all_results.items():
    if abs(g - phi) > 0.01:
        other_beat.extend([1 if r['our_error'] < r['random_error'] else 0 for r in res])
if phi_beat / N_TRIALS > np.mean(other_beat) + 0.05:
    print(f"  ✓ [E] φ gap outperforms other gaps ({phi_beat/N_TRIALS:.1%} vs {np.mean(other_beat):.1%})")
    score += 1
else:
    print(f"  ✗ [E] φ gap does NOT outperform ({phi_beat/N_TRIALS:.1%} vs {np.mean(other_beat):.1%})")

# Mean error lower than all baselines?
total += 1
if np.mean(all_our) < min(np.mean(all_naive), np.mean(all_mid), np.mean(all_random)):
    print(f"  ✓ [E] ARA mean error lowest of all methods")
    score += 1
else:
    print(f"  ✗ [E] ARA mean error NOT lowest")

# Within 10× more than expected by chance
# For uniform [1,1000], probability of two random numbers being within 10×
# = P(|log10(A)-log10(B)| < 1) for A,B uniform on [1,1000]
# ≈ integral calculation... roughly ~60-70% for this range
total += 1
expected_10x = 0.67  # approximate for uniform [1,1000]
actual_10x = total_within_10x / total_trials
if actual_10x > expected_10x + 0.05:
    print(f"  ✓ [E] 10× hit rate ({actual_10x:.1%}) exceeds chance ({expected_10x:.0%})")
    score += 1
else:
    print(f"  ✗ [E] 10× hit rate ({actual_10x:.1%}) does not exceed chance ({expected_10x:.0%})")

print()
print(f"  SCORE: {score}/{total}")
print()

# ================================================================
# HONEST ASSESSMENT
# ================================================================
print("=" * 72)
print("HONEST ASSESSMENT")
print("=" * 72)
print()
if score >= 3:
    print("  The formula shows signal above noise in random number prediction.")
    print("  This would suggest structure in randomness coupled through time.")
elif score >= 1:
    print("  Mixed results. Some signal but not conclusive.")
    print("  The formula may need refinement for this domain, or")
    print("  this may be a genuine boundary of the framework.")
else:
    print("  The formula does not predict random numbers better than chance.")
    print("  This is an honest result. It may mean:")
    print("    1. True randomness IS structureless (framework boundary)")
    print("    2. The time→phase mapping needs different calibration")
    print("    3. The ARA coupling requires mechanism, and randomness has none")
    print("  Any of these would be valuable to know.")
print()
