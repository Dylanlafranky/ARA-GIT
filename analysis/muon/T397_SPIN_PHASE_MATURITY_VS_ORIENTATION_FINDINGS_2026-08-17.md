# T397 — spin phase maturity versus orientation findings

**Date:** 17 August 2026  
**Status:** `ORIENTATION_SUPPORTED_MATURITY_NOT_SUPPORTED`  
**Protocol SHA-256:**
`62D2ADA024A2D7077FCB9A893871EB960BE324ACC431158B24011DC3161B41F5`

## Result in plain language

Spin phase strongly predicts **which detector direction** receives the charged
daughter signal. It does not yet reliably predict **when the whole muon
population releases**. A tiny phase-coherent trace remains after detector
acceptance is balanced, but it is not stable enough across fields and parity
to call it a neutrino-creation or population-maturity clock.

This refines the working ARA interpretation:

> Spin is supported as the orientation of the muon handover waveform. A
> population-wide maturity component remains an unresolved weak coupling.

## Frozen identities and cuts

- **Who:** positive-muon populations in the same 300 K RAL Silver medium.
- **Parent:** the exponentially decaying population envelope.
- **Orientation child `O`:** the signed full 96-detector pattern.
- **Raw total `U`:** forward plus backward counts.
- **Balanced total `V`:** forward plus calibration-only balanced backward
  counts.
- **Strict common mode `W`:** all detector channels normalized with
  calibration-only shares before summation.
- **Time cut:** native 0.016 microsecond bins from 0.25 to 8.00 microseconds.
- **Primary split:** odd spin cycles train; even spin cycles test. The reverse
  split was retained as a sensitivity test.

`O` asks whether phase carries direction. `W` asks the stronger question:
does the same phase remain in an acceptance-balanced parent total strongly
enough to behave as population maturity?

## Main measurements

| Cut | Pooled held-out SSE gain | Hierarchical 95% interval |
|---|---:|---:|
| Orientation `O` | 14.4147% | [2.4618%, 25.2033%] |
| Raw total `U` | -1.6421% | [-3.8863%, 0.9781%] |
| Bank-balanced `V` | -1.6208% | [-3.7710%, 0.9388%] |
| Detector-normalized `W` | 0.7128% | [-1.9853%, 2.8053%] |

The strict common-mode phase amplitude was only `0.06310%` of its fitted
parent envelope. Its phase resultant length was high (`0.9350`) and the
physical cadence beat the predeclared wrong-cadence envelope. Those are useful
lead conditions, but not sufficient evidence of maturity.

Per-field `W` gains were:

- 63 G: `+1.0357%`;
- 160 G: `+1.9543%`;
- 400 G: `-1.0622%`.

Under reverse parity, 63 G also became negative. Consequently the frozen
requirements for positive gain in every field, a bootstrap interval above
zero and reverse-parity field consistency failed.

## What passed

- `O` was positive at all three held-out fields.
- The hierarchical interval for pooled `O` excluded zero.
- Physical spin cadence beat every tested wrong cadence for `O`.
- The small `W` residue was phase coherent and narrowly cadence specific.
- Independent validation reconstructed the saved source layouts, principal
  values, field-level `W` fits, gates, status and claim boundary.

## What did not pass

- Neither raw nor bank-balanced parent total improved on its no-phase model.
- `W` was not positive in every held-out field.
- The hierarchical `W` interval crossed zero.
- Reverse parity did not retain non-negative `W` gain in every field.

The frozen maturity claim therefore failed even though orientation passed.

## Claim boundary

Supported in this source:

> Spin phase is a stable population-level organiser of the charged-daughter
> detector direction in the held-out RAL Silver fields.

Not supported:

- a universal phase-of-release or maturity clock;
- an individual muon's neutrino-creation time;
- revival of the failed exact 7.5-turn trigger;
- direct observation of either neutrino;
- new particle physics.

The archive contains aggregate detector histograms rather than event-linked
parent/daughter records. It was also inspected in earlier tests, so T397 is a
locked new question on an old source, not an untouched-source discovery.

## Next decisive test

Repeat the same `O/U/V/W` construction on an untouched same-medium EMU silver
campaign, learning detector weights only from that campaign's calibration
runs. A maturity replication requires `W` to remain positive at each field,
exclude zero under hierarchical resampling and survive reverse parity while
`O` again passes. Failure would leave spin classified as orientation only;
success would justify seeking event-linked neutral-sensitive data.

## Artifacts

- Protocol: `analysis/muon/T397_SPIN_PHASE_MATURITY_VS_ORIENTATION_PROTOCOL_2026-08-17.md`
- Results: `analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_RESULTS.json`
- Independent validation: `analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_VALIDATION.json`
- Portable report: `analysis/muon/T397_spin_phase_maturity_vs_orientation/T397_SPIN_PHASE_MATURITY_VS_ORIENTATION_REPORT.html`
