#!/usr/bin/env python3
"""
Script 218 — 4D Lock: Pin the Midpoint from All Directions

DYLAN'S INSIGHT:
  We're finding a midpoint in 4 dimensions. To lock it down you need
  constraints from: back, both sides (horizontal), vertical below,
  and vertical above.

  Current constraints:
    BACK:    Previous cycle amplitude → causal gate         ✓ (Script 207)
    SIDE 1:  Previous cycle residual → horizontal bleed     ✓ (Script 217)
    BELOW:   Inner system pulse at singularity + ARA decay  ✓ (Script 216)
    SIDE 2:  NEXT cycle pull → TWO-PASS estimation          ← NEW
    ABOVE:   Outer system opposition at Gleissberg boundary ← RETRY (weaker)

  TWO-PASS APPROACH FOR SIDE 2:
    Pass 1: Run the model forward (causal, only backward-looking).
            This gives rough estimates for all cycles.
    Pass 2: Re-run with the Pass 1 estimates available as "future"
            neighbors. Each cycle now has BOTH sides locked.
            The "forward" neighbor's residual bleeds back just like
            the "backward" neighbor's does.

  This is self-consistent: the model predicts a pattern, then uses
  that pattern to refine itself. Like solving a system of equations
  iteratively — the cascade geometry tells us what SHOULD be on the
  other side.

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
SUN_ACC    = PHI / (PHI + 1)

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

def sing_pulse_decay(phase, decay_rate):
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    return np.exp(-decay_rate * cycle_pos)


# =================================================================
# SINGLE-POINT PREDICTION (core engine, used by all models)
# =================================================================

def predict_point(t, ba, tr, acc_frac=SUN_ACC,
                  h_back=0.0, h_fwd=0.0,
                  above_cc=0.0, above_pulse=0.0,
                  use_drain=False, drain_scale=1.0):
    """
    Predict amplitude at time t with all 4D constraints.

    Constraints:
      BACK:    acc_frac (causal gate from previous cycle)
      BELOW:   inner pulse built into cascade (always on)
      SIDE 1:  h_back = horizontal bleed from previous cycle
      SIDE 2:  h_fwd = horizontal bleed from next cycle (2-pass)
      ABOVE:   above_cc × above_pulse = opposing energy from above
    """
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG

    # Base cascade with causal gate
    gate = sawtooth_valve(gleiss_phase, acc_frac)
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

    # BELOW: inner pulse (φ⁵ at Schwabe singularities, ARA decay)
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    pulse = sing_pulse_decay(schwabe_phase, PHI)
    amp += ba * INV_PHI_3 * pulse * np.cos(schwabe_phase)

    # SIDE 1 + SIDE 2: horizontal coupling
    amp += h_back + h_fwd

    # ABOVE: opposition at Gleissberg singularities
    if above_cc != 0:
        phase_13 = 2 * np.pi * (t - tr) / (PHI**13)
        g_pulse = sing_pulse_decay(gleiss_phase, PHI)
        amp -= ba * above_cc * g_pulse * np.cos(phase_13)

    # DRAIN
    if use_drain:
        amp_ratio = amp / ba
        amp -= INV_PHI_9 * amp * amp_ratio * drain_scale * abs(np.cos(gleiss_phase))

    return amp


# =================================================================
# MODEL BUILDERS
# =================================================================

def mk_model(h_cc=0.0, above_cc=0.0, use_drain=False, use_wald=False,
             two_pass=False, n_passes=2):
    """
    Build a 4D-locked prediction model.

    h_cc:       horizontal coupling strength (both sides)
    above_cc:   above-level opposition coupling
    two_pass:   if True, run Pass 1 (forward only), then Pass 2 (both sides)
    """
    def _p(years, amps, ba, tr):
        n = len(years)

        # --- PASS 1: Forward-only (causal) ---
        pass1 = []
        for i in range(n):
            # Back constraint (causal gate)
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            # Side 1: backward horizontal
            if i > 0 and h_cc != 0:
                delta_back = (amps[i-1] - ba) / ba
                h_back = ba * h_cc * delta_back * np.exp(-PHI)
            else:
                h_back = 0.0

            # Drain scale
            ds = 1.0
            if use_drain and use_wald and i > 0:
                rf = wald_rf(amps[i-1])
                ara_cycle = rf / (1 - rf)
                ds = ara_cycle / PHI

            pred = predict_point(years[i], ba, tr, acc_frac=sa,
                                 h_back=h_back, h_fwd=0.0,
                                 above_cc=above_cc,
                                 use_drain=use_drain, drain_scale=ds)
            pass1.append(pred)

        if not two_pass:
            return pass1

        # --- PASS 2+: Use Pass 1 estimates for forward neighbor ---
        current = list(pass1)
        for p in range(n_passes - 1):
            refined = []
            for i in range(n):
                sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

                # Side 1: backward horizontal (from OBSERVED data)
                if i > 0 and h_cc != 0:
                    delta_back = (amps[i-1] - ba) / ba
                    h_back = ba * h_cc * delta_back * np.exp(-PHI)
                else:
                    h_back = 0.0

                # Side 2: FORWARD horizontal (from previous pass estimates)
                if i < n - 1 and h_cc != 0:
                    # The next cycle's estimated amplitude from last pass
                    next_est = current[i + 1]
                    delta_fwd = (next_est - ba) / ba
                    # Forward neighbor bleeds BACK — its accumulation
                    # phase pulls energy from our release phase
                    h_fwd = ba * h_cc * delta_fwd * np.exp(-PHI)
                else:
                    h_fwd = 0.0

                ds = 1.0
                if use_drain and use_wald and i > 0:
                    rf = wald_rf(amps[i-1])
                    ara_cycle = rf / (1 - rf)
                    ds = ara_cycle / PHI

                pred = predict_point(years[i], ba, tr, acc_frac=sa,
                                     h_back=h_back, h_fwd=h_fwd,
                                     above_cc=above_cc,
                                     use_drain=use_drain, drain_scale=ds)
                refined.append(pred)
            current = refined

        return current

    return _p


# Reference: V5 static
def predict_v5_static(t, ba, tr):
    return predict_point(t, ba, tr)


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
    print("SCRIPT 218 — 4D LOCK: PIN THE MIDPOINT")
    print("=" * 70)
    print("""
  Locking the prediction from all 4 directions:
    BACK:  causal gate (prev cycle amplitude)
    SIDE1: backward horizontal (prev cycle residual)
    SIDE2: forward horizontal (2-pass: estimate then refine)
    BELOW: inner pulse at Schwabe singularity + ARA decay
    ABOVE: opposition at Gleissberg singularity (weak)
""")

    results = []

    # [1] V5 static reference
    print("[1/9] V5 static reference...")
    r = evaluate("V5 static", predict_v5_static)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [2] 1-pass: back + side1 + below (= 217 best, for comparison)
    print("\n[2/9] 1-pass: back+side1+below...")
    fn = mk_model(h_cc=INV_PHI_3, use_drain=True, use_wald=True)
    r = evaluate("1pass B+S1+below", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [3] 2-pass: back + BOTH sides + below (the key test)
    print("\n[3/9] 2-pass: back+S1+S2+below (h=1/phi3)...")
    fn = mk_model(h_cc=INV_PHI_3, two_pass=True, n_passes=2)
    r = evaluate("2pass both sides", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [4] 2-pass + drain + Wald
    print("\n[4/9] 2-pass + Wald drain...")
    fn = mk_model(h_cc=INV_PHI_3, two_pass=True, use_drain=True, use_wald=True)
    r = evaluate("2pass+Wald drain", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [5] 2-pass + above opposition (full 4D lock)
    print("\n[5/9] FULL 4D: 2-pass + above (cc=1/phi6)...")
    fn = mk_model(h_cc=INV_PHI_3, above_cc=INV_PHI**6, two_pass=True)
    r = evaluate("4D: h3+above6", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [6] Full 4D + Wald drain
    print("\n[6/9] FULL 4D + Wald drain...")
    fn = mk_model(h_cc=INV_PHI_3, above_cc=INV_PHI**6,
                   two_pass=True, use_drain=True, use_wald=True)
    r = evaluate("4D+Wald drain", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [7] 3-pass convergence test
    print("\n[7/9] 3-pass convergence...")
    fn = mk_model(h_cc=INV_PHI_3, two_pass=True, n_passes=3)
    r = evaluate("3pass converge", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [8] Weaker horizontal (1/phi4) 2-pass
    print("\n[8/9] 2-pass weaker horizontal (1/phi4)...")
    fn = mk_model(h_cc=INV_PHI_4, two_pass=True, use_drain=True, use_wald=True)
    r = evaluate("2pass h4+Wald", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [9] Full 4D with stronger above (1/phi4)
    print("\n[9/9] Full 4D stronger above (1/phi4)...")
    fn = mk_model(h_cc=INV_PHI_3, above_cc=INV_PHI_4,
                   two_pass=True, use_drain=True, use_wald=True)
    r = evaluate("4D above4+Wald", fn, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # =================================================================
    # REPORT
    # =================================================================
    all_sorted = sorted(results, key=lambda r: r['loo'])
    bl = all_sorted[0]
    bw = min(results, key=lambda r: abs(r['rr']))
    bs = max(results, key=lambda r: (r['sw'], -r['loo']))

    print(f"\n{'='*70}")
    print("ALL MODELS (sorted by LOO)")
    print(f"{'='*70}")
    print(f"\n  {'Model':<30s} {'LOO':>7s} {'%sine':>7s} {'Rise r':>7s} {'Split':>5s}")
    print(f"  {'-'*30} {'-'*7} {'-'*7} {'-'*7} {'-'*5}")
    for r in all_sorted:
        print(f"  {r['label']:<30s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['rr']:+7.3f} {r['sw']:2d}/7")

    print(f"\n  BEST LOO:      {bl['label']} ({bl['loo']:.2f})")
    print(f"  BEST WALDMEIER: {bw['label']} (r={bw['rr']:+.3f})")
    print(f"  BEST SPLITS:   {bs['label']} ({bs['sw']}/7)")

    # Temporal splits
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS")
    print(f"{'='*70}")
    shown = set()
    for r in [bl, bs, bw]:
        if r['label'] in shown: continue
        shown.add(r['label'])
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            mg = sm - pm if w == "phi" else pm - sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: "
                  f"phi={pm:.1f}  sine={sm:.1f}  -> {w} ({mg:.1f})")

    # Dalton
    print(f"\n{'='*70}")
    print("DALTON (Cycles 5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    shown2 = set()
    for r in all_sorted[:5] + [bw, bs]:
        if r['label'] in shown2: continue
        shown2.add(r['label'])
        d = [4, 5, 6]
        dm = np.mean([abs(r['pf'][i] - peak_amps[i]) for i in d])
        print(f"  {r['label']:<30s} Dalton MAE={dm:.1f}  "
              f"(C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f})")

    # Per-cycle
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {bl['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'RF':>6s}")
    for i, c in enumerate(cycle_nums):
        p = bl['pf'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} "
              f"{p - peak_amps[i]:+7.1f} {rise_fracs[i]:6.3f}")

    print(f"\n{'='*70}")
    print("ALL-TIME SCOREBOARD")
    print(f"{'='*70}")
    print(f"""
  203b single gate:        LOO=37.66, splits=1/7, rise r=+0.767
  207 V1 causal:           LOO=38.82, splits=3/7
  210 V5 causal+drain:     LOO=36.62, splits=2/7
  211 V4d Wald+drain:      LOO=36.46, splits=0/7
  214 V4 deep caus:        rise r=+0.583
  216 V5 inner pulse:      LOO=35.28, splits=4/7
  217 V5+H:dlt+Wald:       LOO=35.26, splits=4/7

  This script (4D lock):
    Best LOO:    {bl['label']}: {bl['loo']:.2f}, splits={bl['sw']}/7
    Best Wald:   {bw['label']}: r={bw['rr']:+.3f}
    Best splits: {bs['label']}: {bs['sw']}/7

  Total time: {time.time()-t0:.0f}s
""")
