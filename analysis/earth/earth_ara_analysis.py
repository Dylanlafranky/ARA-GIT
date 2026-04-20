"""
Earth System ARA Analysis — Blind Prediction Test
===================================================
Decompose the Earth into 10 coupled subsystems operating across
timescales from hours to hundreds of thousands of years.
Compute ARA ratios from climate science / geophysics literature.
Make failure-mode predictions based ONLY on ARA theory.
Then validate against known climate tipping points and geophysical phenomena.

Data sources cited per subsystem.
"""

import json

PHI = 1.6180339887

# ============================================================
# STEP 1: Define subsystems with phase durations
# ============================================================

subsystems = {
    "Diurnal Thermal Cycle": {
        "description": "Daily heating/cooling of Earth's surface and lower atmosphere",
        "accumulation_label": "Solar heating (sunrise → peak temperature ~3-5 PM)",
        "release_label": "Radiative cooling (peak temperature → sunrise next day)",
        "T_accumulation": 9,    # hours: ~6 AM to ~3 PM
        "T_release": 15,        # hours: ~3 PM to ~6 AM next day
        "time_unit": "hours",
        "source": "OpenSnow diurnal heating; Wikipedia diurnal temperature variation; Met Office",
        "notes": "Peak temperature lags solar noon by 2-4 hours (thermal inertia). Cooling phase is nearly twice as long as heating."
    },
    "Tidal Cycle": {
        "description": "Gravitational tidal rise and fall in coastal waters",
        "accumulation_label": "Flood tide (rising water, gravitational accumulation)",
        "release_label": "Ebb tide (falling water, gravitational release)",
        "T_accumulation": 5.0,  # hours: flood tide in typical coastal setting
        "T_release": 7.2,      # hours: ebb tide typically longer (flood-dominant asymmetry)
        "time_unit": "hours",
        "source": "Coastal Wiki tidal asymmetry; Libretexts coastal dynamics 5.7.4; NOAA tidal currents",
        "notes": "Flood-dominant systems: shorter flood, longer ebb. Ratio varies by estuary. Using well-documented coastal values."
    },
    "Atmospheric Water Cycle": {
        "description": "Water evaporation, atmospheric residence, and precipitation",
        "accumulation_label": "Evaporation + atmospheric transport + condensation",
        "release_label": "Precipitation event (rain/snow)",
        "T_accumulation": 9,    # days: average atmospheric residence time ~9-10 days
        "T_release": 0.5,      # days: typical precipitation event ~6-12 hours
        "time_unit": "days",
        "source": "NOAA water cycle education; USGS water science; Wikipedia water cycle",
        "notes": "Water spends ~9-10 days in atmosphere. Precipitation events last hours. Extreme snap — long accumulation, fast release."
    },
    "ENSO (El Nino / La Nina)": {
        "description": "Pacific Ocean heat accumulation and release cycle",
        "accumulation_label": "La Nina: trade wind buildup, subsurface heat recharge",
        "release_label": "El Nino: heat release, trade wind collapse",
        "T_accumulation": 2.5,  # years: La Nina phase (often multi-year, 2-3 years typical)
        "T_release": 1.5,      # years: El Nino phase (typically 9-18 months)
        "time_unit": "years",
        "source": "NOAA Climate.gov; Li 2024 GRL ENSO asymmetry; existing ARA ENSO analysis",
        "notes": "La Nina often multi-year (accumulation extends). El Nino terminates rapidly. Period 2-7 years total."
    },
    "Seasonal Thermal Cycle": {
        "description": "Annual warming and cooling cycle (Northern Hemisphere midlatitudes)",
        "accumulation_label": "Warming (temperature minimum ~Jan 25 → peak ~Jul 25)",
        "release_label": "Cooling (temperature peak ~Jul 25 → minimum ~Jan 25)",
        "T_accumulation": 181,  # days: late January to late July (~6 months)
        "T_release": 184,       # days: late July to late January (~6 months)
        "time_unit": "days",
        "source": "Wikipedia Seasonal lag; NOAA; Wang 2021 GRL changing season lengths",
        "notes": "CORRECTED: Previous version used equinox (Mar 20) as temperature minimum — wrong. Actual NH temperature minimum is late January (seasonal lag from ocean thermal inertia). Warming and cooling phases are nearly symmetric."
    },
    "Carbon Cycle (Ocean-Atmosphere)": {
        "description": "CO2 exchange between atmosphere and ocean surface/biosphere",
        "accumulation_label": "CO2 absorption by ocean surface + biosphere (drawdown)",
        "release_label": "CO2 outgassing + respiration (release back to atmosphere)",
        "T_accumulation": 4,    # years: ocean surface equilibration timescale
        "T_release": 50,        # years: atmospheric CO2 adjustment time (50-200 years for perturbation decay)
        "time_unit": "years",
        "source": "Archer 2009 Ann Rev; ScienceDirect Harde 2017; NASA Earth Observatory carbon cycle",
        "notes": "Ocean ABSORBS faster than atmosphere CLEARS. A perturbation (e.g. fossil fuel pulse) takes 50-200 years to decay. Using conservative 50yr."
    },
    "Volcanic Cycle": {
        "description": "Magma chamber pressure accumulation and eruption release",
        "accumulation_label": "Magma chamber recharge (pressure + volatiles build)",
        "release_label": "Eruption (explosive/effusive release)",
        "T_accumulation": 100,  # years: typical recharge for explosive stratovolcano (15-100yr range)
        "T_release": 0.02,     # years: ~1 week typical eruption duration (hours to weeks)
        "time_unit": "years",
        "source": "NAP Volcanic Eruptions; Popocatepetl recharge study (Geology 2022); Kolumbo chamber study",
        "notes": "Extreme snap. Decades-centuries of recharge, hours-weeks of eruption. Most extreme ARA ratio in the Earth system."
    },
    "Thermohaline Circulation (AMOC)": {
        "description": "Atlantic deep water formation, deep transport, and upwelling return",
        "accumulation_label": "Deep water formation + southward transport (cooling, sinking)",
        "release_label": "Upwelling + surface return flow (warming, rising)",
        "T_accumulation": 600,  # years: deep water transit (NADW formation to deep Atlantic ~600yr)
        "T_release": 400,       # years: upwelling return via Southern Ocean + surface northward flow
        "time_unit": "years",
        "source": "Wikipedia AMOC; Britannica AMOC; Kuhlbrodt 2007 Reviews of Geophysics",
        "notes": "Full circuit ~1000 years. Deep sinking is slow and density-driven. Return flow faster (wind-driven upwelling). Ratio approximate — deep ocean mixing poorly constrained."
    },
    "Milankovitch / Ice Age Cycle": {
        "description": "Glaciation-deglaciation cycle driven by orbital forcing",
        "accumulation_label": "Glaciation: slow ice sheet growth over ~90,000 years",
        "release_label": "Deglaciation: rapid ice sheet collapse over ~10,000 years",
        "T_accumulation": 90,   # kyr: slow glaciation
        "T_release": 10,        # kyr: rapid deglaciation (the sawtooth)
        "time_unit": "thousand years (kyr)",
        "source": "NASA Milankovitch; Wikipedia Milankovitch cycles; RealClimate Puzzling Pleistocene",
        "notes": "The famous sawtooth: slow ramp up, fast crash down. ~100 kyr cycle since 800 kya. The asymmetry itself is unexplained by orbital forcing alone."
    },
    "Geomagnetic Dynamo": {
        "description": "Earth's magnetic field: stable polarity period → reversal transition",
        "accumulation_label": "Stable polarity (dipole field maintained, ~200-450 kyr)",
        "release_label": "Polarity reversal transition (~2-12 kyr)",
        "T_accumulation": 300,  # kyr: average stable period between reversals (~240-450 kyr)
        "T_release": 7,         # kyr: typical reversal transition duration (2-12 kyr)
        "time_unit": "thousand years (kyr)",
        "source": "Wikipedia geomagnetic reversal; Nature 2005 structural requirements; 183 reversals in 83 Myr",
        "notes": "Extreme snap at geological timescale. Long stability, short chaotic transition. Aperiodic — appears random."
    }
}

# ============================================================
# STEP 2: Compute ARA ratios
# ============================================================

print("=" * 90)
print("EARTH SYSTEM ARA ANALYSIS — BLIND PREDICTION TEST")
print("=" * 90)
print(f"\nSubsystems: {len(subsystems)}")
print(f"Timescale range: hours (tidal) to hundreds of thousands of years (Milankovitch)")
print()

results = {}
for name, data in subsystems.items():
    ara = data["T_release"] / data["T_accumulation"]

    # Classify on ARA scale
    if ara < 0.02:
        classification = "Ultra-extreme snap"
        zone = "ultra_snap"
    elif ara < 0.15:
        classification = "Extreme snap (trigger)"
        zone = "trigger"
    elif ara < 0.4:
        classification = "Consumer snap"
        zone = "consumer_snap"
    elif ara < 0.8:
        classification = "Consumer"
        zone = "consumer"
    elif 0.8 <= ara < 1.15:
        classification = "Pacemaker / forced symmetry"
        zone = "pacemaker"
    elif 1.15 <= ara < 1.45:
        classification = "Shock absorber / managed"
        zone = "managed"
    elif 1.45 <= ara < 1.75:
        classification = "Sustained engine (phi zone)"
        zone = "phi"
    elif 1.75 <= ara < 2.2:
        classification = "Exothermic source"
        zone = "exothermic"
    else:
        classification = "Beyond scale"
        zone = "extreme"

    phi_deviation = abs(ara - PHI) / PHI * 100

    results[name] = {
        **data,
        "ARA": round(ara, 4),
        "classification": classification,
        "zone": zone,
        "phi_deviation": round(phi_deviation, 1)
    }

# Print results table
print(f"{'Subsystem':<40} {'T_acc':>8} {'T_rel':>8} {'Unit':<10} {'ARA':>8} {'Classification':<30}")
print("-" * 110)
for name, r in results.items():
    print(f"{name:<40} {r['T_accumulation']:>8} {r['T_release']:>8} {r['time_unit']:<10} {r['ARA']:>8.4f} {r['classification']:<30}")

# ============================================================
# STEP 3: BLIND PREDICTIONS (from ARA theory alone)
# ============================================================

print("\n" + "=" * 90)
print("BLIND PREDICTIONS — Based only on ARA theory")
print("=" * 90)

predictions = {
    "Diurnal Thermal Cycle": {
        "ARA": results["Diurnal Thermal Cycle"]["ARA"],
        "prediction": (
            "SUSTAINED ENGINE / phi ZONE (ARA = 1.667). Within 3% of phi.\n"
            "  This is a free-running, self-organising thermal oscillator — not clock-forced\n"
            "  (the Sun sets the energy input, but thermal inertia determines the phase split).\n"
            "  ARA theory predicts:\n"
            "  1. This ratio should be STABLE and SELF-CORRECTING under perturbation\n"
            "  2. Disruption of this ratio (e.g. losing the thermal lag) would destabilise\n"
            "     local climate — the system would overheat faster and cool less efficiently\n"
            "  3. Urban heat islands, deforestation, or albedo changes that shift the\n"
            "     heating/cooling asymmetry should produce measurable climate effects"
        )
    },
    "Tidal Cycle": {
        "ARA": results["Tidal Cycle"]["ARA"],
        "prediction": (
            "SHOCK ABSORBER / MANAGED (ARA = 1.440).\n"
            "  Gravitationally forced but modified by coastal geometry.\n"
            "  1. The asymmetry is maintained by the interaction between forcing and friction —\n"
            "     a managed/damped system, not free-running\n"
            "  2. Changes in coastal geometry (sea level rise, land subsidence) should shift\n"
            "     the flood/ebb ratio, potentially crossing thresholds\n"
            "  3. Sediment transport is coupled to this ratio — shifts in ARA should\n"
            "     change erosion/deposition patterns"
        )
    },
    "Atmospheric Water Cycle": {
        "ARA": results["Atmospheric Water Cycle"]["ARA"],
        "prediction": (
            "EXTREME SNAP (ARA = 0.056). 9 days of accumulation, 12 hours of release.\n"
            "  Classic trigger/snap — long slow buildup, violent fast release.\n"
            "  1. If ARA increases (precipitation events become longer/weaker relative to\n"
            "     accumulation), expect persistent drizzle replacing distinct storm events\n"
            "  2. If ARA decreases further (even more extreme snap), expect more violent,\n"
            "     concentrated precipitation — flash floods, extreme storm intensity\n"
            "  3. Climate warming adds energy to accumulation phase — ARA theory predicts\n"
            "     this should make the snap MORE extreme (shorter, more violent release)"
        )
    },
    "ENSO (El Nino / La Nina)": {
        "ARA": results["ENSO (El Nino / La Nina)"]["ARA"],
        "prediction": (
            "CONSUMER (ARA = 0.600).\n"
            "  Moderate asymmetry — accumulates longer than it releases.\n"
            "  1. If ARA approaches 1.0 (El Nino duration approaches La Nina duration),\n"
            "     the system loses its asymmetric character — neutral periods compress\n"
            "  2. Multi-year La Nina events (extended accumulation) push ARA further below\n"
            "     phi — the system becomes more consumer-like, more snap-prone\n"
            "  3. The coupling to other subsystems (seasonal cycle, thermohaline) should\n"
            "     amplify perturbations — a strong El Nino disrupts downstream ARA ratios"
        )
    },
    "Seasonal Thermal Cycle": {
        "ARA": results["Seasonal Thermal Cycle"]["ARA"],
        "prediction": (
            "PACEMAKER / FORCED SYMMETRY (ARA = 1.017). Nearly symmetric — externally forced.\n"
            "  The seasonal cycle is driven by axial tilt (external forcing), not self-organisation.\n"
            "  1. Near-perfect symmetry (ARA ≈ 1.0) is the signature of a forced oscillator:\n"
            "     the warming and cooling phases are nearly equal because the tilt-driven\n"
            "     insolation cycle is symmetric. Ocean thermal inertia creates a slight asymmetry.\n"
            "  2. Because this is FORCED (not free-running), it cannot self-correct if the\n"
            "     forcing environment changes. Greenhouse gas changes break the symmetry.\n"
            "  3. The seasonal cycle is the boundary condition for most biological rhythms —\n"
            "     perturbation here cascades into agriculture, ecosystems, and migration patterns.\n"
            "  4. Under climate change, the warming/cooling balance shifts — seasons arrive\n"
            "     earlier, persist differently, and amplify unevenly."
        )
    },
    "Carbon Cycle (Ocean-Atmosphere)": {
        "ARA": results["Carbon Cycle (Ocean-Atmosphere)"]["ARA"],
        "prediction": (
            "BEYOND SCALE (ARA = 12.500). Massively release-dominant.\n"
            "  The atmosphere clears CO2 far slower than the ocean absorbs it.\n"
            "  1. This extreme ratio means perturbations PERSIST — any pulse of CO2\n"
            "     is absorbed relatively quickly but takes decades-centuries to decay\n"
            "  2. ARA >> 2.0 means the system is in chronic resonant overload — past\n"
            "     perturbations are still decaying when new ones arrive\n"
            "  3. The system has no self-correcting phi-optimal ratio — it's a one-way\n"
            "     ratchet. Each perturbation stacks on the undecayed tail of the last.\n"
            "  4. PREDICTION: This subsystem should be the Earth's most dangerous\n"
            "     failure mode — and the hardest to reverse once perturbed."
        )
    },
    "Volcanic Cycle": {
        "ARA": results["Volcanic Cycle"]["ARA"],
        "prediction": (
            "ULTRA-EXTREME SNAP (ARA = 0.0002). The most extreme ratio in the system.\n"
            "  Centuries of accumulation, hours-weeks of release.\n"
            "  1. This is a pure trigger — the system has essentially zero 'release'\n"
            "     compared to its accumulation. When it fires, it fires catastrophically.\n"
            "  2. ARA theory predicts longer recharge periods produce more violent release\n"
            "     (more accumulated energy). Supervolcanoes (longest recharge) should produce\n"
            "     the most extreme events.\n"
            "  3. The system couples to atmosphere, climate, and biosphere through the\n"
            "     eruption — a single snap event cascades through multiple other subsystems."
        )
    },
    "Thermohaline Circulation (AMOC)": {
        "ARA": results["Thermohaline Circulation (AMOC)"]["ARA"],
        "prediction": (
            "CONSUMER (ARA = 0.667).\n"
            "  Deep water sinks slowly, returns somewhat faster via wind-driven upwelling.\n"
            "  1. If ARA decreases (return flow weakens), the circulation slows —\n"
            "     less heat is transported northward\n"
            "  2. If fresh water input disrupts deep water formation (reducing accumulation\n"
            "     rate), the entire cycle can stall — ARA approaches undefined (no cycle)\n"
            "  3. A stalled AMOC means the coupling to surface temperature, seasonal cycle,\n"
            "     and carbon cycle all break simultaneously — a cascade failure\n"
            "  4. The 1000-year timescale means recovery from perturbation is SLOW —\n"
            "     once disrupted, the system stays disrupted for centuries"
        )
    },
    "Milankovitch / Ice Age Cycle": {
        "ARA": results["Milankovitch / Ice Age Cycle"]["ARA"],
        "prediction": (
            "EXTREME SNAP (ARA = 0.111). Classic consumer snap — long slow buildup,\n"
            "  fast violent release (the sawtooth pattern).\n"
            "  1. 90,000 years of ice accumulation, 10,000 years of collapse.\n"
            "     The system is a loaded spring that snaps.\n"
            "  2. ARA theory predicts the deglaciation should be SELF-AMPLIFYING —\n"
            "     once release begins, positive feedbacks accelerate it (albedo feedback,\n"
            "     CO2 release from warming oceans)\n"
            "  3. The snap character means the system is BINARY — it's either accumulating\n"
            "     or collapsing. There's no stable intermediate state.\n"
            "  4. We are currently ~11,700 years into an interglacial. The system is in\n"
            "     its release/plateau phase."
        )
    },
    "Geomagnetic Dynamo": {
        "ARA": results["Geomagnetic Dynamo"]["ARA"],
        "prediction": (
            "EXTREME SNAP (ARA = 0.023). Long stability, brief chaotic reversal.\n"
            "  1. The field maintains polarity for hundreds of thousands of years,\n"
            "     then flips in a few thousand years — a geological trigger.\n"
            "  2. ARA theory predicts the reversal should be preceded by field weakening\n"
            "     (the system accumulates instability before the snap)\n"
            "  3. The aperiodic nature (random timing) is consistent with a threshold-driven\n"
            "     system, not a clock-driven one — the dynamo fires when conditions cross\n"
            "     a critical threshold, not on a schedule.\n"
            "  4. During reversal (the snap), the field is weakened/chaotic — the system\n"
            "     loses its protective function temporarily."
        )
    }
}

for name, pred in predictions.items():
    print(f"\n{'─' * 70}")
    print(f"  {name} (ARA = {pred['ARA']})")
    print(f"{'─' * 70}")
    print(f"  {pred['prediction']}")

# ============================================================
# STEP 4: Define coupling network
# ============================================================

print("\n" + "=" * 90)
print("COUPLING NETWORK")
print("=" * 90)

couplings = [
    ("Diurnal Thermal Cycle", "Atmospheric Water Cycle", "Heating drives evaporation", "strong"),
    ("Diurnal Thermal Cycle", "Seasonal Thermal Cycle", "Daily cycles nest within seasonal", "strong"),
    ("Seasonal Thermal Cycle", "ENSO (El Nino / La Nina)", "Seasonal forcing modulates ENSO timing", "moderate"),
    ("ENSO (El Nino / La Nina)", "Atmospheric Water Cycle", "El Nino shifts precipitation patterns globally", "strong"),
    ("ENSO (El Nino / La Nina)", "Carbon Cycle (Ocean-Atmosphere)", "El Nino releases oceanic CO2", "moderate"),
    ("Atmospheric Water Cycle", "Tidal Cycle", "Precipitation + runoff modifies coastal dynamics", "weak"),
    ("Carbon Cycle (Ocean-Atmosphere)", "Seasonal Thermal Cycle", "CO2 greenhouse modifies seasonal amplitude", "moderate"),
    ("Carbon Cycle (Ocean-Atmosphere)", "Thermohaline Circulation (AMOC)", "CO2 warming disrupts deep water formation", "strong"),
    ("Thermohaline Circulation (AMOC)", "Seasonal Thermal Cycle", "Heat transport moderates NH seasons", "strong"),
    ("Thermohaline Circulation (AMOC)", "Carbon Cycle (Ocean-Atmosphere)", "Deep circulation sequesters/releases CO2", "strong"),
    ("Volcanic Cycle", "Carbon Cycle (Ocean-Atmosphere)", "Eruptions inject CO2 + aerosols", "moderate"),
    ("Volcanic Cycle", "Seasonal Thermal Cycle", "Major eruptions cause volcanic winters", "moderate"),
    ("Milankovitch / Ice Age Cycle", "Seasonal Thermal Cycle", "Orbital forcing sets seasonal intensity", "strong"),
    ("Milankovitch / Ice Age Cycle", "Thermohaline Circulation (AMOC)", "Ice sheet meltwater disrupts AMOC", "strong"),
    ("Milankovitch / Ice Age Cycle", "Carbon Cycle (Ocean-Atmosphere)", "Glacial/interglacial CO2 swings", "strong"),
    ("Geomagnetic Dynamo", "Atmospheric Water Cycle", "Weak field → increased cosmic ray flux → cloud nucleation?", "weak"),
]

for src, dst, label, strength in couplings:
    print(f"  [{strength:>8}] {src:<45} → {dst}")
    print(f"           {label}")

# ============================================================
# STEP 5: Summary statistics
# ============================================================

print("\n" + "=" * 90)
print("SUMMARY")
print("=" * 90)

ara_values = [r["ARA"] for r in results.values()]
phi_hits = [name for name, r in results.items() if r["phi_deviation"] < 5]
extreme_snaps = [name for name, r in results.items() if r["ARA"] < 0.15]
consumers = [name for name, r in results.items() if 0.15 <= r["ARA"] < 0.8]
engines = [name for name, r in results.items() if 1.45 <= r["ARA"] < 1.75]
exothermic = [name for name, r in results.items() if 1.75 <= r["ARA"] < 2.2]
beyond = [name for name, r in results.items() if r["ARA"] > 2.2]

print(f"  ARA range: {min(ara_values):.4f} – {max(ara_values):.4f}")
print(f"  Timescale range: hours (tidal/diurnal) to 300,000 years (geomagnetic)")
print(f"  phi-zone hits (within 5%): {len(phi_hits)} — {', '.join(phi_hits) if phi_hits else 'none'}")
print(f"  Extreme snaps (< 0.15): {len(extreme_snaps)} — {', '.join(extreme_snaps)}")
print(f"  Consumers (0.15-0.8): {len(consumers)} — {', '.join(consumers)}")
print(f"  Engines/phi zone (1.45-1.75): {len(engines)} — {', '.join(engines) if engines else 'none'}")
print(f"  Exothermic sources (1.75-2.2): {len(exothermic)} — {', '.join(exothermic) if exothermic else 'none'}")
print(f"  Beyond scale (> 2.2): {len(beyond)} — {', '.join(beyond) if beyond else 'none'}")

print(f"\n  KEY FINDINGS:")
print(f"  • Diurnal thermal cycle: ARA = {results['Diurnal Thermal Cycle']['ARA']:.3f}, "
      f"phi deviation = {results['Diurnal Thermal Cycle']['phi_deviation']}%")
print(f"    → Within 3% of phi. The daily heating/cooling cycle is a free-running thermal engine.")
print(f"  • Seasonal cycle: ARA = {results['Seasonal Thermal Cycle']['ARA']:.3f}, "
      f"near-perfect pacemaker — forced symmetry from axial tilt.")
print(f"  • Carbon cycle: ARA = {results['Carbon Cycle (Ocean-Atmosphere)']['ARA']:.3f}, "
      f"massively beyond the scale — a one-way ratchet.")
print(f"  • Milankovitch: ARA = {results['Milankovitch / Ice Age Cycle']['ARA']:.3f}, "
      f"classic sawtooth snap — the famous unexplained asymmetry IS the ARA signature.")

# Output JSON
output = {
    "subsystems": {k: {
        "ARA": v["ARA"],
        "classification": v["classification"],
        "zone": v["zone"],
        "T_acc": v["T_accumulation"],
        "T_rel": v["T_release"],
        "unit": v["time_unit"],
        "phi_dev": v["phi_deviation"]
    } for k, v in results.items()},
    "predictions": {k: v["prediction"] for k, v in predictions.items()}
}

with open("earth_ara_results.json", "w") as f:
    json.dump(output, f, indent=2)

print("\nResults saved to earth_ara_results.json")
print("\n✓ Analysis complete. Ready for validation against known climate/geophysics.")
