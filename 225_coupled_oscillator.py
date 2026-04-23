#!/usr/bin/env python3
"""
Script 225 — Coupled Oscillator Cascade

THE SNAP: Phases are not clock functions. They EVOLVE.

Previous architecture (Scripts 201-224):
    phase_j = 2π × t / φⁿ          ← replay: ball on rails
    collision modifies amplitude only

New architecture:
    phase_j[t+1] = phase_j[t] + 2π/φⁿ + coupling   ← driving: ball bounces
    collision feeds back into PHASE, not just amplitude

The coupling term IS the collision we already compute. We just route it
differently: into the oscillator's phase, where it changes future collisions.

Coupled oscillators with irrational frequency ratios fill phase space
quasi-periodically — the irrational plane emerges from the dynamics,
not from a bolted-on gate.

Constants: all from φ. No new parameters.
Fitted: ba (baseline amplitude), tr (time reference) — same as before.
"""

import numpy as np
import warnings, time
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9
LOG2 = np.log(2)

# =====================================================================
# DATA
# =====================================================================
CYCLES = {
    1:  (1755.2, 1761.5, 144.1, 11.3), 2:  (1766.5, 1769.7, 193.0, 9.0),
    3:  (1775.5, 1778.4, 264.3, 9.3),  4:  (1784.7, 1788.1, 235.3, 13.6),
    5:  (1798.3, 1805.2, 82.0,  12.3), 6:  (1810.6, 1816.4, 81.2,  12.7),
    7:  (1823.3, 1829.9, 119.2, 10.5), 8:  (1833.8, 1837.2, 244.9, 9.7),
    9:  (1843.5, 1848.1, 219.9, 12.4), 10: (1855.9, 1860.1, 186.2, 11.3),
    11: (1867.2, 1870.6, 234.0, 11.8), 12: (1878.9, 1883.9, 124.4, 11.3),
    13: (1890.2, 1894.1, 146.5, 11.8), 14: (1902.0, 1906.2, 107.1, 11.5),
    15: (1913.5, 1917.6, 175.7, 10.1), 16: (1923.6, 1928.4, 130.2, 10.1),
    17: (1933.8, 1937.4, 198.6, 10.4), 18: (1944.2, 1947.5, 218.7, 10.2),
    19: (1954.3, 1958.2, 285.0, 10.5), 20: (1964.9, 1968.9, 156.6, 11.7),
    21: (1976.5, 1979.9, 232.9, 10.3), 22: (1986.8, 1989.6, 212.5, 9.7),
    23: (1996.4, 2001.9, 180.3, 12.3), 24: (2008.0, 2014.3, 116.4, 11.0),
    25: (2019.5, 2024.5, 173.0, 11.0),
}

cycle_nums = sorted(CYCLES.keys())
start_years = np.array([CYCLES[c][0] for c in cycle_nums])
peak_years  = np.array([CYCLES[c][1] for c in cycle_nums])
peak_amps   = np.array([CYCLES[c][2] for c in cycle_nums])
durations   = np.array([CYCLES[c][3] for c in cycle_nums])
rise_fracs  = (peak_years - start_years) / durations
N = len(cycle_nums)

SCHWABE = PHI**5
GLEISSBERG = PHI**9
SUN_ACC = PHI / (PHI + 1)

# Natural periods of the cascade oscillators
PERIODS = [PHI**11, PHI**9, PHI**6, PHI**4]
N_OSC = len(PERIODS)

def mae(p, o): return np.mean(np.abs(np.array(p) - np.array(o)))

def sawtooth_valve(phase, acc_frac):
    acc_frac = max(0.15, min(0.85, acc_frac))
    cp = (phase % (2*np.pi)) / (2*np.pi)
    if cp < acc_frac: state = (cp / acc_frac) * PHI
    else:
        ramp = (cp - acc_frac) / (1 - acc_frac)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    return state / ((PHI + INV_PHI) / 2)

def ara_to_acc(v): return 1.0 / (1.0 + max(0.01, v))

def sing_pulse_decay(phase, dr):
    cp = (phase % (2*np.pi)) / (2*np.pi)
    return np.exp(-dr * cp)


# =====================================================================
# MODEL A: 223o CHAMPION (fixed phases — baseline for comparison)
# =====================================================================
def mk_fixed_phase(h_cc=INV_PHI_3):
    """The proven champion. Phases from clock. No phase coupling."""
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            gp = 2 * np.pi * (t - tr) / GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            phases = [2 * np.pi * (t - tr) / per for per in PERIODS]
            cos_vals = [np.cos(ph) for ph in phases]
            sin_vals = [np.sin(ph) for ph in phases]

            amp = ba
            for j in range(N_OSC):
                w = cos_vals[j]
                eps = INV_PHI_4 * gate

                if j > 0:
                    phase_diff = phases[j-1] - phases[j]
                    collision = -np.cos(phase_diff)
                    eps *= (1 + collision * INV_PHI)

                tens = -sin_vals[j]
                log_tens = np.sign(tens) * np.log1p(abs(tens)) / LOG2
                if log_tens > 0: eps *= (1 + 0.5 * log_tens * (PHI - 1))
                else:            eps *= (1 + 0.5 * log_tens * (1 - INV_PHI))

                amp *= (1 + eps * w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2 * np.pi * (t - tr) / SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                grief_mult = PHI if prev_dev < 0 else 1.0
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI) * grief_mult

            preds.append(amp)
        return preds
    return _p


# =====================================================================
# MODEL B: COUPLED OSCILLATOR (phases evolve via collision feedback)
# =====================================================================
def mk_coupled_osc(coupling_strength=INV_PHI_4, h_cc=INV_PHI_3):
    """
    THE NEW ARCHITECTURE.

    Each cascade level is an oscillator with natural frequency 2π/φⁿ.
    At each time step (cycle), the oscillator advances by its natural
    frequency PLUS a coupling term from its collision with neighbors.

    The coupling term is the same collision math we already use —
    it just feeds into the phase evolution instead of only into amplitude.

    The phase shift from collision means:
    - When two adjacent oscillators are in-phase (collision strong),
      they pull each other's phases — partial synchronization
    - When out-of-phase (collision weak), they drift freely
    - The irrational frequency ratios prevent full lock-in,
      so the system fills phase space quasi-periodically

    coupling_strength controls how much collision feeds back into phase.
    At 0, this reduces to the fixed-phase champion (Model A).
    """
    def _p(years, amps, ba, tr):
        preds = []

        # Initialize phases from tr (same starting point as fixed model)
        # But from here on, they EVOLVE
        phases = [2 * np.pi * (years[0] - tr) / per for per in PERIODS]

        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            gp = 2 * np.pi * (t - tr) / GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            cos_vals = [np.cos(ph) for ph in phases]
            sin_vals = [np.sin(ph) for ph in phases]

            # --- Compute collisions (same math as champion) ---
            collisions = [0.0] * N_OSC
            for j in range(1, N_OSC):
                phase_diff = phases[j-1] - phases[j]
                collisions[j] = -np.cos(phase_diff)

            # --- Amplitude modulation (same as champion) ---
            amp = ba
            for j in range(N_OSC):
                w = cos_vals[j]
                eps = INV_PHI_4 * gate

                if j > 0:
                    eps *= (1 + collisions[j] * INV_PHI)

                tens = -sin_vals[j]
                log_tens = np.sign(tens) * np.log1p(abs(tens)) / LOG2
                if log_tens > 0: eps *= (1 + 0.5 * log_tens * (PHI - 1))
                else:            eps *= (1 + 0.5 * log_tens * (1 - INV_PHI))

                amp *= (1 + eps * w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2 * np.pi * (t - tr) / SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                grief_mult = PHI if prev_dev < 0 else 1.0
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI) * grief_mult

            preds.append(amp)

            # --- THE NEW PART: Evolve phases for next step ---
            if i < len(years) - 1:
                dt = years[i+1] - years[i]  # actual time step (not fixed!)
                for j in range(N_OSC):
                    # Natural advance: 2π × dt / period
                    natural = 2 * np.pi * dt / PERIODS[j]

                    # Coupling: collision with neighbors shifts phase
                    # Collision with level above (j-1) and below (j+1)
                    phase_kick = 0.0
                    if j > 0:
                        # Coupling from parent: collision pulls phase
                        phase_kick += collisions[j] * coupling_strength
                    if j < N_OSC - 1:
                        # Coupling from child: collision at j+1 also
                        # involves level j, but at 1/φ strength (scale down)
                        phase_kick += collisions[j+1] * coupling_strength * INV_PHI

                    phases[j] += natural + phase_kick

        return preds
    return _p


# =====================================================================
# MODEL C: COUPLED + AMPLITUDE FEEDBACK
# =====================================================================
def mk_coupled_amp_feedback(coupling_strength=INV_PHI_4, h_cc=INV_PHI_3):
    """
    Coupled oscillator + the observed amplitude feeds back into phase.

    The ball doesn't just respond to collisions — it responds to the
    RESULT of its last journey. If the previous cycle was strong,
    the phases shift differently than if it was weak.

    This is the vehicle responding to the terrain it just drove through.
    """
    def _p(years, amps, ba, tr):
        preds = []
        phases = [2 * np.pi * (years[0] - tr) / per for per in PERIODS]

        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            gp = 2 * np.pi * (t - tr) / GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            cos_vals = [np.cos(ph) for ph in phases]
            sin_vals = [np.sin(ph) for ph in phases]

            collisions = [0.0] * N_OSC
            for j in range(1, N_OSC):
                phase_diff = phases[j-1] - phases[j]
                collisions[j] = -np.cos(phase_diff)

            amp = ba
            for j in range(N_OSC):
                w = cos_vals[j]
                eps = INV_PHI_4 * gate

                if j > 0:
                    eps *= (1 + collisions[j] * INV_PHI)

                tens = -sin_vals[j]
                log_tens = np.sign(tens) * np.log1p(abs(tens)) / LOG2
                if log_tens > 0: eps *= (1 + 0.5 * log_tens * (PHI - 1))
                else:            eps *= (1 + 0.5 * log_tens * (1 - INV_PHI))

                amp *= (1 + eps * w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2 * np.pi * (t - tr) / SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                grief_mult = PHI if prev_dev < 0 else 1.0
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI) * grief_mult

            preds.append(amp)

            # --- Evolve phases with BOTH collision AND amplitude feedback ---
            if i < len(years) - 1:
                dt = years[i+1] - years[i]

                # How far was the previous amplitude from baseline?
                # This is the "terrain response" — strong cycle pushes phases forward,
                # weak cycle lets them drift
                amp_dev = (amps[i] - ba) / ba if i < len(amps) else 0.0

                for j in range(N_OSC):
                    natural = 2 * np.pi * dt / PERIODS[j]

                    # Collision coupling (same as Model B)
                    phase_kick = 0.0
                    if j > 0:
                        phase_kick += collisions[j] * coupling_strength
                    if j < N_OSC - 1:
                        phase_kick += collisions[j+1] * coupling_strength * INV_PHI

                    # Amplitude feedback: observed amplitude shifts phase
                    # Strong cycle (amp_dev > 0) = ball pushed further = phase advances
                    # Weak cycle (amp_dev < 0) = ball slowed = phase retards
                    # Scale by 1/φ² so it's a gentle nudge, not a shove
                    amp_kick = amp_dev * coupling_strength * INV_PHI

                    phases[j] += natural + phase_kick + amp_kick

        return preds
    return _p


# =====================================================================
# MODEL D: MULTIPLICATIVE COUPLING (frequency modulation, no drift)
# =====================================================================
def mk_freq_modulated(coupling_strength=INV_PHI_4, h_cc=INV_PHI_3):
    """
    THE FIX: collision modulates FREQUENCY, not phase.

    Instead of: phase += natural + kick        (additive — drifts)
    We use:     phase += natural × (1 + kick)  (multiplicative — stable)

    When collision=0, ball moves at natural speed. No drift accumulation.
    When collision≠0, ball speeds up or slows down temporarily.
    The ball bounces off walls (speed changes) but doesn't teleport.
    """
    def _p(years, amps, ba, tr):
        preds = []
        phases = [2 * np.pi * (years[0] - tr) / per for per in PERIODS]

        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            gp = 2 * np.pi * (t - tr) / GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            cos_vals = [np.cos(ph) for ph in phases]
            sin_vals = [np.sin(ph) for ph in phases]

            collisions = [0.0] * N_OSC
            for j in range(1, N_OSC):
                phase_diff = phases[j-1] - phases[j]
                collisions[j] = -np.cos(phase_diff)

            amp = ba
            for j in range(N_OSC):
                w = cos_vals[j]
                eps = INV_PHI_4 * gate

                if j > 0:
                    eps *= (1 + collisions[j] * INV_PHI)

                tens = -sin_vals[j]
                log_tens = np.sign(tens) * np.log1p(abs(tens)) / LOG2
                if log_tens > 0: eps *= (1 + 0.5 * log_tens * (PHI - 1))
                else:            eps *= (1 + 0.5 * log_tens * (1 - INV_PHI))

                amp *= (1 + eps * w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2 * np.pi * (t - tr) / SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                grief_mult = PHI if prev_dev < 0 else 1.0
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI) * grief_mult

            preds.append(amp)

            # --- MULTIPLICATIVE phase evolution ---
            if i < len(years) - 1:
                dt = years[i+1] - years[i]
                for j in range(N_OSC):
                    natural = 2 * np.pi * dt / PERIODS[j]

                    # Speed modulation from collisions
                    speed_mod = 0.0
                    if j > 0:
                        speed_mod += collisions[j] * coupling_strength
                    if j < N_OSC - 1:
                        speed_mod += collisions[j+1] * coupling_strength * INV_PHI

                    # Multiplicative: frequency changes, no drift
                    phases[j] += natural * (1 + speed_mod)

        return preds
    return _p


# =====================================================================
# MODEL E: FREQ MODULATION + AMPLITUDE FEEDBACK
# =====================================================================
def mk_freq_mod_amp(coupling_strength=INV_PHI_4, h_cc=INV_PHI_3):
    """
    Multiplicative frequency modulation + amplitude terrain response.
    Strong previous cycle = ball moves faster through the corridor.
    Weak previous cycle = ball moves slower.
    """
    def _p(years, amps, ba, tr):
        preds = []
        phases = [2 * np.pi * (years[0] - tr) / per for per in PERIODS]

        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            gp = 2 * np.pi * (t - tr) / GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            cos_vals = [np.cos(ph) for ph in phases]
            sin_vals = [np.sin(ph) for ph in phases]

            collisions = [0.0] * N_OSC
            for j in range(1, N_OSC):
                phase_diff = phases[j-1] - phases[j]
                collisions[j] = -np.cos(phase_diff)

            amp = ba
            for j in range(N_OSC):
                w = cos_vals[j]
                eps = INV_PHI_4 * gate

                if j > 0:
                    eps *= (1 + collisions[j] * INV_PHI)

                tens = -sin_vals[j]
                log_tens = np.sign(tens) * np.log1p(abs(tens)) / LOG2
                if log_tens > 0: eps *= (1 + 0.5 * log_tens * (PHI - 1))
                else:            eps *= (1 + 0.5 * log_tens * (1 - INV_PHI))

                amp *= (1 + eps * w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2 * np.pi * (t - tr) / SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                grief_mult = PHI if prev_dev < 0 else 1.0
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI) * grief_mult

            preds.append(amp)

            # --- MULTIPLICATIVE with amplitude terrain ---
            if i < len(years) - 1:
                dt = years[i+1] - years[i]
                amp_dev = (amps[i] - ba) / ba

                for j in range(N_OSC):
                    natural = 2 * np.pi * dt / PERIODS[j]

                    speed_mod = 0.0
                    if j > 0:
                        speed_mod += collisions[j] * coupling_strength
                    if j < N_OSC - 1:
                        speed_mod += collisions[j+1] * coupling_strength * INV_PHI

                    # Amplitude terrain: strong cycle = faster ball
                    speed_mod += amp_dev * coupling_strength * INV_PHI

                    phases[j] += natural * (1 + speed_mod)

        return preds
    return _p


# =====================================================================
# FITTING + EVALUATION
# =====================================================================
def fit_q(fn, mask, ay, aa):
    best, bba, btr = 1e9, 0, 0
    idx = np.where(mask)[0]; ta = aa[mask]
    for tr in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(ta) * 0.6, np.mean(ta) * 1.4, 40):
            ap = fn(ay, aa, ba, tr)
            m = mae([ap[j] for j in idx], ta)
            if m < best: best, bba, btr = m, ba, tr
    return bba, btr, best


def evaluate(label, fn):
    pe, se = [], []
    fm = np.ones(N, dtype=bool)
    for i in range(N):
        mask = np.ones(N, dtype=bool); mask[i] = False
        ba, tr, _ = fit_q(fn, mask, peak_years, peak_amps)
        pi = fn(peak_years, peak_amps, ba, tr)[i]
        pe.append(abs(pi - peak_amps[i]))
        se.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))
    pe, se = np.array(pe), np.array(se)
    loo, sl = pe.mean(), se.mean()

    bf, tf, _ = fit_q(fn, fm, peak_years, peak_amps)
    pf = fn(peak_years, peak_amps, bf, tf)
    ef = np.array(pf) - peak_amps
    rr = np.corrcoef(rise_fracs, ef)[0, 1]

    sw = 0
    splits_detail = []
    for nt in [5, 8, 10, 12, 15, 18, 20]:
        if nt >= N: continue
        tm = np.zeros(N, dtype=bool); tm[:nt] = True
        bs, ts, _ = fit_q(fn, tm, peak_years, peak_amps)
        tp = fn(peak_years, peak_amps, bs, ts)[nt:]
        ta = peak_amps[nt:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:nt].mean()), ta)
        w = "phi" if pm < sm else "sine"
        if pm < sm: sw += 1
        splits_detail.append((nt, N - nt, pm, sm, w))

    return {'label': label, 'loo': loo, 'sine': sl, 'imp': (loo/sl - 1) * 100,
            'rr': rr, 'sw': sw, 'sd': splits_detail, 'pf': pf, 'ba': bf, 'tr': tf}


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    t0 = time.time()
    print("=" * 70)
    print("SCRIPT 225 — COUPLED OSCILLATOR CASCADE")
    print("=" * 70)
    print(f"""
  THE SNAP: phases evolve via collision feedback.

  Model A: Fixed phases (223o champion baseline)
  Model D: Frequency modulation — collision speeds/slows ball (no drift)
  Model E: Freq modulation + amplitude terrain response

  Key insight: collision modulates SPEED not POSITION.
  No new parameters. Same ba, tr grid search.
""")

    results = []

    # --- Model A: Fixed-phase champion ---
    print("Model A: Fixed phases (champion baseline)...")
    fn_a = mk_fixed_phase()
    r = evaluate("A: Fixed", fn_a)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}  r={r['rr']:+.3f}  s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # --- Model D: Frequency modulation (multiplicative, no drift) ---
    coupling_vals = [
        ('1/φ⁴', INV_PHI**4),
        ('1/φ³', INV_PHI**3),
        ('1/φ²', INV_PHI**2),
        ('1/φ',  INV_PHI),
    ]

    for clabel, cval in coupling_vals:
        print(f"\nModel D: Freq mod c={clabel}...")
        fn_d = mk_freq_modulated(coupling_strength=cval)
        r = evaluate(f"D: c={clabel}", fn_d)
        results.append(r)
        print(f"  LOO={r['loo']:.2f}  r={r['rr']:+.3f}  s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # --- Model E: Freq mod + amplitude feedback ---
    for clabel, cval in coupling_vals:
        print(f"\nModel E: Freq+amp c={clabel}...")
        fn_e = mk_freq_mod_amp(coupling_strength=cval)
        r = evaluate(f"E: c={clabel}", fn_e)
        results.append(r)
        print(f"  LOO={r['loo']:.2f}  r={r['rr']:+.3f}  s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # --- RESULTS ---
    results.sort(key=lambda r: r['loo'])
    best = results[0]

    print(f"\n{'='*70}")
    print("RESULTS (sorted by LOO)")
    print(f"{'='*70}")
    print(f"\n  {'Model':<20s} {'LOO':>7s} {'%sine':>7s} {'Rise r':>7s} {'Split':>5s}")
    print(f"  {'-'*20} {'-'*7} {'-'*7} {'-'*7} {'-'*5}")
    for r in results:
        marker = " ★" if r['loo'] < results[0]['loo'] + 0.01 else ""
        print(f"  {r['label']:<20s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['rr']:+7.3f} {r['sw']:2d}/7{marker}")

    # --- TEMPORAL SPLITS for top 3 ---
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS (top 3)")
    print(f"{'='*70}")
    for r in results[:3]:
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            mg = sm - pm if w == "phi" else pm - sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: phi={pm:.1f} sine={sm:.1f} -> {w} ({mg:.1f})")

    # --- PER-CYCLE for best ---
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {best['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s}")
    for i, c in enumerate(cycle_nums):
        p = best['pf'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} {p - peak_amps[i]:+7.1f}")

    # --- DALTON ---
    print(f"\n{'='*70}")
    print("DALTON MINIMUM (C5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    for r in results[:5]:
        d = [4, 5, 6]
        dm = np.mean([abs(r['pf'][i] - peak_amps[i]) for i in d])
        print(f"  {r['label']:<20s} MAE={dm:.1f} "
              f"(C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f})")

    # --- PHASE DRIFT ANALYSIS (show how phases diverge from clock) ---
    print(f"\n{'='*70}")
    print("PHASE DRIFT ANALYSIS")
    print(f"{'='*70}")
    print(f"\n  How much do coupled phases drift from fixed clock phases?")
    print(f"  (Positive = ahead of clock, negative = behind)")

    # Use best coupled model's parameters
    best_coupled = [r for r in results if 'D:' in r['label'] or 'E:' in r['label']]
    if best_coupled:
        bc = min(best_coupled, key=lambda r: r['loo'])
        ba, tr = bc['ba'], bc['tr']
        print(f"\n  Using {bc['label']} (ba={ba:.1f}, tr={tr:.1f})")

        # Get the coupling strength from the label
        if '1/φ⁴' in bc['label']: cs = INV_PHI**4
        elif '1/φ³' in bc['label']: cs = INV_PHI**3
        elif '1/φ²' in bc['label']: cs = INV_PHI**2
        elif '1/φ' in bc['label']: cs = INV_PHI
        else: cs = INV_PHI_4

        # Run coupled model and track phases
        is_model_c = 'C:' in bc['label']
        phases = [2 * np.pi * (peak_years[0] - tr) / per for per in PERIODS]
        phase_drifts = {j: [] for j in range(N_OSC)}

        for i, t in enumerate(peak_years):
            # What the clock says phases should be
            clock_phases = [2 * np.pi * (t - tr) / per for per in PERIODS]

            for j in range(N_OSC):
                # Drift = actual - clock (mod 2π, centered on 0)
                drift = (phases[j] - clock_phases[j]) % (2 * np.pi)
                if drift > np.pi: drift -= 2 * np.pi
                phase_drifts[j].append(np.degrees(drift))

            # Evolve (same logic as model)
            cos_vals = [np.cos(ph) for ph in phases]
            collisions = [0.0] * N_OSC
            for j in range(1, N_OSC):
                collisions[j] = -np.cos(phases[j-1] - phases[j])

            if i < len(peak_years) - 1:
                dt = peak_years[i+1] - peak_years[i]
                amp_dev = (peak_amps[i] - ba) / ba if is_model_c else 0.0
                for j in range(N_OSC):
                    natural = 2 * np.pi * dt / PERIODS[j]
                    kick = 0.0
                    if j > 0:
                        kick += collisions[j] * cs
                    if j < N_OSC - 1:
                        kick += collisions[j+1] * cs * INV_PHI
                    if is_model_c:
                        kick += amp_dev * cs * INV_PHI
                    phases[j] += natural + kick

        # Print drift at key cycles
        print(f"\n  {'Cyc':>3s}  {'φ¹¹ drift':>10s}  {'φ⁹ drift':>10s}  {'φ⁶ drift':>10s}  {'φ⁴ drift':>10s}")
        print(f"  {'---':>3s}  {'----------':>10s}  {'----------':>10s}  {'----------':>10s}  {'----------':>10s}")
        for i, c in enumerate(cycle_nums):
            print(f"  {c:3d}  {phase_drifts[0][i]:+9.2f}°  {phase_drifts[1][i]:+9.2f}°  "
                  f"{phase_drifts[2][i]:+9.2f}°  {phase_drifts[3][i]:+9.2f}°")

        # Total drift magnitude
        print(f"\n  Total drift (RMS across all cycles):")
        for j, per_label in enumerate(['φ¹¹', 'φ⁹', 'φ⁶', 'φ⁴']):
            rms = np.sqrt(np.mean(np.array(phase_drifts[j])**2))
            print(f"    {per_label}: {rms:.2f}°")

    # --- SCOREBOARD ---
    print(f"\n{'='*70}")
    print("SCOREBOARD")
    print(f"{'='*70}")
    print(f"  223o All three (fixed):     LOO=33.03, 4/7, r=+0.656")
    print(f"  223p Blended α=1/φ:         LOO=33.60, 6/7, r=+0.683")
    print(f"  223d Mirror champion:       LOO=33.25, 5/7, r=+0.702")
    print(f"  ---")
    print(f"  225 best: {best['label']}: LOO={best['loo']:.2f}, {best['sw']}/7, r={best['rr']:+.3f}")
    if best_coupled:
        bc = min(best_coupled, key=lambda r: r['loo'])
        print(f"  225 best coupled: {bc['label']}: LOO={bc['loo']:.2f}, {bc['sw']}/7, r={bc['rr']:+.3f}")
    print(f"\n  Time: {time.time()-t0:.0f}s")
