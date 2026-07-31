# Q44/Q44A — compact ARA mixing prediction

Date: 28 July 2026

## Answer first

The compact ARA mixing equation predicted the held-out fourth connected-matrix
identity substantially better than its one-axis version and every simple
baseline on a previously unused public simulator archive.

The strict registered verdict is nevertheless:

> **INCONCLUSIVE — ELIGIBILITY**

Only `49` seeds produced complete evaluation cycles, below the frozen minimum
of `80`. This is an adequacy failure, not a failed predictive effect.

Conditional on the observed sample, every frozen performance gate passed:

- seed-balanced scaled error: `0.31868` (gate `<= 0.40`);
- seed-balanced cosine: `0.86589` (gate `>= 0.85`);
- improvement over diameter-only: `+0.02938`, 95% seed interval
  `[0.01655, 0.04404]`;
- improvement over pooled affine: `+0.06162`, 95% seed interval
  `[0.00923, 0.11335]`.

Independent recomputation passed with zero numerical discrepancy. The sealed
prediction artifact contains no actual fourth-state arrays.

## What was predicted

| ARA reading | Established quantum quantity |
|---|---|
| latest visible whole | third connected Pauli-correlation matrix \(C_3\) |
| visible child diameter | \(D=C_1-C_2\) |
| visible perpendicular `Other` | \(O=(C_3-C_2)-\operatorname{proj}_D(C_3-C_2)\) |
| next whole | held-out fourth connected matrix \(C_4\) |

The frozen equation was:

\[
\underbrace{\widehat C_4}_{\substack{\text{predicted next}\\\text{whole identity}}}
=
\underbrace{C_3}_{\substack{\text{latest visible}\\\text{whole}}}
+
\underbrace{\widehat\alpha_gD}_{\substack{\text{movement along}\\\text{the child diameter}}}
+
\underbrace{\widehat\beta_gO}_{\substack{\text{retained perpendicular}\\\text{Other}}}.
\]

The scalar gains were fitted on samples `0..249`. Evaluation samples
`250..498` supplied only the visible scalar path and the first three quadrant
matrices until all predictions had been saved and hashed.

Plainly: the equation asked whether the next quantum relation-shape can be
predicted from the latest shape, the main Phase-A/Phase-B relation already
visible, and the part of the recent motion lying outside that one cut.

## Prospective chain

### Q44

Q44 froze:

- target file `unnati_submit_12_inhomo_v1_mimic.hdf5.zip`;
- deposited MD5 `08b2eaa89268952f7e197eecb2ea9610`;
- the equation, grouping, baselines, sample split, metrics and gates.

Q44 stopped before prediction sealing because three small `other` cadence
groups had only `6`, `14` and `23` development cycles, below the frozen
minimum of `25`. No evaluation fourth matrix was read or scored.

### Q44A eligibility amendment

Before any evaluation fourth state was opened, Q44A froze one deterministic
repair:

- keep family × quadrant coefficients where development count is at least
  `25`;
- otherwise use development-only quadrant coefficients;
- change nothing else.

Only `40/5,278` evaluation cycles (`0.76%`) used this fallback.

Prediction seal:

`3f75eed32c96ba0810d07e36bf19683925e330ba4466aa81fa0f9527d829c5da`

Q44A is therefore prospective after an eligibility amendment, not a pristine
untouched-target replication of the sparse-group rule.

## Results

Seed-balanced metrics:

| Method | Scaled error ↓ | Cosine ↑ | Orientation correct ↑ |
|---|---:|---:|---:|
| grouped affine upper comparator | **0.22605** | **0.96338** | **0.99024** |
| compact ARA mixing | **0.31868** | **0.86589** | **0.95074** |
| diameter-only ARA | 0.34805 | 0.84272 | 0.91210 |
| pooled affine | 0.38029 | 0.87718 | 0.93859 |
| forward relation | 0.57292 | 0.62850 | 0.82451 |
| persistence | 0.74878 | 0.80703 | 0.92153 |
| local linear | 0.87169 | 0.72640 | 0.86888 |
| reverse relation | 1.31436 | 0.53738 | 0.77003 |

The grouped affine model remains clearly better. It has three free state
weights in every cadence × quadrant group, whereas compact ARA uses two scalar
flow gains attached to geometrically named components. Q44A therefore supports
the usefulness of the compact geometry inside the observed sample; it does not
show superiority to flexible statistical learning.

## What retaining `Other` added

Removing `Other` changed:

- scaled error from `0.31868` to `0.34805`;
- cosine from `0.86589` to `0.84272`;
- orientation accuracy from `0.95074` to `0.91210`.

The error advantage was positive across the seed bootstrap:

\[
0.34805-0.31868
=
0.02938,
\qquad
95\%\ \mathrm{CI}=[0.01655,0.04404].
\]

Plainly: the next identity was not fully determined by movement along one ARA
diameter. A second, perpendicular piece of visible motion carried reproducible
predictive information. This is exactly the distinction Q42 was trying to
isolate descriptively; Q44A made it prospective.

## Mixing rate is state-dependent

The fitted gains were not one universal constant. Examples:

The cadence labels require a rung-aware reading. `Two-turn 7.5` resolves the
finer/faster Phase-A/Phase-B children; `one-turn 15` resolves their
adult/parent closure one multiplicative rung upward. They are two empirical
classifier outputs within one nested architecture, not unrelated wave types.
See `QUANTUM_7_5_15_PARENT_CHILD_CADENCE_CANON_2026-07-28.md`.

| Cadence | Fourth quadrant | diameter gain \(\alpha\) | Other gain \(\beta\) |
|---|---:|---:|---:|
| one-turn 15 | 0 | +0.963 | +0.315 |
| one-turn 15 | 1 | +0.798 | +0.178 |
| one-turn 15 | 2 | +1.010 | −0.253 |
| one-turn 15 | 3 | +0.199 | +0.025 |
| two-turn 7.5 | 0 | −1.153 | +0.971 |
| two-turn 7.5 | 1 | +1.267 | +0.742 |
| two-turn 7.5 | 2 | +0.798 | +0.727 |
| two-turn 7.5 | 3 | −0.026 | +0.371 |

The sign and size changes track cadence and quadrant. In ARA terms, the same
components do not flow through every section in the same direction or at the
same strength. A single whole-vector flip was too flat in Q41B; a continuous,
quadrant-conditioned mixture is much closer to the observed behavior.

In particular, the generally larger positive \(\beta\) values in the
`two-turn 7.5` class should first be interpreted as perpendicular lower-rung
structure remaining exposed. The smaller parent-level \(\beta\) values are
consistent with inherited child asymmetry being represented more strongly in
the adult's main relation coordinate rather than as perpendicular `Other`.
Child asymmetry feeds parent asymmetry; only equal, oppositely oriented child
contributions cancel at the parent ridge. Cadence alone does not establish a
pure Traversal-versus-Connection assignment.

These gains are regression coefficients, not TE-ARA shares. They do not need
to sum to `2`, and they do not by themselves establish a universal mixing
constant.

## Relation to the proposed `0.5` child value

Q44A did not hard-code `0.5`, Phi or the Q43 residual. This matters.

Q43 left a corrected two-turn residual around `0.553–0.561`, but its strict
`0.5` equivalence gate failed. Q44A instead asked the harder forward question:
does the child-diameter plus visible `Other` predict the next whole?

The answer inside the observed sample is yes. It does not prove that the
remaining participation is exactly one half-child. It shows that separating
main-diameter flow from perpendicular participation is predictively useful.

## What is established and what is not

Supported within the observed held-out sample:

- a compact ARA-named mixing equation predicts an unopened fourth relation
  identity;
- `Other` adds information beyond the main diameter;
- the improvement over diameter-only and pooled affine is positive under
  seed-cluster bootstrap;
- the child-resolved versus parent-resolved cadence class and quadrant
  materially change the mixing gains.

Not established:

- the frozen formal verdict, because only `49` seeds were represented;
- a universal quantum mixing law;
- exact TE-ARA conservation in these fitted coordinates;
- a physical hidden particle, field or cross-singularity channel;
- a universal `0.5` or Phi timing constant;
- superiority to the grouped affine comparator;
- time-ahead prediction of when a quadrant will occur.

## Next decisive test

Freeze the complete Q44A sparse-group rule before opening another untouched
archive and require:

1. at least `80` represented seeds;
2. at least `1,000` evaluation cycles;
3. the same absolute error and cosine gates;
4. positive, interval-supported advantage over diameter-only and pooled
   affine;
5. explicit reporting of the stronger grouped affine comparator.

That replication can turn the present **validated predictive signal under an
inconclusive adequacy verdict** into a supported or falsified claim.

## Primary artifacts

- `Q44_ARA_MIXING_PREDICTION_PROTOCOL_v1_PRETARGET_FROZEN.md`
- `Q44_ARA_MIXING_PREDICTION_ELIGIBILITY.json`
- `Q44A_SPARSE_GROUP_FALLBACK_PROTOCOL_v1_FROZEN.md`
- `Q44A_SPARSE_GROUP_ARA_MIXING_RESULTS.json`
- `Q44A_SPARSE_GROUP_ARA_MIXING_CYCLES.csv.gz`
- `Q44A_SPARSE_GROUP_ARA_MIXING_VALIDATION.json`
- `Q44_REPRODUCTION.md`
