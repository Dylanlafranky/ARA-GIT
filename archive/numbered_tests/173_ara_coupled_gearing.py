#!/usr/bin/env python3
"""
Script 173 — ARA-Coupled Asymmetric Gearing
=============================================

Dylan's insight:
    "we have that ARA plus an inverted ARA value... try and get the ARA
     values linked so they couple together and change in relation"

The ARA value itself sets the gear ratio, and it's ASYMMETRIC:

    ABOVE mean (coming down):  gear ratio = ARA value
        SSN at 1.73 (discharge) → aggressive downshift, snaps back fast
        EQ at 0.15 (consumer)   → very gentle, barely moves

    BELOW mean (going up):     gear ratio = inverted ARA
        Several inversions to test:
        - Mirror: 2 - ARA    (SSN → 0.27, EQ → 1.85)
        - Reciprocal: 1/ARA  (SSN → 0.578, EQ → 6.67)
        - Complement: ARA on the other side of 1.0

    The two ARA values couple: the system oscillates between its
    ARA character (how it discharges/accumulates) and its mirror.

Combined with the inside-outside structure:
    INNER: φ-stable (always on)
    OUTER: standard wave, gated by distance from mean
    GEAR RATIO: ARA-dependent, asymmetric above/below mean
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

# Inverted ARA values
def ara_mirror(ara):
    """2 - ARA: mirror across 1.0 on the 0-2 scale."""
    return 2.0 - ara

def ara_reciprocal(ara):
    """1/ARA: golden-style inversion."""
    return 1.0 / ara

def ara_complement(ara):
    """Distance from 1.0, flipped: 1 + (1 - ARA) = 2 - ARA (same as mirror)."""
    return 2.0 - ara

print(f"SSN ARA = {ARA_SSN:.3f}")
print(f"  Mirror (2-ARA):     {ara_mirror(ARA_SSN):.3f}")
print(f"  Reciprocal (1/ARA): {ara_reciprocal(ARA_SSN):.3f}")
print(f"  φ-inverse (φ/ARA):  {PHI/ARA_SSN:.3f}")
print(f"EQ  ARA = {ARA_EQ:.3f}")
print(f"  Mirror (2-ARA):     {ara_mirror(ARA_EQ):.3f}")
print(f"  Reciprocal (1/ARA): {ara_reciprocal(ARA_EQ):.3f}")
print(f"  φ-inverse (φ/ARA):  {PHI/ARA_EQ:.3f}")

# ─── Core wave functions ─────────────────────────────────────────────

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def phi_stable_delta(log_val, C, R_matter, step_years=1):
    """Inner: φ-averaged wave delta."""
    phi_pos = value_to_longitude(log_val, C, R_matter)
    phi_next = phi_pos + DPHI * step_years
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi_pos, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi_pos+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    return ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

def standard_wave_delta(log_val, C, R_matter, step_years=1):
    """Outer: standard isosceles wave delta."""
    phi = value_to_longitude(log_val, C, R_matter)
    phi_next = phi + DPHI * step_years
    c1n = wave(phi, R_COUPLER)
    c2n = wave(phi+HALF_PHI, R_COUPLER)
    c1x = wave(phi_next, R_COUPLER)
    c2x = wave(phi_next+HALF_PHI, R_COUPLER)
    return ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)


# ─── ARA-coupled geared versions ────────────────────────────────────

def ara_geared_v1(log_val, C, R_matter, step_years=1):
    """
    V1: ARA as gear ratio, mirror-inverted below mean.

    Above mean: outer_weight = ARA × distance
        SSN: 1.73 × dist → aggressive engage → fast snap down
    Below mean: outer_weight = (2-ARA) × distance
        SSN: 0.27 × dist → gentle engage → slow climb up

    Both couple: the system oscillates between ARA character
    and its mirror.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    ara = R_matter  # ARA value of the system
    distance = abs(log_val - C)

    if log_val >= C:
        # Above mean: use ARA (discharge character)
        gear = ara * distance
    else:
        # Below mean: use mirror ARA (accumulation character)
        gear = ara_mirror(ara) * distance

    dlog = inner + gear * outer
    return log_val + dlog


def ara_geared_v2(log_val, C, R_matter, step_years=1):
    """
    V2: Reciprocal inversion (1/ARA) below mean.

    Above: ARA × distance    (SSN: 1.73×d)
    Below: (1/ARA) × distance (SSN: 0.578×d)

    The reciprocal preserves the multiplicative structure:
    ARA × (1/ARA) = 1, so the product of both gear ratios = 1.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    ara = R_matter
    distance = abs(log_val - C)

    if log_val >= C:
        gear = ara * distance
    else:
        gear = (1.0 / ara) * distance

    dlog = inner + gear * outer
    return log_val + dlog


def ara_geared_v3(log_val, C, R_matter, step_years=1):
    """
    V3: Continuous ARA coupling — the gear ratio BLENDS between
    ARA and inverted-ARA based on position.

    At the mean: gear_ara = 1.0 (neutral)
    Above mean: gear → ARA (discharge)
    Below mean: gear → 2-ARA (accumulation)

    gear_ratio = 1.0 + (log_val - C) × (ARA - 1.0) / R_matter

    This makes the ARA coupling continuous, not a switch.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    ara = R_matter
    distance = abs(log_val - C)
    signed_distance = (log_val - C)

    # Continuous gear ratio
    # At C: gear_ratio = 1.0
    # At C+1: gear_ratio = ARA
    # At C-1: gear_ratio = 2-ARA
    gear_ratio = 1.0 + signed_distance * (ara - 1.0)
    gear_ratio = max(gear_ratio, 0.01)  # prevent negative

    dlog = inner + gear_ratio * distance * outer
    return log_val + dlog


def ara_geared_v4(log_val, C, R_matter, step_years=1):
    """
    V4: The ARA value determines the φ/2 gear threshold.

    Above mean: gear engages at distance = φ/2 / ARA
        SSN: φ/2 / 1.73 = 0.468 → kicks in SOONER (discharge snaps)
    Below mean: gear engages at distance = φ/2 × (2-ARA)
        SSN: φ/2 × 0.27 = 0.218 → actually kicks in even sooner!

    Wait — the accumulation side should be SLOWER to engage.
    Below mean: gear engages at distance = φ/2 × ARA
        SSN: φ/2 × 1.73 = 1.40 → very late engagement (slow climb)

    The threshold IS the ARA-coupling.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    ara = R_matter
    distance = abs(log_val - C)

    if log_val >= C:
        # Above mean: threshold lowered by ARA → engages sooner
        threshold = HALF_PHI / ara
        gear = max(0, (distance - threshold)) / HALF_PHI if distance > threshold else 0
    else:
        # Below mean: threshold raised by ARA → engages later
        threshold = HALF_PHI * ara
        gear = max(0, (distance - threshold)) / HALF_PHI if distance > threshold else 0

    dlog = inner + gear * outer
    return log_val + dlog


def ara_geared_v5(log_val, C, R_matter, step_years=1):
    """
    V5: Both ARA values present simultaneously and OSCILLATING.

    The outer wave is split into two components:
        Component A: weighted by ARA     (discharge character)
        Component B: weighted by 2-ARA   (accumulation character)

    Their PHASE is different:
        A is at the current position
        B is at the current position + φ/2 (half-cycle offset)

    The total outer = A_weight × outer_at_pos + B_weight × outer_at_pos+φ/2

    The two ARA values create a BEAT FREQUENCY between them.
    """
    phi = value_to_longitude(log_val, C, R_matter)
    phi_next = phi + DPHI * step_years

    inner = phi_stable_delta(log_val, C, R_matter, step_years)

    ara = R_matter
    inv_ara = 2.0 - ara

    distance = abs(log_val - C)

    # Component A: discharge character at current phase
    c1n_a = wave(phi, R_COUPLER)
    c2n_a = wave(phi + HALF_PHI, R_COUPLER)
    c1x_a = wave(phi_next, R_COUPLER)
    c2x_a = wave(phi_next + HALF_PHI, R_COUPLER)
    delta_a = ((c1x_a + c2x_a)/2 - (c1n_a + c2n_a)/2) * np.exp(-MIDPOINT_OFFSET)

    # Component B: accumulation character at φ/2 offset phase
    c1n_b = wave(phi + HALF_PHI, R_COUPLER)
    c2n_b = wave(phi + 2*HALF_PHI, R_COUPLER)
    c1x_b = wave(phi_next + HALF_PHI, R_COUPLER)
    c2x_b = wave(phi_next + 2*HALF_PHI, R_COUPLER)
    delta_b = ((c1x_b + c2x_b)/2 - (c1n_b + c2n_b)/2) * np.exp(-MIDPOINT_OFFSET)

    # Weighted combination
    outer = (ara * delta_a + inv_ara * delta_b) / (ara + inv_ara)

    dlog = inner + distance * outer
    return log_val + dlog


def ara_geared_v6(log_val, C, R_matter, step_years=1):
    """
    V6: Simplest coupling — the R_matter in the longitude mapping
    SWITCHES between ARA and inverted ARA based on direction.

    When above mean: map longitude using R = ARA (wide mapping → fast return)
    When below mean: map longitude using R = 2-ARA (narrow mapping → slow climb)

    The outer wave uses whichever R is active.
    The inner φ-stable always uses the original R.

    This makes the wave SHAPE change based on position — wider swings
    coming down, tighter swings going up.
    """
    ara = R_matter
    inv_ara = max(2.0 - ara, 0.1)

    inner = phi_stable_delta(log_val, C, R_matter, step_years)

    # Choose R for outer wave based on position
    if log_val >= C:
        R_active = ara
    else:
        R_active = inv_ara

    outer = standard_wave_delta(log_val, C, R_active, step_years)
    distance = abs(log_val - C)

    # Gear engages at φ/2 distance
    blend = min(distance / HALF_PHI, 1.0)

    dlog = (1 - blend) * inner + blend * outer
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
                if ssn < 0: continue
                monthly.setdefault(year, []).append(ssn)
            except ValueError: continue
    return {y: np.mean(v) for y, v in monthly.items() if len(v) >= 6}

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

# ─── Test harness ────────────────────────────────────────────────────

def oscillation_test(fn, label, C, R=ARA_SSN, offsets=[0.5, -0.8]):
    results = []
    for off in offsets:
        log_val = C + off
        prev_d = 0; turns = 0; vals = []
        for yr in range(30):
            new = fn(log_val, C, R, 1)
            d = new - log_val
            if yr > 0 and np.sign(d) != np.sign(prev_d) and prev_d != 0:
                turns += 1
            prev_d = d; vals.append(10**log_val); log_val = new
        results.append((turns, min(vals), max(vals)))
    hi, lo = results
    print(f"  {label}: high_turns={hi[0]}, low_turns={lo[0]}, "
          f"hi_range=[{hi[1]:.0f},{hi[2]:.0f}], lo_range=[{lo[1]:.0f},{lo[2]:.0f}]")
    return hi[0] + lo[0]

def run_blind(data, cutoffs, R_matter, fn):
    results = []
    for cutoff in cutoffs:
        train = {y:v for y,v in data.items() if y < cutoff}
        test  = {y:v for y,v in data.items() if y >= cutoff}
        if len(train)<10 or len(test)<5: continue
        C = np.mean(np.log10([max(v,.1) for v in train.values()]))
        sv = max(data[max(train.keys())],.1)
        ty = sorted(test.keys())
        preds = []; cur = np.log10(sv)
        for y in ty:
            cur = fn(cur, C, R_matter, 1)
            preds.append(10**cur)
        act = [data[y] for y in ty]; n = len(ty); nv = sv
        a,p = np.array(act), np.array(preds)
        c = float(np.corrcoef(a,p)[0,1]) if np.std(a)>0 and np.std(p)>0 and len(a)>2 else 0
        m = float(np.mean(np.abs(a-p)))
        nm = float(np.mean(np.abs(a-nv)))
        b = sum(1 for pi,ai in zip(preds,act) if abs(pi-ai)<abs(nv-ai))/n*100
        x = sum(1 for pi,ai in zip(preds,act) if 1/2<=max(pi,.1)/max(ai,.1)<=2)/n*100
        dm,dt = 0,0
        for i in range(1,n):
            if np.sign(act[i]-act[i-1])!=0:
                dt+=1
                if np.sign(preds[i]-preds[i-1])==np.sign(act[i]-act[i-1]): dm+=1
        d = dm/max(dt,1)*100
        results.append({'cutoff':cutoff,'corr':c,'beats':b,'x2':x,'dir':d,
                        'mae':m,'naive_mae':nm,'preds':preds[:10],'act':act[:10],
                        'yrs':ty[:10],'naive':nv})
    return results

def full_score(ssn_r, eq_r, label):
    s = 0; lines = []
    ac=np.mean([r['corr'] for r in ssn_r]); p=ac>0.3; s+=p
    lines.append(f"SSNc={ac:+.2f}{'✓' if p else '✗'}")
    bn=sum(1 for r in ssn_r if r['beats']>50); p=bn>=3; s+=p
    lines.append(f"bn={bn}/6{'✓' if p else '✗'}")
    ax=np.mean([r['x2'] for r in ssn_r]); p=ax>30; s+=p
    lines.append(f"×2={ax:.0f}%{'✓' if p else '✗'}")
    ad=np.mean([r['dir'] for r in ssn_r]); p=ad>55; s+=p
    lines.append(f"dir={ad:.0f}%{'✓' if p else '✗'}")
    ec=np.mean([r['corr'] for r in eq_r]); p=ec>0.2; s+=p
    lines.append(f"EQc={ec:+.2f}{'✓' if p else '✗'}")
    ex=np.mean([r['x2'] for r in eq_r]); p=ex>30; s+=p
    lines.append(f"EQ×2={ex:.0f}%{'✓' if p else '✗'}")
    bm=sum(1 for r in ssn_r if r['mae']<r['naive_mae']); p=bm>=3; s+=p
    lines.append(f"MAE={bm}/6{'✓' if p else '✗'}")
    nb=all(r['mae']<500 for r in ssn_r); p=nb; s+=p
    lines.append(f"drift{'✓' if p else '✗'}")

    # Print select trajectories
    print(f"\n  {label}  →  SCORE: {s}/8")
    print(f"    {' | '.join(lines)}")

    # Show SSN cutoff 1990 and 2010 trajectories
    for r in ssn_r:
        if r['cutoff'] in [1990, 2010]:
            print(f"    SSN {r['cutoff']}: ", end="")
            for i in range(min(8, len(r['yrs']))):
                act_s = f"{r['act'][i]:.0f}"
                pred_s = f"{r['preds'][i]:.0f}"
                print(f"{r['yrs'][i]}({act_s}/{pred_s}) ", end="")
            print()

    # Show EQ cutoff 2000
    for r in eq_r:
        if r['cutoff'] == 2000:
            print(f"    EQ  2000: ", end="")
            for i in range(min(8, len(r['yrs']))):
                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
            print()

    return s

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_sunspot_annual()
    eq  = load_earthquake_annual()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]
    C_ssn = np.mean(np.log10([max(v,.1) for v in ssn.values()]))

    versions = [
        ("V1: ARA above / mirror below", ara_geared_v1),
        ("V2: ARA above / reciprocal below", ara_geared_v2),
        ("V3: continuous ARA blend", ara_geared_v3),
        ("V4: ARA-scaled thresholds", ara_geared_v4),
        ("V5: dual ARA beat frequency", ara_geared_v5),
        ("V6: ARA switches R_matter", ara_geared_v6),
    ]

    print(f"\n{'='*70}")
    print("OSCILLATION DIAGNOSTIC")
    print("="*70)
    for label, fn in versions:
        oscillation_test(fn, label, C_ssn)

    print(f"\n{'='*70}")
    print("BLIND TESTS")
    print("="*70)

    all_scores = {}
    for label, fn in versions:
        ssn_r = run_blind(ssn, cutoffs, ARA_SSN, fn)
        eq_r  = run_blind(eq,  cutoffs, ARA_EQ,  fn)
        s = full_score(ssn_r, eq_r, label)
        all_scores[label] = s

    print(f"\n{'='*70}")
    print("GRAND COMPARISON")
    print("="*70)
    print(f"  170 V4 (φ inside longitude):  6/8  ← overall best")
    print(f"  172 V6 (restoring-only):      5/8  (SSN beats naive 6/6)")
    print(f"  171 V6 (inner-outer):         5/8  (EQ ×2=100%)")
    for label, s in all_scores.items():
        m = " ★ NEW BEST" if s > 6 else " ← ties" if s == 6 else ""
        print(f"  173 {label}: {s}/8{m}")

    best = max(all_scores.values())
    print(f"\n  Best this script: {best}/8")
    print(f"\nScript 173 complete.")
