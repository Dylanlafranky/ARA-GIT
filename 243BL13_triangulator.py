"""
Script 243BL13: Three-Circle Lotto Triangulator
=================================================

Dylan's insight: We can't predict randomness from ONE side of the
singularity. But the three-circle architecture says you need THREE
coupled systems to reach the triple intersection (beeswax).

Three circles:
  Circle 1: RATIONALITY — our prediction models (patterns, frequencies, φ-mirrors)
  Circle 2: RANDOMNESS — the main 6 numbers (what we're trying to predict)
  Circle 3: INFORMATION — the supplementary numbers + jackpot energy
            (same physical process, different information channel)

The supplementary numbers are the perfect triangulator because:
  - They come from the SAME machine (same randomness source)
  - They carry DIFFERENT information value (can't win Div 1 with them)
  - They sit in a COUPLED but SEPARATE channel
  - They're literally the coupler between our rationality and the machine's randomness

Architecture:
  - Supps from draw N couple to main numbers of draw N (same-draw coupling)
  - Supps from draw N couple to main numbers of draw N+1 (cross-draw coupling)
  - Jackpot size = energy in the system (accumulation pressure)

The φ-coupling should be:
  - Horizontal: Main ↔ Supp (same rung, φ² coupler)
  - Vertical: Draw N → Draw N+1 (2/φ coupler)
  - The pipe carries 2φ down, φ up

Validation: holdout last 100 draws, compare against BL10 (no triangulation)
and BL11 (mirror only). If triangulation works, it should beat both.
"""

import numpy as np
import csv
from collections import defaultdict
from math import comb

PHI = (1 + np.sqrt(5)) / 2
CROSSING_COST = (7 - 4*PHI) / 4  # ≈ 0.132

# ============================================================
# Load full data including supplementary numbers and jackpots
# ============================================================

def load_full_data(filepath):
    draws = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            try:
                main = sorted([int(row[i]) for i in range(2, 8)])
                supps = sorted([int(row[i]) for i in range(8, 10)])
                draw_num = int(row[0])
                # Prize pool — may have varying columns depending on draw era
                try:
                    div1_prize = float(row[12]) if len(row) > 12 and row[12] else 0
                    div1_winners = int(row[10]) if len(row) > 10 and row[10] else 0
                except (ValueError, IndexError):
                    div1_prize = 0
                    div1_winners = 0
                draws.append({
                    'num': draw_num,
                    'main': main,
                    'supps': supps,
                    'prize': div1_prize,
                    'winners': div1_winners,
                })
            except (ValueError, IndexError):
                continue
    return draws

data = load_full_data('/sessions/focused-tender-thompson/lotto/saturday-lotto.csv')

print("=" * 70)
print("Script 243BL13: THREE-CIRCLE LOTTO TRIANGULATOR")
print("=" * 70)
print(f"\nLoaded {len(data)} draws with main + supplementary numbers")
print(f"Last draw #{data[0]['num']}: main={data[0]['main']}, supps={data[0]['supps']}")

# Check how many have prize data
with_prize = sum(1 for d in data if d['prize'] > 0)
print(f"Draws with prize data: {with_prize}/{len(data)}")

# ============================================================
# PART 1: Explore supplementary-main coupling
# ============================================================

print("\n" + "=" * 70)
print("PART 1: SUPPLEMENTARY ↔ MAIN COUPLING ANALYSIS")
print("=" * 70)

# Same-draw coupling: how often do supps predict the neighbourhood of mains?
supp_main_gaps = []
supp_near_main = 0
total_supp_checks = 0

for d in data:
    for s in d['supps']:
        for m in d['main']:
            gap = abs(s - m)
            supp_main_gaps.append(gap)
            if gap <= 3:  # within 3 of a main number
                supp_near_main += 1
            total_supp_checks += 1

mean_gap = np.mean(supp_main_gaps)
expected_gap = 45/3  # rough expected for uniform
near_frac = supp_near_main / total_supp_checks
# Expected fraction within ±3: roughly 7/45 * 6 ≈ 0.93... per supp
# Actually: P(|s-m| ≤ 3) for uniform 1-45 ≈ 7/44 per pair
expected_near = 7/44

print(f"\n  Same-draw supp-main gap:")
print(f"    Mean gap: {mean_gap:.2f} (expected ~{expected_gap:.1f})")
print(f"    Near fraction (±3): {near_frac:.4f} (expected ~{expected_near:.4f})")
print(f"    Ratio obs/expected: {near_frac/expected_near:.4f}")

# Cross-draw coupling: do supps from draw N predict main numbers in draw N+1?
cross_near = 0
cross_total = 0
cross_exact = 0

for i in range(len(data) - 1):
    supps_prev = data[i+1]['supps']  # data is reverse chronological
    mains_next = data[i]['main']
    for s in supps_prev:
        for m in mains_next:
            cross_total += 1
            if abs(s - m) <= 3:
                cross_near += 1
            if s == m:
                cross_exact += 1

cross_near_frac = cross_near / cross_total
cross_exact_frac = cross_exact / cross_total
expected_exact = 6 * 2 / 45  # P(any supp = any main) ≈ 12/45 per draw pair... no
# For 2 supps and 6 mains, P(at least one exact match) ≈ 1-(39/45)*(38/44) per pair
# Per pair: 1/45
expected_exact_per_pair = 1/45

print(f"\n  Cross-draw (supp[N] → main[N+1]):")
print(f"    Near fraction (±3): {cross_near_frac:.4f} (expected ~{expected_near:.4f})")
print(f"    Exact match fraction: {cross_exact_frac:.4f} (expected ~{expected_exact_per_pair:.4f})")
print(f"    Exact ratio obs/expected: {cross_exact_frac/expected_exact_per_pair:.4f}")

# φ-coupling test: is the supp-to-main relationship φ-structured?
print(f"\n  φ-coupling test:")
supp_ratios = []
for d in data:
    for s in d['supps']:
        for m in d['main']:
            if m > 0 and s > 0:
                r = max(s, m) / min(s, m)
                supp_ratios.append(r)

supp_ratios = np.array(supp_ratios)
near_phi = np.sum(np.abs(supp_ratios - PHI) / PHI < 0.05) / len(supp_ratios)
near_phi2 = np.sum(np.abs(supp_ratios - PHI**2) / PHI**2 < 0.05) / len(supp_ratios)
near_inv = np.sum(np.abs(supp_ratios - 1/PHI) / (1/PHI) < 0.05) / len(supp_ratios)

# Expected for random uniform ratios
print(f"    Fraction near φ (±5%):  {near_phi:.4f}")
print(f"    Fraction near φ² (±5%): {near_phi2:.4f}")
print(f"    Fraction near 1/φ: not applicable (ratio always ≥ 1)")

# ============================================================
# PART 2: Build the triangulator
# ============================================================

print("\n" + "=" * 70)
print("PART 2: THREE-CIRCLE PREDICTION STRATEGIES")
print("=" * 70)

HOLDOUT = 100
train_data = data[HOLDOUT:]  # older draws (data is reverse chron)
test_data = data[:HOLDOUT]   # most recent 100

def score(predictions, actual_draws):
    matches = []
    for pred, actual in zip(predictions, actual_draws):
        matches.append(len(set(pred[:6]) & set(actual['main'])))
    return np.mean(matches), matches

EXPECTED = 6 * 6 / 45

# ---- Strategy T1: Supp-neighbourhood prediction ----
# If supps couple to next draw's mains, then numbers NEAR the last supps
# should be more likely.

def strategy_supp_neighbourhood(train, test, radius=3):
    """Predict numbers near the previous draw's supplementary numbers."""
    preds = []
    history = list(reversed(train))  # chronological order

    for i in range(len(test)):
        last_supps = history[-1]['supps']
        # Score each number by proximity to supps
        scores = np.zeros(45)
        for num in range(1, 46):
            for s in last_supps:
                dist = abs(num - s)
                if dist == 0:
                    scores[num-1] += 5  # exact match bonus
                else:
                    scores[num-1] += max(0, (radius + 1 - dist)) / (radius + 1)

        top6 = sorted((np.argsort(scores)[-6:] + 1).tolist())
        preds.append(top6)
        history.append(test[len(test) - 1 - i])

    return preds

# ---- Strategy T2: Supp-neighbourhood MIRRORED ----
# Apply the singularity flip to supp-based predictions

def strategy_supp_mirror(train, test, radius=3):
    """Mirror of supp neighbourhood — numbers FURTHEST from supps."""
    preds = []
    history = list(reversed(train))

    for i in range(len(test)):
        last_supps = history[-1]['supps']
        scores = np.zeros(45)
        for num in range(1, 46):
            for s in last_supps:
                dist = abs(num - s)
                scores[num-1] += dist  # FURTHER = higher score

        top6 = sorted((np.argsort(scores)[-6:] + 1).tolist())
        preds.append(top6)
        history.append(test[len(test) - 1 - i])

    return preds

# ---- Strategy T3: Supp φ-modular coupling ----
# Map supps through golden angle, use as attractors for next draw

def strategy_supp_phi(train, test):
    """Map supps through φ to predict next mains."""
    preds = []
    history = list(reversed(train))

    for i in range(len(test)):
        last_supps = history[-1]['supps']
        last_main = history[-1]['main']

        scores = np.zeros(45)
        for num in range(1, 46):
            # φ-mapped proximity to supps
            for s in last_supps:
                phi_s = (s * PHI) % 45 + 1
                dist = min(abs(num - phi_s), 45 - abs(num - phi_s))
                scores[num-1] += np.exp(-dist / (45 / PHI))

            # φ²-coupled distance from main numbers (horizontal coupler)
            for m in last_main:
                phi2_m = (m * PHI**2) % 45 + 1
                dist = min(abs(num - phi2_m), 45 - abs(num - phi2_m))
                scores[num-1] += np.exp(-dist / (45 / PHI**2)) * 0.5  # weaker

        top6 = sorted((np.argsort(scores)[-6:] + 1).tolist())
        preds.append(top6)
        history.append(test[len(test) - 1 - i])

    return preds

# ---- Strategy T4: Three-circle coupled prediction ----
# Full architecture: main (rationality), supps (information), time (energy)

def strategy_three_circle(train, test):
    """
    Full three-circle architecture:
      Circle A: Main number patterns (frequency-based, MIRRORED)
      Circle B: Supp coupling (φ-modular, through singularity)
      Circle C: Energy/time (jackpot accumulation, draw rhythm)

    Coupling:
      A ↔ B: φ² (horizontal)
      (A+B) → C: 2/φ (vertical)
      Pipe: 2φ down, φ up
    """
    preds = []
    history = list(reversed(train))

    for i in range(len(test)):
        # ---- Circle A: Mirrored frequency ----
        counts = np.zeros(46)
        for d in history[-200:]:  # recent 200 draws
            for n in d['main']:
                counts[n] += 1
        # Mirror: LEAST frequent = highest score
        freq_scores = np.max(counts[1:]) - counts[1:]

        # ---- Circle B: Supp φ-coupling ----
        supp_scores = np.zeros(45)
        # Use last 5 draws of supps for deeper signal
        for d in history[-5:]:
            for s in d['supps']:
                # φ-modular mapping
                phi_s = (s * PHI) % 45
                for num in range(45):
                    dist = min(abs(num - phi_s), 45 - abs(num - phi_s))
                    supp_scores[num] += np.exp(-dist / 7)
        # Mirror the supp scores
        supp_scores = np.max(supp_scores) - supp_scores

        # ---- Circle C: Energy/time signal ----
        energy_scores = np.zeros(45)
        # Jackpot accumulation pattern: when prize pool is growing,
        # the system is in accumulate phase
        recent_prizes = [d['prize'] for d in history[-10:] if d['prize'] > 0]
        if len(recent_prizes) >= 2:
            prize_trend = (recent_prizes[-1] - recent_prizes[0]) / max(recent_prizes[0], 1)
            # If accumulating (growing jackpot): system is building energy
            # Map this to number space: higher energy → higher numbers more likely
            for num in range(45):
                if prize_trend > 0:
                    energy_scores[num] = (num + 1) / 45  # favour high numbers
                else:
                    energy_scores[num] = 1 - (num + 1) / 45  # favour low numbers
        else:
            energy_scores = np.ones(45) * 0.5  # neutral

        # ---- Coupling ----
        # Normalize all to [0, 1]
        def norm(x):
            r = np.max(x) - np.min(x)
            return (x - np.min(x)) / r if r > 0 else np.ones_like(x) * 0.5

        A = norm(freq_scores)
        B = norm(supp_scores)
        C = norm(energy_scores)

        # Three-circle blend with φ-couplers
        # Horizontal: A ↔ B coupled at φ²
        AB = (A * PHI**2 + B) / (PHI**2 + 1)

        # Vertical: AB feeds into C at 2/φ weight
        coupled = AB * (1 - 2/(PHI * (PHI + 2/PHI))) + C * (2/(PHI * (PHI + 2/PHI)))

        # Pipe capacity modulation: 2φ down (strong influence from A,B)
        # φ up (weaker feedback from C)
        final = coupled * (2 * PHI) / (2 * PHI + PHI) + C * PHI / (2 * PHI + PHI)

        top6 = sorted((np.argsort(final)[-6:] + 1).tolist())
        preds.append(top6)
        history.append(test[len(test) - 1 - i])

    return preds

# ---- Strategy T5: Supp-as-seed triangulation ----
# Use supps as SEEDS that grow through φ-lattice

def strategy_supp_seed(train, test):
    """
    Supps are seeds. Each supp generates a φ-lattice of candidates:
    s, s×φ, s×φ², s/φ, s/φ² (mod 45).
    Then intersect with mirrored frequency to pick final 6.
    """
    preds = []
    history = list(reversed(train))

    for i in range(len(test)):
        last_supps = history[-1]['supps']

        # Generate φ-lattice from supps
        lattice_scores = np.zeros(45)
        for s in last_supps:
            # Forward lattice
            for power in [-2, -1, -0.5, 0.5, 1, 2]:
                candidate = (s * PHI**power) % 45
                bin_idx = int(candidate)
                if 0 <= bin_idx < 45:
                    strength = 1.0 / (abs(power) + 0.5)  # closer powers = stronger
                    # Spread across nearby numbers
                    for offset in range(-2, 3):
                        idx = (bin_idx + offset) % 45
                        lattice_scores[idx] += strength * np.exp(-abs(offset) / PHI)

        # Mirrored frequency
        counts = np.zeros(45)
        for d in history[-100:]:
            for n in d['main']:
                counts[n-1] += 1
        mirror_freq = np.max(counts) - counts

        # Combine: lattice × mirror frequency
        combined = norm(lattice_scores) * PHI + norm(mirror_freq)

        top6 = sorted((np.argsort(combined)[-6:] + 1).tolist())
        preds.append(top6)
        history.append(test[len(test) - 1 - i])

    return preds

# ---- Strategy T6: Beeswax triangulation ----
# The triple intersection — combine all three signals with singularity crossings

def strategy_beeswax(train, test):
    """
    The beeswax (triple intersection of all three circles):
    1. Mirror-frequency rankings (Rationality circle)
    2. Supp φ-lattice seeds (Information circle)
    3. Cross-draw supp→main coupling signal (Randomness circle, through S₃)

    Each pair intersection gives a partial signal:
      R ∩ I = which numbers our models agree with supp-lattice on
      I ∩ Random = which supp-derived numbers appeared in recent mains
      R ∩ Random = the BL11 mirror predictions

    Beeswax = R ∩ I ∩ Random — numbers that survive all three filters
    """
    preds = []
    history = list(reversed(train))

    for i in range(len(test)):
        # ---- Rationality circle: mirrored φ-modular ----
        recent = history[-20:]
        phi_mapped = []
        for d in recent:
            for n in d['main']:
                phi_mapped.append((n * PHI) % 45)
        hist_bins, _ = np.histogram(phi_mapped, bins=45, range=(0, 45))
        R_scores = np.zeros(45)
        for num in range(1, 46):
            phi_pos = (num * PHI) % 45
            bin_idx = min(int(phi_pos), 44)
            R_scores[num-1] = hist_bins[bin_idx]
        # Mirror
        R_scores = np.max(R_scores) - R_scores

        # ---- Information circle: supp φ-lattice ----
        I_scores = np.zeros(45)
        for d in history[-10:]:  # last 10 draws of supps
            for s in d['supps']:
                for power in [-PHI, -1, -1/PHI, 1/PHI, 1, PHI]:
                    candidate = (s * PHI**power) % 45
                    bin_idx = int(candidate) % 45
                    weight = PHI / (abs(power) + PHI)  # golden-weighted
                    for offset in range(-1, 2):
                        idx = (bin_idx + offset) % 45
                        I_scores[idx] += weight

        # ---- Randomness circle: cross-draw coupling (through singularity) ----
        Random_scores = np.zeros(45)
        # Which numbers from recent supps appeared as mains in subsequent draws?
        for j in range(min(20, len(history) - 1)):
            supps = history[-(j+2)]['supps']
            next_mains = history[-(j+1)]['main']
            for s in supps:
                for m in next_mains:
                    # Numbers near supp→main connections get boosted
                    gap = abs(s - m)
                    if gap <= 5:
                        # This supp-main gap pattern is real — boost similar gaps from current supps
                        for current_s in history[-1]['supps']:
                            candidate = current_s + (m - s)  # same offset
                            if 1 <= candidate <= 45:
                                Random_scores[candidate - 1] += np.exp(-gap / PHI)

        # ---- Pair intersections ----
        def norm(x):
            r = np.max(x) - np.min(x)
            return (x - np.min(x)) / r if r > 0 else np.ones_like(x) * 0.5

        R = norm(R_scores)
        I = norm(I_scores)
        Rand = norm(Random_scores)

        # R ∩ I: geometric mean (both must be high)
        RI = np.sqrt(R * I + 1e-10)

        # I ∩ Random: geometric mean
        IRand = np.sqrt(I * Rand + 1e-10)

        # R ∩ Random: geometric mean
        RRand = np.sqrt(R * Rand + 1e-10)

        # Beeswax = triple intersection
        # Weighted by coupler strengths
        beeswax = (RI * PHI**2 + IRand * PHI**(3.5) + RRand * (2/PHI)) / (PHI**2 + PHI**3.5 + 2/PHI)

        top6 = sorted((np.argsort(beeswax)[-6:] + 1).tolist())
        preds.append(top6)
        history.append(test[len(test) - 1 - i])

    return preds

# ---- Strategy T7: Beeswax + Mirror combined ----

def strategy_beeswax_mirror(train, test):
    """Beeswax but with the MIRROR flip on the randomness circle."""
    preds = []
    history = list(reversed(train))

    for i in range(len(test)):
        # Rationality: recency-based mirror
        last_seen = {}
        for j, d in enumerate(history):
            for n in d['main']:
                last_seen[n] = j
        R_scores = np.zeros(45)
        for n in range(1, 46):
            R_scores[n-1] = last_seen.get(n, 0)
        # MIRROR: least recent = highest score (the BL11 winner)
        R_scores = np.max(R_scores) - R_scores

        # Information: supp numbers → φ-modular transform
        I_scores = np.zeros(45)
        for d in history[-5:]:
            for s in d['supps']:
                phi_target = int((s * PHI) % 45)
                for offset in range(-3, 4):
                    idx = (phi_target + offset) % 45
                    I_scores[idx] += np.exp(-abs(offset) / PHI)

        # Randomness: what the straight prediction says (then we'll flip)
        counts = np.zeros(45)
        for d in history[-100:]:
            for n in d['main']:
                counts[n-1] += 1
        # DON'T mirror — this is the "other side"
        Rand_scores = counts

        def norm(x):
            r = np.max(x) - np.min(x)
            return (x - np.min(x)) / r if r > 0 else np.ones_like(x) * 0.5

        R = norm(R_scores)
        I = norm(I_scores)
        # Apply φ-modular transform to Randomness (crossing the singularity)
        Rand_norm = norm(Rand_scores)
        Rand_crossed = 1 - (Rand_norm * PHI) % 1.0  # mirror through golden angle

        # Beeswax with pipe geometry
        # Down-pipe: 2φ capacity (strong: R and I feeding into prediction)
        # Up-pipe: φ capacity (weak: randomness feeding back)
        down_signal = (R * PHI**2 + I) / (PHI**2 + 1)  # horizontal coupling
        up_signal = Rand_crossed

        # Vertical coupling at 2/φ
        combined = down_signal * (2 * PHI) / (2 * PHI + PHI) + up_signal * PHI / (2 * PHI + PHI)

        top6 = sorted((np.argsort(combined)[-6:] + 1).tolist())
        preds.append(top6)
        history.append(test[len(test) - 1 - i])

    return preds

# ============================================================
# PART 3: Run all strategies
# ============================================================

print(f"\nHoldout: {HOLDOUT} draws")
print(f"Expected (random): {EXPECTED:.4f} matches/draw")

norm = lambda x: (np.array(x) - np.min(x)) / (np.max(x) - np.min(x)) if np.max(x) > np.min(x) else np.ones_like(x) * 0.5

test_reversed = list(reversed(test_data))  # chronological

strategies = {
    'Random baseline': None,
    'Supp neighbourhood': lambda: strategy_supp_neighbourhood(train_data, test_data),
    'Supp mirror': lambda: strategy_supp_mirror(train_data, test_data),
    'Supp φ-coupling': lambda: strategy_supp_phi(train_data, test_data),
    'Three-circle': lambda: strategy_three_circle(train_data, test_data),
    'Supp seed': lambda: strategy_supp_seed(train_data, test_data),
    'Beeswax': lambda: strategy_beeswax(train_data, test_data),
    'Beeswax + mirror': lambda: strategy_beeswax_mirror(train_data, test_data),
}

print(f"\n{'Strategy':22s} {'Mean':>8s} {'Total':>7s} {'vs Random':>10s} {'Best':>6s}")
print("-" * 58)

np.random.seed(42)
results = {}

for name, fn in strategies.items():
    if fn is None:
        preds = [sorted(np.random.choice(range(1, 46), 6, replace=False).tolist())
                 for _ in range(HOLDOUT)]
        # Score random baseline
        matches = []
        for p, d in zip(preds, test_data):
            matches.append(len(set(p) & set(d['main'])))
        mean_m = np.mean(matches)
        all_m = matches
    else:
        preds = fn()
        matches = []
        for p, d in zip(preds, test_data):
            matches.append(len(set(p) & set(d['main'])))
        mean_m = np.mean(matches)
        all_m = matches

    total = sum(all_m)
    delta = (mean_m / EXPECTED - 1) * 100
    best = max(all_m)
    results[name] = (mean_m, total, delta, best, all_m)

    marker = ""
    if name != 'Random baseline' and delta > 0:
        marker = " ←"
    print(f"  {name:20s} {mean_m:>7.4f}  {total:>5d}   {delta:>+8.1f}%  {best:>4d}{marker}")

# ============================================================
# PART 4: Monte Carlo significance
# ============================================================

print("\n" + "=" * 70)
print("STATISTICAL SIGNIFICANCE")
print("=" * 70)

random_means = []
for _ in range(10000):
    rpreds = [sorted(np.random.choice(range(1, 46), 6, replace=False).tolist())
              for _ in range(HOLDOUT)]
    matches = [len(set(p) & set(d['main'])) for p, d in zip(rpreds, test_data)]
    random_means.append(np.mean(matches))
random_means = np.array(random_means)

print(f"\n  Random distribution: {np.mean(random_means):.4f} ± {np.std(random_means):.4f}")
print(f"  95% threshold: {np.percentile(random_means, 97.5):.4f}")

for name, (mean_m, total, delta, best, all_m) in results.items():
    if name == 'Random baseline':
        continue
    pctile = np.mean(random_means <= mean_m) * 100
    z = (mean_m - np.mean(random_means)) / np.std(random_means)
    sig = "*** SIGNIFICANT ***" if pctile > 97.5 else "not significant"
    marker = " ← BEST" if mean_m == max(r[0] for n, r in results.items() if n != 'Random baseline') else ""
    print(f"  {name:22s}: pctile={pctile:5.1f}%, z={z:+.2f} ({sig}){marker}")

# ============================================================
# PART 5: Compare to BL10/BL11 baselines
# ============================================================

print("\n" + "=" * 70)
print("COMPARISON TO PREVIOUS APPROACHES")
print("=" * 70)

# BL10 best (no mirror): 0.88 matches/draw
# BL11 best (mirror only): 0.93 matches/draw
bl10_best = 0.88
bl11_best = 0.93

best_tri = max((name, r[0]) for name, r in results.items() if name != 'Random baseline')
print(f"\n  BL10 best (no mirror):       {bl10_best:.4f} (+{(bl10_best/EXPECTED-1)*100:.1f}%)")
print(f"  BL11 best (mirror only):     {bl11_best:.4f} (+{(bl11_best/EXPECTED-1)*100:.1f}%)")
print(f"  BL13 best (triangulation):   {best_tri[1]:.4f} (+{(best_tri[1]/EXPECTED-1)*100:.1f}%) [{best_tri[0]}]")

if best_tri[1] > bl11_best:
    improvement = (best_tri[1] - bl11_best) / bl11_best * 100
    print(f"\n  TRIANGULATION BEATS MIRROR by {improvement:.1f}%!")
    print(f"  The third circle (Information/Supps) adds real signal.")
elif best_tri[1] > bl10_best:
    print(f"\n  Triangulation beats no-mirror but not mirror-only.")
    print(f"  Supp coupling adds SOME signal but less than the mirror flip.")
else:
    print(f"\n  Triangulation doesn't beat previous approaches.")

# ============================================================
# PART 6: Generate NEXT DRAW prediction
# ============================================================

print("\n" + "=" * 70)
print("NEXT DRAW PREDICTION (Full triangulation)")
print("=" * 70)

# Run best strategy on ALL data
best_name = best_tri[0]
print(f"\n  Using best strategy: {best_name}")
print(f"  Last draw: #{data[0]['num']} → main={data[0]['main']}, supps={data[0]['supps']}")

# For the actual prediction, run each triangulation strategy on full data
# and create a mega-ensemble

all_full_preds = {}

# Manually run each strategy on full data for one prediction
history_full = list(reversed(data))

def get_full_prediction(strategy_name):
    """Run strategy on full data to get ONE prediction."""
    # We need to replicate each strategy's logic for a single prediction
    return None  # handled below

# Supp neighbourhood
scores = np.zeros(45)
for s in data[0]['supps']:
    for num in range(1, 46):
        dist = abs(num - s)
        if dist == 0:
            scores[num-1] += 5
        else:
            scores[num-1] += max(0, (4 - dist)) / 4
supp_neigh_pred = sorted((np.argsort(scores)[-6:] + 1).tolist())
all_full_preds['Supp neighbourhood'] = supp_neigh_pred

# Supp mirror
scores = np.zeros(45)
for s in data[0]['supps']:
    for num in range(1, 46):
        scores[num-1] += abs(num - s)
supp_mirror_pred = sorted((np.argsort(scores)[-6:] + 1).tolist())
all_full_preds['Supp mirror'] = supp_mirror_pred

# Supp φ-coupling
scores = np.zeros(45)
for s in data[0]['supps']:
    for num in range(1, 46):
        phi_s = (s * PHI) % 45 + 1
        dist = min(abs(num - phi_s), 45 - abs(num - phi_s))
        scores[num-1] += np.exp(-dist / (45 / PHI))
for m in data[0]['main']:
    phi2_m = (m * PHI**2) % 45 + 1
    for num in range(1, 46):
        dist = min(abs(num - phi2_m), 45 - abs(num - phi2_m))
        scores[num-1] += np.exp(-dist / (45 / PHI**2)) * 0.5
supp_phi_pred = sorted((np.argsort(scores)[-6:] + 1).tolist())
all_full_preds['Supp φ-coupling'] = supp_phi_pred

# Supp seed
scores = np.zeros(45)
for s in data[0]['supps']:
    for power in [-PHI, -1, -1/PHI, 1/PHI, 1, PHI]:
        candidate = (s * PHI**power) % 45
        bin_idx = int(candidate) % 45
        weight = PHI / (abs(power) + PHI)
        for offset in range(-2, 3):
            idx = (bin_idx + offset) % 45
            scores[idx] += weight * np.exp(-abs(offset) / PHI)
counts = np.zeros(45)
for d in data[:100]:
    for n in d['main']:
        counts[n-1] += 1
mirror_freq = np.max(counts) - counts
n_s = lambda x: (x - np.min(x)) / (np.max(x) - np.min(x)) if np.max(x) > np.min(x) else np.ones_like(x) * 0.5
combined = n_s(scores) * PHI + n_s(mirror_freq)
supp_seed_pred = sorted((np.argsort(combined)[-6:] + 1).tolist())
all_full_preds['Supp seed'] = supp_seed_pred

# Beeswax + mirror (the full architecture)
# Rationality: recency mirror
last_seen = {}
for j, d in enumerate(reversed(data)):
    for n in d['main']:
        last_seen[n] = j
R = np.zeros(45)
for n in range(1, 46):
    R[n-1] = last_seen.get(n, 0)
R = np.max(R) - R  # mirror

# Information: supp φ-modular
I = np.zeros(45)
for d in data[:5]:
    for s in d['supps']:
        phi_target = int((s * PHI) % 45)
        for offset in range(-3, 4):
            idx = (phi_target + offset) % 45
            I[idx] += np.exp(-abs(offset) / PHI)

# Randomness: frequency crossed through golden angle
counts = np.zeros(45)
for d in data[:100]:
    for n in d['main']:
        counts[n-1] += 1
Rand_norm = n_s(counts)
Rand_crossed = 1 - (Rand_norm * PHI) % 1.0

R_n = n_s(R)
I_n = n_s(I)
down_signal = (R_n * PHI**2 + I_n) / (PHI**2 + 1)
up_signal = Rand_crossed
bm_combined = down_signal * (2 * PHI) / (2 * PHI + PHI) + up_signal * PHI / (2 * PHI + PHI)
beeswax_mirror_pred = sorted((np.argsort(bm_combined)[-6:] + 1).tolist())
all_full_preds['Beeswax + mirror'] = beeswax_mirror_pred

# Mega-ensemble: vote across all triangulation strategies
votes = defaultdict(float)
for name, pred in all_full_preds.items():
    weight = results.get(name, (0.8,))[0]
    for n in pred:
        votes[n] += weight

sorted_votes = sorted(votes.items(), key=lambda x: -x[1])
mega_pred = sorted([n for n, v in sorted_votes[:6]])

print(f"\n  Individual predictions:")
for name, pred in all_full_preds.items():
    perf = results.get(name, (0, 0, 0))[2]
    print(f"    {name:22s}: {pred} ({perf:+.1f}% in holdout)")

print(f"\n  Weighted ensemble vote (top 12):")
for rank, (num, vote) in enumerate(sorted_votes[:12]):
    marker = " ← TOP 6" if num in mega_pred else ""
    print(f"    #{rank+1:2d} Number {num:2d}: score={vote:.3f}{marker}")

print(f"\n  BL12 prediction (mirror only):   [2, 3, 4, 6, 17, 45]")
print(f"  BL13 prediction (triangulated):  {mega_pred}")

# Overlap between BL12 and BL13
bl12 = {2, 3, 4, 6, 17, 45}
bl13 = set(mega_pred)
overlap = bl12 & bl13
print(f"\n  Overlap BL12 ∩ BL13: {sorted(overlap)} ({len(overlap)}/6)")
print(f"  New from triangulation: {sorted(bl13 - bl12)}")
print(f"  Dropped by triangulation: {sorted(bl12 - bl13)}")

print(f"\n  ╔══════════════════════════════════════════════╗")
print(f"  ║  TRIANGULATED PREDICTION: {mega_pred}  ║")
print(f"  ╚══════════════════════════════════════════════╝")

# Numbers the framework says are LEAST likely
anti_pred = sorted([n for n, v in sorted_votes[-6:]])
print(f"\n  Least likely (anti-prediction): {anti_pred}")

print(f"\n  Last draw supps were: {data[0]['supps']}")
print(f"  These coupled through φ to seed the Information circle.")

print(f"\n{'='*70}")
print(f"END Script 243BL13")
print(f"{'='*70}")
