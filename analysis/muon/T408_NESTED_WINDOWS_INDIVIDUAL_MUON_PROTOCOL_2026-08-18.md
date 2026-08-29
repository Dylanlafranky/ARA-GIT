# T408 — nested handover windows in individual muons

**Frozen:** 18 August 2026, before T408 event-window counts, model fitting or
holdout scoring  
**Status:** registered retrospective individual-event transfer  
**Individual source:** T379 public QuarkNet DAQ-6845 event-linked stopped-muon
records  
**Population source:** the previously frozen T400 cumulative child coordinate

## Question

Does the smaller child-of-child completion interval carry individual pre-decay
information only when it is kept inside its larger parent handover window?

T407 tested fixed bands on the incoming parent coordinate alone. T408 instead
keeps the two scales separate:

1. the larger population handover interval defines which individual decay
   events belong to the parent transition;
2. the smaller interval inside it defines the child-of-child completion
   outcome;
3. the incoming four-counter pulse is decompressed into its parent relation
   and its two internal child relations before any outcome is inspected.

## Who / what / when / where / why / how

- **Who:** the same 2,396 calibration and 2,109 held-out T379 stopped-muon
  records, preserving acquisition-run chronology.
- **What:** predict whether one linked charged-daughter arrival falls in the
  smaller completion interval rather than elsewhere in the larger handover
  interval.
- **When:** incoming prompt counter information is measured first; the linked
  daughter arrives `0.30–10.0 microseconds` later. Only the previously frozen
  larger T400 time interval is used for the primary classification.
- **Where:** the larger interval is T400's objective window
  `[0.568857971327256, 1.3828086704815923] microseconds`. Inside it, the
  smaller pure interval is found by monotone interpolation of the saved T400
  map between local child ARA `0.5` and `0.75`.
- **Why:** a parent or population cut can compress child asymmetry. Testing a
  narrow band on that parent coordinate may therefore miss the individual
  relation even when a nested child relation exists.
- **How:** fit calibration-only logistic event models, freeze them, and score
  the two held-out runs by individual log loss. The primary comparison is a
  nested two-child ARA model versus a parent-only ARA model, not versus a
  memoryless population average.

## Frozen windows

Let `t(x)` be monotone interpolation of the already saved T400 relation
`local_child_ara -> time_us`.

- **Large parent handover:**
  `W_P = [0.568857971327256, 1.3828086704815923] microseconds`.
- **Primary small pure-completion interval:**
  `W_G75 = [t(0.5), t(0.75)]`.
- **Secondary observed-completion interval:**
  `W_G706 = [t(0.5), t(0.7063064837018814)]`.

The observed interval is a sensitivity comparison. It cannot replace the
primary pure endpoint after inspection.

For events whose linked daughter lies in `W_P`, the binary outcome is `1` when
it lies in the selected smaller interval and `0` when it lies elsewhere in
`W_P`. Events outside `W_P` are reported and visualised but do not enter the
primary nested-window classifier.

## Frozen incoming ARA decomposition

The calibration-normalised prompt counters are `q1, q2, q3, q4`. Define the
existing parent children

\[
A=q_1+q_2,\qquad B=q_3+q_4,\qquad
x_P=\frac{2B}{A+B}.
\]

When their denominators are present, decompress each child into its own
two-pole relation:

\[
x_A=\frac{2q_2}{q_1+q_2},\qquad
x_B=\frac{2q_4}{q_3+q_4}.
\]

For an absent pair, its signed and absolute child coordinates are set to zero
and a separate presence flag is retained. The frozen nested summaries are

\[
m_C=\frac{(x_A-1)+(x_B-1)}{2},
\qquad
d_C=(x_A-1)-(x_B-1),
\qquad
o_C=(x_A-1)(x_B-1).
\]

No daughter amplitude, daughter channel, daughter time or outcome-derived
quantity enters these predictors.

## Frozen models

All continuous columns are standardised using calibration events only. All
models use a fixed weak L2 penalty selected before fitting.

1. **MG — ordinary detector geometry:** `log(Q)`, prompt multiplicity and
   prompt depth.
2. **MP — parent ARA:** MG plus `x_P-1`, `|x_P-1|`, and the signed-parent by
   depth interaction used in the T379 ARA construction.
3. **MN — nested ARA:** MP plus child presence flags, `m_C`, `d_C`, `o_C`,
   `|x_A-1|` and `|x_B-1|`.
4. **MW — wrong-lineage control:** MP plus the same summaries formed from
   crossed pairs `(q1,q3)` and `(q2,q4)` instead of the physical within-pair
   children.

The primary contrast is `logloss(MP) - logloss(MN)` on holdout. Positive is
better for the nested child model. `MG -> MP` is reported separately so a
parent effect cannot be mislabelled as a grandchild effect.

## Frozen gates

The nested individual relation is supported for a window only if all hold:

1. at least 50 calibration and 50 held-out parent-window events, with at least
   20 positive smaller-window outcomes in each split;
2. `MN` improves mean log loss over `MP` in both held-out runs separately;
3. a 12-block run-stratified bootstrap 95% interval for
   `logloss(MP)-logloss(MN)` is strictly above zero;
4. `MN` beats the wrong-lineage `MW` model on pooled holdout log loss;
5. within-run outcome permutation gives an add-one upper-tail `p <= 0.05` for
   the observed `MP-MN` improvement.

The primary verdict follows `W_G75`. `W_G706` is labelled as secondary. A
secondary pass cannot silently replace a primary failure.

## Required outputs

- exact interpolated window boundaries and class counts;
- calibration and held-out model scores, by run and pooled;
- chronological-block uncertainty and permutation control;
- event-level held-out predictions with named source run and event index;
- a visual showing the larger window, both smaller windows, child geometry and
  fixed-rule individual examples;
- an independent saved-output validator.

## Interpretation boundary

This is an individual muon-to-visible-daughter test. A positive result would
show that the incoming nested counter relation changes the probability that
the same event closes in the smaller population-derived time interval. It
would not directly observe either neutrino, identify two neutrino flavors, or
determine a deterministic birth instant. A negative result would reject this
specific nested detector cut, not the existence of lower-rung asymmetry in an
unmeasured spin or neutral channel.
