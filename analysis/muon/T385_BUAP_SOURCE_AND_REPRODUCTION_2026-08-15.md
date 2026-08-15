# T385 BUAP source and reproduction record

## Frozen source

- Landing page: <https://ciiec.buap.mx/Muon-Decay>
- Direct file: <https://ciiec.buap.mx/Muon-Decay/Datos/MD10000Last.csv>
- Retrieved: 2026-08-15 (Australia/Brisbane)
- HTTP `Content-Length`: `53,641,959 bytes`
- HTTP `Last-Modified`: `Tue, 03 Feb 2026 19:27:09 GMT`
- SHA-256: `C2DC1E012FBDF0F3C5EC305E2D8E4DD1D87B05DF5CBA39B492189C0F7D5454CD`
- Non-empty rows actually observed: `5,001`
- First record timestamp: `20260202-194801`
- Last record timestamp: `20260203-154546`
- Sampling interval stated by the source: `8 ns`

The landing page describes this as the last 10,000 events, but the retrieved frozen object contains 5,001 non-empty rows. The analysis reports the observed row count rather than silently adopting the page label.

## Reproduction

Raw data are intentionally not committed to Git. Run:

```powershell
python analysis/muon/download_t385_buap_source.py
python analysis/muon/t385_buap_causal_irrationality_di_ara.py
python analysis/muon/validate_t385_buap_causal_irrationality_di_ara.py
```

The downloader verifies the frozen hash before replacing the local file. The `MD10000Last.csv` endpoint is mutable; if BUAP updates it, the downloader exits with a hash mismatch rather than presenting new events as an exact T385 replication. A changed file may be registered as a new external replication with a new source manifest and frozen hash.

## Source parser notes

The source contains two header variants:

- `Evt number: N ... Event size = M`, with the declared size in the final CSV field;
- `Evt:N`, with a trailing empty field and no size declaration.

Both carry the same waveform sample layout. The frozen parser accepts both and excludes the non-waveform final field. Predictor time is measured from the detected first pulse; row length and record end are forbidden because the acquisition buffer reveals the second-pulse position.

## Compact committed outputs

The repository stores the protocol, executable analysis, validator, figure, HTML report, JSON results, model scores, lead profile, quadrant occupancy, eligibility ledger and bootstrap summary. It does not store the 53 MB raw waveform CSV or a large per-window derivative CSV.
