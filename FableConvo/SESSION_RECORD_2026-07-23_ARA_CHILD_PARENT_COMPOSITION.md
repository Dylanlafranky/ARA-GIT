# Session record — frozen ARA child-to-parent composition test

**Date:** 23 July 2026  
**Status:** completed; primary protocol and independent validation passed

## User-approved question

After constructing the cosmic-to-quantum physics ladder, the next recommended test was to freeze one mathematical
rule for moving from two child ARA accounts to their parent. The rule was to be tested on a classical system, an
electromagnetic system and an untouched quantum holdout.

## Frozen interpretation

At child grain, flow through a shared interface leaves one child and enters the other. It therefore appears once
as release and once as accumulation. At parent grain the same flow is internal and crosses no parent boundary.

For child \(i\):

\[
x_i=\frac{2R_i}{A_i+R_i}.
\]

For two adjacent children with shared interface magnitude \(I\):

\[
\boxed{
x_P
=
\frac{2(R_1+R_2-I)}
{(A_1+R_1)+(A_2+R_2)-2I}
}.
\]

No coefficient was fitted.

## Models

1. analytic classical string-energy wave — operator establishment;
2. analytic lossless transmission line — verification;
3. analytic free Gaussian probability current — quantum holdout.

Each used `4,097` deterministic raw time samples. No smoothing, Fourier decomposition, learned components or
post-result tuning was used.

## Result

- retained samples: `12,291 / 12,291`;
- worst frozen parent-coordinate error: `2.1538e-14`;
- quantum holdout worst error: `2.4425e-15`;
- best incorrect-control MAE: `0.302350`;
- quantum finite-difference continuity residual: `6.1062e-11` against a frozen `1e-6` tolerance;
- independent validation: `15/15`;
- independent randomized check: `100,000` signed boundary-flux triples, maximum error `3.5083e-14`.

Both wrong controls failed in every model:

1. unweighted mean of the two child coordinates;
2. activity-weighted composition that left the internal interface counted inside the parent.

## Scientific meaning

This is a successful formalization of an ARA aggregation/zoom rule. It demonstrates with exact mathematics why
the classification of a relation changes with boundary:

\[
\text{child boundary flow}\rightarrow\text{parent internal relation}.
\]

It is also the ordinary finite-volume conservation identity in ARA coordinates. The pass therefore establishes
cross-domain consistency and mathematical coherence, not a new law of nature or proof of universal fractality.

## Next discriminating test

Use a system whose relation can store or remove the conserved quantity. Freeze visible child accounts, hide the
native source/storage term, and require the parent residual to recover the hidden term's sign, location and
magnitude prospectively. Candidate systems are a damped spring, resistive line section or controlled open quantum
model.

## Files

- `analysis/physics_ladder/CHILD_PARENT_COMPOSITION_PROTOCOL_2026-07-23.md`
- `analysis/physics_ladder/ara_child_parent_composition_test.py`
- `analysis/physics_ladder/validate_ara_child_parent_composition.py`
- `analysis/physics_ladder/ARA_CHILD_PARENT_COMPOSITION_REPORT_2026-07-23.md`
- `analysis/physics_ladder/ARA_CHILD_PARENT_COMPOSITION_RESULTS.json`
- `analysis/physics_ladder/ARA_CHILD_PARENT_COMPOSITION_VALIDATION.json`
- `analysis/physics_ladder/ARA_CHILD_PARENT_COMPOSITION_REPORT_ARTIFACT.json`
