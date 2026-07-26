# Q19 fidelity note — Tier-3 double-diagonal ablation

**Recorded:** 26 July 2026  
**Status:** written before Q19 calculation

## Dylan's proposed geometry

To destabilise the Tier-1 parent `J`, do not remove `J` itself. Remove two lower Tier-3 parts that help construct
it:

- the Phase A-side diagonal beneath Tier-2 Parent 1;
- the corresponding Phase A-side diagonal beneath Tier-2 Parent 2.

Both removals must occur together. Removing only the Tier-1 parent sections the geometry into relatively pure
Tier-2 parents; it does not remove their lower supports.

## Operational translation

The current Tier-3 children are:

| Child | Parent 1 state | Parent 2 state |
|---|---|---|
| `C00` | Phase A | Phase A |
| `C01` | Phase A | Phase B |
| `C10` | Phase B | Phase A |
| `C11` | Phase B | Phase B |

The primary Phase-A/Phase-A diagonals are frozen from development centroids:

\[
D_{A_1}^{[3]}=\mu_{00}^{dev}-\mu_{01}^{dev},
\qquad
D_{A_2}^{[3]}=\mu_{00}^{dev}-\mu_{10}^{dev}.
\]

They are two different directions even though both meet at `C00`. Their joint two-dimensional span is removed
from every raw record.

## ARA prediction

After both Phase A-side diagonals are removed:

- `C00`, `C01` and `C10`, which contain at least one removed Phase A-side path, should approach one residual
  location;
- `C11`, the Phase B/Phase B child, should remain the principal distinguishable survivor;
- the Tier-1 `J` closure should lose magnitude;
- the four-child parent geometry should contract toward one residual dimension.

The mirror and crossed pairs are secondary branches:

- `BB` should isolate `C00`;
- `AB` should isolate `C10`;
- `BA` should isolate `C01`.

These branches test whether the same tetrahedral/four-corner rule is reversible. Phase A is the registered
primary orientation; a successful mirror is not allowed to repair a failed primary branch.

## Construction–evidence fence

Removing the development span of two development centroid differences guarantees that the corresponding three
development centroids collapse. Development destabilisation is therefore not evidence.

Evidence must come from:

- the untouched holdout triple also contracting;
- the predicted opposite child remaining distinguishable;
- Tier-1 `J` losing holdout magnitude;
- the holdout geometry becoming predominantly rank one;
- the effect exceeding frozen negative controls.

The operation is a mathematical ablation in measurement space, not a physical intervention on a quantum
device. Causal wording is prohibited.

