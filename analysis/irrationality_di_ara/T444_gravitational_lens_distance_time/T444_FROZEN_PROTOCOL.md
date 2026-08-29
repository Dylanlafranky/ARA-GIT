# T444 frozen protocol — gravitational-lens distance/time cut

Frozen before numerical outcome inspection on 2026-08-28.

## Who

The measured child is a repeated quasar light signal arriving through two observed image paths. The foreground deflector is an external Connection parent acting on those paths; it is not silently relabelled as the light signal's internal anti-phase.

## What

Measure the arrival-time difference between the two real image paths and decompose the conventional Fermat arrival relation into:

1. geometric/path contribution, from the extra path geometry;
2. gravitational-potential contribution, from the deflector;
3. residual to the published observed delay, which remains ordinary model mismatch unless an independently measured external relation explains it.

Two frozen physical landmarks are evaluated rather than selecting whichever fits after inspection:

- concentrated point-mass lens;
- extended singular-isothermal-sphere (SIS) lens.

The point-mass landmark supplies independently non-zero geometric and potential differences. The ideal SIS landmark has equal geometric contributions for its two images, so its differential delay is potential-dominated. These are limiting conventional models, not claims that real galaxies are exact point masses or perfect SIS lenses.

## When

Use published observed delays in days. Each row is a completed historical handover: the same source variation is observed in one image and then the other. No future sample is used to tune the two frozen lens families.

## Where

Gaia GraL X catalogue J/A+A/707/A345 (Ducourant et al. 2026), joined between:

- table A1: component astrometry and redshifts;
- table B1: compiled published time delays.

Only systems with an unambiguous two-image pair, an observed deflector position, usable lens/source redshifts, and a matching published delay are eligible. Rows requiring an inferred component label or invented lens centre are excluded and counted.

## Why

Test the refined ARA hypothesis that time-facing traversal is accumulated distance along a path, while Connection bends/restricts the path and changes the arrival relation. A correct future relation therefore needs more than the identity's isolated direction: it needs the opposing connection field and, where present, other overlapping identities such as external shear or line-of-sight mass.

Known lensing mathematics is deliberately retained as a landmark. Reproducing it establishes coordinate direction and scale; it does not by itself prove a new ARA law.

## How

For image angle \(\theta\), source angle \(\beta\), and lens potential \(\psi\), use the conventional Fermat potential

\[
\phi(\theta,\beta)=\frac12|\theta-\beta|^2-\psi(\theta),
\qquad
\Delta t=\frac{D_{\Delta t}}{c}\,\Delta\phi .
\]

Use a frozen flat \(\Lambda\)CDM conversion only to put predictions in days: \(H_0=70\,\mathrm{km\,s^{-1}\,Mpc^{-1}}\), \(\Omega_m=0.3\). Native angular measurements and observed days remain visible.

For each eligible double, the two image radii about the observed deflector determine the one-dimensional axisymmetric landmark parameters. No delay value is used to fit them.

### ARA-facing coordinates

Native terms are primary. For visualization only, define a signed two-pole decomposition for each model:

\[
x_{\rm path}=2\frac{|\Delta t_{\rm geo}|}{|\Delta t_{\rm geo}|+|\Delta t_{\rm pot}|},
\qquad
x_{\rm connection}=2\frac{|\Delta t_{\rm pot}|}{|\Delta t_{\rm geo}|+|\Delta t_{\rm pot}|}.
\]

This is a simple ARA contribution cut, so the two shares intentionally sum to 2. It is not promoted to a Di-ARA: the signed native contributions retain whether the two terms assist or oppose one another, and the raw terms in days must accompany the 0–2 display.

### Frozen evaluation

- Report observed delay, geometric term, potential term, total prediction, signed residual, and absolute error for every eligible system.
- Compare chord-only/path-only, potential-only, and combined predictions.
- Report model-family sensitivity rather than choosing the better family after inspection.
- Null control: permute observed delays among systems 10,000 times; compare the frozen model's median absolute error and rank correlation to the permutation distribution.
- Robustness: leave-one-system-out summary; repeat with absolute delay magnitudes because literature sign conventions vary.
- If external-shear or line-of-sight metadata can be joined independently for a subset, test whether it explains residual magnitude. If not, record that as unavailable rather than reconstructing it from the residual.

### Frozen eligibility geometry

- Require exactly one unambiguous `A`, `B`, and `G` component in a catalogue system classified as `Double`.
- Require the observed deflector to lie between the two image directions: opening angle at the deflector at least 150 degrees.
- Require finite positive image radii, source redshift, deflector redshift, and a published `tAB` value.
- The 150-degree condition is an axisymmetric-model applicability check, not a success gate; all exclusions and near-threshold systems remain counted.

## Interpretation guardrails

- A match to the Fermat relation is a recovery of established gravitational-lensing structure.
- A residual is not evidence for a new identity by itself.
- Different lens families represent different Connection distributions, not different identities of the light.
- Catalogue rows are population-level completed handovers, not a live pre-event prediction test.
- Any data-source or identity pivot requires explicit notice before rerunning.
