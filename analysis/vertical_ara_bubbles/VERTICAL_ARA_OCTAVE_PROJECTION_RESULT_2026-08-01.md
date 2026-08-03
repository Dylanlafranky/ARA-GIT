# Vertical ARA octave-to-Phi projection result

**Date:** 1 August 2026  
**Status:** completed and independently validated  
**Source:** Zenodo `10.5281/zenodo.15102957`

## Outcome

The sampled two-dimensional bubble-centroid coordinate does **not** support
the registered hypothesis that an octave-sized parent of magnitude `2`
projects into its same-origin child at `36 degrees`, producing

\[
2\cos36^\circ=\phi.
\]

The parent and child directions were substantially more aligned. The median
free same-origin angle was:

| Split | Roots | Median free angle | Closest frozen target |
|---|---:|---:|---:|
| Calibration | 125 | 14.41 degrees | 0 degrees |
| Evaluation | 172 | 10.46 degrees | 0 degrees |
| Confirmation | 40 | 10.05 degrees | 0 degrees |

The equivalent ARA projection

\[
x_A=2|\cos\theta_A|
\]

therefore remained close to `2`, not Phi.

## What was measured

At each of four same-origin dyadic levels,

\[
A_\ell=\sum_{j=0}^{n_\ell-1}\Delta z_j,
\qquad
B_\ell=\sum_{j=n_\ell}^{2n_\ell-1}\Delta z_j,
\qquad
P_\ell=A_\ell+B_\ell,
\]

with child spans `2`, `4`, `8`, `16` frames and parent spans `4`, `8`, `16`,
`32` frames. The primary folded angle was

\[
\theta_{A,\ell}
=\arccos
\frac{|A_\ell\cdot P_\ell|}{|A_\ell||P_\ell|}.
\]

Phi was not used to construct the vectors or the measured angle.

## Fixed-angle comparison

Lower root-mean-square angular loss is better.

| Target | Angle | Evaluation loss | Confirmation loss |
|---|---:|---:|---:|
| **Direct** | **0 degrees** | **17.91** | **18.04** |
| 30 degrees | 30 degrees | 22.95 | 23.30 |
| Phi projection | 36 degrees | 27.48 | 27.53 |
| Diagonal | 45 degrees | 34.96 | 34.51 |
| Phi complement | 54 degrees | 42.93 | 42.08 |
| Ridge-half | 60 degrees | 48.43 | 47.39 |
| Perpendicular | 90 degrees | 77.14 | 75.96 |

In evaluation, Phi-minus-direct loss was `+9.572 degrees`, with a whole-video
95% interval `[+6.820,+12.934]`. Phi-minus-30-degrees was `+4.537 degrees`,
with interval `[+4.172,+4.941]`. The positive differences mean the registered
Phi projection was decisively worse than both nearer-direction targets.

## Scale progression

The same-origin angle decreased rather than stabilizing near `36 degrees`:

| Child to parent span | Evaluation mean angle | Evaluation median ARA projection |
|---|---:|---:|
| 2 to 4 frames | 21.20 degrees | 1.9592 |
| 4 to 8 frames | 14.94 degrees | 1.9746 |
| 8 to 16 frames | 12.53 degrees | 1.9843 |
| 16 to 32 frames | 8.78 degrees | 1.9857 |

Confirmation showed the same general alignment, with median ARA projections
from `1.9464` to `1.9897`.

The signed-cosine diagnostic was also predominantly positive. Only `0-4.1%`
of evaluation relations were anti-directional at any level, and the broadest
level had none. This coordinate therefore shows direct persistence, not a
hidden `144-degree` anti-direction that merely folds to `36 degrees`.

## Decisive controls

The phase-scramble control retained each observed `A`, every observed `|B|`,
and the same addition `P=A+B`, but randomized only the relative phase over `64`
deterministic rotations per root.

| Evaluation comparison | Observed Phi loss minus control | 95% whole-video interval | Required for support |
|---|---:|---:|---:|
| Phase-scrambled complement | +3.244 | [+2.427,+4.341] | negative |
| Broken complement | +2.164 | [+1.340,+2.838] | negative |

The observed lineage was farther from `36 degrees` than either control. This
is consistent with real directional persistence pulling the parent toward the
child, not with a Phi projection at this cut.

The complementary `B` child behaved similarly: its evaluation median free
angle was `9.74 degrees`, also closest to direct alignment.

## Gate verdicts

| Registered gate | Result |
|---|---|
| Phi target specificity | Failed |
| Real phase relation versus controls | Failed |
| Phi recurrence at every rung | Failed |
| Free angle closest to 36 degrees | Failed |
| Overall octave-to-Phi projection | **Not supported** |

## Interpretation

This is a clean rejection of one proposed coordinate:

> Phi is not recovered by projecting the same-origin accumulated centroid
> displacement directly onto its doubled-span parent displacement.

The result does **not** reject every version of the new quarter-access idea.
The measured `P=A+B` parent includes `A` itself, so persistent motion makes
direct alignment the natural result. If the intended Phi distortion belongs
to only one quadrant, a perpendicular boundary component, or the relation
between a local phase and an independently measured larger anti-phase, that
object is not isolated by this centroid-parent cut and must be defined before
another test.

The scalar remainder `2-x_A` was not counted as separate evidence because it
is forced by the projection definition. `3/8` and `2-Phi` also remain distinct:

\[
(2-\phi)-\frac38=0.00696601125\ldots
\]

## Reproduction and validation

Frozen protocol:
`FROZEN_PROTOCOL_VERTICAL_ARA_OCTAVE_PROJECTION_2026-08-01.md`

Run with the configured scientific Python:

```powershell
python work/run_vertical_ara_octave_projection.py
python work/validate_vertical_ara_octave_projection.py
```

Independent validation passed with:

- `337` reconstructed roots;
- maximum recorded formula discrepancy `4.26e-11`;
- zero summary discrepancies;
- zero bootstrap discrepancies;
- raw-source vector spot checks below `3e-17`;
- no validator errors.

Machine-readable outputs:

- `results/octave_projection_root_results.csv`
- `results/octave_projection_level_summary.csv`
- `results/octave_projection_summary.json`
- `results/octave_projection_validation.json`

