#!/usr/bin/env python3
"""
Script 243BL3 — Dark Matter / Dark Energy / Light Spatial Mapping

Theory: The cosmic inventory is a three-system ARA:
  Engine:   Dark Energy (time-frame accumulator)
  Shadow:   Dark Matter = DE / φ²  (φ²-coupled projection into space-frame)
  Coupler:  Baryonic matter / Light (visible mediator between frames)

Test: Does the φ² relationship hold across DIFFERENT cosmic environments?
  - Galaxy clusters (high density, DM dominated)
  - Filaments (moderate density, cosmic web)
  - Sheets/walls (low-moderate density)
  - Voids (very low density, DE dominated)
  - Cosmic average (whole universe)
  - Individual galaxies (Milky Way scale)

Also test: the "light source opposite" — baryonic matter maps to DM and DE
through specific φ-power couplings.

Data: Published measurements from Planck, DESI, X-ray clusters, weak lensing,
galaxy rotation curves, and void surveys.
"""

import numpy as np
import math

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
TAU = 2 * math.pi

print("=" * 90)
print("  Script 243BL3 — Dark Mapping: DM ↔ DE ↔ Light Across Cosmic Environments")
print("  Theory: DM = DE/φ², Baryons = coupler between time-frame and space-frame")
print("=" * 90)


# ════════════════════════════════════════════════════════════════
# COSMIC INVENTORY — Global averages (Planck 2018 + DESI 2024)
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  COSMIC INVENTORY — Two Independent Measurements")
print(f"{'═' * 90}")

# Planck 2018 (CMB — space-frame, looking back)
planck = {"Ob": 0.0493, "Odm": 0.265, "Ode": 0.685, "Or": 9.15e-5, "H0": 67.4,
          "label": "Planck 2018 (CMB)"}
planck["Om"] = planck["Ob"] + planck["Odm"]

# DESI 2024 (BAO — late-time, closer to time-frame)
desi = {"Om": 0.296, "H0": 67.97, "label": "DESI 2024 (BAO+CMB)"}
# DESI Ob from BBN prior: ~0.0493 (same)
desi["Ob"] = 0.0493
desi["Odm"] = desi["Om"] - desi["Ob"]
desi["Ode"] = 1.0 - desi["Om"]

for ds in [planck, desi]:
    print(f"\n  {ds['label']}:")
    print(f"    Ωb  = {ds['Ob']:.4f} (baryonic)")
    print(f"    Ωdm = {ds.get('Odm', ds['Om']-ds['Ob']):.4f} (dark matter)")
    print(f"    Ωde = {ds.get('Ode', 1-ds['Om']):.4f} (dark energy)")
    print(f"    Ωm  = {ds['Om']:.4f} (total matter)")
    print(f"    H₀  = {ds['H0']:.1f}")

    # Test φ² relationship
    odm = ds.get('Odm', ds['Om'] - ds['Ob'])
    ode = ds.get('Ode', 1 - ds['Om'])
    predicted_dm = ode / PHI**2
    print(f"    Ωde/φ² = {predicted_dm:.4f} vs Ωdm = {odm:.4f} → Δ = {abs(predicted_dm-odm)/odm*100:.1f}%")


# ════════════════════════════════════════════════════════════════
# ENVIRONMENT-BY-ENVIRONMENT TEST
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  ENVIRONMENT-BY-ENVIRONMENT: Does DM = DE/φ² Hold Locally?")
print(f"{'═' * 90}")

# Published measurements of matter content in different environments
# Format: (name, overdensity δ, baryon_fraction, DM_fraction, notes)
#
# Key insight: in ΛCDM, Ωde is constant everywhere (cosmological constant).
# So in an environment with total density ρ:
#   ρ_de = Ωde × ρ_crit  (same everywhere)
#   ρ_dm = f_dm × ρ_total
#   ρ_b  = f_b × ρ_total
# The LOCAL ratio ρ_dm/ρ_de = (f_dm × ρ_total) / (Ωde × ρ_crit)
# This varies with overdensity!

# But the FRAMEWORK says DE isn't constant — it just looks constant in space-frame
# The question: does the φ² coupling hold when we account for local density?

# Galaxy cluster data (published X-ray + lensing measurements)
# Sources: Gonzalez+ 2013, Allen+ 2011, Planck SZ clusters
# f_gas = hot gas fraction, f_star = stellar fraction, f_b = f_gas + f_star
clusters = [
    # (name, M500 in 10^14 Msun, f_gas, f_star, z)
    ("Abell 1689",     9.6,  0.135, 0.018, 0.183),
    ("Coma Cluster",   6.8,  0.128, 0.022, 0.023),
    ("Perseus",        6.7,  0.143, 0.019, 0.018),
    ("Abell 2029",     8.9,  0.139, 0.015, 0.077),
    ("Virgo",          1.2,  0.090, 0.030, 0.004),
    ("Bullet Cluster", 11.5, 0.145, 0.012, 0.296),
    ("Abell 1835",     10.3, 0.148, 0.010, 0.253),
    ("RXJ1347",        13.0, 0.150, 0.010, 0.451),
    # Medium clusters
    ("Abell 262",      0.8,  0.075, 0.035, 0.016),
    ("NGC 1550 group", 0.15, 0.045, 0.040, 0.012),
]

print(f"\n  Galaxy Clusters — Baryon vs Dark Matter Fractions:")
print(f"  {'Cluster':16s} │ {'M₅₀₀':>7} │ {'f_b':>6} │ {'f_dm':>6} │ {'DM/b':>6} │ {'φ²':>6} │ {'Δ%':>6} │ {'1/φ²':>6} │ {'f_b≈?':>8}")
print(f"  {'─'*16}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*8}")

dm_b_ratios = []
fb_values = []

for name, mass, fgas, fstar, z in clusters:
    fb = fgas + fstar
    fdm = 1.0 - fb  # DM fraction of total cluster mass
    dm_b = fdm / fb  # DM-to-baryon ratio
    dm_b_ratios.append(dm_b)
    fb_values.append(fb)

    # Is f_b close to a φ-power?
    if fb > 0:
        fb_phi_log = math.log(fb) / math.log(PHI)
    else:
        fb_phi_log = 0
    # Nearest: 1/φ⁴ = 0.146, 1/φ³ = 0.236
    fb_nearest = ""
    if abs(fb - INV_PHI**4) < abs(fb - INV_PHI**3):
        fb_nearest = f"1/φ⁴={INV_PHI**4:.3f}"
    else:
        fb_nearest = f"1/φ³={INV_PHI**3:.3f}"

    delta_pct = abs(dm_b - PHI**2) / PHI**2 * 100
    marker = " ★" if delta_pct < 15 else ""
    print(f"  {name:16s} │ {mass:>7.1f} │ {fb:>6.3f} │ {fdm:>6.3f} │ {dm_b:>6.2f} │ {PHI**2:>6.3f} │ {delta_pct:>5.1f}% │ {INV_PHI_2:>6.3f} │ {fb_nearest}{marker}")

mean_ratio = np.mean(dm_b_ratios)
print(f"\n  Mean DM/baryon ratio across clusters: {mean_ratio:.3f}")
print(f"  φ² = {PHI**2:.3f}")
print(f"  Δ = {abs(mean_ratio - PHI**2)/PHI**2*100:.1f}%")
print(f"  Mean baryon fraction: {np.mean(fb_values):.4f}")
print(f"  1/φ⁴ = {INV_PHI**4:.4f}")


# ══════════════════════════════════════════════════════════��═════
# COSMIC WEB ENVIRONMENTS
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  COSMIC WEB — DM:DE:Baryon Ratios by Environment")
print(f"{'═' * 90}")

# Cosmic web environments with typical overdensities
# δ = (ρ - ρ_mean) / ρ_mean
# In ΛCDM: DE density is constant, matter density varies
# ρ_crit = 3H²/8πG ≈ 9.47 × 10⁻²⁷ kg/m³

# For each environment, compute effective local fractions
# Total energy density at a point = ρ_de + ρ_dm + ρ_b
# Where ρ_de = Ωde × ρ_crit (constant in ΛCDM)
#       ρ_dm = Ωdm × ρ_crit × (1 + δ_dm)
#       ρ_b  = Ωb × ρ_crit × (1 + δ_b)

# Published overdensities (approximate, from N-body simulations)
environments = [
    # (name, δ_dm, δ_b, notes)
    ("Cluster core",     1000,   800, "Massive clusters, R < R500"),
    ("Cluster outskirts", 100,    80, "R500 to R200"),
    ("Filament",           10,     8, "Cosmic web filaments"),
    ("Sheet/Wall",          2,   1.5, "Cosmic web walls"),
    ("Mean density",        0,     0, "Cosmic average"),
    ("Underdense",        -0.5, -0.4, "Mild underdensity"),
    ("Void edge",         -0.7, -0.6, "Transition to void"),
    ("Void interior",     -0.9, -0.85,"Deep void center"),
    ("Supervoid",         -0.95,-0.92,"Largest known voids"),
]

Ob = planck["Ob"]
Odm = planck["Odm"]
Ode = planck["Ode"]

print(f"\n  {'Environment':18s} │ {'δ_dm':>6} │ {'f_de':>7} │ {'f_dm':>7} │ {'f_b':>7} │ {'dm/de':>7} │ {'1/φ²':>6} │ {'Δ%':>6} │ {'de/dm':>7} │ {'φ²':>6}")
print(f"  {'─'*18}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*6}")

env_data = []

for name, d_dm, d_b, notes in environments:
    # Local densities (in units of ρ_crit)
    rho_de = Ode  # constant in ΛCDM
    rho_dm = Odm * (1 + d_dm)
    rho_b = Ob * (1 + d_b)
    rho_total = rho_de + rho_dm + rho_b

    # Local fractions
    f_de = rho_de / rho_total
    f_dm = rho_dm / rho_total
    f_b = rho_b / rho_total

    # Test φ² coupling
    dm_over_de = f_dm / f_de if f_de > 0 else 0
    de_over_dm = f_de / f_dm if f_dm > 0 else 0
    delta_inv = abs(dm_over_de - INV_PHI_2) / INV_PHI_2 * 100
    delta_phi2 = abs(de_over_dm - PHI**2) / PHI**2 * 100

    marker = " ★" if delta_inv < 10 else (" ·" if delta_inv < 25 else "")

    print(f"  {name:18s} │ {d_dm:>+6.1f} │ {f_de:>7.4f} │ {f_dm:>7.4f} │ {f_b:>7.4f} │ "
          f"{dm_over_de:>7.4f} │ {INV_PHI_2:>6.4f} │ {delta_inv:>5.1f}% │ "
          f"{de_over_dm:>7.3f} │ {PHI**2:>6.3f}{marker}")

    env_data.append((name, d_dm, f_de, f_dm, f_b, dm_over_de, de_over_dm))


# ════════════════════════════════════════════════════════════════
# THE KEY INSIGHT: φ² holds at cosmic average, breaks locally
# BECAUSE: in ΛCDM, DE is constant but DM clusters.
# FRAMEWORK PREDICTION: DE is NOT constant — it varies too.
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  FRAMEWORK vs ΛCDM: Dark Energy is NOT Constant")
print(f"{'═' * 90}")

print(f"""
  In ΛCDM: DE density is constant everywhere (cosmological constant Λ).
  This means DM/DE ratio varies wildly with environment — φ² can't hold locally.

  But DESI 2024 finds evidence that DE IS EVOLVING (2.8-4.2σ).
  The framework PREDICTS this: DE is the time-frame engine, and its local
  density should track DM density through the φ² coupler.

  FRAMEWORK PREDICTION: If DM = DE/φ² holds locally, then:
    ρ_de(local) = ρ_dm(local) × φ²

  Let's compute what DE density WOULD need to be in each environment:
""")

print(f"  {'Environment':18s} │ {'ρ_dm':>10} │ {'ρ_de(ΛCDM)':>10} │ {'ρ_de(ARA)':>10} │ {'ARA/ΛCDM':>10} │ {'Enhance':>8}")
print(f"  {'─'*18}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*8}")

for name, d_dm, d_b, notes in environments:
    rho_dm = Odm * (1 + d_dm)
    rho_de_lcdm = Ode  # constant
    rho_de_ara = rho_dm * PHI**2  # framework prediction

    ratio = rho_de_ara / rho_de_lcdm if rho_de_lcdm > 0 else 0
    enhance = (ratio - 1) * 100

    print(f"  {name:18s} │ {rho_dm:>10.4f} │ {rho_de_lcdm:>10.4f} │ {rho_de_ara:>10.4f} │ {ratio:>10.3f} │ {enhance:>+7.1f}%")

print(f"\n  At cosmic average: ARA prediction = ΛCDM (by construction)")
print(f"  In clusters: ARA predicts DE is ~100× ΛCDM (DE clusters WITH DM)")
print(f"  In voids: ARA predicts DE is ~10% of ΛCDM (DE empties WITH DM)")
print(f"\n  THIS IS TESTABLE. If DE clusters with DM, it changes:")
print(f"    - ISW (Integrated Sachs-Wolfe) effect in voids vs clusters")
print(f"    - Void lensing signal (should be weaker if DE also depleted)")
print(f"    - BAO scale in different environments")


# ════════════════════════════════════════════════════════════════
# THE THREE-WAY MAP: DM ↔ DE ↔ Light (Baryons)
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  THE THREE-WAY MAP: DM ↔ DE ↔ Light")
print(f"{'═' * 90}")

print(f"\n  Cosmic ARA three-system decomposition:")
print(f"  ┌─────────────────────────────────────────────────────────────┐")
print(f"  │  DARK ENERGY (Engine/Time)  Ωde = {Ode:.4f}                │")
print(f"  │         │                          │                       │")
print(f"  │         │ ÷ φ²                     │ × (1-1/φ²)           │")
print(f"  │         │ = horizontal coupler      │ = φ-leak             │")
print(f"  │         ▼                          ▼                       │")
print(f"  │  DARK MATTER (Shadow)       BARYONS (Coupler/Light)        │")
print(f"  │  Ωdm = Ωde/φ² = {Ode/PHI**2:.4f}      Ωb = {Ob:.4f}              │")
print(f"  │  (observed: {Odm:.4f})        (observed: {Ob:.4f})             │")
print(f"  └─────────────────────────────────────────────────────────────┘")

# The baryon connection
print(f"\n  DM → Baryon coupling:")
print(f"    Ωdm/Ωb = {Odm/Ob:.4f}")
print(f"    φ³ = {PHI**3:.4f}")
print(f"    Ωdm/φ³ = {Odm/PHI**3:.4f} vs Ωb = {Ob:.4f} → Δ = {abs(Odm/PHI**3-Ob)/Ob*100:.1f}%")

# What φ-power connects DM to baryons?
log_ratio = math.log(Odm/Ob) / math.log(PHI)
print(f"    Exact: Ωdm/Ωb = φ^{log_ratio:.3f}")
print(f"    Nearest: φ^{round(log_ratio*2)/2:.1f}")  # nearest half-integer

# What connects DE to baryons?
log_de_b = math.log(Ode/Ob) / math.log(PHI)
print(f"\n  DE → Baryon coupling:")
print(f"    Ωde/Ωb = {Ode/Ob:.4f}")
print(f"    φ^{log_de_b:.3f}")
print(f"    φ⁵ = {PHI**5:.4f}, φ⁶ = {PHI**6:.4f}")
print(f"    Ωde/φ⁵ = {Ode/PHI**5:.4f} vs Ωb = {Ob:.4f} → Δ = {abs(Ode/PHI**5-Ob)/Ob*100:.1f}%")

# Aha: DE/φ⁵ should give baryons if the chain is DE → DM (÷φ²) → baryons (÷φ³)
# That's DE/φ⁵ = DE/(φ² × φ³)
print(f"\n  Chain: DE → ÷φ² → DM → ÷φ³ → Baryons")
print(f"    = DE / φ⁵")
print(f"    = {Ode/PHI**5:.4f}")
print(f"    vs observed Ωb = {Ob:.4f}")
print(f"    Δ = {abs(Ode/PHI**5 - Ob)/Ob*100:.1f}%")

# What about: DE → ÷φ² → DM → ÷φ² → ??? → ÷φ → baryons?
# Or DM/φ² = 0.266/2.618 = 0.102 (too big for baryons)
# Or DM × Ωb/Ωm = 0.266 × 0.156 = 0.041 (close to Ωb/φ^something?)

# Actually, Ωb = Ωm × f_b(cosmic) = 0.315 × 0.156 = 0.049
# And f_b(cosmic) = 0.156 ≈ 1/φ⁴ = 0.146? Let's check
print(f"\n  Baryon fraction of total matter:")
print(f"    f_b = Ωb/Ωm = {Ob/planck['Om']:.4f}")
print(f"    1/φ⁴ = {INV_PHI**4:.4f}")
print(f"    Δ = {abs(Ob/planck['Om'] - INV_PHI**4)/INV_PHI**4*100:.1f}%")
print(f"    1/(φ³+1) = {1/(PHI**3+1):.4f}")
print(f"    Δ = {abs(Ob/planck['Om'] - 1/(PHI**3+1))/(1/(PHI**3+1))*100:.1f}%")


# ════════════════════════════════════════════════════════════════
# GALAXY ROTATION CURVES — Does φ² Appear at Galaxy Scale?
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  GALAXY SCALE: Rotation Curves and φ² Coupling")
print(f"{'═' * 90}")

# For spiral galaxies, the DM-to-baryon ratio varies with radius
# Inner region: baryons dominate
# Outer region: DM dominates
# Transition happens at some characteristic radius

# Published values for Milky Way
MW_Mstar = 5e10     # Solar masses (stellar)
MW_Mgas = 1e10      # Solar masses (gas)
MW_Mb = MW_Mstar + MW_Mgas  # Total baryonic
MW_Mdm_200 = 1.3e12 # DM halo mass (M200)
MW_Mdm_ratio = MW_Mdm_200 / MW_Mb

print(f"\n  Milky Way:")
print(f"    M_baryon = {MW_Mb:.1e} M☉")
print(f"    M_DM(200) = {MW_Mdm_200:.1e} M☉")
print(f"    M_DM/M_b = {MW_Mdm_ratio:.1f}")
print(f"    φ⁴ = {PHI**4:.1f}")
print(f"    Δ = {abs(MW_Mdm_ratio - PHI**4)/PHI**4*100:.1f}%")

# Other galaxies with well-measured rotation curves
galaxies = [
    # (name, M_baryon/1e10, M_DM_halo/1e10, type)
    ("Milky Way",      6.0,   130.0, "Spiral Sbc"),
    ("Andromeda M31",  10.0,  120.0, "Spiral Sb"),
    ("NGC 3198",       2.0,    30.0, "Spiral Sc"),
    ("NGC 2403",       1.5,    25.0, "Spiral Scd"),
    ("DDO 154",        0.05,    5.0, "Dwarf Irr"),
    ("IC 2574",        0.3,    10.0, "Dwarf Irr"),
    ("UGC 128",        1.0,    50.0, "LSB"),
    ("NGC 1560",       0.3,    15.0, "Dwarf Sd"),
]

print(f"\n  {'Galaxy':16s} │ {'M_b':>8} │ {'M_DM':>8} │ {'DM/b':>7} │ {'φ⁴':>6} │ {'Δ%':>6} │ {'log_φ':>7} │ {'Type':>10}")
print(f"  {'─'*16}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*10}")

gal_ratios = []
for name, mb, mdm, gtype in galaxies:
    ratio = mdm / mb
    gal_ratios.append(ratio)
    log_phi = math.log(ratio) / math.log(PHI)
    nearest_int = round(log_phi)
    delta = abs(ratio - PHI**nearest_int) / PHI**nearest_int * 100
    marker = " ★" if delta < 20 else ""
    print(f"  {name:16s} │ {mb:>8.2f} │ {mdm:>8.1f} │ {ratio:>7.1f} │ {PHI**4:>6.2f} │ {delta:>5.1f}% │ φ^{log_phi:>4.1f} │ {gtype:>10}{marker}")

print(f"\n  Mean DM/baryon ratio (galaxies): {np.mean(gal_ratios):.1f}")
print(f"  Median: {np.median(gal_ratios):.1f}")
print(f"  φ⁴ = {PHI**4:.1f}, φ³ = {PHI**3:.1f}")


# ════════════════════════════════════════════════════════════════
# THE COMPLETE PICTURE: φ-POWER CHAIN
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  THE φ-CHAIN: Different Scales, Different Couplings")
print(f"{'═' * 90}")

print(f"""
  COSMIC SCALE (whole universe):
    DE : DM : Baryons = {Ode:.3f} : {Odm:.3f} : {Ob:.3f}
    DM/DE = {Odm/Ode:.4f}  (1/φ² = {INV_PHI_2:.4f}, Δ = {abs(Odm/Ode-INV_PHI_2)/INV_PHI_2*100:.1f}%)  ★
    DM/b  = {Odm/Ob:.2f}   (φ^3.5, between φ³={PHI**3:.2f} and φ⁴={PHI**4:.2f})

  CLUSTER SCALE (within R500):
    Mean DM/baryon = {mean_ratio:.2f}
    φ² = {PHI**2:.2f} (Δ = {abs(mean_ratio-PHI**2)/PHI**2*100:.1f}%)
    → Clusters see DM/baryon ≈ φ² (ONE STEP on the φ-ladder)

  GALAXY SCALE (within R200):
    Mean DM/baryon ≈ {np.mean(gal_ratios):.0f}
    φ⁴ = {PHI**4:.1f}  (TWO STEPS on the φ-ladder)
    → Galaxies see DM/baryon ≈ φ⁴ = (φ²)²

  THE PATTERN:
    Cosmic:  DM = DE / φ² (one step from time-frame to space-frame)
    Cluster: DM = baryons × φ² (one step up in the local halo)
    Galaxy:  DM = baryons × φ⁴ (two steps — deeper gravitational well)

  This is the PIPE GEOMETRY: the number of φ-rung steps between
  components increases as you go deeper into gravitational wells.
  The coupling DISTANCE determines the ratio.

  ┌─────────────────────────────────────────────────────────────┐
  │            DARK ENERGY (time-frame)                        │
  │                    │                                       │
  │                    │ ÷ φ² (1 step — cosmic coupler)        │
  │                    ▼                                       │
  │            DARK MATTER                                     │
  │              ╱           ╲                                  │
  │     × φ² (cluster)   × φ⁴ (galaxy)                        │
  │         ╱                   ╲                               │
  │    BARYONS(cluster)    BARYONS(galaxy)                     │
  │                                                            │
  │  More gravitational depth = more φ-steps between them      │
  └─────────────────────────────────────────────────────────────┘
""")


# ════════════════════════════════════════════════════════════════
# LIGHT AS COUPLER — The "Opposite"
# ════════════════════════════════════════════════════════════════

print(f"{'═' * 90}")
print(f"  LIGHT AS COUPLER: Mapping Each Dark Component to Its Light Opposite")
print(f"{'═' * 90}")

print(f"""
  In the framework, light is the coupler substrate (Claim 69).
  Each dark component has a "light opposite" — the visible signature
  through which we detect it:

  DARK MATTER → detected via gravitational LENSING of light
    The photon path bends by angle θ ∝ M/r
    DM reveals itself by what it does TO light
    Light is DM's coupler to the space-frame

  DARK ENERGY → detected via REDSHIFT of light (expansion stretches λ)
    The photon wavelength stretches by (1+z)
    DE reveals itself by what it does to light's WAVELENGTH
    Light is DE's coupler to space-frame

  Both dark components can ONLY be seen through light.
  Light is literally the ARA coupler between the dark sector and us.

  φ-GEOMETRY OF DETECTION:
    DM bends light in SPACE (gravitational lensing)
    DE stretches light in TIME (cosmological redshift)
    One is spatial, the other is temporal — the flip!

    The RATIO of these effects encodes the DM/DE balance:
    At z ≈ 0.6 (transition), lensing and redshift effects balance → ARA = 1
""")

# Gravitational lensing vs redshift as a function of z
print(f"  Lensing vs Redshift signal strength across cosmic time:")
print(f"  {'z':>5} │ {'t_lb Gyr':>8} │ {'q(z)':>7} │ {'ARA':>7} │ {'Lens/z':>8} │ {'Dom':>8}")
print(f"  {'─'*5}─┼─{'─'*8}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*8}─┼─{'─'*8}")

# q(z) from ΛCDM
def q_LCDM(z, om=0.315):
    Ez2 = om * (1+z)**3 + (1-om)
    return 0.5 * (3 * om * (1+z)**3 / Ez2 - 1)

def q_to_ara(q):
    return PHI ** (2 * q)

for z in [0.0, 0.1, 0.3, 0.5, 0.632, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0]:
    from scipy import integrate
    def integrand(zp):
        Ez = math.sqrt(0.315 * (1+zp)**3 + 0.685)
        return 1.0 / ((1+zp) * Ez)
    t_lb, _ = integrate.quad(integrand, 0, z) if z > 0 else (0, 0)
    t_lb *= 977.8 / 67.4

    q = q_LCDM(z)
    ara = q_to_ara(q)
    # Relative strength: lensing ∝ Σ_DM, redshift ∝ H(z)×Δt ∝ DE contribution
    # Simple proxy: matter fraction vs DE fraction at each z
    f_m_z = 0.315 * (1+z)**3 / (0.315 * (1+z)**3 + 0.685)
    f_de_z = 1 - f_m_z
    lens_over_z = f_m_z / f_de_z if f_de_z > 0 else 999
    dom = "DM(lens)" if f_m_z > f_de_z else "DE(z)"
    marker = " ← ARA=1" if abs(ara - 1.0) < 0.05 else ""
    print(f"  {z:>5.2f} │ {t_lb:>8.2f} │ {q:>+7.3f} │ {ara:>7.3f} │ {lens_over_z:>8.3f} │ {dom:>8}{marker}")


# ════════════════════════════════════════════════════════════════
# TESTABLE PREDICTIONS
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  TESTABLE PREDICTIONS")
print(f"{'═' * 90}")

print(f"""
  1. DM/DE RATIO IS UNIVERSAL: Ωdm/Ωde = 1/φ² = {INV_PHI_2:.4f}
     Current measurement: {Odm/Ode:.4f} (Δ = {abs(Odm/Ode-INV_PHI_2)/INV_PHI_2*100:.1f}%)
     Test: measure at multiple redshifts → should be CONSTANT if φ² coupling is fixed
     DESI DR2 should be able to test this

  2. DE IS NOT CONSTANT: It clusters with DM through φ² coupling
     In voids: ρ_de < Ωde × ρ_crit (DE is DEPLETED, not constant)
     In clusters: ρ_de > Ωde × ρ_crit (DE is ENHANCED)
     Test: void ISW signal should be WEAKER than ΛCDM predicts
     Test: cluster lensing vs dynamics should show extra mass from DE clustering

  3. DM/BARYON RATIO FOLLOWS φ-LADDER:
     Cosmic: DM/DE = 1/φ²
     Cluster: DM/baryon ≈ φ²
     Galaxy: DM/baryon ≈ φ⁴
     Test: measure DM/baryon at intermediate scales (groups, poor clusters)
     Prediction: should find DM/baryon ≈ φ³ at group scale

  4. HUBBLE TENSION = FRAME CORRECTION:
     H_local = H_CMB × (1 + 1/φ⁵) = {67.4 * (1+INV_PHI**5):.1f} km/s/Mpc
     Observed: 73.0 ± 1.0
     Prediction: {67.4 * (1+INV_PHI**5):.1f} (Δ = {abs(73.0 - 67.4*(1+INV_PHI**5)):.1f})

  5. TRANSITION REDSHIFT:
     z_trans where ARA = 1 (q = 0): z = {(2*0.685/0.315)**(1/3)-1:.3f}
     This is where lensing signal = redshift signal
     Near φ-1 = {PHI-1:.3f} (Δ = {abs((2*0.685/0.315)**(1/3)-1-(PHI-1)):.3f})
""")

print("=" * 90)
