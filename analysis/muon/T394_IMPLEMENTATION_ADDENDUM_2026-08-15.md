# T394 implementation addendum

**Frozen after schema/quality inspection and before model scoring:** 15 August 2026  
**Parent protocol:** `T394_NATIVE_NEUTRAL_PAIR_AND_CAUSAL_RELEASE_PROTOCOL_2026-08-15.md`

## Source qualification

- Source: Super-Kamiokande Zenodo record `15081911`.
- Local file: `source_cache/superk_2025/decayes_and_neutrons.csv`.
- SHA-256: `B6BB10270E6C604935B47687293470CAEAFD01172288170D83349043566CD05A`.
- Expected and observed grain: `1,986,465` rows, one selected stopping muon per row.
- Column 1: tagged decay-electron momentum in MeV, or zero.
- Column 2: tagged decay-electron time in microseconds, or zero.
- Remaining columns: zero or more tagged-neutron times in microseconds.

The source exposes no pre-outcome per-muon spin, trajectory, stopping position,
charge or repeated state measurement. Therefore Test 2 Gate 4 is declared
**structurally untestable in this source before scoring**. Electron and neutron
fields remain outcomes and cannot be used to manufacture an anti-phase
predictor.

## Deterministic unseen split

Hash the zero-based row number with SplitMix64:

- buckets `0-4`: calibration;
- buckets `5-6`: validation;
- buckets `7-9`: untouched holdout.

The row order is not documented as acquisition chronology, so no split is
called chronological.

## Test 1 implementation

- Accepted truth events: `1,000,000`.
- Seed: `394`.
- Charged coordinate: rejection sample from `2*x^2*(3-2*x)`.
- V-A neutral child: rejection sample from `z*(1-z)` conditional on `x_e`.
- Phase-space control: uniform `z` on the same event-specific interval.
- Identity-shuffled control: fixed-seed independent random swapping of the two
  neutral labels.
- Coarse-pair neighbourhood: minimum L1 distance to oriented `(0.5,1.5)` or
  `(1.5,0.5)` no greater than `0.20`.

## Test 2 implementation

The primary timing population is all tagged decay-electron rows with
`0.45 <= t <= 30.0` microseconds. Rows without a tagged decay electron and all
neutron information are retained in the source-quality/Other account but not
treated as censored survival times because their observation endpoints are not
provided in this release.

Models fitted only on calibration tagged-decay times:

1. `M0`: exponential density truncated to `[0.45,30.0]`; fit the rate by
   bounded one-dimensional likelihood minimisation.
2. `MP`: 128 equal-width empirical release bins on `[0.45,30.0]`, with
   Jeffreys smoothing `0.5` count per bin and piecewise-uniform density.
3. `MR`: the time-reversed `MP` bin probabilities.

Primary score: untouched-holdout mean negative log likelihood. Secondary
scores: holdout CDF Kolmogorov-Smirnov distance and integrated absolute CDF
error. Use 100 deterministic holdout index blocks and a seed-394, 2,000-draw
block bootstrap for the `M0 minus MP` NLL improvement interval.

Population anti-phase Gate 3 passes only if:

- `MP` holdout NLL is lower than `M0`;
- the 95% block-bootstrap interval for `M0-MP` is wholly above zero;
- `MP` holdout KS is lower than `M0`;
- `MP` beats the reversed control `MR` in holdout NLL.

Even if Gate 3 passes, the result remains a population distribution forecast.
No result from this source can pass individual advance Gate 4.
