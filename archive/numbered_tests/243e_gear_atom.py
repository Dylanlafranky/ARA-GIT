#!/usr/bin/env python3
"""
Script 243e — Gear Mechanism Atom: Asymmetric Directional Decay

Dylan's insight: "The formula runs DOWN and to the right, but they
accumulate and propel it UP to the next system like a gear."

The cascade is a GEAR TRAIN:
  - Engine cascade flows DOWN through rungs (Gleissberg → Target → Below)
    → FULL STRENGTH, no decay. This is the proven mechanism.
  - Consumers at each rung ACCUMULATE the downward energy
    → Then PROPEL it back UP like meshing teeth
    → This upward return DECAYS 1/φ per step
  - At each rung, the gear mesh point is where engine meets consumer
    → One turns clockwise (engine, down), the other counter (consumer, up)

Implementation:
  - Downward pipe rates: UNCHANGED from 235b (proven)
  - Upward pipe rates: DECAYED by 1/φ per rung step from target
  - Horizontal (engine→consumer at same rung): FULL, this is the mesh
  - Geometric ARAs from 243b: KEPT (proven for EQ)
  - Connection field whisper: DIRECTIONAL
    → Engine partners: in-phase, full coupling
    → Consumer partners: anti-phase, step-decayed upward

243b reference: Solar 56.84, ENSO 0.43, EQ 0.60 (-49.9%)
Champion: Solar MAE = 28.11 (236j triangle rider)
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

# Triangle rider basis from 236j
SPACE_BASIS = np.array([9.0, 6.0, 2.0, -2.0])
TIME_BASIS  = np.array([5.0, 3.0, 1.0, -1.0])
RAT_BASIS   = np.array([6.0, 4.0, 1.0, -1.0])
BEST_STEER = 0.2
BEST_MOMENTUM = 0.3


# ════════════════════════════════════════════════════════════════
# CONNECTION FIELD — derive partner ARAs from geometry
# ════════════════════════════════════════════════════════════════

def derive_atom_nodes(seed_ara, seed_period):
    """Full φ⁹ atom: 9 nodes across 3 rungs."""
    mirror_floor = 0.15
    nodes = []
    for rung_offset in [-1, 0, 1]:
        if rung_offset == 0:
            p = seed_period
            engine_ara = seed_ara
            mirror_ara = max(mirror_floor, 2.0 - seed_ara)
        elif rung_offset == 1:
            p = seed_period * PHI
            engine_ara = seed_ara / PHI
            mirror_ara = max(mirror_floor, 2.0 - engine_ara)
        elif rung_offset == -1:
            p = seed_period / PHI
            engine_ara = min(2.0, seed_ara * PHI)
            mirror_ara = max(mirror_floor, 2.0 - engine_ara)
        nodes.append((rung_offset, 'engine',   engine_ara, p))
        nodes.append((rung_offset, 'clock',    1.0,        p))
        nodes.append((rung_offset, 'consumer', mirror_ara, p))
    return nodes


def build_gear_partners(seed_ara, seed_period):
    """
    Build connection field partners with GEAR DIRECTIONALITY.

    Engine partners (downstream cascade): full coupling, in-phase
    Consumer partners (upstream return): step-decayed, anti-phase
    Clock partners (mesh points): quadrature, moderate coupling
    """
    atom = derive_atom_nodes(seed_ara, seed_period)
    partners = []

    for roff, role, ara, period in atom:
        if roff == 0 and role == 'engine':
            continue  # skip seed itself

        rung_dist = abs(roff)

        if role == 'engine':
            # Engine partners: downstream cascade, FULL STRENGTH
            # These drive the gear train down — no decay
            partners.append({
                'period': period,
                'coupling': INV_PHI_4,  # full
                'phase_type': 'in_phase',
                'direction': 'down' if roff > 0 else 'up',
                'role': role,
                'rung_offset': roff,
                'decay': 1.0,  # no decay for engine cascade
            })
        elif role == 'consumer':
            # Consumer partners: upstream return gear, STEP DECAYED
            # These accumulate and push up — decay 1/φ per step
            upward_decay = INV_PHI ** (rung_dist + 1)  # +1 because horizontal cross is already 1 step
            partners.append({
                'period': period,
                'coupling': INV_PHI_4 * upward_decay,
                'phase_type': 'anti',  # counter-rotating gear
                'direction': 'return',
                'role': role,
                'rung_offset': roff,
                'decay': upward_decay,
            })
        elif role == 'clock':
            # Clock partners: mesh points, moderate
            mesh_decay = INV_PHI ** max(1, rung_dist)
            partners.append({
                'period': period,
                'coupling': INV_PHI_4 * mesh_decay,
                'phase_type': 'quadrature',
                'direction': 'mesh',
                'role': role,
                'rung_offset': roff,
                'decay': mesh_decay,
            })

    return partners


# ════════════════════════════════════════════════════════════════
# EXEC 235b
# ════════════════════════════════════════════════════════════════

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
pipe_transfer_reverb = ns_235b['pipe_transfer_reverb']
run_universal_vehicle = ns_235b['run_universal_vehicle']


# ════════════════════════════════════════════════════════════════
# TRIANGLE RIDER
# ════════════════════════════════════════════════════════════════

def find_triangle_position(target_ara, space_bias=0.3):
    if target_ara <= 0: return (1.0, 0.0, 0.0)
    if target_ara >= 2.0: return (0.0, 1.0, 0.0)
    f_min = target_ara / 2.0
    f_max = target_ara / PHI
    f_min = max(f_min, 0.001)
    f_max = min(f_max, 0.999)
    if f_min > f_max:
        f_min = f_max = min(0.999, max(0.001, (f_min + f_max) / 2))
    f = f_max - space_bias * (f_max - f_min)
    f = max(0.001, min(0.999, f))
    s = 1.0 - f
    t = (target_ara - PHI * f) / (2.0 - PHI)
    r = f - t
    t = max(0, min(f, t))
    r = max(0, f - t)
    s = max(0, s)
    total = s + t + r
    return (s / total, t / total, r / total)

def blend_distances(s, t, r):
    return s * SPACE_BASIS + t * TIME_BASIS + r * RAT_BASIS

def clamp_to_triangle(s, t, r):
    wall_hit = None
    wall_energy = 0.0
    if s < 0:
        wall_energy = max(wall_energy, abs(s)); wall_hit = 's'; s = 0.0
    if t < 0:
        wall_energy = max(wall_energy, abs(t)); wall_hit = 't'; t = 0.0
    if r < 0:
        wall_energy = max(wall_energy, abs(r)); wall_hit = 'r'; r = 0.0
    total = s + t + r
    if total > 0:
        s, t, r = s / total, t / total, r / total
    else:
        s, t, r = 1/3, 1/3, 1/3
    return s, t, r, wall_hit, wall_energy


# ════════════════════════════════════════════════════════════════
# GEAR ATOM NODE
# ════════════════════════════════════════════════════════════════

class GearAtomNode(OrigARANode):
    """
    Triangle rider + GEAR-DIRECTIONAL connection field.

    The gear mechanism:
      - Engine cascade partners: full coupling, in-phase (drive shaft)
      - Consumer return partners: decayed coupling, anti-phase (return gear)
      - Clock mesh partners: moderate coupling, quadrature (gear teeth)
    """

    def __init__(self, name, period, ara, rung, base_amp, archetype,
                 seed_ara=None, rung_offset=0):
        super().__init__(name, period, ara, rung, base_amp, archetype)

        s, t, r = find_triangle_position(ara)
        self.pos_s, self.pos_t, self.pos_r = s, t, r
        self.vel_s, self.vel_t, self.vel_r = 0.0, 0.0, 0.0
        self.wall_energy = 0.0
        self.bounce_count = 0
        self.steer = BEST_STEER
        self.momentum = BEST_MOMENTUM
        self.elasticity = INV_PHI
        self.seed_ara = seed_ara or ara
        self.rung_offset = rung_offset
        self.field_partners = []

    def set_field_partners(self, partners):
        self.field_partners = partners

    def cascade_shape(self, t):
        if self.t_ref is None:
            return 1.0

        # ── Instantaneous ARA ──
        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

        # ── Triangle rider update ──
        target_s, target_t, target_r = find_triangle_position(inst_ara)
        force_s = (target_s - self.pos_s) * self.steer
        force_t = (target_t - self.pos_t) * self.steer
        force_r = (target_r - self.pos_r) * self.steer

        self.vel_s = self.vel_s * self.momentum + force_s
        self.vel_t = self.vel_t * self.momentum + force_t
        self.vel_r = self.vel_r * self.momentum + force_r

        vel_mean = (self.vel_s + self.vel_t + self.vel_r) / 3
        self.vel_s -= vel_mean
        self.vel_t -= vel_mean
        self.vel_r -= vel_mean

        new_s = self.pos_s + self.vel_s
        new_t = self.pos_t + self.vel_t
        new_r = self.pos_r + self.vel_r
        new_s, new_t, new_r, wall, w_energy = clamp_to_triangle(
            new_s, new_t, new_r)

        if wall is not None:
            self.bounce_count += 1
            self.wall_energy += w_energy
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
        if cp < acc:
            state = (cp / acc) * PHI
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

        # Three-circle blend
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

        # Below-rung collision dampening
        for j in range(1, len(phases)):
            d = live_d[j]
            if d < 0:
                eps_vals[j] /= (1 + collisions[j] * INV_PHI)
                eps_vals[j] *= (1 + collisions[j] * INV_PHI * 0.5)

        # Tension
        for j in range(len(phases)):
            if j > 0:
                eps_vals[j] *= (1 + collisions[j] * INV_PHI)
            tens = -sin_vals[j]
            if inst_ara >= 1.0:
                if tens > 0:
                    eps_vals[j] *= (1 + 0.5 * tens * (PHI - 1))
                else:
                    eps_vals[j] *= (1 + 0.5 * tens * (1 - INV_PHI))
            else:
                log_tens = math.copysign(math.log1p(abs(tens)) / LOG2, tens)
                if log_tens > 0:
                    eps_vals[j] *= (1 + 0.5 * log_tens * (PHI - 1))
                else:
                    eps_vals[j] *= (1 + 0.5 * log_tens * (1 - INV_PHI))

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

        # ══ GEAR-DIRECTIONAL CONNECTION FIELD WHISPER ══
        #
        # The gear mechanism splits the field into two counter-rotating
        # components:
        #
        #   DRIVE (engine partners): Full coupling, in-phase
        #     → These are the downward cascade. They REINFORCE.
        #     → No decay — proven mechanism.
        #
        #   RETURN (consumer partners): Decayed coupling, anti-phase
        #     → These accumulate and push up. Counter-rotating.
        #     → Decay 1/φ per upward step.
        #
        #   MESH (clock partners): Moderate, quadrature
        #     → The gear teeth where drive meets return.
        #
        if self.field_partners:
            drive_sum = 0.0
            return_sum = 0.0
            mesh_sum = 0.0
            drive_weight = 0.0
            return_weight = 0.0
            mesh_weight = 0.0

            for partner in self.field_partners:
                p_period = partner['period']
                p_coupling = partner['coupling']
                p_phase_type = partner['phase_type']

                partner_phase = TAU * (t - self.t_ref) / p_period

                if p_phase_type == 'in_phase':
                    # DRIVE: engine cascade, full strength, reinforcing
                    drive_sum += p_coupling * math.cos(partner_phase)
                    drive_weight += p_coupling
                elif p_phase_type == 'anti':
                    # RETURN: consumer gear, counter-rotating
                    return_sum -= p_coupling * math.cos(partner_phase)
                    return_weight += p_coupling
                elif p_phase_type == 'quadrature':
                    # MESH: clock at gear teeth
                    mesh_sum += p_coupling * math.sin(partner_phase)
                    mesh_weight += p_coupling

            # Normalise each component separately
            if drive_weight > 0:
                drive_sum /= drive_weight
            if return_weight > 0:
                return_sum /= return_weight
            if mesh_weight > 0:
                mesh_sum /= mesh_weight

            # Combine: drive is dominant, return is the new signal,
            # mesh modulates the handoff
            # Budget: 1/φ⁹ total but asymmetrically distributed
            #   Drive:  φ/(φ+1) of budget (engine dominates)
            #   Return: 1/(φ+1) of budget (consumer weaker)
            #   Mesh:   1/φ⁹ × 1/φ (very small modulation)
            drive_budget = INV_PHI_9 * PHI / (PHI + 1)
            return_budget = INV_PHI_9 * 1.0 / (PHI + 1)
            mesh_budget = INV_PHI_9 * INV_PHI

            gear_total = (drive_budget * drive_sum +
                         return_budget * return_sum +
                         mesh_budget * mesh_sum)

            shape *= (1.0 + gear_total)

        return shape


# ════════════════════════════════════════════════════════════════
# BUILD GEAR ATOM VEHICLE
# ════════════════════════════════════════════════════════════════

def build_rung_ladder_gear(target_rung, target_period, seed_ara):
    """
    Build rung ladder with:
      - GEOMETRIC ARAs from 243b (proven for EQ)
      - GEAR-DIRECTIONAL pipe rates:
        → Downward: FULL (proven cascade)
        → Upward: DECAYED (1/φ per step — the return gear)
        → Horizontal: FULL (gear mesh at each rung)
    """
    mirror_floor = 0.15
    atom = derive_atom_nodes(seed_ara, target_period)
    rungs = []

    for offset in range(-2, 5):
        r = target_rung + offset
        if r < 0:
            continue
        p = target_period * PHI**offset

        if offset == 4:   prefix = "Gleissberg"
        elif offset == 1: prefix = "AboveT"
        elif offset == 0: prefix = "Target"
        elif offset == -1: prefix = "BelowT"
        elif offset == -2: prefix = "SubSub"
        elif offset == 2: prefix = "AboveA"
        elif offset == 3: prefix = "AboveB"
        else: prefix = f"R{r}"

        # GEOMETRIC ARAs from connection field (from 243b)
        engine_ara = PHI
        consumer_ara = INV_PHI
        for roff, role, ara, per in atom:
            if roff == offset or (offset > 1 and roff == 1) or (offset < -1 and roff == -1):
                if role == 'engine':
                    engine_ara = ara
                elif role == 'consumer':
                    consumer_ara = ara

        rungs.append((r, p, prefix, engine_ara, consumer_ara, offset))

    return sorted(rungs, key=lambda x: -x[0])


def grid_search_gear(period, ara, rung, times, peaks, n_tr=80, n_ba=40):
    gleissberg = period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * period
    ba_lo = np.mean(peaks) * 0.5
    ba_hi = np.mean(peaks) * 1.5
    t_refs = np.linspace(tr_lo, tr_hi, n_tr)
    base_amps = np.linspace(ba_lo, ba_hi, n_ba)

    best_mae, best_tr, best_ba = 1e9, t_refs[0], base_amps[0]
    for tr in t_refs:
        for ba in base_amps:
            node = GearAtomNode("temp", period, ara, rung, ba, "engine")
            node.set_t_ref(tr)
            errors = []
            for k in range(len(times)):
                node.prev_amp = peaks[k-1] if k > 0 else None
                if k > 0:
                    node.amp_history = list(peaks[:k])
                pred = node.cascade_amplitude(times[k])
                errors.append(abs(pred - peaks[k]))
            mae = np.mean(errors)
            if mae < best_mae:
                best_mae, best_tr, best_ba = mae, tr, ba
    return best_tr, best_ba, best_mae


def run_gear_atom(times, peaks, period, ara, target_rung,
                  system_name="System", sim_margin=None):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

    # Build gear-directional field partners
    gear_partners = build_gear_partners(ara, period)

    fit_tr, fit_ba, fit_mae = grid_search_gear(
        period, ara, target_rung, times, peaks)

    rungs = build_rung_ladder_gear(target_rung, period, ara)

    all_nodes = {}
    engine_nodes = {}

    for rung_power, rung_period, prefix, eng_ara, cons_ara, offset in rungs:
        dist_from_target = abs(offset)

        for archetype, ara_val in [("engine", eng_ara), ("clock", 1.0),
                                    ("consumer", cons_ara)]:
            name = f"{prefix}_{archetype}"
            if prefix == "Target" and archetype == "engine":
                ara_val = ara
                ba = fit_ba
            else:
                ba = 1.0

            node = GearAtomNode(name, rung_period, ara_val,
                                rung_power, ba, archetype,
                                seed_ara=ara, rung_offset=offset)
            node.set_t_ref(fit_tr)

            if prefix == "Target" and archetype == "engine":
                node.set_field_partners(gear_partners)

            all_nodes[name] = node
            if archetype == "engine":
                engine_nodes[prefix] = node

    # Wire connections: GEAR-DIRECTIONAL pipe rates
    rung_list = [(rp, prefix, offset)
                 for rp, _, prefix, _, _, offset in rungs]

    for i, (rp, prefix, offset) in enumerate(rung_list):
        engine = all_nodes[f"{prefix}_engine"]
        clock_n = all_nodes[f"{prefix}_clock"]
        consumer = all_nodes[f"{prefix}_consumer"]

        # HORIZONTAL: Full coupling at each rung (gear mesh point)
        consumer.add_drain(engine, rate=PHI_LEAK)
        clock_n.add_drain(engine, rate=PHI_LEAK)
        engine.add_feed_target(clock_n, INV_PHI_4, "horizontal")
        clock_n.add_feed_target(consumer, INV_PHI_4, "horizontal")

        # VERTICAL DOWN: Full coupling (engine cascade, proven)
        if i < len(rung_list) - 1:
            below_prefix = rung_list[i + 1][1]
            engine.add_feed_target(all_nodes[f"{below_prefix}_engine"],
                                   INV_PHI_4, "vertical_down")

        # VERTICAL UP: DECAYED coupling (consumer return gear)
        # The return gear weakens with each upward step
        if i > 0:
            above_prefix = rung_list[i - 1][1]
            above_offset = rung_list[i - 1][2]
            # Decay based on distance from target (upward steps)
            upward_dist = abs(offset)  # how far below the target
            upward_decay = INV_PHI ** upward_dist
            upward_rate = PHI_LEAK * INV_PHI * upward_decay
            consumer.add_drain(all_nodes[f"{above_prefix}_engine"],
                              rate=upward_rate)

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

    # Gear diagnostics
    gear_diag = {'drive': [], 'return': [], 'mesh': []}
    for p in gear_partners:
        if p['phase_type'] == 'in_phase':
            gear_diag['drive'].append(p)
        elif p['phase_type'] == 'anti':
            gear_diag['return'].append(p)
        else:
            gear_diag['mesh'].append(p)

    return {
        "mae": mae, "fit_mae": fit_mae, "corr": corr,
        "snaps": target_node.local_ticks,
        "preds": np.array(preds), "errors": np.array(errors),
        "sine_mae": sine_mae,
        "improvement": (1 - mae / sine_mae) * 100 if sine_mae > 0 else 0,
        "failed": False, "name": system_name,
        "snap_times": snap_t, "snap_amps": snap_a,
        "fit_tr": fit_tr, "fit_ba": fit_ba,
        "bounces": target_node.bounce_count,
        "gear_diag": gear_diag,
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
print("Script 243e — Gear Mechanism Atom: Asymmetric Directional Decay")
print("=" * 78)
print()
print("GEAR TRAIN: cascade DOWN (full) → accumulate → return UP (1/φ decay)")
print("Engine pipes DOWN: proven, untouched")
print("Consumer pipes UP: decayed 1/φ per upward step")
print("Horizontal mesh: full coupling (gear teeth at each rung)")
print()

# Show gear structure
print("GEAR FIELD STRUCTURE:")
print("─" * 78)
for name, times, peaks, period, ara, rung in SYSTEMS:
    partners = build_gear_partners(ara, period)
    print(f"\n  {name} (ARA={ara:.3f}):")
    print(f"    {'Component':<10} │ {'Role':<10} {'Rung':>5} │ {'Coupling':>10} {'Decay':>8} │ {'Phase':>12}")
    print(f"    {'─'*10}─┼─{'─'*10} {'─'*5}─┼─{'─'*10} {'─'*8}─┼─{'─'*12}")
    for p in partners:
        comp = p['direction'].upper()
        print(f"    {comp:<10} │ {p['role']:<10} {p['rung_offset']:>+5d} │ "
              f"{p['coupling']:>10.6f} {p['decay']:>8.4f} │ {p['phase_type']:>12}")

    # Show gear ratio
    drive = [p for p in partners if p['direction'] == 'down' or (p['direction'] == 'up' and p['phase_type'] == 'in_phase')]
    ret = [p for p in partners if p['direction'] == 'return']
    drive_c = sum(p['coupling'] for p in drive) if drive else 0
    ret_c = sum(p['coupling'] for p in ret) if ret else 0
    ratio = drive_c / ret_c if ret_c > 0 else float('inf')
    print(f"    Drive/Return ratio: {ratio:.2f}:1")

print()

# Run
print(f"  {'System':<16} │ {'235b':^12} │ {'243b':^12} │ {'243e Gear':^12} │ {'Δ vs 243b':>9}")
print(f"  {'─'*16}─┼─{'─'*12}─┼─{'─'*12}─┼─{'─'*12}─┼─{'─'*9}")

ref_243b = {"Solar (SSN)": 56.84, "ENSO (ONI)": 0.43, "Sanriku EQ": 0.60}

all_results = {}
for name, times, peaks, period, ara, rung in SYSTEMS:
    print(f"  Running {name}...", end="", flush=True)

    res_base = run_universal_vehicle(times, peaks, period=period, ara=ara,
                                      target_rung=rung, system_name=name)
    res_gear = run_gear_atom(times, peaks, period=period, ara=ara,
                              target_rung=rung, system_name=name)

    all_results[name] = {"base": res_base, "gear": res_gear}

    if res_base["failed"] or res_gear["failed"]:
        print(f"\r  {name:<16} │ {'FAIL':^12} │ {'FAIL':^12} │ {'FAIL':^12} │")
        continue

    b243b = ref_243b.get(name, 0)
    delta = res_gear["mae"] - b243b
    better = " ✓" if delta < 0 else ""
    print(f"\r  {name:<16} │ {res_base['mae']:>6.2f}      │ {b243b:>6.2f}      │ "
          f"{res_gear['mae']:>6.2f}      │ {delta:>+6.2f}{better}")


# Solar per-cycle
print(f"\n{'─' * 78}")
print("SOLAR PER-CYCLE — 243e Gear Atom")
print("─" * 78)

ra = all_results["Solar (SSN)"]["gear"]
rb = all_results["Solar (SSN)"]["base"]

if not ra["failed"] and not rb["failed"]:
    print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Base':>6} {'Err':>5} │ "
          f"{'Gear':>6} {'Err':>5} │ {'Win':>5}")
    print(f"  {'─'*3} {'─'*7} {'─'*6}─┼─{'─'*6} {'─'*5}─┼─{'─'*6} {'─'*5}─┼─{'─'*5}")

    bw, gw = 0, 0
    for i in range(len(solar_t)):
        be = rb["errors"][i]
        ge = ra["errors"][i]
        win = "Gear" if ge < be else "Base" if be < ge else "Tie"
        if ge < be: gw += 1
        elif be < ge: bw += 1
        print(f"  C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
              f"{rb['preds'][i]:>6.1f} {be:>5.1f} │ "
              f"{ra['preds'][i]:>6.1f} {ge:>5.1f} │ {win:>5}")

    print(f"\n  Base wins: {bw}  |  Gear wins: {gw}")


# Full comparison table
print(f"\n{'=' * 78}")
print("FULL COMPARISON — All 243 variants")
print("=" * 78)

ref_243c = {"Solar (SSN)": 53.12, "ENSO (ONI)": 0.46, "Sanriku EQ": 1.43}
ref_243d = {"Solar (SSN)": 56.14, "ENSO (ONI)": 0.48, "Sanriku EQ": 1.61}

print(f"\n  {'System':<16} {'235b':>8} {'243b':>8} {'243c':>8} {'243d':>8} {'243e':>8} {'Best':>8}")
print(f"  {'─'*16} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*8}")

for name in all_results:
    rb = all_results[name]["base"]
    rg = all_results[name]["gear"]
    if rb["failed"] or rg["failed"]:
        continue
    b = ref_243b.get(name, 999)
    c = ref_243c.get(name, 999)
    d = ref_243d.get(name, 999)
    vals = [rb['mae'], b, c, d, rg['mae']]
    labels = ['235b', '243b', '243c', '243d', '243e']
    best_i = vals.index(min(vals))
    print(f"  {name:<16} {vals[0]:>8.2f} {vals[1]:>8.2f} {vals[2]:>8.2f} "
          f"{vals[3]:>8.2f} {vals[4]:>8.2f} {labels[best_i]:>8}")

# Champion check
ra_solar = all_results["Solar (SSN)"]["gear"]
if not ra_solar["failed"]:
    print(f"\n  vs Champion (28.11): 243e = {ra_solar['mae']:.2f} "
          f"(Δ={ra_solar['mae']-28.11:+.2f})")
    if ra_solar['mae'] < 28.11:
        print(f"  ★ NEW CHAMPION ★")

# Key finding
print(f"\n  GEAR INSIGHT:")
print(f"    Downward engine cascade: FULL (no decay)")
print(f"    Upward consumer return:  DECAYED (1/φ per step)")
print(f"    Horizontal gear mesh:    FULL (coupling at each rung)")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
print("=" * 78)
