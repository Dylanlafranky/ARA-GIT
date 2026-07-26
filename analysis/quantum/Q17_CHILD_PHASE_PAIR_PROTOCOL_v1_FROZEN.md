# Q17 frozen protocol v1 - strongest child Phase A/B pairing

**Registered:** 25 July 2026  
**Claim:** `Q17-CHILD-PAIR-v1`  
**Status:** frozen before Q17 pair calculation  
**Class:** corrected exploratory follow-up on the Q16 raw ARA records

## Source

- input: `Q16_ARA2_RAW_FOUR_CHILD_RECORDS.csv`;
- input SHA-256: `0f7e58b349e5bf3cdda0110a99627134c7a76c69bb0443be8ba1576c4f01e48b`;
- source protocol SHA-256: `63a099cf2ab200459d09240862a5e0239dfb241f45126c6474921adbb19fe51e`;
- four children, 45 raw ARA cuts, 40 development and 40 holdout records per child.

Only `child`, `split`, `record_index`, `cut`, and `ara_x` enter the primary Q17 geometry.

## Candidate architectures

\[
\mathcal P_1=(C00,C01)+(C10,C11),
\]

\[
\mathcal P_2=(C00,C10)+(C01,C11),
\]

\[
\mathcal P_3=(C00,C11)+(C01,C10).
\]

No architecture is privileged before calculation.

## Split geometry

For split \(S\), calculate each child centroid \(\mu_i^S\in\mathbb R^{45}\), common centre
\(M^S=\frac14\sum_i\mu_i^S\), radial vector \(r_i^S=\mu_i^S-M^S\), and common radius

\[
R^S=\sqrt{\frac14\sum_i\lVert r_i^S\rVert^2}.
\]

For candidate pair \((i,j)\):

\[
A_{ij}^S=-\cos(r_i^S,r_j^S),
\qquad
B_{ij}^S=
\frac{2\min(\lVert r_i^S\rVert,\lVert r_j^S\rVert)}
{\lVert r_i^S\rVert+\lVert r_j^S\rVert},
\]

\[
E_{ij}^S=
\frac{\left\lVert(\mu_i^S+\mu_j^S)/2-M^S\right\rVert}{R^S}.
\]

For a complete architecture \(\mathcal P\):

\[
Q_{\mathcal P}^S
=
\frac{1}{1+\max E_{ij}^S}
\cdot
\min\left(\frac{A_{ij}^S+1}{2}\right)
\cdot
\min B_{ij}^S.
\]

`Q` is a frozen bounded ranking score. It rewards ridge closure, antipodal orientation and radial balance while
letting the weaker constituent pair control the complete architecture.

The development architecture with greatest `Q` is selected. Exact ties are broken lexically by the written
architecture order. Holdout cannot change the selected architecture.

## Frozen pair diameter and holdout discrimination

For selected development pair \((i,j)\):

\[
d_{ij}^{dev}=(\mu_i^{dev}-\mu_j^{dev})/2,
\qquad
\hat d_{ij}^{dev}=d_{ij}^{dev}/\lVert d_{ij}^{dev}\rVert.
\]

The frozen threshold is the projected development pair midpoint. Holdout records are classified to the nearer
pole on this one diameter. Save balanced accuracy and the standardized held-out separation

\[
d'_{ij}
=
\frac{|\bar z_i-\bar z_j|}
{\sqrt{(s_i^2+s_j^2)/2}}.
\]

Diameter persistence is

\[
P_{ij}=
\left|\cos(d_{ij}^{dev},d_{ij}^{hold})\right|.
\]

## Frozen gates

The direct-child Phase A/B architecture is `SUPPORTED` only if all gates pass:

1. the development-selected architecture is also the highest-`Q` architecture in holdout;
2. selected holdout `Q >= 0.70`;
3. both selected holdout pair oppositions are `>= 0.80`;
4. both selected holdout radial balances are `>= 0.80`;
5. both pair diameter persistences are `>= 0.80`;
6. both frozen-diameter holdout balanced accuracies are `>= 0.80`;
7. selected holdout `Q` is at least `10%` larger than the holdout runner-up;
8. the complete-gate rate is `<= 0.01` in `9,999` independent balanced-label shuffles and `<= 0.05` in `1,000`
   within-one-archive pseudo-child controls.

If gates 1-7 fail, the verdict is `NOT SUPPORTED` for direct child-to-child Phase A/B pairing in this
representation. This does not negate the Q16 two-parent/four-child architecture; it may instead mean the parent
poles are groups or relation directions rather than individual children.

## Controls

### Balanced-label shuffle

Within development and holdout separately, pool the 160 record vectors and independently permute them into four
balanced labels of 40 records. Run the complete selection and scoring pipeline. Record whether gates 1-7 pass.

### Within-one-archive pseudo-children

For each iteration, select one real child archive. Independently partition its 40 development and 40 holdout
records into four pseudo-children of 10 records each. Run the complete pipeline. Record whether gates 1-7 pass.

## Secondary analyses

- report all six pair metrics and all three architecture scores;
- leave each of `K0...K8` out in turn and repeat the frozen architecture comparison;
- report whether the same architecture wins without dominant relation setting `K8`;
- movement or lead-lag measures are descriptive only because record indices are not verified synchronized time.

## Conventional comparison quarantine

Established preparation names and expected Bell-state relations may be restored only after the Q17 ARA result
JSON is written. They cannot alter the verdict.

## Determinism and outputs

- seed: `20260725`;
- `9,999` balanced-label shuffles;
- `1,000` pseudo-child controls;
- save pair metrics, architecture metrics, leave-setting-out results, controls, verdict and exact source hashes;
- an independent validator must recompute all central deterministic metrics without importing the primary test
  implementation.
