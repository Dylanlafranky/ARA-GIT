# Vertical ARA temporal-handover result

**Date:** 1 August 2026  
**Status:** GOLDEN FIXED-POINT GEOMETRY RECOVERED; PHI-SPECIFIC MOVEMENT AND TEMPORAL-TENSION CLAIMS NOT SUPPORTED

## Answer first

Measuring **between successive data slices** did recover the golden
self-similarity construction much more cleanly than the earlier bubble-area
test. The calibration fit for the full two-relation handover was

\[
\widehat\tau_{\rm joint}=1.607795,
\]

only `0.010239` below \(\phi=1.618034\). Among the five fixed landmarks, Phi
had the lowest mean joint residual in both evaluation and untouched holdout.
Real adjacent slices were also closer to the golden equality than temporally
shifted slices from the same tracks.

However, that is **not sufficient evidence that the physical movement ratio
is Phi**. The joint ruler

\[
\frac{a+b}{a}=\frac{a}{b}
\]

has Phi as its unique algebraic fixed point, so it structurally privileges
Phi. A post-protocol audit compared the raw step ratio \(a/b\) to every target
with the same one-dimensional loss. That fairer comparison fitted
`1.416072` on calibration—almost exactly \(\sqrt2\)—and preferred
\(\sqrt2\) in evaluation and `1.5` in holdout. Phi was close, but it was not
the empirical winner.

The registered consequence also failed: being closer to Phi did not reliably
predict smoother movement later. The evaluation association was
\(\rho=0.00961\), one-sided \(p=0.3535\); the non-overlapping-window check was
\(\rho=-0.03595\), \(p=0.9524\). Holdout was directionally positive but still
weak (\(\rho=0.03583\), \(p=0.09358\)).

The defensible result is therefore:

> Adjacent bubble trajectories contain a real local continuity relation that
> moves the data toward the golden fixed-point geometry, but this dataset does
> not identify Phi as the actual step ratio or as a predictor of reduced
> future temporal tension.

## What was measured

One tracked bubble identity was followed across five consecutive 50-fps
slices:

\[
P_0\to P_1\to P_2\to P_3\to P_4.
\]

The first two centroid displacements supplied the handover lengths:

\[
s_0=\lVert P_1-P_0\rVert,
\qquad
s_1=\lVert P_2-P_1\rVert.
\]

Letting \(a=\max(s_0,s_1)\) and \(b=\min(s_0,s_1)\), the frozen joint reading
was

\[
q_{\rm whole}=\frac{a+b}{a},
\qquad
q_{\rm lineage}=\frac{a}{b}.
\]

The following two movements were reserved for future directional tension, so
the predictor and primary outcome did not reuse the same displacement.

Only movements of at least approximately one image pixel (`0.0005 m`) were
eligible. Of `153,078` candidate five-slice windows, `152,780` passed; only
`298` were removed as sub-resolution handovers.

## Data split

- calibration: `43,765` windows from six usable `V01-V07` videos;
- evaluation: `82,400` windows from all 21 `V08-V28` videos;
- untouched holdout: `26,615` windows from all seven `V29-V35` videos.

Inference used at most 250 deterministic, evenly spaced windows per video and
5,000 outcome permutations blocked within video. Placement uncertainty used
5,000 whole-video bootstrap resamples. All windows remained in descriptive
distance statistics.

## Frozen joint-ruler result

Mean joint distance on evaluation:

| Target | Mean distance |
|---|---:|
| `1` | 0.833144 |
| \(\sqrt2\) | 0.462805 |
| `1.5` | 0.427140 |
| \(\phi\) | **0.408533** |
| `2` | 0.536204 |
| calibration-fitted `1.607795` | **0.408388** |

Mean joint distance on holdout:

| Target | Mean distance |
|---|---:|
| `1` | 0.860706 |
| \(\sqrt2\) | 0.485999 |
| `1.5` | 0.448153 |
| \(\phi\) | **0.425979** |
| `2` | 0.544696 |
| calibration-fitted `1.607795` | 0.426148 |

Phi beat every other fixed target under the frozen joint ruler in both splits.
Every whole-video 95% bootstrap interval for `Phi distance − competitor
distance` remained below zero.

## What temporal adjacency contributed

The pure golden-equality residual was

\[
S=\left|\log\left(\frac{q_{\rm whole}}{q_{\rm lineage}}\right)\right|.
\]

Evaluation:

- real adjacent mean: `0.517290`;
- within-track shifted mean: `0.555003`;
- paired difference: `−0.037828`;
- whole-video 95% interval: `[-0.045615, -0.030207]`.

Holdout:

- real adjacent mean: `0.536896`;
- within-track shifted mean: `0.598501`;
- paired difference: `−0.061808`;
- whole-video 95% interval: `[-0.071712, -0.049482]`.

Thus real temporal neighbours approach the golden equality more closely than
nonlocal movements from the same trajectories. But this is not Phi-specific:
real adjacency improved distance to **every** frozen landmark, and the largest
adjacency-versus-shift gain occurred at target `1`, consistent with ordinary
local movement continuity.

## Post-protocol direct-ratio audit

Because the joint equality has Phi built into its fixed point, the audit used

\[
E_\tau=\left|\log\left(\frac{a/b}{\tau}\right)\right|.
\]

Evaluation mean direct distance:

| Target | Mean distance |
|---|---:|
| `1` | 0.536606 |
| \(\sqrt2\) | **0.373508** |
| `1.5` | 0.375005 |
| \(\phi\) | 0.385568 |
| `2` | 0.455924 |
| calibration-fitted `1.416072` | **0.373470** |

Holdout mean direct distance:

| Target | Mean distance |
|---|---:|
| `1` | 0.583312 |
| \(\sqrt2\) | 0.402248 |
| `1.5` | **0.398879** |
| \(\phi\) | 0.403208 |
| `2` | 0.457811 |
| calibration-fitted `1.416072` | 0.402101 |

This prevents promotion of the joint result as a discovered physical Phi
constant. The raw movement ratio occupies the broad \(\sqrt2\)-to-`1.5`
neighbourhood in this sampled representation.

## Temporal-tension prediction

Future directional tension was the normalized turn angle between the final two
reserved movement vectors. The frozen prediction required a positive
association: farther from Phi should mean more later turning.

| Split/check | Spearman \(\rho\) | one-sided \(p\) | Windows |
|---|---:|---:|---:|
| Evaluation Phi | 0.00961 | 0.35353 | 5,248 |
| Evaluation non-overlap | -0.03595 | 0.95241 | 1,796 |
| Holdout Phi | 0.03583 | 0.09358 | 1,750 |
| Holdout non-overlap | 0.02837 | 0.15397 | 573 |

The shifted-Phi control predicted future turning more strongly than the real
Phi coordinate in both splits. This is inconsistent with the proposed
low-tension mechanism and suggests broader track-speed or state persistence.

## ARA interpretation

The test supports a narrower statement than the initial hypothesis:

1. Measuring the **change between slices** is a much more faithful temporal
   ARA object than comparing unrelated bubble sizes.
2. The equation joining part, whole and repeated part recovers Phi exactly as
   geometry. The empirical joint fit near Phi shows the bubble motion occupies
   that neighbourhood.
3. The raw movement itself does not settle uniquely at Phi. In this dataset it
   is better described by a nearby \(\sqrt2\)-to-`1.5` band.
4. Temporal adjacency is real: nearby slices are more mutually similar than
   shifted slices. But this continuity is broad and strongest near equal
   movement, not uniquely golden.
5. The proposed claim that Phi minimizes subsequent temporal tension is not
   supported here.

This result is useful because it distinguishes three things that had been
compressed together: the **golden algebraic fixed point**, the **observed
movement ratio**, and the **consequence predicted from that ratio**.

## Measurement boundary and next test

The public source contains segmented centroids and tracker IDs, not raw field
motion. Sampling at a fixed 50 fps can change the apparent step-ratio band, and
centroid quantization can suppress movement below one pixel.

The strongest next test is a multi-cadence trajectory dataset or raw high-speed
video where the same physical path can be resampled at several \(\Delta t\)
values. Freeze the prediction that a genuine Phi handover remains stable after
reasonable cadence changes, whereas a sampling-induced \(\sqrt2\)-to-`1.5`
band will move. Retain the joint equality, direct ratio and future-tension
outcome as three separate gates.

## Reproduction and integrity

- Frozen protocol:
  `FROZEN_PROTOCOL_VERTICAL_ARA_TEMPORAL_HANDOVER_2026-08-01.md`
- Post-result audit declaration:
  `POST_PROTOCOL_AUDIT_TEMPORAL_PHI_2026-08-01.md`
- Analysis:
  `work/run_vertical_ara_temporal_handover.py`
- Independent result assertions:
  `work/validate_vertical_ara_temporal_handover.py`
- Machine-readable summary:
  `results/temporal_ara_summary.json`
- Validated interactive technical report:
  `VERTICAL_ARA_TEMPORAL_HANDOVER_REPORT.artifact.json`
- Target table:
  `results/temporal_ara_target_results.csv`
- Deterministic 10,000-window review sample:
  `results/temporal_ara_window_sample.csv`

Retained SHA-256 hashes:

- summary: `0BA4F0178BA64B25C3F529855556619FB422481B2E0F00B71BD4F914D6BFA003`
- target table: `BF16455D4CA8A90378A0B12BDB6A0FB4BCCBFA391FEC245F755ACEB1479DDCE1`
- review sample: `3E409856037567BDA622A5B669E8306D9CD6D1729F06885810CD5660FD19E35B`

The validator passed all registered structural, split, direct-audit and
future-tension assertions.
