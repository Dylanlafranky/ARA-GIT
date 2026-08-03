# Q59 — cross-rung pentagonal-twist test

Date: 1 August 2026 (Australia/Brisbane)  
Status: **NOT SUPPORTED for a fixed 72°/144° pentagonal screw; reproducible high-angle separation remains descriptive**

## Plain-language result

We tested Dylan's proposed picture directly: each local sphere/circle keeps
its own shape, while moving from the `7.5` child rung to the `15` parent rung
twists the same-phase edge around the sphere by a pentagonal step.

The first public archive was allowed to choose between the two predeclared
pentagon possibilities:

- `72°`: one pentagon edge step;
- `144°`: the same-phase pentagon diagonal.

Greedy selected `72°`. We wrote and hashed that choice before opening the
Landmax replication archive.

Landmax did not reproduce a fixed 72° screw. Its whole-grid median angles
were about `80.26°` for Phase A and `80.43°` for Phase B. Those values are
between the pentagon-edge `72°` and perpendicular `90°` controls. `72°` was
nominally the nearest registered landmark to the whole-grid medians, but the
advantage was small, most individual grid cells were outside the frozen
`72° ± 8°` band, and the same closeness appeared at least as readily when the
parent/child family labels were permuted.

So the honest conclusion is:

> This quantum relation-space cut contains a reproducible, roughly
> quarter-turn parent/child separation, but it does not identify that turn as
> a pentagonal cross-rung screw.

## Frozen method

The source is the two public Q42 simulator archives from Zenodo DOI
`10.5281/zenodo.16753415`. The fixed identities were:

- child rung: Q42 `two_turn_7_5` cadence family;
- parent rung: Q42 `one_turn_15` cadence family;
- Phase A: qualifying increasing half-wave;
- Phase B: the immediately following qualifying decreasing half-wave;
- local ARA grid: `x=0.2,0.4,...,1.8`.

Q58 had tested only the magnitude ratio. Q59 retained the full direction of
the unnormalised connected-correlation matrix. At each matched seed, phase
and local coordinate it calculated

\[
\alpha
=
\cos^{-1}\!\left(
\frac{\langle C_P,C_C\rangle_F}
     {\lVert C_P\rVert_F\lVert C_C\rVert_F}
\right).
\]

This is a genuine directional comparison. Positive rescaling changes the
magnitude but not the angle, and a common orthogonal basis change leaves the
Frobenius angle unchanged.

The public states are Bell-diagonal: all off-diagonal correlation entries are
exactly zero and `Cxx=Cyy`. The full matrix direction therefore lies in an
effective two-coordinate plane. That makes the calculation especially clean,
but it also means this archive cannot display an arbitrary three-dimensional
spatial twist. Q59 tests the proposed pentagon in **correlation space**, not a
literal pentagonal edge in physical space.

The data-quality gate passed with `2,180`/`2,287` eligible lineages,
`35,423`/`38,337` qualifying cycles and `608,452`/`658,479` fixed-coordinate
crossings in Greedy/Landmax. Every reported cell retained at least `93`
matched seeds; the smallest compared parent and child norms were
`0.000200714` and `0.0000248485`, safely above the frozen near-zero limit.

## Calibration and untouched replication

Greedy calibration gave:

| Candidate | Combined mean absolute error |
|---|---:|
| 72° | 11.5417° |
| 144° | 62.5361° |

The calibration therefore locked `72°`. Its best signed model was
co-rotating negative, but even on Greedy that handedness fit was weak
(`68.8032°` mean circular error). The calibration lock was then written and
hashed before Landmax was loaded.

Landmax returned:

| Phase | Cells inside 72° ± 8° | Mean absolute 72° error | Whole-grid median | Seed-bootstrap 95% interval |
|---|---:|---:|---:|---:|
| A | 2/9 | 8.26095° | 80.26276° | 76.60482°–83.79490° |
| B | 4/9 | 9.99221° | 80.42711° | 76.26653°–83.57440° |

Both phases failed the frozen `7/9` cell gate and Phase B failed the `8°`
mean-error gate. The complete signed screw failed much more clearly:

- signed mean circular error: `57.8667°`;
- signed cells within `10°`: `0/18`.

The sign failure is informative. Individual seed angles occur with both
clockwise and counter-clockwise signs. Their unsigned magnitudes remain high,
while the population signed medians collapse toward zero. This is compatible
with a two-handed population mixture, not one stable screw handedness.
Across all nine coordinates, positive-sign shares were `48.57%`/`48.57%`
for Greedy A/B and `47.55%`/`44.95%` for Landmax A/B. The corresponding
median absolute signed angles were `81.65°`, `81.40°`, `80.44°` and
`79.97°`, respectively.

## Controls

Landmax's combined mean absolute landmark errors were:

| Landmark | Mean absolute error |
|---|---:|
| pentagon edge 72° | 9.1266° |
| perpendicular 90° | 10.9527° |
| hexagon edge 60° | 19.8984° |
| pentagon interior 108° | 28.1016° |
| hexagon diagonal 120° | 40.1016° |
| golden angle 137.507764° | 57.6094° |
| pentagon diagonal 144° | 64.1016° |

The nearest-landmark result alone is not enough to claim a pentagon:

- same-phase target error was `9.12658°`;
- wrong-phase target error was slightly smaller at `8.33151°`;
- a `1,999`-draw family-label null had median error `6.78286°`, better than
  observed;
- the one-sided no-worse-than-null probability was `0.822`.

Thus the `~80°` angle is not specific to the declared parent/child labels in
this representation. A near-perpendicular geometry or generic separation of
the two aggregated Bell-diagonal populations is a more economical reading.

## What did replicate

The broad unsigned curve was reproducible across archives:

- greedy-versus-Landmax mean absolute cell difference: `5.16135°` for Phase
  A;
- greedy-versus-Landmax mean absolute cell difference: `8.82279°` for Phase
  B.

Both met the frozen `10°` cross-archive agreement criterion. Away from the
least stable low-`x` cells, both phases sat mostly around `77°–86°` and bent
toward approximately `79°–80°` near `x=1.8`.

That is real descriptive structure. It should not be renamed a new `80°`
constant after seeing it, because the labels and wrong-phase controls do not
show that this structure is uniquely the parent/child handover.

## ARA and conventional readings side by side

| ARA reading | Measurement-language reading |
|---|---|
| Cross-rung direction is not captured by the scalar magnitude alone. | Q59 used the angle between full connected-correlation matrices rather than their Frobenius norms. |
| The proposed pentagonal edge/diagonal twist did not lock. | Neither the frozen 72° nor 144° model passed untouched replication and controls. |
| Both handednesses are present in the population. | Signed seed angles occur on both sides, so signed medians approach zero while unsigned medians remain near 80°. |
| A broad cross-rung turn replicated. | Greedy and Landmax unsigned profiles agreed within 5.16°–8.82° by phase. |
| The turn is not yet identifiable as the ARA pentagon. | Wrong-phase and family-permutation controls were equally or more pentagon-like. |

## Framework implication

Q59 is evidence against this exact operational statement:

\[
C_{P,s}(x)
\approx
\operatorname{Twist}_{72^\circ\text{ or }144^\circ}
\big(C_{C,s}(x)\big)
\quad
\text{with one stable screw orientation}.
\]

It does not disprove the mathematical regular-pentagon construction, the
factor-two `7.5 → 15` cadence, or every possible physical cross-rung handover.
It does show that the pentagon cannot be inferred merely because the observed
angle is closer to `72°` than to a short list of landmarks.

The next scientifically clean pentagon test would use an independent public
system with non-diagonal directional data and explicitly observed child,
parent and grandparent tiers. The `72°/144°` targets should be frozen again
without fitting an `~80°` correction. A separate exploratory model may study
the replicated curved high-angle profile, but it must remain distinct from a
confirmatory pentagon claim.

## Validation and reproduction

The independent validator passed every check:

- frozen protocol and calibration-lock hashes;
- all seed-level matrix angles;
- all grid medians and `10,000`-draw bootstrap intervals;
- the Greedy target and handedness selection;
- `128` direct source-cache interpolation checks with zero mismatch; and
- an independently regenerated family-label null (`p=0.8265` versus stored
  `0.8220`; maximum null-quantile difference `0.02873°`).

From `analysis/quantum`:

```powershell
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe q59_cross_rung_pentagonal_twist.py
F:\SystemFormulaFolder\.venv_ara_verify\Scripts\python.exe q59_validate_cross_rung_pentagonal_twist.py
```

Primary artifacts:

- `Q59_CROSS_RUNG_PENTAGONAL_TWIST_PROTOCOL_v1_FROZEN.md`
- `Q59_CROSS_RUNG_PENTAGONAL_TWIST_CALIBRATION_LOCK.json`
- `Q59_CROSS_RUNG_PENTAGONAL_TWIST_RESULTS.json`
- `Q59_CROSS_RUNG_PENTAGONAL_TWIST_GRID_SUMMARY.csv`
- `Q59_CROSS_RUNG_PENTAGONAL_TWIST_SEED_ANGLES.csv`
- `Q59_CROSS_RUNG_PENTAGONAL_TWIST.png`
- `Q59_CROSS_RUNG_PENTAGONAL_TWIST.svg`
- `Q59_CROSS_RUNG_PENTAGONAL_TWIST_VALIDATION.json`

The deterministic crossing- and pair-level files are intentionally ignored
by Git because they total roughly `32 MB` compressed. The runner reconstructs
them from the public source caches before validation.
