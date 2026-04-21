#!/usr/bin/env python3
"""
Script 78 — UNSUPERVISED CIRCLE DISCOVERY IN THE 3D SPINE
==========================================================
QUESTION:
  Dylan sees three overlapping circles in the 3D temporal coordinate map.
  Script 76 tested three-circle decomposition using HUMAN-CLASSIFIED domains.
  This script asks: do three circles emerge WITHOUT being told they exist?

METHOD:
  1. Take the full dataset, compute 3D coordinates: (logT, ARA, logAction)
  2. Normalise each axis to [0, 1] so clustering isn't biased by scale
  3. Run unsupervised clustering (Gaussian Mixture Model) for k = 1..8
  4. Let BIC/AIC pick the optimal number of clusters
  5. For each discovered cluster, fit a 3D circle:
       a. PCA for the best-fit plane
       b. Project points onto that plane
       c. Algebraic circle fit in 2D
       d. Transform back to 3D
  6. Measure overlap between discovered circles
  7. Compare discovered clusters to the hand-classified domains (quantum/matter/planetary)

TESTS:
  1. Optimal cluster count = 3 (or includes 3 in top candidates)
  2. Discovered clusters correspond to scale-separated populations
  3. Each cluster's points fit a circle (residual < threshold)
  4. Circles overlap — shared boundary regions exist
  5. The matter/middle circle slope is near φ
  6. Circle radii follow a size hierarchy
  7. Triple-overlap region exists near human scale
  8. Discovered clustering matches hand-classified domains (>60% agreement)
  9. Information criterion strongly prefers 3 over 1 or 2
  10. Circle normals are non-parallel (three distinct orientations)

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy import stats
from collections import Counter

np.random.seed(78)
PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

# ============================================================
# FULL DATASET (from Script 76)
# ============================================================
data = [
    # (name, period_s, energy_J, ARA, category, scale_label)
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

N = len(data)

print("=" * 70)
print("SCRIPT 78 — UNSUPERVISED CIRCLE DISCOVERY IN THE 3D SPINE")
print("=" * 70)
print(f"\n  Systems: {N}")
print(f"  Period range: 10^{logT.min():.1f} → 10^{logT.max():.1f} s")
print(f"  Method: GMM clustering → 3D circle fitting → overlap analysis")
print(f"  Key constraint: NO domain labels used in clustering")

# ============================================================
# STEP 1: BUILD 3D COORDINATES
# ============================================================
# Same axes as the 3D visualization:
#   X = log10(Period)
#   Y = ARA  (but we use log for clustering since range is huge)
#   Z = log10(Action/π)
#
# For clustering, we need to handle extreme ARA values.
# Use log10(ARA + 1) to compress while keeping near-1 values distinct.

logARA = np.log10(ARA_arr + 1)  # +1 avoids log(0), preserves ordering

coords_raw = np.column_stack([logT, logARA, logA])

# Normalise to [0, 1] for fair clustering
mins = coords_raw.min(axis=0)
maxs = coords_raw.max(axis=0)
ranges = maxs - mins
ranges[ranges == 0] = 1  # avoid division by zero
coords_norm = (coords_raw - mins) / ranges

print(f"\n  Coordinate ranges (raw):")
print(f"    logT:      [{logT.min():.1f}, {logT.max():.1f}]")
print(f"    logARA:    [{logARA.min():.3f}, {logARA.max():.3f}]")
print(f"    logAction: [{logA.min():.1f}, {logA.max():.1f}]")

# ============================================================
# STEP 2: GAUSSIAN MIXTURE MODEL — LET THE DATA SPEAK
# ============================================================
print("\n" + "=" * 70)
print("PHASE 1: UNSUPERVISED CLUSTERING (GMM)")
print("=" * 70)

# Implement GMM from scratch (no sklearn dependency)
# Using Expectation-Maximization

def gmm_fit(X, k, max_iter=200, tol=1e-6):
    """Fit a Gaussian Mixture Model with k components."""
    n, d = X.shape

    # Initialize with k-means++ style seeding
    centers = [X[np.random.randint(n)]]
    for _ in range(1, k):
        dists = np.array([np.min([np.sum((x - c)**2) for c in centers]) for x in X])
        probs = dists / dists.sum()
        idx = np.random.choice(n, p=probs)
        centers.append(X[idx])

    means = np.array(centers)
    covs = [np.eye(d) * 0.1 for _ in range(k)]
    weights = np.ones(k) / k

    log_likelihood = -np.inf

    for iteration in range(max_iter):
        # E-step: compute responsibilities
        resp = np.zeros((n, k))
        for j in range(k):
            diff = X - means[j]
            cov = covs[j]
            # Add regularization for numerical stability
            cov_reg = cov + np.eye(d) * 1e-6
            try:
                L = np.linalg.cholesky(cov_reg)
                log_det = 2 * np.sum(np.log(np.diag(L)))
                solved = np.linalg.solve(L, diff.T).T
                mahal = np.sum(solved**2, axis=1)
                log_prob = -0.5 * (d * np.log(2*PI) + log_det + mahal)
                resp[:, j] = np.log(weights[j] + 1e-300) + log_prob
            except np.linalg.LinAlgError:
                resp[:, j] = -1e10

        # Log-sum-exp for numerical stability
        max_resp = resp.max(axis=1, keepdims=True)
        log_sum = max_resp + np.log(np.sum(np.exp(resp - max_resp), axis=1, keepdims=True))
        resp = np.exp(resp - log_sum)

        new_ll = np.sum(log_sum)
        if abs(new_ll - log_likelihood) < tol:
            break
        log_likelihood = new_ll

        # M-step: update parameters
        Nk = resp.sum(axis=0) + 1e-10
        weights = Nk / n

        for j in range(k):
            means[j] = (resp[:, j:j+1].T @ X) / Nk[j]
            diff = X - means[j]
            covs[j] = (diff.T * resp[:, j]) @ diff / Nk[j]

    return means, covs, weights, resp, log_likelihood

def compute_bic(ll, k, n, d):
    """Bayesian Information Criterion."""
    # Parameters: k means (k*d) + k covariances (k*d*(d+1)/2) + k-1 weights
    num_params = k * d + k * d * (d + 1) / 2 + (k - 1)
    return -2 * ll + num_params * np.log(n)

def compute_aic(ll, k, d):
    """Akaike Information Criterion."""
    num_params = k * d + k * d * (d + 1) / 2 + (k - 1)
    return -2 * ll + 2 * num_params

# Test k = 1 through 8
print("\n  Testing cluster counts k = 1 → 8 ...")
print(f"  {'k':>3}  {'BIC':>12}  {'AIC':>12}  {'Log-L':>12}")
print(f"  {'—'*3}  {'—'*12}  {'—'*12}  {'—'*12}")

results = {}
best_bic = np.inf
best_k = 1

# Run multiple times per k to avoid local optima
for k in range(1, 9):
    best_ll_k = -np.inf
    best_result_k = None

    for trial in range(10):  # 10 random restarts per k
        np.random.seed(78 * 100 + k * 10 + trial)
        try:
            means, covs, weights, resp, ll = gmm_fit(coords_norm, k)
            if ll > best_ll_k:
                best_ll_k = ll
                best_result_k = (means, covs, weights, resp, ll)
        except:
            continue

    if best_result_k is None:
        continue

    means, covs, weights, resp, ll = best_result_k
    bic = compute_bic(ll, k, N, 3)
    aic = compute_aic(ll, k, 3)
    results[k] = {'bic': bic, 'aic': aic, 'll': ll,
                   'means': means, 'covs': covs, 'weights': weights, 'resp': resp}

    marker = " ◄ best" if bic < best_bic else ""
    if bic < best_bic:
        best_bic = bic
        best_k = k

    print(f"  {k:>3}  {bic:>12.1f}  {aic:>12.1f}  {ll:>12.1f}{marker}")

print(f"\n  ► BIC-optimal cluster count: k = {best_k}")

# Also check: is k=3 in the top candidates?
sorted_by_bic = sorted(results.items(), key=lambda x: x[1]['bic'])
top3_k = [s[0] for s in sorted_by_bic[:3]]
print(f"  ► Top 3 by BIC: k = {top3_k}")

# ============================================================
# STEP 3: ANALYSE THE DISCOVERED CLUSTERS
# ============================================================
print("\n" + "=" * 70)
print("PHASE 2: CLUSTER ANALYSIS")
print("=" * 70)

# Use the best k result, but ALSO analyse k=3 explicitly
# to test Dylan's specific claim
for analysis_k in [best_k] + ([3] if best_k != 3 else []):
    if analysis_k not in results:
        continue

    r = results[analysis_k]
    labels = r['resp'].argmax(axis=1)

    print(f"\n  --- Analysis for k = {analysis_k} ---")

    for c in range(analysis_k):
        mask = labels == c
        count = mask.sum()
        mean_logT = logT[mask].mean() if count > 0 else 0
        mean_logE = logE[mask].mean() if count > 0 else 0
        mean_ARA = ARA_arr[mask].mean() if count > 0 else 0
        median_ARA = np.median(ARA_arr[mask]) if count > 0 else 0
        logT_range = (logT[mask].min(), logT[mask].max()) if count > 0 else (0, 0)

        # What categories are in this cluster?
        cats = Counter(cat_arr[mask])
        scales = Counter(scale_arr[mask])

        print(f"\n  Cluster {c}: {count} systems")
        print(f"    logT range: [{logT_range[0]:.1f}, {logT_range[1]:.1f}]  mean: {mean_logT:.1f}")
        print(f"    mean logE:  {mean_logE:.1f}")
        print(f"    median ARA: {median_ARA:.2f}")
        print(f"    Categories: {dict(cats.most_common(4))}")
        print(f"    Scales:     {dict(scales.most_common(4))}")

# ============================================================
# STEP 4: 3D CIRCLE FITTING
# ============================================================
print("\n" + "=" * 70)
print("PHASE 3: 3D CIRCLE FITTING TO DISCOVERED CLUSTERS")
print("=" * 70)

def fit_circle_3d(points):
    """
    Fit a 3D circle to a set of points.
    Returns: center, normal, radius, v1, v2, residuals

    Method:
    1. PCA to find the best-fit plane
    2. Project onto that plane
    3. Algebraic circle fit in 2D (Kasa method)
    4. Transform back to 3D
    """
    pts = np.array(points)
    n = len(pts)

    if n < 4:
        return None

    # Centroid
    center = pts.mean(axis=0)
    centered = pts - center

    # PCA via SVD
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)

    # v1, v2 = principal axes in the plane; v3 = normal
    v1 = Vt[0]  # largest variance direction
    v2 = Vt[1]  # second largest
    normal = Vt[2]  # smallest variance = normal to best-fit plane

    # Project onto the plane (2D coordinates)
    proj_x = centered @ v1
    proj_y = centered @ v2

    # Planarity: how flat is the point cloud?
    # S[2] / S[0] = ratio of smallest to largest singular value
    planarity = 1.0 - S[2] / S[0] if S[0] > 0 else 0

    # Algebraic circle fit in 2D (Kasa method)
    # Minimize sum of (x^2 + y^2 - ax - by - c)^2
    A_mat = np.column_stack([proj_x, proj_y, np.ones(n)])
    b_vec = proj_x**2 + proj_y**2

    try:
        result, _, _, _ = np.linalg.lstsq(A_mat, b_vec, rcond=None)
    except np.linalg.LinAlgError:
        return None

    cx_2d = result[0] / 2
    cy_2d = result[1] / 2
    radius = np.sqrt(result[2] + cx_2d**2 + cy_2d**2)

    # Transform circle center back to 3D
    circle_center_3d = center + cx_2d * v1 + cy_2d * v2

    # Compute residuals (distance from each point to the circle)
    dists_from_center = np.sqrt((proj_x - cx_2d)**2 + (proj_y - cy_2d)**2)
    residuals = np.abs(dists_from_center - radius)

    return {
        'center': circle_center_3d,
        'normal': normal,
        'radius': radius,
        'v1': v1,
        'v2': v2,
        'residuals': residuals,
        'planarity': planarity,
        'mean_residual': residuals.mean(),
        'max_residual': residuals.max(),
        'n_points': n
    }

# Use k=3 for circle fitting (testing Dylan's specific claim)
k_test = 3
if k_test not in results:
    print("  ERROR: k=3 not available in results")
else:
    r3 = results[k_test]
    labels3 = r3['resp'].argmax(axis=1)

    # Fit circles in the RAW coordinate space (not normalised)
    circle_fits = {}

    for c in range(k_test):
        mask = labels3 == c
        if mask.sum() < 4:
            print(f"\n  Cluster {c}: too few points ({mask.sum()}) for circle fit")
            continue

        pts = coords_raw[mask]
        fit = fit_circle_3d(pts)

        if fit is None:
            print(f"\n  Cluster {c}: circle fit failed")
            continue

        circle_fits[c] = fit

        # Determine which domain this cluster most resembles
        mean_logT = logT[mask].mean()
        if mean_logT < -2:
            domain_guess = "QUANTUM"
        elif mean_logT > 8:
            domain_guess = "COSMIC/PLANETARY"
        else:
            domain_guess = "MATTER"

        print(f"\n  Cluster {c} → likely {domain_guess}")
        print(f"    Points:        {fit['n_points']}")
        print(f"    Planarity:     {fit['planarity']:.3f}  (1.0 = perfectly flat)")
        print(f"    Circle radius: {fit['radius']:.2f}")
        print(f"    Mean residual: {fit['mean_residual']:.3f}")
        print(f"    Max residual:  {fit['max_residual']:.3f}")
        print(f"    Normal vector: [{fit['normal'][0]:.3f}, {fit['normal'][1]:.3f}, {fit['normal'][2]:.3f}]")
        print(f"    Center:        [{fit['center'][0]:.2f}, {fit['center'][1]:.2f}, {fit['center'][2]:.2f}]")

# ============================================================
# STEP 5: OVERLAP ANALYSIS
# ============================================================
print("\n" + "=" * 70)
print("PHASE 4: CIRCLE OVERLAP ANALYSIS")
print("=" * 70)

if k_test in results and len(circle_fits) >= 2:
    r3 = results[k_test]
    resp3 = r3['resp']

    # Soft overlap: points with significant probability (>0.1) in multiple clusters
    overlap_threshold = 0.1
    membership_count = (resp3 > overlap_threshold).sum(axis=1)

    n_single = (membership_count == 1).sum()
    n_double = (membership_count == 2).sum()
    n_triple = (membership_count >= 3).sum()

    print(f"\n  Soft membership (threshold = {overlap_threshold}):")
    print(f"    Single-domain:  {n_single} systems ({100*n_single/N:.1f}%)")
    print(f"    Double-overlap: {n_double} systems ({100*n_double/N:.1f}%)")
    print(f"    Triple-overlap: {n_triple} systems ({100*n_triple/N:.1f}%)")

    # Where is the triple overlap?
    if n_triple > 0:
        triple_mask = membership_count >= 3
        triple_logT = logT[triple_mask]
        print(f"\n    Triple-overlap logT range: [{triple_logT.min():.1f}, {triple_logT.max():.1f}]")
        print(f"    Triple-overlap mean logT:  {triple_logT.mean():.1f}")
        print(f"    Human scale (logT ≈ 0)?    {'YES' if abs(triple_logT.mean()) < 3 else 'NO'}")

    # Circle-circle distances and overlap
    if len(circle_fits) >= 2:
        print(f"\n  Circle-circle relationships:")
        keys = sorted(circle_fits.keys())
        for i in range(len(keys)):
            for j in range(i+1, len(keys)):
                ci = circle_fits[keys[i]]
                cj = circle_fits[keys[j]]

                center_dist = np.linalg.norm(ci['center'] - cj['center'])
                sum_radii = ci['radius'] + cj['radius']
                overlap_ratio = 1.0 - center_dist / sum_radii if sum_radii > 0 else 0

                # Angle between normals
                cos_angle = abs(np.dot(ci['normal'], cj['normal']))
                angle_deg = np.degrees(np.arccos(np.clip(cos_angle, 0, 1)))

                print(f"    Clusters {keys[i]}↔{keys[j]}:")
                print(f"      Center distance: {center_dist:.2f}")
                print(f"      Sum of radii:    {sum_radii:.2f}")
                print(f"      Overlap ratio:   {overlap_ratio:.3f} ({'overlapping' if overlap_ratio > 0 else 'separated'})")
                print(f"      Normal angle:    {angle_deg:.1f}° ({'distinct' if angle_deg > 15 else 'parallel'})")

# ============================================================
# STEP 6: COMPARE TO HAND-CLASSIFIED DOMAINS
# ============================================================
print("\n" + "=" * 70)
print("PHASE 5: COMPARISON TO HAND-CLASSIFIED DOMAINS")
print("=" * 70)

if k_test in results:
    r3 = results[k_test]
    labels3 = r3['resp'].argmax(axis=1)

    # Script 76's classification: quantum if cat='quantum', planetary/cosmic if
    # cat='cosmological' or scale='cosmic', else matter
    hand_labels = []
    for i in range(N):
        if cat_arr[i] == 'quantum':
            hand_labels.append('quantum')
        elif cat_arr[i] == 'cosmological' or scale_arr[i] == 'cosmic':
            hand_labels.append('planetary')
        else:
            hand_labels.append('matter')
    hand_labels = np.array(hand_labels)

    # For each discovered cluster, find best-matching hand domain
    domain_names = ['quantum', 'matter', 'planetary']

    # Build confusion-like matrix
    print(f"\n  Cluster → Domain mapping:")
    cluster_domain_map = {}

    for c in range(k_test):
        mask = labels3 == c
        hand_in_cluster = hand_labels[mask]
        counts = Counter(hand_in_cluster)
        dominant = counts.most_common(1)[0] if counts else ('?', 0)
        purity = dominant[1] / mask.sum() if mask.sum() > 0 else 0

        cluster_domain_map[c] = dominant[0]

        print(f"    Cluster {c}: {dict(counts)}")
        print(f"      → Best match: {dominant[0]} (purity: {purity:.1%})")

    # Overall agreement
    agreement = 0
    for i in range(N):
        if cluster_domain_map.get(labels3[i], '?') == hand_labels[i]:
            agreement += 1

    agreement_pct = 100 * agreement / N
    print(f"\n  Overall agreement: {agreement}/{N} = {agreement_pct:.1f}%")

# ============================================================
# STEP 7: SLOPE ANALYSIS PER CLUSTER
# ============================================================
print("\n" + "=" * 70)
print("PHASE 6: SLOPE ANALYSIS (logE vs logT per cluster)")
print("=" * 70)

if k_test in results:
    r3 = results[k_test]
    labels3 = r3['resp'].argmax(axis=1)

    for c in range(k_test):
        mask = labels3 == c
        if mask.sum() < 3:
            continue

        slope, intercept, r_val, p_val, std_err = stats.linregress(logT[mask], logE[mask])

        # Determine likely domain
        mean_logT = logT[mask].mean()
        domain_tag = "quantum" if mean_logT < -2 else ("planetary" if mean_logT > 8 else "matter")

        phi_dist = abs(slope - PHI)

        print(f"\n  Cluster {c} ({domain_tag}):")
        print(f"    Slope: {slope:.3f}  (|Δφ| = {phi_dist:.3f})")
        print(f"    R²:    {r_val**2:.4f}")
        print(f"    p:     {p_val:.2e}")

        if domain_tag == "matter":
            print(f"    ► Matter slope vs φ: {slope:.3f} vs {PHI:.3f} — {'CLOSE' if phi_dist < 0.2 else 'NOT CLOSE'}")

# ============================================================
# TESTS
# ============================================================
print("\n" + "=" * 70)
print("TESTS")
print("=" * 70)

passed = 0
total = 10

# Test 1: Optimal cluster count = 3 (or 3 is in top 3)
t1 = best_k == 3 or 3 in top3_k
print(f"\n  Test  1: Three clusters emerge as optimal or top candidate")
print(f"           BIC-optimal k = {best_k}, top 3: {top3_k}")
print(f"           → {'PASS ✓' if t1 else 'FAIL ✗'}")
passed += t1

# Test 2: Clusters correspond to scale-separated populations
if k_test in results:
    r3 = results[k_test]
    labels3 = r3['resp'].argmax(axis=1)
    cluster_means = [logT[labels3 == c].mean() for c in range(k_test)]
    cluster_means_sorted = sorted(cluster_means)
    scale_separated = all(cluster_means_sorted[i+1] - cluster_means_sorted[i] > 2
                         for i in range(len(cluster_means_sorted)-1))
    t2 = scale_separated
else:
    t2 = False
print(f"\n  Test  2: Clusters are scale-separated (>2 orders of magnitude apart)")
print(f"           Cluster mean logT: {[f'{m:.1f}' for m in cluster_means_sorted]}")
print(f"           → {'PASS ✓' if t2 else 'FAIL ✗'}")
passed += t2

# Test 3: Each cluster fits a circle (mean residual < 30% of radius)
t3_results = []
for c, fit in circle_fits.items():
    rel_residual = fit['mean_residual'] / fit['radius'] if fit['radius'] > 0 else 999
    t3_results.append(rel_residual < 0.30)
t3 = all(t3_results) and len(t3_results) >= 2
print(f"\n  Test  3: Each cluster fits a circle (relative residual < 30%)")
for c, fit in circle_fits.items():
    rel = fit['mean_residual'] / fit['radius'] if fit['radius'] > 0 else 999
    print(f"           Cluster {c}: {rel:.3f} ({'ok' if rel < 0.30 else 'poor'})")
print(f"           → {'PASS ✓' if t3 else 'FAIL ✗'}")
passed += t3

# Test 4: Circles overlap
if len(circle_fits) >= 2:
    keys = sorted(circle_fits.keys())
    any_overlap = False
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            ci = circle_fits[keys[i]]
            cj = circle_fits[keys[j]]
            center_dist = np.linalg.norm(ci['center'] - cj['center'])
            sum_radii = ci['radius'] + cj['radius']
            if center_dist < sum_radii:
                any_overlap = True
    t4 = any_overlap
else:
    t4 = False
print(f"\n  Test  4: Circles overlap (centers closer than sum of radii)")
print(f"           → {'PASS ✓' if t4 else 'FAIL ✗'}")
passed += t4

# Test 5: Matter/middle cluster slope near φ
t5 = False
for c in range(k_test):
    mask = labels3 == c
    mean_logT = logT[mask].mean()
    if -2 <= mean_logT <= 8:  # middle cluster
        slope, _, _, _, _ = stats.linregress(logT[mask], logE[mask])
        t5 = abs(slope - PHI) < 0.25
        phi_dist = abs(slope - PHI)
        print(f"\n  Test  5: Matter cluster slope near φ")
        print(f"           Slope: {slope:.3f}, |Δφ| = {phi_dist:.3f}")
        break
if not t5:
    print(f"\n  Test  5: Matter cluster slope near φ")
print(f"           → {'PASS ✓' if t5 else 'FAIL ✗'}")
passed += t5

# Test 6: Circle radii show hierarchy (different sizes)
if len(circle_fits) >= 2:
    radii = sorted([f['radius'] for f in circle_fits.values()])
    # Check that largest is at least 1.5x smallest
    t6 = radii[-1] / radii[0] > 1.5 if radii[0] > 0 else False
    print(f"\n  Test  6: Circle radii form hierarchy")
    print(f"           Radii: {[f'{r:.2f}' for r in radii]}")
    print(f"           Ratio max/min: {radii[-1]/radii[0]:.2f}")
else:
    t6 = False
    print(f"\n  Test  6: Circle radii form hierarchy")
print(f"           → {'PASS ✓' if t6 else 'FAIL ✗'}")
passed += t6

# Test 7: Triple-overlap region exists near human scale
t7 = n_triple > 0 and abs(logT[membership_count >= 3].mean()) < 5
print(f"\n  Test  7: Triple-overlap region near human scale")
if n_triple > 0:
    print(f"           {n_triple} systems in triple overlap, mean logT = {logT[membership_count >= 3].mean():.1f}")
else:
    print(f"           No triple-overlap region found")
print(f"           → {'PASS ✓' if t7 else 'FAIL ✗'}")
passed += t7

# Test 8: Agreement with hand-classified domains > 60%
t8 = agreement_pct > 60
print(f"\n  Test  8: Agreement with hand-classified domains > 60%")
print(f"           Agreement: {agreement_pct:.1f}%")
print(f"           → {'PASS ✓' if t8 else 'FAIL ✗'}")
passed += t8

# Test 9: BIC strongly prefers 3 over 1 or 2
if 1 in results and 2 in results and 3 in results:
    bic_1 = results[1]['bic']
    bic_2 = results[2]['bic']
    bic_3 = results[3]['bic']
    t9 = bic_3 < bic_1 and bic_3 < bic_2
    print(f"\n  Test  9: BIC prefers k=3 over k=1 and k=2")
    print(f"           BIC(1)={bic_1:.1f}, BIC(2)={bic_2:.1f}, BIC(3)={bic_3:.1f}")
else:
    t9 = False
    print(f"\n  Test  9: BIC prefers k=3 over k=1 and k=2")
print(f"           → {'PASS ✓' if t9 else 'FAIL ✗'}")
passed += t9

# Test 10: Circle normals are non-parallel (distinct orientations)
if len(circle_fits) >= 2:
    keys = sorted(circle_fits.keys())
    all_distinct = True
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            cos_a = abs(np.dot(circle_fits[keys[i]]['normal'], circle_fits[keys[j]]['normal']))
            angle = np.degrees(np.arccos(np.clip(cos_a, 0, 1)))
            if angle < 10:  # less than 10° = essentially parallel
                all_distinct = False
    t10 = all_distinct
    print(f"\n  Test 10: Circle normals are non-parallel (distinct orientations)")
    for i in range(len(keys)):
        for j in range(i+1, len(keys)):
            cos_a = abs(np.dot(circle_fits[keys[i]]['normal'], circle_fits[keys[j]]['normal']))
            angle = np.degrees(np.arccos(np.clip(cos_a, 0, 1)))
            print(f"           Clusters {keys[i]}↔{keys[j]}: {angle:.1f}°")
else:
    t10 = False
    print(f"\n  Test 10: Circle normals are non-parallel")
print(f"           → {'PASS ✓' if t10 else 'FAIL ✗'}")
passed += t10

# ============================================================
# FINAL SCORE
# ============================================================
print("\n" + "=" * 70)
score = passed
print(f"  SCORE: {score} / {total}")
print("=" * 70)

# Summary
print(f"\n  SUMMARY:")
print(f"  • BIC-optimal clusters: k = {best_k}")
print(f"  • Three circles fitted: {len(circle_fits) >= 3}")
if len(circle_fits) >= 2:
    for c, fit in sorted(circle_fits.items()):
        mean_lt = logT[labels3 == c].mean()
        tag = "quantum" if mean_lt < -2 else ("planetary" if mean_lt > 8 else "matter")
        print(f"  • Cluster {c} ({tag}): radius={fit['radius']:.2f}, planarity={fit['planarity']:.3f}")
print(f"  • Agreement with hand-labels: {agreement_pct:.1f}%")
print(f"  • Triple overlap: {n_triple} systems")
print(f"\n  VERDICT: {'The data DOES naturally cluster into three overlapping circles.' if score >= 6 else 'Insufficient evidence for three natural circles.'}")
print(f"  {'Dylan is seeing real structure in the data.' if score >= 6 else 'The pattern may be imposed by the data selection.'}")
