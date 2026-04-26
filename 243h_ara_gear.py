#!/usr/bin/env python3
"""
Script 243h — ARA-Driven Gear Ratio

Dylan: "Can we just do the triangle method or the same method we did
for the valve?"

Instead of hardcoding pipe asymmetry, let ARA SET the gear ratio:

  up_strength = PHI_LEAK × (1/φ + (ARA/2) × (1 - 1/φ))

  ARA = 0.00 (consumer): up = PHI_LEAK × 1/φ     = 0.0902 (original asymmetric)
  ARA = 1.00 (clock):    up = PHI_LEAK × 0.8090   = 0.1180
  ARA = φ    (engine):   up = PHI_LEAK × 0.8562   = 0.1249 (nearly symmetric)
  ARA = 2.00 (harmonic): up = PHI_LEAK × 1.0      = 0.1459 (fully symmetric)

The system finds its own gear ratio from its ARA identity.
No manual tuning. Same principle as the triangle rider and the valve.

From 243g: pure gear + asymmetric pipes gave EQ 0.42 (-64.7%)
From 243f: decayed-down gave Solar 43.48 (best atom Solar)
This should combine both wins by giving each system its natural ratio.
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


def ara_gear_ratio(ara):
    """
    Compute the upward pipe strength from ARA.
    Slides from 1/φ (consumer, ARA=0) to 1.0 (harmonic, ARA=2).
    """
    t = min(1.0, max(0.0, ara / 2.0))  # normalise to [0,1]
    return INV_PHI + t * (1.0 - INV_PHI)


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


class ARAGearNode(OrigARANode):
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
        if self.t_ref is None: return 1.0

        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

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

        # ══ PURE GEAR WHISPER ══
        if self.field_partners:
            field_sum = 0.0
            for partner_period, coupling, gear_dir in self.field_partners:
                partner_phase = TAU * (t - self.t_ref) / partner_period
                if gear_dir == 'clockwise':
                    field_sum += coupling * math.cos(partner_phase)
                elif gear_dir == 'counter':
                    field_sum -= coupling * math.cos(partner_phase)
                elif gear_dir == 'teeth':
                    field_sum += coupling * math.sin(partner_phase)
            field_sum /= max(1, len(self.field_partners))
            shape *= (1.0 + INV_PHI_9 * field_sum)

        return shape


def build_rung_ladder_ara_gear(target_rung, target_period, seed_ara):
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


def grid_search_ara_gear(period, ara, rung, times, peaks, n_tr=80, n_ba=40):
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
            node = ARAGearNode("temp", period, ara, rung, ba, "engine")
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


def run_ara_gear(times, peaks, period, ara, target_rung,
                 system_name="System", sim_margin=None):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

    # Gear ratio from ARA
    gear_ratio = ara_gear_ratio(ara)

    # Pure gear partners
    atom = derive_atom_nodes(ara, period)
    gear_partners = []
    for roff, role, a, p in atom:
        if roff == 0 and role == 'engine': continue
        if role == 'engine':
            gear_partners.append((p, INV_PHI_4, 'clockwise'))
        elif role == 'consumer':
            gear_partners.append((p, INV_PHI_4, 'counter'))
        elif role == 'clock':
            gear_partners.append((p, INV_PHI_4, 'teeth'))

    fit_tr, fit_ba, fit_mae = grid_search_ara_gear(
        period, ara, target_rung, times, peaks)
    rungs = build_rung_ladder_ara_gear(target_rung, period, ara)

    all_nodes = {}
    engine_nodes = {}

    for rung_power, rung_period, prefix, eng_ara, cons_ara, offset in rungs:
        for archetype, ara_val in [("engine", eng_ara), ("clock", 1.0),
                                    ("consumer", cons_ara)]:
            name = f"{prefix}_{archetype}"
            if prefix == "Target" and archetype == "engine":
                ara_val = ara; ba = fit_ba
            else: ba = 1.0
            node = ARAGearNode(name, rung_period, ara_val,
                               rung_power, ba, archetype,
                               seed_ara=ara, rung_offset=offset)
            node.set_t_ref(fit_tr)
            if prefix == "Target" and archetype == "engine":
                node.set_field_partners(gear_partners)
            all_nodes[name] = node
            if archetype == "engine": engine_nodes[prefix] = node

    # Wire with ARA-DRIVEN gear ratio
    rung_list = [(rp, prefix, offset) for rp, _, prefix, _, _, offset in rungs]
    for i, (rp, prefix, offset) in enumerate(rung_list):
        engine = all_nodes[f"{prefix}_engine"]
        clock_n = all_nodes[f"{prefix}_clock"]
        consumer = all_nodes[f"{prefix}_consumer"]

        # Horizontal: full
        consumer.add_drain(engine, rate=PHI_LEAK)
        clock_n.add_drain(engine, rate=PHI_LEAK)
        engine.add_feed_target(clock_n, INV_PHI_4, "horizontal")
        clock_n.add_feed_target(consumer, INV_PHI_4, "horizontal")

        # Down: full
        if i < len(rung_list) - 1:
            below_prefix = rung_list[i + 1][1]
            engine.add_feed_target(all_nodes[f"{below_prefix}_engine"],
                                   INV_PHI_4, "vertical_down")

        # Up: ARA-DRIVEN gear ratio
        if i > 0:
            above_prefix = rung_list[i - 1][1]
            # The gear ratio slides with ARA:
            #   consumer (low ARA) → weak up (asymmetric)
            #   engine (high ARA) → strong up (nearly symmetric)
            up_rate = PHI_LEAK * gear_ratio
            consumer.add_drain(all_nodes[f"{above_prefix}_engine"],
                              rate=up_rate)

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
                "name": system_name, "fit_mae": fit_mae, "bounces": 0,
                "gear_ratio": gear_ratio}
    errors, preds = [], []
    for i in range(len(times)):
        idx = np.argmin(np.abs(snap_t - times[i]))
        preds.append(snap_a[idx])
        errors.append(abs(snap_a[idx] - peaks[i]))
    mae = np.mean(errors)
    corr = np.corrcoef(preds, peaks)[0, 1] if len(preds) > 2 else 0
    sine_mae = np.mean(np.abs(peaks - np.mean(peaks)))

    return {
        "mae": mae, "fit_mae": fit_mae, "corr": corr,
        "snaps": target_node.local_ticks,
        "preds": np.array(preds), "errors": np.array(errors),
        "sine_mae": sine_mae,
        "improvement": (1 - mae / sine_mae) * 100 if sine_mae > 0 else 0,
        "failed": False, "name": system_name,
        "bounces": target_node.bounce_count,
        "gear_ratio": gear_ratio,
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
print("Script 243h — ARA-Driven Gear Ratio")
print("=" * 78)
print()
print("ARA sets the gear ratio (up/down pipe asymmetry):")
print(f"  {'ARA':>6} │ {'Gear Ratio':>10} │ {'Up Pipe':>10} │ {'Description'}")
print(f"  {'─'*6}─┼─{'─'*10}─┼─{'─'*10}─┼─{'─'*30}")

for test_ara, desc in [(0.0, "Pure consumer"),
                        (0.15, "EQ (consumer)"),
                        (INV_PHI, "1/φ"),
                        (1.0, "Clock"),
                        (PHI, "Solar (engine)"),
                        (2.0, "Pure harmonic (ENSO)")]:
    gr = ara_gear_ratio(test_ara)
    up = PHI_LEAK * gr
    print(f"  {test_ara:>6.3f} │ {gr:>10.4f} │ {up:>10.6f} │ {desc}")

print()

# Reference results
ref = {
    '235b':  {"Solar (SSN)": 46.30, "ENSO (ONI)": 0.44, "Sanriku EQ": 1.19},
    '243b':  {"Solar (SSN)": 56.84, "ENSO (ONI)": 0.43, "Sanriku EQ": 0.60},
    '243f':  {"Solar (SSN)": 43.48, "ENSO (ONI)": 0.44, "Sanriku EQ": 1.48},
    '243g-A': {"Solar (SSN)": 57.08, "ENSO (ONI)": 0.45, "Sanriku EQ": 0.42},
}

print(f"  {'System':<16} │ {'235b':>7} │ {'243b':>7} │ {'243f':>7} │ {'243g-A':>7} │ {'243h':>7} │ {'Gear':>6} │ {'Best':>6}")
print(f"  {'─'*16}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*7}─┼─{'─'*6}─┼─{'─'*6}")

all_results = {}
for name, times, peaks, period, ara, rung in SYSTEMS:
    print(f"  Running {name}...", end="", flush=True)

    res = run_ara_gear(times, peaks, period=period, ara=ara,
                       target_rung=rung, system_name=name)
    all_results[name] = res

    if res["failed"]:
        print(f"\r  {name:<16} │  ---    │  ---    │  ---    │  ---    │  FAIL   │")
        continue

    vals = [ref['235b'][name], ref['243b'][name], ref['243f'][name],
            ref['243g-A'][name], res['mae']]
    labels = ['235b', '243b', '243f', '243g-A', '243h']
    best_i = vals.index(min(vals))
    gr = res['gear_ratio']

    print(f"\r  {name:<16} │ {vals[0]:>7.2f} │ {vals[1]:>7.2f} │ {vals[2]:>7.2f} │ "
          f"{vals[3]:>7.2f} │ {res['mae']:>7.2f} │ {gr:>6.4f} │ {labels[best_i]:>6}")


# Solar per-cycle
print(f"\n{'─' * 78}")
print("SOLAR PER-CYCLE — 243h ARA-Driven Gear")
print("─" * 78)

ra = all_results["Solar (SSN)"]
if not ra["failed"]:
    print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'Pred':>6} {'Err':>5} │")
    for i in range(len(solar_t)):
        print(f"  C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
              f"{ra['preds'][i]:>6.1f} {ra['errors'][i]:>5.1f} │")


# Summary
print(f"\n{'=' * 78}")
print("FULL 243 SERIES SUMMARY")
print("=" * 78)

all_variants = {
    '235b': ref['235b'],
    '243b': ref['243b'],
    '243f': ref['243f'],
    '243g-A': ref['243g-A'],
    '243h': {name: all_results[name]['mae'] for name in all_results if not all_results[name]['failed']},
}

print(f"\n  {'System':<16}", end="")
for v in all_variants: print(f" {v:>7}", end="")
print(f" {'Best':>7}")
print(f"  {'─'*16}", end="")
for v in all_variants: print(f" {'─'*7}", end="")
print(f" {'─'*7}")

for name, _, _, _, ara, _ in SYSTEMS:
    print(f"  {name:<16}", end="")
    vals = []; labels = []
    for v in all_variants:
        val = all_variants[v].get(name, 999)
        vals.append(val); labels.append(v)
        print(f" {val:>7.2f}", end="")
    best_i = vals.index(min(vals))
    print(f" {labels[best_i]:>7}")

    # Show gear ratio for this system
    if name in all_results and not all_results[name]['failed']:
        gr = all_results[name]['gear_ratio']
        print(f"  {'':16} (ARA={ara:.3f} → gear={gr:.4f})")

best_solar = all_results["Solar (SSN)"]['mae'] if not all_results["Solar (SSN)"]["failed"] else 999
print(f"\n  vs Champion (28.11): 243h Solar = {best_solar:.2f} (Δ={best_solar-28.11:+.2f})")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
print("=" * 78)
