# T327 v2 — frozen river thalweg Phi circle-train test

**Frozen:** 2 August 2026, before any T327 endpoint calculation  
**Test ID:** `T327-PHI-CIRCLE-TRAIN-THALWEG-v2`  
**Incorporates:** `T327_PHI_CIRCLE_TRAIN_THALWEG_PROTOCOL_v1_FROZEN.md`  
**Status:** active frozen protocol

## Correction history

Version 1 is preserved as an aborted pre-endpoint draft. Its Section 5 formula
took the minimum of positive and negative candidate losses at each event, even
though the immediately following sentence correctly said that sign cannot be
selected separately by event. That accidental formula would let a path switch
direction freely and would flatten the ordered geometry.

Version 2 changes only that scoring operation. Every other declaration,
source, eligible cross-section, control path, candidate, endpoint, resolution
gate and verdict boundary remains exactly as frozen in version 1.

## Active whole-path sign rule

For path positions `x_i`, let

\[
u_i=(x_i-x_{i-1})\pmod 2.
\]

For candidate magnitude `delta`, calculate two complete-path local scores:

\[
L_+(\delta)=\operatorname{median}_i d_2(u_i,\delta),
\]

\[
L_-(\delta)=\operatorname{median}_i d_2(u_i,2-\delta).
\]

The candidate's local score is

\[
\boxed{L(\delta)=\min\{L_+(\delta),L_-(\delta)\}},
\]

and the selected sign is fixed once for the complete path. It is never changed
between child events.

The parent carrier uses the same rule. From the observed second-slice anchor,
construct one entire positive prediction and one entire negative prediction:

\[
\widehat x^{(+)}_{a+h}=(x_a+h\delta)\pmod2,
\qquad
\widehat x^{(-)}_{a+h}=(x_a-h\delta)\pmod2.
\]

Score each complete prediction against all later observed positions and retain
the lower whole-path median. The selected sign and both directional losses
must be reported.

Every fixed candidate receives the identical two-direction allowance. The
source fixes downstream order; this rule acknowledges that the archive does
not assign an ARA sign to inner-bank versus outer-bank lateral motion.

## Active resolution refinement

The local exact-Phi claim is resolution-eligible only if the median raw
lateral neighbour spacing at selected feature points is smaller than Phi's
distance to its nearest tested fixed rational competitor.

For the multi-step carrier, a candidate pair becomes geometrically separable
at horizon `h` only when

\[
d_2(h\delta_1,h\delta_2)
\]

exceeds the median raw lateral neighbour spacing and that horizon exists in
the 33-slice path. Candidate-score differences below this declared grain are
reported but cannot establish exact-constant recovery.

