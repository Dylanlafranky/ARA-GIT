# T339 — Corrected LLM parent-plus-child forecast

## Technical summary

Dylan's scale correction was right: at the measured parent rung, the parent
retains weight `1` and a direct child one octave below contributes `0.5`.
However, T339 showed that the raw layer-flow variable used as “the child” was
not child-only. It was the whole layer motion and already carried the
model-parent's common motion.

The frozen literal implementation

\[
P+\tfrac12C_{total}
\]

therefore counted the parent twice and was **not supported in this form**. It
was 33.88% worse than T338's equal-average forecast on evaluation and 23.56%
worse on the formula-correction holdout. The independent validator passed
`17/17` checks.

The post-result decomposition resolves the apparent contradiction exactly.
Define the lower-rung child-specific movement as

\[
C_{specific}=C_{total}-P.
\]

Then Dylan's intended rule becomes

\[
P+\tfrac12C_{specific}
=P+\tfrac12(C_{total}-P)
=\tfrac12P+\tfrac12C_{total}.
\]

That is numerically T338's old equal-average forecast. Across all 11,792
eligible layer/stream targets, the maximum discrepancy between these two
expressions was only `8.60e-16`, floating-point noise. This reconciliation is
an exact algebraic identity, not a new predictive win and not a post-result
change to T339's frozen negative verdict.

## The literal total-child formula lost amplitude accuracy

Joint mean absolute error is measured in natural-log activation. Lower is
better.

| Split | Corrected literal `P + 0.5 C_total` | Residual form / T338 equal average | Persistence | Local trend | Broken lineage |
|---|---:|---:|---:|---:|---:|
| Evaluation | 0.116751 | **0.087203** | 0.131258 | 0.088573 | 0.116930 |
| Holdout | 0.146464 | **0.118541** | 0.144781 | **0.115799** | 0.146622 |

The literal rule beat persistence in evaluation but lost to it by 1.16% in
holdout. It lost to local trend in both scored splits. It retained only a very
small intact-lineage advantage over the identically weighted broken-lineage
control: `0.000179` evaluation and `0.000158` holdout. The equal-model
bootstrap interval for the holdout lineage difference crossed zero.

Direction was less damaged than amplitude. Holdout direction accuracy was
`0.775151`, 1.19 percentage points above child-only local flow (`0.763241`).
This is consistent with adding too much motion in roughly the correct
direction: the sign can remain useful while the predicted magnitude
overshoots.

## Both visible streams exposed the same double-counting problem

On the holdout, `top1` literal-rule MAE was `0.196486`, still better than
top1 persistence (`0.207645`). Background/median MAE was `0.096443`, worse
than median persistence (`0.081917`). Thus the frozen both-stream gate failed.

The total layer flow and parent flow were already highly aligned in the larger
models. Parent–child-flow correlations were `0.936–0.942` in evaluation and
`0.944–0.950` in holdout, depending on stream. They also had the same sign on
89.3% to 93.6% of those targets. Adding a full parent to half the total layer
flow therefore commonly reinforced a component already present.

## Metric and cohort definitions

- **Source:** 335 clean raw checkpoint-statistic files from
  `Aimpoint-Digital/pythia-massive-activations`, commit
  `c4c539ac4f8c8fc9694603895d00c1f1af940a20`.
- **Schema exclusion:** malformed `pythia_1b_step0`; no repair or imputation.
- **Rows:** 6,648 reduced model/checkpoint/layer rows and 82,544 saved
  predictor rows across seven predictors.
- **Streams:** sequence-median top-1 activation and sequence-median background
  activation, forecast independently.
- **Evaluation models:** 410m, 1b and 1.4b.
- **Formula-correction holdout models:** 2.8b, 6.9b and 12b. This archive had
  already been opened by T338, so it is not a pristine new-domain holdout.
- **Parent flow:** the recent median flow across layers in the model.
- **Total child flow:** the recent flow of the target layer itself.
- **Child-specific residual:** total child flow minus parent common flow.

## Frozen gates and verdict

| Gate | Result |
|---|---|
| G0 integrity and independent reconstruction | Pass |
| G1 beat persistence in evaluation and holdout | Fail — holdout lost |
| G2 beat local trend in evaluation and holdout | Fail |
| G3 beat corrected broken lineage in both splits | Pass numerically |
| G4 beat persistence in both holdout streams | Fail — median lost |
| G5 beat local-flow holdout direction | Pass |
| G6 beat T338 equal average in both splits | Fail |

Under the frozen verdict rule, T339 is **NOT SUPPORTED IN THIS FORM**.

## What the result changes

The correction distinguishes **scale weight** from **measured total signal**.
The ARA statement “one parent plus half a child” cannot be translated by
adding a full parent to a child measurement that already contains that parent.
The child term must first be isolated as its child-specific residual, or the
hierarchy is flattened and counted twice.

This gives T338 a cleaner post-result mathematical reading:

\[
\underbrace{\tfrac12P+\tfrac12C_{total}}_{\text{T338 numerical rule}}
=
\underbrace{P+\tfrac12(C_{total}-P)}_{\text{full parent + half child-specific residue}}.
\]

The original T338 wording did not make this residual definition, so its frozen
claim must not be silently rewritten. The reconciliation is recorded as a
later derivation and needs a genuinely fresh test in another hierarchy before
being promoted as a predictive principle.

## Robustness, limitations and uncertainty

- Protocol and claim hashes matched their preregistered values.
- Raw reduction, 82,544 predictions, summaries, bootstraps, gates and verdict
  reproduced independently.
- A causal-prefix perturbation confirmed that future values cannot change an
  earlier forecast.
- The direct `1 + 0.5 total-child` failure is secure against the T338 control:
  equal-model bootstrap differences were entirely negative in evaluation
  (`[-0.038331, -0.025114]`) and holdout
  (`[-0.034785, -0.023669]`), where positive would favour T339.
- Only three model families occur in each scored split, so architecture-level
  intervals remain coarse.
- The residual interpretation is algebraically exact but post-result. It does
  not establish that the residual is a physical energy component, Phase A,
  Phase B or a universal octave carrier.

## Recommended next test

Freeze the hierarchy on a fresh public dataset where the parent common mode
and child-specific residual are defined before outcomes are opened:

1. calculate `P` from the declared parent population;
2. calculate `C_specific = C_total - P` without fitting;
3. predict with `P + 0.5*C_specific`;
4. compare with persistence, local trend, total-child double counting,
   parent-only, child-only and broken residual lineage;
5. preserve a model-family or dataset-family holdout not used by T338/T339.

That would test the newly clarified rule rather than merely re-expressing the
already-open T338 numbers.

## Further questions

- Does subtraction in log-flow space isolate the intended child identity, or
  should the parent/child separation use a different ARA-native coordinate?
- Does the half-weight survive when the parent common mode is estimated from a
  disjoint set of siblings rather than a median that includes the target?
- Is the small intact-lineage advantage stable in a fresh architecture family?
- Can the two visible streams be assigned phase ownership without weakening
  the preregistered predictive test?

