# T411F — one-sided child Phase A probability scale

## Status

Frozen post-hoc diagnostic protocol. The S1–S4 identities and T411C/T411D
outputs have already been inspected. This test can establish whether the
proposed probability instrument behaves as claimed in this archive, but a new
identity is required for sealed confirmation.

## ARA proposition

The visible child Phase A coordinate is the already-frozen T411D causal child
coordinate

\[
A_t=x_C(t)\in[0,2].
\]

The unobserved remainder of the child's TE-ARA budget is

\[
B_t^{\rm budget}=2-A_t.
\]

This is bookkeeping only. It is not an independently observed child Phase B.

`A = 0.9` is frozen as 90% of one TE-ARA half: the ordinary 0–2 child
coordinate immediately before the 1.0 ridge. The primary hypothesis is:

> The probability of the already-defined parent handover within one child-scale
> window increases once the visible child Phase A reaches or passes 0.9.

## Who / what / when / where / why / how

- **Who:** the same source-qualified S1–S4 filament identities. No medium or
  identity is changed. S1/S3 supply the development probability scale; S2/S4
  are a diagnostic transfer set.
- **What:** the binary outcome is whether the frozen offline T411C parent
  handover occurs within the next one-child-scale window.
- **When:** each causal fifth frame before the target, using the current and
  earlier frames only.
- **Where:** the visible Phase A child of the T411C unresolved-rate branch.
- **Why:** observing both child phases would reveal the state but would not be
  a forecast. The TE-ARA remainder permits a one-sided probability instrument
  without pretending the missing phase was measured.
- **How:** estimate event-balanced empirical handover probabilities over fixed
  Phase A bins and transfer the S1/S3 probabilities unchanged to S2/S4.

## Causal prediction window

For event `i`, let

\[
\Delta_{C,i}=N_{C,i}\,\Delta t_i,
\]

where `N_C` is the already-frozen T411D child-window length and `Δt` is that
event's observed frame spacing. At each eligible time `t < T_i`, define

\[
Y_i(t)=\mathbf 1\{0<T_i-t\le\Delta_{C,i}\}.
\]

Here `T_i` is the offline T411C parent target and is used only to label the
later outcome.

## Fixed probability bins

\[
[0,.3),[.3,.5),[.5,.7),[.7,.9),[.9,1),[1,1.1),
[1.1,1.3),[1.3,1.5),[1.5,1.7),[1.7,2].
\]

All snapshots are weighted so every event contributes total weight 1. The
development-bin probability is applied unchanged to diagnostic snapshots.

## Primary statistic and controls

The primary contrast is

\[
\Delta P_{.9}=P(Y=1\mid A\ge.9)-P(Y=1\mid A<.9).
\]

Report its risk ratio and compare `ΔP_.9` with 1,000 within-event circular
shifts of `A(t)`. Also report:

1. diagnostic weighted Brier score against the development constant-rate
   baseline;
2. diagnostic weighted ROC AUC;
3. the same contrast at fixed control thresholds `.7,.8,1.0,1.1,1.2`;
4. a direction-conditioned comparator using only snapshots for which Phase A
   is approaching/increasing. Direction is not part of the primary claim.

## Frozen decision rule

The probability-scale hypothesis is supported in this archive only if:

1. `ΔP_.9 > 0` in development and diagnostic identities;
2. pooled circular-shift one-sided `p <= .05`;
3. development-calibrated diagnostic Brier score is lower than the constant
   development-rate baseline; and
4. diagnostic AUC is greater than `.50`.

The size and sharpness of the increase remain empirical readouts; no effect
magnitude is fitted into the pass rule.

## Boundaries

- The target is an offline reconstructed parent handover, not a directly
  observed microscopic event.
- Dense frames are autocorrelated. Five-frame sampling and event-balanced
  weights limit domination by long records; circular shifts preserve each
  event's Phase A distribution and autocorrelation.
- A positive result supports a one-sided probabilistic precursor in this
  operational child cut. It does not identify a unique physical Phase B.
