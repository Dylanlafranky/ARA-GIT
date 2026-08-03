# T326 — frozen independent-plant Phi circle-train replication

**Frozen:** 2 August 2026, before T326 endpoint calculation  
**Test ID:** `T326-PHI-CIRCLE-TRAIN-INDEPENDENT-PLANTS-v1`  
**Originator of ARA/Phi geometry:** Dylan La Franchi  
**Formalisation and boundary audit:** Codex  
**Status:** independent-source replication of the unchanged T325 operator

## 1. Question

Does the scale separation found in T325 repeat in independent ordered plant
lineages: local child placements preferring the cooled `3/8` approximation,
while cumulative ordered parent placement is better described by the exact Phi
circle-train step?

No candidate, orientation rule, anchor, loss, or control may be retuned from
T325 after endpoint calculation begins.

## 2. Sources and exposure boundary

### 2.1 Primary replication: Arabidopsis

Landrein (2015), Zenodo DOI `10.5281/zenodo.20040331`, accompanying
*Meristem size contributes to the robustness of phyllotaxis in Arabidopsis*
(DOI `10.1093/jxb/eru482`). The archive supplies ordered main-stem divergence
angles for four genotypes under two growth conditions:

- `Col0-JL`, `Col0-JC-JL`;
- `WS4-JL`, `WS4-JC-JL`;
- `clasp1-JL`, `clasp1-JC-JL`;
- `bot17-JL`, `bot17-JC-JL`.

The common primary input is each published calculated-divergence file. Raw
angular-position files are available for the WS4 and bot1-7 cohorts and are
used only to verify the published divergence reconstruction. They are not
counted as independent evidence.

The archive and the first rows/schema were inspected to establish eligibility.
No T326 ARA endpoint was calculated before this protocol was frozen.

### 2.2 Resolution control: Cyanella

Robertson et al. (2025), Zenodo DOI `10.5281/zenodo.14989473`, accompanying
*Spiral phyllotaxis predicts left-right asymmetric growth and style deflection
in mirror-image flowers of Cyanella alba* (DOI
`10.1038/s41467-025-58803-5`).

The source records ordered divergence angles in 16 bins of `22.5 degrees`.
Bins increase clockwise, bin 7 represents the clockwise golden-angle branch,
and bin 11 represents its counter-clockwise counterpart when read from older
to younger organs. This source is predeclared as a **resolution control**:
its bin width is much larger than the `2.507764 degree` separation between
`3/8 = 135 degrees` and exact Phi `= 137.507764 degrees`. It cannot confirm or
falsify that fine distinction, regardless of numerical winner.

## 3. ARA-first declaration

1. **Identity:** one plant retained through its recorded organ order.
2. **Child event:** one published divergence angle between successive organs.
3. **Parent carrier:** the cumulative ordered angular placement of those child
   events.
4. **Parent cycle:** `360 degrees`, mapped onto ARA `0..2`.
5. **Direction:** the source's recorded order. No sequence is reversed after
   the result is seen.
6. **Anchor:** the cumulative observed position after the first two child
   events. Events three onward are evaluated without re-anchoring.
7. **Missing data:** no interpolation. A lineage must have at least three valid
   ordered angles.
8. **Grain:** plants, not individual angles, are the independent clusters.

## 4. Frozen mapping and candidates

For a directed angle `theta` in degrees,

\[
u=\frac{\theta}{180}\pmod 2,
\qquad
p_i=\left(\sum_{j\le i}u_j\right)\pmod 2.
\]

Landrein angles retain their published direction. Cyanella lineages are
chirality-normalised using the source-declared bin convention before scoring:
bin centres are `(bin-1)*22.5 degrees`; counter-clockwise sequences are
reflected to the common clockwise minor branch. Mixed-direction lineages are
reported separately and cannot rescue the resolution-control verdict.

The circular loss is

\[
d_2(x,y)=\min(|x-y|,2-|x-y|).
\]

The unchanged fixed increments are:

| Candidate | ARA increment |
|---|---:|
| persistence | `0` |
| one-third phase | `2/3` |
| matched irrational `1/e` | `2/e` |
| cooled `3/8` child | `3/4` |
| Fibonacci rational `8/21` | `16/21` |
| exact Phi | `2/phi^2` |
| two-fifths phase | `4/5` |
| silver conjugate | `2(sqrt(2)-1)` |
| ridge | `1` |

No free development fit is a competitor in the primary replication. A free
carrier fit may be reported only as a diagnostic after all fixed scores.

## 5. Frozen endpoints

### 5.1 Local child endpoint

For every plant and candidate, calculate the median `d2(u_i, delta)` over all
eligible events from event three onward. Aggregate by the median across plants,
with a plant-cluster bootstrap interval for candidate-score differences.

The declared child result is supported only when `3/8` has the lowest fixed
candidate loss. Exact Phi versus `3/8` is also reported directly.

### 5.2 Ordered parent-carrier endpoint

From the observed anchor after event two, predict every later cumulative
position with

\[
\widehat p_{a+h}=(p_a+h\delta)\pmod 2.
\]

Aggregate median circular error within plant and then across plants. Exact Phi
passes the parent endpoint only when it has the lowest fixed-candidate loss.
Report horizon profiles for `h=1,2,3,5,8,13` when supported by the lineage.

### 5.3 Order, lineage, and return controls

- **Within-plant order shuffle:** hold the first two angles fixed and shuffle
  later angles 10,000 times.
- **Broken lineage:** join residuals across different plants while preserving
  the marginal angle distribution.
- **Adjacent compensation:** reuse T325's residual compensation ratio.
- **Fibonacci returns:** compare observed circular returns at lags
  `2,3,5,8,13` with every fixed candidate.
- **Reverse order:** report as a directional sensitivity, not an alternative
  fitted orientation.

The true-order parent loss must be in the lower tail (`p<0.05`) of its shuffle
distribution for order-specific support.

## 6. Cohort and robustness reporting

Report:

- every genotype × growth-condition cohort separately;
- wild types (`Col0`, `WS4`) and mutants (`clasp1`, `bot1-7`) separately;
- all eligible Landrein plants pooled only after cohort results;
- source raw-position reconstruction agreement where available;
- removal of the longest and shortest lineage;
- medians and means;
- all candidate ranks and pairwise Phi-versus-`3/8` differences;
- source hashes and complete event-level output.

## 7. Verdict boundary

Allowed primary verdicts are:

- `REPLICATED SCALE SPLIT` — `3/8` wins the child endpoint, Phi wins the
  parent endpoint, and real order beats shuffled order;
- `PARTIAL / MIXED` — only part of that declared pattern repeats;
- `NOT REPLICATED` — fixed rivals win or the declared ordering reverses;
- `INCONCLUSIVE — RESOLUTION OR CONSTRUCT`.

Cyanella can return only `COMPATIBLE`, `NOT COMPATIBLE AT COARSE SCALE`, or
`INCONCLUSIVE — RESOLUTION`; it cannot establish exact Phi versus `3/8`.

No result proves universal Phi, a complete ARA sphere, or a causal plant
mechanism.

