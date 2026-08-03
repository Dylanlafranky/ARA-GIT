# H2 v2 frozen protocol — longitudinal Phi / 3/8 river-motion test

**Prediction-ledger ID:** T319  
**Frozen:** 2 August 2026, after source-metadata review and before downloading
or opening any target numerical workbook  
**Dylan fidelity verdict:** confirmed after the context-compaction recheck:
`Continue`  
**Replaces:** H2 v1 only as a test of the longitudinal claim. H2 v1 remains a
reproducible perpendicular cross-section proxy.

## 1. Exact object being tested

- **Identity:** one continuous centreline water-flow path through one fixed
  experimental channel reach and flow run.
- **Ordered ARA axis:** source-defined upstream/start position is `0`; the
  downstream/end position is `2`.
- **Direction:** all measurements follow the direction of water travel.
- **Forbidden axis:** bank-to-bank position, lateral peak location, or a
  lateral thalweg coordinate cannot answer this test.

For source centreline distance (s), with the common eligible reach bounded by
(s_0) upstream and (s_1) downstream,

\[
x(s)=2\frac{s-s_0}{s_1-s_0}.
\]

The source's streamwise ordering controls orientation. If upstream and
downstream cannot be established from source metadata, the run is ineligible;
it is never reversed after seeing the result.

## 2. Public source selected without inspecting target values

Li, Xu, Bai and Lu, *Experiment on the Hydrodynamic Characteristics of
Plunging Flows in Bedrock Canyon Bends*, Dryad
[`10.5061/dryad.4xgxd25hg`](https://doi.org/10.5061/dryad.4xgxd25hg).

The source metadata states that:

- ADV measurements provide time-averaged and depth-averaged velocity along
  the channel centreline;
- water depth is supplied along that same centreline;
- five plain-bed runs (`PRUN1`–`PRUN5`) and three undulating-bed runs
  (`URUN1`–`URUN3`) are available;
- undulating-bed topography is also supplied.

These metadata facts were used to establish suitability. Numerical workbook
cells were not opened before this protocol was frozen.

## 3. Frozen observables

Each eligible run supplies two independently extracted longitudinal
coordinates over the same common sampled reach.

### 3.1 Motion coordinate

At every source-defined longitudinal station, use the source-provided
depth-averaged **streamwise** velocity (U_s(s)). The motion coordinate is the
raw station at which that along-path speed is greatest:

\[
x_{\rm motion}=x\!\left(\arg\max_s U_s(s)\right).
\]

If a source-provided (U_s(s)) series is not recoverable, the only permitted
fallback is a depth-average reconstructed from raw time-averaged streamwise
velocity (u_s(s,z)) by trapezoidal integration over the recorded vertical
profile, divided by the recorded sampled depth. The fallback must be declared
before its result is scored. Normalized ratios, transverse speed, total vector
magnitude, fitted velocity curves and smoothed peaks are forbidden
substitutes.

### 3.2 Connection/structure coordinate

Use source-measured water depth (D(s)) along the same centreline and run. The
structure coordinate is

\[
x_{\rm structure}=x\!\left(\arg\max_s D(s)\right).
\]

For undulating-bed runs, source bed topography may be shown as a secondary
structural trace, but it cannot replace the frozen water-depth observable or
rescue its verdict.

### 3.3 Ties and common support

- If several adjacent raw stations share the exact maximum, preserve the full
  plateau interval and use its arithmetic centre only for candidate-distance
  summaries.
- If non-adjacent stations tie, preserve every tied coordinate and mark the
  run `AMBIGUOUS` for winner counting.
- Motion and depth must share the same source-defined longitudinal support.
  Their intersection is fixed before maxima are extracted. Missing endpoints
  are trimmed symmetrically to that intersection; internal gaps are not
  interpolated.

## 4. Frozen ARA landmarks and controls

Motion/handover candidate:

\[
L_{\phi}=\{2-\phi,\phi\}
=\{0.38196601125,1.61803398875\}.
\]

Connection candidate:

\[
L_{3/8}=\{3/8,13/8\}
=\{0.375,1.625\}.
\]

Fixed rival pairs are

\[
L_{1/3}=\{1/3,5/3\},\quad
L_{0.4}=\{0.4,1.6\},\quad
L_{0.5}=\{0.5,1.5\},
\]

plus the ridge (L_1=\{1\}). For any coordinate (x), candidate distance is

\[
d(x,L)=\min_{\ell\in L}|x-\ell|.
\]

No landmark, mirror, orientation, window or smoothing rule may be altered
after values are opened.

## 5. Frozen predictions and gates

1. **Axis fidelity gate:** the analysed coordinate must be longitudinal and
   downstream-directed. Any lateral reading is invalid for this test.
2. **Shared-support gate:** motion and depth must be paired on the same sampled
   centreline interval within a run.
3. **Resolution gate:** exact Phi-versus-`3/8` separation can be adjudicated
   only when local raw coordinate resolution around the maximum is strictly
   smaller than
   \(|(2-\phi)-3/8|=0.00696601125\) ARA units. Otherwise exact separation is
   `INCONCLUSIVE`, irrespective of which candidate is numerically nearer.
4. **Motion gate:** among resolution-eligible, unambiguous runs,
   (x_{\rm motion}) prefers (L_\phi) to (L_{3/8}) and every fixed rival.
5. **Structure gate:** among resolution-eligible, unambiguous runs,
   (x_{\rm structure}) prefers (L_{3/8}) to (L_\phi) and every fixed
   rival.
6. **Replication gate:** report every run separately, then plain-bed,
   undulating-bed and all-run summaries. A pooled average cannot erase
   run-level disagreements.

The primary result is descriptive landmark recovery. No causal claim is made.
With eight runs, exact run counts and sensitivity to tied/invalid runs take
precedence over asymptotic p-values.

## 6. Plain-language prediction

Walk downstream through the same piece of channel. Mark where the
centreline current is fastest and, separately, where that centreline is
deepest. Put the upstream end at `0` and downstream end at `2`. Test whether
the fastest-flow location rests near the Phi handover and whether accumulated
depth rests near the nearby `3/8` connection landmark. Do not look sideways
across the river.

## 7. Falsifiers and honest verdicts

- `SUPPORTED IN THIS REALIZATION`: all fidelity/resolution gates pass and the
  two fields prefer their predeclared distinct candidates at run level.
- `MIXED`: the axis and data are valid but only one field or one bed family
  shows the declared preference.
- `NOT SUPPORTED`: a fixed rival wins or the declared field ordering reverses
  on resolution-eligible runs.
- `INCONCLUSIVE — RESOLUTION`: the along-path data are valid but cannot
  distinguish Phi from `3/8` at the raw sampling grain.
- `INVALID — CONSTRUCT`: the files do not expose a common directed
  longitudinal velocity/depth path matching this protocol.

## 8. AI additions and boundaries

- **AI operationalization:** source-provided depth-averaged streamwise
  velocity is the cleanest available measurement of maximum speed along the
  travel path.
- **AI control design:** mirrored fixed constants and an explicit raw-grid
  resolution kill gate.
- **Not measured:** a complete temporal `0→2→0` cycle, an independently
  observed opposite wave, TE-ARA energy, or a three-dimensional ARA sphere.
- A positive spatial result would support this longitudinal projection only;
  it would not establish Phi as a universal time vector.

