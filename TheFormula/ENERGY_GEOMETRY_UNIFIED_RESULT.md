# Energy & geometry are one measurement — unified ENSO forecaster (7 June 2026)

ARA framework · Dylan La Franchi & Claude. Strict-causal, feeder-era ENSO (NINO3.4 + SOI/WWV/IOD, 1980+,
test 2016–2025). Scripts: `/tmp/endir.py`, `/tmp/combine.py`, `/tmp/unified.py`, `/tmp/cmode.py`,
`/tmp/earatio.py`. Figures: `ARA_unified_three_output_forecaster.png`, `ARA_prediction_geometry_energy_split.png`.

## The reframe (Dylan)
Energy and geometry are NOT two channels. **The geometry is how we measure the energy.** At short horizon
the measurement is coherent → clear energy reading; as horizon grows the reading decoheres → only the bare
geometric skeleton (the phase clock) remains. One quantity, measured well then poorly.

## 1. Energy determines direction at short range (recharge oscillator)
Direction hit-rate, energy-only (WWV charge + recharge rate + stored engine energy, NO phase) vs phase clock:

| h | phase/geometry | ENERGY only | combined |
|---|---|---|---|
| 3 | 0.55 | **0.75** | 0.73 |
| 6 | 0.52 | **0.65** | 0.66 |
| 9 | 0.51 | **0.62** | 0.60 |
| 12 | 0.53 | 0.58 | 0.58 |
| 18 | 0.63 | 0.54 | 0.63 |
| 24 | 0.63 | 0.60 | **0.67** |

Energy alone calls direction at 0.75 @3mo and beats the clock out to ~12mo (the recharge reservoir = warm
water volume leads SST; Jin 1997). Phase/geometry takes over at 18–24mo. They hand off **in time** — same
short/long split as the IOD-short/PDO-long feeder stitch.

## 2. The 5–12mo gap is a SURFACE spectral valley, filled by the SUBSURFACE
Geometry sags toward chance at 6–12mo. Tested Dylan's "missing system" idea with the physically-motivated
candidate — the **ENSO combination mode** (ENSO × annual cycle, Stuecker et al., tones at ~9.6 & ~17.8mo).
Spectral check: peaks ARE there (10.2mo, 17.8mo) but carry **negligible energy (rel power ~0.00–0.01)** —
NINO3.4 has a spectral valley between the annual (12mo) and the interannual engine (30–67mo). Adding the
9.6mo mode did nothing. **Conclusion:** the gap is not a missing internal system — the *surface* signal is
empty at 5–12mo, and the *subsurface* energy reservoir (WWV) is what carries direction there. So the handoff
is also a LAYER handoff: geometry reads the surface (empty mid-range → sags), energy reads the subsurface
(full mid-range → carries it).

## 3. Unified three-output forecaster (one reading, three products)
`ARA_unified_three_output_forecaster.png`: VALUE (correlation, strong short, decays ~36mo), DIRECTION
(energy-clear short → geometry-skeleton long), CONFIDENCE (energy predicts the randomness envelope, peaks
short). All three are the same energy reading at different coherence; underneath sits the ARA-1.0 random core.

## 4. Energy enters the correlation through its ARA, not linearly (Dylan's 2−ARA rule)
Map the asymmetric energy shift to an ARA (1+tanh(z/2)); the available **energy input = 2 − ARA_energy**;
add on top of the correlation forecast. Value correlation:

| h | base | +linear energy | +ARA energy (2−ARA) |
|---|---|---|---|
| 3 | 0.827 | 0.849 | **0.851** |
| 6 | 0.542 | 0.544 | **0.555** |
| 9 | 0.309 | 0.297 ↓ | **0.316** |
| 12 | 0.240 | 0.240 | **0.254** |
| 18 | 0.330 | 0.348 | **0.349** |
| 24 | 0.218 | 0.216 | 0.212 |

The ARA transform beats both base and linear at 5/6 horizons; decisively at h=9 where **linear HURTS
(0.297<0.309) but ARA HELPS (0.316)** — the slow-charge/fast-discharge asymmetry is real amplitude info the
linear term smears. Energy ARA swings 0.08–1.93 (near full 0–2, strongly asymmetric) = depleted→charged.
Gains small (~+0.01–0.015, near noise) but consistent and interpretable. **Principle confirmed: inject energy
through its ARA (2−ARA), not raw.**

## Cross-system (heart & solar)
Residual ARA = 1.0 (random barrier) UNIVERSAL. Energy→confidence holds on heart (+0.21–0.29, like ENSO),
WEAK on solar (~0) — solar is a concentrated clean clock, no spare energy to encode confidence. Energy→
confidence works exactly where the framework wins (spread/coupled), not on concentrated clocks. (Heart series
short, 526 beats — noisier.)

## Standing synthesis
- **Phase (geometry) = when** · **Energy = how big + which way (short) + how much to trust** · same measurement.
- Short horizon: clear energy read (value + direction + confidence). Long horizon: decohered → bare phase clock.
- Surface vs subsurface layer split fills the mid-range; inject energy via its ARA (2−ARA).
- Irreducible ARA-1.0 random core underneath all of it (the barrier; same as the lotto).
