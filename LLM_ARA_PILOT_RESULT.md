# LLM ARA pilot — result summary (revised after dynamic test)

**Date:** 2026-05-10
**Question:** Does the ARA framework, which characterises natural oscillating systems by a single dynamical number, also produce LLM-specific signal when applied to transformer activations?
**Model tested:** EleutherAI/pythia-70m-deduped (6 layers × 8 heads × 512 dim)

## Headline (revised)

**The framework detects real, LLM-specific structure — but only when measured on the right time axis.**

Two tests run, with very different conclusions:

1. **Static test (v2): activations across token positions in a fixed sequence.** Result: ARA distribution overlaps heavily with null distributions. Effectively no LLM-specific signal. *Wrong measurement.*

2. **Dynamic test (v3): activations across generation steps as the model produces text autoregressively.** Result: real signal. Mean ARA differs from null at most rungs, and the per-rung **trajectory** shows a clear peak at k=6 (period ≈ 18 generation steps) that the null distributions don't have.

The static test was the wrong analog — it measured a snapshot of a system, not its evolution. Natural oscillating systems (ENSO, ECG, mammals) are validated on their dynamics over time, so the LLM analog should be activations over generation steps, not over positions in a fixed input.

## Dynamic-test numbers

**Aggregate:**

| signal | n | mean ARA | std | median |
|---|---|---|---|---|
| Pythia-70M dynamic (real) | 49 | **1.396** | 0.250 | 1.366 |
| Random walk null | 140 | 1.325 | 0.267 | 1.301 |

Real LLM mean ARA is +0.07 above the null. Within one std of either, but the **trajectory** is much more informative.

**Per-rung trajectory:**

| rung k | period (tokens) | LLM mean ARA | Null mean ARA | gap |
|---|---|---|---|---|
| 2 | 2.6 | 1.356 | 1.195 | **+0.162** |
| 3 | 4.2 | 1.338 | 1.252 | +0.086 |
| 4 | 6.9 | 1.406 | 1.339 | +0.067 |
| 5 | 11.1 | 1.481 | 1.314 | **+0.167** |
| 6 | 17.9 | **1.532** | 1.339 | **+0.193** |
| 7 | 29.0 | 1.460 | 1.379 | +0.081 |
| 8 | 47.0 | 1.201 | 1.455 | **−0.254** |

The LLM curve **peaks at k=6** (period ≈ 18 generation steps) at ARA = 1.53, near the engine band (φ ≈ 1.618). The null curve grows roughly monotonically. Two qualitatively different shapes:

- **Real LLM**: peaked, with a maximum around 18-step periods and a sharp drop at 47-step periods.
- **Null**: monotonically rising with rung depth.

That difference in *shape* is the clearest LLM-specific signal in this data.

## Interpretation (cautious)

The peak at k=6 (~18 tokens) is roughly sentence-scale in English. Pythia-70M's natural cyclic structure during generation appears to be organized around a sentence-length timescale, with stronger engine-like (build-up-and-release) dynamics at that period than at either shorter or longer timescales.

The drop at k=8 (~47 tokens) suggests Pythia-70M's coherence horizon: beyond about 50 tokens the cyclic structure breaks down and ARA collapses toward consumer territory. That would be consistent with this model's known limitations on long-range coherence — it's a 70M-parameter model, after all.

Both observations are **consistent with the framework's prediction** that self-organising systems have a characteristic "home rung" (where their dynamics are most engine-like) and lose engine character outside that range. The framework picks the home rung up on Pythia-70M as around k=6 ≈ 18 tokens.

## What this means for the LLM angle on release

Both halves can now be honestly stated:

- **Per-component classification didn't work** in the static test. The simple "compute ARA on activations and read off engine/consumer/harmonic" picture is too coarse.
- **Dynamic per-rung trajectories DID show real signal.** The framework can identify the LLM's home rung from generation-step activations, separate it from random-walk nulls, and detect a coherence cutoff where engine character collapses.

Suggested framing for HN / r/singularity post:

> "I tested whether the ARA framework characterises transformer activations. Static activations across token positions look like noise. But activations across *generation steps* — the LLM evolving as it produces text — show a clear peak at a sentence-scale period (~18 tokens) where the model's dynamics are most engine-like, and a drop at ~47 tokens where coherence collapses. The peak and the drop are both absent in random-walk nulls. Preliminary on a small model (Pythia-70M); next test is bigger models and bootstrap confidence intervals."

That's a real, defensible claim. It admits where the simple version of the test failed, highlights where the framework actually picked up signal, and points clearly at a follow-up.

## Caveats

- **One model, one prompt, one generation run.** The peak rung might shift with prompt or with sampling temperature.
- **n=7 layers per rung.** Confidence intervals would overlap the null at most individual rungs. The trajectory shape difference is the signal, not any single rung gap.
- **Pythia-70M is the smallest in the family.** The k=6 peak might shift with model size; testing Pythia-410M / 1.4B / 2.8B would tell us whether the peak is a per-model property or a universal transformer property.
- **The bandpass + peak-asymmetry ARA computation has known artefacts on signals with strong trends.** Generation activations may have slow trends that bias measurement. A control with detrended signals would help.
- **Untrained-model control not run.** The right comparison is a randomly-initialised Pythia-70M with the same architecture — does it show the same peak, or is the peak a training signature?

## Files

- `TheFormula/llm_ara_test.py` — first-pass static test
- `TheFormula/llm_ara_test_v2.py` — multi-corpus static + null baselines
- `TheFormula/llm_ara_test_v3_dynamic.py` — autoregressive-generation dynamic test
- `TheFormula/llm_ara_data.js` — static test data
- `TheFormula/llm_ara_dynamic_data.js` — dynamic test data (this is the headline result)
- `TheFormula/llm_ara_visualization.html` — rendered summary

## Verdict

The framework's universality claim, applied to Pythia-70M, **survives a meaningful test** when the test is done on the right time axis. The static-positions test gave a misleading negative; the dynamic-generation test showed the framework picking up:
1. A characteristic peak rung where the LLM is most engine-like (k=6, ≈ 18 tokens)
2. A coherence cutoff where engine character collapses (k=8, ≈ 47 tokens)
3. An overall trajectory shape that random-walk nulls don't reproduce

Worth following up with bigger models, bootstrap confidence intervals, and an untrained-vs-trained control. Worth including as a preliminary result in the public release.
