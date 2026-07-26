# Q6B physical-CHSH data-quality audit

**Date:** 24 July 2026  
**Verdict:** suitable for a bounded, post-Q5 coherence-ladder calibration; not an independent experiment

## Source

- Madzik and Asaad, *Figure 2 — Bell states tomography*.
- Figshare DOI: `10.6084/m9.figshare.14160476.v2`.
- Licence: CC BY 4.0.
- Four raw-current archives, all matched to the deposit's published MD5 checksums.
- Associated experiment: *Bell-state tomography in a silicon many-electron artificial molecule*.

## Strong points

- The source contains raw current traces rather than only a plotted density matrix.
- All four declared Bell preparations are present.
- Q5 decoded three archives before opening their outcomes and recovered all four expected parent labels.
- Q6B resamples complete classified records within each measurement orientation.
- Point metrics were independently reconstructed and bootstrap artifacts independently audited (`26/26`).

## Important limitations

1. **One device/deposit.** The four states are replications within one experimental platform, not cross-device
   evidence.
2. **Known source.** Q6B was designed after Q5 outcomes were open. It is a calibration of the next mathematical
   layer, not a blind prediction.
3. **Reconstructed controls.** The classical and uniform controls are equal-weight linear combinations of the
   four physically prepared Bell estimates. They were not separately prepared in the laboratory.
4. **Raw linear inversion was nonphysical.** Q6 exposed an apparent Tsirelson violation. Q6B therefore applies a
   declared positive-semidefinite, unit-trace projection.
5. **Projection is not the authors' full estimator.** The eigenvalue-simplex projection is transparent and
   reproducible but is not claimed to equal a maximum-likelihood tomography pipeline.
6. **Bootstrap scope.** Record resampling measures finite-record stability within this archive. It does not
   capture every calibration drift or device-level systematic.

## Safe use

Safe statement:

> In this public four-state deposit, the Q5 parent relation survives a physical density-matrix constraint and
> separates a three-axis Bell-coherent layer from one-axis reconstructed classical controls and a zero-axis
> reconstructed uniform mixture.

Unsafe statements include “ARA discovered Bell nonlocality,” “the reconstructed controls are new experimental
states,” “ARA outperforms tomography,” or “this proves universal fractality.”

