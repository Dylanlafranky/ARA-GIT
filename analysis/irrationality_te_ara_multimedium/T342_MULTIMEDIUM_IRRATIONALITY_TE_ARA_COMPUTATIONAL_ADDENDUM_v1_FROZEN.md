# T342 frozen computational addendum — cadence-neutral ordered blocks

**Frozen:** 5 August 2026, after source acquisition/schema inspection and
before calculating any T342 ARA coordinate or score  
**Applies to:** `T342-MULTIMEDIUM-IRRATIONALITY-TE-ARA-v1`

The source battery ranges from five-second cold-room sampling to 10 kHz
pendulum data and 44.1 kHz acoustic data. Treating every recorded row as an
independent inferential unit would let acquisition cadence, rather than
physical replication, dominate computation and precision.

The following deterministic cap is therefore frozen before scoring.

## Inferential ordered-block sample

For each domain and split:

1. Construct native consecutive `q` states inside each declared lineage.
2. Divide every lineage into non-overlapping blocks of at most 256 consecutive
   valid, non-boundary `q` states. A gap, invalid amplitude or split boundary
   starts a new block.
3. If all blocks contain at most 100,000 states, retain all blocks.
4. Otherwise allocate the 100,000-state budget across lineages as evenly as
   possible, then choose blocks at evenly spaced chronological ranks inside
   each lineage. Ties resolve by lineage name, then earlier block start.
5. Retain complete blocks until the next block would exceed the cap. The final
   block may be truncated chronologically to use the remaining budget, but it
   must retain at least two states.

The selected blocks retain native adjacency and waveform values. They are not
smoothed, averaged, interpolated or spectrally processed. All primary
transition scores, exact 1,000 within-block shuffles and landmark audits use
this same frozen sample.

Full-source row counts, missingness, amplitude validity and quadrant coverage
remain descriptive quality outputs. Cross-domain verdicts are domain-level,
never row-pooled.

## Why this is not an outcome-tuned correction

- the cap and block length are identical for every domain;
- selection uses only lineage, order, validity and recording count;
- no ARA value, quadrant, landmark distance or outcome enters block choice;
- it was specified before the first T342 coordinate was calculated;
- the independent validator reconstructs the selection from the raw sources.

The addendum changes computational grain only. All equations, gates and
interpretive boundaries in the primary frozen protocol remain unchanged.

