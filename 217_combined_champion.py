#!/usr/bin/env python3
"""
Script 217 — Combined Champion: V5 Inner Pulse + Causal + Drain + Horizontal

BREAKTHROUGH FROM 216:
  V5 inner-only with ARA decay: LOO=35.28, 4/7 splits, rise r=+0.690
  First model to beat BOTH interpolation AND extrapolation champions.

THIS SCRIPT:
  Phase 1: Combine V5 with causal gate + drain (vertical refinement)
  Phase 2: Add horizontal coupling — energy from neighboring cycles
           at the SAME scale level bleeding sideways

  Dylan's insight: "it's not just up and down, but side to side too"
  The ARA has three dimensions of energy flow:
    - Vertical UP:   inner system → Sun (Script 216 V5 ✓)
    - Vertical DOWN: above system → Sun (Script 214, weak effect)
    - HORIZONTAL:    previous cycle's residual → current cycle
                     Each cycle's release phase bleeds into the next
                     cycle's accumulation phase at the same level.

  Horizontal coupling = the previous cycle's RELEASE energy that
  didn't fully dissipate before the next cycle began. This residual
  enters the new cycle's accumulation phase as a head start (or deficit).

FREE PARAMETERS: 2 (base_amp, t_ref)
"""

import numpy as np
import warnings, time
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
peak_years  = np.array([CYCLES[c][1] for c in cycle_nums])
peak_amps   = np.array([CYCLES[c][2] for c in cycle_nums])
durations   = np.array([CYCLES[c][3] for c in cycle_nums])
rise_fracs  = (peak_years - start_years) / durations
N = len(cycle_nums)
MEAN_AMP = peak_amps.mean()
MEAN_RF  = rise_fracs.mean()

SCHWABE    = PHI**5
GLEISSBERG = PHI**9
SUN_ACC    = PHI / (PHI + 1)  # 0.618

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


def singularity_pulse_ara_decay(phase, decay_rate):
    """Fires at singularity (phase=0), decays at ARA rate."""
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    return np.exp(-decay_rate * cycle_pos)


# =================================================================
# PHASE 1: V5 + Causal + Drain variants
# =================================================================

def predict_v5_static(t, ba, tr, cc=INV_PHI_3, decay=PHI):
    """216 V5: 203b cascade + inner pulse with ARA decay. Static gate."""
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

    # Inner pulse: φ⁵ at Schwabe singularities, ARA decay
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    pulse = singularity_pulse_ara_decay(schwabe_phase, decay)
    amp += ba * cc * pulse * np.cos(schwabe_phase)

    return amp


def mk_v5_causal(cc=INV_PHI_3, decay=PHI, use_drain=False,
                 use_wald=False):
    """V5 with causal outer gate (prev cycle sets acc_frac)."""
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            if i == 0:
                sa = SUN_ACC
            else:
                prev_ara = amps[i - 1] / ba
                sa = ara_to_acc(prev_ara)

            gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG
            gate = sawtooth_valve(gleiss_phase, sa)
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

            # Inner pulse
            schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
            pulse = singularity_pulse_ara_decay(schwabe_phase, decay)
            amp += ba * cc * pulse * np.cos(schwabe_phase)

            # Drain
            if use_drain:
                if use_wald and i > 0:
                    rf = wald_rf(amps[i - 1])
                    ara_cycle = rf / (1 - rf)
                    drain_scale = ara_cycle / PHI
                else:
                    drain_scale = 1.0
                amp_ratio = amp / ba
                amp -= INV_PHI_9 * amp * amp_ratio * drain_scale * abs(np.cos(gleiss_phase))

            preds.append(amp)
        return preds
    return _p


# =================================================================
# PHASE 2: Horizontal coupling
# =================================================================

def mk_v5_horizontal(cc=INV_PHI_3, decay=PHI, h_cc=INV_PHI_3,
                     h_mode='residual', use_drain=False, use_wald=False):
    """
    V5 + horizontal coupling from neighboring cycles.

    h_mode options:
      'residual': previous cycle's undissipated energy carries over
                  Amount = prev_amp * exp(-φ × duration_fraction)
                  This is the ARA decay residual — what's left after
                  the previous cycle dissipated through its release phase.

      'half_each': take half the horizontal from each side (prev + next neighbor)
                   Only uses prev in causal mode; both when training on known data.

      'delta':     horizontal correction = difference from mean
                   High prev cycle → positive residual → boosts current
                   Low prev cycle → negative residual → suppresses current
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            # Causal gate
            if i == 0:
                sa = SUN_ACC
            else:
                prev_ara = amps[i - 1] / ba
                sa = ara_to_acc(prev_ara)

            # Base cascade
            gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG
            gate = sawtooth_valve(gleiss_phase, sa)
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

            # Vertical: inner pulse
            schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
            pulse = singularity_pulse_ara_decay(schwabe_phase, decay)
            amp += ba * cc * pulse * np.cos(schwabe_phase)

            # Horizontal coupling
            if i > 0:
                prev_amp = amps[i - 1]

                if h_mode == 'residual':
                    # Previous cycle's release energy that didn't fully dissipate
                    # The residual after a full cycle at decay rate φ:
                    # residual = prev_amp * exp(-φ)
                    # This is what bleeds into the next cycle's start
                    residual = prev_amp * np.exp(-PHI)
                    # Normalized: how much above/below mean?
                    h_correction = (residual - ba * np.exp(-PHI)) * h_cc
                    amp += h_correction

                elif h_mode == 'delta':
                    # Simple: previous amplitude relative to base
                    delta = (prev_amp - ba) / ba
                    amp += ba * h_cc * delta * np.exp(-PHI)

                elif h_mode == 'ara_bleed':
                    # The ARA of the previous cycle determines how much
                    # bleeds horizontally. High ARA = fast release = more bleed.
                    # Low ARA = slow release = less bleed.
                    prev_rf = rise_fracs[i - 1] if i - 1 < len(rise_fracs) else MEAN_RF
                    prev_ara = prev_rf / (1 - prev_rf)
                    # More asymmetric release = more leftover energy
                    bleed = prev_amp * (1 - prev_ara / PHI) * np.exp(-PHI)
                    h_correction = (bleed - ba * (1 - 1) * np.exp(-PHI)) * h_cc
                    amp += (prev_amp - ba) * h_cc * (prev_ara / PHI) * np.exp(-decay)

                elif h_mode == 'half_each':
                    # Half from previous, half from... well, causal so only prev
                    residual = (prev_amp - ba) * h_cc * 0.5 * np.exp(-PHI)
                    amp += residual

            # Drain
            if use_drain:
                if use_wald and i > 0:
                    rf = wald_rf(amps[i - 1])
                    ara_cycle = rf / (1 - rf)
                    drain_scale = ara_cycle / PHI
                else:
                    drain_scale = 1.0
                amp_ratio = amp / ba
                amp -= INV_PHI_9 * amp * amp_ratio * drain_scale * abs(np.cos(gleiss_phase))

            preds.append(amp)
        return preds
    return _p


# =================================================================
# FITTING + EVAL
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
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:nt].mean()), ta)
        w = "phi" if pm < sm else "sine"
        if pm < sm: sw += 1
        sd.append((nt, N - nt, pm, sm, w))

    return {'label': label, 'loo': loo, 'sine': sl,
            'imp': (loo / sl - 1) * 100, 'wins': int(np.sum(pe < se)),
            'rr': rr, 'sw': sw, 'sd': sd, 'pf': pf, 'ba': bf, 'tr': tf}


# =================================================================
# MAIN
# =================================================================

if __name__ == '__main__':
    t0 = time.time()

    print("=" * 70)
    print("SCRIPT 217 — COMBINED CHAMPION")
    print("=" * 70)
    print("""
  Base: V5 inner pulse + ARA decay (LOO=35.28, 4/7 splits)
  Phase 1: + causal gate, + drain, + Waldmeier drain
  Phase 2: + horizontal coupling (side-to-side energy bleed)
""")

    results = []

    # ---- Reference: V5 static (from 216) ----
    print("[1] V5 static (reference)...")
    r = evaluate("V5 static ref", predict_v5_static)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # ---- Phase 1: Causal + drain ----
    print(f"\n{'='*70}")
    print("PHASE 1: V5 + CAUSAL GATE + DRAIN")
    print(f"{'='*70}")

    print("\n[2] V5 causal (no drain)...")
    fn = mk_v5_causal()
    r = evaluate("V5 causal", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[3] V5 causal + drain...")
    fn = mk_v5_causal(use_drain=True)
    r = evaluate("V5 causal+drain", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[4] V5 causal + Waldmeier drain...")
    fn = mk_v5_causal(use_drain=True, use_wald=True)
    r = evaluate("V5 causal+Wald drain", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # ---- Phase 2: Horizontal coupling ----
    print(f"\n{'='*70}")
    print("PHASE 2: V5 + HORIZONTAL COUPLING")
    print(f"{'='*70}")

    # Residual mode — previous cycle's undissipated energy
    print("\n[5] V5 causal + horizontal residual (cc=1/phi3)...")
    fn = mk_v5_horizontal(h_mode='residual', h_cc=INV_PHI_3)
    r = evaluate("H:residual 1/phi3", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[6] V5 causal + horizontal residual (cc=1/phi4)...")
    fn = mk_v5_horizontal(h_mode='residual', h_cc=INV_PHI_4)
    r = evaluate("H:residual 1/phi4", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[7] V5 causal + horizontal residual (cc=1/phi6)...")
    fn = mk_v5_horizontal(h_mode='residual', h_cc=INV_PHI**6)
    r = evaluate("H:residual 1/phi6", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # Delta mode — amplitude deviation from base
    print("\n[8] V5 causal + horizontal delta (cc=1/phi3)...")
    fn = mk_v5_horizontal(h_mode='delta', h_cc=INV_PHI_3)
    r = evaluate("H:delta 1/phi3", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[9] V5 causal + horizontal delta (cc=1/phi4)...")
    fn = mk_v5_horizontal(h_mode='delta', h_cc=INV_PHI_4)
    r = evaluate("H:delta 1/phi4", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # Half-each mode
    print("\n[10] V5 causal + horizontal half (cc=1/phi3)...")
    fn = mk_v5_horizontal(h_mode='half_each', h_cc=INV_PHI_3)
    r = evaluate("H:half 1/phi3", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # ---- Phase 3: Best horizontal + drain ----
    print(f"\n{'='*70}")
    print("PHASE 3: BEST HORIZONTAL + DRAIN COMBINATIONS")
    print(f"{'='*70}")

    # Find best horizontal
    horiz_results = [r for r in results if r['label'].startswith('H:')]
    if horiz_results:
        best_h = min(horiz_results, key=lambda r: r['loo'])
        print(f"  Best horizontal: {best_h['label']} (LOO={best_h['loo']:.2f})")

    # Residual + drain combos
    for h_cc_name, h_cc_val in [("1/phi3", INV_PHI_3), ("1/phi4", INV_PHI_4)]:
        for drain_type in ['drain', 'wald']:
            use_w = drain_type == 'wald'
            lbl = f"H:res {h_cc_name}+{drain_type}"
            fn = mk_v5_horizontal(h_mode='residual', h_cc=h_cc_val,
                                  use_drain=True, use_wald=use_w)
            r = evaluate(lbl, fn, is_seq=True)
            results.append(r)
            print(f"  {lbl:<30s} LOO={r['loo']:7.2f} ({r['imp']:+.1f}%) "
                  f"rise r={r['rr']:+.3f} splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # Delta + drain combos
    for h_cc_name, h_cc_val in [("1/phi3", INV_PHI_3), ("1/phi4", INV_PHI_4)]:
        for drain_type in ['drain', 'wald']:
            use_w = drain_type == 'wald'
            lbl = f"H:dlt {h_cc_name}+{drain_type}"
            fn = mk_v5_horizontal(h_mode='delta', h_cc=h_cc_val,
                                  use_drain=True, use_wald=use_w)
            r = evaluate(lbl, fn, is_seq=True)
            results.append(r)
            print(f"  {lbl:<30s} LOO={r['loo']:7.2f} ({r['imp']:+.1f}%) "
                  f"rise r={r['rr']:+.3f} splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # =================================================================
    # FINAL REPORT
    # =================================================================

    all_sorted = sorted(results, key=lambda r: r['loo'])
    bl = all_sorted[0]
    bw = min(results, key=lambda r: abs(r['rr']))
    bs = max(results, key=lambda r: (r['sw'], -r['loo']))

    print(f"\n{'='*70}")
    print("ALL MODELS (sorted by LOO)")
    print(f"{'='*70}")
    print(f"\n  {'Model':<35s} {'LOO':>7s} {'%sine':>7s} {'Rise r':>7s} {'Split':>5s}")
    print(f"  {'-'*35} {'-'*7} {'-'*7} {'-'*7} {'-'*5}")
    for r in all_sorted:
        print(f"  {r['label']:<35s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['rr']:+7.3f} {r['sw']:2d}/7")

    print(f"\n  BEST LOO:      {bl['label']} ({bl['loo']:.2f})")
    print(f"  BEST WALDMEIER: {bw['label']} (r={bw['rr']:+.3f})")
    print(f"  BEST SPLITS:   {bs['label']} ({bs['sw']}/7)")

    # Temporal splits for key models
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS — KEY MODELS")
    print(f"{'='*70}")
    shown = set()
    for r in [bl, bs, bw] + all_sorted[:3]:
        if r['label'] in shown: continue
        shown.add(r['label'])
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            mg = sm - pm if w == "phi" else pm - sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: "
                  f"phi={pm:.1f}  sine={sm:.1f}  -> {w} ({mg:.1f})")

    # Dalton
    print(f"\n{'='*70}")
    print("DALTON MINIMUM (Cycles 5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    shown2 = set()
    for r in all_sorted[:5] + [bw, bs]:
        if r['label'] in shown2: continue
        shown2.add(r['label'])
        d = [4, 5, 6]
        dm = np.mean([abs(r['pf'][i] - peak_amps[i]) for i in d])
        print(f"  {r['label']:<35s} Dalton MAE={dm:.1f}  "
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
    print("CROSS-REFERENCE — ALL-TIME SCOREBOARD")
    print(f"{'='*70}")
    print(f"""
  203b single gate:        LOO=37.66, splits=1/7, rise r=+0.767
  207 V1 causal:           LOO=38.82, splits=3/7 <- was extrap champ
  210 V5 causal+drain:     LOO=36.62, splits=2/7
  211 V4d Wald+drain:      LOO=36.46, splits=0/7 <- was interp champ
  214 V4 deep caus:        rise r=+0.583 <- Waldmeier champ
  216 V5 inner pulse:      LOO=35.28, splits=4/7 <- COMBINED CHAMPION

  This script (combined):
    Best LOO:    {bl['label']}: {bl['loo']:.2f}, splits={bl['sw']}/7
    Best Wald:   {bw['label']}: r={bw['rr']:+.3f}
    Best splits: {bs['label']}: {bs['sw']}/7

  Total time: {time.time()-t0:.0f}s
""")
