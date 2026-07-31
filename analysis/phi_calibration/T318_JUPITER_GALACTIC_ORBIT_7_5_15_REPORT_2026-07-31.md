# T318 — Jupiter–Sun Galactic-Orbit 7.5/15 ARA Test

**Date:** 31 July 2026  
**Frozen protocol:** `T318_JUPITER_GALACTIC_ORBIT_7_5_15_PROTOCOL_v1_REGISTERED.md`  
**Robust verdict:** `7.5/15 NOT SUPPORTED`

## Technical summary

Repeating T309 with Jupiter instead of Earth did **not** reproduce the
predeclared `7.5° : 15°` geometry. In the rounded T309 parent frame the
largest branch angle was `3.4064°` and the largest
opposite-branch aperture was `6.4927°`. In the
modern measured Galactocentric frame they were
`3.1452°` and
`6.0042°`.

The outcome is close to the speed-ratio expectation recorded before the
calculation: Jupiter’s smaller orbital speed produces a smaller angular
opening against the same Galactic translation. This makes the earlier
Earth `7.5 : 15` recurrence planet- and frame-dependent rather than a
universal Solar-System cadence.

## What was measured

JPL Horizons Sun and Jupiter-system-barycentre vectors share the same
five-day timestamps. Subtracting the Sun vector produced Jupiter’s
Sun-relative position and velocity. Data before 1950 estimated the orbital
period; data from 1950 onward were held out for the angle test.

The calibration-only period was
`4332.5126 days`
(`11.861773 years`). The median held-out
Jupiter speed was `13.0512 km/s`.

## Frozen-target results

| Parent frame | median α | maximum α | median β | maximum β | scalar α | verdict |
|---|---:|---:|---:|---:|---:|---|
| Rounded T309 | 3.0530° | 3.4064° | 6.1013° | 6.4927° | 3.2438° | NOT SUPPORTED |
| Modern measured | 2.8440° | 3.1452° | 5.6714° | 6.0042° | 3.0012° | NOT SUPPORTED |

Neither the median gate nor the repeated cycle-envelope gate passed in
either frame. The rounded frame had
`0/12`
complete cycles passing both crest targets; the modern frame had
`0/12`.

## ARA interpretation

The ARA construction still gives a clean paired child around the parent
direction: the two half-orbit branches remain close to an ARA `1.0` balance
when normalized against each other, and the directly measured aperture is
close to their angular sum. What does **not** survive is the specific
`7.5° : 15°` size.

Plainly: Jupiter traces the same kind of child-on-parent geometry as Earth,
but its sphere opens by a smaller amount because its Sun-relative movement
is smaller beside the Galactic parent movement. The repeating relationship
is the branch/aperture construction; `7.5/15` is not a scale-free constant
of that construction.

## Limitations and robustness

- The Galactic vectors are treated as fixed over the 151-year evaluation
  interval, which is adequate for this local construction but is not a full
  Galactic orbit model.
- Linear interpolation is used at the calibration-derived half period.
- This test concerns the Jupiter-system barycentre, not the motion of
  Jupiter’s centre relative to its satellites.
- The ARA pair sum of two is forced by normalization and is not evidence.

## Recommended next step

Treat the result as a useful falsification of a planet-independent
`7.5 : 15` claim. If the broader ARA question is continued, the stronger
test is to predeclare the child/parent speed-ratio scaling law and evaluate
it across all planets, rather than continuing to search for the fixed
Earth-sized angle in each orbit.
