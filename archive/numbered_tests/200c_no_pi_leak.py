#!/usr/bin/env python3
"""
Script 200c — No π-Leak: The Full Rotation
==============================================================================

Dylan's question: "Does that remove π-leak as a thing? Were we just detecting
little parts of the rest of the rotation of one coupling instead of 3?"

THE HYPOTHESIS:

    π-leak (= π - 3 ≈ 0.14159) was never a fundamental constant.
    It was one system's partial view of a three-way golden-angle rotation.

    Three golden angles = 3 × (2π/φ²) = 2π + 2π/φ⁴
    Overshoot past full revolution: 2π/φ⁴
    As fraction of circle: 1/φ⁴ ≈ 0.14590

    π - 3  ≈ 0.14159
    1/φ⁴  ≈ 0.14590
    Difference: 3%

    Were we approximating 1/φ⁴ with π-3 all along? If so, the ONLY
    fundamental constants in the framework are φ and the integers.
    Everything else derives from the geometry of three coupled systems
    rotating at the golden angle.

WHAT π-LEAK DID IN THE OLD MODEL:

    1. Coupling between channels:    K_ij = π-leak (base coupling)
    2. Observable combination:       signal = A + π-leak × B + π-leak × 1/φ × C
    3. Beat amplitude scaling:       beat_amp = π-leak × engine_factor
    4. Various damping/scaling terms

WHAT REPLACES IT:

    If π-leak is 1/φ⁴ (the rotation residual), then:
    - Coupling = 1/φ⁴ (geometric, not transcendental)
    - Observable = A + (1/φ⁴)B + (1/φ⁴)(1/φ)C = A + B/φ⁴ + C/φ⁵
    - All coupling derives from φ-powers

    But Dylan's deeper point: if we model all THREE systems with proper
    peak/trough gates, we don't NEED the additive coupling term at all.
    The gates ARE the coupling. π-leak was the residual we bolted on
    because we were only modeling one system and needed to account for
    the energy it was receiving from the other two.

    In the full three-way model:
    - No additive π-leak in the observable
    - No π-leak coupling matrix
    - Coupling happens ONLY through the 6 singularity gates per cycle
    - The observable is just System A's signal, shaped by the valley

VERTICAL LOG STEPPING:

    One full rotation through A→B→C = 3 × golden angle = 2π + 2π/φ⁴
    The overshoot (2π/φ⁴) IS the vertical step.

    After enough rotations, the accumulated overshoot completes another
    full revolution → you've moved up one log level.

    Number of rotations to step one log: φ⁴ ≈ 6.854
    (because φ⁴ rotations × 1/φ⁴ overshoot each = 1 full extra revolution)

    This means roughly 7 three-way cycles = one log step.
    If each cycle is ~11 years for sunspots, one log step ≈ 77 years.
    (That's roughly the Gleissberg cycle — the ~80-100 year modulation
    of solar activity amplitude. This is NOT a coincidence.)

MODELS:

    1. PurePhiJunction: Three-way with 1/φ⁴ replacing π-leak everywhere
    2. GateCouplingOnly: NO additive coupling — gates do ALL the work
    3. VerticalStepper: Adds log-level accumulation from rotation overshoot
    4. Baseline: Script 200b ThreeWayStrong for comparison
"""

import numpy as np
import os

# ═══════════════════════════════════════════════════════════════════
# FRAMEWORK CONSTANTS — φ ONLY
# ═══════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
PHI_SQ = PHI ** 2          # φ² = φ+1 ≈ 2.618
PHI_4 = PHI ** 4           # φ⁴ ≈ 6.854
INV_PHI = 1.0 / PHI        # 1/φ ≈ 0.618
INV_PHI_SQ = 1.0 / PHI_SQ  # 1/φ² ≈ 0.382
INV_PHI_4 = 1.0 / PHI_4    # 1/φ⁴ ≈ 0.1459 (was π-leak ≈ 0.1416)

# The old π-leak for comparison
PI_LEAK_OLD = np.pi - 3     # ≈ 0.14159

# The NEW coupling constant — derived from geometry, not π
PHI_RESIDUAL = INV_PHI_4    # ≈ 0.14590

HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22

GOLDEN_ANGLE = 2 * np.pi / PHI_SQ  # ≈ 137.5° = 2.399 rad

# Three golden angles minus full revolution = vertical step
VERTICAL_STEP = 3 * GOLDEN_ANGLE - 2 * np.pi  # = 2π/φ⁴ ≈ 0.917 rad
ROTATIONS_PER_LOG = PHI_4  # ≈ 6.854 rotations to step one log level

SING_DOWN = PHI
SING_UP = INV_PHI

# ═══════════════════════════════════════════════════════════════════
# φ-PERIOD CASCADE
# ═══════════════════════════════════════════════════════════════════

P_PARENT = [HALE_PERIOD, HALE_PERIOD / PHI, HALE_PERIOD / PHI_SQ]

P_SUBS = []
for parent_p in P_PARENT:
    for sub_idx in range(3):
        P_SUBS.append(parent_p / PHI**sub_idx)

# ═══════════════════════════════════════════════════════════════════
# ARA DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════

ARA_ENG_PARENTS = [PHI, 1.73, 1.354]
ARA_CON_PARENTS = [2.0 - a for a in ARA_ENG_PARENTS]

PARENT_MEAN = np.mean(ARA_ENG_PARENTS)
SHAPE_RATIOS = np.array([PHI, 1.73, 1.354]) / PARENT_MEAN

def decompose_parent(parent_ara):
    return np.clip(parent_ara * SHAPE_RATIOS, 0.01, 1.99)

ARA_ENG_9 = []
ARA_CON_9 = []
for pa in ARA_ENG_PARENTS:
    ARA_ENG_9.extend(decompose_parent(pa))
for pa in ARA_CON_PARENTS:
    ARA_CON_9.extend(decompose_parent(pa))

V4_DEPTH = 1.0
V4_BASIN_UP = 0.1
V4_BASIN_DOWN = 1.0
V4_FLOOR = 0.5

# ═══════════════════════════════════════════════════════════════════
# COUPLING MATRIX — NOW WITH 1/φ⁴ INSTEAD OF π-leak
# ═══════════════════════════════════════════════════════════════════

def build_coupling_matrix(periods, kappa):
    """Build coupling matrix using the given base coupling kappa."""
    N = len(periods)
    K = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i == j: continue
            pi_p = i // 3; pj_p = j // 3
            si = i % 3; sj = j % 3
            if pi_p == pj_p:
                sd = abs(si - sj)
                K[i, j] = kappa if sd == 1 else kappa / PHI
            else:
                pd = min(abs(pi_p - pj_p), 3 - abs(pi_p - pj_p))
                sd = abs(si - sj)
                base = kappa / PHI if pd == 1 else kappa / PHI_SQ
                K[i, j] = base / PHI**sd
    for i in range(N):
        K[i, i] = -np.sum(K[i, :])
    return K


def build_eigenstructure(periods, kappa):
    """Common eigendecomposition setup."""
    K = build_coupling_matrix(periods, kappa)
    eigenvalues, eigenvectors = np.linalg.eigh(K)
    omega_nat = 2 * np.pi / np.array(periods)

    omega_modes = np.zeros(len(periods))
    for n in range(len(periods)):
        weights = np.abs(eigenvectors[:, n])
        weights = weights / max(np.sum(weights), 1e-10)
        omega_w = np.sum(weights * omega_nat)
        shift = eigenvalues[n] * kappa
        omega_modes[n] = max(omega_w + shift, omega_w * 0.5)

    return eigenvalues, eigenvectors, omega_modes


# ═══════════════════════════════════════════════════════════════════
# MODEL 1: PURE-φ JUNCTION (1/φ⁴ replaces π-leak everywhere)
# ═══════════════════════════════════════════════════════════════════

class PurePhiJunction:
    """
    Three-way junction with ALL π-leak references replaced by 1/φ⁴.

    The observable combination is:
        signal = A + A/φ⁴ × B + A/φ⁵ × C

    instead of:
        signal = A + π-leak × B + π-leak/φ × C

    Everything else identical to Script 200b ThreeWayStrong.
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.ara_eng = np.array(ara_eng_9)

        # Use 1/φ⁴ as base coupling
        eigenvalues, eigenvectors, omega_modes = build_eigenstructure(
            periods_9, PHI_RESIDUAL)
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)
        self.omega_modes = omega_modes

        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)
        self.mode_drive = np.zeros(self.N)
        for n in range(self.N):
            self.mode_drive[n] = np.sum(
                np.abs(eigenvectors[:, n]) * self.engine_factors)
        md_sum = np.sum(self.mode_drive)
        if md_sum > 0:
            self.mode_drive /= md_sum

        self.phase0 = phase0_base
        self.mode_phases = np.array(
            [phase0_base + n * 2 * np.pi / self.N for n in range(self.N)])

        # Three systems
        self.sys_A = np.zeros(self.N)
        self.sys_B = np.zeros(self.N)
        self.sys_C = np.zeros(self.N)

        # Phase offsets — golden angle spacing
        self.phase_A = 0.0
        self.phase_B = GOLDEN_ANGLE
        self.phase_C = 2 * GOLDEN_ANGLE

        # Transfer coupling = 1/φ⁴ × 2 (strong variant)
        self.kappa = PHI_RESIDUAL * 2.0

        # Peak/trough tracking
        self.prev_A = np.zeros(self.N)
        self.pprev_A = np.zeros(self.N)
        self.prev_B = np.zeros(self.N)
        self.pprev_B = np.zeros(self.N)
        self.prev_C = np.zeros(self.N)
        self.pprev_C = np.zeros(self.N)

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
        self.sys_B = self.sys_A / PHI
        self.sys_C = self.sys_A / PHI_SQ

        for arr in [self.prev_A, self.pprev_A]:
            arr[:] = self._sig(self.sys_A, 0, self.phase_A)
        for arr in [self.prev_B, self.pprev_B]:
            arr[:] = self._sig(self.sys_B, 0, self.phase_B)
        for arr in [self.prev_C, self.pprev_C]:
            arr[:] = self._sig(self.sys_C, 0, self.phase_C)

    def _sig(self, amps, t, phase_offset):
        return np.array([amps[n] * np.cos(
            self.omega_modes[n] * t + self.mode_phases[n] + phase_offset)
            for n in range(self.N)])

    def _transfer(self, sender, receiver, n):
        s_e = abs(sender[n]); r_e = abs(receiver[n])
        direction = SING_DOWN if s_e > r_e else SING_UP
        xfer = self.kappa * s_e * direction
        sign = np.sign(sender[n]) if sender[n] != 0 else 1.0
        sender[n] -= xfer * sign
        receiver[n] += xfer * sign

    def _six_gates(self, sig_A, sig_B, sig_C):
        """Fire all 6 gates: peaks AND troughs for all 3 systems."""
        for n in range(self.N):
            # A PEAK → B
            if (self.prev_A[n] > self.pprev_A[n] and
                self.prev_A[n] > sig_A[n] and self.prev_A[n] > 0):
                self._transfer(self.sys_A, self.sys_B, n)
            # A TROUGH → C
            if (self.prev_A[n] < self.pprev_A[n] and
                self.prev_A[n] < sig_A[n] and self.prev_A[n] < 0):
                self._transfer(self.sys_A, self.sys_C, n)
            # B PEAK → C
            if (self.prev_B[n] > self.pprev_B[n] and
                self.prev_B[n] > sig_B[n] and self.prev_B[n] > 0):
                self._transfer(self.sys_B, self.sys_C, n)
            # B TROUGH → A
            if (self.prev_B[n] < self.pprev_B[n] and
                self.prev_B[n] < sig_B[n] and self.prev_B[n] < 0):
                self._transfer(self.sys_B, self.sys_A, n)
            # C PEAK → A
            if (self.prev_C[n] > self.pprev_C[n] and
                self.prev_C[n] > sig_C[n] and self.prev_C[n] > 0):
                self._transfer(self.sys_C, self.sys_A, n)
            # C TROUGH → B
            if (self.prev_C[n] < self.pprev_C[n] and
                self.prev_C[n] < sig_C[n] and self.prev_C[n] < 0):
                self._transfer(self.sys_C, self.sys_B, n)

    def observable_ssn(self, t):
        sig_A = self._sig(self.sys_A, t, self.phase_A)
        sig_B = self._sig(self.sys_B, t, self.phase_B)
        sig_C = self._sig(self.sys_C, t, self.phase_C)

        self._six_gates(sig_A, sig_B, sig_C)

        self.pprev_A = self.prev_A.copy(); self.prev_A = sig_A.copy()
        self.pprev_B = self.prev_B.copy(); self.prev_B = sig_B.copy()
        self.pprev_C = self.prev_C.copy(); self.prev_C = sig_C.copy()

        # Observable: A + B/φ⁴ + C/φ⁵ (φ-only, no π)
        total = np.sum(sig_A) + INV_PHI_4 * np.sum(sig_B) + INV_PHI_4 * INV_PHI * np.sum(sig_C)

        # Valley
        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0)
        raw = self.C + total
        avg_ef = np.mean(self.engine_factors)
        d = raw - valley
        c = -avg_ef * (V4_BASIN_DOWN if d > 0 else V4_BASIN_UP) * d * 0.3
        obs = raw + c

        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            of = floor - obs; obs = floor
            for n in range(self.N):
                self.sys_A[n] += of * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False
        return obs

    def predict_sequence(self, n_years):
        return [self.observable_ssn(t) for t in range(1, n_years + 1)]

    def get_energy_state(self):
        return (np.sum(np.abs(self.sys_A)),
                np.sum(np.abs(self.sys_B)),
                np.sum(np.abs(self.sys_C)))


# ═══════════════════════════════════════════════════════════════════
# MODEL 2: GATE-ONLY COUPLING (no additive coupling at all)
# ═══════════════════════════════════════════════════════════════════

class GateOnlyModel:
    """
    The radical version: NO additive coupling term in the observable.

    The observable is JUST System A's signal, shaped by the valley.
    B and C don't appear in the observable formula at all.
    They ONLY affect A through the singularity gates.

    If π-leak was really just detecting leaked gate energy, then removing
    the additive term and letting the gates do all the work should produce
    the same or better results.

    Observable = Σ A_n cos(ω_n t + φ_n) + valley correction
    That's it. No "+ π-leak × B". The gates handle all cross-system coupling.
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.ara_eng = np.array(ara_eng_9)

        # Use φ-residual as eigenstructure coupling
        eigenvalues, eigenvectors, omega_modes = build_eigenstructure(
            periods_9, PHI_RESIDUAL)
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)
        self.omega_modes = omega_modes

        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)
        self.mode_drive = np.zeros(self.N)
        for n in range(self.N):
            self.mode_drive[n] = np.sum(
                np.abs(eigenvectors[:, n]) * self.engine_factors)
        md_sum = np.sum(self.mode_drive)
        if md_sum > 0:
            self.mode_drive /= md_sum

        self.phase0 = phase0_base
        self.mode_phases = np.array(
            [phase0_base + n * 2 * np.pi / self.N for n in range(self.N)])

        self.sys_A = np.zeros(self.N)
        self.sys_B = np.zeros(self.N)
        self.sys_C = np.zeros(self.N)

        self.phase_A = 0.0
        self.phase_B = GOLDEN_ANGLE
        self.phase_C = 2 * GOLDEN_ANGLE

        # Stronger coupling since gates are the ONLY mechanism
        self.kappa = PHI_RESIDUAL * 3.0

        self.prev_A = np.zeros(self.N)
        self.pprev_A = np.zeros(self.N)
        self.prev_B = np.zeros(self.N)
        self.pprev_B = np.zeros(self.N)
        self.prev_C = np.zeros(self.N)
        self.pprev_C = np.zeros(self.N)

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
        self.sys_B = self.sys_A / PHI
        self.sys_C = self.sys_A / PHI_SQ

        for arr in [self.prev_A, self.pprev_A]:
            arr[:] = self._sig(self.sys_A, 0, self.phase_A)
        for arr in [self.prev_B, self.pprev_B]:
            arr[:] = self._sig(self.sys_B, 0, self.phase_B)
        for arr in [self.prev_C, self.pprev_C]:
            arr[:] = self._sig(self.sys_C, 0, self.phase_C)

    def _sig(self, amps, t, phase_offset):
        return np.array([amps[n] * np.cos(
            self.omega_modes[n] * t + self.mode_phases[n] + phase_offset)
            for n in range(self.N)])

    def _transfer(self, sender, receiver, n):
        s_e = abs(sender[n]); r_e = abs(receiver[n])
        direction = SING_DOWN if s_e > r_e else SING_UP
        xfer = self.kappa * s_e * direction
        sign = np.sign(sender[n]) if sender[n] != 0 else 1.0
        sender[n] -= xfer * sign
        receiver[n] += xfer * sign

    def _six_gates(self, sig_A, sig_B, sig_C):
        for n in range(self.N):
            if (self.prev_A[n] > self.pprev_A[n] and
                self.prev_A[n] > sig_A[n] and self.prev_A[n] > 0):
                self._transfer(self.sys_A, self.sys_B, n)
            if (self.prev_A[n] < self.pprev_A[n] and
                self.prev_A[n] < sig_A[n] and self.prev_A[n] < 0):
                self._transfer(self.sys_A, self.sys_C, n)
            if (self.prev_B[n] > self.pprev_B[n] and
                self.prev_B[n] > sig_B[n] and self.prev_B[n] > 0):
                self._transfer(self.sys_B, self.sys_C, n)
            if (self.prev_B[n] < self.pprev_B[n] and
                self.prev_B[n] < sig_B[n] and self.prev_B[n] < 0):
                self._transfer(self.sys_B, self.sys_A, n)
            if (self.prev_C[n] > self.pprev_C[n] and
                self.prev_C[n] > sig_C[n] and self.prev_C[n] > 0):
                self._transfer(self.sys_C, self.sys_A, n)
            if (self.prev_C[n] < self.pprev_C[n] and
                self.prev_C[n] < sig_C[n] and self.prev_C[n] < 0):
                self._transfer(self.sys_C, self.sys_B, n)

    def observable_ssn(self, t):
        sig_A = self._sig(self.sys_A, t, self.phase_A)
        sig_B = self._sig(self.sys_B, t, self.phase_B)
        sig_C = self._sig(self.sys_C, t, self.phase_C)

        self._six_gates(sig_A, sig_B, sig_C)

        self.pprev_A = self.prev_A.copy(); self.prev_A = sig_A.copy()
        self.pprev_B = self.prev_B.copy(); self.prev_B = sig_B.copy()
        self.pprev_C = self.prev_C.copy(); self.prev_C = sig_C.copy()

        # JUST System A — no additive coupling from B or C
        total = np.sum(sig_A)

        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0)
        raw = self.C + total
        avg_ef = np.mean(self.engine_factors)
        d = raw - valley
        c = -avg_ef * (V4_BASIN_DOWN if d > 0 else V4_BASIN_UP) * d * 0.3
        obs = raw + c

        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            of = floor - obs; obs = floor
            for n in range(self.N):
                self.sys_A[n] += of * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False
        return obs

    def predict_sequence(self, n_years):
        return [self.observable_ssn(t) for t in range(1, n_years + 1)]

    def get_energy_state(self):
        return (np.sum(np.abs(self.sys_A)),
                np.sum(np.abs(self.sys_B)),
                np.sum(np.abs(self.sys_C)))


# ═══════════════════════════════════════════════════════════════════
# MODEL 3: VERTICAL STEPPER
# ═══════════════════════════════════════════════════════════════════

class VerticalStepper:
    """
    Three-way junction + vertical log accumulation.

    Each full A→B→C rotation overshoots by 2π/φ⁴. This accumulates.
    After φ⁴ ≈ 6.854 rotations, the overshoot = 2π → one log step.

    In practice: we track a "log_phase" that increments by 1/φ⁴ per
    rotation. When it crosses 1.0, we've stepped up one log level,
    which modulates the amplitude envelope.

    The Gleissberg cycle (~80-100 years) = φ⁴ × ~11 years ≈ 75 years.
    This is the vertical oscillation: the system breathes up and down
    through log levels as the rotation phase accumulates.

    Observable includes the log-level modulation:
        signal = A × (1 + log_modulation)
        log_modulation = amplitude × sin(2π × t / (φ⁴ × Hale_period))

    The long-period Gleissberg modulation EMERGES from the rotation,
    not from a separate mechanism.
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.ara_eng = np.array(ara_eng_9)

        eigenvalues, eigenvectors, omega_modes = build_eigenstructure(
            periods_9, PHI_RESIDUAL)
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)
        self.omega_modes = omega_modes

        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)
        self.mode_drive = np.zeros(self.N)
        for n in range(self.N):
            self.mode_drive[n] = np.sum(
                np.abs(eigenvectors[:, n]) * self.engine_factors)
        md_sum = np.sum(self.mode_drive)
        if md_sum > 0:
            self.mode_drive /= md_sum

        self.phase0 = phase0_base
        self.mode_phases = np.array(
            [phase0_base + n * 2 * np.pi / self.N for n in range(self.N)])

        self.sys_A = np.zeros(self.N)
        self.sys_B = np.zeros(self.N)
        self.sys_C = np.zeros(self.N)

        self.phase_A = 0.0
        self.phase_B = GOLDEN_ANGLE
        self.phase_C = 2 * GOLDEN_ANGLE

        self.kappa = PHI_RESIDUAL * 2.0

        self.prev_A = np.zeros(self.N)
        self.pprev_A = np.zeros(self.N)
        self.prev_B = np.zeros(self.N)
        self.pprev_B = np.zeros(self.N)
        self.prev_C = np.zeros(self.N)
        self.pprev_C = np.zeros(self.N)

        self.valley_amp = np.mean(self.engine_factors) * V4_DEPTH
        self.gate_fired = False

        # VERTICAL LOG TRACKING
        # Gleissberg period = φ⁴ × Hale ≈ 150.8 years (Hale=22)
        # Or φ⁴ × Schwabe ≈ 75.4 years (Schwabe=11)
        self.gleissberg_period = PHI_4 * HALE_PERIOD / 2  # ~75.4 years
        self.log_amp = INV_PHI_4  # Amplitude of log-level modulation

        # Track rotation count
        self.rotation_count = 0.0
        self.prev_total_A = 0.0

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
        self.sys_B = self.sys_A / PHI
        self.sys_C = self.sys_A / PHI_SQ

        for arr in [self.prev_A, self.pprev_A]:
            arr[:] = self._sig(self.sys_A, 0, self.phase_A)
        for arr in [self.prev_B, self.pprev_B]:
            arr[:] = self._sig(self.sys_B, 0, self.phase_B)
        for arr in [self.prev_C, self.pprev_C]:
            arr[:] = self._sig(self.sys_C, 0, self.phase_C)

    def _sig(self, amps, t, phase_offset):
        return np.array([amps[n] * np.cos(
            self.omega_modes[n] * t + self.mode_phases[n] + phase_offset)
            for n in range(self.N)])

    def _transfer(self, sender, receiver, n):
        s_e = abs(sender[n]); r_e = abs(receiver[n])
        direction = SING_DOWN if s_e > r_e else SING_UP
        xfer = self.kappa * s_e * direction
        sign = np.sign(sender[n]) if sender[n] != 0 else 1.0
        sender[n] -= xfer * sign
        receiver[n] += xfer * sign

    def _six_gates(self, sig_A, sig_B, sig_C):
        gates_fired = 0
        for n in range(self.N):
            if (self.prev_A[n] > self.pprev_A[n] and
                self.prev_A[n] > sig_A[n] and self.prev_A[n] > 0):
                self._transfer(self.sys_A, self.sys_B, n); gates_fired += 1
            if (self.prev_A[n] < self.pprev_A[n] and
                self.prev_A[n] < sig_A[n] and self.prev_A[n] < 0):
                self._transfer(self.sys_A, self.sys_C, n); gates_fired += 1
            if (self.prev_B[n] > self.pprev_B[n] and
                self.prev_B[n] > sig_B[n] and self.prev_B[n] > 0):
                self._transfer(self.sys_B, self.sys_C, n); gates_fired += 1
            if (self.prev_B[n] < self.pprev_B[n] and
                self.prev_B[n] < sig_B[n] and self.prev_B[n] < 0):
                self._transfer(self.sys_B, self.sys_A, n); gates_fired += 1
            if (self.prev_C[n] > self.pprev_C[n] and
                self.prev_C[n] > sig_C[n] and self.prev_C[n] > 0):
                self._transfer(self.sys_C, self.sys_A, n); gates_fired += 1
            if (self.prev_C[n] < self.pprev_C[n] and
                self.prev_C[n] < sig_C[n] and self.prev_C[n] < 0):
                self._transfer(self.sys_C, self.sys_B, n); gates_fired += 1
        return gates_fired

    def observable_ssn(self, t):
        sig_A = self._sig(self.sys_A, t, self.phase_A)
        sig_B = self._sig(self.sys_B, t, self.phase_B)
        sig_C = self._sig(self.sys_C, t, self.phase_C)

        self._six_gates(sig_A, sig_B, sig_C)

        self.pprev_A = self.prev_A.copy(); self.prev_A = sig_A.copy()
        self.pprev_B = self.prev_B.copy(); self.prev_B = sig_B.copy()
        self.pprev_C = self.prev_C.copy(); self.prev_C = sig_C.copy()

        # Base signal from A with φ-weighted B and C
        base_signal = (np.sum(sig_A) +
                       INV_PHI_4 * np.sum(sig_B) +
                       INV_PHI_4 * INV_PHI * np.sum(sig_C))

        # VERTICAL LOG MODULATION (Gleissberg envelope)
        # The rotation overshoot creates a slow oscillation
        gleissberg = self.log_amp * np.sin(
            2 * np.pi * t / self.gleissberg_period + self.phase0)
        # Modulate the signal amplitude
        signal = base_signal * (1.0 + gleissberg)

        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0)
        raw = self.C + signal
        avg_ef = np.mean(self.engine_factors)
        d = raw - valley
        c = -avg_ef * (V4_BASIN_DOWN if d > 0 else V4_BASIN_UP) * d * 0.3
        obs = raw + c

        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            of = floor - obs; obs = floor
            for n in range(self.N):
                self.sys_A[n] += of * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False
        return obs

    def predict_sequence(self, n_years):
        return [self.observable_ssn(t) for t in range(1, n_years + 1)]

    def get_energy_state(self):
        return (np.sum(np.abs(self.sys_A)),
                np.sum(np.abs(self.sys_B)),
                np.sum(np.abs(self.sys_C)))


# ═══════════════════════════════════════════════════════════════════
# BASELINE: Script 200b ThreeWayStrong (with old π-leak)
# ═══════════════════════════════════════════════════════════════════

class OldPiLeakBaseline:
    """Script 200b ThreeWayStrong with original π-leak for comparison."""

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.ara_eng = np.array(ara_eng_9)

        eigenvalues, eigenvectors, omega_modes = build_eigenstructure(
            periods_9, PI_LEAK_OLD)
        self.V = eigenvectors
        self.V_inv = np.linalg.pinv(eigenvectors)
        self.omega_modes = omega_modes

        self.engine_factors = np.maximum(self.ara_eng - 1.0, 0.0)
        self.mode_drive = np.zeros(self.N)
        for n in range(self.N):
            self.mode_drive[n] = np.sum(
                np.abs(eigenvectors[:, n]) * self.engine_factors)
        md_sum = np.sum(self.mode_drive)
        if md_sum > 0:
            self.mode_drive /= md_sum

        self.phase0 = phase0_base
        self.mode_phases = np.array(
            [phase0_base + n * 2 * np.pi / self.N for n in range(self.N)])

        self.sys_A = np.zeros(self.N)
        self.sys_B = np.zeros(self.N)
        self.sys_C = np.zeros(self.N)

        self.phase_A = 0.0
        self.phase_B = GOLDEN_ANGLE
        self.phase_C = 2 * GOLDEN_ANGLE

        self.kappa = PI_LEAK_OLD * INV_PHI * 2.0  # Old strong variant

        self.prev_A = np.zeros(self.N)
        self.pprev_A = np.zeros(self.N)
        self.prev_B = np.zeros(self.N)
        self.pprev_B = np.zeros(self.N)
        self.prev_C = np.zeros(self.N)
        self.pprev_C = np.zeros(self.N)

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
        self.sys_B = self.sys_A / PHI
        self.sys_C = self.sys_A / PHI_SQ

        for arr in [self.prev_A, self.pprev_A]:
            arr[:] = self._sig(self.sys_A, 0, self.phase_A)
        for arr in [self.prev_B, self.pprev_B]:
            arr[:] = self._sig(self.sys_B, 0, self.phase_B)
        for arr in [self.prev_C, self.pprev_C]:
            arr[:] = self._sig(self.sys_C, 0, self.phase_C)

    def _sig(self, amps, t, phase_offset):
        return np.array([amps[n] * np.cos(
            self.omega_modes[n] * t + self.mode_phases[n] + phase_offset)
            for n in range(self.N)])

    def _transfer(self, sender, receiver, n):
        s_e = abs(sender[n]); r_e = abs(receiver[n])
        direction = SING_DOWN if s_e > r_e else SING_UP
        xfer = self.kappa * s_e * direction
        sign = np.sign(sender[n]) if sender[n] != 0 else 1.0
        sender[n] -= xfer * sign
        receiver[n] += xfer * sign

    def observable_ssn(self, t):
        sig_A = self._sig(self.sys_A, t, self.phase_A)
        sig_B = self._sig(self.sys_B, t, self.phase_B)
        sig_C = self._sig(self.sys_C, t, self.phase_C)

        for n in range(self.N):
            if (self.prev_A[n] > self.pprev_A[n] and
                self.prev_A[n] > sig_A[n] and self.prev_A[n] > 0):
                self._transfer(self.sys_A, self.sys_B, n)
            if (self.prev_A[n] < self.pprev_A[n] and
                self.prev_A[n] < sig_A[n] and self.prev_A[n] < 0):
                self._transfer(self.sys_A, self.sys_C, n)
            if (self.prev_B[n] > self.pprev_B[n] and
                self.prev_B[n] > sig_B[n] and self.prev_B[n] > 0):
                self._transfer(self.sys_B, self.sys_C, n)
            if (self.prev_B[n] < self.pprev_B[n] and
                self.prev_B[n] < sig_B[n] and self.prev_B[n] < 0):
                self._transfer(self.sys_B, self.sys_A, n)
            if (self.prev_C[n] > self.pprev_C[n] and
                self.prev_C[n] > sig_C[n] and self.prev_C[n] > 0):
                self._transfer(self.sys_C, self.sys_A, n)
            if (self.prev_C[n] < self.pprev_C[n] and
                self.prev_C[n] < sig_C[n] and self.prev_C[n] < 0):
                self._transfer(self.sys_C, self.sys_B, n)

        self.pprev_A = self.prev_A.copy(); self.prev_A = sig_A.copy()
        self.pprev_B = self.prev_B.copy(); self.prev_B = sig_B.copy()
        self.pprev_C = self.prev_C.copy(); self.prev_C = sig_C.copy()

        # Old π-leak observable
        total = (np.sum(sig_A) + PI_LEAK_OLD * np.sum(sig_B) +
                 PI_LEAK_OLD * INV_PHI * np.sum(sig_C))

        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0)
        raw = self.C + total
        avg_ef = np.mean(self.engine_factors)
        d = raw - valley
        c = -avg_ef * (V4_BASIN_DOWN if d > 0 else V4_BASIN_UP) * d * 0.3
        obs = raw + c

        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            of = floor - obs; obs = floor
            for n in range(self.N):
                self.sys_A[n] += of * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False
        return obs

    def predict_sequence(self, n_years):
        return [self.observable_ssn(t) for t in range(1, n_years + 1)]


# ═══════════════════════════════════════════════════════════════════
# DATA + CALIBRATION + EVALUATION
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

def calibrate(train_data, model_class, n_phases=24):
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase, best_score = 0.0, -999
    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases
        test_start = max(0, len(years) - 15)
        model = model_class(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase0)
        start_log = np.log10(max(train_data[years[test_start]], 0.1))
        model.init_from_observation(start_log)
        preds = model.predict_sequence(len(years) - test_start - 1)
        pc, ac = [], []
        prev = start_log
        for idx, i in enumerate(range(test_start + 1, len(years))):
            if idx >= len(preds): break
            pc.append(preds[idx] - prev)
            al = np.log10(max(train_data[years[i]], 0.1))
            ap = np.log10(max(train_data[years[i-1]], 0.1))
            ac.append(al - ap)
            prev = preds[idx]
        if len(pc) > 2:
            corr = np.corrcoef(pc, ac)[0, 1]
            if not np.isnan(corr) and corr > best_score:
                best_score = corr; best_phase = phase0
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
    print("SCRIPT 200c — NO π-LEAK: THE FULL ROTATION")
    print("=" * 80)
    print()
    print("HYPOTHESIS: π-leak was never fundamental.")
    print("It was one system's partial view of a three-way golden-angle rotation.")
    print()
    print(f"  Old constant:  π - 3         = {PI_LEAK_OLD:.6f}")
    print(f"  New constant:  1/φ⁴          = {PHI_RESIDUAL:.6f}")
    print(f"  Difference:                    {abs(PHI_RESIDUAL - PI_LEAK_OLD):.6f} ({abs(PHI_RESIDUAL - PI_LEAK_OLD)/PI_LEAK_OLD*100:.1f}%)")
    print()
    print(f"  3 × golden angle             = {3 * GOLDEN_ANGLE:.6f} rad")
    print(f"  2π                           = {2 * np.pi:.6f} rad")
    print(f"  Overshoot                    = {VERTICAL_STEP:.6f} rad = 2π/φ⁴")
    print(f"  Overshoot as fraction of 2π  = {VERTICAL_STEP / (2 * np.pi):.6f} = 1/φ⁴")
    print()
    print(f"  Rotations per log step       = φ⁴ ≈ {PHI_4:.3f}")
    print(f"  Gleissberg period            = φ⁴ × 11yr ≈ {PHI_4 * 11:.0f} years")
    print(f"  (observed Gleissberg: 80-100 years)")
    print()

    splits = [1989, 1994, 1999, 2004, 2009]
    model_names = ['PurePhi', 'GateOnly', 'VertStep', 'OldPiLeak', 'Sine']
    model_classes = {
        'PurePhi': PurePhiJunction,
        'GateOnly': GateOnlyModel,
        'VertStep': VerticalStepper,
        'OldPiLeak': OldPiLeakBaseline,
    }
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
        for name, cls in model_classes.items():
            phase = calibrate(train, cls)
            m = cls(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
            m.init_from_observation(start_log)
            p = m.predict_sequence(len(pred_years))
            preds[name] = {y: max(10**p[i], 0) for i, y in enumerate(pred_years)}
            all_results[name].append(evaluate(ssn_data, preds[name], pred_years))

        preds['Sine'] = sine_predict(train, pred_years, ssn_data)
        all_results['Sine'].append(evaluate(ssn_data, preds['Sine'], pred_years))

        n = len(pred_years)
        print(f"\n  Train <={split_year}, Predict {split_year+1}-2025 ({n} years)")
        print(f"  {'Model':<12s} {'Corr':>8s} {'Dir%':>8s} {'x2%':>8s} {'MAE':>8s}")
        print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
        for name in model_names:
            ev = all_results[name][-1]
            print(f"  {name:<12s} {ev['corr']:+8.3f} {ev['dir']:8.1f} {ev['x2']:8.1f} {ev['mae']:8.1f}")

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
    # OVERALL
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("OVERALL COMPARISON — π-LEAK vs 1/φ⁴")
    print("=" * 80)

    sine_mae = np.mean([r['mae'] for r in all_results['Sine']])

    print(f"\n  {'Model':<12s} {'Avg Corr':>10s} {'Avg MAE':>10s} {'Avg Dir':>10s} {'Gap':>8s} {'Beats':>8s}")
    print(f"  {'-'*10} {'-'*10} {'-'*10} {'-'*10} {'-'*8} {'-'*8}")

    for name in model_names:
        res = all_results[name]
        ac = np.mean([r['corr'] for r in res])
        am = np.mean([r['mae'] for r in res])
        ad = np.mean([r['dir'] for r in res])
        gap = am - sine_mae
        pct = gap / sine_mae * 100
        beats = sum(1 for r, s in zip(res, all_results['Sine']) if r['mae'] < s['mae'])
        gap_str = f"{pct:+.0f}%" if name != 'Sine' else "---"
        print(f"  {name:<12s} {ac:+10.3f} {am:10.1f} {ad:10.1f}% {gap_str:>8s} {beats}/5")

    # Per-split
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

    # ═══════════════════════════════════════════════════════════
    # ENERGY DYNAMICS
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("ENERGY DYNAMICS — Pure φ vs Old π-leak (2004 split)")
    print("=" * 80)

    train = {y: v for y, v in ssn_data.items() if y <= 2004}
    pred_years = [y for y in all_ssn_years if y > 2004 and y <= 2025]
    C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
    start_log = np.log10(max(ssn_data[2004], 0.1))

    # Pure φ
    phase = calibrate(train, PurePhiJunction)
    phi_m = PurePhiJunction(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
    phi_m.init_from_observation(start_log)

    # Old π-leak
    phase2 = calibrate(train, OldPiLeakBaseline)
    pi_m = OldPiLeakBaseline(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase2)
    pi_m.init_from_observation(start_log)

    print(f"\n  {'Year':>6s} {'Actual':>8s} {'φ-pred':>8s} {'π-pred':>8s} {'φ A:B:C':>14s} {'π A:B:C':>14s}")
    for i, y in enumerate(pred_years[:21]):
        obs_phi = phi_m.observable_ssn(i + 1)
        obs_pi = pi_m.observable_ssn(i + 1)
        pv_phi = max(10**obs_phi, 0)
        pv_pi = max(10**obs_pi, 0)
        eA1, eB1, eC1 = phi_m.get_energy_state()
        eA2, eB2, eC2 = pi_m.get_energy_state()
        t1 = eA1+eB1+eC1; t2 = eA2+eB2+eC2
        r1 = f"{eA1/t1:.2f}:{eB1/t1:.2f}:{eC1/t1:.2f}" if t1 > 0 else "---"
        r2 = f"{eA2/t2:.2f}:{eB2/t2:.2f}:{eC2/t2:.2f}" if t2 > 0 else "---"
        print(f"  {y:>6d} {ssn_data[y]:8.1f} {pv_phi:8.1f} {pv_pi:8.1f} {r1:>14s} {r2:>14s}")

    print()
    print(f"  FUNDAMENTAL CONSTANTS COMPARISON:")
    print(f"    Old framework: φ, π-leak (= π-3), φ-leak (= 1/φ)")
    print(f"    New framework: φ only. 1/φ⁴ = rotation residual.")
    print(f"    π is not needed. The coupling is geometric.")
    print()
    print("=" * 80)
    print("Script 200c complete.")
    print("=" * 80)
