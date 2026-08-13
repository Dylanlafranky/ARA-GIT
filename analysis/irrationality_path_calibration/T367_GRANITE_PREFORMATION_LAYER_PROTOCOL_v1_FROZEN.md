# T367 frozen protocol v1 - granite pre-formation layer test

**Frozen:** 12 August 2026, after inspecting the T366 source inventory and before calculating T367 coordinates or results  
**Evidence class:** repeated physical-event test with specimen-level development/holdout separation  
**Status at freeze:** `EXACT ENOUGH TO TEST`

## Question

Does the acoustic child relation become more organised while it remains open
before a new acoustic parent burst forms?

In ARA language, the proposed ordering is:

\[
\text{diffuse/open child}
\longrightarrow
\text{open but increasingly determined child layers}
\longrightarrow
\text{parent acoustic burst}.
\]

This protocol tests the observable footprint of that conversion. It does not
treat irrationality as a substance and does not assume that a positive result
identifies a unique physical mechanism.

## WHO

Eight Westerly-granite acoustic-emission catalogues from the T366 source
archive:

- **development specimens:** Wgn19-Wgn22;
- **untouched holdout specimens:** Wgn23-Wgn26.

Within each specimen:

- **connection child:** compression-type AE packets, `polarity < -0.25`;
- **movement child:** shear/tensile AE packets, `polarity >= -0.25`;
- **current acoustic parent:** their combined recent event activity;
- **formation event:** the onset of an isolated large acoustic-parent burst.

Wgn20 and Wgn23 also have published bulk-stress records. Their largest stress
drops are reported as external landmarks only. They do not define the repeated
event population.

## WHAT

Bin every catalogue at 0.25 s. Each detected packet has frozen weight

\[
w_i=\log(1+\mathrm{AdjAmp}_i).
\]

At trailing window \(W\), calculate connection and movement totals \(C_W,M_W\)
and the T366 ARA state coordinates

\[
x_T=\operatorname{clip}\left(2\frac{C_W+M_W-Q_{05,W}}
{Q_{95,W}-Q_{05,W}},0,2\right),
\qquad
x_M=\frac{2M_W}{C_W+M_W}.
\]

All quantiles are learned independently inside each specimen from its first
60% only. Empty windows remain undefined on `x_M`.

The scale ladder is frozen as:

| rung | role | trailing window |
|---:|---|---:|
| -2 | grandchild | 0.5 s |
| -1 | child | 1 s |
| 0 | current | 2 s |
| +1 | parent | 4 s |
| +2 | grandparent | 8 s |

For each rung, unwrap the angular ARA path

\[
z(t)=\frac{1}{2\pi}\arg\big((x_T-1)+i(x_M-1)\big)
\]

inside trailing history windows ending at the scored time. No future event or
parent-burst label enters a coordinate.

### Open-but-determined layer measurements

For every history window, report:

1. **address openness `x_P`:** occupied angular-bin growth across
   \(B\in\{8,16,32,64\}\), mapped to 0-2 as in T348;
2. **stochastic residual `x_R`:** past-half nearest-neighbour successor loss
   divided by a no-history circular-mean loss, mapped to 0-2 as in T348;
3. **history coherence:** mean lag-resultant magnitude over lags 1-64;
4. **layer concentration:** inverse robust circular spread around the densest
   angular layer;
5. **layer count:** occupied peaks in a fixed 24-bin circular histogram, where
   a peak exceeds both neighbours and the uniform expected count by 50%;
6. **narrowing:** the trailing change in layer concentration.

The primary proposed state is `x_P > 1` and `x_R < 1`: open but determined.
The geometry is a gradient; exact pole occupation is not required.

## WHEN AND WHERE

- Bin size: 0.25 s.
- Coordinate histories: 8, 16 and 32 s. Each declared event slice is sampled
  at its midpoint and 0.5 s before that midpoint; this supplies a local
  narrowing direction without allowing dense neighbouring samples from one
  event to dominate the specimen comparison.
- Event exclusion: no candidate onset may lie in the first 60% calibration
  interval or within 32 s of a catalogue boundary.
- Pre-event slices: `[-32,-16]`, `[-16,-8]`, `[-8,-4]`, `[-4,-2]`,
  `[-2,-1]`, and `[-1,0)` seconds.
- Post-event diagnostic slices: `[0,1]`, `[1,2]`, and `[2,4]` seconds.

## FORMATION-EVENT DEFINITION

On development specimens only, form a 2 s trailing parent exposure from total
packet weight. Choose one frozen threshold from `{Q97.5,Q98,Q98.5,Q99}` and
one isolation interval from `{8,16,32}` s. Freeze the lowest quantile and
longest isolation interval that jointly provide at least 48 development events,
with at least three events in every development specimen. This protects the
specimen comparison while acknowledging that some catalogues contain far fewer
large isolated bursts than others. An event is the first upward threshold
crossing; selected onsets must be separated by the frozen isolation interval.

Apply that exact quantile and interval independently to the calibration
distribution of each holdout specimen. No holdout result may alter them.

## PRIMARY PREDICTION

Across holdout events, as time approaches parent-burst onset:

1. child and grandchild `x_R` decrease;
2. child and grandchild layer concentration and lag coherence increase;
3. open-but-determined occupancy increases;
4. these changes begin earlier at the grandchild than at the child, and earlier
   at the child than at the current parent;
5. the last pre-event slice remains distinguishable from the post-event slices.

The crucial direction is **organisation before onset**. Layers that appear only
after time zero are released consequences, not pre-formation support.

## CONTROLS

Every control preserves event count and specimen membership.

1. **Matched quiet windows:** non-overlapping windows drawn from the same
   holdout portion and matched to each event's local parent-exposure decile.
2. **Reversed time:** reverse every event-centred child trajectory.
3. **Shuffled event labels:** circularly shift event onsets within each
   specimen by a fixed-seed random offset of at least 64 s.
4. **Time-preserving surrogate:** circularly shift the movement-child stream
   relative to the connection-child stream, preserving each autocorrelation
   and marginal distribution while breaking their local relation.
5. **Simple parent exposure:** total 2 s acoustic activity without Di-ARA
   geometry.
6. **Simple event rate:** 2 s detected-event count.

## FROZEN SCORING

For every event and quiet control, compress each pre-event slice into its median
feature. The **pre-formation score** is learned on development specimens only
by equal-weight averaging of robustly oriented development features:

- `2 - x_R`;
- layer concentration;
- lag coherence;
- open-but-determined occupancy;
- positive narrowing.

Each feature is median/IQR scaled on development data. A feature whose
development event-minus-quiet median has the wrong sign is retained in the
audit but assigned zero primary weight. No fitted regression, classifier or
holdout-selected weight is allowed.

The alarm threshold is the development quiet-window 95th percentile. Warning
time is the earliest pre-event slice whose score crosses that threshold and
remains above it in the next available slice.

## FROZEN GATES

1. **Source and causality QA:** all hashes recorded; every feature is trailing;
   no holdout event enters calibration.
2. **Holdout event coverage:** the holdout supplies at least 48 isolated parent
   bursts in total, with at least two in every Wgn23-Wgn26 catalogue.
3. **Pre-onset organisation:** pooled paired holdout event-minus-quiet score is
   positive with a specimen-cluster bootstrap 95% interval excluding zero.
4. **Temporal direction:** the median score rises from `[-32,-16]` to `[-1,0)`
   and reversed time does not reproduce that ordered rise.
5. **Child precedence:** median first-warning time is earlier for grandchild or
   child than for the current parent, with the child no later than current.
6. **Not merely released waves:** at least one primary child measure changes
   before zero and the pre-event score is not maximised only after zero.
7. **Relation specificity:** time-preserving child-stream shifts reduce the
   event-minus-quiet effect by at least 25%.
8. **Label specificity:** shifted event labels do not match the real
   event-minus-quiet effect.
9. **Baseline value:** the ARA score exceeds both parent-exposure and event-rate
   baselines in paired event-versus-quiet AUROC on at least three of four
   holdout specimens.
10. **False-warning boundary:** at the frozen alarm threshold, quiet-window
    false positives do not exceed 10% and at least 50% of holdout events receive
    a pre-onset warning.

`SUPPORTED ON THIS GRANITE ARCHIVE` requires Gates 1-10. A failed gate remains
failed. Descriptive bands cannot rescue a failed predictive result.

## REQUIRED OUTPUTS

- specimen and event QA tables;
- event-centred raw feature rows;
- pre/post slice summaries with clustered intervals;
- quiet, reverse, shifted-label and shifted-child controls;
- baseline comparison and frozen gate table;
- one overview figure plus separate event/quiet layer-distribution panels;
- machine-readable results, report and independent validation.

## EVIDENCE BOUNDARY

The catalogues contain thresholded detected AE events, not continuous 10 MHz
waveforms. This test can detect organisation among recorded child events; it
cannot observe quiet sub-threshold motion or prove that an unmeasured
irrational entity existed. A positive result would support a narrower claim:
future acoustic-parent formation is preceded by measurable organisation of the
recorded child relation under a frozen ARA instrument.
