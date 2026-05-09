#!/usr/bin/env python3
"""
Script 38: The Complexity-Scale Curve
======================================
Extracts all 3D temporal coordinates (logT, logARA, logAction/π) from 37 systems,
fits the apparent curve through the data, and tests for φ/π in the parameterisation.

The hypothesis: oscillatory systems in nature don't fill 3D temporal space —
they trace a 1D curve. If true, Period, ARA, and Action/π are not independent.
There is ONE line through temporal space and every system sits on or near it.

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import UnivariateSpline
from sklearn.decomposition import PCA
import json

PI = np.pi
PHI = (1 + np.sqrt(5)) / 2

# ============================================================
# ALL DATA — (name, system, period_s, energy_J, ARA)
# ============================================================
data = [
    # ENGINE
    ("Combustion Cycle", "Engine", 0.04, 2700, 1.00),
    ("Valve Timing", "Engine", 0.04, 2700, 0.618),
    ("Ignition Pulse", "Engine", 0.0053, 0.05, 0.0001),
    ("Cooling Cycle", "Engine", 30, 5000, 1.60),
    # PC
    ("CPU Clock", "PC", 3e-10, 2.9e-8, 1.00),
    ("CPU Boost/Idle", "PC", 3.2, 320, 0.60),
    ("RAM Refresh", "PC", 0.064, 6.2e-3, 0.0047),
    ("Thermal/Cooling", "PC", 23, 2300, 1.30),
    # HEART
    ("SA Node", "Heart", 0.830, 1.3, 0.043),
    ("AV Node", "Heart", 0.135, 0.02, 0.27),
    ("Ventricular Pump", "Heart", 0.830, 1.3, 1.60),
    ("Myocyte", "Heart", 0.830, 1.3, 1.73),
    ("Ventricular AP", "Heart", 0.830, 0.001, 1.35),
    ("RSA Breathing", "Heart", 4.7, 7, 1.61),
    # HYDROGEN
    ("Ground Orbital", "Hydrogen", 1.52e-16, 2.18e-18, 1.00),
    ("Lyman-alpha", "Hydrogen", 1.596e-9, 2.18e-18, 2.54e-7),
    ("2s Metastable", "Hydrogen", 0.122, 2.18e-18, 3.32e-15),
    ("Balmer Cascade", "Hydrogen", 6.96e-9, 2.18e-18, 0.298),
    ("21-cm Hyperfine", "Hydrogen", 3.47e14, 9.43e-25, 2.03e-24),
    # NEURON (original)
    ("Integration→Spike", "Neuron", 0.0265, 5e-12, 0.060),
    ("Depol/Repol", "Neuron", 0.0011, 5e-13, 2.14),
    ("Refractory", "Neuron", 0.0052, 1e-12, 3.33),
    ("Synaptic Vesicle", "Neuron", 0.050, 1e-12, 0.003),
    # THUNDERSTORM
    ("Storm Lifecycle", "Thunderstorm", 3300, 1e12, 2.24),
    ("Lightning", "Thunderstorm", 600, 1e9, 1.67e-7),
    ("Precipitation", "Thunderstorm", 2100, 5e11, 0.75),
    ("Gust Front", "Thunderstorm", 1140, 1e11, 0.58),
    # PREDATOR-PREY
    ("Hare", "Pred-Prey", 9.5*365.25*86400, 1e15, 0.46),
    ("Lynx", "Pred-Prey", 9.5*365.25*86400, 5e14, 0.73),
    ("Vegetation", "Pred-Prey", 4*365.25*86400, 1e14, 0.60),
    # EARTH
    ("Diurnal Thermal", "Earth", 86400, 1.5e22, 1.667),
    ("Tidal Cycle", "Earth", 43920, 3.7e18, 1.44),
    ("Water Cycle", "Earth", 820800, 1.3e21, 0.056),
    ("ENSO", "Earth", 4*365.25*86400, 1e21, 0.60),
    ("Seasonal", "Earth", 365.25*86400, 5.5e24, 1.017),
    ("Milankovitch", "Earth", 1e5*365.25*86400, 1e28, 0.111),
    # BLIND TEST SYSTEMS
    ("AC Waveform", "Energy Grid", 0.02, 2e7, 1.00),
    ("Daily Load", "Energy Grid", 86400, 8.64e14, 1.40),
    ("Lab Cell", "RB Convection", 30, 0.02, 1.00),
    ("Hadley Cell", "RB Convection", 30*86400, 1e18, 1.00),
    ("Annual Colony", "Honeybee", 365.25*86400, 3.8e8, 1.40),
    ("Daily Foraging", "Honeybee", 86400, 1e6, 0.20),
    ("Thermoreg", "Honeybee", 390, 2000, 1.60),
    ("Shuttle Streaming", "Slime Mold", 120, 5e-7, 1.18),
    ("Network Opt", "Slime Mold", 21600, 0.2, 2.00),
    ("Metabolic Osc", "Biofilm", 18000, 1.3, 1.50),
    ("K+ Wave", "Biofilm", 3600, 0.01, 0.50),
    ("Wing Beat", "Starling", 1/13.5, 0.1, 1.38),
    ("Flock Turn", "Starling", 9, 500, 2.00),
    ("Stellar Orbit", "Galaxy", 225e6*365.25*86400, 4.84e37, 1.00),
    ("Arm Passage", "Galaxy", 110e6*365.25*86400, 1e38, 2.67),
    ("Breathing Bubble", "DNA", 80e-6, 5e-19, 4.33),
    ("Cell Cycle", "DNA", 84600, 3e-7, 14.7),
    ("Crab Rotation", "Pulsar", 0.0335, 1.76e49, 1.00),
    ("Typical Pulsar", "Pulsar", 0.71, 7.1e25, 1.00),
    ("CW Round-trip", "Laser", 2e-9, 2e-10, 1.00),
    ("Relaxation Osc", "Laser", 1e-9, 1e-12, 1.50),
    ("Q-switched", "Laser", 200e-6, 0.1, 20000),
    ("Mode-locked", "Laser", 12.5e-9, 1.25e-8, 125000),
    # SYSTEM 24: BRAIN EEG
    ("Gamma 40Hz", "Brain EEG", 0.025, 1e-11, 3.000),
    ("Beta 20Hz", "Brain EEG", 0.050, 5e-12, 2.571),
    ("Alpha 10Hz", "Brain EEG", 0.100, 2e-12, 2.571),
    ("Theta 6Hz", "Brain EEG", 0.167, 1e-12, 2.976),
    ("Delta 2Hz", "Brain EEG", 0.500, 5e-13, 2.333),
    # SYSTEM 25: TIDES
    ("Semi-diurnal M2", "Tides", 44640, 3.7e18, 1.138),
    ("Spring-Neap", "Tides", 1276140, 1e19, 1.182),
    # SYSTEM 26: THREE-DECK
    ("Cardiac SA", "Three-Deck", 0.8, 1.3, 1.667),
    ("Respiratory", "Three-Deck", 4.0, 3, 1.500),
    ("Mayer Wave", "Three-Deck", 10, 0.5, 2.333),
    ("Gastric Wave", "Three-Deck", 20, 0.3, 2.333),
    ("Cortisol", "Three-Deck", 86400, 500, 2.000),
    ("Saccade/Fix", "Three-Deck", 0.31, 1e-4, 7.857),
    ("Blink Cycle", "Three-Deck", 4.0, 0.01, 9.000),
    ("Sleep-Wake", "Three-Deck", 86400, 8e6, 2.000),
    # SYSTEM 28: IMMUNE
    ("Complement", "Immune", 0.285, 1e-10, 5.333),
    ("Neutrophil", "Immune", 30600, 1e-6, 4.667),
    ("Inflammation", "Immune", 432000, 100, 1.500),
    ("Adaptive", "Immune", 1382400, 1000, 3.000),
    ("Memory", "Immune", 3801600, 50, 21.000),
    ("Circadian Immune", "Immune", 86400, 10, 0.846),
    # SYSTEM 29: MECHANICAL
    ("Ideal Pendulum", "Mechanical", 2.006, 0.01, 1.000),
    ("Spring-Mass", "Mechanical", 0.628, 0.5, 1.000),
    ("Tuning Fork", "Mechanical", 2.27e-3, 1e-5, 1.000),
    ("Foucault", "Mechanical", 16.4, 50, 1.016),
    # SYSTEM 30: FORCED
    ("Driven Pendulum", "Forced", 60000, 0.1, 1.000),
    ("Seismic Osc", "Forced", 53.8, 1e15, 1.000),
    ("Van der Pol", "Forced", 10.0, 0.01, 1.857),
    ("Old Faithful", "Forced", 5340, 1e9, 21.250),
    # SYSTEM 31: VENTILATOR
    ("Natural Breath", "Ventilator", 4.0, 3, 1.500),
    ("VC 1:2", "Ventilator", 4.0, 3, 0.498),
    ("NAVA", "Ventilator", 3.8, 3, 1.235),
    ("APRV", "Ventilator", 5.0, 4, 9.000),
    ("HFOV", "Ventilator", 0.034, 0.1, 1.000),
    # SYSTEM 32: QUANTUM
    ("QHO Ground", "Quantum", 1e-13, 1.05e-21, 1.000),
    ("Rabi Osc", "Quantum", 1e-8, 1.05e-26, 1.000),
    ("Caesium Clock", "Quantum", 1.09e-10, 9.63e-25, 1.000),
    ("Phonon", "Quantum", 1e-13, 1.05e-21, 1.000),
    ("H Lyman-alpha", "Quantum", 1.596e-9, 2.18e-18, 2.36e6),
    ("Na Fluorescence", "Quantum", 1.624e-8, 3.37e-19, 4.78e7),
    ("U-238 Alpha", "Quantum", 1.41e17, 6.8e-13, 1.41e38),
    # SYSTEM 33: PLANETARY
    ("Earth Orbit", "Planetary", 3.156e7, 2.65e33, 1.011),
    ("Mercury Orbit", "Planetary", 7.6e6, 1.6e32, 1.149),
    ("Halley's Comet", "Planetary", 2.38e9, 1e28, 4.556),
    ("Jupiter Orbit", "Planetary", 3.74e8, 4.2e35, 1.031),
    ("MS Pulsar", "Planetary", 1.56e-3, 1e44, 1.000),
    ("Crab Emission", "Planetary", 0.0335, 1.76e49, 7.375),
    ("Sunspot Cycle", "Planetary", 3.47e8, 1e25, 1.558),
    ("δ Cephei", "Planetary", 4.64e5, 1.5e30, 2.333),
    # SYSTEM 34: ACTION POTENTIAL
    ("HH Spike", "Action Pot", 0.002, 5e-13, 3.000),
    ("Pyramidal 10Hz", "Action Pot", 0.100, 5e-12, 49.000),
    ("FS Interneuron", "Action Pot", 0.025, 3e-12, 30.250),
    ("Thalamic Burst", "Action Pot", 0.215, 1e-11, 13.333),
    ("AMPA EPSP", "Action Pot", 0.009, 1e-14, 8.000),
    ("GABA IPSP", "Action Pot", 0.032, 5e-14, 15.000),
    ("Ca²⁺ Spike", "Action Pot", 0.105, 1e-11, 20.000),
    # SYSTEM 35: ELECTRONIC
    ("LC Tank", "Electronic", 1.99e-4, 5e-6, 1.000),
    ("555 (R1=R2)", "Electronic", 0.139, 0.01, 2.000),
    ("555 (R1=2R2)", "Electronic", 0.208, 0.01, 3.000),
    ("CMOS Ring", "Electronic", 1.68e-9, 1e-12, 1.500),
    ("Colpitts", "Electronic", 1e-6, 1e-7, 1.041),
    ("Crystal 32kHz", "Electronic", 3.05e-5, 1e-9, 1.000),
    ("Op-amp Relax", "Electronic", 0.069, 0.005, 2.000),
    # SYSTEM 36: FLUID
    ("Water Hammer", "Fluid", 0.134, 1e4, 1.000),
    ("Deep Water Wave", "Fluid", 10.0, 1e6, 1.062),
    ("Dripping Faucet", "Fluid", 0.333, 1e-4, 9.091),
    ("Cavitation", "Fluid", 5.5e-4, 1e3, 10.000),
    ("Rayleigh-Bénard", "Fluid", 1.0, 0.1, 1.222),
    ("Von Kármán 200", "Fluid", 0.037, 1e-3, 1.176),
    # SYSTEM 37: COLONY
    ("Ant Foraging", "Colony", 3600, 0.1, 3.000),
    ("Ant Tandem", "Colony", 4.0, 1e-4, 3.000),
    ("Ant Activity", "Colony", 1680, 0.05, 2.500),
    ("Army Raid", "Colony", 3.02e6, 1e6, 1.333),
    ("Brood Wave", "Colony", 3.46e6, 1e5, 19.000),
    ("Work Week", "Colony", 6.05e5, 5e8, 2.500),
    ("Annual Cycle", "Colony", 3.15e7, 1e10, 12.000),
    ("Ant Task Alloc", "Colony", 259200, 1, 43.200),
]

# ============================================================
# COMPUTE 3D COORDINATES
# ============================================================
names = []
systems = []
logT = []
logARA = []
logAction = []

for name, sys, T, E, ara in data:
    action_pi = (T * E) / PI
    names.append(name)
    systems.append(sys)
    logT.append(np.log10(T))
    logARA.append(np.log10(max(ara, 1e-25)))
    logAction.append(np.log10(max(action_pi, 1e-50)))

logT = np.array(logT)
logARA = np.array(logARA)
logAction = np.array(logAction)

N = len(logT)
print(f"Total data points: {N}")
print(f"logT range: [{logT.min():.1f}, {logT.max():.1f}]")
print(f"logARA range: [{logARA.min():.1f}, {logARA.max():.1f}]")
print(f"logAction range: [{logAction.min():.1f}, {logAction.max():.1f}]")

# ============================================================
# 1. PCA — Does the data live in a lower-dimensional subspace?
# ============================================================
print("\n" + "="*70)
print("1. PRINCIPAL COMPONENT ANALYSIS")
print("="*70)

X = np.column_stack([logT, logARA, logAction])
X_centered = X - X.mean(axis=0)

pca = PCA(n_components=3)
pca.fit(X_centered)

print(f"\nVariance explained by each PC:")
for i, (var, ratio) in enumerate(zip(pca.explained_variance_, pca.explained_variance_ratio_)):
    print(f"  PC{i+1}: variance = {var:.2f}, ratio = {ratio:.4f} ({ratio*100:.1f}%)")

print(f"\nCumulative variance: PC1 = {pca.explained_variance_ratio_[0]*100:.1f}%, "
      f"PC1+PC2 = {sum(pca.explained_variance_ratio_[:2])*100:.1f}%")

print(f"\nPrincipal component directions:")
for i, comp in enumerate(pca.components_):
    print(f"  PC{i+1}: logT={comp[0]:.4f}, logARA={comp[1]:.4f}, logAction={comp[2]:.4f}")

# Project onto PCs
projections = pca.transform(X_centered)
pc1 = projections[:, 0]
pc2 = projections[:, 1]
pc3 = projections[:, 2]

# How close to 1D?
residual_from_1d = np.sqrt(pc2**2 + pc3**2)
print(f"\nResidual distance from PC1 line:")
print(f"  Mean: {residual_from_1d.mean():.2f}")
print(f"  Median: {np.median(residual_from_1d):.2f}")
print(f"  Max: {residual_from_1d.max():.2f} ({names[np.argmax(residual_from_1d)]})")

# Identify outliers (>2σ from the line)
sigma = residual_from_1d.std()
outlier_mask = residual_from_1d > 2 * sigma
print(f"\n  Points >2σ from PC1 line ({np.sum(outlier_mask)}/{N}):")
for i in np.where(outlier_mask)[0]:
    print(f"    {names[i]} ({systems[i]}): distance = {residual_from_1d[i]:.2f}")

# ============================================================
# 2. LINEAR RELATIONSHIPS — logAction vs logT
# ============================================================
print("\n" + "="*70)
print("2. LINEAR FIT: logAction = a·logT + b")
print("="*70)

coeffs_AT = np.polyfit(logT, logAction, 1)
a_AT, b_AT = coeffs_AT
pred_AT = np.polyval(coeffs_AT, logT)
residuals_AT = logAction - pred_AT
r2_AT = 1 - np.sum(residuals_AT**2) / np.sum((logAction - logAction.mean())**2)

print(f"\n  logAction = {a_AT:.4f} · logT + {b_AT:.4f}")
print(f"  R² = {r2_AT:.6f}")
print(f"  Slope a = {a_AT:.4f}")
print(f"  Is slope ≈ 1? (would mean Action/π ∝ T): diff = {abs(a_AT - 1):.4f}")
print(f"  Is slope ≈ φ? diff = {abs(a_AT - PHI):.4f}")
print(f"  Is slope ≈ 2? diff = {abs(a_AT - 2):.4f}")

# ============================================================
# 3. CHECK: logAction = logT + logE/π ... what does logE correlate with?
# ============================================================
print("\n" + "="*70)
print("3. ENERGY-PERIOD RELATIONSHIP")
print("="*70)

logE = logAction + np.log10(PI) - logT  # recover logE from Action/π
coeffs_ET = np.polyfit(logT, logE, 1)
a_ET, b_ET = coeffs_ET
pred_ET = np.polyval(coeffs_ET, logT)
residuals_ET = logE - pred_ET
r2_ET = 1 - np.sum(residuals_ET**2) / np.sum((logE - logE.mean())**2)

print(f"\n  logE = {a_ET:.4f} · logT + {b_ET:.4f}")
print(f"  R² = {r2_ET:.6f}")
print(f"  This means E ∝ T^{a_ET:.3f}")
print(f"  If slope = 1: E ∝ T (energy scales linearly with period)")
print(f"  If slope = 0: E = const (energy independent of period)")

# ============================================================
# 4. THE CURVE: Parametric fit in 3D
# ============================================================
print("\n" + "="*70)
print("4. PARAMETRIC CURVE FIT")
print("="*70)

# Sort by PC1 (the main axis of variation) and fit PC2, PC3 as functions of PC1
sort_idx = np.argsort(pc1)
pc1_sorted = pc1[sort_idx]
pc2_sorted = pc2[sort_idx]
pc3_sorted = pc3[sort_idx]
names_sorted = [names[i] for i in sort_idx]

# Polynomial fit of PC2 as function of PC1
for deg in [1, 2, 3, 4]:
    coeffs = np.polyfit(pc1_sorted, pc2_sorted, deg)
    pred = np.polyval(coeffs, pc1_sorted)
    resid = pc2_sorted - pred
    r2 = 1 - np.sum(resid**2) / np.sum((pc2_sorted - pc2_sorted.mean())**2)
    print(f"  PC2 = f(PC1), degree {deg}: R² = {r2:.4f}")

# Best polynomial
best_deg = 3
coeffs_pc2 = np.polyfit(pc1_sorted, pc2_sorted, best_deg)
print(f"\n  Best fit (degree {best_deg}): PC2 = ", end="")
terms = []
for i, c in enumerate(coeffs_pc2):
    power = best_deg - i
    if power > 0:
        terms.append(f"{c:.6f}·PC1^{power}")
    else:
        terms.append(f"{c:.6f}")
print(" + ".join(terms))

# PC3 as function of PC1
for deg in [1, 2, 3]:
    coeffs = np.polyfit(pc1_sorted, pc3_sorted, deg)
    pred = np.polyval(coeffs, pc1_sorted)
    resid = pc3_sorted - pred
    r2 = 1 - np.sum(resid**2) / np.sum((pc3_sorted - pc3_sorted.mean())**2)
    print(f"  PC3 = f(PC1), degree {deg}: R² = {r2:.4f}")

# ============================================================
# 5. DIRECT RELATIONSHIPS — ARA vs Period
# ============================================================
print("\n" + "="*70)
print("5. ARA vs PERIOD RELATIONSHIP")
print("="*70)

# Filter to non-extreme ARA values (the bulk of data between 0.01 and 50)
mask_bulk = (logARA > -2) & (logARA < 2)
bulk_logT = logT[mask_bulk]
bulk_logARA = logARA[mask_bulk]
n_bulk = np.sum(mask_bulk)

print(f"  Bulk data (ARA 0.01-100): {n_bulk}/{N} points")

coeffs_bulk = np.polyfit(bulk_logT, bulk_logARA, 1)
pred_bulk = np.polyval(coeffs_bulk, bulk_logT)
r2_bulk = 1 - np.sum((bulk_logARA - pred_bulk)**2) / np.sum((bulk_logARA - bulk_logARA.mean())**2)

print(f"  logARA = {coeffs_bulk[0]:.6f} · logT + {coeffs_bulk[1]:.4f}")
print(f"  R² = {r2_bulk:.6f}")
print(f"  Slope ≈ 0 means ARA is independent of period (scale-invariant)")
print(f"  If true: ARA is purely about SHAPE, not SCALE")

# ============================================================
# 6. THE SPINE: logAction vs logT regression for on-curve points
# ============================================================
print("\n" + "="*70)
print("6. THE SPINE — Main diagonal of temporal space")
print("="*70)

# The main relationship is Action/π = T × E / π
# If E scales as a power of T across nature, then logAction = (1+α)·logT + const
# The CURVE we see is this power law plus the ARA variation around it

# Fit the spine more carefully, excluding extreme outliers
mask_spine = residual_from_1d < 2 * sigma
spine_logT = logT[mask_spine]
spine_logAction = logAction[mask_spine]
spine_logARA = logARA[mask_spine]

coeffs_spine = np.polyfit(spine_logT, spine_logAction, 1)
a_spine, b_spine = coeffs_spine
r2_spine = 1 - np.sum((spine_logAction - np.polyval(coeffs_spine, spine_logT))**2) / \
           np.sum((spine_logAction - spine_logAction.mean())**2)

print(f"  On-spine points: {np.sum(mask_spine)}/{N}")
print(f"  logAction = {a_spine:.4f} · logT + {b_spine:.4f}")
print(f"  R² = {r2_spine:.6f}")
print(f"\n  Slope interpretation:")
print(f"    slope = {a_spine:.4f}")
print(f"    E ∝ T^({a_spine:.4f} - 1) = T^{a_spine - 1:.4f}")
print(f"    |slope - 1| = {abs(a_spine - 1):.4f}  (Action ∝ T¹?)")
print(f"    |slope - φ| = {abs(a_spine - PHI):.4f}  (Action ∝ T^φ?)")
print(f"    |slope - 2| = {abs(a_spine - 2):.4f}  (Action ∝ T²?)")
print(f"    |slope - π/2| = {abs(a_spine - PI/2):.4f}  (Action ∝ T^(π/2)?)")

# ============================================================
# 7. CURVATURE TEST — Is the curve straight or bent?
# ============================================================
print("\n" + "="*70)
print("7. CURVATURE — Is the 3D path straight or curved?")
print("="*70)

# If it's perfectly linear, PC2 and PC3 would be constant along PC1
# Test if there's systematic curvature

# Split into quintiles along PC1 and check PC2 mean
n_bins = 5
bin_edges = np.percentile(pc1, np.linspace(0, 100, n_bins + 1))
print(f"\n  PC2 by quintile along PC1 (curvature = systematic trend):")
for i in range(n_bins):
    mask = (pc1 >= bin_edges[i]) & (pc1 < bin_edges[i+1] + 0.001)
    if np.any(mask):
        print(f"    Q{i+1} (PC1 [{bin_edges[i]:.1f}, {bin_edges[i+1]:.1f}]): "
              f"mean PC2 = {pc2[mask].mean():+.2f}, std = {pc2[mask].std():.2f}, "
              f"n = {np.sum(mask)}")

# Quadratic fit test
coeffs_q = np.polyfit(pc1, pc2, 2)
pred_q = np.polyval(coeffs_q, pc1)
r2_q = 1 - np.sum((pc2 - pred_q)**2) / np.sum((pc2 - pc2.mean())**2)
print(f"\n  Quadratic fit PC2 = a·PC1² + b·PC1 + c:")
print(f"    a = {coeffs_q[0]:.6f}, b = {coeffs_q[1]:.6f}, c = {coeffs_q[2]:.6f}")
print(f"    R² = {r2_q:.4f}")
if abs(coeffs_q[0]) > 0.001:
    print(f"    → Significant curvature detected (a ≠ 0)")
    print(f"    → The curve BENDS through 3D temporal space")
else:
    print(f"    → Approximately linear (no significant curvature)")

# ============================================================
# 8. φ AND π IN THE STRUCTURE
# ============================================================
print("\n" + "="*70)
print("8. TESTING FOR φ AND π IN THE CURVE")
print("="*70)

# Test if PCA direction ratios involve φ or π
pc1_dir = pca.components_[0]
ratios = [
    ("PC1[logAction]/PC1[logT]", pc1_dir[2] / pc1_dir[0] if pc1_dir[0] != 0 else float('inf')),
    ("PC1[logARA]/PC1[logT]", pc1_dir[1] / pc1_dir[0] if pc1_dir[0] != 0 else float('inf')),
    ("PC1[logAction]/PC1[logARA]", pc1_dir[2] / pc1_dir[1] if pc1_dir[1] != 0 else float('inf')),
]

print(f"\n  PC1 direction ratios:")
for label, ratio in ratios:
    print(f"    {label} = {ratio:.4f}")
    print(f"      |ratio - φ| = {abs(ratio - PHI):.4f}")
    print(f"      |ratio - π| = {abs(ratio - PI):.4f}")
    print(f"      |ratio - 1| = {abs(ratio - 1):.4f}")
    print(f"      |ratio - 2| = {abs(ratio - 2):.4f}")
    print(f"      |ratio - 1/φ| = {abs(ratio - 1/PHI):.4f}")

# Test slope of spine against φ-related values
print(f"\n  Spine slope tests:")
slope = a_spine
candidates = [
    ("1", 1), ("φ", PHI), ("1/φ", 1/PHI), ("2", 2), ("π/2", PI/2),
    ("√2", np.sqrt(2)), ("√φ", np.sqrt(PHI)), ("φ²", PHI**2),
    ("e", np.e), ("π", PI), ("2φ", 2*PHI), ("φ+1", PHI+1),
    ("π/φ", PI/PHI), ("2π/φ²", 2*PI/PHI**2),
]
for name_c, val in candidates:
    diff = abs(slope - val)
    print(f"    |slope - {name_c}| = {diff:.4f}  ({name_c} = {val:.4f})")

# ============================================================
# 9. DIMENSIONALITY SUMMARY
# ============================================================
print("\n" + "="*70)
print("9. SUMMARY — THE SHAPE OF TEMPORAL SPACE")
print("="*70)

print(f"""
  Total points: {N}
  Dimensions: 3 (logT, logARA, logAction/π)

  PC1 captures {pca.explained_variance_ratio_[0]*100:.1f}% of variance
  PC1+PC2 captures {sum(pca.explained_variance_ratio_[:2])*100:.1f}% of variance

  → The data is {"STRONGLY 1D" if pca.explained_variance_ratio_[0] > 0.8 else
     "effectively 2D" if sum(pca.explained_variance_ratio_[:2]) > 0.95 else
     "genuinely 3D"}

  Spine equation: logAction = {a_spine:.3f} · logT + {b_spine:.3f}  (R² = {r2_spine:.4f})
  → Energy scales as T^{a_spine-1:.3f} across nature

  ARA is {"scale-INVARIANT" if abs(coeffs_bulk[0]) < 0.05 else "weakly scale-dependent"}
  → logARA vs logT slope = {coeffs_bulk[0]:.4f}  (R² = {r2_bulk:.4f})

  The curve {"bends" if r2_q > 0.05 else "is straight"} (curvature R² = {r2_q:.4f})

  PC1 direction: ({pc1_dir[0]:.3f}, {pc1_dir[1]:.3f}, {pc1_dir[2]:.3f})
    logAction/logT ratio = {pc1_dir[2]/pc1_dir[0]:.4f}
""")

# ============================================================
# 10. EXPORT DATA FOR 3D OVERLAY
# ============================================================
print("="*70)
print("10. EXPORTING CURVE DATA FOR VISUALIZATION")
print("="*70)

# Generate the fitted spine curve
t_range = np.linspace(logT.min(), logT.max(), 200)
action_fitted = np.polyval(coeffs_spine, t_range)

# For ARA: use mean or the weak relationship
if abs(coeffs_bulk[0]) < 0.1:
    ara_fitted = np.full_like(t_range, bulk_logARA.mean())
    print(f"  ARA approximately constant along spine: logARA ≈ {bulk_logARA.mean():.3f} (ARA ≈ {10**bulk_logARA.mean():.3f})")
else:
    ara_fitted = np.polyval(coeffs_bulk, t_range)
    print(f"  ARA varies along spine with slope {coeffs_bulk[0]:.4f}")

# Export as JSON for the 3D viz
curve_data = {
    "spine": {
        "logT": t_range.tolist(),
        "logARA": ara_fitted.tolist(),
        "logAction": action_fitted.tolist()
    },
    "fit_params": {
        "action_slope": float(a_spine),
        "action_intercept": float(b_spine),
        "action_r2": float(r2_spine),
        "ara_slope": float(coeffs_bulk[0]),
        "ara_intercept": float(coeffs_bulk[1]),
        "ara_r2": float(r2_bulk),
        "pc1_variance_ratio": float(pca.explained_variance_ratio_[0]),
        "pc1_direction": pca.components_[0].tolist(),
    },
    "points": []
}

for i in range(N):
    curve_data["points"].append({
        "name": names[i],
        "system": systems[i],
        "logT": float(logT[i]),
        "logARA": float(logARA[i]),
        "logAction": float(logAction[i]),
        "pc1": float(pc1[i]),
        "pc2": float(pc2[i]),
        "pc3": float(pc3[i]),
        "distance_from_spine": float(residual_from_1d[i])
    })

with open("/sessions/focused-tender-thompson/mnt/SystemFormulaFolder/computations/38_curve_data.json", "w") as f:
    json.dump(curve_data, f, indent=2)

print(f"  Curve data exported to 38_curve_data.json")
print(f"\n  DONE.")
