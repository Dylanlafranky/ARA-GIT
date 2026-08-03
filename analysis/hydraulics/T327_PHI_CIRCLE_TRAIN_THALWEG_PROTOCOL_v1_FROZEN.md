# T327 — frozen river thalweg Phi circle-train test

**Frozen:** 2 August 2026, before T327 endpoint calculation  
**Test ID:** `T327-PHI-CIRCLE-TRAIN-THALWEG-v1`  
**Originator of ARA/Phi geometry:** Dylan La Franchi  
**Formalisation and boundary audit:** Codex  
**Status:** direct ordered-path test using previously opened public river/flume
topography; not a blind source

## 1. Question

Does the ordered lateral movement of the deepest-bed path through successive
downstream cross-sections retain the ARA Phi circle-train increment more
strongly than fixed rational/irrational rivals, shuffled downstream order, and
matched non-thalweg paths through the same cross-sections?

This is distinct from T319. T319 measured absolute longitudinal maxima. T327
measures the ordered handover of a path across repeated downstream slices.

## 2. Source and eligible reach

Li, Xu, Bai and Lu (2024), Dryad DOI
`10.5061/dryad.4xgxd25hg`, *Experiment on the Hydrodynamic Characteristics of
Plunging Flows in Bedrock Canyon Bends*.

Primary workbook: `Bed-topography.xlsx`, SHA-256
`041FBFF2233E590AECFD9A5DFC08C84C5A17678A8DF1ABDAC667A21A2D823ED7`.

The source paper states that bend cross-sectional bathymetry slices were built
at five-degree intervals. The workbook exposes one common source grid of 41
bed measurements from radius `1000 mm` to `1400 mm` at each retained bend
angle. The maximal uninterrupted five-degree chain is predeclared as
`10,15,...,170 degrees` (33 slices). The isolated `0` and `180` slices are
excluded because their adjacent five-degree slice is absent; no missing slice
is interpolated.

The workbook was previously opened for T319 and its coordinate schema was
inspected to establish T327 eligibility. No T327 circle-train endpoint was
calculated before this protocol was frozen.

## 3. ARA-first declaration

1. **Identity:** the undulating bed through the retained constant-curvature
   bend.
2. **Time/order axis:** increasing source bend angle, following the published
   bend sequence from entry toward exit.
3. **Measurement slice:** one source-defined cross-section.
4. **ARA diameter within a slice:** inner-bank radius maps to `0`; outer-bank
   radius maps to `2`:

   \[
   x=2\frac{r-r_{\min}}{r_{\max}-r_{\min}}.
   \]

5. **Thalweg event:** the measured point with minimum bed elevation `Z` in
   each slice. Exact ties use the arithmetic mean of tied `x` coordinates and
   remain flagged.
6. **Ordered thalweg:** the sequence of those 33 lateral coordinates in
   downstream order.
7. **No smoothing:** no interpolation, fitted centreline, Fourier processing,
   curve regularisation, or after-result rotation is allowed.

## 4. Matched downstream controls

Within each cross-section, sort all 41 measured points by bed elevation from
lowest to highest. Rank 1 is the thalweg. Ranks 2 through 41 define 40 matched
non-thalweg feature paths through the same downstream slices.

Every path therefore has:

- the same number of events;
- the same downstream order;
- the same bank-to-bank normalization;
- the same raw spatial resolution;
- the same candidate and scoring rules.

The thalweg must outperform the distribution of these 40 paths to support
thalweg specificity. The rank paths are controls, not independent river
replicates.

Additional controls are:

- 10,000 permutations of downstream slice order for the thalweg;
- reversed downstream order;
- circular seam shifts of the thalweg sequence;
- fixed lateral-index paths, reported as persistence controls only.

## 5. Frozen Phi operator and rivals

For ordered path positions `x_i`, the observed signed circular increment is

\[
u_i=(x_i-x_{i-1})\pmod 2.
\]

Because the bend source fixes downstream order but does not assign which
lateral bank is the ARA Phi sign, every candidate is scored symmetrically in
both directions:

\[
L(u,\delta)=\min\{d_2(u,\delta),d_2(u,2-\delta)\}.
\]

This sign allowance is identical for every candidate and cannot be selected
separately by event.

Use the unchanged T325 increments:

- persistence `0`;
- one-third `2/3`;
- `1/e` control `2/e`;
- `3/8` child `3/4`;
- Fibonacci `8/21 = 16/21`;
- exact Phi `2/phi^2` (equivalent signed magnitude to `2/phi`);
- two-fifths `4/5`;
- silver conjugate `2(sqrt(2)-1)`;
- ridge `1`.

No free fit may be promoted above the fixed-candidate result. A free increment
is reported only as a diagnostic.

## 6. Frozen endpoints

### 6.1 Local child increments

For every feature-rank path, calculate its median symmetric circular loss to
each fixed increment. Report the thalweg's candidate ranking and its rank among
all 41 paths for each candidate.

### 6.2 Ordered parent carrier

Anchor at observed path position after the second slice. Predict all later
positions without re-anchoring:

\[
\widehat x_{a+h}=(x_a+s\,h\delta)\pmod2,
\qquad s\in\{-1,+1\}.
\]

The sign is selected once per complete path using the lower whole-path loss,
not separately per event. Report horizon profiles at `1,2,3,5,8,13,21`.

### 6.3 Ordered-return fingerprint

For lags `2,3,5,8,13,21`, calculate circular return distances within every
path and compare the observed profile with every fixed candidate's predicted
profile.

### 6.4 Order and specificity gates

- True downstream thalweg carrier loss must beat its 10,000 shuffled-order
  null with lower-tail `p<0.05`.
- Phi must have the lowest fixed-candidate parent-carrier loss.
- The thalweg's Phi loss must be below the median control-rank path and its
  empirical control rank must be reported. A strict specificity pass requires
  it to be in the best 10% of the 41 paths.
- Fibonacci-return agreement must not be worse than the best fixed rival.

## 7. Resolution gate

Report the raw lateral spacing adjacent to every selected feature. Exact Phi
versus nearby rational adjudication is allowed only when the observed grain or
multi-step phase separation resolves the relevant candidate difference.
Numerical nearness below source resolution is `INCONCLUSIVE — RESOLUTION` and
cannot be called a win.

## 8. Verdict boundary

Allowed verdicts:

- `SUPPORTED IN THIS THALWEG CUT`;
- `PARTIAL / MIXED`;
- `NOT SUPPORTED`;
- `INCONCLUSIVE — RESOLUTION`;
- `INVALID — CONSTRUCT`.

A positive result would establish an ordered-path crosswalk in this one flume
bed. It would not prove that physical thalwegs are universally Phi, that a
thalweg is defined by Phi, or that the complete ARA ontology is established.

