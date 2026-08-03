# ENSO three-tier inflow geometry — consultation draft

**Date:** 3 August 2026  
**Geometry supplied by:** Dylan La Franchi  
**Status:** parent poles and grandchild identity geometry **confirmed by Dylan**;
individual observable cuts and causal-test gates remain to be frozen separately

## Confirmed parent orientation

Dylan selected the most direct human/scientific ENSO distinction as the
parent ARA:

\[
\boxed{
0=\text{La Niña pole},
\qquad
2=\text{El Niño pole}
}
\]

with the reverse orientation mathematically equivalent if declared in advance.
The neutral ENSO range is initially treated as the mixed/ridge neighbourhood
between the two poles. This does **not** mean that every conventionally neutral
month is assumed to be an exact physical `1.0` cancellation ridge; that is a
measurement question for the test.

## Why this draft exists

T336/T337 incorrectly compressed ENSO into two convenient, same-scale
perpendicular variables. The replacement does not begin from data columns. It
begins from the ARA identity hierarchy and then asks which observations measure
each part.

## Three generations

The declared minimum hierarchy is now:

```text
Tier 0 / parent:                    ENSO
                                  /    \
Tier 1 / children:          La Niña    El Niño
                              (A)        (B)
                             /   \      /   \
Tier 2 / grandchildren:    AA   AB    BA   BB
```

This is three generations when the ENSO parent is counted: one parent, two
children and four grandchildren. Every node is an identity with its own ARA,
not merely a component to be averaged away.

## Confirmed grandchild identity map

The most direct physical decomposition available from established ENSO
observations is that both La Niña and El Niño have a coupled oceanic expression
and atmospheric expression. Dylan confirmed the following ARA translation on
3 August 2026:

| Parent child | Proposed Phase-A grandchild | Proposed Phase-B grandchild |
|---|---|---|
| La Niña / A | La Niña ocean state: cooler central/eastern surface, enhanced eastern upwelling/shallow thermocline, warm-water displacement toward the west | La Niña atmosphere state: stronger easterly trades, pressure/convection/rainfall displacement |
| El Niño / B | El Niño ocean state: warmer central/eastern surface, reduced upwelling/deeper eastern thermocline, eastward warm-water displacement | El Niño atmosphere state: weaker or reversed trades, pressure/convection/rainfall displacement |

This table is now the frozen identity geometry. It does not assume that the
oceanic and atmospheric manifestations have equal raw scale. Any rung
difference must be measured and translated before their ARA is formed. A
specific measurement may still be rejected without changing the identity tree.

This choice is attractive because it keeps the parent opposition as La Niña
versus El Niño while preserving the ocean-atmosphere feedback inside each pole.
It also gives four distinct grandchild streams instead of reusing NINO3.4 or
WWV for several roles.

Let the four grandchild ARA readings be

\[
x_{AA},\;x_{AB},\;x_{BA},\;x_{BB}\in[0,2].
\]

The two child relations are retained separately:

\[
D_A=(x_{AA},x_{AB}),
\qquad
D_B=(x_{BA},x_{BB}).
\]

The parent structural state is therefore a nested relation:

\[
\boxed{D_{\mathrm{state}}=(D_A,D_B)}.
\]

This notation is a scaffold only. It does not assume ordinary addition,
equal scales, perpendicular physical variables or a particular decoder.

## The independent inflow cut

Static composition is not enough. Each grandchild also receives, stores,
passes or releases a measurable flow. Denote the declared inflow/traversal
reading of each grandchild by

\[
f_{AA},\;f_{AB},\;f_{BA},\;f_{BB}.
\]

Their nested flow relation is

\[
F_A=(f_{AA},f_{AB}),
\qquad
F_B=(f_{BA},f_{BB}),
\]

and

\[
\boxed{D_{\mathrm{flow}}=(F_A,F_B)}.
\]

The moving ENSO description is then the relation between the structural
Di-ARA and the inflow Di-ARA:

\[
\boxed{M_{\mathrm{ENSO}}=(D_{\mathrm{state}},D_{\mathrm{flow}})}.
\]

In Dylan's language, this is the **Di-ARA of the Di-ARA in motion**. The first
side says where the nested identities currently sit; the second follows the
energy/participation stream moving through them.

## Required causal walk

The test must follow the stream rather than jump directly from inputs to a
future ENSO label:

```text
grandchild inflow
    -> grandchild ARA movement
    -> corresponding child accumulation/release
    -> child ARA movement
    -> ENSO-parent accumulation/release
    -> observed ENSO expression
```

Each arrow receives its own delay, orientation and scale declaration. A parent
ridge is not allowed to erase child asymmetry. The first scientific target is
whether the stream propagates through the declared route in the correct order;
forecasting the final ENSO value comes only after that transport is supported.

## Nearby-scale coupling

The four-grandchild tree is the minimum internal identity. ENSO may also receive
same-rung, upper-rung or lower-rung coupling from nearby systems. These must be
measured separately as external or `Other` participation until their rung and
route are demonstrated. They must not be forced into Phase A or Phase B simply
because a data series is available.

Potential observational families to evaluate, not yet assign, include:

- basin-wide, western and eastern warm-water volume;
- thermocline depth and upper-ocean heat content;
- sea-surface temperature and zonal SST gradient;
- trade winds and equatorial zonal wind stress;
- atmospheric pressure/SOI and convection/OLR;
- westerly wind bursts and MJO-scale activity;
- seasonal forcing, PDO/IPO, IOD and off-equatorial heat transport as possible
  nearby-scale couplings.

NINO3.4 is an observed ENSO expression. It is not automatically the whole ENSO
parent or one of its fundamental children.

## Proposed inflow families for the four grandchildren

The state measurement and its inflow measurement must remain different:

| Provisional grandchild | State candidates | Inflow/traversal candidates |
|---|---|---|
| La Niña ocean | Niño-region SST gradient, east/west thermocline depth, east/west WWV | westward warm-water transport, upwelling, zonal/meridional heat-content change |
| La Niña atmosphere | SOI/pressure gradient, trade-wind state, convection/OLR | easterly wind-stress change and movement of the convection centre |
| El Niño ocean | Niño-region SST gradient, east/west thermocline depth, east/west WWV | eastward warm-water/Kelvin-wave transport, WWV discharge, reduced upwelling |
| El Niño atmosphere | SOI/pressure gradient, trade-wind state, convection/OLR | westerly wind bursts, trade-wind weakening and movement of the convection centre |

These streams form a feedback circuit rather than a one-way list. The test must
retain the ordering of atmosphere-to-ocean and ocean-to-atmosphere handovers
instead of averaging them into one simultaneous correlation.

## Existing local evidence and measurement gap

The current archive contains NINO3.4, full/east/west warm-water volume, SOI,
MJO, IOD and PDO records. Earlier diagnostics already found:

- basin warm-water-volume discharge can precede surface ENSO development;
- east/west WWV contains an orientation distinction;
- faster and slower WWV response shapes are distinguishable in some eras;
- repeatedly using WWV as feeder, intermediate and later reservoir fails to
  distinguish the required rungs;
- the archive does not yet contain a proven independent rung directly beneath
  WWV.

The most useful additions are therefore independent thermocline, upper-ocean
heat-content, equatorial wind-stress and westerly-wind-burst measurements at
the finest reliable cadence.

## Geometry confirmation and remaining measurement gate

Before a numerical protocol is frozen, the following must be resolved:

1. ~~what the two ENSO-scale Phase A and Phase B identities are;~~ **resolved:**
   La Niña and El Niño;
2. ~~what the two grandchildren of each identity are;~~ **resolved:** oceanic
   expression and atmospheric expression under both parent poles;
3. which measurements are state cuts and which are inflow cuts;
4. the expected ordering, flips and rung relations;
5. which surrounding systems enter as nearby-scale coupling rather than as an
   internal child.

Codex then translates that confirmed geometry into equations, causal controls
and falsification gates. No replacement ENSO run is authorized by this draft.

The identity geometry in items 1–2 is confirmed. Items 3–5 are measurement and
test-design questions: they may change which public series are admitted, but
they must not silently rewrite the confirmed tree.
