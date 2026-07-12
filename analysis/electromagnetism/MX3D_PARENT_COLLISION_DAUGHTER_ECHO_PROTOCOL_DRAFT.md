# MX3d parent-collision to daughter/echo identity protocol

**Status:** DEVELOPMENT RUN / 6 OF 8 STRICT CRITERIA PASS / CONFIRMATORY TRANSFER REQUIRED  
**Tier:** development on the existing archive; confirmation requires a frozen new simulation

## Clarified causal claim

The daughter wave does not lead the parent. Two parent components must first clash or couple. Their nonlinear
interaction then generates smaller secondary waves, and a sufficiently coherent secondary wave becomes an identity
with its own amplitude, phase, boundary and ARA evolution.

\[
\underbrace{W_A+W_B}_{\substack{\text{parent phase and}\text{anti-phase interaction}}}
\longrightarrow
\underbrace{\mathcal I_{AB}}_{\substack{\text{collision/coupling}\text{event}}}
\longrightarrow
\underbrace{W_D}_{\substack{\text{daughter wave born}\text{after the parent event}}}.
\]

The causal prediction is therefore

\[
\underbrace{t_{AB}}_{\text{parent collision}}
<
\underbrace{t_D}_{\text{daughter onset}},
\]

not daughter-leading-parent.

## Terminology fence

ARA may use *echo daughter* for the general repeated secondary wave. In established plasma physics, *plasma echo*
has a narrower meaning: phase-mixed information from separately timed perturbations rephases into a later observable
response. The present unforced two-stream archive should therefore be described as nonlinear daughter/harmonic
generation unless it satisfies the specific plasma-echo excitation and rephasing conditions.

## Primary plasma implementation

The already frozen parent identity mode is (k_0=5). The primary daughter candidate is its second harmonic
(k_D=2k_0=10). The third harmonic (3k_0=15) is a disclosed secondary comparator.

For a quadratic parent-to-daughter interaction, test the phase-closure relation

\[
\underbrace{\Delta\phi_{2:1}(t)}_{\substack{\text{daughter inheritance}\text{or phase closure}}}
=
\underbrace{2\phi_{k_0}(t)}_{\text{two parent contributions}}
-
\underbrace{\phi_{2k_0}(t)}_{\text{daughter phase}}.
\]

Stable (Delta\phi_{2:1}) after daughter onset is evidence of phase-locked nonlinear inheritance. Amplitude growth
alone is insufficient.

The corresponding bispectral quantity is

\[
\underbrace{B(k_0,k_0)}_{\substack{\text{quadratic phase}\text{coupling statistic}}}
=
\left\langle
\widehat X_{k_0}
\widehat X_{k_0}
\widehat X_{2k_0}^{*}
\right\rangle,
\]

normalised to bicoherence so that ordinary amplitude growth does not automatically count as coupling.

## Identity-birth requirements

The (2k_0) wave qualifies as a daughter identity only if all of the following hold:

1. **Temporal order:** parent interaction/growth precedes daughter onset by a positive frozen lag.
2. **Phase inheritance:** (2\phi_{k_0}-\phi_{2k_0}) becomes more concentrated than shuffled and non-triad controls.
3. **Nonlinear coupling:** bicoherence at ((k_0,k_0,2k_0)) exceeds mode-matched null triplets.
4. **Own persistence:** after onset, the daughter retains measurable amplitude/coherence for a declared minimum life.
5. **Own state:** its field-derived and particle-derived appearances permit a separate ARA/TE-ARA coordinate.
6. **Noise survival:** the relation transfers across particle counts and seeds in the full MX3 family.

## Existing-data development test

1. Calculate complex (k_0), (2k_0) and (3k_0) coefficients for field, particle-source and pressure fields.
2. Freeze parent onset/collision and daughter onset rules without consulting phase closure.
3. Measure whether (k_0^2) amplitude predicts later (2k_0) amplitude more strongly than earlier (2k_0) amplitude.
4. Measure phase-closure concentration before and after daughter onset.
5. Calculate windowed bicoherence at the declared triad.
6. Test daughter persistence after the parent amplitude peaks or declines.
7. Construct a separate daughter TE-ARA participation and closure series only after onset eligibility.

## Nulls

- phase-randomise (2k_0) while preserving its amplitude spectrum;
- circularly shift daughter time relative to the parent;
- compare non-triad modes with similar amplitude;
- compare (k_0+k_j\ne k_D) triplets;
- reverse the temporal order;
- use parent amplitude alone as the baseline;
- require the same onset rule for field and particle views.

## Success rule

Development support requires positive parent-to-daughter temporal order, phase closure, triad-specific bicoherence and
daughter persistence. A strong post-collision pressure-magnitude change alone is only a state-transition marker; it
does not establish daughter birth.

Substantial support requires the complete frozen construction to transfer across particle counts, particle seeds and
the held-out beam configuration.

## Failure rule

The claim fails for this implementation if the secondary harmonic precedes the parent event, lacks phase inheritance,
is indistinguishable from non-triad modes or disappears under particle-noise convergence.

## Plain-language version

First identify the large parent clash. Then look for a smaller wave that appears afterwards. To count as a daughter,
it must not merely rise later: its phase must reveal that it was produced by the parent pair, it must persist long
enough to have its own state, and the same relation must survive cleaner simulations. That directly tests Dylan's
claim that the smaller fractal wave is born from the collision and then becomes an identity of its own.

## Physics cross-reference

- J. H. Malmberg, C. B. Wharton, R. W. Gould and T. M. O'Neil, *Plasma Wave Echo Experiment*, Physical Review
  Letters 20, 95 (1968). This anchors the narrower established meaning of plasma echo.
- Three-wave coupling and bicoherence provide the established comparison family for phase-locked daughter-mode
  generation. A positive ARA result must add a scale/identity interpretation without relabelling those established
  mechanisms as newly discovered.

## Development result - 12 July 2026

The declared \(k=10\) field daughter crossed its sustained threshold 19 slices after parent \(k=5\); the particle
daughter followed 31 slices after the parent. Phase-closure concentration rose from 0.2873 in baseline to 0.9848
between parent and daughter thresholds and remained 0.9352 post-onset. Random-phase null \(p=0.0020\) passed;
circular-shift null \(p=0.5129\) failed because shifting within the long phase-locked interval preserved closure.

Field bicoherence was 0.8376 at the 97.48th control percentile. Particle bicoherence was 0.8334 at the 94.96th
percentile, narrowly missing the predeclared 95% gate. The daughter remained above threshold for 262 slices, including
the entire post-parent-peak period, and averaged 3.25% of parent field power. Field/particle daughter TE correlation
was 0.9991.

Six of eight strict criteria passed. Interpret as strong development support for gradual nonlinear harmonic
inheritance and a persistent secondary mode. Do not claim a discrete creation instant: phase organisation begins
below the visibility threshold. Do not claim universal fractal ARA birth without noise/seed/beam transfer.

Outputs: `MX3D_DAUGHTER_ECHO_REPORT.md`, `MX3D_DAUGHTER_ECHO_RESULTS.json`, and
`MX3D_DAUGHTER_ECHO_RESULT.png`.
