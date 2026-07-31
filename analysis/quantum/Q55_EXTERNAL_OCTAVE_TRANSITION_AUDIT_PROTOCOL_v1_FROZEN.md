# Q55 — external octave-transition audit protocol v1 (frozen)

**Frozen:** 2026-07-31, after the trajectory pattern had been visually
noticed and before the cross-run audit statistics were calculated.

**Status:** retrospective / exploratory. This audit can measure the strength
and specificity of the noticed pattern, but it is not a blind confirmation.

## 1. Dylan's proposed pattern

Verbatim observation:

> “It appears it is going up octave? It seems like they all have small nearby
> jumps first and then the movement gets progressively larger and larger and
> usually moves to another quadrant straight away”

Back-translation:

- **identity:** the fitted whole-circle external direction in each saved run;
- **axis:** circular external heading, expressed on the unchanged ARA
  directional coordinate;
- **ordered poles:** `0` is the declared direction and `2` is the exact
  half-turn opposite; `1` is the directional ridge;
- **observable:** the absolute circular change in external heading between
  adjacent source-time bins;
- **proposed sequence:** small local steps, followed by larger steps, with
  the larger steps commonly crossing a directional quadrant;
- **octave claim:** the change in step scale may be specifically organised by
  powers of two.

The test was accepted as exact enough when Dylan asked to run it “across all
the tested runs we just did.”

## 2. Included paths

The primary population is the twelve comparable paths displayed in
`3D models/q49_q52_partial_external_rotation_3d.html`:

1. Q49/Q50 same-lineage aggregate;
2. Q51 greedy `c2`;
3. Q51 landmax `c2`;
4. Q51 mimic `c2`;
5. Q52 fixed A;
6. Q52 fixed B;
7. Q52 alternating AB;
8. Q52 alternating BA;
9. Q52 random 520101;
10. Q52 random 520102;
11. Q52 random 520103;
12. Q52 random 520104.

Q53 is not pooled because it is recorded trapped-qutrit data with a different
sampling construction and target. Q54 is not pooled because it retained only
one eligible external tangent and therefore has no trajectory.

The compact path table is frozen from the displayed paths. Its rows preserve
source time, ARA coordinate, external heading and relative movement. The
canonical upstream artifacts remain:

- `Q50_SAME_LINEAGE_EXTERNAL_FLIP_BINS.csv`;
- `Q51_CROSS_ARCHIVE_EXTERNAL_REVERSAL_RESULTS.json` plus the public Q51
  archive extraction;
- `Q52_WHOLE_SPHERE_CONTINUATION_BINS.csv.gz`.

## 3. Primary step observable

For adjacent headings \(h_{i-1},h_i\), measured in turns,

\[
s_i
=
\left|
\operatorname{wrap}_{[-1/2,\,1/2)}
(h_i-h_{i-1})
\right|.
\]

Thus `s = 0` is no directional change and `s = 0.5` is a half-turn.

The movement guard for a step is the mean of the two adjacent
`mean_relative_movement` values, divided by that path's maximum step
movement. Primary calculations use all steps. Sensitivities retain steps at
or above `5%`, `10%` and `25%` of the path maximum.

Forbidden substitutes:

- internal cycle rotation;
- raw state-vector angle;
- physical energy;
- line thickness by itself;
- ARA coordinate displacement without circular wrapping;
- quadrant crossing alone.

## 4. Cross-run growth audit

For each path:

1. split its ordered steps into three equal-count chronological sections;
2. calculate median early, middle and late step size;
3. calculate
   \(R_{\rm late/early}=\operatorname{median}(s_{\rm late})/
   \operatorname{median}(s_{\rm early})\);
4. calculate Spearman rank correlation between step order and step size.

The pooled statistics are:

- number of paths with `R > 1`;
- median `log2(R)` across paths;
- number with positive Spearman correlation.

The null independently permutes step order within each path `50,000` times,
using seed `20260731`, while preserving every path's step values and length.

Exploratory growth is supported only if:

- at least `9/12` paths have `R > 1`;
- pooled median `log2(R) > 0`;
- permutation `p <= 0.05`;
- the direction survives the `10%` movement guard.

## 5. Q52 registered-boundary audit

Q52 has a pre-existing, independently declared continuation boundary at source
slice `500`. For each of its eight paths:

- historical steps end at or before `500`;
- continuation steps end after `500`;
- calculate the median post/pre step ratio.

Report:

- number of Q52 paths with post/pre ratio above one;
- median `log2(post/pre)`;
- the same within-path permutation null;
- all movement-guard sensitivities.

The eight Q52 paths are conditions sharing the same historical construction,
not eight independent physical replications.

## 6. Octave specificity

For each positive scale ratio \(R\), first remove direction by
\(M=\max(R,1/R)\). Define its distance from the nearest **non-trivial**
power of candidate base \(b\):

\[
d_b(R)
=
2\left|
\log_b M-n_b
\right|.
\]

where

\[
n_b=\max\!\left(1,\operatorname{round}(\log_b M)\right).
\]

The distance is `0` at an exact non-zero power, `1` halfway between adjacent
non-zero powers, and approaches `2` when there is effectively no scale
change. Excluding exponent zero is essential: otherwise every null ratio near
one would automatically look like the exact octave \(2^0\).

The within-path permutation null is used after the same non-trivial-power
rule. A separate scale-free check compares the observed median distance with
`50,000` sets of uniformly random logarithmic mantissas. Candidate bases are
also compared on the same normalized coordinate, allowing their different
lattice spacings to be compared fairly.

Predeclared bases:

- `2` — ARA octave hypothesis;
- `phi`;
- `e`;
- `3`;
- `10`.

Specific octave support requires all of:

1. base `2` has the smallest median normalized distance in the Q52
   boundary ratios;
2. its distance is smaller than the within-path permutation null at
   `p <= 0.05`;
3. the result survives the `10%` movement guard;
4. the generic cross-run growth gate passes.

This prevents any increase from being called an octave after the fact.

## 7. Quadrant transition audit

The circular heading is divided into four equal quarter-turn sectors relative
to the frozen Q49 reference heading
`0.4929567149606686`.

A **large step** is at least `0.125` turn. Report:

- all step counts;
- large-step counts;
- quadrant transitions;
- the share of large steps that cross quadrant.

This is descriptive because a sufficiently large circular step is
geometrically more likely to cross a quadrant. It cannot by itself establish
an octave.

## 8. Verdict vocabulary

- **Supported scale transition:** growth gates pass, regardless of base.
- **Supported ×2 octave transition:** growth and all octave-specificity gates
  pass.
- **Larger post-boundary response, not ×2-specific:** Q52 grows but the generic
  or base-specific octave gates fail.
- **Not supported:** no reliable step-scale growth.

No result from Q55 may be described as a new quantum law. Q52 is simulated
continuation data; Q49–Q51 are simulator-derived analyses. The result is about
the saved ARA external-direction trajectories.
