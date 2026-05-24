# ARA Mapping Atlas Result

**Date:** 2026-05-24

This branch shelves point prediction and returns to mapping.

The aim is to diagnose geometry across more systems before forcing a forward formula. The new atlas rebuilds the old `temporal_coordinates_3d.html` idea as a reusable data pipeline plus local visualiser.

## Files

- `Mapping/ara_mapping_atlas_build.py`
- `Mapping/ara_mapping_atlas_data.json`
- `Mapping/ara_mapping_atlas_data.js`
- `Mapping/ara_mapping_atlas_3d.html`

## Data Included

The first atlas build contains:

| Layer | Nodes | Meaning |
|---|---:|---|
| catalog | 135 | Original temporal-coordinate catalogue from `archive/early_visualizations/temporal_coordinates_3d.html` |
| measured_fit | 16 | Current fitted subsystem rungs from `systems_map_v3_data.js` |
| state_geometry | 55 | Current anchor-state ARA rungs from `ara_state_geometry_data.js` |

Total:

```text
206 nodes
235 relations
6 triangle candidates
40 systems/subsystems
157.7 phi-rungs of period span
```

## What The Visualiser Shows

The 3D canvas maps:

```text
X = period on the phi-rung axis
Y = bounded ARA geometry position
Z = action/energy/amplitude weight, depending on source layer
```

It also derives:

- ARA class.
- nearest ARA boundary: space, lower wall, balance, phi, upper wall, time.
- scale domain.
- same-rung candidates.
- vertical ARA matches across scale.
- boundary matches.
- original catalogue handoff/feeder/counter-pair links.
- low-ARA fitted event nodes that sit on named state-rung faces, shown as a toggleable triangle overlay.
- K2/K4 endpoint faces that pass through K3 as the bridge/gate rung.
- ARA position status: `0..2` is treated as the clean geometry band; values above `2` are flagged as compound-system or rung-mismatch diagnostics.

This is not a predictor. It is a diagnostic map.

## Current Reading

The prediction work kept circling the same missing piece: the forward operator needs better geometry vocabulary and better physical feeder state.

The atlas is the cleaner next move:

```text
map more systems
diagnose their rungs, boundaries, and relation classes
then return to prediction once the coordinate grammar is richer
```

The first useful workflow is to filter to `State Geometry`, search for `ENSO`, `Solar`, or `ECG`, and inspect how their measured rungs sit relative to the original catalogue.

## Triangle Overlay

The triangle overlay currently adds six ENSO faces.

Three K-bridge faces mark the K2/K4 endpoint coupling through K3:

| Candidate | Score | Reading |
|---|---:|---|
| ENSO SOI k2 / k3 bridge / k4 | 0.996 | K3 sits almost exactly between the K2 and K4 endpoint rungs in ARA/period geometry |
| ENSO PDO k2 / k3 bridge / k4 | 0.996 | same bridge pattern appears in the PDO branch |
| ENSO NINO k2 / k3 bridge / k4 | 0.987 | same bridge pattern appears in the NINO branch |

Three low-ARA event faces mark fitted event/boundary nodes against named state rungs:

| Candidate | Score | Reading |
|---|---:|---|
| ENSO fitted rung 2 c1 / SOI k5 / NINO k5 | 0.908 | low-ARA fitted event node sits almost exactly on the k5 period band |
| ENSO fitted rung 5 c2 / PDO k7 / SOI k7 | 0.873 | slower low-ARA face near the k7 envelope |
| ENSO fitted rung 4 c1 / SOI k6 / NINO k6 | 0.502 | looser period-band face near the k6 body |

These should be read as candidate geometry faces, not proved subsystems. They are useful because they separate:

```text
named physical side of the system
from
low-ARA fitted event/boundary node at the same scale
```

## Guardrail

Because the atlas merges hand-curated catalogue nodes, fitted subsystem nodes, and anchor-state nodes, it should not be treated as one homogeneous measurement set.

The current geometry rule is also stricter than the oldest catalogue wording:

```text
0 <= ARA <= 2  = clean bounded ARA position
ARA > 2        = diagnostic overflow: likely measuring a compound/coupled pair, or the rung/window is wrong
```

For example, the hydrogen 21-cm hyperfine node remains near the zero/space edge (`ARA = 2.03e-24`) rather than being inverted into an enormous coordinate. That reading matches the geometry: a very long held state with a tiny release event.

The working interpretation is now:

```text
ARA position + orientation + raw timing ratio
```

The atlas maps the bounded ARA position. The orientation records which way the system is turning through accumulate/release. The raw timing ratio records what the observer measured from inside time. This matters because a time-process is not a static object: the apparent direction can reverse depending on whether the measurement window starts from accumulation, release, return, or the coupled partner.

So `ARA > 2` is useful, but not as a normal coordinate. It is a warning light: the reading may be crossing orientation, rung, or coupled-system boundaries.

Safer wording:

> The atlas is a geometry workbench. It helps compare candidate coordinates and relation classes, but it does not by itself prove a universal law or forecast skill.

## Next Mapping Targets

The next high-value additions are:

- nostril dominance rungs as a coupled-pair layer.
- Solar north/south hemisphere state rungs.
- tides as paired forcing geometry.
- respiratory/cardiac coupling rungs.
- a clean imported CSV pathway through `ara_mapper.py` so new systems can be added without hand-editing the atlas.
