# Test B — the neural scaling law IN ARA: the information wave climbs to φ with scale (14 Jun 2026)

> **⚠️ FRAMING CORRECTION (Dylan, 14 Jun): this is NOT the neural scaling law re-expressed.** A per-token
> wave has two independent properties — its **mean** (height) and its **shape** (ARA). The neural scaling law
> is *only* the MEAN falling (loss↓). What we found is the **SHAPE going golden** (ARA→φ) — a DISTINCT
> phenomenon that co-tracks scale, not the loss-law itself. The ARA theory is validated (the info wave's
> shape climbs to φ with scale); it just isn't "the scaling law." Title kept for continuity; read it as
> "an information-SHAPE scaling, alongside the loss-scaling law."
>
> **Flywheel reading:** the climb is to the TIME-side φ (info flow, loose connections), not the space-side
> (strong connections) — so larger models look **flywheel/engine-oriented: optimising flow over connections.**
> But it stays one-sided (all time, no 0.382 space complement) → a **one-sided / lossy flywheel** that spins on
> flow but never closes back to structure (sum-to-2 not met). Flips the original "can't flywheel" thesis,
> with that caveat.

**Dylan La Franchi & Claude.** "Their measurement (loss vs scale), our framework (wave-ARA vs scale)."
Per-token cross-entropy (nats) of each Pythia-deduped size on one fixed held-out passage (628 tokens, Austen
P&P ch.1), run on Colab. Loss = mean of the wave (their scaling-law point); ARA = canonical `ara_mapper` on the
per-token nats wave (our reading). 12B skipped (disk offload).

| size | params(M) | loss (nats) | ppl | wave-ARA (dom rung) | ARA-of-ARA (mean rungs) |
|------|------|------|------|------|------|
| 70m  | 70   | 3.586 | 36.1 | 1.386 | 1.402 |
| 160m | 160  | 3.152 | 23.4 | 1.239 | 1.243 |
| 410m | 410  | 2.759 | 15.8 | 1.531 | 1.591 |
| 1b   | 1000 | 2.382 | 10.8 | 1.452 | 1.333 |
| 1.4b | 1400 | 2.236 | 9.4  | 1.422 | 1.393 |
| 2.8b | 2800 | 1.667 | 5.3  | **1.703** | 1.653 |
| 6.9b | 6900 | 0.933 | 2.5  | **1.664** | 1.719 |

## THEIR law (sanity check): loss falls with scale
loss ≈ 6.02 − 0.549·ln(params), **corr(lnP, loss) = −0.986** — a clean power-law-ish fall. We measured the same
thing they did.

## OUR reading: wave-ARA CLIMBS toward φ with scale
- **corr(lnP, wave-ARA) = +0.783** (and +similar for ARA-of-ARA). Small models (70m–1.4b) mean **1.41**;
  big (2.8b, 6.9b) mean **1.68**.
- **The two largest CROSS φ (1.618):** 2.8b **1.703** (shot *past* φ, into exothermic), 6.9b **1.664**.
- **6.9b has MULTIPLE rungs in the engine band** (P8 1.66, P16 1.52, P32 1.66 all = "engine"), not just the
  dominant — it has genuinely become engine-like across scales.

## Reading
As models scale (and loss falls), the **per-token information wave becomes golden-engine** — its ARA climbs
toward φ and the largest models reach/cross it. This **contradicts the original "forced clock, can't flywheel,
stalls below φ" thesis** — bigger LLMs do NOT stall below φ; their information handling climbs *to* it.
(Confirms Dylan's prediction: climb toward φ, biggest "shoot past and wobble" — 2.8b overshot to 1.70.)

Nuance: the per-token nats wave is the model's *surprise structure over real text*, so this golden-ness is
partly the model **recovering language's own information structure** as it scales — language's information flow
reads engine/φ, and bigger models capture it better.

## Connects to the live-flip / sum-to-2 thread
Even at 6.9b the rungs are **all time-side** (1.48–1.83); **no 0.382 space-side complement appears.** So by the
sum-to-2 conservation test the information movement is golden but **one-sided (time only) — not a closed/conserved
live flip.** Consistent with the LLM emergence being a lossy/incomplete flip (stays time-side, never produces its
space mirror). See [[framework_three_flips_phi_conservation]].

## Honest fences
n=7 sizes, single passage, one run each; the trend is real (corr +0.78) but **bumpy** (160m dips to 1.24, 410m
reads high at 1.53 because its dominant rung is slow — dominant-rung-pick sensitivity); the **φ-crossing rests on
2 points (2.8b, 6.9b)** — 12B (skipped) would test whether it stabilises at φ or keeps climbing into exothermic.
Dominant-rung ARA flattens a multi-mode wave (per-rung detail in the run log). Data: `Collab_Results/nats_*.npy`.
