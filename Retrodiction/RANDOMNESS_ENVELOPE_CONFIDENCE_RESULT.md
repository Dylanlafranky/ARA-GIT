# Randomness as a variable constant — energy predicts the confidence, not the value (4 June 2026)

ARA framework · Dylan La Franchi & Claude. Strict-causal, feeder-era ENSO (NINO3.4 + SOI/WWV/IOD, 1980+).
Script: `/tmp/randconst.py`. Best forecast = engine clock (55mo) + home-AR + raw SOI/IOD feeders, golden split.

**Dylan's reframe:** the predictability ceiling feels like a *barrier* — the full random effect, like the
lotto (ARA=1.0 shock absorber, singularity IS the structure). Idea: counter it by using the randomness
itself as a *variable constant* — you can't predict the random value, but if its SIZE is structured you
can fold that in.

## Result — confirmed, three parts

1. **The residual is the random shock-absorber.** Forecast residual (truth − prediction) has **ARA = 1.00**
   — the lotto/singularity signature. The unpredictable core is genuinely structureless in *value*; the
   barrier is real and irreducible (you can't forecast it any more than a lottery draw).

2. **Its MAGNITUDE is predictable — from ENERGY.** |residual| (the randomness envelope) is forecastable at
   **corr +0.25** from energy features (engine amplitude + SOI/IOD energy envelopes + season) — the *same*
   energy that FAILED to predict the value. Resolution: **phase predicts the value; energy predicts the
   randomness envelope.** Energy tells you not *what* ENSO does but *how unpredictable* it will be.

3. **The envelope is a usable trust score.** Splitting the test set by the predicted randomness envelope:
   - overall forecast corr **+0.24**
   - **high-confidence half (low predicted randomness): +0.37**
   - low-confidence half (high predicted randomness): +0.16
   The high-confidence forecasts land at **>2×** the low-confidence ones. You can't beat the barrier, but
   you can *read* it and know in advance which forecasts to trust.

## Session synthesis (clean)
- **Phase → value** (direction/correlation skill; engine clock + feeders)
- **Energy → confidence** (the randomness-envelope size; when to trust)
- **Residual core = ARA 1.0** — a real randomness barrier, same singularity as the lotto: characterizable,
  not penetrable. ([[project_randomness_lotto]])

## Amplitude addition — DONE, small consistent lift at mid-long horizons
Applied the envelope as an amplitude modulator: (truth−cur) ~ a·dev + b·(dev·envelope), envelope =
predicted |residual| from energy+season (fit on train). Lets the predicted swing grow when the envelope
says a big deviation is coming. Strict-causal, golden split.

| h | base corr | +amplitude | gain |
|---|---|---|---|
| 3 | 0.827 | 0.828 | ~0 |
| 6 | 0.542 | 0.541 | ~0 |
| 9 | 0.309 | 0.323 | +0.014 |
| 12 | 0.240 | 0.246 | +0.006 |
| 18 | 0.330 | 0.340 | +0.010 |
| 24 | 0.218 | **0.235** | **+0.017** |

**Outcome:** small but consistent correlation lift at 9–24mo (flat at short range, where amplitude is
already captured). MAE roughly neutral. The mechanism closes end-to-end: energy predicts the randomness
envelope → scale the swing by it → correlation rises exactly where the base forecast mean-reverts/floors
the amplitude. Gains ~+0.01–0.02 (near noise floor) but in the predicted direction at every horizon with
room. You can't predict the random value; reading its envelope buys back a little of the mean-reverted
amplitude. Script: `/tmp/amp.py`.
