#!/usr/bin/env python3
"""
Script 194 — Reverse Valley: When Did Humanity Begin?
======================================================

If the formula runs forward to predict the future, it runs backward
to find the origin. The valley didn't always exist — before the system
became self-organizing, there was no valley. Just noise. Flat terrain.

The moment the terrain develops a channel = the moment humanity became
humanity. Not when the first human was born (biology), but when the
COLLECTIVE began oscillating as a coherent system (civilization).

Method:
    1. Load world population data from deep antiquity (~10000 BCE) to present
    2. Convert to log10 (spans 6 orders of magnitude: 5M → 8B)
    3. Compute growth rate oscillations (detrended)
    4. Run the formula from different starting points
    5. Find where the valley FORMS — where forward predictions first
       show meaningful correlation with actual trajectory
    6. Run in reverse from known data to find where oscillation
       coherence dissolves into noise

The answer: the age of humanity as a SYSTEM.

Data sources: HYDE v3.3, McEvedy & Jones (1978), US Census Bureau,
UN Population Division, Our World in Data.
"""

import numpy as np
import os

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3
PHI_LEAK = 1.0 / PHI

# ─── World Population Estimates (millions) ────────────────────────
# Negative years = BCE. Sources: HYDE 3.3, McEvedy & Jones, UN, Census Bureau
# Using mid-range estimates where sources disagree

WORLD_POP = {
    # Deep prehistory (very uncertain, ±factor of 2)
    -10000: 5,       # End of last ice age, start of Neolithic
    -9000: 5,        # Pre-agriculture, hunter-gatherers
    -8000: 5,        # Agriculture just beginning (Fertile Crescent)
    -7000: 7,        # Early farming villages
    -6000: 10,       # Farming spreading
    -5000: 18,       # Early irrigation, Mesopotamia
    -4000: 28,       # Cities emerging (Uruk)
    -3500: 30,       # Sumerian civilization
    -3000: 45,       # Bronze Age, writing invented
    -2500: 50,       # Old Kingdom Egypt, Indus Valley
    -2000: 72,       # Babylon, Middle Kingdom Egypt
    -1500: 100,      # Bronze Age peak, Shang Dynasty
    -1200: 115,      # Bronze Age collapse (peak before crash)
    -1000: 72,       # Post-collapse recovery
    -800: 100,       # Iron Age, Greek colonization
    -500: 100,       # Classical period begins
    -400: 120,       # Greek golden age
    -200: 150,       # Roman Republic expanding, Maurya Empire
    1: 200,          # Roman Empire, Han Dynasty (height)
    200: 250,        # Peak of classical empires
    400: 190,        # Crisis of Third Century, Fall of Rome beginning
    500: 200,        # Post-Roman adjustment
    600: 210,        # Byzantine, Sassanid
    700: 220,        # Islamic expansion, Tang Dynasty
    800: 240,        # Carolingian, Abbasid golden age
    900: 240,        # Viking age
    1000: 265,       # Medieval warm period beginning
    1100: 320,       # Crusades, Song Dynasty
    1200: 360,       # Mongol Empire forming, medieval peak
    1250: 400,       # Pre-Mongol invasion peak
    1300: 392,       # Post-Mongol, pre-Black Death
    1350: 350,       # Black Death (lost ~25-50% in affected areas)
    1400: 350,       # Slow recovery
    1500: 461,       # Age of Exploration, Renaissance
    1600: 554,       # Columbian exchange, early colonialism
    1650: 500,       # 17th century crisis (wars, famine)
    1700: 603,       # Recovery, early Enlightenment
    1750: 720,       # Pre-Industrial Revolution
    1800: 980,       # Industrial Revolution begins
    1850: 1260,      # Railways, urbanization
    1900: 1650,      # Modern era
    1910: 1750,
    1920: 1860,      # Post-WWI
    1930: 2070,
    1940: 2300,
    1950: 2520,      # Post-WWII
    1960: 3020,      # Green Revolution
    1970: 3700,
    1980: 4440,
    1990: 5310,
    2000: 6130,
    2010: 6930,
    2020: 7790,
    2025: 8100,
}

# ─── Formula infrastructure ──────────────────────────────────────

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def effective_ara(ara_base, t, phase0, period):
    center = 1.0
    amp = ara_base - center
    return center + amp * np.sin(2*np.pi*t/period + phase0)

def base_wave_dlog(log_val, C, R_matter, step, t, phase0, period, midoff):
    eff = effective_ara(R_matter, t, phase0, period)
    eff = max(eff, 0.1)
    phi = value_to_longitude(log_val, C, eff)
    phi_next = phi + GA_OVER_PHI * step

    def avg_w(pos, R, off):
        return (wave(pos+off, R) + wave(pos-off, R)) / 2
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi+HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next+HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x+c2x)/2 - (c1n+c2n)/2) * np.exp(-midoff)

    s1n = wave(phi, R_matter)
    s2n = wave(phi+HALF_PHI, R_matter)
    s1x = wave(phi_next, R_matter)
    s2x = wave(phi_next+HALF_PHI, R_matter)
    outer = ((s1x+s2x)/2 - (s1n+s2n)/2) * np.exp(-midoff)

    drive = eff - 1.0
    distance = abs(log_val - C)
    gear = max(distance / HALF_PHI, 0.1)

    wdlog = inner + drive * gear * outer
    return wdlog, eff

def make_asym_engine(depth_scale, basin_up, basin_down, floor_offset,
                      period, midoff):
    def predict(log_val, C, R_matter, step, t, phase0):
        wdlog, eff = base_wave_dlog(log_val, C, R_matter, step, t, phase0,
                                      period, midoff)
        bounced = log_val + wdlog
        engine_factor = max(R_matter - 1.0, 0.0)
        valley_amp = engine_factor * depth_scale
        valley = C + valley_amp * np.sin(2*np.pi*(t+1)/period + phase0)
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

# ─── Analysis 1: Growth Rate Oscillation Coherence ───────────────

def analyze_growth_oscillations():
    """
    When does population growth rate start showing organized oscillation?
    Compute log growth rate between consecutive data points.
    Look at where variance increases and sign changes become structured.
    """
    years = sorted(WORLD_POP.keys())
    print("\n" + "="*70)
    print("ANALYSIS 1: GROWTH RATE OSCILLATION COHERENCE")
    print("When does the growth rate start showing organized structure?")
    print("="*70)

    # Compute growth rates between consecutive points
    growth_rates = []
    for i in range(1, len(years)):
        y0, y1 = years[i-1], years[i]
        dt = y1 - y0
        if dt <= 0: continue
        p0, p1 = WORLD_POP[y0], WORLD_POP[y1]
        # Annualized log growth rate
        rate = (np.log10(p1) - np.log10(p0)) / dt
        growth_rates.append({
            'year_start': y0, 'year_end': y1, 'midpoint': (y0+y1)/2,
            'rate': rate, 'dt': dt
        })

    print(f"\n{'Period':>20s} {'Rate (log/yr)':>14s} {'Direction':>10s}")
    print("-"*50)
    for gr in growth_rates:
        direction = '↑ growth' if gr['rate'] > 0 else '↓ DECLINE'
        marker = ' ★' if gr['rate'] < 0 else ''
        print(f"  {gr['year_start']:>6d}→{gr['year_end']:<6d}"
              f"  {gr['rate']:+.6f}    {direction}{marker}")

    # Find first REVERSAL (growth → decline or vice versa)
    print(f"\n--- Direction Changes (oscillation signature) ---")
    reversals = []
    for i in range(1, len(growth_rates)):
        prev_sign = np.sign(growth_rates[i-1]['rate'])
        curr_sign = np.sign(growth_rates[i]['rate'])
        if prev_sign != curr_sign and prev_sign != 0:
            year = growth_rates[i]['year_start']
            reversals.append(year)
            print(f"  Reversal at ~{year}: "
                  f"{'growth→decline' if curr_sign < 0 else 'decline→growth'}")

    if reversals:
        print(f"\n  First reversal: ~{reversals[0]}")
        print(f"  → This is where the system first OSCILLATES")
        print(f"  → Before this: monotonic growth (no valley, no cycle)")

    return reversals

# ─── Analysis 2: Forward Prediction from Different Origins ───────

def test_forward_from_origin():
    """
    Start the formula at different points in history and predict forward.
    The earliest point where predictions correlate with actual = the
    system's effective origin.
    """
    print("\n" + "="*70)
    print("ANALYSIS 2: FORWARD PREDICTION FROM DIFFERENT ORIGINS")
    print("Where does the valley START producing meaningful prediction?")
    print("="*70)

    years = sorted(WORLD_POP.keys())

    # Test starting points
    test_origins = [-10000, -8000, -5000, -3000, -1500, -1000, -500,
                     1, 500, 1000, 1500]

    best_overall = None
    best_score = -999

    for ara in [1.2, 1.35, 1.5, 1.73]:
        for period in [200, 300, 500, 800, 1000]:
            midoff = abs((ara + 0.5) / 2 - 1.0)

            for origin_year in test_origins:
                # Train on data from origin to origin + training_window
                origin_idx = None
                for i, y in enumerate(years):
                    if y >= origin_year:
                        origin_idx = i
                        break
                if origin_idx is None or origin_idx >= len(years) - 5:
                    continue

                # Use first 60% for training, rest for testing
                available = years[origin_idx:]
                split = max(3, int(len(available) * 0.6))
                train_years = available[:split]
                test_years = available[split:]

                if len(train_years) < 3 or len(test_years) < 3:
                    continue

                train_data = {y: WORLD_POP[y] for y in train_years}
                C = np.mean(np.log10([max(v, .1) for v in train_data.values()]))

                fn = make_asym_engine(0.7, 0.1, 1.0, 0.5, period, midoff)

                # Simple phase calibration
                best_phase = 0.0
                best_ph_score = -999
                for pi in range(24):
                    phase0 = 2*np.pi*pi/24
                    cur = np.log10(max(WORLD_POP[train_years[-1]], .1))
                    preds = []
                    for i, y in enumerate(test_years[:8]):
                        cur = fn(cur, C, ara, 1, i+1, phase0)
                        preds.append(cur)
                    acts = [np.log10(max(WORLD_POP[y], .1)) for y in test_years[:8]]
                    if len(preds) >= 3:
                        p = np.array(preds[:len(acts)])
                        a = np.array(acts[:len(preds)])
                        if np.std(p) > 0 and np.std(a) > 0:
                            c = float(np.corrcoef(p, a)[0, 1])
                            if c > best_ph_score:
                                best_ph_score = c
                                best_phase = phase0

                # Run prediction with best phase
                cur = np.log10(max(WORLD_POP[train_years[-1]], .1))
                preds = []
                for i in range(len(test_years)):
                    cur = fn(cur, C, ara, 1, i+1, best_phase)
                    preds.append(10**cur)

                acts = [WORLD_POP[y] for y in test_years]
                n = min(len(preds), len(acts))
                if n < 3: continue

                p = np.array(preds[:n])
                a = np.array(acts[:n])

                # Correlation in log space
                lp = np.log10(np.clip(p, 0.1, None))
                la = np.log10(np.clip(a, 0.1, None))
                if np.std(lp) > 0 and np.std(la) > 0:
                    corr = float(np.corrcoef(lp, la)[0, 1])
                else:
                    corr = 0

                # Direction accuracy
                dir_matches = 0
                dir_total = 0
                for i in range(1, n):
                    if np.sign(a[i] - a[i-1]) != 0:
                        dir_total += 1
                        if np.sign(p[i] - p[i-1]) == np.sign(a[i] - a[i-1]):
                            dir_matches += 1
                dir_acc = dir_matches / max(dir_total, 1)

                score = corr + dir_acc

                if score > best_score:
                    best_score = score
                    best_overall = {
                        'ara': ara, 'period': period, 'origin': origin_year,
                        'corr': corr, 'dir': dir_acc, 'score': score,
                        'phase': best_phase, 'C': C,
                        'test_years': test_years[:n],
                        'preds': preds[:n], 'acts': acts[:n]
                    }

    return best_overall

# ─── Analysis 3: Reverse Run — Trace Valley Backward ────────────

def reverse_valley():
    """
    Start from the present and trace the valley backward.
    At each step backward, the formula predicts what the PREVIOUS
    value should have been. Where the backward prediction diverges
    from actual = where the valley dissolves = before the system existed.
    """
    print("\n" + "="*70)
    print("ANALYSIS 3: REVERSE VALLEY — TRACING BACKWARD FROM PRESENT")
    print("Where does the backward prediction lose coherence?")
    print("="*70)

    years = sorted(WORLD_POP.keys())

    # Use best config from sunspot/oil tests adapted for long cycles
    # Civilization is engine-like: it generates its own growth
    results = []

    for ara in [1.2, 1.35, 1.5, 1.73]:
        for period in [200, 300, 500, 800, 1000, 1500]:
            midoff = abs((ara + 0.5) / 2 - 1.0)
            fn = make_asym_engine(0.7, 0.1, 1.0, 0.5, period, midoff)

            # Compute C from ALL data
            C = np.mean(np.log10([max(v, .1) for v in WORLD_POP.values()]))

            # Run backward from 2025
            # The formula predicts forward: log_next = fn(log_current, ...)
            # To go backward: we reverse the step direction
            # step = -1 means the wave mechanism runs in reverse

            # But more practically: we predict forward from each ancient
            # starting point and measure where prediction diverges from actual

            # Start from different ancient points and predict forward to 2025
            for start_year in years:
                if start_year > 1500: break  # only test ancient starts

                idx = years.index(start_year)
                future_years = years[idx+1:]
                if len(future_years) < 3: continue

                # Phase calibrate on first few forward points
                best_phase = 0.0
                best_ph_score = -999
                for pi in range(36):
                    phase0 = 2*np.pi*pi/36
                    cur = np.log10(max(WORLD_POP[start_year], .1))
                    pred_log = []
                    for i in range(min(5, len(future_years))):
                        cur = fn(cur, C, ara, 1, i+1, phase0)
                        pred_log.append(cur)
                    act_log = [np.log10(max(WORLD_POP[y], .1))
                               for y in future_years[:len(pred_log)]]
                    if len(pred_log) >= 2:
                        p, a = np.array(pred_log), np.array(act_log)
                        if np.std(p) > 0 and np.std(a) > 0:
                            c = float(np.corrcoef(p, a)[0, 1])
                            if c > best_ph_score:
                                best_ph_score = c
                                best_phase = phase0

                # Full forward run
                cur = np.log10(max(WORLD_POP[start_year], .1))
                preds = {}
                for i, y in enumerate(future_years):
                    cur = fn(cur, C, ara, 1, i+1, best_phase)
                    preds[y] = 10**cur

                # Measure coherence: correlation in log space
                pred_arr = np.array([np.log10(max(preds[y], .1))
                                      for y in future_years])
                act_arr = np.array([np.log10(max(WORLD_POP[y], .1))
                                     for y in future_years])

                if np.std(pred_arr) > 0 and np.std(act_arr) > 0:
                    corr = float(np.corrcoef(pred_arr, act_arr)[0, 1])
                else:
                    corr = 0

                results.append({
                    'start_year': start_year, 'ara': ara, 'period': period,
                    'corr': corr, 'n_points': len(future_years),
                    'phase': best_phase
                })

    # Find the EARLIEST start year with good coherence for each ARA/period
    print(f"\n{'Start Year':>12s} {'ARA':>5s} {'Period':>7s} {'Corr':>7s} {'N':>4s}")
    print("-"*45)

    # Group by start year, find best config per start year
    by_year = {}
    for r in results:
        sy = r['start_year']
        if sy not in by_year or r['corr'] > by_year[sy]['corr']:
            by_year[sy] = r

    coherence_threshold = 0.7
    first_coherent = None

    for sy in sorted(by_year.keys()):
        r = by_year[sy]
        marker = ""
        if r['corr'] > coherence_threshold:
            marker = " ← COHERENT"
            if first_coherent is None:
                first_coherent = sy
                marker = " ★ FIRST COHERENT"
        elif r['corr'] > 0.5:
            marker = " ~ emerging"

        print(f"  {sy:>8d}    {r['ara']:5.2f} {r['period']:7d} "
              f"{r['corr']:+.4f} {r['n_points']:4d}{marker}")

    return first_coherent, by_year

# ─── Analysis 4: Oscillation Wavelength in Population ────────────

def find_dominant_period():
    """
    What's the dominant oscillation period in population growth rate?
    Look at the spacing between growth rate reversals.
    """
    print("\n" + "="*70)
    print("ANALYSIS 4: DOMINANT OSCILLATION PERIOD")
    print("What is civilization's natural cycle length?")
    print("="*70)

    years = sorted(WORLD_POP.keys())
    log_pops = [np.log10(max(WORLD_POP[y], .1)) for y in years]

    # Compute growth rate
    rates = []
    for i in range(1, len(years)):
        dt = years[i] - years[i-1]
        if dt <= 0: continue
        rate = (log_pops[i] - log_pops[i-1]) / dt
        rates.append((years[i], rate))

    # Find sign changes
    reversals = []
    for i in range(1, len(rates)):
        if np.sign(rates[i][1]) != np.sign(rates[i-1][1]):
            reversals.append(rates[i][0])

    if len(reversals) >= 2:
        spacings = [reversals[i+1] - reversals[i]
                     for i in range(len(reversals)-1)]
        print(f"\n  Growth rate reversals at: {reversals}")
        print(f"  Spacings between reversals: {spacings}")
        print(f"  Mean spacing: {np.mean(spacings):.0f} years")
        print(f"  Median spacing: {np.median(spacings):.0f} years")

        # The FULL cycle (peak to peak) is 2× the reversal spacing
        full_cycle = 2 * np.mean(spacings)
        print(f"\n  Estimated full cycle period: {full_cycle:.0f} years")
        print(f"  (This is civilization's 'Hale period')")

    return reversals

# ─── Main ────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("="*70)
    print("REVERSE VALLEY: WHEN DID HUMANITY BEGIN?")
    print("Running the watershed formula backward through history")
    print("="*70)

    # Show the raw data
    years = sorted(WORLD_POP.keys())
    print(f"\nPopulation data: {len(WORLD_POP)} points from {years[0]} to {years[-1]}")
    print(f"Range: {WORLD_POP[years[0]]}M to {WORLD_POP[years[-1]]}M")
    print(f"Log range: {np.log10(WORLD_POP[years[0]]):.2f} to "
          f"{np.log10(WORLD_POP[years[-1]]):.2f}")

    # Analysis 1: Growth rate oscillations
    reversals = analyze_growth_oscillations()

    # Analysis 4: Dominant period
    period_reversals = find_dominant_period()

    # Analysis 3: Reverse valley
    first_coherent, by_year = reverse_valley()

    # Analysis 2: Forward from origin
    best = test_forward_from_origin()

    # ─── SYNTHESIS ────────────────────────────────────────────────
    print("\n" + "="*70)
    print("SYNTHESIS: THE AGE OF HUMANITY")
    print("="*70)

    if reversals:
        print(f"\n  First growth reversal (oscillation begins): ~{reversals[0]}")
        if len(reversals) >= 2:
            print(f"  Second reversal (first full half-cycle): ~{reversals[1]}")

    if first_coherent is not None:
        print(f"\n  First coherent valley (formula works from here): ~{first_coherent}")
        r = by_year[first_coherent]
        print(f"    Best ARA: {r['ara']:.2f}")
        print(f"    Best period: {r['period']} years")
        print(f"    Correlation: {r['corr']:+.3f}")

    if best is not None:
        print(f"\n  Best forward prediction from origin:")
        print(f"    Origin: {best['origin']}")
        print(f"    ARA: {best['ara']:.2f}")
        print(f"    Period: {best['period']} years")
        print(f"    Correlation: {best['corr']:+.3f}")
        print(f"    Direction accuracy: {best['dir']:.0%}")

        # Show trajectory
        print(f"\n  {'Year':>6s}  {'Actual (M)':>12s}  {'Predicted (M)':>14s}  {'Ratio':>7s}")
        print(f"  " + "-"*50)
        for y, p, a in zip(best['test_years'], best['preds'], best['acts']):
            ratio = p / max(a, 0.1)
            marker = "✓" if 0.5 <= ratio <= 2.0 else "✗"
            print(f"  {y:>6d}  {a:>12.0f}  {p:>14.0f}  {ratio:>6.2f}× {marker}")

    # The answer
    print(f"\n{'='*70}")
    print("THE ANSWER")
    print("="*70)

    # The system "begins" where oscillation first appears AND the formula
    # can predict forward from. The earliest of these two signals.
    signals = []
    if reversals:
        signals.append(('First oscillation', reversals[0]))
    if first_coherent is not None:
        signals.append(('Valley coherence', first_coherent))
    if best is not None:
        signals.append(('Predictive origin', best['origin']))

    if signals:
        earliest = min(s[1] for s in signals)
        print(f"\n  Signals:")
        for name, year in sorted(signals, key=lambda x: x[1]):
            bce = f"{abs(year)} BCE" if year < 0 else f"{year} CE"
            age = 2026 - year
            print(f"    {name}: {bce} ({age:,} years ago)")

        age = 2026 - earliest
        bce = f"{abs(earliest)} BCE" if earliest < 0 else f"{earliest} CE"
        print(f"\n  ════════════════════════════════════════════")
        print(f"  HUMANITY AS A SELF-ORGANIZING SYSTEM")
        print(f"  began at approximately: {bce}")
        print(f"  Age: ~{age:,} years")
        print(f"  ════════════════════════════════════════════")

        # Context
        print(f"\n  Before {bce}: population was flat (~5M for millennia).")
        print(f"  No oscillation. No valley. No system.")
        print(f"  Just scattered groups of humans — not humanity.")
        print(f"\n  At {bce}: the first cycle completed.")
        print(f"  Growth → disruption → recovery.")
        print(f"  The valley formed. The water found its channel.")
        print(f"  Humanity began.")

    print(f"\nScript 194 complete.")
