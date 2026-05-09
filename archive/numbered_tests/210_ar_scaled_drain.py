#!/usr/bin/env python3
"""
Script 210 — AR-Scaled Dynamic Drain: The Sun's Own Ratio Sets Its Leak

INSIGHT (Dylan):
  The drain strength isn't fixed at 1/φ⁹. It's set by the Sun's own
  Accumulation/Release ratio FOR THAT CYCLE. The AR IS the rise fraction.

  High AR (long accumulation, slow rise, e.g. Cycle 24: 0.573):
    → More time with field building → more open flux → BIGGER drain
    → The system bleeds energy longer before peaking → lower peak

  Low AR (short accumulation, fast rise, e.g. Cycle 4: 0.250):
    → Less exposure time → SMALLER drain
    → Energy gets through faster → higher peak

  This directly attacks the Waldmeier effect because it creates a
  differential correction: slow-rising cycles lose more, fast-rising
  cycles lose less. The rise fraction correlation should drop.

  For FORWARD PREDICTION:
    We don't know the next cycle's rise fraction yet.
    But the causal gate (Script 207) gives us acc_frac = 1/(1+prev_ARA).
    That IS the predicted AR for the next cycle.
    So: prev cycle amplitude → predicted AR → drain strength.
    Fully dynamic, fully causal, no future information.

ARCHITECTURE:
  Base = 203b cascade (Mass(φ⁹) —[sawtooth gate]— Time(φ⁹))
  + AR-scaled drain: drain_frac = base_drain × f(AR_ratio)
  + Causal gate (207): past amplitude → current acc_frac → current drain

MODELS:
  V1: Oracle AR — uses OBSERVED rise fraction (upper bound, not predictive)
  V2: Linear AR drain — drain ∝ AR_ratio (longer accumulation = more drain)
  V3: φ-mapped AR drain — drain = 1/φ⁹ × (AR/0.618)^φ (nonlinear, ARA-natural)
  V4: Causal AR — previous cycle's amplitude predicts current AR and drain
  V5: Full causal — causal gate + causal AR drain (the forward-predictable model)
  V6: Causal + phase-aware — V5 but drain is also phase-asymmetric within cycle

FREE PARAMETERS: 2 (base_amp, t_ref) — same as 203b
  Drain scaling derived from AR geometry, not fitted.
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9

# Full Schwabe cycle data (25 cycles, 1755-2025)
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
MEAN_RISE_FRAC = rise_fracs.mean()  # ≈ 0.400

CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
STATIC_ACC = PHI / (PHI + 1)  # ≈ 0.618
ARA_IDEAL_ACC = STATIC_ACC    # φ/(φ+1) — the ARA-natural accumulation fraction

print(f"  Rise fraction stats: mean={MEAN_RISE_FRAC:.3f}, "
      f"std={rise_fracs.std():.3f}, min={rise_fracs.min():.3f}, "
      f"max={rise_fracs.max():.3f}")
print(f"  ARA ideal acc_frac = {ARA_IDEAL_ACC:.3f}")
print(f"  Compression ratio = {MEAN_RISE_FRAC/ARA_IDEAL_ACC:.3f} "
      f"(Sun peaks {MEAN_RISE_FRAC/ARA_IDEAL_ACC*100:.0f}% of the way to φ)")


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


def ara_to_acc(ara_value):
    """ARA → accumulation fraction. Natural ARA division."""
    return 1.0 / (1.0 + ara_value)


# =================================================================
# AR-SCALED DRAIN FUNCTIONS
# =================================================================

def ar_linear_drain(cascade_amp, ar_ratio, base_drain=INV_PHI_9):
    """V2: Linear AR drain.

    drain = base_drain × (ar_ratio / mean_ar)
    Longer accumulation (higher AR) → proportionally more drain.
    At mean AR → drain = base_drain (same as static).
    """
    ar_scale = ar_ratio / MEAN_RISE_FRAC
    return -base_drain * cascade_amp * ar_scale


def ar_phi_drain(cascade_amp, ar_ratio, base_drain=INV_PHI_9):
    """V3: φ-mapped AR drain.

    drain = base_drain × (ar_ratio / ARA_ideal)^φ
    Uses φ as the nonlinear exponent — the ARA-natural curve.
    Deviation from ideal AR (0.618) is amplified by φ.

    At AR=0.618 (ideal): scale = 1.0
    At AR=0.400 (mean):  scale = (0.400/0.618)^φ = 0.647^1.618 ≈ 0.49
    At AR=0.250 (fast):  scale = (0.250/0.618)^φ = 0.404^1.618 ≈ 0.22
    At AR=0.573 (slow):  scale = (0.573/0.618)^φ = 0.927^1.618 ≈ 0.88
    """
    ar_scale = (ar_ratio / ARA_IDEAL_ACC) ** PHI
    return -base_drain * cascade_amp * ar_scale


def ar_ara_drain(cascade_amp, ar_ratio, base_drain=INV_PHI_9):
    """V4/V5/V6: ARA-derived drain.

    The AR ratio maps to an ARA value:
      ARA_cycle = ar_ratio / (1 - ar_ratio)
    Then drain scales by where this ARA sits relative to ideal:
      drain_scale = ARA_cycle / φ

    At AR=0.618: ARA=1.618=φ, scale=1.0
    At AR=0.400: ARA=0.667, scale=0.412
    At AR=0.250: ARA=0.333, scale=0.206
    At AR=0.573: ARA=1.342, scale=0.829

    This is the natural ARA mapping — the drain IS the system's own
    ARA expressed as energy loss.
    """
    ar_clamped = max(0.05, min(0.95, ar_ratio))
    ara_cycle = ar_clamped / (1 - ar_clamped)
    drain_scale = ara_cycle / PHI
    return -base_drain * cascade_amp * drain_scale


# =================================================================
# CORE CASCADE (shared by all models)
# =================================================================

def cascade_output(t, base_amp, t_ref, acc_frac=None):
    """Run the φ⁹ cascade with configurable gate. Returns (amp, gleiss_phase)."""
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
    return amp, gleiss_phase


# =================================================================
# PREDICTION FUNCTIONS
# =================================================================

def predict_203b(t, base_amp, t_ref):
    """Baseline 203b."""
    amp, gleiss_phase = cascade_output(t, base_amp, t_ref)
    amp += base_amp * INV_PHI_9 * np.cos(gleiss_phase)
    return amp


def predict_v1_oracle(t, base_amp, t_ref, rise_frac):
    """V1: Oracle — uses actual observed rise fraction.
    Upper bound. Not usable for prediction."""
    amp, _ = cascade_output(t, base_amp, t_ref)
    amp += ar_ara_drain(amp, rise_frac)
    return amp


def predict_v2_linear(t, base_amp, t_ref, rise_frac):
    """V2: Linear AR drain."""
    amp, _ = cascade_output(t, base_amp, t_ref)
    amp += ar_linear_drain(amp, rise_frac)
    return amp


def predict_v3_phi(t, base_amp, t_ref, rise_frac):
    """V3: φ-mapped AR drain."""
    amp, _ = cascade_output(t, base_amp, t_ref)
    amp += ar_phi_drain(amp, rise_frac)
    return amp


def predict_v4_causal_ar(peak_years_seq, peak_amps_prev, durations_seq,
                          rise_fracs_prev, base_amp, t_ref):
    """V4: Causal AR drain — previous cycle's rise fraction sets drain.

    Uses observed previous rise fraction (one step back).
    This IS available for forward prediction if we model rise fraction
    from amplitude (Waldmeier correlation works in our favor here).
    """
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            prev_rf = MEAN_RISE_FRAC
        else:
            prev_rf = rise_fracs_prev[i - 1] if i - 1 < len(rise_fracs_prev) else MEAN_RISE_FRAC

        amp, _ = cascade_output(t, base_amp, t_ref)
        amp += ar_ara_drain(amp, prev_rf)
        preds.append(amp)
    return preds


def predict_v5_full_causal(peak_years_seq, peak_amps_prev, durations_seq,
                            rise_fracs_prev, base_amp, t_ref):
    """V5: Full causal — causal gate (207) + causal AR drain.

    Previous cycle amplitude → acc_frac (gate shape)
    Previous cycle rise fraction → drain strength

    Both are causally available: we know the previous cycle's
    amplitude and rise fraction before the current cycle starts.

    For TRUE forward prediction (future cycles we haven't seen):
    - acc_frac comes from predicted amplitude (self-feeding from V5)
    - rise fraction estimated from Waldmeier: fast rise ↔ high amp
    """
    preds = []
    for i, t in enumerate(peak_years_seq):
        # Causal gate from previous amplitude
        if i == 0:
            acc_frac = STATIC_ACC
            prev_rf = MEAN_RISE_FRAC
        else:
            prev_amp = peak_amps_prev[i - 1] if i - 1 < len(peak_amps_prev) else MEAN_AMP
            prev_ara = prev_amp / base_amp
            acc_frac = ara_to_acc(prev_ara)
            prev_rf = rise_fracs_prev[i - 1] if i - 1 < len(rise_fracs_prev) else MEAN_RISE_FRAC

        amp, _ = cascade_output(t, base_amp, t_ref, acc_frac)
        amp += ar_ara_drain(amp, prev_rf)
        preds.append(amp)
    return preds


def predict_v6_full_phase(peak_years_seq, peak_amps_prev, durations_seq,
                           rise_fracs_prev, base_amp, t_ref):
    """V6: Full causal + phase-aware drain.

    Same as V5 but the drain is also modulated by WHERE in the
    Gleissberg phase we are. This captures the idea that the drain
    is stronger when the Gleissberg envelope is high (more total
    energy to radiate) and weaker when low.
    """
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            acc_frac = STATIC_ACC
            prev_rf = MEAN_RISE_FRAC
        else:
            prev_amp = peak_amps_prev[i - 1] if i - 1 < len(peak_amps_prev) else MEAN_AMP
            prev_ara = prev_amp / base_amp
            acc_frac = ara_to_acc(prev_ara)
            prev_rf = rise_fracs_prev[i - 1] if i - 1 < len(rise_fracs_prev) else MEAN_RISE_FRAC

        amp, gleiss_phase = cascade_output(t, base_amp, t_ref, acc_frac)

        # AR-scaled drain
        base_drain_val = ar_ara_drain(amp, prev_rf)

        # Phase modulation: drain is stronger near Gleissberg peaks
        gleiss_envelope = 0.5 * (1 + np.cos(gleiss_phase))  # 1 at peak, 0 at trough
        phase_mod = INV_PHI + (1 - INV_PHI) * gleiss_envelope  # ranges 1/φ to 1

        amp += base_drain_val * phase_mod
        preds.append(amp)
    return preds


# =================================================================
# FITTING + EVALUATION
# =================================================================

def fit_simple(predict_fn, train_years, train_amps, train_rf=None):
    """Fit for models that take (t, base_amp, t_ref, rise_frac)."""
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


def fit_sequence(predict_fn, train_years, train_amps, all_years, all_amps,
                 all_durations, all_rise_fracs, train_mask):
    """Fit for sequence models (V4, V5, V6)."""
    best_mae, best_ba, best_tr = 1e9, 0, 0
    train_indices = np.where(train_mask)[0]

    for t_ref in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(train_amps) * 0.6,
                               np.mean(train_amps) * 1.4, 40):
            all_preds = predict_fn(all_years, all_amps, all_durations,
                                    all_rise_fracs, ba, t_ref)
            train_preds = [all_preds[j] for j in train_indices]
            m = mae(train_preds, train_amps)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


def loo_eval_simple(predict_fn, label, uses_rf=False):
    """LOO for simple (non-sequence) models."""
    phi_errors, sine_errors = [], []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        if uses_rf:
            ba_i, tr_i, _ = fit_simple(predict_fn, peak_years[mask],
                                        peak_amps[mask], rise_fracs[mask])
            pred_i = predict_fn(peak_years[i], ba_i, tr_i, rise_fracs[i])
        else:
            ba_i, tr_i, _ = fit_simple(predict_fn, peak_years[mask], peak_amps[mask])
            pred_i = predict_fn(peak_years[i], ba_i, tr_i)
        phi_errors.append(abs(pred_i - peak_amps[i]))
        sine_errors.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    phi_errors = np.array(phi_errors)
    sine_errors = np.array(sine_errors)

    # Full fit for diagnostics
    if uses_rf:
        ba_f, tr_f, _ = fit_simple(predict_fn, peak_years, peak_amps, rise_fracs)
        preds_full = [predict_fn(t, ba_f, tr_f, rf) for t, rf in zip(peak_years, rise_fracs)]
    else:
        ba_f, tr_f, _ = fit_simple(predict_fn, peak_years, peak_amps)
        preds_full = [predict_fn(t, ba_f, tr_f) for t in peak_years]

    errors_full = np.array(preds_full) - peak_amps
    rise_corr = np.corrcoef(rise_fracs, errors_full)[0, 1]
    amp_corr = np.corrcoef(peak_amps, errors_full)[0, 1]

    return {
        'label': label,
        'loo_mae': phi_errors.mean(),
        'sine_mae': sine_errors.mean(),
        'improvement': (phi_errors.mean() / sine_errors.mean() - 1) * 100,
        'n_wins': int(np.sum(phi_errors < sine_errors)),
        'rise_corr': rise_corr,
        'amp_corr': amp_corr,
        'phi_errors': phi_errors,
        'sine_errors': sine_errors,
        'ba': ba_f, 'tr': tr_f,
        'preds_full': preds_full,
    }


def loo_eval_sequence(predict_fn, label):
    """LOO for sequence models."""
    phi_errors, sine_errors = [], []
    full_mask = np.ones(N, dtype=bool)

    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        ba_i, tr_i, _ = fit_sequence(predict_fn, peak_years[mask], peak_amps[mask],
                                      peak_years, peak_amps, durations,
                                      rise_fracs, mask)
        all_preds = predict_fn(peak_years, peak_amps, durations, rise_fracs, ba_i, tr_i)
        pred_i = all_preds[i]
        phi_errors.append(abs(pred_i - peak_amps[i]))
        sine_errors.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    phi_errors = np.array(phi_errors)
    sine_errors = np.array(sine_errors)

    # Full fit
    ba_f, tr_f, _ = fit_sequence(predict_fn, peak_years, peak_amps,
                                  peak_years, peak_amps, durations,
                                  rise_fracs, full_mask)
    preds_full = predict_fn(peak_years, peak_amps, durations, rise_fracs, ba_f, tr_f)
    errors_full = np.array(preds_full) - peak_amps
    rise_corr = np.corrcoef(rise_fracs, errors_full)[0, 1]
    amp_corr = np.corrcoef(peak_amps, errors_full)[0, 1]

    return {
        'label': label,
        'loo_mae': phi_errors.mean(),
        'sine_mae': sine_errors.mean(),
        'improvement': (phi_errors.mean() / sine_errors.mean() - 1) * 100,
        'n_wins': int(np.sum(phi_errors < sine_errors)),
        'rise_corr': rise_corr,
        'amp_corr': amp_corr,
        'phi_errors': phi_errors,
        'sine_errors': sine_errors,
        'ba': ba_f, 'tr': tr_f,
        'preds_full': preds_full,
    }


def temporal_splits_simple(predict_fn, label, uses_rf=False):
    """Temporal splits for simple models."""
    wins = 0
    results = []
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N:
            continue
        if uses_rf:
            ba_s, tr_s, _ = fit_simple(predict_fn, peak_years[:n_train],
                                        peak_amps[:n_train], rise_fracs[:n_train])
            test_preds = [predict_fn(t, ba_s, tr_s, rf)
                          for t, rf in zip(peak_years[n_train:], rise_fracs[n_train:])]
        else:
            ba_s, tr_s, _ = fit_simple(predict_fn, peak_years[:n_train], peak_amps[:n_train])
            test_preds = [predict_fn(t, ba_s, tr_s) for t in peak_years[n_train:]]
        test_amps = peak_amps[n_train:]
        phi_m = mae(test_preds, test_amps)
        sine_m = mae(np.full(len(test_amps), peak_amps[:n_train].mean()), test_amps)
        w = "φ" if phi_m < sine_m else "sine"
        if phi_m < sine_m:
            wins += 1
        results.append((n_train, N - n_train, phi_m, sine_m, w))
    return wins, results


def temporal_splits_sequence(predict_fn, label):
    """Temporal splits for sequence models."""
    wins = 0
    results = []
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N:
            continue
        train_mask = np.zeros(N, dtype=bool)
        train_mask[:n_train] = True
        ba_s, tr_s, _ = fit_sequence(predict_fn, peak_years[:n_train],
                                      peak_amps[:n_train], peak_years, peak_amps,
                                      durations, rise_fracs, train_mask)
        all_preds = predict_fn(peak_years, peak_amps, durations, rise_fracs, ba_s, tr_s)
        test_preds = all_preds[n_train:]
        test_amps = peak_amps[n_train:]
        phi_m = mae(test_preds, test_amps)
        sine_m = mae(np.full(len(test_amps), peak_amps[:n_train].mean()), test_amps)
        w = "φ" if phi_m < sine_m else "sine"
        if phi_m < sine_m:
            wins += 1
        results.append((n_train, N - n_train, phi_m, sine_m, w))
    return wins, results


# =================================================================
# MAIN
# =================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("SCRIPT 210 — AR-SCALED DYNAMIC DRAIN")
    print("=" * 70)

    print(f"""
  The Sun's drain strength = f(its own AR ratio for that cycle).
  AR ratio = rise_fraction = accumulation_time / total_duration.

  High AR (slow rise) → more time bleeding → bigger drain
  Low AR (fast rise) → less exposure → smaller drain

  This should DIFFERENTIALLY correct the Waldmeier distortion:
  fast-rising high-amplitude cycles get less drain penalty,
  slow-rising low-amplitude cycles get more.

  AR drain mapping: ARA_cycle = AR/(1-AR), drain_scale = ARA_cycle/φ
  At AR=0.618 (ideal): drain_scale = 1.0 (full 1/φ⁹)
  At AR=0.400 (mean):  drain_scale = 0.412
  At AR=0.250 (fast):  drain_scale = 0.206
  At AR=0.573 (slow):  drain_scale = 0.829

  Free parameters: 2 (base_amp, t_ref)
    """)

    # === BASELINE ===
    print(f"\n{'='*70}")
    print("BASELINE — 203b")
    print(f"{'='*70}")
    r0 = loo_eval_simple(predict_203b, "203b baseline")
    print(f"  LOO MAE = {r0['loo_mae']:.2f} ({r0['improvement']:+.1f}%)")
    print(f"  Wins: {r0['n_wins']}/25")
    print(f"  Rise frac r = {r0['rise_corr']:+.3f}, Amp r = {r0['amp_corr']:+.3f}")

    w0, s0 = temporal_splits_simple(predict_203b, "203b")
    print(f"  Temporal splits: {w0}/7")

    # === V1: Oracle AR ===
    print(f"\n{'='*70}")
    print("V1 — ORACLE AR DRAIN (uses observed rise fraction — upper bound)")
    print(f"{'='*70}")
    r1 = loo_eval_simple(predict_v1_oracle, "V1 oracle AR", uses_rf=True)
    print(f"  LOO MAE = {r1['loo_mae']:.2f} ({r1['improvement']:+.1f}%)")
    print(f"  Wins: {r1['n_wins']}/25")
    print(f"  Rise frac r = {r1['rise_corr']:+.3f}, Amp r = {r1['amp_corr']:+.3f}")

    # === V2: Linear AR ===
    print(f"\n{'='*70}")
    print("V2 — LINEAR AR DRAIN")
    print(f"{'='*70}")
    r2 = loo_eval_simple(predict_v2_linear, "V2 linear AR", uses_rf=True)
    print(f"  LOO MAE = {r2['loo_mae']:.2f} ({r2['improvement']:+.1f}%)")
    print(f"  Wins: {r2['n_wins']}/25")
    print(f"  Rise frac r = {r2['rise_corr']:+.3f}, Amp r = {r2['amp_corr']:+.3f}")

    # === V3: φ-mapped AR ===
    print(f"\n{'='*70}")
    print("V3 — φ-MAPPED AR DRAIN (nonlinear, ARA-natural)")
    print(f"{'='*70}")
    r3 = loo_eval_simple(predict_v3_phi, "V3 φ-mapped AR", uses_rf=True)
    print(f"  LOO MAE = {r3['loo_mae']:.2f} ({r3['improvement']:+.1f}%)")
    print(f"  Wins: {r3['n_wins']}/25")
    print(f"  Rise frac r = {r3['rise_corr']:+.3f}, Amp r = {r3['amp_corr']:+.3f}")

    # === V4: Causal AR ===
    print(f"\n{'='*70}")
    print("V4 — CAUSAL AR DRAIN (previous cycle's rise fraction)")
    print(f"{'='*70}")
    r4 = loo_eval_sequence(predict_v4_causal_ar, "V4 causal AR")
    print(f"  LOO MAE = {r4['loo_mae']:.2f} ({r4['improvement']:+.1f}%)")
    print(f"  Wins: {r4['n_wins']}/25")
    print(f"  Rise frac r = {r4['rise_corr']:+.3f}, Amp r = {r4['amp_corr']:+.3f}")

    # === V5: Full causal ===
    print(f"\n{'='*70}")
    print("V5 — FULL CAUSAL (gate from 207 + AR drain)")
    print(f"{'='*70}")
    r5 = loo_eval_sequence(predict_v5_full_causal, "V5 full causal")
    print(f"  LOO MAE = {r5['loo_mae']:.2f} ({r5['improvement']:+.1f}%)")
    print(f"  Wins: {r5['n_wins']}/25")
    print(f"  Rise frac r = {r5['rise_corr']:+.3f}, Amp r = {r5['amp_corr']:+.3f}")

    w5, s5 = temporal_splits_sequence(predict_v5_full_causal, "V5")
    print(f"  Temporal splits: {w5}/7")
    for nt, ntest, pm, sm, w in s5:
        print(f"    Train {nt:2d} / Test {ntest:2d}: φ={pm:.1f}  sine={sm:.1f}  → {w}")

    # === V6: Full causal + phase ===
    print(f"\n{'='*70}")
    print("V6 — FULL CAUSAL + GLEISSBERG PHASE MODULATION")
    print(f"{'='*70}")
    r6 = loo_eval_sequence(predict_v6_full_phase, "V6 causal+phase")
    print(f"  LOO MAE = {r6['loo_mae']:.2f} ({r6['improvement']:+.1f}%)")
    print(f"  Wins: {r6['n_wins']}/25")
    print(f"  Rise frac r = {r6['rise_corr']:+.3f}, Amp r = {r6['amp_corr']:+.3f}")

    w6, s6 = temporal_splits_sequence(predict_v6_full_phase, "V6")
    print(f"  Temporal splits: {w6}/7")
    for nt, ntest, pm, sm, w in s6:
        print(f"    Train {nt:2d} / Test {ntest:2d}: φ={pm:.1f}  sine={sm:.1f}  → {w}")

    # === COMPARISON TABLE ===
    print(f"\n{'='*70}")
    print("COMPARISON — ALL MODELS")
    print(f"{'='*70}")

    all_results = [r0, r1, r2, r3, r4, r5, r6]

    print(f"\n  {'Model':<22s} {'LOO MAE':>8s} {'vs sine':>8s} {'Wins':>5s} "
          f"{'Rise r':>7s} {'Amp r':>7s}")
    print(f"  {'-'*22} {'-'*8} {'-'*8} {'-'*5} {'-'*7} {'-'*7}")

    for r in all_results:
        print(f"  {r['label']:<22s} {r['loo_mae']:8.2f} {r['improvement']:+7.1f}% "
              f"{r['n_wins']:3d}/25 {r['rise_corr']:+7.3f} {r['amp_corr']:+7.3f}")

    best_loo = min(all_results, key=lambda r: r['loo_mae'])
    best_wald = min(all_results, key=lambda r: abs(r['rise_corr']))

    print(f"\n  BEST LOO: {best_loo['label']} (MAE={best_loo['loo_mae']:.2f}, "
          f"{best_loo['improvement']:+.1f}%)")
    print(f"  BEST WALDMEIER: {best_wald['label']} "
          f"(rise r={best_wald['rise_corr']:+.3f})")

    # === PER-CYCLE DIAGNOSTIC ===
    print(f"\n{'='*70}")
    print("PER-CYCLE DIAGNOSTIC — BEST MODEL vs 203b vs ORACLE")
    print(f"{'='*70}")

    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'203b':>7s} {'Best':>7s} {'Oracle':>7s} "
          f"{'RF':>6s} {'203b_e':>7s} {'Best_e':>7s} {'Orac_e':>7s}")

    for i, c in enumerate(cycle_nums):
        p0 = r0['preds_full'][i]
        pb = best_loo['preds_full'][i]
        p1 = r1['preds_full'][i]
        obs = peak_amps[i]
        print(f"  {c:3d} {obs:7.1f} {p0:7.1f} {pb:7.1f} {p1:7.1f} "
              f"{rise_fracs[i]:6.3f} {p0-obs:+7.1f} {pb-obs:+7.1f} {p1-obs:+7.1f}")

    # === WALDMEIER SCATTER ===
    print(f"\n{'='*70}")
    print("WALDMEIER ANALYSIS — ERROR vs RISE FRACTION")
    print(f"{'='*70}")

    print(f"\n  203b rise corr:  {r0['rise_corr']:+.3f}")
    print(f"  Oracle rise corr: {r1['rise_corr']:+.3f}")
    print(f"  Best rise corr:   {best_loo['rise_corr']:+.3f}")
    print(f"  Best Wald:        {best_wald['rise_corr']:+.3f}")

    # Group by rise fraction to show the pattern
    fast = rise_fracs < 0.35
    medium = (rise_fracs >= 0.35) & (rise_fracs < 0.45)
    slow = rise_fracs >= 0.45

    for label, mask in [("Fast (<0.35)", fast), ("Medium (0.35-0.45)", medium),
                         ("Slow (>0.45)", slow)]:
        n = mask.sum()
        if n == 0:
            continue
        err_203b = np.mean(np.abs(np.array(r0['preds_full'])[mask] - peak_amps[mask]))
        err_best = np.mean(np.abs(np.array(best_loo['preds_full'])[mask] - peak_amps[mask]))
        err_orac = np.mean(np.abs(np.array(r1['preds_full'])[mask] - peak_amps[mask]))
        print(f"\n  {label} (n={n}):")
        print(f"    203b MAE:   {err_203b:.1f}")
        print(f"    Best MAE:   {err_best:.1f}")
        print(f"    Oracle MAE: {err_orac:.1f}")

    # === SUMMARY ===
    print(f"\n{'='*70}")
    print("SUMMARY — SCRIPT 210")
    print(f"{'='*70}")
    print(f"""
  CONCEPT: The Sun's drain strength is set by its own AR ratio.
  AR ratio = rise_fraction = how asymmetric this cycle is.

  DRAIN MAPPING: ARA_cycle = AR/(1-AR), drain_scale = ARA_cycle/φ
  This is dynamic and generalizable to any system.

  BEST LOO: {best_loo['label']}
    MAE = {best_loo['loo_mae']:.2f} ({best_loo['improvement']:+.1f}% vs sine)
    Wins: {best_loo['n_wins']}/25
    Rise frac r = {best_loo['rise_corr']:+.3f}

  WALDMEIER REDUCTION:
    203b baseline:    r = {r0['rise_corr']:+.3f}
    Oracle AR drain:  r = {r1['rise_corr']:+.3f}
    Best model:       r = {best_loo['rise_corr']:+.3f}

  FORWARD PREDICTION PATH:
    For unknown future cycles:
    1. Previous cycle amplitude → acc_frac = 1/(1+ARA)
    2. Previous cycle rise fraction → drain_scale = ARA_cycle/φ
    3. Both are causally available before next cycle starts
    4. For systems where rise fraction isn't measured:
       Use Waldmeier relation to estimate from amplitude
""")
