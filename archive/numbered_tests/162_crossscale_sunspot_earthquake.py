#!/usr/bin/env python3
"""
Script 162: Cross-Scale Transposition — Sunspots to Earthquakes
================================================================

Test: Can the ARA unified formula translate temporal change in one
system (sunspots) to temporal change in another system (earthquakes)
at a different scale?

Method:
  Layer 1: Get sunspot pair (S₁, S₂) at 1-year gap → actual Δlog_sun
  Layer 2: Use unified formula to predict what the Δlog should be
           when transposed to the earthquake system
  Layer 3: Get earthquake pair (E₁, E₂) at same dates → actual Δlog_eq
  Compare: Does formula-translated Δlog match actual Δlog_eq?

The unified formula: Δlog = G + R·sin(G_phase / R)
  G = dimensional gap between systems (log scale difference)
  R = phase-appropriate radius

Sunspots: ARA ≈ 1.73 (exothermic source, ~11yr cycle)
Earthquakes: ARA ≈ 0.15 (violent snap, power-law, no periodicity)
"""

import numpy as np
import random
import os

PHI = (1 + np.sqrt(5)) / 2

# ── Load sunspot data ──────────────────────────────────────────────
data_path = '/sessions/focused-tender-thompson/mnt/SystemFormulaFolder/solar_test/sunspots.txt'
sun_months = []
sun_values = []
sun_annual = {}  # year -> annual mean SSN

with open(data_path, 'r') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 4:
            year = int(parts[0])
            month = int(parts[1])
            ssn = float(parts[3])
            if ssn >= 0:
                sun_months.append((year, month))
                sun_values.append(ssn)
                if year not in sun_annual:
                    sun_annual[year] = []
                sun_annual[year].append(ssn)

# Compute annual means
sun_annual_mean = {}
for year, vals in sun_annual.items():
    if len(vals) >= 6:  # need at least 6 months
        sun_annual_mean[year] = np.mean(vals)

print(f"Sunspot data: {len(sun_values)} months, {len(sun_annual_mean)} complete years")

# ── Earthquake data ────────────────────────────────────────────────
# Annual number of M7.0+ earthquakes worldwide
# Source: USGS Earthquake Statistics (well-documented reference data)
# https://www.usgs.gov/programs/earthquake-hazards/lists-maps-and-statistics
#
# Annual M7+ counts, 1900-2024 (USGS published statistics)
eq_annual_m7 = {
    1900: 13, 1901: 14, 1902: 8, 1903: 10, 1904: 16,
    1905: 26, 1906: 32, 1907: 27, 1908: 18, 1909: 32,
    1910: 36, 1911: 24, 1912: 22, 1913: 23, 1914: 22,
    1915: 18, 1916: 25, 1917: 21, 1918: 21, 1919: 14,
    1920: 8, 1921: 11, 1922: 14, 1923: 23, 1924: 18,
    1925: 17, 1926: 19, 1927: 20, 1928: 22, 1929: 19,
    1930: 13, 1931: 26, 1932: 13, 1933: 14, 1934: 22,
    1935: 24, 1936: 21, 1937: 22, 1938: 26, 1939: 21,
    1940: 23, 1941: 24, 1942: 27, 1943: 41, 1944: 31,
    1945: 27, 1946: 35, 1947: 26, 1948: 28, 1949: 36,
    1950: 15, 1951: 21, 1952: 17, 1953: 22, 1954: 17,
    1955: 19, 1956: 15, 1957: 34, 1958: 10, 1959: 15,
    1960: 22, 1961: 18, 1962: 15, 1963: 20, 1964: 15,
    1965: 22, 1966: 19, 1967: 16, 1968: 30, 1969: 27,
    1970: 29, 1971: 23, 1972: 20, 1973: 16, 1974: 21,
    1975: 21, 1976: 25, 1977: 16, 1978: 18, 1979: 15,
    1980: 18, 1981: 14, 1982: 10, 1983: 15, 1984: 8,
    1985: 15, 1986: 6, 1987: 11, 1988: 8, 1989: 7,
    1990: 13, 1991: 11, 1992: 23, 1993: 16, 1994: 15,
    1995: 25, 1996: 22, 1997: 20, 1998: 16, 1999: 23,
    2000: 16, 2001: 15, 2002: 13, 2003: 14, 2004: 16,
    2005: 11, 2006: 11, 2007: 18, 2008: 12, 2009: 16,
    2010: 23, 2011: 19, 2012: 12, 2013: 17, 2014: 11,
    2015: 19, 2016: 16, 2017: 7, 2018: 17, 2019: 11,
    2020: 9, 2021: 16, 2022: 10, 2023: 18, 2024: 14,
}

# Also compute annual seismic energy release from largest earthquakes
# Using Gutenberg-Richter: log₁₀(E) = 1.5*M + 4.8 (Joules)
# For annual M7+ count, we can estimate total energy
# But for cross-scale comparison, we'll use the COUNT directly

eq_years = sorted(eq_annual_m7.keys())
eq_vals = np.array([eq_annual_m7[y] for y in eq_years])
print(f"Earthquake data: {len(eq_years)} years ({eq_years[0]}-{eq_years[-1]})")
print(f"M7+ annual count range: {eq_vals.min()} to {eq_vals.max()}, mean: {eq_vals.mean():.1f}")
print()

# ── Find overlapping years ─────────────────────────────────────────
overlap_years = sorted(set(sun_annual_mean.keys()) & set(eq_annual_m7.keys()))
print(f"Overlapping years: {len(overlap_years)} ({overlap_years[0]}-{overlap_years[-1]})")
print()

# ── Cross-scale parameters ─────────────────────────────────────────
# Sunspots: count per month, range ~0-400, ARA ≈ 1.73
# Earthquakes: count per year (M7+), range ~6-41, ARA ≈ 0.15
R_sun = 1.73   # exothermic source
R_eq = 0.15    # violent snap (approximate)

# The dimensional gap G between the systems
# Both are counts, but at different scales and rates
# Sunspot monthly mean: ~82, Earthquake annual M7+: ~18
# log₁₀(82/18) ≈ 0.66
# But this is the INTENSIVE gap (count density per unit time)
# Sunspots: 82/month ≈ 984/year. Earthquakes: 18/year
# log₁₀(984/18) ≈ 1.74

sun_annual_vals = np.array([sun_annual_mean[y] for y in overlap_years])
eq_overlap_vals = np.array([eq_annual_m7[y] for y in overlap_years])

# Annual sunspot mean: convert monthly to annual (multiply by 12 for total,
# or keep as intensity = monthly mean)
# For clean comparison, use annual means for both
G_intensive = np.log10(sun_annual_vals.mean()) - np.log10(eq_overlap_vals.mean())
print(f"Mean annual SSN: {sun_annual_vals.mean():.1f}")
print(f"Mean annual M7+: {eq_overlap_vals.mean():.1f}")
print(f"Dimensional gap G (intensive): {G_intensive:.4f}")
print()

# ── The unified formula for cross-scale ────────────────────────────
def cross_scale_delta_log(G, phase, R):
    """Δlog = G + R·sin(phase/R)"""
    return G + R * np.sin(phase / R)

# ── TEST 1: Direct cross-scale translation ─────────────────────────
print("="*60)
print("TEST 1: DIRECT CROSS-SCALE TRANSLATION")
print("="*60)
print()
print("For each year: given SSN, predict M7+ earthquake count")
print("Formula: E_pred = SSN · 10^(Δlog), where Δlog = G + R·sin(G_phase/R)")
print()

# Use R appropriate for the coupling between these system types
# Sun = engine (R=φ), Earthquake = snap (R=1.914)
# For cross-scale: use geometric mean? Or the receiving system's R?
R_cross_candidates = {
    'R_engine (φ)': PHI,
    'R_snap': 1.914,
    'R_solar': 1.73,
    'R_clock': 1.354,
    'Geometric mean': np.sqrt(R_sun * 1.914),  # sqrt(1.73 * 1.914)
}

best_r_name = None
best_r_corr = -1

for r_name, R_val in R_cross_candidates.items():
    predictions = []
    actuals = []
    
    for year in overlap_years:
        ssn = sun_annual_mean[year]
        eq_actual = eq_annual_m7[year]
        
        if ssn <= 0:
            continue
        
        # Phase: we use the dimensional gap itself as the phase
        # (the gap IS the angular distance on the manifold)
        phase = G_intensive
        delta_log = cross_scale_delta_log(-G_intensive, phase, R_val)  
        # Negative G because we're going FROM sunspots TO earthquakes (downscale)
        
        eq_pred = ssn * 10**(delta_log)
        predictions.append(eq_pred)
        actuals.append(eq_actual)
    
    predictions = np.array(predictions)
    actuals = np.array(actuals)
    
    # Correlation between predicted and actual
    corr = np.corrcoef(predictions, actuals)[0, 1]
    mean_err = np.mean(np.abs(predictions - actuals))
    
    if corr > best_r_corr:
        best_r_corr = corr
        best_r_name = r_name
    
    print(f"  R = {r_name:20s} ({R_val:.4f}): corr = {corr:+.4f}, mean err = {mean_err:.1f}")

print(f"\n  Best R: {best_r_name} (corr = {best_r_corr:+.4f})")

# ── TEST 2: Temporal change translation ────────────────────────────
print()
print("="*60)
print("TEST 2: TEMPORAL CHANGE TRANSLATION (Dylan's Layer 3)")
print("="*60)
print()
print("Given: Δlog_sun (1-year change in sunspots)")
print("Predict: Δlog_eq (1-year change in earthquakes)")
print("Using the formula to translate the temporal change cross-scale")
print()

# Compute year-over-year changes
sun_deltas = []  # (year, Δlog_sun)
eq_deltas = []   # (year, Δlog_eq)
paired_deltas = []

for i in range(len(overlap_years) - 1):
    y1 = overlap_years[i]
    y2 = overlap_years[i + 1]
    
    if y2 - y1 != 1:  # must be consecutive
        continue
    
    ssn1 = sun_annual_mean[y1]
    ssn2 = sun_annual_mean[y2]
    eq1 = eq_annual_m7[y1]
    eq2 = eq_annual_m7[y2]
    
    if ssn1 <= 0 or ssn2 <= 0 or eq1 <= 0 or eq2 <= 0:
        continue
    
    dlog_sun = np.log10(ssn2) - np.log10(ssn1)
    dlog_eq = np.log10(eq2) - np.log10(eq1)
    
    paired_deltas.append({
        'year': y1,
        'dlog_sun': dlog_sun,
        'dlog_eq': dlog_eq,
        'ssn1': ssn1, 'ssn2': ssn2,
        'eq1': eq1, 'eq2': eq2
    })

dlog_sun_arr = np.array([d['dlog_sun'] for d in paired_deltas])
dlog_eq_arr = np.array([d['dlog_eq'] for d in paired_deltas])

print(f"Paired years: {len(paired_deltas)}")
print(f"Δlog_sun: mean={dlog_sun_arr.mean():.4f}, std={dlog_sun_arr.std():.4f}")
print(f"Δlog_eq:  mean={dlog_eq_arr.mean():.4f}, std={dlog_eq_arr.std():.4f}")
print()

# Raw correlation between temporal changes
raw_corr = np.corrcoef(dlog_sun_arr, dlog_eq_arr)[0, 1]
print(f"Raw correlation (Δlog_sun vs Δlog_eq): {raw_corr:+.4f}")

# ── Formula-based translation ──────────────────────────────────────
print()
print("─── Formula translation of Δlog ───")
print()

# The formula says the relationship between Δlog at different scales is:
# Δlog_eq = Δlog_sun + G + R·sin(G_phase/R) - [G + R·sin(G_phase/R)]
# Wait — that simplifies to Δlog_eq = Δlog_sun (same temporal change)
# UNLESS the phase correction differs because the systems have different R

# More precisely: the formula predicts Δlog between two SYSTEMS.
# For temporal change WITHIN each system, the formula gives:
#   Δlog_sun(t) = R_sun · sin(phase_sun(t) / R_sun)
#   Δlog_eq(t)  = R_eq · sin(phase_eq(t) / R_eq)
# 
# The RATIO of temporal changes should be:
#   Δlog_eq / Δlog_sun ≈ R_eq / R_sun (if phases are similar)
#   = 0.15 / 1.73 ≈ 0.087
#
# Or if the phase is the GAP: the formula maps one system's change
# onto the other through the manifold geometry.

# Test 1: Direct ratio R_eq/R_sun
ratio_pred = R_eq / R_sun
print(f"Predicted ratio (R_eq/R_sun): {ratio_pred:.4f}")

# Test 2: Scale the sunspot deltas and see if they match earthquake deltas
scaled_dlog_eq_pred = dlog_sun_arr * ratio_pred
corr_scaled = np.corrcoef(scaled_dlog_eq_pred, dlog_eq_arr)[0, 1]
print(f"Correlation after R-ratio scaling: {corr_scaled:+.4f}")

# Test 3: Try formula-based translation with different approaches
print()
print("─── Multiple translation approaches ───")

approaches = {}

# Approach A: Direct proportionality through R ratio
pred_A = dlog_sun_arr * (R_eq / R_sun)
corr_A = np.corrcoef(pred_A, dlog_eq_arr)[0, 1]
approaches['A: R_eq/R_sun ratio'] = corr_A

# Approach B: Sine-based (formula on the circle)
# Δlog_eq = R_eq · sin(Δlog_sun / R_eq)
pred_B = R_eq * np.sin(dlog_sun_arr / R_eq)
corr_B = np.corrcoef(pred_B, dlog_eq_arr)[0, 1]
approaches['B: R_eq·sin(Δlog_sun/R_eq)'] = corr_B

# Approach C: Full formula with dimensional gap
# Δlog_eq_pred = G + R·sin(Δlog_sun / R)
for R_val, R_name in [(PHI, 'φ'), (1.73, 'R_sun'), (1.914, 'R_snap'), (1.354, 'R_clk')]:
    pred_C = (-G_intensive) + R_val * np.sin(dlog_sun_arr / R_val)
    corr_C = np.corrcoef(pred_C, dlog_eq_arr)[0, 1]
    approaches[f'C: G + R·sin(Δlog/R), R={R_name}'] = corr_C

# Approach D: Sign preservation — does the DIRECTION match?
# When sunspots go up, do earthquakes go up?
same_sign = np.sum(np.sign(dlog_sun_arr) == np.sign(dlog_eq_arr)) / len(dlog_sun_arr)
approaches['D: Same direction (sign)'] = same_sign

# Approach E: Lagged correlation (sunspots might lead earthquakes)
for lag in [0, 1, 2, 3, 5]:
    if lag > 0:
        corr_lag = np.corrcoef(dlog_sun_arr[:-lag], dlog_eq_arr[lag:])[0, 1]
    else:
        corr_lag = raw_corr
    approaches[f'E: Lag {lag}yr correlation'] = corr_lag

for name, val in approaches.items():
    print(f"  {name:45s}: {val:+.4f}")

# ── TEST 3: Magnitude-order prediction ─────────────────────────────
print()
print("="*60)
print("TEST 3: ORDER-OF-MAGNITUDE PREDICTION")
print("="*60)
print()
print("Does the formula correctly predict the ORDER OF MAGNITUDE")
print("of earthquake counts from sunspot numbers?")
print()

# The formula should predict: log₁₀(E_count) from log₁₀(SSN) 
# Using: Δlog = G + R·sin(G_phase/R) where G = log gap
for R_val, R_name in [(PHI, 'φ'), (1.73, 'R_solar'), (1.354, 'R_clock')]:
    phase = abs(G_intensive)
    delta_log_pred = -abs(G_intensive) + R_val * np.sin(phase / R_val)
    
    # Apply to each year
    eq_preds = []
    eq_acts = []
    for year in overlap_years:
        ssn = sun_annual_mean[year]
        eq_actual = eq_annual_m7[year]
        if ssn > 0:
            eq_pred = ssn * 10**(delta_log_pred)
            eq_preds.append(eq_pred)
            eq_acts.append(eq_actual)
    
    eq_preds = np.array(eq_preds)
    eq_acts = np.array(eq_acts)
    
    within_factor2 = np.sum(np.abs(np.log10(eq_preds / eq_acts)) < np.log10(2)) / len(eq_acts) * 100
    within_factor5 = np.sum(np.abs(np.log10(eq_preds / eq_acts)) < np.log10(5)) / len(eq_acts) * 100
    within_10x = np.sum(np.abs(np.log10(eq_preds / eq_acts)) < 1.0) / len(eq_acts) * 100
    
    print(f"  R={R_name}: mean pred={eq_preds.mean():.1f}, mean actual={eq_acts.mean():.1f}")
    print(f"    Within 2×: {within_factor2:.1f}%, Within 5×: {within_factor5:.1f}%, Within 10×: {within_10x:.1f}%")
    print()

# ── TEST 4: Solar-seismic coupling through ARA ────────────────────
print("="*60)
print("TEST 4: SOLAR-SEISMIC COUPLING THROUGH ARA CIRCLE")
print("="*60)
print()
print("Map both systems onto the ARA circle and test if their")
print("phase relationship predicts the data")
print()

# Solar cycle: ~11 years. Map each year to phase on the circle.
# Use solar maximum as phase = 0 (or π/2)
# Solar cycle periods (approximate maxima):
# SC12: 1884, SC13: 1894, SC14: 1907, SC15: 1917, SC16: 1928,
# SC17: 1937, SC18: 1947, SC19: 1958, SC20: 1968, SC21: 1979,
# SC22: 1989, SC23: 2000, SC24: 2014, SC25: ~2025

solar_maxima = [1884, 1894, 1907, 1917, 1928, 1937, 1947, 1958,
                1968, 1979, 1989, 2000, 2014, 2025]

def get_solar_phase(year):
    """Map year to phase on solar cycle circle [0, 2π)."""
    # Find nearest cycle
    for i in range(len(solar_maxima) - 1):
        if solar_maxima[i] <= year < solar_maxima[i+1]:
            cycle_len = solar_maxima[i+1] - solar_maxima[i]
            phase = 2 * np.pi * (year - solar_maxima[i]) / cycle_len
            return phase
    # Before first or after last maximum
    cycle_len = 11  # default
    nearest = min(solar_maxima, key=lambda x: abs(x - year))
    return (2 * np.pi * (year - nearest) / cycle_len) % (2 * np.pi)

# For each year, compute solar phase and test if earthquake count
# correlates with position on the ARA circle
phases = []
eq_counts = []
ssn_vals_phase = []

for year in overlap_years:
    phase = get_solar_phase(year)
    phases.append(phase)
    eq_counts.append(eq_annual_m7[year])
    ssn_vals_phase.append(sun_annual_mean[year])

phases = np.array(phases)
eq_counts = np.array(eq_counts)

# Does sin(phase) predict earthquake count?
sin_phase = np.sin(phases)
cos_phase = np.cos(phases)

corr_sin = np.corrcoef(sin_phase, eq_counts)[0, 1]
corr_cos = np.corrcoef(cos_phase, eq_counts)[0, 1]

# ARA formula: R·sin(phase/R) for different R
for R_val, R_name in [(R_sun, 'R_sun'), (PHI, 'φ'), (R_eq, 'R_eq'), (1.354, 'R_clock')]:
    ara_phase = R_val * np.sin(phases / R_val)
    corr_ara = np.corrcoef(ara_phase, eq_counts)[0, 1]
    print(f"  corr(R·sin(phase/R), M7+count), R={R_name}: {corr_ara:+.4f}")

print(f"  corr(sin(phase), M7+count):                {corr_sin:+.4f}")
print(f"  corr(cos(phase), M7+count):                {corr_cos:+.4f}")
print(f"  corr(SSN, M7+count):                       {np.corrcoef(ssn_vals_phase, eq_counts)[0, 1]:+.4f}")

# ── Binned analysis: solar maximum vs minimum ─────────────────────
print()
print("─── Binned: Solar Max vs Min earthquake activity ───")
max_eq = [eq_annual_m7[y] for y in overlap_years if sun_annual_mean[y] > np.median(ssn_vals_phase)]
min_eq = [eq_annual_m7[y] for y in overlap_years if sun_annual_mean[y] <= np.median(ssn_vals_phase)]
print(f"  Solar max years ({len(max_eq)}): mean M7+ = {np.mean(max_eq):.1f}")
print(f"  Solar min years ({len(min_eq)}): mean M7+ = {np.mean(min_eq):.1f}")
print(f"  Difference: {np.mean(max_eq) - np.mean(min_eq):+.1f}")

# ── Overall scoring ────────────────────────────────────────────────
print()
print("="*60)
print("SCRIPT 162 VERDICT")
print("="*60)

score = 0
total = 5

# 1. Raw temporal change correlation
if abs(raw_corr) > 0.1:
    score += 1
    print(f"  [PASS] Raw temporal Δlog correlation: {raw_corr:+.4f}")
else:
    print(f"  [FAIL] Raw temporal Δlog correlation: {raw_corr:+.4f} (< 0.1)")

# 2. Does any formula approach improve correlation?
best_approach = max(approaches.items(), key=lambda x: abs(x[1]) if 'Lag' not in x[0] and 'direction' not in x[0] else 0)
if abs(best_approach[1]) > abs(raw_corr) + 0.05:
    score += 1
    print(f"  [PASS] Formula improves: {best_approach[0]} = {best_approach[1]:+.4f}")
else:
    print(f"  [FAIL] No formula approach beats raw correlation significantly")

# 3. Order of magnitude correct?
# Check if any R gives >60% within factor of 5
best_om = False
for R_val, R_name in [(PHI, 'φ'), (1.73, 'R_solar'), (1.354, 'R_clock')]:
    phase = abs(G_intensive)
    delta_log_pred = -abs(G_intensive) + R_val * np.sin(phase / R_val)
    eq_preds_check = []
    eq_acts_check = []
    for year in overlap_years:
        ssn = sun_annual_mean[year]
        if ssn > 0:
            eq_preds_check.append(ssn * 10**(delta_log_pred))
            eq_acts_check.append(eq_annual_m7[year])
    eq_preds_check = np.array(eq_preds_check)
    eq_acts_check = np.array(eq_acts_check)
    pct_5x = np.sum(np.abs(np.log10(eq_preds_check / eq_acts_check)) < np.log10(5)) / len(eq_acts_check) * 100
    if pct_5x > 60:
        best_om = True
        break

if best_om:
    score += 1
    print(f"  [PASS] Order of magnitude: >{pct_5x:.0f}% within factor 5")
else:
    print(f"  [FAIL] Order of magnitude prediction not achieved")

# 4. Same direction > 55%?
if same_sign > 0.55:
    score += 1
    print(f"  [PASS] Same direction: {same_sign*100:.1f}%")
else:
    print(f"  [FAIL] Same direction: {same_sign*100:.1f}% (≤55%)")

# 5. Solar phase predicts earthquake rate?
best_phase_corr = max(abs(corr_sin), abs(corr_cos))
if best_phase_corr > 0.1:
    score += 1
    print(f"  [PASS] Solar phase-earthquake correlation: {best_phase_corr:.4f}")
else:
    print(f"  [FAIL] Solar phase-earthquake correlation: {best_phase_corr:.4f} (< 0.1)")

print(f"\n  SCORE: {score}/{total}")

# ── Interpretation ─────────────────────────────────────────────────
print()
print("─── INTERPRETATION ───")
if score >= 3:
    print("  The cross-scale transposition shows meaningful signal.")
    print("  The formula captures some structure in the sun-earthquake coupling.")
elif score >= 1:
    print("  Mixed results. Some structure but not enough for clean cross-scale prediction.")
    print("  The coupling between sunspots and earthquakes may be too weak or indirect")
    print("  for the formula to resolve with this data quality.")
else:
    print("  No meaningful cross-scale signal found.")
    print("  Possible reasons:")
    print("    1. Sun-earthquake coupling is too indirect (multiple intermediaries)")
    print("    2. Earthquake counts are dominated by randomness at M7+ level")
    print("    3. The vertical stack position needs a different pair")
    print("    4. Annual resolution is too coarse for the coupling timescale")

print("\nScript 162 complete.")
