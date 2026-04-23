#!/usr/bin/env python3
"""
Script 204 — Fractal Modulator: Self-Similar Correction at Every Scale

INSIGHT (Dylan):
  The end modulator needs to "account for all the small nudges underneath
  that accumulate and help address the nudges from above."

MATHEMATICAL BASIS:
  The Weierstrass-φ sum: W(t) = Σ φ^(-n) · cos(φⁿ · t)
  - Each scale is φ× weaker and φ× faster than the one above
  - φ is a Pisot number: scales are maximally irrational → no resonance pileup
  - Sum converges to φ (geometric series)
  - Fractal dimension = 1 (borderline smooth/rough — critical threshold)

  Literature confirms sunspot series is multifractal (Oswiecimka et al.)
  Multifractality peaks ~2yr before solar max, then collapses to monofractal.

MODELS TESTED:
  V1: Weierstrass residual — replace 1/φ⁹ with truncated fractal sum
  V2: Extended cascade — add deeper φ^n periods to multiplicative chain
  V3: Fractal gate — sawtooth valve itself has self-similar sub-structure
  V4: Full fractal ARA — multiplicative cascade where each level has its
      own ARA micro-valve (self-similar at every scale)

BASE: Script 203b architecture (LOO MAE = 37.66)
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_4 = INV_PHI ** 4

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
peak_years = np.array([CYCLES[c][1] for c in cycle_nums])
peak_amps = np.array([CYCLES[c][2] for c in cycle_nums])
N = len(cycle_nums)

# Core cascade
CASCADE_BASE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
ACC_FRAC = PHI / (PHI + 1)  # ≈ 0.618

def mae(p, o):
    return np.mean(np.abs(np.array(p) - np.array(o)))

def sawtooth_valve(phase):
    """ARA-asymmetric sawtooth gate."""
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < ACC_FRAC:
        state = (cycle_pos / ACC_FRAC) * PHI
    else:
        ramp = (cycle_pos - ACC_FRAC) / (1 - ACC_FRAC)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    return state / ((PHI + INV_PHI) / 2)


# ============================================================
# MODEL V1: Weierstrass-φ Residual
# Replace single 1/φ⁹ term with truncated fractal sum
# W(t) = Σ_{n=0}^{depth} φ^(-(9+n)) · cos(φⁿ · gleiss_phase)
# ============================================================

def predict_v1(t, base_amp, t_ref, depth=5):
    """V1: Weierstrass residual replaces 1/φ⁹ additive."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)

    # Standard cascade
    amp = base_amp
    for period in CASCADE_BASE:
        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    # Weierstrass-φ fractal residual
    # Each term: φ^(-(9+n)) amplitude, φⁿ× faster than Gleissberg
    fractal_sum = 0.0
    for n in range(depth + 1):
        coeff = INV_PHI ** (9 + n)
        freq_mult = PHI ** n
        fractal_sum += coeff * np.cos(freq_mult * gleiss_phase)

    amp += base_amp * fractal_sum
    return amp


# ============================================================
# MODEL V2: Extended Cascade
# Add deeper periods below φ⁴: φ³, φ², φ¹
# More cascade members = more multiplicative fractal depth
# ============================================================

def predict_v2(t, base_amp, t_ref, extra_depth=3):
    """V2: Extended cascade depth."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)

    # Extended cascade: add lower powers of φ
    cascade_ext = CASCADE_BASE + [PHI**n for n in range(3, 3 - extra_depth, -1) if n >= 1]

    amp = base_amp
    for period in cascade_ext:
        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    # Keep 1/φ⁹ residual
    amp += base_amp * (INV_PHI ** 9) * np.cos(gleiss_phase)
    return amp


# ============================================================
# MODEL V3: Fractal Gate
# Sawtooth valve has self-similar sub-structure:
# gate(phase) = gate_base(phase) × (1 + Σ φ^(-n) · gate_base(φⁿ · phase))
# The valve itself is fractal — rough at every zoom level
# ============================================================

def fractal_sawtooth(phase, depth=4):
    """Self-similar sawtooth: base gate × fractal micro-gates."""
    base_gate = sawtooth_valve(phase)
    correction = 0.0
    for n in range(1, depth + 1):
        sub_phase = (PHI ** n) * phase
        sub_gate = sawtooth_valve(sub_phase)
        # Each sub-gate is φ^(-n) weaker, normalized around 0
        correction += (INV_PHI ** n) * (sub_gate - 1.0)
    return base_gate * (1.0 + correction)

def predict_v3(t, base_amp, t_ref, depth=4):
    """V3: Fractal gate."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = fractal_sawtooth(gleiss_phase, depth)

    amp = base_amp
    for period in CASCADE_BASE:
        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    # Weierstrass residual (V1 best idea) instead of single 1/φ⁹
    fractal_sum = 0.0
    for n in range(depth + 1):
        fractal_sum += (INV_PHI ** (9 + n)) * np.cos((PHI ** n) * gleiss_phase)
    amp += base_amp * fractal_sum

    return amp


# ============================================================
# MODEL V4: Full Fractal ARA
# Each cascade member has its own ARA micro-valve
# The valve at scale n is the gate from scale n+1
# Self-similar: the STRUCTURE repeats, not just the numbers
# ============================================================

def predict_v4(t, base_amp, t_ref, fractal_depth=3):
    """V4: Full fractal ARA — each scale has its own micro-valve."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    macro_gate = sawtooth_valve(gleiss_phase)

    amp = base_amp
    for j, period in enumerate(CASCADE_BASE):
        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)

        # This member's gate: macro gate × micro self-similar corrections
        local_gate = macro_gate
        for n in range(1, fractal_depth + 1):
            # Each sub-gate runs at φⁿ× the local frequency
            sub_phase = phase * (PHI ** n)
            micro_valve = sawtooth_valve(sub_phase)
            # Attenuated by φ^(-n)
            local_gate *= (1.0 + (INV_PHI ** n) * (micro_valve - 1.0))

        eps = INV_PHI_4 * local_gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    # Weierstrass residual
    fractal_sum = 0.0
    for n in range(fractal_depth + 1):
        fractal_sum += (INV_PHI ** (9 + n)) * np.cos((PHI ** n) * gleiss_phase)
    amp += base_amp * fractal_sum

    return amp


# ============================================================
# FITTING & EVALUATION
# ============================================================

def fit_model(predict_fn, train_years, train_amps, **kwargs):
    """Fit base_amp and t_ref on training data."""
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(train_amps) * 0.6,
                               np.mean(train_amps) * 1.4, 40):
            preds = [predict_fn(t, ba, t_ref, **kwargs) for t in train_years]
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae = m
                best_ba, best_tr = ba, t_ref
    return best_ba, best_tr, best_mae


def evaluate_model(name, predict_fn, extra_params=0, **kwargs):
    """Full evaluation: LOO + temporal splits + bootstrap."""
    print(f"\n{'='*70}")
    print(f"  {name}")
    print(f"{'='*70}")

    # LOO
    phi_errors, sine_errors = [], []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        ba_i, tr_i, _ = fit_model(predict_fn, peak_years[mask], peak_amps[mask], **kwargs)
        pred_i = predict_fn(peak_years[i], ba_i, tr_i, **kwargs)
        phi_errors.append(abs(pred_i - peak_amps[i]))
        sine_errors.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    phi_errors = np.array(phi_errors)
    sine_errors = np.array(sine_errors)
    phi_loo = phi_errors.mean()
    sine_loo = sine_errors.mean()
    n_wins = np.sum(phi_errors < sine_errors)

    # Bootstrap
    n_boot = 10000
    phi_better = sum(1 for _ in range(n_boot)
                     if phi_errors[np.random.choice(N, N, True)].mean() <
                        sine_errors[np.random.choice(N, N, True)].mean())

    pct = (phi_loo / sine_loo - 1) * 100
    print(f"  LOO MAE: {phi_loo:.2f} (sine {sine_loo:.2f}) → {pct:+.1f}%")
    print(f"  Wins: {n_wins}/25 | Bootstrap: {phi_better/n_boot*100:.1f}%")
    print(f"  Free params: {2 + extra_params}")

    # Temporal splits
    split_wins = 0
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N: continue
        ba_s, tr_s, _ = fit_model(predict_fn, peak_years[:n_train],
                                   peak_amps[:n_train], **kwargs)
        test_preds = [predict_fn(t, ba_s, tr_s, **kwargs) for t in peak_years[n_train:]]
        test_amps = peak_amps[n_train:]
        phi_m = mae(test_preds, test_amps)
        sine_m = mae(np.full(len(test_amps), peak_amps[:n_train].mean()), test_amps)
        if phi_m < sine_m: split_wins += 1
        winner = "φ" if phi_m < sine_m else "sine"
        print(f"    Train {n_train:2d} / Test {N-n_train:2d}: φ={phi_m:.1f} sine={sine_m:.1f} → {winner}")

    print(f"  Temporal splits: {split_wins}/7")

    return phi_loo, pct, n_wins, phi_better/n_boot*100, split_wins


# ============================================================
# BASELINE (203b for reference)
# ============================================================

def predict_203b(t, base_amp, t_ref):
    """203b baseline for comparison."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase)
    amp = base_amp
    for period in CASCADE_BASE:
        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)
    amp += base_amp * (INV_PHI ** 9) * np.cos(gleiss_phase)
    return amp


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    print("=" * 70)
    print("SCRIPT 204 — FRACTAL MODULATOR")
    print("Self-similar correction at every scale")
    print("=" * 70)

    print(f"\n  φ = {PHI:.10f}")
    print(f"  Weierstrass convergence: Σ φ^(-n) = {PHI:.4f}")
    print(f"  Fractal dimension of W_φ(t): D = 2 - 1 = 1.0 (critical)")
    print(f"  Sunspot series: confirmed multifractal (literature)")

    # Show what the fractal sum looks like
    print(f"\n  Weierstrass-φ residual terms:")
    total = 0
    for n in range(8):
        coeff = INV_PHI ** (9 + n)
        freq = PHI ** n
        total += coeff
        print(f"    n={n}: amplitude φ^(-{9+n}) = {coeff:.6f}, "
              f"freq = φ^{n} × Gleissberg = {GLEISSBERG/freq:.1f}yr period, "
              f"running sum = {total:.6f}")
    print(f"  Convergence limit: φ^(-9) × φ/(φ-1) = {(INV_PHI**9) * PHI/(PHI-1):.6f}")

    results = {}

    # Baseline
    print(f"\n{'='*70}")
    print("  BASELINE: Script 203b")
    print(f"{'='*70}")
    r = evaluate_model("203b Baseline", predict_203b)
    results['203b'] = r

    # V1: Weierstrass residual (depth scan)
    for depth in [3, 5, 8]:
        r = evaluate_model(f"V1: Weierstrass Residual (depth={depth})",
                          predict_v1, depth=depth)
        results[f'V1_d{depth}'] = r

    # V2: Extended cascade
    for ext in [1, 2, 3]:
        r = evaluate_model(f"V2: Extended Cascade (+{ext} levels)",
                          predict_v2, extra_depth=ext)
        results[f'V2_e{ext}'] = r

    # V3: Fractal gate
    for depth in [2, 4]:
        r = evaluate_model(f"V3: Fractal Gate (depth={depth})",
                          predict_v3, depth=depth)
        results[f'V3_d{depth}'] = r

    # V4: Full fractal ARA
    for depth in [2, 3]:
        r = evaluate_model(f"V4: Full Fractal ARA (depth={depth})",
                          predict_v4, fractal_depth=depth)
        results[f'V4_d{depth}'] = r

    # === SUMMARY TABLE ===
    print(f"\n{'='*70}")
    print("SUMMARY TABLE — ALL MODELS")
    print(f"{'='*70}")
    print(f"  {'Model':<35s} {'LOO':>7s} {'vs sine':>8s} {'Wins':>5s} {'Boot%':>6s} {'TSplit':>6s}")
    print(f"  {'-'*35} {'-'*7} {'-'*8} {'-'*5} {'-'*6} {'-'*6}")

    sine_ref = 48.78  # from Script 202
    for name, (loo, pct, wins, boot, splits) in results.items():
        print(f"  {name:<35s} {loo:7.2f} {pct:+7.1f}% {wins:3d}/25 {boot:5.1f}% {splits:3d}/7")

    # Identify best
    best_name = min(results.keys(), key=lambda k: results[k][0])
    best = results[best_name]
    print(f"\n  BEST: {best_name}")
    print(f"    LOO MAE = {best[0]:.2f} ({best[1]:+.1f}% vs sine)")
    print(f"    Wins {best[2]}/25, Bootstrap {best[3]:.1f}%, Temporal splits {best[4]}/7")

    # Check if fractal beats 203b
    base_loo = results['203b'][0]
    if best[0] < base_loo:
        print(f"\n  ✓ Fractal modulator improves on 203b by {(best[0]/base_loo-1)*100:.1f}%")
    else:
        print(f"\n  ✗ No fractal variant beats 203b baseline")

    print(f"\n{'='*70}")
    print("END SCRIPT 204")
    print(f"{'='*70}")
