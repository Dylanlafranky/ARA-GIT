# Frozen protocol — Q14 child phase swap

**Protocol ID:** `Q14-CHILD-PHASE-SWAP-v1`  
**Ledger ID:** `T273`  
**Frozen:** 24 July 2026, after Q13 outcomes were open but before calculating Q14 swap metrics, folds or nulls  
**Test class:** post-outcome parameter-free correspondence and held-out transform test  
**Source:** `Q13_RAMSEY_HAHN_FOUR_CHILDREN.csv`

## Frozen children and operators

For each Bell state and matched ordinal wait index, let:

\[
\mathbf R=
\begin{pmatrix}R_A\\R_B\end{pmatrix},
\qquad
\mathbf H=
\begin{pmatrix}H_A\\H_B\end{pmatrix}.
\]

Test the identity and compulsory child-swap operators:

\[
I=
\begin{pmatrix}1&0\\0&1\end{pmatrix},
\qquad
S=
\begin{pmatrix}0&1\\1&0\end{pmatrix}.
\]

The ARA claim predicts \(S\), not \(I\). Analyze amplitude and direction separately.

## Parameter-free comparison

For each axis calculate:

\[
E_I=\sum\|\mathbf H-I\mathbf R\|^2,
\qquad
E_S=\sum\|\mathbf H-S\mathbf R\|^2,
\]

and swap gain:

\[
G=1-\frac{E_S}{E_I}.
\]

Positive \(G\) means the crossed pairing is closer.

Define phase differences:

\[
D_R=R_A-R_B,\qquad D_H=H_A-H_B.
\]

The swap predicts \(D_HD_R<0\). Report:

- flipped-parity fraction among nonzero cells;
- flipped cosine
  \[
  C_{\rm flip}
  =
  -\frac{\sum D_RD_H}{\sqrt{\sum D_R^2\sum D_H^2}}.
  \]

The operator identity \(\mathbf1^{\mathsf T}S\mathbf R=\mathbf1^{\mathsf T}\mathbf R\) must hold to numerical
precision; this is a mathematical closure check, not empirical support.

## Matched-stage null

Use `9,999` deterministic permutations with seed `27014`. Within each Bell identity, permute the eleven Hahn
ordinal indices as intact \((H_A,H_B)\) pairs, preserving each Hahn child pair while breaking its ordinal
alignment with Ramsey. Calculate \(G\) for each permutation. Use add-one p-values:

\[
p=\frac{1+\#(G_{\rm null}\geq G_{\rm observed})}{10000}.
\]

Amplitude and direction use the same permutation in each iteration.

## Held-out transform

Leave one Bell identity out. On the other `33` cells, fit one nonnegative common scale \(\lambda\) and two target
offsets:

\[
\mathbf H
\approx
\boldsymbol\alpha+\lambda M\mathbf R,
\qquad M\in\{I,S\}.
\]

Apply the frozen coefficients to the held-out identity's `11` cells. Pool both target channels and calculate:

\[
G_{\rm CV}=1-\frac{\operatorname{SSE}_{S}}{\operatorname{SSE}_{I}}.
\]

Report the median across four folds and the number of folds won by \(S\).

## Frozen gates

All twelve gates must pass for `CALIBRATED`.

1. `F1`: exactly `44` finite cells and the expected four Bell identities.
2. `F2`: the swap preserves the two-component sum with maximum numerical error at most `1e-12`.
3. `F3`: parameter-free direction swap gain \(G_y>0\).
4. `F4`: direction matched-stage permutation \(p_y\leq0.05\).
5. `F5`: direction flipped-parity fraction is at least `0.75`.
6. `F6`: direction flipped cosine is at least `0.50`.
7. `F7`: median held-out direction gain is positive.
8. `F8`: the swap wins direction in at least `3/4` held-out Bell identities.
9. `F9`: parameter-free amplitude swap gain \(G_x>0\).
10. `F10`: amplitude matched-stage permutation \(p_x\leq0.05\).
11. `F11`: amplitude flipped-parity fraction is at least `0.75`.
12. `F12`: median held-out amplitude gain is positive.

## Interpretation boundaries

- Success supports crossed correspondence between the two derived child sets, not causal Ramsey-to-Hahn energy
  transfer.
- Failure may reject this operational mapping without rejecting every possible parent-to-child flip elsewhere.
- Local normalization tests shape and orientation, not absolute energy conservation.
- Ramsey covers `0.02–40.02 us`; Hahn covers `1–1000 us`. Equal indices are ordinal stages, not equal times.
- All four children derive from the same underlying density matrices.
- This is a post-Q13 frozen structural test, not a blind prediction, new quantum law or proof of universal
  fractality.

