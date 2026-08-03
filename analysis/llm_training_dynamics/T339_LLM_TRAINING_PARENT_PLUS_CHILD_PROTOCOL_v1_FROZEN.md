# T339 frozen protocol — corrected LLM parent-plus-child forecast

**Frozen:** 4 August 2026, after T338 results and the user's translation
correction were known, but before the corrected `1 parent + 0.5 child`
forecast was calculated or scored  
**Test ID:** `T339-LLM-PARENT-PLUS-CHILD-v1`  
**Fidelity packet:** `T339_LLM_TRAINING_PARENT_PLUS_CHILD_CLAIM_PACKET_v1.md`  
**User correction:** `0.5 child + 1 parent`

## Question

Does the exact cross-rung composition

`v_ARA = 1.0*v_parent + 0.5*v_child`

predict the next positive activation state of a transformer layer better than
the mistaken T338 equal average and the frozen non-ARA baselines?

## Source, admissibility and reduction

Reuse the source and reduction frozen in T338 without alteration:

- raw source: `Aimpoint-Digital/pythia-massive-activations`, Hugging Face
  commit `c4c539ac4f8c8fc9694603895d00c1f1af940a20`;
- only raw `stats/exp2_*_step*` arrays;
- every admitted file parses to `10 x 4 x L`;
- malformed `pythia_1b_step0` is excluded by schema;
- massive stream `L`: median across ten sequences of `top1`;
- background stream `B`: median across ten sequences of `median`;
- relation `R=L/B` is retained for audit but does not tune the forecast;
- publisher fits, conclusions and capability labels remain excluded.

No smoothing, Fourier transform, fitted coefficient, token selection or
future observation enters a forecast.

## Exact coordinates and corrected prediction

Use `tau=log2(step+1)`, successive-checkpoint ratio `s=M_t/M_(t-1)`, exact
ARA coordinate `x=2s/(1+s)`, and rung-normalized log flow as defined in the
claim packet.

After at least three completed intervals, take the median of the last three
flows and freeze:

`v_ARA_corrected = 1.0*v_parent + 0.5*v_child`.

Apply this independently to `top1` and `median`. No division by `1.5` and no
coefficient fitting are allowed.

## Frozen model splits

- calibration/descriptive: `14m`, `70m`, `160m`;
- evaluation: `410m`, `1b`, `1.4b`;
- untouched-by-T339 size holdout: `2.8b`, `6.9b`, `12b`.

The holdout was already opened by T338, so it is a formula-correction holdout,
not a pristine archive holdout. All eligible chronological one-step forecasts
within each model are scored. The first target requires four earlier
checkpoints. Missing checkpoints are not imputed.

## Baselines and controls

1. **T338 equal-average translation:**
   `0.5*v_parent + 0.5*v_child`.
2. **Persistence:** next log value equals current log value.
3. **Local flow:** extrapolate `v_child` alone.
4. **Parent flow:** extrapolate `v_parent` alone.
5. **Ordinary local trend:** least-squares line through the last four
   `(tau, log M)` layer observations.
6. **Corrected broken lineage:** retain the correct `v_parent`, but replace
   `v_child` with the next layer's child flow cyclically:
   `v_parent + 0.5*v_broken_child`.

## Metrics and uncertainty

Primary loss is mean absolute error in natural-log activation, averaged first
with equal weight per model and then across `top1` and `median`. Also report
RMSE, direction accuracy for non-zero changes, per-stream and per-model loss,
and ARA-coordinate absolute error.

For paired comparisons, use an equal-model bootstrap with 10,000 draws on
evaluation and holdout. Report the mean paired difference and percentile 95%
interval. Nine named models, not individual rows, are the cross-architecture
units.

## Registered gates

### G0 — integrity

The source commit, schema exclusion, frozen hashes, splits, causal prefixes,
saved outputs and independent recomputation must pass validation.

### G1 — basic predictive value

Corrected ARA joint MAE must beat persistence in evaluation and holdout.

### G2 — added parent information

Corrected ARA joint MAE must beat ordinary local trend in evaluation and
holdout.

### G3 — child identity is load-bearing

Corrected ARA joint MAE must beat corrected broken lineage in evaluation and
holdout.

### G4 — both visible cuts survive

Corrected ARA must beat persistence for both `top1` and `median` separately in
the formula-correction holdout.

### G5 — direction

Corrected ARA pooled direction accuracy must exceed local-flow direction
accuracy in the formula-correction holdout. Ties fail.

### G6 — the correction itself adds value

Corrected ARA joint MAE must be lower than T338's `0.5 + 0.5` equal-average
translation in evaluation and holdout separately.

## Verdict

- **Supported:** G0–G6 all pass.
- **Mixed/partial:** G0, G1, G3 and G6 pass, but one or more of G2/G4/G5
  fails.
- **Not supported in this form:** G0 fails, or any of G1/G3/G6 fails.

No post-result edit may alter the formula, gates or verdict. T338 remains
frozen and must be labelled as the wrong-translation control rather than
silently rewritten.

