# T408 report design

## Decision and audience

The report is for technical ARA and particle-data readers deciding whether a
large parent timing window and a smaller nested child window transfer to
individual event-linked stopped muons.

The reader must be able to distinguish:

1. a positive directional event-level result;
2. a fully supported result under the frozen gates;
3. a charged-daughter timing proxy from direct neutrino observation.

## Reading order

1. Technical verdict and headline metrics.
2. Model comparison and the nested child geometry.
3. Chronological uncertainty and channel-topology alternatives.
4. Scope, definitions, frozen method and gates.
5. Limitations, next test and open questions.

## Chart map

- `model_logloss`: grouped held-out log loss for the ordinary, parent,
  same-lineage nested and wrong-lineage models.
- `child_geometry`: one point per parent-conditioned held-out muon on the two
  child ARA coordinates, coloured by the observed pure small-window outcome.
- `block_improvement`: parent-minus-nested log-loss improvement across the 12
  chronological uncertainty blocks for both outcome windows.
- `topology_rates`: observed small-window rates for both-pair, A-only and
  B-only incoming counter topologies.

## Visual grammar

- Use a restrained blue/gold categorical palette for the two-root comparison
  and neutral reference lines for zero/no-improvement.
- Keep model and outcome names visible; do not rely on colour alone.
- Preserve the full 527-event reviewed snapshot for the scatter rather than a
  decorative aggregate.
- Neutral chart titles state what is plotted; subtitles state the relevant
  interpretive boundary.

## Semantic rules

- Positive `MP-MN` means the same-lineage nested child model has lower held-out
  log loss than the parent-only model.
- The pure `0.50-0.75` outcome is primary. The observed `0.50-0.706306`
  outcome is secondary and cannot replace a failed primary verdict.
- The report says `not supported` when either registered uncertainty gate
  fails, even when all whole-run point estimates are positive.
- “Individual muon” means one event-linked incoming cluster and later charged
  daughter candidate. It does not mean that either neutrino was observed.

