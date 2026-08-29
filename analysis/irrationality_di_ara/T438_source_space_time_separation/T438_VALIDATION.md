# T438 validation record

## Validation outcome

The protocol freeze, calculation pipeline, controls, static visual and portable
report reproduce.  The correct frozen verdict is **NOT SUPPORTED as two
empirically distinct components**, with a promising non-gated joint-path timing
lead.

## Freeze and provenance

- Protocol SHA-256:
  `ec43cc857c91dc5bda3d8cdb3342e0b7a36c1bc966d9955980fc5848409d9201`.
- The runtime verified that hash against `T438_FREEZE_LOCK.json` before scoring.
- Waveform-only features came from the sealed T435 prediction arrays.
- Individual horizon positions and first common-horizon time came from the T435
  scored arrays and were used only as the known answer key.
- The report labels the test non-blind because the answer key had been opened in
  the preceding T435–T437 work.

## Reproduced primary metrics

- traversal recovery rho: `0.9995589385`;
- connection-on-traversal rho: `0.8311474960`;
- traversal specificity margin: `0.1684114426`;
- closure recovery rho: `0.8410972178`;
- traversal-on-closure rho: `0.9895816222`;
- closure specificity margin: `-0.1484844044`;
- path-direction rho: `0.6352752969`;
- shuffled path-direction rho: `0.0154607028`;
- quarter-roll path-direction rho: `-0.3755795628`.

The traversal-recovery, closure-recovery and path-direction gates pass.  Both
specificity gates fail, so the overall frozen result cannot be promoted to
PARTIAL under the predeclared rule.

## Reproduced timing diagnostics

- strongest path-direction change: `+4.852043 M`, `0.426702` cycles;
- last connection/traversal crossing: `+4.752055 M`, `0.417909` cycles;
- nearest joint ridge: `-292.853848 M`, `25.754362` cycles;
- waveform-power crest baseline: `+7.251742 M`, `0.637738` cycles;
- T435 frozen median baseline: `+37.542193 M`, `3.301562` cycles.

For strongest path-direction change, chronology shuffle scored `36.1584` cycles
and quarter-record roll scored `39.3583` cycles.  The shuffled last-crossing
control scored `0.6289` cycles, so the crossing alone is not event-specific.

## Symmetry and implementation checks

- global phase rotation error: `7.86e-16`;
- hole-label swap traversal error: `1.51e-15`;
- chronology-reversal radial odd-parity median error: `0`;
- chronology-reversal angular odd-parity median error: `0`.

The analysis script compiles under Python 3.12 and reruns deterministically with
the archived dependencies.  All exported CSV and JSON rows were regenerated
from the same source arrays.

## Visual and report QA

`results/T438_SOURCE_SPACE_TIME_AUDIT.png` was rendered and inspected.  Titles,
0–2 axes, component labels, common-horizon reference, correlation matrix,
Space/Time plane, controls and timing units are visible.

The canonical Data Analytics artifact passed schema validation and portable
packaging.  Structural verification passed with 20 blocks, four charts, one
metric strip and four rendered tables.  Browser-level interaction and responsive
QA did not run because no compatible local Chromium executable was available;
the self-contained report retains the semantic fallback tables and charts.

## Interpretation boundary

High diagonal correlations do not establish independent Space and Time
identities because the crossed correlations are also high.  The path-direction
result survives ordered controls and is the strongest new diagnostic, but it is
one known-answer simulation.  No claim of a universal clock, physical Time
substance or ARA generation of spacetime is supported by T438 alone.
