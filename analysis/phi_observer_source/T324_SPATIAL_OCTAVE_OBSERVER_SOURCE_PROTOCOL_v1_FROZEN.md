# T324 — spatial-octave observer–source protocol v1 (frozen)

**Frozen:** 1 August 2026, before downloading or inspecting the selected SOFA
measurements  
**Status:** confirmatory test of Dylan's literal geometric-distance
observer–source interpretation of the Phi handover  
**Primary public source:** KEMAR multi-distance anechoic SOFA measurement at
`0.5`, `1`, `2`, and `3` metres

## Question

T323 tested a frequency octave inside one transfer path. It did not support a
Phi projection: when the archive's separately stored latency was restored, the
result approached the ordinary `45 degree` propagation diagonal.

T324 tests the interpretation Dylan originally intended. The octave is now a
literal source–observer distance change, not a frequency doubling:

- `0.5 -> 1 m` is the first spatial octave;
- `1 -> 2 m` is the second spatial octave;
- `2 -> 3 m` is a non-octave control;
- the source direction, receiver ear, and acoustic frequency are held fixed.

The test asks two related but independent questions:

1. Does the complete observer–source phase and its change across a doubled
   distance form the `36 degree` Phi direction rather than the `45 degree`
   ordinary-propagation direction or the `54 degree` reversed-axis direction?
2. After cancelling any common recording-time offset, do consecutive spatial
   increments scale by `phi` or by the ordinary geometric ratio `2`?

The second question is decisive if the first is sensitive to the recording's
time-origin convention.

## Data and independent identities

Use the publicly listed SOFA file:

`qu_kemar_anechoic_radius_0.5_1_2_3_m.sofa`

from the official SOFA Toolbox test archive. The file is selected before
inspection. It may not be replaced after observing a result. If its contents do
not actually contain matched directions at all four registered radii, or if the
published timing fields cannot be interpreted from their units and metadata,
T324 is **BLOCKED BY DATA**, not silently redirected to another archive.

One source direction is the independent cluster. Receiver ears, frequencies,
and radii are repeated measurements within that direction. Only direction
clusters are resampled for uncertainty.

Matched records must have identical source azimuth and elevation after
conversion to spherical degrees. Radius labels are matched to `0.5`, `1`, `2`,
or `3` metres with absolute tolerance `1e-6 m`. Duplicate records at the same
direction and radius are an exclusion unless the metadata supplies an explicit
repeat index, in which case repeats are averaged in the complex transfer domain
before forming coordinates.

## Complete published timing

The primary analysis must use every timing term published in the SOFA file. No
timing term may be fitted to make a target win.

For record `m`, ear `e`, and radius `r`, calculate the real Fourier transform
of the unwindowed impulse response:

\[
H_{m,e,r}(f)=\mathcal F\{h_{m,e,r}(t)\}.
\]

Unwrap only the stored-IR phase continuously from DC through the positive
frequency bins:

\[
\psi^{\rm IR}_{m,e,r}(f)
=
\operatorname{unwrap}\arg H_{m,e,r}(f).
\]

Convert each explicitly published delay or latency field to seconds using its
own SOFA unit attribute. The complete phase is

\[
\psi^{\rm total}_{m,e,r}(f)
=
\psi^{\rm IR}_{m,e,r}(f)
-2\pi f\,\tau^{\rm published}_{m,e,r},
\]

where `tau_published` is the sum of the applicable `Data.Delay` and
`MeasurementAudioLatency` terms. A scalar, ear-level, measurement-level, or
record-level timing field is broadcast only according to its declared shape.
Missing optional terms contribute zero; an unparseable present timing term
blocks the primary analysis.

This ordering is frozen: unwrap the stored IR first, then add the exact linear
phase implied by metadata. Re-unwrapping after adding a large published delay
could alias a physically valid delay at coarse FFT-bin spacing.

## Frequency eligibility

Use positive-frequency FFT bins from `500` through `8000 Hz`, inclusive. For a
given matched radius set, ear, and frequency:

- every required radius magnitude must be at least `1%` of that individual
  path's maximum positive-frequency magnitude;
- every phase quantity appearing in a denominator or angle coordinate must
  have absolute magnitude at least `0.05 rad`;
- no smoothing, phase-offset fitting, minimum-phase reconstruction, window
  selection, interpolation between FFT bins, or post-result frequency trimming
  is allowed.

If fewer than eight eligible bins remain for a path-level summary, that path is
excluded and counted explicitly.

## Test A — spatial-octave projection angle

For each doubled-radius step `r -> 2r`, where `r` is `0.5` or `1 m`, define

\[
\Delta_{\parallel}(r,f)=\psi^{\rm total}_{r}(f),
\qquad
\Delta_{\rm rung}(r,f)
=
\psi^{\rm total}_{2r}(f)-\psi^{\rm total}_{r}(f).
\]

The folded projection angle is

\[
\theta(r,f)
=
\operatorname{atan2}
\left(
|\Delta_{\rm rung}|,
|\Delta_{\parallel}|
\right),
\qquad 0\leq\theta\leq90^\circ,
\]

with ARA projection

\[
x=2\cos\theta.
\]

Compare identical path-level root-mean-square angular loss against these frozen
targets:

| Label | Angle |
|---|---:|
| direct | 0 degrees |
| thirty | 30 degrees |
| Phi projection | 36 degrees |
| ordinary doubled-distance propagation | 45 degrees |
| reversed-axis Phi | 54 degrees |
| ridge-half | 60 degrees |
| perpendicular | 90 degrees |

For ideal linear propagation with a correctly located time origin,
`psi_r = -k r`, so `Delta_rung = Delta_parallel` and `theta = 45 degrees`.
Therefore `45 degrees` is the principal physical null.

For the non-octave `2 -> 3 m` control, use the same construction with
`Delta_parallel = psi_2m` and `Delta_step = psi_3m - psi_2m`. Ideal linear
propagation predicts

\[
\theta_{2\to3}=\arctan(1/2)=26.565051^\circ,
\]

not `36` or `45 degrees`.

## Test B — offset-invariant increment ratio

At each matched direction, ear, and eligible frequency, calculate

\[
\rho(f)
=
\frac{
|\psi_{2m}(f)-\psi_{1m}(f)|
}{
|\psi_{1m}(f)-\psi_{0.5m}(f)|
}.
\]

Any phase term common to every radius cancels. Ordinary propagation predicts

\[
\rho_{\rm ordinary}=\frac{2-1}{1-0.5}=2,
\]

whereas the registered same-phase cross-rung Phi hypothesis predicts

\[
\rho_{\phi}=\phi=1.6180339887\ldots.
\]

Because a ratio can be heavy-tailed, target loss is measured in log space:

\[
L_q(m,e)
=
\operatorname{median}_f
\left|
\log\rho_{m,e}(f)-\log q
\right|,
\qquad q\in\{\phi,2\}.
\]

The non-octave control is

\[
\eta(f)
=
\frac{
|\psi_{3m}(f)-\psi_{2m}(f)|
}{
|\psi_{2m}(f)-\psi_{1m}(f)|
}.
\]

Both increments span `1 m`, so ordinary propagation predicts `eta = 1`.
Compare log loss to `1`, `phi`, and `2` without relabelling the winner.

## Frozen controls

1. **Analytic free-field null.** Evaluate the identical formulas on
   `psi_r(f) = -2*pi*f*r/c`, using the file's speed of sound if published and
   `343 m/s` otherwise. This must recover `45 degrees`, `rho = 2`, and
   `eta = 1` to numerical tolerance before measured results are accepted.
2. **Broken direction.** Keep the lower-radius path at one direction and take
   the larger-radius path from the next direction after deterministic sorting
   by azimuth and elevation, within the same ear. For `rho`, shift every
   non-base radius together so the two increments remain internally coherent
   but no longer share the observer direction.
3. **Ear symmetry.** Report ears separately; neither may be selected after
   seeing the result.
4. **Timing sensitivity.** Repeat Test A using only the stored IR phase. This
   is descriptive, not the primary. Test B should be invariant to a truly
   common omitted time offset; disagreement diagnoses radius-dependent timing
   metadata or representation.
5. **Quadrants.** Retain the signs of every unfolded coordinate before folding
   the angle.

## Inference

- Primary unit: source direction, with all ears and frequencies resampled
  together.
- Uncertainty: `5,000` deterministic source-direction cluster bootstrap
  samples.
- Fixed-target comparisons are paired within path.
- The two octave steps are reported separately and pooled only as a secondary
  summary.
- All exclusions, eligible bins, directions, ears, phase quadrants, and timing
  fields are reported.

## Registered gates

### G1 — Phi angle specificity

`36 degrees` has lower median path RMS loss than every other fixed target at
both `0.5 -> 1 m` and `1 -> 2 m`; its paired loss difference versus `45
degrees` has a source-cluster 95% interval below zero at both steps.

### G2 — repeated free-angle location

The median free path angle is closer to `36 degrees` than to `45` or `54
degrees` at both octave steps and in both ears.

### G3 — relation control

Observed Phi-angle loss is lower than broken-direction Phi loss at both octave
steps, with source-cluster 95% intervals below zero.

### G4 — offset-invariant Phi scaling

`rho` has lower median log loss to `phi` than to `2` in both ears, with the
paired source-cluster 95% interval below zero. The median `rho` is also closer
to `phi` than to `2`.

### G5 — non-octave discrimination and timing robustness

The `2 -> 3 m` control is closest to its ordinary predictions
`theta = 26.565051 degrees` and `eta = 1`, while the two spatial octaves retain
their registered Phi predictions. Test B's Phi-versus-2 ordering must not
reverse when separately stored common latency is omitted.

Verdict:

- `5/5`: **SUPPORTED in this spatial observer–source coordinate**;
- `3–4/5`: **MIXED**;
- `0–2/5`: **NOT SUPPORTED**.

## Interpretation boundaries

- This tests a literal spatial-octave operationalization of vertical ARA. It
  does not test every possible same-phase lineage or handover definition.
- `36` and `54 degrees` are complementary only after swapping the frozen axes;
  they remain separate targets.
- A win for `45 degrees`, `rho = 2`, and `eta = 1` recovers ordinary linear
  propagation and must not be renamed approximate Phi.
- A win for Phi in Test A without Test B is insufficient because an arbitrary
  common time origin can rotate Test A's coordinate.
- Test B is stronger against common latency, but it is still a descriptive
  property of these acoustic paths rather than evidence that Phi is universal.
- No post-result change of radius pair, frequency band, ear, timing term,
  target set, or loss function may enter the frozen verdict.

