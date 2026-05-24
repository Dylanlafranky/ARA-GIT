# ARA Mapping Atlas Result

**Date:** 2026-05-24

This branch shelves point prediction and returns to mapping.

The aim is to diagnose geometry across more systems before forcing a forward formula. The new atlas rebuilds the old `temporal_coordinates_3d.html` idea as a reusable data pipeline plus local visualiser.

## Files

- `Mapping/ara_mapping_atlas_build.py`
- `Mapping/ara_mapping_atlas_data.json`
- `Mapping/ara_mapping_atlas_data.js`
- `Mapping/ara_mapping_atlas_3d.html`
- `Mapping/build_mapping_extensions.py`
- `Mapping/ara_mapping_extensions.json`
- `Mapping/galactic_rotation_phi_test.py`
- `Mapping/galactic_rotation_phi_test_result.json`
- `Mapping/galactic_structure_time_phi_test.py`
- `Mapping/galactic_structure_time_phi_test_result.json`
- `Mapping/audit_over2_ara_nodes.py`
- `Mapping/ara_over2_audit.json`
- `Mapping/ARA_OVER2_AUDIT.md`

## Data Included

The first atlas build contains:

| Layer | Nodes | Meaning |
|---|---:|---|
| catalog | 135 | Original temporal-coordinate catalogue from `archive/early_visualizations/temporal_coordinates_3d.html` |
| measured_fit | 16 | Current fitted subsystem rungs from `systems_map_v3_data.js` |
| state_geometry | 55 | Current anchor-state ARA rungs from `ara_state_geometry_data.js` |
| mapped_extension | 28 | New mapping targets: nostril dominance, tides, solar hemispheres, human gait, MJO/QBO, and a quantum-to-cosmic scale anchor ladder |

Total:

```text
234 nodes
270 relations
6 triangle candidates
55 systems/subsystems
157.7 phi-rungs of period span
```

## What The Visualiser Shows

The 3D canvas maps:

```text
X = period on the phi-rung axis
Y = bounded ARA geometry position, fixed to the full 0..2 axis
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
- explicit mapping-extension relations for paired dominance, forcing gates, solar hemisphere coupling, gait rung collapse, ENSO climate-feeder links, and cross-scale ladder anchors.
- ARA position status: `0..2` is treated as the clean geometry band; values above `2` are flagged as compound-system or rung-mismatch diagnostics.
- Visual Y scaling: the clean `0..2` ARA range is stretched across the full Y axis; values above `2` are pinned to the top diagnostic rail instead of expanding the axis.
- Quarter-axis markers: `0`, `1/4 anti-phi`, `1/2`, `3/4`, `1 balance`, `5/4`, `3/2`, `phi`, `7/4`, and `2` are drawn as Y-axis guide lines. The added quarter guides are visual markers; they do not rewrite the semantic nearest-boundary relation scan.

This is not a predictor. It is a diagnostic map.

## Current Reading

The prediction work kept circling the same missing piece: the forward operator needs better geometry vocabulary and better physical feeder state.

The atlas is the cleaner next move:

```text
map more systems
diagnose their rungs, boundaries, and relation classes
then return to prediction once the coordinate grammar is richer
```

The first useful workflow is to filter to `State Geometry`, search for `ENSO`, `Solar`, or `ECG`, and inspect how their measured rungs sit relative to the original catalogue. For the new pass, filter to `Mapped Extension` and search `Nostril`, `Tides`, `Solar Hemispheres`, `Human Gait`, `MJO`, `QBO`, `Molecular`, `ATP`, `Chandler`, `Milankovitch`, or `Galactic`.

## 2026-05-24 Mapping Extension Pass

Five high-value diagnostic targets were added after the atlas moved out of `TheFormula` and into `Mapping`:

| Target | Nodes | Main reading |
|---|---:|---|
| Nostril dominance | 2 | Paired anti-phase biological system; signed-cycle geometry remains linked to ENSO as a relation-class match, not direct causation |
| Tides | 3 | M2 carrier, spring-neap envelope, and measured amplitude-breath gate; the gate ratio is near the engine/phi band |
| Solar hemispheres | 3 | North/south cycles plus relaxation gate; saved coupling-speed diagnostic remains near phi |
| Human gait | 8 | Raw PhysioNet gaitndd medians rerun on 2026-05-24, plus preferred phi crossing, walk-run transition, sustainable running mirror-phi crossing, and ALS collapse marker |
| MJO/QBO | 2 | Climate feeder layer below ENSO; QBO has measured k7 concentration, MJO is period-mapped with ARA pending |

A second extension pass added 10 cross-scale anchors, chosen as a bell-curve spread from quantum/molecular to organism, planetary, and cosmic periods:

| Scale anchor | Period | ARA | Reading |
|---|---:|---:|---|
| Molecular vibration | `1e-14 s` | `1.0` | quantum/molecular balanced oscillator placeholder |
| Alpha-helix formation | `100 ns` | `1.0` | conservative protein-folding anchor |
| ATP synthase rotation | `10 ms` | `1.50` | ATP-specific chemical-oscillator rerun maps it as a three-phase rotary engine near phi |
| Human breathing | `4 s` | `phi` | middle-scale biological oscillator anchor |
| Circadian sleep-wake | `24 h` | `2.0` | wake/sleep harmonic boundary convention |
| Chandler wobble | `433 d` | `1.0` | planetary rotational balance anchor |
| Lunar nodal cycle | `18.6 y` | `1.0` | orbital-regression balance anchor |
| Milankovitch obliquity | `41 kyr` | `1.0` | slow Earth orbital-forcing anchor |
| Spiral arm passage | `120 Myr` | `1.2` | galactic structure compression/expansion anchor |
| Galactic rotation MW | `220.25 Myr` | `1.0` | Gaia DR3 Cepheid rotation-curve test supports the period anchor but rejects the archived phi ARA assignment |

These cross-scale edges are visual ladder steps only. They are not forecast features and they do not claim causal transfer from one scale anchor to the next.

Galactic rotation correction: the earlier `phi` ARA was an archived scaffold, not a measurement. `Mapping/galactic_rotation_phi_test.py` now checks the Milky Way rotation-curve table from Gaia DR3 Cepheids. The solar-radius period comes out `220.25 Myr`, within `4.24%` of the old `230 Myr` anchor, but the circular carrier ARA is neutral `1.0`. The measured epicyclic coupling is closer to flat-curve `sqrt(2)` than to phi (`global kappa/Omega = 1.385`, `median = 1.334`; `0/12` local points fall within `0.10` of phi). The atlas keeps the old phi value only as `archived_prior_ara`.

Structure-time follow-up: `Mapping/galactic_structure_time_phi_test.py` separates the balanced carrier from the time-through-structure layer. For a four-arm spiral, `P_cross = P_orb / phi` requires spiral pattern speed `16.61 km/s/kpc`, giving `P_cross = 136.12 Myr`. That sits close to the slow density-wave `12..17 km/s/kpc` literature range; the upper range candidate gives `P_cross/P_orb = 0.640`, within `0.022` of `1/phi`. Bar-pattern central values are sub-phi (`Omega_bar/Omega_sun = 1.470` for the near-side Gaia/VVV candidate), though broad systematics can overlap the phi target. Read this as phi-plausible for spiral time-through-structure, not as a proved galactic phi carrier.

ATP synthase correction: the earlier provisional split into rotor/gradient child nodes was hard-coded and has been removed. The atlas now uses the ATP-specific chemical-oscillator rerun from `archive/numbered_tests/50_chemical_oscillators_ara.py`: ATP synthase maps at ARA `1.50`, near phi. The coupled rotor/gradient idea remains a testable hypothesis, but it needs real single-molecule substep dwell-time data before being mapped as child coordinates.

Gait rerun: after installing the local scientific stack into `F:\SystemFormulaFolder\.venv_ara_verify`, `analysis/gait/analyze_gait_phi.py` completed against raw PhysioNet `gaitndd` records. The atlas now records rerun medians: Control `1.3548`, Parkinson's `1.4414`, ALS `1.4651`, Huntington's `1.3615`.

Gait caveat: the PhysioNet gaitndd medians are controlled instructed-walk data. They are useful for comparing disease/control stride geometry, but they should not be treated as natural open-environment locomotion. The ideal walking/running crossover anchors therefore come from the literature locomotion arc: preferred walking at stance/swing `phi` around `1.27 m/s`, walk-run handoff at `1.0` around `2.20 m/s`, and sustainable running mirror-phi at `1/phi` around `3.85 m/s`.

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

The over-2 audit now makes this explicit. `Mapping/audit_over2_ara_nodes.py` found `45` nodes above `2.0`, all from the original hand-curated `catalog` layer. The newer `measured_fit`, `state_geometry`, and `mapped_extension` layers currently introduce no above-2 leakage. Each older over-2 node is kept as a diagnostic entry until it can be retested from source data, inverted for orientation, shifted to the correct rung, or decomposed into child subsystems.

Safer wording:

> The atlas is a geometry workbench. It helps compare candidate coordinates and relation classes, but it does not by itself prove a universal law or forecast skill.

## Next Mapping Targets

The immediate high-value additions from the previous list are now represented in the atlas. The next useful additions are:

- respiratory/cardiac coupling rungs.
- deeper gait calibration under the current bounded-position + orientation convention, especially the disease-group distribution shapes rather than only pooled medians.
- direct raw-cycle ARA measurement for MJO rather than the current period-only partner coordinate.
- a clean imported CSV pathway through `ara_mapper.py` so new systems can be added without hand-editing the atlas.
