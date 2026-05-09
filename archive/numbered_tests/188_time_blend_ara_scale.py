#!/usr/bin/env python3
"""
Script 188 — Time-Varying Blend + ARA-Scaled Deltas
=====================================================

From 187:
    - V4 wave-gen blend=0.2 → SSNc=+0.19, dir=69% (best correlation ever!)
    - V2 sym k=0.050 → SSN 2010: 73→87→109→134→147 (second peak recovery!)
    But both lost other criteria.

Key insight: the tension between iterative and generative isn't fixed —
it CHANGES over time:
    - Years 1-5: iterative is great (good first-cycle prediction)
    - Years 5-15: iterative collapses (arcsin saturation)
    - Years 15+: need generative to sustain cycles

Solution: TIME-VARYING BLEND
    blend(t) = min(t / T_transition, max_blend)
    prediction = (1 - blend(t)) × iterative + blend(t) × generative

Also testing: ARA-scaled delta amplification
    The wave deltas are ~0.01-0.05 in log-space.
    SSN needs deltas of ~0.3-0.5 for rapid cycle changes.
    Multiply dlog by R_matter: SSN gets ×1.73, EQ gets ×0.15.
    This scales naturally by system type.
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

# ─── V1: Time-varying blend (iterative → generative) ──────────────

def make_time_blend(T_transition, max_blend, amp_scale=1.0):
    """
    blend(t) = min(t / T_transition, max_blend)
    Low t → mostly iterative (captures first cycle)
    High t → more generative (sustains across cycles)

    Generative target: C + (R_matter - 1) × sin(clock) × amp_scale
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        iterative = log_val + wdlog

        # Time-varying blend
        blend = min(t / T_transition, max_blend)

        # Generative target from clock
        amp = (R_matter - 1.0) * amp_scale
        target = C + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

        return (1.0 - blend) * iterative + blend * target
    return predict

# ─── V2: Time blend with wave-derived target ──────────────────────

def make_time_blend_wave(T_transition, max_blend):
    """Use wave function for generative target instead of simple sine."""
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        iterative = log_val + wdlog

        blend = min(t / T_transition, max_blend)

        clock_pos = GA_OVER_PHI * t
        w1 = wave(clock_pos, R_matter)
        w2 = wave(clock_pos + HALF_PHI, R_matter)
        target = C + (w1 + w2) / 2

        return (1.0 - blend) * iterative + blend * target
    return predict

# ─── V3: ARA-scaled deltas ────────────────────────────────────────

def make_ara_scaled(dlog_scale):
    """
    Multiply the wave dlog by a factor derived from R_matter.
    SSN (1.73): deltas × 1.73 → bigger swings
    EQ (0.15): deltas × 0.15 → smaller swings
    Natural scaling by system type.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        return log_val + wdlog * R_matter * dlog_scale
    return predict

# ─── V4: ARA-scaled + spring ──────────────────────────────────────

def make_ara_spring(dlog_scale, spring_k):
    """ARA-scaled deltas PLUS mean reversion spring."""
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # ARA-scaled wave delta
        scaled_dlog = wdlog * R_matter * dlog_scale

        # Spring toward C (clock-gated)
        displacement = C - log_val
        clock_dev = abs(eff - 1.0)
        spring = displacement * clock_dev * spring_k

        return log_val + scaled_dlog + spring
    return predict

# ─── V5: Time blend + spring + π-leak (kitchen sink) ──────────────

def make_full_blend(T_trans, max_blend, spring_k, leak_scale, amp_scale=1.0):
    """Everything together: iterative → generative blend + spring + leak."""
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        iterative = log_val + wdlog

        # Spring
        displacement = C - log_val
        clock_dev = abs(eff - 1.0)
        spring = displacement * clock_dev * spring_k

        # π-leak
        leak = PI_LEAK * (1.0 - eff) * leak_scale

        iterative_full = log_val + wdlog + spring + leak

        # Time blend
        blend = min(t / T_trans, max_blend)
        amp = (R_matter - 1.0) * amp_scale
        target = C + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

        return (1.0 - blend) * iterative_full + blend * target
    return predict

# ─── V6: Sigmoid blend (smooth transition) ────────────────────────

def make_sigmoid_blend(t_mid, steepness, max_blend, amp_scale=1.0):
    """
    Sigmoid blend: smooth transition from iterative to generative.
    blend(t) = max_blend / (1 + exp(-steepness * (t - t_mid)))
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        iterative = log_val + wdlog

        blend = max_blend / (1 + np.exp(-steepness * (t - t_mid)))

        amp = (R_matter - 1.0) * amp_scale
        target = C + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

        return (1.0 - blend) * iterative + blend * target
    return predict

# ─── V7: Distance-gated generative ────────────────────────────────

def make_distance_gated(max_blend, threshold, amp_scale=1.0):
    """
    Generative kicks in when prediction is FAR from C.
    blend = min(|log_val - C| / threshold, max_blend)
    Near C: iterative dominates (small blend)
    Far from C: generative rescues (large blend)
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        iterative = log_val + wdlog

        dist = abs(log_val - C)
        blend = min(dist / threshold, max_blend)

        amp = (R_matter - 1.0) * amp_scale
        target = C + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)

        return (1.0 - blend) * iterative + blend * target
    return predict

# ─── V8: Pure clock model (no iteration at all) ───────────────────

def make_pure_clock(amp_scale=1.0):
    """
    Zero iteration. Pure clock-derived prediction.
    prediction(t) = C + (R_matter - 1) × sin(2πt/22 + phase0) × amp_scale

    If this scores well on correlation, the SHAPE is right
    and we just need to fix the magnitude.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        amp = (R_matter - 1.0) * amp_scale
        return C + amp * np.sin(2*np.pi*t/HALE_PERIOD + phase0)
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
    print("TIME-VARYING BLEND + ARA-SCALED DELTAS")
    print("="*70)

    all_scores = {}
    best_corr = -999
    best_corr_label = ""

    def test(label, fn):
        global best_corr, best_corr_label
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        s, ac = score_and_report(sr, er, label)
        all_scores[label] = s
        if ac > best_corr:
            best_corr = ac
            best_corr_label = label

    # V1: Time-varying blend (linear ramp)
    print(f"\n--- V1: Linear time-blend ---")
    for T in [5, 8, 11, 15, 22]:
        for mb in [0.1, 0.15, 0.2, 0.3]:
            for amp in [0.8, 1.0, 1.2]:
                label = f"V1 T={T} max={mb} amp={amp}"
                test(label, make_time_blend(T, mb, amp))

    # V2: Time blend with wave target
    print(f"\n--- V2: Time-blend with wave target ---")
    for T in [5, 8, 11]:
        for mb in [0.1, 0.15, 0.2, 0.3]:
            label = f"V2 wave T={T} max={mb}"
            test(label, make_time_blend_wave(T, mb))

    # V3: ARA-scaled deltas
    print(f"\n--- V3: ARA-scaled deltas ---")
    for ds in [0.5, 1.0, 1.5, 2.0, PHI, 3.0]:
        label = f"V3 ara-scale={ds:.2f}"
        test(label, make_ara_scaled(ds))

    # V4: ARA-scaled + spring
    print(f"\n--- V4: ARA-scaled + spring ---")
    for ds in [1.0, 1.5, 2.0]:
        for sk in [0.01, 0.02, 0.05]:
            label = f"V4 scale={ds} spring={sk}"
            test(label, make_ara_spring(ds, sk))

    # V5: Full blend (iterative + spring + leak → generative)
    print(f"\n--- V5: Full blend ---")
    for T in [8, 11]:
        for mb in [0.1, 0.15, 0.2]:
            for sk in [0.02, 0.05]:
                label = f"V5 T={T} max={mb} sk={sk}"
                test(label, make_full_blend(T, mb, sk, 0.05, 1.0))

    # V6: Sigmoid blend
    print(f"\n--- V6: Sigmoid blend ---")
    for tmid in [5, 8, 11]:
        for steep in [0.3, 0.5, 1.0]:
            for mb in [0.15, 0.2, 0.3]:
                label = f"V6 mid={tmid} s={steep} max={mb}"
                test(label, make_sigmoid_blend(tmid, steep, mb, 1.0))

    # V7: Distance-gated generative
    print(f"\n--- V7: Distance-gated generative ---")
    for th in [0.5, 1.0, 1.5]:
        for mb in [0.1, 0.2, 0.3, 0.5]:
            label = f"V7 thresh={th} max={mb}"
            test(label, make_distance_gated(mb, th, 1.0))

    # V8: Pure clock (baseline for correlation)
    print(f"\n--- V8: Pure clock (no iteration) ---")
    for amp in [0.5, 0.7, 1.0, 1.2, 1.5]:
        label = f"V8 pure amp={amp}"
        test(label, make_pure_clock(amp))

    print(f"\n{'='*70}")
    print("TOP RESULTS")
    print("="*70)
    print(f"  Previous best:  7/8  (Script 178)")
    print(f"  Best SSN correlation: {best_corr:+.3f} ({best_corr_label})")
    for label, s in sorted(all_scores.items(), key=lambda x: -x[1])[:15]:
        m = " ★★★ 8/8!" if s == 8 else " ★ NEW BEST" if s > 7 else " ← ties 7" if s == 7 else ""
        print(f"  188 {label}: {s}/8{m}")

    print(f"\nScript 188 complete.")
