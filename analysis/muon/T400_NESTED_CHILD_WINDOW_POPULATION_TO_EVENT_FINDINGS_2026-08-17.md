# T400 — nested delayed-child window: population to event

**Date:** 17 August 2026  
**Frozen protocol:** `T400_NESTED_CHILD_WINDOW_POPULATION_TO_EVENT_PROTOCOL_2026-08-17.md`  
**Protocol SHA-256:** `9a7c0e53988235e0ecc3b52c9c2a224afc3141efaf207654ba61423dc35ed263`  
**Verdict:** **nested child ridge not supported at the frozen mode gate; population-to-event transfer partial**

## Answer first

T400 successfully located an objective delayed-child interval inside the
population parent, expanded that interval to its own ARA `0–2`, froze it, and
applied it to untouched detector-event rows. The **balance** of both views is
near the local `1.0` ridge:

- population weighted mean `1.09251`, median `1.11429`;
- event-candidate weighted mean `1.05075`, median `1.03814`.

The stronger prediction was not supported. The frozen primary population
crest is `0.70631`, just below the predeclared population gate beginning at
`0.75`. The primary event-candidate mode is `1.875`, and only `12/20 = 60%`
of deterministic splits placed their modes inside the broad event ridge
window. Therefore the ridge behaves here as a **balance or centre-of-mass
coordinate**, not as a demonstrated bell-curve maximum.

This test does not identify the birth time of either neutrino from one named
muon.

## Identity and exact ARA cut

- **Parent identity:** fitted prompt plus delayed COHERENT CsI neutrino release.
- **Child identity:** the delayed-dominant release interval nested inside that
  parent.
- **Left boundary `L`:** first post-prompt rate equality, `0.568858 µs`.
- **Delayed crest `M`:** `0.785500 µs`.
- **Right boundary `R`:** first post-crest return to the delayed height at
  `L`, `1.382809 µs`.

On the parent ARA these occur at `0.26832`, `0.50005`, and `0.92449`.
Expanding `[L,R]` to the child's own `0–2` coordinate places the crest at
`0.70631`.

## Population result

The objective window is ordered and contains `33.10%` of the fitted delayed
population. Its delayed-rate curve is mildly asymmetric (weighted skewness
`-0.16948`). Sixteen of seventeen valid registered leave-one-bin-out cuts
placed the crest in the predeclared `0.75–1.25` neighbourhood (`94.12%`). A
circular relative-phase control gave `p_upper = 0.01833`.

Those robustness results show that the alignment is structured, but they do
not overrule the frozen primary crest gate. The primary value remains
`0.70631`, so gate P2 failed.

The saved full T398 population fit gives a non-primary comparison of crest
`0.88996`, mean `1.12271`, and median `1.16033`. This shows that the exact
crest is sensitive to source resolution and fitting scope. The frozen primary
T400 result used the calibration-only released `0.5 µs` timing components;
the full T398 reference used the earlier full fitted source. It is reported as
a diagnostic, not substituted for the primary result.

## Population-to-individual transfer

The primary untouched holdout contained `91` beam-coincident rows inside the
frozen child interval, but only `8.98271` effective delayed-event weights.
That missed the predeclared minimum of `10`.

The weighted event mean and median reproduced the local ridge closely, but the
distribution was not bell-shaped around it:

- eight-bin weighted mode: `1.875`;
- deterministic-split broad-ridge mode rate: `60%`;
- bootstrap broad-ridge mode rate: `19.25%`;
- bootstrap 95% interval for the weighted mean: `[0.93228, 1.17471]`.

Bin-count and kernel-width checks kept the event mode predominantly on the
upper side. The coincident and anti-coincident median membership weights were
identical at the available `0.5 µs` timing resolution, so the negative-control
separation gate also failed.

## Scientific interpretation

The result separates two claims that had been compressed together:

1. **Supported as a construction:** a parent-defined child interval can be
   cut out, expanded to its own ARA `0–2`, frozen, and transferred to event
   rows.
2. **Partially supported:** its population and event-weighted centres lie near
   the local ridge.
3. **Not supported here:** the local ridge is the most populous point of a
   bell-like child distribution.
4. **Not observed:** an individual muon's exact neutrino handover or its two
   separately identified neutral children.

The present archive is therefore useful for locating the population handover
and forming event candidates, but is too coarse and sparse to turn the local
coordinate into an individual neutrino-creation clock.

## Implementation audit and validation

Before final scoring, two implementation mismatches were corrected without
changing the frozen protocol: the negative control was given the same frozen
membership scorer as the coincident rows, and gate I5 was calculated from the
specified medians rather than means. The independent saved-artifact validator
then passed all integrity, arithmetic, hash, coordinate, gate-recalculation,
control, and claim-boundary checks.

## Next decisive data

Use an event-linked source that records, within the same event identity, the
parent muon, a charged-daughter direction or momentum, and neutral-sensitive
timing. The T400 coordinate and gates should be transferred without refitting.
That would test whether the child-centred relation predicts individual release
rather than merely organizing a population mixture.

