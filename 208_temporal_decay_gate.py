#!/usr/bin/env python3
"""
Script 208 — Temporal Decay Gate: Memory That Breathes and Fades

INSIGHT (Dylan):
  "We're missing an external ARA — the gate needs a decay factor over
  steps, accumulating temporal tension and releasing it over time.
  Temporal tension feeds back into the cycle, eating itself."

ARCHITECTURE:
  Gate memory = φ-weighted exponential decay of all previous cycles:
    effective_state = Σ (1/φ)^k × amp[n-k-1] / Σ (1/φ)^k

  Temporal tension release: as distance from last observation grows,
  gate relaxes back toward static attractor (0.618).

  This prevents error compounding — each step back reduces influence
  by 1/φ, so old errors decay rather than accumulate.

MODELS:
  V1: φ-decay memory (all past cycles, weighted by 1/φ per step)
  V2: φ-decay + tension release (gate relaxes to 0.618 over time)
  V3: φ-decay memory, self-feeding (no observed data needed)
  V4: Two-rate decay — fast (1/φ) for recent + slow (1/φ²) for deep memory
  V5: Full external ARA — decay gate + Gleissberg modulation
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

CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
GLEISSBERG = PHI**9
STATIC_ACC = PHI / (PHI + 1)  # 0.618

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
    return 1.0 / (1.0 + ara_value)


# ================================================================
# φ-DECAY MEMORY FUNCTIONS
# ================================================================

def phi_decay_memory(past_amps, base_amp, decay=None):
    """Compute effective ARA from φ-weighted history.
    Most recent = weight 1, then 1/φ, 1/φ², ...
    Returns effective ARA value."""
    if decay is None:
        decay = INV_PHI
    if len(past_amps) == 0:
        return 1.0  # Neutral
    weights = np.array([decay**k for k in range(len(past_amps))])
    # past_amps[0] is most recent, [-1] is oldest
    weighted_amp = np.sum(weights * past_amps) / np.sum(weights)
    return weighted_amp / base_amp


def two_rate_memory(past_amps, base_amp):
    """Two-rate decay: fast (1/φ) for recent 3 + slow (1/φ²) for rest."""
    if len(past_amps) == 0:
        return 1.0
    fast_depth = min(3, len(past_amps))
    weights = []
    for k in range(len(past_amps)):
        if k < fast_depth:
            weights.append(INV_PHI ** k)
        else:
            weights.append(INV_PHI ** fast_depth * (INV_PHI**2) ** (k - fast_depth))
    weights = np.array(weights)
    weighted_amp = np.sum(weights * past_amps) / np.sum(weights)
    return weighted_amp / base_amp


# ================================================================
# V1: φ-decay memory (observed history)
# ================================================================

def predict_v1_sequence(peak_years_seq, peak_amps_obs, base_amp, t_ref):
    preds = []
    for i, t in enumerate(peak_years_seq):
        # Collect past amplitudes (most recent first)
        past = list(reversed(peak_amps_obs[:i].tolist())) if i > 0 else []
        eff_ara = phi_decay_memory(past, base_amp)
        acc_frac = ara_to_acc(eff_ara)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# V2: φ-decay + tension release
# Gate relaxes toward STATIC_ACC as memory ages
# Blend = total_weight / φ (never reaches 1, approaches 0 with no data)
# ================================================================

def predict_v2_sequence(peak_years_seq, peak_amps_obs, base_amp, t_ref):
    preds = []
    for i, t in enumerate(peak_years_seq):
        past = list(reversed(peak_amps_obs[:i].tolist())) if i > 0 else []
        if len(past) == 0:
            acc_frac = STATIC_ACC
        else:
            eff_ara = phi_decay_memory(past, base_amp)
            dynamic_acc = ara_to_acc(eff_ara)
            # Tension release: blend strength based on total memory weight
            # Sum of 1/φ^k from k=0 to n-1 = (1 - (1/φ)^n) / (1 - 1/φ)
            n = len(past)
            total_weight = (1 - INV_PHI**n) / (1 - INV_PHI)
            max_weight = PHI  # Limit of geometric sum = 1/(1-1/φ) = φ
            blend = min(total_weight / max_weight, 1.0)  # 0→1 as memory fills
            # With full memory, blend→1 (fully dynamic)
            # With little memory, blend→0 (falls back to static)
            acc_frac = STATIC_ACC + blend * (dynamic_acc - STATIC_ACC)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# V3: φ-decay self-feeding (model's own predictions as memory)
# ================================================================

def predict_v3_sequence(peak_years_seq, base_amp, t_ref):
    preds = []
    for i, t in enumerate(peak_years_seq):
        past = list(reversed(preds[:i])) if i > 0 else []
        eff_ara = phi_decay_memory(past, base_amp)
        acc_frac = ara_to_acc(eff_ara)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# V4: Two-rate decay (fast recent + slow deep memory)
# ================================================================

def predict_v4_sequence(peak_years_seq, peak_amps_obs, base_amp, t_ref):
    preds = []
    for i, t in enumerate(peak_years_seq):
        past = list(reversed(peak_amps_obs[:i].tolist())) if i > 0 else []
        if len(past) == 0:
            eff_ara = 1.0
        else:
            eff_ara = two_rate_memory(past, base_amp)
        acc_frac = ara_to_acc(eff_ara)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# V5: φ-decay + Gleissberg external ARA
# The Gleissberg cycle modulates HOW MUCH the memory matters
# Near Gleissberg peak: memory dominates (strong coupling)
# Near Gleissberg trough: static dominates (weak coupling)
# This IS the external ARA — it controls the coupling transparency
# ================================================================

def predict_v5_sequence(peak_years_seq, peak_amps_obs, base_amp, t_ref):
    preds = []
    for i, t in enumerate(peak_years_seq):
        gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
        gleiss_coupling = 0.5 * (1 + np.cos(gleiss_phase))

        past = list(reversed(peak_amps_obs[:i].tolist())) if i > 0 else []
        if len(past) == 0:
            acc_frac = STATIC_ACC
        else:
            eff_ara = phi_decay_memory(past, base_amp)
            dynamic_acc = ara_to_acc(eff_ara)
            # Gleissberg modulates the coupling strength
            acc_frac = STATIC_ACC + gleiss_coupling * (dynamic_acc - STATIC_ACC)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# V6: φ-decay + tension release + Gleissberg (V2 + V5 combined)
# ================================================================

def predict_v6_sequence(peak_years_seq, peak_amps_obs, base_amp, t_ref):
    preds = []
    for i, t in enumerate(peak_years_seq):
        gleiss_phase = 2 * np.pi * (t - t_ref) / GLEISSBERG
        gleiss_coupling = 0.5 * (1 + np.cos(gleiss_phase))

        past = list(reversed(peak_amps_obs[:i].tolist())) if i > 0 else []
        if len(past) == 0:
            acc_frac = STATIC_ACC
        else:
            eff_ara = phi_decay_memory(past, base_amp)
            dynamic_acc = ara_to_acc(eff_ara)
            n = len(past)
            total_weight = (1 - INV_PHI**n) / (1 - INV_PHI)
            memory_blend = min(total_weight / PHI, 1.0)
            # Both memory fullness AND Gleissberg coupling must be strong
            blend = memory_blend * gleiss_coupling
            acc_frac = STATIC_ACC + blend * (dynamic_acc - STATIC_ACC)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# BASELINE
# ================================================================

def predict_static_sequence(peak_years_seq, base_amp, t_ref):
    return [cascade_core(t, base_amp, t_ref) for t in peak_years_seq]

def predict_207v1_sequence(peak_years_seq, peak_amps_obs, base_amp, t_ref):
    """Script 207 V1 for reference: single previous cycle, no decay."""
    preds = []
    for i, t in enumerate(peak_years_seq):
        if i == 0:
            prev_ara = 1.0
        else:
            prev_ara = peak_amps_obs[i-1] / base_amp
        acc_frac = ara_to_acc(prev_ara)
        pred = cascade_core(t, base_amp, t_ref, acc_frac)
        preds.append(pred)
    return preds


# ================================================================
# FITTING & EVALUATION
# ================================================================

def fit_seq(pred_fn, train_y, train_a, needs_obs=False):
    best_mae, best_ba, best_tr = 1e9, 0, 0
    for t_ref in np.linspace(1700, 1850, 50):
        for ba in np.linspace(np.mean(train_a)*0.6, np.mean(train_a)*1.4, 35):
            if needs_obs:
                preds = pred_fn(train_y, train_a, ba, t_ref)
            else:
                preds = pred_fn(train_y, ba, t_ref)
            m = mae(preds, train_a)
            if m < best_mae:
                best_mae, best_ba, best_tr = m, ba, t_ref
    return best_ba, best_tr, best_mae


def eval_model(name, pred_fn, needs_obs=False):
    print(f"\n{'='*72}")
    print(f"  {name}")
    print(f"{'='*72}")

    # LOO
    phi_errs, sine_errs = [], []
    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        ba_i, tr_i, _ = fit_seq(pred_fn, peak_years[mask], peak_amps[mask], needs_obs)
        if needs_obs:
            full_preds = pred_fn(peak_years[:i+1], peak_amps[:i+1], ba_i, tr_i)
        else:
            full_preds = pred_fn(peak_years[:i+1], ba_i, tr_i)
        pred_i = full_preds[-1]
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
        ba_s, tr_s, _ = fit_seq(pred_fn, peak_years[:n_train],
                                 peak_amps[:n_train], needs_obs)
        if needs_obs:
            full_p = pred_fn(peak_years, peak_amps, ba_s, tr_s)
        else:
            full_p = pred_fn(peak_years, ba_s, tr_s)
        tp = full_p[n_train:]
        ta = peak_amps[n_train:]
        pm = mae(tp, ta)
        sm = mae(np.full(len(ta), peak_amps[:n_train].mean()), ta)
        w = "φ" if pm < sm else "sine"
        if pm < sm: sw += 1
        print(f"    Train {n_train:2d} / Test {N-n_train:2d}: φ={pm:.1f} sine={sm:.1f} → {w}")
    print(f"  Temporal splits: {sw}/7")

    # Per-cycle at full fit
    ba_f, tr_f, _ = fit_seq(pred_fn, peak_years, peak_amps, needs_obs)
    if needs_obs:
        pf = pred_fn(peak_years, peak_amps, ba_f, tr_f)
    else:
        pf = pred_fn(peak_years, ba_f, tr_f)

    errs = np.array(pf) - peak_amps
    rise_fracs = np.array([(CYCLES[c][1]-CYCLES[c][0])/CYCLES[c][3]
                            for c in cycle_nums])
    print(f"\n  Error correlations:")
    print(f"    Rise fraction:   r = {np.corrcoef(errs, rise_fracs)[0,1]:+.3f}")
    print(f"    Peak amplitude:  r = {np.corrcoef(errs, peak_amps)[0,1]:+.3f}")

    return loo, pct, wins, boot/n_boot*100, sw


if __name__ == '__main__':
    print("=" * 72)
    print("SCRIPT 208 — TEMPORAL DECAY GATE")
    print("Memory that breathes and fades")
    print("=" * 72)

    print(f"\n  Decay rate: 1/φ = {INV_PHI:.4f} per cycle step")
    print(f"  Memory depth (99% captured): {int(np.log(0.01)/np.log(INV_PHI))+1} cycles")
    print(f"  Geometric sum limit: φ = {PHI:.4f}")

    # Show decay weights
    print(f"\n  φ-decay weights (most recent first):")
    for k in range(10):
        w = INV_PHI ** k
        print(f"    k={k}: weight = {w:.4f} ({w/PHI*100:.1f}% of total)")

    results = {}

    r = eval_model("BASELINE: Static 203b",
                   predict_static_sequence, needs_obs=False)
    results['Static'] = r

    r = eval_model("207-V1: Single previous (no decay)",
                   predict_207v1_sequence, needs_obs=True)
    results['207_V1'] = r

    r = eval_model("V1: φ-decay memory (observed)",
                   predict_v1_sequence, needs_obs=True)
    results['V1_decay'] = r

    r = eval_model("V2: φ-decay + tension release",
                   predict_v2_sequence, needs_obs=True)
    results['V2_release'] = r

    r = eval_model("V3: φ-decay self-feeding",
                   predict_v3_sequence, needs_obs=False)
    results['V3_self'] = r

    r = eval_model("V4: Two-rate decay (fast+slow)",
                   predict_v4_sequence, needs_obs=True)
    results['V4_2rate'] = r

    r = eval_model("V5: φ-decay + Gleissberg external ARA",
                   predict_v5_sequence, needs_obs=True)
    results['V5_ext'] = r

    r = eval_model("V6: Full — decay + release + Gleissberg",
                   predict_v6_sequence, needs_obs=True)
    results['V6_full'] = r

    # === SUMMARY ===
    print(f"\n{'='*72}")
    print("SUMMARY")
    print(f"{'='*72}")
    print(f"  {'Model':<42s} {'LOO':>7s} {'vs%':>7s} {'W':>4s} {'Boot':>5s} {'TS':>4s}")
    print(f"  {'-'*42} {'-'*7} {'-'*7} {'-'*4} {'-'*5} {'-'*4}")
    for name, (loo, pct, wins, boot, sw) in results.items():
        print(f"  {name:<42s} {loo:7.2f} {pct:+6.1f}% {wins:3d} {boot:5.1f} {sw:3d}")

    best = min(results.keys(), key=lambda k: results[k][0])
    b = results[best]
    print(f"\n  BEST: {best}")
    print(f"    LOO = {b[0]:.2f} ({b[1]:+.1f}% vs sine)")
    print(f"    Temporal splits: {b[4]}/7")

    best_splits = max(r[4] for r in results.values())
    best_split_model = [k for k, r in results.items() if r[4] == best_splits][0]
    print(f"\n  BEST TEMPORAL: {best_split_model} with {best_splits}/7 splits")

    # Rise fraction correlation comparison
    print(f"\n  Rise fraction correlation progression:")
    print(f"    (Lower = less Waldmeier distortion)")

    print(f"\n{'='*72}")
    print("END SCRIPT 208")
    print(f"{'='*72}")
