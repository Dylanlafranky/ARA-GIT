# T423 — parent Di-ARA temporal architecture

**Date:** 23 August 2026  
**Originator hypothesis:** Dylan La Franchi  
**Registration:** frozen before development scoring  
**Final benchmark status:** **SUGGESTIVE / INCONCLUSIVE — SCIENTIFICALLY UNAVAILABLE**  
**Arithmetic/provenance audit:** **PASS, 125/125 checks**

## Outcome first

T423 did not obtain an out-of-sample comparison of the three registered
architectures:

```text
M0: child C1 -> child C2
M1: child C1 -> compressed parent H -> child C2
M2: child C1 -> parent PA -> parent PB -> child C2
```

The T421 archive contains successive opposite-direction child `U=R`
crossings, but the crossing-to-crossing intervals are usually narrower than
the native saved time step. Only four causal prediction rows existed, all in
development. Validation and holdout supplied zero causal rows. No selected
child interval in any split contained the proposed internal-parent `Q=1`
handover.

Therefore T423 cannot select M0, M1 or M2. It also cannot reject their shared
ARA geometry. The result is a measurement-grain failure at the exact temporal
bridge the test needed.

## Confirmed test card

### Who

The full 96-detector muoniated-acetone ensemble spin relation in the ISIS EMU
archive. This remains a detector-population test, not an individual muon or
neutrino event.

### What

Three nested causal predictors of remaining physical time to the next
opposite-direction child `U=R` crossing:

- M0 used child `U,R`, their first differences, elapsed interval time,
  parent-lifespan coordinate, field scale, RF condition and direction;
- M1 added compressed candidate-parent `H,dH,|H-1|`;
- M2 added decompressed orientation `Q,dQ,|Q-1|`.

### When

Only T421 causal timeline values after the fixed `2.25 microsecond`
calibration boundary. Development fit and froze the models; validation and
the 1800–2484 G / 202 K holdout were untouched scoring splits.

### Where

- child cut: full-detector `U <-> R`, each on its own 0–2 coordinate;
- child crossover: `U=R`;
- compressed candidate-parent ridge: `H=1`;
- proposed internal-parent handover: `Q=1`;
- relational C1/C2: the two opposite child-crossing directions.

### Why

To distinguish direct child alternation, traversal through one compressed
parent state, and traversal through an internally decompressed parent
Di-ARA.

### How

Development-only fixed-ridge models, interval-balanced absolute error,
field bootstrap, wrong-frequency, reversed-parent, circular-shift, RF and
parent-order controls, followed by independent saved-artifact validation.

## Availability result

| Frozen split | Raw run/RF sequences | Opposite child intervals | Intervals with causal rows | Causal rows | C1 returns | Q=1 parent handovers |
|---|---:|---:|---:|---:|---:|---:|
| Development | 26 | 4 | 2 | 4 | 2 | 0 |
| Validation | 26 | 7 | 0 | 0 | 3 | 0 |
| Holdout | 40 | 5 | 0 | 0 | 1 | 0 |

The child crossings themselves are real interpolated landmarks. A causal
prediction interval additionally required at least two native sample centres
between its start and end. That second condition is what failed.

## Why the development numbers are not evidence

The saved development MAEs were:

| Model | Features | Training rows | In-sample field-balanced MAE (microseconds) |
|---|---:|---:|---:|
| M0 | 9 | 4 | `0.0000051768` |
| M1 | 12 | 4 | `0.0000051725` |
| M2 | 15 | 4 | `0.0000036280` |

M2 was numerically closest and beat its wrong-frequency and reversed-history
variants in development. This is not an empirical architecture result: every
model had more fitted coefficients than training rows once its intercept is
included. Ridge regularisation provides a numerical solution but cannot make
four in-sample rows identify a 15-feature parent traversal.

## Frozen-gate verdict

- G1 failed: validation had 7 opposite intervals rather than 20; holdout had
  5 rather than 10.
- G2–G4 were unavailable because validation and holdout had zero causal model
  rows.
- G5–G6 were unavailable because no child interval contained a `Q=1`
  parent-orientation crossing.
- G7–G8 were unavailable out of sample for the same model-row reason.

The implementation recorded unavailable gates as false booleans. The
scientific report preserves the more accurate distinction: no directional
reversal was measured; the required scoring object was absent.

## Important methodology finding

Frozen G1 counted complete opposite-direction crossing intervals. The causal
primary needs another availability guard: native interior samples within
those intervals. An interpolated interval can therefore count toward G1 while
providing no prediction row.

Future temporal-architecture tests must freeze both:

1. a minimum number of complete child intervals; and
2. a minimum number of causal interior rows and independent development rows
   relative to fitted model dimension.

This is a test-design correction for future work, not permission to change
T423 after seeing its outcome.

## Two fixed verdicts

### Benchmark verdict

**SUGGESTIVE / INCONCLUSIVE — SCIENTIFICALLY UNAVAILABLE.** The registered
comparison could not be evaluated out of sample. The tiny development errors
are underdetermined in-sample diagnostics and must not be reported as a win.

### ARA geometry verdict

**Successive child U/R handovers are present, but their parent route is
unresolved.** T423 does not decide between:

```text
C1 -> C2
C1 -> H -> C2
C1 -> PA -> PB -> C2
```

It leaves T421's child-singularity/parent-ridge result intact. The missing
object is the chronological path between its landmarks.

## Relational Bridge Map

| Step | Anchor | Recorded relation |
|---:|---|---|
| 1 | Physical identity | Full-detector muoniated-acetone ensemble spin relation |
| 2 | Observed source | Causal T421 timelines after 2.25 microseconds |
| 3 | Child cut | Independent 0–2 U/R coordinates and their opposite crossing directions |
| 4 | Candidate parent | H as compressed ridge coordinate; Q as proposed internal orientation |
| 5 | Discriminating test | Nested M0/M1/M2 forecast of the next opposite child crossover |
| 6 | Available evidence | Four development rows; no validation/holdout rows; no Q=1 events |
| 7 | Actual finding | Child alternation is visible; parent traversal is not temporally resolved |
| 8 | Missing bridge | Finer or longer causal data spanning C1→C2→C1 and Q=1 |

## Pivot Log

No identity, rung, axis, medium, crossing definition or target changed after
scoring began. The frozen geometry was retained even after the data showed
that wider intervals would be easier to score. T423 is therefore an honest
availability result rather than a post-hoc redefinition.

## Recommended next test

Use the same registered geometry only on a timeline that contains:

- multiple native samples within each child interval;
- several complete `C1 -> C2 -> C1` returns in development, validation and
  holdout;
- at least some `Q=1` crossings inside those intervals;
- enough independent development rows to support the frozen model dimension.

If no such recording exists, the next study must explicitly re-card a
different physical observable as C1/C2. It must not silently widen T423's
crossing intervals.

## Durable artifacts

- Frozen protocol: `T423_FROZEN_PROTOCOL.md`
- Development freeze: `T423_DEVELOPMENT_FREEZE.json`
- Analysis: `t423_parent_di_ara_temporal_architecture.py`
- Independent validator: `validate_t423.py`
- Validation receipt: `results/T423_INDEPENDENT_VALIDATION.json`
- Canonical report artifact: `artifact.json`
- Portable visual report:
  `results/T423_PARENT_DI_ARA_TEMPORAL_ARCHITECTURE_REPORT.html`

The portable report passed schema validation and packaging. Browser rendering
was not executed because the local portable-report tool could not locate a
Chromium headless-shell executable; verification was structural only.
