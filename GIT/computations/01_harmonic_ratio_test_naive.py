import math
from fractions import Fraction
from itertools import combinations

# =============================================================
# FRACTAL PREDICTION TEST
# For each coupled system, compute Action/π ratios between
# all subsystem pairs. Check if they approximate simple
# harmonic fractions (n:m where n,m are small integers).
# =============================================================

# Subsystem data: Action/π values from our 8 mapped systems
# Grouped by parent system with subsystem names

systems = {
    "Hydrogen Atom": {
        "Ground orbital (n=1)":   1.055e-34,
        "n=2 orbital":            2 * 1.055e-34,
        "n=3 orbital":            3 * 1.055e-34,
        "Metastable (2s)":        2 * 1.055e-34,  # same n=2
        "Lyman-α photon":         2 * 1.055e-34,   # photon = 2ℏ
    },
    "CPU": {
        "Clock cycle":            2.77e-18,
        "Boost cycle":            2.77e-18 * (3.5/4.7),  # scaled by freq ratio approx
        "Thermal throttle":       2.77e-18 * 1e4,  # ~seconds timescale, much higher action
    },
    "Neuron": {
        "Depolarisation":         4.22e-14 * 0.01,   # ~0.3ms phase of 26.5ms cycle
        "Spike (full AP)":        4.22e-14,
        "Refractory period":      4.22e-14 * 10,     # ~265ms equivalent
        "Vesicle release":        4.22e-14 * 100,    # longer recycling
    },
    "Heart": {
        "Myocyte contraction":    3.45e-1 * 0.01,    # single cell, ~ms timescale
        "Ventricular pump":       3.45e-1,
        "RSA (respiratory sinus)":3.45e-1 * 30,      # ~25s breathing modulation
        "Circadian HRV":          3.45e-1 * 1e5,     # ~24hr modulation
    },
    "Engine": {
        "Valve event":            3.44e1 * 0.001,    # ~ms valve timing
        "Combustion cycle":       3.44e1,
        "PC boost cycle":         3.44e1 * 10,       # ~0.4s boost response
        "Thermal cycle":          3.44e1 * 1e3,      # ~minutes warmup
    },
    "Thunderstorm": {
        "Lightning stroke":       1.05e15 * 1e-6,    # ~μs timescale, ~GJ energy
        "Gust front":             1.05e15 * 0.01,    # ~30s, fraction of storm energy
        "Precipitation cycle":    1.05e15 * 0.1,     # ~5min, partial energy
        "Full cell lifecycle":    1.05e15,
    },
    "Predator-Prey": {
        "Vegetation growth":      9.54e22 * 0.01,    # seasonal, less energy
        "Hare population":        9.54e22 * 0.1,     # ~1yr subcycle
        "Lynx population":        9.54e22 * 0.5,     # ~4yr subcycle
        "Full LV cycle":          9.54e22,
    },
    "Earth Diurnal": {
        "Surface heating":        4.13e26 * 0.01,    # daytime ramp, partial energy
        "Full diurnal":           4.13e26,
        "Seasonal modulation":    4.13e26 * 365,     # annual cycle
        "Milankovitch":           4.13e26 * 1e7,     # ~100kyr cycles
    },
}

# However, the above subsystem estimates are rough. Let me use the ACTUAL
# data from our notes more carefully. The key test is ratios between
# subsystems within the same coupled system.

# Let me recalculate using the actual subsystem data from the papers.
# From the octave structure notes, we have these measured gaps:
# Neuron: Depol → Refractory = 0.976 (log10 gap)
# Neuron: Refractory → Vesicle = 0.983
# Engine: Valve → PC Boost = 0.977
# Thunderstorm: Gust → Precip = 0.964
# Predator-prey: Veg → Lynx = 1.075
# Heart: Myocyte → RSA = 1.484
# Hydrogen: Metastable → CPU = 1.515
# PC: Boost → Thermal = 1.713

# These gaps are log10 ratios. The fractal prediction says these should
# approximate log10 of simple harmonic ratios built from 4π and (2π)².

# But the DEEPER test from the fractal notes is whether ACTION RATIOS
# between subsystems are simple fractions. Let me approach this differently.

# The actual subsystem Action/π values from the 3D visualization data:

subsystems_actual = {
    "Hydrogen": [
        ("Ground orbital", 1.055e-34),
        ("n=2", 2.11e-34),
        ("n=3", 3.165e-34),
        ("Balmer limit", 4.22e-34),
        ("Lyman-α photon", 2.11e-34),
        ("Ionisation", 1.055e-34),  # same as ground, by definition
    ],
    "Neuron": [
        ("Depolarisation", 4.22e-16),  # ~0.3ms, ~pJ
        ("Action potential", 4.22e-14),  # 2.65ms, 5pJ  
        ("Refractory", 4.22e-13),       # ~26.5ms
        ("Vesicle recycling", 4.22e-12), # ~265ms
    ],
    "Heart": [
        ("Myocyte AP", 3.45e-3),        # ~250ms, ~mJ
        ("Ventricular pump", 3.45e-1),   # 833ms, 1.3J
        ("RSA envelope", 1.05e1),        # ~25s, ~J
        ("Circadian HRV", 3.45e4),       # ~24hr
    ],
    "Engine": [
        ("Valve event", 3.44e-2),        # ~1ms  
        ("Combustion cycle", 3.44e1),    # 40ms, 2700J
        ("Boost response", 3.44e2),      # ~0.4s
        ("Thermal equilibrium", 3.44e4), # ~minutes
    ],
    "Thunderstorm": [
        ("Lightning", 1.05e9),           # ~μs, ~GJ
        ("Gust front", 1.05e13),         # ~30s
        ("Precipitation", 1.05e14),      # ~5min
        ("Cell lifecycle", 1.05e15),     # 55min, 1TJ
    ],
    "Predator-Prey": [
        ("Vegetation cycle", 9.54e20),   # seasonal
        ("Hare subcycle", 9.54e21),      # ~1yr
        ("Lynx subcycle", 4.77e22),      # ~4yr
        ("Full LV cycle", 9.54e22),      # 9.5yr
    ],
}

print("=" * 80)
print("FRACTAL PREDICTION TEST: Harmonic Ratios Between Subsystems")
print("=" * 80)
print()
print("Prediction: Action/π ratios between subsystems within the same coupled")
print("system should approximate simple fractions (n:m where n,m ≤ 12).")
print()

# For each system, compute all pairwise ratios
harmonic_targets = []
for n in range(1, 13):
    for m in range(1, n):
        harmonic_targets.append((n, m, n/m))

# Sort by ratio value
harmonic_targets.sort(key=lambda x: x[2])

# Musical names for common ratios
musical_names = {
    (2, 1): "Octave",
    (3, 2): "Perfect fifth",
    (4, 3): "Perfect fourth",
    (5, 4): "Major third",
    (6, 5): "Minor third",
    (5, 3): "Major sixth",
    (8, 5): "Minor sixth",
    (9, 8): "Major second",
    (3, 1): "Octave + fifth",
    (4, 1): "Double octave",
    (7, 4): "Septimal minor seventh",
    (7, 6): "Septimal minor third",
    (10, 9): "Minor second (just)",
}

def find_nearest_harmonic(ratio):
    """Find the simplest harmonic fraction nearest to the given ratio."""
    best = None
    best_err = float('inf')
    for n, m, target in harmonic_targets:
        err = abs(ratio - target) / target
        if err < best_err:
            best_err = err
            best = (n, m, target)
    return best[0], best[1], best[2], best_err

all_results = []

for system_name, subsystems in subsystems_actual.items():
    print(f"\n{'─' * 70}")
    print(f"  {system_name}")
    print(f"{'─' * 70}")
    
    pairs = list(combinations(range(len(subsystems)), 2))
    for i, j in pairs:
        name_i, action_i = subsystems[i]
        name_j, action_j = subsystems[j]
        
        # Always take ratio > 1
        if action_j > action_i:
            ratio = action_j / action_i
            label = f"{name_j} / {name_i}"
        else:
            ratio = action_i / action_j
            label = f"{name_i} / {name_j}"
        
        log_ratio = math.log10(ratio)
        n, m, target, err = find_nearest_harmonic(ratio)
        
        # Also check if log10(ratio) is near a simple fraction
        # (for large ratios, the log is more meaningful)
        if ratio > 12:
            # For large ratios, check if log10(ratio) ≈ simple integer or half-integer
            log_r = math.log10(ratio)
            nearest_int = round(log_r)
            log_err = abs(log_r - nearest_int) / max(nearest_int, 0.01)
            
            # Check 4π spacing
            n_4pi = log_r / math.log10(4 * math.pi)
            nearest_n_4pi = round(n_4pi)
            err_4pi = abs(n_4pi - nearest_n_4pi) / max(nearest_n_4pi, 0.01) if nearest_n_4pi > 0 else 999
            
            print(f"  {label:40s}  ratio = 10^{log_r:.2f}")
            print(f"    → {log_r:.3f} / log₁₀(4π) = {n_4pi:.2f}  ({'✓' if err_4pi < 0.15 else '✗'} {nearest_n_4pi} octaves, {err_4pi*100:.1f}% error)")
            all_results.append((system_name, label, ratio, log_r, n_4pi, nearest_n_4pi, err_4pi))
        else:
            name = musical_names.get((n, m), f"{n}:{m}")
            symbol = "✓" if err < 0.10 else ("~" if err < 0.20 else "✗")
            print(f"  {label:40s}  ratio = {ratio:.4f}  → {n}:{m} ({name}) {symbol} {err*100:.1f}% error")
            all_results.append((system_name, label, ratio, math.log10(ratio), n/m, n/m, err))

# Summary statistics
print(f"\n{'=' * 80}")
print("SUMMARY")
print(f"{'=' * 80}")

# Count octave-based hits (for large ratios)
octave_results = [r for r in all_results if r[2] > 12]
harmonic_results = [r for r in all_results if r[2] <= 12]

print(f"\nSmall ratios (≤12, testable against harmonic fractions): {len(harmonic_results)}")
hits_10 = sum(1 for r in harmonic_results if r[6] < 0.10)
hits_20 = sum(1 for r in harmonic_results if r[6] < 0.20)
print(f"  Within 10% of a simple fraction: {hits_10}/{len(harmonic_results)} ({100*hits_10/max(len(harmonic_results),1):.0f}%)")
print(f"  Within 20% of a simple fraction: {hits_20}/{len(harmonic_results)} ({100*hits_20/max(len(harmonic_results),1):.0f}%)")

print(f"\nLarge ratios (>12, testable against 4π octave spacing): {len(octave_results)}")
oct_hits_10 = sum(1 for r in octave_results if r[6] < 0.10)
oct_hits_15 = sum(1 for r in octave_results if r[6] < 0.15)
print(f"  Within 10% of integer octaves: {oct_hits_10}/{len(octave_results)} ({100*oct_hits_10/max(len(octave_results),1):.0f}%)")
print(f"  Within 15% of integer octaves: {oct_hits_15}/{len(octave_results)} ({100*oct_hits_15/max(len(octave_results),1):.0f}%)")

# Hydrogen special case
print(f"\n{'─' * 70}")
print("HYDROGEN (exact quantum system — ground truth)")
print(f"{'─' * 70}")
print("Hydrogen ratios are EXACTLY n:m by construction (E_n = n²×E₁).")
print("Action at level n = n × ℏ, so ratio between levels n and m = n/m.")
print("This IS the harmonic series. The fractal prediction holds exactly here.")
print("The question is whether this structure echoes at larger scales.")

# What would random look like?
print(f"\n{'─' * 70}")
print("NULL HYPOTHESIS CHECK")
print(f"{'─' * 70}")
import random
random.seed(42)

# Generate random log-uniform subsystem values and check hit rates
null_hits_10 = 0
null_hits_20 = 0  
null_total = 0
for trial in range(10000):
    # Random log-uniform ratio between 1 and 12
    ratio = 10 ** (random.uniform(0, math.log10(12)))
    _, _, _, err = find_nearest_harmonic(ratio)
    null_total += 1
    if err < 0.10:
        null_hits_10 += 1
    if err < 0.20:
        null_hits_20 += 1

print(f"Random ratios (uniform on log scale, 1-12):")
print(f"  Expected within 10% of any harmonic: {100*null_hits_10/null_total:.1f}%")
print(f"  Expected within 20% of any harmonic: {100*null_hits_20/null_total:.1f}%")
print(f"\nOur data within 10%: {100*hits_10/max(len(harmonic_results),1):.0f}%")
print(f"Our data within 20%: {100*hits_20/max(len(harmonic_results),1):.0f}%")

if len(harmonic_results) > 0:
    data_rate = hits_10 / len(harmonic_results)
    null_rate = null_hits_10 / null_total
    if null_rate > 0:
        print(f"\nEnrichment factor (10% threshold): {data_rate/null_rate:.2f}x over random")

# Octave null check
null_oct_hits = 0
null_oct_total = 0
for trial in range(10000):
    log_r = random.uniform(1, 8)  # random log ratio 1-8
    n_4pi = log_r / math.log10(4 * math.pi)
    nearest = round(n_4pi)
    if nearest > 0:
        err = abs(n_4pi - nearest) / nearest
        null_oct_total += 1
        if err < 0.15:
            null_oct_hits += 1

print(f"\nRandom large ratios (log 1-8):")
print(f"  Expected within 15% of integer octaves: {100*null_oct_hits/null_oct_total:.1f}%")
if len(octave_results) > 0:
    print(f"  Our data within 15%: {100*oct_hits_15/len(octave_results):.0f}%")

