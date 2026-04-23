#!/usr/bin/env python3
"""
Script 215 — Singularity-Gated Vertical Coupling

INSIGHT (Dylan):
  Energy doesn't bleed continuously between levels. It crosses
  at SINGULARITY POINTS — when a system completes a full circle.

  Level 1 (Inner) → Level 2 (Sun):
    Energy enters when the INNER system completes a cycle.
    The Schwabe cycle (φ⁵ ≈ 11yr) has troughs every ~11 years.
    AT those troughs, inner energy pulses into the Sun level.
    Between troughs: zero vertical coupling from below.

  Level 3 (Above) → Level 2 (Sun):
    Energy enters when the SUN system completes a full circle.
    The Gleissberg cycle (φ⁹ ≈ 76yr) has troughs every ~76 years.
    AT those troughs, above energy pulses into the Sun level.
    Between troughs: zero vertical coupling from above.

  This is how ARA works at every scale — singularities are the
  ONLY points where energy crosses between levels. The rest of
  the time, each level's own field shields it.

SINGULARITY PULSE:
  Near a singularity (phase ≈ 0 or 2π), coupling strength peaks.
  Away from singularity, coupling → 0.

  Pulse shape: exp(-α × min_distance_to_singularity²)
  Width parameter α controls how sharp the pulse is.
  α = φ² gives a pulse that's ~38.2% of the cycle (1/φ of the period).

CASCADE ARCHITECTURE:
  Level 2 (Sun): φ⁶, φ⁹ — continuous, full coupling (this is US)
  Level 1 (Inner): φ⁴, φ⁵ — pulses in at Schwabe singularities
  Level 3 (Above): φ¹¹, φ¹³ — pulses in at Gleissberg singularities
                                (OPPOSING — destructive interference)

FREE PARAMETERS: 2 (base_amp, t_ref)
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9
INV_PHI_3 = INV_PHI ** 3

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

# Three-level periods
LEVEL1 = [PHI**4, PHI**5]        # Inner: 6.9yr, 11.1yr
LEVEL2 = [PHI**6, PHI**9]        # Sun: 17.9yr, 76.0yr
LEVEL3 = [PHI**11, PHI**13]      # Above: 199yr, 521yr
LEVEL3_DEEP = [PHI**11, PHI**13, PHI**15]  # + 1364yr

SCHWABE = PHI**5
GLEISSBERG = PHI**9

# Gate fractions
INNER_ACC = MEAN_RF    # 0.400
SUN_ACC = PHI / (PHI + 1)  # 0.618
ABOVE_ACC = SUN_ACC    # 0.618

# Waldmeier
wald_c = np.polyfit(peak_amps, rise_fracs, 1)
wald_rf = lambda a: np.clip(wald_c[0] * a + wald_c[1], 0.15, 0.85)


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


def singularity_pulse(phase, width_param):
    """
    Pulse that peaks at singularity points (phase = 0, 2π, 4π...).

    Returns value in [0, 1]:
      1.0 at exact singularity
      ~0 far from singularity

    width_param controls pulse width:
      φ²: pulse covers ~1/φ of the cycle (~38.2%)
      φ³: sharper, ~23.6% of cycle
      φ⁴: very sharp, ~14.6% of cycle
    """
    # Distance to nearest singularity (0 or 2π)
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    dist = min(cycle_pos, 1 - cycle_pos)  # 0 at singularity, 0.5 at midpoint

    return np.exp(-width_param * (dist * 2 * np.pi) ** 2)


# =================================================================
# PREDICTION MODELS
# =================================================================

def predict_203b(t, ba, tr):
    """Baseline."""
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


def predict_sg(t, ba, tr, inner_acc=INNER_ACC, sun_acc=SUN_ACC,
                above_acc=ABOVE_ACC, level3=None,
                pulse_width=PHI**2, cross_coupling=INV_PHI_3,
                oppose_above=True, use_drain=False):
    """
    Singularity-Gated Three-Level Model.

    Level 2 (Sun): continuous — this is our system
    Level 1 (Inner): pulses in at Schwabe singularities
    Level 3 (Above): pulses in at Gleissberg singularities
    """
    if level3 is None:
        level3 = LEVEL3

    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG

    sun_gate = sawtooth_valve(gleiss_phase, sun_acc)
    inner_gate = sawtooth_valve(schwabe_phase, inner_acc)
    above_gate = sawtooth_valve(gleiss_phase, above_acc)

    # Singularity pulses
    inner_pulse = singularity_pulse(schwabe_phase, pulse_width)
    above_pulse = singularity_pulse(gleiss_phase, pulse_width)

    amp = ba

    # Level 2 (Sun): continuous, full coupling
    for period in LEVEL2:
        phase = 2 * np.pi * (t - tr) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * sun_gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    # Level 1 (Inner): GATED by Schwabe singularity pulse
    for period in LEVEL1:
        phase = 2 * np.pi * (t - tr) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * inner_gate * cross_coupling * inner_pulse
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    # Level 3 (Above): GATED by Gleissberg singularity pulse
    sign = -1.0 if oppose_above else 1.0
    for period in level3:
        phase = 2 * np.pi * (t - tr) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * above_gate * cross_coupling * above_pulse * sign
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    if use_drain:
        amp_ratio = amp / ba
        amp -= INV_PHI_9 * amp * amp_ratio * abs(np.cos(gleiss_phase))
    else:
        amp += ba * INV_PHI_9 * np.cos(gleiss_phase)

    return amp


# === WRAPPERS ===

def mk_static(pw=PHI**2, cc=INV_PHI_3, opp=True, drain=False,
               l3=None, label=""):
    def _p(t, ba, tr):
        return predict_sg(t, ba, tr, pulse_width=pw, cross_coupling=cc,
                           oppose_above=opp, use_drain=drain, level3=l3)
    _p.__name__ = label
    return _p


def mk_causal(pw=PHI**2, cc=INV_PHI_3, opp=True, drain=False, l3=None):
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            if i == 0:
                sa = SUN_ACC
            else:
                prev_ara = amps[i - 1] / ba
                sa = ara_to_acc(prev_ara)
            preds.append(predict_sg(t, ba, tr, sun_acc=sa,
                                     pulse_width=pw, cross_coupling=cc,
                                     oppose_above=opp, use_drain=drain,
                                     level3=l3))
        return preds
    return _p


# =================================================================
# FITTING + EVAL (compact)
# =================================================================

def fit_s(fn, ty, ta):
    best, bba, btr = 1e9, 0, 0
    for tr in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(ta) * 0.6, np.mean(ta) * 1.4, 40):
            m = mae([fn(t, ba, tr) for t in ty], ta)
            if m < best: best, bba, btr = m, ba, tr
    return bba, btr, best

def fit_q(fn, mask, ay, aa):
    best, bba, btr = 1e9, 0, 0
    idx = np.where(mask)[0]; ta = aa[mask]
    for tr in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(ta) * 0.6, np.mean(ta) * 1.4, 40):
            ap = fn(ay, aa, ba, tr)
            m = mae([ap[j] for j in idx], ta)
            if m < best: best, bba, btr = m, ba, tr
    return bba, btr, best

def evaluate(label, fn, is_seq=False):
    pe, se = [], []
    fm = np.ones(N, dtype=bool)
    for i in range(N):
        mask = np.ones(N, dtype=bool); mask[i] = False
        if is_seq:
            ba, tr, _ = fit_q(fn, mask, peak_years, peak_amps)
            pi = fn(peak_years, peak_amps, ba, tr)[i]
        else:
            ba, tr, _ = fit_s(fn, peak_years[mask], peak_amps[mask])
            pi = fn(peak_years[i], ba, tr)
        pe.append(abs(pi - peak_amps[i]))
        se.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    pe, se = np.array(pe), np.array(se)
    loo, sl = pe.mean(), se.mean()

    if is_seq:
        bf, tf, _ = fit_q(fn, fm, peak_years, peak_amps)
        pf = fn(peak_years, peak_amps, bf, tf)
    else:
        bf, tf, _ = fit_s(fn, peak_years, peak_amps)
        pf = [fn(t, bf, tf) for t in peak_years]

    ef = np.array(pf) - peak_amps
    rr = np.corrcoef(rise_fracs, ef)[0, 1]
    ar = np.corrcoef(peak_amps, ef)[0, 1]

    sw, sd = 0, []
    for nt in [5, 8, 10, 12, 15, 18, 20]:
        if nt >= N: continue
        tm = np.zeros(N, dtype=bool); tm[:nt] = True
        if is_seq:
            bs, ts, _ = fit_q(fn, tm, peak_years, peak_amps)
            tp = fn(peak_years, peak_amps, bs, ts)[nt:]
        else:
            bs, ts, _ = fit_s(fn, peak_years[:nt], peak_amps[:nt])
            tp = [fn(t, bs, ts) for t in peak_years[nt:]]
        ta = peak_amps[nt:]
        pm, sm = mae(tp, ta), mae(np.full(len(ta), peak_amps[:nt].mean()), ta)
        w = "φ" if pm < sm else "sine"
        if pm < sm: sw += 1
        sd.append((nt, N - nt, pm, sm, w))

    return {'label': label, 'loo': loo, 'sine': sl,
            'imp': (loo / sl - 1) * 100, 'wins': int(np.sum(pe < se)),
            'rr': rr, 'ar': ar, 'sw': sw, 'sd': sd,
            'pf': pf, 'ba': bf, 'tr': tf}


# =================================================================
# MAIN
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("SCRIPT 215 — SINGULARITY-GATED VERTICAL COUPLING")
    print("=" * 70)
    print(f"""
  Energy crosses between levels ONLY at singularity points.

  Inner → Sun:  pulses at Schwabe troughs (every ~{SCHWABE:.0f}yr)
  Above → Sun:  pulses at Gleissberg troughs (every ~{GLEISSBERG:.0f}yr)

  Pulse widths tested: φ² (broad), φ³ (medium), φ⁴ (sharp)
  Cross-coupling tested: 1/φ³, 1/φ⁶, 1/φ⁹
    """)

    results = []

    # Baseline
    print("Baseline 203b...")
    r = evaluate("203b baseline", predict_203b)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7")

    # Sweep: pulse width × coupling strength × oppose/cooperate
    configs = []

    # Key combinations
    for pw_name, pw in [("φ²", PHI**2), ("φ³", PHI**3), ("φ⁴", PHI**4)]:
        for cc_name, cc in [("1/φ³", INV_PHI_3),
                             ("1/φ⁶", INV_PHI**6),
                             ("1/φ⁹", INV_PHI_9)]:
            for opp in [True, False]:
                opp_str = "opp" if opp else "coop"
                configs.append((f"pw={pw_name} cc={cc_name} {opp_str}",
                                pw, cc, opp))

    # Run all static configs
    print(f"\n{'='*70}")
    print("STATIC SWEEP — pulse_width × coupling × direction")
    print(f"{'='*70}")

    for lbl, pw, cc, opp in configs:
        fn = mk_static(pw=pw, cc=cc, opp=opp, label=lbl)
        r = evaluate(lbl, fn)
        results.append(r)

    # Print sweep results sorted by LOO
    sweep = [r for r in results if r['label'] != '203b baseline']
    sweep.sort(key=lambda r: r['loo'])

    print(f"\n  {'Config':<35s} {'LOO':>7s} {'%sine':>7s} {'Rise r':>7s} {'Split':>5s}")
    print(f"  {'-'*35} {'-'*7} {'-'*7} {'-'*7} {'-'*5}")
    for r in sweep[:10]:
        print(f"  {r['label']:<35s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['rr']:+7.3f} {r['sw']:2d}/7")
    print(f"  ...")
    for r in sweep[-3:]:
        print(f"  {r['label']:<35s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['rr']:+7.3f} {r['sw']:2d}/7")

    # Best static
    best_static = sweep[0]
    best_wald_static = min(sweep, key=lambda r: abs(r['rr']))

    print(f"\n  Best static LOO: {best_static['label']}")
    print(f"    LOO={best_static['loo']:.2f}, rise r={best_static['rr']:+.3f}, "
          f"splits={best_static['sw']}/7")
    print(f"  Best Waldmeier: {best_wald_static['label']}")
    print(f"    rise r={best_wald_static['rr']:+.3f}, LOO={best_wald_static['loo']:.2f}")

    # Now run causal versions of best configs
    print(f"\n{'='*70}")
    print("CAUSAL VERSIONS — best static configs + causal outer gate")
    print(f"{'='*70}")

    # Top 3 by LOO + top by Waldmeier
    causal_configs = set()
    for r in sweep[:3]:
        causal_configs.add(r['label'])
    causal_configs.add(best_wald_static['label'])

    causal_results = []
    for lbl, pw, cc, opp in configs:
        if lbl in causal_configs:
            fn = mk_causal(pw=pw, cc=cc, opp=opp)
            clbl = f"C:{lbl}"
            r = evaluate(clbl, fn, is_seq=True)
            results.append(r)
            causal_results.append(r)
            print(f"  {clbl}")
            print(f"    LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
                  f"splits={r['sw']}/7")

    # + drain versions of best causal
    print(f"\n  + drain variants:")
    for lbl, pw, cc, opp in configs:
        if lbl in causal_configs:
            fn = mk_causal(pw=pw, cc=cc, opp=opp, drain=True)
            clbl = f"C+D:{lbl}"
            r = evaluate(clbl, fn, is_seq=True)
            results.append(r)
            causal_results.append(r)
            print(f"  {clbl}")
            print(f"    LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
                  f"splits={r['sw']}/7")

    # === FINAL COMPARISON ===
    print(f"\n{'='*70}")
    print("TOP 10 MODELS (by LOO)")
    print(f"{'='*70}")

    all_sorted = sorted(results, key=lambda r: r['loo'])
    print(f"\n  {'Model':<40s} {'LOO':>7s} {'%sine':>7s} {'Rise r':>7s} {'Split':>5s}")
    print(f"  {'-'*40} {'-'*7} {'-'*7} {'-'*7} {'-'*5}")
    for r in all_sorted[:10]:
        print(f"  {r['label']:<40s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['rr']:+7.3f} {r['sw']:2d}/7")

    bl = all_sorted[0]
    bw = min(results, key=lambda r: abs(r['rr']))
    bs = max(results, key=lambda r: (r['sw'], -r['loo']))

    print(f"\n  BEST LOO: {bl['label']} ({bl['loo']:.2f})")
    print(f"  BEST WALDMEIER: {bw['label']} (r={bw['rr']:+.3f})")
    print(f"  BEST SPLITS: {bs['label']} ({bs['sw']}/7)")

    # Temporal splits for top models
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS — TOP MODELS")
    print(f"{'='*70}")
    shown = set()
    for r in [bl, bs]:
        if r['label'] in shown: continue
        shown.add(r['label'])
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            mg = sm - pm if w == "φ" else pm - sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: "
                  f"φ={pm:.1f}  sine={sm:.1f}  → {w} ({mg:.1f})")

    # Dalton diagnostic
    print(f"\n{'='*70}")
    print("DALTON MINIMUM DIAGNOSTIC (Cycles 5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    for r in all_sorted[:5] + [bw]:
        d = [4, 5, 6]
        dm = np.mean([abs(r['pf'][i] - peak_amps[i]) for i in d])
        print(f"  {r['label']:<40s} Dalton MAE={dm:.1f}  "
              f"(C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f})")

    # Per-cycle for best
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {bl['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'RF':>6s}")
    for i, c in enumerate(cycle_nums):
        p = bl['pf'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} "
              f"{p - peak_amps[i]:+7.1f} {rise_fracs[i]:6.3f}")

    print(f"\n{'='*70}")
    print("CROSS-REFERENCE")
    print(f"{'='*70}")
    print(f"""
  203b single gate:        LOO=37.66, splits=1/7, rise r=+0.767
  207 V1 causal:           LOO=38.82, splits=3/7 ← extrap champ
  211 V4d Wald+drain:      LOO=36.46, splits=0/7 �� interp champ
  213 V2 blended:          LOO=37.11, splits=2/7
  214 V4 deep caus:        rise r=+0.583 ← Waldmeier champ

  This script (singularity-gated):
    Best LOO:    {bl['label']}: {bl['loo']:.2f}, splits={bl['sw']}/7
    Best Wald:   {bw['label']}: r={bw['rr']:+.3f}
    Best splits: {bs['label']}: {bs['sw']}/7

  SINGULARITY GATING:
    Energy crosses levels ONLY at cycle boundaries.
    Inner → Sun at Schwabe troughs (~every {SCHWABE:.0f}yr)
    Above → Sun at Gleissberg troughs (~every {GLEISSBERG:.0f}yr)
""")
