# PN29 interpretive amendment - static orientation omitted ARA flips

**Date:** 22 July 2026  
**Changes frozen PN29 data:** no  
**Changes PN29 arithmetic:** no  
**Changes interpretation:** yes

## Correction

PN29 permanently oriented the declared child pairs as

\[
(1,13),\qquad(3,11),\qquad(5,9).
\]

That was a valid static signed-coordinate diagnostic, but it was not a complete implementation of reversible ARA. The ARA framework had already declared that crossing a singularity introduces a flip. The missing operational rule was clarified after PN29:

\[
\theta_w(N)=\frac{N\bmod w}{w},
\]

and the member of each pair with smaller normalized progress \(\theta\) becomes Phase A until its partner crosses.

Thus `(5,9)` can become `(9,5)`, and similarly for `(3,11)`. Under the pair coordinate,

\[
x_{B\to A}=2-x_{A\to B},
\]

so orientation changes the sign of the pair's ridge displacement while retaining its magnitude.

## What PN29 still establishes

- Its coordinate generation, label firewall, results and `7/7` validation remain correct for the method actually frozen.
- Its strong overall AUC is still evidence that the static coordinate detects the declared finite child-factor web.
- Its failure against unresolved composites remains an accurate result for the static representation.

## What PN29 no longer represents

PN29 must not be described as a complete test of the ARA child geometry because it omitted the singularity-driven AB/BA reversals. PN30 is the corrected reversible implementation.

On a fresh 1001-1999 interval, PN30's dynamic rule increased unresolved-composite AUC from `0.5301` to `0.5663`, but its frozen one-sided result was `p=0.06199`. This is a suggestive improvement rather than confirmed prime-specific evidence.

See `PN30_DYNAMIC_RELATIONAL_FLIP_REPORT.md`.

