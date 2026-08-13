# T365 frozen protocol v1 — fault-tension scale-ladder forecast

**Frozen:** 12 August 2026, after T364 and before scoring any additional tension scale  
**Evidence class:** causal retrospective forecasting audit on an already opened archive

## Disclosed prior information

T364 established post hoc that the existing `(10,50)`-bin stored/release cut
crosses the ridge of its active `Ab` child approximately 2 ms after dense
displacement slip and within ±10 source rows of all 15 stress drops. The dense
child entered its half-ridge approach roughly 8 ms before slip. The hypothesis
that smaller tension children move first has not yet been scored.

This is not an untouched physical confirmation. The purpose is to determine
whether the proposed scale ordering has causal forecast content worth carrying
unchanged to a second archive.

## WHO

Five causally measured tension identities form an octave-like scale ladder.
Relative to the T364 current rung `(smooth,transfer)=(10,50)` bins:

| rung | role | smoothing bins | transfer bins |
|---:|---|---:|---:|
| -2 | grandchild | 3 | 13 |
| -1 | child | 5 | 25 |
| 0 | current T364 identity | 10 | 50 |
| +1 | parent | 20 | 100 |
| +2 | grandparent | 40 | 200 |

Integer rounding is declared explicitly where exact halving is impossible.
Every reading is trailing/past-only.

## WHAT

For each rung, preserve the T363 definitions:

\[
x_S=\operatorname{clip}\left(
2\frac{\bar S-Q_{05}}{Q_{95}-Q_{05}},0,2
\right),
\]

\[
x_F=\frac{2R}{A+R}.
\]

Dense robust scales are learned independently for each rung from its causally
smoothed first 80%; the slip-containing final 20% is untouched holdout.
Replication robust scales are learned once per medium and rung from the
complete published medium record, never per event.

Inside an active parent `Ab` branch (`x_S>=1,x_F>=1`), decompress:

\[
u=2(x_S-1),\qquad v=2(x_F-1),
\qquad
h=\frac{2v}{u+v}.
\]

Retain upward crossings of the fixed ARA landmarks:

\[
h\in\{0.5,0.75,1.0\}.
\]

## Primary online alarm

At time `t`, an alarm sample occurs when all are true:

1. grandchild `h[-2] >= 0.5`;
2. child `h[-1]` crosses upward through `0.5` at `t`;
3. both are inside their active `Ab` branches;
4. current-rung `h[0] < 1`, or the current rung has not yet entered `Ab`;
5. the grandchild and child storage–release gaps have each decreased over their
   own smoothing width.

Alarm samples separated by no more than 50 dense bins (0.10 s), or 101
replication source rows, belong to one alarm bout. An operational forecast is
the first sample of a bout. The slip label is not used to create, merge or
select bouts.

## WHEN / WHERE

- Dense Event 101: first 80% is calibration; final 20% is prospective-style
  holdout. Displacement supplies the independent slip time.
- Replication: the same 10 dry and 5 fluid stress-drop windows used by T363/364.
  They test scale order and event-local repeatability, but cannot independently
  establish advance prediction because the event markers are stress-derived.

## WHY

Test the user's proposed direction:

> Smaller children of stored tension should begin the closing/release handover
> before the current identity and its parents. Their ordered propagation may
> provide advance warning, while the Irrationality Di-ARA identifies the branch
> used by that identity.

## HOW / CONTROLS

1. Run all five fixed rungs without event-conditioned tuning.
2. Report every landmark crossing and every alarm bout in holdout.
3. Score the first alarm bout whose fixed 0.10 s horizon contains dense slip;
   count every earlier bout as a false alarm. If no bout contains slip, the
   primary forecast fails.
4. Compare real dense slip with 1,000 evenly spaced pseudo-markers and the
   quarter/half/three-quarter shifted markers using the unchanged alarm bouts.
5. Repeat scale timing in all 15 events. Report, do not hide, reversals of the
   expected child→current→parent order.
6. At the dense alarm, calculate causal path/history `(x_P,x_R,C(H))` separately
   at each rung using history widths `64,128,256,512,1024` samples. These label
   the Irrationality branch; no multi-quadrant occupancy requirement exists.
7. Controls: reverse chronology, jointly permuted chronology, and single current
   rung. Controls preserve values as far as applicable but break scale order or
   remove the children.

## Frozen gates

1. **Causality QA:** every dense forecast feature ends at or before its reported
   alarm time; calibration uses no holdout sample.
2. **Primary dense forecast:** at least one alarm bout begins before slip and
   contains slip inside its fixed 0.10 s horizon.
3. **Dense false-alarm boundary:** no more than one earlier holdout alarm bout.
4. **Dense child ordering:** the grandchild half-ridge crossing precedes the
   child half-ridge crossing, which precedes the current full-ridge crossing in
   the event-associated bout.
5. **Marker specificity:** real slip timing error to the forecast horizon is
   smaller than the median of 1,000 pseudo-markers and all shifted markers.
6. **Repeated scale ordering:** at least 12/15 replication events place the
   grandchild half-ridge no later than the current full ridge, and at least
   12/15 produce a primary alarm bout whose horizon contains the stress drop.
7. **Irrationality address:** all five dense rung histories return finite
   `(x_P,x_R,C(H))` at the alarm, and their quadrant/child address is reported.

`SUPPORTED AS A CAUSAL FORECAST SIGNATURE ON THIS ARCHIVE` requires Gates 1–7.
Failure is retained without substituting a different landmark or rung.

## Required outputs

- five-rung dense time series;
- all landmark crossings and alarm bouts;
- lead time and false-alarm table;
- 15-event scale-order table;
- causal Irrationality address at alarm;
- controls, frozen gates, figure, machine result and independent validation.

## Evidence boundary

Even a full pass is a causal retrospective forecasting signature, not an
independent earthquake predictor. The archive and base event geometry were
already opened. A second synchronized stress/movement archive must receive this
protocol unchanged before event labels are inspected.

