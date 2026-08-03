# T335 — river/thalweg Irrationality Di-ARA

**Date:** 3 August 2026  
**Status:** **SUPPORTED under the frozen protocol; 17/17 independent
validation checks passed**  
**Scope:** confirmatory reuse of one public curved-flume bed-topography
archive; no Phi or fixed-constant target

## Outcome first

The river archive recovered the typed **Irrationality Di-ARA** coordinate:
downstream step contraction/expansion crossed with reverse/forward turning.
All four declared sectors (`Ba`, `Ab`, `bA`, `aB`) were present in evaluation
and untouched holdout. The contraction and expansion endpoints closed near a
reciprocal pair around the local `1.0` ridge, the amplitude fitted only on
calibration transferred to both untouched splits, the recorded downstream
order beat every one of `1,000` step-order permutations, and intact
elevation-rank lineage substantially beat a cyclic broken-lineage control.

The rank-1 thalweg was unusually clean rather than merely representative of
the whole curved flume: it ranked `4/41` paths in evaluation and `1/41` in
holdout by reciprocal-endpoint loss.

This is a cross-domain recovery of the **four-sector form and reciprocal
organisation**, not a recovery of a universal constant. The fitted river
amplitude was about `1.10`, distinct from the amplitudes previously measured
in recorded qutrit and bubble identities. T335 did not test Phi.

## Plain-language ARA reading

Take one path downstream. Between successive river sections, its next step
can become shorter or longer. It can also turn one way or the other. Those
are two independent ARA cuts:

1. contraction versus expansion;
2. reverse versus forward turning.

Crossing them produces four mixed states:

| | Forward turn | Reverse turn |
|---|---:|---:|
| Contraction | `Ba` | `bA` |
| Expansion | `Ab` | `aB` |

The result says more than “a curving river can do all four things.” The
shortening and lengthening sides settled close to reciprocal positions around
the same-rung ridge, and that organisation depended on both the actual
downstream order and keeping each elevation-rank path intact. The minimum-bed
path expressed the closure especially strongly.

## Frozen construction

For elevation-rank path `r`, the measured planform point at section `k` was

\[
p_{r,k}=x_{r,k}+iy_{r,k}.
\]

Successive displacement vectors were

\[
v_{r,k}=p_{r,k+1}-p_{r,k},
\]

and the same-lineage local relation was

\[
q_{r,k}=\frac{v_{r,k+1}}{v_{r,k}}
=s_{r,k}e^{i\delta_{r,k}}.
\]

Here `s` measures how the next step changes in magnitude and `delta` is its
signed turn. No Fourier transform, smoothing, interpolation, fitted path or
target-dependent rotation was used.

The two exact ARA coordinates were

\[
X=\frac{2s}{1+s},
\qquad
Y=1+\frac{\delta}{\pi}.
\]

The radial map has the exact reflection identity

\[
X(1/s)=2-X(s).
\]

That identity and the diagonal reflection caused by reversing a quotient are
mathematical properties of the transform. They are not empirical findings.
The empirical questions were where the observed endpoint populations sat,
whether their relation transferred, and whether recorded order, intact
lineage and the thalweg outperformed controls.

## Source and splits

- Public workbook: `source_bedrock_bends/Bed-topography.xlsx`
- Source SHA256:
  `041FBFF2233E590AECFD9A5DFC08C84C5A17678A8DF1ABDAC667A21A2D823ED7`
- Retained cross-sections: `33`
- Elevation-rank paths: `41`
- Quotient events per path: `31`
- Primary events: `1,271`
- Calibration: middle angles `15–60°`, `410` field events
- Evaluation: `65–110°`, `410` field events
- Untouched holdout: `115–165°`, `451` field events
- Thalweg: rank `1`; ranks `2–41` were matched controls

The frozen protocol SHA256 was
`9724EA029D2A4A51A28149D1C6639CC55964A7F3DF0F37FE0D7B02F5A4953C72`.

## Primary results

### Reciprocal radial organisation

The calibration-only field amplitude was

\[
\alpha_{\rm cal}=1.097339454.
\]

| Population | Split | Contraction `s-` | Expansion `s+` | Product | Implied `alpha` | Endpoint loss |
|---|---|---:|---:|---:|---:|---:|
| Field | Calibration | 0.923794 | 1.112393 | 1.027622 | 1.097339 | 0.013622 |
| Field | Evaluation | 0.919682 | 1.135847 | 1.044618 | 1.111325 | 0.021826 |
| Field | Holdout | 0.894166 | 1.096260 | 0.980238 | 1.107258 | 0.009982 |
| Thalweg | Evaluation | 0.912532 | 1.135847 | 1.036497 | 1.115670 | 0.017923 |
| Thalweg | Holdout | 0.914068 | 1.091394 | 0.997608 | 1.092695 | 0.004241 |
| Thalweg | Pooled | 0.924170 | 1.091394 | 1.008633 | 1.086732 | 0.009714 |

Both untouched field amplitudes remained within the frozen 10% log-relative
transfer gate. Products remained within the frozen reciprocal-closure ranges.

### Four-sector occupancy

| Field split | `Ba` | `Ab` | `bA` | `aB` |
|---|---:|---:|---:|---:|
| Evaluation | 32.93% | 22.93% | 20.49% | 23.66% |
| Holdout | 27.05% | 30.68% | 22.22% | 20.05% |

Every field share cleared the frozen 5% floor. The thalweg occupied all four
sectors pooled (`8, 8, 6, 8` non-boundary events) and at least three sectors
in each untouched split.

### Order, lineage and thalweg controls

| Split | Observed field loss | 1,000-order-null median | Null 95% interval | Empirical `p` | Broken-lineage loss |
|---|---:|---:|---:|---:|---:|
| Evaluation | 0.021826 | 0.093766 | [0.063294, 0.131349] | 0.000999 | 0.105232 |
| Holdout | 0.009982 | 0.093372 | [0.062368, 0.133221] | 0.000999 | 0.128011 |

The observed order beat all `1,000` deterministic null draws in each split;
the reported empirical floor is therefore `1/(1000+1)`. Breaking the rank
lineage degraded the endpoint loss by roughly fivefold in evaluation and
thirteenfold in holdout.

Against the 40 matched rank controls, the thalweg endpoint loss was:

- evaluation: `0.017923`, rank `4/41`, control median `0.085737`;
- holdout: `0.004241`, rank `1/41`, control median `0.115911`.

## Gate audit

| Gate | Requirement | Result |
|---|---|---|
| G0 | Independent source-to-result integrity | **PASS** (`17/17`) |
| G1 | Four field sectors in evaluation and holdout | **PASS** |
| G2 | Thalweg sector coverage | **PASS** |
| G3 | Reciprocal closure | **PASS** |
| G4 | Calibration-amplitude transfer | **PASS** |
| G5 | Recorded order beats at least 95% of nulls | **PASS** |
| G6 | Intact rank lineage beats broken lineage | **PASS** |
| G7 | Thalweg specificity | **PASS** |

The runner deliberately leaves G0 pending/false so it cannot validate itself.
The separate validator reconstructed the source geometry, coordinates,
splits, endpoints, quadrant shares, path scores, all `2,000` split-null rows,
gates and verdict, passing `17/17` checks.

## What this changes

T335 adds a third materially different empirical setting to the current
Di-ARA evidence:

1. recorded qutrit relations recovered the four-sector reciprocal form and
   strong temporal order, but not exact Phi;
2. bubble lineages recovered the form and intact-identity dependence, while
   strict-holdout chronological order failed;
3. this river field recovered the form, reciprocal transfer, recorded order,
   intact rank lineage and a specifically strong thalweg expression.

The shared result is therefore increasingly the **geometry of two coupled ARA
cuts**, not one universal radial number or identical mechanism. Each domain
still translates those cuts through its own physical observables.

## Boundaries and possible ordinary explanations

1. This workbook was already opened in T327, so T335 is a confirmatory reuse,
   not a pristine discovery archive.
2. Ratios of successive step sizes can form reciprocal-looking distributions
   under stationary variation. That is why order, broken-lineage and thalweg
   controls are load-bearing; reciprocal products alone would be weak.
3. The whole flume bends, which can bias signed turn. Four-sector occupancy
   and matched rank controls reduce but do not eliminate that concern.
4. Elevation-rank paths track geometric bed features; they are not persistent
   parcels of water.
5. The reverse-direction diagonal reflection is algebraically forced by
   `q -> 1/q`, not independent physical evidence.
6. One flume cannot establish a universal river mechanism. An independently
   acquired river or channel archive must replicate the frozen coordinate.
7. T335 contains no Phi target and supplies no evidence for a universal Phi,
   `1/e`, `3/8` or other fixed endpoint.

## Reproduction

From the repository root, with the bundled Python runtime:

```powershell
& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'analysis\hydraulics\work\run_t335_river_irrationality_di_ara.py'

& 'C:\Users\Dylan\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  'analysis\hydraulics\work\validate_t335_river_irrationality_di_ara.py'
```

Primary artifacts:

- `T335_RIVER_IRRATIONALITY_DI_ARA_PROTOCOL_v1_FROZEN.md`
- `T335_RIVER_IRRATIONALITY_DI_ARA_RESULTS.json`
- `T335_RIVER_IRRATIONALITY_DI_ARA_VALIDATION.json`
- `T335_RIVER_IRRATIONALITY_DI_ARA_FIGURE.png`
- `results/T335_RIVER_IRRATIONALITY_DI_ARA_EVENTS.csv`
- `results/T335_RIVER_IRRATIONALITY_DI_ARA_ENDPOINTS.csv`
- `results/T335_RIVER_IRRATIONALITY_DI_ARA_QUADRANTS.csv`
- `results/T335_RIVER_IRRATIONALITY_DI_ARA_PATH_SCORES.csv`
- `results/T335_RIVER_IRRATIONALITY_DI_ARA_ORDER_NULLS.csv`

## Next decisive test

Freeze the same quotient and ARA maps on an independently acquired natural
river or channel trajectory with a declared downstream direction and matched
non-thalweg paths. The strongest replication would retain the reciprocal
field organisation and order/lineage advantage while allowing the fitted
amplitude to remain identity-specific. Failure of order or intact-lineage
controls would reduce T335 to an archive-specific geometric regularity.
