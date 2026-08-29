# T434 results — ARA / IMR scientific bridge

**Primary verdict: NOT SUPPORTED at this frozen cut.**

Median absolute frequency difference: 47.05%.
Events within 25%: 0/4.
Temporal-shift p-value: 0.07019.
Wrong-event assignment p-value: 0.25.
Median orientation-invariant AUC: 0.660; shift p=0.296.

## Post-result diagnostic (not a T434 pass)

The maximum-bin spectral translation visibly jumped among narrow frequency
bands. The already-computed median coherent-excess frequency was therefore
audited after the frozen result:

- median absolute difference: 19.36%;
- three of four events within 25%;
- temporal-shift p-value: 0.00010;
- wrong-event assignment p-value: 0.375;
- median child-order AUC: 0.774; shift p-value: 0.182.

This supports a time-local association with merger activity, but not a unique
event-specific ARA-to-IMR identity bridge. It is a future replication target,
not a replacement for the failed frozen primary.

## Gates

- FAIL — median absolute percentage difference <= 20%
- FAIL — at least 3/4 events within 25%
- FAIL — temporal-shift frequency p <= 0.05
- FAIL — wrong-event assignment p <= 0.05
- FAIL — median AUC >= 0.70 and shift p <= 0.05

## Interpretation boundary

This compares a frozen ARA child exchange with a standard published IMR boundary. The ARA frequency translation and IMR analysis both ultimately use the same detector strain, but the event-specific published cutoff was not used to construct or select the ARA landmark. A failure rejects this operational bridge, not either parent framework.

## Files

- `results/T434_EVENT_RESULTS.csv`
- `results/T434_FREQUENCY_TRACKS.csv`
- `results/T434_RESULTS.json`
- `results/T434_ARA_IMR_COMPARISON.png`
- `results/T434_EVENT_GALLERY.png`
- `results/T434_BRIDGE_AUDIT.png`
- `results/T434_POSTHOC_MEDIAN_DIAGNOSTIC.json`
- `T434_VALIDATION.md`
