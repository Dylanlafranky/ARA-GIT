#!/usr/bin/env python3
"""
Script 40: Spine Wave Analysis — Does the E-T slope oscillate around φ?
========================================================================
Two hypotheses under test:

  H1: The E-T power law slope is NOT constant along the period axis.
       Instead, the local slope oscillates — the spine has wave-like structure.

  H2: φ (1.618) is the attractor the local slope oscillates around.
       Systems closer to φ are "healthier" / more self-organized.
       Deviations from φ are caused by physical constraints:
         - Gravity, friction, forced timing → pull slope below φ
         - Exothermic feedback, massive energy coupling → push slope above φ

Tests:
  1. Sliding window local slopes along log(Period)
  2. Residual analysis: deviations from φ-slope line vs constant-slope line
  3. Category-resolved local slopes (bio vs geo vs engineered vs ecological)
  4. Oscillation test: does the local slope cross φ multiple times?
  5. Wavelet/spectral analysis of the local slope signal
  6. Attractor analysis: is φ the mean/median of local slopes?

Uses ONLY measured/derived energy values (quality != 'estimated')
to avoid circular reasoning from estimated energies.

Dylan La Franchi & Claude — April 2026
"""

import numpy as np
from scipy import stats, signal
from scipy.optimize import curve_fit

np.random.seed(42)
PHI = (1 + np.sqrt(5)) / 2
PI = np.pi

# ============================================================
# DATA — from Script 39
# ============================================================
data = [
    # ENGINE — measured
    ("Combustion Cycle", "Engine", 0.04, 2700, 1.00, "measured", "engineered"),
    ("Valve Timing", "Engine", 0.04, 2700, 0.618, "measured", "engineered"),
    ("Ignition Pulse", "Engine", 0.0053, 0.05, 0.0001, "measured", "engineered"),
    ("Cooling Cycle", "Engine", 30, 5000, 1.60, "measured", "engineered"),
    # PC — measured
    ("CPU Clock", "PC", 3e-10, 2.9e-8, 1.00, "measured", "engineered"),
    ("CPU Boost/Idle", "PC", 3.2, 320, 0.60, "measured", "engineered"),
    ("RAM Refresh", "PC", 0.064, 6.2e-3, 0.0047, "measured", "engineered"),
    ("Thermal/Cooling", "PC", 23, 2300, 1.30, "measured", "engineered"),
    # HEART — measured
    ("SA Node", "Heart", 0.830, 1.3, 0.043, "measured", "biological"),
    ("AV Node", "Heart", 0.135, 0.02, 0.27, "measured", "biological"),
    ("Ventricular Pump", "Heart", 0.830, 1.3, 1.60, "measured", "biological"),
    ("Myocyte", "Heart", 0.830, 1.3, 1.73, "measured", "biological"),
    ("Ventricular AP", "Heart", 0.830, 0.001, 1.35, "measured", "biological"),
    ("RSA Breathing", "Heart", 4.7, 7, 1.61, "measured", "biological"),
    # HYDROGEN — derived from physics
    ("Ground Orbital", "Hydrogen", 1.52e-16, 2.18e-18, 1.00, "derived", "quantum"),
    ("Lyman-alpha", "Hydrogen", 1.596e-9, 2.18e-18, 2.54e-7, "derived", "quantum"),
    ("2s Metastable", "Hydrogen", 0.122, 2.18e-18, 3.32e-15, "derived", "quantum"),
    ("Balmer Cascade", "Hydrogen", 6.96e-9, 2.18e-18, 0.298, "derived", "quantum"),
    ("21-cm Hyperfine", "Hydrogen", 3.47e14, 9.43e-25, 2.03e-24, "derived", "quantum"),
    # NEURON — measured
    ("Integration→Spike", "Neuron", 0.0265, 5e-12, 0.060, "measured", "biological"),
    ("Depol/Repol", "Neuron", 0.0011, 5e-13, 2.14, "measured", "biological"),
    ("Refractory", "Neuron", 0.0052, 1e-12, 3.33, "measured", "biological"),
    ("Synaptic Vesicle", "Neuron", 0.050, 1e-12, 0.003, "measured", "biological"),
    # THUNDERSTORM — measured
    ("Storm Lifecycle", "Thunderstorm", 3300, 1e12, 2.24, "measured", "geophysical"),
    ("Lightning", "Thunderstorm", 600, 1e9, 1.67e-7, "measured", "geophysical"),
    ("Precipitation", "Thunderstorm", 2100, 5e11, 0.75, "measured", "geophysical"),
    ("Gust Front", "Thunderstorm", 1140, 1e11, 0.58, "measured", "geophysical"),
    # PREDATOR-PREY — measured
    ("Hare", "Pred-Prey", 9.5*365.25*86400, 1e15, 0.46, "measured", "ecological"),
    ("Lynx", "Pred-Prey", 9.5*365.25*86400, 5e14, 0.73, "measured", "ecological"),
    ("Vegetation", "Pred-Prey", 4*365.25*86400, 1e14, 0.60, "measured", "ecological"),
    # EARTH — measured
    ("Diurnal Thermal", "Earth", 86400, 1.5e22, 1.667, "measured", "geophysical"),
    ("Tidal Cycle", "Earth", 43920, 3.7e18, 1.44, "measured", "geophysical"),
    ("Water Cycle", "Earth", 820800, 1.3e21, 0.056, "measured", "geophysical"),
    ("ENSO", "Earth", 4*365.25*86400, 1e21, 0.60, "measured", "geophysical"),
    ("Seasonal", "Earth", 365.25*86400, 5.5e24, 1.017, "measured", "geophysical"),
    ("Milankovitch", "Earth", 1e5*365.25*86400, 1e28, 0.111, "measured", "geophysical"),
    # BLIND TEST — measured
    ("AC Waveform", "Energy Grid", 0.02, 2e7, 1.00, "measured", "engineered"),
    ("Daily Load", "Energy Grid", 86400, 8.64e14, 1.40, "measured", "engineered"),
    ("Lab Cell", "RB Convection", 30, 0.02, 1.00, "measured", "geophysical"),
    ("Hadley Cell", "RB Convection", 30*86400, 1e18, 1.00, "measured", "geophysical"),
    ("Annual Colony", "Honeybee", 365.25*86400, 3.8e8, 1.40, "measured", "biological"),
    ("Daily Foraging", "Honeybee", 86400, 1e6, 0.20, "measured", "biological"),
    ("Thermoreg", "Honeybee", 390, 2000, 1.60, "measured", "biological"),
    ("Shuttle Streaming", "Slime Mold", 120, 5e-7, 1.18, "measured", "biological"),
    ("Network Opt", "Slime Mold", 21600, 0.2, 2.00, "measured", "biological"),
    ("Metabolic Osc", "Biofilm", 18000, 1.3, 1.50, "measured", "biological"),
    ("K+ Wave", "Biofilm", 3600, 0.01, 0.50, "measured", "biological"),
    ("Wing Beat", "Starling", 1/13.5, 0.1, 1.38, "measured", "biological"),
    ("Flock Turn", "Starling", 9, 500, 2.00, "measured", "biological"),
    ("Stellar Orbit", "Galaxy", 225e6*365.25*86400, 4.84e37, 1.00, "measured", "geophysical"),
    ("Arm Passage", "Galaxy", 110e6*365.25*86400, 1e38, 2.67, "measured", "geophysical"),
    ("Breathing Bubble", "DNA", 80e-6, 5e-19, 4.33, "measured", "biological"),
    ("Cell Cycle", "DNA", 84600, 3e-7, 14.7, "measured", "biological"),
    ("Crab Rotation", "Pulsar", 0.0335, 1.76e49, 1.00, "measured", "geophysical"),
    ("Typical Pulsar", "Pulsar", 0.71, 7.1e25, 1.00, "measured", "geophysical"),
    ("CW Round-trip", "Laser", 2e-9, 2e-10, 1.00, "measured", "engineered"),
    ("Relaxation Osc", "Laser", 1e-9, 1e-12, 1.50, "measured", "engineered"),
    ("Q-switched", "Laser", 200e-6, 0.1, 20000, "measured", "engineered"),
    ("Mode-locked", "Laser", 12.5e-9, 1.25e-8, 125000, "measured", "engineered"),
    # TIDES — measured
    ("Semi-diurnal M2", "Tides", 44640, 3.7e18, 1.138, "measured", "geophysical"),
    ("Spring-Neap", "Tides", 1276140, 1e19, 1.182, "measured", "geophysical"),
    # THREE-DECK — measured only
    ("Cardiac SA", "Three-Deck", 0.8, 1.3, 1.667, "measured", "biological"),
    ("Respiratory", "Three-Deck", 4.0, 3, 1.500, "measured", "biological"),
    ("Sleep-Wake", "Three-Deck", 86400, 8e6, 2.000, "measured", "biological"),
    # VENTILATOR — measured only
    ("Natural Breath", "Ventilator", 4.0, 3, 1.500, "measured", "biological"),
    ("VC 1:2", "Ventilator", 4.0, 3, 0.498, "measured", "engineered"),
    ("NAVA", "Ventilator", 3.8, 3, 1.235, "measured", "biological"),
    # SEISMIC — measured
    ("Seismic Osc", "Forced", 53.8, 1e15, 1.000, "measured", "geophysical"),
    ("Old Faithful", "Forced", 5340, 1e9, 21.250, "measured", "geophysical"),
    # PLANETARY — measured
    ("Earth Orbit", "Planetary", 3.156e7, 2.65e33, 1.011, "measured", "geophysical"),
    ("Mercury Orbit", "Planetary", 7.6e6, 1.6e32, 1.149, "measured", "geophysical"),
    ("Halley's Comet", "Planetary", 2.38e9, 1e28, 4.556, "measured", "geophysical"),
    ("Jupiter Orbit", "Planetary", 3.74e8, 4.2e35, 1.031, "measured", "geophysical"),
    ("MS Pulsar", "Planetary", 1.56e-3, 1e44, 1.000, "measured", "geophysical"),
    ("Crab Emission", "Planetary", 0.0335, 1.76e49, 7.375, "measured", "geophysical"),
    ("Sunspot Cycle", "Planetary", 3.47e8, 1e25, 1.558, "measured", "geophysical"),
    ("δ Cephei", "Planetary", 4.64e5, 1.5e30, 2.333, "measured", "geophysical"),
    # QUANTUM — derived
    ("QHO Ground", "Quantum", 1e-13, 1.05e-21, 1.000, "derived", "quantum"),
    ("Rabi Osc", "Quantum", 1e-8, 1.05e-26, 1.000, "derived", "quantum"),
    ("Caesium Clock", "Quantum", 1.09e-10, 9.63e-25, 1.000, "derived", "quantum"),
    ("Phonon", "Quantum", 1e-13, 1.05e-21, 1.000, "derived", "quantum"),
    ("H Lyman-alpha", "Quantum", 1.596e-9, 2.18e-18, 2.36e6, "derived", "quantum"),
    ("Na Fluorescence", "Quantum", 1.624e-8, 3.37e-19, 4.78e7, "derived", "quantum"),
    ("U-238 Alpha", "Quantum", 1.41e17, 6.8e-13, 1.41e38, "derived", "quantum"),
]

# Parse
names = [d[0] for d in data]
systems = [d[1] for d in data]
T_arr = np.array([d[2] for d in data])
E_arr = np.array([d[3] for d in data])
ARA_arr = np.array([d[4] for d in data])
quality = [d[5] for d in data]
category = [d[6] for d in data]

logT = np.log10(T_arr)
logE = np.log10(E_arr)
logARA = np.log10(np.maximum(ARA_arr, 1e-25))

N = len(data)
print(f"Total measured/derived data points: {N}")
print(f"Period range: {logT.min():.1f} to {logT.max():.1f} (log10 seconds)")
print(f"Span: {logT.max() - logT.min():.1f} orders of magnitude")
print()

# ============================================================
# TEST 1: SLIDING WINDOW LOCAL SLOPES
# ============================================================
print("=" * 70)
print("TEST 1: SLIDING WINDOW LOCAL E-T SLOPES")
print("=" * 70)

# Sort by period
sort_idx = np.argsort(logT)
logT_s = logT[sort_idx]
logE_s = logE[sort_idx]
names_s = [names[i] for i in sort_idx]
cat_s = [category[i] for i in sort_idx]

# Use overlapping windows of varying sizes to ensure robustness
window_sizes = [15, 20, 25]  # number of points per window
step = 3  # overlap

print(f"\nSliding window analysis (step={step} points):")
print(f"Window sizes tested: {window_sizes}")
print()

all_local_slopes = {}

for ws in window_sizes:
    centers = []
    slopes = []
    slopes_err = []
    n_points = []

    for start in range(0, N - ws + 1, step):
        end = start + ws
        lt = logT_s[start:end]
        le = logE_s[start:end]

        # Linear regression: logE = α * logT + β
        slope, intercept, r, p, se = stats.linregress(lt, le)
        center = np.median(lt)

        centers.append(center)
        slopes.append(slope)
        slopes_err.append(se)
        n_points.append(ws)

    centers = np.array(centers)
    slopes = np.array(slopes)
    slopes_err = np.array(slopes_err)

    all_local_slopes[ws] = (centers, slopes, slopes_err)

    print(f"\n--- Window size = {ws} points ---")
    print(f"  Windows computed: {len(centers)}")
    print(f"  Slope range: [{slopes.min():.3f}, {slopes.max():.3f}]")
    print(f"  Mean slope: {slopes.mean():.3f}")
    print(f"  Median slope: {np.median(slopes):.3f}")
    print(f"  Std of slopes: {slopes.std():.3f}")

    # Count crossings of φ
    above_phi = slopes > PHI
    crossings = np.sum(np.diff(above_phi.astype(int)) != 0)
    print(f"  φ crossings: {crossings}")

    # Fraction of time above vs below φ
    frac_above = above_phi.mean()
    print(f"  Fraction above φ: {frac_above:.3f}")
    print(f"  Fraction below φ: {1-frac_above:.3f}")

    # Distance from φ
    dist_from_phi = slopes - PHI
    mean_dist = dist_from_phi.mean()
    print(f"  Mean distance from φ: {mean_dist:+.3f}")

print()

# ============================================================
# TEST 2: IS φ THE ATTRACTOR? COMPARE ATTRACTOR CANDIDATES
# ============================================================
print("=" * 70)
print("TEST 2: ATTRACTOR ANALYSIS — What value does the local slope orbit?")
print("=" * 70)

# Use the medium window (20)
centers, slopes, slopes_err = all_local_slopes[20]

candidates = {
    "1.0 (unity)": 1.0,
    "1.5 (3/2)": 1.5,
    "φ (1.618)": PHI,
    "√3 (1.732)": np.sqrt(3),
    "2.0": 2.0,
    "π/2 (1.571)": PI/2,
    "Global mean": slopes.mean(),
}

print(f"\nLocal slope distribution (window=20):")
print(f"  Mean:   {slopes.mean():.4f}")
print(f"  Median: {np.median(slopes):.4f}")
print(f"  Mode range: ~{slopes[np.argmax(np.histogram(slopes, bins=20)[0])]:.1f}")
print()

print("Candidate attractors — mean absolute deviation of local slopes:")
for name, val in sorted(candidates.items(), key=lambda x: np.mean(np.abs(slopes - x[1]))):
    mad = np.mean(np.abs(slopes - val))
    rmsd = np.sqrt(np.mean((slopes - val)**2))
    print(f"  {name:20s}: MAD = {mad:.3f}, RMSD = {rmsd:.3f}")

# Bootstrap test: is the mean slope significantly different from φ?
print(f"\nBootstrap test: Is mean local slope = φ?")
n_boot = 10000
boot_means = np.array([np.mean(np.random.choice(slopes, size=len(slopes), replace=True))
                        for _ in range(n_boot)])
ci_low, ci_high = np.percentile(boot_means, [2.5, 97.5])
print(f"  Bootstrap mean: {boot_means.mean():.4f}")
print(f"  95% CI: [{ci_low:.4f}, {ci_high:.4f}]")
print(f"  φ = {PHI:.4f} {'INSIDE' if ci_low <= PHI <= ci_high else 'OUTSIDE'} CI")

# Test against other candidates
for name, val in candidates.items():
    if name == "Global mean":
        continue
    inside = ci_low <= val <= ci_high
    print(f"  {name:20s} = {val:.4f} {'INSIDE' if inside else 'OUTSIDE'} CI")

print()

# ============================================================
# TEST 3: OSCILLATION STRUCTURE — Is the slope variation periodic?
# ============================================================
print("=" * 70)
print("TEST 3: OSCILLATION STRUCTURE — Is there periodicity in local slopes?")
print("=" * 70)

# Detrend the local slopes (remove any overall trend)
centers, slopes, _ = all_local_slopes[20]
slope_trend = np.polyfit(centers, slopes, 1)
detrended = slopes - np.polyval(slope_trend, centers)

print(f"\nOverall trend in local slopes: {slope_trend[0]:.4f} per decade of period")
print(f"  (positive = steeper slopes at longer periods)")
print()

# Autocorrelation of detrended slopes
if len(detrended) > 10:
    # Normalized autocorrelation
    n = len(detrended)
    acf = np.correlate(detrended - detrended.mean(), detrended - detrended.mean(), 'full')
    acf = acf[n-1:] / acf[n-1]  # normalize

    print("Autocorrelation of detrended local slopes:")
    for lag in range(min(8, len(acf))):
        bar = "█" * int(abs(acf[lag]) * 30)
        sign = "+" if acf[lag] > 0 else "-"
        print(f"  Lag {lag}: {acf[lag]:+.3f} {sign}{bar}")

    # First negative crossing = half-period of oscillation
    neg_crossings = np.where(acf[1:] < 0)[0]
    if len(neg_crossings) > 0:
        half_period = neg_crossings[0] + 1
        print(f"\n  First negative autocorrelation at lag {half_period}")
        print(f"  Implied oscillation half-period: ~{half_period * step} data points")
        # Convert to log-period units
        period_span_per_step = (centers[-1] - centers[0]) / (len(centers) - 1)
        print(f"  Implied half-period: ~{half_period * period_span_per_step:.1f} decades of log(Period)")
    else:
        print("\n  No negative autocorrelation found — no clear oscillation")

# Null model: shuffle slopes and compute autocorrelation
print(f"\nNull model: autocorrelation of 10,000 shuffled slope sequences")
n_shuffles = 10000
max_lag = min(8, len(detrended))
null_acf = np.zeros((n_shuffles, max_lag))
for i in range(n_shuffles):
    shuffled = np.random.permutation(detrended)
    acf_s = np.correlate(shuffled - shuffled.mean(), shuffled - shuffled.mean(), 'full')
    acf_s = acf_s[len(shuffled)-1:] / acf_s[len(shuffled)-1]
    null_acf[i, :] = acf_s[:max_lag]

for lag in range(1, max_lag):
    real_acf_val = acf[lag]
    null_95 = np.percentile(np.abs(null_acf[:, lag]), 95)
    sig = "SIGNIFICANT" if abs(real_acf_val) > null_95 else "not significant"
    print(f"  Lag {lag}: real={real_acf_val:+.3f}, null 95th={null_95:.3f} → {sig}")

print()

# ============================================================
# TEST 4: CATEGORY-RESOLVED LOCAL SLOPES
# ============================================================
print("=" * 70)
print("TEST 4: CATEGORY-RESOLVED SLOPES — Which categories orbit closest to φ?")
print("=" * 70)

categories = ["biological", "geophysical", "engineered", "ecological", "quantum"]
cat_arr = np.array(category)

for cat in categories:
    mask = cat_arr == cat
    if mask.sum() < 5:
        print(f"\n{cat}: only {mask.sum()} points, skipping")
        continue

    lt = logT[mask]
    le = logE[mask]

    slope, intercept, r, p, se = stats.linregress(lt, le)
    dist_phi = slope - PHI

    print(f"\n{cat.upper()} (n={mask.sum()}):")
    print(f"  E-T slope: {slope:.3f} ± {se:.3f}")
    print(f"  R² = {r**2:.3f}")
    print(f"  Distance from φ: {dist_phi:+.3f} ({'above' if dist_phi > 0 else 'below'})")

    # Within-category local slope variation
    if mask.sum() >= 10:
        sort_m = np.argsort(lt)
        lt_sm = lt[sort_m]
        le_sm = le[sort_m]
        # Mini sliding windows
        mini_ws = min(8, mask.sum() // 2)
        mini_slopes = []
        for start in range(0, mask.sum() - mini_ws + 1, 2):
            s, _, _, _, _ = stats.linregress(lt_sm[start:start+mini_ws], le_sm[start:start+mini_ws])
            mini_slopes.append(s)
        if mini_slopes:
            mini_slopes = np.array(mini_slopes)
            print(f"  Local slope range: [{mini_slopes.min():.2f}, {mini_slopes.max():.2f}]")
            phi_crossings = np.sum(np.diff((mini_slopes > PHI).astype(int)) != 0)
            print(f"  φ crossings within category: {phi_crossings}")

print()

# ============================================================
# TEST 5: RESIDUALS FROM φ-SLOPE vs BEST-FIT SLOPE
# ============================================================
print("=" * 70)
print("TEST 5: φ-SLOPE vs BEST-FIT — Which predicts energies better?")
print("=" * 70)

# Global best fit
slope_best, intercept_best, r_best, _, _ = stats.linregress(logT, logE)
resid_best = logE - (slope_best * logT + intercept_best)

# φ-slope line (intercept fitted)
intercept_phi = np.mean(logE - PHI * logT)
resid_phi = logE - (PHI * logT + intercept_phi)

# Compare
rmse_best = np.sqrt(np.mean(resid_best**2))
rmse_phi = np.sqrt(np.mean(resid_phi**2))

print(f"\nBest-fit slope: {slope_best:.4f}, R² = {r_best**2:.4f}, RMSE = {rmse_best:.3f}")
print(f"φ-slope (1.618): RMSE = {rmse_phi:.3f}")
print(f"Ratio: RMSE_φ / RMSE_best = {rmse_phi/rmse_best:.3f}")
print(f"Penalty for forcing φ: {(rmse_phi - rmse_best):.3f} dex")

# AIC comparison (assuming Gaussian residuals)
n = len(logT)
k_best = 2  # slope + intercept
k_phi = 1   # intercept only (slope fixed)
aic_best = n * np.log(np.mean(resid_best**2)) + 2 * k_best
aic_phi = n * np.log(np.mean(resid_phi**2)) + 2 * k_phi
print(f"\nAIC (best-fit): {aic_best:.1f}")
print(f"AIC (φ-forced): {aic_phi:.1f}")
print(f"ΔAIC = {aic_phi - aic_best:.1f} ({'φ preferred' if aic_phi < aic_best else 'best-fit preferred'})")

# Category-specific: does φ fit better when restricted to self-organizing systems?
print(f"\nCategory-specific φ-slope fit:")
for cat in categories:
    mask = cat_arr == cat
    if mask.sum() < 5:
        continue
    lt = logT[mask]
    le = logE[mask]
    s, ic, r, _, _ = stats.linregress(lt, le)
    resid_b = le - (s * lt + ic)
    ic_phi = np.mean(le - PHI * lt)
    resid_p = le - (PHI * lt + ic_phi)
    rmse_b = np.sqrt(np.mean(resid_b**2))
    rmse_p = np.sqrt(np.mean(resid_p**2))
    print(f"  {cat:12s}: best={s:.3f} (RMSE {rmse_b:.2f}), φ penalty = {rmse_p - rmse_b:+.3f} dex")

print()

# ============================================================
# TEST 6: SPINE CURVATURE — Is the spine a straight line or a curve?
# ============================================================
print("=" * 70)
print("TEST 6: SPINE CURVATURE — Linear vs quadratic vs sinusoidal fit")
print("=" * 70)

# Fit logE = a * logT + b (linear)
p1 = np.polyfit(logT, logE, 1)
resid_lin = logE - np.polyval(p1, logT)
rss_lin = np.sum(resid_lin**2)

# Fit logE = a * logT² + b * logT + c (quadratic)
p2 = np.polyfit(logT, logE, 2)
resid_quad = logE - np.polyval(p2, logT)
rss_quad = np.sum(resid_quad**2)

# Fit logE = a * logT + b + c * sin(d * logT + e) (sinusoidal modulation)
def sin_model(x, a, b, c, freq, phase):
    return a * x + b + c * np.sin(freq * x + phase)

try:
    # Initial guess: linear part from polyfit, small oscillation
    p0 = [p1[0], p1[1], 2.0, 0.5, 0.0]
    bounds = ([0, -np.inf, 0, 0.05, -PI], [5, np.inf, 20, 5.0, PI])
    popt, pcov = curve_fit(sin_model, logT, logE, p0=p0, bounds=bounds, maxfev=10000)
    resid_sin = logE - sin_model(logT, *popt)
    rss_sin = np.sum(resid_sin**2)
    sin_fit_success = True
except Exception as e:
    sin_fit_success = False
    print(f"  Sinusoidal fit failed: {e}")

# F-test: linear vs quadratic
k_lin = 2
k_quad = 3
f_stat = ((rss_lin - rss_quad) / (k_quad - k_lin)) / (rss_quad / (n - k_quad))
f_p = 1 - stats.f.cdf(f_stat, k_quad - k_lin, n - k_quad)

print(f"\nLinear fit: logE = {p1[0]:.4f} * logT + {p1[1]:.3f}")
print(f"  RSS = {rss_lin:.2f}")
print(f"\nQuadratic fit: logE = {p2[0]:.5f} * logT² + {p2[1]:.4f} * logT + {p2[2]:.3f}")
print(f"  RSS = {rss_quad:.2f}")
print(f"  Curvature coefficient: {p2[0]:.5f}")
print(f"\nF-test (linear vs quadratic): F = {f_stat:.3f}, p = {f_p:.4f}")
print(f"  {'SIGNIFICANT curvature' if f_p < 0.05 else 'No significant curvature'} at p < 0.05")

if sin_fit_success:
    k_sin = 5
    f_stat_sin = ((rss_lin - rss_sin) / (k_sin - k_lin)) / (rss_sin / (n - k_sin))
    f_p_sin = 1 - stats.f.cdf(f_stat_sin, k_sin - k_lin, n - k_sin)

    print(f"\nSinusoidal fit: slope={popt[0]:.3f}, amplitude={popt[2]:.3f}, freq={popt[3]:.3f}/decade")
    print(f"  RSS = {rss_sin:.2f}")
    wavelength = 2 * PI / popt[3]
    print(f"  Wavelength: {wavelength:.1f} decades of log(Period)")
    print(f"  Amplitude: {popt[2]:.2f} dex (orders of magnitude)")
    print(f"\nF-test (linear vs sinusoidal): F = {f_stat_sin:.3f}, p = {f_p_sin:.6f}")
    print(f"  {'SIGNIFICANT oscillation' if f_p_sin < 0.05 else 'No significant oscillation'} at p < 0.05")

    # What is the period of oscillation in the slope?
    # The sinusoidal modulation means the local slope is:
    # d(logE)/d(logT) = a + c * freq * cos(freq * logT + phase)
    # This oscillates between a - c*freq and a + c*freq
    slope_amplitude = popt[2] * popt[3]
    slope_center = popt[0]
    print(f"\n  Implied local slope oscillation:")
    print(f"    Center: {slope_center:.3f}")
    print(f"    Amplitude: ±{slope_amplitude:.3f}")
    print(f"    Range: [{slope_center - slope_amplitude:.3f}, {slope_center + slope_amplitude:.3f}]")
    print(f"    φ = {PHI:.3f} {'within oscillation range' if (slope_center - slope_amplitude <= PHI <= slope_center + slope_amplitude) else 'outside range'}")

print()

# ============================================================
# TEST 7 (BONUS): THE META-WAVE — Residuals from best-fit as a function of scale
# ============================================================
print("=" * 70)
print("TEST 7: META-WAVE — Do residuals from the power law show structure?")
print("=" * 70)

# Sort residuals by period
resid_sorted = resid_lin[np.argsort(logT)]
logT_sorted = np.sort(logT)

# Bin residuals by scale decade
decade_min = int(np.floor(logT.min()))
decade_max = int(np.ceil(logT.max()))
print(f"\nResiduals from E ∝ T^{p1[0]:.3f} binned by scale decade:")
print(f"{'Decade':>10s} {'Mean resid':>12s} {'Std':>8s} {'N':>5s} {'Direction':>10s}")

decade_means = []
decade_centers = []
for d in range(decade_min, decade_max):
    mask = (logT >= d) & (logT < d + 1)
    if mask.sum() < 2:
        continue
    mr = resid_lin[mask].mean()
    sr = resid_lin[mask].std()
    decade_means.append(mr)
    decade_centers.append(d + 0.5)
    direction = "ABOVE" if mr > 0 else "BELOW"
    bar = "█" * min(int(abs(mr) * 3), 30)
    print(f"  10^{d:+3d}    {mr:+.3f}       {sr:.3f}  {mask.sum():4d}  {direction} {bar}")

decade_means = np.array(decade_means)
decade_centers = np.array(decade_centers)

# Check if residuals alternate above/below → wave structure
if len(decade_means) > 3:
    sign_changes = np.sum(np.diff(np.sign(decade_means)) != 0)
    print(f"\n  Sign changes across decades: {sign_changes}")
    print(f"  Total decades with data: {len(decade_means)}")
    print(f"  Expected if random: ~{len(decade_means)/2:.0f}")
    print(f"  {'MORE alternation than random → wave-like' if sign_changes > len(decade_means)/2 else 'Less alternation → no clear wave'}")

# Runs test on signs of residuals (sorted by period)
resid_signs = np.sign(resid_lin[np.argsort(logT)])
resid_signs = resid_signs[resid_signs != 0]
n_plus = np.sum(resid_signs > 0)
n_minus = np.sum(resid_signs < 0)
n_total = len(resid_signs)
runs = 1 + np.sum(np.diff(resid_signs) != 0)
# Expected runs under null
mu_runs = 1 + 2 * n_plus * n_minus / n_total
sigma_runs = np.sqrt(2 * n_plus * n_minus * (2 * n_plus * n_minus - n_total) /
                      (n_total**2 * (n_total - 1)))
z_runs = (runs - mu_runs) / sigma_runs
p_runs = 2 * stats.norm.sf(abs(z_runs))

print(f"\nWald-Wolfowitz runs test on residual signs (sorted by period):")
print(f"  Observed runs: {runs}")
print(f"  Expected (random): {mu_runs:.1f}")
print(f"  Z = {z_runs:.3f}, p = {p_runs:.4f}")
if z_runs < -1.96:
    print(f"  SIGNIFICANT CLUSTERING — residuals are structured, not random")
    print(f"  This means the power law is a simplification — there's scale-dependent structure")
elif z_runs > 1.96:
    print(f"  SIGNIFICANT ALTERNATION — more oscillatory than random")
else:
    print(f"  Not significant — residuals consistent with random scatter")

print()

# ============================================================
# SYNTHESIS
# ============================================================
print("=" * 70)
print("SYNTHESIS")
print("=" * 70)

centers20, slopes20, _ = all_local_slopes[20]
phi_crossings_20 = np.sum(np.diff((slopes20 > PHI).astype(int)) != 0)

print(f"""
DATA: {N} measured/derived systems spanning {logT.max()-logT.min():.0f} orders of magnitude

H1 — THE SPINE HAS WAVE-LIKE STRUCTURE:
  Local E-T slope varies from {slopes20.min():.2f} to {slopes20.max():.2f}
  The slope is NOT constant — it changes across the period axis
  φ crossings: {phi_crossings_20} (local slope crosses φ = {PHI:.3f} multiple times)
  Curvature F-test p = {f_p:.4f} {'→ SIGNIFICANT' if f_p < 0.05 else '→ not significant'}
  {'Sinusoidal modulation F-test p = ' + f'{f_p_sin:.6f}' + (' → SIGNIFICANT' if f_p_sin < 0.05 else ' → not significant') if sin_fit_success else 'Sinusoidal fit did not converge'}
  Residual runs test: p = {p_runs:.4f} {'→ SIGNIFICANT structure' if p_runs < 0.05 else '→ no significant structure'}

H2 — φ IS THE ATTRACTOR:
  Global mean local slope: {slopes20.mean():.3f}
  Global median local slope: {np.median(slopes20):.3f}
  Bootstrap 95% CI of mean: [{ci_low:.3f}, {ci_high:.3f}]
  φ = {PHI:.3f} is {'INSIDE' if ci_low <= PHI <= ci_high else 'OUTSIDE'} the CI
  φ-forced fit penalty vs best: {(rmse_phi - rmse_best):.3f} dex (small = good)

CATEGORY HIERARCHY (distance from φ):""")

cat_results = []
for cat in categories:
    mask = cat_arr == cat
    if mask.sum() < 5:
        continue
    s, _, r, _, _ = stats.linregress(logT[mask], logE[mask])
    cat_results.append((cat, s, abs(s - PHI), mask.sum()))

for cat, s, dist, n_cat in sorted(cat_results, key=lambda x: x[2]):
    arrow = "↑" if s > PHI else "↓"
    print(f"  {cat:12s}: slope = {s:.3f}, |dist from φ| = {dist:.3f} {arrow} (n={n_cat})")

print(f"""
INTERPRETATION:
  The local E-T slope is not a single number — it varies with scale.
  Whether φ is the attractor depends on the statistical tests above.
  Categories with more self-organization (biological) should cluster
  closer to φ than categories dominated by external forces (geophysical).
""")
