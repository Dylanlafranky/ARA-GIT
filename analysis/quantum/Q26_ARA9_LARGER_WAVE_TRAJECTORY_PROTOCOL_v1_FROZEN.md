# Frozen protocol - Q26 ARA^9 larger-wave trajectory

**Protocol ID:** `Q26-ARA9-LARGER-WAVE-v1`  
**Ledger ID:** `T282`  
**Frozen:** 26 July 2026, before downloading or opening `SuppFigure10.csv`  
**Test class:** public-data, staged partially blind trajectory prediction  
**Source:** Steinacker et al. (2025), *Bell inequality violation in gate-defined quantum dots*,
Nature Communications 16, 3606; data DOI `10.5281/zenodo.14880901`

## Question

Q25 showed that a static equal-sphere rule could not universally reconstruct a missing ARA^9 cut. Dylan proposed
before the Q25 reveal that the measured ARA^9 may instead be a crest of a larger connection-space wave and may
become a trough in the next ARA^9.

Q26 asks:

1. can the first seven complete connected ARA^9 matrices predict the final four matrices of a trajectory;
2. does the full relation move from a connection crest toward the opposite trough;
3. is that change an amplitude flip on the `0-2` ARA diameter, a stable orientation reversal, or both?

## Source partitions and blindness

The source deposit and supplementary captions were inspected for filenames, checksums, temperature order, state
order and wait coordinates. The numerical target file was not downloaded before this protocol was frozen.

Already-open development sources:

- Q7 `SuppFigure5a.csv` and `SuppFigure5b.csv`, the `0.1 K` Ramsey and Hahn trajectories;
- `SuppFigure9.csv`, the deposited `0.1 K` Ramsey individual-projection trajectories;
- `SuppFigure3a.csv`, `SuppFigure3b.csv`, and `SuppFigure3c.csv`, the initial Bell-state density matrices at
  `0.1`, `0.2`, and `0.3 K`.

Sealed target source:

- `SuppFigure10.csv`;
- expected MD5 `9a9e3abac0ee8f80535e17ec72313919`;
- caption-defined temperature order
  `0.1, 0.2, 0.3, 0.5, 0.7, 0.85, 1.0, 1.1 K`;
- state order `Phi-plus, Phi-minus, Psi-plus, Psi-minus`;
- Hahn wait coordinates
  `1.00, 1.99, 3.98, 7.94, 15.85, 31.62, 63.09, 125.89, 251.19, 501.18, 1000.00 us`.

The `0.1 K` block is a schema/replication block because its physical content was already opened in Q7. The
primary target contains the other seven temperatures: `28` trajectories and `112` hidden complete ARA^9
matrices.

The paper had already disclosed the coarse result that coherence times shorten with temperature. Therefore
Q26 is not blind to the broad decay direction. The exact nine-cut trajectories, transition locations,
orientation behaviour and forecast errors remain unopened.

## Schema rule

Each source row is a sixteen-coefficient Pauli expansion in this fixed order:

```text
II, IX, IY, IZ, XI, XX, XY, XZ, YI, YX, YY, YZ, ZI, ZX, ZY, ZZ
```

The deposited values are density-expansion coefficients \(c_{ij}\), with \(c_{II}=0.25\). The normalized
expectations are

\[
\langle ij\rangle=4c_{ij}.
\]

If the target is deposited as consecutive numeric rows, the parser must find exactly `352` nonblank rows and
partition them temperature-major, state-minor, eleven waits per trajectory. Blank rows may occur only between
trajectories or temperatures. A schema-only adaptation is allowed if the same `8 x 4 x 11 x 16` values are
encoded as stringified lists; the scientific rule and partitions may not change.

## ARA^9 object

For each density expansion, calculate the two local parent cuts

\[
a_i=\langle \sigma_i\otimes I\rangle,\qquad
b_j=\langle I\otimes\sigma_j\rangle
\]

and the full parent relation

\[
T_{ij}=\langle \sigma_i\otimes\sigma_j\rangle,
\qquad i,j\in\{X,Y,Z\}.
\]

The connected ARA^9 is

\[
C=T-\mathbf a\mathbf b^\mathsf T.
\]

The complete connection-space closure is

\[
h(C)=|\det C|^{1/3}.
\]

For each trajectory, map closure onto its local ARA diameter using its first observed closure:

\[
x_h(t)=2\,\frac{h(C_t)}{h(C_0)}.
\]

This is a local relation coordinate, not a universal physical unit.

Frozen state classes:

- crest: \(x_h\ge1.5\);
- handover/gradient: \(0.5<x_h<1.5\);
- trough: \(x_h\le0.5\);
- ridge crossing: first sampled \(x_h\le1.0\).

## Development/target split

Within every target temperature and Bell identity:

- exposed geometry: wait indices `0-6`, through `63.09 us`;
- sealed target: wait indices `7-10`, from `125.89` through `1000 us`.

The prepare stage must write the exposed and sealed packets separately without displaying target values. The
prediction stage may read only the exposed packet. Predictions must be written and SHA-256 hashed before the
reveal stage reads the sealed packet.

## Frozen ARA trajectory predictor

For the seven exposed matrices \(C_k\), define the transverse Phase-A/Phase-B relation-plane vector

\[
\mathbf q_k=
(C_{XX},C_{XY},C_{YX},C_{YY})_k.
\]

Stack the seven vectors into \(Q\in\mathbb R^{7\times4}\). Take the first two right-singular vectors of the
uncentred \(Q\) as a two-dimensional relation plane. Fix each basis-vector sign by making its largest-magnitude
loading positive. Project:

\[
\mathbf z_k=Q_kV_2^\mathsf T,\qquad
r_k=\|\mathbf z_k\|_2,\qquad
\theta_k=\operatorname{unwrap}\!\left(\operatorname{atan2}(z_{k,2},z_{k,1})\right).
\]

Fit by ordinary least squares on the actual microsecond wait coordinate:

\[
\log r(t)=\alpha+\beta t,\qquad \beta\leftarrow\min(\beta,0),
\]

\[
\theta(t)=\theta_0+\omega t.
\]

At each hidden wait, predict

\[
\widehat{\mathbf z}(t)=
e^{\alpha+\beta t}
\begin{bmatrix}
\cos(\theta_0+\omega t)\\
\sin(\theta_0+\omega t)
\end{bmatrix},
\qquad
\widehat{\mathbf q}(t)=\widehat{\mathbf z}(t)V_2.
\]

This supplies `XX, XY, YX, YY`. Predict the connection-heavy cut as

\[
\widehat C_{ZZ}=\operatorname{median}
(C_{ZZ,4},C_{ZZ,5},C_{ZZ,6}).
\]

The four off-plane cuts `XZ, YZ, ZX, ZY` are predicted as zero. Together these are the nine cells of the
predicted complete ARA^9 matrix.

## Controls

1. **Persistence:** every hidden matrix equals the last exposed \(C_6\).
2. **Elementwise linear:** independently fit each of nine cuts against wait time on indices `0-6`, extrapolate,
   and clip to `[-1,1]`.
3. **No-rotation contraction:** use the ARA predictor's fitted \(r(t)\), but keep the transverse direction fixed
   at \(\mathbf q_6/\|\mathbf q_6\|\). Use the same `ZZ` and off-plane rules as ARA.
4. **Zero/trough:** predict all nine cuts as zero; diagnostic only.

The no-rotation control isolates whether the ordered two-phase path adds information beyond radial contraction.

## Primary metrics

- MAE and RMSE across all nine hidden cuts;
- trajectory-level matrix MAE;
- MAE of \(h(C)\);
- transverse relation-plane angular error;
- crest/handover/trough classification accuracy;
- ridge-crossing and trough-entry sample error;
- Spearman correlation of observed \(h\) with wait;
- fraction of trajectories completing crest-to-trough amplitude movement;
- determinant sign while \(x_h>0.5\);
- entity-cluster bootstrap comparison, clustered by temperature and Bell identity;
- `999` deterministic time-order permutations, seed `26026`.

## Frozen gates

Data and staging:

1. `D1`: target MD5 matches the registered checksum.
2. `D2`: parser returns exactly `8 x 4 x 11 x 16` finite source coefficients.
3. `D3`: every \(c_{II}\) equals `0.25` within `1e-12`.
4. `D4`: all `112` primary predictions are written and hashed before reveal.

Prediction:

5. `P1`: ARA cut MAE is lower than persistence MAE.
6. `P2`: ARA cut MAE is lower than elementwise-linear MAE.
7. `P3`: ARA cut MAE is lower than no-rotation-contraction MAE.
8. `P4`: ARA beats persistence on trajectory MAE in at least `70%` of the `28` primary trajectories.
9. `P5`: ARA closure-\(h\) MAE is lower than persistence.
10. `P6`: ARA transverse angular error is lower than no-rotation contraction.
11. `P7`: ARA crest/handover/trough accuracy is at least `70%`.
12. `P8`: among trajectories with an observed ridge crossing, at least `60%` are predicted within one sampled
    wait.
13. `P9`: among trajectories with an observed trough entry, at least `60%` are predicted within one sampled
    wait.

Larger-wave structure:

14. `W1`: median within-trajectory Spearman correlation between closure \(h\) and wait is at most `-0.70`.
15. `W2`: at least `75%` of trajectories finish in the frozen trough class.
16. `W3`: at least `75%` complete the crest-to-trough amplitude movement from \(x_h(0)=2\) to
    \(x_h(10)\le0.5\).
17. `W4`: exact ARA time order beats at least `95%` of the `999` within-trajectory development-order
    permutations on cut MAE.
18. `W5`: entity-cluster bootstrap probability that ARA has lower cut MAE is at least `95%` separately against
    persistence and elementwise linear.

## Verdict rule

`SUPPORTED` requires:

- all `D1-D4`;
- all core predictive gates `P1-P3`;
- all larger-wave gates `W1-W3`;
- at least `11/14` gates among `P1-P9` and `W1-W5`.

`PARTIALLY SUPPORTED` requires all `D1-D4`, all `W1-W3`, and at least two of `P1-P3`.

Otherwise the verdict is `NOT SUPPORTED`.

The numerical `0.1 K` target block is reported only as a replication and cannot improve the primary verdict.

## Orientation interpretation frozen before reveal

Amplitude and orientation are distinct:

- **amplitude flip:** crest \(x_h\approx2\) becomes trough \(x_h\approx0\);
- **stable orientation flip:** \(\operatorname{sign}(\det C)\) reverses for at least two consecutive samples while
  \(x_h>0.5\) on both sides;
- sign changes confined to \(x_h\le0.5\) are singularity-floor/quiet-region observations and do not establish a
  stable orientation flip.

Q26 does not require an orientation reversal for the larger-wave hypothesis to pass. It reports which of these
three outcomes occurred.

## Evidence boundary

This test predicts complete **connected ARA^9 matrices**, not complete density matrices or individual quantum
shots. The target is a second condition and seven new temperature groups from the same device and deposit, not
an independent laboratory. Coarse faster high-temperature decoherence was already published. Exact target
values, ARA transition positions and relative model performance are the partially blind contribution.

