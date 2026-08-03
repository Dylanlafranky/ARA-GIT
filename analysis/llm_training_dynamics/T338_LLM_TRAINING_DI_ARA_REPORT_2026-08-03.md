# T338 — Pythia training Di-ARA child/parent forecast

**Frozen verdict:** **MIXED/PARTIAL**  
**Validation:** **15/15 independent reconstruction checks passed**  
**Primary scope:** 335 clean public checkpoint files, 9 Pythia sizes, 6,648
model/checkpoint/layer records and 70,752 frozen forecast rows.

## Executive conclusion

The first public LLM training test recovered a real but modest child/parent
forecast relation.

The fixed ARA rule used no fitted coefficients. It combined half of a layer's
recent same-identity movement with half of the whole model's recent
across-layer movement. On the untouched 2.8B, 6.9B and 12B models it:

- reduced joint log-error by **18.12% versus persistence**;
- improved joint log-error by **1.05% versus layer-only flow**;
- achieved **77.69% direction accuracy**, **1.36 percentage points above**
  layer-only flow;
- kept both the massive-activation and background-activation cuts predictive;
- gave a lower point-estimate error than broken layer lineage.

However, ordinary four-point local linear trend was better on the untouched
large models: **0.115799** log-MAE versus **0.118541** for ARA. The difference
was stable across the three held-out model-size units. Therefore the registered
all-gates claim does not pass.

The best reading is not “ARA predicts LLM training better than standard
methods.” It is narrower: **the parent relation adds directional information
to the child layer, but the frozen equal half-and-half amplitude handover is
slightly too coarse for the largest models.**

## What was measured

| ARA language | Conventional measurement |
|---|---|
| Same child identity through time | Same transformer layer across successive training checkpoints |
| Massive stream | Median of the ten sequence-level top-1 activation magnitudes |
| Background stream | Median of the ten sequence-level median activation magnitudes |
| Information³ third relation | `log(top1 / background)` |
| Training rung | `tau = log2(step + 1)` |
| Child flow | Recent log-change per training rung in one layer |
| Parent flow | Recent median log-change per rung across all layers |
| ARA handover forecast | `0.5 * child flow + 0.5 * parent flow` |
| Broken child identity | Use the next layer's history while keeping the target layer and parent fixed |

For each positive successive-checkpoint ratio `s`, the exact reported ARA cut
was

\[
x=\frac{2s}{1+s}
=1+\tanh\!\left(\frac{\log s}{2}\right),
\]

so growth lies above the `1.0` ridge, contraction below it, and reciprocal
inversion maps exactly to `2-x`.

## Frozen splits

- calibration: 14M, 70M, 160M;
- evaluation: 410M, 1B, 1.4B;
- untouched size holdout: 2.8B, 6.9B, 12B.

Every forecast used only earlier checkpoints from the same model. Future-value
perturbation left the corresponding forecast unchanged in validation.

## Primary results

### Joint equal-model log-MAE

| Split | ARA | Persistence | Layer-only flow | Parent-only flow | Local linear trend | Broken lineage |
|---|---:|---:|---:|---:|---:|---:|
| Calibration | 0.102481 | 0.116630 | 0.105700 | 0.102918 | 0.102732 | 0.106379 |
| Evaluation | **0.087203** | 0.131258 | 0.089540 | 0.087413 | 0.088573 | 0.087914 |
| Holdout | 0.118541 | 0.144781 | 0.119794 | 0.119962 | **0.115799** | 0.118927 |

ARA beats either child-only or parent-only flow on evaluation and holdout.
That is the clearest evidence that the cross-scale relation carries something
neither side carries alone. But the advantage is small, and a local OLS trend
describes held-out amplitudes slightly better.

### Direction accuracy

| Split | ARA | Layer-only flow | Local linear trend | Broken lineage |
|---|---:|---:|---:|---:|
| Calibration | 71.36% | 70.10% | **73.40%** | 69.83% |
| Evaluation | **83.41%** | 82.08% | 81.98% | 83.36% |
| Holdout | **77.69%** | 76.32% | 77.30% | 77.59% |

The parent contribution is more useful for **which way the layer moves** than
for its exact next magnitude. This was not used to replace the frozen point
forecast gate.

### Untouched holdout by visible cut

| Stream | ARA MAE | Persistence MAE | Local trend MAE | ARA direction |
|---|---:|---:|---:|---:|
| Massive / top-1 | **0.158195** | 0.207645 | 0.156519 | **80.46%** |
| Background / median | **0.078886** | 0.081917 | 0.075079 | **74.92%** |

Both cuts beat persistence, satisfying the registered survival gate. The
massive stream contains the stronger movement signal. The background stream is
closer to stationary and is where a simple local trend has the clearest edge.

## Registered gates

| Gate | Result |
|---|---|
| G0 integrity and causal-prefix validation | PASS |
| G1 ARA beats persistence in evaluation and holdout | PASS |
| G2 ARA beats local trend in evaluation and holdout | **FAIL — holdout** |
| G3 intact child lineage beats broken lineage | PASS by point estimate |
| G4 both visible cuts beat persistence in holdout | PASS |
| G5 ARA direction beats local-flow direction in holdout | PASS |

The equal-model bootstrap difference versus persistence was positive in both
evaluation (`+0.044055`, 95% interval `[+0.036937,+0.051808]`) and holdout
(`+0.026241`, `[+0.021960,+0.031469]`). Against local trend, evaluation was
uncertain (`+0.001370`, `[-0.001637,+0.004000]`) and holdout favoured local
trend (`-0.002742`, `[-0.004096,-0.000758]`).

The intact-lineage advantage was clear in evaluation (`+0.000712`,
`[+0.000226,+0.001670]`) but small and uncertain across the three holdout
models (`+0.000386`, `[-0.000025,+0.000723]`). It is a positive lead, not a
strong replicated effect.

## Interpretation for ARA

Three parts survived:

1. **The two cuts should not be flattened.** Top-1 and background behave
   differently, yet both retain predictive movement.
2. **The parent is not redundant.** Combining layer and model flow improves
   on either one alone, especially for direction.
3. **Child identity is at least weakly load-bearing.** Breaking layer lineage
   makes the frozen point forecast worse, strongly in evaluation and weakly in
   holdout.

One part did not survive unchanged:

- The pure `0.5 + 0.5` handover is not an adequate exact-amplitude decoder for
  the largest Pythia models. It likely smooths real layer-specific curvature
  that local OLS retains. That diagnosis is post-result and cannot modify
  T338.

This result fits a pattern already seen elsewhere in the project: relational
geometry is often stronger for **direction, transition and confidence** than
for exact point value. Here that pattern appears inside LLM training, but it
still needs a separately frozen capability-handover test.

## Data quality and boundaries

The Pythia checkpoint design is unusually useful because model sizes share the
same training-data order. The raw activation archive is third-party, and its
dataset card contains an unfinished citation placeholder. Accordingly:

- all publisher fits and claimed model laws were excluded;
- only raw arrays were used;
- one malformed 1B step-0 file was excluded by the frozen schema;
- the result should be replicated from original Pythia checkpoints before a
  strong public claim.

The established massive-activation literature describes rare hidden-state
values several orders of magnitude above the median and their abrupt depth
emergence. T338 does not claim to rediscover that mechanism; it tests whether
the training trajectory admits an ARA child/parent forecast.

## Recommended next rung

Freeze a new test whose target is **future relational handover**, not exact
activation magnitude:

1. use only the two already-frozen streams and their third relation;
2. predict the sign or checkpoint of a later change in that relation;
3. keep the 2.8B/6.9B/12B models as a new internal replay split or obtain an
   independent model family;
4. only after freezing predictions, join official zero-shot capability curves
   to ask whether the activation handover precedes a capability change.

That targets the part T338 actually supported without retroactively rescuing
the failed amplitude gate.

## Reproduction

Run:

```powershell
python analysis/llm_training_dynamics/run_t338_llm_training_di_ara.py
python analysis/llm_training_dynamics/validate_t338_llm_training_di_ara.py
```

Set `ARA_PYTHIA_ACTIVATIONS` if the raw archive is not in
`F:/SystemFormulaFolder/external_data/pythia-massive-activations`.

Primary artifacts:

- frozen claim packet and protocol;
- `T338_RAW_REDUCED.csv.gz`;
- `T338_PREDICTIONS.csv.gz`;
- per-model and summary metric CSVs;
- verdict, bootstrap, audit and validation JSON;
- runnable scorer and independent validator.

Sources: [official Pythia model family](https://huggingface.co/EleutherAI/pythia-70m-deduped),
[raw training-activation archive](https://huggingface.co/datasets/Aimpoint-Digital/pythia-massive-activations),
and [Massive Activations in Large Language Models](https://openreview.net/forum?id=F7aAhfitX6).

