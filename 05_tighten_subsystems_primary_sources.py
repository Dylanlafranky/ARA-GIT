import math

# =============================================================
# TIGHTEN SUBSYSTEM VALUES FROM PRIMARY SOURCES
#
# The p=0.000017 result used subsystem gaps from our octave notes.
# Those gaps were computed from subsystem Action/π values.
# Some of those values were rough estimates. Let's go back to
# first principles for each subsystem.
#
# For each: Period (T) and Energy (E) must come from published
# literature. Action/π = T × E / π.
# =============================================================

pi = math.pi

print("=" * 90)
print("SUBSYSTEM ACTION VALUES — PRIMARY SOURCES")
print("=" * 90)
print()

# We need the WITHIN-SYSTEM consecutive gaps.
# The 8 gaps from our octave notes were:
#   Neuron: Depol → Refractory = 0.976
#   Neuron: Refractory → Vesicle = 0.983
#   Engine: Valve → PC Boost = 0.977
#   Thunderstorm: Gust → Precip = 0.964
#   Predator-prey: Veg → Lynx = 1.075
#   Heart: Myocyte → RSA = 1.484
#   Hydrogen: Metastable → CPU (cross-system, shouldn't count)
#   Engine: Boost → Thermal = 1.713
#
# Wait — "Hydrogen: Metastable → CPU" is a CROSS-SYSTEM gap, not within-system.
# That was an error in the original analysis. Let me recompute carefully.

all_subsystems = {}

# ----- NEURON -----
# Source: Attwell & Laughlin, J Cereb Blood Flow Metab, 2001
# Hodgkin & Huxley 1952 for AP timing
print("NEURON (cortical pyramidal)")
print("-" * 60)

neuron = {}

# Depolarisation (subthreshold integration)
# T: ~10ms integration time (from EPSP summation to threshold)
# E: subthreshold ionic current energy ~0.5 pJ
# Source: Lennie 2003, metabolic cost ~0.5-1 pJ per subthreshold integration
neuron["Depolarisation"] = {
    "T": 10e-3,           # 10 ms
    "E": 0.5e-12,         # 0.5 pJ
    "T_source": "Softky & Koch 1993, ~5-20ms integration window",
    "E_source": "Lennie 2003, subthreshold energy budget",
}

# Action potential (full spike + immediate recovery)
# T: 2-3 ms for cortical neuron AP
# E: ~5 pJ (Attwell & Laughlin 2001: ~2.4×10⁹ ATP per spike × 5×10⁻²⁰ J/ATP)
# Actually: Attwell gives ~3.2×10⁸ ATP molecules for one AP in cortical neuron
# At ~5×10⁻²⁰ J per ATP hydrolysis → ~1.6×10⁻¹¹ J ≈ 16 pJ
# More recent: Hallermann et al 2012: ~5-10 pJ
neuron["Action potential"] = {
    "T": 2.65e-3,         # 2.65 ms (our original value)
    "E": 5e-12,           # 5 pJ (conservative estimate)
    "T_source": "Hodgkin & Huxley 1952; Bean 2007",
    "E_source": "Attwell & Laughlin 2001; Hallermann 2012",
}

# Refractory period (absolute + relative)
# T: absolute ~1-2ms, relative ~5-10ms, total effective ~5ms
# E: Na/K pump restoring gradients, ~10 pJ
# Source: Hodgkin cycle; Crotty et al 2006
neuron["Refractory"] = {
    "T": 5e-3,            # 5 ms effective refractory
    "E": 10e-12,          # 10 pJ (pump energy to restore)
    "T_source": "Bean 2007, effective refractory 3-7ms",
    "E_source": "Crotty et al 2006, Na/K pump energy",
}

# Vesicle recycling (full synaptic cycle)
# T: 50-200 ms for fast recycling; ~10s for slow pool
# E: ~0.5-1 pJ per vesicle, but ~100 vesicles per spike
# Fast recycling: T ~100ms, E ~50 pJ
neuron["Vesicle recycling"] = {
    "T": 100e-3,          # 100 ms fast recycling
    "E": 50e-12,          # 50 pJ (100 vesicles × 0.5 pJ)
    "T_source": "Südhof 2004, fast endocytic pathway",
    "E_source": "Bhatt et al 2009, vesicle energetics",
}

for name, data in neuron.items():
    action = data["T"] * data["E"] / pi
    log_a = math.log10(action)
    neuron[name]["action"] = action
    neuron[name]["log"] = log_a
    print(f"  {name:<25s}  T={data['T']:.2e}s  E={data['E']:.2e}J  Action/π={action:.2e}  log={log_a:.3f}")

all_subsystems["Neuron"] = neuron

# ----- HEART -----
print()
print("HEART")
print("-" * 60)

heart = {}

# Myocyte contraction (single cardiomyocyte AP)
# T: ~250-300ms (ventricular AP duration)
# E: ~7-10 mJ metabolic per beat for whole ventricle / ~2×10⁹ myocytes
#   → per myocyte: ~5 nJ
# Better: single myocyte force × displacement, ~1-5 nJ per contraction
# Source: Gibbs & Loiselle 2001
heart["Myocyte AP"] = {
    "T": 280e-3,          # 280 ms ventricular AP
    "E": 5e-9,            # 5 nJ per myocyte contraction
    "T_source": "Nerbonne & Kass 2005, ventricular AP 250-300ms",
    "E_source": "Gibbs & Loiselle 2001, single myocyte energetics",
}

# Ventricular pump (full cardiac cycle)
# T: 833 ms (72 bpm)
# E: 1.3 J (stroke work: ~80 mmHg × 70 mL)
# Source: Guyton & Hall, standard physiology
heart["Ventricular pump"] = {
    "T": 0.833,           # 833 ms
    "E": 1.3,             # 1.3 J stroke work
    "T_source": "Standard: 72 bpm",
    "E_source": "Guyton & Hall, stroke work",
}

# RSA (respiratory sinus arrhythmia)
# T: ~4-6 seconds (respiratory cycle)
# E: modulation energy — the heart rate variation driven by vagal tone
#   HR varies ~10-15 bpm over breathing cycle, affecting cardiac output by ~10%
#   → ~0.13 J variation per breath-modulated beat × ~5 beats = ~0.65 J
# Actually: RSA modulates beat-to-beat interval, total energy effect per 
#   respiratory cycle ≈ change in cardiac output × one breath
# This is tricky. Let's estimate: 
#   Mean CO = 5 L/min, RSA modulates by ~5%, so ~0.25 L/min
#   Over one breath (5s): energy of 0.25/60×5 = 0.021 L of blood at ~1.3 J/beat
#   Better: ~5 beats per breath, each varying by ~10%, so ~5×0.13 = 0.65 J
heart["RSA envelope"] = {
    "T": 5.0,             # 5 seconds (respiratory cycle)
    "E": 0.65,            # ~0.65 J modulation energy
    "T_source": "Normal breathing ~12 breaths/min",
    "E_source": "Estimated from cardiac output modulation",
}

# Circadian HRV
# T: 86400 s (24 hr)
# E: Total cardiac work per day = ~1.3 J × 100,000 beats ≈ 130,000 J
#   But what OSCILLATES is the day-night variation
#   HR drops ~10-20% during sleep, so energy variation ~20% of daily total
#   → ~26,000 J oscillation amplitude
heart["Circadian HRV"] = {
    "T": 86400,           # 24 hours
    "E": 26000,           # ~26 kJ (20% of daily cardiac work)
    "T_source": "24-hour cycle",
    "E_source": "Estimated from sleep-wake HR variation",
}

for name, data in heart.items():
    action = data["T"] * data["E"] / pi
    log_a = math.log10(action)
    heart[name]["action"] = action
    heart[name]["log"] = log_a
    print(f"  {name:<25s}  T={data['T']:.2e}s  E={data['E']:.2e}J  Action/π={action:.2e}  log={log_a:.3f}")

all_subsystems["Heart"] = heart

# ----- ENGINE -----
print()
print("ENGINE (4-stroke petrol, 3000 RPM)")
print("-" * 60)

engine = {}

# Valve event
# T: ~3-5ms at 3000 RPM (valve open duration ~200 crank degrees at high RPM)
#   Actually: intake valve open for ~240° of 720° cycle
#   At 3000 RPM: one cycle = 40ms, valve open = 240/720 × 40 = 13.3ms
#   But the valve EVENT (opening or closing transition) is ~2-5ms
# E: kinetic energy of valve + spring = ~0.5-2 J
#   Valve mass ~50g, peak velocity ~3 m/s → KE = 0.5 × 0.05 × 9 = 0.225 J
#   Spring stored energy ~1-2 J
engine["Valve event"] = {
    "T": 4e-3,            # 4 ms transition
    "E": 1.0,             # ~1 J (spring + kinetic)
    "T_source": "Typical valve event at 3000 RPM",
    "E_source": "Valve spring energy + kinetic",
}

# Combustion cycle (full 4-stroke)
# T: 40 ms at 3000 RPM (720° = 2 revolutions)
# E: 2700 J (fuel energy: ~35 g/kWh × 75kW / 3000 RPM × 60 × 43 MJ/kg)
engine["Combustion cycle"] = {
    "T": 0.04,            # 40 ms
    "E": 2700,            # 2700 J fuel energy
    "T_source": "3000 RPM = 50 Hz → 40ms per cycle",
    "E_source": "Heywood, Internal Combustion Engine Fundamentals",
}

# Boost response (turbo spool-up)
# T: 0.3-1.0 s (turbo lag)
# E: kinetic energy of turbine wheel + compressed air
#   Turbo wheel ~150,000 RPM, mass ~200g, radius ~25mm
#   KE = 0.5 × I × ω² ≈ 0.5 × 0.5×0.2×0.025² × (150000×2π/60)² ≈ ~15 kJ? 
#   That seems high. Typical turbo stores ~1-5 kJ in rotation.
#   Boost pressure energy: ~1 bar × 2L displacement × 50 cycles/s × 0.5s ≈ ~5 kJ
engine["Boost response"] = {
    "T": 0.5,             # 500 ms
    "E": 5000,            # ~5 kJ
    "T_source": "Typical turbo spool time",
    "E_source": "Turbine KE + manifold pressure energy",
}

# Thermal equilibrium (warmup cycle)
# T: ~300s (5 min to reach operating temp)
# E: thermal mass of engine: ~50 kg iron × 500 J/kg·K × 60°C rise = 1.5 MJ
engine["Thermal equilibrium"] = {
    "T": 300,             # 5 minutes
    "E": 1.5e6,           # 1.5 MJ thermal mass
    "T_source": "Typical warmup to operating temperature",
    "E_source": "Engine block thermal mass × temperature rise",
}

for name, data in engine.items():
    action = data["T"] * data["E"] / pi
    log_a = math.log10(action)
    engine[name]["action"] = action
    engine[name]["log"] = log_a
    print(f"  {name:<25s}  T={data['T']:.2e}s  E={data['E']:.2e}J  Action/π={action:.2e}  log={log_a:.3f}")

all_subsystems["Engine"] = engine

# ----- THUNDERSTORM -----
print()
print("THUNDERSTORM (single-cell)")
print("-" * 60)

thunder = {}

# Lightning stroke
# T: ~30 μs for return stroke; ~200ms for full flash including leaders
# E: ~1 GJ (10⁹ J) per flash (Uman 1987)
# Using the return stroke as the "cycle"
thunder["Lightning return stroke"] = {
    "T": 30e-6,           # 30 μs
    "E": 1e9,             # 1 GJ
    "T_source": "Uman 1987, return stroke duration",
    "E_source": "Uman 1987, ~1 GJ dissipated per flash",
}

# Gust front (outflow boundary)
# T: ~5-15 minutes (outflow development to full extent)
# E: kinetic energy of outflow: ~10 km × 10 km × 1 km deep, 
#   density 1.2 kg/m³, speed 15 m/s
#   KE = 0.5 × 1.2 × 10⁴×10⁴×10³ × 15² ≈ 1.35 × 10¹¹ J
thunder["Gust front"] = {
    "T": 600,             # 10 minutes
    "E": 1.35e11,         # ~135 GJ kinetic energy
    "T_source": "Wakimoto 1982, outflow lifecycle",
    "E_source": "Kinetic energy of outflow boundary",
}

# Precipitation cycle (one burst of heavy rain)
# T: ~15-30 minutes for one precipitation pulse
# E: latent heat of condensation for precipitation
#   Typical single cell: 10⁶ kg of rain (1mm over 1 km²)
#   Latent heat: 10⁶ × 2.5×10⁶ J/kg = 2.5 × 10¹² J
thunder["Precipitation pulse"] = {
    "T": 1200,            # 20 minutes
    "E": 2.5e12,          # 2.5 TJ latent heat
    "T_source": "Houze 1993, precipitation lifetime",
    "E_source": "Latent heat of condensation",
}

# Full cell lifecycle
# T: 3300 s (55 min)
# E: 10¹² J total (our original estimate)
thunder["Cell lifecycle"] = {
    "T": 3300,            # 55 minutes
    "E": 1e12,            # 1 TJ total
    "T_source": "Byers & Braham 1949, cell lifecycle ~30-60 min",
    "E_source": "Emanuel 1994, total energy budget",
}

for name, data in thunder.items():
    action = data["T"] * data["E"] / pi
    log_a = math.log10(action)
    thunder[name]["action"] = action
    thunder[name]["log"] = log_a
    print(f"  {name:<25s}  T={data['T']:.2e}s  E={data['E']:.2e}J  Action/π={action:.2e}  log={log_a:.3f}")

all_subsystems["Thunderstorm"] = thunder

# ----- PREDATOR-PREY -----
print()
print("PREDATOR-PREY (lynx-hare, boreal Canada)")
print("-" * 60)

predprey = {}

# Vegetation growth cycle (seasonal)
# T: ~1 year (annual growth pulse)
# E: NPP (net primary productivity) for boreal forest
#   ~400 g C/m²/yr × 43 MJ/kg C × 1000 m²/hectare... 
#   For a 1000 km² study area: 10⁹ m² × 400 g/m² × 43 kJ/g = 1.72 × 10¹³ J
#   But this is for a specific spatial boundary
#   For a watershed (~100 km²): ~1.72 × 10¹² J
predprey["Vegetation annual"] = {
    "T": 3.156e7,         # 1 year in seconds
    "E": 1.72e12,         # ~1.72 TJ for 100 km² watershed
    "T_source": "Annual growing season",
    "E_source": "Boreal NPP ~400 gC/m²/yr (Chapin et al 2006)",
}

# Hare population subcycle
# T: ~3 years (hare population rises for ~3 yr of the 9.5 yr cycle)
# E: metabolic throughput of hare population
#   Peak density ~1500/km² (Krebs et al 2001), area 100 km²
#   ~150,000 hares × 150 kcal/day × 365 days/yr × 3 yr × 4184 J/kcal
#   = 150000 × 150 × 365 × 3 × 4184 ≈ 4.1 × 10¹³ J
predprey["Hare population rise"] = {
    "T": 9.46e7,          # 3 years
    "E": 4.1e13,          # ~41 TJ metabolic throughput
    "T_source": "Krebs et al 2001, hare increase phase",
    "E_source": "Hare population metabolic budget",
}

# Lynx population subcycle  
# T: ~4 years (lynx peaks ~1-2 yr after hare, full swing ~4 yr)
# E: metabolic throughput of lynx population
#   Peak ~30/km² (O'Donoghue et al 1997), area 100 km²
#   Wait, that's too high. Peak density ~15-30 per 100 km²
#   ~25 lynx × 2000 kcal/day × 365 × 4 × 4184
#   = 25 × 2000 × 365 × 4 × 4184 ≈ 3.1 × 10¹⁰ J
#   That seems low. Lynx metabolic rate ~800 kJ/day
#   25 × 8×10⁵ × 365 × 4 = 2.9 × 10¹⁰ J
predprey["Lynx population swing"] = {
    "T": 1.26e8,          # 4 years
    "E": 2.9e10,          # ~29 GJ metabolic throughput
    "T_source": "O'Donoghue et al 1997, lynx cycle phase",
    "E_source": "Lynx population metabolic budget",
}

# Full Lotka-Volterra cycle
# T: 9.5 years (3.0e8 s)
# E: total ecosystem metabolic throughput for full cycle
#   Vegetation + herbivore + predator over 9.5 years
#   Dominated by vegetation: ~1.72 TJ/yr × 9.5 yr = ~16 TJ
predprey["Full LV cycle"] = {
    "T": 3.0e8,           # 9.5 years
    "E": 1.6e13,          # ~16 TJ total ecosystem throughput
    "T_source": "Elton & Nicholson 1942, 9-10 yr cycle",
    "E_source": "Total ecosystem metabolic budget",
}

for name, data in predprey.items():
    action = data["T"] * data["E"] / pi
    log_a = math.log10(action)
    predprey[name]["action"] = action
    predprey[name]["log"] = log_a
    print(f"  {name:<25s}  T={data['T']:.2e}s  E={data['E']:.2e}J  Action/π={action:.2e}  log={log_a:.3f}")

all_subsystems["Predator-Prey"] = predprey

# =============================================================
# COMPUTE WITHIN-SYSTEM CONSECUTIVE GAPS
# =============================================================
print()
print("=" * 90)
print("WITHIN-SYSTEM CONSECUTIVE GAPS (TIGHTENED)")
print("=" * 90)
print()

target_4pi = math.log10(4 * math.pi)        # 1.0992
target_2pi_sq = math.log10((2 * math.pi)**2) # 1.5964

all_gaps = []

for sys_name, subsys in all_subsystems.items():
    items = sorted(subsys.items(), key=lambda x: x[1]["log"])
    print(f"{sys_name}:")
    for i in range(len(items) - 1):
        name_a = items[i][0]
        name_b = items[i+1][0]
        gap = items[i+1][1]["log"] - items[i][1]["log"]
        
        err_4pi = abs(gap - target_4pi) / target_4pi * 100
        err_2pi_sq = abs(gap - target_2pi_sq) / target_2pi_sq * 100
        
        if min(err_4pi, err_2pi_sq) < 30:
            best = "4π" if err_4pi < err_2pi_sq else "(2π)²"
            best_err = min(err_4pi, err_2pi_sq)
            symbol = "✓" if best_err < 12 else ("~" if best_err < 20 else "✗")
        else:
            best = "neither"
            best_err = min(err_4pi, err_2pi_sq)
            symbol = "✗"
            
        all_gaps.append((sys_name, f"{name_a} → {name_b}", gap))
        print(f"  {name_a:<25s} → {name_b:<25s}  gap = {gap:.4f}  → {best} ({best_err:.1f}%) {symbol}")
    print()

# Filter to gaps > 0.5 (meaningful scale jumps)
print("=" * 90)
print("GAPS > 0.5 orders of magnitude (meaningful scale jumps)")
print("=" * 90)
print()

big_gaps = [(s, l, g) for s, l, g in all_gaps if g > 0.5]
for s, l, g in big_gaps:
    err_4pi = abs(g - target_4pi) / target_4pi * 100
    err_2pi_sq = abs(g - target_2pi_sq) / target_2pi_sq * 100
    best = "4π" if err_4pi < err_2pi_sq else "(2π)²"
    best_err = min(err_4pi, err_2pi_sq)
    symbol = "✓" if best_err < 12 else ("~" if best_err < 20 else "✗")
    print(f"  {s:<15s}  {l:<55s}  gap = {g:.4f}  → {best} ({best_err:.1f}%) {symbol}")

print()
print(f"Total gaps > 0.5: {len(big_gaps)}")
gap_values = [g for _, _, g in big_gaps]
print(f"Gap values: {[f'{g:.3f}' for g in sorted(gap_values)]}")

