# Q23 frozen protocol — connection-web and logical-bit parent ARA

**Frozen:** 26 July 2026  
**Source:** Google Willow public surface-code deposit, DOI `10.5281/zenodo.13273331`  
**Untouched patch:** distance 7, `d7_at_q6_7`  
**Outcome status at freeze:** no `obs_flips_actual.b8` file extracted or present

## ARA question

The detector-event measurements used in Q20-Q22 are change/information-heavy. Q23 constructs a slower,
connection-heavy identity from the recurrence of their complete sixteen-path handover web. The logical bit is
constructed separately as retention versus flip. Only after both lower identities exist on their own `0-2`
diameters are they coupled one rung up.

## Measurement grain

Each X/Z and 13/30-round dataset contains 50,000 shots. Preserve source record order and divide it into 200
non-overlapping blocks of 250 shots. Source order is record order, not a claimed wall-clock timestamp.

## Connection-heavy identity

Each shot already has the Q21 four-by-four child-handover web \(H_s\), normalized so:

\[
\sum_{i,j}H_{s,ij}=2.
\]

For each block, average the first 125 and final 125 webs to obtain \(H_A,H_B\). The primary raw connection
identity is the stability of the complete relation web:

\[
C_{\rm raw}
=
2\left(1-\frac{\lVert H_B-H_A\rVert_1}{4}\right).
\]

This is `2` when the whole handover web persists exactly and moves toward `0` as the relation web is replaced.
Declared decompressions, reported without primary claim status, are:

- same-child persistence: diagonal mass of the block-mean web;
- anti-child handover: anti-diagonal mass;
- web concentration: normalized sixteen-path Herfindahl concentration.

## Logical-bit identity

Within the same 250-shot block:

\[
B_{\rm raw}=2(1-p_{\rm flip}).
\]

Thus the connection-facing bit pole is logical retention. The opposite orientation \(2p_{\rm flip}\) is retained
as a declared control.

## Separate local ARA normalization

Connection and bit are distinct identities with different native magnitudes. Convert each marginal block ordering
separately to the open `0-2` diameter:

\[
x=2\frac{\operatorname{midrank}(x_{\rm raw})+0.5}{N}.
\]

This mapping is performed without using the pairing between connection and bit. It tests relational ordering,
not absolute amplitude equality. Ties receive their average rank.

## One-rung-up parent

\[
\boxed{
P_k=\frac{2B_k}{C_k+B_k}
}
\]

and

\[
D_k=|P_k-1|.
\]

The ARA claim is that genuine coupling makes the correctly paired blocks closer to the parent ridge than controls
that preserve the separate identities but break their relation.

## Frozen controls

1. **Half-cycle shift:** rotate bit blocks by 100 positions.
2. **Wrong bit:** pair X connection with Z bit and vice versa at the same round count.
3. **Broken spatial web:** rebuild the handover web after the frozen Q21 spatial coordinate misassignment.
4. **Flip orientation:** use \(2p_{\rm flip}\) instead of bit retention.
5. **Permutation null:** 999 deterministic bit-block permutations per basis/round, seed `20260726`.

## Frozen primary gates

The claim is supported only if all ten gates pass:

1. source and freeze integrity;
2. all local and parent coordinates remain inside `(0,2)`;
3. median parent lies within `[0.95,1.05]` in X/Z at both round counts;
4. paired mean ridge distance is lower than the half-cycle shift in all four datasets;
5. paired mean ridge distance is lower than the wrong-bit control in all four;
6. paired mean ridge distance is lower than the broken-spatial-web control in all four;
7. one-sided permutation `p <= 0.01` in all four;
8. null-mean minus paired mean ridge distance is at least `0.02` in all four;
9. the fraction within `0.10` of the ridge exceeds the permutation-null mean by at least `0.05` in all four;
10. connection/retention rank correlation is at least `0.15` in all four.

No secondary connection decomposition can rescue a failed primary test.

## Claim boundary

Passing would show block-level relational closure between one ARA connection-web instrument and logical
retention on this public patch. It would not identify an external physical field, prove causality, prove the
universal ARA framework, or establish absolute TE-ARA energy transfer. Failure would reject this exact
connection-web/bit construction, not the existence of a larger connection-heavy counterpart.
