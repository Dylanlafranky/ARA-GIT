# Neural scaling law — is it the golden shed (2−φ)?  TEST RESULT: NO (not pinned)

**Dylan La Franchi & Claude, 14 June 2026.** Done properly after the substrate-ARA method fix.

## The right quantity
The scaling law is a **monotone curve** (loss = bits/token vs compute), not an oscillation — so the canonical
`ara_mapper.py` (which reads rise/fall cycles) does **not** apply to it. The scaling law's analogue of the
ARA "shed" is the **per-handover forward/shed split**: per compute-DOUBLING (one octave rung), the reducible
loss multiplies by 2^(−α), so the fraction *forwarded* = 2^(−α) and the **shed = 1 − 2^(−α)**, where α is the
power-law exponent. Golden target: shed = 2−φ = **0.382** (forward 0.618).

## Result — across all 8 Pythia-deduped sizes (lambada-ppl, reducible-loss fit, step≥1000)
| size | shed @best-fit floor | @E=0 | @E=1.5 |
|------|------|------|------|
| 70m | 0.046 | 0.046 | 0.055 |
| 160m | 0.090 | 0.090 | 0.114 |
| 410m | 0.144 | 0.144 | 0.196 |
| 1b | 0.141 | 0.141 | 0.206 |
| 1.4b | 0.320 | 0.159 | 0.239 |
| 2.8b | 0.350 | 0.177 | 0.276 |
| 6.9b | 0.352 | 0.202 | 0.328 |
| 12b | 0.361 | 0.204 | 0.348 |

Big-model converged shed (2.8b/6.9b/12b, best-fit floor) = **0.354**.

NULL — which constant does 0.354 pick?
```
1/e   0.368  |Δ|=0.013   ← closest
1/3   0.333  |Δ|=0.021
2−φ   0.382  |Δ|=0.028   (golden, third)
2/5   0.400  |Δ|=0.046
1/2   0.500  |Δ|=0.146
```

## Verdict: NOT the golden shed
Three independent reasons the golden-shed claim does **not** hold:
1. **Not a constant** — the shed is strongly SIZE-dependent (0.05→0.36); it's a large-model asymptote, not a
   universal value sitting at 2−φ.
2. **Not robust** — it's FLOOR-sensitive (0.20 at E=0 → 0.35 at best-fit floor). The per-octave shed isn't
   well-defined without committing to the irreducible-entropy floor E, and E is itself fit from the same curve.
3. **Null picks against φ** — even at the most golden-favourable setting (0.354), the nearest clean constant is
   **1/e (0.368)**, then **1/3**, with **2−φ third**. And the published Kaplan/Chinchilla loss exponents
   (≈0.05–0.35, all below our proxy's ≈0.63) would push the shed FURTHER below 0.382, not toward it.

So: the scaling law **is** information accounting (loss = bits/token — definitionally true), but its
per-handover shed is **~0.18–0.36 depending on the floor, closest to 1/e, not the golden 2−φ.** This
**confirms the earlier scratch** ("scaling-law-in-ARA clock 1.08" SCRATCHED) and the standing note that
2−φ is **not** reproducible as a scaling exponent (α 0.05–0.64 by size).

## What would make it definitive (not yet run)
The killer is the floor. To settle it you'd need the **true training-loss curve** (not the lambada-ppl
downstream proxy) with a **principled irreducible floor** = the dataset's per-token entropy (measurable
independently), rather than a floor fit from the same curve. OLMo publishes full training-loss logs; that's
the clean follow-up. Until then: **2−φ in the scaling law is NOT shown.**

---

## Apples-to-apples: the scaling law AS an ARA value (14 Jun, follow-up)
Dylan asked to put the scaling law itself on the 0–2 ARA scale to compare with the substrate (~1.25).

> ### ⚠️ SCRATCHED — "scaling law ARA ≈ 1.0 (clock)" — DO NOT USE (14 Jun, Dylan caught it)
> **RESOLVED (same day):** the line has no honest ARA (below, still true) — but that was the wrong object. Measuring **what they measured** (per-token bits = the BASE WAVE the loss averages) gives a clean canonical ARA ≈ **1.36–1.44 (engine-leaning)**, same band as the substrate. See `LLM_SCALING_LAW_BASE_WAVE_ARA.md`. The clock was always a flattening artifact.
> The clock placement below was a **double-log artifact**. To get the "clean power law R²≈0.99 = clock," I fit
> `log(step)` vs `log(reducible BITS)` — but **bits is already `log₂(perplexity)`**, so that's a SECOND log on
> the y-axis. The straight line (hence "clock") is **manufactured by the extra log**, not a property of the
> process. Same trap as the originally-scratched "1.08" (linear axis → consumer ~0; log axis → clock). Calling
> the octave ruler "canonical" excuses the x-axis log, NOT the second y-axis log.
>
> **Deeper reason it's unfixable:** a **monotone** curve has **no axis-independent ARA** at all — ARA is the
> asymmetry of a *cycle* (accumulation vs release), and the scaling law has no cycle. Every value is a
> representation artifact: linear→consumer(~0), bits-vs-octave→curved exponential relaxation, double-log→clock.
> There is **no honest single ARA for the scaling law.**
>
> **The framework-correct statement:** the scaling law is **not an engine — it's the exhaust** (the recorded
> shed-trail / processed accounting of loss let go over compute). You don't take the ARA of the tide-gauge
> logbook; you take it of the tides. **The ARA lives in the SYSTEM (substrate ≈ 1.25), not in its accounting
> record.** The only units-grounded thing the scaling law yields is the **shed fraction (~1/e per octave, in
> bits)** — and even that needs the octave + floor choices — which is **NOT golden 2−φ.** That shed result
> (above) stands; the ARA-value placement does not.

~~**The principled placement:** octave axis → clean power law R²≈0.99 → Scaling law ARA ≈ 1.0 (CLOCK), tick
≈1/e.~~ **SCRATCHED — double-log artifact (see banner). The scaling law has no honest ARA value; ARA lives in
the substrate (~1.25), and the scaling law's only honest content is the non-golden 