"""
Script 243BL9: Randomness as Irrationality — Terrain Mapper
============================================================

Dylan's hypothesis: "Random numbers are just quantum and irrationality linked."
Randomness is a snap-consumer on the ARA scale.

Test: Compare statistical signatures of Australian Saturday Lotto draws against:
  1. Digits of φ (the golden ratio)
  2. Digits of π
  3. Digits of √2
  4. Digits of e
  5. True uniform random (numpy)

If randomness IS irrationality, then:
  - Lotto draws should share deep statistical structure with irrational digit sequences
  - φ should be special (golden ratio = most irrational number)
  - The ARA of randomness should land in consumer territory (< 1.0)

Tests:
  1. Gap distribution — spacing between consecutive numbers
  2. Digit frequency convergence — how fast does flat distribution emerge?
  3. Autocorrelation decay — memory structure in sequences
  4. φ-proximity — do gaps/ratios cluster near φ or 1/φ?
  5. ARA scoring — accumulate/release/accumulate in the sequence itself
  6. Entropy rate — bits per symbol, compared across sources
  7. Benford's Law — first-digit distribution (irrationals obey it, do lotto?)
  8. Pair correlation — consecutive-pair ratios vs φ
  9. Run-length distribution — streaks of above/below median
  10. The snap test — does randomness exhibit ARA snap behaviour?
"""

import numpy as np
from decimal import Decimal, getcontext
import csv
import os

# High precision for irrational digit generation
getcontext().prec = 50000

PHI = (1 + np.sqrt(5)) / 2

# ============================================================
# PART 0: Load and prepare data sources
# ============================================================

def load_lotto_data(filepath):
    """Load Saturday Lotto draws — extract main 6 numbers per draw."""
    draws = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)  # skip header
        for row in reader:
            try:
                nums = [int(row[i]) for i in range(2, 8)]  # columns 2-7 = 6 main numbers
                draws.append(sorted(nums))
            except (ValueError, IndexError):
                continue
    return draws

def generate_phi_digits(n):
    """Generate n digits of φ using high-precision arithmetic."""
    getcontext().prec = n + 100
    five = Decimal(5)
    phi = (1 + five.sqrt()) / 2
    phi_str = str(phi).replace('0.', '').replace('1.', '')
    # φ = 1.6180339887... — take digits after "1."
    full = str(phi)
    if '.' in full:
        digits = full.split('.')[1]
    else:
        digits = full[1:]
    return [int(d) for d in digits[:n]]

def generate_pi_digits(n):
    """Generate n digits of π using Machin's formula with mpmath."""
    try:
        from mpmath import mp, mpf, pi
        mp.dps = n + 50
        pi_str = mp.nstr(pi, n + 10)
        digits = pi_str.replace('3.', '')
        return [int(d) for d in digits[:n]]
    except ImportError:
        # Fallback: use known digits
        pi_str = "14159265358979323846264338327950288419716939937510"
        pi_str += "58209749445923078164062862089986280348253421170679"
        pi_str += "82148086513282306647093844609550582231725359408128"
        pi_str += "48111745028410270193852110555964462294895493038196"
        return [int(d) for d in pi_str[:n]]

def generate_sqrt2_digits(n):
    """Generate n digits of √2."""
    getcontext().prec = n + 100
    two = Decimal(2)
    sqrt2 = two.sqrt()
    full = str(sqrt2)
    if '.' in full:
        digits = full.split('.')[1]
    else:
        digits = full[1:]
    return [int(d) for d in digits[:n]]

def generate_e_digits(n):
    """Generate n digits of e."""
    try:
        from mpmath import mp, e
        mp.dps = n + 50
        e_str = mp.nstr(e, n + 10)
        digits = e_str.replace('2.', '')
        return [int(d) for d in digits[:n]]
    except ImportError:
        getcontext().prec = n + 100
        # e via Taylor series
        e_val = Decimal(0)
        factorial = Decimal(1)
        for i in range(500):
            e_val += 1 / factorial
            factorial *= (i + 1)
        full = str(e_val)
        digits = full.replace('2.', '')
        return [int(d) for d in digits[:n]]

# ============================================================
# PART 1: Statistical signature functions
# ============================================================

def gap_distribution(sequence):
    """Compute gaps between consecutive values in a flattened sequence."""
    flat = np.array(sequence).flatten()
    gaps = np.diff(flat)
    return gaps

def digit_frequency_convergence(digits, window=100):
    """How fast does digit frequency converge to uniform?"""
    n = len(digits)
    deviations = []
    for i in range(window, n, window):
        chunk = digits[:i]
        counts = np.bincount(chunk, minlength=10) / len(chunk)
        deviation = np.mean(np.abs(counts - 0.1))  # mean absolute deviation from 1/10
        deviations.append(deviation)
    return deviations

def autocorrelation(sequence, max_lag=50):
    """Compute autocorrelation at various lags."""
    x = np.array(sequence, dtype=float)
    x = x - np.mean(x)
    if np.std(x) == 0:
        return np.zeros(max_lag)
    result = np.correlate(x, x, mode='full')
    result = result[len(result)//2:]
    result = result / result[0]
    return result[:max_lag]

def phi_proximity(gaps):
    """What fraction of gaps are within 10% of φ, 1/φ, φ², or 1/φ²?"""
    targets = {
        'φ': PHI,
        '1/φ': 1/PHI,
        'φ²': PHI**2,
        '1/φ²': 1/PHI**2,
    }
    results = {}
    gaps = np.abs(gaps).astype(float)
    gaps = gaps[gaps > 0]  # avoid division by zero
    for name, target in targets.items():
        # Check ratios of consecutive gaps
        if len(gaps) > 1:
            ratios = gaps[1:] / gaps[:-1]
            ratios = ratios[np.isfinite(ratios)]
            close = np.sum(np.abs(ratios - target) / target < 0.10) / len(ratios)
            results[name] = close
    return results

def entropy_rate(sequence, base=2):
    """Shannon entropy rate of the sequence."""
    vals, counts = np.unique(sequence, return_counts=True)
    probs = counts / len(sequence)
    entropy = -np.sum(probs * np.log(probs) / np.log(base))
    # Normalize by max possible entropy
    max_entropy = np.log(len(vals)) / np.log(base)
    return entropy, max_entropy, entropy / max_entropy if max_entropy > 0 else 0

def benford_test(sequence):
    """Test first-digit distribution against Benford's Law."""
    first_digits = []
    for val in sequence:
        val = abs(int(val))
        if val > 0:
            while val >= 10:
                val //= 10
            first_digits.append(val)

    if not first_digits:
        return {}, 0

    counts = np.bincount(first_digits, minlength=10)[1:]  # digits 1-9
    observed = counts / counts.sum()

    # Benford's expected
    expected = np.array([np.log10(1 + 1/d) for d in range(1, 10)])

    # Chi-squared-like deviation
    deviation = np.sum((observed - expected)**2 / expected)

    return dict(zip(range(1, 10), observed)), deviation

def run_length_distribution(sequence, threshold=None):
    """Distribution of run lengths (consecutive above/below median)."""
    if threshold is None:
        threshold = np.median(sequence)

    binary = (np.array(sequence) > threshold).astype(int)
    runs = []
    current_run = 1
    for i in range(1, len(binary)):
        if binary[i] == binary[i-1]:
            current_run += 1
        else:
            runs.append(current_run)
            current_run = 1
    runs.append(current_run)
    return np.array(runs)

def compute_ara(sequence, window=10):
    """
    Compute ARA of a sequence: look at accumulation/release pattern.
    Accumulate = values increasing or staying, Release = values decreasing.
    ARA = mean(accumulation spans) / mean(release spans)
    """
    x = np.array(sequence, dtype=float)
    acc_lengths = []
    rel_lengths = []
    current_acc = 0
    current_rel = 0

    for i in range(1, len(x)):
        if x[i] >= x[i-1]:
            current_acc += 1
            if current_rel > 0:
                rel_lengths.append(current_rel)
                current_rel = 0
        else:
            current_rel += 1
            if current_acc > 0:
                acc_lengths.append(current_acc)
                current_acc = 0

    if current_acc > 0:
        acc_lengths.append(current_acc)
    if current_rel > 0:
        rel_lengths.append(current_rel)

    mean_acc = np.mean(acc_lengths) if acc_lengths else 0
    mean_rel = np.mean(rel_lengths) if rel_lengths else 1

    ara = mean_acc / mean_rel if mean_rel > 0 else float('inf')
    return ara, mean_acc, mean_rel

def snap_test(sequence, window=20):
    """
    Test for snap behaviour: sudden large deviations followed by return.
    Snaps are E events in ARA — displacement corrections.
    Returns: snap frequency, mean snap magnitude, recovery time.
    """
    x = np.array(sequence, dtype=float)
    rolling_mean = np.convolve(x, np.ones(window)/window, mode='valid')

    # Snaps = points where |x - mean| > 2 * std
    residuals = x[window-1:] - rolling_mean
    std = np.std(residuals)
    snap_mask = np.abs(residuals) > 2 * std
    snap_count = np.sum(snap_mask)

    if snap_count == 0:
        return 0, 0, 0

    snap_indices = np.where(snap_mask)[0]
    snap_magnitudes = np.abs(residuals[snap_mask])

    # Recovery time: how many steps until |residual| < std after a snap
    recovery_times = []
    for idx in snap_indices:
        for j in range(idx+1, len(residuals)):
            if np.abs(residuals[j]) < std:
                recovery_times.append(j - idx)
                break

    snap_freq = snap_count / len(residuals)
    mean_mag = np.mean(snap_magnitudes) / std  # normalized
    mean_recovery = np.mean(recovery_times) if recovery_times else 0

    return snap_freq, mean_mag, mean_recovery

# ============================================================
# PART 2: Prepare all data sources
# ============================================================

print("=" * 70)
print("Script 243BL9: RANDOMNESS AS IRRATIONALITY — TERRAIN MAPPER")
print("=" * 70)

# Load lotto
lotto_path = os.path.join(os.path.dirname(__file__), '..', '..', 'lotto', 'saturday-lotto.csv')
if not os.path.exists(lotto_path):
    lotto_path = '/sessions/focused-tender-thompson/lotto/saturday-lotto.csv'

draws = load_lotto_data(lotto_path)
print(f"\nLoaded {len(draws)} Saturday Lotto draws (1986-2024)")
print(f"Format: 6 numbers from 1-45 per draw")

# Flatten lotto to single sequence of drawn numbers (in draw order)
lotto_flat = []
for draw in draws:
    lotto_flat.extend(draw)
lotto_flat = np.array(lotto_flat)

# Generate irrational digit sequences (same length as lotto flat)
N = len(lotto_flat)
print(f"Total lotto numbers: {N}")

print("\nGenerating irrational digit sequences...")
phi_digits = generate_phi_digits(N)
pi_digits = generate_pi_digits(N)
sqrt2_digits = generate_sqrt2_digits(N)
e_digits = generate_e_digits(N)

# Pseudo-random (numpy)
np.random.seed(42)
pseudo_random = np.random.randint(0, 10, N)

# Also create "lotto as digits" — map each number to 0-9 range for fair comparison
lotto_digits = (lotto_flat - 1) * 10 // 45  # map 1-45 → 0-9

# For gap analysis, use the raw lotto numbers
lotto_gaps = []
for draw in draws:
    for i in range(1, len(draw)):
        lotto_gaps.append(draw[i] - draw[i-1])
lotto_gaps = np.array(lotto_gaps)

# Irrational gaps
phi_gaps = np.diff(phi_digits)
pi_gaps = np.diff(pi_digits)
sqrt2_gaps = np.diff(sqrt2_digits)
e_gaps = np.diff(e_digits)
pseudo_gaps = np.diff(pseudo_random)

print(f"φ digits: {len(phi_digits)}, π digits: {len(pi_digits)}")
print(f"√2 digits: {len(sqrt2_digits)}, e digits: {len(e_digits)}")

# ============================================================
# TEST 1: Gap Distribution — do they share the same shape?
# ============================================================

print("\n" + "=" * 70)
print("TEST 1: Gap Distribution Shape")
print("=" * 70)

def gap_stats(gaps, name):
    g = np.array(gaps, dtype=float)
    mean_gap = np.mean(np.abs(g))
    std_gap = np.std(g)
    skew = np.mean(((g - np.mean(g)) / np.std(g))**3) if np.std(g) > 0 else 0
    kurt = np.mean(((g - np.mean(g)) / np.std(g))**4) - 3 if np.std(g) > 0 else 0
    # Ratio of mean to std — for uniform random, this should be specific
    ratio = mean_gap / std_gap if std_gap > 0 else 0
    print(f"  {name:15s}: mean|gap|={mean_gap:.3f}, std={std_gap:.3f}, "
          f"skew={skew:.3f}, kurt={kurt:.3f}, mean/std={ratio:.4f}")
    return mean_gap, std_gap, skew, kurt, ratio

print("\nGap statistics (consecutive differences):")
gap_data = {}
gap_data['Lotto'] = gap_stats(lotto_gaps, 'Lotto (1-45)')
gap_data['φ'] = gap_stats(phi_gaps, 'φ digits')
gap_data['π'] = gap_stats(pi_gaps, 'π digits')
gap_data['√2'] = gap_stats(sqrt2_gaps, '√2 digits')
gap_data['e'] = gap_stats(e_gaps, 'e digits')
gap_data['Pseudo'] = gap_stats(pseudo_gaps, 'Pseudo-random')

# Check if irrational gaps share a universal signature
print("\n  Mean/Std ratios (if universal, these should cluster):")
for name, (m, s, sk, ku, r) in gap_data.items():
    print(f"    {name:12s}: {r:.4f}")

irr_ratios = [gap_data[k][4] for k in ['φ', 'π', '√2', 'e']]
print(f"\n  Irrational mean/std cluster: {np.mean(irr_ratios):.4f} ± {np.std(irr_ratios):.4f}")
print(f"  Pseudo-random mean/std:      {gap_data['Pseudo'][4]:.4f}")
print(f"  Lotto mean/std:              {gap_data['Lotto'][4]:.4f}")

# ============================================================
# TEST 2: φ-proximity in gap ratios
# ============================================================

print("\n" + "=" * 70)
print("TEST 2: φ-Proximity in Consecutive Gap Ratios")
print("=" * 70)
print("(Fraction of consecutive gap ratios within 10% of φ-related targets)")

all_sources = {
    'Lotto': np.abs(lotto_gaps).astype(float),
    'φ digits': np.abs(phi_gaps).astype(float),
    'π digits': np.abs(pi_gaps).astype(float),
    '√2 digits': np.abs(sqrt2_gaps).astype(float),
    'e digits': np.abs(e_gaps).astype(float),
    'Pseudo': np.abs(pseudo_gaps).astype(float),
}

for name, gaps in all_sources.items():
    prox = phi_proximity(gaps)
    if prox:
        parts = [f"{k}={v:.4f}" for k, v in prox.items()]
        print(f"  {name:12s}: {', '.join(parts)}")

# ============================================================
# TEST 3: Autocorrelation Decay Profile
# ============================================================

print("\n" + "=" * 70)
print("TEST 3: Autocorrelation Decay Profile")
print("=" * 70)
print("(How fast does memory decay? Pure random → instant drop to 0)")

ac_data = {}
for name, seq in [('Lotto', lotto_flat), ('φ', phi_digits), ('π', pi_digits),
                   ('√2', sqrt2_digits), ('e', e_digits), ('Pseudo', pseudo_random)]:
    ac = autocorrelation(seq, max_lag=20)
    ac_data[name] = ac
    # Measure: sum of |autocorrelation| at lags 1-10 (persistence)
    persistence = np.sum(np.abs(ac[1:11]))
    # Half-life: first lag where |ac| < 0.5
    halflife = next((i for i in range(1, len(ac)) if abs(ac[i]) < 0.05), len(ac))
    print(f"  {name:8s}: persistence(1-10)={persistence:.4f}, "
          f"half-life(to 0.05)={halflife}, ac[1]={ac[1]:.4f}")

# ============================================================
# TEST 4: Entropy Rate
# ============================================================

print("\n" + "=" * 70)
print("TEST 4: Shannon Entropy Rate")
print("=" * 70)
print("(Normalized entropy: 1.0 = maximally random, <1.0 = has structure)")

for name, seq in [('Lotto digits', lotto_digits), ('φ', phi_digits), ('π', pi_digits),
                   ('√2', sqrt2_digits), ('e', e_digits), ('Pseudo', pseudo_random)]:
    ent, max_ent, norm = entropy_rate(seq)
    print(f"  {name:13s}: H={ent:.4f} bits, max={max_ent:.4f}, "
          f"normalized={norm:.6f}")

# ============================================================
# TEST 5: Benford's Law
# ============================================================

print("\n" + "=" * 70)
print("TEST 5: Benford's Law (First-Digit Distribution)")
print("=" * 70)
print("(Irrationals tend to follow Benford's Law; uniform random does not)")

# For Benford, use the RAW lotto numbers (1-45) and irrational digits differently
# Actually for irrationals, use sliding windows of 3 digits as numbers
def make_numbers(digits, window=3):
    """Convert digit sequence to numbers for Benford analysis."""
    nums = []
    for i in range(len(digits) - window + 1):
        n = 0
        for j in range(window):
            n = n * 10 + digits[i + j]
        if n > 0:
            nums.append(n)
    return nums

benford_expected = {d: np.log10(1 + 1/d) for d in range(1, 10)}
print(f"\n  Benford expected: {', '.join(f'{d}:{p:.3f}' for d, p in benford_expected.items())}")

for name, source in [('Lotto raw', lotto_flat),
                     ('φ (3-digit)', make_numbers(phi_digits)),
                     ('π (3-digit)', make_numbers(pi_digits)),
                     ('√2 (3-digit)', make_numbers(sqrt2_digits)),
                     ('e (3-digit)', make_numbers(e_digits)),
                     ('Pseudo (3-digit)', make_numbers(list(pseudo_random)))]:
    dist, dev = benford_test(source)
    if dist:
        print(f"  {name:18s}: χ²-like={dev:.4f}  [{', '.join(f'{d}:{p:.3f}' for d, p in dist.items())}]")

# ============================================================
# TEST 6: ARA Scoring — Accumulate/Release Pattern
# ============================================================

print("\n" + "=" * 70)
print("TEST 6: ARA Scoring — Is Randomness a Consumer?")
print("=" * 70)
print("(ARA < 1 = consumer, ARA ≈ 1 = balanced, ARA > 1 = engine)")

for name, seq in [('Lotto', lotto_flat), ('φ', phi_digits), ('π', pi_digits),
                   ('√2', sqrt2_digits), ('e', e_digits), ('Pseudo', pseudo_random)]:
    ara, mean_acc, mean_rel = compute_ara(seq)
    territory = "CONSUMER" if ara < 0.95 else ("ENGINE" if ara > 1.05 else "BALANCED")
    # Distance from φ
    phi_dist = abs(ara - PHI) / PHI
    one_dist = abs(ara - 1.0)
    print(f"  {name:8s}: ARA = {ara:.4f} ({territory})  "
          f"acc={mean_acc:.2f}, rel={mean_rel:.2f}  "
          f"|ARA-1|={one_dist:.4f}, |ARA-φ|/φ={phi_dist:.4f}")

# ============================================================
# TEST 7: Run-Length Distribution
# ============================================================

print("\n" + "=" * 70)
print("TEST 7: Run-Length Distribution (Streaks)")
print("=" * 70)
print("(Mean run length for pure random = 2.0; deviations indicate structure)")

for name, seq in [('Lotto', lotto_flat), ('φ', phi_digits), ('π', pi_digits),
                   ('√2', sqrt2_digits), ('e', e_digits), ('Pseudo', pseudo_random)]:
    runs = run_length_distribution(seq)
    mean_run = np.mean(runs)
    max_run = np.max(runs)
    # φ-test: is mean run close to φ?
    phi_err = abs(mean_run - PHI) / PHI * 100
    print(f"  {name:8s}: mean run={mean_run:.4f}, max={max_run}, "
          f"count={len(runs)}, |mean-φ|/φ={phi_err:.1f}%")

# ============================================================
# TEST 8: Snap Test — E Events in Random Sequences
# ============================================================

print("\n" + "=" * 70)
print("TEST 8: Snap Test — E Events (Displacement Corrections)")
print("=" * 70)
print("(Frequency of 2σ deviations, their magnitude, and recovery time)")

for name, seq in [('Lotto', lotto_flat), ('φ', phi_digits), ('π', pi_digits),
                   ('√2', sqrt2_digits), ('e', e_digits), ('Pseudo', pseudo_random)]:
    freq, mag, recovery = snap_test(seq, window=20)
    # For Gaussian random, snap freq ≈ 0.046 (2σ = 4.6%)
    print(f"  {name:8s}: freq={freq:.4f} (expect ~0.046), "
          f"magnitude={mag:.2f}σ, recovery={recovery:.1f} steps")

# ============================================================
# TEST 9: Pair Correlation — Consecutive Number Ratios
# ============================================================

print("\n" + "=" * 70)
print("TEST 9: Consecutive Pair Ratios vs φ")
print("=" * 70)
print("(If randomness carries a φ-signature, pair ratios should cluster near φ)")

for name, seq in [('Lotto', lotto_flat), ('φ', phi_digits[:N]), ('π', pi_digits[:N]),
                   ('√2', sqrt2_digits[:N]), ('e', e_digits[:N]), ('Pseudo', pseudo_random)]:
    arr = np.array(seq, dtype=float)
    arr = arr[arr > 0]  # avoid division by zero
    if len(arr) > 1:
        ratios = arr[1:] / arr[:-1]
        ratios = ratios[np.isfinite(ratios)]
        mean_ratio = np.mean(ratios)
        median_ratio = np.median(ratios)
        # What fraction land within 5% of φ or 1/φ?
        near_phi = np.sum(np.abs(ratios - PHI) / PHI < 0.05) / len(ratios)
        near_inv_phi = np.sum(np.abs(ratios - 1/PHI) / (1/PHI) < 0.05) / len(ratios)
        print(f"  {name:8s}: mean={mean_ratio:.4f}, median={median_ratio:.4f}, "
              f"near_φ={near_phi:.4f}, near_1/φ={near_inv_phi:.4f}")

# ============================================================
# TEST 10: The Deep Test — Lotto Gap Histogram vs Irrational Gaps
# ============================================================

print("\n" + "=" * 70)
print("TEST 10: Distribution Shape Comparison (KL Divergence)")
print("=" * 70)
print("(Lower KL divergence = more similar distribution shape)")

def kl_divergence(p, q):
    """KL(P || Q) with smoothing."""
    eps = 1e-10
    p = np.array(p, dtype=float) + eps
    q = np.array(q, dtype=float) + eps
    p = p / p.sum()
    q = q / q.sum()
    return np.sum(p * np.log(p / q))

# Histogram the gaps into 20 bins
def gap_histogram(gaps, bins=20):
    """Normalized histogram of absolute gaps."""
    g = np.abs(gaps)
    counts, _ = np.histogram(g, bins=bins, range=(0, max(10, np.percentile(g, 99))))
    return counts / counts.sum()

# For digit sequences, use absolute gaps
digit_hists = {}
for name, gaps in [('φ', phi_gaps), ('π', pi_gaps), ('√2', sqrt2_gaps),
                    ('e', e_gaps), ('Pseudo', pseudo_gaps)]:
    digit_hists[name] = gap_histogram(gaps, bins=10)

# Lotto needs its own binning (range 1-45 gaps)
lotto_hist = gap_histogram(lotto_gaps, bins=10)

# Compare all digit sources to each other
print("\n  KL divergence between digit-gap distributions:")
digit_names = ['φ', 'π', '√2', 'e', 'Pseudo']
for i, n1 in enumerate(digit_names):
    for n2 in digit_names[i+1:]:
        kl = kl_divergence(digit_hists[n1], digit_hists[n2])
        marker = " ← CLOSEST" if kl < 0.005 else ""
        print(f"    {n1} vs {n2}: KL = {kl:.6f}{marker}")

print("\n  All irrationals vs Pseudo-random:")
for name in ['φ', 'π', '√2', 'e']:
    kl = kl_divergence(digit_hists[name], digit_hists['Pseudo'])
    print(f"    {name} vs Pseudo: KL = {kl:.6f}")

# ============================================================
# SYNTHESIS: The Terrain Map
# ============================================================

print("\n" + "=" * 70)
print("SYNTHESIS: THE RANDOMNESS TERRAIN")
print("=" * 70)

# Compute composite scores
print("\nComposite ARA scores:")
ara_scores = {}
for name, seq in [('Lotto', lotto_flat), ('φ', phi_digits), ('π', pi_digits),
                   ('√2', sqrt2_digits), ('e', e_digits), ('Pseudo', pseudo_random)]:
    ara, _, _ = compute_ara(seq)
    ara_scores[name] = ara

# Sort by ARA
sorted_ara = sorted(ara_scores.items(), key=lambda x: x[1])
print("\n  Randomness sources ordered by ARA:")
for name, ara in sorted_ara:
    phi_err = abs(ara - 1.0) * 100
    bar = "█" * int(ara * 30)
    territory = ""
    if ara < 0.95:
        territory = "[CONSUMER]"
    elif ara < 1.05:
        territory = "[BALANCED]"
    elif ara < PHI - 0.1:
        territory = "[ABOVE 1]"
    elif abs(ara - PHI) / PHI < 0.05:
        territory = "[≈ φ ENGINE]"
    else:
        territory = "[ENGINE]"
    print(f"    {name:8s}: ARA = {ara:.4f}  {bar} {territory}")

# The key question: do irrationals cluster?
irr_aras = [ara_scores[k] for k in ['φ', 'π', '√2', 'e']]
print(f"\n  Irrational ARA cluster: {np.mean(irr_aras):.4f} ± {np.std(irr_aras):.4f}")
print(f"  Pseudo-random ARA:      {ara_scores['Pseudo']:.4f}")
print(f"  Lotto ARA:              {ara_scores['Lotto']:.4f}")
print(f"  Difference (Lotto - Irrational mean): {ara_scores['Lotto'] - np.mean(irr_aras):.4f}")

# Is ARA < 1 universally? → Consumer hypothesis
all_consumer = all(a < 1.05 for a in ara_scores.values())
print(f"\n  ALL sources are consumers (ARA < 1.05): {all_consumer}")

# φ special?
print(f"\n  Is φ the most structured irrational?")
print(f"    φ entropy normalized:  (see Test 4)")
print(f"    φ persistence:         (see Test 3)")

# The snap-consumer verdict
print(f"\n" + "-" * 70)
print("VERDICT:")
print("-" * 70)

snap_data = {}
for name, seq in [('Lotto', lotto_flat), ('φ', phi_digits), ('π', pi_digits),
                   ('√2', sqrt2_digits), ('e', e_digits), ('Pseudo', pseudo_random)]:
    freq, mag, recovery = snap_test(seq)
    snap_data[name] = (freq, mag, recovery)

print(f"\n  Snap frequency (all sources):")
for name in ['Lotto', 'φ', 'π', '√2', 'e', 'Pseudo']:
    freq, mag, rec = snap_data[name]
    print(f"    {name:8s}: {freq:.4f} snaps/step, mag={mag:.2f}σ, recovery={rec:.1f}")

# Final ARA terrain position
print(f"\n  RANDOMNESS ON THE ARA SCALE:")
mean_all = np.mean(list(ara_scores.values()))
print(f"    Mean ARA (all random sources):    {mean_all:.4f}")
print(f"    Expected for pure consumer:       < 1.0")
print(f"    Expected for shock absorber:      ≈ 1.0")
print(f"    φ (golden engine):                {PHI:.4f}")
print(f"    Irrationality mean ARA:           {np.mean(irr_aras):.4f}")

# Is randomness = irrationality?
print(f"\n  RANDOMNESS = IRRATIONALITY TEST:")
# Compare Lotto to irrational cluster vs pseudo-random
lotto_to_irr = abs(ara_scores['Lotto'] - np.mean(irr_aras))
lotto_to_pseudo = abs(ara_scores['Lotto'] - ara_scores['Pseudo'])
print(f"    |Lotto - Irrational mean|:  {lotto_to_irr:.4f}")
print(f"    |Lotto - Pseudo-random|:    {lotto_to_pseudo:.4f}")
if lotto_to_irr < lotto_to_pseudo:
    print(f"    → Lotto is CLOSER to irrationals than to pseudo-random")
else:
    print(f"    → Lotto is CLOSER to pseudo-random than to irrationals")

print(f"\n{'=' * 70}")
print(f"END Script 243BL9")
print(f"{'=' * 70}")
