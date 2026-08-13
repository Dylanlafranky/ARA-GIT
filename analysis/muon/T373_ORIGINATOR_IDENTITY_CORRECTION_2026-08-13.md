# T373 — originator identity correction

**Recorded:** 13 August 2026, immediately after Dylan reviewed the liquid-argon result  
**Status:** material correction to interpretation; frozen computation retained  
**New lead:** nested child-to-parent, Phase-A-to-Phase-B projection; post-result and unconfirmed

## Correction

T373 changed the measured physical identity from solid CsI to liquid argon,
then treated the released source-model child cut and the liquid-detector
response cut as if they occupied the same ARA identity and rung. Dylan rejected
that flattening before accepting the result.

Dylan then supplied the missing refinement: the two are not unrelated
identities. The argon record retains the same stopped-pion/muon source relation
and CEvNS interaction as an embedded child, while the liquid medium and its
couplings form the next mixed parent response. The correct comparison is thus
**nested and cross-rung**, not same-coordinate and not disconnected.

In ARA language, the earlier solid cut is provisionally connection-heavy and
the liquid cut movement-heavy: a Phase-A-to-Phase-B handover of the retained
child relation. In established-physics language, the source lineage and
interaction class are shared, while target nucleus, state of matter, detector
response and backgrounds differ. The physical data do not yet prove that
solid/liquid state causes the coordinate shift.

The frozen numerical compatibility gate remains in the audit trail, but it no
longer supports a same-coordinate CsI-to-argon transfer claim. The identity
premise of that interpretation was invalid.

## Corrected working geometry

Liquid argon is provisionally classified as the more movement-heavy parent
mixture containing the earlier source relation as a child. If the pure child
contribution `0.5` is projected one further rung, its parent-scale contribution
is

\[
0.5/2=0.25.
\]

If the Phase-A-to-Phase-B liquid handover expresses that retained child on the
far side of the parent ridge, the new candidate is

\[
\boxed{x_H=1+0.25=1.25}.
\]

T373 observed

\[
x_H=1.238725,
\]

which is `0.011275` below `1.25`, or `0.902%` relative difference. The prompt
share required for exact `1.25` is `0.503231`; the event best fit was
`0.496709`. Fixing the fit at the exact `1.25` mixture changes the negative
log-likelihood by only `0.000703` from the profiled optimum.

## Evidence boundary

The numerical proximity is strong as a descriptive lead but not as evidence
of prediction: Dylan identified `1.25` after seeing `1.238725`, and the argon
likelihood is broad. T373 therefore cannot confirm the liquid quarter-above-
ridge rule.

The next valid test must freeze, before outcome inspection:

1. the shared child source relation and the liquid/movement-heavy parent
   assignment;
2. the proposed one-further-rung projection `0.5 -> 0.25`;
3. the predicted far-side handover `x_H=1.25`;
4. an independent liquid record or genuinely untouched liquid subset;
5. failure if the independently measured handover excludes `1.25` or is better
   explained by a different declared rung.

No result may again be transferred between different media, detector responses
or rungs without first asking whether the comparison is same-identity,
child-to-parent, parent-to-child or perpendicular/Di-ARA.
