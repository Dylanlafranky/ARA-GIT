# Resonance Is All You Need — paper skeleton (spine + tests + data)

**Draft skeleton, 10 June 2026. Dylan La Franchi & Claude.** The framework's contribution to LLM theory.
Structured so the spine is visible and every claim carries (a) an evidence tier, (b) a concrete test, (c) public
open-weight models / datasets to run it on. **Honest rule:** the paper leads with the *tested* claim (§2). The
rest are labelled as theory/prediction. A framework paper without a real result is a manifesto — §2 is the load-bearing experiment.

## Thesis (one sentence)
*"Attention Is All You Need" gave the coupling **mechanism** but not the **stability criterion**; resonance is
that criterion — stable knowledge sits in **closed, resonant couplings** (closed information triangles, φ-timed
handover), hallucination is **non-resonant coupling that never closes**, training is a climb of **φ-handover
rungs**, and capability transfers by **cross-rung (vertical-ARA) coupling**.*

Attention weights already *are* couplings (which tokens resonate). The new content is not renaming them — it is
predicting **which couplings hold and which decohere**, and tying that to a single constant (φ) the framework
grounds independently (KAM = φ is the last torus to survive; pentagon geometry; `ACTION_AXIS_AND_KAM_GROUNDING.md`).

---

## §1 — The reframe: resonance = the stability criterion on attention
**Claim:** attention = coupling; the framework adds *which couplings are stable* (resonant/closed) vs transient
(non-resonant). **Evidence tier: CONCEPTUAL** — must be made to *predict* something attention alone doesn't, or
it's just relabelling. The teeth come from §2.
**Test:** show a resonance/closure measure on the attention–activation graph separates stable (correct) from
unstable (hallucinated) generations *better than* attention magnitude alone (the relabelling-control).
**Data/models:** any open model with extractable attention + activations — **GPT-2**, **Pythia**, **OLMo**.

## §2 — EMPIRICAL SPINE: closure predicts grounded knowledge; non-closure = hallucination
**Claim:** genuine knowledge = **closed resonant triangles** (mutually-supporting components, the Information³
closure); a hallucination is an **open, non-resonant coupling** that fails to close. So closure at generation
time should track factual correctness, and *gating* on it should cut hallucination.
**Evidence tier: PRELIMINARY-REAL → the one to harden.** We already have the closure metric predicting
*capability* (`LLM_CLOSURE_VS_CAPABILITY`: closed-triangle index, Spearman ρ=1.000 on 5/6 benchmarks) — but
**n=4 models**, and capability ≠ per-generation truthfulness. This section turns it into a per-generation
hallucination test.
**Tests:**
1. *Correlational:* per generated answer, compute activation **closure/resonance** (triangles with |corr|>θ);
   does **low closure predict factual wrongness** on a hallucination benchmark? Report AUROC vs the
   attention-magnitude baseline (the relabelling control) and vs token log-prob/entropy baselines.
2. *Interventional:* **gate** generation on resonance (re-rank/suppress low-closure continuations); measure the
   hallucination-rate drop and the accuracy/abstention trade-off.
3. *Null:* shuffled-component closure should NOT predict truth (guards against a generic confidence proxy).
**Data/models:** open weights with full activation access — **Pythia 70M–12B** (EleutherAI), **OLMo 1B/7B**
(AI2, fully open), **Llama-2/3-8B**, **GPT-2**, **Mistral-7B**, **Qwen**. Hallucination/factuality benchmarks:
**TruthfulQA**, **HaluEval**, **FEVER**, **SimpleQA**, **FActScore**, **PopQA**.

## §3 — THEORY: the φ-handover training law; emergence = rung-breakthrough
**Claim:** the training-time handover is **optimal at φ**; loss **plateaus at the φ-cutoff** until enough
energy/coupling accumulates to **scale to the next rung** — i.e. **emergent abilities are rung-breakthroughs**,
not smooth gains. **Evidence tier: THEORY, falsifiable, data not yet pulled** (`project_llm_phi_handover_hypothesis`).
Honest: the φ-*exponent* fit is unfalsifiable (φ-powers tile densely); the test is the **rung-below** — the
residual structure of the learning curve, NOT the headline slope.
**Tests:**
1. Take a numeric **loss-vs-step learning curve**, detrend the power law, and ask whether the **plateaus/drops
   are φ-rung-spaced** (against a phase-randomised null — same spectrum, scrambled phase).
2. Cross-map the **emergent-ability eval curves** (where accuracy jumps) to those plateau/break locations.
**Data/models:** **OLMo** (best — AI2 releases the *actual loss logs* + hundreds of intermediate checkpoints +
the training data Dolma), **Pythia** (8 sizes × 154 checkpoints, numeric losses), **BLOOM** checkpoints,
**Cerebras-GPT** (scaling-law family). Emergence curves: **BIG-bench**, the emergent-abilities datasets.

## §4 — ENGINEERING: vertical-ARA (cross-rung) coupling drives emergence & transfer
**Claim:** scaling **coupling a rung up or down** on the model's ARA produces behaviour beyond either model
alone — and this **unifies three ML areas as one operation:** distillation (couple a rung *down*),
weak-to-strong (couple a rung *up*), chain-of-thought (each next thought a rung *down*, the recycling flywheel).
**Evidence tier: TESTABLE / NOVEL** (the session's coupling mappings).
**Tests:**
1. Couple two models at **adjacent size-rungs** (teacher↔student both directions); does the *pair* exceed either
   alone, and does the gain peak when the rung gap ≈ the φ-handover?
2. Show **distillation and weak-to-strong are the same cross-rung op** measured by the same coupling quantity
   (symmetric transfer), not two phenomena.
3. Measure **CoT as rung-descent**: do successive reasoning steps occupy successively faster/smaller cycles?
**Data/models:** **Pythia size series** (a ready-made rung ladder, same data/recipe across sizes — ideal for
clean cross-rung coupling), **OLMo sizes**, **Qwen/Llama size families**. Weak-to-strong: **OpenAI's
weak-to-strong-generalization** release (code + setup). Distillation: standard teacher→student on the same suites.

---

## Honest constraints (state these in the paper, not after)
- **§2 is the whole paper's credibility** and it requires running real LLM activation experiments (closure on a
  hallucination set). Our last LLM run (Gemma-4) hit infra walls — this needs GPU access; design it to run on a
  **small open model first** (GPT-2 / Pythia-410M) where activations are cheap, then scale.
- The closure base is **n=4** today; §2 must widen it and move from *capability* to *per-generation truth*.
- **φ-exponent claims are retired** as unfalsifiable (dense φ-power tiling); only the **rung-below / plateau**
  version is testable. φ is the **landmark, not the target** (proven handover: KAM + pentagon, not numerology).
- Keep the descriptive-vs-forecast discipline of `CLAIMS_STATUS.md`: §1 is a reframe, §2 is the result, §§3–4
  are predictions. Don't let the manifesto outrun the experiment.

## ✅ VERIFIED GPU-FREE DATA SOURCE for §3 (found & confirmed 10 June 2026)
The §3 test (capability-vs-step, "emergence = rung-breakthrough") can run **with no GPU** on real logged numbers:
- **Source:** EleutherAI Pythia repo, `evals/bias-evals/` — one JSON per checkpoint, raw-fetchable, e.g.
  `https://raw.githubusercontent.com/EleutherAI/pythia/main/evals/bias-evals/pythia-1.3b-deduped-step{STEP}_eval_results_*.json`
- **Real, not plot-extracted** (this is the trap that killed the Chinchilla set). Each file holds true eval
  numbers: **lambada_openai (acc, ppl), arc_easy, arc_challenge, piqa, sciq, winogrande, wsc** (+ crows_pairs
  bias metrics to ignore). `config.iteration` = the training step.
- **Coverage:** pythia-1.3b checkpoints span steps 1500 → 71500 (every ~5000 early, every 500 in the 67000–71500
  tail). Other sizes (19m … 1.3b) also present → cross-size rung ladder for §4.
- **Example datapoint (proof):** 1.3b @ step 67000 → lambada acc 0.586, arc_easy 0.572, arc_challenge 0.257,
  piqa 0.721, sciq 0.868, winogrande 0.545.
- **The test, once assembled:** build acc-vs-step per benchmark → detrend the saturating trend → are the
  **jumps/plateaus φ-rung-spaced** (vs a phase-randomised null)? Cross-check ppl-vs-step (the loss proxy).
- **Remaining cost:** ~15–20 individual `web_fetch` calls to pull the per-step JSONs (each large; the config
  bloats them) — the one practical friction. Best run fresh as a focused assembly pass.

## Why open models specifically (Dylan's ask: public training weights)
Each test needs **internal access** (activations §2, intermediate checkpoints / loss logs §3, paired sizes §4) —
which closed APIs don't give. Ranked by fit:
- **OLMo (AI2)** — *fully* open: weights, **loss logs**, intermediate checkpoints, training data. Best for §3.
- **Pythia (EleutherAI)** — 8 sizes × 154 checkpoints, one recipe. Best for §4 (rung ladder) and §3 (curves).
- **GPT-2 / Pythia-410M** — cheapest for §2 activation experiments to prototype.
- **Llama / Mistral / Qwen (open weights)** — capable models for §2 hallucination benchmarks at scale.
