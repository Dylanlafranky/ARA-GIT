# T351 frozen protocol v1 — progressive zipper transfer

**Frozen:** 11 August 2026, before implementation or scoring  
**Evidence class:** synthetic known-referee causal instrument calibration  
**Claim packet:** `T351_PROGRESSIVE_ZIPPER_TRANSFER_CLAIM_PACKET_v1.md`

## WHO

Two lower-rung ARA strands contain ordered child pairs (zipper teeth). A parent
front moves along those pairs. Calibration and untouched holdout families vary
tooth count, event duration, approach width, coupling rate, response noise and
seed.

## WHAT

At every causal prefix retain two independent measurements:

1. **Candidate geometry `G`:** ARA circular proximity of the declared child
   pairs and whether their separation is closing near the present front.
2. **Connection response `K`:** rolling same-pair response coherence under an
   independent, seeded perturbation. The detector does not receive hidden edge
   strengths or regime labels.

Also retain:

- open mismatch `U`, directly measured from child-pair phase separation;
- detected lock-on and unlock order;
- parent-front position and velocity;
- a causal ordered-lock history signature.

`K` is never defined as `1-U`, `2-U`, a TE-ARA residual, or another bookkeeping
complement. The two channels can therefore disagree.

## WHEN

Score complete forward events, an interrupted event with a middle hold, and a
forward-then-reverse event. All prefix features are causal. Final endpoints and
hidden referee labels are unavailable to the detector.

## WHERE

Child phase positions are represented on the ARA circumference `x in [0,2)`.
The front coordinate is an ordered cross-rung position from the first to final
child. A parent closure occurs only after the final child position is reached.

## WHY

T350 showed that ordered history develops early and survives an identical
suffix, while the local current state accurately locates the final boundary.
T351 asks whether the more specific zipper interpretation can be operationally
separated from a history-only description: do lower-rung connections visibly
form behind a moving seam, or does phase proximity merely look like locking?

## HOW

### Synthetic referee regimes

- **progressive zip:** hidden edges form from sustained same-pair contact and
  persist behind the advancing front;
- **memory-only mimic:** exact progressive phase geometry with independent
  response channels and no hidden edges;
- **late snap:** exact progressive phase geometry, but hidden edges activate
  only at final closure;
- **false seam:** the visible proximity order is retained but response coupling
  is assigned to a frozen wrong-partner permutation;
- **interrupted zip:** progressive regime with a stationary middle interval;
- **reverse unzip:** progressive locking followed by a reversed front and
  ordered edge release.

The hidden edge process generates response data but is not read during
prediction. Candidate geometry and connection response are calculated by
different formulas.

### Calibration and holdout

Calibration fixes all windows, thresholds and gates. Holdout changes:

- tooth counts;
- durations;
- approach widths;
- connection rates;
- response noise;
- seeds.

No holdout value may alter a formula, threshold or declared regime comparison.

### Frozen gates

1. **Z1 pre-closure construction:** in progressive holdout events, median share
   of final independently measured Connection present by `80%` parent progress
   is at least `0.55`.
2. **Z2 ordered local locks:** median Spearman correlation between child order
   and detected lock order is at least `0.80` in progressive holdout events.
3. **Z3 causal handover:** the connection-response rise must not systematically
   lead candidate compatibility; median detected `K-G` onset lag must lie in
   `[0, 0.15]` of event duration.
4. **Z4 interrupted construction:** during the frozen pause, median connection
   response increases by at least `0.05` while median absolute parent-front
   velocity is below `1e-10` in normalized child positions per tick.
5. **Z5 reverse release:** median Spearman correlation between forward lock
   order and chronological reverse-event unlock order is at most `-0.75`.
6. **Z6 retained lower-rung response:** median post-front same-pair response
   coherence is at least `0.65` in progressive events and at most `0.25` in the
   memory-only mimic.
7. **Z7 independent discrimination:** holdout AUROC for progressive versus
   memory-only is at least `0.90` with the independent response channel.

All seven must pass for `SUPPORTED [progressive zipper signature is measurable
under this synthetic instrument]`.

### Necessary non-identifiability control

Progressive and memory-only regimes have exactly the same phase geometry.
Geometry-only AUROC must remain in `[0.49,0.51]`. This is a required boundary,
not a failure: without an independent connection-bearing consequence, hidden
Connection cannot be inferred from identical visible paths.

### Late-snap and false-seam controls

- At `80%` progress, late-snap Connection share must be below `0.15`.
- Same-pair response in the false seam must be at least `0.25` lower than in the
  progressive regime on the holdout median.

These controls are reported separately and cannot rescue a failed primary gate.

## LEAKAGE CONTROLS

- All prediction features are causal.
- Regime labels and hidden edge strengths are referee truth only.
- Calibration and holdout parameter grids do not overlap.
- Memory-only and progressive phase arrays must match to numerical precision.
- Independent response perturbations are seeded but unavailable as labels.
- Failed gates and non-identifiability must be preserved in the report.

## CHART CONTRACT

Create one static research figure with:

1. ARA child positions and the advancing seam;
2. candidate geometry versus independent Connection through time;
3. progressive, memory-only and late-snap comparison;
4. interrupted-pause construction;
5. forward lock versus reverse unlock order;
6. frozen gate and boundary scorecard.

Use blue and gold roots, neutrals for controls, direct labels, honest fixed
scales and visible caveats. Export CSV, JSON, Markdown and PNG artifacts and
inspect the rendered figure before reporting.

## EVIDENCE BOUNDARY

This is an instrument calibration on generated known-referee processes. A pass
shows that the proposed signature is distinguishable when lower-rung Connection
has an independently observable consequence. It does not by itself establish a
new physical connection process in public data.

