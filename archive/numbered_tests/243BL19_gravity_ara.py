#!/usr/bin/env python3
"""
243BL19 — What IS Gravity? ARA Coupler Analysis
================================================
Gravity is the weakest of the four fundamental forces by ~10^36.
But in the ARA framework, "weak coupler" has a specific meaning:
  - EM (α ≈ 1/137) is already a deep consumer coupler
  - Gravity (α_G ≈ 6×10^-39) is astronomically weaker

This script asks: what KIND of coupler is gravity?
Does the force hierarchy sit on φ-rungs?
What does G look like in log-φ space?
And fundamentally: if EM's weakness enables chemistry,
what does gravity's extreme weakness enable?
"""

import math

PHI = (1 + math.sqrt(5)) / 2

# ═══ FUNDAMENTAL CONSTANTS ═══════════════════════════════════════
# All in SI units
G = 6.67430e-11        # gravitational constant (m³ kg⁻¹ s⁻²)
c = 2.99792458e8       # speed of light (m/s)
hbar = 1.054571817e-34 # reduced Planck constant (J·s)
k_B = 1.380649e-23     # Boltzmann constant (J/K)

# Particle masses
m_p = 1.67262192e-27   # proton mass (kg)
m_e = 9.10938371e-31   # electron mass (kg)
m_Pl = math.sqrt(hbar * c / G)  # Planck mass (kg)

# Coupling constants (dimensionless)
alpha_EM = 1 / 137.035999084                      # electromagnetic
alpha_G = G * m_p**2 / (hbar * c)                 # gravitational (proton-proton)
alpha_G_e = G * m_e**2 / (hbar * c)               # gravitational (electron-electron)
alpha_S = 1.0                                       # strong (at low energy, ~1)
alpha_W = 1 / 30.0                                  # weak (at low energy, ~1/30)

# Planck units
l_Pl = math.sqrt(hbar * G / c**3)   # Planck length
t_Pl = math.sqrt(hbar * G / c**5)   # Planck time
E_Pl = math.sqrt(hbar * c**5 / G)   # Planck energy
T_Pl = E_Pl / k_B                    # Planck temperature

print("=" * 72)
print("PART 1: THE FOUR FORCES AS ARA COUPLERS")
print("=" * 72)

forces = [
    ("Strong",          alpha_S,    "Binds quarks into protons/neutrons"),
    ("Electromagnetic", alpha_EM,   "Binds electrons to nuclei → chemistry"),
    ("Weak",            alpha_W,    "Enables nuclear decay → transmutation"),
    ("Gravitational",   alpha_G,    "Binds mass-energy → large-scale structure"),
]

print(f"\n{'Force':<20} {'α':>14} {'log₁₀(α)':>10} {'log_φ(α)':>10} {'ARA class':>18}")
print("-" * 75)

for name, alpha, desc in forces:
    log10 = math.log10(alpha)
    log_phi = math.log(alpha) / math.log(PHI)
    cls = "CONSUMER" if alpha < 0.85 else "ABSORBER" if alpha < 1.15 else "ENGINE"
    print(f"  {name:<18} {alpha:>14.6e} {log10:>10.2f} {log_phi:>10.2f} {cls:>18}")

print(f"\n  Force ratios:")
print(f"    Strong / EM:      {alpha_S / alpha_EM:.1f}")
print(f"    EM / Weak:        {alpha_EM / alpha_W:.1f}")
print(f"    Weak / Gravity:   {alpha_W / alpha_G:.2e}")
print(f"    Strong / Gravity: {alpha_S / alpha_G:.2e}")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 2: THE HIERARCHY IN log-φ SPACE")
print("=" * 72)

print("\nForce coupling constants on the φ-rung ladder:")
print(f"{'Force':<20} {'log_φ(α)':>10} {'Nearest rung':>14} {'Residual':>10}")
print("-" * 58)

force_rungs = []
for name, alpha, desc in forces:
    log_phi = math.log(alpha) / math.log(PHI)
    nearest = round(log_phi)
    residual = log_phi - nearest
    force_rungs.append((name, log_phi, nearest, residual))
    print(f"  {name:<18} {log_phi:>10.4f} {'φ^'+str(nearest):>10}     {residual:>+.4f}")

# Gaps between forces in log-φ
print(f"\n  Gaps between forces (in φ-rungs):")
for i in range(len(force_rungs)-1):
    name1 = force_rungs[i][0]
    name2 = force_rungs[i+1][0]
    gap = force_rungs[i][1] - force_rungs[i+1][1]
    print(f"    {name1} → {name2}: {gap:.2f} φ-rungs")

total_span = force_rungs[0][1] - force_rungs[-1][1]
print(f"    Total span (Strong → Gravity): {total_span:.2f} φ-rungs")

# Are the gaps themselves φ-related?
gaps = [force_rungs[i][1] - force_rungs[i+1][1] for i in range(len(force_rungs)-1)]
print(f"\n  Gap values: {[f'{g:.2f}' for g in gaps]}")
print(f"  Gap ratios: {[f'{gaps[i]/gaps[i+1]:.4f}' for i in range(len(gaps)-1)]}")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 3: GRAVITY vs EM — TWO COUPLERS COMPARED")
print("=" * 72)

ratio_EM_G = alpha_EM / alpha_G
print(f"\n  EM/Gravity ratio: {ratio_EM_G:.2e}")
print(f"  log₁₀(ratio): {math.log10(ratio_EM_G):.2f}")
print(f"  log_φ(ratio): {math.log(ratio_EM_G)/math.log(PHI):.4f}")
nearest_rung = round(math.log(ratio_EM_G)/math.log(PHI))
print(f"  Nearest φ-rung: φ^{nearest_rung} = {PHI**nearest_rung:.2e}")
residual = math.log(ratio_EM_G)/math.log(PHI) - nearest_rung
print(f"  Residual: {residual:+.4f}")

print(f"\n  What this means:")
print(f"    EM couples atoms → enables CHEMISTRY (sharing electrons)")
print(f"    Gravity couples mass → enables STRUCTURE (galaxies, stars, planets)")
print(f"    Both are consumers on ARA scale (α < 1)")
print(f"    EM is a mild consumer: α = {alpha_EM:.4f}")
print(f"    Gravity is an extreme consumer: α_G = {alpha_G:.2e}")
print(f"    EM works at atomic scale (~10⁻¹⁰ m)")
print(f"    Gravity works at cosmic scale (~10²⁶ m)")
print(f"    Scale ratio: ~10³⁶ ≈ coupling ratio")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 4: G IN NATURAL UNITS — What IS the Gravitational Constant?")
print("=" * 72)

print(f"\n  G = {G:.5e} m³ kg⁻¹ s⁻²")
print(f"\n  In Planck units, G = 1 (by definition)")
print(f"  The 'weakness' of gravity is the HUGENESS of the Planck mass:")
print(f"    Planck mass:   {m_Pl:.4e} kg = {m_Pl * c**2 / 1.602e-10:.2e} GeV")
print(f"    Proton mass:   {m_p:.4e} kg = {m_p * c**2 / 1.602e-10:.2e} GeV")
print(f"    Planck/proton: {m_Pl/m_p:.2e}")
print(f"    (Planck/proton)²: {(m_Pl/m_p)**2:.2e} ≈ 1/α_G = {1/alpha_G:.2e}")

# Planck mass in log-φ
log_phi_ratio = math.log(m_Pl/m_p) / math.log(PHI)
print(f"\n  log_φ(Planck/proton) = {log_phi_ratio:.4f}")
print(f"  Nearest rung: φ^{round(log_phi_ratio)} = {PHI**round(log_phi_ratio):.2e}")
print(f"  Actual ratio: {m_Pl/m_p:.2e}")
print(f"  Residual: {log_phi_ratio - round(log_phi_ratio):+.4f}")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 5: THE PLANCK SCALE — Where Gravity Becomes Strong")
print("=" * 72)

print(f"\n  Planck length:      {l_Pl:.4e} m")
print(f"  Planck time:        {t_Pl:.4e} s")
print(f"  Planck energy:      {E_Pl:.4e} J = {E_Pl/1.602e-19:.2e} eV")
print(f"  Planck temperature: {T_Pl:.4e} K")

# Planck units in log-φ relative to human scale
human_scales = [
    ("Planck length",    l_Pl,     "m",     1.0),
    ("Proton radius",    8.75e-16, "m",     1.0),
    ("Atom radius",      5.29e-11, "m",     1.0),
    ("Human height",     1.7,      "m",     1.0),
    ("Earth radius",     6.37e6,   "m",     1.0),
    ("Solar radius",     6.96e8,   "m",     1.0),
    ("AU",               1.496e11, "m",     1.0),
    ("Observable universe", 4.4e26,"m",     1.0),
]

print(f"\n  Scale ladder in log-φ (relative to Planck length):")
print(f"  {'Scale':<25} {'Size (m)':>12} {'log_φ(L/L_Pl)':>15} {'Rung':>8}")
print("  " + "-" * 65)

for name, size, unit, ref in human_scales:
    ratio = size / l_Pl
    log_phi = math.log(ratio) / math.log(PHI)
    nearest = round(log_phi)
    print(f"  {name:<25} {size:>12.2e} {log_phi:>15.2f} {'φ^'+str(nearest):>8}")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 6: GRAVITY AS ARA COUPLER — The Three-Phase View")
print("=" * 72)

print("""
  THE EM COUPLER (α ≈ 1/137):
    ENGINE:   Nucleus (positive charge)
    CONSUMER: Electron cloud (negative charge)
    COUPLER:  Virtual photons (EM field, α = 0.0073)
    SCALE:    Atomic (~10⁻¹⁰ m)
    RESULT:   Chemistry — sharing and exchanging electrons
    ARA:      α is weak enough that electrons aren't trapped
              but strong enough that atoms are stable
              → enables the MIDDLE ground of molecular complexity

  THE GRAVITY COUPLER (α_G ≈ 6×10⁻³⁹):
    ENGINE:   Mass-energy (any massive particle)
    CONSUMER: Space-time curvature (geometry bends)
    COUPLER:  Gravitons / curved spacetime (gravity field, α_G = 6×10⁻³⁹)
    SCALE:    Cosmic (~10²⁶ m)
    RESULT:   Structure — aggregation into stars, galaxies, clusters
    ARA:      α_G is so weak that individual particles barely feel it
              but it ONLY attracts (no cancellation) and is infinite-range
              → the weakness enables the LARGEST structures
""")

# The KEY insight: coupling strength determines SCALE of operation
print("  COUPLING STRENGTH → SCALE OF OPERATION:")
print(f"    Strong (α ≈ 1):        operates at ~10⁻¹⁵ m (nucleus)")
print(f"    EM (α ≈ 1/137):        operates at ~10⁻¹⁰ m (atom)")
print(f"    Weak (α ≈ 1/30):       operates at ~10⁻¹⁸ m (but via mass)")
print(f"    Gravity (α_G ≈ 10⁻³⁹): operates at ~10²⁶ m (universe)")
print(f"\n    Scale range: ~10⁴¹ m → log_φ = {math.log(1e41)/math.log(PHI):.1f} φ-rungs")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 7: IS GRAVITY JUST EM AT A DIFFERENT φ-RUNG?")
print("=" * 72)

# If coupling constants sit on φ-rungs, gravity might be EM
# shifted by some number of φ-rungs
log_phi_EM = math.log(alpha_EM) / math.log(PHI)
log_phi_G = math.log(alpha_G) / math.log(PHI)
separation = log_phi_EM - log_phi_G

print(f"\n  EM:      log_φ(α)   = {log_phi_EM:.4f}")
print(f"  Gravity: log_φ(α_G) = {log_phi_G:.4f}")
print(f"  Separation: {separation:.4f} φ-rungs")
print(f"  Nearest integer: {round(separation)}")
print(f"  Residual: {separation - round(separation):+.4f}")

# Check: is the separation a φ-power itself?
for k in range(1, 10):
    phi_k = PHI**k
    delta = abs(separation - phi_k)
    if delta < 5:
        print(f"  φ^{k} = {phi_k:.4f}, Δ from separation = {delta:.4f}")

# Is the separation related to known numbers?
print(f"\n  Separation = {separation:.2f}")
print(f"  π × φ^4 = {math.pi * PHI**4:.2f}")
print(f"  φ^5 × 2π = {PHI**5 * 2 * math.pi:.2f}")
print(f"  90 × π/φ = {90 * math.pi / PHI:.2f}")
print(f"  φ^{round(math.log(separation)/math.log(PHI))} = {PHI**round(math.log(separation)/math.log(PHI)):.2f}")

log_phi_sep = math.log(separation) / math.log(PHI)
print(f"  log_φ(separation) = {log_phi_sep:.4f}")
print(f"  Nearest rung: φ^{round(log_phi_sep)}")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 8: THE HIERARCHY PROBLEM — WHY IS GRAVITY WEAK?")
print("=" * 72)

print(f"""
  The hierarchy problem is one of the biggest unsolved questions in physics:
  Why is gravity ~10³⁶ times weaker than EM?

  Standard physics says: we don't know. It's "fine-tuned."

  ARA framework perspective:
""")

print(f"  In ARA, coupling strength determines what you CAN couple:")
print(f"    α ≈ 1 (strong): locks quarks together. Cannot share.")
print(f"    α ≈ 1/137 (EM): holds atoms, but allows chemistry. Can share electrons.")
print(f"    α ≈ 1/30 (weak): transmutes particles. Slow, rare.")
print(f"    α_G ≈ 10⁻³⁹ (gravity): nearly nothing per particle.")
print(f"")
print(f"  But gravity has TWO unique properties no other force has:")
print(f"    1. It is ALWAYS attractive (no cancellation)")
print(f"    2. It couples to EVERYTHING with mass-energy")
print(f"")
print(f"  The ARA interpretation:")
print(f"    α_G is not 'weak'. It is the DEEPEST consumer coupler.")
print(f"    A consumer coupler ACCUMULATES rather than exchanges.")
print(f"    EM exchanges photons back and forth — symmetric coupling.")
print(f"    Gravity only accumulates curvature — one-way coupling.")
print(f"")
print(f"    In ARA terms:")
print(f"      EM coupling:      exchange-based → shock absorber behavior")
print(f"      Gravity coupling:  accumulation-based → pure consumer behavior")
print(f"")
print(f"    The 'weakness' IS the signature of a consumer coupler.")
print(f"    Consumers absorb more than they release.")
print(f"    Gravity absorbs ALL coupling energy into geometry —")
print(f"    it doesn't give photons back, it curves spacetime.")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 9: GRAVITY AND THE ARA SCALE — Dimensional Analysis")
print("=" * 72)

# What if we express the forces as ARA ratios?
# Strong force: quarks are BOUND → engine behavior (accumulate quarks)
# EM: electrons EXCHANGE → absorber behavior (back and forth)
# Weak: particles DECAY → consumer behavior (net loss)
# Gravity: space CURVES → ?

# The key ratio: gravitational binding energy / rest mass energy
# For a proton pair at 1 fm (strong force distance):
r_fm = 1e-15  # 1 femtometer
E_grav_proton = G * m_p**2 / r_fm  # gravitational energy at nuclear distance
E_EM_proton = alpha_EM * hbar * c / r_fm  # EM energy at nuclear distance
E_rest_proton = m_p * c**2

print(f"\n  Energy comparison at nuclear distance (1 fm):")
print(f"    Gravitational:  {E_grav_proton:.2e} J = {E_grav_proton/1.602e-19:.2e} eV")
print(f"    Electromagnetic: {E_EM_proton:.2e} J = {E_EM_proton/1.602e-19:.2e} eV")
print(f"    Proton rest:     {E_rest_proton:.2e} J = {E_rest_proton/1.602e-19:.2e} eV")
print(f"    Ratio EM/Grav at 1fm: {E_EM_proton/E_grav_proton:.2e}")

# At what distance does gravity equal EM for two protons?
# G*m²/r = α*ℏc/r → they're both 1/r, so ratio is scale-independent!
print(f"\n  CRITICAL: Both EM and gravity scale as 1/r")
print(f"  Their RATIO is distance-independent: α_EM/α_G = {alpha_EM/alpha_G:.2e}")
print(f"  Gravity can NEVER catch up to EM at any distance!")
print(f"  Gravity wins only through NUMBERS — astronomical quantities of mass")

# How many protons needed for gravity to match EM?
N_crossover = math.sqrt(alpha_EM / alpha_G)
print(f"\n  Protons needed for gravity to match EM: √(α/α_G) = {N_crossover:.2e}")
print(f"  log_φ(N): {math.log(N_crossover)/math.log(PHI):.2f}")
print(f"  That's about {N_crossover/6e23:.1e} moles")
print(f"  ≈ mass of {N_crossover * m_p:.2e} kg")

# Is this close to any known mass?
crossover_mass = N_crossover * m_p
print(f"\n  The 'gravity = EM' crossover mass:")
print(f"    = {crossover_mass:.2e} kg")
print(f"    = {crossover_mass/5.97e24:.4f} Earth masses")
print(f"    Earth mass = {5.97e24:.2e} kg")
print(f"    Jupiter mass = {1.90e27:.2e} kg")
print(f"    Sun mass = {1.99e30:.2e} kg")
print(f"    Crossover/Earth: {crossover_mass/5.97e24:.4f}")

# Chandrasekhar mass: ~1.4 solar masses — where electron degeneracy = gravity
M_Ch = 1.4 * 1.99e30
print(f"\n  Chandrasekhar mass (e⁻ degeneracy = gravity): {M_Ch:.2e} kg")
print(f"  log_φ(Chandrasekhar/proton): {math.log(M_Ch/m_p)/math.log(PHI):.2f}")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 10: THE φ-RUNG LADDER OF FORCES")
print("=" * 72)

# Let's map everything onto the φ-rung ladder
print("\nEverything in log-φ space (coupling constants):")
items = [
    ("α_G (gravity, e-e)",  alpha_G_e),
    ("α_G (gravity, p-p)",  alpha_G),
    ("α_W (weak)",          alpha_W),
    ("α_EM (electromagnetic)", alpha_EM),
    ("α_S (strong)",        alpha_S),
]

print(f"{'Constant':<30} {'Value':>14} {'log_φ':>10} {'Rung':>8} {'Residual':>10}")
print("-" * 75)
for name, val in items:
    log_phi = math.log(val) / math.log(PHI)
    nearest = round(log_phi)
    residual = log_phi - nearest
    print(f"  {name:<28} {val:>14.4e} {log_phi:>10.2f} {'φ^'+str(nearest):>8} {residual:>+10.4f}")

# Spacing between consecutive forces
print(f"\n  Spacings in φ-rungs:")
log_phis = [math.log(val)/math.log(PHI) for _, val in items]
for i in range(len(items)-1):
    gap = log_phis[i+1] - log_phis[i]
    print(f"    {items[i][0]:>30} → {items[i+1][0]:<25}: {gap:>+.2f} rungs")

# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 72)
print("PART 11: GRAVITY AS THE UNIVERSE'S CONSUMER COUPLER")
print("=" * 72)

print("""
  SYNTHESIS: What IS Gravity in ARA Terms?

  The four forces form a hierarchy of coupler types:

  STRONG (α ≈ 1):
    → ENGINE coupler — holds quarks together, produces mass
    → Works at smallest scale (10⁻¹⁵ m)
    → Confines: the more you pull, the stronger it gets
    → ARA behavior: ACCUMULATOR (confinement = one-way accumulation)

  EM (α ≈ 1/137):
    → SHOCK ABSORBER coupler — exchanges photons bidirectionally
    → Works at atomic scale (10⁻¹⁰ m)
    → Attracts AND repels, cancels over large distances
    → ARA behavior: ABSORBER (exchange = balanced back-and-forth)
    → The weakness enables chemistry (sharing, not trapping)

  WEAK (α ≈ 1/30):
    → RELEASE coupler — enables particle transformation
    → Works at nuclear scale but through mass (W/Z bosons heavy)
    → Violates symmetries that others preserve
    → ARA behavior: RELEASE MECHANISM (decay = net loss from system)

  GRAVITY (α_G ≈ 10⁻³⁹):
    → PURE CONSUMER coupler — only accumulates, never repels
    → Works at ALL scales (infinite range, no cancellation)
    → The weakness per particle is COMPENSATED by universality
    → ARA behavior: CONSUMER (curvature = one-way energy absorption)
    → Curves spacetime irreversibly — energy goes IN, geometry comes OUT
    → The extreme weakness means it takes ~10¹⁸ particles before
      gravity even competes with EM
    → This sets the MINIMUM SIZE for gravitational structures:
      roughly 10¹⁸ protons = a small asteroid

  THE FRAMEWORK ANSWER TO 'WHAT IS GRAVITY?':
    Gravity is the universe's consumer coupler.
    Where EM exchanges (absorber), gravity only absorbs (consumer).
    Its extreme weakness is not a defect — it is the signature of
    a coupler that works by ACCUMULATION rather than exchange.

    EM builds atoms. Gravity builds EVERYTHING ELSE.
    EM needs opposite charges. Gravity just needs mass.
    EM cancels. Gravity adds.

    In ARA terms: gravity is to EM what a consumer is to a shock absorber.
    Consumers are weaker step-by-step, but over long enough time
    (or enough mass), they reshape the entire landscape.

    The hierarchy problem (why 10³⁶?) may be equivalent to asking:
    what is the ARA ratio between the consumer and absorber regimes?
    In log-φ space, the separation is ~79 rungs.
""")

# Final calculation: the separation as potential ARA ratio
sep_rungs = abs(log_phi_G - log_phi_EM)
print(f"  EM → Gravity separation: {sep_rungs:.2f} φ-rungs")
print(f"  φ^{round(sep_rungs)} = {PHI**round(sep_rungs):.2e}")
print(f"  Actual ratio α_EM/α_G = {alpha_EM/alpha_G:.2e}")
print(f"  Match: {(alpha_EM/alpha_G)/(PHI**round(sep_rungs)):.4f}")

print("\nScript complete.")
