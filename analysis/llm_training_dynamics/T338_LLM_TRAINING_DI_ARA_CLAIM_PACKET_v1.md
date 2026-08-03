# T338 claim packet — LLM training Di-ARA forecast

**Claim ID:** `T338/LLM-TRAINING-DI-ARA/v1`  
**User verdict:** `EXACT ENOUGH TO TEST` (3 August 2026)  
**Status:** frozen before trajectory/outcome inspection

## Plain-language claim

Follow the same activation identity in the same transformer layer through
successive training checkpoints. Read the largest activation and the ordinary
background activation as two separate ARA time cuts. Keep every layer as a
child of the whole model rather than averaging the children away.

The frozen prediction is that the next state of a layer can be estimated from
two already-visible relations: its own recent movement and the simultaneous
movement of the model parent. If this is a load-bearing child-to-parent ARA
relation, that fixed forecast should outperform a stationary value, an
ordinary layer-only trend, and the same calculation after layer lineage is
broken. Larger model sizes are kept untouched for the final test.

This first pass does not name either measured stream Phase A or Phase B. It
tests the relational geometry before assigning phase ownership.

## Mathematical translation

For positive observable `M` (independently `top1` and `median`) in layer `l`
at checkpoint `t`, define training-rung time

\[
\tau_t=\log_2(1+\mathrm{step}_t)
\]

and the same-identity interval ratio and ARA coordinate

\[
s_{l,t}=\frac{M_{l,t}}{M_{l,t-1}},\qquad
x_{l,t}=\frac{2s_{l,t}}{1+s_{l,t}}
=1+\tanh\!\left(\frac{\log s_{l,t}}2\right).
\]

The corresponding rung-normalized flow is

\[
v_{l,t}=\frac{\log M_{l,t}-\log M_{l,t-1}}
{\tau_t-\tau_{t-1}}.
\]

Using only the last three completed intervals, let `v_child` be the median
flow of layer `l` and `v_parent` the median of the model-wide layer-median
flows. The frozen ARA forecast is

\[
\widehat v_{l,t+1}^{ARA}
=\tfrac12v_{child}+\tfrac12v_{parent},
\]

\[
\log\widehat M_{l,t+1}
=\log M_{l,t}+\widehat v_{l,t+1}^{ARA}
(\tau_{t+1}-\tau_t).
\]

The `1/2 + 1/2` is the declared child/parent one-rung composition for this
test, not a fitted weight. `top1` and `median` are forecast independently; the
third Information³ relation is their log difference
`log(top1/median)` and is reported, not used to tune the forecast.

## Back-translation check

- Same layer through time = same identity, no identity hopping.
- `top1` and `median` = two separate cuts, not prematurely forced into a
  Phase A/Phase B label.
- Layer flow = child view.
- Median flow across all layers = model-parent view.
- Their fixed half-and-half handover predicts the next layer state.
- Breaking the layer lineage tests whether the child identity matters.
- Larger model families test whether the relation scales beyond the models
  used to establish it.

## Boundaries

This can support a predictive child-to-parent LLM training coordinate. It
cannot by itself prove that all LLM internals are ARA, identify a hidden phase,
establish a universal constant, or show a capability mechanism.

