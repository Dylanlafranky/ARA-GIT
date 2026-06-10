# Gemma 4 coupling-graph test — PRE-REGISTERED blind prediction (9 June 2026)

Logged **before** running, so this is a genuine blind test. Script: `TheFormula/llm_gemma4_coupling.py`
(can't run in the Cowork sandbox — no GPU, ~1 GB disk, gated weights; run on a GPU box / Colab).
Baseline to beat = the Pythia size-series (`LLM_SIZE_SERIES_RESULT.md`): depth-not-width, with
Pythia-410M (24 layers) the prior champion at within/across ratio **1.51**, spectral decay **0.42**,
3520 anti-phase pairs.

Gemma 4 facts (web, June 2026): variants **E2B, E4B, 12B (48 layers, ~12B params), 26B A4B (MoE), 31B**.
Architectural departures vs a plain transformer: **Per-Layer Embeddings** (token identity fed into every
decoder layer), **Shared KV Cache** (later layers reuse earlier layers' K/V), **Dual RoPE** (different rotary
encodings for local vs global attention).

## The framework's predictions (falsifiable)

**P1 — Depth, not params, drives coupling structure.** Within/across ratio, spectral decay, and
Information³ closure (triangles) should track **layer depth**, not parameter count. Gemma 4 **12B has 48
layers — deeper than any Pythia we tested (max 36)** — so the framework predicts Gemma 4 12B shows the
**strongest coupling structure of anything measured to date**: within/across ratio **> 1.51** and a new-max
closure_ratio. A shallow variant (E2B) should be **weak** even though it's a capable model.
*Falsified if* a shallow variant shows strong structure or the 48-layer 12B shows weak structure.

**P2 — φ²-rung depth spacing.** Transitions in coupling structure should land at depth steps of ~φ² ≈ 2.6
layers, not smoothly with size. Within the Gemma 4 family, jumps in within/across ratio should align with
depth gaps, not parameter gaps.

**P3 — Shared KV Cache → elevated CROSS-LAYER coupling.** Gemma 4 literally wires later layers to reuse
earlier layers' K/V — that *is* the framework's matched-rung cross-layer coupling, built into the
architecture. Prediction: Gemma 4's **cross_layer_pos and closure_ratio (triangles) should be unusually
high for its depth** relative to Pythia (which has no such sharing). This is the cleanest Gemma-specific
prediction. *Falsified if* cross-layer coupling is ordinary / no higher than a same-depth plain transformer.

**P4 — Dual RoPE → elevated ANTI-PHASE pairs.** Two rotary systems (local vs global) = two phase families =
the framework's two-wave / space–time split. Prediction: **n_anti (anti-phase pairs) elevated** relative to
a single-RoPE model of comparable depth. *Falsified if* anti-phase count is unremarkable.

**P5 — Per-Layer Embeddings → higher alive%, lower loose_fraction.** Feeding the base datum into every layer
should keep more nodes engaged at every rung (the framework's "datum carried at every scale"). Prediction:
**alive_frac high and loose_fraction low** for Gemma 4's depth. *Falsified if* alive% just tracks size as in
Pythia (56→80%) with no lift from the per-layer embedding.

## Honest caveats (state before looking at results)
- Gemma 4 is **not a clean scaled series** like Pythia — variants differ in architecture (MoE vs dense,
  E2B/E4B are MatFormer-nested), so cross-variant depth comparison is confounded. **P3/P4/P5 (the
  architecture-departure predictions) are the cleaner, more interesting tests** than the raw depth-series P1.
- Cross-architecture comparison to Pythia is itself a confound (different families). The strongest reading is
  *internal*: does Gemma 4's explicit cross-layer KV sharing show up as measurably elevated cross-layer
  coupling vs its own within-layer coupling?
- One prompt, one seed (matching the Pythia protocol). Treat as hypothesis-generating, not settled.
- Shared-KV layers may return `None` attentions for some layers under `eager`; the script zeros those (they
  become "dead" head-nodes) — interpret alive% with that in mind.

## Results (run 9 June 2026, Colab T4, transformers 5.10.0.dev0, AutoModelForImageTextToText)
| variant | n_layers | params_M | alive% | within/across | spectral_decay | n_anti | cross_layer_pos | closure_ratio | intel_index |
|---|---|---|---|---|---|---|---|---|---|
| gemma-4-E2B | 35 | 5104* | 100.0 | 1.276 | 0.289 | 90 | 134 | 0.981 | 1.161 |
| gemma-4-12b | 48 | ~11950 | (not yet run) | | | | | | |

*params_M = full multimodal model (vision+audio+text towers), not the "effective 2B" text decoder; 35 = text-decoder depth.

**Verdict — the predictions mostly did NOT transfer to Gemma 4 (honest miss):**
- **P1 (depth→new-max within/across): MISS.** 35-layer E2B scored within/across **1.276 < Pythia-410M's 1.51** (24 layers). Deeper but *weaker* hierarchical ratio — cuts against depth-monotonicity.
- **P2 (φ²-rungs): untested** (need ≥2 Gemma variants; run 12B to test).
- **P3 (shared-KV→high cross-layer/closure): UNSCORED.** closure_ratio **0.981** is strikingly high (near-saturated triangles) and *consistent* with the idea, but there's no same-depth no-KV-sharing baseline to attribute it. Suggestive, not a win.
- **P4 (dual-RoPE→elevated anti-phase): MISS.** n_anti **90**, far below Pythia-410M's 3520. Anti-phase suppressed, not elevated.
- **P5 (per-layer-emb→high alive, low loose): SPLIT.** alive **100%** (above Pythia's 80% ceiling) lands — but loose_fraction **0.845** (high) is the opposite of "low loose." And alive=100% has a mundane alternative (any capable modern model has all components active over 200 steps; threshold std>1e-6 is tiny) — don't over-credit.

**Confounds (flagged, not buried):** (1) cross-architecture — Gemma vs Pythia different families, within/across not apples-to-apples; (2) the **100%-alive regime likely deflates within/across itself** (uniform engagement spreads coupling), so 1.276 vs 1.51 may be a metric artifact not a depth refutation — the metric isn't clean across alive% regimes. (3) one model, one seed, one prompt = hypothesis-generating only.

**Net:** a single cross-architecture data point that **leans against** the depth/coupling predictions, with one interesting-but-unattributable number (closure 0.981). To make this a real test, run **gemma-4-12b (48 layers)** for the within-family depth comparison (P1/P2) and ideally a same-depth non-shared-KV model for P3. Don't claim a Gemma 4 confirmation.
