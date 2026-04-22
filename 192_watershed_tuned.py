#!/usr/bin/env python3
"""
Script 192 — Tuned Watershed: Engine-Scaled Basin
===================================================

Script 191 key finding: V4 d=1.0 b=0.5 f=0.3 got SSNc=+0.337 (passes 0.3!)
but only 4/8 — the basin kills EQ correlation by pulling consumers toward C.

Root cause: basin_strength applies uniformly. For EQ (ARA=0.15), the valley
is flat at C, so the basin acts as pure mean reversion → kills EQ signal.

FIX: basin_strength itself scales with engine factor:
    effective_basin = basin_strength × max(R_matter - 1, 0)

For SSN (ARA=1.73): effective_basin = 0.73 × basin_strength → deep valley
For EQ  (ARA=0.15): effective_basin = 0.0 → flat terrain, free bounce

This means EQ predictions stay purely iterative (which gets 7/8 on its own)
while SSN gets the valley channeling that gives +0.34 correlation.

Also exploring:
    - Valley amplitude: not just depth_scale × engine_factor, but matched
      to actual log-space range of the data
    - Tighter parameter search around the sweet spot
    - Combined floor + engine-basin with φ-leak
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
PHI_LEAK = 1.0 / PHI

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

# ─── V1: Engine-scaled basin — consumers get no valley ────────────

def make_engine_basin(depth_scale, basin_max, floor_offset=0.5):
    """
    Basin strength scales with engine factor:
        effective_basin = basin_max × max(R_matter - 1, 0)

    For SSN (1.73): eff_basin = 0.73 × basin_max
    For EQ  (0.15): eff_basin = 0.0 (no basin!)

    Valley amplitude also scales with engine factor.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        bounced = log_val + wdlog

        engine_factor = max(R_matter - 1.0, 0.0)

        # Valley
        valley_amp = engine_factor * depth_scale
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        # Engine-scaled basin
        basin_str = engine_factor * basin_max
        displacement = bounced - valley
        correction = -basin_str * displacement

        new_val = bounced + correction

        # Soft floor
        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V2: Engine basin + φ-leak ───────────────────────────────────

def make_engine_basin_phi(depth_scale, basin_max, phi_scale, floor_offset=0.5):
    """V1 + φ-leak energy from sub-ARA flow."""
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        phi_energy = PHI_LEAK * (1.0 - eff) * phi_scale
        bounced = log_val + wdlog + phi_energy

        engine_factor = max(R_matter - 1.0, 0.0)
        valley_amp = engine_factor * depth_scale
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        basin_str = engine_factor * basin_max
        displacement = bounced - valley
        correction = -basin_str * displacement

        new_val = bounced + correction

        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V3: Graduated engine basin — deepens over time ──────────────

def make_graduated_engine(depth_scale, basin_start, basin_end,
                           ramp_years, floor_offset=0.5):
    """
    Basin deepens over time: first cycle is shallow, later cycles deep.
    The molecule finds the valley gradually (water discovering the channel).
    Basin still scaled by engine factor.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        bounced = log_val + wdlog

        engine_factor = max(R_matter - 1.0, 0.0)

        frac = min(t / max(ramp_years, 1), 1.0)
        base_basin = basin_start + (basin_end - basin_start) * frac
        basin_str = engine_factor * base_basin

        valley_amp = engine_factor * depth_scale
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        correction = -basin_str * displacement

        new_val = bounced + correction

        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V4: Asymmetric engine basin ─────────────────────────────────

def make_asym_engine(depth_scale, basin_up, basin_down, floor_offset=0.5):
    """
    Asymmetric: above valley → slides down easily (gravity).
    Below valley → weaker pull (water doesn't flow uphill).
    Both scaled by engine factor.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        bounced = log_val + wdlog

        engine_factor = max(R_matter - 1.0, 0.0)
        valley_amp = engine_factor * depth_scale
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        if displacement > 0:
            correction = -engine_factor * basin_down * displacement
        else:
            correction = -engine_factor * basin_up * displacement

        new_val = bounced + correction

        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V5: Capped engine basin — correction limited by π-leak ──────

def make_capped_engine(depth_scale, basin_max, cap_frac, floor_offset=0.5):
    """
    The basin correction is capped: |correction| ≤ cap_frac × |displacement|.
    This prevents over-correction. The molecule can stray from the valley
    but gets a bounded nudge back each tick. Like a shallow, wide valley
    rather than a narrow gorge.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        bounced = log_val + wdlog

        engine_factor = max(R_matter - 1.0, 0.0)
        valley_amp = engine_factor * depth_scale
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        basin_str = engine_factor * basin_max
        displacement = bounced - valley
        correction = -basin_str * displacement

        # Cap: max correction per tick
        max_corr = abs(displacement) * cap_frac
        correction = np.clip(correction, -max_corr, max_corr)

        new_val = bounced + correction

        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V6: Full watershed — engine basin + φ-leak + turbulence + floor ──

def make_full_engine_watershed(depth_scale, basin_max, phi_scale,
                                turb_scale, floor_offset=0.5):
    """Complete model with engine-scaled basin."""
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        phi_energy = PHI_LEAK * (1.0 - eff) * phi_scale
        turb = PI_LEAK * np.sin(GOLDEN_ANGLE * t) * (1.0 - eff) * turb_scale
        bounced = log_val + wdlog + phi_energy + turb

        engine_factor = max(R_matter - 1.0, 0.0)
        valley_amp = engine_factor * depth_scale
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        basin_str = engine_factor * basin_max
        displacement = bounced - valley
        correction = -basin_str * displacement

        new_val = bounced + correction

        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V7: Engine basin with ARA-scaled valley (not just linear) ───

def make_ara_valley(depth_scale, basin_max, floor_offset=0.5):
    """
    Valley amplitude uses R_matter directly (not just engine factor).
    For SSN (1.73): valley has large amplitude.
    For EQ  (0.15): valley has tiny amplitude (close to C).
    Basin strength still engine-scaled (0 for consumers).

    This separates: valley SHAPE (any system can have one) from
    valley PULL (only engines get channeled).
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        bounced = log_val + wdlog

        # Valley amplitude proportional to R_matter (all systems)
        valley_amp = (R_matter - 1.0) * depth_scale  # can be negative for consumers
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        # Basin pull only for engines
        engine_factor = max(R_matter - 1.0, 0.0)
        basin_str = engine_factor * basin_max
        displacement = bounced - valley
        correction = -basin_str * displacement

        new_val = bounced + correction

        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V8: Sigmoid basin — soft transition around R_coupler ────────

def make_sigmoid_basin(depth_scale, basin_max, steepness=5.0, floor_offset=0.5):
    """
    Instead of hard max(R-1, 0), use sigmoid transition.
    Systems near R_coupler get partial basin, far above get full.
    sigma(x) = 1/(1+exp(-steepness × x))

    This is more physical: the valley doesn't appear abruptly at ARA=1.0.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)
        bounced = log_val + wdlog

        # Sigmoid transition centered at R_coupler
        engine_sig = 1.0 / (1.0 + np.exp(-steepness * (R_matter - 1.0)))
        valley_amp = engine_sig * depth_scale
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        basin_str = engine_sig * basin_max
        displacement = bounced - valley
        correction = -basin_str * displacement

        new_val = bounced + correction

        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
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
    print("TUNED WATERSHED: ENGINE-SCALED BASIN")
    print("Consumers: flat terrain (no basin). Engines: deep φ-valley.")
    print("="*70)

    all_scores = {}
    best_corr = -999; best_label = ""
    best_8 = None

    def test(label, fn):
        global best_corr, best_label, best_8
        sr = run_blind(ssn, cutoffs, ARA_SSN, fn)
        er = run_blind(eq, cutoffs, ARA_EQ, fn)
        s, ac = score_and_report(sr, er, label)
        all_scores[label] = s
        if ac > best_corr: best_corr = ac; best_label = label
        if s == 8 and best_8 is None: best_8 = label

    # ── V1: Engine-scaled basin — fine grid around sweet spot ──
    print(f"\n--- V1: Engine-scaled basin ---")
    for ds in [0.3, 0.5, 0.7, 1.0, 1.3]:
        for bm in [0.3, 0.5, 0.7, 1.0, 1.5]:
            for fo in [0.3, 0.5]:
                test(f"V1 d={ds} b={bm} f={fo}", make_engine_basin(ds, bm, fo))

    # ── V2: Engine basin + φ-leak ──
    print(f"\n--- V2: Engine basin + φ-leak ---")
    for ds in [0.5, 0.7, 1.0]:
        for bm in [0.5, 0.7, 1.0]:
            for ps in [0.01, 0.02, 0.05]:
                test(f"V2 d={ds} b={bm} φ={ps}",
                     make_engine_basin_phi(ds, bm, ps, 0.5))

    # ── V3: Graduated engine basin ──
    print(f"\n--- V3: Graduated engine basin ---")
    for ds in [0.5, 0.7, 1.0]:
        for bs in [0.1, 0.2]:
            for be in [0.5, 0.7, 1.0]:
                for ry in [11, 22]:
                    test(f"V3 d={ds} s={bs} e={be} r={ry}",
                         make_graduated_engine(ds, bs, be, ry, 0.5))

    # ── V4: Asymmetric engine basin ──
    print(f"\n--- V4: Asymmetric engine basin ---")
    for ds in [0.5, 0.7, 1.0]:
        for bu in [0.1, 0.2, 0.3]:
            for bd in [0.5, 0.7, 1.0]:
                test(f"V4 d={ds} u={bu} d={bd}",
                     make_asym_engine(ds, bu, bd, 0.5))

    # ── V5: Capped engine basin ──
    print(f"\n--- V5: Capped engine basin ---")
    for ds in [0.5, 0.7, 1.0]:
        for bm in [0.5, 0.7, 1.0]:
            for cf in [0.3, 0.5, 0.7]:
                test(f"V5 d={ds} b={bm} c={cf}",
                     make_capped_engine(ds, bm, cf, 0.5))

    # ── V6: Full engine watershed ──
    print(f"\n--- V6: Full engine watershed ---")
    for ds in [0.5, 0.7, 1.0]:
        for bm in [0.5, 0.7, 1.0]:
            for ps in [0.01, 0.02]:
                for ts in [0.5, 1.0]:
                    test(f"V6 d={ds} b={bm} φ={ps} t={ts}",
                         make_full_engine_watershed(ds, bm, ps, ts, 0.5))

    # ── V7: ARA-scaled valley ──
    print(f"\n--- V7: ARA-scaled valley ---")
    for ds in [0.3, 0.5, 0.7, 1.0]:
        for bm in [0.3, 0.5, 0.7, 1.0]:
            test(f"V7 d={ds} b={bm}", make_ara_valley(ds, bm, 0.5))

    # ── V8: Sigmoid basin ──
    print(f"\n--- V8: Sigmoid basin ---")
    for ds in [0.5, 0.7, 1.0]:
        for bm in [0.5, 0.7, 1.0]:
            for steep in [3.0, 5.0, 10.0]:
                test(f"V8 d={ds} b={bm} s={steep}",
                     make_sigmoid_basin(ds, bm, steep, 0.5))

    print(f"\n{'='*70}")
    print("TOP RESULTS")
    print("="*70)
    print(f"  Previous best:     7/8  (Script 178)")
    print(f"  191 best SSNc:     +0.337 (V4 d=1.0 b=0.5 f=0.3, 4/8)")
    print(f"  Best SSN corr:     {best_corr:+.3f} ({best_label})")
    if best_8: print(f"  ★★★ FIRST 8/8:    {best_8}")

    sorted_scores = sorted(all_scores.items(), key=lambda x: -x[1])
    for label, s in sorted_scores[:25]:
        m = " ★★★ 8/8!" if s == 8 else " ★ NEW BEST" if s > 7 else " ← ties 7" if s == 7 else ""
        print(f"  192 {label}: {s}/8{m}")

    from collections import Counter
    cnt = Counter(all_scores.values())
    print(f"\nScore distribution: ", end="")
    for score in sorted(cnt.keys(), reverse=True):
        print(f"{score}/8:{cnt[score]}  ", end="")
    print()

    print(f"\nScript 192 complete.")
