# Q44 reproduction

Q44 is a prospective conditional prediction test. Preserve the stage order:

1. download and verify the frozen public archive;
2. build local derived caches;
3. prepare and hash predictions without reading evaluation \(C_4\);
4. reveal evaluation \(C_4\) and score;
5. independently recompute the reported metrics.

Source:

- Zenodo DOI: `10.5281/zenodo.16753415`
- archive: `unnati_submit_12_inhomo_v1_mimic.hdf5.zip`
- deposited MD5: `08b2eaa89268952f7e197eecb2ea9610`

From `analysis/quantum`, run:

```powershell
python q44_zenodo_download.py

$py = "C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py q44_ara_mixing_prediction_test.py build --workers 8
& $py q44_ara_mixing_prediction_test.py prepare
```

On the recorded target, the Q44 `prepare` stage correctly stops at the frozen
eligibility gate. To reproduce the pre-score sparse-group amendment and its
result:

```powershell
& $py q44a_sparse_group_ara_mixing_prediction.py prepare
& $py q44a_sparse_group_ara_mixing_prediction.py score
& $py q44a_validate_sparse_group_ara_mixing.py
```

The explicit Python 3.12 runtime is necessary on the current workstation
because the repository's local numerical dependencies are compiled for
CPython 3.12. Any compatible Python 3.12 environment with NumPy, h5py and
Matplotlib may be substituted.

The critical seal is:

`public_data/q44_mixing_inhomo_v1_mimic/q44_frozen_predictions.npz`

Q44 stops before creating that artifact. Q44A creates:

`public_data/q44_mixing_inhomo_v1_mimic/q44a_frozen_predictions.npz`

Its recorded SHA-256 is
`3f75eed32c96ba0810d07e36bf19683925e330ba4466aa81fa0f9527d829c5da`.
The artifact contains visible \(C_1,C_2,C_3\), target indices, coefficients and
predictions. It does not contain actual \(C_4\).

Primary outputs:

- `Q44_ARA_MIXING_PREDICTION_ELIGIBILITY.json`
- `Q44A_SPARSE_GROUP_ARA_MIXING_RESULTS.json`
- `Q44A_SPARSE_GROUP_ARA_MIXING_CYCLES.csv.gz`
- `Q44A_SPARSE_GROUP_ARA_MIXING_VALIDATION.json`
- `Q44_Q44A_ARA_MIXING_PREDICTION_REPORT_2026-07-28.md`

The archive, extracted HDF5 file, connected-matrix cache and sealed prediction
artifact are intentionally excluded from Git because they are reproducible and
large.
