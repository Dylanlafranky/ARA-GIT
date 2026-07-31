# Q41B cadence-defined strand reversal report

Date: 2026-07-27 (Australia/Brisbane)

Registered verdict: **NOT SUPPORTED — STRAND EXTENSION**

Secondary prospective result: **the cadence-plus-Ba coordinate strongly
improved reversal-state detection, but the proposed full-vector repair was
wrong.**

## Plain-language answer

The 7.5/15 test did tell us something real and transferable: it helped locate
the branch where the hidden relation points backwards.

It did **not** tell us that the entire relation should be reversed as
\(C_3-(C_1-C_2)\). That operation was too large or otherwise geometrically
incomplete. It identified the right kind of event much more often, while
making the reconstructed matrix worse.

So the clean conclusion is:

> The clock helps identify **where** the strand reversal occurs. It does not
> yet specify **how much** of the relation reverses or the complete target
> identity after the crossing.

## Prospective integrity

Q41B used the still-untouched
`unnati_submit_12_inhomo_v1_landmax.hdf5.zip` archive.

- Deposited and verified MD5:
  `f2e191d2f06643818c4ba64743e16238`
- Frozen protocol SHA-256:
  `78491f3c2a0d6df97f069acaa399d6bbca7172cf2d219bfa01e3948418c0631d`
- Frozen target-lock SHA-256:
  `80d0df632223a2f21b6a30aab75d7fdbbffa142fdb36aebd0e0c99e963d06ccd`
- Prediction SHA-256 written before target reveal:
  `9f95d80f317c0854924b333e77b8b971161944d5306d66a19ff4142cba12d399`

The prediction artifact contained all selected Q41B and control matrices
before the fourth connected identity was read.

## Adequacy

All registered minimum counts passed:

| Quantity | Result |
|---|---:|
| Seeds | 100 |
| Evaluation lineages with cycles | 1,006 |
| Evaluation cycles | 15,917 |
| Two-turn Ba cycles | 1,089 |
| Development cycles for the affine control | 15,256 |

Across the eligible closure population, the cadence classifier found 1,545
two-turn lineages, 669 one-turn lineages and 73 other lineages. Some eligible
lineages did not form an evaluation cycle, so these population-family counts
are larger than the 1,006 lineages contributing target scores.

## Primary reconstruction result

Seed-balanced scaled error, lower is better:

| Method | Error |
|---|---:|
| Development affine | **0.35971** |
| Q40 visible rule | **0.46517** |
| Q41B cadence + Ba | 0.51516 |
| Forward relation | 0.51676 |
| Persistence | 0.69126 |

The registered Q41B advantage over Q40 was:

\[
\Delta_{41B:40}
=E_{\rm Q40}-E_{\rm Q41B}
=-0.04999.
\]

Its 95% seed-cluster bootstrap interval was
`[-0.06827, -0.03315]`. Every part of the interval favours Q40, so the primary
gate failed decisively.

Q41B also failed the strong affine gate:

\[
\Delta_{41B:\mathrm{affine}}=-0.15545,
\]

with 95% interval `[-0.18402, -0.12752]`.

## The important split result

Although the matrix reconstruction failed, the target-blind reversal-state
diagnostic improved sharply:

| Diagnostic | Q40 | Q41B |
|---|---:|---:|
| True positives | 867 | 1,611 |
| False negatives | 877 | 133 |
| False positives | 64 | 393 |
| Precision | 0.931 | 0.804 |
| Recall | 0.497 | **0.924** |
| Specificity | **0.995** | 0.972 |
| Balanced accuracy | 0.746 | **0.948** |

In the predeclared two-turn Ba subset:

- 1,089 cycles were present;
- 68.32% actually had negative orientation relative to the forward relation;
- Q40 flagged only 1.47%; and
- Q41B flagged all of them by construction.

This prospectively confirms the Q40C localization: the two-turn Ba coordinate
is strongly enriched for the missed reversal state. But assigning the full
reverse matrix to every member of that coordinate increased scaled error by
`0.6645` within the subset.

## ARA interpretation

The recovered clock is a **state/location coordinate**, not yet a complete
coupling law.

In ARA language, the 7.5/15 closure plus Ba identifies the strand on the far
side of the local seam. The null says that crossing the seam cannot be
represented by simply negating the whole visible relation \(D\). The target
may contain:

- a partial reversal rather than a full reversal;
- a rotation of the relation in the unobserved dimension;
- strand-dependent amplitude;
- an additional child contribution; or
- a mixture of those effects.

Those possibilities are new hypotheses. They cannot be used to repair Q41B
after seeing this target.

## What the result changes

Supported:

- the 7.5/15 cadence is transferable across structured greedy and landmax
  ordering archives;
- two-turn Ba is a strong prospective locator of hidden negative orientation;
- Q40's failure was genuinely concentrated in a strand/crossover state.

Not supported:

- “two-turn Ba” implies the exact full-vector operator
  \(C_3-(C_1-C_2)\);
- the clock alone reconstructs the fourth connected identity; or
- the strand extension beats Q40 or the development-affine baseline.

## Validation

The independent validator recomputed all 15,917 targets and every stored
matrix metric:

- status: `PASS`;
- arithmetic mismatches: `0`;
- recomputed Q41B-over-Q40 advantage: `-0.0499918706`; and
- recomputed prediction SHA-256 matched the pre-reveal hash.

Primary artifacts:

- `Q41B_CADENCE_STRAND_REVERSAL_RESULTS.json`
- `Q41B_CADENCE_STRAND_REVERSAL_CYCLES.csv.gz`
- `Q41B_CADENCE_STRAND_REVERSAL_DIAGNOSTICS.png`
- `Q41B_CADENCE_STRAND_REVERSAL_VALIDATION.json`

