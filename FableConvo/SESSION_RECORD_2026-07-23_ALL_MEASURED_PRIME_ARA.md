# Session record — ARA between all measured consecutive primes

**Date:** 23 July 2026  
**Evidence tier:** deterministic post-endpoint decompression of independently validated PN7B aggregates

## Request and interpretation

Dylan asked to obtain the ARA between all primes after distinguishing prime non-closure from a fixed Phi
non-closing traversal. Because the prime sequence is infinite, “all” was operationalized without sampling as every
internal prime in PN7B's five previously opened complete windows.

For consecutive primes `(p_previous, p, p_next)`, the canonical reading is

```text
incoming gap = p - p_previous
outgoing gap = p_next - p
ARA = 2 * outgoing / (incoming + outgoing)
```

Swapping the two gaps maps `x` to `2-x`.

## Result

- Complete measured prime nodes: `44,360,409`.
- Observed exact incoming/outgoing gap pairs: `8,642`.
- Distinct reduced ARA ratios: `5,280`.
- Mean ARA: `0.9999986966`.
- Median ARA: `1.0`.
- Below ridge: `48.9366%`.
- Exactly on ridge: `2.1178%`.
- Above ridge: `48.9456%`.
- Exact reversal cosine: `0.9999918763`.
- Exact reversal total-variation distance: `0.00313169`.

The whole population therefore reads almost exactly `1.0`, while approximately `97.88%` of individual prime nodes
remain locally asymmetric. The whole ridge is produced by mirrored asymmetric children, not by most children being
individually equal.

## Phi boundary

Every value on this adjacent-gap coordinate is rational because it is formed from integer gaps. Exact Phi is
irrational and cannot occur. Proximity to the two golden landmarks can be counted, but without a declared null it is
only post-hoc occupancy and cannot establish golden enrichment.

## Two prime axes kept separate

1. Factor-survival non-closure identifies a prime only after all required lower-prime gates fail to close.
2. Adjacent-prime gap ARA describes the lateral spacing around already-known prime nodes.

They can be treated as two appearances of ARA geometry, but they are not interchangeable measurements.

## Artifacts

- `analysis/primes/PN7B_ALL_MEASURED_PRIME_ARA_NOTE_2026-07-23.md`
- `analysis/primes/pn7b_combine_all_measured_prime_ara.py`
- `analysis/primes/PN7B_ALL_MEASURED_PRIME_ARA_EXACT_GAP_PAIRS.csv`
- `analysis/primes/PN7B_ALL_MEASURED_PRIME_ARA_EXACT_STATES.csv`
- `analysis/primes/PN7B_ALL_MEASURED_PRIME_ARA_SUMMARY.json`

All eight reconciliation checks passed against the independently validated PN7B source metadata.
