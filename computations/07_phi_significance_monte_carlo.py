import math
import random
random.seed(42)

phi = (1 + math.sqrt(5)) / 2
log_phi = math.log10(phi)  # 0.20898

gaps = [0.577, 1.172, 1.365, 1.569, 1.854, 2.000, 4.431, 5.255, 8.840, 8.888, 9.431]

def fit_score(data, period):
    """Mean squared fractional residual from nearest integer multiple."""
    total = 0
    for g in data:
        n = round(g / period)
        if n == 0: n = 1
        residual = abs(g / period - n)
        total += residual ** 2
    return total / len(data)

our_score = fit_score(gaps, log_phi)
print(f"phi spacing (log10(phi) = {log_phi:.4f})")
print(f"Our data fit score: {our_score:.6f}")
print()

# Monte Carlo with fewer trials to avoid timeout
n_trials = 50000
n_better = 0
gap_min = min(gaps)
gap_max = max(gaps)

for _ in range(n_trials):
    random_gaps = [random.uniform(gap_min, gap_max) for _ in range(len(gaps))]
    score = fit_score(random_gaps, log_phi)
    if score <= our_score:
        n_better += 1

p_phi = n_better / n_trials
print(f"Monte Carlo (uniform on [{gap_min:.1f}, {gap_max:.1f}]):")
print(f"  Random data fitting phi this well: {n_better}/{n_trials}")
print(f"  p-value: {p_phi:.6f}")
print()

# Best-fit period search (use coarser grid for speed)
test_periods = [i * 0.005 for i in range(20, 401)]  # 0.1 to 2.0, step 0.005
our_best_period = None
our_best_score = float('inf')
for p in test_periods:
    s = fit_score(gaps, p)
    if s < our_best_score:
        our_best_score = s
        our_best_period = p

print(f"Best-fit period (coarse grid): {our_best_period:.4f}")
print(f"Best-fit score: {our_best_score:.6f}")
print(f"log10(phi) = {log_phi:.4f}  (diff: {abs(our_best_period-log_phi)/log_phi*100:.1f}%)")
print()

# Proper null: best-fit period for random data
n_trials_2 = 20000
n_better_2 = 0
n_near_phi = 0

for trial in range(n_trials_2):
    random_gaps = [random.uniform(gap_min, gap_max) for _ in range(len(gaps))]
    best_score = float('inf')
    best_p = None
    for p in test_periods:
        s = fit_score(random_gaps, p)
        if s < best_score:
            best_score = s
            best_p = p
    if best_score <= our_best_score:
        n_better_2 += 1
    if abs(best_p - log_phi) / log_phi < 0.05:
        n_near_phi += 1

p_proper = n_better_2 / n_trials_2
print(f"Periodicity significance (proper null):")
print(f"  Random achieving this fit quality: {n_better_2}/{n_trials_2}")
print(f"  p-value: {p_proper:.6f}")
print()

pct_near_phi = n_near_phi / n_trials_2 * 100
print(f"Random datasets whose best-fit period is within 5% of log10(phi):")
print(f"  {n_near_phi}/{n_trials_2} ({pct_near_phi:.1f}%)")
print()

# Verdict
print("=" * 70)
print("VERDICT")
print("=" * 70)
print()
print(f"1. Fit to phi spacing: p = {p_phi:.6f}")
if p_phi < 0.05:
    print("   -> SIGNIFICANT: gaps fit phi better than random")
else:
    print("   -> Not significant at p < 0.05")
    
print(f"\n2. Periodicity (any spacing): p = {p_proper:.6f}")
if p_proper < 0.05:
    print("   -> SIGNIFICANT: data has more periodicity than random")
else:
    print("   -> Not significant at p < 0.05")

print(f"\n3. Is phi SPECIFICALLY the period? {pct_near_phi:.1f}% of random data peaks near phi")
if pct_near_phi < 3:
    print("   -> Yes, finding phi specifically is unlikely by chance")
elif pct_near_phi < 8:
    print("   -> Marginal — phi is somewhat favored but could be geometric coincidence")
else:
    print("   -> No — random data often peaks near phi too")

# One more check: log10(2) = 0.3010 also scored well. 
# Is the data distinguishing phi from log10(2)?
score_phi = fit_score(gaps, log_phi)
score_log2 = fit_score(gaps, math.log10(2))
score_0p2 = fit_score(gaps, 0.200)
print(f"\nDirect comparison:")
print(f"  fit_score(log10(phi)) = {score_phi:.6f}")
print(f"  fit_score(log10(2))   = {score_log2:.6f}")
print(f"  fit_score(0.200)      = {score_0p2:.6f}")
print()
print(f"  phi vs log2 difference: {abs(score_phi - score_log2):.6f}")
print(f"  With only 11 data points, this difference is {'meaningful' if abs(score_phi-score_log2) > 0.005 else 'negligible'}.")

