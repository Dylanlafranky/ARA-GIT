#!/usr/bin/env python3
"""
Script 205b — Read at the Singularity Point

INSIGHT (Dylan):
  "Before makes sense — you're getting the actual information before
  temporal and other couplings energy enters the system for the next cycle."

  "25% to 63% looks like half a cycle. Maybe we need to put a -half a cycle
  in there, to read the energy level AT the singularity point just before,
  to get the correct height of what the trough or crest would be before
  the temporal extras."

APPROACH:
  Instead of reading the cascade at t_peak, read it at:
    t_singularity = t_peak - offset

  where offset is approximately half a Schwabe cycle, landing us at
  the preceding minimum (singularity/trough). The cascade value there
  is the BASE energy before temporal coupling adds on top.

MODELS:
  A: Fixed offset = -φ⁵/2 ≈ -5.545yr (half Schwabe, from φ)
  B: Fixed offset = -duration/2 per cycle (half actual cycle)
  C: Fixed offset = -rise_time per cycle (back to cycle start)
  D: Offset = -(1 - rise_frac) × duration (back to previous trough)
  E: Sweep near -φ⁵/2 for fine-tuning
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9

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
N = len(cycle_nums)
rise_times = peak_years - start_years
rise_fracs = rise_times / durations

CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
ACC_FRAC = PHI / (PHI + 1)
HALF_SCHWABE = (PHI**5) / 2  # ≈ 5.545yr

def mae(p, o):
    return np.mean(np.abs(np.array(p) - np.array(o)))

def sawtooth_valve(phase):
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < ACC_FRAC:
        state = (cycle_pos / ACC_FRAC) * PHI
    else:
        ramp = (cycle_pos - ACC_FRAC) / (1 - ACC_FRAC)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    return state / ((PHI + INV_PHI) / 2)

def cascade_predict(t_eval, base_amp, t_ref):
    """Core cascade evaluation at arbitrary time point."""
    gleiss_phase = 2 * np.pi * (t_eval - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)
    amp = base_amp
    for period in CASCADE:
        phase = 2 * np.pi * (t_eval - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)
    amp += base_amp * INV_PHI_9 * np.cos(gleiss_phase)
    return amp


# --- MODEL A: Fixed offset = -φ⁵/2 ---
def predict_A(t, ba, tr):
    return cascade_predict(t - HALF_SCHWABE, ba, tr)

# --- MODEL B: Variable offset = -duration_i/2 ---
def predict_B(t, ba, tr, dur):
    return cascade_predict(t - dur/2, ba, tr)

# --- MODEL C: Variable offset = -rise_time (back to cycle start) ---
def predict_C(t, ba, tr, rise):
    return cascade_predict(t - rise, ba, tr)

# --- MODEL D: Offset = back to previous trough ---
def predict_D(t, ba, tr, dur, rise_frac):
    # Previous trough is at t_peak - rise_time = t_start
    # But the SINGULARITY is actually at start, so go there
    return cascade_predict(t - (rise_frac * dur), ba, tr)

# --- MODEL E: Fine sweep near -φ⁵/2 ---
def predict_E(t, ba, tr, offset):
    return cascade_predict(t - offset, ba, tr)


def fit_fixed(predict_fn, train_years, train_amps):
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 40):
        for ba in np.linspace(np.mean(train_amps)*0.6, np.mean(train_amps)*1.4, 30):
            preds = [predict_fn(t, ba, t_ref) for t in train_years]
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae

def fit_variable(predict_fn, train_years, train_amps, extra_args_list):
    """extra_args_list[i] = tuple of extra args for train point i."""
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 40):
        for ba in np.linspace(np.mean(train_amps)*0.6, np.mean(train_amps)*1.4, 30):
            preds = [predict_fn(t, ba, t_ref, *args)
                     for t, args in zip(train_years, extra_args_list)]
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


def full_eval(name, predict_fn, is_variable=False, extra_args=None, show_detail=True):
    """LOO + temporal splits + per-cycle detail."""
    print(f"\n{'='*72}")
    print(f"  {name}")
    print(f"{'='*72}")

    phi_errs, sine_errs = [], []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        if is_variable:
            ea_train = [extra_args[j] for j in range(N) if j != i]
            ba_i, tr_i, _ = fit_variable(predict_fn, peak_years[mask],
                                          peak_amps[mask], ea_train)
            pred_i = predict_fn(peak_years[i], ba_i, tr_i, *extra_args[i])
        else:
            ba_i, tr_i, _ = fit_fixed(predict_fn, peak_years[mask], peak_amps[mask])
            pred_i = predict_fn(peak_years[i], ba_i, tr_i)
        phi_errs.append(abs(pred_i - peak_amps[i]))
        sine_errs.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    phi_errs = np.array(phi_errs)
    sine_errs = np.array(sine_errs)
    loo = phi_errs.mean()
    sloo = sine_errs.mean()
    pct = (loo/sloo - 1)*100
    wins = np.sum(phi_errs < sine_errs)

    n_boot = 10000
    boot = sum(1 for _ in range(n_boot)
               if phi_errs[np.random.choice(N,N,True)].mean() <
                  sine_errs[np.random.choice(N,N,True)].mean())

    print(f"  LOO MAE: {loo:.2f} (sine {sloo:.2f}) → {pct:+.1f}%")
    print(f"  Wins: {wins}/25 | Bootstrap: {boot/n_boot*100:.1f}%")

    # Temporal splits
    sw = 0
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N: continue
        if is_variable:
            ea_train = extra_args[:n_train]
            ba_s, tr_s, _ = fit_variable(predict_fn, peak_years[:n_train],
                                          peak_amps[:n_train], ea_train)
            tp = [predict_fn(peak_years[j], ba_s, tr_s, *extra_args[j])
                  for j in range(n_train, N)]
        else:
            ba_s, tr_s, _ = fit_fixed(predict_fn, peak_years[:n_train],
                                       peak_amps[:n_train])
            tp = [predict_fn(t, ba_s, tr_s) for t in peak_years[n_train:]]
        ta = peak_amps[n_train:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:n_train].mean()), ta)
        w = "φ" if pm < sm else "sine"
        if pm < sm: sw += 1
        print(f"    Train {n_train:2d} / Test {N-n_train:2d}: φ={pm:.1f} sine={sm:.1f} → {w}")
    print(f"  Temporal splits: {sw}/7")

    # Per-cycle detail
    if show_detail:
        if is_variable:
            ba_f, tr_f, _ = fit_variable(predict_fn, peak_years, peak_amps, extra_args)
        else:
            ba_f, tr_f, _ = fit_fixed(predict_fn, peak_years, peak_amps)

        print(f"\n  {'Cyc':>3s} {'Year':>6s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} "
              f"{'|Err|':>6s} {'RFrac':>6s}")
        errs = []
        for i, c in enumerate(cycle_nums):
            if is_variable:
                pred = predict_fn(peak_years[i], ba_f, tr_f, *extra_args[i])
            else:
                pred = predict_fn(peak_years[i], ba_f, tr_f)
            err = pred - peak_amps[i]
            errs.append(err)
            print(f"  {c:3d} {peak_years[i]:6.0f} {peak_amps[i]:7.1f} {pred:7.1f} "
                  f"{err:+7.1f} {abs(err):6.1f} {rise_fracs[i]:5.1%}")

        errs = np.array(errs)
        print(f"\n  Error correlations:")
        print(f"    Rise fraction:   r = {np.corrcoef(errs, rise_fracs)[0,1]:+.3f}")
        print(f"    Peak amplitude:  r = {np.corrcoef(errs, peak_amps)[0,1]:+.3f}")
        print(f"    Duration:        r = {np.corrcoef(errs, durations)[0,1]:+.3f}")

    return loo, pct, wins, boot/n_boot*100, sw


if __name__ == '__main__':
    print("=" * 72)
    print("SCRIPT 205b — READ AT THE SINGULARITY POINT")
    print("=" * 72)

    print(f"\n  Key φ-offsets:")
    print(f"    φ⁵/2  = {HALF_SCHWABE:.3f}yr (half Schwabe)")
    print(f"    φ⁵    = {PHI**5:.3f}yr (full Schwabe)")
    print(f"    1/φ   = {INV_PHI:.3f} × cycle")
    print(f"    Mean rise time = {rise_times.mean():.2f}yr")
    print(f"    Mean rise frac = {rise_fracs.mean():.3f}")

    results = {}

    # MODEL A: Fixed -φ⁵/2
    r = full_eval(f"A: Fixed offset = -φ⁵/2 = -{HALF_SCHWABE:.2f}yr (singularity read)",
                  predict_A)
    results['A'] = r

    # MODEL B: Variable -duration/2
    extra_B = [(durations[i],) for i in range(N)]
    r = full_eval("B: Variable offset = -duration_i/2 (half each cycle)",
                  predict_B, is_variable=True, extra_args=extra_B)
    results['B'] = r

    # MODEL C: Variable -rise_time (back to start)
    extra_C = [(rise_times[i],) for i in range(N)]
    r = full_eval("C: Variable offset = -rise_time_i (cycle start)",
                  predict_C, is_variable=True, extra_args=extra_C)
    results['C'] = r

    # MODEL D: Back to previous trough
    extra_D = [(durations[i], rise_fracs[i]) for i in range(N)]
    r = full_eval("D: Variable offset = -rise_frac×dur (previous trough)",
                  predict_D, is_variable=True, extra_args=extra_D)
    results['D'] = r

    # MODEL E: Fine sweep near φ⁵/2
    print(f"\n{'='*72}")
    print("  E: FINE SWEEP near -φ⁵/2")
    print(f"{'='*72}")

    fine_offsets = np.arange(3.0, 8.0, 0.5)
    print(f"\n  {'Offset':>7s} {'LOO':>7s} {'vs sine':>8s} {'Wins':>5s}")
    best_fine_off, best_fine_loo = 0, 999

    for off in fine_offsets:
        pfn = lambda t, ba, tr, o=off: cascade_predict(t - o, ba, tr)
        ba_f, tr_f, _ = fit_fixed(pfn, peak_years, peak_amps)
        # Quick LOO
        pe, se = [], []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            bai, tri, _ = fit_fixed(pfn, peak_years[mask], peak_amps[mask])
            pi = pfn(peak_years[i], bai, tri)
            pe.append(abs(pi - peak_amps[i]))
            se.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))
        loo = np.mean(pe)
        sloo = np.mean(se)
        pct = (loo/sloo-1)*100
        wins = np.sum(np.array(pe) < np.array(se))
        mk = " ◄" if loo < best_fine_loo else ""
        if loo < best_fine_loo:
            best_fine_loo, best_fine_off = loo, off
        print(f"  {off:+6.1f}yr {loo:7.2f} {pct:+7.1f}% {wins:3d}/25{mk}")

    print(f"\n  Best fine offset: -{best_fine_off:.1f}yr → LOO {best_fine_loo:.2f}")

    # Full eval at best fine offset
    pfn_best = lambda t, ba, tr: cascade_predict(t - best_fine_off, ba, tr)
    r = full_eval(f"E_best: Fixed offset = -{best_fine_off:.1f}yr",
                  pfn_best)
    results['E_best'] = r

    # === SUMMARY ===
    print(f"\n{'='*72}")
    print("SUMMARY TABLE")
    print(f"{'='*72}")
    print(f"  {'Model':<45s} {'LOO':>7s} {'vs%':>7s} {'W':>4s} {'Boot':>5s} {'TS':>4s}")
    print(f"  {'-'*45} {'-'*7} {'-'*7} {'-'*4} {'-'*5} {'-'*4}")
    print(f"  {'203b baseline (offset=0)':<45s} {'37.66':>7s} {'-22.8':>6s}% {'15':>3s} {'89.8':>5s} {'1':>3s}")
    for name, (loo, pct, wins, boot, sw) in results.items():
        print(f"  {name:<45s} {loo:7.2f} {pct:+6.1f}% {wins:3d} {boot:5.1f} {sw:3d}")

    print(f"\n  φ⁵/2 = {HALF_SCHWABE:.3f}yr")
    print(f"  Best offset = -{best_fine_off:.1f}yr")
    if best_fine_off > 0:
        ratio = best_fine_off / (PHI**5)
        print(f"  Ratio to φ⁵: {ratio:.3f} (1/2 = {0.5:.3f}, 1/φ = {INV_PHI:.3f})")

    print(f"\n{'='*72}")
    print("END SCRIPT 205b")
    print(f"{'='*72}")
