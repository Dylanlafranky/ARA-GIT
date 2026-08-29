# T400 — nested child window: population to event protocol

**Frozen:** 17 August 2026, before execution  
**Status:** registered exploratory/confirmatory bridge  
**Parent identity:** fitted prompt plus delayed COHERENT CsI neutrino release  
**Child identity:** the delayed-dominant release window nested inside that parent  

## Question

Does the delayed-neutrino branch, when cut from the parent and rescaled to its
own `0–2` ARA coordinate, place its densest population near the local `1.0`
ridge? If it does, does the same frozen child coordinate organize untouched
unbinned detector events without refitting the window to those events?

This is deliberately a population-to-event test. It is **not** a claim that the
archive identifies both neutrinos from one named muon.

## Who / what / when / where / why / how

- **Who:** the official unbinned COHERENT 2022 CsI beam-coincident and
  anti-coincident events, plus the official prompt and delayed source
  templates already qualified in T371/T398.
- **What:** a delayed-child window defined by population structure, then a
  deterministic calibration-to-holdout transfer to individual detector-event
  records.
- **When:** recoil times from `0` to `6 microseconds` after the SNS pulse.
- **Where:** first on the parent cumulative ARA coordinate, then on a local
  child coordinate obtained by expanding the selected parent interval to
  `0–2`.
- **Why:** to test the proposed rule that a child can be located coarsely from
  its parent, then becomes clearer when measured at its own scale.
- **How:** objective rate crossings define the child boundaries; the child
  window is frozen on calibration events and applied unchanged to holdout
  events.

## Population child-window construction

Let `P(t)` and `D(t)` be the calibration-fitted prompt and delayed rates. The
left child boundary `L` is the first proper post-prompt crossing

\[
P(L)=D(L).
\]

Let `M` be the delayed-rate maximum. The right boundary `R` is the first point
after `M` at which the delayed rate returns to its left-boundary height:

\[
D(R)=D(L),\qquad L<M<R.
\]

Let the parent cumulative coordinate be

\[
x_P(t)=2\frac{\int_0^t(P+D)\,dt}{\int_0^{6\mu s}(P+D)\,dt}.
\]

The nested child coordinate is the parent-ARA cut expanded to its own scale:

\[
x_C(t)=2\frac{x_P(t)-x_P(L)}{x_P(R)-x_P(L)},
\qquad L\le t\le R.
\]

This definition does **not** force the crest to equal `1`. The test observes
where `x_C(M)` lands.

## Population gates

1. `L < M < R`, with finite strictly ordered parent coordinates.
2. The delayed crest lands in the predeclared broad ridge neighbourhood
   `0.75 <= x_C(M) <= 1.25`.
3. At least `80%` of valid registered T399 leave-one-bin-out yield cuts place
   the crest in that same neighbourhood.
4. A circular relative-phase control is reported. It is not permitted to
   redefine the window or the ridge gate after inspection.

The distribution may be asymmetric. A Gaussian is only a comparator; failure
of Gaussian symmetry does not by itself falsify a local ridge.

## Population-to-event transfer

The unbinned beam-coincident and anti-coincident records are split
deterministically `70/30`. Only calibration events fit the five-component
population model and define `L`, `R`, `x_P` and `x_C`.

Every untouched holdout event inside `[L,R]` receives:

1. its frozen local coordinate `x_C` from its measured recoil time;
2. a delayed-branch membership weight from the calibration-only mixture model;
3. no new fitted boundary, ridge or timing parameter.

The primary split is supplemented by 20 deterministic split salts.

## Event-transfer gates

1. The primary holdout contains at least `10` effective delayed-event weights
   in the frozen child window.
2. The weighted holdout mode lies in `0.50 <= x_C <= 1.50`.
3. The weighted holdout mean is within `0.30` ARA units of the frozen
   population child mean.
4. At least `70%` of valid repeated splits put the weighted holdout mode in
   `0.50 <= x_C <= 1.50`.
5. The median delayed-membership weight is higher for beam-coincident than for
   anti-coincident holdout events inside the same window.

The broad event gate is wider than the population gate because the source has
only about 1,578 beam-coincident events over the full six-microsecond record.

## Controls and boundaries

- Anti-coincident events provide an observed background control.
- Circular shifts test relative alignment at the population stage.
- Registered leave-one-bin-out yields test sensitivity to the fitted parent
  asymmetry.
- Event weights are statistical branch assignments, not flavor tags.
- Passing the event-transfer gates means the population child coordinate
  organizes individual detector-event candidates. It does not reveal an
  individual neutrino birth or link a specific muon to its two neutrinos.
- Failing the event-transfer gates means the present archive is too sparse or
  the population-defined child window does not survive at event grain; it does
  not erase the already established population waveform.

