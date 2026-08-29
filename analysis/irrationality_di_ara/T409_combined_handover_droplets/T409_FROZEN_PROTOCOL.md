# T409 — Combined Rationality/Irrationality Di-ARA at liquid-droplet handover

Status: **frozen before optical-flow wave extraction or target scoring**  
Source-QA exception: the physical event frames and ROIs below were registered
from silhouette geometry before any Rationality/Irrationality wave was computed.

## Relational address

- **Who:** two liquid-water droplet identities on a pre-wetted fibre. Video S3
  contains a four-droplet cascade and therefore supplies three successive local
  pair handovers.
- **What:** two independently measured movement waves:
  - Rationality/locking wave `R(t)`: coherent affine flow carried by the pair;
  - Irrationality/open wave `I(t)`: non-affine residual flow not explained by
    that coherent transform.
- **When:** frame by frame from an established two-lobe state through the
  independently observed two-lobes-to-one handover.
- **Where:** the local pair ROI at the droplet/fibre scale; this is not a whole-
  apparatus average and not a molecular child cut.
- **Why:** test whether the two visible wave amplitudes form reproducible
  crossings or ridge-neighbourhood landmarks at a physical handover.
- **How:** dense optical flow -> robust affine fit -> coherent and residual
  magnitudes -> independent 0–2 ARA normalisation -> frozen crossing tests.

## Target status

| Item | Status | Meaning |
|---|---|---|
| Physical handover | **Direct** | Silhouette lobe count changes persistently from `n` to `n-1`. |
| Rationality wave | **Inferred measurement** | Affine displacement supported by the observed pixels. |
| Irrationality wave | **Inferred measurement** | Residual displacement after the same affine fit. |
| Molecular bridge formation | **Absent in fibre clips** | The fibre is pre-wetted, so a thin liquid connection already exists. |
| First-contact transfer control | **Direct but separate** | Video S1 has spatially separated droplets on a flat substrate; it is not part of the primary fibre gate. |

The target is therefore the **droplet-identity handover**, not “first bridge.”
This source-forced clarification was made before calculating `R(t)` or `I(t)`.

## Frozen event register

Frame numbers refer to the encoded supplementary videos. The source footage was
acquired at 20,000 fps and published as slowed 29.97-fps files; inferential
timing is therefore reported in encoded frames and dimensionless event position,
not as unverified physical microseconds.

| Event | Video | Pair ROI after horizontal orientation (`x0:x1`) | Start | Direct handover | End | Split |
|---|---:|---:|---:|---:|---:|---|
| E1 | S2 | 70:900 | 0 | 198 | 300 | development |
| E2 | S3 cascade 1 | 70:570 | 0 | 55 | 90 | development |
| E3 | S3 cascade 2 | 180:800 | 60 | 136 | 165 | holdout |
| E4 | S3 cascade 3 | 320:1000 | 142 | 182 | 225 | holdout |
| E5 | S4 vertical fibre (rotated clockwise) | 40:660 | 0 | 48 | 95 | development |
| E6 | S5 | 70:900 | 0 | 75 | 125 | holdout |
| E7 | S6 | 70:950 | 0 | 45 | 105 | development |
| E8 | S7, tracer particles | 70:950 | 0 | 95 | 160 | holdout |

Handover frames were selected by the pre-score silhouette extractor plus visual
QA of persistent, not momentary, lobe loss. Temporary neck pinches that later
returned to two lobes were not labelled handovers.

## Frozen wave construction

For each pair of consecutive oriented greyscale frames:

1. Use the extracted silhouette to keep the local droplet region and suppress
   static background, scale bars and the bare fibre.
2. Calculate dense Farneback optical flow.
3. Sample valid flow vectors on a regular grid and robustly estimate one affine
   map with RANSAC.
4. For the same valid pixels calculate:

   \[
   R_{\rm raw}(t)=\operatorname{median}\|v_{\rm affine}(t)\|,
   \qquad
   I_{\rm raw}(t)=\operatorname{median}\|v(t)-v_{\rm affine}(t)\|.
   \]

   These are independent absolute participations. They are **not** forced to
   sum to two and neither is constructed as `2 -` the other.
5. Apply `log1p` and freeze the 5th/95th percentile for each wave using only
   development events E1, E2, E5 and E7.
6. Map each wave independently to `[0,2]` and clip only outside the development
   range:

   \[
   x_W=2\,\mathrm{clip}\!\left(
   \frac{\log(1+W)-q_{05,W}}{q_{95,W}-q_{05,W}},0,1\right),
   \quad W\in\{R,I\}.
   \]

7. Smooth with a causal exponential moving average, `alpha = 0.25`.
8. Retain the signed affine area-change/convergence term as a directional
   diagnostic only; it does not alter either primary wave amplitude.

## Frozen landmarks and endpoints

Event position is

\[
u=\frac{f-f_{\rm start}}{f_{\rm event}-f_{\rm start}},
\]

so the direct handover is `u = 1`. Frames after handover remain visible for
reclosure but do not move the target.

### Primary holdout endpoint

For each holdout event, locate all interpolated equality crossings
`x_R(u) = x_I(u)` in `0.20 <= u <= 1.35`. Use the crossing closest to the
direct handover and report

\[
e_{\rm cross}=|u_{\rm cross}-1|.
\]

This endpoint is **diagnostic, not a deployable forecaster**, because choosing
the closest crossing uses the known event for scoring.

Frozen support gate:

- at least 3 of 4 holdout events have `e_cross <= 0.15`; and
- the holdout median `e_cross` beats the median of 10,000 within-event circular
  shifts of `I(t)` relative to `R(t)` by at least 25%; and
- the empirical circular-shift probability is `< 0.05`.

### Secondary endpoints

1. Joint ridge distance
   `D_1 = sqrt((x_R - 1)^2 + (x_I - 1)^2)`: its local minimum nearest the
   event is reported, not fitted.
2. Direction at the selected crossing: `R` rising and `I` falling is the
   predeclared irrational-to-rational locking orientation.
3. Signed affine convergence is compared in forward and time-reversed data.
4. A geometry-only lobe/neck timing baseline is reported alongside the wave
   result; because the direct target is defined geometrically, this baseline is
   descriptive rather than an independent discovery test.

## Controls and exclusions

- **Circular-shift control:** preserves each wave's autocorrelation and marginal
  distribution while breaking same-time coupling.
- **Event-pair shuffle:** pairs `R` from one holdout event with normalised `I`
  from another.
- **Time reversal:** recompute signed convergence and ordering. Absolute flow
  energies are expected to be largely reversal-invariant, so reversal is not a
  valid control for their marginal amplitudes alone.
- **Flat-surface S1 transfer:** evaluate separately; never pool into the primary
  fibre gate.
- No near-miss footage is available in this public source. Absence of that
  control is a stated limitation, not evidence for the hypothesis.

## Interpretation boundary

A pass would support a reproducible, source-local combined-wave landmark at
liquid-droplet identity handover. It would not establish a universal Di-ARA
law, a molecular mechanism, or causal navigation by the Irrationality wave. A
failure would mean this specific affine/residual instrument did not recover the
proposed landmark on the held-out droplet events.
