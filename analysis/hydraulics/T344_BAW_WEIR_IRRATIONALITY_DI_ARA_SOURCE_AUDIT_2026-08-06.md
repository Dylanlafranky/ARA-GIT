# T344 BAW weir Irrationality Di-ARA — source audit

**Audit time:** 6 August 2026, 18:51 AEST  
**Audit status:** suitable for a frozen, time-resolved ARA test; target values unopened  
**Primary archive DOI:** <https://doi.org/10.48437/99f329-73aee6>  
**Associated paper DOI:** <https://doi.org/10.59490/jchs.2025.0050>

## Why this source was selected

The earlier river test used ordered bed geometry. It could test spatial lineage and
non-closing path structure, but it did not follow water or an object through time.
The BAW archive supplies the missing measurement:

- laboratory particle positions recorded every `0.01 s`;
- three controlled tailwater/end-sill conditions (`low`, `medium`, `high`);
- approximately `1,700–1,900` laboratory trajectories per condition;
- corresponding numerical trajectories for a later replication check; and
- videos that can be consulted only if a later visual audit is necessary.

The laboratory trajectories therefore permit a native movement cut. A particle's
successive displacement vectors can be decomposed into radial contraction/expansion
and forward/reverse turning without first passing through Fourier, POD, NMF or another
learned representation.

## Official source contents

The public directory reported the following analysis files before any workbook was
downloaded or opened:

| file | listed size | intended role | official SHA-256 |
|---|---:|---|---|
| `Spheres_lab_low.xlsx` | 24 MB | primary laboratory condition | `bf6bf4536bccabb6cb1991db52b2b630bed65de25475482d229bf1552cfbf549` |
| `Spheres_lab_medium.xlsx` | 23 MB | primary laboratory condition | `d42724a1f136a3b3b4d1e37a90cfb9e9bc2c4319d86392a89ff34e1ab62a70a7` |
| `Spheres_lab_high.xlsx` | 31 MB | primary laboratory condition | `2dfd229ac0561a5fc6601ddf9052f13d391b8e54862ea5e09d099a40af91064e` |
| `Spheres_num_low.xlsx` | 75 MB | secondary numerical replication | `6b4b30f532cfca965da92d73f92c100ed429cd5a2078a7c7dfc18d1eaf7bdfdd` |
| `Spheres_num_medium.xlsx` | 76 MB | secondary numerical replication | `feb38f39468a64df5ef50d292b8edbe716f9a4bdd1d76782147d11c0b43a6632` |
| `Spheres_num_high.xlsx` | 77 MB | secondary numerical replication | `4a3e737bfdb66ad913d08fe182d563e573648820e105da73726b88af6eb07eab` |

The three video archives total roughly `15.7 GB` and are excluded from the primary
analysis. The official checksum manifest is preserved as
`T344_BAW_WEIR_SOURCE_CHECKSUMS.sha256.txt`.

## Experimental grain

The associated methods report three laboratory configurations with different
tailwater/end-sill levels. Particle centres were tracked in the longitudinal/vertical
plane at `100 fps`, producing positions at `0.01 s` intervals. Reported laboratory
track counts are `1,903`, `1,857`, and `1,708` for the three conditions. The numerical
model contains `2,000` trajectories per condition at the same temporal interval.

This is repeated-trajectory data, not one averaged curve. It supports:

1. within-trajectory ARA movement coordinates;
2. between-trajectory broken-pair controls;
3. whole-trajectory train/test separation;
4. leave-one-condition-out transfer; and
5. laboratory-to-numerical replication.

## Data-quality hazards frozen before opening values

1. **Manual reconstruction:** the paper reports that roughly one quarter of laboratory
   tracks required some manual reconstruction. Results must be stratified by any
   available reconstruction/quality flag. If no flag is supplied, that limitation is
   irreducible and must remain prominent.
2. **Tracking gaps:** no transition may cross a missing, duplicated or non-monotone
   timestamp. Interpolation is forbidden in the primary result.
3. **Near-zero displacements:** complex quotients become unstable when either adjacent
   displacement is effectively zero. A scale-relative exclusion rule is frozen in the
   protocol and all excluded counts must be reported.
4. **Trajectory leakage:** all splits and resampling units are whole trajectories.
   Adjacent points from one trajectory may never be split across calibration and test.
5. **Condition leakage:** the transfer result holds out one complete hydraulic condition.
6. **Simulation dependence:** numerical tracks are not independent measurements of the
   same physical run. They are a secondary model replication, not additional laboratory
   sample size.
7. **Outcome-derived zones:** collision, water-cushion and hydraulic-jump labels may be
   used only if they are supplied by the archive or fixed from the paper before scoring.
   They may not be drawn after looking at T344 outcome plots.
8. **Smoothing distortion:** raw native positions are primary. Any smoothing or gap
   repair is sensitivity analysis and cannot replace the raw verdict.

## Decision

The archive is materially stronger than the static weir and river-profile candidates
for the Irrationality Di-ARA question. It directly follows movement through a controlled
accumulation/release structure, has repeated identities, supports causal broken-pair
controls and contains three intervention settings. Proceed with the frozen T344
protocol before downloading or inspecting workbook values.

