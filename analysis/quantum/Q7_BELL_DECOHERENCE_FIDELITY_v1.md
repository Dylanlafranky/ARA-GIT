# Q7 Bell-decoherence ARA fidelity

**Claim ID / version:** `Q7-BELL-DECOHERENCE-FID-v1`  
**Date:** 24 July 2026  
**Status at freeze:** `PUBLIC-DATA, PARTIALLY BLINDED REANALYSIS`

## ARA statement being tested

A prepared Bell state is a coherent parent with three measurable relation axes. Under predominantly directional
dephasing, the two phase-sensitive relation axes should contract faster than the most persistent axis. On the ARA
reading, the parent therefore moves from a three-cut coherent closure toward a one-cut remnant before complete
mixing is possible:

\[
\underbrace{(s_1,s_2,s_3)}_{\text{three relation cuts}}
\longrightarrow
\underbrace{(s_1,0,0)}_{\text{one persistent cut}}
\quad\text{rather than assuming}\quad
(0,0,0).
\]

The final zero-axis state is **not** required. Directional dephasing and isotropic mixing are different physical
processes; forcing both into `3 -> 1 -> 0` would flatten the geometry.

The CHSH boundary is an independent physical discriminator:

\[
S_{\max}=2\sqrt{s_1^2+s_2^2}.
\]

Loss of Bell violation should follow contraction of the second relation axis. A Hahn-echo intervention should delay
that contraction by reversing part of the accumulated phase error.

## What is genuinely at risk

The test can fail if:

- the prepared states do not begin with three strong relation axes;
- no preferential axis retention appears;
- a one-axis remnant never occurs;
- the CHSH crossing does not occur in the measured Ramsey interval;
- Hahn echo does not materially delay that crossing.

## What is already known

The source paper states that its directly reported Bell signal remains above `S = 2` for about `15 us` in Ramsey
and beyond `100 us` with Hahn echo. Therefore this is not a blind discovery of a Bell-lifetime extension. The
unopened numerical target is the full Pauli-tensor trajectory after the development interval, its physical
density-matrix reconstruction, singular-axis ordering, exact crossing locations on the sampled grid, and the
relation between the axis transition and CHSH loss.

## Interpretation boundary

A pass would establish that the same ARA relation-axis language used in Q5/Q6B remains quantitatively coherent
through a real, physically prepared time series and a real control intervention. It would not show that ARA
derived dephasing, discovered Bell decay, outperforms quantum mechanics, or proves universal fractality.

