# Q20 Willow ARA dataset audit

**Recorded:** 26 July 2026  
**Source:** [Google Quantum AI Willow QEC deposit](https://doi.org/10.5281/zenodo.13273331)  
**Source version:** Zenodo record `13273331`, version `1.0.0`  
**License:** CC BY 4.0  
**Audit status:** suitable for an exploratory same-deposit development/holdout test

## Why this source

The deposit contains raw surface-code detector events and the corresponding observable-flip targets. This gives
Q20 an objective predictive endpoint while allowing the ARA geometry to be constructed from raw detector
relations before the target is opened.

The full `google_105Q_surface_code_d3_d5_d7.zip` archive is `5,716,907,033` bytes. Its Zenodo MD5 is:

`21fa6ad35b395d838ebcdbc92e364a12`

`q20_zenodo_range_extract.py` reads the ZIP central directory, downloads only the sixteen registered members and
checks every extracted member against its ZIP CRC-32. The ignored raw subset can therefore be reproduced without
downloading the entire archive.

## Registered subset

One distance-5 patch, `d5_at_q4_7`, is used.

| Role | Basis | Cycles | Shots | Detectors per shot | Raw detector bytes |
|---|---:|---:|---:|---:|---:|
| development | X | 13 | 50,000 | 312 | 1,950,000 |
| development | Z | 13 | 50,000 | 312 | 1,950,000 |
| untouched holdout | X | 30 | 50,000 | 720 | 4,500,000 |
| untouched holdout | Z | 30 | 50,000 | 720 | 4,500,000 |

For each row the registered source members are:

- `metadata.json`;
- `circuit_ideal.stim`;
- `detection_events.b8`;
- `obs_flips_actual.b8`.

The `b8` detector records are byte-aligned, little-endian packed bits. A `1` means that detector changed and a
`0` means it did not.

## Outcome-blind development inspection

Only the two 13-cycle `detection_events.b8` files, their metadata and detector coordinates were read during
geometry calibration. `obs_flips_actual.b8` was not read.

| Basis | Mean events per shot | Zero-event fraction |
|---|---:|---:|
| X | 20.51284 | 0.00010 |
| Z | 21.02466 | 0.00006 |

The circuit exposes three direct detector coordinates: physical `x`, physical `y` and cycle/time `t`. For each
possible pair, Q20 formed the four ARA child allocations and measured the development variability of their
crossed-versus-aligned relation.

| Diameter pair | Pooled relation-coordinate SD |
|---|---:|
| x–y | 0.0507863 |
| x–time | **0.0897184** |
| y–time | 0.0857352 |

The frozen outcome-blind rule selects the pair with the largest pooled relation variability. It therefore selects
**x–time**. This selection used no observable-flip labels.

Calibration artifact:

`Q20_WILLOW_ARA_GEOMETRY_CALIBRATION.json`

SHA-256:

`29449fd5c5a27c87c2a0966afbcaaa0b20b28f480ca952c0bfc44d5071e0ed4e`

## Data-quality strengths

- The source is the authors' public experimental deposit.
- Both development and holdout contain 50,000 shots per basis.
- Raw detector records, detector coordinates and outcome targets are present.
- Development and holdout differ in experiment duration, so this is not a random split of identical rows.
- X and Z provide two separately scored physical preparations.
- Source members are immutable and individually CRC-verified.

## Limitations

- Development and holdout belong to the same processor, patch and deposit. This is not independent-device
  replication.
- The holdout has more cycles and therefore more detector coordinates. Q20 must use normalized diameter
  coordinates rather than fixed detector indices.
- The target is the actual logical-observable flip that a decoder should predict. A logical decoding failure is
  the disagreement between a prediction and that target.
- This first test addresses frequent ordinary records. It does not yet isolate the approximately hourly rare
  correlated bursts discussed in the source paper.
- Q20 tests whether a deliberately small ARA relation coordinate contains predictive information. It is not
  registered as a competition with full surface-code decoders.

## Reproduction

From `analysis/quantum`:

```powershell
python q20_zenodo_range_extract.py
python q20_willow_ara_geometry_calibrate.py
```

The source members are written below `public_data/q20_willow_105q/` and are intentionally ignored by Git.

