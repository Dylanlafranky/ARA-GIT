# T425 — Geometric/state Irrationality Di-ARA on the T424 hourglass

**Frozen:** 24 August 2026, before T425 coordinates or plots were calculated  
**ARA hypothesis and geometry:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## Question

Does the older radial × angular Irrationality Di-ARA reveal a materially
different relational cut of the same real hourglass histories measured by
T424?

This is a side-by-side instrument comparison. T424 measures where the
hourglass identity currently sits on independently measured traversal and
packing axes. T425 measures how that already-declared two-axis state moves
between consecutive frames.

## Source and population

- Input coordinates:
  `../T424_hourglass_handover/results/T424_HOLDOUT_ARA_COORDINATES.csv`
- Direct event register:
  `../T424_hourglass_handover/results/T424_HOLDOUT_DIRECT_EVENTS.csv`
- Population: the same 16 held-out Toyoura-sand discharges, truncated at each
  run's independently detected terminal closure.
- No video region, T424 calibration, event label, closure index or smoothing
  parameter may be changed for T425.

## Frozen geometric construction

T424 supplies two complete 0–2 coordinates:

\[
C1_t=x_{trav,t},\qquad C2_t=x_{conn,t}.
\]

Their shared ridge is the origin of the state plane:

\[
z_t=(C1_t-1)+i(C2_t-1).
\]

For consecutive eligible states:

\[
q_t=\frac{z_{t+1}}{z_t}=s_t e^{i\Delta\theta_t},
\qquad s_t>0,
\qquad \Delta\theta_t\in(-\pi,\pi].
\]

The second Irrationality Di-ARA is:

\[
X_t=\frac{2s_t}{1+s_t},
\qquad
Y_t=1+\frac{\Delta\theta_t}{\pi}.
\]

- `X` is the radial/diameter ARA: contraction (`X<1`) versus expansion
  (`X>1`).
- `Y` is the angular/circumference ARA: reverse (`Y<1`) versus forward
  (`Y>1`) traversal.

No complement or sum-to-two relation is imposed between `X` and `Y`.

## Singularity guard

The quotient is undefined at the parent ridge `z=0`. For each run, calculate
the fifth percentile of positive `|z|` during the first 40% of its
pre-closure history. A transition is eligible only when both endpoint radii
exceed that frozen run-local floor. Invalid transitions remain missing; they
are not interpolated for quadrant occupancy or event scoring.

## Four geometric sectors

| Sector | Radial sign | Angular sign |
|---|---:|---:|
| contracting reverse | `log(s)<0` | `Δθ<0` |
| expanding reverse | `log(s)>0` | `Δθ<0` |
| expanding forward | `log(s)>0` | `Δθ>0` |
| contracting forward | `log(s)<0` | `Δθ>0` |

Axis-boundary values within `1e-12` are recorded separately.

## Frozen comparisons

1. Plot the T424 dynamic histories and the T425 geometric histories on
   matched 0–2 scales.
2. Plot the T424 movement/packing plane and the T425 radial/angular plane with
   their 1.0 ridges.
3. Report quadrant/sector occupancy using the same pre-closure frames.
4. Report how many of the 16 runs populate each T425 sector and all four
   sectors.
5. Locate direct events at the last eligible T425 transition at or before the
   event; this is descriptive and is not a forecast gate.

Median histories use 40 equal normalized-history bins. Each run contributes
at most one median per bin, so long runs do not dominate. Bins with no valid
T425 transition remain missing.

## Historical landmarks

The plots may show the earlier candidate landmarks as neutral references:

\[
s\in\{1/e,e\}
\Rightarrow
X\in\left\{\frac{2}{1+e},\frac{2e}{1+e}\right\},
\]

and a reciprocal-Phi angular magnitude

\[
\frac{|\Delta\theta|}{2\pi}=\varphi^{-2}
\Rightarrow
Y=1\pm2\varphi^{-2}.
\]

They are **not pass conditions**. T342 found no support for universal exact
`e` or reciprocal-Phi pure-axis endpoints, and the anti-Phi endpoint remains
unresolved.

## Interpretation boundary

The coordinate is an exact geometric re-expression of movement through the
declared T424 state plane. Four-sector occupancy alone is descriptive, because
the coordinate defines four possible sign combinations. A useful result is a
clear, reproducible difference between the state cut and movement-of-state
cut—not proof that either coordinate causes grain motion or that the historical
constants are universal.

