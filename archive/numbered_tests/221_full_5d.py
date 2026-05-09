#!/usr/bin/env python3
"""
Script 221 — Full 5D: Everything At Once

DYLAN: "Fuck it. We ball."

Bolt ALL missing pieces onto the 220 champion at once:
  BACK:    Causal gate (prev cycle ARA → sawtooth accumulation)
  BELOW:   Inner pulse (singularity decay at φ rate)
  LEFT:    Hale horizontal — prev cycle deviation × cos(π) = -1
  RIGHT:   Hale horizontal — forward neighbor via 2-pass estimation
  ABOVE:   Opposition from outer system (φ¹³ period, singularity-gated)
  DRAIN:   Solar energy loss (Waldmeier-scaled)

2 models only:
  [1] Full 5D: everything
  [2] Full 5D no drain: same minus drain (since drain barely helped before)
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

wald_c = np.polyfit(peak_amps, rise_fracs, 1)
wald_rf = lambda a: np.clip(wald_c[0]*a + wald_c[1], 0.15, 0.85)

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
# CORE PREDICTION POINT
# =================================================================
def predict_point(t, ba, tr, af=SUN_ACC, h_back=0, h_fwd=0,
                  above_cc=0, use_drain=False, ds=1.0):
    """
    Full prediction for a single cycle year.

    Components:
      1. Base cascade: [φ¹¹, φ⁹, φ⁶, φ⁴] with sawtooth valve
      2. Gleissberg additive: ba × 1/φ⁹ × cos(gleiss)
      3. Inner pulse (BELOW): ba × 1/φ³ × decay(φ) × cos(schwabe)
      4. Horizontal (BACK + FWD): pre-computed Hale corrections
      5. Above opposition: -ba × above_cc × decay(gleiss,φ) × cos(φ¹³)
      6. Drain: amplitude-proportional energy loss
    """
    gp = 2*np.pi*(t-tr)/GLEISSBERG
    gate = sawtooth_valve(gp, af)
    amp = ba

    # [1] Four-period cascade
    for per in [PHI**11, PHI**9, PHI**6, PHI**4]:
        ph = 2*np.pi*(t-tr)/per; w = np.cos(ph); tens = -np.sin(ph)
        eps = INV_PHI_4 * gate
        if tens > 0: eps *= (1 + 0.5*tens*(PHI-1))
        else:        eps *= (1 + 0.5*tens*(1-INV_PHI))
        amp *= (1 + eps*w)

    # [2] Gleissberg additive
    amp += ba * INV_PHI_9 * np.cos(gp)

    # [3] Inner pulse (BELOW) — fires at singularity, decays at ARA rate φ
    sp = 2*np.pi*(t-tr)/SCHWABE
    amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

    # [4] Horizontal corrections (Hale inverted)
    amp += h_back + h_fwd

    # [5] Above opposition — outer system pushes back at singularity
    #     φ¹³ period (~843 yr), gated by Gleissberg-phase singularity decay
    if above_cc != 0:
        p13 = 2*np.pi*(t-tr)/(PHI**13)
        amp -= ba * above_cc * sing_pulse_decay(gp, PHI) * np.cos(p13)

    # [6] Drain — energy lost to space, proportional to amplitude²
    if use_drain:
        amp -= INV_PHI_9 * amp * (amp/ba) * ds * abs(np.cos(gp))

    return amp


# =================================================================
# FULL 5D MODEL — 2-PASS WITH HALE INVERSION
# =================================================================
def mk_full_5d(h_cc=INV_PHI_3, above_cc=INV_PHI_3, use_drain=False, use_wald=False):
    """
    Full 5D lock with Hale half-wave inversion on both horizontal neighbors.

    Pass 1: Forward causal only (back horizontal + above + drain)
    Pass 2: Use pass-1 estimates for forward neighbor coupling

    Horizontal coupling carries cos(π) = -1 (INVERTED deviation):
      h_back = ba × (-h_cc) × (prev_obs - ba)/ba × exp(-φ)
      h_fwd  = ba × (-h_cc) × (next_est - ba)/ba × exp(-φ)
    """
    def _p(years, amps, ba, tr):
        n = len(years)

        # ── PASS 1: causal only (no forward neighbor) ──
        p1 = []
        for i in range(n):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            # Hale BACK: inverted previous deviation
            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                h_back = ba * (-h_cc) * prev_dev * np.exp(-PHI)
            else:
                h_back = 0

            # Drain scaling
            ds = 1.0
            if use_drain and use_wald and i > 0:
                rf = wald_rf(amps[i-1])
                ds = (rf/(1-rf)) / PHI

            p1.append(predict_point(years[i], ba, tr, af=sa,
                                     h_back=h_back, h_fwd=0,
                                     above_cc=above_cc,
                                     use_drain=use_drain, ds=ds))

        # ── PASS 2: add forward neighbor from pass-1 estimates ──
        p2 = []
        for i in range(n):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            # Hale BACK: same as pass 1
            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                h_back = ba * (-h_cc) * prev_dev * np.exp(-PHI)
            else:
                h_back = 0

            # Hale FORWARD: inverted next-cycle deviation from pass-1 estimate
            if i < n-1 and h_cc != 0:
                next_dev = (p1[i+1] - ba) / ba
                h_fwd = ba * (-h_cc) * next_dev * np.exp(-PHI)
            else:
                h_fwd = 0

            # Drain scaling
            ds = 1.0
            if use_drain and use_wald and i > 0:
                rf = wald_rf(amps[i-1])
                ds = (rf/(1-rf)) / PHI

            p2.append(predict_point(years[i], ba, tr, af=sa,
                                     h_back=h_back, h_fwd=h_fwd,
                                     above_cc=above_cc,
                                     use_drain=use_drain, ds=ds))

        return p2
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
            'pf': pf, 'ba': bf, 'tr': tf, 'pe': pe}


# =================================================================
# MAIN
# =================================================================
if __name__ == '__main__':
    t0 = time.time()
    print("="*70)
    print("SCRIPT 221 — FULL 5D: EVERYTHING AT ONCE")
    print("="*70)
    print("""
  BACK:  Causal gate (prev ARA → sawtooth)
  BELOW: Inner pulse (singularity decay at φ)
  LEFT:  Hale horizontal — prev deviation × -1 × exp(-φ)
  RIGHT: Hale horizontal — forward neighbor via 2-pass
  ABOVE: Opposition from φ¹³ outer system, singularity-gated
  DRAIN: Waldmeier-scaled amplitude² loss

  "Fuck it. We ball." — Dylan
""")

    results = []

    # [1] Full 5D with drain
    print("[1/2] Full 5D + Wald drain...")
    fn1 = mk_full_5d(h_cc=INV_PHI_3, above_cc=INV_PHI_3,
                      use_drain=True, use_wald=True)
    r = evaluate("Full 5D + drain", fn1)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [2] Full 5D no drain
    print("\n[2/2] Full 5D no drain...")
    fn2 = mk_full_5d(h_cc=INV_PHI_3, above_cc=INV_PHI_3,
                      use_drain=False, use_wald=False)
    r = evaluate("Full 5D no drain", fn2)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # Sort by LOO
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

    # Per-cycle for best
    bn = all_sorted[0]
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {bn['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s}")
    for i, c in enumerate(cycle_nums):
        p = bn['pf'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} {p-peak_amps[i]:+7.1f}")

    # Waldmeier check
    print(f"\n{'='*70}")
    print("WALDMEIER CHECK (rise fraction vs residual)")
    print(f"{'='*70}")
    for r in all_sorted:
        print(f"  {r['label']:<25s} rise-residual r = {r['rr']:+.3f}")

    # Gnevyshev-Ohl
    print(f"\n{'='*70}")
    print("GNEVYSHEV-OHL CHECK")
    print(f"{'='*70}")
    consec_corr = np.corrcoef(peak_amps[:-1], peak_amps[1:])[0, 1]
    print(f"  Observed consecutive correlation: r = {consec_corr:+.3f}")
    delta_amps = np.diff(peak_amps)
    print(f"  Fraction opposite direction: "
          f"{np.mean(delta_amps[:-1] * delta_amps[1:] < 0):.1%}")

    # Scoreboard
    print(f"\n{'='*70}")
    print("SCOREBOARD vs HISTORY")
    print(f"{'='*70}")
    print(f"  220 Hale h=1/φ³:       LOO=34.80, 4/7, r=+0.700  (prev champion)")
    print(f"  216 V5 inner pulse:     LOO=35.28, 4/7, r=+0.690")
    print(f"  217 V5+H:dlt+Wald:     LOO=35.26, 4/7, r=+0.672")
    print(f"  203b baseline:          LOO=37.66, 1/7, r=+0.767")
    print(f"  ---")
    print(f"  This best: {bl['label']}: LOO={bl['loo']:.2f}, {bl['sw']}/7, r={bl['rr']:+.3f}")

    print(f"\n  Time: {time.time()-t0:.0f}s")
