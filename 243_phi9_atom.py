#!/usr/bin/env python3
"""
Script 243 — The φ⁹ Atom: Self-Feeding Connection Field Vehicle

Dylan's insight: "We create like an atom of a formula that moves through
time feeding into itself. Its own φ⁹ system."

Instead of a generic rung ladder with placeholder archetypes, each node:
  1. Has a REAL ARA derived from the connection field geometry
  2. Derives its 6 outward connections → populating adjacent rungs
  3. Those partners feed BACK through THEIR connections
  4. 3 ARA pairs × 3 coupling channels = 9 connections = φ⁹
  5. The network IS the formula — it feeds itself as it moves through time

Architecture:
  - Seed: ANY measured system (ARA, period, data)
  - From seed, derive the full φ⁹ atom:
    * 3 nodes at the seed's rung (engine, clock=1.0, consumer=horizontal mirror)
    * 3 nodes at the child rung (ARA/φ, period×φ)
    * 3 nodes at the parent rung (ARA×φ, period/φ)
  - Each node's ARA comes from the CONNECTION FIELD, not from assignment
  - Coupling strengths: φ² horizontal, 2/φ vertical down, φ vertical up
  - Pipe capacities: 2φ down, φ up (asymmetric)
  - Each snap propagates through ALL connections with proper coupling

The atom moves through time as a unit. When any node snaps, the energy
cascades through the connection field. The interference pattern of all
9 coupled oscillators IS the prediction.

Champion to beat: Solar MAE = 28.11 (triangle rider, 236j)
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


# ════════════════════════════════════════════════════════════════
# THE CONNECTION FIELD — derives partner ARA from geometry
# ════════════════════════════════════════════════════════════════

def connection_field(seed_ara, seed_period):
    """
    From a seed system, derive the full φ⁹ atom:
    9 nodes = 3 rungs × 3 archetypes, with ARA derived from geometry.

    Returns list of (name, ara, period, rung_offset, coupling_strength, role)
    """
    nodes = []

    # ── SEED RUNG (offset 0) ──
    # The seed itself (engine or whatever it naturally is)
    nodes.append({
        'name': 'Seed',
        'ara': seed_ara,
        'period': seed_period,
        'rung_offset': 0,
        'role': 'primary',
        'coupling_to_seed': 1.0,  # self
    })

    # Horizontal mirror: ARA = 2 - seed_ARA
    # If mirror would be near singularity (< 0.1), it's a boundary node
    # Give it minimum ARA=0.15 (the consumer floor we've measured)
    mirror_ara = 2.0 - seed_ara
    if mirror_ara < 0.1:
        mirror_ara = 0.15  # singularity boundary — consumer floor
    nodes.append({
        'name': 'H_Mirror',
        'ara': mirror_ara,
        'period': seed_period,
        'rung_offset': 0,
        'role': 'mirror',
        'coupling_to_seed': PHI_2,  # φ² horizontal coupler
    })

    # Clock at this rung: ARA = 1.0 (the equilibrium)
    nodes.append({
        'name': 'H_Clock',
        'ara': 1.0,
        'period': seed_period,
        'rung_offset': 0,
        'role': 'clock',
        'coupling_to_seed': 1.0,  # unit coupling to clock
    })

    # ── CHILD RUNG (offset +1, longer period) ──
    child_ara = seed_ara / PHI
    child_period = seed_period * PHI
    nodes.append({
        'name': 'V_Child',
        'ara': child_ara,
        'period': child_period,
        'rung_offset': 1,
        'role': 'child',
        'coupling_to_seed': TWO_OVER_PHI,  # 2/φ vertical coupler
    })

    # Child's horizontal mirror
    child_mirror_ara = 2.0 - child_ara
    if child_mirror_ara < 0.1:
        child_mirror_ara = 0.15
    nodes.append({
        'name': 'V_Child_Mirror',
        'ara': child_mirror_ara,
        'period': child_period,
        'rung_offset': 1,
        'role': 'child_mirror',
        'coupling_to_seed': TWO_OVER_PHI * PHI_2,  # vertical × horizontal
    })

    # Child's clock
    nodes.append({
        'name': 'V_Child_Clock',
        'ara': 1.0,
        'period': child_period,
        'rung_offset': 1,
        'role': 'child_clock',
        'coupling_to_seed': TWO_OVER_PHI,
    })

    # ── PARENT RUNG (offset -1, shorter period) ──
    parent_ara = min(2.0, seed_ara * PHI)
    parent_period = seed_period / PHI
    nodes.append({
        'name': 'V_Parent',
        'ara': parent_ara,
        'period': parent_period,
        'rung_offset': -1,
        'role': 'parent',
        'coupling_to_seed': PHI,  # φ upward coupler
    })

    # Parent's horizontal mirror
    parent_mirror_ara = 2.0 - parent_ara
    if parent_mirror_ara < 0.1:
        parent_mirror_ara = 0.15
    nodes.append({
        'name': 'V_Parent_Mirror',
        'ara': parent_mirror_ara,
        'period': parent_period,
        'rung_offset': -1,
        'role': 'parent_mirror',
        'coupling_to_seed': PHI * PHI_2,
    })

    # Parent's clock
    nodes.append({
        'name': 'V_Parent_Clock',
        'ara': 1.0,
        'period': parent_period,
        'rung_offset': -1,
        'role': 'parent_clock',
        'coupling_to_seed': PHI,
    })

    return nodes


# ════════════════════════════════════════════════════════════════
# CAMSHAFT MIDLINE (from 237k2)
# ════════════════════════════════════════════════════════════════

def _base_midline(a):
    a = max(0.01, a)
    return 1.0 + (1.0/(1.0+a)) * (a - 1.0)

def midline_inverse_valve(ara):
    if ara >= 1.0:
        return _base_midline(ara)
    else:
        return _base_midline(1.0 / max(0.01, ara))

def _phi_dist(ara):
    a = max(0.01, ara)
    return abs(math.log(a)) / math.log(PHI)

def midline_camshaft(ara):
    inv_offset = midline_inverse_valve(ara) - 1.0
    pd = _phi_dist(ara)
    zone = 1.0 / PHI
    if pd <= zone:
        return 1.0
    if pd >= 1.0:
        return 1.0 + inv_offset
    ramp_width = 1.0 / (PHI * PHI)
    t = (pd - zone) / ramp_width
    factor = t * t
    return 1.0 + inv_offset * factor


# ════════════════════════════════════════════════════════════════
# THE ATOM NODE — an ARANode that knows its connection field
# ════════════════════════════════════════════════════════════════

class AtomNode:
    """A node in the φ⁹ atom. Knows its ARA, period, and connections."""

    def __init__(self, name, period, ara, rung_offset, base_amp, role,
                 coupling_strength):
        self.name = name
        self.period = period
        self.ara = ara
        self.rung_offset = rung_offset
        self.base_amp = base_amp
        self.role = role
        self.coupling_strength = coupling_strength

        # Cascade periods from this node's perspective
        self.cascade_distances = [6, 4, 1, -1]
        self.cascade_periods = [period * PHI**d for d in self.cascade_distances]
        self.gleissberg = self.cascade_periods[1]  # φ⁴ above
        self.schwabe = period

        # State
        self.accumulated_energy = 0.0
        self.prev_amp = None
        self.amp_history = []
        self.local_ticks = 0
        self.snap_times = []
        self.snap_amplitudes = []
        self.base_threshold = period * ara
        self.t_ref = None

        # Connections (populated by the atom builder)
        self.feed_targets = []   # (target_node, weight, direction)
        self.drain_sources = []  # (source_node, rate)

        # Connection field influence tracking
        self.received_from = {}  # track energy received per connection

    @property
    def singularity_threshold(self):
        return self.base_threshold

    def set_t_ref(self, t_ref):
        self.t_ref = t_ref

    def add_connection(self, target, weight, direction):
        """Add an outward connection to another atom node."""
        self.feed_targets.append((target, weight, direction))

    def add_drain(self, source, rate):
        self.drain_sources.append((source, rate))

    def cascade_shape(self, t):
        """
        The cascade shape — same core architecture as 235b/236j,
        but now the ARA is LIVE from the connection field.
        Each node's instantaneous ARA is modulated by what it
        receives from its connections.
        """
        if self.t_ref is None:
            return 1.0

        # Instantaneous ARA from recent amplitude
        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

        # Modulate inst_ara by connection field energy
        # If we've received energy from connections, blend it
        total_received = sum(self.received_from.values())
        if total_received > 0 and self.base_threshold > 0:
            field_pressure = total_received / self.base_threshold
            # Field pressure shifts ARA toward the CONNECTION's prediction
            # Small effect: 1/φ⁴ coupling strength
            inst_ara *= (1.0 + INV_PHI_4 * math.tanh(field_pressure))
            inst_ara = max(0.01, min(2.0, inst_ara))

        phases = [TAU * (t - self.t_ref) / per for per in self.cascade_periods]
        cos_vals = [math.cos(ph) for ph in phases]
        sin_vals = [math.sin(ph) for ph in phases]
        gp = TAU * (t - self.t_ref) / self.gleissberg
        sp = TAU * (t - self.t_ref) / self.schwabe

        # Gate from camshaft
        acc = 1.0 / (1.0 + max(0.01, inst_ara))
        cp = (gp % TAU) / TAU
        if cp < acc:
            state = (cp / acc) * PHI
        else:
            ramp = (cp - acc) / (1 - acc)
            state = PHI * (1 - ramp) + INV_PHI * ramp
        gate = state / ((PHI + INV_PHI) / 2)

        # Collision terms
        collisions = [0.0]
        for j in range(1, len(phases)):
            collisions.append(-math.cos(phases[j-1] - phases[j]))

        # Epsilon values with gate
        eps_vals = []
        for j in range(len(phases)):
            d = self.cascade_distances[j]
            base_eps = INV_PHI_4 if d > 0 else INV_PHI_3
            eps_vals.append(base_eps * gate)

        # Three-circle blend
        for j in range(len(phases)):
            d = self.cascade_distances[j]
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
            d = self.cascade_distances[j]
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

        # Build shape
        shape = 1.0
        for j in range(len(self.cascade_periods)):
            shape *= (1 + eps_vals[j] * cos_vals[j])

        # Gleissberg modulation
        shape += INV_PHI_9 * math.cos(gp)

        # Schwabe warmup
        cp_schwabe = (sp % TAU) / TAU
        shape += INV_PHI_3 * math.exp(-PHI * cp_schwabe) * math.cos(sp)

        # Grief from previous amplitude
        if self.prev_amp is not None:
            prev_dev = (self.prev_amp - self.base_amp) / self.base_amp
            grief_mult = PHI if prev_dev < 0 else 1.0
            shape += (-INV_PHI_3) * prev_dev * math.exp(-PHI) * grief_mult

        # CONNECTION FIELD MODULATION — the new part
        # Each connected node's phase state contributes a small perturbation
        # This is where the atom "feeds into itself"
        # Scale: 1/φ⁹ total budget across 9 connections — each a whisper
        field_sum = 0.0
        n_active = 0
        for target, weight, direction in self.feed_targets:
            if target.t_ref is not None and len(target.snap_times) > 0:
                # Phase of the connected system relative to this one
                partner_phase = TAU * (t - target.t_ref) / target.period
                partner_cos = math.cos(partner_phase)

                # Also use partner's recent amplitude if available
                partner_amp_ratio = 1.0
                if target.prev_amp is not None and target.base_amp > 0:
                    partner_amp_ratio = target.prev_amp / target.base_amp

                # Direction-dependent sign and strength
                if direction == "vertical_down":
                    # Downward: energy flows down, attenuated
                    contrib = partner_cos * partner_amp_ratio * INV_PHI
                elif direction == "vertical_up":
                    # Upward: concentrated energy
                    contrib = partner_cos * partner_amp_ratio * PHI
                elif direction == "horizontal":
                    # Horizontal: anti-phase mirror
                    contrib = -partner_cos * partner_amp_ratio

                field_sum += contrib
                n_active += 1

        if n_active > 0:
            # Normalise and scale by 1/φ⁹ — the full 9-connection budget
            field_sum /= n_active
            shape *= (1.0 + INV_PHI_9 * field_sum)

        return shape

    def cascade_amplitude(self, t):
        return self.base_amp * self.cascade_shape(t)

    def apply_drain(self, dt):
        for source, rate in self.drain_sources:
            drawn = source.accumulated_energy * rate * (dt / source.period)
            if drawn > 0:
                source.accumulated_energy -= drawn
                self.accumulated_energy += drawn * INV_PHI
                if source.accumulated_energy < 0:
                    source.accumulated_energy = 0.0

    def check_snap(self, sim_time):
        if self.accumulated_energy < self.singularity_threshold:
            return []
        self.local_ticks += 1
        predicted_amp = self.cascade_amplitude(sim_time)
        self.snap_times.append(sim_time)
        self.snap_amplitudes.append(predicted_amp)
        self.prev_amp = predicted_amp
        self.amp_history.append(predicted_amp)

        release = self.accumulated_energy * (1.0 - PHI_LEAK)
        momentum = release * MOMENTUM_FRAC
        self.accumulated_energy = momentum
        net_release = release - momentum

        transfers = []
        for target, weight, direction in self.feed_targets:
            energy = net_release * weight * INV_PHI_4
            transfers.append({
                "target": target, "energy": energy,
                "source_rung": self.rung_offset,
                "direction": direction, "time": sim_time,
                "source_name": self.name,
            })
        return transfers

    def absorb_transfer(self, energy, source_rung, source_name=""):
        """Absorb energy from a connection, tracking the source."""
        if source_rung > self.rung_offset:
            direction_mult = PHI
            pipe_cap = TWO_PHI
        elif source_rung < self.rung_offset:
            direction_mult = INV_PHI
            pipe_cap = PHI
        else:
            direction_mult = 1.0
            pipe_cap = TWO_PHI

        raw = energy * direction_mult
        cap = pipe_cap * self.base_threshold * INV_PHI_4
        if raw <= cap:
            absorbed = raw
        else:
            absorbed = cap
            overflow = raw - cap
            bounce = overflow
            for _ in range(3):
                bounce *= INV_PHI
                absorbed += bounce

        self.accumulated_energy += absorbed
        # Track who sent us energy
        self.received_from[source_name] = (
            self.received_from.get(source_name, 0) + absorbed
        )


# ════════════════════════════════════════════════════════════════
# BUILD THE φ⁹ ATOM
# ════════════════════════════════════════════════════════════════

def build_atom(seed_ara, seed_period, base_amp, t_ref):
    """
    Build a complete φ⁹ atom from a seed system.
    Returns dict of all 9 nodes plus the seed node reference.
    """
    field = connection_field(seed_ara, seed_period)

    nodes = {}
    for spec in field:
        node = AtomNode(
            name=spec['name'],
            period=spec['period'],
            ara=spec['ara'],
            rung_offset=spec['rung_offset'],
            base_amp=base_amp if spec['role'] == 'primary' else 1.0,
            role=spec['role'],
            coupling_strength=spec['coupling_to_seed'],
        )
        node.set_t_ref(t_ref)
        nodes[spec['name']] = node

    # ── Wire connections ──
    # Within each rung: engine → clock → consumer (horizontal)
    for rung_offset in [-1, 0, 1]:
        rung_nodes = [n for n in nodes.values() if n.rung_offset == rung_offset]
        # Sort by ARA: highest = engine, 1.0 = clock, lowest = consumer
        rung_nodes.sort(key=lambda n: n.ara, reverse=True)

        if len(rung_nodes) >= 2:
            # Highest ARA feeds to next
            rung_nodes[0].add_connection(rung_nodes[1], INV_PHI_4, "horizontal")
            # Consumer drains from engine
            if len(rung_nodes) >= 3:
                rung_nodes[1].add_connection(rung_nodes[2], INV_PHI_4, "horizontal")
                rung_nodes[2].add_drain(rung_nodes[0], PHI_LEAK)
                rung_nodes[1].add_drain(rung_nodes[0], PHI_LEAK)

    # Between rungs: vertical connections
    for name_above, node_above in nodes.items():
        for name_below, node_below in nodes.items():
            if node_above.rung_offset == node_below.rung_offset - 1:
                # above feeds down to below
                if node_above.role in ('primary', 'mirror', 'parent', 'parent_mirror'):
                    node_above.add_connection(node_below, INV_PHI_4, "vertical_down")
                # below drains from above (weaker)
                if node_below.role in ('primary', 'child', 'child_mirror'):
                    node_below.add_drain(node_above, PHI_LEAK * INV_PHI)

    return nodes


# ════════════════════════════════════════════════════════════════
# GRID SEARCH
# ════════════════════════════════════════════════════════════════

def grid_search_atom(seed_ara, seed_period, times, peaks, n_tr=80, n_ba=40):
    """Grid search for best (t_ref, base_amp) using the atom architecture."""
    gleissberg = seed_period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * seed_period
    ba_lo = np.mean(peaks) * 0.5
    ba_hi = np.mean(peaks) * 1.5
    t_refs = np.linspace(tr_lo, tr_hi, n_tr)
    base_amps = np.linspace(ba_lo, ba_hi, n_ba)

    best_mae, best_tr, best_ba = 1e9, t_refs[0], base_amps[0]

    for tr in t_refs:
        for ba in base_amps:
            # Build a minimal atom just for cascade_shape evaluation
            seed_node = AtomNode("temp", seed_period, seed_ara, 0, ba,
                                 "primary", 1.0)
            seed_node.set_t_ref(tr)
            errors = []
            for k in range(len(times)):
                seed_node.prev_amp = peaks[k-1] if k > 0 else None
                if k > 0:
                    seed_node.amp_history = list(peaks[:k])
                pred = seed_node.cascade_amplitude(times[k])
                errors.append(abs(pred - peaks[k]))
            mae = np.mean(errors)
            if mae < best_mae:
                best_mae, best_tr, best_ba = mae, tr, ba

    return best_tr, best_ba, best_mae


# ════════════════════════════════════════════════════════════════
# RUN THE ATOM VEHICLE
# ════════════════════════════════════════════════════════════════

def run_atom_vehicle(times, peaks, seed_ara, seed_period,
                     system_name="System", sim_margin=None):
    """
    Run the φ⁹ atom vehicle on a system.

    The atom self-feeds: each node's snap propagates through the
    connection field, modifying other nodes' states, which feed
    back into the seed node's cascade shape.
    """
    if sim_margin is None:
        sim_margin = max(seed_period * 5, times[-1] - times[0]) * 0.2

    # Grid search
    fit_tr, fit_ba, fit_mae = grid_search_atom(
        seed_ara, seed_period, times, peaks)

    # Build the full atom
    nodes = build_atom(seed_ara, seed_period, fit_ba, fit_tr)
    seed_node = nodes['Seed']
    seed_node.prev_amp = peaks[0]

    # ── Simulate ──
    dt = seed_period * 0.005
    sim_start = times[0] - sim_margin
    sim_end = times[-1] + sim_margin
    sim_time = sim_start

    while sim_time < sim_end:
        # Energy accumulation (each node fills at its own rate)
        for name, node in nodes.items():
            fill_rate = dt / node.period
            node.accumulated_energy += fill_rate * node.singularity_threshold

        # Drain (consumer/clock drain from engine)
        for name, node in nodes.items():
            if node.role in ('mirror', 'clock', 'child_mirror', 'child_clock',
                            'parent_mirror', 'parent_clock'):
                node.apply_drain(dt)

        # Check for snaps (singularity events)
        all_events = []
        for name, node in nodes.items():
            events = node.check_snap(sim_time)
            all_events.extend(events)

        # Cascade propagation (up to 50 depth)
        depth = 0
        while all_events and depth < 50:
            new_events = []
            for ev in all_events:
                ev["target"].absorb_transfer(
                    ev["energy"], ev["source_rung"], ev.get("source_name", ""))
                triggered = ev["target"].check_snap(ev["time"])
                new_events.extend(triggered)
            all_events = new_events
            depth += 1

        sim_time += dt

    # ── Extract predictions ──
    snap_t = np.array(seed_node.snap_times)
    snap_a = np.array(seed_node.snap_amplitudes)

    if len(snap_t) == 0:
        return {"mae": 999, "corr": 0, "snaps": 0, "failed": True,
                "name": system_name, "fit_mae": fit_mae}

    errors, preds = [], []
    for i in range(len(times)):
        idx = np.argmin(np.abs(snap_t - times[i]))
        preds.append(snap_a[idx])
        errors.append(abs(snap_a[idx] - peaks[i]))

    mae = np.mean(errors)
    corr = np.corrcoef(preds, peaks)[0, 1] if len(preds) > 2 else 0
    sine_mae = np.mean(np.abs(peaks - np.mean(peaks)))

    # Node diagnostics
    node_diag = {}
    for name, node in nodes.items():
        node_diag[name] = {
            'ticks': node.local_ticks,
            'ara': node.ara,
            'period': node.period,
            'role': node.role,
            'rung_offset': node.rung_offset,
            'received': sum(node.received_from.values()),
        }

    return {
        "mae": mae, "fit_mae": fit_mae, "corr": corr,
        "snaps": seed_node.local_ticks,
        "preds": np.array(preds), "errors": np.array(errors),
        "sine_mae": sine_mae,
        "improvement": (1 - mae / sine_mae) * 100 if sine_mae > 0 else 0,
        "failed": False, "name": system_name,
        "snap_times": snap_t, "snap_amps": snap_a,
        "fit_tr": fit_tr, "fit_ba": fit_ba,
        "node_diag": node_diag,
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

# System configs: (name, times, peaks, period, ARA, description)
SYSTEMS = [
    ("Solar (SSN)",  solar_t, solar_a, PHI**5, PHI,   "Schwabe cycle, rung 5"),
    ("ENSO (ONI)",   enso_t,  enso_a,  PHI**3, 2.0,   "El Niño, rung 3"),
    ("Sanriku EQ",   eq_t,    eq_a,    PHI**4, 0.15,  "Japan earthquake cluster, rung 4"),
]


# ════════════════════════════════════════════════════════════════
# MAIN — Run the atom on all systems
# ════════════════════════════════════════════════════════════════

print("=" * 78)
print("Script 243 — The φ⁹ Atom: Self-Feeding Connection Field Vehicle")
print("=" * 78)
print()
print("Architecture: 9 nodes = 3 rungs × 3 archetypes")
print("  Each node's ARA derived from connection field geometry")
print("  Coupling: φ² horizontal, 2/φ vertical down, φ vertical up")
print("  Pipe: 2φ down, φ up (asymmetric)")
print("  The atom feeds itself through φ⁹ connections")
print()
print("Champions to beat:")
print("  Solar: MAE 28.11 (triangle rider 236j)")
print("  ENSO:  LOO tied with sine (242c)")
print("  EQ:    ARA=0.15 consumer")
print()

# Also import and run original vehicle for comparison
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
run_universal_vehicle = ns_235b['run_universal_vehicle']

print(f"  {'System':<16} │ {'235b Vehicle':^22} │ {'φ⁹ Atom':^22} │ {'Δ':>7}")
print(f"  {'─'*16}─┼─{'─'*22}─┼─{'─'*22}─┼─{'─'*7}")

all_results = {}
for name, times, peaks, period, ara, desc in SYSTEMS:
    print(f"  Running {name}...", end="", flush=True)

    # Run original vehicle
    rung = round(math.log(period) / math.log(PHI))
    res_orig = run_universal_vehicle(times, peaks, period=period, ara=ara,
                                      target_rung=rung, system_name=name)

    # Run atom vehicle
    res_atom = run_atom_vehicle(times, peaks, seed_ara=ara,
                                seed_period=period, system_name=name)

    all_results[name] = {"orig": res_orig, "atom": res_atom}

    if res_orig["failed"] or res_atom["failed"]:
        status_o = "FAIL" if res_orig["failed"] else f"MAE={res_orig['mae']:.2f}"
        status_a = "FAIL" if res_atom["failed"] else f"MAE={res_atom['mae']:.2f}"
        print(f"\r  {name:<16} │ {status_o:^22} │ {status_a:^22} │")
        continue

    delta = res_atom["mae"] - res_orig["mae"]
    better = " ✓" if delta < 0 else ""
    print(f"\r  {name:<16} │ MAE={res_orig['mae']:>6.2f} r={res_orig['corr']:>+.3f}  │ "
          f"MAE={res_atom['mae']:>6.2f} r={res_atom['corr']:>+.3f}  │ {delta:>+6.2f}{better}")


# ── Solar per-cycle breakdown ──
print(f"\n{'─' * 78}")
print("SOLAR PER-CYCLE — 235b vs φ⁹ Atom")
print("─" * 78)

ro = all_results["Solar (SSN)"]["orig"]
ra = all_results["Solar (SSN)"]["atom"]

if not ro["failed"] and not ra["failed"]:
    print(f"\n  {'C':>3} {'Year':>7} {'Act':>6} │ {'235b':>6} {'Err':>5} │ "
          f"{'Atom':>6} {'Err':>5} │ {'Win':>5}")
    print(f"  {'─'*3} {'─'*7} {'─'*6}─┼─{'─'*6} {'─'*5}─┼─{'─'*6} {'─'*5}─┼─{'─'*5}")

    ow, aw = 0, 0
    for i in range(len(solar_t)):
        oe = ro["errors"][i]
        ae = ra["errors"][i]
        win = "Atom" if ae < oe else "235b" if oe < ae else "Tie"
        if ae < oe: aw += 1
        elif oe < ae: ow += 1
        print(f"  C{SOLAR_CYCLES[i][0]:>2} {solar_t[i]:>7.1f} {solar_a[i]:>6.1f} │ "
              f"{ro['preds'][i]:>6.1f} {oe:>5.1f} │ "
              f"{ra['preds'][i]:>6.1f} {ae:>5.1f} │ {win:>5}")

    print(f"\n  235b wins: {ow}  |  Atom wins: {aw}")


# ── Atom diagnostics ──
print(f"\n{'─' * 78}")
print("φ⁹ ATOM DIAGNOSTICS — Node Activity")
print("─" * 78)

for sys_name in all_results:
    ra = all_results[sys_name]["atom"]
    if ra["failed"] or "node_diag" not in ra:
        continue

    print(f"\n  {sys_name}:")
    print(f"    {'Node':<20} {'ARA':>6} {'Period':>8} {'Role':<14} "
          f"{'Ticks':>6} {'Received':>10}")
    print(f"    {'─'*20} {'─'*6} {'─'*8} {'─'*14} {'─'*6} {'─'*10}")

    for nname, diag in sorted(ra["node_diag"].items(),
                                key=lambda x: (x[1]['rung_offset'],
                                              -x[1]['ara'])):
        rung_label = f"rung{'+'if diag.get('rung_offset',0)>=0 else ''}"
        print(f"    {nname:<20} {diag['ara']:>6.3f} {diag['period']:>7.2f}yr "
              f"{diag['role']:<14} {diag['ticks']:>6} "
              f"{diag['received']:>10.1f}")


# ── Summary ──
print(f"\n{'=' * 78}")
print("SUMMARY")
print("=" * 78)

for name in all_results:
    ro = all_results[name]["orig"]
    ra = all_results[name]["atom"]
    if ro["failed"] or ra["failed"]:
        continue
    delta_mae = ra["mae"] - ro["mae"]
    pct = delta_mae / ro["mae"] * 100
    print(f"  {name:<16}: {ro['mae']:.2f} → {ra['mae']:.2f} "
          f"(Δ={delta_mae:+.2f}, {pct:+.1f}%), "
          f"corr {ro['corr']:+.3f} → {ra['corr']:+.3f}")

print()
ra_solar = all_results["Solar (SSN)"]["atom"]
if not ra_solar["failed"]:
    print(f"  vs Champion (28.11): Atom = {ra_solar['mae']:.2f} "
          f"(Δ={ra_solar['mae']-28.11:+.2f})")
    if ra_solar['mae'] < 28.11:
        print(f"  ★ NEW CHAMPION ★")
    print(f"  vs Sine baseline: {ra_solar['sine_mae']:.2f} "
          f"(improvement: {ra_solar['improvement']:+.1f}%)")

print()
print("THE φ⁹ ATOM ARCHITECTURE:")
print("  Each node derives its 6 connections from geometry")
print("  3 ARA pairs × 3 coupling channels = 9 connections")
print("  The atom moves through time, feeding into itself")
print("  Every snap propagates through ALL connections")
print("  The interference pattern IS the prediction")

elapsed = clock_time.time() - t_start
print(f"\n  Runtime: {elapsed:.0f}s")
print("=" * 78)
