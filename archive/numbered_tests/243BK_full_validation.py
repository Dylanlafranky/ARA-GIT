#!/usr/bin/env python3
"""
Script 243BK — Full Pipeline Validation

Runs the updated 243AZ base code (camshaft-E midline + ARA-circle stretch)
through the COMPLETE champion pipeline for ALL available systems:

  1. Solar (SSN) — 25 cycles, ARA=φ (engine), period=φ⁵
  2. ENSO (ONI)  — 23 events, ARA=2.0 (near-harmonic), period=φ³
  3. Sanriku EQ  — 10 events, ARA=0.15 (deep consumer), period=φ⁴
  4. Heart (Mayer wave) — 30 peaks, ARA=1.35 (near-clock), period=10s

Pipeline for each system:
  Phase 1: Teleport LOO (formula-only, refit per fold)
  Phase 2: Path LOO (vehicle-style, refit per fold)
  Phase 3: Blend at α = 1/φ²
  Phase 4: ARA-circle stretch: 1 + (ARA/φ) × 1/φ⁵

Reports: LOO MAE, LOO/Sine ratio, correlation, per-cycle errors.
Compares against known baselines from previous sessions.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
INV_PHI_5 = INV_PHI ** 5
BLEND_ALPHA = INV_PHI_2  # ≈ 0.382

# ════════════════════════════════════════════════════════════════
# Load the updated 243AZ base code (everything up to # MAIN)
# ════════════════════════════════════════════════════════════════

combo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "243AZ_wave_combo.py")
with open(combo_path, 'r') as f:
    combo_code = f.read()

lines = combo_code.split('\n')
cutoff = len(lines)
for i, line in enumerate(lines):
    if '# MAIN' in line and i > 400:
        cutoff = i
        break
base_code = '\n'.join(lines[:cutoff])

# Execute base code to get all functions and data
ns = {'__file__': combo_path, '__name__': '__exec__'}
exec(base_code, ns)

# Extract what we need
EngineMemoryNode = ns['EngineMemoryNode']
grid_search = ns['grid_search']
run_full_simulation = ns['run_full_simulation']
run_formula_loo = ns['run_formula_loo']
ara_midline = ns['ara_midline']
ara_circle_stretch = ns['ara_circle_stretch']

# ════════════════════════════════════════════════════════════════
# DATA — all four systems
# ════════════════════════════════════════════════════════════════

# Solar — already in 243AZ
solar_t = ns['solar_t']
solar_a = ns['solar_a']
SOLAR_CYCLES = ns['SOLAR_CYCLES']

# ENSO — already in 243AZ
enso_t = ns['enso_t']
enso_a = ns['enso_a']

# Earthquake — already in 243AZ
eq_t = ns['eq_t']
eq_a = ns['eq_a']

# Heart (Mayer wave) — from 235b
MAYER_WAVE_PEAKS = [
    (  10, 5.2), ( 20, 7.1), ( 30, 8.3), ( 40, 6.5), ( 50, 4.8),
    ( 60, 3.9), ( 70, 5.5), ( 80, 7.8), ( 90, 9.1), (100, 7.2),
    (110, 5.6), (120, 4.1), (130, 5.8), (140, 8.0), (150, 6.9),
    (160, 5.3), (170, 6.4), (180, 8.7), (190, 7.6), (200, 5.1),
    (210, 3.8), (220, 5.9), (230, 7.5), (240, 8.8), (250, 6.3),
    (260, 4.5), (270, 5.7), (280, 7.3), (290, 6.1), (300, 4.9),
]
heart_t = np.array([m[0] for m in MAYER_WAVE_PEAKS])
heart_a = np.array([m[1] for m in MAYER_WAVE_PEAKS])

SYSTEMS = [
    # name, times, peaks, period, ARA, rung, known_baselines
    ("Solar (SSN)", solar_t, solar_a, PHI**5, PHI, 5, {
        'teleport_loo': 44.05,  # 243AZ wave combo
        'blend_loo': 38.73,     # 243BB
        'stretch_loo': 38.37,   # 243BF/BJ champion
        'sine_loo': 48.78,
    }),
    ("ENSO (ONI)", enso_t, enso_a, PHI**3, 2.0, 3, {
        'teleport_loo': 0.56,   # 243BB (regressed from 0.48 with wave physics)
        'blend_loo': None,
        'stretch_loo': None,
        'sine_loo': 0.53,       # approximate
    }),
    ("Sanriku EQ", eq_t, eq_a, PHI**4, 0.15, 4, {
        'teleport_loo': 0.99,   # 243BB (regressed from 0.63)
        'blend_loo': None,
        'stretch_loo': None,
        'sine_loo': 0.70,       # approximate
    }),
    ("Heart (Mayer)", heart_t, heart_a, 10.0, 1.35, 1, {
        'teleport_loo': None,
        'blend_loo': None,
        'stretch_loo': None,
        'sine_loo': None,       # will compute
    }),
]


# ═══════════════════════════════════════════════════════════���════
# PIPELINE FUNCTIONS
# ══════════════════════════════════════════════════════════════��═

def run_teleport_loo(times, peaks, period, ara, rung, name):
    """Phase 1: Teleport LOO — formula-only, refit per fold."""
    return run_formula_loo(times, peaks, period, ara, rung, name)


def run_path_loo(times, peaks, period, ara, rung, name):
    """Phase 2: Path LOO — simulate forward, refit per fold."""
    N = len(times)
    path_preds = []
    path_train_means = []

    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        train_t = times[mask]
        train_p = peaks[mask]
        path_train_means.append(np.mean(train_p))

        fit_tr, fit_ba, _ = grid_search(period, ara, rung, train_t, train_p)
        snap_t, snap_a = run_full_simulation(
            train_t, train_p, period, ara, rung, fit_tr, fit_ba)

        if len(snap_t) == 0:
            path_preds.append(np.mean(train_p))
        else:
            idx = np.argmin(np.abs(snap_t - times[i]))
            path_preds.append(snap_a[idx])

    path_preds = np.array(path_preds)
    path_train_means = np.array(path_train_means)
    errors = np.abs(path_preds - peaks)
    sine_errors = np.array([abs(peaks[i] - np.mean(peaks[np.arange(N) != i]))
                            for i in range(N)])

    return {
        'preds': path_preds,
        'train_means': path_train_means,
        'errors': errors,
        'loo_mae': np.mean(errors),
        'sine_mae': np.mean(sine_errors),
        'corr': np.corrcoef(path_preds, peaks)[0, 1] if N > 2 else 0,
    }


def run_blend(teleport_preds, path_result, peaks, alpha=BLEND_ALPHA):
    """Phase 3: Blend at α = 1/φ²."""
    blended = alpha * path_result['preds'] + (1 - alpha) * teleport_preds
    errors = np.abs(blended - peaks)
    N = len(peaks)

    # Error correlation between path and teleport
    path_err = path_result['preds'] - peaks
    tele_err = teleport_preds - peaks
    err_corr = np.corrcoef(path_err, tele_err)[0, 1] if N > 2 else 0

    return {
        'preds': blended,
        'errors': errors,
        'loo_mae': np.mean(errors),
        'corr': np.corrcoef(blended, peaks)[0, 1] if N > 2 else 0,
        'err_corr': err_corr,
        'train_means': path_result['train_means'],
    }


def run_stretch(blend_result, peaks, ara):
    """Phase 4: ARA-circle stretch."""
    N = len(peaks)
    stretched = np.zeros(N)
    factor = 1.0 + (ara / PHI) * INV_PHI_5

    for i in range(N):
        dev = blend_result['preds'][i] - blend_result['train_means'][i]
        stretched[i] = blend_result['train_means'][i] + dev * factor

    errors = np.abs(stretched - peaks)
    return {
        'preds': stretched,
        'errors': errors,
        'loo_mae': np.mean(errors),
        'corr': np.corrcoef(stretched, peaks)[0, 1] if N > 2 else 0,
        'factor': factor,
    }


# ════════════════════════════════════════════════════════════════
# MAIN — Run full pipeline on each system
# ════════════════════════════════════════════════════════════════

print("=" * 90)
print("  Script 243BK — Full Pipeline Validation (Updated 243AZ)")
print("  Camshaft-E midline + ARA-circle stretch")
print("  Pipeline: Teleport LOO → Path LOO → 1/φ² Blend → ARA-circle Stretch")
print("=" * 90)

# Show midline values for each system
print(f"\n  Midline values (camshaft-E):")
print(f"  {'System':20s} │ {'ARA':>6} │ {'Midline':>8} │ {'Stretch':>8} │ {'Role':>12}")
print(f"  {'─'*20}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*12}")
for name, _, _, _, ara, _, _ in SYSTEMS:
    mid = ara_midline(ara)
    stretch = 1.0 + (ara / PHI) * INV_PHI_5
    if ara >= PHI:
        role = "ENGINE"
    elif ara >= 1.0:
        role = "near-clock"
    elif ara >= INV_PHI:
        role = "consumer"
    else:
        role = "deep consumer"
    print(f"  {name:20s} │ {ara:>6.3f} │ {mid:>8.4f} │ {stretch:>8.4f} │ {role:>12}")

all_results = {}

for sys_name, times, peaks, period, ara, rung, baselines in SYSTEMS:
    print(f"\n{'═' * 90}")
    print(f"  SYSTEM: {sys_name} (N={len(times)}, ARA={ara:.3f}, period={period:.2f})")
    print(f"{'═' * 90}")

    N = len(times)
    sys_results = {'name': sys_name, 'N': N, 'ara': ara}

    # ── Phase 1: Teleport LOO ──
    print(f"\n  Phase 1: Teleport LOO ({N} folds)...", end="", flush=True)
    t0 = clock_time.time()
    tele = run_teleport_loo(times, peaks, period, ara, rung, sys_name)
    el = clock_time.time() - t0
    sys_results['teleport'] = tele
    base = baselines.get('teleport_loo')
    delta_str = f"Δ={tele['loo_mae'] - base:+.2f}" if base else "—"
    print(f"\r  Phase 1: Teleport LOO = {tele['loo_mae']:.3f}, "
          f"Sine = {tele['sine_mae']:.3f}, "
          f"LOO/Sine = {tele['ratio']:.3f}, "
          f"r = {tele['corr']:+.3f}, "
          f"prev = {base or '—'}, {delta_str} ({el:.0f}s)")

    # ── Phase 2: Path LOO ──
    print(f"  Phase 2: Path LOO ({N} folds)...", end="", flush=True)
    t0 = clock_time.time()
    path = run_path_loo(times, peaks, period, ara, rung, sys_name)
    el = clock_time.time() - t0
    sys_results['path'] = path
    print(f"\r  Phase 2: Path LOO    = {path['loo_mae']:.3f}, "
          f"LOO/Sine = {path['loo_mae']/path['sine_mae']:.3f}, "
          f"r = {path['corr']:+.3f} ({el:.0f}s)")

    # ── Phase 3: Blend ──
    blend = run_blend(tele['preds'], path, peaks)
    sys_results['blend'] = blend
    base_b = baselines.get('blend_loo')
    delta_b = f"Δ={blend['loo_mae'] - base_b:+.3f}" if base_b else "—"
    print(f"  Phase 3: Blend (1/φ²) = {blend['loo_mae']:.3f}, "
          f"r = {blend['corr']:+.3f}, "
          f"err_corr = {blend['err_corr']:+.3f}, "
          f"prev = {base_b or '—'}, {delta_b}")

    # ── Phase 4: Stretch ──
    stretch = run_stretch(blend, peaks, ara)
    sys_results['stretch'] = stretch
    base_s = baselines.get('stretch_loo')
    delta_s = f"Δ={stretch['loo_mae'] - base_s:+.3f}" if base_s else "—"
    sine_mae = tele['sine_mae']
    ls_ratio = stretch['loo_mae'] / sine_mae if sine_mae > 0 else 999
    print(f"  Phase 4: Stretch ({stretch['factor']:.4f}) = {stretch['loo_mae']:.3f}, "
          f"LOO/Sine = {ls_ratio:.3f}, "
          f"r = {stretch['corr']:+.3f}, "
          f"prev = {base_s or '—'}, {delta_s}")

    # ─�� Phase summary ──
    print(f"\n  Pipeline progression:")
    print(f"    Teleport  → {tele['loo_mae']:>8.3f}  (baseline)")
    improvement_bp = (1 - blend['loo_mae'] / tele['loo_mae']) * 100
    print(f"    + Blend   → {blend['loo_mae']:>8.3f}  ({improvement_bp:+.1f}%)")
    improvement_sp = (1 - stretch['loo_mae'] / blend['loo_mae']) * 100
    print(f"    + Stretch → {stretch['loo_mae']:>8.3f}  ({improvement_sp:+.1f}%)")
    total_imp = (1 - stretch['loo_mae'] / tele['loo_mae']) * 100
    print(f"    Total     → {total_imp:+.1f}% from teleport to final")

    beats_sine = "BEATS SINE" if ls_ratio < 1.0 else f"+{(ls_ratio-1)*100:.1f}% above sine"
    print(f"    vs Sine: {beats_sine}")

    # Blend independence check
    if abs(blend['err_corr']) > 0.3:
        print(f"    ⚠ Warning: error correlation {blend['err_corr']:+.3f} is high — blend may be degraded")
    else:
        print(f"    ✓ Error correlation {blend['err_corr']:+.3f} is low — blend is healthy")

    sys_results['final_loo'] = stretch['loo_mae']
    sys_results['final_ratio'] = ls_ratio
    all_results[sys_name] = sys_results


# ════════════════════════════════════════════════════════════════
# MASTER SUMMARY
# ════════════════════════════════════════════════════════════════

print(f"\n{'=' * 90}")
print(f"  MASTER SUMMARY — Full Pipeline Validation")
print(f"{'=' * 90}")
print(f"\n  {'System':20s} │ {'N':>3} │ {'ARA':>6} �� {'Tele LOO':>8} │ {'Blend':>8} │ {'Stretch':>8} │ {'LOO/Sin':>7} │ {'Corr':>6} │ {'ErrCorr':>7}")
print(f"  {'─'*20}─┼─{'─'*3}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*7}")

for sys_name in all_results:
    r = all_results[sys_name]
    beat = " ★" if r['final_ratio'] < 1.0 else ""
    print(f"  {sys_name:20s} │ {r['N']:>3} │ {r['ara']:>6.3f} │ "
          f"{r['teleport']['loo_mae']:>8.3f} │ {r['blend']['loo_mae']:>8.3f} │ "
          f"{r['stretch']['loo_mae']:>8.3f} │ {r['final_ratio']:>7.3f} │ "
          f"{r['stretch']['corr']:>+6.3f} │ {r['blend']['err_corr']:>+7.3f}{beat}")

print(f"\n  Key:")
print(f"    ★ = beats sine baseline (LOO/Sine < 1.0)")
print(f"    ErrCorr = correlation between path and teleport errors (want ~0)")

# Per-cycle detail for Solar
if "Solar (SSN)" in all_results:
    sr = all_results["Solar (SSN)"]
    print(f"\n{'─' * 90}")
    print(f"  SOLAR PER-CYCLE DETAIL")
    print(f"{'─' * 90}")
    print(f"  {'C':>3} {'Year':>7} {'Act':>6} │ {'Tele':>7} {'TErr':>6} │ {'Path':>7} {'PErr':>6} │ {'Blend':>7} {'BErr':>6} │ {'Final':>7} {'FErr':>6}")
    print(f"  {'─'*3} {'─'*7} {'─'*6}─┼─{'─'*7} {'─'*6}─┼─{'─'*7} {'─'*6}─┼─{'─'*7} {'─'*6}─┼─{'─'*7} {'─'*6}")

    for i in range(len(solar_t)):
        cn = SOLAR_CYCLES[i][0]
        act = solar_a[i]
        tp = sr['teleport']['preds'][i]
        te = abs(tp - act)
        pp = sr['path']['preds'][i]
        pe = abs(pp - act)
        bp = sr['blend']['preds'][i]
        be = abs(bp - act)
        fp = sr['stretch']['preds'][i]
        fe = abs(fp - act)
        flag = " ◀" if fe > 80 else ""
        print(f"  C{cn:>2} {solar_t[i]:>7.1f} {act:>6.1f} │ {tp:>7.1f} {te:>6.1f} │ "
              f"{pp:>7.1f} {pe:>6.1f} │ {bp:>7.1f} {be:>6.1f} │ {fp:>7.1f} {fe:>6.1f}{flag}")


elapsed = clock_time.time() - t_start
print(f"\n  Total runtime: {elapsed:.0f}s")
print("=" * 90)
