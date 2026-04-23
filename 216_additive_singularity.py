#!/usr/bin/env python3
"""
Script 216 — Additive Singularity-Gated Coupling with ARA Decay

LEARNING FROM 215:
  Splitting the 4-period cascade into levels killed it (LOO 61-65 vs 37.66).
  Keep 203b cascade intact, add corrections on top.

DYLAN'S INSIGHT:
  Energy arrives at the singularity point, but then it doesn't vanish —
  it DISSIPATES over the decay rate of the system it entered.

  So the pulse shape is ASYMMETRIC:
    - Sharp onset at singularity (cycle boundary / trough)
    - Exponential decay following the RECEIVING system's ARA release rate
    - At cycle_pos=0: pulse=1.0
    - Decays as exp(-cycle_pos * rate) where rate ~ ARA of receiving system

  For inner→Sun: energy enters at Schwabe trough, decays at Sun's ARA rate
  For above→Sun: energy enters at Gleissberg trough, decays at Sun's ARA rate

  The Sun's ARA ≈ φ, so the decay constant is φ.
  After 1/φ of the cycle (~38.2%), energy has decayed to exp(-1) ≈ 37%.
  After the full accumulation phase (61.8%), decayed to exp(-φ×0.618) = exp(-1) ≈ 37%.
  By the end of the cycle: exp(-φ) ≈ 19%.

ARCHITECTURE:
  Base: 203b cascade [φ¹¹, φ⁹, φ⁶, φ⁴] — intact, continuous
  +Inner: φ⁵ correction, fires at Schwabe troughs, decays at Sun ARA rate
  +Above: φ¹³ correction, fires at Gleissberg troughs, decays at Sun ARA rate
         (OPPOSING — destructive interference from above)

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

SUN_ACC = PHI / (PHI + 1)  # 0.618


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
# SINGULARITY PULSE WITH ARA DECAY
# =================================================================

def singularity_pulse_symmetric(phase, width_param):
    """Original symmetric Gaussian — for comparison."""
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    dist = min(cycle_pos, 1 - cycle_pos)
    return np.exp(-width_param * (dist * 2 * np.pi) ** 2)


def singularity_pulse_ara_decay(phase, decay_rate):
    """
    Asymmetric pulse: fires at singularity (phase=0), decays at ARA rate.

    At cycle_pos = 0:       pulse = 1.0 (energy just arrived)
    At cycle_pos = 1/φ:     pulse = exp(-1) ≈ 0.37 (one ARA decay)
    At cycle_pos = 1.0:     pulse = exp(-decay_rate) (end of cycle)

    decay_rate = φ means:
      - 38.2% through cycle → 37% remaining
      - 61.8% through (acc/release boundary) → 13.5% remaining
      - 100% through → 19.4% remaining

    The energy dissipates as it propagates through the receiving system.
    """
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    return np.exp(-decay_rate * cycle_pos)


def singularity_pulse_ara_sawtooth(phase, acc_frac):
    """
    Pulse shape follows the INVERSE of the receiving system's ARA sawtooth.

    Energy arrives at singularity → absorbed during accumulation → released.
    The pulse shape IS the ARA cycle of the receiving system, inverted:
      - Strongest at start (singularity = beginning of new cycle)
      - Decays through accumulation phase
      - Nearly gone by release phase

    This is literally the energy dissipating through the system's own dynamics.
    """
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    acc_frac = max(0.15, min(0.85, acc_frac))

    if cycle_pos < acc_frac:
        # During accumulation: energy is being absorbed, linear decay
        return 1.0 - (cycle_pos / acc_frac)
    else:
        # During release: energy already absorbed, exponential tail
        release_pos = (cycle_pos - acc_frac) / (1 - acc_frac)
        return np.exp(-PHI * release_pos) * INV_PHI  # residual decay


# =================================================================
# CORE CASCADE (203b)
# =================================================================

def cascade_203b(t, ba, tr, acc_frac=SUN_ACC):
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG
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
    return amp


# =================================================================
# MODEL VARIANTS
# =================================================================

def predict_baseline(t, ba, tr):
    """203b baseline."""
    return cascade_203b(t, ba, tr)


def predict_v1_sym(t, ba, tr, cc=INV_PHI_3):
    """Symmetric Gaussian pulse (for comparison)."""
    amp = cascade_203b(t, ba, tr)
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG

    # Inner: symmetric pulse at Schwabe troughs
    pulse_i = singularity_pulse_symmetric(schwabe_phase, PHI**2)
    amp += ba * cc * pulse_i * np.cos(schwabe_phase)

    # Above: symmetric pulse at Gleissberg troughs, opposing
    pulse_a = singularity_pulse_symmetric(gleiss_phase, PHI**2)
    phase_13 = 2 * np.pi * (t - tr) / (PHI**13)
    amp -= ba * cc * pulse_a * np.cos(phase_13)

    return amp


def predict_v2_exp(t, ba, tr, cc=INV_PHI_3, decay=PHI):
    """Exponential ARA decay after singularity."""
    amp = cascade_203b(t, ba, tr)
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG

    # Inner: fires at Schwabe trough, decays at rate φ
    pulse_i = singularity_pulse_ara_decay(schwabe_phase, decay)
    amp += ba * cc * pulse_i * np.cos(schwabe_phase)

    # Above: fires at Gleissberg trough, decays at rate φ, opposing
    pulse_a = singularity_pulse_ara_decay(gleiss_phase, decay)
    phase_13 = 2 * np.pi * (t - tr) / (PHI**13)
    amp -= ba * cc * pulse_a * np.cos(phase_13)

    return amp


def predict_v3_saw(t, ba, tr, cc=INV_PHI_3):
    """Pulse shape follows receiving system's ARA sawtooth (inverted)."""
    amp = cascade_203b(t, ba, tr)
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG

    # Inner: follows Sun's ARA shape (acc_frac=0.618)
    pulse_i = singularity_pulse_ara_sawtooth(schwabe_phase, SUN_ACC)
    amp += ba * cc * pulse_i * np.cos(schwabe_phase)

    # Above: follows Sun's ARA shape, opposing
    pulse_a = singularity_pulse_ara_sawtooth(gleiss_phase, SUN_ACC)
    phase_13 = 2 * np.pi * (t - tr) / (PHI**13)
    amp -= ba * cc * pulse_a * np.cos(phase_13)

    return amp


def predict_v4_obs_saw(t, ba, tr, cc=INV_PHI_3):
    """Pulse follows OBSERVED ARA sawtooth (acc_frac=0.400 from data)."""
    amp = cascade_203b(t, ba, tr)
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG

    # Inner: follows observed ARA shape (acc_frac=0.400)
    pulse_i = singularity_pulse_ara_sawtooth(schwabe_phase, MEAN_RF)
    amp += ba * cc * pulse_i * np.cos(schwabe_phase)

    # Above: follows observed shape, opposing
    pulse_a = singularity_pulse_ara_sawtooth(gleiss_phase, MEAN_RF)
    phase_13 = 2 * np.pi * (t - tr) / (PHI**13)
    amp -= ba * cc * pulse_a * np.cos(phase_13)

    return amp


def predict_v5_inner_only_exp(t, ba, tr, cc=INV_PHI_3, decay=PHI):
    """Just inner, no above. Isolate effect."""
    amp = cascade_203b(t, ba, tr)
    schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE
    pulse_i = singularity_pulse_ara_decay(schwabe_phase, decay)
    amp += ba * cc * pulse_i * np.cos(schwabe_phase)
    return amp


def predict_v6_above_only_exp(t, ba, tr, cc=INV_PHI_3, decay=PHI):
    """Just above opposition, no inner."""
    amp = cascade_203b(t, ba, tr)
    gleiss_phase = 2 * np.pi * (t - tr) / GLEISSBERG
    pulse_a = singularity_pulse_ara_decay(gleiss_phase, decay)
    phase_13 = 2 * np.pi * (t - tr) / (PHI**13)
    amp -= ba * cc * pulse_a * np.cos(phase_13)
    return amp


# Causal wrapper
def mk_causal(pulse_fn_type='exp', cc=INV_PHI_3, decay=PHI,
              use_drain=False, inner=True, above=True):
    def _p(years, amps, ba, tr):
        preds = []
        for i, t in enumerate(years):
            sa = SUN_ACC if i == 0 else ara_to_acc(amps[i-1] / ba)

            # Base cascade with causal gate
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

            schwabe_phase = 2 * np.pi * (t - tr) / SCHWABE

            if pulse_fn_type == 'exp':
                pulse_i = singularity_pulse_ara_decay(schwabe_phase, decay)
                pulse_a = singularity_pulse_ara_decay(gleiss_phase, decay)
            elif pulse_fn_type == 'saw':
                pulse_i = singularity_pulse_ara_sawtooth(schwabe_phase, sa)
                pulse_a = singularity_pulse_ara_sawtooth(gleiss_phase, sa)
            else:
                pulse_i = singularity_pulse_symmetric(schwabe_phase, PHI**2)
                pulse_a = singularity_pulse_symmetric(gleiss_phase, PHI**2)

            if inner:
                amp += ba * cc * pulse_i * np.cos(schwabe_phase)
            if above:
                phase_13 = 2 * np.pi * (t - tr) / (PHI**13)
                amp -= ba * cc * pulse_a * np.cos(phase_13)

            if use_drain:
                amp_ratio = amp / ba
                amp -= INV_PHI_9 * amp * amp_ratio * abs(np.cos(gleiss_phase))

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
    print("SCRIPT 216 — ADDITIVE SINGULARITY + ARA DECAY")
    print("=" * 70)
    print("""
  Energy arrives at singularity, then DISSIPATES at receiving ARA rate.
  Three pulse shapes tested:
    1. Symmetric Gaussian (old approach — for comparison)
    2. Exponential decay at rate φ (Dylan's ARA decay insight)
    3. Inverse sawtooth following receiving system's ARA shape
""")

    results = []

    # ---- Baseline ----
    print("[1/10] 203b baseline...")
    r = evaluate("203b baseline", predict_baseline)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # ---- Static variants ----
    print("\n[2/10] V1: Symmetric pulse (comparison)...")
    r = evaluate("V1 symmetric", predict_v1_sym)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[3/10] V2: Exponential ARA decay (rate=phi)...")
    r = evaluate("V2 exp decay phi", predict_v2_exp)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[4/10] V3: ARA sawtooth decay (ideal 0.618)...")
    r = evaluate("V3 saw decay ideal", predict_v3_saw)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[5/10] V4: ARA sawtooth decay (observed 0.400)...")
    r = evaluate("V4 saw decay observed", predict_v4_obs_saw)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # ---- Isolate inner vs above ----
    print("\n[6/10] V5: Inner only (exp decay)...")
    r = evaluate("V5 inner only exp", predict_v5_inner_only_exp)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    print("\n[7/10] V6: Above only (exp decay, opposing)...")
    r = evaluate("V6 above only exp", predict_v6_above_only_exp)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), rise r={r['rr']:+.3f}, "
          f"splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # ---- Coupling sweep for best pulse type ----
    best_so_far = min([r for r in results if r['label'] != '203b baseline'],
                      key=lambda r: r['loo'])
    print(f"\n  Best static so far: {best_so_far['label']}")

    print("\n[8/10] Coupling strength sweep (exp decay, rate=phi)...")
    for cc_name, cc in [("1/phi", INV_PHI), ("1/phi2", INV_PHI**2),
                        ("1/phi4", INV_PHI_4), ("1/phi6", INV_PHI**6)]:
        lbl = f"V2 cc={cc_name}"
        fn = lambda t, ba, tr, _cc=cc: predict_v2_exp(t, ba, tr, cc=_cc)
        r = evaluate(lbl, fn)
        results.append(r)
        print(f"  {lbl:<25s} LOO={r['loo']:7.2f} ({r['imp']:+.1f}%) "
              f"rise r={r['rr']:+.3f} splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # ---- Decay rate sweep ----
    print("\n[9/10] Decay rate sweep (cc=1/phi3)...")
    for dr_name, dr in [("1/phi", INV_PHI), ("1", 1.0), ("phi", PHI),
                        ("phi2", PHI**2), ("phi3", PHI**3)]:
        lbl = f"V2 decay={dr_name}"
        fn = lambda t, ba, tr, _dr=dr: predict_v2_exp(t, ba, tr, decay=_dr)
        r = evaluate(lbl, fn)
        results.append(r)
        print(f"  {lbl:<25s} LOO={r['loo']:7.2f} ({r['imp']:+.1f}%) "
              f"rise r={r['rr']:+.3f} splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    # ---- Causal + drain versions of best ----
    print("\n[10/10] Causal + drain versions...")

    fn_c1 = mk_causal(pulse_fn_type='exp', cc=INV_PHI_3, decay=PHI)
    r = evaluate("C: exp decay causal", fn_c1, is_seq=True)
    results.append(r)
    print(f"  C: exp decay causal      LOO={r['loo']:7.2f} ({r['imp']:+.1f}%) "
          f"rise r={r['rr']:+.3f} splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    fn_c2 = mk_causal(pulse_fn_type='exp', cc=INV_PHI_3, decay=PHI, use_drain=True)
    r = evaluate("C+D: exp decay+drain", fn_c2, is_seq=True)
    results.append(r)
    print(f"  C+D: exp decay+drain     LOO={r['loo']:7.2f} ({r['imp']:+.1f}%) "
          f"rise r={r['rr']:+.3f} splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    fn_c3 = mk_causal(pulse_fn_type='saw', cc=INV_PHI_3)
    r = evaluate("C: saw decay causal", fn_c3, is_seq=True)
    results.append(r)
    print(f"  C: saw decay causal      LOO={r['loo']:7.2f} ({r['imp']:+.1f}%) "
          f"rise r={r['rr']:+.3f} splits={r['sw']}/7  [{time.time()-t0:.0f}s]")

    fn_c4 = mk_causal(pulse_fn_type='saw', cc=INV_PHI_3, use_drain=True)
    r = evaluate("C+D: saw decay+drain", fn_c4, is_seq=True)
    results.append(r)
    print(f"  C+D: saw decay+drain     LOO={r['loo']:7.2f} ({r['imp']:+.1f}%) "
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

    # Temporal splits for top models
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS — TOP MODELS")
    print(f"{'='*70}")
    shown = set()
    for r in [bl] + all_sorted[1:3] + [bw, bs]:
        if r['label'] in shown: continue
        shown.add(r['label'])
        print(f"\n  {r['label']}: {r['sw']}/7")
        for nt, ntest, pm, sm, w in r['sd']:
            print(f"    Train {nt:2d} / Test {ntest:2d}: "
                  f"phi={pm:.1f}  sine={sm:.1f}  -> {w}")

    # Dalton
    print(f"\n{'='*70}")
    print("DALTON MINIMUM (Cycles 5-7, obs: 82/81/119)")
    print(f"{'='*70}")
    shown2 = set()
    for r in all_sorted[:5] + [bw]:
        if r['label'] in shown2: continue
        shown2.add(r['label'])
        d = [4, 5, 6]
        dm = np.mean([abs(r['pf'][i] - peak_amps[i]) for i in d])
        print(f"  {r['label']:<35s} Dalton MAE={dm:.1f}  "
              f"(C5={r['pf'][4]:.0f} C6={r['pf'][5]:.0f} C7={r['pf'][6]:.0f})")

    # Per-cycle for best non-baseline
    best_new = [r for r in all_sorted if r['label'] != '203b baseline'][0]
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {best_new['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'RF':>6s}")
    for i, c in enumerate(cycle_nums):
        p = best_new['pf'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} "
              f"{p - peak_amps[i]:+7.1f} {rise_fracs[i]:6.3f}")

    print(f"\n{'='*70}")
    print("CROSS-REFERENCE")
    print(f"{'='*70}")
    print(f"""
  203b single gate:        LOO=37.66, splits=1/7, rise r=+0.767
  207 V1 causal:           LOO=38.82, splits=3/7 <- extrap champ
  210 V5 causal+drain:     LOO=36.62, splits=2/7
  211 V4d Wald+drain:      LOO=36.46, splits=0/7 <- interp champ
  214 V4 deep caus:        rise r=+0.583 <- Waldmeier champ
  215c: FAILED — splitting cascade killed it (LOO 61-65)

  This script (additive + ARA decay):
    Best LOO:    {bl['label']}: {bl['loo']:.2f}, splits={bl['sw']}/7
    Best Wald:   {bw['label']}: r={bw['rr']:+.3f}
    Best splits: {bs['label']}: {bs['sw']}/7

  Total time: {time.time()-t0:.0f}s
""")
