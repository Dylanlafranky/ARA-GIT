import math

# =============================================================
# PRECISION TEST: Atomic Clock Transitions on the Action Axis
#
# Caesium-133 and Strontium-87 have transitions known to
# extraordinary precision. If the 4π octave spacing is real
# physics (not sampling artefact), it should appear in these
# systems where measurement error is negligible.
# =============================================================

h = 6.62607015e-34    # Planck constant (exact by definition since 2019)
hbar = h / (2 * math.pi)
eV = 1.602176634e-19  # electron volt in joules (exact)
c = 299792458         # speed of light m/s (exact)
k_B = 1.380649e-23    # Boltzmann constant (exact)

target_4pi = math.log10(4 * math.pi)        # 1.0992
target_2pi_sq = math.log10((2 * math.pi)**2) # 1.5964

print("=" * 80)
print("CAESIUM-133 TRANSITIONS")
print("=" * 80)
print()
print("Cs-133 is THE time standard. The second is defined as")
print("9,192,631,770 periods of the ground-state hyperfine transition.")
print()

# Caesium-133 key transitions
# All frequencies from NIST/CODATA
cs_transitions = {
    "Hyperfine ground (F=3→F=4)": {
        "freq": 9.192631770e9,       # Hz (exact, defines the second)
        "note": "Microwave, defines SI second"
    },
    "D1 line (6S→6P₁/₂)": {
        "freq": 3.351730450e14,      # Hz (NIST)
        "note": "894.3 nm, optical"
    },
    "D2 line (6S→6P₃/₂)": {
        "freq": 3.520586040e14,      # Hz (NIST)
        "note": "852.1 nm, optical"
    },
    "6S→7S (two-photon)": {
        "freq": 5.4394682e14,        # Hz (approx)
        "note": "539.5 nm"
    },
    "6S→5D₃/₂": {
        "freq": 6.535e14,            # Hz (approx, ~459 nm)
        "note": "459 nm UV"
    },
    "Ionisation limit": {
        "freq": 9.4092e14,           # Hz (from ionisation energy 3.894 eV)
        "note": "3.894 eV ionisation energy"
    },
}

print(f"{'Transition':<35s} {'Freq (Hz)':<15s} {'Period (s)':<12s} {'Energy (J)':<12s} {'Action/π (J·s)':<15s} {'log₁₀':<8s}")
print("-" * 100)

cs_actions = []
for name, data in cs_transitions.items():
    freq = data["freq"]
    period = 1.0 / freq
    energy = h * freq  # E = hf
    action_pi = period * energy / math.pi
    log_action = math.log10(action_pi)
    
    cs_actions.append((name, freq, period, energy, action_pi, log_action))
    print(f"{name:<35s} {freq:<15.4e} {period:<12.4e} {energy:<12.4e} {action_pi:<15.4e} {log_action:<8.2f}")

print()
print("Key insight: For ANY transition, Action/π = T × E / π = (1/f) × (hf) / π = h/π")
print(f"h/π = {h/math.pi:.6e} J·s")
print(f"This is CONSTANT for all single-photon transitions!")
print()
print("Wait — that's important. Let me think about this more carefully...")
print()

# The action per cycle of a PHOTON is always h/π = 2ℏ
# But the action of the ORBITAL TRANSITION is different from the photon
# The orbital has its own period and energy

print("=" * 80)
print("CORRECTION: Orbital Action vs Photon Action")
print("=" * 80)
print()
print("There are TWO different actions to compute:")
print("  1. The photon's action: T_photon × E_photon / π = h/π = 2ℏ (always)")
print("  2. The orbital's action: T_orbital × E_orbital / π (varies with n)")
print()
print("For Cs-133, the ORBITAL energy levels are what matter:")
print()

# Caesium energy levels (from ionisation limit)
# Cs ground state: 6S₁/₂ — ionisation energy = 3.8939 eV
# Excited states (energy ABOVE ground, i.e., excitation energy):
cs_levels = {
    "6S₁/₂ (ground)": {
        "binding_eV": 3.8939,     # ionisation energy
        "n_eff": 1.869,           # effective quantum number
    },
    "6P₁/₂": {
        "binding_eV": 3.8939 - 1.3859,  # = 2.508 eV
        "n_eff": 2.362,
    },
    "6P₃/₂": {
        "binding_eV": 3.8939 - 1.4550,  # = 2.439 eV  
        "n_eff": 2.397,
    },
    "7S₁/₂": {
        "binding_eV": 3.8939 - 2.2482,  # = 1.646 eV
        "n_eff": 2.917,
    },
    "5D₃/₂": {
        "binding_eV": 3.8939 - 2.700,   # ≈ 1.194 eV
        "n_eff": 3.426,
    },
}

# For a Rydberg-like atom, the classical orbital period scales as n³
# T_n ∝ n³, E_n ∝ 1/n², so Action ∝ n³ × (1/n²) = n
# Same as hydrogen! Action/π at effective level n_eff should scale linearly

# But Cs is NOT hydrogenic — the quantum defect changes things
# Let's compute properly using the Bohr model with quantum defects

# For alkali atoms: E_n = -Ry / (n - δ_l)² where δ is quantum defect
# Classical period: T_n = 2π × n³ / (Z_eff² × ω_Ry) for Rydberg states
# More precisely: T = h / (2 × |E_binding|) for Bohr orbits

# Actually, for the orbital period in a Coulomb potential:
# T = 2π ℏ n³ / (m_e × c² × α² × Z_eff²)
# But for Cs with quantum defects, n → n* = n - δ

# Simpler: Kepler's third law for Coulomb orbits gives
# T = (2π m_e a₀²) / ℏ × n*³ = (2π ℏ³) / (m_e e⁴) × n*³
# where n* is the effective quantum number

# The atomic unit of time is ℏ/E_h where E_h = 2×Ry = 27.211 eV
E_h_J = 27.211386245988 * eV  # Hartree energy
t_au = hbar / E_h_J           # atomic unit of time = 2.4189e-17 s

print(f"Atomic unit of time: {t_au:.4e} s")
print()

print(f"{'Level':<20s} {'Binding (eV)':<14s} {'n_eff':<8s} {'T_orbital (s)':<14s} {'E_bind (J)':<12s} {'Action/π':<15s} {'log₁₀':<8s}")
print("-" * 100)

cs_orbital_actions = []
for name, data in cs_levels.items():
    E_bind_eV = data["binding_eV"]
    n_eff = data["n_eff"]
    E_bind_J = E_bind_eV * eV
    
    # Classical orbital period: T = 2π ℏ n*³ / E_h  (in atomic units, T = 2π n*³)
    # Actually T = 2π × ℏ × n*³ / (Ry) ... let me be precise
    # For hydrogen: T_n = n³ × T₁ where T₁ = 2π ℏ / (2 Ry) = 2π ℏ³ / (m_e e⁴)
    # T₁ = 2π × 2.4189e-17 s = 1.5198e-16 s (matches our hydrogen ground state)
    # For Cs: replace n with n_eff
    
    T1_hydrogen = 2 * math.pi * t_au  # = 1.5198e-16 s
    T_orbital = T1_hydrogen * n_eff**3
    
    action_pi = T_orbital * E_bind_J / math.pi
    log_action = math.log10(action_pi)
    
    cs_orbital_actions.append((name, E_bind_eV, n_eff, T_orbital, E_bind_J, action_pi, log_action))
    print(f"{name:<20s} {E_bind_eV:<14.4f} {n_eff:<8.3f} {T_orbital:<14.4e} {E_bind_J:<12.4e} {action_pi:<15.4e} {log_action:<8.4f}")

print()
print("ACTION RATIOS BETWEEN Cs LEVELS:")
print("-" * 70)

for i in range(len(cs_orbital_actions)):
    for j in range(i+1, len(cs_orbital_actions)):
        name_i = cs_orbital_actions[i][0]
        name_j = cs_orbital_actions[j][0]
        log_i = cs_orbital_actions[i][6]
        log_j = cs_orbital_actions[j][6]
        gap = abs(log_j - log_i)
        ratio = cs_orbital_actions[j][4] / cs_orbital_actions[i][4]
        
        # Check ratio against n_eff ratio
        n_i = cs_orbital_actions[i][2]
        n_j = cs_orbital_actions[j][2]
        n_ratio = n_j / n_i
        
        # For Coulomb potential: Action/π ∝ n_eff (just like hydrogen)
        # So ratio of actions = ratio of n_eff
        
        print(f"  {name_j:<20s} / {name_i:<20s}  n_eff ratio = {n_ratio:.4f}  Action ratio = {ratio:.4f}  log gap = {gap:.4f}")

print()
print("=" * 80)
print("KEY THEORETICAL RESULT")
print("=" * 80)
print()
print("For ANY atom in a Coulomb potential (hydrogen-like or with quantum defects):")
print()
print("  Action/π = T × E / π")
print("           = (2π ℏ n*³ / E_h) × (Ry / n*²) / π")  
print("           = (2π ℏ × Ry / (π × E_h)) × n*")
print("           = (2ℏ × Ry / E_h) × n*")
print("           = (2ℏ × ½) × n*")
print("           = ℏ × n*")
print()
print("So: Action/π = n_eff × ℏ for ANY atom, not just hydrogen!")
print()
print("This means:")
print("  - The ratio between any two orbital actions = ratio of effective")
print("    quantum numbers")
print("  - For hydrogen (no quantum defect): n_eff = n (integer), ratios")
print("    are exactly the harmonic series")
print("  - For Cs/Sr (with quantum defects): n_eff is non-integer, ratios")
print("    are SHIFTED from the harmonic series by the defect")
print()
print("The quantum defect BREAKS the perfect harmonic structure for")
print("multi-electron atoms. The harmonic series is exact only for hydrogen.")
print()

# Let's verify with our Cs data
print("VERIFICATION with Cs data:")
for name, E_bind_eV, n_eff, T_orb, E_bind_J, action_pi, log_action in cs_orbital_actions:
    predicted = n_eff * hbar
    ratio = action_pi / predicted
    print(f"  {name:<20s}  Action/π = {action_pi:.4e}  n_eff × ℏ = {predicted:.4e}  ratio = {ratio:.6f}")

print()
print("=" * 80)
print("STRONTIUM-87 OPTICAL LATTICE CLOCK")
print("=" * 80)
print()

# Sr-87: THE most precise clock in the world
# Key transition: ¹S₀ → ³P₀ (clock transition) at 429.228 THz
# Ionisation energy: 5.6949 eV

sr_levels = {
    "5S² ¹S₀ (ground)": {
        "binding_eV": 5.6949,
        "n_eff": 1.549,  # effective quantum number for Sr
    },
    "5S5P ³P₀ (clock)": {
        "binding_eV": 5.6949 - 1.7752,  # = 3.9197 eV
        "n_eff": 1.891,
    },
    "5S5P ³P₁": {
        "binding_eV": 5.6949 - 1.7980,  # = 3.8969 eV
        "n_eff": 1.895,
    },
    "5S5P ¹P₁": {
        "binding_eV": 5.6949 - 2.6903,  # = 3.0046 eV
        "n_eff": 2.160,
    },
    "5S6S ³S₁": {
        "binding_eV": 5.6949 - 3.8107,  # = 1.8842 eV
        "n_eff": 2.728,
    },
    "5S4D ¹D₂": {
        "binding_eV": 5.6949 - 3.6366,  # = 2.0583 eV  
        "n_eff": 2.610,
    },
}

print(f"{'Level':<25s} {'Binding (eV)':<14s} {'n_eff':<8s} {'Action/π':<15s} {'n_eff × ℏ':<15s} {'Ratio':<8s}")
print("-" * 90)

sr_orbital_actions = []
for name, data in sr_levels.items():
    E_bind_eV = data["binding_eV"]
    n_eff = data["n_eff"]
    E_bind_J = E_bind_eV * eV
    
    T_orbital = T1_hydrogen * n_eff**3
    action_pi = T_orbital * E_bind_J / math.pi
    predicted = n_eff * hbar
    ratio = action_pi / predicted
    log_action = math.log10(action_pi)
    
    sr_orbital_actions.append((name, n_eff, action_pi, log_action))
    print(f"{name:<25s} {E_bind_eV:<14.4f} {n_eff:<8.3f} {action_pi:<15.4e} {predicted:<15.4e} {ratio:<8.4f}")

print()
print("ACTION RATIOS BETWEEN Sr LEVELS:")
print("-" * 70)

for i in range(len(sr_orbital_actions)):
    for j in range(i+1, len(sr_orbital_actions)):
        name_i = sr_orbital_actions[i][0]
        name_j = sr_orbital_actions[j][0]
        n_i = sr_orbital_actions[i][1]
        n_j = sr_orbital_actions[j][1]
        ratio = n_j / n_i
        
        # Check against simple fractions
        # Find nearest simple fraction
        best_frac = None
        best_err = 999
        for num in range(1, 13):
            for den in range(1, num+1):
                frac = num/den
                err = abs(ratio - frac) / frac
                if err < best_err:
                    best_err = err
                    best_frac = f"{num}:{den}"
        
        symbol = "✓" if best_err < 0.05 else ("~" if best_err < 0.10 else "✗")
        print(f"  {name_j:<25s} / {name_i:<25s}  n* ratio = {ratio:.4f}  nearest = {best_frac} ({best_err*100:.1f}%) {symbol}")

print()
print("=" * 80)
print("GAPS ON THE ACTION AXIS (log₁₀ scale)")
print("=" * 80)
print()

# Sort all Cs and Sr levels by action and compute consecutive gaps
print("CAESIUM consecutive gaps:")
cs_sorted = sorted(cs_orbital_actions, key=lambda x: x[6])
for i in range(len(cs_sorted)-1):
    gap = cs_sorted[i+1][6] - cs_sorted[i][6]
    # Check against 4π
    err_4pi = abs(gap - target_4pi) / target_4pi * 100
    err_2pi_sq = abs(gap - target_2pi_sq) / target_2pi_sq * 100
    best = "4π" if err_4pi < err_2pi_sq else "(2π)²"
    best_err = min(err_4pi, err_2pi_sq)
    print(f"  {cs_sorted[i][0]:<20s} → {cs_sorted[i+1][0]:<20s}  gap = {gap:.4f}  nearest: {best} ({best_err:.1f}%)")

print()
print("STRONTIUM consecutive gaps:")
sr_sorted = sorted(sr_orbital_actions, key=lambda x: x[3])
for i in range(len(sr_sorted)-1):
    gap = sr_sorted[i+1][3] - sr_sorted[i][3]
    err_4pi = abs(gap - target_4pi) / target_4pi * 100
    err_2pi_sq = abs(gap - target_2pi_sq) / target_2pi_sq * 100
    best = "4π" if err_4pi < err_2pi_sq else "(2π)²"
    best_err = min(err_4pi, err_2pi_sq)
    print(f"  {sr_sorted[i][0]:<25s} → {sr_sorted[i+1][0]:<25s}  gap = {gap:.4f}  nearest: {best} ({best_err:.1f}%)")

print()
print("=" * 80)
print("VERDICT")  
print("=" * 80)

