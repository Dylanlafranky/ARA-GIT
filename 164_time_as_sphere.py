#!/usr/bin/env python3
"""
Script 164: Time as Sphere — Systems as Coordinates
=====================================================

Dylan's reframe: Time IS the sphere. Systems live ON it.

Geometry:
  - θ (latitude) = system's ARA position on the sphere
    θ = π × (ARA / 2)
    ARA = 0 → north pole (singularity)
    ARA = 1.0 → equator (coupler/boundary)
    ARA = 2.0 → south pole (pure harmonics)
    
  - φ (longitude) = temporal position
    Time advances → φ advances
    
  - Value at any (θ, φ) = R(θ) · sin(φ / R(θ))
    R depends on the system's phase type:
      R_clock = 1.354 (accumulators, ARA < 1.0)
      R_engine = φ_golden ≈ 1.618 (engines, ARA ≈ 1.0-1.73)
      R_snap = 1.914 (discharge, ARA < 0.5)

The sphere's VALUE at each point is the predicted Δlog.
A system at ARA latitude θ, at time longitude φ, has:
  Δlog(θ, φ) = R(θ) · sin(φ / R(θ))

This naturally gives different curvature at different latitudes.
Same temporal step, different response — because time's geometry 
differs for different system types.

Method:
  1. At t₁: know system value V₁
  2. V₁ maps to a position on time's sphere: (θ_sys, φ₁)
     where φ₁ = R · arcsin((log₁₀(V₁) - C) / R)
  3. Advance time: φ₂ = φ₁ + Δφ
  4. Read off new value: V₂ = 10^(R · sin(φ₂ / R) + C)
  5. For cross-scale: same φ₂, different θ (different ARA latitude)
"""

import numpy as np
import os

PHI = (1 + np.sqrt(5)) / 2

# ── Load data ──────────────────────────────────────────────────────
data_path = '/sessions/focused-tender-thompson/mnt/SystemFormulaFolder/solar_test/sunspots.txt'
sun_annual = {}
with open(data_path, 'r') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 4:
            year = int(parts[0])
            ssn = float(parts[3])
            if ssn >= 0:
                if year not in sun_annual:
                    sun_annual[year] = []
                sun_annual[year].append(ssn)

sun_annual_mean = {y: np.mean(v) for y, v in sun_annual.items() if len(v) >= 6}

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

overlap_years = sorted(set(sun_annual_mean.keys()) & set(eq_annual_m7.keys()))
print(f"Data: {len(overlap_years)} overlapping years ({overlap_years[0]}-{overlap_years[-1]})")

# ── ARA positions ──────────────────────────────────────────────────
ARA_SUN = 1.73    # exothermic source (engine)
ARA_EQ = 0.15     # violent snap
ARA_TIME = 1.0    # coupler

# Phase radii by system type
def R_for_ara(ara):
    """Assign phase radius based on ARA position.
    This encodes the system's type on time's sphere."""
    if ara < 0.5:
        return 1.914   # snap/discharge
    elif ara < 1.2:
        return 1.354   # clock/accumulator
    elif ara < 1.8:
        return PHI      # engine
    else:
        return 1.73     # exothermic (solar)

R_SUN = R_for_ara(ARA_SUN)
R_EQ = R_for_ara(ARA_EQ)

print(f"R_sun = {R_SUN:.4f} (engine at ARA={ARA_SUN})")
print(f"R_eq  = {R_EQ:.4f} (snap at ARA={ARA_EQ})")

# ── Time as sphere: value function ─────────────────────────────────
def sphere_value(phi_time, R):
    """Value of the sphere at temporal longitude φ with radius R.
    This is the Δlog that time's geometry imposes on the system."""
    return R * np.sin(phi_time / R)

# ── APPROACH 1: Absolute phase mapping ─────────────────────────────
# Map each system's value to a temporal longitude,
# then advance and read off the prediction.
print(f"\n{'='*60}")
print("APPROACH 1: VALUE → LONGITUDE → ADVANCE → PREDICT")
print(f"{'='*60}")
print()
print("Each system's value at time t maps to a longitude on time's sphere.")
print("log₁₀(V) = R·sin(φ/R) + C, so �� = R·arcsin((log₁₀(V) - C) / R)")
print()

# For sunspots: C = mean of log₁₀(SSN)
ssn_vals = np.array([sun_annual_mean[y] for y in overlap_years])
ssn_log = np.log10(np.maximum(ssn_vals, 0.1))
C_sun = np.mean(ssn_log)

eq_vals = np.array([eq_annual_m7[y] for y in overlap_years])
eq_log = np.log10(np.maximum(eq_vals, 0.1))
C_eq = np.mean(eq_log)

print(f"C_sun (mean log₁₀ SSN): {C_sun:.4f}")
print(f"C_eq (mean log₁₀ M7+): {C_eq:.4f}")

def value_to_longitude(log_val, C, R):
    """Invert the sphere function: log₁₀(V) = R·sin(φ/R) + C → φ."""
    normalized = (log_val - C) / R
    # Clamp to [-1, 1] for arcsin
    normalized = np.clip(normalized, -1, 1)
    return R * np.arcsin(normalized)

def longitude_to_value(phi, C, R):
    """Forward: φ → log₁₀(V) = R·sin(φ/R) + C → V."""
    log_val = R * np.sin(phi / R) + C
    return 10**log_val

# Test: can we recover the values through the round-trip?
print("\n─── Round-trip check ───")
phi_sun_test = value_to_longitude(ssn_log[0], C_sun, R_SUN)
val_recovered = longitude_to_value(phi_sun_test, C_sun, R_SUN)
print(f"  SSN[0] = {ssn_vals[0]:.1f}, longitude = {phi_sun_test:.4f}, "
      f"recovered = {val_recovered:.1f}")

# ── Temporal advance rate ──────────────────────────────────────────
# How much does longitude advance per year?
# The system's natural cycle determines this.
# Sunspots: ~11 year cycle → Δφ = 2π/11 per year
# Earthquakes: no periodicity → Δφ from data

# For sunspots: fit the advance rate from actual data
phi_sun_all = np.array([value_to_longitude(l, C_sun, R_SUN) for l in ssn_log])

# The advance rate should show the ~11 year cycle
# Let's compute the actual dφ/dt from consecutive years
dphi_sun = np.diff(phi_sun_all)

print(f"\n─── Temporal advance rates ───")
print(f"  Sunspot mean Δφ/year: {np.mean(dphi_sun):.4f}")
print(f"  Sunspot std Δφ/year:  {np.std(dphi_sun):.4f}")

# For a clean test: use multiple candidate advance rates
# and find which one best predicts
print(f"\n{'='*60}")
print("SCANNING ADVANCE RATES")
print(f"{'='*60}")
print()

# Candidate: cycle period T → Δφ = 2π/T per year
periods = [5, 7, 9, 10, 11, 13, 22, PHI*7, np.pi*3.5, 
           1/PHI * 20, 2*np.pi, 11*PHI/np.pi, PHI**4]
period_names = ['5yr', '7yr', '9yr', '10yr', '11yr', '13yr', '22yr',
                f'{PHI*7:.1f}yr', f'{np.pi*3.5:.1f}yr',
                f'{1/PHI*20:.1f}yr', '2π yr', f'{11*PHI/np.pi:.1f}yr',
                f'φ⁴={PHI**4:.1f}yr']

best_ssn_corr = 0
best_ssn_period = 0
best_eq_corr = 0
best_eq_period = 0

header = f"{'Period':>12s}  {'SSN corr':>9s}  {'SSN beats':>9s}  {'EQ corr':>8s}  {'EQ beats':>8s}  {'Cross':>7s}"
print(header)
print("-" * 65)

for T_cycle, T_name in zip(periods, period_names):
    dphi = 2 * np.pi / T_cycle
    
    ssn_preds = []
    ssn_acts = []
    eq_preds = []
    eq_acts = []
    
    for i in range(len(overlap_years) - 1):
        year = overlap_years[i]
        next_year = overlap_years[i + 1]
        
        ssn = sun_annual_mean[year]
        eq = eq_annual_m7[year]
        ssn_next = sun_annual_mean[next_year]
        eq_next = eq_annual_m7[next_year]
        
        if ssn <= 0 or eq <= 0:
            continue
        
        # Map current value to longitude on time's sphere
        phi_now_sun = value_to_longitude(np.log10(ssn), C_sun, R_SUN)
        phi_now_eq = value_to_longitude(np.log10(eq), C_eq, R_EQ)
        
        # Advance longitude by Δφ (one year of time)
        phi_next_sun = phi_now_sun + dphi
        phi_next_eq = phi_now_eq + dphi
        
        # Read off predicted values at new longitude
        ssn_pred = longitude_to_value(phi_next_sun, C_sun, R_SUN)
        eq_pred = longitude_to_value(phi_next_eq, C_eq, R_EQ)
        
        ssn_preds.append(ssn_pred)
        ssn_acts.append(ssn_next)
        eq_preds.append(eq_pred)
        eq_acts.append(eq_next)
    
    ssn_preds = np.array(ssn_preds)
    ssn_acts = np.array(ssn_acts)
    eq_preds = np.array(eq_preds)
    eq_acts = np.array(eq_acts)
    
    # Correlations
    corr_ssn = np.corrcoef(ssn_preds, ssn_acts)[0, 1] if np.std(ssn_preds) > 0 else 0
    corr_eq = np.corrcoef(eq_preds, eq_acts)[0, 1] if np.std(eq_preds) > 0 else 0
    
    # Beats naive (same value prediction)?
    naive_ssn = np.array([sun_annual_mean[overlap_years[i]] for i in range(len(overlap_years)-1) 
                          if sun_annual_mean[overlap_years[i]] > 0 and eq_annual_m7[overlap_years[i]] > 0])
    naive_eq = np.array([eq_annual_m7[overlap_years[i]] for i in range(len(overlap_years)-1)
                         if sun_annual_mean[overlap_years[i]] > 0 and eq_annual_m7[overlap_years[i]] > 0])
    
    beats_ssn = np.sum(np.abs(ssn_preds - ssn_acts) < np.abs(naive_ssn - ssn_acts)) / len(ssn_acts) * 100
    beats_eq = np.sum(np.abs(eq_preds - eq_acts) < np.abs(naive_eq - eq_acts)) / len(eq_acts) * 100
    
    # Cross-scale: does SSN's sphere longitude predict EQ?
    cross_corr = np.corrcoef(ssn_preds / ssn_preds.mean(), eq_acts / eq_acts.mean())[0, 1]
    
    print(f"{T_name:>12s}  {corr_ssn:+9.4f}  {beats_ssn:8.1f}%  {corr_eq:+8.4f}  {beats_eq:7.1f}%  {cross_corr:+7.4f}")
    
    if abs(corr_ssn) > abs(best_ssn_corr):
        best_ssn_corr = corr_ssn
        best_ssn_period = T_cycle
    if abs(corr_eq) > abs(best_eq_corr):
        best_eq_corr = corr_eq
        best_eq_period = T_cycle

print(f"\nBest SSN period: {best_ssn_period:.1f}yr (corr = {best_ssn_corr:+.4f})")
print(f"Best EQ period:  {best_eq_period:.1f}yr (corr = {best_eq_corr:+.4f})")

# ── APPROACH 2: Differential — sphere curvature determines change rate ──
print(f"\n{'='*60}")
print("APPROACH 2: SPHERE CURVATURE → RATE OF CHANGE")
print(f"{'='*60}")
print()
print("The DERIVATIVE of the sphere value gives the rate of change.")
print("dV/dφ = cos(φ/R)")
print("Systems at different R have different curvatures → different change rates.")
print()

# At each year, compute the sphere derivative at each system's longitude
# This derivative predicts the DIRECTION and MAGNITUDE of change
ssn_derivs = []
eq_derivs = []
ssn_actual_changes = []
eq_actual_changes = []

for i in range(len(overlap_years) - 1):
    year = overlap_years[i]
    next_year = overlap_years[i + 1]
    
    ssn = sun_annual_mean[year]
    eq = eq_annual_m7[year]
    
    if ssn <= 0 or eq <= 0:
        continue
    
    phi_sun = value_to_longitude(np.log10(ssn), C_sun, R_SUN)
    phi_eq = value_to_longitude(np.log10(eq), C_eq, R_EQ)
    
    # Sphere derivative at current position
    # dV/dφ = d/dφ[R·sin(φ/R)] = cos(φ/R)
    deriv_sun = np.cos(phi_sun / R_SUN)
    deriv_eq = np.cos(phi_eq / R_EQ)
    
    ssn_derivs.append(deriv_sun)
    eq_derivs.append(deriv_eq)
    
    # Actual change (in log space)
    ssn_next = sun_annual_mean[next_year]
    eq_next = eq_annual_m7[next_year]
    
    ssn_actual_changes.append(np.log10(max(ssn_next, 0.1)) - np.log10(ssn))
    eq_actual_changes.append(np.log10(max(eq_next, 0.1)) - np.log10(eq))

ssn_derivs = np.array(ssn_derivs)
eq_derivs = np.array(eq_derivs)
ssn_changes = np.array(ssn_actual_changes)
eq_changes = np.array(eq_actual_changes)

# Does the sphere derivative predict the direction of change?
corr_deriv_ssn = np.corrcoef(ssn_derivs, ssn_changes)[0, 1]
corr_deriv_eq = np.corrcoef(eq_derivs, eq_changes)[0, 1]

# Does the SSN sphere derivative predict EQ change? (cross-scale)
corr_deriv_cross = np.corrcoef(ssn_derivs, eq_changes)[0, 1]

# Direction match
dir_match_ssn = np.sum(np.sign(ssn_derivs) == np.sign(ssn_changes)) / len(ssn_derivs) * 100
dir_match_eq = np.sum(np.sign(eq_derivs) == np.sign(eq_changes)) / len(eq_derivs) * 100
dir_match_cross = np.sum(np.sign(ssn_derivs) == np.sign(eq_changes)) / len(ssn_derivs) * 100

print(f"SSN sphere derivative vs actual change:")
print(f"  Correlation: {corr_deriv_ssn:+.4f}")
print(f"  Direction match: {dir_match_ssn:.1f}%")
print()
print(f"EQ sphere derivative vs actual change:")
print(f"  Correlation: {corr_deriv_eq:+.4f}")
print(f"  Direction match: {dir_match_eq:.1f}%")
print()
print(f"CROSS-SCALE: SSN derivative vs EQ change:")
print(f"  Correlation: {corr_deriv_cross:+.4f}")
print(f"  Direction match: {dir_match_cross:.1f}%")

# ── APPROACH 3: Curvature ratio between latitudes ──────────────────
print(f"\n{'='*60}")
print("APPROACH 3: CURVATURE RATIO BETWEEN LATITUDES")
print(f"{'='*60}")
print()
print("If time IS the sphere, then the RATIO of curvatures at two")
print("latitudes should predict the ratio of temporal changes.")
print("κ_sun / κ_eq should predict Δlog_sun / Δlog_eq")
print()

# Curvature of R·sin(φ/R) at position φ:
# Second derivative: d²V/dφ² = -(1/R)·sin(φ/R)
# Curvature (unsigned): |sin(φ/R)| / R

# For each year: compute curvature at each system's longitude
curvature_ratios = []
change_ratios = []

for i in range(len(overlap_years) - 1):
    year = overlap_years[i]
    
    ssn = sun_annual_mean[year]
    eq = eq_annual_m7[year]
    
    if ssn <= 0 or eq <= 0:
        continue
    
    phi_sun = value_to_longitude(np.log10(ssn), C_sun, R_SUN)
    phi_eq = value_to_longitude(np.log10(eq), C_eq, R_EQ)
    
    # Curvature at each position
    kappa_sun = abs(np.sin(phi_sun / R_SUN)) / R_SUN
    kappa_eq = abs(np.sin(phi_eq / R_EQ)) / R_EQ
    
    if kappa_eq > 0.001 and abs(eq_changes[i]) > 0.001:
        curvature_ratios.append(kappa_sun / kappa_eq)
        change_ratios.append(abs(ssn_changes[i]) / abs(eq_changes[i]))

if len(curvature_ratios) > 10:
    curv_ratios = np.array(curvature_ratios)
    chg_ratios = np.array(change_ratios)
    
    # Clip outliers
    mask = (chg_ratios < np.percentile(chg_ratios, 95)) & (curv_ratios < np.percentile(curv_ratios, 95))
    curv_ratios_clean = curv_ratios[mask]
    chg_ratios_clean = chg_ratios[mask]
    
    corr_curv = np.corrcoef(curv_ratios_clean, chg_ratios_clean)[0, 1]
    print(f"Curvature ratio vs change ratio:")
    print(f"  N pairs: {len(curv_ratios_clean)}")
    print(f"  Correlation: {corr_curv:+.4f}")
    print(f"  Mean curvature ratio (κ_sun/κ_eq): {np.mean(curv_ratios_clean):.4f}")
    print(f"  Mean change ratio (|Δlog_sun/Δlog_eq|): {np.mean(chg_ratios_clean):.4f}")
    print(f"  R_SUN/R_EQ = {R_SUN/R_EQ:.4f} (predicted ratio if at same phase)")
else:
    print(f"  Insufficient valid pairs ({len(curvature_ratios)})")

# ── APPROACH 4: ALL systems compared via time's ARA topography ──────
print(f"\n{'='*60}")
print("APPROACH 4: TIME'S ARA TOPOGRAPHY — ALL SYSTEM POSITIONS")
print(f"{'='*60}")
print()
print("Map ALL ARA positions to time's sphere and check if the")
print("sphere predicts the relationship between all known systems.")
print()

# Known ARA values from the project
known_systems = {
    'Earthquake M7+': {'ara': 0.15, 'type': 'snap'},
    'Lightning': {'ara': 0.10, 'type': 'snap'},
    'Sea ice': {'ara': 0.91, 'type': 'clock'},
    'Blood glucose': {'ara': 1.20, 'type': 'clock'},
    'Walking gait': {'ara': 1.355, 'type': 'clock'},
    'Breath': {'ara': 1.61, 'type': 'engine'},
    'Heart': {'ara': 1.62, 'type': 'engine'},
    'Watershed': {'ara': 1.67, 'type': 'engine'},
    'Sunspots': {'ara': 1.73, 'type': 'engine'},
    'Cepheid': {'ara': 2.00, 'type': 'harmonic'},
}

print(f"{'System':>16s}  {'ARA':>5s}  {'θ (lat)':>8s}  {'R':>6s}  {'Max Δlog':>9s}  {'Curvature':>10s}")
print("-" * 62)

for name, info in sorted(known_systems.items(), key=lambda x: x[1]['ara']):
    ara = info['ara']
    theta = np.pi * (ara / 2.0)
    R = R_for_ara(ara)
    max_dlog = R  # maximum of R·sin(φ/R) is R
    # Curvature at equator (φ=0): d²/dφ² = 0, at peak: 1/R
    curv_at_peak = 1.0 / R
    
    print(f"{name:>16s}  {ara:5.2f}  {np.degrees(theta):7.1f}°  {R:6.3f}  {max_dlog:9.3f}  {curv_at_peak:10.4f}")

print(f"\nKey: Higher R → wider oscillation amplitude on time's sphere")
print(f"     Higher curvature → sharper turning at extremes")
print(f"     Snap systems (R=1.914) have widest swing but sharpest turn")
print(f"     Engine systems (R=φ) have moderate swing, moderate turn")
print(f"     This IS the ARA mechanism expressed as time geometry")

# ── The key geometric relationship ─────────────────────────────────
print(f"\n{'='*60}")
print("THE GEOMETRIC RELATIONSHIP")
print(f"{'='*60}")
print()
print("On time's sphere:")
print(f"  Snap (R=1.914): max amplitude = ±1.914 decades")
print(f"    → earthquakes can jump 1.9 orders of magnitude per cycle")
print(f"  Engine (R=φ):   max amplitude = ±1.618 decades")
print(f"    → sunspots can vary 1.6 orders of magnitude per cycle")
print(f"  Clock (R=1.354): max amplitude = ±1.354 decades")
print(f"    → gait/glucose vary 1.35 orders of magnitude per cycle")
print()
print("The RATIO of amplitudes:")
print(f"  Snap/Engine = {1.914/PHI:.4f}")
print(f"  Engine/Clock = {PHI/1.354:.4f}")
print(f"  Snap/Clock = {1.914/1.354:.4f}")

# Check actual data
ssn_log_range = ssn_log.max() - ssn_log.min()
eq_log_range = eq_log.max() - eq_log.min()
print(f"\nActual log₁₀ ranges:")
print(f"  Sunspots: {ssn_log_range:.3f} decades (predicted max: {2*R_SUN:.3f})")
print(f"  M7+ EQ:   {eq_log_range:.3f} decades (predicted max: {2*R_EQ:.3f})")
print(f"  Ratio actual:    {ssn_log_range/eq_log_range:.4f}")
print(f"  Ratio predicted: {R_SUN/R_EQ:.4f}")

# ── Overall scoring ─────────���──────────────────────────────────────
print(f"\n{'='*60}")
print("SCRIPT 164 VERDICT")
print(f"{'='*60}")

score = 0
total = 6

# 1. Best SSN correlation > 0.3?
if abs(best_ssn_corr) > 0.3:
    score += 1
    print(f"  [PASS] SSN temporal prediction corr: {best_ssn_corr:+.4f} (period={best_ssn_period:.1f}yr)")
else:
    print(f"  [FAIL] SSN temporal prediction corr: {best_ssn_corr:+.4f} (< 0.3)")

# 2. Sphere derivative predicts SSN direction > 55%?
if dir_match_ssn > 55:
    score += 1
    print(f"  [PASS] SSN direction from sphere: {dir_match_ssn:.1f}%")
else:
    print(f"  [FAIL] SSN direction from sphere: {dir_match_ssn:.1f}% (≤55%)")

# 3. Sphere derivative predicts EQ direction > 55%?
if dir_match_eq > 55:
    score += 1
    print(f"  [PASS] EQ direction from sphere: {dir_match_eq:.1f}%")
else:
    print(f"  [FAIL] EQ direction from sphere: {dir_match_eq:.1f}% (≤55%)")

# 4. Cross-scale derivative correlation > 0.05?
if abs(corr_deriv_cross) > 0.05:
    score += 1
    print(f"  [PASS] Cross-scale derivative corr: {corr_deriv_cross:+.4f}")
else:
    print(f"  [FAIL] Cross-scale derivative corr: {corr_deriv_cross:+.4f} (< 0.05)")

# 5. Log range ratio matches R ratio within 50%?
actual_ratio = ssn_log_range / eq_log_range
predicted_ratio = R_SUN / R_EQ
if abs(actual_ratio - predicted_ratio) / predicted_ratio < 0.5:
    score += 1
    print(f"  [PASS] Log range ratio: actual={actual_ratio:.3f}, predicted={predicted_ratio:.3f}")
else:
    print(f"  [FAIL] Log range ratio: actual={actual_ratio:.3f}, predicted={predicted_ratio:.3f}")

# 6. Best period is physically meaningful (near 11yr solar cycle)?
if abs(best_ssn_period - 11) < 3:
    score += 1
    print(f"  [PASS] Best SSN period {best_ssn_period:.1f}yr ≈ solar cycle (11yr)")
elif abs(best_ssn_period - 22) < 3:
    score += 1
    print(f"  [PASS] Best SSN period {best_ssn_period:.1f}yr ≈ Hale cycle (22yr)")
else:
    print(f"  [FAIL] Best SSN period {best_ssn_period:.1f}yr not near solar cycle")

print(f"\n  SCORE: {score}/{total}")

print(f"\nScript 164 complete.")
