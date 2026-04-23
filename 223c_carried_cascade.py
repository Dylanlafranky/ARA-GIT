#!/usr/bin/env python3
"""
Script 223c — Carried State Cascade with Door Mechanics

DYLAN'S HALLWAY ANALOGY (FULL):
  Doors are all φ distance apart. The ball gets squeezed through
  each door and the direction REVERTS (oscillation axis flips).

  WHERE the ball is when it hits the door matters:
    Near ROOF (peak, cos ≈ +1): ball has low velocity
      → next hallway gets LONG SLOW LOOPS (strong power, gentle)
    Near FLOOR (trough, cos ≈ -1): ball has high velocity
      → next hallway gets NARROW TALL WAVES (high energy, rapid)

  The velocity at the door = tension = -sin(phase).
  High |tension| at door = next period couples STRONGLY
  Low |tension| at door = next period couples GENTLY

  Direction reversal: oscillation flips at each door.
  The ball still moves forward (time progresses), but each
  successive period's wave is inverted from the previous.

  Meanwhile: another φ-hallway runs opposite (Hale horizontal),
  balls bounce off each other at roof/floor (singularity doors).
  Above: same direction hallway, doors at singularity points.

2 models:
  [1] Carried tension — previous period's -sin shapes next coupling
  [2] Direction reversal — cos alternates sign at each door
"""

import numpy as np
import warnings, time
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9

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
SCHWABE = PHI**5; GLEISSBERG = PHI**9; SUN_ACC = PHI/(PHI+1)

def mae(p, o): return np.mean(np.abs(np.array(p) - np.array(o)))

def sawtooth_valve(phase, acc_frac):
    acc_frac = max(0.15, min(0.85, acc_frac))
    cp = (phase % (2*np.pi)) / (2*np.pi)
    if cp < acc_frac: state = (cp/acc_frac)*PHI
    else:
        ramp = (cp-acc_frac)/(1-acc_frac)
        state = PHI*(1-ramp) + INV_PHI*ramp
    return state / ((PHI+INV_PHI)/2)

def ara_to_acc(v): return 1.0/(1.0+max(0.01, v))

def sing_pulse_decay(phase, dr):
    cp = (phase%(2*np.pi))/(2*np.pi)
    return np.exp(-dr*cp)


# =================================================================
# MODEL 1: CARRIED TENSION
# =================================================================
def mk_carried_tension(h_cc=INV_PHI_3):
    """
    Each period's tension (-sin) carries forward to modulate
    the NEXT period's coupling strength.

    High |tension| at door → next period couples STRONGLY
    (ball moving fast → narrow tall waves, high energy)

    Low |tension| at door → next period couples GENTLY
    (ball at roof/floor → long slow loops, strong power)

    Direction reverses at each door: carried tension flips sign.
    Gleissberg gate preserved (shared hallway structure).
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            gp = 2*np.pi*(t-tr)/GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            amp = ba
            carried = 0.0  # tension carried from previous door

            for per in [PHI**11, PHI**9, PHI**6, PHI**4]:
                ph = 2*np.pi*(t-tr)/per
                w = np.cos(ph)
                tens = -np.sin(ph)

                eps = INV_PHI_4 * gate

                # Own tension asymmetry (existing)
                if tens > 0: eps *= (1 + 0.5*tens*(PHI-1))
                else:        eps *= (1 + 0.5*tens*(1-INV_PHI))

                # CARRIED tension from previous door
                # Modulates this period's effective coupling
                # High |carried| → stronger coupling
                # Low |carried| → gentler coupling
                eps *= (1 + carried * INV_PHI)

                amp *= (1 + eps*w)

                # Carry THIS period's tension to next door
                # Direction reversal: sign flips
                carried = -tens

            # Gleissberg additive
            amp += ba * INV_PHI_9 * np.cos(gp)

            # Inner pulse (below)
            sp = 2*np.pi*(t-tr)/SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            # Hale horizontal
            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI)

            preds.append(amp)
        return preds
    return _p


# =================================================================
# MODEL 2: DIRECTION REVERSAL + CARRIED WAVE STATE
# =================================================================
def mk_direction_reversal(h_cc=INV_PHI_3):
    """
    Direction reverses at each door: the wave's cos FLIPS sign.
    Plus: previous period's wave VALUE (cos) shapes the next
    period's coupling — like the ball's position at the door
    determining the next hallway's wave character.

    Near roof (prev cos ≈ +1): gentle next coupling
      (ball has little velocity, creates slow loops)
    Near floor (prev cos ≈ -1): strong next coupling
      (ball has high velocity, creates narrow tall waves)

    wave_shape = 1 - INV_PHI × prev_cos
      At roof: 1 - 0.618×1 = 0.382 (gentle)
      At floor: 1 - 0.618×(-1) = 1.618 (strong = φ!)
      At center: 1 (neutral)
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            gp = 2*np.pi*(t-tr)/GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            amp = ba
            prev_cos = 0.0  # wave state from previous door
            door_sign = 1   # direction alternates

            for per in [PHI**11, PHI**9, PHI**6, PHI**4]:
                ph = 2*np.pi*(t-tr)/per
                w = door_sign * np.cos(ph)  # direction reversal
                tens = door_sign * (-np.sin(ph))

                # Wave shape from previous door position
                # Floor (prev_cos ≈ -1) → strong (φ)
                # Roof (prev_cos ≈ +1) → gentle (1/φ)
                wave_shape = 1 - INV_PHI * prev_cos

                eps = INV_PHI_4 * gate * wave_shape

                # Tension asymmetry
                if tens > 0: eps *= (1 + 0.5*tens*(PHI-1))
                else:        eps *= (1 + 0.5*tens*(1-INV_PHI))

                amp *= (1 + eps*w)

                # Carry state to next door
                prev_cos = np.cos(ph)  # unflipped position
                door_sign *= -1  # direction reverses

            # Gleissberg additive
            amp += ba * INV_PHI_9 * np.cos(gp)

            # Inner pulse
            sp = 2*np.pi*(t-tr)/SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            # Hale horizontal
            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI)

            preds.append(amp)
        return preds
    return _p


# =================================================================
# FITTING + EVAL
# =================================================================
def fit_q(fn, mask, ay, aa):
    best, bba, btr = 1e9, 0, 0
    idx = np.where(mask)[0]; ta = aa[mask]
    for tr in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(ta)*0.6, np.mean(ta)*1.4, 40):
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

    sw, sd = 0, []
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
        sd.append((nt, N-nt, pm, sm, w))

    return {'label': label, 'loo': loo, 'sine': sl, 'imp': (loo/sl-1)*100,
            'wins': int(np.sum(pe < se)), 'rr': rr, 'sw': sw, 'sd': sd,
            'pf': pf, 'ba': bf, 'tr': tf}


# =================================================================
# MAIN
# =================================================================
if __name__ == '__main__':
    t0 = time.time()
    print("="*70)
    print("SCRIPT 223c — CARRIED STATE CASCADE")
    print("="*70)
    print("""
  Doors are φ apart. At each door:
    1. Direction REVERTS (oscillation axis flips)
    2. Ball's state CARRIES to shape next hallway

  Model 1 (Carried Tension):
    Previous period's -sin → modulates next period's coupling
    High velocity at door → strong next coupling (narrow tall waves)
    Low velocity at door → gentle next coupling (long slow loops)

  Model 2 (Direction Reversal + Wave Shape):
    cos flips at each door. Previous cos shapes next coupling.
    Floor → strong (φ), Roof → gentle (1/φ), Center → neutral (1)

  Both keep Gleissberg gate + inner pulse + Hale.
""")

    results = []

    # [1] Carried tension
    print("[1/2] Carried tension cascade...")
    fn1 = mk_carried_tension(h_cc=INV_PHI_3)
    r = evaluate("Carried tension", fn1)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [2] Direction reversal + wave shape
    print("\n[2/2] Direction reversal + wave shape...")
    fn2 = mk_direction_reversal(h_cc=INV_PHI_3)
    r = evaluate("Dir reversal", fn2)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # Sort
    all_sorted = sorted(results, key=lambda r: r['loo'])
    bl = all_sorted[0]

    print(f"\n{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"\n  {'Model':<25s} {'LOO':>7s} {'%sine':>7s} {'Rise r':>7s} {'Split':>5s}")
    print(f"  {'-'*25} {'-'*7} {'-'*7} {'-'*7} {'-'*5}")
    for r in all_sorted:
        print(f"  {r['label']:<25s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['rr']:+7.3f} {r['sw']:2d}/7")

    # Temporal splits
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS")
    print(f"{'='*70}")
    for r in all_sorted:
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            mg = sm-pm if w == "phi" else pm-sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: phi={pm:.1f} sine={sm:.1f} -> {w} ({mg:.1f})")

    # Dalton
    print(f"\n{'='*70}")
    print("DALTON (C5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    for r in all_sorted:
        d = [4, 5, 6]
        dm = np.mean([abs(r['pf'][i] - peak_amps[i]) for i in d])
        print(f"  {r['label']:<25s} MAE={dm:.1f} "
              f"(C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f})")

    # Per-cycle
    bn = all_sorted[0]
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {bn['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s}")
    for i, c in enumerate(cycle_nums):
        p = bn['pf'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} {p-peak_amps[i]:+7.1f}")

    # Scoreboard
    print(f"\n{'='*70}")
    print("SCOREBOARD")
    print(f"{'='*70}")
    print(f"  220 Hale h=1/φ³:       LOO=34.80, 4/7, r=+0.700  (champion)")
    print(f"  216 V5 inner pulse:     LOO=35.28, 4/7, r=+0.690")
    print(f"  203b baseline:          LOO=37.66, 1/7, r=+0.767")
    print(f"  ---")
    print(f"  This best: {bl['label']}: LOO={bl['loo']:.2f}, {bl['sw']}/7, r={bl['rr']:+.3f}")
    print(f"\n  Time: {time.time()-t0:.0f}s")
