# Q47 — ARA⁹ whole-lattice meta-movement protocol v1

**Frozen:** 30 July 2026 before the whole-lattice meta-step values were
calculated  
**Ledger:** T304  
**Status:** retrospective test on the completely opened Q39 source  
**Originating clarification:** Dylan La Franchi

## Question

The complete ARA⁹ connected lattice, not one cell or a count of its cells, is
one identity at a time slice:

\[
C(t)\in\mathbb R^{3\times3}.
\]

Does the **meta movement of that whole identity** from one completed internal
cycle to the next favour the moving-carrier landmark
\(\phi^{-2}=0.381966\ldots\), rather than the nearby connected/local
landmark `3/8 = 0.375` or other fixed rivals?

This is not a test of `3/9`, Bell-state names \(\Phi^\pm\), lattice occupancy,
or individual matrix cells.

## Source and population

Reuse the public Q39 `pure_strongmax` simulator source and its independently
validated cycle boundaries:

- source DOI: `10.5281/zenodo.16753415`;
- branch: `c2_2local connectivity`;
- connected matrices:
  `public_data/q39_information3_strongmax/q39_connected_cache.npy`;
- frozen Q39 cycle rows:
  `Q39_ARA9_INFORMATION3_FOURTH_QUADRANT_CYCLES.csv.gz`;
- only Q39 evaluation cycles already present in that table;
- group by `(seed, pair_index)` and sort by `q1_start`;
- compare consecutive complete cycles inside the same lineage.

The source is already open and deterministic. Q47 can be descriptive and
reproducible, not blind confirmation or quantum-hardware evidence.

## Whole-lattice state

For cycle \(r\) and its ordered internal quadrant visit \(q\in\{1,2,3,4\}\),
average the complete connected matrix across the saved inclusive interval:

\[
M_{r,q}
=
\frac{1}{|I_{r,q}|}
\sum_{t\in I_{r,q}} C(t).
\]

Preserve the unnormalised Frobenius magnitude

\[
A_{r,q}=\lVert M_{r,q}\rVert_F
\]

as the connection/closure diagnostic. Define the scale-free whole-lattice
orientation

\[
U_{r,q}
=
\frac{M_{r,q}}{\lVert M_{r,q}\rVert_F}.
\]

Only numerical zero states with \(A_{r,q}\le10^{-12}\) are ineligible. No
empirical amplitude threshold may be fitted.

## Meta-movement coordinate

Compare the same internal phase in consecutive parent cycles:

\[
\delta_{r,q}
=
\frac{1}{2\pi}
\cos^{-1}
\left(
\operatorname{clip}
\langle U_{r,q},U_{r+1,q}\rangle_F,
-1,1
\right).
\]

Thus \(\delta\in[0,0.5]\) is the shortest signed-orientation-preserving
geodesic distance expressed in full turns:

- `0` = whole-lattice recurrence;
- `0.5` = complete sign opposition;
- `3/8` and \(\phi^{-2}\) remain distinct fixed candidates.

The primary event coordinate is the equal four-quadrant mean:

\[
\bar\delta_r
=
\frac14\sum_{q=1}^{4}\delta_{r,q}.
\]

No quadrant is selected or weighted after inspection.

## Fixed candidates

Score each candidate by median absolute event error
\(\operatorname{median}|\bar\delta-k|\):

| Candidate | Value |
|---|---:|
| recurrence | `0` |
| eighth | `1/8` |
| quarter | `1/4` |
| third | `1/3` |
| three eighths | `3/8` |
| exact Phi carrier | `phi^-2` |
| two fifths | `2/5` |
| silver irrational | `sqrt(2)-1` |
| opposition | `1/2` |

The same candidate table is scored independently for each of the four
quadrant anchors.

## Frozen gates

1. **P1 — pooled specificity:** exact Phi has the lowest pooled
   \(\bar\delta\) error of all fixed candidates.
2. **P2 — close-rival stability:** a seed-cluster bootstrap with `5,000`
   draws favours Phi over `3/8` in at least `95%` of draws.
3. **P3 — phase consistency:** Phi beats `3/8` separately at all four
   same-quadrant anchors.

Verdict:

- `3/3`: supported in this opened simulator;
- `2/3`: mixed/suggestive;
- `0–1/3`: not supported.

## Diagnostics and controls

These do not alter the frozen primary verdict:

- report medians and interquartile ranges of all four \(\delta_q\);
- report magnitude \(A\) and result by magnitude quartile;
- compare adjacent-cycle steps with same-lineage lag-2 steps;
- report seed and lineage counts;
- report whether diagonal-only source geometry limits the result;
- retain both full \(3\times3\) matrices even though this simulator's
  off-diagonal entries are exactly zero.

## Claim boundary

A pass would locate a Phi-like meta-step for the whole connected lattice in
this source. It would not prove universal Phi, universal ARA⁹, physical hidden
waves, quantum hardware behaviour, or that every moving parent uses the same
advance.

