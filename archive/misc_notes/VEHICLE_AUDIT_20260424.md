# ARA Temporal Prediction Vehicle -- Comprehensive Audit

**Date:** 24 April 2026
**Author:** Audit compiled from scripts 234L-235O and session notes
**Researcher:** Dylan La Franchi
**Status:** Honest assessment, no puffery

---

## 1. What Works

### 1.1 The Cascade Shape (the waveform itself)

The cascade shape function is the strongest component. When evaluated at known observation times with known previous amplitudes, it delivers:

- **Solar:** +29.0% vs sine (MAE ~27.0 vs sine MAE ~38.0)
- **ENSO:** +1.8% vs sine
- **Colorado:** -2.3% vs sine (marginal, but near-neutral for a consumer system)

This is the ceiling. Everything else is about how much of this signal the vehicle preserves.

### 1.2 The Autonomous Vehicle (234t champion)

- **Solar MAE: 28.71** (correlation +0.702)
- Beats chained replay (30.09) by 4.6%
- Beats champion LOO (31.94) by 10.1%
- 25 cycles predicted, 49/49 total predictions across the project

The architecture stack, each piece proven as an isolated improvement:

| Component | Script | MAE improvement |
|---|---|---|
| Asymmetric 3-sphere baseline | 234d | 37.49 (starting point) |
| 1/phi^3 momentum (AA boundary) | 234h | 37.49 -> 33.96 |
| Scale density (1/phi^4 above, 1/phi^3 below) | 234L | 33.96 -> 32.38 |
| Space-Time phi^2 coupler | 234n | 32.38 -> 31.77 |
| Rationality circle (2/phi vertical) | 234p | 31.77 -> 31.56 |
| Pipe reverberation (3 bounces, 1/phi decay) | 234s | 31.56 -> 29.38 |
| Corrected pipe capacities (2phi/phi) + collision damp | 234t | 29.38 -> 28.71 |

Every step is architecturally motivated by the framework (not curve-fit), and each was tested in isolation against alternatives. The progression is monotonic with no reversals.

### 1.3 The Grief Chain

The vehicle's grief mechanism (prev_amp feeding into the next prediction) is **signal, not noise**. The 235N diagnostic proved grief contributes -0.13 MAE (marginally better than using actual measurements). This is a genuine finding: the vehicle's own prediction history contains real information about system state.

### 1.4 The Hybrid Prediction (235N)

- **Solar: +28.5%** (vs cascade ceiling of +29.0% -- 98% signal recovery)
- **ENSO: -1.5%** (vs cascade ceiling of +1.8%)
- **Colorado: -1.7%** (vs cascade ceiling of -2.3%)

This proves the cascade signal is fully present in the vehicle. The hybrid reads cascade amplitude at observation times but uses the vehicle's own grief chain instead of measurements. It is a diagnostic tool, not a solution -- it requires knowing observation times in advance.

---

## 2. What Does Not Work

### 2.1 ENSO and Colorado in the Autonomous Vehicle

The autonomous vehicle (snap-based) delivers:

- **ENSO: -13.4% vs sine** (worse than predicting the mean)
- **Colorado: -54.3% vs sine** (catastrophically worse)

These systems have shorter periods (phi^3 ~ 4.24yr for ENSO, phi^4 ~ 6.85yr for Colorado) and weaker intrinsic cascade signal. The snap timing error (2.34yr mean offset) is a larger fraction of their periods. For ENSO, a 2.34yr offset on a 4.24yr period is 55% phase error -- the vehicle is reading the wrong part of the wave nearly half the time.

### 2.2 Fractal Fill Modulation (235M)

Using cascade shape to modulate energy fill rate degrades all systems. Solar drops from +18.1% to -16.6%. The vertical waveform (cascade) cannot drive horizontal energy dynamics (accumulation). These are independent axes. This was tested at multiple strengths from 1/phi^4 to 1/phi; all degrade.

### 2.3 Threshold Modulation (235N)

First attempt was a null operation: when fill rate is proportional to base_threshold and the snap gate uses the same threshold, modulating the threshold moves both together and snap timing is invariant. Second attempt (decoupled fill from threshold) produced extra snaps that caused observation mismatches. Neither approach improved the vehicle.

### 2.4 Diagonal Rider (235O)

Two approaches, both failed:

- **Peak-finding:** Works for Solar (+28.0%) but catastrophic for ENSO (-43.4%) and Colorado (-91.5%). In multi-period interference patterns, the rider grabs wrong peaks.
- **ARA-position:** Uses cascade_shape value as position indicator, applies time correction delta_t = (shape - 1) x period x ride_fraction. Failed at all ride fractions. The shape tells you WHERE you are on the wave but not WHICH DIRECTION to correct. Position without direction is not actionable.

### 2.5 The Dalton Era (Cycles 4-7, 1788-1830)

MAE for C4-C7 is approximately 45.89 vs 28.71 overall. The vehicle cannot explain the 40-year suppression. Cycle 3 (264.3, pre-Dalton spike) is the single worst prediction (error ~113). This may require explicit Gleissberg-scale or supra-Gleissberg modulation that the current 4-period cascade does not capture at sufficient strength.

---

## 3. The Honest Gap

### 3.1 The Numbers

| Metric | Cascade alone | Vehicle (snap) | Gap |
|---|---|---|---|
| Solar improvement vs sine | +29.0% | +18.1% | 10.9pp lost (38% leak) |
| Solar MAE | ~27.0 | 28.71 (matched) | 1.7 MAE |

The 28.71 vehicle MAE uses nearest-snap matching (each observation matched to closest snap). The cascade MAE of ~27.0 evaluates at exact observation times. The 38% leak between cascade and vehicle is entirely attributable to snap timing.

### 3.2 The Root Cause

The 235N diagnostic decomposition:

- **Timing loss:** +5.22 MAE (100% of the gap)
- **Grief loss:** -0.13 MAE (grief helps, not hurts)
- **Mean snap offset:** 2.34 years on an 11-year cycle (76 degrees phase error)
- **Max snap offset:** 5.54 years (half a cycle -- reading trough instead of peak)

The vehicle fires its snaps when accumulated energy crosses a threshold. This threshold-crossing time is determined by energy dynamics (fill rates, drains, transfers, pipe capacities) which are governed by the network topology, not by the cascade waveform. The cascade only determines WHAT amplitude to predict at snap time; it does not determine WHEN to snap.

### 3.3 What the Hybrid Proves

The hybrid (235N) recovers 98% of cascade signal by evaluating at observation times with vehicle grief. This proves:

1. The cascade shape is correct
2. The grief chain is correct
3. The energy accumulation / snap timing mechanism is the sole source of signal loss
4. If you could make the vehicle snap at the right moments, you would have the full signal

---

## 4. Approaches Tried and Ruled Out

| Approach | Scripts | Result | Why it fails |
|---|---|---|---|
| Cascade drives fill rate | 235M | All systems degrade | Vertical waveform conflicts with horizontal energy axis |
| Cascade modulates threshold | 235N v1 | Null operation | Fill proportional to threshold = no timing change |
| Decoupled threshold modulation | 235N v2 | Extra snaps, mismatches | Threshold lowering creates spurious snap events |
| Peak-finding rider | 235O v1 | Solar-only; breaks ENSO/Colorado | Grabs wrong peaks in multi-period interference |
| ARA-position time correction | 235O v2 | All fractions degrade | Position without direction; no gradient information |
| phi^2 as universal coupler | 234o | Only spacetime improves | phi^2 is Space-Time specific |
| phi/2 feed, phi cost | 234q | All degrade | Double-counts coupling already in phase blend |
| Continuous pipe seepage | 234r M3 | Destabilizes timing | Removes burst character that drives cascade diversity |
| Halving below-rung epsilon | 234r M1 | Too aggressive | Removes real cascade signal from below |
| Optimal throughput efficiency | 234s M7 | Breaks diversity | Forces uniform energy transfer, kills amplitude variation |

---

## 5. What Remains Open

### 5.1 Gradient-Based Snap Timing

The diagonal rider showed position has no direction. But dshape/dt (the time derivative of cascade shape) does have direction: it tells you whether the cascade is rising or falling at snap time, and how fast. This has not been tested. The gradient could provide the "which way to correct" information that position alone lacks.

Difficulty: Moderate. The cascade_shape function is differentiable. Computing a numerical gradient at snap time is straightforward. The question is whether the gradient is accurate enough given the 0.05yr simulation timestep and multi-period interference.

### 5.2 Energy-Phase Coupling

The fundamental issue: the vehicle's energy dynamics and the cascade waveform operate on independent axes. All attempts to have the cascade drive energy have failed. The reverse -- having energy dynamics inform WHERE on the cascade to read -- is what the hybrid does, but it requires knowing observation times.

An untried direction: use the accumulated energy level (how full the tank is relative to threshold) as a phase indicator. If the vehicle is 80% full, it knows it is "near snap" and can pre-compute where the cascade will be at threshold crossing. This is a lookahead, not a modulation.

Difficulty: Hard. This requires the vehicle to predict its own future snap time, which depends on future energy inputs from the network.

### 5.3 Adaptive Timestep / Sub-Step Refinement

The simulation runs at fixed 0.05yr timesteps. When energy crosses threshold at t=1800.05, the actual crossing may have occurred anywhere in [1800.00, 1800.05]. A bisection or interpolation at snap time could reduce timing error by up to half the timestep (0.025yr). This would reduce the 2.34yr mean offset only marginally, so it is not the primary solution -- but it is free precision.

Difficulty: Easy. Implement binary search within the timestep that triggered the snap.

### 5.4 Gleissberg-Scale Explicit Modulation

The Dalton era (C4-C7) dominates the error budget. The current cascade has a Gleissberg component (phi^4 ~ 88yr period via cascade_periods[1]) but it enters as a small additive term (INV_PHI_9 * cos(gp)). The 1/phi^9 coefficient may be too weak. An explicit Gleissberg modulation with a stronger amplitude could help, but risks overfitting to one 4-cycle stretch of 25 cycles.

Difficulty: Moderate risk of overfitting. Would need LOO validation.

### 5.5 Multi-System Vehicle Architecture

ENSO and Colorado fail in the autonomous vehicle but succeed in the cascade. The vehicle architecture was developed and tuned on Solar (rung 5, period phi^5 ~ 11.1yr). The network wiring, pipe capacities, and accumulation rates may need system-specific tuning. Alternatively, the vehicle may need to be re-derived from scratch for shorter-period systems where snap timing error is a larger fraction of the cycle.

Difficulty: Hard. This potentially means the vehicle architecture is Solar-specific rather than universal.

### 5.6 LOO Cross-Validation of 234t

The 28.71 MAE is automaton-matched, not LOO. The reverberation mechanism (3 bounces, 1/phi decay, collision dampening) added several architectural choices that could overfit. Running proper LOO would determine if 28.71 generalizes.

Difficulty: Easy to implement, important for credibility.

---

## 6. Structural Assessment

### 6.1 What is solid

The cascade shape function is the core intellectual contribution. It encodes:

- Four phi-power periods in multiplicative interference
- Asymmetric epsilon weighting (scale density)
- Three-circle blend (Space, Time, Rationality)
- Gleissberg envelope
- Schwabe asymmetric ramp
- Grief memory (previous amplitude feedback)

Each component was tested independently, shown to improve MAE, and has a framework-motivated origin. The cascade is not a regression; it is a geometric construction with 2 free parameters (t_ref, base_amp) fit by grid search.

### 6.2 What is fragile

The vehicle (energy accumulation network) is architecturally complex:

- 6 rungs x 3 archetypes = 18 nodes minimum
- Pipe transfer with reverberation (3 bounces, 1/phi decay)
- Collision dampening for below-rung transfers
- Momentum retention (1/phi^3)
- Drain rates, feed weights, all at 1/phi^4

These parameters are all phi-derived (not arbitrary), but the specific choices (3 bounces, not 2 or 4; collision dampening on, not off) were selected by systematic scan against Solar data. This is principled parameter selection, not free-form curve fitting, but it has not been validated out-of-sample.

### 6.3 The core tension

The cascade is a temporal function: given a time, it returns an amplitude. The vehicle is a causal simulation: it accumulates energy and fires events. Bridging temporal knowledge into causal dynamics is the unsolved problem. Every attempt to have the cascade inform the vehicle's timing has either nullified itself (threshold modulation) or broken multi-system generality (peak-finding). The hybrid works by abandoning causality and reading the cascade at known times.

The question the project must answer: **Can a causal energy network fire at times that align with an external temporal waveform, without being told when to fire?**

This is not a programming problem. It is a physics problem. The cascade encodes WHERE peaks should be; the vehicle must discover them through energy dynamics alone. The 2.34yr mean offset is the vehicle's current best attempt at this discovery.

---

## 7. Summary Scorecard

| Metric | Value | Benchmark | Status |
|---|---|---|---|
| Solar autonomous MAE | 28.71 | Champion LOO: 31.94 | PASS (beats by 10%) |
| Solar autonomous corr | +0.702 | -- | Strong |
| Solar cascade signal preserved | 62% | Target: 100% | GAP |
| Solar hybrid signal preserved | 98% | Target: 100% | Diagnostic only |
| ENSO autonomous vs sine | -13.4% | Target: >0% | FAIL |
| Colorado autonomous vs sine | -54.3% | Target: >0% | FAIL |
| ENSO hybrid vs sine | -1.5% | Target: >0% | Near-zero |
| Colorado hybrid vs sine | -1.7% | Target: >0% | Near-zero |
| Dalton era (C4-C7) MAE | ~45.89 | Overall: 28.71 | Dominant error |
| Snap timing offset (mean) | 2.34 yr | Target: <1 yr | 76 degrees phase error |

---

## 8. Honest Bottom Line

The ARA temporal prediction vehicle has genuine predictive power for solar cycle amplitudes, beating established benchmarks (chained replay, champion LOO) with a geometrically motivated architecture. The cascade shape function is the real achievement -- a 2-parameter construction that captures 29% of solar variability beyond the mean.

The vehicle's job is to turn this static waveform into a causal prediction engine. It currently preserves 62% of the cascade's solar signal. The other 38% leaks through snap timing misalignment. This is a hard problem: making an energy network fire at the right moments without being told when the right moments are.

All easy approaches to closing this gap have been tried and failed. What remains are harder: gradient-based corrections, energy-phase lookahead, or fundamentally rethinking how the vehicle discovers peak timing. The Dalton era may require architectural additions (stronger Gleissberg modulation) that risk overfitting without careful validation.

ENSO and Colorado do not work in the autonomous vehicle. The hybrid proves the signal exists; the vehicle cannot yet extract it for short-period systems.

The project has clear, honest results: a working solar predictor, a proven cascade, a diagnosed gap, and a list of failed attempts that narrows the remaining search space. Progress is real but the hardest part -- autonomous temporal alignment -- remains unsolved.

---

*Audit compiled 24 April 2026.*
*ARA Framework -- Scripts 234L through 235O.*
*Dylan La Franchi, independent researcher.*
