# Galactic Structure-Time Phi Test

**Date:** 2026-05-24

Follow-up to `GALACTIC_ROTATION_PHI_TEST.md`.

The previous test found:

```text
Milky Way circular rotation carrier: ARA 1.0
```

This test asks a narrower question:

> If rotation is the balanced carrier, is the time-through-growing-structure layer phi-like?

## Carrier

Using the Gaia DR3 Cepheid rotation-curve result:

```text
solar-neighbourhood radius: 8.48 kpc
circular velocity: 236.54 km/s
Omega_sun: 27.894 km/s/kpc
orbital period: 220.25 Myr
carrier ARA: 1.0
```

## Spiral-Arm Crossing

For an `m`-armed spiral pattern:

```text
P_cross = 2pi / (m * abs(Omega_sun - Omega_pattern))
```

For a four-arm Milky Way, `P_cross = P_orb / phi` requires:

```text
Omega_pattern = 16.61 km/s/kpc
P_cross = 136.12 Myr
```

This is close to the published slow density-wave range of roughly `12-17 km/s/kpc`.

Best measured/range candidate in this test:

```text
candidate: slow_density_wave_broad_upper
Omega_pattern: 17.00 km/s/kpc
P_cross: 140.99 Myr
P_cross / P_orb: 0.640
distance to 1/phi: 0.022
```

So the four-arm spiral structure layer is **phi-plausible**, especially at the upper end of the slow density-wave range. It is not a strict central-value hit.

## Bar Pattern

The bar phi target is:

```text
Omega_bar = phi * Omega_sun = 45.13 km/s/kpc
```

Best measured bar candidate in this test:

```text
candidate: near_side_gaia_vvv
Omega_bar: 41.00 km/s/kpc
Omega_bar / Omega_sun: 1.470
P_bar: 149.85 Myr
distance to phi speed-ratio: 0.148
```

The bar is sub-phi on the central value. Because published bar-pattern estimates have large systematics, the broad range can overlap the phi target, but that should be read as possible rather than supported.

## Interpretation

The clean current reading is:

```text
rotation carrier: supported at ARA 1.0
spiral time-through-structure: phi-plausible, not proved
bar pattern: near-ish but sub-phi on central values
```

This matches the corrected architecture better than forcing phi onto the carrier.

The exact phi target rows are included in the JSON as derived targets only and are excluded from measured-candidate summaries.

## Files

- `Mapping/galactic_structure_time_phi_test.py`
- `Mapping/galactic_structure_time_phi_test_result.json`
