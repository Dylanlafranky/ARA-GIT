#!/usr/bin/env python3
"""
Script 160: φ-Clustering Test Across Ranges and Sources
=========================================================
Script 159 found that Δlog = log₁₀(A₂/A₁) between random
pairs clusters near ±log₁₀(φ) at 4.8× expected rate.

QUESTION: Is this real or an artefact?
  - If it changes with number range → geometric artefact
  - If it persists across ranges → structural
  - If it's source-dependent → generator artefact
  - If it's source-independent → something deeper

TEST:
  3 random sources × 6 number ranges × 5000 pairs each
  No time gaps — just pairs, no waiting.
  Pure question: does the RATIO of two random numbers
  from the same distribution prefer φ?
"""

import numpy as np
import secrets
import os
import struct

print("=" * 72)
print("SCRIPT 160: φ-CLUSTERING TEST")
print("         Does Δlog cluster near log₁₀(φ) across sources and ranges?")
print("=" * 72)
print()

phi = (1 + np.sqrt(5)) / 2
LOG_PHI = np.log10(phi)   # 0.20898
LOG_PI  = np.log10(np.pi)  # 0.49715
LOG_E   = np.log10(np.e)   # 0.43429
LOG_2   = np.log10(2)      # 0.30103
LOG_3   = np.log10(3)      # 0.47712
LOG_SQRT2 = np.log10(np.sqrt(2))  # 0.15051

print(f"  Reference values:")
print(f"    log₁₀(φ)   = {LOG_PHI:.5f}")
print(f"    log₁₀(√2)  = {LOG_SQRT2:.5f}")
print(f"    log₁₀(2)   = {LOG_2:.5f}")
print(f"    log₁₀(e)   = {LOG_E:.5f}")
print(f"    log₁₀(3)   = {LOG_3:.5f}")
print(f"    log₁₀(π)   = {LOG_PI:.5f}")
print()

# ================================================================
# RANDOM SOURCES
# ================================================================
def source_secrets(low, high):
    """OS hardware entropy via secrets module."""
    return secrets.randbelow(high - low + 1) + low

def source_urandom(low, high):
    """Kernel entropy pool via os.urandom."""
    raw = os.urandom(4)
    val = struct.unpack('I', raw)[0]
    return (val % (high - low + 1)) + low

def source_numpy(low, high):
    """NumPy's Mersenne Twister PRNG (pseudo-random)."""
    return np.random.randint(low, high + 1)

sources = [
    ('secrets',  source_secrets),
    ('urandom',  source_urandom),
    ('numpy_MT', source_numpy),
]

# ================================================================
# NUMBER RANGES
# ================================================================
ranges = [
    (1, 10),
    (1, 100),
    (1, 1000),
    (1, 10000),
    (1, 100000),
    (1, 1000000),
]

N_PAIRS = 5000
TOLERANCE = 0.05  # ±0.05 window around each special value

# Special values to check (positive only — we'll check negative too)
special_values = [
    (LOG_SQRT2, 'log₁₀(√2)'),
    (LOG_PHI,   'log₁₀(φ)'),
    (LOG_2,     'log₁₀(2)'),
    (LOG_E,     'log₁₀(e)'),
    (LOG_3,     'log₁₀(3)'),
    (LOG_PI,    'log₁₀(π)'),
    (0.5,       '0.5'),
]

# ================================================================
# THEORETICAL BASELINE
# ================================================================
print("=" * 72)
print("FIRST: WHAT DOES THEORY SAY?")
print("=" * 72)
print()
print("  For A,B uniform on [1, N], the density of Δlog = log₁₀(B/A) is")
print("  NOT uniform — it peaks at 0 and falls off toward ±log₁₀(N).")
print("  We need to compute the expected density at each special value")
print("  to know if any excess is real.")
print()
print("  We'll compute this empirically by comparing against a FLAT")
print("  baseline within each source×range combination.")
print()

# ================================================================
# RUN THE EXPERIMENT
# ================================================================
print("=" * 72)
print("GENERATING PAIRS")
print("=" * 72)
print()

all_results = {}

for src_name, src_func in sources:
    for low, high in ranges:
        key = f"{src_name}_{low}-{high}"
        deltas = []

        for _ in range(N_PAIRS):
            a1 = src_func(low, high)
            a2 = src_func(low, high)
            if a1 > 0 and a2 > 0:
                deltas.append(np.log10(a2) - np.log10(a1))

        all_results[key] = {
            'source': src_name,
            'range': (low, high),
            'deltas': np.array(deltas),
        }

        print(f"  {key}: {len(deltas)} pairs, "
              f"mean={np.mean(deltas):.4f}, std={np.std(deltas):.4f}")

print()

# ================================================================
# ANALYSIS: Density at special values vs local baseline
# ================================================================
print("=" * 72)
print("DENSITY AT SPECIAL VALUES (ratio to local baseline)")
print("=" * 72)
print()
print("  Method: count pairs within ±0.05 of each special value,")
print("  then divide by count in adjacent control windows")
print("  (±0.05 around value+0.15 and value-0.15).")
print("  Ratio > 1 means excess. Ratio ≈ 1 means just the background shape.")
print()

# For each source × range, compute density ratios
def density_ratio(deltas, center, tol=0.05, offset=0.15):
    """Count near center, compare to nearby control windows."""
    count_target = np.sum(np.abs(deltas - center) < tol)
    count_target += np.sum(np.abs(deltas + center) < tol)  # include ±

    # Control windows
    c1 = np.sum(np.abs(deltas - (center + offset)) < tol)
    c1 += np.sum(np.abs(deltas + (center + offset)) < tol)
    c2 = np.sum(np.abs(deltas - (center - offset)) < tol)
    c2 += np.sum(np.abs(deltas + (center - offset)) < tol)

    control = (c1 + c2) / 2 if (c1 + c2) > 0 else 1
    return count_target, control, count_target / control if control > 0 else 0

# Print header
header = f"  {'Source':>10} {'Range':>12}"
for sv, name in special_values:
    header += f" {name:>10}"
print(header)
print(f"  {'-'*10} {'-'*12}" + f" {'-'*10}" * len(special_values))

# Store all density ratios for summary
density_data = {name: [] for _, name in special_values}

for src_name, _ in sources:
    for low, high in ranges:
        key = f"{src_name}_{low}-{high}"
        deltas = all_results[key]['deltas']

        line = f"  {src_name:>10} {f'[{low},{high}]':>12}"
        for sv, name in special_values:
            count, control, ratio = density_ratio(deltas, sv)
            line += f" {ratio:>10.2f}"
            density_data[name].append(ratio)
        print(line)
    print()  # blank line between sources

# ================================================================
# SUMMARY: Average density ratio per special value
# ================================================================
print()
print("=" * 72)
print("SUMMARY: AVERAGE DENSITY RATIO ACROSS ALL SOURCE × RANGE")
print("=" * 72)
print()
print("  Ratio > 1.0 means this value appears MORE than its neighbours.")
print("  Ratio = 1.0 means it's just the background distribution shape.")
print("  Consistent ratio > 1.0 across all conditions = real clustering.")
print()

print(f"  {'Value':>12} {'Mean Ratio':>11} {'StdDev':>8} {'Min':>6} {'Max':>6} {'Always>1?':>10}")
print(f"  {'-'*12} {'-'*11} {'-'*8} {'-'*6} {'-'*6} {'-'*10}")

for sv, name in special_values:
    ratios = density_data[name]
    mean_r = np.mean(ratios)
    std_r = np.std(ratios)
    min_r = min(ratios)
    max_r = max(ratios)
    always = "YES" if all(r > 1.0 for r in ratios) else f"{sum(1 for r in ratios if r > 1.0)}/{len(ratios)}"
    marker = " ← SIGNAL" if mean_r > 1.15 and all(r > 0.9 for r in ratios) else ""
    print(f"  {name:>12} {mean_r:>11.3f} {std_r:>8.3f} {min_r:>6.2f} {max_r:>6.2f} {always:>10}{marker}")

# ================================================================
# DEEP DIVE: Histogram of Δlog for the widest range
# ================================================================
print()
print("=" * 72)
print("HISTOGRAM: Δlog FOR [1, 1000000] (secrets)")
print("=" * 72)
print()

key = "secrets_1-1000000"
deltas = all_results[key]['deltas']

# Fine histogram
bins = np.linspace(-6, 6, 241)  # 0.05 width bins
counts, edges = np.histogram(np.abs(deltas), bins=np.linspace(0, 6, 121))
centres = (edges[:-1] + edges[1:]) / 2

# Find local peaks
print("  Local density peaks in |Δlog| (above smoothed trend):")
print()

# Smooth the counts
from scipy.ndimage import uniform_filter1d
smoothed = uniform_filter1d(counts.astype(float), size=5)

for i in range(2, len(counts) - 2):
    if counts[i] > smoothed[i] * 1.2 and counts[i] > 20:
        c = centres[i]
        # Identify what's near
        nearest = ""
        for sv, name in special_values:
            if abs(c - sv) < 0.03:
                nearest = f" ← {name}"
                break
        if not nearest and abs(c) < 0.03:
            nearest = " ← 0"
        if counts[i] > smoothed[i] * 1.3:
            print(f"    |Δlog| = {c:.3f}  count = {counts[i]:>4}  "
                  f"(vs smooth {smoothed[i]:.0f}, ratio {counts[i]/smoothed[i]:.2f}){nearest}")

# ================================================================
# CONTROL TEST: Does this hold for CONTINUOUS uniform?
# ================================================================
print()
print("=" * 72)
print("CONTROL: CONTINUOUS UNIFORM [0, 1] — NO INTEGER EFFECTS")
print("=" * 72)
print()
print("  If φ-clustering is an integer artefact, it should vanish")
print("  for continuous random numbers.")
print()

continuous_deltas = []
for _ in range(50000):
    a = np.random.uniform(0.001, 1.0)
    b = np.random.uniform(0.001, 1.0)
    continuous_deltas.append(np.log10(b) - np.log10(a))
continuous_deltas = np.array(continuous_deltas)

print(f"  {'Value':>12} {'Count(±.05)':>12} {'Control':>8} {'Ratio':>7}")
print(f"  {'-'*12} {'-'*12} {'-'*8} {'-'*7}")

for sv, name in special_values:
    count, control, ratio = density_ratio(continuous_deltas, sv)
    marker = " ← excess" if ratio > 1.15 else ""
    print(f"  {name:>12} {count:>12} {control:>8.0f} {ratio:>7.2f}{marker}")

# ================================================================
# SCORING
# ================================================================
print()
print("=" * 72)
print("VERDICT")
print("=" * 72)
print()

# Count how many special values show consistent signal
signals = []
for sv, name in special_values:
    ratios = density_data[name]
    if np.mean(ratios) > 1.1 and sum(1 for r in ratios if r > 1.0) >= len(ratios) * 0.7:
        signals.append(name)

if signals:
    print(f"  Consistent clustering found at: {', '.join(signals)}")
    print()
    if 'log₁₀(φ)' in signals:
        print("  φ-CLUSTERING IS REAL and source-independent.")
        print("  This is a property of the ratio distribution itself,")
        print("  not of any particular random generator.")
        print()
        print("  But we still need to determine if this is:")
        print("    a) A mathematical property of log-ratios of uniform integers")
        print("    b) Something deeper about how numbers relate to φ")
    else:
        print("  Clustering found but NOT at φ.")
else:
    print("  No consistent clustering at any special value.")
    print("  The Script 159 result was likely noise or a range artefact.")
    print()
    print("  This is an honest null result: random numbers don't")
    print("  preferentially cluster near φ in their ratios.")

print()
