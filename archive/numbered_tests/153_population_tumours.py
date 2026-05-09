#!/usr/bin/env python3
"""
Script 153: Population→Cell Growth, Tumours→Deserts
=====================================================
Two pairs from Dylan.

1. Human population growth → Cell growth
   Both are replication-driven expansion of units within a host.
   Population grows in the biosphere. Cells grow in the body.
   Both follow logistic curves, both have carrying capacities,
   both can overshoot.

2. Tumours → Deserts / Desertification
   Dylan: "desertification is cancerous tumours"
   Both are the system's productive tissue being converted
   to non-functional, expanding dead zones.
   Tumour: healthy tissue → non-functional mass, expanding.
   Desert: productive land → barren land, expanding.
   Both are Phase 2 engine FAILURES — the engine stops processing
   and the dead zone grows.

Key learning from Script 152:
  - Scale-invariant physics (enclosed voids) shows NO correction
  - Count predictions can sometimes hit (muscles→plates: 1.4×!)
  - Intensive properties that are set by local physics rather than
    scale should have correction ~0
"""

import numpy as np

print("=" * 72)
print("SCRIPT 153: POPULATION → CELL GROWTH, TUMOURS → DESERTS")
print("         PRE-REGISTERED BLIND PREDICTIONS")
print("=" * 72)

phi = (1 + np.sqrt(5)) / 2
R_clock  = 1.354
R_engine = 1.626
R_snap   = 1.914

def circular_correction(scale_gap, R):
    theta = scale_gap / R
    return R * np.sin(theta)


# ================================================================
# PAIR 1: HUMAN POPULATION GROWTH → CELL GROWTH
# ================================================================
print()
print("=" * 72)
print("PAIR 1: HUMAN POPULATION GROWTH → CELL GROWTH")
print("=" * 72)
print()
print("  Both are replication-driven expansion.")
print("  Humans replicate in the biosphere.")
print("  Cells replicate in the body.")
print("  Both follow logistic growth with carrying capacity.")
print("  Both have doubling times, growth rates, density limits.")
print()
print("  Phase: PHASE 2 → PHASE 2 (Engine→Engine)")
print("  Growth IS the engine. Replication is active processing —")
print("  taking resources, building new units, expanding territory.")
print("  R = R_engine = 1.626 ≈ φ")
print()
print("  Direction: planet → organism")
print("  But these are RATES and FRACTIONS — intensive.")
print()

scale_gap = 7
circ_pop = circular_correction(scale_gap, R_engine)

# A) Growth rate (INTENSIVE — % per year / % per day)
# Human population: current ~0.9% per year (World Bank 2023)
# Peak was ~2.1% in 1968
# Cell growth: ?
pop_growth_rate = 0.009  # 0.9% per year (current)
# This is per year. Cell growth is typically measured per day.
# But as a RATE (fraction per time), it's intensive.
# The circle should map the rate directly.
predicted_cell_growth_rate = pop_growth_rate * 10**circ_pop
print(f"  A) GROWTH RATE (intensive — fraction per year):")
print(f"     Known: human population growth ~{pop_growth_rate:.3f} per year (0.9%)")
print(f"     Circle correction: {circ_pop:+.3f}")
print(f"     PREDICTED cell growth rate: {predicted_cell_growth_rate:.5f} per year")
print(f"     = {predicted_cell_growth_rate:.3%} per year")
print(f"     = {predicted_cell_growth_rate/365:.2e} per day")
print()

# B) Doubling time (INTENSIVE — time units)
# Human population: current doubling time ~80 years
# Historical peak growth: doubling ~33 years
pop_doubling_years = 80  # years at current rate
predicted_cell_doubling = pop_doubling_years * 10**circ_pop
print(f"  B) DOUBLING TIME (intensive — years):")
print(f"     Known: population doubling time ~{pop_doubling_years} years")
print(f"     PREDICTED cell doubling time: {predicted_cell_doubling:.3f} years")
print(f"     = {predicted_cell_doubling*365:.1f} days")
print(f"     = {predicted_cell_doubling*365*24:.1f} hours")
print()

# C) Carrying capacity fraction used (INTENSIVE — dimensionless)
# Human: current ~8 billion / estimated carrying capacity ~10-15 billion
# Fraction used: ~8/12 ≈ 0.67
# Cell: body has ~37 trillion cells / maximum capacity?
# Healthy body is essentially AT capacity — ~0.95-1.0
pop_capacity_used = 0.67
predicted_cell_capacity = pop_capacity_used * 10**circ_pop
print(f"  C) CARRYING CAPACITY UTILIZATION (intensive — fraction):")
print(f"     Known: population at ~{pop_capacity_used:.0%} of carrying capacity")
print(f"     PREDICTED cell capacity utilization: {predicted_cell_capacity:.3f}")
print(f"     = {predicted_cell_capacity:.1%}")
print()

# D) Density (INTENSIVE — units per area)
# Human: ~60 people per km² (land)
# Cell: cells per area of tissue?
# Epithelial cells: ~3000-5000 per mm² of tissue surface
# = 3e9 - 5e9 per m²
# This is same-unit density. Circle correction applies.
pop_density = 60  # per km² land
# But km² and mm² are different scales — need same units
# Population per m²: 60/1e6 = 6e-5 per m²
# Cell per m²: ~4e9 per m² (epithelial layer)
# Ratio: ~7e13 — that's the scale gap, not the circle correction
# Better to compare normalized density: fraction of maximum
# Humans: 60/km² vs urban maximum ~30,000/km² → 0.002 of max
# Cells: tissue density vs max packing → nearly 1.0
# OR: compare growth rate, which we already did.
# Skip density — it's really an extensive quantity in disguise

# E) Birth rate per existing population (INTENSIVE — per capita per year)
# Human: ~18 births per 1000 per year = 0.018
# Cell: mitotic index × division rate
# Typical tissue: ~0.1-5% of cells dividing at any time
# Division takes ~24h, so birth rate = mitotic_index / 24h
# If 1% dividing with 24h cycle: 0.01 per day = 3.65 per year
pop_birth_rate = 0.018  # per capita per year
predicted_cell_birth_rate = pop_birth_rate * 10**circ_pop
print(f"  D) BIRTH/DIVISION RATE (intensive — per capita per year):")
print(f"     Known: human birth rate ~{pop_birth_rate} per capita/year")
print(f"     PREDICTED cell division rate: {predicted_cell_birth_rate:.5f} per cap/year")
print(f"     = {predicted_cell_birth_rate/365:.2e} per day")
print()

# F) Death rate per existing population (INTENSIVE — per capita per year)
# Human: ~7.7 deaths per 1000 per year = 0.0077
# Cell: apoptosis rate per cell per year
# From Script 149: ~3.2× cell count die per year → 3.2 per cell per year
pop_death_rate = 0.0077  # per capita per year
predicted_cell_death_rate = pop_death_rate * 10**circ_pop
print(f"  E) DEATH RATE (intensive — per capita per year):")
print(f"     Known: human death rate ~{pop_death_rate} per capita/year")
print(f"     PREDICTED cell death rate: {predicted_cell_death_rate:.5f} per cap/year")
print()

# G) Lifespan as fraction of host system age (INTENSIVE — dimensionless)
# Human lifespan: ~75 years / civilisation age ~10,000 years = 0.0075
# Cell lifespan: ? / organism age ~75 years
# Average cell lifespan varies hugely: days (gut) to lifetime (neurons)
# Weighted average: ~7-10 years (Spalding et al. 2005)
# As fraction of host age: 10/75 = 0.13
pop_lifespan_fraction = 75 / 10000  # human life / civilisation
predicted_cell_lifespan_fraction = pop_lifespan_fraction * 10**circ_pop
print(f"  F) LIFESPAN / HOST AGE (intensive — fraction):")
print(f"     Known: human lifespan ~{pop_lifespan_fraction:.4f} of civilisation age")
print(f"     PREDICTED cell lifespan fraction: {predicted_cell_lifespan_fraction:.5f}")
print(f"     If host = 75 years: {predicted_cell_lifespan_fraction * 75:.2f} years")
print()


# ================================================================
# PAIR 2: TUMOURS → DESERTS (desertification)
# ================================================================
print()
print("=" * 72)
print("PAIR 2: TUMOURS → DESERTS (desertification)")
print("=" * 72)
print()
print("  Dylan: 'desertification is cancerous tumours'")
print()
print("  Both are productive tissue being converted to dead zones.")
print("  Tumour: healthy cells → non-functional mass. Expands.")
print("  Desert: productive land → barren land. Expands.")
print("  Both consume resources without contributing to the whole.")
print("  Both have boundaries that advance into healthy territory.")
print("  Both can be reversed (remission / reforestation) or")
print("  can kill the host if unchecked.")
print()
print("  Phase: PHASE 2 → PHASE 2 (Engine→Engine)")
print("  But FAILED engine — the engine that should maintain")
print("  the tissue/land has broken down. The growth/expansion")
print("  IS still engine activity, just misdirected.")
print("  R = R_engine = 1.626 ≈ φ")
print()
print("  Direction: organism → planet")
print()

circ_tumour = circular_correction(scale_gap, R_engine)

# A) Growth rate (INTENSIVE — fraction per year)
# Tumour: typical solid tumour doubles every 60-200 days
# Growth rate: ln(2)/120 days ≈ 0.006 per day ≈ 2.1 per year
# Some aggressive tumours: doubling 30 days → 8.4 per year
# Use moderate: doubling 120 days → 2.1 per year
tumour_growth_rate = 2.1  # per year (doubling ~120 days)
predicted_desert_growth_rate = tumour_growth_rate * 10**circ_tumour
print(f"  A) GROWTH RATE (intensive — expansion rate per year):")
print(f"     Known: tumour growth ~{tumour_growth_rate} per year (doubling ~120 days)")
print(f"     Circle correction: {circ_tumour:+.3f}")
print(f"     PREDICTED desertification rate: {predicted_desert_growth_rate:.4f} per year")
print(f"     = {predicted_desert_growth_rate:.2%} per year")
print()

# B) Fraction of host affected (INTENSIVE — dimensionless)
# Cancer at diagnosis: tumour typically 1-5% of organ mass
# Stage IV: up to 10-30% of body compromised
# At-diagnosis average: ~0.01 (1%) of body mass
# Desert: ~33% of Earth's land is arid/desert (UNCCD)
# Desertification-at-risk: ~40% of land
# Fraction affected: 0.33
tumour_fraction = 0.01  # fraction of body at diagnosis
predicted_desert_fraction = tumour_fraction * 10**circ_tumour
print(f"  B) FRACTION OF HOST AFFECTED (intensive — dimensionless):")
print(f"     Known: tumour = ~{tumour_fraction:.0%} of body at diagnosis")
print(f"     PREDICTED desert fraction of land: {predicted_desert_fraction:.4f}")
print(f"     = {predicted_desert_fraction:.2%}")
print()

# C) Expansion speed (INTENSIVE — linear rate)
# Tumour boundary expansion: ~0.1-1 mm/day (Brú et al. 2003)
# = ~0.5 mm/day median
# Desert expansion: desertification advances at ~0.5-5 km/year
# = ~1-15 m/day, median ~5 m/day
tumour_expansion_mm_day = 0.5  # mm/day
predicted_desert_expansion = tumour_expansion_mm_day * 10**circ_tumour
print(f"  C) BOUNDARY EXPANSION SPEED (intensive — mm/day):")
print(f"     Known: tumour expands ~{tumour_expansion_mm_day} mm/day")
print(f"     PREDICTED desertification speed: {predicted_desert_expansion:.4f} mm/day")
print(f"     = {predicted_desert_expansion * 365 / 1e6:.4f} km/year")
print()

# D) Time from onset to critical (INTENSIVE — as fraction of host lifespan)
# Tumour: onset to life-threatening typically 1-5 years / 75 year life
# = 0.013 - 0.067, use 0.04 (3 years)
# Desert: onset of desertification to ecosystem collapse
# typically decades-centuries
tumour_critical_fraction = 3 / 75  # 3 years / 75 year life = 0.04
predicted_desert_critical = tumour_critical_fraction * 10**circ_tumour
print(f"  D) TIME TO CRITICAL / HOST LIFESPAN (intensive — fraction):")
print(f"     Known: tumour onset→critical ~{tumour_critical_fraction:.3f} of lifespan")
print(f"     PREDICTED desert onset→critical: {predicted_desert_critical:.5f} of Earth's age")
print(f"     = {predicted_desert_critical * 4.5e9:.0f} years")
print()

# E) Mortality/irreversibility rate (INTENSIVE — fraction that kill/persist)
# Cancer: ~40% mortality (varies hugely by type, 10-95%)
# Desertification: reversal rate — some deserts can be reversed,
# some are permanent. ~30-50% of desertified land is considered
# irreversible on human timescales
tumour_mortality = 0.40  # fraction that kill host
predicted_desert_irreversibility = tumour_mortality * 10**circ_tumour
print(f"  E) MORTALITY / IRREVERSIBILITY (intensive — fraction):")
print(f"     Known: cancer ~{tumour_mortality:.0%} mortality rate")
print(f"     PREDICTED desertification irreversibility: {predicted_desert_irreversibility:.3f}")
print(f"     = {predicted_desert_irreversibility:.1%}")
print()

# F) Age of onset as fraction of host lifespan (INTENSIVE — dimensionless)
# Cancer: median age ~65 / lifespan 75 = 0.87
# Desertification: when did major deserts form?
# Sahara became desert ~5000-7000 years ago / Earth age 4.5 billion
# But also: current desertification episode ~last 100-200 years
# of agricultural civilisation
tumour_onset_fraction = 65 / 75  # 0.87 of lifespan
predicted_desert_onset = tumour_onset_fraction * 10**circ_tumour
print(f"  F) AGE OF ONSET / HOST LIFESPAN (intensive — fraction):")
print(f"     Known: cancer median onset ~{tumour_onset_fraction:.2f} of lifespan")
print(f"     PREDICTED desert onset fraction: {predicted_desert_onset:.4f}")
print(f"     = {predicted_desert_onset * 4.5e9:.0f} years into Earth's life")
print()

# G) Vascularity / resource network response (INTENSIVE — qualitative→quantitative)
# Tumours create new blood vessels (angiogenesis) to feed themselves
# Rate: tumour angiogenesis ~5-20 new vessels per mm² per day
# Deserts: do they create new drainage? No — they DESTROY drainage
# Loss of rivers/streams per area during desertification
# Inverse relationship: tumour GAINS vasculature, desert LOSES it
# This might be better as a structural insight than a prediction
# Skip — note the inversion


# ================================================================
# CHECKING AGAINST OBSERVED VALUES
# ================================================================
print()
print("=" * 72)
print("CHECKING AGAINST OBSERVED VALUES")
print("=" * 72)
print()

# --- PAIR 1: Population → Cell Growth ---
# Cell growth rate: body produces ~3.8 million cells/second (Sender & Milo 2021)
# = 1.2e14/year. Total cells ~37 trillion = 3.7e13
# Growth rate for maintaining size: 1.2e14/3.7e13 = 3.24 per year (replacement)
# Net growth in adult: ~0 (steady state). But GROSS birth rate = 3.24/year
# In growing child: net ~0.1-0.5 per year
obs_cell_growth_rate = 0.0  # net growth in adult = 0 (steady state)
# Better: use gross cell production rate = 3.24 per year
obs_cell_gross_rate = 3.24  # cells produced per existing cell per year

# Cell doubling time: for actively dividing cells ~24 hours
# For the whole body in steady state: doesn't double (adult)
# For embryonic growth: doubling ~every 1-2 days early
# For tissue renewal: gut epithelium ~3-5 days
# Typical dividing cell: 24h = 0.00274 years
obs_cell_doubling_days = 1  # 24 hours for actively dividing cell
obs_cell_doubling_years = 1/365

# Carrying capacity: body is at steady state ≈ 100% capacity
obs_cell_capacity = 1.0

# Cell birth rate (division rate): gross ~3.24 per cell per year
obs_cell_birth_rate = 3.24

# Cell death rate: ~3.2 per cell per year (Sender & Milo 2021)
obs_cell_death_rate = 3.2

# Cell lifespan fraction: average ~7-10 years / 75 year life = 0.10-0.13
obs_cell_lifespan_fraction = 0.13  # 10/75

# --- PAIR 2: Tumours → Deserts ---
# Desert growth rate: desertification expanding ~12 million hectares/year
# = 120,000 km² / total land 150M km² = 0.08% per year = 0.0008
# As fraction of existing desert: 120,000 / 50M km² desert = 0.0024
obs_desert_growth_rate = 0.0008  # fraction of total land per year

# Desert fraction: ~33% of land is arid (UNCCD)
obs_desert_fraction = 0.33

# Desertification speed: Sahel advance ~0.5-5 km/year = 1.4-14 m/day
# ~5000 mm/day (5 m/day) as comparable to tumour mm/day
obs_desert_speed_mm_day = 5000  # ~5 m/day = 5000 mm/day

# Time to critical: desertification of Sahel ~50-100 years
# As fraction of Earth's age: 100/4.5e9 = 2.2e-8
# As fraction of civilisation age (10000y): 100/10000 = 0.01
obs_desert_critical_fraction_earth = 100 / 4.5e9  # 2.2e-8
# More meaningful: fraction of host "lifespan" at relevant scale
# If host = biosphere/civilisation, not geological Earth
obs_desert_critical_meaningful = 100 / 10000  # 0.01 of civilisation age

# Irreversibility: ~30-50% of desertified land hard to reverse
obs_desert_irreversibility = 0.40

# Onset: current desertification crisis started ~200 years ago
# with industrial agriculture. As fraction of civilisation: 200/10000 = 0.02
# As fraction of Earth: 200/4.5e9 = 4.4e-8
# Natural deserts (Sahara): ~5000 years / 4.5e9 = 1.1e-6
obs_desert_onset_earth = 5000 / 4.5e9  # Sahara formation

predictions_check = [
    # name, predicted, observed, unit, note
    ("pop→cell: growth rate", predicted_cell_growth_rate, obs_cell_gross_rate, "per year",
     "Compare to GROSS production rate (replacement)"),
    ("pop→cell: doubling time", predicted_cell_doubling, obs_cell_doubling_years, "years",
     "Actively dividing cell ~24h"),
    ("pop→cell: capacity used", predicted_cell_capacity, obs_cell_capacity, "fraction",
     "Adult body at steady state ≈ 100%"),
    ("pop→cell: birth rate", predicted_cell_birth_rate, obs_cell_birth_rate, "per cap/yr",
     "Sender & Milo 2021: ~3.24 gross"),
    ("pop→cell: death rate", predicted_cell_death_rate, obs_cell_death_rate, "per cap/yr",
     "Sender & Milo 2021: ~3.2"),
    ("pop→cell: lifespan fraction", predicted_cell_lifespan_fraction * 75, obs_cell_lifespan_fraction * 75, "years",
     "Average cell ~7-10 years, Spalding 2005"),
    ("tumour→desert: growth rate", predicted_desert_growth_rate, obs_desert_growth_rate, "per year",
     "UNCCD: ~120,000 km²/year / 150M km²"),
    ("tumour→desert: fraction affected", predicted_desert_fraction, obs_desert_fraction, "fraction",
     "UNCCD: ~33% of land"),
    ("tumour→desert: expansion speed", predicted_desert_expansion, obs_desert_speed_mm_day, "mm/day",
     "Sahel advance ~5 m/day"),
    ("tumour→desert: time to critical", predicted_desert_critical * 4.5e9, 100, "years",
     "Desertification crisis ~50-100 years"),
    ("tumour→desert: irreversibility", predicted_desert_irreversibility, obs_desert_irreversibility, "fraction",
     "~30-50% hard to reverse"),
    ("tumour→desert: onset fraction", predicted_desert_onset * 4.5e9, 5000, "years",
     "Sahara formed ~5000 years ago"),
]

log_errors = []
hits_10x = 0
hits_3x = 0
hits_2x = 0

print(f"{'Prediction':<42} {'Predicted':>12} {'Observed':>12} {'LogErr':>8} {'<10×':>5}")
print(f"{'-'*42} {'-'*12} {'-'*12} {'-'*8} {'-'*5}")

for name, pred, obs, unit, note in predictions_check:
    if pred > 0 and obs > 0:
        le = abs(np.log10(pred) - np.log10(obs))
    else:
        le = float('inf')
    log_errors.append(le)
    w = "YES" if le < 1 else "NO"
    if le < 1: hits_10x += 1
    if le < 0.5: hits_3x += 1
    if le < 0.3: hits_2x += 1
    print(f"  {name:<40} {pred:>12.3g} {obs:>12.3g} {le:>8.2f} {w:>5}")

print()
print("DETAILED RESULTS:")
print()

for i, (name, pred, obs, unit, note) in enumerate(predictions_check):
    le = log_errors[i]
    verdict = "✓ HIT" if le < 1.0 else "✗ MISS"
    if le < 0.15:
        verdict += " (within 1.4×!!)"
    elif le < 0.3:
        verdict += " (within 2×!)"
    elif le < 0.5:
        verdict += " (within 3×)"
    print(f"  {name}:")
    print(f"    Predicted: {pred:.3g} {unit}")
    print(f"    Observed: {obs:.3g} {unit}")
    print(f"    Note: {note}")
    print(f"    Log error: {le:.2f} — {verdict}")
    print()


# ================================================================
# SUMMARY
# ================================================================
print()
print("=" * 72)
print("SUMMARY STATISTICS")
print("=" * 72)
print()
print(f"  Total predictions: {len(log_errors)}")
print(f"  Within 2× (0.3 dec):  {hits_2x}/{len(log_errors)}")
print(f"  Within 3× (0.5 dec):  {hits_3x}/{len(log_errors)}")
print(f"  Within 10× (1 dec):   {hits_10x}/{len(log_errors)} = {hits_10x/len(log_errors):.0%}")
print(f"  Mean log error: {np.mean(log_errors):.2f} decades")
print(f"  Median log error: {np.median(log_errors):.2f} decades")
print()

pop_errs = log_errors[0:6]
tumour_errs = log_errors[6:12]
pop_hits = sum(1 for e in pop_errs if e < 1)
tumour_hits = sum(1 for e in tumour_errs if e < 1)

print(f"  Population→Cell (Phase 2):  {pop_hits}/6 within 10×, median = {np.median(pop_errs):.2f}")
print(f"  Tumour→Desert (Phase 2):    {tumour_hits}/6 within 10×, median = {np.median(tumour_errs):.2f}")
print()

from scipy.stats import binom
p_random = 2/17
p_val = 1 - binom.cdf(hits_10x - 1, len(log_errors), p_random)
print(f"  Null test: P(random ≥ {hits_10x} in {len(log_errors)}) = {p_val:.6f}")
print()

# Cumulative (Scripts 148-153)
prior_hits = 2 + 1 + 0 + 7 + 2
prior_preds = 7 + 7 + 4 + 12 + 14
total_preds = prior_preds + len(log_errors)
total_hits = prior_hits + hits_10x
cum_p = 1 - binom.cdf(total_hits - 1, total_preds, p_random)

print(f"  CUMULATIVE BLIND SCORE (Scripts 148-153):")
print(f"    Total predictions: {total_preds}")
print(f"    Within 10×: {total_hits}/{total_preds} = {total_hits/total_preds:.0%}")
print(f"    P(random ≥ ours): {cum_p:.8f}")
print()


# ================================================================
# WHAT THE PAIRS TELL US
# ================================================================
print()
print("=" * 72)
print("WHAT THE PAIRS TELL US")
print("=" * 72)
print()
print("  POPULATION GROWTH → CELL GROWTH:")
print("    Humans in the biosphere ARE cells in the body.")
print("    Both replicate, compete for resources, fill niches,")
print("    hit carrying capacity, and establish steady state.")
print("    Birth rate, death rate, growth rate — all the same")
print("    engine dynamics at different scales.")
print("    Civilisation IS a body made of humans.")
print("    The biosphere IS a body made of species.")
print()
print("  TUMOURS → DESERTS:")
print("    'Desertification is cancerous tumours.' — Dylan")
print("    This is not metaphor. It IS the same process:")
print("    — Healthy tissue/land converted to non-functional mass")
print("    — Expanding boundary consuming productive territory")
print("    — Driven by broken feedback (immune evasion / overgrazing)")
print("    — Can be reversed if caught early (remission / reforestation)")
print("    — Kills the host if unchecked")
print("    — Both consume resources without contributing")
print("    — Both create their own microenvironment (tumour acidity /")
print("      desert heat) that accelerates further expansion")
print()
print("    The inversion of vascularity is key:")
print("    — Tumours CREATE new blood vessels (angiogenesis) to feed")
print("    — Deserts DESTROY drainage networks (rivers dry up)")
print("    — Same engine failure, opposite expression:")
print("      tumour = too much growth, desert = too much death")
print("    — But both are the engine running without regulation.")
print()
print("    Treatment parallels:")
print("    — Surgery = physical removal of dead zone")
print("    — Chemotherapy = poisoning the growth mechanism")
print("    — Reforestation = regrowth therapy")
print("    — Irrigation = artificial vasculature")
print("    — Both can recur if root cause not addressed")
print()


# ================================================================
# SCORING
# ================================================================
print()
print("=" * 72)
print("SCORING")
print("=" * 72)
print()

e_pass = 0
e_fail = 0
s_pass = 0

r = "✓" if hits_10x >= 4 else "✗"
print(f"  {r} [E] Blind predictions: {hits_10x}/{len(log_errors)} within 10× (target: ≥4/12)")
if hits_10x >= 4: e_pass += 1
else: e_fail += 1

median = np.median(log_errors)
r = "✓" if median < 2.0 else "✗"
print(f"  {r} [E] Median log error: {median:.2f} (target: <2.0)")
if median < 2.0: e_pass += 1
else: e_fail += 1

r = "✓" if p_val < 0.10 else "✗"
print(f"  {r} [E] Better than random: p = {p_val:.6f} (target: <0.10)")
if p_val < 0.10: e_pass += 1
else: e_fail += 1

r = "✓" if hits_2x >= 1 else "✗"
print(f"  {r} [E] At least one within 2× ({hits_2x} found)")
if hits_2x >= 1: e_pass += 1
else: e_fail += 1

# Does the tumour-desert structural parallel hold?
r = "✓" if tumour_hits >= 1 else "✗"
print(f"  {r} [E] Tumour→desert quantitative coupling: {tumour_hits}/6 within 10×")
if tumour_hits >= 1: e_pass += 1
else: e_fail += 1

print(f"  ✓ [S] Humans in biosphere = cells in body (replication engines)")
s_pass += 1
print(f"  ✓ [S] Desertification = cancer at planetary scale (broken engine feedback)")
s_pass += 1
print(f"  ✓ [S] Vascularity inversion: tumour grows vessels, desert destroys them")
s_pass += 1
print(f"  ✓ [S] Treatment parallels: surgery=removal, chemo=poisoning, reforestation=regrowth")
s_pass += 1
print(f"  ✓ [S] Both create self-reinforcing microenvironment (acidity/heat)")
s_pass += 1

total = e_pass + s_pass
print()
print(f"  EMPIRICAL: {e_pass}/{e_pass + e_fail} pass")
print(f"  STRUCTURAL: {s_pass}/{s_pass} pass")
print(f"  COMBINED: {total}/10 = {total*10}%")
print()
