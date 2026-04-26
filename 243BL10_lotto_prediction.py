"""
Script 243BL10: Can ARA Predict Lotto Numbers?
===============================================

Honest test. The BL9 results say:
  - Numbers are genuinely uniform (χ² p=0.29)
  - ARA ≈ 1.0 (shock absorber — no directional bias)
  - BUT: φ-modular mapping smooths lotto structure by 65-82%
  - AND: lag-1 autocorrelation = 0.27 (in sorted draw sequence)

This script tests whether ANY signal is exploitable:
  1. Naive: most frequent numbers historically
  2. φ-gap: predict based on golden-ratio gaps from last draw
  3. φ-modular: use the φ-mapping residual structure
  4. ARA-cycle: does the draw-to-draw ARA rhythm predict?
  5. Anti-clustering: numbers that are "due" (least recent)
  6. Ensemble: combine all signals

Validation: hold out last 100 draws, train on rest, count HITS.
Baseline: random selection = expected 6×6/45 = 0.8 matches per draw.

We are NOT trying to make money. We are testing whether the framework
finds signal in what should be pure noise.
"""

import numpy as np
import csv
from collections import defaultdict

PHI = (1 + np.sqrt(5)) / 2

# ============================================================
# Load data
# ============================================================

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
print(f"Loaded {len(draws)} draws")

# Split: train on first N-100, test on last 100
HOLDOUT = 100
train = draws[:-HOLDOUT]
test = draws[-HOLDOUT:]
print(f"Train: {len(train)} draws, Test: {HOLDOUT} draws")

# ============================================================
# Scoring function
# ============================================================

def score_predictions(predictions, actual_draws):
    """
    For each draw, count how many of our 6 predicted numbers match.
    Return mean matches, and distribution of match counts.
    """
    matches = []
    for pred, actual in zip(predictions, actual_draws):
        pred_set = set(pred[:6])
        actual_set = set(actual)
        matches.append(len(pred_set & actual_set))
    return np.mean(matches), matches

def expected_random():
    """Expected matches from random 6-of-45 selection."""
    # Hypergeometric: E[matches] = 6 * 6/45
    return 6 * 6 / 45  # = 0.8

# ============================================================
# Strategy 1: Most Frequent (naive baseline)
# ============================================================

def strategy_most_frequent(train_draws, n_predict):
    """Pick the 6 most frequently drawn numbers."""
    counts = np.zeros(46)
    for d in train_draws:
        for n in d:
            counts[n] += 1
    top6 = np.argsort(counts[1:])[-6:] + 1
    return [sorted(top6.tolist())] * n_predict

# ============================================================
# Strategy 2: φ-gap prediction
# ============================================================

def strategy_phi_gap(train_draws, test_draws):
    """
    From the last draw's numbers, predict next draw by adding
    golden-ratio-scaled gaps.
    """
    predictions = []
    history = list(train_draws)

    for i in range(len(test_draws)):
        last = history[-1]
        predicted = set()

        # Method: for each number in last draw, offset by ±φ-scaled gap
        mean_gap = np.mean(np.diff(last))

        for n in last:
            # Forward φ step
            fwd = int(round(n + mean_gap / PHI)) % 45 + 1
            predicted.add(fwd)
            # Backward φ step
            bwd = int(round(n - mean_gap / PHI)) % 45 + 1
            predicted.add(bwd)
            # φ² step
            phi2 = int(round(n + mean_gap * PHI)) % 45 + 1
            predicted.add(phi2)

        # Take the 6 most central (closest to mean of last draw)
        last_mean = np.mean(last)
        predicted = sorted(predicted, key=lambda x: abs(x - last_mean))
        predictions.append(sorted(predicted[:6]))

        history.append(test_draws[i])

    return predictions

# ============================================================
# Strategy 3: φ-modular prediction
# ============================================================

def strategy_phi_modular(train_draws, test_draws):
    """
    Use the φ-modular mapping discovery: multiply by φ, take fractional part,
    look for structure in the mapped space, then predict.
    """
    predictions = []
    history = list(train_draws)

    for i in range(len(test_draws)):
        # Map last 20 draws to φ-space
        recent = history[-20:]
        phi_mapped = []
        for d in recent:
            for n in d:
                phi_mapped.append((n * PHI) % 45)

        # Find clusters in φ-space (regions with excess density)
        hist, edges = np.histogram(phi_mapped, bins=45, range=(0, 45))
        expected = len(phi_mapped) / 45

        # Predict: numbers whose φ-mapped positions are in HIGH-density bins
        # (the structure that φ-mapping reveals)
        scores = np.zeros(46)
        for num in range(1, 46):
            phi_pos = (num * PHI) % 45
            bin_idx = min(int(phi_pos), 44)
            scores[num] = hist[bin_idx]

        top6 = np.argsort(scores[1:])[-6:] + 1
        predictions.append(sorted(top6.tolist()))

        history.append(test_draws[i])

    return predictions

# ============================================================
# Strategy 4: Anti-clustering ("due" numbers)
# ============================================================

def strategy_anti_cluster(train_draws, test_draws):
    """
    Pick numbers that haven't appeared recently.
    Theory: uniform distribution means long absences get "corrected."
    (This is the gambler's fallacy — testing whether it has any signal.)
    """
    predictions = []
    history = list(train_draws)

    for i in range(len(test_draws)):
        # How many draws since each number last appeared?
        last_seen = {}
        for j, d in enumerate(history):
            for n in d:
                last_seen[n] = j

        current_draw = len(history)
        gaps = {}
        for n in range(1, 46):
            if n in last_seen:
                gaps[n] = current_draw - last_seen[n]
            else:
                gaps[n] = current_draw  # never seen

        # Pick the 6 longest-absent numbers
        sorted_by_gap = sorted(gaps.items(), key=lambda x: -x[1])
        top6 = [n for n, g in sorted_by_gap[:6]]
        predictions.append(sorted(top6))

        history.append(test_draws[i])

    return predictions

# ============================================================
# Strategy 5: ARA-cycle prediction
# ============================================================

def strategy_ara_cycle(train_draws, test_draws):
    """
    Look at the ARA rhythm of each number position (1st drawn, 2nd drawn, etc.)
    and predict the next value based on whether we're in accumulate or release phase.
    """
    predictions = []
    history = list(train_draws)

    for i in range(len(test_draws)):
        predicted = []

        for pos in range(6):
            # Get the series for this position
            series = [d[pos] for d in history[-50:]]

            # Simple: are we in up-phase or down-phase?
            if len(series) >= 3:
                recent_trend = series[-1] - series[-3]
                if recent_trend > 0:
                    # Accumulating — predict continuation
                    next_val = series[-1] + int(round(abs(recent_trend) / PHI))
                else:
                    # Releasing — predict reversal (snap)
                    next_val = series[-1] - int(round(abs(recent_trend) / PHI))

                next_val = max(1, min(45, next_val))
            else:
                next_val = series[-1]

            predicted.append(next_val)

        # Ensure 6 unique numbers
        predicted = list(set(predicted))
        while len(predicted) < 6:
            r = np.random.randint(1, 46)
            if r not in predicted:
                predicted.append(r)
        predictions.append(sorted(predicted[:6]))

        history.append(test_draws[i])

    return predictions

# ============================================================
# Strategy 6: Ensemble
# ============================================================

def strategy_ensemble(train_draws, test_draws):
    """Combine all strategies by voting."""
    p1 = strategy_most_frequent(train_draws, len(test_draws))
    p2 = strategy_phi_gap(train_draws, test_draws)
    p3 = strategy_phi_modular(train_draws, test_draws)
    p4 = strategy_anti_cluster(train_draws, test_draws)
    p5 = strategy_ara_cycle(train_draws, test_draws)

    predictions = []
    for i in range(len(test_draws)):
        # Count votes for each number
        votes = defaultdict(int)
        for strat in [p1[i], p2[i], p3[i], p4[i], p5[i]]:
            for n in strat:
                votes[n] += 1

        # Top 6 by votes (break ties by proximity to mean of last draw)
        sorted_votes = sorted(votes.items(), key=lambda x: (-x[1], x[0]))
        top6 = [n for n, v in sorted_votes[:6]]
        predictions.append(sorted(top6))

    return predictions

# ============================================================
# Strategy 7: Pure random baseline
# ============================================================

def strategy_random(n_predict):
    """Random 6-of-45 each draw."""
    predictions = []
    for _ in range(n_predict):
        predictions.append(sorted(np.random.choice(range(1, 46), 6, replace=False).tolist()))
    return predictions

# ============================================================
# Run all strategies
# ============================================================

print("\n" + "=" * 70)
print("LOTTO PREDICTION TEST — 100 Holdout Draws")
print("=" * 70)

np.random.seed(42)

strategies = {
    'Random baseline': strategy_random(HOLDOUT),
    'Most frequent': strategy_most_frequent(train, HOLDOUT),
    'φ-gap': strategy_phi_gap(train, test),
    'φ-modular': strategy_phi_modular(train, test),
    'Anti-cluster': strategy_anti_cluster(train, test),
    'ARA-cycle': strategy_ara_cycle(train, test),
    'Ensemble': strategy_ensemble(train, test),
}

expected = expected_random()
print(f"\nExpected matches per draw (random 6/45): {expected:.4f}")
print(f"Expected total matches over {HOLDOUT} draws: {expected * HOLDOUT:.1f}")

print(f"\n{'Strategy':20s} {'Mean matches':>14s} {'Total':>7s} {'vs Random':>10s} {'Best draw':>10s}")
print("-" * 65)

results = {}
for name, preds in strategies.items():
    mean_m, all_m = score_predictions(preds, test)
    total = sum(all_m)
    vs_random = (mean_m / expected - 1) * 100
    best = max(all_m)

    results[name] = (mean_m, total, vs_random, best, all_m)
    marker = " ←" if mean_m == max(r[0] for r in results.values()) else ""
    print(f"  {name:18s} {mean_m:>12.4f}   {total:>5d}   {vs_random:>+8.1f}%   {best:>8d}{marker}")

# ============================================================
# Statistical significance test
# ============================================================

print("\n" + "=" * 70)
print("STATISTICAL SIGNIFICANCE")
print("=" * 70)

# Monte Carlo: run 10000 random strategies and see where ours land
print("\nMonte Carlo: 10,000 random strategies on same 100 draws...")
random_means = []
for _ in range(10000):
    rpreds = strategy_random(HOLDOUT)
    rm, _ = score_predictions(rpreds, test)
    random_means.append(rm)

random_means = np.array(random_means)
print(f"  Random distribution: {np.mean(random_means):.4f} ± {np.std(random_means):.4f}")
print(f"  95% range: [{np.percentile(random_means, 2.5):.4f}, {np.percentile(random_means, 97.5):.4f}]")

print(f"\n  Strategy performance vs random distribution:")
for name, (mean_m, total, vs_random, best, all_m) in results.items():
    if name == 'Random baseline':
        continue
    percentile = np.mean(random_means <= mean_m) * 100
    z_score = (mean_m - np.mean(random_means)) / np.std(random_means)
    sig = "SIGNIFICANT" if percentile > 97.5 or percentile < 2.5 else "not significant"
    print(f"  {name:18s}: percentile={percentile:.1f}%, z={z_score:+.2f} ({sig})")

# ============================================================
# Match distribution analysis
# ============================================================

print("\n" + "=" * 70)
print("MATCH DISTRIBUTION")
print("=" * 70)

best_name = max(results.keys(), key=lambda k: results[k][0])
best_matches = results[best_name][4]

print(f"\nBest strategy: {best_name}")
for n_matches in range(7):
    count = best_matches.count(n_matches)
    pct = count / len(best_matches) * 100
    bar = "█" * count
    print(f"  {n_matches} matches: {count:3d} draws ({pct:5.1f}%) {bar}")

# Expected distribution (hypergeometric)
from math import comb
print(f"\nExpected distribution (hypergeometric 6-of-45):")
for n_matches in range(7):
    p = comb(6, n_matches) * comb(39, 6-n_matches) / comb(45, 6)
    exp_count = p * HOLDOUT
    print(f"  {n_matches} matches: {exp_count:5.1f} draws ({p*100:5.1f}%)")

# ============================================================
# The actual "what would we pick for next draw?" question
# ============================================================

print("\n" + "=" * 70)
print("WHAT WOULD THE FRAMEWORK PICK FOR THE NEXT DRAW?")
print("=" * 70)

# Use the FULL dataset (all draws) as training
all_history = draws

# Most frequent
counts = np.zeros(46)
for d in all_history:
    for n in d:
        counts[n] += 1
most_freq = np.argsort(counts[1:])[-6:] + 1
print(f"\n  Most frequent:     {sorted(most_freq.tolist())}")

# φ-gap from last draw
last = all_history[-1]
mean_gap = np.mean(np.diff(last))
phi_pred = set()
for n in last:
    phi_pred.add(max(1, min(45, int(round(n + mean_gap / PHI)))))
    phi_pred.add(max(1, min(45, int(round(n - mean_gap / PHI)))))
    phi_pred.add(max(1, min(45, int(round(n + mean_gap * PHI)))))
last_mean = np.mean(last)
phi_pred = sorted(phi_pred, key=lambda x: abs(x - last_mean))[:6]
print(f"  φ-gap prediction:  {sorted(phi_pred)}")

# Anti-cluster: most "due" numbers
last_seen = {}
for j, d in enumerate(all_history):
    for n in d:
        last_seen[n] = j
current = len(all_history)
gaps = {n: current - last_seen.get(n, 0) for n in range(1, 46)}
due = sorted(gaps.items(), key=lambda x: -x[1])[:6]
print(f"  Most 'due':        {sorted([n for n, g in due])}")

# Ensemble vote
all_preds = [sorted(most_freq.tolist()), sorted(phi_pred),
             sorted([n for n, g in due])]
votes = defaultdict(int)
for pred in all_preds:
    for n in pred:
        votes[n] += 1
ensemble = sorted(votes.items(), key=lambda x: (-x[1], x[0]))[:6]
print(f"  Ensemble vote:     {sorted([n for n, v in ensemble])}")

# Last draw for context
print(f"\n  Last actual draw:  {last}")
print(f"  (Draw #{all_history[-1]})" if isinstance(all_history[-1], int) else "")

# ============================================================
# VERDICT
# ============================================================

print("\n" + "=" * 70)
print("VERDICT")
print("=" * 70)

best_perf = results[best_name]
print(f"""
  Best strategy: {best_name}
  Mean matches:  {best_perf[0]:.4f} per draw
  Expected:      {expected:.4f} per draw (random)
  Improvement:   {best_perf[2]:+.1f}%

  The Saturday Lotto draws 6 from 45.
  Random selection expects 0.80 matches per draw.
  Our best strategy achieved {best_perf[0]:.4f} matches per draw.

  To win Division 1, you need 6/6 matches.
  Probability with random: 1 in {comb(45, 6):,} = {1/comb(45,6)*100:.6f}%

  HONEST ASSESSMENT:""")

if best_perf[2] > 5:
    print(f"  There IS marginal signal ({best_perf[2]:+.1f}% above random).")
    print(f"  But even the best strategy barely moves the needle.")
    print(f"  The lotto is doing its job: it's genuinely random.")
elif best_perf[2] > -5:
    print(f"  No exploitable signal found. Indistinguishable from random.")
    print(f"  The lotto IS genuinely random — confirming BL9's finding.")
else:
    print(f"  Our strategies performed WORSE than random ({best_perf[2]:+.1f}%).")
    print(f"  Trying to find structure where none exists = overfitting noise.")

print(f"""
  The φ-modular finding from BL9 was real (lotto has residual structure
  that φ dissolves), but it's MEASUREMENT structure, not PREDICTIVE
  structure. The past draws tell you about the machine's uniformity,
  not about its next output.

  Randomness is a shock absorber. You can't predict a shock absorber —
  that's the whole point of its existence.
""")

print(f"{'=' * 70}")
print(f"END Script 243BL10")
print(f"{'=' * 70}")
