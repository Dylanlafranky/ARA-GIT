# H2 Fidelity Packet — Rønne Å motion, structure, and thalweg cuts

**Claim ID:** H2 / v1  
**Frozen:** 2 August 2026, before downloading or opening the target measurement files  
**Dylan verdict:** `EXACT ENOUGH TO TEST` — confirmed in ordinary language, with the dedicated thalweg cut added

> **POST-RUN DYLAN CORRECTION — 2 August 2026:** Phi must be cut **with**
> the direction of travel. H2 v1 used a bank-to-bank diameter perpendicular
> to travel. Even its thalweg panel plotted the lateral deepest-point
> coordinate against downstream chainage; it did not measure a longitudinal
> handover coordinate. Therefore H2 v1 is retained as
> `PROXY TEST — WRONG AXIS FOR LONGITUDINAL PHI`. Its perpendicular
> cross-section measurements remain reproducible, but they are not evidence
> for or against the intended Phi-motion claim.

## USER PRIOR — verbatim source

> “0.3 something is also the mirror point on the rung from Phi for the space side wave. And I have said that 3/8 is Phi cooled down and represented as connection before.”

> “why don't we test something in motion, we know it sort of works with rivers and the Thaumaturge(?), so maybe we have to look for the motion in something in motion like that.”

> “Yes. We also have to do a dedicated cut of the thalweg as that is directly PPhi I have been told, so we can see what it turns out with.”

## Identity and declared ARA relation

- **Parent identity:** one measured river cross-section.
- **ARA diameter:** bank-to-bank lateral position, mapped linearly to `0..2` in the source's fixed downstream-facing orientation.
- **Symmetry:** raw orientation is retained. Candidate scoring may use the two declared mirror locations, never a post-result side flip.
- **Motion child:** the measured downstream-velocity field in that cross-section.
- **Connection child:** the measured bed/bathymetry field in that cross-section.
- **Longitudinal identity:** the ordered line joining successive deepest-bed locations is the dedicated thalweg cut.

## Frozen observables

For every eligible cross-section:

1. `x_flow`: raw `0..2` lateral coordinate of maximum measured downstream velocity.
2. `x_depth`: raw `0..2` lateral coordinate of maximum measured depth (or minimum surveyed bed elevation, according to the source convention).
3. `x_thalweg`: the ordered sequence of `x_depth` values across source-defined cross-sections. This receives a dedicated path view and candidate-distance table.

The thalweg view is **not independent evidence** when it contains the same deepest points as `x_depth`. It becomes an additional empirical cut only if the public bathymetry supplies denser source-defined longitudinal slices that can be extracted without fitting the target constant.

## Frozen candidate geometry

The motion/handover candidate is

\[
h_\phi=2-\phi=0.38196601125,
\qquad
H_\phi=2-h_\phi=1.61803398875.
\]

The accumulated/connection candidate is

\[
h_{3/8}=3/8=0.375,
\qquad
H_{3/8}=2-h_{3/8}=1.625.
\]

For raw coordinate `x`, symmetric candidate loss is fixed as

\[
d_c(x)=\min\{|x-c|,\ |x-(2-c)|\}.
\]

Controls are fixed at `1/3`, `0.4`, `0.5`, and ridge `1.0`, each mirrored in the same way where applicable.

## Predictions and gates

1. **Resolution gate:** the source coordinate uncertainty/resolution must be materially smaller than
   \(|(2-\phi)-3/8|=0.00696601125\) ARA units. Otherwise the Phi-versus-`3/8` distinction is `INCONCLUSIVE`.
2. **Motion gate:** `x_flow` is closer to the mirrored Phi pair than to the mirrored `3/8` pair and fixed controls on held-out eligible cross-sections.
3. **Connection gate:** `x_depth` is closer to the mirrored `3/8` pair than to the mirrored Phi pair and fixed controls on held-out eligible cross-sections.
4. **Dedicated thalweg gate:** report the untouched ordered `x_thalweg` path against all candidates. A Phi result requires Phi to win without redefining thalweg, orientation, normalization, or smoothing after reveal.
5. **Coupling diagnostic:** report the signed and absolute lateral separation between `x_flow` and `x_depth`; this is descriptive and cannot rescue a failed landmark gate.

With only a few cross-sections, exact per-section results and leave-one-section-out sensitivity take precedence over asymptotic p-values.

## Plain restatement

At each river slice, ask where the moving current concentrates and where the accumulated channel structure concentrates. Put both on the same bank-to-bank ARA diameter. Test whether motion prefers the anti-Phi/Phi handover locations while cooled structure prefers `3/8`; then show the deepest-channel line separately so its own result is visible rather than assumed.

## Mathematical back-translation

Two fields measured over the same river width produce two peak-location coordinates. Their distances to predeclared symmetric landmarks are compared without rotating or rescaling the river after seeing the answer. The deepest points are also displayed in longitudinal order, but duplicate points do not count twice as evidence.

## AI additions and discarded information

- **AI addition:** maximum downstream velocity is the operational motion-core proxy.
- **AI addition:** maximum depth/minimum bed elevation is the operational accumulated-structure proxy.
- **AI addition:** fixed symmetric control landmarks and a resolution kill gate.
- **Discarded:** full velocity-vector orientation, turbulence, discharge magnitude, depth magnitude, sediment history, and continuous time evolution.
- **Important scope fence:** this is a spatial motion/structure probe. It does not by itself establish that a velocity maximum is the complete temporal Phi handover.

## Forbidden substitutions

- Mean or median velocity magnitude in place of the location of the velocity core.
- Cumulative-discharge midpoint in place of the raw velocity maximum.
- A smoothed, fitted, Fourier, wavelet, PCA, or learned coordinate selected because it approaches Phi or `3/8`.
- Reorienting individual sections after reveal so the winning side always appears on the same pole.
- Treating literal `0.375` values in source coordinates as evidence without the frozen bank-to-bank normalization.
- Counting the same deepest points once as structure and again as an independent thalweg replication.
- Calling insufficient spatial resolution a positive or negative landmark result.

## Falsifier

The numerical duality is not supported in this realization if eligible held-out motion locations do not prefer Phi, eligible held-out structural locations do not prefer `3/8`, or a fixed rival wins. If the data cannot resolve the two landmarks, the correct verdict is `INCONCLUSIVE`, not support and not falsification.

## Post-run construct verdict

`PROXY TEST — WRONG AXIS FOR LONGITUDINAL PHI.`

The frozen calculations answer where flow and depth maxima sit **across** a
river. Dylan's intended Phi object travels **along** the river. No numerical
outcome from H2 v1 may be promoted as a test of that corrected object. A v2
packet must freeze a longitudinal identity, start/end poles and handover
observable before another dataset is opened.
