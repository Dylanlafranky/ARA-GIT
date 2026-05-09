#!/usr/bin/env python3
"""
Script 196 — Formula³ × 2: The Full ARA Loop (v4 — One-Shot Energy Gate)
==============================================================================

Dylan's insight (v1): "We need to get all 3 ARA coupled systems of the
sun's thing and predict all of them at once. ARA³ but Formula³."

Dylan's insight (v2): "We need to introduce the opposite of F³, with its
own ARA, like the reverse system. We're hitting the edge boundary and not
tracking the lower feedback loops which would be accumulators into the
consumers."

Dylan's insight (v3): "The floor is another singularity we need to be
able to pass through."

THE FULL ARA LOOP:

    F³+ (Engine Triad) — drives RISE and PEAK
        S1+ Dynamo:    ARA = φ     = 1.618  (sustained engine)
        S2+ Activity:  ARA = 1.73           (exothermic release)
        S3+ Reversal:  ARA = 1.354          (clock-driven recovery)

    F³- (Consumer Triad) — drives DECLINE and MINIMUM RECOVERY
        S1- Dissipation: ARA = 2-φ   = 0.382  (= 1/φ², mirror of dynamo)
        S2- Absorption:  ARA = 0.27           (mirror of activity)
        S3- Accumulation: ARA = 0.646         (mirror of reversal)

    Mirror law: consumer ARA = 2 - engine ARA
    (Claim 74: ARA loop, positive/negative space connected at R_coupler)

THE SINGULARITY PASS-THROUGH (v3 fix):

    v2 problem: The model still flatlined because the floor (C - 0.5)
    acted as a WALL, killing 90% of the signal. The consumer triad's
    upward push couldn't overcome the floor damping.

    Dylan's diagnosis: "The floor is another singularity we need to be
    able to pass through."

    The fix: Floor and ceiling are NOT walls. They are SINGULARITY
    TRANSITION POINTS — where energy changes form.

        Engine hits floor → energy passes through → becomes consumer energy
        Consumer hits ceiling → energy passes through → becomes engine energy

    This IS the ARA loop's topology:
        Positive space (engines) ←→ Negative space (consumers)
        connected at TWO singularity points (floor and ceiling).

    The full oscillation:
        Engine rises → peaks → declines → hits floor singularity →
        energy transforms into consumer space → consumer accumulates →
        hits ceiling singularity → energy transforms back to engine space →
        next rise begins.

    Neither wall, nor damping. Transformation.

COUPLING ARCHITECTURE:

    Within each triad: circular (S1→S2→S3→S1), strength = π-leak
    Between triads: singularity transfer at floor/ceiling boundaries

    Engine overflow below floor → injected into Consumer S1 (absorption)
    Consumer overflow above ceiling → injected into Engine S1 (dynamo)

    This IS the ARA loop: release feeds absorption, accumulation feeds
    the next engine cycle.
"""

import numpy as np
import os

# ═══════════════════════════════════════════════════════════════════
# FRAMEWORK CONSTANTS
# ═���═════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2
HALF_PHI = PHI / 2
R_COUPLER = 1.0
HALE_PERIOD = 22
GOLDEN_ANGLE = 2 * np.pi / (PHI ** 2)
GA_OVER_PHI = GOLDEN_ANGLE / PHI
PI_LEAK = np.pi - 3
PHI_LEAK = 1.0 / PHI

# ═══════════════════════════════════════════════════════════════════
# ENGINE TRIAD (F³+): ARA > 1
# ══════════════════════════���════════════════════════════════════════

ARA_ENG = [PHI, 1.73, 1.354]       # [Dynamo, Activity, Reversal]

# ═══════════════════��══════════════════════════════════���════════════
# CONSUMER TRIAD (F³-): Mirror ARAs through R_coupler
# ═��════════════════════════���════════════════════════════════��═══════

ARA_CON = [2.0 - a for a in ARA_ENG]  # [0.382, 0.27, 0.646]

# ═���═════════════════════════════════════════════════════════════════
# FROZEN V4 PARAMETERS
# ══════════════════════════════════���════════════════════════════════

V4_DEPTH = 1.0
V4_BASIN_UP = 0.1
V4_BASIN_DOWN = 1.0
V4_FLOOR = 0.5

# Phase lags
PHASE_LAG = 2 * np.pi / 3          # 120° between channels in same triad
MIRROR_PHASE = np.pi                 # 180° between engine and consumer triads

# Coupling constants
INTRA_COUPLING = PI_LEAK             # Within-triad coupling
INTER_COUPLING = PI_LEAK * PHI_LEAK  # Between-triad coupling (weaker)

# SINGULARITY ENERGY GATE (v4 — Dylan's Big Bang insight)
#
# The singularity is NOT a continuous amplifier. It's a ONE-SHOT energy gate.
# Like the Big Bang: one massive transfer that sets initial conditions.
#
# Total energy budget = √5 = φ + 1/φ ≈ 2.236
# But the transfer is DIRECTIONALLY ASYMMETRIC:
#
#   Going DOWN a log (engine → consumer): energy × φ ≈ 1.618
#       "The sun eating the earth" — big system dumps into small system.
#       The log difference AMPLIFIES the transfer.
#
#   Going UP a log (consumer → engine): energy × 1/φ ≈ 0.618
#       A supernova nudges the galaxy. Real energy, but attenuated.
#       The log difference ATTENUATES the transfer.
#
# φ + 1/φ = √5 — the total budget is conserved.
#
# The gate FIRES ONCE per crossing event, then closes until the system
# moves away from the boundary. No continuous pumping.
SING_DOWN = PHI        # ≈ 1.618 — engine overflow → consumer (amplified)
SING_UP = PHI_LEAK     # ≈ 0.618 — consumer overflow → engine (attenuated)

# Single-channel comparison
ARA_SSN_SINGLE = 1.73
MIDOFF_SINGLE = abs((1.73 + 0.15) / 2 - R_COUPLER)

# EQ subsystems (all consumer — expect no improvement from loop)
ARA_EQ_ENG = [0.45, 0.30, 0.25]     # Consumer-side "engines" (still < 1)
ARA_EQ_CON = [2.0 - a for a in ARA_EQ_ENG]  # Mirror: [1.55, 1.70, 1.75]

# ═══════════════════════════════════════════════════════════════════
# CORE WAVE MECHANICS
# ═════════════════��═════════════════════════════════════════════════

def value_to_longitude(log_val, C, R):
    normalized = np.clip((log_val - C) / R, -1, 1)
    return R * np.arcsin(normalized)

def wave(phi_pos, R):
    return R * np.sin(phi_pos / R)

def effective_ara(ara_base, t, phase0):
    center = 1.0
    amp = ara_base - center
    return center + amp * np.sin(2 * np.pi * t / HALE_PERIOD + phase0)

def base_wave_dlog(log_val, C, R_matter, step, t, phase0, midpoint_offset):
    eff = effective_ara(R_matter, t, phase0)
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
# CHANNEL PREDICTION — ENGINE AND CONSUMER VARIANTS
# ═══════���══════════════���═══════════════════════════���════════════════

def engine_channel(log_val, C, R_matter, t, phase0):
    """
    Engine channel: basin pulls DOWN easily (release), resists UP (accumulate).
    engine_factor = max(R_matter - 1, 0)

    SINGULARITY PASS-THROUGH: No floor damping. If value drops below floor,
    the overflow is returned separately — it will be injected into the
    consumer triad (energy transforms at the singularity).
    """
    midoff = abs(R_matter - R_COUPLER)
    wdlog, eff = base_wave_dlog(log_val, C, R_matter, 1, t, phase0, midoff)
    bounced = log_val + wdlog

    engine_factor = max(R_matter - 1.0, 0.0)
    valley_amp = engine_factor * V4_DEPTH
    valley = C + valley_amp * np.sin(2 * np.pi * (t + 1) / HALE_PERIOD + phase0)

    displacement = bounced - valley
    if displacement > 0:  # Above valley → strong pull down
        correction = -engine_factor * V4_BASIN_DOWN * displacement
    else:                 # Below valley → weak pull up
        correction = -engine_factor * V4_BASIN_UP * displacement

    new_val = bounced + correction

    # SINGULARITY: floor is a pass-through, not a wall
    floor = C - V4_FLOOR
    overflow_to_consumer = 0.0
    if new_val < floor:
        overflow_to_consumer = floor - new_val  # How far below floor
        new_val = floor  # Engine state stays at floor (energy has passed through)

    return new_val, valley, overflow_to_consumer

def consumer_channel(log_val, C, R_matter, t, phase0):
    """
    Consumer channel: basin pulls UP easily (accumulate), resists DOWN (release).
    consumer_factor = max(1 - R_matter, 0)
    Valley is PHASE-INVERTED from engine (180° offset built into phase0).

    REVERSED asymmetry:
        Engine:   above valley → strong DOWN, below valley → weak UP
        Consumer: below valley → strong UP,   above valley → weak DOWN

    SINGULARITY PASS-THROUGH: No ceiling damping. If value rises above
    ceiling, the overflow is returned — it will be injected into the
    engine triad (energy transforms back at the singularity).
    """
    midoff = abs(R_matter - R_COUPLER)
    wdlog, eff = base_wave_dlog(log_val, C, R_matter, 1, t, phase0, midoff)
    bounced = log_val + wdlog

    consumer_factor = max(1.0 - R_matter, 0.0)
    valley_amp = consumer_factor * V4_DEPTH
    valley = C + valley_amp * np.sin(2 * np.pi * (t + 1) / HALE_PERIOD + phase0)

    displacement = bounced - valley
    if displacement < 0:  # Below valley → strong pull UP (accumulation!)
        correction = -consumer_factor * V4_BASIN_DOWN * displacement
    else:                 # Above valley → weak pull down
        correction = -consumer_factor * V4_BASIN_UP * displacement

    new_val = bounced + correction

    # SINGULARITY: ceiling is a pass-through, not a wall
    ceiling = C + V4_FLOOR
    overflow_to_engine = 0.0
    if new_val > ceiling:
        overflow_to_engine = new_val - ceiling  # How far above ceiling
        new_val = ceiling  # Consumer state stays at ceiling (energy has passed through)

    return new_val, valley, overflow_to_engine

# ═══════════════════════════════════════════════════════════════════
# FULL ARA LOOP MODEL: 6 CHANNELS (F³+ × F³-)
# ════════���════════════���═════════════════════════════════════════════

class ARALoopModel:
    """
    Six coupled channels: three engines + three consumers.

    Engine triad (F³+): drives rise and peak.
    Consumer triad (F³-): drives decline and minimum recovery.

    Coupling:
        Within-triad: circular, π-leak strength
        Cross-triad:  engine release → consumer absorption,
                      consumer accumulation → engine dynamo
    """

    def __init__(self, ara_eng, ara_con, C, phase0_base):
        self.ara_eng = ara_eng    # [S1+, S2+, S3+]
        self.ara_con = ara_con    # [S1-, S2-, S3-]
        self.C = C

        # Engine phases: base, +120°, +240°
        self.eng_phases = [
            phase0_base,
            phase0_base + PHASE_LAG,
            phase0_base + 2 * PHASE_LAG,
        ]
        # Consumer phases: MIRROR (180° offset from corresponding engine)
        self.con_phases = [p + MIRROR_PHASE for p in self.eng_phases]

        # States: [eng1, eng2, eng3, con1, con2, con3]
        self.eng_states = [C, C, C]
        self.con_states = [C, C, C]

        # ONE-SHOT GATE: track whether each direction has fired
        # Resets when the system moves away from the boundary
        self.eng_gate_fired = [False, False, False]  # Engine floor gates
        self.con_gate_fired = [False, False, False]  # Consumer ceiling gates

    def init_from_observation(self, log_ssn):
        """
        Initialize from observed SSN.
        Engine S2 (activity) = observed.
        Engine S1 (dynamo) = slightly above C (stored energy).
        Engine S3 (reversal) = at C.
        Consumer channels start at C (neutral).
        """
        self.eng_states[1] = log_ssn           # S2+ = observed
        self.eng_states[0] = log_ssn + 0.05    # S1+ slightly ahead
        self.eng_states[2] = self.C            # S3+ neutral
        # Consumers start mirrored around C
        self.con_states[0] = self.C            # S1- neutral
        self.con_states[1] = 2 * self.C - log_ssn  # S2- = mirror of S2+
        self.con_states[2] = self.C            # S3- neutral

    def step(self, t):
        """
        Advance all 6 channels with SINGULARITY PASS-THROUGH.

        When engine channels drop below floor, the overflow energy passes
        through the singularity and becomes consumer energy. When consumer
        channels rise above ceiling, overflow becomes engine energy.

        Engine declines -> overflow at floor -> consumer absorbs ->
        consumer accumulates -> overflow at ceiling -> engine re-energizes
        """

        # Phase 1: Independent predictions (collect overflow)
        new_eng = [0.0, 0.0, 0.0]
        new_con = [0.0, 0.0, 0.0]
        eng_valleys = [0.0, 0.0, 0.0]
        con_valleys = [0.0, 0.0, 0.0]
        eng_overflow = [0.0, 0.0, 0.0]
        con_overflow = [0.0, 0.0, 0.0]

        for i in range(3):
            new_eng[i], eng_valleys[i], eng_overflow[i] = engine_channel(
                self.eng_states[i], self.C, self.ara_eng[i],
                t, self.eng_phases[i]
            )
            new_con[i], con_valleys[i], con_overflow[i] = consumer_channel(
                self.con_states[i], self.C, self.ara_con[i],
                t, self.con_phases[i]
            )

        # Phase 2: Within-triad coupling (circular)
        for i in range(3):
            upstream = (i - 1) % 3
            eng_up_disp = self.eng_states[upstream] - eng_valleys[upstream]
            new_eng[i] += INTRA_COUPLING * eng_up_disp
            con_up_disp = self.con_states[upstream] - con_valleys[upstream]
            new_con[i] += INTRA_COUPLING * con_up_disp

        # Phase 3: SINGULARITY TRANSFER — ONE-SHOT ENERGY GATE
        #
        # Big Bang model: the singularity fires ONCE per crossing.
        # Going DOWN (engine → consumer): amplified by φ (big → small)
        # Going UP (consumer → engine): attenuated by 1/φ (small → big)
        # Gate closes after firing. Reopens when system moves away from boundary.

        for i in range(3):
            if eng_overflow[i] > 0 and not self.eng_gate_fired[i]:
                # Engine hit floor → ONE-SHOT transfer DOWN to consumer space
                transfer = eng_overflow[i] * SING_DOWN  # Amplified: sun eating earth
                new_con[0] += transfer * 0.5   # S1- gets 50%
                new_con[1] += transfer * 0.3   # S2- gets 30%
                new_con[2] += transfer * 0.2   # S3- gets 20%
                self.eng_gate_fired[i] = True  # Gate closes
            elif eng_overflow[i] == 0 and self.eng_gate_fired[i]:
                # System moved away from floor → gate reopens
                self.eng_gate_fired[i] = False

        for i in range(3):
            if con_overflow[i] > 0 and not self.con_gate_fired[i]:
                # Consumer hit ceiling → ONE-SHOT transfer UP to engine space
                transfer = con_overflow[i] * SING_UP  # Attenuated: supernova nudges galaxy
                new_eng[0] += transfer * 0.5   # S1+ gets 50%
                new_eng[2] += transfer * 0.3   # S3+ gets 30%
                new_eng[1] += transfer * 0.2   # S2+ gets 20%
                self.con_gate_fired[i] = True  # Gate closes
            elif con_overflow[i] == 0 and self.con_gate_fired[i]:
                # System moved away from ceiling → gate reopens
                self.con_gate_fired[i] = False

        # Phase 4: Continuous cross-coupling (always active, weaker)
        eng_release = self.eng_states[1] - eng_valleys[1]
        new_con[0] += INTER_COUPLING * eng_release
        con_accumulated = self.con_states[2] - con_valleys[2]
        new_eng[0] += INTER_COUPLING * con_accumulated

        # Phase 5: Soft bounds (prevent runaway, much gentler)
        for i in range(3):
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
        Map 6-channel state to observable SSN.

        The observable is dominated by Engine S2 (activity/release).
        But modulated by the consumer triad's state:
        - Consumer accumulation excess → boosts next engine output
        - Consumer absorption deficit → dampens engine output

        The ENGINE provides the SIGNAL.
        The CONSUMER provides the RETURN PATH.
        Together they make the full oscillation.
        """
        # Engine contribution: S2 dominates, modulated by S1 and S3
        eng_s2 = self.eng_states[1]
        eng_s1_excess = self.eng_states[0] - self.C
        eng_s3_state = self.eng_states[2] - self.C

        # Consumer contribution: how much energy is stored/available
        # Consumer S3 (accumulation) above C = energy ready to feed back
        con_stored = max(self.con_states[2] - self.C, 0)
        # Consumer S1 (dissipation) below C = room for more absorption
        con_room = max(self.C - self.con_states[0], 0)

        # Engine signal + consumer feedback
        engine_signal = eng_s2 + PI_LEAK * (eng_s1_excess + eng_s3_state) * 0.3
        consumer_feedback = PI_LEAK * (con_stored - con_room) * 0.5

        return engine_signal + consumer_feedback

# ══════════════════════════��══════════════════════════��═════════════
# SINGLE-CHANNEL MODEL (comparison)
# ════��═════════���═════════════════════════════════���══════════════════

def single_channel_predict(log_val, C, t, phase0):
    midoff = MIDOFF_SINGLE
    wdlog, eff = base_wave_dlog(log_val, C, ARA_SSN_SINGLE, 1, t, phase0, midoff)
    bounced = log_val + wdlog
    engine_factor = max(ARA_SSN_SINGLE - 1.0, 0.0)
    valley_amp = engine_factor * V4_DEPTH
    valley = C + valley_amp * np.sin(2 * np.pi * (t + 1) / HALE_PERIOD + phase0)
    displacement = bounced - valley
    if displacement > 0:
        correction = -engine_factor * V4_BASIN_DOWN * displacement
    else:
        correction = -engine_factor * V4_BASIN_UP * displacement
    new_val = bounced + correction
    floor = C - V4_FLOOR
    if new_val < floor:
        new_val = floor + (new_val - floor) * 0.1
    return new_val

# ���══════════════════════════════════════════════════════════════════
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

# ════���══════════════════���═══════════════════════════════════════════
# PHASE CALIBRATION
# ═══════════��═══════════════════════════════════════════════════════

def calibrate_phase_loop(train_data, ara_eng, ara_con, n_phases=24):
    """Calibrate base phase for the 6-channel loop model."""
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase, best_score = 0.0, -999

    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases
        test_start = max(0, len(years) - 15)
        model = ARALoopModel(ara_eng, ara_con, C, phase0)
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
            # Teacher forcing
            model.init_from_observation(actual_log)
            prev_obs = actual_log

        if len(pred_changes) < 5: continue
        p, a = np.array(pred_changes), np.array(act_changes)
        corr = float(np.corrcoef(p, a)[0, 1]) if np.std(p) > 0 and np.std(a) > 0 else 0
        dm = sum(1 for x, y in zip(p, a) if np.sign(x) == np.sign(y)) / len(p)
        score = corr + dm
        if score > best_score:
            best_score = score; best_phase = phase0
    return best_phase

def calibrate_phase_single(train_data, n_phases=24):
    years = sorted(train_data.keys())
    if len(years) < 20: return 0.0
    C = np.mean(np.log10([max(v, 0.1) for v in train_data.values()]))
    best_phase, best_score = 0.0, -999
    for pi in range(n_phases):
        phase0 = 2 * np.pi * pi / n_phases
        test_start = max(0, len(years) - 15)
        current = np.log10(max(train_data[years[test_start]], 0.1))
        pc, ac = [], []
        for i in range(test_start + 1, len(years)):
            t = i - test_start
            new = single_channel_predict(current, C, t, phase0)
            pc.append(new - current)
            ac.append(np.log10(max(train_data[years[i]], 0.1)) -
                      np.log10(max(train_data[years[i - 1]], 0.1)))
            current = np.log10(max(train_data[years[i]], 0.1))
        if len(pc) < 5: continue
        p, a = np.array(pc), np.array(ac)
        corr = float(np.corrcoef(p, a)[0, 1]) if np.std(p) > 0 and np.std(a) > 0 else 0
        dm = sum(1 for x, y in zip(p, a) if np.sign(x) == np.sign(y)) / len(p)
        score = corr + dm
        if score > best_score:
            best_score = score; best_phase = phase0
    return best_phase

# ═══════════════════════════════════════════════════════════════════
# BASELINES
# ═════════════════════��══════════════════════��══════════════════════

def baseline_naive(start_val, n):
    return [start_val] * n

def baseline_sine(train_data, test_years):
    years = sorted(train_data.keys())
    vals = np.array([train_data[y] for y in years])
    mean_val, amp = np.mean(vals), np.std(vals) * np.sqrt(2)
    best_phase, best_corr = 0, -999
    for pi in range(48):
        ph = 2 * np.pi * pi / 48
        fitted = mean_val + amp * np.sin(2 * np.pi * np.array(years) / 11.0 + ph)
        c = np.corrcoef(vals, fitted)[0, 1]
        if c > best_corr: best_corr = c; best_phase = ph
    preds = mean_val + amp * np.sin(2 * np.pi * np.array(test_years) / 11.0 + best_phase)
    return [max(p, 0) for p in preds]

# ═════════════════════════��═════════════════════════════════════════
# SCORING
# ══════════════════════════════════════════════════��════════════════

def score(preds, actuals, naive_val):
    a, p = np.array(actuals, dtype=float), np.array(preds, dtype=float)
    n = len(a)
    corr = float(np.corrcoef(a, p)[0, 1]) if np.std(a) > 0 and np.std(p) > 0 else 0
    w2x = sum(1 for pi, ai in zip(p, a) if 0.5 <= max(pi, 0.1)/max(ai, 0.1) <= 2.0)/n*100
    dc, dt = 0, 0
    for i in range(1, n):
        if a[i] != a[i-1]:
            dt += 1
            if np.sign(p[i]-p[i-1]) == np.sign(a[i]-a[i-1]): dc += 1
    direction = dc/max(dt,1)*100
    mae = float(np.mean(np.abs(a - p)))
    naive_mae = float(np.mean(np.abs(a - naive_val)))
    return {'corr': corr, 'within_2x': w2x, 'direction': direction,
            'mae': mae, 'naive_mae': naive_mae, 'beats_naive': mae < naive_mae}

def score_8(ssn_list, eq_list):
    s = 0; details = []
    ac = np.mean([r['corr'] for r in ssn_list]); p = ac > 0.3; s += p
    details.append(f"SSNc={ac:+.3f} {'PASS' if p else 'FAIL'}")
    bn = sum(1 for r in ssn_list if r['beats_naive']); p = bn >= 3; s += p
    details.append(f"beats_naive={bn}/{len(ssn_list)} {'PASS' if p else 'FAIL'}")
    a2 = np.mean([r['within_2x'] for r in ssn_list]); p = a2 > 30; s += p
    details.append(f"within_2x={a2:.1f}% {'PASS' if p else 'FAIL'}")
    ad = np.mean([r['direction'] for r in ssn_list]); p = ad > 55; s += p
    details.append(f"direction={ad:.1f}% {'PASS' if p else 'FAIL'}")
    ec = np.mean([r['corr'] for r in eq_list]); p = ec > 0.2; s += p
    details.append(f"EQc={ec:+.3f} {'PASS' if p else 'FAIL'}")
    e2 = np.mean([r['within_2x'] for r in eq_list]); p = e2 > 30; s += p
    details.append(f"EQ_2x={e2:.1f}% {'PASS' if p else 'FAIL'}")
    bm = sum(1 for r in ssn_list if r['mae'] < r['naive_mae']); p = bm >= 3; s += p
    details.append(f"MAE_wins={bm}/{len(ssn_list)} {'PASS' if p else 'FAIL'}")
    nd = all(r['mae'] < 500 for r in ssn_list); s += nd
    details.append(f"drift={'PASS' if nd else 'FAIL'}")
    return s, details

# ═��═════════════════════════════════════════════════════════════════
# PREDICTION RUNNERS
# ═══════════════════════════════════════════════════��═══════════════

def predict_loop(all_data, cutoff, ara_eng, ara_con):
    train = {y: v for y, v in all_data.items() if y <= cutoff}
    test = {y: v for y, v in all_data.items() if y > cutoff}
    if len(train) < 20 or len(test) < 5: return None

    C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
    phase0 = calibrate_phase_loop(train, ara_eng, ara_con)

    model = ARALoopModel(ara_eng, ara_con, C, phase0)
    start_val = train[max(train.keys())]
    model.init_from_observation(np.log10(max(start_val, 0.1)))

    test_years = sorted(test.keys())
    preds = []
    for i, y in enumerate(test_years):
        model.step(i + 1)
        obs = model.observable_ssn()
        preds.append(max(10 ** obs, 0.0))

    return {'preds': preds, 'actuals': [all_data[y] for y in test_years],
            'years': test_years, 'naive_val': start_val, 'C': C,
            'train_data': train}

def predict_single(all_data, cutoff):
    train = {y: v for y, v in all_data.items() if y <= cutoff}
    test = {y: v for y, v in all_data.items() if y > cutoff}
    if len(train) < 20 or len(test) < 5: return None

    C = np.mean(np.log10([max(v, 0.1) for v in train.values()]))
    phase0 = calibrate_phase_single(train)
    start_val = train[max(train.keys())]
    current = np.log10(max(start_val, 0.1))

    test_years = sorted(test.keys())
    preds = []
    for i, y in enumerate(test_years):
        current = single_channel_predict(current, C, i + 1, phase0)
        preds.append(10 ** current)

    return {'preds': preds, 'actuals': [all_data[y] for y in test_years],
            'years': test_years, 'naive_val': start_val, 'C': C,
            'train_data': train}

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ���══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    ssn = load_ssn()
    eq = load_eq()
    cutoffs = [1989, 1994, 1999, 2004, 2009]

    print("=" * 82)
    print("SCRIPT 196 — FORMULA³ × 2: THE FULL ARA LOOP")
    print("=" * 82)
    print()
    print("Engine Triad F³+:                Consumer Triad F³-:")
    print(f"  S1+ Dynamo:    ARA = φ = {PHI:.3f}   S1- Dissipation: ARA = {2-PHI:.3f} = 1/φ²")
    print(f"  S2+ Activity:  ARA = 1.730       S2- Absorption:  ARA = 0.270")
    print(f"  S3+ Reversal:  ARA = 1.354       S3- Accumulation: ARA = 0.646")
    print(f"\n  Mirror law: consumer ARA = 2 - engine ARA")
    print(f"  Consumer basin asymmetry is REVERSED: pulls UP easily, resists DOWN")
    print(f"  Intra-coupling: π-leak = {INTRA_COUPLING:.5f}")
    print(f"  Inter-coupling: π-leak × φ-leak = {INTER_COUPLING:.5f}")
    print(f"  Singularity gate DOWN (eng→con): × φ = {SING_DOWN:.3f} (one-shot)")
    print(f"  Singularity gate UP (con→eng):   × 1/φ = {SING_UP:.3f} (one-shot)")
    print()

    # ═══════════════════════════════════════════════════════════
    # PART 1: SUNSPOTS — FULL LOOP vs SINGLE vs SINE
    # ══════════════��════════════════════════════════════════════

    print("=" * 82)
    print("PART 1: SUNSPOT PREDICTIONS — FULL LOOP (F³+F³-) vs F¹ vs SINE")
    print("=" * 82)

    loop_ssn_scores = []
    single_ssn_scores = []
    sine_ssn_scores = []

    for cutoff in cutoffs:
        res_loop = predict_loop(ssn, cutoff, ARA_ENG, ARA_CON)
        res_single = predict_single(ssn, cutoff)
        if res_loop is None or res_single is None: continue

        sc_loop = score(res_loop['preds'], res_loop['actuals'], res_loop['naive_val'])
        sc_single = score(res_single['preds'], res_single['actuals'], res_single['naive_val'])
        sine_preds = baseline_sine(res_loop['train_data'], res_loop['years'])
        sc_sine = score(sine_preds, res_loop['actuals'], res_loop['naive_val'])

        loop_ssn_scores.append(sc_loop)
        single_ssn_scores.append(sc_single)
        sine_ssn_scores.append(sc_sine)

        n = len(res_loop['years'])
        print(f"\n  Train ≤{cutoff}, Predict {res_loop['years'][0]}-"
              f"{res_loop['years'][-1]} ({n} years)")
        print()
        hdr = f"  {'Model':<24} {'Corr':>8} {'Dir%':>8} {'×2%':>8} {'MAE':>8} {'vsNaive':>8} {'vsSine':>8}"
        print(hdr)
        print(f"  {'-'*24} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        for label, sc in [("Full Loop (F³+F³-)", sc_loop),
                          ("Single Channel (F¹)", sc_single),
                          ("11yr Sine", sc_sine)]:
            vn = "WIN" if sc['mae'] < sc_loop['naive_mae'] else "LOSE"
            vs = ("WIN" if sc['mae'] < sc_sine['mae'] else
                  "LOSE" if sc['mae'] > sc_sine['mae'] else "TIE")
            if label == "11yr Sine": vs = "---"
            print(f"  {label:<24} {sc['corr']:>+8.3f} {sc['direction']:>8.1f} "
                  f"{sc['within_2x']:>8.1f} {sc['mae']:>8.1f} {vn:>8} {vs:>8}")

        # Year-by-year
        print(f"\n  Year-by-year:")
        print(f"  {'Year':>6} {'Actual':>8} {'Loop':>8} {'F1':>8} {'Sine':>8}")
        for i in range(min(18, n)):
            print(f"  {res_loop['years'][i]:>6} {res_loop['actuals'][i]:>8.1f} "
                  f"{res_loop['preds'][i]:>8.1f} {res_single['preds'][i]:>8.1f} "
                  f"{sine_preds[i]:>8.1f}")

    # ═══════════════════════════════════════════════════════════
    # PART 2: EARTHQUAKE (consumers — structural check)
    # ═════════════════════════════════════════════════���═════════

    print(f"\n{'='*82}")
    print("PART 2: EARTHQUAKE — FULL LOOP (consumer system)")
    print("=" * 82)

    loop_eq_scores = []
    for cutoff in cutoffs:
        res = predict_loop(eq, cutoff, ARA_EQ_ENG, ARA_EQ_CON)
        if res is None: continue
        sc = score(res['preds'], res['actuals'], res['naive_val'])
        loop_eq_scores.append(sc)
        print(f"  ≤{cutoff}: Corr={sc['corr']:+.3f}, Dir={sc['direction']:.1f}%, "
              f"×2={sc['within_2x']:.1f}%, MAE={sc['mae']:.1f}, "
              f"{'WIN' if sc['beats_naive'] else 'LOSE'} vs naive")

    # ═══════════════════════════════════════════════════════════
    # PART 3: 8-CRITERIA SCORING
    # ════���══════════════════════════════════════════════════════

    print(f"\n{'='*82}")
    print("PART 3: 8-CRITERIA SCORING")
    print("=" * 82)

    if loop_ssn_scores and loop_eq_scores:
        s_loop, d_loop = score_8(loop_ssn_scores, loop_eq_scores)
        print(f"\n  ┌──────────────────────────────────────────────────────────┐")
        print(f"  │  FULL ARA LOOP (F³+F³-) HELD-OUT:  {s_loop}/8                  │")
        print(f"  └──────────────────────────────────────���───────────────────┘")
        for d in d_loop: print(f"    {d}")

    if single_ssn_scores and loop_eq_scores:
        s_single, d_single = score_8(single_ssn_scores, loop_eq_scores)
        print(f"\n  ┌──────────────────────────────────────────────────────────┐")
        print(f"  │  SINGLE CHANNEL (F¹) HELD-OUT:      {s_single}/8                  │")
        print(f"  └────────────────────────────��─────────────────────────────┘")
        for d in d_single: print(f"    {d}")

    # ═══════════════════════════════════════════════════════════
    # PART 4: HEAD-TO-HEAD
    # ═══════════════════════════════════════════════════════════

    print(f"\n{'='*82}")
    print("PART 4: HEAD-TO-HEAD — DOES THE FULL LOOP BEAT THE SINE?")
    print("=" * 82)

    if loop_ssn_scores and sine_ssn_scores:
        n_splits = len(loop_ssn_scores)
        loop_wins_corr = sum(1 for a, b in zip(loop_ssn_scores, sine_ssn_scores)
                            if a['corr'] > b['corr'])
        loop_wins_mae = sum(1 for a, b in zip(loop_ssn_scores, sine_ssn_scores)
                           if a['mae'] < b['mae'])
        loop_wins_dir = sum(1 for a, b in zip(loop_ssn_scores, sine_ssn_scores)
                           if a['direction'] > b['direction'])

        avg_l_corr = np.mean([r['corr'] for r in loop_ssn_scores])
        avg_s_corr = np.mean([r['corr'] for r in sine_ssn_scores])
        avg_l_mae = np.mean([r['mae'] for r in loop_ssn_scores])
        avg_s_mae = np.mean([r['mae'] for r in sine_ssn_scores])
        avg_l_dir = np.mean([r['direction'] for r in loop_ssn_scores])
        avg_s_dir = np.mean([r['direction'] for r in sine_ssn_scores])

        print(f"\n  Full Loop vs 11yr Sine across {n_splits} splits:")
        print(f"    Correlation:  Loop={avg_l_corr:+.3f} vs Sine={avg_s_corr:+.3f}  "
              f"(Loop wins {loop_wins_corr}/{n_splits})")
        print(f"    MAE:          Loop={avg_l_mae:.1f} vs Sine={avg_s_mae:.1f}  "
              f"(Loop wins {loop_wins_mae}/{n_splits})")
        print(f"    Direction:    Loop={avg_l_dir:.1f}% vs Sine={avg_s_dir:.1f}%  "
              f"(Loop wins {loop_wins_dir}/{n_splits})")

        # Also vs single channel
        avg_f1_corr = np.mean([r['corr'] for r in single_ssn_scores])
        avg_f1_mae = np.mean([r['mae'] for r in single_ssn_scores])
        f1_wins = sum(1 for a, b in zip(loop_ssn_scores, single_ssn_scores)
                     if a['mae'] < b['mae'])

        print(f"\n  Full Loop vs Single Channel:")
        print(f"    Correlation:  Loop={avg_l_corr:+.3f} vs F1={avg_f1_corr:+.3f}")
        print(f"    MAE:          Loop={avg_l_mae:.1f} vs F1={avg_f1_mae:.1f}  "
              f"(Loop wins {f1_wins}/{n_splits})")

        beats_sine = loop_wins_mae > n_splits / 2
        beats_f1 = f1_wins > n_splits / 2

        if beats_sine:
            print(f"\n  ★★★ VERDICT: Full ARA Loop BEATS the 11-year sine baseline.")
            print(f"  The consumer triad provides the return path that the engine")
            print(f"  alone couldn't. The full loop captures cycle structure that")
            print(f"  a simple sinusoid cannot.")
        elif beats_f1:
            print(f"\n  VERDICT: Full Loop improves on single-channel but still")
            print(f"  doesn't beat the sine. The consumer triad helps but the")
            print(f"  coupling geometry needs refinement.")
        else:
            print(f"\n  VERDICT: Full Loop doesn't clearly improve. The coupling")
            print(f"  architecture may need different geometry or the consumer")
            print(f"  basin parameters need separate calibration.")

    print(f"\n{'='*82}")
    print("Script 196 complete.")
    print("=" * 82)
