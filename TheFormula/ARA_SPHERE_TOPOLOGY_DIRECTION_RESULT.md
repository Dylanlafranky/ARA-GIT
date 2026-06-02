# ARA Sphere Topology Direction Result

**Date:** 2026-05-25

This test uses the mapped sphere as a topology memory.

The question was:

```text
If the water slice travels across the same or similar spot on the ARA sphere,
does the older completed route through that spot tell us what the data will do next?
```

It also tests the ARA-in-ARA idea: the 0-2 sphere is broken into ARA bands, then each band is recursively remapped back onto 0-2 for two or three local layers. Deeper layers contribute less with:

```text
depth weight = 1 / log2(level + 2)
```

## Files

- `TheFormula/ara_sphere_topology_direction_predictor.py`
- `TheFormula/ara_sphere_topology_direction_result.json`
- `TheFormula/ara_sphere_topology_direction_result.js`
- `TheFormula/ara_sphere_topology_direction_viz.html`

## Leakage Guard

This is strict-causal:

- Sphere/topology features at origin `t` use only the current-origin values exported from the sphere atlas.
- Analog neighbours are eligible only when their own target `s+h` is before the current origin `t`.
- No decoder, lag ridge, future geometry oracle, smoothing, or visual shift is used.
- When not enough completed sphere history exists, the sphere-only branches fall back to persistence, not to another ARA model.

Important caveat: this first pass uses the existing sphere-atlas export, which contains the held-out visual records rather than the full pre-2001 training history. That makes the test stricter than ideal and leaves only part of the series "ready" for sphere-memory lookup.

## Key Result

Across the 6/12/24-month focus window, all rows:

| Model | MAE | Corr | Turn | Large-direction |
|---|---:|---:|---:|---:|
| Persistence | 0.896 | +0.003 | 0.007 | 0.000 |
| Terrain level analog | 0.614 | +0.212 | 0.760 | 0.811 |
| Wobble surface analog | 0.608 | +0.218 | 0.773 | 0.834 |
| Sphere nested-2 level | 0.762 | -0.008 | 0.336 | 0.346 |

The all-row sphere score is conservative because non-ready rows use persistence. The cleaner read is the ready-only subset where the sphere actually has enough previous completed topology to compare against.

Ready-only 6/12/24 focus:

| Model | MAE | Corr | Turn | Direction | Large-direction |
|---|---:|---:|---:|---:|---:|
| Persistence | 0.970 | -0.013 | 0.009 | 0.000 | 0.000 |
| Terrain level analog | 0.620 | +0.273 | 0.759 | 0.767 | 0.813 |
| Wobble surface analog | 0.596 | +0.335 | 0.776 | 0.785 | 0.838 |
| Sphere global delta | 0.890 | -0.060 | 0.663 | 0.671 | 0.699 |
| Sphere global level | 0.650 | +0.059 | 0.737 | 0.745 | 0.788 |
| Sphere nested-2 delta | 0.888 | -0.061 | 0.672 | 0.680 | 0.711 |
| Sphere nested-2 level | 0.649 | +0.061 | 0.754 | 0.762 | 0.799 |
| Sphere nested-3 level | 0.650 | +0.051 | 0.737 | 0.745 | 0.788 |

## Interpretation

This supports the topology-memory idea, but in a specific form:

```text
Same/similar sphere terrain -> useful future level and direction prior.
Same/similar sphere terrain -> not enough to transport the raw delta vector.
```

The best sphere-only branch is `sphere_nested2_level`, not the delta route. On ready rows it reaches MAE `0.649`, turn `0.754`, direction `0.762`, and large-direction `0.799`. That is close to the terrain/wobble analog branches, though still weaker.

The ARA-in-ARA drilldown helps a little at depth 2:

```text
global level ready direction:   0.745
nested-2 level ready direction: 0.762
nested-3 level ready direction: 0.745
```

So the first local subdivision seems useful, but the third layer adds noise or over-localises with this amount of data. In this pass, "two layers deep" is the sweet spot.

## Physical Read

The mapped sphere can be used as a topology lookup, but it should not yet be treated as a solved flow law.

The clean read is:

```text
The sphere remembers what nearby terrain tends to become.
It does not yet know how to advance the exact water-slice vector by itself.
```

That fits the current framework:

- Terrain/wobble analogs are still the best current route predictors.
- Sphere topology adds a compact coordinate system for finding similar terrain.
- Nested ARA bands help most as a local terrain classifier, not as a direct motion equation.

## Next Improvement

The next better version should rebuild the sphere atlas with full causal training history, not just held-out visual records. That would increase ready coverage and make the topology lookup much fairer. The candidate rule should stay the same:

```text
candidate target s+h must be earlier than current origin t
```

After that, test adaptive depth:

```text
use depth 0 near sparse regions
use depth 2 when neighbours remain stable
avoid depth 3 unless candidate density is high
```

