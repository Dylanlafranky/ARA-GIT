# Frozen protocol — Phi-ordered recurrence and resonance death

**Frozen:** 30 July 2026, before numerical inspection of the downloaded
free-swing double-pendulum runs 2–4.

**Status:** ARA-first prospective test using new public endpoints from the
dynamicslab *MultiArm-Pendulum* archive.

## 1. Clarified claim

Dylan's claim is not “maximum inequality is best.” It is:

> Four coupled children remain unequally allocated inside the complete TE-ARA
> budget. Their ordered handover stays non-closing, preventing terminal
> resonance death while the parent continues to traverse.

For child shares \(\mathbf p=(p_{AA},p_{AB},p_{BB},p_{BA})\),

\[
\mathbf t=2\mathbf p,
\qquad
\sum_i t_i=2.
\]

The `2` is normalized closure, not evidence. The empirical questions are
whether child *ordering* is specifically Phi-like and whether it predicts
continued parent traversal after allocation is held approximately fixed.

“Resonance death” here means terminal ARA closure: successive child relations
return to the same phase configuration, the remaining transfer gradient
vanishes at the measured grain, and the parent stops sustaining its previous
excursion. This is narrower than the standard physics word *resonance*, which
can also describe sustained or amplified motion.

## 2. Data freeze and source integrity

Primary source: dynamicslab *MultiArm-Pendulum* public repository,
`Datas/DoublePendulum`, associated with Zenodo DOI
`10.5281/zenodo.6633719`.

- historical development reference:
  `DoubleDataFreeSwing_1_Dt_0_001.mat` (local rename `pend_double.mat`);
- frozen replication:
  `DoubleDataFreeSwing_2_Dt_0_001.mat`;
- frozen replication:
  `DoubleDataFreeSwing_3_Dt_0_001.mat`;
- untouched final confirmation:
  `DoubleDataFreeSwing_4_Dt_0_001.mat`.

SHA-256:

- run 1:
  `2AF828048DEBC0EC33DCD9F46538B747A72A7BFAA3B333852CC474DB5ADA7633`;
- run 2:
  `B0F94AFDC6F1BB20285CA9FD416DDB249521AC678AC84F45C0881F4D9DCB8FF2`;
- run 3:
  `8E8369479E135B8BBD3FC292B051B314EEC61E1AC98DC56CB871CEB8299978EB`;
- run 4:
  `2876A0D76708725723BF382DCE3E42A1C37327D88775671ABB6C9EBD448C77C6`.

Runs 2–4 were downloaded but not numerically opened before this protocol was
written.

## 3. Raw ARA representation

Only timestamps, two arm angles and recorded angular velocities are used. No
Fourier transform, Hilbert phase, SVD/POD, learned model or pendulum equation
enters the endpoints.

Angles are circular-mean centred independently within each run. A parent cycle
is one positive-direction centre crossing of arm 1 to the next. Candidate
crossings closer than `0.4 × 1.333 s` are merged using the existing pendulum
spacing rule.

The signs of the two centred raw angles give four children:

\[
C_{AA}=(+,+),\quad
C_{AB}=(+,-),\quad
C_{BB}=(-,-),\quad
C_{BA}=(-,+).
\]

## 4. Ordered child timing

Within each eligible parent cycle, the fractional cycle time is
\(u\in[0,1)\). For every child \(i\), calculate its circular time centroid:

\[
\mu_i=
\frac{1}{2\pi}
\arg\left(
\frac1{N_i}\sum_{u\in C_i}e^{2\pi\mathrm i u}
\right)
\pmod1.
\]

All four children must have at least three samples.

Sorting the four centroids around the circle gives four timing gaps
\(\mathbf g\) that sum to one. Child names are retained for intercycle
comparison; sorting is used only for the within-cycle gap geometry.

## 5. Candidate non-closing steps

For candidate step \(\alpha\), generate the four orbit points

\[
\{0,\alpha,2\alpha,3\alpha\}\pmod1
\]

and their sorted circular gap template. Compare observed and candidate gaps by
minimum total-variation distance under circular rotation and reflection.

Frozen candidates:

| name | step |
|---|---:|
| Phi | \(\phi^{-2}=0.381966\) |
| close rational | \(3/8=0.375\) |
| close rational | \(2/5=0.4\) |
| silver irrational | \(\sqrt2-1=0.414214\) |
| third | \(1/3\) |
| quarter | \(1/4\) |
| e-conjugate | \(3-e=0.281718\) |
| pi-conjugate | \(\pi-3=0.141593\) |

Phi timing-gap specificity passes only if its median distance is the smallest
in the pooled frozen replication runs 2–3.

## 6. Intercycle rotation and recurrence

For every adjacent pair of eligible cycles, retain the child labels and form
the four signed circular shifts:

\[
\delta_i=
\mu_i^{(n+1)}-\mu_i^{(n)}
\pmod1.
\]

Their circular mean gives the common child-pattern rotation
\(\Delta_n\in[-0.5,0.5]\). Its folded magnitude
\(d_n=|\Delta_n|\in[0,0.5]\) is:

- near `0`: recurrence/phase locking;
- non-zero: continued relational drift;
- near a candidate step: that candidate's proposed handover.

Candidate drift distance is \(|d_n-\alpha_{\rm folded}|\). Phi drift
specificity passes only if Phi has the smallest pooled run-2/3 median.

## 7. Holding TE-ARA allocation approximately fixed

Each cycle receives fixed, predeclared strata from:

- child entropy-inequality \(I_4\), width `0.10`;
- diagonal share \(p_{AA}+p_{BB}\), width `0.20`;
- current parent amplitude rung
  \(\log_2(A/\operatorname{median}A)\), width `0.50`.

Strata are run-specific and require at least three scored cycles.

For each candidate, combine within-cycle gap distance and intercycle drift
distance:

\[
S_\alpha=
1-\frac12\left(
d_{\rm gap,\alpha}+2d_{\rm drift,\alpha}
\right).
\]

Within each stratum, centre \(S_\alpha\) and next-cycle parent amplitude
retention \(R_P\), then calculate their pooled Spearman correlation.
`5,000` within-stratum permutations, seed `20260730`, provide a one-sided
p-value.

Phi retention specificity passes only if:

1. its conditional correlation is positive with `p < 0.05`; and
2. it exceeds every rational and irrational candidate.

## 8. Resonance-death direction

After the same allocation/amplitude-stratum centring, compare:

- near-repeat cycles: \(d_n<0.05\);
- non-closing cycles: \(0.10\le d_n\le0.45\).

The frozen prediction is that the non-closing group has greater next-cycle
parent amplitude retention. A `5,000`-permutation within-stratum one-sided test
must give `p < 0.05`.

This test does not assume that ever-larger drift is better.

## 9. Final confirmation

Run 4 is not used in pooled run-2/3 decisions. It confirms only if:

1. Phi remains the closest gap or drift candidate and is no worse than the
   other on the second specificity metric;
2. conditional Phi score versus retention is positive;
3. the non-closing-minus-repeat retention difference is positive.

## 10. Verdict

Five check families:

1. pooled Phi timing-gap specificity;
2. pooled Phi intercycle-drift specificity;
3. pooled conditional Phi retention specificity;
4. pooled resonance-death direction;
5. run-4 confirmation.

- **SUPPORTED:** `5/5`;
- **MIXED:** `3–4/5`;
- **NOT SUPPORTED:** `0–2/5`.

## 11. Boundaries

- Four child labels are a declared raw ARA cut, not proof of fundamental
  ontology.
- Global circular-mean centring is unsupervised but uses the complete run.
- Occupancy closure and TE-ARA normalization are definitional.
- Phi must beat close rational neighbours, especially `3/8`; merely being
  “near Phi” does not pass.
- A null result may reject this instrument without rejecting every possible
  lower-rung driver.
