# T388 — same-event parent/daughter anti-phase identification protocol

**Frozen:** 2026-08-15, before inspecting the paired-pulse ARA comparison  
**Source:** BUAP `MD10000Last.csv` liquid-scintillator double-pulse records  
**Identity ceiling:** Class-D detector proxy; neither neutrino is directly observed

## Question

Is the two-axis return recovered by T387 the opposed half of a muon-to-neutrino
handover, or is it the liquid-scintillator/digitizer response repeating after
each visible energy deposit?

## W5H

**Who:** eligible evaluation-split records containing a chronological stopped-
muon pulse and later charged-daughter pulse in the same waveform.

**What:** compare the oriented state/path ARA loop around the first pulse with
the loop around the second pulse, using the same coordinate construction and
the same physical medium.

**When:** from `-256 ns` through `+512 ns` relative to each pulse minimum, at
the native `8 ns` sample cadence. The primary ARA window is `128 ns`.

**Where:** the recorded liquid-scintillator voltage trace. This is a detector-
response boundary, not a direct internal muon or neutrino measurement.

**Why:** an actual anti-phase identity must be distinguished from an ordinary
out-and-return response caused by the measurement apparatus.

**How:** retain only paired pulses whose comparison windows do not overlap;
calculate the same trailing-window coordinates around both pulses; compare
direct repetition with the full and one-axis ARA reversals; preserve loop
orientation; and inspect the strictly pre-daughter guard separately.

## Frozen ARA orientation

The detector cut is oriented as follows:

- `x_R = 0`: contraction/retention;
- `x_R = 1`: adjacent-window equality ridge;
- `x_R = 2`: expansion/release;
- `x_H = 0`: recurrent/closing path;
- `x_H = 1`: balanced path ridge;
- `x_H = 2`: open traversal.

The four predeclared mappings of first-pulse coordinates into a candidate
second-pulse trace are

\[
\begin{aligned}
M_D(x_R,x_H)&=(x_R,x_H),\\
M_F(x_R,x_H)&=(2-x_R,2-x_H),\\
M_R(x_R,x_H)&=(2-x_R,x_H),\\
M_H(x_R,x_H)&=(x_R,2-x_H).
\end{aligned}
\]

`M_D` is direct detector repetition. `M_F` is full diagonal anti-phase.
`M_R` and `M_H` are the two allowed one-axis reversals.

## Population and exclusions

Use only the previously frozen evaluation split and T385 eligibility rules.
Additionally require:

1. at least two `128 ns` windows before both pulse minima;
2. at least `512 ns` after both minima;
3. the first-pulse `+512 ns` interval ends at least `256 ns` before the second
   minimum, preventing loop overlap;
4. finite coordinates throughout the scored interval.

No pulse amplitude, delay or event outcome may be used to select which ARA
mapping wins.

## Primary scores

For every paired event, calculate equal-weight two-axis RMSE between the
second-pulse trajectory and each mapped first-pulse trajectory. Bootstrap the
paired median difference

\[
\Delta_j=\operatorname{RMSE}(M_j,P_2)-
         \operatorname{RMSE}(M_D,P_2),
\qquad j\in\{F,R,H\}.
\]

A positive `Delta_j` favours direct repetition over that reversal. A negative
value favours the reversal.

Calculate the signed area of each centred `(x_R,x_H)` loop. The fraction of
events with equal loop-orientation signs is retained as an independent shape
check.

## Strict pre-daughter check

The interval ending `128 ns` before the daughter minimum is the non-leaking
guard used by T385. Report its median coordinates and distance from the first-
pulse quiet state. A feature appearing only inside the last `128 ns`, or after
the daughter pulse, is visible handover/response and not advance information.

## Gates

1. **Direct-repeat gate:** `M_D` has the lowest median paired RMSE and every
   reversal-minus-direct bootstrap 95% interval lies above zero.
2. **Full-anti-phase gate:** `M_F` has the lowest median paired RMSE and its
   direct-minus-full bootstrap 95% interval lies above zero.
3. **One-axis gate:** `M_R` or `M_H` satisfies the equivalent condition.
4. **Orientation gate:** direct repetition and full diagonal anti-phase are
   both orientation-preserving maps and must retain the loop sign in more than
   75% of paired events. A proposed one-axis reversal must reverse the loop
   sign in more than 75%. Handedness distinguishes reflection from rotation;
   it cannot by itself distinguish `M_D` from `M_F`.
5. **Advance-handover gate:** an opposed departure must be present outside the
   `128 ns` guard and add held-out information beyond T385's raw detector
   baseline. T388 cannot pass this gate from post-pulse recovery.

If mapping and orientation gates disagree, record the result as mixed rather
than assigning a physical anti-phase.

## Interpretation ceiling

Passing direct repetition identifies the T387 loop primarily as a detector
impulse/recovery cycle. Passing a reversal identifies a same-boundary candidate
anti-phase requiring independent replication. Neither result directly observes
neutrinos. Only a pre-daughter feature outside the frozen guard can support an
advance handover claim.
