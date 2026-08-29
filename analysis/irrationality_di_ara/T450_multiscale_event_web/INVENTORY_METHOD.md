# T450 pre-freeze source inventory

This is a source-capability audit, not an ARA test and not a frozen T450 protocol.

## Question

Which independently measurable pose, behaviour and environmental channels exist in the 47-fly cohort; at what native time resolution; and with enough demonstrated continuity to support defensible micro, child and parent rungs?

## Source

Princeton Drosophila lifetime dataset, DOI `10.34770/1sab-8845`, `final_data/*.h5`.

## Exact metadata checks

For every HDF5 file:

- root attributes and native frame rate;
- object names, shapes, data types, chunking and compression;
- node and behaviour vocabularies;
- frame count and implied recorded duration;
- agreement between `behaviors`, `tracks`, `seconds_elapsed`, `on_edge`, `temperature` and `relative_humidity` time-axis lengths.

## Pose-continuity sample

Exact full-frame pose profiling would require reading tens of billions of coordinate values. A smoke test also showed that the source's `tracks` chunks are much wider than a short requested interval, so a dense remote sample would fetch tens of gigabytes without adding equivalent inventory value.

The already-completed T448 extraction is reused for all-47 cohort coverage and recorded-hour continuity. Pose continuity is audited on eight files: the lexically first and last HDF5 file from each of the four experimental dates. This spans all experimental batches and the outer available camera/fly positions without pretending that a remote limb-level audit was exhaustive.

The pose audit uses four deterministic, non-overlapping five-second core-pose blocks per selected fly, centred at 12.5%, 37.5%, 62.5% and 87.5% of its recording. It checks `head`, `thorax` and `abdomen` using both x and y coordinates at all four lifecycle positions.

Every selected fly also contributes one all-14-node block. Those blocks are assigned evenly across the four lifecycle quarters. All-node continuity is read from the x-coordinate mask; one file from each experimental batch also has all 14 y-coordinate masks read to test whether x/y missingness agrees before that shortcut is accepted.

Within each block it records:

- both-coordinate availability for the three core body nodes at all four lifecycle positions;
- x-coordinate availability for every body node in the assigned all-node block;
- x/y missingness agreement for all nodes in one file from each experimental batch;
- frames with all 14 nodes and frames with at least 10 of 14 nodes in the stratified all-node sample;
- longest uninterrupted tracked run per node;
- lifecycle quartile and edge share.

This sample is sufficient for rung selection and pilot feasibility, but it is not an exact whole-lifespan missingness estimate. It does not claim that every non-core node was checked in every fly at every lifecycle quarter, or even that all 47 flies have equivalent limb-pose continuity. Any frozen T450 analysis must recompute quality at the exact windows it uses.

## Leakage boundary

Death and collapse landmarks are not used to choose samples or judge pose quality. Blocks are positioned by fractional recording progress only.
