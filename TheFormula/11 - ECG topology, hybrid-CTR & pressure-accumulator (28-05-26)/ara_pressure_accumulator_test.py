"""
ara_pressure_accumulator_test.py

Tests the pressure accumulator hypothesis: the missing mechanism for sustained
oscillation on the ARA terrain without external data input.

Physics model (Dylan's corrected energy interpretation):
  - Phi valleys = MAXIMUM spin (cleanest energy expression, minimum friction)
  - Ridges = MAXIMUM friction (spin slows, pressure ACCUMULATES)
  - Floor provides periodic forcing at HOME/PHI^4 period
  - Each sphere's ARA position determines its energy expression
  - Contact transfer echoes through the stack

Pressure accumulator mechanism:
  1. At each time step, read terrain at current ARA position
  2. Compute friction from proximity to nearest ridge vs phi valley
  3. Near phi: low friction → spin expresses freely, pressure drains
  4. Near ridge: high friction → spin blocked, pressure BUILDS over time
  5. When accumulated pressure > ridge resistance → SPILLOVER
  6. Spillover launches ARA across ridge into next band
  7. Pressure resets, system finds new phi valley, spins freely
  8. Floor forcing re-accumulates pressure → next spillover event
  → Creates asymmetric buildup (slow) / release (fast) oscillation = ENSO

Three test modes:
  A. Calibrated: data-fed ARA at each step + accumulator (must not break shape)
  B. Free-run: after initial calibration, terrain+accumulator drives everything
  C. Comparison: original formula vs accumulator-enhanced
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ara_cross_rung_spin_transfer_test import HOME, PHI
from ara_fractal_sphere_terrain_reader import (
    binary_bounds,
    local_phi_points,
    clamp_ara,
    ara_to_value,
    value_to_ara,
    read_fractal_terrain,
    layer_terrain_read,
)
from ara_sphere_orientation_roll_predictor import EPS

# ─── Phi-friction profile ───────────────────────────────────────────────────

def phi_friction_profile(ara, depth=6):
    """
    Returns (spin_speed, friction, ridge_proximity) at a given ARA coordinate.

    Dylan's corrected model:
      phi valley → spin_speed ≈ 1.0 (max), friction ≈ 0.0 (min)
      ridge      → spin_speed ≈ 0.0 (min), friction ≈ 1.0 (max)

    The profile is computed from the weighted average across all terrain depths.
    """
    ara = clamp_ara(ara)
    total_weight = 0.0
    weighted_ridge_prox = 0.0
    weighted_phi_prox = 0.0

    for d in range(1, depth + 1):
        lo, hi, _ = binary_bounds(ara, d)
        width = hi - lo
        lower_phi, upper_phi = local_phi_points(lo, hi)

        # Distance to nearest phi valley (normalised to band width)
        phi_dist = min(abs(ara - lower_phi), abs(ara - upper_phi)) / max(width, EPS)

        # Distance to nearest ridge/boundary (normalised)
        ridge_dist = min(abs(ara - lo), abs(ara - hi)) / max(width, EPS)

        w = 1.0 / (PHI ** (d - 1))
        total_weight += w
        weighted_ridge_prox += w * (1.0 - ridge_dist)  # high when NEAR ridge
        weighted_phi_prox += w * (1.0 - phi_dist)       # high when NEAR phi

    ridge_proximity = weighted_ridge_prox / total_weight
    phi_proximity = weighted_phi_prox / total_weight

    # Friction: high near ridges, low near phi
    # Use soft mapping: friction = sigmoid(steepness * (ridge_prox - phi_prox))
    balance = ridge_proximity - phi_proximity
    friction = 1.0 / (1.0 + math.exp(-6.0 * balance))
    spin_speed = 1.0 - friction

    return {
        "spin_speed": spin_speed,
        "friction": friction,
        "ridge_proximity": ridge_proximity,
        "phi_proximity": phi_proximity,
    }


# ─── Pressure accumulator state ─────────────────────────────────────────────

class PressureAccumulator:
    """
    Tracks accumulated pressure at each layer across time steps.

    Physics:
      - Floor oscillates at FLOOR_PERIOD, injecting energy each step
      - Energy that can't express as spin (due to friction) becomes pressure
      - Pressure accumulates until it exceeds local ridge resistance
      - Spillover event: ARA jumps across ridge, pressure resets
    """

    def __init__(self, n_layers=5, ridge_threshold=1.0, pressure_decay=0.02,
                 floor_amplitude=0.35, spillover_kick=0.15):
        self.n_layers = n_layers
        self.ridge_threshold = ridge_threshold
        self.pressure_decay = pressure_decay   # slow leak even at ridges
        self.floor_amplitude = floor_amplitude
        self.spillover_kick = spillover_kick

        # State per layer
        self.pressure = [0.0] * n_layers       # accumulated pressure
        self.ara = [1.0] * n_layers             # current ARA position
        self.phase = [0.0] * n_layers           # current phase (degrees)
        self.spin_energy = [0.0] * n_layers     # current spin magnitude
        self.step = 0
        self.spillover_log = []                 # record spillover events

    def set_initial_state(self, layer_aras, layer_phases=None):
        """Set initial ARA positions from calibration data."""
        for i, ara in enumerate(layer_aras):
            if i < self.n_layers:
                self.ara[i] = clamp_ara(ara)
        if layer_phases:
            for i, ph in enumerate(layer_phases):
                if i < self.n_layers:
                    self.phase[i] = float(ph)

    def floor_forcing(self, t_months):
        """
        Floor oscillation at HOME/PHI^4 period.
        Returns a forcing vector (magnitude + direction).
        """
        floor_period = HOME / (PHI ** 4)
        phase = 2.0 * math.pi * t_months / floor_period
        # Multi-frequency floor: primary + first harmonic
        force = self.floor_amplitude * (
            math.sin(phase) + 0.3 * math.sin(2.0 * phase + 0.7)
        )
        return force

    def step_layer(self, layer_idx, floor_force, dt_months, lower_spin=None):
        """
        Advance one layer by dt_months with pressure accumulation.

        Returns dict with new state and any spillover event.
        """
        ara = self.ara[layer_idx]
        profile = phi_friction_profile(ara)
        friction = profile["friction"]
        spin_speed = profile["spin_speed"]

        # Layer period determines natural frequency
        layer_periods = [HOME / (PHI ** (4 - i)) for i in range(5)]
        period = layer_periods[layer_idx]
        frequency = math.sqrt(HOME / max(period, EPS))

        # Incoming energy: floor + lower layer contact transfer
        incoming = abs(floor_force) / (PHI ** layer_idx)  # attenuated by depth
        if lower_spin is not None:
            # Parity flip: each layer rolls opposite
            parity = (-1.0) ** layer_idx
            speed_ratio = math.sqrt(period / max(layer_periods[max(0, layer_idx - 1)], EPS))
            contact_transfer = 0.34 * speed_ratio * abs(lower_spin)
            incoming += contact_transfer

        # Split energy between spin expression and pressure buildup
        # At phi valley: most energy → spin (friction low)
        # At ridge: most energy → pressure (friction high)
        expressed_energy = incoming * spin_speed
        blocked_energy = incoming * friction

        # Pressure accumulates from blocked energy, decays slowly
        self.pressure[layer_idx] += blocked_energy * dt_months
        self.pressure[layer_idx] *= (1.0 - self.pressure_decay)  # slow leak
        self.pressure[layer_idx] = max(0.0, self.pressure[layer_idx])

        # Spin energy from expressed portion
        self.spin_energy[layer_idx] = expressed_energy * frequency

        # Read terrain to get natural slope direction
        terrain_terms = {
            "contact_pressure": incoming,
            "lower_drive": floor_force,
            "upper_gate": 0.0,
        }
        terrain = read_fractal_terrain(ara, ara, terrain_terms)
        natural_direction = terrain["weighted_slope"]

        # Normal ARA displacement from spin
        spin_displacement = 0.34 * expressed_energy * math.copysign(1.0, natural_direction)

        # Check for spillover
        spillover_event = False
        lo, hi, _ = binary_bounds(ara, 1)  # dominant band
        width = hi - lo
        ridge_resistance = profile["ridge_proximity"] * self.ridge_threshold

        if self.pressure[layer_idx] > ridge_resistance and ridge_resistance > 0.1:
            # SPILLOVER: pressure exceeds ridge resistance
            spillover_event = True
            excess = self.pressure[layer_idx] - ridge_resistance

            # Kick direction: toward the slope the pressure was building against
            kick_direction = math.copysign(1.0, natural_direction)
            kick_magnitude = self.spillover_kick * (1.0 + excess)

            new_ara = clamp_ara(ara + kick_direction * kick_magnitude)
            self.pressure[layer_idx] = 0.0  # reset after spillover

            self.spillover_log.append({
                "step": self.step,
                "layer": layer_idx,
                "old_ara": ara,
                "new_ara": new_ara,
                "excess_pressure": excess,
                "kick": kick_direction * kick_magnitude,
            })
        else:
            # Normal displacement: spin + terrain pull
            terrain_pull = 0.78 * terrain["weighted_slope"] * terrain["force_gain"]
            new_ara = clamp_ara(ara + spin_displacement + terrain_pull * 0.1 * dt_months)

        # Phase advancement
        floor_phase_rate = (dt_months / HOME) * 360.0
        self.phase[layer_idx] = (self.phase[layer_idx] + floor_phase_rate * frequency) % 360.0

        # Update state
        self.ara[layer_idx] = new_ara

        return {
            "ara": new_ara,
            "old_ara": ara,
            "spin_speed": spin_speed,
            "friction": friction,
            "pressure": self.pressure[layer_idx],
            "spin_energy": self.spin_energy[layer_idx],
            "incoming": incoming,
            "expressed": expressed_energy,
            "blocked": blocked_energy,
            "displacement": new_ara - ara,
            "spillover": spillover_event,
            "natural_direction": natural_direction,
            "terrain_slope": terrain["weighted_slope"],
        }


def run_free_mode(n_steps=300, dt_months=3.0, calibration_steps=20,
                  calibration_aras=None, ridge_threshold=1.0,
                  floor_amplitude=0.35, spillover_kick=0.15,
                  pressure_decay=0.02):
    """
    Run the pressure accumulator in free mode.

    First `calibration_steps` use provided ARA values (from data).
    After that, the system runs on its own terrain-driven dynamics.
    """
    acc = PressureAccumulator(
        n_layers=5,
        ridge_threshold=ridge_threshold,
        pressure_decay=pressure_decay,
        floor_amplitude=floor_amplitude,
        spillover_kick=spillover_kick,
    )

    # Initial state: start near middle of ARA range
    if calibration_aras and len(calibration_aras) > 0:
        first_aras = calibration_aras[0]
        acc.set_initial_state(first_aras)
    else:
        acc.set_initial_state([1.0, 1.0, 1.0, 1.0, 1.0])

    history = []

    for step in range(n_steps):
        t_months = step * dt_months
        acc.step += 1

        floor_force = acc.floor_forcing(t_months)

        # During calibration, reset ARA from data
        if calibration_aras and step < calibration_steps and step < len(calibration_aras):
            acc.set_initial_state(calibration_aras[step])

        # Propagate through layers
        layer_results = []
        lower_spin = None
        for i in range(5):
            result = acc.step_layer(i, floor_force, dt_months, lower_spin)
            layer_results.append(result)
            lower_spin = result["spin_energy"]

        # Measured sphere (last layer) gives the output value
        measured_ara = acc.ara[4]
        measured_value = ara_to_value(measured_ara)

        record = {
            "step": step,
            "t_months": t_months,
            "floor_force": floor_force,
            "measured_ara": measured_ara,
            "measured_value": measured_value,
            "calibrated": (calibration_aras is not None and step < calibration_steps),
            "layers": layer_results,
            "pressures": list(acc.pressure),
            "aras": list(acc.ara),
        }
        history.append(record)

    return history, acc.spillover_log


def extract_calibration_aras(formula_data, horizon="6"):
    """Extract layer ARA values from formula results for calibration."""
    recs = formula_data["viz_records"][horizon]
    aras_list = []
    for r in recs:
        layer_aras = [layer["ara"] for layer in r["formula"]["layers"]]
        aras_list.append(layer_aras)
    return aras_list


def run_test():
    print("=" * 100)
    print("ARA PRESSURE ACCUMULATOR TEST")
    print("=" * 100)
    print()
    print("Hypothesis: Pressure builds at ridges over time. When it exceeds")
    print("ridge resistance, spillover launches ARA into next band. This")
    print("creates asymmetric buildup/release oscillation without external data.")
    print()

    # ─── 1. Verify phi-friction profile ──────────────────────────────────
    print("1. Phi-friction profile verification")
    print("-" * 60)
    test_points = [0.0, 0.382, 0.5, 0.618, 1.0, 1.236, 1.382, 1.618, 2.0]
    for ara in test_points:
        p = phi_friction_profile(ara)
        label = ""
        if ara in [0.0, 2.0]:
            label = " ← BOUNDARY RIDGE"
        elif abs(ara - 1.0) < 0.01:
            label = " ← MID-POINT"
        elif abs(ara - (2.0 - 2.0/PHI)) < 0.05 or abs(ara - (2.0/PHI)) < 0.05:
            label = " ← PHI VALLEY"
        print(f"  ARA={ara:.3f}: spin={p['spin_speed']:.3f} friction={p['friction']:.3f} "
              f"ridge_prox={p['ridge_proximity']:.3f} phi_prox={p['phi_proximity']:.3f}{label}")
    print()

    # ─── 2. Load formula data for calibration ────────────────────────────
    formula_path = HERE / "ara_layered_sand_single_formula_result.json"
    if not formula_path.exists():
        print("ERROR: formula result not found. Run ara_layered_sand_single_formula.py first.")
        return

    formula_data = json.loads(formula_path.read_text(encoding="utf-8"))

    # ─── 3. Parameter sweep for best oscillation ─────────────────────────
    print("2. Parameter sweep for sustained oscillation")
    print("-" * 60)

    best_config = None
    best_osc_score = -1

    configs = [
        {"ridge_threshold": 0.5, "floor_amplitude": 0.25, "spillover_kick": 0.10, "pressure_decay": 0.01},
        {"ridge_threshold": 0.5, "floor_amplitude": 0.35, "spillover_kick": 0.15, "pressure_decay": 0.02},
        {"ridge_threshold": 0.8, "floor_amplitude": 0.35, "spillover_kick": 0.12, "pressure_decay": 0.01},
        {"ridge_threshold": 0.8, "floor_amplitude": 0.50, "spillover_kick": 0.20, "pressure_decay": 0.02},
        {"ridge_threshold": 1.0, "floor_amplitude": 0.50, "spillover_kick": 0.20, "pressure_decay": 0.01},
        {"ridge_threshold": 1.0, "floor_amplitude": 0.70, "spillover_kick": 0.25, "pressure_decay": 0.02},
        {"ridge_threshold": 0.3, "floor_amplitude": 0.40, "spillover_kick": 0.18, "pressure_decay": 0.03},
        {"ridge_threshold": 0.3, "floor_amplitude": 0.60, "spillover_kick": 0.25, "pressure_decay": 0.01},
        {"ridge_threshold": 0.6, "floor_amplitude": 0.80, "spillover_kick": 0.30, "pressure_decay": 0.02},
        {"ridge_threshold": 0.4, "floor_amplitude": 1.00, "spillover_kick": 0.35, "pressure_decay": 0.01},
        {"ridge_threshold": 0.2, "floor_amplitude": 0.50, "spillover_kick": 0.20, "pressure_decay": 0.05},
        {"ridge_threshold": 0.15, "floor_amplitude": 0.60, "spillover_kick": 0.30, "pressure_decay": 0.03},
    ]

    cal_aras = extract_calibration_aras(formula_data, "6")

    for cfg in configs:
        history, spill_log = run_free_mode(
            n_steps=200, dt_months=3.0,
            calibration_steps=20,
            calibration_aras=cal_aras,
            **cfg,
        )

        # Measure oscillation quality in the free-run portion (after calibration)
        free_values = [h["measured_value"] for h in history if not h["calibrated"]]
        if len(free_values) < 20:
            continue

        std = np.std(free_values)
        mean_val = np.mean(free_values)

        # Count zero-crossings (oscillation frequency proxy)
        crossings = 0
        for i in range(1, len(free_values)):
            if free_values[i] * free_values[i-1] < 0:
                crossings += 1

        # Count spillover events in free-run period
        free_spills = [s for s in spill_log if s["step"] >= 20]

        # Oscillation score: want high std (amplitude) × crossings (frequency)
        # Penalise collapse (std < 0.1) and chaos (crossings > 100)
        osc_score = std * min(crossings, 50) * (1.0 if std > 0.1 else 0.01)

        print(f"  thresh={cfg['ridge_threshold']:.2f} floor_amp={cfg['floor_amplitude']:.2f} "
              f"kick={cfg['spillover_kick']:.2f} decay={cfg['pressure_decay']:.2f} → "
              f"std={std:.3f} crossings={crossings} spills={len(free_spills)} "
              f"score={osc_score:.3f}")

        if osc_score > best_osc_score:
            best_osc_score = osc_score
            best_config = cfg

    print()
    if best_config:
        print(f"  BEST: {best_config} → score={best_osc_score:.3f}")
    print()

    # ─── 4. Run best config in detail ────────────────────────────────────
    print("3. Detailed run with best configuration")
    print("-" * 60)

    if best_config is None:
        best_config = configs[0]

    history, spill_log = run_free_mode(
        n_steps=300, dt_months=3.0,
        calibration_steps=20,
        calibration_aras=cal_aras,
        **best_config,
    )

    # Calibrated portion
    cal_values = [h["measured_value"] for h in history if h["calibrated"]]
    free_values = [h["measured_value"] for h in history if not h["calibrated"]]
    free_aras = [h["measured_ara"] for h in history if not h["calibrated"]]

    print(f"  Calibrated steps: {len(cal_values)}")
    print(f"  Free-run steps: {len(free_values)}")
    print(f"  Calibrated value range: [{min(cal_values):.3f}, {max(cal_values):.3f}]")
    print(f"  Free-run value range:   [{min(free_values):.3f}, {max(free_values):.3f}]")
    print(f"  Free-run std:           {np.std(free_values):.4f}")
    print(f"  Free-run ARA range:     [{min(free_aras):.4f}, {max(free_aras):.4f}]")
    print()

    # Zero crossings in free portion
    crossings = 0
    for i in range(1, len(free_values)):
        if free_values[i] * free_values[i-1] < 0:
            crossings += 1
    mean_period = len(free_values) * 3.0 / max(crossings / 2, 0.5)  # months per full cycle

    print(f"  Zero crossings: {crossings}")
    print(f"  Approx oscillation period: {mean_period:.1f} months")
    print(f"  (ENSO typical: 24-84 months)")
    print()

    # Spillover events
    free_spills = [s for s in spill_log if s["step"] >= 20]
    print(f"  Spillover events (free-run): {len(free_spills)}")
    for s in free_spills[:10]:
        t = s["step"] * 3.0
        print(f"    t={t:.0f}mo layer={s['layer']} "
              f"ARA {s['old_ara']:.4f} → {s['new_ara']:.4f} "
              f"kick={s['kick']:+.4f} excess={s['excess_pressure']:.3f}")
    if len(free_spills) > 10:
        print(f"    ... and {len(free_spills) - 10} more")
    print()

    # Pressure trace for measured layer
    print("  Pressure trace (measured layer, every 10 steps):")
    for h in history[::10]:
        bar_len = int(min(h["pressures"][4], 2.0) * 25)
        bar = "█" * bar_len
        spill_mark = " *SPILL*" if h["layers"][4]["spillover"] else ""
        mode = "CAL" if h["calibrated"] else "FREE"
        print(f"    t={h['t_months']:6.0f}mo [{mode:4s}] p={h['pressures'][4]:.3f} "
              f"ara={h['aras'][4]:.4f} val={h['measured_value']:+.3f} |{bar}{spill_mark}")
    print()

    # ─── 5. Collapse diagnostic ──────────────────────────────────────────
    print("4. Collapse diagnostic")
    print("-" * 60)

    # Check if values converge to a fixed point
    last_50 = free_values[-50:]
    last_50_std = np.std(last_50)
    last_50_mean = np.mean(last_50)

    if last_50_std < 0.05:
        # Check what ARA it converged to
        last_50_aras = free_aras[-50:]
        converged_ara = np.mean(last_50_aras)
        profile = phi_friction_profile(converged_ara)
        print(f"  ⚠ ATTRACTOR COLLAPSE detected!")
        print(f"  Converged to ARA={converged_ara:.4f}, value={last_50_mean:.3f}")
        print(f"  At this point: spin={profile['spin_speed']:.3f}, friction={profile['friction']:.3f}")

        lo, hi, _ = binary_bounds(converged_ara, 1)
        lp, up = local_phi_points(lo, hi)
        print(f"  Dominant band: [{lo:.4f}, {hi:.4f}]")
        print(f"  Phi valleys: {lp:.4f}, {up:.4f}")
        print(f"  Distance to nearest phi: {min(abs(converged_ara-lp), abs(converged_ara-up)):.4f}")
        print()
        print("  WHY: Even with pressure accumulator, once the system reaches a phi")
        print("  valley, friction → 0, so NO pressure accumulates. The floor forcing")
        print("  expresses entirely as spin, never building enough pressure to escape.")
        print()
        print("  POSSIBLE FIX: The floor doesn't just add spin - it adds MOMENTUM")
        print("  that carries the sphere THROUGH phi valleys toward the next ridge.")
        print("  Inertia. A sphere at max spin doesn't stop at phi - it overshoots.")
    else:
        print(f"  ✓ Oscillation SUSTAINED in last 50 steps!")
        print(f"  std={last_50_std:.4f}, mean={last_50_mean:.3f}")

        # Check if it matches ENSO characteristics
        if 18 < mean_period < 96:
            print(f"  ✓ Period ({mean_period:.0f} months) is ENSO-like!")
        else:
            print(f"  ⚠ Period ({mean_period:.0f} months) outside ENSO range (18-96 months)")

    print()

    # ─── 6. Inertia variant ──────────────────────────────────────────────
    print("5. INERTIA VARIANT: sphere overshoots phi valleys")
    print("-" * 60)
    print("  Adding momentum/inertia: sphere doesn't stop at phi, it overshoots")
    print("  toward the next ridge, where pressure builds again.")
    print()

    history_inertia, spill_log_inertia = run_free_mode_with_inertia(
        n_steps=300, dt_months=3.0,
        calibration_steps=20,
        calibration_aras=cal_aras,
        **{**best_config, "inertia": 0.85},
    )

    free_values_i = [h["measured_value"] for h in history_inertia if not h["calibrated"]]
    free_aras_i = [h["measured_ara"] for h in history_inertia if not h["calibrated"]]

    if free_values_i:
        std_i = np.std(free_values_i)
        crossings_i = sum(1 for i in range(1, len(free_values_i))
                         if free_values_i[i] * free_values_i[i-1] < 0)
        period_i = len(free_values_i) * 3.0 / max(crossings_i / 2, 0.5)
        last_50_i = free_values_i[-50:]
        last_50_std_i = np.std(last_50_i)

        print(f"  Free-run value range: [{min(free_values_i):.3f}, {max(free_values_i):.3f}]")
        print(f"  Free-run std:         {std_i:.4f}")
        print(f"  Zero crossings:       {crossings_i}")
        print(f"  Approx period:        {period_i:.1f} months")
        free_spills_i = [s for s in spill_log_inertia if s["step"] >= 20]
        print(f"  Spillover events:     {len(free_spills_i)}")
        print()

        if last_50_std_i < 0.05:
            converged = np.mean(free_aras_i[-50:])
            print(f"  ⚠ Still collapses to ARA={converged:.4f}")
        else:
            print(f"  ✓ SUSTAINED oscillation! Last-50 std={last_50_std_i:.4f}")

        # Pressure trace
        print()
        print("  Pressure+inertia trace (measured layer, every 10 steps):")
        for h in history_inertia[::10]:
            bar_len = int(min(h["pressures"][4], 2.0) * 25)
            bar = "█" * bar_len
            mode = "CAL" if h["calibrated"] else "FREE"
            print(f"    t={h['t_months']:6.0f}mo [{mode:4s}] p={h['pressures'][4]:.3f} "
                  f"ara={h['aras'][4]:.4f} val={h['measured_value']:+.3f} vel={h.get('velocity', 0.0):+.4f} |{bar}")

    print()

    # ─── Save results ────────────────────────────────────────────────────
    out = {
        "date": "2026-05-29",
        "method": "pressure_accumulator_test",
        "best_config": best_config,
        "best_osc_score": best_osc_score,
        "n_free_steps": len(free_values),
        "free_run_std": float(np.std(free_values)),
        "free_run_std_inertia": float(np.std(free_values_i)) if free_values_i else None,
        "zero_crossings": crossings,
        "zero_crossings_inertia": crossings_i if free_values_i else None,
        "spillover_events": len(free_spills),
        "spillover_events_inertia": len(free_spills_i) if free_values_i else None,
        "free_run_values": [float(v) for v in free_values],
        "free_run_values_inertia": [float(v) for v in free_values_i] if free_values_i else [],
        "free_run_aras": [float(a) for a in free_aras],
        "free_run_aras_inertia": [float(a) for a in free_aras_i] if free_aras_i else [],
        "spillover_log": spill_log,
        "spillover_log_inertia": spill_log_inertia if spill_log_inertia else [],
    }

    out_path = HERE / "ara_pressure_accumulator_test_result.json"
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Saved → {out_path}")


# ─── Inertia variant ────────────────────────────────────────────────────────

class PressureAccumulatorWithInertia(PressureAccumulator):
    """
    Extended accumulator with MOMENTUM/INERTIA.

    Key insight: a sphere at max spin in a phi valley has VELOCITY.
    It doesn't stop there — it overshoots toward the next ridge.
    The higher the spin speed (phi valley), the MORE it overshoots.

    This creates the oscillation:
      phi valley → max spin → overshoot → approach ridge →
      friction increases → pressure builds → spillover →
      land in new valley → max spin → overshoot → ...
    """

    def __init__(self, *args, inertia=0.85, **kwargs):
        super().__init__(*args, **kwargs)
        self.inertia = inertia  # momentum retention factor (0-1)
        self.velocity = [0.0] * self.n_layers  # ARA velocity per layer

    def set_initial_state(self, layer_aras, layer_phases=None):
        super().set_initial_state(layer_aras, layer_phases)
        # Don't reset velocity during calibration — let it build

    def step_layer(self, layer_idx, floor_force, dt_months, lower_spin=None):
        ara = self.ara[layer_idx]
        profile = phi_friction_profile(ara)
        friction = profile["friction"]
        spin_speed = profile["spin_speed"]

        layer_periods = [HOME / (PHI ** (4 - i)) for i in range(5)]
        period = layer_periods[layer_idx]
        frequency = math.sqrt(HOME / max(period, EPS))

        # Incoming energy
        incoming = abs(floor_force) / (PHI ** layer_idx)
        if lower_spin is not None:
            parity = (-1.0) ** layer_idx
            speed_ratio = math.sqrt(period / max(layer_periods[max(0, layer_idx - 1)], EPS))
            contact_transfer = 0.34 * speed_ratio * abs(lower_spin)
            incoming += contact_transfer

        # Energy split
        expressed_energy = incoming * spin_speed
        blocked_energy = incoming * friction

        # Pressure accumulation
        self.pressure[layer_idx] += blocked_energy * dt_months
        self.pressure[layer_idx] *= (1.0 - self.pressure_decay)
        self.pressure[layer_idx] = max(0.0, self.pressure[layer_idx])

        self.spin_energy[layer_idx] = expressed_energy * frequency

        # Terrain reading for direction
        terrain_terms = {
            "contact_pressure": incoming,
            "lower_drive": floor_force,
            "upper_gate": 0.0,
        }
        terrain = read_fractal_terrain(ara, ara, terrain_terms)
        natural_direction = terrain["weighted_slope"]

        # ─── INERTIA: velocity carries the sphere through phi valleys ────
        # Force from terrain slope (toward phi valley)
        terrain_force = 0.78 * terrain["weighted_slope"] * terrain["force_gain"]

        # Force from spin expression (higher spin = more displacement force)
        spin_force = 0.34 * expressed_energy * math.copysign(1.0,
            self.velocity[layer_idx] if abs(self.velocity[layer_idx]) > EPS
            else natural_direction)

        # Floor forcing adds directional push
        floor_direction = math.copysign(1.0, floor_force)
        floor_push = 0.1 * abs(floor_force) / max(PHI ** layer_idx, EPS)

        # Friction acts as drag on velocity
        drag = friction * abs(self.velocity[layer_idx]) * 0.5

        # Update velocity: inertia * old_velocity + new forces - drag
        total_force = terrain_force * 0.1 + spin_force + floor_push * floor_direction
        self.velocity[layer_idx] = (
            self.inertia * self.velocity[layer_idx] +
            total_force * dt_months * 0.01 -
            math.copysign(drag, self.velocity[layer_idx]) * dt_months * 0.01
        )

        # Clamp velocity to prevent explosion
        self.velocity[layer_idx] = max(-0.15, min(0.15, self.velocity[layer_idx]))

        # Check spillover
        spillover_event = False
        lo, hi, _ = binary_bounds(ara, 1)
        ridge_resistance = profile["ridge_proximity"] * self.ridge_threshold

        if self.pressure[layer_idx] > ridge_resistance and ridge_resistance > 0.1:
            spillover_event = True
            excess = self.pressure[layer_idx] - ridge_resistance
            kick_direction = math.copysign(1.0, self.velocity[layer_idx] if abs(self.velocity[layer_idx]) > EPS else natural_direction)
            kick_magnitude = self.spillover_kick * (1.0 + excess)

            new_ara = clamp_ara(ara + kick_direction * kick_magnitude)
            self.velocity[layer_idx] += kick_direction * kick_magnitude * 0.5  # spillover adds to momentum
            self.velocity[layer_idx] = max(-0.15, min(0.15, self.velocity[layer_idx]))
            self.pressure[layer_idx] = 0.0

            self.spillover_log.append({
                "step": self.step,
                "layer": layer_idx,
                "old_ara": ara,
                "new_ara": new_ara,
                "excess_pressure": excess,
                "kick": kick_direction * kick_magnitude,
            })
        else:
            # Normal displacement from velocity
            new_ara = clamp_ara(ara + self.velocity[layer_idx])

        # Phase
        floor_phase_rate = (dt_months / HOME) * 360.0
        self.phase[layer_idx] = (self.phase[layer_idx] + floor_phase_rate * frequency) % 360.0

        self.ara[layer_idx] = new_ara

        return {
            "ara": new_ara,
            "old_ara": ara,
            "spin_speed": spin_speed,
            "friction": friction,
            "pressure": self.pressure[layer_idx],
            "spin_energy": self.spin_energy[layer_idx],
            "incoming": incoming,
            "expressed": expressed_energy,
            "blocked": blocked_energy,
            "displacement": new_ara - ara,
            "spillover": spillover_event,
            "natural_direction": natural_direction,
            "terrain_slope": terrain["weighted_slope"],
            "velocity": self.velocity[layer_idx],
        }


def run_free_mode_with_inertia(n_steps=300, dt_months=3.0, calibration_steps=20,
                                calibration_aras=None, ridge_threshold=1.0,
                                floor_amplitude=0.35, spillover_kick=0.15,
                                pressure_decay=0.02, inertia=0.85):
    """Run with inertia variant."""
    acc = PressureAccumulatorWithInertia(
        n_layers=5,
        ridge_threshold=ridge_threshold,
        pressure_decay=pressure_decay,
        floor_amplitude=floor_amplitude,
        spillover_kick=spillover_kick,
        inertia=inertia,
    )

    if calibration_aras and len(calibration_aras) > 0:
        acc.set_initial_state(calibration_aras[0])
    else:
        acc.set_initial_state([1.0, 1.0, 1.0, 1.0, 1.0])

    history = []

    for step in range(n_steps):
        t_months = step * dt_months
        acc.step += 1

        floor_force = acc.floor_forcing(t_months)

        if calibration_aras and step < calibration_steps and step < len(calibration_aras):
            acc.set_initial_state(calibration_aras[step])

        layer_results = []
        lower_spin = None
        for i in range(5):
            result = acc.step_layer(i, floor_force, dt_months, lower_spin)
            layer_results.append(result)
            lower_spin = result["spin_energy"]

        measured_ara = acc.ara[4]
        measured_value = ara_to_value(measured_ara)

        record = {
            "step": step,
            "t_months": t_months,
            "floor_force": floor_force,
            "measured_ara": measured_ara,
            "measured_value": measured_value,
            "calibrated": (calibration_aras is not None and step < calibration_steps),
            "layers": layer_results,
            "pressures": list(acc.pressure),
            "aras": list(acc.ara),
            "velocity": acc.velocity[4],
        }
        history.append(record)

    return history, acc.spillover_log


if __name__ == "__main__":
    run_test()
