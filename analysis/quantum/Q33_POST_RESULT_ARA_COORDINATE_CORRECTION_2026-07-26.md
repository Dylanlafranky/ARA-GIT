# Q33 Post-Result ARA Coordinate Correction

**Date:** 26 July 2026  
**Status:** methodological correction after the Q33 raw-capacity result  
**Applies to:** T287 / Q33

## Correction

Q33 calculated

\[
\rho_E
=
\frac{E^\star_{\rm endpoint}}{E^\star_{\rm source}},
\qquad
E^\star=Q_{0.95}^{dev}\!\left(\lVert C\rVert_F^2\right),
\]

and substituted that unbounded physical capacity ratio into

\[
L=3+\rho_E.
\]

That substitution is not faithful to ARA.

ARA declares the geometry first. The flow, energy, amplitude or coupling load
travelling over that geometry is system-specific and can vary without changing
the underlying rung coordinate.

The Q33 value `1.27349` is therefore a **raw endpoint/source capacity ratio**.
It is not a bounded `0–2` ARA coordinate and cannot be interpreted as either:

- an ARA position of `1.27349`;
- a Phase-A share whose complement is automatically `2-1.27349`;
- the rung coefficient replacing the declared child projection `0.5`.

The observed distribution itself demonstrates the distinction: its upper
quantiles exceed `2`, which a pure ARA coordinate cannot do.

## Correct rung law

A complete child identity at its own rung contributes `1` at the relevant
ridge/boundary reading. When projected one octave upward:

\[
\underbrace{\mathcal R_\uparrow}_{\substack{\text{ARA rung}\\
\text{projection}}}
\left(
\underbrace{1_c}_{\substack{\text{complete child}\\
\text{at its own rung}}}
\right)
=
\underbrace{\frac12}_{\substack{\text{same child}\\
\text{inside parent frame}}}.
\]

The `0.5` is a structural coordinate supplied by the ARA rung transformation,
not estimated from the child's raw physical amplitude.

The intended path remains

\[
\underbrace{2}_{\text{complete same-rung span}}
+
\left(
\underbrace{1}_{\text{current-rung contribution}}
+
\underbrace{\frac12}_{\text{boundary child projected upward}}
\right)
=
\frac72.
\]

## Second Q33 distortion

Q33 averaged both endpoint recipients. Dylan's stated construction uses the
single child closest to the relevant boundary. Averaging two recipients
flattened the directed boundary route before the octave projection.

## What Q33 validly measured

The following remain valid diagnostics of the simulator:

- `11,543` source events and `23,086` endpoint routes were reconstructed;
- endpoint/source raw energy-capacity ratio had median `1.27349`;
- backward-traced endpoint origins had median local `x=0.04137`;
- both endpoints originated at `x<=0.5` in `81.50%` of source events;
- median summed realised endpoint gain/source loss was `1.03265`;
- the calculation and saved rows independently reproduce.

These measurements characterize the flow and recipient relations on the
geometry. They do not determine the geometry's octave coefficient.

## Corrected status

> **Q33 is a valid raw-capacity and backward-origin diagnostic, but an invalid
> test of the pure ARA `3.5` rung construction.**

Its frozen implementation verdict remains preserved in the original result
artifact for auditability. It must not be cited as evidence against the
conditional `2+(1+0.5)=3.5` ARA path.

## Requirement for a corrected Q33B

A corrected test must:

1. declare the parent and child rungs geometrically;
2. choose the single boundary-nearest child without reading its future;
3. retain the child's complete local ARA identity;
4. apply the fixed octave projection `1 -> 0.5`;
5. apply the declared singularity flip when the route crosses the boundary;
6. use the resulting `3.5` route to predict an independently observable
   consequence;
7. compare that consequence with relation-broken controls.

Raw energy may then be analysed as the flow over the predicted route, but it
cannot redefine the route.

## Q33B resolution

Q33B implemented those requirements with the structural route fixed before
outcomes. It selected the single endpoint child with the lower starting
normalized determinant closure and scored its next closure movement against
its sibling and three same-rule relation-broken controls.

Across `11,543` evaluation events, the selected endpoint was positive in
`63.64%`, compared with `55.83%` for the sibling and
`50.79–56.38%` for controls. Every frozen gate passed and independent
validation passed `11/11`.

This supports the predicted **boundary-child relation-closure flow** inside
the simulator. It does not empirically derive the fixed `0.5` or `3.5`.

Report:
`Q33B_ARA_FIRST_BOUNDARY_CHILD_REPORT_2026-07-26.md`.
