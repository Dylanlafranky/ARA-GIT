# T405 — parent landmark versus child distortion

Date frozen: 2026-08-18

## ARA question

The pure or parent-scale landmark at `0.5` is a relational reference, not a compulsory coordinate for every child time slice. Inputs, outputs, lower-rung participation, and boundary asymmetry may displace an individual child expression while the parent aggregate still identifies the `0.5` neighbourhood.

T405 tests whether the T400 child release crest's displacement from `0.5` varies systematically with saved branch participation. If so, `0.706` is evidence of a distorted child expression of the parent landmark rather than a reason to reject the landmark. If not, the displacement remains observed but unexplained.

## Who, what, when, where, why and how

- **Who:** all valid T400 repeated calibration-to-holdout splits.
- **What:** child displacement `delta = population_local_mode - 0.5` and fitted prompt participation `q = n_prompt / (n_prompt + n_delayed)`.
- **When:** each split's already frozen T400 child window; no boundary or event is refit.
- **Where:** the local cumulative-parent-ARA child coordinate `[0,2]`.
- **Why:** test the ARA distinction between a parent/aggregate landmark and a child time-slice distorted by participating branches.
- **How:** Spearman rank relation between `q` and `delta`, 50,000 fixed-seed permutations, leave-one-split-out sign/stability, and a mediation diagnostic through the saved left equality-boundary time.

## Frozen direction and controls

Primary prediction: greater competing prompt participation produces a larger positive child displacement from the `0.5` parent landmark.

Controls and qualifications:

1. Delayed fraction is exactly `1-q` and is reported only as the reciprocal orientation, not independent evidence.
2. The left equality boundary is expected to move with `q`; correlations through it are a mechanism diagnostic, not a second replication.
3. Holdout effective delayed weight is downstream and noisy. Its relation is exploratory.
4. The 20 deterministic splits overlap heavily. They test internal consistency, not external generalization.

## Gates

- at least 15 valid splits;
- primary Spearman `rho >= 0.70`;
- permutation `p <= 0.05`;
- all leave-one-out correlations remain positive and their minimum is at least `0.60`;
- the saved `0.5` parent landmark remains below the median child crest, establishing displacement rather than exact equality.

## Claim boundary

A pass supports a participation-dependent displacement law inside this fitted population. It does not identify the physical energy carrier, prove universal `0.5` displacement across media, or predict one individual muon decay.
