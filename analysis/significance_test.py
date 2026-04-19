"""
Monte Carlo Significance Test for φ-Clustering in ARA Ratios
=============================================================
Question: If you draw N independent ratios from a reasonable null
distribution, how often do you get as many systems within X% of
φ (1.618...) as we actually observed?

Observed data (12 systems tested):
  Within 5% of φ:  breath (0.5%), SCS hydrograph (3.2%),
                    watershed V2 (3.0%), preferred walk speed (exact)
  → 4 out of 12 systems within 5% of φ

  Within 7% of φ:  above 4 + solar (6.9%)
  → 5 out of 12 systems within 7% of φ

We test against multiple null distributions to show robustness:
  1. Uniform on [0, 2]           — no structure assumed
  2. Uniform on [0.5, 2.5]      — wider plausible range
  3. Log-normal (μ=0.2, σ=0.4)  — right-skewed, centered ~1.2
  4. Normal (μ=1.3, σ=0.4)      — centered near typical bio ratios
  5. Beta(2,2) scaled to [0,2]  — peaked in middle of range

For each null:
  - Draw 12 random ratios, 10,000,000 times
  - Count how many of the 12 fall within 5% of φ
  - Report: P(≥4 within 5%) and P(≥5 within 7%)

Additionally, we test the PREDICTIVE structure:
  The framework doesn't just find φ — it predicts WHICH systems
  should hit (free-running) and which should miss (forced/managed).
  We test: given 4 hits in 12 systems, what's the probability that
  ALL 4 hits come from a pre-specified subset of 5 "predicted hits"
  (breath, SCS, watershed, walk speed, solar)?
"""

import numpy as np
from scipy import stats as sp_stats
import time

PHI = (1 + np.sqrt(5)) / 2  # 1.618033988749895

# ── Observed results ──────────────────────────────────────────────
observed_ratios = {
    'Breath':           1.61,
    'SCS hydrograph':   1.67,
    'Watershed V2':     1.57,
    'Walk speed':       1.618,  # exact φ crossing
    'Solar':            1.73,
    'Healthy gait':     1.355,
    'Blood glucose':    1.2,
    'Crypto':           1.19,
    'EEG delta':        1.05,
    'EEG beta':         1.00,
    'Sea ice':          0.91,
    'Cepheid':          2.00,
}

N_SYSTEMS = len(observed_ratios)
N_SIMS = 10_000_000

# Count observed hits
def count_within_pct(ratios, target, pct):
    """Count how many ratios are within pct% of target."""
    threshold = target * pct / 100
    return sum(1 for r in ratios if abs(r - target) <= threshold)

obs_5pct = count_within_pct(observed_ratios.values(), PHI, 5)
obs_7pct = count_within_pct(observed_ratios.values(), PHI, 7)

print("=" * 70)
print("MONTE CARLO SIGNIFICANCE TEST FOR φ-CLUSTERING")
print("=" * 70)
print(f"\nGolden ratio φ = {PHI:.6f}")
print(f"Systems tested: {N_SYSTEMS}")
print(f"Observed within 5% of φ: {obs_5pct} systems")
print(f"Observed within 7% of φ: {obs_7pct} systems")
print(f"Simulations per null: {N_SIMS:,}")
print()

# ── 5% window boundaries ─────────────────────────────────────────
w5_lo = PHI * 0.95
w5_hi = PHI * 1.05
w7_lo = PHI * 0.93
w7_hi = PHI * 1.07
print(f"5% window: [{w5_lo:.4f}, {w5_hi:.4f}]  (width = {w5_hi - w5_lo:.4f})")
print(f"7% window: [{w7_lo:.4f}, {w7_hi:.4f}]  (width = {w7_hi - w7_lo:.4f})")
print()

# ── Define null distributions ─────────────────────────────────────
def uniform_0_2(n_sims, n_sys):
    return np.random.uniform(0, 2, (n_sims, n_sys))

def uniform_05_25(n_sims, n_sys):
    return np.random.uniform(0.5, 2.5, (n_sims, n_sys))

def lognormal_null(n_sims, n_sys):
    # Log-normal with median ~1.2, right-skewed
    return np.random.lognormal(mean=0.2, sigma=0.4, size=(n_sims, n_sys))

def normal_null(n_sims, n_sys):
    # Normal centered at 1.3, truncated to positive
    samples = np.random.normal(1.3, 0.4, (n_sims, n_sys))
    samples = np.clip(samples, 0.01, None)
    return samples

def beta_scaled(n_sims, n_sys):
    # Beta(2,2) on [0,1] scaled to [0,2] — peaked at 1.0
    return np.random.beta(2, 2, (n_sims, n_sys)) * 2

nulls = [
    ("Uniform [0, 2]",       uniform_0_2),
    ("Uniform [0.5, 2.5]",   uniform_05_25),
    ("Log-normal (μ=0.2, σ=0.4)", lognormal_null),
    ("Normal (μ=1.3, σ=0.4)", normal_null),
    ("Beta(2,2) × 2",        beta_scaled),
]

# ── Run simulations ───────────────────────────────────────────────
print("-" * 70)
print(f"{'Null Distribution':<30} {'P(≥4 in 5%)':<16} {'P(≥5 in 7%)':<16} {'Time':>6}")
print("-" * 70)

results = {}

for name, gen_fn in nulls:
    t0 = time.time()

    # Generate all random ratios at once
    samples = gen_fn(N_SIMS, N_SYSTEMS)

    # Count how many fall in the 5% window per simulation
    in_5pct = np.sum((samples >= w5_lo) & (samples <= w5_hi), axis=1)
    in_7pct = np.sum((samples >= w7_lo) & (samples <= w7_hi), axis=1)

    # P(≥ observed)
    p_5 = np.mean(in_5pct >= obs_5pct)
    p_7 = np.mean(in_7pct >= obs_7pct)

    elapsed = time.time() - t0

    results[name] = (p_5, p_7)

    # Format p-values
    p5_str = f"{p_5:.6f}" if p_5 >= 0.000001 else f"< {1/N_SIMS:.1e}"
    p7_str = f"{p_7:.6f}" if p_7 >= 0.000001 else f"< {1/N_SIMS:.1e}"

    print(f"{name:<30} {p5_str:<16} {p7_str:<16} {elapsed:>5.1f}s")

print("-" * 70)

# ── Analytical check (binomial) for Uniform [0,2] ────────────────
print("\n\nANALYTICAL VERIFICATION (Binomial, Uniform [0,2]):")
print("-" * 70)

# Under Uniform[0,2], probability of landing in 5% window
p_hit_5 = (w5_hi - w5_lo) / 2.0
p_hit_7 = (w7_hi - w7_lo) / 2.0

print(f"P(single ratio in 5% window) = {p_hit_5:.4f}  ({p_hit_5*100:.2f}%)")
print(f"P(single ratio in 7% window) = {p_hit_7:.4f}  ({p_hit_7*100:.2f}%)")

# Binomial tail probability
from scipy.stats import binom

p_binom_5 = 1 - binom.cdf(obs_5pct - 1, N_SYSTEMS, p_hit_5)
p_binom_7 = 1 - binom.cdf(obs_7pct - 1, N_SYSTEMS, p_hit_7)

print(f"P(≥{obs_5pct} of {N_SYSTEMS} in 5% window) = {p_binom_5:.6f}  (binomial exact)")
print(f"P(≥{obs_7pct} of {N_SYSTEMS} in 7% window) = {p_binom_7:.6f}  (binomial exact)")

# ── Predictive structure test ─────────────────────────────────────
print("\n\nPREDICTIVE STRUCTURE TEST:")
print("-" * 70)
print("The framework predicts IN ADVANCE which systems should hit φ")
print("(free-running engines) and which should miss (forced/managed).")
print()
print("Pre-specified 'predicted hit' group (5 systems):")
print("  Breath, SCS hydrograph, Watershed V2, Walk speed, Solar")
print("Pre-specified 'predicted miss' group (7 systems):")
print("  Gait (constrained), glucose, crypto, EEG×2, sea ice, Cepheid")
print()

# Observed: all 4 systems within 5% came from the 5-member "hit" group
# What's the probability that if 4 random systems out of 12 are "hits",
# ALL 4 come from a pre-specified subset of 5?

from scipy.special import comb

# Hypergeometric: drawing 4 successes from a population of 12 where 5 are "special"
# P(all 4 from the 5-member group) = C(5,4) × C(7,0) / C(12,4)
p_predict = comb(5, 4, exact=True) * comb(7, 0, exact=True) / comb(12, 4, exact=True)
print(f"P(all {obs_5pct} hits come from pre-specified 5-member group) = {p_predict:.6f}")
print(f"  = {comb(5,4,exact=True)} × {comb(7,0,exact=True)} / {comb(12,4,exact=True)}")
print(f"  = {p_predict:.4f}  (1 in {1/p_predict:.0f})")

# Combined test: P(≥4 within 5%) × P(all from predicted group)
# This is conservative (assumes independence)
for name, (p5, p7) in results.items():
    combined = p5 * p_predict
    print(f"\n  Combined [{name}]:")
    print(f"    P(≥4 in 5%) × P(all from predicted) = {p5:.6f} × {p_predict:.6f} = {combined:.8f}")
    if combined > 0:
        print(f"    = 1 in {1/combined:,.0f}")

# ── Summary ───────────────────────────────────────────────────────
print("\n\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
CLUSTERING TEST:
  Across all 5 null distributions, the probability of getting
  {obs_5pct} or more systems within 5% of φ by chance ranges from
  {min(r[0] for r in results.values()):.6f} to {max(r[0] for r in results.values()):.6f}.

PREDICTIVE STRUCTURE:
  The probability that all {obs_5pct} hits come from a pre-specified
  5-member subset (out of 12) is {p_predict:.4f} (1 in {1/p_predict:.0f}).

COMBINED (conservative):
  The joint probability — getting this many hits AND having them
  all fall in the predicted group — is the product of these two
  independent probabilities.

INTERPRETATION:
  If the clustering p-value is low (< 0.05), the pattern is unlikely
  to be pure chance. If the predictive structure p-value is also low,
  the framework is not just finding φ — it's finding it where it
  predicted it would be and NOT finding it where it predicted it
  wouldn't be.

  The predictive structure test is arguably more important than the
  clustering test, because it addresses the Texas Sharpshooter concern
  directly: the target was drawn BEFORE the bullets were fired.
""")
