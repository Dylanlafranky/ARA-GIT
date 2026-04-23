#!/usr/bin/env python3
"""
Script 223j — Curvy Beeswax (Smooth φ-Blend Collision)

DYLAN'S INSIGHT:
  The beeswax geometry is RIGHT but the vertex/edge decomposition
  was TRIANGULAR (|cos|, 1-|cos|) when it should be CURVED.

  Beeswax cells start as CIRCLES, melt into hexagons.
  The transitions are smooth, not angular.

  Three approaches to "curvy":

  [1] Smooth cos²/sin² blend:
      cos² = smooth vertex zone (peaks at extremes, zero at crossings)
      sin² = smooth edge zone (peaks at crossings, zero at extremes)
      Natural wave decomposition: cos² + sin² = 1
      Vertex collision (weak, ×1/φ) + edge collision (strong, ×φ)

  [2] Phase-difference collision:
      cos(phase_prev - phase_curr) = cos·cos + sin·sin
      Single smooth function. No decomposition needed.
      Naturally blends vertex and edge via trig identity.
      The smoothest possible curve through the beeswax corridor.

  [3] Asymmetric phase-difference:
      Decompose cos(Δphase) but weight components by φ:
      collision = cos·cos × 1/φ + sin·sin × φ
      Weak vertex glancing + strong edge separation.
      But through the SMOOTH cos²/sin² natural partition,
      not through triangular |cos|/(1-|cos|).
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


PERIODS = [PHI**11, PHI**9, PHI**6, PHI**4]


# =================================================================
# MODEL 1: Smooth cos²/sin² blend (weak vertex + strong edge)
# =================================================================
def mk_smooth_blend(h_cc=INV_PHI_3):
    """
    Vertex zone: cos²(prev) × cos²(curr) — smooth, peaks at extremes
    Edge zone:   sin²(prev) × sin²(curr) — smooth, peaks at zero-crossings

    Vertex collision: -cos_prev × cos_curr (champion) weighted by cos²×cos²
    Edge collision:   -sin_prev × sin_curr weighted by sin²×sin²

    Vertex weak (×1/φ), edge strong (×φ).
    Natural smooth blending: cos⁴+sin⁴ partition (not linear ramp).
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            gp = 2*np.pi*(t-tr)/GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            phases = [2*np.pi*(t-tr)/per for per in PERIODS]
            cos_vals = [np.cos(ph) for ph in phases]
            sin_vals = [np.sin(ph) for ph in phases]

            amp = ba
            for j, per in enumerate(PERIODS):
                w = cos_vals[j]
                tens = -sin_vals[j]
                eps = INV_PHI_4 * gate

                if j > 0:
                    cp, cc = cos_vals[j-1], cos_vals[j]
                    sp, sc = sin_vals[j-1], sin_vals[j]

                    # Smooth vertex zone: cos² × cos² weighting
                    vertex_wt = cp*cp * cc*cc  # peaks when both at extremes
                    vertex_col = -cp * cc      # champion-style

                    # Smooth edge zone: sin² × sin² weighting
                    edge_wt = sp*sp * sc*sc    # peaks when both at crossings
                    edge_col = -sp * sc        # velocity-based

                    # Weak vertex + strong edge (smooth curves, not triangles)
                    collision = (vertex_col * vertex_wt * INV_PHI +
                                 edge_col * edge_wt * PHI)

                    eps *= (1 + collision * INV_PHI)

                # Standard tension asymmetry
                if tens > 0: eps *= (1 + 0.5*tens*(PHI-1))
                else:        eps *= (1 + 0.5*tens*(1-INV_PHI))

                amp *= (1 + eps*w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2*np.pi*(t-tr)/SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI)

            preds.append(amp)
        return preds
    return _p


# =================================================================
# MODEL 2: Phase-difference collision (single smooth function)
# =================================================================
def mk_phase_diff(h_cc=INV_PHI_3):
    """
    cos(phase_prev - phase_curr) = cos·cos + sin·sin

    One smooth function that captures the FULL phase relationship
    between adjacent periods. No decomposition, no weighting.
    The smoothest possible curve through the beeswax corridor.

    When phases are aligned (Δ=0): cos(0)=1, max positive coupling
    When phases are opposed (Δ=π): cos(π)=-1, max negative coupling
    Smooth sinusoidal transition between.

    Use NEGATIVE: -cos(Δphase) so that anti-phase = strong coupling
    (matching champion's sign convention).
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            gp = 2*np.pi*(t-tr)/GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            phases = [2*np.pi*(t-tr)/per for per in PERIODS]
            cos_vals = [np.cos(ph) for ph in phases]

            amp = ba
            for j, per in enumerate(PERIODS):
                w = cos_vals[j]
                tens = -np.sin(phases[j])
                eps = INV_PHI_4 * gate

                if j > 0:
                    # Single smooth function: cos of phase difference
                    phase_diff = phases[j-1] - phases[j]
                    collision = -np.cos(phase_diff)

                    eps *= (1 + collision * INV_PHI)

                # Standard tension asymmetry
                if tens > 0: eps *= (1 + 0.5*tens*(PHI-1))
                else:        eps *= (1 + 0.5*tens*(1-INV_PHI))

                amp *= (1 + eps*w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2*np.pi*(t-tr)/SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI)

            preds.append(amp)
        return preds
    return _p


# =================================================================
# MODEL 3: Asymmetric phase-difference (φ-weighted smooth)
# =================================================================
def mk_asym_phase(h_cc=INV_PHI_3):
    """
    Decompose cos(Δphase) into its components but weight by φ:

    cos(a-b) = cos(a)cos(b) + sin(a)sin(b)
                ^^^^^^^^^^^^   ^^^^^^^^^^^^^
                vertex part    edge part

    Weight: vertex × 1/φ (glancing) + edge × φ (separating)

    collision = -(cos_p·cos_c × 1/φ  +  sin_p·sin_c × φ)

    Same smooth cos²/sin² curves as phase-difference,
    but with φ asymmetry between vertex and edge.
    This IS the curvy beeswax: circles→hexagons with φ geometry.
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            gp = 2*np.pi*(t-tr)/GLEISSBERG
            gate = sawtooth_valve(gp, sa)

            phases = [2*np.pi*(t-tr)/per for per in PERIODS]
            cos_vals = [np.cos(ph) for ph in phases]
            sin_vals = [np.sin(ph) for ph in phases]

            amp = ba
            for j, per in enumerate(PERIODS):
                w = cos_vals[j]
                tens = -sin_vals[j]
                eps = INV_PHI_4 * gate

                if j > 0:
                    cp, cc = cos_vals[j-1], cos_vals[j]
                    sp, sc = sin_vals[j-1], sin_vals[j]

                    # Asymmetric phase-difference:
                    # vertex (cos·cos) weak, edge (sin·sin) strong
                    collision = -(cp*cc * INV_PHI + sp*sc * PHI)

                    eps *= (1 + collision * INV_PHI)

                # Standard tension asymmetry
                if tens > 0: eps *= (1 + 0.5*tens*(PHI-1))
                else:        eps *= (1 + 0.5*tens*(1-INV_PHI))

                amp *= (1 + eps*w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2*np.pi*(t-tr)/SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

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


if __name__ == '__main__':
    t0 = time.time()
    print("="*70)
    print("SCRIPT 223j — CURVY BEESWAX (SMOOTH φ-BLEND COLLISION)")
    print("="*70)
    print(f"""
  Circles (π) melt into hexagons (φ). Transitions are CURVED.

  [1] Smooth blend: cos²×cos² vertex (weak) + sin²×sin² edge (strong)
  [2] Phase-difference: cos(Δphase) — single smooth curve
  [3] Asymmetric: cos·cos×1/φ + sin·sin×φ — φ-weighted smooth blend
""")

    results = []

    # [1] Smooth cos²/sin² blend
    print("[1/3] Smooth cos²/sin² blend...")
    fn1 = mk_smooth_blend(h_cc=INV_PHI_3)
    r = evaluate("Smooth blend", fn1)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [2] Phase-difference (single smooth function)
    print("\n[2/3] Phase-difference collision...")
    fn2 = mk_phase_diff(h_cc=INV_PHI_3)
    r = evaluate("Phase-diff", fn2)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [3] Asymmetric phase-difference
    print("\n[3/3] Asymmetric phase-difference...")
    fn3 = mk_asym_phase(h_cc=INV_PHI_3)
    r = evaluate("Asym φ-phase", fn3)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

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

    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS")
    print(f"{'='*70}")
    for r in all_sorted:
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            mg = sm-pm if w == "phi" else pm-sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: phi={pm:.1f} sine={sm:.1f} -> {w} ({mg:.1f})")

    print(f"\n{'='*70}")
    print("DALTON (C5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    for r in all_sorted:
        d = [4, 5, 6]
        dm = np.mean([abs(r['pf'][i] - peak_amps[i]) for i in d])
        print(f"  {r['label']:<25s} MAE={dm:.1f} "
              f"(C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f})")

    bn = all_sorted[0]
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {bn['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s}")
    for i, c in enumerate(cycle_nums):
        p = bn['pf'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} {p-peak_amps[i]:+7.1f}")

    print(f"\n{'='*70}")
    print("SCOREBOARD")
    print(f"{'='*70}")
    print(f"  223d Mirror collision:  LOO=33.25, 5/7, r=+0.702  (champion)")
    print(f"  223g Beeswax log1p:     LOO=33.58, 5/7, r=+0.706")
    print(f"  220 Hale h=1/φ³:       LOO=34.80, 4/7, r=+0.700")
    print(f"  203b baseline:          LOO=37.66, 1/7, r=+0.767")
    print(f"  ---")
    print(f"  This best: {bl['label']}: LOO={bl['loo']:.2f}, {bl['sw']}/7, r={bl['rr']:+.3f}")
    print(f"\n  Time: {time.time()-t0:.0f}s")
