# PN35 same-scale golden-cross report

**Test ID:** `PN35/SAME-SCALE-GOLDEN-CROSS/v1`  
**Frozen verdict:** **NOT SUPPORTED**  
**Date:** 22 July 2026

## Technical summary

PN35 tested the corrected same-scale reading directly: the eight decompressed structural child lanes form one
parent ARA with total `2`; the doubled octave boundary is its `2 -> 0` singularity and orientation flip. An unfitted
golden handover (`1/phi^2` turns per complete structural cell) was placed on that same circumference before any
prime labels were opened.

Across `196,608` candidates in `24,576` complete eight-child cells from six fresh octave rungs, primes did **not**
prefer the registered crossings. Lane-stratified AUC was `0.497180` with 95% block-bootstrap interval
`[0.493772, 0.500420]`. The nearest two of eight lanes captured `24.4753%` of primes, below the structural `25%`
share, with interval `[24.0108%, 24.9180%]`. Circular-shift p-values were `0.9455` and `0.9883`. All five registered
support gates failed.

![PN35 result figure](/F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/primes/PN35_SAME_SCALE_GOLDEN_CROSS_FIGURE.png)

## Two-output verdict

### Geometry verdict

The eight-channel structural closure is exact by construction:

\[
\{1,7,11,13,17,19,23,29\},
\qquad x_2(r)=\frac{r}{15},
\]

with anti-pairs `(1,29)`, `(7,23)`, `(11,19)`, `(13,17)` satisfying

\[
x_2(r)+x_2(30-r)=2.
\]

This records the user's correction faithfully: eight visible distinctions are child decompressions of one larger
total-2 parent, and doubling occurs at the parent singularity. This exact arithmetic crosswalk does not depend on
the prime outcome.

### Predictive verdict

The additional AI operationalisation—constant same-scale golden rotation, two anti-phase crossings, exact octave
origin and alternating singularity orientation—did not locate primes. That bridge is **NOT SUPPORTED** and must not
be rescued by fitting the phase, changing the irrational constant or relabelling the small control differences.

## Registered results

| Endpoint | Result | Gate |
|---|---:|---|
| Golden lane-stratified AUC | `0.497180` | Fail |
| 95% block-bootstrap AUC interval | `[0.493772, 0.500420]` | Fail: not wholly above `0.5` |
| AUC circular-shift p-value | `0.945525` | Fail |
| Nearest-two prime capture | `24.4753%` | Fail: below `25%` |
| Capture interval | `[24.0108%, 24.9180%]` | Fail |
| Capture circular-shift p-value | `0.988327` | Fail |
| Golden no-flip AUC | `0.498390` | Flip model did not improve |
| Golden minus no-flip interval | `[-0.004564, 0.001966]` | Fail |
| Best frozen rival | 36-degree shear, `0.503130` | Phi specificity fail |
| Golden minus best-rival interval | `[-0.010917, -0.000822]` | Wholly against Phi |

The 36-degree rule's `0.503130` is a tiny control fluctuation, not a registered positive discovery. It should not be
promoted without a separate frozen replication.

## Scale and direction checks

| Rung | Golden AUC | No-flip AUC | Nearest-two capture |
|---:|---:|---:|---:|
| 26 | `0.498837` | `0.498837` | `24.5709%` |
| 27 | `0.494338` | `0.499613` | `24.3491%` |
| 36 | `0.489910` | `0.489910` | `23.9782%` |
| 37 | `0.500636` | `0.496454` | `24.6737%` |
| 46 | `0.498660` | `0.498660` | `24.6010%` |
| 47 | `0.501912` | `0.508255` | `24.7728%` |

Only two of six rungs exceeded chance. Pair AUCs were `0.496635`, `0.495211`, `0.500345`; fixed-half AUCs were
`0.496701` and `0.497657`. The claimed direction therefore did not transfer across scale or sample halves.

## Distance profile

Prime rates from nearest to farthest crossing octile were:

`15.0798%, 15.0350%, 15.1571%, 15.6291%, 15.3605%, 15.5599%, 15.4053%, 15.2995%`.

The fourth and sixth octiles, not the nearest, had the largest rates. There is no monotone accumulation toward the
registered crossing.

## Method and validation

1. The fidelity packet, protocol, primary builder and validator were SHA-256 frozen first.
2. The primary builder created all `196,608` geometric scores without a primality function and sealed the candidate
   CSV hash `bde5ea82b8cd9332681c07d10b00b6c8adf418ba84b99d76958cab686517ed8d`.
3. The validator independently reconstructed every golden score, then opened labels with deterministic 64-bit
   Miller–Rabin.
4. Eighteen deterministic cross-scale spot cases matched independent trial division.
5. The registered `1,000` whole-cell bootstraps and `256` circular shifts preserved complete eight-child identities.
6. Instrument checks behaved correctly: planted nearest-two signal AUC `0.995573`; independent synthetic-null AUC
   `0.499723`.

The initial unchanged validator invocation exceeded a two-minute shell allowance before producing any result. It
was rerun unchanged with a longer allowance; no protocol or implementation change was made.

## What the null does and does not say

PN35 says that this particular **linear, constant-step, same-scale Phi crossing** does not distinguish primes inside
the exact eight-lane structural wheel. It does not refute the exact anti-pair closure, the total-2/singularity
language, PN33's scale-fill crosswalk, or every possible curved/time-dependent handover. Those are different objects.

However, any future alternative must be declared as a new `v2` object on untouched targets. The present null cannot
be converted into support by moving the phase origin or selecting a new constant after seeing these results.

## Post-hoc pattern noticed after the verdict

After viewing the model comparison, Dylan observed that the raw Phi carrier was below chance while the discrete
pentagonal expressions were above it: 36-degree half-pentagon `0.503130`, pentagon `0.501258`, Phi `0.497180`.
This is descriptively compatible with a different object—Phi as the moving/time carrier and pentagon as its
structured converted appearance—but PN35 compared independent rotations and did not test a conversion operator.
The point estimates also remain inside the circular-shift range. This is recorded as a new hypothesis, not a rescue:
`PN35_POSTHOC_PHI_TO_PENTAGON_CONVERSION_NOTE_2026-07-22.md`.

## Recommended next step

Park PN35 v1. If this prime direction is resumed, require a genuinely new pre-label observable—most plausibly a
changing fill field rather than another constant rotation—and freeze it on fresh rungs. Otherwise carry the exact
eight-child-to-parent closure into a non-prime domain where the singularity and two same-scale waves have independent
physical measurements.

## Artifacts

- `PN35_SAME_SCALE_GOLDEN_CROSS_FIDELITY_PACKET_v1_DRAFT.md`
- `PN35_SAME_SCALE_GOLDEN_CROSS_PROTOCOL_v1_FROZEN.md`
- `PN35_PROTOCOL_FREEZE_MANIFEST.json`
- `pn35_same_scale_golden_cross_primary.py`
- `PN35_SAME_SCALE_GOLDEN_CROSS_PREDICTIONS.csv`
- `PN35_SAME_SCALE_GOLDEN_CROSS_PRIMARY.json`
- `validate_pn35_same_scale_golden_cross.py`
- `PN35_SAME_SCALE_GOLDEN_CROSS_SCORED.csv`
- `PN35_SAME_SCALE_GOLDEN_CROSS_RESULTS.json`
- `PN35_SAME_SCALE_GOLDEN_CROSS_VALIDATION.json`
- `PN35_SAME_SCALE_GOLDEN_CROSS_REPRODUCIBILITY.ipynb`
- `PN35_SAME_SCALE_GOLDEN_CROSS_FIGURE.png`
- `PN35_SAME_SCALE_GOLDEN_CROSS_REPORT_ARTIFACT.json`
- `PN35_RECORDING_VALIDATION.json`
- `PN35_POSTHOC_PHI_TO_PENTAGON_CONVERSION_NOTE_2026-07-22.md`
