#!/usr/bin/env python3
"""
Script 224b — Wobble on Solar Champion

Dylan's insight: oscillate the direction of travel slightly.
At each cascade collision, a fraction bounces backward (j → j-1).
This is the beeswax corridor wall-bounce effect.

On the cardiac model, wobble=φ gave best DFA (α=0.848).
Does it improve the solar sunspot LOO?

Base: 223o all-three (phase-diff + log tension + asymmetric Hale, LOO=33.03)
"""

import numpy as np
import warnings, time
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9
LOG2 = np.log(2)

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

PERIODS = [PHI**11, PHI**9, PHI**6, PHI**4]

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


def mk_wobble_model(wobble=0.0, h_cc=INV_PHI_3):
    """
    All-three champion (223o) + backward coupling wobble.

    Horizontal: phase-diff collision + log1p tension + wobble
    Vertical: asymmetric Hale
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

            # First pass: compute eps for each level (forward + backward)
            eps_vals = [INV_PHI_4 * gate] * len(PERIODS)

            for j in range(len(PERIODS)):
                # Phase-difference collision
                if j > 0:
                    phase_diff = phases[j-1] - phases[j]
                    collision = -np.cos(phase_diff)
                    eps_vals[j] *= (1 + collision * INV_PHI)

                    # Wobble: backward coupling
                    if wobble > 0:
                        eps_vals[j-1] *= (1 + wobble * collision * INV_PHI)

                # Log1p tension
                tens = -sin_vals[j]
                log_tens = np.sign(tens) * np.log1p(abs(tens)) / LOG2
                if log_tens > 0: eps_vals[j] *= (1 + 0.5*log_tens*(PHI-1))
                else:            eps_vals[j] *= (1 + 0.5*log_tens*(1-INV_PHI))

            amp = ba
            for j in range(len(PERIODS)):
                w = cos_vals[j]
                amp *= (1 + eps_vals[j] * w)

            amp += ba * INV_PHI_9 * np.cos(gp)
            sp = 2*np.pi*(t-tr)/SCHWABE
            amp += ba * INV_PHI_3 * sing_pulse_decay(sp, PHI) * np.cos(sp)

            # Asymmetric Hale
            if i > 0 and h_cc != 0:
                prev_dev = (amps[i-1] - ba) / ba
                grief_mult = PHI if prev_dev < 0 else 1.0
                amp += ba * (-h_cc) * prev_dev * np.exp(-PHI) * grief_mult

            preds.append(amp)
        return preds
    return _p


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

    sw = 0
    for nt in [5, 8, 10, 12, 15, 18, 20]:
        if nt >= N: continue
        tm = np.zeros(N, dtype=bool); tm[:nt] = True
        bs, ts, _ = fit_q(fn, tm, peak_years, peak_amps)
        tp = fn(peak_years, peak_amps, bs, ts)[nt:]
        ta = peak_amps[nt:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:nt].mean()), ta)
        if pm < sm: sw += 1

    return {'label': label, 'loo': loo, 'sine': sl, 'imp': (loo/sl-1)*100,
            'rr': rr, 'sw': sw, 'pf': pf}


if __name__ == '__main__':
    t0 = time.time()
    print("="*70)
    print("SCRIPT 224b — WOBBLE ON SOLAR CHAMPION")
    print("="*70)
    print(f"""
  Base: 223o all-three (phase-diff + log + asymHale), LOO=33.03
  Adding backward coupling (wobble) at each cascade collision.
  Wobble=w means backward force = w × forward collision.
""")

    wobble_vals = [
        ('w=0 (base)',   0.0),
        ('w=1/φ',       INV_PHI),
        ('w=φ',         PHI),
        ('w=φ²',        PHI**2),
    ]

    results = []
    for label, w in wobble_vals:
        fn = mk_wobble_model(wobble=w)
        r = evaluate(label, fn)
        results.append(r)
        print(f"  {label:<15s}  LOO={r['loo']:.2f}  r={r['rr']:+.3f}  s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    results.sort(key=lambda r: r['loo'])
    best = results[0]

    print(f"\n{'='*70}")
    print("RESULTS (sorted by LOO)")
    print(f"{'='*70}")
    print(f"\n  {'Model':<15s} {'LOO':>7s} {'%sine':>7s} {'Rise r':>7s} {'Split':>5s}")
    print(f"  {'-'*15} {'-'*7} {'-'*7} {'-'*7} {'-'*5}")
    for r in results:
        print(f"  {r['label']:<15s} {r['loo']:7.2f} {r['imp']:+6.1f}% "
              f"{r['rr']:+7.3f} {r['sw']:2d}/7")

    print(f"\n{'='*70}")
    print("SCOREBOARD")
    print(f"{'='*70}")
    print(f"  223o All three (no wobble):  LOO=33.03, 4/7, r=+0.656")
    print(f"  223p Blended α=1/φ:          LOO=33.60, 6/7, r=+0.683")
    print(f"  223d Mirror champion:        LOO=33.25, 5/7, r=+0.702")
    print(f"  ---")
    print(f"  This best: {best['label']}: LOO={best['loo']:.2f}, {best['sw']}/7, r={best['rr']:+.3f}")
    print(f"\n  Time: {time.time()-t0:.0f}s")
