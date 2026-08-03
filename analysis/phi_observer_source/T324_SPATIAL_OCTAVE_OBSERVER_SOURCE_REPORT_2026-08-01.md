# T324 — Literal spatial-octave observer–source test

**Date:** 1 August 2026  
**Frozen verdict:** **NOT SUPPORTED — 2/5 formal gates**  
**Scientific interpretation:** **no absolute Phi proximity; literal
time-of-flight is absent from the stored archive representation**  
**Validation:** **PASS — 59/59 independent checks**

## Plain-language outcome

T324 corrected the main limitation of T323: instead of calling `f -> 2f` an
octave, it compared a measured source and observer at literal doubled
distances:

- `0.5 -> 1 m`;
- `1 -> 2 m`;
- with `2 -> 3 m` as a non-octave control.

The stored KEMAR transfer functions did **not** form a `36 degree` Phi
direction. The two octave medians were approximately `2.44 degrees` and `0.46
degrees`, both closest to direct alignment at `0 degrees`. Only about `0.46%`
of eligible octave events lay within five degrees of the registered Phi angle,
whereas `85.4%` and `74.1%` respectively lay within five degrees of zero.

The offset-invariant increment ratio also did not settle near Phi:

\[
\rho=
\frac{|\psi_{2m}-\psi_{1m}|}
     {|\psi_{1m}-\psi_{0.5m}|}.
\]

Its median was `0.2277` by event and `0.1525` by path. Phi predicts `1.618` and
ordinary unaltered propagation predicts `2`. The observed coordinate was far
below both. Only `3.88%` of events were within 10% of Phi.

The most important data-quality finding explains why neither propagation
target appeared. The archive contains `Data.Delay = 0`, no
`MeasurementAudioLatency`, and its stored impulses remain in nearly the same
sample region at every radius. At `44.1 kHz`, literal free-field travel would
move by approximately `64.3`, `128.6`, and `128.6` samples across the three
registered distance steps. The observed median peak shifts were only `4`, `0`,
and `5` samples.

Therefore:

> The frozen test does not support Phi in the radius-dependent transfer shape
> that the file retains. However, this archive cannot adjudicate the literal
> lighthouse–boat time-of-flight version because that distance delay has been
> removed or normalized before publication.

This is not a reason to replace the frozen verdict. It is the boundary on what
the verdict means.

## Frozen measurements

For each direction, ear, frequency, and doubled-radius step,

\[
\Delta_{\parallel}=\psi_r,
\qquad
\Delta_{\rm rung}=\psi_{2r}-\psi_r,
\]

\[
\theta=
\operatorname{atan2}
\left(
|\Delta_{\rm rung}|,
|\Delta_{\parallel}|
\right).
\]

The registered candidates included:

- `36 degrees`: Phi projection;
- `45 degrees`: ordinary doubled-distance propagation;
- `54 degrees`: reversed-axis Phi;
- `0 degrees`: direct alignment.

The implementation inherited T323's existing definition of a free path angle:
the arithmetic mean of that path's eligible event angles. This resolves an
unstated implementation detail without selecting a new estimator from the
observed T324 result.

The second measurement cancelled any phase term common to all radii:

\[
\rho=
\frac{|\psi_{2m}-\psi_{1m}|}
     {|\psi_{1m}-\psi_{0.5m}|},
\qquad
\eta=
\frac{|\psi_{3m}-\psi_{2m}|}
     {|\psi_{2m}-\psi_{1m}|}.
\]

The ideal free-field implementation recovered exactly:

| Quantity | Analytic result |
|---|---:|
| `theta(0.5 -> 1 m)` | `45 degrees` |
| `theta(1 -> 2 m)` | `45 degrees` |
| `theta(2 -> 3 m)` | `26.565051 degrees` |
| `rho` | `2` |
| `eta` | `1` |

That confirms the formulas and distinguishes the measured archive result from
an implementation error.

## Public data

The frozen source was the
[official SOFA test-archive](https://sofacoustics.org/data/sofatoolbox_test/)
file `qu_kemar_anechoic_radius_0.5_1_2_3_m.sofa`. It contains:

- `360` azimuths at zero elevation;
- four exactly matched radii: `0.5`, `1`, `2`, and `3 m`;
- two receiver ears;
- `2048` samples per impulse response;
- sampling rate `44,100 Hz`;
- `1,440` measurement records in total.

Every direction had one and only one record at each radius. No path was lost to
the registered minimum-frequency rule.

Source SHA-256:

`4d11740336d936ad129473029fadce5320f7455f0475634fed4d5519b2878a42`

## Projection-angle results

| Step | Eligible events | Median event angle | Median free path angle | Median ARA `x` | Best frozen target |
|---|---:|---:|---:|---:|---|
| `0.5 -> 1 m` | 249,225 | 2.6860° | 2.4377° | 1.99780 | direct `0°` |
| `1 -> 2 m` | 237,000 | 0.5101° | 0.4562° | 1.99992 | direct `0°` |
| `2 -> 3 m` | 250,314 | 4.0467° | 5.4025° | 1.99501 | `26.565°` control, but still far below it |

Median path RMS target loss for the two spatial octaves was:

| Target | `0.5 -> 1 m` | `1 -> 2 m` |
|---|---:|---:|
| direct `0°` | **2.623°** | **0.540°** |
| Phi `36°` | 33.576° | 35.545° |
| ordinary `45°` | 42.573° | 44.545° |
| reversed Phi `54°` | 51.571° | 53.544° |

Observed Phi loss did not beat the broken-direction relation. The paired
observed-minus-broken intervals crossed zero at both octaves:

- `0.5 -> 1 m`: `+0.00056°`, 95% interval
  `[-0.00118,+0.00329]`;
- `1 -> 2 m`: `+0.00044°`, interval
  `[-0.00356,+0.00854]`.

The measured source direction therefore did not preserve a Phi relation better
than the frozen direction-breaking control.

![T324 spatial-octave result](F:/SystemFormulaFolder/GIT/ARA-GIT/analysis/phi_observer_source/T324_SPATIAL_OCTAVE_OBSERVER_SOURCE.png)

## Offset-invariant ratio results

| Quantity | Measured median by event | Measured median by path | Registered physical values |
|---|---:|---:|---|
| `rho` | 0.22769 | 0.15247 | Phi `1.618`; ordinary `2` |
| `eta` | 7.25212 | 10.69446 | equal-step ordinary `1` |

The two ears returned the same qualitative result:

| Ear | Median `rho` | Median `eta` |
|---|---:|---:|
| 0 | 0.14569 | 11.03764 |
| 1 | 0.16046 | 9.52934 |

These ratios are not small perturbations around Phi or ordinary propagation.
They show that the first retained radius change dominates the second, while the
third retained change becomes much larger again. That is a property of the
stored radius-dependent HRTF shape, not a constant cross-rung multiplier.

## Why two formal gates passed without supporting Phi

The frozen gate table returned `2/5` rather than `0/5`:

| Gate | Formal result |
|---|---|
| G1 — Phi angle specificity | Failed |
| G2 — closer to 36° than 45° or 54° | Passed |
| G3 — beats broken direction | Failed |
| G4 — `rho` closer to Phi than 2 | Passed |
| G5 — non-octave and timing robustness | Failed |

G2 and G4 are weak **relative-ranking** gates. A value near zero is
automatically closer to `36` than to `45` or `54`, and closer to `1.618` than
to `2`, even though it is nowhere near Phi. This is exactly what happened:

- octave angles near `0°` formally preferred `36°` over the two still larger
  alternatives;
- `76.3%` of `rho` events lay below Phi, so the log-loss advantage over `2`
  became the constant target separation `log(phi)-log(2)`, not concentration
  around Phi.

The frozen gates remain unchanged in the record. The scientific interpretation
does not promote those two passes as Phi evidence. A future protocol should
require an absolute tolerance or an equivalence interval around the target in
addition to relative ranking.

## Arrival-time audit

| Step | Expected direct delay shift | Observed median peak shift | Observed 10% onset shift |
|---|---:|---:|---:|
| `0.5 -> 1 m` | 64.29 samples | 4 samples | 4 samples |
| `1 -> 2 m` | 128.57 samples | 0 samples | 0 samples |
| `2 -> 3 m` | 128.57 samples | 5 samples | 5 samples |

Median stored peak samples were `64`, `68`, `68`, and `73` at `0.5`, `1`, `2`,
and `3 m`. The archive's impulses are therefore aligned or otherwise stripped
of most geometric travel time. `Data.Delay` is identically zero and there is no
separate audio-latency field from which to restore it.

This is a stronger limitation than ordinary observational noise: one of the
two quantities the literal lighthouse test needs is absent from the published
representation.

## Bounded conclusion

T324 establishes three things:

1. The ARA observer–source construction can be tested on genuinely matched
   physical radii without reusing a child inside its own parent.
2. The retained radius-dependent KEMAR transfer shape does not select Phi; it
   lies near the direct axis and has nonconstant increment ratios.
3. This particular SOFA archive cannot test the full literal propagation-time
   hypothesis because its stored responses do not preserve the distance-based
   time of flight.

The proper next version would require raw, unsynchronised multi-distance
impulse recordings with one documented clock origin, or a source archive that
publishes the removed radius-specific delays. It should retain the
offset-invariant ratio and add absolute target-proximity gates.

## Reproduction

```powershell
python -m pip install -r requirements.txt
python t324_spatial_octave_observer_source.py --fetch
python validate_t324_spatial_octave_observer_source.py
```

Primary records:

- `T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_PROTOCOL_v1_FROZEN.md`
- `results/T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_RESULTS.json`
- `results/T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_VALIDATION.json`
- `results/T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_PATHS.csv`
- `results/T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_RATIOS.csv`
- `results/T324_SPATIAL_OCTAVE_OBSERVER_SOURCE_FREQUENCIES.csv`
- `T324_SPATIAL_OCTAVE_OBSERVER_SOURCE.png`
