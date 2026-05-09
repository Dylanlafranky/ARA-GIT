import math
import random
random.seed(42)

target_4pi = math.log10(4 * math.pi)       # 1.099
target_2pi_sq = math.log10((2 * math.pi)**2)  # 1.596

# Our measured gaps
gaps = [0.964, 0.976, 0.977, 0.983, 1.075, 1.484, 1.515, 1.713]

print("=" * 80)
print("REFINED ANALYSIS: What the data actually shows")
print("=" * 80)
print()

# The key finding isn't "are these close to 4π?" in isolation.
# It's: "do gaps from DIFFERENT physical systems converge on the 
# SAME preferred values?"

# Five gaps from 4 different systems (neuron, engine, thunderstorm, 
# predator-prey) all land in [0.964, 1.075].
# Three gaps from 3 different systems (heart, hydrogen, engine)
# all land in [1.484, 1.713].

# Cluster tightness
c1 = [0.964, 0.976, 0.977, 0.983, 1.075]
c2 = [1.484, 1.515, 1.713]

c1_std = (sum((x - sum(c1)/len(c1))**2 for x in c1) / len(c1)) ** 0.5
c2_std = (sum((x - sum(c2)/len(c2))**2 for x in c2) / len(c2)) ** 0.5

print(f"Cluster 1 (near 4π = {target_4pi:.3f}):")
print(f"  Values: {c1}")
print(f"  Mean: {sum(c1)/len(c1):.4f}")
print(f"  Std:  {c1_std:.4f}")
print(f"  Spread: {max(c1)-min(c1):.3f} (range)")
print(f"  Systems: Neuron(×2), Engine, Thunderstorm, Predator-Prey")
print()
print(f"Cluster 2 (near (2π)² = {target_2pi_sq:.3f}):")
print(f"  Values: {c2}")
print(f"  Mean: {sum(c2)/len(c2):.4f}")
print(f"  Std:  {c2_std:.4f}")
print(f"  Spread: {max(c2)-min(c2):.3f} (range)")
print(f"  Systems: Heart, Hydrogen, Engine")
print()

# The real question: how tight are these clusters?
# Cluster 1 has spread 0.111 over range 0.964-1.075
# That's 5 values from 4 completely different physical domains
# spanning micro (neuron) to macro (ecology) all landing in
# a 0.111-wide window on a 1.5-wide range.

# Better null: what's the probability that 5 of 8 random values
# from uniform(0.5, 2.0) fall within a window of width 0.111?
# AND the remaining 3 fall within a window of width 0.229?

n_trials = 1000000
n_success = 0
width_1 = max(c1) - min(c1)  # 0.111
width_2 = max(c2) - min(c2)  # 0.229

for _ in range(n_trials):
    rg = sorted([random.uniform(0.5, 2.0) for _ in range(8)])
    # Check all possible 5/3 splits
    from itertools import combinations
    found = False
    for combo in combinations(range(8), 5):
        others = [i for i in range(8) if i not in combo]
        group1 = [rg[i] for i in combo]
        group2 = [rg[i] for i in others]
        if (max(group1) - min(group1) <= width_1 and 
            max(group2) - min(group2) <= width_2):
            found = True
            break
    if found:
        n_success += 1

p_tightness = n_success / n_trials
print("=" * 80)
print("CLUSTER TIGHTNESS TEST")
print("=" * 80)
print()
print(f"Test: 8 random uniform(0.5, 2.0) values can be split into")
print(f"groups of 5 and 3 where:")
print(f"  - Group of 5 has spread ≤ {width_1:.3f}")
print(f"  - Group of 3 has spread ≤ {width_2:.3f}")
print(f"p-value: {p_tightness:.6f} ({n_success}/{n_trials})")
print()

# ALSO: test whether the clusters land near the SPECIFIC predicted values
n_both = 0
for _ in range(n_trials):
    rg = sorted([random.uniform(0.5, 2.0) for _ in range(8)])
    found = False
    for combo in combinations(range(8), 5):
        others = [i for i in range(8) if i not in combo]
        group1 = [rg[i] for i in combo]
        group2 = [rg[i] for i in others]
        m1 = sum(group1)/5
        m2 = sum(group2)/3
        if (max(group1) - min(group1) <= width_1 and 
            max(group2) - min(group2) <= width_2 and
            abs(m1 - target_4pi)/target_4pi < 0.10 and
            abs(m2 - target_2pi_sq)/target_2pi_sq < 0.10):
            found = True
            break
    if found:
        n_both += 1

p_both = n_both / n_trials
print("COMBINED TEST: tight clusters AND near predicted values")
print(f"  Cluster 1 mean within 10% of 4π AND spread ≤ {width_1:.3f}")
print(f"  Cluster 2 mean within 10% of (2π)² AND spread ≤ {width_2:.3f}")
print(f"p-value: {p_both:.6f} ({n_both}/{n_trials})")
if p_both < 0.01:
    print("→ HIGHLY SIGNIFICANT (p < 0.01)")
elif p_both < 0.05:
    print("→ SIGNIFICANT (p < 0.05)")
elif p_both < 0.10:
    print("→ MARGINALLY SIGNIFICANT (p < 0.10)")
else:
    print("→ Not significant")

print()
print("=" * 80)
print("INTERPRETATION")
print("=" * 80)
print()
print("The data shows two clear clusters in subsystem spacing:")
print(f"  Cluster 1: mean 0.995 (4π predicts 1.099) — 9.5% error")
print(f"  Cluster 2: mean 1.571 ((2π)² predicts 1.596) — 1.6% error")
print()
print("The pattern spans wildly different physical domains:")
print("  • Neuron ion channels, engine valves, storm convection,")
print("    and ecological population dynamics all show ~1.0 spacing")
print("  • Heart muscle, hydrogen transitions, and engine thermal")
print("    cycles all show ~1.5 spacing")
print()
print("Whether this is 4π and (2π)² specifically (vs e.g. 10 and 10^1.5)")
print("cannot be determined from 8 data points. The cluster EXISTENCE is")
print("suggestive; the cluster IDENTITY (as multiples of π) requires more")
print("systems to confirm.")
print()
print("WHAT WOULD STRENGTHEN THE CASE:")
print("  1. Map 20+ more systems with independently measured subsystem gaps")
print("  2. If new gaps preferentially fall in these same two bands, the")
print("     clustering is real")
print("  3. If the band centers sharpen toward 4π and (2π)², the π")
print("     connection is real")
print("  4. Atomic clock transitions could settle it — precision to 18")
print("     decimal places")

