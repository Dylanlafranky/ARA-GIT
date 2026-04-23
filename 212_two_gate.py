#!/usr/bin/env python3
"""
Script 212 — Two-Gate Nested Architecture: Envelope + Cycle

INSIGHT (Dylan):
  We've been gating the Sun's overall ARA and its internal cycles
  with the SAME gate shape. But they're at different scales.

  The Gleissberg envelope (φ⁹ ≈ 76yr) is the Sun's SYSTEM-LEVEL ARA.
  It should gate at φ (0.618 accumulation) — the natural ARA.

  The Schwabe cycle (~11yr) is ONE SCALE DOWN — the Sun's internal
  cycle-level ARA. The drain compresses this to ~0.400 accumulation.

  Two nested gates:
    OUTER gate: Gleissberg scale, acc_frac = 0.618 (φ-ARA)
      → Controls the amplitude envelope
      → This is what gives temporal prediction power (207: 3/7 splits)

    INNER gate: Schwabe scale, acc_frac ≈ 0.400 (drain-compressed)
      → Controls individual cycle shape
      → This is what improves per-cycle fit (211: -25.3%)

  The outer gate modulates the inner gate's BASE LEVEL.
  The inner gate modulates the CASCADE within each cycle.

MODELS:
  V1: Static two-gate — outer=0.618, inner=0.400 (both fixed)
  V2: Causal outer — outer gate set by 207's causal mechanism
      (prev amplitude → acc_frac), inner=0.400
  V3: Causal both — outer=causal(prev amp), inner=causal(prev RF via Waldmeier)
  V4: V3 + dynamic drain
  V5: Full model — V4 + Gleissberg phase modulation of drain

FREE PARAMETERS: 2 (base_amp, t_ref)
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
rise_fracs = (peak_years - start_years) / durations
N = len(cycle_nums)
MEAN_AMP = peak_amps.mean()
MEAN_RF = rise_fracs.mean()  # ≈ 0.400

# Cascade: outer two are Gleissberg-scale, inner two are Schwabe-scale
CASCADE_OUTER = [PHI**11, PHI**9]   # ~199yr, ~76yr — envelope
CASCADE_INNER = [PHI**6, PHI**4]    # ~17.9yr, ~6.85yr — cycle
GLEISSBERG = PHI**9
SCHWABE = PHI**5  # ~11.09yr

# Gate fractions
OUTER_ACC = PHI / (PHI + 1)  # 0.618 — system-level ARA (natural)
INNER_ACC = MEAN_RF           # 0.400 — cycle-level ARA (drain-compressed)

# Waldmeier regression for estimating RF from amplitude
wald_coeffs = np.polyfit(peak_amps, rise_fracs, 1)
wald_pred_rf = lambda amp: np.clip(wald_coeffs[0] * amp + wald_coeffs[1], 0.15, 0.85)


def mae(p, o):
    return np.mean(np.abs(np.array(p) - np.array(o)))


def sawtooth_valve(phase, acc_frac):
    """ARA-asymmetric sawtooth gate."""
    acc_frac = max(0.15, min(0.85, acc_frac))
    cycle_pos = (phase % (2 * np.pi)) / (2 * np.pi)
    if cycle_pos < acc_frac:
        state = (cycle_pos / acc_frac) * PHI
    else:
        ramp = (cycle_pos - acc_frac) / (1 - acc_frac)
        state = PHI * (1 - ramp) + INV_PHI * ramp
    return state / ((PHI + INV_PHI) / 2)


def ara_to_acc(ara_value):
    """ARA → accumulation fraction."""
    return 1.0 / (1.0 + max(0.01, ara_value))


# =================================================================
# TWO-GATE PREDICTION
# =================================================================

def predict_two_gate(t, base_amp, t_ref, outer_acc, inner_acc, use_drain=False):
    """
    Two nested gates at two scales.

    OUTER gate (Gleissberg): modulates overall amplitude envelope.
      Operates on CASCADE_OUTER = [φ¹¹, φ⁹]
      acc_frac = outer_acc (default 0.618 = natural ARA)

    INNER gate (Schwabe): modulates cycle-level shape.
      Operates on CASCADE_INNER = [φ⁶, φ⁴]
      acc_frac = inner_acc (default 0.400 = drain-compressed)

    The outer gate feeds INTO the inner gate:
      outer output → base level for inner cascade
    """
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    schwabe_phase = 2 * np.pi * (t - t_ref) / SCHWABE

    # OUTER gate: Gleissberg-scale envelope
    outer_gate = sawtooth_valve(gleiss_phase, outer_acc)

    # Outer cascade: long-period modulation
    amp = base_amp
    for period in CASCADE_OUTER:
        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * outer_gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    # INNER gate: Schwabe-scale cycle shape
    inner_gate = sawtooth_valve(schwabe_phase, inner_acc)

    # Inner cascade: cycle-level modulation
    for period in CASCADE_INNER:
        phase = 2 * np.pi * (t - t_ref) / period
        wave = np.cos(phase)
        tension = -np.sin(phase)
        eps = INV_PHI_4 * inner_gate
        if tension > 0:
            eps *= (1 + 0.5 * tension * (PHI - 1))
        else:
            eps *= (1 + 0.5 * tension * (1 - INV_PHI))
        amp *= (1 + eps * wave)

    if use_drain:
        # Dynamic drain: scales with amplitude and Gleissberg phase
        amp_ratio = amp / base_amp
        amp -= INV_PHI_9 * amp * amp_ratio * abs(np.cos(gleiss_phase))
    else:
        # Static residual
        amp += base_amp * INV_PHI_9 * np.cos(gleiss_phase)

    return amp


# === MODEL WRAPPERS ===

def predict_203b(t, base_amp, t_ref):
    """Baseline: single gate at 0.618 on all 4 periods."""
    gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
    gate = sawtooth_valve(gleiss_phase, OUTER_ACC)
    amp = base_amp
    for period in CASCADE_OUTER + CASCADE_INNER:
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
    """V1: Static two-gate — outer=0.618, inner=0.400."""
    return predict_two_gate(t, base_amp, t_ref, OUTER_ACC, INNER_ACC, False)


def predict_v1d(t, base_amp, t_ref):
    """V1d: Static two-gate + drain."""
    return predict_two_gate(t, base_amp, t_ref, OUTER_ACC, INNER_ACC, True)


def predict_v2_seq(years, amps_prev, base_amp, t_ref):
    """V2: Causal outer gate (207), static inner (0.400)."""
    preds = []
    for i, t in enumerate(years):
        if i == 0:
            outer = OUTER_ACC
        else:
            prev_ara = amps_prev[i - 1] / base_amp
            outer = ara_to_acc(prev_ara)
        preds.append(predict_two_gate(t, base_amp, t_ref, outer, INNER_ACC, False))
    return preds


def predict_v2d_seq(years, amps_prev, base_amp, t_ref):
    """V2d: Causal outer + static inner + drain."""
    preds = []
    for i, t in enumerate(years):
        if i == 0:
            outer = OUTER_ACC
        else:
            prev_ara = amps_prev[i - 1] / base_amp
            outer = ara_to_acc(prev_ara)
        preds.append(predict_two_gate(t, base_amp, t_ref, outer, INNER_ACC, True))
    return preds


def predict_v3_seq(years, amps_prev, base_amp, t_ref):
    """V3: Causal outer (prev amp) + causal inner (Waldmeier-estimated RF)."""
    preds = []
    for i, t in enumerate(years):
        if i == 0:
            outer = OUTER_ACC
            inner = INNER_ACC
        else:
            prev_ara = amps_prev[i - 1] / base_amp
            outer = ara_to_acc(prev_ara)
            inner = wald_pred_rf(amps_prev[i - 1])
        preds.append(predict_two_gate(t, base_amp, t_ref, outer, inner, False))
    return preds


def predict_v3d_seq(years, amps_prev, base_amp, t_ref):
    """V3d: Causal outer + causal inner + drain."""
    preds = []
    for i, t in enumerate(years):
        if i == 0:
            outer = OUTER_ACC
            inner = INNER_ACC
        else:
            prev_ara = amps_prev[i - 1] / base_amp
            outer = ara_to_acc(prev_ara)
            inner = wald_pred_rf(amps_prev[i - 1])
        preds.append(predict_two_gate(t, base_amp, t_ref, outer, inner, True))
    return preds


def predict_v4_seq(years, amps_prev, base_amp, t_ref):
    """V4: Causal outer + observed prev RF as inner gate."""
    preds = []
    for i, t in enumerate(years):
        if i == 0:
            outer = OUTER_ACC
            inner = INNER_ACC
        else:
            prev_ara = amps_prev[i - 1] / base_amp
            outer = ara_to_acc(prev_ara)
            inner = rise_fracs[i - 1]  # actual observed RF of prev cycle
        preds.append(predict_two_gate(t, base_amp, t_ref, outer, inner, False))
    return preds


def predict_v4d_seq(years, amps_prev, base_amp, t_ref):
    """V4d: V4 + drain."""
    preds = []
    for i, t in enumerate(years):
        if i == 0:
            outer = OUTER_ACC
            inner = INNER_ACC
        else:
            prev_ara = amps_prev[i - 1] / base_amp
            outer = ara_to_acc(prev_ara)
            inner = rise_fracs[i - 1]
        preds.append(predict_two_gate(t, base_amp, t_ref, outer, inner, True))
    return preds


# =================================================================
# FITTING + EVALUATION
# =================================================================

def fit_simple(pred_fn, train_y, train_a):
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(train_a) * 0.6,
                               np.mean(train_a) * 1.4, 40):
            preds = [pred_fn(t, ba, t_ref) for t in train_y]
            m = mae(preds, train_a)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


def fit_seq(pred_fn, train_mask, all_years, all_amps):
    best_mae, best_ba, best_tr = 1e9, 0, 0
    idx = np.where(train_mask)[0]
    train_a = peak_amps[train_mask]
    for t_ref in np.linspace(1700, 1850, 60):
        for ba in np.linspace(np.mean(train_a) * 0.6,
                               np.mean(train_a) * 1.4, 40):
            all_p = pred_fn(all_years, all_amps, ba, t_ref)
            train_p = [all_p[j] for j in idx]
            m = mae(train_p, train_a)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


def evaluate(label, pred_fn, is_seq=False):
    """Full evaluation: LOO + temporal splits + diagnostics."""
    phi_e, sine_e = [], []
    full_mask = np.ones(N, dtype=bool)

    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        if is_seq:
            ba_i, tr_i, _ = fit_seq(pred_fn, mask, peak_years, peak_amps)
            all_p = pred_fn(peak_years, peak_amps, ba_i, tr_i)
            pred_i = all_p[i]
        else:
            ba_i, tr_i, _ = fit_simple(pred_fn, peak_years[mask], peak_amps[mask])
            pred_i = pred_fn(peak_years[i], ba_i, tr_i)
        phi_e.append(abs(pred_i - peak_amps[i]))
        sine_e.append(abs(np.mean(peak_amps[mask]) - peak_amps[i]))

    phi_e = np.array(phi_e)
    sine_e = np.array(sine_e)
    loo = phi_e.mean()
    sine_loo = sine_e.mean()
    n_wins = int(np.sum(phi_e < sine_e))

    # Full fit for diagnostics
    if is_seq:
        ba_f, tr_f, _ = fit_seq(pred_fn, full_mask, peak_years, peak_amps)
        pf = pred_fn(peak_years, peak_amps, ba_f, tr_f)
    else:
        ba_f, tr_f, _ = fit_simple(pred_fn, peak_years, peak_amps)
        pf = [pred_fn(t, ba_f, tr_f) for t in peak_years]

    errs = np.array(pf) - peak_amps
    rise_r = np.corrcoef(rise_fracs, errs)[0, 1]
    amp_r = np.corrcoef(peak_amps, errs)[0, 1]

    # Temporal splits
    sw = 0
    sr = []
    for nt in [5, 8, 10, 12, 15, 18, 20]:
        if nt >= N:
            continue
        t_mask = np.zeros(N, dtype=bool)
        t_mask[:nt] = True
        if is_seq:
            ba_s, tr_s, _ = fit_seq(pred_fn, t_mask, peak_years, peak_amps)
            ap = pred_fn(peak_years, peak_amps, ba_s, tr_s)
            tp = ap[nt:]
        else:
            ba_s, tr_s, _ = fit_simple(pred_fn, peak_years[:nt], peak_amps[:nt])
            tp = [pred_fn(t, ba_s, tr_s) for t in peak_years[nt:]]
        ta = peak_amps[nt:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:nt].mean()), ta)
        w = "φ" if pm < sm else "sine"
        if pm < sm:
            sw += 1
        sr.append((nt, N - nt, pm, sm, w))

    return {
        'label': label, 'loo': loo, 'sine_loo': sine_loo,
        'imp': (loo / sine_loo - 1) * 100,
        'wins': n_wins, 'rise_r': rise_r, 'amp_r': amp_r,
        'splits': sw, 'split_detail': sr,
        'preds': pf, 'ba': ba_f, 'tr': tr_f,
    }


# =================================================================
# MAIN
# =================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("SCRIPT 212 — TWO-GATE NESTED ARCHITECTURE")
    print("=" * 70)

    print(f"""
  Two gates at two scales:
    OUTER (Gleissberg, ��⁹≈76yr): acc_frac = 0.618 (natural ARA)
      CASCADE_OUTER = [φ¹¹={PHI**11:.1f}yr, φ⁹={PHI**9:.1f}yr]

    INNER (Schwabe, φ⁵≈11yr): acc_frac = 0.400 (drain-compressed)
      CASCADE_INNER = [φ⁶={PHI**6:.1f}yr, φ⁴={PHI**4:.1f}yr]

  The outer gate modulates amplitude.
  The inner gate modulates cycle shape.
  They're at different scales — different AR values.

  Waldmeier regression: RF = {wald_coeffs[0]:.5f} × amp + {wald_coeffs[1]:.3f}
  (r = {np.corrcoef(peak_amps, rise_fracs)[0,1]:+.3f})
    """)

    results = []

    # Baseline
    print(f"{'='*70}")
    print("BASELINE — 203b (single gate=0.618, all 4 periods)")
    print(f"{'='*70}")
    r = evaluate("203b single gate", predict_203b)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # V1: Static two-gate
    print(f"\n{'='*70}")
    print("V1 — STATIC TWO-GATE (outer=0.618, inner=0.400)")
    print(f"{'='*70}")
    r = evaluate("V1 static 2-gate", predict_v1)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # V1d: Static two-gate + drain
    print(f"\n{'='*70}")
    print("V1d — STATIC TWO-GATE + DRAIN")
    print(f"{'='*70}")
    r = evaluate("V1d 2-gate+drain", predict_v1d)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # V2: Causal outer, static inner
    print(f"\n{'='*70}")
    print("V2 — CAUSAL OUTER + STATIC INNER (0.400)")
    print(f"{'='*70}")
    r = evaluate("V2 causal outer", predict_v2_seq, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # V2d: Causal outer + static inner + drain
    print(f"\n{'='*70}")
    print("V2d — CAUSAL OUTER + STATIC INNER + DRAIN")
    print(f"{'='*70}")
    r = evaluate("V2d causal+drain", predict_v2d_seq, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # V3: Causal both (Waldmeier-estimated inner)
    print(f"\n{'='*70}")
    print("V3 — CAUSAL BOTH (outer=prev amp, inner=Waldmeier-est RF)")
    print(f"{'='*70}")
    r = evaluate("V3 causal both", predict_v3_seq, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # V3d: Causal both + drain
    print(f"\n{'='*70}")
    print("V3d — CAUSAL BOTH + DRAIN")
    print(f"{'='*70}")
    r = evaluate("V3d causal+drain", predict_v3d_seq, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # V4: Causal outer + observed prev RF as inner
    print(f"\n{'='*70}")
    print("V4 — CAUSAL OUTER + OBSERVED PREV RF INNER (oracle-ish)")
    print(f"{'='*70}")
    r = evaluate("V4 obs prev RF", predict_v4_seq, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # V4d: V4 + drain
    print(f"\n{'='*70}")
    print("V4d — CAUSAL OUTER + OBSERVED PREV RF + DRAIN")
    print(f"{'='*70}")
    r = evaluate("V4d obs RF+drain", predict_v4d_seq, is_seq=True)
    results.append(r)
    print(f"  LOO={r['loo']:.2f} ({r['imp']:+.1f}%), {r['wins']}/25, "
          f"rise r={r['rise_r']:+.3f}, splits={r['splits']}/7")

    # === COMPARISON ===
    print(f"\n{'='*70}")
    print("FULL COMPARISON")
    print(f"{'='*70}")

    print(f"\n  {'Model':<22s} {'LOO':>7s} {'vs sine':>8s} {'Wins':>5s} "
          f"{'Rise r':>7s} {'Amp r':>7s} {'Splits':>6s}")
    print(f"  {'-'*22} {'-'*7} {'-'*8} {'-'*5} {'-'*7} {'-'*7} {'-'*6}")
    for r in results:
        print(f"  {r['label']:<22s} {r['loo']:7.2f} {r['imp']:+7.1f}% "
              f"{r['wins']:3d}/25 {r['rise_r']:+7.3f} {r['amp_r']:+7.3f} "
              f"{r['splits']:2d}/7")

    best_loo = min(results, key=lambda r: r['loo'])
    best_wald = min(results, key=lambda r: abs(r['rise_r']))
    best_split = max(results, key=lambda r: r['splits'])

    print(f"\n  BEST LOO: {best_loo['label']} ({best_loo['loo']:.2f}, "
          f"{best_loo['imp']:+.1f}%)")
    print(f"  BEST WALDMEIER: {best_wald['label']} (r={best_wald['rise_r']:+.3f})")
    print(f"  BEST SPLITS: {best_split['label']} ({best_split['splits']}/7)")

    # Temporal split details for top models
    print(f"\n{'='*70}")
    print("TEMPORAL SPLITS — TOP MODELS")
    print(f"{'='*70}")

    shown = set()
    for r in [best_loo, best_split, best_wald]:
        if r['label'] in shown:
            continue
        shown.add(r['label'])
        print(f"\n  {r['label']}: {r['splits']}/7 splits")
        for nt, ntest, pm, sm, w in r['split_detail']:
            margin = sm - pm if w == "φ" else pm - sm
            print(f"    Train {nt:2d} / Test {ntest:2d}: "
                  f"φ={pm:.1f}  sine={sm:.1f}  → {w} ({margin:.1f})")

    # Per-cycle for best LOO
    print(f"\n{'='*70}")
    print(f"PER-CYCLE — {best_loo['label']}")
    print(f"{'='*70}")
    print(f"\n  {'Cyc':>3s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'RF':>6s}")
    for i, c in enumerate(cycle_nums):
        p = best_loo['preds'][i]
        print(f"  {c:3d} {peak_amps[i]:7.1f} {p:7.1f} "
              f"{p - peak_amps[i]:+7.1f} {rise_fracs[i]:6.3f}")

    # === KEY INSIGHT: compare single vs two gate ===
    print(f"\n{'='*70}")
    print("KEY COMPARISON: SINGLE GATE vs TWO GATE")
    print(f"{'='*70}")

    # Reference results from previous scripts
    print(f"""
  Previous best models (from Scripts 203b-211):
    203b (single gate=0.618):           LOO=37.66, splits=1/7
    207 V1 (causal single gate):        LOO=38.82, splits=3/7 ← extrap champ
    209 V5 (causal+drain, single):      LOO=36.97, splits=2/7
    210 V5 (causal+AR drain, single):   LOO=36.62, splits=2/7
    211 V4d (Wald gate+drain, single):  LOO=36.46, splits=0/7 ← interp champ

  This script (two-gate):
    Best LOO:    {best_loo['label']}: {best_loo['loo']:.2f} ({best_loo['imp']:+.1f}%), splits={best_loo['splits']}/7
    Best splits: {best_split['label']}: {best_split['loo']:.2f} ({best_split['imp']:+.1f}%), splits={best_split['splits']}/7
    Best Wald:   {best_wald['label']}: rise r={best_wald['rise_r']:+.3f}
    """)

    print(f"{'='*70}")
    print("SUMMARY — SCRIPT 212")
    print(f"{'='*70}")
    print(f"""
  Two-gate architecture: outer (Gleissberg, φ-ARA) + inner (Schwabe, observed AR)

  The Sun's SYSTEM-LEVEL ARA operates at φ (0.618 accumulation).
  The Sun's CYCLE-LEVEL ARA is drain-compressed to ~0.400.
  These are different scales — different gates.

  BEST LOO: {best_loo['label']}
    MAE = {best_loo['loo']:.2f} ({best_loo['imp']:+.1f}% vs sine)
    Wins: {best_loo['wins']}/25
    Rise frac r = {best_loo['rise_r']:+.3f}
    Splits: {best_loo['splits']}/7

  ARCHITECTURE (for forward prediction):
    1. Outer gate: Gleissberg phase → sawtooth(acc=0.618 or causal)
       Operates on φ¹¹ and φ⁹ periods
    2. Inner gate: Schwabe phase → sawtooth(acc=0.400 or Waldmeier-est)
       Operates on φ⁶ and φ⁴ periods
    3. Drain: 1/φ⁹ × dynamic amplitude scaling
    4. All causal inputs from previous cycle
""")
