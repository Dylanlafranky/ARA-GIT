# Frozen protocol — Vertical ARA temporal Phi handover

**Frozen:** 1 August 2026, after the failed area-ratio placement and before
calculating temporal-handover results  
**Domain:** tracked quasi-two-dimensional fluidized-bed bubbles  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`  
**Status at freeze:** proposed test; the source schema and the earlier
area-ratio analysis are known, but this temporal result has not been computed

## Question

Does Phi occur in the **movement handed between successive observations of the
same bubble lineage**, rather than in the size ratio between two different
bubble identities?

This test treats time as recurrence of the same branch through successive
slices. It does not reuse the earlier child/parent area-ratio measurement.

## Eligible temporal lineage

An eligible window contains one released track ID at five exactly consecutive
50-fps frames:

\[
P_0\to P_1\to P_2\to P_3\to P_4.
\]

The four centroid-displacement vectors are

\[
v_i=P_{i+1}-P_i,\qquad s_i=\lVert v_i\rVert.
\]

The registered handover is the first pair \((s_0,s_1)\). The later pair
\((v_2,v_3)\) is reserved for the primary outcome, so the predictor and outcome
do not reuse the same displacement.

Both registered handover steps must be at least one approximate image pixel,
`0.0005 m`. This is a measurement-resolution boundary, not a fitted target.
Zero or sub-resolution steps are excluded before target distances are computed.

All eligible overlapping windows are retained for description. Inference is
clustered or blocked by source video. A non-overlapping-window result, taking
windows four frames apart from the start of each track, is a declared
robustness check.

## Temporal Phi coordinate

For the two positive handover lengths let

\[
a=\max(s_0,s_1),\qquad b=\min(s_0,s_1),\qquad r=a/b.
\]

The two golden self-similarity readings are

\[
q_{\rm whole}=\frac{a+b}{a},\qquad q_{\rm lineage}=\frac{a}{b}.
\]

They both equal Phi only at the golden fixed point:

\[
\frac{a+b}{a}=\frac{a}{b}=\varphi.
\]

For a registered target \(\tau\), define

\[
D_\tau=
\sqrt{
\log^2\!\left(\frac{q_{\rm whole}}{\tau}\right)+
\log^2\!\left(\frac{q_{\rm lineage}}{\tau}\right)
}.
\]

This is a movement/path coordinate. Bubble area, perimeter and parent/child
size are not searched as substitutes.

## Frozen claims

### Placement claim

Phi is a distinguished same-lineage temporal handover if its **mean** movement
residual is smaller than every fixed competitor on evaluation and repeats that
ordering on holdout. Median residual is a declared robustness statistic.

### Temporal-tension claim

If Phi is an efficient non-repeating handover, windows closer to Phi should
have less future directional tension. The primary outcome is

\[
T_{\rm future}=\frac{\arccos\!\left(
\frac{v_2\cdot v_3}{\lVert v_2\rVert\lVert v_3\rVert}
\right)}{\pi},
\]

where `0` is continued motion and `1` is reversal. The frozen direction is a
positive association between \(D_\varphi\) and \(T_{\rm future}\): farther from
Phi means greater future turning tension.

Secondary outcomes are:

1. future speed tension
   \(\left|\log(s_3/s_2)\right|\);
2. immediate directional tension between \(v_1\) and \(v_2\);
3. whether the released identity persists for at least another ten frames
   after \(P_2\).

The secondary outcomes cannot rescue a failed primary claim.

## Predeclared competitors and nulls

Fixed targets:

\[
1,\qquad \sqrt2,\qquad 1.5,\qquad \varphi,\qquad 2.
\]

Also report:

- the free geometric optimum fitted on calibration only;
- within-track circular-shift controls, which preserve each track's movement
  magnitudes while breaking immediate temporal adjacency;
- outcome permutations blocked within source video;
- the non-overlapping-window robustness analysis.

A Phi result must be target-specific. If every target has the same event
ranking, or if a broad monotone asymmetry explains the result equally well,
the result is not evidence for Phi.

## Source split

Retain the earlier untouched split:

- **calibration:** `V01`–`V07`, amplitude `0.0`;
- **evaluation:** `V08`–`V28`, amplitudes `0.25`–`0.75`;
- **strict holdout:** `V29`–`V35`, amplitude `1.0`.

Calibration may establish the free optimum and verify numerical tolerances.
The placement and temporal-tension verdicts are determined on evaluation and
then checked unchanged on holdout.

## Statistical decisions

- Describe target distance using medians and means by split.
- Estimate uncertainty by resampling whole videos, not individual windows.
- Test the registered positive Spearman association using 5,000 permutations
  blocked within video.
- For permutation inference, take at most 250 deterministic, evenly spaced
  eligible windows from each video. Retain every eligible window for
  descriptive target-distance results. This balances videos and prevents a
  long, densely tracked condition from dominating the randomization.
- Report effect sizes and the number of videos as well as window counts.
- The strict holdout is considered evaluable only if it supplies at least 20
  eligible windows across at least three videos.

## Interpretation gates

**Supports this Phi placement** only if Phi beats every fixed target in
evaluation and keeps the same ordering in strict holdout.

**Supports the temporal-tension consequence** only if Phi distance predicts
lower future directional tension in evaluation, repeats directionally in
holdout, and is not reproduced by the circular-shift control.

**Does not support** the relevant claim if another landmark is consistently
closer, the fitted optimum lies stably elsewhere, or the outcome relation does
not repeat.

**Data-insufficient** applies if lineage continuity, displacement resolution,
or holdout coverage fails.

This experiment tests one precise temporal placement of Phi. It does not by
itself confirm or reject Vertical ARA or the full ARA framework.

## Known measurement limitation

The public files contain already segmented contours and tracker-assigned IDs,
not raw sensor fields. The test can determine whether the recorded trajectory
contains a Phi-structured handover. It cannot determine whether camera
sampling, contour extraction or identity tracking erased a finer handover that
existed before measurement.
