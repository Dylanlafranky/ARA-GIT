#!/usr/bin/env python3
"""
Script 243AQ — Gleissberg Vertical Envelope

Based on 243AJ (champion, Solar LOO 42.89).

PROBLEM (from 243AP diagnostic):
  - Prediction std = 29.4 vs actual std = 55.4 (0.53× too flat)
  - All 4 cascade periods get same 1/φ⁴ coupling → ±20% swing
  - Actual data swings ±50%
  - The Gleissberg sits ABOVE the Schwabe — it's vertical coupling (pipe),
    not horizontal coupling (same-scale). Treating it as horizontal is wrong.

FIX:
  - Pull the Gleissberg (index 1) OUT of the multiplicative cascade
  - Apply it as a VERTICAL amplitude envelope at pipe-strength
  - Pipe capacity: down = 2φ, up = φ (from three-circle architecture)
  - Make the envelope DYNAMIC via inst_ara:
      * inst_ara near φ → moderate pipe flow (balanced engine)
      * inst_ara > φ → fuller pipe (excess energy pushes down harder)
      * inst_ara < φ → weaker pipe (deficit, less energy to push)
  - Keep the other 3 periods (Schwabe-scaled, Sub-Gleissberg, Sub-sub)
    in the standard multiplicative cascade at 1/φ⁴

  The Gleissberg envelope multiplies the DEVIATION from midline,
  giving it direct authority over amplitude — not just phase modulation.
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


# ── FIX 1: Gleissberg memory buffer ──
def compute_memory_buffer(amp_history, current_amp):
    """φ-decaying weighted average of past amplitudes."""
    if not amp_history and current_amp is None:
        return None
    amps = list(amp_history) if amp_history else []
    if current_amp is not None and (not amps or amps[-1] != current_amp):
        amps.append(current_amp)
    if not amps:
        return None
    total_weight = 0.0
    weighted_sum = 0.0
    for i, amp in enumerate(reversed(amps)):
        weight = INV_PHI ** i
        weighted_sum += amp * weight
        total_weight += weight
    return weighted_sum / total_weight if total_weight > 0 else amps[-1]


# ── FIX 3: ARA-dependent momentum ──
def ara_momentum(ara):
    return math.log1p(max(0.01, ara)) / 2.0


# ── FIX 4: Midline from 237d ──
def ara_midline(ara):
    """midline = 1 + acc_frac × (ARA - 1), where acc_frac = 1/(1+ARA)."""
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)


# ── Double log decay ──
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
func_code = '\n'.join(lines[:cutoff_line]) if cutoff_line else full_code
ns_235b = {}
exec(func_code, ns_235b)
OrigARANode = ns_235b['ARANode']


# ── Triangle rider ──
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


class EngineMemoryNode(OrigARANode):
    """
    243AQ: Gleissberg as vertical amplitude envelope.

    Key change: The Gleissberg period is pulled out of the multiplicative
    cascade and applied as a direct amplitude envelope at pipe-strength,
    with dynamic fill level based on inst_ara.
    """

    def __init__(self, name, period, ara, rung, base_amp, archetype,
                 seed_ara=None, rung_offset=0,
                 child_sign=-1, parent_sign=-1,
                 gate_send=True):
        super().__init__(name, period, ara, rung, base_amp, archetype)
        s, t, r = find_triangle_position(ara)
        self.pos_s, self.pos_t, self.pos_r = s, t, r
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
        # FIX 4: Midline
        self.midline = ara_midline(ara)
        # FIX 5: Amplitude scale (static base from champion)
        self.amp_scale = self.midline

        self.child_engine = None
        self.parent_engine = None
        self.child_last_snap_amp = None
        self.parent_last_snap_amp = None
        self.tilt_momentum = 0.0

    def update_gear_state(self):
        if self.child_engine is not None and self.child_engine.snap_amplitudes:
            self.child_last_snap_amp = self.child_engine.snap_amplitudes[-1]
        if self.parent_engine is not None and self.parent_engine.snap_amplitudes:
            self.parent_last_snap_amp = self.parent_engine.snap_amplitudes[-1]

    def cascade_shape(self, t):
        if self.t_ref is None: return 1.0
        self.update_gear_state()

        # ── inst_ara from previous amplitude ──
        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

        # ── Breathing valve ──
        receiver_acc = 1.0 / (1.0 + max(0.01, inst_ara))

        # ── Temporal gear tilt ──
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

        # ── Double-log singularity decay ──
        current_decay = decay_double_log(inst_ara, self.tilt_momentum)

        # ── Asymmetric breathing ──
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

        # ── Triangle rider ──
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
        gate = state / ((PHI + INV_PHI) / 2)

        # ── Build eps_vals for ALL periods (same as champion) ──
        collisions = [0.0]
        for j in range(1, len(phases)):
            collisions.append(-math.cos(phases[j-1] - phases[j]))
        eps_vals = []
        for j in range(len(phases)):
            d = live_d[j]
            base_eps = INV_PHI_4 if d > 0 else INV_PHI_3
            eps_vals.append(base_eps * gate)
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
            eps_vals[j] *= (1 + INV_PHI_4 * blend)
        for j in range(1, len(phases)):
            d = live_d[j]
            if d < 0:
                eps_vals[j] /= (1 + collisions[j] * INV_PHI)
                eps_vals[j] *= (1 + collisions[j] * INV_PHI * 0.5)
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

        # ════════════════════════════════════════════════════════════
        # 243AQ: Gleissberg pulled from cascade, applied as envelope
        # ════════════════════════════════════════════════════════════
        #
        # 3 periods in multiplicative cascade (skip Gleissberg at index 1).
        # Gleissberg applied after as amp_scale modulator (see below).
        #
        shape = 1.0
        for j in range(len(live_periods)):
            if j == 1:  # Skip Gleissberg
                continue
            shape *= (1 + eps_vals[j] * cos_vals[j])

        # Schwabe + Gleissberg additive terms (unchanged from champion)
        shape += INV_PHI_9 * math.cos(gp)
        cp_schwabe = (sp % TAU) / TAU
        shape += INV_PHI_3 * math.exp(-PHI * cp_schwabe) * math.cos(sp)

        # ── FIX 2 DISABLED: Original instant grief correction ──
        if self.prev_amp is not None:
            prev_dev = (self.prev_amp - self.base_amp) / self.base_amp
            grief_mult = 1.0 + INV_PHI_3 * (-prev_dev) * math.exp(-PHI)
            shape *= grief_mult

        if self.wall_energy > 0:
            shape *= (1 + self.wall_energy * INV_PHI_3)
            self.wall_energy *= INV_PHI

        # ── FIX 4: Midline shift ──
        shape += (self.midline - 1.0)

        # ════════════════════════════════════════════════════════════
        # GLEISSBERG VERTICAL ENVELOPE — modulates amp_scale
        # ════════════════════════════════════════════════════════════
        #
        # v2: Instead of post-multiplying the deviation (which can go
        # negative and flip the wave), the Gleissberg modulates the
        # amp_scale BEFORE it's applied. This controls HOW MUCH the
        # wave swings — the Gleissberg sets amplitude authority.
        #
        # Coupling: INV_PHI (0.618) as base — moderate pipe strength.
        #   vs horizontal 1/φ⁴ = 0.146, this is 4.2× stronger.
        #   vs full PHI = 1.618, this avoids wave inversion.
        #
        # Dynamic fill: inst_ara / (inst_ara + 1)
        #   Solar(φ): fill=0.618 → coupling = 0.618 × 0.618 × gate = 0.382 × gate
        #   Consumer: fill=0.130 → coupling = 0.618 × 0.130 × gate = 0.080 × gate
        #
        # Amp_scale range at Solar (gate≈1):
        #   cos=+1: amp_scale = 1.236 × (1 + 0.382) = 1.708 (wide swing)
        #   cos=-1: amp_scale = 1.236 × (1 - 0.382) = 0.764 (narrow swing)
        #
        gleissberg_cos = cos_vals[1]
        fill_level = inst_ara / (inst_ara + 1.0)
        gleissberg_coupling = INV_PHI * fill_level * gate

        # Modulate amp_scale dynamically
        dynamic_amp_scale = self.amp_scale * (1.0 + gleissberg_coupling * gleissberg_cos)
        # Floor: never let amp_scale go negative (would invert the wave)
        dynamic_amp_scale = max(0.05, dynamic_amp_scale)

        # ── FIX 5: Amplitude scale with Gleissberg envelope ──
        dev_from_mid = shape - self.midline
        shape = self.midline + dev_from_mid * dynamic_amp_scale

        return shape


# ════════════════════════════════════════════════════════════════
# VEHICLE BUILD + SIMULATION + LOO
# ════════════════════════════════════════════════════════════════

def build_rung_ladder(target_rung, target_period, seed_ara):
    atom = derive_atom_nodes(seed_ara, target_period)
    rungs = []
    for offset in range(-2, 5):
        r = target_rung + offset
        if r < 0: continue
        p = target_period * PHI**offset
        if offset == 4:   prefix = "Gleissberg"
        elif offset == 1: prefix = "AboveT"
        elif offset == 0: prefix = "Target"
        elif offset == -1: prefix = "BelowT"
        elif offset == -2: prefix = "SubSub"
        elif offset == 2: prefix = "AboveA"
        elif offset == 3: prefix = "AboveB"
        else: prefix = f"R{r}"
        engine_ara = PHI; consumer_ara = INV_PHI
        for roff, role, ara, per in atom:
            if roff == offset or (offset > 1 and roff == 1) or (offset < -1 and roff == -1):
                if role == 'engine': engine_ara = ara
                elif role == 'consumer': consumer_ara = ara
        rungs.append((r, p, prefix, engine_ara, consumer_ara, offset))
    return sorted(rungs, key=lambda x: -x[0])


def grid_search(period, ara, rung, times, peaks, n_tr=80, n_ba=40):
    gleissberg = period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * period
    ba_lo = np.mean(peaks) * 0.3; ba_hi = np.mean(peaks) * 1.8
    t_refs = np.linspace(tr_lo, tr_hi, n_tr)
    base_amps = np.linspace(ba_lo, ba_hi, n_ba)
    best_mae, best_tr, best_ba = 1e9, t_refs[0], base_amps[0]
    for tr in t_refs:
        for ba in base_amps:
            node = EngineMemoryNode("temp", period, ara, rung, ba, "engine")
            node.set_t_ref(tr)
            errors = []
            for k in range(len(times)):
                node.prev_amp = peaks[k-1] if k > 0 else None
                if k > 0: node.amp_history = list(peaks[:k])
                pred = node.cascade_amplitude(times[k])
                errors.append(abs(pred - peaks[k]))
            mae = np.mean(errors)
            if mae < best_mae:
                best_mae, best_tr, best_ba = mae, tr, ba
    return best_tr, best_ba, best_mae


def run_formula_loo(times, peaks, period, ara, target_rung, system_name):
    """Formula LOO: refit per fold, predict with cascade_amplitude."""
    N = len(times)
    loo_errors = []
    loo_preds = []
    sine_errors = []

    for i in range(N):
        mask = np.ones(N, dtype=bool)
        mask[i] = False
        train_t = times[mask]
        train_p = peaks[mask]

        fit_tr, fit_ba, _ = grid_search(period, ara, target_rung, train_t, train_p)

        node = EngineMemoryNode("loo", period, ara, target_rung, fit_ba, "engine")
        node.set_t_ref(fit_tr)
        node.prev_amp = peaks[i-1] if i > 0 else None
        if i > 0:
            node.amp_history = list(peaks[:i])
        pred = node.cascade_amplitude(times[i])
        loo_preds.append(pred)
        loo_errors.append(abs(pred - peaks[i]))
        sine_errors.append(abs(peaks[i] - np.mean(train_p)))

    loo_mae = np.mean(loo_errors)
    sine_mae = np.mean(sine_errors)
    corr = np.corrcoef(loo_preds, peaks)[0, 1] if len(loo_preds) > 2 else 0

    return {
        'loo_mae': loo_mae,
        'sine_mae': sine_mae,
        'ratio': loo_mae / sine_mae if sine_mae > 0 else 999,
        'corr': corr,
        'errors': np.array(loo_errors),
        'preds': np.array(loo_preds),
    }


# ════════════════════════════════════════════════════════════════
# DATA
# ════════════════════════════════════════════════════════════════

SOLAR_CYCLES = [
    (1,  1761.5, 144.1), (2,  1769.7, 193.0), (3,  1778.4, 264.3),
    (4,  1788.1, 235.3), (5,  1805.2,  82.0), (6,  1816.4,  81.2),
    (7,  1829.9, 119.2), (8,  1837.2, 244.9), (9,  1848.1, 219.9),
    (10, 1860.1, 186.2), (11, 1870.6, 234.0), (12, 1883.9, 124.4),
    (13, 1894.1, 146.5), (14, 1906.2, 107.1), (15, 1917.6, 175.7),
    (16, 1928.4, 130.2), (17, 1937.4, 198.6), (18, 1947.5, 218.7),
    (19, 1957.9, 285.0), (20, 1968.9, 156.6), (21, 1979.9, 232.9),
    (22, 1989.6, 212.5), (23, 2001.9, 180.3), (24, 2014.3, 116.4),
    (25, 2024.5, 173.0),
]
ENSO_EVENTS = [
    (1951.9, 1.2), (1953.2, 0.6), (1957.8, 1.7), (1963.8, 1.1),
    (1965.4, 1.4), (1968.9, 1.0), (1972.8, 2.0), (1976.7, 0.8),
    (1977.7, 0.8), (1979.7, 0.6), (1982.8, 2.1), (1986.9, 1.5),
    (1991.6, 1.6), (1994.8, 1.2), (1997.8, 2.3), (2002.8, 1.3),
    (2004.7, 0.7), (2006.8, 0.9), (2009.7, 1.5), (2015.0, 2.6),
    (2018.9, 0.8), (2023.9, 2.0), (2025.2, 0.9),
]
SANRIKU_EVENTS = [
    (1896.46, 8.5), (1933.17, 8.4), (1938.88, 7.7), (1968.42, 7.9),
    (1994.97, 7.7), (2011.19, 9.1), (2021.12, 7.1), (2022.21, 7.4),
    (2025.94, 7.6), (2026.30, 7.5),
]

solar_t = np.array([c[1] for c in SOLAR_CYCLES])
solar_a = np.array([c[2] for c in SOLAR_CYCLES])
enso_t  = np.array([e[0] for e in ENSO_EVENTS])
enso_a  = np.array([e[1] for e in ENSO_EVENTS])
eq_t    = np.array([e[0] for e in SANRIKU_EVENTS])
eq_a    = np.array([e[1] for e in SANRIKU_EVENTS])

SYSTEMS = [
    ("Solar (SSN)", solar_t, solar_a, PHI**5, PHI,   5),
    ("ENSO (ONI)",  enso_t,  enso_a,  PHI**3, 2.0,   3),
    ("Sanriku EQ",  eq_t,    eq_a,    PHI**4, 0.15,  4),
]


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

print("=" * 78)
print("Script 243AQ — Gleissberg Vertical Envelope")
print("=" * 78)
print()
print("  KEY CHANGE: Gleissberg pulled from multiplicative cascade")
print("  → Applied as vertical amplitude envelope at pipe-strength")
print("  → Dynamic fill: inst_ara / (inst_ara + 1)")
print("  → Coupling: INV_PHI × fill × gate (4.2× horizontal, not PHI which inverts)")
print()

# Show envelope strength at different ARA values
print("  Gleissberg envelope strength (at gate=1.0):")
print(f"  {'ARA':>6} │ {'Role':>10} │ {'Fill':>6} │ {'Coupling':>8} │ {'vs 1/φ⁴':>8} │ {'Amp range':>12}")
print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*12}")
for ara, role in [(0.15, "deep cons"), (INV_PHI, "consumer"), (1.0, "clock"),
                  (PHI, "ENGINE"), (2.0, "exotherm")]:
    fill = ara / (ara + 1.0)
    coupling = INV_PHI * fill  # v2: INV_PHI not PHI
    ratio_v = coupling / INV_PHI_4
    mid = ara_midline(ara)
    amp_hi = mid * (1 + coupling)
    amp_lo = mid * (1 - coupling)
    print(f"  {ara:>6.3f} │ {role:>10} │ {fill:>6.3f} │ {coupling:>8.4f} │ "
          f"{ratio_v:>7.1f}× │ {amp_lo:.3f}–{amp_hi:.3f}")
print()
print(f"  Champion 243AJ Gleissberg coupling: {INV_PHI_4:.4f} (horizontal)")
print(f"  Solar AQ envelope coupling (gate=1): {INV_PHI * PHI/(PHI+1):.4f} (vertical, modulates amp_scale)")
print()

# ── FORMULA LOO ──
print("─" * 78)
print("  FORMULA LOO (cascade_amplitude, refit per fold)")
print("─" * 78)

ref_loo = {"Solar (SSN)": 42.89, "ENSO (ONI)": 0.63, "Sanriku EQ": 1.33}
best_loo_ever = {"Solar (SSN)": 31.94, "ENSO (ONI)": 0.382, "Sanriku EQ": 3.48}

print(f"\n  {'System':<17} │ {'243AJ':>7} │ {'Best':>7} │ {'243AQ':>7} │ "
      f"{'Δ vs AJ':>8} │ {'Sine':>6} │ {'LOO/Sine':>8} │ {'Corr':>6}")
print(f"  {'─'*17}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*8}─┼─"
      f"{'─'*6}─┼─{'─'*8}─┼─{'─'*6}")

loo_results = {}
for name, times, peaks, period, ara, rung in SYSTEMS:
    t0 = clock_time.time()
    print(f"  Running {name} LOO ({len(times)} folds)...", end="", flush=True)
    res = run_formula_loo(times, peaks, period, ara, rung, name)
    loo_results[name] = res
    el = clock_time.time() - t0
    delta = res['loo_mae'] - ref_loo[name]
    flag = " ✓ BEAT" if delta < 0 else ""
    print(f"\r  {name:<17} │ {ref_loo[name]:>7.2f} │ {best_loo_ever[name]:>7.2f} │ "
          f"{res['loo_mae']:>7.2f} │ {delta:>+7.2f}{flag} │ {res['sine_mae']:>6.2f} │ "
          f"{res['ratio']:>8.3f} │ {res['corr']:>6.3f}  ({el:.0f}s)")

# Solar LOO per-cycle
if "Solar (SSN)" in loo_results:
    sr = loo_results["Solar (SSN)"]
    print(f"\n  Solar LOO per-cycle:")
    print(f"    {'C':>3} {'Year':>7} {'Act':>6} │ {'Pred':>7} {'Err':>6} │ {'Dev':>6}")
    pred_std = np.std(sr['preds'])
    act_std = np.std(solar_a)
    for i in range(len(solar_t)):
        flag = " ◀" if sr['errors'][i] > 80 else ""
        dev = sr['preds'][i] - solar_a[i]
        print(f"    C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
              f"{sr['preds'][i]:>7.1f} {sr['errors'][i]:>6.1f} │ {dev:>+6.1f}{flag}")
    print(f"\n    Prediction std: {pred_std:.1f}  (actual: {act_std:.1f}, "
          f"ratio: {pred_std/act_std:.2f}×)")
    print(f"    Variance explained: {sr['corr']**2 * 100:.1f}%")


# ════════════════════════════════════════════════════════════════
# DIAGNOSTIC: Compare wave amplitude with and without envelope
# ════════════════════════════════════════════════════════════════
print(f"\n{'─' * 78}")
print("  DIAGNOSTIC: Gleissberg envelope effect")
print("─" * 78)

# Run a single full-data fit to examine the envelope
name, times, peaks, period, ara, rung = SYSTEMS[0]  # Solar
fit_tr, fit_ba, fit_mae = grid_search(period, ara, rung, times, peaks)

print(f"\n  Solar full-fit: t_ref={fit_tr:.1f}, base_amp={fit_ba:.1f}, MAE={fit_mae:.2f}")
print(f"\n  Per-cycle Gleissberg envelope analysis:")
print(f"    {'C':>3} {'Year':>7} │ {'inst_ara':>8} {'fill':>6} {'gate':>6} │ "
      f"{'coupling':>8} {'gleiss_cos':>10} {'dyn_amp':>8}")

node = EngineMemoryNode("diag", period, ara, rung, fit_ba, "engine")
node.set_t_ref(fit_tr)

for i in range(len(times)):
    node.prev_amp = peaks[i-1] if i > 0 else None
    if i > 0: node.amp_history = list(peaks[:i])

    # Compute inst_ara
    if node.prev_amp is not None and node.base_amp > 0:
        ia = node.prev_amp / node.base_amp
        ia = max(0.01, min(2.0, ia))
    else:
        ia = ara

    # Compute phases (simplified — just for diagnostics)
    s, t_pos, r = find_triangle_position(ia)
    live_d = blend_distances(s, t_pos, r)
    live_periods_diag = [period * PHI**d for d in live_d]
    gleiss_per = live_periods_diag[1]
    gp = TAU * (times[i] - fit_tr) / gleiss_per
    gleiss_cos_val = math.cos(gp)

    # Gate
    acc_d = 1.0 / (1.0 + max(0.01, ia))
    cp_d = (gp % TAU) / TAU
    if cp_d < acc_d: state_d = (cp_d / acc_d) * PHI
    else:
        ramp_d = (cp_d - acc_d) / (1 - acc_d)
        state_d = PHI * (1 - ramp_d) + INV_PHI * ramp_d
    gate_d = state_d / ((PHI + INV_PHI) / 2)

    fill = ia / (ia + 1.0)
    coupling = INV_PHI * fill * gate_d  # v2: INV_PHI
    mid = ara_midline(ara)
    dyn_amp = mid * (1.0 + coupling * gleiss_cos_val)

    print(f"    C{SOLAR_CYCLES[i][0]:>2} {times[i]:>7.1f} │ {ia:>8.3f} {fill:>6.3f} {gate_d:>6.3f} │ "
          f"{coupling:>8.4f} {gleiss_cos_val:>10.4f} {dyn_amp:>8.3f}")

    # Actually compute the prediction for comparison
    pred = node.cascade_amplitude(times[i])


# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════

print(f"\n{'=' * 78}")
print("SUMMARY — 243AQ Gleissberg Vertical Envelope")
print("=" * 78)
print()
print("  Architecture change:")
print(f"    Champion 243AJ: Gleissberg in cascade at 1/φ⁴ = {INV_PHI_4:.4f}")
print(f"    This script:    Gleissberg as envelope at INV_PHI×fill×gate (modulates amp_scale)")
print()
print("  LOO comparison vs champion 243AJ:")
for name in loo_results:
    r = loo_results[name]
    delta = r['loo_mae'] - ref_loo[name]
    status = "✓ IMPROVED" if delta < 0 else "✗ regressed" if delta > 0 else "= same"
    print(f"    {name:<17}: 243AJ={ref_loo[name]:.2f} → 243AQ={r['loo_mae']:.2f} "
          f"({delta:+.2f}) {status}")
print()
if "Solar (SSN)" in loo_results:
    sr = loo_results["Solar (SSN)"]
    pred_std = np.std(sr['preds'])
    act_std = np.std(solar_a)
    print(f"  Wave amplitude: pred_std={pred_std:.1f}, actual_std={act_std:.1f}, "
          f"ratio={pred_std/act_std:.2f}×")
    print(f"  (Champion was 0.53× — closer to 1.0 is better)")
print()
print(f"  Best LOO ever: Solar=31.94, ENSO=0.382, EQ=3.48")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
print("=" * 78)
