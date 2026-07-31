# Q40B/Q40C post-result mirror and two-turn report

**Date:** 27 July 2026  
**Status:** descriptive post-result audit; the frozen Q40/T295 verdict remains
`NOT SUPPORTED — RETURN-FLOW RULE`

## Plain-language result

The first repair idea was that Q40 had simply read the B-dominant `Ba`
quadrant upside down—like confusing a stalagmite with a stalactite. That
simple whole-quadrant mirror was tested exactly and failed.

The visible Q40 ARA cut was then re-examined as a flattened view of a path
through time. Dylan identified what looked like two spirals crossing in the
upper-left diagnostic. Restoring sample order as a third axis confirmed a
real two-turn sampled structure in that lineage:

- one apparent rotation takes `7.500965` samples;
- the angle advances almost perfectly linearly (`R² = 0.999948`);
- neither integer approximation to one turn returns to the same path:
  - lag `7`: coordinate correlation `0.533705`;
  - lag `8`: coordinate correlation `0.537665`;
- after two turns, at lag `15`, the path returns with coordinate correlation
  `0.999999232`;
- the phase-return locking at lag `15` is `0.999999336`.

The defensible name is currently a **two-turn stroboscopic orbit** or
**two interleaved sampled phase tracks**. In ARA language, the flattened
diameter cut contains two alternating paths which complete one common
15-sample parent closure.

Calling it a physical double helix is still a hypothesis. Any periodic
two-dimensional phase-plane path becomes helix-like when time is restored as
height. The stronger finding is not merely the helix appearance; it is that
this path requires two turns to return to the same sampled geometry.

## Q40B: simple `Ba` mirror was ruled out

The registered post-result candidate swapped the first and second visible
states only when the fourth quadrant was `Ba`, then applied the unchanged Q40
flag and operator. It had no fitted parameters.

| Measure | Original Q40 | `Ba` full mirror |
|---|---:|---:|
| Global seed-balanced scaled error | `0.462621` | `0.513693` |
| `Ba` seed-balanced scaled error | `0.496688` | `0.815606` |
| Fraction of `Ba` cycles improved | — | `26.67%` |

The mirror worsened global error by `0.051072`, with seed-cluster 95% interval
`[-0.065283, -0.037268]`. Within `Ba`, it worsened error by `0.318918`, with
95% interval `[-0.392520, -0.245535]`.

Therefore the missing rule is not:

> If the state is B-dominant, turn the whole observed coordinate upside down.

That possible explanation is now ruled out on this archive.

## Q40C: population geometry

The same time-restored audit was run over all `968` eligible Q40 lineages.
Every lineage returned very close to the same ARA coordinate after exactly
`15` samples:

- median lag-15 coordinate correlation: `0.999999924`;
- minimum lag-15 coordinate correlation: `0.996266`;
- lineages with lag-15 correlation at least `0.95`: `968 / 968`.

Inside that shared 15-sample closure are two main rotation families:

| Rotation family | Lineages | Fraction |
|---|---:|---:|
| Two turns of approximately `7.5` samples | `361` | `37.29%` |
| One turn of approximately `15` samples | `597` | `61.67%` |
| Other/noisier angle fit | `10` | `1.03%` |

The two-turn family is distributed broadly. It occurs across `93` represented
seeds and `65` of the `66` pair identities. It is not produced by one special
seed or one qubit-pair distance.

**Canonical ARA clarification (28 July 2026).** `Two-turn 7.5` and
`one-turn 15` remain the empirical classifier names, but they are not to be
read as unrelated systems. In the ARA interpretation, the two approximately
`7.5` turns are the resolved Phase-A/Phase-B child expressions of the common
`15`-sample adult/parent closure. The child projection is faster because the
parent is one multiplicative/log rung upward. See
`QUANTUM_7_5_15_PARENT_CHILD_CADENCE_CANON_2026-07-28.md`.

This supports a scale distinction:

```text
two 7.5-sample child rotations
              ↓ coarse-grain
one shared 15-sample parent closure
```

That is an ARA-compatible reading of the observed geometry. Whether the
`7.5 : 15` relation is caused by the simulator cadence, a controlled harmonic,
or a more portable physical relation needs cross-archive testing.

## Prior prime and axiomatic precedents

The broad geometry was recorded before Q40.

### Prime child-to-parent closure

PN13 identified a modular construction in which two child periods near the
square-root boundary close one larger parent:

```text
child q near sqrt(N) × child r near sqrt(N)
                         ≈
                    parent N
```

PN15 then froze and transferred the normalized version to a fresh larger
scale. Its target results were:

- child A: `0.9999985181`;
- child B: `0.9999962435`;
- child sum: `1.9999947616`;
- median adult fill: `0.9999070021`;
- transferred phase-curve correlation: `0.9999467506`.

That was recorded as two half-scale child cycles closing one parent cycle.
The same test also found that the phase curve was not prime-specific: prime,
composite and raw-integer curves overlapped at that grain. It was therefore a
real arithmetic closure crosswalk, not a successful prime discriminator.

### Axiomatic double helix

`ARA_AXIOMATIC_PROOFS_AND_DOMAIN_SUBSETS.md` already contained:

- Theorem 2.9: phase and anti-phase form a double helix when a progression
  coordinate is restored;
- Theorem 2.10: phase → anti-phase → next phase becomes a temporal triangle,
  while a flat circular projection collapses it back to the ARA diameter.

Q40C is therefore not the first time the project invented this geometry. It
is a new empirical appearance of an already-recorded structural form.

The honest provenance distinction is:

- **pre-existing constraint:** two child cycles can close one parent, and
  omitting the progression axis can flatten a double helix into a circular
  crossing;
- **new post-result measurement:** Q40's highlighted lineage uses
  `7.500965`-sample turns, closes at lag `15`, and the two-turn family contains
  most Q40 false negatives;
- **not yet established:** the prime and quantum appearances share one
  physical generating mechanism.

## Why this matters for the failed Q40 rule

The two rotation families do not contribute equally to Q40's failures.

| Family | Cycles | Negative targets | Missed negatives | Recall |
|---|---:|---:|---:|---:|
| Two-turn `7.5` family | `5,658` | `1,797` | `576` | `67.95%` |
| One-turn `15` family | `9,533` | `69` | `54` | `21.74%` |
| Other | `147` | `16` | `16` | `0%` |

The low recall in the one-turn family is numerically real but affects very few
cycles because negative orientation is rare there (`0.72%`). In the two-turn
family negative orientation is common (`31.76%`).

Most importantly:

- Q40 had `646` false negatives in total;
- `576 / 646 = 89.16%` belong to the two-turn family;
- `543 / 646 = 84.06%` are specifically `Ba` false negatives inside that
  two-turn family.

The geometric split therefore localizes the failure much more tightly than
`Ba` alone:

> The unresolved rule is primarily a strand-selection or crossover problem
> inside the two-turn `Ba` geometry, not a global B-dominant mirror.

This is a post-result diagnosis, not a successful prediction.

## ARA and established-language crosswalk

| ARA description | Measurement description |
|---|---|
| Flattened diameter cut | `(u,v)` phase-plane projection |
| Restore movement through the sphere | Add sample order as the third axis |
| Two Phase paths cross in projection | Two interleaved sampled turns |
| Two child cycles close one parent | Two `~7.5` turns return at lag `15` |
| One parent cycle | One `~15` turn returns at lag `15` |
| Wrong return-flow branch | Q40 false negative/orientation miss |

The crosswalk does not declare the ARA ontology proven. It records that the
same measured structure can be stated faithfully in both languages.

## Scientific boundary

This audit establishes:

1. the simple upside-down `Ba` repair fails;
2. the highlighted path has an extremely precise two-turn return;
3. all eligible lineages share a strong 15-sample coordinate return;
4. the population separates mainly into one-turn and two-turn families; and
5. Q40's misses concentrate strongly in the two-turn family.

Here “families” means measured cadence classes within the same nested
child-parent architecture, not two independent proposed physical species.

It does **not** establish:

- two independent physical waves;
- a literal molecular-style double helix;
- universal ARA fractality;
- a physical singularity or hidden Phase B;
- quantum-hardware replication; or
- a repaired predictive rule.

The source is a deterministic public simulator archive, so its driving
schedule and construction must be treated as possible causes of the exact
periodicity.

## Source-paper check

The source paper explicitly describes these networks as phase-covariant
quantum-circuit dynamics built from one fixed two-qubit gate. It states that
the non-random rules show a regular oscillation period inherited from the
unitary-gate angle, and that the fixed angle together with locked interaction
neighbourhoods produces periodic late-time structure:

- [Open-systems tools for non-thermalizing closed quantum systems](https://arxiv.org/abs/2505.00116)
- [public source dataset](https://zenodo.org/records/16753415)

Therefore the broad recurrence is known and partly designed into the source
identity. Q40C did not discover an unknown universal quantum period. Its
distinct contribution is narrower:

1. the connected-correlation closure cut becomes a helix-like orbit when
   sample order is restored;
2. the population separates into one-turn and two-turn realizations of the
   common lag-15 return; and
3. Q40's predictive misses concentrate in the two-turn `Ba` strand.

The exact `7.5 : 15` cadence should be treated as gate-specific until an
angle intervention is performed. A strong later test should change the gate
angle prospectively: the numerical period should move with the gate while
any proposed ARA child-to-parent closure rule must retain its relational
form.

## Correct next test

The next frozen test should not apply a whole-quadrant mirror. Before another
target is opened:

1. classify each lineage as one-turn or two-turn using development data only;
2. define the exact strand/crossover state from the development path;
3. apply any new branch rule only where that state and `Ba` jointly occur;
4. freeze the operator and predictions;
5. score an untouched archive;
6. require global performance, two-turn-`Ba` recall, and comparison with the
   development affine model.

Until the strand-selection operator is defined without using the Q40 fourth
visits, it remains a hypothesis rather than a prediction.

## Reproduction files

- Q40B mirror audit:
  [`q40b_post_result_ba_mirror_audit.py`](q40b_post_result_ba_mirror_audit.py)
- Q40B results:
  [`Q40B_POST_RESULT_BA_MIRROR_RESULTS.json`](Q40B_POST_RESULT_BA_MIRROR_RESULTS.json)
- Q40C two-turn audit:
  [`q40c_post_result_double_helix_projection_audit.py`](q40c_post_result_double_helix_projection_audit.py)
- Q40C detailed results:
  [`Q40C_POST_RESULT_DOUBLE_HELIX_RESULTS.json`](Q40C_POST_RESULT_DOUBLE_HELIX_RESULTS.json)
- Q40C diagnostic PNG:
  [`Q40C_POST_RESULT_DOUBLE_HELIX_DIAGNOSTICS.png`](Q40C_POST_RESULT_DOUBLE_HELIX_DIAGNOSTICS.png)
- Q40C diagnostic SVG:
  [`Q40C_POST_RESULT_DOUBLE_HELIX_DIAGNOSTICS.svg`](Q40C_POST_RESULT_DOUBLE_HELIX_DIAGNOSTICS.svg)
