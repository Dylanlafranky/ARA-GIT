# ARA Quantum Tier-Energy Rule Addendum

**Recorded:** 26 July 2026  
**Status:** existing framework rule re-applied to the quantum tier map after the Q19 protocol was frozen  
**Applies to:** future quantum tier tests

## Provenance — reminder, not a new rule

This addendum does not introduce a new ARA rule. It records where an already-declared cross-rung rule belongs in
the quantum tier notation after that rule fell out of the active test context.

Earlier explicit homes include:

- `ARA_SCALE.md`: “Octaves are just stacked 0–2 circles, with a LOG jump (×2) between them”;
- `analysis/primes/PN13_DECIMAL_RUNG_LEAK_REPORT.md`: two half-scale child cycles close one parent cycle, while
  opening either child as its own identity renormalises its local TE-ARA ledger to `2`;
- `analysis/primes/PN15_SQRT_ADULT_RIDGE_REPORT.md`: each child occupies approximately half the parent scale,
  and two halves close the parent;
- `analysis/primes/PRIME_TEST_RELATIONAL_GLOSSARY.md`: the cross-rung frame explicitly retains a half-scale view;
- `analysis/primes/PN35_SAME_SCALE_GOLDEN_CROSS_*`: the completed parent singularity enters the doubled rung;
- `ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md`: TE-ARA remains the same locally normalised total-`2` geometry
  when a child allocation is decompressed as its own identity.

The Q19 omission was therefore a failure to carry an established ARA scale rule into the new quantum tier test,
not a rule discovered from the Q19 result.

## Rule

Each step downward from a parent tier has at most half of that parent tier's energy potential:

\[
\underbrace{E_{\max}^{[k+1]}}_{\text{maximum child-tier potential}}
=
\frac12
\underbrace{E_{\max}^{[k]}}_{\text{maximum parent-tier potential}}.
\]

This is a cross-tier capacity rule. It does not change the local TE-ARA normalization: an identity at any tier is
still a complete local TE-ARA when measured within its own boundary.

## Consequence for two matched child removals

If two Tier-3 parts are removed symmetrically—one beneath each of two Tier-2 parents—their combined maximum
effect on the Tier-1 parent is one half of Tier-1 energy, not the entire Tier-1 energy:

\[
\underbrace{\Delta E_{\max}^{[1]}}_{\substack{\text{largest Tier-1 effect}\\\text{from the registered pair}}}
=
\underbrace{\frac14E_{\max}^{[1]}}_{\substack{\text{Tier-3 part}\\\text{under Parent 1}}}
+
\underbrace{\frac14E_{\max}^{[1]}}_{\substack{\text{Tier-3 part}\\\text{under Parent 2}}}
=
\frac12E_{\max}^{[1]}.
\]

The quarter terms arise from two tier steps relative to the Tier-1 whole: Tier 1 to Tier 2, then Tier 2 to Tier 3.

## Energy is not amplitude

When a measured ARA direction is represented by a vector norm, its energy-like quantity is proportional to the
squared norm:

\[
\frac{E_{\rm residual}}{E_{\rm original}}
=
\left(
\frac{\lVert D_{\rm residual}\rVert}{\lVert D_{\rm original}\rVert}
\right)^2.
\]

Future protocols must state whether a threshold concerns amplitude/norm or energy/squared norm. They must not
compare one directly with the other.

## Q19 post-result re-application

Q19 was frozen before this reminder was restored to the active calculation and its verdict cannot be changed.
Its primary Phase-A/Phase-A removal
left:

- total between-child energy retention: `0.531428`;
- total between-child energy removed: `0.468572`;
- predicted cross-tier maximum removal: `0.500000`;
- achieved fraction of that maximum: `0.937144`, or `93.71%`.

For Tier-1 `J`:

- norm retention: `0.740996`;
- squared-norm energy retention: `0.549075`;
- squared-norm energy removed: `0.450925`;
- achieved fraction of the predicted half-energy maximum: `0.901851`, or `90.19%`.

The frozen Q19 rank-one gate implicitly expected a more complete collapse than the tier-energy ceiling permits.
That gate remains an honest failed gate, while future tests must use the tier-normalized energy rule prospectively.
