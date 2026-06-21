# 10 — Morphed-sphere terrain, watershed & layered-sand

**Thread:** Recast the ARA state as a position on a morphed sphere / eroding terrain, and forecast by analog-matching older completed terrain paths. Dates 25–26 May 2026. Richly documented (one `*_RESULT.md` per test).

## Model logic / idea
The geometry state is not a flat circle but a local patch on a sphere: **ARA = 0–2 pole-to-pole latitude** (space pole → balance equator → time pole), **phase/degrees = longitude**, **wobble = local surface displacement**. The forecast question becomes topological: if the "water slice" revisits the same spot on the ARA sphere, the older completed route through that spot tells us what comes next. Variants treat the system as a watershed (raw NINO mapped to a 0–2 channel with a φ-valley low-energy route, tributaries, ridges) and as a stack of counter-rolling **layered-sand** spheres (floor → fine/medium/coarse grains → measured sphere, each layer rolling opposite to its contact, reading its own recursive ARA terrain). All branches are strict-causal: terrain features from raw samples `≤t`, analog neighbours only when their own target `s+h<t`, **no decoder, lag ridge, smoothing, bandpass, or oracle**.

## Systems tested
ENSO (NINO 3.4 + SOI/PDO) at 3/6/12/18/24 months.

## Key results (from the `*_RESULT.md` docs)
- **The terrain-analog beats persistence cleanly and is the thread's win.** `terrain_level_analog` (6/12/24-mo): MAE `0.602`, corr `+0.275`, turn `0.769` vs persistence MAE `0.896`, corr `+0.003`. By horizon it degrades gracefully: 3mo corr `+0.758`, 6mo `+0.474`, 12mo `+0.199`, 24mo `+0.152`.
- **Wobble-surface analog is comparable/slightly better** (MAE `0.608`, corr `+0.218`, turn `0.779`); on the ready-only subset corr reaches `+0.335`.
- **The sphere is a better direction/level prior than a raw vector transporter.** Nested ARA-band recursion helps slightly on ready rows; a third nested layer adds noise.
- **The fixed symbolic flow under-rolls.** `lower_spin_formula` reconstructs the *current* terrain slice but barely advances it (corr `+0.024`); the layered-sand full formula produces correct direction but tiny amplitude (amp ratio `0.05–0.20` vs truth `1.0`) — the lower-layer-pressure → measured-roll-displacement transfer law is still wrong.

## What was NOT tested / open
The numeric law converting lower-layer contact pressure + upper compression into measured-sphere roll distance in ARA address space — this is the named next step. The sphere atlas test used held-out visual records rather than full pre-2001 history, leaving only part of the series "ready" for sphere-memory lookup.

## Key files
- `ARA_TERRAIN_ARRIVAL_PREDICTOR_RESULT.md` + `ara_terrain_arrival_predictor.py` — the no-decoder terrain analog that beats persistence
- `ARA_SPHERE_TOPOLOGY_DIRECTION_RESULT.md` + `ara_sphere_topology_direction_predictor.py` — sphere as causal topology memory
- `ARA_LAYERED_SAND_FULL_FORMULA_RESULT.md` + `ara_layered_sand_full_formula.py` — full counter-rolling layered-sand mechanism
- `ARA_RAW_WATERSHED_SLICE_RESULT.md` + `ara_raw_watershed_slice_test.py` — raw (unsmoothed) watershed formula
- `ARA_SPHERE_ATLAS_RESULT.md` + `ara_sphere_atlas_from_wobble.py` — full-sphere mapping workbench
