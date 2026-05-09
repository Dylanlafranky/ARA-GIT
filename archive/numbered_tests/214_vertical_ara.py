#!/usr/bin/env python3
"""
Script 214 — Vertical ARA: Three Levels of Coupled Authority

INSIGHT (Dylan):
  The Sun sits inside a larger system. That system pushes energy DOWN.
  We've only modeled energy going UP (the drain). We need the
  interference from ABOVE.

  Three levels, each φ³ apart:
    INNER (subsystem):    φ³ scale — the cycle-level machinery
    SUN (system):         φ⁶ scale — the Sun's own ARA
    ABOVE (super-system): φ⁹ scale — galactic/interstellar pressing down

  φ³ is the step between levels. Three levels × φ³ = φ⁹ total.
  THIS IS THE 3×3=9 GEOMETRY — three systems on three axes.

  Known long solar cycles map to these:
    φ¹³ ≈ 521yr  — near the ~500yr Eddy cycle
    φ¹⁵ ≈ 1364yr — near the ~1000yr Bond cycle / Hallstatt (~2300yr)
    φ¹⁸ ≈ 5778yr — very long modulation

  The "above" energy OPPOSES the internal cascade — it's an
  interference pattern. When the above-system is in its release
  phase, it suppresses the Sun → grand minima (Maunder, Dalton).
  When it's in accumulation, it supports → grand maxima.

CASCADE ARCHITECTURE:
  Level 1 (Inner, φ³ scale):
    Periods: φ⁴ (6.9yr), φ⁵ (11.1yr = Schwabe)
    Gate: drain-compressed AR (~0.400)
    Direction: UP (feeds into Sun level)

  Level 2 (Sun, φ⁶ scale):
    Periods: φ⁶ (17.9yr), φ⁹ (76.0yr = Gleissberg)
    Gate: natural ARA (0.618)
    Direction: the system being predicted

  Level 3 (Above, φ⁹ scale):
    Periods: φ¹¹ (199yr = de Vries), φ¹³ (521yr ≈ Eddy)
    Gate: natural ARA (0.618) — we assume the above system is also φ
    Direction: DOWN (opposes/modulates Sun level)

  The key: Level 1 energy feeds UP with diminishing authority.
  Level 3 energy pushes DOWN with diminishing authority.
  Level 2 is where they meet — the Sun.

MODELS:
  V1: Static 3-level — all gates fixed
  V2: Add φ¹⁵ (1364yr) to Level 3 — deeper super-system
  V3: Causal Level 2 gate (207 mechanism) + blended authority (213)
  V4: V3 + dynamic drain
  V5: V4 + phase-opposition (Level 3 opposes Level 1)

FREE PARAMETERS: 2 (base_amp, t_ref)
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9

CYCLES = {
    1:  (1755.2, 1761.5, 144.1, 11.3),
    2:  (1766.5, 1769.7, 193.0, 9.0),
    3:  (1775.5, 1778.4, 264.3, 9.3),
    4:  (1784.7, 1788.1, 235.3, 13.6),
    5:  (1798.3, 1805.2, 82.0,  12.3),
    6:  (1810.6, 1816.4, 81.2,  12.7),
    7:  (1823.3, 1829.9, 119.2, 10.5),
    8:  (1833.8, 1837.2, 244.9, 9.7),
    9:  (1843.5, 1848.1, 219.9, 12.4),
    10: (1855.9, 1860.1, 186.2, 11.3),
    11: (1867.2, 1870.6, 234.0, 11.8),
    12: (1878.9, 1883.9, 124.4, 11.3),
    13: (1890.2, 1894.1, 146.5, 11.8),
    14: (1902.0, 1906.2, 107.1, 11.5),
    15: (1913.5, 1917.6, 175.7, 10.1),
    16: (1923.6, 1928.4, 130.2, 10.1),
    17: (1933.8, 1937.4, 198.6, 10.4),
    18: (1944.2, 1947.5, 218.7, 10.2),
    19: (1954.3, 1958.2, 285.0, 10.5),
    20: (1964.9, 1968.9, 156.6, 11.7),
    21: (1976.5, 1979.9, 232.9, 10.3),
    22: (1986.8, 1989.6, 212.5, 9.7),
    23: (1996.4, 2001.9, 180.3, 12.3),
    24: (2008.0, 2014.3, 116.4, 11.0),
    25: (2019.5, 2024.5, 173.0, 11.0),
}

cycle_nums = sorted(CYCLES.keys())
start_years = np.array([CYCLES[c][0] for c in cycle_nums])
peak_years = np.array([CYCLES[c][1] for c in cycle_nums])
peak_amps = np.array([CYCLES[c][2] for c in cycle_nums])
durations = np.array([CYCLES[c][3] for c in cycle_nums])
rise_fracs = (peak_years - start_years) / durations
N = len(cycle_nums)
MEAN_AMP = peak_amps.mean()
MEAN_RF = rise_fracs.mean()

# === THREE-LEVEL CASCADE ===
# Level 1 (Inner): feeds UP
LEVEL1 = [PHI**4, PHI**5]   # 6.9yr, 11.1yr

# Level 2 (Sun): the system
LEVEL2 = [PHI**6, PHI**9]   # 17.9yr, 76.0yr

# Level 3 (Above): pushes DOWN
LEVEL3_SHORT = [PHI**11, PHI**13]       # 199yr, 521yr
LEVEL3_DEEP  = [PHI**11, PHI**13, PHI**15]  # + 1364yr

GLEISSBERG = PHI**9
SCHWABE = PHI**5

# Gate fractions
INNER_ACC = MEAN_RF   # 0.400 (drain-compressed)
SUN_ACC = PHI / (PHI + 1)  # 0.618 (natural ARA)
ABOVE_ACC = PHI / (PHI + 1)  # 0.618 (assume natural for above)

# Authority weights: how much each level's coupling affects the next
# Energy crossing a log boundary gets scaled by 1/φ³
# (φ³ ≈ 4.236 — about a quarter of the energy crosses)
CROSS_LEVEL_COUPLING = INV_PHI ** 3  # ≈ 0.236

# Waldmeier regression
wald_c = np.polyfit(peak_amps, rise_fracs, 1)
wald_rf = lambda a: np.clip(wald_c[0] * a + wald_c[1], 0.15, 0.85)

print(f"Three-level cascade architecture:")
print(f"  Level 1 (Inner):  φ⁴={PHI**4:.1f}yr, φ⁵={PHI**5:.1f}yr  "
      f"gate={INNER_ACC:.3f}")
print(f"  Level 2 (Sun):    φ⁶={PHI**6:.1f}yr, φ⁹={PHI**9:.1f}yr  "
      f"gate={SUN_ACC:.3f}")
print(f"  Level 3 (Above):  φ¹¹={PHI**11:.1f}yr, φ¹³={PHI**13:.1f}yr, "
      f"φ¹⁵={PHI**15:.1f}yr  gate={ABOVE_ACC:.3f}")
print(f"  Cross-level coupling: 1/φ³ = {CROSS_LEVEL_COUPLING:.4f}")
print(f"  φ³ step = {PHI**3:.3f}yr between levels")


def mae(p, o):
    return np.mean(np.abs(np.array(p) - np.array(o)))


def sawtooth_valve(phase, acc_frac):
    acc_frac = max(0.15, min(0.85, acc_frac))
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < acc_frac:
        state = (cycle_pos / acc_frac) * PHI
    else:
        ramp = (cycle_pos - acc_frac) / (1 - acc_frac)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    return state / ((PHI + INV_PHI) / 2)


def ara_to_acc(ara_val):
    return 1.0 / (1.0 + max(0.01, ara_val))


def cascade_level(t, amp, t_ref, periods, gate, coupling_strength=INV_PHI_4):
    """Run a cascade level with given gate and coupling strength."""
    for period in periods:
        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = coupling_strength * gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)
    return amp


# =================================================================
# MODEL FUNCTIONS
# =================================================================

def predict_203b(t, ba, tr):
    """Baseline: single gate, 4 periods."""
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase, SUN_ACC)
    amp = ba
    for period in [PHI**11, PHI**9, PHI**6, PHI**4]:
        phase = 2 * np.pi * (t - tr) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)
    amp += ba * INV_PHI_9 * np.cos(gleiss_phase)
    return amp


def predict_3level(t, ba, tr, inner_acc=INNER_ACC, sun_acc=SUN_ACC,
                    above_acc=ABOVE_ACC, level3=None, use_drain=False,
                    oppose=False):
    """
    Three-level vertical ARA.

    Level 1 (Inner): feeds UP into Sun level
      - Full authority at own level
      - Scaled by 1/φ³ when crossing up to Sun

    Level 2 (Sun): the system being predicted
      - Full authority at own level
      - Receives from below (diminished) and above (diminished)

    Level 3 (Above): pushes DOWN onto Sun level
      - Full authority at own level
      - Scaled by 1/φ³ when crossing down to Sun
      - If oppose=True, coupling is NEGATIVE (interference)
    """
    if level3 is None:
        level3 = LEVEL3_SHORT

    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE

    inner_gate = sawtooth_valve(schwabe_phase, inner_acc)
    sun_gate = sawtooth_valve(gleiss_phase, sun_acc)
    above_gate = sawtooth_valve(gleiss_phase, above_acc)  # above uses Gleissberg-scale phase too

    amp = ba

    # Level 2 (Sun): full authority — this is the primary cascade
    amp = cascade_level(t, amp, tr, LEVEL2, sun_gate, INV_PHI_4)

    # Level 1 (Inner): feeds UP — diminished by 1/φ³
    inner_coupling = INV_PHI_4 * CROSS_LEVEL_COUPLING
    amp = cascade_level(t, amp, tr, LEVEL1, inner_gate, inner_coupling)

    # Level 3 (Above): pushes DOWN — diminished by 1/φ³
    above_coupling = INV_PHI_4 * CROSS_LEVEL_COUPLING
    if oppose:
        above_coupling = -above_coupling  # OPPOSITION — destructive interference
    amp = cascade_level(t, amp, tr, level3, above_gate, above_coupling)

    if use_drain:
        amp_ratio = amp / ba
        amp -= INV_PHI_9 * amp * amp_ratio * abs(np.cos(gleiss_phase))
    else:
        amp += ba * INV_PHI_9 * np.cos(gleiss_phase)

    return amp


# Simple wrappers
def predict_v1(t, ba, tr):
    """V1: Static 3-level, Level 3 = φ¹¹ + φ¹³."""
    return predict_3level(t, ba, tr)

def predict_v1o(t, ba, tr):
    """V1o: V1 with opposition."""
    return predict_3level(t, ba, tr, oppose=True)

def predict_v2(t, ba, tr):
    """V2: Deeper Level 3 (add φ¹⁵)."""
    return predict_3level(t, ba, tr, level3=LEVEL3_DEEP)

def predict_v2o(t, ba, tr):
    """V2o: V2 with opposition."""
    return predict_3level(t, ba, tr, level3=LEVEL3_DEEP, oppose=True)

def predict_v1d(t, ba, tr):
    """V1d: V1 + drain."""
    return predict_3level(t, ba, tr, use_drain=True)

def predict_v1od(t, ba, tr):
    """V1od: V1 + opposition + drain."""
    return predict_3level(t, ba, tr, oppose=True, use_drain=True)

def predict_v2d(t, ba, tr):
    """V2d: Deep + drain."""
    return predict_3level(t, ba, tr, level3=LEVEL3_DEEP, use_drain=True)

def predict_v2od(t, ba, tr):
    """V2od: Deep + opposition + drain."""
    return predict_3level(t, ba, tr, level3=LEVEL3_DEEP,
                          oppose=True, use_drain=True)

# Causal versions
def mk_causal(level3=None, oppose=False, drain=False):
    """Causal outer gate: prev amp sets Sun-level gate."""
    def _pred(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            if i == 0:
                sa = SUN_ACC
            else:
                prev_ara = amps[i - 1] / ba
                sa = ara_to_acc(prev_ara)
            preds.append(predict_3level(t, ba, tr, sun_acc=sa,
                                         level3=level3, use_drain=drain,
                                         oppose=oppose))
        return preds
    return _pred

def mk_causal_full(level3=None, oppose=False, drain=False):
    """Causal both: prev amp → Sun gate, Waldmeier → inner gate."""
    def _pred(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            if i == 0:
                sa = SUN_ACC
                ia = INNER_ACC
            else:
                prev_ara = amps[i - 1] / ba
                sa = ara_to_acc(prev_ara)
                ia = wald_rf(amps[i - 1])
            preds.append(predict_3level(t, ba, tr, inner_acc=ia,
                                         sun_acc=sa, level3=level3,
                                         use_drain=drain, oppose=oppose))
        return preds
    return _pred


# =================================================================
# FITTING + EVALUATION
# =================================================================

def fit_s(fn, ty, ta):
    best, bba, btr = 1e9, 0, 0
    for tr in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(ta) * 0.6, np.mean(ta) * 1.4, 40):
            m = mae([fn(t, ba, tr) for t in ty], ta)
            if m < best:
                best, bba, btr = m, ba, tr
    return bba, btr, best


def fit_q(fn, mask, ay, aa):
    best, bba, btr = 1e9, 0, 0
    idx = np.where(mask)[0]
    ta = aa[mask]
    for tr in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(ta) * 0.6, np.mean(ta) * 1.4, 40):
            ap = fn(ay, aa, ba, tr)
            m = mae([ap[j] for j in idx], ta)
            if m < best:
                best, bba, btr = m, ba, tr
    return bba, btr, best


def evaluate(label, fn, is_seq=False):
    pe, se = [], []
    fm = np.ones(N, dtype=bool)
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        if is_seq:
            ba, tr, _ = fit_q(fn, mask, peak_years, peak_amps)
            ap = fn(peak_years, peak_amps, ba, tr)
            pi = ap[i]
        else:
            ba, tr, _ = fit_s(fn, peak_years[mask], peak_amps[mask])
            pi = fn(peak_years[i], ba, tr)
        pe.append(abs(pi - peak_amps[i]))
        se.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    pe, se = np.array(pe), np.array(se)
    loo = pe.mean()
    sl = se.mean()

    if is_seq:
        bf, tf, _ = fit_q(fn, fm, peak_years, peak_amps)
        pf = fn(peak_years, peak_amps, bf, tf)
    else:
        bf, tf, _ = fit_s(fn, peak_years, peak_amps)
        pf = [fn(t, bf, tf) for t in peak_years]

    ef = np.array(pf) - peak_amps
    rr = np.corrcoef(rise_fracs, ef)[0, 1]
    ar_c = np.corrcoef(peak_amps, ef)[0, 1]

    sw = 0
    sd = []
    for nt in [5, 8, 10, 12, 15, 18, 20]:
        if nt >= N: continue
        tm = np.zeros(N, dtype=bool)
        tm[:nt] = True
        if is_seq:
            bs, ts, _ = fit_q(fn, tm, peak_years, peak_amps)
            ap = fn(peak_years, peak_amps, bs, ts)
            tp = ap[nt:]
        else:
            bs, ts, _ = fit_s(fn, peak_years[:nt], peak_amps[:nt])
            tp = [fn(t, bs, ts) for t in peak_years[nt:]]
        ta = peak_amps[nt:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:nt].mean()), ta)
        w = "φ" if pm < sm else "sine"
        if pm < sm: sw += 1
        sd.append((nt, N - nt, pm, sm, w))

    return {'label': label, 'loo': loo, 'sine': sl,
            'imp': (loo / sl - 1) * 100,
            'wins': int(np.sum(pe < se)),
            'rr': rr, 'ar': ar_c,
            'sw': sw, 'sd': sd,
            'pf': pf, 'ba': bf, 'tr': tf}


# =================================================================
# MAIN
# =================================================================

if __name__ == '__main__':
    print(f"\n{'='*70}")
    print("SCRIPT 214 — VERTICAL ARA: THREE LEVELS")
    print(f"{'='*70}")

    results = []

    # Baseline
    print("\nRunning 203b baseline...")
    r = evaluate("203b baseline", predict_203b)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # V1: Static 3-level (cooperative)
    print("\nV1: 3-level cooperative...")
    r = evaluate("V1 3-level", predict_v1)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # V1o: Opposition
    print("\nV1o: 3-level opposition...")
    r = evaluate("V1o oppose", predict_v1o)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # V2: Deep Level 3
    print("\nV2: deep 3-level...")
    r = evaluate("V2 deep", predict_v2)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # V2o: Deep + opposition
    print("\nV2o: deep opposition...")
    r = evaluate("V2o deep oppose", predict_v2o)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # + drain variants
    for lbl, fn in [("V1d 3lvl+drain", predict_v1d),
                     ("V1od opp+drain", predict_v1od),
                     ("V2d deep+drain", predict_v2d),
                     ("V2od dp opp+dr", predict_v2od)]:
        print(f"\n{lbl}...")
        r = evaluate(lbl, fn)
        results.append(r)
        print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
              f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # Causal versions (best static configs)
    print("\nV3: causal 3-level...")
    fn = mk_causal(level3=LEVEL3_SHORT, oppose=False, drain=False)
    r = evaluate("V3 causal", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    print("\nV3o: causal oppose...")
    fn = mk_causal(level3=LEVEL3_SHORT, oppose=True, drain=False)
    r = evaluate("V3o causal opp", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    print("\nV3od: causal opp+drain...")
    fn = mk_causal(level3=LEVEL3_SHORT, oppose=True, drain=True)
    r = evaluate("V3od caus op+dr", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    print("\nV4: causal deep oppose+drain...")
    fn = mk_causal(level3=LEVEL3_DEEP, oppose=True, drain=True)
    r = evaluate("V4 deep caus", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # Full causal (both gates)
    print("\nV5: full causal opp+drain...")
    fn = mk_causal_full(level3=LEVEL3_SHORT, oppose=True, drain=True)
    r = evaluate("V5 full causal", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    print("\nV5d: full causal deep opp+drain...")
    fn = mk_causal_full(level3=LEVEL3_DEEP, oppose=True, drain=True)
    r = evaluate("V5d deep full", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # === COMPARISON ===
    print(f"\n{'='*70}")
    print("FULL COMPARISON")
    print(f"{'='*70}")
    print(f"\n  {'Model':<22s} {'LOO':>7s} {'%sine':>7s} {'Wins':>5s} "
          f"{'Rise r':>7s} {'Amp r':>7s} {'Split':>5s}")
    print(f"  {'-'*22} {'-'*7} {'-'*7} {'-'*5} {'-'*7} {'-'*7} {'-'*5}")
    for r in results:
        print(f"  {r['label']:<22s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['wins']:3d}/25 {r['rr']:+7.3f} {r['ar']:+7.3f} "
              f"{r['sw']:2d}/7")

    bl = min(results, key=lambda r: r['loo'])
    bw = min(results, key=lambda r: abs(r['rr']))
    bs = max(results, key=lambda r: (r['sw'], -r['loo']))

    print(f"\n  BEST LOO: {bl['label']} ({bl['loo']:.2f}, {bl['imp']:+.1f}%)")
    print(f"  BEST WALDMEIER: {bw['label']} (r={bw['rr']:+.3f})")
    print(f"  BEST SPLITS: {bs['label']} ({bs['sw']}/7)")

    # Split details
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS — TOP MODELS")
    print(f"{'='*70}")
    shown = set()
    for r in [bl, bs, bw]:
        if r['label'] in shown: continue
        shown.add(r['label'])
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            mg = sm - pm if w == "φ" else pm - sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: "
                  f"φ={pm:.1f}  sine={sm:.1f}  → {w} ({mg:.1f})")

    # Per-cycle for best
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {bl['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'RF':>6s}")
    for i, c in enumerate(cycle_nums):
        p = bl['pf'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} "
              f"{p - peak_amps[i]:+7.1f} {rise_fracs[i]:6.3f}")

    # Dalton minimum diagnostic
    print(f"\n{'='*70}")
    print("DALTON MINIMUM DIAGNOSTIC (Cycles 5-7)")
    print(f"{'='*70}")
    dalton = [4, 5, 6]  # indices for cycles 5, 6, 7
    for r in results:
        dalton_err = np.mean([abs(r['pf'][i] - peak_amps[i]) for i in dalton])
        print(f"  {r['label']:<22s} Dalton MAE={dalton_err:.1f}  "
              f"(C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f} "
              f"vs 82/81/119)")

    # === CROSS-REFERENCE ===
    print(f"\n{'='*70}")
    print("CROSS-REFERENCE: ALL SCRIPTS")
    print(f"{'='*70}")
    print(f"""
  203b single gate:        LOO=37.66, splits=1/7, rise r=+0.767
  207 V1 causal:           LOO=38.82, splits=3/7 ← extrap champ
  209 V5 causal+drain:     LOO=36.97, splits=2/7
  210 V5 AR drain:         LOO=36.62, splits=2/7
  211 V4d Wald+drain:      LOO=36.46, splits=0/7 ← interp champ
  213 V2 blended φ-decay:  LOO=37.11, splits=2/7

  This script (3-level vertical ARA):
    Best LOO:    {bl['label']}: {bl['loo']:.2f}, splits={bl['sw']}/7
    Best Wald:   {bw['label']}: r={bw['rr']:+.3f}
    Best splits: {bs['label']}: {bs['sw']}/7

  φ³ SCALE STRUCTURE:
    Inner (φ³):  φ⁴, φ⁵  — cycle guts, drain-compressed gate
    Sun (φ⁶):   φ⁶, φ⁹  — system level, natural ARA gate
    Above (φ⁹): φ¹¹, φ¹³ — galactic interference, opposing energy
""")
