# Frozen protocol — empirical Phi handover in ordered plant phyllotaxis

**Frozen:** 30 July 2026, before the analysis script was written or run.  
**Test ID:** `T302-PHI-PHYLLOTAXIS-v1`  
**Orientation:** one directed placement cycle occupies the `0 -> 1` half of the
ARA diameter; its reversed/mirrored reading occupies `1 -> 2`.

## 1. Status boundary

This is an empirical calibration and retrodiction, not a blind discovery test.
The source paper states that Arabidopsis divergence angles are near the golden
angle and that two biological perturbations increase their variability. The
test can still answer three useful questions:

1. whether the raw measurements map cleanly onto the proposed ARA Phi pair;
2. whether exact Phi is distinguishable from close rational and irrational
   rivals;
3. whether the measured *order* of placements preserves open space better than
   perturbed or shuffled order.

No positive result may be described as discovering Phi in plants.

## 2. Public data

Primary article:

> Tameshige et al., “Mutual inhibition between EPFL2 and auxin extends the
> intervals of periodic leaf morphogenesis,” *Nature Communications* (2025),
> DOI `10.1038/s41467-025-65792-y`.

Canonical source-data archive:

`https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-65792-y/MediaObjects/41467_2025_65792_MOESM9_ESM.zip`

- archive SHA-256:
  `1D93DE8B177F7556525DBCA07D34F1D40880DA33F68DC44ECCF93BBC7CB0D563`;
- workbook:
  `Tameshige_et_al_codes_v251010/code_main/Figure6/Source Data 21.xlsx`;
- workbook SHA-256:
  `E78372214B1386A486B25C8340C19F22BC74D3382F80A9B36A2972CC3D35ADFB`;
- worksheet: `EPFL_phyllo-angle`;
- columns: `genotype`, `meristem`, `angle`.

The workbook contains 359 measured successive divergence angles from 58
meristems: 21 wild-type `Col`, 19 `e2`, and 18 `e1e2`. A new plant begins
whenever `meristem` resets to `1`. Within every inferred plant, the recorded
indices must be exactly `1,2,...,m`; otherwise the test stops as
measurement-limited.

## 3. Raw ARA coordinate

For a measured divergence angle \(\theta_i\) in degrees, define the directed
Phase-A placement coordinate

\[
\underbrace{x_{A,i}}_{\substack{\text{measured directed}\\
\text{handover on }0\to1}}
=
\underbrace{\frac{\theta_i}{360^\circ}}_{\substack{\text{fraction of one}\\
\text{complete placement turn}}}.
\]

The proposed Phi landmark is

\[
x_\phi=\phi^{-2}=0.38196601125.
\]

The reverse-side coordinate is

\[
\underbrace{x_{B,i}}_{\substack{\text{assigned mirror}\\
\text{on }1\to2}}
=
\underbrace{2-x_{A,i}}_{\text{ARA reversal}},
\]

with the Phi mirror at

\[
2-\phi^{-2}=\phi=1.61803398875.
\]

Only \(x_A\) is independently measured. \(x_B=2-x_A\) is forced by the
declared ARA symmetry and must be labelled **ASSIGNED MIRROR** in every result.

## 4. Development and confirmation split

Plant IDs are assigned in source-file order within genotype.

- odd plant IDs: development/split-half stability;
- even plant IDs: frozen confirmation;
- angles 1 and 2 initialize a plant trajectory;
- angles 3 onward are the held-out placement steps.

The source order is not claimed to be randomized. The split is a deterministic
stability check, not a pristine prospective trial.

## 5. Frozen constant rivals

All constants are fixed before scoring:

| Name | Turn fraction | Angle |
|---|---:|---:|
| one third | `1/3` | 120.000° |
| one over e | `1/e` | 132.437° |
| three eighths | `3/8` | 135.000° |
| **Phi** | `phi^-2` | 137.508° |
| close rational | `8/21` | 137.143° |
| two fifths | `2/5` | 144.000° |
| silver conjugate | `sqrt(2)-1` | 149.117° |

Two fitted controls are also reported:

- `development median`: wild-type odd-plant median, frozen before confirmation
  scoring;
- `plant early mean`: circular mean of that plant’s first two angles.

The `8/21` control is mandatory. A broad golden neighbourhood is not exact-Phi
specificity.

## 6. Endpoints

### P1 — ARA landmark recovery

On even wild-type plants, the median measured \(x_A\) for held-out angles must
lie within `0.01` of \(\phi^{-2}\). The assigned mirror is reported but cannot
count as a second pass.

### P2 — exact-Phi step specificity

For every fixed constant, calculate held-out absolute angular error

\[
e_i(c)=\left|\theta_i-360^\circ c\right|.
\]

Phi passes only if it has the smallest confirmation wild-type median error
among all fixed constants, including `8/21`. Fitted controls are reported but
do not decide this gate.

### P3 — cumulative carrier prediction

Let the first two observed steps establish the plant’s starting phase. For
each later step \(k\), predict its cumulative circular position by repeatedly
advancing the candidate constant. Score wrapped angular error in
\([0^\circ,180^\circ]\).

Phi passes only if it has the smallest confirmation wild-type median
cumulative error among fixed constants. The plant-early and development-median
fits remain controls.

### P4 — ordered non-overlap handover

Starting from an origin at zero, cumulatively place each measured divergence
angle on the unit circle. Before placement \(k\), calculate the largest open
gap among existing points. The best possible new point is its midpoint.

For the observed new point:

\[
\text{clearance score}_k
=
\frac{\text{distance to nearest existing point}}
{\tfrac12(\text{largest existing gap})}
\in[0,1].
\]

The frozen gate has two parts:

1. even wild-type plants must have a larger plant-median clearance score than
   both perturbed genotypes;
2. their actual order must beat `10,000` deterministic within-plant order
   shuffles with one-sided `p < 0.05`.

Both parts are required. This is the direct ARA “do not reoccupy the previous
space while remaining nearby” endpoint.

## 7. Secondary geometry

Report without changing the frozen verdict:

- full \(x_A\) and assigned \(x_B\) distributions by genotype;
- per-meristem-position medians;
- adjacent signed deviation pairs around Phi;
- whether two-step errors compensate or compound;
- clearance through each child depth;
- individual trajectories, not only population averages;
- development/confirmation agreement;
- mathematical constant-sequence benchmarks through horizons
  `N=4...55`.

The constant benchmark asks what a supplied generator does. It is not
empirical evidence that the plant selected that generator.

## 8. Verdict

Four equally weighted frozen gates are P1–P4:

- `4/4`: `SUPPORTED` for this empirical ARA cut, pending independent
  replication;
- `2–3/4`: `MIXED / SUGGESTIVE`;
- `0–1/4`: `NOT SUPPORTED`.

Because the source paper already identifies the golden-angle neighbourhood,
this run cannot exceed `SUGGESTIVE` as evidence that ARA independently found
Phi. It can still support or reject the *specific ARA mapping and ordered
handover mechanism*.

## 9. Falsifiers and boundaries

- Exact Phi loses P2 if any frozen rival has lower median error.
- A Phi-like center without order-sensitive clearance is not evidence for the
  proposed handover mechanism.
- The assigned `2-x` mirror is bookkeeping, not an observed second wave.
- Divergence angles do not independently measure radial growth, biochemical
  energy, TE-ARA fill, or a full three-dimensional sphere.
- These are flower-primordium placements, not sunflower seeds; the geometry is
  the relevant shared object.
- Source measurements may contain biological and measurement noise. Results
  must be reported by plant and genotype, with bootstrap intervals, rather
  than treating 359 angles as independent organisms.
