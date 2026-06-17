# Neural scaling law in ARA — measure the BASE WAVE, not the line (14 June 2026)

**Dylan La Franchi & Claude.** The apples-to-apples answer, done the right way at last.

## The mistake I kept making
I kept taking ARA off the **finished scaling-law curve** (loss vs compute) — a curve that is already
**averaged once** (mean over tokens → perplexity) and **fitted once** (power law over compute). Reading ARA off
that flattened line is ill-posed: it's monotone, so the number flips with the axis (linear→consumer ~0,
double-log→"clock"). That whole line of attack was a flatten-then-measure error. Dylan, repeatedly: *"the line
is already processed — measure what they measured, find the SAME wave, don't flatten it."*

## What they actually measure
A scaling-law point is **cross-entropy = mean over tokens of −log₂ P(actual next token)** = mean **bits per
token**. That per-token bits sequence is a **WAVE** (predictable tokens ≈ 0 bits, surprising tokens spike). The
loss is its **mean height**; the scaling law is that mean's trend vs compute. So the wave is the foundation; the
law is two levels of smoothing above it. **Measure the wave.**

## Method (canonical, identical to the substrate fix)
Run a real model on real prose, record per-token bits = the base wave, then `ara_mapper.map_system` (octave-rung
decomposition → ARA of the dominant-amplitude rung). Script: `base_wave_ara.py` / `base_wave_robust.py`.
Model: EleutherAI **pythia-70m-deduped** (CPU). Text: public-domain passages.

## Result — the neural scaling law's base wave is ENGINE-LEANING
| text (pythia-70m) | n tok | mean bits (=loss) | **base-wave ARA** | dominant rung |
|---|---|---|---|---|
| Austen narrative (long) | 427 | 4.95 | **1.44** | P=8 |
| Austen narrative (short) | 249 | 5.67 | 1.22 | P≈19 |
| US Constitution (legal) | 194 | 5.17 | **1.61** (≈φ) | P≈18 |
| cell-biology (expository) | 179 | 4.93 | 1.25 | P≈5 |

**Mean base-wave ARA ≈ 1.36 (sd 0.18); combined-passage 1.44.** Every reading sits in the **engine band
between clock 1.0 and φ 1.618 — never a clock, never a consumer (<1).** Per-rung (70m, long Austen): all rungs
1.24–1.44, dominant P=8 at 1.44.

## Apples-to-apples (all measured the SAME canonical way, from raw signals)
| object | ARA | reading |
|---|---|---|
| LLM substrate (node/edge activations) | ~1.25 | engine-leaning |
| **neural scaling law (base wave = per-token bits)** | **~1.36–1.44** | **engine-leaning** |
| golden engine | 1.618 | (legal text lands here) |
| clock | 1.0 | — (only ever appeared by flattening) |

**Takeaway:** measured from what they measured, the neural scaling law is **engine-leaning (~1.4)** — the SAME
band as the substrate. The earlier "clock" readings (1.08, ~1.0) were flatten/double-log artifacts of reading
the processed line. The loss is this wave's mean; the law is the mean's trend; the **ARA lives in the wave**.

## Honest fences / next
- **70M only.** 160M/410M were bandwidth/disk-limited on this box (unauthenticated HF throttle). The size trend
  — does the base-wave ARA climb toward φ with scale? — is the open follow-up (run on a GPU/Colab box or with an
  HF token). **Dylan's call on the prediction.**
- Single short passages (179–427 tok); ARA has real passage variance (sd 0.18). Trend, not a single digit.
- This does NOT resurrect the scratched line-ARA digits; it replaces the *question* (ARA of the line → ARA of
  the wave the line summarises). See `LLM_SCALING_LAW_SHED_TEST.md` (the line has no honest ARA — still true;
  the base wave does).
