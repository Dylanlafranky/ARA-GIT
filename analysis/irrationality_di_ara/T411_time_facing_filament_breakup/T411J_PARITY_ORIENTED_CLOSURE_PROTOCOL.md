# T411J — parity-oriented three-rung closure protocol

## Frozen question

Does orienting the direct child across the ARA 1.0 ridge convert the T411H
parent–child–grandchild relation into one transferable, time-facing handover
score?

## Source and grain

Use the saved causal snapshots from `T411H_PREDICTIONS.csv` without rebuilding
or relabelling the source events. The population is the same 123 eligible S1–S4
filament identities. Every identity keeps its frozen child handover horizon and
event-balanced snapshot weights.

## Frozen parity geometries

T411H centered coordinates are

\[
v=x_P-1,\qquad u=x_C-1,\qquad w=x_G-1.
\]

T411I supports the candidate orientation

\[
z=(v,-u,w),
\]

equivalent to

\[
x_C^*=2-x_C.
\]

The candidate is compared with all other distinct rung-parity assignments
relative to the parent:

1. no flip: `(v, u, w)`;
2. child flip: `(v, -u, w)` — frozen ARA candidate;
3. grandchild flip: `(v, u, -w)`;
4. both lower rungs flipped: `(v, -u, -w)`.

No fluid-specific orientation is allowed.

## Coefficient-free Information³ closure

For an oriented triplet `z=(z1,z2,z3)`, define agreement

\[
A(z)=1-\frac{|z_1-z_2|+|z_2-z_3|+|z_3-z_1|}{4}.
\]

The divisor four is the maximum possible pairwise spread for three values on
`[-1,1]`. Define the common ridge coordinate and ridge gate

\[
\bar z=\frac{z_1+z_2+z_3}{3},
\qquad
R(z)=1-|\bar z|.
\]

The frozen handover score is

\[
\boxed{H(z)=A(z)R(z)}.
\]

`H=1` means the three oriented rungs agree at the ridge. Larger `H` is frozen
to mean greater probability of handover within the already defined child
horizon. The sign may not be reversed after scoring.

## Primary evaluation

Use event-weighted AUC because `H` is a coefficient-free ranking score rather
than a calibrated event probability.

The child-flip candidate must:

1. have pooled AUC above 0.5;
2. exceed all three fixed parity controls;
3. have AUC above 0.5 in at least three of four fluids;
4. beat 1,000 within-event circular shifts of only the child path at
   one-sided `p <= 0.05`.

## Secondary evaluation

- report AUC for every parity by fluid;
- report score distributions inside and outside the final child horizon;
- report score shape by lead measured in child-horizon units;
- inspect S1 separately without fitting an S1 correction;
- repeat the score using agreement alone, `A(z)`, to identify whether any gain
  comes from parity or merely from the explicit ridge gate.

## Interpretation boundary

A pass would support a transferable operational closure score for these
measured ARA coordinates. It would not establish that the coordinates are
independent physical waves, and it would not yet yield calibrated event
probabilities or an absolute time-to-handover forecast.

