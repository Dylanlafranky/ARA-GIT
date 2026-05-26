# ARA Contact Triangle Roll Result

**Date:** 2026-05-26

This test checks the filter / layered sand interpretation:

```text
lower/faster layers roll first
the next layer rolls from contact with an orientation flip
that back-and-forth continues upward
each sphere is constrained by neighbouring spheres
the predictive unit is local rolling contact, not a simple lower+home+upper feature sum
```

In the script this becomes a strict-causal contact lookup:

```text
current sphere spot
+ lower-to-home induced roll parity
+ home-to-upper/contact parity
+ local triangle compactness/handedness
+ nested ARA band depth 2
-> older completed contact states where s+h < t
-> future level / direction lookup
```

## Files

- `TheFormula/ara_contact_triangle_roll_test.py`
- `TheFormula/ara_contact_triangle_roll_result.json`
- `TheFormula/ara_contact_triangle_roll_result.js`
- `TheFormula/ara_contact_triangle_roll_viz.html`

## Leakage Guard

This is strict-causal:

- Contact features at origin `t` use only current-origin sphere/wobble/spin values.
- Analog neighbours are eligible only when their target `s+h` is before the current origin `t`.
- No decoder, lag ridge, future geometry oracle, smoothing, or visual shift is used.
- Non-ready rows fall back to persistence.

It compares against the previous strict sphere-topology lookup from `ara_sphere_topology_direction_result.json`.

## Contact Features

The local rolling contact is represented as:

```text
home point:
  current ARA latitude + home-cycle longitude

lower contact point:
  current ARA latitude + flow longitude, offset by lower-spin drive
  with one orientation flip

constraint/neighbour point:
  current ARA latitude + torsion longitude, offset by SOI/NINO opposition

triangle:
  side lengths, area, compactness, handedness, contact normal

parity:
  lower -> home flip
  home -> upper/constraint flip
  roll-chain sign
```

This is a first mathematical version of the "grains/spheres touching through triangles" idea.

## Key Result

Across 6/12/24 months, all rows:

| Model | MAE | Corr | Turn | Direction | Large-direction |
|---|---:|---:|---:|---:|---:|
| Persistence | 0.896 | +0.003 | 0.007 | 0.000 | 0.000 |
| Terrain level analog | 0.614 | +0.212 | 0.760 | 0.765 | 0.811 |
| Wobble surface analog | 0.608 | +0.218 | 0.773 | 0.779 | 0.834 |
| Sphere nested-2 level | 0.762 | -0.008 | 0.336 | 0.335 | 0.346 |
| Contact pair level | 0.765 | +0.013 | 0.315 | 0.314 | 0.318 |
| Contact triangle level | 0.771 | +0.001 | 0.319 | 0.318 | 0.323 |
| Contact roll level | 0.769 | +0.008 | 0.316 | 0.315 | 0.323 |

Ready-only 6/12/24 focus, where enough prior completed contact states exist:

| Model | MAE | Corr | Turn | Direction | Large-direction |
|---|---:|---:|---:|---:|---:|
| Persistence | 0.970 | -0.013 | 0.009 | 0.000 | 0.000 |
| Terrain level analog | 0.620 | +0.273 | 0.759 | 0.767 | 0.813 |
| Wobble surface analog | 0.596 | +0.335 | 0.776 | 0.785 | 0.838 |
| Sphere nested-2 level | 0.649 | +0.061 | 0.754 | 0.762 | 0.799 |
| Contact pair level | 0.655 | +0.191 | 0.709 | 0.717 | 0.734 |
| Contact triangle level | 0.668 | +0.156 | 0.718 | 0.726 | 0.747 |
| Contact triangle delta | 0.870 | +0.006 | 0.664 | 0.671 | 0.727 |
| Contact roll level | 0.665 | +0.170 | 0.712 | 0.720 | 0.747 |

## Interpretation

This first contact-triangle metric does **not** beat the simpler terrain/wobble lookup.

The contact formulation does add some signal:

```text
ready-only contact_pair corr:     +0.191
ready-only contact_triangle corr: +0.156
ready-only sphere_nested2 corr:   +0.061
```

But it loses on MAE and direction compared with the existing sphere/wobble terrain priors:

```text
ready-only sphere_nested2 direction: 0.762
ready-only contact_triangle direction: 0.726
ready-only wobble direction: 0.785
```

So the strict read is:

```text
Rolling contact is plausible and measurable,
but this first triangle distance overconstrains the lookup.
The best current predictor is still the local wobble/terrain surface.
```

The triangle branch improves large-direction a little over contact-pair:

```text
contact_pair large-direction:     0.734
contact_triangle large-direction: 0.747
```

That hints the triangle geometry may help with larger moves, but the gain is not enough to promote it yet.

## Physical Read

The result fits the sand/filter analogy in a cautious way:

- The local rolling/contact variables are not nonsense; they carry correlation on ready rows.
- Treating the whole contact triangle as a nearest-neighbour distance is too rigid.
- The contact triangle may be better used as a gate or regime label around the wobble terrain lookup.

In other words:

```text
The terrain surface tells us what route we are on.
The contact triangle may tell us when that route is constrained or likely to flip.
It should not yet replace the terrain surface as the main lookup.
```

## Next Improvement

The next clean version should not add every contact variable into the distance metric. It should use contact geometry as a low-dimensional gate:

```text
1. Use wobble/sphere terrain to find the likely future level.
2. Use contact parity/triangle handedness only to choose among neighbour groups.
3. Penalize impossible orientation chains.
4. Let the contact triangle widen uncertainty when the grains are slipping/opposed.
```

This should test whether contact geometry is a **constraint selector**, not the whole route engine.

