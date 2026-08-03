# T320A Phi-pillar physical transfer — phase-label fidelity correction

**Declared:** 31 July 2026, after T320 v1 was opened and before the corrected
route was calculated.

**Status:** post-result methodology correction; not a new blind test.

**Later identity-boundary correction:** this document removed T320's
instantaneous sign error but still mapped three distinct arms onto one
A–B–A handover. That is not Dylan's intended object. The intended test
holds the arm identity fixed and follows one Phase-A swing, its intervening
Phase-B swing, and the following Phase-A swing of that same arm. Accordingly,
the calculation below is retained only as a cross-arm coupling triangle; it
does not test the same-identity temporal handover.

## Why T320 v1 is retained but not interpreted

T320 v1 required the two cross-rung Phase-A states to have positive
phase-plane dot product and the intermediate Phase-B state to have negative
dot product with each. That translated an ARA identity label into an
instantaneous vector-orientation condition.

The exact benchmark shows the mistake. In the side-one regular pentagon,
the labelled same-phase endpoints \(A_0,A_1\) span a \(144^\circ\) central
angle. Same-phase across rungs therefore does **not** mean parallel position
vectors in the embedding space.

The T320 v1 filter retained only four `0.10 s` evaluation windows and forced
the observed angle toward a narrow sector. Its `NOT SUPPORTED` verdict applies
only to that mistaken same-direction operationalization.

## Cross-arm mapping actually calculated

Retain the predeclared, simultaneously measured hierarchy without adding an
instantaneous sign filter:

\[
\underbrace{z_3(t)}_{A_0\text{ / child scale}}
\rightarrow
\underbrace{z_2(t)}_{B\text{ / intermediate scale}}
\rightarrow
\underbrace{z_1(t)}_{A_1\text{ / larger scale}}.
\]

The common state space, development-only robust coordinate scales, raw data
split, route statistic and candidate landmarks remain exactly those in T320:

\[
q(t)=\frac{2\,d(z_3,z_1)}{d(z_3,z_2)+d(z_2,z_1)}.
\]

All samples with nonzero state norms and nonzero route legs are eligible.
Results are still compressed into non-overlapping `0.10 s` windows.

The mirror branches remain defined only for reporting by the sign of arm 1's
rest-centred angle. This sign does not determine eligibility.

## Frozen controls and gates

The candidates, three shifted-middle controls, endpoint-swap invariance,
equal-leg statistic and all five T320 gates are unchanged:

1. Phi uniquely minimizes median absolute \(q\) error;
2. `108°` uniquely minimizes included-angle error;
3. median equal-leg ratio is at least `0.90`;
4. both reported mirror branches select Phi;
5. the real middle-arm alignment has lower Phi error than shifts of `17%`,
   `31%`, and `47%`.

The verdict bands are unchanged: `5/5` supported, `3–4/5` mixed, `0–2/5`
not supported.

## Evidence boundary

Because the source was already opened by T320 v1 and many earlier pendulum
tests, T320A is a fidelity-corrected retrospective transfer. A pass would
justify freezing this corrected statistic on a different physical domain; a
failure rejects this particular three-arm state-space embedding only. It
does not reject the intended same-arm temporal Phi handover.
