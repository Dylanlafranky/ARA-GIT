# T339 claim packet — corrected LLM parent-plus-child forecast

**Claim ID:** `T339/LLM-PARENT-PLUS-CHILD/v1`  
**User correction:** `0.5 child + 1 parent` (4 August 2026)  
**Status:** frozen after T338 exposed the consequences of the wrong
`0.5 child + 0.5 parent` translation, but before the corrected forecast was
calculated or scored

## Plain-language claim

At the rung being measured, the parent is already one complete local identity,
so it keeps weight `1`. A direct child one octave below contributes half of
that parent-rung capacity, so it has weight `0.5`. The intended composition is
therefore:

`one parent + half one child`, not `half parent + half child`.

Follow the same positive activation identity in the same transformer layer
through successive training checkpoints. Estimate its next state using its
model-parent's recent across-layer movement at full weight plus the layer
child's own recent movement at half weight. If this is the correct cross-rung
ARA translation, it should outperform the old equal-average translation as
well as persistence, ordinary local trend and a broken-child-lineage control.

The result tests this exact numerical translation on this public archive. It
does not retrospectively repair T338, which remains the frozen record of the
wrong translation.

## Mathematical translation

For positive observable `M` (independently `top1` and `median`) in layer `l`
at checkpoint `t`, retain T338's unfitted training-rung time, interval ratio,
ARA coordinate and rung-normalized flow:

\[
\tau_t=\log_2(1+\mathrm{step}_t),
\qquad
s_{l,t}=\frac{M_{l,t}}{M_{l,t-1}},
\qquad
x_{l,t}=\frac{2s_{l,t}}{1+s_{l,t}},
\]

\[
v_{l,t}=\frac{\log M_{l,t}-\log M_{l,t-1}}
{\tau_t-\tau_{t-1}}.
\]

Using only the last three completed intervals, let `v_child` be the median
flow of layer `l` and `v_parent` the median of the model-wide layer-median
flows. The corrected forecast is

\[
\boxed{
\widehat v_{l,t+1}^{ARA}=v_{parent}+\tfrac12v_{child}
}
\]

and

\[
\log\widehat M_{l,t+1}
=\log M_{l,t}+\widehat v_{l,t+1}^{ARA}(\tau_{t+1}-\tau_t).
\]

The direct wrong-translation control is retained as

\[
\widehat v^{equal}=\tfrac12v_{parent}+\tfrac12v_{child}.
\]

No normalization by `1.5` is permitted: `1 + 0.5` is the declared cross-rung
contribution budget, not an average whose coefficients must sum to one.

## Back-translation check

- Same layer through time = same child identity.
- Across-layer median movement = the model-parent cut.
- Parent contribution at its measured rung = `1`.
- Direct child contribution one rung below = `0.5`.
- Corrected composition = `1 parent + 0.5 child`.
- Cyclically replacing the child layer tests whether lineage matters.
- T338's `0.5 + 0.5` remains a named translation-error control.
- `top1` and `median` remain separate visible cuts; Phase ownership is not
  assigned in this test.

## Evidence status and boundaries

This is a corrective confirmatory replay on an archive whose trajectories and
T338 scores have already been opened. The corrected outcome is still frozen
before calculation, but it is not a pristine data-blind new-domain test.

A positive result can support this specific parent-plus-child forecast on the
Pythia activation archive. It cannot by itself prove universal `1 + 0.5`
physics, establish phase ownership, prove all LLM internals are ARA, or show a
capability mechanism.

