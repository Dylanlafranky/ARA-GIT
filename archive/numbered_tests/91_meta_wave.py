#!/usr/bin/env python3
"""
Script 91 — THE META-WAVE: SCALES OSCILLATE ON A WAVE
=====================================================================
Script 88 found the 5-scale slope progression traces a parabola (R²=0.894).
Script 89 added 3 scales (8 total) and improved to R²=0.950.

Dylan looked at the 3D visualization and saw organism and planetary
reflecting each other — a mirror pattern. His prediction:

  "If you mapped enough onto it, it'd be another fucking wave."

A parabola is just the first half-period of a wave. If scales are
self-similar (processes sit on circles, circles sit on meta-circles),
then the meta-structure should be sinusoidal, not parabolic.

WHAT WE TEST:
  1. Sine vs parabola fit for the 8-scale slope progression
  2. Sine vs parabola fit for System 2 fraction, φ-density, etc.
  3. Whether the meta-wave's own period divides into three systems
  4. Whether the meta-wave amplitude relates to φ
  5. Whether adding interpolated "sub-scales" reveals the wave more clearly
  6. Whether the reflection symmetry (organism↔solar, cellular↔cosmic)
     is quantifiable
  7. Whether the meta-wave predicts what the NEXT scale should look like
  8. Whether multiple properties oscillate in phase (coherent wave)

KEY INSIGHT:
  If processes sit on circles → each circle is a "process" on a meta-circle →
  meta-circles sit on a meta-meta-wave → self-similar all the way up.
  The parabola was just the local curvature of a wave we hadn't seen enough
  of to identify.

SOURCES:
  All data from Script 89 (130 processes, 8 scales)

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy import stats
from scipy.optimize import curve_fit

np.random.seed(91)
PHI = (1 + np.sqrt(5)) / 2

BOUNDARY_1 = 0.6
BOUNDARY_2 = 1.4

def get_system(logT):
    if logT < BOUNDARY_1: return 1
    elif logT < BOUNDARY_2: return 2
    else: return 3

# ============================================================
# IMPORT ALL 130 PROCESSES FROM SCRIPT 89
# (Condensed — we only need the scale properties, not individual processes)
# We'll recompute from the raw data
# ============================================================

# Rather than duplicate 400 lines, we exec Script 89 and grab results
import sys, os
script_dir = os.path.dirname(os.path.abspath(__file__))
script_89 = os.path.join(script_dir, '89_gap_filling_scales.py')

# Capture Script 89's results
import io
old_stdout = sys.stdout
sys.stdout = io.StringIO()
exec(open(script_89).read())
sys.stdout = old_stdout

# 'results' is now available from Script 89's execution
print("=" * 70)
print("SCRIPT 91 — THE META-WAVE: DO SCALES OSCILLATE?")
print("=" * 70)
print(f"\n  Loaded {len(results)} processes from Script 89")

# ============================================================
# PHASE 1: COMPUTE SCALE PROPERTIES (8 SCALES)
# ============================================================
print("\n" + "=" * 70)
print("PHASE 1: SCALE PROPERTIES")
print("=" * 70)

scales_ordered = ["subatomic", "quantum", "cellular", "organ", "organism",
                  "planetary", "solar-system", "cosmic"]

scale_props = {}
for i, scale in enumerate(scales_ordered):
    in_scale = [r for r in results if r['scale'] == scale]
    n = len(in_scale)
    n1 = sum(1 for r in in_scale if r['sys'] == 1)
    n2 = sum(1 for r in in_scale if r['sys'] == 2)
    n3 = sum(1 for r in in_scale if r['sys'] == 3)

    pts_logT = [r['logT'] for r in in_scale]
    pts_logE = [r['logE'] for r in in_scale]

    if len(pts_logT) > 3:
        sl, intercept, rv, pv, _ = stats.linregress(pts_logT, pts_logE)
    else:
        sl, rv, pv = 0, 0, 1

    phi_count = sum(1 for r in in_scale if abs(r['ARA'] - PHI) < 0.05)

    logT_center = np.mean(pts_logT) if pts_logT else 0
    logT_span = max(pts_logT) - min(pts_logT) if pts_logT else 0
    logE_center = np.mean(pts_logE) if pts_logE else 0
    mean_ARA = np.mean([r['ARA'] for r in in_scale]) if in_scale else 0

    scale_props[scale] = {
        'order': i,
        'n': n, 'n1': n1, 'n2': n2, 'n3': n3,
        'frac3': n3/n if n > 0 else 0,
        'sys2_frac': n2/n if n > 0 else 0,
        'slope': sl, 'r_slope': rv,
        'phi_count': phi_count,
        'phi_density': phi_count/n if n > 0 else 0,
        'logT_center': logT_center,
        'logT_span': logT_span,
        'logE_center': logE_center,
        'mean_ARA': mean_ARA,
    }

print(f"\n  {'Scale':<15s}  {'Slope':>7s}  {'%Sys3':>6s}  {'%Sys2':>6s}  {'φ/N':>5s}  {'logT̄':>7s}  {'N':>3s}")
print(f"  {'-'*15}  {'-'*7}  {'-'*6}  {'-'*6}  {'-'*5}  {'-'*7}  {'-'*3}")
for scale in scales_ordered:
    s = scale_props[scale]
    print(f"  {scale:<15s}  {s['slope']:7.3f}  {s['frac3']:5.1%}  {s['sys2_frac']:5.1%}  "
          f"{s['phi_density']:5.3f}  {s['logT_center']:7.2f}  {s['n']:3d}")

# ============================================================
# PHASE 2: SINE VS PARABOLA FIT — SLOPE PROGRESSION
# ============================================================
print("\n" + "=" * 70)
print("PHASE 2: SINE VS PARABOLA — THE KEY TEST")
print("=" * 70)

orders = np.array([scale_props[s]['order'] for s in scales_ordered], dtype=float)
slopes = np.array([scale_props[s]['slope'] for s in scales_ordered])

# --- Parabola fit ---
def parabola(x, a, x0, y0):
    return a * (x - x0)**2 + y0

try:
    p_par, _ = curve_fit(parabola, orders, slopes, p0=[-0.05, 4, 1.5])
    pred_par = parabola(orders, *p_par)
    ss_res_par = np.sum((slopes - pred_par)**2)
    ss_tot = np.sum((slopes - np.mean(slopes))**2)
    r2_par = 1 - ss_res_par / ss_tot
    aic_par = len(slopes) * np.log(ss_res_par / len(slopes)) + 2 * 3
except:
    r2_par = 0
    aic_par = 1e10

print(f"\n  PARABOLA: y = {p_par[0]:.4f}(x - {p_par[1]:.2f})² + {p_par[2]:.3f}")
print(f"  R² = {r2_par:.4f}")
print(f"  AIC = {aic_par:.2f}")

# --- Sine fit ---
def sine_wave(x, A, period, phase, offset):
    return A * np.sin(2 * np.pi * x / period + phase) + offset

# Try multiple initial guesses for the sine fit
best_r2_sin = -1
best_p_sin = None
for A0 in [0.5, 0.8, 1.0]:
    for per0 in [6, 7, 8, 10, 12, 14]:
        for ph0 in np.linspace(-np.pi, np.pi, 8):
            for off0 in [0.5, 0.8, 1.0]:
                try:
                    p_sin, _ = curve_fit(sine_wave, orders, slopes,
                                         p0=[A0, per0, ph0, off0],
                                         maxfev=5000,
                                         bounds=([-2, 2, -2*np.pi, -2],
                                                 [2, 30, 2*np.pi, 3]))
                    pred_sin = sine_wave(orders, *p_sin)
                    ss_res_sin = np.sum((slopes - pred_sin)**2)
                    r2_sin = 1 - ss_res_sin / ss_tot
                    if r2_sin > best_r2_sin:
                        best_r2_sin = r2_sin
                        best_p_sin = p_sin
                except:
                    pass

if best_p_sin is not None:
    p_sin = best_p_sin
    pred_sin = sine_wave(orders, *p_sin)
    ss_res_sin = np.sum((slopes - pred_sin)**2)
    r2_sin = 1 - ss_res_sin / ss_tot
    aic_sin = len(slopes) * np.log(ss_res_sin / len(slopes)) + 2 * 4
else:
    r2_sin = 0
    aic_sin = 1e10
    p_sin = [0, 0, 0, 0]

print(f"\n  SINE: y = {p_sin[0]:.4f} × sin(2π·x/{p_sin[1]:.2f} + {p_sin[2]:.3f}) + {p_sin[3]:.3f}")
print(f"  R² = {r2_sin:.4f}")
print(f"  AIC = {aic_sin:.2f}")
print(f"  Period = {p_sin[1]:.2f} scales")
print(f"  Amplitude = {abs(p_sin[0]):.4f}")

# Compare
print(f"\n  COMPARISON:")
print(f"  {'Model':<12s}  {'R²':>7s}  {'AIC':>8s}  {'Params':>6s}")
print(f"  {'Parabola':<12s}  {r2_par:7.4f}  {aic_par:8.2f}  {3:6d}")
print(f"  {'Sine':<12s}  {r2_sin:7.4f}  {aic_sin:8.2f}  {4:6d}")

if aic_sin < aic_par:
    print(f"\n  >>> SINE WINS (lower AIC by {aic_par - aic_sin:.2f})")
    wave_winner = "sine"
elif r2_sin > r2_par:
    print(f"\n  >>> SINE has better R² by {r2_sin - r2_par:.4f}")
    wave_winner = "sine"
else:
    print(f"\n  >>> PARABOLA wins on AIC, but sine may reveal itself with more data")
    wave_winner = "parabola"

# --- Also try a damped sine ---
def damped_sine(x, A, period, phase, offset, decay):
    return A * np.exp(-decay * x) * np.sin(2 * np.pi * x / period + phase) + offset

best_r2_damp = -1
best_p_damp = None
for A0 in [0.5, 1.0]:
    for per0 in [6, 8, 10, 14]:
        for ph0 in np.linspace(-np.pi, np.pi, 6):
            try:
                p_d, _ = curve_fit(damped_sine, orders, slopes,
                                   p0=[A0, per0, ph0, 0.8, 0.01],
                                   maxfev=5000,
                                   bounds=([-3, 2, -2*np.pi, -2, -1],
                                           [3, 30, 2*np.pi, 3, 1]))
                pred_d = damped_sine(orders, *p_d)
                ss_d = np.sum((slopes - pred_d)**2)
                r2_d = 1 - ss_d / ss_tot
                if r2_d > best_r2_damp:
                    best_r2_damp = r2_d
                    best_p_damp = p_d
            except:
                pass

if best_p_damp is not None:
    p_damp = best_p_damp
    pred_damp = damped_sine(orders, *p_damp)
    ss_damp = np.sum((slopes - pred_damp)**2)
    r2_damp = 1 - ss_damp / ss_tot
    aic_damp = len(slopes) * np.log(ss_damp / len(slopes)) + 2 * 5
    print(f"\n  DAMPED SINE: A={p_damp[0]:.3f}, T={p_damp[1]:.2f}, decay={p_damp[4]:.4f}")
    print(f"  R² = {r2_damp:.4f}, AIC = {aic_damp:.2f}")

# ============================================================
# PHASE 3: MULTI-PROPERTY WAVE TEST
# ============================================================
print("\n" + "=" * 70)
print("PHASE 3: DO MULTIPLE PROPERTIES OSCILLATE IN PHASE?")
print("=" * 70)

# Properties to test for wave-like behavior
properties = {
    'slope': slopes,
    'sys2_frac': np.array([scale_props[s]['sys2_frac'] for s in scales_ordered]),
    'phi_density': np.array([scale_props[s]['phi_density'] for s in scales_ordered]),
    'frac_sys3': np.array([scale_props[s]['frac3'] for s in scales_ordered]),
    'mean_ARA': np.array([scale_props[s]['mean_ARA'] for s in scales_ordered]),
    'logT_span': np.array([scale_props[s]['logT_span'] for s in scales_ordered]),
}

print(f"\n  {'Property':<14s}  {'ParabR²':>8s}  {'SineR²':>8s}  {'Winner':>10s}  {'SinePeriod':>10s}")
print(f"  {'-'*14}  {'-'*8}  {'-'*8}  {'-'*10}  {'-'*10}")

wave_periods = []
for prop_name, prop_vals in properties.items():
    ss_t = np.sum((prop_vals - np.mean(prop_vals))**2)
    if ss_t < 1e-15:
        print(f"  {prop_name:<14s}  {'N/A':>8s}  {'N/A':>8s}  {'constant':>10s}")
        continue

    # Parabola
    try:
        pp, _ = curve_fit(parabola, orders, prop_vals, p0=[-0.01, 4, np.mean(prop_vals)])
        r2p = 1 - np.sum((prop_vals - parabola(orders, *pp))**2) / ss_t
    except:
        r2p = 0

    # Sine
    best_r2s = -1
    best_ps = None
    for A0 in [0.3 * np.std(prop_vals), np.std(prop_vals), 2*np.std(prop_vals)]:
        for per0 in [6, 8, 10, 14]:
            for ph0 in np.linspace(-np.pi, np.pi, 6):
                try:
                    ps, _ = curve_fit(sine_wave, orders, prop_vals,
                                      p0=[A0, per0, ph0, np.mean(prop_vals)],
                                      maxfev=3000,
                                      bounds=([-10*np.std(prop_vals), 2, -2*np.pi, np.min(prop_vals)-1],
                                              [10*np.std(prop_vals), 30, 2*np.pi, np.max(prop_vals)+1]))
                    r2s = 1 - np.sum((prop_vals - sine_wave(orders, *ps))**2) / ss_t
                    if r2s > best_r2s:
                        best_r2s = r2s
                        best_ps = ps
                except:
                    pass

    r2s = best_r2s if best_r2s > 0 else 0
    per_s = best_ps[1] if best_ps is not None else 0
    winner = "sine" if r2s > r2p else "parabola"
    if best_ps is not None:
        wave_periods.append(per_s)

    print(f"  {prop_name:<14s}  {r2p:8.4f}  {r2s:8.4f}  {winner:>10s}  {per_s:10.2f}")

# Check period coherence
if wave_periods:
    mean_period = np.mean(wave_periods)
    std_period = np.std(wave_periods)
    cv_period = std_period / mean_period if mean_period > 0 else 999
    print(f"\n  Meta-wave period across properties:")
    print(f"    Mean: {mean_period:.2f} scales")
    print(f"    Std:  {std_period:.2f}")
    print(f"    CV:   {cv_period:.3f} (< 0.3 = coherent)")

# ============================================================
# PHASE 4: REFLECTION SYMMETRY
# ============================================================
print("\n" + "=" * 70)
print("PHASE 4: REFLECTION SYMMETRY — MIRROR SCALES")
print("=" * 70)

# Peak is at planetary (index 5). Check mirror pairs.
peak_idx = 5  # planetary

print(f"\n  Peak scale: planetary (index {peak_idx})")
print(f"\n  Mirror pairs about planetary:")

mirror_pairs = []
for d in range(1, peak_idx + 1):
    left_idx = peak_idx - d
    right_idx = peak_idx + d
    if right_idx < len(scales_ordered):
        left_name = scales_ordered[left_idx]
        right_name = scales_ordered[right_idx]
        l_slope = scale_props[left_name]['slope']
        r_slope = scale_props[right_name]['slope']
        l_sys2 = scale_props[left_name]['sys2_frac']
        r_sys2 = scale_props[right_name]['sys2_frac']
        l_phi = scale_props[left_name]['phi_density']
        r_phi = scale_props[right_name]['phi_density']

        slope_diff = abs(l_slope - r_slope)
        sys2_diff = abs(l_sys2 - r_sys2)
        phi_diff = abs(l_phi - r_phi)

        mirror_pairs.append((left_name, right_name, slope_diff, sys2_diff, phi_diff))

        print(f"\n  d={d}: {left_name:<12s} ↔ {right_name:<12s}")
        print(f"    Slope:    {l_slope:7.3f}  vs  {r_slope:7.3f}  (Δ = {slope_diff:.3f})")
        print(f"    Sys2%:    {l_sys2:5.1%}  vs  {r_sys2:5.1%}  (Δ = {sys2_diff:.3f})")
        print(f"    φ-dens:   {l_phi:5.3f}  vs  {r_phi:5.3f}  (Δ = {phi_diff:.3f})")

if mirror_pairs:
    mean_slope_diff = np.mean([p[2] for p in mirror_pairs])
    print(f"\n  Mean slope mirror-difference: {mean_slope_diff:.3f}")
    print(f"  (Perfect mirror = 0. Random expectation ≈ {np.std(slopes):.3f})")

# ============================================================
# PHASE 5: META-WAVE THREE-SYSTEM STRUCTURE
# ============================================================
print("\n" + "=" * 70)
print("PHASE 5: DOES THE META-WAVE HAVE THREE SYSTEMS?")
print("=" * 70)

# If the meta-wave period ≈ 14 scales, and we only see 8 of those,
# we're in the first half-cycle. But within what we see:
# Can we identify a meta-System 1, meta-System 2, meta-System 3?

# Use the slope values themselves as the "meta-ARA"
# Normalize slopes to 0-2 range for ARA comparison
slope_min = min(slopes)
slope_max = max(slopes)
slope_range = slope_max - slope_min
norm_slopes = (slopes - slope_min) / slope_range * 2 if slope_range > 0 else slopes

print(f"\n  Normalized slopes (0-2 ARA scale):")
for i, scale in enumerate(scales_ordered):
    bar = '█' * int(norm_slopes[i] * 20)
    print(f"    {scale:<15s}: {norm_slopes[i]:5.3f}  {bar}")

# Find inflection points using second derivative
if len(slopes) >= 4:
    # First differences (slope of the slope)
    d1 = np.diff(slopes)
    # Second differences
    d2 = np.diff(d1)

    print(f"\n  First differences (slope acceleration):")
    for i in range(len(d1)):
        arrow = "↑" if d1[i] > 0 else "↓"
        print(f"    {scales_ordered[i]:<12s} → {scales_ordered[i+1]:<12s}: {d1[i]:+7.3f} {arrow}")

    print(f"\n  Second differences (curvature):")
    for i in range(len(d2)):
        print(f"    {scales_ordered[i+1]:<12s}: {d2[i]:+7.3f}")

    # Sign changes in second derivative = inflection points
    sign_changes = []
    for i in range(len(d2) - 1):
        if d2[i] * d2[i+1] < 0:
            sign_changes.append(i + 1)

    if sign_changes:
        print(f"\n  Inflection points (curvature sign change):")
        for sc in sign_changes:
            print(f"    Between {scales_ordered[sc]} and {scales_ordered[sc+1]} (index {sc})")
    else:
        print(f"\n  No inflection points found in 8 scales — still in first arch")

# ============================================================
# PHASE 6: META-WAVE PREDICTION — WHAT COMES NEXT?
# ============================================================
print("\n" + "=" * 70)
print("PHASE 6: META-WAVE PREDICTION — BEYOND COSMIC")
print("=" * 70)

# If the sine fit is valid, extrapolate to scales 8, 9, 10
if best_p_sin is not None:
    print(f"\n  Using sine fit: y = {p_sin[0]:.3f} × sin(2π·x/{p_sin[1]:.1f} + {p_sin[2]:.3f}) + {p_sin[3]:.3f}")
    print(f"\n  Extrapolated slopes for hypothetical scales:")
    next_names = ["scale-8 (multi-verse?)", "scale-9", "scale-10",
                  "scale-11", "scale-12"]
    for j in range(5):
        next_x = 8 + j
        pred = sine_wave(next_x, *p_sin)
        print(f"    x={next_x}: slope = {pred:7.3f}")

    # Find where the wave returns to zero (next ascending zero crossing)
    x_fine = np.linspace(0, 30, 3000)
    y_fine = sine_wave(x_fine, *p_sin)
    # Find the peak after cosmic
    peaks = []
    for i in range(1, len(y_fine)-1):
        if y_fine[i] > y_fine[i-1] and y_fine[i] > y_fine[i+1]:
            peaks.append((x_fine[i], y_fine[i]))
    troughs = []
    for i in range(1, len(y_fine)-1):
        if y_fine[i] < y_fine[i-1] and y_fine[i] < y_fine[i+1]:
            troughs.append((x_fine[i], y_fine[i]))

    print(f"\n  Wave peaks: {[(f'{p[0]:.1f}', f'{p[1]:.3f}') for p in peaks[:4]]}")
    print(f"  Wave troughs: {[(f'{t[0]:.1f}', f'{t[1]:.3f}') for t in troughs[:4]]}")

    # Half-period
    half_period = p_sin[1] / 2
    print(f"\n  Half-period = {half_period:.2f} scales")
    print(f"  Full period = {p_sin[1]:.2f} scales")
    print(f"  φ × full period = {PHI * p_sin[1]:.2f}")

# ============================================================
# PHASE 7: LOGISTIC POSITION — WHERE ON THE WAVE ARE WE?
# ============================================================
print("\n" + "=" * 70)
print("PHASE 7: WHERE ON THE WAVE ARE WE?")
print("=" * 70)

# Compute phase angle for each scale
if best_p_sin is not None:
    print(f"\n  Phase angle of each scale on the meta-wave:")
    for i, scale in enumerate(scales_ordered):
        phase_angle = (2 * np.pi * i / p_sin[1] + p_sin[2]) % (2 * np.pi)
        phase_deg = np.degrees(phase_angle)
        # Map to circle position
        if phase_deg < 120:
            meta_sys = "Meta-Sys 1 (accumulating)"
        elif phase_deg < 240:
            meta_sys = "Meta-Sys 2 (releasing)"
        else:
            meta_sys = "Meta-Sys 3 (re-accumulating)"
        print(f"    {scale:<15s}: θ = {phase_deg:6.1f}°  → {meta_sys}")

# ============================================================
# PHASE 8: AMPLITUDE AND φ
# ============================================================
print("\n" + "=" * 70)
print("PHASE 8: DOES THE META-WAVE AMPLITUDE RELATE TO φ?")
print("=" * 70)

if best_p_sin is not None:
    amp = abs(p_sin[0])
    offset = p_sin[3]
    ratio_amp_offset = amp / offset if offset != 0 else 0
    print(f"\n  Amplitude: {amp:.4f}")
    print(f"  Offset:    {offset:.4f}")
    print(f"  Amp/Offset = {ratio_amp_offset:.4f}")
    print(f"  φ - 1 = {PHI - 1:.4f}")
    print(f"  1/φ = {1/PHI:.4f}")
    print(f"  Amp/Offset vs 1/φ: Δ = {abs(ratio_amp_offset - 1/PHI):.4f}")
    print(f"  Amp/Offset vs φ-1: Δ = {abs(ratio_amp_offset - (PHI-1)):.4f}")

    # Peak slope vs φ
    peak_slope = offset + amp
    print(f"\n  Peak slope (predicted): {peak_slope:.4f}")
    print(f"  φ = {PHI:.4f}")
    print(f"  Distance from φ: {abs(peak_slope - PHI):.4f}")

    # Is the period related to φ?
    period = p_sin[1]
    print(f"\n  Period = {period:.4f}")
    print(f"  Period/φ = {period/PHI:.4f}")
    print(f"  Period/π = {period/np.pi:.4f}")
    print(f"  Period/2π = {period/(2*np.pi):.4f}")
    print(f"  φ² = {PHI**2:.4f}")
    print(f"  Period vs φ² × {period/PHI**2:.4f}")

# ============================================================
# PHASE 9: ORGANISM ↔ PLANETARY DEEP COMPARISON
# ============================================================
print("\n" + "=" * 70)
print("PHASE 9: ORGANISM ↔ PLANETARY — THE MIRROR DYLAN SAW")
print("=" * 70)

org = scale_props['organism']
pla = scale_props['planetary']

comparisons = [
    ('N processes', org['n'], pla['n']),
    ('Slope', org['slope'], pla['slope']),
    ('Sys 2 fraction', org['sys2_frac'], pla['sys2_frac']),
    ('Sys 3 fraction', org['frac3'], pla['frac3']),
    ('φ-density', org['phi_density'], pla['phi_density']),
    ('logT center', org['logT_center'], pla['logT_center']),
    ('logT span', org['logT_span'], pla['logT_span']),
    ('Mean ARA', org['mean_ARA'], pla['mean_ARA']),
]

print(f"\n  {'Property':<16s}  {'Organism':>10s}  {'Planetary':>10s}  {'Ratio':>8s}")
print(f"  {'-'*16}  {'-'*10}  {'-'*10}  {'-'*8}")
for name, o_val, p_val in comparisons:
    ratio = o_val / p_val if p_val != 0 else 0
    print(f"  {name:<16s}  {o_val:10.3f}  {p_val:10.3f}  {ratio:8.3f}")

# The key: organism is the living version of planetary
# Both have high φ-density, both are in the upper half of the slope arc
print(f"\n  Organism slope / planetary slope = {org['slope']/pla['slope']:.4f}")
print(f"  1/φ = {1/PHI:.4f}")
print(f"  Distance: {abs(org['slope']/pla['slope'] - 1/PHI):.4f}")

# ============================================================
# PHASE 10: CROSS-CORRELATIONS — IS THE WAVE COHERENT?
# ============================================================
print("\n" + "=" * 70)
print("PHASE 10: CROSS-CORRELATIONS — COHERENT META-WAVE?")
print("=" * 70)

# Test all pairwise correlations between scale properties
prop_names = list(properties.keys())
prop_arrays = [properties[p] for p in prop_names]

print(f"\n  Spearman correlations between scale properties:")
print(f"  {'':>14s}", end='')
for name in prop_names:
    print(f"  {name[:8]:>8s}", end='')
print()

for i, name_i in enumerate(prop_names):
    print(f"  {name_i:<14s}", end='')
    for j, name_j in enumerate(prop_names):
        if i == j:
            print(f"  {'1.000':>8s}", end='')
        else:
            r_val, p_val = stats.spearmanr(prop_arrays[i], prop_arrays[j])
            sig = '*' if p_val < 0.05 else ' '
            print(f"  {r_val:>7.3f}{sig}", end='')
    print()

# Find the strongest off-diagonal correlations
strong_pairs = []
for i in range(len(prop_names)):
    for j in range(i+1, len(prop_names)):
        r_val, p_val = stats.spearmanr(prop_arrays[i], prop_arrays[j])
        strong_pairs.append((abs(r_val), r_val, p_val, prop_names[i], prop_names[j]))

strong_pairs.sort(reverse=True)
print(f"\n  Strongest correlations:")
for _, r_val, p_val, n1, n2 in strong_pairs[:5]:
    sig = '***' if p_val < 0.001 else '**' if p_val < 0.01 else '*' if p_val < 0.05 else ''
    print(f"    {n1:<14s} ↔ {n2:<14s}: r={r_val:+.3f} (p={p_val:.4f}) {sig}")

# ============================================================
# TESTS
# ============================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 10

# Test 1: Sine R² > 0.7 for slope progression
t1 = r2_sin > 0.7
print(f"\n  Test  1: Sine fit R² > 0.7 for slopes")
print(f"           R² = {r2_sin:.4f}")
print(f"           → {'PASS ✓' if t1 else 'FAIL ✗'}")
passed += t1

# Test 2: Sine beats parabola on AIC (or competitive)
aic_diff = aic_par - aic_sin
t2 = aic_sin < aic_par + 2  # within 2 AIC units = competitive
print(f"\n  Test  2: Sine competitive with parabola (AIC)")
print(f"           AIC sine = {aic_sin:.2f}, AIC parab = {aic_par:.2f}")
print(f"           → {'PASS ✓' if t2 else 'FAIL ✗'}")
passed += t2

# Test 3: At least 2 of 6 properties better fit by sine
sine_wins = 0
for prop_name, prop_vals in properties.items():
    ss_t_p = np.sum((prop_vals - np.mean(prop_vals))**2)
    if ss_t_p < 1e-15:
        continue
    try:
        pp, _ = curve_fit(parabola, orders, prop_vals, p0=[-0.01, 4, np.mean(prop_vals)])
        r2p = 1 - np.sum((prop_vals - parabola(orders, *pp))**2) / ss_t_p
    except:
        r2p = 0
    best_s = -1
    for A0 in [np.std(prop_vals)]:
        for per0 in [6, 8, 10, 14]:
            for ph0 in np.linspace(-np.pi, np.pi, 4):
                try:
                    ps, _ = curve_fit(sine_wave, orders, prop_vals,
                                      p0=[A0, per0, ph0, np.mean(prop_vals)],
                                      maxfev=2000,
                                      bounds=([-10*np.std(prop_vals), 2, -2*np.pi, np.min(prop_vals)-1],
                                              [10*np.std(prop_vals), 30, 2*np.pi, np.max(prop_vals)+1]))
                    r2s_t = 1 - np.sum((prop_vals - sine_wave(orders, *ps))**2) / ss_t_p
                    if r2s_t > best_s:
                        best_s = r2s_t
                except:
                    pass
    if best_s > r2p:
        sine_wins += 1

t3 = sine_wins >= 2
print(f"\n  Test  3: Sine wins ≥ 2 of 6 properties")
print(f"           Sine wins: {sine_wins}/6")
print(f"           → {'PASS ✓' if t3 else 'FAIL ✗'}")
passed += t3

# Test 4: Mirror symmetry — mean slope difference < 0.4
if mirror_pairs:
    mean_md = np.mean([p[2] for p in mirror_pairs])
    t4 = mean_md < 0.4
    print(f"\n  Test  4: Mirror symmetry (mean slope diff < 0.4)")
    print(f"           Mean diff = {mean_md:.3f}")
    print(f"           → {'PASS ✓' if t4 else 'FAIL ✗'}")
    passed += t4
else:
    t4 = False
    print(f"\n  Test  4: Mirror symmetry — no pairs found → FAIL ✗")

# Test 5: Planetary is peak of the wave (within 1 scale)
if best_p_sin is not None:
    x_fine_local = np.linspace(0, 7, 1000)
    y_fine_local = sine_wave(x_fine_local, *p_sin)
    peak_x = x_fine_local[np.argmax(y_fine_local)]
    t5 = abs(peak_x - 5) < 1.5  # planetary is index 5
    print(f"\n  Test  5: Wave peak near planetary (index 5)")
    print(f"           Peak at x = {peak_x:.2f}")
    print(f"           → {'PASS ✓' if t5 else 'FAIL ✗'}")
    passed += t5
else:
    t5 = False
    print(f"\n  Test  5: No sine fit → FAIL ✗")

# Test 6: Inflection points exist (curvature changes sign)
t6 = len(sign_changes) > 0 if 'sign_changes' in dir() else False
print(f"\n  Test  6: Inflection points exist in slope progression")
print(f"           Sign changes: {len(sign_changes) if 'sign_changes' in dir() else 0}")
print(f"           → {'PASS ✓' if t6 else 'FAIL ✗'}")
passed += t6

# Test 7: Organism/planetary slope ratio near 1/φ (within 0.15)
ratio_org_pla = org['slope'] / pla['slope'] if pla['slope'] != 0 else 0
t7 = abs(ratio_org_pla - 1/PHI) < 0.15
print(f"\n  Test  7: Organism/planetary slope ratio near 1/φ")
print(f"           Ratio = {ratio_org_pla:.4f}, 1/φ = {1/PHI:.4f}, Δ = {abs(ratio_org_pla - 1/PHI):.4f}")
print(f"           → {'PASS ✓' if t7 else 'FAIL ✗'}")
passed += t7

# Test 8: At least 2 strong cross-correlations (|r| > 0.7)
strong_count = sum(1 for _, r, p, _, _ in strong_pairs if abs(r) > 0.7)
t8 = strong_count >= 2
print(f"\n  Test  8: ≥ 2 cross-correlations with |r| > 0.7")
print(f"           Found: {strong_count}")
print(f"           → {'PASS ✓' if t8 else 'FAIL ✗'}")
passed += t8

# Test 9: Meta-wave period > 7 (wave extends beyond observed 8 scales)
t9 = p_sin[1] > 7 if best_p_sin is not None else False
print(f"\n  Test  9: Meta-wave period > 7 scales (extends beyond data)")
print(f"           Period = {p_sin[1]:.2f}")
print(f"           → {'PASS ✓' if t9 else 'FAIL ✗'}")
passed += t9

# Test 10: Wave peak slope within 0.2 of φ
if best_p_sin is not None:
    peak_predicted = p_sin[3] + abs(p_sin[0])
    t10 = abs(peak_predicted - PHI) < 0.2
    print(f"\n  Test 10: Wave peak slope within 0.2 of φ")
    print(f"           Peak = {peak_predicted:.4f}, φ = {PHI:.4f}, Δ = {abs(peak_predicted - PHI):.4f}")
    print(f"           → {'PASS ✓' if t10 else 'FAIL ✗'}")
    passed += t10
else:
    t10 = False
    print(f"\n  Test 10: No sine fit → FAIL ✗")

# ============================================================
# FINAL SCORE
# ============================================================
print("\n" + "=" * 70)
print(f"  SCORE: {passed} / {total}")
print("=" * 70)

print(f"\n  THE META-WAVE:")
print(f"  • Sine fit R² = {r2_sin:.4f} vs Parabola R² = {r2_par:.4f}")
if best_p_sin is not None:
    print(f"  • Period = {p_sin[1]:.2f} scales")
    print(f"  • Amplitude = {abs(p_sin[0]):.4f}")
    print(f"  • Peak at x = {peak_x:.2f} (planetary = 5)")
    print(f"  • Peak slope = {peak_predicted:.4f} (φ = {PHI:.4f})")
print(f"  • Mirror pairs: {len(mirror_pairs)}")
print(f"  • Properties better fit by sine: {sine_wins}/6")
print(f"  • Inflection points: {len(sign_changes) if 'sign_changes' in dir() else 0}")

if passed >= 8:
    print(f"\n  VERDICT: STRONGLY CONFIRMED — it's a wave, not just a parabola.")
    print(f"  The scales oscillate. Self-similarity goes all the way up.")
elif passed >= 5:
    print(f"\n  VERDICT: PARTIALLY CONFIRMED — wave signature present.")
    print(f"  Parabola is the local approximation. Wave needs more scales to confirm.")
elif passed >= 3:
    print(f"\n  VERDICT: SUGGESTIVE — wave features visible but parabola adequate for 8 points.")
    print(f"  Dylan's prediction is plausible. More data (finer scales) needed.")
else:
    print(f"\n  VERDICT: NOT CONFIRMED — parabola suffices for current data.")
