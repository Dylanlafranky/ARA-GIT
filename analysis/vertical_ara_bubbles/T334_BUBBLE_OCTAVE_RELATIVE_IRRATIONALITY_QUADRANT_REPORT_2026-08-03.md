# T334 — Bubble octave-relative irrationality quadrant

**Date:** 3 August 2026  
**Status:** **SUPPORTED for the four-quadrant coordinate and octave-relative
reciprocal breathing; NOT SUPPORTED for one stable ordered operator or a
universal Phi endpoint.**  
**Independent validation:** `17/17` checks passed.

## Answer first

The new irrationality quadrant transfers from the recorded-qutrit test to the
public bubble archive at the level of **geometry**.

The previously established bubble Vertical-ARA relation is the complex
parent-to-parent multiplier

\[
q_{r,\ell}=\frac{Z_{r,\ell+1}}{Z_{r,\ell}}
           =s_{r,\ell}e^{i\delta_{r,\ell}}.
\]

Its raw radial scale is centred near the already-established octave carrier
`2`. T334 therefore removed that carrier before testing the new quadrant:

\[
u=\frac{s}{2},
\qquad
h=\log u.
\]

`u<1` is octave-relative contraction, `u>1` is octave-relative expansion,
and the sign of `delta` supplies reverse or forward turning. Their crossing
creates the four registered ARA sectors.

All four sectors occurred well above the frozen 5% floor in evaluation and
holdout. The median contraction and expansion also returned close to a
reciprocal pair:

\[
u_-u_+\approx1.
\]

That is the main positive result. It says the factor-two parent climb is the
carrier, while the lineage breathes inward and outward around that carrier.

It does **not** say every identity breathes at Phi. The bubble pair is much
narrower than the recorded-qutrit pair, and exact chronological order did not
replicate on holdout.

## Frozen design

The protocol was frozen before T334 endpoints were calculated. It reused the
existing immutable Pandey et al. bubble archive and inherited splits:

| Split | Videos | Retained roots | Transitions |
|---|---:|---:|---:|
| Calibration | 7 | 125 | 500 |
| Evaluation | 21 | 172 | 688 |
| Holdout | 7 | 40 | 160 |

The primary carrier was fixed at `2`. A geometric-median raw-scale carrier
was retained only as a sensitivity. The reciprocal endpoint scale was fitted
on calibration and then frozen for evaluation and holdout.

Controls were:

1. `500` deterministic within-root order shuffles;
2. a broken-lineage control that combined steps from different roots;
3. `5,000` whole-video bootstraps;
4. predeclared fixed reciprocal candidates from the plastic constant through
   `e`, including Phi and T333's qutrit endpoint.

Protocol SHA256:
`E827F7907FBE7B12699EA035453A60A3AC7DF5F4BA7A350B5686051D87C0023C`.

## Primary radial result

| Split | Contraction `u_-` | Expansion `u_+` | Product | Implied `alpha` |
|---|---:|---:|---:|---:|
| Calibration | 0.833555 | 1.210918 | 1.009366 | 1.205287 |
| Evaluation | 0.867331 | 1.191348 | 1.033293 | 1.171998 |
| Holdout | 0.784672 | 1.223070 | 0.959709 | 1.248485 |

The calibration-fitted reciprocal scale was

\[
\alpha_{\rm cal}=1.205286726,
\]

and it beat every fixed numerical candidate on evaluation and holdout. The
closest *fixed* candidate happened to be the plastic constant, but it was
only one member of a broad control set and is not promoted as a physical
constant by this result.

The whole-video product intervals were:

| Split | Product | 95% interval |
|---|---:|---:|
| Evaluation | 1.033293 | [0.955988, 1.071325] |
| Holdout | 0.959709 | [0.741966, 1.001206] |

At individual dyadic levels, `3/4` levels passed the registered reciprocal
product window in evaluation and `3/4` passed in holdout. The one failures
were evaluation level 3 (`1.156087`) and holdout level 0 (`0.776843`).

## Four-quadrant occupancy

Shares are calculated after excluding exact sign-boundary cases.

| Split | Contract/reverse | Contract/forward | Expand/reverse | Expand/forward |
|---|---:|---:|---:|---:|
| Calibration | 18.75% | 19.15% | 31.25% | 30.85% |
| Evaluation | 19.83% | 20.41% | 27.70% | 32.07% |
| Holdout | 18.13% | 26.88% | 27.50% | 27.50% |

This is not a sparse quadrant produced by one outlier branch. Every sector is
substantially populated in both untouched splits.

## What the controls say

### Temporal order

Evaluation recorded order was unusually close to the calibration-fitted
reciprocal pair:

- observed score `0.028007`;
- shuffle mean `0.064948`;
- `0/500` shuffles were as close;
- empirical `p=0.001996`.

The strict holdout did **not** repeat that result:

- observed score `0.035214`;
- shuffle mean `0.030545`;
- `329/500` shuffles were as close;
- empirical `p=0.658683`.

Therefore T334 does not support one stable chronological breathing operator.

### Identity preservation

Keeping the correct steps attached to the correct bubble was strongly
load-bearing:

| Split | Intact score | Broken-lineage score | Difference | 95% interval |
|---|---:|---:|---:|---:|
| Evaluation | 0.028007 | 0.113732 | -0.085725 | [-0.140260, -0.043118] |
| Holdout | 0.035214 | 0.235742 | -0.200528 | [-0.299123, -0.127895] |

Lower is better. The reciprocal organisation belongs to intact bubble
lineages rather than to the archive's pooled scale distribution alone.

## Frozen gate verdict

| Gate | Result |
|---|---|
| G0 — hashes, reconstruction and independent validation | **PASS (`17/17`)** |
| G1 — all four quadrants in evaluation and holdout | **PASS** |
| G2 — reciprocal closure around the octave carrier | **PASS** |
| G3 — calibration-fitted scale transfers | **PASS** |
| G4 — recorded order beats shuffles in both splits | **FAIL** |
| G5 — intact identity beats broken lineage | **PASS** |

The full all-gates dynamical claim fails because G4 fails.

## ARA interpretation

In plain ARA language:

- the raw bubble lineage climbs through the known `×2` parent carrier;
- after that carrier is removed, the child relation moves to both sides of
  its local `1.0` ridge;
- contraction/expansion and reverse/forward turning form the full four-mode
  quadrant;
- the inward and outward sides approximately close each other as one local
  reciprocal identity;
- the amount of that breath is identity-specific, not universally Phi;
- correct lineage matters more reliably than exact chronological cadence.

This makes T334 a cross-domain recovery of the **same coordinate family** as
T333, not a recovery of the same numerical endpoints. The shared part is the
four-mode sphere cut and reciprocal ridge closure. The differing part is the
radial amplitude and strength of time ordering.

## Evidential boundary

The bubble archive had already been opened for earlier Vertical-ARA and Phi
tests. T334 is a newly frozen question on those data, not a pristine
independent discovery archive. Dividing by `2` is justified by the
pre-existing bubble octave result; it must not be retrofitted to unrelated
datasets without an independently declared carrier.

The result does not establish Phi, the plastic constant, a universal Time
wave, or a new physical force. It supports a reusable ARA decomposition whose
numerical scale depends on identity and measurement.

## Reproduction

```powershell
python work/run_t334_bubble_octave_relative_irrationality_quadrant.py
python work/validate_t334_bubble_octave_relative_irrationality_quadrant.py
```

Primary files:

- `T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_PROTOCOL_v1_FROZEN.md`
- `T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_RESULTS.json`
- `T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_FIGURE.png`
- `T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_VALIDATION.json`
- `results/T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_EVENTS.csv`
- `results/T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_CELLS.csv`
- `results/T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_QUADRANTS.csv`
- `results/T334_BUBBLE_OCTAVE_RELATIVE_IRRATIONALITY_QUADRANT_NULLS.csv`

