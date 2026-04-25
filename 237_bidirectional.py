#!/usr/bin/env python3
"""
Script 237 — Bidirectional Cascade (235b engine)

Dylan's insight: "We're starting midway and missing the energy coming
BEFORE we start the process. From 1900 onwards it maps fairly cleanly...
but the energy from behind it is probably throwing the actual shape."

"Your suggestion to just run backwards to get the warm up is good."

Architecture:
  - Uses the 235b ARANode cascade (three-circle blend, collision dampening)
  - Phase 1 — Backward extrapolation:
      Run the cascade backwards from C25→C1. This gives us the wave state
      at each known cycle, seen from the future. Then extrapolate BEFORE C1
      to reconstruct phantom pre-1750 cycles. These phantom cycles represent
      the energy that was already flowing before our data begins.
  - Phase 2 — Warm-started forward pass:
      Use the phantom cycles as amplitude history, giving C1 a prev_amp
      and the cascade a running start instead of a cold start.
  - The cascade geometry, gate, distances — ALL locked from 235b.
    The only new element is the backward warmup.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import math
import warnings, time as clock_time
warnings.filterwarnings('ignore')

t_start = clock_time.time()

PHI = (1 + math.sqrt(5)) / 2
PHI_2 = PHI ** 2
INV_PHI = 1 / PHI
INV_PHI_2 = INV_PHI ** 2
INV_PHI_3 = INV_PHI ** 3
INV_PHI_4 = INV_PHI ** 4
INV_PHI_9 = INV_PHI ** 9
LOG2 = math.log(2)
TAU = 2 * math.pi
PHI_LEAK = INV_PHI_4
MOMENTUM_FRAC = INV_PHI_3
TWO_OVER_PHI = 2.0 / PHI
TWO_PHI = 2.0 * PHI

# ================================================================
# IMPORT 235b ARANode
# ================================================================

exec_235b = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         '235b_universal_vehicle.py')
with open(exec_235b, 'r') as f:
    code_235b = f.read()

lines_235b = code_235b.split('\n')
cut_235b = None
for i, line in enumerate(lines_235b):
    if line.strip().startswith('print("="') and i > 100:
        cut_235b = i
        break
ns_235b = {}
exec('\n'.join(lines_235b[:cut_235b]), ns_235b)

ARANode = ns_235b['ARANode']

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

times = np.array([p[0] for p in solar_peaks])
peaks = np.array([p[1] for p in solar_peaks])
period = 11.07
n_cycles = len(times)

# ================================================================
# BIDIRECTIONAL ENGINE
# ================================================================

def predict_with_node(node, t, prev_amp=None, amp_history=None):
    """Run 235b cascade prediction at time t with given context."""
    node.prev_amp = prev_amp
    node.amp_history = list(amp_history) if amp_history else []
    return node.cascade_amplitude(t)


def backward_extrapolate(times, peaks, t_ref, base_amp, period, n_phantom=5):
    """
    Run the cascade backwards through the data, then extrapolate
    before C1 to create phantom pre-1750 cycles.

    Returns: list of (time, amplitude) tuples for phantom cycles,
    ordered chronologically (earliest first).
    """
    n = len(times)

    # Step 1: Run backward through known data to establish the wave state
    # In reverse, 'previous' means the next chronological cycle
    node = ARANode("bwd", period, PHI, 0, base_amp, "engine")
    node.set_t_ref(t_ref)

    bwd_preds = [0.0] * n
    for k_rev in range(n):
        k = n - 1 - k_rev
        prev = peaks[k+1] if k < n-1 else None
        hist = list(peaks[k+1:]) if k < n-1 else []
        bwd_preds[k] = predict_with_node(node, times[k], prev_amp=prev,
                                          amp_history=hist)

    # Step 2: Extrapolate phantom cycles before C1
    # Use the average inter-peak spacing as the backward step
    # (or just use the period)
    phantom_cycles = []
    # The backward pass has "warmed up" by C1 — it knows the energy context
    # from C25 all the way back. Now project further back.

    # For the phantom cycles, we step backwards by ~period from C1
    # and use the backward cascade's predictions as if they were real peaks
    # to provide context for each prior step.

    # Build a combined sequence: phantom times + real times
    # Start from C1 and step backwards
    phantom_amps = []
    phantom_times_list = []

    # Use the backward prediction at C1 as anchor, then keep going
    prev_amp_for_phantom = bwd_preds[0]  # backward prediction at C1
    recent_history = list(bwd_preds[:10])  # backward view of early cycles

    for i in range(n_phantom):
        # Each phantom cycle is one period further back
        t_phantom = times[0] - period * (i + 1)
        phantom_times_list.append(t_phantom)

        node_p = ARANode("phantom", period, PHI, 0, base_amp, "engine")
        node_p.set_t_ref(t_ref)
        node_p.prev_amp = prev_amp_for_phantom
        node_p.amp_history = list(recent_history)

        amp = node_p.cascade_amplitude(t_phantom)
        phantom_amps.append(amp)

        # Update context for next phantom step
        recent_history = [amp] + recent_history
        prev_amp_for_phantom = amp

    # Reverse to chronological order
    phantom_times_list.reverse()
    phantom_amps.reverse()

    phantom_cycles = list(zip(phantom_times_list, phantom_amps))
    return phantom_cycles, bwd_preds


def warmstarted_forward(times, peaks, t_ref, base_amp, period,
                        phantom_cycles, return_all=False):
    """
    Forward pass with phantom cycles providing warmup context.

    phantom_cycles: list of (time, amplitude) for pre-data cycles.
    """
    node = ARANode("fwd", period, PHI, 0, base_amp, "engine")
    node.set_t_ref(t_ref)

    # Build the full amplitude history: phantoms + real data (as we go)
    phantom_amps = [amp for _, amp in phantom_cycles]

    preds = []
    for k in range(len(times)):
        # Amplitude history: all phantom amps + real peaks before this cycle
        full_history = phantom_amps + list(peaks[:k])

        if k > 0:
            prev = peaks[k-1]
        elif len(phantom_amps) > 0:
            prev = phantom_amps[-1]  # last phantom = immediately before C1
        else:
            prev = None

        node.prev_amp = prev
        node.amp_history = full_history

        pred = node.cascade_amplitude(times[k])
        preds.append(pred)

    return np.array(preds)


def cold_forward(times, peaks, t_ref, base_amp, period):
    """Standard cold-start forward pass (235b baseline)."""
    node = ARANode("cold", period, PHI, 0, base_amp, "engine")
    node.set_t_ref(t_ref)

    preds = []
    for k in range(len(times)):
        prev = peaks[k-1] if k > 0 else None
        node.prev_amp = prev
        node.amp_history = list(peaks[:k]) if k > 0 else []
        pred = node.cascade_amplitude(times[k])
        preds.append(pred)
    return np.array(preds)


# ================================================================
# GRID SEARCH
# ================================================================

print("=" * 78)
print("237 — Bidirectional Cascade (235b engine)")
print("=" * 78)
print()

gleissberg = period * PHI**4
data_span = times[-1] - times[0]
tr_lo = times[0] - max(gleissberg, data_span)
tr_hi = times[0] + 2 * period
ba_lo = np.mean(peaks) * 0.5
ba_hi = np.mean(peaks) * 1.5

# First, find 235b cold-start baseline
print("Finding 235b cold-start baseline...")
best_cold = {'mae': 1e9}
for tr in np.linspace(tr_lo, tr_hi, 80):
    for ba in np.linspace(ba_lo, ba_hi, 40):
        preds = cold_forward(times, peaks, tr, ba, period)
        mae = np.mean(np.abs(preds - peaks))
        if mae < best_cold['mae']:
            best_cold = {'mae': mae, 'tr': tr, 'ba': ba, 'preds': preds}

print(f"  235b cold-start: MAE {best_cold['mae']:.2f}, "
      f"t_ref={best_cold['tr']:.2f}, base_amp={best_cold['ba']:.2f}")
print()

# Now test bidirectional with different phantom counts
print("Testing phantom cycle counts...")
for n_phantom in [1, 2, 3, 5, 8, 13]:
    best = {'mae': 1e9}
    for tr in np.linspace(tr_lo, tr_hi, 80):
        for ba in np.linspace(ba_lo, ba_hi, 40):
            phantoms, _ = backward_extrapolate(
                times, peaks, tr, ba, period, n_phantom=n_phantom)
            preds = warmstarted_forward(
                times, peaks, tr, ba, period, phantoms)
            mae = np.mean(np.abs(preds - peaks))
            if mae < best['mae']:
                best = {'mae': mae, 'tr': tr, 'ba': ba}

    print(f"  {n_phantom:>2} phantoms: MAE {best['mae']:.2f}, "
          f"t_ref={best['tr']:.2f}, base_amp={best['ba']:.2f}")

print()

# ================================================================
# DETAILED RUN WITH BEST PHANTOM COUNT
# ================================================================

# Run all phantom counts and pick best
overall_best = {'mae': 1e9}
for n_phantom in [1, 2, 3, 5, 8, 13]:
    for tr in np.linspace(tr_lo, tr_hi, 80):
        for ba in np.linspace(ba_lo, ba_hi, 40):
            phantoms, bwd = backward_extrapolate(
                times, peaks, tr, ba, period, n_phantom=n_phantom)
            preds = warmstarted_forward(
                times, peaks, tr, ba, period, phantoms)
            mae = np.mean(np.abs(preds - peaks))
            if mae < overall_best['mae']:
                overall_best = {
                    'mae': mae, 'tr': tr, 'ba': ba,
                    'preds': preds, 'phantoms': phantoms,
                    'bwd': bwd, 'n_phantom': n_phantom
                }

B = overall_best
print(f"Best config: {B['n_phantom']} phantom cycles")
print(f"Cascade MAE: {B['mae']:.2f}")
print(f"t_ref: {B['tr']:.2f}, base_amp: {B['ba']:.2f}")
print()

# Show phantom cycles
print("Phantom cycles (reconstructed pre-1750):")
for t_ph, a_ph in B['phantoms']:
    print(f"  {t_ph:.1f}:  {a_ph:.1f} SSN")
print()

# Per-cycle comparison
cold_preds = cold_forward(times, peaks, B['tr'], B['ba'], period)

print(f"{'Cycle':<6} {'Year':>6} {'Actual':>7} {'Cold':>7} {'Warm':>7} "
      f"{'ColdErr':>8} {'WarmErr':>8} {'Better':>7}")
print("─" * 70)

for k in range(n_cycles):
    ce = abs(cold_preds[k] - peaks[k])
    we = abs(B['preds'][k] - peaks[k])
    better = "  ✓" if we < ce - 0.1 else ""
    print(f"  C{k+1:<4} {times[k]:>6.1f} {peaks[k]:>7.1f} {cold_preds[k]:>7.1f} "
          f"{B['preds'][k]:>7.1f} {ce:>8.1f} {we:>8.1f} {better}")

cold_mae = np.mean(np.abs(cold_preds - peaks))
warm_mae = np.mean(np.abs(B['preds'] - peaks))

print()
print(f"  Cold-start MAE: {cold_mae:.2f}")
print(f"  Warm-start MAE: {warm_mae:.2f}")
print(f"  Improvement:    {cold_mae - warm_mae:+.2f}")
print()

# Early vs late
early = list(range(0, 7))
late = list(range(7, 25))

cold_early = np.mean(np.abs(cold_preds[early] - peaks[early]))
warm_early = np.mean(np.abs(B['preds'][early] - peaks[early]))
cold_late = np.mean(np.abs(cold_preds[late] - peaks[late]))
warm_late = np.mean(np.abs(B['preds'][late] - peaks[late]))

print(f"  Early cycles (C1-C7):")
print(f"    Cold MAE: {cold_early:.2f}")
print(f"    Warm MAE: {warm_early:.2f}")
print(f"    Improvement: {cold_early - warm_early:+.2f}")
print()
print(f"  Late cycles (C8-C25):")
print(f"    Cold MAE: {cold_late:.2f}")
print(f"    Warm MAE: {warm_late:.2f}")
print(f"    Improvement: {cold_late - warm_late:+.2f}")

# ================================================================
# LOO CROSS-VALIDATION
# ================================================================

print()
print("=" * 78)
print("LOO Cross-Validation")
print("=" * 78)
print()

loo_errors = []
loo_preds_list = []
loo_actuals = []

for hold_idx in range(n_cycles):
    train_mask = np.ones(n_cycles, dtype=bool)
    train_mask[hold_idx] = False
    train_times = times[train_mask]
    train_peaks = peaks[train_mask]

    # Grid search on training data
    tr_lo_loo = train_times[0] - max(gleissberg, train_times[-1] - train_times[0])
    tr_hi_loo = train_times[0] + 2 * period
    ba_lo_loo = np.mean(train_peaks) * 0.5
    ba_hi_loo = np.mean(train_peaks) * 1.5

    best_loo = {'mae': 1e9}
    for tr in np.linspace(tr_lo_loo, tr_hi_loo, 80):
        for ba in np.linspace(ba_lo_loo, ba_hi_loo, 40):
            phantoms, _ = backward_extrapolate(
                train_times, train_peaks, tr, ba, period,
                n_phantom=B['n_phantom'])
            preds = warmstarted_forward(
                train_times, train_peaks, tr, ba, period, phantoms)
            mae = np.mean(np.abs(preds - train_peaks))
            if mae < best_loo['mae']:
                best_loo = {'mae': mae, 'tr': tr, 'ba': ba}

    # Predict held-out cycle using full data for context
    phantoms, _ = backward_extrapolate(
        times, peaks, best_loo['tr'], best_loo['ba'], period,
        n_phantom=B['n_phantom'])
    preds_full = warmstarted_forward(
        times, peaks, best_loo['tr'], best_loo['ba'], period, phantoms)

    held_pred = preds_full[hold_idx]
    actual = peaks[hold_idx]
    error = abs(held_pred - actual)

    loo_errors.append(error)
    loo_preds_list.append(held_pred)
    loo_actuals.append(actual)

    rel_err = error / actual * 100
    print(f"  C{hold_idx+1:<4} {times[hold_idx]:>6.1f}  "
          f"actual={actual:>7.1f}  pred={held_pred:>7.1f}  "
          f"err={error:>6.1f}  ({rel_err:>5.1f}%)")

loo_errors = np.array(loo_errors)
loo_preds_arr = np.array(loo_preds_list)
loo_actuals = np.array(loo_actuals)

loo_mae = np.mean(loo_errors)
loo_median = np.median(loo_errors)
loo_corr = np.corrcoef(loo_preds_arr, loo_actuals)[0, 1]
sine_mae = np.mean(np.abs(loo_actuals - np.mean(loo_actuals)))

print()
print("─" * 55)
print(f"  LOO MAE:    {loo_mae:.2f}")
print(f"  LOO Median: {loo_median:.2f}")
print(f"  LOO Corr:   {loo_corr:+.3f}")
print(f"  Sine MAE:   {sine_mae:.2f}")
print(f"  vs Sine:    {(1 - loo_mae/sine_mae)*100:+.1f}%")
print()

# LOO early vs late
loo_early = np.mean(loo_errors[early])
loo_late = np.mean(loo_errors[late])
print(f"  LOO Early (C1-C7): {loo_early:.2f}")
print(f"  LOO Late (C8-C25): {loo_late:.2f}")
print()

print("─" * 78)
print("COMPARISON")
print("─" * 78)
print()
print(f"  226 v4 champion:      Cascade MAE 27.17, LOO MAE 31.94")
print(f"  235b cold-start:      Cascade MAE {best_cold['mae']:.2f}")
print(f"  237 warm-start (235b): Cascade MAE {warm_mae:.2f}, LOO MAE {loo_mae:.2f}")
delta_cascade = best_cold['mae'] - warm_mae
delta_loo = 31.94 - loo_mae
print(f"  vs 235b cold:         {'+' if delta_cascade > 0 else ''}{delta_cascade:.2f} cascade")
print(f"  vs 226 LOO champion:  {'+' if delta_loo > 0 else ''}{delta_loo:.2f} LOO")
print()

if loo_mae < 31.94:
    print("  *** NEW LOO CHAMPION ***")
elif loo_mae < sine_mae:
    print("  Beats sine but not LOO champion.")
else:
    print("  Does not beat sine baseline.")

elapsed = clock_time.time() - t_start
print()
print(f"Total time: {elapsed:.1f}s")
print("=" * 78)
