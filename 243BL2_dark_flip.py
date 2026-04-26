#!/usr/bin/env python3
"""
Script 243BL2 — Dark Energy: The Time-Dominant Flip

Core insight (Dylan): The dark-energy-dominated regime has TIME as the
dominant system, not space. So our space-frame ARA coordinates are the
WRONG frame to read off φ-geometry. We need to:

  1. Flip coordinates: space-dominant → time-dominant
  2. Find where dark matter sits in TIME-frame ARA
  3. Check if the 10% Ωde miss disappears in the correct frame

Three-circle architecture:
  Space-frame (us, matter-dominated era):
    System 1 = Space (matter, gravity) → accumulates
    System 2 = Time (expansion) → releases
    System 3 = Rationality (coupling/information)
    ARA = Accumulation / Release ≈ Ωm/Ωde < 1 → consumer

  Time-frame (dark-energy-dominated regime):
    System 1 = Time → now the accumulator (accelerating expansion)
    System 2 = Space (matter) → now the consumer (diluting)
    System 3 = Rationality (coupling/information) → same coupler
    ARA = Ωde/Ωm > 1 → ENGINE

The flip: crossing ARA = 1 swaps which system is engine vs consumer.
The geometry should be the MIRROR of our space-frame geometry.
"""

import numpy as np
import math

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
TAU = 2 * math.pi

# Planck 2018 values
Omega_m = 0.315
Omega_de = 0.685
H0 = 67.4
H0_local = 73.0  # SH0ES

print("=" * 90)
print("  Script 243BL2 — Dark Energy: The Time-Dominant Flip")
print("  Hypothesis: Dark sector lives in TIME-frame coordinates, not space-frame")
print("=" * 90)


# ════════════════════════════════════════════════════════════════
# PART 1: THE TWO FRAMES
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  PART 1: Space-Frame vs Time-Frame")
print(f"{'═' * 90}")

# Space-frame ARA (our perspective)
ARA_space = Omega_m / Omega_de
# Time-frame ARA (dark sector perspective)
ARA_time = Omega_de / Omega_m  # = 1/ARA_space

print(f"\n  Space-frame (matter as System 1):")
print(f"    ARA_space = Ωm/Ωde = {Omega_m}/{Omega_de} = {ARA_space:.4f}")
print(f"    Type: CONSUMER (ARA < 1)")
print(f"    φ-rungs from clock: {math.log(ARA_space)/math.log(PHI):+.4f}")

print(f"\n  Time-frame (dark energy as System 1):")
print(f"    ARA_time = Ωde/Ωm = {Omega_de}/{Omega_m} = {ARA_time:.4f}")
print(f"    Type: ENGINE (ARA > 1)")
print(f"    φ-rungs from clock: {math.log(ARA_time)/math.log(PHI):+.4f}")

# Key: ARA_space × ARA_time = 1 always (they're reciprocals)
print(f"\n  ARA_space × ARA_time = {ARA_space * ARA_time:.4f} (= 1, by definition)")
print(f"  The flip IS the ARA loop — crossing 1.0 swaps engine/consumer")


# ════════════════════════════════════════════════════════════════
# PART 2: φ-GEOMETRY IN EACH FRAME
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  PART 2: φ-Geometry in Each Frame")
print(f"{'═' * 90}")

print(f"\n  Testing if fractions land on φ-powers in the CORRECT frame:")
print()

# In space-frame
phi_tests_space = {
    "Ωm":         Omega_m,
    "Ωde":        Omega_de,
    "Ωm/Ωde":     ARA_space,
    "1-Ωm":       1 - Omega_m,
}

print(f"  SPACE-FRAME (our measurement):")
print(f"  {'Quantity':15s} │ {'Value':>8} │ {'Nearest φ':>12} │ {'φ-power':>8} │ {'Δ':>8} │ {'Δ%':>6}")
print(f"  {'─'*15}─┼─{'─'*8}─┼─{'─'*12}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*6}")

def find_nearest_phi_power(val):
    """Find nearest φ^n or simple φ-expression."""
    if val <= 0:
        return "N/A", 0, 999
    candidates = {}
    for n in range(-6, 7):
        candidates[f"φ^{n}"] = PHI ** n
    candidates["1/π"] = 1/math.pi
    candidates["1/(φπ)"] = 1/(PHI * math.pi)
    candidates["φ/π"] = PHI/math.pi
    candidates["2/φ²"] = 2 * INV_PHI_2
    candidates["1-1/φ"] = 1 - INV_PHI
    candidates["1-1/φ²"] = 1 - INV_PHI_2
    candidates["φ-1"] = PHI - 1
    candidates["2-φ"] = 2 - PHI
    candidates["(φ+1)/π"] = (PHI+1)/math.pi

    best_name, best_val, best_delta = "", 0, 999
    for name, v in candidates.items():
        d = abs(val - v)
        if d < best_delta:
            best_name, best_val, best_delta = name, v, d
    pct = best_delta / val * 100 if val > 0 else 999
    return best_name, best_val, pct

for label, val in phi_tests_space.items():
    name, phival, pct = find_nearest_phi_power(val)
    print(f"  {label:15s} │ {val:>8.4f} │ {name:>12s} │ {phival:>8.4f} │ {abs(val-phival):>8.4f} │ {pct:>5.1f}%")

# In time-frame — same physical quantities but now interpreted as time-dominant
print()
print(f"  TIME-FRAME (dark sector perspective — flip Ωm ↔ Ωde roles):")
print(f"  {'Quantity':15s} │ {'Value':>8} │ {'Nearest φ':>12} │ {'φ-power':>8} │ {'Δ':>8} │ {'Δ%':>6}")
print(f"  {'─'*15}─┼─{'─'*8}─┼─{'─'*12}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*6}")

# In the time frame, what's "matter" is time-energy (Ωde), what's "antimatter/consumer" is space-matter (Ωm)
phi_tests_time = {
    "Ω_engine(=Ωde)":  Omega_de,
    "Ω_cons(=Ωm)":     Omega_m,
    "ARA_time":         ARA_time,
    "1/ARA_time":       1/ARA_time,
}

for label, val in phi_tests_time.items():
    name, phival, pct = find_nearest_phi_power(val)
    print(f"  {label:15s} │ {val:>8.4f} │ {name:>12s} │ {phival:>8.4f} │ {abs(val-phival):>8.4f} │ {pct:>5.1f}%")


# ════════════════════════════════════════════════════════════════
# PART 3: THE MIRROR — Where Does Dark Matter Sit?
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  PART 3: Mirror Geometry — Locating Dark Matter")
print(f"{'═' * 90}")

# In our space-frame:
#   Baryonic matter: Ωb = 0.049
#   Dark matter: Ωdm = 0.266
#   Dark energy: Ωde = 0.685
#   Radiation: Ωr ≈ 0 (now)

Omega_b = 0.049
Omega_dm = 0.266
Omega_r = 9.15e-5  # radiation today

print(f"\n  Current cosmic inventory (space-frame):")
print(f"    Baryonic matter:  Ωb  = {Omega_b:.4f}")
print(f"    Dark matter:      Ωdm = {Omega_dm:.4f}")
print(f"    Dark energy:      Ωde = {Omega_de:.4f}")
print(f"    Radiation:        Ωr  = {Omega_r:.5f}")
print(f"    Total:            Ω   = {Omega_b + Omega_dm + Omega_de + Omega_r:.4f}")

print(f"\n  Ratios to test:")
dm_b_ratio = Omega_dm / Omega_b
dm_de_ratio = Omega_dm / Omega_de
b_de_ratio = Omega_b / Omega_de
dm_total_m = Omega_dm / Omega_m

print(f"    Ωdm/Ωb  = {dm_b_ratio:.4f}")
print(f"    Ωdm/Ωde = {dm_de_ratio:.4f}")
print(f"    Ωb/Ωde  = {b_de_ratio:.4f}")
print(f"    Ωdm/Ωm  = {dm_total_m:.4f}")

print(f"\n  φ-proximity of key ratios:")
for label, val in [
    ("Ωdm/Ωb", dm_b_ratio),
    ("Ωdm/Ωde", dm_de_ratio),
    ("Ωb/Ωde", b_de_ratio),
    ("Ωdm/Ωm", dm_total_m),
]:
    name, phival, pct = find_nearest_phi_power(val)
    marker = " ★" if pct < 5 else ""
    print(f"    {label:12s} = {val:.4f} → nearest: {name:>12s} = {phival:.4f} (Δ = {pct:.1f}%){marker}")


# ════════════════════════════════════════════════════════════════
# PART 4: THREE-SYSTEM DECOMPOSITION OF COSMIC INVENTORY
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  PART 4: Three-System Decomposition — ARA of the Cosmos")
print(f"{'═' * 90}")

# Hypothesis: the cosmic inventory IS a three-system ARA
# System 1 (Engine/Accumulator): Dark Energy (drives expansion)
# System 2 (Consumer/Release): Baryonic matter (structured, entropy-producing)
# System 3 (Coupler): Dark Matter (mediates between the two)

print(f"\n  Hypothesis A: DE=Engine, Baryon=Consumer, DM=Coupler")
print(f"    Engine (Ωde):     {Omega_de:.4f}")
print(f"    Consumer (Ωb):    {Omega_b:.4f}")
print(f"    Coupler (Ωdm):    {Omega_dm:.4f}")
ara_A = Omega_de / Omega_b  # engine/consumer
coupler_fraction_A = Omega_dm / (Omega_de + Omega_b + Omega_dm)
print(f"    ARA = Engine/Consumer = {ara_A:.4f}")
name, phival, pct = find_nearest_phi_power(ara_A)
print(f"    Nearest φ: {name} = {phival:.4f} (Δ = {pct:.1f}%)")
print(f"    Coupler fraction: {coupler_fraction_A:.4f}")
name2, phival2, pct2 = find_nearest_phi_power(coupler_fraction_A)
print(f"    Nearest φ: {name2} = {phival2:.4f} (Δ = {pct2:.1f}%)")

# Hypothesis B: flip — Baryon=Engine (locally structured), DE=Consumer (dispersing)
print(f"\n  Hypothesis B: Baryon=Engine(local), DE=Consumer(dispersal), DM=Coupler")
ara_B = Omega_b / Omega_de
print(f"    ARA = Baryon/DE = {ara_B:.4f}")
name, phival, pct = find_nearest_phi_power(ara_B)
print(f"    Nearest φ: {name} = {phival:.4f} (Δ = {pct:.1f}%)")

# Hypothesis C: DM is NOT the coupler — it's the MIRROR engine
# In time-frame: DM is what "matter" looks like from time's perspective
print(f"\n  Hypothesis C: DM = Mirror of baryonic matter through the time flip")
print(f"    If DM is baryonic matter's reflection in time-frame:")
print(f"    Ωdm/Ωb = {dm_b_ratio:.4f}")
name, phival, pct = find_nearest_phi_power(dm_b_ratio)
print(f"    Nearest φ: {name} = {phival:.4f} (Δ = {pct:.1f}%)")

# The ratio Ωdm/Ωb ≈ 5.43 — is this φ^something?
log_phi = math.log(dm_b_ratio) / math.log(PHI)
print(f"    φ-power: Ωdm/Ωb = φ^{log_phi:.4f}")
print(f"    Nearest integer: φ^{round(log_phi)} = {PHI**round(log_phi):.4f}")
print(f"    Δ from φ^{round(log_phi)}: {abs(dm_b_ratio - PHI**round(log_phi)):.4f}")

# Is it 2π/φ² or something involving π?
print(f"    2π/φ² = {TAU/PHI**2:.4f}")
print(f"    φ³ = {PHI**3:.4f}")
print(f"    π·φ/φ² = π/φ = {math.pi/PHI:.4f}")


# ════════════════════════════════════════════════════════════════
# PART 5: THE FLIP GEOMETRY — Correcting the 10% Miss
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  PART 5: The Flip — Does Correcting Frame Fix the 10% Miss?")
print(f"{'═' * 90}")

print(f"\n  Original claim (243BL): Ωde = 1 - 1/φ² = 0.618")
print(f"  Observed: Ωde = 0.685")
print(f"  Miss: {abs(Omega_de - (1-INV_PHI_2)):.4f} = {abs(Omega_de-(1-INV_PHI_2))/Omega_de*100:.1f}%")

print(f"\n  THE FLIP HYPOTHESIS:")
print(f"  In space-frame, we measure Ωde = 0.685")
print(f"  But dark energy lives in TIME-frame")
print(f"  The coupling between frames goes through ARA = 1 (the singularity)")
print(f"  So the 'true' dark energy fraction in its own frame is:")

# Approach 1: Simple reciprocal mapping through ARA=1
# If ARA_space = Ωm/Ωde, then in time-frame: ARA_time = Ωde/Ωm
# The dark energy "fraction" in time-frame is the matter fraction in space-frame
ode_in_time_frame = Omega_m  # what DE "sees" as its own fraction
print(f"\n  Approach 1: Simple flip")
print(f"    Ωde(time-frame) = Ωm(space-frame) = {Omega_m:.4f}")
print(f"    1/φ² = {INV_PHI_2:.4f}")
print(f"    Δ = {abs(Omega_m - INV_PHI_2):.4f} = {abs(Omega_m-INV_PHI_2)/INV_PHI_2*100:.1f}%")
print(f"    CLOSER! But still {abs(Omega_m-INV_PHI_2)/INV_PHI_2*100:.1f}% off")

# Approach 2: The coupler (DM) modifies the flip
# In a three-system, the coupler fraction IS the π-leak
# Effective flip: Ωm_eff = Ωb (baryonic only, the 'true' matter)
# Then DM is the coupler sitting between the frames
print(f"\n  Approach 2: DM is the coupler — true matter = baryonic only")
print(f"    Ωb = {Omega_b:.4f}")
print(f"    Ωde + Ωb = {Omega_de + Omega_b:.4f}")
print(f"    Ωdm as coupler fraction: {Omega_dm/(Omega_de+Omega_b+Omega_dm):.4f}")
print(f"    1-1/φ² = {1-INV_PHI_2:.4f}")

# Approach 3: The ARA midline correction
# In the framework, the midline shifts predictions for non-engine systems
# The universe's ARA_time = 2.175, which has a midline
def ara_midline_simple(ara):
    """Simplified camshaft midline."""
    pd = abs(math.log(abs(ara)) / math.log(PHI)) if ara > 0 else 0
    zone = INV_PHI
    if pd <= zone:
        return 1.0
    if pd >= 1.0:
        inv_offset = 1.0 / max(0.01, ara) - 1.0
        return 1.0 + inv_offset
    ramp_width = INV_PHI_2
    t = (pd - zone) / ramp_width
    inv_offset = 1.0 / max(0.01, ara) - 1.0
    return 1.0 + inv_offset * t * t

mid_space = ara_midline_simple(ARA_space)
mid_time = ara_midline_simple(ARA_time)
print(f"\n  Approach 3: Midline correction")
print(f"    Midline(ARA_space={ARA_space:.4f}) = {mid_space:.4f}")
print(f"    Midline(ARA_time={ARA_time:.4f})  = {mid_time:.4f}")
print(f"    Ωde × midline_space = {Omega_de * mid_space:.4f}")
print(f"    Ωm × midline_time  = {Omega_m * mid_time:.4f}")

# Approach 4: The stretch factor
# In our solar prediction, ARA-circle stretch = 1 + ARA/φ × 1/φ⁵
# What if the cosmic 10% miss IS the stretch factor?
stretch_space = 1 + ARA_space/PHI * INV_PHI**5
stretch_time = 1 + ARA_time/PHI * INV_PHI**5
print(f"\n  Approach 4: ARA-circle stretch")
print(f"    stretch(ARA_space) = {stretch_space:.6f}")
print(f"    stretch(ARA_time)  = {stretch_time:.6f}")
print(f"    (1-1/φ²) × stretch_time = {(1-INV_PHI_2) * stretch_time:.4f}")
print(f"    Observed Ωde = {Omega_de:.4f}")
print(f"    Δ = {abs(Omega_de - (1-INV_PHI_2)*stretch_time):.4f} = {abs(Omega_de-(1-INV_PHI_2)*stretch_time)/Omega_de*100:.1f}%")

# Approach 5: Pipe geometry — 2φ down, φ up
# The dark sector communicates through a pipe with asymmetric capacity
print(f"\n  Approach 5: Pipe geometry (2φ/φ asymmetry)")
print(f"    Pipe down capacity: 2φ = {2*PHI:.4f}")
print(f"    Pipe up capacity:   φ  = {PHI:.4f}")
print(f"    Ratio: 2φ/φ = 2.0 (always)")
print(f"    If Ωm goes through pipe UP to become Ωde:")
print(f"    Ωm × 2φ = {Omega_m * 2 * PHI:.4f}")
print(f"    Ωm × φ² = {Omega_m * PHI**2:.4f}")
print(f"    Observed Ωde = {Omega_de:.4f}")
print(f"    Δ(Ωm×φ², Ωde) = {abs(Omega_m * PHI**2 - Omega_de):.4f} = {abs(Omega_m*PHI**2-Omega_de)/Omega_de*100:.1f}%")

# Whoa — Ωm × φ² = 0.315 × 2.618 = 0.825... not great
# But Ωm × 2φ = 0.315 × 3.236 = 1.019...
# What about the inverse: Ωde / φ² = 0.685 / 2.618 = 0.262
print(f"    Ωde / φ² = {Omega_de / PHI**2:.4f}")
print(f"    Ωdm = {Omega_dm:.4f}")
print(f"    Δ(Ωde/φ², Ωdm) = {abs(Omega_de/PHI**2 - Omega_dm):.4f} = {abs(Omega_de/PHI**2-Omega_dm)/Omega_dm*100:.1f}%")


# ════════════════════════════════════════════════════════════════
# PART 6: DM AS THE SHADOW OF DE THROUGH φ² PIPE
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  PART 6: Dark Matter = Dark Energy / φ²")
print(f"{'═' * 90}")

print(f"\n  ★ KEY FINDING: Ωde / φ² = {Omega_de / PHI**2:.4f} vs Ωdm = {Omega_dm:.4f}")
print(f"  Δ = {abs(Omega_de/PHI**2 - Omega_dm):.4f} ({abs(Omega_de/PHI**2-Omega_dm)/Omega_dm*100:.1f}%)")
print(f"  This is within {abs(Omega_de/PHI**2-Omega_dm)/Omega_dm*100:.1f}% — a NEAR MATCH")

print(f"\n  Interpretation:")
print(f"  Dark matter IS dark energy's shadow through the φ² horizontal coupler.")
print(f"  In the three-circle architecture:")
print(f"    - φ² is the horizontal coupling constant")
print(f"    - Dark energy (time-frame engine) couples down by φ² to produce")
print(f"      dark matter (the gravitational shadow visible in space-frame)")
print(f"    - Ωdm = Ωde / φ²")

# Check the full decomposition
print(f"\n  Full cosmic inventory as φ-chain:")
print(f"    Ωde = {Omega_de:.4f}")
print(f"    Ωdm = Ωde/φ² = {Omega_de/PHI**2:.4f} (observed: {Omega_dm})")
print(f"    Ωb  = Ωdm/φ² = {Omega_de/PHI**4:.4f} (observed: {Omega_b})")
print(f"                   = Ωde/φ⁴")

# Wait... Ωde/φ⁴ = 0.685/6.854 = 0.0999 vs Ωb = 0.049
print(f"    Hmm: Ωde/φ⁴ = {Omega_de/PHI**4:.4f} ≠ Ωb = {Omega_b:.4f}")
print(f"    So the chain breaks at baryonic matter")

# Try: Ωdm/φ³ for baryonic?
print(f"\n  Alternative chains:")
print(f"    Ωdm/φ³ = {Omega_dm/PHI**3:.4f} vs Ωb = {Omega_b:.4f} — Δ = {abs(Omega_dm/PHI**3-Omega_b):.4f}")
print(f"    Ωdm/φ  = {Omega_dm/PHI:.4f} vs Ωr = {Omega_r:.5f} — NO")
print(f"    Ωdm × Ωb/Ωde = {Omega_dm * Omega_b / Omega_de:.5f}")

# More promising: DM as geometric mean?
gm = math.sqrt(Omega_de * Omega_b)
print(f"\n  Geometric mean test:")
print(f"    √(Ωde × Ωb) = {gm:.4f}")
print(f"    Ωdm = {Omega_dm:.4f}")
print(f"    Δ = {abs(gm - Omega_dm):.4f} ({abs(gm-Omega_dm)/Omega_dm*100:.1f}%)")

# Geometric mean of DE and baryonic = 0.183 vs 0.266... not great
# But what about: DM = DE × (Ωb/Ωde)^(1/φ) ?
# i.e., DM is DE scaled by the baryon fraction raised to 1/φ
scaled = Omega_de * (Omega_b/Omega_de)**(1/PHI)
print(f"    Ωde × (Ωb/Ωde)^(1/φ) = {scaled:.4f}")
print(f"    Δ = {abs(scaled - Omega_dm):.4f} ({abs(scaled-Omega_dm)/Omega_dm*100:.1f}%)")

# The cleanest relationship so far: Ωdm ≈ Ωde/φ²
# Let's test: if this is exact, what would Ωde need to be?
ode_needed = Omega_dm * PHI**2
print(f"\n  If Ωdm = Ωde/φ² exactly:")
print(f"    Required Ωde = Ωdm × φ² = {ode_needed:.4f}")
print(f"    Then Ωm = 1 - Ωde = {1-ode_needed:.4f}")
print(f"    And Ωb = Ωm - Ωdm = {1-ode_needed-Omega_dm:.4f}")
print(f"    Observed Ωb = {Omega_b:.4f}")
print(f"    Δ = {abs((1-ode_needed-Omega_dm) - Omega_b):.4f}")

# The reverse: if Ωde is exact and Ωdm = Ωde/φ²
odm_predicted = Omega_de / PHI**2
ob_predicted = 1 - Omega_de - odm_predicted
print(f"\n  If Ωde = 0.685 (Planck) and Ωdm = Ωde/φ²:")
print(f"    Predicted Ωdm = {odm_predicted:.4f} (observed: {Omega_dm}, Δ = {abs(odm_predicted-Omega_dm)/Omega_dm*100:.1f}%)")
print(f"    Predicted Ωb  = {ob_predicted:.4f} (observed: {Omega_b}, Δ = {abs(ob_predicted-Omega_b)/Omega_b*100:.1f}%)")


# ════════════════════════════════════════════════════════════════
# PART 7: THE COMPLETE PICTURE — φ-Ladder of Cosmic Components
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  PART 7: Testing Multiple Decomposition Hypotheses")
print(f"{'═' * 90}")

# Test: each cosmic component as φ-power of something fundamental
print(f"\n  φ-ladder hypothesis: Ω_i = Ω₀ × φ^(-n) for some seed Ω₀")
print(f"  Starting from Ωde = {Omega_de}:")
print()

for n in range(0, 8):
    val = Omega_de * PHI**(-n)
    # Find what observed quantity this is closest to
    obs = {"Ωde": Omega_de, "Ωdm": Omega_dm, "Ωb": Omega_b, "Ωr": Omega_r}
    closest = min(obs.items(), key=lambda x: abs(x[1] - val))
    pct = abs(val - closest[1]) / closest[1] * 100 if closest[1] > 0 else 999
    marker = " ← ★ MATCH" if pct < 5 else (" ← near" if pct < 15 else "")
    print(f"    Ωde/φ^{n} = {val:.5f} ≈ {closest[0]} = {closest[1]:.5f} (Δ = {pct:.1f}%){marker}")

# Alternative: start from 1/φ chain
print(f"\n  Alternative: powers of 1/φ² from Ωde:")
for n in range(0, 5):
    val = Omega_de * INV_PHI_2**n
    obs = {"Ωde": Omega_de, "Ωdm": Omega_dm, "Ωb": Omega_b, "Ωr": Omega_r}
    closest = min(obs.items(), key=lambda x: abs(x[1] - val))
    pct = abs(val - closest[1]) / closest[1] * 100 if closest[1] > 0 else 999
    marker = " ← ★" if pct < 5 else ""
    print(f"    Ωde × (1/φ²)^{n} = {val:.6f} ≈ {closest[0]} = {closest[1]:.6f} (Δ = {pct:.1f}%){marker}")


# ════════════════════════════════════════════════════════════════
# PART 8: HUBBLE TENSION THROUGH THE FLIP
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  PART 8: Hubble Tension — A φ-Frame Mismatch?")
print(f"{'═' * 90}")

print(f"\n  CMB measures H₀ in the SPACE-FRAME (looking back to matter era)")
print(f"  Local measurements measure H₀ in the TIME-FRAME (current epoch)")
print(f"  If there's a φ-correction between frames:")

# The ratio
ratio = H0_local / H0
print(f"\n    H_local/H_CMB = {ratio:.4f}")
print(f"    1 + 1/φ⁵ = {1 + INV_PHI**5:.4f}")
print(f"    Δ = {abs(ratio - (1 + INV_PHI**5)):.4f}")

# That's the ARA-circle stretch factor for ARA=φ!
print(f"\n  ★ WAIT: 1 + 1/φ⁵ = {1+INV_PHI**5:.4f} = ARA-circle stretch for ARA=φ")
print(f"    H_local/H_CMB - 1 = {ratio - 1:.4f}")
print(f"    1/φ⁵ = {INV_PHI**5:.4f}")
print(f"    Δ = {abs((ratio-1) - INV_PHI**5):.4f} ({abs((ratio-1)-INV_PHI**5)/INV_PHI**5*100:.1f}% off)")

# Other φ-power corrections
print(f"\n  Other φ-power corrections:")
for n in range(2, 8):
    corr = 1 + PHI**(-n)
    h_pred = H0 * corr
    delta = abs(h_pred - H0_local)
    pct = delta / (H0_local - H0) * 100
    marker = " ★" if abs(h_pred - H0_local) < 1.5 else ""
    print(f"    H₀ × (1+1/φ^{n}) = {H0} × {corr:.5f} = {h_pred:.1f} (Δ from local: {delta:.1f}){marker}")

# stretch factor from current ARA
stretch_now = 1 + ARA_space/PHI * INV_PHI**5
h_stretched = H0 * stretch_now
print(f"\n  ARA-circle stretch with ARA_space = {ARA_space:.4f}:")
print(f"    Factor = {stretch_now:.6f}")
print(f"    H₀ × factor = {h_stretched:.1f}")
print(f"    Δ from local = {abs(h_stretched - H0_local):.1f}")


# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  SUMMARY — The Dark Flip")
print(f"{'═' * 90}")

print(f"""
  FRAME ANALYSIS:
    Space-frame ARA = {ARA_space:.4f} (consumer)
    Time-frame ARA  = {ARA_time:.4f} (engine)
    The universe is barely past the ARA=1 transition
    ({abs(math.log(ARA_space)/math.log(PHI)):.3f} φ-rungs into consumer territory)

  ★ BEST FINDING: Ωdm ≈ Ωde / φ²
    Predicted: {Omega_de/PHI**2:.4f}
    Observed:  {Omega_dm}
    Match: {100-abs(Omega_de/PHI**2-Omega_dm)/Omega_dm*100:.1f}% ({abs(Omega_de/PHI**2-Omega_dm)/Omega_dm*100:.1f}% off)

    Dark matter IS dark energy's φ²-coupled shadow.
    The horizontal coupler (φ²) translates between frames.
    Time-dominant energy → φ² pipe → gravitational shadow in space.

  HUBBLE TENSION:
    H_local/H_CMB = {ratio:.4f}
    Closest φ-match: 1+1/φ⁵ = {1+INV_PHI**5:.4f} (Δ = {abs(ratio-(1+INV_PHI**5)):.4f})
    This is the ARA-circle stretch factor — the same correction we use
    for solar predictions! The CMB and local ladder may measure from
    different sides of the frame flip.

  WHAT STILL MISSES:
    Ωde = 1-1/φ² was 10% off — the flip doesn't fix this directly.
    The chain Ωde → Ωdm/φ² works, but Ωdm → Ωb chain is broken
    (Ωdm/φ³ = {Omega_dm/PHI**3:.4f} vs Ωb = {Omega_b}, which is {abs(Omega_dm/PHI**3-Omega_b)/Omega_b*100:.1f}% off).
    The cosmic inventory is NOT a clean φ-power ladder from a single seed.
""")
print("=" * 90)
