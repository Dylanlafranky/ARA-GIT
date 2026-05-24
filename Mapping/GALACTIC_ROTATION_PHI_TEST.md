# Galactic Rotation Phi Test

**Date:** 2026-05-24

This test checks whether the atlas entry `Galactic rotation MW = phi` is supported by actual Milky Way rotation-curve geometry.

## Source

Data comes from Table 1 of:

> The rotation curve of the Milky Way measured by classical Cepheids from Gaia DR3  
> `https://academic.oup.com/mnras/article/546/2/stag011/8416425`

The table gives 12 binned circular velocities from `6.58` to `17.58 kpc`, based on 903 Gaia DR3 classical Cepheids.

## Test

The old atlas value was an archived scaffold, not a measurement. The rerun separates:

- **Period anchor:** orbital period near the solar radius.
- **Circular carrier ARA:** a pure near-circular orbit has no observed build/release asymmetry by itself, so its neutral ARA is `1.0`.
- **Epicyclic coupling ratio:** using local rotation-curve slope `beta = d ln(V) / d ln(R)`, the near-circular radial/azimuthal ratio is `kappa/Omega = sqrt(2 * (1 + beta))`.

Phi would require a distinctly rising local rotation curve:

```text
beta for kappa/Omega = phi: 0.309
```

The observed curve is roughly flat to slightly falling:

```text
global beta: -0.042
median beta: -0.110
```

## Result

```text
solar-radius orbital period: 220.25 Myr
atlas 230 Myr period error: 4.239%
pure circular carrier ARA: 1.000
global kappa/Omega: 1.385
median kappa/Omega: 1.334
global period slope dlnT/dlnR: 1.042
median period slope dlnT/dlnR: 1.110
local kappa points within 0.10 of phi: 0 / 12
local period-slope points within 0.10 of phi: 0 / 12
```

## Interpretation

The rough Milky Way galactic-year period is supported near the solar radius.

The phi ARA assignment is **not** supported by this rotation-curve test. The circular carrier maps to balanced ARA `1.0`, and the measured epicyclic coupling is closer to the flat-curve `sqrt(2)` geometry than to phi.

Atlas action taken:

- `mapped_scale_galactic_rotation_mw` now uses ARA `1.0`.
- The archived phi prior is preserved only as metadata: `archived_prior_ara = phi`.
- The node source is now `Mapping/galactic_rotation_phi_test_result.json`.
