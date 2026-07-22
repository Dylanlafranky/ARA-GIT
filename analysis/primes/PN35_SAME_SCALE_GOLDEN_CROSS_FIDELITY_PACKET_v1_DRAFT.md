# PN35 same-scale golden-cross fidelity packet — v1

**Claim ID:** `PN35/SAME-SCALE-GOLDEN-CROSS/v1`  
**Date:** 22 July 2026  
**Orientation:** up = larger/slower octave rung; within a rung, increasing structural child position runs `0 -> 2`.
At the upper singularity, the next doubled rung begins at local `0` with phase/anti-phase orientation reversed.  
**Dylan fidelity verdict:** `EXACT ENOUGH TO TEST` — approval: “Yes it didn't matter because I could just expand it
but for this test we should use it as the two waves are the same scale then. So, Yes please do that.”

## F0 — frozen user prior

> “Can we not now have a Hexagon wave/2 wave, and a pentagon or phi wave, going next to each other. Where the phi
> wave crosses the 2 wave, is where a prime is?”

Correction supplied before this test:

> “you measured 8 distinctions, that is a Phase A, Phase B, Phase A, Phase B. These are the child waves of the
> larger scale. The full ARA is the 8 and it is actually 2. The double occurs at the singularity.”

## Identity, poles, rung and closure

- **Identity:** one complete eight-channel structural prime-wheel cell, retained inside a larger octave rung.
- **Decompressed children:** the eight residues coprime to `30`, `{1,7,11,13,17,19,23,29}`.
- **Anti-pairs:** `(1,29)`, `(7,23)`, `(11,19)`, `(13,17)`.
- **Compressed parent coordinate:** `x_2(r)=r/15` on a circumference of length `2`; every anti-pair totals `2`.
- **Larger rung:** `[2^k,2^(k+1))`. The upper endpoint is the declared parent singularity, not merely a convenient
  interval boundary. The next rung resets to local `0` and reverses orientation.
- **Observable:** whether a structural candidate is prime, measured only after its same-scale golden-crossing score
  has been sealed.

The eight wheel channels are an exact arithmetic decompression. Their use as the measured eight-child appearance of
the user's corrected parent ARA is the approved bridge for this test; it is not a claim that Euler's totient or the
number `30` derives the whole ARA ontology.

## F1 — three-view translation

### Plain restatement

The structural wave supplies eight child positions that close into one parent total of `2`. A second, non-locking
golden handover wave travels on that same `0–2` circumference. It crosses the structural wave twice per local cycle.
At the octave singularity the parent completes, the scale doubles and orientation flips. The test asks whether prime
events occur preferentially near those moving golden crossings rather than merely anywhere on the eight structural
channels.

### Mathematical representation

For a structural wheel cell beginning at the multiple of `30` called `c`, let

\[
\mathcal R=\{1,7,11,13,17,19,23,29\},
\qquad
x_2(r)=\frac r{15}\in(0,2).
\]

Inside octave rung `k`, with lower singularity `L_k=2^k`, define the cell's continuous progress from that
singularity by

\[
t_{k,c}=\frac{c-L_k}{30}.
\]

The frozen golden handover step is the golden-angle turn `alpha_phi=1/phi^2`. On the same length-two circumference,

\[
g_{k,c}=\left(2\,\sigma_k\,\alpha_\phi\,t_{k,c}\right)\bmod2,
\qquad
\sigma_k=(-1)^k.
\]

The two crossings are `g_(k,c)` and `(g_(k,c)+1) mod 2`. Candidate `n=c+r` receives the pre-label crossing distance

\[
d_\times(n)=
\min_{h\in\{g_{k,c},\,(g_{k,c}+1)\bmod2\}}
\min\left(|x_2(r)-h|,\,2-|x_2(r)-h|\right).
\]

Smaller `d_x` means closer to the registered crossing. The claim predicts higher prime incidence at smaller distance.

### Back-translation

Begin at the exact lower singularity of a doubling rung. Walk through the repeated eight-child structural cells while
the golden handover advances around the same parent circumference. Each local pair of wave crossings identifies two
nearby child channels. At the doubled endpoint, close the parent, return `2 -> 0`, and reverse which way the handover
travels. If the proposal is correct in this representation, primes should favour the channels nearest those crossings.

## AI additions and discarded information

**AI additions:**

1. The unfitted golden rotation is operationalised as `1/phi^2` turns per structural cell.
2. Two crossings are placed anti-phase, one unit apart on the length-two circumference.
3. The phase origin is the exact octave singularity; no target-dependent offset is allowed.
4. The singularity flip is operationalised as `sigma_k=(-1)^k`.

**Information discarded:** full factor identities above the `2*3*5` wheel, prime-gap size, PN26's complete lower
parent and PN34's omitted-parent density. PN35 tests a same-scale crossing preference, not exact primality.

**Alternative objects not tested:** a curved/nonconstant Phi path, PN33's eight density-fill bands as a continuous
waveform, the full residue torus, a fitted phase origin, or Phi as spatial curvature rather than handover timing.

## Forbidden reinterpretations

PN35 must not:

- tune the golden phase, crossing count, rotation step, rung boundary or flip after seeing prime labels;
- call wheel survival itself evidence for Phi;
- claim exact prime generation, primality certification, a speed improvement or a new theorem;
- allow a different irrational constant or an arbitrary phase shift to count as a Phi success;
- reinterpret a null crossing result as support because the eight-channel structural crosswalk remains exact; or
- treat the earlier PN12 adjacent-child carrier null as this same observable.

## Fidelity kill gate

The tested identity, eight children, `0–2` parent, octave singularity, orientation flip and prime-incidence observable
must all remain as written. A later change creates `v2`; it may not silently replace this object.

