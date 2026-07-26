# Q25 ARA^9 blind missing-cut reconstruction protocol v1 — FROZEN

**Protocol ID:** `Q25-ARA9-MISSING-CUT-v1`  
**Ledger ID:** `T281`  
**Frozen:** 26 July 2026, before downloading or opening any numerical value from the external evaluation source  
**Primary question:** can eight observed cuts of one ARA^9 parent relation predict its hidden ninth cut?  
**Secondary question:** does a declared parent-to-child transition reverse from a quiet/trough ARA^9 into a
connection-heavy crest ARA^9?

## Evidence boundary at freeze

The predictor was selected using the already-open Q24 four-Bell-state records. Those records are calibration only
and cannot provide new confirmation.

The untouched external evaluation source is:

- Welte et al., *A nondestructive Bell-state measurement on two distant atomic qubits*;
- immutable Zenodo record `10.5281/zenodo.4604775`;
- CC BY 4.0;
- a different physical platform and experiment from the Q24 donor-spin Figshare source.

Before this freeze, only the Zenodo metadata, filenames, sizes, checksums, and the paper's qualitative figure
descriptions were read. No matrix cell, fitted value, Stokes coefficient, Pauli expectation, singular value,
determinant, or ARA coordinate from the evaluation files was opened.

## Frozen source partition

### Primary external density-matrix evaluation

Use these five reconstructed two-atom density matrices:

| File | MD5 | Declared role from the source paper |
|---|---|---|
| `Fig3a_dm.csv` | `6d9c796a2fe5a1e28bf421ddf3854794` | fully mixed input |
| `Fig3b_dm_AA.csv` | `fabd72f98052a53cddd230f5f43dcbb7` | conditioned Bell output |
| `Fig3b_dm_AD.csv` | `098362b0cc4ea2a20c952f0f644ed3b2` | conditioned Bell output |
| `Fig3b_dm_DA.csv` | `9b6f161cc046b92e614e7962c47904ff` | conditioned Bell output |
| `Fig3b_dm_DD.csv` | `98b2c5070cee080eb10dc4ab413acb67` | conditioned Bell output |

Each of the nine connected Pauli cuts is hidden once, producing `5 × 9 = 45` primary predictions.

### Secondary cross-object robustness

Use the four reconstructed measurement operators from Figure 4 after Hermitian symmetrization and trace
normalization:

| File | MD5 |
|---|---|
| `figure4_dm_AA.csv` | `a760fd823f7ca7413013e1edaf2a2537` |
| `figure4_dm_AD.csv` | `231ee28c4b140bfd12cdd85239160608` |
| `figure4_dm_DA.csv` | `c37febe660af215d25d5e64a68849619` |
| `figure4_dm_DD.csv` | `77266fe4df3be1c2792cfaa75881772c` |

These `4 × 9 = 36` predictions are reported separately because a normalized measurement operator is not the
same experimental object as a prepared density matrix.

The source information files may be downloaded after freeze for schema interpretation only:
`figure3_info.txt` and `figure4_info.txt`. No outcome-dependent change to the predictor, baselines, gates, or
source partition is permitted.

## Frozen ARA construction

For each normalized two-qubit operator \(\rho\), calculate:

\[
a_i=\operatorname{Tr}\!\left[\rho(\sigma_i\otimes I)\right],
\qquad
b_j=\operatorname{Tr}\!\left[\rho(I\otimes\sigma_j)\right],
\]

\[
T_{ij}=\operatorname{Tr}\!\left[\rho(\sigma_i\otimes\sigma_j)\right],
\qquad
C=T-\mathbf a\mathbf b^\mathsf T,
\qquad
X^{(9)}=1-C.
\]

The nine hidden targets are the connected cells \(C_{ij}\), not the already-normalized ARA coordinates. Report
both using \(X^{(9)}_{ij}=1-C_{ij}\).

## Frozen ARA^9 missing-cut predictor

For one hidden slot \((p,q)\), retain the other eight connected cells and let \(z\) be the candidate value for the
hidden cell. Search the fixed grid

\[
z\in[-1.25,1.25]
\]

at step `0.0005`.

For every completed candidate \(C(z)\), define

\[
\lambda(z)=\frac{\|C(z)\|_F^2}{3},
\]

\[
L_{\rm sphere}(z)=
\left\|C(z)C(z)^\mathsf T-\lambda(z)I\right\|_F^2
+
\left\|C(z)^\mathsf TC(z)-\lambda(z)I\right\|_F^2
+
100\max\!\left(\det C(z),0\right)^2.
\]

The prediction is

\[
\boxed{
\widehat C_{pq}
=
\underset{z}{\operatorname{argmin}}\;L_{\rm sphere}(z)
}.
\]

Plain ARA reading: choose the missing cut that makes the nine-cut relation close as evenly as possible in both
parent directions while retaining the Q24 Bell relation's orientation-reversing closure. The determinant term
does not reward a large negative determinant; it only rejects the opposite orientation when the eight observed
cuts otherwise leave a sign ambiguity.

Ties are resolved by:

1. smaller \(L_{\rm sphere}\);
2. smaller absolute candidate \(|z|\);
3. smaller numeric \(z\).

No state label, declared Bell identity, target file, source fidelity, fitted density matrix, or neighbouring
external entity may enter the predictor.

## Frozen calibration result

The above rule was selected before external values were opened. Leave-one-cell-out calibration on all four Q24
Bell parents returned:

| Q24 layer | ARA MAE | ARA median AE | pole/quiet accuracy |
|---|---:|---:|---:|
| raw linear | `0.0634` | `0.0434` | `35/36` |
| physical companion | `0.0327` | `0.0276` | `36/36` |

On the Q24 physical companion, the frozen baselines returned:

| Baseline | MAE | Median AE | pole/quiet accuracy |
|---|---:|---:|---:|
| physical interval midpoint | `0.1099` | `0.0267` | `31/36` |
| ridge \(C=0\) | `0.3726` | `0.2136` | `12/36` |
| mean of the other eight cells | `0.4202` | `0.2834` | `22/36` |

These values calibrate the procedure; they are not external test results.

## Frozen controls

For every hidden cell calculate:

1. **ridge:** \(\widehat C=0\);
2. **eight-cell mean:** mean of the other eight observed connected cells;
3. **physical midpoint:** hold the fourteen other Pauli coefficients fixed, determine the interval of hidden
   joint coefficients that keeps the reconstructed operator positive semidefinite, and predict the midpoint of
   the feasible connected interval. If no feasible interval exists after the declared source normalization, mark
   that cell unavailable rather than substituting another method.

The physical midpoint is the established-physics companion. It may compete with ARA but may not alter the ARA
prediction.

## Frozen scores

Report separately for the five primary matrices and four secondary operators:

- mean absolute error;
- median absolute error;
- root mean squared error;
- fraction within absolute error `0.10`;
- Pearson correlation between prediction and target;
- pole/quiet classification accuracy, where target magnitude `<=0.10` is quiet and otherwise its sign declares
  the pole direction;
- per-slot and per-entity errors;
- paired ARA-versus-control absolute-error differences with an exact sign-flip permutation test over the
  entity-slot records;
- 95% entity-cluster bootstrap intervals using seed `2026072625` and `10,000` resamples.

## Frozen primary verdict gates

The primary five-density-matrix evaluation is:

- `SUPPORTED` only if all gates pass;
- `NOT SUPPORTED` if the source is valid and any gate fails;
- `INCONCLUSIVE` only for source, checksum, schema, or reconstruction failure.

Gates:

1. `S1`: all five source MD5 values match.
2. `S2`: every parsed matrix is finite, Hermitian to `1e-8`, trace-normalizable, and positive semidefinite to
   minimum eigenvalue `-1e-6`.
3. `S3`: exactly `45` predictions are frozen before target scoring.
4. `S4`: ARA primary MAE is lower than ridge MAE.
5. `S5`: ARA primary MAE is lower than eight-cell-mean MAE.
6. `S6`: ARA primary MAE is lower than physical-midpoint MAE.
7. `S7`: ARA primary median absolute error is lower than or equal to every control median.
8. `S8`: ARA pole/quiet accuracy is higher than every control.
9. `S9`: ARA primary MAE is at most `0.15`.
10. `S10`: ARA-target Pearson correlation is at least `0.75`.
11. `S11`: the entity-cluster bootstrap probability that ARA MAE is below ridge MAE is at least `0.95`.
12. `S12`: the entity-cluster bootstrap probability that ARA MAE is below physical-midpoint MAE is at least
    `0.90`.

## Frozen larger-wave transition probe

This probe is secondary and cannot change the missing-cut verdict.

The source declares `Fig3a_dm.csv` as a fully mixed input and the four Figure 3b matrices as outcome-conditioned
Bell outputs after the measurement sequence. Using complete matrices only after the missing-cut predictions have
been frozen, calculate:

\[
h=|\det C|^{1/3},
\qquad
r_{0.5}=\#\{s_k(C)\ge0.5\}.
\]

The reversible trough-to-crest half of the proposed larger ARA^9 wave is supported in this transition if:

1. the input has \(r_{0.5}=0\) and \(h\le0.20\);
2. every output has \(r_{0.5}\ge2\) and \(h\ge0.40\);
3. mean output \(h\) exceeds input \(h\) by at least `0.35`.

This dataset runs from a mixed input toward conditioned Bell outputs. It can therefore test
`trough -> crest`. It cannot by itself establish Dylan's specifically proposed next-rung
`crest -> trough` direction. That requires a later paired full-tomography dataset beginning with a Bell crest and
following its declared next ARA^9 child or coarse-grained parent.

## Staged reveal

1. Verify the frozen protocol hash.
2. Download and checksum the immutable source files without printing matrix values.
3. Convert each source into local cuts plus nine connected cells.
4. For each slot, write an eight-cell geometry packet and a separate target packet.
5. Run the predictor using geometry packets only.
6. Save and hash the forty-five primary and thirty-six secondary predictions.
7. Only then read the target packet and score the predictions.
8. Independently rebuild every source matrix, prediction, control, score, gate, and transition metric without
   importing the primary runner.

## Interpretation boundary

A primary pass may say:

> ARA^9 three-direction closure predicted hidden connected Pauli cuts on an untouched external atomic-qubit
> source better than the frozen ridge, eight-cell mean, and positivity-midpoint controls.

It may not say:

- ARA replaces quantum tomography;
- eight arbitrary measurements determine every ninth quantum measurement;
- the result is a new law of quantum mechanics;
- the larger crest-to-trough rung flip has been demonstrated;
- entanglement, universal fractality, TE-ARA, phi, or quantum gravity has been proved.

