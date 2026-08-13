# T375 — liquid-argon nested energy-placement test

**Date:** 13 August 2026  
**Medium and identity:** unchanged from T373/T374  
**Frozen verdict:** **PROGRESSIVE ENERGY-PLACEMENT MECHANISM SUPPORTED**  
**Evidence class:** internal same-event mechanism test; T374 endpoints were
already known, while the intermediate ladder and order controls were frozen
before calculation

## Plain-language result

T374 showed that arrival time knew which branch came first, but it needed
recoil energy to place their equality point inside the liquid parent. T375
tested that explanation directly.

We started with all recoil energies collapsed together, then progressively
restored `2`, `3`, `5` and finally all `12` energy groups. The recovered ARA
handover moved as follows:

\[
\boxed{
1.99893
\rightarrow
1.73393
\rightarrow
1.27726
\rightarrow
1.22397
\rightarrow
1.23883
}
\]

The frozen liquid-parent lead was `1.25`. Every added energy refinement moved
the estimate closer to it. The distance sequence was

\[
0.74893, 0.48393, 0.02726, 0.02603, 0.01117,
\]

giving Spearman correlation `rho=-1.000` between retained energy resolution
and distance from `1.25`. All four successive refinements improved the
distance; the protocol required at least three.

The important shape is not a forced straight interpolation. The previously
uninspected three-group cut jumped into the target neighbourhood from above at
`1.277`. The five-group cut crossed below it to `1.224`; the twelve-group cut
remained below but moved closer again to `1.239`. That looks like increasing
relational resolution converging around a stable neighbourhood, rather than a
line fitted through the known one- and twelve-group endpoints.

## Physical-energy-order control

We then kept the observed events and all background templates fixed while
reversing or randomly permuting only the energy-group labels of the prompt and
delayed CEvNS templates.

| Retained groups | Native rank among 22 | Median permuted penalty (`NLL_perm-NLL_native`) |
|---:|---:|---:|
| `3` | `1/22` | `+4.240` |
| `5` | `1/22` | `+8.127` |
| `12` | `1/22` | `+8.407` |

The native energy ordering was the best fit at all three tested resolutions.
Even the closest permuted alternatives were worse by `+1.063`, `+0.041` and
`+5.746` NLL respectively.

This matters because the result is not produced merely by adding more bins.
The physical order of those bins carries information about where the handover
sits.

## ARA reading

The most faithful present reading is:

> Arrival time retains the forward prompt-to-delayed order. With energy
> collapsed, that ordered motion is visible but its internal placement is
> compressed to the `2.0` pole. Restoring the energy relation decompresses the
> same liquid parent: one split moves it inward, three splits locate the
> `1.25` neighbourhood, and finer splits settle around it.

In the originator's terms, the liquid target is not a replacement for the
stopped-pion/muon child relation. It is the movement-heavy parent mixture that
contains it. T375 shows how one detector relation—energy deposition—lets the
child handover be placed inside that parent rather than flattened to its
singularity.

## Frozen gates

| Gate | Requirement | Result | Verdict |
|---|---|---:|:---:|
| finite ladder | all five centres finite | `5/5` | pass |
| monotone approach | Spearman `<= -0.80` | `-1.000` | pass |
| successive improvement | at least `3/4` | `4/4` | pass |
| same side | intermediate centres `>=1.0` | `3/3` | pass |
| physical energy order | median advantage and top quarter at `3,5,12` groups | rank `1/22` at all | pass |

## What is supported

1. Within this liquid-argon event record, progressively restoring recoil-
   energy structure progressively restores the interior handover placement.
2. Three coarse physical energy groups are already sufficient to move the
   estimate from the far pole into the `1.25` neighbourhood.
3. Physical energy ordering contains information beyond the mere number of
   bins: native order beat reversed/random order at all tested resolutions.
4. T374's statement that time carries order while energy adds placement now
   has a direct frozen mechanism test behind it.

## What is not supported

1. T375 is not independent confirmation of a universal `x_H=1.25` law. It
   uses the same 3,752 events as T373/T374.
2. The one- and twelve-group endpoints were already known before T375. The new
   evidence is the predeclared intermediate trajectory and the permutations.
3. Ordinary statistical language remains valid: energy resolution helps
   distinguish CEvNS signal from prompt-neutron and steady-state backgrounds.
   T375 supplies an ARA crosswalk for that relational recovery; it does not
   replace or disprove the detector explanation.
4. The profile intervals remain broad. The strong result is the resolution-
   ordered trajectory, not a high-precision universal constant measurement.

## Reproduction

- frozen protocol:
  `T375_LIQUID_ARGON_ENERGY_PLACEMENT_PROTOCOL_2026-08-13.md`;
- protocol SHA-256:
  `1fcd0b3cac1d77c8968f2f520aad2450b4c2286ae75fb34407dab5a58f743382`;
- analysis:
  `t375_liquid_argon_energy_placement.py`;
- results:
  `T375_LIQUID_ARGON_ENERGY_PLACEMENT_RESULTS.json`;
- ladder:
  `T375_LIQUID_ARGON_ENERGY_PLACEMENT_LADDER.csv`;
- controls:
  `T375_LIQUID_ARGON_ENERGY_PLACEMENT_CONTROLS.csv`;
- figure:
  `T375_LIQUID_ARGON_ENERGY_PLACEMENT_FIGURE.png` and `.svg`.
