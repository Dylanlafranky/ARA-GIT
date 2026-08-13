# T343 — intact-versus-broken Di-ARA parent coupling

## Frozen protocol v1

**Frozen:** 5 August 2026  
**Originator:** Dylan La Franchi  
**Status:** frozen before any T343 endpoint was scored  
**Relation to T342:** new question on the same source battery; not an independent dataset discovery

## 1. Originator claim being tested

Two perpendicular ARA relations form a Di-ARA parent with four mixed regions:

\[
Ba\;|\;Ab
\qquad\text{above the horizontal ridge, and}\qquad
bA\;|\;aB
\quad\text{below it}.
\]

The four-region geometry is shared. The exact path, order, speed, cadence and
proportion of movement through it are identity-specific. T343 therefore does
**not** require one universal quadrant walk.

The empirical claim is narrower and more direct:

> For a correctly declared pair, the intact two-axis relation carries stable
> parent-level information that is not present in either axis alone and is
> weakened when the local pairing is deliberately broken.

In ARA language, the test asks whether the two children form an efficient
coupled parent branch. It does not ask whether every parent has the same gait.

## 2. Source battery and evidence class

T343 reuses the seven T342 source families and their frozen lineage blocks,
calibration/holdout divisions, caps and raw channel declarations:

1. pendulum;
2. hydraulic pressure;
3. bubbles;
4. cold-room temperature/humidity;
5. stereo acoustics;
6. recorded qutrit relations;
7. ordered river paths.

The exact source files, source hashes, preprocessing, block boundaries,
calibration origins and calibration scales must be inherited from T342. No
domain, channel or lineage may be changed after T343 scoring begins.

Because these records were already opened for T342, T343 is a frozen
cross-question test, not an untouched-source discovery. Any later independent
replication must use new source archives.

## 3. Frozen ARA coordinate

For each valid two-channel lineage, use the T342 calibration-only centring and
scaling to form

\[
z_t=u_t+i v_t,
\qquad
q_t=\frac{z_{t+1}}{z_t}=s_t e^{i\Delta\theta_t}.
\]

The two ARA cuts are

\[
X_t=\frac{2s_t}{1+s_t},
\qquad
Y_t=1+\frac{\Delta\theta_t}{\pi}.
\]

Define binary axis states

\[
R_t=\mathbf 1[X_t\ge1],
\qquad
C_t=\mathbf 1[Y_t\ge1],
\]

and the four-state parent address

\[
Q_t=(R_t,C_t).
\]

The inherited label map is frozen as

\[
\begin{array}{c|c}
Ba & Ab\\
\hline
bA & aB
\end{array}
\]

with `X=1` the vertical ridge and `Y=1` the horizontal ridge. Exact ridge
ties go to the positive side as written above. Labels are relational
addresses, not substances.

## 4. What counts as the intact parent

Only consecutive states inside the same frozen lineage block may form a
transition. The intact parent predictor is the calibration-estimated
four-state transition model

\[
P(Q_{t+1}\mid Q_t).
\]

Every row receives a Jeffreys pseudocount of `1/2` before normalization. The
model is fitted on calibration only and scored on holdout only. Its holdout
mean negative log probability is

\[
L_P=-\frac1N\sum_t\log P(Q_{t+1}\mid Q_t).
\]

No preferred transition direction is built into this model. Each identity is
allowed to learn its own complete `4×4` transition relation.

## 5. Child-only projections

The two child-only predictors use one Di-ARA axis at a time:

\[
P(Q_{t+1}\mid R_t),
\qquad
P(Q_{t+1}\mid C_t).
\]

They use the same calibration-only Jeffreys smoothing and the same intact
holdout target. Their log losses are `L_R` and `L_C`.

The parent advantages are

\[
\Delta_R=L_R-L_P,
\qquad
\Delta_C=L_C-L_P.
\]

Positive values mean the intact four-address parent carries transferable
information unavailable in that one-axis projection.

## 6. Broken-pair control

The load-bearing null keeps both child records but destroys their local
pairing.

For each of exactly `1,000` deterministic controls:

1. draw one shift fraction from `Uniform(0.10,0.90)` using seed
   `34320260805`;
2. alternate which raw standardized child is shifted (`u` on odd controls,
   `v` on even controls);
3. circularly shift that child separately inside every frozen lineage block;
4. use `k=max(1,min(n-1,round(f*n)))` for a block of length `n`;
5. use the same control number and fraction in calibration and holdout;
6. retain the unshifted child, both marginal value sequences, native cadence,
   lineage membership and sample counts;
7. recompute the broken `z`, `q`, `X`, `Y` and four-state address using the
   intact frozen calibration origin and scale;
8. fit `P(Q_intact,t+1 | Q_broken,t)` on calibration and score it against the
   same intact holdout target.

The broken-control loss is `L_B^(r)`. The one-sided exact Monte Carlo value is

\[
p_B=\frac{1+\#\{r:L_B^{(r)}\le L_P\}}{1001}.
\]

Lower loss is better, so `p_B≤0.05` means at least 95% of equal-complexity
broken pairings were worse than the intact parent.

## 7. Uncertainty for parent-versus-child advantage

For each eligible domain, compute per-lineage mean log-loss differences for
parent versus each child-only projection. Use exactly `10,000` deterministic
lineage-level sign-flip permutations with seed `34320260806 + domain_index`.

The one-sided probabilities are `p_R` for `Delta_R>0` and `p_C` for
`Delta_C>0`. This preserves within-lineage dependence and avoids treating
every high-rate sample as independent.

## 8. Eligibility and frozen domain verdict

A holdout domain is inferentially eligible when it has:

- at least `1,000` intact within-lineage transitions;
- at least `20` frozen holdout lineages;
- all four parent addresses present;
- at least `20` holdout states in each address;
- finite scores for all models and controls.

A domain passes only when all are true:

1. `Delta_R > 0` and `p_R ≤ 0.05`;
2. `Delta_C > 0` and `p_C ≤ 0.05`;
3. median broken-pair loss exceeds intact-parent loss;
4. `p_B ≤ 0.05`.

No adjacency, clockwise direction, universal sequence, cadence or fixed
quadrant proportion is a pass requirement.

## 9. Cross-domain verdict

At least five eligible domains are required.

- **SUPPORTED AS A TRANSFERABLE PARENT-COUPLING RULE:** at least 70% of
  eligible domains pass all four domain gates.
- **PARTIAL / PAIR-SPECIFIC:** at least two but fewer than 70% pass.
- **NOT SUPPORTED BY THIS CONSTRUCTION:** fewer than two pass.

A negative result weighs against this particular coordinate and declared pair
battery. It does not logically prove that no physical Di-ARA coupling can
exist.

## 10. Secondary diagnostics

Report without changing the verdict:

1. four-region occupancy and shares;
2. the full identity-specific `4×4` transition matrix;
3. conditional cross-axis information
   \[
   I(R_t;C_{t+1}\mid C_t)+I(C_t;R_{t+1}\mid R_t);
   \]
4. calibration-to-holdout transition-matrix divergence;
5. pole-reversal, axis-swap and time-reversal checks;
6. intact-versus-broken results when only `u` or only `v` is shifted;
7. effect sizes in nats and bits per transition.

Exact `e`, Phi, reciprocal-Phi and any universal quadrant gait are excluded
from T343. They cannot rescue or overturn the primary verdict.

## 11. Visual-first outputs

The result must be understandable without reading the statistical tables.
Generate:

1. one summary figure separating:
   - four-region geometry;
   - parent-versus-child advantage;
   - intact-versus-broken advantage;
2. one domain panel per medium with:
   - intact relation plane;
   - broken relation plane;
   - identity-specific `4×4` transition heatmap;
   - log-loss comparison with the complete broken-null distribution;
3. an interactive three-dimensional explorer with:
   - `X` = first ARA cut;
   - `Y` = perpendicular ARA cut;
   - `Z` = native within-lineage order/time;
   - intact/broken toggle;
   - lineage and medium selectors;
   - visible ridge planes at `X=1` and `Y=1`;
   - canonical `Ba/Ab/bA/aB` labels;
4. a plain-language card for every domain stating what extra information the
   intact pair retained, if any.

No smoothing curve may replace the raw ordered points in the primary visual.
Optional smoothing must be visibly secondary and removable.

## 12. Falsification and interpretation fence

T343 supports the intended claim only if intact coupling predicts its own
future parent address better than both one-axis children and equal-complexity
broken pairings on holdout data.

Merely drawing four quadrants, satisfying `X+(2-X)=2`, or finding a visually
pleasing path is insufficient. Those are geometry/bookkeeping, not the
empirical coupling result.

Conversely, T343 must not penalize an identity because it follows a different
valid path through the same four-region geometry. Common geometry and common
gait are separate claims.
