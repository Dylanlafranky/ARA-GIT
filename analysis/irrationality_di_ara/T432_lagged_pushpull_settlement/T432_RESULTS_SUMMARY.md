# T432 result — lagged push/pull, corner avoidance and settlement

## Frozen verdict

**The strong universal dynamic-handover rule was not supported.** Two of six untouched mergers exceeded the 95th matched off-source percentile for lagged push/pull (`GW190517_055101` and `GW190519_153544`), below the frozen requirement of four. No event passed the joint speed-and-radius settlement gate, and no event reproduced the push/pull threshold independently in both H1 and L1.

This does not erase the ARA path geometry. It narrows the claim: the fixed movement/connection projection can reveal source-specific delayed opposition in some mergers, but this absolute-time cut does not establish it as a universal merger handover or a universal closing-and-settling law.

## Strongest leads

- `GW190519_153544`: push/pull percentile 100.0%, opposition Spearman rho -0.381, opposition occupancy 0.461, selected lag +64 ms.
- `GW190517_055101`: push/pull percentile 96.2%, opposition Spearman rho -0.311, opposition occupancy 0.413, selected lag +60 ms.
- Both selected lags sit near the +64 ms search boundary. The frozen result remains valid, but the lead requires a new lag-stability test before physical interpretation.

## Empty top-left region

The nominal low-movement/high-connection box (`M<=0.5`, `C>=1.5`) was empty in every event and every matched control. Its occupancy percentile was therefore 0.5 for all events. The visible boundary is real in the constructed coordinate plane, but this exact box does not distinguish source strain from off-source strain and cannot presently be treated as a newly discovered physical identity.

## What the data actually are

- Public 4 kHz H1 and L1 calibrated strain files from GWOSC, 32 seconds per detector.
- Calibrated strain is detector response containing astrophysical signal plus instrumental/noise contributions.
- The data are whitened using off-source strain, band-passed from 30 to 512 Hz, and summarized by a 64 ms Hann time-frequency window stepped every 4 ms.
- `C` is a constructed connection-facing coordinate: the mean of network spectral amount, spectral concentration and H1/L1 phase coherence, each mapped to 0–2 against its off-source empirical distribution.
- `M` is a constructed movement-facing coordinate from spectral redistribution, likewise mapped to 0–2.
- `H=max(0,2-C-M)` is unresolved projection residual only. It is not measured hidden energy.

## Limits on interpretation

- H1 and L1 are independent views of the same event, not the two black holes.
- `C`, `M` and `H` are not joules, forces, masses, orbital separations, horizons or literal connection counts.
- The 4 ms hop does not provide 4 ms independent resolution; the 64 ms analysis window smears shorter structure.
- The fixed -0.50 to +0.75 second window does not normalize different events by mass or intrinsic merger/ringdown duration.
- Off-source controls establish within-file specificity only. They cannot by themselves distinguish source physics from all event-coincident detector effects.

## Best next test

Use the 20 now-opened events only as development data to freeze a **timescale-normalized lag-stability instrument**. Measure whether the opposition peak remains stable when the allowed lag range is widened, and align each event by an independently estimated chirp/ringdown duration rather than absolute seconds. Then test on another untouched event set. This directly addresses the two strongest limitations without changing the ARA identity or axes.

