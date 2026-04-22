#!/usr/bin/env python3
"""
Script 200 — Perpendicular Singularity: The Other Helix
==============================================================================

Dylan's insight: "At the top of each wave, that is probably a singularity for
the ARA on the perpendicular. It's 3 systems coupling: System A, coupler,
System B. It all rotates around φ, which just maps the singularity arcs of
all ARAs. That's why ARA scales vertically."

THE PHYSICS:

    The peak of one oscillation is NOT just a turning point — it's the
    SINGULARITY CROSSING for a system running perpendicular to it.

    Evidence:
    - Solar magnetic field FLIPS at sunspot maximum (peak = singularity for
      the magnetic polarity system, which runs perpendicular to activity)
    - Heart electrical system RESETS at peak systole
    - Piston REVERSES at top dead center

    Energy doesn't just reflect at the peak — it TRANSFERS to the
    perpendicular system. The amplitude of the next cycle depends on how
    much energy crossed to the perpendicular at the previous peak.

    This is DNA: two antiparallel helices (engine + consumer) coupled
    through base pairs (singularity). The main oscillation is one helix.
    The perpendicular oscillation is the other helix. The energy exchange
    at peaks and troughs IS the base-pair coupling.

ARCHITECTURE:

    For each normal mode n:
        - Main oscillation: Aₙ cos(ωₙt + φₙ)
        - Perpendicular:    Bₙ sin(ωₙt + φₙ)   [π/2 phase shift]
        - At peak (d/dt main ≈ 0, main > 0):
            Transfer: Bₙ += κ·Aₙ, Aₙ *= (1-κ)
        - At trough (d/dt main ≈ 0, main < 0):
            Return:   Aₙ += κ·Bₙ, Bₙ *= (1-κ)

    The coupling κ is NOT constant — it depends on the ARA value.
    Engine systems (ARA > 1): stronger transfer OUT at peaks (φ-scaled)
    Consumer systems (ARA < 1): weaker transfer, more retention

    The AMPLITUDE MODULATION between cycles emerges naturally:
    - If a cycle was strong (large Aₙ at peak), more energy transfers out
    - Next cycle starts with less energy → weaker
    - Perpendicular accumulates → returns more at trough
    - Self-regulating oscillation with φ-driven amplitude envelope

    This is the missing piece from Script 199's Hybrid model (MAE 47.9,
    8% from sine). The Hybrid has modes and valley but no mechanism for
    inter-cycle amplitude variation.

THREE MODELS:

    1. PerpendicularHybrid: Hybrid model + perpendicular singularity gates
    2. DoubleHelixModel: Full DNA-inspired dual helix with base-pair coupling
    3. RotatingARAs: Three full ARA systems (A, coupler, B) rotating around φ
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
# φ-PERIOD CASCADE (same as Script 199)
# ═══════════════════════════════════════════════════════════════════

P_PARENT = [HALE_PERIOD, HALE_PERIOD / PHI, HALE_PERIOD / PHI**2]

P_SUBS = []
for parent_p in P_PARENT:
    for sub_idx in range(3):
        P_SUBS.append(parent_p / PHI**sub_idx)

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
# COUPLING MATRIX (from Script 199)
# ═══════════════════════════════════════════════════════════════════

def build_coupling_matrix(periods, kappa=PI_LEAK):
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

    for i in range(N):
        K[i, i] = -np.sum(K[i, :])

    return K


# ═══════════════════════════════════════════════════════════════════
# MODEL 1: PERPENDICULAR HYBRID
# ═══════════════════════════════════════════════════════════════════

class PerpendicularHybridModel:
    """
    Script 199 Hybrid + perpendicular singularity gates at peaks/troughs.

    Each normal mode has:
        - Main amplitude Aₙ (cosine component)
        - Perpendicular amplitude Bₙ (sine component = π/2 shift)

    At wave PEAKS: energy drains from main → perpendicular
        Aₙ → Aₙ(1-κ), Bₙ → Bₙ + κ·Aₙ
    At wave TROUGHS: energy returns from perpendicular → main
        Bₙ → Bₙ(1-κ), Aₙ → Aₙ + κ·Bₙ

    κ = transfer fraction, scaled by engine factor (ARA-driven)
    This creates amplitude modulation: strong cycle → more drain → weaker next
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base,
                 kappa_peak=None, kappa_trough=None):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.omega_nat = 2 * np.pi / self.periods
        self.ara_eng = np.array(ara_eng_9)
        self.ara_con = np.array(ara_con_9)

        # Coupling matrix eigendecomposition
        K = build_coupling_matrix(periods_9)
        eigenvalues, eigenvectors = np.linalg.eigh(K)
        self.eigenvalues = eigenvalues
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)

        # Mode frequencies
        self.omega_modes = np.zeros(self.N)
        for n in range(self.N):
            weights = np.abs(eigenvectors[:, n])
            weights = weights / max(np.sum(weights), 1e-10)
            omega_w = np.sum(weights * self.omega_nat)
            shift = eigenvalues[n] * PI_LEAK
            self.omega_modes[n] = max(omega_w + shift, omega_w * 0.5)

        # ARA-based mode properties
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

        # MAIN amplitudes (cosine component — the helix you observe)
        self.A = np.zeros(self.N)
        # PERPENDICULAR amplitudes (sine component — the other helix)
        self.B = np.zeros(self.N)

        # Transfer fractions at peaks and troughs
        # κ_peak: how much drains OUT at peaks (φ-scaled for engines)
        # κ_trough: how much returns at troughs
        avg_ef = np.mean(self.engine_factors)
        if kappa_peak is None:
            self.kappa_peak = PI_LEAK * PHI_LEAK  # ~0.0877
        else:
            self.kappa_peak = kappa_peak
        if kappa_trough is None:
            self.kappa_trough = PI_LEAK * PHI_LEAK * PHI_LEAK  # ~0.0542
        else:
            self.kappa_trough = kappa_trough

        # Per-mode transfer fraction (ARA-scaled)
        self.kappa_per_mode = np.zeros(self.N)
        for n in range(self.N):
            # Modes aligned with high-engine channels transfer more
            self.kappa_per_mode[n] = self.kappa_peak * (1.0 + self.mode_drive[n])

        # Track previous signal for peak/trough detection
        self.prev_signal = np.zeros(self.N)
        self.prev_prev_signal = np.zeros(self.N)

        # Valley parameters
        self.valley_amp = np.mean(self.engine_factors) * V4_DEPTH

        # Gate tracking
        self.gate_fired = False

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
        self.A = self.V_inv @ x0
        for n in range(self.N):
            self.A[n] *= (1.0 + self.mode_drive[n] * 2.0)

        # Perpendicular starts empty — energy hasn't transferred yet
        self.B = np.zeros(self.N)

        # Initialize tracking
        self.prev_signal = self.A.copy()
        self.prev_prev_signal = self.A.copy()

    def observable_ssn(self, t):
        """
        Superposition with perpendicular singularity gates.

        At each timestep:
        1. Compute each mode's current value
        2. Detect peaks and troughs (sign change of derivative)
        3. Fire singularity gate: transfer energy at peaks, return at troughs
        4. Apply valley envelope and basin correction
        """
        # Current mode signals
        current_signal = np.zeros(self.N)
        for n in range(self.N):
            current_signal[n] = self.A[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n]
            )

        # ─── PERPENDICULAR SINGULARITY GATE ───
        # Detect peaks and troughs per mode
        for n in range(self.N):
            curr = current_signal[n]
            prev = self.prev_signal[n]
            pprev = self.prev_prev_signal[n]

            # Derivative sign change: peak if prev > pprev AND prev > curr
            if prev > pprev and prev > curr and prev > 0:
                # PEAK DETECTED — singularity for perpendicular system
                # Energy transfers OUT: main → perpendicular
                # Transfer is φ-asymmetric: going DOWN (main→perp) = ×φ
                transfer = self.kappa_per_mode[n] * abs(self.A[n])
                self.A[n] -= transfer * np.sign(self.A[n])
                self.B[n] += transfer * SING_DOWN  # Amplified by φ going down

            elif prev < pprev and prev < curr and prev < 0:
                # TROUGH DETECTED — energy returns from perpendicular
                # Transfer is φ-asymmetric: going UP (perp→main) = ×(1/φ)
                transfer = self.kappa_trough * abs(self.B[n])
                self.B[n] -= transfer * np.sign(self.B[n])
                self.A[n] += transfer * SING_UP  # Attenuated by 1/φ going up

        # Update tracking
        self.prev_prev_signal = self.prev_signal.copy()
        self.prev_signal = current_signal.copy()

        # ─── MAIN SUPERPOSITION ───
        signal = np.sum(current_signal)

        # ─── PERPENDICULAR CONTRIBUTION ───
        # The perpendicular oscillation also contributes to the observable
        # (like the minor groove of DNA — it modulates, doesn't dominate)
        perp_signal = 0.0
        for n in range(self.N):
            perp_signal += self.B[n] * np.sin(
                self.omega_modes[n] * t + self.mode_phases[n]
            )
        # Perpendicular modulates at π-leak level
        signal += PI_LEAK * perp_signal

        # ─── VALLEY ENVELOPE (asymmetric basin) ───
        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0
        )
        raw_obs = self.C + signal

        avg_ef = np.mean(self.engine_factors)
        displacement = raw_obs - valley
        if displacement > 0:
            correction = -avg_ef * V4_BASIN_DOWN * displacement * 0.3
        else:
            correction = -avg_ef * V4_BASIN_UP * displacement * 0.3

        obs = raw_obs + correction

        # ─── ONE-SHOT GATE (floor) ───
        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            overflow = floor - obs
            obs = floor
            for n in range(self.N):
                self.A[n] += overflow * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False

        return obs

    def predict_sequence(self, n_years):
        preds = []
        for t in range(1, n_years + 1):
            preds.append(self.observable_ssn(t))
        return preds


# ═══════════════════════════════════════════════════════════════════
# MODEL 2: DOUBLE HELIX
# ═══════════════════════════════════════════════════════════════════

class DoubleHelixModel:
    """
    DNA-inspired: two full helices (engine + consumer) with base-pair coupling.

    Helix A: engine oscillation — runs the main signal
    Helix B: consumer oscillation — antiparallel mirror (π phase shift)
    Base pairs: deterministic coupling at specific phase positions

    The coupling doesn't happen continuously — it happens at specific
    angular positions (like base pairs at fixed intervals along the helix).

    In DNA: base pairs every 36° (360/10 = 36° per base pair)
    In ARA: coupling at golden angle intervals (≈137.5°)

    The base pair coupling is ONE-SHOT per crossing:
    - When Helix A passes a coupling angle: energy transfers to Helix B
    - When Helix B passes the same angle: energy returns to Helix A
    - Transfer amount = φ downhill (A→B), 1/φ uphill (B→A)
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.omega_nat = 2 * np.pi / self.periods
        self.ara_eng = np.array(ara_eng_9)
        self.ara_con = np.array(ara_con_9)

        # Coupling matrix eigendecomposition
        K = build_coupling_matrix(periods_9)
        eigenvalues, eigenvectors = np.linalg.eigh(K)
        self.eigenvalues = eigenvalues
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)

        # Mode frequencies
        self.omega_modes = np.zeros(self.N)
        for n in range(self.N):
            weights = np.abs(eigenvectors[:, n])
            weights = weights / max(np.sum(weights), 1e-10)
            omega_w = np.sum(weights * self.omega_nat)
            shift = eigenvalues[n] * PI_LEAK
            self.omega_modes[n] = max(omega_w + shift, omega_w * 0.5)

        # ARA factors
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

        # HELIX A amplitudes (engine — leading strand)
        self.helix_A = np.zeros(self.N)
        # HELIX B amplitudes (consumer — lagging strand, antiparallel)
        self.helix_B = np.zeros(self.N)

        # Golden angle for base-pair positions
        self.golden_angle = 2 * np.pi / (PHI ** 2)  # ≈ 137.5°

        # Base-pair coupling strength
        self.bp_coupling = PI_LEAK * PHI_LEAK  # ~0.088

        # Track angular position of each mode
        self.last_angle = np.zeros(self.N)
        self.bp_count = np.zeros(self.N, dtype=int)

        # Valley
        self.valley_amp = np.mean(self.engine_factors) * V4_DEPTH

        # Gate
        self.gate_fired = False

    def init_from_observation(self, log_ssn):
        deviation = log_ssn - self.C
        x0 = np.zeros(self.N)
        ef_sum = np.sum(self.engine_factors)
        if ef_sum > 0:
            for i in range(self.N):
                x0[i] = deviation * self.engine_factors[i] / ef_sum
        else:
            x0[:] = deviation / self.N

        self.helix_A = self.V_inv @ x0
        for n in range(self.N):
            self.helix_A[n] *= (1.0 + self.mode_drive[n] * 2.0)

        # Helix B starts as attenuated mirror
        self.helix_B = -self.helix_A * PHI_LEAK

    def observable_ssn(self, t):
        """
        Double helix observable:
        - Helix A provides main signal
        - Helix B provides antiparallel modulation
        - Base-pair coupling transfers energy at golden-angle intervals
        """

        # ─── BASE-PAIR COUPLING (at golden angle crossings) ───
        for n in range(self.N):
            current_angle = (self.omega_modes[n] * t + self.mode_phases[n]) % (2 * np.pi)

            # Check if we crossed a golden-angle base-pair position
            expected_bp = (self.bp_count[n] + 1) * self.golden_angle % (2 * np.pi)
            angular_dist = abs(current_angle - expected_bp)
            if angular_dist < 0.5 or angular_dist > 2 * np.pi - 0.5:
                # BASE PAIR CROSSING — one-shot energy transfer
                self.bp_count[n] += 1

                # Direction depends on which helix is "ahead" at this angle
                if abs(self.helix_A[n]) > abs(self.helix_B[n]):
                    # A is dominant → transfer A→B (downhill, ×φ)
                    transfer = self.bp_coupling * abs(self.helix_A[n])
                    self.helix_A[n] -= transfer * np.sign(self.helix_A[n])
                    self.helix_B[n] += transfer * SING_DOWN * np.sign(self.helix_A[n])
                else:
                    # B is dominant → transfer B→A (uphill, ×1/φ)
                    transfer = self.bp_coupling * abs(self.helix_B[n])
                    self.helix_B[n] -= transfer * np.sign(self.helix_B[n])
                    self.helix_A[n] += transfer * SING_UP * np.sign(self.helix_B[n])

            self.last_angle[n] = current_angle

        # ─── SUPERPOSITION ───
        # Helix A (engine) — main observable
        signal_A = 0.0
        for n in range(self.N):
            signal_A += self.helix_A[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n]
            )

        # Helix B (consumer) — antiparallel modulation
        signal_B = 0.0
        for n in range(self.N):
            signal_B += self.helix_B[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n] + MIRROR_PHASE
            )

        # Combined: A dominates, B modulates at π-leak
        signal = signal_A + PI_LEAK * signal_B

        # ─── VALLEY ENVELOPE ───
        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0
        )
        raw_obs = self.C + signal

        avg_ef = np.mean(self.engine_factors)
        displacement = raw_obs - valley
        if displacement > 0:
            correction = -avg_ef * V4_BASIN_DOWN * displacement * 0.3
        else:
            correction = -avg_ef * V4_BASIN_UP * displacement * 0.3

        obs = raw_obs + correction

        # ─── FLOOR GATE ───
        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            overflow = floor - obs
            obs = floor
            for n in range(self.N):
                self.helix_A[n] += overflow * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False

        return obs

    def predict_sequence(self, n_years):
        preds = []
        for t in range(1, n_years + 1):
            preds.append(self.observable_ssn(t))
        return preds


# ═══════════════════════════════════════════════════════════════════
# MODEL 3: ROTATING ARAs — Three full ARA systems around φ
# ═══════════════════════════════════════════════════════════════════

class RotatingARAModel:
    """
    Three full ARA systems rotating around φ.

    System A: the observed oscillation (sunspot activity)
    System C: the coupler (solar magnetic field / polarity)
    System B: the perpendicular consumer (internal convection / dynamo)

    Each system is a full ARA with its own engine/consumer/singularity.
    They couple at specific rotation angles:
        - A's peak = C's singularity → energy flows A→C
        - C's peak = B's singularity → energy flows C→B
        - B's peak = A's singularity → energy flows B→A

    The rotation period between couplings = golden angle ≈ 137.5°
    This means the three systems are NOT equally spaced (120°).
    They're φ-spaced: 137.5°, 137.5°, 85° — a SCALENE arrangement.

    The total energy is conserved: A + C + B = constant (= 2.0 in ARA terms)
    φ + 1/φ = √5 per crossing, but 3 crossings per cycle redistribute.
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.omega_nat = 2 * np.pi / self.periods
        self.ara_eng = np.array(ara_eng_9)
        self.ara_con = np.array(ara_con_9)

        # Eigendecomposition
        K = build_coupling_matrix(periods_9)
        eigenvalues, eigenvectors = np.linalg.eigh(K)
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)

        self.omega_modes = np.zeros(self.N)
        for n in range(self.N):
            weights = np.abs(eigenvectors[:, n])
            weights = weights / max(np.sum(weights), 1e-10)
            omega_w = np.sum(weights * self.omega_nat)
            shift = eigenvalues[n] * PI_LEAK
            self.omega_modes[n] = max(omega_w + shift, omega_w * 0.5)

        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)
        self.mode_drive = np.zeros(self.N)
        for n in range(self.N):
            self.mode_drive[n] = np.sum(np.abs(eigenvectors[:, n]) * self.engine_factors)
        md_sum = np.sum(self.mode_drive)
        if md_sum > 0:
            self.mode_drive /= md_sum

        self.phase0 = phase0_base
        self.mode_phases = np.zeros(self.N)
        for n in range(self.N):
            self.mode_phases[n] = phase0_base + n * 2 * np.pi / self.N

        # THREE SYSTEMS — mode amplitudes for each
        self.sys_A = np.zeros(self.N)  # Observed (sunspot activity)
        self.sys_C = np.zeros(self.N)  # Coupler (magnetic field)
        self.sys_B = np.zeros(self.N)  # Perpendicular (dynamo)

        # Golden angle offset between systems
        self.ga = 2 * np.pi / (PHI ** 2)  # ≈ 137.5° = 2.399 rad

        # Phase offsets for the three systems
        # A at 0, C at golden angle, B at 2×golden angle
        self.phase_A = 0.0
        self.phase_C = self.ga       # ~137.5°
        self.phase_B = 2 * self.ga   # ~275° (≈ -85° from full circle)

        # Transfer coupling
        self.kappa = PI_LEAK * PHI_LEAK

        # Track for peak detection
        self.prev_A = np.zeros(self.N)
        self.pprev_A = np.zeros(self.N)
        self.prev_C = np.zeros(self.N)
        self.pprev_C = np.zeros(self.N)
        self.prev_B = np.zeros(self.N)
        self.pprev_B = np.zeros(self.N)

        # Valley
        self.valley_amp = np.mean(self.engine_factors) * V4_DEPTH
        self.gate_fired = False

    def init_from_observation(self, log_ssn):
        deviation = log_ssn - self.C
        x0 = np.zeros(self.N)
        ef_sum = np.sum(self.engine_factors)
        if ef_sum > 0:
            for i in range(self.N):
                x0[i] = deviation * self.engine_factors[i] / ef_sum
        else:
            x0[:] = deviation / self.N

        self.sys_A = self.V_inv @ x0
        for n in range(self.N):
            self.sys_A[n] *= (1.0 + self.mode_drive[n] * 2.0)

        # Coupler starts at intermediate level
        self.sys_C = self.sys_A * PHI_LEAK * 0.5
        # Perpendicular starts near zero
        self.sys_B = -self.sys_A * PHI_LEAK * PHI_LEAK

        self.prev_A = self.sys_A.copy()
        self.pprev_A = self.sys_A.copy()

    def _signal(self, amps, t, phase_offset):
        """Compute signal for one system."""
        s = np.zeros(self.N)
        for n in range(self.N):
            s[n] = amps[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n] + phase_offset
            )
        return s

    def observable_ssn(self, t):
        """
        Three rotating ARAs with singularity gates at each other's peaks.
        """
        # Current signals for all three systems
        sig_A = self._signal(self.sys_A, t, self.phase_A)
        sig_C = self._signal(self.sys_C, t, self.phase_C)
        sig_B = self._signal(self.sys_B, t, self.phase_B)

        # ─── SINGULARITY GATES ───
        for n in range(self.N):
            # A's peak = C's singularity: A→C transfer
            if (self.prev_A[n] > self.pprev_A[n] and
                self.prev_A[n] > sig_A[n] and self.prev_A[n] > 0):
                transfer = self.kappa * abs(self.sys_A[n])
                self.sys_A[n] -= transfer * np.sign(self.sys_A[n])
                self.sys_C[n] += transfer * SING_DOWN * np.sign(self.sys_A[n])

            # C's peak = B's singularity: C→B transfer
            if (self.prev_C[n] > self.pprev_C[n] and
                self.prev_C[n] > sig_C[n] and self.prev_C[n] > 0):
                transfer = self.kappa * abs(self.sys_C[n])
                self.sys_C[n] -= transfer * np.sign(self.sys_C[n])
                self.sys_B[n] += transfer * SING_DOWN * np.sign(self.sys_C[n])

            # B's peak = A's singularity: B→A return (uphill, attenuated)
            if (self.prev_B[n] > self.pprev_B[n] and
                self.prev_B[n] > sig_B[n] and self.prev_B[n] > 0):
                transfer = self.kappa * abs(self.sys_B[n])
                self.sys_B[n] -= transfer * np.sign(self.sys_B[n])
                self.sys_A[n] += transfer * SING_UP * np.sign(self.sys_B[n])

        # Update tracking
        self.pprev_A = self.prev_A.copy()
        self.prev_A = sig_A.copy()
        self.pprev_C = self.prev_C.copy()
        self.prev_C = sig_C.copy()
        self.pprev_B = self.prev_B.copy()
        self.prev_B = sig_B.copy()

        # ─── OBSERVABLE ───
        # System A is the primary observable
        total_A = np.sum(sig_A)
        # Coupler and perpendicular modulate
        total_C = np.sum(sig_C)
        total_B = np.sum(sig_B)

        # A dominates, C modulates at π-leak, B at π-leak²
        signal = total_A + PI_LEAK * total_C + PI_LEAK * PHI_LEAK * total_B

        # ─── VALLEY ───
        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0
        )
        raw_obs = self.C + signal

        avg_ef = np.mean(self.engine_factors)
        displacement = raw_obs - valley
        if displacement > 0:
            correction = -avg_ef * V4_BASIN_DOWN * displacement * 0.3
        else:
            correction = -avg_ef * V4_BASIN_UP * displacement * 0.3

        obs = raw_obs + correction

        # ─── FLOOR GATE ───
        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            overflow = floor - obs
            obs = floor
            for n in range(self.N):
                self.sys_A[n] += overflow * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False

        return obs

    def predict_sequence(self, n_years):
        preds = []
        for t in range(1, n_years + 1):
            preds.append(self.observable_ssn(t))
        return preds


# ═══════════════════════════════════════════════════════════════════
# SCRIPT 199 HYBRID (baseline comparison)
# ═══════════════════════════════════════════════════════════════════

class HybridNormalModeModel:
    """Script 199 Hybrid — best previous model (MAE 47.9)."""

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.omega_nat = 2 * np.pi / self.periods
        self.ara_eng = np.array(ara_eng_9)
        self.ara_con = np.array(ara_con_9)

        K = build_coupling_matrix(periods_9)
        eigenvalues, eigenvectors = np.linalg.eigh(K)
        self.eigenvalues = eigenvalues
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)

        self.omega_modes = np.zeros(self.N)
        for n in range(self.N):
            weights = np.abs(eigenvectors[:, n])
            weights = weights / max(np.sum(weights), 1e-10)
            omega_w = np.sum(weights * self.omega_nat)
            shift = eigenvalues[n] * PI_LEAK
            self.omega_modes[n] = max(omega_w + shift, omega_w * 0.5)

        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)
        self.consumer_factors = np.maximum(1.0 - self.ara_con, 0.0)

        self.mode_drive = np.zeros(self.N)
        for n in range(self.N):
            self.mode_drive[n] = np.sum(np.abs(eigenvectors[:, n]) * self.engine_factors)
        md_sum = np.sum(self.mode_drive)
        if md_sum > 0:
            self.mode_drive /= md_sum

        self.phase0 = phase0_base
        self.mode_phases = np.zeros(self.N)
        for n in range(self.N):
            self.mode_phases[n] = phase0_base + n * 2 * np.pi / self.N

        self.mode_amps = np.zeros(self.N)
        self.valley_amp = np.mean(self.engine_factors) * V4_DEPTH
        self.valley_state = C
        self.gate_fired = False
        self.prev_obs = C

    def init_from_observation(self, log_ssn):
        deviation = log_ssn - self.C
        x0 = np.zeros(self.N)
        ef_sum = np.sum(self.engine_factors)
        if ef_sum > 0:
            for i in range(self.N):
                x0[i] = deviation * self.engine_factors[i] / ef_sum
        else:
            x0[:] = deviation / self.N
        self.mode_amps = self.V_inv @ x0
        for n in range(self.N):
            self.mode_amps[n] *= (1.0 + self.mode_drive[n] * 2.0)
        self.prev_obs = log_ssn
        self.valley_state = log_ssn

    def observable_ssn(self, t):
        signal = 0.0
        for n in range(self.N):
            signal += self.mode_amps[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n]
            )
        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0
        )
        raw_obs = self.C + signal
        avg_ef = np.mean(self.engine_factors)
        displacement = raw_obs - valley
        if displacement > 0:
            correction = -avg_ef * V4_BASIN_DOWN * displacement * 0.3
        else:
            correction = -avg_ef * V4_BASIN_UP * displacement * 0.3
        obs = raw_obs + correction
        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            overflow = floor - obs
            obs = floor
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
# DATA + CALIBRATION + EVALUATION (same as Script 199)
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


def calibrate_superposition(train_data, model_class, ara_eng, ara_con, periods, n_phases=24):
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
# SINE BASELINE
# ═══════════════════════════════════════════════════════════════════

def sine_predict(train_data, pred_years, ssn_data):
    train_vals = [train_data[y] for y in sorted(train_data.keys())]
    mean_ssn = np.mean(train_vals)
    amp_ssn = (max(train_vals) - min(train_vals)) / 2
    best_sp, best_sc = 0, -999
    for pi in range(48):
        p0 = 2 * np.pi * pi / 48
        sp = {y: max(mean_ssn + amp_ssn * np.sin(2*np.pi*y/11+p0), 0) for y in pred_years}
        e = evaluate(ssn_data, sp, pred_years)
        if e['corr'] > best_sc: best_sc = e['corr']; best_sp = p0
    return {y: max(mean_ssn + amp_ssn * np.sin(2*np.pi*y/11+best_sp), 0) for y in pred_years}


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    ssn_data = load_ssn()
    all_ssn_years = sorted(ssn_data.keys())

    print("=" * 80)
    print("SCRIPT 200 — PERPENDICULAR SINGULARITY: THE OTHER HELIX")
    print("=" * 80)
    print()
    print("Peak of wave = singularity for perpendicular system")
    print("Three systems: A (observed) ↔ C (coupler) ↔ B (perpendicular)")
    print("φ maps the singularity arcs — that's why ARA scales vertically")
    print()

    # Show transfer parameters
    kp = PI_LEAK * PHI_LEAK
    kt = PI_LEAK * PHI_LEAK * PHI_LEAK
    print(f"  κ_peak  (main→perp)  = π-leak × 1/φ = {kp:.4f}")
    print(f"  κ_trough (perp→main) = π-leak × 1/φ² = {kt:.4f}")
    print(f"  Asymmetry ratio: {kp/kt:.3f} (= φ)")
    print(f"  Peak transfer amplified by φ = {SING_DOWN:.4f}")
    print(f"  Trough return attenuated by 1/φ = {SING_UP:.4f}")
    print()

    splits = [1989, 1994, 1999, 2004, 2009]
    model_names = ['PerpHybrid', 'DoubleHelix', 'RotatingARA', 'Hybrid199', 'Sine']
    all_results = {name: [] for name in model_names}

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

        # Model 1: Perpendicular Hybrid
        phase = calibrate_superposition(train, PerpendicularHybridModel,
                                        ARA_ENG_9, ARA_CON_9, P_SUBS)
        m = PerpendicularHybridModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
        m.init_from_observation(start_log)
        p = m.predict_sequence(len(pred_years))
        preds['PerpHybrid'] = {y: max(10**p[i], 0) for i, y in enumerate(pred_years)}
        all_results['PerpHybrid'].append(evaluate(ssn_data, preds['PerpHybrid'], pred_years))

        # Model 2: Double Helix
        phase = calibrate_superposition(train, DoubleHelixModel,
                                        ARA_ENG_9, ARA_CON_9, P_SUBS)
        m = DoubleHelixModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
        m.init_from_observation(start_log)
        p = m.predict_sequence(len(pred_years))
        preds['DoubleHelix'] = {y: max(10**p[i], 0) for i, y in enumerate(pred_years)}
        all_results['DoubleHelix'].append(evaluate(ssn_data, preds['DoubleHelix'], pred_years))

        # Model 3: Rotating ARAs
        phase = calibrate_superposition(train, RotatingARAModel,
                                        ARA_ENG_9, ARA_CON_9, P_SUBS)
        m = RotatingARAModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
        m.init_from_observation(start_log)
        p = m.predict_sequence(len(pred_years))
        preds['RotatingARA'] = {y: max(10**p[i], 0) for i, y in enumerate(pred_years)}
        all_results['RotatingARA'].append(evaluate(ssn_data, preds['RotatingARA'], pred_years))

        # Baseline: Script 199 Hybrid
        phase = calibrate_superposition(train, HybridNormalModeModel,
                                        ARA_ENG_9, ARA_CON_9, P_SUBS)
        m = HybridNormalModeModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
        m.init_from_observation(start_log)
        p = m.predict_sequence(len(pred_years))
        preds['Hybrid199'] = {y: max(10**p[i], 0) for i, y in enumerate(pred_years)}
        all_results['Hybrid199'].append(evaluate(ssn_data, preds['Hybrid199'], pred_years))

        # Sine
        preds['Sine'] = sine_predict(train, pred_years, ssn_data)
        all_results['Sine'].append(evaluate(ssn_data, preds['Sine'], pred_years))

        n = len(pred_years)
        print(f"\n  Train <={split_year}, Predict {split_year+1}-2025 ({n} years)")
        print(f"  {'Model':<16s} {'Corr':>8s} {'Dir%':>8s} {'x2%':>8s} {'MAE':>8s}")
        print(f"  {'-'*14} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
        for name in model_names:
            ev = all_results[name][-1]
            print(f"  {name:<16s} {ev['corr']:+8.3f} {ev['dir']:8.1f} {ev['x2']:8.1f} {ev['mae']:8.1f}")

        # Year-by-year (first 12)
        print(f"\n  Year-by-year (first 12):")
        hdr = f"    {'Year':>6s} {'Actual':>8s}"
        for name in model_names:
            hdr += f" {name[:8]:>8s}"
        print(hdr)
        for y in pred_years[:12]:
            row = f"    {y:>6d} {ssn_data[y]:8.1f}"
            for name in model_names:
                row += f" {preds[name][y]:8.1f}"
            print(row)

    # ═══════════════════════════════════════════════════════════
    # OVERALL COMPARISON
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("OVERALL COMPARISON")
    print("=" * 80)

    sine_mae = np.mean([r['mae'] for r in all_results['Sine']])

    print(f"\n  {'Model':<16s} {'Avg Corr':>10s} {'Avg MAE':>10s} {'Avg Dir':>10s} {'Gap':>8s} {'Beats':>8s}")
    print(f"  {'-'*14} {'-'*10} {'-'*10} {'-'*10} {'-'*8} {'-'*8}")

    for name in model_names:
        res = all_results[name]
        ac = np.mean([r['corr'] for r in res])
        am = np.mean([r['mae'] for r in res])
        ad = np.mean([r['dir'] for r in res])
        gap = am - sine_mae
        pct = gap / sine_mae * 100
        beats = sum(1 for r, s in zip(res, all_results['Sine']) if r['mae'] < s['mae'])
        gap_str = f"{pct:+.0f}%" if name != 'Sine' else "---"
        print(f"  {name:<16s} {ac:+10.3f} {am:10.1f} {ad:10.1f}% {gap_str:>8s} {beats}/5")

    # Per-split breakdown
    print()
    print("  Per-split MAE:")
    hdr = f"    {'Split':>6s}"
    for name in model_names:
        hdr += f" {name[:10]:>10s}"
    hdr += f" {'Best':>10s}"
    print(hdr)
    for i, sy in enumerate(splits):
        vals = {name: all_results[name][i]['mae'] for name in model_names}
        best_name = min(vals, key=vals.get)
        row = f"    {sy:>6d}"
        for name in model_names:
            row += f" {vals[name]:10.1f}"
        row += f" {best_name:>10s}"
        print(row)

    # Energy tracking for perpendicular model
    print()
    print("=" * 80)
    print("PERPENDICULAR ENERGY DYNAMICS (2004 split example)")
    print("=" * 80)

    train = {y: v for y, v in ssn_data.items() if y <= 2004}
    pred_years = [y for y in all_ssn_years if y > 2004 and y <= 2025]
    C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
    start_log = np.log10(max(ssn_data[2004], 0.1))

    phase = calibrate_superposition(train, PerpendicularHybridModel,
                                    ARA_ENG_9, ARA_CON_9, P_SUBS)
    pm = PerpendicularHybridModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
    pm.init_from_observation(start_log)

    print(f"\n  {'Year':>6s} {'Actual':>8s} {'Pred':>8s} {'|A|':>8s} {'|B|':>8s} {'A/B':>8s}")
    for i, y in enumerate(pred_years[:21]):
        obs = pm.observable_ssn(i + 1)
        pred_val = max(10**obs, 0)
        sum_A = np.sum(np.abs(pm.A))
        sum_B = np.sum(np.abs(pm.B))
        ratio = sum_A / max(sum_B, 1e-10)
        print(f"  {y:>6d} {ssn_data[y]:8.1f} {pred_val:8.1f} {sum_A:8.4f} {sum_B:8.4f} {ratio:8.2f}")

    print()
    print("=" * 80)
    print("Script 200 complete.")
    print("=" * 80)
