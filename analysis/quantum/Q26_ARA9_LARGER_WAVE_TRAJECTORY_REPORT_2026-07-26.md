# Q26 ARA^9 larger-wave trajectory

**Date:** 26 July 2026  
**Ledger:** `T282`  
**Primary verdict:** `SUPPORTED — 13/14 SCORED GATES`  
**Independent validation:** `PASS — 282/282 checks`

## Outcome first

Q26 tested Dylan's pre-reveal proposal from Q25:

> the local ARA^9 may be the crest of a larger connection-space wave, and the next ARA^9 may become a trough.

That amplitude statement is supported in this public trajectory:

| Frozen larger-wave result | Outcome |
|---|---:|
| median closure-versus-wait Spearman relation | **`-0.9364`** |
| trajectories ending in the frozen trough (`x_h <= 0.5`) | **`25/28 = 89.3%`** |
| trajectories completing crest-to-trough movement | **`25/28 = 89.3%`** |
| eligible ridge transitions predicted within one sample | **`21/22 = 95.5%`** |
| eligible trough transitions predicted within one sample | **`25/28 = 89.3%`** |
| held-out ARA class accuracy | **`74.1%`** |

The stronger orientation claim is not supported:

| Frozen orientation result | Outcome |
|---|---:|
| reliable stable determinant-orientation reversals | **`1/28 = 3.6%`** |
| ARA relation-plane phase MAE | `1.3819 rad` |
| no-rotation phase MAE | **`1.2388 rad`** |

The clean reading is therefore:

\[
\boxed{
\text{larger ARA}^{9}\text{ amplitude: crest}\rightarrow\text{handover}\rightarrow\text{trough}
}
\]

while the observed orientation mostly remains stable:

\[
\boxed{
\text{amplitude contraction is supported;}
\quad
\text{a full directional flip is not.}
}
\]

This is a staged, partially blind public-data prediction, not proof that every ARA^9 trajectory must behave this
way.

## The ARA object

For every reconstructed two-parent state, the complete connected relation was

\[
C(t)=T(t)-\mathbf a(t)\mathbf b(t)^\mathsf T.
\]

Its rotation-invariant three-direction closure magnitude was

\[
\underbrace{h(t)}_{\substack{\text{ARA}^{9}\text{ closure}\\
\text{connection-space amplitude}}}
=
\left|\det C(t)\right|^{1/3}.
\]

Each trajectory was normalized to its first measured closure:

\[
\underbrace{x_h(t)}_{\substack{\text{local ARA coordinate}\\0\text{ to }2}}
=
2\,\frac{h(t)}{h(t_0)}.
\]

The frozen classes were:

\[
x_h\ge1.5:\text{ crest},
\qquad
0.5<x_h<1.5:\text{ handover},
\qquad
x_h\le0.5:\text{ trough}.
\]

Plainly: each full nine-cut relation begins at its local `2` crest. Q26 asks whether its complete connection
strength then travels through the ARA diameter toward `0`, without treating one missing cell as the whole
problem.

## Source and staged blindness

Q26 used Supplementary Figure 10 from:

- Steinacker et al., *Bell inequality violation in gate-defined quantum dots* (2025);
- Zenodo DOI `10.5281/zenodo.14880901`;
- file `SuppFigure10.csv`;
- source MD5 `9a9e3abac0ee8f80535e17ec72313919`.

The source contains full two-qubit reconstructions for four Bell-family preparations, eleven Hahn-echo wait
times, and eight temperatures from `0.1 K` to `1.1 K`.

The `0.1 K` block was already represented in the earlier quantum arc and was reserved as replication. The seven
temperatures `0.2–1.1 K` supplied the primary set:

- `28` trajectories;
- first `7` matrices exposed (`1–63.09 µs`);
- final `4` matrices sealed (`125.89–1000 µs`);
- `112` hidden complete ARA^9 matrices;
- `1,008` hidden connected cuts.

The exact target matrices, transition locations, orientation behavior, and model comparisons were not opened
until after both the protocol and predictions were hashed.

Protocol SHA-256:

`0bd8f2a0ee96733e0411d477a5c808c4ebd100b083b84b30108d05ed110347e6`

Prediction SHA-256:

`e0e52a552df3b114bc6def1ea392f697d9da301f77d5c71214e7c491355be968`

The broad fact that hotter records decohere more rapidly was published and therefore not blind. The exact
withheld trajectories were.

## Frozen predictor

The early seven matrices supplied the transverse relation-plane cuts

\[
\mathbf q(t)=(C_{XX},C_{XY},C_{YX},C_{YY}).
\]

The predictor:

1. found the two leading relation-plane directions using only the exposed matrices;
2. represented their motion as radius \(r(t)\) and angle \(\theta(t)\);
3. fitted a non-increasing exponential radius;
4. fitted a linear angular path;
5. predicted the four hidden transverse cuts;
6. carried \(C_{ZZ}\) from the median of the final three exposed values;
7. set the four unmodelled cross-plane cuts to zero.

The frozen controls were:

- persistence;
- elementwise linear extrapolation;
- the same contraction with no angular rotation;
- zero relation.

## Held-out prediction

| Model | Cut MAE | Closure MAE | Class accuracy | Phase MAE |
|---|---:|---:|---:|---:|
| ARA radial + angular path | **`0.08502`** | `0.10920` | **`74.1%`** | `1.3819` |
| no-rotation contraction | `0.08632` | **`0.10891`** | **`74.1%`** | **`1.2388`** |
| zero relation | `0.16620` | `0.24294` | `63.4%` | `1.4543` |
| persistence | `0.19341` | `0.36491` | `13.4%` | `1.2388` |
| elementwise linear | `0.52616` | `0.61595` | `17.0%` | `1.4272` |

ARA beat persistence and elementwise linear on every primary trajectory. Cluster bootstrap probability that ARA
had lower cut MAE was `1.0000` against each.

The advantage over no-rotation was only `0.00130` MAE. Its cluster-bootstrap win probability was `0.6344`, and
the angular phase gate failed. Q26 therefore provides strong evidence for radial closure movement but weak
evidence for the fitted rotation.

## Time-order control

The exact wait order mattered. Across `999` within-trajectory time permutations:

\[
\operatorname{MAE}_{\rm observed}=0.08502,
\qquad
\overline{\operatorname{MAE}}_{\rm permuted}=0.19755.
\]

The observed order beat every permutation (`time-order percentile = 1.000`). The crest-to-trough result is
therefore not just a bag of matrices with declining average magnitude.

## Data quality

All `352` source matrices passed the physical reconstruction checks used here:

| Check | Result |
|---|---:|
| maximum trace error | `3.33e-16` |
| maximum Hermiticity residual | `0` |
| minimum eigenvalue | `-1.05e-14` |
| positive-semidefinite fraction at `-1e-10` tolerance | `100%` |

The validator independently reparsed the deposit, rebuilt every connected tensor, replayed the predictor,
controls, bootstrap, permutation test, transitions, gates, and verdict. It passed `282/282` checks.

## What Q26 changes

Q25 showed that a static balanced-sphere completion could not infer an arbitrary hidden ninth cut. Q26 now shows
why the larger-wave alternative was worth separating:

\[
\boxed{
\text{one complete local ARA}^{9}
\text{ can be a time slice on a larger closure wave.}
}
\]

The later complete matrices do not mainly reveal a new spatial orientation. They reveal that the entire
connected relation loses closure strength along the declared trajectory. In Dylan's language, the observed Q24/Q25
ARA^9 object was indeed crest-like relative to the later matrices, and most trajectories reached a trough.

This does **not** establish:

- universal ARA fractality;
- a new quantum-mechanical law;
- an entanglement measure;
- a universal \(2\rightarrow0\) decay rule;
- a demonstrated singularity flip of the full ARA^9 orientation;
- superiority over the nearly tied no-rotation contraction.

## Reproduction

From `analysis/quantum`:

```powershell
python q26_zenodo_download.py --stage development
python q26_ara9_larger_wave_trajectory_test.py prepare
python q26_ara9_larger_wave_trajectory_test.py predict
python q26_zenodo_download.py --stage target
python q26_ara9_larger_wave_trajectory_test.py reveal
python q26_ara9_larger_wave_trajectory_validate.py
```

Primary artifacts:

- `Q26_ARA9_LARGER_WAVE_TRAJECTORY_PROTOCOL_v1_FROZEN.md`
- `Q26_ARA9_LARGER_WAVE_PREDICTIONS.json`
- `Q26_ARA9_LARGER_WAVE_PREDICTIONS.sha256`
- `Q26_ARA9_LARGER_WAVE_PREDICTIONS.csv`
- `Q26_ARA9_LARGER_WAVE_METRICS.csv`
- `Q26_ARA9_LARGER_WAVE_TRAJECTORIES.csv`
- `Q26_ARA9_LARGER_WAVE_PERMUTATION.csv`
- `Q26_ARA9_LARGER_WAVE_RESULTS.json`
- `Q26_ARA9_LARGER_WAVE_VALIDATION.json`
