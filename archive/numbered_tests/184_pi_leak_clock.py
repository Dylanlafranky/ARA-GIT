#!/usr/bin/env python3
"""
Script 184 — π-Leak at Clock Boundaries
=========================================

Dylan's insight: "Each time the clock crosses 0 or reaches one of the 2,
we add or remove π-leak (the opposite of the clock)."

The π-leak is (π - 3) ≈ 0.14159 — the geometric inefficiency of circles.
Circles don't tile: π > 3, and that gap is energy that leaks at boundaries.

Applied to the clock:
    - When effective_ARA > 1 (discharge phase): SUBTRACT π-leak
      → system is outputting, leak bleeds energy → pulls prediction down
    - When effective_ARA < 1 (accumulation phase): ADD π-leak
      → system is absorbing, leak feeds energy in → pushes prediction up

This is OPPOSITE to the clock direction — a restoring force that doesn't
depend on the current value's position.  It works even when the prediction
is trapped at zero (where the wave mechanism dies), because the leak
comes from the CLOCK, not the VALUE.

The leak accumulates: at the bottom of a cycle, the clock spends ~11 years
in accumulation phase, adding ~11 × π-leak × scale = ~1.56 × scale in
log-space.  That's enough to push from log(1) back up toward log(50).

Versions:
    V1: Continuous π-leak (proportional to clock deviation from 1.0)
    V2: Discrete π-leak (impulse at clock zero-crossings)
    V3: Proportional to |eff - 1.0| (stronger at extremes)
    V4: Combined with 178's mechanism (the 7/8 baseline)
    V5: Scaled by ARA (bigger leak for bigger systems)
"""

import numpy as np
import os

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3  # ≈ 0.14159

ARA_SSN = 1.73
ARA_EQ  = 0.15
MIDPOINT_OFFSET = abs((ARA_SSN + ARA_EQ) / 2 - R_COUPLER)

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def effective_ara(ara_base, t, phase0):
    center = 1.0
    amp = ara_base - center
    return center + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

# ─── V1: Continuous π-leak (opposite of clock) ─────────────────────

def make_v1(leak_scale):
    """
    Continuous leak: each year, add PI_LEAK × sign(1.0 - eff) × scale.
    When eff > 1 (discharge): leak is negative (bleeds energy)
    When eff < 1 (accumulation): leak is positive (feeds energy)
    Always pushes OPPOSITE to the clock.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        eff = effective_ara(R_matter, t, phase0)
        eff = max(eff, 0.1)

        # Standard 178 wave mechanism
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

        wave_dlog = inner + drive * gear * outer

        # π-LEAK: opposite of clock direction
        # sign(1.0 - eff) = +1 when accumulating, -1 when discharging
        leak = PI_LEAK * np.sign(1.0 - eff) * leak_scale

        dlog = wave_dlog + leak
        return log_val + dlog
    return predict

# ─── V2: π-leak proportional to |eff - 1| ──────��───────────────────

def make_v2(leak_scale):
    """
    Leak proportional to how far the clock is from center.
    Bigger leak at extremes (peak discharge/accumulation).
    """
    def predict(log_val, C, R_matter, step, t, phase0):
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

        wave_dlog = inner + drive * gear * outer

        # Proportional π-leak: stronger at clock extremes
        leak = PI_LEAK * (1.0 - eff) * leak_scale  # note: (1-eff), not sign

        dlog = wave_dlog + leak
        return log_val + dlog
    return predict

# ─── V3: π-leak scaled by ARA ──────────────────────────────────────

def make_v3(leak_scale):
    """
    Leak scaled by (R_matter - 1.0): bigger systems leak more.
    SSN (ARA=1.73): leak × 0.73
    EQ (ARA=0.15): leak × -0.85 (opposite sign! consumers absorb)
    """
    def predict(log_val, C, R_matter, step, t, phase0):
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

        wave_dlog = inner + drive * gear * outer

        # ARA-scaled π-leak
        ara_factor = R_matter - 1.0  # +0.73 for SSN, -0.85 for EQ
        leak = PI_LEAK * (1.0 - eff) * ara_factor * leak_scale

        dlog = wave_dlog + leak
        return log_val + dlog
    return predict

# ─── V4: π-leak only when clock crosses boundaries ─────────────────

class BoundaryCrossingPredictor:
    """
    Discrete π-leak: only fires when the clock crosses 1.0 (center)
    or reaches near 0 or 2.

    Track previous eff to detect crossings.
    At each crossing, apply a π-leak impulse.
    """
    def __init__(self):
        self.prev_eff = 1.0

    def reset(self, phase0=0.0):
        self.prev_eff = 1.0

    def predict(self, log_val, C, R_matter, step, t, phase0, leak_scale=1.0):
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

        wave_dlog = inner + drive * gear * outer

        # Detect boundary crossings
        leak = 0.0
        # Crossing center (eff crosses 1.0)
        if (self.prev_eff - 1.0) * (eff - 1.0) < 0:
            # Crossed center! Apply impulse opposite to new direction
            leak = PI_LEAK * np.sign(1.0 - eff) * leak_scale

        # Near extremes (eff near 0 or 2)
        if eff > 1.8 or eff < 0.2:
            leak += PI_LEAK * np.sign(1.0 - eff) * leak_scale * 0.5

        self.prev_eff = eff

        dlog = wave_dlog + leak
        return log_val + dlog

# ─── V5: Leak as the sin of the clock (smooth, opposite) ───────────

def make_v5(leak_scale):
    """
    Leak = PI_LEAK × sin(clock_phase + π)  — exactly opposite the clock.
    The sin ensures smooth, continuous, oscillating leak.
    Adding π to the phase makes it exactly antiphase.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
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

        wave_dlog = inner + drive * gear * outer

        # Antiphase π-leak: sin of clock + π
        clock_phase = 2*np.pi*t/HALE_PERIOD + phase0
        leak = PI_LEAK * np.sin(clock_phase + np.pi) * leak_scale

        dlog = wave_dlog + leak
        return log_val + dlog
    return predict

# ─── Phase calibration & data ───────────────────────────────────────

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
                        'mae':m,'naive_mae':nm,'preds':preds[:18],'act':act[:18],
                        'yrs':ty[:18],'naive':nv,'ph':ph})
    return results

def score_and_report(sr, er, label, verbose=False):
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

    if verbose or s >= 7:
        print(f"\n  {label}  →  {s}/8")
        print(f"    {' | '.join(li)}")
        for r in sr:
            if r['cutoff'] in [1990, 2010]:
                print(f"    SSN {r['cutoff']} (φ0={r['ph']:.2f}): ", end="")
                for i in range(min(17, len(r['yrs']))):
                    print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
                print()
        for r in er:
            if r['cutoff'] == 2000:
                print(f"    EQ  2000: ", end="")
                for i in range(min(8, len(r['yrs']))):
                    print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
                print()
    else:
        print(f"  {label}: {s}/8  [{' | '.join(li)}]")
    return s

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_ssn(); eq = load_eq()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

    print(f"π-leak = π - 3 = {PI_LEAK:.5f}")
    print(f"Over 11 years of accumulation: ~{11 * PI_LEAK:.2f} log-units")
    print(f"  = factor of {10**(11*PI_LEAK):.1f}× in linear space")

    print(f"\n{'='*70}")
    print("π-LEAK AT CLOCK BOUNDARIES")
    print("="*70)

    all_scores = {}

    # V1: Continuous sign-based leak
    for ls in [0.1, 0.2, 0.3, 0.5, 0.618, 1.0]:
        label = f"V1 sign leak={ls}"
        fn = make_v1(ls)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    # V2: Proportional leak
    for ls in [0.1, 0.2, 0.3, 0.5, 1.0]:
        label = f"V2 prop leak={ls}"
        fn = make_v2(ls)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    # V3: ARA-scaled leak
    for ls in [0.1, 0.2, 0.3, 0.5, 1.0]:
        label = f"V3 ARA leak={ls}"
        fn = make_v3(ls)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    # V5: Antiphase sinusoidal leak
    for ls in [0.1, 0.2, 0.3, 0.5, 1.0]:
        label = f"V5 sin leak={ls}"
        fn = make_v5(ls)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    print(f"\n{'='*70}")
    print("TOP RESULTS")
    print("="*70)
    print(f"  Previous best:  7/8  (Script 178)")
    for label, s in sorted(all_scores.items(), key=lambda x: -x[1])[:12]:
        m = " ★ 8/8!" if s == 8 else " ★ NEW BEST" if s > 7 else " ← ties 7" if s == 7 else ""
        print(f"  184 {label}: {s}/8{m}")

    print(f"\nScript 184 complete.")
