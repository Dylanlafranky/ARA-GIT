"""
Script 243BL16: The ARA of Prime Numbers
========================================

We showed random numbers = ARA 1.0 (perfect shock absorbers).
We showed the S&P 500 = ARA 0.930 (mild consumer).
Now: what is the ARA of the PRIMES?

Primes have a famous dual nature:
  - Globally: they follow the Prime Number Theorem (structure)
  - Locally: their gaps look almost random (noise)

This is EXACTLY the kind of system ARA should characterize.
If primes are ARA 1.0, they're just noise — indistinguishable from random.
If they're > 1.0, they're engines — self-sustaining structure.
If they're < 1.0, they're consumers — structure that depletes.

Tests:
  1. Compute ARA of prime gaps (consecutive gaps between primes)
  2. Compare to random gap sequences with same statistical properties
  3. φ-modular transform — does it dissolve or disrupt structure?
  4. φ-power periodicities — do gaps echo at φ-power intervals?
  5. Mirror flip — does inverting predictions through singularity help?
  6. Scale-dependent ARA — does the ARA change as primes get larger?
  7. Gap-specific ARA — do small gaps vs large gaps have different signatures?
"""

import numpy as np
from collections import defaultdict, Counter
import time

PHI = (1 + np.sqrt(5)) / 2
CROSSING_COST = (7 - 4*PHI) / 4

# ============================================================
# Generate primes via sieve
# ============================================================

def sieve_of_eratosthenes(limit):
    """Generate all primes up to limit."""
    is_prime = np.ones(limit + 1, dtype=bool)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i*i::i] = False
    return np.where(is_prime)[0]

print("=" * 70)
print("Script 243BL16: THE ARA OF PRIME NUMBERS")
print("=" * 70)

# Generate primes up to 10M (~664k primes — plenty for statistics)
t0 = time.time()
LIMIT = 10_000_000
primes = sieve_of_eratosthenes(LIMIT)
gaps = np.diff(primes)
print(f"\nGenerated {len(primes):,} primes up to {LIMIT:,} in {time.time()-t0:.1f}s")
print(f"Prime gaps: {len(gaps):,}")
print(f"First 20 gaps: {list(gaps[:20])}")
print(f"Mean gap: {np.mean(gaps):.4f}")
print(f"Std gap:  {np.std(gaps):.4f}")
print(f"Max gap:  {np.max(gaps)}")
print(f"Median gap: {np.median(gaps):.1f}")

# ============================================================
# PART 1: Global ARA of prime gaps
# ============================================================

print("\n" + "=" * 70)
print("PART 1: GLOBAL ARA OF PRIME GAPS")
print("=" * 70)

def compute_ara_discrete(series):
    """ARA from consecutive comparisons (ups vs downs)."""
    ups = 0
    downs = 0
    for i in range(len(series) - 1):
        if series[i+1] > series[i]:
            ups += 1
        elif series[i+1] < series[i]:
            downs += 1
    if downs == 0:
        return 2.0
    return ups / downs

def compute_ara_continuous(series):
    """Magnitude-weighted ARA (accumulation vs release energy)."""
    deltas = np.diff(series.astype(float))
    acc = np.sum(np.abs(deltas[deltas > 0]))  # gaps getting bigger = accumulation
    rel = np.sum(np.abs(deltas[deltas < 0]))  # gaps getting smaller = release
    if rel == 0:
        return 2.0
    if acc == 0:
        return 0.0
    return acc / rel

# Full dataset ARA
ara_discrete = compute_ara_discrete(gaps)
ara_continuous = compute_ara_continuous(gaps)

print(f"\n  Prime gaps ARA (discrete):   {ara_discrete:.6f}")
print(f"  Prime gaps ARA (continuous): {ara_continuous:.6f}")

# Classify
def classify_ara(ara):
    if ara < 0.85:
        return "CONSUMER"
    elif ara < 1.15:
        return "SHOCK ABSORBER"
    elif ara < PHI - 0.1:
        return "warm engine"
    elif ara < PHI + 0.1:
        return "φ-ENGINE"
    else:
        return "hot engine"

print(f"\n  Classification (discrete):   {classify_ara(ara_discrete)}")
print(f"  Classification (continuous): {classify_ara(ara_continuous)}")

# Compare to baselines
print(f"\n  ┌─────────────────────────────┬──────────┬──────────┐")
print(f"  │ System                      │ Discrete │ Contin.  │")
print(f"  ├─────────────────────────────┼──────────┼──────────┤")
print(f"  │ Lotto numbers (ARA=1.0)     │  1.000   │  1.000   │")
print(f"  │ S&P 500 returns             │  0.930   │  0.930   │")
print(f"  │ PRIME GAPS                  │  {ara_discrete:.4f}  │  {ara_continuous:.4f}  │")
print(f"  └─────────────────────────────┴──────────┴──────────┘")

# ============================================================
# PART 2: Statistical significance — primes vs random
# ============================================================

print("\n" + "=" * 70)
print("PART 2: PRIMES vs RANDOM — IS THE ARA DIFFERENT?")
print("=" * 70)

# Generate random gap sequences with same length and similar distribution
N_SIMS = 200
random_aras_d = []
random_aras_c = []

# Match the prime gap distribution (geometric-like, but we use shuffled primes)
for _ in range(N_SIMS):
    # Method 1: Shuffle actual prime gaps (preserves distribution, destroys order)
    shuffled = gaps.copy()
    np.random.shuffle(shuffled)
    random_aras_d.append(compute_ara_discrete(shuffled))
    random_aras_c.append(compute_ara_continuous(shuffled))

random_aras_d = np.array(random_aras_d)
random_aras_c = np.array(random_aras_c)

z_discrete = (ara_discrete - np.mean(random_aras_d)) / np.std(random_aras_d)
z_continuous = (ara_continuous - np.mean(random_aras_c)) / np.std(random_aras_c)

print(f"\n  Shuffled gaps baseline (N={N_SIMS}):")
print(f"    Discrete:   {np.mean(random_aras_d):.6f} ± {np.std(random_aras_d):.6f}")
print(f"    Continuous: {np.mean(random_aras_c):.6f} ± {np.std(random_aras_c):.6f}")
print(f"\n  Prime gap ARA vs shuffled:")
print(f"    Discrete z-score:   {z_discrete:+.2f}")
print(f"    Continuous z-score: {z_continuous:+.2f}")

if abs(z_discrete) > 2 or abs(z_continuous) > 2:
    print(f"\n  *** PRIMES ARE SIGNIFICANTLY DIFFERENT FROM RANDOM ***")
    if ara_discrete > np.mean(random_aras_d):
        print(f"      Primes have MORE structure than shuffled gaps (engine-like)")
    else:
        print(f"      Primes have LESS structure than shuffled gaps (consumer-like)")
else:
    print(f"\n  Primes are NOT significantly different from shuffled gaps")
    print(f"  (Same distribution, order doesn't matter)")

# Also test against truly random (exponential gaps matching mean)
print(f"\n  Also testing against truly random (exponential distribution):")
exp_aras_d = []
exp_aras_c = []
for _ in range(N_SIMS):
    exp_gaps = np.random.exponential(scale=np.mean(gaps), size=len(gaps)).astype(int)
    exp_gaps = np.maximum(exp_gaps, 1)  # min gap 1
    # Round to nearest even (prime gaps > 2 are always even)
    exp_gaps[exp_gaps > 2] = ((exp_gaps[exp_gaps > 2] + 1) // 2) * 2
    exp_aras_d.append(compute_ara_discrete(exp_gaps))
    exp_aras_c.append(compute_ara_continuous(exp_gaps))

exp_aras_d = np.array(exp_aras_d)
exp_aras_c = np.array(exp_aras_c)

z_exp_d = (ara_discrete - np.mean(exp_aras_d)) / np.std(exp_aras_d)
z_exp_c = (ara_continuous - np.mean(exp_aras_c)) / np.std(exp_aras_c)

print(f"    Exponential baseline:   {np.mean(exp_aras_d):.6f} ± {np.std(exp_aras_d):.6f}")
print(f"    Discrete z-score:       {z_exp_d:+.2f}")
print(f"    Continuous z-score:     {z_exp_c:+.2f}")

# ============================================================
# PART 3: Scale-dependent ARA — does it change with prime size?
# ============================================================

print("\n" + "=" * 70)
print("PART 3: SCALE-DEPENDENT ARA — DOES IT CHANGE?")
print("=" * 70)

# Split primes into decades
n_chunks = 10
chunk_size = len(gaps) // n_chunks

print(f"\n  {'Chunk':<8s} {'Primes from':<20s} {'Mean gap':>9s} {'ARA(d)':>8s} {'ARA(c)':>8s} {'Type':>14s}")
print(f"  {'─'*70}")

scale_aras_d = []
scale_aras_c = []
scale_labels = []

for i in range(n_chunks):
    start = i * chunk_size
    end = (i + 1) * chunk_size if i < n_chunks - 1 else len(gaps)
    chunk_gaps = gaps[start:end]
    chunk_primes = primes[start:end+1]

    ad = compute_ara_discrete(chunk_gaps)
    ac = compute_ara_continuous(chunk_gaps)
    scale_aras_d.append(ad)
    scale_aras_c.append(ac)
    scale_labels.append(f"{chunk_primes[0]:,}-{chunk_primes[-1]:,}")

    print(f"  {i+1:<8d} {chunk_primes[0]:>9,}-{chunk_primes[-1]:>9,} {np.mean(chunk_gaps):>9.2f} {ad:>8.4f} {ac:>8.4f} {classify_ara(ac):>14s}")

# Trend analysis
from numpy.polynomial import polynomial as P
x = np.arange(n_chunks)
# Linear fit
coeffs_d = np.polyfit(x, scale_aras_d, 1)
coeffs_c = np.polyfit(x, scale_aras_c, 1)

print(f"\n  ARA trend with prime size:")
print(f"    Discrete slope:   {coeffs_d[0]:+.6f} per decade")
print(f"    Continuous slope: {coeffs_c[0]:+.6f} per decade")

if abs(coeffs_c[0]) > 0.005:
    direction = "increasing (toward engine)" if coeffs_c[0] > 0 else "decreasing (toward consumer)"
    print(f"    → ARA is {direction} as primes get larger")
else:
    print(f"    → ARA is STABLE across scales")

# ============================================================
# PART 4: φ-modular transform — dissolve or disrupt?
# ============================================================

print("\n" + "=" * 70)
print("PART 4: φ-MODULAR TRANSFORM — DISSOLVE OR DISRUPT?")
print("=" * 70)

# Rank-transform gaps to [0,1], then apply φ-modular
from scipy import stats as scipy_stats

ranked = scipy_stats.rankdata(gaps) / len(gaps)

# Chi-squared uniformity test
n_bins = 20
expected = len(gaps) / n_bins

hist_orig, _ = np.histogram(ranked, bins=n_bins, range=(0, 1))
chi2_orig = sum((h - expected)**2 / expected for h in hist_orig)

# φ-modular transform
phi_mapped = (ranked * PHI) % 1.0
hist_phi, _ = np.histogram(phi_mapped, bins=n_bins, range=(0, 1))
chi2_phi = sum((h - expected)**2 / expected for h in hist_phi)

change_pct = (chi2_phi / chi2_orig - 1) * 100 if chi2_orig > 0 else 0

print(f"\n  Rank-transformed gaps:")
print(f"    Original χ²:    {chi2_orig:.2f} (df={n_bins-1})")
print(f"    After φ-map χ²: {chi2_phi:.2f}")
print(f"    Change:          {change_pct:+.1f}%")

# Also test on raw gaps (not ranked)
gap_norm = (gaps - gaps.min()) / (gaps.max() - gaps.min())
hist_raw, _ = np.histogram(gap_norm, bins=n_bins, range=(0, 1))
chi2_raw = sum((h - expected)**2 / expected for h in hist_raw)

phi_raw = (gap_norm * PHI) % 1.0
hist_phi_raw, _ = np.histogram(phi_raw, bins=n_bins, range=(0, 1))
chi2_phi_raw = sum((h - expected)**2 / expected for h in hist_phi_raw)

raw_change = (chi2_phi_raw / chi2_raw - 1) * 100 if chi2_raw > 0 else 0

print(f"\n  Raw gaps (normalized):")
print(f"    Original χ²: {chi2_raw:.2f}")
print(f"    After φ-map: {chi2_phi_raw:.2f} ({raw_change:+.1f}%)")

# Comparison table
print(f"\n  ┌─────────────────────────┬────────────┬────────────────────────────┐")
print(f"  │ System                  │ φ-mod Δχ²  │ Interpretation             │")
print(f"  ├─────────────────────────┼────────────┼────────────────────────────┤")
print(f"  │ Lotto (hidden struct)   │ -65 to -82%│ φ DISSOLVES hidden order   │")
print(f"  │ S&P 500 (visible)       │ +581,804%  │ φ DESTROYS visible struct  │")
print(f"  │ PRIMES (ranked)         │ {change_pct:>+9.1f}% │ {'DISSOLVES' if change_pct < -20 else 'DISRUPTS' if change_pct > 20 else 'MINIMAL EFFECT':<26s} │")
print(f"  │ PRIMES (raw)            │ {raw_change:>+9.1f}% │ {'DISSOLVES' if raw_change < -20 else 'DISRUPTS' if raw_change > 20 else 'MINIMAL EFFECT':<26s} │")
print(f"  └─────────────────────────┴────────────┴────────────────────────────┘")

# ============================================================
# PART 5: φ-power periodicities in prime gaps
# ============================================================

print("\n" + "=" * 70)
print("PART 5: φ-POWER PERIODICITIES")
print("=" * 70)

# Test: does gap[n] correlate with gap[n + φ^k]?
# Use φ¹ through φ⁹
print(f"\n  Testing autocorrelation at φ-power lags:")
print(f"  {'Power':>6s} {'Lag':>8s} {'Corr':>8s} {'p-value':>10s} {'vs random':>10s}")
print(f"  {'─'*50}")

# Use a large sample for statistical power
sample_gaps = gaps[:1_000_000]  # first million gaps

phi_corrs = []
for power in range(1, 10):
    lag = int(round(PHI ** power))
    if lag >= len(sample_gaps):
        break

    # Autocorrelation at this lag
    n = len(sample_gaps) - lag
    x = sample_gaps[:n].astype(float)
    y = sample_gaps[lag:lag+n].astype(float)

    corr = np.corrcoef(x, y)[0, 1]

    # Compare to nearby integer lags
    nearby_corrs = []
    for offset in [-2, -1, 1, 2]:
        nearby_lag = lag + offset
        if nearby_lag > 0 and nearby_lag < len(sample_gaps):
            nn = len(sample_gaps) - nearby_lag
            xx = sample_gaps[:nn].astype(float)
            yy = sample_gaps[nearby_lag:nearby_lag+nn].astype(float)
            nearby_corrs.append(np.corrcoef(xx, yy)[0, 1])

    avg_nearby = np.mean(nearby_corrs) if nearby_corrs else 0
    relative = corr / avg_nearby if avg_nearby != 0 else float('inf')

    phi_corrs.append((power, lag, corr, avg_nearby, relative))
    sig = "***" if abs(corr) > 0.01 else ""
    print(f"  φ^{power:<4d} {lag:>8d} {corr:>+8.5f}   vs nearby: {avg_nearby:>+8.5f}  ratio: {relative:.3f} {sig}")

# ============================================================
# PART 6: Gap distribution — Cramér's conjecture & ARA
# ============================================================

print("\n" + "=" * 70)
print("PART 6: GAP DISTRIBUTION — WHERE IS THE STRUCTURE?")
print("=" * 70)

# Gap size distribution
gap_counts = Counter(gaps)
total_gaps = len(gaps)

print(f"\n  Most common gaps:")
for gap_val, count in sorted(gap_counts.items(), key=lambda x: -x[1])[:15]:
    pct = count / total_gaps * 100
    bar = "█" * int(pct * 2)
    print(f"    Gap {gap_val:>3d}: {count:>7,} ({pct:>5.2f}%) {bar}")

# ARA by gap SIZE — do small gaps have different ARA than large gaps?
print(f"\n  ARA by gap size class:")
print(f"  {'Gap class':<16s} {'Count':>8s} {'ARA(d)':>8s} {'ARA(c)':>8s} {'Type':>14s}")
print(f"  {'─'*58}")

# Classify gaps and compute ARA of the SEQUENCE of each class
gap_classes = [
    ("Twin (2)", 2, 2),
    ("Cousin (4)", 4, 4),
    ("Sexy (6)", 6, 6),
    ("Small (2-6)", 2, 6),
    ("Medium (8-18)", 8, 18),
    ("Large (20-50)", 20, 50),
    ("Very large (52+)", 52, 500),
]

for name, lo, hi in gap_classes:
    # Get positions where gaps of this size occur
    positions = np.where((gaps >= lo) & (gaps <= hi))[0]
    if len(positions) < 10:
        continue

    # The gap sequence BETWEEN occurrences of this gap class
    inter_gaps = np.diff(positions)
    if len(inter_gaps) < 4:
        continue

    ad = compute_ara_discrete(inter_gaps)
    ac = compute_ara_continuous(inter_gaps)

    print(f"  {name:<16s} {len(positions):>8,} {ad:>8.4f} {ac:>8.4f} {classify_ara(ac):>14s}")

# ============================================================
# PART 7: Predictability test — can we predict the next gap?
# ============================================================

print("\n" + "=" * 70)
print("PART 7: GAP PREDICTION — CAN ARA SEE FORWARD?")
print("=" * 70)

# Use last 100,000 gaps as test set
TEST_SIZE = 100_000
train_gaps = gaps[:-TEST_SIZE]
test_gaps = gaps[-TEST_SIZE:]

# Strategy 1: Always predict median gap
median_gap = np.median(train_gaps)
pred_median = np.full(TEST_SIZE, median_gap)
mae_median = np.mean(np.abs(test_gaps - pred_median))

# Strategy 2: Last gap repeats
pred_last = gaps[-(TEST_SIZE+1):-1]
mae_last = np.mean(np.abs(test_gaps - pred_last))

# Strategy 3: Moving average
window = 10
pred_ma = []
for i in range(TEST_SIZE):
    idx = len(train_gaps) + i
    recent = gaps[max(0, idx-window):idx]
    pred_ma.append(np.mean(recent))
pred_ma = np.array(pred_ma)
mae_ma = np.mean(np.abs(test_gaps - pred_ma))

# Strategy 4: φ-weighted moving average
pred_phi = []
for i in range(TEST_SIZE):
    idx = len(train_gaps) + i
    recent = gaps[max(0, idx-window):idx]
    # φ-weights: most recent gets φ^0, next gets φ^-1, etc.
    weights = np.array([PHI**(-j) for j in range(len(recent))])
    weights = weights[::-1]  # most recent last
    weights /= weights.sum()
    pred_phi.append(np.sum(recent * weights))
pred_phi = np.array(pred_phi)
mae_phi = np.mean(np.abs(test_gaps - pred_phi))

# Strategy 5: Mirror prediction (invert through ARA singularity)
# If recent trend is "gaps growing", predict "gap shrinking" (and vice versa)
pred_mirror = []
for i in range(TEST_SIZE):
    idx = len(train_gaps) + i
    recent = gaps[max(0, idx-window):idx].astype(float)
    # Recent trend
    if len(recent) >= 2:
        trend = recent[-1] - recent[-2]
        # Mirror: predict opposite direction from median
        mirror_val = median_gap - trend * (1 - CROSSING_COST)
        pred_mirror.append(max(1, mirror_val))
    else:
        pred_mirror.append(median_gap)
pred_mirror = np.array(pred_mirror)
mae_mirror = np.mean(np.abs(test_gaps - pred_mirror))

# Strategy 6: ARA-regime prediction
pred_ara = []
for i in range(TEST_SIZE):
    idx = len(train_gaps) + i
    chunk = gaps[max(0, idx-50):idx]
    if len(chunk) < 10:
        pred_ara.append(median_gap)
        continue
    ara = compute_ara_discrete(chunk)
    if ara > 1.1:  # engine = gaps systematically growing
        pred_ara.append(chunk[-1] * 1.05)  # expect continued growth
    elif ara < 0.9:  # consumer = gaps systematically shrinking
        pred_ara.append(chunk[-1] * 0.95)
    else:  # absorber = mean-reverting
        pred_ara.append(np.mean(chunk))
pred_ara = np.array(pred_ara)
mae_ara = np.mean(np.abs(test_gaps - pred_ara))

# Strategy 7: φ-cycle prediction
pred_phi_cycle = []
for i in range(TEST_SIZE):
    idx = len(train_gaps) + i
    score = 0
    count = 0
    for power in [2, 3, 5, 7]:
        lag = int(round(PHI ** power))
        if idx >= lag:
            score += gaps[idx - lag]
            count += 1
    pred_phi_cycle.append(score / count if count > 0 else median_gap)
pred_phi_cycle = np.array(pred_phi_cycle)
mae_phi_cycle = np.mean(np.abs(test_gaps - pred_phi_cycle))

# Direction accuracy (predict whether next gap is bigger or smaller)
print(f"\n  Gap prediction MAE (test = last {TEST_SIZE:,} gaps):")
print(f"  {'Strategy':<28s} {'MAE':>8s} {'vs median':>10s}")
print(f"  {'─'*50}")

strategies_mae = [
    ("Always median", mae_median),
    ("Last gap repeats", mae_last),
    ("Moving average (10)", mae_ma),
    ("φ-weighted MA", mae_phi),
    ("Mirror prediction", mae_mirror),
    ("ARA regime", mae_ara),
    ("φ-cycle echo", mae_phi_cycle),
]

for name, mae in strategies_mae:
    vs = (mae / mae_median - 1) * 100
    marker = " ←" if mae < mae_median else ""
    print(f"  {name:<28s} {mae:>8.3f} {vs:>+9.1f}%{marker}")

# Direction accuracy
print(f"\n  Direction prediction (up/down from current gap):")
print(f"  {'Strategy':<28s} {'Accuracy':>8s} {'z-score':>8s}")
print(f"  {'─'*48}")

actual_dirs = (test_gaps[1:] > test_gaps[:-1]).astype(int)

def direction_accuracy(preds, actual_gaps):
    """Does prediction correctly anticipate gap direction?"""
    pred_dirs = (preds[1:] > actual_gaps[:-1]).astype(int)
    actual_d = (actual_gaps[1:] > actual_gaps[:-1]).astype(int)
    return np.mean(pred_dirs == actual_d)

base_rate = np.mean(actual_dirs)  # natural up rate
n_test = len(actual_dirs)

for name, pred in [("Moving average", pred_ma), ("φ-weighted MA", pred_phi),
                    ("Mirror", pred_mirror), ("ARA regime", pred_ara),
                    ("φ-cycle echo", pred_phi_cycle)]:
    acc = direction_accuracy(pred, test_gaps)
    z = (acc - 0.5) / np.sqrt(0.25 / n_test)
    sig = " ***" if abs(z) > 3 else " *" if abs(z) > 2 else ""
    print(f"  {name:<28s} {acc*100:>7.2f}% {z:>+7.2f}{sig}")

print(f"\n  Base direction rate (gap grows): {base_rate*100:.1f}%")

# ============================================================
# PART 8: The Fibonacci connection
# ============================================================

print("\n" + "=" * 70)
print("PART 8: FIBONACCI CONNECTION")
print("=" * 70)

# How many prime gaps are Fibonacci numbers?
fibs = set()
a, b = 1, 1
while b <= np.max(gaps):
    fibs.add(b)
    a, b = b, a + b

fib_gap_count = sum(1 for g in gaps if g in fibs)
fib_gap_pct = fib_gap_count / len(gaps) * 100

# Expected if random
unique_gaps = sorted(set(gaps))
fib_in_range = [f for f in fibs if f in set(gaps)]
expected_pct = sum(gap_counts.get(f, 0) for f in fibs) / len(gaps) * 100

# Actually, let's ask a better question: are Fibonacci-valued gaps
# more or less common than expected by the gap distribution?
print(f"\n  Fibonacci numbers in gap range: {sorted(fibs & set(gaps.tolist()))}")
print(f"  Gaps that ARE Fibonacci numbers: {fib_gap_count:,} ({fib_gap_pct:.2f}%)")

# Compare: for each Fibonacci gap value, is it over/under-represented
# compared to its neighbors?
print(f"\n  Fibonacci gap enrichment (vs ±2 neighbors):")
print(f"  {'Fib gap':>8s} {'Count':>8s} {'Neighbor avg':>13s} {'Ratio':>7s}")
print(f"  {'─'*40}")

enrichment_scores = []
for f in sorted(fibs & set(gaps.tolist())):
    if f < 2 or f > 100:
        continue
    fib_count = gap_counts.get(f, 0)
    neighbors = []
    for offset in [-2, -1, 1, 2]:
        n = f + offset
        if n > 0 and n in gap_counts:
            # Only even neighbors for even gaps (gaps > 2 are always even)
            if f > 2 and n % 2 != 0:
                continue
            neighbors.append(gap_counts.get(n, 0))
    if not neighbors:
        continue
    avg_neighbor = np.mean(neighbors)
    ratio = fib_count / avg_neighbor if avg_neighbor > 0 else float('inf')
    enrichment_scores.append(ratio)
    marker = " ←" if ratio > 1.2 else ""
    print(f"  {f:>8d} {fib_count:>8,} {avg_neighbor:>13.0f} {ratio:>7.3f}{marker}")

if enrichment_scores:
    mean_enrichment = np.mean(enrichment_scores)
    print(f"\n  Mean Fibonacci enrichment ratio: {mean_enrichment:.3f}")
    if mean_enrichment > 1.1:
        print(f"  → Fibonacci gaps are OVER-REPRESENTED (φ signature in primes!)")
    elif mean_enrichment < 0.9:
        print(f"  → Fibonacci gaps are UNDER-REPRESENTED")
    else:
        print(f"  → Fibonacci gaps are at expected frequency (no special φ affinity)")

# ============================================================
# PART 9: Twin prime gaps — are they engines?
# ============================================================

print("\n" + "=" * 70)
print("PART 9: TWIN PRIME ANALYSIS")
print("=" * 70)

# Twin primes: gaps of 2
twin_positions = np.where(gaps == 2)[0]
twin_inter_gaps = np.diff(twin_positions)

print(f"\n  Twin primes (gap=2): {len(twin_positions):,}")
print(f"  Inter-twin gaps: mean={np.mean(twin_inter_gaps):.2f}, std={np.std(twin_inter_gaps):.2f}")

twin_ara_d = compute_ara_discrete(twin_inter_gaps)
twin_ara_c = compute_ara_continuous(twin_inter_gaps)

print(f"  Twin prime inter-arrival ARA (discrete):   {twin_ara_d:.4f} → {classify_ara(twin_ara_d)}")
print(f"  Twin prime inter-arrival ARA (continuous): {twin_ara_c:.4f} → {classify_ara(twin_ara_c)}")

# Compare twin ARA to random subsample
twin_random_aras = []
for _ in range(100):
    fake_positions = sorted(np.random.choice(len(gaps), size=len(twin_positions), replace=False))
    fake_inter = np.diff(fake_positions)
    if len(fake_inter) > 3:
        twin_random_aras.append(compute_ara_continuous(fake_inter))

twin_z = (twin_ara_c - np.mean(twin_random_aras)) / np.std(twin_random_aras) if twin_random_aras else 0
print(f"\n  Twin ARA vs random subsample: z = {twin_z:+.2f}")

# ============================================================
# PART 10: The verdict — where do primes sit on the ARA spectrum?
# ============================================================

print("\n" + "=" * 70)
print("PART 10: THE VERDICT")
print("=" * 70)

print(f"""
  ┌──────────────────────────────────────────────────────────────┐
  │                    ARA SPECTRUM                              │
  │                                                              │
  │  0.0          0.5          1.0          φ≈1.618         2.0  │
  │   │            │            │            │               │   │
  │   ├────────────┼────────────┼────────────┼───────────────┤   │
  │   │  CONSUMER  │  mild      │  ABSORBER  │   ENGINE      │   │
  │   │            │  consumer  │            │               │   │
  │   │            │            │            │               │   │""")

# Place systems on the spectrum
systems = {
    'S&P 500': 0.930,
    'PRIMES (discrete)': ara_discrete,
    'PRIMES (continuous)': ara_continuous,
    'Lotto': 1.000,
}

for name, ara in sorted(systems.items(), key=lambda x: x[1]):
    # Map ARA to position in the bar (0-60 chars for 0-2 range)
    pos = int(ara / 2.0 * 56)
    pos = max(0, min(55, pos))
    line = " " * pos + "▼"
    print(f"  │   {line:<57s}│")
    print(f"  │   {' '*max(0,pos-len(name)//2)}{name:<57s}│")

print(f"  │                                                              │")
print(f"  └──────────────────────────────────────────────────────────────┘")

print(f"""
  SUMMARY:
  ─────────
  Prime gap ARA (discrete):   {ara_discrete:.6f}
  Prime gap ARA (continuous): {ara_continuous:.6f}

  vs Shuffled gaps (z):       {z_discrete:+.2f} (discrete), {z_continuous:+.2f} (continuous)
  vs Exponential random (z):  {z_exp_d:+.2f} (discrete), {z_exp_c:+.2f} (continuous)

  φ-modular effect (ranked):  {change_pct:+.1f}%
  φ-modular effect (raw):     {raw_change:+.1f}%

  Scale trend:                {coeffs_c[0]:+.6f} per decade

  Twin prime ARA:             {twin_ara_c:.4f} ({classify_ara(twin_ara_c)})
  Twin vs random subsample:   z = {twin_z:+.2f}
""")

# ============================================================
# FINAL: Is math itself an ARA system?
# ============================================================

print("=" * 70)
print("DOES MATH HAVE AN ARA?")
print("=" * 70)

# Test other mathematical sequences
print(f"\n  Testing mathematical sequences:")
print(f"  {'Sequence':<28s} {'ARA(d)':>8s} {'ARA(c)':>8s} {'Type':>14s}")
print(f"  {'─'*62}")

# 1. Fibonacci gaps
fibs_list = [1, 1]
while fibs_list[-1] < 10_000_000:
    fibs_list.append(fibs_list[-1] + fibs_list[-2])
fib_gaps = np.diff(fibs_list)
fib_ara_d = compute_ara_discrete(fib_gaps)
fib_ara_c = compute_ara_continuous(fib_gaps)
print(f"  {'Fibonacci gaps':<28s} {fib_ara_d:>8.4f} {fib_ara_c:>8.4f} {classify_ara(fib_ara_c):>14s}")

# 2. Fibonacci ratios (should converge to φ)
fib_ratios = np.array([fibs_list[i+1]/fibs_list[i] for i in range(2, len(fibs_list)-1)])
fib_rat_ara_d = compute_ara_discrete(fib_ratios)
fib_rat_ara_c = compute_ara_continuous(fib_ratios)
print(f"  {'Fibonacci ratios (→φ)':<28s} {fib_rat_ara_d:>8.4f} {fib_rat_ara_c:>8.4f} {classify_ara(fib_rat_ara_c):>14s}")

# 3. Powers of 2
pow2 = np.array([2**i for i in range(1, 50)])
pow2_gaps = np.diff(pow2)
pow2_ara_d = compute_ara_discrete(pow2_gaps)
pow2_ara_c = compute_ara_continuous(pow2_gaps)
print(f"  {'Powers of 2 gaps':<28s} {pow2_ara_d:>8.4f} {pow2_ara_c:>8.4f} {classify_ara(pow2_ara_c):>14s}")

# 4. Digits of π (from string representation)
# Generate π digits using mpmath
try:
    from mpmath import mp
    mp.dps = 10050
    pi_str = mp.nstr(mp.pi, 10001, strip_zeros=False).replace('.', '')
    pi_digits = np.array([int(d) for d in pi_str[:10000]])
    pi_gaps = np.diff(pi_digits)
    pi_ara_d = compute_ara_discrete(pi_gaps)
    pi_ara_c = compute_ara_continuous(pi_gaps)
    print(f"  {'π digit differences':<28s} {pi_ara_d:>8.4f} {pi_ara_c:>8.4f} {classify_ara(pi_ara_c):>14s}")
except ImportError:
    print(f"  {'π digits':<28s} (mpmath not available)")

# 5. Digits of e
try:
    e_str = mp.nstr(mp.e, 10001, strip_zeros=False).replace('.', '')
    e_digits = np.array([int(d) for d in e_str[:10000]])
    e_gaps = np.diff(e_digits)
    e_ara_d = compute_ara_discrete(e_gaps)
    e_ara_c = compute_ara_continuous(e_gaps)
    print(f"  {'e digit differences':<28s} {e_ara_d:>8.4f} {e_ara_c:>8.4f} {classify_ara(e_ara_c):>14s}")
except:
    print(f"  {'e digits':<28s} (not available)")

# 6. √2 digits
try:
    sqrt2_str = mp.nstr(mp.sqrt(2), 10001, strip_zeros=False).replace('.', '')
    sqrt2_digits = np.array([int(d) for d in sqrt2_str[:10000]])
    sqrt2_gaps = np.diff(sqrt2_digits)
    sqrt2_ara_d = compute_ara_discrete(sqrt2_gaps)
    sqrt2_ara_c = compute_ara_continuous(sqrt2_gaps)
    print(f"  {'√2 digit differences':<28s} {sqrt2_ara_d:>8.4f} {sqrt2_ara_c:>8.4f} {classify_ara(sqrt2_ara_c):>14s}")
except:
    print(f"  {'√2 digits':<28s} (not available)")

# 7. φ digits
try:
    phi_str = mp.nstr(mp.phi, 10001, strip_zeros=False).replace('.', '')
    phi_digits = np.array([int(d) for d in phi_str[:10000]])
    phi_gaps = np.diff(phi_digits)
    phi_ara_d = compute_ara_discrete(phi_gaps)
    phi_ara_c = compute_ara_continuous(phi_gaps)
    print(f"  {'φ digit differences':<28s} {phi_ara_d:>8.4f} {phi_ara_c:>8.4f} {classify_ara(phi_ara_c):>14s}")
except:
    print(f"  {'φ digits':<28s} (not available)")

# 8. Collatz sequence lengths (smaller range for speed)
collatz_lengths = []
for n in range(2, 10001):
    count = 0
    x = n
    while x != 1:
        x = x // 2 if x % 2 == 0 else 3 * x + 1
        count += 1
    collatz_lengths.append(count)
collatz_arr = np.array(collatz_lengths)
collatz_gaps = np.diff(collatz_arr)
collatz_ara_d = compute_ara_discrete(collatz_gaps)
collatz_ara_c = compute_ara_continuous(collatz_gaps)
print(f"  {'Collatz lengths (2-10k)':<28s} {collatz_ara_d:>8.4f} {collatz_ara_c:>8.4f} {classify_ara(collatz_ara_c):>14s}")

# 9. Divisor count function (sieve approach for speed)
N_DIV = 50000
div_arr = np.zeros(N_DIV + 1, dtype=int)
for d in range(1, N_DIV + 1):
    div_arr[d::d] += 1
div_arr = div_arr[1:]  # start from n=1
div_gaps = np.diff(div_arr)
div_ara_d = compute_ara_discrete(div_gaps)
div_ara_c = compute_ara_continuous(div_gaps)
print(f"  {'Divisor count d(n)':<28s} {div_ara_d:>8.4f} {div_ara_c:>8.4f} {classify_ara(div_ara_c):>14s}")

# 10. Prime counting function π(n)
# Count primes up to each 1000
pi_counts = []
prime_set = set(primes.tolist())
for n in range(1000, min(LIMIT + 1, 10_000_001), 1000):
    # Number of primes up to n
    idx = np.searchsorted(primes, n, side='right')
    pi_counts.append(idx)
pi_arr = np.array(pi_counts)
pi_diffs = np.diff(pi_arr)  # primes per 1000-block
pi_count_ara_d = compute_ara_discrete(pi_diffs)
pi_count_ara_c = compute_ara_continuous(pi_diffs)
print(f"  {'π(n) per 1000-block':<28s} {pi_count_ara_d:>8.4f} {pi_count_ara_c:>8.4f} {classify_ara(pi_count_ara_c):>14s}")

print(f"\n{'='*70}")
print(f"END OF SCRIPT 243BL16")
print(f"{'='*70}")
