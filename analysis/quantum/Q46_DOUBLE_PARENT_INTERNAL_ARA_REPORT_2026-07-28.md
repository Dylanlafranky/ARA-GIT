# Q46 — ARA of the two complete local parents

Date: 28 July 2026  
Status: **coarse parent ridge supported for this measured cut**  
Evidence tier: descriptive decomposition of an already-open archive

## Answer first

Dylan's approximately `42%` expectation appears numerically:

\[
\underbrace{0.58917}_{\substack{\text{local-parent}\\\text{strand }L}}
+
\underbrace{0.41083}_{\substack{\text{connected}\\\text{child }C}}
=1.
\]

The connected-child result is `41.08%`, only `0.92` percentage points from
`42%`. This is an accurate accounting description of the measured movement
cut, but it is not independent evidence: Q45 had already measured the
`58.92%` \(L\) share, and the two shares use the same denominator.

The genuinely new Q46 result is inside \(L\). The two local parents occupy a
coarse same-tier ridge:

\[
\underbrace{x_1}_{P_1}=1.0392,
\qquad
\underbrace{x_2}_{P_2}=0.9608.
\]

When lifted into their shared 3×3 relation space, their unsigned movement
shares were approximately:

\[
\underbrace{53.68\%}_{P_1}
\;+\;
\underbrace{45.76\%}_{P_2}
\;+\;
\underbrace{0.46\%}_{\text{handover Other}}.
\]

The separately seed-balanced medians need not sum to exactly 100%, although
every individual window closes exactly.

## Plain-language interpretation

The double-parent picture is more precise than simply calling \(L\) the
missing half:

1. \(P_1\) and \(P_2\) are two complete local identities at the same
   measurement tier.
2. Their joint local-product strand \(L=P_1P_2^{\mathsf T}\) supplies about
   `58.9%` of the movement visible on the measured double-parent cut.
3. The connected child \(C\) supplies the remaining `41.1%`.
4. Inside \(L\), the two parents contribute nearly equally in the pooled
   account, with only about `0.46%` assigned to the simultaneous handover
   term.

Thus the `41.1%` is not the full TE-ARA of the double parent. It is the
connected-child participation visible beside the local-parent strand on this
one relation cut.

## Important internal asymmetry

The pooled parent coordinate is close to the `1.0` ridge, but the individual
windows are not generally balanced. The seed-balanced mean absolute distance
from the ridge was

\[
|x_1-1|=|x_2-1|\approx0.390.
\]

Plainly: which parent leads changes across windows. Those opposite local
asymmetries cancel when compressed into the coarse parent account, leaving a
near-`1.0` ridge. This is the same parent-ridge/hidden-child-asymmetry problem
already encountered elsewhere in ARA. The correct claim is therefore
**coarse parent ridge**, not pointwise equality of the parents.

Across the four frozen 15-cycle quadrants, the pooled \(P_1\) shares were:

| Parent quadrant | \(P_1\) movement share |
|---|---:|
| Ab | `0.5000` |
| aB | `0.5392` |
| bA | `0.4898` |
| Ba | `0.5000` |

The small shift in `aB` is descriptive because the quadrant seed counts are
only `5–13`.

## Side-by-side translation

| ARA reading | Established quantum representative |
|---|---|
| Complete local parent \(P_1\) | Local Bloch vector \(a\) |
| Complete local parent \(P_2\) | Local Bloch vector \(b\) |
| Coupled local-parent strand | \(L=ab^{\mathsf T}\) |
| Connected child relation | \(C=T-ab^{\mathsf T}\) |
| Measured double-parent cut | \(T=C+L\) |
| Handover Other inside \(L\) | \((\Delta a)(\Delta b)^{\mathsf T}\) |

The exact product-rule decomposition is:

\[
\Delta L
=
\underbrace{(\Delta a)b^{\mathsf T}}_{P_1\text{ carried through }P_2}
+
\underbrace{a(\Delta b)^{\mathsf T}}_{P_2\text{ carried through }P_1}
+
\underbrace{(\Delta a)(\Delta b)^{\mathsf T}}_{\text{simultaneous handover}}.
\]

Raw spot checks reconstructed this identity to approximately `1.04e-16`.

## Method

- Source: public Q44 12-qubit simulator archive, MD5
  `08b2eaa89268952f7e197eecb2ea9610`.
- Population: the unchanged Q45 eligibility list, `79` lineages across `17`
  seeds.
- Evaluation: `1,264` non-overlapping 15-sample windows.
- Parent coordinates were calculated directly from the raw density matrices.
- Summaries were balanced by seed with `20,000` bootstrap draws.
- The protocol and approximately `42%` expectation were frozen before the
  \(P_1/P_2\) trajectories were opened.

## Validation

Every automated validation check passed:

- protocol and archive hashes;
- window, lineage and seed counts;
- finite-value and share-closure checks;
- independently recomputed point summaries;
- swap invariance;
- exact product-rule reconstruction;
- three raw-density-matrix spot checks; and
- PNG/SVG existence and visual inspection.

## Boundaries

Q46 does not show that:

- the Bloch vectors are the complete physical parent spheres;
- the `41.1%` connected share is a universal constant;
- TE-ARA is literal physical energy;
- the complete double-parent sphere has been tomographically recovered; or
- the Q45 candidate is now independently replicated.

The strict interpretation is:

> The measured double-parent cut contains a `58.9%` local-parent strand and a
> `41.1%` connected-child strand. Inside the local-parent strand, the two
> parents form a coarse near-ridge pair while retaining substantial local
> asymmetry that cancels under aggregation.

## Artifacts

- `Q46_DOUBLE_PARENT_INTERNAL_ARA_PROTOCOL_v1_FROZEN.md`
- `Q46_DOUBLE_PARENT_INTERNAL_ARA_RESULTS.json`
- `Q46_DOUBLE_PARENT_INTERNAL_ARA_WINDOWS.csv.gz`
- `Q46_DOUBLE_PARENT_INTERNAL_ARA_VALIDATION.json`
- `Q46_DOUBLE_PARENT_INTERNAL_ARA_DIAGNOSTICS.png`
- `Q46_DOUBLE_PARENT_INTERNAL_ARA_DIAGNOSTICS.svg`
- `q46_double_parent_internal_ara_test.py`
- `q46_validate_double_parent_internal_ara.py`

