# Q35 — Whole Phase-A / External Phase-B Counterpart Protocol v1 (FROZEN)

**Date frozen:** 27 July 2026  
**Ledger:** T290  
**Design:** ARA-first, fixed-lineage, retrospective development/evaluation test  
**Target:** Q34 public `12_pure_greedy` derived cache, `c2` primary branch

## 1. Source and provenance

- Akhouri, Shandera and Henry, Zenodo `10.5281/zenodo.16753415`;
- deposited archive `unnati_submit_12_pure_greedy.hdf5.zip`;
- deposited MD5 `c1cf77ccff486e3786d73ba47f8674f1`;
- Q34 derived closure cache made directly from the deposited two-qubit density
  matrices;
- 12 qubits, 100 unitary seeds, 500 time slices and 66 fixed pair identities;
- `c2_2local connectivity` is the primary branch;
- `c4_2local connectivity` is used only as a network-identity displacement
  control.

No sieve, Ramsey/Hahn filter, Fourier component, quantum model fit, or
time-slice re-selection is introduced.

## 2. Measurement boundary

For each branch \(b\), seed \(s\), time \(t\) and fixed pair \(j\), retain

\[
h_{bsjt}=|\det C_{bsjt}|^{1/3}.
\]

This is a nonnegative relation-closure magnitude. It is **not** declared to be
the pure bounded ARA coordinate.

Define the raw movement cut

\[
g_{bsjt}=h_{bsj,t+1}-h_{bsjt}.
\]

The fixed lineage is the ordered sequence \((h_t,g_t)\) for one deposited
pair. No pair is re-selected after the lineage begins.

## 3. Frozen partitions

- development/calibration times: `t=0..249`;
- evaluation state times: `t=250..499`;
- evaluation movement times: `t=250..498`;
- candidate lags: integer `0..7`;
- deterministic bootstrap seed: `350927`;
- cluster unit: unitary seed.

The archive and broad `c2` circulation were seen before freezing Q35. The
evaluation half is used to prevent direct refitting of candidate identities,
not to claim untouched blindness.

## 4. Two-cut local loop chart

For each fixed lineage, calculate from development only:

\[
m=\frac{Q_{.05}(h)+Q_{.95}(h)}2,\qquad
r=\frac{Q_{.95}(h)-Q_{.05}(h)}2,
\]

\[
f=Q_{.95}(|g|).
\]

Require \(r>10^{-12}\) and \(f>10^{-12}\). Define the dimensionless loop
direction

\[
w_t=\frac{h_t-m}{r}+i\frac{g_t}{f},\qquad
p_t=\frac{w_t}{|w_t|}.
\]

This constructs a direction on the observed two-cut loop. It does not assert
that either raw axis is itself the structural `0–2` diameter.

## 5. Complete-loop eligibility

On development, a lineage is a complete local loop only when:

1. at least `95%` of its movement points have finite nonzero \(w_t\);
2. all four sign quadrants of
   \((\Re w_t,\Im w_t)\) contain at least `5%` of valid points;
3. its circulation coherence is at least `0.80`, where

\[
\kappa=
\left|
\operatorname{mean}
\operatorname{sign}
\arg(\overline p_t p_{t+1})
\right|.
\]

Only complete `c2` loops may be sources or exact counterpart candidates.

## 6. Development-only counterpart selection

For every eligible source lineage \(A=(s,j)\), search every different
eligible fixed pair \(k\ne j\) in the same seed and each lag
\(\ell\in\{0,\ldots,7\}\).

The development opposition score is

\[
O^{dev}_{A,k,\ell}
=
-\operatorname{mean}
\Re\!\left(\overline p_A(t)p_k(t+\ell)\right).
\]

`+1` is perfect half-turn opposition, `0` is unrelated on average and `-1`
is same-phase alignment. Choose the single \((k,\ell)\) with largest score.
Ties are resolved by smaller lag and then smaller pair index.

The chosen pair and lag are frozen for evaluation. There is no future
re-selection.

## 7. Evaluation observables

For the frozen exact relation calculate:

### 7.1 Parent opposition

\[
O^{eval}
=
-\operatorname{mean}
\Re(\overline p_A p_B).
\]

### 7.2 Parent ridge residual

\[
R^{eval}
=
\operatorname{mean}\frac{|p_A+p_B|}{2}.
\]

Lower \(R\) means stronger cancellation of the two complete loop directions.

### 7.3 Half-turn occupancy

\[
H^{eval}
=
\Pr\left(
\left|\operatorname{wrap}(\theta_B-\theta_A-\pi)\right|
\leq\frac{\pi}{4}
\right).
\]

### 7.4 Source seam and counterpart far pole

A source seam event is an evaluation time \(t\ge251\) satisfying

\[
h_A(t)\le Q_{.05}^{dev}(h_A),
\qquad
g_A(t-1)<0.
\]

At the corresponding frozen lag, map the counterpart closure to a
development empirical-rank display coordinate

\[
x_B(t)=2F_B^{dev}(h_B(t)).
\]

This rank coordinate is used only for the seam/far-pole display and
comparison. It is not a physical derivation of the structural ARA diameter.
Record the median \(x_B\), the fraction with \(x_B>1\), and the fraction that
are local high-pole turns

\[
g_B(t-1)>0,\qquad g_B(t)\le0.
\]

### 7.5 Counterpart completeness

Recalculate the counterpart's circulation coherence on evaluation using the
development calibration. Report the median and the fraction at or above
`0.80`.

## 8. Frozen relation-broken controls

Apply the identical evaluation calculations to:

1. **time displacement:** exact counterpart shifted forward `37` evaluation
   slices with circular wrapping;
2. **seed displacement:** same pair and lag in seed `(s+1) mod 100`;
3. **pair displacement:** next development-eligible pair in cyclic pair-index
   order after the exact counterpart, excluding the source;
4. **network displacement:** same seed, pair and lag in the `c4` branch.

These controls preserve the measured object as far as possible while
breaking the selected source/counterpart relation.

## 9. Frozen gates

### Eligibility gate

- at least `500` eligible source lineages;
- every scored source has one fixed exact counterpart;
- at least `5` evaluation seam events per scored source.

If this fails, the claim verdict is inconclusive.

### External-counterpart support gate

All must pass:

1. exact median \(O^{eval}>0\);
2. more than `55%` of source lineages have \(O^{eval}>0\);
3. exact median \(O^{eval}\) exceeds every control and seed-cluster bootstrap
   probability of positive exact-minus-control difference is at least `0.95`;
4. exact median \(R^{eval}\) is lower than every control and seed-cluster
   bootstrap probability of negative exact-minus-control difference is at
   least `0.95`;
5. exact seam median \(x_B>1\), exact far-pole fraction exceeds `55%`, and
   both exceed every relation-broken control;
6. exact counterpart median evaluation circulation coherence is at least
   `0.80`, with at least `50%` of counterparts at or above `0.80`.

The high-pole-turn fraction and half-turn occupancy are secondary geometry
diagnostics. They do not rescue a failed primary gate.

## 10. Verdict language

If all gates pass:

> A fixed external phase-opposed counterpart relation is supported inside the
> Q34 `c2` simulator identity.

If eligibility passes but any support gate fails:

> The proposed fixed external counterpart relation is not supported by this
> representation.

If eligibility fails:

> Inconclusive: the deposited representation does not supply enough complete
> loops or seam events for the frozen test.

Separately report a geometry verdict describing complete loops, seam
occupancy and any partial relation. No result may be promoted to a universal
Phase B, hidden quantum sector, or universal ARA proof.

