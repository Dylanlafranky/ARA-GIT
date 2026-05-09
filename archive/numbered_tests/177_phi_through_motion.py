#!/usr/bin/env python3
"""
Script 177 — φ-Through Motion
===============================

Dylan's insight: "We are doing waves up and down, but we aren't allowing
for the left and right. It should be moving through at φ."

Previous scripts lock the step size to DPHI = 2π/22 (the Hale period),
imposing the oscillation period externally.  But in ARA geometry, the
point PROGRESSES through the circle at the GOLDEN ANGLE:

    golden_angle = 2π / φ²  ≈  2.3999 rad  ≈  137.508°

This is what creates the sunflower spiral, the non-repeating optimal
packing.  Each time step, the position advances by the golden angle.
The wave VALUE read at each position (up/down) creates the oscillation,
but the MOTION (left/right) is at φ.

The period isn't imposed — it EMERGES from the geometry.  After φ²
steps (~2.618), the position has gone ~2π around.  But because it
never exactly repeats (irrational), you get a quasi-periodic signal
with natural beat frequencies.

Approach:
    V1: Golden angle stepping + φ-stable + clock modulation (174 V4 base)
    V2: Golden angle stepping + R_matter outer wave (amplified)
    V3: φ as the step directly (not golden angle)
    V4: Golden angle + restoring force toward mean
    V5: Golden angle + ARA-scaled wave radius
"""

import numpy as np
import os

# ─── Constants ───────────────────────────────────────────────────────
PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)  # ≈ 2.3999 rad ≈ 137.5°
PHI_STEP = PHI  # raw φ as step size

ARA_SSN = 1.73
ARA_EQ  = 0.15
MIDPOINT_OFFSET = abs((ARA_SSN + ARA_EQ) / 2 - R_COUPLER)

# ─── Core functions ──────────────────────────────────────────────────

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def effective_ara(ara_base, t, phase0):
    center = 1.0
    amp = ara_base - center
    return center + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

# ─── V1: Golden angle step + clock (174 V4 upgraded) ────────────────

def v1_golden_clock(log_val, C, R_matter, step, t, phase0):
    """
    174 V4's mechanism but stepping at the golden angle instead of DPHI.

    The position advances by golden_angle per year.
    The clock still modulates the effective ARA.
    φ-stable provides grounding.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    phi = value_to_longitude(log_val, C, eff)
    phi_next = phi + GOLDEN_ANGLE * step  # <-- golden angle, not DPHI

    # φ-stable on R_COUPLER
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Standard wave for outer drive (also golden angle)
    s1n = wave(phi, R_COUPLER)
    s2n = wave(phi+HALF_PHI, R_COUPLER)
    s1x = wave(phi_next, R_COUPLER)
    s2x = wave(phi_next+HALF_PHI, R_COUPLER)
    outer = ((s1x+s2x)/2 - (s1n+s2n)/2) * np.exp(-MIDPOINT_OFFSET)

    drive = eff - 1.0
    distance = abs(log_val - C)
    gear = distance / HALF_PHI

    dlog = inner + drive * gear * outer
    return log_val + dlog

# ─── V2: Golden angle + R_matter outer wave ─────────────────────────

def v2_golden_rmatter(log_val, C, R_matter, step, t, phase0):
    """
    Golden angle stepping with outer wave on R_matter radius.

    Inner (stability): φ-averaged wave on R_COUPLER
    Outer (amplitude): standard wave on R_matter

    SSN: outer wave has R=1.73, naturally larger amplitude
    EQ:  outer wave has R=0.15, naturally smaller amplitude
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    phi = value_to_longitude(log_val, C, eff)
    phi_next = phi + GOLDEN_ANGLE * step

    # φ-stable on R_COUPLER (inner stability)
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Standard wave on R_matter (outer amplitude)
    s1n = wave(phi, R_matter)
    s2n = wave(phi+HALF_PHI, R_matter)
    s1x = wave(phi_next, R_matter)
    s2x = wave(phi_next+HALF_PHI, R_matter)
    outer = ((s1x+s2x)/2 - (s1n+s2n)/2) * np.exp(-MIDPOINT_OFFSET)

    drive = eff - 1.0
    distance = abs(log_val - C)
    gear = distance / HALF_PHI

    dlog = inner + drive * gear * outer
    return log_val + dlog

# ─── V3: φ as the raw step ──────────────────────────────────────────

def v3_phi_step(log_val, C, R_matter, step, t, phase0):
    """
    Step by φ itself (1.618...) instead of golden angle.

    φ radians per year = one full rotation every 2π/φ ≈ 3.88 years.
    That's 2-3 oscillation cycles per 11-year solar cycle.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    phi_pos = value_to_longitude(log_val, C, eff)
    phi_next = phi_pos + PHI_STEP * step  # raw φ

    # φ-stable inner
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi_pos, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi_pos+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Outer drive
    s1n = wave(phi_pos, R_COUPLER)
    s2n = wave(phi_pos+HALF_PHI, R_COUPLER)
    s1x = wave(phi_next, R_COUPLER)
    s2x = wave(phi_next+HALF_PHI, R_COUPLER)
    outer = ((s1x+s2x)/2 - (s1n+s2n)/2) * np.exp(-MIDPOINT_OFFSET)

    drive = eff - 1.0
    distance = abs(log_val - C)
    gear = distance / HALF_PHI

    dlog = inner + drive * gear * outer
    return log_val + dlog

# ─── V4: Golden angle + restoring force ─────────────────────────────

def v4_golden_restoring(log_val, C, R_matter, step, t, phase0):
    """
    Golden angle stepping with an explicit restoring force toward mean.

    The clock provides rhythm. The restoring force prevents runaway.

    dlog = φ_stable + clock_drive - restoring_pull

    restoring = (log_val - C) × damping_rate

    This is like a damped oscillator: the clock pushes, gravity pulls back.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    phi = value_to_longitude(log_val, C, eff)
    phi_next = phi + GOLDEN_ANGLE * step

    # φ-stable inner
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Clock drive (direct sinusoidal push)
    clock_amp = (R_matter - 1.0) * GOLDEN_ANGLE  # scale by golden angle
    clock_push = clock_amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

    # Restoring force: pulls toward mean C
    displacement = log_val - C
    restoring = -displacement * (1.0 / HALE_PERIOD)  # damping rate = 1/T

    dlog = inner + clock_push + restoring
    return log_val + dlog

# ─── V5: Golden angle + ARA-scaled everything ───────────────────────

def v5_golden_ara_scaled(log_val, C, R_matter, step, t, phase0):
    """
    Golden angle stepping where:
    - Position mapped on R_matter (system's scale)
    - φ-stable on R_COUPLER (universal stability)
    - Wave amplitude scaled by R_matter
    - Clock modulates the blend

    The golden angle advance means each year the system reads a
    completely new position on the circle — no repeated readings.
    The ARA scaling means SSN gets big swings, EQ stays quiet.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    # Map value on SYSTEM's circle (R_matter), not coupler
    phi = value_to_longitude(log_val, C, R_matter)
    phi_next = phi + GOLDEN_ANGLE * step

    # φ-stable on R_COUPLER (grounding)
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Standard wave on R_matter (scaled amplitude)
    s1n = wave(phi, R_matter)
    s2n = wave(phi+HALF_PHI, R_matter)
    s1x = wave(phi_next, R_matter)
    s2x = wave(phi_next+HALF_PHI, R_matter)
    outer = ((s1x+s2x)/2 - (s1n+s2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Clock blends inner and outer
    drive = eff - 1.0  # oscillates ±0.73 for SSN
    blend = (1.0 + drive) / 2.0  # normalized 0-1
    blend = np.clip(blend, 0, 1)

    dlog = (1 - blend) * inner + blend * outer
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
        dm = sum(1 for x,y in zip(p,a) if np.sign(x)==np.sign(y))/len(p)
        score = corr + dm
        if score > best_score: best_score = score; best_phase = phase0
    return best_phase

# ─── Data ────────────────────────────────────────────────────────────

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

# ─── Test harness ────────────────────────────────────────────────────

def osc_test(fn, label, C, R=ARA_SSN, phase0=0.0):
    res = []
    for off in [0.5, -0.8]:
        lv = C + off; pd = 0; turns = 0; vals = []
        for yr in range(30):
            nw = fn(lv, C, R, 1, yr, phase0)
            d = nw - lv
            if yr>0 and np.sign(d)!=np.sign(pd) and pd!=0: turns+=1
            pd=d; vals.append(10**lv); lv=nw
        res.append((turns, min(vals), max(vals)))
    h, l = res
    print(f"  {label}: hi={h[0]}t[{h[1]:.0f},{h[2]:.0f}] lo={l[0]}t[{l[1]:.0f},{l[2]:.0f}]")
    return h[0]+l[0]

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
        if r['cutoff'] in [1990, 2010]:
            print(f"    SSN {r['cutoff']} (φ0={r['ph']:.2f}): ", end="")
            for i in range(min(11, len(r['yrs']))):
                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
            print()
    for r in er:
        if r['cutoff'] == 2000:
            print(f"    EQ  2000: ", end="")
            for i in range(min(8, len(r['yrs']))):
                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
            print()
    return s

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_ssn(); eq = load_eq()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]
    C_ssn = np.mean(np.log10([max(v,.1) for v in ssn.values()]))

    versions = {
        "V1 golden+clock (174V4 base)": v1_golden_clock,
        "V2 golden+Rmatter outer": v2_golden_rmatter,
        "V3 raw φ step": v3_phi_step,
        "V4 golden+restoring": v4_golden_restoring,
        "V5 golden+ARA-scaled": v5_golden_ara_scaled,
    }

    print(f"Golden angle = {GOLDEN_ANGLE:.4f} rad = {np.degrees(GOLDEN_ANGLE):.1f}°")
    print(f"φ step = {PHI_STEP:.4f} rad = {np.degrees(PHI_STEP):.1f}°")
    print(f"Old DPHI = {2*np.pi/HALE_PERIOD:.4f} rad = {np.degrees(2*np.pi/HALE_PERIOD):.1f}°")

    print(f"\n{'='*70}")
    print("OSCILLATION DIAGNOSTIC")
    print("="*70)
    for label, fn in versions.items():
        osc_test(fn, label, C_ssn)

    print(f"\n{'='*70}")
    print("BLIND TESTS (with phase calibration)")
    print("="*70)

    all_scores = {}
    for label, fn in versions.items():
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = full_score(sr, er, label)

    print(f"\n{'='*70}")
    print("GRAND COMPARISON")
    print("="*70)
    print(f"  Previous best:  6/8  (Scripts 170 V4, 174 V4)")
    for label, s in sorted(all_scores.items(), key=lambda x: -x[1]):
        m = " ★ NEW BEST" if s > 6 else " ← ties" if s == 6 else ""
        print(f"  177 {label}: {s}/8{m}")

    print(f"\nScript 177 complete.")
