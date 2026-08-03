# T328 v1 - frozen bubble Phi circle-train test

**Frozen:** 2 August 2026, before calculating any T328 endpoint  
**Test ID:** `T328-PHI-CIRCLE-TRAIN-BUBBLES-v1`  
**Domain:** tracked quasi-two-dimensional fluidized-bed bubbles  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`  
**Status at freeze:** active frozen protocol

## Question

When the raw movement direction of one continuously tracked bubble is placed
on an ARA direction circle, does it follow the declared circle-train operator

\[
\boxed{x_{n+1}=\left(x_n+\frac{2}{\phi}\right)\bmod 2}
\]

more closely than the fixed alternatives and order-destroying controls?

This is a test of motion through successive time slices. Bubble area, radius,
speed, merger ratios and prior Phi-derived variables are not substituted for
the movement direction.

## Source population and fixed splits

Reuse the public contour-centroid files and source splits already registered
for the Vertical ARA bubble tests:

- calibration: `V01`-`V07`, amplitude `0.0`;
- evaluation: `V08`-`V28`, amplitudes `0.25`-`0.75`;
- strict holdout: `V29`-`V35`, amplitude `1.0`.

The archive and these split labels have already been opened in earlier tests.
T328 is therefore a newly frozen operator on an existing public archive, not a
claim of a never-opened dataset.

## Eligible lineage

Reuse the non-overlapping 33-position roots from the dyadic-chain work. A root
is one tracker-assigned identity observed at 33 exactly consecutive 50-fps
frames:

\[
P_0\to P_1\to\cdots\to P_{32}.
\]

Within an uninterrupted segment, roots begin at the segment's first frame and
then every 32 frames. All 32 one-frame displacement magnitudes must be at least
`0.0005 m`, the previously frozen one-pixel-scale movement threshold. A root
failing that rule is excluded whole; missing headings are not interpolated.

No smoothing, fitted trajectory, Fourier transform, resampling, or outcome-
dependent rotation is allowed.

## Raw ARA direction coordinate

For displacement

\[
D_j=P_{j+1}-P_j=(\Delta x_j,\Delta y_j),
\]

define its position on the ARA direction circle by

\[
x_j=
\left[
\frac{\operatorname{atan2}(\Delta y_j,\Delta x_j)}{\pi}
\right]\bmod2,
\qquad j=0,\ldots,31.
\]

The circular distance on the 0-2 circle is

\[
d_2(a,b)=\min\left(|a-b|,\,2-|a-b|\right).
\]

The source coordinate handedness is retained exactly as recorded. The primary
test privileges the explicitly proposed positive operator; it does not choose
a sign after seeing each event.

## Frozen candidates

The primary directed increments are the major-orientation versions of the
previously registered ARA landmarks:

| Candidate | Directed increment on 0-2 |
|---|---:|
| persistence | `0` |
| ridge | `1` |
| silver conjugate | `2 - 2(sqrt(2)-1)` |
| two fifths | `2 - 4/5` |
| Phi | `2/phi` |
| Fibonacci 8/21 | `2 - 16/21` |
| three eighths | `2 - 3/4` |
| one over e | `2 - 2/e` |
| one third | `2 - 2/3` |

These use one common orientation convention. The Phi entry is exactly the
user-declared recurrence, not the nearby `8/21` rational.

## Endpoints

### 1. Local child-step score

For candidate increment `delta`, each root contributes

\[
L_{\mathrm{local}}(\delta)=
\operatorname{median}_{j=0}^{30}
d_2\!\left(x_{j+1},(x_j+\delta)\bmod2\right).
\]

### 2. Unreanchored parent-carrier score

Anchor once at `x_0` and predict the complete remaining path:

\[
\widehat x_h=(x_0+h\delta)\bmod2,
\qquad h=1,\ldots,31.
\]

Each root contributes the median circular error over all 31 horizons. This is
the primary endpoint. The carrier is never reanchored after `x_0`.

### 3. Fibonacci return fingerprint

At lags

\[
h\in\{2,3,5,8,13,21\},
\]

compare the median observed return

\[
\operatorname{median}_j d_2(x_{j+h},x_j)
\]

with the candidate return `d_2(0,h delta mod 2)`. Each root contributes the
mean absolute error across the six registered lags.

### 4. ARA reversibility audit

Separately from the positive-direction primary test, give every candidate the
same whole-root two-direction allowance. Calculate the complete positive and
negative local and carrier scores and retain the smaller complete-root score.
The sign is fixed for the whole root and cannot change between events. This is
reported as an ARA symmetry audit and cannot silently replace a failed
directed endpoint.

## Registered controls

### Turn-order shuffle

For each root, calculate the 31 observed circular turns

\[
u_j=(x_{j+1}-x_j)\bmod2.
\]

Within each root, permute those turns, reconstruct a path from the original
`x_0`, and recalculate the Phi parent-carrier score. Use 10,000 deterministic
draws with seed `20260802`. This preserves each root's turn multiset and net
phase while destroying their order.

### Broken-lineage control

Within each source video, retain the first 15 turns from one eligible root and
replace the remaining 16 with those from the next eligible root in a fixed
cyclic ordering. Reconstruct from the original `x_0`. Videos with fewer than
two eligible roots do not enter this control.

### Reversed-time control

Reverse the physical position sequence before calculating displacements and
headings. This includes the required half-turn change caused by reversing a
displacement vector. Report it against the positive-direction primary score;
do not use it to choose the primary orientation.

## Aggregation and uncertainty

- Reduce each root to one score per endpoint and candidate.
- Report root medians and means by split.
- Use 5,000 whole-video cluster-bootstrap draws for paired Phi-minus-rival and
  real-minus-control mean differences.
- The evaluation split carries the inferential intervals; strict holdout must
  repeat the registered direction.
- The holdout is data-sufficient only with at least 20 eligible roots from at
  least three videos.

## Resolution audit

Infer the physical position grain from the source pixel-to-metre coordinates.
For each eligible displacement, estimate the directional grain by

\[
g_j=\frac{\operatorname{atan2}(\sqrt2\,p,\lVert D_j\rVert)}{\pi},
\]

where `p` is one source pixel in metres. Report the median `g_j`.

The one-step exact-Phi claim is resolution-eligible only when this grain is
smaller than Phi's circular separation from the nearest frozen candidate.
The parent claim is resolution-eligible at a registered horizon only when the
candidate separation accumulated at that horizon exceeds the same grain.

## Verdict gates

The exact directed bubble carrier is **supported in this representation** only
if all of the following hold:

1. Phi has the lowest mean parent-carrier loss among fixed candidates in
   evaluation and repeats as the winner in holdout;
2. every paired Phi-minus-rival mean is below zero with an evaluation 95%
   interval wholly below zero and remains directionally below zero in holdout;
3. the observed Phi parent loss beats the turn-order shuffle at lower-tail
   `p < 0.05` in evaluation and holdout;
4. the real lineage beats the broken-lineage control with an evaluation 95%
   interval wholly below zero and repeats directionally in holdout;
5. Phi wins the Fibonacci-return endpoint in evaluation and holdout; and
6. at least one registered horizon resolves Phi from its nearest frozen rival.

If some but not all gates pass, verdict is **partial / mixed**. If no
substantive Phi gate passes, verdict is **not supported**. If the holdout count
or resolution boundary fails, the affected exact claim is **inconclusive**.

Local score, reversibility, free-increment diagnostics and calibration results
are descriptive and cannot rescue a failed primary carrier.

## Scope boundary

This test concerns one explicit placement of the Phi circle-train operator in
tracked bubble centroid directions. It can support or reject that observable.
It does not by itself confirm or reject Phi in other bubble properties,
Vertical ARA, or the full ARA framework.

