#!/usr/bin/env python3
"""
Script 205 — Temporal Offset: Where Are We Actually Reading the Cycle?

INSIGHT (Dylan):
  "We're propelling into φ right for time, but we aren't accurately
  measuring how far into φ we're travelling each time."

  The peak amplitude is the RESULT of the accumulation. Like a scalene
  triangle with two corners locked, the third corner (where we READ)
  may be offset from where the cascade naturally peaks.
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

def predict_base(t, base_amp, t_ref, offset=0.0):
    """203b with temporal offset."""
    t_eval = t + offset
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

def predict_ara_offset(t, base_amp, t_ref, cycle_start, cycle_dur):
    """V5: offset = (ARA_ideal - actual_rise_frac) × duration."""
    actual_frac = (t - cycle_start) / cycle_dur
    offset = (ACC_FRAC - actual_frac) * cycle_dur
    return predict_base(t, base_amp, t_ref, offset=offset)

def fit(train_years, train_amps, offset=0.0):
    best_mae, best_ba, best_tr = 1e9, 0, 0
    # Coarser grid for speed
    for t_ref in np.linspace(1700, 1850, 40):
        for ba in np.linspace(np.mean(train_amps) * 0.6,
                               np.mean(train_amps) * 1.4, 30):
            preds = [predict_base(t, ba, t_ref, offset) for t in train_years]
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae

def fit_v5(train_years, train_amps, train_starts, train_durs):
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 40):
        for ba in np.linspace(np.mean(train_amps) * 0.6,
                               np.mean(train_amps) * 1.4, 30):
            preds = [predict_ara_offset(t, ba, t_ref, s, d)
                     for t, s, d in zip(train_years, train_starts, train_durs)]
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


if __name__ == '__main__':
    print("=" * 72)
    print("SCRIPT 205 — TEMPORAL OFFSET ANALYSIS")
    print("=" * 72)

    # --- Cycle timing data ---
    print(f"\nCYCLE TIMING — Where does the peak actually fall?")
    print(f"  ARA says peak at {ACC_FRAC:.1%} of cycle ({ACC_FRAC:.3f})")
    print(f"\n  {'Cyc':>3s} {'Start':>7s} {'Peak':>7s} {'Dur':>5s} "
          f"{'Rise':>5s} {'Frac':>6s} {'vs ARA':>7s} {'Offset':>8s}")

    for i, c in enumerate(cycle_nums):
        delta = rise_fracs[i] - ACC_FRAC
        offset_yr = (ACC_FRAC - rise_fracs[i]) * durations[i]
        print(f"  {c:3d} {start_years[i]:7.1f} {peak_years[i]:7.1f} "
              f"{durations[i]:5.1f} {rise_times[i]:5.1f} "
              f"{rise_fracs[i]:5.1%} {delta:+6.1%} {offset_yr:+7.2f}yr")

    print(f"\n  Mean rise fraction: {rise_fracs.mean():.3f} (ARA: {ACC_FRAC:.3f})")
    print(f"  Std: {rise_fracs.std():.3f} | Range: {rise_fracs.min():.3f}-{rise_fracs.max():.3f}")

    # --- OFFSET SWEEP (203b only, fastest) ---
    print(f"\n{'='*72}")
    print("203b OFFSET SWEEP — Fixed offset applied to all cycles")
    print(f"{'='*72}")

    offsets = [-3, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3]
    print(f"\n  {'Offset':>7s} {'FullMAE':>8s} {'LOO MAE':>8s} {'vs sine':>8s} {'Wins':>5s}")

    best_off, best_loo = 0, 999
    loo_results = {}

    for offset in offsets:
        ba, tr, fmae = fit(peak_years, peak_amps, offset)
        # LOO
        phi_errs, sine_errs = [], []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            ba_i, tr_i, _ = fit(peak_years[mask], peak_amps[mask], offset)
            pred_i = predict_base(peak_years[i], ba_i, tr_i, offset)
            phi_errs.append(abs(pred_i - peak_amps[i]))
            sine_errs.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))
        loo = np.mean(phi_errs)
        sloo = np.mean(sine_errs)
        pct = (loo / sloo - 1) * 100
        wins = np.sum(np.array(phi_errs) < np.array(sine_errs))
        marker = " ◄" if loo < best_loo else ""
        if loo < best_loo:
            best_loo, best_off = loo, offset
        loo_results[offset] = (loo, pct, wins, phi_errs, sine_errs)
        print(f"  {offset:+6.1f}yr {fmae:8.2f} {loo:8.2f} {pct:+7.1f}% {wins:3d}/25{marker}")

    print(f"\n  Best fixed offset: {best_off:+.1f}yr → LOO {best_loo:.2f}")

    # --- Per-cycle errors at best offset AND at offset=0 ---
    for show_offset in [0, best_off]:
        ba, tr, _ = fit(peak_years, peak_amps, show_offset)
        print(f"\n{'='*72}")
        print(f"  PER-CYCLE DETAIL — offset = {show_offset:+.1f}yr")
        print(f"{'='*72}")
        print(f"  {'Cyc':>3s} {'Year':>6s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} "
              f"{'|Err|':>6s} {'RFrac':>6s} {'Duration':>8s} {'GlPhase':>8s}")

        errors = []
        for i, c in enumerate(cycle_nums):
            pred = predict_base(peak_years[i], ba, tr, show_offset)
            err = pred - peak_amps[i]
            errors.append(err)
            gp = (2*np.pi*(peak_years[i]+show_offset-tr)/GLEISSBERG) % (2*np.pi)
            print(f"  {c:3d} {peak_years[i]:6.0f} {peak_amps[i]:7.1f} {pred:7.1f} "
                  f"{err:+7.1f} {abs(err):6.1f} {rise_fracs[i]:5.1%} "
                  f"{durations[i]:7.1f}yr {gp/(2*np.pi):7.1%}")

        errors = np.array(errors)
        print(f"\n  Error correlations (signed error vs...):")
        print(f"    Rise fraction:   r = {np.corrcoef(errors, rise_fracs)[0,1]:+.3f}")
        print(f"    Duration:        r = {np.corrcoef(errors, durations)[0,1]:+.3f}")
        print(f"    Peak amplitude:  r = {np.corrcoef(errors, peak_amps)[0,1]:+.3f}")
        print(f"    Rise time (yr):  r = {np.corrcoef(errors, rise_times)[0,1]:+.3f}")
        print(f"    Cycle number:    r = {np.corrcoef(errors, np.arange(N))[0,1]:+.3f}")

    # --- Temporal splits at best offset ---
    print(f"\n{'='*72}")
    print(f"  TEMPORAL SPLITS at offset = {best_off:+.1f}yr")
    print(f"{'='*72}")
    split_wins = 0
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N: continue
        ba_s, tr_s, _ = fit(peak_years[:n_train], peak_amps[:n_train], best_off)
        tp = [predict_base(t, ba_s, tr_s, best_off) for t in peak_years[n_train:]]
        ta = peak_amps[n_train:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:n_train].mean()), ta)
        w = "φ" if pm < sm else "sine"
        if pm < sm: split_wins += 1
        print(f"    Train {n_train:2d} / Test {N-n_train:2d}: φ={pm:.1f} sine={sm:.1f} → {w}")
    print(f"  Splits: {split_wins}/7")

    # --- V5: ARA-AWARE VARIABLE OFFSET ---
    print(f"\n{'='*72}")
    print("  V5: ARA-AWARE VARIABLE OFFSET")
    print("  offset_i = (0.618 - rise_frac_i) × duration_i")
    print(f"{'='*72}")

    # LOO
    phi_errs_v5, sine_errs_v5 = [], []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        ba_i, tr_i, _ = fit_v5(peak_years[mask], peak_amps[mask],
                                start_years[mask], durations[mask])
        pred_i = predict_ara_offset(peak_years[i], ba_i, tr_i,
                                     start_years[i], durations[i])
        phi_errs_v5.append(abs(pred_i - peak_amps[i]))
        sine_errs_v5.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    phi_errs_v5 = np.array(phi_errs_v5)
    sine_errs_v5 = np.array(sine_errs_v5)
    loo_v5 = phi_errs_v5.mean()
    sloo_v5 = sine_errs_v5.mean()
    wins_v5 = np.sum(phi_errs_v5 < sine_errs_v5)
    pct_v5 = (loo_v5 / sloo_v5 - 1) * 100

    n_boot = 10000
    boot_v5 = sum(1 for _ in range(n_boot)
                  if phi_errs_v5[np.random.choice(N, N, True)].mean() <
                     sine_errs_v5[np.random.choice(N, N, True)].mean())

    print(f"\n  V5 LOO: {loo_v5:.2f} (sine {sloo_v5:.2f}) → {pct_v5:+.1f}%")
    print(f"  Wins: {wins_v5}/25 | Bootstrap: {boot_v5/n_boot*100:.1f}%")

    # V5 temporal splits
    v5_sw = 0
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N: continue
        ba_s, tr_s, _ = fit_v5(peak_years[:n_train], peak_amps[:n_train],
                                start_years[:n_train], durations[:n_train])
        tp = [predict_ara_offset(peak_years[j], ba_s, tr_s, start_years[j], durations[j])
              for j in range(n_train, N)]
        ta = peak_amps[n_train:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:n_train].mean()), ta)
        w = "φ" if pm < sm else "sine"
        if pm < sm: v5_sw += 1
        print(f"    Train {n_train:2d} / Test {N-n_train:2d}: φ={pm:.1f} sine={sm:.1f} → {w}")
    print(f"  V5 splits: {v5_sw}/7")

    # V5 per-cycle
    ba_f, tr_f, _ = fit_v5(peak_years, peak_amps, start_years, durations)
    print(f"\n  V5 PER-CYCLE:")
    print(f"  {'Cyc':>3s} {'Year':>6s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'Offset':>8s}")
    v5_errors = []
    for i, c in enumerate(cycle_nums):
        pred = predict_ara_offset(peak_years[i], ba_f, tr_f, start_years[i], durations[i])
        err = pred - peak_amps[i]
        v5_errors.append(err)
        off = (ACC_FRAC - rise_fracs[i]) * durations[i]
        print(f"  {c:3d} {peak_years[i]:6.0f} {peak_amps[i]:7.1f} {pred:7.1f} "
              f"{err:+7.1f} {off:+7.2f}yr")

    v5_errors = np.array(v5_errors)
    print(f"\n  V5 error correlations:")
    print(f"    Rise fraction:   r = {np.corrcoef(v5_errors, rise_fracs)[0,1]:+.3f}")
    print(f"    Duration:        r = {np.corrcoef(v5_errors, durations)[0,1]:+.3f}")
    print(f"    Peak amplitude:  r = {np.corrcoef(v5_errors, peak_amps)[0,1]:+.3f}")

    # === FINAL ===
    print(f"\n{'='*72}")
    print("SUMMARY")
    print(f"{'='*72}")
    print(f"  203b (no offset):        LOO = 37.66  (-22.8%)")
    print(f"  203b (best fixed {best_off:+.1f}yr): LOO = {best_loo:.2f}  ({(best_loo/48.78-1)*100:+.1f}%)")
    print(f"  V5 (ARA variable):       LOO = {loo_v5:.2f}  ({pct_v5:+.1f}%)")
    print(f"  V5 temporal splits:      {v5_sw}/7")
