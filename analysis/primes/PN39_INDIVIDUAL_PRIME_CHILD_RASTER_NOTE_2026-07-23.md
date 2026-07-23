# PN39 — Individual-Prime Child ARA Raster

**Date:** 2026-07-23  
**Status:** descriptive visualization on opened PN37 data; not a prediction test

## Purpose

Show the complete lower child field separately for consecutive individual prime parents rather than pooling all parent-child relations into one histogram.

Each column is one prime in occurrence order. For every lower prime gate `q <= sqrt(p)`, place

\[
A_q(p)=2\frac{p\bmod q}{q}
\]

into one of 160 equal bins on `[0,2]`. Cell intensity is the number of lower gates landing in that ARA interval for that parent. Overlay the parent centroid `mean_q A_q(p)` as the compressed parent reading.

The first view uses the first 512 primes in the PN37 interval. This bounded window preserves individual parents at screen-readable width. It is exploratory and must not be treated as a fresh statistical test.

## Descriptive findings

- Every one of the 512 individual primes occupies all `160/160` child ARA bins. At this grain, complete diameter fill is therefore present within each prime separately rather than appearing only after pooling different parents.
- The compressed parent centroids range from `0.9899269` to `1.0102765`.
- Adjacent primes have mean child-histogram residual correlation `0.7657`; this decays through `0.6172` at lag 2, `0.5008` at lag 3, `0.3298` at lag 5, `0.1661` at lag 8, and `0.0157` at lag 13.
- The parent-centroid lag-1 correlation is `0.9094`.
- A reversed distant-half pairing has mean residual correlation `0.0034`.

Plainly: the individual child fields do not redraw independently at each prime. They glide through strongly related nearby configurations, with most similarity gone after roughly thirteen prime events in this window. This is expected to some degree from modular residues advancing continuously as the parent integer increases, so it is a clear structural crosswalk rather than evidence that ARA uniquely predicts primes.

## Reproduction

```powershell
python analysis/primes/pn39_individual_prime_child_raster.py
```

Machine data: `PN39_INDIVIDUAL_PRIME_CHILD_RASTER.json`.

## Follow-up

PN40 quantified Dylan's visual observation of rising diagonal crests in this raster. Local 128-prime fits sit at approximately `4.2°–6.0°` on the displayed chart, while a frozen three-band continuation remains unusually aligned in the second half. See `PN40_DIAGONAL_CHILD_BAND_REPORT_2026-07-23.md`.
