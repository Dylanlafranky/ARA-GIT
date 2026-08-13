# T376 — frozen event-linked muon handover test

**Frozen:** 13 August 2026 (Australia/Brisbane), before acquiring or parsing
the individual decay-event stream and before observing any event-linked
handover result.

## Identity boundary

T376 returns from the T373–T375 liquid-argon parent comparison to a direct
solid-scintillator record of an individual stopped muon and its delayed decay
daughter. The medium therefore changes from liquid argon to a connection-heavy
solid scintillator. The liquid-argon `x_H ≈ 1.25` result is a comparison only;
it is not imported as the solid prediction.

## Who / what / when / where / why / how

- **Who:** an individually linked stopped-muon pulse and its later decay-
  electron/positron pulse in the same solid scintillator; the two neutrinos are
  emitted in that same decay but are not directly detected.
- **What:** whether a pre-decay ARA relation supplies prospective information
  about the later decay/handover time, beyond an ordinary memoryless
  exponential lifetime model.
- **When:** from the initial stopping-muon pulse until the first qualified
  delayed daughter pulse inside the acquisition gate.
- **Where:** event-linked QuarkNet-style solid-scintillator records, selected
  without using the later decay time. A two-ended counter is preferred because
  the two initial pulse views can supply a same-identity asymmetry coordinate.
- **Why:** population cumulative release can locate a descriptive handover but
  cannot tell which individual muon will decay next. T376 asks the harder,
  prospective question.
- **How:** construct candidate ARA coordinates only from information available
  at or before the initial pulse; freeze the schema-specific formula before
  reading the delayed pulse times; split runs chronologically; learn allowed
  nuisance calibration on earlier runs; score untouched later runs against an
  exponential baseline.

## Frozen landmark prediction

The originator's directional prediction is:

1. **Primary solid child-handover landmark:** `x_H = 0.50`.
2. **Directional secondary landmark:** `x_H = 0.75`, because the proposed
   handover is one quarter-rung below the parent ridge while flowing from the
   `0` pole toward `1`: `1 - 0.25 = 0.75`.
3. **Opposite-direction control:** `x_H = 0.25`.
4. **Cross-medium comparison only:** `x_H = 1.25`, the liquid-argon placement
   on the far side of the ridge. It cannot be promoted to the solid prediction
   after seeing the result.

These are not interchangeable descriptions. In particular, “0.25 from the
ridge in the direction of flow” means `0.75`, not `0.25`.

## Data qualification gate

The source passes only if it contains, per candidate event:

1. an initial muon pulse;
2. at least one initial-pulse measurement available before decay;
3. a separately timestamped delayed same-counter daughter pulse or an explicit
   right-censoring indicator;
4. stable run/date identifiers for a chronological split; and
5. enough detector documentation to exclude obvious through-going particles
   and channel swaps.

A catalogue of fitted lifetimes, or a table containing only daughter times,
may be used as a population control but cannot pass the individual-prediction
gate.

## Leakage boundary

The following are forbidden from constructing the predictor:

- delayed-pulse time, width, energy, channel or direction;
- any neutrino-labelled outcome;
- a fit performed on the eventual holdout decay times;
- event acceptance rules that use the answer except for a predeclared physical
  definition of a valid decay pair.

The initial-pulse ARA formula will be appended and hashed after raw-field
qualification, but before delayed times are decoded or scored. This staged
freeze is necessary because the public raw schema is not yet known.

## Schema-specific freeze: QuarkNet DAQ 6234

The qualified detector uses a thick solid scintillator viewed from two ends,
plus a lower veto counter. The raw calibrated pulse stream exposes rising edge,
falling edge and time-over-threshold (ToT) before any delayed daughter is seen.

An **initial candidate** is frozen as a channel-1/channel-2 coincidence within
250 ns, with no lower-veto hit in that gate. Its two pre-decay pole readings are

\[
q_1=\operatorname{ToT}_{1},\qquad q_2=\operatorname{ToT}_{2},
\]

and its directed ARA coordinate is

\[
x_\mu=\frac{2q_2}{q_1+q_2},\qquad
s=x_\mu-1,\qquad a=|x_\mu-1|.
\]

Here `s` preserves which detector end leads, while `a` measures the amount of
same-identity asymmetry without choosing an end. Total initial pulse size
`Q=q1+q2` is retained as a non-ARA nuisance control.

A **visible daughter candidate** is the first later channel-1 or channel-2
pulse cluster from 0.300 us through 20 us after the initial coincidence, with
no lower-veto hit in its 100 ns gate. Two end hits inside that 100 ns gate are
one daughter, not two events. An initial candidate without a qualified visible
daughter is retained as right-censored/undetected; it is not silently deleted.

The time axis is represented after calibration by

\[
x_t(t)=2\left(1-e^{-t/\tau_{\rm cal}}\right),
\]

where `tau_cal` is learned only from earlier calibration runs. Candidate
handover windows have fixed half-width 0.125 on this coordinate, halfway
between the quarter-rung landmarks. No window is moved after holdout scoring.

Two questions are deliberately separated:

1. **Population location:** which frozen window best explains held-out release
   timing: 0.50, 0.75, 0.25 or the liquid-only 1.25 comparison?
2. **Individual advance information:** do `s` and `a`, computed at the incoming
   pulse, improve held-out prediction beyond both a memoryless model and an
   ordinary pulse-size model using `Q` alone?

The ordinary control is therefore not artificially weak. Model 0 has only the
run-aware exponential/detection terms; Model Q may use `log(Q)`; Model ARA may
add `s` and `a` but receives no daughter information. Strong individual support
requires lower proper-score loss than Model Q with a positive run-block
bootstrap interval. A merely descriptive landmark hit is reported separately.

## Frozen comparison and verdict boundary

The primary comparison is prospective chronological holdout performance of:

- **baseline:** a run-aware memoryless exponential decay model;
- **ARA model:** the same baseline plus only the frozen pre-decay ARA relation
  and the frozen landmark alternatives, with `1.25` retained as a labelled
  cross-medium control.

Report survival calibration and proper scoring (held-out log likelihood or
Brier score), not merely event counts near a chosen coordinate. A useful ARA
result requires both:

1. improvement over the exponential baseline on untouched later runs; and
2. localization at a frozen landmark rather than a window selected after the
   result.

The landmark verdict is categorical rather than rewritten as an ordering:
`0.50` supports the direct-child reading; `0.75` supports the directional
quarter-below-ridge/same-rung alternative; `0.25` supports the reversed flow;
and `1.25` indicates that the liquid-parent placement transferred despite the
medium boundary.

If no pre-decay variable improves individual prediction, the result may still
support population-level release geometry, but it does **not** support knowing
when a particular muon will emit its decay neutrinos.
