# T302 — empirical Phi handover in ordered plant phyllotaxis

**Run:** 30 July 2026  
**Frozen verdict:** **MIXED / SUGGESTIVE — 2/4 gates**  
**Status boundary:** empirical calibration/retrodiction, not blind discovery  
**Independent validation:** **16/16 checks passed**

## Outcome first

Ordered Arabidopsis leaf placements were the best available public Phi
calibration because the data contain successive measured placements and two
biological perturbation controls.

The result separates two scales:

1. **Local child step:** exact Phi was not the best fixed description.
   `3/8` had slightly lower one-step error.
2. **Longer parent carrier:** exact Phi was the best fixed rule for cumulative
   circular position across several placements.

This is a useful ARA-shaped result, but not a full confirmation. It suggests
that individual children can move around a longer Phi-like carrier; it does
not show that every child placement equals Phi or that Phi is a universal
handover constant.

## Public source

Tameshige et al. (2025), “Mutual inhibition between EPFL2 and auxin extends
the intervals of periodic leaf morphogenesis,” *Nature Communications*,
DOI [`10.1038/s41467-025-65792-y`](https://doi.org/10.1038/s41467-025-65792-y).

The checksum-locked
[publisher source-data archive](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-65792-y/MediaObjects/41467_2025_65792_MOESM9_ESM.zip)
contains Source Data 21:

- `359` successive divergence-angle measurements;
- `58` meristems/plants;
- `21` wild-type `Col`, `19` `e2`, and `18` `e1e2`;
- exact within-plant sequence reconstruction from the recorded meristem index.

## ARA cut

For each measured angle \(\theta\):

\[
\underbrace{x_A}_{\substack{\text{measured placement}\\\text{on the A side}}}
=
\underbrace{\frac{\theta}{360^\circ}}_{\substack{\text{fraction of one}\\
\text{complete turn}}}.
\]

Exact Phi on this directed half is:

\[
x_\phi=\phi^{-2}=0.38196601125
\quad\Longleftrightarrow\quad
137.507764^\circ.
\]

The reverse coordinate

\[
x_B=2-x_A
\]

is an **assigned ARA mirror**, not a second measurement. It cannot supply
independent evidence.

## Frozen results

| Gate | Frozen requirement | Result | Pass? |
|---|---|---:|:---:|
| P1 | confirmation wild type within `0.01` of \(\phi^{-2}\) | `x_A = 0.387492`; distance `0.005526` | yes |
| P2 | exact Phi has lowest one-step error among fixed rivals | `3/8 = 6.743°`; Phi `= 6.986°` | no |
| P3 | exact Phi has lowest cumulative-position error among fixed rivals | Phi `= 5.429°`; `8/21 = 6.524°`; `3/8 = 10.239°` | yes |
| P4 | wild type beats both mutants and ordered data beat shuffled order | genotype direction passed; shuffle `p = 0.1582` | no |

The wild-type confirmation center was about `139.497°`, approximately
`1.989°` above the exact golden angle. It was near the declared ARA landmark,
but that alone is expected from the source context and cannot count as a
discovery.

## Plain-language reading

If each new leaf were required to take one perfectly fixed step, `3/8` was
slightly closer to the typical local step than exact Phi. But when those
small errors were allowed to accumulate through several placements, Phi kept
the overall position on track better than every other fixed constant tested.

In ARA language: the **children do not each sit exactly on Phi**, yet the
**parent path can still carry a Phi-like relation**. A child can land a little
above the carrier and the next child a little below it, keeping the longer
trajectory closer to Phi than either child alone suggests.

The perturbation result was directionally encouraging: median confirmation
clearance was `0.7392` in wild type, `0.7099` in `e2`, and `0.6666` in
`e1e2`. However, the actual wild-type order did not beat within-plant shuffled
orders at the frozen `p < 0.05` threshold. Therefore this run does **not**
establish the proposed “do not reoccupy previous space” mechanism.

## Post-result child/parent clue

This analysis was secondary and does not alter the frozen `2/4` verdict.

In confirmation wild type, adjacent signed errors around exact Phi were
negatively related:

\[
\rho=-0.5356,
\qquad
p_{\text{within-plant order shuffle}}=0.00060.
\]

The typical absolute error of one child was `0.01859` turns. After averaging
two adjacent children, the error fell to `0.00798` turns, or about `42.9%` of
the individual-child error.

The same direction appeared in development wild type:

\[
\rho=-0.4953,
\qquad
p=0.00270,
\qquad
\text{pair/child error ratio}=0.4249.
\]

Plainly: a step above Phi tended to be followed by a step below Phi. That
compensation is not created by the assigned `2-x` mirror. It offers a concrete
reason exact Phi can lose the local-step contest while winning the cumulative
carrier contest.

This clue is **post hoc**. Its next scientific use is a frozen replication on
an independent ordered phyllotaxis dataset.

## Post-result ARA interpretation of the `3/8` child

Dylan identified the local `3/8` winner as a possible
**connection-form of Phi**: a rational, closing child expression beneath a
non-closing parent carrier.

The proposed geometry is mathematically explicit:

\[
\underbrace{\frac38+\frac38+\frac38}_{\substack{\text{three local}\\
\text{child advances}}}
=
\underbrace{\frac98}_{\substack{\text{one closed }8/8\text{ turn}\\
\text{plus }1/8\text{ into the next cycle}}}.
\]

This is not interchangeable with exact Phi. Their one-step separation is

\[
\phi^{-2}-\frac38
=0.00696601125
=2.507764^\circ.
\]

The interpretation is therefore:

\[
\underbrace{\frac38}_{\substack{\text{local rational child}\\
\text{connection/closure form}}}
\longrightarrow
\underbrace{\phi^{-2}}_{\substack{\text{longer non-closing parent}\\
\text{traversal/carrier form}}}.
\]

T302 establishes only that `3/8` wins the local-step endpoint while Phi wins
the cumulative endpoint. It did not freeze or test the specific
`3 + 3 + 3 = 9` three-child operator. That operator is now a recorded
post-result hypothesis for an independent sequence: compare the observed
three-child residual with the `1/8` residual predicted by `3/8`, the
`0.145898...` residual predicted by exact Phi, and fixed rival steps.

## Controlled mathematical benchmark

When fixed generators were compared over horizons `N=4...55`, Phi was a
strong low-recurrence circle generator but not uniquely best under every
spacing score. This agrees with the empirical distinction:

- supplied Phi is very good at maintaining distributed coverage through time;
- nearby irrational rules can also avoid recurrence;
- a good generator benchmark is not evidence that a biological system uses
  that generator.

## What this adds to ARA

The strongest supported interpretation is narrower than “Phi is every
handover”:

> In this ordered biological system, exact Phi is a better fixed
> **multi-step carrier** than a fixed **single-child step**. Local children
> alternate around the carrier and partially cancel when coarse-grained.

That is compatible with the framework's parent/child distinction and gives
the Phi idea a clearer scale assignment. It is not proof of the complete ARA
sphere, TE-ARA energy allocation, universal fractality, or a causal Phi
mechanism.

## Reproduction

From `analysis/phi_calibration`:

```powershell
python t302_phi_phyllotaxis.py
python validate_t302_phi_phyllotaxis.py
```

The analysis downloads and verifies the public source automatically.
Archive SHA-256:

`1D93DE8B177F7556525DBCA07D34F1D40880DA33F68DC44ECCF93BBC7CB0D563`

Workbook SHA-256:

`E78372214B1386A486B25C8340C19F22BC74D3382F80A9B36A2972CC3D35ADFB`

The validator independently reproduced source integrity, plant sequences,
event coordinates, all four frozen endpoints and all five visualization
panels: `16/16` checks passed.
