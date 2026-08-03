# T331 — Why the Phi tests contain many `1.2…` values

**Date:** 3 August 2026  
**Type:** post-result diagnostic and bookkeeping audit; not a frozen prediction  
**Status:** complete  
**Primary conclusion:** most of the apparent `1.2…` recurrence is one
predeclared coordinate family, not many independent empirical recoveries.

## Answer first

The repeated band has a simple ARA reason. If a left-side landmark is `s` and
its ARA mirror is `2-s`, the separation between the pair is

\[
\boxed{c(s)=(2-s)-s=2(1-s).}
\]

All landmarks near `0.37..0.40` therefore become widths near `1.20..1.264`:

| left-side landmark `s` | mirrored width `c(s)` |
|---:|---:|
| `2/5 = 0.400000` | `1.200000` |
| `8/21 = 0.380952` | `26/21 = 1.238095` |
| `2-phi = 0.381966` | `2/phi = 1.236068` |
| `3/8 = 0.375000` | `5/4 = 1.250000` |
| `1/e = 0.367879` | `2-2/e = 1.264241` |

This is a legitimate structural result: the `1.2…` band is the
mirror-pair-width image of the compact space-side landmark band. It is also a
deduplication warning. The five values are not five separate observations;
they are five candidate landmarks passed through the same mapping.

The inverse is equally simple:

\[
\boxed{s=1-\frac{c}{2}.}
\]

Any reported `1.2…` value can therefore be mapped back to its proposed
left-side landmark before deciding whether it is new evidence.

## What the recent tests actually measured

### Constructed or predeclared values

- T328 and T329 explicitly entered `1.200000`, `1.236068`, `1.238095`,
  `1.250000` and `1.264241` as rival candidate increments. Their repeated
  appearance in result tables is therefore expected and must be counted once,
  as the candidate family—not once per row or test.
- Q60 predeclared the same Phi/rational neighbourhood. Its actual
  calibration-fitted phase advance was `0.000256194`, essentially
  persistence, not `1.2…`.
- T307's `1.250154548 = phi-1/e` is an algebraic construction from the two
  named constants. It is a useful crosswalk but not a data recovery.
- Some other `1.2…` numbers in the repository are loss ratios, raw capacity
  ratios or unrelated ARA coordinates. Values with different definitions and
  units must not be pooled.

### Data-derived values

- T325's development-only phyllotaxis fit was `0.76628` ARA. Under the
  equivalent reverse orientation it is `2-0.76628 = 1.23372`. Its transformed
  95% interval is `1.22003..1.24443`, which contains both exact Phi
  (`1.236068`) and its close rational `26/21` (`1.238095`). This is one real
  fitted estimate near the band, but it comes from the already Phi-known
  phyllotaxis domain.
- T319 reported a raw station-grid maximum at `1.263451`, close to the
  `1/e`-derived control `1.264241`. Its grid resolution was about `0.131725`,
  so this cannot distinguish that constant from neighbouring values and the
  report correctly remains inconclusive.
- T328 found Phi best for a registered return-profile score, but persistence
  won the direct parent carrier and exact-constant resolution failed.
- T329 found persistence best at actual bubble handover seams.
- Q60 found persistence/near-zero best for successive Ramsey sweeps.

Therefore the honest evidence statement is:

> ARA's mirrored landmark construction predicts a narrow `1.2…` candidate
> family exactly. Current data contain one compatible phyllotaxis fit and a
> few coarse or metric-incommensurate neighbours, but do not show many
> independent recoveries of that family.

## Why the visual recurrence felt stronger

Three effects stacked together:

1. **Coordinate compression.** A compact `s=0.37..0.40` neighbourhood is
   automatically mapped into `c=1.20..1.26`.
2. **Candidate-table repetition.** The same registered constants appeared in
   evaluation, holdout, local, parent and return tables.
3. **Metric collision.** Unrelated quantities such as errors, capacity ratios
   and ARA positions happen to share decimal labels near `1.2` but do not
   measure the same relation.

This is not evidence that the geometry is empty. It means the correct object
to test is the *mapping and ordered transport rule*, not the broad numerical
band by itself.

## New audit rule

Future Phi work must classify every `1.2…` occurrence before interpretation:

1. Was it supplied as a candidate or estimated freely from unopened data?
2. Is it an ARA coordinate, a pair width, a loss ratio or another quantity?
3. Does it equal `2(1-s)` for a previously declared left-side landmark?
4. If freely estimated, does its uncertainty exclude `26/21`, `5/4`,
   `2-2/e`, persistence and a flexible fitted control?
5. Does recorded order and lineage outperform shuffled and broken controls?

Only a freely estimated, held-out, order-specific result that survives these
checks counts as an independent empirical recovery of exact Phi.

## Best next discriminating test

Do not score only the fixed `1.2…` candidates. On a genuinely independent,
well-resolved ordered lineage:

1. estimate the step `c` freely on development data;
2. freeze that estimate and all comparison rules;
3. score held-out events without refitting;
4. map the estimate back using `s=1-c/2` as a reversible ARA consistency
   check;
5. require its interval to distinguish exact `2/phi` from `26/21`, `5/4`,
   `2-2/e`, persistence and a flexible nonconstant model.

That test can tell whether the observed process selects exact Phi, merely the
wider ARA mirrored-landmark neighbourhood, or neither.

## Audited sources

- `T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_REPORT_2026-08-02.md`
- `T328_PHI_CIRCLE_TRAIN_BUBBLES_REPORT_2026-08-02.md`
- `T329_ACTUAL_HANDOVER_PHI_SEAM_REPORT_2026-08-02.md`
- `Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_REPORT_2026-08-03.md`
- `T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_REPORT_2026-07-30.md`
- `T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_REPORT_2026-07-31.md`
- `T319_LONGITUDINAL_PHI_THREE_EIGHTHS_REPORT_2026-08-02.md`
- `Q42_ARA_DUAL_STRAND_FLOW_REPORT_2026-07-28.md`
- `Q33_TWO_AXIS_PARENT_CHILD_35_REPORT_2026-07-26.md`
- `Q33_POST_RESULT_ARA_COORDINATE_CORRECTION_2026-07-26.md`

The row-level classification is preserved in
`T331_PHI_1_2_CLUSTER_AUDIT.csv`.
