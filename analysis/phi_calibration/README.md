# T302 — empirical Phi calibration in ordered phyllotaxis

> **Current scope (3 August 2026):** Standalone Phi is no longer the leading
> general ARA irrationality hypothesis. This folder's Phi tests remain valid
> bounded tests of specific operators. The parent model is now the complex
> contraction/expansion × forward/reverse phase quadrant. Its first
> ARA-specific radial placement provisionally spanned `1/e ↔ Phi`, but T307
> did not support that asymmetric span in the idealised muon scheduling model.
> T333 then tested candidate reciprocal `1/Phi <-> Phi` breathing on recorded
> qutrit hardware data. The primary centre instead recovered a stable
> `0.5533 <-> 1.8069` reciprocal breath; two secondary centres sat nearer
> `0.5894 <-> 1.699`. T334 then replicated the four-sector coordinate and
> octave-relative reciprocal closure in public bubble lineages, but at the
> much narrower identity-specific scale `alpha~1.2`; exact time ordering did
> not survive strict holdout. The current lead is therefore a shared
> contraction/expansion x forward/reverse coordinate with identity-specific
> radial amplitude, while `1/e` remains a separate decay landmark and Phi
> remains a narrower candidate. See
> `ARA_COMPLEX_IRRATIONALITY_QUADRANT_HYPOTHESIS_2026-08-03.md`.

This folder contains a reproducible ARA-native calibration of the proposed
Phi handover landmark using ordered Arabidopsis leaf-placement measurements.

## Why this dataset

The source provides measured placement order, not only a finished spiral
image, and includes two biological perturbations alongside wild type. That
makes it more useful than a sunflower photograph for separating:

- the local placement step;
- the longer cumulative carrier;
- ordered open-space clearance;
- the effect of disturbed biological regulation.

Primary source:

Tameshige et al. (2025), “Mutual inhibition between EPFL2 and auxin extends
the intervals of periodic leaf morphogenesis,” *Nature Communications*,
DOI [`10.1038/s41467-025-65792-y`](https://doi.org/10.1038/s41467-025-65792-y).

## Reproduce

From this directory:

```powershell
python t302_phi_phyllotaxis.py
python validate_t302_phi_phyllotaxis.py
```

The first command downloads the publisher's immutable source-data archive,
checks the archive and workbook SHA-256 hashes, reconstructs the plant
sequences, runs the frozen analysis and regenerates all CSV, JSON and HTML
artifacts. The second command independently recalculates the critical
quantities without importing the analysis script.

Python requirements:

```text
numpy
pandas
openpyxl
```

The `data/` cache is intentionally ignored by Git because it can be recreated
from the checksum-locked public archive.

## T318 Jupiter–Sun repetition

`T318_JUPITER_GALACTIC_ORBIT_7_5_15_REPORT_2026-07-31.md` repeats the exact
T309 construction with the Jupiter-system barycentre relative to the Sun in
place of Earth. The target remained frozen at `7.5° : 15°`; the
calibration-only Jupiter period was `4332.513 days`, and evaluation used 1950
onward. The rounded T309 frame produced median/maximum branch angles
`3.053°/3.406°` and median/maximum apertures `6.101°/6.493°`. The modern
measured frame produced `2.844°/3.145°` and `5.671°/6.004°`.

Both fixed target gates failed in all `12/12` complete cycles; the independent
validator passed `32/32` checks. This rules out a planet-independent
`7.5 : 15` cadence in this construction and supports the narrower
child-speed/parent-speed scaling interpretation.

```powershell
python t318_jupiter_galactic_orbit_7_5_15.py
python validate_t318_jupiter_galactic_orbit_7_5_15.py
```

T318 reuses the checksum-recorded T317 Sun and Jupiter-system-barycentre
cache. The compact cycle table, JSON record, report, figure, protocol and
independent validation remain versionable. The 21,192-row two-frame series
CSV is deterministic and ignored.

## Main files

- `ARA_PHI_EMPIRICAL_CALIBRATION_PROTOCOL_2026-07-30.md` — frozen protocol;
- `T302_PHI_PHYLLOTAXIS_RESULT_2026-07-30.md` — reader-facing result;
- `t302_phi_phyllotaxis.py` — complete reproducer;
- `validate_t302_phi_phyllotaxis.py` — independent validator;
- `T302_PHI_PHYLLOTAXIS_VISUALIZATION.html` — five-panel interactive-free
  visual report;
- `T302_PHI_PHYLLOTAXIS_RESULTS.json` — full numerical record;
- the three CSV files — event, plant and candidate-level audit tables.

Additional calibration and cross-domain records:

- `T333_RECORDED_QUTRIT_RECIPROCAL_RADIAL_BREATHING_REPORT_2026-08-03.md`
  — a frozen test of the T307 reciprocal-golden radial lead on a real
  `53,459,987`-measurement trapped-qutrit record. All four complex ARA
  quadrants and a stable reciprocal radial pair were recovered, and true order
  beat all `500` blockwise nulls. The frozen primary endpoints were
  `0.553331 <-> 1.806922`, however, so Phi won only `3/21` primary cells and
  lost badly to the calibration-fitted reciprocal scale. Two secondary centre
  definitions moved toward `0.5894 <-> 1.699` and preferred Phi among the
  fixed candidates, exposing centre-definition dependence rather than rescuing
  a universal Phi endpoint. Verdict: **NOT SUPPORTED for universal reciprocal
  Phi; strong identity-specific reciprocal-coordinate result**. Independent
  validation passed `14/14` checks.

- `T325_PHI_CIRCLE_TRAIN_PHYLLOTAXIS_REPORT_2026-08-02.md` — the first frozen
  child test of the Phi circle-train detection procedure. On 359 ordered
  Arabidopsis divergence angles, `3/8` was the best isolated child-step rule
  (`6.743°` versus Phi `6.986°`), while exact Phi was the best fixed ordered
  parent carrier (`5.429°` versus `3/8` `10.239°`). Real order beat within-plant
  shuffles (`p=0.0263`), adjacent errors compensated (`C=0.319`), and Phi won
  the fixed Fibonacci-lag profile. Independent validation passed 46/46 checks.
  Verdict: **mixed / partial calibration**, because Phi failed the one-step
  gate and the source is previously opened rather than an external holdout.

- [`T432_persistent_meristem_lineage/T432_RESULT.md`](T432_persistent_meristem_lineage/T432_RESULT.md)
  — frozen whole-parent longitudinal test using raw qDII–CLV3–PIN1–PI
  meristem images. E35 identities developed the candidate-blind lineage
  instrument; E37 identities were untouched transfer targets at `10 h` and
  `14 h`. Across 11 persistent holdout children, `sqrt(2)-1` ranked first
  (`0.477789` parent radii) and exact Phi second (`0.528354`). Exact Phi
  retained ordered-lineage, phase, child-order and PIN1-time structure but
  failed the random-increment control (`p=0.129435`). Verdict: **ordered
  temporal whole-identity structure supported; exact Phi not supported as the
  unique generator**. The E37 radial detector reached its frozen search
  ceiling, so angular rankings are stronger than absolute radial magnitude.

- [`../phi_cross_scale/PHASE_LINEAGE_RESULT_2026-07-31.md`](../phi_cross_scale/PHASE_LINEAGE_RESULT_2026-07-31.md)
  — freezes the clarified ARA-octave meaning of child → parent →
  grandparent and tests the six Fibonacci-type sunflower scale families.
  Across 49 adjacent ratios, Phi had the lowest frozen median error
  (`0.024823`); across 43 flip-aware same-phase two-rung ratios, Phi-squared
  had the lowest frozen median error (`0.046605`). Shuffling scale order
  destroyed both relations (`p=0.000100`), and independent validation passed
  13/13 checks. Because the selected families obey the Fibonacci recurrence
  by definition, this is a successful structural crosswalk/calibration, not
  an independent discovery or universal-Phi test.

- `T303_PHI_THREE_EIGHTHS_STATE_DUALITY_AUDIT_2026-07-30.md` — distinguishes
  local rational closure from a moving larger carrier;
- `T307_EMBEDDED_OCTAVE_CLOSURE_CROSSWALK_REPORT_2026-07-30.md` — compares
  the exact embedded \(1/e\leftrightarrow\phi\) radius/displacement identity
  with Q40C's continuous `7.5 : 15` cadence. It supports a shared
  population-level factor-two closure motif but not a literal equality of
  raw scale ratios or seed-specific pairing.
- `T308_PHI_TEMPORAL_RULER_ORBITAL_PROBE_REPORT_2026-07-31.md` — a frozen
  public-data probe of one specific “Phi is a Time ruler” interpretation
  using JPL Moon/Earth and Earth/Sun vectors. Phi ranked `4/7` on the declared
  distance-normalised reconstruction for both systems. The metric family was
  non-identifying: raw error monotonically preferred smaller multipliers,
  while normalised error monotonically preferred larger multipliers and the
  exploratory sweep ended at its upper boundary. The honest result is that
  this reconstruction does not support Phi and is not a strong test against
  other Phi handover formulations.

- `T309_GALACTIC_ORBIT_7_5_15_REPORT_2026-07-31.md` — an exact
  three-dimensional test of the approximately `7.5° : 15°` orbital
  observation. Adding the public JPL Earth/Sun velocity to NASA's rounded
  `829,000 km/h` Solar-System travel estimate produced a stable yearly crest
  (`12/12` complete evaluation years) at maxima `7.519°` and `14.726°`.
  That result did **not** survive the stronger modern Galactocentric-vector
  control constructed from Sgr A* astrometry, the measured Galactic-centre
  distance and Solar peculiar motion: its maxima were `6.960°` and
  `13.636°`. The controlling conclusion is therefore
  **simplified-frame envelope recurrence; not robust as an orbital
  recovery**. The parent-plus-opposite-children ARA decomposition remains
  geometrically clean and is reported separately from the failed numeric
  landmark claim.

- `T317_SOLAR_SYSTEM_BARYCENTRIC_ARA_REPORT_2026-07-31.md` — the corrected
  Solar-System identity test: Sun Phase A versus the combined planetary-system
  Phase B, followed by the completed Solar-System parent in Galactic
  translation. Across 14,683 JPL Horizons states, all 6 frozen crosswalk gates
  passed and the independent validator passed 66/66 checks. The central
  closure is established barycentric conservation, so the result is a
  successful ARA placement/calibration rather than a discovery. The
  non-forced description retains the planetary child composition, residual
  Other, and shared cadence.

T308 reproduction:

```powershell
python t308_phi_temporal_ruler_orbital_probe.py --fetch
python validate_t308_phi_temporal_ruler_orbital_probe.py
```

The JPL cache lives under the already ignored `data/` directory. T308's
243 MB row-level audit CSV is also ignored and deterministically regenerated;
the compact JSON, report, figure, protocol and independent validation remain
versionable.

T309 reproduction:

```powershell
python t309_galactic_orbit_7_5_15.py
python validate_t309_galactic_orbit_7_5_15.py
```

T309 reuses T308's checksum-recorded JPL Earth/Sun vector cache. Its compact
yearly and sensitivity tables, JSON record, static figure and independent
validation are retained in this folder.

T317 reproduction:

```powershell
python t317_solar_system_barycentric_ara.py --fetch
python validate_t317_solar_system_barycentric_ara.py
```

T317 downloads checksum-recorded JPL Horizons vectors for the Sun and nine
planetary-system barycentres into the ignored `data/t317/` cache. The compact
JSON, composition table, report, figure, protocol and independent validation
remain versionable. The 14,683-row series CSV is deterministic and ignored.

T325 reproduction:

```powershell
python t325_phi_circle_train_phyllotaxis.py
python validate_t325_phi_circle_train_phyllotaxis.py
```

T325 reuses the checksum-locked public Source Data 21 workbook already stored
under the ignored `data/` directory. The protocol, compact CSV/JSON outputs,
technical report and independent validation record remain versionable.

T432's frozen protocol, source manifest, extraction amendment, lineage tables,
candidate scores, controls, validation record and portable report live under
`T432_persistent_meristem_lineage/`. The raw checksum-recorded CZI volumes are
stored in the repository's external data cache rather than committed.

## Evidential boundary

This is calibration/retrodiction. The source paper already identifies the
golden-angle neighbourhood, so the run cannot count as ARA independently
discovering Phi in plants. The assigned `x_B = 2 - x_A` mirror illustrates
the declared ARA symmetry but is not an independently observed second wave.
