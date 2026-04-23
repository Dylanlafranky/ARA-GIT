#!/usr/bin/env python3
"""
Script 207 — Causal Gate: Previous Cycle Sets the Present

INSIGHT:
  The gate for cycle N is set by the EXIT STATE of cycle N-1.
  The energy crossing the singularity (trough) determines
  the shape of the next accumulation.

  This is causal: past → present, not present → present.

  Gate shape = f(previous cycle's amplitude / mean)
  Using V3's ARA mapping: acc_frac = 1 / (1 + prev_ARA)

MODELS:
  V1: Previous observed amplitude sets gate (uses actual data — upper bound)
  V2: Previous CASCADE prediction sets gate (fully self-contained)
  V3: Running average of last 2 cycles sets gate (smoothed memory)
  V4: Gleissberg-phase ARA — long-period modulation of gate shape
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
peak_years = np.array([CYCLES[c][1] for c in cycle_nums])
peak_amps = np.array([CYCLES[c][2] for c in cycle_nums])
N = len(cycle_nums)
MEAN_AMP = peak_amps.mean()

CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
STATIC_ACC = PHI / (PHI + 1)

def mae(p, o):
    return np.mean(np.abs(np.array(p) - np.array(o)))

def sawtooth_valve(phase, acc_frac=None):
    if acc_frac is None:
        acc_frac = STATIC_ACC
    acc_frac = max(0.15, min(0.85, acc_frac))
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < acc_frac:
        state = (cycle_pos / acc_frac) * PHI
    else:
        ramp = (cycle_pos - acc_frac) / (1 - acc_frac)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    return state / ((PHI + INV_PHI) / 2)

def cascade_core(t, base_amp, t_ref, acc_frac=None):
    """Core cascade with configurable gate shape."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase, acc_frac)
    amp = base_amp
    for period in CASCADE:
        phase = 2 * np.pi * (t - t_ref) / period
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

def ara_to_acc(ara_value):
    """ARA → accumulation fraction. Natural ARA division.
    High ARA (strong) → low acc_frac (fast rise)
    Low ARA (weak) → high acc_frac (slow rise)
    """
    return 1.0 / (1.0 + ara_value)


# ================================================================
# V1: Previous OBSERVED amplitude sets gate
# Uses actual historical data — provides an upper bound
# on how well causal gate can perform
# ================================================================

def predict_v1_sequence(peak_years_seq, peak_amps_prev, base_amp, t_ref):
    """Predict a sequence where each gate uses the PREVIOUS observed amp."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            # First cycle: use mean as prior (no previous data)
            prev_ara = 1.0
        else:
            prev_ara = peak_amps_prev[i-1] / base_amp
        acc_frac = ara_to_acc(prev_ara)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# V2: Previous CASCADE prediction sets gate (self-contained)
# No observed data needed — model feeds itself
# ================================================================

def predict_v2_sequence(peak_years_seq, base_amp, t_ref):
    """Self-feeding: each gate uses the model's OWN previous prediction."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            prev_ara = 1.0
        else:
            prev_ara = preds[i-1] / base_amp
        acc_frac = ara_to_acc(prev_ara)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# V3: Running average of last 2 observed cycles (smoothed memory)
# ================================================================

def predict_v3_sequence(peak_years_seq, peak_amps_prev, base_amp, t_ref):
    """Gate set by average of last 2 observed amplitudes."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            prev_ara = 1.0
        elif i == 1:
            prev_ara = peak_amps_prev[0] / base_amp
        else:
            prev_ara = (peak_amps_prev[i-1] + peak_amps_prev[i-2]) / (2 * base_amp)
        acc_frac = ara_to_acc(prev_ara)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# V4: Gleissberg-phase modulates gate shape
# The long-period wave controls how "breathing" the gate is
# Near Gleissberg peak: gate is more dynamic (wider ARA range)
# Near Gleissberg trough: gate is more static (near 0.618)
# ================================================================

def predict_v4(t, base_amp, t_ref, prev_amp=None):
    """Gleissberg-modulated dynamic gate."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gleiss_mod = 0.5 * (1 + np.cos(gleiss_phase))  # 0 at trough, 1 at peak

    if prev_amp is not None:
        prev_ara = prev_amp / base_amp
        dynamic_acc = ara_to_acc(prev_ara)
    else:
        dynamic_acc = STATIC_ACC

    # Blend: at Gleissberg peak, gate is fully dynamic
    # At Gleissberg trough, gate reverts to static 0.618
    acc_frac = STATIC_ACC + gleiss_mod * (dynamic_acc - STATIC_ACC)
    return cascade_core(t, base_amp, t_ref, acc_frac)

def predict_v4_sequence(peak_years_seq, peak_amps_prev, base_amp, t_ref):
    preds = []
    for i, t in enumerate(peak_years_seq):
        prev = peak_amps_prev[i-1] if i > 0 else None
        pred = predict_v4(t, base_amp, t_ref, prev)
        preds.append(pred)
    return preds


# ================================================================
# V5: Self-feeding + Gleissberg blend (V2 + V4 combined)
# ================================================================

def predict_v5_sequence(peak_years_seq, base_amp, t_ref):
    """Self-feeding with Gleissberg modulation."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
        gleiss_mod = 0.5 * (1 + np.cos(gleiss_phase))

        if i == 0:
            dynamic_acc = STATIC_ACC
        else:
            prev_ara = preds[i-1] / base_amp
            dynamic_acc = ara_to_acc(prev_ara)

        acc_frac = STATIC_ACC + gleiss_mod * (dynamic_acc - STATIC_ACC)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# BASELINE: static 203b
# ================================================================

def predict_static_sequence(peak_years_seq, base_amp, t_ref):
    return [cascade_core(t, base_amp, t_ref) for t in peak_years_seq]


# ================================================================
# FITTING & EVALUATION
# ================================================================

def fit_sequence(pred_seq_fn, train_years, train_amps, needs_prev=False):
    """Fit base_amp and t_ref using sequential prediction."""
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 50):
        for ba in np.linspace(np.mean(train_amps)*0.6,
                               np.mean(train_amps)*1.4, 35):
            if needs_prev:
                preds = pred_seq_fn(train_years, train_amps, ba, t_ref)
            else:
                preds = pred_seq_fn(train_years, ba, t_ref)
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


def eval_model(name, pred_seq_fn, needs_prev=False, show_detail=True):
    print(f"\n{'='*72}")
    print(f"  {name}")
    print(f"{'='*72}")

    # Full fit
    ba_f, tr_f, fmae = fit_sequence(pred_seq_fn, peak_years, peak_amps, needs_prev)

    if show_detail:
        if needs_prev:
            preds_full = pred_seq_fn(peak_years, peak_amps, ba_f, tr_f)
        else:
            preds_full = pred_seq_fn(peak_years, ba_f, tr_f)

        print(f"\n  {'Cyc':>3s} {'Year':>6s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} "
              f"{'|Err|':>6s} {'PrevObs':>8s} {'GateFrac':>9s}")
        errs = []
        for i, c in enumerate(cycle_nums):
            err = preds_full[i] - peak_amps[i]
            errs.append(err)
            prev_obs = peak_amps[i-1] if i > 0 else MEAN_AMP
            prev_ara = prev_obs / ba_f
            gate = ara_to_acc(prev_ara)
            print(f"  {c:3d} {peak_years[i]:6.0f} {peak_amps[i]:7.1f} "
                  f"{preds_full[i]:7.1f} {err:+7.1f} {abs(err):6.1f} "
                  f"{prev_obs:8.1f} {gate:8.1%}")

        errs = np.array(errs)
        rise_fracs = np.array([(CYCLES[c][1]-CYCLES[c][0])/CYCLES[c][3]
                                for c in cycle_nums])
        print(f"\n  Error correlations:")
        print(f"    Rise fraction:   r = {np.corrcoef(errs, rise_fracs)[0,1]:+.3f}")
        print(f"    Peak amplitude:  r = {np.corrcoef(errs, peak_amps)[0,1]:+.3f}")
        print(f"    Prev amplitude:  r = {np.corrcoef(errs[1:], peak_amps[:-1])[0,1]:+.3f}")

    # LOO — for causal models, we need to handle the sequence carefully
    # Remove point i, refit, predict point i using its predecessor's data
    phi_errs, sine_errs = [], []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        train_y = peak_years[mask]
        train_a = peak_amps[mask]

        ba_i, tr_i, _ = fit_sequence(pred_seq_fn, train_y, train_a, needs_prev)

        # For the held-out point, we need to construct the right sequence
        # The held-out point's predecessor is known (it's in training set)
        if needs_prev:
            # Build sequence up to and including point i
            seq_years = peak_years[:i+1]
            seq_amps = peak_amps[:i+1]  # Previous points are observed
            preds_seq = pred_seq_fn(seq_years, seq_amps, ba_i, tr_i)
            pred_i = preds_seq[-1]
        else:
            preds_seq = pred_seq_fn(peak_years[:i+1], ba_i, tr_i)
            pred_i = preds_seq[-1]

        phi_errs.append(abs(pred_i - peak_amps[i]))
        sine_errs.append(abs(np.mean(train_a) - peak_amps[i]))

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

    print(f"\n  LOO MAE: {loo:.2f} (sine {sloo:.2f}) → {pct:+.1f}%")
    print(f"  Wins: {wins}/25 | Bootstrap: {boot/n_boot*100:.1f}%")

    # Temporal splits — these are naturally causal!
    sw = 0
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N: continue
        ba_s, tr_s, _ = fit_sequence(pred_seq_fn, peak_years[:n_train],
                                      peak_amps[:n_train], needs_prev)
        # Predict test sequence using observed previous amps
        if needs_prev:
            full_preds = pred_seq_fn(peak_years, peak_amps, ba_s, tr_s)
        else:
            full_preds = pred_seq_fn(peak_years, ba_s, tr_s)
        test_preds = full_preds[n_train:]
        test_amps = peak_amps[n_train:]
        pm = mae(test_preds, test_amps)
        sm = mae(np.full(len(test_amps), peak_amps[:n_train].mean()), test_amps)
        w = "φ" if pm < sm else "sine"
        if pm < sm: sw += 1
        print(f"    Train {n_train:2d} / Test {N-n_train:2d}: φ={pm:.1f} sine={sm:.1f} → {w}")
    print(f"  Temporal splits: {sw}/7")

    return loo, pct, wins, boot/n_boot*100, sw


if __name__ == '__main__':
    print("=" * 72)
    print("SCRIPT 207 — CAUSAL GATE: PAST SETS PRESENT")
    print("=" * 72)

    print(f"\n  Gate mapping: acc_frac = 1/(1 + prev_ARA)")
    print(f"  prev_ARA = prev_observed_amp / base_amp")
    print(f"  Mean amplitude = {MEAN_AMP:.1f}")

    # Show what the causal gate SHOULD produce vs actual rise fracs
    print(f"\n  Causal gate vs actual Waldmeier:")
    print(f"  {'Cyc':>3s} {'PrevAmp':>8s} {'PrevARA':>8s} {'GateFrac':>9s} {'ActRise':>8s} {'Match':>6s}")
    ba_approx = MEAN_AMP
    for i, c in enumerate(cycle_nums):
        prev = peak_amps[i-1] if i > 0 else MEAN_AMP
        prev_ara = prev / ba_approx
        gate = ara_to_acc(prev_ara)
        actual = (CYCLES[c][1] - CYCLES[c][0]) / CYCLES[c][3]
        diff = abs(gate - actual)
        print(f"  {c:3d} {prev:8.1f} {prev_ara:8.3f} {gate:8.1%} "
              f"{actual:7.1%}  {diff:5.1%}")

    results = {}

    r = eval_model("BASELINE: Static 203b", predict_static_sequence, needs_prev=False)
    results['Static'] = r

    r = eval_model("V1: Previous OBSERVED amp sets gate (upper bound)",
                   predict_v1_sequence, needs_prev=True)
    results['V1_obs'] = r

    r = eval_model("V2: Self-feeding (model's own prediction sets gate)",
                   predict_v2_sequence, needs_prev=False)
    results['V2_self'] = r

    r = eval_model("V3: Running avg of last 2 observed",
                   predict_v3_sequence, needs_prev=True)
    results['V3_avg2'] = r

    r = eval_model("V4: Gleissberg-modulated dynamic gate",
                   predict_v4_sequence, needs_prev=True)
    results['V4_gleiss'] = r

    r = eval_model("V5: Self-feeding + Gleissberg blend",
                   predict_v5_sequence, needs_prev=False)
    results['V5_self_gl'] = r

    # === SUMMARY ===
    print(f"\n{'='*72}")
    print("SUMMARY")
    print(f"{'='*72}")
    print(f"  {'Model':<45s} {'LOO':>7s} {'vs%':>7s} {'W':>4s} {'Boot':>5s} {'TS':>4s}")
    print(f"  {'-'*45} {'-'*7} {'-'*7} {'-'*4} {'-'*5} {'-'*4}")
    for name, (loo, pct, wins, boot, sw) in results.items():
        print(f"  {name:<45s} {loo:7.2f} {pct:+6.1f}% {wins:3d} {boot:5.1f} {sw:3d}")

    best = min(results.keys(), key=lambda k: results[k][0])
    b = results[best]
    print(f"\n  BEST: {best}")
    print(f"    LOO = {b[0]:.2f} ({b[1]:+.1f}% vs sine)")
    print(f"    Temporal splits: {b[4]}/7")

    static_loo = results['Static'][0]
    if b[0] < static_loo:
        print(f"    Improves on static by {(b[0]/static_loo-1)*100:.1f}%")

    # Key question: did causal gate help temporal splits?
    best_splits = max(r[4] for r in results.values())
    if best_splits > results['Static'][4]:
        print(f"\n  ✓ Causal gate improved temporal splits: {best_splits}/7 vs {results['Static'][4]}/7")
    else:
        print(f"\n  Temporal splits unchanged at {best_splits}/7")

    print(f"\n{'='*72}")
    print("END SCRIPT 207")
    print(f"{'='*72}")
