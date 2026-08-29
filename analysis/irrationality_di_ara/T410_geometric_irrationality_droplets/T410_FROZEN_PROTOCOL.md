# T410 — Geometric Irrationality Di-ARA at water-droplet handover

**Status:** frozen after development-only extraction and before any holdout
geometry was extracted or scored  
**Frozen:** 18 August 2026  
**Originator of the ARA hypothesis:** Dylan La Franchi  
**Operationalisation and implementation:** Codex

## Relational address

- **Who:** the same eight registered water-droplet handovers used by T409.
  E1/E2/E5/E7 are development; E3/E4/E6/E8 remain holdout.
- **What:** the geometric/state Irrationality Di-ARA: radial/diameter scale
  change crossed with angular/circumference rotation.
- **When:** every adjacent encoded frame from the established two-lobe state
  through persistent lobe loss and early reclosure.
- **Where:** the same local droplet-pair ROIs and pre-wetted-fibre identity
  scale as T409.
- **Why:** test whether the physical handover has a reproducible geometric
  quadrant/axis address even though T409's `R=I` amplitude rule failed.
- **How:** robust affine optical flow, polar decomposition, exact ARA mapping,
  development-registered line/contraction gate, held-out transfer and
  within-event circular-shift controls.

## Target status

| Item | Status |
|---|---|
| Persistent lobe-loss handover | **Direct** |
| Radial scale and angular rotation | **Inferred from observed droplet pixels** |
| Molecular bridge formation | **Absent** in the fibre clips; the fibre is pre-wetted |
| Causal microphysical mechanism | **Not measured** |

## Geometric instrument

For every adjacent-frame robust affine map, retain its linear part `A`. Its
proper polar decomposition supplies an isotropic scale `s_t > 0` and rotation
`dtheta_t`. Shear anisotropy is retained as QA and does not alter the primary
coordinate.

Compose the similarity relation from the registered event start:

\[
S_t=\prod_{j\le t}s_j,
\qquad
\Theta_t=\sum_{j\le t}\Delta\theta_j.
\]

Map it to the exact two ARA cuts:

\[
X_t=\frac{2S_t}{1+S_t},
\qquad
Y_t=1+\frac{\operatorname{wrap}(\Theta_t)}{\pi}.
\]

The four quadrants are contraction/expansion (`X<1` / `X>1`) crossed with
reverse/forward rotation (`Y<1` / `Y>1`). The unsigned line-to-circle mixing
angle is

\[
\gamma_t=\operatorname{atan2}(|Y_t-1|,|X_t-1|).
\]

`gamma = 0°` is the pure radial/diameter limit; `gamma = 90°` is the pure
angular/circumference limit. No `e`, Phi or reciprocal-Phi endpoint is fitted
or forced. T341 previously rejected those constants as a universal package.

## Development observation used to freeze the transfer

The development events gave the following direct-target coordinates:

| Event | X at handover | Y at handover | gamma |
|---|---:|---:|---:|
| E1 | 0.987924 | 1.001153 | 5.4517° |
| E2 | 0.992740 | 0.997910 | 16.0579° |
| E5 | 0.992828 | 1.001890 | 14.7640° |
| E7 | 0.995005 | 1.000553 | 6.3135° |

All four are radially contracting. Angular sign is not common, so no preferred
forward/reverse quadrant is registered. The transferred line cone is fixed at
`gamma <= 20°`, the broader cone already used as a T341 sensitivity, rather
than fitted to the exact development maximum.

## Frozen primary holdout gate

At the **direct registered target frame**, an event is a geometric handover
hit when

\[
X<1
\quad\text{and}\quad
\gamma\le20^\circ.
\]

Primary support requires all of:

1. at least `3/4` holdout events are hits;
2. the holdout median direct-target `gamma <= 20°`;
3. the observed holdout hit count exceeds at least 95% of 10,000 joint
   within-event circular shifts of the registered target position over
   `0.20 <= u <= 1.35` (`p < 0.05`, deterministic seed `4102026`).

The shift control preserves every event's geometric trajectory and state
occupancy while breaking its alignment to the physical handover.

## Frozen secondary transition check

For each event compare median mixing angle in the fixed windows

- pre: `0.70 <= u < 1.00`;
- post: `1.00 < u <= 1.30`.

The registered direction is `median(gamma_post) < median(gamma_pre)`, meaning
the geometry becomes more line-like across handover. This is secondary and
cannot rescue a failed primary gate.

## QA and controls

- report RANSAC inlier fraction and valid vector count at every direct target;
- report affine shear anisotropy separately;
- repeat the primary descriptive count for 15° and 25° cones as sensitivity;
- show every holdout trajectory with numerical `X`, `Y`, `u` and `gamma`
  axes;
- keep the flat-substrate S1 transfer separate from the fibre verdict.

## Interpretation boundary

A pass supports a reproducible line-dominant contraction address at these
droplet handovers. It does not prove universal Irrationality Di-ARA, establish
fixed irrational constants, or show that the geometric address causes
coalescence. A failure means this development-derived geometric signature did
not transfer to the four held-out fibre events.
