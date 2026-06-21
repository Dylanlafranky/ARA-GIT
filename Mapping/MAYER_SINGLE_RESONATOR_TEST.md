# Mayer wave: single resonator vs coupled pair — real-data test

**2026-06-21.** Tests Dylan's hypothesis that the Mayer wave's clock-like ARA~1 might arise from
**two sub-systems resonating** (Route B: a coupled-pair cancellation ridge) rather than a single
baroreflex resonance (Route A: one delayed-feedback loop ringing). Both read ~1.0 on a whole-signal
ARA; the discriminator is the **spectrum** — one sharp Lorentzian (single resonator) vs two
reproducible peaks (coupled pair).

## Data
PhysioNet **Autonomic Aging** database (autonomic-aging-cardiovascular), continuous noninvasive
arterial BP (NIBP, 1000 Hz, ~15 min). Records 0001, 0005, 0010. Beat-to-beat systolic BP extracted,
resampled to 4 Hz, detrended; Welch PSD; single- vs double-Lorentzian fit tight around the Mayer band.

## Result

| Subject | Mayer peak | Q (sharpness) | within-Mayer 1-vs-2 |
|---|---|---:|---|
| 0001 | 0.11 Hz | **9.6–28 (high)** | single, sharp |
| 0005 | 0.06 Hz | 2.7 (broad) | "double" but unstable |
| 0010 | 0.06 Hz | 3.9 (broad) | tie, unstable |

- Where the Mayer wave is **well-defined (0001, high Q)** it is an **unambiguous single resonance**
  (Route A). Where it is weak/broad (0005, 0010) the fitter sometimes splits it, but the split
  frequencies **wander between subjects** (0.06+0.12, 0.087+0.113, 0.062+0.105) — the signature of
  fit-noise on one broad peak, **not** two stable reproducible engines.
- **Coupled-pair (Route B) NOT supported**: no reproducible twin frequencies appear.

## The better picture (Dylan's instinct, corrected)
Every subject shows a **ladder of distinct autonomic resonances = rungs**:
- VLF ~0.023 Hz (43 s, myogenic/thermoregulatory)
- **Mayer ~0.07–0.11 Hz (baroreflex)** — the node in question
- Respiration ~0.17–0.28 Hz — a separate, reproducible peak in all three

So multiple sub-systems are real, but they sit at **different rungs** and do **not** cancel into the
Mayer clock. The Mayer wave is its own **single resonator**; respiration is the genuinely independent
neighbor (the real "second oscillator"), at a clearly different frequency.

## Framework takeaway
A worked example distinguishing the **two kinds of ARA~1**:
- **Genuine single-resonator 1.0** (this — a real damped/harmonic clock; the baroreflex loop). One
  sharp Lorentzian, high Q.
- **Coupled-pair cancellation 1.0** (the "sea-level ridge" artifact that bit the LLM whole-signal
  averaging). Two reproducible peaks under the ridge.
Both read 1.0 on a whole-signal ARA; the **Lorentzian/Q test separates them**. Mayer is the first kind.

## Caveats
n=3; 15-min records give limited LF resolution (~0.008 Hz), so fine structure under a broad peak
cannot be excluded — only that no reproducible twin shows up. Script: BP→SBP→Welch→Lorentzian AIC.
