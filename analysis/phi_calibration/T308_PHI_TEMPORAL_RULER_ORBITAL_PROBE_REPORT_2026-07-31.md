# T308 — Phi Temporal-Ruler Orbital Probe

**Date:** 31 July 2026  
**Frozen verdict:** **NOT SUPPORTED BY THIS PROBE**

## Plain-language result

Phi did not uniquely outperform the declared alternative temporal rulers across both orbital systems. This particular way of turning Phi-spaced time slices into an information lock is therefore not supported.

This was a probe of one specific interpretation: two earlier, geometrically
spaced time slices were used to reconstruct a third orbital state. The
physical orbit was not treated as climbing a structural octave.

## Post-result methodology diagnosis

The metric family did not reveal an interior preferred multiplier. In both systems, raw phase error increased monotonically with λ, while the distance-normalised curvature error decreased monotonically with λ. The exploratory sweep then selected its upper boundary (about 2.8). Phi's fourth-place position is therefore the middle of two opposing monotonic effects, not evidence that the data naturally settled on another special constant. This confirms the user's pre-run concern that the probe was reasonable but probably not the best operationalisation of the geometry.

The frozen verdict is retained. This diagnosis limits its scope: the result
is a rejection of this reconstruction as evidence for Phi, not strong
evidence that no Phi temporal relation exists.

## Fixed-candidate evaluation results

| System | Ruler | λ | Phase error | ARA error | Curvature-normalised error | A/B accuracy | Curvature rank |
|---|---:|---:|---:|---:|---:|---:|---:|
| Moon relative to Earth | 1.25 | 1.250000 | 0.03979432 | 0.00902700 | 0.001604941062 | 0.8431 | 7 |
| Moon relative to Earth | sqrt2 | 1.414214 | 0.07339376 | 0.01768829 | 0.001378568547 | 0.7751 | 6 |
| Moon relative to Earth | 1.5 | 1.500000 | 0.08831301 | 0.02192335 | 0.001292508686 | 0.7521 | 5 |
| Moon relative to Earth | phi | 1.618034 | 0.10584910 | 0.02612233 | 0.001202612985 | 0.7457 | 4 |
| Moon relative to Earth | 1.75 | 1.750000 | 0.12077367 | 0.03084473 | 0.001125844593 | 0.7490 | 3 |
| Moon relative to Earth | 2 | 2.000000 | 0.14448063 | 0.04004876 | 0.001017652952 | 0.7711 | 2 |
| Moon relative to Earth | e | 2.718282 | 0.19364165 | 0.06602001 | 0.000902337123 | 0.7999 | 1 |
| Earth relative to Sun | 1.25 | 1.250000 | 0.01138654 | 0.00173694 | 2.967081992e-06 | 0.8148 | 7 |
| Earth relative to Sun | sqrt2 | 1.414214 | 0.02204660 | 0.00273370 | 2.509141431e-06 | 0.7587 | 6 |
| Earth relative to Sun | 1.5 | 1.500000 | 0.02704491 | 0.00328012 | 2.369389687e-06 | 0.7301 | 5 |
| Earth relative to Sun | phi | 1.618034 | 0.03292003 | 0.00396611 | 2.168530712e-06 | 0.7095 | 4 |
| Earth relative to Sun | 1.75 | 1.750000 | 0.03805138 | 0.00505247 | 1.929404521e-06 | 0.7324 | 3 |
| Earth relative to Sun | 2 | 2.000000 | 0.04548230 | 0.00706590 | 1.794929194e-06 | 0.7589 | 2 |
| Earth relative to Sun | e | 2.718282 | 0.06028031 | 0.01264236 | 1.628554377e-06 | 0.7924 | 1 |

## Bootstrap comparison

- **Moon relative to Earth:** best fixed control `e`; Phi minus control = `0.0002983303725`; 95% block-bootstrap interval `[0.0002844396914, 0.0003130848439]`; P(Phi lower) = `0.0000`.
- **Earth relative to Sun:** best fixed control `e`; Phi minus control = `5.562372011e-07`; 95% block-bootstrap interval `[5.007216483e-07, 6.344991382e-07]`; P(Phi lower) = `0.0000`.

## Horizon stability

| System | H/P | Phi curvature rank | Phi / best-control error |
|---|---:|---:|---:|
| Moon relative to Earth | 0.250 | 5/7 | 1.0447 |
| Moon relative to Earth | 0.375 | 2/7 | 1.0173 |
| Moon relative to Earth | 0.500 | 4/7 | 1.0564 |
| Moon relative to Earth | 0.750 | 4/7 | 1.2016 |
| Moon relative to Earth | 1.000 | 4/7 | 1.4426 |
| Moon relative to Earth | 1.500 | 4/7 | 2.2547 |
| Moon relative to Earth | 2.000 | 4/7 | 1.7100 |
| Earth relative to Sun | 0.250 | 4/7 | 1.0191 |
| Earth relative to Sun | 0.375 | 4/7 | 1.0489 |
| Earth relative to Sun | 0.500 | 4/7 | 1.0906 |
| Earth relative to Sun | 0.750 | 4/7 | 1.2247 |
| Earth relative to Sun | 1.000 | 4/7 | 1.4510 |
| Earth relative to Sun | 1.500 | 4/7 | 2.2163 |
| Earth relative to Sun | 2.000 | 4/7 | 1.7114 |

## What this means for ARA

The null is narrow but useful: merely placing two prior observations on a Phi ladder is not enough to recover the next ARA state of these orbits. A better Phi test would need a separately declared handover or coupling observable rather than temporal spacing alone.

## Boundaries

- The result concerns one frozen reconstruction rule, not every possible
  meaning of a Phi handover or temporal-tension path.
- The orbit was reduced through ecliptic longitude and
  `x = 1 − cos(Δθ)`. A different physically declared ARA cut is a new test.
- Daily vectors require linear interpolation for fractional-day Phi slices.
- Daily anchors overlap heavily. The reported uncertainty therefore uses
  30-day block resampling rather than treating every row as independent.
- The continuous multiplier sweep is exploratory and cannot replace the
  frozen fixed-candidate verdict.

## Reproduction

```powershell
python t308_phi_temporal_ruler_orbital_probe.py --fetch
python validate_t308_phi_temporal_ruler_orbital_probe.py
```

Source: NASA/JPL Horizons geometric vector tables retained under
`analysis/phi_calibration/data/t308/`.
