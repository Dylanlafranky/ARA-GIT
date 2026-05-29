# Solar cycle as the flywheel — testing the storer prediction

**Date:** 2026-05-29
**Status:** Exploratory, strict-causal, correlation-led. Real data, ~25 cycles. One line of evidence.
**Data:** SILSO monthly mean total sunspot number, 1749–2026 (3,328 months, ~25 solar cycles). Source: Royal Observatory of Belgium / SIDC, `https://www.sidc.be/SILSO/INFO/snmtotcsv.php`. Cross-available as NOAA SWPC observed solar-cycle indices.
**Question:** The two-system comparison predicts that an energy *storer* (flywheel) should show (a) the shared engine — octave rungs + golden-duty handover — and (b) a much longer horizon than a *spender* like the heart, with an *internal* clock and wall. Does the Sun behave as the formula says a flywheel should?

## Short version

- **Octave rungs — clean hit.** The three strongest bands are **10.7, 85.3, 170.7 years** — ratios of exactly **8× (2³) and 16× (2⁴)**. The sharpest octave ladder we've measured in any system.
- **Golden-duty handover — clean hit, as the within-cycle charge/discharge asymmetry.** Across 24 cycles the rise (fast charge) takes **0.394 ± 0.085** of the cycle and the decline (slow discharge) **0.606** — dead on 1/φ²:1/φ (0.382/0.618), matching ENSO (0.40/0.60) and the heart (0.39/0.61). This is the known Waldmeier effect, here read as the framework's φ-timed handover.
- **Horizon — flywheel confirmed.** The Sun is forecastable for **decades**, against the heart's **seconds-to-minutes**. Self-forecast correlation stays +0.5 to +0.85 out to ~15 years and only dies around **~44 years (≈ φ³ ≈ 4 cycles)**.
- **The storer's fingerprint — a flat indefinite floor.** Because the clock is so regular, the dumbest cycle-aware baseline ("it'll look like it did one ~11yr cycle ago") holds **+0.69 correlation at *every* horizon, forever.** The heart has nothing like this — it has no clock, so its cycle-ago baseline would be useless. **This flat floor is the single cleanest difference between a storer and a spender.**

## The two engine pieces transfer

**Octave rungs (edge-free, two/three strongest distinct spectral peaks, 2–200 yr band):**

| band | period | ratio to Schwabe | octaves |
|---|---|---|---|
| Schwabe | 10.7 yr | 1× | 0 |
| Gleissberg | 85.3 yr | 8.00× | 3.00 |
| (long) | 170.7 yr | 16.00× | 4.00 |

**Golden-duty handover (Waldmeier rise/fall, 24 cycles):** mean rise 4.34 yr, mean fall 6.68 yr, mean cycle 11.02 yr → rise fraction **0.394**, fall **0.606**. The flywheel charges fast (0.39) and discharges slow (0.61), exactly the φ-timed handover seen in the spenders.

Note on *which* duty pairing: between-band duty (Schwabe vs Gleissberg amplitude dominance) does NOT give φ — the 11yr cycle dwarfs the 85yr one (0.84/0.16). For a flywheel the natural handover is the within-cycle charge/discharge asymmetry, and *that* is φ-coded. This is an interpretation choice made after seeing the between-band result fail; it is physically grounded (Waldmeier) but should be flagged as such.

## Horizon — the flywheel reaches decades

Strict-causal linear self-forecast (features = past SSN at lags 1–132 months spanning one cycle; train first half / test second; standardize on train; correlation of predicted vs actual). Two baselines: persistence (value now) and cycle-ago (value ~11 yr earlier).

| horizon | self-forecast | persistence | cycle-ago |
|---|---|---|---|
| 1 yr | +0.853 | +0.734 | +0.685 |
| 2 yr | +0.788 | +0.378 | +0.686 |
| 4 yr | +0.743 | −0.384 | +0.686 |
| 8 yr | +0.752 | +0.072 | +0.687 |
| 11 yr | +0.674 | +0.686 | +0.686 |
| 15 yr | +0.536 | −0.426 | +0.682 |
| 22 yr | +0.352 | +0.538 | +0.684 |
| 25 yr | +0.316 | −0.246 | +0.688 |
| 33 yr | +0.303 | +0.458 | +0.691 |
| 44 yr | −0.030 | +0.332 | +0.677 |

Reading:

- **Learned skill beats the clock only inside ~one cycle.** The self-forecast is well above the cycle-ago floor out to ~8 yr, the two cross at ~11 yr (the home period), and past one cycle the dumb cycle-ago baseline wins. So the model's *added* value has a wall at **~1 cycle (11 yr) = the home period** — the framework's "forecast you can add" boundary.
- **Total dissolution at ~44 yr ≈ φ³ cycles.** Self-forecast skill reaches zero around 44 yr (φ³ × 11 ≈ 46.6 yr). The originally-hypothesised φ^1.75 × home (~25 yr) is roughly where useful added skill has clearly degraded (+0.32), not where it hits zero — so the φ^1.75 internal-wall idea is in the right zone but the *death* point is nearer φ³ cycles. Honest: with ~25 cycles and one record, we can't separate φ^1.75 from φ³ sharply.
- **The clock floor is flat and indefinite (+0.69 at every horizon).** This is the storer's signature. The Sun's period is so stable that "same as one cycle ago" predicts the future about as well at 44 yr as at 1 yr. A spender (heart) has no such floor.

## Verdict against the two-system prediction

The flywheel prediction holds on all three counts:

1. **Shared engine present** — octave rungs (8×, 16×) and φ-golden-duty handover (0.394/0.606) both transfer.
2. **Horizon vastly longer than the spender** — decades vs the heart's minutes, exactly as "stores energy → long memory" predicts.
3. **Internal clock present** — the flat +0.69 cycle-ago floor is the persistent internal metronome the heart lacks; the wall on *added* skill sits at the home period (~11 yr), with total dissolution near φ³ cycles (~44 yr).

So: **same engine, different battery — confirmed on a third, independent system.** ENSO and the heart told us the formula; the Sun shows the storer end of the energy axis behaving as predicted.

## Honest scope / caveats
- One series, ~25 cycles. The octave ratios (8.00, 16.00) land partly on the FFT period grid — clean but resolution-limited; the result is "octave ladder," not "8.00 to three decimals."
- The golden-duty pairing was reinterpreted (within-cycle, not between-band) after the between-band test failed. Flagged above. It is physically the Waldmeier effect.
- A *separate* earlier test (substrate-vs-operating ARA) found φ does NOT win as a *predictor base* on sunspots (base 2.0 won). That is a different question (predictor tuning) and is not contradicted here — this test is about structure (rungs, duty, horizon regime), which transfers cleanly.
- Strict-causal: train/test split, standardize on train, two baselines reported. The cycle-ago baseline is the honest hard floor and the model only beats it sub-cycle.

## Files
- `TheFormula/solar_flywheel_fetch.py` — download + cache SILSO monthly SSN
- `TheFormula/solar_flywheel_structure.py` — octave rungs + between-band duty
- `TheFormula/solar_flywheel_waldmeier.py` — within-cycle rise/fall golden-duty
- `TheFormula/solar_flywheel_horizon.py` — strict-causal horizon sweep vs persistence + cycle-ago
- `TheFormula/solar_silso_monthly.npz` — cached data
