# Q5 four-Bell-state ARA translation fidelity

**Claim ID / version:** `Q5-BELL-4-FID-v1`  
**Date:** 24 July 2026  
**Status at freeze:** `EXACT STANDARD-QUANTUM TARGET; THREE ARCHIVES UNOPENED`

## ARA question

Can four parent identities share essentially the same ridge-like local children yet remain distinguishable through
the ordered relation among three parent cuts?

For every prepared Bell state, Q5 predicts:

1. the six single-qubit child projections remain near ARA `1.0`;
2. `XX`, `YY` and `ZZ` remain far from the ridge;
3. their ordered pole orientations distinguish all four parents;
4. flattening to the local children removes that parent label.

## Frozen parent patterns

Using

\[
x_P=1-\langle P\rangle,
\]

the ideal patterns are:

| Parent | \((XX,YY,ZZ)\) expectations | ARA sides \((x_{XX},x_{YY},x_{ZZ})\) |
|---|---|---|
| \(\Phi^+\) | \((+1,-1,+1)\) | \((0,2,0)\) |
| \(\Phi^-\) | \((-1,+1,+1)\) | \((2,0,0)\) |
| \(\Psi^+\) | \((+1,+1,-1)\) | \((0,0,2)\) |
| \(\Psi^-\) | \((-1,-1,-1)\) | \((2,2,2)\) |

All four have zero ideal single-qubit marginals and therefore local-child ARA coordinates of `1.0`.

## Three-cut lock

The same-axis signs satisfy

\[
\times-\times+=-
\quad\text{or its pole-reversed equivalents,}
\]

so every valid Bell parent has

\[
\operatorname{sgn}(XX)\operatorname{sgn}(YY)\operatorname{sgn}(ZZ)=-1.
\]

Two signs select a quadrant and the third supplies the Pauli consistency relation. This is established
stabilizer geometry, expressed here as a frozen ARA three-cut parent identity.

## Fidelity verdict

The translation is exact enough to test:

- local `1.0` means no local projection on that axis, not absence of a joint identity;
- parent identity is carried by ordered cross-child relations;
- ARA and Pauli coordinates contain the same information through an affine transformation;
- the empirical question is whether the already frozen relation remains visible in all three untouched archives.

Q5 cannot claim to discover Bell states, entanglement or the Pauli algebra.

