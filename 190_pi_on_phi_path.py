#!/usr/bin/env python3
"""
Script 190 — π-Leak on φ-Path with Clock Sampling
====================================================

Dylan's insight: "Pi leak follows the path of phi, maps to it with a clock."

The π-leak (geometric inefficiency of circles, 0.14159) isn't a constant drip.
It TRAVELS along the golden spiral. The clock determines where on that spiral
you sample the leak value. So:

    leak(t) = PI_LEAK × f(golden_spiral_position(t))

where f reads the wave at that position and the clock maps time to position.

This means the leak oscillates naturally with the golden angle rhythm.
Each tick advances GOLDEN_ANGLE radians along the spiral.
The clock (Hale cycle) modulates the amplitude.

Combined with learning from 189:
    - Soft floor at C - offset prevents collapse (V6 worked well)
    - φ-leak per tick adds handoff energy
    - Pure clock gets best SSN correlation (+0.244)

Architecture:
    wave_mechanism → fine structure (within-cycle changes)
    π_on_φ_path → generative oscillation (cross-cycle sustain)
    soft_floor → collapse prevention
"""

import numpy as np
import os

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)  # ≈ 2.3999 rad ≈ 137.508°
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3  # ≈ 0.14159
PHI_LEAK = 1.0 / PHI  # ≈ 0.618

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

# ─── V1: π-leak on φ-path (basic) ─────────────────────────────────

def make_pi_phi_path(scale):
    """
    The π-leak travels along the golden spiral.
    At each tick, advance GOLDEN_ANGLE along the spiral.
    Read the wave at that position. Scale by PI_LEAK.

    leak(t) = PI_LEAK × sin(GOLDEN_ANGLE × t) × scale

    This creates a quasi-periodic oscillation that NEVER repeats
    (golden angle is irrational), giving maximum coverage.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # π-leak position on φ-path
        phi_path_pos = GOLDEN_ANGLE * t + phase0
        leak = PI_LEAK * np.sin(phi_path_pos) * scale

        return log_val + wdlog + leak
    return predict

# ─── V2: π on φ-path with R_matter amplitude ──────────────────────

def make_pi_phi_R(scale):
    """
    Like V1, but the wave is evaluated WITH R_matter as radius.
    This means the leak amplitude scales naturally with system type.
    wave(phi_path, R_matter) uses the ARA-scaled wave function.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        phi_path_pos = GOLDEN_ANGLE * t + phase0
        # Use the actual wave function with R_matter
        leak = PI_LEAK * wave(phi_path_pos, R_matter) * scale

        return log_val + wdlog + leak
    return predict

# ─── V3: π on φ-path with Hale envelope ───────────────────────────

def make_pi_phi_hale(scale):
    """
    The φ-path oscillation is ENVELOPED by the Hale cycle.
    The clock modulates the amplitude of the φ-path leak.

    leak(t) = PI_LEAK × sin(GA × t) × (1 - eff(t)) × scale

    During accumulation (eff < 1): leak is positive (restoring)
    During discharge (eff > 1): leak is negative (releasing)
    The φ-path determines the fine structure within each phase.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        phi_path_pos = GOLDEN_ANGLE * t
        phi_structure = np.sin(phi_path_pos)
        hale_envelope = (1.0 - eff)

        leak = PI_LEAK * phi_structure * hale_envelope * scale

        return log_val + wdlog + leak
    return predict

# ─── V4: π on φ-path + soft floor ─────────────────────────────────

def make_pi_phi_floor(scale, floor_offset=0.8):
    """V3 with soft floor to prevent collapse."""
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        phi_path_pos = GOLDEN_ANGLE * t
        phi_structure = np.sin(phi_path_pos)
        hale_envelope = (1.0 - eff)
        leak = PI_LEAK * phi_structure * hale_envelope * scale

        new_val = log_val + wdlog + leak

        # Soft floor
        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V5: φ-stable π-leak (average of pos+φ and pos-φ) ────────────

def make_pi_phi_stable(scale):
    """
    φ-stable version: average the leak at pos+PHI and pos-PHI
    on the golden path. This creates the same natural dampening
    as the φ-stable wave (cos(φ) ≈ -0.047).

    The dampening prevents the leak from overshooting while
    the golden path prevents it from repeating.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        phi_path_pos = GOLDEN_ANGLE * t + phase0
        # φ-stable: average at ±φ offset
        leak_plus = np.sin((phi_path_pos + PHI) / R_COUPLER)
        leak_minus = np.sin((phi_path_pos - PHI) / R_COUPLER)
        phi_stable_leak = (leak_plus + leak_minus) / 2  # = cos(φ/R) × sin(pos/R)

        hale_gate = (1.0 - eff)
        leak = PI_LEAK * phi_stable_leak * hale_gate * scale

        return log_val + wdlog + leak
    return predict

# ─── V6: Dual path — π leaks on φ, φ leaks on π ���─────────────────

def make_dual_leak(pi_scale, phi_scale):
    """
    Two simultaneous leaks:
    1. π-leak follows the φ-path: PI_LEAK × sin(GA × t) × (1-eff)
    2. φ-leak follows a π-path: PHI_LEAK × sin(π × t/11) × (1-eff)

    The π-path has period 22 (11 half-cycles), naturally matching Hale.
    The φ-path has irrational period, giving non-repeating coverage.
    Together: structured (Hale-locked) + unstructured (golden) leaks.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        hale_gate = (1.0 - eff)

        # π on φ-path
        pi_on_phi = PI_LEAK * np.sin(GOLDEN_ANGLE * t) * hale_gate * pi_scale

        # φ on Hale path (period = 22 through π)
        phi_on_pi = PHI_LEAK * np.sin(np.pi * t / 11.0 + phase0) * phi_scale

        return log_val + wdlog + pi_on_phi + phi_on_pi
    return predict

# ─── V7: Accumulated φ-path leak with floor ───────────────────────

def make_accum_phi_floor(scale, floor_offset=0.8):
    """
    The π-on-φ-path leak ACCUMULATES over time (doesn't apply each tick
    but adds up internally and only manifests as a trend).
    Plus soft floor.

    accumulated(t) = sum_{i=1}^{t} PI_LEAK × sin(GA × i) × (1-eff(i))
    Applied as: C + accumulated(t) × scale + wave_correction
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # Accumulated π-on-φ leak from tick 1 to t
        accum = 0.0
        for i in range(1, t+1):
            eff_i = effective_ara(R_matter, i, phase0)
            accum += PI_LEAK * np.sin(GOLDEN_ANGLE * i) * (1.0 - eff_i) * scale

        new_val = log_val + wdlog + accum / max(t, 1)  # average per tick

        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V8: Generative π-on-φ + iterative wave ───────────────────────

def make_generative_pi_phi(gen_weight, scale):
    """
    Blend iterative wave with a generative term:
    generative(t) = C + PI_LEAK × accumulated_sin(GA × 1..t) × (1-eff) × scale

    The generative part comes from geometry alone — no feedback.
    The iterative part handles within-cycle details.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        iterative = log_val + wdlog

        # Generative: running sum of π-on-φ-path
        running = 0.0
        for i in range(1, t+1):
            eff_i = effective_ara(R_matter, i, phase0)
            running += PI_LEAK * np.sin(GOLDEN_ANGLE * i) * (1.0 - eff_i)

        generative = C + running * scale

        return (1.0 - gen_weight) * iterative + gen_weight * generative
    return predict

# ─── V9: π-on-φ as the STEP SIZE ──────────────────────────────────

def make_pi_phi_step(step_scale):
    """
    Instead of adding π-on-φ as a leak, use it as a MODULATION of
    the step size. The wave mechanism's step advances by:
        step_size = GA/φ + PI_LEAK × sin(GA × t) × step_scale

    This means the wave sometimes steps faster (when π-on-φ is positive)
    and sometimes slower (when negative). The golden angle ensures
    no two ticks step the same amount.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        eff = effective_ara(R_matter, t, phase0)
        eff = max(eff, 0.1)

        # Modulated step size
        phi_mod = PI_LEAK * np.sin(GOLDEN_ANGLE * t) * step_scale
        actual_step = GA_OVER_PHI + phi_mod

        phi = value_to_longitude(log_val, C, eff)
        phi_next = phi + actual_step * step

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
        return log_val + wdlog
    return predict

# ─── Phase calibration & data ─────────────────────────────────────

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
        tr = {y:v for y,v in data.items() if y < cutoff}
        te = {y:v for y,v in data.items() if y >= cutoff}
        if len(tr) < 10 or len(te) < 5: continue
        C = np.mean(np.log10([max(v,.1) for v in tr.values()]))
        ph = calibrate_phase(tr, R_matter, fn)
        sv = max(data[max(tr.keys())], .1)
        ty = sorted(te.keys())
        preds = []; cur = np.log10(sv)
        for i, y in enumerate(ty):
            cur = fn(cur, C, R_matter, 1, i+1, ph); preds.append(10**cur)
        act = [data[y] for y in ty]; n = len(ty); nv = sv
        a, p = np.array(act), np.array(preds)
        c = float(np.corrcoef(a,p)[0,1]) if np.std(a)>0 and np.std(p)>0 and len(a)>2 else 0
        m = float(np.mean(np.abs(a-p))); nm = float(np.mean(np.abs(a-nv)))
        b = sum(1 for pi,ai in zip(preds,act) if abs(pi-ai)<abs(nv-ai))/n*100
        x = sum(1 for pi,ai in zip(preds,act) if 1/2<=max(pi,.1)/max(ai,.1)<=2)/n*100
        dm, dt = 0, 0
        for i in range(1, n):
            if np.sign(act[i]-act[i-1]) != 0:
                dt += 1
                if np.sign(preds[i]-preds[i-1]) == np.sign(act[i]-act[i-1]): dm += 1
        d = dm/max(dt,1)*100
        results.append({'cutoff':cutoff, 'corr':c, 'beats':b, 'x2':x, 'dir':d,
                        'mae':m, 'naive_mae':nm, 'preds':preds[:18], 'act':act[:18],
                        'yrs':ty[:18], 'naive':nv, 'ph':ph})
    return results

def score_and_report(sr, er, label, verbose=False):
    s = 0; li = []
    ac = np.mean([r['corr'] for r in sr]); p = ac > 0.3; s += p
    li.append(f"SSNc={ac:+.2f}{'✓' if p else '✗'}")
    bn = sum(1 for r in sr if r['beats'] > 50); p = bn >= 3; s += p
    li.append(f"bn={bn}{'✓' if p else '✗'}")
    ax = np.mean([r['x2'] for r in sr]); p = ax > 30; s += p
    li.append(f"×2={ax:.0f}%{'✓' if p else '✗'}")
    ad = np.mean([r['dir'] for r in sr]); p = ad > 55; s += p
    li.append(f"dir={ad:.0f}%{'✓' if p else '✗'}")
    ec = np.mean([r['corr'] for r in er]); p = ec > 0.2; s += p
    li.append(f"EQc={ec:+.2f}{'✓' if p else '✗'}")
    ex = np.mean([r['x2'] for r in er]); p = ex > 30; s += p
    li.append(f"EQ×2={ex:.0f}%{'✓' if p else '✗'}")
    bm = sum(1 for r in sr if r['mae'] < r['naive_mae']); p = bm >= 3; s += p
    li.append(f"MAE={bm}{'✓' if p else '✗'}")
    nb = all(r['mae'] < 500 for r in sr); p = nb; s += p
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
    return s, ac

if __name__ == '__main__':
    ssn = load_ssn(); eq = load_eq()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

    print("="*70)
    print("π-LEAK ON φ-PATH WITH CLOCK SAMPLING")
    print(f"Golden angle = {GOLDEN_ANGLE:.5f} rad = {np.degrees(GOLDEN_ANGLE):.3f}°")
    print(f"Period of sin(GA×t): {2*np.pi/GOLDEN_ANGLE:.2f} years (irrational!)")
    print("="*70)

    all_scores = {}
    best_corr = -999; best_label = ""

    def test(label, fn):
        global best_corr, best_label
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        s, ac = score_and_report(sr, er, label)
        all_scores[label] = s
        if ac > best_corr: best_corr = ac; best_label = label

    print(f"\n--- V1: Basic π-on-φ-path ---")
    for s in [0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0]:
        test(f"V1 scale={s}", make_pi_phi_path(s))

    print(f"\n--- V2: π-on-φ with R_matter wave ---")
    for s in [0.1, 0.2, 0.5, 1.0, 2.0]:
        test(f"V2 R-wave={s}", make_pi_phi_R(s))

    print(f"\n--- V3: π-on-φ with Hale envelope ---")
    for s in [0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0]:
        test(f"V3 hale-env={s}", make_pi_phi_hale(s))

    print(f"\n--- V4: π-on-φ + soft floor ---")
    for s in [0.5, 1.0, 2.0, 3.0]:
        for fo in [0.5, 0.8, 1.0]:
            test(f"V4 s={s} f={fo}", make_pi_phi_floor(s, fo))

    print(f"\n--- V5: φ-stable π-leak ---")
    for s in [0.5, 1.0, 2.0, 5.0]:
        test(f"V5 φ-stable={s}", make_pi_phi_stable(s))

    print(f"\n--- V6: Dual leak (π-on-φ + φ-on-π) ---")
    for ps in [0.5, 1.0, 2.0]:
        for fs in [0.01, 0.02, 0.05]:
            test(f"V6 π={ps} φ={fs}", make_dual_leak(ps, fs))

    print(f"\n--- V9: π-on-φ as step modulation ---")
    for s in [0.1, 0.2, 0.5, 1.0, 2.0]:
        test(f"V9 step-mod={s}", make_pi_phi_step(s))

    print(f"\n{'='*70}")
    print("TOP RESULTS")
    print("="*70)
    print(f"  Previous best:     7/8  (Script 178)")
    print(f"  Best SSN corr:     {best_corr:+.3f} ({best_label})")
    for label, s in sorted(all_scores.items(), key=lambda x: -x[1])[:15]:
        m = " ★★★ 8/8!" if s == 8 else " ★ NEW BEST" if s > 7 else " ← ties 7" if s == 7 else ""
        print(f"  190 {label}: {s}/8{m}")

    print(f"\nScript 190 complete.")
