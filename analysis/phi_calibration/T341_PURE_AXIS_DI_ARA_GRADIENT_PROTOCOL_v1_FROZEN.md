# T341 frozen protocol — pure-axis Di-ARA gradient test

**Frozen:** 5 August 2026, before calculating any T341 conditional-axis or
gradient-budget score  
**Test ID:** `T341-PURE-AXIS-DI-ARA-GRADIENT-v1`  
**Originator of the ARA hypothesis:** Dylan La Franchi  
**Operationalisation and implementation:** Codex  
**Status:** frozen cross-question test on previously opened data; not a
pristine discovery test

## 1. Correction being tested

T340 treated the radial and angular constants as possible universal native
step sizes. Dylan corrected that interpretation: the observations remain
points moving through one Di-ARA with mixed gradients. A straight line and a
circle are the two pure-axis limits. Most observations can contain both.

T341 therefore asks three linked questions:

1. as movement approaches the radial/diameter axis, does its radial magnitude
   approach the reciprocal exponential pair `1/e <-> e`?
2. as movement approaches the angular/circumference axis, does its angular
   magnitude approach the golden non-closing turn?
3. between those axes, do the two normalized contributions trade as one
   Di-ARA budget rather than behaving like independently paired magnitudes?

Failure of a fixed pure-axis constant does not erase the two-axis Di-ARA
coordinate. Conversely, occupying all four sign quadrants cannot by itself
pass the pure-axis test.

## 2. Common measured geometry

For every eligible local relation,

\[
q_n=\frac{z_{n+1}}{z_n}=s_ne^{i\Delta\theta_n},
\qquad s_n>0,
\qquad \Delta\theta_n\in(-\pi,\pi].
\]

Retain the exact ARA cuts

\[
X_n=\frac{2s_n}{1+s_n},
\qquad
Y_n=1+\frac{\Delta\theta_n}{\pi}.
\]

Their unsigned distances from the two ridges are

\[
d_{r,n}=|X_n-1|,
\qquad
d_{c,n}=|Y_n-1|.
\]

The Di-ARA mixing angle is

\[
\gamma_n=\operatorname{atan2}(d_{c,n},d_{r,n})
\in[0,\pi/2].
\]

- `gamma=0`: pure radial/diameter or line direction;
- `gamma=pi/2`: pure angular/circumference or circular direction;
- intermediate values: the mixed Di-ARA gradient.

The signed quadrants remain contraction/expansion crossed with
reverse/forward. Signs establish orientation; the following tests use
magnitudes only.

## 3. Fixed pure-axis landmarks

Define radial and angular magnitudes

\[
R_n=|\log s_n|,
\qquad
C_n=\frac{|\Delta\theta_n|}{2\pi}.
\]

The proposed pure radial landmark is

\[
s\in\{1/e,e\}
\quad\Longleftrightarrow\quad
R_e=1.
\]

Because principal angles wrap at half a turn, the proposed golden circular
magnitude is

\[
C_\phi=\phi^{-2}=0.38196601125\ldots,
\]

which is orientation-equivalent to a `1/phi` turn taken around the opposite
direction.

## 4. Frozen purity regions

The primary pure-axis cones are fixed geometrically, not fitted by dataset:

- line-dominant: `gamma <= 15 degrees`;
- circle-dominant: `gamma >= 75 degrees`;
- mixed reference: `30 degrees <= gamma <= 60 degrees`.

Nested `10` and `20` degree cones are reported as sensitivity only. They
cannot replace the primary 15-degree result.

Each primary cone is eligible for a domain-level verdict only if it contains
at least `30` observations and both signs of its own axis contain at least
`10` observations: contraction/expansion for line, reverse/forward for
circle.

## 5. Fixed endpoint scores

For the line cone, let `R_med` be the median `R`. Candidate radial score:

\[
D_r(\alpha)=|R_{med}-\log\alpha|.
\]

Fixed radial candidates are plastic constant, `sqrt(2)`, `3/2`, Phi, `2` and
`e`. Exact exponential line support requires `e` to be the closest fixed
candidate and `D_r(e)<=0.10`.

For the circle cone, let `C_med` be the median `C`. Candidate angular score:

\[
D_c(\tau)=|C_{med}-\tau|.
\]

Fixed angular candidates are `1/4`, `1/3`, `1/e`, `3/8`, `phi^-2`, `2/5`
and `sqrt(2)-1`. Exact golden-circle support requires `phi^-2` to be the
closest fixed candidate and `D_c(phi^-2)<=0.05` turns.

Calibration-only line and circle medians are frozen as identity-specific
fitted controls and transferred unchanged to evaluation/holdout. Exact
constants must score no worse than those controls to pass the strong endpoint
gate.

## 6. Frozen gradient-budget test

The primary ARA mixture budget is the linear two-axis account

\[
B_{e,\phi,n}
=
\frac{R_n}{\log e}
+
\frac{C_n}{\phi^{-2}}
=R_n+\frac{C_n}{\phi^{-2}}.
\]

Pure line gives `(R,C)=(1,0)` and pure circle gives
`(R,C)=(0,phi^-2)`; both give `B=1`. Intermediate gradients are predicted to
trade between those endpoints while remaining near the same budget.

For any fixed pair `(alpha,tau)`, score

\[
L(\alpha,\tau)
=
\operatorname{median}
\left|
\frac{R_n}{\log\alpha}+\frac{C_n}{\tau}-1
\right|.
\]

All `6 x 7 = 42` predeclared radial/angular candidate pairs compete. The
target `(e,phi^-2)` must be the best fixed pair for a fixed-pair pass. Its
absolute budget gate is `L<=0.15`.

The Euclidean alternative

\[
B_2=\sqrt{(R/\log e)^2+(C/\phi^{-2})^2}
\]

is reported as a sensitivity, not a rescue.

## 7. Coupling control

Use `1,000` deterministic permutations per primary evaluation/holdout split.
Keep every `R` value fixed and permute the `C` values within that domain and
split, preserving both marginals while breaking their event-wise gradient
coupling. Seed: `3412026` plus a fixed domain offset.

The observed linear-budget loss must beat at least `95%` of permuted losses:

\[
p=\frac{1+\#\{L_{null}\le L_{obs}\}}{1001}<0.05.
\]

Also report Spearman correlation between `R` and `C`. A negative relation is
predicted by a compensating gradient, but correlation alone is not a pass.

## 8. Frozen datasets and populations

### Recorded qutrit — primary

Reuse the checksum-locked Q53 whole-circle external-centre extraction used by
T333/T340. Use only the frozen algebraic `circle` centre and local lag `1`.
The first half of each of the three planes is calibration; the second half is
holdout. Apply the inherited amplitude, residual and continuity filters.
Pool the three planes for the primary result; plane results are sensitivities.

### Recorded bubbles — transfer

Reuse T334 observed octave-relative events only. Preserve its calibration,
evaluation and holdout source splits. Use `s=u=raw_scale/2` and the recorded
`delta_rad`. Pool all four levels for the primary result; level results are
sensitivities.

### Recorded river — primary replication

Reuse T335 observed field events across all `41` intact elevation-rank paths.
Preserve calibration, evaluation and holdout bend sections. Use
`scale_ratio_s` and `turn_delta_rad`. Rank-1 thalweg results are sensitivity
because its split-level pure cones may be too small.

### Exclusion

The muon scheduling construction is excluded from the cross-domain verdict
because Phi and exponential components are already embedded in its model.

All three source families were previously opened. T341 is a new frozen
conditional question on inherited data, not independent discovery evidence.

## 9. Domain and cross-domain verdicts

A domain split receives:

- **line pass**: eligible line cone, `e` is the closest fixed candidate,
  `D_r(e)<=0.10`, and exact `e` beats the calibration-fitted control;
- **circle pass**: eligible circle cone, `phi^-2` is the closest fixed
  candidate, `D_c(phi^-2)<=0.05`, and exact Phi beats the calibration-fitted
  control;
- **gradient pass**: `(e,phi^-2)` is the best of 42 fixed pairs,
  `L<=0.15`, and permutation `p<0.05`;
- **joint pass**: line, circle and gradient all pass.

Primary cross-domain support requires joint passes in at least `2/3` of the
real-data primary holdouts. `1/3` is **PARTIAL / IDENTITY-SPECIFIC**. `0/3` is
**NOT SUPPORTED** for the proposed universal pure-axis constants and budget.

The four-sector Di-ARA geometry is not adjudicated by this fixed-constant
verdict; T333–T335 already tested that separate claim.

## 10. Required outputs

- protocol and SHA-256;
- source audit;
- pooled split summary and cone sensitivities;
- all fixed-pair budget scores;
- 1,000-null distributions per primary evaluation/holdout split;
- machine-readable JSON/CSV;
- one result figure;
- independent validator that does not import the primary runner;
- claims, glossary, hypothesis and provenance updates after the result.

