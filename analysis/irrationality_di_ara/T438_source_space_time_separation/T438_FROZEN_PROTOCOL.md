# T438 — source-side Space/Time separation after binary inversion

Status before scoring: **FROZEN GEOMETRIC CALIBRATION**

## Question

After T435 recovered the two-hole axis and shared closing relation from the
combined SXS waveform, can that same source path be separated into a radial
Space/Connection component and an angular Time/Traversal component without
defining either as the complement of the other?  Does each waveform-only
component preferentially recover the matching component of the hidden
individual-horizon motion?

This is a one-simulation, known-answer method calibration.  The T435 horizon
answer key has already been opened in earlier work, so T438 is not blind and
cannot establish a universal law.

## Who / what / when / where / why / how

- **Who:** the already-recovered unordered black-hole pair `B1/B2`, its
  waveform parent `P`, and the hidden SXS horizon pair `A/B` used only for
  scoring.
- **What:** decompose one ordered complex source path into radial change and
  angular traversal, then compare those components with radial closure and
  angular traversal of the hidden horizon pair.
- **When:** the common T435 inspiral support ending at first common-horizon
  formation.  The post-common-horizon waveform is retained only for the three
  frozen timing diagnostics.
- **Where:** SXS:BBH:0305, Lev6.  The waveform-only inputs are the sealed T435
  prediction arrays.  The T435 scored horizon arrays are the answer key.
- **Why:** T435 recovered identity orientation and shared closure but not the
  missing handover timing.  T438 tests whether the missing independent relation
  is the orthogonal traversal component rather than another closure measure.
- **How:** use the polar differential of the recovered half-phase source path.
  No coordinate is defined as `2 -` the other, and no horizon time or position
  enters the waveform construction.

## Declared ARA orientation

For this test only:

- **Space/Connection:** inward radial accumulation/closure.
- **Time/Traversal:** angular movement around the recovered pair relation.

Reversing both labels would not alter the relational geometry, but the declared
orientation is retained throughout the report.

## Waveform-only construction

Let

\[
z(n)=A(n)e^{i\theta(n)},
\]

where `A=sqrt(total modal power)` and `theta=phase(h22)/2` are already sealed in
T435.  The sample index `n` supplies order only; it is not used as the definition
of Time.

The exact polar differential is

\[
e^{-i\theta}\Delta z
\simeq
\Delta A+iA\Delta\theta.
\]

To compare scale-free components, freeze

\[
c_P=\Delta\log A,
\qquad
t_P=\Delta\theta.
\]

`c_P` is the signed radial/connection step.  `t_P` is the signed angular
traversal step.  The corresponding state coordinates are independently ranked
onto `[0,2]`; they are not required or expected to sum to two.

The waveform path-direction angle is

\[
\beta_P=\operatorname{atan2}(|t_P|,|c_P|).
\]

This distinguishes a radial state change from movement around the state without
assuming a fixed physical conversion factor between them.

## Hidden answer-key construction

From the individual horizon centers, define

\[
q(n)=x_B(n)-x_A(n)=R(n)e^{i\alpha(n)}
\]

in the dominant orbital plane.  Freeze the matching hidden components

\[
c_H=-\Delta\log R,
\qquad
t_H=\Delta\alpha,
\qquad
\beta_H=\operatorname{atan2}(|t_H|,|c_H|).
\]

The minus sign makes inward radial closure positive.  Only constant orientation,
global handedness and A/B label symmetries allowed by T435 may be removed.  No
time-varying alignment is allowed.

## Frozen primary metrics

All correlations are Spearman correlations on the common inspiral support after
the fixed T435 Savitzky–Golay smoothing window is applied to differential
histories.

1. **Traversal recovery:** `rho(t_P, t_H) >= 0.80` after the already-allowed
   single global handedness choice.
2. **Traversal specificity:** `rho(t_P,t_H) - |rho(c_P,t_H)| >= 0.20`.
3. **Closure recovery:** `rho(c_P,c_H) >= 0.50`.
4. **Closure specificity:** `rho(c_P,c_H) - |rho(t_P,c_H)| >= 0.20`.
5. **Path-direction recovery:** `rho(beta_P,beta_H) >= 0.50` and at least `0.20`
   above the chronology-shuffled control.

The Space/Time split is **SUPPORTED** only if all five gates pass; **PARTIAL**
if traversal recovery/specificity pass but either closure or path-direction
recovery fails; otherwise **NOT SUPPORTED**.  Exact symmetry checks are reported
separately and cannot rescue an empirical gate.

## Frozen controls

- deterministic chronology shuffle (`seed=438`), applied to ordered increments;
- one-quarter-record circular roll;
- radial/traversal label swap;
- global phase rotation by `pi/3`;
- unordered hole-label swap;
- complete chronology reversal, which must reverse the signs of both ordered
  components while preserving their magnitudes after reversing them back onto
  the original sample order.

## Frozen timing diagnostics

These are diagnostics, not primary pass/fail gates because the common-horizon
answer is already known from T435.  Inside the T435 late-parent basin
`relation_ara <= 1` and no later than the waveform-power maximum, report three
independently predeclared waveform-only landmarks:

1. the strongest change in `beta_P`;
2. the last crossing of independently ranked connection and traversal state;
3. the minimum Euclidean distance to their joint ARA ridge `(1,1)`.

Each is scored against first common-horizon formation in `M` and T435 local
parent cycles.  None may be selected after scoring as “the” clock.

## Evidence boundary

A pass would identify a source-side operational Time/Traversal component of this
one numerical-relativity waveform and show that it matches the orthogonal
horizon motion better than the radial component does.  It would remain a
crosswalk inside a GR simulation, not proof that traversal is physical Time or
that ARA generates spacetime.  A failure would reject this polar differential
as the missing Space/Time separator while leaving T435's binary inversion
unchanged.
