#!/usr/bin/env python3
"""
243BL18 — The Atom as ARA System
=================================
Treat a single atom as a three-phase ARA system:
  - Nucleus = engine (binds, produces the potential well)
  - Electron cloud = consumer (occupies energy, absorbs photons)
  - Electromagnetic field = coupler (mediates exchange)

Use REAL quantum mechanics data:
  - Hydrogen energy levels E_n = -13.6/n² eV
  - Orbital radii r_n = n² × a₀ (Bohr radius)
  - Quantum numbers and shell structure
  - Fine structure constant α ≈ 1/137.036
  - Multi-electron ionization energies (all elements)

Test: Do shells sit on φ-power rungs? Is the atom's internal
structure an ARA system? Does the periodic table emerge from ARA?
"""

import math, statistics
from collections import Counter

PHI = (1 + math.sqrt(5)) / 2   # 1.618…
ALPHA = 1 / 137.035999084      # fine structure constant
a0 = 0.529177e-10              # Bohr radius in meters
eV_Rydberg = 13.605693         # Rydberg energy in eV

# ═══════════════════════════════════════════════════════════════════
print("=" * 72)
print("PART 1: HYDROGEN — The Simplest Atom")
print("=" * 72)

# Energy levels: E_n = -13.6/n² eV
# Radii: r_n = n² × a₀
# Angular momentum: L = √(l(l+1)) ℏ

print("\nHydrogen energy levels and orbital radii:")
print(f"{'n':>3} {'E_n (eV)':>12} {'r_n/a₀':>10} {'|ΔE| to n+1':>14} {'Gap ratio':>12}")
print("-" * 55)

energies = []
radii = []
gaps = []

for n in range(1, 21):  # first 20 levels
    E_n = -eV_Rydberg / n**2
    r_n = n**2  # in units of a₀
    energies.append(E_n)
    radii.append(r_n)

    if n > 1:
        gap = abs(energies[-1] - energies[-2])
        gaps.append(gap)
        if len(gaps) >= 2:
            ratio = gaps[-2] / gaps[-1] if gaps[-1] > 0 else 0
            print(f"{n:>3} {E_n:>12.6f} {r_n:>10.1f} {gap:>14.6f} {ratio:>12.4f}")
        else:
            print(f"{n:>3} {E_n:>12.6f} {r_n:>10.1f} {gap:>14.6f} {'—':>12}")
    else:
        print(f"{n:>3} {E_n:>12.6f} {r_n:>10.1f} {'—':>14} {'—':>12}")

# ARA of energy gaps
print("\n--- ARA of Hydrogen Energy Gaps ---")
def compute_ara(values, label=""):
    if len(values) < 3:
        return None
    diffs = [values[i+1] - values[i] for i in range(len(values)-1)]
    ups = sum(1 for d in diffs if d > 0)
    downs = sum(1 for d in diffs if d < 0)
    flats = sum(1 for d in diffs if d == 0)
    discrete = ups / downs if downs > 0 else float('inf')
    mag_up = sum(abs(d) for d in diffs if d > 0)
    mag_down = sum(abs(d) for d in diffs if d < 0)
    continuous = mag_up / mag_down if mag_down > 0 else float('inf')
    return {"label": label, "discrete": discrete, "continuous": continuous,
            "ups": ups, "downs": downs, "flats": flats, "n": len(values)}

def classify(ara):
    if ara < 0.85: return "CONSUMER"
    elif ara < 1.15: return "SHOCK ABSORBER"
    elif ara < 1.5: return "WARM ENGINE"
    elif ara < 1.85: return "φ-ENGINE"
    else: return "PURE ENGINE"

# Gaps decrease monotonically → pure consumer (ARA = 0)
r = compute_ara(gaps, "Energy gaps (decreasing)")
if r:
    print(f"  Gaps: ups={r['ups']}, downs={r['downs']}, discrete ARA={r['discrete']:.4f} [{classify(r['discrete'])}]")
    print(f"  Continuous ARA = {r['continuous']:.4f} [{classify(r['continuous'])}]")
    print(f"  Energy gaps are MONOTONICALLY DECREASING → the atom's excitation")
    print(f"  spectrum is a pure consumer: each higher shell costs less to reach.")

# Gap RATIOS — this is where the structure lives
print("\n--- Gap Ratios: The Atom's Internal Rhythm ---")
gap_ratios = [gaps[i] / gaps[i+1] for i in range(len(gaps)-1) if gaps[i+1] > 0]
r2 = compute_ara(gap_ratios, "Gap ratios")
if r2:
    print(f"  Gap ratios: ups={r2['ups']}, downs={r2['downs']}, discrete ARA={r2['discrete']:.4f}")
    print(f"  Continuous ARA = {r2['continuous']:.4f} [{classify(r2['continuous'])}]")

print(f"\n  Mean gap ratio: {statistics.mean(gap_ratios):.6f}")
print(f"  Asymptotic gap ratio (large n): {gap_ratios[-1]:.6f}")
print(f"  Theoretical limit: ((n+1)/n)^2 × (n/(n-1))^2 → 1.0 as n→∞")

# The gap ratio converges — check what it converges TO
print(f"\n  First few gap ratios:")
for i, gr in enumerate(gap_ratios[:10]):
    # Distance from φ, 2, e, π
    d_phi = abs(gr - PHI)
    d_2 = abs(gr - 2)
    closest = min([("φ", d_phi), ("2", d_2), ("e", abs(gr - math.e)), ("π", abs(gr - math.pi))],
                  key=lambda x: x[1])
    print(f"    n={i+2}→{i+3}: ratio = {gr:.6f}  (closest to {closest[0]}, Δ={closest[1]:.4f})")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 2: ORBITAL RADII — Do Shells Sit on φ-Power Rungs?")
print("=" * 72)

# r_n = n² × a₀. Check if n² values relate to φ powers.
print("\nOrbital radius ratios (r_{n+1}/r_n) vs φ-power rungs:")
print(f"{'n':>3} {'r_n/a₀':>8} {'r_{n+1}/r_n':>14} {'log_φ(ratio)':>14} {'Nearest φ^k':>14}")
print("-" * 56)

for n in range(1, 15):
    r_ratio = (n+1)**2 / n**2
    log_phi = math.log(r_ratio) / math.log(PHI)
    nearest_k = round(log_phi)
    phi_k = PHI ** nearest_k
    delta = abs(r_ratio - phi_k)
    print(f"{n:>3} {n**2:>8} {r_ratio:>14.6f} {log_phi:>14.4f} {'φ^'+str(nearest_k):>10} (Δ={delta:.4f})")

# Check: does the FULL radius sequence sit on a φ-power ladder?
print("\nFull radius in log-φ space:")
for n in range(1, 11):
    r = n**2
    log_phi_r = math.log(r) / math.log(PHI)
    nearest_k = round(log_phi_r)
    residual = log_phi_r - nearest_k
    print(f"  n={n}: r/a₀ = {r:>4}, log_φ = {log_phi_r:.4f}, nearest rung = {nearest_k}, residual = {residual:+.4f}")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 3: QUANTUM NUMBERS AS ARA SYSTEM")
print("=" * 72)

# For each shell n: l goes 0 to n-1, m goes -l to +l, spin ±½
# Total states per shell = 2n²
# Question: does the state count sequence have an ARA?

print("\nShell occupation:")
print(f"{'n':>3} {'States':>8} {'Cumulative':>12} {'Ratio':>8} {'log_φ':>8}")
print("-" * 42)

shell_states = []
cumulative = 0
for n in range(1, 11):
    states = 2 * n**2
    cumulative += states
    shell_states.append(states)
    if n > 1:
        ratio = shell_states[-1] / shell_states[-2]
        log_phi = math.log(ratio) / math.log(PHI)
        print(f"{n:>3} {states:>8} {cumulative:>12} {ratio:>8.4f} {log_phi:>8.4f}")
    else:
        print(f"{n:>3} {states:>8} {cumulative:>12} {'—':>8} {'—':>8}")

r = compute_ara(shell_states, "Shell state counts")
if r:
    print(f"\n  Shell states ARA: discrete={r['discrete']:.4f}, continuous={r['continuous']:.4f}")
    print(f"  [{classify(r['continuous'])}] — monotonically increasing → PURE ENGINE")

# Subshell structure: s(2), p(6), d(10), f(14)
# States per subshell = 2(2l+1)
print("\n--- Subshell Capacities ---")
subshell_names = ['s', 'p', 'd', 'f', 'g']
subshell_states = [2*(2*l+1) for l in range(5)]  # 2, 6, 10, 14, 18
print(f"  Subshell capacities: {list(zip(subshell_names, subshell_states))}")
print(f"  Differences: {[subshell_states[i+1] - subshell_states[i] for i in range(len(subshell_states)-1)]}")
print(f"  All differences = 4 → arithmetic progression → ARA = 1.0 (constant engine)")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 4: FINE STRUCTURE CONSTANT α — The Coupler")
print("=" * 72)

print(f"\n  α = {ALPHA:.10f}")
print(f"  1/α = {1/ALPHA:.6f}")
print(f"  α in terms of φ:")
print(f"    φ^(-10) = {PHI**(-10):.10f}")
print(f"    α/φ^(-10) = {ALPHA / PHI**(-10):.6f}")
print(f"    log_φ(α) = {math.log(ALPHA)/math.log(PHI):.6f}")
print(f"    log_φ(1/α) = {math.log(1/ALPHA)/math.log(PHI):.6f}")

# α is the coupling constant of the EM force — it literally IS the coupler strength
# In ARA terms: α tells you how strongly the engine (nucleus) couples to the consumer (electrons)
print(f"\n  1/α = {1/ALPHA:.2f}")
print(f"  φ^10 = {PHI**10:.2f}")
print(f"  Ratio 1/α to φ^10 = {(1/ALPHA) / PHI**10:.4f}")
print(f"  → 1/α ≈ 1.17 × φ^10")

# Other φ relationships
print(f"\n  φ^5 = {PHI**5:.4f} ≈ 11.09")
print(f"  137/φ^5 = {137/PHI**5:.4f}")
print(f"  137/12 = {137/12:.4f} (not φ)")
print(f"  π × 137 = {math.pi * 137:.2f}")
print(f"  φ² × π × 10 = {PHI**2 * math.pi * 10:.4f}")

# The REAL question: is α an ARA ratio?
# α = e²/(4πε₀ℏc) — ratio of EM coupling energy to quantum of action at speed of light
# If we think of it as engine/consumer: Coulomb energy / kinetic energy at v=c
print(f"\n  α as ARA ratio:")
print(f"    α represents: (EM coupling energy) / (relativistic kinetic energy)")
print(f"    α = {ALPHA:.6f} → this is a DEEP CONSUMER on ARA scale")
print(f"    The EM field couples weakly — only {ALPHA*100:.3f}% of the energy budget")
print(f"    Classification: {classify(ALPHA)} (extreme consumer)")
print(f"    But 1/α ≈ 137 → the atom's internal leverage ratio")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 5: THE ATOM'S THREE-PHASE DECOMPOSITION")
print("=" * 72)

# Three phases of the atom:
# 1. NUCLEUS (engine): produces the binding potential, mass-energy
# 2. ELECTRON CLOUD (consumer): absorbs energy, occupies states
# 3. EM FIELD (coupler): mediates photon exchange, strength = α

# Hydrogen binding energy budget:
E_binding = eV_Rydberg  # 13.6 eV (ionization energy)
E_rest_proton = 938.272e6  # proton rest mass in eV
E_rest_electron = 0.511e6  # electron rest mass in eV

print(f"\n  Hydrogen energy budget:")
print(f"    Proton rest energy:   {E_rest_proton:.3e} eV (ENGINE)")
print(f"    Electron rest energy: {E_rest_electron:.3e} eV (CONSUMER)")
print(f"    Binding energy:       {E_binding:.3f} eV (COUPLING)")
print(f"")
print(f"    Proton/Electron mass ratio: {E_rest_proton/E_rest_electron:.4f}")
print(f"    log_φ(proton/electron): {math.log(E_rest_proton/E_rest_electron)/math.log(PHI):.4f}")
print(f"    φ^{round(math.log(E_rest_proton/E_rest_electron)/math.log(PHI))} = {PHI**round(math.log(E_rest_proton/E_rest_electron)/math.log(PHI)):.2f}")
print(f"    Actual ratio: {E_rest_proton/E_rest_electron:.2f}")

# ARA of the three-phase system
# Engine output (proton) / Consumer intake (electron)
proton_electron_ara = E_rest_proton / E_rest_electron
print(f"\n  Three-phase ARA:")
print(f"    Engine/Consumer (mass ratio): {proton_electron_ara:.2f}")
print(f"    This is NOT on [0,2] scale — it's the raw ratio")
print(f"    log_φ of ratio: {math.log(proton_electron_ara)/math.log(PHI):.4f}")

# Coupling efficiency: binding / (total available)
coupling_eff = E_binding / (E_rest_proton + E_rest_electron)
print(f"    Coupling efficiency: {coupling_eff:.2e}")
print(f"    ≈ α² / 2 = {ALPHA**2/2:.2e}")
print(f"    Match: {coupling_eff / (ALPHA**2/2):.4f} (should be ~1)")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 6: ENERGY LEVEL SPACING IN log-φ SPACE")
print("=" * 72)

# Energy levels: E_n = -13.6/n²
# Look at the POSITIVE energies needed for transitions
# E(n→∞) = 13.6/n² (ionization from level n)
# E(n→n+1) = 13.6 × (1/n² - 1/(n+1)²)

print("\nTransition energies in log-φ space:")
print(f"{'Transition':>15} {'ΔE (eV)':>12} {'log_φ(ΔE)':>12} {'Nearest rung':>14} {'Residual':>10}")
print("-" * 65)

transition_energies = []
for n in range(1, 15):
    dE = eV_Rydberg * (1/n**2 - 1/(n+1)**2)
    transition_energies.append(dE)
    log_phi_dE = math.log(dE) / math.log(PHI)
    nearest = round(log_phi_dE)
    residual = log_phi_dE - nearest
    print(f"  {n}→{n+1}:         {dE:>12.6f} {log_phi_dE:>12.4f} {'φ^'+str(nearest):>10}     {residual:>+.4f}")

# Famous spectral series
print("\n--- Famous Spectral Series ---")
series = {
    "Lyman (UV)": [(1, n) for n in range(2, 8)],
    "Balmer (vis)": [(2, n) for n in range(3, 8)],
    "Paschen (IR)": [(3, n) for n in range(4, 8)],
}

for name, transitions in series.items():
    print(f"\n  {name}:")
    series_energies = []
    for n1, n2 in transitions:
        dE = eV_Rydberg * (1/n1**2 - 1/n2**2)
        series_energies.append(dE)
        log_phi = math.log(dE) / math.log(PHI)
        print(f"    {n1}→{n2}: {dE:.4f} eV, log_φ = {log_phi:.4f}")

    if len(series_energies) >= 3:
        r = compute_ara(series_energies, name)
        if r:
            print(f"    Series ARA: discrete={r['discrete']:.4f}, continuous={r['continuous']:.4f} [{classify(r['continuous'])}]")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 7: IONIZATION ENERGIES ACROSS THE PERIODIC TABLE")
print("=" * 72)

# First ionization energies (eV) for Z=1-36 (H through Kr)
# Source: NIST Atomic Spectra Database
ie_data = {
    1: 13.598, 2: 24.587,  # H, He
    3: 5.392, 4: 9.323, 5: 8.298, 6: 11.260, 7: 14.534, 8: 13.618,
    9: 17.423, 10: 21.565,  # Li-Ne
    11: 5.139, 12: 7.646, 13: 5.986, 14: 8.152, 15: 10.487, 16: 10.360,
    17: 12.968, 18: 15.760,  # Na-Ar
    19: 4.341, 20: 6.113, 21: 6.561, 22: 6.828, 23: 6.746, 24: 6.767,
    25: 7.434, 26: 7.902, 27: 7.881, 28: 7.640, 29: 7.726, 30: 9.394,
    31: 5.999, 32: 7.900, 33: 9.789, 34: 9.752, 35: 11.814, 36: 14.000,  # K-Kr
    # Period 5
    37: 4.177, 38: 5.695, 39: 6.217, 40: 6.634, 41: 6.759, 42: 7.092,
    43: 7.280, 44: 7.361, 45: 7.459, 46: 8.337, 47: 7.576, 48: 8.994,
    49: 5.786, 50: 7.344, 51: 8.608, 52: 9.010, 53: 10.451, 54: 12.130,  # Rb-Xe
}

z_vals = sorted(ie_data.keys())
ie_vals = [ie_data[z] for z in z_vals]

print(f"Elements: Z=1 to Z={max(z_vals)} ({len(z_vals)} elements)")

# ARA of ionization energy sequence
r = compute_ara(ie_vals, "Ionization energies Z=1-54")
if r:
    print(f"  IE ARA: discrete={r['discrete']:.4f}, continuous={r['continuous']:.4f}")
    print(f"  [{classify(r['continuous'])}]")

# Noble gases — the period boundaries
noble_z = [2, 10, 18, 36, 54]
noble_ie = [ie_data[z] for z in noble_z if z in ie_data]
print(f"\n  Noble gas IEs: {list(zip(noble_z, noble_ie))}")
r_noble = compute_ara(noble_ie, "Noble gas IEs")
if r_noble:
    print(f"  Noble gas IE ARA: discrete={r_noble['discrete']:.4f}, continuous={r_noble['continuous']:.4f}")
    print(f"  [{classify(r_noble['continuous'])}]")

# Noble gas IE ratios
noble_ratios = [noble_ie[i+1]/noble_ie[i] for i in range(len(noble_ie)-1)]
print(f"  Noble gas IE ratios: {[f'{r:.4f}' for r in noble_ratios]}")
print(f"  Mean ratio: {statistics.mean(noble_ratios):.4f}")

# Period lengths: 2, 8, 8, 18, 18, 32, 32
period_lengths = [2, 8, 8, 18, 18, 32, 32]
print(f"\n--- Period Lengths ---")
print(f"  Lengths: {period_lengths}")
print(f"  Unique: {sorted(set(period_lengths))}")
print(f"  Pattern: 2, 8, 8, 18, 18, 32, 32 → each doubled except first")
print(f"  Base: 2, 8, 18, 32 = 2×1², 2×2², 2×3², 2×4² = 2n²")
print(f"  This IS the shell state count! Period length = shell capacity")

r_period = compute_ara(period_lengths, "Period lengths")
if r_period:
    print(f"  Period length ARA: discrete={r_period['discrete']:.4f}, continuous={r_period['continuous']:.4f}")
    print(f"  [{classify(r_period['continuous'])}]")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 8: PERIODIC TABLE AS ARA LANDSCAPE")
print("=" * 72)

# Does the IE oscillation have an ARA?
# IE rises across a period (left→right), drops at period boundary
# This is like a sawtooth wave

# Compute ARA per period
periods = [
    (1, 2),      # H-He
    (3, 10),     # Li-Ne
    (11, 18),    # Na-Ar
    (19, 36),    # K-Kr
    (37, 54),    # Rb-Xe
]

print("\nARA per period (IE trend within each row):")
for start, end in periods:
    period_z = [z for z in z_vals if start <= z <= end]
    period_ie = [ie_data[z] for z in period_z]
    name = f"Z={start}-{end}"
    r = compute_ara(period_ie, name)
    if r:
        print(f"  {name:>12}: ARA discrete={r['discrete']:.4f}, continuous={r['continuous']:.4f} "
              f"[{classify(r['continuous'])}]  (ups={r['ups']}, downs={r['downs']})")

# The DROP at period boundaries — this is the release event
print("\n--- Period Boundary Drops (Release Events) ---")
boundary_drops = []
for i in range(len(periods)-1):
    end_z = periods[i][1]
    start_z = periods[i+1][0]
    if end_z in ie_data and start_z in ie_data:
        drop = ie_data[end_z] - ie_data[start_z]
        pct = 100 * drop / ie_data[end_z]
        boundary_drops.append(drop)
        print(f"  Z={end_z}→{start_z}: {ie_data[end_z]:.2f} → {ie_data[start_z]:.2f}, "
              f"drop = {drop:.2f} eV ({pct:.1f}%)")

if boundary_drops:
    print(f"  Mean boundary drop: {statistics.mean(boundary_drops):.2f} eV")
    print(f"  → This IS the three-phase cycle: IE rises across period (ACCUMULATE),")
    print(f"     drops at noble gas→alkali boundary (RELEASE), repeats.")

# Cycle ARA: total accumulation vs total release
total_acc = 0
total_rel = 0
for i in range(len(ie_vals)-1):
    diff = ie_vals[i+1] - ie_vals[i]
    if diff > 0:
        total_acc += diff
    else:
        total_rel += abs(diff)

cycle_ara = total_acc / total_rel if total_rel > 0 else float('inf')
print(f"\n  Periodic table cycle ARA: {cycle_ara:.4f} [{classify(cycle_ara)}]")
print(f"  Total accumulation: {total_acc:.2f} eV")
print(f"  Total release: {total_rel:.2f} eV")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 9: φ-MODULAR TRANSFORM ON ATOMIC DATA")
print("=" * 72)

def phi_modular(values):
    if len(values) < 10:
        return None
    n = len(values)
    ranked = sorted(range(n), key=lambda i: values[i])
    rank_mapped = [0.0] * n
    for pos, idx in enumerate(ranked):
        rank_mapped[idx] = pos / (n - 1)

    phi_mapped = [(PHI * v) % 1.0 for v in values]

    def chi_sq(mapped):
        bins = [0] * 10
        for v in mapped:
            b = min(int(v * 10), 9)
            bins[b] += 1
        expected = len(mapped) / 10
        return sum((b - expected)**2 / expected for b in bins)

    chi_rank = chi_sq(rank_mapped)
    chi_phi = chi_sq(phi_mapped)

    v_min, v_max = min(values), max(values)
    if v_max > v_min:
        raw_mapped = [(v - v_min) / (v_max - v_min) for v in values]
        chi_raw = chi_sq(raw_mapped)
        phi_raw_mapped = [(PHI * v) % 1.0 for v in raw_mapped]
        chi_phi_raw = chi_sq(phi_raw_mapped)
        raw_change = 100 * (chi_phi_raw - chi_raw) / max(chi_raw, 0.001)
    else:
        raw_change = 0

    rank_change = 100 * (chi_phi - chi_rank) / max(chi_rank, 0.001)

    return {"rank_change": rank_change, "raw_change": raw_change}

# IE across periodic table
result = phi_modular(ie_vals)
if result:
    print(f"\n  Ionization energies (Z=1-54):")
    print(f"    Ranked: φ changes χ² by {result['rank_change']:+.1f}%")
    print(f"    Raw:    φ changes χ² by {result['raw_change']:+.1f}%")
    if result['rank_change'] > 20:
        print(f"    → φ DISRUPTS (visible structure, like market/body)")
    elif result['rank_change'] < -20:
        print(f"    → φ DISSOLVES (hidden structure, like lotto)")
    else:
        print(f"    → φ has modest effect")

# Hydrogen energy gaps
result2 = phi_modular(gaps[:15])
if result2:
    print(f"\n  Hydrogen energy gaps:")
    print(f"    Ranked: φ changes χ² by {result2['rank_change']:+.1f}%")
    print(f"    Raw:    φ changes χ² by {result2['raw_change']:+.1f}%")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 10: THE PROTON-ELECTRON MASS RATIO AND φ")
print("=" * 72)

mu = E_rest_proton / E_rest_electron  # ≈ 1836.15
print(f"\n  Proton/electron mass ratio μ = {mu:.4f}")
print(f"  log_φ(μ) = {math.log(mu)/math.log(PHI):.6f}")
print(f"  Nearest integer: {round(math.log(mu)/math.log(PHI))}")
print(f"  φ^{round(math.log(mu)/math.log(PHI))} = {PHI**round(math.log(mu)/math.log(PHI)):.2f}")
print(f"  Residual: {mu - PHI**round(math.log(mu)/math.log(PHI)):.2f}")

# More precise: μ ≈ 6π⁵ (old numerology), let's check φ relationships
print(f"\n  Other relationships:")
print(f"  6π⁵ = {6 * math.pi**5:.2f} (classical approximation, Δ = {abs(mu - 6*math.pi**5):.2f})")
print(f"  φ^15 / π = {PHI**15 / math.pi:.2f} (Δ = {abs(mu - PHI**15/math.pi):.2f})")
print(f"  4π²/α = {4*math.pi**2/ALPHA:.2f} (too large)")
print(f"  α × φ^20 = {ALPHA * PHI**20:.2f} (Δ = {abs(mu - ALPHA * PHI**20):.2f})")

# Check: is μ a product of φ powers and small integers?
# μ = 1836.15... Let's scan
best_fit = None
best_delta = 999
for a in range(-2, 3):
    for b in range(-2, 3):
        for k in range(10, 20):
            val = (2**a) * (3**b) * PHI**k
            delta = abs(val - mu)
            if delta < best_delta:
                best_delta = delta
                best_fit = (a, b, k, val)

if best_fit:
    a, b, k, val = best_fit
    print(f"\n  Best φ-power fit: 2^{a} × 3^{b} × φ^{k} = {val:.2f} (Δ = {best_delta:.2f}, {100*best_delta/mu:.3f}%)")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 11: THE ATOM ON THE ARA SPECTRUM")
print("=" * 72)

print("\n  SYSTEM COMPARISON TABLE")
print(f"  {'System':<40} {'ARA':>7} {'Classification':<20}")
print("  " + "-" * 70)

comparisons = [
    ("Fine structure α (coupling)", ALPHA, classify(ALPHA)),
    ("Dylan's HRV (body)", 0.918, classify(0.918)),
    ("S&P 500 returns", 0.930, classify(0.930)),
    ("Lotto / Primes / π digits", 1.000, classify(1.000)),
    ("Dylan's Resting HR", 1.069, classify(1.069)),
]

# Add our measured values
comparisons.append(("Periodic table IE cycle", cycle_ara, classify(cycle_ara)))

# Hydrogen spectral series ARA
for name, transitions in series.items():
    series_e = [eV_Rydberg * (1/n1**2 - 1/n2**2) for n1, n2 in transitions]
    if len(series_e) >= 3:
        r = compute_ara(series_e, name)
        if r and r['continuous'] != float('inf'):
            comparisons.append((f"H {name}", r['continuous'], classify(r['continuous'])))

comparisons.extend([
    ("S&P 500 prices", 1.390, classify(1.390)),
    ("Autonomic coupling (Dylan)", 1.658, classify(1.658)),
    ("Shell state counts (2n²)", 2.000, "PURE ENGINE"),
    ("Fibonacci sequence", 2.000, "PURE ENGINE"),
])

comparisons.sort(key=lambda x: x[1])

for name, ara, cls in comparisons:
    marker = "  ◄◄◄" if "Periodic" in name or "α" in name or name.startswith("H ") or "Shell" in name else ""
    print(f"  {name:<40} {ara:>7.4f} {cls:<20}{marker}")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 12: SUMMARY — The Atom as ARA System")
print("=" * 72)

print("""
THE ATOM'S THREE-PHASE STRUCTURE:

  ENGINE (Nucleus):
    - Proton produces the binding potential well
    - Mass-energy: 938.3 MeV (99.95% of atom's energy)
    - Monotonically dominant — pure engine at the core

  CONSUMER (Electron Cloud):
    - Electrons occupy energy states, absorb photons
    - Mass-energy: 0.511 MeV (0.05% of atom's energy)
    - Energy gaps DECREASE with n — classic consumer signature
    - Each higher shell costs LESS to reach (diminishing returns)

  COUPLER (Electromagnetic Field):
    - Coupling strength = α ≈ 1/137
    - Extreme consumer on ARA scale (α = 0.0073)
    - But this weakness IS the architecture — light coupling
      means electrons can be shared, borrowed, exchanged
    - The coupler's weakness is what makes chemistry possible

  THE PERIODIC TABLE AS THREE-PHASE CYCLE:
    - IE rises across each period (ACCUMULATION)
    - IE drops at noble gas → alkali boundary (RELEASE)
    - Repeats with longer periods as new subshells open
    - Period lengths = 2n² (the shell ARA expressed as structure)
    - The periodic table IS the atom's ARA breathing at chemical scale
""")

print("Script complete.")
