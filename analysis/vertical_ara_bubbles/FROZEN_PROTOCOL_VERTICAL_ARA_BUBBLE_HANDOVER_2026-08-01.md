# Frozen protocol — Vertical ARA bubble handover

**Frozen:** 1 August 2026, before downloading or inspecting the source rows  
**Domain:** quasi-two-dimensional fluidized-bed bubbles  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`  
**Status at freeze:** proposed test; no event ratios or outcomes inspected

## Question

Does a directly observed child-to-parent bubble lineage show a special Phi
handover, rather than Phi merely appearing somewhere in a broad collection of
unrelated bubble sizes?

This is a test of **Vertical ARA**: the same ARA relation handed between
successive identity scales. It is not a test of arbitrary same-rung bubble
pairs.

## Eligible lineage

An eligible event must reconstruct

\[
\underbrace{C_s}_{\text{smaller child}}
+
\underbrace{C_l}_{\text{larger child}}
\longrightarrow
\underbrace{P}_{\text{new parent}},
\]

from spatially and temporally continuous tracks.

The analysis must not replace a missing lineage with:

- similarly sized bubbles elsewhere in the frame;
- neighbouring catalogue rows without a merger;
- rank-adjacent bubbles;
- a parent assembled from more than two unresolved children.

If the released data cannot identify genuine binary mergers with acceptable
confidence, the test is **data-insufficient**, not a Phi test.

## Measurement

Because the experiment is quasi-two-dimensional, use the released bubble area
as the size coordinate. Do not search diameter, perimeter and area and retain
whichever favours Phi.

For a reconstructed event let

\[
b=A_s,\qquad a=A_l,\qquad p=A_P,
\]

where \(A_s\leq A_l\). Define

\[
r_{cc}=\frac{a}{b},
\qquad
r_{pc}=\frac{p}{a},
\qquad
c=\frac{p}{a+b}.
\]

The Golden Handover condition is

\[
\boxed{r_{cc}=r_{pc}=\varphi}.
\]

The closure coordinate \(c\) is a lineage-quality check. Conservation plus
equal ratios mathematically implies Phi, so recovering the identity alone is
not evidence that the physical system prefers Phi.

## Outcome-bearing prediction

The registered ARA prediction is:

> Among valid binary mergers, events closer to the Golden Handover condition
> will form a stable parent with less post-merger temporal tension.

Primary response, if track length permits: dimensionless or frame-normalised
time for the parent circularity

\[
\chi=\frac{4\pi A}{P^2}
\]

to enter and remain near its post-event settled level.

Secondary responses:

1. integrated post-event circularity deviation;
2. parent persistence duration;
3. observed re-splitting within the available track window.

No result may be promoted if Phi is selected only by changing the response
after inspection. When the primary response cannot be measured, the test is
reported as data-insufficient and secondary results remain exploratory.

## Predeclared competitors

Compare the Phi-fixed handover with fixed alternatives

\[
1,\quad \sqrt2,\quad 1.5,\quad \varphi,\quad 2,
\]

plus:

- a no-ratio model;
- a free optimum estimated on calibration data only;
- within-condition outcome permutations.

The free optimum is required: a result centred elsewhere must be allowed to
reject the Phi-specific claim.

## Source split

The 35 source conditions are split by the published forcing amplitude:

- **pipeline calibration:** videos `V01`–`V07`, amplitude `0.0`;
- **frozen evaluation:** videos `V08`–`V28`, amplitudes `0.25`–`0.75`;
- **strict holdout:** videos `V29`–`V35`, amplitude `1.0`.

Calibration may tune tracking and measurement-error tolerances without using
Phi proximity or outcome advantage. Once frozen, the same lineage detector is
applied unchanged to evaluation and holdout.

## Minimum data boundary

- Fewer than 50 defensible binary events overall: feasibility result only.
- Fewer than 20 events in strict holdout: no strict replication verdict.
- Failed identity continuity, implausible area closure, or unresolved extra
  bubbles exclude an event without reference to its Phi distance.

## Controls and covariates

At minimum account for:

- parent area;
- child approach speed when recoverable;
- vertical position in the bed;
- forcing condition;
- pre-event child shape quality.

Report results both pooled and by forcing family. A pooled Phi result that
reverses within conditions is not support.

## Interpretation gates

**Supports this Vertical-ARA Phi placement** only if the Phi-fixed relation
predicts the registered outcome on evaluation, remains competitive with the
free optimum, beats the fixed alternatives, and repeats directionally on the
strict holdout.

**Does not support this placement** if the free optimum is stably elsewhere,
another fixed landmark predicts better, or the effect vanishes under the
controls.

**Does not test the claim** if genuine binary lineages or the primary temporal
response cannot be reconstructed.

Success or failure concerns this Phi handover subset of Vertical ARA. It does
not by itself confirm or reject the complete ARA framework.

