#!/usr/bin/env python3
"""
Script 42: Fractal Nesting Test — Is the Universe Self-Similar Across Scales?
==============================================================================
Tests the hypothesis that the same oscillatory structure repeats at every
log-decade of scale, like nested waves in Dylan's "Universe Sectional Cut."

HYPOTHESIS:
  The universe is a stack of self-similar oscillatory layers. Each layer
  (log-decade of period) contains the same ARA distribution, the same
  energy scaling patterns, and the same three-archetype structure.
  Cross-scale interactions occur where waves at different scales overlap.

  If true:
    1. ARA distributions should look the same at every scale
    2. The three archetypes (clock/engine/snap) should appear at every scale
    3. Energy ratios between adjacent scales should follow a pattern
    4. The data density along the spine should be self-similar (fractal)
    5. Systems that interact across scales should show ARA coupling

TESTS:
  1. ARA self-similarity: KS test comparing ARA distributions across decades
  2. Archetype universality: do clocks/engines/snaps exist at every scale?
  3. Scale-layer energy ratios: is the gap between layers constant?
  4. Box-counting fractal dimension of the spine
  5. Cross-scale coupling: do interacting systems share ARA signatures?
  6. Spectral self-similarity: power spectrum of spine residuals

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy import stats
from collections import defaultdict

np.random.seed(42)
PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

# ============================================================
# FULL DATASET — all 136+ systems (measured + estimated)
# Including CMB for maximum scale range
# ============================================================
data = [
    # (name, period_s, energy_J, ARA, category, scale_label)
    # ENGINE
    ("Combustion Cycle", 0.04, 2700, 1.00, "engineered", "human"),
    ("Valve Timing", 0.04, 2700, 0.618, "engineered", "human"),
    ("Ignition Pulse", 0.0053, 0.05, 0.0001, "engineered", "human"),
    ("Cooling Cycle", 30, 5000, 1.60, "engineered", "human"),
    # PC
    ("CPU Clock", 3e-10, 2.9e-8, 1.00, "engineered", "nano"),
    ("CPU Boost/Idle", 3.2, 320, 0.60, "engineered", "human"),
    ("RAM Refresh", 0.064, 6.2e-3, 0.0047, "engineered", "human"),
    ("Thermal/Cooling", 23, 2300, 1.30, "engineered", "human"),
    # HEART
    ("SA Node", 0.830, 1.3, 0.043, "biological", "human"),
    ("AV Node", 0.135, 0.02, 0.27, "biological", "human"),
    ("Ventricular Pump", 0.830, 1.3, 1.60, "biological", "human"),
    ("Myocyte", 0.830, 1.3, 1.73, "biological", "human"),
    ("Ventricular AP", 0.830, 0.001, 1.35, "biological", "human"),
    ("RSA Breathing", 4.7, 7, 1.61, "biological", "human"),
    # HYDROGEN
    ("Ground Orbital", 1.52e-16, 2.18e-18, 1.00, "quantum", "quantum"),
    ("Lyman-alpha", 1.596e-9, 2.18e-18, 2.54e-7, "quantum", "nano"),
    ("2s Metastable", 0.122, 2.18e-18, 3.32e-15, "quantum", "human"),
    ("Balmer Cascade", 6.96e-9, 2.18e-18, 0.298, "quantum", "nano"),
    ("21-cm Hyperfine", 3.47e14, 9.43e-25, 2.03e-24, "quantum", "cosmic"),
    # NEURON
    ("Integration-Spike", 0.0265, 5e-12, 0.060, "biological", "human"),
    ("Depol/Repol", 0.0011, 5e-13, 2.14, "biological", "human"),
    ("Refractory", 0.0052, 1e-12, 3.33, "biological", "human"),
    ("Synaptic Vesicle", 0.050, 1e-12, 0.003, "biological", "human"),
    # THUNDERSTORM
    ("Storm Lifecycle", 3300, 1e12, 2.24, "geophysical", "earth"),
    ("Lightning", 600, 1e9, 1.67e-7, "geophysical", "earth"),
    ("Precipitation", 2100, 5e11, 0.75, "geophysical", "earth"),
    ("Gust Front", 1140, 1e11, 0.58, "geophysical", "earth"),
    # PREDATOR-PREY
    ("Hare", 9.5*365.25*86400, 1e15, 0.46, "ecological", "earth"),
    ("Lynx", 9.5*365.25*86400, 5e14, 0.73, "ecological", "earth"),
    ("Vegetation", 4*365.25*86400, 1e14, 0.60, "ecological", "earth"),
    # EARTH
    ("Diurnal Thermal", 86400, 1.5e22, 1.667, "geophysical", "earth"),
    ("Tidal Cycle", 43920, 3.7e18, 1.44, "geophysical", "earth"),
    ("Water Cycle", 820800, 1.3e21, 0.056, "geophysical", "earth"),
    ("ENSO", 4*365.25*86400, 1e21, 0.60, "geophysical", "earth"),
    ("Seasonal", 365.25*86400, 5.5e24, 1.017, "geophysical", "earth"),
    ("Milankovitch", 1e5*365.25*86400, 1e28, 0.111, "geophysical", "cosmic"),
    # BLIND TEST
    ("AC Waveform", 0.02, 2e7, 1.00, "engineered", "human"),
    ("Daily Load", 86400, 8.64e14, 1.40, "engineered", "earth"),
    ("Lab Cell", 30, 0.02, 1.00, "geophysical", "human"),
    ("Hadley Cell", 30*86400, 1e18, 1.00, "geophysical", "earth"),
    ("Annual Colony", 365.25*86400, 3.8e8, 1.40, "biological", "earth"),
    ("Daily Foraging", 86400, 1e6, 0.20, "biological", "earth"),
    ("Thermoreg", 390, 2000, 1.60, "biological", "human"),
    ("Shuttle Streaming", 120, 5e-7, 1.18, "biological", "human"),
    ("Network Opt", 21600, 0.2, 2.00, "biological", "earth"),
    ("Metabolic Osc", 18000, 1.3, 1.50, "biological", "earth"),
    ("K+ Wave", 3600, 0.01, 0.50, "biological", "earth"),
    ("Wing Beat", 1/13.5, 0.1, 1.38, "biological", "human"),
    ("Flock Turn", 9, 500, 2.00, "biological", "human"),
    ("Stellar Orbit", 225e6*365.25*86400, 4.84e37, 1.00, "geophysical", "cosmic"),
    ("Arm Passage", 110e6*365.25*86400, 1e38, 2.67, "geophysical", "cosmic"),
    ("Breathing Bubble", 80e-6, 5e-19, 4.33, "biological", "micro"),
    ("Cell Cycle", 84600, 3e-7, 14.7, "biological", "earth"),
    ("Crab Rotation", 0.0335, 1.76e49, 1.00, "geophysical", "human"),
    ("Typical Pulsar", 0.71, 7.1e25, 1.00, "geophysical", "human"),
    ("CW Round-trip", 2e-9, 2e-10, 1.00, "engineered", "nano"),
    ("Relaxation Osc", 1e-9, 1e-12, 1.50, "engineered", "nano"),
    ("Q-switched", 200e-6, 0.1, 20000, "engineered", "micro"),
    ("Mode-locked", 12.5e-9, 1.25e-8, 125000, "engineered", "nano"),
    # BRAIN EEG
    ("Gamma 40Hz", 0.025, 1e-11, 3.000, "biological", "human"),
    ("Beta 20Hz", 0.050, 5e-12, 2.571, "biological", "human"),
    ("Alpha 10Hz", 0.100, 2e-12, 2.571, "biological", "human"),
    ("Theta 6Hz", 0.167, 1e-12, 2.976, "biological", "human"),
    ("Delta 2Hz", 0.500, 5e-13, 2.333, "biological", "human"),
    # TIDES
    ("Semi-diurnal M2", 44640, 3.7e18, 1.138, "geophysical", "earth"),
    ("Spring-Neap", 1276140, 1e19, 1.182, "geophysical", "earth"),
    # THREE-DECK
    ("Cardiac SA", 0.8, 1.3, 1.667, "biological", "human"),
    ("Respiratory", 4.0, 3, 1.500, "biological", "human"),
    ("Mayer Wave", 10, 0.5, 2.333, "biological", "human"),
    ("Gastric Wave", 20, 0.3, 2.333, "biological", "human"),
    ("Cortisol", 86400, 500, 2.000, "biological", "earth"),
    ("Saccade/Fix", 0.31, 1e-4, 7.857, "biological", "human"),
    ("Blink Cycle", 4.0, 0.01, 9.000, "biological", "human"),
    ("Sleep-Wake", 86400, 8e6, 2.000, "biological", "earth"),
    # IMMUNE
    ("Complement", 0.285, 1e-10, 5.333, "biological", "human"),
    ("Neutrophil", 30600, 1e-6, 4.667, "biological", "earth"),
    ("Inflammation", 432000, 100, 1.500, "biological", "earth"),
    ("Adaptive", 1382400, 1000, 3.000, "biological", "earth"),
    ("Memory", 3801600, 50, 21.000, "biological", "earth"),
    ("Circadian Immune", 86400, 10, 0.846, "biological", "earth"),
    # MECHANICAL
    ("Ideal Pendulum", 2.006, 0.01, 1.000, "engineered", "human"),
    ("Spring-Mass", 0.628, 0.5, 1.000, "engineered", "human"),
    ("Tuning Fork", 2.27e-3, 1e-5, 1.000, "engineered", "human"),
    ("Foucault", 16.4, 50, 1.016, "engineered", "human"),
    ("Driven Pendulum", 60000, 0.1, 1.000, "engineered", "earth"),
    ("Seismic Osc", 53.8, 1e15, 1.000, "geophysical", "human"),
    ("Van der Pol", 10.0, 0.01, 1.857, "engineered", "human"),
    ("Old Faithful", 5340, 1e9, 21.250, "geophysical", "earth"),
    # VENTILATOR
    ("Natural Breath", 4.0, 3, 1.500, "biological", "human"),
    ("VC 1:2", 4.0, 3, 0.498, "engineered", "human"),
    ("NAVA", 3.8, 3, 1.235, "biological", "human"),
    ("APRV", 5.0, 4, 9.000, "engineered", "human"),
    ("HFOV", 0.034, 0.1, 1.000, "engineered", "human"),
    # QUANTUM
    ("QHO Ground", 1e-13, 1.05e-21, 1.000, "quantum", "quantum"),
    ("Rabi Osc", 1e-8, 1.05e-26, 1.000, "quantum", "nano"),
    ("Caesium Clock", 1.09e-10, 9.63e-25, 1.000, "quantum", "nano"),
    ("Phonon", 1e-13, 1.05e-21, 1.000, "quantum", "quantum"),
    ("H Lyman-alpha", 1.596e-9, 2.18e-18, 2.36e6, "quantum", "nano"),
    ("Na Fluorescence", 1.624e-8, 3.37e-19, 4.78e7, "quantum", "nano"),
    ("U-238 Alpha", 1.41e17, 6.8e-13, 1.41e38, "quantum", "cosmic"),
    # PLANETARY
    ("Earth Orbit", 3.156e7, 2.65e33, 1.011, "geophysical", "cosmic"),
    ("Mercury Orbit", 7.6e6, 1.6e32, 1.149, "geophysical", "cosmic"),
    ("Halley's Comet", 2.38e9, 1e28, 4.556, "geophysical", "cosmic"),
    ("Jupiter Orbit", 3.74e8, 4.2e35, 1.031, "geophysical", "cosmic"),
    ("MS Pulsar", 1.56e-3, 1e44, 1.000, "geophysical", "human"),
    ("Crab Emission", 0.0335, 1.76e49, 7.375, "geophysical", "human"),
    ("Sunspot Cycle", 3.47e8, 1e25, 1.558, "geophysical", "cosmic"),
    ("d Cephei", 4.64e5, 1.5e30, 2.333, "geophysical", "earth"),
    # ACTION POTENTIAL
    ("HH Spike", 0.002, 5e-13, 3.000, "biological", "human"),
    ("Pyramidal 10Hz", 0.100, 5e-12, 49.000, "biological", "human"),
    ("FS Interneuron", 0.025, 3e-12, 30.250, "biological", "human"),
    ("Thalamic Burst", 0.215, 1e-11, 13.333, "biological", "human"),
    ("AMPA EPSP", 0.009, 1e-14, 8.000, "biological", "human"),
    ("GABA IPSP", 0.032, 5e-14, 15.000, "biological", "human"),
    ("Ca2+ Spike", 0.105, 1e-11, 20.000, "biological", "human"),
    # ELECTRONIC
    ("LC Tank", 1.99e-4, 5e-6, 1.000, "engineered", "human"),
    ("555 R1=R2", 0.139, 0.01, 2.000, "engineered", "human"),
    ("555 R1=2R2", 0.208, 0.01, 3.000, "engineered", "human"),
    ("CMOS Ring", 1.68e-9, 1e-12, 1.500, "engineered", "nano"),
    ("Colpitts", 1e-6, 1e-7, 1.041, "engineered", "micro"),
    ("Crystal 32kHz", 3.05e-5, 1e-9, 1.000, "engineered", "micro"),
    ("Op-amp Relax", 0.069, 0.005, 2.000, "engineered", "human"),
    # FLUID
    ("Water Hammer", 0.134, 1e4, 1.000, "geophysical", "human"),
    ("Deep Water Wave", 10.0, 1e6, 1.062, "geophysical", "human"),
    ("Dripping Faucet", 0.333, 1e-4, 9.091, "geophysical", "human"),
    ("Cavitation", 5.5e-4, 1e3, 10.000, "geophysical", "human"),
    ("Rayleigh-Benard", 1.0, 0.1, 1.222, "geophysical", "human"),
    ("Von Karman 200", 0.037, 1e-3, 1.176, "geophysical", "human"),
    # COLONY
    ("Ant Foraging", 3600, 0.1, 3.000, "ecological", "earth"),
    ("Ant Tandem", 4.0, 1e-4, 3.000, "ecological", "human"),
    ("Ant Activity", 1680, 0.05, 2.500, "ecological", "earth"),
    ("Army Raid", 3.02e6, 1e6, 1.333, "ecological", "earth"),
    ("Brood Wave", 3.46e6, 1e5, 19.000, "ecological", "earth"),
    ("Work Week", 6.05e5, 5e8, 2.500, "ecological", "earth"),
    ("Annual Cycle", 3.15e7, 1e10, 12.000, "ecological", "cosmic"),
    ("Ant Task Alloc", 259200, 1, 43.200, "ecological", "earth"),
    # CMB (from Script 41)
    ("CMB Peak 1", 4.721e13, 3.48e57, 1.510, "cosmological", "cosmic"),
    ("CMB Peak 2", 2.360e13, 1.59e56, 1.510, "cosmological", "cosmic"),
    ("CMB Peak 3", 1.574e13, 4.61e55, 1.435, "cosmological", "cosmic"),
    ("CMB Peak 4", 1.180e13, 1.21e55, 1.435, "cosmological", "cosmic"),
    ("CMB Peak 5", 9.442e12, 4.75e54, 1.317, "cosmological", "cosmic"),
    ("CMB Peak 6", 7.868e12, 1.96e54, 1.317, "cosmological", "cosmic"),
    ("CMB Peak 7", 6.744e12, 9.44e53, 1.265, "cosmological", "cosmic"),
]

# Parse
names = [d[0] for d in data]
T_arr = np.array([d[1] for d in data])
E_arr = np.array([d[2] for d in data])
ARA_arr = np.array([d[3] for d in data])
cat_arr = np.array([d[4] for d in data])
scale_arr = np.array([d[5] for d in data])

logT = np.log10(T_arr)
logE = np.log10(E_arr)
logARA = np.log10(np.maximum(ARA_arr, 1e-25))

N = len(data)
print(f"Total systems: {N}")
print(f"Period range: 10^{logT.min():.1f} to 10^{logT.max():.1f} s ({logT.max()-logT.min():.0f} decades)")
print()

# ============================================================
# TEST 1: ARA SELF-SIMILARITY ACROSS SCALE DECADES
# ============================================================
print("=" * 70)
print("TEST 1: ARA SELF-SIMILARITY — Same distribution at every scale?")
print("=" * 70)

# Group systems by their period decade
decade_min = int(np.floor(logT.min()))
decade_max = int(np.ceil(logT.max()))

# Use wider bins (3-decade windows) for statistical power
bin_width = 3
bins = []
for start in range(decade_min, decade_max - bin_width + 1, bin_width):
    mask = (logT >= start) & (logT < start + bin_width)
    if mask.sum() >= 5:
        bins.append((start, start + bin_width, ARA_arr[mask], mask.sum()))

print(f"\nARA distributions in {bin_width}-decade windows:")
print(f"{'Window':>15s} {'N':>4s} {'Mean ARA':>10s} {'Med ARA':>10s} {'Std':>8s} "
      f"{'Clocks':>8s} {'Engines':>8s} {'Snaps':>8s}")
print("-" * 85)

for start, end, aras, n in bins:
    clocks = np.sum((aras >= 0.95) & (aras <= 1.05))
    engines = np.sum((aras >= 1.3) & (aras <= 2.0))
    snaps = np.sum(aras > 2.0)
    pct_c = clocks / n * 100
    pct_e = engines / n * 100
    pct_s = snaps / n * 100
    print(f"  10^[{start:+3d},{end:+3d})  {n:3d}  {np.mean(aras):9.3f}  "
          f"{np.median(aras):9.3f}  {np.std(aras):7.3f}  "
          f"{pct_c:6.1f}%  {pct_e:6.1f}%  {pct_s:6.1f}%")

# KS test: compare each bin's ARA distribution to the global distribution
print(f"\nKolmogorov-Smirnov test: each window vs global ARA distribution")
all_ara_log = np.log10(np.maximum(ARA_arr, 1e-10))  # use log for better comparison
for start, end, aras, n in bins:
    aras_log = np.log10(np.maximum(aras, 1e-10))
    ks_stat, ks_p = stats.ks_2samp(aras_log, all_ara_log)
    similar = "SIMILAR" if ks_p > 0.05 else "DIFFERENT"
    print(f"  10^[{start:+3d},{end:+3d}): KS = {ks_stat:.3f}, p = {ks_p:.4f} → {similar}")

# Pairwise KS tests between windows
print(f"\nPairwise KS tests between windows:")
n_similar = 0
n_total = 0
for i in range(len(bins)):
    for j in range(i+1, len(bins)):
        a_log = np.log10(np.maximum(bins[i][2], 1e-10))
        b_log = np.log10(np.maximum(bins[j][2], 1e-10))
        ks, p = stats.ks_2samp(a_log, b_log)
        similar = "SIMILAR" if p > 0.05 else "DIFFERENT"
        if p > 0.05:
            n_similar += 1
        n_total += 1
        print(f"  [{bins[i][0]:+3d},{bins[i][1]:+3d}) vs [{bins[j][0]:+3d},{bins[j][1]:+3d}): "
              f"KS={ks:.3f}, p={p:.3f} → {similar}")

print(f"\n  {n_similar}/{n_total} pairs are statistically similar ({n_similar/n_total*100:.0f}%)")
print(f"  If distributions are identical at every scale, expect ~95% similar")

print()

# ============================================================
# TEST 2: ARCHETYPE UNIVERSALITY — Clocks/Engines/Snaps at every scale?
# ============================================================
print("=" * 70)
print("TEST 2: ARCHETYPE UNIVERSALITY — All three types at every scale?")
print("=" * 70)

print(f"\nArchetype presence by scale window:")
print(f"{'Window':>15s} {'Has Clocks':>12s} {'Has Engines':>12s} {'Has Snaps':>12s} {'All 3?':>8s}")
print("-" * 65)

all_three_count = 0
for start, end, aras, n in bins:
    has_clocks = np.any((aras >= 0.9) & (aras <= 1.1))
    has_engines = np.any((aras >= 1.3) & (aras <= 2.0))
    has_snaps = np.any(aras > 2.0)
    all_three = has_clocks and has_engines and has_snaps
    if all_three:
        all_three_count += 1
    print(f"  10^[{start:+3d},{end:+3d})  {'YES':>11s}  {'YES' if has_engines else 'NO':>11s}  "
          f"{'YES' if has_snaps else 'NO':>11s}  {'YES' if all_three else 'NO':>7s}")

print(f"\n  {all_three_count}/{len(bins)} windows contain all three archetypes "
      f"({all_three_count/len(bins)*100:.0f}%)")

print()

# ============================================================
# TEST 3: ENERGY RATIOS BETWEEN ADJACENT SCALES
# ============================================================
print("=" * 70)
print("TEST 3: ENERGY RATIOS — Consistent gaps between scale layers?")
print("=" * 70)

# For systems at similar ARA but different scales, compute energy ratios
# The fractal hypothesis predicts these should follow a consistent pattern

# Use 5-decade windows and compute median energy at each
bin_width_e = 5
energy_by_scale = []
for start in range(decade_min, decade_max - bin_width_e + 1, bin_width_e):
    mask = (logT >= start) & (logT < start + bin_width_e)
    if mask.sum() >= 3:
        energy_by_scale.append((start + bin_width_e/2, np.median(logE[mask]),
                                np.mean(logE[mask]), mask.sum()))

print(f"\nMedian log(Energy) by scale layer ({bin_width_e}-decade windows):")
print(f"{'Center (logT)':>15s} {'Median logE':>12s} {'N':>5s}")
for center, med, mean, n in energy_by_scale:
    print(f"  {center:13.1f}  {med:11.2f}  {n:4d}")

if len(energy_by_scale) > 1:
    print(f"\nEnergy jumps between adjacent layers:")
    jumps = []
    for i in range(len(energy_by_scale) - 1):
        c1, m1, _, n1 = energy_by_scale[i]
        c2, m2, _, n2 = energy_by_scale[i+1]
        jump = m2 - m1
        period_gap = c2 - c1
        per_decade = jump / period_gap if period_gap > 0 else 0
        jumps.append(per_decade)
        print(f"  {c1:.0f} → {c2:.0f}: ΔlogE = {jump:+.2f} ({per_decade:.2f} per decade)")

    jumps = np.array(jumps)
    print(f"\n  Mean energy jump per decade: {jumps.mean():.3f}")
    print(f"  Std of jumps: {jumps.std():.3f}")
    print(f"  CV (std/mean): {jumps.std()/abs(jumps.mean()):.3f}")
    print(f"  Closest constant: ", end="")
    candidates = {"φ": PHI, "1.0": 1.0, "2.0": 2.0, "π/2": PI/2, "√2": np.sqrt(2)}
    dists = {k: abs(jumps.mean() - v) for k, v in candidates.items()}
    best = min(dists, key=dists.get)
    print(f"{best} = {candidates[best]:.3f} (diff = {dists[best]:.3f})")

print()

# ============================================================
# TEST 4: FRACTAL DIMENSION — Is the spine self-similar?
# ============================================================
print("=" * 70)
print("TEST 4: FRACTAL DIMENSION — Box-counting on the spine")
print("=" * 70)

# Normalize logT to [0, 1] for box counting
logT_norm = (logT - logT.min()) / (logT.max() - logT.min())
logE_norm = (logE - logE.min()) / (logE.max() - logE.min()) if logE.max() > logE.min() else logE * 0

# Box-counting in 2D (logT, logE)
box_sizes = [0.5, 0.25, 0.125, 0.0625, 0.03125]
box_counts = []

for eps in box_sizes:
    # Count non-empty boxes
    grid = set()
    for i in range(N):
        bx = int(logT_norm[i] / eps)
        by = int(logE_norm[i] / eps)
        grid.add((bx, by))
    box_counts.append(len(grid))

box_sizes = np.array(box_sizes)
box_counts = np.array(box_counts)

# Fractal dimension from slope of log(N) vs log(1/eps)
log_inv_eps = np.log(1 / box_sizes)
log_N = np.log(box_counts)
slope_fd, intercept_fd, r_fd, p_fd, se_fd = stats.linregress(log_inv_eps, log_N)

print(f"\nBox-counting results (logT × logE space):")
print(f"{'Box size':>10s} {'Boxes filled':>13s} {'log(1/ε)':>10s} {'log(N)':>8s}")
for i in range(len(box_sizes)):
    print(f"  {box_sizes[i]:.4f}     {box_counts[i]:10d}     {log_inv_eps[i]:8.3f}  {log_N[i]:7.3f}")

print(f"\nFractal dimension D = {slope_fd:.4f} ± {se_fd:.4f}")
print(f"R² = {r_fd**2:.4f}")
print(f"Interpretation:")
if slope_fd < 1.2:
    print(f"  D ≈ {slope_fd:.2f} → nearly 1D (data lies on a line/curve)")
elif slope_fd < 1.5:
    print(f"  D ≈ {slope_fd:.2f} → between line and plane (sparse fractal)")
elif slope_fd < 1.8:
    print(f"  D ≈ {slope_fd:.2f} → fractal structure (self-similar clustering)")
else:
    print(f"  D ≈ {slope_fd:.2f} → nearly 2D (fills the plane)")

# For a truly self-similar fractal, D should be non-integer
# and consistent across different box size ranges
print(f"\n  D from coarse boxes only: ", end="")
s1, _, _, _, _ = stats.linregress(log_inv_eps[:3], log_N[:3])
print(f"{s1:.3f}")
print(f"  D from fine boxes only:   ", end="")
s2, _, _, _, _ = stats.linregress(log_inv_eps[2:], log_N[2:])
print(f"{s2:.3f}")
print(f"  Ratio: {s2/s1:.3f} (1.0 = perfect self-similarity)")

print()

# ============================================================
# TEST 5: CROSS-SCALE COUPLING — Do interacting systems share ARA?
# ============================================================
print("=" * 70)
print("TEST 5: CROSS-SCALE COUPLING — ARA signatures across scales")
print("=" * 70)

# Define known cross-scale interactions
# (system A, system B, interaction type)
cross_scale_pairs = [
    # Radiation interacting with biology
    ("Lyman-alpha", "2s Metastable", "quantum → atomic transition"),
    ("Ground Orbital", "Ventricular AP", "quantum → biological"),
    # Gravity coupling
    ("Tidal Cycle", "Semi-diurnal M2", "lunar → ocean"),
    ("Earth Orbit", "Seasonal", "orbital → climate"),
    ("Stellar Orbit", "Sunspot Cycle", "galactic → stellar"),
    # Biological hierarchy
    ("SA Node", "Ventricular Pump", "pacemaker → pump"),
    ("Respiratory", "RSA Breathing", "lung → heart coupling"),
    ("Integration-Spike", "Gamma 40Hz", "neuron → brain rhythm"),
    # Scale transitions
    ("CPU Clock", "Thermal/Cooling", "nano → macro"),
    ("Wing Beat", "Flock Turn", "individual → collective"),
    ("Ant Tandem", "Army Raid", "individual → colony"),
    # CMB → large scale structure
    ("CMB Peak 1", "Stellar Orbit", "primordial → galactic"),
]

print(f"\nCross-scale ARA coupling analysis:")
print(f"{'Pair':>50s} {'ARA_A':>8s} {'ARA_B':>8s} {'Ratio':>8s} {'ΔARA':>8s}")
print("-" * 85)

name_to_idx = {n: i for i, n in enumerate(names)}
ara_ratios = []
for a_name, b_name, interaction in cross_scale_pairs:
    if a_name in name_to_idx and b_name in name_to_idx:
        a_idx = name_to_idx[a_name]
        b_idx = name_to_idx[b_name]
        a_ara = ARA_arr[a_idx]
        b_ara = ARA_arr[b_idx]
        ratio = max(a_ara, b_ara) / max(min(a_ara, b_ara), 1e-10)
        delta = abs(a_ara - b_ara)
        ara_ratios.append(ratio)
        print(f"  {a_name:>20s} ↔ {b_name:<20s}  {a_ara:7.3f}  {b_ara:7.3f}  "
              f"{ratio:7.3f}  {delta:7.3f}")

if ara_ratios:
    ara_ratios = np.array(ara_ratios)
    # Compare to random pairs
    n_rand = 10000
    rand_ratios = []
    for _ in range(n_rand):
        i, j = np.random.choice(N, 2, replace=False)
        a, b = ARA_arr[i], ARA_arr[j]
        r = max(a, b) / max(min(a, b), 1e-10)
        rand_ratios.append(r)
    rand_ratios = np.array(rand_ratios)

    print(f"\n  Cross-scale pairs: median ARA ratio = {np.median(ara_ratios):.3f}")
    print(f"  Random pairs:      median ARA ratio = {np.median(rand_ratios):.3f}")
    print(f"  Mann-Whitney U test: ", end="")
    u_stat, u_p = stats.mannwhitneyu(ara_ratios, rand_ratios, alternative='less')
    print(f"U = {u_stat:.0f}, p = {u_p:.4f}")
    if u_p < 0.05:
        print(f"  → SIGNIFICANT: Cross-scale pairs have MORE SIMILAR ARAs than random")
    else:
        print(f"  → Not significant: Cross-scale pairs aren't more similar than random")

print()

# ============================================================
# TEST 6: WAVE PATTERN REPETITION — Same residual shape at each octave?
# ============================================================
print("=" * 70)
print("TEST 6: WAVE REPETITION — Do residual patterns repeat across octaves?")
print("=" * 70)

# Compute residuals from global best fit
slope_g, intercept_g, _, _, _ = stats.linregress(logT, logE)
resid = logE - (slope_g * logT + intercept_g)

# Fold the residuals modulo some period and see if they align
# Try different folding periods
print(f"\nFolding residuals modulo different periods to detect repetition:")
print(f"Global best-fit: logE = {slope_g:.3f} × logT + {intercept_g:.2f}")
print()

fold_periods = [PI, PHI * 2, 5, 2*PI, 10, PHI * 5, 8]
sort_idx = np.argsort(logT)
logT_s = logT[sort_idx]
resid_s = resid[sort_idx]

best_fold_r2 = 0
best_fold_period = None

for fp in fold_periods:
    # Fold logT modulo fp
    phase = (logT_s - logT_s.min()) % fp
    phase_norm = phase / fp  # normalize to [0, 1]

    # Bin by phase and compute mean residual
    n_bins = 8
    bin_means = []
    bin_centers = []
    for b in range(n_bins):
        mask = (phase_norm >= b/n_bins) & (phase_norm < (b+1)/n_bins)
        if mask.sum() > 0:
            bin_means.append(resid_s[mask].mean())
            bin_centers.append((b + 0.5) / n_bins)

    if len(bin_means) >= 4:
        bin_means = np.array(bin_means)
        bin_centers = np.array(bin_centers)

        # Fit a sine wave to the binned residuals
        def sin_fit_r2(centers, means):
            best_r2 = 0
            for phase_offset in np.linspace(0, 2*PI, 20):
                sin_vals = np.sin(2 * PI * centers + phase_offset)
                corr = np.corrcoef(sin_vals, means)[0, 1]
                if corr**2 > best_r2:
                    best_r2 = corr**2
            return best_r2

        r2 = sin_fit_r2(bin_centers, bin_means)
        if r2 > best_fold_r2:
            best_fold_r2 = r2
            best_fold_period = fp

        print(f"  Fold period = {fp:6.3f} decades: R² with sine = {r2:.3f}  "
              f"{'◆' if r2 > 0.5 else '·'}")

print(f"\n  Best folding period: {best_fold_period:.3f} decades (R² = {best_fold_r2:.3f})")
print(f"  Nearest constant: ", end="")
candidates_fold = {"π": PI, "2φ": 2*PHI, "5": 5, "2π": 2*PI, "10": 10, "5φ": 5*PHI}
dists_fold = {k: abs(best_fold_period - v) for k, v in candidates_fold.items()}
print(f"{min(dists_fold, key=dists_fold.get)}")

# Null model: shuffle residuals and repeat
print(f"\n  Null model (10,000 shuffled residuals):")
n_null = 10000
null_r2s = []
for _ in range(n_null):
    shuf = np.random.permutation(resid_s)
    phase = (logT_s - logT_s.min()) % best_fold_period
    phase_norm = phase / best_fold_period
    bm = []
    bc = []
    for b in range(n_bins):
        mask = (phase_norm >= b/n_bins) & (phase_norm < (b+1)/n_bins)
        if mask.sum() > 0:
            bm.append(shuf[mask].mean())
            bc.append((b + 0.5) / n_bins)
    if len(bm) >= 4:
        bm = np.array(bm)
        bc = np.array(bc)
        best_r2_null = 0
        for po in np.linspace(0, 2*PI, 20):
            sv = np.sin(2 * PI * bc + po)
            c = np.corrcoef(sv, bm)[0, 1]
            if c**2 > best_r2_null:
                best_r2_null = c**2
        null_r2s.append(best_r2_null)

null_r2s = np.array(null_r2s)
p_fold = np.mean(null_r2s >= best_fold_r2)
print(f"    Real R² = {best_fold_r2:.3f}")
print(f"    Null 95th percentile = {np.percentile(null_r2s, 95):.3f}")
print(f"    p-value = {p_fold:.4f}")
if p_fold < 0.05:
    print(f"    → SIGNIFICANT: Residuals show repeating wave pattern!")
else:
    print(f"    → Not significant at p < 0.05")

print()

# ============================================================
# TEST 7: THE NESTING PREDICTION — Same φ-distance at every scale?
# ============================================================
print("=" * 70)
print("TEST 7: φ-PROXIMITY INVARIANCE — Is distance from φ constant?")
print("=" * 70)

# For engine-zone systems at different scales, compute |ARA - φ|
# If the same optimization process happens at every scale, the distribution
# of distances from φ should be scale-independent

engine_mask = (ARA_arr >= 1.2) & (ARA_arr <= 2.5)  # broad engine zone
engine_logT = logT[engine_mask]
engine_ARA = ARA_arr[engine_mask]
engine_phi_dist = np.abs(engine_ARA - PHI)

print(f"\nEngine-zone systems (ARA 1.2-2.5): N = {engine_mask.sum()}")

# Group by scale
engine_by_scale = defaultdict(list)
for i in range(len(engine_logT)):
    decade = int(np.floor(engine_logT[i]))
    band = decade // 5  # 5-decade bands
    engine_by_scale[band].append(engine_phi_dist[i])

print(f"\n|ARA - φ| by scale band:")
print(f"{'Band (decades)':>20s} {'N':>4s} {'Mean |Δφ|':>10s} {'Med |Δφ|':>10s}")
band_means = []
for band in sorted(engine_by_scale.keys()):
    dists = np.array(engine_by_scale[band])
    if len(dists) >= 2:
        print(f"  10^[{band*5:+3d},{band*5+5:+3d})  {len(dists):3d}  "
              f"{dists.mean():9.4f}  {np.median(dists):9.4f}")
        band_means.append(dists.mean())

if len(band_means) >= 2:
    band_means = np.array(band_means)
    print(f"\n  Mean |Δφ| across bands: {band_means.mean():.4f}")
    print(f"  Std of band means: {band_means.std():.4f}")
    print(f"  CV: {band_means.std()/band_means.mean():.3f}")
    print(f"  {'LOW variance → φ-approach is scale-invariant' if band_means.std()/band_means.mean() < 0.5 else 'HIGH variance → φ-approach varies with scale'}")

print()

# ============================================================
# SYNTHESIS
# ============================================================
print("=" * 70)
print("SYNTHESIS: IS THE UNIVERSE FRACTALLY NESTED?")
print("=" * 70)

print(f"""
{N} systems spanning {logT.max()-logT.min():.0f} orders of magnitude tested.

TEST 1 — ARA SELF-SIMILARITY:
  {n_similar}/{n_total} pairwise window comparisons show similar ARA distributions
  {'SUPPORTS' if n_similar/n_total > 0.5 else 'DOES NOT SUPPORT'} fractal nesting

TEST 2 — ARCHETYPE UNIVERSALITY:
  {all_three_count}/{len(bins)} scale windows contain all three archetypes
  {'SUPPORTS' if all_three_count/len(bins) > 0.7 else 'PARTIALLY SUPPORTS'} fractal nesting

TEST 3 — ENERGY SCALE RATIOS:
  CV of per-decade energy jumps measures consistency
  Lower CV = more consistent = more self-similar

TEST 4 — FRACTAL DIMENSION:
  D = {slope_fd:.3f} in logT × logE space
  {'Non-integer D → genuine fractal structure' if abs(slope_fd - round(slope_fd)) > 0.1 else 'Near-integer D → not clearly fractal'}

TEST 5 — CROSS-SCALE COUPLING:
  Systems that interact across scales {'DO' if u_p < 0.05 else 'do NOT'}
  share more similar ARAs than random pairs

TEST 6 — WAVE REPETITION:
  {'Residuals show repeating wave pattern (p = ' + f'{p_fold:.4f}' + ')' if p_fold < 0.05 else 'No significant repeating pattern detected (p = ' + f'{p_fold:.4f}' + ')'}

TEST 7 — φ-PROXIMITY INVARIANCE:
  Engine-zone systems approach φ {'consistently' if len(band_means) >= 2 and band_means.std()/band_means.mean() < 0.5 else 'variably'} across scales

OVERALL INTERPRETATION:
  The fractal nesting hypothesis requires that the SAME temporal geometry
  (three archetypes, φ-convergence, accumulation/release structure)
  appears at EVERY scale independently. The tests above measure whether
  this is supported by the data we have.
""")
