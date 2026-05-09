#!/usr/bin/env python3
"""
Script 175 — Inner Circle Drives Outer
========================================

Dylan's insight:
    "the circle is too small for the wave we're trying to put on it"
    "The wave is the same log as it, while it needs to be below it
     to fit inside and track it."

Problem: R_COUPLER = 1.0 produces waves with amplitude ~1 log-unit.
SSN needs ~2.5 logs of dynamic range (SSN 3→300).
The prediction circle hits its sin ceiling (±1) before the data
reaches its peak.  Like a gear that's the same size as the wheel
it's trying to drive — it can't make the wheel turn far enough.

Solution: SMALLER prediction circle, AMPLIFIED output.

    R_wave = R_COUPLER / ARA  (or 1/ARA, or other scaling)
    output = wave(phi, R_wave) × ARA

The small circle fits INSIDE the data's range.  It makes FULL
rotations without clipping.  The ARA value is the gear ratio
that amplifies the small circle's motion to the data's scale.

For SSN (ARA=1.73):
    R_wave = 1.0/1.73 = 0.578
    Amplitude = 0.578 × 1.73 = 1.0 ... wait, that just gives 1.0 again.

Actually, the insight is about the MAPPING, not just the amplitude.
The value_to_longitude function clips at ±1 when (log_val - C)/R
exceeds ±1.  If R is too small, the MAPPING clips before the data
reaches its extremes.  If we use a LARGER R for the mapping
(R = ARA instead of 1.0), the mapping won't clip.

Reframing: the wave circle should be AT the ARA scale, not at 1.0.
The COUPLERS are at 1.0, but the PREDICTION needs to use the
system's OWN radius.

Or: the wave operates one log below.  Instead of predicting
log(SSN), we predict log(log(SSN)) — the wave lives in a
compressed space where the full cycle fits on the circle.
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

# ─── Core ────────────────────────────────────────────────────────────

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def effective_ara(ara_base, t, phase0):
    center = 1.0
    amp = ara_base - center
    return center + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

# ─── Versions ────────────────────────────────────────────────────────

def v1_ara_radius_mapping(log_val, C, R_matter, step, t, phase0):
    """
    V1: Use R_matter (ARA) as the mapping radius instead of 1.0.

    For SSN: R=1.73 means the mapping doesn't clip until
    |log - C| > 1.73, which covers the full SSN range.
    The wave can then access the FULL circle before clipping.

    Combined with clock-driven effective ARA.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    # Map using SYSTEM'S radius, not coupler's
    phi = value_to_longitude(log_val, C, R_matter)
    phi_next = phi + DPHI * step

    # φ-inside for stability, but at the SYSTEM'S radius
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2

    # Couplers still at R=1.0, but operating on the wider longitude
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2)

    # Outer wave also at wider mapping
    c1ns = wave(phi, R_COUPLER)
    c2ns = wave(phi+HALF_PHI, R_COUPLER)
    c1xs = wave(phi_next, R_COUPLER)
    c2xs = wave(phi_next+HALF_PHI, R_COUPLER)
    outer = ((c1xs+c2xs)/2 - (c1ns+c2ns)/2)

    # Clock-driven modulation
    drive = eff - 1.0
    distance = abs(log_val - C)
    gear = max(distance / HALF_PHI, 0.1)

    # Amplify by ARA ratio (the gear amplification)
    dlog = (inner + drive * gear * outer) * R_matter * np.exp(-MIDPOINT_OFFSET)
    return log_val + dlog


def v2_wave_below(log_val, C, R_matter, step, t, phase0):
    """
    V2: Wave operates at R_wave = 1/ARA (fits inside).
    Output amplified by ARA.

    For SSN: R_wave = 1/1.73 = 0.578
    The wave makes tighter rotations but the output is scaled up.

    sin(phi / 0.578) oscillates faster → more cycles per radian
    → the wave "fits inside" the larger data circle.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    R_wave = 1.0 / R_matter  # smaller circle

    phi = value_to_longitude(log_val, C, R_matter)  # map at data scale
    phi_next = phi + DPHI * step

    # Wave at the smaller radius
    c1n = wave(phi, R_wave)
    c2n = wave(phi+HALF_PHI, R_wave)
    c1x = wave(phi_next, R_wave)
    c2x = wave(phi_next+HALF_PHI, R_wave)
    delta = ((c1x+c2x)/2 - (c1n+c2n)/2)

    # Amplify by ARA
    drive = eff - 1.0
    dlog = delta * R_matter * (1 + drive * 0.5) * np.exp(-MIDPOINT_OFFSET)
    return log_val + dlog


def v3_nested_circles(log_val, C, R_matter, step, t, phase0):
    """
    V3: Two nested circles.

    Inner circle: R = 1/ARA (the prediction engine, fits inside)
    Outer circle: R = ARA (the data space)

    The inner circle drives the outer through their gear ratio.

    Prediction:
    1. Map value to longitude on the OUTER circle (R=ARA)
    2. Compute wave on the INNER circle (R=1/ARA) at same longitude
    3. Delta = inner_wave × gear_ratio
    4. gear_ratio = ARA² (inner to outer amplification)

    For SSN: gear = 1.73² = 2.99 → nearly 3× amplification
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    R_outer = R_matter        # 1.73 for SSN
    R_inner = 1.0 / R_matter  # 0.578 for SSN
    gear_ratio = R_matter ** 2  # 2.99 for SSN

    # Map on outer circle (wide, no clipping)
    phi = value_to_longitude(log_val, C, R_outer)
    phi_next = phi + DPHI * step

    # φ-stable on inner circle
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2

    c1n = avg_w(phi, R_inner, PHI)
    c1x = avg_w(phi_next, R_inner, PHI)
    c2n = avg_w(phi+HALF_PHI, R_inner, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_inner, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2)

    # Standard wave on inner circle (for outer drive)
    c1ns = wave(phi, R_inner)
    c2ns = wave(phi+HALF_PHI, R_inner)
    c1xs = wave(phi_next, R_inner)
    c2xs = wave(phi_next+HALF_PHI, R_inner)
    outer_drive = ((c1xs+c2xs)/2 - (c1ns+c2ns)/2)

    # Clock modulation
    drive = eff - 1.0
    distance = abs(log_val - C)
    gear_engage = max(distance / HALF_PHI, 0.1)

    # Inner stability + outer drive, both amplified by gear ratio
    dlog = (inner + drive * gear_engage * outer_drive) * gear_ratio * np.exp(-MIDPOINT_OFFSET)
    return log_val + dlog


def v4_log_below(log_val, C, R_matter, step, t, phase0):
    """
    V4: "The wave needs to be below it" — literally.

    Instead of predicting Δ(log_val), predict Δ(normalized_val)
    where normalized = (log_val - C) / R_matter.

    This puts the wave in [-1, 1] space — the natural range
    of the circle.  Then scale back up by R_matter.

    The wave operates in the NORMALIZED space (below the log),
    and the ARA value scales it back to the log.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    # Normalize to [-1, 1]
    norm_val = np.clip((log_val - C) / R_matter, -1, 1)

    # Longitude from normalized value (no R scaling)
    phi = np.arcsin(norm_val)
    phi_next = phi + DPHI * step

    # Wave in normalized space
    def avg_w(pos, off):
        return (np.sin(pos + off) + np.sin(pos - off)) / 2

    # φ-stable in normalized space
    c1n = avg_w(phi, PHI)
    c1x = avg_w(phi_next, PHI)
    c2n = avg_w(phi + HALF_PHI, PHI)
    c2x = avg_w(phi_next + HALF_PHI, PHI)
    inner_norm = ((c1x+c2x)/2 - (c1n+c2n)/2)

    # Standard wave in normalized space
    s1n = np.sin(phi)
    s2n = np.sin(phi + HALF_PHI)
    s1x = np.sin(phi_next)
    s2x = np.sin(phi_next + HALF_PHI)
    outer_norm = ((s1x+s2x)/2 - (s1n+s2n)/2)

    # Clock + gear
    drive = eff - 1.0
    distance = abs(norm_val)
    gear = max(distance, 0.1)

    # Combined in normalized space, then scale to log
    d_norm = inner_norm + drive * gear * outer_norm
    dlog = d_norm * R_matter * np.exp(-MIDPOINT_OFFSET)

    return log_val + dlog


def v5_dual_scale(log_val, C, R_matter, step, t, phase0):
    """
    V5: The prediction uses TWO scales simultaneously.

    Scale 1: Longitude mapped at R=1.0 (coupler scale) — the φ-stable base
    Scale 2: Longitude mapped at R=ARA (system scale) — the amplitude driver

    The clock determines the MIX between the two scales:
        At discharge phase: weight toward system scale (big swings)
        At accumulation phase: weight toward coupler scale (stability)

    This is literally "the gear shifts" — the effective radius of
    the prediction circle changes with the clock.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    # Scale 1: coupler-scale φ-stable (from Script 170 V4)
    phi1 = value_to_longitude(log_val, C, R_COUPLER)
    phi1_next = phi1 + DPHI * step
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi1, R_COUPLER, PHI)
    c1x = avg_w(phi1_next, R_COUPLER, PHI)
    c2n = avg_w(phi1+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi1_next+HALF_PHI, R_COUPLER, PHI)
    delta_coupler = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Scale 2: system-scale standard wave (wider, no clipping)
    phi2 = value_to_longitude(log_val, C, R_matter)
    phi2_next = phi2 + DPHI * step
    s1n = wave(phi2, R_COUPLER)
    s2n = wave(phi2+HALF_PHI, R_COUPLER)
    s1x = wave(phi2_next, R_COUPLER)
    s2x = wave(phi2_next+HALF_PHI, R_COUPLER)
    delta_system = ((s1x+s2x)/2 - (s1n+s2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Amplify system-scale by ARA
    delta_system *= R_matter

    # Clock-driven mix
    # eff > 1: more system scale (discharge, big swings)
    # eff < 1: more coupler scale (accumulation, stability)
    mix = np.clip((eff - 0.5) / 1.0, 0, 1)  # 0 at eff=0.5, 1 at eff=1.5

    dlog = (1 - mix) * delta_coupler + mix * delta_system
    return log_val + dlog


# ─── Phase calibration ──────────────────────────────────────────────

def calibrate_phase(train_data, R_matter, predict_fn, n_phases=24):
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v,.1) for v in train_data.values()]))
    best_phase = 0.0; best_score = -999
    for pi in range(n_phases):
        phase0 = 2*np.pi*pi/n_phases
        test_start = max(0, len(years)-15)
        current = np.log10(max(train_data[years[test_start]],.1))
        pc, ac_list = [], []
        for i in range(test_start+1, len(years)):
            t = i - test_start
            new = predict_fn(current, C, R_matter, 1, t, phase0)
            pc.append(new - current)
            actual = np.log10(max(train_data[years[i]],.1)) - np.log10(max(train_data[years[i-1]],.1))
            ac_list.append(actual)
            current = np.log10(max(train_data[years[i]],.1))
        if len(pc) < 5: continue
        p, a = np.array(pc), np.array(ac_list)
        corr = float(np.corrcoef(p,a)[0,1]) if np.std(p)>0 and np.std(a)>0 else 0
        dm = sum(1 for pi2,ai in zip(p,a) if np.sign(pi2)==np.sign(ai))/len(p)
        score = corr + dm
        if score > best_score: best_score = score; best_phase = phase0
    return best_phase

# ─── Data loaders ────────────────────────────────────────────────────

def load_ssn():
    p = os.path.join(os.path.dirname(__file__), '..', 'solar_test', 'sunspots.txt')
    m = {}
    with open(p) as f:
        for l in f:
            ps = l.split()
            if len(ps)<4: continue
            try:
                y=int(ps[0]); v=float(ps[3])
                if v<0: continue
                m.setdefault(y,[]).append(v)
            except: continue
    return {y:np.mean(v) for y,v in m.items() if len(v)>=6}

def load_eq():
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

# ─── Test ────────────────────────────────────────────────────────────

def osc_test(fn, label, C, R=ARA_SSN, phase0=0.0):
    res = []
    for off in [0.5, -0.8, 1.2]:  # high, low, very high
        lv = C + off; pd = 0; turns = 0; vals = []
        for yr in range(30):
            nw = fn(lv, C, R, 1, yr, phase0)
            d = nw - lv
            if yr>0 and np.sign(d)!=np.sign(pd) and pd!=0: turns+=1
            pd=d; vals.append(10**lv); lv=nw
        res.append((turns, min(vals), max(vals)))
    h,l,vh = res
    print(f"  {label}: hi={h[0]}t[{h[1]:.0f},{h[2]:.0f}] "
          f"lo={l[0]}t[{l[1]:.0f},{l[2]:.0f}] "
          f"vhi={vh[0]}t[{vh[1]:.0f},{vh[2]:.0f}]")
    return h[0]+l[0]+vh[0]

def run_blind(data, cutoffs, R_matter, fn):
    results = []
    for cutoff in cutoffs:
        tr={y:v for y,v in data.items() if y<cutoff}
        te={y:v for y,v in data.items() if y>=cutoff}
        if len(tr)<10 or len(te)<5: continue
        C=np.mean(np.log10([max(v,.1) for v in tr.values()]))
        ph=calibrate_phase(tr,R_matter,fn)
        sv=max(data[max(tr.keys())],.1); ty=sorted(te.keys())
        preds=[]; cur=np.log10(sv)
        for i,y in enumerate(ty):
            cur=fn(cur,C,R_matter,1,i+1,ph); preds.append(10**cur)
        act=[data[y] for y in ty]; n=len(ty); nv=sv
        a,p=np.array(act),np.array(preds)
        c=float(np.corrcoef(a,p)[0,1]) if np.std(a)>0 and np.std(p)>0 and len(a)>2 else 0
        m=float(np.mean(np.abs(a-p))); nm=float(np.mean(np.abs(a-nv)))
        b=sum(1 for pi,ai in zip(preds,act) if abs(pi-ai)<abs(nv-ai))/n*100
        x=sum(1 for pi,ai in zip(preds,act) if 1/2<=max(pi,.1)/max(ai,.1)<=2)/n*100
        dm,dt=0,0
        for i in range(1,n):
            if np.sign(act[i]-act[i-1])!=0:
                dt+=1
                if np.sign(preds[i]-preds[i-1])==np.sign(act[i]-act[i-1]): dm+=1
        d=dm/max(dt,1)*100
        results.append({'cutoff':cutoff,'corr':c,'beats':b,'x2':x,'dir':d,
                        'mae':m,'naive_mae':nm,'preds':preds[:12],'act':act[:12],
                        'yrs':ty[:12],'naive':nv,'ph':ph})
    return results

def full_score(sr, er, label):
    s=0; li=[]
    ac=np.mean([r['corr'] for r in sr]); p=ac>0.3; s+=p
    li.append(f"SSNc={ac:+.2f}{'✓' if p else '✗'}")
    bn=sum(1 for r in sr if r['beats']>50); p=bn>=3; s+=p
    li.append(f"bn={bn}{'✓' if p else '✗'}")
    ax=np.mean([r['x2'] for r in sr]); p=ax>30; s+=p
    li.append(f"×2={ax:.0f}%{'✓' if p else '✗'}")
    ad=np.mean([r['dir'] for r in sr]); p=ad>55; s+=p
    li.append(f"dir={ad:.0f}%{'✓' if p else '✗'}")
    ec=np.mean([r['corr'] for r in er]); p=ec>0.2; s+=p
    li.append(f"EQc={ec:+.2f}{'✓' if p else '✗'}")
    ex=np.mean([r['x2'] for r in er]); p=ex>30; s+=p
    li.append(f"EQ×2={ex:.0f}%{'✓' if p else '✗'}")
    bm=sum(1 for r in sr if r['mae']<r['naive_mae']); p=bm>=3; s+=p
    li.append(f"MAE={bm}{'✓' if p else '✗'}")
    nb=all(r['mae']<500 for r in sr); p=nb; s+=p
    li.append(f"drift{'✓' if p else '✗'}")

    print(f"\n  {label}  →  {s}/8")
    print(f"    {' | '.join(li)}")
    for r in sr:
        if r['cutoff'] in [1990,2010]:
            print(f"    SSN {r['cutoff']}: ",end="")
            for i in range(min(10,len(r['yrs']))):
                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ",end="")
            print()
    for r in er:
        if r['cutoff']==2000:
            print(f"    EQ  2000: ",end="")
            for i in range(min(8,len(r['yrs']))):
                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ",end="")
            print()
    return s

# ─── Main ────────────────────────────────────────────────────────────

if __name__=='__main__':
    ssn=load_ssn(); eq=load_eq()
    cutoffs=[1990,1995,2000,2005,2010,2015]
    C_ssn=np.mean(np.log10([max(v,.1) for v in ssn.values()]))

    versions = [
        ("V1: ARA-radius mapping + clock", v1_ara_radius_mapping),
        ("V2: wave below (R=1/ARA), amplified", v2_wave_below),
        ("V3: nested circles (R_inner=1/ARA, gear=ARA²)", v3_nested_circles),
        ("V4: normalized space (wave below log)", v4_log_below),
        ("V5: dual scale (coupler+system, clock-mixed)", v5_dual_scale),
    ]

    print("="*70)
    print("OSCILLATION DIAGNOSTIC (phase0=0)")
    print("="*70)
    for label,fn in versions:
        osc_test(fn,label,C_ssn)

    print(f"\n{'='*70}")
    print("BLIND TESTS (with phase calibration)")
    print("="*70)

    scores={}
    for label,fn in versions:
        sr=run_blind(ssn,cutoffs,ARA_SSN,fn)
        er=run_blind(eq,cutoffs,ARA_EQ,fn)
        scores[label]=full_score(sr,er,label)

    print(f"\n{'='*70}")
    print("GRAND COMPARISON")
    print("="*70)
    print(f"  170 V4 (φ inside longitude):        6/8")
    print(f"  174 V4 (clock + full modulation):    6/8")
    print(f"  174 V5 (dual coupled oscillators):   6/8")
    for l,s in scores.items():
        m=" ★ NEW BEST" if s>6 else " ← ties" if s==6 else ""
        print(f"  175 {l}: {s}/8{m}")

    print(f"\nScript 175 complete.")
