# T344 BAW weir numerical replication addendum v1 (frozen)

**Frozen:** 6 August 2026, after schema-only inspection of the numerical workbooks and
before calculating any numerical ARA coordinate, sector, model score or closure class.

This is Gate E of
`T344_BAW_WEIR_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md`. It repeats Gates A-D
without retuning their definitions, estimators, thresholds or pass criteria. Numerical
trajectories are a representation-level replication and are never pooled with laboratory
tracks as extra observations.

## Source and integrity

Official source: DOI `10.48437/99f329-73aee6`.

| condition | workbook | official SHA-256 |
|---|---|---|
| low | `Spheres_num_low.xlsx` | `6b4b30f532cfca965da92d73f92c100ed429cd5a2078a7c7dfc18d1eaf7bdfdd` |
| medium | `Spheres_num_medium.xlsx` | `feb38f39468a64df5ef50d292b8edbe716f9a4bdd1d76782147d11c0b43a6632` |
| high | `Spheres_num_high.xlsx` | `4a3e737bfdb66ad913d08fe182d563e573648820e105da73726b88af6eb07eab` |

Each workbook has 2,000 particle columns on sheets `x` and `y`, 2,200 native time rows,
and `0.01 s` cadence. Time zero is the particle's crossing of the weir crest.

## Physical-coordinate mapping

The laboratory sheet's image `y` increases downward, so its frozen physical vertical
coordinate was `z=-y_image`. The numerical sheet is already physical height in metres,
zeroed at the flume bottom, and increases upward. Therefore the replication uses

\[
p_t=(x_t,z_t)=(x_{\rm num,t},y_{\rm num,t}).
\]

This is not a result-dependent flip. It is required to express both representations in
the same declared downstream/right and physical-up orientation. All quotient, ARA,
sector, causal-broken-pair, leave-one-condition-out, window, bootstrap and landmark
rules remain those frozen for the laboratory test.

## Replication interpretation

- Agreement of effect direction across low, medium and high is supportive.
- Disagreement is a laboratory/model boundary and is not averaged away.
- Because laboratory Gate D failed, numerical Gate D cannot rescue it. It can only show
  whether the same failure direction is reproduced or representation-specific.

