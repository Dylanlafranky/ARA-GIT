# Q32 — Edge-child pole handover before revisiting 3.5

**Date:** 26 July 2026  
**Ledger:** T286  
**Source:** already-open Q27/Q28 public quantum-network simulator  
**Selected lag:** `1`, selected on development and kept unchanged on evaluation  
**Independent validation:** **PASS — 9/9 checks**  
**Verdict:** **ORDERED CHILD TRANSFER WITHOUT POLE-ORIGIN SUPPORT**

## Result first

Q32 found strong evidence, inside this simulator, for the immediate relation
Dylan asked to isolate before revisiting `3.5`:

> a connection-rich source begins releasing, and the active child sharing its
> named endpoint gains relation amplitude one slice later.

The result survived all incoming-movement and release/accumulation gates on
`23,591` evaluation events across all `200` branch/seed strata. The exact child
beat topology-, seed- and time-displaced controls, with the same positive
direction in both connectivity strata.

The stronger statement that the receiving child is generally **still at the
low ARA pole at the declared source-release slice** did not survive. Only
`43.52%` began at or below `0.5`, versus the frozen `50%` gate, and their median
starting coordinate was `0.6311`.

The most informative secondary result is a clean gradient:

| Child's starting region | Evaluation events | Mean signed gain one slice later |
|---|---:|---:|
| pole, `x <= 0.5` | `10,267` | `+0.19186` |
| lower gradient, `0.5 < x < 1` | `4,838` | `+0.10168` |
| upper gradient, `1 <= x < 1.5` | `3,113` | `+0.01922` |
| crest, `x >= 1.5` | `5,373` | `−0.13716` |

Plainly: children nearest the low pole rise most; children already near the
opposite crest tend to release. The proposed directional ARA gradient is
visible, but the event marked by source release is usually too late to be the
child's true pole-origin slice.

## How the old 3.5 route was implemented

Q30 did not perform a numerical reflection such as `3.5 - x`. It translated
the geometry topologically:

1. source relation \(S=(u,e)\);
2. accumulating child \(C=(e,v)\);
3. unique edge between their nonshared endpoints \(H=(u,v)\).

It called \(H\) the perpendicular `1.5` leg and called the completed
source-to-child span `2` followed by \(H\) the `3.5 = 2 + 1.5` route. The
closing edge did not recover the Q29 residual and Q30 correctly rejected that
implementation.

Q32 changes the order of inquiry without changing Q30:

1. first establish which actual child receives movement;
2. locate where that child begins on its own `0–2`;
3. establish source-out/child-in timing;
4. only then define a crossed-rung `1.5/3.5` continuation from the observed
   route.

## Frozen Q32 construction

For each pair relation, Q32 reused Q27's coordinate:

\[
x_{uv}(t)=
\frac{2|\det C_{uv}(t)|^{1/3}}
{Q_{0.95}\{|\det C_{uv}|^{1/3}:t<250\}}.
\]

A source event required:

- source `x >= 1.5`;
- positive release from `t` to `t+1`;
- Q28's unchanged deterministic one-in-sixteen event sampler.

For each named endpoint, Q32 chose the active adjacent child having the
smallest starting `x(t)`. No later child value participated in selection.
Topology, seed and time controls applied their own corresponding
baseline-only rule.

## Primary evaluation results

### Incoming signed child movement

| Route | Mean signed gain |
|---|---:|
| exact active endpoint child | **`+0.07565`** |
| nonadjacent topology control | `+0.03302` |
| seed-displaced adjacent child | `+0.00700` |
| time-displaced adjacent child | `+0.00491` |

Trial-weighted exact advantages were:

- `+0.04416` over topology;
- `+0.06855` over seed displacement;
- `+0.07150` over time displacement.

All three exceeded the frozen `+0.02` gate. All three trial-cluster bootstrap
probabilities were `1.000`.

### Source-release / child-accumulation overlap

| Route | Mean overlap |
|---|---:|
| exact active endpoint child | **`0.14051`** |
| topology | `0.01965` |
| seed displaced | `0.06785` |
| time displaced | `0.07174` |

The exact relative advantages were approximately:

- `+615.0%` over topology;
- `+107.1%` over seed displacement;
- `+95.9%` over time displacement.

All overlap bootstrap probabilities were `1.000`. The average
exact-minus-control gain remained positive in both connectivity strata:

- `c2`: `+0.06356`;
- `c4`: `+0.05925`.

### Where the child was when the source began releasing

- mean child starting `x`: `1.00494`;
- median: `0.63108`;
- fraction at or below `0.25`: `27.59%`;
- fraction at or below `0.5`: `43.52%`.

The absolute pole-origin gate therefore failed.

The topology pole comparison also failed, but it carries an additional design
caveat. An exact endpoint usually supplies one active candidate, whereas the
topology control selected the minimum from several nonadjacent active edges.
Its mean start was consequently only `0.03697`. Those candidate counts do not
provide equal order-statistic pressure. The protocol is frozen and the failure
is retained; a later topology control must match the exact child's baseline
and candidate count. This caveat does not create the absolute P1 failure, and
it does not explain why the exact child beat the seed/time controls.

## Flow ARA reading

Q32 described the observed source-out/child-in allocation as:

\[
x_{\rm flow}
=
\frac{2A_{\rm child}}{R_{\rm source}+A_{\rm child}}.
\]

Its exact mean was `0.50290` and median `0.30315`, well below the equal-flow
ridge `1.0`.

This is not an energy-conservation measurement. It says that the one selected
child usually receives only part of the normalized movement leaving the
source. That agrees with Q27's earlier result: release propagates into a
distributed web rather than one exclusive recipient.

## ARA and established-data readings

| ARA reading | Established mathematical/data reading |
|---|---|
| Relation movement leaves a high-connection source and enters its active endpoint child. | Conditional on a high starting source and one-step source decline, the exact adjacent active relation gains more closure amplitude than displaced controls. |
| The handover is immediate at this grain. | Development selected lag `1`; the unchanged evaluation half preserved the strongest exact gain there. |
| Pole-near children rise; crest-near children release. | Signed next-slice gain declines monotonically across the four starting-coordinate regions. |
| Most measured children are already beyond their pole when source release is observed. | Median child start is `0.631`; fewer than half are at `x <= 0.5`. |
| One child does not receive the entire source movement. | The descriptive flow coordinate remains below `1`, consistent with distributed propagation and/or different local normalizations. |

## What this adds

Q27 had already shown aggregate release-to-neighbour accumulation above
relation- and time-shuffled nulls. Q32 sharpens that result:

- it identifies an endpoint-specific active child before looking at its
  future;
- it locates that child on its own ARA axis;
- it shows the strongest response at one slice;
- it reveals the gradient from pole-side accumulation to crest-side release;
- it survives seed and time displacement and both connectivity strata.

This is stronger evidence for a local ARA handover in this simulator. It is
not independent-source evidence because Q27–Q32 share one public simulated
dataset.

## Implication for the revised 3.5 test

The best current candidate for the perpendicular leg is no longer the
triangle-closing edge used by Q30. It is the empirically observed
source-to-active-child handover at the shared endpoint.

However, the correct origin of that leg is not yet known. At the source-release
slice, the exact child is commonly already partway up its gradient. The next
test should trace the same selected child backward, using only fixed
pre-event offsets and active-edge history, to ask whether it was closer to the
low pole before the visible source release began.

Only if that prehistory survives matched controls should the new route be
written as:

\[
\text{source span }2
\;+\;
\text{observed cross-scale handover }1.5
\;=\;
\text{candidate }3.5.
\]

## Evidence boundary

Q32 is retrospective on an opened, exactly diagonal simulator. It does not
establish a universal singularity flip, a physical hidden Phase B, literal
energy conservation, an off-diagonal observation channel or a new quantum
law.

## Reproduction

From `analysis/quantum`:

```powershell
python q32_edge_child_pole_handover_test.py
python q32_validate_edge_child_pole_handover.py
python q32_build_notebook.py
```

Primary artifacts:

- `Q32_EDGE_CHILD_POLE_HANDOVER_FIDELITY_v1.md`
- `Q32_EDGE_CHILD_POLE_HANDOVER_PROTOCOL_v1_FROZEN.md`
- `Q32_EDGE_CHILD_POLE_HANDOVER_RESULTS.json`
- `Q32_EDGE_CHILD_POLE_HANDOVER_LAG_CURVE.csv`
- `Q32_EDGE_CHILD_POLE_HANDOVER_TRIALS.csv`
- `Q32_EDGE_CHILD_POLE_HANDOVER_EVENT_SAMPLE.csv`
- `Q32_EDGE_CHILD_POLE_HANDOVER_GRADIENT.csv`
- `Q32_EDGE_CHILD_POLE_HANDOVER_GEOMETRY.png`
- `Q32_EDGE_CHILD_POLE_HANDOVER_VALIDATION.json`
- `Q32_EDGE_CHILD_POLE_HANDOVER_NOTEBOOK.ipynb`

