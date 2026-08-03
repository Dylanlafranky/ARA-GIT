# Q57A Post-Result Same-Phase Orientation Correction v1

**Registered:** 31 July 2026, after Q57 and before Q57A calculation.

## Why this correction exists

Q57 tested the user-proposed additive expression

\[
2-P_A+\frac12C_A.
\]

After seeing its approximately `1.5` result, Dylan identified the orientation issue. Because the parent is a complete local TE-ARA,

\[
2-P_A=P_B.
\]

Therefore Q57's additive expression is exactly

\[
P_B+\frac12C_A,
\]

a parent-B/child-A cross-phase path. It is not an additive same-phase `AA` path. The same correction applies to Q57's nominal B expression, which is parent A plus child B.

Q57 remains frozen and is not rewritten. Its ratio branch was genuinely same-phase; only its additive branch was mislabelled.

## Corrected calculation

Using the already fixed Q57 seed-level local TE-ARA coordinates:

\[
g_A=P_A+\frac12C_A,
\qquad
g_B=P_B+\frac12C_B.
\]

These are the additive `AA` and `BB` paths in parent units. Report archive medians, 10,000 seed-bootstrap median intervals, nearest named landmarks, and distances from phi.

Because Q57A was motivated by the observed Q57 value, it is a transparent post-result correction, not an independent confirmation. Also,

\[
g_A+g_B=3
\]

is forced by the two local TE-ARA closures and half-weight child projection. The empirical information is the allocation along that fixed total, not the total itself.

