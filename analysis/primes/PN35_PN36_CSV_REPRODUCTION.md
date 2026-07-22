# Reproducing the large PN35 and PN36 CSV files

The four PN35/PN36 CSV products are deterministic build artifacts, not hand-edited source data. Together they
occupy about 485 MB, so Git intentionally ignores them. The repository instead stores the frozen methods, compact
receipts, result summaries and exact output hashes needed to reconstruct and verify them.

## Quick path

From the repository root, using Python 3.12:

```powershell
python -m pip install -r analysis/primes/requirements_pn35_pn36_reproduction.txt
python analysis/primes/reproduce_pn35_pn36_csvs.py
```

On a fresh clone this creates:

- `analysis/primes/PN35_SAME_SCALE_GOLDEN_CROSS_PREDICTIONS.csv`
- `analysis/primes/PN35_SAME_SCALE_GOLDEN_CROSS_SCORED.csv`
- `analysis/primes/PN36_PHI_TO_PENTAGON_CONVERSION_PREDICTIONS.csv`
- `analysis/primes/PN36_PHI_TO_PENTAGON_CONVERSION_SCORED.csv`

The script verifies every output against
`analysis/primes/PN35_PN36_CSV_REPRODUCTION_MANIFEST.json`. Existing matching files are reused. Use `--force` for
a genuine clean recalculation:

```powershell
python analysis/primes/reproduce_pn35_pn36_csvs.py --force
```

Useful narrower commands:

```powershell
# Rebuild PN35 only.
python analysis/primes/reproduce_pn35_pn36_csvs.py --test pn35 --force

# Rebuild only the label-free prediction stage.
python analysis/primes/reproduce_pn35_pn36_csvs.py --stage predictions --force

# Verify existing products without rebuilding.
python analysis/primes/reproduce_pn35_pn36_csvs.py --check

# Keep generated CSVs outside the repository.
python analysis/primes/reproduce_pn35_pn36_csvs.py --output-dir D:\ARA-reproductions --force
```

Allow about 0.5 GB for the final files plus temporary working space. The reference hashes were produced with
Python `3.12.13` and NumPy `2.3.5`. A different Python random-sampling implementation or numerical library version
may reproduce the method but fail byte-for-byte identity; exact reproduction should therefore use the reference
environment.

## Evidence chain

The wrapper does not reimplement the tests. It invokes the original frozen code in this order:

```text
frozen protocol + frozen primary script
        -> label-free prediction CSV
        -> primary receipt and prediction SHA-256
        -> independent validator opens primality labels
        -> scored CSV + results + validation receipt
        -> scored/results/validation SHA-256 checks
```

Temporary outputs are written beside the requested destination. A CSV is moved into its final location only after
its row count, byte count and SHA-256 all match the recorded experiment. The generated metadata is also checked
against the tracked canonical receipts, but the tracked copies are not overwritten.

This preserves the important methodological boundary: PN35/PN36's candidate coordinates are reconstructed without
opening primality labels; only the separate validator supplies labels and scores the frozen coordinates.
