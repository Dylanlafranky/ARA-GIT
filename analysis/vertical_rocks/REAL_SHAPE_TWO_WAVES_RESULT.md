# Vertical ARA on REAL measured shape data — two waves

**Date:** 1 Jul 2026. **Data:** real only. Triaxial ellipsoid radii (a,b,c) = canonical IAU/JPL/Cassini/mission-derived values for 31 bodies (grain→gas giant). Roundness = c/a (min/max axis, 1=sphere) — **derived from measured axes, not eyeballed** (fixes the prior hand-scored table).
**Script:** `map_rocks_real.py` · **Figure:** `rock_real_two_waves.png`

## Wave 1 — size → roundness (the shape wave): CONFIRMED
- Spearman ρ = **0.816**, shuffle-null p = **0.0002** (n=29 non-rotational bodies). Real, not chance.
- Logistic transition radius = **~180 km** — matches the literature "potato radius" (~200–300 km) where gravity starts winning over material strength.
- Bracketed by real bodies: **Proteus** (R≈209 km) still irregular vs **Mimas** (R≈198 km) fully round — the transition is a *contrast*, not a clean handoff, which is why it's fuzzy.

### Outlier honesty (vs the fitted curve)
- **Phobos is NOT the standout** on real axes — c/a=0.70 sits near the curve. The earlier "Phobos outlier" was an artifact of the eyeballed 0.70 score against eyeballed neighbours. Remapping dissolved it.
- Real outliers are two clean physical classes:
  - **Below** the curve (jagged when their size says rounder): **Eros, Ida, Itokawa** — coherent/monolithic shards; rock strength holds an elongated shape.
  - **Above** the curve (round when their size says jagged): **Bennu, Ryugu** — sub-km rubble-pile "spinning tops" already shaped round by self-gravity + rotation.
- So below the potato radius **structure (rubble vs monolith) sets form, not size** — the scatter itself is the signature that no size→roundness law holds yet down there.

### Hyperion vs Mimas (your question, on real numbers)
Same size shelf, **opposite** form — NOT close ARA:
| body | R (km) | c/a | density |
|---|---|---|---|
| Hyperion | 135 | 0.570 | **0.54 g/cc** (porous rubble — never relaxed) |
| Mimas | 198 | 0.917 | 1.15 g/cc (ice — relaxed round) |
The density gap *is* the explanation. They're the two sides of the transition, the cleanest natural experiment in the ladder.

## Wave 2 — formation → erosion (the genuine time-ARA): SUGGESTIVE, FENCED
ARA = T_erosion / T_formation = persistence per unit build-cost. Built from **order-of-magnitude published scaling** (Bottke collisional lifetime: D=0.8 km ~0.3 Gyr → D=10 km ~5 Gyr, power-law ~D^1.1, survival capped at the 4.6 Gyr system age; accretion time: pebbles ~kyr → terrestrial planets ~tens of Myr).
- The ratio **peaks at ~6 km radius (small-asteroid scale)** — your "optimal size" intuition produces a real interior peak: tiny bodies are cheap but fragile; planets are expensive to build and their longevity saturates at the system age, so persistence-per-cost falls off both ends.
- **FENCES (do not over-read):** timescales are model/scaling-derived not per-body measured; erosion processes are heterogeneous across the ladder (stream abrasion ≠ collisional disruption ≠ effectively-stable planet); the peak location is **sensitive to the age cap**. This is a suggestive shape, not an earned measurement.

## Net
The shape wave is the solid result — real measured axes confirm size→roundness (ρ=0.82, p=0.0002) and put the potato-radius transition at ~180 km, with outliers that resolve into clean physics (monolith vs rubble). The formation→erosion wave reproduces your predicted optimal-size *peak* but only at order-of-magnitude confidence. Phobos was an eyeballing artifact; the real story is the rubble-pile spinning tops and the porous Hyperion/Mimas split.
