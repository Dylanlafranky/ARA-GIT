# T318 — Jupiter–Sun Galactic-Orbit 7.5/15 ARA Test

**Registered:** 31 July 2026  
**Status:** frozen before numerical evaluation  
**Relationship to earlier work:** exact T309 construction with the
Earth–Sun child replaced by the Jupiter-system-barycentre–Sun child  
**Primary question:** does Jupiter’s Sun-relative orbital child, carried
through the same Galactic parent translation used by T309, reproduce the
previously declared `7.5° : 15°` branch/aperture geometry?

## Evidential boundary

This is not a blind discovery of `7.5 : 15`. The target and tolerances come
unchanged from T309. Before this protocol was frozen, a speed-ratio
reasonableness check suggested that Jupiter’s approximately `13 km/s`
orbital speed against a `230–249 km/s` parent should ordinarily produce a
smaller angle near `3°` and an opposite-branch aperture near `6°`.

Therefore:

- a recurrence near `7.5° : 15°` would be surprising under the simple
  velocity-ratio explanation;
- a result near `3° : 6°` would support the interpretation that T309’s
  angles scale mainly with child/parent speed rather than forming a
  planet-independent cadence;
- no post-result rotation, target change, fitted parent direction or Earth
  term is permitted.

## Public source and child construction

The retained public source is NASA/JPL Horizons:

- Sun target `10` relative to Solar-System barycentre `500@0`;
- Jupiter-system-barycentre target `5` relative to `500@0`;
- `1900-01-01` through `2101-01-01`;
- five-day cadence, TDB;
- geometric Cartesian vectors in ecliptic ICRF/J2000 axes;
- kilometres and seconds.

At every shared timestamp:

\[
\mathbf r_{J|\odot}(t)=\mathbf r_{J|SSB}(t)-\mathbf r_{\odot|SSB}(t),
\]

\[
\mathbf v_{J|\odot}(t)=\mathbf v_{J|SSB}(t)-\mathbf v_{\odot|SSB}(t).
\]

No Earth vector enters the calculation.

## Frozen frames

### T309 rounded Galactic tangent

The first parent is T309’s local circular Galactic tangent:

- Galactic direction \((l,b)=(90^\circ,0^\circ)\);
- speed `829,000 km/h = 230.2777777778 km/s`;
- unit vector in ecliptic J2000 coordinates fixed to
  `(0.4941094279, -0.1109907334, 0.8622858751)`.

### Modern measured Galactocentric control

The controlling robustness frame is the same T309 modern measured vector:

- speed `248.9314202892 km/s`;
- unit vector in ecliptic J2000 coordinates fixed to
  `(0.4612905078, -0.1551427763, 0.8735798683)`.

The rounded frame is retained for an exact historical crosswalk. A positive
scientific conclusion requires survival in the modern measured frame.

## Calibration and evaluation split

- Calibration: timestamps before `1950-01-01`.
- Evaluation: timestamps on or after `1950-01-01`.
- Jupiter’s period \(P_J\) is estimated only from calibration positions by
  fitting the long-run slope of unwrapped ecliptic longitude.
- The opposite branch is evaluated at \(t+P_J/2\) using deterministic linear
  interpolation of the stored Jupiter–Sun velocity.
- Only evaluation rows whose opposite timestamp remains inside the stored
  source interval are eligible.

## Frozen measurements

For a declared Galactic parent vector \(\mathbf V\),

\[
\mathbf u(t)=\mathbf V+\mathbf v_{J|\odot}(t).
\]

The branch-to-parent angle is

\[
\alpha(t)=
\cos^{-1}
\frac{\mathbf u(t)\cdot\widehat{\mathbf V}}
{|\mathbf u(t)|}.
\]

The directly measured opposite-branch aperture is

\[
\beta(t)=
\cos^{-1}
\frac{\mathbf u(t)\cdot\mathbf u(t+P_J/2)}
{|\mathbf u(t)|\,|\mathbf u(t+P_J/2)|}.
\]

The descriptive ARA pair is

\[
x_A(t)=
\frac{2\alpha(t)}
{\alpha(t)+\alpha(t+P_J/2)},
\qquad
x_B(t)=2-x_A(t).
\]

The equality \(x_A+x_B=2\) is forced bookkeeping, not a test result.

## Frozen gates

Targets and tolerances remain exactly those of T309:

- branch target: \(\alpha=7.5^\circ\), tolerance `±0.25°`;
- aperture target: \(\beta=15.0^\circ\), tolerance `±0.5°`.

### Central cadence supported

Both evaluation medians fall inside their target tolerances.

### Stable crest/envelope recurrence

The central gate fails, but in at least `9/12` consecutive complete
evaluation Jupiter cycles:

- cycle maximum \(\alpha\) lies inside `7.5° ± 0.25°`; and
- cycle maximum \(\beta\) lies inside `15° ± 0.5°`.

Cycles are fixed from the evaluation start using the calibration-only period.
A complete cycle must contain at least 80% of the expected five-day samples.
If fewer than 12 complete cycles are available, the stable-envelope gate is
not evaluated as passed.

### Not supported

Neither gate passes.

### Robust conclusion

The `7.5 : 15` recurrence is robust only if a support gate passes in the
modern measured Galactocentric frame. A pass only in the rounded historical
frame is reported as frame-sensitive and not robust.

## Fixed outputs and checks

For both parent frames:

1. full distribution summaries for \(\alpha\), opposite \(\alpha\), \(\beta\),
   closure residual and \(x_A\);
2. fraction of eligible samples inside each target window;
3. per-cycle medians and maxima;
4. central and stable-envelope gate results;
5. scalar speed-ratio comparison
   \(\tan^{-1}(\operatorname{median}|\mathbf v_{J|\odot}|/|\mathbf V|)\);
6. independent validation of hashes, row alignment, period, angles, gates
   and output files.

## Reproduction contract

```powershell
python t318_jupiter_galactic_orbit_7_5_15.py
python validate_t318_jupiter_galactic_orbit_7_5_15.py
```

The analysis script may read the registered protocol and the retained JPL
files. The independent validator must not import the analysis module.
