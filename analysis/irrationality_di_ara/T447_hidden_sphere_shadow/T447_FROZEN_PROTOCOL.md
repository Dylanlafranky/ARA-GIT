# T447 — Hidden-sphere shadow and independent-third-cut calibration

**Frozen:** 29 August 2026, before calculation  
**Parent question:** Can a larger geometry that is unavailable directly be recovered from its changing shadow on ordinary ARA cuts?

## Plain-language test address

### Who

One physical identity: the EuRoC `MH_01_easy` micro-aerial vehicle. Its orientation was recorded continuously by external motion capture while it flew.

### What

Hide one coordinate of the vehicle's four-coordinate orientation and try to recover it from the visible coordinates. Compare (1) two independent visible cuts, (2) the same two cuts plus a redundant difference, and (3) three genuinely independent visible cuts.

### When

Preserve the recorded order. The earlier 70% of valid samples is development data; the later 30% is an untouched chronological holdout.

### Where

The complete orientation is a point on the unit 3-sphere `S³` in four-coordinate space. The three visible coordinates form its three-dimensional shadow (`B³`); ordinary two-coordinate ARA planes are slices/projections inside that shadow.

### Why

This is a clean instrument calibration for the current ARA hypothesis. It tests whether an independent third cut contains information that `A`, `B`, and a derived `A−B` cannot contain, and whether time order is needed to choose between the two hidden mirror branches.

### How

Use the published quaternion coordinates `(w,x,y,z)`. Hide `w`; infer its distance from the hidden ridge from the unit-sphere relation, test branch recovery from chronological boundary encounters, and compare with redundant-axis, shuffled-axis, shuffled-time, and two-cut controls.

## Identity and medium boundary

- This is a **new medium** relative to T444–T446: a movement-heavy tracked rigid body rather than a connection-heavy gravitational/lensing system.
- The medium is chosen because its complete four-coordinate orientation is independently known. That lets us hide a coordinate on purpose and score recovery honestly.
- This is a calibration of the measurement architecture. It is **not** evidence that physical time literally equals quaternion `w`, nor that the universe is proved to be an `S³`.

## Source and grain

- Source family: EuRoC MAV dataset, `MH_01_easy`, ground-truth state stream.
- Row grain: one motion-capture state sample.
- Required fields: timestamp and quaternion `(q_RS_w, q_RS_x, q_RS_y, q_RS_z)`.
- Preserve source time; for figures and bounded report data, deterministically downsample without changing order.

## Frozen coordinate map

Let the normalized source quaternion be

\[
q(t)=(w(t),x(t),y(t),z(t)),\qquad
w^2+x^2+y^2+z^2=1.
\]

For ARA display only, map any signed component `u∈[-1,1]` to `u_ARA=1+u`, so zero is the ARA ridge `1`, negative is below the ridge, and positive is above it.

The hidden coordinate is `w`. The visible shadow radius is

\[
r_3(t)=\sqrt{x(t)^2+y(t)^2+z(t)^2}.
\]

The hidden distance from its ridge is predicted by

\[
|\hat w_3(t)|=\sqrt{\max(0,\hat R^2-r_3(t)^2)},
\]

where `R̂` is the median quaternion norm in development data. No holdout `w` value enters this magnitude prediction.

## Frozen comparisons

1. **Three independent cuts:** visible `(x,y,z)` predicts hidden `|w|`.
2. **Two cuts:** visible `(x,y)` leaves the joint hidden budget `z²+w²`; an equal-split point estimate is reported only as a deliberately weak baseline.
3. **Redundant third:** `(x,y,x−y)` has the same matrix rank as `(x,y)` and must not be described as an independent cut.
4. **Shuffled third:** permute `z` within the holdout 200 times. This keeps the same values but breaks their event-by-event relation.
5. **Time-shuffled branch:** preserve visible points but permute their order before applying the frozen branch rule.

## Hidden branch rule

The static shadow gives two candidates, `+|w|` and `−|w|`. A branch crossing is possible only when the shadow reaches its outer boundary (`r₃≈R`, equivalently `|w|≈0`).

- Fit one boundary threshold on development data from the distribution of `r₃/R` at known `w` sign changes.
- Seed the first holdout branch with the first holdout sign only; this is an explicit one-bit starting condition.
- Flip the predicted branch only at a local maximum of `r₃/R` above the frozen threshold.
- Score sign accuracy after the seed and crossing-time error for any holdout crossings.
- If development or holdout contains no usable sign crossing, branch recovery is declared **not identifiable** rather than manufactured.

## Primary measurements

- Holdout mean absolute error (MAE) and 95th-percentile absolute error for hidden `|w|`.
- Improvement of three independent cuts over the two-cut equal-split estimate.
- Improvement over the shuffled-third distribution.
- Rank of the independent and redundant design matrices.
- Number of visible-boundary encounters and hidden-branch crossings.
- Branch sign accuracy and crossing-time error, only if identifiable.

## Recorded-data sensitivity

The normalized calculation is the exact geometry calibration. A second, clearly labelled sensitivity repeats hidden-magnitude recovery on the quaternion values exactly as recorded, using only the development median norm as `R̂`; this shows how much the result degrades under the dataset's actual rounding and measurement precision without adding synthetic noise.

An all-axis scan is descriptive only: after the primary `w` result is frozen, each of `w`, `x`, `y`, and `z` is hidden in turn to show which coordinate views of this same trajectory encounter a projection boundary. It cannot replace the primary `w` verdict or be used to select a favourable hidden axis after the fact.

## Geometry-first outputs

The report must show, with numbered axes and legends:

1. the full quaternion histories through time;
2. ordinary two-axis ARA projections;
3. the three-dimensional visible shadow;
4. visible radius against hidden magnitude;
5. true versus reconstructed hidden magnitude;
6. residuals through time;
7. control error distributions;
8. boundary encounters and branch selection;
9. a framework-address diagram locating the 2D cuts, 3D shadow, hidden coordinate, and parent sphere;
10. the old 36°/Phi direction only as a coordinate-dependent reference, not as a pass condition.

## Frozen interpretation boundary

A successful result establishes that this projection-and-history instrument can recover a deliberately hidden coordinate in a known `S³` identity, and that a genuine third cut adds information that a derived difference does not. It does not establish that cosmic time is quaternion `w`, that all ARA identities are literal hyperspheres, or that the old Phi direction is universal.
