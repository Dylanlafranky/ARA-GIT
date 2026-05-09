#!/usr/bin/env python3
"""
Script 202 — Full Historical Sunspot Test: φ⁹ vs Sine on 25 Cycles

PEER REVIEW RESPONSE (v8, Issues #5-8):
  "Test the φ⁹ cascade on the full historical sunspot record (Schwabe 
   cycles 1-23) rather than the most recent 5."
  "Properly cross-validate with retraining."
  "The claim of zero free parameters counts only explicitly scanned phases
   but ignores embedded design choices."

THIS SCRIPT:
  1. Uses ALL known Schwabe cycles (1-25) — roughly 270 years of data
  2. Proper leave-one-out cross-validation WITH retraining
  3. Proper temporal split: train on first N, predict remaining
  4. Honest parameter counting
  5. Head-to-head: φ⁹ cascade vs 11-year sine vs training mean
  6. Reference date sensitivity analysis (reviewer Issue #5)

DATA SOURCE: Standard Schwabe cycle catalog (peak amplitudes, start years)
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

# === CONSTANTS ===
PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_4 = INV_PHI ** 4
INV_PHI_8 = INV_PHI ** 8

# === FULL SCHWABE CYCLE DATA ===
# Cycle number, approximate start year, peak year, peak smoothed SSN, period (years)
# Sources: SILSO / Royal Observatory of Belgium, WDC-SILSO
# Using the "international sunspot number" v2.0 scale where available
# Cycles 1-7 have larger uncertainty in amplitudes

CYCLES = {
    # cycle: (start_year, peak_year, peak_amplitude, period)
    1:  (1755.2, 1761.5, 144.1, 11.3),
    2:  (1766.5, 1769.7, 193.0, 9.0),
    3:  (1775.5, 1778.4, 264.3, 9.3),
    4:  (1784.7, 1788.1, 235.3, 13.6),
    5:  (1798.3, 1805.2, 82.0,  12.3),
    6:  (1810.6, 1816.4, 81.2,  12.7),
    7:  (1823.3, 1829.9, 119.2, 10.5),
    8:  (1833.8, 1837.2, 244.9, 9.7),
    9:  (1843.5, 1848.1, 219.9, 12.4),
    10: (1855.9, 1860.1, 186.2, 11.3),
    11: (1867.2, 1870.6, 234.0, 11.8),
    12: (1878.9, 1883.9, 124.4, 11.3),
    13: (1890.2, 1894.1, 146.5, 11.8),
    14: (1902.0, 1906.2, 107.1, 11.5),
    15: (1913.5, 1917.6, 175.7, 10.1),
    16: (1923.6, 1928.4, 130.2, 10.1),
    17: (1933.8, 1937.4, 198.6, 10.4),
    18: (1944.2, 1947.5, 218.7, 10.2),
    19: (1954.3, 1958.2, 285.0, 10.5),
    20: (1964.9, 1968.9, 156.6, 11.7),
    21: (1976.5, 1979.9, 232.9, 10.3),
    22: (1986.8, 1989.6, 212.5, 9.7),
    23: (1996.4, 2001.9, 180.3, 12.3),
    24: (2008.0, 2014.3, 116.4, 11.0),
    25: (2019.5, 2024.5, 173.0, 11.0),  # cycle 25 peak ~2024, estimated
}

N_CYCLES = len(CYCLES)
cycle_nums = sorted(CYCLES.keys())
start_years = np.array([CYCLES[c][0] for c in cycle_nums])
peak_years = np.array([CYCLES[c][1] for c in cycle_nums])
peak_amps = np.array([CYCLES[c][2] for c in cycle_nums])
periods = np.array([CYCLES[c][3] for c in cycle_nums])


def mae(pred, obs):
    return np.mean(np.abs(pred - obs))


# === MODEL 1: SINE BASELINE ===
def sine_predict(train_amps):
    """Predict = mean of training amplitudes. This IS the sine baseline
    for cycle peaks — a sine wave predicts every peak = same height."""
    return np.mean(train_amps)


# === MODEL 2: φ-CASCADE (DirectCascade from Script 201, properly parameterized) ===
class PhiCascade:
    """
    Multiplicative φ-cascade model.
    
    amplitude(t) = base_amp × ∏ (1 + ε_i × cos(2πt/P_i + phase_i))
    
    Cascade periods: φ², φ⁴, φ⁶, φ⁹ (from geometry)
    Coupling: all 1/φ⁴ (same-axis, from three-way junction)
    
    FREE PARAMETERS (honest count):
      - base_amp: fitted from training data (1 param)
      - t_ref: reference date (1 param) — OR fixed phases (4 params)
      
    We test BOTH:
      (a) Single t_ref scanned — 2 total params (base_amp + t_ref)
      (b) Fixed t_ref at earliest cycle start — 1 param (base_amp only)
    """
    
    CASCADE_PERIODS = [PHI**2, PHI**4, PHI**6, PHI**9]
    EPSILON = INV_PHI_4  # all same coupling
    
    def __init__(self, base_amp, t_ref):
        self.base_amp = base_amp
        self.t_ref = t_ref
        
    def predict_one(self, peak_year):
        amp = self.base_amp
        for P in self.CASCADE_PERIODS:
            phase = 2 * np.pi * (peak_year - self.t_ref) / P
            amp *= (1 + self.EPSILON * np.cos(phase))
        return amp
    
    def predict_all(self, peak_years_arr):
        return np.array([self.predict_one(t) for t in peak_years_arr])


def fit_cascade_fixed_ref(train_peak_years, train_amps, t_ref):
    """Fit with fixed reference date. Only 1 free param: base_amp."""
    # Optimal base_amp minimizes MAE. Since cascade is multiplicative,
    # base_amp ≈ mean(train_amps) / mean(multiplier)
    # Use scipy-free optimization: scan base_amp
    
    best_mae = 1e9
    best_amp = np.mean(train_amps)
    
    for trial_amp in np.linspace(np.mean(train_amps) * 0.5, 
                                  np.mean(train_amps) * 1.5, 200):
        model = PhiCascade(trial_amp, t_ref)
        preds = model.predict_all(train_peak_years)
        m = mae(preds, train_amps)
        if m < best_mae:
            best_mae = m
            best_amp = trial_amp
    
    return PhiCascade(best_amp, t_ref), best_mae


def fit_cascade_scan_ref(train_peak_years, train_amps):
    """Fit with scanned reference date. 2 free params: base_amp + t_ref."""
    best_mae = 1e9
    best_model = None
    
    # Scan reference dates across one Gleissberg period
    for t_ref in np.linspace(1750, 1830, 80):
        model, m = fit_cascade_fixed_ref(train_peak_years, train_amps, t_ref)
        if m < best_mae:
            best_mae = m
            best_model = model
    
    return best_model, best_mae


# === MODEL 3: φ-CASCADE with INDIVIDUAL PHASES (4+1 params) ===
class PhiCascadePhases:
    """Full 4-phase model. 5 params total: base_amp + 4 phases."""
    
    CASCADE_PERIODS = [PHI**2, PHI**4, PHI**6, PHI**9]
    EPSILON = INV_PHI_4
    
    def __init__(self, base_amp, phases):
        self.base_amp = base_amp
        self.phases = phases
    
    def predict_one(self, peak_year):
        amp = self.base_amp
        for P, ph in zip(self.CASCADE_PERIODS, self.phases):
            amp *= (1 + self.EPSILON * np.cos(2 * np.pi * peak_year / P + ph))
        return amp
    
    def predict_all(self, peak_years_arr):
        return np.array([self.predict_one(t) for t in peak_years_arr])


def fit_cascade_phases(train_peak_years, train_amps):
    """Fit 5-param model on training data."""
    best_mae = 1e9
    best_model = None
    n_phase = 12  # coarser grid since we have more data
    phase_grid = np.linspace(0, 2*np.pi, n_phase, endpoint=False)
    base_amp = np.mean(train_amps)
    
    # Scan base_amp and phases
    for ba in np.linspace(base_amp * 0.7, base_amp * 1.3, 30):
        for p0 in phase_grid:
            for p1 in phase_grid:
                for p2 in phase_grid:
                    for p3 in phase_grid:
                        phases = [p0, p1, p2, p3]
                        model = PhiCascadePhases(ba, phases)
                        preds = model.predict_all(train_peak_years)
                        m = mae(preds, train_amps)
                        if m < best_mae:
                            best_mae = m
                            best_model = PhiCascadePhases(ba, phases[:])
    
    return best_model, best_mae


# =================================================================
#  MAIN ANALYSIS
# =================================================================
if __name__ == '__main__':
    print("=" * 72)
    print("SCRIPT 202 — FULL HISTORICAL TEST: φ⁹ vs SINE on 25 CYCLES")
    print("=" * 72)
    
    print(f"\n--- DATA: {N_CYCLES} Schwabe cycles (1755-2025) ---")
    print(f"  Amplitudes: min={peak_amps.min():.1f}, max={peak_amps.max():.1f}, "
          f"mean={peak_amps.mean():.1f}, std={peak_amps.std():.1f}")
    print(f"  Periods: min={periods.min():.1f}, max={periods.max():.1f}, "
          f"mean={periods.mean():.1f}")
    
    # =================================================================
    # TEST 1: Leave-One-Out Cross-Validation WITH RETRAINING
    # =================================================================
    print(f"\n{'='*72}")
    print("TEST 1: LEAVE-ONE-OUT CROSS-VALIDATION (with retraining)")
    print(f"{'='*72}")
    
    sine_errors = []
    cascade_fixed_errors = []
    cascade_scan_errors = []
    
    t_ref_fixed = start_years[0]  # 1755.2 — earliest cycle start
    
    for i in range(N_CYCLES):
        # Train on all except i
        train_mask = np.ones(N_CYCLES, dtype=bool)
        train_mask[i] = False
        train_years = peak_years[train_mask]
        train_amps_i = peak_amps[train_mask]
        test_year = peak_years[i]
        test_amp = peak_amps[i]
        
        # Sine: predict = training mean
        sine_pred = sine_predict(train_amps_i)
        sine_errors.append(abs(sine_pred - test_amp))
        
        # Cascade fixed ref: 1 free param
        model_fixed, _ = fit_cascade_fixed_ref(train_years, train_amps_i, t_ref_fixed)
        pred_fixed = model_fixed.predict_one(test_year)
        cascade_fixed_errors.append(abs(pred_fixed - test_amp))
        
        # Cascade scanned ref: 2 free params
        model_scan, _ = fit_cascade_scan_ref(train_years, train_amps_i)
        pred_scan = model_scan.predict_one(test_year)
        cascade_scan_errors.append(abs(pred_scan - test_amp))
    
    sine_loo = np.mean(sine_errors)
    fixed_loo = np.mean(cascade_fixed_errors)
    scan_loo = np.mean(cascade_scan_errors)
    
    print(f"\n  LOO MAE (retrained each fold):")
    print(f"    Sine baseline (1 param):     {sine_loo:.2f}")
    print(f"    φ-cascade fixed ref (1 param): {fixed_loo:.2f}  "
          f"({(fixed_loo/sine_loo - 1)*100:+.1f}% vs sine)")
    print(f"    φ-cascade scan ref (2 param):  {scan_loo:.2f}  "
          f"({(scan_loo/sine_loo - 1)*100:+.1f}% vs sine)")
    
    print(f"\n  Per-cycle errors (fixed ref):")
    for i, c in enumerate(cycle_nums):
        s_err = sine_errors[i]
        f_err = cascade_fixed_errors[i]
        winner = "φ" if f_err < s_err else "sine"
        print(f"    Cycle {c:2d} ({peak_years[i]:.0f}): "
              f"sine={s_err:.1f}  φ={f_err:.1f}  → {winner}")
    
    n_phi_wins = sum(1 for i in range(N_CYCLES) 
                     if cascade_fixed_errors[i] < sine_errors[i])
    print(f"\n  φ wins {n_phi_wins}/{N_CYCLES} cycles")
    
    # =================================================================
    # TEST 2: TEMPORAL SPLITS (train on first N, predict rest)
    # =================================================================
    print(f"\n{'='*72}")
    print("TEST 2: TEMPORAL SPLITS (train early, predict late)")
    print(f"{'='*72}")
    
    for n_train in [5, 8, 10, 12, 15, 18, 20]:
        if n_train >= N_CYCLES:
            continue
            
        train_years_t = peak_years[:n_train]
        train_amps_t = peak_amps[:n_train]
        test_years_t = peak_years[n_train:]
        test_amps_t = peak_amps[n_train:]
        n_test = len(test_amps_t)
        
        # Sine
        sine_pred_t = np.full(n_test, sine_predict(train_amps_t))
        sine_mae_t = mae(sine_pred_t, test_amps_t)
        
        # Cascade fixed ref
        model_t, _ = fit_cascade_fixed_ref(train_years_t, train_amps_t, t_ref_fixed)
        phi_pred_t = model_t.predict_all(test_years_t)
        phi_mae_t = mae(phi_pred_t, test_amps_t)
        
        # Cascade scan ref
        model_s, _ = fit_cascade_scan_ref(train_years_t, train_amps_t)
        phi_scan_t = model_s.predict_all(test_years_t)
        phi_scan_mae_t = mae(phi_scan_t, test_amps_t)
        
        winner = "φ-fixed" if phi_mae_t < sine_mae_t else "sine"
        print(f"  Train {n_train:2d} / Test {n_test:2d}: "
              f"sine={sine_mae_t:.1f}  φ-fixed={phi_mae_t:.1f}  "
              f"φ-scan={phi_scan_mae_t:.1f}  → {winner}")
    
    # =================================================================
    # TEST 3: REFERENCE DATE SENSITIVITY (reviewer Issue #5)
    # =================================================================
    print(f"\n{'='*72}")
    print("TEST 3: REFERENCE DATE SENSITIVITY")
    print(f"{'='*72}")
    
    ref_dates = np.linspace(1700, 1900, 50)
    ref_maes = []
    for t_ref in ref_dates:
        model_r = PhiCascade(np.mean(peak_amps), t_ref)
        preds_r = model_r.predict_all(peak_years)
        ref_maes.append(mae(preds_r, peak_amps))
    
    ref_maes = np.array(ref_maes)
    print(f"  t_ref range: {ref_dates[0]:.0f} to {ref_dates[-1]:.0f}")
    print(f"  MAE range: {ref_maes.min():.2f} to {ref_maes.max():.2f}")
    print(f"  Best t_ref: {ref_dates[np.argmin(ref_maes)]:.1f} (MAE={ref_maes.min():.2f})")
    print(f"  Worst t_ref: {ref_dates[np.argmax(ref_maes)]:.1f} (MAE={ref_maes.max():.2f})")
    print(f"  Mean MAE across all t_ref: {ref_maes.mean():.2f}")
    print(f"  Sine MAE (for comparison): {mae(np.full(N_CYCLES, peak_amps.mean()), peak_amps):.2f}")
    print(f"\n  If most t_ref values beat sine → the cascade has structural content")
    print(f"  If only narrow t_ref range beats sine → the t_ref is doing the work")
    n_beats_sine = np.sum(ref_maes < mae(np.full(N_CYCLES, peak_amps.mean()), peak_amps))
    print(f"  {n_beats_sine}/{len(ref_dates)} reference dates beat sine "
          f"({n_beats_sine/len(ref_dates)*100:.0f}%)")
    
    # =================================================================
    # TEST 4: FULL MODEL FIT (for comparison only — not cross-validated)
    # =================================================================
    print(f"\n{'='*72}")
    print("TEST 4: FULL FIT (all data, for reference only)")
    print(f"{'='*72}")
    
    # Fixed ref
    model_full_fixed, full_fixed_mae = fit_cascade_fixed_ref(
        peak_years, peak_amps, t_ref_fixed)
    print(f"  Fixed ref (t_ref={t_ref_fixed}): MAE = {full_fixed_mae:.2f}")
    
    # Scanned ref
    model_full_scan, full_scan_mae = fit_cascade_scan_ref(peak_years, peak_amps)
    print(f"  Scanned ref (t_ref={model_full_scan.t_ref:.1f}): "
          f"MAE = {full_scan_mae:.2f}")
    
    # Sine
    full_sine_mae = mae(np.full(N_CYCLES, peak_amps.mean()), peak_amps)
    print(f"  Sine (mean): MAE = {full_sine_mae:.2f}")
    
    # Print predictions vs observed for best model
    best_full = model_full_scan
    preds_full = best_full.predict_all(peak_years)
    
    print(f"\n  Cycle-by-cycle (scan ref model):")
    print(f"  {'Cycle':>5s} {'Year':>6s} {'Obs':>7s} {'Pred':>7s} {'Err':>7s} {'Sine':>7s}")
    for i, c in enumerate(cycle_nums):
        obs = peak_amps[i]
        pred = preds_full[i]
        sine_p = peak_amps.mean()
        print(f"  {c:5d} {peak_years[i]:6.0f} {obs:7.1f} {pred:7.1f} "
              f"{pred-obs:+7.1f} {sine_p-obs:+7.1f}")
    
    # =================================================================
    # TEST 5: WHAT DOES φ-CASCADE CAPTURE THAT SINE DOESN'T?
    # =================================================================
    print(f"\n{'='*72}")
    print("TEST 5: WHAT DOES THE CASCADE ADD?")
    print(f"{'='*72}")
    
    # The sine baseline predicts constant amplitude. The cascade should
    # capture AMPLITUDE MODULATION — the Gleissberg-like envelope.
    
    # Check: does the cascade predict the Grand Minimum (cycles 5-6)?
    print(f"\n  Grand Minimum test (cycles 5-6, Dalton Minimum):")
    print(f"    Observed: {peak_amps[4]:.1f}, {peak_amps[5]:.1f}")
    print(f"    Cascade:  {preds_full[4]:.1f}, {preds_full[5]:.1f}")
    print(f"    Sine:     {peak_amps.mean():.1f}, {peak_amps.mean():.1f}")
    
    # Modern maximum (cycle 19)
    print(f"\n  Modern Maximum test (cycle 19):")
    print(f"    Observed: {peak_amps[18]:.1f}")
    print(f"    Cascade:  {preds_full[18]:.1f}")
    print(f"    Sine:     {peak_amps.mean():.1f}")
    
    # Recent decline (cycles 23-24)
    print(f"\n  Recent decline test (cycles 23-25):")
    for c_idx in [22, 23, 24]:
        c = cycle_nums[c_idx]
        print(f"    Cycle {c}: obs={peak_amps[c_idx]:.1f}  "
              f"cascade={preds_full[c_idx]:.1f}  sine={peak_amps.mean():.1f}")
    
    # Amplitude variance captured
    obs_var = np.var(peak_amps)
    cascade_var = np.var(preds_full)
    sine_var = 0.0
    print(f"\n  Amplitude variance:")
    print(f"    Observed:  {obs_var:.1f}")
    print(f"    Cascade:   {cascade_var:.1f} ({cascade_var/obs_var*100:.1f}% of observed)")
    print(f"    Sine:      {sine_var:.1f} (0% — constant prediction)")
    
    # Correlation
    corr = np.corrcoef(preds_full, peak_amps)[0, 1]
    print(f"\n  Correlation (cascade vs observed): {corr:+.4f}")
    print(f"  Correlation (sine vs observed):    +0.0000 (by definition)")
    
    # =================================================================
    # SUMMARY
    # =================================================================
    print(f"\n{'='*72}")
    print("SUMMARY — SCRIPT 202")
    print(f"{'='*72}")
    
    print(f"""
  DATA: {N_CYCLES} Schwabe cycles, 1755-2025
  
  LOO Cross-Validation (retrained each fold):
    Sine baseline (1 param):       MAE = {sine_loo:.2f}
    φ-cascade fixed ref (1 param): MAE = {fixed_loo:.2f} ({(fixed_loo/sine_loo-1)*100:+.1f}%)
    φ-cascade scan ref (2 params): MAE = {scan_loo:.2f} ({(scan_loo/sine_loo-1)*100:+.1f}%)
    
  φ wins {n_phi_wins}/{N_CYCLES} individual LOO folds
  Reference date sensitivity: {n_beats_sine}/{len(ref_dates)} t_ref values beat sine ({n_beats_sine/len(ref_dates)*100:.0f}%)
  Amplitude variance captured: {cascade_var/obs_var*100:.1f}%
  Correlation: {corr:+.4f}
  
  HONEST PARAMETER COUNT:
    Sine: 1 (training mean)
    φ-cascade fixed: 1 (base_amp; t_ref fixed at cycle 1 start)
    φ-cascade scan:  2 (base_amp + t_ref)
    
  STRUCTURAL CONTENT (NOT in sine):
    - Cascade periods from φ alone (φ², φ⁴, φ⁶, φ⁹)
    - Coupling strength from geometry (1/φ⁴)
    - Amplitude modulation (Gleissberg envelope)
""")

    if fixed_loo < sine_loo:
        print("  ★ φ-CASCADE BEATS SINE ON PROPER LOO CROSS-VALIDATION ★")
        print(f"    With the SAME number of free parameters (1).")
    elif scan_loo < sine_loo:
        print("  ★ φ-CASCADE BEATS SINE WITH 2 PARAMS (scan ref) ★")
        print(f"    But NOT with 1 param (fixed ref). The reference date matters.")
    else:
        print("  Sine baseline still wins on LOO cross-validation.")
        print("  The φ-cascade captures amplitude structure (variance, correlation)")
        print("  but not enough to overcome the noise in individual cycle prediction.")

