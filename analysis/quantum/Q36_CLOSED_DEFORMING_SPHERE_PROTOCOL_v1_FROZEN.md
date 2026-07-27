# Q36 — Closed but Deforming Sphere Protocol v1 (FROZEN)

**Date frozen:** 27 July 2026  
**Ledger:** T291  
**Design:** retrospective ARA-first tensor-shape test  
**Source:** Q34 public `12_pure_greedy` raw-derived connected-tensor cache

## 1. Frozen source

- Zenodo `10.5281/zenodo.16753415`;
- archive `unnati_submit_12_pure_greedy.hdf5.zip`;
- archive MD5 `c1cf77ccff486e3786d73ba47f8674f1`;
- connected cache SHA-256
  `8b02fa7d186e9e6debb60b501297cf39f2d55de11511fe116775d0eb6b4abde7`;
- closure cache SHA-256
  `ab32ad22e207b9913eb69352f52ba9422e18ffb9bf8304d46412d80374428e3c`;
- primary branch `c2`;
- network-identity control `c4`;
- 100 seeds, 500 times and 66 fixed pair lineages.

## 2. Fixed identity and complete-loop eligibility

Reuse Q35's development-only complete-loop rule without alteration:

- development times `0..249`;
- relation closure \(h=|\det C|^{1/3}\);
- movement \(g_t=h_{t+1}-h_t\);
- development-calibrated two-cut loop direction;
- at least `95%` valid points;
- at least `5%` occupancy in every sign quadrant;
- circulation coherence at least `0.80`.

Only eligible fixed `c2` pair lineages enter Q36. There is no time-slice
re-selection.

## 3. Tensor coordinates

For each tensor \(C_t\), calculate singular values
\(\sigma_1\ge\sigma_2\ge\sigma_3\ge0\) and:

\[
A_t=\|C_t\|_F,
\qquad
h_t=|\det C_t|^{1/3},
\]

\[
L_t=\frac{3h_t^2}{A_t^2},
\qquad
D_t=1-L_t,
\]

\[
Q_t=\frac{C_tC_t^\top}{A_t^2},
\qquad
W_t=\|Q_{t+1}-Q_{t-1}\|_F,
\]

\[
p_{i,t}=\frac{\sigma_{i,t}^2}{A_t^2},
\qquad
r_{{\rm eff},t}=\frac1{\sum_i p_{i,t}^2}.
\]

Use `NaN` where a denominator is at most `1e-12`.

## 4. Evaluation trough events

Evaluation candidate times are `t=258..491`, leaving seven samples on both
sides. A time is a determinant trough when:

1. \(h_{t-1}>h_t\le h_{t+1}\);
2. \(h_t\le Q_{.20}^{dev}(h)\);
3. it is at least seven slices after the previous retained event in the same
   lineage.

This is a relative low-lattice trough, not a declaration that raw \(h\) is
the structural ARA coordinate or that every trough is a fundamental
singularity.

## 5. Local baseline and primary observables

For each event, the local baseline is the median of offsets `-7..-1` and
`+1..+7`.

Define:

\[
r_A=\frac{A_t}{\operatorname{median}(A_{\rm local})},
\qquad
r_h=\frac{h_t}{\operatorname{median}(h_{\rm local})},
\]

\[
G=r_A-r_h.
\]

`G>0` means balanced determinant closure fell more than total relation
amplitude.

Also record:

- event \(L,D,r_{\rm eff}\);
- normalized wobble
  \(R_W=W_t/\operatorname{median}(W_{\rm local})\);
- weakest-axis retention
  \(r_3=\sigma_{3,t}/\operatorname{median}(\sigma_{3,\rm local})\);
- seven-slice reclosure
  \(R_+=\max_{1\le k\le7}h_{t+k}/\operatorname{median}(h_{\rm local})\);
- whether \(R_+\ge0.75\).

## 6. Relation-broken controls

Calculate the same local metrics at:

1. **time control:** the same source shifted forward `37` within the valid
   evaluation range with circular wrapping;
2. **pair control:** the next Q35-development-eligible pair in cyclic pair
   order, same seed and time;
3. **network control:** the same seed, pair and time in `c4`.

Controls are not required to be determinant troughs. Their purpose is to
measure whether the retained-magnitude and wobble signature is specifically
located at the source's lattice trough.

## 7. Frozen eligibility gate

Require:

- at least `2,000` retained trough events;
- at least `80` unitary seeds represented;
- at least `500` eligible fixed source lineages represented.

Failure gives an inconclusive claim verdict.

## 8. Frozen closed-but-deforming support gate

All must pass:

1. median exact \(r_A\ge0.75\);
2. at least `80%` of exact events have \(r_A\ge0.50\);
3. median exact selective gap \(G>0.25\), with seed-cluster bootstrap
   probability \(P(G>0)\ge0.99\);
4. median exact deforming share \(D\) exceeds all three controls, with
   seed-cluster bootstrap probability at least `0.95` for each
   exact-minus-control comparison;
5. median exact wobble ratio \(R_W>1\) and exceeds all three controls, with
   seed-cluster bootstrap probability at least `0.95` for each comparison;
6. median exact reclosure \(R_+\ge0.75\), with at least `60%` of events
   reaching `0.75`.

Effective rank and weakest-axis retention are secondary shape diagnostics.
They cannot rescue a failed primary gate.

## 9. Competing verdicts

If eligibility and all support gates pass:

> The determinant trough carries a closed-but-deforming tensor signature
> inside this simulator representation.

If median \(r_A<0.50\) and median \(G\le0\):

> The trough is more consistent with measured relation loss than selective
> deformation.

Otherwise:

> Mixed/inconclusive: determinant balance changes, but the complete frozen
> closed-deforming signature does not close.

No verdict is a proof of literal topological sphere closure.

## 10. Validation and reporting

- Save event-level rows and aggregate summaries.
- Report exact and all controls.
- Use a seed-cluster bootstrap with deterministic seed `361027` and
  `20,000` draws.
- Produce an ARA/physics side-by-side figure showing the median event path,
  lattice/deforming shares, selective gap and wobble/reclosure controls.
- Independently rebuild deterministic event and metric samples without
  importing the primary implementation.
- Report a claim verdict and a separate geometry verdict.

