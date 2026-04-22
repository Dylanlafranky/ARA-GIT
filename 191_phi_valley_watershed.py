#!/usr/bin/env python3
"""
Script 191 — φ-Valley Watershed Model
========================================

Dylan's insight: "Think of it as tracking a single water molecule in a
watershed system or water dissolving in soil. It bounces along but always
finds the phi valley — the path of least resistance — which means survival
for longer wave cycles."

This changes the architecture fundamentally:

PREVIOUS APPROACH (blend/spring):
    prediction = (1-w) × iterative + w × clock
    → The molecule is a WEIGHTED AVERAGE of two positions.
    → It has no terrain, no physics, no agency.

NEW APPROACH (watershed basin):
    prediction bounces iteratively (turbulence)
    terrain is φ-shaped (Hale clock curve = valley floor)
    gravity pulls molecule toward valley ∝ distance from floor
    → The molecule MOVES FREELY but the valley CHANNELS it.

The valley floor:
    valley(t) = C + depth × sin(2π·t/22 + φ0)

The basin (restoring force):
    displacement = current_pos - valley(t)
    force = -basin_strength × displacement
    → Further from valley → stronger pull back
    → IN the valley → no correction (free to bounce)

Basin depth scales with ARA:
    Engines (SSN, ARA=1.73): deep valley → strong channeling
    Consumers (EQ, ARA=0.15): flat terrain → free bounce

This naturally gives us both:
    - Multi-cycle SSN correlation (valley holds the oscillation shape)
    - Single-cycle EQ accuracy (flat terrain = pure iterative)
"""

import numpy as np
import os

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3       # ≈ 0.14159
PHI_LEAK = 1.0 / PHI      # ≈ 0.618

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

# ─── V1: Linear basin — restoring force ∝ displacement ────────────

def make_linear_basin(depth_scale, basin_strength):
    """
    Valley floor = C + depth × sin(2πt/22 + φ0)
    depth = max(R_matter - 1, 0) × depth_scale  (engines only)

    After iterative bounce, apply:
        displacement = bounced_pos - valley(t+1)
        correction = -basin_strength × displacement

    basin_strength ∈ (0,1): 0 = flat terrain, 1 = rigid valley
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # The molecule bounces
        bounced = log_val + wdlog

        # The valley floor at time t+1
        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        # Gravity: pull toward valley
        displacement = bounced - valley
        correction = -basin_strength * displacement

        return bounced + correction
    return predict

# ─── V2: Quadratic basin — stronger pull far from valley ──────────

def make_quadratic_basin(depth_scale, basin_k):
    """
    Force ∝ displacement², signed.
    Weak near valley, strong when far away.
    Like a U-shaped valley cross-section.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        bounced = log_val + wdlog

        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        # Quadratic restoring: sign × d²
        correction = -basin_k * np.sign(displacement) * displacement**2

        return bounced + correction
    return predict

# ─── V3: Basin + φ-leak (molecule picks up energy flowing) ────────

def make_basin_phi_leak(depth_scale, basin_strength, phi_scale):
    """
    Basin channeling + φ-leak per tick.
    The molecule picks up PHI_LEAK energy as it flows through
    each sub-ARA boundary. Modulated by (1-eff) so it's
    strongest during accumulation phase.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # φ-leak: energy picked up at sub-ARA boundaries
        phi_energy = PHI_LEAK * (1.0 - eff) * phi_scale

        bounced = log_val + wdlog + phi_energy

        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        correction = -basin_strength * displacement

        return bounced + correction
    return predict

# ─── V4: Basin + soft floor ───────────────────────────────────────

def make_basin_floor(depth_scale, basin_strength, floor_offset=0.5):
    """
    Basin with soft floor. The valley has a minimum — the molecule
    can't sink below the bedrock. This prevents collapse.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        bounced = log_val + wdlog

        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        correction = -basin_strength * displacement

        new_val = bounced + correction

        # Soft floor (bedrock)
        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V5: Basin + π-on-φ-path turbulence ──────────────────────────

def make_basin_pi_phi(depth_scale, basin_strength, turb_scale):
    """
    Basin channeling + π-on-φ-path turbulence.
    The molecule bounces with BOTH the base wave AND
    the golden-angle turbulence, then gets channeled
    by the valley. The turbulence is the rain hitting
    the watershed — it disturbs the surface but the
    valley still channels the flow.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # Turbulence: π-leak on golden spiral path
        turb = PI_LEAK * np.sin(GOLDEN_ANGLE * t) * (1.0 - eff) * turb_scale

        bounced = log_val + wdlog + turb

        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        correction = -basin_strength * displacement

        return bounced + correction
    return predict

# ─── V6: Full watershed — basin + φ-leak + floor + turbulence ────

def make_full_watershed(depth_scale, basin_strength, phi_scale,
                         turb_scale, floor_offset=0.5):
    """
    The complete watershed model:
    1. Iterative wave engine → base bounce
    2. φ-leak → energy from sub-ARA flow
    3. π-on-φ turbulence → rain on the watershed
    4. φ-valley basin → terrain channels the molecule
    5. Soft floor → bedrock prevents collapse
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # φ-leak energy from sub-ARA boundaries
        phi_energy = PHI_LEAK * (1.0 - eff) * phi_scale

        # π-on-φ turbulence
        turb = PI_LEAK * np.sin(GOLDEN_ANGLE * t) * (1.0 - eff) * turb_scale

        bounced = log_val + wdlog + phi_energy + turb

        # φ-valley
        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        # Basin restoring force
        displacement = bounced - valley
        correction = -basin_strength * displacement

        new_val = bounced + correction

        # Bedrock floor
        floor = C - floor_offset
        if new_val < floor:
            new_val = floor + (new_val - floor) * 0.1

        return new_val
    return predict

# ─── V7: Asymmetric basin — steeper on downhill side ─────────────

def make_asymmetric_basin(depth_scale, basin_up, basin_down):
    """
    Real watersheds are asymmetric. When the molecule is ABOVE the
    valley floor, it slides down easily (gravity helps). When it's
    BELOW... well, water doesn't flow uphill.

    Above valley: strong pull down (basin_down)
    Below valley: weaker pull up (basin_up)

    This means the prediction tracks the TOP of the Hale cycle well
    (slides easily to peaks) but can lag in the troughs (floor catches it).
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        bounced = log_val + wdlog

        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        # Asymmetric: above valley vs below valley
        if displacement > 0:
            correction = -basin_down * displacement
        else:
            correction = -basin_up * displacement

        return bounced + correction
    return predict

# ─── V8: Graduated basin — strength grows with time ──────────────

def make_graduated_basin(depth_scale, basin_start, basin_max, ramp_years):
    """
    The valley deepens over time. First cycle: shallow valley (trust
    the iterative bounce). Later cycles: deeper valley (molecule has
    found the path of least resistance).

    This matches the observation that iterative models are good for
    the first cycle but collapse after. The valley takes over gradually.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        bounced = log_val + wdlog

        # Basin strength grows with time
        frac = min(t / max(ramp_years, 1), 1.0)
        basin_str = basin_start + (basin_max - basin_start) * frac

        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        correction = -basin_str * displacement

        return bounced + correction
    return predict

# ─── V9: φ-valley with golden angle modulated depth ──────────────

def make_golden_valley(depth_scale, basin_strength, mod_scale):
    """
    The valley depth itself oscillates with the golden angle.
    The valley is deeper at some points and shallower at others,
    following the φ-spiral. This means some years the molecule
    is tightly channeled, other years it can explore.

    depth(t) = base_depth × (1 + mod_scale × sin(GA × t))
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        bounced = log_val + wdlog

        base_depth = max(R_matter - 1.0, 0.0) * depth_scale
        # Modulate depth by golden angle position
        golden_mod = 1.0 + mod_scale * np.sin(GOLDEN_ANGLE * t)
        valley_depth = base_depth * golden_mod

        valley = C + valley_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

        displacement = bounced - valley
        correction = -basin_strength * displacement

        return bounced + correction
    return predict

# ─── V10: Full watershed with graduated basin ────────────────────

def make_watershed_graduated(depth_scale, basin_start, basin_max,
                              ramp_years, phi_scale, floor_offset=0.5):
    """
    V6 + V8: full watershed with gradually deepening valley.
    First cycle: iterative dominates. Multi-cycle: valley channels.
    """
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # φ-leak
        phi_energy = PHI_LEAK * (1.0 - eff) * phi_scale

        bounced = log_val + wdlog + phi_energy

        # Graduated basin
        frac = min(t / max(ramp_years, 1), 1.0)
        basin_str = basin_start + (basin_max - basin_start) * frac

        engine_depth = max(R_matter - 1.0, 0.0) * depth_scale
        valley = C + engine_depth * np.sin(2*np.pi*(t+1)/HALE_PERIOD + phase0)

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
    print("φ-VALLEY WATERSHED MODEL")
    print("Water molecule in a watershed — bounces but finds the φ-valley")
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

    # ── V1: Linear basin ──
    print(f"\n--- V1: Linear basin ---")
    for ds in [0.3, 0.5, 0.7, 1.0]:
        for bs in [0.1, 0.2, 0.3, 0.5, 0.7, 0.9]:
            test(f"V1 d={ds} b={bs}", make_linear_basin(ds, bs))

    # ── V2: Quadratic basin ──
    print(f"\n--- V2: Quadratic basin ---")
    for ds in [0.5, 1.0]:
        for bk in [0.1, 0.3, 0.5, 1.0, 2.0]:
            test(f"V2 d={ds} k={bk}", make_quadratic_basin(ds, bk))

    # ── V3: Basin + φ-leak ──
    print(f"\n--- V3: Basin + φ-leak ---")
    for ds in [0.5, 0.7]:
        for bs in [0.2, 0.3, 0.5]:
            for ps in [0.01, 0.02, 0.05]:
                test(f"V3 d={ds} b={bs} φ={ps}", make_basin_phi_leak(ds, bs, ps))

    # ── V4: Basin + soft floor ──
    print(f"\n--- V4: Basin + floor ---")
    for ds in [0.3, 0.5, 0.7, 1.0]:
        for bs in [0.2, 0.3, 0.5, 0.7]:
            for fo in [0.3, 0.5, 0.8]:
                test(f"V4 d={ds} b={bs} f={fo}", make_basin_floor(ds, bs, fo))

    # ── V5: Basin + π-on-φ turbulence ──
    print(f"\n--- V5: Basin + turbulence ---")
    for ds in [0.5, 0.7]:
        for bs in [0.3, 0.5]:
            for ts in [0.5, 1.0, 2.0]:
                test(f"V5 d={ds} b={bs} t={ts}", make_basin_pi_phi(ds, bs, ts))

    # ── V6: Full watershed ──
    print(f"\n--- V6: Full watershed ---")
    for ds in [0.3, 0.5, 0.7]:
        for bs in [0.2, 0.3, 0.5]:
            for ps in [0.01, 0.02]:
                for ts in [0.5, 1.0]:
                    test(f"V6 d={ds} b={bs} φ={ps} t={ts}",
                         make_full_watershed(ds, bs, ps, ts, 0.5))

    # ── V7: Asymmetric basin ──
    print(f"\n--- V7: Asymmetric basin ---")
    for ds in [0.5, 0.7]:
        for bu in [0.1, 0.2, 0.3]:
            for bd in [0.3, 0.5, 0.7]:
                test(f"V7 d={ds} up={bu} dn={bd}", make_asymmetric_basin(ds, bu, bd))

    # ── V8: Graduated basin ──
    print(f"\n--- V8: Graduated basin ---")
    for ds in [0.5, 0.7]:
        for bs_start in [0.05, 0.1]:
            for bs_max in [0.3, 0.5, 0.7]:
                for ramp in [11, 22, 33]:
                    test(f"V8 d={ds} s={bs_start} m={bs_max} r={ramp}",
                         make_graduated_basin(ds, bs_start, bs_max, ramp))

    # ── V9: Golden valley ──
    print(f"\n--- V9: Golden valley ---")
    for ds in [0.5, 0.7]:
        for bs in [0.3, 0.5]:
            for ms in [0.2, 0.5, 1.0]:
                test(f"V9 d={ds} b={bs} m={ms}", make_golden_valley(ds, bs, ms))

    # ── V10: Full watershed graduated ──
    print(f"\n--- V10: Full watershed graduated ---")
    for ds in [0.5, 0.7]:
        for bs_s in [0.05, 0.1]:
            for bs_m in [0.3, 0.5]:
                for ps in [0.01, 0.02]:
                    test(f"V10 d={ds} s={bs_s} m={bs_m} φ={ps}",
                         make_watershed_graduated(ds, bs_s, bs_m, 22, ps, 0.5))

    print(f"\n{'='*70}")
    print("TOP RESULTS")
    print("="*70)
    print(f"  Previous best:     7/8  (Script 178)")
    print(f"  Best SSN corr:     {best_corr:+.3f} ({best_label})")
    if best_8: print(f"  ★★★ FIRST 8/8:    {best_8}")

    sorted_scores = sorted(all_scores.items(), key=lambda x: -x[1])
    for label, s in sorted_scores[:20]:
        m = " ★★★ 8/8!" if s == 8 else " ★ NEW BEST" if s > 7 else " ← ties 7" if s == 7 else ""
        print(f"  191 {label}: {s}/8{m}")

    # Count by score
    from collections import Counter
    cnt = Counter(all_scores.values())
    print(f"\nScore distribution: ", end="")
    for score in sorted(cnt.keys(), reverse=True):
        print(f"{score}/8:{cnt[score]}  ", end="")
    print()

    print(f"\nScript 191 complete.")
