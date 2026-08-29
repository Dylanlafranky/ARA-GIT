# T411 - Time-facing Irrationality Di-ARA in filament breakup

**Status:** development instrument frozen before any S2/S4 holdout trajectory is
computed or scored  
**Frozen split:** 19 August 2026  
**ARA hypothesis:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## Relational address

- **Who:** one Newtonian silicone-oil filament at a time. Fluids S1 and S3 are
  development; S2 and S4 are untouched holdout.
- **What:** the ARA relation between cumulative thinning explained by imposed
  plate separation and cumulative extra thinning not explained by that parent
  model.
- **When:** each original 1000-fps sample from the intact cylinder to the last
  reliable (`D_px >= 5`) neck-width sample. The independently observed breakup
  time remains the direct endpoint.
- **Where:** the vertical filament mid-plane, at one identity scale through
  time. This is a longitudinal/time-facing cut, not a cross-object droplet cut.
- **Why:** test whether the unresolved branch approaches and crosses a
  repeatable equal-participation ridge before breakup, and whether the result
  survives gravity controls.
- **How:** subtract the physical plate-only thinning model from the observed
  cumulative diameter loss; form an exact 0-2 relation from the independently
  obtained terms; transfer a development-registered window to held-out fluids.

## Target and measurement status

| Item | Status |
|---|---|
| Filament breakup time | **Direct**, registered from 1000-fps video |
| Mid-plane diameter | **Direct image measurement**, reliable to 5 pixels |
| Plate contribution | **Modelled from direct inputs**: plate speed and initial geometry |
| Non-plate contribution | **Inferred residual** |
| Capillary share of residual | **External physical validation**, not assumed |
| Gravity share of residual | **Unresolved rival**, explicitly tested |
| Universal time mechanism | **Not identified by this source** |

The medium changes from the T409/T410 water droplets to vertically stretched
silicone-oil filaments. Results must not be pooled silently across these media.

## Source and source QA

- Allgood & Jones, *Breakup dynamics of Newtonian fluids under extension*,
  Royal Society Open Science (2026), DOI `10.1098/rsos.252527`.
- Raw dataset: DOI `10.5281/zenodo.17341800`, `ThinningData.txt`, MD5
  `19bc8f502dde048dc614023bead32f9e`.
- Experiment conditions: DOI `10.6084/m9.figshare.31229231.v1`, Table A1.
- Source contains 176 experiments and 136,159 rows. Zero-valued separator rows
  are not physical frames. Widths below five pixels and subsequent `NaN` values
  are outside the authors' validated automated-measurement range and are not
  imputed.

## Physical parent model

For initial diameter `D0`, initial plate separation `H0`, measured separation
speed `v`, and elapsed time `t`, the plate-only mechanical trajectory is

\[
D_M(t)=D_0\left(1+\frac{vt}{H_0}\right)^{-3/4}.
\]

The two cumulative contributions are

\[
R(t)=D_0-D_M(t),
\qquad
I(t)=D_M(t)-D_{obs}(t).
\]

`R` is the coherent/determined parent contribution. `I` is the unresolved
non-plate contribution. It is not pre-labelled as capillarity, gravity or
time. The exact accounting identity is

\[
R(t)+I(t)=D_0-D_{obs}(t).
\]

No complement is invented and neither wave is normalized from the other.

## ARA coordinate

Once total thinning is at least 10% of `D0` and both contributions are
non-negative, form the relation

\[
x_{RI}(t)=\frac{2I(t)}{R(t)+I(t)}.
\]

- `x_RI = 0`: all measured cumulative thinning is plate-modelled;
- `x_RI = 1`: equal parent and unresolved participation;
- `x_RI = 2`: all measured cumulative thinning is unresolved by the plate
  model.

The primary candidate handover is the first persistent upward crossing of
`x_RI = 1`, equivalently `I = R`. Persistence is five consecutive reliable
samples. The direct breakup remains distinct from this inferred handover.

## Predeclared processing

1. Remove only explicit zero separator rows.
2. Retain samples with finite diameter and `D_px >= 5`.
3. Apply a centred five-sample median only to suppress single-frame pixel
   threshold jitter. Raw values remain in the output.
4. Require at least 20 reliable samples per run.
5. Do not extrapolate through the unmeasured sub-five-pixel tail.
6. Use measured, not target, plate velocity.
7. Calculate viscosity and density at each experiment's recorded temperature
   using the paper's equations; use the measured fluid surface tensions.

## Development and holdout

- **Development:** S1 (lowest viscosity) and S3 (highest viscosity), including
  both 1 and 2 mm plates.
- **Holdout:** S2 (both plate sizes) and S4 (different silicone composition,
  2 mm plates only).

Development may register a crossing window and monotonicity threshold. The
holdout script is disabled until those parameters are written, the final
protocol is hashed, and the hash is recorded.

## Controls

### Temporal-order control

Within each run, circularly shift the unresolved `I(t)` history against the
parent `R(t)` history. This preserves each wave's values and autocorrelation
while breaking their same-time relation. Observed monotonic progression and
crossing concentration must beat these shifts.

### Gravity rival

Initial local Bond number is

\[
Bo_0=\frac{\rho g(D_0/2)^2}{\sigma}.
\]

At the inferred handover, also report local neck Bond number and a
height-sensitive hydrostatic-to-capillary pressure proxy,

\[
G_H(t)=\frac{\rho g H(t)D_{obs}(t)}{2\sigma}.
\]

The result must be reported separately for 1 and 2 mm plates and for low/high
`Bo0`. A fourfold plate-size change in `Bo0` provides the main gravity
sensitivity. A result that merely tracks `Bo0`, `G_H`, or accumulated vertical
length is not accepted as a clean time-facing transfer.

### Capillary crosswalk

The theoretical viscous capillary thinning magnitude is

\[
r_C=2\alpha\frac{\sigma}{\mu},\qquad \alpha=0.0709.
\]

The late observed thinning rate is compared with `r_C`. Agreement supports a
capillary interpretation of the residual near breakup; disagreement leaves
the residual unidentified. This crosswalk cannot by itself pass the ARA gate.

## Interpretation boundary

A transfer would show that this time-facing parent/residual decomposition
tracks a reproducible physical handover regime across fluids. It would not
show that time causes the breakup, that gravity is absent, or that the
Irrationality Di-ARA is universal. A failure would reject this particular
time-facing operationalisation without rejecting the broader ARA geometry.
