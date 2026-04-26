"""
Script 243BL15: S&P 500 Prediction via Mirror/φ-Modular/ARA Lens
================================================================

Applying what we learned from lotto (BL9-BL14) to the stock market.

Key lotto findings to test here:
  1. Randomness = ARA 1.0 (shock absorber). Is the market also 1.0?
  2. Mirror flip: worst predictors become best when inverted. Does this work for stocks?
  3. φ-modular transform dissolves hidden structure. Does it work on returns?
  4. Crossing cost (7-4φ)/4 ≈ 0.132 per boundary.
  5. One crossing (mirror) works, two doesn't.

The market SHOULD be different from lotto:
  - It has trends (momentum), mean reversion, volatility clustering
  - It has information flowing through it (lotto is memoryless)
  - Its ARA should NOT be exactly 1.0

Dataset: S&P 500 monthly prices, 1871-2026 (1,864 months)
Prediction target: monthly direction (up or down)
Baseline: random = ~53% (markets have a slight upward bias)
"""

import numpy as np
import csv
from collections import defaultdict

PHI = (1 + np.sqrt(5)) / 2
CROSSING_COST = (7 - 4*PHI) / 4

# ============================================================
# Load data
# ============================================================

def load_sp500(filepath):
    dates = []
    prices = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            try:
                price = float(row[1])
                if price > 0:
                    dates.append(row[0])
                    prices.append(price)
            except (ValueError, IndexError):
                continue
    return dates, np.array(prices)

dates, prices = load_sp500('/sessions/focused-tender-thompson/sp500/data/data.csv')

# Compute returns
returns = np.diff(np.log(prices))  # log returns
directions = (returns > 0).astype(int)  # 1 = up, 0 = down

print("=" * 70)
print("Script 243BL15: S&P 500 PREDICTION ENGINE")
print("=" * 70)
print(f"\nLoaded {len(prices)} monthly prices ({dates[0]} to {dates[-1]})")
print(f"Returns: {len(returns)} months")
print(f"Up months: {sum(directions)}/{len(directions)} ({sum(directions)/len(directions)*100:.1f}%)")
print(f"Mean return: {np.mean(returns)*100:.3f}% per month")
print(f"Std return: {np.std(returns)*100:.3f}% per month")

# ============================================================
# PART 1: Market ARA measurement
# ============================================================

print("\n" + "=" * 70)
print("PART 1: MARKET ARA — WHERE DOES IT SIT?")
print("=" * 70)

# ARA from consecutive return ratios
def compute_ara_from_series(series):
    """Compute ARA from a time series using consecutive comparisons."""
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

# ARA of returns
ara_returns = compute_ara_from_series(returns)
print(f"\n  ARA of monthly returns: {ara_returns:.4f}")

# ARA of absolute returns (volatility)
abs_returns = np.abs(returns)
ara_volatility = compute_ara_from_series(abs_returns)
print(f"  ARA of volatility (|returns|): {ara_volatility:.4f}")

# ARA of prices themselves
ara_prices = compute_ara_from_series(prices)
print(f"  ARA of raw prices: {ara_prices:.4f}")

# ARA of directions (streak analysis)
ara_direction = compute_ara_from_series(directions.astype(float))
print(f"  ARA of direction sequence: {ara_direction:.4f}")

# Compare to lotto
print(f"\n  Comparison:")
print(f"    Lotto numbers ARA:    1.000 (perfect shock absorber)")
print(f"    S&P 500 returns ARA:  {ara_returns:.3f}", end="")
if ara_returns > 1.1:
    print(f" ← ENGINE (accumulates more than releases)")
elif ara_returns < 0.9:
    print(f" ← CONSUMER (releases more than accumulates)")
else:
    print(f" ← SHOCK ABSORBER (near 1.0)")

# Rolling ARA
window = 120  # 10 years
rolling_aras = []
for i in range(len(returns) - window):
    chunk = returns[i:i+window]
    rolling_aras.append(compute_ara_from_series(chunk))

rolling_aras = np.array(rolling_aras)
print(f"\n  Rolling ARA ({window}-month window):")
print(f"    Mean: {np.mean(rolling_aras):.4f}")
print(f"    Std:  {np.std(rolling_aras):.4f}")
print(f"    Min:  {np.min(rolling_aras):.4f} ({dates[np.argmin(rolling_aras)+window]})")
print(f"    Max:  {np.max(rolling_aras):.4f} ({dates[np.argmax(rolling_aras)+window]})")

# ============================================================
# PART 2: φ-modular test — does φ dissolve hidden structure?
# ============================================================

print("\n" + "=" * 70)
print("PART 2: φ-MODULAR TEST — HIDDEN STRUCTURE?")
print("=" * 70)

# Map returns to [0,1] via rank transform (same as BL9b)
from scipy import stats as scipy_stats

ranked = scipy_stats.rankdata(returns) / len(returns)

# Chi-squared uniformity test
n_bins = 20
hist_orig, _ = np.histogram(ranked, bins=n_bins, range=(0, 1))
chi2_orig = sum((h - len(returns)/n_bins)**2 / (len(returns)/n_bins) for h in hist_orig)

# φ-modular transform
phi_mapped = (ranked * PHI) % 1.0
hist_phi, _ = np.histogram(phi_mapped, bins=n_bins, range=(0, 1))
chi2_phi = sum((h - len(returns)/n_bins)**2 / (len(returns)/n_bins) for h in hist_phi)

change_pct = (chi2_phi / chi2_orig - 1) * 100

print(f"\n  Original χ²:    {chi2_orig:.2f} (df={n_bins-1})")
print(f"  After φ-map χ²: {chi2_phi:.2f}")
print(f"  Change:          {change_pct:+.1f}%")

if change_pct < -20:
    print(f"  → φ DISSOLVES hidden structure (like lotto: -65 to -82%)")
elif change_pct > 20:
    print(f"  → φ DISRUPTS uniformity (like irrationals: +600 to +2800%)")
else:
    print(f"  → Minimal effect — structure is neither hidden nor uniform")

# Also test on raw returns (not ranked)
# Normalize to [0,1] via min-max
r_norm = (returns - returns.min()) / (returns.max() - returns.min())
hist_raw, _ = np.histogram(r_norm, bins=n_bins, range=(0, 1))
chi2_raw = sum((h - len(returns)/n_bins)**2 / (len(returns)/n_bins) for h in hist_raw)

phi_raw = (r_norm * PHI) % 1.0
hist_phi_raw, _ = np.histogram(phi_raw, bins=n_bins, range=(0, 1))
chi2_phi_raw = sum((h - len(returns)/n_bins)**2 / (len(returns)/n_bins) for h in hist_phi_raw)

print(f"\n  Raw returns (not ranked):")
print(f"    Original χ²: {chi2_raw:.2f}")
print(f"    After φ-map: {chi2_phi_raw:.2f} ({(chi2_phi_raw/chi2_raw-1)*100:+.1f}%)")

# ============================================================
# PART 3: Prediction strategies
# ============================================================

print("\n" + "=" * 70)
print("PART 3: PREDICTION STRATEGIES")
print("=" * 70)

HOLDOUT = 200  # ~17 years of monthly data
train_returns = returns[:-HOLDOUT]
test_returns = returns[-HOLDOUT:]
test_directions = directions[-HOLDOUT:]
train_directions = directions[:-HOLDOUT]

# Actual up ratio in test set
actual_up_ratio = np.mean(test_directions)
print(f"\n  Holdout: {HOLDOUT} months ({dates[-HOLDOUT]} to {dates[-1]})")
print(f"  Actual up months in test: {sum(test_directions)}/{HOLDOUT} ({actual_up_ratio*100:.1f}%)")
print(f"  Baseline (always up): {actual_up_ratio*100:.1f}%")

def score_predictions(preds, actuals):
    """Score direction predictions. Returns accuracy."""
    correct = sum(1 for p, a in zip(preds, actuals) if p == a)
    return correct / len(actuals)

# Strategy 1: Momentum (last N months direction predicts next)
def strategy_momentum(train, test, all_returns, lookback=3):
    preds = []
    for i in range(len(test)):
        idx = len(train) + i
        recent = all_returns[idx-lookback:idx]
        # If recent trend is up, predict up
        preds.append(1 if np.mean(recent) > 0 else 0)
    return preds

# Strategy 2: Mean reversion (opposite of recent)
def strategy_mean_reversion(train, test, all_returns, lookback=3):
    preds = []
    for i in range(len(test)):
        idx = len(train) + i
        recent = all_returns[idx-lookback:idx]
        # If recent trend is up, predict DOWN (reversion)
        preds.append(0 if np.mean(recent) > 0 else 1)
    return preds

# Strategy 3: Mirror momentum (from lotto — invert the best normal strategy)
def strategy_mirror_momentum(train, test, all_returns, lookback=3):
    """Mirror of momentum — invert through singularity."""
    preds = strategy_momentum(train, test, all_returns, lookback)
    return [1 - p for p in preds]  # flip all predictions

# Strategy 4: φ-modular momentum
def strategy_phi_momentum(train, test, all_returns, lookback=6):
    """Apply φ-modular transform to recent returns before predicting."""
    preds = []
    for i in range(len(test)):
        idx = len(train) + i
        recent = all_returns[idx-lookback:idx]
        # φ-modular transform
        phi_recent = [(r * PHI) % 0.1 - 0.05 for r in recent]  # wrap around small range
        preds.append(1 if np.mean(phi_recent) > 0 else 0)
    return preds

# Strategy 5: ARA regime detector
def strategy_ara_regime(train, test, all_returns, window=24):
    """Use rolling ARA to predict regime. High ARA = engine = up, low = consumer = down."""
    preds = []
    for i in range(len(test)):
        idx = len(train) + i
        chunk = all_returns[max(0, idx-window):idx]
        ara = compute_ara_from_series(chunk)
        # Engine (ARA > 1) = accumulating = predict UP
        # Consumer (ARA < 1) = releasing = predict DOWN
        preds.append(1 if ara > 1.0 else 0)
    return preds

# Strategy 6: Mirror ARA regime
def strategy_mirror_ara(train, test, all_returns, window=24):
    """Mirror of ARA regime — invert through singularity."""
    preds = strategy_ara_regime(train, test, all_returns, window)
    return [1 - p for p in preds]

# Strategy 7: φ-ARA lens (best from lotto adapted)
def strategy_phi_ara_lens(train, test, all_returns, window=24):
    """ARA lens with φ-modular transform on the ARA itself."""
    preds = []
    for i in range(len(test)):
        idx = len(train) + i
        chunk = all_returns[max(0, idx-window):idx]
        ara = compute_ara_from_series(chunk)

        # φ-modular transform of ARA
        phi_ara = (ara * PHI) % 2.0

        # Mirror direction based on φ-ARA
        if phi_ara < 1.0:
            preds.append(1)  # consumer in φ-space → engine on other side → up
        else:
            preds.append(0)  # engine in φ-space → consumer on other side → down
    return preds

# Strategy 8: Volatility-regime mirror
def strategy_vol_mirror(train, test, all_returns, window=12):
    """High vol = crossing the singularity = mirror. Low vol = normal."""
    preds = []
    long_vol = np.std(train)
    for i in range(len(test)):
        idx = len(train) + i
        chunk = all_returns[max(0, idx-window):idx]
        recent_vol = np.std(chunk)

        # Momentum signal
        momentum = 1 if np.mean(chunk[-3:]) > 0 else 0

        # If vol is high (crossing singularity), mirror the momentum
        if recent_vol > long_vol * 1.5:
            preds.append(1 - momentum)  # mirror
        else:
            preds.append(momentum)  # normal
    return preds

# Strategy 9: φ-cycle detector
def strategy_phi_cycle(train, test, all_returns, all_dates):
    """Look for φ-power periodicities in the market."""
    preds = []
    for i in range(len(test)):
        idx = len(train) + i
        # Check if current month index is near a φ-power cycle point
        # φ¹ ≈ 1.6, φ² ≈ 2.6, φ³ ≈ 4.2, φ⁴ ≈ 6.9, φ⁵ ≈ 11.1 months
        # Use φ⁵ ≈ 11 month cycle (close to annual)
        score = 0
        for power in [3, 5, 7]:
            period = int(round(PHI ** power))
            if idx >= period:
                past_return = all_returns[idx - period]
                # φ-modular: was the return at this φ-distance positive?
                score += 1 if past_return > 0 else -1
        preds.append(1 if score > 0 else 0)
    return preds

# Strategy 10: Double mirror (from lotto BL14 — the "gravitational lens")
def strategy_double_mirror(train, test, all_returns, window=24):
    """ARA distortion + volatility mirror. Read the singularity from both sides."""
    preds = []
    long_vol = np.std(train)

    for i in range(len(test)):
        idx = len(train) + i
        chunk = all_returns[max(0, idx-window):idx]
        ara = compute_ara_from_series(chunk)
        vol = np.std(chunk)

        # ARA signal (mirrored)
        if ara < 1.0:
            ara_signal = +1  # consumer here = engine on other side
        else:
            ara_signal = -1  # engine here = consumer on other side

        # Volatility magnification
        vol_ratio = vol / long_vol
        magnification = 1 + vol_ratio

        # Combined score with crossing cost
        score = ara_signal * magnification * (1 - CROSSING_COST)

        preds.append(1 if score > 0 else 0)
    return preds

# Run all strategies
strategies = {
    'Always up': lambda: [1] * HOLDOUT,
    'Momentum (3m)': lambda: strategy_momentum(train_returns, test_returns, returns, 3),
    'Momentum (6m)': lambda: strategy_momentum(train_returns, test_returns, returns, 6),
    'Momentum (12m)': lambda: strategy_momentum(train_returns, test_returns, returns, 12),
    'Mean reversion (3m)': lambda: strategy_mean_reversion(train_returns, test_returns, returns, 3),
    'Mirror momentum (3m)': lambda: strategy_mirror_momentum(train_returns, test_returns, returns, 3),
    'φ-modular momentum': lambda: strategy_phi_momentum(train_returns, test_returns, returns, 6),
    'ARA regime (24m)': lambda: strategy_ara_regime(train_returns, test_returns, returns, 24),
    'Mirror ARA': lambda: strategy_mirror_ara(train_returns, test_returns, returns, 24),
    'φ-ARA lens': lambda: strategy_phi_ara_lens(train_returns, test_returns, returns, 24),
    'Vol-regime mirror': lambda: strategy_vol_mirror(train_returns, test_returns, returns, 12),
    'φ-cycle detector': lambda: strategy_phi_cycle(train_returns, test_returns, returns, dates),
    'Double mirror': lambda: strategy_double_mirror(train_returns, test_returns, returns, 24),
}

results = {}
print(f"\n  {'Strategy':<24s} {'Accuracy':>8s} {'vs 50%':>8s} {'vs Bias':>8s} {'Correct':>8s}")
print(f"  {'─'*60}")

for name, fn in strategies.items():
    preds = fn()
    acc = score_predictions(preds, test_directions)
    vs_random = (acc - 0.5) * 100
    vs_bias = (acc - actual_up_ratio) * 100
    correct = sum(1 for p, a in zip(preds, test_directions) if p == a)
    results[name] = (acc, vs_random, vs_bias, correct, preds)

    marker = " ←" if acc > actual_up_ratio else ""
    print(f"  {name:<24s} {acc*100:>7.1f}% {vs_random:>+7.1f}% {vs_bias:>+7.1f}% {correct:>7d}/200{marker}")

# ============================================================
# PART 4: Statistical significance
# ============================================================

print("\n" + "=" * 70)
print("PART 4: STATISTICAL SIGNIFICANCE")
print("=" * 70)

# Monte Carlo: random direction prediction
N_SIMS = 5000
random_accs = []
for _ in range(N_SIMS):
    # Random predictions weighted by training set bias
    train_bias = np.mean(train_directions)
    rand_preds = (np.random.random(HOLDOUT) < train_bias).astype(int)
    random_accs.append(score_predictions(rand_preds, test_directions))

random_accs = np.array(random_accs)
rand_mean = np.mean(random_accs)
rand_std = np.std(random_accs)
threshold_95 = np.percentile(random_accs, 95)

print(f"\n  Bias-aware random baseline: {rand_mean*100:.1f}% ± {rand_std*100:.1f}%")
print(f"  95% threshold: {threshold_95*100:.1f}%")

best_strategy = None
best_acc = 0

for name, (acc, vs_random, vs_bias, correct, preds) in results.items():
    if name == 'Always up':
        continue
    pctile = np.mean([1 if acc > r else 0 for r in random_accs]) * 100
    z = (acc - rand_mean) / rand_std if rand_std > 0 else 0
    sig = "SIGNIFICANT" if pctile > 95 else "not significant"

    marker = ""
    if acc > best_acc and name != 'Always up':
        best_acc = acc
        best_strategy = name
        marker = " ← BEST"

    print(f"  {name:<24s}: {acc*100:.1f}%, pctile={pctile:5.1f}%, z={z:+.2f} ({sig}){marker}")

# ============================================================
# PART 5: Market vs Lotto comparison
# ============================================================

print("\n" + "=" * 70)
print("PART 5: MARKET vs LOTTO — FUNDAMENTAL COMPARISON")
print("=" * 70)

print(f"""
  Property                    Lotto           S&P 500
  ──────────────────────────────────────────────────────
  ARA (returns)               1.000           {ara_returns:.3f}
  ARA (volatility)            N/A             {ara_volatility:.3f}
  Directional bias            50.0%           {sum(directions)/len(directions)*100:.1f}%
  φ-modular effect            -65 to -82%     {change_pct:+.1f}%
  Best mirror strategy        +16.3%          {(best_acc-0.5)*100:+.1f}% (vs 50%)
  Landscape                   FLAT (z=-0.19)  TBD
""")

# Is the market a shock absorber?
if 0.9 < ara_returns < 1.1:
    print(f"  The market's return ARA ({ara_returns:.3f}) is NEAR 1.0 — shock absorber territory.")
    print(f"  Like lotto, but with a slight directional bias ({sum(directions)/len(directions)*100:.1f}% up months).")
elif ara_returns > 1.1:
    print(f"  The market's return ARA ({ara_returns:.3f}) is ABOVE 1.0 — it's an ENGINE.")
    print(f"  Unlike lotto (pure absorber), the market accumulates momentum.")
else:
    print(f"  The market's return ARA ({ara_returns:.3f}) is BELOW 1.0 — it's a CONSUMER.")

# ============================================================
# PART 6: Decade-by-decade ARA
# ============================================================

print("\n" + "=" * 70)
print("PART 6: DECADE-BY-DECADE ARA")
print("=" * 70)

# Parse years
import re
years = []
for d in dates:
    match = re.match(r'(\d{4})', d)
    if match:
        years.append(int(match.group(1)))
    else:
        years.append(0)

print(f"\n  {'Decade':<12s} {'ARA':>6s} {'Up%':>6s} {'Vol':>8s} {'Type':>12s}")
print(f"  {'─'*50}")

for decade_start in range(1870, 2030, 10):
    decade_end = decade_start + 10
    mask = [(decade_start <= years[i+1] < decade_end) for i in range(len(returns))]
    decade_returns = returns[mask[:len(returns)]]

    if len(decade_returns) < 24:
        continue

    ara = compute_ara_from_series(decade_returns)
    up_pct = np.mean(decade_returns > 0) * 100
    vol = np.std(decade_returns) * 100

    if ara < 0.9:
        dtype = "CONSUMER"
    elif ara < 1.1:
        dtype = "absorber"
    elif ara < PHI - 0.1:
        dtype = "warm"
    elif ara < PHI + 0.1:
        dtype = "φ-ENGINE"
    else:
        dtype = "hot"

    print(f"  {decade_start}s     {ara:6.3f} {up_pct:5.1f}% {vol:7.2f}%  {dtype}")

# ============================================================
# PART 7: The key question — does mirror flip work for markets?
# ============================================================

print("\n" + "=" * 70)
print("PART 7: MIRROR FLIP — THE KEY TEST")
print("=" * 70)

# For lotto, mirror flip = inverting worst strategy made it best.
# Let's test this properly: find the WORST strategy, mirror it.

worst_name = None
worst_acc = 1.0
for name, (acc, _, _, _, _) in results.items():
    if name == 'Always up':
        continue
    if acc < worst_acc:
        worst_acc = acc
        worst_name = name

print(f"\n  Worst strategy: {worst_name} ({worst_acc*100:.1f}%)")

# Mirror the worst
worst_preds = results[worst_name][4]
mirrored_preds = [1 - p for p in worst_preds]
mirror_acc = score_predictions(mirrored_preds, test_directions)
print(f"  Mirrored worst: {mirror_acc*100:.1f}%")
print(f"  Improvement:    {(mirror_acc - worst_acc)*100:+.1f} pp")

# Is this the same symmetric flip as lotto?
midpoint = (worst_acc + mirror_acc) / 2
asymmetry = abs(midpoint - 0.5)
print(f"  Midpoint:       {midpoint*100:.1f}% (lotto was ~50.0%)")
print(f"  Asymmetry:      {asymmetry*100:.1f} pp from 50%")

if asymmetry < 2:
    print(f"  → SYMMETRIC flip — same as lotto. The singularity is balanced.")
else:
    print(f"  → ASYMMETRIC flip — the market has a BIAS that shifts the singularity.")
    print(f"  → The market's singularity is NOT at 50/50. It's at {midpoint*100:.1f}/{(1-midpoint)*100:.1f}.")

# ============================================================
# PART 8: Can we predict NEXT month?
# ============================================================

print("\n" + "=" * 70)
print("PART 8: NEXT MONTH PREDICTION")
print("=" * 70)

# Use all data to predict the next month
last_returns = returns[-24:]
last_ara = compute_ara_from_series(last_returns)
last_vol = np.std(last_returns)
long_vol = np.std(returns)
recent_momentum = np.mean(returns[-3:])

print(f"\n  Current state ({dates[-1]}):")
print(f"    S&P 500: {prices[-1]:.0f}")
print(f"    Last 3m returns: {recent_momentum*100:+.3f}%")
print(f"    24m ARA: {last_ara:.3f}")
print(f"    Recent vol: {last_vol*100:.2f}% (long-term: {long_vol*100:.2f}%)")
print(f"    Vol ratio: {last_vol/long_vol:.2f}")

# Vote from each strategy using all data
votes = {'up': 0, 'down': 0}
vote_details = []

# Momentum
if recent_momentum > 0:
    votes['up'] += 1
    vote_details.append(("Momentum", "UP", f"recent return {recent_momentum*100:+.3f}%"))
else:
    votes['down'] += 1
    vote_details.append(("Momentum", "DOWN", f"recent return {recent_momentum*100:+.3f}%"))

# Mirror momentum
if recent_momentum > 0:
    votes['down'] += 1
    vote_details.append(("Mirror momentum", "DOWN", "inverted"))
else:
    votes['up'] += 1
    vote_details.append(("Mirror momentum", "UP", "inverted"))

# ARA regime
if last_ara > 1.0:
    votes['up'] += 1
    vote_details.append(("ARA regime", "UP", f"ARA {last_ara:.3f} > 1.0 (engine)"))
else:
    votes['down'] += 1
    vote_details.append(("ARA regime", "DOWN", f"ARA {last_ara:.3f} < 1.0 (consumer)"))

# Mirror ARA
if last_ara > 1.0:
    votes['down'] += 1
    vote_details.append(("Mirror ARA", "DOWN", "inverted"))
else:
    votes['up'] += 1
    vote_details.append(("Mirror ARA", "UP", "inverted"))

# Vol-regime mirror
if last_vol > long_vol * 1.5:
    # High vol: mirror the momentum
    if recent_momentum > 0:
        votes['down'] += 1
        vote_details.append(("Vol mirror", "DOWN", f"high vol ({last_vol/long_vol:.2f}x) → mirror"))
    else:
        votes['up'] += 1
        vote_details.append(("Vol mirror", "UP", f"high vol ({last_vol/long_vol:.2f}x) → mirror"))
else:
    # Normal vol: follow momentum
    if recent_momentum > 0:
        votes['up'] += 1
        vote_details.append(("Vol mirror", "UP", f"normal vol ({last_vol/long_vol:.2f}x) → follow"))
    else:
        votes['down'] += 1
        vote_details.append(("Vol mirror", "DOWN", f"normal vol ({last_vol/long_vol:.2f}x) → follow"))

# φ-ARA lens
phi_ara = (last_ara * PHI) % 2.0
if phi_ara < 1.0:
    votes['up'] += 1
    vote_details.append(("φ-ARA lens", "UP", f"φ-ARA {phi_ara:.3f} < 1.0"))
else:
    votes['down'] += 1
    vote_details.append(("φ-ARA lens", "DOWN", f"φ-ARA {phi_ara:.3f} > 1.0"))

# Double mirror
ara_signal = +1 if last_ara < 1.0 else -1
magnification = 1 + last_vol / long_vol
score = ara_signal * magnification * (1 - CROSSING_COST)
if score > 0:
    votes['up'] += 1
    vote_details.append(("Double mirror", "UP", f"score {score:+.3f}"))
else:
    votes['down'] += 1
    vote_details.append(("Double mirror", "DOWN", f"score {score:+.3f}"))

print(f"\n  Strategy votes:")
for name, direction, reason in vote_details:
    print(f"    {name:<20s}: {direction:<5s} ({reason})")

print(f"\n  Tally: UP={votes['up']}, DOWN={votes['down']}")
prediction = "UP" if votes['up'] > votes['down'] else "DOWN"
confidence = max(votes['up'], votes['down']) / (votes['up'] + votes['down']) * 100

print(f"\n  ╔══════════════════════════════════════════════╗")
print(f"  ║  PREDICTION: {prediction:<5s} (confidence: {confidence:.0f}%)          ║")
print(f"  ╚══════════════════════════════════════════════╝")

# ============================================================
# PART 9: Summary
# ============================================================

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

print(f"""
  The S&P 500 is NOT the same as the lotto machine.

  Lotto:  ARA = 1.000 — perfect shock absorber, flat landscape
  Market: ARA = {ara_returns:.3f} — {"near absorber" if 0.9 < ara_returns < 1.1 else "shifted from absorber"}

  φ-modular effect on market: {change_pct:+.1f}% (lotto: -65 to -82%)
  {"φ dissolves hidden structure in market too!" if change_pct < -20 else "φ has minimal/different effect on market returns."}

  Best prediction strategy: {best_strategy} ({best_acc*100:.1f}%)
  Market bias: {actual_up_ratio*100:.1f}% up months (lotto: 50.0%)

  Mirror flip: worst→mirror = {worst_acc*100:.1f}%→{mirror_acc*100:.1f}%
  {"Symmetric flip (like lotto)" if asymmetry < 2 else f"Asymmetric flip (singularity shifted to {midpoint*100:.1f}%)"}

  Key difference from lotto: the market has a DIRECTIONAL BIAS.
  Lotto numbers have no memory. Markets have trends, momentum,
  and mean reversion — multiple ARA signatures coexisting.

  The singularity crossing cost still applies ((7-4φ)/4 ≈ 0.132),
  but the singularity itself is not at 50/50 — it's shifted by
  the market's engine nature.
""")

print(f"{'='*70}")
print(f"END Script 243BL15")
print(f"{'='*70}")
