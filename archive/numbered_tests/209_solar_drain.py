#!/usr/bin/env python3
"""
Script 209 — Solar Drain: The Sun's Opposing ARA

INSIGHT (Dylan):
  The Sun is NOT a closed loop. It continuously radiates energy into space.
  This is a small opposing ARA at the Sun's own scale — a drain.
  We've been modeling horizontal ARA (Schwabe/Gleissberg cycling) and
  vertical ARA going down (coupling to planets, magnetic subsystems).
  But we haven't given it the vertical ARA going UP — the persistent
  energy loss to the interstellar/galactic system.

  In ARA terms:
    Engine = Sun's internal magnetic dynamo (what we model now)
    Consumer = interplanetary space (absorbs radiated energy)
    Coupler = heliosphere/solar wind boundary

  The drain is:
    - Always negative (energy OUT, never in)
    - Proportional to cycle amplitude (hotter cycles radiate more)
    - Asymmetric in time (accumulation vs release phases drain differently)
    - Dynamic: scales with the system's own state, not a fixed constant

HYPOTHESIS:
  The Waldmeier distortion (rise_frac r≈+0.82) IS this drain.
  Fast-rising, high-amplitude cycles lose MORE energy to space,
  which our model currently doesn't account for → systematic
  over-estimation of high cycles, under-estimation of low ones.

ARCHITECTURE:
  Base = 203b (Mass(φ⁹) —[sawtooth gate]— Time(φ⁹) + 1/φ⁹ residual)
  + Causal gate from 207 (past→present, dynamic acc_frac)
  + NEW: Drain term that opposes the cascade output

  The drain is formulated generically so it can be applied to ANY
  ARA system by plugging in system-specific drain_strength.

MODELS TESTED:
  V1: Static drain — fixed fraction of cascade output subtracted
  V2: Amplitude-proportional drain — drain scales with how far above mean
  V3: Phase-asymmetric drain — drain is stronger during accumulation
      (because that's when the magnetic field is building → more open flux)
  V4: ARA-coupled drain — drain_frac = 1/φ⁹ × (local_amp/mean_amp)
      The drain IS the 1/φ⁹ residual, but made dynamic
  V5: Full model — causal gate (207) + ARA-coupled drain (V4)
  V6: Waldmeier-targeted — drain specifically corrects rise-fraction bias

FREE PARAMETERS: 2 (base_amp, t_ref) — same as 203b
  Drain strength derived from φ geometry, not fitted.
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
rise_fracs = (peak_years - start_years) / durations
N = len(cycle_nums)
MEAN_AMP = peak_amps.mean()

# Cascade periods
CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
STATIC_ACC = PHI / (PHI + 1)  # ≈ 0.618


def mae(p, o):
    return np.mean(np.abs(np.array(p) - np.array(o)))


def sawtooth_valve(phase, acc_frac=None):
    """ARA-asymmetric sawtooth gate."""
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
# DRAIN FUNCTIONS — Generic, reusable for any ARA system
# =================================================================

def static_drain(cascade_amp, base_amp, drain_strength=INV_PHI_9):
    """V1: Fixed drain — constant fraction removed.

    Generic: drain_strength is system-specific.
    For Sun: 1/φ⁹ (the residual leakage from one full 9-coupling rotation)
    """
    return -drain_strength * cascade_amp


def amplitude_drain(cascade_amp, base_amp, drain_strength=INV_PHI_9):
    """V2: Amplitude-proportional drain — hotter systems drain more.

    Drain scales with how far above the system's mean the current
    output is. Neutral at mean, stronger above, weaker below.
    This is the ARA-natural formulation: high-ARA states radiate more.
    """
    excess = (cascade_amp - base_amp) / base_amp  # fractional excess
    return -drain_strength * cascade_amp * (1 + excess)


def phase_asymmetric_drain(cascade_amp, base_amp, gleiss_phase,
                            drain_strength=INV_PHI_9, acc_frac=STATIC_ACC):
    """V3: Phase-asymmetric drain — stronger during accumulation.

    During accumulation (field building), open magnetic flux increases
    → more energy escapes. During release, field is collapsing inward
    → less escapes. The drain has its own ARA asymmetry.
    """
    cycle_pos = (gleiss_phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < acc_frac:
        # Accumulation: drain ramps up (more open flux as field builds)
        phase_mod = 1.0 + (cycle_pos / acc_frac) * (PHI - 1)
    else:
        # Release: drain diminishes (field collapsing inward)
        ramp = (cycle_pos - acc_frac) / (1 - acc_frac)
        phase_mod = PHI * (1 - ramp) + INV_PHI * ramp

    return -drain_strength * cascade_amp * phase_mod


def ara_coupled_drain(cascade_amp, base_amp, gleiss_phase,
                       drain_strength=INV_PHI_9):
    """V4: ARA-coupled drain — the 1/φ⁹ residual made DYNAMIC.

    In 203b, the residual was: base_amp × 1/φ⁹ × cos(gleiss_phase)
    That's a STATIC additive — same for every cycle regardless of amplitude.

    The drain version: scales the residual by the system's current state.
    Hot cycles → bigger drain. Cool cycles → smaller drain.
    This is the Sun's opposing ARA eating its own output.

    Replaces the static 1/φ⁹ residual in 203b.
    """
    amp_ratio = cascade_amp / base_amp
    return -drain_strength * cascade_amp * amp_ratio * abs(np.cos(gleiss_phase))


def waldmeier_drain(cascade_amp, base_amp, gleiss_phase,
                     drain_strength=INV_PHI_9, acc_frac=STATIC_ACC):
    """V6: Waldmeier-targeted drain — specifically corrects rise-fraction bias.

    The Waldmeier effect: fast-rising cycles have higher peaks.
    Our model over-predicts high cycles because it doesn't account for
    the drain being proportionally larger for high-amplitude cycles.

    This drain is stronger when:
    1. Amplitude is high (more energy to radiate)
    2. We're in the accumulation phase (energy building, more flux open)

    The combination should compress the predicted amplitude range,
    reducing the rise-fraction correlation.
    """
    # How "hot" is this cycle relative to mean?
    heat = cascade_amp / base_amp

    # Phase asymmetry: drain peaks during late accumulation
    cycle_pos = (gleiss_phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < acc_frac:
        # Ramp up during accumulation — peaks at transition
        phase_weight = (cycle_pos / acc_frac) ** PHI  # φ-exponent for natural ramp
    else:
        # Decay during release
        ramp = (cycle_pos - acc_frac) / (1 - acc_frac)
        phase_weight = (1 - ramp) ** PHI

    return -drain_strength * cascade_amp * heat * phase_weight


# =================================================================
# PREDICTION FUNCTIONS
# =================================================================

def predict_203b(t, base_amp, t_ref):
    """Original 203b — baseline for comparison."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)
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


def predict_v1(t, base_amp, t_ref):
    """V1: Static drain replaces static residual."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)
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
    # Replace static residual with static drain
    amp += static_drain(amp, base_amp)
    return amp


def predict_v2(t, base_amp, t_ref):
    """V2: Amplitude-proportional drain."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)
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
    amp += amplitude_drain(amp, base_amp)
    return amp


def predict_v3(t, base_amp, t_ref):
    """V3: Phase-asymmetric drain."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)
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
    amp += phase_asymmetric_drain(amp, base_amp, gleiss_phase)
    return amp


def predict_v4(t, base_amp, t_ref):
    """V4: ARA-coupled drain — dynamic 1/φ⁹ residual."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)
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
    amp += ara_coupled_drain(amp, base_amp, gleiss_phase)
    return amp


def predict_v5_sequence(peak_years_seq, peak_amps_prev, base_amp, t_ref):
    """V5: Causal gate (207) + ARA-coupled drain (V4).

    Best of both: past→present gate AND dynamic drain.
    This is the full model: internal cycling + causal memory + energy loss.
    """
    preds = []
    for i, t in enumerate(peak_years_seq):
        # Causal gate: set by previous cycle
        if i == 0:
            acc_frac = STATIC_ACC
        else:
            prev_amp = peak_amps_prev[i - 1] if i - 1 < len(peak_amps_prev) else MEAN_AMP
            prev_ara = prev_amp / base_amp
            acc_frac = ara_to_acc(prev_ara)

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

        # Dynamic drain instead of static residual
        amp += ara_coupled_drain(amp, base_amp, gleiss_phase)

        preds.append(amp)
    return preds


def predict_v6(t, base_amp, t_ref):
    """V6: Waldmeier-targeted drain."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)
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
    amp += waldmeier_drain(amp, base_amp, gleiss_phase)
    return amp


# =================================================================
# FITTING + EVALUATION
# =================================================================

def fit(predict_fn, train_years, train_amps, is_sequence=False,
        all_peak_amps=None, all_peak_years=None, train_mask=None):
    """Fit base_amp and t_ref on training data."""
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(train_amps) * 0.6,
                               np.mean(train_amps) * 1.4, 40):
            if is_sequence:
                # For V5: need to pass the full observed amp sequence for causal gate
                preds = predict_fn(train_years, all_peak_amps, ba, t_ref)
            else:
                preds = [predict_fn(t, ba, t_ref) for t in train_years]
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae = m
                best_ba, best_tr = ba, t_ref
    return best_ba, best_tr, best_mae


def loo_eval(predict_fn, label, is_sequence=False):
    """Leave-one-out with retraining."""
    phi_errors, sine_errors = [], []

    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        train_y = peak_years[mask]
        train_a = peak_amps[mask]

        if is_sequence:
            # For V5: need sequence prediction with causal gate
            # Train on all but i, predict all, take prediction at position i
            ba_i, tr_i, _ = fit(predict_fn, train_y, train_a,
                                is_sequence=True, all_peak_amps=peak_amps,
                                all_peak_years=peak_years, train_mask=mask)
            all_preds = predict_fn(peak_years, peak_amps, ba_i, tr_i)
            pred_i = all_preds[i]
        else:
            ba_i, tr_i, _ = fit(predict_fn, train_y, train_a)
            pred_i = predict_fn(peak_years[i], ba_i, tr_i)

        phi_errors.append(abs(pred_i - peak_amps[i]))
        sine_errors.append(abs(np.mean(train_a) - peak_amps[i]))

    phi_errors = np.array(phi_errors)
    sine_errors = np.array(sine_errors)
    phi_loo = phi_errors.mean()
    sine_loo = sine_errors.mean()
    n_wins = np.sum(phi_errors < sine_errors)

    # Rise fraction correlation (the Waldmeier diagnostic)
    ba_full, tr_full, _ = fit(predict_fn, peak_years, peak_amps,
                               is_sequence=is_sequence, all_peak_amps=peak_amps)
    if is_sequence:
        preds_full = predict_fn(peak_years, peak_amps, ba_full, tr_full)
    else:
        preds_full = [predict_fn(t, ba_full, tr_full) for t in peak_years]

    errors_full = np.array(preds_full) - peak_amps
    rise_corr = np.corrcoef(rise_fracs, errors_full)[0, 1]
    amp_corr = np.corrcoef(peak_amps, errors_full)[0, 1]

    return {
        'label': label,
        'loo_mae': phi_loo,
        'sine_mae': sine_loo,
        'improvement': (phi_loo / sine_loo - 1) * 100,
        'n_wins': n_wins,
        'rise_corr': rise_corr,
        'amp_corr': amp_corr,
        'phi_errors': phi_errors,
        'sine_errors': sine_errors,
        'ba': ba_full,
        'tr': tr_full,
    }


def temporal_splits(predict_fn, label, is_sequence=False):
    """Train on first N cycles, predict rest."""
    wins = 0
    results = []
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N:
            continue
        train_y = peak_years[:n_train]
        train_a = peak_amps[:n_train]

        if is_sequence:
            ba_s, tr_s, _ = fit(predict_fn, train_y, train_a,
                                is_sequence=True, all_peak_amps=peak_amps)
            all_preds = predict_fn(peak_years, peak_amps, ba_s, tr_s)
            test_preds = all_preds[n_train:]
        else:
            ba_s, tr_s, _ = fit(predict_fn, train_y, train_a)
            test_preds = [predict_fn(t, ba_s, tr_s) for t in peak_years[n_train:]]

        test_amps = peak_amps[n_train:]
        phi_m = mae(test_preds, test_amps)
        sine_m = mae(np.full(len(test_amps), train_a.mean()), test_amps)
        winner = "φ" if phi_m < sine_m else "sine"
        if phi_m < sine_m:
            wins += 1
        results.append((n_train, N - n_train, phi_m, sine_m, winner))

    return wins, results


# =================================================================
# MAIN
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("SCRIPT 209 — SOLAR DRAIN: THE SUN'S OPPOSING ARA")
    print("=" * 70)

    print("""
  CONCEPT: The Sun is not a closed loop. It radiates energy into space.
  This is a small opposing ARA — a drain — that we haven't modelled.

  The drain is:
    - Always negative (energy OUT)
    - Proportional to amplitude (hot cycles drain more)
    - Asymmetric in phase (accumulation drains differently from release)
    - Dynamic (scales with system state, not fixed)

  HYPOTHESIS: The Waldmeier distortion (rise_frac r≈+0.82) IS the drain.

  Drain strength = 1/φ⁹ (same as the residual leakage, but now DYNAMIC)
  Free parameters: 2 (base_amp, t_ref) — same as 203b
    """)

    # === BASELINE: 203b ===
    print(f"\n{'='*70}")
    print("BASELINE — 203b (static 1/φ⁹ residual)")
    print(f"{'='*70}")

    r203b = loo_eval(predict_203b, "203b baseline")
    print(f"  LOO MAE = {r203b['loo_mae']:.2f} (sine = {r203b['sine_mae']:.2f})")
    print(f"  Improvement = {r203b['improvement']:+.1f}% vs sine")
    print(f"  Wins: {r203b['n_wins']}/25")
    print(f"  Rise frac corr = {r203b['rise_corr']:+.3f}")
    print(f"  Peak amp corr  = {r203b['amp_corr']:+.3f}")

    w203b, s203b = temporal_splits(predict_203b, "203b")
    print(f"  Temporal splits: {w203b}/7")
    for nt, ntest, pm, sm, w in s203b:
        print(f"    Train {nt:2d} / Test {ntest:2d}: φ={pm:.1f}  sine={sm:.1f}  → {w}")

    # === V1: Static drain ===
    print(f"\n{'='*70}")
    print("V1 — STATIC DRAIN (fixed 1/φ⁹ fraction subtracted)")
    print(f"{'='*70}")

    r1 = loo_eval(predict_v1, "V1 static drain")
    print(f"  LOO MAE = {r1['loo_mae']:.2f} ({r1['improvement']:+.1f}%)")
    print(f"  Wins: {r1['n_wins']}/25")
    print(f"  Rise frac corr = {r1['rise_corr']:+.3f}")
    print(f"  Peak amp corr  = {r1['amp_corr']:+.3f}")

    # === V2: Amplitude-proportional drain ===
    print(f"\n{'='*70}")
    print("V2 — AMPLITUDE-PROPORTIONAL DRAIN (hot cycles drain more)")
    print(f"{'='*70}")

    r2 = loo_eval(predict_v2, "V2 amp drain")
    print(f"  LOO MAE = {r2['loo_mae']:.2f} ({r2['improvement']:+.1f}%)")
    print(f"  Wins: {r2['n_wins']}/25")
    print(f"  Rise frac corr = {r2['rise_corr']:+.3f}")
    print(f"  Peak amp corr  = {r2['amp_corr']:+.3f}")

    # === V3: Phase-asymmetric drain ===
    print(f"\n{'='*70}")
    print("V3 — PHASE-ASYMMETRIC DRAIN (stronger during accumulation)")
    print(f"{'='*70}")

    r3 = loo_eval(predict_v3, "V3 phase drain")
    print(f"  LOO MAE = {r3['loo_mae']:.2f} ({r3['improvement']:+.1f}%)")
    print(f"  Wins: {r3['n_wins']}/25")
    print(f"  Rise frac corr = {r3['rise_corr']:+.3f}")
    print(f"  Peak amp corr  = {r3['amp_corr']:+.3f}")

    # === V4: ARA-coupled drain ===
    print(f"\n{'='*70}")
    print("V4 — ARA-COUPLED DRAIN (dynamic 1/φ⁹ — the residual eats itself)")
    print(f"{'='*70}")

    r4 = loo_eval(predict_v4, "V4 ARA drain")
    print(f"  LOO MAE = {r4['loo_mae']:.2f} ({r4['improvement']:+.1f}%)")
    print(f"  Wins: {r4['n_wins']}/25")
    print(f"  Rise frac corr = {r4['rise_corr']:+.3f}")
    print(f"  Peak amp corr  = {r4['amp_corr']:+.3f}")

    # === V5: Causal gate + ARA drain ===
    print(f"\n{'='*70}")
    print("V5 — CAUSAL GATE + ARA DRAIN (207 + V4 combined)")
    print(f"{'='*70}")

    r5 = loo_eval(predict_v5_sequence, "V5 causal+drain", is_sequence=True)
    print(f"  LOO MAE = {r5['loo_mae']:.2f} ({r5['improvement']:+.1f}%)")
    print(f"  Wins: {r5['n_wins']}/25")
    print(f"  Rise frac corr = {r5['rise_corr']:+.3f}")
    print(f"  Peak amp corr  = {r5['amp_corr']:+.3f}")

    w5, s5 = temporal_splits(predict_v5_sequence, "V5", is_sequence=True)
    print(f"  Temporal splits: {w5}/7")
    for nt, ntest, pm, sm, w in s5:
        print(f"    Train {nt:2d} / Test {ntest:2d}: φ={pm:.1f}  sine={sm:.1f}  → {w}")

    # === V6: Waldmeier-targeted drain ===
    print(f"\n{'='*70}")
    print("V6 — WALDMEIER-TARGETED DRAIN (heat × phase asymmetry)")
    print(f"{'='*70}")

    r6 = loo_eval(predict_v6, "V6 Waldmeier drain")
    print(f"  LOO MAE = {r6['loo_mae']:.2f} ({r6['improvement']:+.1f}%)")
    print(f"  Wins: {r6['n_wins']}/25")
    print(f"  Rise frac corr = {r6['rise_corr']:+.3f}")
    print(f"  Peak amp corr  = {r6['amp_corr']:+.3f}")

    # === COMPARISON TABLE ===
    print(f"\n{'='*70}")
    print("COMPARISON — ALL MODELS")
    print(f"{'='*70}")

    all_results = [r203b, r1, r2, r3, r4, r5, r6]

    print(f"\n  {'Model':<25s} {'LOO MAE':>8s} {'vs sine':>8s} {'Wins':>5s} "
          f"{'Rise r':>7s} {'Amp r':>7s}")
    print(f"  {'-'*25} {'-'*8} {'-'*8} {'-'*5} {'-'*7} {'-'*7}")

    for r in all_results:
        print(f"  {r['label']:<25s} {r['loo_mae']:8.2f} {r['improvement']:+7.1f}% "
              f"{r['n_wins']:3d}/25 {r['rise_corr']:+7.3f} {r['amp_corr']:+7.3f}")

    # Find best by LOO
    best = min(all_results, key=lambda r: r['loo_mae'])
    print(f"\n  BEST LOO: {best['label']} (MAE={best['loo_mae']:.2f})")

    # Find best Waldmeier reduction
    best_wald = min(all_results, key=lambda r: abs(r['rise_corr']))
    print(f"  BEST WALDMEIER: {best_wald['label']} (r={best_wald['rise_corr']:+.3f})")

    # === TEMPORAL SPLITS for best drain models ===
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS — KEY MODELS")
    print(f"{'='*70}")

    # Find best non-sequence model for temporal splits
    non_seq_results = [r for r in [r1, r2, r3, r4, r6]
                       if r['loo_mae'] == min(x['loo_mae'] for x in [r1, r2, r3, r4, r6])]
    best_drain_fn_map = {
        'V1 static drain': predict_v1,
        'V2 amp drain': predict_v2,
        'V3 phase drain': predict_v3,
        'V4 ARA drain': predict_v4,
        'V6 Waldmeier drain': predict_v6,
    }

    for r in [r2, r4, r6]:
        fn = best_drain_fn_map.get(r['label'])
        if fn:
            w, splits = temporal_splits(fn, r['label'])
            print(f"\n  {r['label']}: {w}/7 temporal splits")
            for nt, ntest, pm, sm, winner in splits:
                print(f"    Train {nt:2d} / Test {ntest:2d}: "
                      f"φ={pm:.1f}  sine={sm:.1f}  → {winner}")

    # === DIAGNOSTIC: per-cycle drain effect ===
    print(f"\n{'='*70}")
    print("DIAGNOSTIC — DRAIN EFFECT PER CYCLE")
    print(f"{'='*70}")

    # Show how the drain changes predictions vs 203b
    ba_ref, tr_ref, _ = fit(predict_203b, peak_years, peak_amps)
    ba_best, tr_best = best['ba'], best['tr']

    print(f"\n  Best drain model: {best['label']}")
    print(f"  {'Cycle':>5s} {'Obs':>7s} {'203b':>7s} {'Drain':>7s} {'Δ':>7s} "
          f"{'RiseFr':>7s}")

    best_fn_map = {
        '203b baseline': predict_203b,
        'V1 static drain': predict_v1,
        'V2 amp drain': predict_v2,
        'V3 phase drain': predict_v3,
        'V4 ARA drain': predict_v4,
        'V6 Waldmeier drain': predict_v6,
    }

    best_fn = best_fn_map.get(best['label'], predict_203b)

    for i, c in enumerate(cycle_nums):
        p203b = predict_203b(peak_years[i], ba_ref, tr_ref)
        p_best = best_fn(peak_years[i], ba_best, tr_best)
        delta = p_best - p203b
        print(f"  {c:5d} {peak_amps[i]:7.1f} {p203b:7.1f} {p_best:7.1f} "
              f"{delta:+7.1f} {rise_fracs[i]:7.3f}")

    # === SUMMARY ===
    print(f"\n{'='*70}")
    print("SUMMARY — SCRIPT 209")
    print(f"{'='*70}")
    print(f"""
  CONCEPT: The Sun has a drain — a small opposing ARA where energy
  dissipates into space. This is the vertical ARA going UP that we
  hadn't modelled.

  BEST MODEL: {best['label']}
    LOO MAE = {best['loo_mae']:.2f} ({best['improvement']:+.1f}% vs sine)
    Wins: {best['n_wins']}/25
    Rise frac correlation: {best['rise_corr']:+.3f} (was +0.82 in 203b-208)
    Peak amp correlation: {best['amp_corr']:+.3f}

  WALDMEIER DIAGNOSTIC:
    203b baseline:    rise_frac r = {r203b['rise_corr']:+.3f}
    Best drain:       rise_frac r = {best_wald['rise_corr']:+.3f}
    Change: {abs(best_wald['rise_corr']) - abs(r203b['rise_corr']):+.3f} (closer to 0 = better)

  The drain functions are GENERIC — they take (cascade_amp, base_amp,
  drain_strength) and can be applied to any ARA system by setting
  drain_strength to the appropriate scale leakage constant.

  For the Sun: drain_strength = 1/φ⁹ (the 9-coupling rotation residual)
  For other systems: drain_strength = 1/φⁿ where n = coupling count
""")
