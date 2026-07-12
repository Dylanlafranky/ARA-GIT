# MX3e daughter-to-grandchild harmonic result

**Tier:** DEVELOPMENT / ALREADY INSPECTED / SINGLE NOISE REALISATION  
**Declared grandchild candidate:** k=20 from k=10+k=10  
**Mixed alternative route:** k=5+k=15 -> k=20  
**Criteria passed:** 8/8

## Onset order

| Mode | Field onset index | Time | Particle onset index |
|---|---:|---:|---:|
| parent k5 | 178 | 17.3280 | 164 |
| daughter k10 | 197 | 18.7720 | 209 |
| mixed descendant k15 | 297 | 26.3720 | 317 |
| grandchild candidate k20 | 260 | 23.5600 | 266 |

k20 follows k10 by 63 field slices
(4.7880 time units) and
57 particle slices.

## Phase inheritance

| Route | Post-onset resultant | Random-phase p |
|---|---:|---:|
| k10+k10->k20 | 0.8481 | 0.0010 |
| k5+k15->k20 | 0.3750 | 0.2088 |

k10+k10->k20 phase concentration: baseline 0.3146, between daughter and grandchild thresholds
0.8439, post-grandchild 0.8481.

## Route bicoherence

| View | k10+k10->k20 | k5+k15->k20 | k10 route percentile among sum-20 routes |
|---|---:|---:|---:|
| field | 0.5760 | 0.2407 | 0.9000 |
| particle | 0.6022 | 0.2654 | 0.9000 |

## Persistence and separate state

- persistent slices after k20 onset: 199;
- mean k20/k10 field-power ratio: 1.809603;
- mean k20 field-power fraction: 0.00173931;
- field/particle k20 TE correlation: 0.9988;
- mean k20 closure: 0.9989.

## Criteria

- PASS: grandchild_field_after_daughter
- PASS: grandchild_particle_after_daughter
- PASS: daughter_self_coupling_phase_null_pass
- PASS: daughter_self_coupling_field_bicoherence_top_20pct_routes
- PASS: daughter_self_coupling_particle_bicoherence_top_20pct_routes
- PASS: persists_declared_slices
- PASS: separate_field_particle_state_correlation_over_0_8
- PASS: detectable_mean_power_fraction_over_1e_minus_5

## Verdict

All eight development criteria pass for a detectable, persistent k20 descendant after k10. The daughter-self-coupling
route has strong phase inheritance and is much stronger than the disclosed k5+k15 mixed route. However, k10+k10 is
not the strongest sum-20 triad: k9+k11 has higher field and particle bicoherence. The result therefore supports a
grandchild within a wider nonlinear coupling web, not an exclusive binary family tree.

The k20 field onset precedes k15, and the k5+k15 phase null fails, which argues against that mixed route being the
primary origin in this trajectory. The grandchild remains fine but measurable, with mean field-power fraction
{state['mean_grandchild_field_power_fraction']:.8f} and field/particle state correlation
{state['field_particle_te_correlation']:.4f}.

**Status:** `8/8 DEVELOPMENT CRITERIA / GRANDCHILD HARMONIC SUPPORTED / UNIQUE GENEALOGY AND NOISE TRANSFER OPEN`.

## Fence

A k20 harmonic is not genealogically unique. It can be generated through k10+k10, k5+k15, repeated k5
self-coupling, or a wider nonlinear network. Strong k10+k10 coupling supports a daughter-self-coupling route but does
not prove that it is the only route. Noise/seed convergence is required because fine modes are most vulnerable to
particle and grid noise.
