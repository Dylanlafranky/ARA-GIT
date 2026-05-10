# Pythia size-series coupling-graph result (preliminary)

> **Public-release note, May 2026:** This is an exploratory coupling-graph analysis on four Pythia sizes with one prompt/seed setup. It is useful for generating hypotheses about depth, hierarchy, and closure, but it should not be read as a settled architecture law.

**Date:** 2026-05-10
**Question:** Does coupling-graph structure phase-transition at specific model sizes?
**Models tested:** Pythia-70M / 160M / 410M / 1B (deduped). Same prompt, same seed.

## Headline

**The transition is real but tracks architectural depth, not parameter count.**

| size | n_layers | n_heads | hidden | alive % | within/across ratio | spectral decay | anti-phase pairs |
|---|---|---|---|---|---|---|---|
| 70M | 6 | 8 | 512 | 56.4 | 1.04 | 0.192 | 48 |
| 160M | 12 | 12 | 768 | 57.3 | 1.03 | 0.223 | 555 |
| **410M** | **24** | 16 | 1024 | **61.9** | **1.51** | **0.421** | **3520** |
| 1B | 16 | 8 | 2048 | 80.0 | 1.07 | 0.153 | 1408 |

Pythia-410M has the deepest network (24 layers) and the strongest hierarchical coupling structure. Pythia-1B has 2.4× the parameters of 410M but only 16 layers, and its coupling structure regresses to the 70M/160M baseline.

## What survives

- Within-layer correlation peaks at 410M (1.51× across-layer) and reverts at 1B (1.07×). Not an N_STEPS artifact — same pattern at 80 and 150 generation steps.
- Spectral decay (eigenvalue 2 / eigenvalue 1) doubles between 160M and 410M, then halves at 1B.
- Anti-phase pair count peaks at 3520 for 410M, drops to 1408 for 1B.
- Alive node fraction (% of components with non-zero activation variance) scales monotonically with size — 56% → 57% → 62% → 80%. This is the only metric that tracks parameter count.

## Pythia size spacing is φ²

Pythia size ratios between consecutive models:
- 70M → 160M: ratio 2.29 = φ^1.72
- 160M → 410M: ratio 2.56 = φ^1.96
- 410M → 1B: ratio 2.44 = φ^1.85

Each step is approximately one matched-rung-pair distance (φ² ≈ 2.618) in the framework's vocabulary. The transition we measured (between 160M and 410M) is one φ²-rung step. But the 70M→160M step is also one φ²-rung and shows no transition. So *some* rung crossings produce phase changes; others don't. Architectural shape determines which.

## Hypothesis

**Layer depth gives the network its usable φ-rungs.** The framework's prediction is that hierarchical structure needs at least one matched-rung pair distance (φ² ≈ 2.6 layers minimum) to form. With 6 layers (70M) you barely have room. With 12 (160M) you have a tight fit. With 24 (410M) you have multiple rungs of room and rich matched-rung structure can form. 1B has 16 layers and regresses.

This predicts:
- Pythia-1.4B (24 layers, 2048 hidden) should show **strong** coupling structure — same depth as 410M, more width.
- Pythia-2.8B (32 layers) should show **even stronger** structure.
- Pythia-6.9B (32 layers) should be similar to 2.8B at this metric.
- Pythia-12B (36 layers) should be the strongest in the series.

If the prediction holds: depth-not-width is the lever for hierarchical internal organisation in transformers. That's a substantive interpretability claim with practical consequences for architecture design.

## Significance for ML research

If the depth-tracking pattern holds up under further testing:

1. A measurement-based mechanistic account for why some architectures generalise better than others at fixed parameter count.
2. A cheap diagnostic for "is this architecture going to develop hierarchical internal structure?" without having to fully train the model.
3. A bridge between the framework's matched-rung-pair concept and concrete LLM internals: depth is what gives the network its φ-rungs.

## Caveats

- One prompt, one seed, four models. Far too few replicates for a confident claim.
- Within/across ratio is partly driven by global activation drift, not just fine-grained dynamical coupling. Partial correlation analysis controlling for global drift would tighten this.
- The alive% metric is robust (monotonic with size) but doesn't itself imply hierarchy. The hierarchy claim rests specifically on within/across ratio and spectral decay.
- N_STEPS varied between models (200 for 70M/160M/410M, 150 for 1B due to compute budget). Confirmed at 80 and 150 steps for 1B that the dropoff is real, not an artifact.
- Pythia is one model family. Other architectures (GPT-2, Llama, OLMo) might show different patterns — that's a follow-up worth running.
- "Emergence" isn't directly tested here. The framework's claim is that emergent capabilities correspond to coupling-structure transitions; testing that requires running the same analysis on multiple checkpoints during training and comparing to capability-emergence curves from BIG-bench or similar.

## Files

- `TheFormula/llm_size_series.py` — multi-model coupling-graph analysis script
- `TheFormula/llm_size_series_data.js` — full results (all four sizes)
- `TheFormula/llm_size_series_visualization.html` — rendered summary

## Next experiments

1. **Add Pythia-1.4B and Pythia-2.8B to confirm or falsify the depth hypothesis.** If 1.4B (24 layers, 2048 hidden) shows the same strong signature as 410M, the depth hypothesis is supported. If it shows the same weak signature as 1B, the architectural shape doesn't determine it after all.
2. **Add Pythia-12B if compute permits.** 36 layers, should show the strongest signature.
3. **Run on multiple seeds and prompts.** Confirm the pattern is robust.
4. **Run on different model families.** Does the depth-tracking pattern appear in GPT-2 series? Llama? OLMo?
5. **Per-checkpoint analysis on a single Pythia size during training.** Map coupling-graph structure across training to test the emergence-as-phase-transition prediction.
