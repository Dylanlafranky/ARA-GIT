#!/usr/bin/env python3
"""
Script 166: Isosceles Triangle — φ/2 Phase Correction, Midpoint Geometry
=========================================================================

Dylan's construction:
  - Two couplers (Time and Third) both at ARA = 1.0
  - Separated by phase offset φ/2 (half phi, the ARA-native correction)
  - This opens the degenerate line into an isosceles triangle
  - The MATTER systems (sunspots, earthquakes) sit at their own ARA latitudes
  - The MIDPOINT of the matter systems on the ARA scale → ~0.94
  - The DISTANCE from that midpoint to the coupler (1.0) → ~0.06
  - This distance along the time axis determines the triangle's proportions

Geometry:
  Coupler 1 (Time):    θ = π/2 (equator), φ = 0
  Coupler 2 (Third):   θ = π/2 (equator), φ = φ_golden/2
  Matter system:       θ = π·(ARA/2), φ = from data
  
  Isosceles: both couplers equidistant from matter
  Base: great-circle distance between couplers = φ/2 in longitude
  Vertex: matter system at its ARA latitude

Prediction:
  The φ/2 offset corrects the anti-phase problem from Script 164.
  Instead of reading the sphere at the raw longitude,
  read it at longitude + φ/2 (shifted by half the golden ratio).
"""

import numpy as np
import os

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2  # = 0.80902...

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

ssn_arr = np.array([sun_annual_mean[y] for y in overlap_years])
eq_arr = np.array([eq_annual_m7[y] for y in overlap_years])
ssn_log = np.log10(np.maximum(ssn_arr, 0.1))
eq_log = np.log10(np.maximum(eq_arr, 0.1))
C_sun = np.mean(ssn_log)
C_eq = np.mean(eq_log)

dlog_ssn = np.diff(ssn_log)
dlog_eq = np.diff(eq_log)

print(f"Data: {N} years ({overlap_years[0]}-{overlap_years[-1]})")

# ── ARA positions and geometry ─────────────────────────────────────
ARA_SUN = 1.73
ARA_EQ = 0.15
ARA_COUPLER = 1.0

# Midpoint of the two matter systems
ARA_MIDPOINT = (ARA_SUN + ARA_EQ) / 2
DISTANCE_TO_COUPLER = abs(ARA_COUPLER - ARA_MIDPOINT)

print(f"\n=== ISOSCELES TRIANGLE GEOMETRY ===")
print(f"Coupler ARA: {ARA_COUPLER}")
print(f"Matter midpoint: ({ARA_SUN} + {ARA_EQ})/2 = {ARA_MIDPOINT:.4f}")
print(f"Distance midpoint → coupler: {DISTANCE_TO_COUPLER:.4f}")
print(f"Phase offset (φ/2): {HALF_PHI:.5f} rad = {np.degrees(HALF_PHI):.2f}°")

# The R value for the coupler position
R_COUPLER = 1.354  # clock/accumulator at ARA ≈ 1.0

def R_for_ara(ara):
    if ara < 0.5: return 1.914
    elif ara < 1.2: return 1.354
    elif ara < 1.85: return PHI
    else: return 1.73

R_SUN = R_for_ara(ARA_SUN)
R_EQ = R_for_ara(ARA_EQ)

print(f"R values: Sun={R_SUN:.4f}, EQ={R_EQ:.4f}, Coupler={R_COUPLER:.4f}")

# ── φ/2 CORRECTED PREDICTION ──────────────────────────────────────
print(f"\n{'='*60}")
print("TEST 1: φ/2 PHASE CORRECTION ON SPHERE")
print(f"{'='*60}")
print()
print("Script 164 found -0.48 correlation (anti-phased).")
print("Adding φ/2 to the longitude should flip the sign.")
print()

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def longitude_to_value(phi, C, R):
    return 10**(R * np.sin(phi / R) + C)

# Test with φ/2 correction and multiple advance rates
print(f"{'Period':>8s}  {'No corr':>8s}  {'φ/2 corr':>9s}  {'φ/2 dir%':>9s}  {'beats%':>7s}")
print("-" * 50)

best_corr = 0
best_period = 0
best_beats = 0

for T_cycle in [5, 7, 9, 10, 11, 13, 22, PHI*7, PHI**4]:
    dphi = 2 * np.pi / T_cycle
    
    preds_raw = []
    preds_corrected = []
    actuals = []
    naives = []
    
    for i in range(N - 1):
        ssn = ssn_arr[i]
        if ssn <= 0: continue
        
        phi_now = value_to_longitude(ssn_log[i], C_sun, R_SUN)
        
        # Raw (no correction)
        phi_next_raw = phi_now + dphi
        pred_raw = longitude_to_value(phi_next_raw, C_sun, R_SUN)
        
        # With φ/2 phase correction
        phi_next_corr = phi_now + dphi + HALF_PHI
        pred_corr = longitude_to_value(phi_next_corr, C_sun, R_SUN)
        
        preds_raw.append(pred_raw)
        preds_corrected.append(pred_corr)
        actuals.append(ssn_arr[i + 1])
        naives.append(ssn)
    
    preds_raw = np.array(preds_raw)
    preds_corr = np.array(preds_corrected)
    actuals = np.array(actuals)
    naives = np.array(naives)
    
    if np.std(preds_raw) < 1e-10 or np.std(preds_corr) < 1e-10:
        continue
    
    corr_raw = np.corrcoef(preds_raw, actuals)[0, 1]
    corr_corr = np.corrcoef(preds_corr, actuals)[0, 1]
    
    dir_match = np.sum(np.sign(np.diff(preds_corr[:50])) == np.sign(np.diff(actuals[:50]))) / 49 * 100
    beats = np.sum(np.abs(preds_corr - actuals) < np.abs(naives - actuals)) / len(actuals) * 100
    
    label = f"{T_cycle:.1f}" if T_cycle != int(T_cycle) else f"{int(T_cycle)}"
    print(f"{label:>8s}  {corr_raw:+8.4f}  {corr_corr:+9.4f}  {dir_match:8.1f}%  {beats:6.1f}%")
    
    if abs(corr_corr) > abs(best_corr):
        best_corr = corr_corr
        best_period = T_cycle
        best_beats = beats

print(f"\nBest: period={best_period:.1f}, corr={best_corr:+.4f}, beats naive={best_beats:.1f}%")

# ── Now scan phase corrections beyond just φ/2 ────────────────────
print(f"\n{'='*60}")
print("TEST 2: SCAN PHASE CORRECTIONS")
print(f"{'='*60}")
print()
print("Scanning phase offset from 0 to 2π to find optimal correction")
print("(expecting φ/2 or something ARA-related to win)")
print()

# Use the best period from above
T_best = best_period
dphi_best = 2 * np.pi / T_best

phase_offsets = np.arange(0, 2*np.pi, 0.02)
offset_results = []

for offset in phase_offsets:
    preds = []
    actuals = []
    naives = []
    
    for i in range(N - 1):
        ssn = ssn_arr[i]
        if ssn <= 0: continue
        
        phi_now = value_to_longitude(ssn_log[i], C_sun, R_SUN)
        phi_next = phi_now + dphi_best + offset
        pred = longitude_to_value(phi_next, C_sun, R_SUN)
        
        preds.append(pred)
        actuals.append(ssn_arr[i + 1])
        naives.append(ssn)
    
    preds = np.array(preds)
    actuals = np.array(actuals)
    naives = np.array(naives)
    
    if np.std(preds) < 1e-10: continue
    
    corr = np.corrcoef(preds, actuals)[0, 1]
    beats = np.sum(np.abs(preds - actuals) < np.abs(naives - actuals)) / len(actuals) * 100
    offset_results.append((offset, corr, beats))

offset_results = np.array(offset_results)

# Find optimal offset
best_idx = np.argmax(offset_results[:, 1])  # best positive correlation
optimal_offset = offset_results[best_idx, 0]
optimal_corr = offset_results[best_idx, 1]
optimal_beats = offset_results[best_idx, 2]

print(f"Optimal phase offset: {optimal_offset:.4f} rad = {np.degrees(optimal_offset):.2f}°")
print(f"Optimal correlation: {optimal_corr:+.4f}")
print(f"Optimal beats naive: {optimal_beats:.1f}%")
print()

# Check what the optimal offset is close to
special_offsets = {
    'φ/2': PHI/2,
    'φ': PHI,
    '1/φ': 1/PHI,
    'π/2': np.pi/2,
    'π': np.pi,
    'π/φ': np.pi/PHI,
    'φ/π': PHI/np.pi,
    '1': 1.0,
    '2': 2.0,
    'e/2': np.e/2,
    '√φ': np.sqrt(PHI),
    'ln(φ)': np.log(PHI),
    'π-φ': np.pi - PHI,
    '2π/φ': 2*np.pi/PHI,
    'π/3': np.pi/3,
    '2π/3': 2*np.pi/3,
    'arctan(φ)': np.arctan(PHI),
    'π·(φ-1)': np.pi*(PHI-1),
    'φ²/2': PHI**2/2,
    '3φ/π': 3*PHI/np.pi,
}

print(f"─── Proximity to special values ───")
for name, val in sorted(special_offsets.items(), key=lambda x: abs(x[1] - optimal_offset)):
    delta = abs(val - optimal_offset)
    if delta < 0.15:
        marker = " ◄──" if delta < 0.03 else ""
        print(f"  {name:>12s} = {val:.4f} (Δ = {delta:.4f}){marker}")

# ── TEST 3: Apply to earthquake with same correction ──────────────
print(f"\n{'='*60}")
print("TEST 3: SAME φ/2 CORRECTION ON EARTHQUAKES")
print(f"{'='*60}")
print()

# Use optimal offset from SSN scan
for offset_val, offset_name in [(HALF_PHI, "φ/2"), (optimal_offset, "optimal")]:
    eq_preds = []
    eq_acts = []
    eq_naives = []
    
    for i in range(N - 1):
        eq = eq_arr[i]
        if eq <= 0: continue
        
        phi_now = value_to_longitude(eq_log[i], C_eq, R_EQ)
        phi_next = phi_now + dphi_best + offset_val
        pred = longitude_to_value(phi_next, C_eq, R_EQ)
        
        eq_preds.append(pred)
        eq_acts.append(eq_arr[i + 1])
        eq_naives.append(eq)
    
    eq_preds = np.array(eq_preds)
    eq_acts = np.array(eq_acts)
    eq_naives = np.array(eq_naives)
    
    corr_eq = np.corrcoef(eq_preds, eq_acts)[0, 1]
    beats_eq = np.sum(np.abs(eq_preds - eq_acts) < np.abs(eq_naives - eq_acts)) / len(eq_acts) * 100
    dir_eq = np.sum(np.sign(eq_preds[1:] - eq_preds[:-1]) == np.sign(eq_acts[1:] - eq_acts[:-1])) / (len(eq_acts)-1) * 100
    
    print(f"  {offset_name:>10s} offset ({offset_val:.4f}): corr={corr_eq:+.4f}, beats={beats_eq:.1f}%, dir={dir_eq:.1f}%")

# ── TEST 4: CROSS-SCALE with midpoint geometry ────────────────────
print(f"\n{'='*60}")
print("TEST 4: CROSS-SCALE VIA MIDPOINT GEOMETRY")
print(f"{'='*60}")
print()
print(f"Matter midpoint = {ARA_MIDPOINT:.4f}")
print(f"Coupler-midpoint distance = {DISTANCE_TO_COUPLER:.4f}")
print()

# The midpoint is where the two matter systems "meet" on the ARA scale.
# The distance from midpoint to coupler (0.06) is the coupling offset.
# This should modulate the cross-scale prediction.

# Method: predict SSN change from sphere, then translate to EQ change
# using the midpoint-coupler geometry as a scaling factor.

# The scaling factor = ratio of (ARA distances from midpoint)
# Sun is (1.73 - 0.94) = 0.79 from midpoint
# EQ is (0.94 - 0.15) = 0.79 from midpoint  ← they're EQUAL!
# Because midpoint is the arithmetic mean, both are equidistant!

d_sun_mid = abs(ARA_SUN - ARA_MIDPOINT)
d_eq_mid = abs(ARA_EQ - ARA_MIDPOINT)

print(f"Distance Sun → midpoint:  {d_sun_mid:.4f}")
print(f"Distance EQ → midpoint:   {d_eq_mid:.4f}")
print(f"These are EQUAL (midpoint = arithmetic mean).")
print()

# More useful: ratio of distances to coupler
d_sun_coupler = abs(ARA_SUN - ARA_COUPLER)
d_eq_coupler = abs(ARA_EQ - ARA_COUPLER)
print(f"Distance Sun → coupler:   {d_sun_coupler:.4f}")
print(f"Distance EQ → coupler:    {d_eq_coupler:.4f}")
print(f"Ratio (EQ/Sun):           {d_eq_coupler/d_sun_coupler:.4f}")
print(f"  (Earthquake is {d_eq_coupler/d_sun_coupler:.2f}× as far from the coupler as sunspots)")
print()

# Use this ratio to translate SSN predictions to EQ predictions
# A system closer to the coupler should be MORE coupled (smaller correction)
# A system farther should be LESS coupled (larger correction)
coupling_ratio = d_sun_coupler / d_eq_coupler  # Sun/EQ distance ratio

# SSN predicted Δlog → EQ predicted Δlog via coupling ratio
ssn_preds_dlog = []
for i in range(N - 1):
    ssn = ssn_arr[i]
    if ssn <= 0: continue
    phi_now = value_to_longitude(ssn_log[i], C_sun, R_SUN)
    phi_next = phi_now + dphi_best + optimal_offset
    val_now = R_SUN * np.sin(phi_now / R_SUN)
    val_next = R_SUN * np.sin(phi_next / R_SUN)
    ssn_preds_dlog.append(val_next - val_now)

ssn_preds_dlog = np.array(ssn_preds_dlog)

# Translate to EQ scale using:
# 1. Simple coupling ratio
eq_pred_simple = ssn_preds_dlog * coupling_ratio
# 2. R-ratio scaling  
eq_pred_R = ssn_preds_dlog * (R_EQ / R_SUN)
# 3. Combined: coupling ratio × R ratio
eq_pred_combined = ssn_preds_dlog * coupling_ratio * (R_EQ / R_SUN)
# 4. Midpoint offset correction
eq_pred_midpoint = ssn_preds_dlog * coupling_ratio * np.exp(-DISTANCE_TO_COUPLER)

n_compare = min(len(ssn_preds_dlog), len(dlog_eq))

print(f"Cross-scale translation (SSN Δlog → EQ Δlog):")
for name, pred in [("Coupling ratio", eq_pred_simple),
                     ("R-ratio", eq_pred_R),
                     ("Combined", eq_pred_combined),
                     ("Midpoint-corrected", eq_pred_midpoint)]:
    if np.std(pred[:n_compare]) > 1e-10:
        corr = np.corrcoef(pred[:n_compare], dlog_eq[:n_compare])[0, 1]
        dir_match = np.sum(np.sign(pred[:n_compare]) == np.sign(dlog_eq[:n_compare])) / n_compare * 100
        print(f"  {name:>20s}: corr = {corr:+.4f}, direction = {dir_match:.1f}%")

# ── TEST 5: THE FULL ISOSCELES CONSTRUCTION ────���──────────────────
print(f"\n{'='*60}")
print("TEST 5: FULL ISOSCELES — TWO COUPLERS, MATTER AT VERTEX")
print(f"{'='*60}")
print()

# Two couplers at ARA = 1.0, separated by φ/2 in longitude
# Matter (sunspot) at ARA = 1.73
# The AVERAGE of the two coupler signals, weighted by the triangle geometry,
# gives the prediction

def sphere_xyz(theta, phi):
    return np.array([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)])

theta_coupler = np.pi * (ARA_COUPLER / 2)  # equator = π/2
theta_sun = np.pi * (ARA_SUN / 2)
theta_eq = np.pi * (ARA_EQ / 2)

# Compute the isosceles triangle for sunspots
# Coupler 1 at (θ_c, 0), Coupler 2 at (θ_c, φ/2)
C1 = sphere_xyz(theta_coupler, 0)
C2 = sphere_xyz(theta_coupler, HALF_PHI)
M_sun = sphere_xyz(theta_sun, 0)  # at φ=0 initially

# Great circle distances
from numpy.linalg import norm
def gc(a, b):
    return np.arccos(np.clip(np.dot(a, b), -1, 1))

d_C1_C2 = gc(C1, C2)
d_C1_M = gc(C1, M_sun)
d_C2_M = gc(C2, M_sun)

print(f"Isosceles triangle sides:")
print(f"  Base (C1-C2):  {np.degrees(d_C1_C2):.2f}° ({d_C1_C2:.4f} rad)")
print(f"  Side C1-M:     {np.degrees(d_C1_M):.2f}° ({d_C1_M:.4f} rad)")
print(f"  Side C2-M:     {np.degrees(d_C2_M):.2f}° ({d_C2_M:.4f} rad)")
print(f"  Isosceles? |C1M - C2M| = {abs(d_C1_M - d_C2_M):.4f}")

# Vertex angle at Matter
v1 = C1 - np.dot(C1, M_sun) * M_sun
v2 = C2 - np.dot(C2, M_sun) * M_sun
n1 = norm(v1)
n2 = norm(v2)
if n1 > 1e-10 and n2 > 1e-10:
    vertex_angle = np.arccos(np.clip(np.dot(v1, v2) / (n1 * n2), -1, 1))
    print(f"  Vertex angle at Matter: {np.degrees(vertex_angle):.2f}°")
    
    # Compare to water
    print(f"  Water molecule angle:   104.50°")
    print(f"  Difference:             {abs(np.degrees(vertex_angle) - 104.5):.2f}°")
else:
    vertex_angle = 0
    print(f"  Vertex angle: degenerate")

# ── Prediction using isosceles average ─────────────────────────────
print(f"\n─── Isosceles prediction ───")
print(f"Two coupler readings averaged, weighted by triangle geometry")
print()

isosceles_preds_ssn = []
isosceles_preds_eq = []
ssn_acts = []
eq_acts = []
ssn_naives = []
eq_naives = []

for i in range(N - 1):
    ssn = ssn_arr[i]
    eq = eq_arr[i]
    if ssn <= 0 or eq <= 0: continue
    
    # Map SSN to longitude
    phi_matter = value_to_longitude(ssn_log[i], C_sun, R_SUN)
    
    # Two coupler readings: one at φ_matter, one at φ_matter + φ/2
    # Coupler 1 sees the system at current phase
    # Coupler 2 sees the system shifted by φ/2
    val_C1 = R_COUPLER * np.sin(phi_matter / R_COUPLER)
    val_C2 = R_COUPLER * np.sin((phi_matter + HALF_PHI) / R_COUPLER)
    
    # Average of two coupler readings = the isosceles prediction
    # Weighted by proximity to matter on the ARA scale
    # (closer coupler has more weight)
    avg_coupler = (val_C1 + val_C2) / 2
    
    # Advance time by best period
    phi_next = phi_matter + dphi_best
    val_C1_next = R_COUPLER * np.sin(phi_next / R_COUPLER)
    val_C2_next = R_COUPLER * np.sin((phi_next + HALF_PHI) / R_COUPLER)
    avg_next = (val_C1_next + val_C2_next) / 2
    
    # The predicted Δlog = change in averaged coupler signal
    dlog_pred = avg_next - avg_coupler
    
    # Apply to matter system
    ssn_pred = ssn * 10**(dlog_pred)
    
    # For earthquake: same temporal advance, different R
    phi_eq_now = value_to_longitude(eq_log[i], C_eq, R_EQ)
    val_C1_eq = R_COUPLER * np.sin(phi_eq_now / R_COUPLER)
    val_C2_eq = R_COUPLER * np.sin((phi_eq_now + HALF_PHI) / R_COUPLER)
    avg_eq = (val_C1_eq + val_C2_eq) / 2
    
    phi_eq_next = phi_eq_now + dphi_best
    val_C1_eq_next = R_COUPLER * np.sin(phi_eq_next / R_COUPLER)
    val_C2_eq_next = R_COUPLER * np.sin((phi_eq_next + HALF_PHI) / R_COUPLER)
    avg_eq_next = (val_C1_eq_next + val_C2_eq_next) / 2
    
    dlog_eq_pred = avg_eq_next - avg_eq
    eq_pred = eq * 10**(dlog_eq_pred)
    
    isosceles_preds_ssn.append(ssn_pred)
    isosceles_preds_eq.append(eq_pred)
    ssn_acts.append(ssn_arr[i + 1])
    eq_acts.append(eq_arr[i + 1])
    ssn_naives.append(ssn)
    eq_naives.append(eq)

iso_ssn = np.array(isosceles_preds_ssn)
iso_eq = np.array(isosceles_preds_eq)
act_ssn = np.array(ssn_acts)
act_eq = np.array(eq_acts)
naiv_ssn = np.array(ssn_naives)
naiv_eq = np.array(eq_naives)

corr_iso_ssn = np.corrcoef(iso_ssn, act_ssn)[0, 1]
corr_iso_eq = np.corrcoef(iso_eq, act_eq)[0, 1]
beats_iso_ssn = np.sum(np.abs(iso_ssn - act_ssn) < np.abs(naiv_ssn - act_ssn)) / len(act_ssn) * 100
beats_iso_eq = np.sum(np.abs(iso_eq - act_eq) < np.abs(naiv_eq - act_eq)) / len(act_eq) * 100

# Cross-scale: does the isosceles SSN signal predict EQ?
cross_iso = np.corrcoef(iso_ssn / iso_ssn.mean(), act_eq / act_eq.mean())[0, 1]
dlog_iso_ssn = np.log10(np.maximum(iso_ssn, 0.1)) - ssn_log[:-1][:len(iso_ssn)]
dlog_act_eq = dlog_eq[:len(dlog_iso_ssn)]
cross_dlog = np.corrcoef(dlog_iso_ssn, dlog_act_eq)[0, 1]

print(f"Isosceles SSN: corr = {corr_iso_ssn:+.4f}, beats naive = {beats_iso_ssn:.1f}%")
print(f"Isosceles EQ:  corr = {corr_iso_eq:+.4f}, beats naive = {beats_iso_eq:.1f}%")
print(f"Cross-scale (normalized): {cross_iso:+.4f}")
print(f"Cross-scale (Δlog):       {cross_dlog:+.4f}")

# ── VERDICT ────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print("SCRIPT 166 VERDICT")
print(f"{'='*60}")

score = 0
total = 6

# 1. φ/2 correction flips the anti-correlation?
if best_corr > 0:
    score += 1
    print(f"  [PASS] φ/2 correction gives positive corr: {best_corr:+.4f}")
else:
    print(f"  [FAIL] φ/2 correction still negative: {best_corr:+.4f}")

# 2. Optimal phase offset near a special ARA value?
nearest = min(special_offsets.items(), key=lambda x: abs(x[1] - optimal_offset))
if abs(nearest[1] - optimal_offset) < 0.05:
    score += 1
    print(f"  [PASS] Optimal offset ≈ {nearest[0]} ({optimal_offset:.4f} vs {nearest[1]:.4f})")
else:
    print(f"  [FAIL] Optimal offset {optimal_offset:.4f} not near special value (nearest: {nearest[0]})")

# 3. Beats naive > 35%?
if best_beats > 35:
    score += 1
    print(f"  [PASS] Beats naive {best_beats:.1f}%")
else:
    print(f"  [FAIL] Beats naive only {best_beats:.1f}%")

# 4. Isosceles improves over single-coupler?
if corr_iso_ssn > best_corr * 0.5:  # at least half as good
    score += 1
    print(f"  [PASS] Isosceles SSN corr: {corr_iso_ssn:+.4f}")
else:
    print(f"  [FAIL] Isosceles SSN corr: {corr_iso_ssn:+.4f} (much worse)")

# 5. Cross-scale signal > 0.05?
if abs(cross_dlog) > 0.05 or abs(cross_iso) > 0.05:
    score += 1
    best_cross = max(abs(cross_dlog), abs(cross_iso))
    print(f"  [PASS] Cross-scale signal: {best_cross:.4f}")
else:
    print(f"  [FAIL] Cross-scale signal too weak: {max(abs(cross_dlog), abs(cross_iso)):.4f}")

# 6. Vertex angle near meaningful value?
if vertex_angle > 0:
    all_geom = [(abs(np.degrees(vertex_angle) - v), n) for n, v in 
                {104.5: 'water', 109.47: 'tetrahedral', 90: 'right', 120: 'hexagonal',
                 60: 'equilateral', 108: 'pentagon'}.items()]
    best_match = min(all_geom, key=lambda x: x[0])
    if best_match[0] < 10:
        score += 1
        print(f"  [PASS] Vertex angle {np.degrees(vertex_angle):.1f}° ≈ {best_match[1]} ({best_match[0]:.1f}° off)")
    else:
        print(f"  [FAIL] Vertex angle {np.degrees(vertex_angle):.1f}° not near geometric value")

print(f"\n  SCORE: {score}/{total}")
print(f"\nScript 166 complete.")
