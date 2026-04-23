#!/usr/bin/env python3
"""
Script 217b — Combined Champion (lean: 10 key models only)
V5 inner pulse + causal + drain + horizontal coupling
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
# V5 STATIC (reference — from 216)
# =================================================================
def predict_v5_static(t, ba, tr):
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
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    pulse = sing_pulse_decay(schwabe_phase, PHI)
    amp += ba * INV_PHI_3 * pulse * np.cos(schwabe_phase)
    return amp


# =================================================================
# COMBINED MODEL: V5 + causal + drain + horizontal
# =================================================================
def mk_combined(use_drain=False, use_wald=False,
                h_mode=None, h_cc=0.0):
    """
    Full combined model.
    h_mode: None, 'residual', 'delta'
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            # Causal gate
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

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

            # Vertical: inner pulse (φ⁵ at Schwabe singularities)
            schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
            pulse = sing_pulse_decay(schwabe_phase, PHI)
            amp += ba * INV_PHI_3 * pulse * np.cos(schwabe_phase)

            # Horizontal coupling
            if h_mode and i > 0:
                prev_amp = amps[i - 1]
                if h_mode == 'residual':
                    # Previous cycle's undissipated energy
                    residual = prev_amp * np.exp(-PHI)
                    baseline_residual = ba * np.exp(-PHI)
                    amp += (residual - baseline_residual) * h_cc
                elif h_mode == 'delta':
                    # Amplitude deviation from base, ARA-decayed
                    delta = (prev_amp - ba) / ba
                    amp += ba * h_cc * delta * np.exp(-PHI)

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


if __name__ == '__main__':
    t0 = time.time()
    print("=" * 70)
    print("SCRIPT 217b — COMBINED CHAMPION (LEAN)")
    print("=" * 70)

    results = []

    # 1. V5 static reference
    print("\n[1/10] V5 static reference...")
    r = evaluate("V5 static", predict_v5_static)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 2. V5 + causal (no drain, no horizontal)
    print("\n[2/10] V5 causal...")
    r = evaluate("V5 causal", mk_combined(), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 3. V5 + causal + drain
    print("\n[3/10] V5 causal+drain...")
    r = evaluate("V5 causal+drain", mk_combined(use_drain=True), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 4. V5 + causal + Waldmeier drain
    print("\n[4/10] V5 causal+Wald drain...")
    r = evaluate("V5 caus+Wald drain", mk_combined(use_drain=True, use_wald=True), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 5. V5 + causal + horizontal residual 1/φ³
    print("\n[5/10] V5 causal + H:residual 1/phi3...")
    r = evaluate("V5+H:res 1/phi3", mk_combined(h_mode='residual', h_cc=INV_PHI_3), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 6. V5 + causal + horizontal residual 1/φ⁴
    print("\n[6/10] V5 causal + H:residual 1/phi4...")
    r = evaluate("V5+H:res 1/phi4", mk_combined(h_mode='residual', h_cc=INV_PHI_4), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 7. V5 + causal + horizontal delta 1/φ³
    print("\n[7/10] V5 causal + H:delta 1/phi3...")
    r = evaluate("V5+H:dlt 1/phi3", mk_combined(h_mode='delta', h_cc=INV_PHI_3), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 8. V5 + causal + H:residual + drain
    print("\n[8/10] V5+H:res 1/phi3 + drain...")
    r = evaluate("V5+H:res+drain", mk_combined(h_mode='residual', h_cc=INV_PHI_3, use_drain=True), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 9. V5 + causal + H:delta + Wald drain
    print("\n[9/10] V5+H:dlt 1/phi3 + Wald drain...")
    r = evaluate("V5+H:dlt+Wald", mk_combined(h_mode='delta', h_cc=INV_PHI_3, use_drain=True, use_wald=True), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # 10. V5 + causal + H:residual 1/phi4 + Wald drain (kitchen sink)
    print("\n[10/10] V5+H:res 1/phi4 + Wald drain...")
    r = evaluate("V5+H:res4+Wald", mk_combined(h_mode='residual', h_cc=INV_PHI_4, use_drain=True, use_wald=True), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, rise r={r['rr']:+.3f}, splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

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
    print("CROSS-REFERENCE")
    print(f"{'='*70}")
    print(f"""
  203b single gate:        LOO=37.66, splits=1/7, rise r=+0.767
  207 V1 causal:           LOO=38.82, splits=3/7
  210 V5 causal+drain:     LOO=36.62, splits=2/7
  211 V4d Wald+drain:      LOO=36.46, splits=0/7
  214 V4 deep caus:        rise r=+0.583
  216 V5 inner pulse:      LOO=35.28, splits=4/7 <- PREV CHAMPION

  This script:
    Best LOO:    {bl['label']}: {bl['loo']:.2f}, splits={bl['sw']}/7
    Best Wald:   {bw['label']}: r={bw['rr']:+.3f}
    Best splits: {bs['label']}: {bs['sw']}/7

  Total time: {time.time()-t0:.0f}s
""")
