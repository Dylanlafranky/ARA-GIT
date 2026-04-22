#!/usr/bin/env python3
"""
Script 174 — ARA Cycle Clock
==============================

The missing piece: the formula needs an INDEPENDENT TIME COUNTER.

Previous scripts mapped value → longitude → wave → delta, but if the
value doesn't change, the longitude doesn't change, and you get the
same delta forever.  No oscillation.

The fix: TIME TICKS FORWARD independently of value.

    effective_ARA(t) = ARA_center + ARA_amplitude × sin(2πt / T_hale)

Over one Hale cycle (22 years), the effective ARA smoothly oscillates
between the system's ARA value and its inversion:

    ARA peak = ARA (discharge character, e.g. 1.73 for SSN)
    ARA trough = 2 - ARA (accumulation character, e.g. 0.27 for SSN)
    ARA center = 1.0 (the coupler midpoint)
    ARA amplitude = ARA - 1.0 (e.g. 0.73 for SSN)

When effective_ARA is high → the formula behaves like a discharge system
    → large deltas, fast changes, snapping down
When effective_ARA is low → accumulation character
    → small deltas, slow changes, building up

The VALUE feedback still works (φ-inside for stability), but the
DRIVE comes from the clock.  Even at flat values, the gear ratio
changes, so the prediction changes direction.

The cycle counter needs a START PHASE — calibrated from training data
by finding which phase best matches the known cycle.
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

# ─── Effective ARA over time ─────────────────────────────────────────

def effective_ara(ara_base, t_years, phase0):
    """
    ARA oscillates between ara_base and (2-ara_base) over the Hale cycle.
    Center = 1.0, amplitude = |ara_base - 1.0|.
    """
    center = 1.0
    amplitude = ara_base - center  # positive for SSN (1.73-1=0.73), negative for EQ (0.15-1=-0.85)
    return center + amplitude * np.sin(2 * np.pi * t_years / HALE_PERIOD + phase0)

# ─── Core wave functions ─────────────────────────────────────────────

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def phi_stable_delta(log_val, C, R_matter, step_years=1):
    """Inner: φ-averaged wave delta (stability)."""
    phi_pos = value_to_longitude(log_val, C, R_matter)
    phi_next = phi_pos + DPHI * step_years
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi_pos, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi_pos+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    return ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

def standard_wave_delta(log_val, C, R_matter, step_years=1):
    """Outer: standard isosceles wave delta (rhythm)."""
    phi = value_to_longitude(log_val, C, R_matter)
    phi_next = phi + DPHI * step_years
    c1n = wave(phi, R_COUPLER)
    c2n = wave(phi+HALF_PHI, R_COUPLER)
    c1x = wave(phi_next, R_COUPLER)
    c2x = wave(phi_next+HALF_PHI, R_COUPLER)
    return ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

# ─── Clock-driven predictions ───────────────────────────────────────

def clock_v1(log_val, C, R_matter, step_years, t, phase0):
    """
    V1: The effective ARA modulates the outer wave strength.

    φ-stable always on.
    Outer wave × (effective_ARA - 1.0) gives signed drive:
        When eff_ARA > 1: outer pushes (discharge phase)
        When eff_ARA < 1: outer pulls back (accumulation phase)
        When eff_ARA = 1: pure stability

    The CLOCK determines push vs pull, not the value.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)
    outer = standard_wave_delta(log_val, C, R_matter, step_years)

    eff = effective_ara(R_matter, t, phase0)
    drive = eff - 1.0  # oscillates between +0.73 and -0.73 for SSN

    distance = abs(log_val - C)
    gear = max(distance / HALF_PHI, 0.1)  # minimum gear engagement

    dlog = inner + drive * gear * outer
    return log_val + dlog


def clock_v2(log_val, C, R_matter, step_years, t, phase0):
    """
    V2: The effective ARA replaces R_matter in the longitude mapping.

    At each time step, the system's ARA character changes.
    This means value_to_longitude maps the SAME value to DIFFERENT
    longitudes at different times → the wave reads different positions
    → natural oscillation even at flat values.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)  # prevent division by zero

    # Use effective ARA for the longitude mapping
    phi = value_to_longitude(log_val, C, eff)
    phi_next = phi + DPHI * step_years

    # φ-inside for stability
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2

    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Standard wave at the time-shifted longitude
    c1n_s = wave(phi, R_COUPLER)
    c2n_s = wave(phi+HALF_PHI, R_COUPLER)
    c1x_s = wave(phi_next, R_COUPLER)
    c2x_s = wave(phi_next+HALF_PHI, R_COUPLER)
    outer = ((c1x_s+c2x_s)/2 - (c1n_s+c2n_s)/2) * np.exp(-MIDPOINT_OFFSET)

    # Gated blend
    distance = abs(log_val - C)
    blend = min(distance / HALF_PHI, 1.0)

    dlog = (1 - blend) * inner + blend * outer
    return log_val + dlog


def clock_v3(log_val, C, R_matter, step_years, t, phase0):
    """
    V3: The clock adds a DIRECT sinusoidal push to the prediction.

    The φ-stable provides the base (keeps you in range).
    The clock provides the RHYTHM directly:

    dlog = φ_stable_delta + amplitude × sin(2πt/T + phase0)

    where amplitude = (ARA - 1.0) × scale_factor

    This is the simplest possible clock: just add a sine wave
    on top of the stabilized prediction.
    """
    inner = phi_stable_delta(log_val, C, R_matter, step_years)

    # Clock drive: sinusoidal push
    amplitude = (R_matter - 1.0) * 0.1  # scale down to prevent blowup
    clock_push = amplitude * np.sin(2 * np.pi * t / HALE_PERIOD + phase0)

    dlog = inner + clock_push
    return log_val + dlog


def clock_v4(log_val, C, R_matter, step_years, t, phase0):
    """
    V4: Full integration — the clock modulates BOTH the mapping AND the drive.

    1. effective_ARA(t) oscillates the system's character
    2. The longitude is mapped using effective_ARA (V2's trick)
    3. The drive strength is modulated by effective_ARA (V1's trick)
    4. φ-stable provides base stability

    The two effects compound: at discharge phase (eff_ARA > 1),
    the mapping stretches AND the drive pushes → fast snap.
    At accumulation phase (eff_ARA < 1), mapping compresses
    AND drive pulls back → slow climb.
    """
    eff = effective_ara(R_matter, t, phase0)
    eff = max(eff, 0.1)

    # Longitude with time-varying ARA
    phi = value_to_longitude(log_val, C, eff)
    phi_next = phi + DPHI * step_years

    # φ-stable at this longitude
    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-MIDPOINT_OFFSET)

    # Standard wave for outer drive
    outer = standard_wave_delta(log_val, C, eff, step_years)

    # Modulation
    drive = eff - 1.0
    distance = abs(log_val - C)
    gear = distance / HALF_PHI

    dlog = inner + drive * gear * outer
    return log_val + dlog


def clock_v5(log_val, C, R_matter, step_years, t, phase0):
    """
    V5: The ARA and inverted ARA run as TWO COUPLED OSCILLATORS.

    Oscillator A: ARA value, phase = 2πt/T + phase0
    Oscillator B: (2-ARA) value, phase = 2πt/T + phase0 + φ/2

    Each contributes a wave delta. Their INTERFERENCE pattern
    is the prediction.

    When A and B are in phase: constructive → big push
    When A and B are out of phase: destructive → stability
    The φ/2 offset ensures they're never fully in or out of phase.
    """
    # φ-stable base
    inner = phi_stable_delta(log_val, C, R_matter, step_years)

    ara_a = R_matter
    ara_b = 2.0 - R_matter

    # Phase of each oscillator
    phase_a = 2 * np.pi * t / HALE_PERIOD + phase0
    phase_b = phase_a + HALF_PHI  # golden offset

    # Wave contribution from oscillator A
    amp_a = (ara_a - 1.0) * np.sin(phase_a)
    # Wave contribution from oscillator B
    amp_b = (ara_b - 1.0) * np.sin(phase_b)

    # Combined interference
    interference = (amp_a + amp_b) * 0.1  # scale factor

    # The interference modulates the outer wave
    outer = standard_wave_delta(log_val, C, R_matter, step_years)
    distance = abs(log_val - C)

    dlog = inner + interference * max(distance, 0.1) * outer
    return log_val + dlog


# ─── Phase calibration ──────────────────────────────────────────────

def calibrate_phase(train_data, R_matter, predict_fn, n_phases=24):
    """
    Find the starting phase that best matches training data.
    Test n_phases evenly spaced phases over [0, 2π).
    Score by correlation between predicted and actual year-over-year changes.
    """
    years = sorted(train_data.keys())
    if len(years) < 20:
        return 0.0

    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase = 0.0
    best_score = -999

    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases

        # Predict last 15 years of training data
        test_start = max(0, len(years) - 15)
        start_log = np.log10(max(train_data[years[test_start]], 0.1))

        pred_changes = []
        actual_changes = []
        current = start_log

        for i in range(test_start + 1, len(years)):
            t = i - test_start  # time counter
            new = predict_fn(current, C, R_matter, 1, t, phase0)
            pred_changes.append(new - current)
            actual_change = np.log10(max(train_data[years[i]], 0.1)) - \
                           np.log10(max(train_data[years[i-1]], 0.1))
            actual_changes.append(actual_change)
            current = np.log10(max(train_data[years[i]], 0.1))  # use actual for next step

        if len(pred_changes) < 5:
            continue

        pc = np.array(pred_changes)
        ac = np.array(actual_changes)

        if np.std(pc) > 0 and np.std(ac) > 0:
            corr = float(np.corrcoef(pc, ac)[0, 1])
        else:
            corr = 0

        # Also reward direction matching
        dir_match = sum(1 for p, a in zip(pc, ac) if np.sign(p) == np.sign(a)) / len(pc)

        score = corr + dir_match
        if score > best_score:
            best_score = score
            best_phase = phase0

    return best_phase


# ─── Data loaders ────────────────────────────────────────────────────

def load_sunspot_annual():
    ssn_path = os.path.join(os.path.dirname(__file__), '..', 'solar_test', 'sunspots.txt')
    monthly = {}
    with open(ssn_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 4: continue
            try:
                yr = int(parts[0]); val = float(parts[3])
                if val < 0: continue
                monthly.setdefault(yr, []).append(val)
            except ValueError: continue
    return {y: np.mean(v) for y, v in monthly.items() if len(v) >= 6}

def load_earthquake_annual():
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

def oscillation_test(predict_fn, label, C, R=ARA_SSN, phase0=0.0):
    """Test oscillation with the clock running."""
    results = []
    for off in [0.5, -0.8]:
        log_val = C + off
        prev_d = 0; turns = 0; vals = []
        for yr in range(30):
            new = predict_fn(log_val, C, R, 1, yr, phase0)
            d = new - log_val
            if yr > 0 and np.sign(d) != np.sign(prev_d) and prev_d != 0:
                turns += 1
            prev_d = d; vals.append(10**log_val); log_val = new
        results.append((turns, min(vals), max(vals), vals[-1]))
    hi, lo = results
    print(f"  {label}: hi_turns={hi[0]} lo_turns={lo[0]} "
          f"hi=[{hi[1]:.0f},{hi[2]:.0f}→{hi[3]:.0f}] "
          f"lo=[{lo[1]:.0f},{lo[2]:.0f}→{lo[3]:.0f}]")
    return hi[0] + lo[0]

def run_blind(data, cutoffs, R_matter, predict_fn):
    results = []
    for cutoff in cutoffs:
        train = {y:v for y,v in data.items() if y < cutoff}
        test  = {y:v for y,v in data.items() if y >= cutoff}
        if len(train)<10 or len(test)<5: continue

        C = np.mean(np.log10([max(v,.1) for v in train.values()]))

        # Calibrate phase from training data
        phase0 = calibrate_phase(train, R_matter, predict_fn)

        sv = max(data[max(train.keys())],.1)
        ty = sorted(test.keys())

        preds = []; cur = np.log10(sv)
        for i, y in enumerate(ty):
            cur = predict_fn(cur, C, R_matter, 1, i+1, phase0)
            preds.append(10**cur)

        act = [data[y] for y in ty]; n = len(ty); nv = sv
        a,p = np.array(act), np.array(preds)
        c = float(np.corrcoef(a,p)[0,1]) if np.std(a)>0 and np.std(p)>0 and len(a)>2 else 0
        m = float(np.mean(np.abs(a-p)))
        nm = float(np.mean(np.abs(a-nv)))
        b = sum(1 for pi,ai in zip(preds,act) if abs(pi-ai)<abs(nv-ai))/n*100
        x = sum(1 for pi,ai in zip(preds,act) if 1/2<=max(pi,.1)/max(ai,.1)<=2)/n*100
        dm,dt = 0,0
        for i in range(1,n):
            if np.sign(act[i]-act[i-1])!=0:
                dt+=1
                if np.sign(preds[i]-preds[i-1])==np.sign(act[i]-act[i-1]): dm+=1
        d = dm/max(dt,1)*100
        results.append({'cutoff':cutoff,'corr':c,'beats':b,'x2':x,'dir':d,
                        'mae':m,'naive_mae':nm,'preds':preds[:12],'act':act[:12],
                        'yrs':ty[:12],'naive':nv,'phase0':phase0})
    return results

def full_score(ssn_r, eq_r, label):
    s = 0; lines = []
    ac=np.mean([r['corr'] for r in ssn_r]); p=ac>0.3; s+=p
    lines.append(f"SSNc={ac:+.2f}{'✓' if p else '✗'}")
    bn=sum(1 for r in ssn_r if r['beats']>50); p=bn>=3; s+=p
    lines.append(f"bn={bn}/6{'✓' if p else '✗'}")
    ax=np.mean([r['x2'] for r in ssn_r]); p=ax>30; s+=p
    lines.append(f"×2={ax:.0f}%{'✓' if p else '✗'}")
    ad=np.mean([r['dir'] for r in ssn_r]); p=ad>55; s+=p
    lines.append(f"dir={ad:.0f}%{'✓' if p else '✗'}")
    ec=np.mean([r['corr'] for r in eq_r]); p=ec>0.2; s+=p
    lines.append(f"EQc={ec:+.2f}{'✓' if p else '✗'}")
    ex=np.mean([r['x2'] for r in eq_r]); p=ex>30; s+=p
    lines.append(f"EQ×2={ex:.0f}%{'✓' if p else '✗'}")
    bm=sum(1 for r in ssn_r if r['mae']<r['naive_mae']); p=bm>=3; s+=p
    lines.append(f"MAE={bm}/6{'✓' if p else '✗'}")
    nb=all(r['mae']<500 for r in ssn_r); p=nb; s+=p
    lines.append(f"drift{'✓' if p else '✗'}")

    print(f"\n  {label}  →  SCORE: {s}/8")
    print(f"    {' | '.join(lines)}")

    for r in ssn_r:
        if r['cutoff'] in [1990, 2005, 2010]:
            print(f"    SSN {r['cutoff']} (φ0={r['phase0']:.2f}): ", end="")
            for i in range(min(10, len(r['yrs']))):
                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
            print()

    for r in eq_r:
        if r['cutoff'] == 2000:
            print(f"    EQ  2000 (φ0={r['phase0']:.2f}): ", end="")
            for i in range(min(8, len(r['yrs']))):
                print(f"{r['yrs'][i]}({r['act'][i]:.0f}/{r['preds'][i]:.0f}) ", end="")
            print()

    return s

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_sunspot_annual()
    eq  = load_earthquake_annual()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]
    C_ssn = np.mean(np.log10([max(v,.1) for v in ssn.values()]))

    versions = [
        ("V1: ARA modulates outer strength", clock_v1),
        ("V2: ARA rotates longitude mapping", clock_v2),
        ("V3: direct sinusoidal push", clock_v3),
        ("V4: full ARA+longitude modulation", clock_v4),
        ("V5: dual coupled oscillators", clock_v5),
    ]

    print("="*70)
    print("OSCILLATION DIAGNOSTIC (with clock, phase0=0)")
    print("="*70)
    for label, fn in versions:
        oscillation_test(fn, label, C_ssn)

    print(f"\n{'='*70}")
    print("BLIND TESTS (with phase calibration)")
    print("="*70)

    all_scores = {}
    for label, fn in versions:
        ssn_r = run_blind(ssn, cutoffs, ARA_SSN, fn)
        eq_r  = run_blind(eq,  cutoffs, ARA_EQ,  fn)
        s = full_score(ssn_r, eq_r, label)
        all_scores[label] = s

    print(f"\n{'='*70}")
    print("GRAND COMPARISON")
    print("="*70)
    print(f"  170 V4 (φ inside longitude):  6/8  ← overall best")
    print(f"  172 V6 (restoring-only):      5/8  (SSN beats 6/6)")
    for label, s in all_scores.items():
        m = " ★ NEW BEST" if s > 6 else " ← ties" if s == 6 else ""
        print(f"  174 {label}: {s}/8{m}")

    print(f"\nScript 174 complete.")
