# T319 report — longitudinal Phi-motion / 3/8-structure test

**Date:** 2 August 2026  
**Frozen protocol:** `H2_LONGITUDINAL_PHI_THREE_EIGHTHS_PROTOCOL_v2_FROZEN.md`  
**Protocol SHA-256:** `D4E3D7ECE8A7C1ADA9568AE609C84135A6A19F0497D1E57115C4CCF59B6884AA`  
**Result:** **INCONCLUSIVE — RESOLUTION**  
**Independent validation:** **PASS, 55/55 checks**

## Answer first

The corrected longitudinal ARA cut was successfully constructed and measured.
This test follows water in its direction of travel, rather than measuring
sideways across the channel.

The public data are not fine enough to distinguish the two predeclared nearby
landmarks. Phi's low-side point is

\[
2-\phi=0.38196601125,
\]

while the proposed cooled/connection point is

\[
3/8=0.375.
\]

Their separation is only `0.00696601125` on the ARA `0..2` axis. The local
raw station spacing around the observed maxima ranged from `0.104824` to
`0.333333`. Every run therefore fails the frozen resolution gate by a wide
margin. Numerical nearness to either landmark cannot honestly decide between
them.

The coarse, directly visible pattern does **not** support the proposed
field separation:

- none of the seven motion maxima had Phi as its closest predeclared
  candidate on the raw grid;
- none of the seven structure maxima had `3/8` as its closest predeclared
  candidate;
- all four plain-bed runs repeated the same coarse placement: motion maximum
  at upstream boundary `x=0`, structure maximum at `x=5/3`;
- the three undulating-bed runs disagreed with one another.

Those observations matter, but they do not override the frozen resolution
rule. The formal verdict is therefore **inconclusive due to sampling
resolution**, with **no positive evidence for the declared Phi-motion /
3/8-structure separation in this dataset**.

## What was measured

The public source is Li, Xu, Bai and Lu, *Experiment on the Hydrodynamic
Characteristics of Plunging Flows in Bedrock Canyon Bends*, Dryad
[`10.5061/dryad.4xgxd25hg`](https://doi.org/10.5061/dryad.4xgxd25hg).

For each eligible experimental run:

1. The common centreline distance interval was fixed from the released
   velocity and depth workbooks.
2. Source distance increased from upstream/start `0` to downstream/end `2`:

   \[
   x(s)=2\frac{s-s_0}{s_1-s_0}.
   \]

3. The **motion cut** was the untouched station containing maximum
   depth-averaged streamwise speed \(U_s\).
4. The **connection/structure cut** was the untouched station containing
   maximum centreline water depth.
5. No interpolation, smoothing, Fourier processing, fitted peak, or
   after-result orientation change was used.

The source workbook does not repeat \(U_s\) as a standalone column. It supplies
both local \(u_s\) and the source-normalized ratio \(u_s/U_s\). The same
source \(U_s\) value was recovered algebraically at every vertical sample:

\[
U_s=\frac{u_s}{u_s/U_s}.
\]

The median of those repeated algebraic copies was used at each station. This
extracts the authors' own normalizer; it does not fit a new velocity model.

## Run-level result

| Run | Bed | Motion maximum \(x\) | Structure maximum \(x\) | Closest coarse motion candidate | Closest coarse structure candidate | Local resolution (motion / structure) | Exact verdict |
|---|---|---:|---:|---|---|---:|---|
| PRUN1 | plain | 0.000000 | 1.666667 | 1/3 mirror | 1/3 mirror | 0.111111 / 0.333333 | inconclusive |
| PRUN2 | plain | 0.000000 | 1.666667 | 1/3 mirror | 1/3 mirror | 0.111111 / 0.333333 | inconclusive |
| PRUN3 | plain | 0.000000 | 1.666667 | 1/3 mirror | 1/3 mirror | 0.111111 / 0.333333 | inconclusive |
| PRUN5 | plain | 0.000000 | 1.666667 | 1/3 mirror | 1/3 mirror | 0.111111 / 0.333333 | inconclusive |
| URUN1 | undulating | 0.473098 | 1.263451 | 1/2 mirror | 1/2 mirror | 0.131725 / 0.131725 | inconclusive |
| URUN2 | undulating | 0.104824 | 1.263451 | 1/3 mirror | 1/2 mirror | 0.104824 / 0.131725 | inconclusive |
| URUN3 | undulating | 0.341373 | 0.000000 | 1/3 mirror | 1/3 mirror | 0.131725 / 0.104824 | inconclusive |

`PRUN4` is ineligible because the released water-depth workbook contains no
matching `PRUN4` depth series. All other released paired runs are included.

## ARA reading and established hydraulic reading

| ARA view | Established hydraulic view |
|---|---|
| The axis is now the intended longitudinal `0→2` cut. | Centreline distance follows the current from the bend entrance through the measured reach. |
| Speed is the motion/time-oriented observable. | \(U_s\) is the depth-averaged velocity component tangent to the channel centreline. |
| Water depth is the accumulated connection/structure observable. | Depth records the free-surface/bed-controlled hydraulic state along the same centreline. |
| Phi and `3/8` are too close for this measurement grain. | Sampling intervals are roughly 15–48 times larger than the landmark separation at the peak locations. |
| The parent-level result cannot recover the proposed handover distinction. | A denser longitudinal station grid, or a genuinely temporal particle/feature track, is required. |

## What this test does and does not say

It establishes that the corrected test object is measurable and reproducible.
It also shows that this particular public dataset is a poor discriminator for
two landmarks separated by less than `0.007` ARA units.

It does **not** show that the maxima are Phi, that `3/8` is a cooled Phi state,
or that a universal time vector has been measured. It also does not cleanly
falsify those larger claims, because the preregistered spatial resolution gate
failed in every run.

The visible profiles provide a useful warning: choosing a continuous-looking
river record does not guarantee that the recorded station grid resolves the
handover geometry. The maximum can also fall on a measurement boundary, as it
does for the four plain-bed motion profiles and one undulating structure
profile.

## Post-run construct refinement — extrema proxy versus handover path

The later `Phicircles.png` construction identifies a more specific operator
than the frozen T319 maxima test. The standard ARA circle has diameter `2`.
The circle whose diameter runs from `2-phi` to `phi` is ridge-centred and has
diameter `2/phi`. Repeating those two tangent circle trains creates a relative
phase step of `1/phi` of the base period.

T319 did **not** measure that step. It measured two absolute longitudinal
locations:

\[
s_v=\arg\max_s U_s(s),
\qquad
s_d=\arg\max_s D_{\rm centre}(s).
\]

A direct thalweg handover construction instead needs an ordered deepest-point
path across successive cross-sections, for example

\[
y_t(s)=\arg\max_y D(s,y)
\]

under a predeclared cross-section and tie rule, followed by the signed phase or
contact displacement from one retained slice to the next. A thalweg is not
defined as Phi in established hydraulics; Phi is the ARA hypothesis to be
tested on that ordered path.

Therefore T319 should be read as a **valid longitudinal-extrema proxy, not a
direct thalweg/Phi-circle handover test**. This post-run distinction does not
alter its frozen result or resolution verdict. It identifies a different
future observable and prevents the maxima result from being promoted as a
test of the newly derived `2/phi` increment.

## Required next dataset

To adjudicate Phi versus `3/8` on the same construction, a source must provide:

- a directed longitudinal velocity and structure record on the same support;
- raw spacing finer than `0.006966` after mapping the support to ARA `0..2`;
- preferably internal maxima rather than maxima at an observed boundary;
- enough independent runs to test whether the field ordering repeats.

For the direct Phi-circle/thalweg operator, the source must additionally
provide dense repeated cross-sections or time-resolved trajectories from which
successive handover displacement can be calculated without fitting the target
constant. The frozen primary should score the `2/phi` increment (or `1/phi` of
one standard ARA period), held-out phase prediction, and Fibonacci
near-closures against rational and fitted controls.

For reaches with the lengths used here, the needed physical station spacing
is approximately:

- plain reach: less than `0.0131 m` (about `1.31 cm`);
- undulating reach: less than `0.0166 m` (about `1.66 cm`).

The released station intervals are much coarser. A high-resolution tracer,
particle-track, flume scan, or dense time-resolved centreline measurement is
the appropriate next target.

## Reproduction artifacts

- `t319_longitudinal_phi_three_eighths.mjs` — source extraction and frozen test
- `validate_t319_longitudinal_phi_three_eighths.mjs` — independent source-level recomputation
- `plot_t319_longitudinal_phi_three_eighths.py` — untouched-profile figure
- `T319_LONGITUDINAL_PHI_THREE_EIGHTHS_RESULTS.json` — complete machine-readable result
- `T319_LONGITUDINAL_PHI_THREE_EIGHTHS_RUNS.csv` — run-level maxima and scores
- `T319_LONGITUDINAL_PHI_THREE_EIGHTHS_STATIONS.csv` — every shared raw station
- `T319_LONGITUDINAL_PHI_THREE_EIGHTHS_CANDIDATE_SUMMARY.csv` — candidate distances
- `T319_LONGITUDINAL_PHI_THREE_EIGHTHS_PAIR_SUMMARY.csv` — declared versus swapped pair summary
- `T319_LONGITUDINAL_PHI_THREE_EIGHTHS_VALIDATION.json` — 55 independent checks and hashes
- `T319_LONGITUDINAL_PHI_THREE_EIGHTHS_FIGURE.png` — visual audit

## Scientific status

**Valid construct; exact result inconclusive due to resolution; no positive
support in the coarse observed maxima.** This is a useful negative/limiting
result and should remain in the record unchanged if a finer dataset is tested
later.
