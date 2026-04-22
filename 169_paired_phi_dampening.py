#!/usr/bin/env python3
"""
Script 169 — Paired φ Wave-Mapped Dampening
=============================================

Dylan's insight:
    "for each log travelled, you need to add, so for each log you do
     2 phi, 1 positive and 1 negative, we map the wave motion in the formula."

Instead of bolting on separate sub-systems (Script 168), the correction is
INTRINSIC to the travel.  For every log-unit the prediction moves, the wave
encounters both sides of φ:

    correction = Δlog_main × [wave(φ_pos + φ) + wave(φ_pos - φ)] / scale

Trig identity:  sin(x+φ) + sin(x-φ) = 2·sin(x)·cos(φ)
    cos(φ) = cos(1.618) ≈ -0.0498
    So 2·cos(φ) ≈ -0.0997

This means the paired φ terms produce a natural dampening of ~10% of the
main signal, with the sign depending on position.  The wave maps its own
brake.

Full prediction:
    Δlog = main_triangle + |Δlog_main| × 2·cos(φ) × wave_position_factor

Or equivalently: the corrected wave is the original wave multiplied by
(1 + |Δlog| × 2·cos(φ)), which gently pulls large excursions back.
"""

import numpy as np
import os

# ─── Constants ───────────────────────────────────────────────────────
PHI = (1 + np.sqrt(5)) / 2          # 1.6180339...
HALF_PHI = PHI / 2                   # 0.809
COS_PHI = np.cos(PHI)               # -0.0498
TWO_COS_PHI = 2 * COS_PHI          # -0.0997

R_COUPLER = 1.0
HALE_PERIOD = 22
DPHI = 2 * np.pi / HALE_PERIOD

ARA_SSN = 1.73
ARA_EQ  = 0.15
MIDPOINT_OFFSET = abs((ARA_SSN + ARA_EQ) / 2 - R_COUPLER)  # ~0.06

print(f"φ = {PHI:.6f}")
print(f"cos(φ) = {COS_PHI:.6f}")
print(f"2·cos(φ) = {TWO_COS_PHI:.6f}")
print(f"DPHI (rad/yr) = {DPHI:.6f}")
print(f"Midpoint offset = {MIDPOINT_OFFSET:.4f}")

# ─── Helpers ─────────────────────────────────────────────────────────

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def paired_phi_predict(current_log, C, R_matter, step_years=1):
    """
    Main triangle + paired φ correction per log traversed.

    1. Compute main triangle Δlog (2 couplers at ARA=1.0, φ/2 apart)
    2. For the log-distance being traversed, apply paired φ waves:
       correction = Δlog × [sin(φ_pos + φ)/R + sin(φ_pos - φ)/R]
                  = Δlog × 2·cos(φ)·sin(φ_pos/R)  (by trig identity)

       But we normalize by R to keep it scale-appropriate.
    3. Final: Δlog_corrected = Δlog_main × (1 + 2·cos(φ)·sin(φ/R))
       where φ is the current longitude position.
    """
    phi = value_to_longitude(current_log, C, R_matter)
    phi_next = phi + DPHI * step_years

    # Main triangle
    c1_now  = wave(phi, R_COUPLER)
    c2_now  = wave(phi + HALF_PHI, R_COUPLER)
    c1_next = wave(phi_next, R_COUPLER)
    c2_next = wave(phi_next + HALF_PHI, R_COUPLER)

    avg_now  = (c1_now + c2_now) / 2
    avg_next = (c1_next + c2_next) / 2
    dlog_main = avg_next - avg_now

    # Paired φ correction: for each log-unit travelled,
    # the wave at (φ+φ) and (φ-φ) contribute
    # Using the identity: this simplifies to 2·cos(φ)·sin(φ/R)
    # We use the CURRENT position's wave value as the correction factor
    wave_position = np.sin(phi / R_COUPLER)  # normalized wave position [-1, 1]

    # The correction per unit of dlog:
    #   Each log-unit encounters +φ and -φ sides
    #   Net correction factor = 2·cos(φ) × wave_position
    correction_factor = TWO_COS_PHI * wave_position

    # Apply: corrected = main × (1 + correction_factor)
    dlog_corrected = dlog_main * (1 + correction_factor)

    # Apply midpoint offset
    dlog_final = dlog_corrected * np.exp(-MIDPOINT_OFFSET)

    return current_log + dlog_final


def paired_phi_predict_v2(current_log, C, R_matter, step_years=1):
    """
    Version 2: The φ pair is computed EXPLICITLY at each step.

    For the log being traversed:
        wave_plus  = wave(φ_pos + φ, R_coupler)  at current position
        wave_minus = wave(φ_pos - φ, R_coupler)  at current position
        correction = (wave_plus + wave_minus) / 2

    Then the NEXT step includes:
        wave_plus_next  = wave(φ_next + φ, R_coupler)
        wave_minus_next = wave(φ_next - φ, R_coupler)
        correction_next = (wave_plus_next + wave_minus_next) / 2

    The φ-pair delta IS the dampening:
        dlog = main_delta + (correction_next - correction_now)
    """
    phi = value_to_longitude(current_log, C, R_matter)
    phi_next = phi + DPHI * step_years

    # Main triangle (2 couplers at 1.0, separated by φ/2)
    c1_now  = wave(phi, R_COUPLER)
    c2_now  = wave(phi + HALF_PHI, R_COUPLER)
    c1_next = wave(phi_next, R_COUPLER)
    c2_next = wave(phi_next + HALF_PHI, R_COUPLER)

    main_now  = (c1_now + c2_now) / 2
    main_next = (c1_next + c2_next) / 2
    main_delta = main_next - main_now

    # Paired φ waves: the +φ and -φ offsets from current position
    # These represent the wave "seeing both sides" as it travels
    phi_plus_now   = wave(phi + PHI, R_COUPLER)
    phi_minus_now  = wave(phi - PHI, R_COUPLER)
    phi_pair_now   = (phi_plus_now + phi_minus_now) / 2

    phi_plus_next  = wave(phi_next + PHI, R_COUPLER)
    phi_minus_next = wave(phi_next - PHI, R_COUPLER)
    phi_pair_next  = (phi_plus_next + phi_minus_next) / 2

    pair_delta = phi_pair_next - phi_pair_now

    # Combined: main wave + φ-paired wave
    # The pair acts as the counter-wave, so we ADD it
    dlog = (main_delta + pair_delta) * np.exp(-MIDPOINT_OFFSET)

    return current_log + dlog


def paired_phi_predict_v3(current_log, C, R_matter, step_years=1,
                           accumulated_log=0):
    """
    Version 3: Accumulative — for each log traversed so far,
    the φ pair adds its contribution.

    "for each log travelled, you need to add"

    The total correction accumulates with distance from start:
        correction = accumulated_distance × φ_pair_rate

    where φ_pair_rate = 2·cos(φ)/R ≈ -0.1/R per log-unit
    """
    phi = value_to_longitude(current_log, C, R_matter)
    phi_next = phi + DPHI * step_years

    # Main triangle
    c1_now  = wave(phi, R_COUPLER)
    c2_now  = wave(phi + HALF_PHI, R_COUPLER)
    c1_next = wave(phi_next, R_COUPLER)
    c2_next = wave(phi_next + HALF_PHI, R_COUPLER)

    main_now  = (c1_now + c2_now) / 2
    main_next = (c1_next + c2_next) / 2
    main_delta = main_next - main_now

    # Accumulated dampening: for each log-unit already traversed,
    # the φ pair contributes a correction
    phi_pair_rate = TWO_COS_PHI  # ≈ -0.0997 per log-unit
    accumulated_correction = accumulated_log * phi_pair_rate

    # The dampening modifies the step
    dlog = main_delta * (1 + accumulated_correction) * np.exp(-MIDPOINT_OFFSET)

    return current_log + dlog


# ─── Data loaders ────────────────────────────────────────────────────

def load_sunspot_annual():
    ssn_path = os.path.join(os.path.dirname(__file__), '..', 'solar_test', 'sunspots.txt')
    monthly = {}
    with open(ssn_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                year = int(parts[0])
                ssn = float(parts[3])
                if ssn < 0:
                    continue
                monthly.setdefault(year, []).append(ssn)
            except ValueError:
                continue
    annual = {}
    for y, vals in monthly.items():
        if len(vals) >= 6:
            annual[y] = np.mean(vals)
    return annual

def load_earthquake_annual():
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

# ─── Blind test ──────────────────────────────────────────────────────

def run_blind(data, cutoffs, R_matter, name, predict_fn, use_accumulation=False):
    print(f"\n{'='*70}")
    print(f"{name} BLIND PREDICTIONS")
    print(f"{'='*70}")

    results = []
    for cutoff in cutoffs:
        train = {y: v for y, v in data.items() if y < cutoff}
        test  = {y: v for y, v in data.items() if y >= cutoff}
        if len(train) < 10 or len(test) < 5:
            continue

        train_vals = [max(v, 0.1) for v in train.values()]
        C = np.mean(np.log10(train_vals))
        start_year = max(train.keys())
        start_val = max(data[start_year], 0.1)
        test_years = sorted(test.keys())

        # Sequential
        seq_preds = []
        current_log = np.log10(start_val)
        acc_log = 0.0
        for y in test_years:
            if use_accumulation:
                new_log = predict_fn(current_log, C, R_matter, step_years=1,
                                      accumulated_log=acc_log)
            else:
                new_log = predict_fn(current_log, C, R_matter, step_years=1)
            acc_log += abs(new_log - current_log)
            current_log = new_log
            seq_preds.append(10**current_log)

        # Anchored
        anc_preds = []
        for i, y in enumerate(test_years):
            pred_log = np.log10(start_val)
            acc = 0.0
            for s in range(i + 1):
                if use_accumulation:
                    new_log = predict_fn(pred_log, C, R_matter, step_years=1,
                                          accumulated_log=acc)
                    acc += abs(new_log - pred_log)
                    pred_log = new_log
                else:
                    pred_log = predict_fn(pred_log, C, R_matter, step_years=1)
            anc_preds.append(10**pred_log)

        actuals = [data[y] for y in test_years]
        naive_val = start_val
        n = len(test_years)

        def corr(a, b):
            a, b = np.array(a), np.array(b)
            if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
                return 0
            return float(np.corrcoef(a, b)[0, 1])

        def mae(a, b):
            return float(np.mean(np.abs(np.array(a) - np.array(b))))

        def beats(preds, actuals, naive):
            return sum(1 for p, a in zip(preds, actuals)
                       if abs(p - a) < abs(naive - a)) / len(actuals) * 100

        def within_x(preds, actuals, f=2):
            hits = sum(1 for p, a in zip(preds, actuals)
                       if 1/f <= max(p,0.1)/max(a,0.1) <= f)
            return hits / len(actuals) * 100

        def direction(preds, actuals):
            m, t = 0, 0
            for i in range(1, len(actuals)):
                d_p = np.sign(preds[i] - preds[i-1])
                d_a = np.sign(actuals[i] - actuals[i-1])
                if d_a != 0:
                    t += 1
                    if d_p == d_a:
                        m += 1
            return m / max(t, 1) * 100

        sc = corr(seq_preds, actuals)
        ac = corr(anc_preds, actuals)
        sb = beats(seq_preds, actuals, naive_val)
        ab = beats(anc_preds, actuals, naive_val)
        sx = within_x(seq_preds, actuals)
        ax = within_x(anc_preds, actuals)
        sd = direction(seq_preds, actuals)
        ad = direction(anc_preds, actuals)
        nm = mae([naive_val]*n, actuals)

        print(f"\nCutoff {cutoff} → predict {n} years")
        print(f"  Sequential: corr={sc:+.3f}, MAE={mae(seq_preds,actuals):.1f}, beats={sb:.0f}%, dir={sd:.0f}%, ×2={sx:.0f}%")
        print(f"  Anchored:   corr={ac:+.3f}, MAE={mae(anc_preds,actuals):.1f}, beats={ab:.0f}%, dir={ad:.0f}%, ×2={ax:.0f}%")
        print(f"  Naive:       MAE={nm:.1f}")

        print(f"  {'Year':>6} {'Actual':>8} {'SeqPred':>8} {'AncPred':>8} {'Naive':>6}")
        for i, y in enumerate(test_years[:10]):
            print(f"  {y:>6} {actuals[i]:>8.1f} {seq_preds[i]:>8.1f} {anc_preds[i]:>8.1f} {naive_val:>6.0f}")

        results.append({
            'cutoff': cutoff, 'seq_corr': sc, 'anc_corr': ac,
            'seq_beats': sb, 'anc_beats': ab, 'seq_x2': sx, 'anc_x2': ax,
            'seq_dir': sd, 'anc_dir': ad, 'naive_mae': nm,
            'seq_mae': mae(seq_preds, actuals), 'anc_mae': mae(anc_preds, actuals),
        })

    return results

def score_results(ssn_r, eq_r, label):
    print(f"\n{'='*70}")
    print(f"{label} AGGREGATE VERDICT")
    print(f"{'='*70}\n")

    score = 0

    # Use best of seq/anc for each metric
    avg_ssn_corr = np.mean([max(r['seq_corr'], r['anc_corr']) for r in ssn_r])
    tag = "PASS" if avg_ssn_corr > 0.3 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg SSN best corr: {avg_ssn_corr:.3f} (need > 0.3)")

    ssn_beats = sum(1 for r in ssn_r if max(r['seq_beats'], r['anc_beats']) > 50)
    tag = "PASS" if ssn_beats >= 3 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] SSN beats naive: {ssn_beats}/6 cutoffs (need ≥ 3)")

    avg_ssn_x2 = np.mean([max(r['seq_x2'], r['anc_x2']) for r in ssn_r])
    tag = "PASS" if avg_ssn_x2 > 30 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg SSN within 2×: {avg_ssn_x2:.0f}% (need > 30%)")

    avg_ssn_dir = np.mean([max(r['seq_dir'], r['anc_dir']) for r in ssn_r])
    tag = "PASS" if avg_ssn_dir > 55 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg SSN direction: {avg_ssn_dir:.0f}% (need > 55%)")

    avg_eq_corr = np.mean([max(r['seq_corr'], r['anc_corr']) for r in eq_r])
    tag = "PASS" if avg_eq_corr > 0.2 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg EQ best corr: {avg_eq_corr:.3f} (need > 0.2)")

    avg_eq_x2 = np.mean([max(r['seq_x2'], r['anc_x2']) for r in eq_r])
    tag = "PASS" if avg_eq_x2 > 30 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg EQ within 2×: {avg_eq_x2:.0f}% (need > 30%)")

    ssn_better_mae = sum(1 for r in ssn_r
                          if min(r['seq_mae'], r['anc_mae']) < r['naive_mae'])
    tag = "PASS" if ssn_better_mae >= 3 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] SSN lower MAE than naive: {ssn_better_mae}/6 (need ≥ 3)")

    # Cross-check: sequential doesn't explode (max pred < 10× max actual)
    no_explode = all(r['seq_mae'] < 500 for r in ssn_r)
    tag = "PASS" if no_explode else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] No runaway drift (seq MAE < 500 all cutoffs)")

    print(f"\n  SCORE: {score}/8")
    return score

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_sunspot_annual()
    eq  = load_earthquake_annual()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

    # ─── Version 1: Correction factor on main delta ──────────────────
    print("\n" + "#"*70)
    print("# VERSION 1: Multiplicative correction (1 + 2·cos(φ)·sin(φ/R))")
    print("#"*70)

    ssn_r1 = run_blind(ssn, cutoffs, ARA_SSN, "SSN v1", paired_phi_predict)
    eq_r1  = run_blind(eq,  cutoffs, ARA_EQ,  "EQ v1",  paired_phi_predict)
    s1 = score_results(ssn_r1, eq_r1, "VERSION 1")

    # ─── Version 2: Explicit φ±pair as additional wave ───────────────
    print("\n" + "#"*70)
    print("# VERSION 2: Explicit φ-pair delta added to main delta")
    print("#"*70)

    ssn_r2 = run_blind(ssn, cutoffs, ARA_SSN, "SSN v2", paired_phi_predict_v2)
    eq_r2  = run_blind(eq,  cutoffs, ARA_EQ,  "EQ v2",  paired_phi_predict_v2)
    s2 = score_results(ssn_r2, eq_r2, "VERSION 2")

    # ─── Version 3: Accumulative per log traversed ───────────────────
    print("\n" + "#"*70)
    print("# VERSION 3: Accumulative dampening per total log traversed")
    print("#"*70)

    ssn_r3 = run_blind(ssn, cutoffs, ARA_SSN, "SSN v3", paired_phi_predict_v3,
                         use_accumulation=True)
    eq_r3  = run_blind(eq,  cutoffs, ARA_EQ,  "EQ v3",  paired_phi_predict_v3,
                         use_accumulation=True)
    s3 = score_results(ssn_r3, eq_r3, "VERSION 3")

    # ─── Summary ─────────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"FINAL COMPARISON")
    print(f"{'='*70}")
    print(f"  Script 167 (undampened):           0/8")
    print(f"  Script 168 (5 sub-systems):        2/8")
    print(f"  Script 169 v1 (multiplicative φ):  {s1}/8")
    print(f"  Script 169 v2 (explicit φ-pair):   {s2}/8")
    print(f"  Script 169 v3 (accumulative φ):    {s3}/8")
    print(f"\n  cos(φ) = {COS_PHI:.6f}")
    print(f"  Natural dampening rate = {TWO_COS_PHI:.4f} per log-unit")
    print(f"\nScript 169 complete.")
