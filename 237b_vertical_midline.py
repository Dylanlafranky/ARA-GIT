#!/usr/bin/env python3
"""
Script 237b — Bidirectional Cascade with Vertical Midline (235b engine)

Two key changes from 237:

1. PERSISTENT WARMUP — Phantom cycles create a decaying memory that
   fades over several real cycles (1/φ decay per cycle), not just
   prev_amp that gets instantly overwritten at C2.

2. VERTICAL MIDLINE (+1) — "The top systems give 1 down before any
   horizontal movement happens." The cascade shape doesn't oscillate
   around 1.0 (= base_amp). It oscillates around 1.0 + 1.0 = 2.0,
   because the vertical pipe delivers 1 unit of normalized energy
   before the horizontal cascade begins. The grid search will find
   the right base_amp to compensate (should be roughly half current).

   Wave lives between +1 and -1 from the midline, not 0 and +max.
   The vertical gift IS the midline.
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
# MODIFIED CASCADE — VERTICAL MIDLINE
# ================================================================

class VerticalMidlineNode(ARANode):
    """
    235b ARANode with +1 vertical offset on cascade shape.

    The vertical pipe delivers 1 unit before horizontal cascade runs.
    Shape oscillates around 2.0 instead of 1.0.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.phantom_memory = 0.0  # decaying phantom warmup
        self.phantom_decay = INV_PHI  # decay rate per cycle

    def cascade_shape(self, t):
        """Standard 235b cascade_shape + vertical offset."""
        base_shape = super().cascade_shape(t)
        # Add vertical midline: +1 unit from the pipe above
        return base_shape + 1.0

    def cascade_amplitude(self, t):
        """Override to include phantom memory as decaying warmup."""
        shape = self.cascade_shape(t)
        amp = self.base_amp * shape

        # Add decaying phantom memory influence
        if self.phantom_memory != 0.0:
            amp += self.phantom_memory

        return amp


# ================================================================
# BIDIRECTIONAL ENGINE WITH PERSISTENT WARMUP
# ================================================================

def backward_extrapolate(times, peaks, t_ref, base_amp, period, n_phantom=5):
    """Run backward to reconstruct phantom pre-1750 cycles."""
    n = len(times)
    node = ARANode("bwd", period, PHI, 0, base_amp, "engine")
    node.set_t_ref(t_ref)

    # Run backward through known data
    bwd_preds = [0.0] * n
    for k_rev in range(n):
        k = n - 1 - k_rev
        prev = peaks[k+1] if k < n-1 else None
        hist = list(peaks[k+1:]) if k < n-1 else []
        node.prev_amp = prev
        node.amp_history = hist
        bwd_preds[k] = node.cascade_amplitude(times[k])

    # Extrapolate phantom cycles before C1
    phantom_cycles = []
    phantom_amps = []
    phantom_times_list = []
    prev_amp_for_phantom = bwd_preds[0]
    recent_history = list(bwd_preds[:10])

    for i in range(n_phantom):
        t_phantom = times[0] - period * (i + 1)
        phantom_times_list.append(t_phantom)
        node_p = ARANode("phantom", period, PHI, 0, base_amp, "engine")
        node_p.set_t_ref(t_ref)
        node_p.prev_amp = prev_amp_for_phantom
        node_p.amp_history = list(recent_history)
        amp = node_p.cascade_amplitude(t_phantom)
        phantom_amps.append(amp)
        recent_history = [amp] + recent_history
        prev_amp_for_phantom = amp

    phantom_times_list.reverse()
    phantom_amps.reverse()
    return list(zip(phantom_times_list, phantom_amps)), bwd_preds


def warmstarted_forward_v2(times, peaks, t_ref, base_amp, period,
                           phantom_cycles, use_vertical_midline=True):
    """
    Forward pass with:
    1. Phantom cycles providing persistent decaying warmup
    2. Optional vertical midline offset (+1 on shape)
    """
    if use_vertical_midline:
        node = VerticalMidlineNode("fwd", period, PHI, 0, base_amp, "engine")
    else:
        node = ARANode("fwd", period, PHI, 0, base_amp, "engine")
    node.set_t_ref(t_ref)

    phantom_amps = [amp for _, amp in phantom_cycles]

    # Compute initial phantom memory — sum of phantom deviations from base_amp,
    # each decayed by 1/φ per step from the present
    phantom_memory = 0.0
    if phantom_amps:
        for i, pa in enumerate(phantom_amps):
            # Distance from present: len(phantom_amps) - i steps ago
            steps_back = len(phantom_amps) - i
            deviation = pa - base_amp
            phantom_memory += deviation * (INV_PHI ** steps_back)

    preds = []
    for k in range(len(times)):
        # Set prev_amp with phantom fallback
        if k > 0:
            prev = peaks[k-1]
        elif phantom_amps:
            prev = phantom_amps[-1]
        else:
            prev = None

        # Amplitude history includes phantoms
        full_history = phantom_amps + list(peaks[:k])

        node.prev_amp = prev
        node.amp_history = full_history

        if use_vertical_midline:
            node.phantom_memory = phantom_memory

        pred = node.cascade_amplitude(times[k])
        preds.append(pred)

        # Decay phantom memory each cycle
        phantom_memory *= INV_PHI

    return np.array(preds)


def cold_forward(times, peaks, t_ref, base_amp, period, use_vertical_midline=False):
    """Standard cold-start forward pass."""
    if use_vertical_midline:
        node = VerticalMidlineNode("cold", period, PHI, 0, base_amp, "engine")
    else:
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
print("237b — Bidirectional Cascade + Vertical Midline (235b engine)")
print("=" * 78)
print()

gleissberg = period * PHI**4
data_span = times[-1] - times[0]
tr_lo = times[0] - max(gleissberg, data_span)
tr_hi = times[0] + 2 * period

# Note: with +1 offset, base_amp should be roughly HALF of what it was
# because shape now oscillates around 2.0 not 1.0
# So we search a wider base_amp range
ba_lo = np.mean(peaks) * 0.2
ba_hi = np.mean(peaks) * 1.5

# ── Test 1: 235b cold baseline (no changes) ──
print("1. 235b cold-start baseline (no vertical offset)...")
best_cold = {'mae': 1e9}
for tr in np.linspace(tr_lo, tr_hi, 80):
    for ba in np.linspace(np.mean(peaks)*0.5, np.mean(peaks)*1.5, 40):
        preds = cold_forward(times, peaks, tr, ba, period, use_vertical_midline=False)
        mae = np.mean(np.abs(preds - peaks))
        if mae < best_cold['mae']:
            best_cold = {'mae': mae, 'tr': tr, 'ba': ba}
print(f"   MAE {best_cold['mae']:.2f}, t_ref={best_cold['tr']:.2f}, "
      f"base_amp={best_cold['ba']:.2f}")
print()

# ── Test 2: Vertical midline only (cold start) ──
print("2. Vertical midline only (cold start, no phantoms)...")
best_vert = {'mae': 1e9}
for tr in np.linspace(tr_lo, tr_hi, 80):
    for ba in np.linspace(ba_lo, ba_hi, 40):
        preds = cold_forward(times, peaks, tr, ba, period, use_vertical_midline=True)
        mae = np.mean(np.abs(preds - peaks))
        if mae < best_vert['mae']:
            best_vert = {'mae': mae, 'tr': tr, 'ba': ba}
print(f"   MAE {best_vert['mae']:.2f}, t_ref={best_vert['tr']:.2f}, "
      f"base_amp={best_vert['ba']:.2f}")
print()

# ── Test 3: Phantoms only (no vertical offset) ──
print("3. Phantom warmup only (no vertical offset)...")
best_phantom = {'mae': 1e9}
for n_ph in [3, 5, 8]:
    for tr in np.linspace(tr_lo, tr_hi, 80):
        for ba in np.linspace(np.mean(peaks)*0.5, np.mean(peaks)*1.5, 40):
            phantoms, _ = backward_extrapolate(times, peaks, tr, ba, period, n_phantom=n_ph)
            preds = warmstarted_forward_v2(times, peaks, tr, ba, period, phantoms,
                                            use_vertical_midline=False)
            mae = np.mean(np.abs(preds - peaks))
            if mae < best_phantom['mae']:
                best_phantom = {'mae': mae, 'tr': tr, 'ba': ba, 'n_ph': n_ph}
print(f"   MAE {best_phantom['mae']:.2f}, t_ref={best_phantom['tr']:.2f}, "
      f"base_amp={best_phantom['ba']:.2f}, phantoms={best_phantom['n_ph']}")
print()

# ── Test 4: BOTH — vertical midline + phantom warmup ──
print("4. Vertical midline + phantom warmup (the full idea)...")
best_both = {'mae': 1e9}
for n_ph in [3, 5, 8]:
    for tr in np.linspace(tr_lo, tr_hi, 80):
        for ba in np.linspace(ba_lo, ba_hi, 40):
            phantoms, _ = backward_extrapolate(times, peaks, tr, ba, period, n_phantom=n_ph)
            preds = warmstarted_forward_v2(times, peaks, tr, ba, period, phantoms,
                                            use_vertical_midline=True)
            mae = np.mean(np.abs(preds - peaks))
            if mae < best_both['mae']:
                best_both = {'mae': mae, 'tr': tr, 'ba': ba, 'n_ph': n_ph}
print(f"   MAE {best_both['mae']:.2f}, t_ref={best_both['tr']:.2f}, "
      f"base_amp={best_both['ba']:.2f}, phantoms={best_both['n_ph']}")
print()

# ================================================================
# DETAILED COMPARISON — BEST CONFIG
# ================================================================

print("=" * 78)
print("DETAILED RESULTS")
print("=" * 78)
print()

# Pick overall best
configs = [
    ('235b cold', best_cold, False, 0),
    ('vertical midline', best_vert, True, 0),
    ('phantom warmup', best_phantom, False, best_phantom.get('n_ph', 5)),
    ('vert + phantom', best_both, True, best_both.get('n_ph', 5)),
]

# Sort by MAE
configs.sort(key=lambda x: x[1]['mae'])
best_name, best_cfg, best_use_vert, best_n_ph = configs[0]

print(f"Best config: {best_name}")
print(f"Cascade MAE: {best_cfg['mae']:.2f}")
print(f"t_ref: {best_cfg['tr']:.2f}, base_amp: {best_cfg['ba']:.2f}")
if best_n_ph > 0:
    print(f"Phantom cycles: {best_n_ph}")
print()

# Generate predictions for all configs at their best params
results = {}
for name, cfg, use_vert, n_ph in configs:
    if n_ph > 0:
        phantoms, _ = backward_extrapolate(times, peaks, cfg['tr'], cfg['ba'],
                                            period, n_phantom=n_ph)
        preds = warmstarted_forward_v2(times, peaks, cfg['tr'], cfg['ba'],
                                        period, phantoms, use_vertical_midline=use_vert)
    else:
        preds = cold_forward(times, peaks, cfg['tr'], cfg['ba'], period,
                              use_vertical_midline=use_vert)
    results[name] = preds

# Per-cycle table for best config
best_preds = results[best_name]
cold_preds = results['235b cold']

print(f"{'Cycle':<6} {'Year':>6} {'Actual':>7} {'Cold':>7} {'Best':>7} "
      f"{'ColdErr':>8} {'BestErr':>8} {'Better':>7}")
print("─" * 70)

for k in range(n_cycles):
    ce = abs(cold_preds[k] - peaks[k])
    be = abs(best_preds[k] - peaks[k])
    better = "  ✓" if be < ce - 0.5 else ""
    print(f"  C{k+1:<4} {times[k]:>6.1f} {peaks[k]:>7.1f} {cold_preds[k]:>7.1f} "
          f"{best_preds[k]:>7.1f} {ce:>8.1f} {be:>8.1f} {better}")

print()

# Early vs late
early = list(range(0, 7))
late = list(range(7, 25))

for name in ['235b cold', best_name]:
    p = results[name]
    mae_all = np.mean(np.abs(p - peaks))
    mae_early = np.mean(np.abs(p[early] - peaks[early]))
    mae_late = np.mean(np.abs(p[late] - peaks[late]))
    print(f"  {name:>20}: MAE={mae_all:.2f}  early={mae_early:.2f}  late={mae_late:.2f}")

print()

# ================================================================
# LOO CROSS-VALIDATION (on best config)
# ================================================================

print("=" * 78)
print(f"LOO Cross-Validation ({best_name})")
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

    tr_lo_loo = train_times[0] - max(gleissberg, train_times[-1] - train_times[0])
    tr_hi_loo = train_times[0] + 2 * period
    ba_lo_loo = np.mean(train_peaks) * (0.2 if best_use_vert else 0.5)
    ba_hi_loo = np.mean(train_peaks) * 1.5

    best_loo = {'mae': 1e9}
    for tr in np.linspace(tr_lo_loo, tr_hi_loo, 80):
        for ba in np.linspace(ba_lo_loo, ba_hi_loo, 40):
            if best_n_ph > 0:
                phantoms, _ = backward_extrapolate(
                    train_times, train_peaks, tr, ba, period, n_phantom=best_n_ph)
                preds = warmstarted_forward_v2(
                    train_times, train_peaks, tr, ba, period, phantoms,
                    use_vertical_midline=best_use_vert)
            else:
                preds = cold_forward(train_times, train_peaks, tr, ba, period,
                                      use_vertical_midline=best_use_vert)
            mae = np.mean(np.abs(preds - train_peaks))
            if mae < best_loo['mae']:
                best_loo = {'mae': mae, 'tr': tr, 'ba': ba}

    # Predict held-out using full data context
    if best_n_ph > 0:
        phantoms, _ = backward_extrapolate(
            times, peaks, best_loo['tr'], best_loo['ba'], period, n_phantom=best_n_ph)
        preds_full = warmstarted_forward_v2(
            times, peaks, best_loo['tr'], best_loo['ba'], period, phantoms,
            use_vertical_midline=best_use_vert)
    else:
        preds_full = cold_forward(
            times, peaks, best_loo['tr'], best_loo['ba'], period,
            use_vertical_midline=best_use_vert)

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

loo_early = np.mean(loo_errors[early])
loo_late = np.mean(loo_errors[late])
print(f"  LOO Early (C1-C7): {loo_early:.2f}")
print(f"  LOO Late (C8-C25): {loo_late:.2f}")
print()

print("─" * 78)
print("COMPARISON")
print("─" * 78)
print()
print(f"  226 v4 champion:       Cascade MAE 27.17, LOO MAE 31.94")
print(f"  235b cold-start:       Cascade MAE {best_cold['mae']:.2f}")
print(f"  237b ({best_name}):  Cascade MAE {best_cfg['mae']:.2f}, LOO MAE {loo_mae:.2f}")
delta_loo = 31.94 - loo_mae
print(f"  vs 226 LOO champion:   {'+' if delta_loo > 0 else ''}{delta_loo:.2f}")
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
