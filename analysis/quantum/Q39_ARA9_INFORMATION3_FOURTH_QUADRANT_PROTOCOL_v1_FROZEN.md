# Frozen Protocol — Q39 ARA⁹ Information³ Fourth-Quadrant Reconstruction

**Test ID:** `Q39-ARA9-INFORMATION3-FOURTH-QUADRANT-v1`  
**Frozen:** 27 July 2026, before downloading or numerically inspecting the
target archive  
**Design:** prospective cross-archive reconstruction  
**Target:** previously untouched `unnati_submit_12_pure_strongmax.hdf5.zip`

## 1. Question

When one complete connected ARA⁹ relation traverses four ordered quadrants of
its own closure–flow plane, can the first three raw quadrant identities
reconstruct the fourth more accurately than simple local baselines?

Secondary question: does better ARA reconstruction track independently
calculated two-qubit purity or computational-basis coherence?

## 2. Public source and frozen target

- Akhouri, Shandera and Henry, *Dataset for 6–14 qubits evolving on network
  with varying connectivity*;
- Zenodo DOI `10.5281/zenodo.16753415`;
- target archive `unnati_submit_12_pure_strongmax.hdf5.zip`;
- deposited MD5 `11b5f14ba185a9901f6a85bd31497d71`;
- density matrices span `500` simulator slices and `100` seeds for each
  connectivity branch.

`pure_random`, `pure_greedy`, `pure_landmax` and `pure_mimic` were already
opened in Q27–Q38. `pure_strongmax` was selected and this protocol was frozen
before its values were downloaded or inspected.

## 3. Measured ARA⁹ identity

For each two-qubit density matrix \(\rho(t)\), calculate:

\[
a_i(t)=\operatorname{Tr}[\rho(t)(\sigma_i\otimes I)],
\qquad
b_j(t)=\operatorname{Tr}[\rho(t)(I\otimes\sigma_j)],
\]

\[
T_{ij}(t)=\operatorname{Tr}[\rho(t)(\sigma_i\otimes\sigma_j)],
\qquad
\boxed{C_{ij}(t)=T_{ij}(t)-a_i(t)b_j(t)}.
\]

The complete \(3\times3\) matrix \(C(t)\), not a Bell label and not a single
entry, is the tested ARA⁹ identity.

Its invariant closure cut is:

\[
h(t)=|\det C(t)|^{1/3}.
\]

## 4. Development-only normalisation

For each seed–pair lineage in the `c2` branch, use only slices `0..249`:

\[
h_{05}=Q_{0.05}(h),\qquad h_{95}=Q_{0.95}(h),
\]

\[
m=\frac{h_{05}+h_{95}}2,\qquad
r=\frac{h_{95}-h_{05}}2,
\]

\[
s=Q_{0.95}(|\Delta h|).
\]

Require \(r>10^{-12}\) and \(s>10^{-12}\). Define:

\[
u(t)=\frac{h(t)-m}{r},
\qquad
v(t)=\frac{h(t+1)-h(t)}s.
\]

No target-archive coefficient is fitted beyond this per-lineage
development-only coordinate normalisation.

## 5. Four meta quadrants

The four quadrants are the Cartesian product:

\[
\operatorname{sign}u(t)\times\operatorname{sign}v(t).
\]

Use the explicit labels:

| Label | \(u\) | \(v\) |
|---|---:|---:|
| `Q++` | \(\ge0\) | \(\ge0\) |
| `Q-+` | \(<0\) | \(\ge0\) |
| `Q--` | \(<0\) | \(<0\) |
| `Q+-` | \(\ge0\) | \(<0\) |

Determine the dominant circulation direction from development slices by the
signed mean of non-zero phase turns in \(u+iv\). Require absolute circulation
coherence at least `0.80`, at least `5%` development occupancy in every
quadrant and at least `95%` finite development coordinates.

## 6. Evaluation cycles

Use slices `250..498`, because \(v(t)\) requires \(t+1\).

1. Collapse consecutive equal quadrant labels into contiguous visits.
2. Discard visits shorter than `2` samples.
3. Following the development circulation direction, retain non-overlapping
   sequences of four consecutive visits that traverse all four distinct
   quadrants in the expected circular order with no skip or reversal.
4. For each retained visit, define its raw quadrant identity as the arithmetic
   mean of all raw \(C(t)\) matrices in that visit:

\[
C_k=\frac1{|V_k|}\sum_{t\in V_k}C(t),\qquad k=1,2,3,4.
\]

The visit boundaries may be used to locate the masked fourth quadrant, but no
entry of \(C_4\) may enter the predictor.

## 7. Frozen Information³ predictor

\[
\boxed{\widehat C_4^{\rm ARA}=C_1-C_2+C_3}.
\]

This is the fixed ordered affine closure of four quadrant identities:

\[
C_1+C_3=C_2+C_4.
\]

No coefficient, rotation, scale correction or post-result sign choice is
allowed.

## 8. Frozen baselines and controls

Calculate the same metrics for:

1. **Persistence:** \(\widehat C_4=C_3\).
2. **No flip / old identity:** \(\widehat C_4=C_1\).
3. **Linear continuation:** \(\widehat C_4=2C_3-C_2\).
4. **Three-state mean:** \(\widehat C_4=(C_1+C_2+C_3)/3\).
5. **Wrong ordered relation:** \(\widehat C_4=C_2-C_1+C_3\).

The wrong-order control tests the ARA claim that ordered relation, not merely
the same three matrices, matters.

## 9. Metrics

For every retained cycle and predictor:

\[
\operatorname{NRMSE}
=
\frac{\|\widehat C_4-C_4\|_F}
{\|C_4\|_F+10^{-12}},
\]

\[
\operatorname{cos}
=
\frac{\langle\widehat C_4,C_4\rangle_F}
{\|\widehat C_4\|_F\|C_4\|_F+10^{-12}},
\]

\[
\epsilon_h
=
\frac{\left||\det\widehat C_4|^{1/3}
-|\det C_4|^{1/3}\right|}
{|\det C_4|^{1/3}+10^{-12}}.
\]

Report event-level medians and means. For inference, average each metric
within seed–pair lineage, then use paired lineage differences.

Use a fixed `20,000`-draw seed-cluster bootstrap (`390027`) and a two-sided
paired sign permutation check for ARA versus every baseline. The script must
also report the fraction of cycles on which ARA has the lowest NRMSE.

## 10. Independent quantum cross-checks

For every target fourth-quadrant visit, independently calculate from the raw
density matrices:

\[
P=\operatorname{Tr}(\rho^2)
\]

and the computational-basis \(l_1\) coherence:

\[
C_{l_1}=\sum_{i\ne j}|\rho_{ij}|.
\]

Average each quantity over the target visit. Report Spearman correlations
between ARA reconstruction fidelity \(-\operatorname{NRMSE}\) and both
quantities, plus NRMSE in their upper and lower quartiles.

These are secondary crosswalks. \(C_{l_1}\) is basis-dependent and neither
quantity is defined to be ARA coherence.

## 11. Eligibility

The prospective result is `INCONCLUSIVE — ELIGIBILITY` unless the primary
`c2` target contains at least:

- `500` complete four-visit cycles;
- `80` represented seeds;
- `300` represented seed–pair lineages.

All available cycles must be retained after applying the frozen rules.

## 12. Primary gates

Conditional on eligibility, Q39 supports this specific Information³
reconstruction only if all are true:

1. ARA has lower lineage-mean NRMSE than every named baseline.
2. The paired seed-cluster bootstrap probability that ARA is no better than
   each baseline is below `0.05`.
3. ARA has higher lineage-mean cosine than every named baseline.
4. ARA is the lowest-NRMSE method on at least `55%` of individual cycles.
5. The wrong-order control is worse than the correct ordered ARA rule.

If eligibility passes but any primary gate fails, the verdict is
`NOT SUPPORTED` for the tested operator.

The purity and \(l_1\) coherence associations are reported but are not
required for the primary verdict.

## 13. Quality and validation

- verify archive MD5 and frozen-file SHA-256 values;
- check trace, Hermiticity and minimum density-matrix eigenvalue on sampled
  raw records;
- independently recompute at least `4,000` connected matrices and all metrics
  for a deterministic cycle sample;
- verify visit order, no overlap and target masking;
- export raw cycle results as compressed CSV plus a compact JSON summary;
- render a static figure and inspect it at full resolution.

## 14. Interpretation boundary

A pass would establish a prospective, non-fitted, masked fourth-quadrant
reconstruction advantage in this public deterministic simulator family.
It would support the utility of the proposed ordered ARA⁹ / Information³
crosswalk at this location.

It would not prove:

- that Bell states are the lower four quadrants;
- that two unique hidden physical children have been identified;
- a new quantum state, physical singularity or universal law;
- that target quadrant timing can be predicted without observing the scalar
  closure–flow cut;
- that every quantum dataset or every ARA⁹ identity follows the same affine
  closure.

