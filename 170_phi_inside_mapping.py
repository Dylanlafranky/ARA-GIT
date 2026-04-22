#!/usr/bin/env python3
"""
Script 170 — φ Inside the Mapping: Two-Future Averaging
=========================================================

Dylan's insight:
    "the system sees TWO possible futures — one φ ahead and one φ behind —
     and the actual step is the average of those two futures"

    "we'd have to abuse BODMAS... map the wave INTO the formula"

The key move: φ enters INSIDE the value→longitude mapping, not as a
post-hoc correction.  At each prediction step:

    1. Take current log-value L
    2. Compute prediction from (L + φ)  — the view from φ above
    3. Compute prediction from (L - φ)  — the view from φ below
    4. Actual prediction = average of these two views

WHY THIS OSCILLATES:
    value_to_longitude uses arcsin, which clips at ±1.
    - When L is HIGH: (L+φ) hits ceiling, (L-φ) sees center → average pulls DOWN
    - When L is LOW:  (L-φ) hits floor,  (L+φ) sees center → average pulls UP
    - When L is MIDDLE: both views symmetric → average ≈ standard prediction

    The restoring force emerges from the geometry.
    φ sets the window width.  arcsin provides the nonlinear rails.
    The wave is inside the formula.
"""

import numpy as np
import os

# ─── Constants ───────────────────────────────────────────────────────
PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
DPHI = 2 * np.pi / HALE_PERIOD

ARA_SSN = 1.73
ARA_EQ  = 0.15
MIDPOINT_OFFSET = abs((ARA_SSN + ARA_EQ) / 2 - R_COUPLER)

# ─── Core functions ──────────────────────────────────────────────────

def value_to_longitude(log_val, C, R):
    """Map log-value to longitude. arcsin clips at ±1 → nonlinear rails."""
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def standard_predict(log_val, C, R_matter, step_years=1):
    """Standard isosceles prediction (Script 166 style, no φ-inside)."""
    phi = value_to_longitude(log_val, C, R_matter)
    phi_next = phi + DPHI * step_years

    c1_now  = wave(phi, R_COUPLER)
    c2_now  = wave(phi + HALF_PHI, R_COUPLER)
    c1_next = wave(phi_next, R_COUPLER)
    c2_next = wave(phi_next + HALF_PHI, R_COUPLER)

    dlog = ((c1_next + c2_next)/2 - (c1_now + c2_now)/2)
    dlog *= np.exp(-MIDPOINT_OFFSET)
    return log_val + dlog


def phi_inside_predict(log_val, C, R_matter, step_years=1):
    """
    TWO-FUTURE AVERAGING: φ inside the mapping.

    Instead of predicting from L, predict from (L+φ) and (L-φ),
    then average the TWO PREDICTED VALUES (not the deltas).
    """
    # View from φ above
    pred_plus = standard_predict(log_val + PHI, C, R_matter, step_years)

    # View from φ below
    pred_minus = standard_predict(log_val - PHI, C, R_matter, step_years)

    # The truth is the average of both futures
    return (pred_plus + pred_minus) / 2


def phi_inside_predict_v2(log_val, C, R_matter, step_years=1):
    """
    Version 2: Average the DELTAS, not the absolute predictions.

    Compute Δlog from (L+φ) viewpoint and Δlog from (L-φ) viewpoint.
    Apply the averaged delta to the ACTUAL current position.
    """
    # Delta from the +φ viewpoint
    pred_plus = standard_predict(log_val + PHI, C, R_matter, step_years)
    delta_plus = pred_plus - (log_val + PHI)

    # Delta from the -φ viewpoint
    pred_minus = standard_predict(log_val - PHI, C, R_matter, step_years)
    delta_minus = pred_minus - (log_val - PHI)

    # Average delta, applied to actual position
    avg_delta = (delta_plus + delta_minus) / 2
    return log_val + avg_delta


def phi_inside_predict_v3(log_val, C, R_matter, step_years=1):
    """
    Version 3: HALF-φ window (φ/2 matching the isosceles separation).

    Same logic but the window is φ/2 instead of full φ.
    Tighter window → more local → less extreme clipping → subtler oscillation.
    """
    pred_plus = standard_predict(log_val + HALF_PHI, C, R_matter, step_years)
    pred_minus = standard_predict(log_val - HALF_PHI, C, R_matter, step_years)
    return (pred_plus + pred_minus) / 2


def phi_inside_predict_v4(log_val, C, R_matter, step_years=1):
    """
    Version 4: φ enters the LONGITUDE directly, not the log-value.

    Instead of offsetting the input value by ±φ in log-space,
    offset the longitude by ±φ after mapping:

    1. Map L → φ_pos
    2. Compute wave at (φ_pos + φ) and (φ_pos - φ)
    3. Average those two wave values for both couplers
    4. Step forward and do the same
    5. Δlog = avg_next - avg_now

    This is the deepest BODMAS abuse: φ goes inside the sin() argument.
    """
    phi_pos = value_to_longitude(log_val, C, R_matter)
    phi_next = phi_pos + DPHI * step_years

    # Current: average of ±φ views for each coupler
    def avg_wave_at(pos, R, offset):
        return (wave(pos + offset, R) + wave(pos - offset, R)) / 2

    # Coupler 1 at current and next
    c1_now  = avg_wave_at(phi_pos, R_COUPLER, PHI)
    c1_next = avg_wave_at(phi_next, R_COUPLER, PHI)

    # Coupler 2 (offset by φ/2) at current and next
    c2_now  = avg_wave_at(phi_pos + HALF_PHI, R_COUPLER, PHI)
    c2_next = avg_wave_at(phi_next + HALF_PHI, R_COUPLER, PHI)

    avg_now  = (c1_now + c2_now) / 2
    avg_next = (c1_next + c2_next) / 2

    dlog = (avg_next - avg_now) * np.exp(-MIDPOINT_OFFSET)
    return log_val + dlog


def phi_inside_predict_v5(log_val, C, R_matter, step_years=1):
    """
    Version 5: THREE views — current, +φ, and -φ — weighted by
    the golden ratio itself.

    current has weight 1, each φ-view has weight 1/φ.
    Total weight = 1 + 2/φ = 1 + 2×0.618 = 2.236 ≈ √5

    This is the ARA weighting: the center (the system itself) matters
    most, the two φ-futures contribute proportionally to their distance.
    """
    w_center = 1.0
    w_phi = 1.0 / PHI  # 0.618

    pred_center = standard_predict(log_val, C, R_matter, step_years)
    pred_plus   = standard_predict(log_val + PHI, C, R_matter, step_years)
    pred_minus  = standard_predict(log_val - PHI, C, R_matter, step_years)

    total_weight = w_center + 2 * w_phi  # = √5
    weighted = (w_center * pred_center + w_phi * pred_plus + w_phi * pred_minus)
    return weighted / total_weight


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

# ─── Oscillation diagnostic ─────────────────────────────────────────

def oscillation_test(predict_fn, label, C=1.5, R_matter=ARA_SSN):
    """
    Start from a high value and step forward 30 years.
    Does the prediction oscillate or monotonically drift?
    """
    print(f"\n  {label}:")
    print(f"  {'Year':>6} {'LogVal':>8} {'Value':>10} {'Delta':>8} {'Dir':>4}")

    log_val = C + 0.5  # Start high
    prev_delta = 0
    turns = 0
    for yr in range(30):
        new_log = predict_fn(log_val, C, R_matter, step_years=1)
        delta = new_log - log_val
        direction = "↑" if delta > 0 else "↓" if delta < 0 else "="
        if yr > 0 and np.sign(delta) != np.sign(prev_delta) and prev_delta != 0:
            turns += 1
            direction += " ⟲"
        if yr < 15 or yr >= 28:
            print(f"  {yr:>6} {log_val:>8.4f} {10**log_val:>10.1f} {delta:>+8.5f} {direction:>4}")
        elif yr == 15:
            print(f"  {'...':>6}")
        prev_delta = delta
        log_val = new_log

    print(f"  Direction changes (turns): {turns}/29")
    return turns


# ─── Blind test ──────────────────────────────────────────────────────

def run_blind(data, cutoffs, R_matter, name, predict_fn):
    print(f"\n{'='*70}")
    print(f"{name}")
    print(f"{'='*70}")

    results = []
    for cutoff in cutoffs:
        train = {y: v for y, v in data.items() if y < cutoff}
        test  = {y: v for y, v in data.items() if y >= cutoff}
        if len(train) < 10 or len(test) < 5:
            continue

        C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
        start_year = max(train.keys())
        start_val = max(data[start_year], 0.1)
        test_years = sorted(test.keys())

        # Sequential
        seq_preds = []
        current_log = np.log10(start_val)
        for y in test_years:
            current_log = predict_fn(current_log, C, R_matter, step_years=1)
            seq_preds.append(10**current_log)

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

        def beats(preds, acts, naive):
            return sum(1 for p, a in zip(preds, acts)
                       if abs(p - a) < abs(naive - a)) / len(acts) * 100

        def within_x(preds, acts, f=2):
            return sum(1 for p, a in zip(preds, acts)
                       if 1/f <= max(p,0.1)/max(a,0.1) <= f) / len(acts) * 100

        def direction(preds, acts):
            m, t = 0, 0
            for i in range(1, len(acts)):
                if np.sign(acts[i] - acts[i-1]) != 0:
                    t += 1
                    if np.sign(preds[i] - preds[i-1]) == np.sign(acts[i] - acts[i-1]):
                        m += 1
            return m / max(t, 1) * 100

        sc = corr(seq_preds, actuals)
        sb = beats(seq_preds, actuals, naive_val)
        sx = within_x(seq_preds, actuals)
        sd = direction(seq_preds, actuals)
        sm = mae(seq_preds, actuals)
        nm = mae([naive_val]*n, actuals)

        print(f"\n  Cutoff {cutoff} → {n}yr: corr={sc:+.3f}, MAE={sm:.1f}, "
              f"beats={sb:.0f}%, dir={sd:.0f}%, ×2={sx:.0f}% (naive MAE={nm:.1f})")

        # Show trajectory
        print(f"    {'Year':>6} {'Actual':>8} {'Pred':>8} {'Naive':>6}")
        for i, y in enumerate(test_years[:12]):
            print(f"    {y:>6} {actuals[i]:>8.1f} {seq_preds[i]:>8.1f} {naive_val:>6.0f}")
        if n > 12:
            print(f"    {'...':>6}")

        results.append({
            'cutoff': cutoff, 'corr': sc, 'beats': sb, 'x2': sx,
            'dir': sd, 'mae': sm, 'naive_mae': nm,
        })

    return results


def score(ssn_r, eq_r, label):
    print(f"\n{'='*70}")
    print(f"  {label} VERDICT")
    print(f"{'='*70}\n")

    s = 0

    avg_corr = np.mean([r['corr'] for r in ssn_r])
    p = "PASS" if avg_corr > 0.3 else "FAIL"
    if p == "PASS": s += 1
    print(f"  [{p}] SSN avg corr: {avg_corr:.3f} (> 0.3)")

    bn = sum(1 for r in ssn_r if r['beats'] > 50)
    p = "PASS" if bn >= 3 else "FAIL"
    if p == "PASS": s += 1
    print(f"  [{p}] SSN beats naive: {bn}/6 (≥ 3)")

    ax = np.mean([r['x2'] for r in ssn_r])
    p = "PASS" if ax > 30 else "FAIL"
    if p == "PASS": s += 1
    print(f"  [{p}] SSN within 2×: {ax:.0f}% (> 30%)")

    ad = np.mean([r['dir'] for r in ssn_r])
    p = "PASS" if ad > 55 else "FAIL"
    if p == "PASS": s += 1
    print(f"  [{p}] SSN direction: {ad:.0f}% (> 55%)")

    eq_corr = np.mean([r['corr'] for r in eq_r])
    p = "PASS" if eq_corr > 0.2 else "FAIL"
    if p == "PASS": s += 1
    print(f"  [{p}] EQ avg corr: {eq_corr:.3f} (> 0.2)")

    eq_x = np.mean([r['x2'] for r in eq_r])
    p = "PASS" if eq_x > 30 else "FAIL"
    if p == "PASS": s += 1
    print(f"  [{p}] EQ within 2×: {eq_x:.0f}% (> 30%)")

    bm = sum(1 for r in ssn_r if r['mae'] < r['naive_mae'])
    p = "PASS" if bm >= 3 else "FAIL"
    if p == "PASS": s += 1
    print(f"  [{p}] SSN lower MAE: {bm}/6 (≥ 3)")

    no_blow = all(r['mae'] < 500 for r in ssn_r)
    p = "PASS" if no_blow else "FAIL"
    if p == "PASS": s += 1
    print(f"  [{p}] No drift (MAE < 500)")

    # Bonus: oscillation
    turns_ssn = sum(1 for i in range(1, len(ssn_r))
                     if np.sign(ssn_r[i]['corr']) != np.sign(ssn_r[i-1]['corr']))
    print(f"\n  SCORE: {s}/8")
    return s


# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_sunspot_annual()
    eq  = load_earthquake_annual()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

    # ─── Oscillation diagnostic ──────────────────────────────────────
    print("="*70)
    print("OSCILLATION DIAGNOSTIC — Starting high, 30 year trajectory")
    print("="*70)

    C_test = np.mean(np.log10([max(v, 0.1) for v in ssn.values()]))
    print(f"\n  C (mean log SSN) = {C_test:.4f}")
    print(f"  Start: C+0.5 = {C_test+0.5:.4f} → SSN ≈ {10**(C_test+0.5):.0f}")

    oscillation_test(standard_predict, "Standard (no φ-inside)", C_test)
    t1 = oscillation_test(phi_inside_predict, "V1: Average predicted values (±φ in log)", C_test)
    t2 = oscillation_test(phi_inside_predict_v2, "V2: Average deltas (±φ in log)", C_test)
    t3 = oscillation_test(phi_inside_predict_v3, "V3: Half-φ window (±φ/2 in log)", C_test)
    t4 = oscillation_test(phi_inside_predict_v4, "V4: ±φ inside longitude (deepest BODMAS)", C_test)
    t5 = oscillation_test(phi_inside_predict_v5, "V5: Three views, golden-weighted", C_test)

    print(f"\n  Turn summary: V1={t1}, V2={t2}, V3={t3}, V4={t4}, V5={t5}")
    print(f"  (More turns = better oscillation, max 29)")

    # ─── Also test starting LOW ──────────────────────────────────────
    print(f"\n{'='*70}")
    print("OSCILLATION DIAGNOSTIC — Starting LOW, 30 year trajectory")
    print(f"{'='*70}")
    print(f"\n  Start: C-0.8 = {C_test-0.8:.4f} → SSN ≈ {10**(C_test-0.8):.0f}")

    def osc_low(predict_fn, label):
        print(f"\n  {label}:")
        log_val = C_test - 0.8
        prev_delta = 0
        turns = 0
        for yr in range(30):
            new_log = predict_fn(log_val, C_test, ARA_SSN, step_years=1)
            delta = new_log - log_val
            direction = "↑" if delta > 0 else "↓"
            if yr > 0 and np.sign(delta) != np.sign(prev_delta) and prev_delta != 0:
                turns += 1
                direction += " ⟲"
            if yr < 10:
                print(f"    {yr:>3} {10**log_val:>8.1f} → {10**new_log:>8.1f}  Δ={delta:>+.5f} {direction}")
            prev_delta = delta
            log_val = new_log
        print(f"    Turns: {turns}/29")
        return turns

    osc_low(standard_predict, "Standard")
    osc_low(phi_inside_predict, "V1: ±φ in log, avg values")
    osc_low(phi_inside_predict_v5, "V5: Three views, golden-weighted")

    # ─── Blind tests for best oscillators ────────────────────────────
    versions = [
        ("V1: Avg predicted values (±φ)", phi_inside_predict),
        ("V2: Avg deltas (±φ)", phi_inside_predict_v2),
        ("V3: Half-φ window (±φ/2)", phi_inside_predict_v3),
        ("V4: φ inside longitude", phi_inside_predict_v4),
        ("V5: Three views golden-weighted", phi_inside_predict_v5),
    ]

    all_scores = {}
    for label, fn in versions:
        print(f"\n{'#'*70}")
        print(f"# {label}")
        print(f"{'#'*70}")

        ssn_r = run_blind(ssn, cutoffs, ARA_SSN, f"SSN — {label}", fn)
        eq_r  = run_blind(eq,  cutoffs, ARA_EQ,  f"EQ — {label}",  fn)
        s = score(ssn_r, eq_r, label)
        all_scores[label] = s

    # ─── Final comparison ────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("FINAL COMPARISON — ALL SCRIPTS")
    print(f"{'='*70}")
    print(f"  Script 167 (undampened):              0/8")
    print(f"  Script 168 (5 sub-systems):           2/8")
    print(f"  Script 169 (paired φ corrections):    1/8")
    for label, s in all_scores.items():
        print(f"  Script 170 {label}: {s}/8")

    print(f"\nScript 170 complete.")
