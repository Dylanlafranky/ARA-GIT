# PN32 child-parent double Information³ lock - result

**Date:** 22 July 2026  
**Status:** **NULL**  
**Scope:** 500 untouched odd integers from 3001 through 3999; five independent waves; child rung `N`; parent rung `2N`

## Answer first

The proposed six-component closure did **not** survive its frozen test.

The most important result is that PN31's complete five-child ordering did not replicate in the immediately following
untouched interval:

\[
\operatorname{TV}_{child}=0.6057,
\qquad
p=0.2244.
\]

The doubled parent order was also null:

\[
\operatorname{TV}_{parent}=0.5362,
\qquad
p=0.8023.
\]

Most decisively, the complete rearrangement from child order at \(N\) to parent order at \(2N\) was **less**
different between primes and hard composites than random label assignments normally produce:

\[
\operatorname{TV}_{closure}=0.1895,
\qquad
\mathbb E_{null}[\operatorname{TV}]=0.2606,
\qquad
p=0.9684.
\]

Plainly: primes and unresolved composites used essentially the same child-to-parent rearrangement classes. Under
this exact representation, the proposed double Information³/hexagon closure is not a prime-specific structure.

## What was tested

For each chosen number \(N\), the same five independent waves were retained:

\[
\{3,5,9,11,13\}.
\]

For each wave, PN32 measured its forward distance to the next handover on its own `0-2` cycle. It then constructed
two complete relational triangles:

\[
\underbrace{(A_c,B_c,J_c)}_{\substack{\text{nearest child, farthest child,}\\\text{complete order at }N}}
\qquad\text{and}\qquad
\underbrace{(A_p,B_p,J_p)}_{\substack{\text{nearest parent, farthest parent,}\\\text{complete order at }2N}}.
\]

This is the science translation of the suggested **full double information lock**. `A` and `B` are the two declared
extrema and `J` retains everything between them. The six components form two Information³ locks; they were not
created by calling five items plus an arbitrary sixth item a hexagon.

The cross-rung closure coordinate was

\[
K_{c\to p}=J_p\circ J_c^{-1},
\]

the five-place permutation describing how every child wave's rank changes on doubling. This is the relation between
the two triangles, not an extra independent wave.

## Label firewall

1. The protocol was hashed before coordinates existed.
2. Child and parent coordinates were generated for 500 odd numbers without a primality routine.
3. The 1,000 relation-broken parent maps were also generated without labels.
4. Both artifacts were hashed and frozen.
5. Prime labels were then attached by direct trial division; no sieve was used.

The coordinate hash is
`C21EC1F1DB49E9C6BBE20CAFF075F1B5C67D7A1D6E60F0B0AA833B3CA5583B05`.

The population contained 120 primes, 380 odd composites, and 103 **unresolved composites** that also evaded direct
division by all five declared waves. The frozen primary comparison therefore contained 223 hard rows. None had a
child-order or parent-order tie.

## Frozen results

| Endpoint | Observed TV | Permutation-null mean | Frozen p | Verdict |
|---|---:|---:|---:|---|
| PN31 child-order replication | `0.605744` | `0.579124` | `0.224378` | Null |
| Doubled parent order | `0.536246` | `0.565482` | `0.802320` | Null |
| Child-to-parent closure relation | `0.189482` | `0.260568` | `0.968403` | Null |

All three predeclared inferential gates failed. The frozen decision is therefore `NULL`.

## Relation-broken control and its limitation

The control retained every child triangle and every parent triangle, but reassigned which local parent belonged to
which local child. Every one of the 1,000 broken controls had a larger raw TV than the intact closure (`p=1.0`).

That does **not** mean breaking the relation creates a real prime signal. Independent validation found that the
intact doubling map occupied only 27 closure categories, while a broken control occupied about 101 categories on
average. With only 223 hard rows, the extra category sparsity mechanically raises TV. Raw intact-versus-broken TV is
therefore not support-matched and must not be read as an effect-size comparison.

This limitation does not rescue the hypothesis. The valid, support-aware label permutation for the intact closure
already gave `p=0.9684`: there is no prime/composite separation to explain.

## What the test did uncover

The exact `N -> 2N` modular map is highly constrained: only 27 relative ordering classes appeared, compared with
about 101 after local parent reassignment. That is real arithmetic closure of the doubling map. It applies to both
primes and unresolved composites, so it is not evidence for a prime ridge or a prime-specific hexagon.

The literal six-component signature was also too sparse for inference: 219 distinct child-parent order pairs appeared
among 223 hard rows. Its descriptive TV was `0.9833`, exactly the kind of near-perfect but non-generalizing result
that sparse categories can manufacture. The protocol correctly excluded it from the verdict.

## Consequence for the ARA interpretation

PN32 rejects this specific chain:

> PN31 five-wave order difference → stable adjacent-interval structure → double Information³ lock under `N -> 2N`.

It does **not** reject Information³ in general, every possible parent definition, or the overall ARA framework. It
shows that `2N` plus nearest/farthest/full-order triangles is not the missing prime-specific closure operator, and
that PN31's isolated order result should now be treated as unreplicated rather than promoted.

The scientifically useful outcome is a narrower map: the doubling relation is a genuine constrained arithmetic
transformation, but it does not distinguish prime identity from difficult composite identity at this grain.

## Audit trail

- Frozen protocol: `PN32_DOUBLE_INFORMATION_LOCK_PROTOCOL_v1_FROZEN.md`
- Protocol freeze: `PN32_PROTOCOL_FREEZE_MANIFEST.json`
- Frozen coordinates: `PN32_DOUBLE_INFORMATION_LOCK_FROZEN_COORDINATES.csv`
- Frozen broken-relation maps: `PN32_RELATION_BROKEN_PARENT_INDEXES.json`
- Coordinate freeze: `PN32_COORDINATE_FREEZE_MANIFEST.json`
- Scored rows: `PN32_DOUBLE_INFORMATION_LOCK_SCORED.csv`
- Results: `PN32_DOUBLE_INFORMATION_LOCK_RESULTS.json`
- Independent validation: `PN32_DOUBLE_INFORMATION_LOCK_VALIDATION.json` (`14/14` passed)
- Reproducibility notebook: `PN32_DOUBLE_INFORMATION_LOCK_REPRODUCIBILITY.ipynb`

