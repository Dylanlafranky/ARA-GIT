# T309 — Galactic-Orbit 7.5/15 ARA Geometry

**Date:** 31 July 2026  
**Registered verdict:** **STABLE CREST/ENVELOPE RECURRENCE**  
**Evidence class:** exact-3D confirmation after a known scalar clue; not blind

## Plain-language result

The exact 3D orbit does reproduce the 7.5°/15° neighbourhood, but as the stable outer crest of the yearly motion—not as its typical or median angle.

That registered result does **not** survive the stronger post-result
robustness audit. The `230.28 km/s` value is a rounded NASA public-facts
description. A modern astrometric construction using Sgr A*'s measured reflex
proper motion and the GRAVITY Galactic-centre distance gives a Solar velocity
of `248.931 km/s` in a slightly
different three-dimensional direction. Under that vector:

- maximum alpha = `6.9602°`;
- maximum beta = `13.6357°`;
- verdict = `NOT SUPPORTED`.

The scientifically controlling conclusion is therefore:
**simplified-frame envelope recurrence; not robust as the best available
Galactocentric orbit estimate**.

The simple calculation
`atan(Earth orbital speed / Galactic parent speed)` gives
`7.3679°`, whose doubled value is
`14.7358°`. Once the real orbital-plane
orientation and the changing three-dimensional Earth velocity are restored,
the evaluation median moves inward:

- branch inclination alpha: median `7.0274°`, range
  `5.8898°` to `7.5192°`;
- independently measured opposite-branch aperture beta: median
  `13.8066°`, range `12.8021°` to
  `14.7260°`.

The central registered gate therefore
`did not pass`. The yearly crest
gate passed in `12/12` complete evaluation years.

## What the geometry actually says

The 7.5° value is not the orbit's constant pitch. The branch breathes across
the year because the ecliptic is tilted relative to the declared Galactic
travel direction and because Earth's orbital speed varies. In the primary
frame, the outer branch reaches `7.5192°`; the full Phase A/Phase B
aperture reaches `14.7260°`.

The directly measured aperture is almost exactly the sum of the two
parent-relative branch angles:

```text
median beta - (alpha_A + alpha_B)
= -0.0009363 degrees
```

That is a clean geometric decomposition of two opposite child branches around
one parent traversal axis. It is established vector geometry; calling it an
ARA parent/child crosswalk is the framework interpretation.

The normalized pair coordinate had median
`0.998954` and range
`0.919725` to `1.080314`. Its
TE-ARA sum of two is imposed by normalization, so that sum is bookkeeping,
not independent evidence. The observed branch variation is the informative
part.

## Frame and speed controls

The result is relational, not absolute. In the CMB control frame:

- median alpha = `3.3330°`;
- maximum alpha = `4.6544°`;
- median beta = `6.6719°`;
- maximum beta = `9.2406°`.

The CMB control verdict is `NOT SUPPORTED`. Therefore the Galactic result
must not be described as a universal angle of Earth's motion. It belongs to
the declared child-orbit/parent-Galactic-travel relation.

The sensitivity table records the same Galactic direction from `200` through
`369 km/s`. This matters because the published `829,000 km/h` parent speed is
rounded and a different Galactic velocity convention changes the angle.

The modern measured-vector audit is not part of the originally registered
primary frame; it was added because the fixed speed sensitivity showed that
the result depended materially on the rounded parent speed. It is a required
post-result correction, not a second frozen prediction.

## ARA reading

The strongest faithful ARA statement is:

\[
\underbrace{\mathbf V_{\rm parent}}_{\text{larger traversal}}
+
\underbrace{\mathbf v_{\rm child}(t)}_{\text{0→2→0 orbit}}
\longrightarrow
\underbrace{\mathbf v_\oplus(t)}_{\text{extruded child path}}.
\]

The earlier `7.5 : 15` cadence reappears in the simplified `230 km/s`
Galactocentric construction as a stable upper envelope. It does **not**
survive the best measured parent vector, and therefore cannot currently be
claimed as an orbital recovery. What does survive is the ARA-shaped
decomposition itself: one parent direction, two opposite child branches, an
almost exact branch-sum aperture and a periodically breathing asymmetry.

## Sources

- [NASA Solar System Facts](https://science.nasa.gov/solar-system/solar-system-facts/)
  — Solar System Galactic speed and period.
- [NASA Reference Systems](https://science.nasa.gov/learn/basics-of-space-flight/chapter2-1/)
  — Earth orbital-speed range.
- [NASA/JPL Horizons](https://ssd.jpl.nasa.gov/horizons/)
  — retained Earth-relative-to-Sun Cartesian vectors.
- [ESA Planck CMB velocity result](https://sci.esa.int/s/WLdyMrW)
  — CMB-frame control speed and direction.
- [Reid & Brunthaler (2020)](https://arxiv.org/abs/2001.04386)
  — measured Sgr A* reflex proper motion.
- [GRAVITY Collaboration (2019)](https://arxiv.org/abs/1904.05721)
  — geometric Galactic-centre distance used to convert proper motion to speed.
- [Schönrich, Binney & Dehnen (2010)](https://academic.oup.com/mnras/article/403/4/1829/1054839)
  — local Solar radial component and peculiar-motion reference.

## Reproduction

```powershell
python t308_phi_temporal_ruler_orbital_probe.py --fetch
python t309_galactic_orbit_7_5_15.py
python validate_t309_galactic_orbit_7_5_15.py
```

Source SHA-256:
`fa93fb2c2a4f55c4a5b19355b8c54a57b6e527ce6a72bd94a84efa40dcf85199`.
