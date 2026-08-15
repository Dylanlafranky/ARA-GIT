# T383 — 7.5 child cycles before the parent pole

Date frozen: 2026-08-14  
Status: exploratory, post-T382 observation  
Parent source: T382 RAL Silver population fit

## Discovery statement

In the T382 visual, the 63 G candidate child appears to complete about 7.5
native cycles while the population parent visually settles near its `2` pole.
The observation was made after T382 outcome inspection and cannot confirm
itself.

Using the already frozen T382 cadence and origin, the exact 63 G 7.5-cycle
landmark is:

- `t_star = 8.6258334927 μs`;
- `xP_star = 1.9608580375`;
- parent completion fraction `xP_star / 2 = 0.9804290187`.

This common parent coordinate is frozen before calculating the comparison-field
phases.

## Two claims kept separate

### H1 — literal count invariance

At `xP_star`, every comparison field has accumulated approximately 7.5 child
cycles.

This is the literal reading of the visual. It fails if the accumulated cycle
count changes materially with field.

### H2 — child-pole phase locking

Whole child cycles may differ, but the fractional phase at `xP_star` remains
near one half-cycle:

\[
n_C(t_*)\bmod1\approx0.5,
\]

equivalently

\[
x_C(t_*)=1-\cos(2\pi n_C)\approx2.
\]

This is the ARA-native version because completed whole cycles coarse-grain away
while the pole position remains.

## Primary comparison cohort

- Discovery only: 63 G (`EMU00066578`).
- Comparisons: 160 G (`EMU00066579`) and 400 G (`EMU00066580`).
- 20/25 G calibration and validation runs are secondary context because they
  participated in cadence selection.
- 1000/2000/4000 G runs remain out-of-band diagnostics.

No cadence, origin, parent lifetime, field, or landmark is refitted.

## Frozen gates

H1 passes only if every comparison cycle count lies within `±0.25` cycles of
7.5.

H2 passes only if:

1. every comparison fractional phase is within `1/8` cycle (`π/4`) of `0.5`;
2. the comparison circular mean is closer to `0.5` than to `0`, `0.25`, or
   `0.75` cycles;
3. the mean pole score `-cos(2πf)` is positive;
4. the result beats matched random-origin and mirrored-origin controls.

## Boundary

T382 did not qualify the 96-detector relation as a stable physical child. T383
therefore tests the internal geometry of the frozen candidate construction. A
pass would be a replication target for a new transverse-field source, not a
physical neutrino-timing result. A failure rejects this specific 7.5/pole-lock
interpretation without altering the successful T382 population parent.
