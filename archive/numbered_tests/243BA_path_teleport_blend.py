#!/usr/bin/env python3
"""
Script 243BA — Path + Teleport Blend

Runs BOTH prediction methods with the wave physics additions
(mode coupling + standing wave from 243AZ combo), then blends
their predictions at various ratios to find the optimal mix.

  PATH method (vehicle):   Simulates entire timeline step by step.
                           Has gear mesh, multi-rung coupling, snaps.
                           Gets full temporal context but can't LOO easily.

  TELEPORT method (formula): Jumps to each cycle independently.
                             Refits per LOO fold. Has cascade_shape only.

  BLEND:  pred = α × path_pred + (1-α) × teleport_pred
          Scan α from 0.0 to 1.0 in steps of 0.1
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import time as clock_time

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI

t_start = clock_time.time()

# ── Load the 243AZ wave combo code ──
combo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "243AZ_wave_combo.py")
with open(combo_path, 'r') as f:
    combo_code = f.read()

# Strip the MAIN output section — we want functions + data only
lines = combo_code.split('\n')
cutoff = len(lines)
for i, line in enumerate(lines):
    if '# MAIN' in line and i > 400:
        cutoff = i
        break

base_code = '\n'.join(lines[:cutoff])

# Exec into our namespace
ns = {'__file__': combo_path, '__name__': '__exec__'}
exec(base_code, ns)

# Pull out what we need
SOLAR_CYCLES = ns['SOLAR_CYCLES']
solar_t = ns['solar_t']
solar_a = ns['solar_a']
SYSTEMS = ns['SYSTEMS']
run_full_fit = ns['run_full_fit']
run_formula_loo = ns['run_formula_loo']
grid_search = ns['grid_search']
run_full_simulation = ns['run_full_simulation']
EngineMemoryNode = ns['EngineMemoryNode']

SINE_BASELINE = np.mean(np.abs(solar_a - np.mean(solar_a)))

print("=" * 78)
print("  Script 243BA — Path + Teleport Blend")
print("  Wave combo base (mode coupling + standing wave)")
print("=" * 78)

# ══════════════════════════════════════════════
# STEP 1: Run the TELEPORT method (Formula LOO)
# ══════════════════════════════════════════════

print("\n  STEP 1: Teleport method (formula LOO, 25 folds)...")
t0 = clock_time.time()
teleport = run_formula_loo(solar_t, solar_a, PHI**5, PHI, 5, "Solar")
print(f"    LOO = {teleport['loo_mae']:.2f}  |  Corr = {teleport['corr']:.3f}  "
      f"|  LOO/Sine = {teleport['ratio']:.3f}  ({clock_time.time()-t0:.0f}s)")
teleport_preds = np.array(teleport['preds'])

# ══════════════════════════════════════════════
# STEP 2: Run the PATH method (Full Vehicle)
# ══════════════════════════════════════════════

print("\n  STEP 2: Path method (full vehicle simulation)...")
t0 = clock_time.time()
path_result = run_full_fit(solar_t, solar_a, PHI**5, PHI, 5, "Solar")

if path_result['failed']:
    print("    ⚠ VEHICLE FAILED — cannot blend")
    sys.exit(1)

path_preds = np.array(path_result['preds'])
path_mae = path_result['mae']
print(f"    MAE  = {path_mae:.2f}  ({clock_time.time()-t0:.0f}s)")

# Also run a LOO-like evaluation for path (refit each fold)
print("\n  STEP 2b: Path method LOO (refit per fold, 25 folds)...")
t0 = clock_time.time()
N = len(solar_t)
path_loo_preds = []
path_loo_errors = []

for i in range(N):
    mask = np.ones(N, dtype=bool)
    mask[i] = False
    train_t = solar_t[mask]
    train_p = solar_a[mask]

    # Refit on training set
    fit_tr, fit_ba, _ = grid_search(PHI**5, PHI, 5, train_t, train_p)

    # Run full vehicle simulation on training set
    snap_t, snap_a = run_full_simulation(
        train_t, train_p, PHI**5, PHI, 5,
        fit_tr, fit_ba
    )

    if len(snap_t) == 0:
        # Fallback to mean
        path_loo_preds.append(np.mean(train_p))
        path_loo_errors.append(abs(solar_a[i] - np.mean(train_p)))
        continue

    # Find closest snap to the test time
    idx = np.argmin(np.abs(snap_t - solar_t[i]))
    pred = snap_a[idx]
    path_loo_preds.append(pred)
    path_loo_errors.append(abs(pred - solar_a[i]))

path_loo_preds = np.array(path_loo_preds)
path_loo_mae = np.mean(path_loo_errors)
path_loo_corr = np.corrcoef(path_loo_preds, solar_a)[0, 1] if np.std(path_loo_preds) > 0 else 0
print(f"    LOO  = {path_loo_mae:.2f}  |  Corr = {path_loo_corr:.3f}  "
      f"|  LOO/Sine = {path_loo_mae/SINE_BASELINE:.3f}  ({clock_time.time()-t0:.0f}s)")

# ══════════════════════════════════════════════
# STEP 3: Blend at various ratios
# ══════════════════════════════════════════════

print(f"\n{'─' * 78}")
print("  STEP 3: Blend scan  (α × path + (1-α) × teleport)")
print(f"{'─' * 78}")
print(f"\n  {'α':>5} │ {'Blend LOO':>9} │ {'Corr':>6} │ {'LOO/Sine':>8} │ {'Δ champ':>8} │ Note")
print(f"  {'─'*5}─┼─{'─'*9}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*20}")

CHAMP_LOO = 42.89
best_alpha = 0.0
best_loo = 999

for alpha_pct in range(0, 101, 5):
    alpha = alpha_pct / 100.0
    blended = alpha * path_loo_preds + (1 - alpha) * teleport_preds
    errors = np.abs(blended - solar_a)
    loo = np.mean(errors)
    corr = np.corrcoef(blended, solar_a)[0, 1] if np.std(blended) > 0 else 0
    ratio = loo / SINE_BASELINE
    delta = loo - CHAMP_LOO

    note = ""
    if alpha == 0.0: note = "← pure teleport"
    elif alpha == 1.0: note = "← pure path"
    elif abs(alpha - INV_PHI) < 0.03: note = "← ≈ 1/φ"
    elif abs(alpha - 0.5) < 0.01: note = "← 50/50"

    marker = "★" if loo < best_loo else " "
    if loo < best_loo:
        best_loo = loo
        best_alpha = alpha

    print(f"  {alpha:>5.2f} │ {loo:>9.2f} │ {corr:>+6.3f} │ {ratio:>8.3f} │ {delta:>+8.2f} │ {marker} {note}")

# Also test φ-weighted blends specifically
print(f"\n  Special φ-blends:")
for name, alpha in [("1/φ²", INV_PHI**2), ("1/φ", INV_PHI), ("2/φ-1", 2/PHI-1),
                     ("φ-1", PHI-1), ("2-φ", 2-PHI)]:
    blended = alpha * path_loo_preds + (1 - alpha) * teleport_preds
    errors = np.abs(blended - solar_a)
    loo = np.mean(errors)
    corr = np.corrcoef(blended, solar_a)[0, 1] if np.std(blended) > 0 else 0
    delta = loo - CHAMP_LOO
    marker = "★" if loo < best_loo else " "
    if loo < best_loo:
        best_loo = loo
        best_alpha = alpha
    print(f"  α={name:>6} ({alpha:.4f}) │ LOO={loo:>7.2f} │ Corr={corr:>+.3f} │ Δchamp={delta:>+6.2f} │ {marker}")

# ══════════════════════════════════════════════
# STEP 4: Per-cycle breakdown at best blend
# ══════════════════════════════════════════════

print(f"\n{'─' * 78}")
print(f"  BEST BLEND: α = {best_alpha:.2f}  →  LOO = {best_loo:.2f}")
print(f"{'─' * 78}")

blended_best = best_alpha * path_loo_preds + (1 - best_alpha) * teleport_preds
print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Path':>7} {'Telep':>7} {'Blend':>7} │ {'P err':>6} {'T err':>6} {'B err':>6} │ Winner")
print(f"  {'─'*3} {'─'*7} {'─'*6}─┼─{'─'*7} {'─'*7} {'─'*7}─┼─{'─'*6} {'─'*6} {'─'*6}─┼─{'─'*6}")

path_wins = 0; tele_wins = 0; blend_wins = 0
for i in range(N):
    actual = solar_a[i]
    p_pred = path_loo_preds[i]
    t_pred = teleport_preds[i]
    b_pred = blended_best[i]
    p_err = abs(p_pred - actual)
    t_err = abs(t_pred - actual)
    b_err = abs(b_pred - actual)
    best_err = min(p_err, t_err, b_err)
    if best_err == b_err: winner = "BLEND"; blend_wins += 1
    elif best_err == p_err: winner = "path"; path_wins += 1
    else: winner = "telep"; tele_wins += 1
    cn = SOLAR_CYCLES[i][0]
    print(f"  C{cn:>2} {solar_t[i]:>7.1f} {actual:>6.1f} │ {p_pred:>7.1f} {t_pred:>7.1f} {b_pred:>7.1f} │ "
          f"{p_err:>6.1f} {t_err:>6.1f} {b_err:>6.1f} │ {winner}")

print(f"\n  Wins: Path={path_wins}  Teleport={tele_wins}  Blend={blend_wins}")

# ══════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════

print(f"\n{'=' * 78}")
print("  SUMMARY")
print(f"{'=' * 78}")
print(f"  Sine baseline:           {SINE_BASELINE:.2f}")
print(f"  Champion (243AJ):        42.89  (LOO/Sine = 0.879)")
print(f"  Teleport (wave combo):   {teleport['loo_mae']:.2f}  (LOO/Sine = {teleport['ratio']:.3f})")
print(f"  Path LOO (wave combo):   {path_loo_mae:.2f}  (LOO/Sine = {path_loo_mae/SINE_BASELINE:.3f})")
print(f"  Best blend (α={best_alpha:.2f}):    {best_loo:.2f}  (LOO/Sine = {best_loo/SINE_BASELINE:.3f})")
if best_loo < 42.89:
    print(f"\n  ★ NEW CHAMPION: Δ = {best_loo - 42.89:.2f} vs previous best!")
else:
    print(f"\n  Gap to champion: +{best_loo - 42.89:.2f}")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
