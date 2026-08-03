# T319 — Pentagon Phi-Pillar / Two-ARA Hexagon Geometry

**Date:** 31 July 2026  
**Status:** **EXACT CONSTRUCTION SUPPORTED (13/13); INDEPENDENT VALIDATION 23/23**  
**Evidence class:** exact geometry and ARA internal-consistency crosswalk; not
an empirical observation of a physical mechanism

## Question

Can Dylan's proposed Hexagon/Pentagon geometry be constructed without fitting
numbers after the fact?

The frozen proposal was:

1. normalize each local Phase step to length `1`;
2. let the complete mixed route (A_0\rightarrow B\rightarrow A_1) have length
   (1+1=2);
3. test whether the direct same-phase route (A_0\rightarrow A_1) is
   (phi);
4. test whether the unused seam inside the full path is
   (2-phi=phi^{-2}\approx0.382);
5. test whether repeating the same construction produces a pentagonal,
   recursively scaled scaffold;
6. construct the proposed hexagonal parent from two three-direction
   Information³ closures offset by (60^\circ);
7. compare the pentagon with regular-polygon controls rather than assuming it
   in advance.

## Exact construction

Take a regular pentagon whose side length is `1`. Select three consecutive
vertices and label them (A_0,B,A_1).

The route along the two adjacent sides is

\[
\underbrace{|A_0B|}_{1}+\underbrace{|BA_1|}_{1}=2.
\]

The direct line joining the two same-phase vertices is a regular-pentagon
diagonal. Its length is exactly

\[
\underbrace{|A_0A_1|}_{\text{direct same-phase path}}
=\phi
=1.618033988749895\ldots
\]

Therefore the part of the complete length-two route not occupied by the
direct diagonal is

\[
\underbrace{2-|A_0A_1|}_{\text{seam}}
=2-\phi
=\phi^{-2}
=0.381966011250105\ldots
\]

This gives the exact ARA identity

\[
\boxed{\phi+\phi^{-2}=2}.
\]

## Pentagon recursion

Draw all five diagonals. They form a pentagram. Every proper intersection
divides the participating diagonals in the golden ratio, and the intersections
form a new inner pentagon.

With the outer side normalized to `1`, the inner pentagon's side is

\[
\phi^{-2}=0.381966011250105\ldots
\]

Repeating the construction yields the scale sequence

\[
1,\ \phi^{-2},\ \phi^{-4},\ \phi^{-6},\ \phi^{-8},\ \phi^{-10},\ldots
\]

Numerically:

| recursion level | scale |
|---:|---:|
| 0 | 1.000000000 |
| 1 | 0.381966011 |
| 2 | 0.145898034 |
| 3 | 0.055728090 |
| 4 | 0.021286236 |
| 5 | 0.008130619 |

This is the clean mathematical sense in which the five diagonals may be
called recursive **Phi pillars**: the long same-phase paths have length
(phi), and their intersections generate the next pentagonal rung at
(phi^{-2}) of the preceding scale.

## Angle correction

The earlier provisional record mixed two different circle normalizations.
T319 fixes the construction to a **regular pentagon with side length `1`**.
In this tested embedding:

- adjacent pentagon vertices are separated by a (72^\circ) central step;
- the pentagon interior angle is (108^\circ);
- the (phi)-length diagonal spans (144^\circ) at the centre;
- (36^\circ) is the half-step identity in
  (phi=2\cos36^\circ).

It is separately true that a chord of length (phi) in a *unit-radius circle*
subtends (108^\circ). That is not the same normalization as the tested
side-one regular pentagon and must not be used as its diagonal angle.

## Two-ARA hexagonal parent

The first three-direction closure was placed at

\[
0^\circ,\ 120^\circ,\ 240^\circ,
\]

and its coupled partner at

\[
60^\circ,\ 180^\circ,\ 300^\circ.
\]

Their union is

\[
0^\circ,\ 60^\circ,\ 120^\circ,\ 180^\circ,\ 240^\circ,\ 300^\circ,
\]

which is a six-node regular hexagonal scaffold with six exact (60^\circ)
steps. This validates the proposed `3+3 -> 6` topology. It does **not** mean
that two TE-ARA budgets should be added to make energy `4`; the resulting
parent is renormalized as one identity at its own measurement tier.

## Polygon controls

For a regular (n)-gon with side length `1`, the direct chord that skips one
vertex has length

\[
d_n=2\cos\left(\frac{\pi}{n}\right).
\]

The frozen controls were (n=3,\ldots,12). Only the pentagon returned
(d_n=\phi) exactly:

| polygon | two-edge shortcut | absolute distance from (phi) |
|---:|---:|---:|
| 3 | 1.000000000 | 0.618033989 |
| 4 | 1.414213562 | 0.203820426 |
| **5** | **1.618033989** | **0.000000000** |
| 6 | 1.732050808 | 0.114016819 |
| 7 | 1.801937736 | 0.183903747 |
| 8 | 1.847759065 | 0.229725076 |
| 9 | 1.879385242 | 0.261351253 |
| 10 | 1.902113033 | 0.284079044 |
| 11 | 1.918985947 | 0.300951958 |
| 12 | 1.931851653 | 0.313817664 |

Thus, within the declared family, the pentagon is not an arbitrary shape
chosen after seeing the answer. It is uniquely selected by requiring two unit
steps to have a direct shortcut of exactly (phi).

## Frozen gates

All `13/13` analysis gates passed:

1. two-side route equals `2`;
2. diagonal/side equals (phi);
3. seam equals (phi^{-2});
4. diagonal central angle equals (144^\circ);
5. interior angle equals (108^\circ);
6. all pentagram diagonal divisions are golden;
7. inner-pentagon scale equals (phi^{-2});
8. recursive scales follow (phi^{-2k});
9. the two triangles supply six distinct directions;
10. all resulting hexagonal gaps equal (60^\circ);
11. only (n=5) matches (phi) among the frozen polygon controls;
12. the square control returns (sqrt2);
13. the hexagon control returns (sqrt3).

An independent implementation that does not import the analysis script
reconstructed the vertices, intersections, ratios, angles and controls. It
passed `23/23` checks and matched the saved result.

## Plain-language result

The geometry Dylan described exists exactly.

If the mixed route takes two equal steps around a regular pentagon, its total
is `2`. The direct line from the starting Phase A to the next Phase A is
exactly Phi. The missing part is exactly `0.382`, the reverse Phi landmark.
Drawing all five direct lines makes a pentagram, and that pentagram generates
a smaller copy of the same pentagon at exactly the `0.382` scale. Separately,
two three-part closures offset from one another generate a six-part hexagonal
parent.

That is a strong and unusually clean **internal geometry result** for the ARA
Hexagon/Pentagon idea. It proves that the proposed pieces can be one coherent
mathematical construction. It does not yet prove that a physical system uses
these paths, nor that Phi is universally the cross-rung handover law.

## Evidence boundary and next empirical test

**Established by T319:** the full exact construction, its angles, its
recursion, its seam and its polygon-control uniqueness in the tested range.

**Not established by T319:** that measured Phase A and Phase B trajectories in
nature occupy those diagonals, that two physical ARA systems generate a
hexagon by this mechanism, or that all cross-scale same-phase paths use Phi.

The next empirical test should freeze a physical system with independently
identified child, parent and grandparent ARA scales, then test whether its
same-phase cross-scale paths prefer (phi) and (phi^2), and whether its
rotational projections prefer the declared (72^\circ/144^\circ) pentagonal
signatures over matched non-pentagonal controls.

## Reproduction files

- Frozen protocol: `T319_PENTAGON_PHI_PILLAR_GEOMETRY_PROTOCOL_v1_FROZEN.md`
- Analysis: `t319_pentagon_phi_pillar_geometry.py`
- Results: `T319_PENTAGON_PHI_PILLAR_GEOMETRY_RESULTS.json`
- Independent validator: `validate_t319_pentagon_phi_pillar_geometry.py`
- Validation result: `T319_PENTAGON_PHI_PILLAR_GEOMETRY_VALIDATION.json`
- Interactive visual: `T319_PENTAGON_PHI_PILLAR_GEOMETRY.html`
- Static visual: `T319_PENTAGON_PHI_PILLAR_GEOMETRY.svg`

