# ENSO energy through the pipe, overflow, and the sphere-position residence law (4 June 2026)

ARA framework · Dylan La Franchi & Claude. Strict-causal, real data (NOAA NINO3.4 1870+, ERSST PDO,
WWV, NOAA DMI/IOD, SILSO sunspots, CPC QBO). This document records the "look at the channel before
predicting through it" arc: how much energy fits through the pipe, where each subsystem stores it, how
saturated rungs overflow, and how the residence (well/ridge) landscape is set by sphere position.

Scripts: `TheFormula/ara_enso_energy_pipe_breakdown.py`, `plot_enso_energy_pipe.py`,
overflow + wells in `/tmp` runs (logic captured below); figures
`TheFormula/ARA_enso_energy_pipe_breakdown.png`.

---

## 1. Pipe capacity — how much fits through at once

Framework pipe model (EnergyRatio/THE_BEDROCK_REFERENCE.md): a **Space pipe of width 2** hands into a
**Time pipe of width φ**, so the maximum head-on through-share is **φ/2 = 0.809** of the channel; the
remaining **1 − φ/2 = 0.191** is shed/recycled. That is the theoretical "at once" capacity.

**Measured (φ-rung ladder 12·φ^k months, energy = variance of causal bandpass):** NO ENSO subsystem
fills the pipe. Dominant-rung energy fractions: WWV 0.42 (fullest), NINO 0.32, SOI 0.29, IOD 0.31,
WWVe 0.25, PDO 0.26 — all **well under the 0.809 saturation line.** ENSO's energy is spread across
rungs, never saturating one. **This is the geometric root of the concentration meta-rule**: spread
energy ⇒ headroom ⇒ cross-rung coupling has work to do ⇒ framework adds signal. A clean clock that
pushed one rung past 0.809 (QBO, solar) leaves the framework nothing to add — exactly the observed
tie on those systems.

## 2. Wave breakdown — each subsystem feeds the rung it lives on

Energy-per-rung location maps one-to-one onto the empirically-found forecasting roles:
- **IOD peaks at the fast 19-mo rung** → lifts short/mid horizons (the fast donor).
- **PDO peaks at the slow 133-mo rung** → holds long horizons (the slow clock).
- **WWV and NINO both peak at the 51-mo ENGINE rung** → WWV literally is the engine's energy reservoir.

The IOD-short / PDO-long stitch we found empirically over many tests is **geometrically inevitable** —
each feeder helps at the horizon where its energy sits. NINO's rung cascade *rises into* the engine rung
then drops by **0.25 ≈ 1/φ³** to the rung above it (a golden-power shed packet, not arbitrary).

## 3. Overflow — saturated rungs spill UP toward the 2.0 singularity

Adjacent-rung energy-envelope cross-correlation (NINO): the **faster rung leads the slower** at every
step through the engine band (lags +7, +10, +14, +2 mo; corr 0.2–0.5). Saturation-conditioned (rung in
top 20% of its energy): the **next-up rung gains while the next-down rung loses** at every rung
(e.g. 31-mo full → 51-mo +0.07σ, 19-mo −0.48σ). So when a pipe fills, energy breaks through **upward**
toward the wider/slower tube — the φ-tube breakthrough mechanism in real data.

**Threshold = 2.0, not 1.5.** Engine-rung instantaneous ARA: mean 1.00, 95th pct 1.68, **max 1.91** —
it blows past 1.5, past φ, and climbs toward (but never reaches) the **2.0 harmonic singularity**. The
overflow happens as the rung crosses past φ on its way to 2.0. Caveats: couplings modest (0.1–0.5),
gains small; the decadal top (133→215 mo) inverts (slow leads), so "always up" holds through the engine
band, not at the PDO-scale top.

## 4. Gravity wells are NOT at 0.25/1.75 — they track sphere position

Tested Dylan's "wells on each 0.25 end" via ARA residence (1+tanh(z/2)) vs a phase-randomized surrogate
(same spectrum). The literal 0.25/1.75 wells are **NOT supported**: 0.25 is *avoided* (−0.12, a barrier);
1.75 is flat (~0, slow-transit but no clear dwell). What the data shows instead:
- **ENSO dwells low (0.5–0.9, +0.16–0.20) and spikes near 1.93** (the 2.0 pole), avoiding the **φ-ridge
  (1.33–1.62, −0.14 to −0.17)** — φ is a *ridge it shoots through*, confirming "φ = the unlockable
  handover/breathing gap." The low-dwell/high-spike asymmetry is ENSO's real El Niño/La Niña skew.

### The law (Dylan's synthesis): the residence landscape inverts with sphere position
Residence excess by system position (low 0.5–0.9 / φ-ridge 1.3–1.6 / high 1.8–2.0 / skew):

| system (position) | low | φ-ridge | high | skew |
|---|---|---|---|---|
| ENSO (engine) | +0.11 | −0.11 | +0.06 | +0.48 |
| Sunspots (flywheel 1.73) | +0.29 | −0.17 | +0.12 | +0.91 |
| QBO (clean clock) | −0.10 | **+0.44** | −0.07 | −0.28 |

**Engines dwell at the poles and avoid/transit φ; the clock dwells AT φ/middle and avoids the poles —
the same location is a ridge for an engine and a well for a clock.** It scales: the more engine-like and
skewed (sunspots), the deeper the low well and sharper the high spike. So φ is not intrinsically a
well or barrier — **its role is set by the system's position on the topographic sphere.** "Everything is
a gradient determined by position on the sphere" — confirmed directionally (n=3; amplitude-residence,
spectrum-controlled).

## 4b. Spin-rate wobble — real wave, but NOT feeder-steered (4 June 2026)

Dylan: spin SPEED set by GCS position (confirmed earlier); spin DIRECTION may wobble toward whichever
feeder is feeding most at that moment (precession, not a flip) — reintroducing the layered-sand wobble,
itself an ARA-wave. Tested on ENSO engine instantaneous phase velocity (spin rate) vs feeder dominance.

- **Spin-rate wobble is REAL and is its own wave:** dominant period ~60mo (ENSO's own engine scale),
  mean ARA **1.04** (balance/CLOCK-class), symmetric (rise-fraction 0.52). So the wobble re-enters as a
  near-balance clock-wave nested inside the engine — Dylan's "wobble is an ARA in itself" CONFIRMED.
- **It tracks COLLECTIVE feeder loudness, not direction:** raw corr(wobble, fast-weighted feeder pull)
  = +0.21, but this is entirely the common mode (when feeders are loud together, engine spins faster).
- **The DIRECTIONAL claim FAILS:** removing the common mode (relative dominance = each feeder's energy
  minus the across-feeder mean), corr(wobble, relative fast-tilt) = **+0.007** (zero). Spin-rate when
  each feeder is *relatively* dominant is scattered (IOD −0.003, SOI +0.026, WWV −0.025, PDO +0.009);
  corr(feeder frequency, spin-when-dominant) = **+0.04** (a clean directional law would be +1).

**Verdict:** the engine has a genuine spin-rate wobble that is its own clock-class (~60mo, ARA~1.0)
nested wave, and it speeds up with TOTAL feeder energy — but it does NOT steer/precess toward the
dominant feeder. Feeders modulate the engine's amplitude/energy (loudness → faster spin), they do not
redirect it. Consistent with the session theme: the engine's own dynamics carry the structure; feeders
shape energy, not direction. Script: `/tmp/wobble.py`, `/tmp/wobble2.py`.

## 5. How it all ties together
ENSO is an engine → it lives at the poles and transits φ fast → its energy spreads across rungs (pipe
never saturates) → its phase sweeps rather than lingers. That single fact is why (a) the engine-phase
clock can call its turns (~0.73 direction @18–24mo), (b) the energy has headroom for cross-rung coupling
(framework adds signal where energy is spread), and (c) feeders work exactly at the rung their energy
occupies. The residence landscape, the pipe headroom, and the direction-skill are one fact seen three ways.

**Open next:** add a heart-RR engine and a true integer-resonance clock to test whether the
engine-poles / clock-middle inversion holds as a law; measure per-breakthrough packet size at the 2.0
threshold (transfer capacity vs storage capacity).
