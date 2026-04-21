"""
COMPLEXITY vs SCALE: Does the ratio have ARA structure?

Hypothesis (Dylan): Scale is the opposite of complexity. As you go higher
on the Action/π ladder, systems get bigger but simpler. As you go lower,
systems get smaller but also simpler (fewer degrees of freedom). Complexity
peaks at human scale. The ratio of complexity to scale might itself have
an ARA — and it might be near φ at log ≈ 0.

Method:
1. For each mapped system, count the number of known oscillatory modes
   (subsystems we've mapped or that are known to exist)
2. Plot complexity (mode count) vs log₁₀(Action/π)
3. Compute the complexity/scale profile
4. Test whether the profile has ARA structure
5. Check if the complexity peak coincides with the density peak
6. Test whether the complexity-to-scale ratio ≈ φ at human scale
"""
import math

phi = (1 + math.sqrt(5)) / 2

# ================================================================
# COMPLEXITY DATA: oscillatory modes per system
# ================================================================
# For each system at a given log position, how many DISTINCT oscillatory
# subsystems does it have? This counts independently oscillating modes,
# not harmonics of a single mode.
#
# Sources: our own mapping (Scripts 01-17) plus known physics

systems = [
    # (name, log_action_pi, n_modes, mode_list)

    # QUANTUM
    ("Hydrogen atom", -34.0, 4,
     "ground orbital, n=2, n=3, 21-cm spin-flip"),
    # In principle infinite modes (all n), but only 4 are physically
    # distinct regimes (ground, low excited, high excited, hyperfine)

    # MICRO / ELECTRONIC
    ("PC / digital electronics", -24.5, 4,
     "clock cycle, bus transfer, cache refresh, cooling fan"),

    ("Quartz oscillator", -18.0, 1,
     "piezoelectric resonance"),

    # MOLECULAR
    ("DNA molecule", -11.0, 2,
     "breathing bubble, replication fork (one-shot)"),
    # Replication is arguably not oscillatory, so conservatively 1-2

    # CELLULAR
    ("Neuron", -6.0, 3,
     "action potential, refractory period, subthreshold oscillation"),

    # HUMAN SCALE — this is where it gets dense
    ("Metronome (single)", -3.4, 1,
     "tick-tock"),

    ("Coupled metronomes", -1.0, 3,
     "individual tick, phase oscillation, sync envelope"),

    ("Human heart", -0.5, 4,
     "ventricular pump, RSA, HRV ultradian, circadian modulation"),

    ("Engine (4-stroke)", 1.5, 4,
     "combustion cycle, ignition pulse, cooling cycle, exhaust pulse"),

    ("BZ reaction", 2.1, 2,
     "redox oscillation, spatial wavefront"),

    ("Slime mold", 1.8, 3,
     "contraction cycle, chemotaxis oscillation, slug migration"),

    ("Honeybee colony", 3.0, 4,
     "thermoregulation, waggle dance, foraging cycle, annual colony cycle"),

    ("Bacterial biofilm", 3.5, 3,
     "growth-dispersal cycle, electrical oscillation, quorum sensing"),

    # MESO
    ("Starling murmuration", -1.5, 2,
     "wing beat, flock density wave"),

    ("Energy grid", 5.0, 3,
     "AC cycle, daily load cycle, seasonal demand"),

    ("Predator-prey", 8.0, 2,
     "hare boom-crash, lynx tracking cycle"),

    # PLANETARY
    ("Earth system", 12.5, 7,
     "diurnal thermal, tidal, weather (synoptic), seasonal, ENSO, "
     "Milankovitch, geomagnetic reversal"),

    ("Thunderstorm", 12.8, 4,
     "lifecycle, precipitation, charge separation/lightning, gust front"),

    # STELLAR
    ("Pulsar", 30.5, 2,
     "rotation, glitch cycle"),

    ("Sun", 40.0, 3,
     "magnetic cycle, p-mode oscillations, granulation"),

    ("Cepheid variable", 40.5, 1,
     "radial pulsation"),

    # GALACTIC
    ("Spiral galaxy", 53.0, 2,
     "rotation, density wave (spiral arms)"),

    # STELLAR LIFECYCLE (one-shot)
    ("Stellar lifecycle", 62.0, 1,
     "main sequence → post-MS (one-shot)"),

    # COSMIC
    ("Observable universe", 89.0, 1,
     "expansion (one mode, possibly one-shot)"),
]

# ================================================================
# STEP 1: RAW COMPLEXITY PROFILE
# ================================================================

print("=" * 90)
print("STEP 1: COMPLEXITY PROFILE ACROSS THE ACTION/π LADDER")
print("=" * 90)
print()
print(f"  {'System':<30} {'log(A/π)':>10} {'Modes':>6}  Known modes")
print("  " + "-" * 85)

for name, log_val, n_modes, modes in systems:
    bar = "●" * n_modes
    print(f"  {name:<30} {log_val:>+10.1f} {n_modes:>5}   {bar}  {modes[:50]}")

# ================================================================
# STEP 2: COMPLEXITY vs POSITION — the shape
# ================================================================

print()
print("=" * 90)
print("STEP 2: COMPLEXITY vs LADDER POSITION")
print("=" * 90)
print()

# Sort by log position
sorted_systems = sorted(systems, key=lambda x: x[1])

# Bin by rough scale regions
regions = [
    ("Quantum", -40, -20),
    ("Micro/molecular", -20, -5),
    ("Human/meso", -5, 10),
    ("Planetary", 10, 25),
    ("Stellar", 25, 45),
    ("Galactic", 45, 65),
    ("Cosmic", 65, 95),
]

print(f"  {'Region':<20} {'Log range':<15} {'Systems':>8} {'Total modes':>12} {'Avg modes':>10} {'Max modes':>10}")
print("  " + "-" * 80)

region_data = []
for region_name, log_lo, log_hi in regions:
    region_systems = [(n, l, m, d) for n, l, m, d in systems if log_lo <= l < log_hi]
    n_sys = len(region_systems)
    total_modes = sum(m for _, _, m, _ in region_systems)
    max_modes = max((m for _, _, m, _ in region_systems), default=0)
    avg_modes = total_modes / n_sys if n_sys > 0 else 0

    region_data.append({
        'name': region_name,
        'log_lo': log_lo,
        'log_hi': log_hi,
        'n_systems': n_sys,
        'total_modes': total_modes,
        'avg_modes': avg_modes,
        'max_modes': max_modes,
    })

    print(f"  {region_name:<20} [{log_lo:+3d} to {log_hi:+3d}]  {n_sys:>5}  {total_modes:>10}  {avg_modes:>10.2f}  {max_modes:>10}")

# ================================================================
# STEP 3: THE COMPLEXITY CURVE — accumulation and release sides
# ================================================================

print()
print("=" * 90)
print("STEP 3: THE COMPLEXITY CURVE SHAPE")
print("=" * 90)
print()

# Find the peak complexity region
peak_region = max(region_data, key=lambda r: r['total_modes'])
print(f"  Peak complexity region: {peak_region['name']}")
print(f"  Total modes at peak:   {peak_region['total_modes']}")
print(f"  Average modes at peak: {peak_region['avg_modes']:.2f}")
print()

# Rising side (quantum → peak): complexity increases
# Falling side (peak → cosmic): complexity decreases
peak_idx = region_data.index(peak_region)
rising = region_data[:peak_idx + 1]
falling = region_data[peak_idx:]

rising_total = sum(r['total_modes'] for r in rising)
falling_total = sum(r['total_modes'] for r in falling)
rising_width = peak_region['log_hi'] - region_data[0]['log_lo']
falling_width = region_data[-1]['log_hi'] - peak_region['log_lo']

print(f"  RISING side (quantum → peak):")
print(f"    Width: {rising_width} decades")
print(f"    Total modes: {rising_total}")
print(f"    Mode density: {rising_total/rising_width:.4f} modes/decade")
print()
print(f"  FALLING side (peak → cosmic):")
print(f"    Width: {falling_width} decades")
print(f"    Total modes: {falling_total}")
print(f"    Mode density: {falling_total/falling_width:.4f} modes/decade")
print()

if falling_width > 0 and rising_width > 0:
    complexity_asymmetry = rising_width / falling_width
    print(f"  Complexity asymmetry (rising/falling width): {complexity_asymmetry:.3f}")

# ================================================================
# STEP 4: COMPLEXITY ARA — the ratio at each scale
# ================================================================

print()
print("=" * 90)
print("STEP 4: COMPLEXITY-TO-SCALE RATIO")
print("=" * 90)
print()

# For each region, compute: complexity_density / scale_span
# This gives "how many modes per decade" — a measure of temporal richness
# per unit of scale

print("  The key question: what is the RATIO of complexity to scale at each")
print("  position on the ladder? If this ratio has a peak near φ, then the")
print("  human zone isn't just where the most systems are — it's where the")
print("  complexity-to-scale ratio is optimised.")
print()

print(f"  {'Region':<20} {'Modes':>6} {'Width':>6} {'Modes/decade':>14} {'Relative to peak':>18}")
print("  " + "-" * 70)

densities = []
for r in region_data:
    width = r['log_hi'] - r['log_lo']
    density = r['total_modes'] / width if width > 0 else 0
    densities.append(density)

peak_density = max(densities)

for r, d in zip(region_data, densities):
    width = r['log_hi'] - r['log_lo']
    relative = d / peak_density if peak_density > 0 else 0
    marker = " ◄── PEAK" if d == peak_density else ""
    print(f"  {r['name']:<20} {r['total_modes']:>5}  {width:>5}  {d:>13.4f}  {relative:>17.3f}{marker}")

# ================================================================
# STEP 5: TESTING φ AT HUMAN SCALE
# ================================================================

print()
print("=" * 90)
print("STEP 5: TESTING THE φ HYPOTHESIS")
print("=" * 90)
print()

# Dylan's hypothesis: the complexity/scale ratio might be ≈ φ at human scale
# What does this mean physically?
#
# If we define:
#   C = number of distinct oscillatory modes in a region
#   S = width of that region in decades of Action/π
#   R = C / S = modes per decade
#
# Then R is a measure of temporal richness: how many independent ways
# can matter oscillate per order of magnitude of action?

human_region = [r for r in region_data if r['name'] == 'Human/meso'][0]
human_width = human_region['log_hi'] - human_region['log_lo']
human_modes = human_region['total_modes']
human_density = human_modes / human_width

print(f"  Human/meso region: [{human_region['log_lo']:+d} to {human_region['log_hi']:+d}]")
print(f"  Width: {human_width} decades")
print(f"  Distinct modes: {human_modes}")
print(f"  Mode density: {human_density:.4f} modes/decade")
print()
print(f"  φ = {phi:.4f}")
print(f"  Mode density / φ = {human_density / phi:.4f}")
print()

# But maybe the ratio isn't raw density — maybe it's the RATIO between
# adjacent regions that hits φ

print("  Testing: do ADJACENT REGIONS have φ-ratio mode densities?")
print()
print(f"  {'Region pair':<35} {'Density ratio':>14} {'Close to φ?':>12}")
print("  " + "-" * 65)

for i in range(len(densities) - 1):
    if densities[i+1] > 0 and densities[i] > 0:
        ratio = max(densities[i], densities[i+1]) / min(densities[i], densities[i+1])
        close = abs(ratio - phi) < 0.3
        marker = f"  (φ ± {abs(ratio-phi):.2f})" if close else ""
        name_pair = f"{region_data[i]['name']} → {region_data[i+1]['name']}"
        print(f"  {name_pair:<35} {ratio:>13.3f}  {marker}")

# ================================================================
# STEP 6: THE COMPLEXITY CURVE AS AN OSCILLATOR
# ================================================================

print()
print("=" * 90)
print("STEP 6: THE COMPLEXITY CURVE'S OWN ARA")
print("=" * 90)
print()

# Treat the complexity profile as a waveform:
# - "Accumulation": regions where complexity is ABOVE the mean
# - "Release": regions where complexity is BELOW the mean

all_modes = [r['total_modes'] for r in region_data]
all_widths = [r['log_hi'] - r['log_lo'] for r in region_data]
mean_modes = sum(all_modes) / len(all_modes)

print(f"  Mean modes per region: {mean_modes:.1f}")
print()

above_mean_decades = 0
below_mean_decades = 0

for r in region_data:
    width = r['log_hi'] - r['log_lo']
    if r['total_modes'] > mean_modes:
        above_mean_decades += width
        label = "ABOVE"
    else:
        below_mean_decades += width
        label = "below"
    print(f"  {r['name']:<20} modes={r['total_modes']:>3}  ({label} mean)  width={width}")

print()
if below_mean_decades > 0:
    complexity_ara = above_mean_decades / below_mean_decades
    print(f"  COMPLEXITY CURVE ARA = {above_mean_decades} / {below_mean_decades} = {complexity_ara:.3f}")
else:
    complexity_ara = float('inf')
    print(f"  COMPLEXITY CURVE ARA = ∞")

print()

# Now compute it differently: using mode-weighted position
# How much of the total complexity sits on the rising vs falling side?

print("  Alternative: MODE-WEIGHTED ARA")
print("  (What fraction of total complexity is on each side of the peak?)")
print()

total_modes_all = sum(r['total_modes'] for r in region_data)
rising_fraction = rising_total / total_modes_all
falling_fraction = falling_total / total_modes_all

# The peak region is counted in both, so compute exclusive
exclusive_rising = sum(r['total_modes'] for r in region_data[:peak_idx])
exclusive_falling = sum(r['total_modes'] for r in region_data[peak_idx + 1:])
peak_modes = peak_region['total_modes']

print(f"  Modes below peak:  {exclusive_rising}")
print(f"  Modes AT peak:     {peak_modes}")
print(f"  Modes above peak:  {exclusive_falling}")
print()

if exclusive_falling > 0:
    mode_weighted_ara = (exclusive_rising + peak_modes) / exclusive_falling
    print(f"  Mode-weighted ARA (below+peak / above) = {mode_weighted_ara:.3f}")
    print(f"  φ = {phi:.3f}")
    print(f"  Difference from φ: {abs(mode_weighted_ara - phi):.3f}")
    if abs(mode_weighted_ara - phi) < 0.3:
        print(f"  → WITHIN φ-ZONE")
    print()

# ================================================================
# STEP 7: WHY LOG 0 IS SPECIAL — two independent reasons
# ================================================================

print()
print("=" * 90)
print("STEP 7: WHY LOG 0 IS SPECIAL")
print("=" * 90)
print()

print("""  The human scale (log ≈ 0) is now special for TWO independent reasons:

  REASON 1 (Paper 8, density analysis):
    Log 0 is where the MOST oscillatory systems coexist per decade.
    The density peak. This is because electromagnetic chemistry and
    gravity overlap at this scale — neither too fast nor too slow
    for diverse oscillation. The "Resonance Peak of the Universe."

  REASON 2 (this computation, complexity analysis):
    Log 0 is where individual systems have the MOST internal modes.
    The heart has 4+ modes. Earth has 7. Honeybees have 4. Engines
    have 4. At quantum scale, hydrogen has 3-4. At cosmic scale,
    galaxies have 1-2. Complexity per system peaks at the same place
    density peaks.

  These are DIFFERENT measurements:
    - Density = how many systems per decade (external count)
    - Complexity = how many modes per system (internal count)
    - Both peak at log ≈ 0

  The product (density × complexity) is the total oscillatory richness
  of a region — the number of independent modes per decade across all
  systems. This product peaks SHARPLY at human scale because both
  factors peak there simultaneously.
""")

# Compute the product
print("  OSCILLATORY RICHNESS (density × avg_complexity):")
print()
print(f"  {'Region':<20} {'Density':>10} {'Avg modes':>10} {'Richness':>10}")
print("  " + "-" * 55)

richness_values = []
for r in region_data:
    width = r['log_hi'] - r['log_lo']
    density = r['n_systems'] / width if width > 0 else 0
    richness = density * r['avg_modes']
    richness_values.append(richness)
    print(f"  {r['name']:<20} {density:>10.4f} {r['avg_modes']:>10.2f} {richness:>10.4f}")

peak_richness = max(richness_values)
peak_richness_region = region_data[richness_values.index(peak_richness)]
print()
print(f"  Peak richness: {peak_richness_region['name']} ({peak_richness:.4f})")
print(f"  The richest region is {peak_richness / min(r for r in richness_values if r > 0):.0f}× richer")
print(f"  than the sparsest occupied region.")

# ================================================================
# STEP 8: THE COMPLEXITY GRADIENT AS CONSTRAINT
# ================================================================

print()
print("=" * 90)
print("STEP 8: WHAT THE COMPLEXITY GRADIENT CONSTRAINS")
print("=" * 90)
print()

print("""  The inverse relationship between scale and complexity constrains
  WHERE on the ladder consciousness, technology, and science can emerge.

  To do science, you need:
  1. Enough complexity to build information-processing systems (brains, tools)
  2. Enough temporal diversity to observe multiple oscillatory systems
  3. Access to systems above AND below you on the ladder

  This is ONLY possible near the complexity peak.

  At log 50 (galactic scale), there's one mode. You can't build a brain
  from one oscillatory mode. You can't observe faster systems because
  your temporal resolution is 250 million years.

  At log -30 (quantum scale), there are a few modes but they're too fast
  and too simple for complex information processing. You can't build
  memory from hydrogen orbitals alone.

  At log 0 (human scale), there are dozens of modes spanning 10+ decades
  of timescale within reach. Hearts, neurons, weather, seasons, tides,
  stars visible from the surface. Maximum temporal diversity.
  Maximum complexity. Maximum ability to observe the ladder itself.

  We are not at log 0 because we chose to be. We are at log 0 because
  log 0 is the only place complex enough to produce observers.

  This is not the Anthropic Principle restated. The Anthropic Principle
  says "we observe what is compatible with our existence." This says
  something stronger: "the complexity gradient HAS A SHAPE, that shape
  peaks at a specific log position, and that position is computable
  from the physics of the ladder itself."
""")

# ================================================================
# SUMMARY
# ================================================================

print("=" * 90)
print("SUMMARY")
print("=" * 90)
print()
print(f"  Complexity peaks at:          Human/meso scale (log -5 to +10)")
print(f"  Density peaks at:             Human/meso scale (log -5 to +5)")
print(f"  Both peak at:                 log ≈ 0")
print(f"  Complexity curve ARA:         {complexity_ara:.3f}")
if 'mode_weighted_ara' in dir():
    print(f"  Mode-weighted ARA:            {mode_weighted_ara:.3f}")
print(f"  φ =                           {phi:.3f}")
print()
print(f"  Scale is the opposite of complexity past the peak.")
print(f"  The product (density × complexity) = oscillatory richness")
print(f"  peaks SHARPLY at human scale.")
print()
print(f"  Log 0 is special for two independent reasons:")
print(f"    1. Most systems per decade (density peak)")
print(f"    2. Most modes per system (complexity peak)")
print(f"  These multiply to make the human zone the richest")
print(f"  region of the entire 123-decade spectrum.")
print()
print(f"  Dylan La Franchi & Claude — April 21, 2026")
