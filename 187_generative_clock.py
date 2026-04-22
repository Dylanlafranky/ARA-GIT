#!/usr/bin/env python3
"""
Script 187 — Generative Clock + Mean Reversion
================================================

The iterative problem:
    x(t+1) = x(t) + dlog(x(t), t)
    When x(t) drifts, dlog(x(t)) gets worse → spiral collapse.
    After one solar cycle, predictions lock to zero and never recover.

The fix: add a NON-ITERATIVE generative term.
    The Hale clock KNOWS the cycle shape independently.
    It can say "at this phase, the system should be near C + offset"
    without caring where the prediction was last year.

Three approaches:
    A) Clock-generated target: predict = iterative + pull_toward(clock_target)
    B) Mean reversion spring: pull toward C proportional to distance
    C) Blended: iterative for within-cycle, generative for cross-cycle

The clock target for SSN:
    - At peak accumulation (eff ≈ 1.73): target = C + amplitude
    - At peak discharge (eff ≈ 0.27): target = C - amplitude
    - amplitude derived from wave at clock position × ARA

The mean reversion:
    - When far below C during accumulation: strong pull UP
    - When far above C during discharge: strong pull DOWN
    - Spring constant = PI_LEAK (geometry gives the rate)

Also testing: the connection-snapping idea.
    When crossing a log boundary, the impulse should scale with
    the VALUE at the crossing point (10^log_level), not just PI_LEAK.
    Higher log levels have more connections → bigger snap.
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
    """The 178 wave mechanism — returns (wave_dlog, eff)."""
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

# ─── V1: Mean Reversion Spring ────────────────────────────────────

def make_spring(spring_k):
    """
    Mean reversion: pull toward C proportional to distance × clock opposition.
    Spring fires during accumulation (eff < 1): pulls UP toward C.
    Spring fires during discharge (eff > 1): lets go / pushes away.

    spring_k = PI_LEAK means the spring constant = geometric inefficiency.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # Spring: pull toward C when accumulating
        displacement = C - log_val  # positive when below C
        clock_gate = max(1.0 - eff, 0)  # positive during accumulation, 0 during discharge
        spring = displacement * clock_gate * spring_k

        return log_val + wdlog + spring
    return predict

# ─── V2: Symmetric Spring (both directions) ───────────────────────

def make_spring_sym(spring_k):
    """
    Spring pulls toward C in BOTH phases:
    - Accumulation (eff < 1): pull up from below C
    - Discharge (eff > 1): pull down from above C
    The spring direction is ALWAYS toward C. The strength
    is modulated by how far the clock is from center.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        displacement = C - log_val
        clock_deviation = abs(eff - 1.0)  # 0 at center, max at extremes
        spring = displacement * clock_deviation * spring_k

        return log_val + wdlog + spring
    return predict

# ─── V3: Generative Clock Target ──────────────────────────────────

def make_generative(blend, amplitude_scale):
    """
    The clock generates an expected log level at each time step.
    target(t) = C + amplitude × sin(2πt/22 + phase0)

    The amplitude comes from the ARA: (R_matter - 1.0) × scale.
    For SSN (ARA=1.73): amplitude ≈ 0.73 × scale
    For EQ  (ARA=0.15): amplitude ≈ -0.85 × scale (inverted!)

    The prediction blends iterative and generative:
    x(t+1) = (1-blend) × (x(t) + dlog) + blend × target(t+1)
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        iterative = log_val + wdlog

        # Generative target from clock
        amp = (R_matter - 1.0) * amplitude_scale
        target = C + amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        # Blend
        return (1.0 - blend) * iterative + blend * target
    return predict

# ─── V4: Generative with wave-derived amplitude ───────────────────

def make_generative_wave(blend):
    """
    Instead of a simple sine for the target, use the WAVE function
    evaluated at the clock position. This gives the correct ARA
    geometry (not just a sine).

    target = C + wave(clock_position, R_matter) × scale
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        iterative = log_val + wdlog

        # Clock position advances at golden angle / φ per year
        clock_pos = GA_OVER_PHI * (t + 1)
        # Wave at clock position, using R_matter as radius
        w1 = wave(clock_pos, R_matter)
        w2 = wave(clock_pos + HALF_PHI, R_matter)
        target_offset = (w1 + w2) / 2  # φ-stable average

        target = C + target_offset

        return (1.0 - blend) * iterative + blend * target
    return predict

# ─── V5: Spring + π-leak combined ─────────────────────────────────

def make_spring_leak(spring_k, leak_scale):
    """
    Combines mean reversion spring with continuous π-leak.
    Spring handles the structural pull-back.
    π-leak adds the geometric correction from clock opposition.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # Mean reversion spring (symmetric)
        displacement = C - log_val
        clock_dev = abs(eff - 1.0)
        spring = displacement * clock_dev * spring_k

        # π-leak (proportional, from 184)
        leak = PI_LEAK * (1.0 - eff) * leak_scale

        return log_val + wdlog + spring + leak
    return predict

# ─── V6: Exponential spring (stronger when far) ───────────────────

def make_exp_spring(spring_k):
    """
    Exponential mean reversion: stronger pull when further from C.
    Uses exp(|displacement|) - 1 instead of linear displacement.
    Prevents runaway while allowing natural variation near C.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        displacement = C - log_val
        # Exponential spring: grows faster with distance
        spring_force = np.sign(displacement) * (np.exp(abs(displacement)) - 1.0)
        clock_gate = max(1.0 - eff, 0)  # only during accumulation
        spring = spring_force * clock_gate * spring_k

        return log_val + wdlog + spring
    return predict

# ─── V7: Proportional generative (scale by distance from C) ──────

def make_proportional_gen(gen_scale):
    """
    Generative term proportional to how far prediction is from C.
    When near C: small generative term (wave mechanism dominates).
    When far from C: large generative term (generative rescues).

    gen_force = (C - log_val) × |eff - 1| × gen_scale
    This naturally reverses direction with the clock AND with displacement.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        displacement = C - log_val
        clock_drive = (1.0 - eff)  # positive in accum, negative in discharge
        gen = displacement * clock_drive * gen_scale

        return log_val + wdlog + gen
    return predict

# ─── V8: Clock target with PI_LEAK spring constant ────────────────

def make_pi_spring_target(target_weight):
    """
    The clock says where you SHOULD be.
    The spring constant is PI_LEAK — geometry dictates the pull rate.
    Pull = PI_LEAK × (target - current) per year.

    target(t) = C + (R_matter - 1) × sin(clock) × range_scale
    range_scale calibrated so SSN target oscillates over ~1.5 log units.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # Clock target
        clock_sin = np.sin(2*np.pi*(t)/HALE_PERIOD + phase0)
        # Range: for SSN, (1.73-1)=0.73, want ~0.7 log range → scale ≈ 1.0
        target = C + (R_matter - 1.0) * clock_sin

        # PI_LEAK spring toward target
        pull = PI_LEAK * (target - log_val) * target_weight

        return log_val + wdlog + pull
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
    return s

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_ssn(); eq = load_eq()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

    print("="*70)
    print("GENERATIVE CLOCK + MEAN REVERSION")
    print("="*70)

    all_scores = {}

    # V1: Mean reversion spring (accumulation-gated)
    print(f"\n--- V1: Accumulation-gated spring ---")
    for k in [0.01, 0.02, 0.05, 0.1, PI_LEAK, 0.2, 0.3, 0.5]:
        label = f"V1 spring k={k:.3f}"
        fn = make_spring(k)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    # V2: Symmetric spring
    print(f"\n--- V2: Symmetric spring ---")
    for k in [0.01, 0.02, 0.05, 0.1, PI_LEAK, 0.2, 0.3]:
        label = f"V2 sym k={k:.3f}"
        fn = make_spring_sym(k)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    # V3: Generative clock target (simple sine)
    print(f"\n--- V3: Generative target (sine) ---")
    for blend in [0.05, 0.1, 0.15, 0.2, 0.3, 0.5]:
        for amp in [0.5, 1.0, 1.5]:
            label = f"V3 blend={blend} amp={amp}"
            fn = make_generative(blend, amp)
            sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
            er = run_blind(eq, cutoffs, ARA_EQ, fn)
            all_scores[label] = score_and_report(sr, er, label)

    # V4: Generative with wave-derived target
    print(f"\n--- V4: Generative wave target ---")
    for blend in [0.05, 0.1, 0.15, 0.2, 0.3]:
        label = f"V4 wave-gen blend={blend}"
        fn = make_generative_wave(blend)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    # V5: Spring + π-leak
    print(f"\n--- V5: Spring + π-leak ---")
    for sk in [0.02, 0.05, 0.1]:
        for ls in [0.05, 0.1, 0.2]:
            label = f"V5 spring={sk} leak={ls}"
            fn = make_spring_leak(sk, ls)
            sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
            er = run_blind(eq, cutoffs, ARA_EQ, fn)
            all_scores[label] = score_and_report(sr, er, label)

    # V6: Exponential spring
    print(f"\n--- V6: Exponential spring ---")
    for k in [0.01, 0.02, 0.05, 0.1, PI_LEAK]:
        label = f"V6 exp-spring k={k:.3f}"
        fn = make_exp_spring(k)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    # V7: Proportional generative
    print(f"\n--- V7: Proportional generative ---")
    for gs in [0.01, 0.02, 0.05, 0.1, PI_LEAK, 0.2]:
        label = f"V7 prop-gen scale={gs:.3f}"
        fn = make_proportional_gen(gs)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    # V8: PI_LEAK spring toward clock target
    print(f"\n--- V8: PI_LEAK spring toward clock target ---")
    for tw in [0.5, 1.0, 1.5, 2.0, PHI, 3.0]:
        label = f"V8 π-target w={tw:.2f}"
        fn = make_pi_spring_target(tw)
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        all_scores[label] = score_and_report(sr, er, label)

    print(f"\n{'='*70}")
    print("TOP RESULTS")
    print("="*70)
    print(f"  Previous best:  7/8  (Script 178)")
    for label, s in sorted(all_scores.items(), key=lambda x: -x[1])[:15]:
        m = " ★★★ 8/8!" if s == 8 else " ★ NEW BEST" if s > 7 else " ← ties 7" if s == 7 else ""
        print(f"  187 {label}: {s}/8{m}")

    print(f"\nScript 187 complete.")
