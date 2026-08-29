# T411 cumulative development result - parent history, not handover

The first development instrument used cumulative plate-modelled thinning
`R = D0 - D_M` and cumulative unresolved thinning `I = D_M - D_obs`.

Across the 70 S1/S3 development experiments:

- no reliable trajectory reached a persistent `I = R` crossing before the
  validated five-pixel measurement limit;
- 66 runs had enough finite ARA samples to score temporal order;
- median Spearman correlation between elapsed event time and the cumulative
  ARA coordinate was `0.9904817`;
- 2,000 within-run circular shifts gave a null median of `0.4548763`, 95th
  percentile `0.7643477`, and empirical `p = 0.00049975`.

This is not treated as a failed geometry. It is treated as a **failed
handover instrument**: cumulative accounting retains the early plate work and
therefore measures the parent-scale history of the filament, not which branch
controls its current movement. S2/S4 holdout data were not opened.

The predeclared correction is to apply the same parent/residual relation to
current thinning rates. That child/movement instrument is specified separately
in `T411B_RATE_DEVELOPMENT_PROTOCOL.md`.
