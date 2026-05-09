#!/usr/bin/env python3
"""
Script 200b — Three-Way Junction: Peaks AND Troughs
==============================================================================

Dylan's correction to Script 200:
    1. Transfers happen at EVERY trough too, not just peaks
    2. It's not just perpendicular — it's a 3-way junction
    3. Every extremum of every system is a singularity for one of
       the other two systems

THE THREE-WAY JUNCTION:

    System A (observed)  — sunspot activity / engine signal
    System B (coupler)   — magnetic field / coupling medium
    System C (third axis) — internal dynamo / structural reservoir

    At A's PEAK:    singularity for B → energy A→B (downhill, ×φ)
    At A's TROUGH:  singularity for C → energy A→C (downhill, ×φ)
    At B's PEAK:    singularity for C → energy B→C (downhill, ×φ)
    At B's TROUGH:  singularity for A → energy B→A (uphill, ×1/φ)
    At C's PEAK:    singularity for A → energy C→A (uphill, ×1/φ)
    At C's TROUGH:  singularity for B → energy C→B (uphill, ×1/φ)

    6 transfer events per full cycle. Energy circulates:
        Peaks:   A → B → C → A  (clockwise, downhill-amplified)
        Troughs: A → C → B → A  (counterclockwise, also downhill)

    The two circulation directions are OPPOSITE — like the two DNA
    strands running antiparallel. Net flow depends on ARA values.

    The golden angle (137.5°) spaces the three systems:
        A at 0°, B at 137.5°, C at 275° (= -85°)
    This is the SCALENE triangle — not 120° equal spacing.

ENERGY BUDGET:

    At each gate crossing, the transfer is:
        transfer = κ × |amplitude| × direction_factor

    Downhill (high→low energy): direction = φ (amplified)
    Uphill (low→high energy): direction = 1/φ (attenuated)

    Per full cycle with 6 crossings:
        Net flow A: -κφ|A|(peak) - κφ|A|(trough) + κ/φ|B|(trough) + κ/φ|C|(peak)
        This self-regulates: when A is large, it loses more. When small, it gains.
        The φ/1/φ asymmetry means the system doesn't settle to equal — it
        settles to a φ-ratio between systems.

    With MORE transfers (6 per cycle vs 3 before), the amplitude
    modulation is MUCH stronger. This should produce the cycle-to-cycle
    variation that was missing in Script 200.

VARIANTS:

    1. ThreeWayJunction: Full 3-system model with peak+trough gates
    2. ThreeWayStrong: Same but with stronger coupling (2× baseline κ)
    3. ThreeWayBalanced: Initial energy distributed across all 3 systems
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

SING_DOWN = PHI
SING_UP = PHI_LEAK

# ═══════════════════════════════════════════════════════════════════
# COUPLING MATRIX
# ═══════════════════════════════════════════════════════════════════

def build_coupling_matrix(periods, kappa=PI_LEAK):
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
                base = kappa / PHI if pd == 1 else kappa / PHI**2
                K[i, j] = base / PHI**sd
    for i in range(N):
        K[i, i] = -np.sum(K[i, :])
    return K


# ═══════════════════════════════════════════════════════════════════
# THREE-WAY JUNCTION MODEL
# ═══════════════════════════════════════════════════════════════════

class ThreeWayJunction:
    """
    Three systems coupled at a junction. Every peak AND every trough
    of each system is a singularity crossing for one of the other two.

    6 transfer events per cycle. Energy circulates in both directions.

    A's peak  → gate to B (clockwise)
    A's trough → gate to C (counterclockwise)
    B's peak  → gate to C (clockwise)
    B's trough → gate to A (counterclockwise)
    C's peak  → gate to A (clockwise)
    C's trough → gate to B (counterclockwise)

    Clockwise flow: A→B→C→A (downhill, ×φ)
    Counter-clockwise flow: A→C→B→A (uphill, ×1/φ)

    Wait — direction (downhill/uphill) depends on the RELATIVE energy
    level, not the circulation direction. The system with MORE energy
    at the crossing is the sender (downhill), the one with LESS is
    the receiver. φ amplifies the transfer when going high→low,
    1/φ attenuates when going low→high.
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base,
                 kappa_base=None):
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

        # ─── THREE SYSTEMS ───
        # Mode amplitudes for each system
        self.sys_A = np.zeros(self.N)  # Observed (sunspot activity)
        self.sys_B = np.zeros(self.N)  # Coupler (magnetic field)
        self.sys_C = np.zeros(self.N)  # Third axis (dynamo)

        # Golden angle offsets — scalene triangle
        self.ga = 2 * np.pi / (PHI ** 2)  # ≈ 137.5°
        self.phase_A = 0.0
        self.phase_B = self.ga          # 137.5°
        self.phase_C = 2 * self.ga      # 275°

        # Transfer coupling strength
        if kappa_base is None:
            self.kappa = PI_LEAK * PHI_LEAK  # ~0.088
        else:
            self.kappa = kappa_base

        # ─── PEAK/TROUGH TRACKING ───
        # Need 2 previous signals for each system to detect extrema
        self.prev_A = np.zeros(self.N)
        self.pprev_A = np.zeros(self.N)
        self.prev_B = np.zeros(self.N)
        self.pprev_B = np.zeros(self.N)
        self.prev_C = np.zeros(self.N)
        self.pprev_C = np.zeros(self.N)

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

        # B and C start with proportional energy (not zero!)
        # Three-way junction means all three carry energy from the start
        # A has the most (it's the observed engine), B and C split the rest
        # Ratio: A gets φ/(φ+1+1/φ), B gets 1/(φ+1+1/φ), C gets 1/φ/(φ+1+1/φ)
        total_budget = PHI + 1.0 + PHI_LEAK  # φ + 1 + 1/φ = √5 + 1
        self.sys_B = self.sys_A * (1.0 / total_budget) / (PHI / total_budget)
        self.sys_C = self.sys_A * (PHI_LEAK / total_budget) / (PHI / total_budget)
        self.sys_A = self.sys_A * (PHI / total_budget) / (PHI / total_budget)
        # Simplifies to: A stays as-is, B = A/φ, C = A/φ²
        # Actually let me just be explicit:
        self.sys_B = self.sys_A / PHI
        self.sys_C = self.sys_A / (PHI * PHI)

        # Initialize tracking
        for arr in [self.prev_A, self.pprev_A]:
            arr[:] = self._compute_signal(self.sys_A, 0, self.phase_A)
        for arr in [self.prev_B, self.pprev_B]:
            arr[:] = self._compute_signal(self.sys_B, 0, self.phase_B)
        for arr in [self.prev_C, self.pprev_C]:
            arr[:] = self._compute_signal(self.sys_C, 0, self.phase_C)

    def _compute_signal(self, amps, t, phase_offset):
        """Per-mode signal for a system."""
        s = np.zeros(self.N)
        for n in range(self.N):
            s[n] = amps[n] * np.cos(
                self.omega_modes[n] * t + self.mode_phases[n] + phase_offset
            )
        return s

    def _transfer(self, sender_amps, receiver_amps, sender_signal_n, n):
        """
        One-shot singularity gate transfer for mode n.

        Direction (downhill/uphill) determined by relative energy:
            Sender has more |amplitude| → downhill → ×φ
            Sender has less |amplitude| → uphill → ×1/φ
        """
        s_energy = abs(sender_amps[n])
        r_energy = abs(receiver_amps[n])

        if s_energy > r_energy:
            # Sender is higher energy → downhill → amplified by φ
            direction = SING_DOWN
        else:
            # Sender is lower energy → uphill → attenuated by 1/φ
            direction = SING_UP

        transfer_amount = self.kappa * s_energy * direction

        # Remove from sender, add to receiver
        sender_amps[n] -= transfer_amount * np.sign(sender_amps[n])
        # Receiver gets it in the sign of the sender's amplitude
        receiver_amps[n] += transfer_amount * np.sign(sender_amps[n] + 1e-20)

    def observable_ssn(self, t):
        """
        Three-way junction with 6 transfer gates per cycle.
        """
        # Compute current signals
        sig_A = self._compute_signal(self.sys_A, t, self.phase_A)
        sig_B = self._compute_signal(self.sys_B, t, self.phase_B)
        sig_C = self._compute_signal(self.sys_C, t, self.phase_C)

        # ─── SIX SINGULARITY GATES ───
        for n in range(self.N):
            # ── System A extrema ──
            # A PEAK → gate to B
            if (self.prev_A[n] > self.pprev_A[n] and
                self.prev_A[n] > sig_A[n] and self.prev_A[n] > 0):
                self._transfer(self.sys_A, self.sys_B, self.prev_A[n], n)

            # A TROUGH → gate to C
            if (self.prev_A[n] < self.pprev_A[n] and
                self.prev_A[n] < sig_A[n] and self.prev_A[n] < 0):
                self._transfer(self.sys_A, self.sys_C, self.prev_A[n], n)

            # ── System B extrema ──
            # B PEAK → gate to C
            if (self.prev_B[n] > self.pprev_B[n] and
                self.prev_B[n] > sig_B[n] and self.prev_B[n] > 0):
                self._transfer(self.sys_B, self.sys_C, self.prev_B[n], n)

            # B TROUGH → gate to A
            if (self.prev_B[n] < self.pprev_B[n] and
                self.prev_B[n] < sig_B[n] and self.prev_B[n] < 0):
                self._transfer(self.sys_B, self.sys_A, self.prev_B[n], n)

            # ── System C extrema ──
            # C PEAK → gate to A
            if (self.prev_C[n] > self.pprev_C[n] and
                self.prev_C[n] > sig_C[n] and self.prev_C[n] > 0):
                self._transfer(self.sys_C, self.sys_A, self.prev_C[n], n)

            # C TROUGH → gate to B
            if (self.prev_C[n] < self.pprev_C[n] and
                self.prev_C[n] < sig_C[n] and self.prev_C[n] < 0):
                self._transfer(self.sys_C, self.sys_B, self.prev_C[n], n)

        # Update tracking
        self.pprev_A = self.prev_A.copy()
        self.prev_A = sig_A.copy()
        self.pprev_B = self.prev_B.copy()
        self.prev_B = sig_B.copy()
        self.pprev_C = self.prev_C.copy()
        self.prev_C = sig_C.copy()

        # ─── OBSERVABLE ───
        # A is primary, B modulates at π-leak, C at π-leak × 1/φ
        total_A = np.sum(sig_A)
        total_B = np.sum(sig_B)
        total_C = np.sum(sig_C)

        signal = total_A + PI_LEAK * total_B + PI_LEAK * PHI_LEAK * total_C

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
                self.sys_A[n] += overflow * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False

        return obs

    def predict_sequence(self, n_years):
        return [self.observable_ssn(t) for t in range(1, n_years + 1)]

    def get_energy_state(self):
        """Return current energy in each system."""
        return (np.sum(np.abs(self.sys_A)),
                np.sum(np.abs(self.sys_B)),
                np.sum(np.abs(self.sys_C)))


# ═══════════════════════════════════════════════════════════════════
# VARIANT: STRONG COUPLING (2×κ)
# ═══════════════════════════════════════════════════════════════════

class ThreeWayStrong(ThreeWayJunction):
    """Same as ThreeWayJunction but with 2× coupling strength."""
    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        super().__init__(ara_eng_9, ara_con_9, periods_9, C, phase0_base,
                         kappa_base=PI_LEAK * PHI_LEAK * 2.0)


# ═══════════════════════════════════════════════════════════════════
# VARIANT: PHI-RATIO COUPLING (κ_peak = φ × κ_trough)
# ═══════════════════════════════════════════════════════════════════

class ThreeWayPhiRatio(ThreeWayJunction):
    """
    Peak transfers are φ× stronger than trough transfers.
    Not just the direction factor — the BASE coupling is asymmetric
    between peaks and troughs.

    Peak κ = base × φ
    Trough κ = base × 1 (= base)

    This means peaks drain MORE energy than troughs return,
    creating a net flow that the φ-direction factor then amplifies further.
    """
    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        super().__init__(ara_eng_9, ara_con_9, periods_9, C, phase0_base)
        self.kappa_peak = self.kappa * PHI
        self.kappa_trough = self.kappa

    def _transfer_peak(self, sender_amps, receiver_amps, n):
        """Transfer at peak — stronger coupling."""
        s_energy = abs(sender_amps[n])
        r_energy = abs(receiver_amps[n])
        direction = SING_DOWN if s_energy > r_energy else SING_UP
        transfer_amount = self.kappa_peak * s_energy * direction
        sender_amps[n] -= transfer_amount * np.sign(sender_amps[n])
        receiver_amps[n] += transfer_amount * np.sign(sender_amps[n] + 1e-20)

    def _transfer_trough(self, sender_amps, receiver_amps, n):
        """Transfer at trough — weaker coupling."""
        s_energy = abs(sender_amps[n])
        r_energy = abs(receiver_amps[n])
        direction = SING_DOWN if s_energy > r_energy else SING_UP
        transfer_amount = self.kappa_trough * s_energy * direction
        sender_amps[n] -= transfer_amount * np.sign(sender_amps[n])
        receiver_amps[n] += transfer_amount * np.sign(sender_amps[n] + 1e-20)

    def observable_ssn(self, t):
        sig_A = self._compute_signal(self.sys_A, t, self.phase_A)
        sig_B = self._compute_signal(self.sys_B, t, self.phase_B)
        sig_C = self._compute_signal(self.sys_C, t, self.phase_C)

        for n in range(self.N):
            # A PEAK → B (strong)
            if (self.prev_A[n] > self.pprev_A[n] and
                self.prev_A[n] > sig_A[n] and self.prev_A[n] > 0):
                self._transfer_peak(self.sys_A, self.sys_B, n)
            # A TROUGH → C (weak)
            if (self.prev_A[n] < self.pprev_A[n] and
                self.prev_A[n] < sig_A[n] and self.prev_A[n] < 0):
                self._transfer_trough(self.sys_A, self.sys_C, n)
            # B PEAK → C (strong)
            if (self.prev_B[n] > self.pprev_B[n] and
                self.prev_B[n] > sig_B[n] and self.prev_B[n] > 0):
                self._transfer_peak(self.sys_B, self.sys_C, n)
            # B TROUGH → A (weak)
            if (self.prev_B[n] < self.pprev_B[n] and
                self.prev_B[n] < sig_B[n] and self.prev_B[n] < 0):
                self._transfer_trough(self.sys_B, self.sys_A, n)
            # C PEAK → A (strong)
            if (self.prev_C[n] > self.pprev_C[n] and
                self.prev_C[n] > sig_C[n] and self.prev_C[n] > 0):
                self._transfer_peak(self.sys_C, self.sys_A, n)
            # C TROUGH → B (weak)
            if (self.prev_C[n] < self.pprev_C[n] and
                self.prev_C[n] < sig_C[n] and self.prev_C[n] < 0):
                self._transfer_trough(self.sys_C, self.sys_B, n)

        self.pprev_A = self.prev_A.copy(); self.prev_A = sig_A.copy()
        self.pprev_B = self.prev_B.copy(); self.prev_B = sig_B.copy()
        self.pprev_C = self.prev_C.copy(); self.prev_C = sig_C.copy()

        total_A = np.sum(sig_A)
        total_B = np.sum(sig_B)
        total_C = np.sum(sig_C)
        signal = total_A + PI_LEAK * total_B + PI_LEAK * PHI_LEAK * total_C

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
                self.sys_A[n] += overflow * SING_UP * self.mode_drive[n] * 0.1
            self.gate_fired = True
        elif obs >= floor and self.gate_fired:
            self.gate_fired = False

        return obs


# ═══════════════════════════════════════════════════════════════════
# SCRIPT 199 HYBRID (baseline)
# ═══════════════════════════════════════════════════════════════════

class HybridBaseline:
    """Script 199 Hybrid — MAE 47.9 baseline."""
    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.N = 9
        self.C = C
        self.periods = np.array(periods_9)
        self.omega_nat = 2 * np.pi / self.periods
        self.ara_eng = np.array(ara_eng_9)

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
        self.mode_amps = np.zeros(self.N)
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
        self.mode_amps = self.V_inv @ x0
        for n in range(self.N):
            self.mode_amps[n] *= (1.0 + self.mode_drive[n] * 2.0)

    def observable_ssn(self, t):
        signal = sum(self.mode_amps[n] * np.cos(
            self.omega_modes[n] * t + self.mode_phases[n]) for n in range(self.N))
        valley = self.C + self.valley_amp * np.sin(
            2 * np.pi * t / HALE_PERIOD + self.phase0)
        raw_obs = self.C + signal
        avg_ef = np.mean(self.engine_factors)
        d = raw_obs - valley
        c = -avg_ef * (V4_BASIN_DOWN if d > 0 else V4_BASIN_UP) * d * 0.3
        obs = raw_obs + c
        floor = self.C - V4_FLOOR
        if obs < floor and not self.gate_fired:
            of = floor - obs; obs = floor
            for n in range(self.N):
                self.mode_amps[n] += of * SING_UP * self.mode_drive[n] * 0.1
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

def calibrate(train_data, model_class, ara_eng, ara_con, periods, n_phases=24):
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
        preds = model.predict_sequence(len(years) - test_start - 1)
        pred_c, act_c = [], []
        prev = start_log
        for idx, i in enumerate(range(test_start + 1, len(years))):
            if idx >= len(preds): break
            pred_c.append(preds[idx] - prev)
            al = np.log10(max(train_data[years[i]], 0.1))
            ap = np.log10(max(train_data[years[i-1]], 0.1))
            act_c.append(al - ap)
            prev = preds[idx]
        if len(pred_c) > 2:
            corr = np.corrcoef(pred_c, act_c)[0, 1]
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
    mean_ssn = np.mean(train_vals); amp_ssn = (max(train_vals) - min(train_vals)) / 2
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
    print("SCRIPT 200b — THREE-WAY JUNCTION: PEAKS AND TROUGHS")
    print("=" * 80)
    print()
    print("Every extremum is a singularity for one of the other two systems.")
    print("6 transfer events per cycle: 3 at peaks, 3 at troughs.")
    print("Energy circulates: A→B→C→A (peaks) and A→C→B→A (troughs)")
    print()
    print(f"  κ_base = π-leak × 1/φ = {PI_LEAK * PHI_LEAK:.4f}")
    print(f"  Downhill (high→low): ×φ = ×{SING_DOWN:.4f}")
    print(f"  Uphill (low→high): ×1/φ = ×{SING_UP:.4f}")
    print(f"  Initial energy ratio: A : B : C = φ : 1 : 1/φ")
    print(f"                       = {PHI:.3f} : 1.000 : {PHI_LEAK:.3f}")
    print()

    splits = [1989, 1994, 1999, 2004, 2009]
    model_names = ['3Way', '3WayStrong', '3WayPhiR', 'Hybrid199', 'Sine']
    model_classes = {
        '3Way': ThreeWayJunction,
        '3WayStrong': ThreeWayStrong,
        '3WayPhiR': ThreeWayPhiRatio,
        'Hybrid199': HybridBaseline,
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
            phase = calibrate(train, cls, ARA_ENG_9, ARA_CON_9, P_SUBS)
            m = cls(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
            m.init_from_observation(start_log)
            p = m.predict_sequence(len(pred_years))
            preds[name] = {y: max(10**p[i], 0) for i, y in enumerate(pred_years)}
            all_results[name].append(evaluate(ssn_data, preds[name], pred_years))

        preds['Sine'] = sine_predict(train, pred_years, ssn_data)
        all_results['Sine'].append(evaluate(ssn_data, preds['Sine'], pred_years))

        n = len(pred_years)
        print(f"\n  Train <={split_year}, Predict {split_year+1}-2025 ({n} years)")
        print(f"  {'Model':<14s} {'Corr':>8s} {'Dir%':>8s} {'x2%':>8s} {'MAE':>8s}")
        print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
        for name in model_names:
            ev = all_results[name][-1]
            print(f"  {name:<14s} {ev['corr']:+8.3f} {ev['dir']:8.1f} {ev['x2']:8.1f} {ev['mae']:8.1f}")

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

    print(f"\n  {'Model':<14s} {'Avg Corr':>10s} {'Avg MAE':>10s} {'Avg Dir':>10s} {'Gap':>8s} {'Beats':>8s}")
    print(f"  {'-'*12} {'-'*10} {'-'*10} {'-'*10} {'-'*8} {'-'*8}")

    for name in model_names:
        res = all_results[name]
        ac = np.mean([r['corr'] for r in res])
        am = np.mean([r['mae'] for r in res])
        ad = np.mean([r['dir'] for r in res])
        gap = am - sine_mae
        pct = gap / sine_mae * 100
        beats = sum(1 for r, s in zip(res, all_results['Sine']) if r['mae'] < s['mae'])
        gap_str = f"{pct:+.0f}%" if name != 'Sine' else "---"
        print(f"  {name:<14s} {ac:+10.3f} {am:10.1f} {ad:10.1f}% {gap_str:>8s} {beats}/5")

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
    # ENERGY DYNAMICS — Track all 3 systems
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("THREE-WAY ENERGY DYNAMICS (2004 split)")
    print("=" * 80)

    train = {y: v for y, v in ssn_data.items() if y <= 2004}
    pred_years = [y for y in all_ssn_years if y > 2004 and y <= 2025]
    C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
    start_log = np.log10(max(ssn_data[2004], 0.1))

    phase = calibrate(train, ThreeWayJunction, ARA_ENG_9, ARA_CON_9, P_SUBS)
    tw = ThreeWayJunction(ARA_ENG_9, ARA_CON_9, P_SUBS, C, phase)
    tw.init_from_observation(start_log)

    print(f"\n  {'Year':>6s} {'Actual':>8s} {'Pred':>8s} {'|A|':>8s} {'|B|':>8s} {'|C|':>8s} {'A:B:C':>12s}")
    for i, y in enumerate(pred_years[:21]):
        obs = tw.observable_ssn(i + 1)
        pred_val = max(10**obs, 0)
        eA, eB, eC = tw.get_energy_state()
        total = eA + eB + eC
        if total > 0:
            rA = eA / total; rB = eB / total; rC = eC / total
            ratio_str = f"{rA:.2f}:{rB:.2f}:{rC:.2f}"
        else:
            ratio_str = "---"
        print(f"  {y:>6d} {ssn_data[y]:8.1f} {pred_val:8.1f} {eA:8.4f} {eB:8.4f} {eC:8.4f} {ratio_str:>12s}")

    # Show the phi ratio check
    print()
    eA, eB, eC = tw.get_energy_state()
    if eB > 0:
        print(f"  Final A/B ratio: {eA/eB:.3f} (φ = {PHI:.3f})")
    if eC > 0:
        print(f"  Final B/C ratio: {eB/eC:.3f} (φ = {PHI:.3f})")
    if eC > 0:
        print(f"  Final A/C ratio: {eA/eC:.3f} (φ² = {PHI**2:.3f})")

    print()
    print("=" * 80)
    print("Script 200b complete.")
    print("=" * 80)
