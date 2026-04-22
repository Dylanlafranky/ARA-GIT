#!/usr/bin/env python3
"""
Script 186 — Log-Boundary π-Leak Accumulation
===============================================

Dylan's insight: "Pi leak might be affected by the log underneath it.
Whenever you cross a log, you add the accumulation of the amount of the
cycle from the one you just came from — extra connections snapping on
at singularity crossover."

The geometry:
    - In log-space, each integer = one circle (factor of 10)
    - The prediction moves THROUGH these circles over a Hale cycle
    - π-leak (π-3 ≈ 0.14159) accumulates within each circle
    - When the prediction crosses from one log level to the next,
      ALL the accumulated leak from that circle discharges as an IMPULSE
    - This simulates connections snapping on/off at phase transitions

For SSN: log10(5)=0.7 → log10(200)=2.3, spanning ~1.5 circles
For EQ:  log10(6)=0.78 → log10(41)=1.61, spanning ~0.8 circles

Variants:
    V1: Log-floor crossing detector — impulse at integer log boundaries
    V2: φ-spaced boundaries — crossings at every 1/φ in log-space
    V3: Accumulated cycle fraction — tracks time in each level
    V4: Hybrid — continuous small leak + boundary impulse
    V5: Proportional boundary — impulse scaled by how much cycle was
        spent in the previous level (more time = more accumulation)
    V6: Bidirectional — different impulse for ascending vs descending
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

# ─── V1: Log-floor crossing impulse ───────────────────────────────

class LogBoundaryV1:
    """
    Track which integer log-floor we're in.
    When floor(log_val) changes → discharge impulse.
    Impulse = PI_LEAK × (cycle_fraction in previous level) × scale.
    Ascending (floor increases): positive impulse (connections snap ON)
    Descending (floor decreases): negative impulse (connections snap OFF)
    """
    def __init__(self, leak_scale=1.0):
        self.prev_floor = None
        self.ticks_in_level = 0
        self.leak_scale = leak_scale

    def predict(self, log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        current_floor = int(np.floor(log_val))
        leak = 0.0

        if self.prev_floor is not None and current_floor != self.prev_floor:
            # Boundary crossing! Accumulated leak from previous level
            cycle_frac = self.ticks_in_level / HALE_PERIOD
            direction = np.sign(current_floor - self.prev_floor)
            # Ascending: positive (new connections), Descending: negative
            leak = PI_LEAK * cycle_frac * direction * self.leak_scale
            self.ticks_in_level = 0
        else:
            self.ticks_in_level += 1

        self.prev_floor = current_floor
        return log_val + wdlog + leak

# ─── V2: φ-spaced boundary crossings ──────────────────────────────

class LogBoundaryV2:
    """
    Boundaries at every 1/φ ≈ 0.618 in log-space instead of every 1.0.
    More frequent crossings = more frequent but smaller impulses.
    The golden spacing means no two consecutive impulses align —
    maximum coverage of the cycle.
    """
    def __init__(self, leak_scale=1.0):
        self.spacing = 1.0 / PHI  # ≈ 0.618
        self.prev_zone = None
        self.ticks_in_zone = 0
        self.leak_scale = leak_scale

    def predict(self, log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        current_zone = int(np.floor(log_val / self.spacing))
        leak = 0.0

        if self.prev_zone is not None and current_zone != self.prev_zone:
            cycle_frac = self.ticks_in_zone / HALE_PERIOD
            direction = np.sign(current_zone - self.prev_zone)
            leak = PI_LEAK * cycle_frac * direction * self.leak_scale
            self.ticks_in_zone = 0
        else:
            self.ticks_in_zone += 1

        self.prev_zone = current_zone
        return log_val + wdlog + leak

# ─── V3: Continuous accumulation + boundary discharge ──────────────

class LogBoundaryV3:
    """
    π-leak accumulates silently each tick (based on clock phase).
    Only discharges when crossing a log boundary.
    The accumulated amount depends on how deep into accumulation
    vs discharge the clock was during that period.
    """
    def __init__(self, leak_scale=1.0):
        self.prev_floor = None
        self.accumulated = 0.0
        self.leak_scale = leak_scale

    def predict(self, log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # Accumulate π-leak silently (opposite of clock)
        self.accumulated += PI_LEAK * (1.0 - eff) * self.leak_scale

        current_floor = int(np.floor(log_val))
        leak = 0.0

        if self.prev_floor is not None and current_floor != self.prev_floor:
            # Discharge ALL accumulated leak at boundary
            leak = self.accumulated
            self.accumulated = 0.0  # Reset after discharge

        self.prev_floor = current_floor
        return log_val + wdlog + leak

# ─── V4: Hybrid — small continuous + boundary impulse ──────────────

class LogBoundaryV4:
    """
    Continuous small leak (like 184 V2) PLUS a bigger impulse at boundaries.
    The continuous part keeps the prediction from freezing.
    The boundary impulse gives the discrete "snap" at level transitions.
    """
    def __init__(self, cont_scale=0.05, boundary_scale=1.0):
        self.prev_floor = None
        self.ticks_in_level = 0
        self.cont_scale = cont_scale
        self.boundary_scale = boundary_scale

    def predict(self, log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        # Continuous small leak (always active)
        cont_leak = PI_LEAK * (1.0 - eff) * self.cont_scale

        # Boundary impulse
        current_floor = int(np.floor(log_val))
        boundary_leak = 0.0

        if self.prev_floor is not None and current_floor != self.prev_floor:
            cycle_frac = self.ticks_in_level / HALE_PERIOD
            direction = np.sign(current_floor - self.prev_floor)
            boundary_leak = PI_LEAK * cycle_frac * direction * self.boundary_scale
            self.ticks_in_level = 0
        else:
            self.ticks_in_level += 1

        self.prev_floor = current_floor
        return log_val + wdlog + cont_leak + boundary_leak

# ─── V5: Log-distance weighted — how FAR you crossed matters ──────

class LogBoundaryV5:
    """
    Instead of just detecting crossings, measure the log-distance
    travelled since last tick. The leak is proportional to distance
    travelled × π-leak × clock opposition.

    More movement = more circles traversed = more leak accumulated.
    """
    def __init__(self, leak_scale=1.0):
        self.prev_log = None
        self.leak_scale = leak_scale

    def predict(self, log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        leak = 0.0
        if self.prev_log is not None:
            distance = abs(log_val - self.prev_log)
            # Leak proportional to distance × clock opposition
            leak = PI_LEAK * distance * np.sign(1.0 - eff) * self.leak_scale

        new_val = log_val + wdlog + leak
        self.prev_log = new_val  # Track where we END UP, not where we started
        return new_val

# ─── V6: ARA-scaled boundary impulse ──────────────────────────────

class LogBoundaryV6:
    """
    Boundary impulse scaled by (R_matter - 1.0).
    Engines (ARA>1) get positive impulse on ascent — more connections.
    Consumers (ARA<1) get opposite — fewer connections on ascent.
    Also: the impulse magnitude = PI_LEAK × number_of_levels_crossed.
    """
    def __init__(self, leak_scale=1.0):
        self.prev_floor = None
        self.ticks_in_level = 0
        self.leak_scale = leak_scale

    def predict(self, log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        current_floor = int(np.floor(log_val))
        leak = 0.0

        if self.prev_floor is not None and current_floor != self.prev_floor:
            levels_crossed = abs(current_floor - self.prev_floor)
            cycle_frac = self.ticks_in_level / HALE_PERIOD
            direction = np.sign(current_floor - self.prev_floor)
            ara_factor = R_matter - 1.0  # +0.73 SSN, -0.85 EQ
            leak = PI_LEAK * levels_crossed * cycle_frac * direction * ara_factor * self.leak_scale
            self.ticks_in_level = 0
        else:
            self.ticks_in_level += 1

        self.prev_floor = current_floor
        return log_val + wdlog + leak

# ─── V7: Half-log boundaries (every 0.5 in log space) ─────────────

class LogBoundaryV7:
    """
    Boundaries every 0.5 in log-space = every sqrt(10) ≈ 3.16× in linear.
    Finer granularity than V1, coarser than V2.
    """
    def __init__(self, leak_scale=1.0, spacing=0.5):
        self.spacing = spacing
        self.prev_zone = None
        self.ticks_in_zone = 0
        self.leak_scale = leak_scale

    def predict(self, log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        current_zone = int(np.floor(log_val / self.spacing))
        leak = 0.0

        if self.prev_zone is not None and current_zone != self.prev_zone:
            cycle_frac = self.ticks_in_zone / HALE_PERIOD
            direction = np.sign(current_zone - self.prev_zone)
            leak = PI_LEAK * cycle_frac * direction * self.leak_scale
            self.ticks_in_zone = 0
        else:
            self.ticks_in_zone += 1

        self.prev_zone = current_zone
        return log_val + wdlog + leak

# ─── V8: Clock-gated boundary — only fire during accumulation ─────

class LogBoundaryV8:
    """
    Boundary impulse only fires when crossing a log level during
    accumulation phase (eff < 1). During discharge, crossings are
    natural and don't need the extra push.

    This is Dylan's "opposite of the clock" — leak restores during
    accumulation, stays silent during discharge.
    """
    def __init__(self, leak_scale=1.0):
        self.prev_floor = None
        self.ticks_in_level = 0
        self.leak_scale = leak_scale

    def predict(self, log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0)

        current_floor = int(np.floor(log_val))
        leak = 0.0

        if self.prev_floor is not None and current_floor != self.prev_floor:
            cycle_frac = self.ticks_in_level / HALE_PERIOD
            # Only apply during accumulation (eff < 1)
            if eff < 1.0:
                leak = PI_LEAK * cycle_frac * self.leak_scale  # Always positive during accum
            self.ticks_in_level = 0
        else:
            self.ticks_in_level += 1

        self.prev_floor = current_floor
        return log_val + wdlog + leak

# ─── Phase calibration & data ─────────────────────────────────────

def calibrate_phase_stateful(train_data, R_matter, predictor_class, **kwargs):
    """Calibrate phase for stateful (class-based) predictors."""
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v,.1) for v in train_data.values()]))
    best_phase = 0.0; best_score = -999
    for pi in range(24):
        phase0 = 2*np.pi*pi/24
        test_start = max(0, len(years)-15)
        current = np.log10(max(train_data[years[test_start]],.1))
        # Fresh predictor for each phase test
        pred = predictor_class(**kwargs)
        pc, ac_list = [], []
        for i in range(test_start+1, len(years)):
            t = i - test_start
            new = pred.predict(current, C, R_matter, 1, t, phase0)
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

def run_blind_stateful(data, cutoffs, R_matter, predictor_class, **kwargs):
    """Run blind test for stateful predictors (must be re-instantiated)."""
    results = []
    for cutoff in cutoffs:
        tr = {y:v for y,v in data.items() if y < cutoff}
        te = {y:v for y,v in data.items() if y >= cutoff}
        if len(tr) < 10 or len(te) < 5: continue
        C = np.mean(np.log10([max(v,.1) for v in tr.values()]))
        ph = calibrate_phase_stateful(tr, R_matter, predictor_class, **kwargs)
        sv = max(data[max(tr.keys())], .1)
        ty = sorted(te.keys())

        # Fresh predictor for actual blind test
        pred = predictor_class(**kwargs)
        preds = []; cur = np.log10(sv)
        for i, y in enumerate(ty):
            cur = pred.predict(cur, C, R_matter, 1, i+1, ph)
            preds.append(10**cur)

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
    print("LOG-BOUNDARY π-LEAK ACCUMULATION")
    print("="*70)
    print(f"π-leak = {PI_LEAK:.5f}")
    print(f"SSN spans log levels: {np.log10(5):.2f} to {np.log10(200):.2f} (~{np.log10(200)-np.log10(5):.1f} circles)")
    print(f"EQ  spans log levels: {np.log10(6):.2f} to {np.log10(41):.2f} (~{np.log10(41)-np.log10(6):.1f} circles)")

    all_scores = {}

    # V1: Log-floor crossing
    print(f"\n--- V1: Integer log-floor crossings ---")
    for ls in [0.5, 1.0, 1.5, 2.0, 3.0, PHI]:
        label = f"V1 floor scale={ls:.2f}"
        sr = run_blind_stateful(ssn, cutoffs, ARA_SSN, LogBoundaryV1, leak_scale=ls)
        er = run_blind_stateful(eq, cutoffs, ARA_EQ, LogBoundaryV1, leak_scale=ls)
        all_scores[label] = score_and_report(sr, er, label)

    # V2: φ-spaced boundaries
    print(f"\n--- V2: φ-spaced boundaries (1/φ ≈ 0.618) ---")
    for ls in [0.5, 1.0, 1.5, 2.0, PHI]:
        label = f"V2 φ-space scale={ls:.2f}"
        sr = run_blind_stateful(ssn, cutoffs, ARA_SSN, LogBoundaryV2, leak_scale=ls)
        er = run_blind_stateful(eq, cutoffs, ARA_EQ, LogBoundaryV2, leak_scale=ls)
        all_scores[label] = score_and_report(sr, er, label)

    # V3: Accumulated + boundary discharge
    print(f"\n--- V3: Silent accumulation, boundary discharge ---")
    for ls in [0.05, 0.1, 0.2, 0.3, 0.5]:
        label = f"V3 accum scale={ls:.2f}"
        sr = run_blind_stateful(ssn, cutoffs, ARA_SSN, LogBoundaryV3, leak_scale=ls)
        er = run_blind_stateful(eq, cutoffs, ARA_EQ, LogBoundaryV3, leak_scale=ls)
        all_scores[label] = score_and_report(sr, er, label)

    # V4: Hybrid — continuous + boundary
    print(f"\n--- V4: Hybrid (continuous + boundary) ---")
    for cs in [0.03, 0.05, 0.08]:
        for bs in [1.0, 2.0, PHI]:
            label = f"V4 cont={cs} bound={bs:.2f}"
            sr = run_blind_stateful(ssn, cutoffs, ARA_SSN, LogBoundaryV4,
                                     cont_scale=cs, boundary_scale=bs)
            er = run_blind_stateful(eq, cutoffs, ARA_EQ, LogBoundaryV4,
                                     cont_scale=cs, boundary_scale=bs)
            all_scores[label] = score_and_report(sr, er, label)

    # V5: Distance-weighted leak
    print(f"\n--- V5: Log-distance weighted ---")
    for ls in [0.5, 1.0, PHI, 2.0, 3.0]:
        label = f"V5 dist scale={ls:.2f}"
        sr = run_blind_stateful(ssn, cutoffs, ARA_SSN, LogBoundaryV5, leak_scale=ls)
        er = run_blind_stateful(eq, cutoffs, ARA_EQ, LogBoundaryV5, leak_scale=ls)
        all_scores[label] = score_and_report(sr, er, label)

    # V6: ARA-scaled boundary
    print(f"\n--- V6: ARA-scaled boundary ---")
    for ls in [1.0, 2.0, 3.0, PHI]:
        label = f"V6 ARA-bd scale={ls:.2f}"
        sr = run_blind_stateful(ssn, cutoffs, ARA_SSN, LogBoundaryV6, leak_scale=ls)
        er = run_blind_stateful(eq, cutoffs, ARA_EQ, LogBoundaryV6, leak_scale=ls)
        all_scores[label] = score_and_report(sr, er, label)

    # V7: Half-log boundaries
    print(f"\n--- V7: Half-log boundaries (0.5 spacing) ---")
    for ls in [0.5, 1.0, 1.5, 2.0]:
        label = f"V7 half-log scale={ls:.2f}"
        sr = run_blind_stateful(ssn, cutoffs, ARA_SSN, LogBoundaryV7,
                                 leak_scale=ls, spacing=0.5)
        er = run_blind_stateful(eq, cutoffs, ARA_EQ, LogBoundaryV7,
                                 leak_scale=ls, spacing=0.5)
        all_scores[label] = score_and_report(sr, er, label)

    # V8: Clock-gated boundary (accumulation only)
    print(f"\n--- V8: Clock-gated (accumulation phase only) ---")
    for ls in [1.0, 2.0, 3.0, PHI, 5.0]:
        label = f"V8 accum-gate scale={ls:.2f}"
        sr = run_blind_stateful(ssn, cutoffs, ARA_SSN, LogBoundaryV8, leak_scale=ls)
        er = run_blind_stateful(eq, cutoffs, ARA_EQ, LogBoundaryV8, leak_scale=ls)
        all_scores[label] = score_and_report(sr, er, label)

    print(f"\n{'='*70}")
    print("TOP RESULTS")
    print("="*70)
    print(f"  Previous best:  7/8  (Script 178)")
    for label, s in sorted(all_scores.items(), key=lambda x: -x[1])[:15]:
        m = " ★★★ 8/8!" if s == 8 else " ★ NEW BEST" if s > 7 else " ← ties 7" if s == 7 else ""
        print(f"  186 {label}: {s}/8{m}")

    print(f"\nScript 186 complete.")
