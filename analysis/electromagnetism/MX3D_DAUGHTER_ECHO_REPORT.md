# MX3d parent-collision to daughter identity result

**Tier:** DEVELOPMENT / ALREADY INSPECTED / SINGLE NOISE REALISATION  
**Parent:** k=5  
**Primary daughter candidate:** k=10  
**Criteria passed:** 6/8

## Temporal order

Parent onset: index 178, t=17.3280.  
Daughter field onset: index 197, t=18.7720.  
Daughter particle onset: index 209, t=19.6840.  
Field daughter minus parent: 19 slices,
1.4440 time units.

## Phase inheritance

| Measure | Value |
|---|---:|
| pre-parent baseline weighted resultant | 0.2873 |
| pre-daughter weighted phase-closure resultant | 0.9848 |
| post-daughter weighted phase-closure resultant | 0.9352 |
| post-daughter unweighted resultant | 0.8916 |
| circular-shift p | 0.5129 |
| random-phase p | 0.0020 |
| third-harmonic post-onset resultant | 0.6349 |

## Bicoherence

| View | Target bicoherence | Control percentile |
|---|---:|---:|
| field k5+k5->k10 | 0.8376 | 0.9748 |
| particle source k5+k5->k10 | 0.8334 | 0.9496 |
| pressure k5+k5->k10 | 0.6168 | not primary |

Baseline field/particle bicoherence: 0.1444 / 0.1082.  
Pre-daughter field bicoherence after parent onset: 0.9598.

## Parent-to-daughter lag

Raw daughter amplitude: best lag -20 slices, r=0.9172.  
Daughter growth: best lag -20 slices, r=-0.2509.  
Positive lag means parent driver leads daughter.

## Persistence and separate state

- consecutive slices above threshold after daughter onset: 262;
- fraction above threshold after parent peak: 1.0000;
- mean daughter amplitude after/before parent peak ratio: 0.9536;
- daughter field/particle TE correlation post-onset: 0.9991;
- mean daughter closure post-onset: 0.9985;
- mean daughter/parent field-power ratio post-onset: 0.0325.

## Decision criteria

- PASS: positive_temporal_order
- FAIL: phase_inheritance_beats_shift_null
- PASS: phase_inheritance_beats_random_phase_null
- PASS: field_bicoherence_top_5_percent_controls
- FAIL: particle_bicoherence_top_5_percent_controls
- PASS: persists_at_least_declared_slices
- PASS: persists_after_parent_peak
- PASS: separate_field_particle_state_correlation_over_0_8

## Verdict

The declared k10 candidate receives strong but incomplete development support as a nonlinear daughter identity. It
crosses the field threshold 19 slices after the parent and the particle threshold 31 slices after the parent. Phase
closure rises from {baseline_phase_r:.4f} before parent eligibility to {pre_phase_r:.4f} during sub-threshold daughter
formation and remains {post_phase_r:.4f} after visible onset. Field bicoherence rises from
{baseline_field_bicoherence:.4f} to {field_bicoherence:.4f}; particle bicoherence is
{particle_bicoherence:.4f}. The daughter persists and has a highly reproducible field/particle participation state.

Two strict fences prevent promotion. Circularly shifting the daughter within the already phase-locked post-onset
interval does not destroy closure, so the time-local shift null fails. Particle bicoherence ranks at the
{particle_percentile:.4f} percentile, just below the predeclared 0.95 cutoff. Parent-driver cross-correlation also peaks
at a negative boundary even though threshold onset order is positive, showing that gradual shared trends do not give
a clean predictive growth lag.

The most defensible reading is gradual nonlinear inheritance: coupling becomes phase-organised below the chosen
visibility threshold, the daughter then becomes measurable and persists as its own small participation mode. This is
consistent with established harmonic/three-wave physics. Whether the same bundle defines a scale-general ARA identity
requires noise/seed transfer.

**Status:** `6/8 STRICT CRITERIA / NONLINEAR DAUGHTER IDENTITY DEVELOPMENT-SUPPORTED / TIME-LOCAL AND PARTICLE-BICOHERENCE FENCES OPEN`.

## Fences

- Harmonic generation and three-wave phase coupling are established plasma mechanisms.
- This test asks whether the declared secondary mode meets a reproducible ARA identity-birth bundle.
- Daughter closure near one is not sufficient by itself because both participation fractions can be small; the
  field/particle correlation, phase inheritance, onset order and persistence carry the interpretation.
- Threshold onset means first sustained visibility under the declared rule, not creation from exact zero.
- A single already-inspected noise realisation cannot establish fractality or universality.
- The onset thresholds and mode family require transfer without alteration.
