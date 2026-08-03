# T319 — Pentagon Phi-pillar geometry protocol v1 (frozen)

**Frozen:** 31 July 2026, before procedural construction and numerical
measurement.

**Evidence class:** exact geometry / internal mathematical consistency test.
This is not an empirical natural-system test.

## 1. Clarified question

Can Dylan's proposed ARA path

\[
\text{Phase A}\rightarrow\text{Phase B}\rightarrow\text{starting Phase A}
\]

be embedded in a regular pentagonal scaffold such that:

- the two-leg route has normalized length `2`;
- the direct same-phase Phase A → Phase A route has length \(\phi\);
- the difference is the reverse-Phi ARA landmark \(\phi^{-2}\);
- and the same construction recursively produces smaller rungs?

The companion Hexagon claim is tested as a topology: two three-node
Information³ closures, rotated by `60°`, should supply the six outer nodes of
a regular hexagonal parent scaffold.

## 2. Frozen construction

### Pentagon

Construct a regular pentagon with side length exactly `1`.

Choose three consecutive vertices `(A0, B, A1)`.

- full mixed route: `A0 → B → A1`;
- direct same-phase pillar: `A0 → A1`;
- draw all five diagonals to form the pentagram;
- calculate all diagonal intersections and the central inner pentagon.

### Hexagon

Construct two unit-circle equilateral triangles:

- triangle A at angles `(0°, 120°, 240°)`;
- triangle B at angles `(60°, 180°, 300°)`.

Their ordered union should be the six vertices of a regular hexagon.

This is a node/topology count, not addition of TE-ARA energy budgets.

## 3. Frozen predictions

The Pentagon Phi-pillar construction passes only if all exact numerical gates
hold to absolute tolerance `1e-12`:

1. `two_side_path = 2`;
2. `pentagon_diagonal / side = phi`;
3. `two_side_path - diagonal = phi^-2`;
4. the diagonal subtends `144°` at the pentagon centre;
5. the pentagon interior angle is `108°`;
6. every diagonal intersection divides a diagonal in the golden ratio;
7. the central inner-pentagon side / outer-pentagon side is `phi^-2`;
8. recursively generated inner-pentagon side scales follow
   `1, phi^-2, phi^-4, ...`;
9. the two equilateral triangles supply six equally spaced outer directions;
10. the resulting hexagonal neighbour step is `60°`.

## 4. Frozen polygon controls

For a regular `n`-gon with unit side, the direct shortcut across two adjacent
edges is

\[
d_n=2\cos(\pi/n).
\]

Evaluate `n = 3...12` without fitting. Pentagon specificity requires:

- `n=5` is the unique tested polygon whose two-edge shortcut equals `phi`
  within `1e-12`;
- the hexagon control gives `sqrt(3)`, not `phi`;
- the square gives `sqrt(2)`, not `phi`.

## 5. Interpretation gates

- **Exact Pentagon pillar supported:** all ten construction gates and all
  polygon controls pass.
- **Partial:** the path identity passes but recursive pentagram or hexagon
  topology gates fail.
- **Not supported:** the two-leg/direct/seam identity fails.

Even a complete pass establishes only that the proposed ARA interpretation is
an exact regular-polygon construction. It does not show that a physical ARA
system uses the construction.

## 6. Documentation correction required on pass

If the regular-pentagon construction passes, replace the provisional wording
“a Phi chord in a unit-radius circle subtends 108°” as the pillar mechanism.
That statement is algebraically true, but it is not the regular-pentagon
diagonal embedding. The corrected roles are:

- `108°`: pentagon interior angle;
- `72°`: pentagon central/exterior step;
- `144°`: central angle spanned by a pentagon diagonal;
- `phi`: diagonal length when pentagon side is normalized to `1`.
