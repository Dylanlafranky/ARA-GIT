#!/usr/bin/env python3
"""
Compute the ARA of the U-238 alpha particle nuclear oscillation from first principles.

Method:
  1. Build the full radial potential V(r) that the alpha particle sees inside
     and near the surface of a U-238 (→ Th-234 + alpha) nucleus:
       - Woods-Saxon nuclear well (attractive)
       - Coulomb repulsion (outside the nuclear surface)
       - Centrifugal term (l=0 dominant channel for U-238 ground-state decay)
  2. Find the classical turning points where KE = 0 (V(r) = E_alpha).
  3. Numerically integrate the classical equation of motion dr/dt through one
     full oscillation inside the well.
  4. Decompose into accumulation and release phases:
       - Accumulation: alpha moving TOWARD the Coulomb barrier wall (outward),
         slowing down as KE converts to PE.  The system is storing energy in
         the Coulomb field.
       - Release: alpha moving AWAY from the barrier wall (inward), speeding
         up as PE converts to KE.  The stored potential energy is released as
         kinetic energy.
     The outer turning point is the phase boundary.
  5. Compute ARA = T_accumulation / T_release.
  6. Save full results to JSON with provenance.

Nuclear physics parameters from:
  - Krane, "Introductory Nuclear Physics" (1988)
  - Gamow model standard references
  - NUBASE2020 for Q_alpha of U-238

The l=0 channel dominates U-238 alpha decay (0+ → 0+ transition).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "quantum_u238_alpha_ara_result.json"

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
HBAR = 1.054571817e-34        # J·s
C = 2.99792458e8              # m/s
E_CHARGE = 1.602176634e-19    # C
MEV_TO_J = 1.602176634e-13    # J per MeV
AMU_TO_KG = 1.66053906660e-27 # kg per u
EPSILON_0 = 8.8541878128e-12  # F/m
FM_TO_M = 1.0e-15             # m per fm

# ---------------------------------------------------------------------------
# Nuclear parameters for U-238 → Th-234 + alpha
# ---------------------------------------------------------------------------
A_PARENT = 238                # U-238 mass number
Z_PARENT = 92                 # U-238 atomic number
A_DAUGHTER = 234              # Th-234 mass number
Z_DAUGHTER = 90               # Th-234 atomic number
Z_ALPHA = 2                   # alpha particle charge
A_ALPHA = 4                   # alpha particle mass number
M_ALPHA_AMU = 4.002603254     # alpha particle mass in u
M_DAUGHTER_AMU = 234.0436     # Th-234 mass in u (approximate)

Q_ALPHA_MEV = 4.270           # alpha decay Q-value (kinetic energy of emitted alpha
                               # in the lab frame, corrected for recoil)

# Woods-Saxon potential parameters (standard for heavy nuclei)
R0_FM = 1.25                  # nuclear radius parameter (fm)
A_DIFFUSE_FM = 0.65           # diffuseness parameter (fm)
V0_MEV = 50.0                 # well depth (MeV) — typical for alpha-nucleus potential

# Derived quantities
R_DAUGHTER_FM = R0_FM * A_DAUGHTER ** (1.0 / 3.0)  # daughter nuclear radius
R_ALPHA_FM = R0_FM * A_ALPHA ** (1.0 / 3.0)        # alpha nuclear radius
R_NUCLEAR_FM = R_DAUGHTER_FM + R_ALPHA_FM            # effective nuclear radius (sum)

M_ALPHA_KG = M_ALPHA_AMU * AMU_TO_KG
M_DAUGHTER_KG = M_DAUGHTER_AMU * AMU_TO_KG
# Reduced mass for alpha + daughter system
MU_KG = (M_ALPHA_KG * M_DAUGHTER_KG) / (M_ALPHA_KG + M_DAUGHTER_KG)

# Alpha kinetic energy in the center-of-mass frame
# E_cm = Q_alpha * M_daughter / (M_daughter + M_alpha)
E_CM_MEV = Q_ALPHA_MEV * M_DAUGHTER_AMU / (M_DAUGHTER_AMU + M_ALPHA_AMU)
E_CM_J = E_CM_MEV * MEV_TO_J


def coulomb_potential_mev(r_fm: float) -> float:
    """Coulomb potential between alpha (Z=2) and daughter (Z=90) at distance r."""
    if r_fm < 0.01:
        return 1e6  # regularise
    r_m = r_fm * FM_TO_M
    v_j = (Z_DAUGHTER * Z_ALPHA * E_CHARGE**2) / (4.0 * math.pi * EPSILON_0 * r_m)
    return v_j / MEV_TO_J


def woods_saxon_mev(r_fm: float) -> float:
    """Woods-Saxon nuclear potential (attractive, negative)."""
    return -V0_MEV / (1.0 + math.exp((r_fm - R_NUCLEAR_FM) / A_DIFFUSE_FM))


def total_potential_mev(r_fm: float) -> float:
    """Total potential = Woods-Saxon + Coulomb.  l=0, no centrifugal term."""
    return woods_saxon_mev(r_fm) + coulomb_potential_mev(r_fm)


def find_inner_turning_point(e_mev: float, r_start: float = 0.5, r_end: float = None) -> float:
    """Find the inner classical turning point where V(r) = E, searching outward."""
    if r_end is None:
        r_end = R_NUCLEAR_FM + 5.0
    # At very small r, the Coulomb term is huge (>> E), so we're above E.
    # The inner turning point is where V(r) first drops to E as we move outward.
    dr = 0.001  # fm step
    r = r_start
    # First, find where V(r) < E (we've entered the well)
    while r < r_end:
        if total_potential_mev(r) < e_mev:
            # Now back up to find the crossing
            r_cross = r
            # Bisection
            lo, hi = r - dr, r
            for _ in range(100):
                mid = (lo + hi) / 2.0
                if total_potential_mev(mid) > e_mev:
                    lo = mid
                else:
                    hi = mid
            return (lo + hi) / 2.0
        r += dr
    raise ValueError("Could not find inner turning point")


def find_outer_turning_point(e_mev: float, r_start: float = None) -> float:
    """Find the outer classical turning point where V(r) = E, searching outward
    from inside the well."""
    if r_start is None:
        r_start = R_NUCLEAR_FM - 2.0
    dr = 0.001
    r = r_start
    # Inside the well, V(r) < E.  Find where V(r) rises back to E.
    in_well = False
    while r < R_NUCLEAR_FM + 20.0:
        v = total_potential_mev(r)
        if v < e_mev:
            in_well = True
        if in_well and v >= e_mev:
            # Bisection
            lo, hi = r - dr, r
            for _ in range(100):
                mid = (lo + hi) / 2.0
                if total_potential_mev(mid) < e_mev:
                    lo = mid
                else:
                    hi = mid
            return (lo + hi) / 2.0
        r += dr
    raise ValueError("Could not find outer turning point")


def compute_trajectory(e_mev: float, n_steps: int = 200000):
    """Numerically integrate the classical radial trajectory for one full oscillation.

    The alpha starts at the inner turning point moving outward, reaches the
    outer turning point, and returns to the inner turning point.

    Returns arrays of (time_seconds, r_fm, v_fm_per_s, ke_mev, pe_mev).
    """
    r_inner = find_inner_turning_point(e_mev)
    r_outer = find_outer_turning_point(e_mev)
    e_j = e_mev * MEV_TO_J

    print(f"Inner turning point: {r_inner:.4f} fm")
    print(f"Outer turning point: {r_outer:.4f} fm")
    print(f"Nuclear radius (R_daughter + R_alpha): {R_NUCLEAR_FM:.4f} fm")
    print(f"Coulomb barrier peak: {coulomb_potential_mev(R_NUCLEAR_FM):.2f} MeV")
    print(f"Alpha CM energy: {e_mev:.4f} MeV")

    # Start just inside the inner turning point, moving outward
    r0_fm = r_inner + 0.001
    v_pot_j = total_potential_mev(r0_fm) * MEV_TO_J
    ke_j = e_j - v_pot_j
    if ke_j < 0:
        ke_j = 0.0
    # v = sqrt(2 * KE / mu), positive = outward
    v0 = math.sqrt(2.0 * ke_j / MU_KG) if ke_j > 0 else 0.0

    # Adaptive time step based on velocity
    # Rough estimate of traversal time: distance / average velocity
    avg_ke_mev = (e_mev - total_potential_mev((r_inner + r_outer) / 2.0))
    if avg_ke_mev <= 0:
        avg_ke_mev = 1.0  # fallback
    avg_v = math.sqrt(2.0 * avg_ke_mev * MEV_TO_J / MU_KG)
    est_half_period = (r_outer - r_inner) * FM_TO_M / avg_v
    dt = 2.0 * est_half_period / n_steps  # time step

    # Integrate using velocity-Verlet
    r = r0_fm
    v = v0  # fm/s but we work in SI then convert
    r_m = r * FM_TO_M
    v_ms = v  # already in m/s from sqrt(2*KE/mu)

    # Actually let's work entirely in SI (meters, seconds, kg, joules)
    r_si = r_inner * FM_TO_M + 0.001 * FM_TO_M
    v_pot_si = total_potential_mev(r_si / FM_TO_M) * MEV_TO_J
    ke_si = e_j - v_pot_si
    if ke_si < 0:
        ke_si = 0.0
    v_si = math.sqrt(2.0 * ke_si / MU_KG)  # outward positive

    times = [0.0]
    rs_fm = [r_si / FM_TO_M]
    vs = [v_si]

    def force_si(r_m):
        """Compute -dV/dr numerically."""
        dr = 1e-18  # 0.001 fm in meters
        v_plus = total_potential_mev((r_m + dr) / FM_TO_M) * MEV_TO_J
        v_minus = total_potential_mev((r_m - dr) / FM_TO_M) * MEV_TO_J
        return -(v_plus - v_minus) / (2.0 * dr)

    t = 0.0
    passed_outer = False
    completed = False

    # Phase tracking
    # outward leg = accumulation (approaching barrier, KE→PE)
    # inward leg = release (leaving barrier, PE→KE)
    outward_time = 0.0
    inward_time = 0.0
    direction = "outward"  # start moving outward

    for step in range(n_steps * 4):  # extra margin
        # Force at current position
        f = force_si(r_si)
        a = f / MU_KG

        # Velocity-Verlet integration
        v_half = v_si + 0.5 * a * dt
        r_si_new = r_si + v_half * dt
        f_new = force_si(r_si_new)
        a_new = f_new / MU_KG
        v_si_new = v_half + 0.5 * a_new * dt

        t += dt

        # Track phase time
        if direction == "outward":
            outward_time += dt
        else:
            inward_time += dt

        # Check for outer turning point (velocity changes sign, outward → inward)
        if v_si > 0 and v_si_new <= 0:
            passed_outer = True
            direction = "inward"

        # Check for return to inner turning point (velocity changes sign again,
        # inward → outward, after having passed the outer turning point)
        if passed_outer and v_si < 0 and v_si_new >= 0:
            completed = True

        r_si = r_si_new
        v_si = v_si_new

        # Store samples (not every step, to keep memory reasonable)
        if step % 100 == 0:
            times.append(t)
            rs_fm.append(r_si / FM_TO_M)
            vs.append(v_si)

        if completed:
            break

        # Safety: if r goes below 0.1 fm or above 100 fm, something is wrong
        if r_si / FM_TO_M < 0.05 or r_si / FM_TO_M > 100.0:
            print(f"WARNING: r out of bounds at step {step}: r={r_si/FM_TO_M:.4f} fm")
            break

    period_s = t
    # The full oscillation: outward leg + inward leg
    # Accumulation = outward (approaching Coulomb barrier, storing PE)
    # Release = inward (retreating from barrier, releasing PE as KE)

    return {
        "r_inner_fm": r_inner,
        "r_outer_fm": r_outer,
        "period_seconds": period_s,
        "t_accumulation_seconds": outward_time,
        "t_release_seconds": inward_time,
        "ara": outward_time / inward_time if inward_time > 0 else None,
        "completed": completed,
        "n_steps_used": step + 1,
        "dt_seconds": dt,
        "trajectory_samples": {
            "times_s": times[:200],  # cap for JSON size
            "r_fm": rs_fm[:200],
        },
    }


def potential_profile(r_min_fm=0.5, r_max_fm=30.0, n_points=500):
    """Generate the potential profile for diagnostics."""
    rs = np.linspace(r_min_fm, r_max_fm, n_points)
    vs_ws = [woods_saxon_mev(r) for r in rs]
    vs_coul = [coulomb_potential_mev(r) for r in rs]
    vs_total = [total_potential_mev(r) for r in rs]
    return {
        "r_fm": rs.tolist(),
        "V_woods_saxon_MeV": vs_ws,
        "V_coulomb_MeV": vs_coul,
        "V_total_MeV": vs_total,
    }


def main():
    print("=" * 70)
    print("U-238 Alpha Particle Nuclear Oscillation — ARA Computation")
    print("=" * 70)

    print(f"\nNuclear parameters:")
    print(f"  Parent: U-{A_PARENT} (Z={Z_PARENT})")
    print(f"  Daughter: Th-{A_DAUGHTER} (Z={Z_DAUGHTER})")
    print(f"  Q_alpha: {Q_ALPHA_MEV:.3f} MeV")
    print(f"  E_cm: {E_CM_MEV:.4f} MeV")
    print(f"  R_nuclear (R_d + R_a): {R_NUCLEAR_FM:.3f} fm")
    print(f"  Woods-Saxon depth: {V0_MEV:.1f} MeV")
    print(f"  Woods-Saxon diffuseness: {A_DIFFUSE_FM:.2f} fm")
    print(f"  Reduced mass: {MU_KG:.6e} kg")

    # Build potential profile
    print(f"\nBuilding potential profile...")
    profile = potential_profile()

    # Find barrier peak
    barrier_r = R_NUCLEAR_FM
    barrier_v = coulomb_potential_mev(R_NUCLEAR_FM)
    # Scan for actual peak
    for r in np.linspace(R_NUCLEAR_FM - 2.0, R_NUCLEAR_FM + 10.0, 1000):
        v = total_potential_mev(r)
        if v > barrier_v:
            barrier_v = v
            barrier_r = r
    print(f"  Coulomb barrier peak: {barrier_v:.2f} MeV at r = {barrier_r:.2f} fm")

    # Compute trajectory
    print(f"\nComputing classical trajectory...")
    traj = compute_trajectory(E_CM_MEV)

    print(f"\nResults:")
    print(f"  Completed full oscillation: {traj['completed']}")
    print(f"  Period: {traj['period_seconds']:.6e} s")
    print(f"  T_accumulation (outward, KE→PE): {traj['t_accumulation_seconds']:.6e} s")
    print(f"  T_release (inward, PE→KE): {traj['t_release_seconds']:.6e} s")
    print(f"  ARA = T_acc / T_rel: {traj['ara']:.6f}")

    # Compute action/pi
    energy_j = Q_ALPHA_MEV * MEV_TO_J
    action_pi = traj["period_seconds"] * energy_j / math.pi

    print(f"\n  Energy (Q_alpha): {energy_j:.4e} J")
    print(f"  Action/pi: {action_pi:.4e} J·s")
    print(f"  log10(Action/pi): {math.log10(action_pi) if action_pi > 0 else 'N/A':.2f}")

    # Oscillation frequency
    freq = 1.0 / traj["period_seconds"] if traj["period_seconds"] > 0 else 0
    print(f"  Oscillation frequency: {freq:.4e} Hz")

    # Compare to original catalog
    original_period = 1.41e17
    original_ara = 1.41e38
    print(f"\n  Original catalog period (half-life): {original_period:.2e} s")
    print(f"  Original catalog ARA: {original_ara:.2e}")
    print(f"  Period correction factor: {original_period / traj['period_seconds']:.2e}")

    # How many oscillations before tunneling (= half-life / period)
    half_life_s = 4.468e9 * 365.25 * 86400.0  # 4.468 Gyr in seconds
    n_attempts = half_life_s / traj["period_seconds"]
    tunneling_prob = math.log(2) / n_attempts  # per attempt
    print(f"  Half-life: {half_life_s:.4e} s")
    print(f"  Oscillations before tunneling: {n_attempts:.4e}")
    print(f"  Tunneling probability per attempt: {tunneling_prob:.4e}")

    # Build result
    result = {
        "system": "U-238 alpha decay nuclear oscillation",
        "method": "Classical trajectory in Woods-Saxon + Coulomb potential, velocity-Verlet integration",
        "parent": f"U-{A_PARENT} (Z={Z_PARENT})",
        "daughter": f"Th-{A_DAUGHTER} (Z={Z_DAUGHTER})",
        "nuclear_parameters": {
            "Q_alpha_MeV": Q_ALPHA_MEV,
            "E_cm_MeV": E_CM_MEV,
            "R_nuclear_fm": R_NUCLEAR_FM,
            "R_daughter_fm": R_DAUGHTER_FM,
            "R_alpha_fm": R_ALPHA_FM,
            "V0_MeV": V0_MEV,
            "diffuseness_fm": A_DIFFUSE_FM,
            "reduced_mass_kg": MU_KG,
            "barrier_peak_MeV": barrier_v,
            "barrier_peak_r_fm": barrier_r,
        },
        "trajectory": {
            "r_inner_fm": traj["r_inner_fm"],
            "r_outer_fm": traj["r_outer_fm"],
            "period_seconds": traj["period_seconds"],
            "t_accumulation_seconds": traj["t_accumulation_seconds"],
            "t_release_seconds": traj["t_release_seconds"],
            "accumulation_definition": "Outward leg: alpha moves toward Coulomb barrier, KE converts to PE (energy stored in field)",
            "release_definition": "Inward leg: alpha moves away from barrier, PE converts to KE (stored energy released)",
            "ara": traj["ara"],
            "completed": traj["completed"],
            "integration_steps": traj["n_steps_used"],
            "dt_seconds": traj["dt_seconds"],
        },
        "derived": {
            "oscillation_frequency_Hz": freq,
            "energy_per_cycle_J": energy_j,
            "action_over_pi_Js": action_pi,
            "log10_action_over_pi": math.log10(action_pi) if action_pi > 0 else None,
            "half_life_seconds": half_life_s,
            "oscillations_before_tunneling": n_attempts,
            "tunneling_probability_per_attempt": tunneling_prob,
        },
        "comparison_to_catalog": {
            "original_period_seconds": original_period,
            "original_ara": original_ara,
            "diagnosis": "Original catalog used the half-life as the period and mixed it with a nuclear-timescale release, producing an astronomically large ARA. The actual oscillatory system is the alpha particle bouncing inside the nuclear potential well.",
        },
        "potential_profile": profile,
    }

    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
