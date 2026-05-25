#!/usr/bin/env python3
"""
Compute the ARA of atomic fluorescence cycles from first principles.

Systems:
  1. Na D-line fluorescence (3p → 3s, 589.3 nm)
  2. H Lyman-alpha fluorescence (2p → 1s, 121.6 nm)

Method:
  The oscillatory system is a two-level atom cycling through:
    ground → absorbs photon → excited → emits photon → ground

  To find T_accumulation and T_release, we solve the optical Bloch equations
  for a driven two-level atom with spontaneous emission.  These give the
  actual time-resolved population dynamics ρ_ee(t) — the probability of
  finding the atom in the excited state as a function of time.

  Phase decomposition:
    - ACCUMULATION: the atom absorbs a photon and the excited-state population
      rises from 0 toward its peak.  Energy is being stored in the atomic
      excitation.  Duration = time from ρ_ee minimum to ρ_ee maximum.
    - RELEASE: the excited-state population decays from its peak back down,
      as the atom emits a photon (spontaneous or stimulated).  Stored energy
      is released as radiation.  Duration = time from ρ_ee maximum back to
      ρ_ee minimum.

  The Bloch equations naturally include both the driving field (absorption)
  and spontaneous decay (emission), so the asymmetry between accumulation
  and release emerges from the physics.

  We examine three pump regimes:
    - Weak pump (Ω_R << Γ): incoherent regime, rate-equation limit
    - Moderate pump (Ω_R ~ Γ): intermediate regime
    - Strong pump (Ω_R >> Γ): coherent Rabi oscillation regime

  The ARA may depend on pump strength, which is itself diagnostic information.
  We also compute the natural (undriven) spontaneous emission dynamics for
  comparison.

Physical parameters from:
  - NIST Atomic Spectra Database for transition rates and lifetimes
  - Foot, "Atomic Physics" (2005) for dipole matrix elements
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "quantum_fluorescence_ara_result.json"

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
HBAR = 1.054571817e-34   # J·s
H_PLANCK = 6.62607015e-34  # J·s
C = 2.99792458e8         # m/s
E_CHARGE = 1.602176634e-19  # C
EV_TO_J = 1.602176634e-19  # J per eV
EPSILON_0 = 8.8541878128e-12
ME = 9.1093837015e-31    # electron mass, kg
A0 = 5.29177210903e-11   # Bohr radius, m


# ---------------------------------------------------------------------------
# Atom data
# ---------------------------------------------------------------------------
ATOMS = {
    "Na_D_line": {
        "name": "Na D-line fluorescence",
        "transition": "3p → 3s",
        "wavelength_nm": 589.3,
        "lifetime_ns": 16.24,          # natural lifetime of Na 3p state (NIST)
        "einstein_A_per_s": 6.16e7,    # spontaneous emission rate Γ = 1/τ
        "notes": "Sodium D₂ line. τ = 16.24 ns from NIST ASD.",
    },
    "H_Lyman_alpha": {
        "name": "H Lyman-alpha fluorescence",
        "transition": "2p → 1s",
        "wavelength_nm": 121.567,
        "lifetime_ns": 1.596,          # natural lifetime of H 2p state (NIST)
        "einstein_A_per_s": 6.2649e8,  # spontaneous emission rate
        "notes": "Hydrogen Lyman-alpha. τ = 1.596 ns from NIST ASD.",
    },
}


def photon_energy_j(wavelength_nm: float) -> float:
    return H_PLANCK * C / (wavelength_nm * 1e-9)


def solve_bloch_equations(gamma: float, omega_rabi: float, n_lifetimes: float = 20.0,
                           dt_factor: float = 0.001) -> dict:
    """Solve the optical Bloch equations for a two-level atom.

    The Bloch equations for a resonantly driven two-level atom (detuning = 0)
    in the rotating wave approximation:

      dρ_ee/dt = (i/2) Ω_R (ρ_ge - ρ_eg) - Γ ρ_ee
      dρ_eg/dt = (i/2) Ω_R (ρ_ee - ρ_gg) - (Γ/2) ρ_eg
      ρ_gg = 1 - ρ_ee

    Using real Bloch vector components (u, v, w) where:
      u = Re(ρ_eg + ρ_ge)  (in-phase coherence)
      v = Im(ρ_eg - ρ_ge)  (quadrature coherence)
      w = ρ_ee - ρ_gg      (population inversion, -1 = ground, +1 = excited)

    The equations become:
      du/dt = -Γ/2 · u
      dv/dt = -Γ/2 · v + Ω_R · w
      dw/dt = -Γ(w + 1) - Ω_R · v

    Initial conditions: atom in ground state → u=0, v=0, w=-1 (ρ_ee=0).

    Parameters:
      gamma: spontaneous decay rate Γ (1/s)
      omega_rabi: Rabi frequency Ω_R (rad/s)
      n_lifetimes: number of lifetimes (1/Γ) to simulate
      dt_factor: time step as fraction of shortest timescale

    Returns dict with time arrays and phase analysis.
    """
    tau = 1.0 / gamma  # natural lifetime

    # Time step: must resolve both Rabi oscillations and decay
    shortest_timescale = min(tau, 2.0 * math.pi / max(omega_rabi, gamma))
    dt = shortest_timescale * dt_factor
    t_max = n_lifetimes * tau
    n_steps = int(t_max / dt)
    n_steps = min(n_steps, 10_000_000)  # safety cap

    # Arrays
    times = np.zeros(n_steps)
    rho_ee = np.zeros(n_steps)  # excited state population

    # Initial conditions
    u, v, w = 0.0, 0.0, -1.0  # ground state

    for i in range(n_steps):
        times[i] = i * dt
        rho_ee[i] = (w + 1.0) / 2.0  # ρ_ee = (w+1)/2

        # Bloch equation derivatives
        du = -(gamma / 2.0) * u
        dv = -(gamma / 2.0) * v + omega_rabi * w
        dw = -gamma * (w + 1.0) - omega_rabi * v

        # Euler integration (adequate for smooth Bloch dynamics with small dt)
        u += du * dt
        v += dv * dt
        w += dw * dt

    # --- Phase analysis ---
    # Find cycles: ρ_ee rises (accumulation) then falls (release)
    # Look for local maxima and minima to define complete cycles

    # Smooth the signal slightly for peak detection
    rho = rho_ee

    # Find peaks (local maxima) and troughs (local minima)
    peaks = []
    troughs = [0]  # start is a trough (ρ_ee = 0)

    for i in range(1, n_steps - 1):
        if rho[i] > rho[i - 1] and rho[i] >= rho[i + 1]:
            # Avoid noise: only count if this is a meaningful peak
            if rho[i] > 0.01:
                peaks.append(i)
        if rho[i] < rho[i - 1] and rho[i] <= rho[i + 1]:
            if len(peaks) > 0:  # only count troughs after a peak
                troughs.append(i)

    # Compute accumulation and release times for each complete half-cycle
    acc_times = []
    rel_times = []
    cycle_periods = []

    for j in range(len(peaks)):
        # Find the trough before this peak
        preceding_troughs = [t for t in troughs if t < peaks[j]]
        if not preceding_troughs:
            continue
        trough_before = preceding_troughs[-1]

        # Find the trough after this peak
        following_troughs = [t for t in troughs if t > peaks[j]]
        if not following_troughs:
            continue
        trough_after = following_troughs[0]

        t_acc = times[peaks[j]] - times[trough_before]
        t_rel = times[trough_after] - times[peaks[j]]

        if t_acc > 0 and t_rel > 0:
            acc_times.append(t_acc)
            rel_times.append(t_rel)
            cycle_periods.append(t_acc + t_rel)

    # Steady-state analysis
    # After several lifetimes, the Bloch equations reach steady state.
    # Steady-state ρ_ee = (Ω_R² / Γ²) / (1 + 2·Ω_R²/Γ²)  (on resonance)
    ss_rho_ee = (omega_rabi**2 / gamma**2) / (1.0 + 2.0 * omega_rabi**2 / gamma**2) if gamma > 0 else 0.5
    # Actual steady state from simulation (last 20% of data)
    late_start = int(0.8 * n_steps)
    actual_ss_mean = float(np.mean(rho[late_start:]))
    actual_ss_std = float(np.std(rho[late_start:]))

    # Compute ARA statistics across cycles
    if acc_times and rel_times:
        aras = [a / r for a, r in zip(acc_times, rel_times)]
        median_ara = float(np.median(aras))
        mean_ara = float(np.mean(aras))
        std_ara = float(np.std(aras))
        median_acc = float(np.median(acc_times))
        median_rel = float(np.median(rel_times))
        median_period = float(np.median(cycle_periods))
        n_cycles = len(aras)
    else:
        # No oscillatory cycles detected — system is overdamped
        aras = []
        median_ara = None
        mean_ara = None
        std_ara = None
        median_acc = None
        median_rel = None
        median_period = None
        n_cycles = 0

    # Subsample trajectory for JSON output
    stride = max(1, n_steps // 2000)
    sampled_times = times[::stride].tolist()
    sampled_rho = rho[::stride].tolist()

    return {
        "gamma_per_s": gamma,
        "omega_rabi_per_s": omega_rabi,
        "omega_over_gamma": omega_rabi / gamma if gamma > 0 else float("inf"),
        "n_cycles_detected": n_cycles,
        "median_t_acc_s": median_acc,
        "median_t_rel_s": median_rel,
        "median_period_s": median_period,
        "median_ara": median_ara,
        "mean_ara": mean_ara,
        "std_ara": std_ara,
        "all_aras": aras[:50],  # cap for JSON size
        "all_acc_times_s": acc_times[:50],
        "all_rel_times_s": rel_times[:50],
        "steady_state_rho_ee_theory": ss_rho_ee,
        "steady_state_rho_ee_measured": actual_ss_mean,
        "steady_state_rho_ee_std": actual_ss_std,
        "trajectory_sample": {
            "times_s": sampled_times[:500],
            "rho_ee": sampled_rho[:500],
        },
        "integration": {
            "dt_s": dt,
            "n_steps": n_steps,
            "t_max_s": t_max,
        },
    }


def analyze_atom(atom_key: str) -> dict:
    """Run the full analysis for one atom."""
    atom = ATOMS[atom_key]
    gamma = atom["einstein_A_per_s"]   # Γ = 1/τ
    tau = 1.0 / gamma
    wavelength = atom["wavelength_nm"]
    energy_j = photon_energy_j(wavelength)

    print(f"\n{'='*60}")
    print(f"  {atom['name']}")
    print(f"  Transition: {atom['transition']}")
    print(f"  Wavelength: {wavelength} nm")
    print(f"  Lifetime τ: {tau*1e9:.3f} ns")
    print(f"  Decay rate Γ: {gamma:.4e} s⁻¹")
    print(f"  Photon energy: {energy_j:.4e} J ({energy_j/EV_TO_J:.4f} eV)")
    print(f"{'='*60}")

    # Test multiple pump regimes
    regimes = {
        "weak_pump": 0.1 * gamma,       # Ω_R = 0.1 Γ (rate-equation limit)
        "moderate_pump": 1.0 * gamma,    # Ω_R = Γ (intermediate)
        "strong_pump": 5.0 * gamma,      # Ω_R = 5 Γ (Rabi oscillation regime)
        "very_strong_pump": 20.0 * gamma, # Ω_R = 20 Γ (deep Rabi regime)
    }

    regime_results = {}
    for regime_name, omega_r in regimes.items():
        print(f"\n  Regime: {regime_name} (Ω_R/Γ = {omega_r/gamma:.1f})")
        result = solve_bloch_equations(gamma, omega_r, n_lifetimes=30.0)
        regime_results[regime_name] = result

        if result["n_cycles_detected"] > 0:
            print(f"    Cycles detected: {result['n_cycles_detected']}")
            print(f"    Median T_acc: {result['median_t_acc_s']:.4e} s")
            print(f"    Median T_rel: {result['median_t_rel_s']:.4e} s")
            print(f"    Median ARA: {result['median_ara']:.6f}")
            print(f"    Mean ARA ± std: {result['mean_ara']:.6f} ± {result['std_ara']:.6f}")
        else:
            print(f"    No oscillatory cycles detected (overdamped regime)")
            print(f"    Steady-state ρ_ee: {result['steady_state_rho_ee_measured']:.6f}")

    # Also compute the spontaneous emission only (no pump) for reference:
    # An atom prepared in the excited state with no driving field.
    # This is a pure exponential decay: ρ_ee(t) = exp(-Γt)
    # In this case, the entire process is "release" (no accumulation phase).
    print(f"\n  Spontaneous emission only (no pump):")
    print(f"    ρ_ee(t) = exp(-Γt), pure exponential decay")
    print(f"    This is all release, no accumulation — not a cycle.")
    print(f"    The fluorescence cycle REQUIRES a pump to be oscillatory.")

    # Determine the physically meaningful ARA
    # The fluorescence cycle needs a pump to exist as an oscillation.
    # The natural regime for fluorescence is typically weak to moderate pump.
    # Report the regime where clean cycles exist.
    primary_regime = None
    primary_ara = None
    for rname in ["moderate_pump", "strong_pump", "very_strong_pump"]:
        r = regime_results[rname]
        if r["n_cycles_detected"] >= 3:
            primary_regime = rname
            primary_ara = r["median_ara"]
            break

    return {
        "atom": atom,
        "photon_energy_J": energy_j,
        "photon_energy_eV": energy_j / EV_TO_J,
        "natural_lifetime_s": tau,
        "decay_rate_gamma_per_s": gamma,
        "regimes": regime_results,
        "primary_regime": primary_regime,
        "primary_ara": primary_ara,
        "original_catalog_ara": {
            "Na_D_line": 47800000.0,
            "H_Lyman_alpha": 2360000.0,
        }.get(atom_key),
        "original_catalog_period_s": {
            "Na_D_line": 1.624e-8,
            "H_Lyman_alpha": 1.596e-9,
        }.get(atom_key),
    }


def main():
    print("=" * 70)
    print("Atomic Fluorescence ARA Computation — Optical Bloch Equations")
    print("=" * 70)

    results = {}
    for atom_key in ATOMS:
        results[atom_key] = analyze_atom(atom_key)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for atom_key, res in results.items():
        print(f"\n  {res['atom']['name']}:")
        print(f"    Original catalog ARA: {res['original_catalog_ara']:.2e}")
        if res["primary_ara"] is not None:
            print(f"    Computed ARA ({res['primary_regime']}): {res['primary_ara']:.6f}")
            print(f"    Period of fluorescence cycle: {res['regimes'][res['primary_regime']]['median_period_s']:.4e} s")
        else:
            print(f"    No oscillatory regime found with ≥3 cycles")
        print(f"    Natural lifetime (catalog period): {res['natural_lifetime_s']:.4e} s")

    # Write results
    # Clean up numpy types for JSON serialization
    def clean(obj):
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [clean(v) for v in obj]
        return obj

    OUT.write_text(json.dumps(clean(results), indent=2), encoding="utf-8")
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
