# Q58 — same-gradient vertical Phi-pillar test

Date: 31 July 2026 (Australia/Brisbane)  
Status: **NOT SUPPORTED for a constant Phi pillar; directed, gradient-dependent parent/child separation supported**

## Technical summary

Q58 tested Dylan's corrected placement of the proposed same-phase Phi
handover. Instead of comparing already compressed parent and child ridge
durations, it held the local ARA coordinate fixed at

\[
x\in\{0.2,0.4,\ldots,1.8\}
\]

and compared the unnormalised connected-correlation magnitude of the Q42
`one-turn-15` parent family with the `two-turn-7.5` child family. Phase A was
compared only with Phase A, and Phase B only with Phase B:

\[
R_A(x)=\frac{\lVert C_{P,A}(x)\rVert_F}
                 {\lVert C_{C,A}(x)\rVert_F},
\qquad
R_B(x)=\frac{\lVert C_{P,B}(x)\rVert_F}
                 {\lVert C_{C,B}(x)\rVert_F}.
\]

The frozen claim was that these ratios would remain within
\(\phi\pm0.08\) across at least seven of the nine coordinates in each phase
and archive. It failed clearly: only one or two cells per phase/archive were
inside that band, and the mean cell-median errors from Phi were `0.1355` to
`0.2494`.

The data did reveal a strong narrower relation. The parent magnitude exceeded
the child magnitude at **all 36** archive–phase–coordinate cells. The size of
that separation changed with \(x\), so the empirical vertical relation is a
gradient-shaped profile rather than one constant cross-rung pillar.

## Result table

| Archive | Phase | Phi-band cells | Mean absolute Phi error | Whole-grid median | Nearest registered landmark | Parent > child |
|---|---:|---:|---:|---:|---|---:|
| greedy | A | 1/9 | 0.249441 | 1.863399 | \(\sqrt3\) (error 0.131349) | 9/9 |
| greedy | B | 2/9 | 0.244231 | 1.846715 | \(\sqrt3\) (error 0.114664) | 9/9 |
| landmax | A | 1/9 | 0.170397 | 1.783341 | \(\sqrt3\) (error 0.051290) | 9/9 |
| landmax | B | 1/9 | 0.135486 | 1.732067 | \(\sqrt3\) (error 0.000016) | 9/9 |

Cross-archive grid mean absolute differences were `0.084187` for Phase A and
`0.164071` for Phase B. The registered replication limit was `0.08`, so
neither phase passed that gate.

## What was measured

The source was the two public Q42 simulator archives (`greedy` and `landmax`)
from Zenodo DOI `10.5281/zenodo.16753415`. Q58 used:

- `2,180` eligible greedy lineages and `2,287` eligible landmax lineages;
- `35,423` and `38,337` qualifying cycles, respectively;
- `1,266,931` fixed-coordinate crossing rows;
- `59,116` pair profiles; and
- `3,465` seed-level ratios.

The local ARA coordinate was the frozen Q42 determinant coordinate,
\(x=2(h-h_{05})/(h_{95}-h_{05})\), where
\(h=|\det C|^{1/3}\). To avoid using that same determinant to define both
axes, the primary vertical magnitude was the Frobenius norm of the original,
unnormalised connected-correlation matrix. Its spectral norm was a registered
robustness check and reproduced the same broad profile.

The calculation was population-level and seed-balanced: cycle crossings were
aggregated to pair profiles, pair profiles to seed/family profiles, and the
parent/child ratio was then calculated within each seed. It does not assert
that one observed parent lineage is the literal genealogical parent of one
observed child lineage.

## Controls and validation

The data-quality gate passed. Every grid cell retained at least `93` seeds,
and the smallest child denominator was `0.00194094`, safely above the frozen
near-zero exclusion.

Wrong-phase controls did not reveal a uniquely same-phase Phi relation.
Registered `9,999`-draw family-label permutations also failed to show that the
observed labels were unusually Phi-like:

- greedy observed mean absolute Phi error `1.01551`, null median `0.78664`,
  one-sided no-worse-than-null probability `0.9999`;
- landmax observed `0.87767`, null median `0.76943`, probability `0.9844`.

Those permutation errors are means over long-tailed seed ratios, whereas the
headline curves use robust seed medians. Both were frozen before inspection.

An independent validator recalculated the protocol hash, fixed grid, data
gate, row counts, grid medians, all `10,000` bootstrap intervals, controls,
`256` sampled interpolations and all `9,999` permutation summaries. Every
check passed; the largest reproduced numerical discrepancy was approximately
`3.1e-15`.

## ARA and conventional readings side by side

| ARA reading | Measurement-language reading |
|---|---|
| Same-phase parent and child were compared at the same local gradient. | The two cadence families were evaluated at identical values of the Q42 determinant coordinate. |
| A single Phi-length pillar was not recovered. | The parent/child magnitude ratio was not constant at \(\phi\) across the fixed grid. |
| The parent consistently carried more exposed magnitude than the child. | Every cell had \(\lVert C_P\rVert_F/\lVert C_C\rVert_F>1\). |
| The vertical relation itself has an ARA-shaped variation. | Ratio magnitude depends on the local coordinate rather than behaving as a scale constant. |
| A local Phase-A boundary remains Phi-like. | At \(x=0.2\), Phase A was `1.64305` in greedy and `1.60213` in landmax, both inside the predeclared Phi band. |

The final row is a legitimate predeclared-grid observation, but it is not the
registered universal result: Phi occurs only locally and the other phase does
not replicate it at the same coordinate.

## Interpretation and claim boundary

Q58 rejects this exact operational statement:

\[
R_A(x)\approx R_B(x)\approx\phi
\quad\text{throughout the parent/child gradient.}
\]

It does **not** reject ARA's broader fractal parent/child architecture. It
shows that, in this archive and with unnormalised connected-matrix magnitude,
the cross-tier relation is not represented by one invariant Phi multiplier.
The supported empirical statement is:

\[
R_A(x)>1,\qquad R_B(x)>1,
\]

at all tested coordinates, with both ratios varying as functions of \(x\).

All four whole-grid medians happened to be nearest \(\sqrt3\), including an
almost exact landmax Phase-B value. This was not the frozen target, the curves
are not flat at \(\sqrt3\), and the archive disagreement is material.
Therefore \(\sqrt3\) is a post-hoc clue only—not a recovered constant or a
claim.

## Best next test

The cleanest follow-up is a separately frozen **boundary-localisation** test:

1. predeclare a narrow low-\(x\) interval without selecting its optimum;
2. test whether the replicated Phase-A approach to Phi persists in additional
   archives or systems;
3. compare Phi against nearby constants and a smooth unconstrained curve; and
4. require Phase-B behaviour to be predicted in advance rather than explained
   after inspection.

A separate test could model \(R_A(x)\) and \(R_B(x)\) as functions rather than
constants. That would test the newly observed gradient shape without turning
the failed pillar claim into a moving target.

## Reproduction

From `analysis/quantum`:

```powershell
python q58_same_gradient_vertical_phi_pillar.py
python q58_validate_same_gradient_vertical_phi_pillar.py
```

Primary artifacts:

- `Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_PROTOCOL_v1_FROZEN.md`
- `Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_PROTOCOL_v1_FROZEN.sha256`
- `Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_RESULTS.json`
- `Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_GRID_SUMMARY.csv`
- `Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_SEED_RATIOS.csv`
- `Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR.png`
- `Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR.svg`
- `Q58_SAME_GRADIENT_VERTICAL_PHI_PILLAR_VALIDATION.json`

The deterministic row-level crossing file (`26.2 MB` compressed) and
pair-profile file (`1.3 MB` compressed) are deliberately ignored by Git. The
runner recreates both before the independent validator checks them, preserving
the full audit trail without permanently bloating the repository.
