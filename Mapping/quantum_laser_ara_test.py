#!/usr/bin/env python3
"""
Compute the ARA of laser pulse cycles from first principles using laser rate equations.

Systems:
  1. Mode-locked laser (Ti:sapphire-class, ~80 MHz rep rate, ~100 fs pulses)
  2. Q-switched laser (Nd:YAG-class, ~5 kHz rep rate, ~10 ns pulses)

Method:
  Solve the standard laser rate equations for the intracavity photon number
  n(t) and population inversion N(t):

    dN/dt = R_pump - N/τ_upper - B·N·n          (gain medium)
    dn/dt = B·N·n - n/τ_cav + spontaneous_term  (optical field)

  where:
    R_pump  = pump rate (excitation per second)
    τ_upper = upper state lifetime
    B       = stimulated emission cross-section × c / V_mode
    τ_cav   = cavity photon lifetime (round-trip time / loss)

  For mode-locked lasers, we add a saturable absorber term that creates
  pulse formation via self-amplitude modulation.

  For Q-switched lasers, we modulate the cavity loss (Q-factor) to build
  up large inversion then dump it rapidly.

  Phase decomposition:
    We track the total stored energy in the system E_total(t) = E_gain(t) + E_field(t).
    - ACCUMULATION: dE_total/dt > 0  (system is gaining net energy from pump)
    - RELEASE: dE_total/dt < 0  (system is losing net energy as output)
    T_acc and T_rel are measured from the actual energy flow waveform.

  This lets the physics determine the phase boundary, not our assumptions
  about which component is "accumulating" or "releasing."

Physical parameters from:
  - Siegman, "Lasers" (1986)
  - Saleh & Teich, "Fundamentals of Photonics" (2007)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "quantum_laser_ara_result.json"

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------
HBAR = 1.054571817e-34
H_PLANCK = 6.62607015e-34
C = 2.99792458e8
EV_TO_J = 1.602176634e-19


# ===================================================================
# Q-SWITCHED LASER (Nd:YAG class)
# ===================================================================

def simulate_q_switched():
    """Simulate a Q-switched Nd:YAG laser using standard rate equations.

    The Q-switch cycle:
      1. Cavity loss is held high (Q is low) → no lasing, pump builds inversion
      2. Q-switch opens (loss drops) → massive inversion dumps into giant pulse
      3. Pulse depletes inversion → cavity loss restored → back to step 1

    Rate equations (Siegman notation):
      dN/dt = R_pump - N/τ_f - γ·c·σ·N·φ
      dφ/dt = γ·c·σ·N·φ - φ/τ_c + R_sp

    where:
      N = population inversion density (m⁻³)
      φ = intracavity photon density (m⁻³)
      R_pump = pump rate density (m⁻³ s⁻¹)
      τ_f = fluorescence lifetime of upper laser level
      σ = stimulated emission cross-section
      γ = mode overlap factor
      τ_c = cavity photon lifetime
      R_sp = spontaneous emission into lasing mode (small seed)
    """
    print("\n" + "=" * 60)
    print("  Q-Switched Laser (Nd:YAG class)")
    print("=" * 60)

    # Nd:YAG parameters
    wavelength = 1064e-9       # m
    sigma = 2.8e-19 * 1e-4     # stimulated emission cross section (2.8e-19 cm² → m²)
    tau_f = 230e-6             # fluorescence lifetime (230 μs)
    n_refr = 1.82              # refractive index of YAG
    photon_energy = H_PLANCK * C / wavelength  # 1.87e-19 J

    # Cavity parameters (typical flash-pumped Q-switched)
    cavity_length = 0.15       # m (15 cm cavity)
    crystal_length = 0.05      # m (5 cm rod)
    mode_area = 3e-6           # m² (beam cross-section in rod)
    mode_volume = mode_area * crystal_length
    output_coupling = 0.3      # 30% output coupler
    internal_loss = 0.05       # 5% internal loss per round trip
    round_trip_time = 2 * cavity_length / C  # ~1 ns

    # Cavity photon lifetime
    loss_per_rt = output_coupling + internal_loss
    tau_c_lasing = round_trip_time / loss_per_rt  # ~2.9 ns when Q is high (lasing)
    tau_c_blocked = round_trip_time / 0.99         # ~1 ns when Q is low (blocked)

    # Pump rate — chosen to reach ~3× threshold inversion in 200 μs
    N_threshold = 1.0 / (sigma * C / n_refr * tau_c_lasing)  # threshold inversion
    R_pump = 3.0 * N_threshold / (200e-6)  # pump to 3× threshold in 200 μs

    # Simulation parameters
    rep_period = 200e-6        # 5 kHz repetition rate

    print(f"  Wavelength: {wavelength*1e9:.0f} nm")
    print(f"  Cross section: {sigma*1e4:.2e} cm²")
    print(f"  Upper state lifetime: {tau_f*1e6:.0f} μs")
    print(f"  Cavity length: {cavity_length*100:.0f} cm")
    print(f"  Round-trip time: {round_trip_time*1e9:.2f} ns")
    print(f"  τ_c (lasing): {tau_c_lasing*1e9:.2f} ns")
    print(f"  N_threshold: {N_threshold:.3e} m⁻³")
    print(f"  Rep period: {rep_period*1e6:.0f} μs")

    # Phase 1: Pump with Q blocked (high loss)
    # Phase 2: Open Q-switch, let pulse build and fire
    q_switch_time = 190e-6  # open Q-switch at 190 μs into the cycle

    N = 0.0  # initial inversion
    phi = 1e6  # initial photon density (spontaneous seed)

    gamma_c_sigma = C / n_refr * sigma  # combined rate constant

    times = []
    N_arr = []
    phi_arr = []
    E_gain_arr = []
    E_field_arr = []
    E_total_arr = []

    # Two-phase simulation:
    # Phase 1: coarse dt during pump-up (no pulse dynamics)
    # Phase 2: fine dt after Q-switch opens (resolve the pulse)
    dt_coarse = 100e-9   # 100 ns steps during pump phase
    dt_fine = 10e-12      # 10 ps steps during pulse phase

    # --- Phase 1: Pump up to Q-switch time ---
    t = 0.0
    n_pump_steps = int(q_switch_time / dt_coarse)
    stride_pump = max(1, n_pump_steps // 5000)

    for step in range(n_pump_steps):
        t = step * dt_coarse
        tau_c = tau_c_blocked

        stim = gamma_c_sigma * N * phi
        dN = R_pump - N / tau_f - stim
        dphi = stim - phi / tau_c + N / tau_f * 1e-6

        N += dN * dt_coarse
        phi += dphi * dt_coarse
        if N < 0: N = 0.0
        if phi < 0: phi = 1.0

        if step % stride_pump == 0:
            E_gain = N * photon_energy * mode_volume
            E_field = phi * photon_energy * mode_volume
            times.append(t)
            N_arr.append(N)
            phi_arr.append(phi)
            E_gain_arr.append(E_gain)
            E_field_arr.append(E_field)
            E_total_arr.append(E_gain + E_field)

    print(f"  After pump-up: N = {N:.3e} m⁻³ ({N/N_threshold:.2f}× threshold)")

    # --- Phase 2: Q-switch opens, fine resolution ---
    t_switch = q_switch_time
    pulse_window = rep_period - q_switch_time  # remaining time
    n_pulse_steps = int(pulse_window / dt_fine)
    n_pulse_steps = min(n_pulse_steps, 5_000_000)
    stride_pulse = max(1, n_pulse_steps // 20000)

    for step in range(n_pulse_steps):
        t = t_switch + step * dt_fine
        tau_c = tau_c_lasing

        stim = gamma_c_sigma * N * phi
        dN = R_pump - N / tau_f - stim
        dphi = stim - phi / tau_c + N / tau_f * 1e-6

        N += dN * dt_fine
        phi += dphi * dt_fine
        if N < 0: N = 0.0
        if phi < 0: phi = 1.0

        if step % stride_pulse == 0:
            E_gain = N * photon_energy * mode_volume
            E_field = phi * photon_energy * mode_volume
            times.append(t)
            N_arr.append(N)
            phi_arr.append(phi)
            E_gain_arr.append(E_gain)
            E_field_arr.append(E_field)
            E_total_arr.append(E_gain + E_field)

    times = np.array(times)
    E_total_arr = np.array(E_total_arr)
    E_gain_arr = np.array(E_gain_arr)
    E_field_arr = np.array(E_field_arr)
    phi_arr = np.array(phi_arr)

    # --- Phase decomposition from E_total ---
    # dE_total/dt > 0 → accumulation, < 0 → release
    dE = np.diff(E_total_arr)
    dt_arr = np.diff(times)

    # Find the peak of E_total (transition from accumulation to release)
    peak_idx = np.argmax(E_total_arr)
    peak_time = times[peak_idx]

    # Find the trough before the peak (start of accumulation)
    # and trough after the peak (end of release)
    # Look for minimum before peak
    trough_before_idx = np.argmin(E_total_arr[:peak_idx]) if peak_idx > 0 else 0
    # Look for minimum after peak (or end of array)
    if peak_idx < len(E_total_arr) - 1:
        trough_after_idx = peak_idx + np.argmin(E_total_arr[peak_idx:])
    else:
        trough_after_idx = len(E_total_arr) - 1

    t_acc = times[peak_idx] - times[trough_before_idx]
    t_rel = times[trough_after_idx] - times[peak_idx]

    # Also measure from the photon density pulse shape directly
    phi_peak_idx = np.argmax(phi_arr)
    # Find where phi rises above 10% of peak (pulse start) and falls below (pulse end)
    phi_peak = phi_arr[phi_peak_idx]
    threshold = 0.1 * phi_peak
    pulse_start = phi_peak_idx
    for i in range(phi_peak_idx, -1, -1):
        if phi_arr[i] < threshold:
            pulse_start = i
            break
    pulse_end = phi_peak_idx
    for i in range(phi_peak_idx, len(phi_arr)):
        if phi_arr[i] < threshold:
            pulse_end = i
            break

    pulse_rise_time = times[phi_peak_idx] - times[pulse_start]
    pulse_fall_time = times[pulse_end] - times[phi_peak_idx]
    pulse_fwhm = pulse_rise_time + pulse_fall_time  # rough FWHM proxy

    ara_total_energy = t_acc / t_rel if t_rel > 0 else None
    ara_pulse_shape = pulse_rise_time / pulse_fall_time if pulse_fall_time > 0 else None

    print(f"\n  Results (E_total decomposition):")
    print(f"    T_accumulation (dE/dt > 0): {t_acc:.4e} s")
    print(f"    T_release (dE/dt < 0): {t_rel:.4e} s")
    print(f"    ARA (E_total): {ara_total_energy:.6f}" if ara_total_energy else "    ARA: N/A")
    print(f"    E_total peak at: {peak_time:.4e} s")

    print(f"\n  Results (pulse shape decomposition):")
    print(f"    Pulse rise time (10%-to-peak): {pulse_rise_time:.4e} s")
    print(f"    Pulse fall time (peak-to-10%): {pulse_fall_time:.4e} s")
    print(f"    ARA (pulse shape): {ara_pulse_shape:.6f}" if ara_pulse_shape else "    ARA: N/A")
    print(f"    Pulse FWHM proxy: {pulse_fwhm:.4e} s")

    print(f"    Peak photon density: {phi_peak:.3e} m⁻³")
    print(f"    Peak E_gain: {max(E_gain_arr):.4e} J")
    print(f"    Peak E_field: {max(E_field_arr):.4e} J")

    # Subsample for JSON
    sub = max(1, len(times) // 2000)
    return {
        "system": "Q-switched laser (Nd:YAG class)",
        "parameters": {
            "wavelength_nm": wavelength * 1e9,
            "sigma_cm2": sigma * 1e4,
            "tau_f_us": tau_f * 1e6,
            "cavity_length_cm": cavity_length * 100,
            "round_trip_time_ns": round_trip_time * 1e9,
            "tau_c_lasing_ns": tau_c_lasing * 1e9,
            "N_threshold_m3": N_threshold,
            "rep_period_us": rep_period * 1e6,
            "q_switch_time_us": q_switch_time * 1e6,
            "photon_energy_J": photon_energy,
        },
        "total_energy_decomposition": {
            "T_accumulation_s": t_acc,
            "T_release_s": t_rel,
            "ARA": ara_total_energy,
            "period_s": t_acc + t_rel,
            "accumulation_definition": "dE_total/dt > 0: system net gaining energy from pump (inversion building, field small)",
            "release_definition": "dE_total/dt < 0: system net losing energy (pulse dumps stored energy as output)",
        },
        "pulse_shape_decomposition": {
            "rise_time_s": pulse_rise_time,
            "fall_time_s": pulse_fall_time,
            "ARA": ara_pulse_shape,
            "pulse_width_s": pulse_fwhm,
            "definition": "Rise = photon density increasing (field accumulating), Fall = photon density decreasing (field releasing)",
        },
        "original_catalog": {
            "period_s": 0.0002,
            "ara": 20000.0,
        },
        "trajectory_sample": {
            "times_s": times[::sub].tolist(),
            "E_total_J": E_total_arr[::sub].tolist(),
            "E_gain_J": E_gain_arr[::sub].tolist(),
            "E_field_J": E_field_arr[::sub].tolist(),
        },
    }


# ===================================================================
# MODE-LOCKED LASER (Ti:sapphire class)
# ===================================================================

def simulate_mode_locked():
    """Simulate a mode-locked Ti:sapphire laser using Haus master equation.

    The mode-locked cycle:
      1. Pulse circulates in cavity, passing through gain medium each round trip
      2. Saturable absorber provides self-amplitude modulation (pulse shortening)
      3. Gain medium provides amplification (compensates cavity losses)
      4. Dispersion and self-phase modulation shape the pulse

    For ARA decomposition, we use the Haus master equation simplified to
    track pulse energy E_p(t) and gain g(t) over many round trips:

      E_p[n+1] = E_p[n] · exp(g[n] - l + q(E_p[n]))
      g[n+1]   = g[n] + (g0 - g[n])/τ_g · T_rt - g[n] · E_p[n] / E_sat_g

    where:
      g = net gain per round trip
      l = total cavity loss per round trip
      q = saturable absorber modulation (provides pulse stabilization)
      g0 = small-signal gain (from pump)
      τ_g = gain recovery time
      T_rt = round-trip time
      E_sat_g = gain saturation energy

    For the individual pulse shape (within one round trip), we track the
    temporal profile of the intracavity pulse intensity I(t) during one
    pass through the gain medium and saturable absorber.
    """
    print("\n" + "=" * 60)
    print("  Mode-Locked Laser (Ti:sapphire class)")
    print("=" * 60)

    # Ti:sapphire parameters
    wavelength = 800e-9         # m
    tau_g = 3.2e-6              # gain recovery time (3.2 μs for Ti:sapph)
    photon_energy = H_PLANCK * C / wavelength

    # Cavity parameters (typical 80 MHz oscillator)
    cavity_length = 1.875       # m (for 80 MHz rep rate)
    T_rt = 2 * cavity_length / C  # round-trip time ~12.5 ns
    rep_rate = 1.0 / T_rt

    # Loss and gain
    total_loss = 0.05           # 5% total loss per round trip
    l = -math.log(1 - total_loss)  # loss coefficient
    g0 = 0.08                   # small-signal gain coefficient (above threshold)
    E_sat_g = 1e-6              # gain saturation energy (1 μJ)

    # Saturable absorber (Kerr lens mode-locking proxy)
    q0 = 0.02                   # modulation depth
    E_sat_a = 50e-9             # absorber saturation energy (50 nJ)

    # Typical pulse parameters for steady-state Ti:sapph
    pulse_duration_fwhm = 100e-15  # 100 fs FWHM
    avg_power = 0.5             # 0.5 W average
    pulse_energy_ss = avg_power / rep_rate  # ~6.25 nJ per pulse

    print(f"  Wavelength: {wavelength*1e9:.0f} nm")
    print(f"  Cavity length: {cavity_length:.3f} m")
    print(f"  Round-trip time: {T_rt*1e9:.3f} ns")
    print(f"  Rep rate: {rep_rate*1e-6:.1f} MHz")
    print(f"  Gain recovery: {tau_g*1e6:.1f} μs")
    print(f"  Typical pulse FWHM: {pulse_duration_fwhm*1e15:.0f} fs")
    print(f"  Typical pulse energy: {pulse_energy_ss*1e9:.2f} nJ")

    # Simulate round-trip-to-round-trip dynamics
    n_round_trips = 5000
    E_p = np.zeros(n_round_trips)
    g = np.zeros(n_round_trips)
    E_total = np.zeros(n_round_trips)  # total stored energy

    # Initial conditions: small noise, gain at small-signal
    E_p[0] = 1e-15  # tiny seed (spontaneous emission)
    g[0] = g0       # full small-signal gain

    for n in range(n_round_trips - 1):
        # Saturable absorber modulation
        q_n = q0 / (1.0 + E_p[n] / E_sat_a)

        # Net gain per round trip
        net_gain = g[n] - l + q0 - q_n  # SAM gives more transmission for higher energy

        # Pulse energy update
        E_p[n + 1] = E_p[n] * math.exp(net_gain)
        if E_p[n + 1] > 1e-3:  # cap at 1 mJ for stability
            E_p[n + 1] = 1e-3

        # Gain update (gain depleted by pulse, recovered by pump)
        g[n + 1] = g[n] + (g0 - g[n]) * T_rt / tau_g - g[n] * E_p[n] / E_sat_g

        # Total stored energy: gain medium + field
        # E_gain ~ g[n] * E_sat_g (energy stored in population inversion)
        # E_field ~ E_p[n] (energy in the pulse)
        E_total[n] = g[n] * E_sat_g + E_p[n]

    E_total[-1] = g[-1] * E_sat_g + E_p[-1]

    # --- Steady-state analysis ---
    # In steady state, the pulse energy and gain should be constant per round trip.
    # The ARA is measured from the INTRAPULSE dynamics: how does energy flow
    # within a single pulse cycle?
    ss_start = int(0.7 * n_round_trips)
    ss_E_p = np.mean(E_p[ss_start:])
    ss_g = np.mean(g[ss_start:])

    print(f"\n  Steady-state pulse energy: {ss_E_p:.4e} J ({ss_E_p*1e9:.2f} nJ)")
    print(f"  Steady-state gain: {ss_g:.6f}")

    # --- Intrapulse ARA ---
    # The pulse itself has a sech² or Gaussian temporal profile.
    # Accumulation = leading edge (intensity rising, energy building in the pulse)
    # Release = trailing edge (intensity falling, energy leaving as output)
    #
    # For a sech² pulse (standard mode-locked shape):
    #   I(t) = I_peak · sech²(t / τ_p)
    # This is perfectly symmetric: rise time = fall time → ARA = 1.0 (by math)
    #
    # But we should check if gain saturation or absorber dynamics break this
    # symmetry. Simulate one pulse passing through the gain + absorber.

    print(f"\n  Intrapulse shape analysis:")

    # Simulate one pulse passing through gain + saturable absorber
    # Using the pulse propagation: I(t,z) through gain and absorber
    tau_p = pulse_duration_fwhm / 1.7627  # sech² pulse: FWHM = 1.7627 × τ_p
    t_window = 10 * tau_p
    n_t = 100000
    dt_pulse = 2 * t_window / n_t
    t_pulse = np.linspace(-t_window, t_window, n_t)

    # Input pulse (sech² shape)
    I_input = ss_E_p / (2 * tau_p) * (1.0 / np.cosh(t_pulse / tau_p)) ** 2

    # After passing through saturating gain medium:
    # The leading edge sees full gain, trailing edge sees depleted gain
    g_inst = ss_g  # instantaneous gain
    I_output = np.zeros(n_t)
    for i in range(n_t):
        I_output[i] = I_input[i] * math.exp(g_inst)
        # Gain depletes proportional to extracted energy
        g_inst -= I_input[i] * dt_pulse / E_sat_g
        if g_inst < 0:
            g_inst = 0

    # The output pulse shape after gain saturation:
    # Leading edge is amplified more (sees full gain)
    # Trailing edge is amplified less (gain depleted)
    # This creates an ASYMMETRIC pulse shape

    # Find the peak
    peak_idx_pulse = np.argmax(I_output)
    peak_time_pulse = t_pulse[peak_idx_pulse]

    # Measure rise and fall times (10% threshold)
    I_peak_val = I_output[peak_idx_pulse]
    thresh = 0.1 * I_peak_val

    rise_start_idx = 0
    for i in range(peak_idx_pulse):
        if I_output[i] >= thresh:
            rise_start_idx = i
            break
    fall_end_idx = n_t - 1
    for i in range(peak_idx_pulse, n_t):
        if I_output[i] < thresh:
            fall_end_idx = i
            break

    rise_time = t_pulse[peak_idx_pulse] - t_pulse[rise_start_idx]
    fall_time = t_pulse[fall_end_idx] - t_pulse[peak_idx_pulse]
    intrapulse_ara = rise_time / fall_time if fall_time > 0 else None

    print(f"    Input pulse: sech² with τ_p = {tau_p*1e15:.1f} fs")
    print(f"    After gain saturation:")
    print(f"      Peak shifts by: {peak_time_pulse*1e15:.1f} fs (negative = toward leading edge)")
    print(f"      Rise time (10%-to-peak): {rise_time*1e15:.1f} fs")
    print(f"      Fall time (peak-to-10%): {fall_time*1e15:.1f} fs")
    print(f"      Intrapulse ARA: {intrapulse_ara:.6f}" if intrapulse_ara else "      Intrapulse ARA: N/A")

    # --- Full-cycle ARA (round-trip level) ---
    # Over one round trip, the total stored energy E_total rises (pump) then
    # drops (pulse output). Measure from the steady-state waveform.
    # In mode-locking, the pulse is SO short compared to T_rt that the
    # per-round-trip E_total is essentially:
    #   rise for ~T_rt (pump fills gain) then drop for ~τ_pulse (pulse dumps)
    # But this mixes timescales. The actual E_total changes smoothly over
    # many round trips during mode-lock buildup, then is constant in steady state.

    # The physically meaningful ARA for the mode-locked laser as a mapped system
    # is the intrapulse ARA — the shape of the actual oscillating waveform.
    # The round-trip repetition is the cavity clock, which is the coupled system.

    # Also compute: if we treat the FULL CYCLE (accumulation between pulses +
    # pulse release) as the system:
    full_cycle_acc = T_rt - pulse_duration_fwhm
    full_cycle_rel = pulse_duration_fwhm
    full_cycle_ara = full_cycle_acc / full_cycle_rel

    print(f"\n  Full-cycle decomposition (for comparison):")
    print(f"    T_acc (inter-pulse pump): {full_cycle_acc:.4e} s")
    print(f"    T_rel (pulse): {full_cycle_rel:.4e} s")
    print(f"    ARA (full cycle): {full_cycle_ara:.1f}")
    print(f"    NOTE: This is the original catalog value. See discussion below.")

    print(f"\n  DIAGNOSTIC NOTE:")
    print(f"    The mode-locked laser has two oscillatory systems:")
    print(f"    1. The intracavity pulse (temporal shape) — ARA from pulse rise/fall")
    print(f"    2. The cavity repetition cycle (gain recovery + pulse) — ARA from cycle")
    print(f"    The pulse shape is the ground-cycle oscillation.")
    print(f"    The cavity repetition is the coupled clock (META ARA).")

    sub = max(1, n_round_trips // 2000)
    sub_pulse = max(1, n_t // 2000)
    return {
        "system": "Mode-locked laser (Ti:sapphire class)",
        "parameters": {
            "wavelength_nm": wavelength * 1e9,
            "cavity_length_m": cavity_length,
            "round_trip_time_ns": T_rt * 1e9,
            "rep_rate_MHz": rep_rate * 1e-6,
            "gain_recovery_us": tau_g * 1e6,
            "pulse_fwhm_fs": pulse_duration_fwhm * 1e15,
            "tau_p_fs": tau_p * 1e15,
            "steady_state_pulse_energy_nJ": ss_E_p * 1e9,
            "steady_state_gain": ss_g,
            "photon_energy_J": photon_energy,
        },
        "intrapulse_decomposition": {
            "rise_time_fs": rise_time * 1e15,
            "fall_time_fs": fall_time * 1e15,
            "ARA": intrapulse_ara,
            "pulse_fwhm_fs": pulse_duration_fwhm * 1e15,
            "peak_shift_fs": peak_time_pulse * 1e15,
            "accumulation_definition": "Pulse leading edge: intensity rising, energy building in the optical field via stimulated emission",
            "release_definition": "Pulse trailing edge: intensity falling, depleted gain cannot sustain field, energy disperses",
            "note": "Gain saturation breaks the sech² symmetry — the leading edge sees more gain than the trailing edge",
        },
        "full_cycle_decomposition": {
            "T_acc_s": full_cycle_acc,
            "T_rel_s": full_cycle_rel,
            "ARA": full_cycle_ara,
            "note": "This is the original catalog value. It mixes the cavity repetition clock (META ARA) with the pulse event. The intrapulse shape is the ground-cycle ARA.",
        },
        "original_catalog": {
            "period_s": 1.25e-8,
            "ara": 125000.0,
        },
        "round_trip_dynamics": {
            "times_rt": list(range(0, n_round_trips, sub)),
            "E_pulse_J": E_p[::sub].tolist(),
            "gain": g[::sub].tolist(),
            "E_total_J": E_total[::sub].tolist(),
        },
        "pulse_shape": {
            "times_fs": (t_pulse[::sub_pulse] * 1e15).tolist(),
            "I_input": I_input[::sub_pulse].tolist(),
            "I_output": I_output[::sub_pulse].tolist(),
        },
    }



def main():
    print("=" * 70)
    print("Laser Pulse ARA Computation - Rate Equations")
    print("=" * 70)

    results = {}
    results["q_switched"] = simulate_q_switched()
    results["mode_locked"] = simulate_mode_locked()

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    for key, res in results.items():
        print(f"\n  {res['system']}:")
        print(f"    Original catalog ARA: {res['original_catalog']['ara']:.0f}")
        if "total_energy_decomposition" in res:
            d = res["total_energy_decomposition"]
            if d.get("ARA") is not None:
                print(f"    E_total decomposition ARA: {d['ARA']:.6f}")
                print(f"    T_acc={d['T_accumulation_s']:.4e} s, T_rel={d['T_release_s']:.4e} s")
            else:
                print(f"    E_total ARA: N/A (T_rel=0)")
        if "pulse_shape_decomposition" in res:
            d = res["pulse_shape_decomposition"]
            if d.get("ARA") is not None:
                print(f"    Pulse shape ARA: {d['ARA']:.6f}")
            else:
                print(f"    Pulse shape ARA: N/A")
        if "intrapulse_decomposition" in res:
            d = res["intrapulse_decomposition"]
            if d.get("ARA") is not None:
                print(f"    Intrapulse ARA: {d['ARA']:.6f}")
                print(f"    Rise: {d['rise_time_fs']:.1f} fs, Fall: {d['fall_time_fs']:.1f} fs")
            else:
                print(f"    Intrapulse ARA: N/A")

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
