#!/usr/bin/env python3
"""
Script 213 — Blended Gate: Scale-Weighted Authority

INSIGHT (Dylan):
  The internal systems feed into the Sun's overall system, but
  energy at the internal level has less effect on the overall —
  it needs to TRANSFORM UP a log or dimension of energy.

  So: keep the full 4-period multiplicative cascade intact,
  but each cascade member feels a BLEND of two gate signals:
    - OUTER gate (Gleissberg): φ-ARA (0.618) — the system's natural rhythm
    - INNER gate (Schwabe): drain-compressed (~0.400) — the cycle's actual shape

  The blend weight depends on WHERE in the scale hierarchy each
  cascade member sits:
    φ¹¹ (199yr) — almost purely outer gate (system level)
    φ⁹  (76yr)  — mostly outer
    φ⁶  (18yr)  — mostly inner
    φ⁴  (6.9yr) — almost purely inner gate (cycle level)

  The weight IS the log-scale position. Members closer to the
  Gleissberg period feel the outer gate; members closer to the
  Schwabe period feel the inner gate. The transition encodes
  the singularity between scales.

BLEND FUNCTION:
  For cascade member with period P:
    w_outer = log(P/P_inner) / log(P_outer/P_inner)
    w_inner = 1 - w_outer
    gate_effective = w_outer × outer_gate + w_inner × inner_gate

  This gives:
    φ¹¹: w_outer = 1.00 (log ratio 199/6.9 vs 76/6.9)
    φ⁹:  w_outer = 0.78
    φ⁶:  w_outer = 0.31
    φ⁴:  w_outer = 0.00

MODELS:
  V1: Static blend — outer=0.618, inner=0.400
  V2: Causal outer — prev amplitude sets outer gate, inner=0.400
  V3: Causal both — outer from prev amp, inner from Waldmeier-est RF
  V4: V3 + dynamic drain
  V5: φ-weighted blend — weight = 1/φ^(scale_distance) instead of linear log

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

CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
SCHWABE = PHI**5

OUTER_ACC = PHI / (PHI + 1)  # 0.618
INNER_ACC = MEAN_RF           # 0.400

# Waldmeier regression
wald_c = np.polyfit(peak_amps, rise_fracs, 1)
wald_rf = lambda a: np.clip(wald_c[0] * a + wald_c[1], 0.15, 0.85)

# Pre-compute blend weights for each cascade member
P_outer = CASCADE[0]   # φ¹¹ = 199yr (longest = most outer)
P_inner = CASCADE[-1]  # φ⁴ = 6.9yr (shortest = most inner)
log_range = np.log(P_outer / P_inner)

BLEND_WEIGHTS_LOG = []
for P in CASCADE:
    w_outer = np.log(P / P_inner) / log_range
    w_outer = max(0.0, min(1.0, w_outer))
    BLEND_WEIGHTS_LOG.append(w_outer)

# φ-weighted: distance in powers of φ from inner
# φ⁴ → 0 steps, φ⁶ → 2 steps, φ⁹ → 5 steps, φ¹¹ → 7 steps
PHI_STEPS = [11 - 4, 9 - 4, 6 - 4, 4 - 4]  # [7, 5, 2, 0]
MAX_STEP = max(PHI_STEPS)
BLEND_WEIGHTS_PHI = [s / MAX_STEP for s in PHI_STEPS]

# 1/φ decay: each step away from inner, influence decays by 1/φ
BLEND_WEIGHTS_DECAY = []
for s in PHI_STEPS:
    w = 1 - INV_PHI ** s  # 0 at inner (s=0), approaches 1 as s→∞
    BLEND_WEIGHTS_DECAY.append(w)


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


# =================================================================
# BLENDED PREDICTION
# =================================================================

def predict_blended(t, base_amp, t_ref, outer_acc, inner_acc,
                     blend_weights, use_drain=False):
    """
    Full 4-period cascade with blended gate at each member.

    Each cascade member feels:
      gate = w_outer × outer_gate + (1-w_outer) × inner_gate

    This preserves the multiplicative chain while encoding
    two different AR values at two different scales.
    """
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    schwabe_phase = 2 * np.pi * (t - t_ref) / SCHWABE

    outer_gate = sawtooth_valve(gleiss_phase, outer_acc)
    inner_gate = sawtooth_valve(schwabe_phase, inner_acc)

    amp = base_amp
    for j, period in enumerate(CASCADE):
        w = blend_weights[j]
        gate = w * outer_gate + (1 - w) * inner_gate

        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)

        eps = INV_PHI_4 * gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))

        amp *= (1 + eps * wave)

    if use_drain:
        amp_ratio = amp / base_amp
        amp -= INV_PHI_9 * amp * amp_ratio * abs(np.cos(gleiss_phase))
    else:
        amp += base_amp * INV_PHI_9 * np.cos(gleiss_phase)

    return amp


# === MODEL WRAPPERS ===

def predict_203b(t, ba, tr):
    """Baseline: single gate at 0.618."""
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase, OUTER_ACC)
    amp = ba
    for period in CASCADE:
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


# -- Static blends --
def mk_static(weights, drain=False, label=""):
    def _pred(t, ba, tr):
        return predict_blended(t, ba, tr, OUTER_ACC, INNER_ACC, weights, drain)
    _pred.__name__ = label
    return _pred

# -- Causal sequence blends --
def mk_causal_outer(weights, drain=False):
    """Causal outer gate (prev amp), static inner (0.400)."""
    def _pred(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            if i == 0:
                oa = OUTER_ACC
            else:
                prev_ara = amps[i - 1] / ba
                oa = ara_to_acc(prev_ara)
            preds.append(predict_blended(t, ba, tr, oa, INNER_ACC, weights, drain))
        return preds
    return _pred

def mk_causal_both(weights, drain=False):
    """Causal outer (prev amp) + causal inner (Waldmeier-est RF)."""
    def _pred(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            if i == 0:
                oa = OUTER_ACC
                ia = INNER_ACC
            else:
                prev_ara = amps[i - 1] / ba
                oa = ara_to_acc(prev_ara)
                ia = wald_rf(amps[i - 1])
            preds.append(predict_blended(t, ba, tr, oa, ia, weights, drain))
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
    ar = np.corrcoef(peak_amps, ef)[0, 1]

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
            'rr': rr, 'ar': ar,
            'sw': sw, 'sd': sd,
            'pf': pf, 'ba': bf, 'tr': tf}


# =================================================================
# MAIN
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("SCRIPT 213 — BLENDED GATE: SCALE-WEIGHTED AUTHORITY")
    print("=" * 70)

    print(f"""
  Each cascade member feels a BLEND of outer + inner gate.
  Full multiplicative chain preserved.

  Cascade member   Period   Log-weight   φ-weight   Decay-weight
  φ¹¹             {CASCADE[0]:6.1f}yr   {BLEND_WEIGHTS_LOG[0]:.3f}        {BLEND_WEIGHTS_PHI[0]:.3f}      {BLEND_WEIGHTS_DECAY[0]:.3f}
  φ⁹              {CASCADE[1]:6.1f}yr   {BLEND_WEIGHTS_LOG[1]:.3f}        {BLEND_WEIGHTS_PHI[1]:.3f}      {BLEND_WEIGHTS_DECAY[1]:.3f}
  φ⁶              {CASCADE[2]:6.1f}yr   {BLEND_WEIGHTS_LOG[2]:.3f}        {BLEND_WEIGHTS_PHI[2]:.3f}      {BLEND_WEIGHTS_DECAY[2]:.3f}
  φ⁴              {CASCADE[3]:6.1f}yr   {BLEND_WEIGHTS_LOG[3]:.3f}        {BLEND_WEIGHTS_PHI[3]:.3f}      {BLEND_WEIGHTS_DECAY[3]:.3f}

  (weight = how much OUTER gate this member feels; 1-weight = inner)

  Outer gate: Gleissberg phase, acc_frac = 0.618 (natural ARA)
  Inner gate: Schwabe phase, acc_frac = 0.400 (drain-compressed)
    """)

    results = []

    # Baseline
    print("Running 203b baseline...")
    r = evaluate("203b single gate", predict_203b)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # Static blends with different weight schemes
    for wname, weights in [("log", BLEND_WEIGHTS_LOG),
                            ("phi-linear", BLEND_WEIGHTS_PHI),
                            ("phi-decay", BLEND_WEIGHTS_DECAY)]:
        for drain in [False, True]:
            dstr = "+drain" if drain else ""
            lbl = f"V1 {wname}{dstr}"
            print(f"Running {lbl}...")
            fn = mk_static(weights, drain, lbl)
            r = evaluate(lbl, fn)
            results.append(r)
            print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
                  f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # Causal outer with best weight scheme (try all 3)
    for wname, weights in [("log", BLEND_WEIGHTS_LOG),
                            ("phi-linear", BLEND_WEIGHTS_PHI),
                            ("phi-decay", BLEND_WEIGHTS_DECAY)]:
        for drain in [False, True]:
            dstr = "+drain" if drain else ""
            lbl = f"V2 {wname}{dstr}"
            print(f"Running {lbl} (causal outer)...")
            fn = mk_causal_outer(weights, drain)
            r = evaluate(lbl, fn, is_seq=True)
            results.append(r)
            print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
                  f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # Causal both with best weight scheme
    for wname, weights in [("log", BLEND_WEIGHTS_LOG),
                            ("phi-linear", BLEND_WEIGHTS_PHI),
                            ("phi-decay", BLEND_WEIGHTS_DECAY)]:
        for drain in [False, True]:
            dstr = "+drain" if drain else ""
            lbl = f"V3 {wname}{dstr}"
            print(f"Running {lbl} (causal both)...")
            fn = mk_causal_both(weights, drain)
            r = evaluate(lbl, fn, is_seq=True)
            results.append(r)
            print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
                  f"rise r={r['rr']:+.3f}, splits={r['sw']}/7")

    # === COMPARISON ===
    print(f"\n{'='*70}")
    print("FULL COMPARISON")
    print(f"{'='*70}")

    print(f"\n  {'Model':<24s} {'LOO':>7s} {'%sine':>7s} {'Wins':>5s} "
          f"{'Rise r':>7s} {'Amp r':>7s} {'Split':>5s}")
    print(f"  {'-'*24} {'-'*7} {'-'*7} {'-'*5} {'-'*7} {'-'*7} {'-'*5}")
    for r in results:
        print(f"  {r['label']:<24s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['wins']:3d}/25 {r['rr']:+7.3f} {r['ar']:+7.3f} "
              f"{r['sw']:2d}/7")

    bl = min(results, key=lambda r: r['loo'])
    bw = min(results, key=lambda r: abs(r['rr']))
    bs = max(results, key=lambda r: (r['sw'], -r['loo']))

    print(f"\n  BEST LOO: {bl['label']} ({bl['loo']:.2f}, {bl['imp']:+.1f}%)")
    print(f"  BEST WALDMEIER: {bw['label']} (r={bw['rr']:+.3f})")
    print(f"  BEST SPLITS: {bs['label']} ({bs['sw']}/7, LOO={bs['loo']:.2f})")

    # Splits detail for top
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

    # === CROSS-REFERENCE ===
    print(f"\n{'='*70}")
    print("CROSS-REFERENCE: ALL SCRIPTS 203b-213")
    print(f"{'='*70}")
    print(f"""
  203b single gate (0.618):       LOO=37.66, splits=1/7, rise r=+0.767
  207 V1 causal gate:             LOO=38.82, splits=3/7 ← extrap champ
  209 V5 causal+drain:            LOO=36.97, splits=2/7
  210 V5 causal+AR drain:         LOO=36.62, splits=2/7
  211 V4d Wald gate+drain:        LOO=36.46, splits=0/7 ← interp champ
  212 V2 two-gate causal:         LOO=39.27, splits=2/7, rise r=+0.752

  This script:
    Best LOO:    {bl['label']}: {bl['loo']:.2f} ({bl['imp']:+.1f}%), splits={bl['sw']}/7
    Best Wald:   {bw['label']}: rise r={bw['rr']:+.3f}
    Best splits: {bs['label']}: {bs['sw']}/7
    """)

    print(f"{'='*70}")
    print("SUMMARY — SCRIPT 213")
    print(f"{'='*70}")
    print(f"""
  Blended gate: each cascade member blends outer + inner gate
  weighted by its position in the scale hierarchy.

  Internal energy has full authority at its own level but must
  transform up a log to affect the system level — the blend
  weights encode this transformation cost.

  BEST LOO: {bl['label']}
    MAE = {bl['loo']:.2f} ({bl['imp']:+.1f}% vs sine)
    Wins: {bl['wins']}/25
    Rise frac r = {bl['rr']:+.3f}
    Splits: {bl['sw']}/7

  Three weight schemes tested:
    Log:       w = log(P/P_inner) / log(P_outer/P_inner)
    φ-linear:  w = (power - 4) / 7
    φ-decay:   w = 1 - 1/φ^(power-4)

  The blend preserves the multiplicative cascade's cross-coupling
  while encoding two AR values at two scales.
""")
