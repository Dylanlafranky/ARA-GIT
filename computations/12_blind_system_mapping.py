import math

pi = math.pi
phi = (1 + math.sqrt(5)) / 2

print("=" * 80)
print("BLIND SYSTEM MAPPING — Following the 15-Step Method")
print("=" * 80)
print()
print("Convention (locked): ARA = T_accumulation / T_release")
print("φ zone (sustained engine): ARA ≈ 1.618")
print("High ARA = slow charge, fast snap")
print()

# ================================================================
# SYSTEM 1: POWER GRID (AC electrical grid)
# ================================================================
print("═" * 80)
print("SYSTEM 1: ENERGY GRID (AC Power Grid)")
print("═" * 80)
print()

print("Step 1: Is it oscillatory?")
print("  Yes. AC power oscillates at 50/60 Hz. Voltage and current")
print("  cycle continuously. Supply-demand also oscillates (daily load curve).")
print()

print("Step 2: Ground cycle")
print("  Two candidates:")
print("  (a) The AC waveform: 50 Hz sinusoid (fundamental electrical oscillation)")
print("  (b) The daily load cycle: 24-hour demand oscillation")
print("  The AC waveform is the irreducible cycle — remove it and no power flows.")
print("  The daily load cycle is a higher-level modulation.")
print("  Ground cycle: AC waveform at 50 Hz (or 60 Hz).")
print()

print("Step 3: Lock phase direction")
print("  AC is sinusoidal — symmetric by design. Each half-cycle:")
print("  Accumulation: current builds from zero to peak (magnetic field stores energy)")
print("  Release: current falls from peak to zero (energy delivered to load)")
print("  For a pure sine wave: T_acc = T_rel = T/2 = 10 ms (at 50 Hz)")
print()

print("Step 4: Compute ARA")
ara_grid_ac = 10.0 / 10.0  # T_acc / T_rel for pure sine
print(f"  ARA (AC waveform) = T_acc / T_rel = 10ms / 10ms = {ara_grid_ac:.3f}")
print(f"  Zone: Near-symmetric (externally clocked)")
print(f"  This makes sense — the grid IS externally clocked by generators.")
print()

print("Step 5: Classify")
print("  ARA = 1.000 → Externally clocked / forced symmetry zone")
print("  Predictions:")
print("    - Requires external timing to maintain (generators enforce 50Hz) ✓")
print("    - Loses coherence if clock is disrupted (frequency drift → blackout)")
print("    - No self-timing ability — purely reactive")
print()

print("Step 6: Subsystems")
print("  (a) AC waveform: 50 Hz, ARA = 1.0")
print("  (b) Daily load cycle: 24hr, accumulation = demand ramp (morning),")
print("      release = demand fall (evening)")
print()

# Daily load cycle
# Demand ramps from ~4am to ~6pm (14 hours accumulation)
# Demand falls from ~6pm to ~4am (10 hours release)
t_acc_daily = 14 * 3600  # 14 hours in seconds
t_rel_daily = 10 * 3600  # 10 hours in seconds
ara_daily = t_acc_daily / t_rel_daily
print(f"  Daily load cycle ARA = {t_acc_daily/3600:.0f}hr / {t_rel_daily/3600:.0f}hr = {ara_daily:.2f}")
print(f"  Zone: Sustained engine / managed ({ara_daily:.2f})")
print()

print("Step 8-10: Period and Action/π")
print()

# AC waveform
T_ac = 1/50  # 20 ms at 50 Hz
# Energy per cycle: power delivered per cycle
# Typical grid: 1 GW power station
# Energy per cycle = Power × Period = 1e9 × 0.02 = 2e7 J
E_ac = 1e9 * T_ac  # 20 MJ per cycle for 1 GW
action_ac = T_ac * E_ac / pi
log_ac = math.log10(action_ac)
print(f"  AC waveform (per 1 GW station):")
print(f"    T = {T_ac:.4f} s")
print(f"    E = {E_ac:.2e} J (power × period)")
print(f"    Action/π = {action_ac:.2e} J·s")
print(f"    log₁₀ = {log_ac:.2f}")
print()

# Daily load cycle
T_daily = 86400  # 24 hours
# Energy oscillation: difference between peak and trough demand
# Peak ~40 GW, trough ~20 GW, average ~30 GW
# Energy that OSCILLATES = (Peak - Trough) × half-period
# = 20 GW × 12 hr = 20e9 × 43200 = 8.64e14 J ≈ 10^15 J
E_daily = 20e9 * 43200  # ~8.6e14 J
action_daily = T_daily * E_daily / pi
log_daily = math.log10(action_daily)
print(f"  Daily load cycle:")
print(f"    T = {T_daily} s")
print(f"    E = {E_daily:.2e} J (demand oscillation amplitude)")
print(f"    Action/π = {action_daily:.2e} J·s")
print(f"    log₁₀ = {log_daily:.2f}")
print()

# ================================================================
# SYSTEM 2: RAYLEIGH-BÉNARD CONVECTION CELLS
# ================================================================
print("═" * 80)
print("SYSTEM 2: RAYLEIGH-BÉNARD CONVECTION CELLS")
print("═" * 80)
print()

print("Step 1: Is it oscillatory?")
print("  Yes — but subtly. Once established, the cells are STEADY-STATE rolls.")
print("  However, they oscillate during:")
print("  (a) Cell formation (instability → roll establishment)")
print("  (b) Oscillatory convection (above a second critical Rayleigh number)")
print("  At high Ra, cells oscillate: hot plumes rise, cool, sink, repeat.")
print("  Ground cycle: one convective overturn (plume rises, cools, sinks).")
print()

print("Step 2: Ground cycle")
print("  One complete convective overturn: hot fluid rises from bottom,")
print("  reaches top, cools, sinks back down.")
print()

print("Step 3: Lock phase direction")
print("  Accumulation: fluid heats at bottom boundary, building buoyancy.")
print("    Thermal energy stores as the thermal boundary layer thickens.")
print("  Release: buoyant plume detaches and rises. Energy converts from")
print("    thermal (potential) to kinetic (convective motion).")
print()

print("Step 4: Compute ARA")
# In oscillatory RB convection:
# The heating (accumulation) is continuous from below — it takes time for
# the boundary layer to become unstable (this is T_acc).
# The plume eruption (release) is relatively fast.
# Typical: boundary layer builds over ~0.7 of the cycle, plume erupts in ~0.3
# (This varies with Rayleigh number)
t_acc_rb = 0.7  # fraction of cycle
t_rel_rb = 0.3  # fraction of cycle
ara_rb = t_acc_rb / t_rel_rb
print(f"  ARA = T_acc / T_rel ≈ 0.7T / 0.3T = {ara_rb:.2f}")
print(f"  Zone: Exothermic / near-2.0 territory")
print(f"  (boundary layer builds slowly, plume erupts fast)")
print()

# Wait — let me reconsider. In steady-state RB rolls, the circulation is
# roughly symmetric (fluid goes up on one side, down on the other).
# In OSCILLATORY RB (above Ra_c2), there IS asymmetry.
# Actually, for a single plume cycle:
# Heating phase: thermal diffusion timescale ~ d²/κ
# Rising phase: convective timescale ~ d/v
# For typical lab RB: d = 1cm, κ = 1.5e-7 m²/s (water), v ~ 1 mm/s
# T_diff ~ (0.01)²/1.5e-7 = 667 s (very long!)
# T_conv ~ 0.01/0.001 = 10 s
# ARA ~ 667/10 = 67! That's an extreme snap in our inverted convention.

# Wait no — with new convention ARA = T_acc/T_rel
# T_acc = heating time = long
# T_rel = plume rise = short  
# ARA = 667/10 = 67 → very high ARA = slow charge, fast release
# That's... outside the 0-2 scale. Same territory as lightning.
# But that can't be right for a sustained convection cell.

# Let me reconsider what the "cycle" is.
# In STEADY convection rolls: the circulation IS the system. Fluid goes
# around in a loop. There's no clear acc/rel — it's continuous.
# ARA ≈ 1.0 (symmetric circulation)

# In OSCILLATORY convection: plumes detach periodically.
# The cycle is: build boundary layer (slow) → detach plume (fast) → repeat
# This IS asymmetric. But the "release" includes the plume rising AND 
# cooling AND sinking — that's most of the cycle.
# More accurately:
# Accumulation: boundary layer thickens (thermal diffusion, slow)
# Release: plume detaches, rises, delivers heat to top, fluid sinks
# The release is actually the LONGER phase (the whole convective loop)
# Accumulation is just the boundary layer rebuild.

# For oscillatory RB with period ~100s in a lab setup:
# Boundary layer rebuild: ~30s (accumulation)
# Convective overturn: ~70s (release — plume rise + cool + sink)
# ARA = 30/70 = 0.43

print("  CORRECTION: Reconsidering the phase assignment.")
print("  Accumulation = boundary layer heating (waiting for instability)")
print("  Release = convective overturn (plume rise + cool + sink)")
print("  For oscillatory RB in lab (period ~100s):")
t_acc_rb2 = 30  # seconds, boundary layer rebuild
t_rel_rb2 = 70  # seconds, overturn
ara_rb2 = t_acc_rb2 / t_rel_rb2
print(f"  ARA = {t_acc_rb2}s / {t_rel_rb2}s = {ara_rb2:.2f}")
print(f"  Zone: Snap/consumer (ARA < 0.5)")
print(f"  Prediction: System 'consumes' external heat input, releases in")
print(f"  a longer convective phase. Sensitive to input disruption.")
print()

# Alternative: steady-state rolls
print("  Alternative (steady-state rolls, not oscillatory):")
print("  ARA ≈ 1.0 (symmetric circulation, externally driven by ΔT)")
print("  This makes more sense for classical RB cells.")
print()

# Use the steady-state interpretation for now
ara_rb_final = 1.0  # symmetric rolls

print("Step 8-10: Period and Action/π")
# Lab-scale RB: cell diameter ~1 cm, period of circulation ~10-100s
# Energy: kinetic energy of the flow + thermal energy transported
# For a lab cell (1cm × 1cm × 1cm, water):
# Velocity ~1 mm/s, mass ~1g
# KE = 0.5 × 0.001 × (0.001)² = 5e-10 J (tiny!)
# Thermal energy transported per cycle: 
# Q = k×A×ΔT/d × period = 0.6 × 1e-4 × 10 / 0.01 × 30 = 0.018 J
# The energy that oscillates is the thermal transport per overturn
T_rb = 30  # seconds for one overturn
E_rb = 0.02  # ~20 mJ thermal transport per overturn (lab scale)
action_rb = T_rb * E_rb / pi
log_rb = math.log10(action_rb)
print(f"  Lab-scale RB cell:")
print(f"    T = {T_rb} s")
print(f"    E = {E_rb} J (thermal energy transported per overturn)")
print(f"    Action/π = {action_rb:.4f} J·s")
print(f"    log₁₀ = {log_rb:.2f}")
print()

# Atmospheric-scale RB (like Hadley cells): much larger
T_rb_atm = 30 * 86400  # ~30 days for atmospheric cell overturn
E_rb_atm = 1e18  # ~10^18 J (major atmospheric circulation energy)
action_rb_atm = T_rb_atm * E_rb_atm / pi
log_rb_atm = math.log10(action_rb_atm)
print(f"  Atmospheric-scale (Hadley cell):")
print(f"    T = {T_rb_atm:.2e} s (~30 days)")
print(f"    E = {E_rb_atm:.2e} J")
print(f"    Action/π = {action_rb_atm:.2e} J·s")
print(f"    log₁₀ = {log_rb_atm:.2f}")
print()

# ================================================================
# SYSTEM 3: HONEYBEE COLONY
# ================================================================
print("═" * 80)
print("SYSTEM 3: HONEYBEE COLONY")
print("═" * 80)
print()

print("Step 1: Is it oscillatory?")
print("  Yes — multiple oscillations:")
print("  (a) Daily foraging cycle: bees leave at dawn, return by dusk")
print("  (b) Annual colony cycle: spring buildup → summer peak → winter cluster")
print("  (c) Brood cycle: egg → larva → pupa → adult (~21 days for workers)")
print("  (d) Thermoregulation: heating/cooling the hive ±0.5°C around 35°C")
print()

print("Step 2: Ground cycle")
print("  The ANNUAL colony cycle is the ground cycle for the colony-as-organism.")
print("  Remove it (prevent seasonal variation) and the colony structure")
print("  breaks down — no swarming, no queen replacement, no winter prep.")
print("  Ground cycle: annual population/resource cycle (~1 year).")
print()

print("Step 3: Lock phase direction")
print("  Accumulation: Spring → Summer. Colony builds population,")
print("    stores honey, accumulates resources. ~7 months (March-September).")
print("  Release: Autumn → Winter. Colony contracts, consumes stores,")
print("    population drops. ~5 months (October-February).")
print()

print("Step 4: Compute ARA")
t_acc_bee = 7  # months (spring-summer buildup)
t_rel_bee = 5  # months (autumn-winter contraction)
ara_bee = t_acc_bee / t_rel_bee
print(f"  ARA = {t_acc_bee} months / {t_rel_bee} months = {ara_bee:.2f}")
print(f"  Zone: Sustained engine (ARA = 1.4, in the managed/engine zone)")
print()

print("Step 5: Classify")
print(f"  ARA = {ara_bee:.2f} → Sustained engine / managed zone (1.2-1.7)")
print(f"  Predictions:")
print(f"    - Self-organising (no external controller needed) ✓")
print(f"    - Resource-efficient (accumulation exceeds release = net storage)")
print(f"    - Robust to perturbation (can survive partial resource loss)")
print(f"    - Near φ → system has evolved toward optimal time-packing")
print()

print("Step 6: Subsystems")
print("  (a) Annual colony cycle — ground cycle, ARA = 1.40")
print("  (b) Daily foraging cycle (dawn departure → dusk return)")
t_acc_forage = 2   # hours before first foraging (warming, scouting)
t_rel_forage = 10  # hours of active foraging
ara_forage = t_acc_forage / t_rel_forage
print(f"      T_acc = ~2hr (warm up, scout), T_rel = ~10hr (foraging)")
print(f"      ARA = {ara_forage:.2f} — consumer/snap zone")
print(f"      (Quick prep, long active phase — makes sense for foraging)")
print()

print("  (c) Brood cycle (21 days: egg 3d, larva 6d, pupa 12d)")
# Accumulation: egg + larva feeding (9 days, building the organism)
# Release: metamorphosis + emergence (12 days, transformation to adult)
t_acc_brood = 9  # days (egg + larva)
t_rel_brood = 12  # days (pupa → emergence)
ara_brood = t_acc_brood / t_rel_brood
print(f"      T_acc = 9 days (egg+larva), T_rel = 12 days (pupa+emerge)")
print(f"      ARA = {ara_brood:.2f} — near-symmetric / slightly snap")
print()

print("  (d) Thermoregulation cycle (~minutes)")
# Hive temp oscillates ±0.5°C around 35°C
# Heating phase: bees shiver (accumulate heat) ~3-5 min
# Cooling phase: bees fan/evaporate (release heat) ~2-3 min
t_acc_therm = 4  # minutes (heating)
t_rel_therm = 2.5  # minutes (cooling)
ara_therm = t_acc_therm / t_rel_therm
print(f"      T_acc = ~4 min (heating), T_rel = ~2.5 min (cooling)")
print(f"      ARA = {ara_therm:.2f} — sustained engine zone!")
print(f"      (Thermoregulation is itself a φ-adjacent engine)")
print()

print("Step 8-10: Period and Action/π")
print()

# Annual colony cycle
T_bee_annual = 365.25 * 86400  # 1 year in seconds
# Energy: total honey production per year for one colony
# A healthy colony produces ~25-30 kg honey surplus + ~90 kg consumed
# Total: ~120 kg honey × 3000 kcal/kg × 4184 J/kcal = 1.5e9 J
# But what OSCILLATES is the difference between peak and trough:
# Summer stores ~30 kg honey = 3.8e8 J stored, consumed over winter
E_bee_annual = 3.8e8  # ~380 MJ (honey energy that accumulates then depletes)
action_bee_annual = T_bee_annual * E_bee_annual / pi
log_bee_annual = math.log10(action_bee_annual)
print(f"  Annual colony cycle:")
print(f"    T = {T_bee_annual:.2e} s (1 year)")
print(f"    E = {E_bee_annual:.2e} J (honey energy stored/consumed)")
print(f"    Action/π = {action_bee_annual:.2e} J·s")
print(f"    log₁₀ = {log_bee_annual:.2f}")
print()

# Daily foraging
T_bee_daily = 86400  # 24 hours
# Energy from daily nectar collection: ~1 kg nectar/day × 3000 kcal/kg × 0.3 conversion
# Actually: colony brings in ~1 kg nectar → ~0.3 kg honey/day during peak
# Energy: 0.3 kg × 3000 kcal/kg × 4184 = 3.8e6 J
# What oscillates: energy leaves as bee metabolism for foraging (~50,000 bees × 
# 0.5 mJ per flight-hour × 10 hours = ~2.5e5 J), energy returns as nectar.
# Net oscillation: ~10^6 J in and out per day
E_bee_daily = 1e6  # ~1 MJ oscillates between hive and field
action_bee_daily = T_bee_daily * E_bee_daily / pi
log_bee_daily = math.log10(action_bee_daily)
print(f"  Daily foraging cycle:")
print(f"    T = {T_bee_daily} s (24 hours)")
print(f"    E = {E_bee_daily:.2e} J (nectar energy flow)")
print(f"    Action/π = {action_bee_daily:.2e} J·s")
print(f"    log₁₀ = {log_bee_daily:.2f}")
print()

# Thermoregulation
T_bee_therm = (t_acc_therm + t_rel_therm) * 60  # ~6.5 min in seconds
# Energy: heating a hive by 0.5°C
# Hive thermal mass: ~30 kg (wax, bees, honey) × 2000 J/kg·K × 0.5°C = 30,000 J? 
# No, that's too much. The oscillation is only ±0.5°C of a small volume.
# Active heating zone ~5 kg × 3000 J/kg·K × 0.5 = 7500 J
# More realistic: individual bee cluster ~1000 bees shivering
# Each bee ~0.1 W × 4 min = 24 J per bee × 1000 = 24,000 J? 
# Published: hive metabolic heat production ~30-80 W continuous
# Oscillation amplitude: ~30 W × 6.5 min ≈ 12,000 J? That's total, not oscillation.
# The oscillation is maybe ±5W around a mean → 5W × 390s = ~2000 J
E_bee_therm = 2000  # ~2 kJ thermal oscillation
action_bee_therm = T_bee_therm * E_bee_therm / pi
log_bee_therm = math.log10(action_bee_therm)
print(f"  Thermoregulation cycle:")
print(f"    T = {T_bee_therm:.0f} s (~6.5 min)")
print(f"    E = {E_bee_therm} J (thermal oscillation)")
print(f"    Action/π = {action_bee_therm:.2e} J·s")
print(f"    log₁₀ = {log_bee_therm:.2f}")
print()

# ================================================================
# SUMMARY TABLE
# ================================================================
print("═" * 80)
print("SUMMARY: ALL THREE SYSTEMS ON THE ACTION SPECTRUM")
print("═" * 80)
print()
print(f"{'System':<35s} {'ARA':<8s} {'T (s)':<12s} {'E (J)':<12s} {'Action/π':<12s} {'log₁₀':<8s}")
print("-" * 90)

systems = [
    ("Energy Grid — AC waveform", f"{ara_grid_ac:.2f}", T_ac, E_ac, action_ac, log_ac),
    ("Energy Grid — Daily load", f"{ara_daily:.2f}", T_daily, E_daily, action_daily, log_daily),
    ("RB Convection — Lab cell", f"~1.0", T_rb, E_rb, action_rb, log_rb),
    ("RB Convection — Atmospheric", f"~1.0", T_rb_atm, E_rb_atm, action_rb_atm, log_rb_atm),
    ("Honeybee — Annual colony", f"{ara_bee:.2f}", T_bee_annual, E_bee_annual, action_bee_annual, log_bee_annual),
    ("Honeybee — Daily foraging", f"{ara_forage:.2f}", T_bee_daily, E_bee_daily, action_bee_daily, log_bee_daily),
    ("Honeybee — Thermoregulation", f"{ara_therm:.2f}", T_bee_therm, E_bee_therm, action_bee_therm, log_bee_therm),
]

for name, ara, T, E, action, log_a in systems:
    print(f"{name:<35s} {ara:<8s} {T:<12.2e} {E:<12.2e} {action:<12.2e} {log_a:<8.2f}")

print()
print("CLUSTER PLACEMENT:")
print(f"  Energy Grid AC:       log {log_ac:.1f}  → Human cluster")
print(f"  Energy Grid Daily:    log {log_daily:.1f} → Macro cluster")
print(f"  RB Lab cell:          log {log_rb:.1f}  → Human cluster (barely)")
print(f"  RB Atmospheric:       log {log_rb_atm:.1f} → Macro cluster")
print(f"  Honeybee Annual:      log {log_bee_annual:.1f} → Macro cluster")
print(f"  Honeybee Daily:       log {log_bee_daily:.1f} → Mesoscale cluster")
print(f"  Honeybee Thermo:      log {log_bee_therm:.1f}  → Human cluster")
print()
print("NOTE: These are first-pass estimates. Energy values need")
print("cross-referencing with published literature for confirmation.")

