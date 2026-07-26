# Q14 child-phase-swap report

**Date:** 24 July 2026  
**Ledger:** T273  
**Status:** **PARTIAL / NOT CALIBRATED — 2/12 frozen gates passed**  
**Protocol:** `Q14_CHILD_PHASE_SWAP_PROTOCOL_v1_FROZEN.md`  
**Protocol SHA-256:** `ba12118684b6e42d627267aa2cc8c9fb6495f96e73318935bd640a551733d1c9`

> **Sphere-first/quadrant re-evaluation, corrected 24 July 2026:** Ramsey and Hahn remain two complete ARA parent
> paths with four coordinate children across the larger comparison. Q14 tested a literal A/B label swap between
> equal-depth child sets; it did not test the orthogonal Hadamard rotation between ideal Ramsey/Hahn control
> functions. The frozen rejection of an unmatched swap remains valid but contributes neither completed-rung nor
> quadrant evidence. See `Q13_Q14_RAMSEY_HAHN_QUADRANT_REAUDIT_2026-07-24.md`.

## Plain-language result

Dylan proposed a compulsory phase exchange at a parent-to-child crossing:

\[
\boxed{
A_{\rm parent}\rightarrow B_{\rm child},
\qquad
B_{\rm parent}\rightarrow A_{\rm child}.
}
\]

Q14 froze a first operational proxy using Q13's four trajectories. It compared:

\[
\underbrace{R_A\leftrightarrow H_A,\;R_B\leftrightarrow H_B}_{\text{same-label correspondence}}
\]

with:

\[
\underbrace{R_A\leftrightarrow H_B,\;R_B\leftrightarrow H_A}_{\text{crossed correspondence}}.
\]

The crossed correspondence failed strongly. Same-label pairing was much closer in amplitude and direction.

However, the audit exposed a crucial level distinction: Q14 compared **two child sets at the same proposed
depth**, not a measured parent pair to its immediate child pair. If both branches undergo the same compulsory
flip, that common parity cancels when the branches are compared. The failure of an *extra* swap between the
branches therefore does not test—and does not refute—the parent-to-child rule itself.

The direct generational rule remains untested because the current table contains:

\[
(R_A,R_B),\qquad(H_A,H_B),
\]

but does not contain the corresponding parent phase vectors:

\[
(P_{R,A},P_{R,B}),\qquad(P_{H,A},P_{H,B}).
\]

## Post-result fidelity correction: the flip is a completed-rung event

After Q14 was opened, Dylan corrected the operational statement. A child relation does **not** flip merely
because it is called a child. Phase orientation is retained within the same rung, including nearby decompressions
inside that rung. The swap occurs only when one complete TE-ARA at that scale closes and the relation crosses
into the next rung.

Let \(N_{\partial T}\) be the number of completed TE-ARA rung boundaries between two measurements. Then the
minimal parity rule is:

\[
\boxed{
\mathbf u_{\rm destination}
=
S^{N_{\partial T}}\mathbf u_{\rm source}.
}
\]

Therefore:

\[
\boxed{
N_{\partial T}\ \text{even}\Rightarrow I,
\qquad
N_{\partial T}\ \text{odd}\Rightarrow S.
}
\]

In particular:

\[
N_{\partial T}=0
\quad\Rightarrow\quad
\text{same-rung phase labels are retained}.
\]

“Complete TE-ARA” here means completion and promotion of the full scale-level identity, not that TE-ARA itself
temporarily ceases to equal its normalized total of `2`.

This clarification was made **after** Q14's frozen result and cannot alter its gates. It changes the test's
theoretical relevance: Q14 tested an odd-parity swap between records now proposed to occupy the same or a nearby
rung. Its strong same-label result is consistent with \(N_{\partial T}=0\) or another even boundary count. It
does not independently establish the rung count, because same-label alignment has other explanations.
The timestamped correction is preserved separately in
`Q14_POST_RESULT_FIDELITY_CORRECTION_2026-07-24.md`.
Earlier Formula, prime, pendulum, recycling and axiomatic occurrences are traced in
`Q14_COMPLETED_RUNG_FLIP_PRIOR_LINEAGE_2026-07-24.md`.

## Frozen operator test

Q14 defined:

\[
\mathbf R=
\begin{pmatrix}R_A\\R_B\end{pmatrix},
\qquad
\mathbf H=
\begin{pmatrix}H_A\\H_B\end{pmatrix},
\]

and compared:

\[
I=
\begin{pmatrix}1&0\\0&1\end{pmatrix}
\quad\text{against}\quad
S=
\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

For each axis:

\[
E_I=\sum\|\mathbf H-I\mathbf R\|^2,
\qquad
E_S=\sum\|\mathbf H-S\mathbf R\|^2,
\]

\[
\underbrace{G}_{\text{swap gain}}
=
1-\frac{E_S}{E_I}.
\]

Positive \(G\) would favour the crossed pairing. Negative \(G\) favours the same-label pairing.

## Parameter-free results

| Axis | Same-label SSE | Crossed SSE | Swap gain | Crossed/same error |
|---|---:|---:|---:|---:|
| Amplitude | 47.043038 | 159.129490 | **−2.382636** | 3.382636× |
| Direction | 28.092914 | 44.923606 | **−0.599108** | 1.599108× |

The same-label model is therefore clearly closer. Swapping made amplitude error about `3.38×` as large and
direction error about `1.60×` as large.

## Parity result

Define each child set's ordering:

\[
D_R=R_A-R_B,\qquad D_H=H_A-H_B.
\]

An unmatched swap predicts opposite order:

\[
D_RD_H<0.
\]

Observed:

| Axis | Opposite-order fraction | Frozen requirement | Flipped cosine |
|---|---:|---:|---:|
| Amplitude | 0.340909 | ≥0.75 | −0.550957 |
| Direction | 0.227273 | ≥0.75 | −0.264721 |

The negative “flipped cosine” means the differences predominantly align in the same orientation rather than the
opposite orientation.

The error difference has the exact identity:

\[
\boxed{
E_I-E_S=-2\sum D_RD_H.
}
\]

Thus the error comparison and parity comparison are two views of the same tested geometry, not independent
pieces of evidence.

## Matched-stage null

Q14 preserved each Hahn \((H_A,H_B)\) pair while permuting its eleven ordinal positions within each Bell
identity. It repeated the complete comparison `9,999` times.

| Axis | Observed swap gain | Null 95th percentile | Add-one p |
|---|---:|---:|---:|
| Amplitude | −2.382636 | +0.512703 | 1.0000 |
| Direction | −0.599108 | −0.341604 | 0.3098 |

Neither axis supports the crossed correspondence. The amplitude result is more same-label-aligned than every
permuted comparison under this one-sided swap-support test.

## Held-out Bell-identity test

For both identity and swap operators, Q14 fitted one nonnegative common scale and two offsets on three Bell
identities:

\[
\mathbf H\approx\boldsymbol\alpha+\lambda M\mathbf R,
\qquad\lambda\geq0,\quad M\in\{I,S\}.
\]

It then applied those frozen coefficients to the fourth identity.

| Axis | Median held-out swap gain | Swap wins |
|---|---:|---:|
| Amplitude | −1.177394 | 0/4 |
| Direction | 0.000000 | 1/4 |

For amplitude, the same-label model learned positive scales from `0.7586` to `0.7882`; every crossed model's
raw scale was negative and was therefore clipped to the frozen nonnegative boundary. For direction, both models
were weak: only the held-out \(\Phi^+\) identity gave a small crossed improvement (`+0.0122`).

## Why this is not the direct completed-rung-flip test

Under the original Q14 operationalization, let the two unobserved parent pairs be \(\mathbf P_R\) and
\(\mathbf P_H\):

\[
\mathbf C_R=S\mathbf P_R,
\qquad
\mathbf C_H=S\mathbf P_H.
\]

If the parents have same-label correspondence:

\[
\mathbf P_H\approx\mathbf P_R,
\]

then their children also have same-label correspondence:

\[
\mathbf C_H
\approx
S\mathbf P_R
=
\mathbf C_R.
\]

Equivalently, comparing equal-depth branches removes the shared parity operation:

\[
\boxed{S^{\mathsf T}S=I.}
\]

Q14 tested whether one equal-depth branch required an **additional unmatched swap**:

\[
\mathbf C_H\stackrel{?}{\approx}S\mathbf C_R.
\]

The data reject that extra swap. Under the completed-rung correction, this is the expected result when no full
TE-ARA boundary separates the two child sets. They are consistent with both child sets having the same parity, but this
cannot distinguish:

1. zero completed rung crossings;
2. an equal even number of crossings on both paths;
3. the A/B labels describing persistent identity types rather than rung-transition paths.

The missing parent vectors are required to distinguish those explanations.

## Frozen gates

Only the data-completeness and algebraic-sum checks passed:

| Gate family | Result |
|---|---|
| Data shape and finite values | PASS |
| Swap preserves the two-component sum | PASS — exact |
| Direction swap gain/null/parity/cosine | FAIL |
| Direction held-out gain and fold wins | FAIL |
| Amplitude swap gain/null/parity | FAIL |
| Amplitude held-out gain | FAIL |

Overall: `2/12`.

The exact sum preservation:

\[
\mathbf1^{\mathsf T}S\mathbf v=\mathbf1^{\mathsf T}\mathbf v
\]

is a mathematical property of the swap matrix, not empirical support for ARA or TE-ARA.

## Scientific conclusion

**Supported by Q14:**

- The Q13 Ramsey and Hahn child sets have substantially stronger same-label than crossed-label correspondence.
- An additional unmatched A/B swap between those two child sets is not supported.
- The result reproduces across held-out Bell identities for amplitude.

**Not tested by Q14:**

- Whether crossing one complete TE-ARA rung swaps Phase A and Phase B.
- Whether physical energy moves along those paths.
- Whether the four Q13 coordinates are the correct phase components for such an energy account.

**Next required dataset:**

For two states predeclared to be separated by exactly one completed TE-ARA rung boundary, observe both:

\[
\mathbf P=
\begin{pmatrix}P_A\\P_B\end{pmatrix}
\quad\text{and}\quad
\mathbf C=
\begin{pmatrix}C_A\\C_B\end{pmatrix}
\]

in common units or a declared normalization. Then freeze:

\[
\mathbf C\approx S\mathbf P
\quad\text{versus}\quad
\mathbf C\approx I\mathbf P.
\]

That would be the direct test of the clarified odd-boundary rule. A same-rung pair should instead be frozen to
predict \(I\), as Q14's observed correspondence does.

## Data-quality and validation boundaries

- All `44` expected matched cells and four Bell identities were present and finite.
- Ramsey spans `0.02–40.02 us`; Hahn spans `1–1000 us`. Equal indices are ordinal, not simultaneous.
- The children are local transforms of the same reconstructed density matrices, not four independent sensors.
- The test was frozen after Q13 but before Q14 metrics were calculated.
- An independent source-to-result implementation reproduced all parameter-free metrics, held-out summaries and
  `9,999`-permutation values exactly.
- This is a structural diagnostic, not a forward prediction, causal experiment, new quantum law or proof of
  universal fractality.

## Reproduction files

- `q14_child_phase_swap_test.py`
- `q14_child_phase_swap_validate.py`
- `Q14_CHILD_PHASE_SWAP_METRICS.csv`
- `Q14_CHILD_PHASE_SWAP_FOLDS.csv`
- `Q14_CHILD_PHASE_SWAP_GATES.csv`
- `Q14_CHILD_PHASE_SWAP_NULL.json`
- `Q14_CHILD_PHASE_SWAP_RESULTS.json`
- `Q14_CHILD_PHASE_SWAP_VALIDATION.json`
- `Q14_CHILD_PHASE_SWAP_GEOMETRY.svg`
- `Q14_CHILD_PHASE_SWAP_GEOMETRY.png`
- `Q14_POST_RESULT_FIDELITY_CORRECTION_2026-07-24.md`
- `Q14_COMPLETED_RUNG_FLIP_PRIOR_LINEAGE_2026-07-24.md`
