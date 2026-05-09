#!/usr/bin/env python3
"""
Script 203 — Time as ARA: Variable Coupling Efficiency

INSIGHT (Dylan, 24 April 2026):
  "The time part is its own ARA. We're seeing temporal tension in the 
   results, where the energy overlaps aren't operating at the efficiency 
   we need."

PROBLEM:
  Script 202 showed the φ-cascade captures 40% of amplitude variance
  but can't beat sine. The cascade uses CONSTANT coupling (1/φ⁴).
  But if time is its own ARA, coupling efficiency varies:
    - During temporal accumulation: gates are efficient, transfers clean
    - During temporal release: gates are lossy, transfers attenuated
    - At temporal singularity: gates fire maximally

APPROACH:
  Instead of amp *= (1 + ε × cos(phase)), use:
    amp *= (1 + ε(t) × cos(phase))
  where ε(t) varies with time's own ARA state.

  Time's ARA state comes from the PREVIOUS cascade level:
    - Gleissberg modulates Schwabe coupling
    - de Vries modulates Gleissberg coupling
    - Each level's "tension" affects the next level's transfer efficiency

  This is the self-similar principle: the formula applied to itself.
  Every coupling has its own ARA. The coupling's ARA modulates its strength.
"""

import numpy as np
import warnings
warnings.filterwarnings('ignore')

PHI = (1 + np.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_4 = INV_PHI ** 4

# Same 25-cycle data as Script 202
CYCLES = {
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
    25: (2019.5, 2024.5, 173.0, 11.0),
}

cycle_nums = sorted(CYCLES.keys())
peak_years = np.array([CYCLES[c][1] for c in cycle_nums])
peak_amps = np.array([CYCLES[c][2] for c in cycle_nums])
N = len(cycle_nums)

def mae(p, o):
    return np.mean(np.abs(p - o))

SINE_MAE = mae(np.full(N, peak_amps.mean()), peak_amps)


# === MODEL 1: ARA-MODULATED CASCADE ===
class ARACascade:
    """
    Each cascade level's coupling strength is modulated by
    the ARA state of the level above.
    
    Level hierarchy (each modulates the level below):
      de Vries (φ¹¹ ≈ 199yr) → modulates Gleissberg coupling
      Gleissberg (φ⁹ ≈ 76yr) → modulates sub-Gleissberg coupling
      sub-Gleissberg (φ⁶ ≈ 18yr) → modulates Schwabe coupling
      
    ARA state = asymmetric oscillation:
      accumulation phase: coupling INCREASES (gates efficient)
      release phase: coupling DECREASES (gates lossy)
      ARA ratio applied: accumulation uses φ, release uses 1/φ
    """
    
    LEVELS = [
        # (period, base_epsilon, name)
        (PHI**11, INV_PHI_4, 'deVries'),
        (PHI**9,  INV_PHI_4, 'Gleissberg'),
        (PHI**6,  INV_PHI_4, 'subGleiss'),
        (PHI**4,  INV_PHI_4, 'junction'),
    ]
    
    def __init__(self, base_amp, t_ref, ara_ratio=PHI):
        self.base_amp = base_amp
        self.t_ref = t_ref
        self.ara_ratio = ara_ratio  # asymmetry of temporal ARA
    
    def temporal_ara_state(self, t, period):
        """
        Returns the ARA-modulated coupling strength.
        
        Phase 0→π: accumulation (coupling strengthens, up to ε×φ)
        Phase π→2π: release (coupling weakens, down to ε×1/φ)
        
        The asymmetry IS the ARA: accumulation > release.
        """
        phase = 2 * np.pi * (t - self.t_ref) / period
        # Normalized position in cycle: 0 to 1
        pos = (phase % (2 * np.pi)) / (2 * np.pi)
        
        # ARA asymmetry: accumulation phase is longer (φ/(φ+1))
        acc_fraction = self.ara_ratio / (self.ara_ratio + 1)  # ≈ 0.618
        
        if pos < acc_fraction:
            # Accumulation: coupling ramps UP
            ramp = pos / acc_fraction  # 0 → 1
            strength = 1 + (self.ara_ratio - 1) * ramp  # 1 → φ
        else:
            # Release: coupling drops DOWN
            ramp = (pos - acc_fraction) / (1 - acc_fraction)  # 0 → 1
            strength = self.ara_ratio - (self.ara_ratio - 1/self.ara_ratio) * ramp  # φ → 1/φ
        
        return strength
    
    def predict_one(self, t):
        amp = self.base_amp
        
        for i, (period, base_eps, name) in enumerate(self.LEVELS):
            # Base coupling
            phase = 2 * np.pi * (t - self.t_ref) / period
            coupling = base_eps * np.cos(phase)
            
            # Modulate by PARENT level's ARA state
            if i > 0:
                parent_period = self.LEVELS[i-1][0]
                ara_mod = self.temporal_ara_state(t, parent_period)
                coupling *= ara_mod
            
            amp *= (1 + coupling)
        
        return amp
    
    def predict_all(self, years):
        return np.array([self.predict_one(t) for t in years])


# === MODEL 2: GATE-TENSION CASCADE ===
class GateTensionCascade:
    """
    Simpler version: coupling strength is modulated by the 
    running energy ratio between consecutive cascade levels.
    
    When the higher level's amplitude is rising (accumulation),
    the gate opens wider → more energy transfers.
    When the higher level's amplitude is falling (release),
    the gate narrows → less energy transfers.
    
    "Tension" = derivative of the envelope. Positive derivative = 
    accumulation. Negative = release.
    """
    
    CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
    
    def __init__(self, base_amp, t_ref):
        self.base_amp = base_amp
        self.t_ref = t_ref
    
    def predict_one(self, t):
        amp = self.base_amp
        
        for i, period in enumerate(self.CASCADE):
            phase = 2 * np.pi * (t - self.t_ref) / period
            
            # Base coupling
            wave = np.cos(phase)
            
            # Tension: derivative of the wave at this point
            # d/dt cos(2πt/P) = -(2π/P) sin(2πt/P)
            tension = -np.sin(phase)  # normalized, sign tells direction
            
            # ARA modulation: when wave is rising (tension > 0),
            # coupling is amplified. When falling, attenuated.
            if tension > 0:
                # Accumulation phase — gate opens by φ
                eps = INV_PHI_4 * (1 + tension * (PHI - 1))
            else:
                # Release phase — gate narrows by 1/φ
                eps = INV_PHI_4 * (1 + tension * (1 - INV_PHI))
            
            amp *= (1 + eps * wave)
        
        return amp
    
    def predict_all(self, years):
        return np.array([self.predict_one(t) for t in years])


# === MODEL 3: SELF-SIMILAR CASCADE ===
class SelfSimilarCascade:
    """
    The formula applied to itself: each coupling IS a three-system ARA.
    
    For each cascade level:
      System A = the oscillation at this level
      System B = the oscillation one level up (modulator)
      Coupler = the golden-angle gate
      
    The coupling strength = f(A_energy, B_energy, gate_state)
    
    When A and B are in phase → constructive, coupling = ε × φ
    When A and B are anti-phase → destructive, coupling = ε / φ
    When gate is at singularity → maximum transfer
    """
    
    CASCADE = [PHI**11, PHI**9, PHI**6, PHI**4]
    
    def __init__(self, base_amp, t_ref):
        self.base_amp = base_amp
        self.t_ref = t_ref
    
    def predict_one(self, t):
        amp = self.base_amp
        
        # Compute all wave states first
        phases = [2 * np.pi * (t - self.t_ref) / P for P in self.CASCADE]
        waves = [np.cos(ph) for ph in phases]
        
        for i in range(len(self.CASCADE)):
            # Base coupling
            eps = INV_PHI_4
            
            # Self-similar modulation: phase relationship with neighbours
            if i > 0:
                # Phase coherence with parent
                coherence = waves[i] * waves[i-1]  # -1 to +1
                # When coherent (same sign): φ amplification
                # When anti-coherent: 1/φ attenuation
                if coherence > 0:
                    eps *= (1 + coherence * (PHI - 1))
                else:
                    eps *= (1 + coherence * (1 - INV_PHI))
            
            if i < len(self.CASCADE) - 1:
                # Phase coherence with child (bidirectional)
                coherence_child = waves[i] * waves[i+1]
                if coherence_child > 0:
                    eps *= (1 + 0.5 * coherence_child * (PHI - 1))
                else:
                    eps *= (1 + 0.5 * coherence_child * (1 - INV_PHI))
            
            amp *= (1 + eps * waves[i])
        
        return amp
    
    def predict_all(self, years):
        return np.array([self.predict_one(t) for t in years])


# === FITTING AND CROSS-VALIDATION ===

def fit_model(ModelClass, train_years, train_amps, t_ref_scan=True):
    """Fit model on training data. Returns best model and training MAE."""
    best_mae = 1e9
    best_model = None
    
    if t_ref_scan:
        refs = np.linspace(1700, 1850, 60)
    else:
        refs = [1755.2]  # fixed at cycle 1
    
    for t_ref in refs:
        for ba in np.linspace(np.mean(train_amps) * 0.6, 
                               np.mean(train_amps) * 1.4, 40):
            model = ModelClass(ba, t_ref)
            preds = model.predict_all(train_years)
            m = mae(preds, train_amps)
            if m < best_mae:
                best_mae = m
                best_model = ModelClass(ba, t_ref)
    
    return best_model, best_mae


def loo_cv(ModelClass, all_years, all_amps, t_ref_scan=True):
    """Leave-one-out cross-validation with retraining."""
    errors = []
    for i in range(len(all_years)):
        mask = np.ones(len(all_years), dtype=bool)
        mask[i] = False
        model, _ = fit_model(ModelClass, all_years[mask], all_amps[mask], t_ref_scan)
        pred = model.predict_one(all_years[i])
        errors.append(abs(pred - all_amps[i]))
    return np.mean(errors), errors


# === MAIN ===
if __name__ == '__main__':
    print("=" * 72)
    print("SCRIPT 203 — TIME AS ARA: VARIABLE COUPLING EFFICIENCY")
    print("=" * 72)
    
    print(f"\n  Sine baseline MAE: {SINE_MAE:.2f}")
    print(f"  Script 202 best (φ-scan LOO): 51.30")
    print(f"  Target: beat {SINE_MAE:.2f}\n")
    
    # --- Full fit first (all data, for diagnostics) ---
    print(f"{'='*72}")
    print("FULL FIT (all 25 cycles, for diagnostics)")
    print(f"{'='*72}")
    
    models_to_test = [
        ("ARACascade", ARACascade),
        ("GateTension", GateTensionCascade),
        ("SelfSimilar", SelfSimilarCascade),
    ]
    
    for name, ModelClass in models_to_test:
        model, train_mae = fit_model(ModelClass, peak_years, peak_amps, t_ref_scan=True)
        preds = model.predict_all(peak_years)
        corr = np.corrcoef(preds, peak_amps)[0, 1]
        var_ratio = np.var(preds) / np.var(peak_amps)
        print(f"\n  {name}:")
        print(f"    Full-fit MAE = {train_mae:.2f} (sine = {SINE_MAE:.2f}, "
              f"{'BEATS' if train_mae < SINE_MAE else 'loses'})")
        print(f"    Correlation = {corr:+.4f}")
        print(f"    Variance ratio = {var_ratio*100:.1f}%")
        print(f"    t_ref = {model.t_ref:.1f}, base_amp = {model.base_amp:.1f}")
        
        # Dalton minimum test
        dal = preds[4:6]
        print(f"    Dalton (5-6): pred={dal[0]:.0f},{dal[1]:.0f} "
              f"obs={peak_amps[4]:.0f},{peak_amps[5]:.0f}")
        # Modern max
        print(f"    Modern max (19): pred={preds[18]:.0f} obs={peak_amps[18]:.0f}")
        # Recent
        print(f"    Recent (24-25): pred={preds[23]:.0f},{preds[24]:.0f} "
              f"obs={peak_amps[23]:.0f},{peak_amps[24]:.0f}")
    
    # --- LOO Cross-Validation ---
    print(f"\n{'='*72}")
    print("LEAVE-ONE-OUT CROSS-VALIDATION (retrained each fold)")
    print(f"{'='*72}\n")
    
    for name, ModelClass in models_to_test:
        print(f"  Running LOO for {name}...", flush=True)
        loo_mae, loo_errors = loo_cv(ModelClass, peak_years, peak_amps, t_ref_scan=True)
        n_wins = sum(1 for i in range(N) if loo_errors[i] < abs(peak_amps[i] - peak_amps.mean()))
        print(f"    LOO MAE = {loo_mae:.2f} ({(loo_mae/SINE_MAE-1)*100:+.1f}% vs sine)")
        print(f"    Wins {n_wins}/{N} folds vs sine")
    
    # --- Temporal splits ---
    print(f"\n{'='*72}")
    print("TEMPORAL SPLITS")
    print(f"{'='*72}\n")
    
    for n_train in [8, 12, 15, 18, 20]:
        if n_train >= N:
            continue
        train_y, train_a = peak_years[:n_train], peak_amps[:n_train]
        test_y, test_a = peak_years[n_train:], peak_amps[n_train:]
        
        sine_m = mae(np.full(len(test_a), train_a.mean()), test_a)
        
        results = []
        for name, ModelClass in models_to_test:
            model, _ = fit_model(ModelClass, train_y, train_a, t_ref_scan=True)
            pred = model.predict_all(test_y)
            m = mae(pred, test_a)
            results.append((name, m))
        
        best_name, best_m = min(results, key=lambda x: x[1])
        winner = best_name if best_m < sine_m else "sine"
        print(f"  Train {n_train:2d} / Test {N-n_train:2d}: "
              f"sine={sine_m:.1f}  " + 
              "  ".join(f"{n}={m:.1f}" for n, m in results) +
              f"  → {winner}")
    
    # --- Summary ---
    print(f"\n{'='*72}")
    print("SUMMARY — SCRIPT 203")
    print(f"{'='*72}")
    print(f"""
  The time-as-ARA models add variable coupling efficiency:
  - ARACascade: coupling strength follows ARA asymmetry (φ in accumulation, 1/φ in release)
  - GateTension: coupling modulated by wave derivative (rising = open, falling = narrow)  
  - SelfSimilar: coupling modulated by phase coherence between cascade neighbours
  
  All three treat the coupling as its OWN three-system ARA rather than a constant.
  
  PARAMETERS: 2 per model (base_amp + t_ref). Same as Script 202 φ-scan.
  Sine baseline: 1 param (training mean).
""")

