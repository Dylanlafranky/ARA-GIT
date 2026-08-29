# T411I — opposite-side rung-parity evaluation

## Assessment: the proposed inversion is present one rung earlier

**S1 and S2 are not distinguished by an opposite-side grandchild.** Across all
four fluids, the direct child is predominantly on the opposite side of the
parent ridge, while the grandchild returns predominantly to the parent's side.

The outcome-free result is therefore

\[
\boxed{P\;\longrightarrow\;-C\;\longrightarrow\;+G}
\]

rather than

\[
P\;\longrightarrow\;+C\;\longrightarrow\;-G.
\]

## Quiet-prefix evidence

The conservative cut excludes the final two child horizons. Values below are
event medians.

| Fluid | Events | Parent–child opposite-side occupancy | Parent–grandchild opposite-side occupancy | Parent–child alignment | Parent–grandchild alignment |
|---|---:|---:|---:|---:|---:|
| S1 | 32 | 0.659 | 0.437 | −0.335 | +0.076 |
| S2 | 61 | 0.824 | 0.321 | −0.550 | +0.293 |
| S3 | 7 | 0.836 | 0.359 | −0.693 | +0.321 |
| S4 | 20 | 0.904 | 0.381 | −0.718 | +0.279 |

The ridge-side count agrees with the cosine orientation. The direct child is
opposite the parent for roughly 66–90% of quiet snapshots, while the
grandchild is opposite for only 32–44%, meaning it is usually back on the
parent side.

## S1/S2 grouping check

The suggested S1/S2 versus S3/S4 split does not reproduce as one stable
identity rule. S1 is less strongly aligned than S3 in the development
partition, but S2 and S4 are indistinguishable in the diagnostic partition.
The parent–grandchild contrast is:

- development: S1 minus S3 median alignment `−0.245`, bootstrap interval
  approximately `[−0.51, −0.06]`;
- diagnostic: S2 minus S4 median alignment `+0.014`, bootstrap interval
  approximately `[−0.13, +0.14]`.

Thus S1 remains the distorted or weakly resolved case; it does not establish a
shared S1/S2 grandchild parity.

## Robustness

- The same rung ordering appears with either a one-child-horizon or
  two-child-horizon quiet guard.
- Orientation is event-balanced, so long records do not dominate the result.
- The handover outcome and its final child window are excluded.
- Position and simple ridge-side occupancy agree.
- Flow alignment is weak and near zero; the result concerns relative ARA side,
  not synchronized instantaneous velocity.

## Consequence for the next lock

A useful parity-corrected ARA lock should orient the direct child before
combination:

\[
u^*=-u
\quad\Longleftrightarrow\quad
x_C^*=2-x_C,
\]

then compare the same-side triplet `(v, u*, w)`. Merely flipping `u` inside an
unconstrained linear model would not be a real test because its fitted
coefficient can absorb the sign. The next test must freeze one shared
geometric closure rule and transfer it across fluids or into a new dataset.

## Claim boundary

T411I supports alternating rung parity in the operational T411H coordinates.
It does not prove that the three coordinates are independently observed
physical waves, and it does not show that S1 and S2 form a distinct
opposite-grandchild family.

