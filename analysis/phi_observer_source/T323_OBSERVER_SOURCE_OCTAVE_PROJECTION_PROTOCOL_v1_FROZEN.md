# T323 — observer–source octave projection protocol v1 (frozen)

**Frozen:** 1 August 2026, before downloading or inspecting the selected SOFA
measurements  
**Status:** confirmatory pilot of Dylan's observer–source interpretation of
the Phi handover  
**Primary public source:** ARI subject NH2, SOFA test archive  
**Directional confirmation:** ARI subject NH4, same archive and measurement
convention

## Question

The failed bubble-centroid projection T322B compared a child displacement with
a parent that already contained that child. Dylan clarified that this is not
the intended object. The intended geometry is an observer looking toward an
independent source across both a propagation axis and a scale axis:

- the observer is the boat;
- the source is the lighthouse;
- the measured transfer path is the third relation;
- horizontal is the source-to-observer phase accumulated at one frequency;
- vertical is the additional phase accumulated when the frequency doubles.

This pilot asks whether their resultant direction preferentially occupies the
Phi projection angle

\[
\theta_\phi=36^\circ,
\qquad
2\cos\theta_\phi=\phi,
\]

rather than the direct, diagonal, or other preregistered alternatives.

## Data and independent identities

Use measured head-related impulse responses (HRIRs) from the public ARI SOFA
files:

1. `ARI_NH2_hrtf_M_dtf 256.sofa` — primary evaluation;
2. `ARI_NH4_hrtf_M_dtf 256.sofa` — directional confirmation.

Each source direction and receiver ear is one observer–source path. The source
direction metadata must be retained. The two receiver ears are separate paths
but uncertainty is clustered at source direction, so they are not counted as
independent directions.

The files are selected before inspection. NH4 cannot be substituted if NH2
fails. Any file-format incompatibility must be documented before choosing a
replacement.

## Frozen transform

For every source direction `m` and receiver `e`, calculate the unwindowed
real Fourier transform of the measured impulse response:

\[
H_{m,e}(f)=\mathcal F\{h_{m,e}(t)\}.
\]

Unwrap phase continuously from DC through the positive-frequency bins:

\[
\psi_{m,e}(f)=\operatorname{unwrap}\arg H_{m,e}(f).
\]

Use exact FFT-bin octave pairs `(k, 2k)`. Eligible lower bins satisfy:

- `2 <= k <= floor((N/2)/2)`;
- both magnitudes are at least `1%` of that path's maximum positive-frequency
  magnitude;
- `|psi(f_k)| >= 0.05 rad`, preventing an unstable angle from two nearly zero
  coordinates.

No smoothing, minimum-phase reconstruction, time-alignment fitting, or
post-observation phase offset may be introduced.

## Observer–source ARA coordinate

For each eligible pair, define

\[
\Delta_{\parallel}=\psi(f_k),
\qquad
\Delta_{\rm octave}=\psi(f_{2k})-\psi(f_k).
\]

The first coordinate is the accumulated source-to-observer phase at the lower
scale. The second is the additional phase between that scale and its doubled
frequency. Their signed relation is retained as one of four quadrants.

The primary folded projection angle is

\[
\theta
=
\operatorname{atan2}
\left(
|\Delta_{\rm octave}|,
|\Delta_{\parallel}|
\right),
\qquad 0\leq\theta\leq90^\circ.
\]

The equivalent ARA diameter projection is

\[
x=2\cos\theta.
\]

Phi predicts `theta = 36 degrees` and `x = phi`.

## Physical baseline and interpretation

For a pure delay,

\[
\psi(2f)=2\psi(f),
\]

so

\[
|\Delta_{\rm octave}|=|\Delta_{\parallel}|
\quad\Longrightarrow\quad
\theta=45^\circ.
\]

Thus `45 degrees` is a strong physical null, not a weak arbitrary control.
A `36-degree` result must outperform it directly.

This test operationalizes the vertical ARA rung as a frequency octave. A
negative result rejects that operationalization for these acoustic transfer
paths; it does not reject every observer–source, geometric-size, or temporal
version of vertical ARA.

## Frozen targets and loss

Compare the identical per-path root-mean-square angular loss against:

| Label | Angle |
|---|---:|
| direct | 0 degrees |
| thirty | 30 degrees |
| Phi projection | 36 degrees |
| pure-delay diagonal | 45 degrees |
| Phi complement | 54 degrees |
| ridge-half | 60 degrees |
| perpendicular | 90 degrees |

For target `t`,

\[
L_t(m,e)
=
\sqrt{\frac{1}{K_{m,e}}
\sum_k(\theta_{m,e,k}-t)^2}.
\]

The free path angle is the arithmetic mean of its eligible folded angles.
Dataset summaries report medians across paths and bootstrap at source
direction.

## Frozen controls

1. **Broken source–receiver relation.** Keep the lower phase from one source
   direction and take the doubled-frequency phase from the next source
   direction after sorting by azimuth, elevation, and radius, within the same
   ear. This preserves the measured phase marginals and frequency structure
   but breaks the direct lighthouse–boat path.
2. **Phase-scrambled path.** Preserve each measured magnitude spectrum and
   randomly permute the non-DC positive-frequency phase increments within a
   path. Reintegrate the increments from zero phase. Use `64` deterministic
   hash-seeded permutations per path and average target losses.
3. **Ear symmetry.** Report left and right paths separately. Neither may be
   selected after observing which is closer to Phi.
4. **Quadrants.** Report the signs of `(Delta_parallel, Delta_octave)` rather
   than using the folded angle alone.

## Inference

- Primary unit: source direction, with both ears resampled together.
- Uncertainty: `5,000` source-direction cluster bootstrap samples.
- Fixed-target comparisons are paired within path.
- NH2 is primary evaluation; NH4 is confirmation.
- Report all eligible frequency pairs and the result by octave-pair bin.

## Registered gates

### G1 — target specificity

`36 degrees` has lower median path loss than every other fixed target in NH2
and NH4. In NH2, every paired Phi-minus-control 95% cluster interval is below
zero.

### G2 — pure-delay discrimination

Phi-minus-45-degree loss is negative in both datasets, and its NH2 95%
cluster interval is below zero.

### G3 — free-angle proximity

The median free path angle is closer to `36 degrees` than to any other frozen
target in both datasets.

### G4 — real path relation

Observed Phi loss is lower than both broken-path and phase-scrambled Phi loss
in NH2, with both 95% cluster intervals below zero, and both point differences
remain negative in NH4.

### G5 — octave recurrence

At more than half of eligible lower-frequency bins in each dataset, the median
angle across source directions and ears is closer to `36 degrees` than to any
other frozen target.

Verdict:

- `5/5`: **SUPPORTED in this acoustic observer–source coordinate**;
- `3–4/5`: **MIXED**;
- `0–2/5`: **NOT SUPPORTED**.

## Algebraic boundaries

- `2 - phi` is forced once `x = phi`; it is not independent evidence.
- `3/8` and `2 - phi` remain distinct.
- `36 degrees` and `54 degrees` are complementary only when the axes are
  swapped. The axes are frozen here, so they are separate targets.
- A result near `45 degrees` recovers ordinary frequency-doubling phase for a
  delay path; it must not be relabelled as a failed approximation to Phi.

