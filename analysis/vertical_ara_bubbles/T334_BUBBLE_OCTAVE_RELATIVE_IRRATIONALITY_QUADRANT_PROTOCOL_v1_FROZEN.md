# T334 frozen protocol — bubble octave-relative irrationality quadrant

**Frozen:** 3 August 2026, before calculating any T334 endpoint, quadrant,
candidate, shuffle or broken-lineage result  
**Originator of ARA interpretation:** Dylan La Franchi  
**Operationalisation and implementation:** Codex  
**Source:** Pandey et al., Zenodo `10.5281/zenodo.15102957`  
**Data status:** recorded bubble trajectories already opened for Vertical-ARA
and Phi tests; this is a new frozen question on an existing archive, not a
pristine discovery dataset

## Question

T333 recovered a two-axis complex ARA coordinate in recorded qutrit data:
radial contraction/expansion crossed with forward/reverse turning. Its radial
endpoints were stable and approximately reciprocal, but were not exact Phi and
changed with the identity-centre definition.

The bubble Vertical-ARA work had independently constructed the same complex
object across nested temporal rungs:

\[
q_{r,\ell}
=\frac{Z_{r,\ell+1}}{Z_{r,\ell}}
=s_{r,\ell}e^{i\delta_{r,\ell}},
\qquad \ell=0,1,2,3.
\]

Here the raw radial scale contains a known carrier: each parent window has
twice the temporal span of its child. The completed earlier test found a raw
scale close to `2`, not Phi. T334 therefore asks a different and more faithful
question:

> After retaining the established octave carrier `2`, does the residual
> breathing around that carrier form the same four-quadrant and reciprocal
> radial architecture seen in T333?

Phi is a competitor, not a construction rule.

## Source lock and population

Primary raw archive:

- `data.zip`
- SHA256
  `11F050285C740CCA7B4248E64F24304317E0563E61D39DC5A9F2A7F39BA86BC0`

Extracted source set:

- `35` source CSV files, `V01` through `V35`;
- sorted filename-plus-file-hash manifest digest
  `D712AA9BB5935C400AE76DA50B93DB97F5FEFD1E1E8814E5DC8322BD66076C7F`.

The source split and eligibility rule are inherited unchanged:

- calibration: `V01-V07`;
- primary evaluation: `V08-V28`;
- directional confirmation/holdout: `V29-V35`;
- one root contains `32` successive released centroid displacements;
- all same-origin `2`, `4`, `8`, `16` and `32` frame parent vectors must have
  magnitude at least `0.0005 m`.

The previously validated extraction retained `337` roots. T334 must
reconstruct them from the raw CSVs rather than trusting the saved T307-era
summary table.

## Native complex lineage

For root `r`, define the same-origin parent vectors

\[
Z_{r,\ell}
=\sum_{j=0}^{2^{\ell+1}-1}
(\Delta x_{r,j}+i\Delta y_{r,j}),
\qquad \ell=0,1,2,3,4.
\]

The four cross-rung complex multipliers are

\[
q_{r,\ell}=Z_{r,\ell+1}/Z_{r,\ell}
=s_{r,\ell}e^{i\delta_{r,\ell}}.
\]

No smoothing, interpolation, Fourier transform, trajectory fitting or
Phi-dependent selection is permitted.

## Primary octave-relative coordinate

The primary carrier is fixed independently at

\[
c_0=2.
\]

Define the residual radial breath

\[
u_{r,\ell}=\frac{s_{r,\ell}}{2},
\qquad
h_{r,\ell}=\log u_{r,\ell}.
\]

The two binary signs are:

- radial contraction/expansion: `sign(h)`;
- reverse/forward rotation: `sign(delta)`.

They define the four exact complex ARA quadrants. Values within `1e-12` of a
sign boundary are reported separately and are not assigned by convenience.

### Sensitivity carrier

One sensitivity uses

\[
c_{\rm cal}=\exp\bigl(\operatorname{median}_{\rm calibration}\log s\bigr).
\]

It is calculated using calibration only and then frozen for evaluation and
holdout. It cannot replace the primary `c0=2` verdict.

## Reciprocal endpoints

For each split, transition level and the pooled record, compute

\[
u_- = \operatorname{median}(u\mid u<1),
\qquad
u_+ = \operatorname{median}(u\mid u>1).
\]

The reciprocal-closure product is

\[
P=u_-u_+.
\]

The split-specific implied reciprocal scale is

\[
\widehat\alpha
=\exp\left[
\frac{
\operatorname{median}(\log u\mid u>1)
-\operatorname{median}(\log u\mid u<1)}{2}
\right].
\]

The calibration pooled value `alpha_cal` is the only fitted scale allowed in
evaluation and holdout.

For a candidate reciprocal pair `1/alpha <-> alpha`, define endpoint score

\[
L(\alpha)
=\frac12\left(
|\log u_-+\log\alpha|
+|\log u_+-\log\alpha|
\right).
\]

Lower is better.

## Frozen fixed candidates

The candidates are:

| name | alpha |
|---|---:|
| plastic | `1.324717957244746` |
| square root of two | `1.4142135623730951` |
| three halves | `1.5` |
| Phi | `1.618033988749895` |
| T333 recorded-qutrit scale | `1.809114052291864` |
| octave | `2` |
| e | `2.718281828459045` |

The calibration-fitted `alpha_cal` is reported beside these candidates but is
not a universal-constant claim.

## Controls

### 1. Temporal step-order null

For each of `500` deterministic draws, independently permute the same `32`
centroid-displacement vectors within every root. This preserves each root's
step multiset and full `32`-frame resultant while breaking the recorded prefix
ordering that creates the nested `2`, `4`, `8` and `16` frame parents.

Recompute all five vectors, all four multipliers, primary residuals and the
pooled evaluation/holdout endpoint score to frozen `alpha_cal`. Incomplete
controls are counted and excluded only from that draw.

### 2. Broken vertical identity

Within each video, pair every eligible root with the next eligible root in
chronological/root order. Form

\[
q^{\rm broken}_{r,\ell}
=\frac{Z_{\operatorname{partner}(r),\ell+1}}
       {Z_{r,\ell}}.
\]

This preserves video condition and scale level but breaks child-to-parent
identity. Compare its endpoint score with the observed record.

### 3. Raw-carrier audit

Report the unnormalised `s` endpoints and quadrant counts around `s=1`. This
is descriptive only. It must show how much of the apparent expansion is the
known octave carrier rather than silently removing it.

## Inference

- Primary grain: root-transition; report all `4` transition levels and pooled.
- Dependence-aware uncertainty: `5,000` whole-video cluster bootstraps for
  observed-minus-broken endpoint score and reciprocal products.
- Temporal-null p-value: `(1 + null scores <= observed score)/(501)`.
- Calibration selects only `alpha_cal` and `c_cal`; evaluation is primary and
  holdout is directional confirmation.
- Report candidate wins at each of the `4` levels plus pooled for evaluation
  and holdout (`10` cells total).

## Registered gates

### G0 — integrity

Raw hashes, inherited splits, root counts, vector reconstruction and all saved
metrics must pass an independent validator.

### G1 — usable four-quadrant residual coordinate

Under primary `c0=2`, all four quadrants must be present in evaluation and
holdout, and each quadrant must contain at least `5%` of non-boundary events in
each split.

### G2 — reciprocal closure

In both evaluation and holdout:

- pooled `P` must lie in `[0.90,1.10]`; and
- at least `3/4` transition levels must have `P` in `[0.85,1.15]`.

### G3 — calibration-to-holdout radial identity

The frozen `alpha_cal` must have lower pooled endpoint score than every fixed
candidate in evaluation and holdout. Its implied evaluation and holdout alpha
must each be within `10%` log-relative distance of `alpha_cal`.

### G4 — recorded order

The observed evaluation and holdout pooled scores to `alpha_cal` must each
beat at least `95%` of the `500` temporal step-order nulls.

### G5 — intact vertical identity

Observed endpoint score must be lower than broken-lineage score in evaluation
with a whole-video 95% interval below zero, and the difference must remain
negative in holdout.

## Verdict rule

- Passing G1 supports the complex residual quadrant coordinate in bubbles.
- Passing G1 and G2 supports an octave-relative reciprocal breath.
- Passing G1-G5 supports a stable, ordered, identity-preserving reciprocal
  breath across the sampled bubble rungs.
- Exact Phi or T333-alpha universality requires that fixed candidate to win
  the frozen candidate comparison in both evaluation and holdout. It is not
  inferred from visual proximity.
- Sensitivity results cannot rescue a failed primary carrier.

## Interpretation boundary

The residual `u=s/2` is not a claim that physical bubble radius literally
doubles. It is the breathing of cumulative centroid movement around a doubled
temporal observation span. Passing would establish the same ARA decomposition
in a second recorded domain; it would not prove a universal cosmic Time wave.

