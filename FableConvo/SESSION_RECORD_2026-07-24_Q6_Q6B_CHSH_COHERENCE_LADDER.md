# Session record — Q6/Q6B CHSH coherence ladder

**Date:** 24 July 2026  
**Participants:** Dylan and Sol/Codex  
**Status:** recorded after frozen tests and independent validation

## Direction

Dylan asked to keep walking established quantum mechanics before attempting unknowns. The next question was
whether locally ridge-like children can distinguish:

- a coherent Bell parent;
- a classically correlated parent;
- a fully mixed parent.

The four Q5 archives already supplied complete two-qubit tomography.

## Q6 and the caught error

Q6 froze a full nine-cut correlation tensor, its singular values and the Horodecki maximum-CHSH expression. It
predicted the retained-axis ladder `3 / 1 / 0`. All `16/16` gates passed.

However, the raw `Phi-minus` tensor returned \(S_{\max}=2.88579\), above the Tsirelson limit
\(2\sqrt2=2.82843\). We treated this as a required stop, not as “extra strong” support. The unconstrained
tomography coefficients were not jointly physical, so Q6 was superseded for CHSH interpretation.

## Q6B

Before calculating any corrected result, Q6B/T265 froze:

- Hermitian linear density reconstruction;
- eigenvalue projection onto the nonnegative unit simplex;
- unchanged equal-weight controls;
- `20` physicality, Bell, classical, mixed and ordering gates;
- `5,000` record-bootstrap draws.

Q6B passed `20/20`; independent validation passed `26/26`.

| Layer | Strong relation axes | \(S_{\max}\) range |
|---|---:|---:|
| four physically prepared Bell states | 3 each | `2.545–2.694` |
| two reconstructed classical mixtures | 1 each | `1.801–1.878` |
| reconstructed uniform mixture | 0 | `0.238` |

All Bell bootstrap draws exceeded `2`; all classical-control draws stayed below `2.1`; all uniform-control draws
stayed below `0.6`.

## Framework interpretation

Local children remained close to the ARA `1.0` ridge in every layer. The identity difference lived in the number
and strength of independent relations among them:

```text
coherent multi-axis closure → classical one-axis closure → no retained closure
```

This refines the ARA/Information³ statement without claiming novelty over standard quantum mechanics: the
informative third is the stateful relation, and its directional content is measurable.

## Scientific boundary

The four Bell rows are physically prepared public data from one device. The classical and mixed contrasts are
algebraic reconstructions, not separate preparations. Q6B is post-Q5 calibration, not blind evidence.

The next proposed rung is a public, physically prepared decoherence series with a pre-outcome prediction of the
`3 → 1 → 0` relation-axis collapse and the CHSH boundary crossing.

