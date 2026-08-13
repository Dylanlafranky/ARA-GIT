# T355 frozen protocol v1 - Irrationality relational parent ridge

**Frozen:** 11 August 2026, before T355 implementation or scoring  
**Evidence class:** synthetic known-referee relational-instrument calibration  
**Upstream result:** T354 single-direction ridge test failed; a post-hoc midpoint of opposite directional readings localized the known seam

## Question

T354 found that the forward and reverse one-sided ridge readings moved away
from the known seam with nearly equal and opposite biases. Their unweighted
midpoint returned to the seam, but the generator used exactly reversed paths.

T355 asks whether that paired result survives when the two directional children
are no longer exact mirrors:

> Does the parent ridge live in the relation between two opposite directional
> readings, rather than in either reading alone?

## WHO

New known-referee circle paths use parameters disjoint from T352-T354:

- rational denominators `q={19,29,31}`;
- irrational advances from `d={59,61,67}`;
- nominal handover durations `{288,480,672}` states;
- eight new identities per parameter combination;
- 72 identity pairs with unique hidden seam times from state `1376` through
  `2720`;
- observation windows `W={128,256,384,512}` with 32-state stride.

Every identity has simultaneous irrational-to-rational and
rational-to-irrational children sharing one referee parent seam.

Two construction conditions are used:

1. **clean pair:** opposite endpoint paths with equal linear handover timing but
   independent initial phases;
2. **asymmetric pair:** independently phased paths with unequal pre/post
   durations, different nonlinear handover shapes, and different tapered child
   perturbations. Both children still reach 50% endpoint mixing at the same
   parent seam, but their surrounding histories are not mirrors.

## WHAT

For each child independently, retain the frozen T354 estimator:

1. calculate the T348 address-openness coordinate `x_P`;
2. obtain stable first/last endpoint medians from the outer quarters;
3. orient the child from `0` to `2`;
4. locate its blind `x_P=1` crossing inside the longest `0.5..1.5` run.

Call the two independently predicted child centres
`t_hat_IR` and `t_hat_RI`. Before scoring, freeze the relational parent estimate

\[
\boxed{
\widehat t_{parent}
=
\frac{\widehat t_{IR}+\widehat t_{RI}}{2}
}.
\]

No direction-specific weight, fitted offset or duration correction is allowed.

## Controlled child asymmetry

The clean condition uses identical linear mixing profiles in both directions.
The asymmetric condition preserves the common 50% parent seam but deliberately
changes the surrounding child histories:

- the two directions receive different left/right transition extents;
- their pre- and post-seam power-law exponents differ;
- their initial circle phases are independently seeded;
- each receives a different tapered sinusoidal child perturbation that is zero
  in the stable endpoint regions.

Let `lambda_IR(t)` and `lambda_RI(t)` be the two direction-specific endpoint
mixing fractions. Exact mirroring would have `lambda_IR=lambda_RI`. The
generator audit records

\[
A_lambda=RMS(lambda_{IR}-lambda_{RI})
\]

and the normalized failure of the two instantaneous advances to sum to the two
stable endpoints. These values must verify that the asymmetric condition is not
an exact reversal.

## WHEN, WHERE AND WHY

Paths contain `4096` states. Stable endpoint medians come only from the outer
quarters. Hidden seam times are revealed after both one-sided estimates and the
unweighted parent midpoint are saved.

The test is at the relation between the two directional child readings. It does
not identify the lower child composition of the handover and does not assume
that its physical identity is literal dusk or dawn.

## Controls

1. **Single-direction control:** retain the better of the two one-sided absolute
   errors for each identity.
2. **Wrong-pair control:** pair each forward child with a reverse child from a
   different hidden seam, using a deterministic half-rotation within
   `condition x W`.
3. **Clean-pair control:** confirms the post-hoc T354 relation on new parameters
   before the deliberately non-mirrored condition is judged.
4. **Observer-width control:** the same pair is measured at all four windows.

## Frozen gates

All intervals use 5,000 pair-level bootstraps with seed `35520260811`.

1. **P1 asymmetry audit.** Clean pairs have median `A_lambda<=1e-12`.
   Asymmetric pairs have median `A_lambda>=0.05` and median normalized
   advance-complement residual at least `0.01`.
2. **P2 endpoint recovery.** Every `condition x direction x W` group has median
   absolute endpoint separation at least `0.75` raw ARA units, and at least 95%
   of children yield a ridge prediction.
3. **P3 relational localization.** In both conditions, identity-level median
   paired absolute error is at most `32` states and its 95% bootstrap upper
   bound is at most `64` states. Every `condition x W` group also has median
   paired absolute error at most `32` states.
4. **P4 relational window invariance.** In both conditions, the identity-level
   range of paired parent predictions across windows has median at most `32`
   states and 95% bootstrap upper bound at most `64` states.
5. **P5 pair beats either child.** In both conditions, median paired absolute
   error is at most one quarter of the median better-single-child error, with a
   strictly positive paired-bootstrap interval for
   `better-single error - paired error`.
6. **P6 wrong-pair specificity.** In both conditions, true-pair median absolute
   error is at most one quarter of wrong-pair error, with a strictly positive
   paired-bootstrap interval for `wrong-pair error - true-pair error`.

All six gates must pass for `SUPPORTED [synthetic relational parent-ridge
instrument only]`. P1-P2 passing with P3 or P4 failing is `RELATIONAL RIDGE NOT
RESOLVED`. P1-P5 passing with P6 failing is `PAIRING NOT SPECIFIC`.

## Required outputs

- generator asymmetry audit;
- one row per child direction, condition, identity and window;
- paired parent estimates, single-child and wrong-pair controls;
- identity-level window-invariance summaries;
- frozen gate table and machine-readable JSON;
- a static figure that exposes the separate child biases, paired parent
  estimate, asymmetry regimes, observer-width behaviour and controls;
- independent validation recomputing all headline results.

## Evidence boundary

A pass shows only that two opposite readings of this controlled synthetic
Irrationality instrument contain enough relational information to reconstruct a
known shared seam under the declared asymmetries. It does not prove a universal
parent ridge, establish a physical dusk identity, or show that arbitrary
opposite datasets may be paired. Because both synthetic children are generated
around a supplied common seam, physical transfer requires an independently
defined pairing and an unseen event time.
