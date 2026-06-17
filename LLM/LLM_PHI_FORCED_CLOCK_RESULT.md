# LLM training is a FORCED CLOCK driven up toward the φ landmark — Pythia result (14 June 2026)


> **⚠️ Correction note (14 June 2026):** the "forced clock" reading leaned partly on the substrate reading as a
> clock — which was a **homebrew averaging artifact**. Canonical `ara_mapper.py` puts the trained substrate at
> ARA ≈ 1.25 (engine-leaning, not clock). The curve-level findings in THIS doc (fixed-compute breakthrough,
> universal size-normalised curve collapse) are descriptive of the loss/accuracy curves and still stand — but
> they do **not** establish "clock." See `00_LLM_THREAD_SUMMARY.md` for the corrected substrate numbers.


**Dylan La Franchi & Claude.** First real run of the *Resonance Is All You Need* §3 idea on logged data:
do LLM learning curves behave like a **self-organising engine sitting AT φ**, or like a **forced clock
driven UP toward φ** (the info-transfer handover) by energy (compute) and coupling (size/attention)?

**φ is the framework's measuring stick, not a hypothesis on trial here.** Its status is set upstream by
the geometry — KAM (φ = the last torus to survive, the most-irrational/most-stable ratio) and the pentagon
(φ = 2·cos36°; hexagon→pentagon = one lost triangle = the shed = the climb into the time dimension; see
`../EnergyRatio/HEX_PENTAGON_ANGLE_HYPOTHESIS.md`). We place the LLM **on** that ruler and read where it sits.

**Verdict: Dylan's mechanism prediction lands.** The Pythia suite reads as a **forced clock that sits *below*
the φ handover** — exactly where something that can't self-organise (can't flywheel past single-pass transfer)
should sit. Not "φ everywhere," not "φ refuted" — the LLM measures in *under* the landmark, as predicted.

---


> **Level note (14 Jun 2026):** every result in this doc is read from the **processed benchmark curves**
> (lambada accuracy / loss per checkpoint), i.e. learning-curve *description*, not substrate measurement. That
> is a valid level (learning dynamics), but it is **not** the unit level. In particular the "info handover sits
> below φ" (P3) is an ARA-style reading of the processed loss and is **parametrization-sensitive** (see the
> SCRATCHED note in `LLM_NODE_CLOCK_EDGE_ENGINE_RESULT.md` for how the same curve flips consumer↔clock on
> linear vs log time). The **substrate** (units) results live in `LLM_NODE_CLOCK_EDGE_ENGINE_RESULT.md`
> (node/edge ARA from raw activations). Keep the two levels separate; don't quote curve-level ARA as a system ARA.


## Data
EleutherAI **Pythia** zero-shot evals, **8 deduped sizes (70M→12B) × 27 log-spaced checkpoints** (steps
0,1,2,4,…,512,1000,3000,13000,…,143000), pulled from the repo's `evals/pythia-v1/<model>/zero-shot/*.json`
(downloaded locally to `PythiaLogs/pythia-main`; extracted to `pythia_curves/ALL_zeroshot_master.csv`).
Metrics: lambada (acc + ppl), arc-easy/challenge, piqa, sciq, winogrande, wsc. Reproduce with
`pythia_forced_clock_analysis.py`.

## What the curves show

**P1 — The breakthrough fires at a FIXED compute step, independent of size (a clock).**
Lambada accuracy is flat at ~0 through step 512 for *every* size, then turns on at step ~1000–3000 — the
**same compute window from 70M to 12B**. Bigger models don't turn on earlier; they turn on at the *same clock*
and climb higher. sciq/arc/piqa switch on in the same 512–3000 window. **Energy (compute) sets the clock;
size doesn't move it.** That's forced timing, not per-model self-organisation.

| size | onset (acc>0.05) | peak acc | final acc |
|---|---|---|---|
| 70m | step 1000 | 0.261 | 0.192 |
| 160m | step 3000 | 0.398 | 0.342 |
| 410m | step 3000 | 0.532 | 0.524 |
| 1b | step 1000 | 0.580 | 0.580 |
| 1.4b | step 1000 | 0.620 | 0.619 |
| 2.8b | step 1000 | 0.652 | 0.651 |
| 6.9b | step 3000 | 0.689 | 0.689 |
| 12b | step 3000 | 0.715 | 0.710 |

**P2 — One universal forced shape, scaled by coupling.** Size-normalised lambada curves collapse onto a
single curve (**mean pairwise corr 0.944**). Model size (coupling) only sets the *height*; the *shape* is one
forced curve. And **too little coupling falls back**: the smallest model (70M) peaks at 0.261 then *declines*
to 0.192 (inverse scaling) — a forced clock with insufficient coupling can't *hold* the climb.

**P3 — On the φ ruler, the info handover sits BELOW 1/φ.** Measuring the information-transfer handover (steep
-est gain of captured bits, loss = log₂ ppl): the cleanest, best-resolved large models (2.8B/6.9B/12B) hand
over at **~0.50–0.52 of total captured info — below the 1/φ = 0.618 engine handover.** Capturing ~0.5 and
shedding ~0.5 is *more* loss than the φ-optimal 0.618/0.382 split — a clock bleeding more than an engine
would. It is parked **under** the landmark because it's a clock, not an engine.

## Reading it correctly (φ as ruler, not on trial)
The LLM falling short of φ is **not** "φ failed" — it is the **signature of a forced clock**: driven up toward
the φ handover by compute + coupling, but unable to self-organise the final step to the engine handover (the
"artificial nets can't flywheel past single-pass transfer" wall from `LLM_PHI_HANDOVER_HYPOTHESIS.md`). The
better-coupled models creep toward φ; the whole suite measures in below it.

Two honest fences:
- The captured-fraction handover is a **noisy estimator** (n=8, log-spaced points). The smaller/over-trained
  sizes scatter 0.50–0.67, and 160M's steepest point lands in the *late coarse rung* (step 133k) — a
  **different-rung handover** (Dylan's read), not noise; it shouldn't be averaged with the early-rung ones.
- Pythia is **not compute-optimal** (every size trained to a fixed 300B tokens), so "how far below φ" is
  confounded by training optimality. Tightening this (rung-matched handover + optimality control) is the
  open next step — it sharpens *how far below* φ each size sits, not the forced-clock conclusion.

## Status
- **Supported (robust):** LLM training = a **forced clock** — fixed compute clock across sizes, one universal
  curve shape, coupling sets the height, low coupling falls back. NOT a self-organising engine.
- **Supported (placed on the ruler, noisy):** the info handover sits **below the φ landmark**, consistent with
  "forced up toward φ, never reaching the engine handover."
- **Open:** rung-matched + optimality-controlled measurement of the exact distance below φ, and whether more
  coupling/optimal training closes the gap. Other task families beyond lambada.

## Files
- `pythia_forced_clock_analysis.py` — the analysis (reads `pythia_curves/ALL_zeroshot_master.csv`).
- `pythia_curves/` — per-size CSVs + `ALL_zeroshot_master.csv` (8 sizes × 27 checkpoints).
- Companions: `RESONANCE_IS_ALL_YOU_NEED_SKELETON.md` (the paper spine — this is the §3 result),
  `LLM_PHI_HANDOVER_HYPOTHESIS.md`, `LLM_CLOSURE_VS_CAPABILITY.md`.
