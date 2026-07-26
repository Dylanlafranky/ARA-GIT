# Q31 source-data reproduction

Large public source archives are intentionally excluded from Git. The Q31
audit expects this local layout:

```text
q31_data/
├── source/
│   ├── SourceData_Fig2.xlsx
│   ├── SourceData_Fig3.xlsx
│   └── SourceData_Fig4.xlsx
├── candidate5/
│   └── quantinuum-2d-trajectory-data.zip
└── candidate6/
    └── Source Data _ full_version.zip
```

## Candidate 4 — photonic quantum walks

Public record:

- <https://zenodo.org/records/18264638>
- <https://doi.org/10.5061/dryad.3ffbg79vk>

Files and MD5:

| File | MD5 |
|---|---|
| `SourceData_Fig2.xlsx` | `746c65ddccd37e82d0710712ecfec4fb` |
| `SourceData_Fig3.xlsx` | `c24a6ed6475b64d61e08318eeae0c629` |
| `SourceData_Fig4.xlsx` | `7d4dda38985171a5196981ee5a7ed397` |

## Candidate 5 — Quantinuum H1 trajectories

Public record:

- <https://zenodo.org/records/20075236>

Rename the downloaded archive to:

`quantinuum-2d-trajectory-data.zip`

MD5:

`185a52581636ce37dfeb950bf64214de`

## Candidate 6 — fluxon-decay transitions

Public record:

- <https://zenodo.org/records/8004359>

File:

`Source Data _ full_version.zip`

MD5:

`ced1ed4af893ad064045900903e19a17`

## Run

From `analysis/quantum/`:

```powershell
python q31_data_gate_audit.py
python q31_build_notebook.py
python q31_validate_data_gate.py
```

The audit writes `Q31_DATA_GATE_AUDIT_RESULTS.json`. It checks eligibility and
does not calculate the registered Q31 flip outcome on a source that fails a
data gate.
