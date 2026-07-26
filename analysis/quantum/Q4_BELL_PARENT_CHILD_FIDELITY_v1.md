# Q4 Bell parent/child ARA translation fidelity

**Claim ID / version:** `Q4-BELL-PC-FID-v1`  
**Date:** 24 July 2026  
**Status:** `EXACT STANDARD-QUANTUM TARGET PATTERN; EMPIRICAL MAGNITUDES UNOPENED`

## ARA question

Can a real two-qubit identity be locally ridge-like on each child while remaining strongly structured in the
parent relation?

For the selected prepared Bell state, ARA predicts:

- the six single-qubit child cuts are near the `1.0` ridge;
- the same-axis pair cuts `XX`, `YY`, `ZZ` are far from the ridge;
- the ordered sign pattern identifies the coupled parent even though either child alone does not.

## Standard quantum target

For

\[
|\Phi^-\rangle
=
\frac{|00\rangle-|11\rangle}{\sqrt2},
\]

ideal quantum mechanics gives

\[
\langle XX\rangle=-1,\qquad
\langle YY\rangle=+1,\qquad
\langle ZZ\rangle=+1.
\]

Every single-qubit marginal is maximally mixed:

\[
\langle XI\rangle=\langle YI\rangle=\langle ZI\rangle
=
\langle IX\rangle=\langle IY\rangle=\langle IZ\rangle=0.
\]

The remaining six mixed pair projections `XY`, `YX`, `XZ`, `ZX`, `YZ`, `ZY` also vanish ideally.

Using the already-validated ARA/Bloch orientation

\[
\boxed{x_P=1-\langle P\rangle},
\]

the ideal ARA pattern is:

| Projection group | Ideal ARA coordinate |
|---|---|
| `XX` | `2` |
| `YY`, `ZZ` | `0` |
| all twelve other projections | `1` |

## Information³ relation

The three same-axis pair signs obey

\[
\operatorname{sgn}\langle XX\rangle
\times
\operatorname{sgn}\langle YY\rangle
\times
\operatorname{sgn}\langle ZZ\rangle
=-1
\]

when multiplied, because for two qubits

\[
(XX)(YY)=-ZZ.
\]

This gives a precise version of the proposed three-cut lock:

- two correlation signs select a Bell-state quadrant;
- the third supplies a consistency relation;
- the child marginals alone contain no Bell-state label.

That is an established stabilizer/Pauli identity expressed in ARA coordinates. Q4 may test its empirical
visibility, but may not claim to have discovered Bell correlations or quantum entanglement.

## Fidelity verdict

The ARA translation preserves the intended parent/child distinction:

- `1.0` at a child cut means zero local Pauli projection, not “nothing exists”;
- the parent is carried by cross-child correlations that disappear under local compression;
- the three-cut correlation pattern is mathematically specific and falsifiable before values are opened.

This is exact enough to test.
