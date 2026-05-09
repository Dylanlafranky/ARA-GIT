#!/usr/bin/env python3
"""
Script 165: Three-Sphere Water Molecule — Scan for the Third Sphere
=====================================================================

Dylan's insight: prediction needs THREE spheres locked together in ARA,
like the water molecule (H-O-H). Two spheres (time + matter) give a 
line. Three spheres give the full constraint.

The three spheres:
  1. TIME   — ARA = 1.0 (the manifold/coupler, equator)
  2. MATTER — ARA = system-specific (sunspot=1.73, earthquake=0.15)
  3. ???    — ARA = unknown (Energy? Information? Light?)

Method:
  - Scan the third sphere's ARA from 0.01 to 2.0
  - At each value, compute the three-sphere water molecule geometry:
    * Bond angle between the three spheres
    * Coupling strength (spherical triangle area)
  - Use the three-sphere geometry to predict temporal changes
  - Find which ARA value maximises predictive power
  - Check if the optimal value lands on a special number (φ, π/2, e, etc.)
  
The water molecule effect:
  - Three ARA values → three colatitudes on the sphere
  - The ANGLE between them determines the coupling geometry
  - In water: H-O-H angle = 104.5° (set by sp³ hybridisation)
  - In ARA: the angle between Time-Matter-Third determines prediction power
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
N = len(overlap_years)

# Pre-compute annual arrays
ssn_arr = np.array([sun_annual_mean[y] for y in overlap_years])
eq_arr = np.array([eq_annual_m7[y] for y in overlap_years])
ssn_log = np.log10(np.maximum(ssn_arr, 0.1))
eq_log = np.log10(np.maximum(eq_arr, 0.1))

# Year-over-year changes
dlog_ssn = np.diff(ssn_log)
dlog_eq = np.diff(eq_log)

print(f"Data: {N} years ({overlap_years[0]}-{overlap_years[-1]})")
print(f"SSN range: {ssn_arr.min():.1f}-{ssn_arr.max():.1f}")
print(f"M7+ range: {eq_arr.min()}-{eq_arr.max()}")

# ── ARA positions ──────────────────────────────────────────────────
ARA_TIME = 1.0
ARA_SUN = 1.73
ARA_EQ = 0.15

# Solar cycle maxima for phase
solar_maxima = [1884, 1894, 1907, 1917, 1928, 1937, 1947, 1958,
                1968, 1979, 1989, 2000, 2014, 2025]

def get_solar_phase(year):
    for i in range(len(solar_maxima) - 1):
        if solar_maxima[i] <= year < solar_maxima[i+1]:
            cycle_len = solar_maxima[i+1] - solar_maxima[i]
            return 2 * np.pi * (year - solar_maxima[i]) / cycle_len
    return (2 * np.pi * (year - 2014) / 11) % (2 * np.pi)

# ── Sphere geometry functions ──────────────────────────────────────
def ara_to_theta(ara):
    """ARA value [0,2] → colatitude [0,π]."""
    return np.pi * (ara / 2.0)

def R_for_ara(ara):
    """Phase radius from ARA position."""
    if ara < 0.5:
        return 1.914
    elif ara < 1.2:
        return 1.354
    elif ara < 1.85:
        return PHI
    else:
        return 1.73

def sphere_xyz(theta, phi):
    return np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])

def gc_dist(p1, p2):
    return np.arccos(np.clip(np.dot(p1, p2), -1, 1))

def bond_angle(p_center, p1, p2):
    """Angle at center between p1 and p2, on the sphere."""
    v1 = p1 - np.dot(p1, p_center) * p_center  # project onto tangent plane at center
    v2 = p2 - np.dot(p2, p_center) * p_center
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    if n1 < 1e-10 or n2 < 1e-10:
        return 0
    cos_angle = np.clip(np.dot(v1, v2) / (n1 * n2), -1, 1)
    return np.arccos(cos_angle)

# ── THREE-SPHERE PREDICTION FUNCTION ──────────────────────────────
def predict_with_three_spheres(ARA_third, ARA_matter, system_log, system_dlog,
                                phase_func=None, years=None):
    """
    Three spheres locked in water molecule geometry:
      Time (ARA=1.0) - Matter (ARA=system) - Third (ARA=scanned)
    
    The prediction uses:
    1. Bond angle at Matter vertex → determines how Time and Third couple
    2. R values at each latitude → determines amplitude of oscillation
    3. The Third sphere's contribution modulates the temporal prediction
    
    Returns correlation between predicted and actual year-over-year changes.
    """
    theta_time = ara_to_theta(ARA_TIME)
    theta_matter = ara_to_theta(ARA_matter)
    theta_third = ara_to_theta(ARA_third)
    
    R_matter = R_for_ara(ARA_matter)
    R_third = R_for_ara(ARA_third)
    R_time = R_for_ara(ARA_TIME)
    
    predictions = []
    
    for i in range(len(years) - 1):
        year = years[i]
        
        # Matter's longitude: from its current value
        C = np.mean(system_log)
        normalized = np.clip((system_log[i] - C) / R_matter, -1, 1)
        phi_matter = R_matter * np.arcsin(normalized)
        
        # Time's longitude: solar cycle phase (universal clock)
        phi_time = get_solar_phase(year)
        
        # Third sphere's longitude: derived from the coupling
        # The third sphere's phase = function of both time and matter
        # It oscillates between them — like a vine between supports
        # Phase = weighted average based on ARA distances
        d_time_matter = abs(ARA_TIME - ARA_matter)
        d_third_matter = abs(ARA_third - ARA_matter)
        d_third_time = abs(ARA_third - ARA_TIME)
        total_d = d_time_matter + d_third_matter + d_third_time + 1e-10
        
        # Third's longitude = weighted combination
        w_time = 1.0 - d_third_time / total_d
        w_matter = 1.0 - d_third_matter / total_d
        phi_third = w_time * phi_time + w_matter * phi_matter
        
        # Place on sphere
        T_pt = sphere_xyz(theta_time, phi_time)
        M_pt = sphere_xyz(theta_matter, phi_matter)
        X_pt = sphere_xyz(theta_third, phi_third)
        
        # Water molecule geometry: bond angle at Matter
        angle_at_matter = bond_angle(M_pt, T_pt, X_pt)
        
        # Coupling strength from triangle
        d_TM = gc_dist(T_pt, M_pt)
        d_TX = gc_dist(T_pt, X_pt)
        d_MX = gc_dist(M_pt, X_pt)
        
        # The formula on the sphere at matter's position,
        # MODULATED by the water molecule geometry:
        # Δlog = R_matter · sin(phi_matter / R_matter) · cos(angle/2)
        # The cos(angle/2) term is the water molecule's coupling factor
        # At angle = 0: full coupling. At angle = π: anti-coupling.
        # At water's angle (104.5° = 1.824 rad): cos(52.25°) = 0.612
        
        coupling_factor = np.cos(angle_at_matter / 2)
        
        # The third sphere ALSO contributes its own oscillation
        # The third sphere's value at its longitude:
        third_contribution = R_third * np.sin(phi_third / R_third)
        
        # Combined prediction: matter's own change + third sphere's modulation
        # Advance matter's longitude by one time step
        dphi_time = 2 * np.pi / 22  # Hale cycle (best from Script 164)
        
        phi_matter_next = phi_matter + dphi_time * coupling_factor
        
        # Predicted Δlog = change in sphere value at new longitude
        val_now = R_matter * np.sin(phi_matter / R_matter)
        val_next = R_matter * np.sin(phi_matter_next / R_matter)
        
        # Add third sphere's contribution, scaled by ARA distance
        dlog_pred = (val_next - val_now) + third_contribution * (d_MX / np.pi)
        
        predictions.append(dlog_pred)
    
    predictions = np.array(predictions)
    
    if np.std(predictions) < 1e-10:
        return 0, 0, predictions
    
    actual = system_dlog[:len(predictions)]
    corr = np.corrcoef(predictions, actual)[0, 1]
    
    # Direction match
    dir_match = np.sum(np.sign(predictions) == np.sign(actual)) / len(actual) * 100
    
    return corr, dir_match, predictions

# ── SCAN THIRD SPHERE ARA ─────────────────────────────────────────
print(f"\n{'='*60}")
print("SCANNING THIRD SPHERE ARA VALUE")
print(f"{'='*60}")
print()

# Fine scan from 0.01 to 2.0
ara_scan = np.concatenate([
    np.arange(0.01, 0.5, 0.02),
    np.arange(0.5, 1.5, 0.01),
    np.arange(1.5, 2.01, 0.02)
])

# Special values to mark
special_values = {
    '1/φ': 1/PHI,
    'φ-1': PHI-1,
    '1/π': 1/np.pi,
    '1/e': 1/np.e,
    '0.5': 0.5,
    '1/√2': 1/np.sqrt(2),
    '√2-1': np.sqrt(2)-1,
    'ln2': np.log(2),
    '1.0': 1.0,
    '2/π': 2/np.pi,
    'π/4': np.pi/4,
    'φ': PHI,
    '√φ': np.sqrt(PHI),
    'e/π': np.e/np.pi,
    'π/e': np.pi/np.e,
    '1/φ²': 1/PHI**2,
    '2φ-2': 2*PHI-2,
    'π-2': np.pi-2,
}

# Results storage
results_ssn = []
results_eq = []
results_cross = []

years_list = overlap_years

for ara_third in ara_scan:
    # Sunspot prediction
    corr_ssn, dir_ssn, preds_ssn = predict_with_three_spheres(
        ara_third, ARA_SUN, ssn_log, dlog_ssn, years=years_list)
    
    # Earthquake prediction
    corr_eq, dir_eq, preds_eq = predict_with_three_spheres(
        ara_third, ARA_EQ, eq_log, dlog_eq, years=years_list)
    
    # Cross-scale: does the SSN-tuned third sphere predict EQ?
    if len(preds_ssn) == len(dlog_eq):
        cross_corr = np.corrcoef(preds_ssn, dlog_eq[:len(preds_ssn)])[0, 1]
    else:
        cross_corr = 0
    
    results_ssn.append((ara_third, corr_ssn, dir_ssn))
    results_eq.append((ara_third, corr_eq, dir_eq))
    results_cross.append((ara_third, cross_corr))

# Find optima
results_ssn = np.array([(r[0], r[1], r[2]) for r in results_ssn])
results_eq = np.array([(r[0], r[1], r[2]) for r in results_eq])
results_cross = np.array([(r[0], r[1]) for r in results_cross])

# Best for SSN correlation
best_ssn_idx = np.argmax(np.abs(results_ssn[:, 1]))
best_ssn_ara = results_ssn[best_ssn_idx, 0]
best_ssn_corr = results_ssn[best_ssn_idx, 1]
best_ssn_dir = results_ssn[best_ssn_idx, 2]

# Best for EQ correlation
best_eq_idx = np.argmax(np.abs(results_eq[:, 1]))
best_eq_ara = results_eq[best_eq_idx, 0]
best_eq_corr = results_eq[best_eq_idx, 1]
best_eq_dir = results_eq[best_eq_idx, 2]

# Best for cross-scale
best_cross_idx = np.argmax(np.abs(results_cross[:, 1]))
best_cross_ara = results_cross[best_cross_idx, 0]
best_cross_corr = results_cross[best_cross_idx, 1]

# Combined score: SSN corr + EQ corr + cross corr
combined = np.abs(results_ssn[:, 1]) + np.abs(results_eq[:, 1]) + np.abs(results_cross[:, 1])
best_combined_idx = np.argmax(combined)
best_combined_ara = ara_scan[best_combined_idx]
best_combined_score = combined[best_combined_idx]

print(f"─── OPTIMAL ARA VALUES ───")
print(f"  Best for Sunspots:    ARA = {best_ssn_ara:.4f} (corr = {best_ssn_corr:+.4f}, dir = {best_ssn_dir:.1f}%)")
print(f"  Best for Earthquakes: ARA = {best_eq_ara:.4f} (corr = {best_eq_corr:+.4f}, dir = {best_eq_dir:.1f}%)")
print(f"  Best for Cross-scale: ARA = {best_cross_ara:.4f} (corr = {best_cross_corr:+.4f})")
print(f"  Best Combined:        ARA = {best_combined_ara:.4f} (score = {best_combined_score:.4f})")

# ── Check proximity to special values ──────────────────────────────
print(f"\n─── PROXIMITY TO SPECIAL VALUES ───")

for opt_name, opt_val in [("SSN optimal", best_ssn_ara), 
                           ("EQ optimal", best_eq_ara),
                           ("Cross optimal", best_cross_ara),
                           ("Combined optimal", best_combined_ara)]:
    closest_name = ""
    closest_dist = 999
    for sv_name, sv_val in special_values.items():
        dist = abs(opt_val - sv_val)
        if dist < closest_dist:
            closest_dist = dist
            closest_name = sv_name
    print(f"  {opt_name:18s} = {opt_val:.4f}, nearest special: {closest_name} = {special_values[closest_name]:.4f} (Δ = {closest_dist:.4f})")

# ── Print the landscape around optima ──────────────────────────────
print(f"\n─── SCAN LANDSCAPE (top 20 by combined score) ───")
sorted_idx = np.argsort(-combined)[:20]
print(f"  {'ARA':>6s}  {'SSN corr':>9s}  {'EQ corr':>8s}  {'Cross':>7s}  {'Combined':>8s}  {'Near':>8s}")
print("-" * 60)

for idx in sorted_idx:
    ara = ara_scan[idx]
    # Find nearest special value
    nearest = min(special_values.items(), key=lambda x: abs(x[1] - ara))
    near_str = f"{nearest[0]}" if abs(nearest[1] - ara) < 0.03 else ""
    print(f"  {ara:6.3f}  {results_ssn[idx,1]:+9.4f}  {results_eq[idx,1]:+8.4f}  "
          f"{results_cross[idx,1]:+7.4f}  {combined[idx]:8.4f}  {near_str:>8s}")

# ── BOND ANGLE ANALYSIS ───────────────────────────────────────────
print(f"\n{'='*60}")
print("WATER MOLECULE BOND ANGLE ANALYSIS")
print(f"{'='*60}")
print()

# For the combined optimal ARA, what's the bond angle?
for name, ara_third in [("Combined", best_combined_ara), 
                         ("SSN", best_ssn_ara), 
                         ("EQ", best_eq_ara)]:
    theta_T = ara_to_theta(ARA_TIME)
    theta_M_sun = ara_to_theta(ARA_SUN)
    theta_M_eq = ara_to_theta(ARA_EQ)
    theta_X = ara_to_theta(ara_third)
    
    # Static bond angles (all at φ=0)
    T_pt = sphere_xyz(theta_T, 0)
    S_pt = sphere_xyz(theta_M_sun, 0)
    E_pt = sphere_xyz(theta_M_eq, 0)
    X_pt = sphere_xyz(theta_X, 0)
    
    # Angle at Time between Matter and Third
    angle_at_T_sun = bond_angle(T_pt, S_pt, X_pt)
    angle_at_T_eq = bond_angle(T_pt, E_pt, X_pt)
    
    # Angle at Third between Time and Matter
    angle_at_X_sun = bond_angle(X_pt, T_pt, S_pt)
    angle_at_X_eq = bond_angle(X_pt, T_pt, E_pt)
    
    print(f"  {name} optimal (ARA = {ara_third:.4f}):")
    print(f"    Time-Third-Sun angle:  {np.degrees(angle_at_X_sun):.1f}°")
    print(f"    Time-Third-EQ angle:   {np.degrees(angle_at_X_eq):.1f}°")
    print(f"    Third-Time-Sun angle:  {np.degrees(angle_at_T_sun):.1f}°")
    print(f"    Third-Time-EQ angle:   {np.degrees(angle_at_T_eq):.1f}°")
    
    # Is any angle close to water's 104.5°?
    all_angles = [angle_at_X_sun, angle_at_X_eq, angle_at_T_sun, angle_at_T_eq]
    water_angle = 104.5
    closest_to_water = min(all_angles, key=lambda a: abs(np.degrees(a) - water_angle))
    print(f"    Closest to water's 104.5°: {np.degrees(closest_to_water):.1f}°")
    print()

# ── What does the optimal third sphere MEAN? ──────────────────────
print(f"{'='*60}")
print("INTERPRETATION: WHAT IS THE THIRD SPHERE?")
print(f"{'='*60}")
print()

# The combined optimal tells us what ARA value the third sphere needs
ara_opt = best_combined_ara
print(f"Optimal third sphere ARA: {ara_opt:.4f}")
print()

# Where does this sit on the ARA scale?
if ara_opt < 0.2:
    pos = "violent snap zone (lightning, earthquakes)"
elif ara_opt < 0.9:
    pos = "consumer zone (fire, avalanches)"
elif ara_opt < 1.3:
    pos = "shock absorber zone (glucose, sea ice, EEG)"
elif ara_opt < 1.5:
    pos = "clock-driven zone (walking gait)"
elif ara_opt < 1.7:
    pos = "sustained engine zone (breath, heart)"
elif ara_opt < 1.85:
    pos = "exothermic source zone (solar)"
else:
    pos = "near pure harmonics (Cepheid)"

print(f"ARA scale position: {pos}")
print()

# Check which candidate it most resembles
# Energy: E=mc², E=hf, thermodynamic. If energy conserves perfectly, ARA→1.0
# Information: Shannon entropy, Bekenstein bound. Optimal coding → φ
# Light: Speed = c, vacuum coupler. As system → Script 100 values

candidates = {
    'Energy (conservation → 1.0)': 1.0,
    'Energy (dissipation → φ)': PHI,
    'Information (optimal coding → φ)': PHI,
    'Information (entropy → e/π)': np.e/np.pi,
    'Information (bits → ln2)': np.log(2),
    'Light (vacuum coupler → 1.0)': 1.0,
    'Light (as system → φ)': PHI,
    'Light (speed ratio → 2/π)': 2/np.pi,
    'Gravity (vertical coupler → 1.0)': 1.0,
    'Space (3D → π/2)': np.pi/2,
}

print(f"  {'Candidate':>40s}  {'ARA':>6s}  {'Δ from opt':>10s}")
print("-" * 65)
for name, val in sorted(candidates.items(), key=lambda x: abs(x[1] - ara_opt)):
    delta = abs(val - ara_opt)
    marker = " ← CLOSEST" if delta == min(abs(v - ara_opt) for v in candidates.values()) else ""
    print(f"  {name:>40s}  {val:6.4f}  {delta:10.4f}{marker}")

# ── Overall verdict ────────────────────────────────────────────────
print(f"\n{'='*60}")
print("SCRIPT 165 VERDICT")
print(f"{'='*60}")

score = 0
total = 5

# 1. Did the scan find any ARA that gives |corr| > 0.3 for SSN?
if abs(best_ssn_corr) > 0.3:
    score += 1
    print(f"  [PASS] SSN prediction: corr = {best_ssn_corr:+.4f} at ARA = {best_ssn_ara:.4f}")
else:
    print(f"  [FAIL] SSN prediction: corr = {best_ssn_corr:+.4f} (< 0.3)")

# 2. Did it find |corr| > 0.15 for EQ?
if abs(best_eq_corr) > 0.15:
    score += 1
    print(f"  [PASS] EQ prediction: corr = {best_eq_corr:+.4f} at ARA = {best_eq_ara:.4f}")
else:
    print(f"  [FAIL] EQ prediction: corr = {best_eq_corr:+.4f} (< 0.15)")

# 3. Cross-scale |corr| > 0.1?
if abs(best_cross_corr) > 0.1:
    score += 1
    print(f"  [PASS] Cross-scale: corr = {best_cross_corr:+.4f} at ARA = {best_cross_ara:.4f}")
else:
    print(f"  [FAIL] Cross-scale: corr = {best_cross_corr:+.4f} (< 0.1)")

# 4. Optimal ARA lands near a special value (within 0.05)?
nearest_special = min(special_values.items(), key=lambda x: abs(x[1] - best_combined_ara))
if abs(nearest_special[1] - best_combined_ara) < 0.05:
    score += 1
    print(f"  [PASS] Optimal ARA {best_combined_ara:.4f} ≈ {nearest_special[0]} ({nearest_special[1]:.4f})")
else:
    print(f"  [FAIL] Optimal ARA {best_combined_ara:.4f} not near any special value (nearest: {nearest_special[0]} at {nearest_special[1]:.4f})")

# 5. Bond angle near water (104.5°) or other geometric angle?
geometric_angles = {
    'water': 104.5,
    'tetrahedral': 109.47,
    'equilateral': 60.0,
    'right angle': 90.0,
    '120° (hexagonal)': 120.0,
    'pentagon': 108.0,
    'φ angle': np.degrees(np.arccos(1/PHI)),
}

# Check all computed angles
all_computed_angles = []
for name, ara_third in [("Combined", best_combined_ara)]:
    theta_X = ara_to_theta(ara_third)
    T_pt = sphere_xyz(ara_to_theta(ARA_TIME), 0)
    S_pt = sphere_xyz(ara_to_theta(ARA_SUN), 0)
    X_pt = sphere_xyz(theta_X, 0)
    angle = bond_angle(X_pt, T_pt, S_pt)
    all_computed_angles.append(np.degrees(angle))

best_geom_match = None
best_geom_dist = 999
for gname, gval in geometric_angles.items():
    for ca in all_computed_angles:
        if abs(ca - gval) < best_geom_dist:
            best_geom_dist = abs(ca - gval)
            best_geom_match = gname

if best_geom_dist < 5:
    score += 1
    print(f"  [PASS] Bond angle near {best_geom_match} ({geometric_angles[best_geom_match]:.1f}°, Δ={best_geom_dist:.1f}°)")
else:
    print(f"  [FAIL] Bond angle not near geometric angle (nearest: {best_geom_match}, Δ={best_geom_dist:.1f}°)")

print(f"\n  SCORE: {score}/{total}")
print(f"\nScript 165 complete.")
