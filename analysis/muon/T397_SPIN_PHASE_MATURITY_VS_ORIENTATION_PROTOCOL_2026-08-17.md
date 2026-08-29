# T397 — spin phase: maturity clock or orientation organiser?

**Frozen:** 17 August 2026, before T397 execution or T397-specific scoring  
**Status:** executable frozen protocol  
**Source state:** the RAL Silver counts were inspected in T382/T389–T391; this is therefore a new locked analysis on an old source, not a pristine source-blind replication  
**Parent programme:** `T381_ARA_NATIVE_MUON_NEUTRINO_HANDOVER_MASTER_PROTOCOL_2026-08-14.md`

## Who, what, when, where, why and how

- **Who:** coherent positive-muon populations stopped in the same 300 K RAL Silver medium used by T382 and T389–T391.
- **What:** separate the measured spin relation into (a) a detector-contrast/orientation cut and (b) an acceptance-balanced common-mode/release cut. Ask whether the spin phase predicts only where charged daughters are seen or also when the parent population releases them.
- **When:** native 0.016 microsecond bins over `0.25 <= t < 8.00 microseconds`. The calibration-frozen cadence defines complete spin cycles. Odd cycles fit each phase term; even cycles are untouched within-run prediction rows. The parity is reversed only as a sensitivity check.
- **Where:** ISIS EMU investigation RB1620201, DOI `10.5286/ISIS.E.RB1620201`; 96 detectors arranged as official forward detectors 1–48 and backward detectors 49–96.
- **Why:** T391 established a raw population spin anti-phase, while T390 rejected one exact 7.5-turn release trigger. T397 tests the broader ARA hypothesis that spin is the muon waveform/lifespan and therefore marks release maturity at some stable phase, without assuming an exact pole or turn count.
- **How:** freeze the spin cadence from earlier calibration, fit phase on odd cycles, predict even cycles, and compare the orientation field with three increasingly strict parent-release sums. Wrong cadences, train/test reversal, cycle-block bootstrap and acceptance-cancellation controls distinguish a physical common-mode release signal from directional detector leakage.

## Identity, rung and direction

### Parent release identity

The parent is the surviving muon population. Its calibration-frozen population envelope is

\[
\lambda_P(t)=A e^{-t/\tau_P}+b,
\qquad
\tau_P=2.1928\ \mu\mathrm{s}.
\]

The parent release cut is the detector common mode after this envelope is removed. It is population-grain: no individual muon, neutrino or deterministic lifetime is observed.

### Spin traversal child

The child is the raw population spin relation recovered in T391. Its frozen cadence is

\[
\theta_B(t)=2\pi\widehat\gamma B t,
\qquad
\widehat\gamma=0.01382\ \mathrm{MHz/G}.
\]

The ARA display coordinate remains

\[
x_S(t)=1-\cos\theta_B(t),
\]

with the joint signed Di-ARA supplied by `cos(theta)` and `sin(theta)`. The phase origin is arbitrary for the two-quadrature test; no release pole is selected after looking.

### Hypotheses

- **Maturity hypothesis:** the spin child phase contributes a reproducible common-mode modulation to the parent release channel. The phase term learned on odd cycles predicts even cycles after directional acceptance is balanced.
- **Orientation-only hypothesis:** the spin phase strongly predicts detector contrast, but cancels from the balanced common mode. It organises daughter direction without measurably changing the population decay hazard.
- **Inconclusive:** the orientation positive control fails, or a common-mode term appears only in an acceptance-sensitive construction and cannot survive the stricter common-mode cuts.

## Frozen source split

Cadence, parent lifetime and detector acceptance are learned only from the six T382 calibration runs:

- 20 G: `EMU00066572`, `EMU00066574`, `EMU00066576`;
- 25 G: `EMU00066573`, `EMU00066575`, `EMU00066577`.

Primary untouched fields remain:

- 63 G: `EMU00066578`;
- 160 G: `EMU00066579`;
- 400 G: `EMU00066580`.

The 20/25 G bookends are validation diagnostics. The 1000/2000/4000 G runs remain excluded from primary inference because of the EMU measurable-frequency band and native resolution boundaries already frozen in T382.

## Four measurement channels

Let `n_d(t)` be detector counts, `F(t)` the sum of detectors 1–48 and `B(t)` the sum of detectors 49–96.

### O — orientation/contrast channel

Use the full 96-detector share residual

\[
\mathbf y(t)=\frac{\mathbf n(t)}{\sum_d n_d(t)}-\bar{\mathbf q},
\]

where `q_bar` is the run-wide count-weighted detector share. Fit detector-specific `cos(theta)` and `sin(theta)` coefficients on odd cycles and predict even cycles. This is the positive-control child cut; it does not use the detector total as a target.

### U — unbalanced raw parent total

\[
U(t)=F(t)+B(t).
\]

This retains the instrument's native acceptance and is expected to be most vulnerable to directional leakage.

### V — bank-balanced parent total

Using the calibration-only efficiency ratio

\[
\alpha={\sum F_{cal}\over\sum B_{cal}},
\]

form

\[
V(t)=F(t)+\alpha B(t).
\]

The matching contrast `F-alpha*B` is not added to `V`; opposite bank orientation should cancel in this sum.

### W — detector-normalised parent common mode

Let `q_d` be detector `d`'s calibration-only share over the frozen analysis window and let `q_med` be their median. Freeze

\[
w_d={q_{med}\over q_d}
\]

and form

\[
W(t)=\sum_d w_d n_d(t).
\]

`W` is the strictest T397 common-mode cut. It equalises persistent detector sensitivity before the holdout phase is scored.

## Model and within-run holdout

For each scalar parent channel `Z in {U,V,W}`, fit the parent-only model on odd cycles:

\[
\widehat Z_0(t)=A_Ze^{-t/\tau_P}+b_Z,
\]

then fit the phase model on the same odd cycles:

\[
\widehat Z_1(t)=\widehat Z_0(t)
\left[1+\beta_c\cos\theta_B(t)+\beta_s\sin\theta_B(t)\right].
\]

The phase coefficients are bounded only as required to keep predictions positive. Both models are scored once on even cycles using count-weighted squared fractional error. `U` additionally receives a Poisson likelihood sensitivity score because it remains integer-valued.

For the orientation field, use the same odd-cycle fit/even-cycle score with detector-share residuals and total counts as weights.

Primary phase gain is

\[
G=1-\frac{\mathrm{SSE}_{phase,even}}{\mathrm{SSE}_{parent,even}}.
\]

The release amplitude is

\[
A_{release}=\sqrt{\beta_c^2+\beta_s^2},
\]

reported as a fraction and percent of the parent envelope. Phase angles are reported but not post-hoc aligned to a preferred ARA landmark.

## Frozen controls

1. **Orientation positive control:** `O` must have positive prediction gain in every primary field.
2. **Acceptance ladder:** compare `U -> V -> W`. A genuine common-mode maturity signal should survive balancing; a directional leak should shrink or lose coherence.
3. **Wrong cadence:** repeat the scalar phase fit using fixed frequency multipliers `0.50, 0.60, ..., 0.90, 1.10, ..., 1.50`, while the odd/even split remains defined by the correct cadence.
4. **Other-field cadence:** for each run, use the other two primary fields as deliberately wrong timing fields.
5. **Reverse parity:** fit even cycles and predict odd cycles as a sensitivity check; it cannot replace the primary odd-to-even verdict.
6. **Cycle-block bootstrap:** resample complete scored cycles within fields and fields as blocks, without refitting predictions, for the pooled `G` interval.
7. **Field consistency:** report each field separately. A pooled gain cannot hide a field with opposite sign.
8. **Established-physics crosswalk:** compare the result only after the ARA-first gate is frozen and scored.

## Decision gates

### Orientation recovered

Pass only if:

1. odd-to-even orientation gain is positive in all three primary fields;
2. the pooled orientation gain has a cycle/field bootstrap 95% lower bound above zero;
3. the correct cadence beats every frozen wrong-cadence family in pooled orientation gain.

### Maturity supported

Pass only if orientation is recovered and:

1. strict common mode `W` has positive odd-to-even phase gain in all three primary fields;
2. pooled `W` gain has a cycle/field bootstrap 95% lower bound above zero;
3. correct-cadence `W` gain exceeds the 97.5th percentile of all frozen wrong-cadence gains;
4. the fitted common-mode phase is directionally coherent across fields (circular resultant length at least `0.70`);
5. `W` retains at least half of the phase amplitude seen in `U`, or `W` has a stronger held-out gain than `U`; this guards against declaring a vanishing acceptance residue a parent clock;
6. reverse-parity `W` gain is non-negative in every field.

### Orientation only

If orientation passes but maturity does not, classify T397 as `ORIENTATION_SUPPORTED_MATURITY_NOT_SUPPORTED`. This is the expected classification when the phase is carried by the daughter-direction field and cancels in the parent common mode.

## Claim boundary

T397 can test a phase-dependent **population release hazard**. It cannot determine a named muon's decay instant, directly observe either neutrino, or prove that spin is the causal source of decay. A positive common-mode result would require untouched same-medium replication; a negative result rejects this source's measurable population-level maturity modulation, not every possible lower-rung individual mechanism.

## Required outputs

1. protocol hash;
2. source and data-quality manifest;
3. per-field orientation and `U/V/W` scores;
4. wrong-cadence and reverse-parity controls;
5. cycle/field bootstrap intervals;
6. machine-readable results and independent validation JSON;
7. a labelled visual report showing orientation, common mode, phase amplitude, control ranks and exact axes/units;
8. explicit ARA-first verdict and established-physics crosswalk.
