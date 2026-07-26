# Q25 blind ARA^9 missing-cut reconstruction

**Date:** 26 July 2026  
**Ledger:** `T281`  
**Primary verdict:** `NOT SUPPORTED — 7/12 FROZEN GATES`  
**Independent validation:** `PASS — 490/490 checks`  
**Larger-wave probe:** `NOT SUPPORTED — 2/3 FROZEN GATES`

## Outcome first

Q25 asked whether the other eight cells of an ARA^9 connected relation could predict its hidden ninth cell on a
previously untouched external quantum source.

The frozen ARA sphere-closure rule produced useful signal, but did not beat the strongest established-physics
control:

| Primary external density matrices | MAE | Median AE | Correlation | Pole/quiet accuracy |
|---|---:|---:|---:|---:|
| ARA^9 sphere closure | `0.12394` | `0.10050` | `0.8538` | `86.7%` |
| physical-positivity midpoint | **`0.08687`** | **`0.03506`** | **`0.9093`** | **`91.9%`** |
| ridge \(C=0\) | `0.18616` | `0.04782` | `0.0000` | `57.8%` |
| mean of the other eight cells | `0.21630` | `0.09888` | `-0.0460` | `48.9%` |

ARA beat the ridge and eight-cell mean with entity-cluster bootstrap probabilities of `99.98%` and `99.97%`.
However, the probability that ARA beat the physical midpoint was only `0.50%`. On the `37` records where the
physical interval existed, ARA MAE was `0.11320` versus `0.08687` for the physical midpoint. The failure is
therefore not caused only by unequal eligible sample counts.

This rejects the tested claim that **one locally balanced, negative-orientation ARA^9 sphere closure is sufficient
to reconstruct an arbitrary missing cut in these external prepared states**.

It does not reject Q24's identification of the complete ARA^9 relation object.

## Why this was a genuinely external test

Q24 calibrated the reconstruction rule on a donor-spin Bell-tomography source. Q25 then froze that rule before
downloading or opening values from:

- Welte et al., *A nondestructive Bell-state measurement on two distant atomic qubits*;
- Zenodo DOI `10.5281/zenodo.4604775`;
- a different atomic-qubit platform and experimental protocol.

The frozen protocol hash was:

`d267c807ff60ca84f2475e04fd29b22ed953e3c6b23036aeb022de1dd6c69397`.

All `81` predictions were written and hashed before the sealed targets were read:

`ec06e6ea3075cfd30f945de3142613c7cf40b2b33f258ef5911d8f0d8c7ad390`.

The primary test used five external reconstructed density matrices and hid each of their nine connected Pauli
cuts once, giving `45` predictions. Four normalized Bell-measurement operators supplied a separate `36`-record
secondary robustness set.

## The frozen ARA predictor

For a connected relation tensor

\[
C=T-\mathbf a\mathbf b^\mathsf T,
\]

one cell was replaced by a candidate \(z\). Q25 selected the candidate that made the completed relation as close
as possible to a balanced three-direction sphere in both parent orientations:

\[
L(z)=
\left\|C(z)C(z)^\mathsf T-\lambda I\right\|_F^2
+
\left\|C(z)^\mathsf TC(z)-\lambda I\right\|_F^2
+
100\max(\det C(z),0)^2,
\]

\[
\lambda=\frac{\|C(z)\|_F^2}{3}.
\]

The last term retained the negative determinant orientation observed in all four Q24 Bell parents.

On Q24's already-open physical calibration matrices this rule had MAE `0.0327`, compared with `0.1099` for the
physical midpoint and `0.3726` for the ridge. It therefore earned a proper external test.

## Where it failed

The external generated Bell states were not full balanced Q24-like crests:

| Entity | Singular values | Retained at 0.50 | Closure \(h\) |
|---|---|---:|---:|
| mixed input | `0.0207, 0.0082, 0.0041` | `0` | `0.0089` |
| AA output | `0.7794, 0.4550, 0.3879` | `1` | `0.5162` |
| AD output | `0.8213, 0.5141, 0.4538` | `2` | `0.5765` |
| DA output | `0.7922, 0.5313, 0.3508` | `2` | `0.5286` |
| DD output | `0.8344, 0.4918, 0.3581` | `1` | `0.5277` |

The strongest systematic errors occurred when the predictor tried to complete these uneven partial crests as
though all three directions belonged to one locally balanced sphere. In particular, the hidden `XX` cuts of the
four Bell outputs were under-reconstructed by `0.324–0.402`.

The source paper reports only about `65–69%` Bell fidelity for these generated states. That independently agrees
with the data's attenuated and anisotropic three-direction relation. It does not excuse the failed ARA gate: the
frozen claim was intended to work on the supplied external matrices and did not.

## Data-quality boundary

Four of the five primary matrices were positive semidefinite at the frozen tolerance. `Fig3b-DD` had minimum
eigenvalue `-0.01306`, so frozen source-quality gate `S2` failed. This is a known possible feature of reconstructed
tomography rather than a checksum or parser failure.

The physical-midpoint control was consequently unavailable for eight DD cells. The matched `37`-cell comparison
still favoured the physical midpoint, so the Q25 verdict does not depend on treating those missing control values
as successes.

## Secondary Bell-measurement operators

On the four normalized Figure 4 measurement operators, ARA performed better:

| Secondary operators | MAE | Median AE | Correlation | Pole/quiet accuracy |
|---|---:|---:|---:|---:|
| ARA^9 sphere closure | **`0.07105`** | **`0.05778`** | **`0.9583`** | **`88.9%`** |
| physical midpoint | `0.08716` | `0.07290` | `0.9288` | `86.1%` |
| ridge | `0.19516` | `0.07080` | `0.0000` | `61.1%` |
| eight-cell mean | `0.23332` | `0.14865` | `0.0270` | `50.0%` |

This is a useful secondary result because these operators describe the Bell measurement relation itself. It
cannot rescue the primary verdict because the object class and source partition were frozen separately.

## Larger-wave transition probe

The source supplies a declared temporal/causal ordering:

\[
\text{fully mixed input}
\longrightarrow
\text{four outcome-conditioned Bell outputs}.
\]

The input was an extremely clean ARA^9 trough:

\[
h_{\rm input}=0.0089,\qquad r_{0.5}=0.
\]

The mean output closure was:

\[
\bar h_{\rm output}=0.5372,
\qquad
\bar h_{\rm output}-h_{\rm input}=0.5284.
\]

Thus the closure magnitude changed sharply from trough toward crest. The probe nevertheless failed because the
frozen rule required every output to retain at least two directions at threshold `0.50`; AA and DD retained only
one.

Descriptively, all four outputs had three singular directions at or above approximately `0.35`, but lowering the
threshold after seeing the result would be post-hoc and is not used as confirmation.

The best ARA reading is therefore:

> The data show a strong trough-to-partial-crest transition, not a completed three-direction crest under the
> frozen Q24 scale. The local ARA^9 appears amplitude-shaped by a larger relation coordinate.

The specifically proposed next-rung `crest -> trough` direction remains untested because this source runs in the
opposite direction, from mixed input toward conditioned Bell outputs.

## What Q25 changes

Q24 established that ARA^9 is a faithful name and decomposition for the complete connected Bell relation.

Q25 establishes a new boundary:

\[
\boxed{
\text{knowing the ARA}^9\text{ object}
\not\Rightarrow
\text{eight static cells universally determine the ninth}
}
\]

The missing information appears to include the local ARA^9's position or amplitude on a larger connection-space
wave. A static equal-sphere closure flattened that coordinate.

This makes the next clean test a **full ARA^9 trajectory**, not another retuned static completion:

1. obtain repeated full two-qubit tomography across a declared time, decoherence, or coupling sweep;
2. calculate all nine connected cuts at every step;
3. freeze crest, handover, trough, and orientation-flip criteria from early steps;
4. predict later complete ARA^9 matrices before opening them;
5. test whether a crest becomes a trough at the next declared rung or whether the wave reverses only in closure
   magnitude.

## Reproduction

From `analysis/quantum`:

```powershell
python q25_zenodo_download.py
python q25_ara9_blind_missing_cut_test.py prepare
python q25_ara9_blind_missing_cut_test.py predict
python q25_ara9_blind_missing_cut_test.py reveal
python q25_ara9_blind_missing_cut_validate.py
```

Primary artifacts:

- `Q25_ARA9_BLIND_MISSING_CUT_PROTOCOL_v1_FROZEN.md`
- `Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.json`
- `Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.sha256`
- `Q25_ARA9_BLIND_MISSING_CUT_PREDICTIONS.csv`
- `Q25_ARA9_BLIND_MISSING_CUT_METRICS.csv`
- `Q25_ARA9_BLIND_MISSING_CUT_RESULTS.json`
- `Q25_ARA9_BLIND_MISSING_CUT_GEOMETRY.svg`
- `Q25_ARA9_BLIND_MISSING_CUT_GEOMETRY.png`
- `Q25_ARA9_BLIND_MISSING_CUT_VALIDATION.json`

