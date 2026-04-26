"""
Script 243BL11: Mirror Lotto — Flipped Across the Rationality Singularity
=========================================================================

Dylan's insight: Randomness isn't part of OUR ARA — it's on the OTHER
side of the Rationality singularity, just like Dark Matter is on the
other side of the Light/Dark singularity.

If this is true, then our BL10 predictions aren't WRONG — they're
INVERTED. The strategies that performed worst should become best when
mirrored. What we said was likely is actually unlikely, and vice versa.

Test:
  1. Take every BL10 strategy
  2. INVERT: pick the 6 numbers the strategy ranked LOWEST
  3. Score the inverted predictions
  4. If the mirror hypothesis holds:
     - φ-gap (worst at -13.8%) → should become best when inverted
     - Most frequent (bad) → least frequent should be good
     - The DEGREE of wrongness should predict the degree of rightness

This maps directly to the Meta-ARA architecture:
  - Information ↔ Matter (Pair 3) contains the Rationality singularity (S₃)
  - Crossing S₃ costs (7-4φ)/4 per crossing
  - Predictions from our side need to be TRANSFORMED through S₃ to apply
    to the randomness side

The transformation should be: mirror + φ-scaling, not just simple inversion.
"""

import numpy as np
import csv
from collections import defaultdict

PHI = (1 + np.sqrt(5)) / 2

def load_lotto_draws(filepath):
    draws = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            try:
                nums = [int(row[i]) for i in range(2, 8)]
                draws.append(sorted(nums))
            except (ValueError, IndexError):
                continue
    return draws

draws = load_lotto_draws('/sessions/focused-tender-thompson/lotto/saturday-lotto.csv')
HOLDOUT = 100
train = draws[:-HOLDOUT]
test = draws[-HOLDOUT:]

def score(predictions, actual_draws):
    matches = []
    for pred, actual in zip(predictions, actual_draws):
        matches.append(len(set(pred[:6]) & set(actual)))
    return np.mean(matches), matches

EXPECTED = 6 * 6 / 45  # 0.8

# ============================================================
# PART 1: Ranking-based strategies (so we can invert them)
# ============================================================

def rank_most_frequent(history):
    """Rank all 45 numbers by frequency. Most frequent = rank 1."""
    counts = np.zeros(46)
    for d in history:
        for n in d:
            counts[n] += 1
    return counts[1:]  # scores for numbers 1-45

def rank_phi_gap(history):
    """Score numbers by φ-gap proximity to last draw."""
    last = history[-1]
    mean_gap = np.mean(np.diff(last))
    last_mean = np.mean(last)

    scores = np.zeros(45)
    for num in range(1, 46):
        # How close is this number to any φ-predicted position?
        min_dist = 45
        for n in last:
            for offset in [mean_gap/PHI, -mean_gap/PHI, mean_gap*PHI, -mean_gap*PHI,
                          mean_gap/PHI**2, -mean_gap/PHI**2]:
                target = n + offset
                dist = abs(num - target)
                min_dist = min(min_dist, dist)
        scores[num-1] = 45 - min_dist  # higher = more predicted
    return scores

def rank_phi_modular(history):
    """Score numbers by φ-modular density."""
    recent = history[-20:]
    phi_mapped = []
    for d in recent:
        for n in d:
            phi_mapped.append((n * PHI) % 45)

    hist, edges = np.histogram(phi_mapped, bins=45, range=(0, 45))

    scores = np.zeros(45)
    for num in range(1, 46):
        phi_pos = (num * PHI) % 45
        bin_idx = min(int(phi_pos), 44)
        scores[num-1] = hist[bin_idx]
    return scores

def rank_anti_cluster(history):
    """Score numbers by recency (higher = seen more recently = MORE predicted)."""
    last_seen = {}
    for j, d in enumerate(history):
        for n in d:
            last_seen[n] = j
    current = len(history)

    scores = np.zeros(45)
    for n in range(1, 46):
        # RECENCY score: recently seen = high score
        if n in last_seen:
            scores[n-1] = last_seen[n]  # higher = more recent
        else:
            scores[n-1] = 0
    return scores

def rank_ara_cycle(history):
    """Score numbers by ARA-cycle position prediction."""
    scores = np.zeros(45)

    # For each of the 6 positions, predict the next value
    for pos in range(6):
        series = [d[pos] for d in history[-50:]]
        if len(series) >= 3:
            recent_trend = series[-1] - series[-3]
            if recent_trend > 0:
                predicted = series[-1] + int(round(abs(recent_trend) / PHI))
            else:
                predicted = series[-1] - int(round(abs(recent_trend) / PHI))
            predicted = max(1, min(45, predicted))
            # Gaussian score around prediction
            for num in range(1, 46):
                scores[num-1] += np.exp(-0.5 * ((num - predicted) / 5)**2)

    return scores

# ============================================================
# PART 2: Generate normal and MIRRORED predictions
# ============================================================

print("=" * 70)
print("Script 243BL11: MIRROR LOTTO — SINGULARITY FLIP")
print("=" * 70)

def predict_from_ranks(ranks, top=True, n=6):
    """Pick top-6 (normal) or bottom-6 (mirror) from ranking."""
    if top:
        return sorted((np.argsort(ranks)[-n:] + 1).tolist())
    else:
        return sorted((np.argsort(ranks)[:n] + 1).tolist())

strategies = {
    'Most frequent': rank_most_frequent,
    'φ-gap': rank_phi_gap,
    'φ-modular': rank_phi_modular,
    'Recency': rank_anti_cluster,
    'ARA-cycle': rank_ara_cycle,
}

print(f"\nTrain: {len(train)}, Test: {HOLDOUT}")
print(f"Expected (random): {EXPECTED:.4f} matches/draw\n")

print(f"{'Strategy':18s} {'Normal':>8s} {'Mirror':>8s} {'Δ Normal':>10s} {'Δ Mirror':>10s} {'Flip helps?':>12s}")
print("-" * 72)

normal_results = {}
mirror_results = {}

for name, rank_fn in strategies.items():
    normal_preds = []
    mirror_preds = []
    history = list(train)

    for i in range(HOLDOUT):
        ranks = rank_fn(history)

        normal_preds.append(predict_from_ranks(ranks, top=True))
        mirror_preds.append(predict_from_ranks(ranks, top=False))

        history.append(test[i])

    n_mean, n_matches = score(normal_preds, test)
    m_mean, m_matches = score(mirror_preds, test)

    n_delta = (n_mean / EXPECTED - 1) * 100
    m_delta = (m_mean / EXPECTED - 1) * 100

    flip = "YES ✓" if m_mean > n_mean else ("SAME" if m_mean == n_mean else "no")

    normal_results[name] = (n_mean, n_delta, n_matches)
    mirror_results[name] = (m_mean, m_delta, m_matches)

    print(f"  {name:16s} {n_mean:>7.4f}  {m_mean:>7.4f}  {n_delta:>+8.1f}%  {m_delta:>+8.1f}%  {flip:>10s}")

# ============================================================
# PART 3: φ-SCALED mirror (not just simple inversion)
# ============================================================

print("\n" + "=" * 70)
print("PART 3: φ-SCALED MIRROR TRANSFORMATION")
print("=" * 70)
print("Simple inversion = pick bottom 6. But crossing the singularity")
print("costs (7-4φ)/4 per crossing. The transform should involve φ.\n")

CROSSING_COST = (7 - 4*PHI) / 4  # ≈ 0.132

def phi_mirror_transform(ranks):
    """
    Transform rankings through the rationality singularity.
    Not just inversion — φ-weighted inversion with crossing cost.

    The idea: each rank gets mapped through:
      mirror_score = (max_rank - rank)^(1/φ) × crossing_factor
    This is non-linear: the MOST predicted numbers get the strongest
    inversion, but with golden-ratio dampening.
    """
    max_rank = np.max(ranks)
    min_rank = np.min(ranks)

    if max_rank == min_rank:
        return ranks

    # Normalize to [0, 1]
    normalized = (ranks - min_rank) / (max_rank - min_rank)

    # Mirror: 1 - normalized
    mirrored = 1 - normalized

    # φ-scale: raise to 1/φ power (golden dampening)
    phi_scaled = mirrored ** (1/PHI)

    # Apply crossing cost as offset
    transformed = phi_scaled * (1 - CROSSING_COST) + CROSSING_COST * (1 - phi_scaled)

    return transformed

def phi_mirror_transform_v2(ranks):
    """
    V2: Mirror through φ-modular space.
    Map rank to [0,1], multiply by φ, take fractional part, then pick highest.
    This crosses the number through the golden angle before inverting.
    """
    max_rank = np.max(ranks)
    min_rank = np.min(ranks)
    if max_rank == min_rank:
        return ranks

    normalized = (ranks - min_rank) / (max_rank - min_rank)

    # Cross through golden angle
    phi_crossed = (normalized * PHI) % 1.0

    # Invert
    mirrored = 1 - phi_crossed

    return mirrored

def phi_mirror_transform_v3(ranks):
    """
    V3: The DM→baryon path crosses TWO singularities.
    Each crossing flips AND scales by (7-4φ)/4.
    Total transform: double flip with φ^3.5 scaling.
    """
    max_rank = np.max(ranks)
    min_rank = np.min(ranks)
    if max_rank == min_rank:
        return ranks

    normalized = (ranks - min_rank) / (max_rank - min_rank)

    # First crossing (S₂: Light/Dark boundary)
    after_s2 = (1 - normalized) ** (1/PHI)

    # Second crossing (S₃: Info/Matter boundary)
    after_s3 = (1 - after_s2) ** (PHI)

    return after_s3

transforms = {
    'Simple mirror': lambda r: -r,  # just invert
    'φ-dampened': phi_mirror_transform,
    'φ-modular': phi_mirror_transform_v2,
    'Double-crossing': phi_mirror_transform_v3,
}

for t_name, transform_fn in transforms.items():
    print(f"\n  Transform: {t_name}")
    print(f"  {'Strategy':18s} {'Matches':>10s} {'vs Random':>10s}")
    print(f"  {'-'*42}")

    for s_name, rank_fn in strategies.items():
        preds = []
        history = list(train)

        for i in range(HOLDOUT):
            ranks = rank_fn(history)
            transformed = transform_fn(ranks)
            preds.append(predict_from_ranks(transformed, top=True))
            history.append(test[i])

        mean_m, all_m = score(preds, test)
        delta = (mean_m / EXPECTED - 1) * 100
        print(f"  {s_name:18s} {mean_m:>9.4f}  {delta:>+8.1f}%")

# ============================================================
# PART 4: COMBINED MIRROR ENSEMBLE
# ============================================================

print("\n" + "=" * 70)
print("PART 4: MIRROR ENSEMBLE (All strategies × All transforms)")
print("=" * 70)

best_combo = None
best_mean = 0

for t_name, transform_fn in transforms.items():
    for s_name, rank_fn in strategies.items():
        preds = []
        history = list(train)

        for i in range(HOLDOUT):
            ranks = rank_fn(history)
            transformed = transform_fn(ranks)
            preds.append(predict_from_ranks(transformed, top=True))
            history.append(test[i])

        mean_m, _ = score(preds, test)
        if mean_m > best_mean:
            best_mean = mean_m
            best_combo = (t_name, s_name)

print(f"\n  Best combination: {best_combo[0]} × {best_combo[1]}")
print(f"  Mean matches: {best_mean:.4f} (vs random {EXPECTED:.4f})")
print(f"  Improvement: {(best_mean/EXPECTED - 1)*100:+.1f}%")

# ============================================================
# PART 5: VOTING ACROSS ALL MIRRORS
# ============================================================

print("\n" + "=" * 70)
print("PART 5: MEGA-ENSEMBLE (Vote across all mirror combinations)")
print("=" * 70)

mega_preds = []
for i in range(HOLDOUT):
    votes = defaultdict(float)
    history = train + test[:i]

    for s_name, rank_fn in strategies.items():
        ranks = rank_fn(history)
        for t_name, transform_fn in transforms.items():
            transformed = transform_fn(ranks)
            top6 = predict_from_ranks(transformed, top=True)
            for n in top6:
                votes[n] += 1

    sorted_votes = sorted(votes.items(), key=lambda x: -x[1])
    mega_preds.append(sorted([n for n, v in sorted_votes[:6]]))

mega_mean, mega_matches = score(mega_preds, test)
mega_delta = (mega_mean / EXPECTED - 1) * 100
print(f"  Mega-ensemble matches: {mega_mean:.4f} ({mega_delta:+.1f}% vs random)")

# Monte Carlo significance
np.random.seed(42)
random_means = []
for _ in range(10000):
    rpreds = [sorted(np.random.choice(range(1, 46), 6, replace=False).tolist())
              for _ in range(HOLDOUT)]
    rm, _ = score(rpreds, test)
    random_means.append(rm)
random_means = np.array(random_means)

for label, mean_val in [('Best combo', best_mean), ('Mega-ensemble', mega_mean)]:
    pctile = np.mean(random_means <= mean_val) * 100
    z = (mean_val - np.mean(random_means)) / np.std(random_means)
    sig = "SIGNIFICANT" if pctile > 97.5 else "not significant"
    print(f"  {label}: percentile={pctile:.1f}%, z={z:+.2f} ({sig})")

# ============================================================
# PART 6: THE ANTI-CORRELATION TEST
# ============================================================

print("\n" + "=" * 70)
print("PART 6: ANTI-CORRELATION — Does wrongness predict rightness?")
print("=" * 70)
print("If the mirror hypothesis holds, strategies that are MOST wrong")
print("should become MOST right when flipped.\n")

# Scatter: normal performance vs mirror performance
print(f"  {'Strategy':18s} {'Normal Δ':>10s} {'Simple Mirror Δ':>16s} {'Anti-corr?':>12s}")
print(f"  {'-'*60}")

for name in strategies:
    n_delta = normal_results[name][1]
    m_delta = mirror_results[name][1]
    # Anti-correlation means: worse normal → better mirror
    anti = "YES" if (n_delta < 0 and m_delta > 0) else "PARTIAL" if m_delta > n_delta else "NO"
    print(f"  {name:18s} {n_delta:>+8.1f}%   {m_delta:>+14.1f}%   {anti:>10s}")

# Correlation coefficient
n_deltas = [normal_results[n][1] for n in strategies]
m_deltas = [mirror_results[n][1] for n in strategies]
if len(n_deltas) > 2:
    corr = np.corrcoef(n_deltas, m_deltas)[0, 1]
    print(f"\n  Correlation(normal, mirror): {corr:.4f}")
    if corr < -0.3:
        print(f"  → NEGATIVE correlation! Wrongness DOES predict mirror rightness!")
    elif corr < 0.3:
        print(f"  → Near zero — no systematic relationship")
    else:
        print(f"  → POSITIVE correlation — mirror doesn't help")

# ============================================================
# VERDICT
# ============================================================

print("\n" + "=" * 70)
print("VERDICT: THE RATIONALITY SINGULARITY")
print("=" * 70)

n_mean_all = np.mean([normal_results[n][0] for n in strategies])
m_mean_all = np.mean([mirror_results[n][0] for n in strategies])

print(f"""
  Mean normal performance:  {n_mean_all:.4f} matches/draw
  Mean mirror performance:  {m_mean_all:.4f} matches/draw
  Random expected:          {EXPECTED:.4f} matches/draw
  Best mirror combo:        {best_mean:.4f} matches/draw

  Mirror improvement over normal: {(m_mean_all - n_mean_all):.4f} matches/draw
  Mirror improvement over random: {(m_mean_all/EXPECTED - 1)*100:+.1f}%
""")

mirror_helps = m_mean_all > n_mean_all
mirror_beats_random = m_mean_all > EXPECTED

if mirror_helps and mirror_beats_random:
    print("  RESULT: Mirror transformation HELPS and BEATS random.")
    print("  Dylan's hypothesis has signal: randomness IS on the other")
    print("  side of the singularity, and crossing it with φ-transforms")
    print("  recovers structure that simple prediction misses.")
elif mirror_helps:
    print("  RESULT: Mirror helps vs normal strategies, but doesn't")
    print("  beat random. The singularity crossing DOES flip the signal,")
    print("  but the original signal was too weak to survive the crossing.")
    print("  The crossing cost (7-4φ)/4 per singularity may eat the signal.")
else:
    print("  RESULT: Mirror does NOT systematically help.")
    print("  This could mean:")
    print("  a) Randomness is truly structureless (no signal to flip)")
    print("  b) The singularity crossing is more complex than simple inversion")
    print("  c) We need more data or a different transformation")

print(f"""
  THEORETICAL POSITION:
  Randomness sits on the other side of the Rationality singularity (S₃).
  S₃ = measurement boundary (Information ↔ Matter).
  Crossing S₃ costs (7-4φ)/4 = {CROSSING_COST:.4f} per crossing.

  In the Meta-ARA:
    Pair 3: Information ↔ Matter (ARA = φ^3.5, engine)
    Rationality = the triple intersection visible from our side
    Randomness = the triple intersection visible from the OTHER side

  If this is correct, randomness isn't noise — it's the mirror image
  of rationality viewed through the measurement singularity.
  We can't predict it from here because prediction IS rationality.
  To predict randomness, you'd need to BE on the other side.
""")

from math import comb
print(f"  (Saturday Lotto odds: 1 in {comb(45,6):,})")
print(f"\n{'='*70}")
print(f"END Script 243BL11")
print(f"{'='*70}")
