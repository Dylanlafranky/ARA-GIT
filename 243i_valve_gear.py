#!/usr/bin/env python3
"""
Script 243i — Valve-Modulated Gear

The simplest possible design:
  1. PIPES: Proven 235b wiring. No changes.
  2. GEAR: Pure counter-rotating whisper from 243g
     (engine cos, consumer -cos, clock sin)
  3. VALVE: The existing cascade_shape gate (acc = 1/(1+ARA))
     modulates HOW MUCH of each gear component gets through.

     High ARA (engine, Solar):
       acc = 1/(1+φ) = 0.382 → valve mostly closed
       → consumer return whisper dominates (completing the cycle)
       → engine cascade whisper is throttled (it IS the cascade)

     Low ARA (consumer, EQ):
       acc = 1/(1+0.15) = 0.870 → valve mostly open
       → engine cascade whisper dominates (feeding the consumer)
       → consumer return whisper is small (consumer has little to return)

The gate already knows ARA → asymmetry. We just pipe the
counter-rotating gear field through it.

From 243g: pure gear + asymmetric pipes → EQ 0.42 (best ever)
From 243f: decayed-down → Solar 43.48 (best atom Solar)
This should capture BOTH by letting the valve set the ratio dynamically.
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

SPACE_BASIS = np.array([9.0, 6.0, 2.0, -2.0])
TIME_BASIS  = np.array([5.0, 3.0, 1.0, -1.0])
RAT_BASIS   = np.array([6.0, 4.0, 1.0, -1.0])
BEST_STEER = 0.2
BEST_MOMENTUM = 0.3


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


class ValveGearNode(OrigARANode):
    """
    Triangle rider + VALVE-MODULATED counter-rotating gear.

    The gear has three components (from 243g):
      - Engine partners:  cos  (clockwise)
      - Consumer partners: -cos (counter-clockwise)
      - Clock partners:    sin  (gear teeth, 90°)

    The valve (acc = 1/(1+ARA)) modulates the MIX:
      - drive_weight = 1 - acc  (engine contribution, high when ARA high)
      - return_weight = acc     (consumer contribution, high when ARA low)

    So at high ARA (engine): consumer return dominates the whisper
       at low ARA (consumer): engine drive dominates the whisper
    Each system hears what it NEEDS — the other half of the gear.
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
        self.gear_drive = []    # engine partners (clockwise)
        self.gear_return = []   # consumer partners (counter-clockwise)
        self.gear_mesh = []     # clock partners (teeth)

    def set_gear_partners(self, drive, ret, mesh):
        self.gear_drive = drive
        self.gear_return = ret
        self.gear_mesh = mesh

    def cascade_shape(self, t):
        if self.t_ref is None: return 1.0

        # ── Instantaneous ARA ──
        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

        # ── Triangle rider ──
        target_s, target_t, target_r = find_triangle_position(inst_ara)
        force_s = (target_s - self.pos_s) * self.steer
        force_t = (target_t - self.pos_t) * self.steer
        force_r = (target_r - self.pos_r) * self.steer
        self.vel_s = self.vel_s * self.momentum + force_s
        self.vel_t = self.vel_t * self.momentum + force_t
        self.vel_r = self.vel_r * self.momentum + force_r
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

        # ── VALVE: acc = 1/(1+ARA) ──
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

        # ══════════════════════════════════════════════════════
        # VALVE-MODULATED GEAR WHISPER
        #
        # The valve (acc) sets how much of each gear half we hear:
        #   drive_weight  = 1 - acc  (engine half, louder at high ARA)
        #   return_weight = acc      (consumer half, louder at low ARA)
        #
        # But we INVERT which half the system listens to:
        #   High ARA → hears the RETURN (consumer completing the cycle)
        #   Low ARA  → hears the DRIVE (engine feeding it)
        #
        # So: high ARA system hears consumer return × (1-acc)
        #     low ARA system hears engine drive × acc
        #     Both hear mesh (teeth) at moderate level
        # ══════════════════════════════════════════════════════

        if self.gear_drive or self.gear_return or self.gear_mesh:
            drive_sum = 0.0
            return_sum = 0.0
            mesh_sum = 0.0

            for period_p, coupling in self.gear_drive:
                pp = TAU * (t - self.t_ref) / period_p
                drive_sum += coupling * math.cos(pp)

            for period_p, coupling in self.gear_return:
                pp = TAU * (t - self.t_ref) / period_p
                return_sum -= coupling * math.cos(pp)  # counter-rotating

            for period_p, coupling in self.gear_mesh:
                pp = TAU * (t - self.t_ref) / period_p
                mesh_sum += coupling * math.sin(pp)  # 90° teeth

            n_total = len(self.gear_drive) + len(self.gear_return) + len(self.gear_mesh)
            if n_total > 0:
                drive_sum /= n_total
                return_sum /= n_total
                mesh_sum /= n_total

            # Valve weights: acc modulates which half dominates
            # Engine system (high ARA, small acc) → hears return (consumer)
            # Consumer system (low ARA, large acc) → hears drive (engine)
            drive_weight = acc          # louder when ARA is low
            return_weight = 1.0 - acc   # louder when ARA is high
            mesh_weight = INV_PHI       # always moderate

            gear_signal = (drive_weight * drive_sum +
                          return_weight * return_sum +
                          mesh_weight * mesh_sum)

            shape *= (1.0 + INV_PHI_9 * gear_signal)

        return shape


# ════════════════════════════════════════════════════════════════
# BUILD VALVE GEAR VEHICLE
# ════════════════════════════════════════════════════════════════

def build_rung_ladder_valve(target_rung, target_period, seed_ara):
    mirror_floor = 0.15
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


def grid_search_valve(period, ara, rung, times, peaks, n_tr=80, n_ba=40):
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
            node = ValveGearNode("temp", period, ara, rung, ba, "engine")
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


def run_valve_gear(times, peaks, period, ara, target_rung,
                   system_name="System", sim_margin=None):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

    # Split gear partners into drive/return/mesh
    atom = derive_atom_nodes(ara, period)
    drive = []   # engine partners
    ret = []     # consumer partners
    mesh = []    # clock partners

    for roff, role, a, p in atom:
        if roff == 0 and role == 'engine': continue
        if role == 'engine':
            drive.append((p, INV_PHI_4))
        elif role == 'consumer':
            ret.append((p, INV_PHI_4))
        elif role == 'clock':
            mesh.append((p, INV_PHI_4))

    fit_tr, fit_ba, fit_mae = grid_search_valve(
        period, ara, target_rung, times, peaks)
    rungs = build_rung_ladder_valve(target_rung, period, ara)

    all_nodes = {}
    engine_nodes = {}

    for rung_power, rung_period, prefix, eng_ara, cons_ara, offset in rungs:
        for archetype, ara_val in [("engine", eng_ara), ("clock", 1.0),
                                    ("consumer", cons_ara)]:
            name = f"{prefix}_{archetype}"
            if prefix == "Target" and archetype == "engine":
                ara_val = ara; ba = fit_ba
            else: ba = 1.0
            node = ValveGearNode(name, rung_period, ara_val,
                                 rung_power, ba, archetype,
                                 seed_ara=ara, rung_offset=offset)
            node.set_t_ref(fit_tr)
            if prefix == "Target" and archetype == "engine":
                node.set_gear_partners(drive, ret, mesh)
            all_nodes[name] = node
            if archetype == "engine": engine_nodes[prefix] = node

    # PROVEN PIPES — unchanged from 235b
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

    # Valve diagnostics
    valve_acc = 1.0 / (1.0 + ara)

    return {
        "mae": mae, "fit_mae": fit_mae, "corr": corr,
        "snaps": target_node.local_ticks,
        "preds": np.array(preds), "errors": np.array(errors),
        "sine_mae": sine_mae,
        "improvement": (1 - mae / sine_mae) * 100 if sine_mae > 0 else 0,
        "failed": False, "name": system_name,
        "bounces": target_node.bounce_count,
        "valve_acc": valve_acc,
        "drive_weight": valve_acc,
        "return_weight": 1.0 - valve_acc,
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
print("Script 243i — Valve-Modulated Gear")
print("=" * 78)
print()
print("DESIGN:")
print("  Pipes:   PROVEN (235b, unchanged)")
print("  Gear:    PURE counter-rotating (243g)")
print("  Valve:   EXISTING acc = 1/(1+ARA) gates the gear mix")
print()
print("  High ARA (engine) → hears consumer return (completing cycle)")
print("  Low ARA (consumer) → hears engine drive (feeding it)")
print()

# Show valve settings
print("VALVE SETTINGS PER SYSTEM:")
print("─" * 78)
for name, _, _, _, ara, _ in SYSTEMS:
    acc = 1.0 / (1.0 + ara)
    print(f"  {name:<16} ARA={ara:.3f}  acc={acc:.3f}  "
          f"drive_wt={acc:.3f}  return_wt={1-acc:.3f}")
print()

# Best known results
ref = {
    '235b':   {"Solar (SSN)": 46.30, "ENSO (ONI)": 0.44, "Sanriku EQ": 1.19},
    '243b':   {"Solar (SSN)": 56.84, "ENSO (ONI)": 0.43, "Sanriku EQ": 0.60},
    '243f':   {"Solar (SSN)": 43.48, "ENSO (ONI)": 0.44, "Sanriku EQ": 1.48},
    '243g-A': {"Solar (SSN)": 57.08, "ENSO (ONI)": 0.45, "Sanriku EQ": 0.42},
    'BEST':   {"Solar (SSN)": 43.48, "ENSO (ONI)": 0.43, "Sanriku EQ": 0.42},
}

print(f"  {'System':<16} │ {'235b':>7} │ {'Best243':>7} │ {'243i':>7} │ {'ValveAcc':>8} │ {'vs Best':>8}")
print(f"  {'─'*16}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*8}─┼─{'─'*8}")

all_results = {}
for name, times, peaks, period, ara, rung in SYSTEMS:
    print(f"  Running {name}...", end="", flush=True)

    res = run_valve_gear(times, peaks, period=period, ara=ara,
                         target_rung=rung, system_name=name)
    all_results[name] = res

    if res["failed"]:
        print(f"\r  {name:<16} │  ---    │  ---    │  FAIL   │")
        continue

    best = ref['BEST'][name]
    delta = res['mae'] - best
    better = " ✓" if delta <= 0 else ""
    print(f"\r  {name:<16} │ {ref['235b'][name]:>7.2f} │ {best:>7.2f} │ "
          f"{res['mae']:>7.2f} │ {res['valve_acc']:>8.3f} │ {delta:>+7.2f}{better}")


# Solar per-cycle
print(f"\n{'─' * 78}")
print("SOLAR PER-CYCLE — 243i Valve Gear")
print("─" * 78)

ra = all_results["Solar (SSN)"]
if not ra["failed"]:
    print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Pred':>6} {'Err':>5} │")
    for i in range(len(solar_t)):
        print(f"  C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
              f"{ra['preds'][i]:>6.1f} {ra['errors'][i]:>5.1f} │")
    print(f"\n  Solar valve: acc={ra['valve_acc']:.3f} "
          f"(drive={ra['drive_weight']:.3f}, return={ra['return_weight']:.3f})")


# Full 243 series
print(f"\n{'=' * 78}")
print("COMPLETE 243 SERIES — BEST OF EACH")
print("=" * 78)

print(f"\n  {'System':<16} {'235b':>7} {'b':>7} {'f':>7} {'g-A':>7} {'i':>7} {'BEST':>7} {'From':>6}")
print(f"  {'─'*16} {'─'*7} {'─'*7} {'─'*7} {'─'*7} {'─'*7} {'─'*7} {'─'*6}")

for name, _, _, _, ara, _ in SYSTEMS:
    r = all_results[name]
    if r["failed"]: continue
    vals = {
        '235b': ref['235b'][name],
        'b': ref['243b'][name],
        'f': ref['243f'][name],
        'g-A': ref['243g-A'][name],
        'i': r['mae'],
    }
    best_key = min(vals, key=vals.get)
    best_val = vals[best_key]
    print(f"  {name:<16} {vals['235b']:>7.2f} {vals['b']:>7.2f} {vals['f']:>7.2f} "
          f"{vals['g-A']:>7.2f} {vals['i']:>7.2f} {best_val:>7.2f} {best_key:>6}")

# Champion
best_s = all_results["Solar (SSN)"]['mae'] if not all_results["Solar (SSN)"]["failed"] else 999
print(f"\n  vs Champion (28.11): 243i Solar = {best_s:.2f} (Δ={best_s-28.11:+.2f})")
if best_s < 28.11:
    print(f"  ★ NEW CHAMPION ★")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
print("=" * 78)
