# Q41B target lock — frozen before target access

Date: 2026-07-27 (Australia/Brisbane)

Test ID: `Q41B-CADENCE-STRAND-REVERSAL-LANDMAX-v1`

## Inherited frozen files

- `Q41_CADENCE_STRAND_REVERSAL_FIDELITY_v1.md`
- `Q41_CADENCE_STRAND_REVERSAL_PROTOCOL_v1_PRETARGET_FROZEN.md`
- `Q41_TARGET_LOCK_v1_FROZEN.md`

Q41B changes only the target archive. The operator and gates remain exactly as
frozen in those files and in the Q41B protocol.

## Target

- DOI: `10.5281/zenodo.16753415`
- Archive: `unnati_submit_12_inhomo_v1_landmax.hdf5.zip`
- Deposited MD5: `f2e191d2f06643818c4ba64743e16238`
- Member: `unnati_submit_12_inhomo_v1_landmax.hdf5`
- Branch: `c2_2local connectivity`

At freeze time this archive was absent from
`analysis/quantum/public_data`. It had not been opened or inspected by the
Q41B test.

## No-repair clause

Q41B must not repair the Q40-derived strand rule if the landmax result fails.
Any later amplitude, partial-reversal or continuous-strand operator requires a
new numbered test.

