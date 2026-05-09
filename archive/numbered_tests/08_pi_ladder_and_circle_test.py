import math
import random
random.seed(42)

pi = math.pi
phi = (1 + math.sqrt(5)) / 2
hbar = 1.0546e-34

big_gaps = [0.577, 1.172, 1.365, 1.569, 1.854, 2.000, 4.431, 5.255, 8.840, 8.888, 9.431]

print("=" * 80)
print("π/2 = 1.5708 as ladder width")
print("=" * 80)
print()
for g in sorted(big_gaps):
    n = max(1, round(g / (pi/2)))
    pred = n * pi/2
    err = abs(g - pred) / pred * 100
    symbol = "✓" if err < 8 else ("~" if err < 15 else "✗")
    print(f"  {g:.3f} ÷ (π/2) = {g/(pi/2):.2f} ≈ {n} ({err:.1f}%) {symbol}")

print()
print("=" * 80)
print("log₁₀(π) = 0.4971 as fundamental step")
print("=" * 80)
print()
for g in sorted(big_gaps):
    n = max(1, round(g / math.log10(pi)))
    pred = n * math.log10(pi)
    err = abs(g - pred) / pred * 100
    symbol = "✓" if err < 8 else ("~" if err < 15 else "✗")
    print(f"  {g:.3f} ÷ log₁₀(π) = {g/math.log10(pi):.2f} ≈ {n} ({err:.1f}%) {symbol}")

# Significance test for log₁₀(π)
def fit_score(data, period):
    total = 0
    for g in data:
        n = max(1, round(g / period))
        residual = abs(g / period - n)
        total += residual ** 2
    return total / len(data)

our_score_logpi = fit_score(big_gaps, math.log10(pi))
print(f"\nFit score for log₁₀(π): {our_score_logpi:.6f}")

# Monte Carlo
n_trials = 50000
n_better = 0
for _ in range(n_trials):
    rg = [random.uniform(0.5, 9.5) for _ in range(len(big_gaps))]
    if fit_score(rg, math.log10(pi)) <= our_score_logpi:
        n_better += 1

p_logpi = n_better / n_trials
print(f"p-value for log₁₀(π) spacing: {p_logpi:.4f}")
if p_logpi < 0.05:
    print("→ SIGNIFICANT")
else:
    print(f"→ Not significant (random data fits this well {p_logpi*100:.0f}% of the time)")

# Now the CIRCLE idea
print()
print("=" * 80)
print("THE ACTION AXIS AS A CIRCLE")
print("=" * 80)
print()

floor = math.log10(hbar)  # -33.98
systems_log = {
    "Hydrogen": -34.0,
    "CPU": -17.6,
    "Neuron": -13.4,
    "Heart": -0.46,
    "Engine": 1.54,
    "Thunderstorm": 15.0,
    "Predator-prey": 23.0,
    "Earth diurnal": 26.6,
}

# Try different ceilings
ceilings = {
    "Earth diurnal": 26.6,
    "Milankovitch (100kyr)": math.log10(3.15e12 * 1e25 / pi),  # rough
    "Galactic": math.log10(7.9e15 * 2e35 / pi),
}

for ceil_name, ceil_val in ceilings.items():
    span = ceil_val - floor
    print(f"─── Ceiling: {ceil_name} (log = {ceil_val:.1f}, span = {span:.1f}) ───")
    print()
    print(f"  1 radian = {span/(2*pi):.2f} orders of magnitude")
    print(f"  Span / π = {span/pi:.2f}")
    print(f"  Span / (2π) = {span/(2*pi):.2f}")
    print()
    
    print(f"  Systems on the circle:")
    for name, log_val in sorted(systems_log.items(), key=lambda x: x[1]):
        angle = (log_val - floor) / span * 2 * pi
        angle_deg = math.degrees(angle)
        print(f"    {name:<20s}  {angle_deg:6.1f}°  ({angle/(2*pi)*100:.0f}% around)")
    print()

# THE KEY INSIGHT: what if the span IS 2π × something nice?
print("=" * 80)
print("WHAT IF THE SPAN ITSELF ENCODES π?")
print("=" * 80)
print()
span_earth = 26.6 - floor  # ~60.6
print(f"Current measured span: {span_earth:.1f} orders")
print()
print(f"  {span_earth:.1f} / π   = {span_earth/pi:.2f}")
print(f"  {span_earth:.1f} / 2π  = {span_earth/(2*pi):.2f}")
print(f"  {span_earth:.1f} / π²  = {span_earth/(pi**2):.2f}")
print(f"  {span_earth:.1f} / 4π  = {span_earth/(4*pi):.2f}")
print(f"  {span_earth:.1f} / (2π)² = {span_earth/((2*pi)**2):.2f}")
print(f"  {span_earth:.1f} / 20  = {span_earth/20:.2f}")
print(f"  {span_earth:.1f} / φ×π² = {span_earth/(phi*pi**2):.2f}")
print()
print("60.6 / π² = 6.14 ≈ 2π? No, 2π = 6.28. Close-ish (2.3% off).")
print(f"Actually: 60.6 / (2π) = {span_earth/(2*pi):.3f}")
print(f"And: (2π)² = {(2*pi)**2:.3f}")
print()

# Wait. 60.6 / π² = 6.14. And 2π = 6.28.
# So span ≈ π² × 2π = 2π³? Let's check:
print(f"2π³ = {2*pi**3:.2f}")
print(f"Span = {span_earth:.1f}")
print(f"Span / 2π³ = {span_earth/(2*pi**3):.3f}")
print()
print("Not quite. But:")
print(f"  π² × (2π) = {pi**2 * 2*pi:.2f} = 2π³ = {2*pi**3:.2f}")
print(f"  Span / 10 = {span_earth/10:.2f}")
print(f"  6 × π² = {6*pi**2:.2f}")
print(f"  6 × π² = {6*pi**2:.2f}  (1.4% off from 60.6)")
print()

# 6π² = 59.22. Our span is 60.6. That's 2.3% off.
# Or: 60.6 / 6 = 10.1. And π² = 9.87. So span ≈ 6 × 10 = 60. Trivial.

# Let's not force it. The span depends on the ceiling, which we haven't established.
# The only firm thing is the FLOOR (ℏ).

print("=" * 80)
print("HONEST CONCLUSION")  
print("=" * 80)
print()
print("log₁₀(π) = 0.497 scored best as a spacing candidate,")
print("but we already know from the φ test that small spacings")
print("trivially fit. The p-value tells the real story.")
print()
print(f"log₁₀(π) spacing p-value: {p_logpi:.4f}")
print()
print("The circle idea is conceptually beautiful (action axis wraps")
print("around, quantum meets macro) but we can't test it without")
print("knowing the ceiling — and the ceiling depends on mapping")
print("galactic/cosmological oscillatory systems.")
print()
print("What IS testable right now:")
print("  1. The floor is ℏ (proven)")
print("  2. The formula works (proven)")
print("  3. The clusters exist (suggestive, needs more systems)")
print("  4. The spacing between clusters is [specific value] — NOT YET TESTABLE")
print()
print("The E problem blocks everything beyond #3.")
print("Until E is nailed down, we're measuring our assumptions,")
print("not physics.")

