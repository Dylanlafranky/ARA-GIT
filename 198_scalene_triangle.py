#!/usr/bin/env python3
"""
Script 198 — The Scalene Triangle: φ in Two Directions, ARA in One
==============================================================================

Dylan's insight: "Maybe it's traveling φ in two directions and ARA in one.
Phi is a constant, but if you think of our system, it's a scalene triangle.
We have ARA = 1 for clocks, but clocks are just where the singularity event
occurs. We have Phi in one direction which is horizontal, so it makes sense
that that result is one corner of the triangle and it'd be equal to the other
coupling that isn't the ARA."

THE SCALENE TRIANGLE:

    Corner 1: ARA = 1 (singularity/clock)    — the VERTICAL axis
    Corner 2: φ-horizontal (time/periods)     — already in Script 197
    Corner 3: φ-coupling (coupling strength)  — NEW: the missing dimension

    Three sides, three different lengths, three φ/ARA relationships.
    The triangle is SCALENE because ARA ≠ φ — they're different constants
    governing different axes of the same geometry.

    Previously: coupling was FLAT (PI_LEAK everywhere).
    Now: coupling cascades by φ just like periods do.

    φ-time cascade (horizontal):
        Periods: P, P/φ, P/φ²  (22y → 13.6y → 8.4y)

    φ-coupling cascade (the third corner):
        Within triad: adjacent = κ, skip-one = κ/φ
        Between triads: adjacent = κ/φ, skip-one = κ/φ²
        (where κ = base coupling strength)

    ARA axis (vertical):
        Valve lift = max(ARA - 1, 0) for engines
        Unchanged — but valve AUTHORITY now also cascades by φ:
        sub-1 (middle speed) has φ× more valve influence than sub-2 (fastest)

    This means: the fast-channel valve isn't just open/closed, it has
    DIRECTIONAL AUTHORITY in the coupling space. The middle channel
    (one φ-step away) gates with authority φ/(φ+1) ≈ 61.8%.
    The fastest channel (two φ-steps away) gates with authority 1/(φ+1) ≈ 38.2%.
    Valve = weighted average, not exponential product — conserves energy.

    ENERGY BUDGET FIX (v2):
    The 9×9 coupling matrix sums to ~0.58 per channel vs ~0.37 in flat model.
    To preserve the φ RATIOS without changing total energy, we normalize
    each row of the coupling matrix so the row sum matches the flat model's
    total coupling budget. This way φ-geometry shapes the flow direction,
    but doesn't inject extra energy.
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
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3
PHI_LEAK = 1.0 / PHI

# ═══════════════════════════════════════════════════════════════════
# SCALENE TRIANGLE: φ-COUPLING CASCADE
# ═══════════════════════════════════════════════════════════════════

# Base coupling strength
KAPPA = PI_LEAK  # ≈ 0.14159

# Within a sub-triad: coupling decays by φ with distance
#   adjacent (1 step in period hierarchy) = κ
#   skip-one (2 steps) = κ/φ
INTRA_ADJACENT = KAPPA           # sub-0 ↔ sub-1, sub-1 ↔ sub-2
INTRA_SKIP     = KAPPA / PHI     # sub-0 ↔ sub-2

# Between parent triads: one more φ step down
#   adjacent parents (1 step) = κ/φ
#   skip-one parents (2 steps) = κ/φ²
INTER_ADJACENT = KAPPA / PHI       # parent-0 ↔ parent-1, parent-1 ↔ parent-2
INTER_SKIP     = KAPPA / PHI**2    # parent-0 ↔ parent-2

# Singularity gate
SING_DOWN = PHI       # engine → consumer (amplified)
SING_UP = PHI_LEAK    # consumer → engine (attenuated)

# ═══════════════════════════════════════════════════════════════════
# φ-PERIOD CASCADE (unchanged from Script 197)
# ═══════════════════════════════════════════════════════════════════

P_PARENT = [HALE_PERIOD, HALE_PERIOD / PHI, HALE_PERIOD / PHI**2]

P_SUBS = []
for parent_p in P_PARENT:
    for sub_idx in range(3):
        P_SUBS.append(parent_p / PHI**sub_idx)

# ═══════════════════════════════════════════════════════════════════
# ARA DECOMPOSITION (unchanged)
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

# ═══════════════════════════════════════════════════════════════════
# FROZEN V4 PARAMETERS
# ═══════════════════════════════════════════════════════════════════

V4_DEPTH = 1.0
V4_BASIN_UP = 0.1
V4_BASIN_DOWN = 1.0
V4_FLOOR = 0.5

SUB_PHASE_LAG = 2 * np.pi / 3
PARENT_PHASE_LAG = 2 * np.pi / 3
MIRROR_PHASE = np.pi

ARA_SSN_SINGLE = 1.73
MIDOFF_SINGLE = abs((1.73 + 0.15) / 2 - R_COUPLER)

# ═══════════════════════════════════════════════════════════════════
# CORE WAVE MECHANICS (unchanged from 197)
# ═══════════════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════════════
# CHANNEL PREDICTION (unchanged from 197)
# ═══════════════════════════════════════════════════════════════════

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
    overflow_to_consumer = 0.0
    if new_val < floor:
        overflow_to_consumer = floor - new_val
        new_val = floor

    return new_val, valley, overflow_to_consumer

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
    overflow_to_engine = 0.0
    if new_val > ceiling:
        overflow_to_engine = new_val - ceiling
        new_val = ceiling

    return new_val, valley, overflow_to_engine

# ═══════════════════════════════════════════════════════════════════
# SCALENE TRIANGLE MODEL
# ═══════════════════════════════════════════════════════════════════

class ScaleneTriangleModel:
    """
    F⁹ with the scalene triangle geometry:

    Axis 1 — ARA (vertical): valve lift, engine/consumer behavior
    Axis 2 — φ-time (horizontal): period cascade P/φ^n
    Axis 3 — φ-coupling (diagonal): coupling strength cascade κ/φ^n

    The coupling between any two channels depends on their DISTANCE
    in the φ-period hierarchy, not just whether they share a parent.
    Closer in period = stronger coupling = more influence.

    The valve authority also follows φ-coupling:
    sub-1 (one φ-step from base) has valve weight φ
    sub-2 (two φ-steps from base) has valve weight 1
    Total valve = (valve_1)^φ × (valve_2)^1
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.ara_eng = list(ara_eng_9)
        self.ara_con = list(ara_con_9)
        self.periods = list(periods_9)
        self.C = C
        self.N = 9

        # Phase array
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

        # Pre-compute the φ-coupling matrix (9×9) — ASYMMETRIC (scalene)
        #
        # The scalene triangle has NO axis of symmetry.
        # Information flowing DOWN (slow→fast, long period→short period)
        # is amplified by φ — like gravity, energy flows downhill easily.
        # Information flowing UP (fast→slow, short period→long period)
        # is attenuated by 1/φ — uphill is harder.
        #
        # This is the SAME asymmetry as the one-shot gate (φ down, 1/φ up)
        # but applied to the continuous coupling channel.
        #
        # Combined with period-distance decay, the coupling from j→i is:
        #   base_strength × φ^(direction_factor)
        # where direction_factor = +1 if j is slower (downhill to i)
        #                        = -1 if j is faster (uphill to i)
        #                        =  0 if same speed

        raw_matrix = np.zeros((9, 9))
        for i in range(9):
            for j in range(9):
                if i == j:
                    continue
                pi_parent = i // 3
                pj_parent = j // 3
                si_sub = i % 3
                sj_sub = j % 3

                if pi_parent == pj_parent:
                    sub_distance = abs(si_sub - sj_sub)
                    if sub_distance == 1:
                        base = INTRA_ADJACENT
                    else:
                        base = INTRA_SKIP
                else:
                    parent_distance = min(
                        abs(pi_parent - pj_parent),
                        3 - abs(pi_parent - pj_parent)
                    )
                    sub_distance = abs(si_sub - sj_sub)
                    if parent_distance == 1:
                        base = INTER_ADJACENT
                    else:
                        base = INTER_SKIP
                    base = base / PHI**sub_distance

                # DIRECTIONAL ASYMMETRY (the scalene):
                # periods[j] > periods[i] means j is slower → downhill → ×φ
                # periods[j] < periods[i] means j is faster → uphill → ×(1/φ)
                period_j = periods_9[j]
                period_i = periods_9[i]
                if period_j > period_i * 1.01:  # j is slower → downhill
                    direction = PHI
                elif period_j < period_i * 0.99:  # j is faster → uphill
                    direction = PHI_LEAK
                else:  # same period
                    direction = 1.0

                raw_matrix[i, j] = base * direction

        # Normalize total coupling per channel to match flat model budget
        flat_budget = 2 * PI_LEAK + PI_LEAK * PHI_LEAK
        self.coupling_matrix = np.zeros((9, 9))
        for i in range(9):
            row_sum = raw_matrix[i].sum()
            if row_sum > 0:
                self.coupling_matrix[i] = raw_matrix[i] * (flat_budget / row_sum)

    def init_from_observation(self, log_ssn):
        for i in range(3):
            self.eng_states[i] = log_ssn + 0.03 * (1 - i * 0.3)
            self.eng_states[3 + i] = log_ssn - 0.01 * i
            self.eng_states[6 + i] = self.C
        for i in range(9):
            self.con_states[i] = 2 * self.C - self.eng_states[i]

    def step(self, t):
        new_eng = [0.0] * self.N
        new_con = [0.0] * self.N
        eng_valleys = [0.0] * self.N
        con_valleys = [0.0] * self.N
        eng_overflow = [0.0] * self.N
        con_overflow = [0.0] * self.N

        # Phase 1: Independent predictions
        for i in range(self.N):
            new_eng[i], eng_valleys[i], eng_overflow[i] = engine_channel(
                self.eng_states[i], self.C, self.ara_eng[i],
                t, self.eng_phases[i], self.periods[i]
            )
            new_con[i], con_valleys[i], con_overflow[i] = consumer_channel(
                self.con_states[i], self.C, self.ara_con[i],
                t, self.con_phases[i], self.periods[i]
            )

        # Phase 2: φ-COUPLING CASCADE (the third corner of the triangle)
        # Each channel pulls on every other channel, but strength decays by φ
        # with distance in the period hierarchy
        for i in range(self.N):
            eng_pull = 0.0
            con_pull = 0.0
            for j in range(self.N):
                if i == j:
                    continue
                kappa_ij = self.coupling_matrix[j, i]  # j pulls on i
                if kappa_ij > 0:
                    eng_disp = self.eng_states[j] - eng_valleys[j]
                    con_disp = self.con_states[j] - con_valleys[j]
                    eng_pull += kappa_ij * eng_disp
                    con_pull += kappa_ij * con_disp
            new_eng[i] += eng_pull
            new_con[i] += con_pull

        # Phase 3: Singularity gate (one-shot, φ/1/φ)
        for i in range(self.N):
            if eng_overflow[i] > 0 and not self.eng_gate_fired[i]:
                transfer = eng_overflow[i] * SING_DOWN
                parent = i // 3
                con_base = parent * 3
                new_con[con_base] += transfer * 0.5
                new_con[con_base + 1] += transfer * 0.3
                new_con[con_base + 2] += transfer * 0.2
                self.eng_gate_fired[i] = True
            elif eng_overflow[i] == 0 and self.eng_gate_fired[i]:
                self.eng_gate_fired[i] = False

        for i in range(self.N):
            if con_overflow[i] > 0 and not self.con_gate_fired[i]:
                transfer = con_overflow[i] * SING_UP
                parent = i // 3
                eng_base = parent * 3
                new_eng[eng_base] += transfer * 0.5
                new_eng[eng_base + 1] += transfer * 0.3
                new_eng[eng_base + 2] += transfer * 0.2
                self.con_gate_fired[i] = True
            elif con_overflow[i] == 0 and self.con_gate_fired[i]:
                self.con_gate_fired[i] = False

        # Phase 4: Cross-triad continuous coupling (engine activity → consumer, etc.)
        # Now uses φ-cascade instead of flat INTER_SUB_COUPLING
        act_mean = np.mean([self.eng_states[3 + j] - eng_valleys[3 + j] for j in range(3)])
        acc_mean = np.mean([self.con_states[6 + j] - con_valleys[6 + j] for j in range(3)])
        for j in range(3):
            new_con[j] += INTER_ADJACENT * act_mean
            new_eng[j] += INTER_ADJACENT * acc_mean

        # Phase 5: Soft bounds
        for i in range(self.N):
            floor = self.C - V4_FLOOR * 1.5
            if new_eng[i] < floor:
                new_eng[i] = floor
            ceiling = self.C + V4_FLOOR * 1.5
            if new_con[i] > ceiling:
                new_con[i] = ceiling

        self.eng_states = new_eng
        self.con_states = new_con

    def observable_ssn(self):
        """
        SCALENE VALVE: CAM valve with φ-weighted authority.

        The valve authority IS the third corner of the triangle:
            sub-1 (middle, one φ-step from base): weight = φ/(φ+1) ≈ 61.8%
            sub-2 (fastest, two φ-steps from base): weight = 1/(φ+1) ≈ 38.2%

        valve = (φ × vp1 + 1 × vp2) / (φ + 1)

        Weighted average: middle channel has φ× more authority than fastest.
        Conserves energy (no exponential blowup), preserves φ-geometry.
        """
        W1 = PHI / (PHI + 1.0)    # ≈ 0.618 — middle sub-channel weight
        W2 = 1.0 / (PHI + 1.0)    # ≈ 0.382 — fastest sub-channel weight

        eng_parent_obs = []
        con_parent_obs = []

        for parent_idx in range(3):
            base = parent_idx * 3

            # ENGINE VALVE with φ-authority
            eng_base_signal = self.eng_states[base] - self.C

            # Sub-1 (middle speed, one φ-step away): weight = W1
            i1 = base + 1
            fast_state_1 = self.eng_states[i1]
            fast_ara_1 = self.ara_eng[i1]
            ef1 = max(fast_ara_1 - 1.0, 0.0)
            fd1 = fast_state_1 - self.C
            vp1 = max(0.0, 1.0 + ef1 * fd1)  # valve position sub-1

            # Sub-2 (fastest, two φ-steps away): weight = W2
            i2 = base + 2
            fast_state_2 = self.eng_states[i2]
            fast_ara_2 = self.ara_eng[i2]
            ef2 = max(fast_ara_2 - 1.0, 0.0)
            fd2 = fast_state_2 - self.C
            vp2 = max(0.0, 1.0 + ef2 * fd2)  # valve position sub-2

            # φ-weighted average valve
            eng_valve = W1 * vp1 + W2 * vp2
            eng_obs = self.C + eng_base_signal * eng_valve
            eng_parent_obs.append(eng_obs)

            # CONSUMER VALVE with φ-authority (reversed)
            con_base_signal = self.con_states[base] - self.C

            i1c = base + 1
            cs1 = self.con_states[i1c]
            ca1 = self.ara_con[i1c]
            cf1 = max(1.0 - ca1, 0.0)
            cd1 = self.C - cs1
            cvp1 = max(0.0, 1.0 + cf1 * cd1)

            i2c = base + 2
            cs2 = self.con_states[i2c]
            ca2 = self.ara_con[i2c]
            cf2 = max(1.0 - ca2, 0.0)
            cd2 = self.C - cs2
            cvp2 = max(0.0, 1.0 + cf2 * cd2)

            con_valve = W1 * cvp1 + W2 * cvp2
            con_obs = self.C + con_base_signal * con_valve
            con_parent_obs.append(con_obs)

        # System observable (same combination as F⁶)
        eng_s2 = eng_parent_obs[1]
        eng_s1_excess = eng_parent_obs[0] - self.C
        eng_s3_state = eng_parent_obs[2] - self.C
        con_stored = max(con_parent_obs[2] - self.C, 0)
        con_room = max(self.C - con_parent_obs[0], 0)

        engine_signal = eng_s2 + PI_LEAK * (eng_s1_excess + eng_s3_state) * 0.3
        consumer_feedback = PI_LEAK * (con_stored - con_room) * 0.5

        return engine_signal + consumer_feedback

# ═══════════════════════════════════════════════════════════════════
# FLAT-COUPLING F⁹ (Script 197 v4 — CAM valve, for comparison)
# ═══════════════════════════════════════════════════════════════════

INTRA_SUB_COUPLING_FLAT = PI_LEAK
INTER_SUB_COUPLING_FLAT = PI_LEAK * PHI_LEAK

class FlatCouplingModel:
    """Script 197 v4 CAM valve with flat coupling (no φ-cascade)."""

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
        new_eng = [0.0] * self.N
        new_con = [0.0] * self.N
        eng_valleys = [0.0] * self.N
        con_valleys = [0.0] * self.N
        eng_overflow = [0.0] * self.N
        con_overflow = [0.0] * self.N

        for i in range(self.N):
            new_eng[i], eng_valleys[i], eng_overflow[i] = engine_channel(
                self.eng_states[i], self.C, self.ara_eng[i],
                t, self.eng_phases[i], self.periods[i]
            )
            new_con[i], con_valleys[i], con_overflow[i] = consumer_channel(
                self.con_states[i], self.C, self.ara_con[i],
                t, self.con_phases[i], self.periods[i]
            )

        # FLAT coupling — same strength everywhere within triad / between triads
        for parent_idx in range(3):
            base = parent_idx * 3
            for local in range(3):
                i = base + local
                upstream = base + (local - 1) % 3
                eng_disp = self.eng_states[upstream] - eng_valleys[upstream]
                new_eng[i] += INTRA_SUB_COUPLING_FLAT * eng_disp
                con_disp = self.con_states[upstream] - con_valleys[upstream]
                new_con[i] += INTRA_SUB_COUPLING_FLAT * con_disp

        for parent_idx in range(3):
            src_base = parent_idx * 3
            dst_base = ((parent_idx + 1) % 3) * 3
            src_eng_disp = np.mean([
                self.eng_states[src_base + j] - eng_valleys[src_base + j]
                for j in range(3)
            ])
            src_con_disp = np.mean([
                self.con_states[src_base + j] - con_valleys[src_base + j]
                for j in range(3)
            ])
            for j in range(3):
                new_eng[dst_base + j] += INTER_SUB_COUPLING_FLAT * src_eng_disp
                new_con[dst_base + j] += INTER_SUB_COUPLING_FLAT * src_con_disp

        for i in range(self.N):
            if eng_overflow[i] > 0 and not self.eng_gate_fired[i]:
                transfer = eng_overflow[i] * SING_DOWN
                parent = i // 3
                con_base = parent * 3
                new_con[con_base] += transfer * 0.5
                new_con[con_base + 1] += transfer * 0.3
                new_con[con_base + 2] += transfer * 0.2
                self.eng_gate_fired[i] = True
            elif eng_overflow[i] == 0 and self.eng_gate_fired[i]:
                self.eng_gate_fired[i] = False

        for i in range(self.N):
            if con_overflow[i] > 0 and not self.con_gate_fired[i]:
                transfer = con_overflow[i] * SING_UP
                parent = i // 3
                eng_base = parent * 3
                new_eng[eng_base] += transfer * 0.5
                new_eng[eng_base + 1] += transfer * 0.3
                new_eng[eng_base + 2] += transfer * 0.2
                self.con_gate_fired[i] = True
            elif con_overflow[i] == 0 and self.con_gate_fired[i]:
                self.con_gate_fired[i] = False

        act_mean = np.mean([self.eng_states[3 + j] - eng_valleys[3 + j] for j in range(3)])
        acc_mean = np.mean([self.con_states[6 + j] - con_valleys[6 + j] for j in range(3)])
        for j in range(3):
            new_con[j] += INTER_SUB_COUPLING_FLAT * act_mean
            new_eng[j] += INTER_SUB_COUPLING_FLAT * acc_mean

        for i in range(self.N):
            floor = self.C - V4_FLOOR * 1.5
            if new_eng[i] < floor:
                new_eng[i] = floor
            ceiling = self.C + V4_FLOOR * 1.5
            if new_con[i] > ceiling:
                new_con[i] = ceiling

        self.eng_states = new_eng
        self.con_states = new_con

    def observable_ssn(self):
        """Script 197 v4 CAM valve — flat authority (both sub-channels equal)."""
        eng_parent_obs = []
        con_parent_obs = []

        for parent_idx in range(3):
            base = parent_idx * 3
            eng_base_signal = self.eng_states[base] - self.C
            eng_valve = 1.0
            for sub_idx in [1, 2]:
                i = base + sub_idx
                fast_state = self.eng_states[i]
                fast_ara = self.ara_eng[i]
                engine_factor = max(fast_ara - 1.0, 0.0)
                fast_displacement = fast_state - self.C
                valve_position = max(0.0, 1.0 + engine_factor * fast_displacement)
                eng_valve *= valve_position
            eng_obs = self.C + eng_base_signal * eng_valve
            eng_parent_obs.append(eng_obs)

            con_base_signal = self.con_states[base] - self.C
            con_valve = 1.0
            for sub_idx in [1, 2]:
                i = base + sub_idx
                fast_state = self.con_states[i]
                fast_ara = self.ara_con[i]
                consumer_factor = max(1.0 - fast_ara, 0.0)
                fast_displacement = self.C - fast_state
                valve_position = max(0.0, 1.0 + consumer_factor * fast_displacement)
                con_valve *= valve_position
            con_obs = self.C + con_base_signal * con_valve
            con_parent_obs.append(con_obs)

        eng_s2 = eng_parent_obs[1]
        eng_s1_excess = eng_parent_obs[0] - self.C
        eng_s3_state = eng_parent_obs[2] - self.C
        con_stored = max(con_parent_obs[2] - self.C, 0)
        con_room = max(self.C - con_parent_obs[0], 0)

        engine_signal = eng_s2 + PI_LEAK * (eng_s1_excess + eng_s3_state) * 0.3
        consumer_feedback = PI_LEAK * (con_stored - con_room) * 0.5

        return engine_signal + consumer_feedback

# ═══════════════════════════════════════════════════════════════════
# F⁶ MODEL (from Script 196)
# ═══════════════════════════════════════════════════════════════════

class ARALoopModel:
    def __init__(self, ara_eng, ara_con, C, phase0_base):
        self.ara_eng = ara_eng
        self.ara_con = ara_con
        self.C = C
        self.eng_phases = [phase0_base + i * 2 * np.pi / 3 for i in range(3)]
        self.con_phases = [p + MIRROR_PHASE for p in self.eng_phases]
        self.eng_states = [C, C, C]
        self.con_states = [C, C, C]
        self.eng_gate_fired = [False, False, False]
        self.con_gate_fired = [False, False, False]

    def init_from_observation(self, log_ssn):
        self.eng_states[1] = log_ssn
        self.eng_states[0] = log_ssn + 0.05
        self.eng_states[2] = self.C
        self.con_states[0] = self.C
        self.con_states[1] = 2 * self.C - log_ssn
        self.con_states[2] = self.C

    def step(self, t):
        new_eng = [0.0, 0.0, 0.0]
        new_con = [0.0, 0.0, 0.0]
        eng_v = [0.0, 0.0, 0.0]
        con_v = [0.0, 0.0, 0.0]
        eng_of = [0.0, 0.0, 0.0]
        con_of = [0.0, 0.0, 0.0]

        for i in range(3):
            new_eng[i], eng_v[i], eng_of[i] = engine_channel(
                self.eng_states[i], self.C, self.ara_eng[i],
                t, self.eng_phases[i], HALE_PERIOD)
            new_con[i], con_v[i], con_of[i] = consumer_channel(
                self.con_states[i], self.C, self.ara_con[i],
                t, self.con_phases[i], HALE_PERIOD)

        for i in range(3):
            up = (i - 1) % 3
            new_eng[i] += PI_LEAK * (self.eng_states[up] - eng_v[up])
            new_con[i] += PI_LEAK * (self.con_states[up] - con_v[up])

        for i in range(3):
            if eng_of[i] > 0 and not self.eng_gate_fired[i]:
                tr = eng_of[i] * SING_DOWN
                new_con[0] += tr * 0.5; new_con[1] += tr * 0.3; new_con[2] += tr * 0.2
                self.eng_gate_fired[i] = True
            elif eng_of[i] == 0 and self.eng_gate_fired[i]:
                self.eng_gate_fired[i] = False
            if con_of[i] > 0 and not self.con_gate_fired[i]:
                tr = con_of[i] * SING_UP
                new_eng[0] += tr * 0.5; new_eng[2] += tr * 0.3; new_eng[1] += tr * 0.2
                self.con_gate_fired[i] = True
            elif con_of[i] == 0 and self.con_gate_fired[i]:
                self.con_gate_fired[i] = False

        new_con[0] += INTER_SUB_COUPLING_FLAT * (self.eng_states[1] - eng_v[1])
        new_eng[0] += INTER_SUB_COUPLING_FLAT * (self.con_states[2] - con_v[2])

        for i in range(3):
            new_eng[i] = max(new_eng[i], self.C - V4_FLOOR * 1.5)
            new_con[i] = min(new_con[i], self.C + V4_FLOOR * 1.5)

        self.eng_states = new_eng
        self.con_states = new_con

    def observable_ssn(self):
        s2 = self.eng_states[1]
        s1x = self.eng_states[0] - self.C
        s3x = self.eng_states[2] - self.C
        cs = max(self.con_states[2] - self.C, 0)
        cr = max(self.C - self.con_states[0], 0)
        return s2 + PI_LEAK * (s1x + s3x) * 0.3 + PI_LEAK * (cs - cr) * 0.5

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
    if d > 0:
        c = -ef * V4_BASIN_DOWN * d
    else:
        c = -ef * V4_BASIN_UP * d
    nv = bounced + c
    floor = C - V4_FLOOR
    if nv < floor:
        nv = floor + (nv - floor) * 0.1
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

def calibrate_model(train_data, model_factory, n_phases=24):
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase, best_score = 0.0, -999

    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases
        test_start = max(0, len(years) - 15)
        model = model_factory(C, phase0)
        start_log = np.log10(max(train_data[years[test_start]], 0.1))
        model.init_from_observation(start_log)

        pred_changes, act_changes = [], []
        prev_obs = start_log

        for i in range(test_start + 1, len(years)):
            t = i - test_start
            model.step(t)
            obs = model.observable_ssn()
            pred_changes.append(obs - prev_obs)
            actual_log = np.log10(max(train_data[years[i]], 0.1))
            actual_prev = np.log10(max(train_data[years[i - 1]], 0.1))
            act_changes.append(actual_log - actual_prev)
            prev_obs = obs

        if len(pred_changes) > 2:
            corr = np.corrcoef(pred_changes, act_changes)[0, 1]
            if not np.isnan(corr) and corr > best_score:
                best_score = corr
                best_phase = phase0

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
            t = i - test_start
            log_val = single_channel_predict(log_val, C, t, phase0)
            pred_c.append(log_val - prev)
            al = np.log10(max(train_data[years[i]], 0.1))
            ap = np.log10(max(train_data[years[i - 1]], 0.1))
            act_c.append(al - ap)
            prev = log_val
        if len(pred_c) > 2:
            corr = np.corrcoef(pred_c, act_c)[0, 1]
            if not np.isnan(corr) and corr > best_score:
                best_score = corr
                best_phase = phase0
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
    print("SCRIPT 198 — THE SCALENE TRIANGLE: phi IN TWO DIRECTIONS, ARA IN ONE")
    print("=" * 80)
    print()
    print("Three corners of the prediction geometry:")
    print(f"  Corner 1: ARA = 1 (singularity/clock) — vertical axis (valve lift)")
    print(f"  Corner 2: phi-horizontal (time) — period cascade P/phi^n")
    print(f"  Corner 3: phi-coupling (strength) — coupling cascade kappa/phi^n")
    print()
    print("phi-coupling matrix (9x9):")
    print("  Intra-triad adjacent: {:.4f}".format(INTRA_ADJACENT))
    print("  Intra-triad skip:     {:.4f}  (/{:.3f} = phi)".format(INTRA_SKIP, INTRA_ADJACENT/INTRA_SKIP))
    print("  Inter-triad adjacent: {:.4f}  (/{:.3f} = phi)".format(INTER_ADJACENT, INTRA_ADJACENT/INTER_ADJACENT))
    print("  Inter-triad skip:     {:.4f}  (/{:.3f} = phi^2)".format(INTER_SKIP, INTRA_ADJACENT/INTER_SKIP))
    print()
    print("Valve authority (phi-weighted):")
    print(f"  Sub-1 (middle, 1 phi-step): weight = phi = {PHI:.3f}")
    print(f"  Sub-2 (fastest, 2 phi-steps): weight = 1")
    print(f"  Valve = vp1^phi x vp2^1")
    print()

    # Build coupling matrix for display
    test_model = ScaleneTriangleModel(ARA_ENG_9, ARA_CON_9, P_SUBS, 1.0, 0.0)
    print("  Full coupling matrix (engine side):")
    labels = []
    for p in range(3):
        for s in range(3):
            labels.append(f"P{p}S{s}")
    print(f"      {'  '.join(f'{l:>6s}' for l in labels)}")
    for i in range(9):
        row = [f"{test_model.coupling_matrix[i,j]:6.4f}" for j in range(9)]
        print(f"  {labels[i]:>4s} {'  '.join(row)}")
    print()

    # ═══════════════════════════════════════════════════════════
    # MODELS
    # ═══════════════════════════════════════════════════════════

    # Also test: flat coupling but φ-weighted observable
    class PhiObservableModel(FlatCouplingModel):
        """Flat coupling (same as F9-flat) but φ-weighted system observable.

        The third corner of the triangle: φ weights the COMBINATION of
        parent-level signals, not the coupling between them.

        Parent 0 (Dynamo, slowest): excess contributes × φ
        Parent 1 (Activity, middle): the primary signal (× 1)
        Parent 2 (Reversal, fastest): state contributes × 1/φ

        Similarly for consumer side.
        This makes the observable φ-structured in the SCALE direction.
        """
        def observable_ssn(self):
            # Same CAM valve as parent class to get parent obs
            eng_parent_obs = []
            con_parent_obs = []

            for parent_idx in range(3):
                base = parent_idx * 3
                eng_base_signal = self.eng_states[base] - self.C
                eng_valve = 1.0
                for sub_idx in [1, 2]:
                    i = base + sub_idx
                    fast_state = self.eng_states[i]
                    fast_ara = self.ara_eng[i]
                    engine_factor = max(fast_ara - 1.0, 0.0)
                    fast_displacement = fast_state - self.C
                    valve_position = max(0.0, 1.0 + engine_factor * fast_displacement)
                    eng_valve *= valve_position
                eng_obs = self.C + eng_base_signal * eng_valve
                eng_parent_obs.append(eng_obs)

                con_base_signal = self.con_states[base] - self.C
                con_valve = 1.0
                for sub_idx in [1, 2]:
                    i = base + sub_idx
                    fast_state = self.con_states[i]
                    fast_ara = self.ara_con[i]
                    consumer_factor = max(1.0 - fast_ara, 0.0)
                    fast_displacement = self.C - fast_state
                    valve_position = max(0.0, 1.0 + consumer_factor * fast_displacement)
                    con_valve *= valve_position
                con_obs = self.C + con_base_signal * con_valve
                con_parent_obs.append(con_obs)

            # φ-WEIGHTED COMBINATION (the scalene observable)
            eng_s2 = eng_parent_obs[1]  # Activity: primary signal
            eng_s1_excess = eng_parent_obs[0] - self.C  # Dynamo excess: × φ
            eng_s3_state = eng_parent_obs[2] - self.C   # Reversal state: × 1/φ
            con_stored = max(con_parent_obs[2] - self.C, 0)  # Slowest consumer: × φ
            con_room = max(self.C - con_parent_obs[0], 0)    # Fastest consumer: × 1/φ

            # φ-weighted: slow parent contributes more, fast parent less
            engine_signal = eng_s2 + PI_LEAK * (PHI * eng_s1_excess + PHI_LEAK * eng_s3_state) * 0.3
            consumer_feedback = PI_LEAK * (PHI * con_stored - PHI_LEAK * con_room) * 0.5

            return engine_signal + consumer_feedback

    models_to_test = {
        'Scalene':   lambda C, p0: ScaleneTriangleModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, p0),
        'Phi-obs':   lambda C, p0: PhiObservableModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, p0),
        'F9-flat':   lambda C, p0: FlatCouplingModel(ARA_ENG_9, ARA_CON_9, P_SUBS, C, p0),
        'F6':        lambda C, p0: ARALoopModel(ARA_ENG_PARENTS, ARA_CON_PARENTS, C, p0),
    }

    splits = [1989, 1994, 1999, 2004, 2009]
    all_results = {name: [] for name in models_to_test}
    all_results['F1'] = []
    all_results['Sine'] = []

    print("=" * 80)
    print("SUNSPOT PREDICTIONS — SCALENE vs FLAT vs F6 vs F1 vs SINE")
    print("=" * 80)

    for split_year in splits:
        train = {y: v for y, v in ssn_data.items() if y <= split_year}
        pred_years = [y for y in all_ssn_years if y > split_year and y <= 2025]
        if not pred_years: continue

        C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
        start_year = max(train.keys())
        start_log = np.log10(max(ssn_data[start_year], 0.1))

        preds = {}

        for name, factory in models_to_test.items():
            phase = calibrate_model(train, factory)
            model = factory(C, phase)
            model.init_from_observation(start_log)
            p = {}
            for i, y in enumerate(pred_years):
                model.step(i + 1)
                obs = model.observable_ssn()
                p[y] = max(10 ** obs, 0)
            preds[name] = p
            ev = evaluate(ssn_data, p, pred_years)
            all_results[name].append(ev)

        # F1
        phase_f1 = calibrate_single(train)
        log_val = start_log
        p_f1 = {}
        for i, y in enumerate(pred_years):
            log_val = single_channel_predict(log_val, C, i + 1, phase_f1)
            p_f1[y] = max(10 ** log_val, 0)
        preds['F1'] = p_f1
        ev_f1 = evaluate(ssn_data, p_f1, pred_years)
        all_results['F1'].append(ev_f1)

        # Sine
        train_vals = [ssn_data[y] for y in sorted(train.keys())]
        mean_ssn = np.mean(train_vals)
        amp_ssn = (max(train_vals) - min(train_vals)) / 2
        best_sp, best_sc = 0, -999
        for pi in range(48):
            p0 = 2 * np.pi * pi / 48
            sp = {y: max(mean_ssn + amp_ssn * np.sin(2*np.pi*y/11+p0), 0) for y in pred_years}
            e = evaluate(ssn_data, sp, pred_years)
            if e['corr'] > best_sc:
                best_sc = e['corr']; best_sp = p0
        p_sine = {y: max(mean_ssn + amp_ssn * np.sin(2*np.pi*y/11+best_sp), 0) for y in pred_years}
        preds['Sine'] = p_sine
        ev_sine = evaluate(ssn_data, p_sine, pred_years)
        all_results['Sine'].append(ev_sine)

        n = len(pred_years)
        print(f"\n  Train <={split_year}, Predict {split_year+1}-2025 ({n} years)")
        print()
        print(f"  {'Model':<16s} {'Corr':>8s} {'Dir%':>8s} {'x2%':>8s} {'MAE':>8s}")
        print(f"  {'-'*14} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
        for name in ['Scalene', 'Phi-obs', 'F9-flat', 'F6', 'F1', 'Sine']:
            ev = all_results[name][-1]
            print(f"  {name:<16s} {ev['corr']:+8.3f} {ev['dir']:8.1f} {ev['x2']:8.1f} {ev['mae']:8.1f}")

        # Year-by-year
        print(f"\n  Year-by-year (first 15):")
        print(f"    {'Year':>6s} {'Actual':>8s} {'Scalene':>8s} {'Phi-obs':>8s} {'F9-flat':>8s} {'F6':>8s} {'Sine':>8s}")
        for y in pred_years[:15]:
            print(f"    {y:>6d} {ssn_data[y]:8.1f} {preds['Scalene'][y]:8.1f} {preds['Phi-obs'][y]:8.1f} {preds['F9-flat'][y]:8.1f} {preds['F6'][y]:8.1f} {preds['Sine'][y]:8.1f}")

    # ═══════════════════════════════════════════════════════════
    # EARTHQUAKE
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("EARTHQUAKE — SCALENE vs F9-flat vs F6")
    print("=" * 80)

    ARA_EQ_ENG = [0.45, 0.30, 0.25]
    ARA_EQ_CON = [2.0 - a for a in ARA_EQ_ENG]
    eq_mean = np.mean(ARA_EQ_ENG)
    eq_shape = np.array(ARA_EQ_ENG) / eq_mean
    ARA_EQ_E9 = []
    ARA_EQ_C9 = []
    for pa in ARA_EQ_ENG:
        ARA_EQ_E9.extend(np.clip(pa * eq_shape, 0.01, 1.99))
    for pa in ARA_EQ_CON:
        ARA_EQ_C9.extend(np.clip(pa * eq_shape, 0.01, 1.99))

    EQ_BASE_P = 30
    P_EQ = []
    for pidx in range(3):
        pp = EQ_BASE_P / PHI**pidx
        for sidx in range(3):
            P_EQ.append(pp / PHI**sidx)

    eq_res = {name: [] for name in ['Scalene', 'Phi-obs', 'F9-flat', 'F6']}

    for split_year in splits:
        eq_train = {y: v for y, v in eq_data.items() if y <= split_year}
        eq_pred = [y for y in all_eq_years if y > split_year and y <= 2024]
        if not eq_pred: continue

        C_eq = np.mean(np.log10([max(v, 0.1) for v in eq_train.values()]))
        se = max(eq_train.keys())
        sl = np.log10(max(eq_data[se], 0.1))

        # Scalene EQ
        scl_fac = lambda C, p0: ScaleneTriangleModel(ARA_EQ_E9, ARA_EQ_C9, P_EQ, C, p0)
        ph = calibrate_model(eq_train, scl_fac)
        m = scl_fac(C_eq, ph)
        m.init_from_observation(sl)
        pq = {}
        for i, y in enumerate(eq_pred):
            m.step(i+1)
            pq[y] = max(10**m.observable_ssn(), 0)
        ev = evaluate(eq_data, pq, eq_pred)
        eq_res['Scalene'].append(ev)

        # Phi-obs EQ
        po_fac = lambda C, p0: PhiObservableModel(ARA_EQ_E9, ARA_EQ_C9, P_EQ, C, p0)
        ph = calibrate_model(eq_train, po_fac)
        m = po_fac(C_eq, ph)
        m.init_from_observation(sl)
        pq = {}
        for i, y in enumerate(eq_pred):
            m.step(i+1)
            pq[y] = max(10**m.observable_ssn(), 0)
        ev = evaluate(eq_data, pq, eq_pred)
        eq_res['Phi-obs'].append(ev)

        # F9-flat EQ
        f9_fac = lambda C, p0: FlatCouplingModel(ARA_EQ_E9, ARA_EQ_C9, P_EQ, C, p0)
        ph = calibrate_model(eq_train, f9_fac)
        m = f9_fac(C_eq, ph)
        m.init_from_observation(sl)
        pq = {}
        for i, y in enumerate(eq_pred):
            m.step(i+1)
            pq[y] = max(10**m.observable_ssn(), 0)
        ev = evaluate(eq_data, pq, eq_pred)
        eq_res['F9-flat'].append(ev)

        # F6 EQ
        f6_fac = lambda C, p0: ARALoopModel(ARA_EQ_ENG, ARA_EQ_CON, C, p0)
        ph6 = calibrate_model(eq_train, f6_fac)
        m6 = f6_fac(C_eq, ph6)
        m6.init_from_observation(sl)
        pq6 = {}
        for i, y in enumerate(eq_pred):
            m6.step(i+1)
            pq6[y] = max(10**m6.observable_ssn(), 0)
        ev6 = evaluate(eq_data, pq6, eq_pred)
        eq_res['F6'].append(ev6)

        print(f"  <={split_year}: Scalene={eq_res['Scalene'][-1]['corr']:+.3f}/{eq_res['Scalene'][-1]['mae']:.1f} | "
              f"Phi-obs={eq_res['Phi-obs'][-1]['corr']:+.3f}/{eq_res['Phi-obs'][-1]['mae']:.1f} | "
              f"F9-flat={eq_res['F9-flat'][-1]['corr']:+.3f}/{eq_res['F9-flat'][-1]['mae']:.1f} | "
              f"F6={eq_res['F6'][-1]['corr']:+.3f}/{eq_res['F6'][-1]['mae']:.1f}")

    # ═══════════════════════════════════════════════════════════
    # 8-CRITERIA SCORING
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("8-CRITERIA SCORING")
    print("=" * 80)

    for name in ['Scalene', 'Phi-obs', 'F9-flat', 'F6', 'F1']:
        res = all_results[name]
        eq_r = eq_res.get(name, eq_res.get('F6', []))

        avg_c = np.mean([r['corr'] for r in res])
        avg_d = np.mean([r['dir'] for r in res])
        avg_x = np.mean([r['x2'] for r in res])
        avg_m = np.mean([r['mae'] for r in res])

        nw = 0
        for i, sy in enumerate(splits):
            train = {y: v for y, v in ssn_data.items() if y <= sy}
            py = [y for y in all_ssn_years if y > sy and y <= 2025]
            if len(py) < 2: continue
            nm = np.mean([abs(ssn_data[py[j]]-ssn_data[py[j-1]]) for j in range(1,len(py))])
            if res[i]['mae'] < nm: nw += 1

        avg_eq_c = np.mean([r['corr'] for r in eq_r]) if eq_r else 0
        avg_eq_x = np.mean([r['x2'] for r in eq_r]) if eq_r else 0

        score = 0
        checks = []
        s1 = avg_c > 0.3; score += s1; checks.append(f"SSNc={avg_c:+.3f} {'PASS' if s1 else 'FAIL'}")
        s2 = nw >= 3; score += s2; checks.append(f"beats_naive={nw}/5 {'PASS' if s2 else 'FAIL'}")
        s3 = avg_x > 30; score += s3; checks.append(f"within_2x={avg_x:.1f}% {'PASS' if s3 else 'FAIL'}")
        s4 = avg_d > 55; score += s4; checks.append(f"direction={avg_d:.1f}% {'PASS' if s4 else 'FAIL'}")
        s5 = avg_eq_c > 0.2; score += s5; checks.append(f"EQc={avg_eq_c:+.3f} {'PASS' if s5 else 'FAIL'}")
        s6 = avg_eq_x > 30; score += s6; checks.append(f"EQ_2x={avg_eq_x:.1f}% {'PASS' if s6 else 'FAIL'}")
        s7 = nw >= 3; score += s7; checks.append(f"MAE_wins={nw}/5 {'PASS' if s7 else 'FAIL'}")
        drift = abs(res[-1]['corr'] - res[0]['corr']) < 0.5
        score += drift; checks.append(f"drift={'PASS' if drift else 'FAIL'}")

        print(f"\n  +{'='*58}+")
        print(f"  |  {name:<40s} {score}/8{' '*12}|")
        print(f"  +{'='*58}+")
        for ch in checks:
            print(f"    {ch}")

    # ═══════════════════════════════════════════════════════════
    # COMPARISON TABLE
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("RESOLUTION PROGRESSION — SCALENE TRIANGLE vs EVERYTHING")
    print("=" * 80)

    print(f"\n  {'Model':<16s} {'Avg Corr':>10s} {'Avg MAE':>10s} {'Avg Dir':>10s} {'Beats Sine':>12s}")
    print(f"  {'-'*14} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")

    for name in ['Scalene', 'F9-flat', 'F6', 'F1', 'Sine']:
        res = all_results[name]
        ac = np.mean([r['corr'] for r in res])
        am = np.mean([r['mae'] for r in res])
        ad = np.mean([r['dir'] for r in res])
        beats = sum(1 for r, s in zip(res, all_results['Sine']) if r['mae'] < s['mae'])
        print(f"  {name:<16s} {ac:+10.3f} {am:10.1f} {ad:10.1f}% {beats}/5 splits")

    sine_mae_avg = np.mean([r['mae'] for r in all_results['Sine']])
    scl_mae_avg = np.mean([r['mae'] for r in all_results['Scalene']])
    flat_mae_avg = np.mean([r['mae'] for r in all_results['F9-flat']])

    print(f"\n  Scalene MAE:   {scl_mae_avg:.1f}")
    print(f"  F9-flat MAE:   {flat_mae_avg:.1f}")
    print(f"  Sine MAE:      {sine_mae_avg:.1f}")

    if scl_mae_avg < sine_mae_avg:
        print(f"  *** SCALENE TRIANGLE BEATS THE SINE BASELINE ***")
        print(f"  Margin: {sine_mae_avg - scl_mae_avg:.1f} ({(sine_mae_avg - scl_mae_avg)/sine_mae_avg*100:.1f}% better)")
    else:
        gap = scl_mae_avg - sine_mae_avg
        pct = gap/sine_mae_avg*100
        print(f"  Scalene gap to sine: {gap:.1f} ({pct:.0f}% away)")

    po_mae_avg = np.mean([r['mae'] for r in all_results['Phi-obs']])

    print(f"\n  Phi-obs MAE:   {po_mae_avg:.1f}")

    # Per-split breakdown
    print()
    print("  Per-split MAE comparison:")
    print(f"    {'Split':>6s} {'Scalene':>10s} {'Phi-obs':>10s} {'F9-flat':>10s} {'Sine':>10s} {'Best ARA':>10s}")
    for i, sy in enumerate(splits):
        scl = all_results['Scalene'][i]['mae']
        po = all_results['Phi-obs'][i]['mae']
        flt = all_results['F9-flat'][i]['mae']
        sne = all_results['Sine'][i]['mae']
        best_ara = min(scl, po, flt)
        best_name = 'Scalene' if best_ara == scl else ('Phi-obs' if best_ara == po else 'F9-flat')
        w = "* BEATS SINE" if best_ara < sne else ""
        print(f"    {sy:>6d} {scl:10.1f} {po:10.1f} {flt:10.1f} {sne:10.1f} {best_name:>10s} {w}")

    print()
    print("=" * 80)
    print("Script 198 complete.")
    print("=" * 80)
