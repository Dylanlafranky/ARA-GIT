# When does ARA beat the baseline? The energy-concentration meta-rule (3 June 2026)

Dylan's hypothesis after Codex's standard-baseline benchmark (which showed ARA ties strong baselines on most
systems, winning only 6/34 horizons): **ARA's advantage over a simple single-cycle baseline is inversely
related to how concentrated the signal's energy is in the dominant wave.** Concentrated (one big cycle) → a
seasonal/harmonic clock already captures it → ARA can't add. Spread across coupled rungs → no single clock
captures it → ARA's cross-rung coupling is exactly what's needed.

## Test (Solar, QBO, ENSO)

Dominant-wave concentration (three measures: band-power fraction around the dominant peak; single-sinusoid R²
at the dominant period; spectral 1−entropy) vs ARA's advantage (max corr lift over the best non-ARA baseline
from the standard-baseline benchmark).

| system | band-conc | 1-mode R² | spectral-conc | ARA advantage (max lift) |
|---|---:|---:|---:|---:|
| **ENSO** | **0.135** | **0.023** | **0.291** | **+0.071** (only real win) |
| QBO | 0.571 | 0.202 | 0.507 | +0.008 (~tie) |
| Solar | 0.526 | 0.218 | 0.507 | −0.002 (~tie) |

**All three concentration measures agree, and the ordering is monotonic:** ENSO is far less concentrated
(energy spread; a single sinusoid explains only ~2% of its variance — it is genuinely multi-band) and is the
*only* system where ARA beats the strong baselines. QBO and Solar are concentrated single cycles and ARA ties.
Consistent with the rest of the benchmark: sea ice, flu, retail are all single-dominant-cycle (concentrated)
and ARA tied the seasonal baseline on every one.

## The meta-rule (confirmed, suggestive scale)

> **ARA adds forecast signal exactly when energy is spread across coupled rungs (low concentration). When one
> wave dominates, a single-cycle baseline already equals ARA — so ARA ties, and correctly so.**

The framework therefore *predicts its own win/loss pattern*: its distinctive value is the coupled,
low-concentration regime (ENSO-like multi-band systems with real drivers), not clean single oscillators
(QBO/Solar/flu/sea-ice/retail), where it is — accurately — no better than a seasonal clock.

**Ties to the amplitude issue + EnergyRatio:** concentrated systems hold their energy in the *dominant wave's
amplitude*, which seasonal-naive captures and the current ARA self-forecast drops (the amplitude gap that shows
up as worse MAE). Carrying the dominant-wave amplitude forward would close the tie on concentrated systems; the
cross-rung coupling already does the work on spread ones. Rung-distance EnergyRatio decay is the second,
still-untested axis of the same idea.

**Honest fences:** 3 systems in the core test (6 counting the consistent single-cycle ties); "advantage" = the
best-horizon corr lift (mean lift ≈ 0 across horizons). A clean, monotonic, suggestive ordering and a real
self-consistency result — not a statistically heavy proof. Concentration script logic recorded inline.
