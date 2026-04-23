#!/usr/bin/env python3
"""
Script 219 — Full Formula Horizontal Coupling

DYLAN'S INSIGHT:
  "We need to apply the whole formula to the side ones too."

  The horizontal neighbors aren't just passing raw amplitude.
  They're ARA systems. Their energy transforms through the SAME
  φ-cascade before reaching the current cycle.

  Previous cycle's contribution at time t =
    cascade(t, ba, tr_prev) × coupling_strength

  The previous cycle's ARA FIELD extends forward in time.
  What we receive horizontally is the CASCADE evaluated from
  the neighbor's reference point — their φ-wave field, not
  just their peak amplitude.

  Similarly, the next cycle's field extends backward.

ARCHITECTURE:
  For cycle i at peak time t_i:
    BASE:       cascade(t_i, ba, tr)           — Sun's own field
    BELOW:      inner pulse + ARA decay         — vertical from below
    SIDE_BACK:  cascade(t_i, ba, tr_prev) × cc — prev cycle's field HERE
    SIDE_FWD:   cascade(t_i, ba, tr_next) × cc — next cycle's field HERE
    ABOVE:      opposition pulse                — vertical from above

  tr_prev/tr_next = reference points shifted by one cycle period.
  The key: the SAME formula generates the horizontal contribution,
  just evaluated from the neighbor's temporal origin.

TOP 3 MODELS ONLY (per Dylan's feedback)
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
MEAN_DUR = durations.mean()  # ~11.1yr ≈ Schwabe
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
# CORE CASCADE — evaluable from ANY reference point
# =================================================================

def cascade_raw(t, ba, tr, af=SUN_ACC):
    """
    The full φ-cascade evaluated at time t with reference tr.
    This is the ARA field at point t as seen from origin tr.
    """
    gp = 2*np.pi*(t-tr)/GLEISSBERG
    gate = sawtooth_valve(gp, af)
    amp = ba
    for per in [PHI**11, PHI**9, PHI**6, PHI**4]:
        ph = 2*np.pi*(t-tr)/per
        w = np.cos(ph); tens = -np.sin(ph)
        eps = INV_PHI_4 * gate
        if tens > 0: eps *= (1 + 0.5*tens*(PHI-1))
        else: eps *= (1 + 0.5*tens*(1-INV_PHI))
        amp *= (1 + eps*w)
    amp += ba * INV_PHI_9 * np.cos(gp)
    return amp


def cascade_with_inner(t, ba, tr, af=SUN_ACC):
    """Cascade + inner pulse (V5 architecture)."""
    amp = cascade_raw(t, ba, tr, af)
    sp = 2*np.pi*(t-tr)/SCHWABE
    amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)
    return amp


# =================================================================
# FULL HORIZONTAL MODEL
# =================================================================

def mk_full_horizontal(h_cc=INV_PHI_3, use_drain=False, use_wald=False):
    """
    Each cycle's prediction = its own cascade
      + h_cc × (previous cycle's cascade evaluated HERE)
      + inner pulse

    The previous cycle's cascade field at the current time point
    is computed by evaluating the SAME formula with a shifted
    reference point (tr shifted back by one cycle duration).
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            # Causal gate from previous cycle
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            # OWN cascade at this time
            own = cascade_with_inner(t, ba, tr, af=sa)

            # HORIZONTAL: previous cycle's CASCADE FIELD evaluated at t
            # The neighbor's reference point is shifted by ~one Schwabe period
            # We use the actual duration between cycles as the shift
            if i > 0 and h_cc != 0:
                # Previous cycle peaked at years[i-1]
                # Its cascade field at time t = cascade(t, ba, tr_shifted)
                # where tr_shifted puts the previous cycle at its own origin
                dt = t - years[i-1]  # time since prev peak
                # The previous cycle's field decays with ARA rate
                # Evaluate cascade from prev's perspective
                tr_prev = tr - (years[i] - years[i-1])
                prev_field = cascade_with_inner(t, ba, tr_prev, af=sa)
                # The horizontal contribution is the DIFFERENCE between
                # what the neighbor's field says and what our own says
                # scaled by coupling and ARA decay over the gap
                gap_decay = np.exp(-PHI * dt / SCHWABE)
                h_contrib = (prev_field - own) * h_cc * gap_decay
                own += h_contrib

            # Drain
            if use_drain:
                gp = 2*np.pi*(t-tr)/GLEISSBERG
                ds = 1.0
                if use_wald and i > 0:
                    rf = wald_rf(amps[i-1])
                    ds = (rf/(1-rf))/PHI
                own -= INV_PHI_9 * own * (own/ba) * ds * abs(np.cos(gp))

            preds.append(own)
        return preds
    return _p


def mk_full_horizontal_v2(h_cc=INV_PHI_3, use_drain=False, use_wald=False):
    """
    V2: Previous cycle's cascade is evaluated with its OWN acc_frac
    (from the cycle before it), not the current cycle's.
    Each horizontal neighbor brings its own ARA character.
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            own = cascade_with_inner(t, ba, tr, af=sa)

            if i > 0 and h_cc != 0:
                # Previous cycle's OWN acc_frac (from the cycle before it)
                sa_prev = SUN_ACC if i <= 1 else ara_to_acc(amps[i-2] / ba)
                tr_prev = tr - (years[i] - years[i-1])
                prev_field = cascade_with_inner(t, ba, tr_prev, af=sa_prev)
                dt = t - years[i-1]
                gap_decay = np.exp(-PHI * dt / SCHWABE)
                own += (prev_field - own) * h_cc * gap_decay

            if use_drain:
                gp = 2*np.pi*(t-tr)/GLEISSBERG
                ds = 1.0
                if use_wald and i > 0:
                    rf = wald_rf(amps[i-1])
                    ds = (rf/(1-rf))/PHI
                own -= INV_PHI_9 * own * (own/ba) * ds * abs(np.cos(gp))

            preds.append(own)
        return preds
    return _p


def mk_full_horizontal_v3(h_cc=INV_PHI_3, use_drain=False, use_wald=False):
    """
    V3: Additive, not differential. The previous cycle's field
    ADDS to the current, scaled down. No subtraction of own field.
    Like interference: two wave fields superposing.
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)
            own = cascade_with_inner(t, ba, tr, af=sa)

            if i > 0 and h_cc != 0:
                sa_prev = SUN_ACC if i <= 1 else ara_to_acc(amps[i-2] / ba)
                tr_prev = tr - (years[i] - years[i-1])
                prev_field = cascade_with_inner(t, ba, tr_prev, af=sa_prev)
                dt = t - years[i-1]
                gap_decay = np.exp(-PHI * dt / SCHWABE)
                # Additive: prev field contributes ON TOP of own
                # But centered on ba so we don't double-count the base
                own += (prev_field - ba) * h_cc * gap_decay

            if use_drain:
                gp = 2*np.pi*(t-tr)/GLEISSBERG
                ds = 1.0
                if use_wald and i > 0:
                    rf = wald_rf(amps[i-1])
                    ds = (rf/(1-rf))/PHI
                own -= INV_PHI_9 * own * (own/ba) * ds * abs(np.cos(gp))

            preds.append(own)
        return preds
    return _p


# Reference
def predict_v5_static(t, ba, tr):
    return cascade_with_inner(t, ba, tr)


# =================================================================
# FITTING + EVAL
# =================================================================

def fit_s(fn, ty, ta):
    best, bba, btr = 1e9, 0, 0
    for tr in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(ta)*0.6, np.mean(ta)*1.4, 40):
            m = mae([fn(t, ba, tr) for t in ty], ta)
            if m < best: best, bba, btr = m, ba, tr
    return bba, btr, best

def fit_q(fn, mask, ay, aa):
    best, bba, btr = 1e9, 0, 0
    idx = np.where(mask)[0]; ta = aa[mask]
    for tr in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(ta)*0.6, np.mean(ta)*1.4, 40):
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
        pm, sm = mae(tp, ta), mae(np.full(len(ta), peak_amps[:nt].mean()), ta)
        w = "phi" if pm < sm else "sine"
        if pm < sm: sw += 1
        sd.append((nt, N-nt, pm, sm, w))

    return {'label': label, 'loo': loo, 'sine': sl,
            'imp': (loo/sl-1)*100, 'wins': int(np.sum(pe < se)),
            'rr': rr, 'sw': sw, 'sd': sd, 'pf': pf, 'ba': bf, 'tr': tf}


if __name__ == '__main__':
    t0 = time.time()
    print("=" * 70)
    print("SCRIPT 219 — FULL FORMULA HORIZONTAL COUPLING")
    print("=" * 70)
    print("""
  Previous cycle's CASCADE FIELD evaluated at current time point.
  Not raw amplitude — the full φ-formula from the neighbor's origin.
""")

    results = []

    # [1] V5 static reference
    print("\n[1/4] V5 static reference...")
    r = evaluate("V5 static", predict_v5_static)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [2] V1: differential (prev_field - own) × coupling × decay
    print("\n[2/4] V1: differential horizontal...")
    r = evaluate("V1 diff horiz", mk_full_horizontal(h_cc=INV_PHI_3), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [3] V2: prev uses its OWN acc_frac
    print("\n[3/4] V2: own-gate horizontal...")
    r = evaluate("V2 own-gate", mk_full_horizontal_v2(h_cc=INV_PHI_3), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [4] V3: additive interference (prev_field - ba) on top
    print("\n[4/4] V3: additive interference...")
    r = evaluate("V3 additive", mk_full_horizontal_v3(h_cc=INV_PHI_3), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # Report
    all_sorted = sorted(results, key=lambda r: r['loo'])
    bl = all_sorted[0]
    bw = min(results, key=lambda r: abs(r['rr']))
    bs = max(results, key=lambda r: (r['sw'], -r['loo']))

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
    for r in all_sorted[:3]:
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            mg = sm-pm if w=="phi" else pm-sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: phi={pm:.1f} sine={sm:.1f} -> {w} ({mg:.1f})")

    # Dalton
    print(f"\n{'='*70}")
    print("DALTON (C5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    for r in all_sorted:
        d = [4, 5, 6]
        dm = np.mean([abs(r['pf'][i]-peak_amps[i]) for i in d])
        print(f"  {r['label']:<25s} MAE={dm:.1f} (C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f})")

    # Per-cycle for best non-static
    best_new = [r for r in all_sorted if 'static' not in r['label']]
    if best_new:
        bn = best_new[0]
        print(f"\n{'='*70}")
        print(f"PER-CYCLE — {bn['label']}")
        print(f"{'='*70}")
        print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s}")
        for i, c in enumerate(cycle_nums):
            p = bn['pf'][i]
            print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} {p-peak_amps[i]:+7.1f}")

    print(f"\n  SCOREBOARD:")
    print(f"  216 V5 inner pulse:  LOO=35.28, 4/7, r=+0.690")
    print(f"  217 V5+H:dlt+Wald:  LOO=35.26, 4/7, r=+0.672")
    print(f"  This: {bl['label']}: LOO={bl['loo']:.2f}, {bl['sw']}/7, r={bl['rr']:+.3f}")
    print(f"\n  Time: {time.time()-t0:.0f}s")
