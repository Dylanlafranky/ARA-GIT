#!/usr/bin/env python3
"""
Script 206 — Dynamic ARA Gate: The Sun's ARA Breathes

INSIGHT (Dylan):
  "The sun's ARA would change dynamically with the system. It won't
  always be the same 1.73 or whatever, that's just what we averaged
  and diagnosed it at, but it isn't a set number, just a set number
  for that time period."

  The gate accumulation fraction (0.618 in the static model) should
  vary per cycle based on the energy flowing through the system.
  This IS the Waldmeier effect in ARA language:
    - Strong cycle → ARA closer to φ → faster accumulation → lower rise fraction
    - Weak cycle → ARA drifts from φ → slower accumulation → higher rise fraction

APPROACH:
  Two-pass feedback model:
    Pass 1: Compute raw cascade amplitude with default gate (gets energy level)
    Pass 2: Use raw amplitude to set dynamic ACC_FRAC, recompute with new gate

  The dynamic gate uses the relationship:
    acc_frac = f(amplitude / mean_amplitude)
  where f maps energy level to accumulation speed.

MODELS:
  V1: Linear Waldmeier — acc_frac scales linearly with amplitude ratio
  V2: φ-bounded — acc_frac bounded between 1/φ² and φ/(φ+1)
  V3: ARA-driven — the local ARA value directly sets the gate asymmetry
  V4: Iterative convergence — run multiple passes until gate stabilizes
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
rise_fracs = (peak_years - start_years) / durations

CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
STATIC_ACC = PHI / (PHI + 1)  # 0.618

def mae(p, o):
    return np.mean(np.abs(np.array(p) - np.array(o)))

def sawtooth_valve(phase, acc_frac=None):
    """ARA sawtooth with variable accumulation fraction."""
    if acc_frac is None:
        acc_frac = STATIC_ACC
    # Clamp to valid range
    acc_frac = max(0.15, min(0.85, acc_frac))
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < acc_frac:
        state = (cycle_pos / acc_frac) * PHI
    else:
        ramp = (cycle_pos - acc_frac) / (1 - acc_frac)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    return state / ((PHI + INV_PHI) / 2)


def raw_cascade(t, base_amp, t_ref):
    """Pass 1: static gate, get raw energy level."""
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


def cascade_with_gate(t, base_amp, t_ref, acc_frac):
    """Pass 2: dynamic gate with given acc_frac."""
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


# ================================================================
# V1: Linear Waldmeier
# Higher raw amp → lower acc_frac (faster rise)
# acc_frac = STATIC_ACC - k * (raw_amp/base_amp - 1)
# ================================================================

def predict_v1(t, base_amp, t_ref):
    raw = raw_cascade(t, base_amp, t_ref)
    ratio = raw / base_amp
    # Linear: when ratio > 1, acc_frac decreases (faster rise)
    # Calibrated so that ratio=1 gives static acc, ratio=1.5 gives ~0.35
    k = 0.4  # Waldmeier slope
    acc_frac = STATIC_ACC - k * (ratio - 1.0)
    return cascade_with_gate(t, base_amp, t_ref, acc_frac)


# ================================================================
# V2: φ-bounded Waldmeier
# acc_frac bounded between INV_PHI² ≈ 0.382 and STATIC_ACC = 0.618
# Uses φ ratio: strong cycles approach 1/φ², weak approach φ/(φ+1)
# ================================================================

def predict_v2(t, base_amp, t_ref):
    raw = raw_cascade(t, base_amp, t_ref)
    ratio = raw / base_amp
    # Map ratio through sigmoid-like function bounded by φ values
    lower = INV_PHI ** 2   # ≈ 0.382 (fast rise, strong cycles)
    upper = STATIC_ACC      # ≈ 0.618 (slow rise, weak cycles)
    # When ratio < 1 (weak): acc_frac → upper (slower)
    # When ratio > 1 (strong): acc_frac → lower (faster)
    # Use tanh for smooth transition
    x = (ratio - 1.0) * 3.0  # Scale factor
    blend = 0.5 * (1 + np.tanh(x))  # 0 when weak, 1 when strong
    acc_frac = upper - blend * (upper - lower)
    return cascade_with_gate(t, base_amp, t_ref, acc_frac)


# ================================================================
# V3: ARA-driven gate
# The sun's instantaneous ARA directly sets the gate shape
# ARA = raw_amp / base_amp (normalized energy)
# acc_frac = 1 / (1 + ARA)  — the ARA division rule
# When ARA=φ: acc_frac = 1/(1+φ) = 1/φ² ≈ 0.382
# When ARA=1: acc_frac = 0.500
# When ARA=1/φ: acc_frac = φ/(1+φ) = φ/φ² = 1/φ ≈ 0.618
# This is beautiful: the gate IS the ARA, expressed as timing
# ================================================================

def predict_v3(t, base_amp, t_ref):
    raw = raw_cascade(t, base_amp, t_ref)
    local_ara = raw / base_amp
    # ARA → acc_frac: the natural ARA division
    # acc_frac = 1 / (1 + local_ara)
    acc_frac = 1.0 / (1.0 + local_ara)
    return cascade_with_gate(t, base_amp, t_ref, acc_frac)


# ================================================================
# V4: Iterative convergence
# Run gate ↔ cascade feedback until stable
# ================================================================

def predict_v4(t, base_amp, t_ref, max_iter=5):
    acc_frac = STATIC_ACC  # Start with static
    for _ in range(max_iter):
        amp = cascade_with_gate(t, base_amp, t_ref, acc_frac)
        local_ara = amp / base_amp
        new_acc = 1.0 / (1.0 + local_ara)
        if abs(new_acc - acc_frac) < 1e-6:
            break
        acc_frac = 0.5 * acc_frac + 0.5 * new_acc  # Damped update
    return amp


# ================================================================
# V5: Inverse — acc_frac = ARA / (1 + ARA)
# The OPPOSITE mapping: strong cycles get HIGHER acc_frac
# This means the cascade has MORE time to accumulate, producing
# EVEN HIGHER peaks — a positive feedback that could explain
# why some cycles are extreme
# ================================================================

def predict_v5(t, base_amp, t_ref):
    raw = raw_cascade(t, base_amp, t_ref)
    local_ara = raw / base_amp
    acc_frac = local_ara / (1.0 + local_ara)
    return cascade_with_gate(t, base_amp, t_ref, acc_frac)


# ================================================================
# BASELINE: static 203b
# ================================================================

def predict_203b(t, base_amp, t_ref):
    return raw_cascade(t, base_amp, t_ref)


# ================================================================
# FITTING & EVALUATION
# ================================================================

def fit(predict_fn, train_years, train_amps):
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 40):
        for ba in np.linspace(np.mean(train_amps)*0.6,
                               np.mean(train_amps)*1.4, 30):
            preds = [predict_fn(t, ba, t_ref) for t in train_years]
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


def full_eval(name, predict_fn, show_detail=True):
    print(f"\n{'='*72}")
    print(f"  {name}")
    print(f"{'='*72}")

    # Full fit first (for per-cycle detail)
    ba_f, tr_f, fmae = fit(predict_fn, peak_years, peak_amps)

    # Show per-cycle detail with dynamic acc_frac
    if show_detail:
        print(f"\n  {'Cyc':>3s} {'Year':>6s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} "
              f"{'|Err|':>6s} {'RFrac':>6s} {'AccFrac':>8s}")
        errs, acc_fracs_shown = [], []
        for i, c in enumerate(cycle_nums):
            pred = predict_fn(peak_years[i], ba_f, tr_f)
            err = pred - peak_amps[i]
            errs.append(err)
            # Get the dynamic acc_frac for display
            raw = raw_cascade(peak_years[i], ba_f, tr_f)
            local_ara = raw / ba_f
            dyn_acc = 1.0 / (1.0 + local_ara)
            acc_fracs_shown.append(dyn_acc)
            print(f"  {c:3d} {peak_years[i]:6.0f} {peak_amps[i]:7.1f} {pred:7.1f} "
                  f"{err:+7.1f} {abs(err):6.1f} {rise_fracs[i]:5.1%} {dyn_acc:7.1%}")
        errs = np.array(errs)
        print(f"\n  Error correlations:")
        print(f"    Rise fraction:   r = {np.corrcoef(errs, rise_fracs)[0,1]:+.3f}")
        print(f"    Peak amplitude:  r = {np.corrcoef(errs, peak_amps)[0,1]:+.3f}")

    # LOO
    phi_errs, sine_errs = [], []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        ba_i, tr_i, _ = fit(predict_fn, peak_years[mask], peak_amps[mask])
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

    print(f"\n  LOO MAE: {loo:.2f} (sine {sloo:.2f}) → {pct:+.1f}%")
    print(f"  Wins: {wins}/25 | Bootstrap: {boot/n_boot*100:.1f}%")
    print(f"  Free params: 2 (base_amp + t_ref)")

    # Temporal splits
    sw = 0
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N: continue
        ba_s, tr_s, _ = fit(predict_fn, peak_years[:n_train], peak_amps[:n_train])
        tp = [predict_fn(t, ba_s, tr_s) for t in peak_years[n_train:]]
        ta = peak_amps[n_train:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:n_train].mean()), ta)
        w = "φ" if pm < sm else "sine"
        if pm < sm: sw += 1
        print(f"    Train {n_train:2d} / Test {N-n_train:2d}: φ={pm:.1f} sine={sm:.1f} → {w}")
    print(f"  Temporal splits: {sw}/7")

    return loo, pct, wins, boot/n_boot*100, sw


if __name__ == '__main__':
    print("=" * 72)
    print("SCRIPT 206 — DYNAMIC ARA GATE")
    print("The Sun's ARA Breathes")
    print("=" * 72)

    print(f"\n  Static ACC_FRAC = {STATIC_ACC:.3f} (φ/(φ+1))")
    print(f"  Actual mean rise_frac = {rise_fracs.mean():.3f}")
    print(f"  Waldmeier correlation (obs): rise_frac vs peak_amp = "
          f"{np.corrcoef(rise_fracs, peak_amps)[0,1]:+.3f}")

    # Show the ARA → acc_frac mapping
    print(f"\n  V3 ARA → acc_frac mapping (the natural ARA division):")
    print(f"    ARA = 1/φ² ≈ {INV_PHI**2:.3f} → acc = {1/(1+INV_PHI**2):.3f} (very weak)")
    print(f"    ARA = 1/φ  ≈ {INV_PHI:.3f}  → acc = {1/(1+INV_PHI):.3f} = {STATIC_ACC:.3f} (idle)")
    print(f"    ARA = 1.0          → acc = {1/(1+1.0):.3f} (balanced)")
    print(f"    ARA = φ    ≈ {PHI:.3f}  → acc = {1/(1+PHI):.3f} = {INV_PHI**2:.3f} (strong)")
    print(f"    ARA = φ²   ≈ {PHI**2:.3f}  → acc = {1/(1+PHI**2):.3f} (very strong)")

    results = {}

    r = full_eval("BASELINE: 203b (static gate)", predict_203b)
    results['203b'] = r

    r = full_eval("V1: Linear Waldmeier (k=0.4)", predict_v1)
    results['V1'] = r

    r = full_eval("V2: φ-bounded sigmoid", predict_v2)
    results['V2'] = r

    r = full_eval("V3: ARA-driven gate: acc = 1/(1+ARA)", predict_v3)
    results['V3'] = r

    r = full_eval("V4: Iterative convergence (5 passes)", predict_v4)
    results['V4'] = r

    r = full_eval("V5: Inverse ARA gate: acc = ARA/(1+ARA)", predict_v5)
    results['V5'] = r

    # === SUMMARY ===
    print(f"\n{'='*72}")
    print("SUMMARY")
    print(f"{'='*72}")
    print(f"  {'Model':<42s} {'LOO':>7s} {'vs%':>7s} {'W':>4s} {'Boot':>5s} {'TS':>4s}")
    print(f"  {'-'*42} {'-'*7} {'-'*7} {'-'*4} {'-'*5} {'-'*4}")
    for name, (loo, pct, wins, boot, sw) in results.items():
        print(f"  {name:<42s} {loo:7.2f} {pct:+6.1f}% {wins:3d} {boot:5.1f} {sw:3d}")

    # Which is best?
    best = min(results.keys(), key=lambda k: results[k][0])
    b = results[best]
    print(f"\n  BEST: {best}")
    print(f"    LOO = {b[0]:.2f} ({b[1]:+.1f}% vs sine)")

    base_loo = results['203b'][0]
    if b[0] < base_loo:
        print(f"    Improves on 203b by {(b[0]/base_loo-1)*100:.1f}%")
    else:
        print(f"    Does not beat 203b baseline")

    print(f"\n{'='*72}")
    print("END SCRIPT 206")
    print(f"{'='*72}")
