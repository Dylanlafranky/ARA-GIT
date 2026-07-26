# H1 Public Hydraulic Dataset Audit

**Audit time:** 24 July 2026, before numerical files were downloaded or opened  
**Source:** UCI Machine Learning Repository dataset 447  
**DOI:** `10.24432/C5CW21`  
**License:** CC BY 4.0  
**Declared use:** public real-hardware test of the connection-rich two-cut ARA hypothesis

## Source facts inspected before freeze

Only the public UCI metadata page was inspected. No numerical sensor or target values were opened.

The source describes:

- an experimental hydraulic test rig;
- a primary working circuit and secondary cooling/filtration circuit connected through an oil tank;
- `2,205` repeated load cycles, each lasting `60` seconds;
- six pressure sensors, `PS1`–`PS6`, recorded at `100 Hz`;
- two volume-flow sensors, four temperature sensors, one vibration sensor, motor power and virtual efficiencies;
- independently varied condition labels for the cooler, valve, pump and hydraulic accumulator;
- four published accumulator states: `130`, `115`, `100` and `90 bar`;
- raw process measurements without source feature extraction;
- no reported missing values.

## Why this source was selected

The hydraulic accumulator is a literal storage/connection component embedded in a coupled pressure network.
Several synchronized pressure sensors observe different spatial cuts of the same rig during one completed cycle.
This matches the proposed complementary boundary after Q2:

- information-heavy, strongly aligned output may be represented adequately by one cut;
- a connection-rich distributed identity should more often retain independent structure across multiple cuts.

The six pressure channels also share units and sampling rate. This avoids comparing unrelated measurement units
and lets the test ask a narrow question: do two spatial cuts of one coupled pressure field retain held-out
accumulator-condition information absent from the best single cut?

## Selection risks

The following risks must be controlled:

1. Adjacent cycles may be autocorrelated.
2. Other component faults are superimposed and may confound accumulator classification.
3. Training-time sensor-pair selection can overfit among the 15 possible pairs.
4. Two cuts contain more values than one cut; any gain is an information-retention result, not automatically an
   ARA-specific advantage.
5. An affine 0–2 map is invertible, so equality with a same-information raw classifier is expected.
6. If one pressure sensor already measures the accumulator state almost perfectly, the benchmark may reproduce
   Q2's one-cut saturation boundary.

## Pre-open decision

Proceed only after a fidelity packet, frozen protocol, file hashes and ledger entry are written. Numerical source
values may then be downloaded and opened exactly once for the frozen test. No gate or primary endpoint may be
changed after that opening.

