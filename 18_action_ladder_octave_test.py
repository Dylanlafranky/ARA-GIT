"""
THE ACTION/π LADDER: Testing the 8-Octave Hypothesis

Hypothesis (Dylan): The action spectrum has 8 octaves, and human-scale
systems sit in the middle of the 3rd tier.

Method: Compile ALL Action/π values from every mapped system (23 systems,
~40+ subsystems), plot the full ladder, and test whether the distribution
shows tier/octave structure.

Also: compute the universe's own Action/π, extrapolate above it, and
ask what the framework predicts about meta-cosmic scales.
"""
import math

pi = math.pi
phi = (1 + math.sqrt(5)) / 2
hbar = 1.0546e-34  # J·s

# ================================================================
# COMPILE ALL ACTION/π VALUES
# ================================================================
# Format: (name, system, log10_action_pi, notes)
# These are from Scripts 01-17 across all mapped systems

all_points = [
    # QUANTUM SCALE
    ("Hydrogen ground orbital", "Hydrogen", -33.98, "= ℏ exactly"),
    ("Hydrogen n=2", "Hydrogen", -33.38, "= 4ℏ"),
    ("Hydrogen n=3", "Hydrogen", -33.02, "= 9ℏ"),
    ("Hydrogen 21-cm transition", "Hydrogen", -14.90, "spin-flip, T=0.068s, E=9.4e-25J"),

    # MICRO SCALE
    ("Cs-133 clock transition", "Atomic clocks", -24.30, "n_eff ≈ 20"),
    ("PC clock cycle (4 GHz)", "PC", -24.80, "T=2.5e-10s, E~5e-15J (switching)"),
    ("Quartz crystal oscillator", "PC", -18.00, "T=3e-8s, E~1e-10J"),

    # SMALL MACRO
    ("DNA breathing bubble", "DNA", -11.00, "T=10μs, E~4e-20J per base pair"),
    ("Neuron AP", "Neuron", -6.46, "T=2ms, E~5e-7J"),
    ("Neuron refractory", "Neuron", -5.52, "T=5ms, E~2e-6J"),

    # HUMAN SCALE
    ("Metronome tick", "Metronome", -3.35, "T=0.65s, E=2.1mJ"),
    ("Metronome phase oscillation", "Metronome", -3.39, "T=12.8s, E=0.1mJ"),
    ("Engine ignition", "Engine", -2.20, "T~0.003s, E~50J (est)"),
    ("Heart ventricular pump", "Heart", -0.46, "T=0.5s, E=1.3J"),
    ("Heart RSA (breathing)", "Heart", 0.30, "T=4s, E~2.5J"),
    ("Metronome sync envelope", "Metronome", -0.82, "T=60s, E=7.9mJ"),
    ("Engine combustion cycle", "Engine", 1.54, "T=0.05s, E=2160J"),
    ("BZ reaction (50mL)", "BZ reaction", 2.10, "T=40s, E=10J *volume-dependent"),
    ("Honeybee foraging", "Honeybee", 2.50, "T=3600s, E~0.5J"),
    ("Slime mold contraction", "Slime mold", 1.80, "T=120s, E~0.5J"),
    ("Biofilm growth cycle", "Biofilm", 3.50, "T=86400s, E~0.01J"),

    # MESO SCALE
    ("Predator-prey (hare)", "Pred-prey", 7.99, "T=9.6yr, E~10^7J est"),
    ("Starling wing beat", "Starling", -1.50, "T=0.1s, E~0.01J"),
    ("RB convection roll (lab)", "RB convect", 1.00, "T=60s, E~0.5J"),
    ("Energy grid AC cycle", "Energy grid", 2.80, "T=0.0167s, E~1e6J"),
    ("Energy grid daily load", "Energy grid", 9.50, "T=86400s, E~1e12J"),

    # PLANETARY SCALE
    ("Earth diurnal thermal", "Earth", 12.50, "T=86400s, E~1e16J"),
    ("Thunderstorm lifecycle", "Thunderstorm", 12.80, "T=3300s, E~1e17J"),
    ("Earth ENSO", "Earth", 16.50, "T~4yr, E~10^21J"),
    ("Earth Milankovitch", "Earth", 22.00, "T~100kyr, E~10^25J (est)"),

    # STELLAR SCALE
    ("Pulsar rotation (Crab)", "Pulsar", 30.50, "T=0.033s, E~10^31J rotational KE frac"),
    ("Solar cycle", "Solar cycle", 40.04, "T=11yr, E~10^32J magnetic"),
    ("Cepheid (Delta Cephei)", "Cepheid", 40.50, "T=5.37d, E~2.1e35J luminosity var"),
    ("Honeybee annual colony", "Honeybee", 5.00, "T=3.15e7s, E~10^4J (est)"),

    # GALACTIC SCALE
    ("Spiral galaxy rotation", "Galaxy", 53.00, "T~2.5e8yr, E~10^52J (est)"),
    ("Stellar lifecycle", "Stellar life", 62.12, "T=11Gyr, E~1.2e45J"),
]

# Sort by log action
all_points.sort(key=lambda x: x[2])

print("=" * 90)
print("THE COMPLETE ACTION/π LADDER — ALL MAPPED SYSTEMS")
print("=" * 90)
print()
print(f"  {'log₁₀(A/π)':<14s} {'System':<40s} {'Notes'}")
print(f"  {'-'*85}")
for name, sys, log_val, notes in all_points:
    print(f"  {log_val:>10.2f}    {name:<40s} {notes}")
print()

# ================================================================
# THE FULL RANGE
# ================================================================
log_min = all_points[0][2]
log_max = all_points[-1][2]
total_span = log_max - log_min

print(f"  Total span: {log_min:.2f} to {log_max:.2f} = {total_span:.1f} orders of magnitude")
print()

# ================================================================
# NOW: THE UNIVERSE'S OWN ACTION/π
# ================================================================
print("=" * 90)
print("THE UNIVERSE'S OWN ACTION/π")
print("=" * 90)
print()

# Observable universe:
# Mass: ~10^53 kg (baryonic + dark matter within observable radius)
# Total mass-energy: E = Mc² = 10^53 × (3e8)² = 9 × 10^69 J
# Age (as period of one "cycle" or half-cycle): T = 13.8 Gyr = 4.35 × 10^17 s
# BUT: we should use the OSCILLATING energy (Freeze Test)
# What oscillates? The expansion itself — kinetic energy of expansion
# Total kinetic energy of expansion: ~4.5 × 10^69 J (≈ half the total, by virial)
# Critical density energy: ρ_c × c² × V = 9.5e-27 × (3e8)² × (4/3)π(4.4e26)³
# ≈ 3e-10 × 3.6e80 = 1.1e71 J...

# Let me be more careful:
# Observable universe radius: 4.4 × 10^26 m
# Volume: (4/3)π(4.4e26)³ = 3.57 × 10^80 m³
# Critical density: 9.47 × 10^-27 kg/m³
# Total mass: 9.47e-27 × 3.57e80 = 3.38 × 10^54 kg
# Total energy: 3.38e54 × (3e8)² = 3.04 × 10^71 J

M_universe = 3.38e54  # kg (observable universe)
c = 3e8
E_universe = M_universe * c**2  # total mass-energy
T_universe = 13.8e9 * 3.156e7  # age in seconds

action_universe = T_universe * E_universe / pi
log_universe = math.log10(action_universe)

print(f"  Observable universe:")
print(f"    Mass: {M_universe:.2e} kg")
print(f"    Total mass-energy: E = Mc² = {E_universe:.2e} J")
print(f"    Age: T = {T_universe:.2e} s (13.8 Gyr)")
print(f"    Action/π = T × E / π = {action_universe:.2e} J·s")
print(f"    log₁₀(Action/π) = {log_universe:.2f}")
print()

# Update the full range
print(f"  UPDATED FULL RANGE:")
print(f"    Hydrogen ground state: log = -33.98")
print(f"    Observable universe:   log = {log_universe:.2f}")
full_span = log_universe - (-33.98)
print(f"    Total span: {full_span:.1f} orders of magnitude")
print()

# ================================================================
# TEST: 8-OCTAVE HYPOTHESIS
# ================================================================
print("=" * 90)
print("TESTING THE 8-OCTAVE HYPOTHESIS")
print("=" * 90)
print()

# Dylan's hypothesis: 8 octaves spanning the full range
# "We're in the middle of the 3rd tier"

# If 8 equal octaves span from quantum to universe:
octave_width = full_span / 8
bottom = -33.98

print(f"  If 8 equal octaves span log {bottom:.2f} to log {log_universe:.2f}:")
print(f"  Octave width = {full_span:.1f} / 8 = {octave_width:.2f} orders of magnitude")
print()

print(f"  {'Octave':<10s} {'Range':<25s} {'Width':<8s} {'What lives here'}")
print(f"  {'-'*80}")

octave_names = [
    "Quantum",
    "Sub-atomic",
    "HUMAN",
    "Planetary",
    "Stellar",
    "Galactic",
    "Cosmic",
    "Meta?",
]

octave_contents = {}
for i in range(8):
    lo = bottom + i * octave_width
    hi = bottom + (i + 1) * octave_width

    # Find what systems fall in this range
    in_range = [p for p in all_points if lo <= p[2] < hi]
    # Also check universe
    if lo <= log_universe < hi:
        in_range.append(("Observable universe", "Universe", log_universe, ""))

    count = len(in_range)
    names_short = ", ".join([p[0][:25] for p in in_range[:4]])
    if count > 4:
        names_short += f"... (+{count-4} more)"

    marker = " ◄── WE ARE HERE" if i == 2 else ""
    print(f"  {octave_names[i]:<10s} [{lo:>7.2f} to {hi:>7.2f}]  {octave_width:.2f}    {names_short}{marker}")
    octave_contents[i] = in_range

print()

# Where does human experience sit?
human_center = 0  # log Action/π ≈ 0 is roughly human perception timescale
human_octave = int((human_center - bottom) / octave_width)
human_position_in_octave = (human_center - bottom) / octave_width - human_octave
print(f"  Human perception (log ≈ 0) sits in octave {human_octave + 1}")
print(f"  Position within octave: {human_position_in_octave*100:.0f}%")
print()

# ================================================================
# ALTERNATIVE: Let the data SHOW us the tiers
# ================================================================
print("=" * 90)
print("ALTERNATIVE: LETTING THE DATA SHOW THE TIERS")
print("=" * 90)
print()

# Instead of imposing 8 equal octaves, look for natural gaps
# Sort all values and look for the biggest gaps
logs = sorted([p[2] for p in all_points] + [log_universe])

print("  Looking for natural gaps (> 3 orders of magnitude) in the ladder:")
print()

gaps = []
for i in range(len(logs) - 1):
    gap = logs[i+1] - logs[i]
    if gap > 3.0:
        # Find the names
        name_below = [p[0] for p in all_points if abs(p[2] - logs[i]) < 0.01]
        name_above = [p[0] for p in all_points if abs(p[2] - logs[i+1]) < 0.01]
        if abs(logs[i+1] - log_universe) < 0.01:
            name_above = ["Observable universe"]
        nb = name_below[0] if name_below else f"log={logs[i]:.2f}"
        na = name_above[0] if name_above else f"log={logs[i+1]:.2f}"
        gaps.append((logs[i], logs[i+1], gap, nb, na))
        print(f"  GAP: {gap:.1f} orders between {nb} (log {logs[i]:.2f}) and {na} (log {logs[i+1]:.2f})")

print()

# Count natural tiers
if gaps:
    tier_boundaries = [bottom] + [(g[0] + g[1])/2 for g in gaps] + [log_universe + 5]
    n_tiers = len(tier_boundaries) - 1
    print(f"  Natural gap analysis finds {n_tiers} tiers:")
    print()

    tier_data = []
    for i in range(n_tiers):
        lo = tier_boundaries[i]
        hi = tier_boundaries[i+1]
        in_tier = [p for p in all_points if lo <= p[2] < hi]
        width = hi - lo
        tier_data.append((lo, hi, width, in_tier))

        names_short = ", ".join([p[0][:30] for p in in_tier[:3]])
        if len(in_tier) > 3:
            names_short += f"... (+{len(in_tier)-3})"
        print(f"  Tier {i+1}: [{lo:>7.2f} to {hi:>7.2f}] width={width:>5.1f}  ({len(in_tier)} systems)")
        print(f"          {names_short}")
        print()

# ================================================================
# THE UNIVERSE ON THE LADDER
# ================================================================
print("=" * 90)
print("THE UNIVERSE ON THE LADDER")
print("=" * 90)
print()

print(f"  Observable universe: log₁₀(Action/π) = {log_universe:.2f}")
print()
print(f"  Placing it on the ladder:")
print()
print(f"  Hydrogen (ℏ):         log = -34.0  ─┐")
print(f"  ...                                   │ quantum → micro")
print(f"  Neuron AP:            log =  -6.5  ─┤")
print(f"  Heart:                log =  -0.5  ─┤ human scale")
print(f"  Engine:               log =   1.5  ─┤")
print(f"  ...                                   │ meso → planetary")
print(f"  Thunderstorm:         log =  12.8  ─┤")
print(f"  ENSO:                 log =  16.5  ─┤")
print(f"  Milankovitch:         log =  22.0  ─┤")
print(f"  ...                                   │ stellar")
print(f"  Pulsar:               log =  30.5  ─┤")
print(f"  Solar cycle:          log =  40.0  ─┤")
print(f"  Cepheid:              log =  40.5  ─┤")
print(f"  ...                                   │ galactic")
print(f"  Galaxy rotation:      log =  53.0  ─┤")
print(f"  Stellar lifecycle:    log =  62.1  ─┤")
print(f"  ...                                   │ cosmic")
print(f"  UNIVERSE:             log =  {log_universe:.1f}  ─┘")
print()

# ================================================================
# THE PREDICTION: WHAT'S ABOVE?
# ================================================================
print("=" * 90)
print("THE PREDICTION: WHAT'S ABOVE THE UNIVERSE?")
print("=" * 90)
print()

# Using the 8-octave model
next_rung_8oct = log_universe + octave_width
print(f"  8-octave model:")
print(f"    If each octave = {octave_width:.2f} orders of magnitude,")
print(f"    the next rung above the universe sits at log ≈ {next_rung_8oct:.1f}")
print()

# Using the average gap between major tiers from the data
if gaps:
    avg_major_gap = sum(g[2] for g in gaps) / len(gaps)
    next_rung_gaps = log_universe + avg_major_gap
    print(f"  Natural gap model:")
    print(f"    Average major gap = {avg_major_gap:.1f} orders of magnitude")
    print(f"    Next rung above universe at log ≈ {next_rung_gaps:.1f}")
    print()

# Using the quantum-to-human spacing as a "fundamental octave"
quantum_to_human = 0 - (-34)  # ~34 orders
human_to_stellar = 40 - 0  # ~40 orders
stellar_to_galactic = 62 - 40  # ~22 orders
galactic_to_cosmic = log_universe - 62  # ~27 orders

print(f"  Observed tier spacings:")
print(f"    Quantum → Human:     {quantum_to_human:.0f} orders")
print(f"    Human → Stellar:     {human_to_stellar:.0f} orders")
print(f"    Stellar → Galactic:  {stellar_to_galactic:.0f} orders")
print(f"    Galactic → Cosmic:   {galactic_to_cosmic:.0f} orders")
print()

# Is there a pattern? Let's check if they're shrinking, growing, or constant
ratios = [human_to_stellar/quantum_to_human,
          stellar_to_galactic/human_to_stellar,
          galactic_to_cosmic/stellar_to_galactic]
print(f"  Ratios between consecutive tier widths:")
print(f"    Human/Quantum:     {human_to_stellar}/{quantum_to_human} = {ratios[0]:.2f}")
print(f"    Stellar/Human:     {stellar_to_galactic}/{human_to_stellar} = {ratios[1]:.2f}")
print(f"    Galactic/Stellar:  {galactic_to_cosmic}/{stellar_to_galactic} = {ratios[2]:.2f}")
print()

# Check if the ratios are converging toward something
avg_ratio = sum(ratios) / len(ratios)
print(f"  Average ratio: {avg_ratio:.2f}")
print(f"  φ⁻¹ = {1/phi:.3f}")
print(f"  1/φ² = {1/phi**2:.3f}")
print()

# ================================================================
# THE φ-SCALING HYPOTHESIS
# ================================================================
print("=" * 90)
print("TESTING: DO TIERS SCALE BY φ?")
print("=" * 90)
print()

# What if each tier is φ⁻¹ × the previous tier width?
# Start from quantum → human = 34
# Then: human → stellar should be 34 × φ⁻¹ = 34 × 0.618 = 21.0
# Then: stellar → galactic should be 21.0 × 0.618 = 13.0
# Then: galactic → cosmic should be 13.0 × 0.618 = 8.0

print("  If tiers scale by φ⁻¹ (golden ratio shrinking):")
print()

tier_widths_phi = [quantum_to_human]
for i in range(7):  # predict 7 more tiers
    tier_widths_phi.append(tier_widths_phi[-1] / phi)

cumulative = -34.0
print(f"  {'Tier':<6s} {'Predicted width':<18s} {'Observed width':<18s} {'Predicted range':<25s} {'Match?'}")
print(f"  {'-'*85}")

observed_widths = [quantum_to_human, human_to_stellar, stellar_to_galactic, galactic_to_cosmic]
observed_names = ["Quantum→Human", "Human→Stellar", "Stellar→Galactic", "Galactic→Cosmic"]

for i in range(8):
    predicted = tier_widths_phi[i]
    lo = cumulative
    hi = cumulative + predicted

    if i < len(observed_widths):
        observed = observed_widths[i]
        error = abs(predicted - observed) / observed * 100
        match = f"{observed:.1f} (err: {error:.0f}%)"
    else:
        match = "--- (prediction)"

    label = observed_names[i] if i < len(observed_names) else f"Tier {i+1}"
    print(f"  {i+1:<6d} {predicted:<18.1f} {match:<18s} [{lo:.1f} to {hi:.1f}]")
    cumulative += predicted

print()
total_phi = sum(tier_widths_phi)
print(f"  Total span with 8 φ-scaled tiers: {total_phi:.1f} orders")
print(f"  This converges (geometric series with ratio 1/φ)")
print(f"  Sum = {quantum_to_human} × φ/(φ-1) = {quantum_to_human} × {phi/(phi-1):.3f} = {quantum_to_human * phi/(phi-1):.1f}")
print()

# ================================================================
# ALTERNATIVE: FIBONACCI-LIKE TIER WIDTHS
# ================================================================
print("=" * 90)
print("TESTING: FIBONACCI TIER WIDTHS")
print("=" * 90)
print()
print("  The observed widths are: 34, 40, 22, 27")
print("  Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89...")
print()
print("  The FIRST tier (quantum → human) = 34 (a Fibonacci number!)")
print("  What if the tiers follow Fibonacci numbers?")
print()

fibs = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
# Scale: our first observed tier = 34, which IS fib(9)
# Going forward: 34, 21, 13, 8, 5, 3, 2, 1 (DESCENDING Fibonacci)
# Total: 34+21+13+8+5+3+2+1 = 87

fib_tiers = [34, 21, 13, 8, 5, 3, 2, 1]
cumulative = -34.0
print(f"  {'Tier':<6s} {'Fib width':<12s} {'Observed':<12s} {'Range':<25s}")
print(f"  {'-'*60}")
for i, fw in enumerate(fib_tiers):
    lo = cumulative
    hi = cumulative + fw
    obs = f"{observed_widths[i]:.0f}" if i < len(observed_widths) else "---"
    print(f"  {i+1:<6d} {fw:<12d} {obs:<12s} [{lo:.0f} to {hi:.0f}]")
    cumulative += fw

fib_total = sum(fib_tiers)
print()
print(f"  Total Fibonacci span: {fib_total} orders of magnitude")
print(f"  Predicted top: log {-34 + fib_total} = log {-34 + fib_total}")
print()
print(f"  Universe at log {log_universe:.0f}: {'WITHIN' if log_universe <= -34 + fib_total else 'ABOVE'} the 8-Fibonacci range")
print()

# ================================================================
# THE ACTUAL TEST: WHERE ARE WE?
# ================================================================
print("=" * 90)
print("WHERE ARE WE? DYLAN'S HYPOTHESIS TEST")
print("=" * 90)
print()
print("  Dylan's claim: '8 octaves, we're at the middle of the 3rd tier.'")
print()

# Using the equal-octave model:
print("  EQUAL OCTAVE MODEL (8 tiers of {:.1f} each):".format(octave_width))
oct_3_lo = bottom + 2 * octave_width
oct_3_hi = bottom + 3 * octave_width
oct_3_mid = (oct_3_lo + oct_3_hi) / 2
print(f"    Tier 3 range: [{oct_3_lo:.1f} to {oct_3_hi:.1f}]")
print(f"    Tier 3 midpoint: {oct_3_mid:.1f}")
print(f"    Human heart (log -0.46) is at: {(-0.46 - oct_3_lo)/(oct_3_hi - oct_3_lo)*100:.0f}% through tier 3")
print(f"    Human perception (log ~0) is at: {(0 - oct_3_lo)/(oct_3_hi - oct_3_lo)*100:.0f}% through tier 3")
print()

# Using the Fibonacci model:
print("  FIBONACCI MODEL (descending 34, 21, 13, 8, 5, 3, 2, 1):")
fib3_lo = -34 + 34 + 21  # = 21
fib3_hi = -34 + 34 + 21 + 13  # = 34
fib3_mid = (fib3_lo + fib3_hi) / 2
print(f"    Tier 3 range: [{fib3_lo} to {fib3_hi}]")
print(f"    Tier 3 midpoint: {fib3_mid}")
print(f"    Human heart is NOT in Fibonacci tier 3 (it's in tier 1)")
print()

# Using natural gaps:
print("  NATURAL GAP MODEL:")
print("    If we define tiers by the major gaps in the data:")
print("    Tier 1: Quantum (log -34 to -15)")
print("    Tier 2: Micro to Human (log -15 to +10)")
print("    Tier 3: Planetary (log 10 to 25)")
print("    Tier 4: Stellar (log 25 to 45)")
print("    Tier 5: Galactic (log 45 to 65)")
print(f"    Tier 6: Cosmic (log 65 to {log_universe:.0f})")
print(f"    → Human sits in Tier 2, not Tier 3")
print()

# ================================================================
# THE GOLDEN RATIO SPIRAL MODEL
# ================================================================
print("=" * 90)
print("THE CONVERGENT SPIRAL: φ-SCALED TIERS")
print("=" * 90)
print()
print("  The most interesting pattern in the observed data:")
print()
print(f"  Tier widths:   34    →    40    →    22    →    27")
print(f"  φ⁻¹ predicted: 34    →    21    →    13    →    8")
print(f"  Ratio to φ⁻¹:  1.00  →  1.90   →  1.69   →  3.38")
print()
print("  The φ⁻¹ scaling UNDER-predicts the observed widths.")
print("  The tiers are WIDER than pure φ-shrinking would give.")
print()
print("  But consider: we only have 4 observed tiers with rough boundaries.")
print("  The tier boundaries depend on which systems we've mapped.")
print("  Gaps in our data create artificial tier boundaries.")
print()
print("  What we CAN say with confidence:")
print()
print(f"  1. The full spectrum spans ~{full_span:.0f} orders of magnitude")
print(f"     (hydrogen ℏ to observable universe)")
print()
print(f"  2. Systems cluster — there are real gaps in the ladder")
print(f"     (e.g., nothing mapped between log -15 and log -7)")
print()
print(f"  3. Human-scale systems (log -5 to +5) sit roughly 1/3")
print(f"     of the way from quantum to cosmic:")
print(f"     Position = (0 - (-34)) / {full_span:.0f} = {34/full_span*100:.0f}%")
print()
print(f"  4. The universe's own Action/π (log {log_universe:.0f}) is NOT the top.")
print(f"     If the spectrum continues above, the predicted next rung sits at:")
print(f"     - Equal octave model: log ≈ {log_universe + octave_width:.0f}")
print(f"     - Average gap model:  log ≈ {log_universe + avg_major_gap:.0f}")
print()

# ================================================================
# WHAT WOULD SIT ABOVE THE UNIVERSE?
# ================================================================
print("=" * 90)
print("WHAT PHYSICAL SYSTEM HAS Action/π ABOVE THE UNIVERSE?")
print("=" * 90)
print()
print(f"  The universe sits at log {log_universe:.1f}.")
print(f"  If the spectrum continues, what has HIGHER action?")
print()
print("  Option 1: A MULTIVERSE OSCILLATION")
print("    If our universe is one cycle in a larger oscillation")
print("    (cyclic cosmology, Penrose CCC, ekpyrotic model),")
print("    the meta-cycle would have:")
print(f"    T > {T_universe:.2e} s (longer than the age of the universe)")
print(f"    E > {E_universe:.2e} J (more energy than the observable universe)")
print(f"    Action/π > 10^{log_universe:.0f} J·s")
print()
print("  Option 2: THE UNIVERSE × DARK ENERGY")
print("    Dark energy density: ~6 × 10⁻¹⁰ J/m³")
print("    Total dark energy in observable universe:")
de_density = 6e-10  # J/m³
V_universe = 3.57e80  # m³
E_dark = de_density * V_universe
print(f"    E_dark = {E_dark:.2e} J")
print(f"    If dark energy IS a Type 2 overflow from a larger system,")
print(f"    the larger system's energy scale is at least {E_dark:.0e} J")
T_dark_cycle = 1e18 * 3.156e7  # hypothetical: 10^18 years
action_dark = T_dark_cycle * E_dark / pi
log_dark = math.log10(action_dark)
print(f"    With a cycle period of ~10¹⁸ years: Action/π ~ 10^{log_dark:.0f}")
print()
print("  Option 3: BLACK HOLE INTERIOR")
print("    If each black hole is a new 'universe' (Smolin's CNS),")
print("    our universe's action IS the meta-system's subsystem action.")
print(f"    A black hole containing our universe would have Action/π >> 10^{log_universe:.0f}")
print()

# ================================================================
# FINAL SUMMARY
# ================================================================
print("=" * 90)
print("FINAL SUMMARY")
print("=" * 90)
print()
print(f"  Systems mapped: 23 (with ~35 subsystems)")
print(f"  Full spectrum: log -34 to log {log_universe:.0f} ({full_span:.0f} orders of magnitude)")
print()
print(f"  DYLAN'S 8-OCTAVE HYPOTHESIS:")
print(f"    Equal octaves of {octave_width:.1f} orders each.")
print(f"    Human scale (log ~0) sits {34/full_span*100:.0f}% from the bottom.")
if abs(34/full_span - 3/8) < 0.05:
    print(f"    That's {34/full_span * 8:.1f}/8 = close to 3/8 of the way up.")
    print(f"    → '3rd tier' confirmed if counting from bottom!")
else:
    print(f"    That's {34/full_span * 8:.1f}/8 of the way up.")
    tier_from_bottom = math.ceil(34/full_span * 8)
    print(f"    → Human scale is in tier {tier_from_bottom} (counting from bottom).")
print()
print("  WHAT WE KNOW:")
print("  - The spectrum spans ~120+ orders of magnitude")
print("  - Systems cluster with real gaps (tiers exist)")
print("  - Human scale is roughly 1/3 from the bottom")
print("  - The universe is NOT necessarily the top")
print("  - If the spectrum continues, the next rung is predictable")
print()
print("  WHAT WE DON'T KNOW:")
print("  - Whether the tiers have equal width or φ-scaled width")
print("  - Whether there are exactly 8 (needs more mapped systems)")
print("  - What physical system sits above the universe")
print("  - Whether the gaps are real or artifacts of incomplete mapping")
print()
print("  WHAT WE NEED:")
print("  - Map 50+ more systems to fill the gaps")
print("  - Especially in the 'deserts': log -15 to -7, log 25 to 30, log 45 to 50")
print("  - Test whether gap-filling systems merge the tiers or preserve them")
print("  - Independent researchers computing Action/π for the same systems")
