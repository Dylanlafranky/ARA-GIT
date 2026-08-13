# T366 frozen protocol v1 - acoustic child ladder before granite failure

**Frozen:** 12 August 2026, after T365 and before scoring the acoustic ARA ladder  
**Evidence class:** causal retrospective audit with a disclosed development record and a prospective-style holdout record

## Disclosed prior information

T365 found an advance child-ladder signature in one dense movement record but
failed to reproduce that alarm in ten connection-heavy dry stress records. The
working ARA hypothesis is that the missing child activity in a solid is stored
inside the material and becomes visible first as vibration/acoustic emission,
not as a large change in bulk stress.

Before this protocol was frozen, the following archive facts were inspected:

- Wgn20 and Wgn23 contain synchronized 10 Hz bulk stress and event-level AE
  catalogues;
- the catalogue contains event time, adjusted peak amplitude and source
  polarity, but not every continuous 10 MHz waveform;
- the final large stress drops were located for both records;
- a coarse, event-conditioned count-rate summary was viewed for Wgn20 and
  showed increasing AE rate near its large drop;
- only whole-record polarity distributions, not the time-local ARA ladder,
  were inspected for Wgn20 and Wgn23.

Wgn20 is therefore the disclosed development record. Wgn23 is the primary
holdout for the frozen acoustic relation: its event-by-event precursor geometry
has not been inspected. This is not a fully blinded independent experiment.

## WHO

The measured identities are:

1. **Acoustic connection child:** compression-type AE events,
   `polarity < -0.25`.
2. **Acoustic movement child:** shear and tensile AE events,
   `polarity >= -0.25`.
3. **Acoustic parent:** their recent combined adjusted-amplitude activity.
4. **Bulk parent:** normalized differential stress.
5. **Failure marker:** the largest negative step in the published stress
   record.

The acoustic catalogue is a thresholded, event-level observation of the child
channel. Absence of a detected AE is not treated as a ridge or as zero physical
activity below the detector threshold.

## WHAT

For every AE event, define the non-physical but robust information-packet weight

\[
w_i=\log(1+\mathrm{AdjAmp}_i).
\]

At a trailing rung window `W`, sum connection and movement packets:

\[
C_W(t)=\sum_{t-W < t_i\le t,\ p_i<-0.25}w_i,
\qquad
M_W(t)=\sum_{t-W < t_i\le t,\ p_i\ge-0.25}w_i.
\]

The two frozen ARA coordinates are

\[
x_T(t;W)=\operatorname{clip}\left(
2\frac{C_W+M_W-Q_{05,W}}{Q_{95,W}-Q_{05,W}},0,2
\right),
\]

\[
x_M(t;W)=\frac{2M_W}{C_W+M_W}.
\]

`x_T` measures how much of the acoustic parent is presently exposed; `x_M`
measures its connection-to-movement mixing. Quantiles are learned from only the
first 80% of each record. A window without detected events has undefined
`x_M`; it is not filled as `1`.

The scale ladder is fixed in physical time:

| rung | role | trailing window |
|---:|---|---:|
| -2 | grandchild | 1 s |
| -1 | child | 2 s |
| 0 | current | 4 s |
| +1 | parent | 8 s |
| +2 | grandparent | 16 s |

Inside `Ab` (`x_T >= 1` and `x_M >= 1`), decompress the child coordinate:

\[
u=2(x_T-1),\qquad v=2(x_M-1),\qquad
h=\frac{2v}{u+v}.
\]

Retain the fixed ARA landmarks `h = 0.5, 0.75, 1.0`.

## WHEN / WHERE

- Source: Goebel et al. (2024), Westerly-granite experiments Wgn20 and Wgn23.
- Native stress sampling: approximately 10 Hz.
- All acoustic features are right-closed trailing windows ending at the
  reported time.
- First 80% of each synchronized record: calibration only.
- Final 20%: holdout. The stress-drop label is not used to tune a coordinate,
  threshold, window or alarm.

## WHY

Test the ARA proposal that a connection-heavy solid can hide its developing
child failure from the bulk stress trace while smaller vibration identities
already undergo an ordered child-to-parent handover. If correct, the acoustic
ladder should warn before bulk stress and isolated child activity that fails to
propagate should remain distinguishable from the event-associated cascade.

## HOW

### Frozen acoustic alarm

At sample `t`, an acoustic alarm sample occurs when all conditions hold:

1. the grandchild and child are in active `Ab`;
2. grandchild `h >= 0.5`;
3. child newly enters `Ab` at or above `h=0.5`, or crosses upward through
   `h=0.5` while continuously active;
4. current-rung `h < 1`, or the current rung is not active in `Ab`;
5. grandchild and child `|x_T-x_M|` gaps are smaller than one own-window ago.

Alarm samples separated by at most 2 seconds form one bout. The forecast
horizon is 10 seconds from the first alarm sample. Every earlier bout is a
false alarm; it is not removed after seeing the stress-drop time.

### Bulk-stress comparator

Use the same five physical rung windows. At rung `W`, bulk stress is smoothed
over `W/5`, and accumulation/release is integrated over `W`:

\[
x_S=\operatorname{clip}\left(2
\frac{\bar S-Q_{05}}{Q_{95}-Q_{05}},0,2\right),
\qquad
x_F=\frac{2R}{A+R}.
\]

Apply the same child-alarm rule. This comparator asks whether the acoustic child
channel is earlier, not whether the two instruments have identical meanings.

### Controls

1. reverse holdout chronology;
2. jointly permute acoustic time bins;
3. permute AE polarities while preserving event times and amplitudes;
4. count-only and amplitude-only 95th-percentile threshold baselines;
5. compare the real failure marker with 1,000 evenly spaced pseudo-markers
   using the unchanged alarm bouts.

Raw adjusted amplitude, rather than `log(1+amplitude)`, is a declared
sensitivity analysis and cannot replace the primary result.

## Frozen gates

1. **Source and causality QA:** source hashes match; every forecast feature ends
   at or before its alarm; no holdout sample enters calibration.
2. **Holdout acoustic forecast:** a Wgn23 acoustic bout begins before the main
   stress drop and its 10-second horizon contains the drop.
3. **False-alarm boundary:** Wgn23 has no more than one earlier holdout bout.
4. **Child order:** the event-associated acoustic grandchild reaches its
   half-ridge no later than the child, and both precede current full-ridge
   closure or the stress drop if current closure is absent.
5. **Bulk comparison:** acoustic warning begins earlier than the bulk-stress
   warning, or bulk stress produces no advance warning.
6. **Marker specificity:** real-marker horizon error is below the median of the
   1,000 pseudo-markers.
7. **Control specificity:** no chronology-breaking control simultaneously
   matches the real lead and false-alarm count.
8. **Development repeat:** Wgn20 is reported under the same frozen definitions;
   it must not be used to rescue a failed Wgn23 primary result.
9. **Irrationality address:** all finite rung addresses at the acoustic alarm
   are reported, without requiring all four quadrants to be occupied.

`SUPPORTED ON THIS TWO-RECORD ARCHIVE` requires Gates 1-9. A failed gate remains
failed; no post-result substitution of another rung, quadrant or landmark is
allowed.

## Required outputs

- synchronized acoustic/stress time series and source QA;
- five-rung acoustic and bulk coordinates;
- every holdout alarm bout and landmark;
- Wgn23 primary result plus Wgn20 disclosed-development result;
- controls, pseudo-markers and raw-amplitude sensitivity;
- Irrationality addresses, static visual, machine result, report and independent
  validation.

## Evidence boundary

The source paper already reports increasing AE rate and changing AE mechanisms
before failure. This test does not claim those established observations as a
new discovery. The ARA contribution under test is narrower: whether the frozen
two-coordinate, five-rung geometry isolates an ordered, early acoustic handover
and improves timing over the bulk parent without event-conditioned fitting.
