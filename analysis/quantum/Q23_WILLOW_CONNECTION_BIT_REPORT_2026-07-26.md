# Q23 Willow connection-web and logical-bit parent ARA

**Date:** 26 July 2026  
**Status:** **NOT SUPPORTED** (`3/10` frozen gates)  
**Source:** Google Willow public surface-code records, DOI `10.5281/zenodo.13273331`  
**Fresh source:** distance-7 patch `d7_at_q6_7`, X/Z, 13/30 rounds

## Question

Q20-Q22 mainly dissected detector changes: a time/information-heavy expression. Q23 tested Dylan's proposed next
cut:

1. construct the larger connection-heavy relation web independently;
2. construct the logical bit identity independently;
3. move one rung up;
4. ask whether their parent lands at the ARA `1.0` ridge.

The logical outcome was used only after the connection instrument, block grain, parent equation, controls and
thresholds were frozen.

## ARA construction

The Q21 four-by-four handover matrix supplies sixteen child-to-child relation paths per shot and always closes to
TE-ARA `2`. In each 250-shot block, Q23 compared the mean web in the first and second halves:

\[
C_{\rm raw}
=
2\left(1-\frac{\lVert H_B-H_A\rVert_1}{4}\right).
\]

This primary connection identity is high when the complete relation web persists.

The logical bit was constructed separately:

\[
B_{\rm raw}=2(1-p_{\rm flip}).
\]

Because these are different identities with different native magnitudes, each marginal ordering was separately
mapped to its open `0-2` ARA diameter using midpoint ranks. The pairing between them was not used in either local
normalization.

Their one-rung-up parent was:

\[
\boxed{
P=\frac{2B}{C+B}
},
\qquad
D=|P-1|.
\]

Correct blocks were compared with a half-cycle shift, the opposite-basis bit, a spatially broken web, the flip
orientation and 999 bit-block permutations.

## Prospective separation

The public archive contained four distance-5 patches, all already opened by Q20-Q22. Q23 therefore moved to the
previously untouched distance-7 patch. Twelve geometry/event members were extracted first. No logical outcome
file was present while the geometry was calibrated and the protocol/code hashes were frozen.

Frozen protocol SHA-256:

`5ec5c9dd363c6d6edc93e00493d78c5cfa67be3e40d0009785d9e5c0a57e1c0a`

Only then were the four `obs_flips_actual.b8` members extracted.

## Primary result

| Dataset | Flip rate | Paired ridge distance | Null mean | Parent median | Rank relation | Permutation p |
|---|---:|---:|---:|---:|---:|---:|
| X, 13 rounds | 0.05850 | 0.37987 | 0.38410 | 1.01787 | +0.05371 | 0.375 |
| X, 30 rounds | 0.06122 | 0.38132 | 0.38469 | 1.01560 | +0.00509 | 0.397 |
| Z, 13 rounds | 0.05578 | 0.39831 | 0.38438 | 0.99433 | -0.09616 | 0.836 |
| Z, 30 rounds | 0.06210 | 0.38513 | 0.38437 | 0.99515 | -0.02300 | 0.525 |

Only source integrity, coordinate range and parent-median gates passed. The genuine pair was not consistently
closer to the ridge than shifted, wrong-bit or spatially broken controls. No permutation p-value approached the
frozen `0.01` threshold, and the signed relation changed between X and Z.

Independent validation rebuilt all four detector webs, block identities, rank diameters, parent coordinates,
controls, gates and 3,996 permutations without importing the Q23 runner or feature module. It passed `117/117`
checks.

## What “the parent ends at 1” means after this test

All four genuine parent medians landed near `1`, exactly as Dylan proposed. But relation-broken controls also did.
When two identities are separately rank-normalized to the same symmetric `0-2` grid, a random pairing is
exchangeable: swapping \(C\) and \(B\) changes \(P\) to \(2-P\). Its aggregate parent therefore tends to centre
near `1` even without coupling.

Consequently:

\[
\boxed{
\text{parent near }1
\text{ is not sufficient;}
\quad
\text{correct pairing must be closer to }1
\text{ than broken pairing.}
}
\]

This does not discard the ridge rule. It separates a parent-level coarse-grained ridge from evidence that two
particular lower identities are coupled.

## Predeclared decompressions and post-result clue

The frozen protocol required three connection-web decompressions to be reported without rescue authority:
same-child persistence, anti-child handover and web concentration.

The anti-child handover coordinate had a small positive rank relation with bit retention in all four datasets:

- X/r13: `+0.01746`;
- X/r30: `+0.07181`;
- Z/r13: `+0.09223`;
- Z/r30: `+0.10186`.

Their mean was `+0.07084`. A post-result pooled permutation gave `p=0.0226`. This is an exploratory lineage clue,
not a supported result: its pooled test and threshold were not frozen, four decompositions were inspected, and
the effect is small. It cannot rescue Q23.

## Verdict and boundary

The complete sixteen-path web-stability identity did not show specific block-level coupling to logical retention
at this grain. That rejects this exact larger-connection-wave instrument. It does not show that the missing
counterpart is absent, identify an external field, reject individual handover lineages, test causality or
falsify ARA generally.

The clean follow-up is to freeze the anti-child handover lineage—not the complete web—on still-sealed distance-7
round counts, using the same shifted, wrong-bit, broken-web and permutation controls.

## Reproduction files

- `Q23_WILLOW_CONNECTION_BIT_PROTOCOL_v1_FROZEN.md`
- `Q23_WILLOW_CONNECTION_BIT_FREEZE_MANIFEST.json`
- `Q23_WILLOW_CONNECTION_BIT_CALIBRATION.json`
- `Q23_WILLOW_CONNECTION_BIT_RESULTS.json`
- `Q23_WILLOW_CONNECTION_BIT_VALIDATION.json`
- `Q23_WILLOW_CONNECTION_BIT_SECONDARY_EXPLORATION.json`
- `q23_zenodo_range_extract.py`
- `q23_connection_bit_calibrate.py`
- `q23_connection_bit_test.py`
- `q23_connection_bit_validate.py`

