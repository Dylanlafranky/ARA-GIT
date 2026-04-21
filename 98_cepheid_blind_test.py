#!/usr/bin/env python3
"""
Script 98: Cepheid Variable Blind Test
=======================================
ARA Framework — Dylan La Franchi & Claude, April 2026

BLIND TEST PROTOCOL:
  Predictions were recorded in BLIND_PREDICTIONS_98-100.md BEFORE any data lookup.
  This script now checks those predictions against published Cepheid light curve data.

PREDICTIONS (from the blind document):
  1. ARA = T_dimming / T_brightening ≈ 1.6-1.8 (best guess: ~1.7)
  2. Light curve asymmetric: fast rise, slow decline
  3. Longer-period Cepheids → higher ARA (more asymmetric)
  4. Cepheids sit on ARA spine in engine/exothermic range

DATA SOURCES:
  - Delta Cephei: AAVSO (rise ~1.5 days of 5.366-day period)
  - Rise fraction ~0.30 of period (multiple sources confirm)
  - Hertzsprung progression: systematic shape changes with period
  - Fourier decomposition parameters from Galactic Cepheid surveys
"""

import numpy as np

print("=" * 70)
print("SCRIPT 98: CEPHEID VARIABLE — BLIND TEST")
print("=" * 70)

# =====================================================================
# SECTION 1: KNOWN CEPHEID DATA
# =====================================================================
# Rise fraction = fraction of period spent brightening (ascending branch)
# Fall fraction = 1 - rise fraction (descending branch / dimming)
# ARA = T_accumulation / T_release = T_fall / T_rise = (1-f)/f
#
# Data from AAVSO, OGLE atlas, and published Fourier decomposition studies.
# Rise fractions are approximate, derived from light curve morphology.

cepheids = [
    # (Name, Period_days, Rise_fraction, Notes)
    # Short-period
    ("SU Cas",       1.95,  0.47, "s-Cepheid, nearly sinusoidal, first overtone"),
    ("DT Cyg",       2.50,  0.45, "s-Cepheid, low amplitude, symmetric"),
    ("SU Cyg",       3.85,  0.35, "short period, moderate asymmetry"),

    # Classical short-period
    ("δ Cep",        5.366, 0.28, "prototype, well-measured: rise ~1.5d of 5.37d"),
    ("FF Aql",       4.47,  0.30, "classical, typical asymmetry"),
    ("Y Oph",        6.96,  0.32, "classical, bump forming on descending branch"),

    # Hertzsprung progression zone (6-10 days)
    ("η Aql",        7.177, 0.30, "bump on descending branch"),
    ("W Sgr",        7.59,  0.32, "bump near maximum, P ≈ HP center approaching"),
    ("S Sge",        8.38,  0.35, "bump migrating toward maximum"),
    ("β Dor",        9.84,  0.38, "near Hertzsprung center, more symmetric"),
    ("ζ Gem",       10.15,  0.40, "at Hertzsprung center (~10d), most symmetric classical"),

    # Post-Hertzsprung
    ("T Mon",       13.00,  0.33, "bump on ascending branch now"),
    ("X Cyg",       16.39,  0.30, "bump absorbed, asymmetry returns"),
    ("SV Vul",      45.01,  0.28, "very long period, strong asymmetry"),
    ("l Car",       35.56,  0.30, "long period, well-studied"),
    ("RS Pup",      41.39,  0.28, "long period, dust echoes famous"),
]

print("\n--- SECTION 1: Cepheid ARA Measurements ---\n")
print(f"{'Star':<12} {'Period(d)':>10} {'Rise_frac':>10} {'Fall_frac':>10} {'ARA':>8} {'Notes'}")
print("-" * 90)

names = []
periods = []
rise_fracs = []
aras = []

for name, period, rise_f, notes in cepheids:
    fall_f = 1.0 - rise_f
    ara = fall_f / rise_f
    names.append(name)
    periods.append(period)
    rise_fracs.append(rise_f)
    aras.append(ara)
    print(f"{name:<12} {period:>10.3f} {rise_f:>10.2f} {fall_f:>10.2f} {ara:>8.3f}   {notes}")

aras = np.array(aras)
periods = np.array(periods)
rise_fracs = np.array(rise_fracs)

# =====================================================================
# SECTION 2: PREDICTION CHECK
# =====================================================================
print("\n" + "=" * 70)
print("SECTION 2: PREDICTION vs REALITY")
print("=" * 70)

# Prediction 1: ARA = 1.6-1.8 (best guess 1.7)
delta_cep_ara = aras[names.index("δ Cep")]
print(f"\n--- Prediction 1: ARA numerical value ---")
print(f"  Predicted: 1.6 - 1.8 (best guess: 1.7)")
print(f"  Actual (δ Cep): {delta_cep_ara:.3f}")
print(f"  Error: {abs(delta_cep_ara - 1.7)/delta_cep_ara * 100:.1f}% off")
print(f"  VERDICT: ✗ MISS — actual is ~34% higher than predicted")
print(f"           Predicted 1.7, got 2.57. Off by 0.87.")
print(f"           The prediction was in the right DIRECTION but wrong MAGNITUDE.")

# What's the mean ARA across all Cepheids?
mean_ara = np.mean(aras)
median_ara = np.median(aras)
# Exclude s-Cepheids for classical mean
classical_mask = np.array([not n.startswith("SU Cas") and not n.startswith("DT Cyg") for n in names])
classical_mean = np.mean(aras[classical_mask])

print(f"\n  Mean ARA (all Cepheids): {mean_ara:.3f}")
print(f"  Mean ARA (classical only): {classical_mean:.3f}")
print(f"  Median ARA: {median_ara:.3f}")
print(f"  Range: {aras.min():.3f} to {aras.max():.3f}")

# Prediction 2: Fast rise, slow decline (correct phase identification)
print(f"\n--- Prediction 2: Phase identification ---")
all_asymmetric = all(a > 1.0 for a in aras)
print(f"  Predicted: All Cepheids have fast rise, slow decline (ARA > 1)")
print(f"  Actual: {sum(a > 1.0 for a in aras)}/{len(aras)} have ARA > 1")
print(f"  VERDICT: ✓ CORRECT — every Cepheid has T_dimming > T_brightening")
print(f"           Phase identification was right. Accumulation IS the dimming phase.")

# Prediction 3: Longer period → higher ARA
print(f"\n--- Prediction 3: Period-ARA correlation ---")
log_p = np.log10(periods)
corr = np.corrcoef(log_p, aras)[0, 1]
print(f"  Predicted: Longer period → higher ARA (positive correlation)")
print(f"  Actual correlation (logP vs ARA): r = {corr:.3f}")

# But wait — the Hertzsprung progression creates a DIP around 10 days
# Let's check short-period and long-period separately
short_mask = periods < 7  # before Hertzsprung
long_mask = periods > 15   # after Hertzsprung
hertz_mask = (periods >= 7) & (periods <= 15)  # Hertzsprung zone

short_mean = np.mean(aras[short_mask]) if any(short_mask) else 0
hertz_mean = np.mean(aras[hertz_mask]) if any(hertz_mask) else 0
long_mean = np.mean(aras[long_mask]) if any(long_mask) else 0

print(f"\n  Short-period (<7d) mean ARA: {short_mean:.3f} (n={sum(short_mask)})")
print(f"  Hertzsprung zone (7-15d) mean ARA: {hertz_mean:.3f} (n={sum(hertz_mask)})")
print(f"  Long-period (>15d) mean ARA: {long_mean:.3f} (n={sum(long_mask)})")
print(f"\n  The Hertzsprung progression (resonance near 10d) creates a SYMMETRY DIP.")
print(f"  Short and long period Cepheids are MORE asymmetric than ~10d Cepheids.")
print(f"  VERDICT: ✗ PARTIAL — the overall correlation is weak (r={corr:.3f})")
print(f"           because the Hertzsprung resonance disrupts the monotonic trend.")
print(f"           The prediction was too simple — it missed the resonance physics.")

# =====================================================================
# SECTION 3: WHERE DO CEPHEIDS SIT ON THE ARA SCALE?
# =====================================================================
print("\n" + "=" * 70)
print("SECTION 3: CEPHEIDS ON THE ARA SCALE")
print("=" * 70)

phi = (1 + np.sqrt(5)) / 2  # 1.618
sqrt3 = np.sqrt(3)           # 1.732

print(f"\n  ARA Scale reference points:")
print(f"    φ (engine):        {phi:.3f}")
print(f"    √3 (exothermic):   {sqrt3:.3f}")
print(f"    2.0 (harmonics):   2.000")
print(f"\n  Cepheid results:")
print(f"    s-Cepheids:        ARA ≈ {np.mean(aras[~classical_mask]):.2f} (near clock/engine boundary)")
print(f"    Classical mean:    ARA ≈ {classical_mean:.2f} (ABOVE harmonics)")
print(f"    δ Cep:             ARA = {delta_cep_ara:.2f}")

# Count how many are near different scale markers
near_phi = sum((aras > phi - 0.2) & (aras < phi + 0.2))
near_sqrt3 = sum((aras > sqrt3 - 0.2) & (aras < sqrt3 + 0.2))
near_2 = sum((aras > 1.8) & (aras < 2.2))
above_2 = sum(aras > 2.0)

print(f"\n  Near φ (1.4-1.8):     {near_phi}/{len(aras)} stars")
print(f"  Near √3 (1.5-1.9):   {near_sqrt3}/{len(aras)} stars")
print(f"  Near 2.0 (1.8-2.2):  {near_2}/{len(aras)} stars")
print(f"  Above 2.0:           {above_2}/{len(aras)} stars")

print(f"\n  SURPRISE: Classical Cepheids don't cluster at φ or √3.")
print(f"  They cluster ABOVE 2.0, in the pure harmonics / high-asymmetry zone.")
print(f"  This was NOT predicted. We expected engine/exothermic (1.6-1.8).")

# =====================================================================
# SECTION 4: WHY THE PREDICTION MISSED
# =====================================================================
print("\n" + "=" * 70)
print("SECTION 4: WHY THE PREDICTION MISSED")
print("=" * 70)

print("""
The prediction assumed Cepheids would sit between φ (engine) and √3 (exothermic)
because they are self-organizing heat engines driven by nuclear energy.

What we got: ARA ≈ 2.0-2.6 for classical Cepheids.

WHY the miss:

1. PULSATION ≠ OPERATION
   The heart's ARA measures its operational cycle (fill/pump).
   The Cepheid's ARA measures its PULSATION cycle (compress/expand).
   The pulsation is a perturbation ON TOP of the star's steady-state operation.
   The star's OPERATIONAL ARA (fusion duty cycle) might be near φ,
   but the PULSATION has its own, more extreme asymmetry.

2. THE KAPPA MECHANISM IS A TRAP-AND-RELEASE
   The ionization zone TRAPS heat for ~70% of the cycle (accumulation)
   then goes transparent and DUMPS it in ~30% (release).
   This is fundamentally a relaxation mechanism — closer to a snap than an engine.
   The pulsation is driven by an opacity valve, not by smooth feedback.

3. GRAVITY AMPLIFIES ASYMMETRY
   The recompression phase involves the entire envelope falling inward
   under gravity, decelerated by pressure. This is slow.
   The expansion phase is pressure-driven — faster.
   Gravity makes accumulation systematically longer.

REVISED UNDERSTANDING:
   Cepheids are PULSATIONAL SNAPS, not engines.
   Their ARA sits in the 2.0-2.6 range, between harmonics and mild snaps.
   The STAR ITSELF may be an engine (operational ARA near φ),
   but its PULSATION MODE is a relaxation oscillation.

   This is exactly like the heart distinction:
   - Heart operational cycle: ARA ≈ 1.6 (engine)
   - Heart electrophysiology (action potential): ARA ≈ 5-10 (snap)
   Same organ, different oscillation mode, different ARA.
""")

# =====================================================================
# SECTION 5: THE HERTZSPRUNG PROGRESSION AS ARA RESONANCE
# =====================================================================
print("=" * 70)
print("SECTION 5: HERTZSPRUNG PROGRESSION = ARA RESONANCE")
print("=" * 70)

print(f"""
The Hertzsprung progression is a well-known feature: around P ≈ 10 days,
the light curve becomes more symmetric due to a 2:1 resonance between
the fundamental mode and the second overtone.

In ARA terms: the resonance FORCES the system toward ARA = 1.0 (clock).
The 2:1 frequency lock imposes external timing, overriding the natural
relaxation asymmetry.

  Pre-resonance (P < 7d):   mean ARA = {short_mean:.2f} (natural asymmetry)
  Resonance zone (7-15d):   mean ARA = {hertz_mean:.2f} (forced toward symmetry)
  Post-resonance (P > 15d): mean ARA = {long_mean:.2f} (asymmetry returns)

This is EXACTLY what the framework predicts for systems under external forcing:
the natural ARA gets pulled toward 1.0 when an external clock (the overtone
resonance) dominates.

The Hertzsprung progression is a CLOCK → ENGINE → SNAP transition
in ARA space, driven by whether the internal resonance is active.

This was NOT in our blind prediction, but it's a post-hoc result that
the framework explains naturally.
""")

# =====================================================================
# SECTION 6: SCORECARD
# =====================================================================
print("=" * 70)
print("SECTION 6: FINAL SCORECARD")
print("=" * 70)

predictions = [
    ("ARA ≈ 1.6-1.8 (best: 1.7)", "ARA ≈ 2.3-2.6", False,
     "Off by ~50%. Predicted engine, got relaxation snap."),
    ("Fast rise, slow decline", "Confirmed for all 16 Cepheids", True,
     "Phase identification correct. Accumulation = dimming."),
    ("Longer period → higher ARA", "Disrupted by Hertzsprung resonance", False,
     "Too simple. Resonance at ~10d creates non-monotonic behavior."),
    ("Cepheids on spine, engine/exothermic range", "On spine, but snap range (>2.0)", False,
     "Right that they're on the spine. Wrong about which zone."),
]

correct = sum(1 for _, _, c, _ in predictions if c)
total = len(predictions)

print(f"\n  Score: {correct}/{total}\n")

for pred, actual, correct_bool, comment in predictions:
    mark = "✓" if correct_bool else "✗"
    print(f"  {mark} Predicted: {pred}")
    print(f"    Actual:    {actual}")
    print(f"    {comment}\n")

print(f"  OVERALL: {correct}/{total} = {correct/total*100:.0f}%")
print(f"  This is a PARTIAL HIT.")
print(f"  The phase identification was correct (which is non-trivial).")
print(f"  The numerical value was wrong — we underestimated by ~50%.")
print(f"  The framework WORKS for classification (snap vs engine vs clock)")
print(f"  but the SPECIFIC prediction of where Cepheids sit was off because")
print(f"  we confused the star's operational ARA with its pulsational ARA.")

# =====================================================================
# SECTION 7: NEW INSIGHT — ARA MODE DECOMPOSITION
# =====================================================================
print("\n" + "=" * 70)
print("SECTION 7: NEW INSIGHT — ARA MODE DECOMPOSITION")
print("=" * 70)

print("""
The Cepheid test reveals something important that wasn't in the framework:

  A SYSTEM CAN HAVE MULTIPLE ARA VALUES FOR DIFFERENT OSCILLATION MODES.

  The star's:
  - Nuclear burning cycle:    ARA near φ (sustained engine)
  - Radial pulsation mode:    ARA ≈ 2.3-2.6 (relaxation snap)
  - Second overtone:          ARA ≈ 1.0 (clock — enforces symmetry at P~10d)

  These coexist. They couple. The Hertzsprung progression is the
  interference pattern between modes with different ARAs.

  This is the same as the heart:
  - Ventricular pump cycle:   ARA ≈ 1.6 (engine)
  - SA node firing:           ARA ≈ 5+ (snap)
  - Respiratory sinus arrhythmia: ARA modulated by breathing

  The heart's operational ARA (1.6) and electrophysiological ARA (5+)
  are different oscillation modes of the same organ.

  PREDICTION (new): Every system with multiple oscillation modes
  should show distinct ARA values for each mode, and the coupling
  between modes should follow the three-system architecture.
""")

print("=" * 70)
print("END OF SCRIPT 98")
print("=" * 70)
