#!/usr/bin/env python3
"""
Script 161: Sunspot Temporal Prediction — Forward and Reverse
=============================================================

Test: Can the unified ARA formula predict sunspot numbers through time?

Method:
  1. Pick random past date → get sunspot number S₁
  2. Skip 1 year (12 months) → get actual sunspot number S₂
  3. Use formula to predict S₂ from S₁ + time distance
  4. REVERSE: predict S₁ from S₂ using formula in reverse
  5. Compare against baselines

Formula: Δlog = G + R·sin(G_phase / R)
  - For temporal prediction within one system: G = 0 (same scale, intensive quantity)
  - So: Δlog = R·sin(time_phase / R)
  - R_solar = 1.73 (exothermic source ARA position)
  - time_phase encodes the temporal distance on the circle

Cross-scale transposition (Layer 3) handled in Script 162.
"""

import numpy as np
import random
import os

# ── Load sunspot data ──────────────────────────────────────────────
data_path = os.path.join(os.path.dirname(__file__), '..', 'solar_test', 'sunspots.txt')
if not os.path.exists(data_path):
    data_path = '/sessions/focused-tender-thompson/mnt/SystemFormulaFolder/solar_test/sunspots.txt'

months = []
values = []
with open(data_path, 'r') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 4:
            year = int(parts[0])
            month = int(parts[1])
            frac_year = float(parts[2])
            ssn = float(parts[3])
            if ssn >= 0:  # valid data
                months.append((year, month, frac_year))
                values.append(ssn)

values = np.array(values)
frac_years = np.array([m[2] for m in months])
N = len(values)
print(f"Loaded {N} months of sunspot data")
print(f"Range: {months[0][0]}-{months[0][1]:02d} to {months[-1][0]}-{months[-1][1]:02d}")
print(f"SSN range: {values.min():.1f} to {values.max():.1f}, mean: {values.mean():.1f}")
print()

# ── ARA parameters ─────────────────────────────────────────────────
PHI = (1 + np.sqrt(5)) / 2  # 1.618...
R_solar = 1.73  # exothermic source ARA position

# Solar cycle period ~ 11 years = 132 months
# One full revolution on the ARA circle = one solar cycle
SOLAR_CYCLE_MONTHS = 132  # ~11 years

# ── Formula functions ──────────────────────────────────────────────
def time_to_phase(dt_months):
    """Convert temporal distance to phase angle on the ARA circle.
    One full solar cycle (132 months) = 2π radians."""
    return 2 * np.pi * dt_months / SOLAR_CYCLE_MONTHS

def predict_forward(S1, dt_months, R=R_solar):
    """Predict S₂ from S₁ using ARA temporal formula.
    
    For same-system temporal prediction: G = 0 (intensive, same scale)
    Δlog = R · sin(phase / R)
    S₂ = S₁ · 10^(Δlog)
    """
    if S1 <= 0:
        return S1  # can't log zero
    phase = time_to_phase(dt_months)
    delta_log = R * np.sin(phase / R)
    S2_pred = S1 * 10**delta_log
    return max(S2_pred, 0)  # sunspots can't be negative

def predict_reverse(S2, dt_months, R=R_solar):
    """Predict S₁ from S₂ using formula in REVERSE.
    
    Reverse = negate the phase (go backwards in time).
    S₁ = S₂ · 10^(-Δlog)
    """
    if S2 <= 0:
        return S2
    phase = time_to_phase(dt_months)
    delta_log = R * np.sin(phase / R)
    S1_pred = S2 * 10**(-delta_log)
    return max(S1_pred, 0)

# ── Baselines ──────────────────────────────────────────────────────
def baseline_naive(S1):
    """Predict same number."""
    return S1

def baseline_mean(S1):
    """Predict global mean."""
    return values.mean()

def baseline_cycle_mean(idx, dt=12):
    """Predict from same phase in previous cycle."""
    # Look back ~11 years to find same phase
    lookback = SOLAR_CYCLE_MONTHS
    target = idx + dt
    cycle_idx = target - lookback
    if 0 <= cycle_idx < N:
        return values[cycle_idx]
    return values.mean()

# ── Run trials ─────────────────────────────────────────────────────
DT = 12  # 1 year skip
NUM_TRIALS = 500

random.seed(42)
np.random.seed(42)

# Pick random starting indices (must have room for +12 months)
max_start = N - DT - 1
indices = sorted(random.sample(range(max_start), min(NUM_TRIALS, max_start)))

results = {
    'forward': {'ara': [], 'naive': [], 'mean': [], 'cycle': []},
    'reverse': {'ara': [], 'naive': [], 'mean': []}
}

forward_details = []

for idx in indices:
    S1 = values[idx]
    S2_actual = values[idx + DT]
    
    if S1 <= 0 or S2_actual <= 0:
        continue  # skip zero months
    
    # Forward prediction
    S2_ara = predict_forward(S1, DT)
    S2_naive = baseline_naive(S1)
    S2_mean = baseline_mean(S1)
    S2_cycle = baseline_cycle_mean(idx, DT)
    
    err_ara = abs(S2_ara - S2_actual)
    err_naive = abs(S2_naive - S2_actual)
    err_mean = abs(S2_mean - S2_actual)
    err_cycle = abs(S2_cycle - S2_actual)
    
    results['forward']['ara'].append(err_ara)
    results['forward']['naive'].append(err_naive)
    results['forward']['mean'].append(err_mean)
    results['forward']['cycle'].append(err_cycle)
    
    # Reverse prediction
    S1_ara = predict_reverse(S2_actual, DT)
    S1_naive = S2_actual  # naive: same number
    S1_mean = values.mean()
    
    rev_err_ara = abs(S1_ara - S1)
    rev_err_naive = abs(S1_naive - S1)
    rev_err_mean = abs(S1_mean - S1)
    
    results['reverse']['ara'].append(rev_err_ara)
    results['reverse']['naive'].append(rev_err_naive)
    results['reverse']['mean'].append(rev_err_mean)
    
    forward_details.append({
        'idx': idx, 'date': f"{months[idx][0]}-{months[idx][1]:02d}",
        'S1': S1, 'S2_actual': S2_actual, 'S2_ara': S2_ara,
        'err_ara': err_ara, 'err_naive': err_naive
    })

n_trials = len(results['forward']['ara'])
print(f"=== SCRIPT 161: SUNSPOT TEMPORAL PREDICTION ===")
print(f"Trials: {n_trials} (skipped {len(indices) - n_trials} zero-SSN months)")
print(f"Time gap: {DT} months (1 year)")
print(f"R_solar: {R_solar}")
print(f"Solar cycle period: {SOLAR_CYCLE_MONTHS} months")
print()

# ── Forward results ────────────────────────────────────────────────
print("─── FORWARD PREDICTION (S₁ → S₂) ───")
for name, errs in results['forward'].items():
    errs = np.array(errs)
    print(f"  {name:8s}: mean error = {errs.mean():7.1f}, median = {np.median(errs):7.1f}, "
          f"std = {errs.std():7.1f}")

# ARA beats naive?
ara_fwd = np.array(results['forward']['ara'])
naive_fwd = np.array(results['forward']['naive'])
mean_fwd = np.array(results['forward']['mean'])
cycle_fwd = np.array(results['forward']['cycle'])

beats_naive = np.sum(ara_fwd < naive_fwd) / n_trials * 100
beats_mean = np.sum(ara_fwd < mean_fwd) / n_trials * 100
beats_cycle = np.sum(ara_fwd < cycle_fwd) / n_trials * 100

print(f"\n  ARA beats naive: {beats_naive:.1f}%")
print(f"  ARA beats mean:  {beats_mean:.1f}%")
print(f"  ARA beats cycle: {beats_cycle:.1f}%")

# ── Reverse results ────────────────────────────────────────────────
print("\n─── REVERSE PREDICTION (S₂ → S₁) ───")
for name, errs in results['reverse'].items():
    errs = np.array(errs)
    print(f"  {name:8s}: mean error = {errs.mean():7.1f}, median = {np.median(errs):7.1f}, "
          f"std = {errs.std():7.1f}")

ara_rev = np.array(results['reverse']['ara'])
naive_rev = np.array(results['reverse']['naive'])
mean_rev = np.array(results['reverse']['mean'])

beats_naive_rev = np.sum(ara_rev < naive_rev) / n_trials * 100
beats_mean_rev = np.sum(ara_rev < mean_rev) / n_trials * 100

print(f"\n  ARA beats naive: {beats_naive_rev:.1f}%")
print(f"  ARA beats mean:  {beats_mean_rev:.1f}%")

# ── Round-trip consistency ─────────────────────────────────────────
print("\n─── ROUND-TRIP CONSISTENCY ───")
print("  (Forward then reverse should return to S₁)")
roundtrip_errors = []
for d in forward_details:
    S2_ara = d['S2_ara']
    if S2_ara > 0:
        S1_roundtrip = predict_reverse(S2_ara, DT)
        roundtrip_err = abs(S1_roundtrip - d['S1'])
        roundtrip_errors.append(roundtrip_err)

roundtrip_errors = np.array(roundtrip_errors)
print(f"  Mean roundtrip error: {roundtrip_errors.mean():.4f}")
print(f"  Max roundtrip error:  {roundtrip_errors.max():.4f}")
if roundtrip_errors.mean() < 0.01:
    print("  ✓ Formula is self-consistent (forward + reverse ≈ identity)")
else:
    print(f"  Note: sin is nonlinear, so roundtrip isn't exact")

# ── Test multiple time gaps ────────────────────────────────────────
print("\n─── MULTIPLE TIME GAPS ───")
time_gaps = [1, 3, 6, 12, 24, 66, 132]  # months
gap_names = ['1mo', '3mo', '6mo', '1yr', '2yr', '½cyc', 'full']

for dt, name in zip(time_gaps, gap_names):
    max_idx = N - dt - 1
    if max_idx < 100:
        continue
    sample_indices = random.sample(range(max_idx), min(300, max_idx))
    
    ara_errs = []
    naive_errs = []
    for idx in sample_indices:
        S1 = values[idx]
        S2 = values[idx + dt]
        if S1 <= 0 or S2 <= 0:
            continue
        S2_pred = predict_forward(S1, dt)
        ara_errs.append(abs(S2_pred - S2))
        naive_errs.append(abs(S1 - S2))
    
    if len(ara_errs) > 0:
        ara_mean = np.mean(ara_errs)
        naive_mean = np.mean(naive_errs)
        beat_pct = np.sum(np.array(ara_errs) < np.array(naive_errs)) / len(ara_errs) * 100
        ratio = ara_mean / naive_mean if naive_mean > 0 else float('inf')
        print(f"  {name:5s} (dt={dt:3d}): ARA mean={ara_mean:7.1f}, naive={naive_mean:7.1f}, "
              f"ratio={ratio:.3f}, ARA wins={beat_pct:.1f}%")

# ── Test multiple R values ─────────────────────────────────────────
print("\n─── R-VALUE SENSITIVITY ───")
R_candidates = [1.0, 1.354, PHI, 1.73, 1.914, 2.0, np.pi, np.e]
R_names = ['1.0', 'R_clock', 'φ', 'R_solar', 'R_snap', '2.0', 'π', 'e']

for R_val, R_name in zip(R_candidates, R_names):
    errs = []
    for idx in indices[:300]:
        S1 = values[idx]
        S2 = values[idx + DT]
        if S1 <= 0 or S2 <= 0:
            continue
        S2_pred = predict_forward(S1, DT, R=R_val)
        errs.append(abs(S2_pred - S2))
    if errs:
        print(f"  R={R_name:8s} ({R_val:.4f}): mean error = {np.mean(errs):7.1f}, "
              f"median = {np.median(errs):7.1f}")

# ── Phase-aware prediction ─────────────────────────────────────────
# The formula might work better if we account for WHERE in the solar
# cycle we are (ascending vs descending phase)
print("\n─── PHASE-AWARE ANALYSIS ───")
print("  (Does the formula work better during rising/falling phases?)")

# Simple rising/falling classification: compare to 12-month trailing average
rising_ara = []
falling_ara = []
rising_naive = []
falling_naive = []

for d in forward_details:
    idx = d['idx']
    if idx >= 12:
        trailing = values[idx-12:idx].mean()
        if d['S1'] > trailing:
            rising_ara.append(d['err_ara'])
            rising_naive.append(d['err_naive'])
        else:
            falling_ara.append(d['err_ara'])
            falling_naive.append(d['err_naive'])

if rising_ara and falling_ara:
    rising_ara = np.array(rising_ara)
    falling_ara = np.array(falling_ara)
    rising_naive = np.array(rising_naive)
    falling_naive = np.array(falling_naive)
    
    print(f"  Rising phase ({len(rising_ara)} trials):")
    print(f"    ARA mean: {rising_ara.mean():.1f}, naive: {rising_naive.mean():.1f}, "
          f"ARA/naive: {rising_ara.mean()/rising_naive.mean():.3f}")
    print(f"  Falling phase ({len(falling_ara)} trials):")
    print(f"    ARA mean: {falling_ara.mean():.1f}, naive: {falling_naive.mean():.1f}, "
          f"ARA/naive: {falling_ara.mean()/falling_naive.mean():.3f}")

# ── Log-space analysis ─────────────────────────────────────────────
print("\n─── LOG-SPACE ANALYSIS ───")
print("  (Formula operates in log space — how does it perform there?)")
log_ara_errs = []
log_naive_errs = []
for d in forward_details:
    if d['S1'] > 0 and d['S2_actual'] > 0 and d['S2_ara'] > 0:
        log_actual = np.log10(d['S2_actual'])
        log_pred = np.log10(d['S2_ara'])
        log_naive = np.log10(d['S1'])
        log_ara_errs.append(abs(log_pred - log_actual))
        log_naive_errs.append(abs(log_naive - log_actual))

log_ara = np.array(log_ara_errs)
log_naive = np.array(log_naive_errs)
print(f"  ARA mean |Δlog| error:  {log_ara.mean():.4f}")
print(f"  Naive mean |Δlog| error: {log_naive.mean():.4f}")
print(f"  ARA beats naive in log: {np.sum(log_ara < log_naive)/len(log_ara)*100:.1f}%")

# ── Show some example predictions ──────────────────────────────────
print("\n─── EXAMPLE PREDICTIONS (first 10) ───")
print(f"  {'Date':>10s}  {'S₁':>7s}  {'S₂ actual':>9s}  {'S₂ ARA':>8s}  {'error':>7s}  {'naive err':>9s}")
for d in forward_details[:10]:
    print(f"  {d['date']:>10s}  {d['S1']:7.1f}  {d['S2_actual']:9.1f}  {d['S2_ara']:8.1f}  "
          f"{d['err_ara']:7.1f}  {d['err_naive']:9.1f}")

# ── Overall scoring ────────────────────────────────────────────────
print("\n" + "="*60)
print("SCRIPT 161 VERDICT")
print("="*60)

score = 0
total = 5

# 1. Forward beats naive?
if beats_naive > 50:
    score += 1
    print(f"  [PASS] Forward ARA beats naive {beats_naive:.1f}% of time")
else:
    print(f"  [FAIL] Forward ARA beats naive only {beats_naive:.1f}% of time")

# 2. Reverse beats naive?
if beats_naive_rev > 50:
    score += 1
    print(f"  [PASS] Reverse ARA beats naive {beats_naive_rev:.1f}% of time")
else:
    print(f"  [FAIL] Reverse ARA beats naive only {beats_naive_rev:.1f}% of time")

# 3. Round-trip consistent?
if roundtrip_errors.mean() < 1.0:
    score += 1
    print(f"  [PASS] Round-trip mean error: {roundtrip_errors.mean():.4f}")
else:
    print(f"  [FAIL] Round-trip mean error: {roundtrip_errors.mean():.4f}")

# 4. ARA beats mean baseline?
if beats_mean > 50:
    score += 1
    print(f"  [PASS] ARA beats global mean {beats_mean:.1f}% of time")
else:
    print(f"  [FAIL] ARA beats global mean only {beats_mean:.1f}% of time")

# 5. Log-space performance
if np.sum(log_ara < log_naive)/len(log_ara) > 0.50:
    score += 1
    print(f"  [PASS] ARA wins in log space {np.sum(log_ara < log_naive)/len(log_ara)*100:.1f}%")
else:
    print(f"  [FAIL] ARA loses in log space {np.sum(log_ara < log_naive)/len(log_ara)*100:.1f}%")

print(f"\n  SCORE: {score}/{total}")

# ── Extract data for Script 162 ────────────────────────────────────
# Save the formula's Δlog values for cross-scale transposition
print("\n─── DATA FOR CROSS-SCALE TRANSPOSITION ───")
delta_logs = []
for d in forward_details:
    if d['S1'] > 0 and d['S2_actual'] > 0:
        actual_dlog = np.log10(d['S2_actual']) - np.log10(d['S1'])
        phase = time_to_phase(DT)
        formula_dlog = R_solar * np.sin(phase / R_solar)
        delta_logs.append({
            'date': d['date'],
            'S1': d['S1'],
            'S2': d['S2_actual'],
            'actual_dlog': actual_dlog,
            'formula_dlog': formula_dlog
        })

print(f"  Formula Δlog for 1-year gap: {delta_logs[0]['formula_dlog']:.6f}")
print(f"  Actual Δlog mean: {np.mean([d['actual_dlog'] for d in delta_logs]):.6f}")
print(f"  Actual Δlog std:  {np.std([d['actual_dlog'] for d in delta_logs]):.6f}")
print(f"  Phase angle (1 year): {time_to_phase(DT):.6f} rad = {np.degrees(time_to_phase(DT)):.2f}°")

print("\nScript 161 complete.")
