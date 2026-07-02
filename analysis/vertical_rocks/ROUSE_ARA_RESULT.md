# Bagnold/Rouse sediment transport, ARA-ised — the collapse test

**Date:** 1 Jul 2026. **Scripts:** `rouse_ara_test.py` (compute+provenance), `rouse_ara_viz.py` (figure). **Figure:** `rouse_ara_collapse.png`.
**Replicable:** settling via Ferguson & Church (2004) closed form; every grain size / shear velocity / fluid property is a cited public value; deterministic; provenance printed on run.

## Setup
Accumulation = settling/deposition; Release = turbulent suspension/erosion. ARA variable **s = w_s/u*** (fall velocity ÷ shear velocity = κ·Rouse). **Ridge s=1 is empirically the suspension↔saltation transition** ("fall ≈ friction ≈ unity", sourced [M3]) — so the ridge is anchored by real physics, not convention. Deposition (s>1) → ARA>1; suspension (s<1) → ARA<1. 12 systems across air, water, Mars.

## Dylan's prediction — CONFIRMED
He predicted: adjusting for medium and dimension, the systems collapse to a similar ARA structure (self-similarity, echoing the caves↔sinuses test 152).

- **Variance in log s explained by MODE (dimension available to the grain): η² = 0.77**
- **Variance explained by MEDIUM (air/water/Mars): η² = 0.19**

Mode organizes the ARA; **medium washes out.** The collapse is visible directly: the aeolian dune (Earth air), aeolian ripple (Earth air) and **Mars dune** all sit together in the saltation/bed family on the deposition side — despite a 50× air-density difference, different gravity, and different grain size. *A dune is a dune on Earth or Mars* once expressed through the dimensionless ratio. Suspension systems (dust storm-air, turbidity current-water, Mars dust) cluster at the release pole across all three media.

This is the same self-similarity the cave test showed (an Earth void and a skull void predict each other after scale correction) — here, different-medium transport systems predict each other after the Rouse normalization. Medium and dimension adjusted; structure preserved.

## Honest nuance (a real subtlety, not a failure)
The net-depositional *environments* (river-mouth delta, floodplain mud) land on the **suspension** side (low s), not the deposition pole. That's physically correct: their fines only settle when flow stalls; at any finite u* they're still marginally suspended — which is exactly why mud is the last thing to drop. So the true high-s **deposition pole is coarse bedload** (gravel river, alluvial fan, dunes), and "depositional environment" ≠ "instantaneously deposition-dominated." Worth keeping straight.

## Fences
Representative order-of-magnitude grain sizes and shear velocities per environment (cited); Ferguson–Church settling is a validated closed form (sanity-checked: 0.25 mm quartz → 3.2 cm/s in water, 1.75 m/s in air, both match measured); mapping width W is a free convention (sign + ridge are sourced). Mode-vs-medium η² uses n=12 across 5 modes — suggestive, not high-powered.

## Sources
Ferguson & Church 2004 (settling). Aeolian: leovanrijn-sediment.com Aeoliansandtransport2018; USGS Lees Ferry threshold dataset. Fluvial u*: Julien, open-channel texts. Mars: pnas.org/doi/10.1073/pnas.0800202105 (giant saltation); Sullivan 2017 JGR (low-wind saltation); pnas.org/doi/10.1073/pnas.2012386118 (Mars threshold).

---

# Push 2 — more systems, more media, and the MEDIUM WAVE (1 Jul 2026)

**Scripts:** `rouse_ara_expanded.py`, `rouse_ara_master_collapse.py`. **Figures:** `rouse_ara_expanded.png`, `rouse_ara_medium_wave.png`, `rouse_ara_master_collapse.png`.
Expanded to **22 systems across 8 media** (added Venus dense CO₂, Titan liquid methane + Titan air, debris slurry, pyroclastic, blowing snow, subglacial, lahar, loess). Venus/Titan sourced ([V] Magellan/boundary-layer studies; [T] Huygens-condition liquid ρ=615, ν=8.9e-7).

## Still collapses; medium is now a clean secondary signal
- η² MODE = 0.62, η² MEDIUM = 0.28 (n=22). Mode still organizes; medium is an ordered secondary — a real line, not noise. Dylan called this ("a line forming that shows the wave of the medium").

## The medium wave — and an honest correction
Each medium traces **the same S-curve of ARA vs grain size, shifted horizontally** (`rouse_ara_medium_wave.png`): converging at the coarse/bedload end, fanning out toward suspension. Same shape, different position = the self-similar signature.

**Correction (discipline):** I first eyeballed the shift as ordered by *fluid density*. The clean computation says otherwise — density predicts the shift poorly (Spearman ρ=0.29). The shift is **perfectly** ordered (ρ=1.00) by the composite **ν^(2/3)/(Rg)^(1/3)**, which is exactly the standard **dimensionless grain diameter** rescaling D* = D·[Rg/ν²]^(1/3). The density story was wrong; the D* story is exact.

## The master collapse
Plot ARA against the **dimensionless grain diameter D*** instead of real grain size and **all 8 media fall on ONE curve** (`rouse_ara_master_collapse.png`): across-media ARA spread = **0.403 at fixed real grain size → 0.000 at fixed D***. The medium is removed completely by the textbook rescaling. So the fullest statement of your prediction: **adjust for medium via D* (the medium wave), organize by dimension via mode → one universal ARA curve.** Same shape everywhere; medium and dimension only set position — exactly the fractal/gradient picture.

## Fences
Medium-wave curves use u*=1.5×threshold with Bagnold threshold u*t=0.1√(RgD) (sand+; fine/cohesive end approximate). η² n=22 across 5 modes — suggestive. D* collapse is analytic (Ferguson–Church + Shields grain scale), so the 0.000 spread is a mathematical identity of the rescaling, not a fitted result — the empirical content is that real transport systems *sit* on that curve at the D* their environment selects.
