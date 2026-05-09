#!/usr/bin/env python3
"""
Script 163: Sphere Triangulation — Sunspot-Earthquake-Time Triad
=================================================================

Dylan's insight: the circle formula uses 2 points (1D line).
The sphere needs 3 points to triangulate: System A, System B, 
and Time (the coupler). Three points on a sphere form a 
spherical triangle. The triangle constrains the prediction.

Geometry:
  - ARA value → colatitude θ on the sphere
    θ = π × (ARA / 2)
    ARA = 0 → θ = 0 (north pole, singularity)
    ARA = 1.0 → θ = π/2 (equator, coupler/boundary)
    ARA = 2.0 → θ = π (south pole, pure harmonics)
    
  - Phase in cycle → longitude φ
    φ = 2π × (position in cycle / cycle period)

Three vertices of the spherical triangle:
  S = Sunspot (ARA=1.73, solar cycle phase)
  E = Earthquake (ARA=0.15, seismic phase)
  T = Time (ARA=1.0, temporal phase)

The spherical triangle SET constrains the relationship.
Spherical excess = area of triangle = coupling strength.
Side lengths = great-circle distances = ARA gaps.
Angles = phase relationships.

Prediction method:
  Know: S₁ (sunspot value at t₁), time gap Δt
  Know: positions of S, E, T on sphere
  Predict: S₂ at t₂, and E₂ at t₂ (cross-scale)
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

# Earthquake M7+ annual counts (USGS reference data)
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
print(f"Overlapping years: {len(overlap_years)} ({overlap_years[0]}-{overlap_years[-1]})")

# Solar cycle maxima for phase calculation
solar_maxima = [1884, 1894, 1907, 1917, 1928, 1937, 1947, 1958,
                1968, 1979, 1989, 2000, 2014, 2025]

# ── ARA parameters ─────────────────────────────────────────────────
ARA_SUN = 1.73    # exothermic source
ARA_EQ = 0.15     # violent snap
ARA_TIME = 1.0    # coupler (equator)

# ── Sphere mapping ─────────────────────────────────────────────────
def ara_to_colatitude(ara):
    """Map ARA value [0, 2] to colatitude θ [0, π] on sphere."""
    return np.pi * (ara / 2.0)

def get_solar_phase(year):
    """Map year to longitude on sphere [0, 2π) based on solar cycle."""
    for i in range(len(solar_maxima) - 1):
        if solar_maxima[i] <= year < solar_maxima[i+1]:
            cycle_len = solar_maxima[i+1] - solar_maxima[i]
            return 2 * np.pi * (year - solar_maxima[i]) / cycle_len
    cycle_len = 11
    nearest = min(solar_maxima, key=lambda x: abs(x - year))
    return (2 * np.pi * (year - nearest) / cycle_len) % (2 * np.pi)

def sphere_point(theta, phi):
    """Convert (colatitude, longitude) to Cartesian (x, y, z) on unit sphere."""
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    return np.array([x, y, z])

def great_circle_distance(p1, p2):
    """Angular distance between two points on unit sphere (in radians)."""
    dot = np.clip(np.dot(p1, p2), -1, 1)
    return np.arccos(dot)

def spherical_triangle_area(a, b, c):
    """Area of spherical triangle given three side lengths (radians).
    Uses spherical excess formula: E = A + B + C - π
    Where A, B, C are the angles, computed from sides via spherical law of cosines."""
    # Spherical law of cosines for angles
    cos_A = (np.cos(a) - np.cos(b) * np.cos(c)) / (np.sin(b) * np.sin(c) + 1e-15)
    cos_B = (np.cos(b) - np.cos(a) * np.cos(c)) / (np.sin(a) * np.sin(c) + 1e-15)
    cos_C = (np.cos(c) - np.cos(a) * np.cos(b)) / (np.sin(a) * np.sin(b) + 1e-15)
    
    cos_A = np.clip(cos_A, -1, 1)
    cos_B = np.clip(cos_B, -1, 1)
    cos_C = np.clip(cos_C, -1, 1)
    
    A = np.arccos(cos_A)
    B = np.arccos(cos_B)
    C = np.arccos(cos_C)
    
    excess = A + B + C - np.pi  # spherical excess = area on unit sphere
    return excess, A, B, C

def formula_on_sphere(theta, phi, R):
    """The unified formula evaluated at a point on the sphere.
    Δlog = G(θ) + R·sin(G_phase(θ,φ) / R)
    
    G(θ) = colatitude component (dimensional gap)
    Phase = longitudinal component
    """
    G = theta  # colatitude IS the dimensional gap on the sphere
    phase = phi  # longitude IS the phase
    return G + R * np.sin(phase / R)

# ── Map system positions ───────────────────────────────────────────
theta_sun = ara_to_colatitude(ARA_SUN)
theta_eq = ara_to_colatitude(ARA_EQ)
theta_time = ara_to_colatitude(ARA_TIME)

print(f"\n=== SPHERE POSITIONS ===")
print(f"Sunspot:    θ = {np.degrees(theta_sun):.1f}°  (ARA = {ARA_SUN})")
print(f"Earthquake: θ = {np.degrees(theta_eq):.1f}°   (ARA = {ARA_EQ})")
print(f"Time:       θ = {np.degrees(theta_time):.1f}°  (ARA = {ARA_TIME})")

# ── Static triangle properties ─────────────────────────────────────
print(f"\n=== STATIC TRIANGLE (ARA positions only, φ=0) ===")
S0 = sphere_point(theta_sun, 0)
E0 = sphere_point(theta_eq, 0)
T0 = sphere_point(theta_time, 0)

side_SE = great_circle_distance(S0, E0)
side_ST = great_circle_distance(S0, T0)
side_ET = great_circle_distance(E0, T0)

print(f"Side S-E: {np.degrees(side_SE):.1f}° ({side_SE:.4f} rad)")
print(f"Side S-T: {np.degrees(side_ST):.1f}° ({side_ST:.4f} rad)")
print(f"Side E-T: {np.degrees(side_ET):.1f}° ({side_ET:.4f} rad)")

area, angle_S, angle_E, angle_T = spherical_triangle_area(side_SE, side_ST, side_ET)
print(f"\nAngles: S={np.degrees(angle_S):.1f}°, E={np.degrees(angle_E):.1f}°, T={np.degrees(angle_T):.1f}°")
print(f"Spherical excess (area): {area:.4f} sr = {np.degrees(area):.2f}°")
print(f"  (This is the coupling strength of the triad)")

# ── Phase-dependent sphere formula ─────────────────────────────────
# R values by system type:
R_SNAP = 1.914    # earthquake (discharge)
R_ENGINE = PHI    # sunspot magnetic dynamo
R_CLOCK = 1.354   # time (accumulator/clock)

print(f"\n=== SPHERE FORMULA VALUES ===")
print(f"R values: sunspot={R_ENGINE:.3f} (engine), earthquake={R_SNAP:.3f} (snap), time={R_CLOCK:.3f} (clock)")

# ── TRIANGULATION METHOD ───────────────────────────────────────────
print(f"\n{'='*60}")
print("TRIANGULATION PREDICTION")
print(f"{'='*60}")
print()
print("Method: Place S, E, T on sphere at their ARA latitudes.")
print("As time advances, the triangle rotates (time's longitude changes).")
print("The triangle's shape (sides, angles, area) at each moment")
print("determines the coupling between systems at that moment.")
print()

# The key idea: as the solar cycle progresses, the triangle changes shape
# because the sunspot longitude advances. The AREA of the triangle
# (spherical excess) at each year should correlate with the strength
# of sun-earthquake coupling at that year.

# For each year: 
#   1. Compute solar cycle phase → sunspot longitude
#   2. Earthquake longitude: earthquakes are aperiodic, but their
#      "phase" can be defined by the deviation from mean rate
#   3. Time longitude: advances uniformly (Δφ = 2π per year? per decade?)
#   4. Compute triangle properties
#   5. Use triangle to predict

# TIME'S PHASE: What does longitude mean for time?
# Time as ARA = 1.0 (equator). Its "cycle" is... what?
# Time's ARA came from Script 61: accumulation of events, release of consequences
# Time awareness correlates with |Δφ|
# For universal time: φ_time could advance at rate related to 
# the measurement timescale relative to the systems being coupled.
# For 1-year resolution coupling sun and earthquakes:
# φ_time = 2π × (year / coupling_period)
# 
# The coupling period between sun and earthquake is unknown —
# but the TRIANGLE can find it. If we scan coupling periods,
# the one that maximises predictive power IS the natural period.

print("─── Scanning time coupling periods ───")
print()

best_corr = 0
best_period = 0
best_method = ""

results = {}

for T_period in [1, 2, 3, 5, 7, 11, 13, 22, PHI*10, np.pi*10, 33, 50, 100]:
    T_label = f"{T_period:.1f}yr" if T_period != int(T_period) else f"{int(T_period)}yr"
    
    triangle_areas = []
    triangle_sides_SE = []
    triangle_angles_T = []
    ssn_vals = []
    eq_vals = []
    eq_next = []
    ssn_next = []
    
    for i, year in enumerate(overlap_years[:-1]):
        ssn = sun_annual_mean[year]
        eq = eq_annual_m7[year]
        
        if ssn <= 0 or eq <= 0:
            continue
        
        # Longitudes
        phi_sun = get_solar_phase(year)
        # Earthquake: map relative intensity to phase
        eq_mean = np.mean([eq_annual_m7[y] for y in overlap_years])
        phi_eq = 2 * np.pi * (eq / eq_mean - 0.5)  # deviation from mean → phase
        # Time: uniform advance
        phi_time = 2 * np.pi * ((year - overlap_years[0]) / T_period) % (2 * np.pi)
        
        # Three points on sphere
        S = sphere_point(theta_sun, phi_sun)
        E = sphere_point(theta_eq, phi_eq)
        T = sphere_point(theta_time, phi_time)
        
        # Triangle properties
        d_SE = great_circle_distance(S, E)
        d_ST = great_circle_distance(S, T)
        d_ET = great_circle_distance(E, T)
        
        if np.sin(d_ST) > 0.001 and np.sin(d_ET) > 0.001 and np.sin(d_SE) > 0.001:
            area, a_S, a_E, a_T = spherical_triangle_area(d_SE, d_ST, d_ET)
            triangle_areas.append(area)
            triangle_sides_SE.append(d_SE)
            triangle_angles_T.append(a_T)
        else:
            triangle_areas.append(0)
            triangle_sides_SE.append(d_SE)
            triangle_angles_T.append(0)
        
        ssn_vals.append(ssn)
        eq_vals.append(eq)
        
        # Next year values for prediction
        next_year = overlap_years[i + 1]
        ssn_next.append(sun_annual_mean[next_year])
        eq_next.append(eq_annual_m7[next_year])
    
    areas = np.array(triangle_areas)
    sides = np.array(triangle_sides_SE)
    angles_T = np.array(triangle_angles_T)
    ssn_arr = np.array(ssn_vals)
    eq_arr = np.array(eq_vals)
    ssn_next_arr = np.array(ssn_next)
    eq_next_arr = np.array(eq_next)
    
    # Test 1: Does triangle AREA predict next year's earthquake count?
    if len(areas) > 10 and np.std(areas) > 0:
        corr_area_eq = np.corrcoef(areas, eq_next_arr)[0, 1]
        corr_area_ssn = np.corrcoef(areas, ssn_next_arr)[0, 1]
    else:
        corr_area_eq = 0
        corr_area_ssn = 0
    
    # Test 2: Does S-E side length predict cross-scale relationship?
    if len(sides) > 10 and np.std(sides) > 0:
        # Ratio of next year's values
        ratio_next = np.log10(ssn_next_arr / eq_next_arr)
        corr_side_ratio = np.corrcoef(sides, ratio_next)[0, 1]
    else:
        corr_side_ratio = 0
    
    # Test 3: Does time's angle predict temporal change?
    if len(angles_T) > 10 and np.std(angles_T) > 0:
        dlog_ssn = np.log10(ssn_next_arr / ssn_arr)
        dlog_eq = np.log10(eq_next_arr / eq_arr)
        corr_angle_dssn = np.corrcoef(angles_T, dlog_ssn)[0, 1]
        corr_angle_deq = np.corrcoef(angles_T, dlog_eq)[0, 1]
    else:
        corr_angle_dssn = 0
        corr_angle_deq = 0
    
    # Track best
    max_corr = max(abs(corr_area_eq), abs(corr_area_ssn), abs(corr_side_ratio),
                   abs(corr_angle_dssn), abs(corr_angle_deq))
    
    results[T_label] = {
        'area_eq': corr_area_eq,
        'area_ssn': corr_area_ssn,
        'side_ratio': corr_side_ratio,
        'angle_dssn': corr_angle_dssn,
        'angle_deq': corr_angle_deq,
        'max': max_corr
    }
    
    if max_corr > abs(best_corr):
        best_corr = max_corr
        best_period = T_period

# Print results table
print(f"{'Period':>8s}  {'Area→EQ':>8s}  {'Area→SSN':>9s}  {'Side→Ratio':>10s}  {'∠T→ΔSSN':>8s}  {'∠T→ΔEQ':>8s}  {'MAX':>6s}")
print("-" * 72)
for label, r in sorted(results.items(), key=lambda x: -x[1]['max']):
    print(f"{label:>8s}  {r['area_eq']:+8.4f}  {r['area_ssn']:+9.4f}  {r['side_ratio']:+10.4f}  "
          f"{r['angle_dssn']:+8.4f}  {r['angle_deq']:+8.4f}  {r['max']:6.4f}")

print(f"\nBest coupling period: {best_period}")
print(f"Best |correlation|: {abs(best_corr):.4f}")

# ── FULL TRIANGULATION PREDICTION with best period ─────────────────
print(f"\n{'='*60}")
print(f"FULL PREDICTION — Time period = {best_period}")
print(f"{'='*60}")
print()

T_period = best_period
predictions_ssn = []
predictions_eq = []
actuals_ssn = []
actuals_eq = []

for i in range(len(overlap_years) - 1):
    year = overlap_years[i]
    next_year = overlap_years[i + 1]
    
    ssn = sun_annual_mean[year]
    eq = eq_annual_m7[year]
    
    if ssn <= 0 or eq <= 0:
        continue
    
    # Current sphere positions
    phi_sun = get_solar_phase(year)
    eq_mean = np.mean([eq_annual_m7[y] for y in overlap_years])
    phi_eq = 2 * np.pi * (eq / eq_mean - 0.5)
    phi_time = 2 * np.pi * ((year - overlap_years[0]) / T_period) % (2 * np.pi)
    
    S = sphere_point(theta_sun, phi_sun)
    E = sphere_point(theta_eq, phi_eq)
    T_pt = sphere_point(theta_time, phi_time)
    
    # Next year: time advances by 1/T_period of a revolution
    phi_time_next = (phi_time + 2 * np.pi / T_period) % (2 * np.pi)
    # Sun advances by ~1/11 of a revolution
    phi_sun_next = get_solar_phase(next_year)
    
    S_next = sphere_point(theta_sun, phi_sun_next)
    T_next = sphere_point(theta_time, phi_time_next)
    
    # The formula value at the new sunspot position
    formula_val_sun = formula_on_sphere(theta_sun, phi_sun_next, R_ENGINE)
    formula_val_eq = formula_on_sphere(theta_eq, phi_eq, R_SNAP)
    
    # Triangle at next timestep
    d_SE_next = great_circle_distance(S_next, E)  # E hasn't moved yet
    d_ST_next = great_circle_distance(S_next, T_next)
    d_ET_next = great_circle_distance(E, T_next)
    
    if (np.sin(d_ST_next) > 0.001 and np.sin(d_ET_next) > 0.001 
        and np.sin(d_SE_next) > 0.001):
        area_next, a_S, a_E, a_T = spherical_triangle_area(d_SE_next, d_ST_next, d_ET_next)
    else:
        area_next = 0
    
    # PREDICTION via sphere:
    # The formula evaluated at the sunspot's new position gives
    # the predicted Δlog relative to the triangle's centroid
    # Scale by triangle area (coupling strength)
    
    # For sunspot prediction: advance on the solar circle
    # Δlog_sun = R_engine · sin(Δφ_sun / R_engine) × (area / π)
    dphi_sun = phi_sun_next - phi_sun
    dlog_sun_pred = R_ENGINE * np.sin(dphi_sun / R_ENGINE) * (area_next / np.pi)
    ssn_pred = ssn * 10**(dlog_sun_pred)
    
    # For earthquake prediction: use triangle coupling
    # The earthquake system's response = sun change * coupling factor
    # Coupling factor = sin(angle at T) / sin(angle at S) 
    # (how much of the solar change reaches earthquakes through time)
    if a_S > 0.001:
        coupling = np.sin(a_T) / np.sin(a_S)
    else:
        coupling = 1.0
    
    dlog_eq_pred = dlog_sun_pred * coupling * (ARA_EQ / ARA_SUN)
    eq_pred = eq * 10**(dlog_eq_pred)
    
    predictions_ssn.append(ssn_pred)
    predictions_eq.append(eq_pred)
    actuals_ssn.append(sun_annual_mean[next_year])
    actuals_eq.append(eq_annual_m7[next_year])

pred_ssn = np.array(predictions_ssn)
pred_eq = np.array(predictions_eq)
act_ssn = np.array(actuals_ssn)
act_eq = np.array(actuals_eq)

print("─── Sunspot next-year prediction ───")
corr_ssn = np.corrcoef(pred_ssn, act_ssn)[0, 1]
err_ssn = np.mean(np.abs(pred_ssn - act_ssn))
naive_err_ssn = np.mean(np.abs(np.array([sun_annual_mean[y] for y in overlap_years[:-1]]) - act_ssn))
within_10x_ssn = np.sum(np.abs(np.log10(np.maximum(pred_ssn, 0.1) / np.maximum(act_ssn, 0.1))) < 1.0) / len(act_ssn) * 100
beats_naive_ssn = np.sum(np.abs(pred_ssn - act_ssn) < np.abs(
    np.array([sun_annual_mean[y] for y in overlap_years[:-1]]) - act_ssn)) / len(act_ssn) * 100

print(f"  Correlation (predicted vs actual): {corr_ssn:+.4f}")
print(f"  Mean absolute error: {err_ssn:.1f} (naive: {naive_err_ssn:.1f})")
print(f"  Within 10×: {within_10x_ssn:.1f}%")
print(f"  Beats naive: {beats_naive_ssn:.1f}%")

print("\n─── Earthquake next-year prediction ───")
corr_eq = np.corrcoef(pred_eq, act_eq)[0, 1]
err_eq = np.mean(np.abs(pred_eq - act_eq))
naive_err_eq = np.mean(np.abs(np.array([eq_annual_m7[y] for y in overlap_years[:-1]]) - act_eq))
within_10x_eq = np.sum(np.abs(np.log10(np.maximum(pred_eq, 0.1) / np.maximum(act_eq, 0.1))) < 1.0) / len(act_eq) * 100
beats_naive_eq = np.sum(np.abs(pred_eq - act_eq) < np.abs(
    np.array([eq_annual_m7[y] for y in overlap_years[:-1]]) - act_eq)) / len(act_eq) * 100

print(f"  Correlation (predicted vs actual): {corr_eq:+.4f}")
print(f"  Mean absolute error: {err_eq:.1f} (naive: {naive_err_eq:.1f})")
print(f"  Within 10×: {within_10x_eq:.1f}%")
print(f"  Beats naive: {beats_naive_eq:.1f}%")

# ── Cross-scale: given SSN change, predict EQ change ───────────────
print(f"\n─── Cross-scale: SSN temporal change → EQ temporal change ───")
dlog_ssn_actual = np.log10(np.maximum(act_ssn, 0.1)) - np.log10(np.maximum(
    np.array([sun_annual_mean[y] for y in overlap_years[:-1]]), 0.1))
dlog_eq_actual = np.log10(np.maximum(act_eq, 0.1)) - np.log10(np.maximum(
    np.array([eq_annual_m7[y] for y in overlap_years[:-1]]), 0.1))

# Use sphere geometry to translate SSN change into EQ change
# The ARA ratio between systems modulates the amplitude
dlog_eq_from_ssn = dlog_ssn_actual * (ARA_EQ / ARA_SUN)
corr_cross = np.corrcoef(dlog_eq_from_ssn, dlog_eq_actual)[0, 1]
print(f"  Simple ARA ratio: corr = {corr_cross:+.4f}")

# Sphere-modulated: scale by triangle area variation
# Recompute areas for each year
areas_yearly = []
for year in overlap_years[:-1]:
    ssn = sun_annual_mean[year]
    eq = eq_annual_m7[year]
    eq_mean = np.mean([eq_annual_m7[y] for y in overlap_years])
    
    phi_sun = get_solar_phase(year)
    phi_eq = 2 * np.pi * (eq / eq_mean - 0.5)
    phi_time = 2 * np.pi * ((year - overlap_years[0]) / best_period) % (2 * np.pi)
    
    S = sphere_point(theta_sun, phi_sun)
    E = sphere_point(theta_eq, phi_eq)
    T = sphere_point(theta_time, phi_time)
    
    d_SE = great_circle_distance(S, E)
    d_ST = great_circle_distance(S, T)
    d_ET = great_circle_distance(E, T)
    
    if np.sin(d_ST) > 0.001 and np.sin(d_ET) > 0.001 and np.sin(d_SE) > 0.001:
        a, _, _, _ = spherical_triangle_area(d_SE, d_ST, d_ET)
        areas_yearly.append(a)
    else:
        areas_yearly.append(0)

areas_yearly = np.array(areas_yearly)
if np.std(areas_yearly) > 0:
    area_norm = areas_yearly / np.mean(areas_yearly[areas_yearly > 0])
else:
    area_norm = np.ones_like(areas_yearly)

dlog_eq_sphere = dlog_ssn_actual * (ARA_EQ / ARA_SUN) * area_norm
corr_sphere = np.corrcoef(dlog_eq_sphere, dlog_eq_actual)[0, 1]
print(f"  Sphere-modulated (area weighting): corr = {corr_sphere:+.4f}")

# ── Special values check ──────────────────────────────────────────
print(f"\n{'='*60}")
print("SPECIAL VALUES CHECK")
print(f"{'='*60}")

# Do the triangle properties land on ARA special values?
mean_area = np.mean(areas_yearly[areas_yearly > 0])
print(f"\n  Mean triangle area: {mean_area:.4f} rad²")
print(f"  Area / π: {mean_area/np.pi:.4f}")
print(f"  Area / φ: {mean_area/PHI:.4f}")
print(f"  Side S-E (static): {side_SE:.4f} = {side_SE/np.pi:.4f}π")
print(f"  Side S-T (static): {side_ST:.4f} = {side_ST/np.pi:.4f}π")
print(f"  Side E-T (static): {side_ET:.4f} = {side_ET/np.pi:.4f}π")
print(f"  S-E / S-T ratio:   {side_SE/side_ST:.4f} (φ = {PHI:.4f})")
print(f"  E-T / S-T ratio:   {side_ET/side_ST:.4f}")
print(f"  E-T / S-E ratio:   {side_ET/side_SE:.4f}")

# ── Overall scoring ────────────────────────────────────────────────
print(f"\n{'='*60}")
print("SCRIPT 163 VERDICT")
print(f"{'='*60}")

score = 0
total = 6

# 1. Sunspot prediction: beats naive?
if beats_naive_ssn > 50:
    score += 1
    print(f"  [PASS] SSN sphere prediction beats naive {beats_naive_ssn:.1f}%")
else:
    print(f"  [FAIL] SSN sphere prediction beats naive only {beats_naive_ssn:.1f}%")

# 2. Earthquake prediction: beats naive?
if beats_naive_eq > 50:
    score += 1
    print(f"  [PASS] EQ sphere prediction beats naive {beats_naive_eq:.1f}%")
else:
    print(f"  [FAIL] EQ sphere prediction beats naive only {beats_naive_eq:.1f}%")

# 3. Correlation with actuals > 0.3?
max_corr = max(abs(corr_ssn), abs(corr_eq))
if max_corr > 0.3:
    score += 1
    print(f"  [PASS] Best correlation: {max_corr:.4f}")
else:
    print(f"  [FAIL] Best correlation: {max_corr:.4f} (< 0.3)")

# 4. Cross-scale translation improved by sphere?
if abs(corr_sphere) > abs(corr_cross) + 0.02:
    score += 1
    print(f"  [PASS] Sphere improves cross-scale: {corr_sphere:+.4f} vs {corr_cross:+.4f}")
else:
    print(f"  [FAIL] Sphere doesn't improve: {corr_sphere:+.4f} vs {corr_cross:+.4f}")

# 5. Best coupling period is physically meaningful?
meaningful_periods = [11, 22, PHI*10]  # solar cycle, double cycle, φ-scaled
closest = min(meaningful_periods, key=lambda x: abs(x - best_period))
if abs(best_period - closest) / closest < 0.2:
    score += 1
    print(f"  [PASS] Best period {best_period} near meaningful value {closest:.1f}")
else:
    print(f"  [FAIL] Best period {best_period} not near expected values")

# 6. Triangle area has special value relationship?
area_over_pi = mean_area / np.pi
ratios_to_check = [1/PHI, PHI-1, 1/np.pi, 1/np.e, 0.5, 1/3]
names_to_check = ['1/φ', 'φ-1', '1/π', '1/e', '1/2', '1/3']
close_match = False
for val, name in zip(ratios_to_check, names_to_check):
    if abs(area_over_pi - val) < 0.05:
        score += 1
        close_match = True
        print(f"  [PASS] Triangle area/π ≈ {name} ({area_over_pi:.4f} vs {val:.4f})")
        break
if not close_match:
    print(f"  [FAIL] Triangle area/π = {area_over_pi:.4f} — no special value match")

print(f"\n  SCORE: {score}/{total}")

print(f"\nScript 163 complete.")
