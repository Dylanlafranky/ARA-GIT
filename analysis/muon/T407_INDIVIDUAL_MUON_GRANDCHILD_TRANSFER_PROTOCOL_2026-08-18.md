# T407 — individual-muon grandchild transfer protocol

**Frozen:** 18 August 2026, before T407 model fitting or scoring  
**Status:** registered retrospective external-record transfer  
**Source:** public QuarkNet DAQ-6845 event-linked stopped-muon records already
reduced and audited in T379

## Question

Does a pre-decay ARA relation near the independently proposed grandchild
completion (`0.75`, with `0.706306` as the observed displaced comparison)
carry advance information about the later charged-daughter delay of the same
individual stopped-muon event?

This is an individual-muon test because each row links one incoming candidate
to one later daughter pulse cluster. It is not direct neutrino timing and is
not spin-resolved.

## Who / what / when / where / why / how

- **Who:** 2,396 calibration and 2,109 untouched T379 holdout stopped-muon
  candidates, split by acquisition run before this test.
- **What:** the incoming event coordinate `x_mu = 2B/(A+B)` formed only from
  the prompt upper/lower counter relation, compared with that event's later
  charged-daughter delay.
- **When:** prompt measurement at the incoming muon, followed by the linked
  daughter `0.30–10.0 microseconds` later.
- **Where:** the primary pure completion band `0.75±0.05`; the secondary
  displaced band `0.706306±0.05`.
- **Why:** test whether the population-derived grandchild landmark transfers
  to advance information at individual-event grain in an independent detector
  archive.
- **How:** fit calibration-only truncated exponential-plus-background timing
  models, freeze all coefficients, then score the two holdout runs by
  individual-event log loss and chronological-block bootstrap.

## Models

- **Ordinary model `MG`:** prompt total strength, prompt multiplicity and
  detector-depth centroid.
- **Pure-grandchild model `M075`:** `MG` plus an indicator for
  `|x_mu-0.75| <= 0.05`.
- **Observed-child model `M0706`:** `MG` plus an indicator for
  `|x_mu-0.7063064837| <= 0.05`.
- **Controls:** the same model with centres `0.50`, `1.00`, `1.25` and `1.50`.

No daughter amplitude, daughter channel, daughter delay, holdout statistic or
neutrino label enters a predictor.

## Gates

For each proposed band:

1. Calibration direction is higher handover hazard / earlier daughter arrival.
2. `NLL(MG)-NLL(Mcandidate)` is positive in both holdout runs.
3. Chronological-block bootstrap 95% interval for the holdout NLL improvement
   is strictly above zero.
4. The candidate beats the ordinary model after within-run permutation of the
   delays no more often than expected from the observed improvement.

The primary `0.75` claim is supported only if gates 1–3 pass. The `0.706306`
comparison may show that the child-scale displacement is more informative, but
it does not replace the frozen pure endpoint after inspection.

## Event-level boundary

Even a supported result predicts a change in an individual event's timing
distribution, not an exact deterministic decay timestamp. The detector sees
the charged daughter; it does not separately observe the two neutrinos.

