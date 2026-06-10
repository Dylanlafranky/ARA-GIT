# The prediction window reopens at one engine cycle; the second wave = geometry in reverse (7 June 2026)

ARA framework · Dylan La Franchi & Claude. Strict-causal, real NOAA NINO3.4 (1870+), universal
`ara_forecast`. Script: `Retrodiction/plot_second_window.py`. Figure: `ARA_enso_second_window.png`.

## Finding 1 — direction is a STANDING capability, not a horizon-limited one
Forecast skill measured at horizons 1–72 months:
- **Shape/direction skill (change-corr) barely decays:** +0.64 (6mo) → peak +0.75 (18mo) → dips only to
  **+0.59 at the ~30mo wall** → recovers to **+0.66 out to 72 months (6 years).** There is essentially
  **no wall for direction** — the engine cycle keeps "which way it turns" callable indefinitely.
- This reframes the "predictability wall": it's a wall for the *exact value*, not for direction.

## Finding 2 — the value-coherence window REOPENS at one engine cycle (Dylan's intuition, confirmed)
Value correlation by horizon:
- First window: +0.53 (6mo), the familiar near-term skill.
- **Dies and goes NEGATIVE at ~30–32mo (−0.16)** — the decoherence wall; the forecast actively misleads.
- **Recovers and peaks again at ~55–57mo — exactly one engine cycle (~55mo)** — reaching **+0.13**, then
  fades after one period.
- So the predictable structure is not gone forever past 2 years; it **re-phases at one engine cycle and a
  second (smaller) window opens** — "where that part of the topographic sphere comes back around" (Dylan).
  Modest (+0.13 vs +0.53) because each cycle the ARA-1.0 random core erodes more of it.

## Finding 3 (hypothesis to test) — we have ONE wave; the second wave is the geometry IN REVERSE
Dylan: "we have half of the topographic sphere — one wave right, but not the second A and the handover,
and the handover should be the ARA of the system." And crucially: **the second wave should be the same
geometry but in reverse.**
- We forecast with ONE wave (the gold engine, forward). A single wave decoheres — its amplitude/phase
  smears each cycle (the random core leaking in) → the value-corr decay and the only-+0.13 second window.
- The **second (anti-phase) wave = the SAME engine geometry run in REVERSE** — which is exactly the
  Retrodiction result (the forward predictor on reversed time IS the reverse engine clock). So the two
  waves of the sphere are **forward geometry + reverse geometry.**
- The **handover between them happens at the system's ARA** (φ = the handover/breathing gap in the
  framework; the ARA position is where the two waves exchange).
- HYPOTHESIS: modelling the second wave (reverse geometry) and timing its handover to the ARA could let
  the two waves **re-cohere each other at the handover** — refilling the coherence a single wave loses,
  filling the ~30mo decoherence trough and/or strengthening the cyclic second window.

## Finding 4 — SIX attempts to fill the trough, ALL fail: it's a clock-locked physical floor
Tested whether the ~30mo value-coherence trough can be filled. Every attempt verified on the real
`ara_forecast` feature set (reconstruction matches ara_forecast to 0.00e+00):

1. **Reverse the same wave** (cos(θ−2πh/P)): mathematically REDUNDANT — already spanned by the formula's
   forward cos/sin. Identical results (−0.1340 → −0.1340).
2. **Reverse HEMISPHERE / anti-phase partner (SOI)**: +0.002 at the trough = nothing. SOI is the
   atmospheric MIRROR of the same ENSO wave (~−0.9 corr), LOCKED to the same clock, so it decoheres on the
   same schedule.
3. **Slow driver above (PDO, solar)**: null (tested earlier sessions).
4. **Clock-swap @ half-cycle** (two regime models, rising vs falling): HURTS (−0.036 at trough) — splitting
   data halves the training set → overfits.
5. **φ-handover** (swap at 0.618 of the combined NINO+SOI cycle, run to cycle end, hand back): worst of all
   (−0.218 at trough).
6. **Handover-point sweep** (0.382 / 0.5 / 0.618 / 0.82=ARA): NONE beat the single model; every split hurts.

**Conclusion (robust):** the handover TIMING was never the issue — there is nothing INDEPENDENT to hand
over to. The "two waves" are the same oscillation on the same clock; any phase-timed split just halves the
data and overfits. Everything tied to the ENSO clock — its reverse, mirror, anti-phase partner, slow
envelope, or any φ/ARA-timed regime split — decoheres WITH it. **The ~30mo trough is a genuine physical
floor (the spring predictability barrier / ARA-1.0 random core); only a truly independent pacemaker could
fill it, which ENSO does not appear to have.** The framework honestly delivers: near-term value window +
standing direction skill + small second window at one engine cycle + an unfillable trough between.
Sweep script: `/tmp/sweep.py`, `/tmp/phihand.py`, `/tmp/hemi.py`, `/tmp/swap.py`.
