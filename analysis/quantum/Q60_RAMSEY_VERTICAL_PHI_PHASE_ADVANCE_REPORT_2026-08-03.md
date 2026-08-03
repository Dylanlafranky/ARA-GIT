# Q60 — Ramsey vertical-Phi relative-phase advance

**Date:** 3 August 2026 (Australia/Brisbane)  
**Status:** FROZEN RETROSPECTIVE TEST COMPLETE  
**Result:** ORDERED TRANSPORT NOT SUPPORTED; NOT PHI-COMPATIBLE; PHI NOT IDENTIFIED  
**Independent validation:** PASS, `70/70` checks

## Answer first

This test rejects one precise proposed location for Phi:

> Phi is not the fixed phase advance from one complete saved Ramsey
> interference sweep to the next in this public experiment.

The reconstructed sweep-to-sweep phase was centred very close to no movement
around the ARA circle. The calibration-fitted step was

\[
c_{\rm fit}=0.000256194,
\]

whereas the predeclared Phi circle-train step was

\[
c_\phi=\frac{2}{\phi}=1.236067977.
\]

On evaluation data, persistence produced `0.207843` circular loss and Phi
produced `0.715688`. On holdout, persistence produced `0.398358` and Phi
produced `0.584061`. Lower is better.

This is evidence for the **asymmetric/persistent-circle explanation in this
observable**, not for a Phi handover between complete Ramsey sweeps. It does
not disprove the exact Phi circle-train mathematics, every possible
cross-scale Phi relation, or a distinct within-sweep/measurement-strength
effect. Those are different tests and cannot be substituted after seeing this
result.

## What was tested

### ARA description

- One complete Ramsey interference sweep was treated as one repeated identity
  or time slice.
- Its recovered phase was placed on the native ARA circle `0..2`.
- The ordered handover was

\[
d_j=(x_{j+1}-x_j)\bmod2.
\]

- The frozen Phi proposal predicted

\[
x_{j+1}=\left(x_j+\frac{2}{\phi}\right)\bmod2.
\]

### Established measurement description

Each raw row is a complete Ramsey fringe measured across `126` delay values.
The two detector channels were projected onto the common readout direction.
The file-average trace fixed the decay and oscillation frequency; sine and
cosine coefficients then recovered a phase for each of the `2,000` raw
sweeps. Detector `I/Q` were not relabelled as Bloch `X/Y`.

The six chronological files were split before scoring:

- calibration: 9 and 12 May 2023;
- evaluation: 16 and 19 May;
- holdout: 24 and 31 May.

The test is retrospective because the public archive had already been opened
for earlier ARA work, but its exact Q60 endpoint was frozen before calculation.

## Data adequacy

All six averaged Ramsey waveforms passed the frozen quality gate:

| Split | Mean-wave `R²` values | Raw sweep phases |
|---|---:|---:|
| Calibration | `0.9830`, `0.9845` | `2,000` per file |
| Evaluation | `0.9793`, `0.9654` | `2,000` per file |
| Holdout | `0.9310`, `0.8013` | `2,000` per file |

Individual raw sweeps were noisy: median per-sweep `R²` ranged from `0.0128`
to `0.0437`. This limits how finely a single phase can be interpreted. It does
not rescue the fixed-Phi claim: the same frozen reconstruction and circular
loss were used for every candidate, Phi was far from the observed central
step, and the result repeated in both evaluation and holdout.

## Primary frozen comparison

| Candidate step | Evaluation loss | Holdout loss |
|---|---:|---:|
| Persistence `0` | **0.207843** | 0.398358 |
| Calibration-fitted `0.000256` | **0.207843** | **0.398239** |
| Previous-step velocity | 0.345401 | 0.483470 |
| `1/e` | 0.385968 | 0.444993 |
| `sqrt(2)` | 0.574826 | 0.540135 |
| `2/e` | 0.701604 | 0.557458 |
| `5/4` | 0.707356 | 0.580724 |
| `26/21` | 0.714066 | 0.583591 |
| **`2/phi`** | **0.715688** | **0.584061** |
| anti-Phi orientation | 0.720039 | 0.568028 |

The evaluation circular-mean step was `1.999731`, equivalent to a tiny
negative drift around the `0..2` circle. Its block-bootstrap interval was
`[1.995425, 2.004399]`. Holdout was `0.035194`, interval
`[0.000285, 0.063744]`. Neither interval contains `2/phi`.

At Fibonacci lags `1,2,3,5,8,13,21`, persistence/calibration-fitted remained
best. Phi's aggregate loss was `0.347553` in evaluation and `0.440639` in
holdout, versus persistence's `0.209189` and `0.388909`.

## Controls and frozen verdicts

The fitted near-zero advance did not establish general ordered transport:

- evaluation improved over shuffled order by only `0.94%`, not the frozen
  `20%` gate (`p_no_worse=0.291`);
- holdout was `2.42%` worse than shuffled order (`p_no_worse=0.9275`);
- broken-lineage and persistence gates were not both passed in both splits.

Therefore:

| Gate | Verdict |
|---|---|
| G0 — usable phase reconstruction | **PASS** |
| G1 — ordered phase transport | **FAIL / NOT SUPPORTED** |
| G2 — Phi compatibility | **FAIL / NOT PHI-COMPATIBLE** |
| G3 — Phi identification | **FAIL / PHI NOT IDENTIFIED** |

The close rational `26/21` was not cleanly distinguishable from exact Phi,
but that resolution issue is secondary: both were decisively worse than
persistence and the calibration-fitted step. The result does not depend on
choosing between those two neighbouring constants.

## Plain-language interpretation

The repeated quantum interference circles did not step around the ARA circle
by Phi. They mostly returned to approximately the same phase, with growing
scatter in the later files. In the language of the question, measurement did
not reveal a regular irrational Phi handover that then collapsed into a
rational-looking path. This dataset instead shows a stable laboratory phase
reference plus drift/noise.

That gives the Phi investigation a sharper map:

1. **Ruled out here:** a universal `2/phi` jump between consecutive complete
   Ramsey sweeps.
2. **Still open but untested here:** Phi as a within-sweep relation, a
   cross-scale parent/child relation, or a change specifically caused by
   varying which-path/measurement strength.
3. **Methodological consequence:** none of those open placements may be used
   to reinterpret Q60. Each requires a new frozen coordinate and a dataset
   that actually varies the relevant measurement or scale.

## Reproduction and audit

- Frozen protocol:
  `Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_PROTOCOL_v1_FROZEN.md`
- Primary runner:
  `q60_ramsey_vertical_phi_phase_advance.py`
- Independent validator:
  `q60_validate_ramsey_vertical_phi_phase_advance.py`
- Machine-readable result:
  `Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_RESULTS.json`
- Per-sweep phases:
  `Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_PHASES.csv.gz`
- Primary scores and Fibonacci lags:
  `Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_SCORES.csv`,
  `Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_LAGS.csv`
- Figure:
  `Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE.png` and `.svg`
- Validation record:
  `Q60_RAMSEY_VERTICAL_PHI_PHASE_ADVANCE_VALIDATION.json`

Source: Arnold and Werner, *All-optical superconducting qubit readout*,
Zenodo DOI `10.5281/zenodo.14033026`. Source archive SHA-256:
`73F3E2CA7B3658452B4C171532C751E96D7392DCB8741B87A18E28C7073D67FD`.

## Boundary

The archive preserves row order but supplies no per-sweep timestamps, so Q60
assumes row order is acquisition order. Q60 measures reconstructed phase
between repeated Ramsey sweeps; it is not a literal double-slit trajectory
test and it does not compare measured versus unmeasured particles. A direct
measurement-collapse claim needs a public experiment with frozen conditions
that vary which-path information or measurement strength while preserving
the underlying phase coordinate.
