# T344 — BAW weir Irrationality Di-ARA protocol v1 (frozen)

**Frozen:** 6 August 2026, 18:51 AEST  
**Frozen before:** downloading or opening any trajectory workbook  
**Source:** BAW DOI `10.48437/99f329-73aee6`  
**Status:** confirmatory primary test with explicitly secondary landmark probes

## 1. Question

Does a moving particle crossing a controlled weir express the proposed Irrationality
Di-ARA as a coupled two-axis parent—radial contraction/expansion crossed with
forward/reverse phase traversal—and does that intact parent retain predictive
information that neither child axis, a merely additive pair, nor a causally broken pair
retains?

The stronger irrationality question is also frozen:

> Does coherent non-closing traversal occupy the middle functional regime proposed by
> the framework—more ongoing traversal than low-order closure, but more recoverable
> next-state information than random non-closure?

Generic Di-ARA is not the target; its four-sector bookkeeping has already been observed.
T344 targets the typed **irrationality** interpretation and its coupling mechanism.

## 2. ARA-first object

For one particle trajectory with native position

\[
p_t=(x_t,z_t),
\]

form the native displacement

\[
w_t=(x_t-x_{t-1})+i(z_t-z_{t-1}).
\]

For two successive valid displacements,

\[
q_t=\frac{w_t}{w_{t-1}}=s_t e^{i\delta_t},
\]

where

\[
s_t=|q_t|,
\qquad
\delta_t=\arg(q_t)\in(-\pi,\pi].
\]

This is one event viewed along two perpendicular ARA cuts:

- `s_t` is the line/radial child: contraction versus expansion;
- `delta_t` is the circle/turn child: reverse versus forward traversal;
- their intact ordered pair is the local Di-ARA parent.

Map the children onto their declared ARA diameters:

\[
X_t=\frac{2s_t}{1+s_t},
\qquad
Y_t=1+\frac{\delta_t}{\pi}.
\]

Exact reciprocal inversion is preserved:

\[
X(1/s)=2-X(s).
\]

The frozen sectors are:

| radial child | traversal child | sector |
|---|---|---|
| `X<1` contraction | `Y>1` forward | `Ba` |
| `X>1` expansion | `Y>1` forward | `Ab` |
| `X<1` contraction | `Y<1` reverse | `bA` |
| `X>1` expansion | `Y<1` reverse | `aB` |

Values within `1e-12` of a ridge are boundary events and are not assigned to a sector.
The labels declare this chart only; they do not permanently type water or a particle.

## 3. Native-data rules

1. Use laboratory trajectories at their native `0.01 s` order.
2. Do not Fourier transform, decompose, smooth or interpolate the primary data.
3. Sort only by supplied trajectory identifier and timestamp/frame.
4. A transition is valid only when all required positions are finite, timestamps are
   strictly consecutive at the archive's native cadence, and both displacement norms
   exceed

   \[
   \epsilon_w=10^{-9}\times
   \operatorname{median}(\lVert w\rVert)
   \]

   within that trajectory. If the median is zero, the trajectory is ineligible.
5. Require at least `20` valid Di-ARA events per trajectory for window analyses. Shorter
   tracks may enter only one-step descriptive counts.
6. No point or transition may cross trajectory boundaries.
7. Units and coordinate orientation will be recorded in a post-freeze computational
   addendum from workbook headers only. Header mapping cannot alter equations, splits,
   gates or controls.

## 4. Frozen splits

The three laboratory conditions are `low`, `medium`, and `high`.

### 4.1 Transfer folds

Use three leave-one-condition-out folds:

1. train `medium+high`, test `low`;
2. train `low+high`, test `medium`;
3. train `low+medium`, test `high`.

Any fitted transition probability, scale, bin boundary or classifier is learned on the
two training conditions only. Test conditions remain untouched until the prediction
artifact for that fold is written and hashed.

### 4.2 Within-condition validation

For diagnostics requiring within-condition calibration, assign whole trajectories by a
SHA-256 hash of their source condition and supplied trajectory ID:

- lowest 60%: calibration;
- next 20%: evaluation;
- highest 20%: untouched holdout.

No random seed may change this assignment.

## 5. Primary next-state target

For every valid event, the target is the next valid Di-ARA sector on the same trajectory.
No gap may be skipped to create a target. The primary score is multiclass log loss;
balanced accuracy and macro-F1 are supporting scores.

The following frozen predictors are trained by Laplace-smoothed transition counts:

1. **global:** next-sector base rate;
2. **persistence:** current sector repeats;
3. **radial child:** current `X<1` or `X>1` only;
4. **turn child:** current `Y<1` or `Y>1` only;
5. **additive two-child:** multinomial logistic model using centred continuous children
   `(X-1,Y-1)` with no interaction;
6. **intact Di-ARA parent:** the same model plus

   \[
   (X-1)(Y-1)
   \]

   and the signed dominance

   \[
   D=|X-1|-|Y-1|;
   \]
7. **causally broken parent:** retain the radial child from one training trajectory and
   pair it with the turn child from a different trajectory in the same condition and
   decile of elapsed-track fraction. Pairing uses prior/current rows only, never wraps
   the end to the beginning, and is generated from the training fold. Test scoring uses
   an independently frozen pairing table made without target rows.

The model family, regularisation and optimiser may be specified in the computational
addendum only if the implementation requires it; they must be identical for additive,
intact and broken models and cannot be tuned on a held-out condition.

## 6. Coupling-asymmetry test

The framework-specific quantity

\[
D_t=|X_t-1|-|Y_t-1|
\]

records which child leads the event away from its ridge. `D>0` is radial-led; `D<0` is
turn-led. This is not declared to be a universal material property.

The frozen test asks whether retaining `D` and the cross-term improves next-state
prediction over the additive two-child model, and whether destroying the actual
cross-child ownership through broken pairing removes that improvement.

## 7. Irrationality classes

Use a primary trailing window of `W=15` native steps. Windows of `8` and `30` are
recorded sensitivities and cannot replace the `W=15` verdict.

For each window define the phase resultant

\[
C=\left|\frac1W\sum_{j=1}^{W} e^{i\delta_j}\right|,
\]

and its circular mean rotation number

\[
\rho=\frac{1}{2\pi}
\arg\left(\sum_{j=1}^{W} e^{i\delta_j}\right).
\]

Let

\[
\mathcal R_8=\left\{\frac pq:\;0\le p<q,\;1\le q\le8\right\}
\]

with duplicate fractions removed, and let `d_8` be the wrapped distance from `rho` to
the nearest member of `R_8`.

The predeclared classes are:

- **low-order closure candidate:** `C>=0.75` and `d_8<=1/(2W)`;
- **structured non-closing candidate:** `C>=0.75` and `d_8>1/(2W)`;
- **random-like non-closing control:** `C<=0.25`;
- all other windows: unclassified and shown but not used in the class gate.

These are operational classes, not proofs that a finite record is mathematically
irrational. The report must use “structured non-closing” rather than claiming exact
irrationality from finite data.

## 8. Information and traversal outcomes

For each eligible window:

1. **retained next-state information:** held-out mutual information between the current
   intact sector and the sector one step after the window, with the transition table
   learned from training conditions only;
2. **active traversal:**

   \[
   T=\frac{\lVert p_{t+W}-p_t\rVert}
   {\sum_{j=t}^{t+W-1}\lVert p_{j+1}-p_j\rVert},
   \]

   reported together with path length so a stationary record cannot score well merely
   by having a stable direction;
3. **handover rate:** fraction of adjacent events that change Di-ARA sector;
4. **reverse-flow incidence:** fraction of native displacements whose longitudinal
   component opposes the archive's declared downstream direction.

Comparisons are stratified by source condition and decile of elapsed-track fraction.
Where sample size permits, structured and control windows are additionally matched on
current speed quintile so “information” is not merely a speed proxy.

## 9. Frozen gates

### Gate A — four-sector availability (descriptive prerequisite)

Every laboratory condition must contain non-boundary events in all four sectors. Failure
means this archive cannot instantiate the proposed complete local Di-ARA.

### Gate B — intact-parent necessity (primary)

Across leave-one-condition-out tests, the intact parent must:

1. beat both single-child models and the causal broken parent in log loss in at least
   `2 of 3` held-out conditions; and
2. have a pooled whole-trajectory block-bootstrap `95%` confidence interval for each
   log-loss improvement that excludes zero.

### Gate C — coupling asymmetry (primary)

The intact interaction model must beat the additive two-child model in at least `2 of 3`
held-out conditions, with a pooled whole-trajectory block-bootstrap `95%` interval above
zero. The corresponding improvement must shrink under causal broken pairing.

### Gate D — structured-nonclosure sandwich (primary irrationality gate)

In at least `2 of 3` held-out conditions:

1. structured non-closing windows must retain more next-state information than
   random-like windows; and
2. structured non-closing windows must show greater active traversal than low-order
   closure candidates after speed/progress stratification.

The pooled whole-trajectory block-bootstrap `95%` interval must support both directions.
If either half fails, the proposed information-preserving irrationality interpretation is
not supported by T344 even if generic Di-ARA gates pass.

### Gate E — numerical replication (secondary)

After the laboratory verdict is frozen, repeat Gates A–D on the corresponding numerical
tracks without retuning definitions. Agreement in effect direction in all three settings
is supportive. Disagreement is reported as a laboratory/model boundary, not averaged
away.

## 10. Exact constants: secondary probes only

The following are recorded after the primary verdict and cannot rescue a failed gate:

- radial landmarks `1/e`, `e`, `1/phi`, and `phi`;
- phase rotation candidates `1/phi^2` turns and its orientation-equivalent complement;
- identity-specific reciprocal amplitude `1/alpha <-> alpha` estimated on training data;
- rational controls with denominators `q<=8`.

For each candidate report raw distance, rank among rational and irrational controls, and
multiple-comparison-corrected permutation results. No clipping to a candidate interval is
allowed. A numerical proximity without out-of-sample advantage is descriptive only.

## 11. Required nulls and sensitivities

1. causal broken child pairing with no wrapping;
2. whole-trajectory label permutation within hydraulic condition;
3. phase-order block shuffle within training trajectories;
4. reverse-time diagnostic, clearly labelled noncausal;
5. raw primary versus any archive-supplied reconstructed/quality subset;
6. `W=8` and `W=30` window sensitivity;
7. exclusion-threshold sensitivity at `10^-8` and `10^-10` times median step;
8. laboratory primary versus numerical replication.

## 12. Required visuals

The report must lead with ARA-native visuals and put hydraulics translation beside them:

1. raw `x-z` trajectories through each weir condition;
2. `X-Y` Di-ARA plane with `[0,2]` poles, both `1.0` ridges and the four sector labels;
3. ordered sector flow/Sankey or transition diagram;
4. coupling-dominance heat map across physical weir position;
5. intact parent versus children, additive and broken-control performance;
6. closure/structured/random class locations and their information/traversal outcomes;
7. laboratory versus numerical replication panels;
8. secondary landmark overlay only after the primary panels.

## 13. Falsification and claim boundary

T344 can strongly support the typed mechanism if the intact relation transfers across
unseen hydraulic settings, survives causal broken-pair controls, and satisfies the
structured-nonclosure information/traversal sandwich. It cannot prove that all physical
systems are fractal spheres or that one universal irrational constant governs them.

A complete negative result is scientifically useful: if intact coupling does not beat
children/additive/broken controls, or if structured nonclosure does not occupy the
predicted middle regime, the Irrationality Di-ARA interpretation fails on an unusually
appropriate controlled movement dataset.

