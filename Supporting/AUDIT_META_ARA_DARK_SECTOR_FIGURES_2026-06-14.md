# Audit: Meta-ARA Dark Sector Figures

Date: 2026-06-14

Audited source:

- `META_ARA_DARK_SECTOR.pdf` (canonical document)
- Archived source document and scripts `243BL` through `243BL8`

This audit does not modify the source document.

## Overall finding

The central formula is calculated correctly:

```text
DM = 1 / (phi^2 + 1 + phi^(-7/2)) = 0.2629074992
DE = phi^2 * DM                         = 0.6883007689
b  = DM / phi^(7/2)                    = 0.0487917318
DE + DM + b                            = 1.0000000000
```

Most percentages in the PDF reproduce from the rounded comparison values it
uses. There are, however, three material numerical/presentation corrections:

1. `phi^6.1` is `18.8289`, not `19.2`.
2. The displayed "total matter" comparison omits the neutrino contribution
   included in Planck's published `Omega_m`.
3. The `243BL6` result of `0.43%` is a best-fit exponent result, not the fixed
   `7/2` formula result.

Several "additional predictions" are correct calculations but are dependent
re-expressions of the same Planck parameters, not independent observations.

## Central results table

Using the PDF's rounded comparison values:

| Component | Formula | PDF comparison | Recalculated error |
|---|---:|---:|---:|
| Dark energy | 0.6883008 | 0.6850 | 0.4819% |
| Dark matter | 0.2629075 | 0.2650 | 0.7896% |
| Baryons | 0.0487917 | 0.0493 | 1.0310% |
| Matter (`DM+b`) | 0.3116992 | 0.3143 | 0.8275% |

The stated `0.77%` average is correct if it means the mean error across the
three independent components `DE`, `DM`, and `b`:

```text
mean independent-component error = 0.7675%
```

If all four displayed rows are averaged, including the dependent `DM+b` row,
the result is `0.7825%`, which rounds to `0.78%`.

Recommended wording:

> Mean error across the three independently displayed components: 0.77%.

## Planck convention check

For the Planck 2018 `TT,TE,EE+lowE+lensing` baseline, representative published
values are:

```text
H0             = 67.36
Omega_b h^2    = 0.02237
Omega_c h^2    = 0.1200
Omega_m        = 0.3153
Omega_Lambda   = 0.6847
```

Using `h=0.6736` gives:

```text
Omega_b = 0.0493017
Omega_c = 0.2644704
Omega_m - Omega_b - Omega_c = 0.0015279
```

The final term is principally the matter contribution assigned to massive
neutrinos in the baseline model. Consequently:

- If `DM` means cold dark matter, compare it with `Omega_c`.
- If `DM` means all non-baryonic matter, compare it with
  `Omega_m - Omega_b = 0.2659983`.
- Do not label `DM+b = 0.3143` as Planck's full `Omega_m` without stating that
  the neutrino contribution has been excluded.

Against the exact baseline values above, the formula errors are approximately:

| Quantity | Error |
|---|---:|
| Dark energy | 0.526% |
| Cold dark matter | 0.591% |
| Baryons | 1.034% |
| Full total matter | 1.142% |

The central match remains close, but "every component within 1%" is not
strictly true under this convention. "Mean component error below 1%" is true.

## Additional prediction table

### Hubble value

The PDF calculation is correct:

```text
67.4 * (1 + phi^-5) = 73.4775
```

This is `0.65%` from `73.0` and `0.60%` from the SH0ES baseline
`73.04 +/- 1.04`.

The phrase "Hubble tension = 1/phi^5" needs care. `1/phi^5` is being used as a
fractional frame correction to `H0`; it is not the conventional statistical
definition of the Hubble tension.

### Transition redshift

For a flat matter-plus-cosmological-constant model:

```text
z_transition = (2*Omega_Lambda/Omega_m)^(1/3) - 1
```

Using the PDF's `0.685/0.315` gives `0.63231`, so the reported `2.3%`
difference from `1/phi = 0.61803` is correct.

However, `0.632` is a value inferred from the same Planck parameters, not a
separate direct observation. Label it "Planck Lambda-CDM inferred".

### ARA_space, DM/baryons, and DE/DM

The arithmetic is correct:

```text
0.3143 / 0.6850 = 0.458832
0.2650 / 0.0493 = 5.375254
0.6850 / 0.2650 = 2.584906
```

These are all derived from the same component values used in the main table.
They are useful consistency checks, but not three additional independent
predictions.

## Incorrect or ambiguous figures

### `phi^6.1 approximately 19.2`

This is numerically incorrect:

```text
phi^6.1 = 18.828885
```

An exponent producing `19.2` is approximately:

```text
log_phi(19.2) = 6.14056
```

Using the exact Planck baseline and defining dark as
`Omega_Lambda + Omega_c`, the dark/light ratio is approximately `19.2523`,
corresponding to exponent `6.1462`.

Recommended correction:

> Dark/light is approximately 19.25:1, or `phi^6.15` descriptively.

Do not simultaneously state `phi^6.1` and `19.2` as an equality.

### Radiation `Omega approximately 5e-5`

`5e-5` is approximately the present photon density, not total radiation once
relativistic neutrinos are included. Label the row `Photons`, or use roughly
`9e-5` for total present relativistic radiation under the standard convention.

### Baryon split failure `73-79%`

For the explicit PDF comparison value `Omega_m=0.3143`:

```text
b_pred = Omega_m / (1 + phi^2) = 0.0868704
error versus 0.0493 = 76.21%
```

The broad `73-79%` range may be obtainable from different input datasets, but
the document does not define them. Replace the range with `76.2%` for the
stated inputs, or cite each dataset producing the range.

## Secondary arithmetic checks

These figures are correct for the values selected in the PDF:

```text
golden angle = 360/phi^2 = 137.5078 degrees
7 - 4*phi = 0.527864
2*phi = 3.236068
(7 - 4*phi)/2 = 0.263932
2*phi + (7 - 4*phi)/2 = 3.5 exactly
phi^3.5 = 5.388362
```

The arithmetic identity is exact. The interpretation of the remainder as a
physical "singularity cost" is a hypothesis, not established by the identity.

The revised octave paragraph is also arithmetically correct:

```text
left span  = 3.5 - (-phi) = 5.118034
right span = 6.1 - 3.5    = 2.600000
ratio      = 1.968475
distance from 2 = 1.576%
distance from phi = 21.658%
```

This result depends on the selected rounded exponent `6.1`; it should be
presented as a descriptive pattern, not a parameter-free confirmation.

The failed redshift comparison also reproduces:

```text
3402 / 1089.90 = 3.12139
error from phi^2 = 19.23%
error from pi    = 0.64%
```

The exact redshift values vary slightly with the Planck likelihood combination,
but the conclusion does not change.

The era-duration ratio reproduces from the script's rounded ages:

```text
(7.7 - 0.000047) / (13.8 - 7.7) = 1.26229
error from phi = 21.99%
```

This is a rough derived chronology, not a precision measurement.

## Fitting provenance

The PDF's fixed formula uses `alpha=7/2=3.5` and has the stated independent
component mean error of `0.77%`.

Script `243BL6_coupled_grid.py` first searches:

```text
DM/b = phi^alpha
```

over `alpha=0.5...5.0`. The best fit is:

```text
alpha approximately 3.4773
mean error approximately 0.424%
```

Therefore the script-reference statement:

> 243BL6 ... 3-component formula avg Delta = 0.43%

must be labelled "best-fit alpha diagnostic". It is not the result of the
fixed `alpha=3.5` formula.

Likewise, the final expression contains no numerically fitted free parameter
once `2` and `7/2` are fixed, but `7/2` was selected after exploratory scans
and inspection of the observed ratio. A rigorous claim should read:

> The final closed-form expression has no continuously fitted parameters;
> its structural exponents were selected during prior hypothesis development.

## Interpretation issue affecting a numerical prediction

The statement "DM/DE ratio constant across redshift" requires a precise
definition. In standard Lambda-CDM physical densities:

```text
rho_DM scales as a^-3
rho_DE is constant
rho_DE/rho_DM scales as a^3
```

Thus the ordinary density ratio is not constant across redshift. If ARA means
a different normalized coupling coordinate, the document must define that
coordinate and state how it is calculated at each redshift before DESI can
test the prediction.

## Recommended minimum corrections

1. Change `phi^6.1 approximately 19.2` to a numerically consistent statement.
2. Define whether `DM` means cold dark matter or all non-baryonic matter.
3. Compare total matter with Planck `Omega_m=0.3153`, or explicitly label
   `0.3143` as `baryons + chosen DM, excluding neutrinos`.
4. Clarify that `0.77%` averages three independent components.
5. Label the `0.43%` result as fitted-alpha, not fixed-formula.
6. Relabel derived Planck ratios as consistency checks rather than independent
   observations.
7. Replace the undefined `73-79%` baryon error range with the reproducible
   `76.2%` value or provide its dataset-specific derivation.
8. Define the redshift-dependent quantity intended by the "constant DM/DE"
   prediction.

## Primary references

- Planck Collaboration, *Planck 2018 results. VI. Cosmological parameters*:
  https://arxiv.org/abs/1807.06209
- Riess et al., *A Comprehensive Measurement of the Local Value of the Hubble
  Constant...*:
  https://arxiv.org/abs/2112.04510
