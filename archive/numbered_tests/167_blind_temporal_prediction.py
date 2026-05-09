#!/usr/bin/env python3
"""
Script 167: Blind Temporal Prediction — Train on Past, Predict Known "Future"
===============================================================================

The test Dylan asked for: predict the future from the present,
but do it with past data we already have. Proper out-of-sample validation.

Method:
  1. Pick a cutoff year (the "present")
  2. Calibrate using ONLY data before the cutoff:
     - Mean log₁₀ (the centre C)
     - Temporal advance rate (from Hale cycle = 22yr)
     - Phase correction (φ/2)
  3. Predict forward year by year from the cutoff
  4. Compare against actual data (which we have but didn't use)
  5. Repeat with multiple cutoffs for robustness

Geometry: Isosceles two-coupler construction from Script 166
  - Two couplers at ARA = 1.0, phase-separated by φ/2
  - Matter system at its ARA latitude
  - 22-year Hale cycle advance rate
  - 0.06 midpoint-coupler correction

Also test: cross-scale (predict EQ from SSN model and vice versa)
"""

import numpy as np

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2

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

all_years = sorted(set(sun_annual_mean.keys()) & set(eq_annual_m7.keys()))

# ── ARA geometry constants ─────────────────────────────────────────
ARA_SUN = 1.73
ARA_EQ = 0.15
ARA_COUPLER = 1.0
MIDPOINT_OFFSET = 0.06  # |coupler - midpoint(sun, eq)|
R_SUN = PHI
R_EQ = 1.914
R_COUPLER = 1.354
HALE_PERIOD = 22.0
DPHI = 2 * np.pi / HALE_PERIOD

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def longitude_to_value(phi, C, R):
    return 10**(R * np.sin(phi / R) + C)

def isosceles_predict_next(current_log, C, R_matter, step_years=1):
    """
    Predict next value using isosceles two-coupler geometry.
    
    Two couplers at ARA=1.0, separated by φ/2.
    Average their readings. Advance by Hale cycle step.
    Apply midpoint correction.
    """
    phi = value_to_longitude(current_log, C, R_matter)
    
    # Two coupler readings at current position
    val_C1 = R_COUPLER * np.sin(phi / R_COUPLER)
    val_C2 = R_COUPLER * np.sin((phi + HALF_PHI) / R_COUPLER)
    avg_now = (val_C1 + val_C2) / 2
    
    # Advance by step_years worth of Hale cycle
    phi_next = phi + DPHI * step_years
    
    val_C1_next = R_COUPLER * np.sin(phi_next / R_COUPLER)
    val_C2_next = R_COUPLER * np.sin((phi_next + HALF_PHI) / R_COUPLER)
    avg_next = (val_C1_next + val_C2_next) / 2
    
    # Predicted Δlog = change in averaged coupler signal
    # Apply midpoint correction as damping factor
    dlog = (avg_next - avg_now) * np.exp(-MIDPOINT_OFFSET)
    
    return current_log + dlog

# ── BLIND PREDICTION FUNCTION ─────────────────────────────────────
def run_blind_prediction(cutoff_year, system_data, system_name, R_matter):
    """
    Train on data before cutoff, predict forward, compare to actual.
    """
    # Split data
    train_years = [y for y in all_years if y < cutoff_year]
    test_years = [y for y in all_years if y >= cutoff_year]
    
    if len(train_years) < 20 or len(test_years) < 5:
        return None
    
    # Calibrate: compute C (mean log) from training data only
    train_vals = np.array([system_data[y] for y in train_years])
    train_log = np.log10(np.maximum(train_vals, 0.1))
    C_train = np.mean(train_log)
    
    # Starting point: last year of training
    start_year = train_years[-1]
    start_val = system_data[start_year]
    start_log = np.log10(max(start_val, 0.1))
    
    # Predict forward, year by year
    # Two modes: 
    #   A) Sequential: each prediction uses the PREVIOUS prediction as input
    #   B) Anchored: each prediction starts from the last known value
    
    preds_sequential = []
    preds_anchored = []
    actuals = []
    naive_preds = []  # "same as cutoff year"
    
    current_log = start_log
    
    for i, year in enumerate(test_years):
        actual = system_data[year]
        actuals.append(actual)
        naive_preds.append(start_val)  # always predict the starting value
        
        # Sequential: chain predictions
        pred_log = isosceles_predict_next(current_log, C_train, R_matter, step_years=1)
        pred_val = 10**pred_log
        preds_sequential.append(pred_val)
        current_log = pred_log  # use prediction as next input
        
        # Anchored: always start from the known value
        pred_log_a = isosceles_predict_next(start_log, C_train, R_matter, step_years=i+1)
        preds_anchored.append(10**pred_log_a)
    
    actuals = np.array(actuals)
    preds_seq = np.array(preds_sequential)
    preds_anc = np.array(preds_anchored)
    naive = np.array(naive_preds)
    
    # Metrics
    corr_seq = np.corrcoef(preds_seq, actuals)[0, 1] if np.std(preds_seq) > 1e-10 else 0
    corr_anc = np.corrcoef(preds_anc, actuals)[0, 1] if np.std(preds_anc) > 1e-10 else 0
    
    mae_seq = np.mean(np.abs(preds_seq - actuals))
    mae_anc = np.mean(np.abs(preds_anc - actuals))
    mae_naive = np.mean(np.abs(naive - actuals))
    
    beats_seq = np.sum(np.abs(preds_seq - actuals) < np.abs(naive - actuals)) / len(actuals) * 100
    beats_anc = np.sum(np.abs(preds_anc - actuals) < np.abs(naive - actuals)) / len(actuals) * 100
    
    # Direction of change (up/down from start)
    dir_seq = np.sum(np.sign(preds_seq - start_val) == np.sign(actuals - start_val)) / len(actuals) * 100
    dir_anc = np.sum(np.sign(preds_anc - start_val) == np.sign(actuals - start_val)) / len(actuals) * 100
    
    # Within factor of 2?
    within_2x_seq = np.sum(np.abs(np.log10(np.maximum(preds_seq, 0.1) / np.maximum(actuals, 0.1))) < np.log10(2)) / len(actuals) * 100
    within_2x_anc = np.sum(np.abs(np.log10(np.maximum(preds_anc, 0.1) / np.maximum(actuals, 0.1))) < np.log10(2)) / len(actuals) * 100
    
    return {
        'cutoff': cutoff_year,
        'n_test': len(test_years),
        'corr_seq': corr_seq, 'corr_anc': corr_anc,
        'mae_seq': mae_seq, 'mae_anc': mae_anc, 'mae_naive': mae_naive,
        'beats_seq': beats_seq, 'beats_anc': beats_anc,
        'dir_seq': dir_seq, 'dir_anc': dir_anc,
        'within_2x_seq': within_2x_seq, 'within_2x_anc': within_2x_anc,
        'test_years': test_years,
        'actuals': actuals,
        'preds_seq': preds_seq,
        'preds_anc': preds_anc,
        'naive': naive,
        'start_val': start_val,
    }

# ── RUN BLIND PREDICTIONS ─────────────────────────────────────────
cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

print(f"\n{'='*70}")
print("SUNSPOT BLIND PREDICTIONS")
print(f"{'='*70}")
print()

ssn_results = []
for cutoff in cutoffs:
    result = run_blind_prediction(cutoff, sun_annual_mean, "Sunspot", R_SUN)
    if result:
        ssn_results.append(result)
        r = result
        print(f"Cutoff {cutoff} → predict {r['n_test']} years ({cutoff}-{cutoff + r['n_test'] - 1})")
        print(f"  Start value: {r['start_val']:.1f}")
        print(f"  Sequential: corr={r['corr_seq']:+.3f}, MAE={r['mae_seq']:.1f}, beats={r['beats_seq']:.0f}%, dir={r['dir_seq']:.0f}%, ×2={r['within_2x_seq']:.0f}%")
        print(f"  Anchored:   corr={r['corr_anc']:+.3f}, MAE={r['mae_anc']:.1f}, beats={r['beats_anc']:.0f}%, dir={r['dir_anc']:.0f}%, ×2={r['within_2x_anc']:.0f}%")
        print(f"  Naive:       MAE={r['mae_naive']:.1f}")
        
        # Show first 5 predictions
        print(f"  Year   Actual   Seq_Pred   Anc_Pred   Naive")
        for j in range(min(8, r['n_test'])):
            print(f"  {r['test_years'][j]}   {r['actuals'][j]:6.1f}   {r['preds_seq'][j]:8.1f}   {r['preds_anc'][j]:8.1f}   {r['naive'][j]:6.1f}")
        print()

print(f"\n{'='*70}")
print("EARTHQUAKE BLIND PREDICTIONS")
print(f"{'='*70}")
print()

eq_results = []
for cutoff in cutoffs:
    result = run_blind_prediction(cutoff, eq_annual_m7, "Earthquake", R_EQ)
    if result:
        eq_results.append(result)
        r = result
        print(f"Cutoff {cutoff} → predict {r['n_test']} years ({cutoff}-{cutoff + r['n_test'] - 1})")
        print(f"  Start value: {r['start_val']}")
        print(f"  Sequential: corr={r['corr_seq']:+.3f}, MAE={r['mae_seq']:.1f}, beats={r['beats_seq']:.0f}%, dir={r['dir_seq']:.0f}%, ×2={r['within_2x_seq']:.0f}%")
        print(f"  Anchored:   corr={r['corr_anc']:+.3f}, MAE={r['mae_anc']:.1f}, beats={r['beats_anc']:.0f}%, dir={r['dir_anc']:.0f}%, ×2={r['within_2x_anc']:.0f}%")
        print(f"  Naive:       MAE={r['mae_naive']:.1f}")
        
        print(f"  Year   Actual   Seq_Pred   Anc_Pred   Naive")
        for j in range(min(8, r['n_test'])):
            print(f"  {r['test_years'][j]}   {r['actuals'][j]:6.0f}   {r['preds_seq'][j]:8.1f}   {r['preds_anc'][j]:8.1f}   {r['naive'][j]:6.0f}")
        print()

# ── CROSS-SCALE BLIND TEST ────────────────────────────────────────
print(f"\n{'='*70}")
print("CROSS-SCALE BLIND TEST")
print(f"{'='*70}")
print()
print("Use SSN model's temporal change to predict EQ direction")
print()

for cutoff in [2000, 2005, 2010]:
    test_years = [y for y in all_years if y >= cutoff]
    train_years = [y for y in all_years if y < cutoff]
    
    if len(test_years) < 5: continue
    
    C_ssn_train = np.mean([np.log10(max(sun_annual_mean[y], 0.1)) for y in train_years])
    
    # For each test year: predict SSN direction, check if EQ goes same way
    ssn_dirs = []
    eq_dirs = []
    
    for i in range(len(test_years) - 1):
        y = test_years[i]
        y_next = test_years[i + 1]
        
        ssn_now = sun_annual_mean[y]
        ssn_log_now = np.log10(max(ssn_now, 0.1))
        
        # Predict SSN direction from sphere
        pred_log = isosceles_predict_next(ssn_log_now, C_ssn_train, R_SUN)
        ssn_direction = np.sign(pred_log - ssn_log_now)
        ssn_dirs.append(ssn_direction)
        
        # Actual EQ direction
        eq_now = eq_annual_m7[y]
        eq_next = eq_annual_m7[y_next]
        eq_direction = np.sign(eq_next - eq_now)
        eq_dirs.append(eq_direction)
    
    ssn_dirs = np.array(ssn_dirs)
    eq_dirs = np.array(eq_dirs)
    
    # How often does SSN predicted direction match EQ actual direction?
    match = np.sum(ssn_dirs == eq_dirs) / len(eq_dirs) * 100
    anti_match = np.sum(ssn_dirs == -eq_dirs) / len(eq_dirs) * 100
    
    print(f"  Cutoff {cutoff}: SSN→EQ direction match = {match:.1f}% (anti: {anti_match:.1f}%, N={len(eq_dirs)})")

# ── AGGREGATE SCORING ──────────────────────────────────────────────
print(f"\n{'='*70}")
print("SCRIPT 167 AGGREGATE VERDICT")
print(f"{'='*70}")
print()

score = 0
total = 8

# 1. Average SSN sequential correlation > 0.3?
avg_ssn_corr = np.mean([r['corr_seq'] for r in ssn_results])
if avg_ssn_corr > 0.3:
    score += 1
    print(f"  [PASS] Avg SSN seq corr: {avg_ssn_corr:+.3f}")
else:
    print(f"  [FAIL] Avg SSN seq corr: {avg_ssn_corr:+.3f} (< 0.3)")

# 2. Average SSN anchored correlation > 0.3?
avg_ssn_anc = np.mean([r['corr_anc'] for r in ssn_results])
if avg_ssn_anc > 0.3:
    score += 1
    print(f"  [PASS] Avg SSN anch corr: {avg_ssn_anc:+.3f}")
else:
    print(f"  [FAIL] Avg SSN anch corr: {avg_ssn_anc:+.3f} (< 0.3)")

# 3. SSN beats naive in at least 2 cutoffs?
beats_count_ssn = sum(1 for r in ssn_results if r['beats_seq'] > 50)
if beats_count_ssn >= 2:
    score += 1
    print(f"  [PASS] SSN beats naive in {beats_count_ssn}/{len(ssn_results)} cutoffs")
else:
    print(f"  [FAIL] SSN beats naive in only {beats_count_ssn}/{len(ssn_results)} cutoffs")

# 4. SSN within 2× for >60% on average?
avg_within_2x = np.mean([r['within_2x_seq'] for r in ssn_results])
if avg_within_2x > 60:
    score += 1
    print(f"  [PASS] Avg SSN within 2×: {avg_within_2x:.0f}%")
else:
    print(f"  [FAIL] Avg SSN within 2×: {avg_within_2x:.0f}%")

# 5. EQ prediction positive correlation on average?
avg_eq_corr = np.mean([r['corr_seq'] for r in eq_results])
if avg_eq_corr > 0:
    score += 1
    print(f"  [PASS] Avg EQ seq corr: {avg_eq_corr:+.3f}")
else:
    print(f"  [FAIL] Avg EQ seq corr: {avg_eq_corr:+.3f}")

# 6. EQ within 2× for >50% on average?
avg_eq_2x = np.mean([r['within_2x_seq'] for r in eq_results])
if avg_eq_2x > 50:
    score += 1
    print(f"  [PASS] Avg EQ within 2×: {avg_eq_2x:.0f}%")
else:
    print(f"  [FAIL] Avg EQ within 2×: {avg_eq_2x:.0f}%")

# 7. Direction correct >55% for SSN?
avg_dir_ssn = np.mean([r['dir_seq'] for r in ssn_results])
if avg_dir_ssn > 55:
    score += 1
    print(f"  [PASS] Avg SSN direction: {avg_dir_ssn:.0f}%")
else:
    print(f"  [FAIL] Avg SSN direction: {avg_dir_ssn:.0f}%")

# 8. Any cutoff where both SSN and EQ beat naive?
both_beat = sum(1 for i in range(len(ssn_results)) 
                if ssn_results[i]['beats_seq'] > 50 and eq_results[i]['beats_seq'] > 50)
if both_beat > 0:
    score += 1
    print(f"  [PASS] Both systems beat naive in {both_beat} cutoff(s)")
else:
    print(f"  [FAIL] No cutoff where both systems beat naive")

print(f"\n  SCORE: {score}/{total}")

# ── Honest summary ─────────────────────────────────────────────────
print(f"\n{'='*70}")
print("HONEST SUMMARY")
print(f"{'='*70}")
print()
if score >= 5:
    print("The sphere geometry predicts temporal behaviour out-of-sample.")
    print("The isosceles two-coupler construction with φ/2 correction works.")
elif score >= 3:
    print("Partial signal. The geometry captures some structure but doesn't")
    print("consistently beat the naive baseline. More work needed on the")
    print("phase calibration or the choice of test systems.")
else:
    print("The current construction doesn't reliably predict out-of-sample.")
    print("The high in-sample correlations from Script 166 were driven by")
    print("autocorrelation preservation, not genuine predictive power.")
    print("The GEOMETRY may still be correct — but the CALIBRATION needs work.")

print(f"\nScript 167 complete.")
