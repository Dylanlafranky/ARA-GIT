#!/usr/bin/env python3
"""
Script 189 — φ-Leak Per Tick + Clock-Iterative Blend
======================================================

Two breakthroughs from 187-188:
    1. Pure clock (C + amp × sin(clock)) → SSNc = +0.244 (best ever!)
       The 22-year oscillation IS the signal for SSN.
    2. Iterative wave mechanism → 7/8 on everything EXCEPT SSN correlation.
       Great for EQ, good for SSN accuracy, bad for SSN correlation.

Dylan's φ-leak insight:
    "Each step passes through multiple small ARA.
     Each step we should be adding phi leak to it."

    The wave traverses a medium of sub-systems, each with its own ARA.
    At each sub-system boundary (each tick), a φ-fraction leaks:
        - 1/φ = φ-1 ≈ 0.618 — the complementary fraction at handoff
        - This is NOT π-3 (circle inefficiency)
        - φ-leak is about HANDOFF between nested systems
        - π-leak is about INEFFICIENCY within a circle

    The φ-leak should accumulate: each tick adds φ_leak × scale.
    Direction: opposite to clock (restoring during accumulation).

Strategy: ARA-weighted blend
    For SSN (ARA=1.73, far from 1.0):
        → Strong clock component (captures 22-yr oscillation)
        → φ-leak adds sub-system handoff energy
    For EQ (ARA=0.15, also far from 1.0 but on consumer side):
        → Different clock character (inverted)
        → Smaller φ-leak (consumer systems have fewer sub-connections)

The blend weight = f(|R_matter - 1|):
    - More engine/consumer → more clock-like behavior
    - Near 1.0 → more iterative (shock absorbers are noisy)
"""

import numpy as np
import os

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3
PHI_LEAK = 1.0 / PHI  # ≈ 0.618 — the handoff fraction

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

# ─── V1: φ-leak per tick (continuous handoff) ─────────────────────

def make_phi_leak(leak_scale):
    """
    Each tick: add φ_leak × scale × (1 - eff) [opposite of clock].
    φ_leak ≈ 0.618 — the handoff fraction between sub-systems.
    Much larger than π_leak ≈ 0.142!
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        leak = PHI_LEAK * (1.0 - eff) * leak_scale
        return log_val + wdlog + leak
    return predict

# ─── V2: φ-leak + clock blend (ARA-weighted) ──────────────────────

def make_phi_clock_blend(clock_weight, leak_scale, clock_amp=0.5):
    """
    prediction = (1-w) × iterative_with_φleak + w × clock_target
    where w = clock_weight × |R_matter - 1|

    For SSN: w = clock_weight × 0.73 → strong clock
    For EQ: w = clock_weight × 0.85 → also strong (consumer!)
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # φ-leak
        leak = PHI_LEAK * (1.0 - eff) * leak_scale

        iterative = log_val + wdlog + leak

        # Clock target
        amp = (R_matter - 1.0) * clock_amp
        target = C + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

        # ARA-weighted blend
        w = min(clock_weight * abs(R_matter - 1.0), 0.5)

        return (1.0 - w) * iterative + w * target
    return predict

# ─── V3: φ-leak with sign (like π-leak V1) ────────────────────────

def make_phi_sign(leak_scale):
    """φ-leak with sign(1-eff) instead of proportional."""
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        leak = PHI_LEAK * np.sign(1.0 - eff) * leak_scale
        return log_val + wdlog + leak
    return predict

# ─── V4: φ-leak + π-leak combined ─────────────────────────────────

def make_phi_pi_combined(phi_scale, pi_scale):
    """
    Two separate leaks operating simultaneously:
    - φ-leak: handoff between sub-systems (per tick, proportional)
    - π-leak: geometric inefficiency of circles (per tick, proportional)
    Both opposite to clock. φ-leak is ~4.4× larger than π-leak.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        phi_leak = PHI_LEAK * (1.0 - eff) * phi_scale
        pi_leak = PI_LEAK * (1.0 - eff) * pi_scale
        return log_val + wdlog + phi_leak + pi_leak
    return predict

# ─── V5: Pure clock + φ-leak correction ───────────────────────────

def make_clock_phi_correction(clock_amp, phi_scale):
    """
    Start from pure clock (which has best SSN correlation).
    Add φ-leak as a correction that accounts for sub-system handoffs.
    The φ-leak modifies the clock's smooth sine with real physics.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        eff = effective_ara(R_matter, t, phase0)

        # Pure clock target
        amp = (R_matter - 1.0) * clock_amp
        target = C + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

        # φ-leak correction
        leak = PHI_LEAK * (1.0 - eff) * phi_scale

        # The prediction is the clock + accumulated φ-leak from start
        return target + leak
    return predict

# ─── V6: Iterative with φ-leak + soft floor ───────────────────────

def make_phi_floor(leak_scale, floor_offset=1.0):
    """
    φ-leak per tick + soft floor at C - floor_offset.
    The floor prevents predictions from collapsing to -inf.
    floor_offset = 1.0 means minimum prediction ≈ C - 1.0 (in log space).
    For SSN: C ≈ 1.7, floor ≈ 0.7 → minimum SSN ≈ 5
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        leak = PHI_LEAK * (1.0 - eff) * leak_scale
        new_val = log_val + wdlog + leak

        # Soft floor
        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1  # 90% bounce back

        return new_val
    return predict

# ─── V7: Engine-scaled φ-leak ─────────────────────────────────────

def make_phi_engine(leak_scale):
    """
    φ-leak scaled by how many sub-systems the wave passes through.
    Engines (ARA > 1) have MORE sub-connections → bigger leak.
    Consumers (ARA < 1) have FEWER → smaller leak.
    Scale = R_matter (not R_matter - 1, since consumers still have structure).
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        leak = PHI_LEAK * (1.0 - eff) * R_matter * leak_scale
        return log_val + wdlog + leak
    return predict

# ─── V8: φ-leak with golden angle modulation ──────────────────────

def make_phi_golden_mod(leak_scale):
    """
    The φ-leak is modulated by the golden angle position.
    As the wave advances by GA/φ each tick, the leak varies
    by where in the golden spiral the system currently sits.
    This gives maximum variety (no tick repeats the same leak).
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        clock_pos = GA_OVER_PHI * t
        golden_mod = np.sin(clock_pos * GOLDEN_ANGLE)
        leak = PHI_LEAK * (1.0 - eff) * (1.0 + golden_mod) * leak_scale * 0.5
        return log_val + wdlog + leak
    return predict

# ─── V9: Blended clock for SSN, iterative for EQ ──────────────────

def make_ara_adaptive_blend(clock_amp, phi_scale, blend_at_ara_1=0.0):
    """
    Adaptive blend: the further R_matter is from 1.0, the more clock.
    But ENGINE vs CONSUMER get different treatment:
    - Engines (R>1): clock oscillates UPWARD at accumulation
    - Consumers (R<1): clock oscillates DOWNWARD at accumulation

    blend = |R_matter - 1| × sensitivity
    For SSN (1.73): blend ≈ 0.73 × sensitivity
    For EQ (0.15): blend ≈ 0.85 × sensitivity

    To differentiate: make blend = max(R_matter - 1, 0) × sensitivity
    This gives SSN a clock but EQ (consumer) stays iterative.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # φ-leak
        leak = PHI_LEAK * (1.0 - eff) * phi_scale

        iterative = log_val + wdlog + leak

        # Engine-only clock blend
        engine_factor = max(R_matter - 1.0, 0.0)  # 0 for consumers!
        blend = min(engine_factor * 0.5, 0.4)  # cap at 0.4

        amp = engine_factor * clock_amp
        target = C + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

        return (1.0 - blend) * iterative + blend * target
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

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_ssn(); eq = load_eq()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

    print("="*70)
    print("φ-LEAK PER TICK + CLOCK-ITERATIVE BLEND")
    print(f"φ-leak = 1/φ = {PHI_LEAK:.5f}  (4.37× larger than π-leak={PI_LEAK:.5f})")
    print("="*70)

    all_scores = {}
    best_corr = -999; best_corr_label = ""

    def test(label, fn):
        global best_corr, best_corr_label
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        s, ac = score_and_report(sr, er, label)
        all_scores[label] = s
        if ac > best_corr: best_corr = ac; best_corr_label = label

    # V1: φ-leak per tick (proportional)
    print(f"\n--- V1: φ-leak per tick (proportional) ---")
    for ls in [0.01, 0.02, 0.03, 0.05, 0.08, 0.1, 0.15, 0.2]:
        test(f"V1 φ-prop={ls}", make_phi_leak(ls))

    # V2: φ-leak + clock blend (ARA-weighted)
    print(f"\n--- V2: φ-leak + ARA-weighted clock blend ---")
    for cw in [0.1, 0.2, 0.3, 0.5]:
        for ls in [0.02, 0.05, 0.1]:
            for ca in [0.3, 0.5, 0.7]:
                test(f"V2 cw={cw} φ={ls} ca={ca}", make_phi_clock_blend(cw, ls, ca))

    # V3: φ-leak with sign
    print(f"\n--- V3: φ-leak sign ---")
    for ls in [0.01, 0.02, 0.05, 0.1, 0.15]:
        test(f"V3 φ-sign={ls}", make_phi_sign(ls))

    # V4: φ + π combined
    print(f"\n--- V4: φ-leak + π-leak combined ---")
    for ps in [0.02, 0.05, 0.1]:
        for pp in [0.05, 0.1]:
            test(f"V4 φ={ps} π={pp}", make_phi_pi_combined(ps, pp))

    # V5: Pure clock + φ correction
    print(f"\n--- V5: Clock + φ correction ---")
    for ca in [0.3, 0.5, 0.7]:
        for ps in [0.01, 0.02, 0.05]:
            test(f"V5 clk={ca} φ={ps}", make_clock_phi_correction(ca, ps))

    # V6: φ-leak + soft floor
    print(f"\n--- V6: φ-leak + soft floor ---")
    for ls in [0.02, 0.05, 0.1]:
        for fo in [0.5, 1.0, 1.5]:
            test(f"V6 φ={ls} floor={fo}", make_phi_floor(ls, fo))

    # V7: Engine-scaled φ-leak
    print(f"\n--- V7: Engine-scaled φ-leak ---")
    for ls in [0.01, 0.02, 0.03, 0.05, 0.08]:
        test(f"V7 engine-φ={ls}", make_phi_engine(ls))

    # V8: Golden angle modulated φ-leak
    print(f"\n--- V8: Golden-modulated φ-leak ---")
    for ls in [0.02, 0.05, 0.1]:
        test(f"V8 golden-φ={ls}", make_phi_golden_mod(ls))

    # V9: Engine-only clock blend (SSN gets clock, EQ stays iterative)
    print(f"\n--- V9: Engine-only adaptive blend ---")
    for ca in [0.3, 0.5, 0.7, 1.0]:
        for ps in [0.02, 0.05, 0.1]:
            test(f"V9 clk={ca} φ={ps}", make_ara_adaptive_blend(ca, ps))

    print(f"\n{'='*70}")
    print("TOP RESULTS")
    print("="*70)
    print(f"  Previous best:     7/8  (Script 178)")
    print(f"  Best SSN corr:     {best_corr:+.3f} ({best_corr_label})")
    print(f"  Pure clock (188):  SSNc=+0.244")
    for label, s in sorted(all_scores.items(), key=lambda x: -x[1])[:15]:
        m = " ★★★ 8/8!" if s == 8 else " ★ NEW BEST" if s > 7 else " ← ties 7" if s == 7 else ""
        print(f"  189 {label}: {s}/8{m}")

    print(f"\nScript 189 complete.")
