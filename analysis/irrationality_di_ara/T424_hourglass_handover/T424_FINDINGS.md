# T424 — Literal hourglass Irrationality Di-ARA

## Outcome

**Partial structural support; frozen prediction gate failed.**

The two independently measured child coordinates recovered the intended
packing-to-traversal-to-packing path in a held-out granular material. All 16
Toyoura-sand discharges crossed the traversal/connection equality line at least
once. The joint Di-ARA contained more event information than either child axis
alone, but it did not beat an elapsed-time-only forecast and therefore is not a
unique prospective predictor in this source.

## What was measured

| ARA term | Physical measurement |
|---|---|
| Parent identity | One upper-reservoir–throat–lower-reservoir hourglass discharge |
| Child C1 | Traversal/movement from optical flow through the throat |
| Child C2 | Connection/packing from translation-compensated texture persistence upstream of the throat |
| Irrationality Di-ARA | The joint `(C1, C2)` history, with each child independently mapped to 0–2 |
| Direct events | 16 terminal closures and one independently detected micro-jam release |

The coordinates were **not** defined as complements. On holdout they remained
strongly opposed (`r = -0.962`) but passed every frozen anti-flattening check:
the correlation was below the `0.98` ceiling, `std(C1+C2) = 0.134`, and the
complement reconstruction RMSE was `0.134`.

## Frozen holdout results

| Test | Result | Gate |
|---|---:|---|
| Runs with a C1/C2 crossing | 16 / 16 | descriptive |
| Event closeness improvement over shifted histories | 4.63% | **failed** required 20% |
| Circular-shift empirical p | 0.0224 | passed `< 0.05` |
| Joint average precision | 0.259 | beat C1, C2 and amount; **lost** to elapsed time `0.317` |
| Joint Brier score | 0.098 | **lost** to best baseline `0.073` |
| Frozen warning coverage | 17 / 17 events | passed |
| Median warning lead | 1.57 s | passed, but not independent of run age |

The primary gate was therefore not met.

## ARA interpretation

Before terminal closure, the mean quadrant occupancy was:

- connection-heavy: 79.0%;
- movement-heavy: 16.2%;
- both-low: 2.64%;
- both-high: 2.12%.

The median path began near `(0, 2)`, opened toward movement, passed through the
joint ridge neighbourhood, and returned toward connection as the discharge
ended. This is a coherent Irrationality Di-ARA trajectory rather than a fixed
neighbour-by-neighbour quadrant order.

The most interesting post-hoc diagnostic is the first independently detected
flow onset. Across the 16 holdout runs its median coordinate was:

\[
(C1,C2)=(0.5012,1.5000),\qquad (C1+C2)/2=1.0011.
\]

That is the `(0.5, 1.5)` coarse pair while the compressed parent relation sits
at the 1.0 ridge. It was not a frozen success criterion, and the onset detector
uses downstream motion from the same video, so it is evidence for a repeatable
geometric address—not yet an independent prediction.

The direct closure/release events themselves occurred later, with median
`(C1,C2) = (0.265, 1.921)`. That explains why a test aimed at final closure did
not place those events at equality: equality marks the opening handover in this
cut, while terminal closure is the return toward the connection-heavy side.

## Scientific translation

The source is a quasi-two-dimensional granular hopper in vacuum under
artificial gravity. In conventional language, the figure tracks the transfer
between a persistent packed bed and grain flux through the outlet. The gradual
fall and reclosure are strongly tied to how long each published run has been
underway; this is why elapsed time remains the better held-out event predictor.

## What this result does and does not support

It supports this operational claim:

> An independently measured packing/traversal pair organizes real hourglass
> discharge into the expected two-axis ARA geometry and transfers across a
> held-out granular material.

It does **not** yet support:

- a unique Irrationality Di-ARA prediction of terminal closure;
- a causal claim that the coordinate drives grain motion;
- a universal quadrant sequence; or
- a universal physical law inferred from one montage-style dataset.

## Best next test

Freeze a new target at the **opening handover** rather than terminal closure:
flow onset or arch-collapse/release. Use repeated flips at the same gravity and
material, so an elapsed-time clock cannot win merely because every run has a
similar duration. Retain the current C1/C2 equations and compare the frozen
coarse-pair/ridge prediction with duration-matched and circular-shift controls.

## Sources and audit trail

- S. Ozaki et al., “Granular flow experiment using artificial gravity
  generator at International Space Station,” *npj Microgravity* 9, 61 (2023):
  <https://www.nature.com/articles/s41526-023-00308-w>
- Public source movies and metadata: <https://osf.io/3zcm2/>
- Frozen protocol: `T424_FROZEN_PROTOCOL.md`
- Frozen model hash:
  `62de4692f866c60c5a1e95386eadb958fd9f6f0bcf5a6acae715ec70d8371124`

