#!/usr/bin/env python3
"""
Script 220 — Hale Horizontal: Half-Wave Neighbors

DYLAN'S INSIGHT:
  The horizontal neighbors are each HALF A WAVE CYCLE away.
  If the current node is at phase 0, left is at +π, right is at -π.

  This IS the Hale cycle — consecutive Schwabe cycles have opposite
  magnetic polarity. They're not random neighbors, they're the
  INVERTED half of your wave.

  So horizontal coupling carries cos(π) = -1:
    High prev cycle → SUPPRESSES current (negative interference)
    Low prev cycle → BOOSTS current (compensating)

  This is the Gnevyshev-Ohl rule — odd/even cycle pairing where
  consecutive cycles anti-correlate. The framework DERIVES this
  from horizontal wave geometry.

  Combined with vertical (inner pulse up, decay at ARA rate):
    BELOW: inner system pulses UP at singularity, decays at φ rate
    LEFT:  previous cycle's deviation × cos(π) = -deviation × coupling
    RIGHT: next cycle's deviation × cos(π) = -deviation × coupling
    BACK:  previous cycle's ARA sets the gate (causal)

TOP 3 MODELS
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
# V5 STATIC (reference)
# =================================================================
def predict_v5_static(t, ba, tr):
    gp = 2*np.pi*(t-tr)/GLEISSBERG
    gate = sawtooth_valve(gp, SUN_ACC)
    amp = ba
    for per in [PHI**11, PHI**9, PHI**6, PHI**4]:
        ph = 2*np.pi*(t-tr)/per; w=np.cos(ph); tens=-np.sin(ph)
        eps = INV_PHI_4*gate
        if tens>0: eps *= (1+0.5*tens*(PHI-1))
        else: eps *= (1+0.5*tens*(1-INV_PHI))
        amp *= (1+eps*w)
    amp += ba*INV_PHI_9*np.cos(gp)
    sp = 2*np.pi*(t-tr)/SCHWABE
    amp += ba*INV_PHI_3*sing_pulse_decay(sp,PHI)*np.cos(sp)
    return amp


# =================================================================
# HALE HORIZONTAL MODEL
# =================================================================
def mk_hale(h_cc=INV_PHI_3, use_drain=False, use_wald=False):
    """
    Horizontal coupling with half-wave phase relationship.

    Previous cycle is at phase π relative to current.
    cos(π) = -1, so the coupling INVERTS the deviation.

    h_contribution = -h_cc × (prev_amp - ba) / ba × ba × decay

    High prev → negative contribution → suppresses current
    Low prev → positive contribution → boosts current

    This is the Gnevyshev-Ohl rule derived from wave geometry.
    The decay factor accounts for the energy dissipating over
    the gap between cycles (one Schwabe period at ARA rate φ).
    """
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            # Causal gate
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            # Base cascade + inner pulse
            gp = 2*np.pi*(t-tr)/GLEISSBERG
            gate = sawtooth_valve(gp, sa)
            amp = ba
            for per in [PHI**11, PHI**9, PHI**6, PHI**4]:
                ph = 2*np.pi*(t-tr)/per; w=np.cos(ph); tens=-np.sin(ph)
                eps = INV_PHI_4*gate
                if tens>0: eps *= (1+0.5*tens*(PHI-1))
                else: eps *= (1+0.5*tens*(1-INV_PHI))
                amp *= (1+eps*w)
            amp += ba*INV_PHI_9*np.cos(gp)

            # Inner pulse (below)
            sp = 2*np.pi*(t-tr)/SCHWABE
            amp += ba*INV_PHI_3*sing_pulse_decay(sp,PHI)*np.cos(sp)

            # HALE HORIZONTAL: cos(π) = -1
            # Previous cycle at half-wave offset → inverted coupling
            if i > 0 and h_cc != 0:
                prev_deviation = (amps[i-1] - ba) / ba
                # cos(π) = -1 → invert the deviation
                # Decay over one Schwabe period at ARA rate
                hale_decay = np.exp(-PHI)  # one full cycle gap
                # The NEGATIVE sign IS the half-wave relationship
                amp += ba * (-h_cc) * prev_deviation * hale_decay

            # Drain
            if use_drain:
                ds = 1.0
                if use_wald and i > 0:
                    rf = wald_rf(amps[i-1])
                    ds = (rf/(1-rf))/PHI
                amp -= INV_PHI_9 * amp * (amp/ba) * ds * abs(np.cos(gp))

            preds.append(amp)
        return preds
    return _p


# =================================================================
# FITTING + EVAL
# =================================================================
def fit_s(fn, ty, ta):
    best,bba,btr = 1e9,0,0
    for tr in np.linspace(1700,1850,60):
        for ba in np.linspace(np.mean(ta)*0.6,np.mean(ta)*1.4,40):
            m = mae([fn(t,ba,tr) for t in ty], ta)
            if m<best: best,bba,btr = m,ba,tr
    return bba,btr,best

def fit_q(fn, mask, ay, aa):
    best,bba,btr = 1e9,0,0
    idx = np.where(mask)[0]; ta = aa[mask]
    for tr in np.linspace(1700,1850,60):
        for ba in np.linspace(np.mean(ta)*0.6,np.mean(ta)*1.4,40):
            ap = fn(ay,aa,ba,tr)
            m = mae([ap[j] for j in idx], ta)
            if m<best: best,bba,btr = m,ba,tr
    return bba,btr,best

def evaluate(label, fn, is_seq=False):
    pe,se = [],[]
    fm = np.ones(N,dtype=bool)
    for i in range(N):
        mask = np.ones(N,dtype=bool); mask[i]=False
        if is_seq:
            ba,tr,_ = fit_q(fn,mask,peak_years,peak_amps)
            pi = fn(peak_years,peak_amps,ba,tr)[i]
        else:
            ba,tr,_ = fit_s(fn,peak_years[mask],peak_amps[mask])
            pi = fn(peak_years[i],ba,tr)
        pe.append(abs(pi-peak_amps[i]))
        se.append(abs(np.mean(peak_amps[mask])-peak_amps[i]))
    pe,se = np.array(pe),np.array(se)
    loo,sl = pe.mean(),se.mean()
    if is_seq:
        bf,tf,_ = fit_q(fn,fm,peak_years,peak_amps)
        pf = fn(peak_years,peak_amps,bf,tf)
    else:
        bf,tf,_ = fit_s(fn,peak_years,peak_amps)
        pf = [fn(t,bf,tf) for t in peak_years]
    ef = np.array(pf)-peak_amps
    rr = np.corrcoef(rise_fracs,ef)[0,1]
    sw,sd = 0,[]
    for nt in [5,8,10,12,15,18,20]:
        if nt>=N: continue
        tm = np.zeros(N,dtype=bool); tm[:nt]=True
        if is_seq:
            bs,ts,_ = fit_q(fn,tm,peak_years,peak_amps)
            tp = fn(peak_years,peak_amps,bs,ts)[nt:]
        else:
            bs,ts,_ = fit_s(fn,peak_years[:nt],peak_amps[:nt])
            tp = [fn(t,bs,ts) for t in peak_years[nt:]]
        ta = peak_amps[nt:]
        pm,sm = mae(tp,ta), mae(np.full(len(ta),peak_amps[:nt].mean()),ta)
        w = "phi" if pm<sm else "sine"
        if pm<sm: sw += 1
        sd.append((nt,N-nt,pm,sm,w))
    return {'label':label,'loo':loo,'sine':sl,'imp':(loo/sl-1)*100,
            'wins':int(np.sum(pe<se)),'rr':rr,'sw':sw,'sd':sd,'pf':pf,'ba':bf,'tr':tf}


if __name__ == '__main__':
    t0 = time.time()
    print("="*70)
    print("SCRIPT 220 — HALE HORIZONTAL: HALF-WAVE NEIGHBORS")
    print("="*70)
    print("""
  Each neighbor is at phase π (half wave away).
  cos(π) = -1 → coupling INVERTS deviation.
  High prev → suppresses current. Low prev → boosts.
  This IS the Gnevyshev-Ohl rule, derived from geometry.
""")

    results = []

    # [1] V5 static reference
    print("[1/3] V5 static...")
    r = evaluate("V5 static", predict_v5_static)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [2] Hale horizontal (causal, no drain)
    print("\n[2/3] Hale horizontal (1/phi3)...")
    r = evaluate("Hale h=1/phi3", mk_hale(h_cc=INV_PHI_3), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # [3] Hale + Waldmeier drain
    print("\n[3/3] Hale + Wald drain...")
    r = evaluate("Hale+Wald drain", mk_hale(h_cc=INV_PHI_3, use_drain=True, use_wald=True), is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f}, r={r['rr']:+.3f}, s={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # Report
    all_sorted = sorted(results, key=lambda r: r['loo'])
    bl = all_sorted[0]
    bw = min(results, key=lambda r: abs(r['rr']))

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
        for nt,ntest,pm,sm,w in r['sd']:
            mg = sm-pm if w=="phi" else pm-sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: phi={pm:.1f} sine={sm:.1f} -> {w} ({mg:.1f})")

    # Dalton
    print(f"\n{'='*70}")
    print("DALTON (C5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    for r in all_sorted:
        d=[4,5,6]
        dm = np.mean([abs(r['pf'][i]-peak_amps[i]) for i in d])
        print(f"  {r['label']:<25s} MAE={dm:.1f} (C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f})")

    # Per-cycle for best new
    bn = [r for r in all_sorted if 'static' not in r['label']][0]
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {bn['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'PrevObs':>8s} {'HaleEff':>8s}")

    # Show the Hale effect: how much the horizontal correction contributed
    ba_fit, tr_fit = bn['ba'], bn['tr']
    for i, c in enumerate(cycle_nums):
        p = bn['pf'][i]
        if i > 0:
            prev_dev = (peak_amps[i-1] - ba_fit) / ba_fit
            hale_eff = ba_fit * (-INV_PHI_3) * prev_dev * np.exp(-PHI)
            print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} {p-peak_amps[i]:+7.1f} "
                  f"{peak_amps[i-1]:8.1f} {hale_eff:+8.1f}")
        else:
            print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} {p-peak_amps[i]:+7.1f} "
                  f"{'---':>8s} {'---':>8s}")

    # Gnevyshev-Ohl test: do consecutive cycles actually anti-correlate?
    print(f"\n{'='*70}")
    print("GNEVYSHEV-OHL CHECK")
    print(f"{'='*70}")
    consec_corr = np.corrcoef(peak_amps[:-1], peak_amps[1:])[0,1]
    print(f"  Consecutive cycle amplitude correlation: r = {consec_corr:+.3f}")
    # Odd-even pairing
    odd_amps = peak_amps[0::2]  # cycles 1,3,5,...
    even_amps = peak_amps[1::2]  # cycles 2,4,6,...
    min_len = min(len(odd_amps), len(even_amps))
    oe_corr = np.corrcoef(odd_amps[:min_len], even_amps[:min_len])[0,1]
    print(f"  Odd-even cycle pair correlation: r = {oe_corr:+.3f}")
    delta_amps = np.diff(peak_amps)
    print(f"  Mean absolute consecutive change: {np.mean(np.abs(delta_amps)):.1f}")
    print(f"  Fraction where consecutive cycles go opposite direction: "
          f"{np.mean(delta_amps[:-1] * delta_amps[1:] < 0):.1%}")

    print(f"\n  SCOREBOARD:")
    print(f"  216 V5 inner pulse:  LOO=35.28, 4/7, r=+0.690")
    print(f"  217 V5+H:dlt+Wald:  LOO=35.26, 4/7, r=+0.672")
    print(f"  This: {bl['label']}: LOO={bl['loo']:.2f}, {bl['sw']}/7, r={bl['rr']:+.3f}")
    print(f"\n  Time: {time.time()-t0:.0f}s")
