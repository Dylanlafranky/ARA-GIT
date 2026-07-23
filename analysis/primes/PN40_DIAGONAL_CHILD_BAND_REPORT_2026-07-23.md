# PN40 — Diagonal Child-Band Report

**Date:** 2026-07-23  
**Status:** post-hoc visual observation, frozen development fit, and same-file fixed-continuation transfer

## Observation

Dylan marked three rising, approximately parallel crests in the first 256 columns of the PN39 individual-prime raster and estimated their slight screen rise as roughly five degrees while mentally wrapping the `0–2` axis as a circle.

This is a real feature of the displayed field, but it is not one perfectly rigid straight line. The best description is a **locally five-degree, slowly bending band family on the circular child-ARA coordinate**.

## Frozen primary test

The first 256 primes were treated as opened development data. Adjacent pairs of the original 160 bins were summed to reproduce the displayed 80-bin raster exactly. Each row was centred and RMS-standardised so the detector measured the location of child concentration rather than total child count. The vertical `0–2` coordinate was treated circularly, allowing a band to wrap from `2` to `0`.

A frozen detector searched positive slopes and exactly three separated crests. Its strongest long-path development fit was:

- `0.0335` displayed bin per prime occurrence;
- `0.0008375` native ARA unit per prime occurrence;
- `0.2144` ARA unit across 256 occurrences;
- approximately `3.12°` on the current chart.

The three fitted starting locations were `0.075`, `1.025`, and `1.525` ARA. Their circular gaps were `0.95`, `0.50`, and `0.55`, which exactly complete the `2.0` circumference. This spacing is descriptive because the detector was instructed to select three separated crests.

## Fixed continuation

Without changing slope or intercepts, the three-line template was continued into primes 256–511:

- fixed continuation score: `0.51776` standardised residual unit;
- percentile against 800 common circular offsets: `99.69th`;
- percentile against 2,000 deterministic prime-order shuffles: `>99.95th`.

This shows that the detected diagonal family is sequentially coherent rather than an isolated mark in the opened half. It is still a same-file transfer check, not a new blind interval.

## Why Dylan's five-degree estimate is still right locally

Independent fits to four consecutive 128-prime windows gave screen angles of approximately:

1. `4.37°`
2. `6.04°`
3. `5.90°`
4. `4.23°`

Their centre is close to the hand-drawn `~5°` observation. A single exact five-degree straight path did not preserve its phase across the whole 512-prime window: its development score was `0.67664`, but its fixed continuation score fell to `0.14108`. Therefore the honest statement is **a local five-degree band whose slope or carrier drifts**, not a universal fixed five-degree line.

## Arithmetic source and ARA crosswalk

For an individual lower child gate `q`, the raw child coordinate obeys

\[
A_q(p_{i+1})
=
A_q(p_i)+2\frac{p_{i+1}-p_i}{q}
\pmod 2.
\]

Plainly: as the parent moves from one prime to the next, each lower child advances around its own `0–2` circle. Because the horizontal axis is **prime occurrence order**, while actual prime gaps vary, a fixed child gate does not appear as a perfectly constant screen-angle line. It speeds up and slows down slightly. Many nearby gates superpose into visible travelling bands.

The primary fitted slope corresponds to an effective child-gate scale near `q ≈ 53,000–55,000` in this interval, inside the available lower-gate range. This supplies a direct arithmetic mechanism for the observed motion.

In ARA language: PN39 does not show each prime as a static filled strip. It shows the lower child phases **travelling around the circular `0–2` diameter from one parent identity to the next**, with wrapping at the singularities. The parent centroid remains near the `1.0` ridge while the child distribution underneath it moves asymmetrically.

## Scientific boundary

This result strengthens the descriptive ARA crosswalk: the child field has measurable circular phase transport, and Dylan correctly saw it before numerical fitting. The arithmetic transport law is established modular behaviour in the coordinates used here. PN40 does not yet show that the band predicts an unseen prime or that five degrees is a universal ARA landmark.

## Reproduction

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' analysis/primes/pn40_diagonal_child_band.py
```

Files:

- `PN40_DIAGONAL_CHILD_BAND_PROTOCOL_v1_FROZEN.md`
- `pn40_diagonal_child_band.py`
- `PN40_DIAGONAL_CHILD_BAND_RESULTS.json`
