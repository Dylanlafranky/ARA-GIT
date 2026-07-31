# Q45 reproduction

Date: 28 July 2026

## Source

Q45 reuses the verified Q44 public archive:

`public_data/q44_mixing_inhomo_v1_mimic/unnati_submit_12_inhomo_v1_mimic.hdf5.zip`

Deposited MD5:

`08b2eaa89268952f7e197eecb2ea9610`

The archive and extracted HDF5 are intentionally local because of their size.
Use `q44_zenodo_download.py` and `Q44_REPRODUCTION.md` to reproduce that source
stage.

## Run

Use the repository's Python 3.12-compatible numerical environment with
`numpy`, `h5py` and `matplotlib`.

From the repository root:

```powershell
python analysis/quantum/q45_15_cycle_parent_complement_test.py --workers 8
python analysis/quantum/q45_validate_15_cycle_parent_complement.py
```

The first run builds a local `118.8 MB` product-relation cache directly from
the raw density matrices. Later runs reuse it and finish in seconds.

## Recreated tracked-scale artifacts

- frozen-protocol hash check;
- lineage-level compressed CSV;
- seed-level flow CSV;
- bounded phase-profile NPZ;
- JSON results and validation;
- PNG and SVG diagnostics.

The large raw HDF5 and local matrix caches are reproduction inputs, not Git
artifacts.

