# MX10 Cross-Rung State-Contraction Report

**Date:** 2026-07-23  
**Verdict:** **NOT SUPPORTED as one transferable numerical scale law**  
**What remains supported:** exact MX9 ARA state geometry at every declared rung; strong evidence that the
child-to-parent contraction rate is identity- and dataset-dependent

## Plain-language result

The same ARA state ball can be constructed at every spatial resolution. That part worked exactly: every two-channel
state stayed within its allowed sphere, every one-cell state lay on its boundary, and larger blocks moved inward as
unresolved children mixed.

What failed was the stronger shortcut:

> Learn one number from the first child-to-parent step and use that same number for every later rung, every A/B
> component pair, and another plasma simulation.

The geometry repeated; the **speed and shape of travel through it did not repeat as one universal constant**.

This produces a useful refinement:

\[
\boxed{
\text{invariant ARA state geometry}
\quad+\quad
\text{identity-conditioned rung map}
}
\]

Plainly: ARA can supply the common coordinate system, but the local identity still supplies how quickly it mixes
when the measuring scale changes.

## Frozen test

For each collocated electric-component pair `(E_x,E_y)`, `(E_y,E_z)`, and `(E_z,E_x)`, a positive two-channel
coherency matrix was constructed inside non-overlapping spatial blocks. Its MX9 state radius was

\[
r=
\frac{\sqrt{(2G_{AB})^2+(G_{BB}-G_{AA})^2}}{\operatorname{tr}G},
\qquad 0\le r\le1.
\]

The activity-weighted field statistic \(D_b\) was measured at doubled block widths. The frozen one-number law was

\[
\widehat D_b=b^{-\beta}.
\]

Only Warp development data at the first transition \(1\to2\) were allowed to determine \(\beta\). That one value
then predicted:

- larger Warp rungs;
- ten later held-out Warp iterations;
- all three component pairs;
- 93 collocated 2-D planes from an independent PIConGPU snapshot.

Comparators were no contraction, independent 2-D mixing, a development law fitted separately by component pair,
and a local law allowed to observe one child transition in the identity being scored.

## Data-quality correction

The first v1 run paired equal array indices before accounting for half-cell field staggering. That does not compare
the same physical location. V1 was invalidated and preserved.

V2 was frozen before corrected outcomes. Each component was linearly collocated to the common half-cell centre,
with no wraparound or padding. The corrected run produced the same substantive verdict, so the failure is not a
grid-offset artifact.

## Numerical findings

The common development exponent was

\[
\widehat\beta=0.00647591,
\qquad
95\%\ {\rm bootstrap\ interval}=[0.00631875,0.00664017].
\]

But the three Warp component-pair exponents learned at the same first rung were

| Pair | Development \(1\to2\) exponent |
|---|---:|
| \(E_x/E_y\) | 0.0000996 |
| \(E_y/E_z\) | 0.0002416 |
| \(E_z/E_x\) | 0.0190865 |

The common number is therefore mainly an average of unlike identities.

### Held-out Warp

| Model | MALE, rungs 2–16 |
|---|---:|
| Common one-number law | 0.057750 |
| No contraction | **0.054540** |
| Independent 2-D mixing | 1.678328 |
| Pair-specific development law | **0.043353** |

On rungs 4–16, common-law error was `1.360×` local one-step error, above the frozen `1.20×` limit. It was
`1.332×` pair-specific error, above the `1.10×` limit. The internal gate failed.

The reason is visible in the held-out paths:

| Pair | \(D_2\) | \(D_4\) | \(D_8\) | \(D_{16}\) |
|---|---:|---:|---:|---:|
| \(E_x/E_y\) | 0.999923 | 0.999883 | 0.999620 | 0.999607 |
| \(E_y/E_z\) | 0.999855 | 0.999833 | 0.999131 | 0.998967 |
| \(E_z/E_x\) | 0.984361 | 0.938467 | 0.864960 | 0.652503 |

Two pairs remain almost on the state boundary; the third moves strongly inward and accelerates at the largest
rung. Flattening those three paths into one coefficient loses real structure.

### Post-result flip, direction and participation audit

Increasing \(b\) groups resolved children into a larger parent, so MX10 travels **upward in observational rung**.
Moving inward in the state ball is not movement down the rung ladder. It is the loss of separately resolved child
orientation as those children close into the parent.

This is a child-mixing or aggregation singularity in the declared ARA terminology:

\[
\{s_i^{\rm child}\}
\xrightarrow[\text{coarse-grain upward}]{\mathcal R}
s_{\rm parent}
=\frac{\sum_iT_i s_i}{\sum_iT_i}.
\]

Oppositely oriented child contributions can cancel in the parent even when the parent itself does not reverse.
That must be distinguished from a same-parent `A -> B` flip. Because the radius \(D_b\) is unsigned, a separate
signed audit retained the two real state components for the `zx` orientation:

\[
s_{\rm coh}=\frac{2G_{zx}}{T},
\qquad
s_{\rm pop}=\frac{G_{xx}-G_{zz}}{T}.
\]

Across the held-out Warp iterations, the global signed centroid remained

\[
\langle s_{\rm coh}\rangle\approx3.5\times10^{-17},
\qquad
\langle s_{\rm pop}\rangle\approx-0.5226
\]

at every block rung. The parent population direction therefore did not reverse. From rung 8 to 16, only `0.0111%`
of activity had a dominant child antipodal to its parent.

The corrected interpretation is:

- **observed:** upward child-to-parent mixing and loss of resolved child orientation;
- **ARA classification:** a cross-rung child-mixing singularity;
- **not observed:** a global same-parent `AB -> BA` orientation flip.

The field-wide radius was still `0.6525` at rung 16, so the whole field had not reached complete mixing. Locally,
about `9.65%` of activity lay below radius `0.25` at rung 16. The imposed block ladder therefore shows partial/local
singularity formation, but it does not identify rung 16 as a natural physical singularity scale.

The apparent three-pair difference also has a major participation explanation. On held-out Warp data, mean electric
energy fractions were:

| Component | Fraction of total electric-field energy |
|---|---:|
| \(E_x\) | 0.020999% |
| \(E_y\) | 99.912032% |
| \(E_z\) | 0.066969% |

Thus `xy` and `yz` remain near the state-ball boundary largely because \(E_y\) overwhelms its partner. They are not
three equally participating physical A/B identities. The `zx` pair compares the two weak components, so their
changing local orientation is visible when blocks are enlarged. This strengthens the conclusion that arbitrary
coordinate pairs cannot be assigned one common rung coefficient. It does not establish a parent-axis flip, while
remaining an example of the distinct child-mixing singularity.

### External PIConGPU

| Model | MALE, rungs 2–8 |
|---|---:|
| Common Warp-trained law | 0.633558 |
| No contraction | 0.642535 |
| Independent 2-D mixing | 0.743759 |
| Local one-step law, rungs 4–8 | **0.127123** |

The common law narrowly beat the two fixed comparators, but its larger-rung error was `6.252×` the local law,
far beyond the frozen `1.25×` limit. The external gate failed.

PIConGPU nevertheless showed clean pair-specific paths. Its effective exponents were approximately:

- \(E_x/E_y\): `0.47–0.49`;
- \(E_y/E_z\): `0.51–0.54`;
- \(E_z/E_x\): `0.29–0.34`.

Thus the local child transition carried substantial information about later rungs, but the rate did not transfer
from the Warp identity.

## ARA interpretation

The result separates two claims that had been travelling together:

1. **Same state geometry:** supported exactly. Every declared A/B pair generates the MX9 unit ball and every axis
   generates a reversible 0–2 diameter.
2. **Same numerical rung speed:** rejected in the tested form. One \(\beta\) did not govern all pairs and both
   simulators.

In Dylan's terminology, the sphere recurs, but its local coupling web determines how it fills or contracts. This
is compatible with the longstanding statement that identity changes the local expression while the underlying
geometry remains recognizable. It also means that “fractal” cannot yet be operationalised as one universal
coefficient per doubling.

A better next mathematical form is

\[
\underbrace{D_{k+1}}_{\substack{\text{parent state}\\\text{at next rung}}}
=
\underbrace{\mathcal R}_{\substack{\text{common rung}\\\text{operator form}}}
\left(
\underbrace{D_k}_{\text{resolved child state}},
\underbrace{\eta_k}_{\substack{\text{local identity/coupling}\\\text{coordinate}}}
\right),
\]

where \(\eta_k\) must be measured independently rather than fitted after the parent is opened.

Plainly: the next rung depends on both the current ARA state and a local description of what is coupling inside
that identity. The local \(D_2\) transition is a promising summary, but it is not yet a complete independent
coordinate.

## Evidence boundary

MX10 does **not** disprove ARA's sphere/diameter mathematics or the exact Maxwell crosswalk. It rejects one
specific, deliberately strong physical-fractality prediction: a single constant contraction exponent transferred
across component identities and simulators.

The spatial blocks are controlled observation rungs, not independently discovered physical octaves. A future
stronger test should define physical rungs from an external wavelength, correlation length, material boundary, or
mode transition before calculating ARA. It should then test whether a predeclared local coupling coordinate
predicts the rung map without reading the parent.

## Prime-thread correspondence

The prime work contains the same formal child-to-parent operator on an arithmetic axis:

- lower factor gates or residue lanes are the resolved children;
- their combined wheel/survivor account is the parent;
- a compressed parent can conceal broad child asymmetry;
- the parent then becomes a child/source for the next gate.

PN37's full-child field explicitly showed parent cancellation hiding asymmetric prime children. MX10 showed the
physical-field counterpart: opposed local component orientations closed into a more mixed spatial parent. Both are
instances of the non-injective child-to-parent closure formalised by Corollary 8.5a.

The evidence levels remain different. Electromagnetic coarse-graining is a physical-field measurement; prime
closure is arithmetic, and PN42's stronger claim that a prime itself is the completed vertical `2 -> 0`
singularity still lacks independently calculable \(a(N)\) and \(v(N)\). The shared result is the recursive closure
operator, not yet one universal causal law.

## Validation and reproducibility

Independent validation recomputed a deterministic subset directly from both HDF5 sources using an explicit block
loop rather than the production reshape. It passed `20/20` checks, including:

- source hashes;
- staggered-grid collocation;
- selected Warp and PIConGPU rung values;
- the common fitted exponent;
- every recorded state radius remaining in `[0,1]`;
- every one-cell state lying at radius `1`.

Files:

- `MX10_CROSS_RUNG_STATE_CONTRACTION_PROTOCOL_v1_FROZEN.md` — invalidated protocol and reason;
- `MX10_CROSS_RUNG_STATE_CONTRACTION_RESULTS.json` — preserved invalid v1 output;
- `MX10_CROSS_RUNG_STATE_CONTRACTION_PROTOCOL_v2_FROZEN.md` — corrected frozen protocol;
- `mx10_cross_rung_state_contraction_v2.py` — corrected runner;
- `MX10_CROSS_RUNG_STATE_CONTRACTION_RESULTS_v2.json` — full result and observations;
- `mx10_validate_outputs_v2.py` — independent validator;
- `MX10_CROSS_RUNG_STATE_CONTRACTION_VALIDATION_v2.json` — `20/20` validation record.
