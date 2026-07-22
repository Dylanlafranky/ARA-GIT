# Session record — PN35/PN36 large-CSV reproduction pathway

**Date:** 23 July 2026  
**Scope:** close the fresh-clone reproducibility gap identified by the independent prime-thread audit.

## Problem

PN35 and PN36 each produce a label-free prediction CSV and a separately scored CSV. The four files total about
485 MB, which is too large and inconvenient for ordinary Git tracking. The frozen builders and validators were
already tracked, but a new reader had no single documented command that recreated the omitted products and proved
that they matched the original experiment.

## Resolution

The four generated CSVs are now explicitly ignored by Git. The repository instead tracks:

- `analysis/primes/reproduce_pn35_pn36_csvs.py` — the orchestration and verification entry point;
- `analysis/primes/PN35_PN36_CSV_REPRODUCTION_MANIFEST.json` — exact SHA-256, byte-count and row-count anchors;
- `analysis/primes/requirements_pn35_pn36_reproduction.txt` — the reference numerical dependency;
- `analysis/primes/PN35_PN36_CSV_REPRODUCTION.md` — plain-language fresh-clone instructions.

The wrapper calls the original frozen primary builders rather than translating their mathematics. It keeps the
primary stage label-free, checks the prediction receipt, then calls the independent validator to open primality
labels and build the scored file. All temporary products are checked before the two large CSVs are moved into their
final locations. The tracked primary, results and validation JSON files are used as immutable compact witnesses and
are not overwritten.

## Scientific effect

This is an infrastructure correction only. PN35 and PN36 retain their recorded **NOT SUPPORTED** verdicts and their
existing scope qualifications. No model, gate, comparison, label or result was changed.

## Reproduction command

From the repository root:

```powershell
python -m pip install -r analysis/primes/requirements_pn35_pn36_reproduction.txt
python analysis/primes/reproduce_pn35_pn36_csvs.py --force
```

The no-flag form reuses any CSV whose size and SHA-256 already match. `--check` verifies existing products without
rebuilding them. Exact byte-for-byte reproduction should use the recorded reference environment: Python `3.12.13`
and NumPy `2.3.5`.
