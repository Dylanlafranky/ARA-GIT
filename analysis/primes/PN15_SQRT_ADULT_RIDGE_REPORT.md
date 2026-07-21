# PN15 — Full Square-Root Child Closure and Adult-Rung Ridge

**Test ID:** `PN15/SQRT-CHILD-ADULT-RIDGE/v1`  
**Date:** 21 July 2026  
**Status:** Frozen scale-12 target opened; both registered arms supported; independent validation passed  
**Primary report:** `PN15_SQRT_ADULT_RIDGE_REPORT.html`

## Answer first

The untouched scale-12 target passed every frozen criterion.

- Adult growth from scale 11 to 12 was `10.0017276297`, against the registered `10` reference.
- The representative square-root children were `0.9999985181` and `0.9999962435` on the ARA factor coordinate.
- Their ratio was `1.0000022746` and their sum was `1.9999947616`.
- The adult product filled `0.9999070021` of the scale-12 anchor.
- The frozen 16-sector phase template transferred to target primes with correlation `0.9999467506` and RMSE `0.0015826589`.
- The independent validator reproduced every frozen hash, gate, pair, sector count, sector mean and summary metric.

In ARA language, the full square-root construction produces an exceptionally tight `1.0 / 1.0` child ridge which closes to an adult coordinate of almost `2.0`.

## Plain-language interpretation

We previously saw two child increases of roughly `8.07` and `7.96`. Their ratio was already close to `1.0`, but those children were selected near `n^0.45`, so their scale growth was expected to be below `10`.

PN15 moved the children to the complete square-root boundary, `n^0.5`. On that coordinate, each child is almost exactly half of the parent's logarithmic scale. A half plus a half reads almost exactly `2.0` in the decompressed two-child sum, while the two halves are almost exactly equal to each other at the `1.0` ridge.

That is the clean version of the geometry you identified:

\[
\underbrace{x_N(q)}_{\text{child A}\approx 1}
+
\underbrace{x_N(r)}_{\text{child B}\approx 1}
=
\underbrace{x_N(qr)}_{\text{adult}\approx 2},
\qquad
x_N(p)=\frac{2\log p}{\log N}.
\]

Plainly: two prime gates just below the square root each occupy almost one half-scale position. Multiplying them closes the parent scale, and adding their ARA coordinates gives almost two.

## Frozen design

For each anchor

\[
N_d=4\times10^d,\qquad d\in\{8,9,10,11,12\},
\]

the test selected the nine largest primes at or below `sqrt(N_d)`, formed eight adjacent pairs, and used the median pair product `J_d` as the adult coordinate. Scales 8–11 were development only. Scale 12 was not calculated until the protocol, development outputs, primary script, dependency and independent validator were SHA-256 sealed.

The second arm used one deterministic median-product pair at each scale, divided its relative-phase cycle into 16 equal sectors, and kept raw integers, exact primes and exact composites separate.

## Arm A — square-root child and adult ridge

| Quantity | Fresh target | Frozen criterion | Result |
|---|---:|---:|---|
| `J_12 / J_11` | `10.0017276297` | within 1% of `10` | supported |
| growth ridge A | `1.0001358139` | `[0.995, 1.005]` | supported |
| growth ridge B | `0.9998641861` | `[0.995, 1.005]` | supported |
| child A | `0.9999985181` | `[0.995, 1]` | supported |
| child B | `0.9999962435` | `[0.995, 1]` | supported |
| child sum | `1.9999947616` | `[1.99, 2]` | supported |
| median adult fill | `0.9999070021` | `[0.999, 1)` | supported |

The observed adjacent adult growths were:

| Transition | Growth | Absolute deviation from `10` |
|---|---:|---:|
| scale 8 → 9 | `10.0060146718` | `0.0601%` |
| scale 9 → 10 | `10.0149166324` | `0.1492%` |
| scale 10 → 11 | `10.0044447463` | `0.0444%` |
| scale 11 → 12 | `10.0017276297` | `0.0173%` |

## Arm B — relative-phase transfer

| Quantity | Fresh target | Frozen criterion | Result |
|---|---:|---:|---|
| template correlation | `0.9999467506` | at least `0.95` | supported |
| template RMSE | `0.0015826589` | at most `0.025` | supported |
| zero-curve RMSE | `0.1476758565` | target at least 60% better | supported |
| wrong-coordinate RMSE | `0.1839812533` | target better | supported |
| permutation RMSE | `0.2058615194` | descriptive rival | target better |
| minimum primes per sector | `137,605` | at least `1,000` | supported |

The transferred curve is real and stable. It is not prime-specific. The largest absolute difference between target prime and composite sector means was only `0.0010394739`; their lines visually overlap with the raw-integer and analytic curves.

This is an important negative result: the present phase coordinate recovers the arithmetic geometry of the two selected gates, but it does not distinguish primes from composites at this grain.

## What the result establishes

PN15 establishes all of the following within its registered scope:

1. The ARA logarithmic child coordinate exactly crosswalks the standard square-root factor boundary.
2. Two independently selected near-square-root prime children read as an almost equal `1.0 / 1.0` pair and close to an adult sum near `2.0`.
3. The adult product follows the registered tenfold rung change on a fresh scale.
4. The phase template transfers across scale and survives the frozen controls.
5. The full calculation is reproducible by a separately implemented validator.

## What the result does not establish

The extraordinary numerical precision is largely expected once the children are deliberately chosen immediately below `sqrt(N)`:

\[
q\approx\sqrt N,quad r\approx\sqrt N
\quad\Longrightarrow\quad
x_N(q)\approx x_N(r)\approx1,quad qr\approx N.
\]

Likewise, multiplying `N` by ten makes a near-`N` product grow by approximately ten. PN15 therefore validates the translation, implementation, freeze discipline and cross-scale consistency. It is not a new method for locating primes, and by itself it does not prove that ARA is the universal fractal geometry.

The phase arm is also a generic two-gate closure curve in this construction. Because primes and composites overlap, it cannot presently be promoted as a prime classifier or predictor.

## Independent validation and QA

`validate_pn15_sqrt_adult_ridge.py` used a separate bytearray sieve and independently recomputed:

- every frozen input hash;
- the scale-12 boundary gates and adjacent pairs;
- all 16 raw, prime and composite sector counts and means;
- all adult-ridge and phase-transfer metrics; and
- a small analytic-cycle fixture.

Every check passed. The static figure was rendered after target opening and visually inspected. The portable HTML report passed canonical validation and structural verification; interactive Chromium verification was unavailable because no compatible headless Chromium executable was installed. Its semantic chart/table fallback remains self-contained and readable.

## Best next test

Keep PN15 as a successful calibration and crosswalk result. The next load-bearing prime test should preregister a quantity that the square-root selection does not already guarantee.

A suitable direction is to ask whether a child-wave residual measured before the moving square-root boundary predicts an untouched prime-survival frequency, location class or gap class better than raw modular and sieve-informed controls. That would test whether ARA contributes information beyond reconstruction of the known factor boundary.

## Files

- Frozen fidelity packet: `PN15_SQRT_ADULT_RIDGE_FIDELITY_PACKET_v1.md`
- Frozen protocol: `PN15_SQRT_ADULT_RIDGE_PROTOCOL_v1_FROZEN.md`
- Target freeze: `PN15_TARGET_FREEZE_MANIFEST.json`
- Primary implementation: `pn15_sqrt_adult_ridge.py`
- Independent validator: `validate_pn15_sqrt_adult_ridge.py`
- Development results: `PN15_DEVELOPMENT_RESULTS.json`
- Target results: `PN15_TARGET_RESULTS.json`
- Validation receipt: `PN15_SQRT_ADULT_RIDGE_VALIDATION.json`
- Static figure: `PN15_SQRT_ADULT_RIDGE.png`
- Portable report: `PN15_SQRT_ADULT_RIDGE_REPORT.html`
- Reproducible notebook: `PN15_SQRT_ADULT_RIDGE.ipynb`

