#!/usr/bin/env python3
"""
Script 243c — Selective Atom with Step-Decayed Coupling

Key changes from 243b:
  1. SELECTIVE: Only consumer-side rung nodes get geometric ARAs.
     Engine nodes keep their PROVEN values (φ, 1.0, 1/φ pattern).
     Solar's cascade timing stays intact.

  2. STEP DECAY: Connection field whisper decays by 1/φ per hop.
     - Direct horizontal partner (1 hop):  weight × (1/φ)¹
     - Direct vertical partner (1 hop):    weight × (1/φ)¹
     - Cross-rung mirror (2 hops):         weight × (1/φ)²
     - Cross-rung consumer (2 hops):       weight × (1/φ)²
     - Distant partners (3+ hops):         weight × (1/φ)³

  3. DIRECTIONAL COUPLING: Respects pipe asymmetry.
     - Down:       2φ capacity → stronger coupling
     - Up:         φ capacity  → weaker coupling
     - Horizontal: φ² coupling → moderate

  4. REVERSE TEST: Track whether exothermic nodes feed consumers
     properly — consumers should benefit from populated fields.

Champion to beat: Solar MAE = 28.11 (triangle rider 236j)
243b results: Solar 56.84 (worse), ENSO 0.43, EQ 0.60 (-49.9%)
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
MOMENTUM_FRAC = INV_PHI_3

# Triangle rider basis from 236j
SPACE_BASIS = np.array([9.0, 6.0, 2.0, -2.0])
TIME_BASIS  = np.array([5.0, 3.0, 1.0, -1.0])
RAT_BASIS   = np.array([6.0, 4.0, 1.0, -1.0])
BEST_STEER = 0.2
BEST_MOMENTUM = 0.3


# ════════════════════════════════════════════════════════════════
# CONNECTION FIELD — derive partner ARA values from geometry
# ════════════════════════════════════════════════════════════════

def derive_atom_nodes(seed_ara, seed_period):
    """
    Derive the full φ⁹ atom: 9 nodes across 3 rungs.
    Returns list of (rung_offset, role, ara, period, hops, direction).

    hops = number of geometric steps from seed engine:
      - seed engine's horizontal mirror: 1 hop
      - seed clock: 1 hop
      - child engine: 1 hop (vertical)
      - child mirror: 2 hops (vertical + horizontal)
      - parent engine: 1 hop (vertical)
      - parent mirror: 2 hops (vertical + horizontal)
      - child/parent clock: 2 hops (vertical + role-change)
    """
    mirror_floor = 0.15  # singularity boundary floor

    nodes = []
    for rung_offset in [-1, 0, 1]:
        if rung_offset == 0:
            p = seed_period
            engine_ara = seed_ara
            mirror_ara = max(mirror_floor, 2.0 - seed_ara)
        elif rung_offset == 1:
            # Child rung (one down = longer period)
            p = seed_period * PHI
            engine_ara = seed_ara / PHI
            mirror_ara = max(mirror_floor, 2.0 - engine_ara)
        elif rung_offset == -1:
            # Parent rung (one up = shorter period)
            p = seed_period / PHI
            engine_ara = min(2.0, seed_ara * PHI)
            mirror_ara = max(mirror_floor, 2.0 - engine_ara)

        # Hops from seed engine
        if rung_offset == 0:
            engine_hops = 0
            clock_hops = 1
            mirror_hops = 1
        else:
            engine_hops = 1  # one vertical step
            clock_hops = 2   # vertical + role-change
            mirror_hops = 2  # vertical + horizontal

        # Direction for pipe asymmetry
        if rung_offset == 0:
            direction = 'horizontal'
        elif rung_offset > 0:
            direction = 'vertical_down'
        else:
            direction = 'vertical_up'

        nodes.append((rung_offset, 'engine',   engine_ara, p, engine_hops, direction))
        nodes.append((rung_offset, 'clock',    1.0,        p, clock_hops,  direction))
        nodes.append((rung_offset, 'consumer', mirror_ara, p, mirror_hops, direction))

    return nodes


def build_field_partners(seed_ara, seed_period):
    """
    Build connection field partners with step-decayed coupling.

    Each partner gets:
      - base coupling from direction (φ² horiz, 2/φ vert_down, φ vert_up)
      - decay factor (1/φ)^hops
      - phase relationship (anti-phase for mirrors, in-phase for engines)
    """
    atom = derive_atom_nodes(seed_ara, seed_period)
    partners = []

    for roff, role, ara, period, hops, direction in atom:
        # Skip the seed itself
        if roff == 0 and role == 'engine':
            continue

        # Base coupling strength from direction
        if direction == 'horizontal':
            base_coupling = PHI_2       # φ² horizontal
        elif direction == 'vertical_down':
            base_coupling = TWO_OVER_PHI  # 2/φ vertical down
        elif direction == 'vertical_up':
            base_coupling = PHI           # φ vertical up
        else:
            base_coupling = 1.0

        # Step decay: (1/φ)^hops
        decay = INV_PHI ** hops

        # Effective coupling
        effective = base_coupling * decay

        # Phase relationship
        if role == 'consumer':
            phase_type = 'anti'      # mirrors are anti-phase
        elif role == 'clock':
            phase_type = 'quadrature'  # clocks are π/2 offset
        else:
            phase_type = 'in_phase'   # engines are in-phase

        partners.append({
            'period': period,
            'coupling': effective,
            'hops': hops,
            'direction': direction,
            'phase_type': phase_type,
            'role': role,
            'rung_offset': roff,
            'ara': ara,
        })

    return partners


# ════════════════════════════════════════════════════════════════
# EXEC 235b for the vehicle infrastructure
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
# TRIANGLE RIDER FUNCTIONS (from 236j)
# ════════════════════════════════════════════════════════════════

def find_triangle_position(target_ara, space_bias=0.3):
    if target_ara <= 0:
        return (1.0, 0.0, 0.0)
    if target_ara >= 2.0:
        return (0.0, 1.0, 0.0)
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
        wall_energy = max(wall_energy, abs(s))
        wall_hit = 's'
        s = 0.0
    if t < 0:
        wall_energy = max(wall_energy, abs(t))
        wall_hit = 't'
        t = 0.0
    if r < 0:
        wall_energy = max(wall_energy, abs(r))
        wall_hit = 'r'
        r = 0.0
    total = s + t + r
    if total > 0:
        s, t, r = s / total, t / total, r / total
    else:
        s, t, r = 1/3, 1/3, 1/3
    return s, t, r, wall_hit, wall_energy


# ════════════════════════════════════════════════════════════════
# SELECTIVE ATOM NODE — Step-Decayed Connection Field
# ════════════════════════════════════════════════════════════════

class SelectiveAtomNode(OrigARANode):
    """
    Triangle rider node with STEP-DECAYED connection field whisper.

    Key differences from 243b AtomRiderNode:
      - Field partners have per-hop decay (1/φ per step)
      - Directional coupling (φ² horiz, 2/φ down, φ up)
      - Phase relationships: anti-phase mirrors, quadrature clocks
      - Total whisper budget still 1/φ⁹ but distributed by decay
    """

    def __init__(self, name, period, ara, rung, base_amp, archetype,
                 seed_ara=None):
        super().__init__(name, period, ara, rung, base_amp, archetype)

        # Triangle rider state
        s, t, r = find_triangle_position(ara)
        self.pos_s, self.pos_t, self.pos_r = s, t, r
        self.vel_s, self.vel_t, self.vel_r = 0.0, 0.0, 0.0
        self.wall_energy = 0.0
        self.bounce_count = 0
        self.steer = BEST_STEER
        self.momentum = BEST_MOMENTUM
        self.elasticity = INV_PHI

        # Connection field
        self.seed_ara = seed_ara or ara
        self.field_partners = []  # list of partner dicts from build_field_partners

    def set_field_partners(self, partners):
        """Set step-decayed connection field partners."""
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
            if wall == 's':
                self.vel_s = abs(self.vel_s) * self.elasticity
            elif wall == 't':
                self.vel_t = abs(self.vel_t) * self.elasticity
            elif wall == 'r':
                self.vel_r = abs(self.vel_r) * self.elasticity

        self.pos_s, self.pos_t, self.pos_r = new_s, new_t, new_r

        # ── Cascade distances from rider position ──
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

        # ══ STEP-DECAYED CONNECTION FIELD WHISPER ══
        # Each partner's contribution is:
        #   coupling × (1/φ)^hops × phase_term
        # Total budget remains 1/φ⁹ but NOW weighted by geometry
        if self.field_partners:
            field_sum = 0.0
            total_weight = 0.0

            for partner in self.field_partners:
                p_period = partner['period']
                p_coupling = partner['coupling']  # already includes decay
                p_phase_type = partner['phase_type']

                partner_phase = TAU * (t - self.t_ref) / p_period

                if p_phase_type == 'anti':
                    # Mirror: anti-phase contribution
                    phase_term = -math.cos(partner_phase)
                elif p_phase_type == 'quadrature':
                    # Clock: π/2 offset — sin contribution
                    phase_term = math.sin(partner_phase)
                else:
                    # Engine: in-phase
                    phase_term = math.cos(partner_phase)

                field_sum += p_coupling * phase_term
                total_weight += p_coupling

            # Normalise by total coupling weight, scale by 1/φ⁹
            if total_weight > 0:
                field_sum /= total_weight
            shape *= (1.0 + INV_PHI_9 * field_sum)

        return shape


# ════════════════════════════════════════════════════════════════
# BUILD SELECTIVE ATOM VEHICLE
# ════════════════════════════════════════════════════════════════

def build_rung_ladder_selective(target_rung, target_period, seed_ara):
    """
    Build a φ-ladder where:
      - Engine nodes keep PROVEN generic ARAs (φ, 1.0, 1/φ)
      - Consumer nodes get GEOMETRIC ARAs from connection field
      - Clock nodes stay at 1.0

    This preserves Solar's cascade timing while giving consumers
    the populated connection field they need.
    """
    mirror_floor = 0.15
    rungs = []

    for offset in range(-2, 5):
        r = target_rung + offset
        if r < 0:
            continue
        p = target_period * PHI**offset

        if offset == 4:
            prefix = "Gleissberg"
        elif offset == 1:
            prefix = "AboveT"
        elif offset == 0:
            prefix = "Target"
        elif offset == -1:
            prefix = "BelowT"
        elif offset == -2:
            prefix = "SubSub"
        elif offset == 2:
            prefix = "AboveA"
        elif offset == 3:
            prefix = "AboveB"
        else:
            prefix = f"R{r}"

        # Engine: KEEP PROVEN VALUES
        engine_ara = PHI  # default engine

        # Consumer: GEOMETRIC from connection field
        if offset == 0:
            consumer_ara = max(mirror_floor, 2.0 - seed_ara)
        elif offset == 1:
            child_eng = seed_ara / PHI
            consumer_ara = max(mirror_floor, 2.0 - child_eng)
        elif offset == -1:
            parent_eng = min(2.0, seed_ara * PHI)
            consumer_ara = max(mirror_floor, 2.0 - parent_eng)
        else:
            # Distant rungs: extrapolate
            if offset > 0:
                distant_eng = seed_ara / (PHI ** offset)
                consumer_ara = max(mirror_floor, 2.0 - distant_eng)
            else:
                distant_eng = min(2.0, seed_ara * PHI ** abs(offset))
                consumer_ara = max(mirror_floor, 2.0 - distant_eng)

        rungs.append((r, p, prefix, engine_ara, consumer_ara))

    return sorted(rungs, key=lambda x: -x[0])


def grid_search_selective(period, ara, rung, times, peaks, n_tr=80, n_ba=40):
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
            node = SelectiveAtomNode("temp", period, ara, rung, ba, "engine")
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


def run_selective_atom(times, peaks, period, ara, target_rung,
                       system_name="System", sim_margin=None):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

    # Build step-decayed field partners
    field_partners = build_field_partners(ara, period)

    fit_tr, fit_ba, fit_mae = grid_search_selective(
        period, ara, target_rung, times, peaks)

    # Build rung ladder: engines=proven, consumers=geometric
    rungs = build_rung_ladder_selective(target_rung, period, ara)

    all_nodes = {}
    engine_nodes = {}
    for rung_power, rung_period, prefix, eng_ara, cons_ara in rungs:
        for archetype, ara_val in [("engine", eng_ara), ("clock", 1.0),
                                    ("consumer", cons_ara)]:
            name = f"{prefix}_{archetype}"
            if prefix == "Target" and archetype == "engine":
                ara_val = ara
                ba = fit_ba
            else:
                ba = 1.0

            node = SelectiveAtomNode(name, rung_period, ara_val,
                                      rung_power, ba, archetype,
                                      seed_ara=ara)
            node.set_t_ref(fit_tr)

            # Give the target engine its step-decayed field partners
            if prefix == "Target" and archetype == "engine":
                node.set_field_partners(field_partners)

            all_nodes[name] = node
            if archetype == "engine":
                engine_nodes[prefix] = node

    # Wire connections (same proven wiring)
    rung_list = [(rp, prefix) for rp, _, prefix, _, _ in rungs]
    for i, (rp, prefix) in enumerate(rung_list):
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

    # Field partner diagnostics
    field_diag = []
    for p in field_partners:
        field_diag.append({
            'role': p['role'],
            'rung': p['rung_offset'],
            'hops': p['hops'],
            'coupling': p['coupling'],
            'phase': p['phase_type'],
            'period': p['period'],
        })

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
        "field_partners": field_diag,
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
print("Script 243c — Selective Atom with Step-Decayed Coupling")
print("=" * 78)
print()
print("SELECTIVE: Engine nodes keep proven ARAs, consumers get geometric ARAs")
print("STEP DECAY: Coupling decays (1/φ)^hops — closer partners whisper louder")
print("DIRECTIONAL: φ² horizontal, 2/φ down, φ up — respects pipe asymmetry")
print()

# Show field partner structure for each system
print("CONNECTION FIELD STRUCTURE:")
print("─" * 78)
for name, times, peaks, period, ara, rung in SYSTEMS:
    partners = build_field_partners(ara, period)
    print(f"\n  {name} (seed ARA={ara:.3f}, period={period:.2f}):")
    print(f"    {'Role':<12} {'Rung':>5} {'Hops':>5} {'Coupling':>10} {'Decayed':>10} {'Phase':>12}")
    for p in partners:
        print(f"    {p['role']:<12} {p['rung_offset']:>+5d} {p['hops']:>5d} "
              f"{p['coupling']:>10.4f} {p['coupling']:>10.4f} {p['phase_type']:>12}")

print()

# Run all systems
print(f"\n  {'System':<16} │ {'235b Base':^22} │ {'Sel. Atom':^22} │ {'Δ':>7}")
print(f"  {'─'*16}─┼─{'─'*22}─┼─{'─'*22}─┼─{'─'*7}")

all_results = {}
for name, times, peaks, period, ara, rung in SYSTEMS:
    print(f"  Running {name}...", end="", flush=True)

    # Run 235b vehicle as baseline
    res_base = run_universal_vehicle(times, peaks, period=period, ara=ara,
                                      target_rung=rung, system_name=name)

    # Run selective atom
    res_atom = run_selective_atom(times, peaks, period=period, ara=ara,
                                  target_rung=rung, system_name=name)

    all_results[name] = {"base": res_base, "atom": res_atom}

    if res_base["failed"] or res_atom["failed"]:
        print(f"\r  {name:<16} │ {'FAIL':^22} │ {'FAIL':^22} │")
        continue

    delta = res_atom["mae"] - res_base["mae"]
    better = " ✓" if delta < 0 else ""
    print(f"\r  {name:<16} │ MAE={res_base['mae']:>6.2f} r={res_base['corr']:>+.3f}  │ "
          f"MAE={res_atom['mae']:>6.2f} r={res_atom['corr']:>+.3f}  │ {delta:>+6.2f}{better}")


# Solar per-cycle detail
print(f"\n{'─' * 78}")
print("SOLAR PER-CYCLE — Base vs Selective Atom")
print("─" * 78)

rr = all_results["Solar (SSN)"]["base"]
ra = all_results["Solar (SSN)"]["atom"]

if not rr["failed"] and not ra["failed"]:
    print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Base':>6} {'Err':>5} │ "
          f"{'Atom':>6} {'Err':>5} │ {'Win':>5}")
    print(f"  {'─'*3} {'─'*7} {'─'*6}─┼─{'─'*6} {'─'*5}─┼─{'─'*6} {'─'*5}─┼─{'─'*5}")

    bw, aw = 0, 0
    for i in range(len(solar_t)):
        re_b = rr["errors"][i]
        ae = ra["errors"][i]
        win = "Atom" if ae < re_b else "Base" if re_b < ae else "Tie"
        if ae < re_b: aw += 1
        elif re_b < ae: bw += 1
        print(f"  C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
              f"{rr['preds'][i]:>6.1f} {re_b:>5.1f} │ "
              f"{ra['preds'][i]:>6.1f} {ae:>5.1f} │ {win:>5}")

    print(f"\n  Base wins: {bw}  |  Atom wins: {aw}")


# Step decay analysis
print(f"\n{'─' * 78}")
print("STEP DECAY ANALYSIS — Coupling weights by hop distance")
print("─" * 78)

for name in all_results:
    ra = all_results[name]["atom"]
    if ra["failed"] or "field_partners" not in ra:
        continue
    print(f"\n  {name}:")
    by_hops = {}
    for p in ra["field_partners"]:
        h = p['hops']
        if h not in by_hops:
            by_hops[h] = []
        by_hops[h].append(p)
    for h in sorted(by_hops.keys()):
        partners = by_hops[h]
        total_c = sum(p['coupling'] for p in partners)
        roles = ", ".join(f"{p['role']}(r{p['rung']:+d})" for p in partners)
        print(f"    {h} hop{'s' if h!=1 else ''}: {len(partners)} partners, "
              f"total coupling={total_c:.4f} — {roles}")


# Summary
print(f"\n{'=' * 78}")
print("SUMMARY — 243c Selective Atom with Step Decay")
print("=" * 78)

for name in all_results:
    rb = all_results[name]["base"]
    ra = all_results[name]["atom"]
    if rb["failed"] or ra["failed"]:
        continue
    delta_mae = ra["mae"] - rb["mae"]
    pct = delta_mae / rb["mae"] * 100 if rb["mae"] > 0 else 0
    print(f"  {name:<16}: {rb['mae']:.2f} → {ra['mae']:.2f} "
          f"(Δ={delta_mae:+.2f}, {pct:+.1f}%), "
          f"corr {rb['corr']:+.3f} → {ra['corr']:+.3f}")

# vs champion
ra_solar = all_results["Solar (SSN)"]["atom"]
if not ra_solar["failed"]:
    print(f"\n  vs Champion (28.11): Selective Atom = {ra_solar['mae']:.2f} "
          f"(Δ={ra_solar['mae']-28.11:+.2f})")
    if ra_solar['mae'] < 28.11:
        print(f"  ★ NEW CHAMPION ★")

# Key insight
print(f"\n  Key design: Engines UNTOUCHED (proven cascade timing preserved)")
print(f"  Consumers get geometric ARAs from connection field")
print(f"  Whisper decays (1/φ)^hops — near partners dominate")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
print("=" * 78)
