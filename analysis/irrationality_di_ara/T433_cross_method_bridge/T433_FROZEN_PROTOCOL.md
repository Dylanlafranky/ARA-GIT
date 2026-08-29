# T433 — Cross-method Irrationality Di-ARA bridge

**Status:** frozen before cross-method bridge scores were calculated  
**Date:** 26 August 2026 (Australia/Brisbane)  
**ARA hypothesis and geometry:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## Relational address

- **Who:** one binary-black-hole event at a time. H1 and L1 remain two
  detector views of that event; they are not the two black holes.
- **What:** test whether independently constructed Irrationality Di-ARA cuts
  expose a reproducible temporal/geometric bridge. Curves are not required to
  match, close, share amplitudes, or use identical ARA orientations.
- **When:** the common available interval from `-0.496 s` to `-0.032 s`
  relative to published event GPS, sampled on a common 4 ms grid.
- **Where:** five events available in every instrument family:
  `GW170104`, `GW170608`, `GW170809`, `GW170814`, and `GW170818`.
- **Why:** different instruments may expose different children, scales, or
  perpendicular faces of the same Irrationality Di-ARA. A bridge means that
  their changes remain relationally linked, not numerically identical.
- **How:** construct one two-coordinate history per method, compare the timing
  of trajectory-speed bursts and turning behaviour, and test same-event pairs
  against wrong-event plus large circular-time-shift controls.

## Instrument families

All input histories were generated in earlier tests and have already been
inspected individually. T433 is therefore a frozen exploratory cross-method
test, not an untouched external confirmation.

1. **T427 direct strain cut** — `M=c1`, `C=c2`.
2. **T428 paired-phase cut** —
   `M=mean(T_A,T_B)`, `C=mean(K_A,K_B)`.
3. **T429 separated cut** — `M=T_A`, `C=S_B`.
4. **T432 dynamic ledger cut** — `M=movement_M`, `C=connection_C`.

T431 is not counted as an independent family because T431 and T432 share the
same core movement/connection construction. Counting both would inflate
cross-method agreement.

**T430 is secondary only.** Its `M_rem` is a cumulative remaining-traversal
budget rather than local movement. It is displayed as phase progress
`M_progress=2-M_rem` beside `C_acc`, but cannot contribute to the primary
multi-method bridge verdict.

## Bridge observables

Each coordinate is smoothed by a centred seven-frame median. No coordinate is
defined as the complement of another.

For each method, calculate:

1. trajectory speed
   `v(t)=sqrt((dM/dt)^2+(dC/dt)^2)`, converted to its within-event rank so
   method-specific amplitude scales do not determine the result;
2. standardized derivative direction in the `(M,C)` plane;
3. distance to the ARA ridge point `(1,1)`;
4. high-movement landmarks: the top 20% of ranked trajectory-speed samples.

For every method pair and event, search lags from `-64 ms` to `+64 ms` in 4 ms
steps and retain:

- maximum Spearman association between the two speed histories;
- lag of that maximum;
- Dice overlap of high-movement landmarks at that lag;
- median derivative-vector cosine at that lag: positive = similarly oriented,
  negative = oppositely oriented, near zero = perpendicular/mixed;
- separation between each method's closest approach to `(1,1)`.

The speed and landmark measures are orientation-invariant bridge tests. The
cosine and ridge timing are descriptive and cannot rescue a failed bridge.

## Controls

For each method pair use seed `43320260826` and 2,000 null replicates. Each
replicate:

1. deranges the five event identities for the second method, ensuring no
   same-event pair remains;
2. circularly shifts each second-method history by at least 128 ms before the
   same +/-64 ms lag search;
3. recomputes the median association and landmark overlap across five events.

This tests whether the bridge requires both the correct event identity and the
correct temporal neighbourhood. It does not establish causal direction.

## Frozen primary gate

For the six pairs among T427, T428, T429, and T432:

- calculate one-sided empirical p-values for median speed association and
  median landmark overlap;
- control each p-value family with Benjamini-Hochberg FDR across six pairs;
- a pair supports a bridge only when both FDR-adjusted q-values are `<=0.05`.

A broad cross-method Irrationality Di-ARA bridge is supported when at least
three of the six independent method pairs pass. Fewer passing pairs imply a
partial or method-specific bridge.

T430 comparisons are secondary and reported without contributing to this
gate.

## Interpretation boundary

A pass would show that different ARA cuts retain common event-specific timing
or transition structure. It would not show that the coordinate values are the
same physical quantity, identify literal internal black-hole children, prove a
singularity flip, or establish causal information transfer. Because all cuts
come from the same detector strain, a bridge may reflect common astrophysical
signal morphology; the ARA contribution is the reproducible relational
organization across deliberately different projections.

