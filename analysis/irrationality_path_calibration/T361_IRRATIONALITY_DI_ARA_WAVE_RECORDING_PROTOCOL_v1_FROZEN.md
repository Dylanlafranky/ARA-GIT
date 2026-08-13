# T361 frozen protocol — Irrationality Di-ARA wave recording and recovery

**Frozen:** 12 August 2026, before T361 outcome scoring  
**Source archive:** local byte-identical `T358_SOURCE_DATA.zip`, expected MD5 `abe81a3631481b58977925daf453ede5`  
**Random seed:** none used by the primary recorder

## WHO — the identities being measured

Use the nine coupled records in the published resistance-detuning sweep. Each record contains 80 raw current traces sampled at 200 Hz. Columns 1–40 are visible Parent/Phase-A candidates and columns 41–80 are their correspondingly indexed Child/Phase-B partners. The physical pairs are `(1,41)` through `(40,80)`.

Each matched pair is one directly observed same-tier two-wave system. The 40 child reconstructions are also coarse-grained into one population-level child parent for each record.

**Future relation:** if this pairwise recording works, the same interface can be used where one branch remains observed and a coupled branch becomes missing or inaccessible. The population reconstruction tests whether recovered children can rebuild an adult-scale record.

## WHAT — exact ARA measurements

For each pair:

1. `x_A(t)` is the visible parent's raw current mapped onto its own 0–2 ARA diameter.
2. `x_B(t)` is the child's raw current mapped onto its own 0–2 ARA diameter.
3. `D(t)=(x_A(t),x_B(t))` is the raw-amplitude Di-ARA path.
4. `Q(t)` is one of four direction states from the signs of the next parent and child steps: `++`, `+-`, `--`, `-+`. These are the operational four mixed states; the sign labels are retained beside, rather than substituted for, the framework labels `Ab`, `aB`, `Ba`, `bA`.
5. `z(t)=atan2(x_B-1,x_A-1)/(2*pi) mod 1` is the angular/circumference cut around the shared ridge `(1,1)`.
6. `r(t)=sqrt((x_A-1)^2+(x_B-1)^2)/sqrt(2)` is the retained radial amplitude. It is not discarded when `z(t)` is measured.
7. The unchanged Irrationality path readings are applied to `z(t)`: address reuse/opening `x_P`, ordered-relation residual `x_R`, and closure history `C(H)`.

**Future relation:** `x_A,x_B,Q` say where the two waves are and how they are moving; `x_P,x_R,C(H)` say whether that path reuses relations, remains history-recoverable and returns or coherently misses. Together they are the proposed recording packet for later missing-wave recovery.

## WHEN — chronology and holdout

Discard the first 10 seconds of every raw trace. On each visible-parent channel, register cycles with the frozen T359 raw event rule: arm below `Q35(current)` and register the next upward crossing of `Q65(current)`. Use only complete event-to-event cycles.

Split complete cycles chronologically: the first 60% are the recording prefix and the final 40% are the untouched recovery suffix. Quantile scales and the movement recorder use the prefix only.

Every physical cycle is sampled at 64 equal **time fractions** between its observed boundaries. Raw amplitudes are interpolated at those times. Equal time fractions establish a common reading grid but do not linearize either waveform.

At recovery, the first two child readings of each held-out cycle supply only the child's entry position and initial direction. The remaining 62 child readings are hidden from the recorder until scoring.

**Future relation:** this is a boundary-entry recovery test. It models the practical case where a coupled branch is visible at handover and then becomes hidden while its partner remains observable.

## WHERE — the 0–2 mapping

For each channel, calculate `L=Q05(current)` and `U=Q95(current)` from prefix raw samples only. Define

`x(t)=2*clip((current(t)-L)/(U-L),0,1)`.

The declared orientation is low current `0` to high current `2`. Reversing both identity orientations is geometrically equivalent but is not performed after freezing.

The shared Di-ARA ridge is `(1,1)`. Direction zeros inherit the preceding nonzero direction within a cycle.

## WHY — the question this design answers

T358 used a derivative phase cut that backtracked and failed its clock audit. T359 repaired chronology but mapped every oscillator linearly between events, erasing the raw coupling identity. T361 retains the event boundary while restoring within-cycle amplitude and direction.

The test therefore asks whether the actual two-wave Di-ARA path contains a reusable physical record, not whether a processed phase label sorts regimes better than chance.

## HOW — recorder and reconstruction

### A. Prefix recording

For every prefix transition store the tuple

`(x_A(t), x_B(t), delta x_A(t), Q(t), delta x_B(t))`.

This is a chronological relation table, not a fitted global waveform. The primary decoder selects the nine closest stored relations in `(x_A,x_B,delta x_A)` from the same direction state `Q` and uses their median `delta x_B`. If fewer than nine same-state relations exist, use all available same-state relations; if none exist, use the nearest relation regardless of state and flag the fallback.

### B. Untouched child recovery

For each suffix cycle:

1. reveal the complete visible-parent `x_A` cycle;
2. reveal only the first two child values;
3. infer the current child direction from those two values;
4. retrieve the local recorded `delta x_B` using the current predicted child state, visible parent state, visible parent step and four-state direction;
5. advance the child one reading, clipped to `[0,2]`;
6. repeat through the remaining cycle.

No outcome-dependent refit or cycle-specific correction is allowed.

### C. Exact recovery measurements

Score every held-out cycle with:

- `RMSE_ARA`: root-mean-square child error in 0–2 ARA units;
- `MAE_ARA`: mean absolute child error in 0–2 ARA units;
- `waveform_r`: Pearson correlation of actual and recovered child waveform;
- `direction_agreement`: share of non-flat child steps with matching sign;
- `quadrant_agreement`: share of steps in the same four-state Di-ARA direction quadrant;
- `turn_error`: median nearest turning-point separation divided by 64 readings, with a value of 1 if one path has turns and the other does not;
- `endpoint_error`: absolute child error at the final reading;
- `angular_path_error`: mean circular difference between actual and recovered `z(t)`;
- `radial_path_error`: mean absolute difference between actual and recovered `r(t)`.

For each physical record, also average the time-aligned recovered child coordinates over all available pairs and compare that coarse-grained population child with the actual population child using `parent_RMSE_ARA` and `parent_waveform_r`.

### D. Mechanism controls, not chance controls

1. **Direction-blind recorder:** retrieve from the same prefix relation table without separating the four direction states. This tests whether the Di-ARA quadrant carries recovery information.
2. **Wrong-lineage recorder:** use the next matched pair's prefix recorder in cyclic pair order. This tests whether the stored relation belongs to the measured coupling rather than a generic oscillator shape.
3. **Previous-cycle replay:** replay the final observed prefix child cycle. This is a descriptive recurrence reference, not a chance null.

### E. Frozen interpretation gates

The primary question is supported on this archive only if all are true at the physical-record-median level:

1. **Waveform record:** median `waveform_r >= 0.80` and median `RMSE_ARA <= 0.30` in at least 7/9 coupled records.
2. **Movement record:** median direction and quadrant agreement are both at least `0.75`, median `turn_error <= 0.10`, in at least 7/9 records.
3. **Closure record:** median `endpoint_error <= 0.20` and angular path error `<= 0.15` turns in at least 7/9 records.
4. **Four-state contribution:** the primary recorder improves median RMSE by at least `0.05` ARA units or direction agreement by at least `0.05` over the direction-blind recorder in at least 5/9 records.
5. **Lineage contribution:** the primary recorder improves median RMSE by at least `0.05` or waveform correlation by at least `0.05` over wrong lineage in at least 5/9 records.
6. **Child-to-parent recovery:** population `parent_waveform_r >= 0.90` and `parent_RMSE_ARA <= 0.20` in at least 7/9 records.

Failed gates remain evidence about which claimed recording layer did not transfer. They do not get replaced by classifier accuracy or chance comparison.

## Required artifacts

- claim and frozen protocol with hashes;
- prefix/holdout and source-integrity audit;
- complete cycle and physical-record summaries;
- retained Irrationality readings `x_P,x_R,C(H)`;
- primary, direction-blind, wrong-lineage and recurrence recovery measurements;
- synchronized visuals of raw waves, 0–2 Di-ARA traversal, recovered waves and child-to-parent reconstruction;
- independent validator that does not import the analysis program;
- concise report stating exactly what was and was not recorded.

