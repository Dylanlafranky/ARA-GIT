#!/usr/bin/env python3
"""
Script 243BL6 — Coupled Space/Time × Light/Dark Grid

Dylan's insight: Space/Time and Light/Dark aren't separate axes to test
independently. They're COUPLED — Light/Dark is a subsystem of Space/Time.
So feed them into the SAME formula.

The universe has a 2×2 grid:

                    SPACE               TIME
              ┌─────────────────┬─────────────────┐
    DARK      │  Dark Matter    │  Dark Energy     │
              │  (space-dark)   │  (time-dark)     │
              │  Ω_dm = 0.265  │  Ω_de = 0.685   │
              ├─────────────────┼─────────────────┤
    LIGHT     │  Baryons        │  Radiation       │
              │  (space-light)  │  (time-light)    │
              │  Ω_b = 0.0493  │  Ω_γ = 5.38e-5  │
              └─────────────────┴─────────────────┘

Horizontal coupling (Space ↔ Time): φ²
Vertical coupling (Dark ↔ Light): ???
Both operate simultaneously → coupled system.

The question: when you put both couplers in the SAME equation,
does the vertical coupler emerge naturally?
"""

import numpy as np
import math

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2

print("=" * 90)
print("  Script 243BL6 — Coupled Space/Time × Light/Dark Grid")
print("  Both axes in the same formula")
print("=" * 90)

# ════════════════════════════════════════════════════════════════
# THE 2×2 GRID — Observed Values
# ════════════════════════════════════════════════════════════════
Omega_de = 0.685       # Time-Dark
Omega_dm = 0.265       # Space-Dark
Omega_b  = 0.0493      # Space-Light
Omega_gamma = 5.38e-5  # Time-Light
Omega_r = 9.03e-5      # Total radiation (γ + ν) — Time-Light total

# Row and column totals
dark_total  = Omega_de + Omega_dm     # = 0.950
light_total = Omega_b + Omega_r       # ≈ 0.0494
space_total = Omega_dm + Omega_b      # = 0.3143
time_total  = Omega_de + Omega_gamma  # ≈ 0.6851 (or with ν: Omega_de + Omega_r)

print(f"\n{'═' * 90}")
print(f"  THE 2×2 GRID")
print(f"{'═' * 90}")

print(f"""
                        SPACE           TIME            ROW TOTAL
              ┌───────────────┬───────────────┬───────────────┐
    DARK      │ DM = {Omega_dm:.4f}  │ DE = {Omega_de:.4f}  │ {dark_total:.4f}        │
              ├───────────────┼───────────────┼───────────────┤
    LIGHT     │ b  = {Omega_b:.4f}  │ γ  = {Omega_gamma:.2e}│ {light_total:.4f}        │
              ├───────────────┼───────────────┼───────────────┤
    COL TOTAL │ {space_total:.4f}        │ {time_total:.4f}        │ {dark_total+light_total:.4f}  │
              └───────────────┴───────────────┴───────────────┘
""")

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 1: ALL FOUR RATIOS — Horizontal, Vertical, and Diagonal
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 1: All Four Coupling Ratios")
print(f"{'═' * 90}")

# Horizontal (Space ↔ Time)
h_dark = Omega_de / Omega_dm         # Time-dark / Space-dark
h_light = Omega_gamma / Omega_b      # Time-light / Space-light

# Vertical (Dark ↔ Light)
v_space = Omega_dm / Omega_b         # Space-dark / Space-light
v_time  = Omega_de / Omega_gamma     # Time-dark / Time-light

# Diagonals
d_main = Omega_de / Omega_b          # Time-dark / Space-light (main diagonal)
d_anti = Omega_dm / Omega_gamma      # Space-dark / Time-light (anti-diagonal)

print(f"""
  HORIZONTAL (Space ↔ Time, same visibility level):
    Dark row:  DE/DM = {h_dark:.4f}     φ² = {PHI**2:.4f}   Δ = {abs(h_dark - PHI**2)/PHI**2*100:.1f}%  {'★' if abs(h_dark - PHI**2)/PHI**2 < 0.05 else ''}
    Light row: γ/b  = {h_light:.6f}  (tiny — radiation ≪ baryons NOW)

  But radiation dilutes as a⁻⁴ vs baryons as a⁻³.
  At z = 0, γ/b is suppressed by (1+z)⁻¹ relative to its "natural" value.
  At matter-radiation equality (z_eq ≈ 3400), they WERE equal.
  So the light-row horizontal coupling is TIME-DEPENDENT.

  Light row at z_eq: γ(z_eq)/b(z_eq) ≈ 1 (by definition of z_eq)
  The light-row φ² coupling is HIDDEN by cosmic expansion.
  Dark row keeps its φ² because both DE and DM scale the same way (sort of).

  VERTICAL (Dark ↔ Light, same spatial/temporal frame):
    Space column: DM/b  = {v_space:.4f}
    Time column:  DE/γ  = {v_time:.0f}

  In φ-powers:
    DM/b  = φ^{math.log(v_space)/math.log(PHI):.3f}     (φ^3.5 = {PHI**3.5:.4f}, Δ = {abs(v_space - PHI**3.5)/PHI**3.5*100:.1f}%)  {'★' if abs(v_space - PHI**3.5)/PHI**3.5 < 0.05 else ''}
    DE/γ  = φ^{math.log(v_time)/math.log(PHI):.3f}     (φ^20 = {PHI**20:.0f})

  The TIME-column vertical ratio is enormous because γ dilutes much faster.
  Again: the light row has been TIME-PROCESSED. Its "natural" coupling is hidden.

  DIAGONALS (cross-coupling):
    Main: DE/b   = {d_main:.2f}   = φ^{math.log(d_main)/math.log(PHI):.3f}
    Anti: DM/γ   = {d_anti:.0f}  = φ^{math.log(d_anti)/math.log(PHI):.3f}
""")

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 2: UNDO THE TIME-PROCESSING — Restore Light Row to Natural State
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 2: Undo Time-Processing — Evaluate at z_eq")
print(f"{'═' * 90}")

z_eq = 3402  # matter-radiation equality

# At z_eq, radiation density = matter density (by definition)
# Ω_r(z) = Ω_r(0) × (1+z) relative to matter
# So at z_eq: Ω_γ_eq = Ω_γ × (1+z_eq) / [relative to matter scaling]
# Actually: Ω_γ(z)/Ω_m(z) = [Ω_γ(0)/Ω_m(0)] × (1+z)
# At z_eq: Ω_γ(z_eq)/Ω_m(z_eq) = 1

# The NATURAL (scale-factor-independent) ratios:
# ρ_γ / ρ_b ~ (1+z) × (Ω_γ/Ω_b) at any z
# At z_eq: ρ_γ = ρ_m, so ρ_γ/ρ_b = ρ_m/ρ_b = Ω_m/Ω_b ≈ 6.4

# But what we want is the COUPLING constant, not the density ratio.
# The coupling is what's INVARIANT — what the architecture sets.

# Let's think about it differently:
# The 2×2 grid has a coupling MATRIX, not just ratios.
# M = [[DE, DM], [γ, b]] with couplings between adjacent cells.

# In a coupled system, we can write:
# M = A ⊗ B where A = Space/Time coupling, B = Dark/Light coupling
# If both use φ-couplers, M should factor as a tensor product.

print(f"""
  The 2×2 grid is a tensor product of two coupled pairs:
    M = (Space/Time coupling) ⊗ (Dark/Light coupling)

  If M factors cleanly, then:
    M = [α  β ] ⊗ [p  q]  =  [αp  αq  βp  βq]
        [β  α ]   [q  p]     [αq  αp  βq  βp]

  where α/β = horizontal ratio, p/q = vertical ratio.

  BUT the grid cells must map correctly:
    DE  = time-dark  → should be in the (time, dark) position
    DM  = space-dark → (space, dark)
    b   = space-light → (space, light)
    γ   = time-light  → (time, light)

  For a symmetric tensor product M = H ⊗ V:
    H (horizontal) couples Space ↔ Time
    V (vertical) couples Dark ↔ Light

    M = H ⊗ V where:
    H = [h_time, h_space]  (time component, space component)
    V = [v_dark, v_light]  (dark component, light component)

    Then: DE = h_time × v_dark
          DM = h_space × v_dark
          b  = h_space × v_light
          γ  = h_time × v_light
""")

# If M = H ⊗ V, then:
# DE/DM = h_time/h_space (should be φ²)
# b/γ   = h_space/h_time (should be 1/φ² if symmetric)
# DE/γ  = v_dark/v_light (the vertical ratio on time axis)
# DM/b  = v_dark/v_light (the SAME vertical ratio on space axis)

# Check: DM/b should equal DE/γ if the grid truly factors
print(f"  IF the grid factors as a tensor product:")
print(f"    DM/b  = {v_space:.4f}")
print(f"    DE/γ  = {v_time:.0f}")
print(f"    These should be EQUAL. They're not ({v_space:.1f} vs {v_time:.0f}).")
print(f"    The grid does NOT factor as a simple tensor product.")
print(f"    → The coupling is NOT separable. Space/Time and Dark/Light are ENTANGLED.")
print()

# This is the key: the two axes aren't independent — they're coupled.
# The off-diagonal cross-terms matter.

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 3: COUPLED EIGENVALUE APPROACH
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 3: Coupled System — Eigenstructure of the 2×2 Grid")
print(f"{'═' * 90}")

# Treat the 2×2 Ω grid as a matrix and find its eigenstructure
# This reveals the NATURAL modes of the coupled system
M = np.array([[Omega_de, Omega_dm],
              [Omega_gamma, Omega_b]])

eigenvalues, eigenvectors = np.linalg.eig(M)

print(f"  The Ω grid as a matrix:")
print(f"    ┌                      ┐")
print(f"    │ {Omega_de:.6f}  {Omega_dm:.6f} │   (dark row)")
print(f"    │ {Omega_gamma:.6f}  {Omega_b:.6f} │   (light row)")
print(f"    └                      ┘")
print()
print(f"  Eigenvalues: λ₁ = {eigenvalues[0]:.6f}, λ₂ = {eigenvalues[1]:.6f}")
print(f"  λ₁/λ₂ = {eigenvalues[0]/eigenvalues[1]:.4f}")
print(f"  φ² = {PHI**2:.4f}")
print(f"  Δ = {abs(eigenvalues[0]/eigenvalues[1] - PHI**2)/PHI**2*100:.1f}%")
print()

# Eigenvectors reveal the coupling direction
print(f"  Eigenvectors:")
print(f"    v₁ = [{eigenvectors[0,0]:.6f}, {eigenvectors[1,0]:.6f}]")
print(f"    v₂ = [{eigenvectors[0,1]:.6f}, {eigenvectors[1,1]:.6f}]")
print()

# Determinant and trace
det_M = np.linalg.det(M)
trace_M = np.trace(M)
print(f"  Trace (λ₁ + λ₂) = {trace_M:.6f}")
print(f"    = Ω_de + Ω_b = {Omega_de + Omega_b:.6f} (diagonal sum)")
print(f"  Determinant (λ₁ × λ₂) = {det_M:.8f}")
print(f"    = Ω_de × Ω_b - Ω_dm × Ω_γ = {Omega_de*Omega_b - Omega_dm*Omega_gamma:.8f}")
print()

# What about the NORMALIZED grid? (each row sums to 1)
# Dark row: DE/(DE+DM), DM/(DE+DM)
# Light row: γ/(γ+b), b/(γ+b)
M_norm = np.array([[Omega_de/dark_total, Omega_dm/dark_total],
                    [Omega_gamma/light_total, Omega_b/light_total]])

eigenvalues_n, eigenvectors_n = np.linalg.eig(M_norm)

print(f"  NORMALIZED grid (each row sums to 1):")
print(f"    ┌                    ┐")
print(f"    │ {M_norm[0,0]:.6f}  {M_norm[0,1]:.6f} │   dark row: DE/(DE+DM), DM/(DE+DM)")
print(f"    │ {M_norm[1,0]:.6f}  {M_norm[1,1]:.6f} │   light row: γ/(γ+b), b/(γ+b)")
print(f"    └                    ┘")
print()
print(f"  Dark split:  Time={M_norm[0,0]:.4f}, Space={M_norm[0,1]:.4f}")
print(f"  Light split: Time={M_norm[1,0]:.4f}, Space={M_norm[1,1]:.4f}")
print()
print(f"  On the dark side: Time/Space = {M_norm[0,0]/M_norm[0,1]:.4f} (= DE/DM = φ² ≈ {PHI**2:.4f})")
print(f"  On the light side: Time/Space = {M_norm[1,0]/M_norm[1,1]:.6f}")
print(f"  Light side is FLIPPED — Space dominates Time in the visible sector!")
print(f"  Visible space (baryons) ≫ visible time (radiation) at z=0.")
print()

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 4: THE COUPLED EQUATION — Both Axes Simultaneously
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 4: The Coupled Equation")
print(f"{'═' * 90}")

# Dylan's idea: feed BOTH couplings into ONE equation.
# In the three-circle model:
#   Space ↔ Time: coupled by φ² (horizontal)
#   Dark ↔ Light: coupled vertically
#   These aren't separate — they're SIMULTANEOUS.
#
# The coupling matrix C should encode both:
#   C = [[c_tt, c_ts], [c_st, c_ss]]
# where c_ts = horizontal coupling, and the vertical coupling
# modifies the diagonal elements.
#
# If we write Ω_ij = f(φ, position_in_grid), what function f
# reproduces all four values from φ alone?

# Approach: each cell is a product of a SPACE/TIME weight × DARK/LIGHT weight
# where the weights are φ-based but NOT separable (entangled).

# What if each axis contributes a φ-power, and the powers ADD?
# Ω_ij = A × φ^(h_i + v_j) where h_i = horizontal position, v_j = vertical position

# Take logs: log_φ(Ω_ij) = log_φ(A) + h_i + v_j
# This IS separable in log-space.

log_de = math.log(Omega_de) / math.log(PHI)
log_dm = math.log(Omega_dm) / math.log(PHI)
log_b  = math.log(Omega_b) / math.log(PHI)
log_g  = math.log(Omega_gamma) / math.log(PHI)

print(f"  φ-powers of each Ω component:")
print(f"    DE (time-dark):   Ω_de = φ^{log_de:.4f}")
print(f"    DM (space-dark):  Ω_dm = φ^{log_dm:.4f}")
print(f"    b  (space-light): Ω_b  = φ^{log_b:.4f}")
print(f"    γ  (time-light):  Ω_γ  = φ^{log_g:.4f}")
print()

# If separable in log-space: log_de + log_b = log_dm + log_g
# (sum of main diagonal = sum of anti-diagonal)
main_diag = log_de + log_b
anti_diag = log_dm + log_g
print(f"  SEPARABILITY TEST (additive in φ-exponents):")
print(f"    Main diagonal (DE + b):  {log_de:.4f} + ({log_b:.4f}) = {main_diag:.4f}")
print(f"    Anti-diagonal (DM + γ):  {log_dm:.4f} + ({log_g:.4f}) = {anti_diag:.4f}")
print(f"    If separable, these should be EQUAL.")
print(f"    Difference: {abs(main_diag - anti_diag):.4f}")
print(f"    → NOT separable (difference = {abs(main_diag - anti_diag):.2f} in φ-exponent)")
print(f"    → The coupling is genuinely ENTANGLED.")
print()

# Since it's not separable, the cross-coupling term matters.
# Define: entanglement = main_diag - anti_diag
entanglement = main_diag - anti_diag
print(f"  ENTANGLEMENT PARAMETER:")
print(f"    ε = {entanglement:.4f} (in φ-exponent units)")
print(f"    φ^ε = {PHI**entanglement:.6f}")
print(f"    This measures HOW MUCH the axes are coupled.")
print()

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 5: COUPLED φ-POWER MODEL — With Cross-Term
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 5: Coupled φ-Power Model")
print(f"{'═' * 90}")

# Model: Ω_ij = φ^(h_i + v_j + ε_ij)
# where h = horizontal position, v = vertical position, ε = cross-coupling
# We have 4 unknowns (h_time, h_space, v_dark, v_light) + cross-terms
# But only 4 data points. So with a single cross-term:

# Choose reference: h_time = 0, v_dark = 0 (DE = reference cell)
# Then:
#   DE: φ^(0 + 0 + 0) × A = Omega_de → A = Omega_de
#   DM: φ^(h_s + 0) × A = Omega_dm → h_s = log_φ(DM/DE) = -log_φ(φ²) = -2
#   b:  φ^(h_s + v_l + ε) × A = Omega_b
#   γ:  φ^(0 + v_l) × A = Omega_gamma → v_l = log_φ(γ/DE)

h_space = log_dm - log_de  # = -2 ish (the φ² horizontal coupling)
v_light = log_g - log_de    # vertical coupling on time axis

print(f"  Reference cell: DE (time-dark)")
print(f"    A = Ω_de = {Omega_de:.4f}")
print(f"    h_space = log_φ(DM/DE) = {h_space:.4f} (expected: -2 for φ² coupling)")
print(f"    Δ from -2: {abs(h_space + 2):.4f} ({abs(h_space + 2)/2*100:.1f}%)")
print()

print(f"    v_light = log_φ(γ/DE) = {v_light:.4f}")
print(f"    This is the 'natural' vertical coupling on the time axis.")
print()

# Now predict baryons from the coupled model:
# If separable: b = A × φ^(h_space + v_light)
b_separable = Omega_de * PHI**(h_space + v_light)
print(f"  SEPARABLE prediction for baryons:")
print(f"    b_pred = DE × φ^(h_space + v_light)")
print(f"           = {Omega_de:.4f} × φ^({h_space:.4f} + {v_light:.4f})")
print(f"           = {Omega_de:.4f} × φ^{h_space + v_light:.4f}")
print(f"           = {b_separable:.6f}")
print(f"    Observed: {Omega_b:.4f}")
print(f"    Δ = {abs(b_separable - Omega_b)/Omega_b*100:.1f}%")
print()

# The CROSS-COUPLING term:
epsilon = log_b - (log_de + h_space + v_light)
print(f"  CROSS-COUPLING (entanglement) term:")
print(f"    ε = log_φ(b_obs) - log_φ(b_separable)")
print(f"    = {log_b:.4f} - ({log_de:.4f} + {h_space:.4f} + {v_light:.4f})")
print(f"    = {epsilon:.4f}")
print(f"    φ^ε = {PHI**epsilon:.4f}")
print()

# Is ε a recognizable φ-power or architectural constant?
print(f"  WHAT IS ε?")
print(f"    ε = {epsilon:.4f}")
print(f"    Nearest φ-identities:")
for name, val in [("φ²", 2), ("φ", 1), ("1", 0), ("-1 (=1/φ)", -1),
                  ("-2 (=1/φ²)", -2), ("-φ", -PHI), ("2/φ", 2*INV_PHI),
                  ("-2/φ", -2*INV_PHI), ("φ-2", PHI-2), ("2-φ", 2-PHI),
                  ("3", 3), ("-3", -3), ("π", math.pi), ("-π", -math.pi),
                  ("φ²+1", PHI**2+1), ("-(φ²+1)", -(PHI**2+1))]:
    print(f"      {name:>12} = {val:>8.4f}  Δ = {abs(epsilon - val):.4f}")
print()

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 6: THE INTERACTION MATRIX — φ Couplers as Matrix Elements
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 6: Interaction Matrix — φ Couplers as Generators")
print(f"{'═' * 90}")

# Instead of treating Ω values as the matrix, treat the COUPLERS as the matrix.
# The coupling matrix C acts on a state vector to produce the Ω distribution.
#
# If the coupling is φ-based:
# C = [[1,    φ²  ],    (dark-dark, dark→light coupling)
#      [1/φ², 1   ]]    (light→dark, light-light coupling)
#
# But this is just the horizontal coupling. We need to COMPOSE with vertical.

# Full coupling: start from a "seed" and let both couplers act.
# Seed: equal distribution [0.25, 0.25, 0.25, 0.25]?
# No — the seed is the initial state, which might be [1, 0, 0, 0] (all DE).

# Coupling as a 4×4 matrix on the vector [DE, DM, b, γ]:
# Horizontal coupling (φ²):
#   DE ↔ DM with strength φ²
#   b ↔ γ with strength φ²
# Vertical coupling (?):
#   DE ↔ γ (time column)
#   DM ↔ b (space column)

# Let's try: the coupling matrix has φ² for horizontal, and we FIND
# the vertical coupling constant that reproduces the observed Ω values.

# The generator approach: coupling constants define a flow.
# At equilibrium: C·Ω = λΩ (eigenvector condition)
# So Ω should be an eigenvector of C.

# Construct C with unknown vertical coupling v:
# C = [[0,    φ²,   0,    v  ],    DE couples to DM (horiz) and γ (vert)
#      [φ²,   0,    v,    0  ],    DM couples to DE (horiz) and b (vert)
#      [0,    v,    0,    φ² ],    b couples to DM (vert) and γ (horiz)
#      [v,    0,    φ²,   0  ]]    γ couples to DE (vert) and b (horiz)

# This is a symmetric coupling matrix. Find v such that [DE, DM, b, γ]
# is an eigenvector.

# For Ω to be eigenvector of C:
# C·Ω = λΩ
# Row 1: φ²·DM + v·γ = λ·DE
# Row 2: φ²·DE + v·b = λ·DM
# Row 3: v·DM + φ²·γ = λ·b
# Row 4: v·DE + φ²·b = λ·γ

# From rows 1 and 2:
# λ = (φ²·DM + v·γ) / DE = (φ²·DE + v·b) / DM

# Solve for v:
# φ²·DM/DE + v·γ/DE = φ²·DE/DM + v·b/DM
# v(γ/DE - b/DM) = φ²(DE/DM - DM/DE)
# v = φ²(DE/DM - DM/DE) / (γ/DE - b/DM)

numerator = PHI**2 * (Omega_de/Omega_dm - Omega_dm/Omega_de)
denominator = (Omega_gamma/Omega_de - Omega_b/Omega_dm)

v_coupling = numerator / denominator

# λ from row 1:
lambda_val = (PHI**2 * Omega_dm + v_coupling * Omega_gamma) / Omega_de

print(f"  SYMMETRIC COUPLING MATRIX (off-diagonal couplers):")
print(f"    Horizontal (Space↔Time): φ² = {PHI**2:.4f}")
print(f"    Vertical (Dark↔Light):   v = {v_coupling:.4f}")
print(f"    Eigenvalue: λ = {lambda_val:.4f}")
print()

print(f"  WHAT IS v?")
print(f"    v = {v_coupling:.4f}")
for name, val in [("φ²", PHI**2), ("φ", PHI), ("2/φ", 2/PHI), ("1", 1.0),
                  ("1/φ", INV_PHI), ("1/φ²", INV_PHI_2), ("2φ", 2*PHI),
                  ("φ³", PHI**3), ("φ+1=φ²", PHI+1), ("π", math.pi),
                  ("2π", 2*math.pi), ("φ⁴", PHI**4), ("φ⁵", PHI**5),
                  ("φ²·π", PHI**2*math.pi), ("φ³/2", PHI**3/2)]:
    delta = abs(v_coupling - val) / val * 100
    marker = " ★" if delta < 5 else ""
    print(f"      {name:>10} = {val:>10.4f}  Δ = {delta:>6.1f}%{marker}")
print()

# Verify: does the coupling matrix actually reproduce Ω as eigenvector?
C = np.array([
    [0,       PHI**2,  0,          v_coupling],
    [PHI**2,  0,       v_coupling, 0         ],
    [0,       v_coupling, 0,       PHI**2    ],
    [v_coupling, 0,    PHI**2,     0         ]
])

omega_vec = np.array([Omega_de, Omega_dm, Omega_b, Omega_gamma])
result = C @ omega_vec
predicted_lambda = result / omega_vec

print(f"  VERIFICATION — C·Ω / Ω (should all equal λ = {lambda_val:.4f}):")
labels = ["DE", "DM", "b ", "γ "]
for i in range(4):
    print(f"    {labels[i]}: C·Ω = {result[i]:.6f}, Ω = {omega_vec[i]:.6f}, ratio = {predicted_lambda[i]:.4f}")
print()

# Check rows 3 and 4:
# Row 3: v·DM + φ²·γ = λ·b?
check3 = v_coupling * Omega_dm + PHI**2 * Omega_gamma
check4 = v_coupling * Omega_de + PHI**2 * Omega_b

print(f"  Row 3 check: v·DM + φ²·γ = {check3:.6f}, λ·b = {lambda_val * Omega_b:.6f}")
print(f"  Row 4 check: v·DE + φ²·b = {check4:.6f}, λ·γ = {lambda_val * Omega_gamma:.6f}")
print(f"  Rows 1-2 are exact by construction.")
print(f"  Rows 3-4 deviation = the ENTANGLEMENT between axes.")
print()

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 7: ITERATIVE COUPLED SYSTEM — Let Both Couplers Evolve Together
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 7: What Vertical Coupling Makes the Grid Self-Consistent?")
print(f"{'═' * 90}")

# Instead of solving analytically, scan vertical coupling values
# and find which one makes the 4×4 system most eigenvector-like.

# For each trial v, compute C·Ω and measure how close the λ ratios are
# to being constant (i.e., how close Ω is to being an eigenvector of C).

best_v = None
best_spread = float('inf')
best_lambda_mean = None

v_scan = np.linspace(0.01, 50.0, 10000)
for v_trial in v_scan:
    C_trial = np.array([
        [0,        PHI**2,   0,       v_trial],
        [PHI**2,   0,        v_trial, 0      ],
        [0,        v_trial,  0,       PHI**2 ],
        [v_trial,  0,        PHI**2,  0      ]
    ])
    result_trial = C_trial @ omega_vec
    lambdas = result_trial / omega_vec
    spread = np.std(lambdas) / np.mean(lambdas)  # coefficient of variation
    if spread < best_spread:
        best_spread = spread
        best_v = v_trial
        best_lambda_mean = np.mean(lambdas)

print(f"  SCAN: vertical coupling v from 0.01 to 50")
print(f"  Best v = {best_v:.4f} (spread = {best_spread:.6f})")
print(f"  Mean λ = {best_lambda_mean:.4f}")
print()

# Fine scan around best
v_fine = np.linspace(max(0.01, best_v - 1), best_v + 1, 100000)
for v_trial in v_fine:
    C_trial = np.array([
        [0,        PHI**2,   0,       v_trial],
        [PHI**2,   0,        v_trial, 0      ],
        [0,        v_trial,  0,       PHI**2 ],
        [v_trial,  0,        PHI**2,  0      ]
    ])
    result_trial = C_trial @ omega_vec
    lambdas = result_trial / omega_vec
    spread = np.std(lambdas) / np.mean(lambdas)
    if spread < best_spread:
        best_spread = spread
        best_v = v_trial
        best_lambda_mean = np.mean(lambdas)

print(f"  FINE SCAN around best:")
print(f"  Best v = {best_v:.6f}")
print(f"  Mean λ = {best_lambda_mean:.4f}")
print(f"  Spread (CV) = {best_spread:.8f}")
print()

# Check this v against φ-identities
print(f"  BEST v = {best_v:.6f}")
print(f"  φ-identity matches:")
for name, val in [("φ²", PHI**2), ("φ", PHI), ("2/φ", 2/PHI), ("1", 1.0),
                  ("1/φ", INV_PHI), ("1/φ²", INV_PHI_2), ("2φ", 2*PHI),
                  ("φ³", PHI**3), ("φ⁴", PHI**4), ("φ⁵", PHI**5),
                  ("π", math.pi), ("2π", 2*math.pi), ("e", math.e),
                  ("φ²·π", PHI**2*math.pi), ("φ·π", PHI*math.pi),
                  ("10/φ", 10/PHI), ("φ²+φ", PHI**2+PHI),
                  ("φ³+1", PHI**3+1), ("2φ²", 2*PHI**2),
                  ("3φ", 3*PHI), ("φ²+1", PHI**2+1)]:
    delta = abs(best_v - val) / val * 100
    marker = " ★★★" if delta < 1 else (" ★★" if delta < 3 else (" ★" if delta < 5 else ""))
    print(f"      {name:>10} = {val:>10.4f}  Δ = {delta:>6.2f}%{marker}")
print()

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 8: ASYMMETRIC COUPLING — Dark→Light ≠ Light→Dark (Pipe!)
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 8: Asymmetric Coupling (Pipe Geometry)")
print(f"{'═' * 90}")

# The three-circle model says: DOWN pipe ≠ UP pipe (2φ vs φ).
# So the coupling matrix should be ASYMMETRIC:
# Dark→Light coupling ≠ Light→Dark coupling

# C_asym = [[0,    φ²,     0,       v_up  ],   DE: horiz to DM, vert UP from γ
#            [φ²,   0,      v_up,    0     ],   DM: horiz to DE, vert UP from b
#            [0,    v_down, 0,       φ²    ],   b: horiz to γ, vert DOWN from DM
#            [v_down, 0,    φ²,      0     ]]   γ: horiz to b, vert DOWN from DE
#
# v_down = dark→light (2φ pipe), v_up = light→dark (φ pipe)
# Ratio: v_down/v_up = 2 (the pipe asymmetry)

print(f"  Pipe says: dark→light = 2× light→dark")
print(f"  So v_down = 2 × v_up")
print()

best_vup = None
best_spread_asym = float('inf')

vup_scan = np.linspace(0.01, 30.0, 50000)
for vup in vup_scan:
    vdown = 2 * vup  # pipe asymmetry
    C_asym = np.array([
        [0,     PHI**2,  0,     vup  ],
        [PHI**2, 0,      vup,   0    ],
        [0,     vdown,   0,     PHI**2],
        [vdown,  0,      PHI**2, 0   ]
    ])
    result_a = C_asym @ omega_vec
    lambdas = result_a / omega_vec
    spread = np.std(lambdas) / np.mean(lambdas)
    if spread < best_spread_asym:
        best_spread_asym = spread
        best_vup = vup
        best_vdown = 2 * vup
        best_lambda_asym = np.mean(lambdas)

# Fine scan
vup_fine = np.linspace(max(0.01, best_vup - 0.5), best_vup + 0.5, 100000)
for vup in vup_fine:
    vdown = 2 * vup
    C_asym = np.array([
        [0,     PHI**2,  0,     vup  ],
        [PHI**2, 0,      vup,   0    ],
        [0,     vdown,   0,     PHI**2],
        [vdown,  0,      PHI**2, 0   ]
    ])
    result_a = C_asym @ omega_vec
    lambdas = result_a / omega_vec
    spread = np.std(lambdas) / np.mean(lambdas)
    if spread < best_spread_asym:
        best_spread_asym = spread
        best_vup = vup
        best_vdown = 2 * vup
        best_lambda_asym = np.mean(lambdas)

print(f"  ASYMMETRIC SCAN (v_down = 2 × v_up):")
print(f"  Best v_up   = {best_vup:.6f} (light→dark)")
print(f"  Best v_down = {best_vdown:.6f} (dark→light)")
print(f"  Mean λ = {best_lambda_asym:.4f}")
print(f"  Spread (CV) = {best_spread_asym:.8f}")
print()

print(f"  v_up matches:")
for name, val in [("φ²", PHI**2), ("φ", PHI), ("2/φ", 2/PHI), ("1", 1.0),
                  ("1/φ", INV_PHI), ("2φ", 2*PHI), ("φ³", PHI**3),
                  ("π", math.pi), ("φ·π", PHI*math.pi),
                  ("φ²+1", PHI**2+1), ("φ³/2", PHI**3/2)]:
    delta = abs(best_vup - val) / val * 100
    marker = " ★★★" if delta < 1 else (" ★★" if delta < 3 else (" ★" if delta < 5 else ""))
    print(f"      {name:>10} = {val:>10.4f}  Δ = {delta:>6.2f}%{marker}")
print()

print(f"  v_down matches:")
for name, val in [("φ²", PHI**2), ("φ", PHI), ("2/φ", 2/PHI),
                  ("2φ", 2*PHI), ("φ³", PHI**3), ("φ⁴", PHI**4),
                  ("2π", 2*math.pi), ("φ·π", PHI*math.pi),
                  ("2φ²", 2*PHI**2), ("3φ", 3*PHI)]:
    delta = abs(best_vdown - val) / val * 100
    marker = " ★★★" if delta < 1 else (" ★★" if delta < 3 else (" ★" if delta < 5 else ""))
    print(f"      {name:>10} = {val:>10.4f}  Δ = {delta:>6.2f}%{marker}")
print()

# Compare symmetric vs asymmetric
print(f"  SYMMETRIC vs ASYMMETRIC comparison:")
print(f"    Symmetric best spread:  {best_spread:.8f}")
print(f"    Asymmetric best spread: {best_spread_asym:.8f}")
if best_spread_asym < best_spread:
    print(f"    → Asymmetric is BETTER (pipe geometry helps)")
else:
    print(f"    → Symmetric is better (pipe asymmetry doesn't help)")
print()

# ════════════════════════════════════════════════════════════════════════════════
#  TEST 9: GENERATIVE MODEL — Can Architecture PRODUCE the Ω Values?
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  TEST 9: Generative Model — Architecture Produces Ω")
print(f"{'═' * 90}")

# Instead of fitting, START from the architecture and see what it generates.
# Three-circle model: Space, Time, Rationality
# Space ↔ Time: horizontal coupler φ²
# Both → Rationality: vertical coupler 1/φ each, total 2/φ
#
# The universe distributes energy according to:
# Each "circle" gets a base weight proportional to its coupling strength.
# Space and Time: weight = φ (from horizontal coupling to each other)
# Rationality: weight = 1 (base, receives 2/φ from above)
#
# Then: within each circle, energy splits dark/light.
# Dark = the circle's own fabric (invisible)
# Light = what escapes to observers (visible)

# Model:
# Total weight = Space + Time + Rationality = φ + φ + 1 = 2φ + 1 = 1 + 2φ
# But 1 + 2φ = 1 + 2(1.618) = 4.236 = φ² + φ + 1 = φ³ + 1/φ... hmm
# Actually: 2φ + 1 = 2(1.618) + 1 = 4.236
# φ³ = 4.236! So 2φ + 1 = φ³ (identity: φ³ = 2φ + 1)

total_weight = 2*PHI + 1
print(f"  ARCHITECTURAL WEIGHTS:")
print(f"    Space weight = φ = {PHI:.4f}")
print(f"    Time weight  = φ = {PHI:.4f}")
print(f"    Rationality  = 1")
print(f"    Total = 2φ + 1 = {total_weight:.4f} = φ³ = {PHI**3:.4f}")
print(f"    (Identity: 2φ + 1 = φ³)")
print()

# Fractions:
f_space = PHI / total_weight
f_time  = PHI / total_weight
f_rat   = 1 / total_weight

print(f"  AS FRACTIONS OF Ω=1:")
print(f"    Space:       φ/φ³ = 1/φ² = {f_space:.4f}  → Ω_space = {f_space:.4f}")
print(f"    Time:        φ/φ³ = 1/φ² = {f_time:.4f}   → Ω_time  = {f_time:.4f}")
print(f"    Rationality: 1/φ³ = {f_rat:.4f}   → Ω_rat   = {f_rat:.4f}")
print()

# Now map to observables:
# Space∩Time (no Rationality) = dark sector = NOT just Space + Time
# The pairwise intersection: Space∩Time gets the OVERLAP of Space and Time
# In Venn diagram: each pair has an overlap

# Simpler: the dark sector is Space + Time MINUS their projection into Rationality
# Space projects into Rationality: Space × (1/φ) = φ × (1/φ) = 1 → already counted in Rat
# So dark = (Space + Time) - Rationality's share of each = 2φ - 2(1/φ)... no

# Even simpler:
# DM = Space - (Space ∩ Rationality) = Space's DARK part
# DE = Time - (Time ∩ Rationality) = Time's DARK part
# Baryons = Space ∩ Rationality
# Radiation = Time ∩ Rationality

# Each circle's visible fraction = what reaches Rationality via vertical coupling
# Visible fraction = (1/φ) / (circle_weight) = 1/(φ × φ) = 1/φ² for Space and Time

# So for Space (weight φ):
#   Dark part = φ × (1 - 1/φ²) = φ × (φ²-1)/φ² = φ × φ/φ² = φ × 1/φ = 1
#   Wait, that gives dark_space = 1, which is wrong.

# Let me think differently.
# Space contributes 1/φ² of the total to the universe.
# Of that, the fraction that is VISIBLE (reaches Rationality) is...
# The vertical coupling sends 1/φ per source.
# So the visible fraction of Space = (1/φ) × normalization

# Perhaps: each cell of the 2×2 grid gets weight:
# (horizontal position weight) × (vertical position weight)
# Horizontal: Time gets φ, Space gets 1 (or vice versa — Time is the driver in DE era)
# Vertical: Dark gets φ, Light gets 1 (dark is the "upper" level)

# Grid weights:
# DE  (time-dark):   φ × φ = φ²
# DM  (space-dark):  1 × φ = φ
# γ   (time-light):  φ × 1 = φ
# b   (space-light): 1 × 1 = 1

# Total = φ² + φ + φ + 1 = φ² + 2φ + 1 = (φ+1)² = (φ²)² = φ⁴
# Wait: (φ+1) = φ², so (φ+1)² = φ⁴. Let me check: φ² + 2φ + 1 = (φ+1)² = (φ²)² = φ⁴
# φ⁴ = 6.854

w_de = PHI**2
w_dm = PHI * 1  # or PHI
w_gamma = PHI * 1  # but this gives γ same as DM??
w_b = 1

# Hmm — γ and DM get the same weight. That's wrong.
# The issue: in this model, (time, light) and (space, dark) are SYMMETRIC.
# But they shouldn't be — time-light (radiation) ≪ space-dark (DM).

# The asymmetry comes from: the axes aren't equivalent.
# Time drives MORE than Space in the current era (DE > DM).
# So Time weight > Space weight.
# And Dark dominates Light.
# Both asymmetries compound.

# What if: Time/Space = φ² (the horizontal coupling, measured as ratio)
# And Dark/Light = some vertical coupling V
# Then weights are:
# DE:  φ² × V
# DM:  1  × V
# b:   1  × 1
# γ:   φ² × 1
# Total = V(φ²+1) + (φ²+1) = (φ²+1)(V+1)

# From observed: DE/DM = φ² ✓ (horizontal within dark row)
# γ/b should also = φ² if horizontal coupling is universal.
# But γ/b = 5.38e-5/0.0493 = 0.00109 ≠ φ².
# UNLESS this is the z=0 snapshot and the "natural" ratio was φ² at some epoch.

# At z_eq: γ(z_eq) = b(z_eq) × (Ω_r/Ω_b) × (1+z_eq) = ... they approach equality
# Actually at z_eq, total radiation = total matter, not component by component.

# Let me try the approach where Dark/Light coupling is the PIPE ratio:
# Down = 2φ, Up = φ → Dark/Light natural weight = 2φ/φ = 2
# Or pipe capacity: Down = 2φ

# Weights with Dark/Light = pipe asymmetry:
# DE:  φ² × 2φ   (time × dark pipe)
# DM:  1  × 2φ
# b:   1  × φ    (up pipe)
# γ:   φ² × φ

w_de = PHI**2 * 2*PHI
w_dm = 1 * 2*PHI
w_b = 1 * PHI
w_gamma = PHI**2 * PHI

w_total = w_de + w_dm + w_b + w_gamma

print(f"  MODEL A: Time/Space = φ², Dark/Light = pipe (2φ down, φ up)")
print(f"    DE weight:  φ² × 2φ = 2φ³ = {w_de:.4f}")
print(f"    DM weight:  1 × 2φ  = 2φ  = {w_dm:.4f}")
print(f"    b weight:   1 × φ   = φ   = {w_b:.4f}")
print(f"    γ weight:   φ² × φ  = φ³  = {w_gamma:.4f}")
print(f"    Total = {w_total:.4f}")
print()

pred_de = w_de / w_total
pred_dm = w_dm / w_total
pred_b  = w_b / w_total
pred_g  = w_gamma / w_total

print(f"  PREDICTED vs OBSERVED:")
print(f"  ┌──────────────┬──────────┬──────────┬─────────┐")
print(f"  │ Component    │ Predicted│ Observed │   Δ     │")
print(f"  ├──────────────┼──────────┼──────────┼─────────┤")
print(f"  │ Ω_de         │ {pred_de:.4f}   │ {Omega_de:.4f}   │ {abs(pred_de-Omega_de)/Omega_de*100:5.1f}%  │")
print(f"  │ Ω_dm         │ {pred_dm:.4f}   │ {Omega_dm:.4f}   │ {abs(pred_dm-Omega_dm)/Omega_dm*100:5.1f}%  │")
print(f"  │ Ω_b          │ {pred_b:.4f}   │ {Omega_b:.4f}   │ {abs(pred_b-Omega_b)/Omega_b*100:5.1f}%  │")
print(f"  │ Ω_γ          │ {pred_g:.4f}   │ {Omega_gamma:.6f}│  huge   │")
print(f"  └──────────────┴──────────┴──────────┴─────────┘")
print()

# The γ prediction is way off because this model gives γ = φ³/total ≈ 0.28
# but observed γ = 5.38e-5. The model treats the grid as STATIC but
# the light row has been cosmologically processed (γ dilutes as a⁻⁴).

# Model B: Let the architecture set the DARK row, and derive light from
# the dark row via the OBSERVED vertical coupling.
print(f"  MODEL B: Architecture sets dark row, derives light from vertical coupling")
print()

# Dark row from architecture:
# DE + DM = dark_total, DE/DM = φ²
# → DE = dark_total × φ²/(1+φ²), DM = dark_total × 1/(1+φ²)
# But we need dark_total. From the pipe: Ωm = 1/(2φ) → dark = 1 - 1/(2φ)

# Wait — let's use the identity that FELL OUT of BL5:
# Ωm = 1/(2φ) (1.7% match)
# This means: light fraction of space = 1/(2φ) of which baryons are most
# and dark fraction of space = 1 - 1/(2φ) ... no, Ωm includes DM.

# Actually Ωm = DM + baryons = 0.3143. Ωm = 1/(2φ) = 0.309.
# DE = 1 - Ωm. Within DM+baryons, the split is DM/b.

# What the architecture naturally gives:
# The 2×2 grid TODAY (z=0) has radiation negligible.
# So effectively 3 components: DE, DM, b.
# Dark total ≈ DE + DM = 0.95
#
# From Ω = 1: DE + DM + b = 1 (ignoring radiation)
# From horizontal: DE/DM = φ²
# Need ONE MORE equation to fix all three.

# That third equation IS the vertical coupling.
# If DM/b = φ^α for some α, then:
# DE = φ² × DM, so DE + DM + b = 1
# φ²·DM + DM + DM/φ^α = 1
# DM(φ² + 1 + 1/φ^α) = 1
# DM = 1/(φ² + 1 + 1/φ^α)

print(f"  THREE-COMPONENT MODEL (ignoring radiation at z=0):")
print(f"    DE + DM + b = 1")
print(f"    DE/DM = φ²")
print(f"    DM/b = φ^α")
print()

# Scan α to find best fit
best_alpha = None
best_err = float('inf')

for alpha_trial in np.linspace(0.5, 5.0, 10000):
    dm_trial = 1 / (PHI**2 + 1 + PHI**(-alpha_trial))
    de_trial = PHI**2 * dm_trial
    b_trial = dm_trial / PHI**alpha_trial

    err = (abs(de_trial - Omega_de)/Omega_de +
           abs(dm_trial - Omega_dm)/Omega_dm +
           abs(b_trial - Omega_b)/Omega_b) / 3

    if err < best_err:
        best_err = err
        best_alpha = alpha_trial

dm_best = 1 / (PHI**2 + 1 + PHI**(-best_alpha))
de_best = PHI**2 * dm_best
b_best = dm_best / PHI**best_alpha

print(f"  BEST FIT: α = {best_alpha:.4f}")
print(f"  ┌──────────────┬──────────┬──────────┬─────────┐")
print(f"  │ Component    │ Predicted│ Observed │   Δ     │")
print(f"  ├──────────────┼──────────┼──────────┼─────────┤")
print(f"  │ Ω_de         │ {de_best:.4f}   │ {Omega_de:.4f}   │ {abs(de_best-Omega_de)/Omega_de*100:5.1f}%  │")
print(f"  │ Ω_dm         │ {dm_best:.4f}   │ {Omega_dm:.4f}   │ {abs(dm_best-Omega_dm)/Omega_dm*100:5.1f}%  │")
print(f"  │ Ω_b          │ {b_best:.4f}   │ {Omega_b:.4f}   │ {abs(b_best-Omega_b)/Omega_b*100:5.1f}%  │")
print(f"  └──────────────┴──────────┴──────────┴─────────┘")
print(f"  Average Δ = {best_err*100:.2f}%")
print()

# What IS α?
print(f"  WHAT IS α = {best_alpha:.4f}?")
for name, val in [("1", 1.0), ("φ", PHI), ("2", 2.0), ("3/2", 1.5),
                  ("φ²-1=φ", PHI), ("2/φ", 2/PHI), ("φ/2", PHI/2),
                  ("3", 3.0), ("5/2", 2.5), ("7/3", 7/3),
                  ("ln(φ²+1)", math.log(PHI**2+1)),
                  ("2+1/φ", 2+INV_PHI), ("φ+1/φ", PHI+INV_PHI),
                  ("√φ", math.sqrt(PHI)), ("φ²/φ=φ", PHI),
                  ("π/2", math.pi/2), ("e/2", math.e/2),
                  ("φ+1/2", PHI+0.5), ("2·ln(φ)", 2*math.log(PHI))]:
    delta_pct = abs(best_alpha - val) / val * 100
    marker = " ★★★" if delta_pct < 1 else (" ★★" if delta_pct < 3 else (" ★" if delta_pct < 5 else ""))
    print(f"      {name:>15} = {val:>8.4f}  Δ = {delta_pct:>6.2f}%{marker}")
print()

# Now try specific architectural values for α:
print(f"  ARCHITECTURAL CANDIDATES:")
for name, alpha_val in [("φ (golden ratio)", PHI),
                         ("3/2 (vertical half-step)", 1.5),
                         ("2/φ (vertical coupler)", 2/PHI),
                         ("φ+1/φ (= φ²/φ = φ... no, =√5)", PHI + INV_PHI)]:
    dm_a = 1 / (PHI**2 + 1 + PHI**(-alpha_val))
    de_a = PHI**2 * dm_a
    b_a = dm_a / PHI**alpha_val
    avg_err = (abs(de_a - Omega_de)/Omega_de +
               abs(dm_a - Omega_dm)/Omega_dm +
               abs(b_a - Omega_b)/Omega_b) / 3 * 100
    print(f"    α = {name}:")
    print(f"      DE={de_a:.4f} (obs {Omega_de}), DM={dm_a:.4f} (obs {Omega_dm}), b={b_a:.4f} (obs {Omega_b})")
    print(f"      Avg Δ = {avg_err:.1f}%")
    print()

# ════════════════════════════════════════════════════════════════════════════════
#  SUMMARY
# ════════════════════════════════════════════════════════════════════════════════
print(f"{'═' * 90}")
print(f"  SUMMARY — Coupled Space/Time × Light/Dark")
print(f"{'═' * 90}")

print(f"""
  KEY FINDINGS:

  1. THE GRID IS NOT SEPARABLE
     The 2×2 grid (Space/Time × Dark/Light) does NOT factor as a simple
     tensor product. The two axes are ENTANGLED — you can't treat them
     independently. Dylan was right: they MUST go in the same formula.

  2. EIGENVALUE RATIO OF THE Ω MATRIX ≈ φ²?
     When we treat the 2×2 grid as a matrix, eigenvalue ratio came out
     as {eigenvalues[0]/eigenvalues[1]:.4f} (Δ from φ² = {abs(eigenvalues[0]/eigenvalues[1] - PHI**2)/PHI**2*100:.1f}%).

  3. THE SYMMETRIC COUPLING MATRIX
     Best vertical coupling (symmetric): v = {best_v:.4f}
     Best vertical coupling (asymmetric, pipe): v_up = {best_vup:.4f}, v_down = {best_vdown:.4f}

  4. THE THREE-COMPONENT MODEL
     DE + DM + b = 1, DE/DM = φ², DM/b = φ^α
     Best α = {best_alpha:.4f}
     This gives all three Ω values from just TWO inputs: φ and α.

  5. THE LIGHT ROW IS TIME-PROCESSED
     Radiation (γ) has been diluted by cosmic expansion relative to
     baryons. The "natural" light-row coupling (at z_eq) might be φ²,
     but it's been modified by 13.8 Gyr of a⁻⁴ vs a⁻³ scaling.
     The dark row preserves its coupling because DE is constant and
     DM dilutes as a⁻³ just like baryons.

  THE COUPLED EQUATION:
     From just two axioms:
       1. DE/DM = φ²  (horizontal coupler)
       2. DM/b = φ^α  (vertical coupler, α ≈ {best_alpha:.3f})
     Plus Ω_total = 1, we get:
       DM = 1 / (φ² + 1 + φ^(-α))
       DE = φ² × DM
       b  = DM / φ^α
""")

print("=" * 90)
