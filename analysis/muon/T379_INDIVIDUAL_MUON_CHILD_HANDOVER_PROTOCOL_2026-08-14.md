# T379 — Individual-muon child handover

**Status:** FROZEN before full raw-event reduction or inspection of decay-time outcomes  
**Freeze date:** 14 August 2026  
**Source:** public QuarkNet Cosmic Ray e-Lab, detector 6845  
**Identity/medium:** individual stopped cosmic-ray muons in four closely stacked solid-plastic scintillators

## Question

The earlier event-linked test established the population-scale muon lifetime curve but did not show that an incoming two-ended pulse relation predicted the later decay time of one muon. T379 moves the cut to a new, independent detector and asks the child-scale question directly:

> Does the pre-decay ARA relation inside one stopped-muon event contain held-out advance information about the time at which that same event hands over to its visible decay electron?

The directly measured later signal is the charged electron candidate. The neutrinos are produced in the same muon decay but are not directly observed by this detector. Accordingly, “handover time” means the experimentally linked muon-to-electron delay, not a directly timed neutrino measurement.

## W5H freeze

- **Who:** individual stopped-muon candidates with one initial pulse cluster and exactly one later electron candidate in a channel touched by the initial cluster.
- **What:** a pre-decay two-child ARA coordinate formed from the gain-normalised upper and lower counter pairs.
- **When:** 11–12 February 2020 for calibration; 17–18 March 2020 for untouched chronological holdout.
- **Where:** QuarkNet DAQ 6845, four equal-area solid scintillators stacked at z = −0.47, −0.50, −0.53 and −0.56 m.
- **Why:** determine whether the previously observed parent population handover descends to event-specific child information.
- **How:** stream the public raw events, reconstruct pulse times and widths, retain clean linked candidates, and compare frozen prospective models on later runs.

## Source and configuration qualification

Frozen files:

| role | file |
|---|---|
| calibration | `6845.2020.0211.0` |
| calibration | `6845.2020.0212.0` |
| holdout | `6845.2020.0317.0` |
| holdout | `6845.2020.0318.0` |

All four files use DAQ firmware 1.12, `ConReg0..3 = 1F,71,1E,00`, discriminator thresholds 300 on all channels, and the same four-counter solid-scintillator geometry. Small run-specific TMC calibration registers and clock-frequency corrections are treated as timing calibration, not as physical predictors.

## Raw-event reconstruction

The QuarkNet raw format is decoded from its documented 16-word event lines.

1. A new event begins where bit 7 of word 2 is set.
2. Words 2–9 provide valid rising/falling edges for channels 1–4. Edge time is reconstructed from the 32-bit trigger counter and the 0.75 ns TMC subcount, using the run CPLD frequency.
3. Rising edges are paired with the next valid falling edge on the same channel.
4. The initial muon cluster consists of pulses beginning within 100 ns of the event's earliest pulse.
5. A later candidate must begin 0.30–10.0 microseconds after the initial cluster and occur in a channel present in that initial cluster.
6. The primary clean sample requires exactly one such later pulse cluster and at least two initial channels. Events with ambiguous multiple delayed candidates are excluded.

Cut sensitivity will be reported for initial-cluster widths of 50 and 150 ns and lower delay bounds of 0.20 and 0.50 microseconds. Those variants are diagnostics, not parameter-selection opportunities.

## Calibration-only channel normalisation

Let `ToT_j` be the initial time-over-threshold for counter j. Each channel is divided by its calibration-run median on fourfold, prompt, through-going events:

\[
q_j=\frac{\mathrm{ToT}_j}{\operatorname{median}_{\rm cal,4fold}(\mathrm{ToT}_j)}.
\]

Missing prompt channels contribute zero. Define the upper and lower children

\[
A=q_1+q_2,
\qquad
B=q_3+q_4,
\]

and the full ARA coordinate

\[
x_\mu=\frac{2B}{A+B}\in[0,2].
\]

The frozen decompression is

\[
s=x_\mu-1,
\qquad
a=|x_\mu-1|.
\]

No daughter amplitude, daughter channel, or decay delay enters `A`, `B`, `x_mu`, `s` or `a`.

## Competing prospective models

All coefficients are estimated on calibration events only. The outcome is the linked daughter delay, scored with the likelihood appropriate to the frozen 0.30–10.0 microsecond observation window.

1. **M0 — memoryless:** one population decay rate plus background.
2. **MG — ordinary geometry:** M0 plus total prompt strength, prompt multiplicity and prompt depth centroid.
3. **MA — ARA:** MG plus signed relation `s`, asymmetry `a`, and their predeclared interaction with prompt depth.

The primary empirical quantity is held-out mean negative log likelihood. Lower is better.

## Frozen landmarks

The connection-heavy solid-medium landmark is

\[
x_\mu=0.50
\]

using a fixed ±0.05 window. The following are separately labelled diagnostics and will not replace the primary landmark after inspection:

- `x_mu = 0.75` and `1.25`: quarter-ridge offsets;
- `x_mu = 1.00`: parent ridge;
- `x_mu = 1.50`: mirror of the solid-medium landmark.

For each window, observed held-out delay behaviour is compared with the fitted calibration-only memoryless expectation. All windows and denominators are reported, including empty or weakly populated ones.

The predeclared release direction is **earlier handover / higher daughter-arrival hazard** inside the `x_mu=0.50±0.05` window than in ordinary-geometry-matched events outside it. A later or null handover does not support the landmark claim.

## Decision gates

### Event-specific advance information — supported only if all hold

1. MA improves held-out mean NLL over MG in both holdout runs separately.
2. A stratified chronological-block bootstrap 95% interval for `NLL(MG) − NLL(MA)` is strictly above zero. Each holdout run is divided into six contiguous event-order blocks so the interval does not pretend that adjacent events are wholly independent.
3. The improvement survives calibration-only channel normalisation and the frozen cut-sensitivity variants.
4. It fails under within-run permutation of decay delays while retaining prompt features.

Otherwise the individual-prediction claim is **not supported**.

### Landmark handover — supported only if all hold

1. The frozen `x_mu=0.50±0.05` window differs from calibration-fitted memoryless expectation in the predeclared direction in both holdout runs.
2. Its stratified chronological-block bootstrap 95% interval excludes the null, using the same six blocks per holdout run.
3. The result is not explained by prompt total strength, multiplicity or counter-depth composition.

The landmark gate is separate from the event-specific predictive gate.

## Controls

- chronological holdout by acquisition date;
- within-run outcome permutation;
- upper/lower label reversal and wrong counter pairings;
- ordinary pulse/depth model without ARA terms;
- per-run results, not only pooled results;
- channel-gain and timing-calibration audit;
- background/accidental estimate from late-gate structure;
- explicit sample-retention accounting at every cut.

## Required outputs

- a machine-readable event table with source run and split;
- full numerical result and validation JSON;
- labelled calibration/holdout and control tables;
- a saveable HTML report with explicit axes, units, landmarks and denominators;
- 8–12 named individual-event traces selected by a fixed rule, not by visual appeal;
- a plain-language distinction between population timing and individual advance information.

## Interpretation boundary

A positive result would show that a pre-decay relation measured within one detector event carries reproducible information about the later visible muon-decay handover. It would not by itself identify a neutrino trajectory, measure neutrino energy, or establish deterministic decay times. A negative result would mean this particular child cut does not outperform the memoryless and ordinary detector/depth descriptions.
