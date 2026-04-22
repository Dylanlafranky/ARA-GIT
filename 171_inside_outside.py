#!/usr/bin/env python3
"""
Script 171 — Inside-Outside: φ-Stable Core + Standard Wave Shell
=================================================================

Dylan's insight:
    "Just on the outside, we add the overall same system but on the outside."

Script 170 V4 (φ inside the longitude) scored 6/8:
    - Killed the drift completely
    - EQ within 2×: 79%
    - But: zero oscillation, no rhythm, direction accuracy ≈ coin flip

The standard isosceles prediction (Script 166):
    - Knows the Hale cycle
    - Has the phase information
    - But: drifts to infinity

SOLUTION: Nest them.
    INNER: φ inside longitude → stable attractor (holds you in place)
    OUTER: standard isosceles wave → oscillation (makes you dance)

    predicted = standard_wave( φ_stable( current ) )

The inner φ prevents drift. The outer wave provides rhythm.
The system lives on a stable orbit and oscillates around it.
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

# ─── Core functions ──────────────────────────────────────────────────

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def standard_predict(log_val, C, R_matter, step_years=1):
    """Standard isosceles prediction — has rhythm, no stability."""
    phi = value_to_longitude(log_val, C, R_matter)
    phi_next = phi + DPHI * step_years

    c1_now  = wave(phi, R_COUPLER)
    c2_now  = wave(phi + HALF_PHI, R_COUPLER)
    c1_next = wave(phi_next, R_COUPLER)
    c2_next = wave(phi_next + HALF_PHI, R_COUPLER)

    dlog = ((c1_next + c2_next)/2 - (c1_now + c2_now)/2) * np.exp(-MIDPOINT_OFFSET)
    return log_val + dlog

def phi_stable(log_val, C, R_matter, step_years=1):
    """V4: φ inside longitude — has stability, no rhythm."""
    phi_pos = value_to_longitude(log_val, C, R_matter)
    phi_next = phi_pos + DPHI * step_years

    def avg_wave(pos, R, offset):
        return (wave(pos + offset, R) + wave(pos - offset, R)) / 2

    c1_now  = avg_wave(phi_pos, R_COUPLER, PHI)
    c1_next = avg_wave(phi_next, R_COUPLER, PHI)
    c2_now  = avg_wave(phi_pos + HALF_PHI, R_COUPLER, PHI)
    c2_next = avg_wave(phi_next + HALF_PHI, R_COUPLER, PHI)

    avg_now  = (c1_now + c2_now) / 2
    avg_next = (c1_next + c2_next) / 2

    dlog = (avg_next - avg_now) * np.exp(-MIDPOINT_OFFSET)
    return log_val + dlog


# ─── Inside-Outside versions ────────────────────────────────────────

def inside_outside_v1(log_val, C, R_matter, step_years=1):
    """
    V1: Sequential nesting.
    Step 1: φ-stable gives the stabilized position
    Step 2: Standard wave predicts from that stabilized position

    predicted = standard_wave( φ_stable( current ) )
    """
    # Inner: stabilize
    stable_log = phi_stable(log_val, C, R_matter, step_years)
    # Outer: oscillate from the stable position
    final_log = standard_predict(stable_log, C, R_matter, step_years)
    return final_log


def inside_outside_v2(log_val, C, R_matter, step_years=1):
    """
    V2: Additive combination.
    The stable delta + the wave delta, applied once.

    Δlog = φ_stable_delta + standard_wave_delta
    (But the wave delta is computed from the STABLE position, not raw)
    """
    # Inner delta (stability)
    stable_log = phi_stable(log_val, C, R_matter, step_years)
    stable_delta = stable_log - log_val

    # Outer delta (rhythm) — computed from the stabilized position
    wave_log = standard_predict(stable_log, C, R_matter, step_years)
    wave_delta = wave_log - stable_log

    # Combined: stable base + wave oscillation
    return log_val + stable_delta + wave_delta


def inside_outside_v3(log_val, C, R_matter, step_years=1):
    """
    V3: Weighted combination.
    The inner (φ-stable) provides the base with weight φ.
    The outer (standard wave) provides oscillation with weight 1.
    Normalized by (1 + φ).

    This gives the stable attractor ~62% say, oscillation ~38% say.
    """
    stable_log = phi_stable(log_val, C, R_matter, step_years)
    wave_log = standard_predict(log_val, C, R_matter, step_years)

    # Golden-weighted average: stability dominates
    return (PHI * stable_log + 1.0 * wave_log) / (PHI + 1.0)


def inside_outside_v4(log_val, C, R_matter, step_years=1):
    """
    V4: The wave rides the stable orbit.

    1. φ-stable determines WHERE on the attractor you are
    2. Standard wave computes the DELTA (oscillation) from current position
    3. The oscillation is SCALED by the ratio of stable/raw deltas

    This means: the wave oscillates, but its amplitude is controlled
    by how far from the attractor you are.
    """
    # Stable position
    stable_log = phi_stable(log_val, C, R_matter, step_years)
    stable_delta = stable_log - log_val

    # Raw wave delta
    wave_log = standard_predict(log_val, C, R_matter, step_years)
    wave_delta = wave_log - log_val

    # Scale factor: how much the stability modifies the wave
    # When stable pulls the same direction as wave → amplify slightly
    # When stable opposes wave → dampen
    if abs(wave_delta) > 1e-10:
        scale = 1.0 + stable_delta / wave_delta
        # Clip to prevent sign reversal from going extreme
        scale = np.clip(scale, -2, 2)
    else:
        scale = 1.0

    return log_val + wave_delta * scale * 0.5


def inside_outside_v5(log_val, C, R_matter, step_years=1):
    """
    V5: Simplest possible nesting — φ-stable sets the TARGET,
    standard wave determines the STEP toward it.

    1. φ-stable(current) → where you SHOULD be (attractor)
    2. standard_predict(current) - current → how the wave WANTS to move
    3. Blend: move toward attractor + wave oscillation

    target = φ_stable(current)
    wave_impulse = standard_delta
    next = current + (target - current) × coupling + wave_impulse × (1 - coupling)
    """
    # Attractor
    target = phi_stable(log_val, C, R_matter, step_years)

    # Wave impulse
    wave_next = standard_predict(log_val, C, R_matter, step_years)
    wave_delta = wave_next - log_val

    # Coupling strength: 1/φ (golden ratio sub-dominance)
    coupling = 1.0 / PHI  # 0.618

    # Attractor pull
    attractor_pull = target - log_val

    # Combined step
    step = coupling * attractor_pull + (1 - coupling) * wave_delta
    return log_val + step


def inside_outside_v6(log_val, C, R_matter, step_years=1):
    """
    V6: Pure composition — apply the FULL formula twice,
    but the inner pass uses φ-averaged waves and the outer uses standard.

    This is literally: predict(predict(x)) where inner has φ,
    but we only advance time ONCE (both passes share the same DPHI step).
    The inner pass stabilizes the LONGITUDE, the outer pass reads the WAVE
    at that stabilized longitude.
    """
    # Inner: get the stabilized longitude
    phi_raw = value_to_longitude(log_val, C, R_matter)

    # φ-averaged wave values at current position
    def avg_wave_at(pos, R, offset):
        return (wave(pos + offset, R) + wave(pos - offset, R)) / 2

    stable_c1 = avg_wave_at(phi_raw, R_COUPLER, PHI)
    stable_c2 = avg_wave_at(phi_raw + HALF_PHI, R_COUPLER, PHI)
    stable_now = (stable_c1 + stable_c2) / 2

    # This stable_now IS the inner value — map it to a stabilized log
    # stable_now is a small number near zero (because cos(φ) ≈ -0.05)
    # It represents the φ-corrected "position" on the wave

    # Outer: advance the RAW longitude by DPHI and read the standard wave
    phi_next = phi_raw + DPHI * step_years

    c1_next = wave(phi_next, R_COUPLER)
    c2_next = wave(phi_next + HALF_PHI, R_COUPLER)
    outer_next = (c1_next + c2_next) / 2

    # The full delta: difference between outer-next and inner-now
    # Inner (φ-stabilized) tells you where you ARE
    # Outer (standard) tells you where you're GOING
    dlog = (outer_next - stable_now) * np.exp(-MIDPOINT_OFFSET)

    # But this might be large because stable_now is tiny and outer_next isn't
    # Scale by the stable/standard ratio at current position
    c1_now = wave(phi_raw, R_COUPLER)
    c2_now = wave(phi_raw + HALF_PHI, R_COUPLER)
    standard_now = (c1_now + c2_now) / 2

    # The correction: how different is φ-stable from standard at current pos
    correction = stable_now - standard_now  # negative when φ is dampening

    # Standard delta (what the wave wants)
    standard_delta = (outer_next - standard_now) * np.exp(-MIDPOINT_OFFSET)

    # Corrected: standard wave + φ correction
    dlog = standard_delta + correction * np.exp(-MIDPOINT_OFFSET)

    return log_val + dlog


# ─── Data loaders ────────────────────────────────────────────────────

def load_sunspot_annual():
    ssn_path = os.path.join(os.path.dirname(__file__), '..', 'solar_test', 'sunspots.txt')
    monthly = {}
    with open(ssn_path) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                year = int(parts[0])
                ssn = float(parts[3])
                if ssn < 0:
                    continue
                monthly.setdefault(year, []).append(ssn)
            except ValueError:
                continue
    annual = {}
    for y, vals in monthly.items():
        if len(vals) >= 6:
            annual[y] = np.mean(vals)
    return annual

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

# ─── Oscillation diagnostic ─────────────────────────────────────────

def oscillation_test(predict_fn, label, C, R_matter=ARA_SSN, start_offset=0.5):
    log_val = C + start_offset
    prev_delta = 0
    turns = 0
    vals = []
    for yr in range(30):
        new_log = predict_fn(log_val, C, R_matter, step_years=1)
        delta = new_log - log_val
        if yr > 0 and np.sign(delta) != np.sign(prev_delta) and prev_delta != 0:
            turns += 1
        prev_delta = delta
        vals.append(10**log_val)
        log_val = new_log

    # Check range of predictions
    vmin, vmax = min(vals), max(vals)
    print(f"  {label}: turns={turns}/29, range=[{vmin:.1f}, {vmax:.1f}], "
          f"final={vals[-1]:.1f}")
    return turns

# ─── Blind test ──────────────────────────────────────────────────────

def run_blind(data, cutoffs, R_matter, name, predict_fn):
    results = []
    for cutoff in cutoffs:
        train = {y: v for y, v in data.items() if y < cutoff}
        test  = {y: v for y, v in data.items() if y >= cutoff}
        if len(train) < 10 or len(test) < 5:
            continue

        C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
        start_year = max(train.keys())
        start_val = max(data[start_year], 0.1)
        test_years = sorted(test.keys())

        seq_preds = []
        current_log = np.log10(start_val)
        for y in test_years:
            current_log = predict_fn(current_log, C, R_matter, step_years=1)
            seq_preds.append(10**current_log)

        actuals = [data[y] for y in test_years]
        naive_val = start_val
        n = len(test_years)

        def corr(a, b):
            a, b = np.array(a), np.array(b)
            if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
                return 0
            return float(np.corrcoef(a, b)[0, 1])

        def mae(a, b):
            return float(np.mean(np.abs(np.array(a) - np.array(b))))

        def beats(preds, acts, naive):
            return sum(1 for p, a in zip(preds, acts)
                       if abs(p - a) < abs(naive - a)) / len(acts) * 100

        def within_x(preds, acts, f=2):
            return sum(1 for p, a in zip(preds, acts)
                       if 1/f <= max(p,0.1)/max(a,0.1) <= f) / len(acts) * 100

        def direction(preds, acts):
            m, t = 0, 0
            for i in range(1, len(acts)):
                if np.sign(acts[i] - acts[i-1]) != 0:
                    t += 1
                    if np.sign(preds[i] - preds[i-1]) == np.sign(acts[i] - acts[i-1]):
                        m += 1
            return m / max(t, 1) * 100

        results.append({
            'cutoff': cutoff,
            'corr': corr(seq_preds, actuals),
            'beats': beats(seq_preds, actuals, naive_val),
            'x2': within_x(seq_preds, actuals),
            'dir': direction(seq_preds, actuals),
            'mae': mae(seq_preds, actuals),
            'naive_mae': mae([naive_val]*n, actuals),
            'preds': seq_preds[:12],
            'actuals': actuals[:12],
            'years': test_years[:12],
            'naive': naive_val,
        })

    return results

def print_results(results, name):
    print(f"\n  {name}:")
    for r in results:
        print(f"    Cutoff {r['cutoff']}: corr={r['corr']:+.3f}, MAE={r['mae']:.1f}, "
              f"beats={r['beats']:.0f}%, dir={r['dir']:.0f}%, ×2={r['x2']:.0f}% "
              f"(naive={r['naive_mae']:.1f})")

def print_trajectory(results, name):
    """Show first cutoff's trajectory in detail."""
    print(f"\n  {name} — Cutoff {results[0]['cutoff']} trajectory:")
    print(f"    {'Year':>6} {'Actual':>8} {'Pred':>8} {'Naive':>6}")
    for i in range(min(12, len(results[0]['years']))):
        print(f"    {results[0]['years'][i]:>6} {results[0]['actuals'][i]:>8.1f} "
              f"{results[0]['preds'][i]:>8.1f} {results[0]['naive']:>6.0f}")

def score(ssn_r, eq_r):
    s = 0
    checks = []

    avg_corr = np.mean([r['corr'] for r in ssn_r])
    p = avg_corr > 0.3
    if p: s += 1
    checks.append(f"  [{'PASS' if p else 'FAIL'}] SSN corr: {avg_corr:.3f} (> 0.3)")

    bn = sum(1 for r in ssn_r if r['beats'] > 50)
    p = bn >= 3
    if p: s += 1
    checks.append(f"  [{'PASS' if p else 'FAIL'}] SSN beats naive: {bn}/6 (≥ 3)")

    ax = np.mean([r['x2'] for r in ssn_r])
    p = ax > 30
    if p: s += 1
    checks.append(f"  [{'PASS' if p else 'FAIL'}] SSN within 2×: {ax:.0f}% (> 30%)")

    ad = np.mean([r['dir'] for r in ssn_r])
    p = ad > 55
    if p: s += 1
    checks.append(f"  [{'PASS' if p else 'FAIL'}] SSN direction: {ad:.0f}% (> 55%)")

    ec = np.mean([r['corr'] for r in eq_r])
    p = ec > 0.2
    if p: s += 1
    checks.append(f"  [{'PASS' if p else 'FAIL'}] EQ corr: {ec:.3f} (> 0.2)")

    ex = np.mean([r['x2'] for r in eq_r])
    p = ex > 30
    if p: s += 1
    checks.append(f"  [{'PASS' if p else 'FAIL'}] EQ within 2×: {ex:.0f}% (> 30%)")

    bm = sum(1 for r in ssn_r if r['mae'] < r['naive_mae'])
    p = bm >= 3
    if p: s += 1
    checks.append(f"  [{'PASS' if p else 'FAIL'}] SSN lower MAE: {bm}/6 (≥ 3)")

    nb = all(r['mae'] < 500 for r in ssn_r)
    p = nb
    if p: s += 1
    checks.append(f"  [{'PASS' if p else 'FAIL'}] No drift (MAE < 500)")

    return s, checks

# ─── Main ────────────────────────────────────────────────────────────

if __name__ == '__main__':
    ssn = load_sunspot_annual()
    eq  = load_earthquake_annual()
    cutoffs = [1990, 1995, 2000, 2005, 2010, 2015]

    C_ssn = np.mean(np.log10([max(v, 0.1) for v in ssn.values()]))

    # ─── Oscillation diagnostic ──────────────────────────────────────
    print("="*70)
    print("OSCILLATION DIAGNOSTIC (starting high, C+0.5)")
    print("="*70)

    oscillation_test(standard_predict, "Standard (reference)", C_ssn)
    oscillation_test(phi_stable, "φ-stable V4 (reference)", C_ssn)

    versions = [
        ("V1: sequential nest", inside_outside_v1),
        ("V2: additive deltas", inside_outside_v2),
        ("V3: golden-weighted", inside_outside_v3),
        ("V4: scaled wave", inside_outside_v4),
        ("V5: attractor+impulse", inside_outside_v5),
        ("V6: inner-longitude outer-wave", inside_outside_v6),
    ]

    for label, fn in versions:
        oscillation_test(fn, label, C_ssn)

    print(f"\n{'='*70}")
    print("OSCILLATION DIAGNOSTIC (starting low, C-0.8)")
    print("="*70)

    for label, fn in versions:
        oscillation_test(fn, label, C_ssn, start_offset=-0.8)

    # ─── Blind tests ─────────────────────────────────────────────────
    all_scores = {}
    for label, fn in versions:
        print(f"\n{'#'*70}")
        print(f"# {label}")
        print(f"{'#'*70}")

        ssn_r = run_blind(ssn, cutoffs, ARA_SSN, f"SSN", fn)
        eq_r  = run_blind(eq,  cutoffs, ARA_EQ,  f"EQ",  fn)

        print_results(ssn_r, "SSN")
        print_trajectory(ssn_r, "SSN")
        print_results(eq_r, "EQ")
        print_trajectory(eq_r, "EQ")

        s, checks = score(ssn_r, eq_r)
        print(f"\n  VERDICT:")
        for c in checks:
            print(c)
        print(f"\n  SCORE: {s}/8")
        all_scores[label] = s

    # ─── Final comparison ────────────────────────────────────────────
    print(f"\n{'='*70}")
    print("GRAND COMPARISON — ALL SCRIPTS")
    print(f"{'='*70}")
    print(f"  Script 167 (undampened):              0/8")
    print(f"  Script 168 (5 sub-systems):           2/8")
    print(f"  Script 169 (paired φ):                1/8")
    print(f"  Script 170 V4 (φ inside longitude):   6/8  ← previous best")
    for label, s in all_scores.items():
        marker = " ← NEW BEST" if s > 6 else " ← TIES BEST" if s == 6 else ""
        print(f"  Script 171 {label}: {s}/8{marker}")

    print(f"\nScript 171 complete.")
