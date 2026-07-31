# Q43 projected child ridge and Phi handover report

Date: 2026-07-28 (Australia/Brisbane)

Test ID: `Q43-CHILD-RIDGE-PHI-HANDOVER-v1`

Overall assessment: **share with caveats**. The calculation and independent
validation pass. Neither frozen support gate passes.

## Plain-language result

At the child's own rung, the child's ridge is `1.0`. When that complete child
is viewed from one full rung above, octave halving assigns it `0.5`. This is
not half of an incomplete child; it is the whole child expressed in the
parent's coordinate.

Q42's large residual was not generically `0.544` once the cadence families
were separated. In the predeclared two-turn family it was:

`Two-turn 7.5` and `one-turn 15` are empirical classifier names. Under the
canonical ARA interpretation they are nested grains: the approximately `7.5`
Phase-A/Phase-B children combine into the approximately `15` adult/parent
closure one multiplicative rung upward. See
`QUANTUM_7_5_15_PARENT_CHILD_CADENCE_CANON_2026-07-28.md`.

- greedy: `0.6443`, 95% seed-bootstrap interval `[0.6153, 0.6829]`;
- landmax: `0.6287`, interval `[0.6185, 0.6743]`.

The fitted symmetric sampling control moved the lineage-matched estimates
substantially toward the projected child ridge:

- greedy: `0.5532`, interval `[0.5282, 0.5914]`;
- landmax: `0.5611`, interval `[0.5319, 0.5947]`.

That is very close to the proposed `0.5`, but the complete intervals do not
fit inside the frozen `[0.45, 0.55]` equivalence band. The child-ridge gate
therefore **fails**, narrowly in location and clearly in uncertainty.

The remaining point offsets are `+0.0532` and `+0.0611`, not zero. Sampling
explains a substantial part of the apparent excess, but it does not remove
all of it.

## Why the rung wording matters

\[
\underbrace{1.0}_{\text{child ridge at its own rung}}
\xrightarrow{\text{view one rung upward}}
\underbrace{0.5}_{\text{same completed child in parent units}}.
\]

Moving downward into the child reverses the normalization:

\[
0.5_{\rm parent\ view}\longrightarrow1.0_{\rm child\ view}.
\]

Therefore `0.5` is not "only half the child" in the child's own geometry.
It is the complete child contribution after projection into the parent
rung.

## A useful control

The one-turn family did not produce the same residual:

- greedy raw estimate: `0.0025`;
- landmax raw estimate: `−0.0148`.

This means the near-child-scale residual is localized to the two-turn
geometry rather than being an automatic consequence of the normalization.
That is useful ARA structure, but it does not identify the residual as a
physical hidden child by itself.

The one-turn result is therefore a parent-view control for the resolved-child
geometry, not an unrelated cadence system.

## Phi handover result

The second frozen question was independent:

> Does the exact directional pair \((2-\phi,\phi)\) minimize the mismatch in
> the fractions of elapsed half-wave time at which forward and return
> strands cross corresponding landmarks?

It did not.

For the two-turn family:

| Archive | Exact-Phi temporal tension | Grid fraction no better than Phi | Frozen gate |
|---|---:|---:|---|
| greedy | 0.19987 | 39.3% | fail |
| landmax | 0.19680 | 36.1% | fail |

The frozen gate required at least 90% in both archives. Under this passage
timing definition, tension generally increased as the low landmark moved
from `0.20` toward `0.50`; exact Phi was not a special minimum.

The secondary local-speed measure also did not isolate Phi. Phi was smoother
than the quarter and third landmarks, but slightly worse than `0.40` and
substantially worse than the `0.50/1.50` pair in both archives.

This does **not** disprove every possible ARA Phi-handover formulation. It
falsifies this specific, frozen formulation: Phi is not privileged by simple
opposite-direction passage-time matching in these trajectories.

## Method and data

Sources:

- public simulator DOI `10.5281/zenodo.16753415`;
- Q40 greedy archive;
- Q41B landmax archive;
- 73,760 Q42 independently measured scalar half-wave pairs.

Child-ridge primary population:

- 27,167 greedy two-turn pairs;
- 30,248 landmax two-turn pairs;
- 100 seed clusters per archive.

Phi common-support population:

- 11,265 greedy two-turn pairs across 94 seeds;
- 12,931 landmax two-turn pairs across 100 seeds.

Both paths had to independently span `0.20` through `1.80`, so every
symmetric landmark candidate was evaluated on the same population.

The source archives had already been revealed. Q43 was frozen before its
calculations but remains descriptive rather than prospective.

## Validation

Independent validation status: **PASS**.

Verified:

- frozen protocol hash;
- source hashes;
- row/profile alignment;
- exact residual identity
  `residual = forward + return − 2`;
- sampling correction arithmetic;
- complete fixed candidate grid;
- common-support counts;
- independent exact-Phi temporal and speed recalculation;
- non-empty PNG and SVG artifacts.

Maximum recalculation error for the residual and exact-Phi scores was zero
at saved precision.

## Interpretation boundary

The strongest supported statement is:

> The two-turn family contains a reproducible, cadence-localized exposed
> residual. A fitted symmetric sampling control moves its parent-view
> coordinate close to, but not demonstrably onto, the projected child ridge
> `0.5`.

Do not promote this to:

- proof that the residual is one isolated child;
- proof that every child contributes exactly this observed amount in these
  sampled trajectories;
- a universal Phi handover result; or
- a prospective quantum prediction.

The unresolved `≈0.05–0.06` may contain imperfect control matching,
additional lower-rung participation, nonlinear mixing, or another
measurement effect. Those possibilities require a separately frozen test.

## Reproduction artifacts

- `Q43_CHILD_RIDGE_AND_PHI_HANDOVER_PROTOCOL_v1_FROZEN.md`
- `q43_child_ridge_and_phi_handover_test.py`
- `Q43_CHILD_RIDGE_AND_PHI_HANDOVER_RESULTS.json`
- `Q43_CHILD_RIDGE_SAMPLING_CONTROL.csv.gz`
- `Q43_PHI_HANDOVER_GRID.csv`
- `Q43_CHILD_RIDGE_AND_PHI_HANDOVER_DIAGNOSTICS.png`
- `Q43_CHILD_RIDGE_AND_PHI_HANDOVER_DIAGNOSTICS.svg`
- `q43_validate_child_ridge_and_phi_handover.py`
- `Q43_CHILD_RIDGE_AND_PHI_HANDOVER_VALIDATION.json`
