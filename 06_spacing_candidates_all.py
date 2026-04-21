import math
import random
random.seed(42)

# =============================================================
# TEST ALL CANDIDATE SPACINGS
#
# The 4π claim broke under scrutiny. Let's test EVERY reasonable
# candidate against the tightened gap data and see what (if 
# anything) actually fits.
#
# Also: Dylan's φ insight and the "smallest/largest circle" idea.
# =============================================================

pi = math.pi
phi = (1 + math.sqrt(5)) / 2  # 1.61803...
hbar = 1.0546e-34

# The tightened gaps (> 0.5 orders of magnitude)
gaps = [0.577, 1.172, 1.365, 1.569, 1.854, 2.000, 4.431, 5.255, 8.840, 8.888, 9.431]

# ALL gaps (including small ones)
all_gaps = [0.423, 0.577, 2.000, 8.889, 0.477, 8.840, 4.431, 1.365, 5.255,
            9.431, 1.569, 0.041, 1.172, 1.854, 0.093]

# Candidate spacings (log₁₀ values)
candidates = {
    "1 (decade)":         1.0000,
    "π":                  math.log10(pi),          # 0.4971
    "2π":                 math.log10(2*pi),        # 0.7982
    "4π":                 math.log10(4*pi),        # 1.0992
    "(2π)²":              math.log10((2*pi)**2),   # 1.5964
    "φ":                  math.log10(phi),         # 0.2090
    "φ²":                 math.log10(phi**2),      # 0.4181
    "2φ":                 math.log10(2*phi),       # 0.5099
    "π×φ":               math.log10(pi*phi),      # 0.7061
    "2π/φ":              math.log10(2*pi/phi),    # 0.5892
    "e":                  math.log10(math.e),      # 0.4343
    "e²":                 math.log10(math.e**2),   # 0.8686
    "10":                 1.0000,
    "√10":               0.5000,
    "2":                  math.log10(2),           # 0.3010
    "3":                  math.log10(3),           # 0.4771
}

print("=" * 80)
print("CANDIDATE SPACINGS — FIT TO TIGHTENED GAP DATA")
print("=" * 80)
print()
print("Method: For each candidate spacing S, check whether gaps are")
print("approximate integer multiples of S. Compute mean fractional error.")
print()
print(f"{'Candidate':<15s} {'log₁₀ value':<12s} {'Mean frac err':<15s} {'Best fits':<40s}")
print("-" * 85)

results = []
for name, spacing in sorted(candidates.items(), key=lambda x: x[1]):
    # For each gap, find nearest integer multiple of spacing
    total_err = 0
    fits = []
    for g in gaps:
        n = round(g / spacing)
        if n == 0:
            n = 1
        predicted = n * spacing
        err = abs(g - predicted) / predicted
        total_err += err
        fits.append((g, n, err))
    
    mean_err = total_err / len(gaps)
    good_fits = [(g, n, e) for g, n, e in fits if e < 0.10]
    results.append((name, spacing, mean_err, good_fits))
    
    fit_str = ", ".join([f"{g:.2f}≈{n}×" for g, n, e in good_fits[:4]])
    print(f"{name:<15s} {spacing:<12.4f} {mean_err:<15.4f} {fit_str:<40s}")

# Sort by best fit
print()
print("RANKED BY FIT QUALITY:")
print("-" * 60)
for name, spacing, mean_err, good_fits in sorted(results, key=lambda x: x[2]):
    pct_good = len(good_fits) / len(gaps) * 100
    print(f"  {name:<15s}  mean_err = {mean_err:.4f}  hits = {len(good_fits)}/{len(gaps)} ({pct_good:.0f}%)")

print()
print("=" * 80)
print("KEY INSIGHT: What spacing makes ALL gaps integer multiples?")
print("=" * 80)
print()

# GCD-like approach: find the fundamental spacing that divides all gaps
# If there's a "fundamental rung", all gaps should be multiples of it
# Use continuous GCD: find smallest S such that all gaps ≈ n×S

# Try: S = gap between each pair of close gaps
# The gaps sorted: 0.577, 1.172, 1.365, 1.569, 1.854, 2.000, 4.431, 5.255, 8.840, 8.888, 9.431
# Differences between adjacent: 0.595, 0.193, 0.204, 0.285, 0.146, 2.431, 0.824, 3.585, 0.048, 0.543

# Better approach: frequency analysis
# What period best fits the gap distribution?

print("Frequency analysis: testing fundamental periods 0.1 to 2.0")
print()

best_period = None
best_score = float('inf')
test_periods = [i * 0.001 for i in range(100, 2001)]

for period in test_periods:
    score = 0
    for g in gaps:
        n = round(g / period)
        if n == 0:
            n = 1
        residual = abs(g / period - n)  # How far from integer
        score += residual ** 2
    score /= len(gaps)
    if score < best_score:
        best_score = score
        best_period = period

print(f"Best-fit fundamental period: {best_period:.4f}")
print(f"Mean squared residual: {best_score:.6f}")
print()

# Check what this period IS
print(f"Comparison to known constants:")
print(f"  log₁₀(2π) = {math.log10(2*pi):.4f}")
print(f"  log₁₀(4π) = {math.log10(4*pi):.4f}")
print(f"  log₁₀(e)  = {math.log10(math.e):.4f}")
print(f"  log₁₀(φ)  = {math.log10(phi):.4f}")
print(f"  π/4        = {pi/4:.4f}")
print(f"  1/φ        = {1/phi:.4f}")
print(f"  Best fit   = {best_period:.4f}")
print()

# How do our gaps fit as multiples of the best period?
print(f"Gaps as multiples of {best_period:.4f}:")
for g in sorted(gaps):
    n = round(g / best_period)
    predicted = n * best_period
    err = abs(g - predicted) / predicted * 100
    symbol = "✓" if err < 8 else ("~" if err < 15 else "✗")
    print(f"  {g:.3f} = {g/best_period:.2f} × {best_period:.3f} ≈ {n} × {best_period:.3f} ({err:.1f}%) {symbol}")

print()
print("=" * 80)
print("DYLAN'S φ INSIGHT")
print("=" * 80)
print()
print("φ = 1.618... is the MOST IRRATIONAL number.")
print("Its continued fraction [1;1,1,1,...] converges most slowly to")
print("any rational approximation. In music: it's maximally dissonant.")
print()
print("If the action spectrum has preferred positions at simple ratios")
print("(2:1, 3:2, 4:3...), then φ is the position LEAST resonant with")
print("any of them. Systems at φ-positions on the action axis would be:")
print("  - Maximally decoupled from harmonic lock-in")
print("  - Free to adapt (not trapped in resonance)")
print("  - Self-sustaining without external harmonic support")
print()
print("On the ARA scale, φ = 1.618 IS the 'sustained engine' point —")
print("the most efficient, most persistent systems live here.")
print()
print("CONNECTION: Maybe φ isn't ON the octave ladder. Maybe φ is the")
print("GEOMETRY of the ladder itself — the ratio between how the ladder")
print("is built. Not a note, but the spacing principle.")
print()

# Test: is φ or 1/φ a factor in the gaps?
print("Are gaps expressible as simple combinations involving φ?")
print()
for g in sorted(gaps):
    # Try g = a + b×log₁₀(φ) for small integers a, b
    log_phi = math.log10(phi)
    best_combo = None
    best_err_combo = 999
    for a in range(-2, 20):
        for b in range(-5, 6):
            if a == 0 and b == 0:
                continue
            candidate = a * 1.0 + b * log_phi  # integer decades + phi multiples
            if candidate > 0:
                err = abs(g - candidate) / g
                if err < best_err_combo:
                    best_err_combo = err
                    best_combo = f"{a} + {b}×log(φ)"
    
    # Also try: g = n × log₁₀(φ^m) for various m
    for m in range(1, 10):
        target = m * log_phi
        n = round(g / target)
        if n > 0:
            pred = n * target
            err = abs(g - pred) / g
            if err < best_err_combo:
                best_err_combo = err
                best_combo = f"{n} × log₁₀(φ^{m}) = {n}×{target:.4f}"
    
    print(f"  {g:.3f}  best: {best_combo} ({best_err_combo*100:.1f}%)")

print()
print("=" * 80)
print("THE 'SMALLEST AND LARGEST CIRCLE' IDEA")
print("=" * 80)
print()
print("Dylan's idea: ℏ is the smallest complete circle (minimum action).")
print("Is there a largest? And does the ratio define the octave?")
print()
print(f"Smallest action observed: ℏ = 1.055e-34 J·s (hydrogen ground state)")
print(f"Largest action mapped: Earth diurnal = 4.13e+26 J·s")
print(f"")
print(f"Total range: 10^(-34) to 10^(+26.6) = 10^60.6 orders of magnitude")
print(f"")
print(f"If this 60.6-order range is ONE meta-octave:")
print(f"  Number of 4π octaves that fit: {60.6 / math.log10(4*pi):.1f}")
print(f"  Number of 2π octaves: {60.6 / math.log10(2*pi):.1f}")
print(f"  Number of decade octaves: {60.6 / 1.0:.1f}")
print(f"  Number of φ² steps: {60.6 / math.log10(phi**2):.1f}")
print(f"  Number of φ steps: {60.6 / math.log10(phi):.1f}")
print()

# What if the "octave" is defined by ARA = 1:1?
# ARA = 1 means accumulation = release (symmetric)
# The systems at ARA ≈ 1 are: hydrogen, CPU, engine (all at ARA = 1.000)
# These span actions from 10^-34 to 10^1.5 — that's 35.5 orders!
print("ARA = 1.000 systems (symmetric cycles):")
print("  Hydrogen: Action/π = 10^-34.0")
print("  CPU:      Action/π = 10^-17.6") 
print("  Engine:   Action/π = 10^+1.5")
print(f"  Span of ARA=1 systems: 35.5 orders")
print(f"  That's {35.5/math.log10(2*pi):.1f} × log₁₀(2π)")
print(f"  Or {35.5/math.log10(phi):.1f} × log₁₀(φ)")
print()
print("Hmm. 35.5 / log₁₀(2π) = 44.5. Not obviously meaningful.")
print()

# What about the MIDPOINT?
midpoint = (-34 + 26.6) / 2
print(f"Midpoint of action spectrum: log₁₀ = {midpoint:.1f}")
print(f"Systems near midpoint: Heart (log -0.46), Engine (log 1.5)")
print(f"The HUMAN SCALE sits at the midpoint.")
print()

# THE REAL INSIGHT: maybe it's not about log spacing.
# Maybe it's about the SHAPE of the action spectrum itself.
print("=" * 80)
print("REFRAME: THE SHAPE OF THE ACTION SPECTRUM")
print("=" * 80)
print()
print("What if we're looking for the wrong thing?")
print()
print("The 4π spacing was sensitive to how we cut systems into subsystems.")
print("But the OVERALL structure — 5 clusters, gaps between them,")
print("midpoint at human scale — that's robust.")
print()
print("The 5 clusters and their midpoints (log₁₀ Action/π):")
print("  Quantum:   -34 to -10   (midpoint -22)")
print("  Micro:     -18 to -13   (midpoint -15.5)")
print("  Human:     -4 to +5     (midpoint +0.5)")
print("  Mesoscale: +11 to +15   (midpoint +13)")
print("  Macro:     +21 to +40   (midpoint +30.5)")
print()

cluster_midpoints = [-22, -15.5, 0.5, 13, 30.5]
print("Gaps between cluster midpoints:")
for i in range(len(cluster_midpoints)-1):
    gap = cluster_midpoints[i+1] - cluster_midpoints[i]
    print(f"  {cluster_midpoints[i]:+.1f} → {cluster_midpoints[i+1]:+.1f}:  gap = {gap:.1f}")

print()
between_gaps = [cluster_midpoints[i+1] - cluster_midpoints[i] for i in range(len(cluster_midpoints)-1)]
print(f"Between-cluster gaps: {between_gaps}")
print(f"Mean: {sum(between_gaps)/len(between_gaps):.1f}")
print(f"  6.5, 16.0, 12.5, 17.5")
print()
print("These are NOT equal. The spectrum is not periodic at the cluster level.")
print("But: is there structure in the asymmetry?")
print()

# Ratios between consecutive cluster gaps
for i in range(len(between_gaps)-1):
    ratio = between_gaps[i+1] / between_gaps[i]
    print(f"  Gap {i+1}→{i+2} / Gap {i}→{i+1} = {between_gaps[i+1]:.1f}/{between_gaps[i]:.1f} = {ratio:.3f}")

print()
print("Ratio 16/6.5 = 2.46 ≈ φ+1 = φ² = 2.618? No, 2.46.")
print(f"Actually: φ² = {phi**2:.3f}, 5/2 = 2.5, e = {math.e:.3f}")
print()
print("The cluster gaps go: 6.5, 16, 12.5, 17.5")
print("The OUTER gaps (Quantum→Micro, Meso→Macro) average: {:.1f}".format((6.5+17.5)/2))
print("The INNER gaps (Micro→Human, Human→Meso) average: {:.1f}".format((16+12.5)/2))
print()
print("The spectrum might have an HOURGLASS shape:")
print("tight at the extremes (quantum and macro), wide in the middle (human).")
print("That's... interesting. The human scale has the most ACTION SPACE")
print("around it. The most room to maneuver.")

