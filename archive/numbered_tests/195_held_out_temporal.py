#!/usr/bin/env python3
"""
Script 195 — Held-Out Temporal Prediction Test
================================================

PURPOSE: Answer peer reviewer's overfitting critique (Issue #15, Audit v7).

The reviewer's argument: Scripts 161-192 tested ~200-600 model configurations
against the same 8 criteria on the same data. Achieving 8/8 after that search
is expected by chance. The 8/8 claim is not credible without held-out testing.

PROTOCOL:
    1. FREEZE the exact V4 asymmetric engine basin from Script 192
       Parameters: depth_scale=1.0, basin_up=0.1, basin_down=1.0, floor=0.5
       (These are the winning parameters from the original search.)

    2. TRAIN on pre-2000 sunspot data ONLY
       - Phase calibration uses years ≤ 1999 exclusively
       - C (log-space mean) computed from ≤ 1999 data exclusively
       - No information from 2000+ enters training

    3. PREDICT 2000-2025 blind (26 years unseen)
       - Iterative: each year's prediction feeds the next
       - Starting value: actual 1999 SSN

    4. SCORE against the same 8 criteria used in Script 192
       - SSN correlation > 0.3
       - Beats naive in ≥3 windows
       - Within 2× for >30% of predictions
       - Direction accuracy > 55%
       - EQ correlation > 0.2
       - EQ within 2× for >30%
       - MAE beats naive in ≥3 windows
       - No drift (MAE < 500 in all windows)

    5. COMPARE to baselines:
       - Naive persistence (predict last known value forever)
       - Simple 11-year sine fit (best sinusoidal fit to training data)
       - Mean reversion (predict C forever)

    6. ALSO test multiple train/test splits:
       - Train ≤1989, predict 1990-2025 (36 years)
       - Train ≤1994, predict 1995-2025 (31 years)
       - Train ≤1999, predict 2000-2025 (26 years)
       - Train ≤2004, predict 2005-2025 (21 years)
       - Train ≤2009, predict 2010-2025 (16 years)

    NO PARAMETER SEARCHING. One model, one set of frozen parameters.
    Pass or fail. This is the test the reviewer asked for.
"""

import numpy as np
import os

# ═══════════════════════════════════════════════════════════════════
# FRAMEWORK CONSTANTS (identical to Script 192)
# ═══════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3
PHI_LEAK = 1.0 / PHI

ARA_SSN = 1.73
ARA_EQ  = 0.15
MIDPOINT_OFFSET = abs((ARA_SSN + ARA_EQ) / 2 - R_COUPLER)

# FROZEN V4 parameters — exactly as selected in Script 192
V4_DEPTH = 1.0
V4_BASIN_UP = 0.1
V4_BASIN_DOWN = 1.0
V4_FLOOR = 0.5

# ═══════════════════════════════════════════════════════════════════
# MODEL (copied verbatim from Script 192)
# ═══════════════════════════════════════════════════════════════════

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def effective_ara(ara_base, t, phase0):
    center = 1.0
    amp = ara_base - center
    return center + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

def base_wave_dlog(log_val, C, R_matter, step, t, phase0):
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)
    phi = value_to_longitude(log_val, C, eff)
    phi_next = phi + GA_OVER_PHI * step

    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    s1n = wave(phi, R_matter)
    s2n = wave(phi+HALF_PHI, R_matter)
    s1x = wave(phi_next, R_matter)
    s2x = wave(phi_next+HALF_PHI, R_matter)
    outer = ((s1x+s2x)/2 - (s1n+s2n)/2) * np.exp(-MIDPOINT_OFFSET)

    drive = eff - 1.0
    distance = abs(log_val - C)
    gear = max(distance / HALF_PHI, 0.1)

    wdlog = inner + drive * gear * outer
    return wdlog, eff

def v4_predict(log_val, C, R_matter, step, t, phase0):
    """V4 Asymmetric Engine Basin — FROZEN from Script 192."""
    wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
    bounced = log_val + wdlog

    engine_factor = max(R_matter - 1.0, 0.0)
    valley_amp = engine_factor * V4_DEPTH
    valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

    displacement = bounced - valley
    if displacement > 0:
        correction = -engine_factor * V4_BASIN_DOWN * displacement
    else:
        correction = -engine_factor * V4_BASIN_UP * displacement

    new_val = bounced + correction

    floor = C - V4_FLOOR
    if new_val < floor:
        new_val = floor + (new_val - floor) * 0.1

    return new_val

# ═══════════════════════════════════════════════════════════════════
# PHASE CALIBRATION (uses ONLY training data)
# ═══════════════════════════════════════════════════════════════════

def calibrate_phase(train_data, R_matter, n_phases=24):
    """Find optimal phase offset using ONLY training data."""
    years = sorted(train_data.keys())
    if len(years) < 20:
        return 0.0
    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase = 0.0
    best_score = -999
    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases
        # Use last 15 years of TRAINING data for phase calibration
        test_start = max(0, len(years) - 15)
        current = np.log10(max(train_data[years[test_start]], 0.1))
        pred_changes, act_changes = [], []
        for i in range(test_start + 1, len(years)):
            t = i - test_start
            new = v4_predict(current, C, R_matter, 1, t, phase0)
            pred_changes.append(new - current)
            actual = np.log10(max(train_data[years[i]], 0.1)) - \
                     np.log10(max(train_data[years[i-1]], 0.1))
            act_changes.append(actual)
            current = np.log10(max(train_data[years[i]], 0.1))
        if len(pred_changes) < 5:
            continue
        p = np.array(pred_changes)
        a = np.array(act_changes)
        corr = float(np.corrcoef(p, a)[0, 1]) if np.std(p) > 0 and np.std(a) > 0 else 0
        dm = sum(1 for x, y in zip(p, a) if np.sign(x) == np.sign(y)) / len(p)
        score = corr + dm
        if score > best_score:
            best_score = score
            best_phase = phase0
    return best_phase

# ═══════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════

def load_ssn():
    """Load sunspot data, return dict {year: annual_mean}."""
    p = os.path.join(os.path.dirname(__file__), '..', 'solar_test', 'sunspots.txt')
    monthly = {}
    with open(p) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                y = int(parts[0])
                v = float(parts[3])
                if v < 0:
                    continue
                monthly.setdefault(y, []).append(v)
            except:
                continue
    return {y: np.mean(v) for y, v in monthly.items() if len(v) >= 6}

def load_eq():
    """Earthquake data (M6.0+ per year). Same as Script 192."""
    return {
        1900:13,1901:14,1902:8,1903:10,1904:16,1905:26,1906:32,1907:27,
        1908:18,1909:32,1910:36,1911:24,1912:22,1913:23,1914:22,1915:18,
        1916:25,1917:21,1918:21,1919:14,1920:8,1921:11,1922:14,1923:23,
        1924:18,1925:17,1926:19,1927:20,1928:22,1929:19,1930:13,1931:26,
        1932:13,1933:14,1934:22,1935:24,1936:21,1937:22,1938:26,1939:21,
        1940:23,1941:24,1942:27,1943:41,1944:31,1945:27,1946:35,1947:26,
        1948:28,1949:36,1950:15,1951:21,1952:17,1953:22,1954:17,1955:19,
        1956:15,1957:34,1958:10,1959:15,1960:22,1961:18,1962:15,1963:20,
        1964:15,1965:22,1966:19,1967:16,1968:30,1969:27,1970:29,1971:23,
        1972:20,1973:16,1974:21,1975:21,1976:25,1977:16,1978:18,1979:15,
        1980:18,1981:14,1982:10,1983:15,1984:8,1985:15,1986:6,1987:11,
        1988:8,1989:7,1990:13,1991:11,1992:23,1993:16,1994:15,1995:25,
        1996:22,1997:20,1998:16,1999:23,2000:16,2001:15,2002:13,2003:14,
        2004:16,2005:11,2006:11,2007:18,2008:12,2009:16,2010:23,2011:19,
        2012:12,2013:17,2014:11,2015:19,2016:16,2017:7,2018:17,2019:11,
        2020:9,2021:16,2022:10,2023:18,2024:15
    }

# ═══════════════════════════════════════════════════════════════════
# BASELINES
# ═══════════════════════════════════════════════════════════════════

def baseline_naive(start_val, n_years):
    """Predict last known value forever."""
    return [start_val] * n_years

def baseline_mean(C_linear, n_years):
    """Predict training mean forever."""
    return [C_linear] * n_years

def baseline_sine(train_data, test_years):
    """Best-fit 11-year sinusoid from training data."""
    years = sorted(train_data.keys())
    vals = np.array([train_data[y] for y in years])
    mean_val = np.mean(vals)
    amp = np.std(vals) * np.sqrt(2)

    # Fit phase to training data
    best_phase = 0
    best_corr = -999
    for pi in range(48):
        ph = 2 * np.pi * pi / 48
        fitted = mean_val + amp * np.sin(2 * np.pi * np.array(years) / 11.0 + ph)
        c = np.corrcoef(vals, fitted)[0, 1]
        if c > best_corr:
            best_corr = c
            best_phase = ph

    # Predict test years
    preds = mean_val + amp * np.sin(2 * np.pi * np.array(test_years) / 11.0 + best_phase)
    return [max(p, 0) for p in preds]

# ═══════════════════════════════════════════════════════════════════
# HELD-OUT PREDICTION
# ═══════════════════════════════════════════════════════════════════

def held_out_predict(all_data, cutoff_year, R_matter):
    """
    Train on data ≤ cutoff_year. Predict all subsequent years.
    Returns (predictions, actuals, test_years, phase0, C, naive_val, train_data).
    """
    train = {y: v for y, v in all_data.items() if y <= cutoff_year}
    test = {y: v for y, v in all_data.items() if y > cutoff_year}

    if len(train) < 20 or len(test) < 5:
        return None

    C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
    phase0 = calibrate_phase(train, R_matter)

    test_years = sorted(test.keys())
    start_val = train[max(train.keys())]
    current = np.log10(max(start_val, 0.1))

    preds = []
    for i, y in enumerate(test_years):
        current = v4_predict(current, C, R_matter, 1, i + 1, phase0)
        preds.append(10 ** current)

    actuals = [all_data[y] for y in test_years]

    return {
        'preds': preds,
        'actuals': actuals,
        'years': test_years,
        'phase0': phase0,
        'C': C,
        'naive_val': start_val,
        'train_data': train,
        'C_linear': np.mean(list(train.values()))
    }

# ═══════════════════════════════════════════════════════════════════
# SCORING
# ═══════════════════════════════════════════════════════════════════

def score_predictions(preds, actuals, naive_val):
    """Compute all metrics for a single prediction run."""
    a = np.array(actuals, dtype=float)
    p = np.array(preds, dtype=float)
    n = len(a)

    # Correlation
    corr = float(np.corrcoef(a, p)[0, 1]) if np.std(a) > 0 and np.std(p) > 0 else 0

    # Within 2×
    within_2x = sum(1 for pi, ai in zip(p, a)
                    if 0.5 <= max(pi, 0.1) / max(ai, 0.1) <= 2.0) / n * 100

    # Direction accuracy
    dir_correct = 0
    dir_total = 0
    for i in range(1, n):
        if a[i] != a[i-1]:
            dir_total += 1
            if np.sign(p[i] - p[i-1]) == np.sign(a[i] - a[i-1]):
                dir_correct += 1
    direction = dir_correct / max(dir_total, 1) * 100

    # MAE
    mae = float(np.mean(np.abs(a - p)))
    naive_mae = float(np.mean(np.abs(a - naive_val)))
    beats_naive = mae < naive_mae

    return {
        'corr': corr,
        'within_2x': within_2x,
        'direction': direction,
        'mae': mae,
        'naive_mae': naive_mae,
        'beats_naive': beats_naive,
        'n': n
    }

def score_8_criteria(ssn_results_list, eq_results_list):
    """
    Apply the same 8 criteria from Script 192.
    ssn_results_list and eq_results_list are lists of score dicts
    from multiple cutoff windows.
    """
    score = 0
    details = []

    # 1. SSN correlation > 0.3
    avg_corr = np.mean([r['corr'] for r in ssn_results_list])
    p = avg_corr > 0.3
    score += p
    details.append(f"SSNc={avg_corr:+.3f} {'PASS' if p else 'FAIL'}")

    # 2. Beats naive in ≥3 windows
    bn = sum(1 for r in ssn_results_list if r['beats_naive'])
    p = bn >= 3
    score += p
    details.append(f"beats_naive={bn}/{len(ssn_results_list)} {'PASS' if p else 'FAIL'}")

    # 3. Within 2× for >30%
    avg_2x = np.mean([r['within_2x'] for r in ssn_results_list])
    p = avg_2x > 30
    score += p
    details.append(f"within_2x={avg_2x:.1f}% {'PASS' if p else 'FAIL'}")

    # 4. Direction accuracy > 55%
    avg_dir = np.mean([r['direction'] for r in ssn_results_list])
    p = avg_dir > 55
    score += p
    details.append(f"direction={avg_dir:.1f}% {'PASS' if p else 'FAIL'}")

    # 5. EQ correlation > 0.2
    avg_eq_corr = np.mean([r['corr'] for r in eq_results_list])
    p = avg_eq_corr > 0.2
    score += p
    details.append(f"EQc={avg_eq_corr:+.3f} {'PASS' if p else 'FAIL'}")

    # 6. EQ within 2× > 30%
    avg_eq_2x = np.mean([r['within_2x'] for r in eq_results_list])
    p = avg_eq_2x > 30
    score += p
    details.append(f"EQ_2x={avg_eq_2x:.1f}% {'PASS' if p else 'FAIL'}")

    # 7. MAE beats naive in ≥3 windows
    bm = sum(1 for r in ssn_results_list if r['mae'] < r['naive_mae'])
    p = bm >= 3
    score += p
    details.append(f"MAE_wins={bm}/{len(ssn_results_list)} {'PASS' if p else 'FAIL'}")

    # 8. No drift
    no_drift = all(r['mae'] < 500 for r in ssn_results_list)
    score += no_drift
    details.append(f"drift={'PASS' if no_drift else 'FAIL'}")

    return score, details

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    ssn = load_ssn()
    eq = load_eq()

    print("=" * 75)
    print("SCRIPT 195 — HELD-OUT TEMPORAL PREDICTION TEST")
    print("=" * 75)
    print()
    print("PURPOSE: Answer peer reviewer's overfitting critique (Issue #15)")
    print("MODEL:   V4 asymmetric engine basin from Script 192")
    print(f"PARAMS:  depth={V4_DEPTH}, basin_up={V4_BASIN_UP}, "
          f"basin_down={V4_BASIN_DOWN}, floor={V4_FLOOR}")
    print("NOTE:    Parameters FROZEN. No searching. One model, pass or fail.")
    print()

    # ── SSN held-out tests across multiple splits ──
    ssn_cutoffs = [1989, 1994, 1999, 2004, 2009]
    eq_cutoffs = [1989, 1994, 1999, 2004, 2009]

    print("=" * 75)
    print("PART 1: SUNSPOT PREDICTIONS (ARA=1.73, Engine)")
    print("=" * 75)

    ssn_score_list = []
    for cutoff in ssn_cutoffs:
        result = held_out_predict(ssn, cutoff, ARA_SSN)
        if result is None:
            print(f"\n  Train ≤{cutoff}: insufficient data, skipping")
            continue

        scores = score_predictions(result['preds'], result['actuals'],
                                    result['naive_val'])
        ssn_score_list.append(scores)

        # Baselines
        n = len(result['years'])
        naive_preds = baseline_naive(result['naive_val'], n)
        mean_preds = baseline_mean(result['C_linear'], n)
        sine_preds = baseline_sine(result['train_data'], result['years'])

        naive_scores = score_predictions(naive_preds, result['actuals'],
                                          result['naive_val'])
        mean_scores = score_predictions(mean_preds, result['actuals'],
                                         result['naive_val'])
        sine_scores = score_predictions(sine_preds, result['actuals'],
                                         result['naive_val'])

        print(f"\n  Train ≤{cutoff}, Predict {result['years'][0]}-"
              f"{result['years'][-1]} ({n} years)")
        print(f"  Phase φ₀ = {result['phase0']:.3f}, "
              f"C = {result['C']:.3f} (log₁₀)")
        print()

        print(f"  {'Model':<20} {'Corr':>8} {'Dir%':>8} {'×2%':>8} "
              f"{'MAE':>8} {'vs Naive':>10}")
        print(f"  {'-'*20} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")
        print(f"  {'ARA Watershed':<20} {scores['corr']:>+8.3f} "
              f"{scores['direction']:>8.1f} {scores['within_2x']:>8.1f} "
              f"{scores['mae']:>8.1f} "
              f"{'WIN' if scores['beats_naive'] else 'LOSE':>10}")
        print(f"  {'Naive (persist)':<20} {naive_scores['corr']:>+8.3f} "
              f"{naive_scores['direction']:>8.1f} {naive_scores['within_2x']:>8.1f} "
              f"{naive_scores['mae']:>8.1f} {'---':>10}")
        print(f"  {'11yr Sine':<20} {sine_scores['corr']:>+8.3f} "
              f"{sine_scores['direction']:>8.1f} {sine_scores['within_2x']:>8.1f} "
              f"{sine_scores['mae']:>8.1f} "
              f"{'WIN' if sine_scores['mae'] < naive_scores['mae'] else 'LOSE':>10}")
        print(f"  {'Training Mean':<20} {mean_scores['corr']:>+8.3f} "
              f"{mean_scores['direction']:>8.1f} {mean_scores['within_2x']:>8.1f} "
              f"{mean_scores['mae']:>8.1f} "
              f"{'WIN' if mean_scores['mae'] < naive_scores['mae'] else 'LOSE':>10}")

        # Show actual vs predicted for key years
        print(f"\n  Year-by-year (first 15 years):")
        print(f"  {'Year':>6} {'Actual':>8} {'ARA':>8} {'Naive':>8} {'Sine':>8}")
        for i in range(min(15, n)):
            print(f"  {result['years'][i]:>6} {result['actuals'][i]:>8.1f} "
                  f"{result['preds'][i]:>8.1f} "
                  f"{naive_preds[i]:>8.1f} "
                  f"{sine_preds[i]:>8.1f}")

    # ── EQ held-out tests ──
    print(f"\n{'='*75}")
    print("PART 2: EARTHQUAKE PREDICTIONS (ARA=0.15, Consumer)")
    print("=" * 75)

    eq_score_list = []
    for cutoff in eq_cutoffs:
        result = held_out_predict(eq, cutoff, ARA_EQ)
        if result is None:
            print(f"\n  Train ≤{cutoff}: insufficient data, skipping")
            continue

        scores = score_predictions(result['preds'], result['actuals'],
                                    result['naive_val'])
        eq_score_list.append(scores)

        n = len(result['years'])
        naive_preds = baseline_naive(result['naive_val'], n)

        print(f"\n  Train ≤{cutoff}, Predict {result['years'][0]}-"
              f"{result['years'][-1]} ({n} years)")
        print(f"  Corr={scores['corr']:+.3f}, Dir={scores['direction']:.1f}%, "
              f"×2={scores['within_2x']:.1f}%, MAE={scores['mae']:.1f}, "
              f"vs naive: {'WIN' if scores['beats_naive'] else 'LOSE'}")

        # Show first 10 years
        print(f"  {'Year':>6} {'Actual':>8} {'ARA':>8} {'Naive':>8}")
        for i in range(min(10, n)):
            print(f"  {result['years'][i]:>6} {result['actuals'][i]:>8.1f} "
                  f"{result['preds'][i]:>8.1f} "
                  f"{naive_preds[i]:>8.1f}")

    # ── FINAL 8-CRITERIA SCORING ──
    print(f"\n{'='*75}")
    print("PART 3: 8-CRITERIA SCORING (HELD-OUT)")
    print("=" * 75)

    if ssn_score_list and eq_score_list:
        total, details = score_8_criteria(ssn_score_list, eq_score_list)

        print(f"\n  ┌─────────────────────────────────────────────────┐")
        print(f"  │  HELD-OUT SCORE:  {total}/8                          │")
        print(f"  └─────────────────────────────────────────────────┘")
        print()
        for d in details:
            print(f"    {d}")

        print(f"\n  For reference:")
        print(f"    Script 192 (training data): 8/8")
        print(f"    Script 161 (original ARA):  1/5")
        print(f"    Peer reviewer threshold:    beats naive persistence")

        # ── Detailed comparison ──
        print(f"\n{'='*75}")
        print("PART 4: HONEST ASSESSMENT")
        print("=" * 75)

        avg_ssn_corr = np.mean([r['corr'] for r in ssn_score_list])
        avg_ssn_dir = np.mean([r['direction'] for r in ssn_score_list])
        avg_ssn_2x = np.mean([r['within_2x'] for r in ssn_score_list])
        ssn_wins = sum(1 for r in ssn_score_list if r['beats_naive'])

        print(f"\n  SSN avg correlation:  {avg_ssn_corr:+.3f}")
        print(f"  SSN avg direction:   {avg_ssn_dir:.1f}%")
        print(f"  SSN avg within 2×:   {avg_ssn_2x:.1f}%")
        print(f"  SSN naive wins:      {ssn_wins}/{len(ssn_score_list)}")

        avg_eq_corr = np.mean([r['corr'] for r in eq_score_list])
        print(f"  EQ  avg correlation: {avg_eq_corr:+.3f}")

        if total >= 7:
            print(f"\n  VERDICT: The watershed model PASSES on held-out data.")
            print(f"  The overfitting critique is addressed — the model generalizes.")
            if total == 8:
                print(f"  8/8 on UNSEEN data. The reviewer's Issue #15 is resolved.")
        elif total >= 5:
            print(f"\n  VERDICT: PARTIAL pass on held-out data ({total}/8).")
            print(f"  The model retains some predictive power but loses precision")
            print(f"  on unseen data. The asymmetric basin helps but doesn't fully")
            print(f"  generalize. Overfitting concern is partially justified.")
        else:
            print(f"\n  VERDICT: The watershed model FAILS on held-out data ({total}/8).")
            print(f"  The reviewer was right — the 8/8 from Script 192 was")
            print(f"  overfitting to the training data. The temporal prediction")
            print(f"  campaign needs fundamental rethinking.")

    else:
        print("\n  ERROR: Insufficient data to compute 8-criteria score.")

    print(f"\n{'='*75}")
    print("Script 195 complete.")
    print("=" * 75)
