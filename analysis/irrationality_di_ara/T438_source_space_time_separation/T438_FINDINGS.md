# T438 findings — source-side Space/Time separation

## Outcome

**Frozen verdict: NOT SUPPORTED as two empirically distinct components.**

The proposed polar separation was nevertheless informative.  The angular
half-phase step recovered hidden horizon traversal almost perfectly, the radial
waveform step recovered hidden closure strongly, and their combined path
direction retained ordered geometry.  The strict result failed because the
matching components did not separate cleanly from the crossed relations: in
this one monotonic chirp, angular traversal also tracks radial closure.

## Answer first

- waveform Time/Traversal versus hidden angular traversal:
  `rho = 0.999559` — PASS;
- traversal specificity margin over the radial waveform component:
  `0.168411` versus required `0.20` — FAIL;
- waveform Space/Connection versus hidden radial closure:
  `rho = 0.841097` — PASS;
- closure specificity margin over the angular waveform component:
  `-0.148484` versus required `0.20` — FAIL;
- radial/angular path direction versus hidden path direction:
  `rho = 0.635275`, chronology-shuffled `0.015461` — PASS.

Three of five frozen empirical gates passed.

## What “Time” looked like in this cut

The clean operational candidate was not elapsed coordinate time and was not
defined as `2 - Space`.  For the recovered source path

\[
z=Ae^{i\theta},
\]

the exact polar differential separates into radial and angular parts.  T438
therefore measured

\[
\text{Space/Connection step}=\Delta\log A,
\qquad
\text{Time/Traversal step}=\Delta\theta,
\]

where `theta` is the T435 half-phase child axis.  The hidden answer key used
minus the log-change of A–B horizon separation for closure and the angular
change of the A–B horizon axis for traversal.

The angular component is real and accurately recovered, but this event does not
support treating it as an independent scalar Time identity.  All four histories
are strongly maturity-ordered.  The stronger new quantity is the relation
between the radial and angular components:

\[
\beta=\operatorname{atan2}(|\Delta\theta|,|\Delta\log A|).
\]

In ARA terms, the candidate Time information is therefore better described as
the ordered traversal **through the coupled radial/angular relation** than as a
standalone amount.  This is consistent with an Information³ reading: radial
state, angular traversal, and the direction/curvature of their relation are
three distinct pieces of information.

## Timing result

The strongest change in the radial-versus-angular path direction occurred
`+4.852 M` after first common-horizon formation, or `0.4267` local parent
cycles.  The last component crossing occurred at `+4.752 M` (`0.4179` cycles).
Both are closer than the waveform-power crest baseline at `+7.252 M`
(`0.6377` cycles) and much closer than T435's frozen median at `+37.542 M`.

The controls distinguish the two timing ideas:

- strongest path-direction change moved `36.16` cycles early under chronology
  shuffle and `39.36` cycles early under a quarter-record roll;
- last component crossing did not pass the same specificity test because the
  chronology shuffle also landed within one cycle (`0.629` cycles);
- swapping radial and angular labels leaves both symmetric landmarks unchanged.
  They can locate a joint handover but cannot decide which axis deserves the
  physical label Time.

Accordingly, the strongest path-direction change is the useful frozen lead.
It remains a known-answer, one-event calibration rather than a validated clock.

## ARA interpretation

The result does not show two unrelated source waves.  It shows two tightly
coupled components of one source trajectory.  Their separate values are
insufficiently specific, while the way the path turns between them is ordered
and event-local.  The most faithful current ARA reading is:

\[
\text{Connection state}
\;\xleftrightarrow{\text{ordered traversal / path direction}}\;
\text{changed connection state}.
\]

This makes “Time” a time-facing relation or traversal operator in this cut, not
a third substance added to the two black holes and not the complement of a
Space coordinate.

## Scientific boundary

T438 uses one SXS numerical-relativity simulation generated within general
relativity.  T435's horizon answer key had already been opened, so this was not
blind.  The half-phase traversal result is also an expected continuation of
T435's quadrupolar orientation crosswalk.  The new evidence lies in the polar
path relation and its timing-control behaviour, not in rediscovering that
waveform half-phase tracks orbital phase.

## Best next test

Freeze only the strongest radial/angular path-direction-change landmark and run
the unchanged construction across several additional SXS binaries spanning
mass ratio and spin.  Score the offset from first common-horizon formation on
untouched simulations and retain waveform crest as the named baseline.  If the
offset generalizes while shuffle and roll controls remain far away, the
time-facing relation advances from one-event calibration to a reproducible
source clock.  If it does not, the next independent candidate should be a
mode-to-mode phase lag or horizon-shear relation rather than another scalar
relabeling of chirp cadence.

## Files

- `T438_FROZEN_PROTOCOL.md`
- `T438_FREEZE_LOCK.json`
- `t438_source_space_time_separation.py`
- `results/T438_RESULTS.json`
- `results/T438_COMPONENT_HISTORIES.csv`
- `results/T438_SPACE_TIME_PLANE.csv`
- `results/T438_CORRELATION_MATRIX.csv`
- `results/T438_TIMING_CONTROLS.csv`
- `results/T438_SOURCE_SPACE_TIME_AUDIT.png`
- `results/T438_SOURCE_SPACE_TIME_REPORT.html`

