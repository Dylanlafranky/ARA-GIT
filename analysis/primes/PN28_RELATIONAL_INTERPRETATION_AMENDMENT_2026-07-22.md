# PN28 relational interpretation amendment

**Date:** 22 July 2026  
**Applies to:** `PN28_THREE_CHILD_RESIDUAL_LIFT_*`

## Correction

PN28 evaluated

\[
\widehat P_1
=\widehat P_0
+\operatorname{round}\left(4[R_{\rm child}-1]\right).
\]

This treated a dimensionless ARA displacement as a raw integer correction. It also caused the adjustment to become
constant inside several exact-fit child classes. For example, Phase A `3` received `-2`, changing the PN27
candidate `N+26` into `N+24` for the whole class.

Dylan clarified that this is not the intended method. The intended rule is:

1. convert each local relation onto that rung's dimensionless `0–2` ARA coordinate;
2. perform collapse and ridge operations only in ARA coordinate space;
3. on upward coarse-graining, halve normalised ridge displacement per rung;
4. do not add an ARA displacement to a raw integer;
5. convert back to the domain's units only through a separately declared inverse coordinate map.

## Claim boundary

PN28 validly shows that its own mixed-units integer bridge performs poorly. It does **not** test or refute the
corrected relational three-rung transport.

The corrected coordinate-only diagnostic is frozen and tested as PN29.

