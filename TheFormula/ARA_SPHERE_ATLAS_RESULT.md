# ARA Sphere Atlas Result

**Date:** 2026-05-25

This is the first full-sphere mapping workbench for the ENSO water-slice terrain records.

It follows the correction:

```text
The water slice is not just revisiting a flat circular path.
It sits on a local surface of a sphere.
ARA gives the 0-2 pole-to-pole position.
Phase/degrees gives the longitude.
Wobble gives the local surface displacement.
```

## Files

- `TheFormula/ara_sphere_atlas_from_wobble.py`
- `TheFormula/ara_sphere_atlas_data.json`
- `TheFormula/ara_sphere_atlas_data.js`
- `TheFormula/ara_sphere_atlas_viz.html`

## Coordinate System

The atlas maps:

```text
ARA latitude:
  ARA 0   -> space pole
  2-phi   -> anti-phi mirror band
  0.5     -> quarter band
  ARA 1   -> balance equator
  phi     -> phi valley band
  ARA 2   -> time pole

Longitude:
  home-cycle degrees
  wobble-vector degrees
  flow-direction degrees
  torsion degrees

Surface displacement:
  x = downstream / topology-arrival tilt
  y = lateral bank / ridge-channel tilt
  z = vertical sea/backpressure lift-sink tilt
```

The current NINO-derived ARA range in the held-out records spans:

```text
0.188 .. 1.937
```

So the ENSO water-slice path covers most of the sphere, not just a narrow band.

## Interpretation

This is a mapping tool, not a new forecast. It lets us inspect:

```text
current terrain path
future truth path
wobble-surface predicted path
terrain-level predicted path
error links between prediction and truth
local wobble arrows
```

The useful next question is whether forecast errors cluster at particular sphere bands, longitudes, or torsion states. If they do, the missing predictor term is probably not another raw lag term, but a topology/contact correction for specific sphere regions.

That next question is now tested in `ARA_SPHERE_TOPOLOGY_DIRECTION_RESULT.md`. The short read: the sphere can be used as a causal topology memory, but it works better as a future-level/direction prior than as a raw vector/delta transporter. Two nested ARA-band layers help slightly on ready rows; a third layer adds noise in the first pass.

## Verification

Checked locally:

```text
python -m py_compile TheFormula/ara_sphere_atlas_from_wobble.py
python -m json.tool TheFormula/ara_sphere_atlas_data.json
inline visualizer JavaScript syntax check
generated data JavaScript syntax check
git diff --check
```

The available Node environment did not have Playwright installed, so I could not run a headless screenshot/canvas-pixel render check in this pass.
