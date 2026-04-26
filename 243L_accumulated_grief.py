#!/usr/bin/env python3
"""
Script 243L — Accumulated Grief: The Consumer IS the History

Dylan: "losing a fair bit of energy each cycle"

The current grief mechanism only looks ONE cycle back (prev_amp).
But a real consumer drains CUMULATIVELY. Multiple weak cycles in a row
should compound the drain — the Sun enters a Grand Minimum and the
consumer keeps pulling, cycle after cycle.

MECHANISM:
  - Track a "consumer debt" that accumulates when cycles are weak
  - debt += (base_amp - prev_amp) / base_amp  when prev_amp < base_amp
  - debt *= INV_PHI  when prev_amp >= base_amp (recovery, but slow)
  - The debt modulates cascade_shape as a deeper grief term
  - No new constants: uses existing φ relationships
  - Fully dynamic: emerges from the amplitude history

This replaces the single-cycle grief with accumulated grief.
Everything else from 243j temporal gear is preserved.

ALSO tests VARIANT B: Space loop — a bottom rung that feeds back
to the top at reduced efficiency (1/φ per cycle).
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


# ── Load 235b ──
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


class AccumulatedGriefNode(OrigARANode):
    """
    Triangle rider with ACCUMULATED GRIEF as the consumer mechanism.

    Instead of single-cycle grief (prev_amp only), this node tracks
    a running "consumer debt" that compounds during weak phases
    and slowly recovers during strong phases.
    """

    def __init__(self, name, period, ara, rung, base_amp, archetype,
                 seed_ara=None, rung_offset=0, use_temporal_gear=True):
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
        self.use_temporal_gear = use_temporal_gear

        # ACCUMULATED GRIEF — the consumer
        self.consumer_debt = 0.0  # Compounds during weak cycles

        # Temporal gear (from 243j)
        self.child_engine = None
        self.parent_engine = None
        self.child_last_snap_amp = None
        self.parent_last_snap_amp = None

    def update_gear_state(self):
        if self.child_engine is not None and self.child_engine.snap_amplitudes:
            self.child_last_snap_amp = self.child_engine.snap_amplitudes[-1]
        if self.parent_engine is not None and self.parent_engine.snap_amplitudes:
            self.parent_last_snap_amp = self.parent_engine.snap_amplitudes[-1]

    def update_consumer_debt(self):
        """
        Called when prev_amp is set (between cycles).
        Accumulates debt when cycles are weak, slowly recovers when strong.
        """
        if self.prev_amp is not None and self.base_amp > 0:
            dev = (self.prev_amp - self.base_amp) / self.base_amp
            if dev < 0:
                # Weak cycle: consumer takes more (debt grows)
                # The deeper the weakness, the more debt accumulates
                self.consumer_debt += abs(dev) * INV_PHI
            else:
                # Strong cycle: consumer gives back slowly
                # Recovery is 1/φ as fast as accumulation
                self.consumer_debt *= INV_PHI
                # But also partially offset by the surplus
                self.consumer_debt = max(0, self.consumer_debt - dev * INV_PHI_2)

    def cascade_shape(self, t):
        if self.t_ref is None: return 1.0

        if self.use_temporal_gear:
            self.update_gear_state()

        # ── Instantaneous ARA ──
        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

        # ── Temporal gear modulation (from 243k2 Variant A: child consumes) ──
        if self.use_temporal_gear:
            gear_tilt = 0.0
            if self.child_last_snap_amp is not None and self.child_engine is not None:
                child_dev = (self.child_last_snap_amp - self.child_engine.base_amp)
                if self.child_engine.base_amp > 0:
                    child_dev /= self.child_engine.base_amp
                gear_tilt -= INV_PHI_4 * child_dev  # Child CONSUMES (negative)

            if self.parent_last_snap_amp is not None and self.parent_engine is not None:
                parent_dev = (self.parent_last_snap_amp - self.parent_engine.base_amp)
                if self.parent_engine.base_amp > 0:
                    parent_dev /= self.parent_engine.base_amp
                gear_tilt -= INV_PHI_4 * parent_dev

            inst_ara = max(0.01, min(2.0, inst_ara + gear_tilt))

        # ── ACCUMULATED GRIEF: Consumer debt tilts ARA toward consumer ──
        # High debt = system is being drained = ARA moves toward consumer
        # This compounds over multiple weak cycles
        if self.consumer_debt > 0:
            # Debt pushes ARA downward (toward consumer territory)
            # Capped at INV_PHI to prevent runaway
            grief_drag = min(INV_PHI, self.consumer_debt)
            inst_ara = max(0.01, inst_ara - grief_drag)

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

        # ORIGINAL single-cycle grief (kept — accumulated grief is ON TOP)
        if self.prev_amp is not None:
            prev_dev = (self.prev_amp - self.base_amp) / self.base_amp
            grief_mult = PHI if prev_dev < 0 else 1.0
            shape += (-INV_PHI_3) * prev_dev * math.exp(-PHI) * grief_mult

        # ACCUMULATED GRIEF: consumer debt suppresses shape
        if self.consumer_debt > 0:
            # The consumer debt acts as an additional drag on the shape
            # Stronger than single-cycle grief because it compounds
            shape *= (1 - min(INV_PHI_2, self.consumer_debt * INV_PHI_3))

        if self.wall_energy > 0:
            shape *= (1 + self.wall_energy * INV_PHI_3)
            self.wall_energy *= INV_PHI

        return shape


# ════════════════════════════════════════════════════════════════
# BUILD AND RUN
# ════════════════════════════════════════════════════════════════

def build_rung_ladder(target_rung, target_period, seed_ara):
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


def grid_search(period, ara, rung, times, peaks, use_tg, n_tr=80, n_ba=40):
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
            node = AccumulatedGriefNode("temp", period, ara, rung, ba, "engine",
                                         use_temporal_gear=use_tg)
            node.set_t_ref(tr)
            errors = []
            for k in range(len(times)):
                if k > 0:
                    node.prev_amp = peaks[k-1]
                    node.amp_history = list(peaks[:k])
                    node.update_consumer_debt()
                else:
                    node.prev_amp = None
                pred = node.cascade_amplitude(times[k])
                errors.append(abs(pred - peaks[k]))
            mae = np.mean(errors)
            if mae < best_mae:
                best_mae, best_tr, best_ba = mae, tr, ba
    return best_tr, best_ba, best_mae


def run_grief_vehicle(times, peaks, period, ara, target_rung,
                      system_name="System", use_temporal_gear=True,
                      sim_margin=None):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

    fit_tr, fit_ba, fit_mae = grid_search(
        period, ara, target_rung, times, peaks, use_temporal_gear)
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
            node = AccumulatedGriefNode(name, rung_period, ara_val,
                                         rung_power, ba, archetype,
                                         seed_ara=ara, rung_offset=offset,
                                         use_temporal_gear=use_temporal_gear)
            node.set_t_ref(fit_tr)
            all_nodes[name] = node
            if archetype == "engine": engine_nodes[prefix] = node

    # Proven pipes
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

    # Temporal gear wiring
    if use_temporal_gear:
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
            # After a snap, update consumer debt for the target
            if events and node == engine_nodes.get("Target"):
                node.update_consumer_debt()
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
        return {"mae": 999, "failed": True, "name": system_name}
    errors, preds = [], []
    for i in range(len(times)):
        idx = np.argmin(np.abs(snap_t - times[i]))
        preds.append(snap_a[idx])
        errors.append(abs(snap_a[idx] - peaks[i]))
    mae = np.mean(errors)
    rung_snap_counts = {}
    for prefix in engine_nodes:
        rung_snap_counts[prefix] = engine_nodes[prefix].local_ticks

    return {
        "mae": mae, "fit_mae": fit_mae,
        "preds": np.array(preds), "errors": np.array(errors),
        "failed": False, "name": system_name,
        "rung_snaps": rung_snap_counts,
        "debt_final": target_node.consumer_debt,
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
solar_p = np.array([c[2] for c in SOLAR_CYCLES])
enso_t = np.array([e[0] for e in ENSO_EVENTS])
enso_p = np.array([e[1] for e in ENSO_EVENTS])
eq_t = np.array([e[0] for e in SANRIKU_EVENTS])
eq_p = np.array([e[1] for e in SANRIKU_EVENTS])


# ════════════════════════════════════════════════════════════════
# RUN VARIANTS
# ════════════════════════════════════════════════════════════════

print("=" * 78)
print("Script 243L — Accumulated Grief: The Consumer IS the History")
print("=" * 78)
print()

# Baselines
base_solar = run_universal_vehicle(solar_t, solar_p, 11.0, PHI, 4, "Solar")
base_enso  = run_universal_vehicle(enso_t, enso_p, 3.7, INV_PHI_2, 2, "ENSO")
base_eq    = run_universal_vehicle(eq_t, eq_p, 25.0, 0.5, 3, "EQ")

best_243 = {"Solar": 43.48, "ENSO": 0.43, "EQ": 0.42}

variants = [
    ("A: grief only",      False),  # Accumulated grief, no temporal gear
    ("B: grief + gear",    True),   # Both accumulated grief AND temporal gear
]

print(f"  {'Variant':<22} │ {'Solar':>7} │ {'ENSO':>6} │ {'EQ':>6} │ {'Debt_S':>6} │ Notes")
print(f"  {'─'*22}┼{'─'*9}┼{'─'*8}┼{'─'*8}┼{'─'*8}┼{'─'*30}")
print(f"  {'235b baseline':<22} │ {base_solar['mae']:>7.2f} │ {base_enso['mae']:>6.2f} │ {base_eq['mae']:>6.2f} │ {'n/a':>6} │ proven champion cascade")
print(f"  {'Best 243 series':<22} │ {best_243['Solar']:>7.2f} │ {best_243['ENSO']:>6.2f} │ {best_243['EQ']:>6.2f} │ {'n/a':>6} │ best from each variant")
print(f"  {'─'*22}┼{'─'*9}┼{'─'*8}┼{'─'*8}┼{'─'*8}┼{'─'*30}")

for vname, use_tg in variants:
    print(f"  Running {vname}...", end="", flush=True)

    r_sol = run_grief_vehicle(solar_t, solar_p, 11.0, PHI, 4,
                              "Solar", use_temporal_gear=use_tg)
    r_enso = run_grief_vehicle(enso_t, enso_p, 3.7, INV_PHI_2, 2,
                               "ENSO", use_temporal_gear=use_tg)
    r_eq = run_grief_vehicle(eq_t, eq_p, 25.0, 0.5, 3,
                             "EQ", use_temporal_gear=use_tg)

    sol_mark = " ✓" if r_sol["mae"] < base_solar["mae"] else ""
    enso_mark = " ✓" if r_enso["mae"] < base_enso["mae"] else ""
    eq_mark = " ✓" if r_eq["mae"] < base_eq["mae"] else ""

    notes = []
    if r_sol["mae"] < best_243["Solar"]: notes.append("Solar BEST!")
    if r_enso["mae"] < best_243["ENSO"]: notes.append("ENSO BEST!")
    if r_eq["mae"] < best_243["EQ"]: notes.append("EQ BEST!")
    if r_sol["mae"] < base_solar["mae"]: notes.append("Solar↓")
    if r_enso["mae"] < base_enso["mae"]: notes.append("ENSO↓")
    if r_eq["mae"] < base_eq["mae"]: notes.append("EQ↓")

    debt_s = r_sol.get("debt_final", 0)

    print(f"\r  {vname:<22} │ {r_sol['mae']:>7.2f}{sol_mark:2s} │ {r_enso['mae']:>6.2f}{enso_mark:2s} │ {r_eq['mae']:>6.2f}{eq_mark:2s} │ {debt_s:>6.3f} │ {', '.join(notes)}")

    # Per-cycle for solar
    if "grief" in vname.lower() and not use_tg:
        print()
        print(f"  Solar per-cycle ({vname}):")
        for i, (cn, yr, act) in enumerate(SOLAR_CYCLES):
            pred = r_sol["preds"][i]
            err = r_sol["errors"][i]
            better = "✓" if err < abs(act - np.mean(solar_p)) else ""
            print(f"    C{cn:>2} {yr:>6.1f}: act={act:>5.1f} pred={pred:>6.1f} err={err:>5.1f} {better}")
        print()


# ════════════════════════════════════════════════════════════════
# VARIANT C: SPACE LOOP — bottom rung feeds back to top at 1/φ
# ════════════════════════════════════════════════════════════════

print()
print("─" * 78)
print("VARIANT C: Space Loop — bottom feeds back to top at 1/φ efficiency")
print("─" * 78)
print()
print("  SubSub's output feeds back into Gleissberg on next cycle")
print("  Efficiency = 1/φ (not full strength — energy lost to space)")
print()


class SpaceLoopNode(AccumulatedGriefNode):
    """Same as accumulated grief, plus a space-loop reference."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.space_loop_engine = None  # Reference to bottom rung
        self.space_loop_amp = None

    def update_gear_state(self):
        super().update_gear_state()
        if self.space_loop_engine is not None and self.space_loop_engine.snap_amplitudes:
            self.space_loop_amp = self.space_loop_engine.snap_amplitudes[-1]

    def cascade_shape(self, t):
        if self.t_ref is None: return 1.0

        # Get base shape from parent class
        shape = super().cascade_shape(t)

        # SPACE LOOP: if this is the TOP rung and we have a bottom reference,
        # the bottom's last snap feeds back into the top at 1/φ
        if self.space_loop_amp is not None and self.space_loop_engine is not None:
            if self.space_loop_engine.base_amp > 0:
                loop_dev = (self.space_loop_amp - self.space_loop_engine.base_amp)
                loop_dev /= self.space_loop_engine.base_amp
                # Feed back at 1/φ efficiency (energy lost to space)
                shape *= (1 + INV_PHI * INV_PHI_4 * loop_dev)

        return shape


def run_space_loop(times, peaks, period, ara, target_rung,
                   system_name="System", sim_margin=None):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

    # Grid search with base node (space loop barely affects grid search)
    fit_tr, fit_ba, fit_mae = grid_search(
        period, ara, target_rung, times, peaks, True)
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
            node = SpaceLoopNode(name, rung_period, ara_val,
                                  rung_power, ba, archetype,
                                  seed_ara=ara, rung_offset=offset,
                                  use_temporal_gear=True)
            node.set_t_ref(fit_tr)
            all_nodes[name] = node
            if archetype == "engine": engine_nodes[prefix] = node

    # Proven pipes
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

    # Temporal gear wiring
    for i, (rp, prefix, offset) in enumerate(rung_list):
        engine = engine_nodes[prefix]
        if i < len(rung_list) - 1:
            child_prefix = rung_list[i + 1][1]
            engine.child_engine = engine_nodes[child_prefix]
        if i > 0:
            parent_prefix = rung_list[i - 1][1]
            engine.parent_engine = engine_nodes[parent_prefix]

    # SPACE LOOP: top rung's engine gets reference to bottom rung's engine
    top_prefix = rung_list[0][1]     # Gleissberg (highest rung)
    bottom_prefix = rung_list[-1][1]  # SubSub (lowest rung)
    engine_nodes[top_prefix].space_loop_engine = engine_nodes[bottom_prefix]

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
            if events and node == engine_nodes.get("Target"):
                node.update_consumer_debt()
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
        return {"mae": 999, "failed": True, "name": system_name}
    errors, preds = [], []
    for i in range(len(times)):
        idx = np.argmin(np.abs(snap_t - times[i]))
        preds.append(snap_a[idx])
        errors.append(abs(snap_a[idx] - peaks[i]))
    mae = np.mean(errors)

    return {
        "mae": mae, "fit_mae": fit_mae,
        "preds": np.array(preds), "errors": np.array(errors),
        "failed": False, "name": system_name,
        "debt_final": target_node.consumer_debt,
    }


# Run space loop
print(f"  {'Variant':<22} │ {'Solar':>7} │ {'ENSO':>6} │ {'EQ':>6} │ Notes")
print(f"  {'─'*22}┼{'─'*9}┼{'─'*8}┼{'─'*8}┼{'─'*30}")

print(f"  Running C: space loop...", end="", flush=True)
r_sol = run_space_loop(solar_t, solar_p, 11.0, PHI, 4, "Solar")
r_enso = run_space_loop(enso_t, enso_p, 3.7, INV_PHI_2, 2, "ENSO")
r_eq = run_space_loop(eq_t, eq_p, 25.0, 0.5, 3, "EQ")

sol_mark = " ✓" if r_sol["mae"] < base_solar["mae"] else ""
enso_mark = " ✓" if r_enso["mae"] < base_enso["mae"] else ""
eq_mark = " ✓" if r_eq["mae"] < base_eq["mae"] else ""

notes = []
if r_sol["mae"] < best_243["Solar"]: notes.append("Solar BEST!")
if r_sol["mae"] < base_solar["mae"]: notes.append("Solar↓")
if r_enso["mae"] < base_enso["mae"]: notes.append("ENSO↓")
if r_eq["mae"] < base_eq["mae"]: notes.append("EQ↓")

print(f"\r  {'C: space loop':<22} │ {r_sol['mae']:>7.2f}{sol_mark:2s} │ {r_enso['mae']:>6.2f}{enso_mark:2s} │ {r_eq['mae']:>6.2f}{eq_mark:2s} │ {', '.join(notes)}")

# Per-cycle
print()
print(f"  Solar per-cycle (C: space loop):")
for i, (cn, yr, act) in enumerate(SOLAR_CYCLES):
    pred = r_sol["preds"][i]
    err = r_sol["errors"][i]
    print(f"    C{cn:>2} {yr:>6.1f}: act={act:>5.1f} pred={pred:>6.1f} err={err:>5.1f}")


print()
print("=" * 78)
print(f"  Runtime: {clock_time.time() - t_start:.0f}s")
print("=" * 78)
