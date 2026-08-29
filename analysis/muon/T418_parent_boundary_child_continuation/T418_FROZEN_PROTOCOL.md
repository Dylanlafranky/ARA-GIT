# T418 — Parent-boundary child continuation in the muon Irrationality Di-ARA

**Frozen before T418 development fitting or validation/holdout scoring:** 22 August 2026  
**Status:** ARA-first post-T417 locked reanalysis; same public muon-population spin identity  
**Source:** ISIS EMU RB1620447 at 300 K; the 47-run archive already used by T413–T417

## Question

When the T417 unresolved parent coordinate reaches its apparent pole
`I_parent = 2`, does the uncapped relation beneath that pole retain ordered
information that helps predict the later, independently measured State
Di-ARA?  The test distinguishes a parent estimator ceiling with recoverable
child structure from a boundary after which the available child relation adds
no transferable information.

This is not a test of an individual muon, a neutrino birth time, or an unseen
particle constituent.  Every record is a 96-detector population histogram.

## Who / what / when / where / why / how

### Who

The 13 development, 13 validation and 20 holdout magnetic-field runs from the
T413 source manifest.  RF-on and RF-off remain separate run/period identities;
field bootstrap resampling keeps the two periods paired.

### What

Retain the T417 parent waves and recover the two losses that were compressed
into the capped unresolved coordinate.  Open their exact child ARA balance and
test whether it contributes causal prediction of the later State Di-ARA after
the parent boundary has been reached.

### When

The native source interval remains 0.25–6.00 microseconds.  A 128-bin
past-only history is read every four native bins, exactly as in T416; the
prediction horizon is four such reads, or 16 native bins (approximately
0.256 microseconds).  Every predictor is available at or before the prediction
origin.

### Where

The particle, archive, material, temperature, detector-share reconstruction,
spin-frequency calibration and ARA rung are unchanged from T416–T417.  This
test does not silently pool a different medium or connect RF boundaries.

### Why

T417 showed a directed `R = I` crossing followed by an `I = 2` ceiling, while
the late evaluation population visibly pressed against the exact upper
amount/balance boundary.  T418 asks whether that boundary conceals a child
continuation rather than treating the end of the parent instrument as the end
of the relation.

### How

Recompute the T416 complex spin path and its 128-bin history losses directly
from the frozen public source.  Development rows alone fit the prediction
models and scaling constants.  The same frozen coefficients and gates are then
scored once on validation and once on holdout.

## Parent and child geometry

T416 used

\[
q(t)=\frac{L_{\rm local}(t)}{L_{\rm null}(t)},
\qquad
I_{\rm parent}(t)=2\min(1,q(t)).
\]

Thus all `q >= 1` values were compressed to `I_parent = 2`.  T418 preserves
that parent coordinate and opens the relation underneath it as

\[
x_{\rm child}(t)
=\frac{2q(t)}{1+q(t)}
=\frac{2L_{\rm local}(t)}
       {L_{\rm local}(t)+L_{\rm null}(t)},
\]

\[
x_{\rm child}^{\rm anti}(t)=2-x_{\rm child}(t).
\]

The pair is exact TE-ARA bookkeeping at the child cut.  Parent contact
`q = 1`, where `I_parent` first reaches two, is the child ridge
`x_child = 1`; values `q > 1` remain visible on the child `1–2` gradient.

The T417 parent plane remains

\[
R=2\rho,\quad A=\frac{R+I_{\rm parent}}{2},\quad
B=1+\frac{I_{\rm parent}-R}{I_{\rm parent}+R}.
\]

Its exact inverse is

\[
I_{\rm parent}=AB,\qquad R=A(2-B).
\]

Therefore the upper and lower parent boundaries are declared in advance:

\[
AB=2\quad(I_{\rm parent}=2),
\qquad
A(2-B)=2\quad(R=2).
\]

Their existence is geometric; the empirical questions are occupancy,
chronological approach and information retained after contact.

## Prediction target

The later independent State Di-ARA is

\[
Y_{t+h}=\bigl(x_L(t+h),x_C(t+h)\bigr),
\qquad h=4\ \text{T416 reads}.
\]

Only origins with `q(t) >= 1`, a previous child value and an available future
target are scored.  A run/period sequence is eligible when it contributes at
least four such origins.

The **parent/current-state baseline** uses

\[
Z_0(t)=\bigl[1,\ x_{\rm parent}(t),\ R(t),\ x_L(t),\ x_C(t)\bigr].
\]

The **child-continuation model** adds the child position and its causal first
difference:

\[
Z_1(t)=\bigl[Z_0(t),\ x_{\rm child}(t),\
x_{\rm child}(t)-x_{\rm child}(t-1)\bigr].
\]

Development means and standard deviations standardise predictors and targets;
ordinary least squares fits both two-output models.  Evaluation uses mean
squared Euclidean error on the two 0–2 State coordinates.  Metrics are first
averaged within run/period and then within magnetic field so dense time rows do
not masquerade as independent replicates.

## Frozen controls

1. **Circular child shift:** shift the two child predictors together by a
   deterministic non-trivial offset within each eligible run/period.  One
   thousand draws preserve their marginal path while breaking local timing.
2. **Reverse child:** reverse both child predictors inside each eligible
   run/period while leaving parent/current-state predictors and future targets
   fixed.
3. **Wrong-frequency child:** reconstruct the same uncapped child balance at
   the four T416 sideband frequencies and use their pointwise median.
4. **Parent/current-state baseline:** omit both child terms.
5. **RF separation:** score RF-on and RF-off separately before the field-paired
   pooled result.

All pseudorandom controls use seed 418.  Bootstrap intervals use 10,000
field-level resamples.

## Frozen gates

Validation and holdout receive separate verdicts.  A stage supports the child
continuation only if all gates pass:

1. **Availability:** at least 75% of run/period sequences are eligible.
2. **Added future-State information:** the field-bootstrap 95% interval for
   `MSE_baseline − MSE_child` lies wholly above zero.
3. **Timing specificity:** the observed child MSE is below at least 95% of the
   1,000 circular-shift MSE values (`p < 0.05`).
4. **Frequency specificity:** the field-bootstrap 95% interval for
   `MSE_wrong_frequency − MSE_child` lies wholly above zero.
5. **Direction specificity:** the field-bootstrap 95% interval for
   `MSE_reverse − MSE_child` lies wholly above zero.
6. **RF robustness:** the median baseline-minus-child improvement is positive
   in both RF conditions.

The result is labelled **replicated within this archive** only if both the
validation and holdout stages pass all six gates.  Because these source files
have appeared in earlier tests, even a replicated result is an operator-new
locked reanalysis, not untouched-source confirmation.

## Chart contract

The report must contain:

1. the parent amount/balance plane with the exact `I=2` and `R=2` boundaries,
   chronological arrows and RF separation;
2. parent `I`, child position and child anti-position through time for labelled
   example sequences;
3. a post-boundary child-position distribution with ridge and sample counts;
4. observed prediction error against baseline, shifted, reversed and
   wrong-frequency controls;
5. per-field paired improvements with RF identity visible;
6. a complete sequence table, gate table, equations, units and claim boundary.

All axes must carry numeric ticks, units or dimensionless `0–2` labels, and
legends.  Colour cannot be the only encoding of identity or direction.

## Claim boundary

Passing would show that the uncapped loss relation retains chronology-specific,
frequency-specific information about a later population State Di-ARA after the
capped parent coordinate reaches two.  It would support an ARA child
continuation through this instrument boundary.  It would not prove a universal
singularity law, identify the red/green drawn continuations as literal physical
spheres, observe an individual muon continuously, or time a neutrino release.
