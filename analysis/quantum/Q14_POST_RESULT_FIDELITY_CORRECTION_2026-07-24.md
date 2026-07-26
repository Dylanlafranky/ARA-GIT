# Q14 post-result fidelity correction

**Recorded:** 24 July 2026, after Q14 results were opened  
**Frozen Q14 gates changed:** no  
**Frozen Q14 results changed:** no

## Original operationalization

Q14 treated the presence of child labels as sufficient to predict an A/B swap between the Ramsey and Hahn child
sets.

## Dylan's correction

Phase orientation is retained within the same or a nearby rung. A discrete phase swap occurs only after one full
TE-ARA at that scale completes and the relation crosses into the next rung.

\[
\boxed{
\mathbf u_{\rm destination}
=
S^{N_{\partial T}}\mathbf u_{\rm source},
\qquad
S=
\begin{pmatrix}0&1\\1&0\end{pmatrix}.
}
\]

- \(N_{\partial T}=0\): no completed boundary; retain labels.
- odd \(N_{\partial T}\): swap labels.
- even \(N_{\partial T}\): restore the original parity.

TE-ARA remains normalized to `2`; “complete” refers to closure and promotion of that scale-level identity.

## Consequence for Q14

Q14's frozen odd-swap prediction was not faithful to the clarified same-rung claim. Its `2/12` result honestly
rejects an additional unmatched swap between the two Q13 child sets. It does not reject the completed-rung flip
rule.

The same-label result is consistent with zero or even completed-rung separation. It does not independently prove
that Ramsey and Hahn occupy the same rung, because same-label correspondence can have other causes.

## Correct direct test

Predeclare two phase vectors to be separated by exactly one completed TE-ARA boundary, then compare:

\[
\mathbf C\approx S\mathbf P
\quad\text{against}\quad
\mathbf C\approx I\mathbf P.
\]

The present Q13/Q14 table does not contain such a parent/boundary/child observation.

This rule predates Q14. Its Formula/engine, prime, pendulum, recycling and axiomatic lineage is indexed in
`Q14_COMPLETED_RUNG_FLIP_PRIOR_LINEAGE_2026-07-24.md`.
