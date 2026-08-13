# T354 frozen protocol v1 - Irrationality parent-ridge centre invariance

**Frozen:** 11 August 2026, before T354 implementation or scoring  
**Evidence class:** synthetic known-referee instrument calibration  
**Upstream instruments:** T348 Irrationality Di-ARA; T352 handover excursion; T353 window-smear result

## Question

T352 and T353 showed that a finite observation window broadens an
Irrationality handover, but did not test whether the broadened feature retains a
fixed centre. T354 asks the narrower parent-ridge question:

> When the observer width changes, does the midpoint between the two stable
> Irrationality endpoint coordinates remain locked to the known transition
> centre?

This test does **not** assume that direct-coupling dusk/dawn and Irrationality
handover share the same child identity. It tests only whether the current
Irrationality coordinate contains a stable parent-ridge location underneath
window-dependent broadening.

## WHO

New known-referee circle paths use rational and irrational endpoint advances in
both directions. Parameters are disjoint from T352 and T353:

- rational denominators `q={13,17,23}`;
- irrational advances from `d={43,47,53}`;
- ordered handover durations `{256,448,640}` states;
- six new initial phases per parameter combination;
- matched ordered and abrupt transitions;
- identity-specific transition centres distributed between states `1408` and
  `2688`, rather than fixed at one common time.

The changing centres make a wrong-time permutation control meaningful.

## WHAT

Retain the T348 address-openness coordinate `x_P`, whose stable rational and
irrational endpoints occupy opposite sides of the ARA diameter. For each path
and observation width, estimate the two stable endpoint medians only from the
first and last quarters of the record. Define the identity-specific parent
ridge level

\[
x_{P,ridge}=\frac{\widetilde{x}_{P,first}+\widetilde{x}_{P,last}}{2}.
\]

Normalize the endpoint direction so that the first stable endpoint is `0`, the
last stable endpoint is `2`, and the parent ridge is `1`:

\[
r_P(t)=2\,\frac{x_P(t)-\widetilde{x}_{P,first}}
{\widetilde{x}_{P,last}-\widetilde{x}_{P,first}}.
\]

The predicted ridge time is the linearly interpolated chronological crossing
of `r_P=1` inside the longest contiguous transition run bounded by
`0.5 <= r_P <= 1.5`. No known transition label is used to choose the crossing.

The visible transition width is the span of that `0.5..1.5` run. The T348
stochastic-residual coordinate `x_R` is retained only as a diagnostic around
the predicted ridge; it does not define the primary ridge verdict.

## WHEN AND WHERE

Paths contain `4096` states. Observation windows are
`W={128,256,384,512}` with a common 32-state stride. The event centre and
ordered-ramp boundaries are hidden from the estimator and revealed only for
scoring.

The measurement is local to the existing Irrationality Di-ARA rung. A pass
supports a stable parent-ridge coordinate under observer broadening; it does
not identify the child composition of an Irrationality handover.

## HOW

For each identity, direction, mode and window:

1. calculate `x_P` across the complete path;
2. obtain stable endpoint medians from the outer quarters;
3. orient and normalize the coordinate to `0..2`;
4. select the longest contiguous `0.5..1.5` run;
5. interpolate its `r_P=1` crossing without using the referee centre;
6. reveal the centre and record signed and absolute error;
7. separately record transition-run width and a local `x_R` diagnostic.

The wrong-time control circularly permutes referee centres among identities
within each direction and mode while retaining every predicted ridge time.

## Frozen gates

All intervals use 5,000 identity-level bootstraps with seed `35420260811`.

1. **R1 endpoint separation.** Every `direction x mode x W` group has median
   absolute endpoint separation of at least `0.75` raw ARA units, and at least
   95% of series yield a ridge prediction.
2. **R2 known-centre localization.** In both directions and both modes, median
   absolute ridge-centre error is at most `64` states and its 95% bootstrap
   upper bound is at most `128` states.
3. **R3 window invariance.** Across the four windows, the identity-level median
   predicted-centre range is at most `64` states in each direction and mode,
   with a 95% bootstrap upper bound at most `128` states.
4. **R4 directional complement.** For ordered paths, the two directions differ
   in median signed error by at most `32` states and each direction has absolute
   median signed error at most `32` states.
5. **R5 broadening without centre drift.** In both directions and both modes,
   median transition width is nondecreasing across `W`, while the absolute
   slope of median predicted centre versus `W` is at most `0.10` states per
   window-state.
6. **R6 wrong-time control.** In both directions and both modes, the true-label
   median absolute error is at most one quarter of the permuted-label median
   absolute error, with a strictly positive matched-bootstrap interval for
   `permuted error - true error`.

All six gates must pass for `SUPPORTED [synthetic parent-ridge instrument
only]`. R1 passing with R2 or R3 failing is `RIDGE NOT RESOLVED`. R1-R5 passing
with R6 failing is `ALIGNMENT NOT SPECIFIC`.

## Required outputs

- complete `x_P` profiles and local `x_R` diagnostics;
- one row per identity, mode and window with predicted ridge and width;
- identity-level invariance summaries and wrong-time controls;
- frozen gate table and machine-readable JSON;
- static figure showing window-dependent broadening, ridge-centre predictions,
  direction complement and wrong-time separation;
- independent validation report recomputing the headline values.

## Evidence boundary

The generator supplies a known rule transition. A pass shows that the existing
Irrationality `x_P` coordinate localizes the parent midpoint robustly across
observer widths under these controlled conditions. It does not establish a
physical Irrationality dusk, prove that the midpoint is a universal physical
singularity, or determine which lower children perform the handover.
