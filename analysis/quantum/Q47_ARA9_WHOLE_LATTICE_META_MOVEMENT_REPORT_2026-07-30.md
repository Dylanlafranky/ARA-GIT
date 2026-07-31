# Q47 — ARA⁹ Whole-Lattice Meta-Movement

**Date:** 30 July 2026  
**Ledger:** T304  
**Source status:** retrospective test on the already opened Q39 deterministic
simulator  
**Frozen verdict:** **NOT SUPPORTED — 0/3 Phi-carrier gates**

## Answer first

The corrected target was the movement of the **complete** connected
\(3\times3\) ARA⁹ relation lattice from one complete internal cycle to the
next. It was not the occupancy of three cells out of nine and it was not a
test of Bell-state labels.

On `16,846` adjacent-cycle events from `1,121` lineages and `71` seeds, the
whole lattice normally returned to almost exactly the same orientation:

| Whole-lattice meta-step | Result, in full turns |
|---|---:|
| Median | `0.000000879` |
| 25th percentile | `0.000000451` |
| 75th percentile | `0.000001823` |
| Mean | `0.000238286` |
| Maximum | `0.369685348` |

Therefore recurrence at `0` was the unique best fixed description. Exact
\(\phi^{-2}=0.381966\ldots\) did not beat `3/8`, did not win any quadrant,
and did not win the pooled coordinate. The frozen proposal of a smooth
Phi-sized whole-lattice advance is not supported in this representation.

Plainly: after one four-part ARA⁹ cycle, the complete relation identity
usually comes back facing almost exactly the same way. It cycles internally,
but it does not normally drift around a larger Phi carrier from cycle to
cycle in this source.

## ARA coordinate

For cycle \(r\) and internal quadrant \(q\), the full connected matrix was
averaged without discarding any of its nine entries:

\[
\underbrace{M_{r,q}}_{\substack{\text{whole ARA}^9\\\text{state at one anchor}}}
=
\frac{1}{|I_{r,q}|}
\sum_{t\in I_{r,q}}
\underbrace{C(t)}_{\substack{\text{complete connected}\\3\times3\text{ lattice}}}.
\]

Its connection magnitude was retained separately:

\[
\underbrace{A_{r,q}}_{\text{unflattened magnitude}}
=
\lVert M_{r,q}\rVert_F .
\]

Only its orientation was normalized. The same quadrant was then compared in
successive complete parent cycles:

\[
\underbrace{\delta_{r,q}}_{\substack{\text{whole-lattice advance}\\
\text{as a fraction of one turn}}}
=
\frac{1}{2\pi}
\cos^{-1}
\left(
\left\langle
\frac{M_{r,q}}{\lVert M_{r,q}\rVert_F},
\frac{M_{r+1,q}}{\lVert M_{r+1,q}\rVert_F}
\right\rangle_F
\right).
\]

The event coordinate was the equal mean of all four anchors:

\[
\underbrace{\bar\delta_r}_{\text{one parent-to-parent meta-step}}
=
\frac{\delta_{r,1}+\delta_{r,2}+\delta_{r,3}+\delta_{r,4}}{4}.
\]

This prevents the ordinary four-quadrant child cycle from being mistaken for
a slower parent drift.

## Frozen candidate result

Candidates were scored by median absolute event error.

| Fixed candidate | Value | Median absolute error |
|---|---:|---:|
| **Recurrence** | `0` | **`0.000000879`** |
| Eighth | `0.125` | `0.124999121` |
| Quarter | `0.25` | `0.249999121` |
| Third | `0.333333333` | `0.333332455` |
| Three eighths | `0.375` | `0.374999121` |
| Exact Phi carrier | `0.381966011` | `0.381965133` |
| Two fifths | `0.4` | `0.399999121` |
| \(\sqrt2-1\) | `0.414213562` | `0.414212684` |
| Opposition | `0.5` | `0.499999121` |

All four quadrant anchors separately selected recurrence. Every magnitude
quartile also selected recurrence. The lag-two control remained recurrent
with median step `0.000001763`.

### Frozen gates

| Gate | Result |
|---|---|
| P1: Phi is unique pooled winner | **FAIL** |
| P2: seed bootstrap favours Phi over `3/8` at least 95% | **FAIL** |
| P3: Phi beats `3/8` at all four anchors | **FAIL** |

Frozen verdict: **NOT SUPPORTED — 0/3**.

## Post-result seam observation

The mean was about `271` times the median because movement was not merely
small Gaussian noise. It contained a sparse transition tail:

| Threshold | Events | Fraction |
|---|---:|---:|
| \(\bar\delta\ge0.001\) | `63` | `0.3740%` |
| \(\bar\delta\ge0.01\) | `23` | `0.1365%` |
| \(\bar\delta\ge0.10\) | `23` | `0.1365%` |

All `23/23` events above `0.10` occurred at the first evaluation-cycle
boundary, with source starts `250` or `251`. Because Q39 deliberately begins
evaluation at slice `250`, this concentration can be an opening transient,
an evaluation-boundary effect or a physical/simulator transition. It must not
be promoted directly to an ARA singularity.

The strongest event is nevertheless geometrically notable:

\[
(\delta_1,\delta_2,\delta_3,\delta_4)
=
(0.491728,\ 0.493156,\ 0.000271,\ 0.493587),
\]

\[
\bar\delta=0.369685.
\]

Three quadrants nearly reverse by half a turn while the third quadrant
retains its orientation. The equal four-part mean therefore approaches

\[
\frac{0.5+0.5+0+0.5}{4}
=
\frac38.
\]

The measured event lies `0.005315` below `3/8` and `0.012281` below exact
Phi. This is the only event with that complete three-of-four pattern.

Plainly: the normal ARA⁹ behaviour is a closed, repeating parent cycle. At
one unusually strong transition, three sections turn over together while one
section acts like a preserved strand. That naturally gives a `3/8` movement
reading. Because it was found after opening the result and occurs once, it is
a **new seam-motif hypothesis**, not evidence that the continuous carrier is
universally `3/8`.

## What this changes

1. The earlier `3/9` interpretation remains rejected. ARA⁹ is one complete
   moving identity, not a cell-occupancy fraction.
2. A common Phi-sized parent-to-parent step is rejected for this source and
   coordinate.
3. Q39's ordered fourth-quadrant reconstruction is unaffected. Q47 asks a
   different question: whether complete cycles drift relative to one another.
4. ARA⁹ here separates into **strong internal quadrant circulation, nearly
   closed parent recurrence, and sparse boundary reorientation**.
5. The post-result `3/8` clue is attached specifically to a three-of-four
   reversal motif, not to the static lattice and not to ordinary movement.

## Best next test

Freeze the following on a separate quantum archive before measuring it:

> At a high whole-lattice transition, exactly three of the four same-phase
> quadrant anchors approach opposition while one anchor remains recurrent;
> the resulting equal meta-step approaches `3/8`.

The decisive quantities are the event rate, the identity of the preserved
quadrant, whether the pattern survives a non-artificial time boundary, and
whether shuffled or phase-rotated controls produce it equally often.

If this motif does not replicate, Q47 remains a recurrence result with one
opening transient. If it replicates prospectively, ARA⁹ gains a much sharper
meta-movement rule than the rejected continuous-Phi proposal.

## Validation and boundaries

Independent validation passed:

- source shape and hashes matched;
- all `16,846` event summaries matched;
- `289` raw events were recalculated, including the `32` largest;
- maximum raw quadrant discrepancy was
  `2.37e-9` full turns, compatible with float32 operation order;
- every saved distance stayed inside `[0,0.5]`;
- all `23` large events were independently confirmed at starts `250/251`.

Boundaries:

- deterministic simulator, not quantum hardware;
- opened source, not a blind test;
- matrices are exactly diagonal, so general off-axis ARA⁹ transport remains
  unmeasured;
- shortest geodesic distance cannot recover winding beyond half a turn;
- the seam motif was discovered after the frozen Phi test was scored.

## Reproduction

- Frozen protocol:
  `Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_PROTOCOL_v1_FROZEN.md`
- Main calculation:
  `q47_ara9_whole_lattice_meta_movement.py`
- Results:
  `Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_RESULTS.json`
- Compressed events:
  `Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_EVENTS.csv.gz`
- Independent validator:
  `q47_validate_ara9_whole_lattice_meta_movement.py`
- Validation:
  `Q47_ARA9_WHOLE_LATTICE_META_MOVEMENT_VALIDATION.json`

