# Frozen protocol - Q7 physical Bell-decoherence trajectory

**Protocol ID:** `Q7-BELL-DECOHERENCE-v1`  
**Ledger ID:** `T266`  
**Frozen:** 24 July 2026, after public-file checksum and schema inspection but before programmatic opening of the
held-out Pauli trajectories  
**Test class:** public-data, partially blinded reanalysis with a known coarse Bell-lifetime result  
**Source:** Steinacker et al. (2025), Nature Communications, DOI `10.1038/s41467-025-57987-0`; data DOI
`10.5281/zenodo.14880901`

## Frozen inputs

- `SuppFigure5a.csv`: Ramsey Pauli projections.
- `SuppFigure5b.csv`: Hahn-echo Pauli projections.
- `MainFigure5b.csv` and `MainFigure5c.csv`: authors' four reported Bell-signal trajectories, retained as an
  external cross-check rather than substituted for the tensor calculation.
- Expected source checksums:
  - `MainFigure5b.csv`: `3991a446f66fc244651dc3c303ea0990`
  - `MainFigure5c.csv`: `fc7cc2a7376d5ca1ca81c91611b38500`
  - `SuppFigure5a.csv`: `c198c156a7aa2235b2c3c35b6a1aaa35`
  - `SuppFigure5b.csv`: `55ff84cddfc6b009fcc626345195af5b`

The supplementary CSV schema is fixed as:

- rows `0:4`: authors' four aggregate projection norms;
- row `4`: separator;
- rows `5:9`: the four Bell-state Pauli vectors;
- eleven columns: increasing wait times;
- each Pauli vector follows
  `II, IX, IY, IZ, XI, XX, XY, XZ, YI, YX, YY, YZ, ZI, ZX, ZY, ZZ`.

Wait coordinates are fixed from the published figure:

- Ramsey: `0.02, 4.02, 8.02, 12.02, 16.02, 20.02, 24.02, 28.02, 32.02, 36.02, 40.02 us`;
- Hahn: `1.00, 1.99, 3.98, 7.94, 15.85, 31.62, 63.09, 125.89, 251.19, 501.18, 1000.00 us`.

Bell-state row order is fixed from the source legend:
`Phi-plus, Phi-minus, Psi-plus, Psi-minus`.

## Frozen reconstruction

For every state and wait:

1. linearly reconstruct
   \[
   \rho_{\rm lin}=\frac14\sum_{i,j\in\{I,X,Y,Z\}}
   \langle ij\rangle\,\sigma_i\otimes\sigma_j;
   \]
2. Hermitize it;
3. project its eigenvalues onto the unit probability simplex while preserving eigenvectors;
4. reconstruct the physical density matrix;
5. recompute the physical Pauli coefficients and the \(3\times3\) correlation tensor;
6. calculate descending singular values \(s_1\ge s_2\ge s_3\);
7. calculate \(S_{\max}=2\sqrt{s_1^2+s_2^2}\);
8. count strong relation axes with the inherited Q6B threshold \(s_i\ge0.50\).

No threshold may be tuned after target opening.

## Development and target split

- Development: the first five Ramsey waits (`0.02` through `16.02 us`).
- Primary target: the final six Ramsey waits (`20.02` through `40.02 us`).
- Intervention replication: the complete Hahn-echo trajectory. Its coarse lifetime extension is already disclosed
  by the paper, so it is scored as external-control replication, not a blind target.

## Frozen gates

All primary gates `P1-P8` must pass for the primary verdict `SUPPORTED`. Echo gates are reported separately.

1. `P1`: all `88` reconstructed states are physical within tolerance: trace error `<=1e-12`, minimum eigenvalue
   `>=-1e-12`, Hermiticity residual `<=1e-12`, and \(S_{\max}\le2\sqrt2+10^{-12}\).
2. `P2`: all four Ramsey states have exactly three strong axes at the first wait.
3. `P3`: all four Ramsey states cross from \(S_{\max}>2\) to \(S_{\max}\le2\) within the sampled interval.
4. `P4`: all four Ramsey states exhibit at least one one-strong-axis observation after their last three-axis
   observation.
5. `P5`: at the final Ramsey wait, the median retained fraction of \(s_1\) across states is at least `0.50`.
6. `P6`: at the final Ramsey wait, the median retained fraction of \(s_2\) is at most `0.50`.
7. `P7`: preferential retention is material: median final \(s_1\)-retention minus median final
   \(s_2\)-retention is at least `0.20`.
8. `P8`: in each state, the first sampled CHSH failure occurs no earlier than the last sampled three-axis state.

Echo replication gates:

9. `E1`: all four Hahn states begin with exactly three strong axes.
10. `E2`: all four Hahn states cross from \(S_{\max}>2\) to \(S_{\max}\le2\) within the sampled interval.
11. `E3`: the geometric mean of Hahn first-crossing times divided by the geometric mean of Ramsey first-crossing
    times is at least `4.0`.
12. `E4`: every Hahn state retains three strong axes at a wait later than its Ramsey first-crossing time.

## Required outputs

- one record per state, condition and wait;
- singular values, strong-axis count, physicality diagnostics and \(S_{\max}\);
- exact sampled crossing times;
- retention ratios and gate table;
- independent validation that recomputes the results from source files;
- a report that distinguishes established quantum mechanics from the ARA crosswalk.

