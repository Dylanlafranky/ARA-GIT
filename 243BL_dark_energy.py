#!/usr/bin/env python3
"""
Script 243BL — Dark Energy Validation via ARA Geometry

Theory (Paper 7): The universe's expansion history IS an ARA transition.
  - Singularity: ARA → ∞ (pure accumulation)
  - Matter era:  ARA > 1 (gravity winning, structures form)
  - Transition:  ARA = 1 (balanced at z ≈ 0.67)
  - Current:     ARA < 1 (dark energy winning, accelerating)
  - Heat death:  ARA → 0 (pure release)

KEY TESTS:
  1. Does ARA = φ^(2q) map the deceleration parameter correctly?
  2. Does the framework predict Ωde ≈ 1 - 1/φ² (0.382)?
  3. Can a φ-parameterized H(z) compete with ΛCDM?
  4. Does the transition redshift z_trans map to ARA = 1?
  5. Is there a φ-wave signature in H(z) residuals?

Data: Published H(z) from cosmic chronometers + BAO (41 measurements)
"""

import numpy as np
import math
import time as clock_time

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
TAU = 2 * math.pi

# ════════════════════════════════════════════════════════════════
# COSMOLOGICAL DATA — H(z) measurements
# ════════════════════════════════════════════════════════════════

# Published H(z) from cosmic chronometers (CC) and BAO
H_Z_DATA = [
    # Cosmic chronometers (differential age method)
    (0.07,  69.0,   19.6, "CC"),
    (0.09,  69.0,   12.0, "CC"),
    (0.12,  68.6,   26.2, "CC"),
    (0.17,  83.0,    8.0, "CC"),
    (0.179, 75.0,    4.0, "CC"),
    (0.199, 75.0,    5.0, "CC"),
    (0.20,  72.9,   29.6, "CC"),
    (0.27,  77.0,   14.0, "CC"),
    (0.28,  88.8,   36.6, "CC"),
    (0.352, 83.0,   14.0, "CC"),
    (0.3802,83.0,   13.5, "CC"),
    (0.4,   95.0,   17.0, "CC"),
    (0.4004,77.0,   10.2, "CC"),
    (0.4247,87.1,   11.2, "CC"),
    (0.4497,92.8,   12.9, "CC"),
    (0.47,  89.0,   49.6, "CC"),
    (0.4783,80.9,    9.0, "CC"),
    (0.48,  97.0,   62.0, "CC"),
    (0.593, 104.0,  13.0, "CC"),
    (0.68,  92.0,    8.0, "CC"),
    (0.781, 105.0,  12.0, "CC"),
    (0.875, 125.0,  17.0, "CC"),
    (0.88,  90.0,   40.0, "CC"),
    (0.9,   117.0,  23.0, "CC"),
    (1.037, 154.0,  20.0, "CC"),
    (1.3,   168.0,  17.0, "CC"),
    (1.363, 160.0,  33.6, "CC"),
    (1.43,  177.0,  18.0, "CC"),
    (1.53,  140.0,  14.0, "CC"),
    (1.75,  202.0,  40.0, "CC"),
    (1.965, 186.5,  50.4, "CC"),
    # BAO measurements
    (0.24,  79.7,    2.7, "BAO"),
    (0.35,  84.4,    7.0, "BAO"),
    (0.43,  86.5,    3.7, "BAO"),
    (0.44,  82.6,    7.8, "BAO"),
    (0.57,  96.8,    3.4, "BAO"),
    (0.6,   87.9,    6.1, "BAO"),
    (0.73,  97.3,    7.0, "BAO"),
    (2.33,  224.0,   8.6, "BAO"),
    (2.34,  222.0,   7.0, "BAO"),
    (2.36,  226.0,   8.0, "BAO"),
]

H_Z_DATA.sort(key=lambda x: x[0])
hz_z = np.array([d[0] for d in H_Z_DATA])
hz_H = np.array([d[1] for d in H_Z_DATA])
hz_err = np.array([d[2] for d in H_Z_DATA])
N = len(hz_z)


# ════════════════════════════════════════════════════════════════
# ΛCDM MODEL — the standard prediction
# ════════════════════════════════════════════════════════════════

H0_planck = 67.4
Omega_m_planck = 0.315
Omega_de_planck = 1.0 - Omega_m_planck

def H_LCDM(z, h0=H0_planck, om=Omega_m_planck):
    return h0 * math.sqrt(om * (1 + z)**3 + (1 - om))

def q_LCDM(z, om=Omega_m_planck):
    Ez2 = om * (1 + z)**3 + (1 - om)
    return 0.5 * (3 * om * (1 + z)**3 / Ez2 - 1)

z_trans_lcdm = (2 * Omega_de_planck / Omega_m_planck) ** (1.0/3) - 1

lcdm_preds = np.array([H_LCDM(z) for z in hz_z])
lcdm_residuals = hz_H - lcdm_preds
lcdm_mae = np.mean(np.abs(lcdm_residuals))
lcdm_wmae = np.sum(np.abs(lcdm_residuals) / hz_err) / np.sum(1.0 / hz_err)
lcdm_chi2 = np.sum((lcdm_residuals / hz_err)**2)
lcdm_chi2_red = lcdm_chi2 / (N - 2)  # H0 + Omega_m = 2 params

print("=" * 90)
print("  Script 243BL — Dark Energy Validation via ARA Geometry")
print("  Theory: Universe expansion = ARA transition from ∞ → 0")
print("=" * 90)
print(f"\n  Data: {N} H(z) measurements, z = {hz_z[0]:.2f} to {hz_z[-1]:.2f}")
print(f"  ΛCDM: H₀={H0_planck}, Ωm={Omega_m_planck}, Ωde={Omega_de_planck:.3f}")
print(f"  ΛCDM MAE = {lcdm_mae:.2f}, χ²/dof = {lcdm_chi2_red:.2f}")
print(f"  ΛCDM transition: z_trans = {z_trans_lcdm:.3f}")


# ════════════════════════════════════════════════════════════════
# TEST 1: ARA MAPPING — q(z) → ARA via φ-power
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  TEST 1: ARA = φ^(2q) — Universe ARA Evolution")
print(f"{'═' * 90}")

def q_to_ara(q):
    """φ-power mapping: ARA = φ^(2q)"""
    return PHI ** (2 * q)

# ARA at key epochs
print(f"\n  {'Epoch':25s} │ {'z':>6} │ {'q(z)':>7} │ {'ARA':>7} │ {'Type':>15} │ {'φ-rungs':>8}")
print(f"  {'─'*25}─┼─{'─'*6}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*15}─┼─{'─'*8}")

epochs = [
    ("De Sitter limit",        -1,    -1.0),
    ("Current epoch",          0.0,   None),
    ("Recent past z=0.3",      0.3,   None),
    ("★ Transition (q=0)",     None,  0.0),
    ("Structure formation z=1",1.0,   None),
    ("Early matter z=3",       3.0,   None),
    ("Deep matter z=10",       10.0,  None),
    ("Recombination z=1089",   1089,  None),
    ("Einstein–de Sitter",     -1,    0.5),
]

for name, z, q in epochs:
    if q is None:
        q = q_LCDM(z)
    if z is None:
        z = z_trans_lcdm
    ara = q_to_ara(q)
    ara_c = max(0.001, min(100, ara))
    phi_rungs = math.log(ara_c) / math.log(PHI) if ara_c > 0.001 else -99
    if ara >= PHI:
        role = "ENGINE"
    elif ara >= 1.0:
        role = "near-clock"
    elif ara >= INV_PHI:
        role = "consumer"
    else:
        role = "deep consumer"
    print(f"  {name:25s} │ {z:>6.1f} │ {q:>+7.3f} │ {ara_c:>7.3f} │ {role:>15} │ {phi_rungs:>+8.3f}")

# Current universe ARA
q0 = q_LCDM(0)
ara_now = q_to_ara(q0)
print(f"\n  Current universe: q₀ = {q0:+.4f}, ARA = {ara_now:.4f}")
print(f"  φ-distance from clock: {abs(math.log(ara_now)/math.log(PHI)):.4f} rungs")
print(f"  ARA(now) / (1/φ) = {ara_now * PHI:.4f} ← how close to 1/φ?")


# ════════════════════════════════════════════════════════════════
# TEST 2: φ-PARAMETERIZED COSMOLOGY
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  TEST 2: φ-Parameterized H(z) Models")
print(f"  Can Ωm built from φ-powers match the data?")
print(f"{'═' * 90}")

def fit_H0_for_omega(om, z_data, H_data, H_err):
    """Best-fit H0 for a given Omega_m, minimizing weighted chi²."""
    E_z = np.array([math.sqrt(om * (1+z)**3 + (1-om)) for z in z_data])
    w = 1.0 / H_err**2
    h0_fit = np.sum(w * H_data * E_z) / np.sum(w * E_z**2)
    preds = h0_fit * E_z
    resid = H_data - preds
    chi2 = np.sum((resid / H_err)**2)
    mae = np.mean(np.abs(resid))
    return h0_fit, mae, chi2, preds

# φ-motivated Omega_m candidates
omega_tests = [
    ("ΛCDM Planck",           Omega_m_planck),
    ("1/φ² = 0.382",          INV_PHI_2),
    ("1/φ³ = 0.236",          INV_PHI**3),
    ("2/φ³ = 0.472",          2*INV_PHI**3),
    ("1 - 1/φ = 0.382",       1 - INV_PHI),
    ("1/φ⁴ = 0.146",          INV_PHI**4),
    ("1/3 = 0.333",           1.0/3),
    ("(3-φ)/π = 0.440",       (3-PHI)/math.pi),
    ("1/(φ·π) = 0.197",       1/(PHI * math.pi)),
]

print(f"\n  {'Model':25s} │ {'Ωm':>7} │ {'Ωde':>7} │ {'H₀ fit':>7} │ {'MAE':>7} │ {'χ²/dof':>7} │ {'vs ΛCDM':>8}")
print(f"  {'─'*25}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*8}")

best_phi_model = (999, "", 0, 0, None)

for name, om in omega_tests:
    h0_fit, mae, chi2, preds = fit_H0_for_omega(om, hz_z, hz_H, hz_err)
    chi2_red = chi2 / (N - 1)  # 1 free param (H0), Omega_m fixed
    vs_lcdm = (mae - lcdm_mae) / lcdm_mae * 100
    marker = " ★" if mae <= lcdm_mae * 1.05 else ""
    print(f"  {name:25s} │ {om:>7.4f} │ {1-om:>7.4f} │ {h0_fit:>7.1f} │ {mae:>7.2f} │ {chi2_red:>7.2f} │ {vs_lcdm:>+7.1f}%{marker}")

    if mae < best_phi_model[0]:
        best_phi_model = (mae, name, om, h0_fit, preds)

print(f"\n  Best φ-model: {best_phi_model[1]} (Ωm={best_phi_model[2]:.4f})")
print(f"  H₀ = {best_phi_model[3]:.1f}, MAE = {best_phi_model[0]:.2f}")


# ════════════════════════════════════════════════════════════════
# TEST 3: SCAN Ωm CONTINUOUSLY — find true best fit and check φ proximity
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  TEST 3: Continuous Ωm Scan — Where Does φ Land?")
print(f"{'═' * 90}")

om_scan = np.linspace(0.05, 0.60, 1000)
scan_results = []
for om in om_scan:
    h0_fit, mae, chi2, _ = fit_H0_for_omega(om, hz_z, hz_H, hz_err)
    scan_results.append((om, h0_fit, mae, chi2))

scan_results = np.array(scan_results)
best_idx = np.argmin(scan_results[:, 2])
best_om = scan_results[best_idx, 0]
best_h0 = scan_results[best_idx, 1]
best_mae = scan_results[best_idx, 2]

# Find closest φ-power to best Ωm
phi_powers = {
    "1/φ²": INV_PHI_2,
    "1/φ³": INV_PHI**3,
    "2/φ³": 2*INV_PHI**3,
    "1/3": 1/3,
}
closest_phi = min(phi_powers.items(), key=lambda x: abs(x[1] - best_om))

print(f"\n  Best-fit Ωm = {best_om:.4f}, H₀ = {best_h0:.1f}, MAE = {best_mae:.2f}")
print(f"  Planck Ωm = {Omega_m_planck:.4f} (difference: {abs(best_om - Omega_m_planck):.4f})")
print(f"  Closest φ-power: {closest_phi[0]} = {closest_phi[1]:.4f} (difference: {abs(best_om - closest_phi[1]):.4f})")
print(f"  1/φ² = {INV_PHI_2:.4f} → difference from best: {abs(best_om - INV_PHI_2):.4f}")

# Check MAE at key Ωm values near the best
for om_label, om_val in [("Best fit", best_om), ("Planck", 0.315), ("1/φ²", INV_PHI_2), ("1/3", 1/3)]:
    h0_fit, mae, chi2, _ = fit_H0_for_omega(om_val, hz_z, hz_H, hz_err)
    print(f"    Ωm = {om_val:.4f} ({om_label:8s}): H₀ = {h0_fit:.1f}, MAE = {mae:.2f}, Δ from best = {mae - best_mae:+.3f}")


# ════════════════════════════════════════════════════════════════
# TEST 4: TRANSITION REDSHIFT — does z_trans land on a φ-power?
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  TEST 4: Transition Redshift z_trans — φ-Power?")
print(f"{'═' * 90}")

# z_trans for different Ωm
for label, om in [("Planck", 0.315), ("1/φ²", INV_PHI_2), ("Best fit", best_om), ("1/3", 1/3)]:
    z_tr = (2 * (1-om) / om) ** (1.0/3) - 1
    # Check proximity to φ-powers
    phi_test = {
        "1/φ": INV_PHI,
        "φ-1": PHI-1,
        "2/3": 2/3,
        "1/φ²": INV_PHI_2,
    }
    closest = min(phi_test.items(), key=lambda x: abs(x[1] - z_tr))
    print(f"  Ωm = {om:.4f} ({label:8s}): z_trans = {z_tr:.4f}, closest: {closest[0]} = {closest[1]:.4f} (Δ = {abs(z_tr - closest[1]):.4f})")

# Transition redshift for Ωm = 1/φ²
z_trans_phi = (2 * (1 - INV_PHI_2) / INV_PHI_2) ** (1.0/3) - 1
print(f"\n  If Ωm = 1/φ²: z_trans = {z_trans_phi:.4f}")
print(f"    1/φ = {INV_PHI:.4f}, φ-1 = {PHI-1:.4f}")
print(f"    z_trans - 1/φ = {z_trans_phi - INV_PHI:.4f}")
print(f"    z_trans - (φ-1) = {z_trans_phi - (PHI-1):.4f}")


# ════════════════════════════════════════════════════════════════
# TEST 5: ARA-WAVE RESIDUALS — is there a φ-periodic signal in H(z)?
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  TEST 5: φ-Wave in H(z) Residuals")
print(f"{'═' * 90}")

# Compute lookback time (simple numerical integration)
from scipy import integrate

def lookback_time(z, h0=H0_planck, om=Omega_m_planck):
    def integrand(zp):
        Ez = math.sqrt(om * (1 + zp)**3 + (1 - om))
        return 1.0 / ((1 + zp) * Ez)
    result, _ = integrate.quad(integrand, 0, z)
    t_H = 977.8 / h0
    return result * t_H

t_lookback = np.array([lookback_time(z) for z in hz_z])

# ΛCDM residuals as function of lookback time
resid = hz_H - lcdm_preds

# Test for wave at φ-power periods
print(f"\n  Lookback time range: {t_lookback[0]:.2f} to {t_lookback[-1]:.2f} Gyr")
print(f"  Testing φ-wave in ΛCDM residuals:")
print(f"  {'Period (Gyr)':>14} │ {'φ-power':>10} │ {'Wave amp':>10} │ {'% of σ_res':>10} │ {'Phase':>8}")
print(f"  {'─'*14}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*8}")

resid_std = np.std(resid)
w = 1.0 / hz_err**2

for power in range(-2, 6):
    period = PHI ** power
    if period < 0.3 or period > 15:
        continue
    # Weighted sinusoidal fit
    phases = TAU * t_lookback / period
    cos_comp = np.sum(w * resid * np.cos(phases)) / np.sum(w)
    sin_comp = np.sum(w * resid * np.sin(phases)) / np.sum(w)
    amp = math.sqrt(cos_comp**2 + sin_comp**2)
    phase = math.atan2(sin_comp, cos_comp)
    pct_sigma = amp / resid_std * 100 if resid_std > 0 else 0

    label = f"φ^{power}" if power != 1 else "φ"
    marker = " ★" if pct_sigma > 30 else ""
    print(f"  {period:>14.3f} │ {label:>10s} │ {amp:>10.2f} │ {pct_sigma:>9.1f}% │ {phase:>+8.3f}{marker}")


# ════════════════════════════════════════════════════════════════
# TEST 6: GEOMETRIC PREDICTIONS — framework-derived cosmic ratios
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  TEST 6: Framework Geometric Predictions")
print(f"{'═' * 90}")

print(f"\n  Dark energy fraction:")
print(f"    Observed Ωde = {Omega_de_planck:.4f}")
print(f"    1 - 1/φ²    = {1 - INV_PHI_2:.4f}  (φ-leak hypothesis)")
print(f"    1/φ          = {INV_PHI:.4f}")
print(f"    Δ(Ωde, 1-1/φ²) = {abs(Omega_de_planck - (1-INV_PHI_2)):.4f} ({abs(Omega_de_planck - (1-INV_PHI_2))/Omega_de_planck*100:.1f}%)")

print(f"\n  Matter-dark energy ratio:")
print(f"    Observed Ωm/Ωde  = {Omega_m_planck/Omega_de_planck:.4f}")
print(f"    1/φ²/(1-1/φ²)   = {INV_PHI_2/(1-INV_PHI_2):.4f}")
print(f"    1/(φ²-1) = 1/φ² × φ² = ... let's compute:")
om_phi = INV_PHI_2
ode_phi = 1 - INV_PHI_2
print(f"    If Ωm = 1/φ²: Ωm/Ωde = {om_phi/ode_phi:.4f}")
print(f"    Observed:       Ωm/Ωde = {Omega_m_planck/Omega_de_planck:.4f}")
print(f"    1/φ             = {INV_PHI:.4f}")
print(f"    Ωm/Ωde ≈ 1/φ?  Δ = {abs(Omega_m_planck/Omega_de_planck - INV_PHI):.4f}")

print(f"\n  Deceleration parameter geometry:")
print(f"    q₀ (current)    = {q0:+.4f}")
print(f"    -1/φ²           = {-INV_PHI_2:+.4f}")
print(f"    -(1-1/φ)        = {-(1-INV_PHI):+.4f}")
print(f"    -1/(1+φ²)       = {-1/(1+PHI**2):+.4f}")
print(f"    Δ(q₀, -1/φ²) = {abs(q0 + INV_PHI_2):.4f}")
print(f"    Δ(q₀, -1/(1+φ²)) = {abs(q0 + 1/(1+PHI**2)):.4f}")

# Hubble constant from φ
print(f"\n  Hubble constant:")
print(f"    H₀ (Planck) = {H0_planck} km/s/Mpc")
print(f"    100/φ       = {100/PHI:.1f}")
print(f"    φ⁴ × 10     = {PHI**4 * 10:.1f}")
print(f"    100×INV_PHI = {100*INV_PHI:.1f}")
print(f"    Δ(H₀, 100/φ) = {abs(H0_planck - 100/PHI):.1f}")

# Hubble tension: is it φ-related?
H0_local = 73.0  # SH0ES value
print(f"\n  Hubble tension:")
print(f"    Planck (CMB): {H0_planck}")
print(f"    SH0ES (local): {H0_local}")
print(f"    Ratio: {H0_local/H0_planck:.4f}")
print(f"    φ/φ-something?  {H0_local/H0_planck:.4f}, 1/φ + 1 = {1/PHI + 1:.4f}")
print(f"    Difference: {H0_local - H0_planck:.1f} km/s/Mpc")
print(f"    H_local/H_planck - 1 = {H0_local/H0_planck - 1:.4f}")
print(f"    1/φ⁴ = {INV_PHI**4:.4f}")
print(f"    Δ(ratio-1, 1/φ⁴) = {abs(H0_local/H0_planck - 1 - INV_PHI**4):.4f}")


# ════════════════════════════════════════════════════════════════
# TEST 7: SIMPLE ARA CASCADE (lightweight) — weighted mean reversion
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  TEST 7: Lightweight ARA Prediction — LOO on H(z)")
print(f"{'═' * 90}")

# Simple cascade-like prediction: for each held-out point,
# predict using ARA-weighted distance to training points
# This tests whether ARA geometry helps predict H(z) without the full engine

sine_mae_loo = np.mean(np.abs(hz_H - np.mean(hz_H)))

def ara_weighted_predict(i, z_data, H_data, t_data, ara_func, period):
    """Predict H(z_i) using ARA-weighted neighbours in lookback time."""
    mask = np.ones(len(z_data), dtype=bool)
    mask[i] = False
    z_train = z_data[mask]
    H_train = H_data[mask]
    t_train = t_data[mask]

    t_pred = t_data[i]
    z_pred = z_data[i]

    # ARA at prediction point
    ara_pred = ara_func(z_pred)

    # Phase distance in ARA-wave space
    dt = np.abs(t_train - t_pred)
    phase = dt / period * TAU

    # ARA-weighted kernel: closer in time AND in ARA-phase space
    wave_weight = (1 + np.cos(phase)) / 2  # [0,1]
    time_weight = np.exp(-dt / (period * PHI))

    # Combine
    weights = wave_weight * time_weight
    if np.sum(weights) < 1e-10:
        return np.mean(H_train)

    return np.sum(weights * H_train) / np.sum(weights)

print(f"\n  Sine baseline (LOO of mean): {sine_mae_loo:.2f}")

# Test different ARA functions and periods
ara_funcs = [
    ("constant φ",   lambda z: PHI),
    ("constant 1/φ", lambda z: INV_PHI),
    ("dynamic q(z)", lambda z: q_to_ara(q_LCDM(z))),
    ("constant 1.0", lambda z: 1.0),
]

periods_gyr = [
    ("φ² Gyr", PHI**2),
    ("φ³ Gyr", PHI**3),
    ("φ⁴ Gyr", PHI**4),
]

print(f"\n  {'ARA model':20s} │ {'Period':>10} │ {'LOO MAE':>8} │ {'LOO/Sine':>8} │ {'vs ΛCDM':>8}")
print(f"  {'─'*20}─┼─{'─'*10}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}")

for ara_name, ara_func in ara_funcs:
    for per_name, per_val in periods_gyr:
        errors = []
        for i in range(N):
            pred = ara_weighted_predict(i, hz_z, hz_H, t_lookback, ara_func, per_val)
            errors.append(abs(pred - hz_H[i]))
        mae = np.mean(errors)
        ratio = mae / sine_mae_loo
        vs_lcdm = (mae - lcdm_mae) / lcdm_mae * 100
        marker = " ★" if ratio < 1.0 else ""
        print(f"  {ara_name:20s} │ {per_name:>10} │ {mae:>8.2f} │ {ratio:>8.3f} │ {vs_lcdm:>+7.1f}%{marker}")

# Also test: pure distance-weighted (no ARA, no wave — just nearby H(z))
errors_knn = []
for i in range(N):
    mask = np.ones(N, dtype=bool)
    mask[i] = False
    dt = np.abs(t_lookback[mask] - t_lookback[i])
    w = np.exp(-dt / 2.0)  # 2 Gyr decay
    pred = np.sum(w * hz_H[mask]) / np.sum(w)
    errors_knn.append(abs(pred - hz_H[i]))
mae_knn = np.mean(errors_knn)
print(f"\n  {'No-ARA (time-only)':20s} │ {'2 Gyr':>10} │ {mae_knn:>8.2f} │ {mae_knn/sine_mae_loo:>8.3f} │ {(mae_knn-lcdm_mae)/lcdm_mae*100:>+7.1f}%")


# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════

print(f"\n{'═' * 90}")
print(f"  SUMMARY — ARA Dark Energy Geometry")
print(f"{'═' * 90}")

print(f"""
  KEY FINDINGS:

  1. ARA MAPPING: φ^(2q) maps deceleration parameter cleanly:
     • q = +0.5 → ARA = φ (engine, matter-dominated)
     • q = 0    → ARA = 1 (clock, transition at z = {z_trans_lcdm:.2f})
     • q = -0.5 → ARA = 1/φ (consumer, dark-energy-dominated)
     • Current: q₀ = {q0:+.3f} → ARA = {ara_now:.3f}
     • The universe is currently a CONSUMER ({abs(math.log(ara_now)/math.log(PHI)):.2f} φ-rungs from clock)

  2. Ωde vs φ-GEOMETRY:
     • Observed Ωde = {Omega_de_planck:.3f}
     • Framework: 1 - 1/φ² = {1-INV_PHI_2:.3f}
     • Difference: {abs(Omega_de_planck - (1-INV_PHI_2)):.3f} ({abs(Omega_de_planck-(1-INV_PHI_2))/Omega_de_planck*100:.1f}%)
     • This is a {abs(Omega_de_planck-(1-INV_PHI_2))/Omega_de_planck*100:.0f}% miss — NOT a match.
     • Ωm/Ωde = {Omega_m_planck/Omega_de_planck:.3f} vs 1/φ = {INV_PHI:.3f} — also ~{abs(Omega_m_planck/Omega_de_planck - INV_PHI)/INV_PHI*100:.0f}% off

  3. H₀ and φ:
     • 100/φ = {100/PHI:.1f} vs Planck H₀ = {H0_planck}
     • Hubble tension ratio: {H0_local/H0_planck:.4f} (difference {abs(H0_local/H0_planck - 1 - INV_PHI**4):.4f} from 1+1/φ⁴)

  4. BEST FIT Ωm from data: {best_om:.4f} (closest φ-power: {closest_phi[0]} = {closest_phi[1]:.4f})

  HONEST ASSESSMENT:
  The ARA → q(z) mapping is ELEGANT (φ-power of deceleration = ARA type),
  but the specific numeric predictions (Ωde = 1-1/φ²) are OFF by ~10%.
  This doesn't falsify the geometric framework but shows the cosmos may
  sit at a φ-power rung NEAR but not exactly ON 1/φ² for matter fraction.
  The transition epoch ARA = 1 (q = 0) is a NATURAL prediction of the framework.
""")

elapsed = clock_time.time() - t_start
print(f"  Runtime: {elapsed:.1f}s")
print("=" * 90)
