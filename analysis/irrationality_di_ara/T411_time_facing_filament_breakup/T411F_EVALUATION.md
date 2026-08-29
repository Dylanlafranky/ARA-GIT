# T411F — One-sided child Phase A probability evaluation

## Status

**The universal position-only probability scale is not supported in this
archive.** Phase A position carries a strong development association, but the
association does not transfer across the diagnostic identities.

This was a frozen post-hoc archive diagnostic. S1–S4 had already been inspected
in earlier T411 work; a future positive refinement requires a new identity for
sealed confirmation.

## Exact proposition tested

The visible child Phase A was the frozen T411D coordinate

\[
A_t=x_C(t),
\]

with the unobserved TE-ARA remainder recorded as

\[
B_t^{\rm budget}=2-A_t.
\]

`B_budget` was not treated as an observed second child. The primary question
was whether the probability of the offline T411C parent handover within one
frozen child window rose once `A >= 0.9`, where 0.9 is 90% of one TE-ARA half.

The analysis used every fifth causal frame and event-balanced weights, so each
filament event contributed total weight 1.

## Population

- Development: **41 events**, **3,826 causal snapshots** from S1/S3.
- Diagnostic: **82 events**, **6,974 causal snapshots** from S2/S4.
- Pooled: **123 events**, **10,800 causal snapshots**.

## Primary 0.9 contrast

| Partition | P(handover soon \| A >= .9) | P(handover soon \| A < .9) | Risk difference | Risk ratio |
|---|---:|---:|---:|---:|
| Development S1/S3 | 0.0937 | 0.0158 | +0.0779 | 5.93 |
| Diagnostic S2/S4 | 0.0704 | 0.0911 | -0.0206 | 0.77 |
| Pooled | 0.0770 | 0.0435 | +0.0336 | 1.77 |

The strong development association reverses on the diagnostic identities.

## Transfer and falsification

- Development-calibrated diagnostic Brier score: **0.06885**.
- Constant-development-rate diagnostic Brier score: **0.06690**.
- Relative Brier change: **2.91% worse** than constant.
- Diagnostic weighted ROC AUC: **0.4621**.
- Pooled circular-shift result: observed risk difference **0.03355**,
  shift-null median **0.01681**, shift 95th percentile **0.03626**,
  one-sided **p = 0.0869**.
- Frozen gates: **1/5 passed**.

The pooled association is positive but does not clear the time-locality control,
and the learned development probability scale does not predict the diagnostic
identities better than a constant rate.

## Direction comparator

Restricting the readout to frames where Phase A was increasing produced an
encouraging aggregate:

- development risk ratio **2.92**;
- diagnostic risk ratio **1.53**;
- pooled risk ratio **2.07**.

However, the identity split exposes a Simpson's-paradox risk:

| Identity | Position-only risk difference | Increasing/approaching risk difference |
|---|---:|---:|
| S1, 34 events | +0.0886 | +0.0997 |
| S2, 62 events | -0.0077 | +0.0606 |
| S3, 7 events | -0.3225 | -0.3676 |
| S4, 20 events | -0.1815 | -0.3454 |

The positive aggregate direction result is mainly carried by S1 and S2. It is
not yet a stable cross-identity probability law.

## What the probability shape says

The diagnostic S2/S4 probability curve rises toward the ridge, peaks in the
`0.7–0.9` region, and then declines beyond 0.9. The development curve instead
generally rises across the upper Phase A range. This is real heterogeneity, not
permission to replace the frozen 0.9 threshold with 0.7 after seeing the answer.

Possible explanations that remain open are:

1. identity-dependent distortion or phase orientation;
2. different placement of the operational child cut within the parent branch;
3. the visible child Phase A needs its direction and parent state to become a
   transferable coordinate; or
4. the offline reconstructed parent target does not represent the same local
   handover feature in every fluid identity.

## ARA interpretation boundary

The calculation `2-A` is useful TE-ARA bookkeeping, but it contains no new
independent measurement beyond `A`. It cannot by itself recover the missing
child Phase B or distinguish approach, residence and retreat at the same ARA
position.

The defensible conclusion is therefore:

> Visible child Phase A contains identity-specific temporal information, but
> absolute proximity to or passage beyond 0.9 is not yet a transferable
> probability scale for parent handover.

The next test should freeze a genuinely two-dimensional causal state—Phase A
position plus its direction, with the parent's current side of the ridge as a
possible guard—on balanced development identities and then evaluate it on a
new untouched identity. It must not refit a separate threshold for S1–S4.

## Reproduction

- Protocol: `T411F_PHASE_A_PROBABILITY_PROTOCOL.md`
- Analysis: `t411f_phase_a_probability.py`
- Visual: `results/T411F_phase_a_probability/T411F_PHASE_A_PROBABILITY_VISUAL.png`
- Machine result: `results/T411F_phase_a_probability/T411F_RESULTS.json`
- Snapshot data: `results/T411F_phase_a_probability/T411F_SNAPSHOTS.csv`
- Probability bins: `results/T411F_phase_a_probability/T411F_PROBABILITY_BINS.csv`
- Threshold controls: `results/T411F_phase_a_probability/T411F_THRESHOLD_CONTROLS.csv`
- Shift null: `results/T411F_phase_a_probability/T411F_SHIFT_NULL.csv`
