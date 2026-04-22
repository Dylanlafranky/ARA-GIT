#!/usr/bin/env python3
"""
Script 172 — Log-Geared Inside-Outside Prediction
===================================================

Dylan's insight:
    "It's up an additional log, so we need to check how many logs it does,
     but only kick it up a gear when the wave reaches that point in the journey."

The outer wave (standard isosceles) only engages when the system has
traveled far enough in log-space from its mean.  Like gear shifts:

    Gear 1 (always):  φ-stable attractor (inner)
    Gear 2 (at 1 log): + 1× outer wave contribution
    Gear 3 (at 2 logs): + 2× outer wave contribution
    ...

The gear level = floor(|current_log - C|) or a continuous version.

Why this works:
    - EQ (range ~0.7 log): never leaves gear 1 → pure stability → 100% ×2
    - SSN (range ~2.5 log): shifts to gear 2-3 at peaks/troughs → gets
      the oscillation push it needs to turn around at extremes
    - Near the mean: just the attractor. Far from mean: attractor + rhythm.
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
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def phi_stable_delta(log_val, C, R_matter, step_years=1):
    """Inner: φ-averaged wave delta (stability)."""
    phi_pos = value_to_longitude(log_val, C, R_matter)
    phi_next = phi_pos + DPHI * step_years

    def avg_w(pos, R, offset):
        return (wave(pos + offset, R) + wave(pos - offset, R)) / 2

    c1_now  = avg_w(phi_pos, R_COUPLER, PHI)
    c1_next = avg_w(phi_next, R_COUPLER, PHI)
    c2_now  = avg_w(phi_pos + HALF_PHI, R_COUPLER, PHI)
    c2_next = avg_w(phi_next + HALF_PHI, R_COUPLER, PHI)

    return ((c1_next + c2_next)/2 - (c1_now + c2_now)/2) * np.exp(-MIDPOINT_OFFSET)

def standard_wave_delta(log_val, C, R_matter, step_years=1):
    """Outer: standard isosceles wave delta (rhythm)."""
    phi = value_to_longitude(log_val, C, R_matter)
    phi_next = phi + DPHI * step_years

    c1_now  = wave(phi, R_COUPLER)
    c2_now  = wave(phi + HALF_PHI, R_COUPLER)
    c1_next = wave(phi_next, R_COUPLER)
    c2_next = wave(phi_next + HALF_PHI, R_COUPLER)

    return ((c1_next + c2_next)/2 - (c1_now + c2_now)/2) * np.exp(-MIDPOINT_OFFSET)


# ─── Geared versions ────────────────────────────────────────────────

def geared_v1(log_val, C, R_matter, step_years=1):
    """
    V1: Discrete gears.
    gear = floor(|log_val - C|)
    At gear 0: only φ-stable
    At gear 1+: φ-stable + gear × outer_wave
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    distance = abs(log_val - C)
    gear = int(np.floor(distance))  # 0, 1, 2, ...

    if gear == 0:
        dlog = inner
    else:
        dlog = inner + gear * outer

    return log_val + dlog


def geared_v2(log_val, C, R_matter, step_years=1):
    """
    V2: Continuous gear — outer wave scales smoothly with log-distance.

    The outer wave contribution = |log_val - C| × outer_delta
    At distance 0: pure inner
    At distance 1: inner + 1× outer
    Smooth transition, no discrete jumps.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    distance = abs(log_val - C)
    dlog = inner + distance * outer

    return log_val + dlog


def geared_v3(log_val, C, R_matter, step_years=1):
    """
    V3: φ-thresholded gears.
    The gear threshold isn't at 1.0 log — it's at φ/2 (≈0.809).
    And each subsequent gear is another φ/2 away.

    gear = floor(distance / (φ/2))

    This ties the gear spacing to the same φ/2 that separates the couplers.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    distance = abs(log_val - C)
    gear = int(np.floor(distance / HALF_PHI))

    if gear == 0:
        dlog = inner
    else:
        dlog = inner + gear * outer

    return log_val + dlog


def geared_v4(log_val, C, R_matter, step_years=1):
    """
    V4: Smooth gear with φ/2 unit + golden damping.

    outer_weight = distance / (φ/2)
    But the outer contribution is damped by 1/φ per gear
    to prevent the old runaway problem.

    effective_outer = outer × (distance / (φ/2)) × (1/φ)^(distance/(φ/2))

    This peaks at some optimal distance and falls off — the wave pushes
    hardest at ~1 gear out, then the φ-damping takes over.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    distance = abs(log_val - C)
    gears = distance / HALF_PHI

    # Outer weight: ramps up linearly, but φ-damped
    outer_weight = gears * (1.0 / PHI) ** gears

    dlog = inner + outer_weight * outer

    return log_val + dlog


def geared_v5(log_val, C, R_matter, step_years=1):
    """
    V5: The V6 from Script 171 (best inner-outer so far) BUT with
    the outer wave gated by log-distance.

    V6 computed: dlog = standard_delta + (φ_stable_correction)
    Here: dlog = φ_stable_delta + gear_weight × (standard_delta - φ_stable_delta)

    When gear=0 (close to mean): pure φ-stable
    When gear=1+ (far from mean): blends toward standard wave

    Using continuous weighting capped at 1.0.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    distance = abs(log_val - C)
    # Blend factor: 0 at center, 1 at 1 log away, capped at 1
    blend = min(distance, 1.0)

    dlog = (1 - blend) * inner + blend * outer

    return log_val + dlog


def geared_v6(log_val, C, R_matter, step_years=1):
    """
    V6: Same as V5 but with φ/2 as the blend distance and
    the outer wave sign-aware — only engages when it OPPOSES
    the current direction from mean.

    If you're ABOVE the mean and outer wants to push you UP → ignore outer
    If you're ABOVE the mean and outer wants to push you DOWN → engage outer

    This is the "only kick it up a gear when the wave reaches that point"
    interpretation: the gear engages specifically when the wave is turning.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    distance = abs(log_val - C)
    direction_from_mean = np.sign(log_val - C)  # +1 if above, -1 if below

    # Blend based on distance
    blend = min(distance / HALF_PHI, 1.0)

    # Is the outer wave pushing us BACK toward the mean?
    outer_restoring = (np.sign(outer) != direction_from_mean) if direction_from_mean != 0 else True

    if outer_restoring:
        # Outer wave is helping — engage it proportional to distance
        dlog = (1 - blend) * inner + blend * outer
    else:
        # Outer wave would push us further out — stay on inner only
        dlog = inner

    return log_val + dlog


def geared_v7(log_val, C, R_matter, step_years=1):
    """
    V7: The gear engages at φ/2 distance, but the outer contribution
    is the V6-style (inner-longitude + outer-wave) from Script 171.

    Compute the V6 delta and the pure φ-stable delta.
    Gate the V6 component by log-distance.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)

    # Compute the V6-style delta (inner longitude, outer wave)
    phi_raw = value_to_longitude(log_val, C, R_matter)

    def avg_w(pos, R, offset):
        return (wave(pos + offset, R) + wave(pos - offset, R)) / 2

    stable_c1 = avg_w(phi_raw, R_COUPLER, PHI)
    stable_c2 = avg_w(phi_raw + HALF_PHI, R_COUPLER, PHI)
    stable_now = (stable_c1 + stable_c2) / 2

    phi_next = phi_raw + DPHI * step_years
    c1_next = wave(phi_next, R_COUPLER)
    c2_next = wave(phi_next + HALF_PHI, R_COUPLER)
    outer_next = (c1_next + c2_next) / 2

    c1_now = wave(phi_raw, R_COUPLER)
    c2_now = wave(phi_raw + HALF_PHI, R_COUPLER)
    standard_now = (c1_now + c2_now) / 2

    correction = stable_now - standard_now
    standard_delta = (outer_next - standard_now) * np.exp(-MIDPOINT_OFFSET)
    v6_delta = standard_delta + correction * np.exp(-MIDPOINT_OFFSET)

    # Gate by log-distance
    distance = abs(log_val - C)
    blend = min(distance / HALF_PHI, 1.0)

    dlog = (1 - blend) * inner + blend * v6_delta

    return log_val + dlog


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

# ─── Oscillation + Blind test ───────────────────────────────────────

def oscillation_test(predict_fn, label, C, R_matter=ARA_SSN, start_offset=0.5):
    log_val = C + start_offset
    prev_delta = 0
    turns = 0
    vals = []
    for yr in range(30):
        new_log = predict_fn(log_val, C, R_matter, step_years=1)
        delta = new_log - log_val
        if yr > 0 and np.sign(delta) != np.sign(prev_delta) and prev_delta != 0:
            turns += 1
        prev_delta = delta
        vals.append(10**log_val)
        log_val = new_log
    vmin, vmax = min(vals), max(vals)
    print(f"  {label}: turns={turns}/29, range=[{vmin:.1f}, {vmax:.1f}]")
    return turns

def run_blind(data, cutoffs, R_matter, predict_fn):
    results = []
    for cutoff in cutoffs:
        train = {y: v for y, v in data.items() if y < cutoff}
        test  = {y: v for y, v in data.items() if y >= cutoff}
        if len(train) < 10 or len(test) < 5:
            continue

        C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
        start_val = max(data[max(train.keys())], 0.1)
        test_years = sorted(test.keys())

        preds = []
        current = np.log10(start_val)
        for y in test_years:
            current = predict_fn(current, C, R_matter, step_years=1)
            preds.append(10**current)

        actuals = [data[y] for y in test_years]
        naive = start_val
        n = len(test_years)

        a, p = np.array(actuals), np.array(preds)
        c = float(np.corrcoef(a, p)[0,1]) if np.std(a)>0 and np.std(p)>0 and len(a)>2 else 0
        m = float(np.mean(np.abs(a - p)))
        nm = float(np.mean(np.abs(a - naive)))
        b = sum(1 for pi,ai in zip(preds,actuals) if abs(pi-ai)<abs(naive-ai))/n*100
        x2 = sum(1 for pi,ai in zip(preds,actuals) if 1/2<=max(pi,.1)/max(ai,.1)<=2)/n*100

        dm, dt = 0, 0
        for i in range(1,n):
            if np.sign(actuals[i]-actuals[i-1])!=0:
                dt+=1
                if np.sign(preds[i]-preds[i-1])==np.sign(actuals[i]-actuals[i-1]):
                    dm+=1
        d = dm/max(dt,1)*100

        results.append({
            'cutoff':cutoff,'corr':c,'beats':b,'x2':x2,'dir':d,
            'mae':m,'naive_mae':nm,
            'preds':preds[:12],'actuals':actuals[:12],
            'years':test_years[:12],'naive':naive
        })
    return results

def score_and_print(ssn_r, eq_r, label):
    s = 0
    print(f"\n  {label}:")

    # Print SSN trajectories for first and last cutoffs
    for r in [ssn_r[0], ssn_r[-1]]:
        print(f"    SSN cutoff {r['cutoff']}: corr={r['corr']:+.3f}, beats={r['beats']:.0f}%, "
              f"×2={r['x2']:.0f}%, dir={r['dir']:.0f}%, MAE={r['mae']:.1f} (naive={r['naive_mae']:.1f})")
        print(f"      {'Yr':>6} {'Act':>7} {'Pred':>7}")
        for i in range(min(8, len(r['years']))):
            print(f"      {r['years'][i]:>6} {r['actuals'][i]:>7.1f} {r['preds'][i]:>7.1f}")

    # Print EQ summary
    for r in [eq_r[0], eq_r[2]]:
        print(f"    EQ  cutoff {r['cutoff']}: corr={r['corr']:+.3f}, beats={r['beats']:.0f}%, "
              f"×2={r['x2']:.0f}%, MAE={r['mae']:.1f} (naive={r['naive_mae']:.1f})")
        print(f"      {'Yr':>6} {'Act':>7} {'Pred':>7}")
        for i in range(min(6, len(r['years']))):
            print(f"      {r['years'][i]:>6} {r['actuals'][i]:>7.1f} {r['preds'][i]:>7.1f}")

    checks = []

    ac = np.mean([r['corr'] for r in ssn_r])
    p = ac > 0.3; s += p
    checks.append(f"[{'PASS' if p else 'FAIL'}] SSN corr: {ac:.3f}")

    bn = sum(1 for r in ssn_r if r['beats']>50); p = bn>=3; s += p
    checks.append(f"[{'PASS' if p else 'FAIL'}] SSN beats naive: {bn}/6")

    ax = np.mean([r['x2'] for r in ssn_r]); p = ax>30; s += p
    checks.append(f"[{'PASS' if p else 'FAIL'}] SSN ×2: {ax:.0f}%")

    ad = np.mean([r['dir'] for r in ssn_r]); p = ad>55; s += p
    checks.append(f"[{'PASS' if p else 'FAIL'}] SSN dir: {ad:.0f}%")

    ec = np.mean([r['corr'] for r in eq_r]); p = ec>0.2; s += p
    checks.append(f"[{'PASS' if p else 'FAIL'}] EQ corr: {ec:.3f}")

    ex = np.mean([r['x2'] for r in eq_r]); p = ex>30; s += p
    checks.append(f"[{'PASS' if p else 'FAIL'}] EQ ×2: {ex:.0f}%")

    bm = sum(1 for r in ssn_r if r['mae']<r['naive_mae']); p = bm>=3; s += p
    checks.append(f"[{'PASS' if p else 'FAIL'}] SSN MAE<naive: {bm}/6")

    nb = all(r['mae']<500 for r in ssn_r); p = nb; s += p
    checks.append(f"[{'PASS' if p else 'FAIL'}] No drift")

    print(f"    " + " | ".join(checks))
    print(f"    SCORE: {s}/8")
    return s


# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_sunspot_annual()
    eq  = load_earthquake_annual()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]
    C_ssn = np.mean(np.log10([max(v, 0.1) for v in ssn.values()]))

    print("="*70)
    print("OSCILLATION DIAGNOSTIC (high start C+0.5, low start C-0.8)")
    print("="*70)

    versions = [
        ("V1: discrete gear (1 log)", geared_v1),
        ("V2: continuous gear", geared_v2),
        ("V3: φ/2 threshold gear", geared_v3),
        ("V4: φ-damped gear", geared_v4),
        ("V5: blend to outer", geared_v5),
        ("V6: restoring-only outer", geared_v6),
        ("V7: blend to V6-style", geared_v7),
    ]

    print(f"\n  Starting HIGH (C+0.5 = {C_ssn+0.5:.2f}, SSN≈{10**(C_ssn+0.5):.0f}):")
    for label, fn in versions:
        oscillation_test(fn, label, C_ssn, start_offset=0.5)

    print(f"\n  Starting LOW (C-0.8 = {C_ssn-0.8:.2f}, SSN≈{10**(C_ssn-0.8):.0f}):")
    for label, fn in versions:
        oscillation_test(fn, label, C_ssn, start_offset=-0.8)

    # Blind tests
    print(f"\n{'='*70}")
    print("BLIND TESTS — ALL VERSIONS")
    print("="*70)

    all_scores = {}
    for label, fn in versions:
        ssn_r = run_blind(ssn, cutoffs, ARA_SSN, fn)
        eq_r  = run_blind(eq,  cutoffs, ARA_EQ,  fn)
        s = score_and_print(ssn_r, eq_r, label)
        all_scores[label] = s

    # Grand comparison
    print(f"\n{'='*70}")
    print("GRAND COMPARISON")
    print("="*70)
    print(f"  Script 167 (undampened):              0/8")
    print(f"  Script 168 (5 sub-systems):           2/8")
    print(f"  Script 170 V4 (φ inside longitude):   6/8")
    print(f"  Script 171 V6 (inner-outer):          5/8  (EQ ×2=100%)")
    for label, s in all_scores.items():
        marker = ""
        if s > 6: marker = " ★ NEW BEST"
        elif s == 6: marker = " ← ties best"
        print(f"  Script 172 {label}: {s}/8{marker}")

    print(f"\nScript 172 complete.")
