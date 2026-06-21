# 17 — River-landscape & thalweg regime map (09-06-26)

**Thread:** The morphed-sphere / river-landscape model — record of Dylan's energy-movement quotes plus what was tested: the conserved φ-thalweg, terrain-position regime map, catchments, siphons, and a 3D molded-sphere build. Dated 9 June 2026.

**Model logic / idea:** The wave *is* the topography. Training morphs a sphere into a fractal terrain carrying an ARA along each axis (X = Mapping, Y = Rungs as nested sub-ARAs, Z = coupling; φ-line = diagonal). On this river-bed: **φ-thalwegs = conserved high lanes where energy rides fastest and cleanest; the middle (1.0) = the low dissipative sink where opposing flows collide and cancel (turbulent for energy, calm for the river); banks (0, 2) = snap edges.** A clock is the special case where both banks deliver equal energy meeting at 1.0. Siphons = systems just below the sphere that drain a little energy and steer the wobble; catchments = recombining scattered noisy spikes near a crest to recover amplitude. To run it: calibrate position, rotate + wobble, energy rolls to the lowest unless the counter-wave carries it up a ridge.

**Systems tested:** ENSO/NINO3.4 (primary); sunspots as the clock null.

**What was tested:** (numbers from the linked `RIVER_LANDSCAPE_AND_THALWEG_RESULT.md`; this folder holds the model write-up, figures, and the 3D HTML build)
- Conserved φ-thalweg calm-lane test.
- Terrain-position → regime (bank vs channel) test.
- Geometry-driven generative rollout (direction).
- Axis-count ablation (2 vs 3 axes).
- The molded-sphere 3D visualiser (`ARA_molded_sphere_3D.html`).

**Key results:**
- **Conserved φ-thalweg — VALIDATED:** the high-energy φ-lane (ARA 0.382 & 1.618) is +28–33% calmer than the turbulent middle (h=9–18, bootstrap P≈0.99), and the advantage *grows with energy* (beats regression-to-mean). ENSO only; sunspots (clock) null per the concentration rule.
- **Terrain position predicts regime — VALIDATED:** bank → snap (corr +0.38 directionality, +0.46 magnitude, −0.30 reversals); channel → bounded oscillation. Causal, non-circular.
- **Generative rollout works for DIRECTION:** pure rollout gives change-skill +0.40 → +0.68 growing with horizon, beating persistence. 2 axes ≡ a bare clock (+0.00); 3 axes beats the clock by +0.02–0.07 — completing the geometry added real, if small, drive.
- **NULL as a VALUE predictor:** regression still wins on value; the geometry delivers direction + confidence, not the exact number. Also null: siphons-as-predictor, forward-turbulence, clock-centralizes-turbulence, terrain-weighted blend ≡ equal-weight.
- **3D build not right yet:** Dylan flagged it keeps flattening — too-smooth analytic profiles instead of a carved fractal surface; the fractal must come from rung-axis nesting + real training roughness at high resolution.

**What was NOT tested / open:** The correct fractal morphed-SURFACE build (canonical axes, rung-nested cross-sections, minimal smoothing) is the explicit pick-up task. Whether the full physics finally beats the clock on VALUE once the terrain is genuinely fractal is unresolved. A detailed pick-up checklist is in the doc.

**Key files:**
- `MORPHED_SPHERE_MODEL_AND_QUOTES.md` — the model, Dylan's verbatim quotes, tested numbers, and pick-up checklist (headline doc).
- `ARA_molded_sphere_3D.html` — the 3D molded-sphere build (terrain still too smooth).
- `ARA_conserved_thalweg.png`, `ARA_terrain_regime_map.png`, `ARA_terrain_working_vs_truth.png`
