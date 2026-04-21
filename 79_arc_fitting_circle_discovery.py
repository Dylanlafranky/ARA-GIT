#!/usr/bin/env python3
"""
Script 79 — ARC-FITTING CIRCLE DISCOVERY
=========================================
Script 78 used Gaussian Mixture Models (blob-shaped clusters) and found
k=7 optimal, not k=3. But Dylan sees ARCS, not blobs. GMM can't find
arcs — it assumes convex ellipsoidal clusters.

NEW APPROACH:
  Instead of clustering → circle fit, we go directly to arc detection:

  1. Use RANSAC (Random Sample Consensus) to find circles in 3D:
     - Sample 3 random points → fit unique circle through them
     - Count how many other points lie near that circle (inliers)
     - Keep the circle with the most inliers
  2. Remove inliers, repeat to find second and third circles
  3. For each discovered arc: extrapolate to the full 360° circle
  4. Measure overlap, angles between circles, arc coverage

  This is what Dylan's eye is doing — tracing curves through the cloud,
  not looking for gaussian blobs.

COORDINATE SPACE:
  Same as the 3D visualization:
    X = log10(Period)
    Y = ARA (linear, capped for visualization — but we use log for fitting)
    Z = log10(Action/π)

TESTS:
  1. RANSAC finds at least 3 distinct circles
  2. Each circle captures ≥10 inlier points
  3. Circles are non-degenerate (radius > 1, < 100 in log-space)
  4. At least 2 circles have distinct orientations (normal angle > 15°)
  5. Arc coverage: each circle's inliers span > 30° of arc
  6. Extrapolated circles overlap (intersect in 3D)
  7. The matter-scale circle slope near φ
  8. Circle radii are different (not all the same size)
  9. Inlier sets together cover > 60% of all systems
  10. Residuals: mean distance to circle < 15% of radius

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy import stats

np.random.seed(79)
PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

# ============================================================
# FULL DATASET
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

# Parse
names = [d[0] for d in data]
T_arr = np.array([d[1] for d in data])
E_arr = np.array([d[2] for d in data])
ARA_arr = np.array([d[3] for d in data])
cat_arr = np.array([d[4] for d in data])
scale_arr = np.array([d[5] for d in data])

logT = np.log10(T_arr)
logE = np.log10(E_arr)
logA = logT + logE - np.log10(PI)  # Action = T*E/π

# For the ARA axis, use log10(1 + ARA) to compress the extreme outliers
# while keeping the structure around ARA ~ 1-3 visible
logARA = np.log10(1 + ARA_arr)

N = len(data)

print("=" * 70)
print("SCRIPT 79 — ARC-FITTING CIRCLE DISCOVERY (RANSAC)")
print("=" * 70)
print(f"\n  Systems: {N}")
print(f"  Method: RANSAC arc detection → circle extrapolation → overlap mapping")
print(f"  Key: Finding ARCS in the point cloud, not gaussian blobs")

# ============================================================
# 3D COORDINATES — match the visualization
# ============================================================
# The 3D map uses: X = logT, Y = ARA (or logARA), Z = logAction
# We normalise each axis to comparable ranges for distance calculations

coords = np.column_stack([logT, logARA, logA])

# Normalise to unit variance for fair distance measurements
means = coords.mean(axis=0)
stds = coords.std(axis=0)
stds[stds == 0] = 1
coords_norm = (coords - means) / stds

print(f"\n  Raw coordinate ranges:")
print(f"    logT:      [{logT.min():.1f}, {logT.max():.1f}]  σ={logT.std():.1f}")
print(f"    logARA:    [{logARA.min():.3f}, {logARA.max():.1f}]  σ={logARA.std():.2f}")
print(f"    logAction: [{logA.min():.1f}, {logA.max():.1f}]  σ={logA.std():.1f}")

# ============================================================
# CIRCLE FITTING TOOLS
# ============================================================

def fit_circle_through_3_points(p1, p2, p3):
    """
    Fit the unique circle passing through 3 non-collinear points in 3D.
    Returns: center, normal, radius (or None if degenerate)
    """
    # Vectors from p1
    v1 = p2 - p1
    v2 = p3 - p1

    # Normal to the plane
    normal = np.cross(v1, v2)
    norm_len = np.linalg.norm(normal)
    if norm_len < 1e-10:
        return None  # Collinear points
    normal = normal / norm_len

    # The circumcenter lies in the plane of the 3 points.
    # Use the perpendicular bisector method:
    # midpoint of p1-p2 and p1-p3, then solve for intersection
    d11 = np.dot(v1, v1)
    d12 = np.dot(v1, v2)
    d22 = np.dot(v2, v2)

    denom = 2 * (d11 * d22 - d12 * d12)
    if abs(denom) < 1e-10:
        return None

    s = (d11 * d22 - d22 * d12) / denom
    t = (d22 * d11 - d11 * d12) / denom

    # Wait, let me use the standard circumcenter formula
    # center = p1 + s * v1 + t * v2
    b1 = d11 / 2
    b2 = d22 / 2

    # Solve: d11*s + d12*t = b1, d12*s + d22*t = b2
    det = d11 * d22 - d12 * d12
    if abs(det) < 1e-10:
        return None

    s = (d22 * b1 - d12 * b2) / det
    t = (d11 * b2 - d12 * b1) / det

    center = p1 + s * v1 + t * v2
    radius = np.linalg.norm(center - p1)

    if radius < 1e-10 or radius > 1000:
        return None

    # Build orthonormal basis in the circle plane
    e1 = (p1 - center)
    e1_norm = np.linalg.norm(e1)
    if e1_norm < 1e-10:
        return None
    e1 = e1 / e1_norm
    e2 = np.cross(normal, e1)

    return {
        'center': center,
        'normal': normal,
        'radius': radius,
        'e1': e1,
        'e2': e2
    }


def distance_to_circle(points, circle):
    """
    Compute distance from each point to a circle in 3D.
    Distance = sqrt(dist_to_plane² + (dist_in_plane - radius)²)
    """
    centered = points - circle['center']

    # Distance to the plane
    dist_to_plane = centered @ circle['normal']

    # Projection onto the plane
    proj = centered - np.outer(dist_to_plane, circle['normal'])

    # Distance from projection to center (in-plane)
    dist_in_plane = np.linalg.norm(proj, axis=1)

    # Distance to the circle
    radial_diff = dist_in_plane - circle['radius']
    dist = np.sqrt(dist_to_plane**2 + radial_diff**2)

    return dist


def point_angle_on_circle(point, circle):
    """Get the angle (0 to 2π) of a point's projection on the circle."""
    centered = point - circle['center']
    # Project onto plane
    dist_to_plane = np.dot(centered, circle['normal'])
    proj = centered - dist_to_plane * circle['normal']
    # Get angle from e1, e2 basis
    x = np.dot(proj, circle['e1'])
    y = np.dot(proj, circle['e2'])
    return np.arctan2(y, x) % (2 * PI)


def arc_span_degrees(angles):
    """
    Compute the angular span of a set of angles on a circle.
    Handles wraparound.
    """
    if len(angles) < 2:
        return 0
    angles_sorted = np.sort(angles)
    # Gaps between consecutive angles
    gaps = np.diff(angles_sorted)
    # Add the wraparound gap
    gaps = np.append(gaps, (2*PI - angles_sorted[-1] + angles_sorted[0]))
    # The arc span is 360° minus the largest gap
    largest_gap = gaps.max()
    span = 2*PI - largest_gap
    return np.degrees(span)


# ============================================================
# RANSAC CIRCLE DETECTION
# ============================================================
print("\n" + "=" * 70)
print("PHASE 1: RANSAC ARC DETECTION")
print("=" * 70)

def ransac_find_circle(points, indices_pool, threshold, min_inliers=8,
                       n_iterations=20000):
    """
    RANSAC: find the best circle in a 3D point cloud.
    - Sample 3 points, fit circle, count inliers within threshold
    - Return best circle and its inlier indices
    """
    best_circle = None
    best_inliers = []
    best_score = 0
    n_pool = len(indices_pool)

    if n_pool < 3:
        return None, []

    pool_points = points[indices_pool]

    for _ in range(n_iterations):
        # Sample 3 random points
        sample_idx = np.random.choice(n_pool, 3, replace=False)
        p1, p2, p3 = pool_points[sample_idx]

        # Fit circle
        circle = fit_circle_through_3_points(p1, p2, p3)
        if circle is None:
            continue

        # Filter: reasonable radius
        if circle['radius'] < 0.5 or circle['radius'] > 50:
            continue

        # Count inliers
        dists = distance_to_circle(pool_points, circle)
        inlier_mask = dists < threshold
        n_inliers = inlier_mask.sum()

        if n_inliers > best_score:
            best_score = n_inliers
            best_circle = circle
            best_inliers = indices_pool[inlier_mask]

    return best_circle, best_inliers


# Adaptive threshold: fraction of the data spread
data_spread = np.linalg.norm(coords_norm.max(axis=0) - coords_norm.min(axis=0))
threshold = data_spread * 0.08  # 8% of total spread

print(f"\n  Data spread: {data_spread:.2f}")
print(f"  Inlier threshold: {threshold:.3f} (8% of spread)")
print(f"  Iterations per round: 20,000")

# Find circles iteratively
available = np.arange(N)
circles_found = []
inlier_sets = []
MAX_CIRCLES = 6  # Look for up to 6, see how many are real

for round_num in range(MAX_CIRCLES):
    if len(available) < 8:
        break

    circle, inliers = ransac_find_circle(
        coords_norm, available, threshold,
        min_inliers=8, n_iterations=20000
    )

    if circle is None or len(inliers) < 8:
        print(f"\n  Round {round_num + 1}: No more circles found (insufficient inliers)")
        break

    # Compute arc span for this circle's inliers
    angles = np.array([point_angle_on_circle(coords_norm[i], circle) for i in inliers])
    span = arc_span_degrees(angles)

    # Mean distance (quality)
    dists = distance_to_circle(coords_norm[inliers], circle)
    mean_dist = dists.mean()
    rel_residual = mean_dist / circle['radius']

    # What systems are in this circle?
    cats_in = [cat_arr[i] for i in inliers]
    scales_in = [scale_arr[i] for i in inliers]
    mean_logT_in = logT[inliers].mean()

    # Domain guess from mean logT
    if mean_logT_in < -4:
        domain = "QUANTUM"
    elif mean_logT_in > 8:
        domain = "COSMIC"
    else:
        domain = "MATTER"

    circles_found.append(circle)
    inlier_sets.append(inliers)

    print(f"\n  Round {round_num + 1}: Circle found → likely {domain}")
    print(f"    Inliers:       {len(inliers)}")
    print(f"    Radius:        {circle['radius']:.3f}")
    print(f"    Arc span:      {span:.1f}°")
    print(f"    Mean residual: {mean_dist:.4f} ({rel_residual:.1%} of radius)")
    print(f"    Normal:        [{circle['normal'][0]:.3f}, {circle['normal'][1]:.3f}, {circle['normal'][2]:.3f}]")
    print(f"    Center:        [{circle['center'][0]:.3f}, {circle['center'][1]:.3f}, {circle['center'][2]:.3f}]")
    print(f"    Mean logT:     {mean_logT_in:.1f}")
    print(f"    Categories:    {dict(zip(*np.unique(cats_in, return_counts=True)))}")

    # Remove inliers from pool
    available = np.setdiff1d(available, inliers)
    print(f"    Remaining:     {len(available)} systems")

n_circles = len(circles_found)
print(f"\n  ► Total circles found: {n_circles}")

# ============================================================
# PHASE 2: CIRCLE EXTRAPOLATION AND PROPERTIES
# ============================================================
print("\n" + "=" * 70)
print("PHASE 2: EXTRAPOLATED CIRCLE PROPERTIES")
print("=" * 70)

# Convert circle parameters back to raw coordinates for interpretation
for i, (circle, inliers) in enumerate(zip(circles_found, inlier_sets)):
    # Transform center back to raw coords
    center_raw = circle['center'] * stds + means
    # Radius in raw coords (approximate — anisotropic scaling)
    radius_raw_x = circle['radius'] * stds[0]  # logT units
    radius_raw_y = circle['radius'] * stds[1]  # logARA units
    radius_raw_z = circle['radius'] * stds[2]  # logAction units

    # Arc coverage
    angles = np.array([point_angle_on_circle(coords_norm[j], circle) for j in inliers])
    span = arc_span_degrees(angles)
    coverage = span / 360.0

    # logT extent of the full circle
    # The circle spans center_x ± radius_raw_x in logT
    logT_min_circle = center_raw[0] - radius_raw_x
    logT_max_circle = center_raw[0] + radius_raw_x

    mean_logT_in = logT[inliers].mean()
    domain = "QUANTUM" if mean_logT_in < -4 else ("COSMIC" if mean_logT_in > 8 else "MATTER")

    print(f"\n  Circle {i+1} ({domain}):")
    print(f"    Center (raw):   logT={center_raw[0]:.1f}, logARA={center_raw[1]:.2f}, logA={center_raw[2]:.1f}")
    print(f"    Radius (logT):  {radius_raw_x:.1f} orders of magnitude")
    print(f"    Radius (logA):  {radius_raw_z:.1f} orders of magnitude")
    print(f"    Arc observed:   {span:.0f}° ({coverage:.0%} of full circle)")
    print(f"    Full circle logT range: [{logT_min_circle:.1f}, {logT_max_circle:.1f}]")
    print(f"    Points sampled: logT [{logT[inliers].min():.1f}, {logT[inliers].max():.1f}]")

    # Slope analysis for this circle's systems
    if len(inliers) > 3:
        slope, intercept, r_val, p_val, std_err = stats.linregress(logT[inliers], logE[inliers])
        phi_dist = abs(slope - PHI)
        print(f"    logE vs logT slope: {slope:.3f}  (|Δφ| = {phi_dist:.3f})")
        if domain == "MATTER" and phi_dist < 0.25:
            print(f"    ► MATTER SLOPE NEAR φ: {slope:.3f} vs {PHI:.3f}")

# ============================================================
# PHASE 3: CIRCLE-CIRCLE RELATIONSHIPS
# ============================================================
print("\n" + "=" * 70)
print("PHASE 3: CIRCLE-CIRCLE RELATIONSHIPS")
print("=" * 70)

if n_circles >= 2:
    for i in range(n_circles):
        for j in range(i+1, n_circles):
            ci = circles_found[i]
            cj = circles_found[j]

            # Normal angle (orientation difference)
            cos_a = abs(np.dot(ci['normal'], cj['normal']))
            angle_deg = np.degrees(np.arccos(np.clip(cos_a, 0, 1)))

            # Center distance vs sum of radii
            center_dist = np.linalg.norm(ci['center'] - cj['center'])
            sum_radii = ci['radius'] + cj['radius']
            overlap = center_dist < sum_radii

            # Shared inliers (points claimed by both circles)
            shared = np.intersect1d(inlier_sets[i], inlier_sets[j])

            print(f"\n  Circles {i+1} ↔ {j+1}:")
            print(f"    Normal angle:    {angle_deg:.1f}°  ({'distinct' if angle_deg > 15 else 'similar orientation'})")
            print(f"    Center distance: {center_dist:.3f}")
            print(f"    Sum of radii:    {sum_radii:.3f}")
            print(f"    Geometric overlap: {'YES' if overlap else 'NO'}")
            print(f"    Shared points:   {len(shared)}")

    # Do the circles intersect? (two circles in 3D intersect at 0 or 2 points
    # if their planes intersect and the circles are close enough)
    print(f"\n  Intersection analysis:")
    for i in range(n_circles):
        for j in range(i+1, n_circles):
            ci = circles_found[i]
            cj = circles_found[j]

            # Check if planes intersect (they always do unless parallel)
            cos_a = abs(np.dot(ci['normal'], cj['normal']))
            if cos_a > 0.999:
                print(f"    Circles {i+1}↔{j+1}: Planes nearly parallel — no intersection")
            else:
                # Planes intersect along a line. Check if that line passes
                # close enough to both circles.
                # This is the full 3D circle-circle intersection test
                n1, n2 = ci['normal'], cj['normal']
                c1, c2 = ci['center'], cj['center']
                r1, r2 = ci['radius'], cj['radius']

                # Line direction = cross(n1, n2)
                line_dir = np.cross(n1, n2)
                line_dir = line_dir / np.linalg.norm(line_dir)

                # Point on the intersection line closest to both centers
                # Solve: n1·p = n1·c1, n2·p = n2·c2
                A_mat = np.array([n1, n2, line_dir])
                if abs(np.linalg.det(A_mat)) < 1e-10:
                    print(f"    Circles {i+1}↔{j+1}: Degenerate intersection")
                    continue

                b_vec = np.array([np.dot(n1, c1), np.dot(n2, c2), 0])
                # Use least squares for the 3-equation system
                p0 = np.linalg.solve(A_mat, b_vec)

                # Distance from p0 to each circle center
                d1 = np.linalg.norm(p0 - c1)
                d2 = np.linalg.norm(p0 - c2)

                # The intersection line passes at distance d from circle center
                # If |d - r| is small, circles cross near each other
                print(f"    Circles {i+1}↔{j+1}: Plane intersection at angle {np.degrees(np.arccos(cos_a)):.1f}°")
                print(f"      Distance from line to center 1: {d1:.3f} (radius {r1:.3f})")
                print(f"      Distance from line to center 2: {d2:.3f} (radius {r2:.3f})")

                # Rough intersection check
                if d1 < r1 * 1.5 and d2 < r2 * 1.5:
                    print(f"      → CIRCLES LIKELY INTERSECT")
                else:
                    print(f"      → Circles may not intersect at these radii")

# ============================================================
# PHASE 4: TRIPLE OVERLAP CHECK
# ============================================================
print("\n" + "=" * 70)
print("PHASE 4: TRIPLE OVERLAP CHECK")
print("=" * 70)

if n_circles >= 3:
    # Check each point: how many circles is it near?
    proximity_threshold = threshold * 1.5  # slightly relaxed for overlap check
    circle_membership = np.zeros((N, n_circles))

    for c_idx, circle in enumerate(circles_found):
        dists = distance_to_circle(coords_norm, circle)
        circle_membership[:, c_idx] = (dists < proximity_threshold).astype(float)

    n_near = circle_membership.sum(axis=1)
    n_near_1 = (n_near >= 1).sum()
    n_near_2 = (n_near >= 2).sum()
    n_near_3 = (n_near >= 3).sum()

    print(f"\n  Points near at least 1 circle: {n_near_1}")
    print(f"  Points near at least 2 circles: {n_near_2}")
    print(f"  Points near at least 3 circles: {n_near_3}")

    if n_near_3 > 0:
        triple_idx = np.where(n_near >= 3)[0]
        triple_names = [names[i] for i in triple_idx]
        triple_logT = logT[triple_idx]
        print(f"\n  Triple-overlap systems:")
        for idx in triple_idx:
            print(f"    {names[idx]:25s}  logT={logT[idx]:.1f}  ARA={ARA_arr[idx]:.2f}")
        print(f"\n  Mean logT of triple overlap: {triple_logT.mean():.1f}")
        print(f"  Near human scale? {'YES' if abs(triple_logT.mean()) < 4 else 'NO'}")
    else:
        # Relax threshold and check again
        for factor in [2.0, 2.5, 3.0]:
            relaxed = threshold * factor
            cm = np.zeros((N, n_circles))
            for c_idx, circle in enumerate(circles_found):
                dists = distance_to_circle(coords_norm, circle)
                cm[:, c_idx] = (dists < relaxed).astype(float)
            n3 = (cm.sum(axis=1) >= 3).sum()
            if n3 > 0:
                print(f"\n  At threshold × {factor:.1f}: {n3} systems near 3+ circles")
                triple_idx = np.where(cm.sum(axis=1) >= 3)[0]
                print(f"  Mean logT: {logT[triple_idx].mean():.1f}")
                break
        else:
            print(f"\n  No triple overlap found even at relaxed thresholds")

# ============================================================
# TESTS
# ============================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 10

# Test 1: Found at least 3 circles
t1 = n_circles >= 3
print(f"\n  Test  1: RANSAC finds at least 3 distinct circles")
print(f"           Found: {n_circles}")
print(f"           → {'PASS ✓' if t1 else 'FAIL ✗'}")
passed += t1

# Test 2: Each circle has ≥ 10 inliers
t2 = all(len(s) >= 10 for s in inlier_sets[:min(3, n_circles)])
print(f"\n  Test  2: Each circle captures ≥ 10 inlier points")
for i, s in enumerate(inlier_sets[:min(3, n_circles)]):
    print(f"           Circle {i+1}: {len(s)} inliers")
print(f"           → {'PASS ✓' if t2 else 'FAIL ✗'}")
passed += t2

# Test 3: Circles are non-degenerate (reasonable radius)
t3 = all(0.5 < c['radius'] < 50 for c in circles_found[:min(3, n_circles)])
print(f"\n  Test  3: Circle radii non-degenerate (0.5 < r < 50)")
for i, c in enumerate(circles_found[:min(3, n_circles)]):
    print(f"           Circle {i+1}: r = {c['radius']:.3f}")
print(f"           → {'PASS ✓' if t3 else 'FAIL ✗'}")
passed += t3

# Test 4: At least 2 circles have distinct orientations
if n_circles >= 2:
    angles_between = []
    for i in range(min(3, n_circles)):
        for j in range(i+1, min(3, n_circles)):
            cos_a = abs(np.dot(circles_found[i]['normal'], circles_found[j]['normal']))
            angles_between.append(np.degrees(np.arccos(np.clip(cos_a, 0, 1))))
    t4 = any(a > 15 for a in angles_between)
    print(f"\n  Test  4: At least 2 circles have distinct orientations (>15°)")
    for k, a in enumerate(angles_between):
        print(f"           Pair {k+1}: {a:.1f}°")
else:
    t4 = False
    print(f"\n  Test  4: At least 2 circles have distinct orientations")
print(f"           → {'PASS ✓' if t4 else 'FAIL ✗'}")
passed += t4

# Test 5: Arc coverage > 30° for each circle
arc_spans = []
for i, (circle, inliers) in enumerate(zip(circles_found[:min(3, n_circles)],
                                           inlier_sets[:min(3, n_circles)])):
    angles = np.array([point_angle_on_circle(coords_norm[j], circle) for j in inliers])
    span = arc_span_degrees(angles)
    arc_spans.append(span)
t5 = all(s > 30 for s in arc_spans) if arc_spans else False
print(f"\n  Test  5: Arc coverage > 30° for each circle")
for i, s in enumerate(arc_spans):
    print(f"           Circle {i+1}: {s:.0f}°")
print(f"           → {'PASS ✓' if t5 else 'FAIL ✗'}")
passed += t5

# Test 6: Circles overlap geometrically
if n_circles >= 2:
    any_overlap = False
    for i in range(min(3, n_circles)):
        for j in range(i+1, min(3, n_circles)):
            cd = np.linalg.norm(circles_found[i]['center'] - circles_found[j]['center'])
            sr = circles_found[i]['radius'] + circles_found[j]['radius']
            if cd < sr:
                any_overlap = True
    t6 = any_overlap
else:
    t6 = False
print(f"\n  Test  6: Circles overlap (centers < sum of radii)")
print(f"           → {'PASS ✓' if t6 else 'FAIL ✗'}")
passed += t6

# Test 7: Matter circle slope near φ
t7 = False
for i, inliers in enumerate(inlier_sets[:min(3, n_circles)]):
    mean_lt = logT[inliers].mean()
    if -4 <= mean_lt <= 8 and len(inliers) > 5:
        slope, _, _, _, _ = stats.linregress(logT[inliers], logE[inliers])
        if abs(slope - PHI) < 0.25:
            t7 = True
            print(f"\n  Test  7: Matter-scale circle slope near φ")
            print(f"           Circle {i+1}: slope = {slope:.3f}, |Δφ| = {abs(slope-PHI):.3f}")
            break
if not t7:
    print(f"\n  Test  7: Matter-scale circle slope near φ")
    print(f"           No matter circle found with slope near φ")
print(f"           → {'PASS ✓' if t7 else 'FAIL ✗'}")
passed += t7

# Test 8: Radii are different
if n_circles >= 2:
    radii = sorted([c['radius'] for c in circles_found[:min(3, n_circles)]])
    t8 = radii[-1] / radii[0] > 1.3 if radii[0] > 0 else False
    print(f"\n  Test  8: Circle radii are different (ratio > 1.3)")
    print(f"           Radii: {[f'{r:.3f}' for r in radii]}")
    print(f"           Ratio: {radii[-1]/radii[0]:.2f}")
else:
    t8 = False
    print(f"\n  Test  8: Circle radii are different")
print(f"           → {'PASS ✓' if t8 else 'FAIL ✗'}")
passed += t8

# Test 9: Inlier sets cover > 60% of all systems
all_inliers = set()
for s in inlier_sets[:min(3, n_circles)]:
    all_inliers.update(s)
coverage_pct = 100 * len(all_inliers) / N
t9 = coverage_pct > 60
print(f"\n  Test  9: Inliers cover > 60% of all systems")
print(f"           Coverage: {len(all_inliers)}/{N} = {coverage_pct:.1f}%")
print(f"           → {'PASS ✓' if t9 else 'FAIL ✗'}")
passed += t9

# Test 10: Mean residual < 15% of radius
t10_results = []
for i, (circle, inliers) in enumerate(zip(circles_found[:min(3, n_circles)],
                                           inlier_sets[:min(3, n_circles)])):
    dists = distance_to_circle(coords_norm[inliers], circle)
    rel = dists.mean() / circle['radius'] if circle['radius'] > 0 else 999
    t10_results.append(rel < 0.15)
t10 = all(t10_results) if t10_results else False
print(f"\n  Test 10: Mean distance to circle < 15% of radius")
for i, (circle, inliers) in enumerate(zip(circles_found[:min(3, n_circles)],
                                           inlier_sets[:min(3, n_circles)])):
    dists = distance_to_circle(coords_norm[inliers], circle)
    rel = dists.mean() / circle['radius']
    print(f"           Circle {i+1}: {rel:.3f} ({rel:.1%})")
print(f"           → {'PASS ✓' if t10 else 'FAIL ✗'}")
passed += t10

# ============================================================
# FINAL SCORE
# ============================================================
print("\n" + "=" * 70)
score = passed
print(f"  SCORE: {score} / {total}")
print("=" * 70)

print(f"\n  SUMMARY:")
print(f"  • Circles found by RANSAC: {n_circles}")
for i in range(min(n_circles, 4)):
    mean_lt = logT[inlier_sets[i]].mean()
    domain = "quantum" if mean_lt < -4 else ("cosmic" if mean_lt > 8 else "matter")
    span = arc_spans[i] if i < len(arc_spans) else 0
    print(f"  • Circle {i+1} ({domain}): {len(inlier_sets[i])} pts, r={circles_found[i]['radius']:.2f}, arc={span:.0f}°")

total_inliers = sum(len(s) for s in inlier_sets[:min(3, n_circles)])
print(f"  • Total systems on arcs: {len(all_inliers)}/{N} ({coverage_pct:.0f}%)")

if score >= 7:
    print(f"\n  VERDICT: STRONG — The data contains arc/circle structure detectable by RANSAC.")
    print(f"  Dylan's visual pattern recognition is confirmed by blind arc fitting.")
elif score >= 5:
    print(f"\n  VERDICT: MODERATE — Arc structure exists but is partial.")
    print(f"  Some of what Dylan sees is real geometry; some may be pattern-matching.")
else:
    print(f"\n  VERDICT: WEAK — RANSAC does not strongly support three-circle structure.")
    print(f"  The visual impression may be driven by data density, not curvature.")

# ============================================================
# OUTPUT CIRCLE DATA FOR VISUALIZATION
# ============================================================
print("\n" + "=" * 70)
print("CIRCLE DATA FOR 3D MAP (raw coordinates)")
print("=" * 70)

for i, circle in enumerate(circles_found[:min(4, n_circles)]):
    center_raw = circle['center'] * stds + means
    normal_raw = circle['normal']  # direction doesn't change with translation
    # Scale the basis vectors back
    e1_raw = circle['e1'] * stds
    e2_raw = circle['e2'] * stds
    radius_scaled = circle['radius']

    # Generate full circle points (extrapolated)
    print(f"\n  Circle {i+1}:")
    print(f"    center: [{center_raw[0]:.4f}, {center_raw[1]:.4f}, {center_raw[2]:.4f}]")
    print(f"    normal: [{normal_raw[0]:.4f}, {normal_raw[1]:.4f}, {normal_raw[2]:.4f}]")
    print(f"    e1:     [{e1_raw[0]:.4f}, {e1_raw[1]:.4f}, {e1_raw[2]:.4f}]")
    print(f"    e2:     [{e2_raw[0]:.4f}, {e2_raw[1]:.4f}, {e2_raw[2]:.4f}]")
    print(f"    radius (norm): {radius_scaled:.4f}")

    # What are the extrapolated circle bounds in physical units?
    # Generate 36 points around the circle
    for angle_deg in [0, 90, 180, 270]:
        a = np.radians(angle_deg)
        pt = circle['center'] + circle['radius'] * (np.cos(a) * circle['e1'] + np.sin(a) * circle['e2'])
        pt_raw = pt * stds + means
        print(f"    @{angle_deg:3d}°: logT={pt_raw[0]:.1f}, logARA={pt_raw[1]:.2f}, logA={pt_raw[2]:.1f}")
