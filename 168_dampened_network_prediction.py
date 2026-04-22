#!/usr/bin/env python3
"""
Script 168 — Dampened Network Prediction
=========================================

Hypothesis (Dylan):
The runaway drift in Script 167 happened because we only modelled the
MAIN triangle (2 couplers + matter).  In reality every coupler is itself
coupled to OTHER systems whose counter-waves should dampen the pump.

Structure
---------
Main triangle (from Script 166):
    Two couplers at ARA = 1.0, separated by φ/2 in longitude.
    Matter system at vertex (sunspots ARA=1.73, earthquakes ARA=0.15).

Sub-coupled network (NEW):
    Each coupler is part of its own ARA triple →
        2 sub-systems per coupler  = 4
    Time (also ARA=1.0) has 1 sub-system  = 1
                                    Total  = 5

    Each sub-system contributes a wave at HALF magnitude, INVERTED.
    This is the "return stroke" — the part that keeps the oscillator
    from pumping itself to infinity.

Sub-system ARA values:
    Following self-similarity, the sub-systems of a coupler at 1.0
    should bracket it the way matter brackets couplers.  The natural
    ARA positions for sub-couplers:
        - Sub-system A of each coupler: ARA = φ  (1.618 — engine side)
        - Sub-system B of each coupler: ARA = 1/φ (0.618 — consumer side)
    These are the golden complements of 1.0.
    - Time's sub-system: ARA = 1.354 (clock/accumulator — the tick)

Phase offsets for sub-systems:
    Self-similar to the main triangle: each sub-pair separated by φ/2
    from their parent coupler, but at the NEXT harmonic.

Dampening factor: -0.5 (half magnitude, inverted sign)

Test: Same blind out-of-sample protocol as Script 167.
"""

import numpy as np
import os

# ─── Constants ───────────────────────────────────────────────────────
PHI = (1 + np.sqrt(5)) / 2          # 1.6180339...
HALF_PHI = PHI / 2                   # 0.809
R_COUPLER = 1.0                      # ARA of couplers
HALE_PERIOD = 22                     # years
DPHI = 2 * np.pi / HALE_PERIOD      # radians per year

# Sub-system ARA values
SUB_ARA_ENGINE  = PHI                # 1.618
SUB_ARA_CONSUMER = 1.0 / PHI        # 0.618
SUB_ARA_CLOCK   = 1.354             # accumulator

# Dampening: sub-systems contribute at -0.5× magnitude
DAMP = -0.5

# Matter system ARA
ARA_SSN = 1.73
ARA_EQ  = 0.15

# Midpoint offset (from Script 166)
MIDPOINT_SSN = abs((ARA_SSN + ARA_EQ) / 2 - R_COUPLER)  # ~0.06
MIDPOINT_EQ  = MIDPOINT_SSN  # same geometric offset

# ─── Helper functions ────────────────────────────────────────────────

def value_to_longitude(log_val, C, R):
    """Map a log-value to longitude on the sphere."""
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    """Single wave contribution: R·sin(φ/R)."""
    return R * np.sin(phi_pos / R)

def main_triangle_prediction(phi_now, phi_next):
    """
    Main triangle: 2 couplers at ARA=1.0, separated by φ/2.
    Returns (avg_now, avg_next).
    """
    c1_now  = wave(phi_now, R_COUPLER)
    c2_now  = wave(phi_now + HALF_PHI, R_COUPLER)
    avg_now = (c1_now + c2_now) / 2

    c1_next  = wave(phi_next, R_COUPLER)
    c2_next  = wave(phi_next + HALF_PHI, R_COUPLER)
    avg_next = (c1_next + c2_next) / 2

    return avg_now, avg_next

def sub_network_contribution(phi_now, phi_next):
    """
    5 sub-coupled systems, each contributing DAMP × their wave delta.

    Coupler 1 subs (phase-locked to coupler 1 = phi_now):
        Sub A: ARA=φ,   phase = phi + φ/2  (golden offset from parent)
        Sub B: ARA=1/φ, phase = phi - φ/2  (mirror side)

    Coupler 2 subs (phase-locked to coupler 2 = phi_now + φ/2):
        Sub C: ARA=φ,   phase = (phi + φ/2) + φ/2
        Sub D: ARA=1/φ, phase = (phi + φ/2) - φ/2

    Time sub (phase = phi + π/φ — irrational offset from main):
        Sub E: ARA=1.354

    Each contributes: DAMP × (wave_next - wave_now)
    """
    total_delta = 0.0

    # Sub-systems of Coupler 1
    # Sub A: engine side
    phase_A_now  = phi_now + HALF_PHI
    phase_A_next = phi_next + HALF_PHI
    delta_A = wave(phase_A_next, SUB_ARA_ENGINE) - wave(phase_A_now, SUB_ARA_ENGINE)

    # Sub B: consumer side
    phase_B_now  = phi_now - HALF_PHI
    phase_B_next = phi_next - HALF_PHI
    delta_B = wave(phase_B_next, SUB_ARA_CONSUMER) - wave(phase_B_now, SUB_ARA_CONSUMER)

    # Sub-systems of Coupler 2
    c2_phase = HALF_PHI  # coupler 2 offset from coupler 1
    # Sub C: engine side
    phase_C_now  = phi_now + c2_phase + HALF_PHI
    phase_C_next = phi_next + c2_phase + HALF_PHI
    delta_C = wave(phase_C_next, SUB_ARA_ENGINE) - wave(phase_C_now, SUB_ARA_ENGINE)

    # Sub D: consumer side
    phase_D_now  = phi_now + c2_phase - HALF_PHI
    phase_D_next = phi_next + c2_phase - HALF_PHI
    delta_D = wave(phase_D_next, SUB_ARA_CONSUMER) - wave(phase_D_now, SUB_ARA_CONSUMER)

    # Sub-system of Time
    # Irrational offset: π/φ ≈ 1.942 (ensures no harmonic lock with main)
    time_offset = np.pi / PHI
    phase_E_now  = phi_now + time_offset
    phase_E_next = phi_next + time_offset
    delta_E = wave(phase_E_next, SUB_ARA_CLOCK) - wave(phase_E_now, SUB_ARA_CLOCK)

    total_delta = DAMP * (delta_A + delta_B + delta_C + delta_D + delta_E)
    return total_delta

def network_predict_next(current_log, C, R_matter, step_years=1):
    """
    Full network prediction: main triangle + dampened sub-network.
    """
    phi = value_to_longitude(current_log, C, R_matter)
    phi_next = phi + DPHI * step_years

    # Main triangle contribution
    avg_now, avg_next = main_triangle_prediction(phi, phi_next)
    main_delta = avg_next - avg_now

    # Sub-network dampening
    sub_delta = sub_network_contribution(phi, phi_next)

    # Combined
    dlog = (main_delta + sub_delta) * np.exp(-MIDPOINT_SSN)
    return current_log + dlog

# ─── Load data ───────────────────────────────────────────────────────

def load_sunspot_annual():
    """Load sunspot data, compute annual means."""
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
    """USGS M7+ annual counts (1900-2024)."""
    eq = {
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
    return eq

# ─── Blind test protocol ────────────────────────────────────────────

def run_blind_test(data_dict, cutoffs, R_matter, system_name, predict_fn):
    """Run out-of-sample blind test across multiple cutoffs."""
    all_years = sorted(data_dict.keys())

    print(f"\n{'='*70}")
    print(f"{system_name} BLIND PREDICTIONS (DAMPENED NETWORK)")
    print(f"{'='*70}")

    results_summary = []

    for cutoff in cutoffs:
        # Training data: everything before cutoff
        train = {y: v for y, v in data_dict.items() if y < cutoff}
        test  = {y: v for y, v in data_dict.items() if y >= cutoff}

        if len(train) < 10 or len(test) < 5:
            continue

        # Calibrate C from training data only
        train_vals = [max(v, 0.1) for v in train.values()]
        log_vals = np.log10(train_vals)
        C = np.mean(log_vals)

        # Start value: last known
        start_year = max(train.keys())
        start_val = max(data_dict[start_year], 0.1)

        test_years = sorted(test.keys())
        n_pred = len(test_years)

        # Sequential prediction (chain forward)
        seq_preds = []
        current_log = np.log10(start_val)
        for y in test_years:
            current_log = predict_fn(current_log, C, R_matter, step_years=1)
            seq_preds.append(10**current_log)

        # Anchored prediction (from last known each time)
        anc_preds = []
        for i, y in enumerate(test_years):
            steps = i + 1
            pred_log = np.log10(start_val)
            for s in range(steps):
                pred_log = predict_fn(pred_log, C, R_matter, step_years=1)
            anc_preds.append(10**pred_log)

        # Actual values
        actuals = [data_dict[y] for y in test_years]
        naive_val = start_val

        # --- Metrics ---
        def corr(a, b):
            if len(a) < 3:
                return 0
            a, b = np.array(a), np.array(b)
            if np.std(a) == 0 or np.std(b) == 0:
                return 0
            return float(np.corrcoef(a, b)[0, 1])

        def mae(a, b):
            return float(np.mean(np.abs(np.array(a) - np.array(b))))

        def beats_naive(preds, actuals, naive):
            wins = sum(1 for p, a in zip(preds, actuals)
                       if abs(p - a) < abs(naive - a))
            return wins / len(actuals) * 100

        def within_factor(preds, actuals, factor=2):
            hits = 0
            for p, a in zip(preds, actuals):
                if a == 0:
                    a = 0.1
                ratio = max(p, 0.1) / max(a, 0.1)
                if 1/factor <= ratio <= factor:
                    hits += 1
            return hits / len(actuals) * 100

        def direction_match(preds, actuals):
            if len(actuals) < 2:
                return 0
            matches = 0
            total = 0
            for i in range(1, len(actuals)):
                pred_dir = np.sign(preds[i] - preds[i-1])
                actual_dir = np.sign(actuals[i] - actuals[i-1])
                if actual_dir != 0:
                    total += 1
                    if pred_dir == actual_dir:
                        matches += 1
            return matches / max(total, 1) * 100

        seq_corr = corr(seq_preds, actuals)
        anc_corr = corr(anc_preds, actuals)
        seq_mae  = mae(seq_preds, actuals)
        anc_mae  = mae(anc_preds, actuals)
        naive_mae = mae([naive_val]*n_pred, actuals)
        seq_beats = beats_naive(seq_preds, actuals, naive_val)
        anc_beats = beats_naive(anc_preds, actuals, naive_val)
        seq_x2   = within_factor(seq_preds, actuals)
        anc_x2   = within_factor(anc_preds, actuals)
        seq_dir  = direction_match(seq_preds, actuals)
        anc_dir  = direction_match(anc_preds, actuals)

        print(f"\nCutoff {cutoff} → predict {n_pred} years ({cutoff}-{test_years[-1]})")
        print(f"  Start value: {start_val}")
        print(f"  Sequential: corr={seq_corr:+.3f}, MAE={seq_mae:.1f}, beats={seq_beats:.0f}%, dir={seq_dir:.0f}%, ×2={seq_x2:.0f}%")
        print(f"  Anchored:   corr={anc_corr:+.3f}, MAE={anc_mae:.1f}, beats={anc_beats:.0f}%, dir={anc_dir:.0f}%, ×2={anc_x2:.0f}%")
        print(f"  Naive:       MAE={naive_mae:.1f}")

        # Show first 8 years
        print(f"  {'Year':>6}  {'Actual':>8}  {'Seq_Pred':>8}  {'Anc_Pred':>8}  {'Naive':>6}")
        for i, y in enumerate(test_years[:8]):
            print(f"  {y:>6}  {actuals[i]:>8.1f}  {seq_preds[i]:>8.1f}  {anc_preds[i]:>8.1f}  {naive_val:>6.0f}")

        results_summary.append({
            'cutoff': cutoff,
            'seq_corr': seq_corr,
            'anc_corr': anc_corr,
            'seq_beats': seq_beats,
            'anc_beats': anc_beats,
            'seq_x2': seq_x2,
            'anc_x2': anc_x2,
            'seq_dir': seq_dir,
            'anc_dir': anc_dir,
            'seq_mae': seq_mae,
            'anc_mae': anc_mae,
            'naive_mae': naive_mae,
        })

    return results_summary

# ─── Diagnostic: show dampening effect ───────────────────────────────

def show_dampening_analysis():
    """Compare single-step predictions: undampened vs dampened."""
    print("\n" + "="*70)
    print("DAMPENING ANALYSIS — Single step Δlog comparison")
    print("="*70)

    # Test across a range of input log values
    test_logs = np.linspace(-0.5, 2.5, 20)
    C = 1.5  # typical SSN log mean

    print(f"\n  {'log_val':>8}  {'Undamped':>10}  {'Dampened':>10}  {'Ratio':>8}")
    print(f"  {'':>8}  {'Δlog':>10}  {'Δlog':>10}  {'D/U':>8}")

    for lv in test_logs:
        # Undampened (Script 167 style)
        phi = value_to_longitude(lv, C, ARA_SSN)
        phi_next = phi + DPHI
        avg_now_u, avg_next_u = main_triangle_prediction(phi, phi_next)
        dlog_undamped = (avg_next_u - avg_now_u) * np.exp(-MIDPOINT_SSN)

        # Dampened (this script)
        main_delta = avg_next_u - avg_now_u
        sub_delta = sub_network_contribution(phi, phi_next)
        dlog_dampened = (main_delta + sub_delta) * np.exp(-MIDPOINT_SSN)

        ratio = dlog_dampened / dlog_undamped if abs(dlog_undamped) > 1e-10 else float('nan')
        print(f"  {lv:>8.2f}  {dlog_undamped:>+10.6f}  {dlog_dampened:>+10.6f}  {ratio:>8.3f}")

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':

    ssn_data = load_sunspot_annual()
    eq_data  = load_earthquake_annual()

    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

    # Show dampening effect
    show_dampening_analysis()

    # Blind tests
    ssn_results = run_blind_test(ssn_data, cutoffs, ARA_SSN, "SUNSPOT",
                                  network_predict_next)
    eq_results  = run_blind_test(eq_data, cutoffs, ARA_EQ, "EARTHQUAKE",
                                  network_predict_next)

    # ─── Cross-scale test ────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("CROSS-SCALE BLIND TEST (DAMPENED)")
    print(f"{'='*70}")
    print("\nUse SSN model's temporal change to predict EQ direction\n")

    overlap_years = sorted(set(ssn_data.keys()) & set(eq_data.keys()))
    for cutoff in [2000, 2005, 2010]:
        train_ssn = {y: v for y, v in ssn_data.items() if y < cutoff}
        C_ssn = np.mean([np.log10(max(v, 0.1)) for v in train_ssn.values()])

        test_yrs = [y for y in overlap_years if y >= cutoff]
        if len(test_yrs) < 5:
            continue

        matches = 0
        anti = 0
        n = 0
        for i in range(1, len(test_yrs)):
            y0, y1 = test_yrs[i-1], test_yrs[i]
            if y1 - y0 != 1:
                continue

            ssn_log0 = np.log10(max(ssn_data[y0], 0.1))
            ssn_log1 = network_predict_next(ssn_log0, C_ssn, ARA_SSN, step_years=1)
            ssn_dir = np.sign(ssn_log1 - ssn_log0)

            eq_dir = np.sign(eq_data[y1] - eq_data[y0])
            if eq_dir == 0:
                continue
            n += 1
            if ssn_dir == eq_dir:
                matches += 1
            else:
                anti += 1

        pct = matches / max(n, 1) * 100
        anti_pct = anti / max(n, 1) * 100
        print(f"  Cutoff {cutoff}: SSN→EQ direction match = {pct:.1f}% (anti: {anti_pct:.1f}%, N={n})")

    # ─── Aggregate verdict ───────────────────────────────────────────
    print(f"\n{'='*70}")
    print("SCRIPT 168 AGGREGATE VERDICT")
    print(f"{'='*70}\n")

    score = 0
    total = 8

    # 1. Average SSN sequential correlation
    avg_ssn_seq = np.mean([r['seq_corr'] for r in ssn_results])
    tag = "PASS" if avg_ssn_seq > 0.3 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg SSN seq corr: {avg_ssn_seq:.3f} (need > 0.3)")

    # 2. Average SSN anchored correlation
    avg_ssn_anc = np.mean([r['anc_corr'] for r in ssn_results])
    tag = "PASS" if avg_ssn_anc > 0.3 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg SSN anch corr: {avg_ssn_anc:.3f} (need > 0.3)")

    # 3. SSN beats naive
    ssn_beats = sum(1 for r in ssn_results if r['anc_beats'] > 50)
    tag = "PASS" if ssn_beats >= 3 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] SSN beats naive in {ssn_beats}/6 cutoffs (need ≥ 3)")

    # 4. SSN within 2×
    avg_ssn_x2 = np.mean([r['anc_x2'] for r in ssn_results])
    tag = "PASS" if avg_ssn_x2 > 30 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg SSN within 2×: {avg_ssn_x2:.0f}% (need > 30%)")

    # 5. EQ sequential correlation
    avg_eq_seq = np.mean([r['seq_corr'] for r in eq_results])
    tag = "PASS" if avg_eq_seq > 0.2 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg EQ seq corr: {avg_eq_seq:.3f} (need > 0.2)")

    # 6. EQ within 2×
    avg_eq_x2 = np.mean([r['anc_x2'] for r in eq_results])
    tag = "PASS" if avg_eq_x2 > 30 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg EQ within 2×: {avg_eq_x2:.0f}% (need > 30%)")

    # 7. Average direction accuracy
    avg_dir = np.mean([r['anc_dir'] for r in ssn_results])
    tag = "PASS" if avg_dir > 55 else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Avg SSN direction: {avg_dir:.0f}% (need > 55%)")

    # 8. Any cutoff where BOTH systems beat naive
    both_beat = any(
        ssn_results[i]['anc_beats'] > 50 and eq_results[i]['anc_beats'] > 50
        for i in range(min(len(ssn_results), len(eq_results)))
    )
    tag = "PASS" if both_beat else "FAIL"
    if tag == "PASS": score += 1
    print(f"  [{tag}] Any cutoff where both beat naive")

    print(f"\n  SCORE: {score}/{total}")

    # ─── Comparison with Script 167 ──────────────────────────────────
    print(f"\n{'='*70}")
    print("COMPARISON: Script 167 (undampened) vs 168 (dampened)")
    print(f"{'='*70}")
    print(f"""
  Script 167 scores: 0/8
  Script 168 scores: {score}/8

  Key question: Does the sub-network dampening reduce the runaway drift?
  Check the Dampening Analysis table above — if Ratio is between 0 and 1,
  the sub-network is pulling predictions back toward zero (good).
  If Ratio is > 1 or < 0, the sub-network is amplifying or reversing (bad).
    """)

    # ─── Max prediction value diagnostic ─────────────────────────────
    print("MAX PREDICTION VALUES (sequential, first 10 years):")
    for r in ssn_results[:3]:
        print(f"  SSN cutoff {r['cutoff']}: seq MAE = {r['seq_mae']:.1f}")
    for r in eq_results[:3]:
        print(f"  EQ  cutoff {r['cutoff']}: seq MAE = {r['seq_mae']:.1f}")

    print("\nScript 168 complete.")
