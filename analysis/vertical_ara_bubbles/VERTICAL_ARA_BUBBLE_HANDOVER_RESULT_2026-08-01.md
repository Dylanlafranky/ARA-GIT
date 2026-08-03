# Vertical ARA bubble handover result

**Date:** 1 August 2026  
**Status:** PHI AREA-RATIO CLAIM NOT SUPPORTED IN THIS DATASET; VERTICAL ARA AND TEMPORAL-HANDOVER CLAIMS REMAIN OPEN

## Answer first

This frozen test did **not** support \(\phi\) as the specific area ratio of a
direct bubble child-to-parent handover. More importantly, the recovered
families did not sample the intended comparison region: even the broadest
frozen detector found no family whose two registered vertical legs were both
within 20% of \(\phi\).

The observed events were mostly a large bubble absorbing a much smaller
contour. Under the primary detector, the evaluation child-area ratio ranged
from `4.335` to `263.346` (median `31.987`), while the parent usually retained
the large child's scale (median parent/larger-child ratio `0.982`). These are
strongly asymmetric absorptions rather than approximately balanced
same-lineage closures in the target interval from 1 to 2.

The result therefore rejects a claim about **this measured coordinate in this
population**. It does not reject Vertical ARA as same-lineage recurrence, and
it does not test the distinct proposal that \(\phi\) belongs to handover
timing, boundary motion or another path coordinate.

## ARA interpretation retained by the test

The test used the following distinction:

- **Vertical ARA:** the same branch or phase lineage repeated across scale,
  here operationalized as two child bubbles becoming one persistent parent.
- **Temporal recurrence:** that same branch carried through successive time
  slices. Time does not require a different geometry; it is the lineage
  replicated in time, with each slice providing the next relational state.
- **Phi handover subset:** the narrower hypothesis that the transition has a
  distinguished \(\phi\)-related coordinate.

Thus the framework-level statement and the tested numerical statement are
not identical. A shared generative relation may appear in both vertical scale
inheritance and temporal recurrence, but the coordinate must be declared.
This experiment declared **observed 2D area ratio**. A null result there cannot
be silently moved to timing, but neither can it falsify timing.

## Public source and split

The source was the public dataset
[Bubble dynamics data for oscillating gas flow in a quasi-2D fluidized bed](https://doi.org/10.5281/zenodo.15102957):

- 35 one-minute contour CSV files;
- 50 frames per second;
- quasi-2D fluidized-bed bubbles;
- `V01-V07` for calibration of identity reconstruction;
- `V08-V28` for evaluation;
- `V29-V35` as an untouched holdout.

Phi proximity and outcomes were not used to define the lineage detector.

## Frozen measurement

For each accepted two-child-to-one-parent family:

\[
r_1=\frac{\text{larger child area}}{\text{smaller child area}},
\qquad
r_2=\frac{\text{parent area}}{\text{larger child area}}.
\]

Distance from a registered target \(\tau\) was

\[
D_\tau=
\sqrt{
\log^2\!\left(\frac{r_1}{\tau}\right)+
\log^2\!\left(\frac{r_2}{\tau}\right)
}.
\]

The fixed competitors were \(1\), \(\sqrt2\), \(1.5\), \(\phi\) and \(2\).
The registered outcomes were parent circularity tension, settling time and
parent persistence. One-sided significance was estimated with 5,000
permutations blocked within source video.

## Event recovery and coverage

| Detector | Calibration | Evaluation | Holdout | Total | Both legs within 20% of Phi |
|---|---:|---:|---:|---:|---:|
| Strict | 6 | 5 | 3 | 14 | 0 |
| Primary | 26 | 58 | 19 | 103 | 0 |
| Broad | 57 | 150 | 42 | 249 | 0 |

The minimum child-area ratio was `4.335` in primary evaluation and `7.637`
in primary holdout. Even the broad detector's minimum ratios were `2.685`
and `4.539`. The dataset therefore offered no direct leverage for choosing
Phi over the other targets between 1 and 2.

## Frozen outcomes

### Circularity tension

- Primary evaluation at Phi: \(\rho=0.3494\), blocked one-sided
  \(p=0.5323\).
- Primary holdout at Phi: \(\rho=0.4491\), \(p=0.02559\).
- The holdout \(\rho\) and \(p\) were exactly the same for every fixed target
  from 1 through 2.
- The free evaluation optimum was 1.0, not Phi.

The holdout contains a real-looking relation between size asymmetry and shape
tension, but it is a **generic asymmetry signal**. Because every observed
child ratio lies above the comparison range, every target gives the same
ranking of events.

### Settling time

- Primary evaluation at Phi: \(\rho=0.0870\), \(p=0.2985\).
- Primary holdout at Phi: \(\rho=-0.1389\), \(p=0.6297\).
- The free evaluation optimum was `1.6525`, numerically near Phi, but its
  association was negligible in evaluation and reversed in holdout.

This outcome does not support the prediction.

### Parent persistence

- Primary evaluation at Phi: \(\rho=0.0136\), \(p=0.9332\).
- Primary holdout at Phi: \(\rho=-0.3975\), \(p=0.9314\).

This outcome also failed the registered direction.

## Verdict

1. **Phi as the direct child/parent area-ratio handover is not supported by
   this dataset.**
2. **No Phi-specific comparison was available**, because no frozen detector
   recovered events near the registered region.
3. **Generic asymmetry may matter:** more asymmetric families had more shape
   tension in the holdout, but this relation could not distinguish any target
   between 1 and 2.
4. **Vertical ARA remains a broader structural hypothesis.** This result
   tests one operationalization, not the existence of same-lineage recurrence.
5. **Time remains a separate measurement axis of the same proposed branch.**
   The claim that time is the branch replicated through successive slices is
   coherent with the detector, but Phi in timing was not tested here.

## Stronger next test

Use labelled, controlled bubble or droplet coalescence in which initial child
size ratios deliberately span 1 to 2 and densely sample Phi. Freeze two
coordinates separately:

1. **vertical/scale coordinate:** child-to-parent size closure;
2. **temporal coordinate:** same-phase handover time or boundary-path length.

Then test whether one common Phi rule predicts post-merger relaxation or
re-separation better than \(1\), \(\sqrt2\), \(1.5\), \(2\), and a fitted
target on a labelled holdout set.

## Reproduction and integrity

- Frozen hypothesis protocol:
  `FROZEN_PROTOCOL_VERTICAL_ARA_BUBBLE_HANDOVER_2026-08-01.md`
- Frozen identity detector:
  `FROZEN_LINEAGE_DETECTOR_2026-08-01.md`
- Analysis script: `work/run_vertical_ara_test.py`
- Reconstructed events: `results/vertical_ara_bubble_events.csv`
- Target results: `results/vertical_ara_target_results.csv`
- Machine-readable summary: `results/vertical_ara_summary.json`
- Validated interactive report: `VERTICAL_ARA_BUBBLE_HANDOVER_REPORT.artifact.json`

Retained SHA-256 hashes:

- events: `7217950D137A1DCA398B0313007BFB342071404114874D12FB3381AE0AD10FFA`
- target results: `735B9F559D13BC37430419C16AB6F6F67CF4EA88F65B1BA79096CF70E989AD5C`
- summary: `B2C8062C7381A48C1AA23BAE02661653FE1EC09C053693B97E77FB116C28E4B6`

