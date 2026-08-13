# T374 — liquid-argon axis-consistency audit

**Date:** 13 August 2026  
**Medium:** unchanged — the same CENNS-10 liquid argon used in T373  
**Events:** unchanged — the same 3,752 released events, inspected through
different axes  
**Frozen verdict:** **LIQUID-PARENT `1.25` LEAD NOT AXIS-CONSISTENT**  
**Secondary result:** **THE NATIVE PROMPT-TO-DELAYED ORDER PASSED EVERY
SHIFTED-ORDER CONTROL**

## Plain-language result

We did not swap argon for another material. We kept the same liquid parent,
the same stopped-pion / stopped-muon neutrino source and the same CEvNS
interaction. We only changed which parts of the released detector record were
allowed to separate the two release branches.

The complete three-dimensional record returned

\[
x_H=1.23883,
\]

close to the frozen liquid-parent lead `1.25`. Keeping **energy and arrival
time** returned

\[
x_H=1.35817,
\]

which is still on the predeclared movement-heavy interval `1.0–1.5` and
comfortably permits exact `1.25` (`Delta NLL=0.05798`).

Keeping **pulse shape and arrival time**, however, drove the central estimate
to the `2.0` boundary. Exact `1.25` was only barely inside the conventional
95% profile boundary (`Delta NLL=1.91264` versus the frozen limit
`1.92073`). Time alone also ran to `2.0`.

Cuts without arrival time were nearly flat in the prompt/delayed mixture. They
technically permit `1.25`, but they do not locate it. Their arbitrary profile
minima must not be read as physical ARA positions.

Under the frozen rule requiring both time-bearing two-axis cuts to have their
central estimates in `1.0–1.5`, the primary axis-consistency gate **fails**.

## What the result does support

The source order itself is real and strongly present. For every time-bearing
cut, the unshifted prompt-to-delayed source order had the best likelihood of
all ten possibilities: the native order plus nine circular shifts.

| Cut | Native rank among 10 | Median shifted penalty (`NLL_shift-NLL_native`) |
|---|---:|---:|
| full energy × F90 × time | `1/10` | `+7.096` |
| energy × time | `1/10` | `+6.848` |
| F90 × time | `1/10` | `+3.489` |
| time only | `1/10` | `+0.898` |

Thus the data distinguish the correct direction/order of the release even
when a reduced cut cannot place the equality point inside the ARA parent.

The cleanest current reading is:

> Arrival time carries the ordering. Energy supplies the additional relation
> needed to separate CEvNS from the large prompt-neutron and steady-state
> mixture and therefore place the handover inside the liquid parent. Pulse
> shape plus time sees the forward release but compresses its inferred mixture
> to the far `2.0` pole. The full relation restores the interior `1.239`
> location.

This is consistent with ARA's general warning that one cut can preserve
direction while losing relational placement. It is **not** a confirmation of
the specific `1.25` law.

## Frozen projection results

| Measurement cut | Best prompt share | Central `x_H` | `Delta NLL` at `1.25` | Exact `1.25` compatible? | Centre in `1.0–1.5`? |
|---|---:|---:|---:|:---:|:---:|
| full 3D | `0.49677` | `1.23883` | `0.00071` | yes | yes |
| energy × time | `0.56788` | `1.35817` | `0.05798` | yes | yes |
| F90 × time | `0.99900` | `1.99893` | `1.91264` | barely | no |
| energy × F90 | weak/flat | `1.82676`* | `0.00002` | uninformatively | no |
| time only | `0.99900` | `1.99893` | `0.85750` | yes | no |
| energy only | weak/flat | `1.77496`* | `0.00014` | uninformatively | no |
| F90 only | weak/flat | `1.96381`* | `0.00006` | uninformatively | no |

`*` The time-free likelihoods are almost flat. Their numerical minima are
optimizer/profile-grid locations, not localized physical estimates.

The prompt share that gives exact `x_H=1.25` under the frozen native timing
bases is `0.503231`.

## Scientific interpretation

### Supported

1. The CENNS-10 record contains a robust native prompt-to-delayed order. The
   correct order beats every shifted control in all four time-bearing cuts.
2. The full 3D cut and the energy × time cut both place the handover on the
   movement-heavy side of the parent ridge and remain compatible with `1.25`.
3. Measurement cuts are not interchangeable: direction can survive while
   internal ARA placement collapses to a pole or becomes unidentifiable.

### Not supported

1. The strong claim that the `1.25` handover is recovered consistently by all
   informative axes through this liquid parent.
2. Treating simple compatibility with `1.25` as evidence that a weak cut found
   it. Several profiles are broad enough to permit almost the entire ARA line.
3. Counting seven correlated cuts through the same 3,752 events as seven
   replications.

### Still open

The exact `1.25` liquid-parent law remains a credible lead because the full 3D
minimum is `1.23883` and the energy × time minimum is `1.35817`, but T374 does
not confirm it. A new event record with the same liquid-parent identity is
still required for prospective confirmation.

## Method and safeguards

- The protocol was frozen and hashed before any projection-specific fit:
  SHA-256 `96186d69e2f1a54cba582d15e7c5d809720f6ce1c47ae21ad2dcceda52019c3a`.
- Every projection used the same five components as T373: prompt CEvNS,
  delayed CEvNS, prompt beam-related neutrons, delayed beam-related neutrons
  and steady-state background.
- Projection centres were obtained from an explicitly profiled prompt share,
  not a single optimiser starting point.
- Profile widths and central locations are reported separately so that a flat
  profile cannot masquerade as a precise hit.
- The source-order control circularly shifted both CEvNS timing branches while
  leaving observed data and background templates fixed.

## Reproduction files

- frozen protocol:
  `T374_LIQUID_ARGON_AXIS_CONSISTENCY_PROTOCOL_2026-08-13.md`;
- protocol hash:
  `T374_LIQUID_ARGON_AXIS_CONSISTENCY_PROTOCOL_2026-08-13.sha256`;
- analysis:
  `t374_liquid_argon_axis_consistency.py`;
- results:
  `T374_LIQUID_ARGON_AXIS_CONSISTENCY_RESULTS.json`;
- cut table:
  `T374_LIQUID_ARGON_AXIS_CONSISTENCY_CUTS.csv`;
- shifted-order controls:
  `T374_LIQUID_ARGON_AXIS_CONSISTENCY_CONTROLS.csv`;
- figure:
  `T374_LIQUID_ARGON_AXIS_CONSISTENCY_FIGURE.png` and `.svg`.
