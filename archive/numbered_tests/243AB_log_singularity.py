#!/usr/bin/env python3
"""
Script 243AB — Log-Singularity Breathing: The Golden Exhale Must Be Earned

Dylan: "Are we scaling the approach to the φ singularity by log?
It should be harder to reach and require more energy to get to that point."

φ as singularity means the approach is LOG-COMPRESSED:
  - First 90% of improvement comes cheap
  - Last 10% costs exponentially more energy
  - Like approaching the speed of light — diminishing returns

Three variants:

  A — Single log: decay = (1/φ) × log(1+ARA)/log(1+φ)
      Clean log compression. At φ you earn the golden rate.

  B — Energy-gated: the MOMENTUM (fired tilt) is the energy.
      Big tilt → lots of energy → can push closer to golden decay.
      Small tilt → stuck in log compression far from φ.
      Engines fire big raw tilts → earn long exhale.
      Consumers fire small tilts → can't afford it.
      decay = base_log × (1 + log(1 + |momentum| × φ²) × 1/φ)

  C — Double log: log(log()) even steeper compression near φ.
      Brutally hard to earn the golden rate.

Above φ: engines get amplified (log growth above golden).
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
LOG_1_PLUS_PHI = math.log(1.0 + PHI)  # normalizer for log curve

SPACE_BASIS = np.array([9.0, 6.0, 2.0, -2.0])
TIME_BASIS  = np.array([5.0, 3.0, 1.0, -1.0])
RAT_BASIS   = np.array([6.0, 4.0, 1.0, -1.0])
BEST_STEER = 0.2
BEST_MOMENTUM = 0.3

# Double-log normalizer: log(1 + log(1 + φ²))
LOG_LOG_NORM = math.log(1.0 + math.log(1.0 + PHI_2))


# ── Decay curves ──

def decay_single_log(inst_ara, momentum=0.0):
    """
    Single log approach to φ.
    Below φ: decay = (1/φ) × log(1+ARA)/log(1+φ)  — log compression
    Above φ: decay = (1/φ) × (1 + log(1+(ARA-φ)) × 1/φ)  — log amplification

    Values: 0→0, 0.15→0.090, 0.618→0.309, 1.0→0.445, φ→0.618, 2.0→0.818
    """
    if inst_ara >= PHI:
        above = inst_ara - PHI
        return min(0.95, INV_PHI * (1.0 + math.log(1.0 + above) * INV_PHI))
    else:
        return INV_PHI * math.log(1.0 + max(0.0, inst_ara)) / LOG_1_PLUS_PHI

def decay_energy_gated(inst_ara, momentum=0.0):
    """
    Energy-gated: base log curve × energy boost from momentum.
    The momentum IS the energy that lets you approach φ's golden rate.
    Big fired tilt = lots of energy = closer to golden.
    Small tilt = stuck in log compression.

    base = single_log(ARA)
    energy_boost = log(1 + |momentum| × φ²) — converts momentum to energy
    effective = base × (1 + energy_boost × 1/φ)
    Capped at 0.95.

    Engines fire big raw tilts → big momentum → high energy → earn golden exhale.
    Consumers fire small tilts → low momentum → low energy → quick snap.
    """
    # Base from log curve
    if inst_ara >= PHI:
        above = inst_ara - PHI
        base = min(0.95, INV_PHI * (1.0 + math.log(1.0 + above) * INV_PHI))
    else:
        base = INV_PHI * math.log(1.0 + max(0.0, inst_ara)) / LOG_1_PLUS_PHI

    # Energy from momentum
    energy = math.log(1.0 + abs(momentum) * PHI_2)
    effective = base * (1.0 + energy * INV_PHI)
    return min(0.95, max(0.01, effective))

def decay_double_log(inst_ara, momentum=0.0):
    """
    Double log: log(1 + log(1 + ARA×φ)) — brutally steep compression near φ.
    Even harder to earn the golden rate.

    Below φ: decay = (1/φ) × log(1+log(1+ARA×φ)) / log(1+log(1+φ²))
    Above φ: same amplification as single log.

    Values: 0→0, 0.15→0.168, 0.618→0.369, 1.0→0.444, φ→0.618, 2.0→0.818
    """
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


# ── 235b ──
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
run_universal_vehicle = ns_235b['run_universal_vehicle']


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


class LogSingularityNode(OrigARANode):
    """
    Log-singularity breathing node.

    The approach to φ's golden exhale is LOG-COMPRESSED.
    You must EARN the golden rate — it's not given.

    Variant B (energy-gated) uses momentum as energy:
    big tilts push closer to φ, small tilts get stuck.
    """

    def __init__(self, name, period, ara, rung, base_amp, archetype,
                 seed_ara=None, rung_offset=0,
                 child_sign=-1, parent_sign=-1,
                 gate_send=True, decay_func=decay_single_log):
        super().__init__(name, period, ara, rung, base_amp, archetype)
        s, t, r = find_triangle_position(ara)
        self.pos_s, self.pos_t, self.pos_r = s, t, r
        self.vel_s, self.vel_t, self.vel_r = 0.0, 0.0, 0.0
        self.wall_energy = 0.0
        self.bounce_count = 0
        self.steer = BEST_STEER
        self.momentum_param = BEST_MOMENTUM
        self.elasticity = INV_PHI
        self.seed_ara = seed_ara or ara
        self.rung_offset = rung_offset
        self.child_sign = child_sign
        self.parent_sign = parent_sign
        self.gate_send = gate_send
        self.decay_func = decay_func

        self.child_engine = None
        self.parent_engine = None
        self.child_last_snap_amp = None
        self.parent_last_snap_amp = None

        # Momentum state
        self.tilt_momentum = 0.0

        # Diagnostics
        self.gear_tilts_raw = []
        self.gear_tilts_gated = []
        self.valve_history = []
        self.inhale_count = 0
        self.exhale_count = 0
        self.momentum_history = []
        self.decay_history = []

    def update_gear_state(self):
        if self.child_engine is not None and self.child_engine.snap_amplitudes:
            self.child_last_snap_amp = self.child_engine.snap_amplitudes[-1]
        if self.parent_engine is not None and self.parent_engine.snap_amplitudes:
            self.parent_last_snap_amp = self.parent_engine.snap_amplitudes[-1]

    def cascade_shape(self, t):
        if self.t_ref is None: return 1.0
        self.update_gear_state()

        # ── Instantaneous ARA ──
        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

        # ── BREATHING VALVE ──
        receiver_acc = 1.0 / (1.0 + max(0.01, inst_ara))

        # ── TEMPORAL GEAR TILT (raw) ──
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

        # ── LOG-SINGULARITY DECAY ──
        # Pass momentum so energy-gated variant can use it
        current_decay = self.decay_func(inst_ara, self.tilt_momentum)

        # ── ASYMMETRIC BREATHING ──
        home_ara = self.ara
        deviation = inst_ara - home_ara

        if abs(deviation) < 0.01:
            is_inhale = True
        else:
            is_inhale = (gear_tilt_raw * deviation) < 0

        if is_inhale:
            gear_tilt_gated = gear_tilt_raw * receiver_acc
            inst_ara = max(0.01, min(2.0, inst_ara + gear_tilt_gated))
            self.inhale_count += 1
        else:
            self.tilt_momentum += gear_tilt_raw
            self.exhale_count += 1
            gear_tilt_gated = 0.0

        # Apply decaying momentum (gated)
        momentum_contribution = self.tilt_momentum * receiver_acc
        inst_ara = max(0.01, min(2.0, inst_ara + momentum_contribution))

        # Decay momentum using log-singularity rate
        self.tilt_momentum *= current_decay

        if abs(self.tilt_momentum) < 1e-8:
            self.tilt_momentum = 0.0

        # Track diagnostics
        self.gear_tilts_raw.append(gear_tilt_raw)
        self.gear_tilts_gated.append(gear_tilt_gated + momentum_contribution)
        self.valve_history.append(receiver_acc)
        self.momentum_history.append(self.tilt_momentum)
        self.decay_history.append(current_decay)

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

        # ── Cascade from rider (standard) ──
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

        shape = 1.0
        for j in range(len(live_periods)):
            shape *= (1 + eps_vals[j] * cos_vals[j])
        shape += INV_PHI_9 * math.cos(gp)
        cp_schwabe = (sp % TAU) / TAU
        shape += INV_PHI_3 * math.exp(-PHI * cp_schwabe) * math.cos(sp)
        if self.prev_amp is not None:
            prev_dev = (self.prev_amp - self.base_amp) / self.base_amp
            grief_mult = PHI if prev_dev < 0 else 1.0
            shape += (-INV_PHI_3) * prev_dev * math.exp(-PHI) * grief_mult
        if self.wall_energy > 0:
            shape *= (1 + self.wall_energy * INV_PHI_3)
            self.wall_energy *= INV_PHI

        return shape


# ════════════════════════════════════════════════════════════════
# BUILD VEHICLE
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


def grid_search(period, ara, rung, times, peaks, n_tr=80, n_ba=40,
                decay_func=decay_single_log):
    gleissberg = period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * period
    ba_lo = np.mean(peaks) * 0.5; ba_hi = np.mean(peaks) * 1.5
    t_refs = np.linspace(tr_lo, tr_hi, n_tr)
    base_amps = np.linspace(ba_lo, ba_hi, n_ba)
    best_mae, best_tr, best_ba = 1e9, t_refs[0], base_amps[0]
    for tr in t_refs:
        for ba in base_amps:
            node = LogSingularityNode("temp", period, ara, rung, ba, "engine",
                                       decay_func=decay_func)
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


def run_log_singularity(times, peaks, period, ara, target_rung,
                        system_name="System", sim_margin=None,
                        decay_func=decay_single_log):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

    fit_tr, fit_ba, fit_mae = grid_search(
        period, ara, target_rung, times, peaks,
        decay_func=decay_func)
    rungs = build_rung_ladder(target_rung, period, ara)

    all_nodes = {}
    engine_nodes = {}

    for rung_power, rung_period, prefix, eng_ara, cons_ara, offset in rungs:
        for archetype, ara_val in [("engine", eng_ara), ("clock", 1.0),
                                    ("consumer", cons_ara)]:
            name = f"{prefix}_{archetype}"
            if prefix == "Target" and archetype == "engine":
                ara_val = ara; ba = fit_ba
            else: ba = 1.0
            node = LogSingularityNode(name, rung_period, ara_val,
                                       rung_power, ba, archetype,
                                       seed_ara=ara, rung_offset=offset,
                                       decay_func=decay_func)
            node.set_t_ref(fit_tr)
            all_nodes[name] = node
            if archetype == "engine": engine_nodes[prefix] = node

    # PROVEN PIPES
    rung_list = [(rp, prefix, offset) for rp, _, prefix, _, _, offset in rungs]
    for i, (rp, prefix, offset) in enumerate(rung_list):
        engine = all_nodes[f"{prefix}_engine"]
        clock_n = all_nodes[f"{prefix}_clock"]
        consumer = all_nodes[f"{prefix}_consumer"]
        consumer.add_drain(engine, rate=PHI_LEAK)
        clock_n.add_drain(engine, rate=PHI_LEAK)
        engine.add_feed_target(clock_n, INV_PHI_4, "horizontal")
        clock_n.add_feed_target(consumer, INV_PHI_4, "horizontal")
        if i < len(rung_list) - 1:
            below_prefix = rung_list[i + 1][1]
            engine.add_feed_target(all_nodes[f"{below_prefix}_engine"],
                                   INV_PHI_4, "vertical_down")
        if i > 0:
            above_prefix = rung_list[i - 1][1]
            consumer.add_drain(all_nodes[f"{above_prefix}_engine"],
                              rate=PHI_LEAK * INV_PHI)

    # TEMPORAL GEAR WIRING
    for i, (rp, prefix, offset) in enumerate(rung_list):
        engine = engine_nodes[prefix]
        if i < len(rung_list) - 1:
            child_prefix = rung_list[i + 1][1]
            engine.child_engine = engine_nodes[child_prefix]
        if i > 0:
            parent_prefix = rung_list[i - 1][1]
            engine.parent_engine = engine_nodes[parent_prefix]

    engine_nodes["Target"].prev_amp = peaks[0]

    # Simulate
    dt = period * 0.005
    sim_start = times[0] - sim_margin
    sim_end = times[-1] + sim_margin
    sim_time = sim_start
    while sim_time < sim_end:
        for name, node in all_nodes.items():
            fill_rate = dt / node.period
            node.accumulated_energy += fill_rate * node.singularity_threshold
        for name, node in all_nodes.items():
            if node.archetype in ("consumer", "clock"):
                node.apply_drain(dt)
        all_events = []
        for name, node in all_nodes.items():
            events = node.check_snap(sim_time)
            all_events.extend(events)
        depth = 0
        while all_events and depth < 50:
            new_events = []
            for ev in all_events:
                ev["target"].absorb_transfer(ev["energy"], ev["source_rung"])
                triggered = ev["target"].check_snap(ev["time"])
                new_events.extend(triggered)
            all_events = new_events
            depth += 1
        sim_time += dt

    target_node = engine_nodes["Target"]
    snap_t = np.array(target_node.snap_times)
    snap_a = np.array(target_node.snap_amplitudes)
    if len(snap_t) == 0:
        return {"mae": 999, "corr": 0, "snaps": 0, "failed": True,
                "name": system_name, "fit_mae": fit_mae, "bounces": 0}
    errors, preds = [], []
    for i in range(len(times)):
        idx = np.argmin(np.abs(snap_t - times[i]))
        preds.append(snap_a[idx])
        errors.append(abs(snap_a[idx] - peaks[i]))
    mae = np.mean(errors)
    corr = np.corrcoef(preds, peaks)[0, 1] if len(preds) > 2 else 0
    sine_mae = np.mean(np.abs(peaks - np.mean(peaks)))

    rung_snap_counts = {}
    for prefix in engine_nodes:
        rung_snap_counts[prefix] = engine_nodes[prefix].local_ticks

    valve_hist = target_node.valve_history
    tilt_raw = target_node.gear_tilts_raw
    tilt_gated = target_node.gear_tilts_gated
    mom_hist = target_node.momentum_history
    dec_hist = target_node.decay_history

    return {
        "mae": mae, "fit_mae": fit_mae, "corr": corr,
        "snaps": target_node.local_ticks,
        "preds": np.array(preds), "errors": np.array(errors),
        "sine_mae": sine_mae,
        "improvement": (1 - mae / sine_mae) * 100 if sine_mae > 0 else 0,
        "failed": False, "name": system_name,
        "bounces": target_node.bounce_count,
        "rung_snaps": rung_snap_counts,
        "avg_valve": np.mean(valve_hist) if valve_hist else 0,
        "avg_tilt_raw": np.mean(np.abs(tilt_raw)) if tilt_raw else 0,
        "avg_tilt_gated": np.mean(np.abs(tilt_gated)) if tilt_gated else 0,
        "valve_range": (min(valve_hist), max(valve_hist)) if valve_hist else (0, 0),
        "inhales": target_node.inhale_count,
        "exhales": target_node.exhale_count,
        "avg_momentum": np.mean(np.abs(mom_hist)) if mom_hist else 0,
        "max_momentum": max(np.abs(mom_hist)) if mom_hist else 0,
        "avg_decay": np.mean(dec_hist) if dec_hist else 0,
        "decay_range": (min(dec_hist), max(dec_hist)) if dec_hist else (0, 0),
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


VARIANTS = {
    "A": {
        "label": "Single log: log(1+ARA)/log(1+φ)",
        "decay_func": decay_single_log,
    },
    "B": {
        "label": "Energy-gated: log curve × momentum energy",
        "decay_func": decay_energy_gated,
    },
    "C": {
        "label": "Double log: log(1+log(1+ARA×φ)) — brutal compression",
        "decay_func": decay_double_log,
    },
}


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════

print("=" * 78)
print("Script 243AB — Log-Singularity Breathing")
print("=" * 78)
print()
print("  The golden exhale must be EARNED. φ is a singularity —")
print("  the approach is log-compressed. Last 10% costs more than first 90%.")
print()
print("  Variant B: momentum IS energy. Big tilt → earn golden exhale.")
print("             Small tilt → stuck in log compression.")
print()

# Show decay curves
print("  Decay rates (without energy gating):")
print(f"  {'ARA':>6} │ {'Role':>10} │ {'A (log)':>8} │ {'C (log²)':>9} │ {'243Y-B':>7}")
print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*8}─┼─{'─'*9}─┼─{'─'*7}")
for ara, role in [(0.15, "deep cons"), (INV_PHI, "consumer"), (1.0, "clock"),
                  (PHI, "ENGINE"), (2.0, "exotherm")]:
    a = decay_single_log(ara)
    c = decay_double_log(ara)
    marker = " ◄ φ" if abs(ara - PHI) < 0.01 else ""
    print(f"  {ara:>6.3f} │ {role:>10} │ {a:>8.4f} │ {c:>9.4f} │ {INV_PHI:>7.4f}{marker}")

print()
print("  Variant B energy boost at different momentum levels (ARA=1.0):")
print(f"  {'momentum':>10} │ {'energy':>7} │ {'base':>6} │ {'boosted':>8}")
print(f"  {'─'*10}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*8}")
base_at_1 = decay_single_log(1.0)
for mom in [0.0, 0.001, 0.005, 0.01, 0.02, 0.05]:
    boosted = decay_energy_gated(1.0, mom)
    energy = math.log(1.0 + abs(mom) * PHI_2)
    print(f"  {mom:>10.3f} │ {energy:>7.4f} │ {base_at_1:>6.4f} │ {boosted:>8.4f}")
print()

ref = {
    '235b':  {"Solar (SSN)": 46.30, "ENSO (ONI)": 0.44, "Sanriku EQ": 1.19},
    '243O-C': {"Solar (SSN)": 48.45, "ENSO (ONI)": 0.41, "Sanriku EQ": 1.07},
    '243Y-B': {"Solar (SSN)": 49.83, "ENSO (ONI)": 0.47, "Sanriku EQ": 1.15},
}

for var_key in ["A", "B", "C"]:
    var = VARIANTS[var_key]
    print(f"\n{'─' * 78}")
    print(f"  VARIANT {var_key}: {var['label']}")
    print(f"{'─' * 78}")
    print(f"\n  {'System':<17} │ {'235b':>7} │ {'O-C':>7} │ {'Y-B':>7} │ "
          f"{'243AB':>7} │ {'Δ vs 235b':>9} │ {'Δ vs O-C':>9} │ {'avg_dec':>7}")
    print(f"  {'─'*17}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─"
          f"{'─'*7}─┼─{'─'*9}─┼─{'─'*9}─┼─{'─'*7}")

    var_results = {}
    for name, times, peaks, period, ara, rung in SYSTEMS:
        print(f"  Running {name}...", end="", flush=True)
        res = run_log_singularity(
            times, peaks, period=period, ara=ara, target_rung=rung,
            system_name=name, decay_func=var["decay_func"])
        var_results[name] = res

        if res["failed"]:
            print(f"\r  {name:<17} │  ---    │  ---    │  ---    │  FAIL   │")
            continue

        d235 = res['mae'] - ref['235b'][name]
        dOC = res['mae'] - ref['243O-C'][name]
        b235 = " ✓" if d235 < 0 else ""
        bOC = " ✓" if dOC < 0 else ""
        print(f"\r  {name:<17} │ {ref['235b'][name]:>7.2f} │ {ref['243O-C'][name]:>7.2f} │ "
              f"{ref['243Y-B'][name]:>7.2f} │ {res['mae']:>7.2f} │ "
              f"{d235:>+8.2f}{b235} │ {dOC:>+8.2f}{bOC} │ {res['avg_decay']:>7.4f}")

    # Diagnostics
    print(f"\n  Diagnostics:")
    for name in var_results:
        r = var_results[name]
        if r["failed"]: continue
        pct_exhale = r['exhales'] / max(1, r['inhales'] + r['exhales']) * 100
        dr = r['decay_range']
        print(f"    {name:<16}: valve={r['avg_valve']:.4f}, "
              f"in={r['inhales']}/ex={r['exhales']} ({pct_exhale:.0f}%), "
              f"avg_mom={r['avg_momentum']:.6f}, max_mom={r['max_momentum']:.6f}")
        print(f"    {'':16}  decay_avg={r['avg_decay']:.4f}, "
              f"decay_range=[{dr[0]:.4f}, {dr[1]:.4f}], "
              f"tilt_raw={r['avg_tilt_raw']:.6f}, tilt_eff={r['avg_tilt_gated']:.6f}")

    # Solar per-cycle
    if "Solar (SSN)" in var_results and not var_results["Solar (SSN)"]["failed"]:
        ra = var_results["Solar (SSN)"]
        print(f"\n  Solar per-cycle (Variant {var_key}):")
        print(f"    {'C':>3} {'Year':>7} {'Act':>6} │ {'Pred':>6} {'Err':>5} │")
        for i in range(len(solar_t)):
            err_flag = " ◀" if ra['errors'][i] > 60 else ""
            print(f"    C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
                  f"{ra['preds'][i]:>6.1f} {ra['errors'][i]:>5.1f} │{err_flag}")


print(f"\n{'=' * 78}")
print("SUMMARY — 243AB Log-Singularity Breathing")
print("=" * 78)
print()
print("  The approach to φ is LOG-COMPRESSED.")
print("  Variant B: momentum = energy to approach the singularity.")
print("  Engines earn the golden exhale. Consumers can't afford it.")
print()
print(f"  Baselines: 235b Solar=46.30, 243O-C Solar=48.45, 243Y-B Solar=49.83")
print(f"  Records: ENSO=0.39 (243W-A), EQ=0.41 (243W-C)")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
print("=" * 78)
