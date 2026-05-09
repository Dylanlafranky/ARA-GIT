#!/usr/bin/env python3
"""
Script 199 — Normal Mode Decomposition: How Physics Actually Does It
==============================================================================

Dylan's insight: "We should have been looking at how physicists treat waves
and adapting that to our framework."

THE PHYSICS:

    Any coupled oscillator system has NORMAL MODES — patterns where everything
    oscillates at the same frequency. The general motion is a SUPERPOSITION
    of these modes:

        x(t) = Σ Aₙ cos(ωₙt + φₙ)

    You don't iterate each oscillator separately and bolt on coupling.
    You find the normal modes FIRST, evolve THOSE independently, then
    reconstruct what any single oscillator does from the superposition.

    Normal modes are orthogonal — they don't interfere with each other.
    They are the natural "alphabet" of the system.

WHY φ IS THE RIGHT CASCADE — BEAT FREQUENCIES:

    When two modes with frequencies ω₁ and ω₂ are superposed, you get:
        cos(ω₁t) + cos(ω₂t) = 2cos(ω_avg · t)cos(ω_beat · t)

    where ω_beat = |ω₁ - ω₂|/2

    In our φ-cascade: periods P, P/φ, P/φ²
        Beat between P and P/φ:
            Δω = 2π/P - 2π/(P/φ) = (2π/P)(1 - φ) = -(2π/P)/φ²
            Beat period = P · φ²/(φ-1) = P · φ (since φ² = φ+1, φ-1 = 1/φ)

    Actually: ω₁ = 2π/P, ω₂ = 2πφ/P
        Δω = 2π(φ-1)/P = 2π/(Pφ) = ω for period Pφ
        Beat period = Pφ ← one φ-step UP from the parent!

    And: ω₂ = 2πφ/P, ω₃ = 2πφ²/P
        Δω = 2πφ(φ-1)/P = 2πφ/Pφ = 2π/P = ω₁
        Beat period = P ← equals the PARENT period!

    φ is the ONLY ratio where beat frequencies land exactly on other
    members of the cascade. Beats between sub-channels reinforce the
    parent channel. This is why φ-cascading channels don't create noise —
    their interference pattern IS the signal at the next scale up.

ARA IN THE NORMAL MODE FRAMEWORK:

    The ARA determines MODE AMPLITUDES, not individual channel states.
    Engine systems (ARA > 1): preferentially excite high-amplitude modes
    Consumer systems (ARA < 1): suppress mode amplitudes, flatten output
    The asymmetry between engine and consumer IS the asymmetry between
    mode excitation and mode damping.

    The φ-valley (from Scripts 191-192) becomes the ENVELOPE of the
    superposition — the slowly-varying amplitude that the modes ride within.

ARCHITECTURE:

    1. Build the coupling matrix K (9×9, from ARA decomposition)
    2. Eigendecompose K → eigenvalues λₙ, eigenvectors vₙ
    3. λₙ shifts the natural frequencies: ω'ₙ = √(ωₙ² + λₙ)
    4. Decompose initial condition into mode amplitudes: A = V⁻¹ · x₀
    5. Evolve: x(t) = Σ Aₙ · vₙ · cos(ω'ₙt + φₙ)
    6. Observable = superposition at the "sunspot channel" location
    7. Envelope = ARA-weighted valley (engine → deep valley, consumer → flat)
"""

import numpy as np
import os

# ═══════════════════════════════════════════════════════════════════
# FRAMEWORK CONSTANTS
# ═══════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
PI_LEAK = np.pi - 3
PHI_LEAK = 1.0 / PHI

# ═══════════════════════════════════════════════════════════════════
# φ-PERIOD CASCADE
# ═══════════════════════════════════════════════════════════════════

P_PARENT = [HALE_PERIOD, HALE_PERIOD / PHI, HALE_PERIOD / PHI**2]

P_SUBS = []
for parent_p in P_PARENT:
    for sub_idx in range(3):
        P_SUBS.append(parent_p / PHI**sub_idx)

# Natural angular frequencies
OMEGA_NATURAL = [2 * np.pi / p for p in P_SUBS]

# ═══════════════════════════════════════════════════════════════════
# ARA DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════

ARA_ENG_PARENTS = [PHI, 1.73, 1.354]
ARA_CON_PARENTS = [2.0 - a for a in ARA_ENG_PARENTS]

PARENT_MEAN = np.mean(ARA_ENG_PARENTS)
SHAPE_RATIOS = np.array([PHI, 1.73, 1.354]) / PARENT_MEAN

def decompose_parent(parent_ara):
    subs = parent_ara * SHAPE_RATIOS
    return np.clip(subs, 0.01, 1.99)

ARA_ENG_9 = []
ARA_CON_9 = []
for parent_ara in ARA_ENG_PARENTS:
    ARA_ENG_9.extend(decompose_parent(parent_ara))
for parent_ara in ARA_CON_PARENTS:
    ARA_CON_9.extend(decompose_parent(parent_ara))

# V4 frozen parameters
V4_DEPTH = 1.0
V4_BASIN_UP = 0.1
V4_BASIN_DOWN = 1.0
V4_FLOOR = 0.5

ARA_SSN_SINGLE = 1.73
MIDOFF_SINGLE = abs((1.73 + 0.15) / 2 - R_COUPLER)
MIRROR_PHASE = np.pi

SING_DOWN = PHI
SING_UP = PHI_LEAK

# ═══════════════════════════════════════════════════════════════════
# COUPLING MATRIX — The physics of how channels interact
# ═══════════════════════════════════════════════════════════════════

def build_coupling_matrix(periods, kappa=PI_LEAK):
    """
    Build the coupling matrix for 9 channels.

    In physics, the coupling matrix K enters the equations of motion:
        M·x'' + K·x = 0

    For our system, coupling strength decays with period-distance.
    Within triad: adjacent = κ, skip-one = κ/φ
    Between triads: adjacent = κ/φ, skip-one = κ/φ²
    """
    N = len(periods)
    K = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            pi_parent = i // 3
            pj_parent = j // 3
            si_sub = i % 3
            sj_sub = j % 3

            if pi_parent == pj_parent:
                sub_distance = abs(si_sub - sj_sub)
                if sub_distance == 1:
                    K[i, j] = kappa
                else:
                    K[i, j] = kappa / PHI
            else:
                parent_distance = min(
                    abs(pi_parent - pj_parent),
                    3 - abs(pi_parent - pj_parent)
                )
                sub_distance = abs(si_sub - sj_sub)
                base = kappa / PHI if parent_distance == 1 else kappa / PHI**2
                K[i, j] = base / PHI**sub_distance

    # Make the diagonal: K_ii = -Σ K_ij (ensures zero-sum per row)
    for i in range(N):
        K[i, i] = -np.sum(K[i, :])

    return K

# ═══════════════════════════════════════════════════════════════════
# NORMAL MODE MODEL
# ═══════════════════════════════════════════════════════════════════

class NormalModeModel:
    """
    Physics-based coupled oscillator with normal mode decomposition.

    1. Build coupling matrix from ARA structure
    2. Eigendecompose → normal mode frequencies and shapes
    3. Express initial condition as superposition of modes
    4. Evolve each mode at its eigenfrequency
    5. Reconstruct observable as superposition

    ARA role: determines MODE AMPLITUDES
        Engine ARA → amplifies modes (like driving a coupled system)
        Consumer ARA → damps modes (like friction on a coupled system)
        The engine_factor modulates how much each mode contributes
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.omega_nat = 2 * np.pi / self.periods  # Natural frequencies
        self.ara_eng = np.array(ara_eng_9)
        self.ara_con = np.array(ara_con_9)

        # Build coupling matrix
        K = build_coupling_matrix(periods_9)

        # Eigendecompose: K·v = λ·v
        # eigenvalues give frequency shifts, eigenvectors give mode shapes
        eigenvalues, eigenvectors = np.linalg.eigh(K)
        self.eigenvalues = eigenvalues
        self.eigenvectors = eigenvectors  # columns are eigenvectors
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)

        # Mode frequencies: ω'_n = ω_nat_n × (1 + λ_n / ω_nat_n²)^0.5
        # Approximate for small coupling: ω'_n ≈ ω_nat_n + λ_n / (2·ω_nat_n)
        # Use the proper formula with safeguard against negative values
        self.omega_modes = np.zeros(self.N)
        for n in range(self.N):
            # Each mode's frequency is based on the dominant natural frequency
            # weighted by the eigenvector
            weights = np.abs(eigenvectors[:, n])
            weights = weights / np.sum(weights)
            omega_weighted = np.sum(weights * self.omega_nat)
            # Coupling shifts the frequency
            shift = eigenvalues[n] * PI_LEAK  # Scale by π-leak
            self.omega_modes[n] = max(omega_weighted + shift, omega_weighted * 0.5)

        # ARA-weighted mode amplitudes
        # Engine factor for each channel: how much it drives
        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)
        self.consumer_factors = np.maximum(1.0 - self.ara_con, 0.0)

        # Mode amplitude scaling: eigenvectors weighted by engine_factors
        # Modes that align with high-ARA channels get amplified
        self.mode_drive = np.zeros(self.N)
        for n in range(self.N):
            self.mode_drive[n] = np.sum(
                np.abs(eigenvectors[:, n]) * self.engine_factors
            )
        # Normalize
        md_sum = np.sum(self.mode_drive)
        if md_sum > 0:
            self.mode_drive = self.mode_drive / md_sum

        # Consumer mode damping
        self.mode_damp = np.zeros(self.N)
        for n in range(self.N):
            self.mode_damp[n] = np.sum(
                np.abs(eigenvectors[:, n]) * self.consumer_factors
            )
        md_sum = np.sum(self.mode_damp)
        if md_sum > 0:
            self.mode_damp = self.mode_damp / md_sum

        # Phase offsets
        self.phase0_base = phase0_base
        self.mode_phases = np.zeros(self.N)
        for n in range(self.N):
            self.mode_phases[n] = phase0_base + n * 2 * np.pi / self.N

        # Mode amplitudes (initialized from data)
        self.mode_amps_eng = np.zeros(self.N)
        self.mode_amps_con = np.zeros(self.N)

        # Valley envelope
        self.valley_amp = np.mean(self.engine_factors) * V4_DEPTH

    def init_from_observation(self, log_ssn):
        """Project initial observation into mode space."""
        deviation = log_ssn - self.C

        # Initial channel states: deviation distributed across channels
        x0_eng = np.zeros(self.N)
        for i in range(self.N):
            x0_eng[i] = deviation * self.engine_factors[i] / max(np.sum(self.engine_factors), 0.01)

        # Project into mode space: a = V^-1 · x
        self.mode_amps_eng = self.V_inv @ x0_eng

        # Scale by mode drive (ARA determines which modes are excited)
        for n in range(self.N):
            # Modes aligned with engine channels get the initial energy
            self.mode_amps_eng[n] *= (1.0 + self.mode_drive[n])

        # Consumer starts as mirror
        x0_con = -x0_eng
        self.mode_amps_con = self.V_inv @ x0_con
        for n in range(self.N):
            self.mode_amps_con[n] *= (1.0 + self.mode_damp[n])

    def observable_ssn(self, t):
        """
        THE SUPERPOSITION:

        x(t) = Σ Aₙ · cos(ωₙt + φₙ)

        Each normal mode contributes its own frequency.
        The observable is the sum at the "sunspot observation point."

        Engine modes add. Consumer modes subtract (mirror).
        The valley envelope from ARA provides slow modulation.
        """
        # Engine superposition
        eng_signal = 0.0
        for n in range(self.N):
            eng_signal += self.mode_amps_eng[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n]
            )

        # Consumer superposition
        con_signal = 0.0
        for n in range(self.N):
            con_signal += self.mode_amps_con[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n] + MIRROR_PHASE
            )

        # Valley envelope (ARA-driven slow modulation)
        valley = self.valley_amp * np.sin(2 * np.pi * t / HALE_PERIOD + self.phase0_base)

        # Combine: engine signal in the valley, with consumer feedback
        raw = eng_signal + PI_LEAK * con_signal + valley

        return self.C + raw

    def predict_sequence(self, n_years):
        """Generate predictions for n_years."""
        preds = []
        for t in range(1, n_years + 1):
            obs = self.observable_ssn(t)
            preds.append(obs)
        return preds


# ═══════════════════════════════════════════════════════════════════
# BEAT FREQUENCY MODEL — Explicit beat tracking
# ═══════════════════════════════════════════════════════════════════

class BeatFrequencyModel:
    """
    Uses the φ-cascade beat structure explicitly.

    The key insight: in a φ-cascade, beat frequencies between adjacent
    channels land on other cascade members:
        beat(P, P/φ) = period of φ·P  (one step UP)
        beat(P/φ, P/φ²) = P            (the PARENT period)

    This means we can express the observable as:
        x(t) = Σ Aₙ cos(ωₙt + φₙ) × [1 + Bₙ cos(ω_beat_n · t + ψₙ)]

    Each mode rides an amplitude envelope set by the beats from
    the modes above and below it in the cascade.
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.omega = 2 * np.pi / self.periods
        self.ara_eng = np.array(ara_eng_9)
        self.phase0 = phase0_base

        # Engine factors determine amplitude
        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)

        # Beat frequencies between adjacent channels
        self.beat_omega = np.zeros(self.N)
        self.beat_amp = np.zeros(self.N)
        for i in range(self.N):
            # Beat with the channel one φ-step slower (if it exists)
            parent_idx = i // 3
            sub_idx = i % 3
            if sub_idx > 0:
                # Beat with previous sub-channel in same triad
                j = i - 1
                self.beat_omega[i] = abs(self.omega[i] - self.omega[j])
                # Beat amplitude scales with engine factor
                self.beat_amp[i] = PI_LEAK * self.engine_factors[i]
            elif parent_idx > 0:
                # Beat with last sub-channel of previous triad
                j = (parent_idx - 1) * 3 + 2
                self.beat_omega[i] = abs(self.omega[i] - self.omega[j])
                self.beat_amp[i] = PI_LEAK * PHI_LEAK * self.engine_factors[i]

        # Mode amplitudes and phases
        self.amps = np.zeros(self.N)
        self.phases = np.zeros(self.N)
        for i in range(self.N):
            self.phases[i] = phase0_base + i * 2 * np.pi / (3 * self.N)

        # Valley
        self.valley_amp = np.mean(self.engine_factors) * V4_DEPTH

    def init_from_observation(self, log_ssn):
        deviation = log_ssn - self.C

        # Distribute initial amplitude across modes
        # Higher engine-factor channels get more initial energy
        total_ef = np.sum(self.engine_factors)
        if total_ef > 0:
            for i in range(self.N):
                self.amps[i] = deviation * self.engine_factors[i] / total_ef
        else:
            self.amps[:] = deviation / self.N

    def observable_ssn(self, t):
        """
        x(t) = Σ Aₙ cos(ωₙt + φₙ) × [1 + Bₙ cos(ω_beat_n · t)]
                + valley envelope
        """
        signal = 0.0
        for i in range(self.N):
            # Base oscillation
            base = self.amps[i] * np.cos(self.omega[i] * t + self.phases[i])

            # Beat envelope (amplitude modulation from adjacent mode)
            if self.beat_omega[i] > 0:
                envelope = 1.0 + self.beat_amp[i] * np.cos(self.beat_omega[i] * t)
            else:
                envelope = 1.0

            signal += base * envelope

        # Valley envelope
        valley = self.valley_amp * np.sin(2 * np.pi * t / HALE_PERIOD + self.phase0)

        return self.C + signal + valley

    def predict_sequence(self, n_years):
        preds = []
        for t in range(1, n_years + 1):
            preds.append(self.observable_ssn(t))
        return preds


# ═══════════════════════════════════════════════════════════════════
# HYBRID MODEL — Normal modes + ARA valley + one-shot gate
# ═══════════════════════════════════════════════════════════════════

class HybridNormalModeModel:
    """
    Combines:
    - Normal mode decomposition (physics)
    - ARA-driven valley envelope (ARA framework)
    - Asymmetric basin (watershed model)
    - One-shot singularity gate (Big Bang insight)

    The modes provide the FREQUENCY STRUCTURE.
    The ARA provides the AMPLITUDE STRUCTURE.
    The valley provides the STABILITY.
    The gate provides the SCALE COUPLING.
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.omega_nat = 2 * np.pi / self.periods
        self.ara_eng = np.array(ara_eng_9)
        self.ara_con = np.array(ara_con_9)

        # Coupling matrix and eigendecomposition
        K = build_coupling_matrix(periods_9)
        eigenvalues, eigenvectors = np.linalg.eigh(K)
        self.eigenvalues = eigenvalues
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)

        # Mode frequencies (coupling-shifted)
        self.omega_modes = np.zeros(self.N)
        for n in range(self.N):
            weights = np.abs(eigenvectors[:, n])
            weights = weights / max(np.sum(weights), 1e-10)
            omega_w = np.sum(weights * self.omega_nat)
            shift = eigenvalues[n] * PI_LEAK
            self.omega_modes[n] = max(omega_w + shift, omega_w * 0.5)

        # ARA-based mode amplitudes
        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)
        self.consumer_factors = np.maximum(1.0 - self.ara_con, 0.0)

        self.mode_drive = np.zeros(self.N)
        for n in range(self.N):
            self.mode_drive[n] = np.sum(np.abs(eigenvectors[:, n]) * self.engine_factors)
        md_sum = np.sum(self.mode_drive)
        if md_sum > 0:
            self.mode_drive /= md_sum

        # Phases
        self.phase0 = phase0_base
        self.mode_phases = np.zeros(self.N)
        for n in range(self.N):
            self.mode_phases[n] = phase0_base + n * 2 * np.pi / self.N

        # Mode amplitudes
        self.mode_amps = np.zeros(self.N)

        # Valley parameters
        self.valley_amp = np.mean(self.engine_factors) * V4_DEPTH
        self.valley_state = C  # Tracks slow valley movement

        # Gate tracking
        self.gate_fired = False
        self.prev_obs = C

    def init_from_observation(self, log_ssn):
        deviation = log_ssn - self.C

        # Distribute initial energy across channels
        x0 = np.zeros(self.N)
        ef_sum = np.sum(self.engine_factors)
        if ef_sum > 0:
            for i in range(self.N):
                x0[i] = deviation * self.engine_factors[i] / ef_sum
        else:
            x0[:] = deviation / self.N

        # Project into mode space
        self.mode_amps = self.V_inv @ x0

        # Scale by mode drive
        for n in range(self.N):
            self.mode_amps[n] *= (1.0 + self.mode_drive[n] * 2.0)

        self.prev_obs = log_ssn
        self.valley_state = log_ssn

    def observable_ssn(self, t):
        """
        Hybrid: normal mode superposition + ARA valley + gate
        """
        # SUPERPOSITION of engine normal modes
        signal = 0.0
        for n in range(self.N):
            signal += self.mode_amps[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n]
            )

        # ARA VALLEY ENVELOPE (asymmetric basin)
        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0
        )

        raw_obs = self.C + signal

        # Asymmetric basin correction (watershed)
        avg_ef = np.mean(self.engine_factors)
        displacement = raw_obs - valley
        if displacement > 0:
            correction = -avg_ef * V4_BASIN_DOWN * displacement * 0.3
        else:
            correction = -avg_ef * V4_BASIN_UP * displacement * 0.3

        obs = raw_obs + correction

        # ONE-SHOT GATE (singularity transfer)
        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            # Below floor: consumer energy transfers back
            overflow = floor - obs
            obs = floor
            # Redistribute: slightly boost mode amplitudes
            for n in range(self.N):
                self.mode_amps[n] += overflow * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False

        self.prev_obs = obs
        return obs

    def predict_sequence(self, n_years):
        preds = []
        for t in range(1, n_years + 1):
            preds.append(self.observable_ssn(t))
        return preds


# ═══════════════════════════════════════════════════════════════════
# ITERATIVE F⁹ (Script 197 v4 — CAM valve for comparison)
# ═══════════════════════════════════════════════════════════════════

GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
INTRA_SUB_COUPLING = PI_LEAK
INTER_SUB_COUPLING = PI_LEAK * PHI_LEAK
SUB_PHASE_LAG = 2 * np.pi / 3
PARENT_PHASE_LAG = 2 * np.pi / 3

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def effective_ara(ara_base, t, phase0, period):
    center = 1.0
    amp = ara_base - center
    return center + amp * np.sin(2 * np.pi * t / period + phase0)

def base_wave_dlog(log_val, C, R_matter, step, t, phase0, midpoint_offset, period):
    eff = effective_ara(R_matter, t, phase0, period)
    eff = max(eff, 0.1)
    phi = value_to_longitude(log_val, C, eff)
    phi_next = phi + GA_OVER_PHI * step
    def avg_w(pos, R, off):
        return (wave(pos + off, R) + wave(pos - off, R)) / 2
    c1n = avg_w(phi, R_COUPLER, PHI)
    c1x = avg_w(phi_next, R_COUPLER, PHI)
    c2n = avg_w(phi + HALF_PHI, R_COUPLER, PHI)
    c2x = avg_w(phi_next + HALF_PHI, R_COUPLER, PHI)
    inner = ((c1x + c2x) / 2 - (c1n + c2n) / 2) * np.exp(-midpoint_offset)
    s1n = wave(phi, R_matter)
    s2n = wave(phi + HALF_PHI, R_matter)
    s1x = wave(phi_next, R_matter)
    s2x = wave(phi_next + HALF_PHI, R_matter)
    outer = ((s1x + s2x) / 2 - (s1n + s2n) / 2) * np.exp(-midpoint_offset)
    drive = eff - 1.0
    distance = abs(log_val - C)
    gear = max(distance / HALF_PHI, 0.1)
    wdlog = inner + drive * gear * outer
    return wdlog, eff

def engine_channel(log_val, C, R_matter, t, phase0, period):
    midoff = abs(R_matter - R_COUPLER)
    wdlog, eff = base_wave_dlog(log_val, C, R_matter, 1, t, phase0, midoff, period)
    bounced = log_val + wdlog
    engine_factor = max(R_matter - 1.0, 0.0)
    valley_amp = engine_factor * V4_DEPTH
    valley = C + valley_amp * np.sin(2 * np.pi * (t + 1) / period + phase0)
    displacement = bounced - valley
    if displacement > 0:
        correction = -engine_factor * V4_BASIN_DOWN * displacement
    else:
        correction = -engine_factor * V4_BASIN_UP * displacement
    new_val = bounced + correction
    floor = C - V4_FLOOR
    overflow = 0.0
    if new_val < floor:
        overflow = floor - new_val
        new_val = floor
    return new_val, valley, overflow

def consumer_channel(log_val, C, R_matter, t, phase0, period):
    midoff = abs(R_matter - R_COUPLER)
    wdlog, eff = base_wave_dlog(log_val, C, R_matter, 1, t, phase0, midoff, period)
    bounced = log_val + wdlog
    consumer_factor = max(1.0 - R_matter, 0.0)
    valley_amp = consumer_factor * V4_DEPTH
    valley = C + valley_amp * np.sin(2 * np.pi * (t + 1) / period + phase0)
    displacement = bounced - valley
    if displacement < 0:
        correction = -consumer_factor * V4_BASIN_DOWN * displacement
    else:
        correction = -consumer_factor * V4_BASIN_UP * displacement
    new_val = bounced + correction
    ceiling = C + V4_FLOOR
    overflow = 0.0
    if new_val > ceiling:
        overflow = new_val - ceiling
        new_val = ceiling
    return new_val, valley, overflow

class IterativeF9Model:
    """Script 197 v4 — iterative F⁹ with CAM valve (for comparison)."""
    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.ara_eng = list(ara_eng_9)
        self.ara_con = list(ara_con_9)
        self.periods = list(periods_9)
        self.C = C
        self.N = 9
        self.eng_phases = []
        self.con_phases = []
        for parent_idx in range(3):
            parent_phase = phase0_base + parent_idx * PARENT_PHASE_LAG
            for sub_idx in range(3):
                sub_phase = parent_phase + sub_idx * SUB_PHASE_LAG / 3
                self.eng_phases.append(sub_phase)
                self.con_phases.append(sub_phase + MIRROR_PHASE)
        self.eng_states = [C] * self.N
        self.con_states = [C] * self.N
        self.eng_gate_fired = [False] * self.N
        self.con_gate_fired = [False] * self.N

    def init_from_observation(self, log_ssn):
        for i in range(3):
            self.eng_states[i] = log_ssn + 0.03 * (1 - i * 0.3)
            self.eng_states[3 + i] = log_ssn - 0.01 * i
            self.eng_states[6 + i] = self.C
        for i in range(9):
            self.con_states[i] = 2 * self.C - self.eng_states[i]

    def step(self, t):
        new_eng = [0.0]*self.N; new_con = [0.0]*self.N
        eng_v = [0.0]*self.N; con_v = [0.0]*self.N
        eng_of = [0.0]*self.N; con_of = [0.0]*self.N
        for i in range(self.N):
            new_eng[i], eng_v[i], eng_of[i] = engine_channel(
                self.eng_states[i], self.C, self.ara_eng[i], t, self.eng_phases[i], self.periods[i])
            new_con[i], con_v[i], con_of[i] = consumer_channel(
                self.con_states[i], self.C, self.ara_con[i], t, self.con_phases[i], self.periods[i])
        for parent_idx in range(3):
            base = parent_idx * 3
            for local in range(3):
                i = base + local
                upstream = base + (local - 1) % 3
                new_eng[i] += INTRA_SUB_COUPLING * (self.eng_states[upstream] - eng_v[upstream])
                new_con[i] += INTRA_SUB_COUPLING * (self.con_states[upstream] - con_v[upstream])
        for parent_idx in range(3):
            src_base = parent_idx * 3
            dst_base = ((parent_idx + 1) % 3) * 3
            se = np.mean([self.eng_states[src_base+j]-eng_v[src_base+j] for j in range(3)])
            sc = np.mean([self.con_states[src_base+j]-con_v[src_base+j] for j in range(3)])
            for j in range(3):
                new_eng[dst_base+j] += INTER_SUB_COUPLING * se
                new_con[dst_base+j] += INTER_SUB_COUPLING * sc
        for i in range(self.N):
            if eng_of[i] > 0 and not self.eng_gate_fired[i]:
                tr = eng_of[i] * SING_DOWN
                p = i // 3; cb = p * 3
                new_con[cb] += tr*0.5; new_con[cb+1] += tr*0.3; new_con[cb+2] += tr*0.2
                self.eng_gate_fired[i] = True
            elif eng_of[i] == 0 and self.eng_gate_fired[i]:
                self.eng_gate_fired[i] = False
        for i in range(self.N):
            if con_of[i] > 0 and not self.con_gate_fired[i]:
                tr = con_of[i] * SING_UP
                p = i // 3; eb = p * 3
                new_eng[eb] += tr*0.5; new_eng[eb+1] += tr*0.3; new_eng[eb+2] += tr*0.2
                self.con_gate_fired[i] = True
            elif con_of[i] == 0 and self.con_gate_fired[i]:
                self.con_gate_fired[i] = False
        act_mean = np.mean([self.eng_states[3+j]-eng_v[3+j] for j in range(3)])
        acc_mean = np.mean([self.con_states[6+j]-con_v[6+j] for j in range(3)])
        for j in range(3):
            new_con[j] += INTER_SUB_COUPLING * act_mean
            new_eng[j] += INTER_SUB_COUPLING * acc_mean
        for i in range(self.N):
            new_eng[i] = max(new_eng[i], self.C - V4_FLOOR*1.5)
            new_con[i] = min(new_con[i], self.C + V4_FLOOR*1.5)
        self.eng_states = new_eng
        self.con_states = new_con

    def observable_ssn(self):
        eng_parent_obs = []
        con_parent_obs = []
        for parent_idx in range(3):
            base = parent_idx * 3
            eng_base_signal = self.eng_states[base] - self.C
            eng_valve = 1.0
            for sub_idx in [1, 2]:
                i = base + sub_idx
                ef = max(self.ara_eng[i] - 1.0, 0.0)
                fd = self.eng_states[i] - self.C
                vp = max(0.0, 1.0 + ef * fd)
                eng_valve *= vp
            eng_parent_obs.append(self.C + eng_base_signal * eng_valve)
            con_base_signal = self.con_states[base] - self.C
            con_valve = 1.0
            for sub_idx in [1, 2]:
                i = base + sub_idx
                cf = max(1.0 - self.ara_con[i], 0.0)
                fd = self.C - self.con_states[i]
                vp = max(0.0, 1.0 + cf * fd)
                con_valve *= vp
            con_parent_obs.append(self.C + con_base_signal * con_valve)
        es2 = eng_parent_obs[1]
        e1x = eng_parent_obs[0] - self.C
        e3x = eng_parent_obs[2] - self.C
        cs = max(con_parent_obs[2] - self.C, 0)
        cr = max(self.C - con_parent_obs[0], 0)
        return es2 + PI_LEAK * (e1x + e3x) * 0.3 + PI_LEAK * (cs - cr) * 0.5

# ═══════════════════════════════════════════════════════════════════
# SINGLE-CHANNEL MODEL
# ═══════════════════════════════════════════════════════════════════

def single_channel_predict(log_val, C, t, phase0):
    midoff = MIDOFF_SINGLE
    wdlog, eff = base_wave_dlog(log_val, C, ARA_SSN_SINGLE, 1, t, phase0, midoff, HALE_PERIOD)
    bounced = log_val + wdlog
    ef = max(ARA_SSN_SINGLE - 1.0, 0.0)
    va = ef * V4_DEPTH
    valley = C + va * np.sin(2 * np.pi * (t + 1) / HALE_PERIOD + phase0)
    d = bounced - valley
    if d > 0: c = -ef * V4_BASIN_DOWN * d
    else: c = -ef * V4_BASIN_UP * d
    nv = bounced + c
    floor = C - V4_FLOOR
    if nv < floor: nv = floor + (nv - floor) * 0.1
    return nv

# ═══════════════════════════════════════════════════════════════════
# DATA
# ═══════════════════════════════════════════════════════════════════

def load_ssn():
    p = os.path.join(os.path.dirname(__file__), '..', 'solar_test', 'sunspots.txt')
    monthly = {}
    with open(p) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 4: continue
            try:
                y = int(parts[0]); v = float(parts[3])
                if v < 0: continue
                monthly.setdefault(y, []).append(v)
            except: continue
    return {y: np.mean(v) for y, v in monthly.items() if len(v) >= 6}

def load_eq():
    return {
        1900:13,1901:14,1902:8,1903:10,1904:16,1905:26,1906:32,1907:27,
        1908:18,1909:32,1910:36,1911:24,1912:22,1913:23,1914:22,1915:18,
        1916:25,1917:21,1918:21,1919:14,1920:8,1921:11,1922:14,1923:23,
        1924:18,1925:17,1926:19,1927:20,1928:22,1929:19,1930:13,1931:26,
        1932:13,1933:14,1934:22,1935:24,1936:21,1937:22,1938:26,1939:21,
        1940:23,1941:24,1942:27,1943:41,1944:31,1945:27,1946:35,1947:26,
        1948:28,1949:36,1950:15,1951:21,1952:17,1953:22,1954:17,1955:19,
        1956:15,1957:34,1958:10,1959:15,1960:22,1961:18,1962:15,1963:20,
        1964:15,1965:22,1966:19,1967:16,1968:30,1969:27,1970:29,1971:23,
        1972:20,1973:16,1974:21,1975:21,1976:25,1977:16,1978:18,1979:15,
        1980:18,1981:14,1982:10,1983:15,1984:8,1985:15,1986:6,1987:11,
        1988:8,1989:7,1990:13,1991:11,1992:23,1993:16,1994:15,1995:25,
        1996:22,1997:20,1998:16,1999:23,2000:16,2001:15,2002:13,2003:14,
        2004:16,2005:11,2006:11,2007:18,2008:12,2009:16,2010:23,2011:19,
        2012:12,2013:17,2014:11,2015:19,2016:16,2017:7,2018:17,2019:11,
        2020:9,2021:16,2022:10,2023:18,2024:15
    }

# ═══════════════════════════════════════════════════════════════════
# PHASE CALIBRATION
# ═══════════════════════════════════════════════════════════════════

def calibrate_superposition(train_data, model_class, ara_eng, ara_con, periods, n_phases=24):
    """Calibrate phase for superposition-based models."""
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase, best_score = 0.0, -999

    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases
        test_start = max(0, len(years) - 15)
        model = model_class(ara_eng, ara_con, periods, C, phase0)
        start_log = np.log10(max(train_data[years[test_start]], 0.1))
        model.init_from_observation(start_log)

        pred_changes, act_changes = [], []
        preds = model.predict_sequence(len(years) - test_start - 1)

        prev = start_log
        for idx, i in enumerate(range(test_start + 1, len(years))):
            if idx >= len(preds): break
            obs = preds[idx]
            pred_changes.append(obs - prev)
            actual_log = np.log10(max(train_data[years[i]], 0.1))
            actual_prev = np.log10(max(train_data[years[i-1]], 0.1))
            act_changes.append(actual_log - actual_prev)
            prev = obs

        if len(pred_changes) > 2:
            corr = np.corrcoef(pred_changes, act_changes)[0, 1]
            if not np.isnan(corr) and corr > best_score:
                best_score = corr
                best_phase = phase0

    return best_phase

def calibrate_iterative(train_data, n_phases=24):
    """Calibrate iterative F⁹ model."""
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase, best_score = 0.0, -999
    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases
        test_start = max(0, len(years) - 15)
        model = IterativeF9Model(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase0)
        start_log = np.log10(max(train_data[years[test_start]], 0.1))
        model.init_from_observation(start_log)
        pred_c, act_c = [], []
        prev = start_log
        for i in range(test_start + 1, len(years)):
            model.step(i - test_start)
            obs = model.observable_ssn()
            pred_c.append(obs - prev)
            al = np.log10(max(train_data[years[i]], 0.1))
            ap = np.log10(max(train_data[years[i-1]], 0.1))
            act_c.append(al - ap)
            prev = obs
        if len(pred_c) > 2:
            corr = np.corrcoef(pred_c, act_c)[0, 1]
            if not np.isnan(corr) and corr > best_score:
                best_score = corr; best_phase = phase0
    return best_phase

def calibrate_single(train_data, n_phases=24):
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase, best_score = 0.0, -999
    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases
        test_start = max(0, len(years) - 15)
        log_val = np.log10(max(train_data[years[test_start]], 0.1))
        pred_c, act_c = [], []
        prev = log_val
        for i in range(test_start + 1, len(years)):
            log_val = single_channel_predict(log_val, C, i - test_start, phase0)
            pred_c.append(log_val - prev)
            al = np.log10(max(train_data[years[i]], 0.1))
            ap = np.log10(max(train_data[years[i-1]], 0.1))
            act_c.append(al - ap)
            prev = log_val
        if len(pred_c) > 2:
            corr = np.corrcoef(pred_c, act_c)[0, 1]
            if not np.isnan(corr) and corr > best_score:
                best_score = corr; best_phase = phase0
    return best_phase

# ═══════════════════════════════════════════════════════════════════
# EVALUATION
# ═══════════════════════════════════════════════════════════════════

def evaluate(actual_dict, pred_dict, years):
    av = [actual_dict[y] for y in years]
    pv = [pred_dict[y] for y in years]
    n = len(years)
    if n < 3: return {'corr': 0, 'dir': 0, 'x2': 0, 'mae': 999}
    corr = np.corrcoef(av, pv)[0, 1]
    if np.isnan(corr): corr = 0
    dc = sum(1 for i in range(1, n) if (av[i]-av[i-1])*(pv[i]-pv[i-1]) > 0)
    direction = dc / (n - 1) * 100
    w2 = sum(1 for a, p in zip(av, pv) if a > 0 and p > 0 and max(a,p)/max(min(a,p),0.1) <= 2)
    within_2x = w2 / n * 100
    mae = np.mean(np.abs(np.array(av) - np.array(pv)))
    return {'corr': corr, 'dir': direction, 'x2': within_2x, 'mae': mae}

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    ssn_data = load_ssn()
    eq_data = load_eq()
    all_ssn_years = sorted(ssn_data.keys())
    all_eq_years = sorted(eq_data.keys())

    print("=" * 80)
    print("SCRIPT 199 — NORMAL MODE DECOMPOSITION: HOW PHYSICS DOES IT")
    print("=" * 80)
    print()

    # Show the eigenstructure
    K = build_coupling_matrix(P_SUBS)
    eigenvalues, eigenvectors = np.linalg.eigh(K)
    print("Coupling matrix eigenvalues:")
    for n, ev in enumerate(eigenvalues):
        print(f"  Mode {n}: eigenvalue = {ev:+.4f}")
    print()

    # Show beat frequencies
    print("φ-cascade beat structure:")
    for i in range(len(P_SUBS) - 1):
        if i % 3 < 2:  # adjacent within triad
            beat_period = 1.0 / abs(1.0/P_SUBS[i] - 1.0/P_SUBS[i+1])
            print(f"  Beat({P_SUBS[i]:.1f}y, {P_SUBS[i+1]:.1f}y) = {beat_period:.1f}y")
    print()

    # ═══════════════════════════════════════════════════════════
    # TEST ALL MODELS
    # ═══════════════════════════════════════════════════════════

    splits = [1989, 1994, 1999, 2004, 2009]

    all_results = {name: [] for name in ['NormalMode', 'Beats', 'Hybrid', 'F9-iter', 'F1', 'Sine']}

    print("=" * 80)
    print("SUNSPOT PREDICTIONS")
    print("=" * 80)

    for split_year in splits:
        train = {y: v for y, v in ssn_data.items() if y <= split_year}
        pred_years = [y for y in all_ssn_years if y > split_year and y <= 2025]
        if not pred_years: continue

        C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
        start_year = max(train.keys())
        start_log = np.log10(max(ssn_data[start_year], 0.1))

        preds = {}

        # Normal Mode model
        phase_nm = calibrate_superposition(train, NormalModeModel, ARA_ENG_9, ARA_CON_9, P_SUBS)
        nm = NormalModeModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase_nm)
        nm.init_from_observation(start_log)
        nm_preds = nm.predict_sequence(len(pred_years))
        p_nm = {y: max(10**nm_preds[i], 0) for i, y in enumerate(pred_years)}
        preds['NormalMode'] = p_nm
        all_results['NormalMode'].append(evaluate(ssn_data, p_nm, pred_years))

        # Beat model
        phase_bt = calibrate_superposition(train, BeatFrequencyModel, ARA_ENG_9, ARA_CON_9, P_SUBS)
        bt = BeatFrequencyModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase_bt)
        bt.init_from_observation(start_log)
        bt_preds = bt.predict_sequence(len(pred_years))
        p_bt = {y: max(10**bt_preds[i], 0) for i, y in enumerate(pred_years)}
        preds['Beats'] = p_bt
        all_results['Beats'].append(evaluate(ssn_data, p_bt, pred_years))

        # Hybrid model
        phase_hy = calibrate_superposition(train, HybridNormalModeModel, ARA_ENG_9, ARA_CON_9, P_SUBS)
        hy = HybridNormalModeModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase_hy)
        hy.init_from_observation(start_log)
        hy_preds = hy.predict_sequence(len(pred_years))
        p_hy = {y: max(10**hy_preds[i], 0) for i, y in enumerate(pred_years)}
        preds['Hybrid'] = p_hy
        all_results['Hybrid'].append(evaluate(ssn_data, p_hy, pred_years))

        # Iterative F⁹ (Script 197 v4)
        phase_it = calibrate_iterative(train)
        it_model = IterativeF9Model(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase_it)
        it_model.init_from_observation(start_log)
        p_it = {}
        for i, y in enumerate(pred_years):
            it_model.step(i + 1)
            p_it[y] = max(10**it_model.observable_ssn(), 0)
        preds['F9-iter'] = p_it
        all_results['F9-iter'].append(evaluate(ssn_data, p_it, pred_years))

        # F1
        phase_f1 = calibrate_single(train)
        log_val = start_log
        p_f1 = {}
        for i, y in enumerate(pred_years):
            log_val = single_channel_predict(log_val, C, i + 1, phase_f1)
            p_f1[y] = max(10**log_val, 0)
        preds['F1'] = p_f1
        all_results['F1'].append(evaluate(ssn_data, p_f1, pred_years))

        # Sine
        train_vals = [ssn_data[y] for y in sorted(train.keys())]
        mean_ssn = np.mean(train_vals)
        amp_ssn = (max(train_vals) - min(train_vals)) / 2
        best_sp, best_sc = 0, -999
        for pi in range(48):
            p0 = 2 * np.pi * pi / 48
            sp = {y: max(mean_ssn + amp_ssn * np.sin(2*np.pi*y/11+p0), 0) for y in pred_years}
            e = evaluate(ssn_data, sp, pred_years)
            if e['corr'] > best_sc: best_sc = e['corr']; best_sp = p0
        p_sine = {y: max(mean_ssn + amp_ssn * np.sin(2*np.pi*y/11+best_sp), 0) for y in pred_years}
        preds['Sine'] = p_sine
        all_results['Sine'].append(evaluate(ssn_data, p_sine, pred_years))

        n = len(pred_years)
        print(f"\n  Train <={split_year}, Predict {split_year+1}-2025 ({n} years)")
        print(f"  {'Model':<16s} {'Corr':>8s} {'Dir%':>8s} {'x2%':>8s} {'MAE':>8s}")
        print(f"  {'-'*14} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
        for name in ['NormalMode', 'Beats', 'Hybrid', 'F9-iter', 'F1', 'Sine']:
            ev = all_results[name][-1]
            print(f"  {name:<16s} {ev['corr']:+8.3f} {ev['dir']:8.1f} {ev['x2']:8.1f} {ev['mae']:8.1f}")

        # Year-by-year
        print(f"\n  Year-by-year (first 12):")
        print(f"    {'Year':>6s} {'Actual':>8s} {'NormMode':>8s} {'Beats':>8s} {'Hybrid':>8s} {'F9-iter':>8s} {'Sine':>8s}")
        for y in pred_years[:12]:
            print(f"    {y:>6d} {ssn_data[y]:8.1f} {preds['NormalMode'][y]:8.1f} {preds['Beats'][y]:8.1f} {preds['Hybrid'][y]:8.1f} {preds['F9-iter'][y]:8.1f} {preds['Sine'][y]:8.1f}")

    # ═══════════════════════════════════════════════════════════
    # COMPARISON TABLE
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("OVERALL COMPARISON")
    print("=" * 80)

    print(f"\n  {'Model':<16s} {'Avg Corr':>10s} {'Avg MAE':>10s} {'Avg Dir':>10s} {'Beats Sine':>12s}")
    print(f"  {'-'*14} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")

    for name in ['NormalMode', 'Beats', 'Hybrid', 'F9-iter', 'F1', 'Sine']:
        res = all_results[name]
        ac = np.mean([r['corr'] for r in res])
        am = np.mean([r['mae'] for r in res])
        ad = np.mean([r['dir'] for r in res])
        beats = sum(1 for r, s in zip(res, all_results['Sine']) if r['mae'] < s['mae'])
        print(f"  {name:<16s} {ac:+10.3f} {am:10.1f} {ad:10.1f}% {beats}/5 splits")

    sine_mae = np.mean([r['mae'] for r in all_results['Sine']])
    for name in ['NormalMode', 'Beats', 'Hybrid', 'F9-iter']:
        m = np.mean([r['mae'] for r in all_results[name]])
        gap = m - sine_mae
        pct = gap / sine_mae * 100
        sym = "BEATS" if gap < 0 else "gap"
        print(f"\n  {name}: MAE={m:.1f}, {sym}: {abs(gap):.1f} ({abs(pct):.0f}%)")

    # Per-split breakdown
    print()
    print("  Per-split MAE:")
    print(f"    {'Split':>6s} {'NormMode':>10s} {'Beats':>10s} {'Hybrid':>10s} {'F9-iter':>10s} {'Sine':>10s} {'Best':>10s}")
    for i, sy in enumerate(splits):
        vals = {}
        for name in ['NormalMode', 'Beats', 'Hybrid', 'F9-iter', 'Sine']:
            vals[name] = all_results[name][i]['mae']
        best_name = min(vals, key=vals.get)
        print(f"    {sy:>6d} {vals['NormalMode']:10.1f} {vals['Beats']:10.1f} {vals['Hybrid']:10.1f} {vals['F9-iter']:10.1f} {vals['Sine']:10.1f} {best_name:>10s}")

    print()
    print("=" * 80)
    print("Script 199 complete.")
    print("=" * 80)
