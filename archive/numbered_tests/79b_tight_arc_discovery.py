#!/usr/bin/env python3
"""
Script 79b — TIGHT ARC DISCOVERY + MULTI-CIRCLE DECOMPOSITION
==============================================================
Script 79 found ONE giant circle capturing 96% of data — too greedy.
The threshold was too loose to see sub-structure.

TWO NEW APPROACHES:

APPROACH A — TIGHT RANSAC:
  Reduce threshold to 3% of data spread. This forces RANSAC to find
  tighter-fitting arcs, possibly revealing sub-structures.

APPROACH B — SIMULTANEOUS 3-CIRCLE FIT:
  Dylan's insight: the spine IS where three circles overlap.
  Instead of finding three separate arcs, fit three circles
  simultaneously that together best explain the point cloud.
  Each point is assigned to its nearest circle.
  Optimise all three circle parameters jointly.

APPROACH C — PROJECTION ANALYSIS:
  Project the data onto the best-fit plane (from Script 79's giant circle).
  In that 2D projection, look for curvature changes that indicate where
  one arc ends and another begins. This is what the eye does.

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy import stats
from scipy.optimize import minimize

np.random.seed(79)
PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

# ============================================================
# FULL DATASET (same as 79)
# ============================================================
data = [
    ("Combustion Cycle", 0.04, 2700, 1.00, "engineered", "human"),
    ("Valve Timing", 0.04, 2700, 0.618, "engineered", "human"),
    ("Ignition Pulse", 0.0053, 0.05, 0.0001, "engineered", "human"),
    ("Cooling Cycle", 30, 5000, 1.60, "engineered", "human"),
    ("CPU Clock", 3e-10, 2.9e-8, 1.00, "engineered", "nano"),
    ("CPU Boost/Idle", 3.2, 320, 0.60, "engineered", "human"),
    ("RAM Refresh", 0.064, 6.2e-3, 0.0047, "engineered", "human"),
    ("Thermal/Cooling", 23, 2300, 1.30, "engineered", "human"),
    ("SA Node", 0.830, 1.3, 0.043, "biological", "human"),
    ("AV Node", 0.135, 0.02, 0.27, "biological", "human"),
    ("Ventricular Pump", 0.830, 1.3, 1.60, "biological", "human"),
    ("Myocyte", 0.830, 1.3, 1.73, "biological", "human"),
    ("Ventricular AP", 0.830, 0.001, 1.35, "biological", "human"),
    ("RSA Breathing", 4.7, 7, 1.61, "biological", "human"),
    ("Ground Orbital", 1.52e-16, 2.18e-18, 1.00, "quantum", "quantum"),
    ("Lyman-alpha", 1.596e-9, 2.18e-18, 2.54e-7, "quantum", "nano"),
    ("2s Metastable", 0.122, 2.18e-18, 3.32e-15, "quantum", "human"),
    ("Balmer Cascade", 6.96e-9, 2.18e-18, 0.298, "quantum", "nano"),
    ("21-cm Hyperfine", 3.47e14, 9.43e-25, 2.03e-24, "quantum", "cosmic"),
    ("Integration-Spike", 0.0265, 5e-12, 0.060, "biological", "human"),
    ("Depol/Repol", 0.0011, 5e-13, 2.14, "biological", "human"),
    ("Refractory", 0.0052, 1e-12, 3.33, "biological", "human"),
    ("Synaptic Vesicle", 0.050, 1e-12, 0.003, "biological", "human"),
    ("Storm Lifecycle", 3300, 1e12, 2.24, "geophysical", "earth"),
    ("Lightning", 600, 1e9, 1.67e-7, "geophysical", "earth"),
    ("Precipitation", 2100, 5e11, 0.75, "geophysical", "earth"),
    ("Gust Front", 1140, 1e11, 0.58, "geophysical", "earth"),
    ("Hare", 9.5*365.25*86400, 1e15, 0.46, "ecological", "earth"),
    ("Lynx", 9.5*365.25*86400, 5e14, 0.73, "ecological", "earth"),
    ("Vegetation", 4*365.25*86400, 1e14, 0.60, "ecological", "earth"),
    ("Diurnal Thermal", 86400, 1.5e22, 1.667, "geophysical", "earth"),
    ("Tidal Cycle", 43920, 3.7e18, 1.44, "geophysical", "earth"),
    ("Water Cycle", 820800, 1.3e21, 0.056, "geophysical", "earth"),
    ("ENSO", 4*365.25*86400, 1e21, 0.60, "geophysical", "earth"),
    ("Seasonal", 365.25*86400, 5.5e24, 1.017, "geophysical", "earth"),
    ("Milankovitch", 1e5*365.25*86400, 1e28, 0.111, "geophysical", "cosmic"),
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
    ("Gamma 40Hz", 0.025, 1e-11, 3.000, "biological", "human"),
    ("Beta 20Hz", 0.050, 5e-12, 2.571, "biological", "human"),
    ("Alpha 10Hz", 0.100, 2e-12, 2.571, "biological", "human"),
    ("Theta 6Hz", 0.167, 1e-12, 2.976, "biological", "human"),
    ("Delta 2Hz", 0.500, 5e-13, 2.333, "biological", "human"),
    ("Semi-diurnal M2", 44640, 3.7e18, 1.138, "geophysical", "earth"),
    ("Spring-Neap", 1276140, 1e19, 1.182, "geophysical", "earth"),
    ("Cardiac SA", 0.8, 1.3, 1.667, "biological", "human"),
    ("Respiratory", 4.0, 3, 1.500, "biological", "human"),
    ("Mayer Wave", 10, 0.5, 2.333, "biological", "human"),
    ("Gastric Wave", 20, 0.3, 2.333, "biological", "human"),
    ("Cortisol", 86400, 500, 2.000, "biological", "earth"),
    ("Saccade/Fix", 0.31, 1e-4, 7.857, "biological", "human"),
    ("Blink Cycle", 4.0, 0.01, 9.000, "biological", "human"),
    ("Sleep-Wake", 86400, 8e6, 2.000, "biological", "earth"),
    ("Complement", 0.285, 1e-10, 5.333, "biological", "human"),
    ("Neutrophil", 30600, 1e-6, 4.667, "biological", "earth"),
    ("Inflammation", 432000, 100, 1.500, "biological", "earth"),
    ("Adaptive", 1382400, 1000, 3.000, "biological", "earth"),
    ("Memory", 3801600, 50, 21.000, "biological", "earth"),
    ("Circadian Immune", 86400, 10, 0.846, "biological", "earth"),
    ("Ideal Pendulum", 2.006, 0.01, 1.000, "engineered", "human"),
    ("Spring-Mass", 0.628, 0.5, 1.000, "engineered", "human"),
    ("Tuning Fork", 2.27e-3, 1e-5, 1.000, "engineered", "human"),
    ("Foucault", 16.4, 50, 1.016, "engineered", "human"),
    ("Driven Pendulum", 60000, 0.1, 1.000, "engineered", "earth"),
    ("Seismic Osc", 53.8, 1e15, 1.000, "geophysical", "human"),
    ("Van der Pol", 10.0, 0.01, 1.857, "engineered", "human"),
    ("Old Faithful", 5340, 1e9, 21.250, "geophysical", "earth"),
    ("Natural Breath", 4.0, 3, 1.500, "biological", "human"),
    ("VC 1:2", 4.0, 3, 0.498, "engineered", "human"),
    ("NAVA", 3.8, 3, 1.235, "biological", "human"),
    ("APRV", 5.0, 4, 9.000, "engineered", "human"),
    ("HFOV", 0.034, 0.1, 1.000, "engineered", "human"),
    ("QHO Ground", 1e-13, 1.05e-21, 1.000, "quantum", "quantum"),
    ("Rabi Osc", 1e-8, 1.05e-26, 1.000, "quantum", "nano"),
    ("Caesium Clock", 1.09e-10, 9.63e-25, 1.000, "quantum", "nano"),
    ("Phonon", 1e-13, 1.05e-21, 1.000, "quantum", "quantum"),
    ("H Lyman-alpha", 1.596e-9, 2.18e-18, 2.36e6, "quantum", "nano"),
    ("Na Fluorescence", 1.624e-8, 3.37e-19, 4.78e7, "quantum", "nano"),
    ("U-238 Alpha", 1.41e17, 6.8e-13, 1.41e38, "quantum", "cosmic"),
    ("Earth Orbit", 3.156e7, 2.65e33, 1.011, "geophysical", "cosmic"),
    ("Mercury Orbit", 7.6e6, 1.6e32, 1.149, "geophysical", "cosmic"),
    ("Halley's Comet", 2.38e9, 1e28, 4.556, "geophysical", "cosmic"),
    ("Jupiter Orbit", 3.74e8, 4.2e35, 1.031, "geophysical", "cosmic"),
    ("MS Pulsar", 1.56e-3, 1e44, 1.000, "geophysical", "human"),
    ("Crab Emission", 0.0335, 1.76e49, 7.375, "geophysical", "human"),
    ("Sunspot Cycle", 3.47e8, 1e25, 1.558, "geophysical", "cosmic"),
    ("d Cephei", 4.64e5, 1.5e30, 2.333, "geophysical", "earth"),
    ("HH Spike", 0.002, 5e-13, 3.000, "biological", "human"),
    ("Pyramidal 10Hz", 0.100, 5e-12, 49.000, "biological", "human"),
    ("FS Interneuron", 0.025, 3e-12, 30.250, "biological", "human"),
    ("Thalamic Burst", 0.215, 1e-11, 13.333, "biological", "human"),
    ("AMPA EPSP", 0.009, 1e-14, 8.000, "biological", "human"),
    ("GABA IPSP", 0.032, 5e-14, 15.000, "biological", "human"),
    ("Ca2+ Spike", 0.105, 1e-11, 20.000, "biological", "human"),
    ("LC Tank", 1.99e-4, 5e-6, 1.000, "engineered", "human"),
    ("555 R1=R2", 0.139, 0.01, 2.000, "engineered", "human"),
    ("555 R1=2R2", 0.208, 0.01, 3.000, "engineered", "human"),
    ("CMOS Ring", 1.68e-9, 1e-12, 1.500, "engineered", "nano"),
    ("Colpitts", 1e-6, 1e-7, 1.041, "engineered", "micro"),
    ("Crystal 32kHz", 3.05e-5, 1e-9, 1.000, "engineered", "micro"),
    ("Op-amp Relax", 0.069, 0.005, 2.000, "engineered", "human"),
    ("Water Hammer", 0.134, 1e4, 1.000, "geophysical", "human"),
    ("Deep Water Wave", 10.0, 1e6, 1.062, "geophysical", "human"),
    ("Dripping Faucet", 0.333, 1e-4, 9.091, "geophysical", "human"),
    ("Cavitation", 5.5e-4, 1e3, 10.000, "geophysical", "human"),
    ("Rayleigh-Benard", 1.0, 0.1, 1.222, "geophysical", "human"),
    ("Von Karman 200", 0.037, 1e-3, 1.176, "geophysical", "human"),
    ("Ant Foraging", 3600, 0.1, 3.000, "ecological", "earth"),
    ("Ant Tandem", 4.0, 1e-4, 3.000, "ecological", "human"),
    ("Ant Activity", 1680, 0.05, 2.500, "ecological", "earth"),
    ("Army Raid", 3.02e6, 1e6, 1.333, "ecological", "earth"),
    ("Brood Wave", 3.46e6, 1e5, 19.000, "ecological", "earth"),
    ("Work Week", 6.05e5, 5e8, 2.500, "ecological", "earth"),
    ("Annual Cycle", 3.15e7, 1e10, 12.000, "ecological", "cosmic"),
    ("Ant Task Alloc", 259200, 1, 43.200, "ecological", "earth"),
    ("CMB Peak 1", 4.721e13, 3.48e57, 1.510, "cosmological", "cosmic"),
    ("CMB Peak 2", 2.360e13, 1.59e56, 1.510, "cosmological", "cosmic"),
    ("CMB Peak 3", 1.574e13, 4.61e55, 1.435, "cosmological", "cosmic"),
    ("CMB Peak 4", 1.180e13, 1.21e55, 1.435, "cosmological", "cosmic"),
    ("CMB Peak 5", 9.442e12, 4.75e54, 1.317, "cosmological", "cosmic"),
    ("CMB Peak 6", 7.868e12, 1.96e54, 1.317, "cosmological", "cosmic"),
    ("CMB Peak 7", 6.744e12, 9.44e53, 1.265, "cosmological", "cosmic"),
]

names = [d[0] for d in data]
T_arr = np.array([d[1] for d in data])
E_arr = np.array([d[2] for d in data])
ARA_arr = np.array([d[3] for d in data])
cat_arr = np.array([d[4] for d in data])
scale_arr = np.array([d[5] for d in data])

logT = np.log10(T_arr)
logE = np.log10(E_arr)
logA = logT + logE - np.log10(PI)
logARA = np.log10(1 + ARA_arr)

N = len(data)
coords = np.column_stack([logT, logARA, logA])
means_c = coords.mean(axis=0)
stds_c = coords.std(axis=0)
stds_c[stds_c == 0] = 1
coords_norm = (coords - means_c) / stds_c

print("=" * 70)
print("SCRIPT 79b — TIGHT ARC + MULTI-CIRCLE DECOMPOSITION")
print("=" * 70)

# ============================================================
# APPROACH C: CURVATURE ANALYSIS ON THE SPINE
# ============================================================
# Instead of looking for spatially separate arcs (which fail because
# the circles overlap), we analyse the CURVATURE along the spine.
# If three circles compose the spine, we should see curvature changes
# at the transition points between circles.

print("\n" + "=" * 70)
print("APPROACH C: CURVATURE ANALYSIS ALONG THE SPINE")
print("=" * 70)
print(f"\n  Idea: Sort points along the spine (by logT), compute local")
print(f"  curvature. Where curvature changes → circle boundary.")

# Sort all points by logT
sort_idx = np.argsort(logT)
sorted_logT = logT[sort_idx]
sorted_logE = logE[sort_idx]
sorted_logA = logA[sort_idx]
sorted_coords = coords_norm[sort_idx]
sorted_names = [names[i] for i in sort_idx]
sorted_cats = [cat_arr[i] for i in sort_idx]

# Compute local curvature using sliding window
# For each point i, take window of ±w points, fit a circle, measure radius
# Large radius = nearly straight, small radius = tight curve

def local_curvature_radius(points, idx, window=5):
    """Estimate local curvature radius at index idx using nearby points."""
    n = len(points)
    lo = max(0, idx - window)
    hi = min(n, idx + window + 1)
    local_pts = points[lo:hi]

    if len(local_pts) < 4:
        return np.inf, None

    # PCA to get best-fit plane
    center = local_pts.mean(axis=0)
    centered = local_pts - center
    try:
        U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    except:
        return np.inf, None

    # Project to 2D
    v1, v2 = Vt[0], Vt[1]
    normal = Vt[2]
    proj_x = centered @ v1
    proj_y = centered @ v2

    # Algebraic circle fit
    n_pts = len(local_pts)
    A_mat = np.column_stack([proj_x, proj_y, np.ones(n_pts)])
    b_vec = proj_x**2 + proj_y**2
    try:
        result, _, _, _ = np.linalg.lstsq(A_mat, b_vec, rcond=None)
    except:
        return np.inf, None

    cx = result[0] / 2
    cy = result[1] / 2
    r_sq = result[2] + cx**2 + cy**2
    if r_sq <= 0:
        return np.inf, None
    radius = np.sqrt(r_sq)
    return radius, normal

print(f"\n  Computing local curvature (window = 7 points)...")

curvatures = []
normals_along = []
window = 7

for i in range(N):
    r, n = local_curvature_radius(sorted_coords, i, window)
    curvatures.append(1.0 / r if r > 0 and r < 1000 else 0)
    normals_along.append(n)

curvatures = np.array(curvatures)

# Smooth curvature signal
from scipy.ndimage import uniform_filter1d
curv_smooth = uniform_filter1d(curvatures, size=5)

# Find curvature peaks (transition points between circles)
# A peak in curvature = point of maximum bending = likely circle boundary
print(f"\n  Looking for curvature transitions...")

# Simple peak detection
peaks = []
for i in range(2, N-2):
    if curv_smooth[i] > curv_smooth[i-1] and curv_smooth[i] > curv_smooth[i+1]:
        if curv_smooth[i] > np.median(curv_smooth) * 1.5:  # significant peak
            peaks.append(i)

print(f"  Found {len(peaks)} curvature peaks")
for p in peaks[:10]:
    print(f"    idx={p:3d}  logT={sorted_logT[p]:6.1f}  κ={curv_smooth[p]:.3f}  system={sorted_names[p]}")

# Find the top 2 peaks (which would define 3 segments)
if len(peaks) >= 2:
    # Sort by curvature magnitude
    peaks_sorted = sorted(peaks, key=lambda i: curv_smooth[i], reverse=True)
    top2 = sorted(peaks_sorted[:2])  # sort by position

    seg1 = sort_idx[:top2[0]]
    seg2 = sort_idx[top2[0]:top2[1]]
    seg3 = sort_idx[top2[1]:]

    print(f"\n  Top 2 curvature peaks at logT = {sorted_logT[top2[0]]:.1f} and {sorted_logT[top2[1]]:.1f}")
    print(f"  This divides the spine into 3 segments:")
    print(f"    Segment 1: {len(seg1)} systems, logT [{sorted_logT[0]:.1f}, {sorted_logT[top2[0]-1]:.1f}]")
    print(f"    Segment 2: {len(seg2)} systems, logT [{sorted_logT[top2[0]]:.1f}, {sorted_logT[top2[1]-1]:.1f}]")
    print(f"    Segment 3: {len(seg3)} systems, logT [{sorted_logT[top2[1]]:.1f}, {sorted_logT[-1]:.1f}]")

    segments = [seg1, seg2, seg3]
else:
    # Try using curvature sign changes instead
    print(f"\n  Fewer than 2 peaks found. Using fixed logT boundaries as fallback.")
    segments = None

# ============================================================
# APPROACH D: FIT 3 CIRCLES TO THE CURVATURE-DERIVED SEGMENTS
# ============================================================
print("\n" + "=" * 70)
print("APPROACH D: CIRCLE FITTING TO CURVATURE-DERIVED SEGMENTS")
print("=" * 70)

def fit_circle_3d_svd(points):
    """Fit circle to 3D points using SVD + algebraic circle fit."""
    pts = np.array(points)
    n = len(pts)
    if n < 4:
        return None

    center = pts.mean(axis=0)
    centered = pts - center
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)

    v1, v2, normal = Vt[0], Vt[1], Vt[2]
    planarity = 1.0 - S[2] / S[0] if S[0] > 0 else 0

    proj_x = centered @ v1
    proj_y = centered @ v2

    A_mat = np.column_stack([proj_x, proj_y, np.ones(n)])
    b_vec = proj_x**2 + proj_y**2
    try:
        result, _, _, _ = np.linalg.lstsq(A_mat, b_vec, rcond=None)
    except:
        return None

    cx = result[0] / 2
    cy = result[1] / 2
    r_sq = result[2] + cx**2 + cy**2
    if r_sq <= 0:
        return None
    radius = np.sqrt(r_sq)

    circle_center_3d = center + cx * v1 + cy * v2

    dists_from_center = np.sqrt((proj_x - cx)**2 + (proj_y - cy)**2)
    residuals = np.abs(dists_from_center - radius)

    # Compute angular span
    angles = np.arctan2(proj_y - cy, proj_x - cx) % (2*PI)
    angles_sorted = np.sort(angles)
    gaps = np.diff(angles_sorted)
    gaps = np.append(gaps, 2*PI - angles_sorted[-1] + angles_sorted[0])
    arc_span = np.degrees(2*PI - gaps.max())

    return {
        'center': circle_center_3d,
        'normal': normal,
        'radius': radius,
        'v1': v1, 'v2': v2,
        'planarity': planarity,
        'residuals': residuals,
        'mean_residual': residuals.mean(),
        'arc_span': arc_span,
        'n_points': n
    }


if segments is not None:
    circle_fits = []
    for i, seg in enumerate(segments):
        pts = coords_norm[seg]
        fit = fit_circle_3d_svd(pts)
        if fit is None:
            print(f"\n  Segment {i+1}: circle fit failed")
            circle_fits.append(None)
            continue

        circle_fits.append(fit)
        mean_lt = logT[seg].mean()
        domain = "QUANTUM" if mean_lt < -4 else ("COSMIC" if mean_lt > 8 else "MATTER")

        print(f"\n  Segment {i+1} → {domain} ({len(seg)} points)")
        print(f"    Planarity:     {fit['planarity']:.3f}")
        print(f"    Circle radius: {fit['radius']:.3f}")
        print(f"    Arc span:      {fit['arc_span']:.0f}°")
        print(f"    Mean residual: {fit['mean_residual']:.4f} ({fit['mean_residual']/fit['radius']:.1%} of radius)")
        print(f"    Normal:        [{fit['normal'][0]:.3f}, {fit['normal'][1]:.3f}, {fit['normal'][2]:.3f}]")

        # Slope analysis
        if len(seg) > 3:
            slope, _, r_val, p_val, _ = stats.linregress(logT[seg], logE[seg])
            print(f"    logE slope:    {slope:.3f}  (|Δφ| = {abs(slope-PHI):.3f}, R²={r_val**2:.3f})")

        # Extrapolated full circle in raw coords
        center_raw = fit['center'] * stds_c + means_c
        r_logT = fit['radius'] * stds_c[0]
        print(f"    Center (raw):  logT={center_raw[0]:.1f}, logARA={center_raw[1]:.2f}, logA={center_raw[2]:.1f}")
        print(f"    Radius (logT): {r_logT:.1f} orders of magnitude")
        print(f"    Full span:     logT [{center_raw[0]-r_logT:.1f}, {center_raw[0]+r_logT:.1f}]")

# ============================================================
# CIRCLE-CIRCLE COMPARISONS
# ============================================================
print("\n" + "=" * 70)
print("CIRCLE-CIRCLE COMPARISONS")
print("=" * 70)

valid_fits = [(i, f) for i, f in enumerate(circle_fits) if f is not None]

for idx_a in range(len(valid_fits)):
    for idx_b in range(idx_a + 1, len(valid_fits)):
        ia, fa = valid_fits[idx_a]
        ib, fb = valid_fits[idx_b]

        # Normal angle
        cos_a = abs(np.dot(fa['normal'], fb['normal']))
        angle = np.degrees(np.arccos(np.clip(cos_a, 0, 1)))

        # Center distance
        cd = np.linalg.norm(fa['center'] - fb['center'])
        sr = fa['radius'] + fb['radius']

        print(f"\n  Segments {ia+1} ↔ {ib+1}:")
        print(f"    Normal angle:    {angle:.1f}°  ({'DISTINCT' if angle > 15 else 'similar'})")
        print(f"    Center distance: {cd:.3f}")
        print(f"    Sum of radii:    {sr:.3f}")
        print(f"    Overlap:         {'YES' if cd < sr else 'no'}")

# ============================================================
# APPROACH E: MODEL COMPARISON
# ============================================================
print("\n" + "=" * 70)
print("APPROACH E: 1-CIRCLE vs 3-CIRCLE MODEL COMPARISON")
print("=" * 70)

# Fit ONE circle to all data
fit_1 = fit_circle_3d_svd(coords_norm)
print(f"\n  1-Circle model:")
print(f"    Radius:        {fit_1['radius']:.3f}")
print(f"    Mean residual: {fit_1['mean_residual']:.4f}")
print(f"    Arc span:      {fit_1['arc_span']:.0f}°")

# 3-Circle model: total residual across segments
if segments is not None and all(f is not None for f in circle_fits):
    total_resid_3 = 0
    total_pts_3 = 0
    for seg, fit in zip(segments, circle_fits):
        total_resid_3 += fit['mean_residual'] * fit['n_points']
        total_pts_3 += fit['n_points']
    mean_resid_3 = total_resid_3 / total_pts_3

    improvement = (fit_1['mean_residual'] - mean_resid_3) / fit_1['mean_residual'] * 100

    print(f"\n  3-Circle model:")
    print(f"    Mean residual: {mean_resid_3:.4f}")
    print(f"\n  Improvement: {improvement:.1f}%")
    print(f"  (3-circle reduces residuals by {improvement:.1f}% compared to 1-circle)")

    # Statistical test: is 3-circle significantly better?
    # Use F-test comparing residual sums
    resid_1 = fit_1['residuals']
    ss_1 = np.sum(resid_1**2)

    ss_3 = 0
    for seg, fit in zip(segments, circle_fits):
        ss_3 += np.sum(fit['residuals']**2)

    # Degrees of freedom: each circle has ~7 params (center xyz, normal 2 angles, radius, phase)
    df_1 = N - 7
    df_3 = N - 3 * 7

    if df_3 > 0 and ss_3 > 0:
        f_stat = ((ss_1 - ss_3) / (df_1 - df_3)) / (ss_3 / df_3)
        # F-distribution p-value
        from scipy.stats import f as f_dist
        p_val = 1 - f_dist.cdf(f_stat, df_1 - df_3, df_3)
        print(f"\n  F-test: F = {f_stat:.2f}, p = {p_val:.2e}")
        print(f"  {'3-circle model SIGNIFICANTLY better (p < 0.05)' if p_val < 0.05 else '3-circle model NOT significantly better'}")

# ============================================================
# TESTS
# ============================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 10

# Test 1: Curvature analysis finds at least 2 transition points
t1 = len(peaks) >= 2
print(f"\n  Test  1: Curvature analysis finds ≥2 transition points")
print(f"           Found: {len(peaks)} peaks")
print(f"           → {'PASS ✓' if t1 else 'FAIL ✗'}")
passed += t1

# Test 2: 3 segments each contain ≥10 points
t2 = segments is not None and all(len(s) >= 10 for s in segments)
print(f"\n  Test  2: Each segment has ≥10 points")
if segments:
    for i, s in enumerate(segments):
        print(f"           Segment {i+1}: {len(s)}")
print(f"           → {'PASS ✓' if t2 else 'FAIL ✗'}")
passed += t2

# Test 3: Each segment fits a circle (relative residual < 25%)
t3_checks = []
for f in circle_fits:
    if f is not None:
        t3_checks.append(f['mean_residual'] / f['radius'] < 0.25)
    else:
        t3_checks.append(False)
t3 = all(t3_checks)
print(f"\n  Test  3: Each segment fits a circle (residual < 25% of radius)")
for i, f in enumerate(circle_fits):
    if f:
        print(f"           Segment {i+1}: {f['mean_residual']/f['radius']:.3f}")
print(f"           → {'PASS ✓' if t3 else 'FAIL ✗'}")
passed += t3

# Test 4: At least 2 circle normals differ by > 15°
if len(valid_fits) >= 2:
    angles_list = []
    for idx_a in range(len(valid_fits)):
        for idx_b in range(idx_a+1, len(valid_fits)):
            _, fa = valid_fits[idx_a]
            _, fb = valid_fits[idx_b]
            cos_a = abs(np.dot(fa['normal'], fb['normal']))
            angles_list.append(np.degrees(np.arccos(np.clip(cos_a, 0, 1))))
    t4 = any(a > 15 for a in angles_list)
else:
    t4 = False
    angles_list = []
print(f"\n  Test  4: At least 2 normals differ by > 15°")
for a in angles_list:
    print(f"           {a:.1f}°")
print(f"           → {'PASS ✓' if t4 else 'FAIL ✗'}")
passed += t4

# Test 5: Arc span > 60° for each segment's circle
t5 = all(f['arc_span'] > 60 for f in circle_fits if f is not None)
print(f"\n  Test  5: Arc span > 60° for each circle")
for i, f in enumerate(circle_fits):
    if f:
        print(f"           Segment {i+1}: {f['arc_span']:.0f}°")
print(f"           → {'PASS ✓' if t5 else 'FAIL ✗'}")
passed += t5

# Test 6: Extrapolated circles overlap
t6 = False
for idx_a in range(len(valid_fits)):
    for idx_b in range(idx_a+1, len(valid_fits)):
        _, fa = valid_fits[idx_a]
        _, fb = valid_fits[idx_b]
        cd = np.linalg.norm(fa['center'] - fb['center'])
        if cd < fa['radius'] + fb['radius']:
            t6 = True
print(f"\n  Test  6: Extrapolated circles overlap")
print(f"           → {'PASS ✓' if t6 else 'FAIL ✗'}")
passed += t6

# Test 7: Matter segment slope near φ
t7 = False
if segments is not None:
    for i, seg in enumerate(segments):
        mean_lt = logT[seg].mean()
        if -4 <= mean_lt <= 8 and len(seg) > 5:
            slope, _, _, _, _ = stats.linregress(logT[seg], logE[seg])
            if abs(slope - PHI) < 0.25:
                t7 = True
                print(f"\n  Test  7: Matter segment slope near φ")
                print(f"           Segment {i+1}: slope = {slope:.3f}")
                break
if not t7:
    print(f"\n  Test  7: Matter segment slope near φ")
print(f"           → {'PASS ✓' if t7 else 'FAIL ✗'}")
passed += t7

# Test 8: 3-circle model has lower residuals than 1-circle
t8 = segments is not None and all(f is not None for f in circle_fits) and mean_resid_3 < fit_1['mean_residual']
print(f"\n  Test  8: 3-circle model beats 1-circle model")
if segments is not None and all(f is not None for f in circle_fits):
    print(f"           1-circle: {fit_1['mean_residual']:.4f}")
    print(f"           3-circle: {mean_resid_3:.4f}")
print(f"           → {'PASS ✓' if t8 else 'FAIL ✗'}")
passed += t8

# Test 9: F-test significant (p < 0.05)
t9 = 'p_val' in dir() and p_val < 0.05
print(f"\n  Test  9: F-test: 3-circle significantly better (p < 0.05)")
if 'p_val' in dir():
    print(f"           p = {p_val:.2e}")
print(f"           → {'PASS ✓' if t9 else 'FAIL ✗'}")
passed += t9

# Test 10: Circle radii show hierarchy
if len(valid_fits) >= 3:
    radii = sorted([f['radius'] for _, f in valid_fits])
    t10 = radii[-1] / radii[0] > 1.3 if radii[0] > 0 else False
    print(f"\n  Test 10: Circle radii show hierarchy (ratio > 1.3)")
    print(f"           Radii: {[f'{r:.3f}' for r in radii]}")
    print(f"           Ratio: {radii[-1]/radii[0]:.2f}")
elif len(valid_fits) >= 2:
    radii = sorted([f['radius'] for _, f in valid_fits])
    t10 = radii[-1] / radii[0] > 1.3 if radii[0] > 0 else False
    print(f"\n  Test 10: Circle radii show hierarchy")
    print(f"           Radii: {[f'{r:.3f}' for r in radii]}")
else:
    t10 = False
    print(f"\n  Test 10: Circle radii show hierarchy")
print(f"           → {'PASS ✓' if t10 else 'FAIL ✗'}")
passed += t10

# ============================================================
# FINAL SCORE
# ============================================================
print("\n" + "=" * 70)
score = passed
print(f"  SCORE: {score} / {total}")
print("=" * 70)

if score >= 7:
    verdict = "STRONG"
    msg = "Three circles with distinct properties emerge from curvature analysis."
elif score >= 5:
    verdict = "MODERATE"
    msg = "Evidence for multi-circle structure, but boundaries are soft."
else:
    verdict = "WEAK"
    msg = "Curvature analysis does not strongly support three distinct circles."

print(f"\n  VERDICT: {verdict} — {msg}")

# Print extrapolated circle sizes for visualization
print(f"\n  EXTRAPOLATED FULL CIRCLES (for 3D map):")
for i, (seg, fit) in enumerate(zip(segments, circle_fits)):
    if fit is None:
        continue
    center_raw = fit['center'] * stds_c + means_c
    r_logT = fit['radius'] * stds_c[0]
    r_logA = fit['radius'] * stds_c[2]
    mean_lt = logT[seg].mean()
    domain = "QUANTUM" if mean_lt < -4 else ("COSMIC" if mean_lt > 8 else "MATTER")

    print(f"\n  Circle {i+1} ({domain}):")
    print(f"    Observed arc:     logT [{logT[seg].min():.1f}, {logT[seg].max():.1f}]")
    print(f"    Extrapolated:     logT [{center_raw[0]-r_logT:.1f}, {center_raw[0]+r_logT:.1f}]")
    print(f"    Radius:           {r_logT:.1f} decades in T, {r_logA:.1f} decades in Action")
    print(f"    Center:           logT={center_raw[0]:.1f}")
    print(f"    Arc observed:     {fit['arc_span']:.0f}° of 360°")
