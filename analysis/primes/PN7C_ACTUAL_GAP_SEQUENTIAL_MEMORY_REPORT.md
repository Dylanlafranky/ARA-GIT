# PN7C actual-prime gap sequential-memory report

**Test ID:** `PN7C/ACTUAL-GAP-SEQUENTIAL-MEMORY/CODE-ISOLATED-R11-v1`  
**Status:** `ARRIVAL MEMORY TRANSFERS / BEYOND SHARED OVERLAP / NOT BEYOND FIRST-ORDER RAW-GAP CONTROL / 5 OF 7 PASS / RESIDUAL CORE FAILS`  
**Independent validation:** `43/43` checks passed, including an exact R11 rebuild with different segment boundaries  
**Protected material:** the p31 primorial wheel and R12 remain unopened

## TL;DR

PN7C asked whether knowing **how the sequence arrived at the current ARA state** helps predict the next actual-prime
gap state.

Yes, strongly. On 39,475,587 code-isolated R11 prediction events, the two-state ARA model improves cross-entropy by
`0.118054` bits per reading over the one-state ARA model. The improvement occurs in all 100 contiguous R11 blocks
and remains positive at 12, 24 and 48 bins. It also improves Brier score and top-3 accuracy.

That improvement is not merely the unavoidable effect of neighbouring ARA readings sharing one prime gap. R11's
empirical conditional-memory gain is `0.121900` bits, while the largest of five exact-gap-inventory shuffles is
`0.101432` bits. The observed ordering therefore adds `0.020467` bits beyond the registered overlap-only ceiling.

The stricter control changes the conclusion. A first-order raw-gap Markov world produces `0.118849` bits of the same
conditional-memory gain. The real record exceeds it by only `0.003051` bits, below the predeclared `0.010` margin.
The exact one-step raw-gap model also predicts the next ARA bin better than compressed ARA-M2: `3.621871` versus
`4.112585` bits per reading.

Therefore P1-P4 and P7 pass; P5-P6 fail. The residual ordered-memory core P1-P5 fails.

Plainly: the local three-reading ARA shape is real, repeatable and predictively useful. Actual gap order contains
more structure than a shuffled gap inventory. But this test does not establish that the remaining structure is a
separate larger wave or memory law beyond ordinary one-step dependence between exact prime gaps. It also does not
test the proposed slow adult wave across distant number-line scale; PN7C is a local sequential test.

## What was measured

Let consecutive actual-prime gaps be

\[
\underbrace{g_i}_{\text{one actual-prime traversal gap}}
=p_{i+1}-p_i.
\]

Each pair of adjacent gaps gives the direct node-centred ARA reading retained from PN7B:

\[
\underbrace{x_i}_{\substack{\text{ARA location}\text{on the 0--2 diameter}}}
=
\frac{2\underbrace{g_{i+1}}_{\text{outgoing side}}}
{\underbrace{g_i}_{\text{incoming side}}+\underbrace{g_{i+1}}_{\text{outgoing side}}}.
\]

The predictive relation is

\[
\underbrace{x_{i-1}}_{\substack{\text{arrival origin}\text{where it came from}}}
\longrightarrow
\underbrace{x_i}_{\substack{\text{current ARA state}\text{where it is}}}
\longrightarrow
\underbrace{x_{i+1}}_{\substack{\text{next ARA state}\text{what is predicted}}}.
\]

Plainly: the first reading records the direction of arrival, the second fixes the current local relation, and the
third is the next relation to predict. This is a three-point ARA stencil. It is not automatically Information³:
that stronger name requires two identified information sources and their retained coupling relation.

## Frozen separation and integrity

The protocol was written and hashed before constructing any PN7C development or target gap sequence. The exact order
was:

1. freeze the question, models, controls, thresholds and data windows;
2. construct only R9 and R10 development gaps;
3. fit and hash every model;
4. create a target builder that verifies the frozen model hash;
5. then construct and score R11.

| Use | Rung | Interval | Actual primes | Internal gaps |
|---|---:|---:|---:|---:|
| Development | R9 | `[1,000,000,000, 1,010,000,000)` | 482,449 | 482,448 |
| Development | R10 | `[10,000,000,000, 10,100,000,000)` | 4,341,930 | 4,341,929 |
| Evaluation | R11 | `[100,000,000,000, 101,000,000,000)` | 39,475,591 | 39,475,590 |

No outside prime closed a window boundary, and no R9-R10 boundary transition was fitted. R9/R10 counts reconcile
exactly with PN3A/PN5; R11 reconciles exactly with PN6. The frozen model packet is
`9141AA398C6A6694C3C5F3ECA954681D4AD8091C01310D13C6703DB30668F3A2`.

R11 was historically opened in earlier prime tests. Code isolation prevents PN7C target tuning, but it does not make
the result blind.

## The four frozen predictors

At the primary 24-bin grain:

- **ARA-IID** knows only how common each next ARA state was in R9-R10.
- **ARA-M1** knows the current ARA state: `P(x_next | x_current)`.
- **ARA-M2** knows arrival plus current state: `P(x_next | x_previous, x_current)`.
- **RawGap-M1** knows the exact shared current gap and its one-step transition law, then projects the predicted next
  gap through the same ARA coordinate.

The raw control is intentionally stronger in local numerical detail. ARA-M2 retains two dimensionless relational
readings but discards absolute gap scale. RawGap-M1 retains that scale but only one raw transition. P6 asked whether
ARA's compression nevertheless predicted better.

## Predictive transfer to R11

### Primary 24-bin result

| Frozen model | Cross-entropy (bits) | Perplexity | Brier | Top-1 | Top-3 |
|---|---:|---:|---:|---:|---:|
| ARA-IID | 4.496676 | 22.5753 | 0.953978 | 6.475% | 17.911% |
| ARA-M1 | 4.230639 | 18.7737 | 0.939698 | 9.218% | 25.311% |
| **ARA-M2** | **4.112585** | **17.2986** | **0.933152** | **10.421%** | **27.952%** |
| **RawGap-M1** | **3.621871** | **12.3110** | **0.907127** | **14.405%** | **36.316%** |

Arrival direction improves the ARA model by

\[
\underbrace{4.230639}_{\substack{\text{current state only}\text{ARA-M1}}}
-
\underbrace{4.112585}_{\substack{\text{arrival + current}\text{ARA-M2}}}
=
\underbrace{0.118054\ \text{bits}}_{\text{transferred arrival-memory gain}}.
\]

P1 passes by more than ten times its `0.010` threshold. All 100 fixed blocks are positive. The block bootstrap interval
is `[0.117877, 0.118234]` bits, so P2 passes. ARA-M2 improves both Brier and top-3 accuracy over ARA-M1, so P7 passes.

### Measurement-grain recurrence

| ARA bins | ARA-M1 CE | ARA-M2 CE | M1 − M2 gain |
|---:|---:|---:|---:|
| 12 | 3.303480 | 3.212182 | +0.091298 |
| 24 | 4.230639 | 4.112585 | +0.118054 |
| 48 | 5.081456 | 4.872646 | +0.208810 |

The direction is positive at every frozen grain, so P3 passes. A finer grain contains more distinguishable arrival
contexts, hence the larger bit gain; this does not mean the underlying physical effect grew.

## What the controls remove

### Shared-gap overlap control

Consecutive readings mechanically share a gap:

\[
x_i=f(g_i,g_{i+1}),
\qquad
x_{i+1}=f(g_{i+1},g_{i+2}).
\]

Even a shuffled gap inventory therefore creates apparent memory. Five fixed R11 shuffles preserve every gap and the
overlap construction while destroying actual order.

| Record | Conditional-memory gain (bits) |
|---|---:|
| Observed R11 | **0.121900** |
| Shuffle 1 | 0.101195 |
| Shuffle 2 | 0.101238 |
| Shuffle 3 | 0.101432 |
| Shuffle 4 | 0.101315 |
| Shuffle 5 | 0.101249 |

Observed minus the maximum shuffle is `0.020467` bits, above the `0.010` threshold. P4 passes. Actual gap order adds
structure beyond the shared-gap geometry alone.

### First-order raw-gap control

The stricter world retains both overlap and the fitted one-step raw-gap transition:

\[
g_0\to g_1\to g_2\to g_3,
\]

then projects each of 10,000,000 independent four-gap paths into the same three overlapping ARA readings. Its
conditional-memory gain is `0.118849` bits.

\[
\underbrace{0.121900}_{\text{observed R11}}
-
\underbrace{0.118849}_{\substack{\text{first-order raw-gap}\text{Markov world}}}
=
\underbrace{0.003051\ \text{bits}}_{\substack{\text{residual}\<0.010\text{ requirement}}}.
\]

P5 fails. The visible local arrival memory is almost reproduced by ordinary one-step dependence between exact gaps
after the same nonlinear overlapping ARA projection.

## Why the raw-gap model wins P6

ARA-M2 is a deliberate compression. The pair of binned ratios tells us how neighbouring gaps compare, but not their
absolute magnitudes. For example, proportional triples can occupy the same ARA contexts while having very different
exact gaps. The raw model knows the exact current magnitude, which matters for the distribution of the next prime
gap. It wins by `0.490714` bits per reading at 24 bins, so P6 fails.

This does not erase the ARA result. The compressed relation still transfers, is distributed across all blocks, and
beats its own one-state form. It does mean that the tested ARA coordinate is not a sufficient statistic for
next-gap prediction and does not outperform the best frozen local raw-data control.

## Registered outcome

| Condition | Result | Meaning |
|---|---|---|
| P1 | **PASS** | Arrival improves transferred ARA prediction by at least 0.010 bits |
| P2 | **PASS** | Improvement is distributed, not isolated |
| P3 | **PASS** | Direction recurs at 12, 24 and 48 bins |
| P4 | **PASS** | Observed memory exceeds shared-overlap shuffles |
| P5 | **FAIL** | Residual over first-order raw-gap world is below 0.010 bits |
| P6 | **FAIL** | Exact RawGap-M1 predicts better than compressed ARA-M2 |
| P7 | **PASS** | ARA-M2 improves Brier and top-3 over ARA-M1 |

The residual ordered-memory core P1-P5 therefore fails. Five of seven individual conditions pass.

## What this implies for the ARA framework

Supported here:

- the direct incoming/outgoing ARA state retains sequential information;
- the direction of arrival matters for the next local relation;
- that benefit transfers from R9-R10 to R11 and is stable throughout R11;
- actual gap order contributes more than shared overlap alone;
- the effect recurs across three fixed measurement grains.

Not supported here:

- a substantial residual local memory beyond a first-order exact-gap process;
- superior predictive sufficiency of the compressed ARA coordinate;
- a separate adult Time wave, physical wave cause, or exact prime-location generator.

Most importantly for Dylan's current geometric diagnosis, PN7C tested the **local child handover** among consecutive
gaps. It did not test a slow parent coordinate spread across many primes or across the number-line rung. Failure of
P5 therefore constrains the local-memory claim; it neither demonstrates nor refutes that larger proposed axis.

## Implementation note

The first scoring execution stopped before writing a result because the raw marginal initially omitted the
protocol's frozen `alpha=0.5` categorical smoothing over gap values `1..1024`. Rare R11 gaps absent from R9-R10 then
received zero probability and made raw cross-entropy infinite. The implementation was corrected to apply the already
registered smoothing rule; no model count, ARA result, threshold, control, target or criterion changed. The complete
scorer was rerun, and only the corrected run is recorded. This preserves the scientific distinction between fixing
a protocol implementation and changing a protocol after seeing a result.

## Validation and files

The independent validator does not import the scorer. It:

- reconstructs all R11 primes with a different segment size and matches every stored gap exactly;
- recomputes all five primary metrics for all four 24-bin models;
- recomputes all 100 block gains and the observed conditional-memory value;
- repeats all five seeded shuffles and the 10-million-path Markov world;
- reconstructs P1-P7 and the failed residual core.

All `43/43` checks pass. The static figure was inspected at its native `1500×960` resolution. The executed notebook
provides a lightweight, reviewable companion; the scripts and hashed binary packets hold the full reconstruction.

## Allowed concise claim

> On code-isolated R11 actual-prime gaps, adding arrival direction to the current ARA state improves next-state
> prediction by 0.118 bits per reading throughout the record and exceeds matched shared-overlap shuffles. However,
> the residual over a first-order raw-gap Markov world is only 0.003 bits—below the registered threshold—and the
> exact raw-gap predictor outperforms compressed ARA-M2. PN7C therefore supports local ARA sequential structure but
> not a distinct residual memory law beyond one-step raw-gap dynamics.

