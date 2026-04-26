#!/usr/bin/env python3
"""
Script 236O — Phase-Aware Gate: Champion Architecture + PTF Timing

THE PRINCIPLE (Dylan + GPT + data):
  "Timing and the ARA of the original system should be the only
  variable you need to know before letting this rip."

  The LOO analysis proved: the champion (226 v4) wins because it has
  ONE dynamic knob — the gate timing — and everything else is locked
  geometry. Our 17-knob meta-triangle fitted beautifully but collapsed
  under cross-validation.

  GPT's insight: wave phase should control TIMING, not DISTANCES.
  The cascade distances are the road — universal geometry, [6,4,1,-1].
  What changes is how the vehicle interacts with that road.

ARCHITECTURE (four clean layers):

  1. GEOMETRY (frozen):
     - Cascade distances: [6, 4, 1, -1] — locked, universal
     - Cascade periods: P × φ^d for each distance
     - Three-circle blend weights: φ, 1/φ — locked
     - Collision, tension, grief coefficients — all locked
     - Base epsilon: 1/φ⁴ (positive d), 1/φ³ (negative d)

  2. STATE (two numbers):
     - inst_ara = prev_amp / base_amp (energy state)
     - wave_phase = where on the cycle (derived from amplitude history)
     Both feed into the gate. That's all.

  3. DYNAMICS (the gate):
     - acc_frac = f(inst_ara, wave_phase)
     - Champion form: acc = 1 / (1 + inst_ara)
     - Phase modulation: acc is shifted by wave_phase position
       At peak: gate opens earlier (system is about to reverse → snap sooner)
       At trough: gate opens later (system is building → wait longer)
       At flow: gate timing unchanged (maximum momentum, don't interfere)

  4. READOUT:
     - base_amp × cascade_shape(t)
     - Cascade shape is computed with FIXED distances, modulated gate

  Only two things need to be known: the system's ARA and its timing.
  Everything else is derived from the geometry.
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
PHI_LEAK = INV_PHI ** 4
LOG2 = math.log(2)
MOMENTUM_FRAC = INV_PHI ** 3

# LOCKED distances — universal geometry, never changes
CASCADE_DISTANCES = [6, 4, 1, -1]


# ================================================================
# WAVE PHASE DETECTION
# ================================================================

def detect_wave_phase(amp_history, base_amp):
    """Determine where on the wave cycle the system sits.

    Returns a single scalar: phase_shift.
      phase_shift > 0 → near peak (gate should open earlier)
      phase_shift < 0 → near trough (gate should open later)
      phase_shift ≈ 0 → in flow (don't interfere)

    The shift is bounded by ±1/φ² to prevent the gate from being
    pushed outside its stable operating range.
    """
    if len(amp_history) < 2 or base_amp <= 0:
        return 0.0

    # Current amplitude ratio
    curr = amp_history[-1] / base_amp
    curr = max(0.01, min(3.0, curr))

    # Derivative (direction of travel)
    prev = amp_history[-2] / base_amp
    prev = max(0.01, min(3.0, prev))
    d_amp = curr - prev

    # Smooth with third point if available
    if len(amp_history) >= 3:
        prev2 = amp_history[-3] / base_amp
        prev2 = max(0.01, min(3.0, prev2))
        d_amp = 0.5 * d_amp + 0.5 * (prev - prev2)

    # Height above/below mean
    deviation = curr - 1.0  # positive = above mean, negative = below

    # Phase position:
    # Near peak: high amplitude AND falling → positive shift (snap sooner)
    # Near trough: low amplitude AND rising → negative shift (wait longer)
    # Flow: high |derivative|, near mean → zero shift (don't interfere)

    # The shift is the product of deviation and anti-derivative
    # At peak: deviation > 0, d_amp ≈ 0 or < 0 → shift positive
    # At trough: deviation < 0, d_amp ≈ 0 or > 0 → shift negative
    # At flow: deviation ≈ 0 → shift ≈ 0 regardless of derivative
    phase_shift = deviation * max(0, 1.0 - abs(d_amp) * 2.0)

    # Bound to ±1/φ² (gate stays in stable range)
    max_shift = INV_PHI_2
    phase_shift = max(-max_shift, min(max_shift, phase_shift))

    return phase_shift


# ================================================================
# EXEC 235b (for vehicle pipeline)
# ================================================================

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
build_rung_ladder = ns_235b['build_rung_ladder']
pipe_transfer_reverb = ns_235b['pipe_transfer_reverb']
run_universal_vehicle = ns_235b['run_universal_vehicle']


# ================================================================
# PHASE-GATE NODE
# ================================================================

class PhaseGateNode(OrigARANode):
    """Champion cascade architecture + phase-aware gate timing.

    GEOMETRY: Locked. Distances [6,4,1,-1], three-circle blend,
    collision, tension, grief — all exactly as in champion 226 v4.

    STATE: Two inputs to the gate:
      1. inst_ara = prev_amp / base_amp (energy state, same as champion)
      2. phase_shift = scalar from wave phase detection (NEW)

    DYNAMICS: Gate accumulation fraction combines both:
      acc = 1 / (1 + inst_ara) + phase_weight × phase_shift

    READOUT: base_amp × cascade_shape(t) — same as champion.

    phase_weight controls how much the wave phase affects gate timing.
    At phase_weight=0, this IS the champion.
    """

    def __init__(self, name, period, ara, rung, base_amp, archetype):
        super().__init__(name, period, ara, rung, base_amp, archetype)
        self.recent_amps = []
        self.phase_weight = 0.0  # how much phase affects gate timing

    def cascade_shape(self, t):
        if self.t_ref is None:
            return 1.0

        # Track amplitude history
        if self.prev_amp is not None:
            self.recent_amps.append(self.prev_amp)
            if len(self.recent_amps) > 10:
                self.recent_amps = self.recent_amps[-10:]

        # ── STATE: Two inputs ──
        if self.prev_amp is not None and self.base_amp > 0:
            inst_ara = self.prev_amp / self.base_amp
            inst_ara = max(0.01, min(2.0, inst_ara))
        else:
            inst_ara = self.ara

        phase_shift = detect_wave_phase(self.recent_amps, self.base_amp)

        # ── DYNAMICS: Phase-aware gate ──
        # Champion gate: acc = 1 / (1 + inst_ara)
        base_acc = 1.0 / (1.0 + max(0.01, inst_ara))

        # Phase modulation of gate timing
        # phase_shift > 0 (peak) → reduce acc → gate opens earlier
        # phase_shift < 0 (trough) → increase acc → gate opens later
        # phase_shift ≈ 0 (flow) → no change
        acc = base_acc + self.phase_weight * phase_shift
        acc = max(0.15, min(0.85, acc))  # keep in stable range

        # ── GEOMETRY: All locked, same as champion ──
        phases = [TAU * (t - self.t_ref) / per for per in self.cascade_periods]
        cos_vals = [math.cos(ph) for ph in phases]
        sin_vals = [math.sin(ph) for ph in phases]
        gp = TAU * (t - self.t_ref) / self.gleissberg
        sp = TAU * (t - self.t_ref) / self.schwabe

        # Gate with phase-modulated accumulation
        cp = (gp % TAU) / TAU
        if cp < acc:
            state = (cp / acc) * PHI
        else:
            ramp = (cp - acc) / (1 - acc)
            state = PHI * (1 - ramp) + INV_PHI * ramp
        gate = state / ((PHI + INV_PHI) / 2)

        # Collision pattern — locked geometry
        collisions = [0.0]
        for j in range(1, len(phases)):
            collisions.append(-math.cos(phases[j-1] - phases[j]))

        # Epsilon values — locked
        eps_vals = []
        for j in range(len(phases)):
            d = self.cascade_distances[j]
            base_eps = INV_PHI_4 if d > 0 else INV_PHI_3
            eps_vals.append(base_eps * gate)

        # Three-circle blend — locked
        for j in range(len(phases)):
            d = self.cascade_distances[j]
            space_phase = phases[j] * PHI_2
            rat_phase = phases[j] * TWO_OVER_PHI
            space_cos = math.cos(space_phase)
            rat_cos = math.cos(rat_phase)
            if d > 0:
                bl = (cos_vals[j] * PHI + space_cos * INV_PHI + rat_cos * INV_PHI)
                bl /= (PHI + INV_PHI + INV_PHI)
            else:
                bl = (cos_vals[j] * INV_PHI + space_cos * PHI + rat_cos * INV_PHI)
                bl /= (INV_PHI + PHI + INV_PHI)
            eps_vals[j] *= (1 + INV_PHI_4 * bl)

        # Collision dampening — locked
        for j in range(1, len(phases)):
            d = self.cascade_distances[j]
            if d < 0:
                eps_vals[j] /= (1 + collisions[j] * INV_PHI)
                eps_vals[j] *= (1 + collisions[j] * INV_PHI * 0.5)

        # Tension — locked
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

        # Cascade shape — locked formula
        shape = 1.0
        for j in range(len(self.cascade_periods)):
            shape *= (1 + eps_vals[j] * cos_vals[j])

        # Gleissberg residual — locked
        shape += INV_PHI_9 * math.cos(gp)

        # Schwabe pulse — locked
        cp_schwabe = (sp % TAU) / TAU
        shape += INV_PHI_3 * math.exp(-PHI * cp_schwabe) * math.cos(sp)

        # Grief — locked
        if self.prev_amp is not None:
            prev_dev = (self.prev_amp - self.base_amp) / self.base_amp
            grief_mult = PHI if prev_dev < 0 else 1.0
            shape += (-INV_PHI_3) * prev_dev * math.exp(-PHI) * grief_mult

        return shape


# ================================================================
# CASCADE-LEVEL EVALUATION
# ================================================================

def eval_cascade(times, peaks, period, ara, rung, phase_weight=0.0, fast=False):
    gleissberg = period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * period
    ba_lo = np.mean(peaks) * 0.5
    ba_hi = np.mean(peaks) * 1.5

    n_tr = 20 if fast else 80
    n_ba = 10 if fast else 40
    t_refs = np.linspace(tr_lo, tr_hi, n_tr)
    base_amps = np.linspace(ba_lo, ba_hi, n_ba)

    best_mae, best_tr, best_ba = 1e9, t_refs[0], base_amps[0]

    for tr in t_refs:
        for ba in base_amps:
            node = PhaseGateNode("t", period, ara, rung, ba, "engine")
            node.set_t_ref(tr)
            node.phase_weight = phase_weight
            errors = []
            for k in range(len(times)):
                node.prev_amp = peaks[k-1] if k > 0 else None
                if k > 0:
                    node.recent_amps = list(peaks[max(0,k-10):k])
                pred = node.cascade_amplitude(times[k])
                errors.append(abs(pred - peaks[k]))
            mae = np.mean(errors)
            if mae < best_mae:
                best_mae, best_tr, best_ba = mae, tr, ba

    # Best run trace
    node = PhaseGateNode("best", period, ara, rung, best_ba, "engine")
    node.set_t_ref(best_tr)
    node.phase_weight = phase_weight
    preds, errors, phase_shifts = [], [], []
    for k in range(len(times)):
        node.prev_amp = peaks[k-1] if k > 0 else None
        if k > 0:
            node.recent_amps = list(peaks[max(0,k-10):k])
        # Record phase shift before prediction
        ps = detect_wave_phase(node.recent_amps, best_ba)
        phase_shifts.append(ps)
        pred = node.cascade_amplitude(times[k])
        preds.append(pred)
        errors.append(abs(pred - peaks[k]))

    preds = np.array(preds)
    errors = np.array(errors)
    corr = np.corrcoef(preds, peaks)[0, 1] if len(preds) > 2 else 0

    return best_mae, corr, preds, errors, phase_shifts, best_tr, best_ba


# ================================================================
# LOO CROSS-VALIDATION
# ================================================================

def run_loo(times, peaks, period, ara, rung, phase_weight=0.0):
    n = len(times)
    loo_errors = []
    loo_preds = []

    for hold in range(n):
        mask = np.ones(n, dtype=bool)
        mask[hold] = False
        tr_times = times[mask]
        tr_peaks = peaks[mask]

        # Fit on training data
        gleissberg = period * PHI**4
        data_span = tr_times[-1] - tr_times[0]
        tr_lo = tr_times[0] - max(gleissberg, data_span)
        tr_hi = tr_times[0] + 2 * period
        ba_lo = np.mean(tr_peaks) * 0.5
        ba_hi = np.mean(tr_peaks) * 1.5

        t_refs = np.linspace(tr_lo, tr_hi, 80)
        base_amps = np.linspace(ba_lo, ba_hi, 40)

        best_mae, best_tr, best_ba = 1e9, t_refs[0], base_amps[0]
        for tr in t_refs:
            for ba in base_amps:
                node = PhaseGateNode("t", period, ara, rung, ba, "engine")
                node.set_t_ref(tr)
                node.phase_weight = phase_weight
                errs = []
                for k in range(len(tr_times)):
                    node.prev_amp = tr_peaks[k-1] if k > 0 else None
                    if k > 0:
                        node.recent_amps = list(tr_peaks[max(0,k-10):k])
                    pred = node.cascade_amplitude(tr_times[k])
                    errs.append(abs(pred - tr_peaks[k]))
                mae = np.mean(errs)
                if mae < best_mae:
                    best_mae, best_tr, best_ba = mae, tr, ba

        # Predict held-out using full sequence context
        node = PhaseGateNode("loo", period, ara, rung, best_ba, "engine")
        node.set_t_ref(best_tr)
        node.phase_weight = phase_weight
        for k in range(n):
            node.prev_amp = peaks[k-1] if k > 0 else None
            if k > 0:
                node.recent_amps = list(peaks[max(0,k-10):k])
            pred = node.cascade_amplitude(times[k])
            if k == hold:
                loo_preds.append(pred)
                loo_errors.append(abs(pred - peaks[k]))

    loo_errors = np.array(loo_errors)
    loo_preds = np.array(loo_preds)
    loo_mae = np.mean(loo_errors)
    loo_corr = np.corrcoef(loo_preds, peaks)[0, 1] if len(loo_preds) > 2 else 0

    return loo_mae, loo_corr, loo_errors, loo_preds


# ================================================================
# FULL PIPELINE
# ================================================================

def run_phase_gate_vehicle(times, peaks, period, ara, target_rung,
                           phase_weight=0.0, sim_margin=None):
    if sim_margin is None:
        sim_margin = max(period * 5, times[-1] - times[0]) * 0.2

    # Grid search
    fit_tr, fit_ba, fit_mae = None, None, 1e9
    gleissberg = period * PHI**4
    data_span = times[-1] - times[0]
    tr_lo = times[0] - max(gleissberg, data_span)
    tr_hi = times[0] + 2 * period
    ba_lo = np.mean(peaks) * 0.5
    ba_hi = np.mean(peaks) * 1.5
    t_refs = np.linspace(tr_lo, tr_hi, 40)
    base_amps = np.linspace(ba_lo, ba_hi, 20)

    for tr in t_refs:
        for ba in base_amps:
            node = PhaseGateNode("t", period, ara, target_rung, ba, "engine")
            node.set_t_ref(tr)
            node.phase_weight = phase_weight
            errs = []
            for k in range(len(times)):
                node.prev_amp = peaks[k-1] if k > 0 else None
                if k > 0:
                    node.recent_amps = list(peaks[max(0,k-10):k])
                pred = node.cascade_amplitude(times[k])
                errs.append(abs(pred - peaks[k]))
            mae = np.mean(errs)
            if mae < fit_mae:
                fit_mae = mae
                fit_tr, fit_ba = tr, ba

    # Build network
    rungs = build_rung_ladder(target_rung, period)
    all_nodes = {}
    engine_nodes = {}
    for rung_power, rung_period, prefix in rungs:
        for archetype, ara_val in [("engine", PHI), ("clock", 1.0),
                                    ("consumer", INV_PHI)]:
            name = f"{prefix}_{archetype}"
            if prefix == "Target" and archetype == "engine":
                ara_val = ara
                ba = fit_ba
            else:
                ba = 1.0
            node = PhaseGateNode(name, rung_period, ara_val,
                                  rung_power, ba, archetype)
            node.set_t_ref(fit_tr)
            node.phase_weight = phase_weight
            all_nodes[name] = node
            if archetype == "engine":
                engine_nodes[prefix] = node

    rung_list = [(rp, prefix) for rp, _, prefix in rungs]
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
        return {"mae": 999, "corr": 0, "snaps": 0, "failed": True}

    errors, preds = [], []
    for i in range(len(times)):
        idx = np.argmin(np.abs(snap_t - times[i]))
        preds.append(snap_a[idx])
        errors.append(abs(snap_a[idx] - peaks[i]))

    mae = np.mean(errors)
    corr = np.corrcoef(preds, peaks)[0, 1] if len(preds) > 2 else 0
    sine_mae = np.mean(np.abs(peaks - np.mean(peaks)))

    return {
        "mae": mae, "corr": corr, "fit_mae": fit_mae,
        "snaps": target_node.local_ticks,
        "sine_mae": sine_mae, "failed": False,
    }


# ================================================================
# SOLAR DATA
# ================================================================

solar_peaks = [
    (1755.5, 86.5), (1766.0, 115.8), (1775.5, 158.5),
    (1784.5, 141.2), (1805.0, 49.2), (1816.0, 48.7),
    (1829.5, 71.7), (1837.0, 146.9), (1848.0, 131.9),
    (1860.0, 97.9), (1870.5, 140.5), (1883.5, 74.6),
    (1894.0, 87.9), (1906.0, 64.2), (1917.5, 105.4),
    (1928.5, 78.1), (1937.5, 119.2), (1947.5, 151.8),
    (1958.0, 201.3), (1968.5, 110.6), (1979.5, 164.5),
    (1989.5, 158.5), (2000.5, 120.8), (2014.0, 113.3),
    (2024.5, 144.0),
]

times_solar = np.array([p[0] for p in solar_peaks])
peaks_solar = np.array([p[1] for p in solar_peaks])
period_solar = 11.07
ara_solar = PHI
rung_solar = 0

print("=" * 78)
print("SCRIPT 236O — PHASE-AWARE GATE")
print("Champion architecture + one new knob (wave phase → gate timing)")
print("=" * 78)
print()
print("ARCHITECTURE:")
print("  Geometry:  LOCKED — distances [6,4,1,-1], three-circle, all constants")
print("  State:     inst_ara (energy) + phase_shift (cycle position)")
print("  Dynamics:  acc = 1/(1+inst_ara) + phase_weight × phase_shift")
print("  Readout:   base_amp × cascade_shape(t)")
print()
print("  At phase_weight=0, this IS the champion.")
print()


# ================================================================
# PART 1: CASCADE-LEVEL — phase_weight scan
# ================================================================

print("─" * 78)
print("PART 1: CASCADE-LEVEL — phase_weight scan")
print("─" * 78)
print()

# Geometric values for phase_weight
weights = [0.0, INV_PHI_4, INV_PHI_3, INV_PHI_2, INV_PHI, 0.5,
           PHI - 1, 1.0, PHI]
labels = ["0 (champion)", f"1/φ⁴={INV_PHI_4:.4f}", f"1/φ³={INV_PHI_3:.3f}",
          f"1/φ²={INV_PHI_2:.3f}", f"1/φ={INV_PHI:.3f}", "0.5",
          f"φ-1={PHI-1:.3f}", "1.0", f"φ={PHI:.3f}"]

print(f"{'Phase weight':<22} {'MAE':>8} {'Corr':>8}")
print("─" * 42)

cascade_results = []
for pw, label in zip(weights, labels):
    mae, corr, _, _, _, _, _ = eval_cascade(
        times_solar, peaks_solar, period_solar, ara_solar, rung_solar,
        phase_weight=pw, fast=True)
    cascade_results.append((label, pw, mae, corr))
    prev_best = min(r[2] for r in cascade_results[:-1]) if len(cascade_results) > 1 else 1e9
    marker = " ← best" if mae < prev_best else ""
    print(f"  {label:<20} {mae:>8.2f} {corr:>+8.3f}{marker}")

best_casc = min(cascade_results, key=lambda x: x[2])
print()
print(f"  Best cascade: pw={best_casc[1]:.4f}, MAE={best_casc[2]:.2f}")

# Full resolution on best
print("  Re-running best at 80×40...")
bc_mae, bc_corr, bc_preds, bc_errs, bc_shifts, _, _ = eval_cascade(
    times_solar, peaks_solar, period_solar, ara_solar, rung_solar,
    phase_weight=best_casc[1], fast=False)
print(f"  Full-res: MAE={bc_mae:.2f}, corr={bc_corr:+.3f}")

# Show phase shifts
print()
print("  Phase shifts per cycle (+ = near peak, - = near trough):")
for k in range(len(bc_shifts)):
    bar = "█" * int(abs(bc_shifts[k]) * 40)
    sign = "+" if bc_shifts[k] >= 0 else "-"
    print(f"    C{k+1:>2} ({times_solar[k]:.0f}): {sign}{abs(bc_shifts[k]):.3f} {bar}")


# ================================================================
# PART 2: LOO — champion (pw=0) vs best cascade pw
# ================================================================

print()
print("─" * 78)
print("PART 2: LOO CROSS-VALIDATION")
print("─" * 78)
print()

# Always run pw=0 (champion baseline) and best cascade pw
loo_configs = [(0.0, "0 (champion)")]
if best_casc[1] != 0.0:
    loo_configs.append((best_casc[1], best_casc[0]))

# Also test a few geometric midpoints
for pw, label in [(INV_PHI_4, f"1/φ⁴"), (INV_PHI_3, f"1/φ³"),
                   (INV_PHI_2, f"1/φ²"), (INV_PHI, f"1/φ")]:
    if pw != best_casc[1] and pw != 0.0:
        loo_configs.append((pw, label))

# Keep top 5 to limit runtime
loo_configs = loo_configs[:5]

sine_mae = np.mean(np.abs(peaks_solar - np.mean(peaks_solar)))

print(f"{'Config':<22} {'LOO MAE':>10} {'LOO Corr':>10} {'vs Sine':>10}")
print("─" * 56)

loo_results = []
for pw, label in loo_configs:
    loo_mae, loo_corr, loo_errs, loo_preds = run_loo(
        times_solar, peaks_solar, period_solar, ara_solar, rung_solar,
        phase_weight=pw)
    loo_results.append((label, pw, loo_mae, loo_corr))
    vs_sine = (1 - loo_mae / sine_mae) * 100
    marker = ""
    if loo_mae < 31.94:
        marker = " ★ NEW LOO CHAMPION"
    elif len(loo_results) > 1 and loo_mae < min(r[2] for r in loo_results[:-1]):
        marker = " ← best"
    print(f"  {label:<20} {loo_mae:>10.2f} {loo_corr:>+10.3f} "
          f"{vs_sine:>+9.1f}%{marker}")

best_loo = min(loo_results, key=lambda x: x[2])
print()
print(f"  Best LOO: pw={best_loo[1]:.4f}, MAE={best_loo[2]:.2f}")
print(f"  226 v4 champion LOO: 31.94")
print(f"  Difference: {31.94 - best_loo[2]:+.2f} SSN")


# ================================================================
# PART 3: FULL PIPELINE — best LOO config
# ================================================================

print()
print("─" * 78)
print("PART 3: FULL PIPELINE")
print("─" * 78)
print()

pipe_configs = [(0.0, "0 (champion)"), (best_loo[1], best_loo[0])]
if best_casc[1] != best_loo[1] and best_casc[1] != 0.0:
    pipe_configs.append((best_casc[1], best_casc[0]))

print(f"{'Config':<22} {'Pipe MAE':>10} {'Corr':>8} {'Snaps':>6}")
print("─" * 50)

for pw, label in pipe_configs:
    result = run_phase_gate_vehicle(
        times_solar, peaks_solar, period_solar, ara_solar, rung_solar,
        phase_weight=pw)
    failed = " FAILED" if result.get("failed") else ""
    print(f"  {label:<20} {result['mae']:>10.2f} {result['corr']:>+8.3f} "
          f"{result.get('snaps', 0):>6}{failed}")


# ================================================================
# SUMMARY
# ================================================================

print()
print("─" * 78)
print("SUMMARY")
print("─" * 78)
print()
print(f"  226 v4 champion LOO:     MAE 31.94")
print(f"  236O best LOO:           MAE {best_loo[2]:.2f} (pw={best_loo[1]:.4f})")
print(f"  236N meta-triangle LOO:  MAE 37.17")
print(f"  Sine baseline:           MAE {sine_mae:.2f}")
print()
print(f"  236i cascade best:       MAE 28.11")
print(f"  236N cascade best:       MAE 22.82")
print(f"  236O cascade best:       MAE {best_casc[2]:.2f}")
print()
print(f"  234t full pipeline:      MAE 28.71")

elapsed = clock_time.time() - t_start
print()
print(f"Total time: {elapsed:.1f}s")
print("=" * 78)
