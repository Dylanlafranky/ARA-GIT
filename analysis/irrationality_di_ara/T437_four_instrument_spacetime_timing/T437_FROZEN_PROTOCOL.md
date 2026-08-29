# T437 frozen protocol — four ARA timing instruments on SXS:BBH:0305

**Frozen:** 2026-08-27, before the T437 event-time answer key was read.

## Scope and evidence class

This is a one-event, known-answer method calibration using the same waveform-only
identity and parent basin as T435/T436.  It is not population validation and it
cannot establish a universal black-hole timing law.  The common-horizon time is
withheld from the prediction script and is read only by the separate scorer.

## Who / what / when / where / why / how

- **Who:** the SXS:BBH:0305 waveform identity already reconstructed in T435.
- **What:** three previously defined Irrationality Di-ARA instruments — state,
  path/history and dynamic handover — plus one explicitly experimental,
  reverse-facing Rationality reconstruction.
- **When:** state, path/history and dynamic reads use only samples at or before
  their reported time.  Rationality uses samples after the reported time and is
  therefore retrospective.
- **Where:** the frozen late-parent basin from T436:
  `relation_ara <= 1` and reported time no later than the waveform-power maximum.
- **Why:** test whether T436 failed because it used the wrong Irrationality
  instrument, or because a settled event is better localized by reconstructing
  closure from the resolved side.
- **How:** every instrument retains its own 0–2 coordinates.  Coordinates are
  never forced to sum to 2.  The prediction artifact is hashed before scoring.

## Shared waveform identity

Let

\[
z(t)=A(t)e^{i\theta(t)},\qquad A(t)=\sqrt{P(t)},
\]

where `P` is T435 total modal power and `theta` is T435's recovered half-phase
child coordinate.  The T435 relation coordinate is used only to identify the
already-frozen late-parent basin, not as the handover answer.

## Instrument 1 — state Irrationality Di-ARA

At each read time, compare the current radius with the radius one local parent
cycle earlier:

\[
s(t)=\frac{A(t)}{A(t-T_P(t))},\qquad
x_L(t)=\frac{2s(t)}{1+s(t)}.
\]

The phase-orientation coordinate over that same interval is

\[
x_C(t)=1+\frac{\sum_j\sin\Delta\theta_j}
                  {\sum_j|\sin\Delta\theta_j|}.
\]

The state clock is the expansion-to-contraction crossing `x_L: >1 -> <1`
inside the late-parent basin.  If several crossings exist, the crossing with
the greatest local waveform amplitude is selected without access to the
horizon time.  If none exists, the nearest `x_L=1` read is reported as a
fallback and explicitly labelled.

This clock is expected to be closely related to the amplitude crest.  If it is
numerically identical to the power maximum it is a crosswalk, not an
independent timing discovery.

## Instrument 2 — path/history Irrationality Di-ARA

Use past-only 128-sample windows, evaluated every four samples.  On the circular
half-phase path `u=theta/(2*pi) mod 1`:

1. `x_P` is twice the clipped log-log occupied-support slope over 8, 16, 32 and
   64 circular bins.
2. `x_R` is twice the causal local-neighbour prediction loss divided by its
   matched no-history loss, capped at 2.
3. `rho` is the median magnitude of the complex lag relations at lags 1–32.

The declared handover target is the boundary between open and reused address
history while continuation remains determined and coherent:

\[
D_{\rm path}=\sqrt{(x_P-1)^2+x_R^2+(1-\rho)^2}.
\]

The path/history clock is the eligible past-only read minimizing this distance.
Downward `x_P=1` crossings with `x_R<1` are retained as diagnostics, but are not
substituted for the frozen primary clock after scoring.

## Instrument 3 — dynamic Irrationality Di-ARA

The exact T436 waveform-only clock is retained unchanged:

\[
D_{\rm dynamic}=\sqrt{(U-R)^2+(H-1)^2}.
\]

Its T436 timestamp and result are imported rather than refitted.  This prevents
T437 from repairing a failed instrument after seeing the known event.

## Instrument 4 — experimental Rationality reconstruction

For every candidate forward-time anchor `t`, read the next 128 samples in
reverse chronological order.  Apply the same `x_P`, `x_R` and `rho` equations
as the path/history instrument and the same boundary distance:

\[
D_{\rm rational}=\sqrt{(x_P-1)^2+x_R^2+(1-\rho)^2}.
\]

The clock is the eligible anchor minimizing this distance.  It asks where the
settled/reused relation ceases when the completed waveform is traced backward.
It is not defined as `2 - irrationality`, and its use of future support means it
cannot be advertised as a live forecast.

## Frozen controls

- full parent phase in place of the half-phase child path;
- quarter-record chronology roll;
- deterministic global chronology shuffle (`seed=437`);
- one-cycle amplitude chronology roll for the state clock;
- the existing T435 median clock, T436 dynamic clock and waveform-power maximum.

Controls retain the same selection rules and late-parent mask.  A control may
occasionally land near the answer in a single event; that is reported rather
than treated as proof or disproof by itself.

## Scoring

After the prediction artifact is written and hashed, read the T435 scorer's
common-horizon time and report for every clock:

- signed and absolute error in `M`;
- error in T435 local parent cycles;
- improvement or degradation relative to the T435 median clock;
- whether it falls within one local parent cycle.

The report must show coordinate histories, timing landmarks, controls and the
causal/retrospective distinction.  A one-event success remains calibration.
