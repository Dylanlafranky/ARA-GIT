# Q46 — double-parent internal ARA protocol

Date frozen: 28 July 2026 (Australia/Brisbane)

Status: **pre-analysis frozen descriptive protocol**.

Q46 reuses the already-open Q44 archive and the Q45 eligibility list. It is
therefore a decomposition and validation test, not an independent replication.

## Question

Q45 decomposed one measured two-body relation into

\[
T=C+L,\qquad L=ab^{\mathsf T},
\]

where \(C\) is the connected child relation and \(L\) is the local-product
relation. Q46 now decompresses \(L\) into the two complete local parents:

\[
\underbrace{\mathrm{TE\!-\!ARA}_{P_1}}_{2}
+
\underbrace{\mathrm{TE\!-\!ARA}_{P_2}}_{2}
\longrightarrow
\underbrace{\mathrm{TE\!-\!ARA}_{P_1P_2}}_
{\text{new identity; normalized to 2 at its own tier}}.
\]

The measured Bloch vectors \(a(t)\) and \(b(t)\) are the established-physics
representatives of \(P_1\) and \(P_2\) for this cut. This does not claim that
either vector is the complete physical sphere.

## Source and population

- Public archive and hash: unchanged from Q45.
- Q45 eligible lineages only: `79` lineages across `17` seeds.
- Evaluation samples: `250..499`.
- Non-overlapping 15-sample windows: starts `250, 265, ..., 475`.
- No new eligibility filter may use the Q46 parent trajectories.

## Frozen ARA coordinates

For each 15-sample window, the native parent paths are

\[
P_1=\sum_{j=0}^{14}\|a(t+j+1)-a(t+j)\|_2,
\qquad
P_2=\sum_{j=0}^{14}\|b(t+j+1)-b(t+j)\|_2.
\]

Their symmetric 0–2 ARA coordinates are

\[
x_1=2\frac{P_1}{P_1+P_2},
\qquad
x_2=2-x_1.
\]

Because the labels of the two qubits are conventional, the orientation-free
asymmetry is

\[
d_{12}=|x_1-1|=|x_2-1|.
\]

The predeclared equal-parent ridge is \(x_1=x_2=1\). A broad same-tier ridge
gate passes when the seed-balanced median parent share lies in `[0.4, 0.6]`
and its seed-bootstrap 95% interval contains `0.5`.

## Exact lifted decomposition of the coupled strand

To compare both parents in the common 3×3 relation space, define

\[
\Delta a=a_{t+1}-a_t,\qquad
\Delta b=b_{t+1}-b_t,
\]

\[
D_1=(\Delta a)b_t^{\mathsf T},
\qquad
D_2=a_t(\Delta b)^{\mathsf T},
\qquad
D_\times=(\Delta a)(\Delta b)^{\mathsf T}.
\]

The product rule requires

\[
\Delta L=D_1+D_2+D_\times.
\]

This equality is bookkeeping and not evidence by itself. Its numerical
reconstruction error must nevertheless remain below `1e-6`.

The unsigned path shares inside the local-product strand are

\[
s_1=\frac{\sum\|D_1\|_F}
{\sum(\|D_1\|_F+\|D_2\|_F+\|D_\times\|_F)},
\]

\[
s_2=\frac{\sum\|D_2\|_F}
{\sum(\|D_1\|_F+\|D_2\|_F+\|D_\times\|_F)},
\qquad
s_\times=1-s_1-s_2.
\]

Here \(s_\times\) is the explicit within-handover `Other`. It is not silently
assigned to either parent.

## The approximately 42% prediction

Q45 already observed

\[
s_L=0.5891668.
\]

Therefore its complementary connected-child path share is arithmetically
fixed:

\[
s_C=1-s_L=0.4108332.
\]

Before Q46 calculation, Dylan predicted that the part not supplied by the
cross-parent/local strand would be approximately `42%`. Q46 will recompute
this from the saved lineage paths and display it, but this is a
**retrodictive accounting match**, not a fresh inferential gate, because both
numbers share the Q45 denominator.

The genuinely new Q46 quantities are the \(P_1:P_2\) ARA, the lifted
\(s_1:s_2:s_\times\) decomposition, and their stability across seeds,
families and parent phase.

## Controls and reporting

1. Report the raw ordered \(x_1,x_2\) coordinate and the orientation-free
   asymmetry.
2. Swap \(P_1\leftrightarrow P_2\); the orientation-free summaries must be
   invariant.
3. Report seed-balanced bootstrap intervals rather than treating 79 lineages
   as independent.
4. Report the two-turn `7.5` and one-turn `15` families separately.
5. Divide each eligible lineage into four frozen parent-phase quadrants using
   the Q45 development slope and intercept; report whether the parent share
   remains near the same ridge or rotates materially.
6. Do not describe Bloch-vector norm, tensor norm or path share as literal
   energy.

## Interpretation boundary

A same-tier \(P_1:P_2\) ridge would support the internal double-parent ARA
reading for this measured cut. It would not prove that the complete quantum
system has been recovered, that TE-ARA is a physical conserved quantity, or
that the approximately 42% connected share is universal.

