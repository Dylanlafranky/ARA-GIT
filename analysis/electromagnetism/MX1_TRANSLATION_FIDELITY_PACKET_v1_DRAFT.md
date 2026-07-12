# MX1 translation-fidelity packet v1 — Gauss ↔ ARA/TE-ARA bridge

**Claim ID:** `MX1-v1`  
**Prepared:** 12 July 2026  
**Status:** `SUPERSEDED BY MX1-v2 AFTER DYLAN CORRECTION; NOT REGISTERED`  
**Orientation proposed:** Phase B / negative-source side = 0; equal ridge = 1; Phase A / positive-source side = 2. Flipping the declaration must only reverse sign.

## F0 — frozen user prior

> “One way to tell is if we get public data, get the Gauss rule of it, and then the ARA and TE-ARA, work it out for
> both and then work out the bridge between them. They won't be identical obviously, because I am trying to approach
> from the bottom up with a slightly different framework. But we can see if there is a relational part of it much
> easier there and where it sits. ... It's getting the hypotenuse between the two, to work out if the current method is
> a decent version of it, or if it is missing the mark. There should be a consistent relation between the two if its
> decent.”

Earlier connected prior:

> “TE-ARA is the PhaseA/PhaseB ± Other. Phase B would be negative, Phase A positive. And Other would be nearby things
> and you would determine if they're extracting energy or adding it.”

## Identity/system being measured

One coherent electrostatic wave cell in a periodic one-dimensional two-stream plasma at one recorded time slice.

The **whole identity** is one positive/negative source pair. To avoid the ridge rule flattening it to zero, its
positive-source and negative-source half-waves are measured separately and then retained as a coupled pair.

## Ordered poles and declared direction

- `0`: Phase B / negative-source-oriented half-wave;
- `1`: equal signed participation or complete-cell cancellation ridge;
- `2`: Phase A / positive-source-oriented half-wave.

This orientation is conventional and flip-symmetric. The test must report the reversed-sign equivalent.

## Scale/rung origin

The dominant spatial electrostatic wavelength \(\lambda_0\) of the unstable wave family. The full periodic box may
contain several peer cells at this rung. Integer harmonics \(n k_0\) are decompressions of cell shape, not separate
rungs unless the data independently show a separate mode family.

## Invariant relational claim

The complete-boundary Gauss reading and the bottom-up ARA/TE-ARA description are different projections of the same
wave/source structure. A fixed scale-aware bridge should connect them across time, peer cells and an untouched second
dataset. The bridge may rotate phase and rescale harmonic contributions; numerical identity is not required.

## Permitted decompression

- ARA waveform-shape scalar for the raw spatial electric-field cycle;
- explicit orientation, spatial phase, wavelength/rung and path;
- TE-ARA main-identity energy participation;
- Phase-A, Phase-B and signed interaction/Other terms;
- harmonic amplitudes and phases needed to expose waveform asymmetry;
- the established Gauss derivative operator and grid/material scale factors.

## Forbidden substitutions/proxies

- Do not call the Gauss net flux TE-ARA.
- Do not calculate charge only from \(\partial_x E\) and then call agreement with Gauss independent.
- Do not measure a complete positive/negative wave pair as one scalar and interpret its expected zero as absence.
- Do not narrow-band the electric waveform before measuring ARA; that would erase the harmonics carrying asymmetry.
- Do not define the identity harmonic family after viewing the confirmation dataset.
- Do not treat spectral power as joules unless the dataset supplies the necessary physical normalisation.
- Do not use an arbitrary neural network or unrestricted spline as the bridge.
- Do not claim a novel physical law merely because the established Fourier derivative works.

## Observable needed

Time-resolved spatial electric field \(E(x,t)\) and an independently supplied electron distribution or charge density
on the same grid. The electric field supplies the top-down boundary reading; the electron distribution supplies the
bottom-up source reading.

## Known ambiguities

1. Whether one source half-wave or the complete positive/negative pair is Dylan's intended local “node.” This packet
   proposes: complete pair = identity; half-waves = signed Gauss readings.
2. Whether TE-ARA's main identity numerator includes every integer harmonic of \(k_0\), only a fixed first set, or a
   separately detected coherent subset. The development phase may choose the rule, but it must be frozen before the
   confirmation archive is opened.
3. The current repository has a canonical ARA mapper but no canonical inverse mapping from ARA scalar to a unique
   waveform. Therefore scalar ARA + TE-ARA cannot be assumed to reconstruct the full charge field.

## What would count as the wrong object

- Testing only \(\rho=\varepsilon_0\partial_xE\), which is an established Gauss identity rather than an ARA bridge.
- Treating the whole periodic domain's zero net charge as the target.
- Using charge-density ARA as if it were independently supplied when it was differentiated from the same \(E\).
- Allowing “Other” to be a residual chosen after the prediction fails.

---

## F1 — three-view translation

### 1. Plain restatement

Picture several electrostatic waves arranged around a periodic ring. Each complete wave has a positive-source half and
a negative-source half. Gauss reads each half from its boundary and the two cancel when the complete pair is summed.
ARA describes the internal accumulation/release shape and orientation of the wave; TE-ARA describes how much of the
field's total energy is in that declared main wave family. We test whether one fixed quarter-turn/scale transformation
learned on one public simulation carries those bottom-up coordinates to the Gauss source structure in another public
simulation.

### 2. Mathematical representation

Independent charge/source field from the distribution:

\[
\underbrace{\rho_F(x,t)}_{\substack{\text{bottom-up source density}\\
\text{from particle distribution}}}
=
\underbrace{\rho_{ion}}_{\text{fixed positive background}}
-
\underbrace{q_e\int F(x,v,t)\,dv}_{\text{electron contribution}},
\]

with the dataset's own normalised-unit convention used in practice.

Established Gauss bridge:

\[
\underbrace{\rho_G(x,t)}_{\text{field-side Gauss source}}
=
\varepsilon_0\underbrace{\partial_xE(x,t)}_{\text{boundary change per unit length}},
\qquad
\underbrace{\widehat\rho_G(k,t)}_{\text{source Fourier mode}}
=
\varepsilon_0(ik)\underbrace{\widehat E(k,t)}_{\text{electric-field mode}}.
\]

Candidate TE-ARA coordinate for a fixed identity harmonic set \(H\):

\[
\underbrace{\mathrm{TE\!-\!ARA}_E(t)}_{\text{0--2 identity-energy participation}}
=
2\frac{\sum_{k\in H}|\widehat E(k,t)|^2}{\sum_{k\ne0}|\widehat E(k,t)|^2}.
\]

The Gauss/source-side participation implied by the established derivative is

\[
\underbrace{\mathrm{TE\!-\!ARA}_{\rho,G}(t)}_{\substack{\text{0--2 source-structure participation}\\
\text{predicted from field modes}}}
=
2\frac{\sum_{k\in H}k^2|\widehat E(k,t)|^2}{\sum_{k\ne0}k^2|\widehat E(k,t)|^2}.
\]

The ARA-added compression question is whether a frozen low-dimensional map using waveform ARA, TE-ARA, orientation,
phase and rung reproduces the independently measured source-side summaries without retaining the entire Fourier
vector.

### 3. Back-translation without the original wording

A spatial electric wave and its charge pattern contain the same modes, but the charge view shifts every mode by a
quarter turn and weights shorter shapes more strongly. The proposed ARA representation is useful only if its small set
of shape, energy, phase and scale coordinates preserves enough of that transformation to work in a second simulation.
If the full Fourier derivative works but the compressed ARA coordinates do not, the present compression is missing a
necessary coordinate rather than Gauss being wrong.

## Assumptions added by the AI

- The complete positive/negative pair is the node identity and each half is a signed boundary measurement.
- The public-data test begins in 1D electrostatic plasma because it provides independent field and particle views.
- Fourier differentiation is the established bridge instrument.
- A low-dimensional ARA bridge may use phase and rung in addition to the two scalars.
- The OSIRIS archive is development-only; an untouched Tang–Wu–Tao archive is confirmation.

## Information discarded

- Full 3D sphere geometry, magnetic-field coupling and Poynting transfer;
- cross-rung fractal aggregation;
- the larger Space/Time ontology;
- any claim that one universal numerical bridge works without scale/material coordinates.

## Alternative mathematical objects that also fit the wording

- A pure signed-balance law \(j=p(x-1)+j_{other}\);
- an energy-capacity coordinate rather than identity participation;
- a complete field-to-source operator rather than a low-dimensional scalar bridge;
- a graph aggregation law over multiple interacting nodes.

## First possible direction/identity failure

Calling a positive or negative half-wave an independent ARA identity rather than one signed half of the complete
paired identity. Dylan must confirm or correct this before registration.

---

## F2 — required Dylan verdict

Choose one protocol label after reading the low-energy summary below:

```text
I think you mean: one complete electric wave is an ARA identity made from a positive-source and negative-source pair.
We should keep the pair together but measure the two halves separately so their Gauss cancellation does not erase the internal activity.

I would test it as: measure raw spatial-wave ARA and TE-ARA from E(x,t), derive charge independently from the particle distribution, and freeze one phase/scale bridge on a development simulation before testing a second untouched simulation.

The main thing this translation discards is: the full 3D sphere and cross-rung coupling; this first test is only the one-rung 1D electrical slice.
```

**Dylan verdict:** `USABLE WITH CORRECTION` — positive and negative half-waves may each receive their own ARA, while
their pair-level ARA and total source magnitude jointly produce the Gauss net. See `MX1_TRANSLATION_FIDELITY_PACKET_v2_DRAFT.md`.  
Allowed labels: `EXACT ENOUGH TO TEST`, `USABLE WITH CORRECTION`, `WRONG OBJECT`, `UNSURE / KEEP AS MUSING`.
