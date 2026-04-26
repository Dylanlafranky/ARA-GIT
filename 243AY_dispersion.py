#!/usr/bin/env python3
"""
Script 243AY — Dispersion: Period-Dependent Gate Speed

Based on 243AJ champion (Solar LOO 42.89).

WAVE PHYSICS STEP 3: Dispersion — different periods travel at different speeds.
In a dispersive medium, wave velocity v = v(λ). For ARA cascades, this means
the Gleissberg envelope should NOT modulate all rungs identically. Longer-period
rungs (further from the fundamental) should see a slower effective gate, because
their larger wavelength means they sample the envelope over more time.

Implementation: Each rung gets its own gate phase, shifted by the ratio of
its period to the Gleissberg period. The velocity ratio is (period_j / gleissberg),
so longer periods advance the gate MORE slowly:

  gp_j = TAU * (t - t_ref) / (live_gleissberg * (live_periods[j] / live_gleissberg)^(1/φ⁴))

This is a VERY gentle dispersion — the exponent 1/φ⁴ ≈ 0.146 means a rung
twice the Gleissberg period only slows by ~10%.

  Still disabled:
  1. Memory buffer — OFF
  2. Grief bleed — OFF
  3. ARA-dependent momentum — OFF (hardcoded 0.3)
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
    """φ-decaying weighted average of past amplitudes.
    N-1: weight 1.0, N-2: weight 1/φ, N-3: weight 1/φ², etc.
    Returns weighted average, or current_amp if no history."""
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
        weight = INV_PHI ** i  # most recent = 1.0, then 1/φ, 1/φ², ...
        weighted_sum += amp * weight
        total_weight += weight
    return weighted_sum / total_weight if total_weight > 0 else amps[-1]


# ── FIX 3: ARA-dependent momentum ──
def ara_momentum(ara):
    """Derive triangle rider momentum from ARA.
    Consumer (0.15) → 0.07 (stops dead).
    Clock (1.0) → 0.35 (moderate).
    Engine (φ) → 0.48 (bounces hard).
    Exothermic (2.0) → 0.55."""
    return math.log1p(max(0.01, ara)) / 2.0


# ── FIX 4: Midline from 237d ──
def ara_midline(ara):
    """midline = 1 + acc_frac × (ARA - 1), where acc_frac = 1/(1+ARA).
    Solar (φ): 1.236. Consumer (1/φ): 0.764. Clock (1.0): 1.0."""
    acc = 1.0 / (1.0 + max(0.01, ara))
    return 1.0 + acc * (ara - 1.0)


# ── Double log decay (champion from 243AB-C) ──
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
    Node with all four engine memory fixes:
    1. φ-decaying memory buffer for inst_ara computation
    2. Slow-bleed asymmetric grief
    3. ARA-dependent momentum
    4. Midline reintegration
    Plus: double-log singularity breathing from 243AB-C.
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
        # FIX 3 DISABLED: hardcoded 0.3 (not ARA-dependent)
        self.momentum_param = 0.3
        self.elasticity = INV_PHI
        self.seed_ara = seed_ara or ara
        self.rung_offset = rung_offset
        self.child_sign = child_sign
        self.parent_sign = parent_sign
        self.gate_send = gate_send
        # FIX 4: Midline
        self.midline = ara_midline(ara)

        # FIX 5: Amplitude scale — the "other half" of accumulate/snap
        # Use midline itself as the scale: Solar 1.236, Consumer 0.764, Clock 1.0
        self.amp_scale = self.midline

        self.child_engine = None
        self.parent_engine = None
        self.child_last_snap_amp = None
        self.parent_last_snap_amp = None

        # Asymmetric breathing state
        self.tilt_momentum = 0.0

        # FIX 2 DISABLED: no grief reservoir (instant correction)

    def update_gear_state(self):
        if self.child_engine is not None and self.child_engine.snap_amplitudes:
            self.child_last_snap_amp = self.child_engine.snap_amplitudes[-1]
        if self.parent_engine is not None and self.parent_engine.snap_amplitudes:
            self.parent_last_snap_amp = self.parent_engine.snap_amplitudes[-1]

    def cascade_shape(self, t):
        if self.t_ref is None: return 1.0
        self.update_gear_state()

        # ── FIX 1 DISABLED: Use prev_amp only (original 243AB-C behavior) ──
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

        # ── Triangle rider (FIX 3: ARA-dependent momentum already set) ──
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

        # ── DISPERSION v3: phase velocity depends on period ──
        # Instead of modifying the gate, add a period-dependent phase offset
        # to each rung's wave. Longer periods accumulate less phase per unit time
        # (slower velocity), creating a dispersion-induced phase lag.
        # The offset is: Δφ_j = (period_j / schwabe - 1) × 1/φ⁹
        # This is zero for the Schwabe (fundamental) and grows for longer periods.
        for j in range(len(phases)):
            disp_offset = (live_periods[j] / self.schwabe - 1.0) * INV_PHI_9
            phases[j] += disp_offset
        # Recompute cos/sin with dispersed phases
        cos_vals = [math.cos(ph) for ph in phases]
        sin_vals = [math.sin(ph) for ph in phases]

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

        # ── FIX 2 DISABLED: Original instant grief correction (from 235b) ──
        if self.prev_amp is not None:
            prev_dev = (self.prev_amp - self.base_amp) / self.base_amp
            grief_mult = 1.0 + INV_PHI_3 * (-prev_dev) * math.exp(-PHI)
            shape *= grief_mult

        if self.wall_energy > 0:
            shape *= (1 + self.wall_energy * INV_PHI_3)
            self.wall_energy *= INV_PHI

        # ── FIX 4: Midline shift ──
        shape += (self.midline - 1.0)

        # ── FIX 5: Amplitude scale — the other half ──
        deviation = shape - self.midline
        shape = self.midline + deviation * self.amp_scale

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
    ba_lo = np.mean(peaks) * 0.3; ba_hi = np.mean(peaks) * 1.8  # wider for midline
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


def run_full_simulation(times, peaks, period, ara, target_rung,
                        fit_tr, fit_ba, sim_margin=None):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

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
            node = EngineMemoryNode(name, rung_period, ara_val,
                                     rung_power, ba, archetype,
                                     seed_ara=ara, rung_offset=offset)
            node.set_t_ref(fit_tr)
            all_nodes[name] = node
            if archetype == "engine": engine_nodes[prefix] = node

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

    for i, (rp, prefix, offset) in enumerate(rung_list):
        engine = engine_nodes[prefix]
        if i < len(rung_list) - 1:
            child_prefix = rung_list[i + 1][1]
            engine.child_engine = engine_nodes[child_prefix]
        if i > 0:
            parent_prefix = rung_list[i - 1][1]
            engine.parent_engine = engine_nodes[parent_prefix]

    engine_nodes["Target"].prev_amp = peaks[0]

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
    return np.array(target_node.snap_times), np.array(target_node.snap_amplitudes)


def run_full_fit(times, peaks, period, ara, target_rung, system_name):
    """Run full fit (no LOO) and return MAE + per-point results."""
    fit_tr, fit_ba, fit_mae = grid_search(period, ara, target_rung, times, peaks)
    snap_t, snap_a = run_full_simulation(times, peaks, period, ara, target_rung,
                                          fit_tr, fit_ba)
    if len(snap_t) == 0:
        return {"mae": 999, "failed": True, "name": system_name}

    errors, preds = [], []
    for i in range(len(times)):
        idx = np.argmin(np.abs(snap_t - times[i]))
        preds.append(snap_a[idx])
        errors.append(abs(snap_a[idx] - peaks[i]))
    mae = np.mean(errors)
    sine_mae = np.mean(np.abs(peaks - np.mean(peaks)))
    return {
        "mae": mae, "fit_mae": fit_mae, "sine_mae": sine_mae,
        "preds": np.array(preds), "errors": np.array(errors),
        "failed": False, "name": system_name,
    }


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
        # FIX 1: Feed full history, not just prev_amp
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
print("Script 243AJ — Ablation: Midline ONLY")
print("=" * 78)
print()
print("  Fix 1: Gleissberg memory buffer                              ← OFF")
print("  Fix 2: Grief bleed                                           ← OFF")
print("  Fix 3: ARA-dependent momentum                                ← OFF")
print("  Fix 4: Midline reintegration (wave pivots around ARA midline) ← ON")
print()

# Show fix values
print("  ARA-dependent parameters:")
print(f"  {'ARA':>6} │ {'Role':>10} │ {'Momentum':>8} │ {'Midline':>8} │ {'AmpScale':>8} │ {'Mid×Amp':>8} │ {'Decay@φ':>8}")
print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}")
for ara, role in [(0.15, "deep cons"), (INV_PHI, "consumer"), (1.0, "clock"),
                  (PHI, "ENGINE"), (2.0, "exotherm")]:
    snap = ara / (1.0 + ara)
    amp_s = 1.0 + snap * (ara - 1.0) * PHI
    mid = ara_midline(ara)
    print(f"  {ara:>6.3f} │ {role:>10} │ {ara_momentum(ara):>8.4f} │ "
          f"{mid:>8.4f} │ {amp_s:>8.4f} │ {mid*amp_s:>8.4f} │ {decay_double_log(ara):>8.4f}")
print()

# ── FULL FIT ──
print("─" * 78)
print("  FULL FIT (all data)")
print("─" * 78)

ref_prev = {"Solar (SSN)": 45.56, "ENSO (ONI)": 0.48, "Sanriku EQ": 0.70}
ref_235b = {"Solar (SSN)": 46.30, "ENSO (ONI)": 0.44, "Sanriku EQ": 1.19}

print(f"\n  {'System':<17} │ {'235b':>7} │ {'243AB-C':>7} │ {'243AE':>7} │ {'Δ vs 235b':>9} │ {'Δ vs AB-C':>9}")
print(f"  {'─'*17}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*9}─┼─{'─'*9}")

full_results = {}
for name, times, peaks, period, ara, rung in SYSTEMS:
    print(f"  Running {name}...", end="", flush=True)
    res = run_full_fit(times, peaks, period, ara, rung, name)
    full_results[name] = res
    if res["failed"]:
        print(f"\r  {name:<17} ��  FAIL")
        continue
    d235 = res['mae'] - ref_235b[name]
    dABC = res['mae'] - ref_prev[name]
    b235 = " ✓" if d235 < 0 else ""
    bABC = " ✓" if dABC < 0 else ""
    print(f"\r  {name:<17} │ {ref_235b[name]:>7.2f} │ {ref_prev[name]:>7.2f} │ "
          f"{res['mae']:>7.2f} │ {d235:>+8.2f}{b235} │ {dABC:>+8.2f}{bABC}")

# Solar per-cycle
if "Solar (SSN)" in full_results and not full_results["Solar (SSN)"]["failed"]:
    ra = full_results["Solar (SSN)"]
    print(f"\n  Solar per-cycle:")
    print(f"    {'C':>3} {'Year':>7} {'Act':>6} │ {'Pred':>6} {'Err':>5} │")
    for i in range(len(solar_t)):
        flag = " ◀" if ra['errors'][i] > 60 else ""
        print(f"    C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
              f"{ra['preds'][i]:>6.1f} {ra['errors'][i]:>5.1f} │{flag}")

# ── FORMULA LOO ──
print(f"\n{'─' * 78}")
print("  FORMULA LOO (cascade_amplitude, refit per fold)")
print("─" * 78)

ref_loo_prev = {"Solar (SSN)": 68.95, "ENSO (ONI)": 0.63, "Sanriku EQ": 1.33}
best_loo_ever = {"Solar (SSN)": 31.94, "ENSO (ONI)": 0.382, "Sanriku EQ": 3.48}

print(f"\n  {'System':<17} │ {'Prev LOO':>8} │ {'Best Ever':>9} │ {'243AD LOO':>9} �� "
      f"{'Sine':>6} │ {'LOO/Sine':>8} │ {'Corr':>6}")
print(f"  {'─'*17}─┼─{'─'*8}─┼─{'─'*9}─┼─{'─'*9}─┼─{'─'*6}─┼─{'─'*8}─┼─{'─'*6}")

loo_results = {}
for name, times, peaks, period, ara, rung in SYSTEMS:
    t0 = clock_time.time()
    print(f"  Running {name} LOO ({len(times)} folds)...", end="", flush=True)
    res = run_formula_loo(times, peaks, period, ara, rung, name)
    loo_results[name] = res
    el = clock_time.time() - t0
    vs_sine = "BEAT!" if res['ratio'] < 1.0 else f"+{(res['ratio']-1)*100:.0f}%"
    print(f"\r  {name:<17} │ {ref_loo_prev[name]:>8.2f} │ {best_loo_ever[name]:>9.2f} │ "
          f"{res['loo_mae']:>9.2f} │ {res['sine_mae']:>6.2f} │ {res['ratio']:>8.3f} │ "
          f"{res['corr']:>6.3f}  ({el:.0f}s)")

# Solar LOO per-cycle
if "Solar (SSN)" in loo_results:
    print(f"\n  Solar LOO per-cycle:")
    sr = loo_results["Solar (SSN)"]
    print(f"    {'C':>3} {'Year':>7} {'Act':>6} │ {'LOO Pred':>8} {'LOO Err':>7} │")
    for i in range(len(solar_t)):
        flag = " ◀" if sr['errors'][i] > 80 else ""
        print(f"    C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
              f"{sr['preds'][i]:>8.1f} {sr['errors'][i]:>7.1f} │{flag}")


# ════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════

print(f"\n{'=' * 78}")
print("SUMMARY — 243AY Dispersion (Period-Dependent Gate Speed)")
print("=" * 78)
print()
print("  Full-fit comparison:")
for name in full_results:
    r = full_results[name]
    if r["failed"]: continue
    print(f"    {name:<17}: 235b={ref_235b[name]:.2f} → 243AB-C={ref_prev[name]:.2f} → "
          f"243AD={r['mae']:.2f}")
print()
print("  LOO comparison:")
for name in loo_results:
    r = loo_results[name]
    full_mae = full_results[name]['mae'] if not full_results[name]['failed'] else 999
    loo_full = r['loo_mae'] / full_mae if full_mae > 0 else 999
    print(f"    {name:<17}: LOO={r['loo_mae']:.2f}, Sine={r['sine_mae']:.2f}, "
          f"LOO/Sine={r['ratio']:.3f}, LOO/Full={loo_full:.2f}x")
print()
print("  Best LOO ever: Solar=31.94, ENSO=0.382, EQ=3.48")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
print("=" * 78)
