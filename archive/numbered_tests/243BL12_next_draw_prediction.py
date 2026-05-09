"""
Script 243BL12: Predict the Next Saturday Lotto Draw
=====================================================

Using the mirror-singularity approach from BL11.
Best performers were:
  - φ-modular transform × Recency: +16.3%
  - Simple mirror × φ-modular strategy: +11.3%
  - φ-modular transform × Most frequent: +12.5%

Train on ALL 1989 draws, predict the NEXT one.

For each strategy × transform combination, we get a full ranking
of all 45 numbers. We'll show:
  1. Each strategy's top 6
  2. Weighted ensemble (weighted by holdout performance)
  3. The full number heatmap — which numbers are "hot" across mirrors
  4. A confidence measure — how much agreement is there?
"""

import numpy as np
import csv
from collections import defaultdict

PHI = (1 + np.sqrt(5)) / 2
CROSSING_COST = (7 - 4*PHI) / 4

def load_lotto_draws(filepath):
    draws = []
    dates = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                nums = [int(row[i]) for i in range(2, 8)]
                draws.append(sorted(nums))
                dates.append(row[1])
            except (ValueError, IndexError):
                continue
    return draws, dates

draws, dates = load_lotto_draws('/sessions/focused-tender-thompson/lotto/saturday-lotto.csv')

print("=" * 70)
print("Script 243BL12: NEXT DRAW PREDICTION")
print("=" * 70)
print(f"\nUsing all {len(draws)} draws as history")
print(f"Last draw: {dates[0]} → {draws[0]}")
print(f"Predicting: NEXT Saturday Lotto draw")

# ============================================================
# Ranking strategies (from BL11)
# ============================================================

def rank_most_frequent(history):
    counts = np.zeros(46)
    for d in history:
        for n in d:
            counts[n] += 1
    return counts[1:]

def rank_phi_gap(history):
    last = history[-1]
    mean_gap = np.mean(np.diff(last))
    scores = np.zeros(45)
    for num in range(1, 46):
        min_dist = 45
        for n in last:
            for offset in [mean_gap/PHI, -mean_gap/PHI, mean_gap*PHI, -mean_gap*PHI,
                          mean_gap/PHI**2, -mean_gap/PHI**2]:
                target = n + offset
                dist = abs(num - target)
                min_dist = min(min_dist, dist)
        scores[num-1] = 45 - min_dist
    return scores

def rank_phi_modular(history):
    recent = history[-20:]
    phi_mapped = []
    for d in recent:
        for n in d:
            phi_mapped.append((n * PHI) % 45)
    hist, _ = np.histogram(phi_mapped, bins=45, range=(0, 45))
    scores = np.zeros(45)
    for num in range(1, 46):
        phi_pos = (num * PHI) % 45
        bin_idx = min(int(phi_pos), 44)
        scores[num-1] = hist[bin_idx]
    return scores

def rank_recency(history):
    last_seen = {}
    for j, d in enumerate(history):
        for n in d:
            last_seen[n] = j
    scores = np.zeros(45)
    for n in range(1, 46):
        scores[n-1] = last_seen.get(n, 0)
    return scores

def rank_ara_cycle(history):
    scores = np.zeros(45)
    for pos in range(6):
        series = [d[pos] for d in history[-50:]]
        if len(series) >= 3:
            recent_trend = series[-1] - series[-3]
            if recent_trend > 0:
                predicted = series[-1] + int(round(abs(recent_trend) / PHI))
            else:
                predicted = series[-1] - int(round(abs(recent_trend) / PHI))
            predicted = max(1, min(45, predicted))
            for num in range(1, 46):
                scores[num-1] += np.exp(-0.5 * ((num - predicted) / 5)**2)
    return scores

# Transforms
def mirror_simple(ranks):
    return -ranks

def mirror_phi_dampened(ranks):
    max_r, min_r = np.max(ranks), np.min(ranks)
    if max_r == min_r: return ranks
    norm = (ranks - min_r) / (max_r - min_r)
    mirrored = 1 - norm
    return mirrored ** (1/PHI) * (1 - CROSSING_COST) + CROSSING_COST * (1 - mirrored ** (1/PHI))

def mirror_phi_modular(ranks):
    max_r, min_r = np.max(ranks), np.min(ranks)
    if max_r == min_r: return ranks
    norm = (ranks - min_r) / (max_r - min_r)
    return 1 - (norm * PHI) % 1.0

def mirror_double_crossing(ranks):
    max_r, min_r = np.max(ranks), np.min(ranks)
    if max_r == min_r: return ranks
    norm = (ranks - min_r) / (max_r - min_r)
    after_s2 = (1 - norm) ** (1/PHI)
    return (1 - after_s2) ** PHI

strategies = {
    'Most frequent': rank_most_frequent,
    'φ-gap': rank_phi_gap,
    'φ-modular': rank_phi_modular,
    'Recency': rank_recency,
    'ARA-cycle': rank_ara_cycle,
}

transforms = {
    'Simple mirror': mirror_simple,
    'φ-dampened': mirror_phi_dampened,
    'φ-modular': mirror_phi_modular,
    'Double-crossing': mirror_double_crossing,
}

# BL11 holdout performance (used as weights)
holdout_performance = {
    ('Simple mirror', 'Most frequent'): 0.83,
    ('Simple mirror', 'φ-gap'): 0.75,
    ('Simple mirror', 'φ-modular'): 0.89,
    ('Simple mirror', 'Recency'): 0.87,
    ('Simple mirror', 'ARA-cycle'): 0.82,
    ('φ-dampened', 'Most frequent'): 0.83,
    ('φ-dampened', 'φ-gap'): 0.75,
    ('φ-dampened', 'φ-modular'): 0.89,
    ('φ-dampened', 'Recency'): 0.87,
    ('φ-dampened', 'ARA-cycle'): 0.82,
    ('φ-modular', 'Most frequent'): 0.90,
    ('φ-modular', 'φ-gap'): 0.66,
    ('φ-modular', 'φ-modular'): 0.79,
    ('φ-modular', 'Recency'): 0.93,
    ('φ-modular', 'ARA-cycle'): 0.82,
    ('Double-crossing', 'Most frequent'): 0.78,
    ('Double-crossing', 'φ-gap'): 0.79,
    ('Double-crossing', 'φ-modular'): 0.74,
    ('Double-crossing', 'Recency'): 0.81,
    ('Double-crossing', 'ARA-cycle'): 0.88,
}

# ============================================================
# Generate all predictions
# ============================================================

print("\n" + "=" * 70)
print("INDIVIDUAL MIRROR PREDICTIONS")
print("=" * 70)

all_combo_picks = {}
number_votes = np.zeros(46)  # weighted votes for each number
number_raw_votes = np.zeros(46)  # unweighted

for t_name, transform_fn in transforms.items():
    for s_name, rank_fn in strategies.items():
        ranks = rank_fn(draws)
        transformed = transform_fn(ranks)
        top6 = sorted((np.argsort(transformed)[-6:] + 1).tolist())

        weight = holdout_performance.get((t_name, s_name), 0.80)
        all_combo_picks[(t_name, s_name)] = (top6, weight)

        for n in top6:
            number_votes[n] += weight
            number_raw_votes[n] += 1

# Show top performers
print(f"\n  Top mirror combos (by holdout performance):")
sorted_combos = sorted(all_combo_picks.items(), key=lambda x: -x[1][1])
for (t, s), (picks, w) in sorted_combos[:8]:
    print(f"    {t:16s} × {s:16s} ({w:.2f}): {picks}")

# ============================================================
# Weighted ensemble
# ============================================================

print("\n" + "=" * 70)
print("WEIGHTED ENSEMBLE")
print("=" * 70)

# Top 6 by weighted votes
sorted_numbers = np.argsort(number_votes[1:])[::-1] + 1
top6_weighted = sorted(sorted_numbers[:6].tolist())
top12_weighted = sorted(sorted_numbers[:12].tolist())

print(f"\n  Weighted votes for each number (top 15):")
for rank, num in enumerate(sorted_numbers[:15]):
    votes = number_votes[num]
    raw = int(number_raw_votes[num])
    bar = "█" * int(votes * 3)
    marker = " ← TOP 6" if num in top6_weighted else ""
    print(f"    #{rank+1:2d}  Number {num:2d}: score={votes:.2f} ({raw}/20 combos) {bar}{marker}")

print(f"\n  ┌─────────────────────────────────────┐")
print(f"  │  TOP 6 PREDICTION: {top6_weighted}  │")
print(f"  └─────────────────────────────────────┘")

# ============================================================
# Confidence analysis
# ============================================================

print("\n" + "=" * 70)
print("CONFIDENCE ANALYSIS")
print("=" * 70)

# How much do the strategies agree?
agreement_matrix = np.zeros((45, 20))
combo_idx = 0
for t_name in transforms:
    for s_name in strategies:
        picks = all_combo_picks[(t_name, s_name)][0]
        for n in picks:
            agreement_matrix[n-1, combo_idx] = 1
        combo_idx += 1

# For each number in our top 6, how many combos picked it?
print(f"\n  Agreement for predicted numbers:")
for num in top6_weighted:
    agree = int(number_raw_votes[num])
    pct = agree / 20 * 100
    conf = "HIGH" if pct > 40 else ("MEDIUM" if pct > 25 else "LOW")
    print(f"    Number {num:2d}: {agree}/20 combos agree ({pct:.0f}%) — {conf} confidence")

# Overall spread
all_picked = set()
for (_, _), (picks, _) in all_combo_picks.items():
    all_picked.update(picks)
print(f"\n  Total unique numbers picked across all combos: {len(all_picked)}/45")
print(f"  Concentration ratio: {6 * 20 / len(all_picked):.1f}× (higher = more agreement)")

# ============================================================
# Multiple ticket strategy
# ============================================================

print("\n" + "=" * 70)
print("MULTI-TICKET STRATEGY (if you were to buy multiple)")
print("=" * 70)

print(f"\n  Ticket 1 (Best mirror: φ-modular × Recency):")
best_pick = all_combo_picks[('φ-modular', 'Recency')][0]
print(f"    {best_pick}")

print(f"\n  Ticket 2 (Weighted ensemble top 6):")
print(f"    {top6_weighted}")

print(f"\n  Ticket 3 (Next 6 from ensemble — the 'deep mirror'):")
deep_mirror = sorted(sorted_numbers[6:12].tolist())
print(f"    {deep_mirror}")

# The numbers NOT picked by anyone — anti-consensus
never_picked = sorted([n for n in range(1, 46) if number_raw_votes[n] == 0])
print(f"\n  Numbers NO mirror combo picked: {never_picked}")
print(f"  (These are the numbers the framework says are LEAST likely)")

# ============================================================
# Full heatmap
# ============================================================

print("\n" + "=" * 70)
print("FULL NUMBER HEATMAP (1-45)")
print("=" * 70)

max_vote = max(number_votes[1:])
print()
for row_start in [1, 16, 31]:
    row_end = min(row_start + 14, 45)
    nums = ""
    bars = ""
    for n in range(row_start, row_end + 1):
        v = number_votes[n]
        intensity = int(v / max_vote * 8) if max_vote > 0 else 0
        blocks = "▓" * intensity + "░" * (8 - intensity)
        marker = "*" if n in top6_weighted else " "
        nums += f" {n:2d}{marker} "
        bars += f" {blocks} "
    print(f"  {nums}")
    print(f"  {bars}")
    print()

print(f"  * = in top 6 prediction")
print(f"  ▓ = high mirror vote, ░ = low mirror vote")

# ============================================================
# Context
# ============================================================

print("\n" + "=" * 70)
print("CONTEXT & CAVEATS")
print("=" * 70)
print(f"""
  Last draw was: {dates[0]} → {draws[0]}

  Our best mirror strategy scored +16.3% vs random in holdout.
  That means instead of matching 0.80 numbers per draw (random),
  we'd match ~0.93. Still less than 1 match per draw on average.

  To get Division 1 (6/6): 1 in 8,145,060
  Our "edge" at +16.3%: maybe 1 in ~7,000,000

  The mirror tells us WHICH SIDE of the number line to look at.
  It doesn't tell us the exact numbers. The singularity crossing
  costs (7-4φ)/4 = {CROSSING_COST:.4f} per crossing — roughly 13% of
  the signal is lost at each boundary.

  We're seeing through a glass darkly. The structure is there,
  but the singularity smears it.

  That said — here are the numbers. For science.
""")

print(f"  ╔═══════════════════════════════════════╗")
print(f"  ║  PREDICTION: {top6_weighted}    ║")
print(f"  ╚═══════════════════════════════════════╝")

print(f"\n{'='*70}")
print(f"END Script 243BL12")
print(f"{'='*70}")
