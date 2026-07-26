# Q33 ARA fidelity packet — two-axis parent/child 3.5 projection

**Date:** 26 July 2026  
**Ledger:** T287  
**Status:** translation lock before Q33 outcome calculation  
**Source status:** retrospective analysis of the already-open Q27/Q28 public
simulator

## User geometry being tested

The intended `3.5` is not a triangle-closing edge. It is an ordered two-axis
path:

1. a complete same-rung ARA traversal contributes `2`;
2. the crossed-rung leg retains one full current-rung contribution, `1`;
3. one child viewed in the parent frame contributes `0.5`;
4. therefore the vertical leg is `1 + 0.5 = 1.5`, and the ordered path is
   `2 + 1.5 = 3.5`.

The child remains a complete local TE-ARA of `2` when opened inside its own
boundary. The `0.5` is only its capacity when projected into the parent frame.

## Correction to Q30 and Q32

Q30 called the Information³ triangle-closing edge `1.5`. That was one frozen
proxy and it failed; it was not the parent-plus-half-child construction above.

Q32 found ordered source release followed by adjacent-child accumulation, but
normalised every relation independently to its own `0–2`. That correctly
measured local child position while erasing whether the child has half the
source/parent energy capacity.

Q33 therefore retains both readings:

- **local ARA:** each relation receives its own development-frozen `0–2`;
- **parent projection:** source and child are compared in the common raw
  connected-relation energy unit before local renormalisation.

## Quantum measurement translation

For connected two-qubit relation matrix \(C_p(t)\), declare

\[
E_p(t)=\lVert C_p(t)\rVert_F^2.
\]

Its development-frozen capacity is

\[
E_{\max,p}=Q_{0.95}\{E_p(t):0\leq t<250\}.
\]

For source relation \(p\) and active endpoint child \(c\),

\[
\rho_{c\mid p}
=
\frac{E_{\max,c}}{E_{\max,p}}.
\]

This is the missing parent-facing projection. The ARA rung prediction is

\[
\rho_{c\mid p}\approx\frac12,\qquad
V=1+\rho_{c\mid p}\approx1.5,\qquad
L=2+V=3+\rho_{c\mid p}\approx3.5.
\]

This test does not assume that calling a relation a temporal `child` proves it
is one octave lower. The capacity ratio is the discriminator.

## Event and lineage object

- A source begins at local `x >= 1.5` and releases over the next slice.
- The active matching edge attached to each of the source's two endpoints is
  retained. These are two separately reportable child routes.
- Selection uses only topology and values available at the event slice.
- Each child is traced backward eight slices to its latest local minimum.
- The source is traced backward over the same window to its latest local
  maximum.

The backward trace tests whether Q32 observed the child after it had already
left its low pole. It does not change the frozen capacity ratio.

## Controls

1. **Topology:** two distinct active edges disjoint from the source, matched to
   the two exact children by closest starting local ARA coordinate.
2. **Seed:** endpoint children from seed `+37 mod 100`.
3. **Time:** endpoint children at the fixed within-split `+137` time shift.

Every control has two children and uses its own development-frozen capacities
and backward history. No future value selects a child or a control.

## Separate questions

1. Are the exact endpoint children at half the source energy capacity in the
   parent frame?
2. Are they closer to `0.5` than relation-broken controls?
3. Does backward tracing recover a child-pole origin more cleanly than Q32?
4. How much source energy loss appears as child energy gain?
5. Is the signed child movement oblique to the source-release direction?

Questions 4 and 5 are diagnostics. The simulator does not guarantee local
energy conservation, and no exact angle was declared before opening.

## Evidence boundary

Q33 can determine whether Q32's temporally named children also behave as
one-rung-lower children in the available common energy coordinate. Even a
positive result would remain retrospective evidence inside one diagonal
simulator. It would not prove the dark-sector formula, universal `3.5`,
physical energy conservation, a hidden Phase B, or that Manhattan routing is
the unique law of nature.
