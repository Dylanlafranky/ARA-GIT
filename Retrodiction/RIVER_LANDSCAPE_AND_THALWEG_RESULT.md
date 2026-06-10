# The river landscape: siphons, the conserved φ-thalweg, and the morphed-sphere regime map (9 June 2026)

ARA framework · Dylan La Franchi & Claude. Strict-causal, real public data (NOAA NINO3.4 1870+, SILSO
monthly sunspots, PhysioNet ECG, NOAA PDO/IOD, WWV). All forecasts through the universal
`Retrodiction/ara_prediction_formula.py`. Scripts in `/tmp/` (siphon*, watershed, lanes*, conserved_thalweg,
thalweg_forecaster, regime_map). This documents one long exploratory arc that started from "is there a system
that takes energy OUT of ENSO?" and ended on a validated **regime + confidence map** carved into the state
sphere — with several clean nulls flagged along the way.

**Headline:** The morphed "topographic sphere" is real and useful as a **regime map** (where you sit predicts
*what kind* of behaviour comes next) and a **confidence map** (the conserved φ-thalweg tells you *how much to
trust* the reading). It is **NOT** a better *value* predictor — knowing the terrain doesn't hand you a sharper
number. This is the same lesson the framework keeps teaching: it reads **what kind** and **how much to trust**,
not **what exact value**.

---

## 1. Siphons — ENSO's energy outflow is real but a FOLLOWER (null for prediction)
Directed transfer entropy on engelope-energy, ENSO vs each subsystem (+ = ENSO is the source/loses energy):
- **ENSO → WWV +0.011** (subsurface discharge, the biggest drain), **ENSO → IOD +0.005**, **ENSO → PDO +0.001**.
- **SOI → ENSO −0.011**: SOI is the *anti-phase mirror* (donates, locked to the same clock), NOT a siphon.

So ENSO genuinely sheds a small amount of energy downward (subsurface) and sideways (Indian Ocean) — exactly
the **0.382 = 1/φ² shed** (the small side of the φ handover: 0.618 kept + 0.382 shed). But as a *predictor* it
is null:
- Combined 3-siphon dissipation term added to the forecast: **flat on the long record, HURTS post-1980**
  (h=24 decay skill +0.75 → +0.39).
- Drain-*rate* carries the right-sign decay signature (filling drains → ENSO falls next, **−0.12 @3–6mo**) but
  it is **redundant with ENSO's own memory lags** — a downstream drain is a delayed echo of the source's past.
- As a **wobble** controller (gear/gap idea): in-sample the gap-imbalance led the wobble (+0.18) but it
  **failed split-half replication** (+0.28 → −0.11) and the OOS ridge flipped to −0.32. Null.

**Lesson:** anything that merely *receives* from ENSO is a follower; it can confirm the energy budget balances
but cannot lead/sharpen a forecast. To beat the wall you need an *upstream* lead, not a drain.

![Siphon vs formula vs truth](ARA_enso_siphon_vs_formula_vs_truth.png)

---

## 2. Catchment recombination — an amplitude *discriminator*, not a recovery
At a big crest the forecast doesn't miss the event, it **shatters** it into a cluster of smaller spikes. Dylan:
combine them and you recover the amplitude. Honest OOS (calibrate scale on train events, test on held-out):
- The big in-sample lifts (reach 0.68 → 0.82) were mostly scale-fitting; they shrink under honest calibration.
- What survives: at **24-month lead the recombined cluster tracks event SIZE better than the tallest single
  spike — corr +0.77 vs +0.61.** It's an amplitude **discriminator** ("which events are big"), not a height
  **recovery**.
- **Concentration rule:** works on the *spread* system (ENSO); fails on the *concentrated* ECG QRS, where the
  spike energy is broadband (outside the engine band) — energy genuinely gone, nothing to re-gather.

![Catchment recombination](ARA_enso_catchment_recombination.png)

---

## 3. The watershed cross-section — φ is the fast slope, the floor is the balance line
Dylan's river model: energy flows off both **ridges** (ARA 0 and 2), the **thalweg** is the fast clean channel.
Mapping the ENSO engine speed vs ARA position:
- Coming off the 2.0 ridge the flow **accelerates toward φ** (speed 0.017→0.032), confirming "fast on the
  slope, not on the ridge."
- But the **fastest point (valley floor) is ~1.0 (balance), not φ** — φ (1.618) sits partway down the slope.
  This is φ's framework role: the **handover on the descent**, not the resting point.
- Torricelli check (speed at φ ∝ √ridge-drop): **+0.25, z=+1.8** vs shuffled null — right sign, weak.

![Watershed cross-section](ARA_enso_watershed_crosssection.png)

---

## 4. The clean lane MIGRATES — middle → φ-lane as coherence drops (concentration-gated)
The φ-lanes sit at **ARA 0.382 and 1.618**, each 1/φ² off a singularity bank. Forecast navigability
(low error) by ARA position, across horizons:
- **Short range (3–6mo): the middle (balance ~1.0) is the clean lane** (φ-lane −13% at 3mo).
- **Mid range (9–15mo): the lane swings out to the φ-line — +14% to +19% more navigable** than the middle.
- **Concentration rule gates it:** sunspots (clean clock) **never hand over** — the middle stays best at all
  horizons (−30% to −3%). Only the spread engine develops a turbulent middle that forces the swing to the
  φ-lane.
- Past ~18–24mo (the value wall) both lanes break down (the h=24 −68% is past the ~30mo trough).

So the navigable channel is a **moving thalweg**: it migrates from centre to φ-curve exactly as Dylan predicted
("it moves around the river in a φ shape as the terrain changes").

![Lane migration](ARA_lane_migration.png)

---

## 5. The conserved φ-thalweg — VALIDATED (calm-by-conservation vs calm-by-dissipation)
Dylan's key refinement: the middle is calm *because the two flows cancelled there* (energy spent → still
water), whereas the φ-thalweg is calm *because it kept its energy* (clean curve, never collided). This makes a
**non-trivial** prediction that beats regression-to-the-mean: there should be a lane that is calm **and**
energetic. Conditioning forecast error on engine energy:

| energy band | middle err | φ-lane err | edge |
|---|---|---|---|
| LOW  | 0.94 | 0.93 | tied (calm everywhere — energy spent) |
| MID  | 0.79 | 0.68 | **+13%** |
| HIGH | 1.00 | 0.69 | **+31%** |

The advantage **grows with energy** (+2 → +13 → +31%) — the fingerprint of a conserved channel (regression to
the mean would make all high-energy states hard). **Robust per-horizon:** +28–33% at h=9,12,15,18, **bootstrap
P = 0.98–1.00**, n ≈ 40–60 per cell. Flips only at h=24 (past the value wall, expected). **ENSO only**;
sunspots (clock) show no thalweg (−14% to −0%) — concentration rule. This is the strongest result of the arc.

![Conserved thalweg](ARA_conserved_thalweg.png)

What did NOT survive testing (clean nulls, flagged):
- **"Forward turbulence"** (collision keeps direction while losing value): null — the middle loses *both*
  value and direction; the φ-lane keeps *both*.
- **"A clock centralises turbulence at 1.0":** null — a symmetric synthetic clock put its max error at the
  *extremes*, middle calmest. Plus the locate-by-max-error metric is confounded by regression to the mean.

---

## 6. Morphing the sphere — NULL for value, VALIDATED as a regime map
**6a. As a point-value predictor — null.** Built the fractal forecaster: engine read at φ-scaled cross-sections
(periods 19.5, 31.5, 51, 82.5, 133 mo — note these *are* the real rung ladder), each carrying its own
(ARA × energy) reliability terrain, scales blended weighted by terrain. Result: **thalweg-weighted blend ≡
equal-weight averaging** (Δ ≈ −0.001 everywhere). More cross-sections gave a small *ensembling* gain
(+0.13 → +0.15 @h=12) but a good single scale matched it. **Knowing the water is turbulent doesn't route around
it** — all scales decohere together at the turbulent times; the turbulence is genuine energy loss, not a
routing problem.

**6b. As a regime map — VALIDATED.** Once the sphere is morphed and frozen, *position* predicts **what kind**
of behaviour comes next. Causal terrain coordinate in, future behaviour (measured from the raw signal →
non-circular) out, on ENSO (H=9):
- **Bank → snap:** corr(bank-height, directional snap) **+0.38**, corr(bank-height, magnitude) **+0.46**,
  corr(bank-height, reversals) **−0.30**.
- **Channel → bounded oscillation:** bank states snap with directionality 0.49 / magnitude 1.66 / few reversals
  (0.41); channel states wander with directionality 0.30 / magnitude 1.08 / *more* reversals (0.55).
- **Sunspots:** directionally consistent (banks snap bigger/straighter) but a clean clock reverses everywhere
  (~0.76), so the contrast is muted — the clock floods the whole terrain.

Caveats: part of "bank → big move" is ordinary mean-reversion, but the *regime distinction* (snap vs oscillate,
the reversal-rate gap 0.41 vs 0.55) is real beyond that. The third terrain reading — **ridge → clock by
divergence** — is **untested** (defining a ridge cleanly needs a 2-D spatial field, not a 1-D index).

![Terrain regime map](ARA_terrain_regime_map.png)

---

## Standing synthesis (one line)
**The morphed sphere is a regime map (bank→snap · channel→bounded · φ-thalweg conserved at high energy) and a
confidence map (trust the φ-lane, distrust the high-energy middle) — NOT a value predictor.** Same lesson as
the framework everywhere: it reads *what kind* and *how much to trust*, not the exact number.

## Open threads
- **Ridge → divergent clock**: test on a genuine 2-D spatial field (an SST basin, not the NINO3.4 index line).
- Re-test the thalweg/regime lanes under alternate instantaneous-ARA estimators (current = trailing
  rise-fraction) to confirm the lane positions are estimator-robust.
- Operational comparison (IRI/NMME) for the value forecast still pending (separate from this arc).
