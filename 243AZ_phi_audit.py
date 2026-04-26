#!/usr/bin/env python3
"""
Script 243AZ — φ Constant Audit

Systematic scan of every φ-power usage in the champion cascade_shape.
For each constant, we test: what if it should be one φ-power higher or lower?

AUDIT OF ALL φ USAGES IN cascade_shape:
═══════════════════════════════════════

#  Line  Constant       Value    Role                                    Suspect?
── ──── ──────────────── ──────── ─────────────────────────────────────── ────────
1  246  INV_PHI_4       0.146   Gear coupling (child/parent snap)        ⚠ Symmetric for up/down — pipe says 2:1
2  312  PHI**d          φ^d     Period ladder spacing                    ✓ Correct
3  320  1/(1+inst_ara)  varies  Valve accumulation fraction              ✓ Framework-derived
4  322  PHI             1.618   Sawtooth peak                            ✓ Max coupling at φ
5  325  PHI→INV_PHI     ramp    Sawtooth ramp range                     ✓ φ to 1/φ
6  326  (PHI+INV_PHI)/2 √5/2    Gate normalization                      ? √5/2 ≈ 1.118
7  334  INV_PHI_3/4     .236/.146 Base eps: 1/φ³ (d≤0), 1/φ⁴ (d>0)    ⚠⚠ Ratio = φ, pipe says 2:1
8  338  PHI_2           2.618   Space phase multiplier                   ✓ φ² horizontal coupler
9  339  TWO_OVER_PHI    1.236   Rationality phase multiplier             ✓ 2/φ vertical coupler
10 342  PHI / INV_PHI   blend   Three-circle blend weights               ✓ Engine=time, Consumer=space
11 348  INV_PHI_4       0.146   Three-circle modulation strength         ? Could be 1/φ³
12 352  INV_PHI         0.618   Collision coupling (d<0, divide)         ✓
13 353  0.5             0.5     Collision re-add fraction                 ⚠ Why 0.5 not 1/φ = 0.618?
14 355  INV_PHI         0.618   Collision coupling (all j>0)             ✓
15 358  PHI-1 = 1/φ     0.618   Positive tension (engines)               ✓ = INV_PHI
16 359  1-INV_PHI=1/φ²  0.382   Negative tension (engines)               ✓ = INV_PHI_2
17 368  INV_PHI_9       0.013   Gleissberg residual                      ✓ φ⁹ coupling
18 370  INV_PHI_3       0.236   Schwabe rider coupling                   ? Could be 1/φ⁴
19 370  exp(-PHI)       0.198   Schwabe exponential decay                ? exp(-φ) or exp(-φ²)?
20 375  INV_PHI_3       0.236   Grief coupling                           ✓
21 375  exp(-PHI)       0.198   Grief decay                              ✓ Matches Schwabe
22 379  INV_PHI_3       0.236   Wall energy coupling                     ✓
23 380  INV_PHI         0.618   Wall energy decay                        ✓
24 196  INV_PHI         0.618   Triangle elasticity                      ✓
25 207  midline=1.236   1.236   amp_scale = midline                      ⚠⚠ Docstring says φ!

TOP SUSPECTS (testing each independently on 243AZ combo base):
  A. eps ratio: 1/φ³ vs 1/φ⁴ → try 2/φ⁴ vs 1/φ⁴ (pipe-correct 2:1 ratio)
  B. amp_scale: midline (1.236) → try φ (1.618) as docstring intended
  C. collision 0.5 → try 1/φ (0.618)
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9
TAU = 2 * math.pi
PHI_2 = PHI ** 2
TWO_OVER_PHI = 2.0 / PHI
TWO_PHI = 2.0 * PHI
PHI_LEAK = INV_PHI_4
LOG2 = math.log(2)
LOG_LOG_NORM = math.log(1.0 + math.log(1.0 + PHI_2))

SPACE_BASIS = np.array([9.0, 6.0, 2.0, -2.0])
TIME_BASIS  = np.array([5.0, 3.0, 1.0, -1.0])
RAT_BASIS   = np.array([6.0, 4.0, 1.0, -1.0])
BEST_STEER = 0.2


def ara_midline(ara):
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)

def decay_double_log(inst_ara, momentum=0.0):
    if inst_ara >= PHI:
        above = inst_ara - PHI
        return min(0.95, INV_PHI * (1.0 + math.log(1.0 + above) * INV_PHI))
    else:
        inner = math.log(1.0 + max(0.0, inst_ara) * PHI)
        return INV_PHI * math.log(1.0 + inner) / LOG_LOG_NORM

def derive_atom_nodes(seed_ara, seed_period):
    mirror_floor = 0.15
    nodes = []
    for rung_offset in [-1, 0, 1]:
        if rung_offset == 0:
            p = seed_period; engine_ara = seed_ara
            mirror_ara = max(mirror_floor, 2.0 - seed_ara)
        elif rung_offset == 1:
            p = seed_period * PHI; engine_ara = seed_ara / PHI
            mirror_ara = max(mirror_floor, 2.0 - engine_ara)
        elif rung_offset == -1:
            p = seed_period / PHI; engine_ara = min(2.0, seed_ara * PHI)
            mirror_ara = max(mirror_floor, 2.0 - engine_ara)
        nodes.append((rung_offset, 'engine',   engine_ara, p))
        nodes.append((rung_offset, 'clock',    1.0,        p))
        nodes.append((rung_offset, 'consumer', mirror_ara, p))
    return nodes


# ── 235b base ──
script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "235b_universal_vehicle.py")
with open(script_path, 'r') as f:
    full_code = f.read()
lines = full_code.split('\n')
cutoff_line = None
for i, line in enumerate(lines):
    if line.strip().startswith('print("="') and i > 100:
        cutoff_line = i
        break
if cutoff_line is None:
    cutoff_line = len(lines)
base_code = '\n'.join(lines[:cutoff_line])
exec(base_code)


# ────────────────────────────────────────────
# Parameterized cascade — accepts variant flags
# ────────────────────────────────────────────

def find_triangle_position(target_ara, space_bias=0.3):
    if target_ara <= 0: return (1.0, 0.0, 0.0)
    if target_ara >= 2.0: return (0.0, 1.0, 0.0)
    f_min = target_ara / 2.0; f_max = target_ara / PHI
    f_min = max(f_min, 0.001); f_max = min(f_max, 0.999)
    if f_min > f_max:
        f_min = f_max = min(0.999, max(0.001, (f_min + f_max) / 2))
    f = f_max - space_bias * (f_max - f_min)
    f = max(0.001, min(0.999, f))
    s = 1.0 - f; t = (target_ara - PHI * f) / (2.0 - PHI); r = f - t
    t = max(0, min(f, t)); r = max(0, f - t); s = max(0, s)
    total = s + t + r
    return (s / total, t / total, r / total)

def blend_distances(s, t, r):
    return s * SPACE_BASIS + t * TIME_BASIS + r * RAT_BASIS

def clamp_to_triangle(s, t, r):
    wall_hit = None; wall_energy = 0.0
    if s < 0: wall_energy = max(wall_energy, abs(s)); wall_hit = 's'; s = 0.0
    if t < 0: wall_energy = max(wall_energy, abs(t)); wall_hit = 't'; t = 0.0
    if r < 0: wall_energy = max(wall_energy, abs(r)); wall_hit = 'r'; r = 0.0
    total = s + t + r
    if total > 0: s, t, r = s / total, t / total, r / total
    else: s, t, r = 1/3, 1/3, 1/3
    return s, t, r, wall_hit, wall_energy


class AuditCascadeEngine:
    """Parameterized cascade engine for φ-constant testing."""

    def __init__(self, period, ara, schwabe, *, seed_ara=None, rung_offset=0,
                 child_sign=1.0, parent_sign=-1.0, gate_send=True,
                 # Variant flags:
                 eps_below=None,       # override base_eps for d≤0 (default 1/φ³)
                 eps_above=None,       # override base_eps for d>0  (default 1/φ⁴)
                 amp_scale_override=None,  # override amp_scale
                 collision_frac=0.5,       # the 0.5 in collision re-add
                 three_circle_mod=None,    # override INV_PHI_4 blend strength
                 schwabe_coupling=None,    # override INV_PHI_3 schwabe
                 schwabe_decay_exp=None,   # override exp(-PHI) schwabe decay
                 gate_norm=None,           # override (PHI+INV_PHI)/2
                 # Wave physics combo:
                 mode_coupling=True,
                 standing_wave=True,
                 ):
        self.period = period
        self.ara = ara
        self.schwabe = schwabe
        self.base_amp = 0.0
        self.prev_amp = None
        self.t_ref = None

        # Variant params
        self.eps_below = eps_below if eps_below is not None else INV_PHI_3
        self.eps_above = eps_above if eps_above is not None else INV_PHI_4
        self.collision_frac = collision_frac
        self.three_circle_mod = three_circle_mod if three_circle_mod is not None else INV_PHI_4
        self.schwabe_coupling = schwabe_coupling if schwabe_coupling is not None else INV_PHI_3
        self.schwabe_decay_exp = schwabe_decay_exp if schwabe_decay_exp is not None else PHI
        self.gate_norm = gate_norm if gate_norm is not None else (PHI + INV_PHI) / 2
        self.mode_coupling = mode_coupling
        self.standing_wave = standing_wave

        # Triangle rider state
        s0, t0, r0 = find_triangle_position(ara)
        self.pos_s, self.pos_t, self.pos_r = s0, t0, r0
        self.vel_s, self.vel_t, self.vel_r = 0.0, 0.0, 0.0
        self.wall_energy = 0.0
        self.bounce_count = 0
        self.steer = BEST_STEER
        self.momentum_param = 0.3
        self.elasticity = INV_PHI
        self.seed_ara = seed_ara or ara
        self.rung_offset = rung_offset
        self.child_sign = child_sign
        self.parent_sign = parent_sign
        self.gate_send = gate_send
        self.midline = ara_midline(ara)

        if amp_scale_override is not None:
            self.amp_scale = amp_scale_override
        else:
            self.amp_scale = self.midline  # champion default

        self.child_engine = None
        self.parent_engine = None
        self.child_last_snap_amp = None
        self.parent_last_snap_amp = None
        self.tilt_momentum = 0.0

    def update_gear_state(self):
        pass

    def cascade_shape(self, t):
        if self.t_ref is None: return 1.0
        self.update_gear_state()

        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

        receiver_acc = 1.0 / (1.0 + max(0.01, inst_ara))

        # Gear tilts (unchanged)
        gear_tilt_raw = 0.0
        if self.child_last_snap_amp is not None and self.child_engine is not None:
            child_dev = (self.child_last_snap_amp - self.child_engine.base_amp)
            if self.child_engine.base_amp > 0:
                child_dev /= self.child_engine.base_amp
            raw_child = self.child_sign * INV_PHI_4 * child_dev
            if self.gate_send and self.child_engine.prev_amp is not None:
                child_ara_est = self.child_engine.prev_amp / max(0.01, self.child_engine.base_amp)
                child_ara_est = max(0.01, min(2.0, child_ara_est))
                sender_strength = 1.0 - 1.0 / (1.0 + child_ara_est)
                raw_child *= sender_strength
            gear_tilt_raw += raw_child

        if self.parent_last_snap_amp is not None and self.parent_engine is not None:
            parent_dev = (self.parent_last_snap_amp - self.parent_engine.base_amp)
            if self.parent_engine.base_amp > 0:
                parent_dev /= self.parent_engine.base_amp
            raw_parent = self.parent_sign * INV_PHI_4 * parent_dev
            if self.gate_send and self.parent_engine.prev_amp is not None:
                parent_ara_est = self.parent_engine.prev_amp / max(0.01, self.parent_engine.base_amp)
                parent_ara_est = max(0.01, min(2.0, parent_ara_est))
                sender_strength = 1.0 - 1.0 / (1.0 + parent_ara_est)
                raw_parent *= sender_strength
            gear_tilt_raw += raw_parent

        current_decay = decay_double_log(inst_ara, self.tilt_momentum)

        home_ara = self.ara
        deviation = inst_ara - home_ara
        if abs(deviation) < 0.01:
            is_inhale = True
        else:
            is_inhale = (gear_tilt_raw * deviation) < 0

        if is_inhale:
            gear_tilt_gated = gear_tilt_raw * receiver_acc
            inst_ara = max(0.01, min(2.0, inst_ara + gear_tilt_gated))
        else:
            self.tilt_momentum += gear_tilt_raw

        momentum_contribution = self.tilt_momentum * receiver_acc
        inst_ara = max(0.01, min(2.0, inst_ara + momentum_contribution))
        self.tilt_momentum *= current_decay
        if abs(self.tilt_momentum) < 1e-8:
            self.tilt_momentum = 0.0

        # Triangle rider
        target_s, target_t, target_r = find_triangle_position(inst_ara)
        force_s = (target_s - self.pos_s) * self.steer
        force_t = (target_t - self.pos_t) * self.steer
        force_r = (target_r - self.pos_r) * self.steer
        self.vel_s = self.vel_s * self.momentum_param + force_s
        self.vel_t = self.vel_t * self.momentum_param + force_t
        self.vel_r = self.vel_r * self.momentum_param + force_r
        vel_mean = (self.vel_s + self.vel_t + self.vel_r) / 3
        self.vel_s -= vel_mean; self.vel_t -= vel_mean; self.vel_r -= vel_mean
        new_s = self.pos_s + self.vel_s
        new_t = self.pos_t + self.vel_t
        new_r = self.pos_r + self.vel_r
        new_s, new_t, new_r, wall, w_energy = clamp_to_triangle(new_s, new_t, new_r)
        if wall is not None:
            self.bounce_count += 1; self.wall_energy += w_energy
            if wall == 's': self.vel_s = abs(self.vel_s) * self.elasticity
            elif wall == 't': self.vel_t = abs(self.vel_t) * self.elasticity
            elif wall == 'r': self.vel_r = abs(self.vel_r) * self.elasticity
        self.pos_s, self.pos_t, self.pos_r = new_s, new_t, new_r

        # ── Cascade from rider ──
        live_d = blend_distances(self.pos_s, self.pos_t, self.pos_r)
        live_periods = [self.period * PHI**d for d in live_d]
        live_gleissberg = live_periods[1]
        phases = [TAU * (t - self.t_ref) / per for per in live_periods]
        cos_vals = [math.cos(ph) for ph in phases]
        sin_vals = [math.sin(ph) for ph in phases]
        gp = TAU * (t - self.t_ref) / live_gleissberg
        sp = TAU * (t - self.t_ref) / self.schwabe

        acc = 1.0 / (1.0 + max(0.01, inst_ara))
        cp = (gp % TAU) / TAU
        if cp < acc: state = (cp / acc) * PHI
        else:
            ramp = (cp - acc) / (1 - acc)
            state = PHI * (1 - ramp) + INV_PHI * ramp
        gate = state / self.gate_norm

        collisions = [0.0]
        for j in range(1, len(phases)):
            collisions.append(-math.cos(phases[j-1] - phases[j]))

        # ── VARIANT: eps_below / eps_above ──
        eps_vals = []
        for j in range(len(phases)):
            d = live_d[j]
            base_eps = self.eps_above if d > 0 else self.eps_below
            eps_vals.append(base_eps * gate)

        # Three-circle modulation
        for j in range(len(phases)):
            d = live_d[j]
            space_phase = phases[j] * PHI_2
            rat_phase = phases[j] * TWO_OVER_PHI
            space_cos = math.cos(space_phase)
            rat_cos = math.cos(rat_phase)
            if d > 0:
                blend = (cos_vals[j] * PHI + space_cos * INV_PHI + rat_cos * INV_PHI)
                blend /= (PHI + INV_PHI + INV_PHI)
            else:
                blend = (cos_vals[j] * INV_PHI + space_cos * PHI + rat_cos * INV_PHI)
                blend /= (INV_PHI + PHI + INV_PHI)
            eps_vals[j] *= (1 + self.three_circle_mod * blend)

        # Collision processing
        for j in range(1, len(phases)):
            d = live_d[j]
            if d < 0:
                eps_vals[j] /= (1 + collisions[j] * INV_PHI)
                eps_vals[j] *= (1 + collisions[j] * INV_PHI * self.collision_frac)
        for j in range(len(phases)):
            if j > 0: eps_vals[j] *= (1 + collisions[j] * INV_PHI)
            tens = -sin_vals[j]
            if inst_ara >= 1.0:
                if tens > 0: eps_vals[j] *= (1 + 0.5 * tens * (PHI - 1))
                else: eps_vals[j] *= (1 + 0.5 * tens * (1 - INV_PHI))
            else:
                log_tens = math.copysign(math.log1p(abs(tens)) / LOG2, tens)
                if log_tens > 0: eps_vals[j] *= (1 + 0.5 * log_tens * (PHI - 1))
                else: eps_vals[j] *= (1 + 0.5 * log_tens * (1 - INV_PHI))

        # ── MODE COUPLING (from 243AW-v2) ──
        if self.mode_coupling:
            for j in range(len(eps_vals) - 1, 0, -1):
                transfer = eps_vals[j] * INV_PHI_9
                eps_vals[j] -= transfer
                eps_vals[j-1] += transfer

        shape = 1.0
        for j in range(len(live_periods)):
            shape *= (1 + eps_vals[j] * cos_vals[j])
        shape += INV_PHI_9 * math.cos(gp)
        cp_schwabe = (sp % TAU) / TAU
        shape += self.schwabe_coupling * math.exp(-self.schwabe_decay_exp * cp_schwabe) * math.cos(sp)

        # ── STANDING WAVE (from 243AX-v3) ──
        if self.standing_wave:
            standing_now = math.sin(math.pi * inst_ara / 2.0)
            standing_home = math.sin(math.pi * self.ara / 2.0)
            standing_delta = standing_now - standing_home
            shape *= (1.0 + standing_delta * INV_PHI_3)

        # Grief
        if self.prev_amp is not None:
            prev_dev = (self.prev_amp - self.base_amp) / self.base_amp
            grief_mult = 1.0 + INV_PHI_3 * (-prev_dev) * math.exp(-PHI)
            shape *= grief_mult

        if self.wall_energy > 0:
            shape *= (1 + self.wall_energy * INV_PHI_3)
            self.wall_energy *= INV_PHI

        shape += (self.midline - 1.0)
        deviation_val = shape - self.midline
        shape = self.midline + deviation_val * self.amp_scale

        return shape


# ════════════════════════════════════════════════════════
# SOLAR-ONLY LOO TEST
# ════════════════════════════════════════════════════════

# Solar data
SOLAR_CYCLES = [
    (1, 1755.0, 1766.4, 144.1), (2, 1766.4, 1775.4, 193.0),
    (3, 1775.4, 1784.7, 264.3), (4, 1784.7, 1798.3, 235.3),
    (5, 1798.3, 1810.6, 82.0),  (6, 1810.6, 1823.2, 81.2),
    (7, 1823.2, 1833.9, 119.2), (8, 1833.9, 1843.5, 244.9),
    (9, 1843.5, 1855.7, 219.9), (10, 1855.7, 1867.0, 186.2),
    (11, 1867.0, 1878.9, 234.0),(12, 1878.9, 1890.2, 124.4),
    (13, 1890.2, 1902.0, 146.5),(14, 1902.0, 1913.6, 107.1),
    (15, 1913.6, 1923.6, 175.7),(16, 1923.6, 1933.8, 130.2),
    (17, 1933.8, 1944.2, 198.6),(18, 1944.2, 1954.3, 218.7),
    (19, 1954.3, 1964.7, 285.0),(20, 1964.7, 1976.5, 156.6),
    (21, 1976.5, 1986.8, 232.9),(22, 1986.8, 1996.4, 212.5),
    (23, 1996.4, 2008.9, 180.3),(24, 2008.9, 2019.7, 116.4),
    (25, 2019.7, 2030.0, 173.0),
]


def run_solar_loo(variant_name, **variant_kwargs):
    """Run Solar LOO with given variant parameters."""
    n = len(SOLAR_CYCLES)
    loo_errors = []
    loo_preds = []

    for leave_out in range(n):
        train = [c for i, c in enumerate(SOLAR_CYCLES) if i != leave_out]
        test_cycle = SOLAR_CYCLES[leave_out]

        periods = [c[2] - c[1] for c in train]
        amps = [c[3] for c in train]
        mean_period = np.mean(periods)
        mean_amp = np.mean(amps)

        seed_ara = PHI
        schwabe = mean_period

        engine = AuditCascadeEngine(
            mean_period, seed_ara, schwabe,
            **variant_kwargs
        )
        engine.base_amp = mean_amp
        engine.t_ref = train[0][1]

        # Feed training history
        for i, c in enumerate(train):
            t_peak = (c[1] + c[2]) / 2
            engine.prev_amp = c[3]

        # Predict
        t_test = (test_cycle[1] + test_cycle[2]) / 2
        shape = engine.cascade_shape(t_test)
        pred = mean_amp * max(0.01, shape)
        actual = test_cycle[3]

        loo_errors.append(abs(pred - actual))
        loo_preds.append(pred)

    loo = np.mean(loo_errors)
    # Correlation
    actuals = [c[3] for c in SOLAR_CYCLES]
    if np.std(loo_preds) > 0 and np.std(actuals) > 0:
        corr = np.corrcoef(actuals, loo_preds)[0, 1]
    else:
        corr = 0.0

    return loo, corr, loo_preds


# ════════════════════════════════════════════════════════
# RUN ALL VARIANTS
# ════════════════════════════════════════════════════════

SINE_BASELINE = 48.78
CHAMPION_LOO = 42.89

print("=" * 78)
print("  φ CONSTANT AUDIT — Systematic Scan")
print("  Champion LOO: 42.89 | Sine baseline: 48.78")
print("=" * 78)
print()

variants = {
    # Baseline: 243AZ combo (mode coupling + standing wave) with all champion defaults
    "BASELINE (243AZ combo)": {},

    # ── SUSPECT A: eps ratio ──
    # Current: 1/φ³ (below) vs 1/φ⁴ (above), ratio = φ
    # Test: 2/φ⁴ (below) vs 1/φ⁴ (above), ratio = 2 (pipe-correct)
    "A1: eps_below=2/φ⁴ (pipe 2:1)": {"eps_below": 2 * INV_PHI_4},
    # Test: 1/φ² (below) vs 1/φ³ (above) — both one power UP
    "A2: eps ↑1 power (1/φ² / 1/φ³)": {"eps_below": INV_PHI_2, "eps_above": INV_PHI_3},
    # Test: 1/φ⁴ (below) vs 1/φ⁴ (above) — equal (remove asymmetry)
    "A3: eps symmetric 1/φ⁴": {"eps_below": INV_PHI_4},

    # ── SUSPECT B: amp_scale ──
    # Current: midline (1.236 for Solar)
    # Test: φ (1.618) as docstring intended — so midline × amp_scale = 2.0
    "B1: amp_scale=φ (docstring)": {"amp_scale_override": PHI},
    # Test: √φ ≈ 1.272 (geometric mean of 1 and φ)
    "B2: amp_scale=√φ": {"amp_scale_override": math.sqrt(PHI)},
    # Test: φ² (the horizontal coupler)
    "B3: amp_scale=φ²": {"amp_scale_override": PHI_2},

    # ── SUSPECT C: collision fraction ──
    # Current: 0.5
    # Test: 1/φ ≈ 0.618
    "C1: collision_frac=1/φ": {"collision_frac": INV_PHI},
    # Test: 1/φ² ≈ 0.382
    "C2: collision_frac=1/φ²": {"collision_frac": INV_PHI_2},

    # ── SUSPECT D: three-circle modulation strength ──
    # Current: 1/φ⁴
    # Test: 1/φ³
    "D1: 3-circle mod=1/φ³": {"three_circle_mod": INV_PHI_3},
    # Test: 1/φ²
    "D2: 3-circle mod=1/φ²": {"three_circle_mod": INV_PHI_2},

    # ── SUSPECT E: schwabe coupling ──
    # Current: 1/φ³
    # Test: 1/φ⁴
    "E1: schwabe=1/φ⁴": {"schwabe_coupling": INV_PHI_4},
    # Test: 1/φ²
    "E2: schwabe=1/φ²": {"schwabe_coupling": INV_PHI_2},

    # ── SUSPECT F: schwabe decay exponent ──
    # Current: exp(-φ)
    # Test: exp(-1) — standard e-folding
    "F1: schwabe decay=exp(-1)": {"schwabe_decay_exp": 1.0},
    # Test: exp(-φ²)
    "F2: schwabe decay=exp(-φ²)": {"schwabe_decay_exp": PHI_2},

    # ── SUSPECT G: gate normalization ──
    # Current: (φ+1/φ)/2 = √5/2
    # Test: 1.0 (no normalization offset)
    "G1: gate_norm=1.0": {"gate_norm": 1.0},
    # Test: φ (normalize by φ itself)
    "G2: gate_norm=φ": {"gate_norm": PHI},
}

results = []
for name, kwargs in variants.items():
    loo, corr, preds = run_solar_loo(name, **kwargs)
    delta_champ = loo - CHAMPION_LOO
    ratio = loo / SINE_BASELINE
    marker = "★ NEW BEST" if loo < CHAMPION_LOO else ("✓ beats sine" if loo < SINE_BASELINE else "✗")
    results.append((name, loo, corr, delta_champ, ratio, marker))
    print(f"  {name:40s} │ LOO={loo:6.2f} │ Corr={corr:+.3f} │ Δchamp={delta_champ:+6.2f} │ {marker}")

print()
print("=" * 78)
print("  RANKED BY LOO (best first)")
print("=" * 78)
for name, loo, corr, delta, ratio, marker in sorted(results, key=lambda x: x[1]):
    print(f"  {loo:6.2f} │ {corr:+.3f} │ Δ={delta:+6.2f} │ {ratio:.3f}× sine │ {name} {marker}")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
