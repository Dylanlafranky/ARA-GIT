# T409 report design

## Decision and audience

The report is for technical ARA and particle-data readers deciding whether the
three vertical structures marked in the T408 incoming-parent scatter are
stable ridges, chronological motion paths, or sampling/discretization effects.

The report must keep four distinctions visible:

1. presence of a density crest is not evidence that the crest travels;
2. the original frozen broad R3 test captured its lower interval edge;
3. the repaired `~1.35` crest sensitivity is post-hoc;
4. all coordinates come from the incoming charged-detector relation, not from
   direct neutrino observation.

## Reading order

1. Technical answer and the three recovered centres.
2. Chronological tracks and shuffled-order motion controls.
3. Occupancy/strength comparison.
4. Scope, definitions, estimator and validation.
5. Limitations, next test and open questions.

## Chart map

- `ridge_track`: resolved R1, R2 and repaired marked-R3 centres across twelve
  chronological blocks.
- `motion_control`: observed motion statistic against global-order and
  within-run shuffled 95th-percentile controls.
- `ridge_occupancy`: event counts in each recovered non-pole coordinate zone.

## Visual grammar

- Blue, gold and pink identify R1, R2 and marked R3; grey marks shuffle
  controls.
- Gaps are meaningful: they mark blocks where the sparse interior crest did
  not satisfy the fixed resolution rule.
- Neutral titles state what is plotted. Interpretation remains in adjacent
  narrative blocks.
- Counts and p-values stay visible in tables/tooltips so the weaker third crest
  is not visually promoted to the strength of R1/R2.

## Semantic rules

- `motion_M` is weighted root-mean-square displacement from the pooled centre.
- A low upper-tail permutation p-value means chronological displacement exceeds
  shuffled event order at this block scale.
- The T409B `1.395` result is the relevant marked upper-interior crest. T409's
  broad R3 maximum at `1.180` is retained only as an edge-capture failure.
- “Not travelling” means not resolved beyond chronological sampling noise in
  this coordinate and dataset; it does not rule out motion in a different ARA
  cut or unmeasured anti-phase.
