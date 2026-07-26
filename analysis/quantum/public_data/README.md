# Q2 public-data reproduction

The Q2 source is the open Zenodo dataset:

<https://doi.org/10.5281/zenodo.14033026>

Expected archive:

- `AllopticalSCQreadout_data.zip`
- SHA-256:
  `73F3E2CA7B3658452B4C171532C751E96D7392DCB8741B87A18E28C7073D67FD`

The source archive and extracted files are intentionally ignored by Git. The Q2 runner downloads the immutable
DOI version when `--download` is supplied, verifies the checksum, and extracts only the required files.

Install the analysis dependencies with:

```powershell
python -m pip install -r ..\q2_public_hardware_requirements.txt
```

Then run from `analysis/quantum`:

```powershell
python q2_public_hardware_iq_test.py --download
python q2_public_hardware_iq_validate.py
```

The raw source is never rewritten. All committed CSV and JSON outputs are derived summaries and can be regenerated.

## Q4/Q5 Bell-tomography reproduction

The Q4/Q5 source is the public Figshare deposit:

<https://doi.org/10.6084/m9.figshare.14160476.v2>

Place these four archives in `q4_bell_tomography/`:

| Archive | File ID | Size | MD5 |
|---|---:|---:|---|
| `UPDOWN-DOWNUP.zip` | `26690657` | `307629500` | `1724b4484ffb88e41dbac5f50981e91a` |
| `UPDOWN+DOWNUP.zip` | `26690660` | `305874138` | `43f782ed4404b01393fb57a2da5d1534` |
| `UPUP-DOWNDOWN.zip` | `26690663` | `41182988` | `8cd8a5f2b3b9a2ccd090e47312bcc390` |
| `UPUP+DOWNDOWN.zip` | `26690666` | `151973378` | `3275210b912d51e5f10ba99d93ad6ca5` |

Direct public downloads use:

`https://ndownloader.figshare.com/files/<file-id>`.

Then run from the repository root:

```powershell
python analysis\quantum\q5_bell_four_state_test.py
python analysis\quantum\q5_bell_four_state_validate.py
```

The test verifies all source checksums and the frozen protocol checksum before reconstruction. The large source
archives are intentionally ignored by Git.

## Q6/Q6B coherence-ladder reproduction

Q6 and Q6B reuse the same four immutable Q4/Q5 Bell-tomography archives. Q6 is retained as a raw-tensor
physicality diagnostic. Q6B applies the frozen positive-semidefinite, unit-trace density-matrix correction and is
the scientifically usable coherence-ladder result.

From `analysis/quantum` run:

```powershell
python q6_chsh_coherence_ladder_test.py
python q6b_physical_chsh_coherence_test.py
python q6b_physical_chsh_coherence_validate.py
```

The runners verify all archive and frozen-protocol checksums. The large bootstrap CSVs are derived artifacts and
can be regenerated from the ignored public archives.

## Q20 Willow surface-code reproduction

Q20 uses the public Google Quantum AI deposit:

<https://doi.org/10.5281/zenodo.13273331>

The registered source archive is:

- `google_105Q_surface_code_d3_d5_d7.zip`
- size: `5,716,907,033` bytes
- MD5: `21fa6ad35b395d838ebcdbc92e364a12`

Downloading the full archive is unnecessary. `q20_zenodo_range_extract.py` reads its ZIP central directory,
downloads only sixteen registered members for one distance-5 patch, and verifies each member's CRC-32.

Run from `analysis/quantum` with a Python environment containing NumPy:

```powershell
python q20_zenodo_range_extract.py
python q20_willow_ara_geometry_calibrate.py
python q20_willow_ara_relation_decoder_test.py
python q20_willow_ara_relation_decoder_validate.py
```

The ignored source subset is written to:

`public_data/q20_willow_105q/`

Committed protocols, metrics, controls, bounded projections, result JSON and independent validation are sufficient
to audit the result without committing the raw source records.

## Q21 Willow recursive-child reproduction

Q21 uses the same immutable Zenodo archive as Q20 but stages a fresh distance-5
patch so its geometry is frozen before its outcomes are extracted.

Run from `analysis/quantum` with a Python environment containing NumPy:

```powershell
python q21_zenodo_range_extract.py --stage geometry
python q21_willow_child_topology_calibrate.py
```

The committed frozen protocol must hash to:

`bd26fa2e70c1e4ddbb4e5d768b6099cb6caaea3c96ab1ce3cac545d6575cd24d`

Then run:

```powershell
python q21_zenodo_range_extract.py --stage outcomes
python q21_willow_recursive_child_topology_test.py
python q21_willow_recursive_child_topology_validate.py
```

The two ignored source roots are:

- `public_data/q21_willow_105q/` for the six pre-freeze geometry/event members;
- `public_data/q21_willow_105q_outcomes/` for the two post-freeze targets.

The primary test retains eight time-grandchildren and sixteen directed local
handovers beneath the recompressed parent ridge. The independent validator
rebuilds every coordinate and reruns all `1,998` permutations without
importing the primary runner.

## Q22/Q22B Willow vertical-tier reproduction

Q22A and Q22B use two additional distance-5 Willow patches. Each source extraction is staged so detector
geometry and events are available before freeze while logical-observable target bits remain absent.

Q22A is retained as an unflipped method-control:

```powershell
python q22_zenodo_range_extract.py --stage geometry
python q22_willow_vertical_relation_calibrate.py
python q22_zenodo_range_extract.py --stage outcomes
python q22_willow_vertical_relation_test.py
python q22_willow_vertical_relation_validate.py
```

Q22B applies the corrected net odd-parity orientation \(x_{4\rightarrow1}=2-x_4\) on a new patch:

```powershell
python q22b_zenodo_range_extract.py --stage geometry
python q22b_willow_flip_vertical_calibrate.py
python q22b_zenodo_range_extract.py --stage outcomes
python q22b_willow_flip_vertical_test.py
python q22b_willow_flip_vertical_validate.py
```

The Q22B protocol must hash to:

`625689063971a2c56a568f1a58610915e1792e3d0721305408ffff3452334725`

The four ignored source roots are:

- `public_data/q22_willow_105q_geometry/`
- `public_data/q22_willow_105q_outcomes/`
- `public_data/q22b_willow_105q_geometry/`
- `public_data/q22b_willow_105q_outcomes/`

The independent validators rebuild the coordinates without importing the primary runners. Q22A passed `56/56`
checks and Q22B passed `57/57`.

## Q23 distance-7 connection-web/bit reproduction

Q23 moves to the previously untouched distance-7 patch `d7_at_q6_7`. Stage geometry first:

```powershell
python q23_zenodo_range_extract.py --stage geometry
python q23_connection_bit_calibrate.py
```

Before outcomes are extracted, the protocol must hash to:

`5ec5c9dd363c6d6edc93e00493d78c5cfa67be3e40d0009785d9e5c0a57e1c0a`

Then run:

```powershell
python q23_zenodo_range_extract.py --stage outcomes
python q23_connection_bit_test.py
python q23_connection_bit_validate.py
python q23_secondary_connection_exploration.py
```

Raw public subsets are ignored at:

- `public_data/q23_willow_d7_geometry/`
- `public_data/q23_willow_d7_outcomes/`

The validator independently rebuilds all four relation webs, block identities, controls, gates and 3,996
permutations; it passed `117/117`.

## Q25 external atomic-qubit ARA^9 reproduction

Q25 uses the immutable Zenodo deposit:

<https://doi.org/10.5281/zenodo.4604775>

The checksum-locked source contains reconstructed two-atom density matrices and Bell-measurement operators. The
small source files are downloaded into the ignored directory:

`public_data/q25_atomic_bell/`

Run from `analysis/quantum`:

```powershell
python q25_zenodo_download.py
python q25_ara9_blind_missing_cut_test.py prepare
python q25_ara9_blind_missing_cut_test.py predict
python q25_ara9_blind_missing_cut_test.py reveal
python q25_ara9_blind_missing_cut_validate.py
```

The staged runner writes eight-cell geometry packets and sealed target packets separately. The prediction packet
must be written and hashed before the reveal stage reads any hidden ninth cut. The frozen protocol hash is:

`d267c807ff60ca84f2475e04fd29b22ed953e3c6b23036aeb022de1dd6c69397`.

The frozen prediction hash from the registered run is:

`ec06e6ea3075cfd30f945de3142613c7cf40b2b33f258ef5911d8f0d8c7ad390`.

Q25 returned `NOT SUPPORTED — 7/12`; independent validation passed `490/490`.

## Q26 public ARA^9 temperature trajectories

Q26 uses the immutable Zenodo deposit:

<https://doi.org/10.5281/zenodo.14880901>

The target file is `SuppFigure10.csv`, MD5:

`9a9e3abac0ee8f80535e17ec72313919`.

Downloaded source files are ignored at:

`public_data/q26_temperature_ara9/`

The downloader preserves the staged boundary. Run from `analysis/quantum`:

```powershell
python q26_zenodo_download.py --stage development
python q26_ara9_larger_wave_trajectory_test.py prepare
python q26_ara9_larger_wave_trajectory_test.py predict
python q26_zenodo_download.py --stage target
python q26_ara9_larger_wave_trajectory_test.py reveal
python q26_ara9_larger_wave_trajectory_validate.py
```

The target must not be downloaded before the protocol is frozen and the `prepare` and `predict` stages have
written the sealed geometry and prediction hashes. The registered hashes are:

- protocol: `0bd8f2a0ee96733e0411d477a5c808c4ebd100b083b84b30108d05ed110347e6`;
- predictions: `e0e52a552df3b114bc6def1ea392f697d9da301f77d5c71214e7c491355be968`.

Q26 returned `SUPPORTED — 13/14` scored gates. Independent validation passed `282/282`. The supported component
is crest-to-trough closure amplitude; a stable orientation flip was not supported.
