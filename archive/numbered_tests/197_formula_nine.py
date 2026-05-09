#!/usr/bin/env python3
"""
Script 197 — Formula⁹: Fractal Resolution with φ-Time
==============================================================================

Dylan's insight: "We need to increase the resolution of the formula.
Drill down with the ARA system further in all 3 directions.
It would travel along φ on time."

THE FRACTAL CLOCK:

    Each log level down in the ARA hierarchy runs φ× faster.
    Period cascades through φ:

    Parent level (F³):
        Dynamo:    P = 22 years (Hale cycle)
        Activity:  P/φ ≈ 13.6 years
        Reversal:  P/φ² ≈ 8.4 years

    Sub-level (F⁹ — each parent decomposes into 3):
        Dynamo subs:    22.0,  13.6,  8.4
        Activity subs:  13.6,   8.4,  5.2
        Reversal subs:   8.4,   5.2,  3.2

    This spans 22 years → 3.2 years, covering virtually every known
    solar periodicity. The overlapping periods (e.g. Dynamo-sub3 and
    Activity-sub1 both at 8.4) are natural resonance points — same
    clock speed, different ARA.

    Why φ and not harmonics (1/2, 1/3)?
    φ creates IRRATIONAL frequency ratios — they never lock into exact
    resonance, which prevents the sub-channels from phase-locking into
    a single drone. This is KAM theorem applied to the formula itself:
    the most persistent tori have the most irrational frequency ratios.

    Also testing: period/2 (octave) and period/3 (harmonic) for comparison.

ARCHITECTURE:

    9 engine sub-channels + 9 consumer sub-channels = 18 total
    Each with its own:
        - ARA (from parent decomposition)
        - Period (from φ cascade)
        - Phase (120° within sub-triad + parent offset)

    Coupling:
        Level 1: within sub-triad (π-leak, same parent)
        Level 2: between parents (π-leak × φ-leak)
        Level 3: engine ↔ consumer singularity gate (one-shot, φ/1/φ)
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
# φ-PERIOD CASCADE
# ═══════════════════════════════════════════════════════════════════

# Parent periods
P_PARENT = [HALE_PERIOD, HALE_PERIOD / PHI, HALE_PERIOD / PHI**2]
# ≈ [22.0, 13.6, 8.4]

# Sub-channel periods: each parent's 3 subs cascade by /φ
P_SUBS = []  # 9 periods
for parent_p in P_PARENT:
    for sub_idx in range(3):
        P_SUBS.append(parent_p / PHI**sub_idx)
# Dynamo: 22.0, 13.6, 8.4
# Activity: 13.6, 8.4, 5.2
# Reversal: 8.4, 5.2, 3.2

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

INTRA_SUB_COUPLING = PI_LEAK
INTER_SUB_COUPLING = PI_LEAK * PHI_LEAK
SING_DOWN = PHI
SING_UP = PHI_LEAK

ARA_SSN_SINGLE = 1.73
MIDOFF_SINGLE = abs((1.73 + 0.15) / 2 - R_COUPLER)

# ═══════════════════════════════════════════════════════════════════
# CORE WAVE MECHANICS (period-aware)
# ═══════════════════════════════════════════════════════════════════

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def effective_ara(ara_base, t, phase0, period):
    """ARA oscillates with the channel's OWN period."""
    center = 1.0
    amp = ara_base - center
    return center + amp * np.sin(2 * np.pi * t / period + phase0)

def base_wave_dlog(log_val, C, R_matter, step, t, phase0, midpoint_offset, period):
    """Wave mechanics with channel-specific period."""
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
# CHANNEL PREDICTION — PERIOD-AWARE
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
# F⁹ MODEL WITH φ-TIME
# ═══════════════════════════════════════════════════════════════════

class ARANinePhiTime:
    """
    18 coupled sub-channels, each with its own period from φ cascade.
    """

    def __init__(self, ara_eng_9, ara_con_9, periods_9, C, phase0_base):
        self.ara_eng = list(ara_eng_9)
        self.ara_con = list(ara_con_9)
        self.periods = list(periods_9)  # 9 distinct periods
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

    def init_from_observation(self, log_ssn):
        deviation = log_ssn - self.C
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

        # Phase 1: Independent predictions — each with its OWN period
        for i in range(self.N):
            new_eng[i], eng_valleys[i], eng_overflow[i] = engine_channel(
                self.eng_states[i], self.C, self.ara_eng[i],
                t, self.eng_phases[i], self.periods[i]
            )
            new_con[i], con_valleys[i], con_overflow[i] = consumer_channel(
                self.con_states[i], self.C, self.ara_con[i],
                t, self.con_phases[i], self.periods[i]
            )

        # Phase 2: Within-sub-triad coupling (Level 1)
        for parent_idx in range(3):
            base = parent_idx * 3
            for local in range(3):
                i = base + local
                upstream = base + (local - 1) % 3
                eng_disp = self.eng_states[upstream] - eng_valleys[upstream]
                new_eng[i] += INTRA_SUB_COUPLING * eng_disp
                con_disp = self.con_states[upstream] - con_valleys[upstream]
                new_con[i] += INTRA_SUB_COUPLING * con_disp

        # Phase 3: Between-parent coupling (Level 2)
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
                new_eng[dst_base + j] += INTER_SUB_COUPLING * src_eng_disp
                new_con[dst_base + j] += INTER_SUB_COUPLING * src_con_disp

        # Phase 4: Singularity gate (one-shot, φ/1/φ)
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

        # Phase 5: Cross-triad continuous coupling
        act_mean = np.mean([self.eng_states[3 + j] - eng_valleys[3 + j] for j in range(3)])
        acc_mean = np.mean([self.con_states[6 + j] - con_valleys[6 + j] for j in range(3)])
        for j in range(3):
            new_con[j] += INTER_SUB_COUPLING * act_mean
            new_eng[j] += INTER_SUB_COUPLING * acc_mean

        # Phase 6: Soft bounds
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
        CAM VALVE: fast sub-channels gate the slow channel's signal.
        Valve is tuned to the SYSTEM'S ARA, not φ.

        Slow channel (sub-0): carries the BASE SIGNAL through time.
        Fast channels (sub-1, sub-2): act as a VALVE (camshaft).

        The valve bounces in its own ARA-tuned valley:
            valley = C + engine_factor × depth × sin(2πt/period)
            displacement = fast_state - valley

        When fast channel is ABOVE its valley → valve OPEN → signal passes.
        When BELOW valley → valve CLOSED → signal blocked.

        Valve LIFT = engine_factor = max(ARA - 1, 0).
            Higher ARA = deeper valley = more dramatic swing = richer signal.
            Consumer ARA = flat valley = valve barely moves = flat output.

        This IS why engines produce rich oscillations and consumers flatline.
        The valve lift IS the ARA.
        """
        eng_parent_obs = []
        con_parent_obs = []

        for parent_idx in range(3):
            base = parent_idx * 3

            # ENGINE VALVE
            eng_base_signal = self.eng_states[base] - self.C  # Slow channel deviation

            # Fast channel valve states: compute valley, then displacement
            eng_valve = 1.0  # Default: fully open
            for sub_idx in [1, 2]:  # Middle and fastest sub-channels
                i = base + sub_idx
                fast_state = self.eng_states[i]
                fast_ara = self.ara_eng[i]
                engine_factor = max(fast_ara - 1.0, 0.0)

                # The valve's own ARA-tuned valley
                # (We don't know exact t here, so use state displacement from C
                #  as proxy — how far the valve is from neutral)
                fast_displacement = fast_state - self.C

                # Valve opening: proportional to how far ABOVE neutral
                # Scaled by engine_factor (ARA determines valve lift)
                # valve_position ranges from 0 (closed) to ~2 (wide open)
                valve_position = max(0.0, 1.0 + engine_factor * fast_displacement)
                eng_valve *= valve_position

            # Gated signal: base × valve
            eng_obs = self.C + eng_base_signal * eng_valve
            eng_parent_obs.append(eng_obs)

            # CONSUMER VALVE (reversed: consumer below neutral → valve open)
            con_base_signal = self.con_states[base] - self.C

            con_valve = 1.0
            for sub_idx in [1, 2]:
                i = base + sub_idx
                fast_state = self.con_states[i]
                fast_ara = self.ara_con[i]
                consumer_factor = max(1.0 - fast_ara, 0.0)

                fast_displacement = self.C - fast_state  # Reversed: below C = positive

                valve_position = max(0.0, 1.0 + consumer_factor * fast_displacement)
                con_valve *= valve_position

            con_obs = self.C + con_base_signal * con_valve
            con_parent_obs.append(con_obs)

        # System observable
        eng_s2 = eng_parent_obs[1]
        eng_s1_excess = eng_parent_obs[0] - self.C
        eng_s3_state = eng_parent_obs[2] - self.C
        con_stored = max(con_parent_obs[2] - self.C, 0)
        con_room = max(self.C - con_parent_obs[0], 0)

        engine_signal = eng_s2 + PI_LEAK * (eng_s1_excess + eng_s3_state) * 0.3
        consumer_feedback = PI_LEAK * (con_stored - con_room) * 0.5

        return engine_signal + consumer_feedback

# ═══════════════════════════════════════════════════════════════════
# F⁶ MODEL (from Script 196 — comparison)
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

        new_con[0] += INTER_SUB_COUPLING * (self.eng_states[1] - eng_v[1])
        new_eng[0] += INTER_SUB_COUPLING * (self.con_states[2] - con_v[2])

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
    """Generic phase calibration for any model."""
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
    print("SCRIPT 197 — FORMULA^9 WITH phi-TIME CASCADING PERIODS")
    print("=" * 80)
    print()
    print("Period cascade (phi-time):")
    for p_idx, pname in enumerate(["Dynamo", "Activity", "Reversal"]):
        base = p_idx * 3
        print(f"  {pname} (parent P={P_PARENT[p_idx]:.1f}y):")
        for s in range(3):
            i = base + s
            print(f"    Sub-{s+1}: ARA={ARA_ENG_9[i]:.3f}, Period={P_SUBS[i]:.1f}y")
    print()

    # Also build alternative period cascades for comparison
    # /2 (octave)
    P_SUBS_HALF = []
    for parent_p in P_PARENT:
        for sub_idx in range(3):
            P_SUBS_HALF.append(parent_p / 2**sub_idx)

    # /3 (harmonic)
    P_SUBS_THIRD = []
    for parent_p in P_PARENT:
        for sub_idx in range(3):
            P_SUBS_THIRD.append(parent_p / 3**sub_idx)

    # All same (control — like Script 197 v1)
    P_SUBS_SAME = [HALE_PERIOD] * 9

    models_to_test = {
        'F9-phi':    lambda C, p0: ARANinePhiTime(ARA_ENG_9, ARA_CON_9, P_SUBS, C, p0),
        'F9-half':   lambda C, p0: ARANinePhiTime(ARA_ENG_9, ARA_CON_9, P_SUBS_HALF, C, p0),
        'F9-third':  lambda C, p0: ARANinePhiTime(ARA_ENG_9, ARA_CON_9, P_SUBS_THIRD, C, p0),
        'F9-same':   lambda C, p0: ARANinePhiTime(ARA_ENG_9, ARA_CON_9, P_SUBS_SAME, C, p0),
        'F6':        lambda C, p0: ARALoopModel(ARA_ENG_PARENTS, ARA_CON_PARENTS, C, p0),
    }

    splits = [1989, 1994, 1999, 2004, 2009]
    all_results = {name: [] for name in models_to_test}
    all_results['F1'] = []
    all_results['Sine'] = []

    print("=" * 80)
    print("SUNSPOT PREDICTIONS — ALL MODELS")
    print("=" * 80)

    for split_year in splits:
        train = {y: v for y, v in ssn_data.items() if y <= split_year}
        pred_years = [y for y in all_ssn_years if y > split_year and y <= 2025]
        if not pred_years: continue

        C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
        start_year = max(train.keys())
        start_log = np.log10(max(ssn_data[start_year], 0.1))

        preds = {}

        # Test each model variant
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

        # Print split results
        n = len(pred_years)
        print(f"\n  Train <={split_year}, Predict {split_year+1}-2025 ({n} years)")
        print()
        print(f"  {'Model':<16s} {'Corr':>8s} {'Dir%':>8s} {'x2%':>8s} {'MAE':>8s}")
        print(f"  {'-'*14} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
        for name in ['F9-phi', 'F9-half', 'F9-third', 'F9-same', 'F6', 'F1', 'Sine']:
            ev = all_results[name][-1]
            print(f"  {name:<16s} {ev['corr']:+8.3f} {ev['dir']:8.1f} {ev['x2']:8.1f} {ev['mae']:8.1f}")

        # Year-by-year for key models
        print(f"\n  Year-by-year (first 15):")
        print(f"    {'Year':>6s} {'Actual':>8s} {'F9-phi':>8s} {'F6':>8s} {'F1':>8s} {'Sine':>8s}")
        for y in pred_years[:15]:
            print(f"    {y:>6d} {ssn_data[y]:8.1f} {preds['F9-phi'][y]:8.1f} {preds['F6'][y]:8.1f} {preds['F1'][y]:8.1f} {preds['Sine'][y]:8.1f}")

    # ═══════════════════════════════════════════════════════════
    # EARTHQUAKE
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("EARTHQUAKE — F9-phi vs F6")
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

    # EQ periods (different base — EQ has different dominant period)
    EQ_BASE_P = 30  # ~30 year seismic cycle
    P_EQ = []
    for pidx in range(3):
        pp = EQ_BASE_P / PHI**pidx
        for sidx in range(3):
            P_EQ.append(pp / PHI**sidx)

    eq_res_f9 = []
    eq_res_f6 = []

    for split_year in splits:
        eq_train = {y: v for y, v in eq_data.items() if y <= split_year}
        eq_pred = [y for y in all_eq_years if y > split_year and y <= 2024]
        if not eq_pred: continue

        C_eq = np.mean(np.log10([max(v, 0.1) for v in eq_train.values()]))
        se = max(eq_train.keys())
        sl = np.log10(max(eq_data[se], 0.1))

        # F9-phi EQ
        f9_fac = lambda C, p0: ARANinePhiTime(ARA_EQ_E9, ARA_EQ_C9, P_EQ, C, p0)
        ph = calibrate_model(eq_train, f9_fac)
        m = f9_fac(C_eq, ph)
        m.init_from_observation(sl)
        pq = {}
        for i, y in enumerate(eq_pred):
            m.step(i+1)
            pq[y] = max(10**m.observable_ssn(), 0)
        ev9 = evaluate(eq_data, pq, eq_pred)
        eq_res_f9.append(ev9)

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
        eq_res_f6.append(ev6)

        print(f"  <={split_year}: F9-phi Corr={ev9['corr']:+.3f}, Dir={ev9['dir']:.1f}%, MAE={ev9['mae']:.1f} | "
              f"F6 Corr={ev6['corr']:+.3f}, MAE={ev6['mae']:.1f}")

    # ═══════════════════════════════════════════════════════════
    # 8-CRITERIA SCORING
    # ═══════════════════════════════════════════════════════════

    print()
    print("=" * 80)
    print("8-CRITERIA SCORING")
    print("=" * 80)

    for name in ['F9-phi', 'F9-half', 'F9-third', 'F9-same', 'F6', 'F1']:
        res = all_results[name]
        sine = all_results['Sine']
        eq_r = eq_res_f9 if 'F9' in name else eq_res_f6

        avg_c = np.mean([r['corr'] for r in res])
        avg_d = np.mean([r['dir'] for r in res])
        avg_x = np.mean([r['x2'] for r in res])
        avg_m = np.mean([r['mae'] for r in res])

        # Beats naive
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
    print("RESOLUTION PROGRESSION — ALL PERIOD CASCADES")
    print("=" * 80)

    print(f"\n  {'Model':<16s} {'Avg Corr':>10s} {'Avg MAE':>10s} {'Avg Dir':>10s} {'vs Sine MAE':>12s}")
    print(f"  {'-'*14} {'-'*10} {'-'*10} {'-'*10} {'-'*12}")

    for name in ['F9-phi', 'F9-half', 'F9-third', 'F9-same', 'F6', 'F1', 'Sine']:
        res = all_results[name]
        ac = np.mean([r['corr'] for r in res])
        am = np.mean([r['mae'] for r in res])
        ad = np.mean([r['dir'] for r in res])
        sine_mae = np.mean([r['mae'] for r in all_results['Sine']])
        beats = sum(1 for r, s in zip(res, all_results['Sine']) if r['mae'] < s['mae'])
        print(f"  {name:<16s} {ac:+10.3f} {am:10.1f} {ad:10.1f}% {beats}/5")

    sine_mae_avg = np.mean([r['mae'] for r in all_results['Sine']])
    phi_mae_avg = np.mean([r['mae'] for r in all_results['F9-phi']])

    print(f"\n  phi-cascade MAE: {phi_mae_avg:.1f}")
    print(f"  Sine MAE:        {sine_mae_avg:.1f}")
    if phi_mae_avg < sine_mae_avg:
        print(f"  *** F9-phi BEATS THE SINE BASELINE ***")
    else:
        gap = phi_mae_avg - sine_mae_avg
        print(f"  Gap: {gap:.1f} ({gap/sine_mae_avg*100:.0f}% away)")

    print()
    print("=" * 80)
    print("Script 197 complete.")
    print("=" * 80)
