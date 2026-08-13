# T376 — event-linked solid-scintillator muon handover

**Date:** 13 August 2026  
**Evidence class:** frozen chronological holdout  
**Individual prediction verdict:** **not supported by this pre-decay cut**  
**Population landmark verdict:** **small unresolved preference for `x = 0.50`**

## Answer first

T376 separated two claims which earlier aggregate work could not separate.

1. The frozen direct-child window at `x = 0.50` contained slightly more
   held-out release events than expected from the calibrated exponential
   lifetime: `1.0389×` expectation. It was the largest of the four frozen
   windows, but its ordinary binomial interval includes the null. This is a
   **hint**, not a confirmed landmark.
2. The two-pole relation in the incoming muon pulse did **not** tell us when
   that individual muon would produce its visible decay daughter. Adding the
   ARA direction and asymmetry to an ordinary total-pulse-size model worsened
   held-out exponential NLL by `0.001836` per event. The run-block 95% interval
   was `-0.003495` to `+0.000167` for `NLL_Q - NLL_ARA`: mostly on the wrong
   side and crossing zero only slightly.

Therefore we can retain the population-level `0.50` placement as unresolved,
but we cannot say that this measurement predicts the release time of a single
muon.

## Identity and medium

This test intentionally returned from the T373–T375 liquid-argon parent to a
connection-heavy solid scintillator. DAQ 6234 uses a thick upper scintillator
viewed from two ends and a lower counter. The upper two pulse readings provide
the pre-decay ARA cut; the lower counter is used as a veto.

Two January files were rejected before extraction because their lower-counter
stream was absent. Including them would have changed the measured detector
identity inside the test. Eight identity-consistent days remained: four early
calibration days and four later holdout days.

## Frozen predictions

| coordinate | frozen interpretation |
|---:|---|
| `0.50` | direct solid child handover |
| `0.75` | one quarter below the ridge in the direction of flow |
| `0.25` | reversed-direction control |
| `1.25` | liquid-parent comparison only |

The exact pre-result protocol hash was
`e355c9eed8052ea4bc3cc62516ff6e2526933933083602bb8fdf424ce3127ffc`.

## Pre-decay ARA measurement

For the two initial pulse ends,

\[
x_\mu=\frac{2q_2}{q_1+q_2},\qquad
s=x_\mu-1,\qquad a=|x_\mu-1|.
\]

`s` preserves direction; `a` preserves the amount of asymmetry. `Q=q1+q2`
was kept as an ordinary pulse-size control. No delayed-pulse field was allowed
into the predictor.

The release-time coordinate used the earlier-run exponential calibration,

\[
x_t(t)=2\left(1-e^{-t/\tau_{cal}}\right),
\]

with fixed landmark half-width `0.125`. Here
`tau_cal = 2.19070 μs` after the frozen 0.300 μs minimum delay.

## Data and holdout results

- 9,975 clustered visible candidates were extracted and retained both initial
  pulse poles.
- 5,224 belonged to calibration days.
- 4,751 belonged to later holdout days.
- A short February run and the following full run share a Julian-day label;
  assignment used each raw file's within-day acquisition span rather than the
  date label alone.

### Scope deviation from the full frozen protocol

The public archive's `lifetimeOut` product enumerates qualified initial/delayed
pairs. It does not expose the full population of initial pulses with an
explicit right-censor flag in the same table. T376 therefore scores **decay
time conditional on a visible qualified daughter**, not the probability that
an arbitrary initial pulse later receives a detected daughter. The negative
individual-timing result remains valid for that narrower question; the full
censor-aware branch of the frozen protocol remains outstanding.

### Individual predictive score

| model | held-out mean exponential NLL | interpretation |
|---|---:|---|
| memoryless | 1.793158 | population lifetime only |
| total pulse `Q` | **1.791357** | strongest tested model |
| `Q + s + a` | 1.793193 | ARA relation added |

The held-out rank correlations were also essentially zero:

\[
\rho(s,t)=-0.00694,\qquad \rho(a,t)=-0.02142.
\]

These results reject the tested shortcut from initial detector-end asymmetry
to later individual decay time. They do not reject every possible child cut;
they identify this cut as the wrong or insufficient one.

### Frozen population windows

| x | meaning | held-out count | fraction | enrichment |
|---:|---|---:|---:|---:|
| 0.50 | direct child | 617 / 4,751 | 12.987% | **1.0389×** |
| 0.75 | quarter below ridge | 569 / 4,751 | 11.976% | 0.9581× |
| 0.25 | reversed flow | 600 / 4,751 | 12.629% | 1.0103× |
| 1.25 | liquid comparison | 599 / 4,751 | 12.608% | 1.0086× |

The direct-child coordinate won the frozen comparison numerically. Its 95%
binomial interval for the window fraction was `12.031%–13.943%`, which contains
the `12.5%` exponential expectation. It is therefore an unresolved small
effect requiring independent replication, not a claimed discovery.

## What this means in ARA language

The earlier aggregate curves could locate where a whole population accumulates
and releases. T376 asked whether the incoming individual's two visible poles
contained enough lower-rung information to say when its handover would occur.
They did not.

That leaves three live explanations:

1. the `0.50` child landmark is only a population coarse-graining;
2. the useful precursor exists in a deeper child relation not measured by two
   photomultiplier ends; or
3. individual muon decay has no measurable precursor of this kind and remains
   memoryless at this boundary.

The data distinguishes those statements rather than flattening them into a
single pass/fail.

## Reproduction

- Frozen protocol:
  `T376_EVENT_LINKED_MUON_HANDOVER_PROTOCOL_2026-08-13.md`
- Reproduction script: `t376_event_linked_handover.py`
- Machine result: `T376_event_linked/results.json`
- Event table: `T376_event_linked/events.csv`
- Saveable visual report:
  `T376_event_linked/T376_EVENT_LINKED_MUON_HANDOVER.html`

The downloaded `.wd` files live under the ignored
`analysis/muon/data/quarknet/t376/` cache and can be reacquired from the public
QuarkNet Cosmic Ray e-Lab.
