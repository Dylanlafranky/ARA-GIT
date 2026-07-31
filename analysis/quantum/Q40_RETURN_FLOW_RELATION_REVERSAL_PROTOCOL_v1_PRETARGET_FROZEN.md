# Frozen Pretarget Protocol — Q40 Conditional Return-Flow Relation Reversal

**Test ID:** `Q40-RETURN-FLOW-RELATION-REVERSAL-v1`  
**Frozen:** 27 July 2026 at approximately 17:00 AEST  
**Freeze stage:** before target-file enumeration or numerical inspection  
**Design:** prospective, masked fourth-visit replication  
**Target:** selected only after this file and the fidelity file are hashed

## 1. Primary question

On an untouched time-resolved two-qubit archive, does the target-blind
condition

\[
\cos(C_1-C_2+C_3,C_3)<0
\]

identify an ordered return-flow branch on which reversing only the relation
contribution,

\[
\widehat C_4=C_3-(C_1-C_2),
\]

reconstructs the masked fourth quadrant better than ordinary forward
continuation and the frozen controls?

## 2. Source class and deterministic target selection

The preferred source class is a deposited, public, time-resolved density
matrix archive from the same Akhouri–Shandera–Henry simulator family used in
Q27–Q39. This is a same-family replication before any independent-family
generalisation.

After the SHA-256 hashes of this protocol and the fidelity file are recorded:

1. enumerate deposited filenames and checksums using metadata only;
2. exclude every archive whose numerical values, derived matrices or
   outcome metrics appear in an earlier ARA test, script output, cache,
   report or ledger entry;
3. require at least `100` deposited seed trials, at least `500` time slices
   per trial and raw density matrices sufficient to reconstruct \(C(t)\);
4. restrict to complete two-qubit trajectories with the same measurement
   schema as Q39;
5. sort the remaining eligible deposited filenames lexicographically and
   choose the first;
6. use connectivity branch `c2` as the primary branch, matching Q39; all
   other branches are secondary and cannot rescue it;
7. write and hash a separate target-lock file containing the DOI, filename,
   deposited checksum, primary branch and repository-use audit;
8. only then download or open target values.

If no archive passes these metadata-only rules, Q40 stops as
`BLOCKED — NO UNTOUCHED COMPATIBLE TARGET`. No substitute may be chosen
after numerical inspection.

## 3. Measured lower-tier identity

For each two-qubit density matrix \(\rho(t)\):

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

The full raw connected \(3\times3\) matrix \(C(t)\) is the tested identity.
Its scalar closure cut is

\[
h(t)=|\det C(t)|^{1/3}.
\]

No Bell label, supplied Ramsey/Hahn filter, concurrence or other processed
quantum label enters the ARA coordinate or predictor.

## 4. Development/evaluation split

For a `500`-slice trajectory:

- development: slices `0..249`;
- evaluation coordinate: slices `250..498`, because \(v(t)\) requires
  \(t+1\);
- the raw evaluation \(C_4\) matrices remain masked until predictions and
  flags are saved.

If a metadata-compatible target has more than `500` slices, use the first
`500`. If it has fewer, it is ineligible before values are opened.

## 5. Development-only ARA coordinates

For each seed–pair lineage, using only development slices:

\[
h_{05}=Q_{0.05}(h),\qquad h_{95}=Q_{0.95}(h),
\]

\[
m=\frac{h_{05}+h_{95}}2,\qquad
r=\frac{h_{95}-h_{05}}2,\qquad
s=Q_{0.95}(|\Delta h|).
\]

Require \(r>10^{-12}\) and \(s>10^{-12}\). Define

\[
u(t)=\frac{h(t)-m}{r},
\qquad
v(t)=\frac{h(t+1)-h(t)}s.
\]

Quadrants:

| Numerical label | Sign pair | ARA label |
|---|---:|---|
| `Q++` | \(u\ge0,\ v\ge0\) | \(Ab\) |
| `Q-+` | \(u<0,\ v\ge0\) | \(Ba\) |
| `Q--` | \(u<0,\ v<0\) | \(bA\) |
| `Q+-` | \(u\ge0,\ v<0\) | \(aB\) |

Determine circulation from development data exactly as in Q39: the sign of
the mean non-zero angular turn in \(u+iv\). Require:

- circulation coherence at least `0.80`;
- development occupancy at least `5%` in every quadrant;
- at least `95%` finite development coordinates.

## 6. Complete four-visit cycles

For both development and evaluation windows:

1. collapse consecutive equal labels into contiguous visits;
2. discard visits shorter than `2` samples;
3. retain non-overlapping sequences of four consecutive visits containing
   all four quadrants in the development-learned circular order with no
   skip or reversal;
4. define each visit identity as the arithmetic mean of raw \(C(t)\):

\[
C_k=\frac{1}{|V_k|}\sum_{t\in V_k}C(t),
\qquad k=1,2,3,4.
\]

Development cycles may fit the comparator in Section 9. Evaluation \(C_4\)
values may not enter any ARA flag, prediction or fitted coefficient.

## 7. Frozen Q40 rule

For each evaluation cycle:

\[
D=C_1-C_2,\qquad P=C_3+D.
\]

\[
F=
\mathbf 1
\left[
\frac{\langle P,C_3\rangle_F}
{\|P\|_F\|C_3\|_F+10^{-12}}<0
\right].
\]

\[
\boxed{
\widehat C_4^{\mathrm{Q40}}=
\begin{cases}
C_3-D, & F=1,\\
C_3+D, & F=0.
\end{cases}}
\]

The flag and prediction file, including seed, pair, visit bounds, quadrant
order, \(F\) and every predicted matrix, must be written and SHA-256 hashed
before the evaluation \(C_4\) arrays are exposed to the scoring function.

## 8. Frozen non-fitted controls

Score:

1. **Forward relation / unchanged Q39:** \(C_3+D\).
2. **Persistence:** \(C_3\).
3. **Old identity:** \(C_1\).
4. **Linear continuation:** \(2C_3-C_2\).
5. **Three-state mean:** \((C_1+C_2+C_3)/3\).
6. **Wrong ordered relation:** \(C_3+(C_2-C_1)\).
7. **Conditional whole-sign guard:** use \(-P\) when \(F=1\), otherwise \(P\).
8. **Conditional persistence guard:** use \(C_3\) when \(F=1\), otherwise
   \(P\).
9. **Inverted-flag relation reversal:** use \(C_3-D\) when \(F=0\), otherwise
   \(P\).

Controls 7–9 distinguish relation reversal from a whole-identity flip, a
generic refusal to extrapolate and an indiscriminate sign choice.

## 9. Development-fitted affine comparator

Using development cycles only, fit the same three scalar coefficients across
all nine matrix entries and all eligible development cycles:

\[
\widehat C_4^{\mathrm{affine}}
=
\alpha C_1+\beta C_2+\gamma C_3.
\]

Fit ordinary least squares with no intercept. If the \(3\times3\) normal
matrix has condition number above \(10^{10}\), use its Moore–Penrose
pseudoinverse with `rcond=1e-12`. Freeze \(\alpha,\beta,\gamma\) in the
prediction file before exposing evaluation \(C_4\).

This comparator is allowed to learn the target archive's development
dynamics. Q40 is not.

## 10. Metrics

For every method and evaluation cycle, report:

### Primary scale-stabilised matrix error

Using the lineage's development-only median relation magnitude

\[
g=\operatorname{median}_{t=0}^{249}\|C(t)\|_F,
\]

\[
\boxed{
E_g=
\frac{\|\widehat C_4-C_4\|_F}{g+10^{-12}}}.
\]

This avoids dividing by a possibly near-zero target matrix.

### Continuity metrics

\[
E_{\mathrm{abs}}=\|\widehat C_4-C_4\|_F,
\]

\[
\operatorname{NRMSE}
=
\frac{\|\widehat C_4-C_4\|_F}{\|C_4\|_F+10^{-12}},
\]

\[
\operatorname{cos}
=
\frac{\langle\widehat C_4,C_4\rangle_F}
{\|\widehat C_4\|_F\|C_4\|_F+10^{-12}}.
\]

Also report determinant-magnitude closure error, target norm and every
metric split by visible flag, target orientation and fourth quadrant.

Aggregate first within seed–pair lineage, then balance lineages within seed.
Use a fixed `20,000`-draw seed-cluster bootstrap with seed `400027`.
For the primary comparisons use one-sided paired bootstrap probabilities
for Q40 advantage and Holm-correct them across the named comparator family.
Also report two-sided paired seed-level sign-permutation checks.

## 11. Orientation outcome

Only after the prediction file is frozen, define the target orientation:

\[
Y=
\mathbf 1
\left[
\cos(P,C_4)<0
\right].
\]

The visible flag \(F\) predicts \(Y\). Report its full confusion matrix,
precision, recall, specificity, balanced accuracy and seed-cluster
confidence intervals. This target is for scoring only; it cannot alter the
prediction.

## 12. Eligibility

The primary branch is `INCONCLUSIVE — ELIGIBILITY` unless it contains:

- at least `1,000` complete evaluation cycles;
- at least `300` represented seed–pair lineages;
- at least `60` represented seeds;
- at least `100` visibly flagged cycles across at least `20` seeds;
- at least `100` target-negative-orientation cycles across at least `20`
  seeds.

These thresholds are fixed from the Q39 development result before Q40 target
selection. All cycles passing the frozen lineage rules must be retained.

## 13. Primary gates

Conditional on eligibility, the exact Q40 operator is fully supported only
if all are true:

1. Q40 has lower seed-balanced lineage-mean \(E_g\) than every comparator in
   Sections 8 and 9.
2. Every Holm-corrected one-sided seed-cluster probability for that advantage
   is below `0.05`.
3. On visibly flagged cycles, Q40 improves \(E_g\) over forward relation on
   more than `70%` of cycles and the seed-cluster `95%` interval for mean
   improvement excludes zero.
4. Flag precision and recall for negative target orientation are each at
   least `0.75`, and specificity is at least `0.90`.
5. Q40 has higher seed-balanced lineage-mean cosine than forward relation
   and leaves fewer than `5%` of predictions with negative target cosine.
6. Q40 beats both the conditional whole-sign guard and the inverted-flag
   relation control on seed-balanced lineage-mean \(E_g\).

The six-way or ten-way single-best fraction is diagnostic only. It is not an
outright-majority gate.

If eligibility passes and Gates 1–6 pass, verdict:
`SUPPORTED ON UNTOUCHED SAME-FAMILY ARCHIVE`.

If Gates 3–6 pass but the development-fitted affine comparator alone beats
Q40, verdict:
`MECHANISM REPLICATED; NOT BEST PREDICTOR`.

If eligibility passes and the flag fails Gates 3 or 4, verdict:
`NOT SUPPORTED — RETURN-FLOW RULE`.

All other eligible failures are:
`NOT SUPPORTED — COMPLETE Q40 OPERATOR`.

## 14. Quality checks

- verify deposited and downloaded checksums;
- record SHA-256 for fidelity, protocol, target lock, source, prediction and
  result files;
- audit repository history and reports for prior numerical target use;
- check raw density-matrix trace, Hermiticity and minimum eigenvalue on at
  least `4,000` deterministic records;
- independently recompute at least `4,000` connected matrices;
- verify development/evaluation separation;
- verify circulation, visit order, non-overlap and fourth-visit masking;
- verify no scoring array is loaded before the prediction hash is recorded;
- independently reproduce at least `400` cycle predictions and all confusion
  counts without importing the main test module;
- export compressed cycle results and a compact machine-readable summary;
- render and inspect flag, error, quadrant and orientation diagnostics.

## 15. Interpretation boundaries

A pass supports a prospective conditional ordered relation-flow rule within
an untouched archive from this simulator family. It does not prove that the
flag is a literal physical singularity, that \(Ab,aB,bA,Ba\) are new quantum
states, that Bell work has been replaced, or that the same operator recurs
across every tier.

The cross-tier fractality test and a time-resolved entanglement
sudden-death/revival test must be frozen separately after Q40. They cannot
rescue Q40.
