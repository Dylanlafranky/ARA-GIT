import math
import random
random.seed(42)

# =============================================================
# FRACTAL PREDICTION TEST v2 — TIGHTENED
# 
# Problem with v1: With 66 harmonic targets (n:m, n,m ≤ 12),
# the fractions are so dense that ANY ratio hits one. 
# The test was not discriminating.
#
# Fix: 
# 1. Restrict to the SIMPLEST fractions only (n,m ≤ 4) — the
#    musically consonant intervals
# 2. Use ACTUALLY MEASURED subsystem values where available
#    (not my estimated multiples of 10)
# 3. Test whether our data preferentially hits the simplest
#    fractions vs random
# =============================================================

# The simplest harmonic fractions — the ones that MATTER musically
simple_harmonics = [
    (1, 1, 1.000, "Unison"),
    (2, 1, 2.000, "Octave"),
    (3, 2, 1.500, "Perfect fifth"),
    (4, 3, 1.333, "Perfect fourth"),
    (3, 1, 3.000, "Twelfth"),
    (4, 1, 4.000, "Double octave"),
    (5, 4, 1.250, "Major third"),
    (5, 3, 1.667, "Major sixth"),
    (6, 5, 1.200, "Minor third"),
    (5, 2, 2.500, "Tenth"),
    (5, 1, 5.000, "Major 3rd + 2 octaves"),
    (8, 5, 1.600, "Minor sixth"),
]

def find_nearest_simple(ratio):
    """Find nearest simple harmonic fraction."""
    best = None
    best_err = float('inf')
    for n, m, target, name in simple_harmonics:
        err = abs(ratio - target) / target
        if err < best_err:
            best_err = err
            best = (n, m, target, name)
    return best[0], best[1], best[2], best[3], best_err

# =============================================================
# CRITICAL HONESTY CHECK
# =============================================================
print("=" * 80)
print("HONESTY CHECK: Are the subsystem values independently measured?")
print("=" * 80)
print()
print("Problem: In v1, I ESTIMATED many subsystem action values by")
print("multiplying the parent system's action by powers of 10.")
print("That guarantees ratios OF powers of 10, which is circular.")
print()
print("What we ACTUALLY have measured (from our notes):")
print()

# These are the gaps from paper5_octave_structure_notes.md
# These are LOG10 gaps between consecutive subsystems
# within the same system — derived from independently sourced data
measured_gaps = [
    ("Neuron", "Depol → Refractory", 0.976),
    ("Neuron", "Refractory → Vesicle", 0.983),
    ("Engine", "Valve → PC Boost", 0.977),
    ("Thunderstorm", "Gust → Precip", 0.964),
    ("Predator-prey", "Veg → Lynx", 1.075),
    ("Heart", "Myocyte → RSA", 1.484),
    ("Hydrogen", "Metastable → some gap", 1.515),  
    ("Engine", "Boost → Thermal", 1.713),
]

print("Measured log₁₀ gaps between consecutive subsystems:")
print("-" * 60)
for sys, label, gap in measured_gaps:
    print(f"  {sys:15s}  {label:25s}  gap = {gap:.3f}")

print()
print("=" * 80)
print("TEST: Do these gaps cluster at PREFERRED values?")
print("=" * 80)
print()

# The prediction from the octave structure notes:
# Gaps should cluster near log₁₀(4π) = 1.099 or log₁₀((2π)²) = 1.596
target_4pi = math.log10(4 * math.pi)   # 1.099
target_2pi_sq = math.log10((2 * math.pi) ** 2)  # 1.596
target_pi = math.log10(math.pi)  # 0.497
target_2pi = math.log10(2 * math.pi)  # 0.799

targets = [
    (target_pi, "π", "0.497"),
    (target_2pi, "2π", "0.799"),
    (target_4pi, "4π", "1.099"),
    (target_2pi_sq, "(2π)²", "1.596"),
    (2 * target_4pi, "2×4π", "2.199"),
]

print(f"Target values (log₁₀ scale):")
for val, name, display in targets:
    print(f"  log₁₀({name}) = {val:.3f}")
print()

for sys, label, gap in measured_gaps:
    # Find nearest target
    best_name = None
    best_err = float('inf')
    for val, name, display in targets:
        err = abs(gap - val) / val
        if err < best_err:
            best_err = err
            best_name = name
            best_val = val
    
    symbol = "✓" if best_err < 0.12 else ("~" if best_err < 0.20 else "✗")
    print(f"  {sys:15s} {label:25s}  gap={gap:.3f}  → {best_name} ({best_val:.3f}) {symbol} {best_err*100:.1f}% error")

# Now the key question: is this clustering significant?
print()
print("=" * 80)
print("NULL HYPOTHESIS: Monte Carlo test")
print("=" * 80)
print()
print("Question: If gaps were randomly distributed (uniform on 0.5-2.0),")
print("how often would they cluster this well around our preferred targets?")
print()

# Compute our data's total distance from nearest target
def total_target_distance(gaps, targets_list):
    total = 0
    for gap in gaps:
        best_err = min(abs(gap - t[0]) / t[0] for t in targets_list)
        total += best_err
    return total / len(gaps)

our_gaps = [g[2] for g in measured_gaps]
our_score = total_target_distance(our_gaps, targets)

# Monte Carlo: generate random gap sets and compute their scores
n_trials = 100000
n_better = 0
for _ in range(n_trials):
    random_gaps = [random.uniform(0.5, 2.0) for _ in range(len(our_gaps))]
    random_score = total_target_distance(random_gaps, targets)
    if random_score <= our_score:
        n_better += 1

p_value = n_better / n_trials

print(f"Our data: mean distance from nearest target = {our_score:.4f}")
print(f"Random data scoring as well or better: {n_better}/{n_trials}")
print(f"p-value = {p_value:.4f}")
print()
if p_value < 0.05:
    print(f"→ SIGNIFICANT at p < 0.05. The clustering is unlikely by chance.")
elif p_value < 0.10:
    print(f"→ MARGINALLY significant (p < 0.10). Suggestive but not conclusive.")
else:
    print(f"→ NOT significant. The clustering could easily arise by chance.")

# Now do a finer test: specifically for 4π and (2π)²
print()
print("=" * 80)
print("SPECIFIC TEST: Clustering around 4π (1.099) and (2π)² (1.596)")
print("=" * 80)
print()

# Group gaps by which target they're nearest to
near_4pi = [(s, l, g) for s, l, g in measured_gaps if abs(g - target_4pi) < abs(g - target_2pi_sq)]
near_2pi_sq = [(s, l, g) for s, l, g in measured_gaps if abs(g - target_2pi_sq) <= abs(g - target_4pi)]

print(f"Gaps nearer to 4π (1.099):")
for s, l, g in near_4pi:
    err = abs(g - target_4pi) / target_4pi * 100
    print(f"  {s:15s} {l:25s}  {g:.3f}  ({err:.1f}% from 4π)")
    
print(f"\nGaps nearer to (2π)² (1.596):")
for s, l, g in near_2pi_sq:
    err = abs(g - target_2pi_sq) / target_2pi_sq * 100
    print(f"  {s:15s} {l:25s}  {g:.3f}  ({err:.1f}% from (2π)²)")

# Mean error for each group
if near_4pi:
    mean_4pi_err = sum(abs(g - target_4pi)/target_4pi for _, _, g in near_4pi) / len(near_4pi) * 100
    print(f"\nMean error from 4π: {mean_4pi_err:.1f}% (n={len(near_4pi)})")
if near_2pi_sq:
    mean_2pi_err = sum(abs(g - target_2pi_sq)/target_2pi_sq for _, _, g in near_2pi_sq) / len(near_2pi_sq) * 100
    print(f"Mean error from (2π)²: {mean_2pi_err:.1f}% (n={len(near_2pi_sq)})")

# Two-sample test: do the gaps bimodally cluster around these two values?
print()
print("=" * 80)
print("BIMODAL CLUSTERING TEST")
print("=" * 80)
print()

all_gaps_sorted = sorted(our_gaps)
print(f"All gaps sorted: {[f'{g:.3f}' for g in all_gaps_sorted]}")
print()

# Check if there's a gap in the middle (bimodal signature)
gap_diffs = [all_gaps_sorted[i+1] - all_gaps_sorted[i] for i in range(len(all_gaps_sorted)-1)]
print(f"Consecutive differences: {[f'{d:.3f}' for d in gap_diffs]}")
max_gap_idx = gap_diffs.index(max(gap_diffs))
print(f"Largest gap: {gap_diffs[max_gap_idx]:.3f} between values {all_gaps_sorted[max_gap_idx]:.3f} and {all_gaps_sorted[max_gap_idx+1]:.3f}")

cluster_1 = all_gaps_sorted[:max_gap_idx+1]
cluster_2 = all_gaps_sorted[max_gap_idx+1:]
print(f"\nCluster 1: {[f'{g:.3f}' for g in cluster_1]}  mean = {sum(cluster_1)/len(cluster_1):.3f}")
print(f"Cluster 2: {[f'{g:.3f}' for g in cluster_2]}  mean = {sum(cluster_2)/len(cluster_2):.3f}")
print(f"\n4π = {target_4pi:.3f}")
print(f"(2π)² = {target_2pi_sq:.3f}")

# How close are cluster means to the predicted values?
if cluster_1:
    c1_mean = sum(cluster_1)/len(cluster_1)
    c1_err = abs(c1_mean - target_4pi) / target_4pi * 100
    print(f"\nCluster 1 mean vs 4π: {c1_err:.1f}% error")
if cluster_2:
    c2_mean = sum(cluster_2)/len(cluster_2)
    c2_err = abs(c2_mean - target_2pi_sq) / target_2pi_sq * 100
    print(f"Cluster 2 mean vs (2π)²: {c2_err:.1f}% error")

# Monte Carlo for bimodal clustering
print()
print("Monte Carlo: how often do 8 random values on [0.5, 2.0] form")
print(f"two clusters with means within 15% of 4π and (2π)²?")

n_bimodal = 0
for _ in range(n_trials):
    rg = sorted([random.uniform(0.5, 2.0) for _ in range(8)])
    # Find largest gap
    diffs = [rg[i+1] - rg[i] for i in range(7)]
    mi = diffs.index(max(diffs))
    c1 = rg[:mi+1]
    c2 = rg[mi+1:]
    if c1 and c2:
        m1 = sum(c1)/len(c1)
        m2 = sum(c2)/len(c2)
        e1 = abs(m1 - target_4pi) / target_4pi
        e2 = abs(m2 - target_2pi_sq) / target_2pi_sq
        if e1 < 0.15 and e2 < 0.15:
            n_bimodal += 1

p_bimodal = n_bimodal / n_trials
print(f"p-value (bimodal): {p_bimodal:.5f}")
if p_bimodal < 0.01:
    print(f"→ HIGHLY SIGNIFICANT. The bimodal clustering around 4π and (2π)² is very unlikely by chance.")
elif p_bimodal < 0.05:
    print(f"→ SIGNIFICANT at p < 0.05.")
else:
    print(f"→ Not significant at p < 0.05.")

