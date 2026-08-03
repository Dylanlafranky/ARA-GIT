# T338 frozen protocol — LLM training Di-ARA forecast

**Frozen:** 3 August 2026, after source/schema/integrity inspection but before
opening model trajectories, forecasts, errors, phase directions or capability
associations  
**Test ID:** `T338-LLM-TRAINING-DI-ARA-v1`  
**Fidelity packet:** `T338_LLM_TRAINING_DI_ARA_CLAIM_PACKET_v1.md`  
**User verdict:** `EXACT ENOUGH TO TEST`

## Question

Can the next massive-activation and background-activation state of a
transformer layer be predicted from the fixed ARA composition of:

1. that layer's recent same-identity flow; and
2. the model parent's recent across-layer flow?

The test is about training-time relational transport. No Phase A/Phase B
ownership is assigned in advance.

## Source and admissibility

Raw source: `Aimpoint-Digital/pythia-massive-activations`, Hugging Face commit
`c4c539ac4f8c8fc9694603895d00c1f1af940a20`, MIT licence.

Only raw `stats/exp2_*_step*` arrays are admissible. Each clean file must parse
to `10 x 4 x L`, where quantities are `top1`, `top2`, `top3`, `median`.
Publisher fits, plots and conclusions are excluded from inputs. The malformed
`pythia_1b_step0` file found during integrity inspection is excluded by schema,
not repaired.

Official EleutherAI zero-shot checkpoint results may be joined only after the
primary activation forecast is scored. They are secondary context and cannot
alter the primary verdict.

## Frozen identities and reduction

For every clean model/checkpoint/layer:

- massive stream `L`: median across the 10 sequences of `top1`;
- background stream `B`: median across the 10 sequences of `median`;
- relation stream `R=L/B`, reported as the Information³ third relation.

No smoothing, Fourier transform, publisher curve, token selection or
cross-layer averaging replaces these child records. The median across layers
is used only to construct the explicit model-parent flow.

## Exact coordinates and prediction

Use the equations in the frozen claim packet. Training time is
`tau=log2(step+1)`. Each positive interval ratio maps exactly to
`x=2s/(1+s)`, with reciprocal inversion `x(1/s)=2-x(s)`.

After at least three completed intervals, forecast the next checkpoint using
the median of the last three rung-normalized flows:

`v_ARA = 0.5*v_child + 0.5*v_parent`.

This is performed independently for `L` and `B`. No coefficient is fitted.

## Frozen model splits

- calibration/descriptive: `14m`, `70m`, `160m`;
- evaluation: `410m`, `1b`, `1.4b`;
- untouched size holdout: `2.8b`, `6.9b`, `12b`.

All eligible chronological one-step forecasts within each model are scored.
The first target needs four earlier checkpoints (three completed flows plus
the current value). Missing source checkpoints are not imputed.

## Baselines and controls

1. **Persistence:** next log value equals current log value.
2. **Local flow:** extrapolate the layer's median last-three flow without the
   parent contribution.
3. **Parent flow:** extrapolate only the model-parent last-three flow.
4. **Ordinary local trend:** least-squares line through the last four
   `(tau, log M)` layer observations, extrapolated one checkpoint.
5. **Broken lineage:** cyclically take `v_child` from the next layer while
   retaining the correct target value and parent flow. Last layer wraps to
   first. This preserves checkpoint/model population while breaking child
   identity.

## Metrics

Primary loss is mean absolute error in natural-log activation, pooled with
equal weight per model and then averaged across `L` and `B`. Also report RMSE,
direction accuracy for non-zero observed log changes, per-stream loss,
per-model loss, and ARA-coordinate error.

For paired comparisons, bootstrap whole models when at least three models are
available and separately bootstrap checkpoints within model for descriptive
intervals. The nine named models, not individual layer rows, are the
cross-architecture units.

## Registered gates

### G0 — integrity

All source commits, file counts, schemas, model splits, causal prefixes and
saved calculations must pass an independent validator. Future-value
perturbation must not change any forecast made from the earlier prefix.

### G1 — basic predictive value

ARA joint MAE must beat persistence in evaluation and holdout separately.

### G2 — added parent information

ARA joint MAE must beat ordinary local trend in evaluation and holdout
separately. This is the main nontrivial gate.

### G3 — child identity is load-bearing

ARA joint MAE must be lower than broken-lineage MAE in evaluation and holdout
separately.

### G4 — both visible cuts survive

ARA must beat persistence for both `top1` and `median` separately in the
untouched holdout.

### G5 — direction

ARA pooled direction accuracy must exceed local-flow direction accuracy in
the untouched holdout. Ties fail.

## Verdict

- **Supported:** G0–G5 all pass.
- **Mixed/partial:** G0 passes and at least G1 plus G3 pass, but one or more of
  G2/G4/G5 fails.
- **Not supported in this form:** G0 fails, or either G1 or G3 fails.

No post-result change may alter this verdict. Any capability association,
emergence-layer interpretation or Phase label requires a later protocol.

