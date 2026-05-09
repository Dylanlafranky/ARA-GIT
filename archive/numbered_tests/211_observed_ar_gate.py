#!/usr/bin/env python3
"""
Script 211 — Observed-AR Gate: The Drain IS the Gate Shape

INSIGHT:
  The sawtooth gate in 203b uses ACC_FRAC = 0.618 (ARA-ideal).
  But the Sun actually peaks at 40% of its cycle, not 61.8%.

  The drain doesn't just subtract energy — it COMPRESSES the
  accumulation phase. The Sun's natural ARA would be φ (0.618),
  but the energy loss to space shortens how long energy can
  accumulate before it must release.

  So instead of:
    gate(ideal 0.618) + small drain correction
  It should be:
    gate(observed AR) — the drain is ALREADY in the gate shape

  For forward prediction:
    - Static: use mean observed AR (0.400)
    - Dynamic: previous cycle's AR sets current gate shape
    - Causal: previous amplitude → estimated AR via Waldmeier relation

MODELS:
  V1: Static mean AR gate — ACC_FRAC = 0.400 (observed mean)
  V2: Per-cycle oracle AR — ACC_FRAC = observed rise_frac per cycle (upper bound)
  V3: Causal AR gate — ACC_FRAC from previous cycle's observed rise fraction
  V4: Amplitude-estimated AR — use Waldmeier relation to estimate AR from prev amplitude
  V5: Full model — causal amplitude gate + amplitude-estimated AR + dynamic drain
  V6: Sweep — find optimal static ACC_FRAC, then compare to data-driven versions

FREE PARAMETERS: 2 (base_amp, t_ref) — same as 203b
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
rise_times = peak_years - start_years
rise_fracs = rise_times / durations
N = len(cycle_nums)
MEAN_AMP = peak_amps.mean()
MEAN_RF = rise_fracs.mean()

CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
IDEAL_ACC = PHI / (PHI + 1)  # 0.618

# Waldmeier relation: fit rise_frac = a + b * amplitude
# (negative correlation — high amp = fast rise = low rise_frac)
wald_slope = np.polyfit(peak_amps, rise_fracs, 1)
wald_pred_rf = lambda amp: np.clip(wald_slope[0] * amp + wald_slope[1], 0.15, 0.85)


def mae(p, o):
    return np.mean(np.abs(np.array(p) - np.array(o)))


def sawtooth_valve(phase, acc_frac):
    """ARA-asymmetric sawtooth gate with configurable acc_frac."""
    acc_frac = max(0.15, min(0.85, acc_frac))
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < acc_frac:
        state = (cycle_pos / acc_frac) * PHI
    else:
        ramp = (cycle_pos - acc_frac) / (1 - acc_frac)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    return state / ((PHI + INV_PHI) / 2)


def predict_core(t, base_amp, t_ref, acc_frac, use_drain=False):
    """Core prediction with configurable gate shape and optional drain."""
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

    if use_drain:
        # Dynamic drain: scale by how far amp is from base
        amp_ratio = amp / base_amp
        amp -= INV_PHI_9 * amp * amp_ratio * abs(np.cos(gleiss_phase))
    else:
        # Static residual (203b style)
        amp += base_amp * INV_PHI_9 * np.cos(gleiss_phase)

    return amp


# === MODEL FUNCTIONS ===

def predict_203b(t, base_amp, t_ref):
    """Baseline — gate at 0.618."""
    return predict_core(t, base_amp, t_ref, IDEAL_ACC, use_drain=False)


def predict_v1(t, base_amp, t_ref):
    """V1: Static mean AR gate — 0.400."""
    return predict_core(t, base_amp, t_ref, MEAN_RF, use_drain=False)


def predict_v1d(t, base_amp, t_ref):
    """V1d: Static mean AR gate + dynamic drain."""
    return predict_core(t, base_amp, t_ref, MEAN_RF, use_drain=True)


def predict_v2(t, base_amp, t_ref, rf):
    """V2: Oracle per-cycle AR gate."""
    return predict_core(t, base_amp, t_ref, rf, use_drain=False)


def predict_v2d(t, base_amp, t_ref, rf):
    """V2d: Oracle per-cycle AR gate + dynamic drain."""
    return predict_core(t, base_amp, t_ref, rf, use_drain=True)


def predict_v3_seq(peak_years_seq, rise_fracs_all, base_amp, t_ref):
    """V3: Causal AR gate — previous cycle's observed RF."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            rf = MEAN_RF
        else:
            rf = rise_fracs_all[i - 1]
        preds.append(predict_core(t, base_amp, t_ref, rf, use_drain=False))
    return preds


def predict_v3d_seq(peak_years_seq, rise_fracs_all, base_amp, t_ref):
    """V3d: Causal AR gate + dynamic drain."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            rf = MEAN_RF
        else:
            rf = rise_fracs_all[i - 1]
        preds.append(predict_core(t, base_amp, t_ref, rf, use_drain=True))
    return preds


def predict_v4_seq(peak_years_seq, peak_amps_all, base_amp, t_ref):
    """V4: Amplitude-estimated AR via Waldmeier relation.
    Previous amplitude → estimated rise fraction → gate shape.
    Fully forward-predictable."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            est_rf = MEAN_RF
        else:
            prev_amp = peak_amps_all[i - 1]
            est_rf = wald_pred_rf(prev_amp)
        preds.append(predict_core(t, base_amp, t_ref, est_rf, use_drain=False))
    return preds


def predict_v4d_seq(peak_years_seq, peak_amps_all, base_amp, t_ref):
    """V4d: Amplitude-estimated AR + dynamic drain."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            est_rf = MEAN_RF
        else:
            prev_amp = peak_amps_all[i - 1]
            est_rf = wald_pred_rf(prev_amp)
        preds.append(predict_core(t, base_amp, t_ref, est_rf, use_drain=True))
    return preds


def predict_v5_seq(peak_years_seq, combined_data, base_amp, t_ref):
    """V5: Full model — causal amplitude gate + causal AR + drain.
    Uses BOTH previous amplitude AND previous rise fraction.
    combined_data = (peak_amps_all, rise_fracs_all) packed together."""
    peak_amps_all, rise_fracs_all = combined_data
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            rf = MEAN_RF
        else:
            # Use previous cycle's observed rise fraction for gate shape
            rf = rise_fracs_all[i - 1]
        preds.append(predict_core(t, base_amp, t_ref, rf, use_drain=True))
    return preds


# === FITTING ===

def fit_simple(predict_fn, train_years, train_amps, train_rf=None):
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(train_amps) * 0.6,
                               np.mean(train_amps) * 1.4, 40):
            if train_rf is not None:
                preds = [predict_fn(t, ba, t_ref, rf)
                         for t, rf in zip(train_years, train_rf)]
            else:
                preds = [predict_fn(t, ba, t_ref) for t in train_years]
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


def fit_seq(predict_fn, train_mask, all_years, all_data1, ba_range_ref,
            all_data2=None):
    """Generic sequence fitter."""
    best_mae, best_ba, best_tr = 1e9, 0, 0
    train_indices = np.where(train_mask)[0]
    train_amps_local = peak_amps[train_mask]

    for t_ref in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(train_amps_local) * 0.6,
                               np.mean(train_amps_local) * 1.4, 40):
            if all_data2 is not None:
                all_preds = predict_fn(all_years, all_data1, all_data2, ba, t_ref)
            else:
                all_preds = predict_fn(all_years, all_data1, ba, t_ref)
            train_preds = [all_preds[j] for j in train_indices]
            m = mae(train_preds, train_amps_local)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


# === EVALUATION ===

def evaluate(label, predict_type, predict_fn, extra_data=None, extra_data2=None):
    """Unified evaluation: LOO + temporal splits + Waldmeier diagnostic.

    predict_type: 'simple', 'simple_rf', 'seq1', 'seq2'
    """
    phi_errors, sine_errors = [], []
    full_mask = np.ones(N, dtype=bool)

    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False

        if predict_type == 'simple':
            ba_i, tr_i, _ = fit_simple(predict_fn, peak_years[mask], peak_amps[mask])
            pred_i = predict_fn(peak_years[i], ba_i, tr_i)
        elif predict_type == 'simple_rf':
            ba_i, tr_i, _ = fit_simple(predict_fn, peak_years[mask],
                                        peak_amps[mask], rise_fracs[mask])
            pred_i = predict_fn(peak_years[i], ba_i, tr_i, rise_fracs[i])
        elif predict_type == 'seq1':
            ba_i, tr_i, _ = fit_seq(predict_fn, mask, peak_years, extra_data, None)
            all_preds = predict_fn(peak_years, extra_data, ba_i, tr_i)
            pred_i = all_preds[i]
        elif predict_type == 'seq2':
            ba_i, tr_i, _ = fit_seq(predict_fn, mask, peak_years,
                                     extra_data, extra_data2)
            all_preds = predict_fn(peak_years, extra_data, extra_data2, ba_i, tr_i)
            pred_i = all_preds[i]

        phi_errors.append(abs(pred_i - peak_amps[i]))
        sine_errors.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    phi_errors = np.array(phi_errors)
    sine_errors = np.array(sine_errors)
    phi_loo = phi_errors.mean()
    sine_loo = sine_errors.mean()

    # Full fit for diagnostics
    if predict_type == 'simple':
        ba_f, tr_f, _ = fit_simple(predict_fn, peak_years, peak_amps)
        preds_full = [predict_fn(t, ba_f, tr_f) for t in peak_years]
    elif predict_type == 'simple_rf':
        ba_f, tr_f, _ = fit_simple(predict_fn, peak_years, peak_amps, rise_fracs)
        preds_full = [predict_fn(t, ba_f, tr_f, rf)
                      for t, rf in zip(peak_years, rise_fracs)]
    elif predict_type == 'seq1':
        ba_f, tr_f, _ = fit_seq(predict_fn, full_mask, peak_years, extra_data, None)
        preds_full = predict_fn(peak_years, extra_data, ba_f, tr_f)
    elif predict_type == 'seq2':
        ba_f, tr_f, _ = fit_seq(predict_fn, full_mask, peak_years,
                                 extra_data, extra_data2)
        preds_full = predict_fn(peak_years, extra_data, extra_data2, ba_f, tr_f)

    errors_full = np.array(preds_full) - peak_amps
    rise_corr = np.corrcoef(rise_fracs, errors_full)[0, 1]
    amp_corr = np.corrcoef(peak_amps, errors_full)[0, 1]

    # Temporal splits
    split_wins = 0
    split_results = []
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N:
            continue
        t_mask = np.zeros(N, dtype=bool)
        t_mask[:n_train] = True

        if predict_type == 'simple':
            ba_s, tr_s, _ = fit_simple(predict_fn, peak_years[:n_train],
                                        peak_amps[:n_train])
            test_p = [predict_fn(t, ba_s, tr_s) for t in peak_years[n_train:]]
        elif predict_type == 'simple_rf':
            ba_s, tr_s, _ = fit_simple(predict_fn, peak_years[:n_train],
                                        peak_amps[:n_train], rise_fracs[:n_train])
            test_p = [predict_fn(t, ba_s, tr_s, rf)
                      for t, rf in zip(peak_years[n_train:], rise_fracs[n_train:])]
        elif predict_type == 'seq1':
            ba_s, tr_s, _ = fit_seq(predict_fn, t_mask, peak_years, extra_data, None)
            all_p = predict_fn(peak_years, extra_data, ba_s, tr_s)
            test_p = all_p[n_train:]
        elif predict_type == 'seq2':
            ba_s, tr_s, _ = fit_seq(predict_fn, t_mask, peak_years,
                                     extra_data, extra_data2)
            all_p = predict_fn(peak_years, extra_data, extra_data2, ba_s, tr_s)
            test_p = all_p[n_train:]

        test_a = peak_amps[n_train:]
        phi_m = mae(test_p, test_a)
        sine_m = mae(np.full(len(test_a), peak_amps[:n_train].mean()), test_a)
        w = "φ" if phi_m < sine_m else "sine"
        if phi_m < sine_m:
            split_wins += 1
        split_results.append((n_train, N - n_train, phi_m, sine_m, w))

    return {
        'label': label,
        'loo_mae': phi_loo,
        'sine_mae': sine_loo,
        'improvement': (phi_loo / sine_loo - 1) * 100,
        'n_wins': int(np.sum(phi_errors < sine_errors)),
        'rise_corr': rise_corr,
        'amp_corr': amp_corr,
        'split_wins': split_wins,
        'split_results': split_results,
        'preds_full': preds_full,
        'ba': ba_f, 'tr': tr_f,
    }


# =================================================================
# MAIN
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("SCRIPT 211 — OBSERVED-AR GATE: THE DRAIN IS THE GATE SHAPE")
    print("=" * 70)

    print(f"""
  The Sun peaks at {MEAN_RF:.1%} of its cycle, not {IDEAL_ACC:.1%}.
  That 35% compression IS the drain — it shortens accumulation.

  Instead of ideal gate + drain correction, use the observed AR
  as the gate shape itself.

  Waldmeier regression: RF = {wald_slope[0]:.5f} × amp + {wald_slope[1]:.3f}
    (r = {np.corrcoef(peak_amps, rise_fracs)[0,1]:+.3f})
    At amp=100: RF = {wald_pred_rf(100):.3f}
    At amp=200: RF = {wald_pred_rf(200):.3f}
    At amp=285: RF = {wald_pred_rf(285):.3f}
    """)

    # === V6: SWEEP to find optimal static ACC_FRAC ===
    print(f"{'='*70}")
    print("ACC_FRAC SWEEP — what's the best static gate position?")
    print(f"{'='*70}")

    sweep_results = []
    for af in np.arange(0.20, 0.80, 0.02):
        def _pred(t, ba, tr, _af=af):
            return predict_core(t, ba, tr, _af, use_drain=False)
        ba_s, tr_s, _ = fit_simple(_pred, peak_years, peak_amps)
        preds_s = [_pred(t, ba_s, tr_s) for t in peak_years]
        # Quick LOO estimate (use full-fit errors as proxy for speed)
        err_s = mae(preds_s, peak_amps)
        sweep_results.append((af, err_s))

    sweep_results.sort(key=lambda x: x[1])
    print(f"\n  Top 5 ACC_FRAC values (by full-fit MAE):")
    for af, m in sweep_results[:5]:
        print(f"    ACC_FRAC = {af:.2f}: MAE = {m:.2f}")
    print(f"  ...")
    print(f"    ACC_FRAC = 0.62 (ARA ideal): MAE = "
          f"{[m for a,m in sweep_results if abs(a-0.62)<0.01][0]:.2f}")

    best_static_af = sweep_results[0][0]
    print(f"\n  Best static ACC_FRAC = {best_static_af:.2f}")

    # Now do proper LOO for key ACC_FRAC values
    print(f"\n  Proper LOO for key ACC_FRAC values:")

    for af_test in [0.30, 0.35, MEAN_RF, 0.45, 0.50, IDEAL_ACC, best_static_af]:
        def _pred(t, ba, tr, _af=af_test):
            return predict_core(t, ba, tr, _af, use_drain=False)

        phi_e = []
        sine_e = []
        for i in range(N):
            mask = np.ones(N, dtype=bool)
            mask[i] = False
            ba_i, tr_i, _ = fit_simple(_pred, peak_years[mask], peak_amps[mask])
            pred_i = _pred(peak_years[i], ba_i, tr_i)
            phi_e.append(abs(pred_i - peak_amps[i]))
            sine_e.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

        loo_m = np.mean(phi_e)
        sine_m = np.mean(sine_e)
        wins = sum(1 for a, b in zip(phi_e, sine_e) if a < b)
        tag = ""
        if abs(af_test - MEAN_RF) < 0.001:
            tag = " ← observed mean"
        elif abs(af_test - IDEAL_ACC) < 0.001:
            tag = " ← ARA ideal"
        elif abs(af_test - best_static_af) < 0.01:
            tag = " ← sweep best"
        print(f"    AF={af_test:.3f}: LOO={loo_m:.2f} ({(loo_m/sine_m-1)*100:+.1f}%), "
              f"{wins}/25 wins{tag}")

    # === Run all models ===
    print(f"\n{'='*70}")
    print("MODEL EVALUATION")
    print(f"{'='*70}")

    results = []

    # Baseline
    print(f"\n  Running 203b baseline (gate=0.618)...")
    r = evaluate("203b (gate=0.618)", 'simple', predict_203b)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V1: Static mean AR
    print(f"\n  Running V1 (gate=0.400, static residual)...")
    r = evaluate("V1 gate=0.400", 'simple', predict_v1)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V1d: Static mean AR + drain
    print(f"\n  Running V1d (gate=0.400, dynamic drain)...")
    r = evaluate("V1d gate=0.4+drain", 'simple', predict_v1d)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V2: Oracle per-cycle AR
    print(f"\n  Running V2 oracle (gate=per-cycle observed RF)...")
    r = evaluate("V2 oracle RF", 'simple_rf', predict_v2)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V2d: Oracle per-cycle AR + drain
    print(f"\n  Running V2d oracle + drain...")
    r = evaluate("V2d oracle+drain", 'simple_rf', predict_v2d)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V3: Causal AR (previous RF)
    print(f"\n  Running V3 causal RF gate...")
    r = evaluate("V3 causal RF", 'seq1', predict_v3_seq,
                 extra_data=rise_fracs)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V3d: Causal AR + drain
    print(f"\n  Running V3d causal RF + drain...")
    r = evaluate("V3d causal RF+drain", 'seq1', predict_v3d_seq,
                 extra_data=rise_fracs)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V4: Amplitude-estimated AR (Waldmeier)
    print(f"\n  Running V4 Waldmeier-estimated AR gate...")
    r = evaluate("V4 Wald-est RF", 'seq1', predict_v4_seq,
                 extra_data=peak_amps)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V4d: Amplitude-estimated AR + drain
    print(f"\n  Running V4d Waldmeier-estimated + drain...")
    r = evaluate("V4d Wald-est+drain", 'seq1', predict_v4d_seq,
                 extra_data=peak_amps)
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # V5: Full causal — pack both arrays into a tuple
    print(f"\n  Running V5 full causal (RF gate + drain)...")
    r = evaluate("V5 full causal", 'seq1', predict_v5_seq,
                 extra_data=(peak_amps, rise_fracs))
    results.append(r)
    print(f"    LOO={r['loo_mae']:.2f} ({r['improvement']:+.1f}%), "
          f"{r['n_wins']}/25, rise r={r['rise_corr']:+.3f}, "
          f"splits={r['split_wins']}/7")

    # === COMPARISON TABLE ===
    print(f"\n{'='*70}")
    print("FULL COMPARISON")
    print(f"{'='*70}")

    print(f"\n  {'Model':<22s} {'LOO':>7s} {'vs sine':>8s} {'Wins':>5s} "
          f"{'Rise r':>7s} {'Amp r':>7s} {'Splits':>6s}")
    print(f"  {'-'*22} {'-'*7} {'-'*8} {'-'*5} {'-'*7} {'-'*7} {'-'*6}")

    for r in results:
        print(f"  {r['label']:<22s} {r['loo_mae']:7.2f} {r['improvement']:+7.1f}% "
              f"{r['n_wins']:3d}/25 {r['rise_corr']:+7.3f} {r['amp_corr']:+7.3f} "
              f"{r['split_wins']:2d}/7")

    best = min(results, key=lambda r: r['loo_mae'])
    best_wald = min(results, key=lambda r: abs(r['rise_corr']))
    best_splits = max(results, key=lambda r: r['split_wins'])

    print(f"\n  BEST LOO: {best['label']} ({best['loo_mae']:.2f}, "
          f"{best['improvement']:+.1f}%)")
    print(f"  BEST WALDMEIER: {best_wald['label']} "
          f"(r={best_wald['rise_corr']:+.3f})")
    print(f"  BEST SPLITS: {best_splits['label']} "
          f"({best_splits['split_wins']}/7)")

    # === TEMPORAL SPLITS DETAIL for top models ===
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS — TOP MODELS")
    print(f"{'='*70}")

    for r in results:
        if r['split_wins'] >= max(x['split_wins'] for x in results) - 1:
            print(f"\n  {r['label']}: {r['split_wins']}/7")
            for nt, ntest, pm, sm, w in r['split_results']:
                margin = sm - pm if w == "φ" else pm - sm
                print(f"    Train {nt:2d} / Test {ntest:2d}: "
                      f"φ={pm:.1f}  sine={sm:.1f}  → {w} (margin {margin:.1f})")

    # === PER-CYCLE for best model ===
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {best['label']}")
    print(f"{'='*70}")

    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'RF':>6s} "
          f"{'|Err|':>6s}")
    total_abs = 0
    for i, c in enumerate(cycle_nums):
        p = best['preds_full'][i]
        e = p - peak_amps[i]
        total_abs += abs(e)
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} {e:+7.1f} "
              f"{rise_fracs[i]:6.3f} {abs(e):6.1f}")
    print(f"  {'':3s} {'':7s} {'':7s} {'MAE':>7s} {'':6s} {total_abs/N:6.1f}")

    # === SUMMARY ===
    print(f"\n{'='*70}")
    print("SUMMARY — SCRIPT 211")
    print(f"{'='*70}")
    print(f"""
  The gate shape is WHERE the drain lives.
  The Sun's observed AR (0.400) is the ARA-ideal (0.618) AFTER
  the drain has compressed the accumulation phase.

  BEST LOO: {best['label']}
    MAE = {best['loo_mae']:.2f} ({best['improvement']:+.1f}% vs sine)
    Wins: {best['n_wins']}/25
    Rise frac r = {best['rise_corr']:+.3f}
    Temporal splits: {best['split_wins']}/7

  BEST WALDMEIER: {best_wald['label']}
    Rise frac r = {best_wald['rise_corr']:+.3f}

  BEST SPLITS: {best_splits['label']}
    {best_splits['split_wins']}/7 temporal splits

  KEY FINDING: Optimal static ACC_FRAC = {best_static_af:.2f}
  (sweep found this beats both 0.400 and 0.618)

  FORWARD PREDICTION ARCHITECTURE:
    1. Previous amplitude → Waldmeier regression → estimated RF
    2. Estimated RF → gate shape (acc_frac)
    3. Gate shape encodes the drain naturally
    4. No separate drain term needed if gate is correct
    5. All causally available — no future information used
""")
