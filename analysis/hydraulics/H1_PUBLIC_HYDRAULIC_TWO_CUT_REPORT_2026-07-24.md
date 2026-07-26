# H1 Public Hydraulic Two-Cut ARA Test

**Test ID:** T260-H1  
**Date:** 24 July 2026  
**Frozen verdict:** **SUPPORTED — 8/8 gates passed**  
**Independent validation:** **PASS — 26/26 checks**

## Technical summary

The predeclared connection-rich prediction was supported on the public UCI hydraulic test-rig data. A two-pressure-cut account reached `0.877304` balanced accuracy, compared with `0.711848` for the best training-selected single pressure cut. The gain was `+0.165456`, or **+16.55 percentage points**, with a paired 95% bootstrap interval of **+12.39 to +21.04 points**. The two-cut model won all five whole-group outer folds, and the worst accumulator-class recall was `0.729549`.

The most informative structural control destroyed synchronization by shifting the second sensor's twelve within-cycle bins. Balanced accuracy then collapsed to `0.266827`, close to the four-class chance level of `0.25`. This shows that the retained information was in the synchronized relation between two spatial pressure cuts, not merely in having two sensor columns.

The result supports the bounded claim that two real cuts through this distributed, connection/storage-heavy system retain held-out state information that the best single cut discards. It does **not** show that ARA is a superior classifier: independently standardized raw features produced exactly the same LDA predictions, and a standard random forest on the selected sensor pair reached `0.955753`.

## Primary result

| Measure | Frozen result |
|---|---:|
| Two-cut balanced accuracy | `0.877304` |
| Best one-cut balanced accuracy | `0.711848` |
| Two-cut gain | `+0.165456` |
| Paired 95% gain interval | `[+0.123947, +0.210383]` |
| Worst class recall | `0.729549` |
| Outer-fold wins | `5/5` |
| Frozen gates | `8/8` |

Nested training-only selection chose `PS3` as the single cut and `PS1+PS3` as the pair in every outer fold. That stability was not required by the gates, but it reduces concern that the result arose from unstable sensor fishing.

### Outer-fold results

| Fold | One cut | Two cuts | Gain | Shifted second cut | Random forest |
|---:|---:|---:|---:|---:|---:|
| 0 | `0.693258` | `0.850455` | `+0.157197` | `0.274621` | `0.973788` |
| 1 | `0.733081` | `0.938889` | `+0.205808` | `0.252778` | `0.977778` |
| 2 | `0.715644` | `0.878120` | `+0.162476` | `0.264025` | `0.972131` |
| 3 | `0.667309` | `0.843331` | `+0.176022` | `0.265625` | `0.885889` |
| 4 | `0.763895` | `0.893929` | `+0.130034` | `0.260483` | `0.984453` |

### Class recalls

| Accumulator state | Recall |
|---:|---:|
| `90 bar` | `0.982673` |
| `100 bar` | `0.879699` |
| `115 bar` | `0.917293` |
| `130 bar` | `0.729549` |

## What one cut and two cuts meant

One identity was one complete 60-second hydraulic cycle. One pressure sensor was treated as one spatial cut through that completed cycle; a pair of synchronized pressure sensors was treated as two cuts through the same cycle identity.

Each sensor trace was divided into twelve fixed five-second windows. The mean and population standard deviation in each window produced 24 features per cut. The test used no Fourier transform, wavelet, PCA, NMF or learned embedding. The ARA representation was a training-only affine calibration of each feature:

\[
\underbrace{x}_{\substack{\text{ARA reading}\\\text{for this cut feature}}}
=
1+
\underbrace{o}_{\substack{\text{frozen pole}\\\text{orientation}}}
\frac{
\underbrace{f-m}_{\substack{\text{feature distance}\\\text{from training centre}}}
}{
\underbrace{s}_{\substack{\text{training-only}\\\text{robust scale}}}
}.
\]

Values were not clipped to `0–2`; overshoot remained visible. Because this mapping is invertible and affine, the exact tie with independently standardized raw LDA is an expected coordinate equivalence rather than an ARA-specific algorithmic advantage.

## Frozen design

- Source: UCI *Condition monitoring of hydraulic systems*, DOI `10.24432/C5CW21`, CC BY 4.0.
- Population: all `2,205` documented 60-second experimental cycles.
- Target: four hydraulic-accumulator pressure states: `130`, `115`, `100` and `90 bar`.
- Inputs: synchronized `PS1`–`PS6` pressure traces sampled at `100 Hz`.
- Holdout unit: contiguous 15-cycle groups; whole groups remained together.
- Outer evaluation: five `StratifiedGroupKFold` splits.
- Inner selection: four grouped folds selected one of six sensors and one of fifteen distinct sensor pairs using training data only.
- Classifier: shrinkage LDA (`lsqr`, automatic shrinkage).
- Uncertainty: paired bootstrap over held-out predictions.
- Verdict rule: all eight frozen gates had to pass.

The numerical archive was not opened until the fidelity packet, frozen protocol, hashes and ledger entry existed.

## Controls and robustness

| Control | Result | Interpretation |
|---|---:|---|
| Same-information raw LDA | `0.877304` | Exact ARA/raw coordinate tie |
| Raw/ARA disagreements | `0` | Same decision boundary under affine change |
| Pole-reversal disagreements | `0` | Declared pole naming did not change predictions |
| 500 label permutations, mean | `0.260568` | Near four-class chance |
| 500 label permutations, 95th percentile | `0.310884` | Below frozen `0.35` bound |
| Shifted second cut | `0.266827` | Synchronized cross-cut relation was necessary |
| Random forest, same selected pair | `0.955753` | Standard nonlinear model extracted more information |

Independent validation reconstructed the sample accounting, group isolation, nested selections, predictions, fold metrics, paired interval, control results, gate logic and final verdict. It passed `26/26` checks.

## What this does and does not support

### Supported here

- A second real spatial pressure cut retained substantial held-out accumulator-state information absent from the best single cut.
- The useful information depended on synchronized within-cycle relation.
- The ARA coordinates were a faithful reversible representation of the same information used by standard LDA.
- The exact result generalized across all five complete-group holdouts without changing the method.

### Not established

- ARA is not the best predictive algorithm on this dataset; the random forest scored higher.
- The result does not prove a universal Connection/Space law, universal fractality, TE-ARA ontology, phi, new hydraulic physics or quantum–classical unification.
- The contrast with the negative Q2 quantum I/Q result is currently a two-dataset pattern, not a universal theorem that two cuts help every connection-heavy system and fail every information-heavy one.
- The post-hoc subgroup patterns are descriptive and cannot alter the frozen verdict.

## Post-hoc clue for a later frozen test

The pair gain was `+0.200762` on cycles labelled stable and `+0.025257` on cycles labelled unstable. This is compatible with the idea that synchronized multi-cut structure is easier to recover when the coupled identity has settled, but the split was examined after the result and is not confirmatory. A dedicated stable-versus-unstable interaction test must be frozen before reuse.

## Recommended next test

Replicate the same instrument on a second public connection-rich system before adding new ARA machinery. A bridge-strain network, battery pack, structural vibration array or fluid-storage system with synchronized spatial sensors would be suitable. Freeze both:

1. the overall two-cut gain; and
2. an interaction asking whether the gain is larger in settled than transition-heavy states.

This would test whether H1 is a repeatable measurement principle rather than a hydraulic-dataset peculiarity.

## Reproduction

Run from `analysis/hydraulics`:

```powershell
python -m pip install -r h1_public_hydraulic_requirements.txt
python h1_public_hydraulic_two_cut_test.py --download
python h1_public_hydraulic_two_cut_validate.py
```

The runner verifies archive SHA-256
`24128aad2ee45eea7e6b63ebbd9992cdf25d0483a2cebefbfc13bc69079af1f2`
before analysis. The exact fidelity and protocol hashes are independently rechecked by the validator.

## Evidence files

- `H1_PUBLIC_HYDRAULIC_TWO_CUT_FIDELITY_v1.md`
- `H1_PUBLIC_HYDRAULIC_TWO_CUT_PROTOCOL_v1_FROZEN.md`
- `h1_public_hydraulic_two_cut_test.py`
- `h1_public_hydraulic_two_cut_validate.py`
- `H1_PUBLIC_HYDRAULIC_FOLDS.csv`
- `H1_PUBLIC_HYDRAULIC_PREDICTIONS.csv`
- `H1_PUBLIC_HYDRAULIC_PERMUTATIONS.csv`
- `H1_PUBLIC_HYDRAULIC_RESULTS.json`
- `H1_PUBLIC_HYDRAULIC_VALIDATION.json`

