# T358 frozen protocol v1 - detuned physical-oscillator Irrationality Di-ARA

**Orientation:** `x_P: 0 -> 2` finite/reused to open/resolving; `x_R: 0 -> 2` relation-determined to stochastic residual.  
**Frozen:** 12 August 2026, before downloading or scoring the experimental archive  
**Evidence class:** controlled public physical-system transfer  
**Claim packet:** `T358_DETUNED_OSCILLATOR_IRRATIONALITY_DI_ARA_CLAIM_PACKET_v1.md`

## WHO

The public electrochemical-oscillator archive at Zenodo 10.5281/zenodo.15122129. Each record contains 80 current traces sampled at 200 Hz. Electrodes 1-40 form population 1 and electrodes 41-80 form population 2. The primary physical pairs are `(1,41), (2,42), ..., (40,80)`. Pair readings are summarized inside each physical record; they are not counted as independent experiments.

Declared coupled detuning sweep:

| file | delta R (ohm) |
|---|---:|
| `oc091818_28.lvm` | 0 |
| `oc091818_39.lvm` | 50 |
| `oc091818_41.lvm` | 100 |
| `oc091818_42.lvm` | 150 |
| `oc091818_43.lvm` | 170 |
| `oc091818_45.lvm` | 190 |
| `oc091818_46.lvm` | 240 |
| `oc091818_50.lvm` | 290 |
| `oc091818_51.lvm` | 340 |

The published 170-ohm record is the declared closure reference, but this label is used only after the coordinates are scored. The remaining nonzero detunings are candidates, not assumed non-closing cases.

Declared uncoupled controls use `oc032118_4.lvm` (`R_ind=1000 ohm`) and `oc032118_8.lvm` (`R_ind=1150 ohm`). They were acquired with population and global coupling resistances set to zero. Parent traces come from the 1000-ohm record and correspondingly indexed child traces from the 1150-ohm record, aligned by fractional record time. This is the uncoupled, deliberately detuned control.

## WHAT

Apply the unchanged T357 `x_P`, `x_R`, and `C(H)` instrument to every declared oscillator pair. The primary question is whether a coupled detuned child can remain coherent while missing the same parent-cycle return, and whether that geometry contains relation-specific information absent from uncoupled detuned drift.

## WHEN

Use all complete numerical rows in each archived record. Construct phase directly from current and its centred derivative. Detect complete upward rest crossings of the parent oscillator. Read eight equal parent-phase landmarks per cycle and score non-overlapping four-cycle windows (32 child samples), as in T357. No fitted period or outcome-dependent trimming is permitted. If a file contains a textual LabVIEW header, remove only nonnumeric header rows.

## WHERE

For each current trace `I(t)`:

`q = I - median(I)`,

`v = centred finite difference of I with respect to the declared 200-Hz clock`,

`z = arg(q/s_q + i*v/s_v)/(2*pi) mod 1`,

where `s_q` and `s_v` are the trace-level 90th percentiles of absolute nonzero `q` and `v`. Select the global sign that makes the median unwrapped phase increment positive; this uses traversal orientation only, never the coupling or detuning label.

The child is sampled at the physical times of the parent's eight equal phase landmarks. This is a Poincare-style ARA cut, not a Fourier or Hilbert phase.

## WHY

T357 showed that the instrument transferred to physical pendula but its coupled records did not occupy the coherent-nonclosing sector: two were phase locked and one was incoherent. T358 deliberately tests a physical archive in which coupling and frequency mismatch are controlled, while an uncoupled mismatch is also available.

## HOW

### Frozen coordinates

For every 32-sample child window, use the T357 definitions unchanged:

- `x_P`: twice the clipped slope of occupied circular bins at `B={4,8,16,32}`;
- `x_R`: past-only `k=3` nearest-neighbour circular successor loss relative to the training circular-mean successor null;
- `C(H)`: return coherence `rho_h` and signed circular miss `d_h` at lags `1..16`;
- one-parent-cycle lag: `h=8`;
- physical closure: `rho_8 >= 0.80` and `|d_8| <= 0.03` turns;
- coherent non-closure: `rho_8 >= 0.80`, `|d_8| > 0.03`, and at least one coherent return in lags `1..16`;
- orientation: signed circular mean of one-step increments, descriptive except for reversal.

Summarize windows within pair by medians, then summarize the 40 paired electrodes within physical record by medians and interquartile ranges. Frozen gates operate on physical-record summaries.

### Frozen controls

1. **Time shuffle:** fixed-seed permutation within each 32-value child window. Support is unchanged; chronology is destroyed.
2. **Time reverse:** reverse the same child window.
3. **Wrong record:** keep a coupled record's parent schedule but replace its child with the next detuning file in the declared ascending cycle `0 -> 50 -> ... -> 340 -> 0`, aligned by fractional record time.
4. **Uncoupled detuned:** 1000-ohm parent record versus 1150-ohm child record, correspondingly indexed and aligned by fractional record time.

Random seed: `3580812`.

## Frozen gates

1. **Closure referee:** the 170-ohm record has median `x_P < 1`, median `x_R < 1`, `rho_8 >= 0.80`, and `|d_8| <= 0.03`; at least 60% of its 40 pair summaries close.
2. **Coupled coherent non-closure:** at least three of the seven non-reference nonzero detuning records (`50,100,150,190,240,290,340`) have median `x_R < 1.25`, `rho_8 >= 0.80`, `|d_8| > 0.03`, and coherent non-closure in at least 40% of pair summaries.
3. **Chronology:** in at least four of the seven candidate records, shuffling raises median `x_R` by at least `0.25` and lowers median best return coherence by at least `0.15`. Shuffling changes record median `x_P` by at most `0.02` in all nine coupled sweep records.
4. **Coupling specificity:** the median candidate coupled record has `x_R` at least `0.15` below, or best return coherence at least `0.15` above, the uncoupled-detuned control. At least four candidate records must beat the uncoupled control in one of those relation-sensitive directions.
5. **Record lineage:** wrong-record replacement raises `x_R` by at least `0.15` or lowers best return coherence by at least `0.15` in at least four of seven candidate records.
6. **Reversal:** across all nine coupled sweep records, reversal changes median `x_P` by at most `0.02` and best return coherence by at most `0.05`; orientation changes sign within a sum error of `0.02` turns/sample in at least seven records.

The overall verdict is `SUPPORTED [controlled detuned physical transfer]` only if Gates 1-6 all pass. Partial gates remain independently reportable. No descriptive visual may rescue a failed gate.

## Chart contract

One static research figure must show:

1. `x_P`-`x_R` record positions across detuning, with the uncoupled control;
2. child phase strands across successive parent cycles for closure, coherent-miss, and uncoupled examples;
3. one-cycle coherence and signed miss across the detuning sweep;
4. chronological versus shuffle/wrong-record control penalties;
5. pair-level distributions rather than record medians alone;
6. frozen gates and the finite-data boundary.

Axes must expose the ARA `0-2` poles and `1.0` ridge wherever applicable. Conclusions may not rely on colour alone.

## Evidence boundary

Passing T358 would show that the frozen ARA path-history instrument distinguishes specific physical coupled/uncoupled relations in this archive. It would not prove a universal Di-ARA, prove exact mathematical irrationality, or establish that the chosen current-phase construction is unique.
