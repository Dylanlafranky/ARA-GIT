# PN40 — Diagonal child-band test (v1, frozen)

**Frozen:** 2026-07-23, before running PN40.

## Status and observation boundary

This is a **post-hoc descriptive follow-up**, prompted by Dylan marking three roughly parallel rising crests in the first 256 columns of the PN39 individual-prime child raster. The marked region is therefore the opened development half. The remaining 256 PN39 columns will be used only as a fixed-continuation transfer check; because the underlying file already existed, this is not called a blind confirmation.

## Fixed representation

- Source: `PN39_INDIVIDUAL_PRIME_CHILD_RASTER.json`.
- Preserve prime occurrence order; do not Fourier-transform, sieve again, or reorder the primes.
- Sum adjacent pairs of the original 160 child-ARA bins, exactly reproducing the 80 vertical cells in the displayed raster.
- Treat the vertical child-ARA coordinate as circular on `[0,2)`, so a rising crest may wrap from `2` back to `0`.
- Subtract each prime row's mean and divide by that row's root-mean-square residual. This tests **where** each prime's child field is concentrated, not its total child count.

## Frozen line detector

1. Use columns 0–255 as development and 256–511 as transfer.
2. Search only positive slopes from `+0.0200` to `+0.1000` displayed bins per prime occurrence, in steps of `0.0005`. This range was fixed from the user's approximate five-degree visual observation.
3. Score a circular line by bilinear sampling of the residual field along it, with fixed cross-band weights `0.25, 0.50, 0.25` at offsets `-1, 0, +1` displayed bins.
4. At each slope select exactly three positive crests, greedily, with at least 12 displayed bins of circular separation. Select the development slope with the highest mean score across those three crests.
5. Carry that slope and all three intercepts forward without refitting into columns 256–511.

## Fixed controls and reporting

Report:

- slope in displayed bins per prime occurrence;
- slope in native ARA units per prime occurrence (`0.025 × displayed-bin slope`);
- approximate on-screen angle for the existing 684 × 348 plot area (the angle is aspect-ratio dependent);
- the three development intercepts in ARA coordinates and their circular separations;
- development score and fixed-continuation transfer score;
- transfer percentile against all common circular offsets of the three-line template;
- transfer percentile against 2,000 deterministic prime-order shuffles (seed `4000000007`);
- independently refitted transfer slope as a descriptive stability check;
- the equivalent child-gate scale inferred from the mean prime gap, using `q ≈ 2 mean(gap) / slope_ARA`.

## Interpretation rule

- A stable positive slope supports Dylan's visual claim that a coherent rising band is present in this representation.
- Transfer above the common-offset and shuffled-order controls supports sequential continuity, but remains a same-window replication rather than a new blind result.
- A gate-scale match is an explanatory arithmetic crosswalk: for child gate `q`, `A_q(p_next) = A_q(p) + 2(p_next-p)/q (mod 2)`. It does **not** by itself establish a new prime-prediction law or a universal five-degree constant.

