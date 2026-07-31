# Q46 reproduction

Date: 28 July 2026

## Inputs

Q46 reuses:

- the verified Q44 public archive, MD5
  `08b2eaa89268952f7e197eecb2ea9610`;
- `Q45_15_CYCLE_PARENT_COMPLEMENT_LINEAGES.csv.gz`; and
- the Q44 connected-relation cache.

Use `Q44_REPRODUCTION.md` and `Q45_REPRODUCTION.md` to recreate those stages.
The 3.45 GB extracted HDF5 remains a local reproduction input.

## Run

Use a Python 3.12-compatible environment containing `numpy`, `h5py` and
`matplotlib`. From the repository root:

```powershell
python analysis/quantum/q46_double_parent_internal_ara_test.py
python analysis/quantum/q46_validate_double_parent_internal_ara.py
```

The test reads the two local parent Bloch vectors directly from the raw
density matrices. On the reference machine this takes roughly three minutes.

## Recreated artifacts

- compressed 15-sample-window record;
- JSON result and validation;
- PNG and SVG diagnostics; and
- frozen-protocol hash verification.

