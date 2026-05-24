# Mapping

This folder is for geometry-first diagnostic workbenches and map-building assets.

The files here are not the forward formula itself. They are for locating systems, rungs, ARA positions, orientations, boundaries, and relation candidates before deciding whether a prediction test makes sense.

The atlas visualiser uses a fixed `0..2` Y axis for bounded ARA position. Above-2 diagnostic values are pinned to the top rail so overflow readings do not compress the clean geometry band. The Y axis draws quarter markers at `0`, `1/4 anti-phi`, `1/2`, `3/4`, `1 balance`, `5/4`, `3/2`, `phi`, `7/4`, and `2`.

Current contents:

- `ara_mapping_atlas_3d.html` - interactive 3D mapping atlas.
- `ara_mapping_atlas_build.py` - rebuilds the atlas data from the old temporal-coordinate visualiser and current `TheFormula` data exports.
- `ara_mapping_atlas_data.json` - structured atlas data.
- `ara_mapping_atlas_data.js` - browser-loadable atlas data.
- `build_mapping_extensions.py` - builds the current mapping-extension layer for nostril dominance, tides, solar hemispheres, human gait, MJO/QBO, and the 10-system quantum-to-cosmic anchor ladder.
- `ara_mapping_extensions.json` - generated extension nodes and hand-declared diagnostic relations.
- `galactic_rotation_phi_test.py` - checks whether the Milky Way rotation-curve geometry supports the old galactic-rotation phi scaffold.
- `galactic_rotation_phi_test_result.json` - generated result from that check.
- `galactic_structure_time_phi_test.py` - checks whether bar/spiral time-through-structure is phi-like after separating the rotation carrier.
- `galactic_structure_time_phi_test_result.json` - generated result from that structure-time check.
- `audit_over2_ara_nodes.py` - audits all atlas nodes above the clean `0..2` ARA band.
- `ara_over2_audit.json` - generated above-2 audit data.
- `ARA_OVER2_AUDIT.md` - readable above-2 review ledger and retest rules.

To rebuild:

```powershell
python Mapping\galactic_rotation_phi_test.py
python Mapping\galactic_structure_time_phi_test.py
python Mapping\build_mapping_extensions.py
python Mapping\ara_mapping_atlas_build.py
python Mapping\audit_over2_ara_nodes.py
```

The gait disease/control nodes in the extension layer are based on the raw PhysioNet rerun from `analysis\gait\analyze_gait_phi.py`. Treat those as controlled instructed-walk geometry. The preferred walking, walk-run handoff, and sustainable running anchors come from the literature locomotion arc in `analysis\gait\analyze_running_phi.py`.

The cross-scale anchor ladder is pulled from older archive ladder scripts. It is useful for orientation across quantum, molecular, organism, planetary, and cosmic scales, but its ladder edges are visual adjacency links rather than causal or predictive claims.

ATP synthase uses the ATP-specific chemical-oscillator rerun at ARA `1.50`. The earlier hard-coded rotor/gradient child coordinates were removed; testing that coupled-subsystem idea needs real substep dwell-time data.

Galactic rotation no longer uses the old archived phi value as its measured ARA. The rotation-curve diagnostic supports the rough galactic-year period near the solar radius (`220.25 Myr`, close to the old `230 Myr` scaffold), but maps the pure circular carrier at ARA `1.0`. The old phi assignment is kept only as archived-prior metadata.

The structure-time follow-up is more favourable but still provisional: a four-arm spiral crossing becomes `P_orb / phi` at pattern speed `16.61 km/s/kpc`, close to the slow density-wave `12..17 km/s/kpc` literature range. The upper slow-wave candidate gives `P_cross/P_orb = 0.640`, within `0.022` of `1/phi`. Bar-pattern central values are sub-phi.

The above-2 audit currently finds `45` nodes over the clean `0..2` ARA band. All `45` are from the older hand-curated catalogue layer; no over-2 nodes are introduced by `measured_fit`, `state_geometry`, or `mapped_extension`. Treat them as diagnostic overflow until each one is remeasured, inverted for orientation, moved to a better rung, or split into child subsystems.
