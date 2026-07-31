# Q41B cadence-defined strand reversal — unchanged transfer protocol

Date: 2026-07-27 (Australia/Brisbane)

Test ID: `Q41B-CADENCE-STRAND-REVERSAL-LANDMAX-v1`

Status at authorship: target archive not downloaded or inspected locally

## Why Q41B exists

Q41 prospectively selected the inhomogeneous-v1 `random` ordering archive. All
6,600 closure lineages failed the frozen direction-coherence threshold, so
Q41 had zero eligible cycles. Q41 was recorded as inconclusive without writing
a prediction artifact or revealing any fourth connected identity.

Q41B transfers the **unchanged** Q41 operator to a second untouched archive
whose ordering rule is structured rather than random. No threshold, quadrant,
operator or decision gate is altered.

## Frozen method

This protocol incorporates
`Q41_CADENCE_STRAND_REVERSAL_FIDELITY_v1.md` by reference.

For \(D=C_1-C_2\), preserve the Q40 visible reversal flag and additionally
reverse \(D\) exactly when:

1. \(7.35\leq T_{\rm orbit}\leq7.65\);
2. lag-15 two-coordinate return correlation is at least 0.95; and
3. the target visit is Ba (`q4 = 1`).

Then

\[
\widehat C_4
=
\begin{cases}
C_3-D,&\text{reversal flag true},\\
C_3+D,&\text{otherwise}.
\end{cases}
\]

All Q41 eligibility rules, allowed inputs, cycle extraction, controls, metrics,
seed-cluster bootstrap, minimum counts and support gates remain unchanged.

## Frozen target

- Zenodo DOI: `10.5281/zenodo.16753415`
- Archive: `unnati_submit_12_inhomo_v1_landmax.hdf5.zip`
- Deposited MD5: `f2e191d2f06643818c4ba64743e16238`
- HDF member: `unnati_submit_12_inhomo_v1_landmax.hdf5`
- Branch: `c2_2local connectivity`

Selection used public filename and source metadata only. Although the
repository previously analysed the separate `pure_landmax` archive, this
inhomogeneous-v1 target had not been downloaded or inspected locally when this
protocol was frozen. Results from `pure_landmax` cannot tune Q41B.

## Reveal order

1. verify archive MD5 and schema;
2. build physical-observable caches;
3. run the frozen eligibility inventory;
4. if adequate, write and hash every Q41B/control prediction without reading
   \(C_4\);
5. reveal \(C_4\), score and independently validate;
6. if inadequate, record an inconclusive result without target reveal.

