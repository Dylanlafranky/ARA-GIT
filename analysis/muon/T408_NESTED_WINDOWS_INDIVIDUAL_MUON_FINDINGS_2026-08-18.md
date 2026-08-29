# T408 — Nested parent and child windows in individual muons

Date: 18 August 2026  
Status: **directionally positive; frozen confirmation rule not supported**

## Question

After conditioning individual event-linked stopped muons on the previously
transferred large parent timing window, do the separately decompressed
same-lineage child ARA relations predict which charged-daughter signals fall
inside a smaller child handover window?

This is deliberately different from T407. T407 asked whether a fixed incoming
parent coordinate predicted later timing. T408 first selects the parent stage,
then decomposes the incoming four-counter structure into its two child
relations.

## Frozen windows

- Parent conditioning window: `0.568858–1.382809 microseconds`.
- Pure small child window: `0.714271–0.801804 microseconds`, the cumulative-ARA
  image of local `0.50–0.75`.
- Secondary observed small window: `0.714271–0.785615 microseconds`, the image
  of local `0.50–0.706306`.

Only events inside the parent window were scored. The pure endpoint is the
primary outcome. The observed endpoint is retained as a secondary descriptive
test and cannot replace a failed primary verdict.

## Individual sample

The two holdout runs contain `2,109` event-linked records in total. The parent
window retains `527` individual muons:

- `62/527 = 11.76%` lie in the pure small window;
- `51/527 = 9.68%` lie in the observed small window.

The calibration run supplies another `599` parent-window events. It alone was
used for training and gain normalization.

## Models

- `MG`: ordinary prompt charge, multiplicity and detector-depth geometry.
- `MP`: ordinary geometry plus parent ARA.
- `MN`: `MP` plus separately decompressed same-lineage child ARA coordinates
  and their signed/absolute relation.
- `MW`: the same nested construction after deliberately crossing the counter
  lineages; this is the geometric wrong-pair control.

The primary contrast is mean held-out log loss `MP-MN`. Positive values mean
the nested child relation improves prediction beyond the parent coordinate.

## Results

### Pure `0.50–0.75` window

- `MP-MN = +0.00237581` log-loss units.
- Both held-out runs are positive: `+0.00262848` and `+0.00211036`.
- `MN` beats the wrong-lineage control by `+0.00103748`.
- AUC rises from `0.51594` for `MP` to `0.54431` for `MN`.
- 12-block bootstrap 95% interval: `[-0.00099095,+0.00513850]`.
- Within-run permutation `p=0.175165`.
- Frozen gates passed: sample size, both runs positive and wrong-lineage
  control. Failed: strictly positive block interval and permutation.

Verdict: **not supported**.

### Secondary observed `0.50–0.706306` window

- `MP-MN = +0.00386585` log-loss units.
- Both held-out runs are positive: `+0.00575641` and `+0.00187966`.
- `MN` beats the wrong-lineage control by `+0.00198596`.
- AUC rises from `0.56321` for `MP` to `0.59946` for `MN`.
- 12-block bootstrap 95% interval: `[-0.00184017,+0.00796394]`.
- Within-run permutation `p=0.0327934`.
- Four of five frozen gates pass; only the block interval fails.

Verdict: **near-support directional signal, not confirmation**.

## Where the uncertainty comes from

The fifth chronological block of the 18 March run reverses sharply:

- pure `MP-MN = -0.01227996`;
- observed `MP-MN = -0.02218340`.

This one block is strong enough to keep both resampling intervals across zero.
It is not removed. It may represent a detector/channel regime or a genuinely
different local participation state; the current archive cannot distinguish
those explanations.

Channel topology is also material. The A-only incoming topology has a pure
small-window rate of `16.67%`, versus `9.75%` for events where both pairs are
present. The nested model underpredicts that enrichment. Thus the nested ARA
relation is not yet cleanly separated from channel availability.

## ARA interpretation

The result supports the methodological distinction Dylan expected:

- a parent landmark is a conditioning stage, not an exact individual child
  coordinate;
- individual child coordinates may be displaced by local participation;
- decomposing the children can carry information that a fixed parent band
  loses.

That interpretation is evidence-consistent but not confirmed by this test.
The pure result fails two frozen gates, and the secondary result fails its
chronological uncertainty gate.

## Physics boundary

The later linked signal is a charged-daughter candidate. Neither neutrino is
directly observed, and the archive has no individual muon-spin trajectory.
T408 therefore changes the probability of a later daughter-timing outcome; it
does **not** identify an exact neutrino-creation instant for one muon.

## Next strict test

Freeze the current window map and nested feature construction, then score new
dates or a second detector archive without retuning. Confirmation requires:

1. positive nested improvement in every new run;
2. a positive chronological block interval;
3. superiority to the crossed-lineage control;
4. no post-hoc exclusion of adverse blocks;
5. preferably, an independent spin-, daughter-direction- or
   missing-momentum relation for an Information³ lock.

Primary output directory:
`analysis/muon/T408_nested_windows_individual_muon/`.

